"""
ara_enso_coupled_pocket_visibility_test.py

Test Dylan's coupled-ENSO explanation for the mixed temporal-pocket result:

    If ENSO is already a strongly coupled resonant pair in the measured rung,
    negative-k temporal pockets should be damped/hidden when NINO/SOI closure
    is high, and become more visible when the coupling is weak or transitioning.

The causal pocket marker is the rolling coefficient k from:

    temporal_friction = B + k * |ARA - phi|

Two variants are tested:
  - single_nino_k: k fit from NINO-only geometry
  - coupled_enso_k: k fit from full NINO/SOI/PDO geometry

At origin t and horizon h:
  - k is fit only from completed windows s+h<t
  - NINO/SOI coupling metrics use geometry at t only
  - future movement is scored only as the outcome
"""

from __future__ import annotations

import json
import math
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_ROOT))

from ara_geometry_state_transition_test import (
    build_snapshot_from_series,
    decode_state_features,
    natural_advance_decode_features,
    raw_series_dict,
)
from ara_geometry_transport_test import BASE, clean_for_json, load_enso_frame
from ara_phi_distance_bk_fit_test import (
    DatasetSpec,
    FRICTION_MAX,
    FRICTION_MIN,
    build_scale,
    decode_signal_features,
    fit_bk,
    friction_from_flow,
    label_for,
    natural_advance_state,
    phi_distance,
    read_signal_state,
    vectorize,
)
from ara_retroactive_flow_test import best_scalar_flow


HORIZONS = [1, 3, 6, 12, 24, 60]
RUNG_KS = [3, 4, 5, 6, 7]
HOME_PERIOD = 47.0
MIN_TRAIN = 96
ORIGIN_STRIDE = 3
START_YEAR = 2001


@dataclass(frozen=True)
class MarkerSpec:
    name: str
    k_key: str
    strength_key: str


MARKERS = [
    MarkerSpec("single_nino", "single_k", "single_pocket_strength"),
    MarkerSpec("coupled_enso", "coupled_k", "coupled_pocket_strength"),
]


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


def phase_alignment(a, b):
    return math.cos(2.0 * math.pi * phase_gap(a, b))


