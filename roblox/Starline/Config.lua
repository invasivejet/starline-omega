--!strict
--[[
  STARLINE Ω — tunable coefficients (mirror of python/starline/config.py)
]]

local Config = {}

Config.Drag = 0.15
Config.MaxSpeed = 120
Config.MaxSpeedHard = 200
Config.ThrottleAccel = 80
Config.BrakeDecel = 120

Config.JerkWeight = 1.0
Config.CurveWeight = 2.0
Config.SteeringGain = 0.08

Config.Beta = 1.8

Config.FlowEnterStableC = 0.45
Config.FlowExitStableC = 0.38
Config.FlowEnterResonantC = 0.72
Config.FlowExitResonantC = 0.65
Config.FlowEnterFlowC = 0.92
Config.FlowExitFlowC = 0.85
Config.FlowEnterFlowR = 0.85
Config.FlowExitFlowR = 0.75

Config.NoisePenalty = 2.2
Config.NoiseSteerWeight = 1.0
Config.NoiseOscillationWeight = 1.5
Config.NoiseBrakeWeight = 0.8
Config.NoiseJerkWeight = 0.3
Config.JerkNoiseScale = 8.0

Config.ResonanceGeomWeight = 0.55
Config.ResonanceSyncWeight = 0.45
Config.ResonanceKappaScale = 12.0

Config.AnticipationDs = 8.0
Config.AnticipationSpeedScale = 0.15
Config.AnticipationBlend = 0.45

Config.SteerInstabilityWeight = 0.6
Config.BrakeInstabilityWeight = 0.4

Config.Gamma = 0.35

Config.Omega = 0.05
Config.SyncSlipstream = 0.25
Config.SyncResonance = 0.15

Config.BaseTempo = 90
Config.TempoPerSpeed = 0.4
Config.HarmonyFromSync = 1.0
Config.DissonanceFromCoherence = 1.0

-- --- simulation (deterministic) ---
Config.SimHz = 60
Config.FixedDt = 1 / Config.SimHz
Config.MaxSimStepsPerFrame = 4
Config.MaxSimCatchupSec = 0.25

-- --- economy energy projection (server only): dℛ = k·Ψ·S·c^γ·(1+λR₊)·dt ---
Config.ResonanceEarnK = 0.35
Config.ResonanceCoherenceGamma = 1.35
Config.ResonanceSyncLambda = 0.35
Config.ResonanceCMin = 0.4

-- --- delta-wire (20Hz downlink) ---
Config.WireKeyframeInterval = 20
Config.WireDeltaEpsilon = 0.001
Config.UseWirePack = true

-- --- networking (bandwidth + CPU) ---
Config.ControlHz = 30
Config.ReplicateHz = 20
Config.EconomyAttributeHz = 5
Config.ReplicateEpsilon = 0.002
Config.UseUnreliableState = true
Config.InterpBufferScale = 1.05

-- --- presentation (client) ---
Config.TrailHz = 15
Config.CameraHz = 60

-- --- visuals ---
Config.TrackVisualSamples = 96

-- --- coherence tuning (anti-saturation; mirror python config.py) ---
Config.Alpha = 1.85
Config.CoherencePower = 2.5 -- Δc ∝ S·(1-c)^p

-- --- persistence ---
Config.EconomyAutosaveSec = 120

-- --- AFK cruise (realistic passive ℛ — not separate cash) ---
Config.AfkEarnMultiplier = 1.65
Config.AfkSessionCap = 250
Config.AfkCoherenceCap = 0.72
Config.AfkMinCoherence = 0.4
Config.AfkMinVelocity = 8
Config.AfkThrottle = 0.44
Config.AfkBrake = 0.15
Config.AfkBrakeAboveSpeed = 115
Config.AfkMinCruiseSpeed = 20
Config.AfkMaxCruiseSpeed = 72
Config.AfkSteerGain = 12

return Config
