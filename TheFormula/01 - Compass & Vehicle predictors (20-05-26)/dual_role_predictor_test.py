"""
dual_role_predictor_test.py — Dylan's two-bases-two-jobs hypothesis.

After the ARA-distance-spacing test gave mixed results, Dylan refined the
architecture (2026-05-10):

    φ does Job 1: structure-finding. Rungs at φ^k periods.
    The ARA scale (0-2) does Job 2: how far apart subsystems sit operationally.

    The OLD formula was using `base^(-|k - home_k|)` to weight contributions —
    a k-DIFFERENCE penalty. The right version uses ARA-DIFFERENCE between rungs:

        weight_k = exp(-α × |ARA_k - ARA_home|)

    where ARA_k is each rung's own measured ARA (bandpass at that period,
    measure rise/fall ratio).

Settled-liquids picture: the ladder is a stratified column of densities. Each
rung sits at a meniscus between layers. Distance between layers (in density =
in ARA) sets how much leak occurs when energy moves between them.

This script tests the architecture on ENSO and solar, sweeps α, and inspects
the per-rung ARA distribution.
"""
import os, sys, json, math
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfilt, find_peaks
from scipy.ndimage import gaussian_filter1d

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, REPO_ROOT)
from ara_framework import (
    Topology, causal_bandpass, _measure_rung,
)

PHI = (1 + 5**0.5) / 2
LN_PHI = math.log(PHI)
LN_TWO = math.log(2.0)


# ---------------- Per-rung ARA measurement ----------------
def measure_rung_ara(arr_up_to_t, period, bw=0.85):
    """ARA at one rung: rise/fall ratio averaged across detected cycles
    in bandpassed signal at this period. 1.0 = symmetric, >1 = engine, <1 = consumer."""
    arr = np.asarray(arr_up_to_t, dtype=float)
    n = len(arr)
    if n < 3 * int(period):
        return None
    f_c = 1.0 / period
    nyq = 0.5
    Wn_lo = max(1e-6, (1 - bw) * f_c / nyq)
    Wn_hi = min(0.999, (1 + bw) * f_c / nyq)
    if Wn_lo >= Wn_hi:
        return None
    sos = butter(2, [Wn_lo, Wn_hi], btype='bandpass', output='sos')
    bp = sosfilt(sos, arr - np.mean(arr))
    smoothed = gaussian_filter1d(bp, max(1, int(period * 0.05)))
    peaks, _ = find_peaks(smoothed, distance=max(2, int(period * 0.7)))
    if len(peaks) < 2:
        return None
    aras = []
    for i in range(len(peaks) - 1):
        seg = smoothed[peaks[i]:peaks[i + 1] + 1]
        if len(seg) < 3:
            continue
        f_t = max(0.15, min(0.85, int(np.argmin(seg)) / max(1, len(seg) - 1)))
        aras.append((1 - f_t) / f_t)
    if not aras:
        return None
    return float(np.mean(np.clip(aras, 0.3, 3.0)))


# ---------------- Topology with per-rung ARA ----------------
def extract_topology_with_aras(data, t, rungs_k, home_k, pin_factor=4):
    """Substrate: φ-spaced rungs. Each rung also gets its own measured ARA."""
    arr = np.asarray(data, dtype=float)
    if t < 5 or t > len(arr): return None, None
    v_now = float(arr[t - 1])
    mean_train = float(np.mean(arr[:t]))
    rungs = []
    rung_aras = {}
    for k in rungs_k:
        period = PHI ** int(k)
        if period < 2 or pin_factor * period > t: continue
        bp = causal_bandpass(arr[:t], period)
        rec = _measure_rung(bp, period, k)
        if rec is None: continue
        # Now measure ARA at this rung
        ara = measure_rung_ara(arr[:t], period)
        if ara is not None:
            rec['ara'] = float(ara)
            rung_aras[int(k)] = float(ara)
        rungs.append(rec)
    topo = Topology(v_now=v_now, mean_train=mean_train, home_k=home_k, rungs=rungs)
    return topo, rung_aras


