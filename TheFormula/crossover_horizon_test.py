"""
crossover_horizon_test.py

Fine-grained horizon sweep on ENSO and ECG to locate the crossover
between actual-values delta-integration (ACT) and structured-wave (OLD).

Hypothesis: the crossover sits at a framework-natural distance —
possibly a φ-power of the home rung period, or some combination of φ and π
that converts between "delta-dominated" and "structured-dominated" regimes.

Outputs:
  - per-horizon corr for both methods on each system
  - crossover horizon (where ACT corr drops below OLD corr)
  - that horizon expressed in multiples of home period and in φ-powers
"""
import json, os, time
import numpy as np, pandas as pd
import wfdb
from scipy.signal import butter, sosfilt

PHI = 1.6180339887498949
HOME_K = 8

def _resolve(p):
    p_lin = p.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p

NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
SOI_PATH  = _resolve(r"F:\SystemFormulaFolder\SOI_NOAA\soi.data")
ECG_DIR   = _resolve(r"F:\SystemFormulaFolder\normal-sinus-rhythm-rr-interval-database-1.0.0")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\crossover_horizon_data.js")

def causal_bandpass(arr, period_units, bw=0.4, order=2):
    n = len(arr); f_c = 1.0/period_units; nyq = 0.5
    Wn_lo = max(1e-6, (1-bw)*f_c/nyq); Wn_hi = min(0.999, (1+bw)*f_c/nyq)
    if Wn_lo >= Wn_hi: return np.zeros(n)
    try:
        sos = butter(order, [Wn_lo, Wn_hi], btype='bandpass', output='sos')
        return sosfilt(sos, arr - np.mean(arr))
    except Exception:
        return np.zeros(n)

def measure_state(bp, period_units):
    p_int = max(2, int(period_units))
    if len(bp) < 2 * p_int + 5: return None
    last_cycle = bp[-p_int:]
    amp = float((np.max(last_cycle) - np.min(last_cycle)) / 2.0)
    if amp < 1e-9: return None
    v_now = float(bp[-1]); v_prev = float(bp[-2])
    norm = max(amp, 1e-9)
    ratio = max(-0.99, min(0.99, v_now / norm))
    th = np.arccos(ratio) * (-1 if (v_now - v_prev) > 0 else 1)
    return dict(amp=amp, theta=float(th), period=float(period_units))

def states_at_anchor(arr, t_anchor, RUNGS):
    states = []
    for k, p in RUNGS:
        if 4*p > t_anchor: continue
        bp = causal_bandpass(arr[:t_anchor], p)
        st = measure_state(bp, p)
        if st is None: continue
        st['k'] = k
        states.append(st)
    return states

def project_act(arr, t_anchor, h, RUNGS, cached_states=None):
    """Actual-values delta integration."""
    v_now = float(arr[t_anchor - 1])
    states = cached_states if cached_states is not None else states_at_anchor(arr, t_anchor, RUNGS)
    if not states: return v_now
    delta = 0.0
    for s in states:
        delta += s['amp'] * (np.cos(s['theta'] + 2*np.pi*h/s['period']) - np.cos(s['theta']))
    return v_now + delta

def amp_std50(bp):
    n_recent = min(50, len(bp))
    return float(np.std(bp[-n_recent:]) * np.sqrt(2)) + 1e-9

def old_states_at_anchor(arr, t_anchor, RUNGS, k_ref=HOME_K):
    arr_t = arr[:t_anchor]
    mean_t = float(np.mean(arr_t))
    pinned = []
    for k, p in RUNGS:
        if 4*p > t_anchor: continue
        bp = causal_bandpass(arr_t, p)
        a = amp_std50(bp)
        last = bp[-1]; rate = bp[-1] - bp[-2]
        ratio = max(-0.99, min(0.99, last/a))
        th = np.arccos(ratio) * (-1 if rate > 0 else 1)
        pinned.append(dict(p=p, amp=a, theta=th, k=k))
    if not pinned: return (mean_t, None, None)
    rung_w = np.array([PHI**(-abs(s['k'] - k_ref)) for s in pinned])
    rung_w = rung_w / rung_w.sum()
    return (mean_t, pinned, rung_w)

def project_old(arr, t_anchor, h, RUNGS, k_ref=HOME_K, cached=None):
    """Structured wave from training mean."""
    if cached is None:
        cached = old_states_at_anchor(arr, t_anchor, RUNGS, k_ref)
    mean_t, pinned, rung_w = cached
    if not pinned: return mean_t
    contrib = 0.0
    for j, s in enumerate(pinned):
        new_th = s['theta'] + 2*np.pi*h/s['p']
        contrib += rung_w[j] * s['amp'] * np.cos(new_th)
    return mean_t + contrib

