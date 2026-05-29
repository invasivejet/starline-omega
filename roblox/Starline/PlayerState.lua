--!strict
local PlayerState = {}
PlayerState.__index = PlayerState

export type PlayerState = {
	s: number,
	v: number,
	a: number,
	jerk: number,
	phase: number,
	coherence: number,
	steer: number,
	throttle: number,
	brake: number,
	aPrev: number,
	steerPrev: number,
	position: Vector3,
	smoothness: number,
	instability: number,
	vEff: number,
	resonance: number,
}

function PlayerState.new(s0: number?): PlayerState
	return {
		s = s0 or 0,
		v = 0,
		a = 0,
		jerk = 0,
		phase = 0,
		coherence = 0,
		steer = 0,
		throttle = 0,
		brake = 0,
		aPrev = 0,
		steerPrev = 0,
		position = Vector3.zero,
		smoothness = 0,
		instability = 0,
		vEff = 0,
		resonance = 0,
	}
end

function PlayerState.clampCoherence(self: PlayerState)
	self.coherence = math.clamp(self.coherence, 0, 1)
end

function PlayerState.effectiveSpeed(self: PlayerState, gamma: number): number
	return self.v * (1 + gamma * self.coherence)
end

return PlayerState
