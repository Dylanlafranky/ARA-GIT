"""
multi_subject_dip_test.py

Run the actual-values delta-integration architecture across multiple PhysioNet
NSR subjects. Goal: see whether the 100-1000 beat dip in mid-horizon prediction
is consistent across subjects (supporting Dylan's "intruder wave" hypothesis)
or subject-specific (just one person's autonomic noise).

For each subject:
  - Load R-peak annotations from PhysioNet WFDB format
  - Convert to RR intervals (ms)
  - Run actual_values_delta architecture at multiple anchors
  - Score across horizons spanning 1 beat to ~6000 beats

Then aggregate dip-shape across subjects.
"""
import os
import json, os, time
import numpy as np
import wfdb
from scipy.signal import butter, sosfilt

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
# Repo root: parent dir if this script is in TheFormula/, else current dir
REPO_ROOT = _PARENT if os.path.basename(_HERE) == "TheFormula" else _HERE

PHI = 1.6180339887498949

DATA_DIR = os.path.join(REPO_ROOT, "normal-sinus-rhythm-rr-interval-database-1.0.0")
OUT      = os.path.join(REPO_ROOT, "TheFormula/multi_subject_dip_data.js")

SUBJECTS = ['nsr001','nsr005','nsr010','nsr015','nsr020','nsr025','nsr030','nsr035','nsr040','nsr045','nsr050']

def load_rr(subject):
    """Read R-peak annotations and convert to RR intervals (ms)."""
    ann = wfdb.rdann(os.path.join(DATA_DIR, subject), 'ecg')
    fs = ann.fs
    rr_ms = np.diff(ann.sample) / fs * 1000.0
    return rr_ms.astype(float)

def causal_bandpass(arr, period_beats, bw=0.4, order=2):
    n = len(arr); f_c = 1.0/period_beats; nyq = 0.5
    Wn_lo = max(1e-6, (1-bw)*f_c/nyq); Wn_hi = min(0.999, (1+bw)*f_c/nyq)
    if Wn_lo >= Wn_hi: return np.zeros(n)
    try:
        sos = butter(order, [Wn_lo, Wn_hi], btype='bandpass', output='sos')
        return sosfilt(sos, arr - np.mean(arr))
    except Exception:
        return np.zeros(n)

RUNGS_K = list(range(2, 22))
RUNGS = [(k, PHI**k) for k in RUNGS_K]

def measure_state(bp, period_beats):
    p_int = max(2, int(period_beats))
    if len(bp) < 2 * p_int + 5: return None
    last_cycle = bp[-p_int:]
    amp = float((np.max(last_cycle) - np.min(last_cycle)) / 2.0)
    if amp < 1e-9: return None
    v_now = float(bp[-1]); v_prev = float(bp[-2])
    norm = max(amp, 1e-9)
    ratio = max(-0.99, min(0.99, v_now / norm))
    th = np.arccos(ratio) * (-1 if (v_now - v_prev) > 0 else 1)
    return dict(amp=amp, theta=float(th), period=float(period_beats))

def project_actual(rr, t_anchor, h, cached_states=None):
    """Δ-integration over h steps telescopes to closed form:
    v(h) = v_now + Σ_rung amp × (cos(θ + 2π·h/p) − cos(θ))
    No step loop needed — fast for any h."""
    v_now = float(rr[t_anchor - 1])
    if cached_states is None:
        states = []
        for k, p in RUNGS:
            if 4*p > t_anchor: continue
            bp = causal_bandpass(rr[:t_anchor], p)
            st = measure_state(bp, p)
            if st is None: continue
            states.append(st)
    else:
        states = cached_states
    if not states: return v_now
    delta = 0.0
    for s in states:
        delta += s['amp'] * (np.cos(s['theta'] + 2*np.pi*h/s['period']) - np.cos(s['theta']))
    return v_now + delta

def states_at_anchor(rr, t_anchor):
    """Cache the per-rung states at an anchor — reused across all horizons."""
    states = []
    for k, p in RUNGS:
        if 4*p > t_anchor: continue
        bp = causal_bandpass(rr[:t_anchor], p)
        st = measure_state(bp, p)
        if st is None: continue
        states.append(st)
    return states

# Horizons spanning 1 beat to multi-thousand beats
HORIZONS = [1, 3, 10, 30, 100, 300, 600, 1000, 2000, 3000, 5000]

