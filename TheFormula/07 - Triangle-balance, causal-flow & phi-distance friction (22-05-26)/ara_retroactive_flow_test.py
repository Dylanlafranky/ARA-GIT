"""
ara_retroactive_flow_test.py

Retroactive diagnostic for ARA geometry flow.

This is not a forecast. It looks at actual geometry(t+h) and asks:

  1. Can a single scalar flow map current geometry toward natural future geometry?
  2. Can a single scalar flow map natural geometry toward event-cascade geometry?
  3. Does actual future same-rung cross-system geometry look more sync-like or
     gear-like around the ARA valve gate?

If the inferred scalar flow is stable, it may be reusable across formulas. If it
varies strongly by horizon/state/rung, flow should be modeled as a state variable.
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
    MIN_TRAIN,
    RUNG_KS,
    START_YEAR,
    clean_for_json,
    load_enso_frame,
    phase_alignment,
)
from ara_geometry_state_transition_test import (
    ORIGIN_STRIDE,
    build_snapshot_from_series,
    decode_state_features,
    event_ordered_cascade_decode_features,
    natural_advance_decode_features,
    raw_series_dict,
)
from ara_gear_coupled_transition_test import gear_event_ordered_cascade_decode_features
from ara_shape_kernel_test import PHI, release_fraction


SYSTEMS = ["NINO", "SOI", "PDO"]


def finite(value, fallback=0.0):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return fallback
    return value if math.isfinite(value) else fallback


def vectorize(features, keys, scale):
    return np.asarray([finite(features.get(key, 0.0)) / scale[key] for key in keys], dtype=float)


def best_scalar_flow(start, direction, actual):
    denom = float(np.dot(direction, direction))
    if denom <= 1e-12:
        return 0.0
    return float(np.dot(actual - start, direction) / denom)


def mae_vec(left, right):
    return float(np.mean(np.abs(left - right)))


def summarize(values):
    vals = np.asarray([finite(v) for v in values if math.isfinite(finite(v))], dtype=float)
    if len(vals) == 0:
        return {"n": 0}
    return {
        "n": int(len(vals)),
        "mean": float(np.mean(vals)),
        "std": float(np.std(vals)),
        "p10": float(np.percentile(vals, 10)),
        "p50": float(np.percentile(vals, 50)),
        "p90": float(np.percentile(vals, 90)),
        "min": float(np.min(vals)),
        "max": float(np.max(vals)),
    }


def signed_phase_gap(a, b):
    """Signed shortest difference b-a in cycles."""
    return ((float(b) - float(a) + 0.5) % 1.0) - 0.5


def by_k(subsystem):
    return {int(rung["k"]): rung for rung in subsystem["rungs"]}


def gear_phase(source_phase, target_ara):
    gate = release_fraction(target_ara)
    return (2.0 * gate - float(source_phase)) % 1.0


def future_pair_alignment(snapshot_future):
    """Compare actual future cross-system same-rung sync vs gear alignment."""
    sync_vals = []
    gear_vals = []
    gear_minus_sync = []
    for target_name in SYSTEMS:
        target_rungs = by_k(snapshot_future[target_name])
        for source_name in SYSTEMS:
            if source_name == target_name:
                continue
            source_rungs = by_k(snapshot_future[source_name])
            for k in sorted(set(target_rungs).intersection(source_rungs)):
                target = target_rungs[k]
                source = source_rungs[k]
                weight = math.sqrt(max(target["occupancy"], 0.0) * max(source["occupancy"], 0.0))
                if weight <= 1e-12:
                    continue
                sync = phase_alignment(source["phase"], target["phase"])
                gear = phase_alignment(gear_phase(source["phase"], target["ara"]), target["phase"])
                sync_vals.append(weight * sync)
                gear_vals.append(weight * gear)
                gear_minus_sync.append(weight * (gear - sync))
    return {
        "weighted_sync_alignment": float(np.sum(sync_vals) / (len(sync_vals) + 1e-12)) if sync_vals else 0.0,
        "weighted_gear_alignment": float(np.sum(gear_vals) / (len(gear_vals) + 1e-12)) if gear_vals else 0.0,
        "weighted_gear_minus_sync": float(np.sum(gear_minus_sync) / (len(gear_minus_sync) + 1e-12)) if gear_minus_sync else 0.0,
    }


def rung_flow_diagnostics(snapshot_now, snapshot_future, horizon):
    rows = []
    for name in SYSTEMS:
        now_by_k = by_k(snapshot_now[name])
        fut_by_k = by_k(snapshot_future[name])
        for k in sorted(set(now_by_k).intersection(fut_by_k)):
            now = now_by_k[k]
            fut = fut_by_k[k]
            natural_phase = (now["phase"] + float(horizon) / max(now["period"], 1e-12)) % 1.0
            phase_residual = signed_phase_gap(natural_phase, fut["phase"])
            rows.append(
                {
                    "system": name,
                    "k": int(k),
                    "abs_phase_residual": abs(float(phase_residual)),
                    "signed_phase_residual": float(phase_residual),
                    "ara_delta": float(fut["ara"] - now["ara"]),
                    "abs_ara_delta": abs(float(fut["ara"] - now["ara"])),
                    "occupancy_delta": float(fut["occupancy"] - now["occupancy"]),
                    "abs_occupancy_delta": abs(float(fut["occupancy"] - now["occupancy"])),
                    "weight": float(math.sqrt(max(now["occupancy"], 0.0) * max(fut["occupancy"], 0.0))),
                }
            )
    return rows


def weighted_mean(rows, value_key):
    denom = sum(max(0.0, row["weight"]) for row in rows)
    if denom <= 1e-12:
        return None
    return float(sum(max(0.0, row["weight"]) * row[value_key] for row in rows) / denom)


def run():
    started = time.time()
    frame = load_enso_frame()
    dates = list(frame.index)
    series = raw_series_dict(frame)
    n = len(frame)
    max_h = max(HORIZONS)
    min_anchor = max(4 * max(RUNG_KS), int(4 * BASE ** max(RUNG_KS)), 48)
    start_idx = int(np.searchsorted(np.asarray(dates, dtype="datetime64[ns]"), np.datetime64(f"{START_YEAR}-01-01")))
    test_start = max(start_idx + 1, min_anchor + MIN_TRAIN + max_h + 1)
    last_origin = n - max_h
    all_anchors = list(range(min_anchor, n + 1))

    print("ARA retroactive geometry-flow diagnostic", flush=True)
    print("=" * 96, flush=True)
    print(f"sample: {dates[0].date()} -> {dates[-1].date()}  n={n}", flush=True)
    print("diagnostic only: actual future geometry is used to infer flow, not to forecast", flush=True)
    print(
        f"origins start: {dates[test_start - 1].date()}  "
        f"longest-horizon last origin: {dates[last_origin - 1].date()}  "
        f"origin_stride={ORIGIN_STRIDE}",
        flush=True,
    )
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
    keys = sorted(decode_cache[min_anchor].keys())
    scale = {}
    for key in keys:
        vals = np.asarray([finite(decode_cache[a].get(key, 0.0)) for a in all_anchors], dtype=float)
        std = float(np.std(vals))
        scale[key] = std if std > 1e-9 else 1.0

    horizon_rows = {h: [] for h in HORIZONS}
    rung_rows = {h: [] for h in HORIZONS}
    pair_rows = {h: [] for h in HORIZONS}

    for h in HORIZONS:
        for origin in range(test_start, n - h + 1, ORIGIN_STRIDE):
            target_anchor = origin + h
            current_features = decode_cache[origin]
            future_features = decode_cache[target_anchor]
            natural_features = natural_advance_decode_features(snapshots[origin], h)
            sync_features = event_ordered_cascade_decode_features(snapshots[origin], h)
            gear_features = gear_event_ordered_cascade_decode_features(snapshots[origin], h)

            current = vectorize(current_features, keys, scale)
            future = vectorize(future_features, keys, scale)
            natural = vectorize(natural_features, keys, scale)
            sync = vectorize(sync_features, keys, scale)
            gear = vectorize(gear_features, keys, scale)

            alpha_natural = best_scalar_flow(current, natural - current, future)
            alpha_sync_residual = best_scalar_flow(natural, sync - natural, future)
            alpha_gear_residual = best_scalar_flow(natural, gear - natural, future)

            natural_blend = current + alpha_natural * (natural - current)
            sync_blend = natural + alpha_sync_residual * (sync - natural)
            gear_blend = natural + alpha_gear_residual * (gear - natural)

            horizon_rows[h].append(
                {
                    "origin": dates[origin - 1].strftime("%Y-%m-%d"),
                    "target": dates[target_anchor - 1].strftime("%Y-%m-%d"),
                    "alpha_current_to_natural": alpha_natural,
                    "alpha_natural_to_sync_event": alpha_sync_residual,
                    "alpha_natural_to_gear_event": alpha_gear_residual,
                    "err_current": mae_vec(current, future),
                    "err_natural": mae_vec(natural, future),
                    "err_sync_event": mae_vec(sync, future),
                    "err_gear_event": mae_vec(gear, future),
                    "err_best_scalar_natural": mae_vec(natural_blend, future),
                    "err_best_scalar_sync_event": mae_vec(sync_blend, future),
                    "err_best_scalar_gear_event": mae_vec(gear_blend, future),
                }
            )
            rung_rows[h].extend(rung_flow_diagnostics(snapshots[origin], snapshots[target_anchor], h))
            pair_rows[h].append(future_pair_alignment(snapshots[target_anchor]))

    summaries = {}
    for h in HORIZONS:
        rows = horizon_rows[h]
        summaries[str(h)] = {
            "alpha_current_to_natural": summarize([row["alpha_current_to_natural"] for row in rows]),
            "alpha_natural_to_sync_event": summarize([row["alpha_natural_to_sync_event"] for row in rows]),
            "alpha_natural_to_gear_event": summarize([row["alpha_natural_to_gear_event"] for row in rows]),
            "mean_errors": {
                key: float(np.mean([row[key] for row in rows])) if rows else None
                for key in [
                    "err_current",
                    "err_natural",
                    "err_sync_event",
                    "err_gear_event",
                    "err_best_scalar_natural",
                    "err_best_scalar_sync_event",
                    "err_best_scalar_gear_event",
                ]
            },
            "rung_flow": {
                "weighted_abs_phase_residual": weighted_mean(rung_rows[h], "abs_phase_residual"),
                "weighted_abs_ara_delta": weighted_mean(rung_rows[h], "abs_ara_delta"),
                "weighted_abs_occupancy_delta": weighted_mean(rung_rows[h], "abs_occupancy_delta"),
            },
            "future_pair_alignment": {
                key: float(np.mean([row[key] for row in pair_rows[h]])) if pair_rows[h] else None
                for key in ["weighted_sync_alignment", "weighted_gear_alignment", "weighted_gear_minus_sync"]
            },
        }

    print("h  alpha_nat_mean/std   sync_alpha_mean/std  gear_alpha_mean/std  phase_res  pair gear-sync")
    for h in HORIZONS:
        summary = summaries[str(h)]
        an = summary["alpha_current_to_natural"]
        ass = summary["alpha_natural_to_sync_event"]
        ag = summary["alpha_natural_to_gear_event"]
        phase_res = summary["rung_flow"]["weighted_abs_phase_residual"]
        gear_minus_sync = summary["future_pair_alignment"]["weighted_gear_minus_sync"]
        print(
            f"{h:2d} "
            f"{an.get('mean', 0.0):8.3f}/{an.get('std', 0.0):6.3f} "
            f"{ass.get('mean', 0.0):10.3f}/{ass.get('std', 0.0):6.3f} "
            f"{ag.get('mean', 0.0):10.3f}/{ag.get('std', 0.0):6.3f} "
            f"{phase_res if phase_res is not None else float('nan'):9.4f} "
            f"{gear_minus_sync if gear_minus_sync is not None else float('nan'):+12.5f}",
            flush=True,
        )

    out = {
        "date": "2026-05-23",
        "method": "retroactive ARA geometry-flow diagnostic",
        "diagnostic_note": "Uses actual future geometry to infer flow; not a forecast.",
        "system": "ENSO",
        "horizons_months": HORIZONS,
        "rungs_k": RUNG_KS,
        "origin_stride_months": ORIGIN_STRIDE,
        "sample": {
            "start": dates[0].strftime("%Y-%m-%d"),
            "end": dates[-1].strftime("%Y-%m-%d"),
            "n": int(n),
            "test_start_origin": dates[test_start - 1].strftime("%Y-%m-%d"),
            "test_last_origin_longest_horizon": dates[last_origin - 1].strftime("%Y-%m-%d"),
        },
        "definitions": {
            "alpha_current_to_natural": "least-squares scalar alpha where future ~= current + alpha*(natural_phase_advance-current)",
            "alpha_natural_to_sync_event": "least-squares scalar alpha where future ~= natural + alpha*(sync_event_projection-natural)",
            "alpha_natural_to_gear_event": "least-squares scalar alpha where future ~= natural + alpha*(gear_event_projection-natural)",
            "weighted_gear_minus_sync": "positive means actual future same-rung cross-system phase geometry is more gear-like than sync-like",
        },
        "summaries": summaries,
        "rows": horizon_rows,
        "elapsed_seconds": round(time.time() - started, 3),
    }

    out_path = HERE / "ara_retroactive_flow_data.js"
    with out_path.open("w", encoding="utf-8") as f:
        f.write("window.ARA_RETROACTIVE_FLOW = ")
        json.dump(clean_for_json(out), f, indent=2, allow_nan=False)
        f.write(";\n")
    print(f"Saved -> {out_path}")


if __name__ == "__main__":
    run()
