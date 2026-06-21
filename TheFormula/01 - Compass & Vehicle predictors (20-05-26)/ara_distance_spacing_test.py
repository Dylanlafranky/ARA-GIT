"""
ara_distance_spacing_test.py — Dylan's "ARA distance is the ruler" hypothesis.

After the φ-base ablation on solar killed the strong form of "φ is the universal
predictor base," Dylan articulated a refinement (2026-05-10):

    Phi is the north star. Once the system is fully mapped onto φ-rungs (the
    substrate), use the system's measured mean ARA to set the OPERATING base
    of the OLD weight-decay formula. Different systems should get different
    operating bases derived from their ARAs.

This script tests that hypothesis on ENSO and solar sunspots.

Operational definition
----------------------
1. Substrate: rungs stay at φ^k periods (unchanged from canonical).
2. Operating base for the OLD weight-decay `w_k = base^(-|k - home_k|)`:
     Test two mappings of measured ARA → base.
       (A) ADD-ONE  :  base = 1 + ARA       (balance → 2.0, engine φ → φ²)
       (B) DIRECT   :  base = max(1.05, ARA) (literal ARA-as-base)
3. ARA measurement: rise/fall ratio averaged across cycles in the training
   window, exactly as `llm_ara_test.py:ara_full` defines it.

Compared against fixed-base predictors (φ, 2.0) from the prior ablation.

Honest note: this is a single architecture variant on two systems. A clean win
on one and a loss on the other would be informative but not definitive.
"""
import os, sys, json, math
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, REPO_ROOT)
from ara_framework import (
    Topology, causal_bandpass, _measure_rung, _predict_old,
)

PHI = (1 + 5**0.5) / 2


# ---------------- ARA measurement (rise/fall ratio per cycle) ----------------
def measure_mean_ara(arr, period, bw=0.85):
    """Mean ARA = mean(rise/fall) over detected cycles in bandpassed signal.
    1.0 = symmetric, >1 = engine (long rise, short fall), <1 = consumer."""
    from scipy.signal import butter, sosfilt
    arr = np.asarray(arr, dtype=float)
    n = len(arr)
    f_c = 1.0 / period
    nyq = 0.5
    Wn_lo = max(1e-6, (1 - bw) * f_c / nyq)
    Wn_hi = min(0.999, (1 + bw) * f_c / nyq)
    if Wn_lo >= Wn_hi:
        return None
    sos = butter(2, [Wn_lo, Wn_hi], btype='bandpass', output='sos')
    bp = sosfilt(sos, arr - np.mean(arr))
    if len(bp) < 3 * int(period):
        return None
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


# ---------------- Topology extraction (substrate = φ-rungs, fixed) ----------
def extract_topology_phi_substrate(data, t, rungs_k, home_k, pin_factor=4):
    arr = np.asarray(data, dtype=float)
    if t < 5 or t > len(arr): return None
    v_now = float(arr[t - 1])
    mean_train = float(np.mean(arr[:t]))
    rungs = []
    for k in rungs_k:
        period = PHI ** int(k)   # SUBSTRATE: always φ-spaced
        if period < 2 or pin_factor * period > t: continue
        bp = causal_bandpass(arr[:t], period)
        rec = _measure_rung(bp, period, k)
        if rec is not None: rungs.append(rec)
    return Topology(v_now=v_now, mean_train=mean_train, home_k=home_k, rungs=rungs)


# ---------------- OLD predictor with TUNABLE operating base ----------------
def predict_old_with_op_base(topo, h, op_base):
    """OLD regime, but the weight-decay base is the operating ARA-derived value,
       not necessarily φ. Substrate rung periods remain φ^k."""
    if topo is None or not topo.rungs:
        return float('nan') if topo is None else topo.mean_train
    if op_base <= 1.0:
        # flat weighting — all rungs contribute equally
        weights = np.ones(len(topo.rungs))
    else:
        weights = np.array([op_base ** (-abs(s['k'] - topo.home_k)) for s in topo.rungs])
    weights = weights / weights.sum()
    contrib = 0.0
    for j, s in enumerate(topo.rungs):
        new_th = s['theta'] + 2 * np.pi * h / s['period']
        contrib += weights[j] * s['amp'] * np.cos(new_th)
    return topo.mean_train + contrib


