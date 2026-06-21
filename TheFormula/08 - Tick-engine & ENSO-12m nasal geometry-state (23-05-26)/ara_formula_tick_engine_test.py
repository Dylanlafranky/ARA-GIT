"""
ara_formula_tick_engine_test.py

Strict-causal test of a constrained formula tick engine.

This follows the current framework more tightly than the previous variable
recursion test:

  1. Read current ARA/rung state from data[:t].
  2. Advance each rung one tick with bounded formula mechanics:
       phase flow = ARA / (ARA + temporal friction)
       energy_next = energy + incoming pressure - release - pi-leak +/- coupling
       ARA_next = slow bounded drift from phi pull / coupling pressure
  3. Repeat ticks to the forecast horizon.
  4. Decode the predicted geometry state into the observed value.

The learned version does NOT learn a free future variable vector.  It learns
only small scalar mechanism gains from completed one-tick transitions:
phase gain, coupling turn, energy input/release/leak, breath, and ARA drift.

Leakage guard for origin t and horizon h:
  - state snapshots at t use only data[:t]
  - formula gain training uses one-tick pairs s+tick < t only
  - value decoders use geometry anchors a < t only
  - direct controls use completed windows s+h < t only
  - actual future geometry is used only for oracle/error diagnostics
"""

from __future__ import annotations

import copy
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_ROOT))

from ara_geometry_state_transition_test import fit_ridge_model, predict_ridge_model
from ara_geometry_transport_test import clean_for_json, fit_predict_ridge, lag_feature_dict, score_points
from ara_phi_distance_bk_fit_test import (
    PHI,
    PI_LEAK_ENERGY,
    DatasetSpec,
    decode_signal_features,
    label_for,
    load_ecg_rr,
    load_enso,
    load_solar,
)
from ara_shape_kernel_test import release_fraction, shape_value_at_phase
from ara_tick_variable_recursion_test import (
    build_variable_caches,
    energy_variables,
    finite,
    format_score,
    gcd_list,
    min_anchor_for,
    state_feature_error,
    summarize,
    with_prefix,
)
from ara_triangle_amplitude_gate_test import universal_triangle_features


RIDGE_ALPHA_MECHANISM = 8.0
RIDGE_ALPHA_DECODER = 5.0
RIDGE_ALPHA_DIRECT = 10.0

MODEL_KEYS = [
    "natural_phase_decoder",
    "formula_tick_fixed_decoder",
    "formula_tick_learned_decoder",
    "direct_value_required_variables",
    "lag_ridge",
]
ORACLE_KEY = "oracle_actual_future_geometry_decoder"


def clip(value, lo, hi):
    return max(lo, min(hi, finite(value)))


def signed_phase_delta(start, end):
    return float(((finite(end) - finite(start) + 0.5) % 1.0) - 0.5)


def clone_state(state):
    new_state = dict(state)
    new_state["rungs"] = [dict(rung) for rung in state.get("rungs", [])]
    return new_state


def finalize_projected_state(state):
    total_energy = 0.0
    for rung in state["rungs"]:
        rung["ara"] = clip(rung.get("ara", 1.0), 0.2, 4.0)
        rung["energy"] = max(0.0, finite(rung.get("energy", 0.0)))
        rung["amp"] = math.sqrt(rung["energy"])
        rung["phase"] = finite(rung.get("phase", 0.0)) % 1.0
        rung["release_fraction"] = release_fraction(rung["ara"])
        rung["is_release"] = 1.0 if rung["phase"] < rung["release_fraction"] else 0.0
        rung["position"] = float(rung["k"]) + rung["ara"] / 2.0
        rung["shape_now"] = shape_value_at_phase(rung["phase"], rung["ara"], rung["kernel"])
        rung["component"] = rung["amp"] * rung["shape_now"]
        total_energy += rung["energy"]

    state["total_energy"] = float(total_energy)
    center_position = 0.0
    center_ara = 0.0
    phase_x = 0.0
    phase_y = 0.0
    if total_energy > 1e-12 and state["rungs"]:
        for rung in state["rungs"]:
            rung["occupancy"] = rung["energy"] / total_energy
            center_position += rung["position"] * rung["occupancy"]
            center_ara += rung["ara"] * rung["occupancy"]
            angle = 2.0 * math.pi * rung["phase"]
            phase_x += rung["occupancy"] * math.cos(angle)
            phase_y += rung["occupancy"] * math.sin(angle)
    else:
        for rung in state["rungs"]:
            rung["occupancy"] = 1.0 / max(1, len(state["rungs"]))
        center_position = finite(state.get("home_position", 0.0))
        center_ara = finite(state.get("home_ara", 1.0), 1.0)

    state["center_position"] = float(center_position)
    state["center_ara"] = float(center_ara)
    if abs(phase_x) + abs(phase_y) > 1e-12:
        state["center_phase"] = float((math.atan2(phase_y, phase_x) / (2.0 * math.pi)) % 1.0)
    else:
        state["center_phase"] = 0.0
    return state


