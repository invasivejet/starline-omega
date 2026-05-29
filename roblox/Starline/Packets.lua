--!strict
--[[
  Wire layout mirror of python/starline/packets.py (WIRE_SIZE = 20).
  Index map: docs/ENCODING.md
]]

export type EnginePacket = {
	geometric: { sNorm: number, kappa: number, kappaAhead: number, S: number, curveError: number, topologyCode: number },
	physical: { v: number, a: number, jerk: number, vEff: number },
	chemical: { c: number, instability: number, resonance: number, phi: number, noise: number },
	harmonic: { R: number },
	flow: { value: number, stateCode: number },
}

local Packets = {}

Packets.WIRE_SIZE = 20

function Packets.toWire(pkt: EnginePacket): { number }
	local g = pkt.geometric
	local p = pkt.physical
	local c = pkt.chemical
	local h = pkt.harmonic
	local f = pkt.flow
	return {
		g.sNorm, g.kappa, g.kappaAhead, g.S, g.curveError, g.topologyCode,
		p.v, p.a, p.jerk, p.vEff,
		c.c, c.instability, c.resonance, c.phi, c.noise,
		h.R, f.value, f.stateCode,
		0, 1,
	}
end

function Packets.fromWire(wire: { number }): EnginePacket
	return {
		geometric = {
			sNorm = wire[1] or 0, kappa = wire[2] or 0, kappaAhead = wire[3] or 0,
			S = wire[4] or 0, curveError = wire[5] or 0, topologyCode = wire[6] or 255,
		},
		physical = { v = wire[7] or 0, a = wire[8] or 0, jerk = wire[9] or 0, vEff = wire[10] or 0 },
		chemical = {
			c = wire[11] or 0, instability = wire[12] or 0, resonance = wire[13] or 0,
			phi = wire[14] or 0, noise = wire[15] or 0,
		},
		harmonic = { R = wire[16] or 0 },
		flow = { value = wire[17] or 0, stateCode = wire[18] or 0 },
	}
end

function Packets.applyWireToAttributes(player: Player, wire: { number })
	for i, val in wire do
		player:SetAttribute("StarlineWire" .. tostring(i - 1), val)
	end
end

return Packets