# ---------------- Per-system test runner ----------------
def run_system(system_name, data, home_period_data_units, horizons,
               n_anchors=60, test_window=None):
    """Run the ARA-distance test on one system.
       Returns dict: per-base scores at each horizon."""
    n = len(data)
    home_k = round(math.log(home_period_data_units) / math.log(PHI))
    k_lo = max(2, int(math.log(3.0) / math.log(PHI)))
    k_hi = int(math.log(min(720.0, n / 4.0)) / math.log(PHI)) + 1
    rungs_k = list(range(k_lo, k_hi + 1))

    # Anchor placement
    if test_window is None:
        test_window = min(30 * 12, n // 3)
    test_start = max(int(4 * home_period_data_units), n - test_window)
    anchor_idxs = np.linspace(test_start, n - max(horizons) - 1, n_anchors).astype(int)

    # Build per-anchor topologies, measure per-anchor ARA, run predictions.
    print(f"  measuring mean ARA at home_period={home_period_data_units}...")
    # ARA from full training data at each anchor — use the full window up to anchor.
    # We collect ARA values at all anchors then average — this is the system's
    # "operating ARA" averaged over the test span.
    aras_at_anchors = []
    for t in anchor_idxs:
        ara = measure_mean_ara(data[:t], home_period_data_units)
        if ara is not None:
            aras_at_anchors.append(ara)
    if not aras_at_anchors:
        print("  [WARN] could not measure ARA on this system.")
        return None
    mean_ara = float(np.mean(aras_at_anchors))
    std_ara = float(np.std(aras_at_anchors))
    print(f"  mean ARA at home rung: {mean_ara:.3f} (±{std_ara:.3f} across anchors)")

    # Derive operating bases from ARA
    op_bases = {
        'phi (substrate baseline)':   PHI,
        '2.0 (fixed baseline)':       2.0,
        'ARA_direct (max(1.05,ARA))': max(1.05, mean_ara),
        'ARA_plus_1 (1+ARA)':         1.0 + mean_ara,
    }
    print(f"  operating bases to test:")
    for name, b in op_bases.items():
        print(f"    {name:>32}  →  base = {b:.4f}")

    # Score each base across horizons
    out = {name: {h: {'preds': [], 'truths': []} for h in horizons} for name in op_bases}
    pers_preds = {h: {'preds': [], 'truths': []} for h in horizons}

    for t in anchor_idxs:
        topo = extract_topology_phi_substrate(data, t, rungs_k, home_k)
        if topo is None: continue
        for h in horizons:
            if t + h >= n: continue
            truth = float(data[t + h - 1])
            pers_preds[h]['preds'].append(float(data[t - 1]))
            pers_preds[h]['truths'].append(truth)
            for name, base in op_bases.items():
                p = predict_old_with_op_base(topo, h, base)
                if np.isfinite(p):
                    out[name][h]['preds'].append(p)
                    out[name][h]['truths'].append(truth)

    # Compute MAE etc.
    summary = {}
    for name in op_bases:
        per_h = {}
        for h in horizons:
            P = np.array(out[name][h]['preds'])
            T = np.array(out[name][h]['truths'])
            if len(P) < 5:
                per_h[h] = dict(n=int(len(P)))
                continue
            mae = float(np.mean(np.abs(P - T)))
            corr = float(np.corrcoef(P, T)[0, 1]) if T.std() > 0 and P.std() > 0 else float('nan')
            per_h[h] = dict(n=int(len(P)), mae=round(mae, 4), corr=round(corr, 4))
        summary[name] = dict(operating_base=round(op_bases[name], 4), scores=per_h)

    # Persistence baseline
    pers_summary = {}
    for h in horizons:
        P = np.array(pers_preds[h]['preds'])
        T = np.array(pers_preds[h]['truths'])
        if len(P) < 5:
            pers_summary[h] = dict(n=int(len(P)))
            continue
        mae = float(np.mean(np.abs(P - T)))
        pers_summary[h] = dict(n=int(len(P)), mae=round(mae, 4))

    return dict(
        system=system_name,
        home_period=home_period_data_units,
        home_k=int(home_k),
        rungs_k=rungs_k,
        n_anchors=int(n_anchors),
        mean_ara=round(mean_ara, 4),
        std_ara=round(std_ara, 4),
        bases=summary,
        persistence=pers_summary,
        horizons=horizons,
    )


def print_table(result):
    print(f"\n=== {result['system']} ===")
    print(f"  home_period = {result['home_period']}, home_k = {result['home_k']}")
    print(f"  mean ARA at home rung: {result['mean_ara']:.3f}")
    horizons = result['horizons']
    print(f"\n  MAE table:")
    print(f"  {'base':>32}  " + "  ".join(f"h={h:>5}" for h in horizons))
    print('-' * (35 + 9 * len(horizons)))
    for name, info in result['bases'].items():
        row = [f"{name:>32}"]
        for h in horizons:
            s = info['scores'].get(h, {})
            if 'mae' in s:
                row.append(f"  {s['mae']:>5.3f}")
            else:
                row.append(f"  {'-':>5}")
        print("".join(row))
    # Persistence
    row = [f"{'persistence':>32}"]
    for h in horizons:
        s = result['persistence'].get(h, {})
        if 'mae' in s:
            row.append(f"  {s['mae']:>5.3f}")
        else:
            row.append(f"  {'-':>5}")
    print("".join(row))

    # Per-horizon winner
    print(f"\n  Per-horizon winner:")
    print(f"  {'horizon':>8}  {'best base':>32}  {'best MAE':>9}  {'ARA-derived?':>14}")
    for h in horizons:
        by_base = []
        for name, info in result['bases'].items():
            s = info['scores'].get(h, {})
            if 'mae' in s:
                by_base.append((name, s['mae']))
        if not by_base: continue
        by_base.sort(key=lambda x: x[1])
        winner_name, winner_mae = by_base[0]
        ara_flag = 'YES' if 'ARA' in winner_name else 'no'
        print(f"  {h:>8}  {winner_name:>32}  {winner_mae:>9.4f}  {ara_flag:>14}")


# ---------------- ENSO ----------------
print("[1/3] ENSO ...")
nino_path = os.path.join(REPO_ROOT, 'Nino34', 'nino34.long.anom.csv')
df = pd.read_csv(nino_path, skiprows=1, names=['date', 'val'], header=None,
                 sep=',', engine='python')
NINO = pd.to_numeric(df['val'], errors='coerce').dropna().values.astype(float)
NINO = NINO[NINO > -50]
print(f"  loaded {len(NINO)} months")
enso_result = run_system('ENSO', NINO, home_period_data_units=47.0,
                         horizons=[1, 6, 12, 60, 120], n_anchors=60,
                         test_window=30 * 12)
print_table(enso_result)


# ---------------- Solar ----------------
print("\n[2/3] Solar SILSO ...")
silso_path = os.path.join(REPO_ROOT, 'SILSO_Solar', 'SN_m_tot_V2.0.csv')
df = pd.read_csv(silso_path, sep=';', header=None,
                 names=['year', 'month', 'decyear', 'val', 'std', 'n_obs', 'marker'])
SUN = pd.to_numeric(df['val'], errors='coerce').dropna().values.astype(float)
SUN = SUN[SUN >= 0]
print(f"  loaded {len(SUN)} months ({len(SUN)/12:.1f} years)")
solar_result = run_system('Solar SILSO', SUN, home_period_data_units=132.0,
                          horizons=[6, 12, 60, 132, 264], n_anchors=60,
                          test_window=100 * 12)
print_table(solar_result)


# ---------------- Save ----------------
OUT = os.path.join(_HERE, 'ara_distance_spacing_data.js')
with open(OUT, 'w') as f:
    f.write("window.ARA_DISTANCE_SPACING = " + json.dumps(dict(
        date='2026-05-10',
        regime='pure_OLD',
        substrate='φ-rungs (fixed)',
        bases_tested=['phi (substrate baseline)', '2.0 (fixed baseline)',
                       'ARA_direct (max(1.05,ARA))', 'ARA_plus_1 (1+ARA)'],
        results=dict(ENSO=enso_result, solar=solar_result),
    ), default=str) + ";\n")
print(f"\n[3/3] Saved -> {OUT}")
