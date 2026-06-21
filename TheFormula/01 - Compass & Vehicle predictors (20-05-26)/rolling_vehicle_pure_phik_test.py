"""
Rolling vehicle PURE + φ^k amplitude scaling — framework constants only.

Adds the ECG-validated φ^k amplitude rule as a structural constant:
  amp(rung k) = base × φ^(k − k_ref)   for k ≥ k_ref
  amp(rung k) = base × φ^(k_ref − k)  for k < k_ref  (mirror — peak at home)

Test BOTH forms:
  V_PHIK_RISE: amp grows as φ^(k-k_ref) — ECG rule (longer period = bigger)
  V_PHIK_PEAK: amp peaks at k_ref, falls as φ^(-|k-k_ref|) — home rung dominant

Single base amplitude, measured at k_ref, propagated to all rungs by the rule.
NO regression, NO learning. Pure structural constraint.
"""
import json, os, time
import numpy as np, pandas as pd
from scipy.signal import butter, lfilter, find_peaks
from scipy.ndimage import gaussian_filter1d

PHI = 1.6180339887498949
INV_PHI3 = 1.0 / (PHI**3)
INV_PHI4 = 1.0 / (PHI**4)

def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
AMO_PATH  = _resolve(r"F:\SystemFormulaFolder\HURDAT2\Temp\amonuslong.txt")
TNA_PATH  = _resolve(r"F:\SystemFormulaFolder\HURDAT2\Temp\tna.txt")
PDO_PATH  = _resolve(r"F:\SystemFormulaFolder\PDO_NOAA\ersst.v5.pdo.dat")
IOD_PATH  = _resolve(r"F:\SystemFormulaFolder\IOD_NOAA\dmi.had.long.data")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\rolling_vehicle_pure_phik_data.js")

def load_nino():
    df = pd.read_csv(NINO_PATH, skiprows=1, header=None, names=['date','val'])
    df['date'] = pd.to_datetime(df['date'].str.strip())
    df = df[df['val'] > -90].copy()
    return df.set_index('date')['val'].astype(float)
def load_grid_text(path, header_lines=1):
    rows=[]
    with open(path,'r') as f:
        for _ in range(header_lines): next(f)
        for ln in f:
            parts = ln.split()
            if len(parts) < 13: continue
            try: year = int(parts[0])
            except: continue
            for m in range(12):
                try: v = float(parts[1+m])
                except: continue
                if v < -90 or v > 90: continue
                rows.append((pd.Timestamp(year=year, month=m+1, day=1), v))
    return pd.Series(dict(rows)).sort_index()
def load_iod():
    rows=[]
    with open(IOD_PATH,'r') as f:
        next(f)
        for ln in f:
            parts = ln.split()
            if len(parts) < 13: continue
            try: year = int(parts[0])
            except: continue
            for m in range(12):
                try: v = float(parts[1+m])
                except: continue
                if v < -90 or v > 90: continue
                rows.append((pd.Timestamp(year=year, month=m+1, day=1), v))
    return pd.Series(dict(rows)).sort_index()

print("Loading...")
nino = load_nino()
amo = load_grid_text(AMO_PATH); tna = load_grid_text(TNA_PATH)
pdo = load_grid_text(PDO_PATH, header_lines=2); iod = load_iod()
def to_monthly(s):
    s = s.copy(); s.index = pd.to_datetime(s.index).to_period('M').to_timestamp()
    return s.groupby(s.index).first()
nino = to_monthly(nino); amo = to_monthly(amo); tna = to_monthly(tna)
pdo = to_monthly(pdo); iod = to_monthly(iod)
common = nino.index
for s in [amo, tna, pdo, iod]:
    common = common.intersection(s.index)
common = common.sort_values()
NINO = nino.reindex(common).values.astype(float)
AMO  = amo.reindex(common).values.astype(float)
TNA  = tna.reindex(common).values.astype(float)
PDO  = pdo.reindex(common).values.astype(float)
IOD  = iod.reindex(common).values.astype(float)
DATES = common; N = len(NINO)
print(f"  N={N} months, {DATES[0].date()} to {DATES[-1].date()}")

