"""
ara_gear_coupled_transition_test.py

Strict-causal ENSO test for the "coupled circles behave like gears" idea.

Existing event-cascade transport lets a source rung pull a receiving rung toward
the source's phase. This test adds a gear-coupled variant:

    incoming_phase = (2 * gate_phase - source_phase) mod 1

For cross-system contacts the gate is the target's ARA valve boundary:

    gate_phase = release_fraction(target_ara) = 1 / (1 + ARA)

Same-system transport remains normal source-phase coupling. This isolates the
question: does mirrored gear contact improve geometry(t)->geometry(t+h)->NINO?
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
    HORIZONS,
    HOME_PERIOD,
    MIN_TRAIN,
    RUNG_KS,
    START_YEAR,
    clean_for_json,
    fit_predict_ridge,
    lag_feature_dict,
    load_enso_frame,
    phase_alignment,
    score_points,
)
from ara_geometry_state_transition_test import (
    ORIGIN_STRIDE,
    build_snapshot_from_series,
    circular_phase,
    decode_state_features,
    event_ordered_cascade_decode_features,
    event_packet_strength,
    finalize_projected_subsystem,
    finite,
    natural_advance_decode_features,
    predict_ridge_model,
    raw_series_dict,
    fit_ridge_model,
)
from ara_shape_kernel_test import PHI, release_fraction


MODEL_KEYS = [
    "natural_advance_decoder",
    "sync_event_cascade_decoder",
    "gear_event_cascade_decoder",
    "same_rung_sync_pair_decoder",
    "same_rung_gear_pair_decoder",
    "lag_ridge",
]
ORACLE_KEY = "oracle_actual_future_geometry_decoder"


def gear_phase(source_phase, target_ara, gate_offset=0.0):
    gate = (release_fraction(target_ara) + float(gate_offset)) % 1.0
    return (2.0 * gate - float(source_phase)) % 1.0


def gear_event_ordered_cascade_snapshot(snapshot, horizon, gate_offset=0.0):
    """Event cascade where cross-system contact reverses phase like gears."""
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
        record["id"]: {"strength": 0.0, "phase_x": 0.0, "phase_y": 0.0, "ara_num": 0.0, "gear_contact": 0.0}
        for record in records
    }

    for source in sorted(records, key=lambda item: (item["period"], item["position"])):
        packet = event_packet_strength(source["old"], horizon)
        if packet <= 1e-12:
            continue
        for target in records:
            if target["period"] <= source["period"] * (1.0 + 1e-12):
                continue
            same_system = source["name"] == target["name"]
            if same_system:
                contact_phase = source["phase"]
                cross_gate = 1.0
            else:
                contact_phase = gear_phase(source["phase"], target["ara"], gate_offset=gate_offset)
                cross_gate = 1.0 / PHI

            distance = abs(target["position"] - source["position"])
            scale_gap = max(0.0, math.log(target["period"] / source["period"], BASE))

            if same_system:
                phase_gate = 0.25 + 0.75 * max(0.0, (1.0 + phase_alignment(source["phase"], target["phase"])) / 2.0)
            else:
                # Gear contact is strongest when the mirrored tooth lands near the receiving tooth.
                phase_gate = 0.25 + 0.75 * max(0.0, (1.0 + phase_alignment(contact_phase, target["phase"])) / 2.0)

            weight = packet * (PHI ** (-(distance + 0.5 * scale_gap))) * phase_gate * cross_gate
            angle = 2.0 * math.pi * contact_phase
            slot = incoming[target["id"]]
            slot["strength"] += weight
            slot["phase_x"] += weight * math.cos(angle)
            slot["phase_y"] += weight * math.sin(angle)
            slot["ara_num"] += weight * source["ara"]
            slot["gear_contact"] += 0.0 if same_system else weight

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
        for idx, rung in enumerate(subsystem["rungs"]):
            old = old_rungs[idx]
            slot = incoming[(name, idx)]
            strength = slot["strength"]
            natural_phase = float(rung["phase"])
            if strength > 1e-12:
                influence = flow * strength / (strength + old_occ[idx] + 1e-12)
                influence = max(0.0, min(0.75, influence))
                incoming_phase = circular_phase(slot["phase_x"], slot["phase_y"])
                incoming_ara = slot["ara_num"] / strength
            else:
                influence = 0.0
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
            rung["occupancy"] = float(new_occ[idx])

        finalize_projected_subsystem(subsystem, total_energy, home_ara=None)
        subsystem["home_ara"] = (1.0 - flow) * snapshot[name]["home_ara"] + flow * subsystem["center_ara"]

    return projected


def gear_event_ordered_cascade_decode_features(snapshot, horizon, gate_offset=0.0):
    return decode_state_features(gear_event_ordered_cascade_snapshot(snapshot, horizon, gate_offset=gate_offset))


def same_rung_pair_coupled_snapshot(snapshot, horizon, gear=True):
    """Cross-system same-rung coupling, closer to literal meshed gears."""
    flow = 1.0 - PHI ** (-float(horizon) / HOME_PERIOD)
    flow = max(0.0, min(0.75, flow))

    projected = {}
    records = []
    for name, subsystem in snapshot.items():
        projected_rungs = []
        for idx, rung in enumerate(subsystem["rungs"]):
            projected_rung = dict(rung)
            projected_rung["phase"] = float((rung["phase"] + horizon / rung["period"]) % 1.0)
            projected_rungs.append(projected_rung)
            records.append(
                {
                    "id": (name, idx),
                    "name": name,
                    "idx": idx,
                    "old": rung,
                    "period": float(rung["period"]),
                    "position": float(rung["position"]),
                    "phase": float(projected_rung["phase"]),
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
    by_name_k = {(record["name"], record["k"]): record for record in records}

    for target in records:
        for source_name in snapshot:
            if source_name == target["name"]:
                continue
            source = by_name_k.get((source_name, target["k"]))
            if source is None:
                continue

            source_energy = max(source["old"].get("occupancy", 0.0), 0.0) * max(source["old"].get("amp", 0.0), 0.0)
            target_energy = max(target["old"].get("occupancy", 0.0), 0.0) * max(target["old"].get("amp", 0.0), 0.0)
            packet = math.sqrt(source_energy * target_energy)
            if packet <= 1e-12:
                continue

            distance = abs(target["position"] - source["position"])
            if gear:
                contact_phase = gear_phase(source["phase"], target["ara"])
            else:
                contact_phase = source["phase"]
            phase_gate = 0.25 + 0.75 * max(0.0, (1.0 + phase_alignment(contact_phase, target["phase"])) / 2.0)
            weight = packet * (PHI ** (-distance)) * phase_gate / PHI
            angle = 2.0 * math.pi * contact_phase
            slot = incoming[target["id"]]
            slot["strength"] += weight
            slot["phase_x"] += weight * math.cos(angle)
            slot["phase_y"] += weight * math.sin(angle)
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
        for idx, rung in enumerate(subsystem["rungs"]):
            old = old_rungs[idx]
            slot = incoming[(name, idx)]
            strength = slot["strength"]
            natural_phase = float(rung["phase"])
            if strength > 1e-12:
                influence = flow * strength / (strength + old_occ[idx] + 1e-12)
                influence = max(0.0, min(0.75, influence))
                incoming_phase = circular_phase(slot["phase_x"], slot["phase_y"])
                incoming_ara = slot["ara_num"] / strength
            else:
                influence = 0.0
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
            rung["occupancy"] = float(new_occ[idx])

        finalize_projected_subsystem(subsystem, total_energy, home_ara=None)
        subsystem["home_ara"] = (1.0 - flow) * snapshot[name]["home_ara"] + flow * subsystem["center_ara"]

    return projected


def same_rung_pair_coupled_decode_features(snapshot, horizon, gear=True):
    return decode_state_features(same_rung_pair_coupled_snapshot(snapshot, horizon, gear=gear))


def point(origin_date, target_date, pred, actual, persistence):
    return {
        "origin": origin_date,
        "date": target_date,
        "pred": float(pred),
        "actual": float(actual),
        "persistence": float(persistence),
    }


def format_score(score):
    if "mae" not in score:
        return "n/a"
    return (
        f"MAE={score['mae']:.4f} vs pers={score['persistence_mae']:.4f} "
        f"lift={score['mae_lift_vs_persistence']:+.4f} corr={score['corr']:+.3f} "
        f"dir={score['direction']:.3f}"
    )


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
    all_anchors = list(range(min_anchor, n + 1))

    print("ARA gear-coupled geometry transition ENSO test", flush=True)
    print("=" * 104, flush=True)
    print(f"sample: {dates[0].date()} -> {dates[-1].date()}  n={n}", flush=True)
    print("gear rule: cross-system incoming_phase = 2*release_fraction(target ARA) - source_phase", flush=True)
    print(
        f"test origins start: {dates[test_start - 1].date()}  "
        f"longest-horizon last origin: {dates[last_origin - 1].date()}  "
        f"origin_stride={ORIGIN_STRIDE} months",
        flush=True,
    )
    print("strict guards: decoder a<t; lag baseline s+h<t", flush=True)
    print(flush=True)

    snapshots = {}
    t0 = time.time()
    for i, anchor in enumerate(all_anchors, start=1):
        snapshots[anchor] = build_snapshot_from_series(series, anchor)
        if i % 100 == 0:
            print(f"  snapshots {i:4d}/{len(all_anchors)} in {time.time() - t0:.1f}s", flush=True)
    print(f"  snapshots {len(all_anchors):4d}/{len(all_anchors)} in {time.time() - t0:.1f}s", flush=True)
    print(flush=True)

    decode_cache = {anchor: decode_state_features(snapshots[anchor]) for anchor in all_anchors}
    projection_cache = {h: {} for h in HORIZONS}
    for h in HORIZONS:
        for anchor in all_anchors:
            snap = snapshots[anchor]
            projection_cache[h][anchor] = {
                "natural_advance_decoder": natural_advance_decode_features(snap, h),
                "sync_event_cascade_decoder": event_ordered_cascade_decode_features(snap, h),
                "gear_event_cascade_decoder": gear_event_ordered_cascade_decode_features(snap, h, gate_offset=0.0),
                "same_rung_sync_pair_decoder": same_rung_pair_coupled_decode_features(snap, h, gear=False),
                "same_rung_gear_pair_decoder": same_rung_pair_coupled_decode_features(snap, h, gear=True),
            }

    all_points = {model: {h: [] for h in HORIZONS} for model in MODEL_KEYS + [ORACLE_KEY]}

    for h in HORIZONS:
        for origin in range(test_start, n - h + 1, ORIGIN_STRIDE):
            target_anchor = origin + h
            train_decoder = [a for a in all_anchors if a < origin]
            train_transition = [s for s in all_anchors if s + h < origin]
            if len(train_decoder) < MIN_TRAIN or len(train_transition) < MIN_TRAIN:
                continue

            actual = float(nino[target_anchor - 1])
            persistence = float(nino[origin - 1])
            origin_date = dates[origin - 1].strftime("%Y-%m-%d")
            target_date = dates[target_anchor - 1].strftime("%Y-%m-%d")

            decoder_model = fit_ridge_model(
                [decode_cache[a] for a in train_decoder],
                [float(nino[a - 1]) for a in train_decoder],
            )

            for model in [
                "natural_advance_decoder",
                "sync_event_cascade_decoder",
                "gear_event_cascade_decoder",
                "same_rung_sync_pair_decoder",
                "same_rung_gear_pair_decoder",
            ]:
                pred = float(predict_ridge_model(decoder_model, projection_cache[h][origin][model])[0])
                all_points[model][h].append(point(origin_date, target_date, pred, actual, persistence))

            train_y_delta = [float(nino[s + h - 1] - nino[s - 1]) for s in train_transition]
            lag_delta, _, _ = fit_predict_ridge(
                [lag_feature_dict(nino, s) for s in train_transition],
                train_y_delta,
                lag_feature_dict(nino, origin),
            )
            all_points["lag_ridge"][h].append(
                point(origin_date, target_date, persistence + lag_delta, actual, persistence)
            )

            oracle_pred = float(predict_ridge_model(decoder_model, decode_cache[target_anchor])[0])
            all_points[ORACLE_KEY][h].append(point(origin_date, target_date, oracle_pred, actual, persistence))

        print(f"h={h:>2} months")
        for model in MODEL_KEYS:
            print(f"  {model:38s} {format_score(score_points(all_points[model][h]))}")
        print(f"  {ORACLE_KEY:38s} {format_score(score_points(all_points[ORACLE_KEY][h]))}  diagnostic")
        best = min(MODEL_KEYS, key=lambda m: score_points(all_points[m][h]).get("mae", float("inf")))
        print(f"  best forecast: {best}")
        print()

    scores = {model: {h: score_points(all_points[model][h]) for h in HORIZONS} for model in MODEL_KEYS + [ORACLE_KEY]}
    winners = {str(h): min(MODEL_KEYS, key=lambda m: scores[m][h].get("mae", float("inf"))) for h in HORIZONS}

    out = {
        "date": "2026-05-22",
        "method": "strict-causal ARA gear-coupled geometry transition ENSO test",
        "leakage_guard": "At origin t, decoder training uses only geometry anchors a<t. Lag baseline uses only s+h<t. Deterministic projections use only geometry at origin.",
        "gear_rule": "cross-system incoming_phase = (2 * release_fraction(target_ara) - source_phase) mod 1",
        "system": "ENSO",
        "target": "NINO3.4 anomaly",
        "base": BASE,
        "home_period_months": HOME_PERIOD,
        "rungs_k": RUNG_KS,
        "horizons_months": HORIZONS,
        "min_train_examples": MIN_TRAIN,
        "origin_stride_months": ORIGIN_STRIDE,
        "models": {
            "natural_advance_decoder": "Advance phases naturally, then decode geometry.",
            "sync_event_cascade_decoder": "Existing event cascade: cross-system incoming phase is copied from source.",
            "gear_event_cascade_decoder": "Gear event cascade: cross-system phase is mirrored around the target ARA release gate.",
            "same_rung_sync_pair_decoder": "Same-rung cross-system pair coupling with copied source phase.",
            "same_rung_gear_pair_decoder": "Same-rung cross-system pair coupling with mirrored gear phase around the target ARA release gate.",
            "lag_ridge": "Control: causal target lags and slopes.",
            ORACLE_KEY: "Diagnostic only: decode actual future geometry.",
        },
        "scores": scores,
        "winners": winners,
        "points": all_points,
        "elapsed_seconds": round(time.time() - started, 3),
    }

    out_path = HERE / "ara_gear_coupled_transition_data.js"
    with out_path.open("w", encoding="utf-8") as f:
        f.write("window.ARA_GEAR_COUPLED_TRANSITION = ")
        json.dump(clean_for_json(out), f, indent=2, allow_nan=False)
        f.write(";\n")
    print(f"Saved -> {out_path}")


if __name__ == "__main__":
    run()
