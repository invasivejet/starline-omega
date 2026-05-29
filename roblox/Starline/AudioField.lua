--!strict
--[[ A(t) = f(v, S, c, R, κ) — no arbitrary soundtrack switching ]]
local Config = require(script.Parent.Config)
local AudioField = {}

export type AudioField = {
	tempo: number,
	dissonance: number,
	harmony: number,
	percussion: number,
	richness: number,
	flowState: string,
}

function AudioField.compute(state: any, track: any, syncR: number, flowState: string?): AudioField
	local v = state.v
	local S = state.smoothness
	local c = state.coherence
	local R = syncR
	local kappa = track:curvature(state.s)

	local tempo = Config.BaseTempo + v * Config.TempoPerSpeed
	local dissonance = (1 - c) * Config.DissonanceFromCoherence + (1 - S) * 0.35
	local harmony = c * S * (0.35 + 0.65 * R) * Config.HarmonyFromSync
	local percussion = math.min(1, math.abs(kappa) * 0.05 + (1 - S) * 0.1)
	local richness = c * S

	local fs = flowState or "unstable"
	if fs == "flow" then
		harmony *= 1.15
		dissonance *= 0.85
	elseif fs == "unstable" then
		dissonance = math.min(1, dissonance * 1.25)
		harmony *= 0.7
	end

	return {
		tempo = tempo,
		dissonance = math.min(1, dissonance),
		harmony = math.min(1, harmony),
		percussion = percussion,
		richness = richness,
		flowState = fs,
	}
end

--[[
  Hook this into SoundService / your music system:
    workspace:SetAttribute("StarlineTempo", audio.tempo)
    etc.
]]
function AudioField.applyToAttributes(player: Player, audio: AudioField)
	player:SetAttribute("StarlineTempo", audio.tempo)
	player:SetAttribute("StarlineDissonance", audio.dissonance)
	player:SetAttribute("StarlineHarmony", audio.harmony)
	player:SetAttribute("StarlinePercussion", audio.percussion)
	player:SetAttribute("StarlineRichness", audio.richness)
	player:SetAttribute("StarlineFlowState", audio.flowState)
	player:SetAttribute("StarlineCoherence", player:GetAttribute("StarlineCoherence") or 0)
end

return AudioField
