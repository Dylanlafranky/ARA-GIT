#!/usr/bin/env python3
"""
map_heart.py — Map the heart to the framework as a sum of subsystems.

The heart isn't ONE oscillator at one ARA. It's several coupled rhythms — cardiac
cycle, HF (respiratory), LF (sympathovagal), VLF (slow autonomic) — each on a
different φ-rung. The formula stays the same; each subsystem is just one instance
of it at its own ARA / amp / period.

Total wave = data_centerline + Σ over subsystems of value_in_cycle(t, ARA_k, amp_k, period_k)

Strategy:
  1. Compute centerline = mean(R-R)
  2. Residuals = data − centerline (zero-mean signal)
  3. For each candidate φ-rung period k:
       grid-search ARA, amp, t_ref to find the best subsystem at that period
  4. Pick the strongest subsystems (highest correlation contribution)
  5. Sequentially subtract them from residuals
  6. Report each subsystem's framework parameters
  7. Reconstruct full wave; report fit quality
"""

import csv
import math
import os
import sys
import numpy as np

PHI = (1 + math.sqrt(5)) / 2
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
ECG_CSV = os.path.join(PROJECT_ROOT, "computations", "real_ecg_rr.csv")


# =====================================================================
# THE MINIMAL FORMULA (vectorized for speed)
# =====================================================================

def ara_to_T(ara, period):
    T_acc = period / (2 * (1 + ara))
    T_rel = ara * period / (2 * (1 + ara))
    return T_acc, T_rel


def polarity(ara):
    return max(0.0, 1 - abs(ara - 1) / (PHI - 1))


def value_at_times(t, ara, amp, period, t_ref=0.0):
    """Vectorized value_in_cycle: returns wave value at each t in the array."""
    a = max(0.05, ara)
    pol = polarity(ara)
    T_acc, T_rel = ara_to_T(a, period)
    out = np.zeros_like(t)
    eff = t - t_ref
    x = np.mod(eff, period)
    # Segment masks
    m1 = x < T_rel
    m2 = (x >= T_rel) & (x < T_rel + T_acc)
    m3 = (x >= T_rel + T_acc) & (x < 2 * T_rel + T_acc)
    m4 = x >= 2 * T_rel + T_acc
    # Segment 1: peak -> 0
    f1 = np.clip(x[m1] / T_rel, 0, 1)
    out[m1] = amp * (1 - np.power(f1, a))
    # Segment 2: 0 -> -peak
    f2 = np.clip((x[m2] - T_rel) / T_acc, 0, 1)
    out[m2] = -amp * pol * np.power(f2, 1.0 / a)
    # Segment 3: -peak -> 0
    f3 = np.clip((x[m3] - T_rel - T_acc) / T_rel, 0, 1)
    out[m3] = -amp * pol * (1 - np.power(f3, a))
    # Segment 4: 0 -> peak
    f4 = np.clip((x[m4] - 2 * T_rel - T_acc) / T_acc, 0, 1)
    out[m4] = amp * np.power(f4, 1.0 / a)
    return out


# =====================================================================
# DATA
# =====================================================================

def load_ecg():
    rows = []
    with open(ECG_CSV) as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append((float(r["time_s"]), float(r["rr_ms"])))
    rows.sort(key=lambda x: x[0])
    t = np.array([r[0] for r in rows])
    v = np.array([r[1] for r in rows])
    t = t - t[0]
    return t, v


# =====================================================================
# PER-SUBSYSTEM SEARCH — find best (ARA, amp, t_ref) at a given period
# =====================================================================

def search_subsystem(t, residuals, period,
                     ara_grid=None, tref_grid=None):
    """For a fixed period, search ARA and t_ref. Amp is solved in closed form.

    For each (ARA, t_ref) candidate:
      pred_unit = value_at_times(t, ara, amp=1, period, t_ref)
      optimal amp = (pred_unit · residuals) / (pred_unit · pred_unit)
    This is the linear-regression coefficient; minimizes ||amp·pred − residuals||².
    """
    if ara_grid is None:
        ara_grid = np.linspace(0.1, 2.0, 20)
    if tref_grid is None:
        tref_grid = np.linspace(0, period, 16, endpoint=False)

    best = {"corr": -2.0, "mae": 1e9}
    for ara in ara_grid:
        for t_ref in tref_grid:
            pred_unit = value_at_times(t, ara, 1.0, period, t_ref=t_ref)
            denom = float(np.sum(pred_unit * pred_unit))
            if denom < 1e-9:
                continue
            amp = float(np.sum(pred_unit * residuals) / denom)
            pred = amp * pred_unit
            if np.std(pred) < 1e-9:
                continue
            corr = float(np.corrcoef(pred, residuals)[0, 1])
            if not np.isfinite(corr):
                continue
            if corr > best["corr"]:
                mae = float(np.mean(np.abs(pred - residuals)))
                best = {"ara": float(ara), "amp": amp,
                        "period": float(period), "t_ref": float(t_ref),
                        "corr": corr, "mae": mae}
    return best


