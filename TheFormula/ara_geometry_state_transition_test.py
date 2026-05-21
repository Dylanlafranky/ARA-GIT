"""
ara_geometry_state_transition_test.py

Strict-causal ENSO test of:

    geometry(t) -> geometry(t+h) -> NINO(t+h)

This is the follow-up to ara_geometry_transport_test.py. The previous test
regressed from current geometry features directly to a future value delta.
This test inserts the missing middle state:

  1. Build ARA geometry snapshots at rolling anchors.
  2. Learn a causal transition model from current geometry to future geometry.
  3. Learn a causal decoder from already-observed geometry states to NINO value.
  4. Predict future geometry, then decode that geometry into NINO.

For origin t and horizon h:
  - transition training uses anchors s where s + h < t
  - decoder training uses geometry anchors a where a < t
  - the test target at t+h is never used as input

An oracle decoder diagnostic is also reported. It uses the actual future
geometry state, so it is NOT a forecast; it measures the decoder ceiling.
"""

from __future__ import annotations

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

from ara_geometry_transport_test import (
    BASE,
    HOME_PERIOD,
    HORIZONS,
    MIN_TRAIN,
    RIDGE_ALPHA,
    RUNG_KS,
    START_YEAR,
    center_features,
    clean_for_json,
    coupling_drive,
    fit_predict_ridge,
    lag_feature_dict,
    load_enso_frame,
    phase_alignment,
    score_points,
    self_drive,
)
from ara_geometry_transport_test import build_snapshot as build_snapshot_from_series
from ara_shape_kernel_test import PHI, release_fraction, shape_value_at_phase


MODEL_KEYS = [
    "event_ordered_cascade_decoder",
    "phi_flow_decoder",
    "state_transition_decoder",
    "state_transition_decoder_current",
    "direct_value_geometry_ridge",
    "lag_ridge",
]
ORACLE_KEY = "oracle_actual_future_geometry_decoder"
ORIGIN_STRIDE = 3


def finite(value, fallback=0.0):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return fallback
    return value if math.isfinite(value) else fallback


def round_float(value, digits=6):
    return round(finite(value), digits)


def raw_series_dict(frame):
    return {name: {"z": frame[name].values.astype(float)} for name in frame.columns}


def merge_feature_dicts(*items):
    out = {}
    for item in items:
        out.update(item)
    return out


def same_k_pair_features(left, right, left_name, right_name):
    out = {}
    left_by_k = {r["k"]: r for r in left["rungs"]}
    right_by_k = {r["k"]: r for r in right["rungs"]}
    for k in RUNG_KS:
        prefix = f"{left_name.lower()}_{right_name.lower()}_k{k}"
        a = left_by_k.get(k)
        b = right_by_k.get(k)
        if a is None or b is None:
            out[f"{prefix}_distance"] = 0.0
            out[f"{prefix}_alignment"] = 0.0
            out[f"{prefix}_support"] = 0.0
            out[f"{prefix}_opposition"] = 0.0
            continue
        distance = abs(a["position"] - b["position"])
        align = phase_alignment(a["phase"], b["phase"])
        energy = math.sqrt(max(a["occupancy"], 0.0) * max(b["occupancy"], 0.0))
        proximity = BASE ** (-distance)
        out[f"{prefix}_distance"] = distance
        out[f"{prefix}_alignment"] = align
        out[f"{prefix}_support"] = energy * proximity * max(0.0, (1.0 + align) / 2.0)
        out[f"{prefix}_opposition"] = energy * proximity * max(0.0, (1.0 - align) / 2.0)
    return out