def causal_bandpass(arr, period_units, bw=0.4, order=2):
    n = len(arr); f_c = 1.0/period_units; nyq = 0.5
    Wn_lo = max(1e-6, (1-bw)*f_c/nyq); Wn_hi = min(0.999, (1+bw)*f_c/nyq)
    if Wn_lo >= Wn_hi: return np.zeros(n)
    try:
        b, a = butter(order, [Wn_lo, Wn_hi], btype='bandpass')
        return lfilter(b, a, arr - np.mean(arr))
    except Exception:
        return np.zeros(n)

def read_amp_theta(bp_to_t):
    if len(bp_to_t) < 2: return 0.0, 0.0
    n_recent = min(50, len(bp_to_t))
    amp = float(np.std(bp_to_t[-n_recent:]) * np.sqrt(2)) + 1e-9
    last = bp_to_t[-1]; rate = bp_to_t[-1] - bp_to_t[-2]
    ratio = max(-0.99, min(0.99, last/amp))
    return amp, np.arccos(ratio) * (-1 if rate > 0 else 1)

def per_rung_ARA_causal(arr_train, period):
    bp = causal_bandpass(arr_train, period, bw=0.85)
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

# ===== FRAMEWORK CONSTANTS =====
RUNGS = [(k, PHI**k) for k in range(4, 14)]
N_RUNGS = len(RUNGS)
K_REF = 8

# Per-rung influence weight: 1/φ^|k-k_ref|  (vertical-ARA / river prediction)
RUNG_WEIGHTS = np.array([PHI**(-abs(k - K_REF)) for k,_ in RUNGS])
RUNG_WEIGHTS = RUNG_WEIGHTS / np.sum(RUNG_WEIGHTS)

# φ^k amplitude scaling (TWO forms tested)
# Form RISE: amp(k) = base × φ^(k-K_REF) — ECG-style, longer period bigger
PHIK_RISE_AMP = np.array([PHI**(k - K_REF) for k,_ in RUNGS])
# Form PEAK: amp(k) = base × φ^(-|k-K_REF|) — home rung dominant, both sides decay
PHIK_PEAK_AMP = np.array([PHI**(-abs(k - K_REF)) for k,_ in RUNGS])

FEEDER_SIGNS = dict(AMO=+1, TNA=+1, PDO=-1, IOD=+1)
SYS = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD)
FEEDERS = ['AMO','TNA','PDO','IOD']

def vehicle_pure_phik(refit_t, h, last_residual, amp_scaling):
    """amp_scaling: 'NONE' | 'RISE' | 'PEAK'"""
    arr_train = NINO[:refit_t]
    mean_train = float(np.mean(arr_train))
    bp = {}
    for nm in SYS:
        bp[nm] = [causal_bandpass(SYS[nm][:refit_t], p) for k,p in RUNGS]

    # Read amp & phase at all rungs
    state = {}
    for nm in SYS:
        for ri, (k, p) in enumerate(RUNGS):
            a, th = read_amp_theta(bp[nm][ri])
            ara = per_rung_ARA_causal(SYS[nm][:refit_t], p) if nm == 'NINO' else 1.0
            state[(nm, ri)] = (a, th, ara)

    # Apply φ^k amplitude scaling — replace observed amplitudes with structural ones
    if amp_scaling != 'NONE':
        # Use the observed amplitude at k_ref as the base, rescale others structurally
        ref_idx = next(i for i,(k,_) in enumerate(RUNGS) if k == K_REF)
        for nm in SYS:
            base_amp = state[(nm, ref_idx)][0]
            scale = PHIK_RISE_AMP if amp_scaling == 'RISE' else PHIK_PEAK_AMP
            for ri in range(N_RUNGS):
                _, th, ara = state[(nm, ri)]
                state[(nm, ri)] = (base_amp * scale[ri], th, ara)

    # Forward project
    nino_rung_future = []
    feeder_rung_future = {fn: [] for fn in FEEDERS}
    for ri, (k, p) in enumerate(RUNGS):
        a_n, th_n, ara_n = state[('NINO', ri)]
        new_th_n = th_n + 2*np.pi*h/p
        kappa = 0.05
        decay_n = np.exp(-abs(ara_n - PHI) * h / p * kappa)
        nino_rung_future.append(a_n * decay_n * np.cos(new_th_n))
        for fn in FEEDERS:
            a_f, th_f, _ = state[(fn, ri)]
            new_th_f = th_f + 2*np.pi*h/p
            feeder_rung_future[fn].append(a_f * np.cos(new_th_f))
    nino_rung_future = np.array(nino_rung_future)

    own_pred = float(np.dot(RUNG_WEIGHTS, nino_rung_future))
    feeder_pred = 0.0
    for fn in FEEDERS:
        feeder_arr = np.array(feeder_rung_future[fn])
        sign = FEEDER_SIGNS[fn]
        feeder_pred += INV_PHI4 * sign * float(np.dot(RUNG_WEIGHTS, feeder_arr)) / len(FEEDERS)

    structural_pred = mean_train + own_pred + feeder_pred
    pred = structural_pred + INV_PHI3 * last_residual
    truth = NINO[refit_t + h - 1]
    return pred, truth

