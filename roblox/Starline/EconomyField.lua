--!strict
--[[
  Economy = projection of simulation energy over time (server authoritative).
  dℛ = k · Ψ · S · c^γ · (1 + λ·R₊) · dt
  AFK: constrained motion → lower S, capped c_eff — not a parallel reward system.
]]

local Config = require(script.Parent.Config)
local AfkPilot = require(script.Parent.AfkPilot)

local EconomyField = {}

function EconomyField.energyIncrement(
	state: any,
	syncR: number,
	dt: number,
	afkSession: AfkPilot.AfkSession?
): number
	local c = state.coherence or 0
	local S = state.smoothness or 0
	local psi = state.resonance or 0
	local v = state.v or 0
	local cMin = if afkSession and afkSession.enabled then Config.AfkMinCoherence else Config.ResonanceCMin
	if c < cMin then
		return 0
	end
	if afkSession and afkSession.enabled and v < Config.AfkMinVelocity then
		return 0
	end

	local cEff = if afkSession and afkSession.enabled then math.min(c, Config.AfkCoherenceCap) else c
	cEff = math.clamp(cEff, 0, 1)
	local gamma = math.max(Config.ResonanceCoherenceGamma, 1.01)
	local rPlus = math.max(0, syncR)
	local syncTerm = 1 + Config.ResonanceSyncLambda * rPlus
	return Config.ResonanceEarnK * math.max(0, psi) * math.max(0, S) * (cEff ^ gamma) * syncTerm * dt
end

function EconomyField.newSession(player: Player)
	player:SetAttribute("StarlineResonance", 0)
	player:SetAttribute("StarlineResonancePeak", 0)
	player:SetAttribute("StarlineCoherenceIntegral", 0)
end

function EconomyField.integrate(
	player: Player,
	dt: number,
	state: any,
	syncR: number,
	_topologyCode: number?,
	_config: any?,
	afkSession: AfkPilot.AfkSession?
): number
	local dR = EconomyField.energyIncrement(state, syncR, dt, afkSession)
	local c = state.coherence or 0
	local integ = (player:GetAttribute("StarlineCoherenceIntegral") or 0) + math.max(0, c) * dt
	player:SetAttribute("StarlineCoherenceIntegral", integ)

	if afkSession and afkSession.enabled then
		local cap = AfkPilot.capRemaining(afkSession)
		if cap <= 0 then
			dR = 0
		else
			dR = math.min(dR, cap)
			afkSession.earnedSession += dR
		end
	end

	local R = (player:GetAttribute("StarlineResonance") or 0) + dR
	player:SetAttribute("StarlineResonance", R)
	local peak = player:GetAttribute("StarlineResonancePeak") or 0
	if R > peak then
		player:SetAttribute("StarlineResonancePeak", R)
	end
	if afkSession and afkSession.enabled then
		player:SetAttribute("StarlineAfkEarned", afkSession.earnedSession)
	end
	return R
end

function EconomyField.canAfford(player: Player, cost: number): boolean
	return (player:GetAttribute("StarlineResonance") or 0) >= cost
end

function EconomyField.spend(player: Player, cost: number): boolean
	local R = player:GetAttribute("StarlineResonance") or 0
	if R < cost then
		return false
	end
	player:SetAttribute("StarlineResonance", R - cost)
	return true
end

return EconomyField
