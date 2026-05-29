--!strict
--[[
  Track as musical-geometric score — resonance zones, torsion events.
]]

export type ResonanceZone = {
	sStart: number,
	sEnd: number,
	label: string,
	boost: number,
}

export type TrackScore = {
	name: string,
	resonanceZones: { ResonanceZone },
}

local TrackScore = {}

function TrackScore.new(name: string?): TrackScore
	return {
		name = name or "untitled",
		resonanceZones = {},
	}
end

function TrackScore.resonanceBoostAt(score: TrackScore, s: number): number
	local boost = 0
	for _, z in score.resonanceZones do
		if s >= z.sStart and s <= z.sEnd then
			boost = math.max(boost, z.boost)
		end
	end
	return boost
end

return TrackScore