def sweep_metrics(arr, anchors, horizons, RUNGS):
    metrics = {h: {'OLD': [], 'ACT': []} for h in horizons}
    N_arr = len(arr)
    for t_a in anchors:
        # cache states per anchor — reused across all horizons
        act_cache = states_at_anchor(arr, t_a, RUNGS)
        old_cache = old_states_at_anchor(arr, t_a, RUNGS)
        for h in horizons:
            if t_a + h - 1 >= N_arr: continue
            truth = float(arr[t_a + h - 1])
            metrics[h]['OLD'].append((project_old(arr, t_a, h, RUNGS, cached=old_cache), truth, float(arr[t_a-1])))
            metrics[h]['ACT'].append((project_act(arr, t_a, h, RUNGS, cached_states=act_cache), truth, float(arr[t_a-1])))
    out = {}
    for h in horizons:
        for method in ['OLD', 'ACT']:
            recs = metrics[h][method]
            if len(recs) < 5: continue
            preds = np.array([r[0] for r in recs])
            truths = np.array([r[1] for r in recs])
            pers = np.array([r[2] for r in recs])
            c = float(np.corrcoef(preds, truths)[0,1]) if np.std(preds) > 1e-9 else 0
            mae = float(np.mean(np.abs(preds-truths)))
            r2p = float(1 - np.sum((truths-preds)**2)/np.sum((truths-pers)**2))
            out[(h, method)] = dict(corr=c, mae=mae, r2p=r2p, n=int(len(recs)))
    return out

# === ENSO ===
print("Loading NINO + SOI...")
def load_nino():
    df = pd.read_csv(NINO_PATH, skiprows=1, header=None, names=['date','val'])
    df['date'] = pd.to_datetime(df['date'].str.strip())
    df = df[df['val'] > -90].copy()
    return df.set_index('date')['val'].astype(float)
def to_monthly(s):
    s = s.copy(); s.index = pd.to_datetime(s.index).to_period('M').to_timestamp()
    return s.groupby(s.index).first()
nino = to_monthly(load_nino())
NINO = nino.values.astype(float)
N_NINO = len(NINO)

ENSO_RUNGS = [(k, PHI**k) for k in range(3, 13)]
HOME_PERIOD_ENSO = PHI**HOME_K  # 47 months
print(f"  N={N_NINO} months, home period {HOME_PERIOD_ENSO:.1f} mo")

# Fine-grain horizons for ENSO: 1..36 months
ENSO_HORIZONS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 18, 21, 24, 28, 32, 36]
ENSO_ANCHORS = list(range(30*12, N_NINO - max(ENSO_HORIZONS), 3))
print(f"  {len(ENSO_ANCHORS)} ENSO anchors, sweeping {len(ENSO_HORIZONS)} horizons")

t0 = time.time()
enso_metrics = sweep_metrics(NINO, ENSO_ANCHORS, ENSO_HORIZONS, ENSO_RUNGS)
print(f"  ran in {time.time()-t0:.1f}s")

# === ECG (single subject for sharp crossover) ===
print("\nLoading ECG nsr001...")
ann = wfdb.rdann(os.path.join(ECG_DIR, 'nsr001'), 'ecg')
RR = np.diff(ann.sample) / ann.fs * 1000.0
RR = RR.astype(float)
N_RR = len(RR)
ECG_RUNGS = [(k, PHI**k) for k in range(2, 22)]
HOME_PERIOD_ECG = PHI**HOME_K  # 47 beats
print(f"  N={N_RR} beats, home period {HOME_PERIOD_ECG:.1f} beats")

ECG_HORIZONS = [1, 2, 3, 5, 8, 13, 21, 35, 50, 80, 130, 210, 350, 550, 900, 1500, 2500, 4000]
ECG_ANCHORS = list(range(20000, N_RR - max(ECG_HORIZONS), 5000))
print(f"  {len(ECG_ANCHORS)} ECG anchors, sweeping {len(ECG_HORIZONS)} horizons")

t0 = time.time()
ecg_metrics = sweep_metrics(RR, ECG_ANCHORS, ECG_HORIZONS, ECG_RUNGS)
print(f"  ran in {time.time()-t0:.1f}s")

