"""
ara_shape_kernel_test.py

Strict-causal test of an ARA-shaped accumulate/release kernel.

Question:
  Is a learned accumulate/release cycle shape better than a cosine once ARA
  tells us how much of the cycle is release vs accumulation?

Protocol:
  - At each anchor t, learn shape kernels from data[:t] only.
  - Learn two median half-cycle shapes:
      release:    peak -> trough
      accumulate: trough -> next peak
  - Measure each rung's ARA from data[:t] only.
  - Infer the rung's current phase from the observed bandpass value and slope.
  - Predict by advancing phase by h / period and reading the learned shape.

This is not path tracing. The prediction uses a reusable shape kernel plus
current topology coordinates; scored future values are never read by the model.
"""

import json
import math
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent

sys.path.insert(0, str(REPO_ROOT))
from ara_framework import Topology, _measure_rung, causal_bandpass

PHI = (1 + 5**0.5) / 2
GRID_N = 101
GRID = np.linspace(0.0, 1.0, GRID_N)
FALLBACK_RELEASE = np.cos(np.pi * GRID)
FALLBACK_ACCUMULATE = -np.cos(np.pi * GRID)


def find_workspace_root():
    candidates = [HERE, REPO_ROOT, Path.cwd(), *Path.cwd().parents, *HERE.parents]
    for candidate in candidates:
        if (candidate / "Nino34" / "nino34.long.anom.csv").exists():
            return candidate
    raise FileNotFoundError("Could not find workspace root containing Nino34 data.")


WORKSPACE_ROOT = find_workspace_root()


def load_enso():
    nino = pd.read_csv(
        WORKSPACE_ROOT / "Nino34" / "nino34.long.anom.csv",
        skiprows=1,
        names=["d", "v"],
        header=None,
        sep=",",
        engine="python",
    )
    vals = pd.to_numeric(nino["v"], errors="coerce").dropna().values.astype(float)
    return vals[vals > -50]


def load_solar():
    silso = pd.read_csv(
        WORKSPACE_ROOT / "SILSO_Solar" / "SN_m_tot_V2.0.csv",
        sep=";",
        header=None,
        names=["y", "m", "dy", "v", "s", "n", "mk"],
    )
    vals = pd.to_numeric(silso["v"], errors="coerce").dropna().values.astype(float)
    return vals[vals >= 0]


def fallback_kernel():
    return {
        "release": FALLBACK_RELEASE.copy(),
        "accumulate": FALLBACK_ACCUMULATE.copy(),
        "n_cycles": 0,
        "fallback": True,
    }


def interp_segment(values):
    values = np.asarray(values, dtype=float)
    if len(values) < 2:
        return None
    src = np.linspace(0.0, 1.0, len(values))
    return np.interp(GRID, src, values)


def kernel_from_bandpass(bp, period, max_cycles=48):
    bp = np.asarray(bp, dtype=float)
    if len(bp) < max(16, int(3 * period)):
        return fallback_kernel()

    smoothed = gaussian_filter1d(bp, max(1, int(period * 0.05)))
    peaks, _ = find_peaks(smoothed, distance=max(2, int(period * 0.55)))
    if len(peaks) < 3:
        return fallback_kernel()

    releases = []
    accumulates = []
    recent_peaks = peaks[-(max_cycles + 1) :]
    for p0, p1 in zip(recent_peaks[:-1], recent_peaks[1:]):
        if p1 <= p0 + 4:
            continue
        span = p1 - p0
        if span < 0.35 * period or span > 2.25 * period:
            continue

        seg = smoothed[p0 : p1 + 1]
        trough = int(np.argmin(seg))
        if trough < 2 or trough > len(seg) - 3:
            continue

        peak_level = float((seg[0] + seg[-1]) / 2.0)
        trough_level = float(seg[trough])
        amp = (peak_level - trough_level) / 2.0
        if amp <= 1e-9:
            continue
        center = (peak_level + trough_level) / 2.0
        norm = np.clip((seg - center) / amp, -1.25, 1.25)

        rel = interp_segment(norm[: trough + 1])
        acc = interp_segment(norm[trough:])
        if rel is not None and acc is not None:
            releases.append(rel)
            accumulates.append(acc)

    if len(releases) < 3 or len(accumulates) < 3:
        return fallback_kernel()

    release = gaussian_filter1d(np.median(np.vstack(releases), axis=0), 1.0)
    accumulate = gaussian_filter1d(np.median(np.vstack(accumulates), axis=0), 1.0)
    release[0], release[-1] = 1.0, -1.0
    accumulate[0], accumulate[-1] = -1.0, 1.0
    return {
        "release": np.clip(release, -1.2, 1.2),
        "accumulate": np.clip(accumulate, -1.2, 1.2),
        "n_cycles": int(len(releases)),
        "fallback": False,
    }


