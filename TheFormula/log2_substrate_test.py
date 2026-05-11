"""
log2_substrate_test.py — does swapping the substrate from φ-spaced to 2-spaced
help, hurt, or do nothing?

Context (2026-05-11):
  - φ does Job 1: structure — where on the time axis subsystems live (φ^k rungs).
  - 2 does Job 2: operating distance — how far apart subsystems sit in ARA terms.
  - Dual-role predictor (φ-substrate + per-rung ARA-distance weighting) beats fixed
    base 2.0 on solar.

Open question: if 2 is structurally meaningful (the ceiling, the mirror-partner
distance, the matched-pair count), maybe 2-spaced rungs in TIME also work?

This script tests three configurations on ENSO and solar:

  A. φ substrate + φ k-decay weight       (original canonical)
  B. φ substrate + 2 k-decay weight       (what wins under OLD ablation)
  C. φ substrate + per-rung ARA-distance  (dual-role winner)
  D. 2 substrate + 2 k-decay weight       (pure octave predictor)
  E. 2 substrate + per-rung ARA-distance  (NEW — what Dylan asked for)

Framework prediction: D and E should be no better than C, because φ is the right
TIME-spacing constant. If E *beats* C, that's a real surprise and the framework
needs to revisit which job φ is actually doing.
"""
import os, sys, json, math
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfilt, find_peaks
from scipy.ndimage import gaussian_filter1d

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, REPO_ROOT)
from ara_framework import causal_bandpass, _measure_rung, Topology

PHI = (1 + 5**0.5) / 2


# ---------------- Per-rung ARA measurement (same as dual-role test) ----------------
def measure_rung_ara(arr_up_to_t, period, bw=0.85):
    arr = np.asarray(arr_up_to_t, dtype=float)
    n = len(arr)
    if n < 3 * int(period): return None
    f_c = 1.0 / period
    nyq = 0.5
    Wn_lo = max(1e-6, (1 - bw) * f_c / nyq)
    Wn_hi = min(0.999, (1 + bw) * f_c / nyq)
    if Wn_lo >= Wn_hi: return None
    sos = butter(2, [Wn_lo, Wn_hi], btype='bandpass', output='sos')
    bp = sosfilt(sos, arr - np.mean(arr))
    smoothed = gaussian_filter1d(bp, max(1, int(period * 0.05)))
    peaks, _ = find_peaks(smoothed, distance=max(2, int(period * 0.7)))
    if len(peaks) < 2: return None
    aras = []
    for i in range(len(peaks) - 1):
        seg = smoothed[peaks[i]:peaks[i + 1] + 1]
        if len(seg) < 3: continue
        f_t = max(0.15, min(0.85, int(np.argmin(seg)) / max(1, len(seg) - 1)))
        aras.append((1 - f_t) / f_t)
    if not aras: return None
    return float(np.mean(np.clip(aras, 0.3, 3.0)))


def extract_topology(data, t, rungs_k, home_k, rung_base, pin_factor=4):
    """Topology with rungs at rung_base^k (NOT necessarily φ)."""
    arr = np.asarray(data, dtype=float)
    if t < 5 or t > len(arr): return None, None
    v_now = float(arr[t - 1])
    mean_train = float(np.mean(arr[:t]))
    rungs = []
    rung_aras = {}
    for k in rungs_k:
        period = rung_base ** int(k)
        if period < 2 or pin_factor * period > t: continue
        bp = causal_bandpass(arr[:t], period)
        rec = _measure_rung(bp, period, k)
        if rec is None: continue
        ara = measure_rung_ara(arr[:t], period)
        if ara is not None:
            rec['ara'] = float(ara)
            rung_aras[int(k)] = float(ara)
        rungs.append(rec)
    topo = Topology(v_now=v_now, mean_train=mean_train, home_k=home_k, rungs=rungs)
    return topo, rung_aras


def predict_old_kdiff(topo, h, weight_base):
    """OLD with weight_k = weight_base^(-|k-home_k|)."""
    if topo is None or not topo.rungs: return float('nan')
    weights = np.array([weight_base ** (-abs(s['k'] - topo.home_k)) for s in topo.rungs])
    weights /= weights.sum()
    contrib = 0.0
    for j, s in enumerate(topo.rungs):
        contrib += weights[j] * s['amp'] * np.cos(s['theta'] + 2*np.pi*h/s['period'])
    return topo.mean_train + contrib


def predict_old_ara_distance(topo, h, alpha):
    """OLD with weight_k = exp(-alpha × |ARA_k - ARA_home|)."""
    if topo is None or not topo.rungs: return float('nan')
    ara_at = {s['k']: s.get('ara') for s in topo.rungs}
    ara_home = ara_at.get(topo.home_k)
    if ara_home is None:
        avail = [a for a in ara_at.values() if a is not None]
        if not avail: return topo.mean_train
        ara_home = float(np.mean(avail))
    weights = []
    for s in topo.rungs:
        a = s.get('ara')
        weights.append(math.exp(-alpha * abs((a if a is not None else ara_home) - ara_home)))
    weights = np.array(weights)
    if weights.sum() <= 0: return topo.mean_train
    weights /= weights.sum()
    contrib = 0.0
    for j, s in enumerate(topo.rungs):
        contrib += weights[j] * s['amp'] * np.cos(s['theta'] + 2*np.pi*h/s['period'])
    return topo.mean_train + contrib


