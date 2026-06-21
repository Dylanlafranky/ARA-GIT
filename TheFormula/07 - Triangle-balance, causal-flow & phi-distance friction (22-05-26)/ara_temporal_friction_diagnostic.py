"""
ara_temporal_friction_diagnostic.py

Retroactive diagnostic for Dylan's temporal-friction hypothesis.

If natural geometry flow behaves like:

    flow = ARA / (ARA + temporal_friction)

then:

    temporal_friction = ARA * (1 - flow) / flow

The recent retroactive flow test found natural-flow alpha around 0.6-0.7, close
to phi-1 = 1/phi. This script checks whether the implied friction is near 1.

Diagnostic only: uses actual future geometry to infer flow.
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

from ara_geometry_transport_test import BASE, HORIZONS, MIN_TRAIN, RUNG_KS, START_YEAR, clean_for_json, load_enso_frame
from ara_geometry_state_transition_test import (
    ORIGIN_STRIDE,
    build_snapshot_from_series,
    decode_state_features,
    natural_advance_decode_features,
    raw_series_dict,
)
from ara_retroactive_flow_test import best_scalar_flow, finite, vectorize
from ara_shape_kernel_test import PHI


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
        "mae_vs_1": float(np.mean(np.abs(vals - 1.0))),
    }


def scale_from_decode_cache(decode_cache, anchors, keys):
    scale = {}
    for key in keys:
        vals = np.asarray([finite(decode_cache[a].get(key, 0.0)) for a in anchors], dtype=float)
        std = float(np.std(vals))
        scale[key] = std if std > 1e-9 else 1.0
    return scale


def triad_mean_ara(snapshot):
    return float(np.mean([finite(subsystem["center_ara"], 1.0) for subsystem in snapshot.values()]))


def triad_energy_weighted_ara(snapshot):
    weights = np.asarray([max(0.0, finite(subsystem["total_energy"], 0.0)) for subsystem in snapshot.values()], dtype=float)
    aras = np.asarray([finite(subsystem["center_ara"], 1.0) for subsystem in snapshot.values()], dtype=float)
    if float(weights.sum()) <= 1e-12:
        return float(np.mean(aras))
    return float(np.dot(weights / weights.sum(), aras))


def flow_from_ara(ara, friction=1.0):
    ara = max(1e-12, finite(ara, 1.0))
    friction = max(1e-12, finite(friction, 1.0))
    return float(ara / (ara + friction))


def friction_from_flow(ara, flow):
    ara = max(1e-12, finite(ara, 1.0))
    flow = max(1e-9, finite(flow, 1e-9))
    return float(ara * (1.0 - flow) / flow)


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

    print("ARA temporal-friction retro diagnostic", flush=True)
    print("=" * 88, flush=True)
    print(f"phi-1 = {PHI - 1.0:.6f};  flow(ARA=phi, friction=1) = {flow_from_ara(PHI):.6f}", flush=True)
    print("diagnostic only: actual future geometry is used to infer flow", flush=True)
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
    scale = scale_from_decode_cache(decode_cache, all_anchors, keys)

    rows = {h: [] for h in HORIZONS}
    for h in HORIZONS:
        for origin in range(test_start, n - h + 1, ORIGIN_STRIDE):
            target_anchor = origin + h
            current = vectorize(decode_cache[origin], keys, scale)
            future = vectorize(decode_cache[target_anchor], keys, scale)
            natural_features = natural_advance_decode_features(snapshots[origin], h)
            natural = vectorize(natural_features, keys, scale)
            flow = best_scalar_flow(current, natural - current, future)

            snap = snapshots[origin]
            target_ara = finite(snap["NINO"]["center_ara"], 1.0)
            mean_ara = triad_mean_ara(snap)
            weighted_ara = triad_energy_weighted_ara(snap)
            rows[h].append(
                {
                    "origin": dates[origin - 1].strftime("%Y-%m-%d"),
                    "target": dates[target_anchor - 1].strftime("%Y-%m-%d"),
                    "flow": flow,
                    "flow_minus_phi_inv": flow - (PHI - 1.0),
                    "target_ara": target_ara,
                    "triad_mean_ara": mean_ara,
                    "triad_energy_weighted_ara": weighted_ara,
                    "friction_target_ara": friction_from_flow(target_ara, flow),
                    "friction_triad_mean_ara": friction_from_flow(mean_ara, flow),
                    "friction_triad_energy_weighted_ara": friction_from_flow(weighted_ara, flow),
                    "flow_from_target_ara_friction_1": flow_from_ara(target_ara),
                    "flow_from_triad_mean_ara_friction_1": flow_from_ara(mean_ara),
                    "flow_from_weighted_ara_friction_1": flow_from_ara(weighted_ara),
                }
            )

    summaries = {}
    for h in HORIZONS:
        hrows = rows[h]
        summaries[str(h)] = {
            "flow": summarize([row["flow"] for row in hrows]),
            "flow_minus_phi_inv": summarize([row["flow_minus_phi_inv"] for row in hrows]),
            "target_ara": summarize([row["target_ara"] for row in hrows]),
            "triad_mean_ara": summarize([row["triad_mean_ara"] for row in hrows]),
            "triad_energy_weighted_ara": summarize([row["triad_energy_weighted_ara"] for row in hrows]),
            "friction_target_ara": summarize([row["friction_target_ara"] for row in hrows]),
            "friction_triad_mean_ara": summarize([row["friction_triad_mean_ara"] for row in hrows]),
            "friction_triad_energy_weighted_ara": summarize([row["friction_triad_energy_weighted_ara"] for row in hrows]),
            "ara_friction_1_flow_mae": {
                "target_ara": float(np.mean([abs(row["flow"] - row["flow_from_target_ara_friction_1"]) for row in hrows])),
                "triad_mean_ara": float(np.mean([abs(row["flow"] - row["flow_from_triad_mean_ara_friction_1"]) for row in hrows])),
                "triad_energy_weighted_ara": float(
                    np.mean([abs(row["flow"] - row["flow_from_weighted_ara_friction_1"]) for row in hrows])
                ),
                "constant_phi_inv": float(np.mean([abs(row["flow"] - (PHI - 1.0)) for row in hrows])),
            },
        }

    print("h  flow mean/std  flow-phiInv  friction(target)  friction(meanARA)  flow MAE: target/mean/phiInv")
    for h in HORIZONS:
        s = summaries[str(h)]
        flow = s["flow"]
        diff = s["flow_minus_phi_inv"]
        ft = s["friction_target_ara"]
        fm = s["friction_triad_mean_ara"]
        mae = s["ara_friction_1_flow_mae"]
        print(
            f"{h:2d} "
            f"{flow['mean']:7.3f}/{flow['std']:5.3f} "
            f"{diff['mean']:+9.3f} "
            f"{ft['mean']:10.3f}/{ft['std']:5.3f} "
            f"{fm['mean']:10.3f}/{fm['std']:5.3f} "
            f"{mae['target_ara']:7.3f}/{mae['triad_mean_ara']:7.3f}/{mae['constant_phi_inv']:7.3f}",
            flush=True,
        )

    out = {
        "date": "2026-05-23",
        "method": "retroactive temporal-friction diagnostic",
        "diagnostic_note": "Uses actual future geometry to infer flow; not a forecast.",
        "hypothesis": "flow = ARA / (ARA + temporal_friction); temporal_friction ~= 1 would make ARA=phi produce flow=phi-1.",
        "phi": PHI,
        "phi_minus_1": PHI - 1.0,
        "flow_phi_friction_1": flow_from_ara(PHI),
        "horizons_months": HORIZONS,
        "origin_stride_months": ORIGIN_STRIDE,
        "summaries": summaries,
        "rows": rows,
        "elapsed_seconds": round(time.time() - started, 3),
    }

    out_path = HERE / "ara_temporal_friction_data.js"
    with out_path.open("w", encoding="utf-8") as f:
        f.write("window.ARA_TEMPORAL_FRICTION = ")
        json.dump(clean_for_json(out), f, indent=2, allow_nan=False)
        f.write(";\n")
    print(f"Saved -> {out_path}")


if __name__ == "__main__":
    run()
