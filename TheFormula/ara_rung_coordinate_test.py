"""
ara_rung_coordinate_test.py

Dylan's "ARA rungs" hypothesis, 2026-05-20.

Question:
    What if the ladder is not only phi-spaced? What if a system's measured ARA
    is itself the spacing between subsystem rungs, and the ARA measured within
    each rung is the local coordinate inside that scale step?

Coordinate tested:
    subsystem_position = k + ARA_k / 2

where:
    k       = scale rung index under the tested substrate base
    ARA_k   = measured rise/fall ratio at that rung, from training data only
    /2      = ARA's natural 0..2 span, mapping one ARA-range to one rung interval

Distance between two subsystem rungs:
    distance = abs((k_a + ARA_a/2) - (k_b + ARA_b/2))

This tests whether across-rung coupling is better described by a scale+ARA
coordinate than by plain integer rung distance.

Configurations:
    1. phi substrate + phi k-distance decay       baseline
    2. phi substrate + 2.0 k-distance decay       prior OLD winner/control
    3. phi substrate + ARA-coordinate distance
    4. 2.0 substrate + 2.0 k-distance decay
    5. 2.0 substrate + ARA-coordinate distance    Dylan's requested 2.0 test
    6. system-ARA substrate + ARA-coordinate distance
    7. 1+system-ARA substrate + ARA-coordinate distance

This is an exploratory OLD-regime test on ENSO and solar. It is strict-causal
with respect to the scored target values: each topology reads only data[:t].
"""

import csv
import json
import math
import os
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent


PHI = (1.0 + 5.0**0.5) / 2.0
MIN_VALID_BASE = 1.10
MAX_RUNGS = 90


@dataclass
class Topology:
    v_now: float
    mean_train: float
    home_k: int
    rungs: list = field(default_factory=list)


def find_workspace_root():
    candidates = [HERE, REPO_ROOT, Path.cwd(), *Path.cwd().parents, *HERE.parents]
    for candidate in candidates:
        if (candidate / "Nino34" / "nino34.long.anom.csv").exists():
            return candidate
    raise FileNotFoundError("Could not find workspace root containing Nino34 data.")


WORKSPACE_ROOT = find_workspace_root()


def load_enso():
    path = WORKSPACE_ROOT / "Nino34" / "nino34.long.anom.csv"
    vals = []
    with path.open("r", encoding="utf-8") as f:
        next(f, None)
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            try:
                val = float(row[1])
            except ValueError:
                continue
            if val > -50:
                vals.append(val)
    return np.asarray(vals, dtype=float)


