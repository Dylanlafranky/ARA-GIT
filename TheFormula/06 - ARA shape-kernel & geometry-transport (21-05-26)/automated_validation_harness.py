"""
automated_validation_harness.py — Unified benchmark of the ARA framework's
predictive power against standard baselines and negative controls.

Loads:
  - ENSO (climate): Nino 3.4 anomalies
  - Solar (astrophysics): SILSO sunspot numbers
  - ECG (cardiology): normal sinus rhythm RR intervals (nsr001)

Compares:
  - Baselines: Persistence, Mean, Direct AR(p), Fourier Fit
  - ARA Models: Canonical blended predictor, Base-sweeping, Dual-Role predictor
"""
import os
import sys
import json
import math
import time
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfilt
import wfdb

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, REPO_ROOT)

# Imports from canonical framework
from ara_framework import (
    Topology, causal_bandpass, _measure_rung, PHI
)

# Inline measure_rung_ara to avoid side-effects of importing dual_role_predictor_test.py
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d

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

# ----------------- GENERALIZED ARA PREDICTORS -----------------

def extract_topology_with_base(data, t, rung_base, rungs_k, home_k, pin_factor=4):
    """Substrate: rung_base^k spaced rungs."""
    arr = np.asarray(data, dtype=float)
    if t < 5 or t > len(arr):
        return None
    v_now = float(arr[t - 1])
    mean_train = float(np.mean(arr[:t]))
    rungs = []
    for k in rungs_k:
        period = rung_base ** int(k)
        if period < 2 or pin_factor * period > t:
            continue
        bp = causal_bandpass(arr[:t], period)
        rec = _measure_rung(bp, period, k)
        if rec is not None:
            # Also add rung ARA for dual-role weighting
            ara = measure_rung_ara(arr[:t], period)
            if ara is not None:
                rec['ara'] = float(ara)
            rungs.append(rec)
    return Topology(v_now=v_now, mean_train=mean_train, home_k=home_k, rungs=rungs)


def predict_blended_with_base(topo, h, rung_base, closed=False, steepness=2.0):
    """Blended ACT/OLD prediction using generalized base."""
    if topo is None or not topo.rungs:
        return float('nan') if topo is None else topo.mean_train

    # 1. ACT prediction (integrating actual deltas)
    delta = 0.0
    for s in topo.rungs:
        a, th, p = s['amp'], s['theta'], s['period']
        delta += a * (np.cos(th + 2 * np.pi * h / p) - np.cos(th))
    p_act = topo.v_now + delta

    # 2. OLD prediction (base-weighted training mean)
    weights = np.array([rung_base ** (-abs(s['k'] - topo.home_k)) for s in topo.rungs])
    if weights.sum() <= 0:
        p_old = topo.mean_train
    else:
        weights = weights / weights.sum()
        contrib = 0.0
        for j, s in enumerate(topo.rungs):
            new_th = s['theta'] + 2 * np.pi * h / s['period']
            contrib += weights[j] * s['amp'] * np.cos(new_th)
        p_old = topo.mean_train + contrib

    # 3. Blended weighting
    home_period = float(rung_base ** topo.home_k)
    sign = -1.0 if closed else +1.0
    h_cross = home_period * (rung_base ** (sign * 1.75))
    z = steepness * (h_cross - h) / max(h_cross, 1e-9)
    w_act = 1.0 / (1.0 + np.exp(-z))

    return w_act * p_act + (1.0 - w_act) * p_old