def triangle_with_breath(state, spec, context):
    tri = universal_triangle_features(state, spec)
    pull = finite(tri.get("triangle_pull", 0.0))
    prev_pull = finite(context.get("prev_triangle_pull", pull))
    scale = max(finite(context.get("triangle_pull_scale", 1.0), 1.0), 1e-9)
    velocity_z = (pull - prev_pull) / scale
    position_mean = finite(context.get("triangle_pull_mean", pull))
    position_z = (pull - position_mean) / scale
    phase = (math.atan2(velocity_z, position_z) / (2.0 * math.pi)) % 1.0
    expansion_gate = 0.5 + 0.5 * math.tanh(velocity_z)
    tri.update(
        {
            "breath_position_z": float(position_z),
            "breath_velocity_z": float(velocity_z),
            "breath_slow_velocity_z": float(velocity_z),
            "breath_energy": float(math.hypot(position_z, velocity_z)),
            "breath_phase": float(phase),
            "breath_expansion_gate": float(expansion_gate),
            "breath_slow_expansion_gate": float(expansion_gate),
            "breath_circular_gate": float(0.5 + 0.5 * math.sin(2.0 * math.pi * phase)),
            "breath_pull": float(pull * expansion_gate),
            "breath_slow_pull": float(pull * expansion_gate),
            "breath_signed_pull": float(pull * math.tanh(velocity_z)),
            "breath_contracting_pull": float(pull * (1.0 - expansion_gate)),
        }
    )
    context["prev_triangle_pull"] = pull
    return tri


def state_to_geometry_features(state, spec, context=None):
    if context is None:
        context = {}
    out = {}
    out.update(decode_signal_features(state, spec))
    out.update(with_prefix("tri_", triangle_with_breath(state, spec, context)))
    return {key: finite(value) for key, value in out.items()}


def strip_triangle_features(geometry_features):
    tri = {}
    for key, value in geometry_features.items():
        if key.startswith("tri_"):
            tri[key[4:]] = finite(value)
    return tri


def geometry_feature_stats(geometry_cache, anchors):
    pulls = [finite(geometry_cache[a].get("tri_triangle_pull", 0.0)) for a in anchors if a in geometry_cache]
    if not pulls:
        return {"triangle_pull_mean": 0.0, "triangle_pull_scale": 1.0}
    scale = float(np.std(pulls))
    return {
        "triangle_pull_mean": float(np.mean(pulls)),
        "triangle_pull_scale": scale if scale > 1e-9 else 1.0,
    }


def coupling_maps(state, spec):
    phase_turn = {int(rung["k"]): 0.0 for rung in state.get("rungs", [])}
    energy_exchange = {int(rung["k"]): 0.0 for rung in state.get("rungs", [])}
    rungs = list(state.get("rungs", []))
    base = finite(getattr(spec, "base", 2.0), 2.0)
    for i, left in enumerate(rungs):
        for right in rungs[i + 1 :]:
            lk = int(left["k"])
            rk = int(right["k"])
            dist = abs(finite(left.get("position", 0.0)) - finite(right.get("position", 0.0)))
            contact = math.sqrt(max(0.0, finite(left.get("occupancy", 0.0))) * max(0.0, finite(right.get("occupancy", 0.0))))
            contact *= base ** (-dist)
            if contact <= 1e-12:
                continue
            l_target = (finite(right.get("phase", 0.0)) + 0.5) % 1.0
            r_target = (finite(left.get("phase", 0.0)) + 0.5) % 1.0
            phase_turn[lk] += contact * signed_phase_delta(left.get("phase", 0.0), l_target)
            phase_turn[rk] += contact * signed_phase_delta(right.get("phase", 0.0), r_target)
            occ_gap = finite(right.get("occupancy", 0.0)) - finite(left.get("occupancy", 0.0))
            anti = 0.5 * (1.0 - math.cos(2.0 * math.pi * signed_phase_delta(left.get("phase", 0.0), right.get("phase", 0.0))))
            exchange = contact * anti * occ_gap
            energy_exchange[lk] += exchange
            energy_exchange[rk] -= exchange
    return phase_turn, energy_exchange


