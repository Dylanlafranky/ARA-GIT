"""
Rolling vehicle PURE — framework constants only. No regression. No learned weights.

The formula is a deterministic map from current state to next state, using only:
  - φ = 1.618...
  - 1/φ³ ≈ 0.236   (AR feedback constant, validated on ECG)
  - 1/φ^|k−k_ref|  (per-rung amplitude weights — vertical ARA / river prediction)
  - φ⁻|ARA−φ| × κ (amplitude decay per rung from unified φ-pressure engine)
  - Matched-rung coupling signs from framework geometry (PDO–ENSO anti-phase at φ⁸)

Procedure at each refit time t:
  1. Causal bandpass on training data only — observe each (system, rung) amp & phase.
  2. Forward project deterministically using framework rules.
  3. Sum across rungs with framework-given weights (1/φ^|k−k_ref|).
  4. Apply AR feedback at exactly γ=1/φ³ from the previous month's residual.
  5. Compare prediction to truth.

NO REGRESSION ANYWHERE. Only framework constants and observed state.

The framework's claim under test:
  "Once the topology and current state are known, the time-geometry tells you
   what comes next. No learning needed."
"""
import json, os, time
import numpy as np, pandas as pd
from scipy.signal import butter, lfilter, find_peaks
from scipy.ndimage import gaussian_filter1d

PHI = 1.6180339887498949
INV_PHI3 = 1.0 / (PHI**3)

def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
AMO_PATH  = _resolve(r"F:\SystemFormulaFolder\HURDAT2\Temp\amonuslong.txt")
TNA_PATH  = _resolve(r"F:\SystemFormulaFolder\HURDAT2\Temp\tna.txt")
PDO_PATH  = _resolve(r"F:\SystemFormulaFolder\PDO_NOAA\ersst.v5.pdo.dat")
IOD_PATH  = _resolve(r"F:\SystemFormulaFolder\IOD_NOAA\dmi.had.long.data")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\rolling_vehicle_pure_data.js")

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
    n = len(arr)
    f_c = 1.0/period_units; nyq = 0.5
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
    last = bp_to_t[-1]
    rate = bp_to_t[-1] - bp_to_t[-2]
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
K_REF = 8  # ENSO home rung at φ⁸

# Per-rung weight from framework: 1/φ^|k-k_ref|  (vertical ARA / river prediction memory)
RUNG_WEIGHTS = np.array([PHI**(-abs(k - K_REF)) for k,_ in RUNGS])
# Normalise so sum to 1
RUNG_WEIGHTS = RUNG_WEIGHTS / np.sum(RUNG_WEIGHTS)

# Feeder-to-NINO sign convention from framework geometry:
# - PDO at home rung (φ⁸) = matched-rung mirror = anti-phase → sign -1
# - AMO, TNA = same-side ocean basins, in-phase → +1 at lower rungs, dampened at high
# - IOD = adjacent ocean basin, mostly in-phase → +1
# These signs come from the matched-rung topology, NOT from regression.
FEEDER_SIGNS = dict(AMO=+1, TNA=+1, PDO=-1, IOD=+1)
# Feeder strength per rung: max at the matched rung, decaying as 1/φ^|k-k_match|
# For ENSO, all feeders strongest at φ⁸ (matched rung)
FEEDER_RUNG_STRENGTH = np.array([PHI**(-abs(k - K_REF)) for k,_ in RUNGS])
# Overall feeder weight: 1/φ⁴ blend constant from three-circle architecture
FEEDER_BLEND = PHI**(-4)  # ≈ 0.146

SYS = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD)
FEEDERS = ['AMO','TNA','PDO','IOD']

def vehicle_pure(refit_t, h, last_residual):
    """Pure-structure vehicle. NO regression. Only framework constants.

    last_residual = [NINO[t-1] - vehicle_predicted(t-1)] from the past, used in AR γ=1/φ³.
    """
    arr_train = NINO[:refit_t]
    mean_train = float(np.mean(arr_train))

    # Causal bandpass for each (system, rung) on training data
    bp = {}
    for nm in SYS:
        bp[nm] = [causal_bandpass(SYS[nm][:refit_t], p) for k,p in RUNGS]

    # Read state (amp, theta, ARA) at end of training data
    state = {}
    for nm in SYS:
        for ri, (k, p) in enumerate(RUNGS):
            a, th = read_amp_theta(bp[nm][ri])
            ara = per_rung_ARA_causal(SYS[nm][:refit_t], p) if nm == 'NINO' else 1.0
            state[(nm, ri)] = (a, th, ara)

    # Forward project each (system, rung) deterministically
    nino_rung_future = []
    feeder_rung_future = {fn: [] for fn in FEEDERS}

    for ri, (k, p) in enumerate(RUNGS):
        # NINO own oscillator
        a_n, th_n, ara_n = state[('NINO', ri)]
        new_th_n = th_n + 2*np.pi*h/p
        # Amplitude decay per ARA-stability: φ⁻|ARA-φ| × κ (κ=0.05/period normalises)
        kappa = 0.05
        decay_n = np.exp(-abs(ara_n - PHI) * h / p * kappa)
        nino_rung_future.append(a_n * decay_n * np.cos(new_th_n))
        # Feeder oscillators
        for fn in FEEDERS:
            a_f, th_f, _ = state[(fn, ri)]
            new_th_f = th_f + 2*np.pi*h/p
            # Feeders assumed near their own classic ARA (=1 by default), no decay
            feeder_rung_future[fn].append(a_f * np.cos(new_th_f))

    nino_rung_future = np.array(nino_rung_future)

    # Sum NINO rungs with framework weights
    own_pred = float(np.dot(RUNG_WEIGHTS, nino_rung_future))

    # Matched-rung coupling: feeder at rung k contributes to NINO at rung k
    feeder_pred = 0.0
    for fn in FEEDERS:
        feeder_arr = np.array(feeder_rung_future[fn])
        sign = FEEDER_SIGNS[fn]
        # Weight per rung × overall feeder strength
        contribution = sign * float(np.dot(FEEDER_RUNG_STRENGTH * RUNG_WEIGHTS, feeder_arr))
        # Normalise by amplitude scale of feeder
        # Feeder amplitudes are different from NINO so apply feeder-blend constant
        feeder_pred += FEEDER_BLEND * contribution / len(FEEDERS)

    # Total prediction (without AR)
    structural_pred = mean_train + own_pred + feeder_pred

    # AR feedback at exactly γ=1/φ³
    ar_term = INV_PHI3 * last_residual

    pred = structural_pred + ar_term
    truth = NINO[refit_t + h - 1]
    return pred, truth, structural_pred

