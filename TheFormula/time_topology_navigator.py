"""
time_topology_navigator.py

The framework's two halves working together — forward + inverse = full ARA cycle:
  - INVERSE half (build / consumer): given a time series and an anchor time t,
    extract (k, θ, ARA, amplitude) for every pinned φ-rung.
  - FORWARD half (release / engine): given that state, navigate via three operations:
      (A) Spin θ forward by Δt on current rung
      (B) Hop to rung k±1 (φ-rescale time, same shape)
      (C) Add/remove matched-rung partner

This script does the inverse extraction + computes forward projections at multiple
horizons AND on neighbouring rungs (k-1, k, k+1). All saved to JSON for the
HTML visualization to navigate interactively.

Strict-causal: anchor t means we only use NINO[:t]. Everything past t is read
later for comparison only.

System: ENSO (NINO 3.4 + SOI matched-rung partner at φ^8).
"""
import json, os, time
import numpy as np, pandas as pd
from scipy.signal import butter, sosfilt, find_peaks
from scipy.ndimage import gaussian_filter1d

PHI = 1.6180339887498949
INV_PHI3 = 1.0 / PHI**3

def _resolve(p):
    p_lin = p.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p

NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
SOI_PATH  = _resolve(r"F:\SystemFormulaFolder\SOI_NOAA\soi.data")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\time_topology_navigator_data.js")

def load_nino():
    df = pd.read_csv(NINO_PATH, skiprows=1, header=None, names=['date','val'])
    df['date'] = pd.to_datetime(df['date'].str.strip())
    df = df[df['val'] > -90].copy()
    return df.set_index('date')['val'].astype(float)

def load_soi():
    rows=[]
    with open(SOI_PATH) as f:
        next(f)
        for ln in f:
            parts = ln.split()
            if len(parts) < 13: continue
            try: y = int(parts[0])
            except: continue
            if y < 1900 or y > 2100: continue
            for m in range(12):
                try: v = float(parts[1+m])
                except: continue
                if v < -90: continue
                rows.append((pd.Timestamp(year=y, month=m+1, day=1), v))
    return pd.Series(dict(rows)).sort_index()

print("Loading NINO + SOI...")
nino = load_nino()
soi  = load_soi()

def to_monthly(s):
    s = s.copy(); s.index = pd.to_datetime(s.index).to_period('M').to_timestamp()
    return s.groupby(s.index).first()

nino, soi = to_monthly(nino), to_monthly(soi)
common = nino.index.intersection(soi.index).sort_values()
NINO = nino.reindex(common).values.astype(float)
SOI  = soi.reindex(common).values.astype(float)
DATES = common
N = len(NINO)
print(f"  N={N} months, {DATES[0].date()} to {DATES[-1].date()}")

def causal_bandpass(arr, period_units, bw=0.4, order=2):
    n = len(arr); f_c = 1.0/period_units; nyq = 0.5
    Wn_lo = max(1e-6, (1-bw)*f_c/nyq); Wn_hi = min(0.999, (1+bw)*f_c/nyq)
    if Wn_lo >= Wn_hi: return np.zeros(n)
    try:
        sos = butter(order, [Wn_lo, Wn_hi], btype='bandpass', output='sos')
        return sosfilt(sos, arr - np.mean(arr))
    except Exception:
        return np.zeros(n)

def per_rung_ARA(arr, period):
    """Read ARA at this rung from training data — fraction of cycle in build vs release."""
    bp = causal_bandpass(arr, period, bw=0.85)
    if len(bp) < 3*int(period): return 1.0
    smoothed = gaussian_filter1d(bp, max(1, int(period * 0.05)))
    peaks, _ = find_peaks(smoothed, distance=max(2, int(period * 0.7)))
    if len(peaks) < 2: return 1.0
    aras = []
    for i in range(len(peaks)-1):
        seg = smoothed[peaks[i]:peaks[i+1]+1]
        if len(seg) < 3: continue
        f_t = max(0.15, min(0.85, int(np.argmin(seg)) / max(1, len(seg)-1)))
        aras.append((1 - f_t) / f_t)
    if not aras: return 1.0
    return float(np.mean(np.clip(aras, 0.3, 3.0)))

def read_amp_theta(bp_to_t):
    """At end of bandpass output, extract amplitude and current phase θ."""
    if len(bp_to_t) < 2: return 0.0, 0.0, 0.0
    n_recent = min(50, len(bp_to_t))
    amp = float(np.std(bp_to_t[-n_recent:]) * np.sqrt(2)) + 1e-9
    last = bp_to_t[-1]; rate = bp_to_t[-1] - bp_to_t[-2]
    ratio = max(-0.99, min(0.99, last/amp))
    th = np.arccos(ratio) * (-1 if rate > 0 else 1)
    return amp, th, last