# ---------------- Dual-role predictor ----------------
def predict_dual_role(topo, h, alpha):
    """OLD regime, weights by ARA-DIFFERENCE not k-difference.
       weight_k = exp(-alpha × |ARA_k - ARA_home|)"""
    if topo is None or not topo.rungs:
        return float('nan') if topo is None else topo.mean_train
    # Find ARA at home rung (or nearest available)
    ara_at_rung = {s['k']: s.get('ara') for s in topo.rungs}
    ara_home = ara_at_rung.get(topo.home_k)
    if ara_home is None:
        # fall back to mean of available ARAs
        avail = [a for a in ara_at_rung.values() if a is not None]
        if not avail:
            return topo.mean_train
        ara_home = float(np.mean(avail))
    # Compute weights using ARA-distance
    weights = []
    for s in topo.rungs:
        a = s.get('ara')
        if a is None:
            # ungrudgingly assign mean weight (no info)
            weights.append(math.exp(-alpha * 1.0))  # neutral middle-ish
        else:
            weights.append(math.exp(-alpha * abs(a - ara_home)))
    weights = np.array(weights)
    if weights.sum() <= 0:
        return topo.mean_train
    weights = weights / weights.sum()
    contrib = 0.0
    for j, s in enumerate(topo.rungs):
        new_th = s['theta'] + 2 * np.pi * h / s['period']
        contrib += weights[j] * s['amp'] * np.cos(new_th)
    return topo.mean_train + contrib


def predict_old_fixed_base(topo, h, base):
    """OLD regime with fixed-base k-difference weighting (baseline for comparison)."""
    if topo is None or not topo.rungs:
        return float('nan') if topo is None else topo.mean_train
    weights = np.array([base ** (-abs(s['k'] - topo.home_k)) for s in topo.rungs])
    weights = weights / weights.sum()
    contrib = 0.0
    for j, s in enumerate(topo.rungs):
        new_th = s['theta'] + 2 * np.pi * h / s['period']
        contrib += weights[j] * s['amp'] * np.cos(new_th)
    return topo.mean_train + contrib


