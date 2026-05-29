--!strict
--[[
  Presentation cache with temporal interpolation between State packets.
  Server sim is authoritative; this only smooths HUD / audio / trail / camera.
]]

local Config = require(script.Parent.Config)
local WireDelta = require(script.Parent.WireDelta)
local WirePack = require(script.Parent.WirePack)

export type Snapshot = {
	coherence: number,
	smoothness: number,
	syncR: number,
	resonance: number,
	resonanceField: number,
	flowState: string,
	flowValue: number,
	v: number,
	vEff: number,
	tempo: number,
	dissonance: number,
	harmony: number,
	richness: number,
	position: Vector3,
	look: Vector3,
}

local ClientState = {}

local function blank(): Snapshot
	return {
		coherence = 0,
		smoothness = 0,
		syncR = 0,
		resonance = 0,
		resonanceField = 0,
		flowState = "unstable",
		flowValue = 0,
		v = 0,
		vEff = 0,
		tempo = 90,
		dissonance = 1,
		harmony = 0,
		richness = 0,
		position = Vector3.zero,
		look = Vector3.zero,
	}
end

local function lerp(a: number, b: number, t: number): number
	return a + (b - a) * t
end

local function lerpVec(a: Vector3, b: Vector3, t: number): Vector3
	return a:Lerp(b, t)
end

local function copy(s: Snapshot): Snapshot
	return {
		coherence = s.coherence,
		smoothness = s.smoothness,
		syncR = s.syncR,
		resonance = s.resonance,
		resonanceField = s.resonanceField,
		flowState = s.flowState,
		flowValue = s.flowValue,
		v = s.v,
		vEff = s.vEff,
		tempo = s.tempo,
		dissonance = s.dissonance,
		harmony = s.harmony,
		richness = s.richness,
		position = s.position,
		look = s.look,
	}
end

local function lerpSnap(a: Snapshot, b: Snapshot, t: number): Snapshot
	return {
		coherence = lerp(a.coherence, b.coherence, t),
		smoothness = lerp(a.smoothness, b.smoothness, t),
		syncR = lerp(a.syncR, b.syncR, t),
		resonance = lerp(a.resonance, b.resonance, t),
		resonanceField = lerp(a.resonanceField, b.resonanceField, t),
		flowState = if t >= 0.5 then b.flowState else a.flowState,
		flowValue = lerp(a.flowValue, b.flowValue, t),
		v = lerp(a.v, b.v, t),
		vEff = lerp(a.vEff, b.vEff, t),
		tempo = lerp(a.tempo, b.tempo, t),
		dissonance = lerp(a.dissonance, b.dissonance, t),
		harmony = lerp(a.harmony, b.harmony, t),
		richness = lerp(a.richness, b.richness, t),
		position = lerpVec(a.position, b.position, t),
		look = lerpVec(a.look, b.look, t),
	}
end

local _lastWire: { number }? = nil

local function applyPayloadTo(target: Snapshot, payload: any)
	if typeof(payload) ~= "table" then
		return
	end
	local wire: { number }? = nil
	if typeof(payload.packed) == "buffer" then
		wire = WirePack.decodeToWire(payload.packed, _lastWire)
	elseif typeof(payload.wire) == "table" then
		wire = WireDelta.decode(payload, _lastWire) or payload.wire
	else
		wire = WireDelta.decode(payload, _lastWire)
	end
	if wire then
		_lastWire = WireDelta.copyWire(wire)
	end
	if typeof(wire) == "table" then
		target.coherence = wire[11] or target.coherence
		target.smoothness = wire[4] or target.smoothness
		target.syncR = wire[16] or target.syncR
		target.resonanceField = wire[13] or target.resonanceField
		target.flowValue = wire[17] or target.flowValue
		target.v = wire[7] or target.v
		target.vEff = wire[10] or target.vEff
	end
	target.resonance = payload.resonance or target.resonance
	target.flowState = payload.flowState or target.flowState
	local audio = payload.audio
	if typeof(audio) == "table" then
		target.tempo = audio.tempo or target.tempo
		target.dissonance = audio.dissonance or target.dissonance
		target.harmony = audio.harmony or target.harmony
		target.richness = audio.richness or target.richness
	end
	if typeof(payload.position) == "Vector3" then
		target.position = payload.position
	end
	if typeof(payload.look) == "Vector3" then
		target.look = payload.look
	end
end

local _prev: Snapshot = blank()
local _curr: Snapshot = blank()
local _hasPair = false
local _recvAt = 0.0

function ClientState.pushPayload(payload: any)
	if _hasPair then
		_prev = copy(_curr)
	end
	applyPayloadTo(_curr, payload)
	if not _hasPair then
		_prev = copy(_curr)
		_hasPair = true
	end
	_recvAt = os.clock()
end

function ClientState.sampleInterpolated(): Snapshot
	if not _hasPair then
		return copy(_curr)
	end
	local duration = (1 / Config.ReplicateHz) * Config.InterpBufferScale
	local alpha = math.clamp((os.clock() - _recvAt) / duration, 0, 1)
	return lerpSnap(_prev, _curr, alpha)
end

function ClientState.get(): Snapshot
	return ClientState.sampleInterpolated()
end

function ClientState.syncAttributes(player: Player)
	local s = ClientState.sampleInterpolated()
	player:SetAttribute("StarlineCoherence", s.coherence)
	player:SetAttribute("StarlineSyncR", s.syncR)
	player:SetAttribute("StarlineResonance", s.resonance)
	player:SetAttribute("StarlineFlowState", s.flowState)
	player:SetAttribute("StarlineTempo", s.tempo)
	player:SetAttribute("StarlineHarmony", s.harmony)
	player:SetAttribute("StarlineDissonance", s.dissonance)
	player:SetAttribute("StarlineRichness", s.richness)
end

return ClientState