def decode_state_features(snapshot):
    """Full system geometry state, excluding raw current values."""
    out = {}
    for name, subsystem in snapshot.items():
        prefix = name.lower()
        out[f"{prefix}_home_ara"] = subsystem["home_ara"]
        out[f"{prefix}_center_position"] = subsystem["center_position"]
        out[f"{prefix}_center_ara"] = subsystem["center_ara"]
        out[f"{prefix}_center_phase_sin"] = math.sin(2.0 * math.pi * subsystem["center_phase"])
        out[f"{prefix}_center_phase_cos"] = math.cos(2.0 * math.pi * subsystem["center_phase"])
        out[f"{prefix}_total_energy"] = subsystem["total_energy"]
        out[f"{prefix}_release_balance"] = sum(
            (2.0 * r["is_release"] - 1.0) * r["occupancy"] for r in subsystem["rungs"]
        )

        by_k = {r["k"]: r for r in subsystem["rungs"]}
        for k in RUNG_KS:
            r = by_k.get(k)
            rprefix = f"{prefix}_k{k}"
            if r is None:
                out[f"{rprefix}_amp"] = 0.0
                out[f"{rprefix}_ara"] = 0.0
                out[f"{rprefix}_position"] = 0.0
                out[f"{rprefix}_occupancy"] = 0.0
                out[f"{rprefix}_phase_sin"] = 0.0
                out[f"{rprefix}_phase_cos"] = 0.0
                out[f"{rprefix}_shape_now"] = 0.0
                out[f"{rprefix}_component"] = 0.0
                out[f"{rprefix}_is_release"] = 0.0
                continue
            out[f"{rprefix}_amp"] = r["amp"]
            out[f"{rprefix}_ara"] = r["ara"]
            out[f"{rprefix}_position"] = r["position"]
            out[f"{rprefix}_occupancy"] = r["occupancy"]
            out[f"{rprefix}_phase_sin"] = math.sin(2.0 * math.pi * r["phase"])
            out[f"{rprefix}_phase_cos"] = math.cos(2.0 * math.pi * r["phase"])
            out[f"{rprefix}_shape_now"] = r["shape_now"]
            out[f"{rprefix}_component"] = r["amp"] * r["shape_now"]
            out[f"{rprefix}_is_release"] = r["is_release"]

    for left_name, right_name in [("NINO", "SOI"), ("NINO", "PDO"), ("SOI", "PDO")]:
        left = snapshot[left_name]
        right = snapshot[right_name]
        pair = center_features(left, right)
        prefix = f"{left_name.lower()}_{right_name.lower()}"
        out[f"{prefix}_center_distance"] = pair["distance"]
        out[f"{prefix}_center_ara_gap"] = pair["ara_gap"]
        out[f"{prefix}_center_phase_alignment"] = pair["phase_alignment"]
        out[f"{prefix}_center_energy_product"] = pair["energy_product"]
        out.update(same_k_pair_features(left, right, left_name, right_name))

    return {k: finite(v) for k, v in out.items()}


def movement_features(snapshot, horizon):
    nino = snapshot["NINO"]
    soi = snapshot["SOI"]
    pdo = snapshot["PDO"]
    soi_c = coupling_drive(nino, soi, horizon)
    pdo_c = coupling_drive(nino, pdo, horizon)
    sp_c = coupling_drive(soi, pdo, horizon)
    out = {
        "horizon": float(horizon),
        "nino_self_drive": self_drive(nino, horizon),
        "soi_self_drive": self_drive(soi, horizon),
        "pdo_self_drive": self_drive(pdo, horizon),
        "soi_to_nino_drive": soi_c["drive"],
        "soi_to_nino_support": soi_c["support"],
        "soi_to_nino_opposition": soi_c["opposition"],
        "pdo_to_nino_drive": pdo_c["drive"],
        "pdo_to_nino_support": pdo_c["support"],
        "pdo_to_nino_opposition": pdo_c["opposition"],
        "pdo_to_soi_drive": sp_c["drive"],
        "pdo_to_soi_support": sp_c["support"],
        "pdo_to_soi_opposition": sp_c["opposition"],
    }
    return {k: finite(v) for k, v in out.items()}


def current_value_features(snapshot):
    return {f"{name.lower()}_current": subsystem["current"] for name, subsystem in snapshot.items()}


def transition_features(snapshot, horizon, include_current=False, include_lags=False, nino_values=None, anchor=None):
    out = merge_feature_dicts(decode_state_features(snapshot), movement_features(snapshot, horizon))
    if include_current:
        out.update(current_value_features(snapshot))
    if include_lags:
        if nino_values is None or anchor is None:
            raise ValueError("nino_values and anchor are required for lag features")
        out.update({f"lag_{k}": v for k, v in lag_feature_dict(nino_values, anchor).items()})
    return out


def dicts_to_matrix(dicts, keys=None):
    if keys is None:
        keys = sorted({key for item in dicts for key in item})
    x = np.asarray([[finite(item.get(key, 0.0)) for key in keys] for item in dicts], dtype=float)
    return x, keys


def fit_ridge_multi(train_dicts, train_y, test_dict, alpha=RIDGE_ALPHA):
    x_train, keys = dicts_to_matrix(train_dicts)
    x_test, _ = dicts_to_matrix([test_dict], keys=keys)
    y = np.asarray(train_y, dtype=float)
    if y.ndim == 1:
        y = y.reshape(-1, 1)

    mean_x = x_train.mean(axis=0)
    std_x = x_train.std(axis=0)
    std_x[std_x < 1e-9] = 1.0
    xz = (x_train - mean_x) / std_x
    tz = (x_test - mean_x) / std_x

    mean_y = y.mean(axis=0)
    yc = y - mean_y
    reg = float(alpha) * np.eye(xz.shape[1])
    try:
        beta = np.linalg.solve(xz.T @ xz + reg, xz.T @ yc)
    except np.linalg.LinAlgError:
        beta, *_ = np.linalg.lstsq(xz.T @ xz + reg, xz.T @ yc, rcond=None)
    pred = mean_y + tz[0] @ beta
    return np.asarray(pred, dtype=float), keys