# ============================================================
# INVERSE HALF — extract (k, θ, ARA, amp) at anchor time t
# ============================================================
def inverse_extract(t, rungs):
    """For each rung, read the system's state from arr[:t]."""
    state = []
    arr = NINO[:t]
    soi_arr = SOI[:t]
    mean_train = float(np.mean(arr))
    std_train  = float(np.std(arr)) + 1e-9
    for k, p in rungs:
        if 2*p > t:
            state.append(dict(k=k, period=p, pinned=False, amp=0, theta=0, ara=1.0,
                              amp_soi=0, theta_soi=0, last_value=0))
            continue
        bp = causal_bandpass(arr, p)
        soi_bp = causal_bandpass(soi_arr, p)
        amp, th, last = read_amp_theta(bp)
        amp_s, th_s, _ = read_amp_theta(soi_bp)
        ara = per_rung_ARA(arr, p)
        state.append(dict(k=k, period=float(p), pinned=True,
                          amp=amp, theta=float(th), ara=ara,
                          amp_soi=amp_s, theta_soi=float(th_s),
                          last_value=float(last)))
    return state, mean_train, std_train

# ============================================================
# FORWARD HALF — three navigation operations
# ============================================================
def spin_theta(state_k, h_months):
    """(A) Advance phase forward by h months on this rung."""
    p = state_k['period']
    new_th = state_k['theta'] + 2*np.pi*h_months/p
    # ARA-driven amplitude decay over the horizon
    decay = np.exp(-abs(state_k['ara'] - PHI) * h_months / p * 0.05)
    return state_k['amp'] * decay * np.cos(new_th)

def hop_rung(state, current_k, target_k, h_months_in_current):
    """(B) Hop to neighbouring rung. Target rung sees the same shape but
    time-stretched by φ^(target_k - current_k). So a horizon h on current rung
    corresponds to h × φ^Δk on target rung in absolute clock-time, but the
    same θ in dimensionless rung-space."""
    cur_idx = next((i for i,s in enumerate(state) if s['k'] == current_k), None)
    tar_idx = next((i for i,s in enumerate(state) if s['k'] == target_k), None)
    if cur_idx is None or tar_idx is None: return None
    if not state[tar_idx]['pinned']: return None
    # Target rung: the same θ-fraction-of-cycle gets traversed in φ^Δk × h months
    tar = state[tar_idx]
    delta_k = target_k - current_k
    # equivalent traversal: h_months × φ^Δk on target rung
    p_tar = tar['period']
    new_th = tar['theta'] + 2*np.pi*h_months_in_current*(PHI**delta_k)/p_tar
    decay = np.exp(-abs(tar['ara'] - PHI) * h_months_in_current * (PHI**delta_k) / p_tar * 0.05)
    return tar['amp'] * decay * np.cos(new_th)

def project_with_partner(state, mean_train, std_train, h_months, k_ref=8, use_partner=True):
    """(C) Forward project NINO at horizon h, optionally including SOI matched-rung partner at φ^k_ref."""
    rung_w = np.array([PHI**(-abs(s['k'] - k_ref)) if s['pinned'] else 0.0 for s in state])
    rung_w = rung_w / max(rung_w.sum(), 1e-9)
    # NINO own contribution
    own = 0.0
    for i, s in enumerate(state):
        if not s['pinned']: continue
        own += rung_w[i] * spin_theta(s, h_months)
    # SOI matched-rung partner at k_ref (anti-phase, full weight × 5 like SOI_MATCHED)
    partner = 0.0
    if use_partner:
        ref_idx = next((i for i,s in enumerate(state) if s['k'] == k_ref and s['pinned']), None)
        if ref_idx is not None:
            ref = state[ref_idx]
            new_th_soi = ref['theta_soi'] + 2*np.pi*h_months/ref['period']
            soi_val = ref['amp_soi'] * np.cos(new_th_soi)
            soi_norm = soi_val / (float(np.std(SOI)) + 1e-9) * std_train
            partner = -1 * soi_norm * rung_w[ref_idx] * 5.0
    return mean_train + own + partner

# ============================================================
# Run inverse + navigation suite
# ============================================================
RUNGS = [(k, PHI**k) for k in range(3, 13)]
N_RUNGS = len(RUNGS)

# Anchor at end of 2010 — gives us 12+ years of test data after
anchor_idx = next(i for i, d in enumerate(DATES) if d >= pd.Timestamp('2010-12-01'))
print(f"\nAnchor: {DATES[anchor_idx-1].date()} (training = months 0..{anchor_idx-1}, n={anchor_idx})")

state, mean_train, std_train = inverse_extract(anchor_idx, RUNGS)
print(f"\n=== INVERSE EXTRACTION at anchor ===")
print(f"  {'k':>3}  {'period':>8}  {'pinned':>7}  {'amp':>6}  {'θ (deg)':>8}  {'ARA':>5}  {'last':>6}")
for s in state:
    pinned = "✓" if s['pinned'] else "—"
    th_deg = np.degrees(s['theta'])
    print(f"  {s['k']:>3}  {s['period']:>8.1f}mo  {pinned:>7}  {s['amp']:.3f}  {th_deg:>+7.1f}°  {s['ara']:.2f}  {s['last_value']:+.3f}")