def formula_pressures_for_rung(rung, state, tri, driver_delta_z, tick, spec, phase_turn, energy_exchange):
    period = max(finite(rung.get("period", 1.0), 1.0), 1e-9)
    ara = clip(rung.get("ara", 1.0), 0.2, 4.0)
    friction = 1.0 + PI_LEAK_ENERGY + abs(ara - PHI)
    flow = ara / max(ara + friction, 1e-12)
    base_phase_delta = float(tick) / period * flow

    current_shape = shape_value_at_phase(rung.get("phase", 0.0), ara, rung["kernel"])
    natural_shape = shape_value_at_phase(finite(rung.get("phase", 0.0)) + float(tick) / period, ara, rung["kernel"])
    shape_delta = natural_shape - current_shape

    pull = finite(tri.get("triangle_pull", 0.0))
    breath_signed = finite(tri.get("breath_signed_pull", 0.0))
    breath_pull = finite(tri.get("breath_pull", 0.0))
    occupancy = max(0.0, finite(rung.get("occupancy", 0.0)))
    release_pressure = max(0.0, -shape_delta) * (1.0 + pull) * (0.25 + occupancy)
    input_pressure = abs(finite(driver_delta_z)) * (0.25 + max(0.0, shape_delta)) * (0.25 + math.sqrt(max(0.0, occupancy)))
    leak_pressure = PI_LEAK_ENERGY * (float(tick) / period) * (1.0 + abs(ara - PHI))
    coupling_energy = finite(energy_exchange.get(int(rung["k"]), 0.0))
    coupling_turn = finite(phase_turn.get(int(rung["k"]), 0.0))
    breath_turn = breath_signed * (float(tick) / period)
    energy_turn = finite(driver_delta_z) * (float(tick) / period) * (0.25 + math.sqrt(max(0.0, occupancy)))
    return {
        "base_phase_delta": base_phase_delta,
        "coupling_turn": coupling_turn,
        "breath_turn": breath_turn,
        "energy_turn": energy_turn,
        "input_pressure": input_pressure,
        "release_pressure": release_pressure,
        "leak_pressure": leak_pressure,
        "coupling_energy": coupling_energy,
        "breath_energy": breath_pull,
        "phi_pull": (PHI - ara) * (float(tick) / period),
        "ara_coupling": coupling_energy,
        "ara_energy": finite(driver_delta_z) * (float(tick) / period),
        "ara_release": release_pressure,
    }


def default_phase_delta(features):
    return (
        finite(features.get("base_phase_delta", 0.0))
        + 0.15 * finite(features.get("coupling_turn", 0.0))
        + 0.05 * finite(features.get("breath_turn", 0.0))
        + 0.03 * finite(features.get("energy_turn", 0.0))
    )


def default_energy_log_delta(features):
    return (
        0.06 * finite(features.get("input_pressure", 0.0))
        - 0.08 * finite(features.get("release_pressure", 0.0))
        - 0.05 * finite(features.get("leak_pressure", 0.0))
        + 0.04 * finite(features.get("coupling_energy", 0.0))
        + 0.02 * finite(features.get("breath_energy", 0.0))
    )


def default_ara_delta(features):
    return (
        0.30 * finite(features.get("phi_pull", 0.0))
        + 0.05 * finite(features.get("ara_coupling", 0.0))
        + 0.02 * finite(features.get("ara_energy", 0.0))
        - 0.02 * finite(features.get("ara_release", 0.0))
    )


