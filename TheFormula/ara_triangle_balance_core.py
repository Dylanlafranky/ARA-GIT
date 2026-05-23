"""
ara_triangle_balance_core.py

Generic ARA triangle-balance feature engine.

This module is deliberately system-neutral. A dataset-specific runner supplies:
    - z-scored time series by subsystem name
    - ARA geometry snapshots by subsystem name
    - a TriadConfig naming target / counter / third systems

The same feature engine can then be applied to ENSO, ECG-derived coupled
signals, solar/planetary triads, or other three-system arrangements.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from ara_shape_kernel_test import PHI, release_fraction, shape_value_at_phase


@dataclass(frozen=True)
class TriadConfig:
    target: str
    counter: str
    third: str
    counter_sign: float = -1.0
    third_sign: float = 1.0
    third_to_target_sign: float = 1.0
    third_to_counter_sign: float = -1.0
    closure_third_weight: float = 0.5


def finite(value, fallback=0.0):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return fallback
    return value if math.isfinite(value) else fallback


def signed_value(zseries, name, anchor, sign=1.0, lag=0):
    idx = anchor - 1 - lag
    if idx < 0:
        idx = anchor - 1
    return float(sign) * finite(zseries[name][idx])


def safe_ratio(num, denom):
    return finite(num) / (abs(finite(denom)) + 1e-12)


def ara_side_weight(ara):
    """Weight one side by its ARA valve fraction."""
    ara = max(0.2, min(3.0, finite(ara, 1.0)))
    return 1.0 / (1.0 + ara)


def snap_pressure(feed, current_level):
    """Signed snap pressure when feeder magnitude exceeds stored level."""
    feed = finite(feed)
    current_level = finite(current_level)
    excess = max(0.0, abs(feed) - abs(current_level))
    if excess <= 0.0:
        return 0.0
    return math.copysign(excess, feed)


def pair_gate(left, right, base=2.0):
    distance = abs(left["center_position"] - right["center_position"])
    return base ** (-distance), distance


def active_period(subsystem, fallback=47.0):
    rungs = subsystem.get("rungs", [])
    if not rungs:
        return float(fallback)
    weights = [max(0.0, finite(rung.get("occupancy", 0.0))) for rung in rungs]
    total = sum(weights)
    if total <= 1e-12:
        return float(fallback)
    return float(sum(weight * finite(rung.get("period", fallback), fallback) for weight, rung in zip(weights, rungs)) / total)


def rotating_counter_sign(snapshot, horizon, config, home_period=47.0):
    """Smooth relation sign: +1 now, -1 at half-cycle, +1 at full-cycle."""
    period = max(active_period(snapshot[config.target], fallback=home_period), 1e-12)
    phase = float(horizon) / period
    sign = math.cos(2.0 * math.pi * phase)
    return sign, period, phase


def meta_wave_gate(snapshot, horizon, config, home_period=47.0):
    """Meta-cycle gate: current-side pressure near phase 0/full wave,
    counter-side pressure near half wave.

    The transition split uses the established ARA valve fraction:
        release = 1 / (1 + ARA)
        accumulate = ARA / (1 + ARA)
    """
    period = max(active_period(snapshot[config.target], fallback=home_period), 1e-12)
    phase = (float(horizon) / period) % 1.0
    wave = math.cos(2.0 * math.pi * phase)
    same_gate = 0.5 * (1.0 + wave)
    counter_gate = 1.0 - same_gate
    split = release_fraction(snapshot[config.target]["center_ara"])
    accumulate = 1.0 - split
    transition_sharpness = 1.0 + abs(accumulate - split)
    return {
        "meta_active_period": period,
        "meta_cycle_phase": phase,
        "meta_cycle_sin": math.sin(2.0 * math.pi * phase),
        "meta_cycle_cos": wave,
        "meta_same_gate": same_gate,
        "meta_counter_gate": counter_gate,
        "meta_release_fraction": split,
        "meta_accumulate_fraction": accumulate,
        "meta_transition_sharpness": transition_sharpness,
        "meta_same_release_gate": same_gate * split,
        "meta_same_accumulate_gate": same_gate * accumulate,
        "meta_counter_release_gate": counter_gate * split,
        "meta_counter_accumulate_gate": counter_gate * accumulate,
    }


def normalize_triangle(a_raw, r_raw, t_raw):
    vals = np.asarray([max(0.0, finite(a_raw)), max(0.0, finite(r_raw)), max(0.0, finite(t_raw))], dtype=float)
    if vals.sum() <= 1e-12:
        vals[:] = 1.0 / 3.0
    else:
        vals /= vals.sum()
    return float(vals[0]), float(vals[1]), float(vals[2])


def counter_balance_features(
    snapshot,
    zseries,
    anchor,
    horizon,
    config,
    include_snap,
    base=2.0,
    home_period=47.0,
    counter_sign_override=None,
):
    target_value = signed_value(zseries, config.target, anchor, 1.0)
    counter_sign = config.counter_sign if counter_sign_override is None else float(counter_sign_override)
    counter_value = signed_value(zseries, config.counter, anchor, counter_sign)
    third_value = signed_value(zseries, config.third, anchor, config.third_sign)

    target_sys = snapshot[config.target]
    counter_sys = snapshot[config.counter]
    third_sys = snapshot[config.third]

    tc_gate, tc_distance = pair_gate(target_sys, counter_sys, base=base)
    tt_gate, tt_distance = pair_gate(target_sys, third_sys, base=base)
    ct_gate, ct_distance = pair_gate(counter_sys, third_sys, base=base)

    target_weight = ara_side_weight(target_sys["center_ara"])
    counter_weight = ara_side_weight(counter_sys["center_ara"])
    third_weight = ara_side_weight(third_sys["center_ara"])

    weighted_target = target_weight * target_value
    weighted_counter = counter_weight * counter_value
    weighted_third = third_weight * third_value

    target_third = config.third_to_target_sign * weighted_third
    counter_third = config.third_to_counter_sign * weighted_third

    balance_to_target = tc_gate * (weighted_counter - weighted_target)
    balance_to_counter = tc_gate * (weighted_target - weighted_counter)
    feed_to_target = tt_gate * (target_third - weighted_target)
    feed_to_counter = ct_gate * (counter_third - weighted_counter)
    common_mode = 0.5 * (weighted_target + weighted_counter)
    imbalance = weighted_target - weighted_counter
    flow = 1.0 - PHI ** (-float(horizon) / home_period)
    flow = max(0.0, min(0.75, flow))

    out = {
        "horizon": float(horizon),
        "flow": flow,
        "target_value": target_value,
        "counter_value": counter_value,
        "third_value": third_value,
        "counter_relation_sign": counter_sign,
        "target_weight": target_weight,
        "counter_weight": counter_weight,
        "third_weight": third_weight,
        "weighted_target": weighted_target,
        "weighted_counter": weighted_counter,
        "weighted_third": weighted_third,
        "target_counter_gate": tc_gate,
        "target_counter_distance": tc_distance,
        "target_third_gate": tt_gate,
        "target_third_distance": tt_distance,
        "counter_third_gate": ct_gate,
        "counter_third_distance": ct_distance,
        "balance_to_target": balance_to_target,
        "balance_to_counter": balance_to_counter,
        "feed_to_target": feed_to_target,
        "feed_to_counter": feed_to_counter,
        "common_mode": common_mode,
        "imbalance": imbalance,
        "flow_balance_to_target": flow * balance_to_target,
        "flow_feed_to_target": flow * feed_to_target,
    }

    if include_snap:
        target_snap = tt_gate * snap_pressure(target_third, weighted_target)
        counter_snap = ct_gate * snap_pressure(counter_third, weighted_counter)
        out.update(
            {
                "target_snap": target_snap,
                "counter_snap": counter_snap,
                "snap_difference": target_snap - counter_snap,
                "snap_sum": target_snap + counter_snap,
                "flow_target_snap": flow * target_snap,
                "flow_counter_snap": flow * counter_snap,
                "is_target_snap": 1.0 if abs(target_third) > abs(weighted_target) else 0.0,
                "is_counter_snap": 1.0 if abs(counter_third) > abs(weighted_counter) else 0.0,
            }
        )

    return {key: finite(value) for key, value in out.items()}


def triangle_balance_features(
    snapshot,
    zseries,
    anchor,
    horizon,
    config,
    include_snap,
    base=2.0,
    home_period=47.0,
    counter_sign_override=None,
):
    base_features = counter_balance_features(
        snapshot,
        zseries,
        anchor,
        horizon,
        config,
        include_snap=include_snap,
        base=base,
        home_period=home_period,
        counter_sign_override=counter_sign_override,
    )
    energy = (
        abs(base_features["weighted_target"])
        + abs(base_features["weighted_counter"])
        + abs(base_features["weighted_third"])
        + 1e-12
    )

    target_v1 = signed_value(zseries, config.target, anchor, 1.0) - signed_value(zseries, config.target, anchor, 1.0, lag=1)
    target_v3 = (
        signed_value(zseries, config.target, anchor, 1.0)
        - signed_value(zseries, config.target, anchor, 1.0, lag=3)
    ) / 3.0
    target_v12 = (
        signed_value(zseries, config.target, anchor, 1.0)
        - signed_value(zseries, config.target, anchor, 1.0, lag=12)
    ) / 12.0

    counter_sign = config.counter_sign if counter_sign_override is None else float(counter_sign_override)
    counter_v1 = signed_value(zseries, config.counter, anchor, counter_sign) - signed_value(
        zseries, config.counter, anchor, counter_sign, lag=1
    )
    counter_v3 = (
        signed_value(zseries, config.counter, anchor, counter_sign)
        - signed_value(zseries, config.counter, anchor, counter_sign, lag=3)
    ) / 3.0

    third_v1 = signed_value(zseries, config.third, anchor, config.third_sign) - signed_value(
        zseries, config.third, anchor, config.third_sign, lag=1
    )
    third_v3 = (
        signed_value(zseries, config.third, anchor, config.third_sign)
        - signed_value(zseries, config.third, anchor, config.third_sign, lag=3)
    ) / 3.0

    pair_imbalance_ratio = min(1.0, abs(base_features["imbalance"]) / energy)
    feed_excess_ratio = min(1.0, abs(base_features["weighted_third"]) / energy)
    closure_error = abs(
        base_features["weighted_target"]
        - base_features["weighted_counter"]
        + config.closure_third_weight * base_features["weighted_third"]
    )
    triad_closure = 1.0 - min(1.0, closure_error / energy)
    coupling_coherence = (
        max(base_features["target_counter_gate"], 0.0)
        * max(base_features["target_third_gate"], 0.0)
        * max(base_features["counter_third_gate"], 0.0)
    ) ** (1.0 / 3.0)

    time_pressure = (
        0.50 * target_v1
        + 0.25 * target_v3
        + 0.15 * counter_v1
        + 0.05 * counter_v3
        + 0.05 * third_v1
        + 0.05 * third_v3
    )
    time_motion_ratio = min(1.0, abs(time_pressure) / energy)

    ara_raw = pair_imbalance_ratio + 0.5 * feed_excess_ratio
    rationality_raw = triad_closure * coupling_coherence
    time_raw = base_features["flow"] + time_motion_ratio
    tri_ara, tri_rationality, tri_time = normalize_triangle(ara_raw, rationality_raw, time_raw)

    balance_pressure = base_features["balance_to_target"] + 0.5 * base_features["feed_to_target"]
    rationality_pressure = triad_closure * (
        base_features["balance_to_target"] - 0.5 * base_features["feed_to_counter"]
    )
    snap_pressure_value = base_features.get("target_snap", 0.0) - 0.5 * base_features.get("counter_snap", 0.0)
    triangle_pressure = (
        tri_ara * (balance_pressure + snap_pressure_value)
        + tri_rationality * rationality_pressure
        + tri_time * time_pressure
    )

    out = dict(base_features)
    out.update(
        {
            "target_v1": target_v1,
            "target_v3": target_v3,
            "target_v12": target_v12,
            "counter_v1": counter_v1,
            "counter_v3": counter_v3,
            "third_v1": third_v1,
            "third_v3": third_v3,
            "pair_imbalance_ratio": pair_imbalance_ratio,
            "feed_excess_ratio": feed_excess_ratio,
            "closure_error": closure_error,
            "triad_closure": triad_closure,
            "coupling_coherence": coupling_coherence,
            "time_pressure": time_pressure,
            "time_motion_ratio": time_motion_ratio,
            "triangle_ara": tri_ara,
            "triangle_rationality": tri_rationality,
            "triangle_time": tri_time,
            "balance_pressure": balance_pressure,
            "rationality_pressure": rationality_pressure,
            "triangle_snap_pressure": snap_pressure_value,
            "triangle_pressure": triangle_pressure,
            "ara_x_balance": tri_ara * balance_pressure,
            "ara_x_snap": tri_ara * snap_pressure_value,
            "rationality_x_closure": tri_rationality * triad_closure,
            "rationality_x_pressure": tri_rationality * rationality_pressure,
            "time_x_pressure": tri_time * time_pressure,
            "time_x_flow": tri_time * base_features["flow"],
        }
    )

    if not include_snap:
        for key in [
            "target_snap",
            "counter_snap",
            "snap_difference",
            "snap_sum",
            "flow_target_snap",
            "flow_counter_snap",
            "is_target_snap",
            "is_counter_snap",
            "triangle_snap_pressure",
            "ara_x_snap",
        ]:
            out.pop(key, None)

    return {key: finite(value) for key, value in out.items()}


def rotating_counter_balance_features(snapshot, zseries, anchor, horizon, config, include_snap, base=2.0, home_period=47.0):
    sign, period, phase = rotating_counter_sign(snapshot, horizon, config, home_period=home_period)
    out = counter_balance_features(
        snapshot,
        zseries,
        anchor,
        horizon,
        config,
        include_snap=include_snap,
        base=base,
        home_period=home_period,
        counter_sign_override=sign,
    )
    out.update(
        {
            "rotating_counter_sign": sign,
            "rotating_counter_period": period,
            "rotating_counter_cycle_phase": phase,
            "rotating_counter_halfwave": 1.0 if sign < 0.0 else 0.0,
        }
    )
    return {key: finite(value) for key, value in out.items()}


def rotating_triangle_balance_features(snapshot, zseries, anchor, horizon, config, include_snap, base=2.0, home_period=47.0):
    sign, period, phase = rotating_counter_sign(snapshot, horizon, config, home_period=home_period)
    out = triangle_balance_features(
        snapshot,
        zseries,
        anchor,
        horizon,
        config,
        include_snap=include_snap,
        base=base,
        home_period=home_period,
        counter_sign_override=sign,
    )
    out.update(
        {
            "rotating_counter_sign": sign,
            "rotating_counter_period": period,
            "rotating_counter_cycle_phase": phase,
            "rotating_counter_halfwave": 1.0 if sign < 0.0 else 0.0,
        }
    )
    return {key: finite(value) for key, value in out.items()}


def add_meta_wave_gate_features(features, snapshot, horizon, config, home_period=47.0):
    """Add meta-wave blend gates without changing subsystem identity."""
    out = dict(features)
    gate = meta_wave_gate(snapshot, horizon, config, home_period=home_period)
    out.update(gate)

    same_gate = gate["meta_same_gate"]
    counter_gate = gate["meta_counter_gate"]
    release_gate = gate["meta_release_fraction"]
    accumulate_gate = gate["meta_accumulate_fraction"]

    gated_terms = [
        "triangle_pressure",
        "balance_pressure",
        "rationality_pressure",
        "time_pressure",
        "triangle_snap_pressure",
        "balance_to_target",
        "feed_to_target",
        "flow_balance_to_target",
        "flow_feed_to_target",
        "target_snap",
        "snap_difference",
    ]
    for key in gated_terms:
        value = finite(out.get(key, 0.0))
        out[f"meta_same_{key}"] = same_gate * value
        out[f"meta_counter_{key}"] = counter_gate * value
        out[f"meta_release_{key}"] = release_gate * value
        out[f"meta_accumulate_{key}"] = accumulate_gate * value
        out[f"meta_counter_release_{key}"] = counter_gate * release_gate * value
        out[f"meta_counter_accumulate_{key}"] = counter_gate * accumulate_gate * value

    balance_pressure = finite(out.get("balance_pressure", out.get("balance_to_target", 0.0)))
    snap_pressure_value = finite(out.get("triangle_snap_pressure", out.get("target_snap", 0.0)))
    time_pressure = finite(out.get("time_pressure", 0.0))
    rationality_pressure = finite(out.get("rationality_pressure", 0.0))

    out["meta_gated_counter_pressure"] = counter_gate * (balance_pressure + snap_pressure_value)
    out["meta_gated_same_pressure"] = same_gate * time_pressure
    out["meta_valved_counter_pressure"] = counter_gate * (
        release_gate * snap_pressure_value + accumulate_gate * balance_pressure
    )
    out["meta_gated_triangle_pressure"] = (
        same_gate * time_pressure
        + counter_gate * (balance_pressure + snap_pressure_value)
        + release_gate * rationality_pressure
    )
    return {key: finite(value) for key, value in out.items()}


def add_minimal_meta_wave_gate_features(features, snapshot, horizon, config, home_period=47.0):
    """Small, constrained meta-wave gate.

    This keeps the meta-wave as a clock/blender rather than a large feature
    expansion: near phase 0 use same-side continuation pressure, near half-wave
    use counter-balance pressure.
    """
    out = {}
    gate = meta_wave_gate(snapshot, horizon, config, home_period=home_period)
    out.update(gate)

    flow = finite(features.get("flow", 0.0))
    same_gate = gate["meta_same_gate"]
    counter_gate = gate["meta_counter_gate"]
    release_gate = gate["meta_release_fraction"]
    accumulate_gate = gate["meta_accumulate_fraction"]

    time_pressure = finite(features.get("time_pressure", 0.0))
    triangle_pressure = finite(features.get("triangle_pressure", 0.0))
    rationality_pressure = finite(features.get("rationality_pressure", 0.0))
    balance_to_target = finite(features.get("balance_to_target", 0.0))
    feed_to_target = finite(features.get("feed_to_target", 0.0))
    target_snap = finite(features.get("target_snap", 0.0))
    counter_snap = finite(features.get("counter_snap", 0.0))

    counter_pressure = balance_to_target + 0.5 * feed_to_target + target_snap - 0.5 * counter_snap
    same_pressure = 0.5 * time_pressure + 0.5 * triangle_pressure
    valved_counter_pressure = accumulate_gate * (balance_to_target + 0.5 * feed_to_target) + release_gate * (
        target_snap - 0.5 * counter_snap
    )

    out.update(
        {
            "horizon": finite(features.get("horizon", horizon)),
            "flow": flow,
            "same_pressure": same_pressure,
            "counter_pressure": counter_pressure,
            "valved_counter_pressure": valved_counter_pressure,
            "rationality_pressure": rationality_pressure,
            "same_gate_pressure": same_gate * same_pressure,
            "counter_gate_pressure": counter_gate * counter_pressure,
            "counter_gate_valved_pressure": counter_gate * valved_counter_pressure,
            "release_rationality_pressure": release_gate * rationality_pressure,
            "flow_same_gate_pressure": flow * same_gate * same_pressure,
            "flow_counter_gate_pressure": flow * counter_gate * counter_pressure,
            "flow_counter_gate_valved_pressure": flow * counter_gate * valved_counter_pressure,
            "flow_release_rationality_pressure": flow * release_gate * rationality_pressure,
            "minimal_meta_blend_pressure": same_gate * same_pressure + counter_gate * valved_counter_pressure,
            "flow_minimal_meta_blend_pressure": flow * (
                same_gate * same_pressure + counter_gate * valved_counter_pressure
            ),
        }
    )
    return {key: finite(value) for key, value in out.items()}


def triangle_fixed_delta(features):
    return features["flow"] * features["triangle_pressure"]


def add_per_rung_antiphase_features(features, snapshot, horizon, config, rung_ks=None):
    """Add one anti-phase gate per target rung so the runner can learn which
    larger/smaller wave owns each horizon."""
    out = dict(features)
    rungs = snapshot[config.target]["rungs"]
    if rung_ks is not None:
        allowed = set(rung_ks)
        rungs = [rung for rung in rungs if rung["k"] in allowed]

    triangle_pressure = finite(out.get("triangle_pressure", 0.0))
    balance_pressure = finite(out.get("balance_pressure", 0.0))
    rationality_pressure = finite(out.get("rationality_pressure", 0.0))
    time_pressure = finite(out.get("time_pressure", 0.0))
    snap_pressure_value = finite(out.get("triangle_snap_pressure", 0.0))

    for rung in rungs:
        k = int(rung["k"])
        prefix = f"rung_k{k}"
        phase = finite(rung["phase"])
        period = max(finite(rung["period"], 1.0), 1e-12)
        horizon_alignment = math.cos(2.0 * math.pi * float(horizon) / period)
        inphase = max(0.0, horizon_alignment)
        antiphase = max(0.0, -horizon_alignment)
        future_phase = (phase + horizon / period) % 1.0
        future_shape = shape_value_at_phase(future_phase, rung["ara"], rung["kernel"])
        now_shape = finite(rung.get("shape_now", 0.0))
        shape_delta = future_shape - now_shape

        out.update(
            {
                f"{prefix}_period": period,
                f"{prefix}_phase_sin": math.sin(2.0 * math.pi * phase),
                f"{prefix}_phase_cos": math.cos(2.0 * math.pi * phase),
                f"{prefix}_horizon_alignment": horizon_alignment,
                f"{prefix}_inphase_gate": inphase,
                f"{prefix}_antiphase_gate": antiphase,
                f"{prefix}_shape_now": now_shape,
                f"{prefix}_shape_future": future_shape,
                f"{prefix}_shape_delta": shape_delta,
                f"{prefix}_triangle_pressure_aligned": triangle_pressure * horizon_alignment,
                f"{prefix}_triangle_pressure_inphase": triangle_pressure * inphase,
                f"{prefix}_triangle_pressure_antiphase": -triangle_pressure * antiphase,
                f"{prefix}_balance_pressure_aligned": balance_pressure * horizon_alignment,
                f"{prefix}_rationality_pressure_aligned": rationality_pressure * horizon_alignment,
                f"{prefix}_time_pressure_aligned": time_pressure * horizon_alignment,
                f"{prefix}_snap_pressure_antiphase": -snap_pressure_value * antiphase,
                f"{prefix}_triangle_pressure_shape_future": triangle_pressure * future_shape,
                f"{prefix}_triangle_pressure_shape_delta": triangle_pressure * shape_delta,
            }
        )
    return {key: finite(value) for key, value in out.items()}