# ===== Rolling loop =====
HORIZONS = [1, 3, 6, 12, 24]
MIN_TRAIN = 30 * 12
STEP = 12

print(f"\n  Rolling pure vehicle with φ^k amplitude scaling — 3 variants")
print(f"  K_REF = φ^{K_REF} (ENSO home rung)")

results_by_variant = {}
for variant in ['NONE', 'RISE', 'PEAK']:
    print(f"\n--- amp_scaling = {variant} ---")
    if variant == 'RISE':
        print(f"  amp(k) = base × φ^(k-{K_REF})  →  longer-period rungs scaled UP (×φ⁵ at k=13)")
    elif variant == 'PEAK':
        print(f"  amp(k) = base × φ^(-|k-{K_REF}|)  →  amplitude peaked at home rung")
    else:
        print(f"  observed amplitudes (no structural override)")

    results = {h: [] for h in HORIZONS}
    last_residual = 0.0
    t_start = time.time()
    for refit_t in range(MIN_TRAIN, N - max(HORIZONS), STEP):
        for h in HORIZONS:
            if refit_t + h - 1 >= N: continue
            pred, truth = vehicle_pure_phik(refit_t, h, last_residual, variant)
            results[h].append((refit_t, pred, truth))
        if results[1]:
            last_residual = float(results[1][-1][2] - results[1][-1][1])
    print(f"  {time.time()-t_start:.1f}s")

    print(f"  {'horizon':>10}  {'corr':>7}  {'MAE':>7}  {'R²(clim)':>9}  {'R²(pers)':>9}  {'dir':>6}")
    metrics = {}
    clim_pred = float(np.mean(NINO))
    for h in HORIZONS:
        if not results[h]: continue
        preds = np.array([r[1] for r in results[h]])
        truths = np.array([r[2] for r in results[h]])
        pers_preds = np.array([NINO[r[0]-1] for r in results[h]])
        corr = float(np.corrcoef(preds, truths)[0,1]) if np.std(preds)>1e-9 and np.std(truths)>1e-9 else 0.0
        mae = float(np.mean(np.abs(preds - truths)))
        ss_res = np.sum((truths - preds)**2)
        ss_clim = np.sum((truths - clim_pred)**2)
        ss_pers = np.sum((truths - pers_preds)**2)
        r2_clim = float(1 - ss_res/ss_clim) if ss_clim > 0 else 0.0
        r2_pers = float(1 - ss_res/ss_pers) if ss_pers > 0 else 0.0
        dir_acc = float(np.mean(np.sign(preds - pers_preds) == np.sign(truths - pers_preds)))
        print(f"  h={h:>2} mo  {corr:+.3f}  {mae:.3f}    {r2_clim:+.3f}    {r2_pers:+.3f}    {dir_acc*100:5.1f}%")
        metrics[h] = dict(corr=corr, mae=mae, r2_clim=r2_clim, r2_pers=r2_pers, dir_acc=dir_acc, n=len(results[h]))
    results_by_variant[variant] = metrics

out = dict(method="Pure structure + φ^k amplitude scaling test",
           variants=dict(NONE='no override', RISE=f'φ^(k-{K_REF})', PEAK=f'φ^(-|k-{K_REF}|)'),
           results_by_variant=results_by_variant)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.VEHICLE_PURE_PHIK = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