def fit_ridge_model(train_dicts, train_y, alpha=RIDGE_ALPHA):
    x_train, keys = dicts_to_matrix(train_dicts)
    y = np.asarray(train_y, dtype=float)
    if y.ndim == 1:
        y = y.reshape(-1, 1)

    mean_x = x_train.mean(axis=0)
    std_x = x_train.std(axis=0)
    std_x[std_x < 1e-9] = 1.0
    xz = (x_train - mean_x) / std_x

    mean_y = y.mean(axis=0)
    yc = y - mean_y
    reg = float(alpha) * np.eye(xz.shape[1])
    try:
        beta = np.linalg.solve(xz.T @ xz + reg, xz.T @ yc)
    except np.linalg.LinAlgError:
        beta, *_ = np.linalg.lstsq(xz.T @ xz + reg, xz.T @ yc, rcond=None)
    return {
        "keys": keys,
        "mean_x": mean_x,
        "std_x": std_x,
        "mean_y": mean_y,
        "beta": beta,
    }


def predict_ridge_model(model, test_dict):
    x_test, _ = dicts_to_matrix([test_dict], keys=model["keys"])
    tz = (x_test - model["mean_x"]) / model["std_x"]
    return np.asarray(model["mean_y"] + tz[0] @ model["beta"], dtype=float)


def vector_to_dict(vector, keys):
    return {key: finite(value) for key, value in zip(keys, vector)}


def sanitize_predicted_state_features(features):
    out = dict(features)
    for name in ["nino", "soi", "pdo"]:
        occ_keys = [f"{name}_k{k}_occupancy" for k in RUNG_KS]
        occ = np.asarray([max(0.0, finite(out.get(key, 0.0))) for key in occ_keys], dtype=float)
        if occ.sum() > 1e-9:
            occ /= occ.sum()
        for key, value in zip(occ_keys, occ):
            out[key] = float(value)

        for k in RUNG_KS:
            prefix = f"{name}_k{k}"
            amp = max(0.0, finite(out.get(f"{prefix}_amp", 0.0)))
            ara = min(3.0, max(0.2, finite(out.get(f"{prefix}_ara", 1.0))))
            phase_sin = finite(out.get(f"{prefix}_phase_sin", 0.0))
            phase_cos = finite(out.get(f"{prefix}_phase_cos", 1.0))
            norm = math.hypot(phase_sin, phase_cos)
            if norm > 1e-9:
                phase_sin /= norm
                phase_cos /= norm
            shape_now = min(1.4, max(-1.4, finite(out.get(f"{prefix}_shape_now", 0.0))))
            out[f"{prefix}_amp"] = amp
            out[f"{prefix}_ara"] = ara
            out[f"{prefix}_position"] = float(k) + ara / 2.0
            out[f"{prefix}_phase_sin"] = phase_sin
            out[f"{prefix}_phase_cos"] = phase_cos
            out[f"{prefix}_shape_now"] = shape_now
            out[f"{prefix}_component"] = amp * shape_now
            out[f"{prefix}_is_release"] = 1.0 if finite(out.get(f"{prefix}_is_release", 0.0)) >= 0.5 else 0.0

    return out


def circular_phase(vx, vy):
    if abs(vx) + abs(vy) < 1e-12:
        return 0.0
    return (math.atan2(vy, vx) / (2.0 * math.pi)) % 1.0