# ---------------- Per-system runner ----------------
def run_system(system_name, data, home_period_data_units, horizons,
               alphas=(0.25, 0.5, 1.0, 2.0, 4.0), n_anchors=60, test_window=None):
    n = len(data)
    home_k = round(math.log(home_period_data_units) / math.log(PHI))
    k_lo = max(2, int(math.log(3.0) / math.log(PHI)))
    k_hi = int(math.log(min(720.0, n / 4.0)) / math.log(PHI)) + 1
    rungs_k = list(range(k_lo, k_hi + 1))

    if test_window is None:
        test_window = min(30 * 12, n // 3)
    test_start = max(int(4 * home_period_data_units), n - test_window)
    anchor_idxs = np.linspace(test_start, n - max(horizons) - 1, n_anchors).astype(int)

    # Storage
    out_dual = {a: {h: {'preds': [], 'truths': []} for h in horizons} for a in alphas}
    out_phi = {h: {'preds': [], 'truths': []} for h in horizons}
    out_two = {h: {'preds': [], 'truths': []} for h in horizons}
    pers = {h: {'preds': [], 'truths': []} for h in horizons}

    # Per-rung ARA distribution across anchors
    rung_ara_samples = {k: [] for k in rungs_k}

    for t in anchor_idxs:
        topo, rung_aras = extract_topology_with_aras(data, t, rungs_k, home_k)
        if topo is None: continue
        for k, ara in (rung_aras or {}).items():
            rung_ara_samples[k].append(ara)
        for h in horizons:
            if t + h >= n: continue
            truth = float(data[t + h - 1])
            # Predictions
            for a in alphas:
                p = predict_dual_role(topo, h, a)
                if np.isfinite(p):
                    out_dual[a][h]['preds'].append(p)
                    out_dual[a][h]['truths'].append(truth)
            p_phi = predict_old_fixed_base(topo, h, PHI)
            p_two = predict_old_fixed_base(topo, h, 2.0)
            if np.isfinite(p_phi):
                out_phi[h]['preds'].append(p_phi)
                out_phi[h]['truths'].append(truth)
            if np.isfinite(p_two):
                out_two[h]['preds'].append(p_two)
                out_two[h]['truths'].append(truth)
            pers[h]['preds'].append(float(data[t - 1]))
            pers[h]['truths'].append(truth)

    # Summarise
    def _mae(d):
        P = np.array(d['preds']); T = np.array(d['truths'])
        if len(P) < 5: return None
        return float(np.mean(np.abs(P - T)))

    summary = {}
    for a in alphas:
        summary[f'dual α={a}'] = {h: _mae(out_dual[a][h]) for h in horizons}
    summary['fixed φ (baseline)'] = {h: _mae(out_phi[h]) for h in horizons}
    summary['fixed 2.0 (baseline)'] = {h: _mae(out_two[h]) for h in horizons}
    summary['persistence'] = {h: _mae(pers[h]) for h in horizons}

    rung_ara_dist = {k: dict(n=len(v),
                             mean=float(np.mean(v)) if v else None,
                             std=float(np.std(v)) if v else None)
                     for k, v in rung_ara_samples.items()}

    return dict(
        system=system_name,
        home_period=home_period_data_units,
        home_k=int(home_k),
        rungs_k=rungs_k,
        horizons=horizons,
        alphas=list(alphas),
        scores=summary,
        rung_ara_distribution=rung_ara_dist,
    )


def print_result(result):
    print(f"\n=== {result['system']} ===")
    print(f"  home_period = {result['home_period']}, home_k = {result['home_k']}")

    # Per-rung ARA distribution
    print(f"\n  Per-rung ARA distribution (anchored over test span):")
    print(f"  {'k':>3}  {'period':>10}  {'n':>4}  {'mean ARA':>9}  {'σ':>6}  {'note':<20}")
    home_k = result['home_k']
    for k, info in sorted(result['rung_ara_distribution'].items()):
        if info['n'] == 0:
            continue
        period = PHI ** k
        marker = '← home' if k == home_k else ''
        mean = info.get('mean')
        std = info.get('std')
        mean_str = f"{mean:>9.3f}" if mean is not None else f"{'—':>9}"
        std_str = f"{std:>6.3f}" if std is not None else f"{'—':>6}"
        print(f"  {k:>3}  {period:>10.2f}  {info['n']:>4}  {mean_str}  {std_str}  {marker}")

    # MAE table
    print(f"\n  MAE table:")
    horizons = result['horizons']
    print(f"  {'model':>22}  " + "  ".join(f"h={h:>5}" for h in horizons))
    print('-' * (25 + 9 * len(horizons)))
    for name, h_dict in result['scores'].items():
        row = [f"{name:>22}"]
        for h in horizons:
            v = h_dict.get(h)
            row.append(f"  {v:>5.3f}" if v is not None else f"  {'-':>5}")
        print("".join(row))

    # Per-horizon winner
    print(f"\n  Per-horizon winner (excluding persistence):")
    print(f"  {'horizon':>8}  {'best model':>22}  {'best MAE':>9}  {'dual?':>6}")
    for h in horizons:
        cands = []
        for name, h_dict in result['scores'].items():
            if name == 'persistence': continue
            v = h_dict.get(h)
            if v is not None:
                cands.append((name, v))
        if not cands: continue
        cands.sort(key=lambda x: x[1])
        winner_name, winner_mae = cands[0]
        dual = 'YES' if winner_name.startswith('dual') else 'no'
        print(f"  {h:>8}  {winner_name:>22}  {winner_mae:>9.4f}  {dual:>6}")


# ---------------- ENSO ----------------
print("[1/3] ENSO ...")
nino_path = os.path.join(REPO_ROOT, 'Nino34', 'nino34.long.anom.csv')
df = pd.read_csv(nino_path, skiprows=1, names=['date', 'val'], header=None,
                 sep=',', engine='python')
NINO = pd.to_numeric(df['val'], errors='coerce').dropna().values.astype(float)
NINO = NINO[NINO > -50]
print(f"  loaded {len(NINO)} months")
enso_result = run_system('ENSO', NINO, home_period_data_units=47.0,
                         horizons=[1, 6, 12, 60, 120],
                         alphas=(0.25, 0.5, 1.0, 2.0, 4.0),
                         n_anchors=60, test_window=30 * 12)
print_result(enso_result)


# ---------------- Solar ----------------
print("\n[2/3] Solar SILSO ...")
silso_path = os.path.join(REPO_ROOT, 'SILSO_Solar', 'SN_m_tot_V2.0.csv')
df = pd.read_csv(silso_path, sep=';', header=None,
                 names=['year', 'month', 'decyear', 'val', 'std', 'n_obs', 'marker'])
SUN = pd.to_numeric(df['val'], errors='coerce').dropna().values.astype(float)
SUN = SUN[SUN >= 0]
print(f"  loaded {len(SUN)} months ({len(SUN)/12:.1f} years)")
solar_result = run_system('Solar SILSO', SUN, home_period_data_units=132.0,
                          horizons=[6, 12, 60, 132, 264],
                          alphas=(0.25, 0.5, 1.0, 2.0, 4.0),
                          n_anchors=60, test_window=100 * 12)
print_result(solar_result)


# ---------------- Save ----------------
OUT = os.path.join(_HERE, 'dual_role_predictor_data.js')
with open(OUT, 'w') as f:
    f.write("window.DUAL_ROLE_PREDICTOR = " + json.dumps(dict(
        date='2026-05-10',
        substrate='φ-rungs (fixed)',
        weighting='exp(-α × |ARA_k - ARA_home|) — per-rung ARA, ARA-distance',
        baselines=['fixed φ k-decay', 'fixed 2.0 k-decay', 'persistence'],
        results=dict(ENSO=enso_result, solar=solar_result),
    ), default=str) + ";\n")
print(f"\n[3/3] Saved -> {OUT}")