# ===== Rolling loop =====
HORIZONS = [1, 3, 6, 12, 24]
MIN_TRAIN = 30 * 12
STEP = 12
print(f"\n  Rolling: refit every {STEP} months, min_train={MIN_TRAIN}, horizons={HORIZONS}")
print(f"  Framework constants only — NO regression, NO learned weights.")
print(f"  Per-rung weights: 1/φ^|k-{K_REF}| (vertical-ARA/river-prediction)")
print(f"  Feeder signs: PDO=-1 (matched-rung mirror), AMO/TNA/IOD=+1")
print(f"  Feeder blend: 1/φ⁴ ≈ {FEEDER_BLEND:.4f}")
print(f"  AR feedback: 1/φ³ ≈ {INV_PHI3:.4f}")

results = {h: [] for h in HORIZONS}
forecasts_h24 = []
last_residual = 0.0

t_start = time.time()
for refit_t in range(MIN_TRAIN, N - max(HORIZONS), STEP):
    for h in HORIZONS:
        if refit_t + h - 1 >= N: continue
        pred, truth, struct_pred = vehicle_pure(refit_t, h, last_residual)
        results[h].append((refit_t, pred, truth, struct_pred))
        if h == 24:
            forecasts_h24.append(dict(refit_t=int(refit_t), date=str(DATES[refit_t].date()), pred=pred, truth=truth))
    # Update last_residual from h=1 prediction & truth
    if results[1]:
        r = results[1][-1]
        last_residual = float(r[2] - r[1])
print(f"  {time.time()-t_start:.1f}s, {len(results[HORIZONS[0]])} forecasts/horizon")

print(f"\n  {'horizon':>10}  {'corr':>7}  {'MAE':>7}  {'pers MAE':>9}  {'clim MAE':>9}  {'R²(clim)':>9}  {'R²(pers)':>9}  {'dir':>6}")
metrics = {}
clim_pred = float(np.mean(NINO))
for h in HORIZONS:
    if not results[h]: continue
    preds = np.array([r[1] for r in results[h]])
    truths = np.array([r[2] for r in results[h]])
    pers_preds = np.array([NINO[r[0]-1] for r in results[h]])
    corr = float(np.corrcoef(preds, truths)[0,1]) if np.std(preds)>1e-9 and np.std(truths)>1e-9 else 0.0
    mae = float(np.mean(np.abs(preds - truths)))
    pers_mae = float(np.mean(np.abs(pers_preds - truths)))
    clim_mae = float(np.mean(np.abs(clim_pred - truths)))
    ss_res = np.sum((truths - preds)**2)
    ss_clim = np.sum((truths - clim_pred)**2)
    ss_pers = np.sum((truths - pers_preds)**2)
    r2_clim = float(1 - ss_res/ss_clim) if ss_clim > 0 else 0.0
    r2_pers = float(1 - ss_res/ss_pers) if ss_pers > 0 else 0.0
    dir_acc = float(np.mean(np.sign(preds - pers_preds) == np.sign(truths - pers_preds)))
    print(f"  h={h:>2} mo  {corr:+.3f}  {mae:.3f}    {pers_mae:.3f}      {clim_mae:.3f}  {r2_clim:+.3f}    {r2_pers:+.3f}    {dir_acc*100:5.1f}%")
    metrics[h] = dict(corr=corr, mae=mae, pers_mae=pers_mae, clim_mae=clim_mae,
                      r2_clim=r2_clim, r2_pers=r2_pers, dir_acc=dir_acc, n=len(results[h]))

out = dict(method="Pure-structure vehicle: framework constants only, no regression",
           constants=dict(rung_weights=RUNG_WEIGHTS.tolist(), feeder_blend=FEEDER_BLEND, ar_gamma=INV_PHI3),
           horizons=HORIZONS, results=metrics, forecasts_h24=forecasts_h24)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.VEHICLE_PURE = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