# =====================================================================
# MULTI-SUBSYSTEM MAPPING — sequentially fit subsystems on different φ-rungs
# =====================================================================

def map_subsystems(t, v, candidate_rungs=None, max_subsystems=4, verbose=True):
    """Find up to N subsystems on different φ-rungs that explain the data.

    Returns: list of subsystem dicts + the final reconstructed wave.
    """
    centerline = float(np.mean(v))
    residuals = v - centerline

    if candidate_rungs is None:
        # Cardiac-relevant scales: φ⁰=1s, φ¹=1.6s, φ²=2.6s (HF), φ³=4.2s, φ⁴=6.9s (LF),
        # φ⁵=11s, φ⁶=17.9s (VLF), φ⁷=29s, φ⁸=46.9s (lower VLF)
        candidate_rungs = [0, 1, 2, 3, 4, 5, 6, 7, 8]

    candidate_periods = [PHI**k for k in candidate_rungs]

    # First pass: rank each candidate period by best-fit correlation against residuals
    if verbose:
        print(f"\nScreening {len(candidate_periods)} candidate φ-rungs:")
        print(f"{'rung':>5} {'period(s)':>10} {'best ARA':>9} {'best amp':>9} {'corr':>7}")
    candidates = []
    for k, p in zip(candidate_rungs, candidate_periods):
        best = search_subsystem(t, residuals, p)
        candidates.append((k, p, best))
        if verbose:
            print(f"{k:>5} {p:>10.4f} {best['ara']:>9.3f} {best['amp']:>9.2f} {best['corr']:>+7.3f}")

    # Sort by absolute correlation (best fit first)
    candidates.sort(key=lambda x: abs(x[2]["corr"]), reverse=True)

    # Sequentially extract top subsystems
    subsystems = []
    current_residuals = residuals.copy()
    used_rungs = set()
    if verbose:
        print(f"\nSequentially extracting subsystems (max {max_subsystems}):")
    for k, p, _initial in candidates:
        if len(subsystems) >= max_subsystems:
            break
        # Don't use neighboring rungs (they share too much info)
        if any(abs(k - uk) < 1 for uk in used_rungs):
            continue
        # Re-fit to current residuals (after previous subtractions)
        best = search_subsystem(t, current_residuals, p)
        if abs(best["corr"]) < 0.10:
            continue  # too weak to count
        # Subtract this subsystem
        pred = value_at_times(t, best["ara"], best["amp"], p, t_ref=best["t_ref"])
        current_residuals = current_residuals - pred
        best["rung"] = k
        subsystems.append(best)
        used_rungs.add(k)
        if verbose:
            print(f"  Subsystem {len(subsystems)}: rung φ^{k} P={p:.3f}s "
                  f"ARA={best['ara']:.3f} amp={best['amp']:.2f} corr={best['corr']:+.3f}")

    # Joint re-fit: with all subsystems' shapes (ARA, period, t_ref) fixed,
    # solve simultaneously for all amplitudes + centerline via linear least squares.
    # This eliminates double-counting from sequential subtraction.
    if subsystems:
        N = len(subsystems)
        X = np.zeros((len(t), N + 1))
        X[:, 0] = 1.0  # constant column → centerline
        for i, s in enumerate(subsystems):
            X[:, i + 1] = value_at_times(t, s["ara"], 1.0, s["period"], t_ref=s["t_ref"])
        # Least squares: X @ coefs ≈ v
        coefs, *_ = np.linalg.lstsq(X, v, rcond=None)
        centerline = float(coefs[0])
        for i, s in enumerate(subsystems):
            s["amp"] = float(coefs[i + 1])
        if verbose:
            print(f"\nJoint LSQ refit: centerline={centerline:.2f}, amplitudes:")
            for i, s in enumerate(subsystems):
                print(f"  Subsystem {i+1} (rung φ^{s['rung']}): amp={s['amp']:.2f}")

    # Reconstruct full wave from centerline + all subsystems (with refitted amps)
    full_pred = np.full_like(v, centerline)
    for s in subsystems:
        full_pred += value_at_times(t, s["ara"], s["amp"], s["period"], t_ref=s["t_ref"])
    final_corr = float(np.corrcoef(full_pred, v)[0, 1]) if np.std(full_pred) > 0 else 0
    final_mae = float(np.mean(np.abs(full_pred - v)))

    return {
        "centerline": centerline,
        "subsystems": subsystems,
        "full_pred": full_pred,
        "corr": final_corr,
        "mae": final_mae,
    }