def measure_rung_ara_from_bp(bp, period):
    kernel = kernel_from_bandpass(bp, period)
    if kernel["fallback"]:
        return None

    smoothed = gaussian_filter1d(np.asarray(bp, dtype=float), max(1, int(period * 0.05)))
    peaks, _ = find_peaks(smoothed, distance=max(2, int(period * 0.55)))
    if len(peaks) < 2:
        return None

    aras = []
    for p0, p1 in zip(peaks[:-1], peaks[1:]):
        seg = smoothed[p0 : p1 + 1]
        if len(seg) < 5:
            continue
        trough_fraction = int(np.argmin(seg)) / max(1, len(seg) - 1)
        trough_fraction = max(0.15, min(0.85, trough_fraction))
        aras.append((1.0 - trough_fraction) / trough_fraction)
    if not aras:
        return None
    return float(np.mean(np.clip(aras, 0.3, 3.0)))


def release_fraction(ara):
    ara = float(np.clip(ara if np.isfinite(ara) else 1.0, 0.3, 3.0))
    return 1.0 / (1.0 + ara)


def infer_phase_from_shape(bp, amp, ara, kernel):
    if len(bp) < 2 or amp <= 1e-9:
        return 0.0
    v = float(np.clip(bp[-1] / amp, -1.0, 1.0))
    falling = float(bp[-1] - bp[-2]) < 0.0
    split = release_fraction(ara)
    if falling:
        idx = int(np.argmin(np.abs(kernel["release"] - v)))
        return split * (idx / max(1, GRID_N - 1))
    idx = int(np.argmin(np.abs(kernel["accumulate"] - v)))
    return split + (1.0 - split) * (idx / max(1, GRID_N - 1))


def shape_value_at_phase(phase, ara, kernel):
    phase = float(phase % 1.0)
    split = release_fraction(ara)
    if phase < split:
        u = 0.0 if split <= 1e-9 else phase / split
        return float(np.interp(u, GRID, kernel["release"]))
    denom = max(1e-9, 1.0 - split)
    u = (phase - split) / denom
    return float(np.interp(u, GRID, kernel["accumulate"]))


def safe_base(x):
    if not np.isfinite(x):
        return 1.05
    return max(1.05, float(x))


def rung_range(base, n, max_rungs=90):
    k_lo = max(2, int(math.log(3.0) / math.log(base)))
    k_hi = int(math.log(min(720.0, n / 4.0)) / math.log(base)) + 1
    rungs = list(range(k_lo, k_hi + 1))
    if len(rungs) <= max_rungs:
        return rungs
    idx = np.linspace(0, len(rungs) - 1, max_rungs).round().astype(int)
    return sorted({rungs[i] for i in idx})


def estimate_system_ara(data, home_period, anchors):
    vals = []
    for t in anchors:
        bp = causal_bandpass(data[:t], home_period)
        ara = measure_rung_ara_from_bp(bp, home_period)
        if ara is not None and np.isfinite(ara):
            vals.append(float(ara))
    if not vals:
        return 1.0, 0.0
    return float(np.mean(vals)), float(np.std(vals))


def extract_topology(data, t, rungs_k, home_k, rung_base, home_kernel, home_ara, pin_factor=4):
    arr = np.asarray(data, dtype=float)
    if t < 5 or t > len(arr):
        return None
    rungs = []
    for k in rungs_k:
        period = rung_base ** int(k)
        if period < 2 or pin_factor * period > t:
            continue
        bp = causal_bandpass(arr[:t], period)
        rec = _measure_rung(bp, period, k)
        if rec is None:
            continue

        ara = measure_rung_ara_from_bp(bp, period)
        if ara is None or not np.isfinite(ara):
            ara = home_ara
        local_kernel = kernel_from_bandpass(bp, period)
        rec["ara"] = float(ara)
        rec["phase_home"] = infer_phase_from_shape(bp, rec["amp"], ara, home_kernel)
        rec["phase_rung"] = infer_phase_from_shape(bp, rec["amp"], ara, local_kernel)
        rec["kernel_rung"] = local_kernel
        rungs.append(rec)

    return Topology(
        v_now=float(arr[t - 1]),
        mean_train=float(np.mean(arr[:t])),
        home_k=int(home_k),
        rungs=rungs,
    )


