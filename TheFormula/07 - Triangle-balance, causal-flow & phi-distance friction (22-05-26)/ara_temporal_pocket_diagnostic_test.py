"""
ara_temporal_pocket_diagnostic_test.py

Diagnostic for Dylan's "temporal pocket" interpretation:

    negative k in friction = B + k*|ARA-phi|

may be a resonance/collision pocket rather than a bad coefficient.  This script
keeps the same strict-causal coefficient fit from ara_phi_distance_bk_fit_test,
then asks whether negative-k / strong-pocket origins line up with:

  - larger same-horizon movement or next-horizon movement
  - release-boundary / snap-like states
  - anti-phase rung collision / gear-contact geometry

The k estimate is causal: it is fit only from windows s+h<t.  The future
movement is used only as the scored outcome.
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

from ara_geometry_transport_test import clean_for_json
from ara_phi_distance_bk_fit_test import (
    DatasetSpec,
    FRICTION_MAX,
    FRICTION_MIN,
    fit_bk,
    friction_from_flow,
    label_for,
    load_ecg_rr,
    load_enso,
    load_solar,
    phi_distance,
    read_signal_state,
    build_scale,
    vectorize,
    decode_signal_features,
    natural_advance_state,
)
from ara_retroactive_flow_test import best_scalar_flow


def finite(value, fallback=0.0):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return fallback
    return value if math.isfinite(value) else fallback


def clip(value, lo, hi):
    return max(lo, min(hi, finite(value)))


def phase_gap(a, b):
    d = abs((float(a) - float(b)) % 1.0)
    return min(d, 1.0 - d)


def boundary_gap(phase, boundary):
    return phase_gap(phase, boundary % 1.0)


def corr(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    good = np.isfinite(x) & np.isfinite(y)
    x = x[good]
    y = y[good]
    if len(x) < 5 or float(np.std(x)) < 1e-12 or float(np.std(y)) < 1e-12:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def mean(rows, key):
    vals = [finite(row.get(key, float("nan")), float("nan")) for row in rows]
    vals = [v for v in vals if math.isfinite(v)]
    return float(np.mean(vals)) if vals else None


def rate(rows, key):
    vals = [row.get(key) for row in rows if row.get(key) is not None]
    return float(np.mean(vals)) if vals else None


def summarize_values(values):
    vals = np.asarray([finite(v, float("nan")) for v in values], dtype=float)
    vals = vals[np.isfinite(vals)]
    if len(vals) == 0:
        return {"n": 0}
    return {
        "n": int(len(vals)),
        "mean": float(np.mean(vals)),
        "std": float(np.std(vals)),
        "p25": float(np.percentile(vals, 25)),
        "p50": float(np.percentile(vals, 50)),
        "p75": float(np.percentile(vals, 75)),
    }


def group_summary(rows):
    if not rows:
        return {"n": 0}
    return {
        "n": int(len(rows)),
        "mean_k": mean(rows, "k"),
        "mean_pocket_strength": mean(rows, "pocket_strength"),
        "mean_abs_delta": mean(rows, "abs_delta"),
        "mean_abs_next_h_delta": mean(rows, "abs_next_h_delta"),
        "mean_abs_next_tick_delta": mean(rows, "abs_next_tick_delta"),
        "surge_rate": rate(rows, "is_surge"),
        "next_h_surge_rate": rate(rows, "is_next_h_surge"),
        "anti_phase_energy": mean(rows, "anti_phase_energy"),
        "gear_contact_energy": mean(rows, "gear_contact_energy"),
        "adjacent_gear_contact": mean(rows, "adjacent_gear_contact"),
        "support_energy": mean(rows, "support_energy"),
        "collision_minus_support": mean(rows, "collision_minus_support"),
        "release_transition_gate": mean(rows, "release_transition_gate"),
        "release_boundary_gap": mean(rows, "release_boundary_gap"),
        "wrap_gate": mean(rows, "wrap_gate"),
        "release_balance": mean(rows, "release_balance"),
        "center_ara": mean(rows, "center_ara"),
        "phi_distance": mean(rows, "phi_distance"),
    }


def ratio(a, b):
    if a is None or b is None or abs(float(b)) < 1e-12:
        return None
    return float(a) / float(b)


def state_collision_features(state):
    phase = finite(state.get("center_phase", 0.0))
    ara = finite(state.get("center_ara", 1.0), 1.0)
    release_fraction = 1.0 / (1.0 + max(ara, 1e-12))
    release_gap = boundary_gap(phase, release_fraction)
    wrap_gap = min(phase, 1.0 - phase)

    anti_phase_energy = 0.0
    support_energy = 0.0
    gear_contact_energy = 0.0
    adjacent_gear_contact = 0.0
    weighted_gap_num = 0.0
    weighted_gap_den = 0.0

    rungs = state.get("rungs", [])
    for i, left in enumerate(rungs):
        for right in rungs[i + 1 :]:
            occ = math.sqrt(max(0.0, finite(left.get("occupancy", 0.0))) * max(0.0, finite(right.get("occupancy", 0.0))))
            if occ <= 1e-12:
                continue
            distance = abs(finite(left.get("position", 0.0)) - finite(right.get("position", 0.0)))
            proximity = float(state.get("base", 2.0)) ** (-distance) if "base" in state else 2.0 ** (-distance)
            weight = occ * proximity
            gap = phase_gap(finite(left.get("phase", 0.0)), finite(right.get("phase", 0.0)))
            alignment = math.cos(2.0 * math.pi * gap)
            anti_gate = max(0.0, (1.0 - alignment) / 2.0)
            support_gate = max(0.0, (1.0 + alignment) / 2.0)
            contact_gate = math.exp(-((gap - 0.5) ** 2) / (2.0 * 0.08**2))
            anti_phase_energy += weight * anti_gate
            support_energy += weight * support_gate
            gear_contact_energy += weight * contact_gate
            if abs(int(left.get("k", 0)) - int(right.get("k", 0))) == 1:
                adjacent_gear_contact += weight * contact_gate
            weighted_gap_num += weight * abs(gap - 0.5)
            weighted_gap_den += weight

    return {
        "center_phase": phase,
        "center_ara": ara,
        "phi_distance": phi_distance(ara),
        "release_fraction": release_fraction,
        "release_boundary_gap": release_gap,
        "release_transition_gate": math.exp(-(release_gap**2) / (2.0 * 0.08**2)),
        "wrap_gap": wrap_gap,
        "wrap_gate": math.exp(-(wrap_gap**2) / (2.0 * 0.08**2)),
        "release_balance": sum((2.0 * finite(r.get("is_release", 0.0)) - 1.0) * finite(r.get("occupancy", 0.0)) for r in rungs),
        "anti_phase_energy": anti_phase_energy,
        "support_energy": support_energy,
        "gear_contact_energy": gear_contact_energy,
        "adjacent_gear_contact": adjacent_gear_contact,
        "collision_minus_support": anti_phase_energy - support_energy,
        "weighted_anti_phase_gap": weighted_gap_num / weighted_gap_den if weighted_gap_den > 1e-12 else 0.5,
    }


def build_needed_anchors(spec: DatasetSpec):
    n = len(spec.values)
    max_h = max(spec.horizons)
    max_period = max(float(spec.base**k) for k in spec.rungs_k)
    min_anchor = max(int(math.ceil(4.0 * max_period)), int(4 * max(spec.rungs_k)), 48)
    test_start = max(spec.start_index_floor, min_anchor + spec.min_train * spec.anchor_stride + max_h + 1)
    if test_start >= n - max_h:
        test_start = max(min_anchor + max_h + 1, int(n * 0.70))
    base_anchors = list(range(min_anchor, n + 1, spec.anchor_stride))
    origins_by_h = {
        h: list(range(test_start, n - h + 1, spec.origin_stride))
        for h in spec.horizons
        if test_start < n - h + 1
    }
    needed = set(base_anchors)
    for h in spec.horizons:
        for a in base_anchors:
            if a + h <= n:
                needed.add(a + h)
        for origin in origins_by_h.get(h, []):
            needed.add(origin)
            if origin + h <= n:
                needed.add(origin + h)
    return min_anchor, test_start, base_anchors, origins_by_h, sorted(a for a in needed if min_anchor <= a <= n)


def summarize_horizon(rows):
    if not rows:
        return {"n": 0}
    negative = [row for row in rows if row["k"] < 0.0]
    nonnegative = [row for row in rows if row["k"] >= 0.0]
    strengths = np.asarray([row["pocket_strength"] for row in rows], dtype=float)
    if float(np.std(strengths)) > 1e-12:
        lo_cut = float(np.percentile(strengths, 25))
        hi_cut = float(np.percentile(strengths, 75))
        weak = [row for row in rows if row["pocket_strength"] <= lo_cut]
        strong = [row for row in rows if row["pocket_strength"] >= hi_cut]
    else:
        weak = []
        strong = []

    neg_s = group_summary(negative)
    non_s = group_summary(nonnegative)
    strong_s = group_summary(strong)
    weak_s = group_summary(weak)

    abs_delta_ratio = ratio(strong_s.get("mean_abs_delta"), weak_s.get("mean_abs_delta"))
    next_ratio = ratio(strong_s.get("mean_abs_next_h_delta"), weak_s.get("mean_abs_next_h_delta"))
    anti_ratio = ratio(strong_s.get("anti_phase_energy"), weak_s.get("anti_phase_energy"))
    transition_ratio = ratio(strong_s.get("release_transition_gate"), weak_s.get("release_transition_gate"))

    return {
        "n": int(len(rows)),
        "negative_k_n": int(len(negative)),
        "negative_k_share": float(len(negative) / len(rows)),
        "k": summarize_values([row["k"] for row in rows]),
        "B": summarize_values([row["B"] for row in rows]),
        "pocket_strength": summarize_values([row["pocket_strength"] for row in rows]),
        "all": group_summary(rows),
        "negative_k": neg_s,
        "nonnegative_k": non_s,
        "strong_pocket_q4": strong_s,
        "weak_pocket_q1": weak_s,
        "strong_vs_weak_abs_delta_ratio": abs_delta_ratio,
        "strong_vs_weak_next_h_delta_ratio": next_ratio,
        "strong_vs_weak_anti_phase_ratio": anti_ratio,
        "strong_vs_weak_release_transition_ratio": transition_ratio,
        "corr_pocket_abs_delta": corr([row["pocket_strength"] for row in rows], [row["abs_delta"] for row in rows]),
        "corr_pocket_next_h_delta": corr([row["pocket_strength"] for row in rows], [row["abs_next_h_delta"] for row in rows]),
        "corr_pocket_anti_phase": corr([row["pocket_strength"] for row in rows], [row["anti_phase_energy"] for row in rows]),
        "corr_pocket_gear_contact": corr([row["pocket_strength"] for row in rows], [row["gear_contact_energy"] for row in rows]),
        "corr_pocket_adjacent_contact": corr([row["pocket_strength"] for row in rows], [row["adjacent_gear_contact"] for row in rows]),
        "corr_pocket_release_transition": corr([row["pocket_strength"] for row in rows], [row["release_transition_gate"] for row in rows]),
        "corr_pocket_release_gap": corr([row["pocket_strength"] for row in rows], [row["release_boundary_gap"] for row in rows]),
        "corr_pocket_phi_distance": corr([row["pocket_strength"] for row in rows], [row["phi_distance"] for row in rows]),
        "corr_anti_phase_abs_delta": corr([row["anti_phase_energy"] for row in rows], [row["abs_delta"] for row in rows]),
        "corr_gear_contact_abs_delta": corr([row["gear_contact_energy"] for row in rows], [row["abs_delta"] for row in rows]),
    }


def run_dataset(spec: DatasetSpec):
    values = np.asarray(spec.values, dtype=float)
    n = len(values)
    min_anchor, test_start, base_anchors, origins_by_h, needed_anchors = build_needed_anchors(spec)

    print(f"\n{spec.name}: n={n}, unit={spec.unit}", flush=True)
    print(
        f"  home={spec.home_period:g}, rungs={spec.rungs_k}, "
        f"test_start={label_for(spec.dates, test_start)}, states={len(needed_anchors)}",
        flush=True,
    )

    state_cache = {}
    t0 = time.time()
    for i, anchor in enumerate(needed_anchors, start=1):
        state = read_signal_state(values, anchor, spec)
        state["base"] = spec.base
        state_cache[anchor] = state
        if i % 250 == 0:
            print(f"    states {i:4d}/{len(needed_anchors)} in {time.time() - t0:.1f}s", flush=True)
    print(f"    states {len(needed_anchors):4d}/{len(needed_anchors)} in {time.time() - t0:.1f}s", flush=True)

    decode_cache = {a: decode_signal_features(state, spec) for a, state in state_cache.items()}
    keys = sorted(next(iter(decode_cache.values())).keys())
    natural_cache = {
        h: {a: decode_signal_features(natural_advance_state(state_cache[a], h), spec) for a in needed_anchors}
        for h in spec.horizons
    }

    rows_by_h = {h: [] for h in spec.horizons}
    for h in spec.horizons:
        for origin in origins_by_h.get(h, []):
            target_anchor = origin + h
            train_transition = [
                a for a in base_anchors
                if a + h < origin and a in decode_cache and a + h in decode_cache
            ]
            train_decoder = [a for a in base_anchors if a < origin and a in decode_cache]
            if len(train_transition) < spec.min_train or len(train_decoder) < spec.min_train:
                continue

            scale = build_scale(decode_cache, train_decoder, keys)
            train_distances = []
            train_frictions = []
            train_abs_delta = []
            for s in train_transition:
                current_vec = vectorize(decode_cache[s], keys, scale)
                natural_vec = vectorize(natural_cache[h][s], keys, scale)
                future_vec = vectorize(decode_cache[s + h], keys, scale)
                alpha = best_scalar_flow(current_vec, natural_vec - current_vec, future_vec)
                ara = state_cache[s]["center_ara"]
                train_distances.append(phi_distance(ara))
                train_frictions.append(clip(friction_from_flow(ara, alpha), FRICTION_MIN, FRICTION_MAX))
                train_abs_delta.append(abs(float(values[s + h - 1] - values[s - 1])))

            B, k = fit_bk(train_distances, train_frictions)
            current = float(values[origin - 1])
            actual = float(values[target_anchor - 1])
            delta = actual - current
            if target_anchor + h <= n:
                next_h_delta = float(values[target_anchor + h - 1] - actual)
                abs_next_h_delta = abs(next_h_delta)
            else:
                next_h_delta = None
                abs_next_h_delta = float("nan")
            if target_anchor + 1 <= n:
                next_tick_delta = float(values[target_anchor] - actual)
                abs_next_tick_delta = abs(next_tick_delta)
            else:
                next_tick_delta = None
                abs_next_tick_delta = float("nan")

            threshold = float(np.percentile(train_abs_delta, 75)) if train_abs_delta else float("nan")
            features = state_collision_features(state_cache[origin])
            row = {
                "origin": label_for(spec.dates, origin),
                "date": label_for(spec.dates, target_anchor),
                "horizon": int(h),
                "B": float(B),
                "k": float(k),
                "pocket_strength": max(0.0, -float(k)),
                "is_negative_k": bool(k < 0.0),
                "current": current,
                "actual": actual,
                "delta": float(delta),
                "abs_delta": abs(float(delta)),
                "next_h_delta": next_h_delta,
                "abs_next_h_delta": abs_next_h_delta,
                "next_tick_delta": next_tick_delta,
                "abs_next_tick_delta": abs_next_tick_delta,
                "surge_threshold": threshold,
                "is_surge": bool(abs(float(delta)) >= threshold) if math.isfinite(threshold) else None,
                "is_next_h_surge": bool(abs_next_h_delta >= threshold) if math.isfinite(abs_next_h_delta) and math.isfinite(threshold) else None,
                **features,
            }
            rows_by_h[h].append(row)

        summary = summarize_horizon(rows_by_h[h])
        print(
            f"  h={h:>4}: n={summary['n']:>3} negK={summary['negative_k_share']:.2f} "
            f"corr pocket->absDelta={summary['corr_pocket_abs_delta']:+.3f} "
            f"pocket->anti={summary['corr_pocket_anti_phase']:+.3f} "
            f"strong/weak delta={summary['strong_vs_weak_abs_delta_ratio']}",
            flush=True,
        )

    summaries = {str(h): summarize_horizon(rows_by_h[h]) for h in spec.horizons}
    return {
        "config": {
            "name": spec.name,
            "unit": spec.unit,
            "n": int(n),
            "home_period": float(spec.home_period),
            "base": float(spec.base),
            "rungs_k": spec.rungs_k,
            "horizons": spec.horizons,
            "min_train": spec.min_train,
            "anchor_stride": spec.anchor_stride,
            "origin_stride": spec.origin_stride,
            "test_start": label_for(spec.dates, test_start),
            "min_anchor": int(min_anchor),
        },
        "summary": summaries,
        "rows": rows_by_h,
    }


def run():
    started = time.time()
    print("ARA temporal-pocket diagnostic", flush=True)
    print("=" * 92, flush=True)
    print("Pocket marker: causal rolling k<0 in friction = B + k*abs(ARA-phi)", flush=True)
    print("Outcome checks: future surge, release boundary, anti-phase rung collision.", flush=True)

    datasets = {}
    for spec in [load_enso(), load_solar(), load_ecg_rr()]:
        datasets[spec.name] = run_dataset(spec)

    out = {
        "method": "temporal pocket diagnostic for negative k in B+k*abs(ARA-phi)",
        "leakage": "k is fit from completed windows s+h<t; future movement is scored only as outcome",
        "datasets": datasets,
        "elapsed_seconds": time.time() - started,
    }
    out_path = HERE / "ara_temporal_pocket_diagnostic_data.js"
    with out_path.open("w", encoding="utf-8") as f:
        f.write("window.ARA_TEMPORAL_POCKET_DIAGNOSTIC = ")
        json.dump(clean_for_json(out), f, indent=2)
        f.write(";\n")

    print("\nStrongest pocket signals", flush=True)
    print("-" * 92, flush=True)
    for name, result in datasets.items():
        print(name, flush=True)
        for h, summary in result["summary"].items():
            if summary.get("n", 0) == 0:
                continue
            print(
                f"  h={h:>4}: negK={summary['negative_k_share']:.2f} "
                f"corrAbs={summary['corr_pocket_abs_delta']:+.3f} "
                f"corrNext={summary['corr_pocket_next_h_delta']:+.3f} "
                f"corrAnti={summary['corr_pocket_anti_phase']:+.3f} "
                f"corrGear={summary['corr_pocket_gear_contact']:+.3f} "
                f"deltaQ4/Q1={summary['strong_vs_weak_abs_delta_ratio']}",
                flush=True,
            )

    print(f"\nWrote {out_path}", flush=True)
    print(f"Done in {time.time() - started:.1f}s", flush=True)


if __name__ == "__main__":
    run()
