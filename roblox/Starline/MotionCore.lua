--!strict
local Config = require(script.Parent.Config)
local PlayerState = require(script.Parent.PlayerState)

local MotionCore = {}

local function C(cfg: any?): any
	return cfg or Config
end

function MotionCore.updateVelocity(state: any, dt: number, dragScale: number?, cfg: any?)
	local c = C(cfg)
	local ds = dragScale or 1
	local thrust = state.throttle * c.ThrottleAccel - state.brake * c.BrakeDecel
	state.a = thrust
	state.v = state.v + state.a * dt
	state.v = state.v - c.Drag * ds * state.v * dt
	state.v = math.clamp(state.v, 0, c.MaxSpeed)
end

function MotionCore.updateJerk(state: any, dt: number)
	if dt <= 0 then
		state.jerk = 0
		return
	end
	state.jerk = (state.a - state.aPrev) / dt
	state.aPrev = state.a
end

function MotionCore.advanceArcLength(state: any, trackLength: number, dt: number, cfg: any?)
	local c = C(cfg)
	state.vEff = PlayerState.effectiveSpeed(state, c.Gamma)
	state.s = (state.s + state.vEff * dt) % trackLength
end

return MotionCore
