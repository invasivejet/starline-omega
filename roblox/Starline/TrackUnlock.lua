--!strict
--[[
  Track registry + geometric unlock (spend ℛ).
  Workspace folders:
    - StarlineWaypoints        → track id "oval" (or custom waypoints)
    - StarlineWaypointsCircuit → track id "circuit" (unlock required)
]]

local EconomyField = require(script.Parent.EconomyField)

export type TrackDef = {
	id: string,
	displayName: string,
	waypointFolder: string?,
	fallbackOvalRadius: number?,
	cost: number,
}

local TrackUnlock = {}

TrackUnlock.TRACKS = {
	{
		id = "oval",
		displayName = "Oval",
		waypointFolder = "StarlineWaypoints",
		fallbackOvalRadius = 200,
		cost = 0,
	},
	{
		id = "circuit",
		displayName = "Circuit",
		waypointFolder = "StarlineWaypointsCircuit",
		fallbackOvalRadius = 120,
		cost = 40,
	},
} :: { TrackDef }

function TrackUnlock.getDef(trackId: string): TrackDef?
	for _, def in TrackUnlock.TRACKS do
		if def.id == trackId then
			return def
		end
	end
	return nil
end

function TrackUnlock.parseUnlocks(player: Player): { string }
	local s = (player:GetAttribute("StarlineUnlocks") or "oval") :: string
	local out: { string } = {}
	for part in string.gmatch(s, "[^,]+") do
		table.insert(out, part)
	end
	return out
end

function TrackUnlock.hasUnlock(player: Player, trackId: string): boolean
	for _, id in TrackUnlock.parseUnlocks(player) do
		if id == trackId then
			return true
		end
	end
	return false
end

function TrackUnlock.grantUnlock(player: Player, trackId: string)
	if TrackUnlock.hasUnlock(player, trackId) then
		return
	end
	local list = TrackUnlock.parseUnlocks(player)
	table.insert(list, trackId)
	player:SetAttribute("StarlineUnlocks", table.concat(list, ","))
end

function TrackUnlock.tryUnlock(player: Player, trackId: string): (boolean, string)
	local def = TrackUnlock.getDef(trackId)
	if not def then
		return false, "unknown_track"
	end
	if TrackUnlock.hasUnlock(player, trackId) then
		return true, "already_unlocked"
	end
	if def.cost <= 0 then
		TrackUnlock.grantUnlock(player, trackId)
		return true, "free"
	end
	if not EconomyField.spend(player, def.cost) then
		return false, "insufficient_resonance"
	end
	TrackUnlock.grantUnlock(player, trackId)
	return true, "purchased"
end

function TrackUnlock.setActiveTrack(player: Player, trackId: string): (boolean, string)
	if not TrackUnlock.hasUnlock(player, trackId) then
		return false, "locked"
	end
	player:SetAttribute("StarlineActiveTrack", trackId)
	return true, "ok"
end

function TrackUnlock.listForPlayer(player: Player): { { id: string, name: string, cost: number, unlocked: boolean } }
	local out = {}
	for _, def in TrackUnlock.TRACKS do
		table.insert(out, {
			id = def.id,
			name = def.displayName,
			cost = def.cost,
			unlocked = TrackUnlock.hasUnlock(player, def.id),
		})
	end
	return out
end

return TrackUnlock
