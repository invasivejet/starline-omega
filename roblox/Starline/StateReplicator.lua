--!strict
local Packets = require(script.Parent.Packets)
local AudioField = require(script.Parent.AudioField)
local Flow = require(script.Parent.Flow)
local WireDelta = require(script.Parent.WireDelta)
local WirePack = require(script.Parent.WirePack)
local HexLattice = require(script.Parent.HexLattice)
local Config = require(script.Parent.Config)

local StateReplicator = {}

local FLOW_CODES = { unstable = 0, stable = 1, resonant = 2, flow = 3 }

local function flowCode(state: string): number
	return FLOW_CODES[state] or 0
end

function StateReplicator.buildWire(st: any, track: any, syncR: number, flowState: string): { number }
	local L = track.length
	local sNorm = if L > 0 then (st.s % L) / L else 0
	local k0 = track:curvature(st.s)
	local ds = 8 + 0.15 * math.max(st.vEff or 0, 0)
	local k1 = track:curvature(st.s + ds)
	return {
		sNorm,
		k0,
		k1,
		st.smoothness or 0,
		st.curveError or 0,
		255,
		st.v or 0,
		st.a or 0,
		st.jerk or 0,
		st.vEff or 0,
		st.coherence or 0,
		st.instability or 0,
		st.resonance or 0,
		st.phase or 0,
		0,
		syncR,
		0,
		flowCode(flowState),
		0,
		1,
	}
end

export type ReplicatePayload = {
	seq: number?,
	keyframe: boolean?,
	noop: boolean?,
	deltas: { [string]: number }?,
	packed: buffer?,
	hexLattice: { [string]: number }?,
	wire: { number },
	resonance: number,
	flowState: string,
	audio: { tempo: number, dissonance: number, harmony: number, richness: number, percussion: number },
	position: Vector3,
	look: Vector3,
}

function StateReplicator.buildPayload(
	st: any,
	track: any,
	syncR: number,
	flowState: string,
	resonance: number,
	prevWire: { number }?,
	seq: number?
): ReplicatePayload
	local wire = StateReplicator.buildWire(st, track, syncR, flowState)
	local audio = AudioField.compute(st, track, syncR, flowState)
	local pos = st.position or Vector3.zero
	local tangent = track:tangent(st.s)
	local audioBlock = {
		tempo = audio.tempo,
		dissonance = audio.dissonance,
		harmony = audio.harmony,
		richness = audio.richness,
		percussion = audio.percussion,
	}
	local base: ReplicatePayload = {
		wire = wire,
		resonance = resonance,
		flowState = flowState,
		audio = audioBlock,
		position = pos,
		look = pos + tangent,
	}

	if seq == nil then
		return base
	end

	local encoded = WireDelta.encode(prevWire, wire, seq)
	base.seq = encoded.seq
	base.keyframe = encoded.keyframe
	base.noop = encoded.noop
	base.deltas = encoded.deltas
	if encoded.keyframe == true and typeof(encoded.wire) == "table" then
		base.wire = encoded.wire
	end
	if Config.UseWirePack then
		base.packed = WirePack.encodeFromWire(base.wire)
	end
	base.hexLattice = HexLattice.fromWire(base.wire, resonance)
	return base
end

function StateReplicator.wireChanged(prev: { number }?, wire: { number }, epsilon: number): boolean
	if not prev then
		return true
	end
	for i = 1, Packets.WIRE_SIZE do
		if math.abs((prev[i] or 0) - (wire[i] or 0)) > epsilon then
			return true
		end
	end
	return false
end

return StateReplicator