def predict_dual_role(topo, h, rung_base, closed=False, alpha=4.0, steepness=2.0):
    """Blended predictor where OLD weights are determined by measured ARA-distance."""
    if topo is None or not topo.rungs:
        return float('nan') if topo is None else topo.mean_train

    # 1. ACT prediction
    delta = 0.0
    for s in topo.rungs:
        a, th, p = s['amp'], s['theta'], s['period']
        delta += a * (np.cos(th + 2 * np.pi * h / p) - np.cos(th))
    p_act = topo.v_now + delta

    # 2. OLD prediction with ARA-distance weights
    ara_at_rung = {s['k']: s.get('ara') for s in topo.rungs}
    ara_home = ara_at_rung.get(topo.home_k)
    if ara_home is None:
        avail = [a for a in ara_at_rung.values() if a is not None]
        ara_home = float(np.mean(avail)) if avail else 1.0

    weights = []
    for s in topo.rungs:
        a = s.get('ara')
        if a is None:
            weights.append(math.exp(-alpha * 1.0))
        else:
            weights.append(math.exp(-alpha * abs(a - ara_home)))
    weights = np.array(weights)
    if weights.sum() <= 0:
        p_old = topo.mean_train
    else:
        weights = weights / weights.sum()
        contrib = 0.0
        for j, s in enumerate(topo.rungs):
            new_th = s['theta'] + 2 * np.pi * h / s['period']
            contrib += weights[j] * s['amp'] * np.cos(new_th)
        p_old = topo.mean_train + contrib

    # 3. Blended weighting
    home_period = float(rung_base ** topo.home_k)
    sign = -1.0 if closed else +1.0
    h_cross = home_period * (rung_base ** (sign * 1.75))
    z = steepness * (h_cross - h) / max(h_cross, 1e-9)
    w_act = 1.0 / (1.0 + np.exp(-z))

    return w_act * p_act + (1.0 - w_act) * p_old

# ----------------- NON-FRAMEWORK BASELINES -----------------

def predict_persistence(data, t, h):
    """Persistence baseline: future is same as now."""
    return float(data[t - 1])


def predict_mean(data, t, h):
    """Mean baseline: future is historical mean."""
    return float(np.mean(data[:t]))


def predict_ar_direct(data, t, h, p=12):
    """Direct Autoregressive AR(p) baseline trained via least squares."""
    arr = np.asarray(data[:t], dtype=float)
    if len(arr) < p + h + 10:
        return float(np.mean(arr))
    
    # Construct lag matrix: X = [lag_0, lag_1, ..., lag_{p-1}, bias]
    X = []
    Y = []
    for i in range(p - 1, len(arr) - h):
        row = [arr[i - j] for j in range(p)]
        row.append(1.0)
        X.append(row)
        Y.append(arr[i + h])
    X = np.array(X)
    Y = np.array(Y)
    
    try:
        beta, _, _, _ = np.linalg.lstsq(X, Y, rcond=None)
        current_row = [arr[t - 1 - j] for j in range(p)]
        current_row.append(1.0)
        return float(np.dot(current_row, beta))
    except Exception:
        return float(np.mean(arr))


def predict_fourier(data, t, h, num_components=5):
    """Fourier projection baseline: fits dominant periods on training set."""
    arr = np.asarray(data[:t], dtype=float)
    n = len(arr)
    mean_val = np.mean(arr)
    detrended = arr - mean_val
    
    fft_vals = np.fft.rfft(detrended)
    fft_freqs = np.fft.rfftfreq(n)
    amps = np.abs(fft_vals)
    amps[0] = 0  # Ignore DC component
    
    top_idxs = np.argsort(amps)[-num_components:]
    
    X = []
    for idx in range(n):
        row = [1.0]
        for f_idx in top_idxs:
            freq = fft_freqs[f_idx]
            row.append(np.cos(2 * np.pi * freq * idx))
            row.append(np.sin(2 * np.pi * freq * idx))
        X.append(row)
    X = np.array(X)
    
    try:
        beta, _, _, _ = np.linalg.lstsq(X, arr, rcond=None)
        proj_idx = t - 1 + h
        current_row = [1.0]
        for f_idx in top_idxs:
            freq = fft_freqs[f_idx]
            current_row.append(np.cos(2 * np.pi * freq * proj_idx))
            current_row.append(np.sin(2 * np.pi * freq * proj_idx))
        return float(np.dot(current_row, beta))
    except Exception:
        return float(mean_val)

# ----------------- DATA LOADERS -----------------

def load_enso():
    nino_path = os.path.join(REPO_ROOT, 'Nino34', 'nino34.long.anom.csv')
    df = pd.read_csv(nino_path, skiprows=1, header=None, names=['date', 'val'])
    df = df[df['val'] > -90].copy()
    return df['val'].values.astype(float)


