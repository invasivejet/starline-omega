--!strict
--[[ No false reward: ∂c/∂noise < 0 ]]
local Config = require(script.Parent.Config)

local InputNoise = {}

local function C(cfg: any?): any
	return cfg or Config
end

function InputNoise.metric(state: any, cfg: any?): number
	local c = C(cfg)
	local dsteer = math.abs(state.steer - (state.steerPrev or 0))
	local oscillation = dsteer * math.abs(state.steer)
	local brakeSpam = state.brake * dsteer
	local jerkNoise = math.min(1, math.abs(state.jerk) / math.max(c.JerkNoiseScale, 1e-6))
	return c.NoiseSteerWeight * dsteer
		+ c.NoiseOscillationWeight * oscillation
		+ c.NoiseBrakeWeight * brakeSpam
		+ c.NoiseJerkWeight * jerkNoise
end

return InputNoise