def phi_flow_snapshot(snapshot, horizon):
    """Deterministic phi-flow geometry projection.

    This treats flow as a smooth fraction of a home-period event:

        flow = 1 - phi^(-h / home_period)

    Rungs exchange influence through a phi-decayed distance kernel. Release
    rungs send more strongly; accumulating rungs receive more strongly.
    """
    flow = 1.0 - PHI ** (-float(horizon) / HOME_PERIOD)
    flow = max(0.0, min(0.75, flow))
    all_sources = []
    for source_name, source_subsystem in snapshot.items():
        for source_rung in source_subsystem["rungs"]:
            all_sources.append((source_name, source_rung))

    projected = {}
    for name, subsystem in snapshot.items():
        old_rungs = subsystem["rungs"]
        if not old_rungs:
            projected[name] = dict(subsystem)
            projected[name]["rungs"] = []
            continue

        field_values = []
        projected_rungs = []
        for target in old_rungs:
            field = 0.0
            ara_num = 0.0
            phase_x = 0.0
            phase_y = 0.0
            for source_name, source in all_sources:
                distance = abs(target["position"] - source["position"])
                align = max(0.0, (1.0 + phase_alignment(target["phase"], source["phase"])) / 2.0)
                source_gate = 1.0 + float(source["is_release"])
                receiver_gate = 1.0 + (1.0 - float(target["is_release"]))
                cross_gate = 1.0 if source_name == name else 1.0 / PHI
                weight = (
                    max(source["occupancy"], 0.0)
                    * (PHI ** (-distance))
                    * (0.25 + 0.75 * align)
                    * source_gate
                    * receiver_gate
                    * cross_gate
                )
                source_phase = (source["phase"] + horizon / source["period"]) % 1.0
                angle = 2.0 * math.pi * source_phase
                field += weight
                ara_num += weight * source["ara"]
                phase_x += weight * math.cos(angle)
                phase_y += weight * math.sin(angle)

            if field <= 1e-12:
                field = max(target["occupancy"], 0.0)
                ara_target = target["ara"]
                phase_target = (target["phase"] + horizon / target["period"]) % 1.0
            else:
                ara_target = ara_num / field
                phase_target = circular_phase(phase_x, phase_y)

            natural_phase = (target["phase"] + horizon / target["period"]) % 1.0
            natural_angle = 2.0 * math.pi * natural_phase
            target_angle = 2.0 * math.pi * phase_target
            blended_phase = circular_phase(
                (1.0 - flow) * math.cos(natural_angle) + flow * math.cos(target_angle),
                (1.0 - flow) * math.sin(natural_angle) + flow * math.sin(target_angle),
            )
            new_ara = (1.0 - flow) * target["ara"] + flow * ara_target
            field_values.append(field)
            projected_rungs.append(
                {
                    "k": target["k"],
                    "period": target["period"],
                    "theta": target.get("theta", 0.0),
                    "ara": float(max(0.2, min(3.0, new_ara))),
                    "phase": float(blended_phase),
                    "kernel": target.get("kernel"),
                }
            )

        field_values = np.asarray(field_values, dtype=float)
        desired_occ = field_values / field_values.sum() if field_values.sum() > 1e-12 else np.ones(len(old_rungs)) / len(old_rungs)
        old_occ = np.asarray([max(r["occupancy"], 0.0) for r in old_rungs], dtype=float)
        old_occ = old_occ / old_occ.sum() if old_occ.sum() > 1e-12 else np.ones(len(old_rungs)) / len(old_rungs)
        new_occ = (1.0 - flow) * old_occ + flow * desired_occ
        new_occ = new_occ / new_occ.sum() if new_occ.sum() > 1e-12 else old_occ
        total_energy = max(subsystem["total_energy"], 1e-12)

        phase_x = 0.0
        phase_y = 0.0
        center_position = 0.0
        center_ara = 0.0
        for idx, rung in enumerate(projected_rungs):
            rung["occupancy"] = float(new_occ[idx])
            rung["amp"] = float(math.sqrt(max(rung["occupancy"] * total_energy, 0.0)))
            rung["position"] = float(rung["k"] + rung["ara"] / 2.0)
            kernel = rung.get("kernel")
            if kernel is None:
                rung["shape_now"] = 0.0
            else:
                rung["shape_now"] = float(shape_value_at_phase(rung["phase"], rung["ara"], kernel))
            rung["component"] = float(rung["amp"] * rung["shape_now"])
            rung["is_release"] = 1.0 if rung["phase"] < release_fraction(rung["ara"]) else 0.0
            center_position += rung["position"] * rung["occupancy"]
            center_ara += rung["ara"] * rung["occupancy"]
            angle = 2.0 * math.pi * rung["phase"]
            phase_x += rung["occupancy"] * math.cos(angle)
            phase_y += rung["occupancy"] * math.sin(angle)

        projected_subsystem = dict(subsystem)
        projected_subsystem["rungs"] = projected_rungs
        projected_subsystem["center_position"] = float(center_position)
        projected_subsystem["center_ara"] = float(center_ara)
        projected_subsystem["center_phase"] = circular_phase(phase_x, phase_y)
        projected_subsystem["home_ara"] = (1.0 - flow) * subsystem["home_ara"] + flow * center_ara
        projected_subsystem["home_position"] = subsystem["home_position"]
        projected_subsystem["total_energy"] = float(total_energy)
        projected[name] = projected_subsystem

    return projected


