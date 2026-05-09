"""
Rolling vehicle PURE + QBO atmospheric coupling — tests "closing the system".

Adds QBO (Quasi-Biennial Oscillation, stratospheric zonal wind, ~28mo period)
as an atmospheric system coupled to ENSO. QBO sits at φ⁷, ENSO at φ⁸ (adjacent
rungs). Framework predicts adjacent-rung pipe coupling.

Three variants:
  V_BASE: ocean only (NINO, AMO, TNA, PDO, IOD) — same as rolling_vehicle_pure_test
  V_QBO_PLUS: + QBO coupled with sign +1
  V_QBO_MINUS: + QBO coupled with sign -1

If "closing the system" is right, adding atmospheric QBO should improve magnitude
prediction at long lead — especially R²(clim) and correlation, which were the
weakest metrics in the pure ocean-only vehicle.
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
QBO_PATH  = _resolve(r"F:\SystemFormulaFolder\QBO_NOAA\qbo.data")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\rolling_vehicle_qbo_data.js")

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
def load_qbo():
    rows=[]
    with open(QBO_PATH,'r') as f:
        first = f.readline()  # year range header
        for ln in f:
            parts = ln.split()
            if len(parts) < 13: continue
            try: year = int(parts[0])
            except: continue
            if year < 1900 or year > 2100: continue
            for m in range(12):
                try: v = float(parts[1+m])
                except: continue
                if v < -200 or v > 200: continue
                rows.append((pd.Timestamp(year=year, month=m+1, day=1), v))
    return pd.Series(dict(rows)).sort_index()

print("Loading...")
nino = load_nino()
amo = load_grid_text(AMO_PATH); tna = load_grid_text(TNA_PATH)
pdo = load_grid_text(PDO_PATH, header_lines=2); iod = load_iod()
qbo = load_qbo()
print(f"  QBO: {len(qbo)} months, {qbo.index[0].date()} to {qbo.index[-1].date()}")

def to_monthly(s):
    s = s.copy(); s.index = pd.to_datetime(s.index).to_period('M').to_timestamp()
    return s.groupby(s.index).first()
nino = to_monthly(nino); amo = to_monthly(amo); tna = to_monthly(tna)
pdo = to_monthly(pdo); iod = to_monthly(iod); qbo = to_monthly(qbo)
common = nino.index
for s in [amo, tna, pdo, iod, qbo]:
    common = common.intersection(s.index)
common = common.sort_values()
NINO = nino.reindex(common).values.astype(float)
AMO  = amo.reindex(common).values.astype(float)
TNA  = tna.reindex(common).values.astype(float)
PDO  = pdo.reindex(common).values.astype(float)
IOD  = iod.reindex(common).values.astype(float)
QBO  = qbo.reindex(common).values.astype(float)
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
RUNG_WEIGHTS = np.array([PHI**(-abs(k - K_REF)) for k,_ in RUNGS])
RUNG_WEIGHTS = RUNG_WEIGHTS / np.sum(RUNG_WEIGHTS)

# Feeder signs from framework geometry
# PDO at φ⁸ = matched-rung mirror of ENSO → -1
# AMO/TNA/IOD = same-side ocean basins → +1
# QBO at φ⁷ = atmospheric, ADJACENT rung → tested both signs
FEEDER_SIGNS_BASE = dict(AMO=+1, TNA=+1, PDO=-1, IOD=+1)

def vehicle(refit_t, h, last_residual, qbo_sign):
    """qbo_sign in {0 (no QBO), +1, -1}"""
    arr_train = NINO[:refit_t]
    mean_train = float(np.mean(arr_train))

    # Choose feeder set
    feeder_signs = dict(FEEDER_SIGNS_BASE)
    if qbo_sign != 0:
        feeder_signs['QBO'] = qbo_sign
    SYS_local = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD)
    if qbo_sign != 0:
        SYS_local['QBO'] = QBO
    feeders = [k for k in SYS_local if k != 'NINO']

    bp = {}
    for nm in SYS_local:
        bp[nm] = [causal_bandpass(SYS_local[nm][:refit_t], p) for k,p in RUNGS]

    # State at end of training data
    state = {}
    for nm in SYS_local:
        for ri, (k, p) in enumerate(RUNGS):
            a, th = read_amp_theta(bp[nm][ri])
            ara = per_rung_ARA_causal(SYS_local[nm][:refit_t], p) if nm == 'NINO' else 1.0
            state[(nm, ri)] = (a, th, ara)

    # Forward project
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

    feeder_pred = 0.0
    for fn in feeders:
        feeder_arr = np.array(feeder_rung_future[fn])
        sign = feeder_signs[fn]
        # Normalise QBO scale (it's m/s, much larger than SST anomalies)
        if fn == 'QBO':
            qbo_norm = float(np.std(QBO[:refit_t])) + 1e-9
            feeder_arr = feeder_arr / qbo_norm * float(np.std(NINO[:refit_t]))
        feeder_pred += INV_PHI4 * sign * float(np.dot(RUNG_WEIGHTS, feeder_arr)) / len(feeders)

    structural_pred = mean_train + own_pred + feeder_pred
    pred = structural_pred + INV_PHI3 * last_residual
    truth = NINO[refit_t + h - 1]
    return pred, truth

# ===== Rolling loop =====
HORIZONS = [1, 3, 6, 12, 24]
MIN_TRAIN = 30 * 12
STEP = 12
print(f"\n  Rolling pure vehicle, with/without QBO atmospheric coupling")
print(f"  RUNG_WEIGHTS shape: {RUNG_WEIGHTS}")

results_by_variant = {}
for variant_name, qbo_sign in [('BASE', 0), ('QBO_PLUS', +1), ('QBO_MINUS', -1)]:
    print(f"\n--- {variant_name} ---")
    if qbo_sign == 0: print("  No QBO — ocean only")
    else: print(f"  QBO coupled at sign {qbo_sign:+d}")

    results = {h: [] for h in HORIZONS}
    last_residual = 0.0
    t_start = time.time()
    for refit_t in range(MIN_TRAIN, N - max(HORIZONS), STEP):
        for h in HORIZONS:
            if refit_t + h - 1 >= N: continue
            pred, truth = vehicle(refit_t, h, last_residual, qbo_sign)
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
    results_by_variant[variant_name] = metrics

out = dict(method="Pure vehicle + QBO atmospheric coupling test",
           variants=dict(BASE='ocean only', QBO_PLUS='+ QBO sign +1', QBO_MINUS='+ QBO sign -1'),
           results_by_variant=results_by_variant)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.VEHICLE_QBO = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