# === Find crossover ===
def find_crossover(metrics, horizons, label):
    print(f"\n=== {label} crossover analysis ===")
    print(f"  {'h':>5}  {'ACT corr':>9}  {'OLD corr':>9}  {'ACT > OLD?':>11}")
    points = []
    for h in horizons:
        a = metrics.get((h, 'ACT'), {}).get('corr')
        o = metrics.get((h, 'OLD'), {}).get('corr')
        if a is None or o is None: continue
        flag = "yes" if a > o else "NO"
        print(f"  {h:>5}  {a:+.3f}     {o:+.3f}     {flag:>11}")
        points.append((h, a, o))
    crossover_h = None
    for i in range(1, len(points)):
        prev_h, prev_a, prev_o = points[i-1]
        h, a, o = points[i]
        if (prev_a > prev_o) and (a <= o):
            # linear interpolate the exact crossover horizon (in log space)
            d_prev = prev_a - prev_o
            d_now  = a - o
            frac = d_prev / (d_prev - d_now) if (d_prev - d_now) != 0 else 0.5
            log_cross = np.log(prev_h) + frac * (np.log(h) - np.log(prev_h))
            crossover_h = float(np.exp(log_cross))
            break
    if crossover_h:
        print(f"  → crossover at h ≈ {crossover_h:.1f}")
    else:
        print("  → no clean crossover in this range")
    return crossover_h, points

cross_enso, pts_enso = find_crossover(enso_metrics, ENSO_HORIZONS, "ENSO (months)")
cross_ecg,  pts_ecg  = find_crossover(ecg_metrics, ECG_HORIZONS,  "ECG (beats)")

# === Express in framework units ===
print(f"\n=== Crossover in framework-natural units ===")
if cross_enso:
    ratio = cross_enso / HOME_PERIOD_ENSO
    log_phi = np.log(cross_enso) / np.log(PHI)
    log_phi_ratio = np.log(ratio) / np.log(PHI)
    print(f"  ENSO: {cross_enso:.2f} mo")
    print(f"        / home period {HOME_PERIOD_ENSO:.2f} mo  =  {ratio:.4f}")
    print(f"        log_φ(crossover) = {log_phi:.3f}     (i.e., φ^{log_phi:.3f})")
    print(f"        log_φ(ratio)     = {log_phi_ratio:.3f}  (offset from home rung in φ-rungs)")
if cross_ecg:
    ratio = cross_ecg / HOME_PERIOD_ECG
    log_phi = np.log(cross_ecg) / np.log(PHI)
    log_phi_ratio = np.log(ratio) / np.log(PHI)
    print(f"  ECG:  {cross_ecg:.2f} beats")
    print(f"        / home period {HOME_PERIOD_ECG:.2f} beats  =  {ratio:.4f}")
    print(f"        log_φ(crossover) = {log_phi:.3f}")
    print(f"        log_φ(ratio)     = {log_phi_ratio:.3f}  (offset from home rung in φ-rungs)")

# === Are the offsets consistent? ===
if cross_enso and cross_ecg:
    off_enso = np.log(cross_enso / HOME_PERIOD_ENSO) / np.log(PHI)
    off_ecg  = np.log(cross_ecg  / HOME_PERIOD_ECG)  / np.log(PHI)
    print(f"\n  ENSO offset from home: {off_enso:+.3f} φ-rungs")
    print(f"  ECG  offset from home: {off_ecg:+.3f} φ-rungs")
    print(f"  difference: {abs(off_enso - off_ecg):.3f} φ-rungs")
    # framework-relevant references
    refs = [('-1/φ³', -1/PHI**3), ('-1/φ²', -1/PHI**2), ('-1/φ', -1/PHI),
            ('0', 0), ('+1/φ', 1/PHI), ('+1/φ²', 1/PHI**2), ('+1', 1),
            ('+φ', PHI), ('+φ²', PHI**2), ('+2', 2)]
    print("\n  Closest framework-natural offsets:")
    for sys_label, off in [('ENSO', off_enso), ('ECG', off_ecg)]:
        closest = min(refs, key=lambda r: abs(r[1] - off))
        print(f"    {sys_label}: {off:+.3f} → closest is {closest[0]} ({closest[1]:+.3f}, diff {abs(closest[1]-off):.3f})")

out = dict(
    enso=dict(home_period_mo=HOME_PERIOD_ENSO, crossover_h=cross_enso, points=pts_enso, metrics={f"{h}_{m}":enso_metrics[(h,m)] for h,m in enso_metrics}),
    ecg=dict(home_period_beats=HOME_PERIOD_ECG, crossover_h=cross_ecg, points=pts_ecg, metrics={f"{h}_{m}":ecg_metrics[(h,m)] for h,m in ecg_metrics}),
)
with open(OUT, 'w') as f:
    f.write("window.CROSSOVER = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
