"""
predictor_filter_comparison.py — does Morlet help the predictor vs Butterworth?

Run canonical predictor on ENSO with BOTH filters, compare MAE at h=1,3,6,12.

Short-range hypothesis: Morlet captures more phase information, so ACT
(integration of deltas from v_now) might be more accurate.

Long-range hypothesis: Morlet's overlapping bands cause OLD (weighted sum)
to over-count, so long-range may degrade.
"""
import os, json, math
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfilt

PHI = (1 + 5**0.5) / 2
CROSSOVER_EXPONENT = 7.0 / 4.0

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)


def butter_bandpass(arr, period, bw=0.4, order=2):
    arr = np.asarray(arr, dtype=float)
    n = len(arr)
    f_c = 1.0/period; nyq = 0.5
    Wn_lo = max(1e-6, (1-bw)*f_c/nyq); Wn_hi = min(0.999, (1+bw)*f_c/nyq)
    if Wn_lo >= Wn_hi: return np.zeros(n)
    sos = butter(order, [Wn_lo, Wn_hi], btype='bandpass', output='sos')
    return sosfilt(sos, arr - np.mean(arr))


def morlet_causal_bandpass(arr, period, n_cycles=4):
    arr = np.asarray(arr, dtype=float) - np.mean(arr)
    n = len(arr)
    sigma = n_cycles * period / 6.0
    kernel_len = min(int(6*sigma), 800)  # cap kernel for speed
    t_kernel = np.arange(kernel_len)
    kernel = np.exp(-t_kernel**2 / (2*sigma**2)) * np.cos(2*np.pi*t_kernel/period)
    kernel = kernel / max(1e-9, np.sqrt(np.sum(kernel**2)))
    out = np.zeros(n)
    for i in range(n):
        j_max = min(kernel_len, i+1)
        out[i] = float(np.dot(kernel[:j_max], arr[i-j_max+1:i+1][::-1]))
    return out


def measure_rung(bp, period, k):
    p_int = max(2, int(period))
    if len(bp) < 2*p_int + 5: return None
    last_cycle = bp[-p_int:]
    amp = float((np.max(last_cycle) - np.min(last_cycle)) / 2.0)
    if amp < 1e-9: return None
    v_recent = float(bp[-1]); v_prev = float(bp[-2])
    norm = max(amp, 1e-9)
    ratio = max(-0.99, min(0.99, v_recent / norm))
    theta = float(math.acos(ratio) * (-1.0 if (v_recent - v_prev) > 0 else 1.0))
    return dict(k=int(k), period=float(period), amp=amp, theta=theta)


def extract_topology(data, t, filter_fn, rungs_k, home_k, pin_factor=4):
    arr = np.asarray(data, dtype=float)
    if t < 5 or t > len(arr): return None
    v_now = float(arr[t-1]); mean_train = float(np.mean(arr[:t]))
    rungs = []
    for k in rungs_k:
        period = PHI ** int(k)
        if period < 2 or pin_factor * period > t: continue
        bp = filter_fn(arr[:t], period)
        rec = measure_rung(bp, period, k)
        if rec: rungs.append(rec)
    return dict(v_now=v_now, mean_train=mean_train, home_k=home_k, rungs=rungs)


def predict_canonical(topo, h, closed=False, blend_steepness=2.0):
    if not topo['rungs']: return topo['v_now']
    home_period = PHI ** topo['home_k']
    sign = -1.0 if closed else +1.0
    cross_h = home_period * (PHI ** (sign * CROSSOVER_EXPONENT))
    z = blend_steepness * (cross_h - h) / max(cross_h, 1e-9)
    w_act = 1.0 / (1.0 + math.exp(-z))
    # ACT
    delta = sum(r['amp'] * (math.cos(r['theta'] + 2*math.pi*h/r['period']) - math.cos(r['theta']))
                for r in topo['rungs'])
    p_act = topo['v_now'] + delta
    # OLD
    weights = np.array([PHI ** (-abs(r['k'] - topo['home_k'])) for r in topo['rungs']])
    weights /= weights.sum()
    contrib = sum(w * r['amp'] * math.cos(r['theta'] + 2*math.pi*h/r['period'])
                  for w, r in zip(weights, topo['rungs']))
    p_old = topo['mean_train'] + contrib
    return w_act * p_act + (1.0 - w_act) * p_old


