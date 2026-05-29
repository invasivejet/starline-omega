--!strict
--[[ Delta-wire encoding for 20Hz downlink — slow fields as deltas vs last keyframe. ]]

local Config = require(script.Parent.Config)

local WireDelta = {}

-- Indices that change slowly and compress well (1-based wire layout)
WireDelta.DELTA_INDICES = { 4, 7, 10, 11, 13, 14, 16, 17, 18 }

function WireDelta.copyWire(wire: { number }): { number }
	local out = table.create(#wire)
	for i, v in wire do
		out[i] = v
	end
	return out
end

function WireDelta.applyDeltas(base: { number }, deltas: { [string]: number }): { number }
	local w = WireDelta.copyWire(base)
	for idx, delta in deltas do
		local i = tonumber(idx)
		if i then
			w[i] = (w[i] or 0) + delta
		end
	end
	return w
end

function WireDelta.encode(
	prev: { number }?,
	curr: { number },
	seq: number,
	epsilon: number?
): { [string]: any }
	local eps = epsilon or Config.WireDeltaEpsilon or 0.001
	local interval = Config.WireKeyframeInterval or 20
	local keyframe = prev == nil or seq % interval == 0

	if keyframe then
		return {
			seq = seq,
			keyframe = true,
			wire = WireDelta.copyWire(curr),
		}
	end

	local deltas: { [string]: number } = {}
	local anyChange = false
	for _, i in WireDelta.DELTA_INDICES do
		local d = (curr[i] or 0) - (prev[i] or 0)
		if math.abs(d) > eps then
			deltas[tostring(i)] = d
			anyChange = true
		end
	end

	if not anyChange then
		return {
			seq = seq,
			keyframe = false,
			noop = true,
		}
	end

	return {
		seq = seq,
		keyframe = false,
		deltas = deltas,
	}
end

function WireDelta.decode(payload: { [string]: any }, lastWire: { number }?): { number }?
	if typeof(payload) ~= "table" then
		return nil
	end
	if payload.keyframe == true and typeof(payload.wire) == "table" then
		return WireDelta.copyWire(payload.wire)
	end
	if payload.noop == true and lastWire then
		return WireDelta.copyWire(lastWire)
	end
	if typeof(payload.deltas) == "table" and lastWire then
		return WireDelta.applyDeltas(lastWire, payload.deltas)
	end
	if typeof(payload.wire) == "table" then
		return WireDelta.copyWire(payload.wire)
	end
	return nil
end

return WireDelta