# =====================================================================
# MAIN
# =====================================================================

def main():
    print("=" * 78)
    print("map_heart.py — Mapping the heart as a sum of φ-rung subsystems")
    print("=" * 78)
    print()

    if not os.path.exists(ECG_CSV):
        print(f"ERROR: {ECG_CSV} not found.")
        sys.exit(1)

    t, v = load_ecg()
    print(f"Loaded {len(t)} R-R intervals from PhysioNet Subject 402")
    print(f"  Time span:    {t[-1]:.2f} sec")
    print(f"  R-R range:    {v.min():.1f} to {v.max():.1f} ms (range {v.max()-v.min():.1f})")
    print(f"  R-R mean:     {v.mean():.1f} ms")
    print(f"  R-R std:      {v.std():.1f} ms")
    print()

    result = map_subsystems(t, v, max_subsystems=4, verbose=True)

    print()
    print("=" * 78)
    print("THE HEART, MAPPED")
    print("=" * 78)
    print()
    print(f"Centerline (= mean R-R):  {result['centerline']:.2f} ms")
    print(f"  Equivalent to BPM:      {60000.0/result['centerline']:.1f} bpm")
    print()
    print(f"Subsystems found: {len(result['subsystems'])}")
    print()
    for i, s in enumerate(result['subsystems'], 1):
        # Classify HRV band
        f = 1.0 / s["period"]
        if f >= 0.15:
            band = "HF (respiratory)"
        elif f >= 0.04:
            band = "LF (sympathovagal)"
        elif f >= 0.0033:
            band = "VLF (slow autonomic)"
        else:
            band = "ULF"
        # ARA classification
        if abs(s["ara"] - 1) < 0.2:
            zone = "near clock"
        elif s["ara"] >= PHI - 0.1:
            zone = "engine zone"
        elif s["ara"] >= 1:
            zone = "warm engine"
        else:
            zone = "consumer zone"
        print(f"Subsystem {i}: rung φ^{s['rung']}  ({band})")
        print(f"  Period:      {s['period']:.3f} sec  ({f:.4f} Hz)")
        print(f"  ARA:         {s['ara']:.3f}  ({zone})")
        print(f"  Amplitude:   {s['amp']:.2f} ms (peak deviation from centerline)")
        print(f"  Phase t_ref: {s['t_ref']:+.3f} sec")
        print(f"  Polarity:    {polarity(s['ara']):.3f}")
        print(f"  Independent corr to data: {s['corr']:+.4f}")
        print()

    # Combined fit
    print(f"Combined wave fit (centerline + {len(result['subsystems'])} subsystems):")
    print(f"  Correlation to data:  {result['corr']:+.4f}")
    print(f"  MAE:                   {result['mae']:.3f} ms")
    print(f"  Baseline MAE (constant=mean): {float(np.mean(np.abs(v - v.mean()))):.3f} ms")
    print()

    # Variance explained
    total_variance = float(np.var(v))
    residual_variance = float(np.var(v - result['full_pred']))
    var_explained = 100 * (1 - residual_variance / total_variance)
    print(f"  Variance explained:    {var_explained:.1f}% of total R-R variance")
    print()

    # Save full reconstruction for visualization
    import json
    out_data = {
        "centerline": result["centerline"],
        "subsystems": result["subsystems"],
        "metrics": {"corr": result["corr"], "mae": result["mae"],
                    "var_explained": var_explained,
                    "bpm_equivalent": 60000.0 / result["centerline"]},
        "data_t": [float(x) for x in t],
        "data_v": [float(x) for x in v],
        "pred_v": [float(x) for x in result["full_pred"]],
    }
    out_path = os.path.join(HERE, "heart_map.json")
    with open(out_path, "w") as f:
        json.dump(out_data, f)
    print(f"Saved full mapping to {out_path}")


if __name__ == "__main__":
    main()
