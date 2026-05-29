--!strict
--[[ Per-vehicle motion coefficients — merges catalog overrides onto global Config. ]]

local Config = require(script.Parent.Config)
local VehicleCatalog = require(script.Parent.VehicleCatalog)

local MotionConfig = {}

export type MotionCoef = { [string]: number }

function MotionConfig.merge(overrides: MotionCoef?): typeof(Config)
	if not overrides or next(overrides) == nil then
		return Config
	end
	local merged: { [string]: any } = {}
	for key, value in Config :: any do
		merged[key] = value
	end
	for key, value in overrides do
		merged[key] = value
	end
	return merged
end

function MotionConfig.forVehicle(vehicleId: string): typeof(Config)
	local def = VehicleCatalog.getDef(vehicleId)
	if not def then
		return Config
	end
	return MotionConfig.merge(def.coef)
end

return MotionConfig
