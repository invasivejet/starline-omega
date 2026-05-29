--!strict
--[[ SCHRÖDINGERIZED LATTICE — hex opcode map (mirror python/starline/hex_lattice.py) ]]

local HexLattice = {}

HexLattice.OP_V = 0x76
HexLattice.OP_S = 0x53
HexLattice.OP_C = 0x63
HexLattice.OP_PHI = 0xCF
HexLattice.OP_R = 0x52
HexLattice.OP_PSI = 0xA8
HexLattice.OP_KAPPA = 0xD0
HexLattice.OP_RESONANCE = 0x211B

HexLattice.MODE_NOISE = 0x00
HexLattice.MODE_RHYTHM = 0x01
HexLattice.MODE_ANTICIPATION = 0x02
HexLattice.MODE_SYNC = 0x03
HexLattice.MODE_EMERGENCE = 0x04
HexLattice.MODE_FLOW = 0x05

local FLOW_TO_MODE = {
	unstable = HexLattice.MODE_NOISE,
	stable = HexLattice.MODE_RHYTHM,
	resonant = HexLattice.MODE_ANTICIPATION,
	flow = HexLattice.MODE_FLOW,
}

function HexLattice.encodeHex(state: { [string]: number }): { [string]: number }
	local out = {}
	local map = {
		v = "0x76",
		S = "0x53",
		c = "0x63",
		phi = "0xCF",
		R = "0x52",
		psi = "0xA8",
		kappa = "0xD0",
		resonance = "0x211B",
	}
	for field, key in map do
		if state[field] ~= nil then
			out[key] = state[field]
		end
	end
	return out
end

function HexLattice.fromWire(wire: { number }, resonanceCredit: number?): { [string]: number }
	local w = wire
	return HexLattice.encodeHex({
		v = w[7] or 0,
		S = w[4] or 0,
		c = w[11] or 0,
		phi = w[14] or 0,
		R = w[16] or 0,
		psi = w[13] or 0,
		kappa = w[2] or 0,
		resonance = resonanceCredit or 0,
	})
end

function HexLattice.flowToMode(flowState: string): number
	return FLOW_TO_MODE[flowState] or HexLattice.MODE_NOISE
end

function HexLattice.schrodingerState(flowState: string, coherence: number, instability: number): { alpha: number, beta: number, gamma: number, delta: number }
	local c = math.clamp(coherence, 0, 1)
	local inst = math.clamp(instability, 0, 1)
	local fracture = inst * (1 - c)
	local a, b, g, d = 0.2, 0.1, 0.05, 0.65 + fracture * 0.2
	if flowState == "flow" then
		a, b, g, d = 0.1, 0.15, 0.7, fracture
	elseif flowState == "resonant" then
		a, b, g, d = 0.15, 0.65, 0.1, fracture
	elseif flowState == "stable" then
		a, b, g, d = 0.7, 0.15, 0.05, fracture
	end
	local n = math.sqrt(a * a + b * b + g * g + d * d)
	if n < 1e-9 then
		return { alpha = 1, beta = 0, gamma = 0, delta = 0 }
	end
	return { alpha = a / n, beta = b / n, gamma = g / n, delta = d / n }
end

return HexLattice