def load_solar():
    silso_path = os.path.join(REPO_ROOT, 'SILSO_Solar', 'SN_m_tot_V2.0.csv')
    df = pd.read_csv(silso_path, sep=';', header=None,
                     names=['year', 'month', 'decyear', 'val', 'std', 'n_obs', 'marker'])
    return df['val'].values.astype(float)


def load_ecg():
    nsr_path = os.path.join(REPO_ROOT, 'normal-sinus-rhythm-rr-interval-database-1.0.0/nsr001')
    ann = wfdb.rdann(nsr_path, 'ecg')
    return (np.diff(ann.sample) / ann.fs * 1000).astype(float)

# ----------------- BENCHMARK ENGINE -----------------

def run_benchmark(name, data, home_period, horizons, closed, rungs_k, bases, n_anchors=40):
    print(f"\nBenchmarking {name}...")
    n = len(data)
    
    # Select anchors spaced out in the last 30% of the dataset
    test_window = int(0.30 * n)
    test_start = max(int(4 * home_period), n - test_window)
    anchors = np.linspace(test_start, n - max(horizons) - 1, n_anchors).astype(int)
    
    # Store predictions: {model_name: {horizon: [predictions]}}
    models = {
        'persistence': lambda data, t, h, topo: predict_persistence(data, t, h),
        'mean': lambda data, t, h, topo: predict_mean(data, t, h),
        'AR(12)': lambda data, t, h, topo: predict_ar_direct(data, t, h, p=12),
        'Fourier(5)': lambda data, t, h, topo: predict_fourier(data, t, h, num_components=5),
        'ARA (Dual-Role)': lambda data, t, h, topo: predict_dual_role(topo, h, PHI, closed=closed, alpha=4.0),
    }
    
    # Add bases to sweep
    for b_name, base_val in bases:
        models[f'ARA ({b_name})'] = lambda data, t, h, topo, bv=base_val: predict_blended_with_base(topo, h, bv, closed=closed)

    # Initialise storage
    preds = {m: {h: [] for h in horizons} for m in models}
    truths = {h: [] for h in horizons}
    
    # Pre-extract topologies for each base to save computation time
    topologies_by_base = {b_name: [] for b_name, _ in bases}
    topologies_by_base['PHI'] = []  # For dual role
    
    for t in anchors:
        # Extract topology for each base
        topos = {}
        for b_name, base_val in bases:
            home_k = round(math.log(home_period) / math.log(base_val))
            topo = extract_topology_with_base(data, t, base_val, rungs_k, home_k)
            topos[f'ARA ({b_name})'] = topo
            
        # Topo for PHI (used for dual role)
        home_k_phi = round(math.log(home_period) / math.log(PHI))
        topos['ARA (Dual-Role)'] = extract_topology_with_base(data, t, PHI, rungs_k, home_k_phi)
        
        for h in horizons:
            truths[h].append(float(data[t + h - 1]))
            for m_name, pred_fn in models.items():
                topo = topos.get(m_name)
                val = pred_fn(data, t, h, topo)
                preds[m_name][h].append(val)
                
    # Calculate metrics
    results = {}
    for h in horizons:
        results[h] = {}
        T = np.array(truths[h])
        pers_mae = np.mean(np.abs(np.array(preds['persistence'][h]) - T))
        
        for m_name in models:
            P = np.array(preds[m_name][h])
            # Drop nans
            valid = np.isfinite(P)
            if np.sum(valid) < 5:
                continue
            
            p_val = P[valid]
            t_val = T[valid]
            
            mae = float(np.mean(np.abs(p_val - t_val)))
            corr = float(np.corrcoef(p_val, t_val)[0, 1]) if np.std(p_val) > 1e-9 and np.std(t_val) > 1e-9 else 0.0
            
            # Directional accuracy
            v_now = np.array([data[t - 1] for t in anchors])[valid]
            pred_change = p_val - v_now
            true_change = t_val - v_now
            dir_acc = float(np.mean((pred_change * true_change) > 0))
            
            # Skill vs persistence
            skill_pers = float(1.0 - (mae / pers_mae)) if pers_mae > 0 else 0.0
            
            results[h][m_name] = {
                'mae': round(mae, 4),
                'corr': round(corr, 4),
                'dir_acc': round(dir_acc, 4),
                'skill_pers': round(skill_pers, 4)
            }
            
    return results

