--!strict
--[[
  High-performance client:
  - throttled control uplink
  - UnreliableRemoteEvent state downlink
  - interpolated presentation (FOV, audio, trail, camera hint)
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")

local Starline = ReplicatedStorage:WaitForChild("Starline")
local CoherenceTrail = require(Starline.CoherenceTrail)
local MusicController = require(Starline.MusicController)
local ClientState = require(Starline.ClientState)
local Config = require(Starline.Config)

local player = Players.LocalPlayer
local remotes = ReplicatedStorage:WaitForChild("StarlineRemotes")
local controlRemote = remotes:WaitForChild("Control") :: RemoteEvent

local stateUnreliable = remotes:FindFirstChild("StateUnreliable")
local stateReliable = remotes:FindFirstChild("State")

local throttle, brake, steer = 0, 0, 0
local controlAccum = 0
local controlInterval = 1 / Config.ControlHz
local trailAccum = 0
local trailInterval = 1 / Config.TrailHz

local trail = CoherenceTrail.new(player, 24)
local music = MusicController.new()

local lastControl = { throttle = -1, brake = -1, steer = -1 }

local function onStatePayload(payload: any)
	ClientState.pushPayload(payload)
	ClientState.syncAttributes(player)
end

if Config.UseUnreliableState and stateUnreliable and stateUnreliable:IsA("UnreliableRemoteEvent") then
	stateUnreliable.OnClientEvent:Connect(onStatePayload)
elseif stateReliable and stateReliable:IsA("RemoteEvent") then
	stateReliable.OnClientEvent:Connect(onStatePayload)
else
	warn("[Starline] no State remote found; waiting for server")
	task.spawn(function()
		local u = remotes:WaitForChild("StateUnreliable", 30)
		if u and u:IsA("UnreliableRemoteEvent") then
			u.OnClientEvent:Connect(onStatePayload)
		end
	end)
end

UserInputService.InputBegan:Connect(function(input, processed)
	if processed then
		return
	end
	if input.KeyCode == Enum.KeyCode.W or input.KeyCode == Enum.KeyCode.Up then
		throttle = 1
	elseif input.KeyCode == Enum.KeyCode.S or input.KeyCode == Enum.KeyCode.Down then
		brake = 1
	elseif input.KeyCode == Enum.KeyCode.A or input.KeyCode == Enum.KeyCode.Left then
		steer = -1
	elseif input.KeyCode == Enum.KeyCode.D or input.KeyCode == Enum.KeyCode.Right then
		steer = 1
	end
end)

UserInputService.InputEnded:Connect(function(input)
	if input.KeyCode == Enum.KeyCode.W or input.KeyCode == Enum.KeyCode.Up then
		throttle = 0
	elseif input.KeyCode == Enum.KeyCode.S or input.KeyCode == Enum.KeyCode.Down then
		brake = 0
	elseif input.KeyCode == Enum.KeyCode.A or input.KeyCode == Enum.KeyCode.Left then
		if steer < 0 then
			steer = 0
		end
	elseif input.KeyCode == Enum.KeyCode.D or input.KeyCode == Enum.KeyCode.Right then
		if steer > 0 then
			steer = 0
		end
	end
end)

controlRemote:FireServer({ throttle = 0, brake = 0, steer = 0 })

RunService.Heartbeat:Connect(function(dt)
	controlAccum += dt
	if controlAccum >= controlInterval then
		controlAccum = 0
		if throttle ~= lastControl.throttle or brake ~= lastControl.brake or steer ~= lastControl.steer then
			lastControl = { throttle = throttle, brake = brake, steer = steer }
			controlRemote:FireServer(lastControl)
		end
	end
end)

RunService.RenderStepped:Connect(function(dt)
	local snap = ClientState.sampleInterpolated()

	local cam = workspace.CurrentCamera
	if cam then
		cam.FieldOfView = 68 + 14 * snap.coherence
		local hint = snap.look - snap.position
		if hint.Magnitude > 1 then
			local target = CFrame.lookAt(snap.position, snap.look)
			cam.CFrame = cam.CFrame:Lerp(target, math.clamp(8 * dt, 0, 0.35))
		end
	end

	music:updateFromSnap(snap)

	trailAccum += dt
	if trailAccum >= trailInterval then
		trailAccum = 0
		local char = player.Character
		local root = char and char:FindFirstChild("HumanoidRootPart") :: BasePart?
		if root then
			trail:push(root.Position, snap.coherence)
		end
	end
end)

player.CharacterRemoving:Connect(function()
	trail:destroy()
end)
