--!strict
--[[
  Test-drive bootstrap — visible floor, spawn hint, control print.
  Safe to remove for published places with custom maps.
]]

local Players = game:GetService("Players")

local function ensureFloor()
	if workspace:FindFirstChild("StarlineTestFloor") then
		return
	end
	local floor = Instance.new("Part")
	floor.Name = "StarlineTestFloor"
	floor.Anchored = true
	floor.Size = Vector3.new(512, 1, 512)
	floor.Position = Vector3.new(0, -0.5, 0)
	floor.Color = Color3.fromRGB(28, 32, 42)
	floor.Material = Enum.Material.SmoothPlastic
	floor.Parent = workspace
end

local function printControls(plr: Player)
	print(
		("[Starline] Welcome %s — WASD drive | B garage | F AFK | U unlock circuit | 1 oval | 2 circuit"):format(
			plr.Name
		)
	)
end

ensureFloor()

Players.PlayerAdded:Connect(function(plr)
	task.defer(printControls, plr)
end)

for _, plr in Players:GetPlayers() do
	printControls(plr)
end

print("[Starline] Test-drive bootstrap ready — press Play and drive the glowing track")