def run_one(data, name, home_period, horizons, n_anchors=60, test_window=None):
    n = len(data)
    if test_window is None: test_window = min(30*12, n//3)
    test_start = max(int(4*home_period), n - test_window)
    anchor_idxs = np.linspace(test_start, n - max(horizons) - 1, n_anchors).astype(int)

    # Set up the five configs
    configs = {}
    # A, B, C: phi substrate
    home_k_phi = round(math.log(home_period)/math.log(PHI))
    k_lo_phi = max(2, int(math.log(3.0)/math.log(PHI)))
    k_hi_phi = int(math.log(min(720.0, n/4.0))/math.log(PHI)) + 1
    rungs_k_phi = list(range(k_lo_phi, k_hi_phi+1))
    configs['A: phi-sub + phi-decay'] = ('phi', rungs_k_phi, home_k_phi, 'kdiff', PHI)
    configs['B: phi-sub + 2-decay'] = ('phi', rungs_k_phi, home_k_phi, 'kdiff', 2.0)
    configs['C: phi-sub + ARA-dist(α=4)'] = ('phi', rungs_k_phi, home_k_phi, 'aradist', 4.0)
    # D, E: 2 substrate
    home_k_2 = round(math.log(home_period)/math.log(2.0))
    k_lo_2 = max(2, int(math.log(3.0)/math.log(2.0)))
    k_hi_2 = int(math.log(min(720.0, n/4.0))/math.log(2.0)) + 1
    rungs_k_2 = list(range(k_lo_2, k_hi_2+1))
    configs['D: 2-sub + 2-decay'] = (2.0, rungs_k_2, home_k_2, 'kdiff', 2.0)
    configs['E: 2-sub + ARA-dist(α=4)'] = (2.0, rungs_k_2, home_k_2, 'aradist', 4.0)

    out = {cname: {h: {'p':[], 't':[]} for h in horizons} for cname in configs}
    pers = {h: {'p':[], 't':[]} for h in horizons}

    for t in anchor_idxs:
        for cname, (rb, rk, hk, mode, param) in configs.items():
            rung_base = PHI if rb == 'phi' else 2.0
            topo, _ = extract_topology(data, t, rk, hk, rung_base)
            if topo is None: continue
            for h in horizons:
                if t + h >= n: continue
                if mode == 'kdiff':
                    p = predict_old_kdiff(topo, h, param)
                else:
                    p = predict_old_ara_distance(topo, h, param)
                truth = float(data[t+h-1])
                if np.isfinite(p):
                    out[cname][h]['p'].append(p)
                    out[cname][h]['t'].append(truth)
        for h in horizons:
            if t + h >= n: continue
            pers[h]['p'].append(float(data[t-1]))
            pers[h]['t'].append(float(data[t+h-1]))

    print(f'\n=== {name} ===')
    print(f"{'config':35s} " + ' '.join(f'h={h:>4}' for h in horizons))
    summary = {}
    for cname in configs:
        row = [f'{cname:35s}']
        per_h = {}
        for h in horizons:
            P = np.array(out[cname][h]['p']); T = np.array(out[cname][h]['t'])
            if len(P) < 5:
                row.append(f' {"-":>4}'); per_h[h] = None; continue
            mae = float(np.mean(np.abs(P-T)))
            row.append(f' {mae:>5.3f}')
            per_h[h] = mae
        summary[cname] = per_h
        print(''.join(row))
    # Persistence
    row = [f'{"persistence":35s}']
    for h in horizons:
        P = np.array(pers[h]['p']); T = np.array(pers[h]['t'])
        if len(P) >= 5:
            mae = float(np.mean(np.abs(P-T)))
            row.append(f' {mae:>5.3f}')
        else:
            row.append(f' {"-":>4}')
    print(''.join(row))

    # Per-horizon winner
    print(f"\nPer-horizon winner:")
    for h in horizons:
        cands = [(c, summary[c][h]) for c in summary if summary[c][h] is not None]
        cands.sort(key=lambda x: x[1])
        if cands:
            winner, mae = cands[0]
            print(f'  h={h:>4}  {winner:35s}  MAE={mae:.3f}')

    return summary


# ---------------- Load and run ----------------
print('Loading ENSO ...')
nino = pd.read_csv(os.path.join(REPO_ROOT,'Nino34','nino34.long.anom.csv'),
                   skiprows=1, names=['d','v'], header=None, sep=',', engine='python')
NINO = pd.to_numeric(nino['v'], errors='coerce').dropna().values.astype(float)
NINO = NINO[NINO > -50]
print(f'  {len(NINO)} months')
enso_s = run_one(NINO, 'ENSO', 47.0, [1,6,12,60,120], test_window=30*12)

print('\nLoading solar SILSO ...')
silso = pd.read_csv(os.path.join(REPO_ROOT,'SILSO_Solar','SN_m_tot_V2.0.csv'),
                    sep=';', header=None,
                    names=['y','m','dy','v','s','n','mk'])
SUN = pd.to_numeric(silso['v'], errors='coerce').dropna().values.astype(float)
SUN = SUN[SUN >= 0]
print(f'  {len(SUN)} months ({len(SUN)/12:.1f}yr)')
solar_s = run_one(SUN, 'Solar SILSO', 132.0, [6,12,60,132,264], test_window=100*12)

# Save
OUT = os.path.join(_HERE, 'log2_substrate_data.js')
with open(OUT, 'w') as f:
    f.write("window.LOG2_SUBSTRATE = " + json.dumps({
        'date': '2026-05-11',
        'configs': ['phi-sub + phi-decay', 'phi-sub + 2-decay', 'phi-sub + ARA-dist',
                    '2-sub + 2-decay', '2-sub + ARA-dist'],
        'enso': enso_s, 'solar': solar_s,
    }, default=str) + ";\n")
print(f'\nSaved -> {OUT}')