# Forward projection on home rung k=8 with partner ON and OFF
print(f"\n=== FORWARD PROJECTION (k=8 home, with vs without SOI partner) ===")
print(f"  {'h(mo)':>5}  {'date':>11}  {'pred (no partner)':>17}  {'pred (+SOI)':>11}  {'truth':>7}")
horizons = [1, 3, 6, 12, 24, 36]
forward_table = []
for h in horizons:
    pred_solo = project_with_partner(state, mean_train, std_train, h, use_partner=False)
    pred_pair = project_with_partner(state, mean_train, std_train, h, use_partner=True)
    if anchor_idx + h - 1 < N:
        truth = NINO[anchor_idx + h - 1]
        date = DATES[anchor_idx + h - 1].strftime('%Y-%m-%d')
    else:
        truth = None; date = '—'
    print(f"  {h:>5}  {date:>11}  {pred_solo:>+17.3f}  {pred_pair:>+11.3f}  {truth if truth is None else f'{truth:+.3f}':>7}")
    forward_table.append(dict(h=h, date=date,
                              pred_solo=pred_solo, pred_pair=pred_pair,
                              truth=truth if truth is not None else None))

# Hop to neighbouring rungs — show same forward projection from k=7 and k=9
print(f"\n=== RUNG-HOP: same forward shape projected via k-1 and k+1 ===")
print(f"(Hop demonstrates: same θ-fraction-of-cycle, φ-stretched in clock time)")
hop_results = {}
for hop_k in [6, 7, 8, 9, 10]:
    print(f"\n  -- viewing through rung k={hop_k} (period {PHI**hop_k:.1f} mo) --")
    print(f"  {'h(mo)':>5}  {'amp from k='+str(hop_k):>14}")
    rec = []
    for h in horizons:
        val = hop_rung(state, 8, hop_k, h)
        if val is not None:
            print(f"  {h:>5}  {val:>+14.3f}")
            rec.append(dict(h=h, amp=float(val)))
        else:
            print(f"  {h:>5}  unpinned")
            rec.append(dict(h=h, amp=None))
    hop_results[f'k{hop_k}'] = rec

# Generate dense forward curve for plotting (every month, h=1..36)
print("\nBuilding dense forward curves for visualization...")
dense_h = list(range(1, 37))
dense_solo = [project_with_partner(state, mean_train, std_train, h, use_partner=False) for h in dense_h]
dense_pair = [project_with_partner(state, mean_train, std_train, h, use_partner=True) for h in dense_h]
dense_truth = [float(NINO[anchor_idx + h - 1]) if anchor_idx + h - 1 < N else None for h in dense_h]
dense_dates = [DATES[anchor_idx + h - 1].strftime('%Y-%m-%d') if anchor_idx + h - 1 < N else None for h in dense_h]

# History (last 36 months before anchor) for context
hist_h = list(range(max(0, anchor_idx-36), anchor_idx))
hist_truth = [float(NINO[i]) for i in hist_h]
hist_dates = [DATES[i].strftime('%Y-%m-%d') for i in hist_h]

# Reverse — same trick but going backward in time on each rung
print("Computing reverse spin (negative h)...")
rev_h = list(range(-36, 0))
rev_pred = [project_with_partner(state, mean_train, std_train, h, use_partner=True) for h in rev_h]
rev_truth = [float(NINO[anchor_idx + h - 1]) if 0 <= anchor_idx + h - 1 < N else None for h in rev_h]
rev_dates = [DATES[anchor_idx + h - 1].strftime('%Y-%m-%d') if 0 <= anchor_idx + h - 1 < N else None for h in rev_h]

# Also generate dense per-rung view: each rung's forward wave on its own
print("Computing per-rung forward waves for hop visualization...")
per_rung_curves = {}
for k_view in [5, 6, 7, 8, 9, 10, 11]:
    s = next((s for s in state if s['k'] == k_view), None)
    if s is None or not s['pinned']: continue
    curve = []
    # show full multi-cycle forward view on this rung — span 2 full periods
    span_months = int(2 * s['period'])
    for h in range(1, span_months + 1):
        v = spin_theta(s, h)
        curve.append(dict(h=h, amp=float(v)))
    per_rung_curves[f'k{k_view}'] = dict(period=s['period'], ara=s['ara'], amp=s['amp'],
                                          theta_deg=float(np.degrees(s['theta'])), curve=curve)

out = dict(
    anchor=dict(idx=int(anchor_idx), date=DATES[anchor_idx-1].strftime('%Y-%m-%d')),
    state=state,
    mean_train=mean_train, std_train=std_train,
    forward=dict(
        horizons=dense_h, dates=dense_dates,
        pred_solo=dense_solo, pred_pair=dense_pair, truth=dense_truth,
    ),
    history=dict(dates=hist_dates, truth=hist_truth),
    reverse=dict(horizons=rev_h, dates=rev_dates, pred=rev_pred, truth=rev_truth),
    per_rung_curves=per_rung_curves,
    hop_table=hop_results,
    forward_table=forward_table,
    rungs=[k for k,_ in RUNGS],
)
with open(OUT, 'w') as f:
    f.write("window.NAVIGATOR = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