def fit_formula_mechanism_models(state_cache, geometry_cache, values, train_anchors, tick, spec):
    phase_rows = []
    phase_targets = []
    energy_rows = []
    energy_targets = []
    ara_rows = []
    ara_targets = []

    for anchor in train_anchors:
        state = state_cache.get(anchor)
        future = state_cache.get(anchor + tick)
        if state is None or future is None:
            continue
        tri = strip_triangle_features(geometry_cache[anchor])
        std = max(finite(state.get("std", 1.0), 1.0), 1e-9)
        prev_idx = max(0, anchor - tick - 1)
        driver_delta_z = (finite(values[anchor - 1]) - finite(values[prev_idx])) / std
        phase_turn, energy_exchange = coupling_maps(state, spec)
        future_by_k = {int(r["k"]): r for r in future.get("rungs", [])}
        for rung in state.get("rungs", []):
            f_rung = future_by_k.get(int(rung["k"]))
            if f_rung is None:
                continue
            features = formula_pressures_for_rung(
                rung,
                state,
                tri,
                driver_delta_z,
                tick,
                spec,
                phase_turn,
                energy_exchange,
            )
            phase_rows.append(
                {
                    "base_phase_delta": features["base_phase_delta"],
                    "coupling_turn": features["coupling_turn"],
                    "breath_turn": features["breath_turn"],
                    "energy_turn": features["energy_turn"],
                }
            )
            phase_targets.append(signed_phase_delta(rung.get("phase", 0.0), f_rung.get("phase", 0.0)))
            energy_rows.append(
                {
                    "input_pressure": features["input_pressure"],
                    "release_pressure": features["release_pressure"],
                    "leak_pressure": features["leak_pressure"],
                    "coupling_energy": features["coupling_energy"],
                    "breath_energy": features["breath_energy"],
                }
            )
            old_energy = max(finite(rung.get("energy", 0.0)), 1e-9)
            new_energy = max(finite(f_rung.get("energy", 0.0)), 1e-9)
            energy_targets.append(clip(math.log(new_energy / old_energy), -0.75, 0.75))
            ara_rows.append(
                {
                    "phi_pull": features["phi_pull"],
                    "ara_coupling": features["ara_coupling"],
                    "ara_energy": features["ara_energy"],
                    "ara_release": features["ara_release"],
                }
            )
            ara_targets.append(clip(finite(f_rung.get("ara", 1.0), 1.0) - finite(rung.get("ara", 1.0), 1.0), -0.20, 0.20))

    if len(phase_rows) < 24 or len(energy_rows) < 24 or len(ara_rows) < 24:
        return None
    return {
        "phase": fit_ridge_model(phase_rows, phase_targets, alpha=RIDGE_ALPHA_MECHANISM),
        "energy": fit_ridge_model(energy_rows, energy_targets, alpha=RIDGE_ALPHA_MECHANISM),
        "ara": fit_ridge_model(ara_rows, ara_targets, alpha=RIDGE_ALPHA_MECHANISM),
        "n_rows": int(len(phase_rows)),
    }


def predict_mechanism(models, kind, features, mode):
    if mode == "fixed" or models is None:
        if kind == "phase":
            return default_phase_delta(features)
        if kind == "energy":
            return default_energy_log_delta(features)
        if kind == "ara":
            return default_ara_delta(features)
    model = models[kind]
    return float(predict_ridge_model(model, features)[0])