# ----------------- MAIN EXECUTION -----------------

def main():
    print("==================================================")
    print("      ARA AUTOMATED VALIDATION HARNESS            ")
    print("==================================================")
    
    # Load Datasets
    print("Loading datasets...")
    enso_data = load_enso()
    solar_data = load_solar()
    ecg_data = load_ecg()
    
    print(f"Loaded: ENSO ({len(enso_data)} months), Solar ({len(solar_data)} months), ECG ({len(ecg_data)} beats)")
    
    # Set up Bases to Sweep (negative controls)
    bases = [
        ('sqrt(2)', math.sqrt(2)),
        ('1.5', 1.5),
        ('1.6', 1.6),
        ('phi', PHI),
        ('1.7', 1.7),
        ('e_alt', 1.7183),
        ('1.8', 1.8),
        ('2.0', 2.0),
    ]
    
    # Run ENSO
    enso_results = run_benchmark(
        name='ENSO (closed=True)',
        data=enso_data,
        home_period=47.0, # ~4-year main cycle
        horizons=[1, 3, 6, 12, 24],
        closed=True,
        rungs_k=range(3, 13),
        bases=bases,
        n_anchors=40
    )
    
    # Run Solar
    solar_results = run_benchmark(
        name='Solar (closed=False)',
        data=solar_data,
        home_period=132.0, # 11-year cycle
        horizons=[6, 12, 60, 132],
        closed=False,
        rungs_k=range(4, 14),
        bases=bases,
        n_anchors=40
    )
    
    # Run ECG
    ecg_results = run_benchmark(
        name='ECG (closed=False)',
        data=ecg_data,
        home_period=60.0, # Short breathing/BRAC home
        horizons=[1, 3, 10, 30],
        closed=False,
        rungs_k=range(2, 12),
        bases=bases,
        n_anchors=40
    )
    
    # Prepare summary JSON
    all_results = {
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'datasets': {
            'ENSO': enso_results,
            'Solar': solar_results,
            'ECG': ecg_results
        }
    }
    
    # Save results to a JavaScript artifact
    out_path = os.path.join(_HERE, 'automated_validation_harness_data.js')
    with open(out_path, 'w') as f:
        f.write("window.VALIDATION_HARNESS = " + json.dumps(all_results, indent=2) + ";\n")
    print(f"\nSaved raw results to: {out_path}")
    
    # Print clean ELI5 Summary
    print("\n==================================================")
    print("                KEY TAKEAWAYS                     ")
    print("==================================================")
    
    for domain, res in [('ENSO', enso_results), ('Solar', solar_results), ('ECG', ecg_results)]:
        print(f"\n--- {domain} ---")
        # Identify the best models at short and long horizons
        sorted_horizons = sorted(res.keys())
        short_h = sorted_horizons[0]
        long_h = sorted_horizons[-1]
        
        for h_label, h in [('Short-lead', short_h), ('Long-lead', long_h)]:
            h_res = res[h]
            # Find best model by MAE
            best_model = min(h_res.keys(), key=lambda k: h_res[k]['mae'])
            best_mae = h_res[best_model]['mae']
            best_corr = h_res[best_model]['corr']
            best_skill = h_res[best_model]['skill_pers']
            
            # Find phi performance
            phi_model = 'ARA (phi)'
            phi_mae = h_res[phi_model]['mae'] if phi_model in h_res else float('nan')
            phi_skill = h_res[phi_model]['skill_pers'] if phi_model in h_res else float('nan')
            
            print(f"  * {h_label} (h={h}):")
            print(f"    - Best: {best_model} (MAE: {best_mae:.3f}, Corr: {best_corr:+.3f}, Skill vs Pers: {best_skill:+.3f})")
            if best_model != phi_model and phi_model in h_res:
                print(f"    - ARA (phi): MAE: {phi_mae:.3f}, Skill vs Pers: {phi_skill:+.3f}")
                
if __name__ == '__main__':
    main()
