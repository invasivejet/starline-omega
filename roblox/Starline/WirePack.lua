--!strict
--[[ 8-byte perceptual pack — mirror python/starline/wire_pack.py ]]

local WirePack = {}

WirePack.PACKED_SIZE = 8
WirePack.V_MAX = 200

local function clamp(x: number, lo: number, hi: number): number
	return math.max(lo, math.min(hi, x))
end

local function q10(x: number): number
	return math.floor(clamp(x, 0, 1) * 1023 + 0.5)
end

local function q12unit(x: number, scale: number): number
	return math.floor(clamp(x / scale, 0, 1) * 4095 + 0.5)
end

function WirePack.encodeFromWire(wire: { number }): buffer
	local v = wire[7] or 0
	local S = wire[4] or 0
	local c = wire[11] or 0
	local phi = wire[14] or 0
	local R = wire[16] or 0
	local flow = wire[18] or 0
	local topo = wire[6] or 15
	if topo >= 255 then
		topo = 15
	end

	local ci = q10(c)
	local si = q10(S)
	local vi = q12unit(v, WirePack.V_MAX)
	local phii = q12unit(phi % (math.pi * 2), math.pi * 2)
	local ri = q10(R)
	local fi = math.floor(flow) % 4
	local ti = math.floor(topo) % 16

	local val = ci + si * 2 ^ 10 + vi * 2 ^ 20 + phii * 2 ^ 32 + ri * 2 ^ 44 + fi * 2 ^ 54 + ti * 2 ^ 56

	local buf = buffer.create(WirePack.PACKED_SIZE)
	buffer.writeu32(buf, 0, val % 2 ^ 32)
	buffer.writeu32(buf, 4, math.floor(val / 2 ^ 32))
	return buf
end

function WirePack.decodeToWire(packed: buffer, template: { number }?): { number }
	local w = template or table.create(20, 0)
	for i = 1, 20 do
		if w[i] == nil then
			w[i] = 0
		end
	end
	local lo = buffer.readu32(packed, 0)
	local hi = buffer.readu32(packed, 4)
	local val = lo + hi * 2 ^ 32
	local ci = val % 2 ^ 10
	local si = math.floor(val / 2 ^ 10) % 2 ^ 10
	local vi = math.floor(val / 2 ^ 20) % 2 ^ 12
	local phii = math.floor(val / 2 ^ 32) % 2 ^ 12
	local ri = math.floor(val / 2 ^ 44) % 2 ^ 10
	local fi = math.floor(val / 2 ^ 54) % 4
	local ti = math.floor(val / 2 ^ 56) % 16

	w[4] = si / 1023
	w[6] = ti
	w[7] = vi / 4095 * WirePack.V_MAX
	w[11] = ci / 1023
	w[14] = phii / 4095 * (math.pi * 2)
	w[16] = ri / 1023
	w[18] = fi
	return w
end

return WirePack
