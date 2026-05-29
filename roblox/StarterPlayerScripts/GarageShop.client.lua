--!strict
--[[ Garage — buy & equip vehicles with ℛ. Press B to open. ]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")
local remotes = ReplicatedStorage:WaitForChild("StarlineRemotes")
local listVehicles = remotes:WaitForChild("ListVehicles") :: RemoteFunction
local buyVehicle = remotes:WaitForChild("BuyVehicle") :: RemoteEvent
local equipVehicle = remotes:WaitForChild("EquipVehicle") :: RemoteEvent

type VehicleRow = {
	id: string,
	name: string,
	tagline: string,
	category: string,
	inspiredBy: string,
	cost: number,
	owned: boolean,
	equipped: boolean,
	stats: { [string]: number },
}

local gui = Instance.new("ScreenGui")
gui.Name = "StarlineGarage"
gui.ResetOnSpawn = false
gui.Enabled = false
gui.Parent = playerGui

local backdrop = Instance.new("Frame")
backdrop.Size = UDim2.new(1, 0, 1, 0)
backdrop.BackgroundColor3 = Color3.fromRGB(0, 0, 0)
backdrop.BackgroundTransparency = 0.45
backdrop.BorderSizePixel = 0
backdrop.Parent = gui

local panel = Instance.new("Frame")
panel.Size = UDim2.fromOffset(420, 480)
panel.Position = UDim2.new(0.5, -210, 0.5, -240)
panel.BackgroundColor3 = Color3.fromRGB(14, 16, 26)
panel.BorderSizePixel = 0
panel.Parent = gui

local panelCorner = Instance.new("UICorner")
panelCorner.CornerRadius = UDim.new(0, 10)
panelCorner.Parent = panel

local title = Instance.new("TextLabel")
title.Size = UDim2.new(1, -24, 0, 36)
title.Position = UDim2.fromOffset(12, 8)
title.BackgroundTransparency = 1
title.Font = Enum.Font.GothamBold
title.TextSize = 18
title.TextXAlignment = Enum.TextXAlignment.Left
title.TextColor3 = Color3.fromRGB(235, 245, 255)
title.Text = "GARAGE — formulate your ride"
title.Parent = panel

local balance = Instance.new("TextLabel")
balance.Size = UDim2.new(1, -24, 0, 20)
balance.Position = UDim2.fromOffset(12, 42)
balance.BackgroundTransparency = 1
balance.Font = Enum.Font.GothamMedium
balance.TextSize = 13
balance.TextXAlignment = Enum.TextXAlignment.Left
balance.TextColor3 = Color3.fromRGB(160, 200, 255)
balance.Text = "ℛ 0"
balance.Parent = panel

local hint = Instance.new("TextLabel")
hint.Size = UDim2.new(1, -24, 0, 32)
hint.Position = UDim2.fromOffset(12, 62)
hint.BackgroundTransparency = 1
hint.Font = Enum.Font.Gotham
hint.TextSize = 11
hint.TextWrapped = true
hint.TextXAlignment = Enum.TextXAlignment.Left
hint.TextColor3 = Color3.fromRGB(140, 150, 170)
hint.Text = "Fictional marques · stats = handling on the spline. [B] close"
hint.Parent = panel

local scroll = Instance.new("ScrollingFrame")
scroll.Size = UDim2.new(1, -24, 1, -108)
scroll.Position = UDim2.fromOffset(12, 96)
scroll.BackgroundTransparency = 1
scroll.BorderSizePixel = 0
scroll.ScrollBarThickness = 6
scroll.CanvasSize = UDim2.fromOffset(0, 0)
scroll.Parent = panel

local listLayout = Instance.new("UIListLayout")
listLayout.Padding = UDim.new(0, 8)
listLayout.SortOrder = Enum.SortOrder.LayoutOrder
listLayout.Parent = scroll

local catalog: { VehicleRow } = {}

local function formatStats(stats: { [string]: number }): string
	local keys = { "MaxSpeed", "SteeringGain", "ThrottleAccel", "Drag", "Gamma" }
	local parts = {}
	for _, key in keys do
		local v = stats[key]
		if v then
			table.insert(parts, key .. " " .. tostring(v))
		end
	end
	if #parts == 0 then
		return "stock coil"
	end
	return table.concat(parts, " · ")
end

local function clearRows()
	for _, child in scroll:GetChildren() do
		if child:IsA("Frame") then
			child:Destroy()
		end
	end
end

local function makeRow(row: VehicleRow, order: number)
	local card = Instance.new("Frame")
	card.Name = row.id
	card.Size = UDim2.new(1, -4, 0, 108)
	card.BackgroundColor3 = if row.equipped
		then Color3.fromRGB(28, 42, 58)
		else Color3.fromRGB(22, 24, 34)
	card.BorderSizePixel = 0
	card.LayoutOrder = order
	card.Parent = scroll

	local cardCorner = Instance.new("UICorner")
	cardCorner.CornerRadius = UDim.new(0, 6)
	cardCorner.Parent = card

	local nameLbl = Instance.new("TextLabel")
	nameLbl.Size = UDim2.new(1, -12, 0, 22)
	nameLbl.Position = UDim2.fromOffset(8, 6)
	nameLbl.BackgroundTransparency = 1
	nameLbl.Font = Enum.Font.GothamBold
	nameLbl.TextSize = 14
	nameLbl.TextXAlignment = Enum.TextXAlignment.Left
	nameLbl.TextColor3 = Color3.fromRGB(220, 235, 255)
	nameLbl.Text = row.name .. if row.equipped then "  ✓" else ""
	nameLbl.Parent = card

	local catLbl = Instance.new("TextLabel")
	catLbl.Size = UDim2.new(1, -12, 0, 16)
	catLbl.Position = UDim2.fromOffset(8, 26)
	catLbl.BackgroundTransparency = 1
	catLbl.Font = Enum.Font.Gotham
	catLbl.TextSize = 11
	catLbl.TextXAlignment = Enum.TextXAlignment.Left
	catLbl.TextColor3 = Color3.fromRGB(130, 180, 220)
	catLbl.Text = row.category .. " · " .. row.inspiredBy
	catLbl.Parent = card

	local tagLbl = Instance.new("TextLabel")
	tagLbl.Size = UDim2.new(1, -12, 0, 28)
	tagLbl.Position = UDim2.fromOffset(8, 42)
	tagLbl.BackgroundTransparency = 1
	tagLbl.Font = Enum.Font.Gotham
	tagLbl.TextSize = 11
	tagLbl.TextWrapped = true
	tagLbl.TextXAlignment = Enum.TextXAlignment.Left
	tagLbl.TextColor3 = Color3.fromRGB(170, 180, 195)
	tagLbl.Text = row.tagline .. "\n" .. formatStats(row.stats)
	tagLbl.Parent = card

	local action = Instance.new("TextButton")
	action.Size = UDim2.fromOffset(96, 28)
	action.Position = UDim2.new(1, -104, 1, -36)
	action.BackgroundColor3 = Color3.fromRGB(50, 90, 140)
	action.Font = Enum.Font.GothamMedium
	action.TextSize = 12
	action.TextColor3 = Color3.fromRGB(255, 255, 255)
	action.Parent = card

	local actionCorner = Instance.new("UICorner")
	actionCorner.CornerRadius = UDim.new(0, 6)
	actionCorner.Parent = action

	if row.equipped then
		action.Text = "Equipped"
		action.AutoButtonColor = false
		action.BackgroundColor3 = Color3.fromRGB(40, 55, 70)
	elseif row.owned then
		action.Text = "Equip"
		action.MouseButton1Click:Connect(function()
			equipVehicle:FireServer(row.id)
		end)
	else
		action.Text = if row.cost <= 0 then "Claim" else (tostring(row.cost) .. " ℛ")
		action.MouseButton1Click:Connect(function()
			buyVehicle:FireServer(row.id)
			if row.cost <= 0 then
				task.wait(0.15)
				equipVehicle:FireServer(row.id)
			end
		end)
	end
end

local function refresh()
	local R = (player:GetAttribute("StarlineResonance") or 0) :: number
	balance.Text = string.format("Balance: ℛ %.1f", R)
	clearRows()
	local ok, rows = pcall(function()
		return listVehicles:InvokeServer()
	end)
	if not ok or typeof(rows) ~= "table" then
		return
	end
	catalog = rows :: { VehicleRow }
	local order = 0
	for _, row in catalog do
		order += 1
		makeRow(row, order)
	end
	scroll.CanvasSize = UDim2.fromOffset(0, listLayout.AbsoluteContentSize.Y + 8)
end

listLayout:GetPropertyChangedSignal("AbsoluteContentSize"):Connect(function()
	scroll.CanvasSize = UDim2.fromOffset(0, listLayout.AbsoluteContentSize.Y + 8)
end)

local function toggle()
	gui.Enabled = not gui.Enabled
	if gui.Enabled then
		refresh()
	end
end

UserInputService.InputBegan:Connect(function(input, processed)
	if processed or UserInputService:GetFocusedTextBox() then
		return
	end
	if input.KeyCode == Enum.KeyCode.B then
		toggle()
	end
end)

player:GetAttributeChangedSignal("StarlineResonance"):Connect(function()
	if gui.Enabled then
		refresh()
	end
end)
player:GetAttributeChangedSignal("StarlineLastEconomyAction"):Connect(function()
	if gui.Enabled then
		task.defer(refresh)
	end
end)
player:GetAttributeChangedSignal("StarlineActiveVehicle"):Connect(function()
	if gui.Enabled then
		task.defer(refresh)
	end
end)
