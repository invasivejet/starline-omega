--!strict
--[[
  STARLINE Ω — high-performance authoritative server.
  Fixed sim tick · capped catch-up · batched replicate (wire) · minimal attributes.
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Starline = ReplicatedStorage:WaitForChild("Starline")
local Config = require(Starline.Config)
local Engine = require(Starline.Engine)
local EconomyField = require(Starline.EconomyField)
local EconomyStore = require(Starline.EconomyStore)
local TrackUnlock = require(Starline.TrackUnlock)
local VehicleGarage = require(Starline.VehicleGarage)
local MotionConfig = require(Starline.MotionConfig)
local TrackBuilder = require(Starline.TrackBuilder)
local TrackVisual = require(Starline.TrackVisual)
local SimClock = require(Starline.SimClock)
local StateReplicator = require(Starline.StateReplicator)
local TelemetrySink = require(Starline.TelemetrySink)
local AfkPilot = require(Starline.AfkPilot)

type PlayerEngineEntry = {
	engine: any,
	track: any,
	trackId: string,
	vehicleId: string,
	lastWire: { number }?,
	wireSeq: number,
	lastResonance: number,
	replicateAccum: number,
	economyAccum: number,
	telemetryAccum: number,
}

local playerEngines: { [number]: PlayerEngineEntry } = {}
local afkSessions: { [number]: any } = {}
local activeUserIds: { number } = {}
local globalVisualTrackId: string? = nil

local simClock = SimClock.new(Config.FixedDt, Config.MaxSimStepsPerFrame)
local replicateInterval = 1 / Config.ReplicateHz
local economyInterval = 1 / Config.EconomyAttributeHz

local remotes = ReplicatedStorage:FindFirstChild("StarlineRemotes") :: Folder?
if not remotes then
	remotes = Instance.new("Folder")
	remotes.Name = "StarlineRemotes"
	remotes.Parent = ReplicatedStorage
end

local function ensureRemote(name: string, className: string): Instance
	local r = remotes:FindFirstChild(name)
	if r then
		return r
	end
	local inst = Instance.new(className)
	inst.Name = name
	inst.Parent = remotes
	return inst
end

local controlRemote = ensureRemote("Control", "RemoteEvent") :: RemoteEvent

local stateRemote: RemoteEvent | UnreliableRemoteEvent
if Config.UseUnreliableState then
	local existing = remotes:FindFirstChild("StateUnreliable")
	if existing and existing:IsA("UnreliableRemoteEvent") then
		stateRemote = existing
	else
		local old = remotes:FindFirstChild("State")
		if old then
			old:Destroy()
		end
		local u = Instance.new("UnreliableRemoteEvent")
		u.Name = "StateUnreliable"
		u.Parent = remotes
		stateRemote = u
	end
else
	stateRemote = ensureRemote("State", "RemoteEvent") :: RemoteEvent
end
local unlockRemote = ensureRemote("UnlockTrack", "RemoteEvent") :: RemoteEvent
local selectRemote = ensureRemote("SelectTrack", "RemoteEvent") :: RemoteEvent
local tracksRemote = ensureRemote("ListTracks", "RemoteFunction") :: RemoteFunction
local afkRemote = ensureRemote("AfkToggle", "RemoteEvent") :: RemoteEvent
local buyVehicleRemote = ensureRemote("BuyVehicle", "RemoteEvent") :: RemoteEvent
local equipVehicleRemote = ensureRemote("EquipVehicle", "RemoteEvent") :: RemoteEvent
local listVehiclesRemote = ensureRemote("ListVehicles", "RemoteFunction") :: RemoteFunction

local function rebuildVisual(track: any, trackId: string)
	if globalVisualTrackId == trackId then
		return
	end
	TrackVisual.destroy()
	TrackVisual.build(track, Config.TrackVisualSamples)
	globalVisualTrackId = trackId
end

local function addActiveUser(userId: number)
	for _, id in activeUserIds do
		if id == userId then
			return
		end
	end
	table.insert(activeUserIds, userId)
end

local function removeActiveUser(userId: number)
	for i, id in activeUserIds do
		if id == userId then
			table.remove(activeUserIds, i)
			return
		end
	end
end

local function ensureEngine(player: Player): PlayerEngineEntry
	local trackId = (player:GetAttribute("StarlineActiveTrack") or "oval") :: string
	local vehicleId = (player:GetAttribute("StarlineActiveVehicle") or "urban_pulse") :: string
	local existing = playerEngines[player.UserId]
	if existing and existing.trackId == trackId and existing.vehicleId == vehicleId then
		return existing
	end

	if existing then
		existing.engine.players[player.UserId] = nil
		existing.engine.controls[player.UserId] = nil
		existing.engine.flowMachines[player.UserId] = nil
	end

	local track = TrackBuilder.fromWorkspace(trackId)
	rebuildVisual(track, trackId)
	local motionCfg = MotionConfig.forVehicle(vehicleId)
	local eng = Engine.new(track, motionCfg)
	eng:addPlayer(player.UserId, 0)
	local entry: PlayerEngineEntry = {
		engine = eng,
		track = track,
		trackId = trackId,
		vehicleId = vehicleId,
		lastWire = nil,
		wireSeq = 0,
		lastResonance = 0,
		replicateAccum = 0,
		economyAccum = 0,
		telemetryAccum = 0,
	}
	playerEngines[player.UserId] = entry
	addActiveUser(player.UserId)
	player:SetAttribute("StarlineActiveTrack", trackId)
	player:SetAttribute("StarlineActiveVehicle", vehicleId)
	return entry
end

controlRemote.OnServerEvent:Connect(function(player, payload)
	if typeof(payload) ~= "table" then
		return
	end
	local afk = afkSessions[player.UserId]
	if afk and afk.enabled then
		return
	end
	local entry = ensureEngine(player)
	entry.engine:setControl(player.UserId, payload)
end)

afkRemote.OnServerEvent:Connect(function(player)
	local session = afkSessions[player.UserId]
	if not session then
		session = AfkPilot.newSession()
		afkSessions[player.UserId] = session
	end
	session.enabled = not session.enabled
	player:SetAttribute("StarlineAfkMode", session.enabled)
	player:SetAttribute("StarlineAfkEarned", session.earnedSession)
	player:SetAttribute(
		"StarlineLastEconomyAction",
		if session.enabled then "afk_cruise_on" else "afk_cruise_off"
	)
end)

unlockRemote.OnServerEvent:Connect(function(player, trackId: any)
	if typeof(trackId) ~= "string" then
		return
	end
	local ok, reason = TrackUnlock.tryUnlock(player, trackId)
	player:SetAttribute("StarlineLastEconomyAction", reason)
	if ok and (reason == "purchased" or reason == "free" or reason == "already_unlocked") then
		EconomyStore.queueSave(player)
	end
end)

selectRemote.OnServerEvent:Connect(function(player, trackId: any)
	if typeof(trackId) ~= "string" then
		return
	end
	local ok, reason = TrackUnlock.setActiveTrack(player, trackId)
	if not ok then
		player:SetAttribute("StarlineLastEconomyAction", reason)
		return
	end
	ensureEngine(player)
	EconomyStore.queueSave(player)
	player:SetAttribute("StarlineLastEconomyAction", "track_" .. trackId)
end)

tracksRemote.OnServerInvoke = function(player)
	return TrackUnlock.listForPlayer(player)
end

buyVehicleRemote.OnServerEvent:Connect(function(player, vehicleId: any)
	if typeof(vehicleId) ~= "string" then
		return
	end
	local ok, reason = VehicleGarage.tryUnlock(player, vehicleId)
	player:SetAttribute("StarlineLastEconomyAction", reason)
	if ok then
		EconomyStore.queueSave(player)
	end
end)

equipVehicleRemote.OnServerEvent:Connect(function(player, vehicleId: any)
	if typeof(vehicleId) ~= "string" then
		return
	end
	local ok, reason = VehicleGarage.setActiveVehicle(player, vehicleId)
	if not ok then
		player:SetAttribute("StarlineLastEconomyAction", reason)
		return
	end
	ensureEngine(player)
	EconomyStore.queueSave(player)
	player:SetAttribute("StarlineLastEconomyAction", "vehicle_" .. vehicleId)
end)

listVehiclesRemote.OnServerInvoke = function(player)
	return VehicleGarage.listForPlayer(player)
end

local function onPlayerAdded(player: Player)
	EconomyStore.load(player)
	if not TrackUnlock.hasUnlock(player, "oval") then
		TrackUnlock.grantUnlock(player, "oval")
	end
	if not player:GetAttribute("StarlineActiveTrack") then
		player:SetAttribute("StarlineActiveTrack", "oval")
	end
	if not VehicleGarage.hasUnlock(player, "urban_pulse") then
		VehicleGarage.grantUnlock(player, "urban_pulse")
	end
	if not player:GetAttribute("StarlineActiveVehicle") then
		VehicleGarage.setActiveVehicle(player, "urban_pulse")
	end
	ensureEngine(player)
	afkSessions[player.UserId] = AfkPilot.newSession()
	player:SetAttribute("StarlineAfkMode", false)
	player:SetAttribute("StarlineAfkEarned", 0)
end

local function onPlayerRemoving(player: Player)
	EconomyStore.save(player)
	local entry = playerEngines[player.UserId]
	if entry then
		entry.engine.players[player.UserId] = nil
		entry.engine.controls[player.UserId] = nil
		entry.engine.flowMachines[player.UserId] = nil
	end
	playerEngines[player.UserId] = nil
	afkSessions[player.UserId] = nil
	removeActiveUser(player.UserId)
end

Players.PlayerAdded:Connect(onPlayerAdded)
Players.PlayerRemoving:Connect(onPlayerRemoving)
for _, plr in Players:GetPlayers() do
	onPlayerAdded(plr)
end

EconomyStore.startAutosave(Config.EconomyAutosaveSec)

RunService.Heartbeat:Connect(function(frameDt)
	local steps = simClock:consume(frameDt)
	if steps <= 0 then
		return
	end

	local stepDt = Config.FixedDt
	for _ = 1, steps do
		for _, userId in activeUserIds do
			local entry = playerEngines[userId]
			if not entry then
				continue
			end
			local plr = Players:GetPlayerByUserId(userId)
			if not plr then
				continue
			end
			local eng = entry.engine
			local track = entry.track
			local st = eng.players[userId]
			if not st then
				continue
			end

			local afk = afkSessions[userId]
			if afk and afk.enabled then
				local ctrl = AfkPilot.control(track, st.s, st.v, st.vEff, eng.cfg)
				eng:setControl(userId, ctrl)
			end

			local R = eng:step(stepDt)
			EconomyField.integrate(plr, stepDt, st, R, nil, nil, afk)

			local root = plr.Character and plr.Character:FindFirstChild("HumanoidRootPart") :: BasePart?
			if root then
				root.CFrame = CFrame.lookAt(st.position, st.position + track:tangent(st.s))
			end
		end
	end

	for _, userId in activeUserIds do
		local entry = playerEngines[userId]
		if not entry then
			continue
		end
		local plr = Players:GetPlayerByUserId(userId)
		if not plr then
			continue
		end
		local eng = entry.engine
		local track = entry.track
		local st = eng.players[userId]
		if not st then
			continue
		end

		entry.replicateAccum += frameDt
		entry.economyAccum += frameDt
		entry.telemetryAccum += frameDt

		local R = eng:syncR()
		local flowMachine = eng.flowMachines[userId]
		local flowState = if flowMachine then flowMachine.state else "unstable"
		local resonance = (plr:GetAttribute("StarlineResonance") or 0) :: number

		if entry.replicateAccum >= replicateInterval then
			entry.replicateAccum = 0
			entry.wireSeq += 1
			local payload = StateReplicator.buildPayload(
				st,
				track,
				R,
				flowState,
				resonance,
				entry.lastWire,
				entry.wireSeq
			)
			if payload.noop ~= true then
				entry.lastWire = payload.wire
				stateRemote:FireClient(plr, payload)
			end
		end

		if entry.economyAccum >= economyInterval then
			entry.economyAccum = 0
			if math.abs(resonance - entry.lastResonance) > 0.05 then
				entry.lastResonance = resonance
				plr:SetAttribute("StarlineResonance", resonance)
			end
			local peakFlow = plr:GetAttribute("StarlinePeakFlow") or 0
			local ff = st.coherence * st.smoothness
			if ff > peakFlow then
				plr:SetAttribute("StarlinePeakFlow", ff)
			end
		end

		if entry.telemetryAccum >= 5.0 then
			entry.telemetryAccum = 0
			TelemetrySink.maybeFlush(plr, {
				c = st.coherence,
				S = st.smoothness,
				R = R,
				resonance = resonance,
				flow = flowState,
				track = entry.trackId,
			}, frameDt)
		end
	end
end)

local stateMode = if Config.UseUnreliableState then "UnreliableRemoteEvent" else "RemoteEvent"
print(
	"[Starline] perf server | sim",
	Config.SimHz,
	"Hz | replicate",
	Config.ReplicateHz,
	"Hz | state",
	stateMode,
	"| control",
	Config.ControlHz,
	"Hz"
)
