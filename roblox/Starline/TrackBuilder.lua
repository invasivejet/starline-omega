--!strict
local SplineTrack = require(script.Parent.SplineTrack)
local TrackUnlock = require(script.Parent.TrackUnlock)

local TrackBuilder = {}

function TrackBuilder.fromWorkspace(trackId: string): any
	local def = TrackUnlock.getDef(trackId)
	if not def then
		return SplineTrack.oval(200, 5, 16)
	end
	if def.waypointFolder then
		local folder = workspace:FindFirstChild(def.waypointFolder)
		if folder then
			local wps: { Vector3 } = {}
			for _, inst in folder:GetChildren() do
				if inst:IsA("BasePart") then
					table.insert(wps, inst.Position)
				end
			end
			if #wps >= 4 then
				return SplineTrack.new(wps)
			end
		end
	end
	local r = def.fallbackOvalRadius or 200
	return SplineTrack.oval(r, 5, 16)
end

return TrackBuilder
