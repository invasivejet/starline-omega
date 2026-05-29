"""Tunable engine parameters (shared contract with Roblox Config module)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EngineConfig:
    """All coefficients for the MVP coherent-motion kernel."""

    # --- motion core ---
    drag: float = 0.15
    max_speed: float = 120.0       # stable envelope max
    max_speed_hard: float = 200.0  # hard clamp
    throttle_accel: float = 80.0
    brake_decel: float = 120.0

    # --- smoothness ---
    jerk_weight: float = 1.0
    curve_weight: float = 2.0
    steering_gain: float = 0.08  # maps steer [-1,1] → curvature response

    # --- coherence (sacred: c) ---
    alpha: float = 1.85  # gain from smoothness S (tuned — anti-saturation)
    beta: float = 1.8    # penalty from instability I
    coherence_power: float = 2.5  # Δc ∝ S·(1-c)^p  — anti-saturation
    steer_instability_weight: float = 0.6
    brake_instability_weight: float = 0.4

    # --- flow-state (instant classify legacy) ---
    flow_stable_c: float = 0.4
    flow_resonant_c: float = 0.7

    # --- flow hysteresis (enter / exit) ---
    flow_enter_stable_c: float = 0.45
    flow_exit_stable_c: float = 0.38
    flow_enter_resonant_c: float = 0.72
    flow_exit_resonant_c: float = 0.65
    flow_enter_flow_c: float = 0.92
    flow_exit_flow_c: float = 0.85
    flow_enter_flow_R: float = 0.85
    flow_exit_flow_R: float = 0.75

    # --- no false reward (∂c/∂noise < 0) ---
    noise_penalty: float = 2.2
    noise_steer_weight: float = 1.0
    noise_oscillation_weight: float = 1.5
    noise_brake_weight: float = 0.8
    noise_jerk_weight: float = 0.3
    jerk_noise_scale: float = 8.0

    # --- resonance field (multiplicative, not buff) ---
    resonance_geom_weight: float = 0.55
    resonance_sync_weight: float = 0.45
    resonance_kappa_scale: float = 12.0

    # --- simulation vs presentation ---
    sim_dt: float = 1.0 / 60.0
    max_sim_steps_per_frame: int = 4
    max_sim_catchup_sec: float = 0.25
    replicate_epsilon: float = 0.002

    # --- economy energy: dℛ = k·Ψ·S·c^γ·(1+λ·R₊)·dt ---
    resonance_earn_k: float = 0.35
    resonance_coherence_gamma: float = 1.35
    resonance_sync_lambda: float = 0.35
    resonance_c_min: float = 0.4

    # --- predictive smoothness (anticipation) ---
    anticipation_ds: float = 8.0       # base lookahead Δs
    anticipation_speed_scale: float = 0.15  # Δs += k_v · v_eff
    anticipation_blend: float = 0.45   # weight on κ(s+Δs) vs κ(s)

    # --- resonance / speed feedback ---
    gamma: float = 0.35  # v_eff = v * (1 + gamma * coherence)

    # --- phase ---
    omega: float = 0.05  # phase += v * dt * omega
    sync_slipstream: float = 0.25   # drag reduction when R high
    sync_resonance: float = 0.15     # extra coherence when R high

    # --- audio mapping ---
    base_tempo: float = 90.0
    tempo_per_speed: float = 0.4
    harmony_from_sync: float = 1.0
    dissonance_from_coherence: float = 1.0

    # --- multiplayer ---
    min_players_for_sync: int = 1

    # --- AFK cruise (realistic passive ℛ) ---
    afk_earn_multiplier: float = 1.65  # with S·min(c,0.72) quality → ~40% active ℛ/min
    afk_session_cap: float = 250.0
    afk_coherence_cap: float = 0.72
    afk_min_coherence: float = 0.4
    afk_min_velocity: float = 8.0
    afk_throttle: float = 0.44
    afk_brake: float = 0.0
    afk_brake_above_speed: float = 115.0
    afk_min_cruise_speed: float = 20.0
    afk_max_cruise_speed: float = 72.0
    afk_steer_gain: float = 12.0
