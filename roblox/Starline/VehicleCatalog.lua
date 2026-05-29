--!strict
--[[
  Garage catalog — fictional vehicles inspired by real marques (no trademarks).
  Stats = engine coefficient presets only (INVARIANTS-safe).
]]

local MotionConfig = require(script.Parent.MotionConfig)

export type VehicleCategory =
	"starter"
	| "europe_car"
	| "japan_moto"
	| "japan_ebike"
	| "europe_ebike"
	| "america_ebike"

export type VehicleDef = {
	id: string,
	displayName: string,
	tagline: string,
	category: VehicleCategory,
	inspiredBy: string,
	cost: number,
	coef: MotionConfig.MotionCoef,
}

local VehicleCatalog = {}

-- Coefficients tune feel: MaxSpeed envelope, SteeringGain agility, ThrottleAccel punch, etc.
VehicleCatalog.VEHICLES = {
	{
		id = "urban_pulse",
		displayName = "Urban Pulse",
		tagline = "City starter · balanced coil",
		category = "starter",
		inspiredBy = "Entry urban mobility",
		cost = 0,
		coef = {},
	},
	-- European cars (BMW / Alpine touring character)
	{
		id = "rhein_gt",
		displayName = "Rhein GT",
		tagline = "Autobahn cruiser · stable high-c",
		category = "europe_car",
		inspiredBy = "German grand-tourer (BMW-class)",
		cost = 85,
		coef = {
			MaxSpeed = 118,
			MaxSpeedHard = 195,
			Drag = 0.12,
			ThrottleAccel = 74,
			BrakeDecel = 125,
			SteeringGain = 0.065,
			CurveWeight = 1.85,
			Gamma = 0.38,
			Alpha = 1.9,
		},
	},
	{
		id = "bavaria_touring",
		displayName = "Bavaria Touring",
		tagline = "Long-phase GT · forgiving anticipation",
		category = "europe_car",
		inspiredBy = "Bavarian touring sedan",
		cost = 120,
		coef = {
			MaxSpeed = 112,
			Drag = 0.13,
			ThrottleAccel = 70,
			SteeringGain = 0.07,
			AnticipationDs = 9.5,
			AnticipationBlend = 0.5,
			NoisePenalty = 1.95,
			Gamma = 0.36,
		},
	},
	{
		id = "alpine_line",
		displayName = "Alpine Line",
		tagline = "Alpine grip · rewards clean arcs",
		category = "europe_car",
		inspiredBy = "European sports sedan",
		cost = 155,
		coef = {
			MaxSpeed = 115,
			ThrottleAccel = 78,
			SteeringGain = 0.075,
			CurveWeight = 2.15,
			ResonanceGeomWeight = 0.58,
			Beta = 1.75,
		},
	},
	-- Japanese motorcycles (Yamaha / Kawasaki sport character)
	{
		id = "sakura_r1",
		displayName = "Sakura R1",
		tagline = "Supersport lean · high κ response",
		category = "japan_moto",
		inspiredBy = "Japanese inline-four sport (Yamaha-class)",
		cost = 75,
		coef = {
			MaxSpeed = 108,
			MaxSpeedHard = 188,
			ThrottleAccel = 90,
			BrakeDecel = 135,
			SteeringGain = 0.105,
			CurveWeight = 2.45,
			SteerInstabilityWeight = 0.72,
			Gamma = 0.32,
		},
	},
	{
		id = "kiso_ninety",
		displayName = "Kiso Ninety",
		tagline = "Naked aggression · peak Ψ on rhythm",
		category = "japan_moto",
		inspiredBy = "Japanese street sport (Kawasaki-class)",
		cost = 98,
		coef = {
			MaxSpeed = 112,
			ThrottleAccel = 94,
			SteeringGain = 0.11,
			CurveWeight = 2.5,
			ResonanceKappaScale = 13.5,
			Alpha = 1.95,
			Beta = 1.92,
		},
	},
	{
		id = "kanjo_drift",
		displayName = "Kanjo Drift",
		tagline = "Night kanjo · high risk / high flow",
		category = "japan_moto",
		inspiredBy = "Japanese canyon bike culture",
		cost = 115,
		coef = {
			MaxSpeed = 102,
			SteeringGain = 0.115,
			CurveWeight = 2.6,
			SteerInstabilityWeight = 0.78,
			ResonanceGeomWeight = 0.6,
			FlowEnterFlowC = 0.9,
		},
	},
	-- Japanese e-bikes
	{
		id = "kyoto_flux",
		displayName = "Kyoto Flux",
		tagline = "Kei-smooth assist · snappy low-v",
		category = "japan_ebike",
		inspiredBy = "Japanese commuter e-bike",
		cost = 32,
		coef = {
			MaxSpeed = 74,
			MaxSpeedHard = 95,
			ThrottleAccel = 88,
			BrakeDecel = 100,
			SteeringGain = 0.092,
			AnticipationBlend = 0.48,
			Gamma = 0.3,
		},
	},
	{
		id = "edo_line",
		displayName = "Edo Line",
		tagline = "River-path cadence · low noise",
		category = "japan_ebike",
		inspiredBy = "Tokyo river-path e-bike",
		cost = 58,
		coef = {
			MaxSpeed = 70,
			Drag = 0.17,
			ThrottleAccel = 82,
			NoisePenalty = 1.85,
			AnticipationDs = 9.0,
			Alpha = 1.88,
		},
	},
	-- European e-bikes
	{
		id = "amsterdam_cruise",
		displayName = "Amsterdam Cruise",
		tagline = "Dutch upright · stable coherence",
		category = "europe_ebike",
		inspiredBy = "Benelux city e-bike",
		cost = 38,
		coef = {
			MaxSpeed = 68,
			Drag = 0.18,
			SteeringGain = 0.088,
			ThrottleAccel = 78,
			NoisePenalty = 1.9,
			Gamma = 0.29,
		},
	},
	{
		id = "alp_volt",
		displayName = "Alp Volt",
		tagline = "Alpine assist · curve-phrasing",
		category = "europe_ebike",
		inspiredBy = "European trekking e-bike",
		cost = 62,
		coef = {
			MaxSpeed = 72,
			ThrottleAccel = 80,
			CurveWeight = 2.1,
			AnticipationDs = 8.5,
			AnticipationSpeedScale = 0.17,
			ResonanceGeomWeight = 0.57,
		},
	},
	-- American e-bikes
	{
		id = "brooklyn_volt",
		displayName = "Brooklyn Volt",
		tagline = "Borough snap · punchy throttle",
		category = "america_ebike",
		inspiredBy = "US city e-bike (Brooklyn-class)",
		cost = 28,
		coef = {
			MaxSpeed = 76,
			ThrottleAccel = 96,
			BrakeDecel = 105,
			SteeringGain = 0.095,
			Gamma = 0.31,
		},
	},
	{
		id = "sierra_glide",
		displayName = "Sierra Glide",
		tagline = "West-coast glide · comfort S",
		category = "america_ebike",
		inspiredBy = "American cruiser e-bike",
		cost = 48,
		coef = {
			MaxSpeed = 80,
			Drag = 0.16,
			ThrottleAccel = 84,
			NoisePenalty = 1.88,
			JerkWeight = 0.92,
			AnticipationBlend = 0.42,
		},
	},
} :: { VehicleDef }

function VehicleCatalog.getDef(vehicleId: string): VehicleDef?
	for _, def in VehicleCatalog.VEHICLES do
		if def.id == vehicleId then
			return def
		end
	end
	return nil
end

function VehicleCatalog.categoryLabel(cat: VehicleCategory): string
	if cat == "europe_car" then
		return "European cars"
	elseif cat == "japan_moto" then
		return "Japanese motorcycles"
	elseif cat == "japan_ebike" then
		return "Japanese e-bikes"
	elseif cat == "europe_ebike" then
		return "European e-bikes"
	elseif cat == "america_ebike" then
		return "American e-bikes"
	end
	return "Starter"
end

return VehicleCatalog
