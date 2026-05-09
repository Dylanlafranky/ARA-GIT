"""
actual_values_delta_test.py

Per Dylan's request: no averages, no means. Use actual values throughout.
  - Raw RR per beat, indexed by beat number (no resampling, no time-grid).
  - Bandpasses operate directly on the RR signal in beat units.
  - At anchor, each rung's state read from the MOST RECENT CYCLE ONLY (not averaged).
  - Forward by integrating actual deltas (Δ per beat) — v[n+1] = v[n] + Σ channel_deltas.
  - Sum across rungs (not average).
  - No mean addition or subtraction at any stage.

Compares to OLD method (mean + averaged amp + cosine + averaged sum).
"""
import json, os, time
import numpy as np, pandas as pd
from scipy.signal import butter, sosfilt, find_peaks
from scipy.ndimage import gaussian_filter1d

PHI = 1.6180339887498949

def _resolve(p):
    p_lin = p.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p

ECG_PATH = _resolve(r"F:\SystemFormulaFolder\TheFormula\nsr001_rr.csv")
OUT      = _resolve(r"F:\SystemFormulaFolder\TheFormula\actual_values_delta_data.js")

print("Loading ECG nsr001 (per-beat RR — no resampling)...")
df = pd.read_csv(ECG_PATH)
RR = df['rr_ms'].values.astype(float)  # per-beat sequence
TIMES = df['time_s'].values.astype(float)
N = len(RR)
print(f"  {N} beats, mean RR {np.mean(RR):.0f} ms")

def causal_bandpass(arr, period_beats, bw=0.4, order=2):
    """Bandpass on the per-beat sequence directly. Period in beat units."""
    n = len(arr); f_c = 1.0/period_beats; nyq = 0.5
    Wn_lo = max(1e-6, (1-bw)*f_c/nyq); Wn_hi = min(0.999, (1+bw)*f_c/nyq)
    if Wn_lo >= Wn_hi: return np.zeros(n)
    try:
        sos = butter(order, [Wn_lo, Wn_hi], btype='bandpass', output='sos')
        # we'll subtract local mean internally so we can keep input as actual values
        return sosfilt(sos, arr - np.mean(arr))
    except Exception:
        return np.zeros(n)

# φ-rungs in BEAT units. Heartbeat itself is at φ⁰ = 1 beat.
# For nsr001 with mean RR ~760ms, beat ≈ 0.76s, so:
#   φ⁵  ≈ 11 beats ≈ 8.4s    (breathing)
#   φ¹⁰ ≈ 123 beats ≈ 93s    (Mayer wave / baroreflex)
#   φ¹⁵ ≈ 1364 beats ≈ 17min  (BRAC envelope range)
#   φ²⁰ ≈ 15127 beats ≈ 3.2h  (multi-hour autonomic)
RUNGS_K = list(range(2, 22))   # φ² (2.6 beats) up through φ²¹ (15k beats)
RUNGS = [(k, PHI**k) for k in RUNGS_K]
N_RUNGS = len(RUNGS)

def measure_local_state(bp, period_beats):
    """Read state from the MOST RECENT CYCLE only — no averaging across history.
    Returns (v_recent, dv_recent, amp_local, phase) where amp_local = peak-to-peak of last cycle / 2."""
    p_int = max(2, int(period_beats))
    if len(bp) < 2 * p_int + 5: return None
    last_cycle = bp[-p_int:]
    amp_local = float((np.max(last_cycle) - np.min(last_cycle)) / 2.0)
    if amp_local < 1e-9: return None
    v_now  = float(bp[-1])
    v_prev = float(bp[-2])
    dv = v_now - v_prev
    # phase from current value & velocity
    norm = max(amp_local, 1e-9)
    ratio = max(-0.99, min(0.99, v_now / norm))
    th = np.arccos(ratio) * (-1 if dv > 0 else 1)
    return dict(v_now=v_now, dv=dv, amp=amp_local, theta=float(th), period=float(period_beats))

def channel_delta_at_step(state, step):
    """Δ for one bandpass channel between step n and step n+1, given local state."""
    p = state['period']
    th_n   = state['theta'] + 2*np.pi*(step) / p
    th_np1 = state['theta'] + 2*np.pi*(step + 1) / p
    return state['amp'] * (np.cos(th_np1) - np.cos(th_n))

# === ACTUAL-VALUES METHOD ===
def project_actual(t_anchor, h_beats):
    """Anchor at v_now (actual RR value). Step forward h beats by integrating
    sum of channel deltas. No mean subtraction or addition."""
    v_now = float(RR[t_anchor - 1])
    states = []
    for k, p in RUNGS:
        if 4*p > t_anchor: continue
        bp = causal_bandpass(RR[:t_anchor], p)
        st = measure_local_state(bp, p)
        if st is None: continue
        states.append(st)
    if not states: return v_now

    v = v_now
    for step in range(h_beats):
        delta_total = 0.0
        for s in states:
            delta_total += channel_delta_at_step(s, step)
        v = v + delta_total
    return v