# ============================================================================
# Load ENSO, set up anchors
# ============================================================================
print("Loading ENSO...")
df = pd.read_csv(os.path.join(REPO_ROOT, 'Nino34', 'nino34.long.anom.csv'),
                 skiprows=1, names=['d','v'], header=None, sep=',', engine='python')
nino = pd.to_numeric(df['v'], errors='coerce').dropna().values.astype(float)
nino = nino[nino > -50]
print(f"  {len(nino)} months")

HOME_K = 8  # period φ^8 ≈ 47 months
RUNGS = list(range(2, 13))
HORIZONS = [1, 3, 6, 12, 24]
N_ANCHORS = 30

test_start = max(240, len(nino) - 30*12)
anchors = np.linspace(test_start, len(nino) - max(HORIZONS) - 1, N_ANCHORS).astype(int)

# ============================================================================
# Run both filters
# ============================================================================
print(f"\nRunning {N_ANCHORS} anchors × {len(HORIZONS)} horizons × 2 filters...")
results = {'butter': {h: {'preds':[], 'truths':[]} for h in HORIZONS},
           'morlet': {h: {'preds':[], 'truths':[]} for h in HORIZONS}}

for i, t in enumerate(anchors):
    if i % 5 == 0: print(f"  anchor {i+1}/{N_ANCHORS}", flush=True)
    for fname, ffn in [('butter', butter_bandpass), ('morlet', morlet_causal_bandpass)]:
        topo = extract_topology(nino, t, ffn, RUNGS, HOME_K)
        if topo is None: continue
        for h in HORIZONS:
            if t + h >= len(nino): continue
            p = predict_canonical(topo, h)
            if not math.isfinite(p): continue
            results[fname][h]['preds'].append(p)
            results[fname][h]['truths'].append(float(nino[t+h-1]))

# ============================================================================
# Score
# ============================================================================
print()
print("=" * 70)
print("HEAD-TO-HEAD: Butterworth vs Morlet for ENSO prediction")
print("=" * 70)
print(f"{'h':>4}  {'butter_MAE':>11}  {'morlet_MAE':>11}  {'butter_corr':>12}  {'morlet_corr':>12}  {'winner':<8}")
print('-' * 75)
for h in HORIZONS:
    rb = results['butter'][h]; rm = results['morlet'][h]
    if len(rb['preds']) < 5 or len(rm['preds']) < 5: continue
    pb = np.array(rb['preds']); tb = np.array(rb['truths'])
    pm = np.array(rm['preds']); tm = np.array(rm['truths'])
    mae_b = float(np.mean(np.abs(pb - tb)))
    mae_m = float(np.mean(np.abs(pm - tm)))
    corr_b = float(np.corrcoef(pb, tb)[0,1]) if tb.std() > 0 and pb.std() > 0 else float('nan')
    corr_m = float(np.corrcoef(pm, tm)[0,1]) if tm.std() > 0 and pm.std() > 0 else float('nan')
    winner = 'butter' if mae_b < mae_m else 'morlet'
    print(f"  {h:>3}  {mae_b:>11.3f}  {mae_m:>11.3f}  {corr_b:>+12.3f}  {corr_m:>+12.3f}  {winner:<8}")

print()
print("Note: same predictor formula, only filter differs. Lower MAE = better.")
print("If Morlet wins SHORT horizons but Butterworth wins LONG horizons, it confirms")
print("the framework reading: Morlet better for phase-coherent ACT, Butterworth for OLD.")