def phi_flow_decode_features(snapshot, horizon):
    return decode_state_features(phi_flow_snapshot(snapshot, horizon))


def boundary_crossings(phase, delta, boundary):
    """Count threshold crossings in phase space over a forward delta."""
    start = float(phase)
    end = start + float(delta)
    boundary = float(boundary)
    if boundary <= 0.0:
        boundary = 1.0
    return max(0, int(math.floor(end - boundary) - math.floor(start - boundary)))


def event_packet_strength(rung, horizon):
    """Strength of a fast-rung event packet available to feed larger rungs."""
    delta = float(horizon) / max(float(rung["period"]), 1e-12)
    split = release_fraction(rung["ara"])
    release_crosses = boundary_crossings(rung["phase"], delta, split)
    wrap_crosses = boundary_crossings(rung["phase"], delta, 1.0)

    # A strict boundary-only packet is too sparse at short horizons, so include
    # a small winding pressure while still letting actual phase events dominate.
    winding_pressure = delta / (PHI**2)
    release_gate = 1.0 + float(rung["is_release"]) / PHI
    event_count = release_crosses + wrap_crosses / PHI + winding_pressure
    return max(0.0, rung["occupancy"]) * max(0.0, rung["amp"]) * event_count * release_gate


def event_ordered_cascade_snapshot(snapshot, horizon):
    """Deterministic small-to-large event cascade projection.

    The rule is intentionally directional: faster/smaller rungs emit event
    packets first, then larger/slower rungs receive phase, ARA, and occupancy
    nudges through a phi-decayed distance kernel.
    """
    flow = 1.0 - PHI ** (-float(horizon) / HOME_PERIOD)
    flow = max(0.0, min(0.75, flow))

    records = []
    projected = {}
    for name, subsystem in snapshot.items():
        projected_rungs = []
        for idx, rung in enumerate(subsystem["rungs"]):
            natural_phase = (rung["phase"] + horizon / rung["period"]) % 1.0
            projected_rung = dict(rung)
            projected_rung["phase"] = float(natural_phase)
            projected_rungs.append(projected_rung)
            records.append(
                {
                    "id": (name, idx),
                    "name": name,
                    "idx": idx,
                    "old": rung,
                    "natural": projected_rung,
                    "period": float(rung["period"]),
                    "position": float(rung["position"]),
                    "phase": float(natural_phase),
                    "ara": float(rung["ara"]),
                    "k": int(rung["k"]),
                }
            )
        projected_subsystem = dict(subsystem)
        projected_subsystem["rungs"] = projected_rungs
        projected[name] = projected_subsystem

    incoming = {
        record["id"]: {"strength": 0.0, "phase_x": 0.0, "phase_y": 0.0, "ara_num": 0.0}
        for record in records
    }

    for source in sorted(records, key=lambda item: (item["period"], item["position"])):
        packet = event_packet_strength(source["old"], horizon)
        if packet <= 1e-12:
            continue
        source_phase = source["phase"]
        source_angle = 2.0 * math.pi * source_phase
        for target in records:
            if target["period"] <= source["period"] * (1.0 + 1e-12):
                continue
            distance = abs(target["position"] - source["position"])
            scale_gap = max(0.0, math.log(target["period"] / source["period"], BASE))
            phase_gate = 0.25 + 0.75 * max(0.0, (1.0 + phase_alignment(source_phase, target["phase"])) / 2.0)
            cross_gate = 1.0 if source["name"] == target["name"] else 1.0 / PHI
            weight = packet * (PHI ** (-(distance + 0.5 * scale_gap))) * phase_gate * cross_gate
            slot = incoming[target["id"]]
            slot["strength"] += weight
            slot["phase_x"] += weight * math.cos(source_angle)
            slot["phase_y"] += weight * math.sin(source_angle)
            slot["ara_num"] += weight * source["ara"]

    for name, subsystem in projected.items():
        old_rungs = snapshot[name]["rungs"]
        if not old_rungs:
            continue

        incoming_values = np.asarray(
            [incoming[(name, idx)]["strength"] for idx in range(len(old_rungs))],
            dtype=float,
        )
        old_occ = np.asarray([max(r["occupancy"], 0.0) for r in old_rungs], dtype=float)
        old_occ = old_occ / old_occ.sum() if old_occ.sum() > 1e-12 else np.ones(len(old_rungs)) / len(old_rungs)

        if incoming_values.sum() > 1e-12:
            desired_occ = old_occ + incoming_values / incoming_values.sum()
            desired_occ = desired_occ / desired_occ.sum()
        else:
            desired_occ = old_occ
        new_occ = (1.0 - flow) * old_occ + flow * desired_occ
        new_occ = new_occ / new_occ.sum() if new_occ.sum() > 1e-12 else old_occ

        total_energy = max(snapshot[name]["total_energy"], 1e-12)
        center_position = 0.0
        center_ara = 0.0
        phase_x = 0.0
        phase_y = 0.0
        for idx, rung in enumerate(subsystem["rungs"]):
            old = old_rungs[idx]
            slot = incoming[(name, idx)]
            strength = slot["strength"]
            natural_phase = float(rung["phase"])
            influence = 0.0
            if strength > 1e-12:
                influence = flow * strength / (strength + old_occ[idx] + 1e-12)
                influence = max(0.0, min(0.75, influence))
                incoming_phase = circular_phase(slot["phase_x"], slot["phase_y"])
                incoming_ara = slot["ara_num"] / strength
            else:
                incoming_phase = natural_phase
                incoming_ara = old["ara"]

            natural_angle = 2.0 * math.pi * natural_phase
            incoming_angle = 2.0 * math.pi * incoming_phase
            rung["phase"] = float(
                circular_phase(
                    (1.0 - influence) * math.cos(natural_angle) + influence * math.cos(incoming_angle),
                    (1.0 - influence) * math.sin(natural_angle) + influence * math.sin(incoming_angle),
                )
            )
            rung["ara"] = float(max(0.2, min(3.0, (1.0 - influence) * old["ara"] + influence * incoming_ara)))
            rung["position"] = float(rung["k"] + rung["ara"] / 2.0)
            rung["occupancy"] = float(new_occ[idx])
            rung["amp"] = float(math.sqrt(max(rung["occupancy"] * total_energy, 0.0)))
            rung["shape_now"] = float(shape_value_at_phase(rung["phase"], rung["ara"], rung["kernel"]))
            rung["component"] = float(rung["amp"] * rung["shape_now"])
            rung["release_fraction"] = float(release_fraction(rung["ara"]))
            rung["is_release"] = 1.0 if rung["phase"] < rung["release_fraction"] else 0.0
            center_position += rung["position"] * rung["occupancy"]
            center_ara += rung["ara"] * rung["occupancy"]
            angle = 2.0 * math.pi * rung["phase"]
            phase_x += rung["occupancy"] * math.cos(angle)
            phase_y += rung["occupancy"] * math.sin(angle)

        subsystem["center_position"] = float(center_position)
        subsystem["center_ara"] = float(center_ara)
        subsystem["center_phase"] = circular_phase(phase_x, phase_y)
        subsystem["home_ara"] = (1.0 - flow) * snapshot[name]["home_ara"] + flow * center_ara
        subsystem["total_energy"] = float(total_energy)

    return projected


