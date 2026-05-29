--!strict
local Config = require(script.Parent.Config)

local Smoothness = {}

local function C(cfg: any?): any
	return cfg or Config
end

function Smoothness.steeringResponse(state: any, kappa: number, cfg: any?): number
	local c = C(cfg)
	local resp = state.steer * c.SteeringGain * math.max(math.abs(kappa), 1e-6)
	state.steeringResponse = resp
	return resp
end

function Smoothness.curveError(state: any, kappa: number, steerResp: number): number
	local err = math.abs(kappa - steerResp)
	state.curveError = err
	return err
end

function Smoothness.anticipatoryKappa(track: any, s: number, vEff: number, cfg: any?): (number, number)
	local c = C(cfg)
	local ds = c.AnticipationDs + c.AnticipationSpeedScale * math.max(vEff, 0)
	local k0 = track:curvature(s)
	local k1 = track:curvature(s + ds)
	return k0, k1
end

function Smoothness.score(state: any, kappa: number, kappaAhead: number?, cfg: any?): number
	local c = C(cfg)
	local wA = if kappaAhead ~= nil then c.AnticipationBlend else 0
	local steerResp = Smoothness.steeringResponse(state, kappa, c)
	local cerr = Smoothness.curveError(state, kappa, steerResp)
	if kappaAhead ~= nil and wA > 0 then
		local steerA = Smoothness.steeringResponse(state, kappaAhead, c)
		local cerrA = Smoothness.curveError(state, kappaAhead, steerA)
		cerr = (1 - wA) * cerr + wA * cerrA
	end
	local penalty = c.JerkWeight * math.abs(state.jerk) + c.CurveWeight * cerr
	state.smoothness = math.exp(-penalty)
	return state.smoothness
end

function Smoothness.instability(state: any, cfg: any?): number
	local c = C(cfg)
	local dsteer = math.abs(state.steer - state.steerPrev)
	state.steerPrev = state.steer
	local inst = c.SteerInstabilityWeight * dsteer + c.BrakeInstabilityWeight * state.brake
	state.instability = inst
	return inst
end

return Smoothness
