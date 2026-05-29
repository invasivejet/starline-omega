--!strict
--[[ Resonance field Ψ_res — geometric alignment, not a buff ]]
local Config = require(script.Parent.Config)

local Resonance = {}

local function C(cfg: any?): any
	return cfg or Config
end

function Resonance.field(state: any, kappa: number, kappaAhead: number, syncR: number, cfg: any?): number
	local c = C(cfg)
	local steerA = state.steer * c.SteeringGain * math.max(math.abs(kappaAhead), 1e-6)
	local anticipErr = math.abs(kappaAhead - steerA)
	local anticipAlign = 1 / (1 + c.ResonanceKappaScale * anticipErr)
	local kappaAlign = 1 / (1 + c.ResonanceKappaScale * math.abs(state.curveError or 0))
	local geom = state.smoothness * (0.5 * anticipAlign + 0.5 * kappaAlign)
	local sync = math.clamp(syncR, 0, 1)
	local psi = geom * (c.ResonanceGeomWeight + c.ResonanceSyncWeight * sync)
	return math.clamp(psi, 0, 1)
end

return Resonance