def event_ordered_cascade_decode_features(snapshot, horizon):
    return decode_state_features(event_ordered_cascade_snapshot(snapshot, horizon))


def state_error(predicted, actual):
    keys = sorted(set(predicted).intersection(actual))
    if not keys:
        return 0.0
    diffs = [abs(finite(predicted.get(k, 0.0)) - finite(actual.get(k, 0.0))) for k in keys]
    return float(np.mean(diffs))


def print_score_table(scores):
    for h in HORIZONS:
        print(f"h={h:>2} months")
        for model in MODEL_KEYS:
            s = scores[model][h]
            print(
                f"  {model:34s} "
                f"MAE={s.get('mae', float('nan')):.4f} "
                f"vs pers={s.get('persistence_mae', float('nan')):.4f} "
                f"lift={s.get('mae_lift_vs_persistence', float('nan')):+.4f} "
                f"corr={s.get('corr', float('nan')):+.3f} "
                f"dir={s.get('direction', float('nan')):.3f}"
            )
        oracle = scores[ORACLE_KEY][h]
        print(
            f"  {ORACLE_KEY:34s} "
            f"MAE={oracle.get('mae', float('nan')):.4f} "
            f"(diagnostic, not forecast)"
        )
        best = min(MODEL_KEYS, key=lambda m: scores[m][h].get("mae", float("inf")))
        print(f"  best forecast: {best}")
        print()


