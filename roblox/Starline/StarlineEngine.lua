--!strict
--[[
  STARLINE Ω — single require() entry for the game engine (Roblox).

  local StarlineEngine = require(ReplicatedStorage.Starline.StarlineEngine)
  local eng = StarlineEngine.createEngine(track)
]]

local Config = require(script.Parent.Config)
local Engine = require(script.Parent.Engine)
local TrackBuilder = require(script.Parent.TrackBuilder)
local TrackUnlock = require(script.Parent.TrackUnlock)
local Flow = require(script.Parent.Flow)
local Packets = require(script.Parent.Packets)

export type EngineHandle = {
	engine: any,
	track: any,
	trackId: string,
}

local StarlineEngine = {}

StarlineEngine.VERSION = "0.1.0"
StarlineEngine.WIRE_SIZE = Packets.WIRE_SIZE
StarlineEngine.FROZEN_LOOP = "Motion→Smoothness→Coherence→Phase→Perception"

function StarlineEngine.createEngine(trackId: string): EngineHandle
	local track = TrackBuilder.fromWorkspace(trackId)
	local eng = Engine.new(track)
	return {
		engine = eng,
		track = track,
		trackId = trackId,
	}
end

function StarlineEngine.config()
	return Config
end

function StarlineEngine.tracks()
	return TrackUnlock.TRACKS
end

return StarlineEngine
