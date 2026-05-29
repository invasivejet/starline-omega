--!strict
local Config = require(script.Parent.Config)

local PhaseSync = {}

local function C(cfg: any?): any
	return cfg or Config
end

function PhaseSync.updatePhase(state: any, dt: number, cfg: any?)
	local c = C(cfg)
	local twoPi = math.pi * 2
	state.phase = (state.phase + state.v * dt * c.Omega) % twoPi
end

function PhaseSync.orderParameter(phases: { number }): number
	if #phases == 0 then
		return 0
	end
	local re, im = 0, 0
	for _, ph in phases do
		re += math.cos(ph)
		im += math.sin(ph)
	end
	re /= #phases
	im /= #phases
	return math.sqrt(re * re + im * im)
end

function PhaseSync.slipstreamDragFactor(R: number, cfg: any?): number
	local c = C(cfg)
	return math.max(0, 1 - c.SyncSlipstream * R)
end

return PhaseSync
