--!strict
--[[
  Minimal state-driven music hook.
  Wire a Sound instance named "StarlineMusic" under SoundService, or create one.
]]

local SoundService = game:GetService("SoundService")

local MusicController = {}
MusicController.__index = MusicController

export type MusicController = typeof(setmetatable({} :: {
	_sound: Sound?,
}, MusicController))

function MusicController.new(): MusicController
	local self = setmetatable({}, MusicController)
	local existing = SoundService:FindFirstChild("StarlineMusic")
	if existing and existing:IsA("Sound") then
		self._sound = existing
	else
		local s = Instance.new("Sound")
		s.Name = "StarlineMusic"
		s.Looped = true
		s.SoundId = "" -- assign rbxassetid in Studio
		s.Volume = 0.4
		s.Parent = SoundService
		self._sound = s
	end
	return self
end

function MusicController.updateFromSnap(self: MusicController, snap: any)
	local s = self._sound
	if not s then
		return
	end
	local tempo = snap.tempo or 90
	local harmony = snap.harmony or 0
	local dissonance = snap.dissonance or 1
	local coherence = snap.coherence or 0
	s.PlaybackSpeed = math.clamp(tempo / 90, 0.5, 2.0)
	s.Volume = math.clamp(0.15 + 0.35 * coherence + 0.2 * harmony - 0.15 * dissonance, 0, 1)
	if s.SoundId ~= "" and not s.IsPlaying then
		s:Play()
	end
end

function MusicController.updateFromPlayer(self: MusicController, player: Player)
	local s = self._sound
	if not s then
		return
	end
	local tempo = (player:GetAttribute("StarlineTempo") or 90) :: number
	local harmony = (player:GetAttribute("StarlineHarmony") or 0) :: number
	local dissonance = (player:GetAttribute("StarlineDissonance") or 1) :: number
	local coherence = (player:GetAttribute("StarlineCoherence") or 0) :: number

	-- map state → playback feel (placeholder until real stems)
	s.PlaybackSpeed = math.clamp(tempo / 90, 0.5, 2.0)
	s.Volume = math.clamp(0.15 + 0.35 * coherence + 0.2 * harmony - 0.15 * dissonance, 0, 1)
	if s.SoundId ~= "" and not s.IsPlaying then
		s:Play()
	end
end

return MusicController
