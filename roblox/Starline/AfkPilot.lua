--!strict
--[[ AFK Cruise — server authoritative autopilot + earn rules ]]
local Config = require(script.Parent.Config)

local AfkPilot = {}

export type AfkSession = {
	enabled: boolean,
	earnedSession: number,
}

function AfkPilot.newSession(): AfkSession
	return { enabled = false, earnedSession = 0 }
end

function AfkPilot.quality(c: number, S: number): number
	if c < Config.AfkMinCoherence then
		return 0
	end
	local q = S * math.min(c, Config.AfkCoherenceCap)
	return math.clamp(q, 0, 1)
end

function AfkPilot.earnScale(quality: number): number
	return quality * Config.AfkEarnMultiplier
end

function AfkPilot.capRemaining(session: AfkSession): number
	return math.max(0, Config.AfkSessionCap - session.earnedSession)
end

function AfkPilot.control(
	track: any,
	s: number,
	v: number,
	vEff: number,
	motionCfg: any?
): { throttle: number, brake: number, steer: number }
	local m = motionCfg or Config
	local ds = m.AnticipationDs + m.AnticipationSpeedScale * math.max(vEff, 0)
	local kAhead = track:curvature(s + ds)
	local steer = math.clamp(kAhead / m.SteeringGain, -1, 1)
	local throttle = Config.AfkThrottle
	local brake = 0
	if v < Config.AfkMinCruiseSpeed then
		throttle = Config.AfkThrottle
	elseif v > Config.AfkMaxCruiseSpeed then
		local over = v - Config.AfkMaxCruiseSpeed
		throttle = Config.AfkThrottle * math.max(0.12, 1 - over / 25)
	end
	if v > Config.AfkBrakeAboveSpeed then
		throttle = 0
		brake = Config.AfkBrake
	end
	return { throttle = throttle, brake = brake, steer = steer }
end

return AfkPilot