def run():
    started = time.time()
    frame = load_enso_frame()
    dates = list(frame.index)
    series = raw_series_dict(frame)
    nino = frame["NINO"].values.astype(float)
    n = len(frame)
    max_h = max(HORIZONS)
    min_anchor = max(4 * max(RUNG_KS), int(4 * BASE ** max(RUNG_KS)), 48)
    start_idx = int(np.searchsorted(np.asarray(dates, dtype="datetime64[ns]"), np.datetime64(f"{START_YEAR}-01-01")))
    test_start = max(start_idx + 1, min_anchor + MIN_TRAIN + max_h + 1)
    last_origin = n - max_h

    print("ARA geometry state-transition ENSO test", flush=True)
    print("=" * 112, flush=True)
    print(f"sample: {dates[0].date()} -> {dates[-1].date()}  n={n}", flush=True)
    print(f"base={BASE}, home_period={HOME_PERIOD} months, rungs={RUNG_KS}", flush=True)
    print(
        f"test origins start: {dates[test_start - 1].date()}  "
        f"longest-horizon last origin: {dates[last_origin - 1].date()}  "
        f"origin_stride={ORIGIN_STRIDE} months",
        flush=True,
    )
    print("strict guards: transition s+h<t; decoder a<t", flush=True)
    print(flush=True)

    snapshots = {}
    t0 = time.time()
    all_anchors = list(range(min_anchor, n + 1))
    for i, anchor in enumerate(all_anchors, start=1):
        snapshots[anchor] = build_snapshot_from_series(series, anchor)
        if i % 100 == 0:
            print(f"  snapshots {i:4d}/{len(all_anchors)} in {time.time() - t0:.1f}s", flush=True)
    print(f"  snapshots {len(all_anchors):4d}/{len(all_anchors)} in {time.time() - t0:.1f}s", flush=True)
    print(flush=True)

    decode_cache = {anchor: decode_state_features(snapshots[anchor]) for anchor in all_anchors}
    transition_cache = {h: {} for h in HORIZONS}
    for h in HORIZONS:
        for anchor in all_anchors:
            snap = snapshots[anchor]
            transition_cache[h][anchor] = {
                "geometry": transition_features(snap, h, include_current=False),
                "current": transition_features(snap, h, include_current=True),
                "lags": transition_features(snap, h, include_current=True, include_lags=True, nino_values=nino, anchor=anchor),
            }

    all_points = {model: {h: [] for h in HORIZONS} for model in MODEL_KEYS + [ORACLE_KEY]}
    state_errors = {model: {h: [] for h in HORIZONS} for model in MODEL_KEYS if model.startswith("state_transition")}

    for h in HORIZONS:
        origins = list(range(test_start, n - h + 1, ORIGIN_STRIDE))
        target_keys = sorted(decode_cache[min_anchor].keys())
        for origin in origins:
            if origin + h > n:
                continue
            train_transition = [s for s in all_anchors if s + h < origin]
            train_decoder = [a for a in all_anchors if a < origin]
            if len(train_transition) < MIN_TRAIN or len(train_decoder) < MIN_TRAIN:
                continue

            target_anchor = origin + h
            actual = float(nino[target_anchor - 1])
            persistence = float(nino[origin - 1])
            origin_date = dates[origin - 1].strftime("%Y-%m-%d")
            target_date = dates[target_anchor - 1].strftime("%Y-%m-%d")

            decoder_train_x = [decode_cache[a] for a in train_decoder]
            decoder_train_y = [float(nino[a - 1]) for a in train_decoder]

            decoder_model = fit_ridge_model(decoder_train_x, decoder_train_y)

            # Event-ordered cascade: fast/small rungs fire into slower/larger rungs first.
            event_geom = event_ordered_cascade_decode_features(snapshots[origin], h)
            event_pred = float(predict_ridge_model(decoder_model, event_geom)[0])
            all_points["event_ordered_cascade_decoder"][h].append(
                {
                    "origin": origin_date,
                    "date": target_date,
                    "pred": event_pred,
                    "actual": actual,
                    "persistence": persistence,
                }
            )

            # Deterministic phi-flow: current geometry -> phi-projected future geometry -> decoded value.
            phi_geom = phi_flow_decode_features(snapshots[origin], h)
            phi_pred = float(predict_ridge_model(decoder_model, phi_geom)[0])
            all_points["phi_flow_decoder"][h].append(
                {
                    "origin": origin_date,
                    "date": target_date,
                    "pred": phi_pred,
                    "actual": actual,
                    "persistence": persistence,
                }
            )

            # Two-stage forecasts: predict future geometry, then decode it.
            for model, feature_variant in [
                ("state_transition_decoder", "geometry"),
                ("state_transition_decoder_current", "current"),
            ]:
                train_x = [transition_cache[h][s][feature_variant] for s in train_transition]
                train_y = [[decode_cache[s + h].get(key, 0.0) for key in target_keys] for s in train_transition]
                pred_vec, _ = fit_ridge_multi(train_x, train_y, transition_cache[h][origin][feature_variant])
                pred_geom = sanitize_predicted_state_features(vector_to_dict(pred_vec, target_keys))
                pred = float(predict_ridge_model(decoder_model, pred_geom)[0])
                all_points[model][h].append(
                    {
                        "origin": origin_date,
                        "date": target_date,
                        "pred": pred,
                        "actual": actual,
                        "persistence": persistence,
                    }
                )
                state_errors[model][h].append(state_error(pred_geom, decode_cache[target_anchor]))

            # Direct value control: current geometry -> future value delta.
            train_y_delta = [float(nino[s + h - 1] - nino[s - 1]) for s in train_transition]
            direct_delta, _, _ = fit_predict_ridge(
                [transition_cache[h][s]["geometry"] for s in train_transition],
                train_y_delta,
                transition_cache[h][origin]["geometry"],
            )
            all_points["direct_value_geometry_ridge"][h].append(
                {
                    "origin": origin_date,
                    "date": target_date,
                    "pred": persistence + direct_delta,
                    "actual": actual,
                    "persistence": persistence,
                }
            )

            # Causal lag baseline.
            lag_delta, _, _ = fit_predict_ridge(
                [lag_feature_dict(nino, s) for s in train_transition],
                train_y_delta,
                lag_feature_dict(nino, origin),
            )
            all_points["lag_ridge"][h].append(
                {
                    "origin": origin_date,
                    "date": target_date,
                    "pred": persistence + lag_delta,
                    "actual": actual,
                    "persistence": persistence,
                }
            )

            # Diagnostic only: decode the actual future geometry using a causal decoder.
            oracle_pred = float(predict_ridge_model(decoder_model, decode_cache[target_anchor])[0])
            all_points[ORACLE_KEY][h].append(
                {
                    "origin": origin_date,
                    "date": target_date,
                    "pred": oracle_pred,
                    "actual": actual,
                    "persistence": persistence,
                }
            )

    scores = {model: {h: score_points(all_points[model][h]) for h in HORIZONS} for model in MODEL_KEYS + [ORACLE_KEY]}
    for model in state_errors:
        for h in HORIZONS:
            scores[model][h]["mean_abs_state_feature_error"] = (
                float(np.mean(state_errors[model][h])) if state_errors[model][h] else None
            )

    print_score_table(scores)

    winners = {}
    for h in HORIZONS:
        winners[str(h)] = min(MODEL_KEYS, key=lambda m: scores[m][h].get("mae", float("inf")))

    out = {
        "date": "2026-05-21",
        "method": "strict-causal ARA geometry state-transition ENSO test",
        "leakage_guard": "At origin t, transition training uses only s+h<t and decoder training uses only a<t.",
        "oracle_note": "oracle_actual_future_geometry_decoder uses the true future geometry and is diagnostic only, not a forecast.",
        "system": "ENSO",
        "target": "NINO3.4 anomaly",
        "feeders": ["SOI", "PDO"],
        "base": BASE,
        "home_period_months": HOME_PERIOD,
        "rungs_k": RUNG_KS,
        "horizons_months": HORIZONS,
        "ridge_alpha": RIDGE_ALPHA,
        "min_train_examples": MIN_TRAIN,
        "origin_stride_months": ORIGIN_STRIDE,
        "sample": {
            "start": dates[0].strftime("%Y-%m-%d"),
            "end": dates[-1].strftime("%Y-%m-%d"),
            "n": int(n),
            "test_start_origin": dates[test_start - 1].strftime("%Y-%m-%d"),
            "test_last_origin_longest_horizon": dates[last_origin - 1].strftime("%Y-%m-%d"),
        },
        "models": {
            "event_ordered_cascade_decoder": (
                "Deterministic small-to-large event-ordered cascade, then causal geometry decoder."
            ),
            "state_transition_decoder": "Predict full future geometry state from current geometry, then decode value.",
            "state_transition_decoder_current": "Same, with observed current subsystem values included in the transition input.",
            "phi_flow_decoder": "Deterministic phi-decayed geometry flow, then causal geometry decoder.",
            "direct_value_geometry_ridge": "Control: direct current-geometry to future-value delta regression.",
            "lag_ridge": "Control: causal NINO lags and slopes to future-value delta.",
            ORACLE_KEY: "Diagnostic only: causal decoder applied to actual future geometry.",
        },
        "scores": scores,
        "winners": winners,
        "points": all_points,
        "elapsed_seconds": round_float(time.time() - started, 3),
    }
    out_path = HERE / "ara_geometry_state_transition_data.js"
    with out_path.open("w", encoding="utf-8") as f:
        f.write("window.ARA_GEOMETRY_STATE_TRANSITION = ")
        json.dump(clean_for_json(out), f, indent=2, allow_nan=False)
        f.write(";\n")
    print(f"Saved -> {out_path}")


if __name__ == "__main__":
    run()
