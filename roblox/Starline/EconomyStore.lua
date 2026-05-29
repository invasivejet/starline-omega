--!strict
--[[
  DataStore persistence for geometric economy (ℛ + unlocks).
  Studio: enable "Enable Studio Access to API Services" for local tests.
]]

local DataStoreService = game:GetService("DataStoreService")
local RunService = game:GetService("RunService")

local EconomyStore = {}

local STORE_NAME = "StarlineEconomy_v1"
local AUTOSAVE_INTERVAL = 120

local _store = DataStoreService:GetDataStore(STORE_NAME)
local _saveQueued: { [number]: boolean } = {}

export type SaveData = {
	resonance: number,
	resonancePeak: number,
	unlocks: { string },
	activeTrack: string,
	vehicleUnlocks: { string },
	activeVehicle: string,
}

local function defaultData(): SaveData
	return {
		resonance = 0,
		resonancePeak = 0,
		unlocks = { "oval" },
		activeTrack = "oval",
		vehicleUnlocks = { "urban_pulse" },
		activeVehicle = "urban_pulse",
	}
end

local function unlocksToString(unlocks: { string }): string
	return table.concat(unlocks, ",")
end

local function unlocksFromString(s: string): { string }
	local out: { string } = {}
	for part in string.gmatch(s, "[^,]+") do
		table.insert(out, part)
	end
	if #out == 0 then
		return { "oval" }
	end
	return out
end

function EconomyStore.applyToPlayer(player: Player, data: SaveData)
	player:SetAttribute("StarlineResonance", data.resonance)
	player:SetAttribute("StarlineResonancePeak", data.resonancePeak)
	player:SetAttribute("StarlineUnlocks", unlocksToString(data.unlocks))
	player:SetAttribute("StarlineActiveTrack", data.activeTrack)
	player:SetAttribute("StarlineVehicleUnlocks", unlocksToString(data.vehicleUnlocks))
	player:SetAttribute("StarlineActiveVehicle", data.activeVehicle)
end

function EconomyStore.readFromPlayer(player: Player): SaveData
	return {
		resonance = (player:GetAttribute("StarlineResonance") or 0) :: number,
		resonancePeak = (player:GetAttribute("StarlineResonancePeak") or 0) :: number,
		unlocks = unlocksFromString((player:GetAttribute("StarlineUnlocks") or "oval") :: string),
		activeTrack = (player:GetAttribute("StarlineActiveTrack") or "oval") :: string,
		vehicleUnlocks = unlocksFromString((player:GetAttribute("StarlineVehicleUnlocks") or "urban_pulse") :: string),
		activeVehicle = (player:GetAttribute("StarlineActiveVehicle") or "urban_pulse") :: string,
	}
end

function EconomyStore.load(player: Player): SaveData
	if RunService:IsStudio() then
		local key = "u_" .. tostring(player.UserId)
		local ok, result = pcall(function()
			return _store:GetAsync(key)
		end)
		if ok and typeof(result) == "table" then
			local data = defaultData()
			data.resonance = result.resonance or 0
			data.resonancePeak = result.resonancePeak or 0
			data.unlocks = result.unlocks or { "oval" }
			data.activeTrack = result.activeTrack or "oval"
			data.vehicleUnlocks = result.vehicleUnlocks or { "urban_pulse" }
			data.activeVehicle = result.activeVehicle or "urban_pulse"
			EconomyStore.applyToPlayer(player, data)
			return data
		end
		local data = defaultData()
		EconomyStore.applyToPlayer(player, data)
		return data
	end
	local key = "u_" .. tostring(player.UserId)
	local ok, result = pcall(function()
		return _store:GetAsync(key)
	end)
	local data = defaultData()
	if ok and typeof(result) == "table" then
		data.resonance = result.resonance or 0
		data.resonancePeak = result.resonancePeak or 0
		data.unlocks = result.unlocks or { "oval" }
		data.activeTrack = result.activeTrack or "oval"
		data.vehicleUnlocks = result.vehicleUnlocks or { "urban_pulse" }
		data.activeVehicle = result.activeVehicle or "urban_pulse"
	end
	EconomyStore.applyToPlayer(player, data)
	return data
end

function EconomyStore.save(player: Player): boolean
	local data = EconomyStore.readFromPlayer(player)
	if RunService:IsStudio() then
		return true
	end
	local key = "u_" .. tostring(player.UserId)
	local ok = pcall(function()
		_store:SetAsync(key, data)
	end)
	return ok
end

function EconomyStore.queueSave(player: Player)
	_saveQueued[player.UserId] = true
end

function EconomyStore.startAutosave(intervalSec: number?)
	local interval = intervalSec or AUTOSAVE_INTERVAL
	task.spawn(function()
		while true do
			task.wait(interval)
			for userId, _ in _saveQueued do
				local plr = game:GetService("Players"):GetPlayerByUserId(userId)
				if plr then
					EconomyStore.save(plr)
				end
				_saveQueued[userId] = nil
			end
		end
	end)
end

return EconomyStore