def coord_weights(topo, decay_base=2.0):
    ara_at = {s["k"]: s.get("ara") for s in topo.rungs if s.get("ara") is not None}
    home_ara = ara_at.get(topo.home_k)
    if home_ara is None:
        home_ara = float(np.mean(list(ara_at.values()))) if ara_at else 1.0
    home_pos = topo.home_k + home_ara / 2.0
    distances = []
    for s in topo.rungs:
        ara_k = s.get("ara", home_ara)
        distances.append(abs((s["k"] + ara_k / 2.0) - home_pos))
    weights = np.array([decay_base ** (-d) for d in distances], dtype=float)
    if weights.sum() <= 0:
        return None
    return weights / weights.sum()


def k_weights(topo, decay_base):
    weights = np.array([decay_base ** (-abs(s["k"] - topo.home_k)) for s in topo.rungs], dtype=float)
    if weights.sum() <= 0:
        return None
    return weights / weights.sum()


def predict_cosine(topo, h, weight_mode, decay_base):
    if topo is None or not topo.rungs:
        return float("nan")
    weights = coord_weights(topo, decay_base) if weight_mode == "coord" else k_weights(topo, decay_base)
    if weights is None:
        return float("nan")
    contrib = 0.0
    for j, s in enumerate(topo.rungs):
        contrib += weights[j] * s["amp"] * np.cos(s["theta"] + 2.0 * np.pi * h / s["period"])
    return topo.mean_train + contrib


def predict_shape(topo, h, weight_mode, decay_base, home_kernel, phase_mode):
    if topo is None or not topo.rungs:
        return float("nan")
    weights = coord_weights(topo, decay_base) if weight_mode == "coord" else k_weights(topo, decay_base)
    if weights is None:
        return float("nan")
    contrib = 0.0
    for j, s in enumerate(topo.rungs):
        if phase_mode == "home":
            kernel = home_kernel
            phase = s["phase_home"]
        else:
            kernel = s["kernel_rung"]
            phase = s["phase_rung"]
        future_phase = phase + h / s["period"]
        contrib += weights[j] * s["amp"] * shape_value_at_phase(future_phase, s["ara"], kernel)
    return topo.mean_train + contrib


def score_records(records):
    preds = np.array([r[0] for r in records], dtype=float)
    truths = np.array([r[1] for r in records], dtype=float)
    if len(preds) < 5:
        return {"n": int(len(preds))}
    corr = float(np.corrcoef(preds, truths)[0, 1]) if preds.std() > 1e-9 and truths.std() > 1e-9 else float("nan")
    return {
        "n": int(len(preds)),
        "mae": float(np.mean(np.abs(preds - truths))),
        "corr": corr,
    }


