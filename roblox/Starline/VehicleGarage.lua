--!strict
--[[ Garage — buy & equip vehicles with ℛ (same pattern as TrackUnlock). ]]

local EconomyField = require(script.Parent.EconomyField)
local VehicleCatalog = require(script.Parent.VehicleCatalog)

local VehicleGarage = {}

function VehicleGarage.parseUnlocks(player: Player): { string }
	local s = (player:GetAttribute("StarlineVehicleUnlocks") or "urban_pulse") :: string
	local out: { string } = {}
	for part in string.gmatch(s, "[^,]+") do
		table.insert(out, part)
	end
	return out
end

function VehicleGarage.hasUnlock(player: Player, vehicleId: string): boolean
	for _, id in VehicleGarage.parseUnlocks(player) do
		if id == vehicleId then
			return true
		end
	end
	return false
end

function VehicleGarage.grantUnlock(player: Player, vehicleId: string)
	if VehicleGarage.hasUnlock(player, vehicleId) then
		return
	end
	local list = VehicleGarage.parseUnlocks(player)
	table.insert(list, vehicleId)
	player:SetAttribute("StarlineVehicleUnlocks", table.concat(list, ","))
end

function VehicleGarage.tryUnlock(player: Player, vehicleId: string): (boolean, string)
	local def = VehicleCatalog.getDef(vehicleId)
	if not def then
		return false, "unknown_vehicle"
	end
	if VehicleGarage.hasUnlock(player, vehicleId) then
		return true, "already_owned"
	end
	if def.cost <= 0 then
		VehicleGarage.grantUnlock(player, vehicleId)
		return true, "free"
	end
	if not EconomyField.spend(player, def.cost) then
		return false, "insufficient_resonance"
	end
	VehicleGarage.grantUnlock(player, vehicleId)
	return true, "purchased_" .. vehicleId
end

function VehicleGarage.setActiveVehicle(player: Player, vehicleId: string): (boolean, string)
	if not VehicleGarage.hasUnlock(player, vehicleId) then
		return false, "locked"
	end
	if not VehicleCatalog.getDef(vehicleId) then
		return false, "unknown_vehicle"
	end
	player:SetAttribute("StarlineActiveVehicle", vehicleId)
	local def = VehicleCatalog.getDef(vehicleId)
	if def then
		player:SetAttribute("StarlineVehicleName", def.displayName)
	end
	return true, "ok"
end

function VehicleGarage.listForPlayer(player: Player): {
	{
		id: string,
		name: string,
		tagline: string,
		category: string,
		inspiredBy: string,
		cost: number,
		owned: boolean,
		equipped: boolean,
		stats: { [string]: number },
	}
}
	local active = (player:GetAttribute("StarlineActiveVehicle") or "urban_pulse") :: string
	local out = {}
	for _, def in VehicleCatalog.VEHICLES do
		local stats: { [string]: number } = {}
		for key, val in def.coef do
			stats[key] = val
		end
		table.insert(out, {
			id = def.id,
			name = def.displayName,
			tagline = def.tagline,
			category = VehicleCatalog.categoryLabel(def.category),
			inspiredBy = def.inspiredBy,
			cost = def.cost,
			owned = VehicleGarage.hasUnlock(player, def.id),
			equipped = def.id == active,
			stats = stats,
		})
	end
	return out
end

return VehicleGarage