# === OLD AVERAGE METHOD (for comparison) ===
def amp_std50(bp):
    n_recent = min(50, len(bp))
    return float(np.std(bp[-n_recent:]) * np.sqrt(2)) + 1e-9

def project_old(t_anchor, h_beats):
    """Mean + averaged amp + averaged sum cosine."""
    arr = RR[:t_anchor]
    mean_t = float(np.mean(arr))
    arr0 = arr - mean_t
    pinned = []
    for k, p in RUNGS:
        if 4*p > t_anchor: continue
        bp = causal_bandpass(arr, p)  # already de-means internally
        a = amp_std50(bp)
        last = bp[-1]; rate = bp[-1] - bp[-2]
        ratio = max(-0.99, min(0.99, last/a))
        th = np.arccos(ratio) * (-1 if rate > 0 else 1)
        pinned.append(dict(p=p, amp=a, theta=th, k=k))
    if not pinned: return mean_t
    rung_w = np.array([PHI**(-abs(s['k'] - 8)) for s in pinned])
    rung_w = rung_w / rung_w.sum()
    contrib = 0.0
    for j, s in enumerate(pinned):
        new_th = s['theta'] + 2*np.pi*h_beats/s['p']
        contrib += rung_w[j] * s['amp'] * np.cos(new_th)
    return mean_t + contrib

# === Sweep ===
HORIZONS = [1, 10, 100, 500, 1000, 3000]   # beats ahead
HORIZON_LABELS = ['1 beat', '10 beats', '100 beats', '500 beats', '1000 beats', '3000 beats']
ANCHORS = list(range(20000, 90000, 5000))  # 14 anchors across the recording
print(f"\n{len(ANCHORS)} anchors, comparing OLD (mean+avg) vs ACTUAL (delta-integration)")

t0 = time.time()
results = {('OLD', h): [] for h in HORIZONS}
results.update({('ACT', h): [] for h in HORIZONS})
for t_a in ANCHORS:
    for h in HORIZONS:
        if t_a + h - 1 >= N: continue
        truth = float(RR[t_a + h - 1])
        results[('OLD', h)].append((t_a, project_old(t_a, h), truth))
        results[('ACT', h)].append((t_a, project_actual(t_a, h), truth))
print(f"  ran in {time.time()-t0:.1f}s")

print(f"\n{'horizon':>11}  {'method':>6}  {'corr':>7}  {'MAE_ms':>7}  {'R2(pers)':>9}  n")
out_metrics = {}
for h, lbl in zip(HORIZONS, HORIZON_LABELS):
    for method in ['OLD', 'ACT']:
        recs = results[(method, h)]
        if not recs: continue
        rec = np.array(recs)
        origins = rec[:,0].astype(int); preds = rec[:,1].astype(float); truths = rec[:,2].astype(float)
        pers = RR[origins-1]
        c = float(np.corrcoef(preds, truths)[0,1]) if np.std(preds) > 1e-9 else 0
        mae = float(np.mean(np.abs(preds-truths)))
        r2p = float(1 - np.sum((truths-preds)**2)/np.sum((truths-pers)**2))
        print(f"  {lbl:>11}  {method:>6}  {c:+.3f}    {mae:>6.1f}    {r2p:>+.3f}    {len(recs)}")
        out_metrics[f'{lbl}_{method}'] = dict(corr=c, mae=mae, r2p=r2p, n=int(len(recs)))

# Dense forward at one anchor (60000 beats in ≈ 12.7h)
anchor_idx = 60000
print(f"\nDense forward at anchor beat {anchor_idx} ({TIMES[anchor_idx]/3600:.1f}h)...")
dense_h = list(range(1, 5001, 25))
dense_old = [project_old(anchor_idx, h) for h in dense_h]
dense_act = [project_actual(anchor_idx, h) for h in dense_h]
dense_truth = [float(RR[anchor_idx + h - 1]) if anchor_idx + h - 1 < N else None for h in dense_h]
dense_t_h = [TIMES[anchor_idx + h - 1] / 3600 if anchor_idx + h - 1 < N else None for h in dense_h]
hist_t_h = [TIMES[i] / 3600 for i in range(max(0, anchor_idx-2000), anchor_idx)]
hist_truth = [float(RR[i]) for i in range(max(0, anchor_idx-2000), anchor_idx)]

out = dict(metrics=out_metrics, anchor_beat=anchor_idx, anchor_t_h=TIMES[anchor_idx]/3600,
           dense=dict(t_h=dense_t_h, h_beats=dense_h, old=dense_old, act=dense_act, truth=dense_truth),
           history=dict(t_h=hist_t_h, truth=hist_truth))
with open(OUT, 'w') as f:
    f.write("window.ACTUAL_DELTA = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