def build_roll_bounds(state_cache, values, train_anchors, spec):
    value_rows = np.asarray([finite(values[a - 1]) for a in train_anchors if 1 <= a <= len(values)], dtype=float)
    if len(value_rows):
        v_lo = float(np.percentile(value_rows, 1))
        v_hi = float(np.percentile(value_rows, 99))
        v_span = max(v_hi - v_lo, float(np.std(value_rows)), 1e-9)
        value_bounds = (v_lo - 0.5 * v_span, v_hi + 0.5 * v_span)
    else:
        value_bounds = (-1e6, 1e6)

    energy_bounds = {}
    for k in spec.rungs_k:
        rows = []
        for anchor in train_anchors:
            state = state_cache.get(anchor)
            if state is None:
                continue
            for rung in state.get("rungs", []):
                if int(rung["k"]) == int(k):
                    rows.append(max(0.0, finite(rung.get("energy", 0.0))))
                    break
        vals = np.asarray(rows, dtype=float)
        if len(vals):
            e_lo = float(np.percentile(vals, 1))
            e_hi = float(np.percentile(vals, 99))
            e_span = max(e_hi - e_lo, float(np.std(vals)), 1e-9)
            energy_bounds[int(k)] = (max(0.0, e_lo - 0.5 * e_span), max(1e-9, e_hi + 0.5 * e_span))
        else:
            energy_bounds[int(k)] = (0.0, 1e9)
    return {"value": value_bounds, "energy_by_k": energy_bounds}


def apply_energy_wall(energy, bounds):
    lo, hi = bounds
    energy = max(0.0, finite(energy))
    if energy > hi:
        return hi - (energy - hi) / PHI
    if energy < lo:
        return lo + (lo - energy) / PHI
    return energy


def apply_value_wall(value, bounds):
    lo, hi = bounds
    value = finite(value)
    if value > hi:
        return hi - (value - hi) / PHI
    if value < lo:
        return lo + (lo - value) / PHI
    return value


def formula_one_tick(state, tri, driver_delta_z, tick, spec, models=None, mode="learned", bounds=None):
    next_state = clone_state(state)
    phase_turn, energy_exchange = coupling_maps(state, spec)
    next_rungs = []
    for rung in state.get("rungs", []):
        features = formula_pressures_for_rung(
            rung,
            state,
            tri,
            driver_delta_z,
            tick,
            spec,
            phase_turn,
            energy_exchange,
        )
        if mode == "natural":
            phase_delta = float(tick) / max(finite(rung.get("period", 1.0), 1.0), 1e-9)
            energy_log_delta = 0.0
            ara_delta = 0.0
        else:
            phase_delta = predict_mechanism(
                models,
                "phase",
                {
                    "base_phase_delta": features["base_phase_delta"],
                    "coupling_turn": features["coupling_turn"],
                    "breath_turn": features["breath_turn"],
                    "energy_turn": features["energy_turn"],
                },
                mode,
            )
            energy_log_delta = predict_mechanism(
                models,
                "energy",
                {
                    "input_pressure": features["input_pressure"],
                    "release_pressure": features["release_pressure"],
                    "leak_pressure": features["leak_pressure"],
                    "coupling_energy": features["coupling_energy"],
                    "breath_energy": features["breath_energy"],
                },
                mode,
            )
            ara_delta = predict_mechanism(
                models,
                "ara",
                {
                    "phi_pull": features["phi_pull"],
                    "ara_coupling": features["ara_coupling"],
                    "ara_energy": features["ara_energy"],
                    "ara_release": features["ara_release"],
                },
                mode,
            )
        new_rung = dict(rung)
        new_rung["phase"] = (finite(rung.get("phase", 0.0)) + clip(phase_delta, -0.45, 0.45)) % 1.0
        energy = max(0.0, finite(rung.get("energy", 0.0)) * math.exp(clip(energy_log_delta, -0.20, 0.20)))
        if bounds is not None:
            energy = apply_energy_wall(energy, bounds["energy_by_k"].get(int(rung["k"]), (0.0, 1e9)))
        new_rung["energy"] = energy
        new_rung["ara"] = clip(finite(rung.get("ara", 1.0), 1.0) + clip(ara_delta, -0.08, 0.08), 0.2, 4.0)
        next_rungs.append(new_rung)

    next_state["rungs"] = next_rungs
    return finalize_projected_state(next_state)


