"""
Rolling vehicle — ECG amplitude template on ENSO+SOI closed system.

Combines two validated framework claims:
  1. CLOSED-SYSTEM coupling (SOI matched-rung anti-phase pair at φ⁸)
     - Validated 2026-05-02: lifts h=6/h=12 from negative to positive
  2. VERTICAL ARA cross-domain template
     - Validated 2026-05-02: ECG profile matches ENSO profile within ±2 rungs of peak (corr +0.695)

The ECG profile is a CLEANER estimate of the universal cycle amplitude shape
(thousands of cycles in 22.5h vs ~16 cycles in 75 years of ENSO data).
Use ECG's profile as a STRUCTURAL PRIOR for ENSO's per-rung amplitudes.

Three blend levels:
  α=0.0  pure observed amplitudes (= SOI_MATCHED baseline)
  α=0.5  blended observed + ECG template
  α=1.0  pure ECG template
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
SOI_PATH  = _resolve(r"F:\SystemFormulaFolder\SOI_NOAA\soi.data")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\rolling_vehicle_ecg_template_data.js")

# ===== ECG amplitude profile (from ecg_template_for_enso_test.py, run 2026-05-02) =====
# Normalized to peak (k_ecg=19, ECG BRAC envelope). rel_k = k - peak.
# These values come from causal Butterworth bandpass on 22.5h of nsr001 RR-interval data.
ECG_PROFILE = {
    -19: 0.000,  # k=0 heartbeat — nearly zero amplitude relative to slow envelope
    -18: 0.177,
    -17: 0.361,
    -16: 0.467,
    -15: 0.452,
    -14: 0.507,
    -13: 0.553,
    -12: 0.583,
    -11: 0.599,
    -10: 0.613,
     -9: 0.654,
     -8: 0.690,
     -7: 0.712,
     -6: 0.741,
     -5: 0.773,
     -4: 0.823,
     -3: 0.807,
     -2: 0.797,
     -1: 0.984,
      0: 1.000,
     +1: 0.774,
}
# Beyond +1, mirror reflection from negative side (assume symmetry, conservative)
def ecg_template_value(rel_k):
    if rel_k in ECG_PROFILE:
        return ECG_PROFILE[rel_k]
    if rel_k > 1 and -rel_k in ECG_PROFILE:  # mirror
        return ECG_PROFILE[-rel_k]
    return 0.5  # fallback

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
def load_soi():
    rows=[]
    with open(SOI_PATH) as f:
        next(f)
        for ln in f:
            parts = ln.split()
            if len(parts) < 13: continue
            try: year = int(parts[0])
            except: continue
            if year < 1900 or year > 2100: continue
            for m in range(12):
                try: v = float(parts[1+m])
                except: continue
                if v < -90: continue
                rows.append((pd.Timestamp(year=year, month=m+1, day=1), v))
    return pd.Series(dict(rows)).sort_index()

print("Loading...")
nino = load_nino()
amo = load_grid_text(AMO_PATH); tna = load_grid_text(TNA_PATH)
pdo = load_grid_text(PDO_PATH, header_lines=2); iod = load_iod()
soi = load_soi()

def to_monthly(s):
    s = s.copy(); s.index = pd.to_datetime(s.index).to_period('M').to_timestamp()
    return s.groupby(s.index).first()
nino = to_monthly(nino); amo = to_monthly(amo); tna = to_monthly(tna)
pdo = to_monthly(pdo); iod = to_monthly(iod); soi = to_monthly(soi)
common = nino.index
for s in [amo, tna, pdo, iod, soi]:
    common = common.intersection(s.index)
common = common.sort_values()
NINO = nino.reindex(common).values.astype(float)
AMO  = amo.reindex(common).values.astype(float)
TNA  = tna.reindex(common).values.astype(float)
PDO  = pdo.reindex(common).values.astype(float)
IOD  = iod.reindex(common).values.astype(float)
SOI  = soi.reindex(common).values.astype(float)
DATES = common; N = len(NINO)
print(f"  N={N} months common, {DATES[0].date()} to {DATES[-1].date()}")

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
K_REF_IDX = next(i for i,(k,_) in enumerate(RUNGS) if k == K_REF)
RUNG_WEIGHTS = np.array([PHI**(-abs(k - K_REF)) for k,_ in RUNGS])
RUNG_WEIGHTS = RUNG_WEIGHTS / np.sum(RUNG_WEIGHTS)

# ECG template applied to ENSO rungs: rel_k = k - K_REF
ECG_AMP_TEMPLATE = np.array([ecg_template_value(k - K_REF) for k,_ in RUNGS])
print(f"\nECG amplitude template applied to ENSO rungs (peak at φ⁸):")
for i, (k, p) in enumerate(RUNGS):
    rel_k = k - K_REF
    print(f"  k={k:>2} (rel {rel_k:+d}) P={p:>7.1f}mo  ECG_template={ECG_AMP_TEMPLATE[i]:.3f}")

def vehicle(refit_t, h, last_residual, alpha):
    """alpha: 0.0=observed, 0.5=blend, 1.0=pure ECG template"""
    arr_train = NINO[:refit_t]
    mean_train = float(np.mean(arr_train))
    nino_scale = float(np.std(arr_train)) + 1e-9
    soi_scale = float(np.std(SOI[:refit_t])) + 1e-9

    SYS_local = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD, SOI=SOI)
    feeders = ['AMO','TNA','PDO','IOD','SOI']
    feeder_signs = dict(AMO=+1, TNA=+1, PDO=-1, IOD=+1, SOI=-1)

    bp = {}
    for nm in SYS_local:
        bp[nm] = [causal_bandpass(SYS_local[nm][:refit_t], p) for k,p in RUNGS]

    state = {}
    for nm in SYS_local:
        for ri, (k, p) in enumerate(RUNGS):
            a, th = read_amp_theta(bp[nm][ri])
            ara = per_rung_ARA_causal(SYS_local[nm][:refit_t], p) if nm == 'NINO' else 1.0
            state[(nm, ri)] = (a, th, ara)

    # Apply ECG amplitude template to NINO's per-rung amplitudes
    # Base = NINO's observed amplitude at home rung (k=8)
    base_amp_nino = state[('NINO', K_REF_IDX)][0]
    if alpha > 0:
        for ri in range(N_RUNGS):
            obs_amp, th, ara = state[('NINO', ri)]
            template_amp = base_amp_nino * ECG_AMP_TEMPLATE[ri]
            blended_amp = (1-alpha) * obs_amp + alpha * template_amp
            state[('NINO', ri)] = (blended_amp, th, ara)

    # Forward project all rungs
    nino_rung_future = []
    feeder_rung_future = {fn: [] for fn in feeders}
    for ri, (k, p) in enumerate(RUNGS):
        a_n, th_n, ara_n = state[('NINO', ri)]
        new_th_n = th_n + 2*np.pi*h/p
        kappa = 0.05
        decay_n = np.exp(-abs(ara_n - PHI) * h / p * kappa)
        nino_rung_future.append(a_n * decay_n * np.cos(new_th_n))
        for fn in feeders:
            a_f, th_f, _ = state[(fn, ri)]
            new_th_f = th_f + 2*np.pi*h/p
            feeder_rung_future[fn].append(a_f * np.cos(new_th_f))
    nino_rung_future = np.array(nino_rung_future)
    own_pred = float(np.dot(RUNG_WEIGHTS, nino_rung_future))

    # SOI = matched-rung pair (full weight at φ⁸); other feeders = 1/φ⁴ blend
    feeder_pred = 0.0
    for fn in feeders:
        feeder_arr = np.array(feeder_rung_future[fn])
        sign = feeder_signs[fn]
        f_scale = float(np.std(SYS_local[fn][:refit_t])) + 1e-9
        feeder_arr_norm = feeder_arr / f_scale * nino_scale

        if fn == 'SOI':
            soi_at_match = feeder_arr_norm[K_REF_IDX]
            feeder_pred += sign * 1.0 * soi_at_match * RUNG_WEIGHTS[K_REF_IDX] * 5
            for ri in range(N_RUNGS):
                if ri == K_REF_IDX: continue
                feeder_pred += sign * (1.0/PHI**abs(RUNGS[ri][0]-K_REF)) * INV_PHI4 * feeder_arr_norm[ri] * RUNG_WEIGHTS[ri]
        else:
            feeder_pred += INV_PHI4 * sign * float(np.dot(RUNG_WEIGHTS, feeder_arr_norm)) / 4.0

    structural_pred = mean_train + own_pred + feeder_pred
    pred = structural_pred + INV_PHI3 * last_residual
    truth = NINO[refit_t + h - 1]
    return pred, truth

# ===== Rolling loop =====
HORIZONS = [1, 3, 6, 12, 24]
MIN_TRAIN = 30 * 12
STEP = 12
print(f"\n  Rolling closed-system vehicle (ENSO+SOI) with ECG amplitude template")

results_by_alpha = {}
for alpha in [0.0, 0.3, 0.5, 0.7, 1.0]:
    print(f"\n--- α = {alpha} ---")
    if alpha == 0: print("  Pure observed amplitudes (= SOI_MATCHED baseline)")
    elif alpha == 1.0: print("  Pure ECG amplitude template")
    else: print(f"  Blend: {(1-alpha)*100:.0f}% observed + {alpha*100:.0f}% ECG template")

    results = {h: [] for h in HORIZONS}
    last_residual = 0.0
    t_start = time.time()
    for refit_t in range(MIN_TRAIN, N - max(HORIZONS), STEP):
        for h in HORIZONS:
            if refit_t + h - 1 >= N: continue
            pred, truth = vehicle(refit_t, h, last_residual, alpha)
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
    results_by_alpha[str(alpha)] = metrics

out = dict(method="ENSO+SOI closed-system vehicle + ECG amplitude template (alpha blend)",
           ecg_template={int(k):v for k,v in ECG_PROFILE.items()},
           results_by_alpha=results_by_alpha)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.VEHICLE_ECG_TEMPLATE = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
