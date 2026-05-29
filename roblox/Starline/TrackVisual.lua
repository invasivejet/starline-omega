--!strict
--[[
  Builds a glowing spline mesh in Workspace (neon beams between dense samples).
]]

local TrackVisual = {}

local function makeBeam(p0: Vector3, p1: Vector3, parent: Instance, color: Color3)
	local a0 = Instance.new("Attachment")
	a0.WorldPosition = p0
	a0.Parent = parent
	local a1 = Instance.new("Attachment")
	a1.WorldPosition = p1
	a1.Parent = parent
	local beam = Instance.new("Beam")
	beam.Attachment0 = a0
	beam.Attachment1 = a1
	beam.Width0 = 0.35
	beam.Width1 = 0.35
	beam.FaceCamera = true
	beam.LightEmission = 1
	beam.Color = ColorSequence.new(color)
	beam.Transparency = NumberSequence.new(0.15)
	beam.Parent = parent
end

function TrackVisual.build(track: any, samples: number?, color: Color3?): Folder
	local n = samples or 128
	local col = color or Color3.fromRGB(80, 200, 255)
	local folder = Instance.new("Folder")
	folder.Name = "StarlineTrackVisual"
	folder.Parent = workspace

	local anchor = Instance.new("Part")
	anchor.Name = "TrackAnchor"
	anchor.Anchored = true
	anchor.CanCollide = false
	anchor.CanQuery = false
	anchor.CanTouch = false
	anchor.Transparency = 1
	anchor.Size = Vector3.new(1, 1, 1)
	anchor.Position = track:position(0)
	anchor.Parent = folder

	local step = track.length / n
	local prev = track:position(0)
	for i = 1, n do
		local s = i * step
		local pos = track:position(s)
		makeBeam(prev, pos, anchor, col)
		prev = pos
	end
	-- close loop visually
	makeBeam(prev, track:position(0), anchor, col)
	return folder
end

function TrackVisual.destroy()
	local f = workspace:FindFirstChild("StarlineTrackVisual")
	if f then
		f:Destroy()
	end
end

return TrackVisual
