--!strict
--[[ Fixed simulation timestep accumulator (deterministic, capped catch-up). ]]

local Config = require(script.Parent.Config)

local SimClock = {}
SimClock.__index = SimClock

export type SimClock = typeof(setmetatable({} :: {
	simDt: number,
	maxSteps: number,
	maxCatchupSec: number,
	accumulator: number,
	simTime: number,
}, SimClock))

function SimClock.new(simDt: number, maxSteps: number, maxCatchupSec: number?): SimClock
	return setmetatable({
		simDt = simDt,
		maxSteps = maxSteps,
		maxCatchupSec = maxCatchupSec or Config.MaxSimCatchupSec or 0.25,
		accumulator = 0,
		simTime = 0,
	}, SimClock)
end

function SimClock.consume(self: SimClock, frameDt: number): number
	self.accumulator += frameDt
	if self.accumulator > self.maxCatchupSec then
		self.accumulator = self.maxCatchupSec
	end
	local steps = 0
	while self.accumulator >= self.simDt and steps < self.maxSteps do
		self.accumulator -= self.simDt
		self.simTime += self.simDt
		steps += 1
	end
	if steps >= self.maxSteps then
		self.accumulator = 0
	end
	return steps
end

function SimClock.alpha(self: SimClock): number
	if self.simDt <= 0 then
		return 0
	end
	return self.accumulator / self.simDt
end

return SimClock
