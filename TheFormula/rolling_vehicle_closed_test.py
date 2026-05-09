"""
Rolling vehicle PURE + SOI (closed-system test).

ENSO and SOI are two halves of the same Walker Circulation oscillation,
matched-rung anti-phase pair at φ⁸. Together they form a CLOSED system in
the framework sense. The framework predicts:
  - SOI coupling sign = −1 (anti-phase)
  - SOI strength at matched rung (φ⁸) is full, not the 1/φ⁴ blend used for
    incidental feeders. Use 1.0 weight at the matched rung.
  - Adding SOI should improve amplitude prediction at all horizons because
    we're now modeling both halves of the energy exchange.

Variants:
  V_BASE:         Ocean-only pure vehicle (NINO + AMO + TNA + PDO + IOD)
  V_SOI_BLEND:    + SOI with 1/φ⁴ blend (treat as one more feeder)
  V_SOI_MATCHED:  + SOI with FULL matched-rung weight at φ⁸ (proper closed-system)
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
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\rolling_vehicle_closed_data.js")

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
print(f"  SOI: {len(soi)} months, {soi.index[0].date()} to {soi.index[-1].date()}")

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

def vehicle(refit_t, h, last_residual, mode):
    """mode: 'BASE' | 'SOI_BLEND' | 'SOI_MATCHED'"""
    arr_train = NINO[:refit_t]
    mean_train = float(np.mean(arr_train))
    n_train = float(np.std(arr_train)) + 1e-9

    SYS_local = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD)
    feeders = ['AMO','TNA','PDO','IOD']
    feeder_signs = dict(AMO=+1, TNA=+1, PDO=-1, IOD=+1)

    if mode != 'BASE':
        SYS_local['SOI'] = SOI
        feeders.append('SOI')
        feeder_signs['SOI'] = -1  # framework: anti-phase matched-rung mirror

    bp = {}
    for nm in SYS_local:
        bp[nm] = [causal_bandpass(SYS_local[nm][:refit_t], p) for k,p in RUNGS]

    state = {}
    for nm in SYS_local:
        for ri, (k, p) in enumerate(RUNGS):
            a, th = read_amp_theta(bp[nm][ri])
            ara = per_rung_ARA_causal(SYS_local[nm][:refit_t], p) if nm == 'NINO' else 1.0
            state[(nm, ri)] = (a, th, ara)

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

    # Feeder contributions — distinguish SOI in MATCHED mode
    feeder_pred = 0.0
    for fn in feeders:
        feeder_arr = np.array(feeder_rung_future[fn])
        sign = feeder_signs[fn]
        # Normalise by feeder's own scale, scale to NINO units
        f_scale = float(np.std(SYS_local[fn][:refit_t])) + 1e-9
        feeder_arr_norm = feeder_arr / f_scale * n_train

        if fn == 'SOI' and mode == 'SOI_MATCHED':
            # FULL matched-rung weight — only at φ⁸ (closed-system anti-phase)
            # ENSO + SOI together = closed loop. SOI provides the OTHER HALF
            # of the wave at this rung.
            soi_at_match = feeder_arr_norm[K_REF_IDX]
            feeder_pred += sign * 1.0 * soi_at_match * RUNG_WEIGHTS[K_REF_IDX] * 5
            # Plus secondary contributions at adjacent rungs with reduced weight
            for ri in range(N_RUNGS):
                if ri == K_REF_IDX: continue
                feeder_pred += sign * (1.0/PHI**abs(RUNGS[ri][0]-K_REF)) * INV_PHI4 * feeder_arr_norm[ri] * RUNG_WEIGHTS[ri]
        else:
            # Standard blend (incidental feeder)
            feeder_pred += INV_PHI4 * sign * float(np.dot(RUNG_WEIGHTS, feeder_arr_norm)) / len(feeders)

    structural_pred = mean_train + own_pred + feeder_pred
    pred = structural_pred + INV_PHI3 * last_residual
    truth = NINO[refit_t + h - 1]
    return pred, truth

# ===== Rolling loop =====
HORIZONS = [1, 3, 6, 12, 24]
MIN_TRAIN = 30 * 12
STEP = 12
print(f"\n  Rolling pure vehicle, closed-system test (with/without SOI)")

results_by_variant = {}
for mode in ['BASE', 'SOI_BLEND', 'SOI_MATCHED']:
    print(f"\n--- {mode} ---")
    if mode == 'BASE': print("  Ocean only (no SOI)")
    elif mode == 'SOI_BLEND': print("  + SOI as standard feeder (1/φ⁴ blend)")
    else: print("  + SOI as MATCHED-RUNG closed-system pair (full weight at φ⁸)")

    results = {h: [] for h in HORIZONS}
    last_residual = 0.0
    t_start = time.time()
    for refit_t in range(MIN_TRAIN, N - max(HORIZONS), STEP):
        for h in HORIZONS:
            if refit_t + h - 1 >= N: continue
            pred, truth = vehicle(refit_t, h, last_residual, mode)
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
    results_by_variant[mode] = metrics

out = dict(method="Pure vehicle + SOI closed-system test",
           variants=dict(BASE='ocean only',
                         SOI_BLEND='+SOI 1/φ⁴ blend',
                         SOI_MATCHED='+SOI full matched-rung at φ⁸'),
           nino_soi_correlation=-0.72,
           results_by_variant=results_by_variant)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.VEHICLE_CLOSED = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
