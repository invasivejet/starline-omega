--!strict
local Config = require(script.Parent.Config)

local Stability = {}

local function C(cfg: any?): any
	return cfg or Config
end

function Stability.apply(state: any, cfg: any?)
	local c = C(cfg)
	state.v = math.clamp(state.v, 0, c.MaxSpeedHard)
	state.coherence = math.clamp(state.coherence, 0, 1)
	state.smoothness = math.clamp(state.smoothness, 0, 1)
	state.jerk = math.clamp(state.jerk, -20, 20)
end

return Stability
