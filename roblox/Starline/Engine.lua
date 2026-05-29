--!strict
--[[
  Coherent Motion Engine — authoritative server tick.
]]

local Config = require(script.Parent.Config)
local SplineTrack = require(script.Parent.SplineTrack)
local PlayerState = require(script.Parent.PlayerState)
local MotionCore = require(script.Parent.MotionCore)
local Smoothness = require(script.Parent.Smoothness)
local Coherence = require(script.Parent.Coherence)
local PhaseSync = require(script.Parent.PhaseSync)
local AudioField = require(script.Parent.AudioField)
local Resonance = require(script.Parent.Resonance)
local InputNoise = require(script.Parent.InputNoise)
local Flow = require(script.Parent.Flow)
local Stability = require(script.Parent.Stability)

export type ControlInput = {
	throttle: number,
	brake: number,
	steer: number,
}

local Engine = {}
Engine.__index = Engine

export type Engine = typeof(setmetatable({} :: {
	track: any,
	cfg: any,
	flowMachines: { [number]: any },
	players: { [number]: any },
	controls: { [number]: ControlInput },
	time: number,
}, Engine))

function Engine.new(track: any, motionCfg: any?): Engine
	return setmetatable({
		track = track,
		cfg = motionCfg or Config,
		flowMachines = {},
		players = {},
		controls = {},
		time = 0,
	}, Engine)
end

function Engine.addPlayer(self: Engine, userId: number, s0: number?)
	local st = PlayerState.new(s0)
	st.position = self.track:position(st.s)
	self.players[userId] = st
	self.flowMachines[userId] = Flow.newMachine()
	self.controls[userId] = { throttle = 0, brake = 0, steer = 0 }
	return st
end

function Engine.setControl(self: Engine, userId: number, ctrl: ControlInput)
	self.controls[userId] = {
		throttle = math.clamp(ctrl.throttle, 0, 1),
		brake = math.clamp(ctrl.brake, 0, 1),
		steer = math.clamp(ctrl.steer, -1, 1),
	}
end

function Engine.syncR(self: Engine): number
	local n = 0
	for _ in self.players do
		n += 1
	end
	if n == 0 then
		return 0
	end
	local phases = table.create(n)
	local i = 0
	for _, st in self.players do
		i += 1
		phases[i] = st.phase
	end
	return PhaseSync.orderParameter(phases)
end

function Engine.step(self: Engine, dt: number)
	local cfg = self.cfg
	local R = self:syncR()
	local dragScale = PhaseSync.slipstreamDragFactor(R, cfg)

	for userId, st in self.players do
		local ctrl = self.controls[userId]
		st.throttle = ctrl.throttle
		st.brake = ctrl.brake
		st.steer = ctrl.steer

		MotionCore.updateVelocity(st, dt, dragScale, cfg)
		MotionCore.updateJerk(st, dt)

		local k0, k1 = Smoothness.anticipatoryKappa(self.track, st.s, st.vEff, cfg)
		local S = Smoothness.score(st, k0, k1, cfg)
		local inst = Smoothness.instability(st, cfg)

		local psi = Resonance.field(st, k0, k1, R, cfg)
		st.resonance = psi
		local noise = InputNoise.metric(st, cfg)
		Coherence.update(st, dt, S, inst, psi, noise, cfg)
		PhaseSync.updatePhase(st, dt, cfg)
		MotionCore.advanceArcLength(st, self.track.length, dt, cfg)
		st.position = self.track:position(st.s)
		Stability.apply(st, cfg)

		local flowState = Flow.update(self.flowMachines[userId], st.coherence, R, cfg)
		local audio = AudioField.compute(st, self.track, R, flowState)
		-- replicate key scalars for client VFX/audio
		-- (server sets on player instance if you pass Player object in)
	end

	self.time += dt
	return R
end

return Engine