def load_solar():
    path = WORKSPACE_ROOT / "SILSO_Solar" / "SN_m_tot_V2.0.csv"
    vals = []
    with path.open("r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        for row in reader:
            if len(row) < 4:
                continue
            try:
                val = float(row[3])
            except ValueError:
                continue
            if val >= 0:
                vals.append(val)
    return np.asarray(vals, dtype=float)


def ema(arr, span):
    """One-sided exponential moving average."""
    arr = np.asarray(arr, dtype=float)
    if len(arr) == 0:
        return arr
    alpha = 2.0 / (max(1.0, float(span)) + 1.0)
    out = np.empty_like(arr)
    out[0] = arr[0]
    for i in range(1, len(arr)):
        out[i] = alpha * arr[i] + (1.0 - alpha) * out[i - 1]
    return out


def causal_bandpass(arr, period, bandwidth=0.65):
    """Simple one-sided EMA bandpass. Rougher than Butterworth, dependency-light."""
    arr = np.asarray(arr, dtype=float)
    if len(arr) < 3:
        return np.zeros_like(arr)
    centered = arr - np.mean(arr)
    fast_span = max(2.0, period * (1.0 - bandwidth))
    slow_span = max(fast_span + 1.0, period * (1.0 + bandwidth))
    return ema(centered, fast_span) - ema(centered, slow_span)


def find_peaks_simple(series, distance):
    """Local maxima with a minimum spacing rule."""
    x = np.asarray(series, dtype=float)
    if len(x) < 3:
        return np.asarray([], dtype=int)
    candidates = []
    for i in range(1, len(x) - 1):
        if x[i] > x[i - 1] and x[i] >= x[i + 1]:
            if candidates and i - candidates[-1] < distance:
                if x[i] > x[candidates[-1]]:
                    candidates[-1] = i
            else:
                candidates.append(i)
    return np.asarray(candidates, dtype=int)


def measure_rung(bp, period, k):
    """Read amplitude and phase from the most recent approximate bandpass cycle."""
    p_int = max(2, int(period))
    if len(bp) < 2 * p_int + 5:
        return None
    last_cycle = bp[-p_int:]
    amp = float((np.max(last_cycle) - np.min(last_cycle)) / 2.0)
    if amp < 1e-9:
        return None
    v_recent = float(bp[-1])
    v_prev = float(bp[-2])
    ratio = max(-0.99, min(0.99, v_recent / max(amp, 1e-9)))
    theta = float(np.arccos(ratio) * (-1.0 if (v_recent - v_prev) > 0 else 1.0))
    return {"k": int(k), "period": float(period), "amp": amp, "theta": theta}


def safe_base(value):
    """A logarithmic rung base must be > 1. Clamp direct ARA if needed."""
    if not np.isfinite(value):
        return MIN_VALID_BASE
    return max(MIN_VALID_BASE, float(value))


def make_rungs(base, n_samples):
    max_period = min(720.0, n_samples / 4.0)
    k_lo = max(1, int(math.floor(math.log(3.0) / math.log(base))))
    k_hi = int(math.ceil(math.log(max_period) / math.log(base)))
    rungs = list(range(k_lo, k_hi + 1))
    if len(rungs) <= MAX_RUNGS:
        return rungs
    # Keep a uniform sample of rung indices when direct ARA creates dense spacing.
    idx = np.linspace(0, len(rungs) - 1, MAX_RUNGS).round().astype(int)
    return sorted({rungs[i] for i in idx})


def measure_rung_ara(arr_up_to_t, period, bw=0.85):
    """Rise/fall ARA at one period, using only the training window."""
    arr = np.asarray(arr_up_to_t, dtype=float)
    if len(arr) < 3 * int(period):
        return None
    smoothed = causal_bandpass(arr, period, bandwidth=bw)
    smoothed = ema(smoothed, max(2, int(period * 0.05)))
    peaks = find_peaks_simple(smoothed, distance=max(2, int(period * 0.7)))
    if len(peaks) < 2:
        return None
    aras = []
    for i in range(len(peaks) - 1):
        seg = smoothed[peaks[i] : peaks[i + 1] + 1]
        if len(seg) < 3:
            continue
        trough_fraction = int(np.argmin(seg)) / max(1, len(seg) - 1)
        trough_fraction = max(0.15, min(0.85, trough_fraction))
        aras.append((1.0 - trough_fraction) / trough_fraction)
    if not aras:
        return None
    return float(np.mean(np.clip(aras, 0.3, 3.0)))


def extract_topology_with_aras(data, t, rung_base, rungs_k, home_k, pin_factor=4):
    arr = np.asarray(data, dtype=float)
    if t < 5 or t > len(arr):
        return None
    mean_train = float(np.mean(arr[:t]))
    rungs = []
    for k in rungs_k:
        period = rung_base ** int(k)
        if period < 2 or pin_factor * period > t:
            continue
        bp = causal_bandpass(arr[:t], period)
        rec = measure_rung(bp, period, k)
        if rec is None:
            continue
        ara = measure_rung_ara(arr[:t], period)
        if ara is not None:
            rec["ara"] = float(ara)
        rungs.append(rec)
    return Topology(
        v_now=float(arr[t - 1]),
        mean_train=mean_train,
        home_k=int(home_k),
        rungs=rungs,
    )


def mean_home_ara(data, home_period, anchors):
    values = []
    for t in anchors:
        ara = measure_rung_ara(data[:t], home_period)
        if ara is not None and np.isfinite(ara):
            values.append(ara)
    if not values:
        return 1.0, 0.0, 0
    return float(np.mean(values)), float(np.std(values)), len(values)


def predict_k_distance(topo, h, decay_base):
    if topo is None or not topo.rungs:
        return float("nan")
    weights = np.array([decay_base ** (-abs(s["k"] - topo.home_k)) for s in topo.rungs])
    if weights.sum() <= 0:
        return float("nan")
    weights = weights / weights.sum()
    contrib = 0.0
    for j, s in enumerate(topo.rungs):
        contrib += weights[j] * s["amp"] * np.cos(s["theta"] + 2.0 * np.pi * h / s["period"])
    return topo.mean_train + contrib


def predict_ara_coordinate(topo, h, decay_base=2.0, fallback_home_ara=1.0):
    if topo is None or not topo.rungs:
        return float("nan")
    ara_by_k = {s["k"]: s.get("ara") for s in topo.rungs if s.get("ara") is not None}
    home_ara = ara_by_k.get(topo.home_k, fallback_home_ara)
    home_coord = topo.home_k + home_ara / 2.0
    distances = []
    for s in topo.rungs:
        ara = s.get("ara", home_ara)
        coord = s["k"] + ara / 2.0
        distances.append(abs(coord - home_coord))
    weights = np.array([decay_base ** (-d) for d in distances])
    if weights.sum() <= 0:
        return float("nan")
    weights = weights / weights.sum()
    contrib = 0.0
    for j, s in enumerate(topo.rungs):
        contrib += weights[j] * s["amp"] * np.cos(s["theta"] + 2.0 * np.pi * h / s["period"])
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

    system_ara, system_ara_std, system_ara_n = mean_home_ara(data, home_period, anchors)
    direct_base = safe_base(system_ara)
    plus_one_base = safe_base(1.0 + system_ara)

    configs = [
        {
            "name": "phi substrate + phi k-distance",
            "rung_base": PHI,
            "mode": "k",
            "decay_base": PHI,
        },
        {
            "name": "phi substrate + 2 k-distance",
            "rung_base": PHI,
            "mode": "k",
            "decay_base": 2.0,
        },
        {
            "name": "phi substrate + ARA-coordinate",
            "rung_base": PHI,
            "mode": "coord",
            "decay_base": 2.0,
        },
        {
            "name": "2 substrate + 2 k-distance",
            "rung_base": 2.0,
            "mode": "k",
            "decay_base": 2.0,
        },
        {
            "name": "2 substrate + ARA-coordinate",
            "rung_base": 2.0,
            "mode": "coord",
            "decay_base": 2.0,
        },
        {
            "name": "system-ARA substrate + ARA-coordinate",
            "rung_base": direct_base,
            "mode": "coord",
            "decay_base": 2.0,
        },
        {
            "name": "1+system-ARA substrate + ARA-coordinate",
            "rung_base": plus_one_base,
            "mode": "coord",
            "decay_base": 2.0,
        },
    ]

    for cfg in configs:
        cfg["home_k"] = int(round(math.log(home_period) / math.log(cfg["rung_base"])))
        cfg["rungs_k"] = make_rungs(cfg["rung_base"], n)

    records = {cfg["name"]: {h: [] for h in horizons} for cfg in configs}
    persistence = {h: [] for h in horizons}
    ara_samples = {cfg["name"]: {} for cfg in configs}

    for t in anchors:
        topo_by_config = {}
        for cfg in configs:
            topo = extract_topology_with_aras(data, t, cfg["rung_base"], cfg["rungs_k"], cfg["home_k"])
            topo_by_config[cfg["name"]] = topo
            if topo is not None:
                for s in topo.rungs:
                    if "ara" in s:
                        ara_samples[cfg["name"]].setdefault(int(s["k"]), []).append(float(s["ara"]))

        for h in horizons:
            if t + h - 1 >= n:
                continue
            truth = float(data[t + h - 1])
            persistence[h].append((float(data[t - 1]), truth))
            for cfg in configs:
                topo = topo_by_config[cfg["name"]]
                if cfg["mode"] == "k":
                    pred = predict_k_distance(topo, h, cfg["decay_base"])
                else:
                    pred = predict_ara_coordinate(
                        topo,
                        h,
                        decay_base=cfg["decay_base"],
                        fallback_home_ara=system_ara,
                    )
                if np.isfinite(pred):
                    records[cfg["name"]][h].append((float(pred), truth))

    scores = {cfg["name"]: {h: score_records(records[cfg["name"]][h]) for h in horizons} for cfg in configs}
    scores["persistence"] = {h: score_records(persistence[h]) for h in horizons}

    distribution = {}
    for cfg in configs:
        rows = {}
        for k, vals in ara_samples[cfg["name"]].items():
            rows[k] = {
                "n": len(vals),
                "mean": float(np.mean(vals)),
                "std": float(np.std(vals)),
            }
        distribution[cfg["name"]] = rows

    return {
        "system": name,
        "n_samples": int(n),
        "home_period": float(home_period),
        "horizons": horizons,
        "n_anchors": int(len(anchors)),
        "system_ara_at_home_period": {
            "mean": system_ara,
            "std": system_ara_std,
            "n": system_ara_n,
            "direct_base_used": direct_base,
            "plus_one_base_used": plus_one_base,
        },
        "configs": [
            {
                "name": cfg["name"],
                "rung_base": cfg["rung_base"],
                "home_k": cfg["home_k"],
                "n_rungs": len(cfg["rungs_k"]),
                "mode": cfg["mode"],
                "decay_base": cfg["decay_base"],
            }
            for cfg in configs
        ],
        "scores": scores,
        "rung_ara_distribution": distribution,
    }


def print_table(result):
    horizons = result["horizons"]
    print(f"\n=== {result['system']} ===")
    home = result["system_ara_at_home_period"]
    print(
        "  home_period={:.1f}, home ARA={:.3f} +/- {:.3f} (n={}), direct_base={:.3f}, plus_one_base={:.3f}".format(
            result["home_period"],
            home["mean"],
            home["std"],
            home["n"],
            home["direct_base_used"],
            home["plus_one_base_used"],
        )
    )
    print("\n  MAE by configuration:")
    print("  {:44s}".format("configuration") + "".join(f"  h={h:>5}" for h in horizons))
    print("  " + "-" * (44 + 9 * len(horizons)))
    for name, by_h in result["scores"].items():
        row = f"  {name:44s}"
        for h in horizons:
            score = by_h[h]
            row += f"  {score['mae']:>7.3f}" if "mae" in score else f"  {'-':>7}"
        print(row)

    print("\n  Winners excluding persistence:")
    for h in horizons:
        candidates = []
        for name, by_h in result["scores"].items():
            if name == "persistence":
                continue
            score = by_h[h]
            if "mae" in score:
                candidates.append((score["mae"], name))
        candidates.sort()
        if candidates:
            print(f"    h={h:>5}: {candidates[0][1]}  MAE={candidates[0][0]:.3f}")


def main():
    print("Loading data from", WORKSPACE_ROOT)
    enso = load_enso()
    solar = load_solar()
    print(f"  ENSO months: {len(enso)}")
    print(f"  Solar months: {len(solar)}")

    enso_result = run_system(
        "ENSO",
        enso,
        home_period=47.0,
        horizons=[1, 6, 12, 60, 120],
        n_anchors=45,
        test_window=30 * 12,
    )
    print_table(enso_result)

    solar_result = run_system(
        "Solar SILSO",
        solar,
        home_period=132.0,
        horizons=[6, 12, 60, 132, 264],
        n_anchors=45,
        test_window=100 * 12,
    )
    print_table(solar_result)

    output = {
        "date": "2026-05-20",
        "hypothesis": "ARA rungs: scale coordinate plus within-rung ARA coordinate",
        "coordinate": "position = k + ARA_k / 2; distance = abs(position_k - position_home)",
        "workspace_root": str(WORKSPACE_ROOT),
        "results": {"enso": enso_result, "solar": solar_result},
    }
    out_path = HERE / "ara_rung_coordinate_data.js"
    with out_path.open("w", encoding="utf-8") as f:
        f.write("window.ARA_RUNG_COORDINATE = ")
        json.dump(output, f, indent=2)
        f.write(";\n")
    print(f"\nSaved -> {out_path}")


if __name__ == "__main__":
    main()