print(f"Multi-subject dip test, {len(SUBJECTS)} subjects, {len(HORIZONS)} horizons")
results = {}
for subj in SUBJECTS:
    try:
        rr = load_rr(subj)
        N_subj = len(rr)
        print(f"  {subj}: {N_subj} beats, mean RR {np.mean(rr):.0f} ms")
    except Exception as e:
        print(f"  {subj}: load failed ({e})")
        continue
    if N_subj < 10000:
        print(f"    skipping (too short for dip test)")
        continue
    # Anchors: every 5000 beats from beat 20000 onwards, leave room for max horizon
    max_h = max(HORIZONS)
    anchor_set = list(range(20000, N_subj - max_h, 5000))
    if len(anchor_set) < 4:
        print(f"    skipping (not enough room for anchors)")
        continue

    subj_results = {h: [] for h in HORIZONS}
    t0 = time.time()
    for t_a in anchor_set:
        # Cache per-anchor states once — reused across all horizons
        cached = states_at_anchor(rr, t_a)
        for h in HORIZONS:
            if t_a + h - 1 >= N_subj: continue
            truth = float(rr[t_a + h - 1])
            pred = project_actual(rr, t_a, h, cached_states=cached)
            subj_results[h].append((t_a, pred, truth))

    metrics = {}
    for h in HORIZONS:
        recs = subj_results[h]
        if len(recs) < 3: continue
        rec = np.array(recs)
        origins = rec[:,0].astype(int); preds = rec[:,1].astype(float); truths = rec[:,2].astype(float)
        pers = rr[origins-1]
        c = float(np.corrcoef(preds, truths)[0,1]) if np.std(preds) > 1e-9 else 0
        mae = float(np.mean(np.abs(preds-truths)))
        r2p = float(1 - np.sum((truths-preds)**2)/np.sum((truths-pers)**2))
        metrics[h] = dict(corr=c, mae=mae, r2p=r2p, n=int(len(recs)))
    results[subj] = dict(n_beats=int(N_subj), mean_rr=float(np.mean(rr)),
                          n_anchors=len(anchor_set), metrics=metrics)
    print(f"    {len(anchor_set)} anchors, ran in {time.time()-t0:.1f}s")

# === Aggregate dip pattern ===
print(f"\n{'horizon':>7}", end='')
for subj in results: print(f"  {subj}", end='')
print(f"  {'mean corr':>10}")
mean_corr_by_h = {}
for h in HORIZONS:
    print(f"{h:>7}", end='')
    corrs_at_h = []
    for subj in results:
        c = results[subj]['metrics'].get(h, {}).get('corr', None)
        if c is not None:
            corrs_at_h.append(c)
            print(f"  {c:+.3f}", end='')
        else:
            print(f"   ----", end='')
    if corrs_at_h:
        mean_c = float(np.mean(corrs_at_h))
        mean_corr_by_h[h] = mean_c
        print(f"   {mean_c:+.3f}")
    else:
        print()

# Find each subject's dip
print(f"\n{'subject':>8}  {'dip_h':>6}  {'dip_corr':>9}  {'recovery_h':>10}  {'pre-dip corr':>13}")
dip_patterns = {}
for subj, info in results.items():
    corrs = [(h, info['metrics'].get(h, {}).get('corr', None)) for h in HORIZONS]
    valid = [(h, c) for h, c in corrs if c is not None]
    if len(valid) < 5: continue
    # Find lowest corr in mid range
    mid_range = [(h, c) for h, c in valid if 30 <= h <= 2000]
    if not mid_range: continue
    dip_h, dip_c = min(mid_range, key=lambda x: x[1])
    pre = [c for h, c in valid if h <= 30]
    pre_c = float(np.mean(pre)) if pre else None
    # Find recovery: first horizon AFTER dip where corr returns to within 0.1 of pre-dip
    recovery_h = None
    if pre_c is not None:
        for h, c in valid:
            if h > dip_h and c >= pre_c - 0.15:
                recovery_h = h; break
    dip_patterns[subj] = dict(dip_h=dip_h, dip_corr=dip_c, recovery_h=recovery_h, pre_dip_corr=pre_c)
    print(f"  {subj:>6}  {dip_h:>6}  {dip_c:+.3f}     {str(recovery_h) if recovery_h else '—':>10}     {pre_c:+.3f}" if pre_c is not None else "")

out = dict(subjects=list(results.keys()), horizons=HORIZONS,
           results=results, mean_corr_by_h=mean_corr_by_h, dip_patterns=dip_patterns)
with open(OUT, 'w') as f:
    f.write("window.MULTI_DIP = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
            if h > dip_h and c >= pre_c - 0.15:
                recovery_h = h; break
    dip_patterns[subj] = dict(dip_h=dip_h, dip_corr=dip_c, recovery_h=recovery_h, pre_dip_corr=pre_c)
    if pre_c is not None:
        print(f"  {subj:>6}  {dip_h:>6}  {dip_c:+.3f}     {str(recovery_h) if recovery_h else '-':>10}     {pre_c:+.3f}")

out = dict(subjects=list(results.keys()), horizons=HORIZONS,
           results=results, mean_corr_by_h=mean_corr_by_h, dip_patterns=dip_patterns)
with open(OUT, 'w') as f:
    f.write("window.MULTI_DIP = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