def roll_formula_state(state, horizon, tick, spec, decoder, mode, models, context, values, origin, bounds):
    current_state = finalize_projected_state(clone_state(state))
    previous_current = finite(values[max(0, origin - tick - 1)])
    current_value = finite(values[origin - 1])
    last_features = state_to_geometry_features(current_state, spec, dict(context))
    steps = int(horizon // tick)
    roll_context = dict(context)
    for _ in range(steps):
        std = max(finite(current_state.get("std", 1.0), 1.0), 1e-9)
        driver_delta_z = (current_value - previous_current) / std
        tri = triangle_with_breath(current_state, spec, roll_context)
        current_state = formula_one_tick(
            current_state,
            tri,
            driver_delta_z,
            tick,
            spec,
            models=models,
            mode=mode,
            bounds=bounds,
        )
        previous_current = current_value
        last_features = state_to_geometry_features(current_state, spec, roll_context)
        current_value = apply_value_wall(float(predict_ridge_model(decoder, last_features)[0]), bounds["value"])
        current_state["current"] = current_value
    return current_state, last_features, current_value


def make_point(origin, date, pred, actual, persistence, extras=None):
    out = {
        "origin": origin,
        "date": date,
        "pred": float(pred),
        "actual": float(actual),
        "persistence": float(persistence),
    }
    if extras:
        out.update(extras)
    return out


def run_dataset(spec: DatasetSpec):
    values = np.asarray(spec.values, dtype=float)
    n = len(values)
    tick = gcd_list(spec.horizons)
    max_h = max(spec.horizons)
    min_anchor = min_anchor_for(spec)
    test_start = max(
        spec.start_index_floor,
        min_anchor + spec.min_train * tick + max_h + 1,
    )
    if test_start >= n - max_h:
        test_start = max(min_anchor + spec.min_train * tick + max_h + 1, int(n * 0.70))

    base_anchors = list(range(min_anchor, n + 1, tick))
    origins_by_h = {
        h: list(range(test_start, n - h + 1, spec.origin_stride))
        for h in spec.horizons
        if h % tick == 0 and test_start < n - h + 1
    }
    needed = set(base_anchors)
    for h, origins in origins_by_h.items():
        needed.update(origins)
        needed.update(origin + h for origin in origins if origin + h <= n)
    needed = sorted(a for a in needed if min_anchor <= a <= n)

    print(f"\n{spec.name}: n={n}, unit={spec.unit}", flush=True)
    print(
        f"  tick={tick}, home={spec.home_period:g}, rungs={spec.rungs_k}, "
        f"min_anchor={min_anchor}, test_start={label_for(spec.dates, test_start)}",
        flush=True,
    )
    print(f"  building {len(needed)} causal formula states...", flush=True)
    state_cache, geometry_cache, energy_cache = build_variable_caches(spec, needed, tick)
    geometry_keys = sorted({key for item in geometry_cache.values() for key in item})

    points = {model: {str(h): [] for h in spec.horizons} for model in MODEL_KEYS + [ORACLE_KEY]}
    geometry_errors = {
        "natural_phase_decoder": {str(h): [] for h in spec.horizons},
        "formula_tick_fixed_decoder": {str(h): [] for h in spec.horizons},
        "formula_tick_learned_decoder": {str(h): [] for h in spec.horizons},
    }
    mechanism_rows = {}
    origin_model_cache = {}

    def get_origin_models(origin):
        cached = origin_model_cache.get(origin)
        if cached is not None:
            return cached

        train_tick = [
            a for a in base_anchors
            if a + tick < origin and a in state_cache and a + tick in state_cache
        ]
        train_decoder = [a for a in base_anchors if a < origin and a in geometry_cache]
        if len(train_tick) < spec.min_train or len(train_decoder) < spec.min_train:
            return None

        decoder = fit_ridge_model(
            [geometry_cache[a] for a in train_decoder],
            [float(values[a - 1]) for a in train_decoder],
            alpha=RIDGE_ALPHA_DECODER,
        )
        mechanisms = fit_formula_mechanism_models(state_cache, geometry_cache, values, train_tick, tick, spec)
        if mechanisms is None:
            return None
        stats = geometry_feature_stats(geometry_cache, train_decoder)
        bounds = build_roll_bounds(state_cache, values, train_decoder, spec)
        cached = {
            "train_tick": train_tick,
            "train_decoder": train_decoder,
            "decoder": decoder,
            "mechanisms": mechanisms,
            "context": stats,
            "bounds": bounds,
        }
        mechanism_rows[origin] = mechanisms["n_rows"]
        origin_model_cache[origin] = cached
        return cached

    for h in spec.horizons:
        h_key = str(h)
        origins = origins_by_h.get(h, [])
        for origin in origins:
            target_anchor = origin + h
            train_horizon = [
                a for a in base_anchors
                if a + h < origin and a in energy_cache and a + h in energy_cache
            ]
            origin_models = get_origin_models(origin)
            if origin_models is None or len(train_horizon) < spec.min_train:
                continue

            actual = float(values[target_anchor - 1])
            persistence = float(values[origin - 1])
            origin_date = label_for(spec.dates, origin)
            target_date = label_for(spec.dates, target_anchor)
            common = {
                "tick": float(tick),
                "steps": int(h // tick),
                "origin_anchor": int(origin),
                "target_anchor": int(target_anchor),
                "mechanism_rows": int(origin_models["mechanisms"]["n_rows"]),
            }

            for model_name, mode, mechanisms in [
                ("natural_phase_decoder", "natural", None),
                ("formula_tick_fixed_decoder", "fixed", None),
                ("formula_tick_learned_decoder", "learned", origin_models["mechanisms"]),
            ]:
                _, pred_features, pred_value = roll_formula_state(
                    state_cache[origin],
                    h,
                    tick,
                    spec,
                    origin_models["decoder"],
                    mode,
                    mechanisms,
                    origin_models["context"],
                    values,
                    origin,
                    origin_models["bounds"],
                )
                points[model_name][h_key].append(
                    make_point(origin_date, target_date, pred_value, actual, persistence, common)
                )
                geometry_errors[model_name][h_key].append(
                    state_feature_error(
                        pred_features,
                        geometry_cache.get(target_anchor),
                        geometry_cache,
                        origin_models["train_decoder"],
                        geometry_keys,
                    )
                )

            train_delta = [float(values[a + h - 1] - values[a - 1]) for a in train_horizon]
            direct_delta, _, _ = fit_predict_ridge(
                [energy_cache[a] for a in train_horizon],
                train_delta,
                energy_cache[origin],
                alpha=RIDGE_ALPHA_DIRECT,
            )
            points["direct_value_required_variables"][h_key].append(
                make_point(origin_date, target_date, persistence + direct_delta, actual, persistence, common)
            )
            lag_delta, _, _ = fit_predict_ridge(
                [lag_feature_dict(values, a) for a in train_horizon],
                train_delta,
                lag_feature_dict(values, origin),
                alpha=RIDGE_ALPHA_DIRECT,
            )
            points["lag_ridge"][h_key].append(
                make_point(origin_date, target_date, persistence + lag_delta, actual, persistence, common)
            )
            oracle_pred = float(predict_ridge_model(origin_models["decoder"], geometry_cache[target_anchor])[0])
            points[ORACLE_KEY][h_key].append(
                make_point(origin_date, target_date, oracle_pred, actual, persistence, common)
            )

        print(f"  h={h:>4} {spec.unit}", flush=True)
        for model in MODEL_KEYS:
            print(f"    {model:38s} {format_score(score_points(points[model][h_key]))}", flush=True)
        print(f"    {ORACLE_KEY:38s} {format_score(score_points(points[ORACLE_KEY][h_key]))}  diagnostic only", flush=True)

    scores = {model: {str(h): score_points(points[model][str(h)]) for h in spec.horizons} for model in MODEL_KEYS + [ORACLE_KEY]}
    for model, by_h in geometry_errors.items():
        for h_key, rows in by_h.items():
            vals = [finite(v, float("nan")) for v in rows]
            vals = [v for v in vals if math.isfinite(v)]
            scores[model][h_key]["mean_scaled_geometry_error"] = float(np.mean(vals)) if vals else None

    winners = {}
    for h in spec.horizons:
        h_key = str(h)
        candidates = {model: scores[model][h_key].get("mae", float("inf")) for model in MODEL_KEYS}
        winners[h_key] = min(candidates, key=candidates.get) if candidates else None

    return {
        "config": {
            "name": spec.name,
            "unit": spec.unit,
            "n": int(n),
            "home_period": float(spec.home_period),
            "base": float(spec.base),
            "rungs_k": spec.rungs_k,
            "horizons": spec.horizons,
            "tick": int(tick),
            "min_train": int(spec.min_train),
            "origin_stride": int(spec.origin_stride),
            "test_start": label_for(spec.dates, test_start),
            "min_anchor": int(min_anchor),
            "geometry_variable_count": int(len(geometry_keys)),
            "mechanism_rows": summarize(mechanism_rows.values()),
        },
        "scores": scores,
        "winners": winners,
        "geometry_error_summary": {
            model: {h: summarize(rows) for h, rows in by_h.items()}
            for model, by_h in geometry_errors.items()
        },
        "points": points,
    }


def run(out_path=HERE / "ara_formula_tick_engine_data.js"):
    started = time.time()
    print("ARA constrained formula tick engine test", flush=True)
    print("=" * 100, flush=True)
    print(
        "No leakage: state data[:t], mechanism gains s+tick<t, decoders a<t, controls s+h<t.",
        flush=True,
    )
    print(
        "The learned method fits only scalar mechanism gains, not a free future variable vector.",
        flush=True,
    )

    datasets = {}
    for spec in [load_enso(), load_solar(), load_ecg_rr()]:
        datasets[spec.name] = run_dataset(spec)

    out = {
        "date": "2026-05-23",
        "method": "strict-causal constrained ARA formula tick engine",
        "hypothesis": (
            "Prediction should improve when future geometry is advanced by lawful formula mechanics "
            "rather than by a free future-variable regression."
        ),
        "leakage_guard": (
            "At origin t, state snapshots use only data[:t]; mechanism gain training uses only completed "
            "one-tick pairs s+tick<t; decoders use geometry anchors a<t; direct controls use s+h<t; "
            "oracle future geometry is diagnostic only."
        ),
        "models": {
            "natural_phase_decoder": "Deterministic phase advance with no energy/ARA update.",
            "formula_tick_fixed_decoder": "Hand-fixed formula tick: ARA flow, energy in/release/pi-leak/coupling, slow ARA drift.",
            "formula_tick_learned_decoder": "Same formula tick with causal scalar mechanism gains fitted from one-tick geometry transitions.",
            "direct_value_required_variables": "Control: current required variables directly regress future value delta.",
            "lag_ridge": "Control: causal raw-value lags and slopes directly regress future value delta.",
            ORACLE_KEY: "Diagnostic only: causal decoder applied to actual future geometry.",
        },
        "ridge_alpha_mechanism": RIDGE_ALPHA_MECHANISM,
        "ridge_alpha_decoder": RIDGE_ALPHA_DECODER,
        "ridge_alpha_direct": RIDGE_ALPHA_DIRECT,
        "datasets": datasets,
        "elapsed_seconds": time.time() - started,
    }

    with out_path.open("w", encoding="utf-8") as f:
        f.write("window.ARA_FORMULA_TICK_ENGINE = ")
        json.dump(clean_for_json(out), f, indent=2, allow_nan=False)
        f.write(";\n")

    print("\nSummary", flush=True)
    print("-" * 100, flush=True)
    for name, data in datasets.items():
        print(name, flush=True)
        for h in data["config"]["horizons"]:
            h_key = str(h)
            winner = data["winners"].get(h_key)
            learned = data["scores"]["formula_tick_learned_decoder"].get(h_key, {})
            fixed = data["scores"]["formula_tick_fixed_decoder"].get(h_key, {})
            direct = data["scores"]["direct_value_required_variables"].get(h_key, {})
            lag = data["scores"]["lag_ridge"].get(h_key, {})
            oracle = data["scores"][ORACLE_KEY].get(h_key, {})
            print(
                f"  h={h:>4}: winner={winner} "
                f"learnedFormula MAE={learned.get('mae', float('nan')):.4f} "
                f"fixedFormula MAE={fixed.get('mae', float('nan')):.4f} "
                f"direct MAE={direct.get('mae', float('nan')):.4f} "
                f"lag MAE={lag.get('mae', float('nan')):.4f} "
                f"oracle MAE={oracle.get('mae', float('nan')):.4f}",
                flush=True,
            )
    print(f"\nWrote {out_path}", flush=True)
    print(f"Done in {time.time() - started:.1f}s", flush=True)


if __name__ == "__main__":
    run()
