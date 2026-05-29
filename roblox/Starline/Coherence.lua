--!strict
local Config = require(script.Parent.Config)

local Coherence = {}

local function C(cfg: any?): any
	return cfg or Config
end

function Coherence.update(
	state: any,
	dt: number,
	S: number,
	instability: number,
	resonance: number?,
	noise: number?,
	cfg: any?
): number
	local c = C(cfg)
	local coh = state.coherence
	local pwr = math.max(c.CoherencePower, 1.01)
	local resMod = 0.5 + 0.5 * math.clamp(resonance or 0, 0, 1)
	local gain = c.Alpha * S * ((1 - coh) ^ pwr) * resMod * dt
	local loss = c.Beta * instability * dt
	local noiseLoss = c.NoisePenalty * math.max(noise or 0, 0) * dt
	state.coherence = coh + gain - loss - noiseLoss
	state:clampCoherence()
	return state.coherence
end

return Coherence