def corr(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    good = np.isfinite(x) & np.isfinite(y)
    x = x[good]
    y = y[good]
    if len(x) < 5 or float(np.std(x)) < 1e-12 or float(np.std(y)) < 1e-12:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


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


def mean(rows, key):
    vals = [finite(row.get(key, float("nan")), float("nan")) for row in rows]
    vals = [v for v in vals if math.isfinite(v)]
    return float(np.mean(vals)) if vals else None


def ratio(a, b):
    if a is None or b is None or abs(float(b)) < 1e-12:
        return None
    return float(a) / float(b)


def normalize(values):
    vals = np.asarray(values, dtype=float)
    good = np.isfinite(vals)
    if not np.any(good):
        return np.zeros_like(vals)
    lo = float(np.min(vals[good]))
    hi = float(np.max(vals[good]))
    if hi - lo < 1e-12:
        return np.zeros_like(vals)
    out = (vals - lo) / (hi - lo)
    out[~good] = 0.0
    return out


def make_enso_spec(frame):
    dates = frame.index.strftime("%Y-%m-%d").tolist()
    start_floor = int(np.searchsorted(frame.index.values.astype("datetime64[ns]"), np.datetime64(f"{START_YEAR}-01-01"))) + 1
    return DatasetSpec(
        name="ENSO_common_NINO34",
        unit="monthly NINO3.4 anomaly",
        dates=dates,
        values=frame["NINO"].values.astype(float),
        home_period=HOME_PERIOD,
        rungs_k=RUNG_KS,
        horizons=HORIZONS,
        min_train=MIN_TRAIN,
        anchor_stride=1,
        origin_stride=ORIGIN_STRIDE,
        start_index_floor=start_floor,
        base=BASE,
    )


def build_anchor_plan(spec):
    n = len(spec.values)
    max_h = max(spec.horizons)
    max_period = max(float(spec.base**k) for k in spec.rungs_k)
    min_anchor = max(int(math.ceil(4.0 * max_period)), int(4 * max(spec.rungs_k)), 48)
    test_start = max(spec.start_index_floor, min_anchor + spec.min_train + max_h + 1)
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


def same_rung_by_k(subsystem):
    return {int(rung["k"]): rung for rung in subsystem.get("rungs", [])}


def enso_coupling_features(snapshot):
    nino = snapshot["NINO"]
    soi = snapshot["SOI"]
    center_distance = abs(finite(nino["center_position"]) - finite(soi["center_position"]))
    center_proximity = BASE ** (-center_distance)
    center_alignment = phase_alignment(nino["center_phase"], soi["center_phase"])
    center_anti_phase = max(0.0, (1.0 - center_alignment) / 2.0)
    center_support = max(0.0, (1.0 + center_alignment) / 2.0)
    nrg = max(0.0, finite(nino["total_energy"]))
    srg = max(0.0, finite(soi["total_energy"]))
    energy_balance = 1.0 - abs(nrg - srg) / (nrg + srg + 1e-12)

    n_by_k = same_rung_by_k(nino)
    s_by_k = same_rung_by_k(soi)
    same_anti = 0.0
    same_support = 0.0
    same_contact = 0.0
    same_total = 0.0
    best_same_contact = 0.0
    weighted_gap = 0.0
    weighted_gap_den = 0.0

    for k in RUNG_KS:
        left = n_by_k.get(k)
        right = s_by_k.get(k)
        if left is None or right is None:
            continue
        occ = math.sqrt(max(0.0, finite(left["occupancy"])) * max(0.0, finite(right["occupancy"])))
        distance = abs(finite(left["position"]) - finite(right["position"]))
        proximity = BASE ** (-distance)
        weight = occ * proximity
        gap = phase_gap(left["phase"], right["phase"])
        alignment = math.cos(2.0 * math.pi * gap)
        anti = max(0.0, (1.0 - alignment) / 2.0)
        support = max(0.0, (1.0 + alignment) / 2.0)
        contact = math.exp(-((gap - 0.5) ** 2) / (2.0 * 0.08**2))
        same_anti += weight * anti
        same_support += weight * support
        same_contact += weight * contact
        same_total += weight
        best_same_contact = max(best_same_contact, weight * contact)
        weighted_gap += weight * abs(gap - 0.5)
        weighted_gap_den += weight

    same_anti_fraction = same_anti / (same_total + 1e-12)
    same_contact_fraction = same_contact / (same_total + 1e-12)
    coupling_completeness = (
        same_anti
        * (0.25 + 0.75 * center_anti_phase)
        * (0.25 + 0.75 * center_proximity)
        * (0.50 + 0.50 * energy_balance)
    )
    transition_contact = same_contact * (1.0 - energy_balance + abs(center_anti_phase - 0.5))

    return {
        "nino_soi_center_distance": center_distance,
        "nino_soi_center_proximity": center_proximity,
        "nino_soi_center_alignment": center_alignment,
        "nino_soi_center_anti_phase": center_anti_phase,
        "nino_soi_center_support": center_support,
        "nino_soi_energy_balance": energy_balance,
        "nino_soi_same_anti_phase_energy": same_anti,
        "nino_soi_same_support_energy": same_support,
        "nino_soi_same_contact_energy": same_contact,
        "nino_soi_same_total_energy": same_total,
        "nino_soi_same_anti_phase_fraction": same_anti_fraction,
        "nino_soi_same_contact_fraction": same_contact_fraction,
        "nino_soi_best_same_contact": best_same_contact,
        "nino_soi_weighted_anti_phase_gap": weighted_gap / weighted_gap_den if weighted_gap_den > 1e-12 else 0.5,
        "nino_soi_coupling_completeness": coupling_completeness,
        "nino_soi_transition_contact": transition_contact,
    }


def group_summary(rows, marker: MarkerSpec):
    if not rows:
        return {"n": 0}
    strength = marker.strength_key
    return {
        "n": int(len(rows)),
        "mean_k": mean(rows, marker.k_key),
        "mean_pocket_strength": mean(rows, strength),
        "mean_closure": mean(rows, "nino_soi_coupling_completeness"),
        "mean_abs_delta": mean(rows, "abs_delta"),
        "mean_abs_next_h_delta": mean(rows, "abs_next_h_delta"),
        "surge_rate": mean(rows, "is_surge"),
        "next_h_surge_rate": mean(rows, "is_next_h_surge"),
        "mean_anti_phase_energy": mean(rows, "nino_soi_same_anti_phase_energy"),
        "mean_contact_energy": mean(rows, "nino_soi_same_contact_energy"),
        "mean_energy_balance": mean(rows, "nino_soi_energy_balance"),
        "corr_pocket_abs_delta": corr([r[strength] for r in rows], [r["abs_delta"] for r in rows]),
        "corr_pocket_next_h_delta": corr([r[strength] for r in rows], [r["abs_next_h_delta"] for r in rows]),
        "corr_pocket_closure": corr([r[strength] for r in rows], [r["nino_soi_coupling_completeness"] for r in rows]),
        "corr_pocket_contact": corr([r[strength] for r in rows], [r["nino_soi_same_contact_energy"] for r in rows]),
    }


def strong_weak_ratio(rows, marker: MarkerSpec, outcome_key):
    if len(rows) < 8:
        return None
    vals = np.asarray([r[marker.strength_key] for r in rows], dtype=float)
    if float(np.std(vals)) < 1e-12:
        return None
    lo = float(np.percentile(vals, 25))
    hi = float(np.percentile(vals, 75))
    weak = [r for r in rows if r[marker.strength_key] <= lo]
    strong = [r for r in rows if r[marker.strength_key] >= hi]
    return ratio(mean(strong, outcome_key), mean(weak, outcome_key))


def summarize_marker(rows, marker: MarkerSpec):
    if not rows:
        return {"n": 0}
    closures = np.asarray([r["nino_soi_coupling_completeness"] for r in rows], dtype=float)
    lo_c = float(np.percentile(closures, 25))
    hi_c = float(np.percentile(closures, 75))
    low_closure = [r for r in rows if r["nino_soi_coupling_completeness"] <= lo_c]
    high_closure = [r for r in rows if r["nino_soi_coupling_completeness"] >= hi_c]
    mid_closure = [r for r in rows if lo_c < r["nino_soi_coupling_completeness"] < hi_c]

    strengths = np.asarray([r[marker.strength_key] for r in rows], dtype=float)
    closure_norm = normalize(closures)
    pocket_norm = normalize(strengths)
    low_visibility = pocket_norm * (1.0 - closure_norm)
    high_visibility = pocket_norm * closure_norm

    low_s = group_summary(low_closure, marker)
    high_s = group_summary(high_closure, marker)
    all_s = group_summary(rows, marker)
    return {
        "n": int(len(rows)),
        "negative_k_share": float(np.mean([r[marker.k_key] < 0.0 for r in rows])),
        "k": summarize_values([r[marker.k_key] for r in rows]),
        "pocket_strength": summarize_values([r[marker.strength_key] for r in rows]),
        "closure": summarize_values(closures),
        "all": all_s,
        "low_closure_q1": low_s,
        "mid_closure": group_summary(mid_closure, marker),
        "high_closure_q4": high_s,
        "strong_vs_weak_abs_delta_ratio_all": strong_weak_ratio(rows, marker, "abs_delta"),
        "strong_vs_weak_abs_delta_ratio_low_closure": strong_weak_ratio(low_closure, marker, "abs_delta"),
        "strong_vs_weak_abs_delta_ratio_high_closure": strong_weak_ratio(high_closure, marker, "abs_delta"),
        "strong_vs_weak_next_h_delta_ratio_low_closure": strong_weak_ratio(low_closure, marker, "abs_next_h_delta"),
        "strong_vs_weak_next_h_delta_ratio_high_closure": strong_weak_ratio(high_closure, marker, "abs_next_h_delta"),
        "low_over_high_closure_abs_delta": ratio(low_s.get("mean_abs_delta"), high_s.get("mean_abs_delta")),
        "low_over_high_closure_next_h_delta": ratio(low_s.get("mean_abs_next_h_delta"), high_s.get("mean_abs_next_h_delta")),
        "corr_low_visibility_abs_delta": corr(low_visibility, [r["abs_delta"] for r in rows]),
        "corr_high_visibility_abs_delta": corr(high_visibility, [r["abs_delta"] for r in rows]),
        "corr_low_visibility_next_h_delta": corr(low_visibility, [r["abs_next_h_delta"] for r in rows]),
        "corr_high_visibility_next_h_delta": corr(high_visibility, [r["abs_next_h_delta"] for r in rows]),
        "corr_closure_abs_delta": corr(closures, [r["abs_delta"] for r in rows]),
        "corr_closure_next_h_delta": corr(closures, [r["abs_next_h_delta"] for r in rows]),
    }


def run():
    started = time.time()
    frame = load_enso_frame()
    spec = make_enso_spec(frame)
    values = spec.values
    n = len(values)
    min_anchor, test_start, base_anchors, origins_by_h, needed_anchors = build_anchor_plan(spec)

    print("ENSO coupled-pocket visibility test", flush=True)
    print("=" * 96, flush=True)
    print("Hypothesis: high NINO/SOI closure hides/damps negative-k pockets; weak closure reveals surges.", flush=True)
    print(
        f"sample={spec.dates[0]}->{spec.dates[-1]} n={n} "
        f"min_anchor={min_anchor} test_start={label_for(spec.dates, test_start)} states={len(needed_anchors)}",
        flush=True,
    )

    series = raw_series_dict(frame)
    single_state_cache = {}
    triad_cache = {}
    t0 = time.time()
    for i, anchor in enumerate(needed_anchors, start=1):
        single_state_cache[anchor] = read_signal_state(values, anchor, spec)
        triad_cache[anchor] = build_snapshot_from_series(series, anchor)
        if i % 150 == 0:
            print(f"  states {i:4d}/{len(needed_anchors)} in {time.time() - t0:.1f}s", flush=True)
    print(f"  states {len(needed_anchors):4d}/{len(needed_anchors)} in {time.time() - t0:.1f}s", flush=True)

    single_decode = {a: decode_signal_features(single_state_cache[a], spec) for a in needed_anchors}
    single_keys = sorted(next(iter(single_decode.values())).keys())
    triad_decode = {a: decode_state_features(triad_cache[a]) for a in needed_anchors}
    triad_keys = sorted(next(iter(triad_decode.values())).keys())
    coupling_cache = {a: enso_coupling_features(triad_cache[a]) for a in needed_anchors}

    single_natural = {
        h: {a: decode_signal_features(natural_advance_state(single_state_cache[a], h), spec) for a in needed_anchors}
        for h in HORIZONS
    }
    triad_natural = {
        h: {a: natural_advance_decode_features(triad_cache[a], h) for a in needed_anchors}
        for h in HORIZONS
    }

    rows_by_h = {h: [] for h in HORIZONS}
    summary = {marker.name: {} for marker in MARKERS}

    for h in HORIZONS:
        for origin in origins_by_h.get(h, []):
            target_anchor = origin + h
            train_transition = [
                a for a in base_anchors
                if a + h < origin and a in single_decode and a + h in single_decode and a in triad_decode and a + h in triad_decode
            ]
            train_decoder = [a for a in base_anchors if a < origin and a in single_decode and a in triad_decode]
            if len(train_transition) < MIN_TRAIN or len(train_decoder) < MIN_TRAIN:
                continue

            single_scale = build_scale(single_decode, train_decoder, single_keys)
            triad_scale = build_scale(triad_decode, train_decoder, triad_keys)
            single_distances = []
            single_frictions = []
            coupled_distances = []
            coupled_frictions = []
            train_abs_delta = []
            for s in train_transition:
                sc = vectorize(single_decode[s], single_keys, single_scale)
                sn = vectorize(single_natural[h][s], single_keys, single_scale)
                sf = vectorize(single_decode[s + h], single_keys, single_scale)
                single_alpha = best_scalar_flow(sc, sn - sc, sf)
                single_ara = single_state_cache[s]["center_ara"]
                single_distances.append(phi_distance(single_ara))
                single_frictions.append(clip(friction_from_flow(single_ara, single_alpha), FRICTION_MIN, FRICTION_MAX))

                tc = vectorize(triad_decode[s], triad_keys, triad_scale)
                tn = vectorize(triad_natural[h][s], triad_keys, triad_scale)
                tf = vectorize(triad_decode[s + h], triad_keys, triad_scale)
                coupled_alpha = best_scalar_flow(tc, tn - tc, tf)
                coupled_ara = triad_cache[s]["NINO"]["center_ara"]
                coupled_distances.append(phi_distance(coupled_ara))
                coupled_frictions.append(clip(friction_from_flow(coupled_ara, coupled_alpha), FRICTION_MIN, FRICTION_MAX))
                train_abs_delta.append(abs(float(values[s + h - 1] - values[s - 1])))

            single_B, single_k = fit_bk(single_distances, single_frictions)
            coupled_B, coupled_k = fit_bk(coupled_distances, coupled_frictions)

            actual = float(values[target_anchor - 1])
            current = float(values[origin - 1])
            delta = actual - current
            if target_anchor + h <= n:
                next_h_delta = float(values[target_anchor + h - 1] - actual)
                abs_next_h_delta = abs(next_h_delta)
            else:
                next_h_delta = None
                abs_next_h_delta = float("nan")
            threshold = float(np.percentile(train_abs_delta, 75)) if train_abs_delta else float("nan")

            row = {
                "origin": label_for(spec.dates, origin),
                "date": label_for(spec.dates, target_anchor),
                "horizon": int(h),
                "current": current,
                "actual": actual,
                "delta": float(delta),
                "abs_delta": abs(float(delta)),
                "next_h_delta": next_h_delta,
                "abs_next_h_delta": abs_next_h_delta,
                "surge_threshold": threshold,
                "is_surge": 1.0 if math.isfinite(threshold) and abs(float(delta)) >= threshold else 0.0,
                "is_next_h_surge": 1.0
                if math.isfinite(threshold) and math.isfinite(abs_next_h_delta) and abs_next_h_delta >= threshold
                else 0.0,
                "single_B": float(single_B),
                "single_k": float(single_k),
                "single_pocket_strength": max(0.0, -float(single_k)),
                "coupled_B": float(coupled_B),
                "coupled_k": float(coupled_k),
                "coupled_pocket_strength": max(0.0, -float(coupled_k)),
                "single_center_ara": float(single_state_cache[origin]["center_ara"]),
                "coupled_nino_center_ara": float(triad_cache[origin]["NINO"]["center_ara"]),
                **coupling_cache[origin],
            }
            rows_by_h[h].append(row)

        print(f"h={h:>2} months", flush=True)
        for marker in MARKERS:
            sm = summarize_marker(rows_by_h[h], marker)
            summary[marker.name][str(h)] = sm
            print(
                f"  {marker.name:13s} negK={sm.get('negative_k_share', 0.0):.2f} "
                f"lowVis->abs={sm.get('corr_low_visibility_abs_delta', 0.0):+.3f} "
                f"highVis->abs={sm.get('corr_high_visibility_abs_delta', 0.0):+.3f} "
                f"low/high abs={sm.get('low_over_high_closure_abs_delta')}",
                flush=True,
            )

    out = {
        "method": "ENSO negative-k pocket visibility split by NINO/SOI coupling closure",
        "leakage": "k fit uses only completed windows s+h<t; coupling metrics use origin t only; future movement is outcome only",
        "config": {
            "sample_start": spec.dates[0],
            "sample_end": spec.dates[-1],
            "n": int(n),
            "home_period": HOME_PERIOD,
            "rungs_k": RUNG_KS,
            "horizons": HORIZONS,
            "min_train": MIN_TRAIN,
            "origin_stride": ORIGIN_STRIDE,
            "test_start": label_for(spec.dates, test_start),
            "min_anchor": int(min_anchor),
        },
        "summary": summary,
        "rows": rows_by_h,
    }
    out_path = HERE / "ara_enso_coupled_pocket_visibility_data.js"
    with out_path.open("w", encoding="utf-8") as f:
        f.write("window.ARA_ENSO_COUPLED_POCKET_VISIBILITY = ")
        json.dump(clean_for_json(out), f, indent=2)
        f.write(";\n")

    print("\nVisibility summary", flush=True)
    print("-" * 96, flush=True)
    for marker in MARKERS:
        print(marker.name, flush=True)
        for h in HORIZONS:
            sm = summary[marker.name][str(h)]
            print(
                f"  h={h:>2}: negK={sm.get('negative_k_share', 0.0):.2f} "
                f"lowVisAbs={sm.get('corr_low_visibility_abs_delta', 0.0):+.3f} "
                f"highVisAbs={sm.get('corr_high_visibility_abs_delta', 0.0):+.3f} "
                f"lowRatio={sm.get('strong_vs_weak_abs_delta_ratio_low_closure')} "
                f"highRatio={sm.get('strong_vs_weak_abs_delta_ratio_high_closure')} "
                f"low/high={sm.get('low_over_high_closure_abs_delta')}",
                flush=True,
            )

    print(f"\nWrote {out_path}", flush=True)
    print(f"Done in {time.time() - started:.1f}s", flush=True)


if __name__ == "__main__":
    run()
