--!strict
--[[ HUD — reads interpolated ClientState; economy/track hotkeys ]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")

local Starline = ReplicatedStorage:WaitForChild("Starline")
local ClientState = require(Starline.ClientState)

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")
local remotes = ReplicatedStorage:WaitForChild("StarlineRemotes")
local unlockRemote = remotes:WaitForChild("UnlockTrack") :: RemoteEvent
local selectRemote = remotes:WaitForChild("SelectTrack") :: RemoteEvent
local listTracks = remotes:WaitForChild("ListTracks") :: RemoteFunction
local afkRemote = remotes:WaitForChild("AfkToggle") :: RemoteEvent

local gui = Instance.new("ScreenGui")
gui.Name = "StarlineHud"
gui.ResetOnSpawn = false
gui.Parent = playerGui

local frame = Instance.new("Frame")
frame.Size = UDim2.fromOffset(340, 168)
frame.Position = UDim2.new(0, 12, 0, 12)
frame.BackgroundColor3 = Color3.fromRGB(12, 14, 22)
frame.BackgroundTransparency = 0.2
frame.BorderSizePixel = 0
frame.Parent = gui

local corner = Instance.new("UICorner")
corner.CornerRadius = UDim.new(0, 8)
corner.Parent = frame

local label = Instance.new("TextLabel")
label.Size = UDim2.new(1, -16, 1, -16)
label.Position = UDim2.fromOffset(8, 8)
label.BackgroundTransparency = 1
label.TextColor3 = Color3.fromRGB(220, 235, 255)
label.TextXAlignment = Enum.TextXAlignment.Left
label.TextYAlignment = Enum.TextYAlignment.Top
label.Font = Enum.Font.GothamMedium
label.TextSize = 14
label.TextWrapped = true
label.Text = "STARLINE Ω"
label.Parent = frame

local lastAction = ""

local function refresh()
	local snap = ClientState.sampleInterpolated()
	local track = (player:GetAttribute("StarlineActiveTrack") or "oval") :: string
	local vehicle = (player:GetAttribute("StarlineVehicleName") or "Urban Pulse") :: string
	local afkOn = player:GetAttribute("StarlineAfkMode") == true
	local afkEarned = (player:GetAttribute("StarlineAfkEarned") or 0) :: number
	local afkLine = if afkOn then "AFK CRUISE · earned " .. string.format("%.1f", afkEarned) else "active drive"
	label.Text = string.format(
		"ℛ %.1f (resonance cash)  ·  %s\n"
			.. "c %.2f  ·  %s  ·  Ψ %.2f  ·  v %.0f\n"
			.. "ride: %s  ·  track: %s\n"
			.. "[B] garage  [F] AFK  [U] circuit (40 ℛ)\n"
			.. "[1] oval  [2] circuit\n"
			.. "%s",
		snap.resonance,
		afkLine,
		snap.coherence,
		snap.flowState,
		snap.resonanceField,
		snap.vEff,
		vehicle,
		track,
		lastAction
	)
end

RunService.RenderStepped:Connect(function()
	refresh()
end)

player:GetAttributeChangedSignal("StarlineLastEconomyAction"):Connect(function()
	lastAction = (player:GetAttribute("StarlineLastEconomyAction") or "") :: string
end)

task.spawn(function()
	pcall(function()
		listTracks:InvokeServer()
	end)
	refresh()
end)

UserInputService.InputBegan:Connect(function(input, processed)
	if processed or UserInputService:GetFocusedTextBox() then
		return
	end
	if input.KeyCode == Enum.KeyCode.U then
		unlockRemote:FireServer("circuit")
		lastAction = "unlocking circuit…"
	elseif input.KeyCode == Enum.KeyCode.One then
		selectRemote:FireServer("oval")
		lastAction = "select oval"
	elseif input.KeyCode == Enum.KeyCode.Two then
		selectRemote:FireServer("circuit")
		lastAction = "select circuit"
	elseif input.KeyCode == Enum.KeyCode.F then
		afkRemote:FireServer()
		lastAction = "toggle AFK cruise"
	end
end)

player:GetAttributeChangedSignal("StarlineAfkMode"):Connect(refresh)
player:GetAttributeChangedSignal("StarlineAfkEarned"):Connect(refresh)

refresh()