def run_system(name, data, home_period, horizons, n_anchors=45, test_window=None):
    n = len(data)
    if test_window is None:
        test_window = min(30 * 12, n // 3)
    test_start = max(int(4 * home_period), n - test_window)
    anchors = np.linspace(test_start, n - max(horizons) - 1, n_anchors).astype(int)

    sys_ara, sys_ara_std = estimate_system_ara(data, home_period, anchors)
    sys_base = safe_base(sys_ara)
    sys_base_plus = safe_base(1.0 + sys_ara)

    configs = [
        ("phi + phi-k cosine", PHI, "k", PHI, "cos", "home"),
        ("phi + coord cosine", PHI, "coord", 2.0, "cos", "home"),
        ("phi + coord shape-home", PHI, "coord", 2.0, "shape", "home"),
        ("phi + coord shape-rung", PHI, "coord", 2.0, "shape", "rung"),
        ("2 + coord cosine", 2.0, "coord", 2.0, "cos", "home"),
        ("2 + coord shape-home", 2.0, "coord", 2.0, "shape", "home"),
        ("2 + coord shape-rung", 2.0, "coord", 2.0, "shape", "rung"),
        ("sysARA + coord shape-home", sys_base, "coord", 2.0, "shape", "home"),
        ("sysARA + coord shape-rung", sys_base, "coord", 2.0, "shape", "rung"),
        ("1+sysARA + coord shape-rung", sys_base_plus, "coord", 2.0, "shape", "rung"),
    ]

    config_records = []
    for label, base, weight_mode, decay_base, predictor, phase_mode in configs:
        config_records.append(
            {
                "label": label,
                "rung_base": base,
                "weight_mode": weight_mode,
                "decay_base": decay_base,
                "predictor": predictor,
                "phase_mode": phase_mode,
                "home_k": round(math.log(home_period) / math.log(base)),
                "rungs_k": rung_range(base, n),
            }
        )

    results = {c["label"]: {h: [] for h in horizons} for c in config_records}
    persistence = {h: [] for h in horizons}
    final_home_kernel = fallback_kernel()

    for t in anchors:
        home_bp = causal_bandpass(data[:t], home_period)
        home_kernel = kernel_from_bandpass(home_bp, home_period)
        final_home_kernel = home_kernel
        home_ara = measure_rung_ara_from_bp(home_bp, home_period)
        if home_ara is None or not np.isfinite(home_ara):
            home_ara = sys_ara

        topo_cache = {}
        for c in config_records:
            key = (round(c["rung_base"], 10), c["home_k"], tuple(c["rungs_k"]))
            if key not in topo_cache:
                topo_cache[key] = extract_topology(
                    data,
                    t,
                    c["rungs_k"],
                    c["home_k"],
                    c["rung_base"],
                    home_kernel,
                    home_ara,
                )
            topo = topo_cache[key]
            for h in horizons:
                if t + h >= n:
                    continue
                if c["predictor"] == "cos":
                    pred = predict_cosine(topo, h, c["weight_mode"], c["decay_base"])
                else:
                    pred = predict_shape(topo, h, c["weight_mode"], c["decay_base"], home_kernel, c["phase_mode"])
                if np.isfinite(pred):
                    results[c["label"]][h].append((pred, float(data[t + h - 1])))

        for h in horizons:
            if t + h < n:
                persistence[h].append((float(data[t - 1]), float(data[t + h - 1])))

    summary = {
        label: {h: score_records(records) for h, records in per_h.items()}
        for label, per_h in results.items()
    }
    pers_summary = {h: score_records(records) for h, records in persistence.items()}

    print(f"\n=== {name} ===")
    print(
        f"  home_period={home_period:.1f}, sys_ara={sys_ara:.3f} +/- {sys_ara_std:.3f}, "
        f"sys_base={sys_base:.3f}, 1+sys_base={sys_base_plus:.3f}, "
        f"final_shape_cycles={final_home_kernel['n_cycles']}"
    )
    print(f"  {'config':31s} " + " ".join(f"h={h:>5}" for h in horizons))
    for label in summary:
        row = [f"{label:31s}"]
        for h in horizons:
            s = summary[label][h]
            row.append(f" {s['mae']:>7.3f}" if "mae" in s else "       -")
        print("".join(row))
    row = [f"{'persistence':31s}"]
    for h in horizons:
        s = pers_summary[h]
        row.append(f" {s['mae']:>7.3f}" if "mae" in s else "       -")
    print("".join(row))

    print("\n  Winners excluding persistence:")
    for h in horizons:
        cands = []
        for label in summary:
            if "mae" in summary[label][h]:
                cands.append((summary[label][h]["mae"], label))
        cands.sort(key=lambda x: x[0])
        if cands:
            print(f"    h={h:>5}: {cands[0][1]}  MAE={cands[0][0]:.3f}")

    return {
        "system": name,
        "home_period": home_period,
        "sys_ara": sys_ara,
        "sys_ara_std": sys_ara_std,
        "sys_base": sys_base,
        "sys_base_plus": sys_base_plus,
        "horizons": horizons,
        "scores": summary,
        "persistence": pers_summary,
        "final_home_kernel": {
            "n_cycles": final_home_kernel["n_cycles"],
            "fallback": final_home_kernel["fallback"],
            "grid": GRID.tolist(),
            "release": final_home_kernel["release"].tolist(),
            "accumulate": final_home_kernel["accumulate"].tolist(),
        },
    }


def main():
    print("Loading ENSO and solar datasets from workspace root...")
    nino = load_enso()
    sun = load_solar()

    enso_res = run_system("ENSO", nino, 47.0, [1, 6, 12, 60, 120], n_anchors=45, test_window=30 * 12)
    solar_res = run_system("Solar SILSO", sun, 132.0, [6, 12, 60, 132, 264], n_anchors=45, test_window=100 * 12)

    out = HERE / "ara_shape_kernel_data.js"
    with out.open("w", encoding="utf-8") as f:
        f.write(
            "window.ARA_SHAPE_KERNEL = "
            + json.dumps(
                {
                    "date": "2026-05-21",
                    "method": "strict-causal ARA accumulate/release shape kernel test",
                    "shape": "median release and accumulate half-cycle kernels learned from data[:t]",
                    "coordinate": "k + ARA_k/2 with 2^(-distance) decay for coord configs",
                    "enso": enso_res,
                    "solar": solar_res,
                },
                default=str,
            )
            + ";\n"
        )
    print(f"\nSaved -> {out}")


if __name__ == "__main__":
    main()
