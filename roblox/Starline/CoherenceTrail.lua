--!strict
--[[
  Client-side motion trail whose brightness scales with StarlineCoherence attribute.
]]

local RunService = game:GetService("RunService")

local CoherenceTrail = {}
CoherenceTrail.__index = CoherenceTrail

export type CoherenceTrail = typeof(setmetatable({} :: {
	_player: Player,
	_parts: { BasePart },
	_max: number,
}, CoherenceTrail))

function CoherenceTrail.new(player: Player, maxParts: number?): CoherenceTrail
	return setmetatable({
		_player = player,
		_parts = {},
		_max = maxParts or 24,
	}, CoherenceTrail)
end

function CoherenceTrail.push(self: CoherenceTrail, position: Vector3, coherence: number)
	local p = Instance.new("Part")
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.Size = Vector3.new(0.6, 0.6, 2.2)
	p.Material = Enum.Material.Neon
	p.Color = Color3.fromRGB(80, 180, 255):Lerp(Color3.fromRGB(255, 120, 220), 1 - coherence)
	p.Transparency = 0.25 + 0.5 * (1 - coherence)
	p.CFrame = CFrame.new(position)
	p.Parent = workspace

	table.insert(self._parts, p)
	while #self._parts > self._max do
		local old = table.remove(self._parts, 1)
		if old then
			old:Destroy()
		end
	end
end

function CoherenceTrail.destroy(self: CoherenceTrail)
	for _, p in self._parts do
		p:Destroy()
	end
	table.clear(self._parts)
end

return CoherenceTrail
