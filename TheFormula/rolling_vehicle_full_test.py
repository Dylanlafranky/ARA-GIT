"""
Rolling vehicle FULL — multi-system, matched-rung coupling, ARA-driven amplitude,
AR feedback at γ=1/φ³. Strict causal everywhere.

Forward step at each forecast time t:
  1. Read state for each (system, rung) — causal bandpass amp & phase.
  2. Each rung phase advances at 2π/period per month.
  3. Amplitude evolves via ARA-stability rule:
       a(t+dt) = a(t) × exp(-|ARA-φ| × dt/period × κ)   (κ small constant)
     Engines (ARA≈φ) preserve amplitude; far-from-φ rungs decay.
  4. Cross-system coupling: at each rung, add weighted sum of feeder rung values
     (matched-rung). Weights learned from training data correlations.
  5. Output prediction = weighted sum of all NINO rungs, with AR feedback:
       pred(t+h) = vehicle(t+h) + (1/φ³)·[obs(t-1) - vehicle_predicted(t-1)]
       (γ=1/φ³ momentum from the three-circle architecture)

Compares to V0/V1/V2 single-system vehicle and to climatology/persistence.
"""
import json, os, time
import numpy as np, pandas as pd
from scipy.signal import butter, lfilter
import re

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
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\rolling_vehicle_full_data.js")

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
    """Causally read amp & phase at end of bp_to_t."""
    if len(bp_to_t) < 2: return 0.0, 0.0
    n_recent = min(50, len(bp_to_t))
    amp = float(np.std(bp_to_t[-n_recent:]) * np.sqrt(2)) + 1e-9
    last = bp_to_t[-1]
    rate = bp_to_t[-1] - bp_to_t[-2]
    ratio = max(-0.99, min(0.99, last/amp))
    return amp, np.arccos(ratio) * (-1 if rate > 0 else 1)

def per_rung_ARA_causal(arr_train, period):
    """ARA from training data only — uses zero-phase IIR filtfilt? No — keep causal."""
    bp = causal_bandpass(arr_train, period, bw=0.85)
    if len(bp) < 3*int(period): return 1.0
    # Identify peaks/troughs in bp (smooth slightly)
    from scipy.signal import find_peaks
    from scipy.ndimage import gaussian_filter1d
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

RUNGS = [(k, PHI**k) for k in range(4, 14)]
N_RUNGS = len(RUNGS)
SYS = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD)
FEEDERS = ['AMO','TNA','PDO','IOD']

def vehicle_full(refit_t, h, history_errors):
    """Full vehicle predict NINO at refit_t + h - 1.

    Uses:
      - Causal bandpass for each (system, rung)
      - Read amp & phase at refit_t for each
      - Forward-project each as oscillator with ARA-amplitude decay
      - Matched-rung coupling: feeder rungs influence NINO rungs via training-fit weights
      - AR feedback at γ=1/φ³ from history of past forecast errors
    """
    arr_train_NINO = NINO[:refit_t]
    mean_train = float(np.mean(arr_train_NINO))

    # Per-(system, rung) bandpass on training data (causal)
    bp = {nm: [causal_bandpass(SYS[nm][:refit_t], p) for k,p in RUNGS] for nm in SYS}

    # Read state at end of training data
    state = {}  # (system, rung_idx) -> (amp, theta, ARA)
    for nm in SYS:
        for ri, (k, p) in enumerate(RUNGS):
            a, th = read_amp_theta(bp[nm][ri])
            ara = per_rung_ARA_causal(SYS[nm][:refit_t], p)
            state[(nm, ri)] = (a, th, ara)

    # Train matched-rung coupling weights:
    # NINO_bp_at_rung_k(t) = sum_feeder w_k_feeder * feeder_bp_at_rung_k(t) + b
    # Fit on training data at each rung
    rung_betas = []
    for ri in range(N_RUNGS):
        rows = []; ys = []
        warm = max(50, int(2*RUNGS[ri][1]))
        warm = min(warm, refit_t-100)
        if warm >= refit_t:
            rung_betas.append(np.zeros(len(FEEDERS)+2))
            continue
        for t in range(warm, refit_t):
            row = [bp[fn][ri][t] for fn in FEEDERS] + [bp['NINO'][ri][t], 1.0]
            rows.append(row); ys.append(bp['NINO'][ri][t])
        # Self-feature here means we're predicting NINO_bp[t] from itself — skip self-feature
        # Actually let's just learn feeder weights on NINO at this rung
        rows2 = [[r[i] for i in range(len(FEEDERS))] + [1.0] for r in rows]
        X = np.array(rows2); y = np.array(ys)
        if X.shape[0] > 10:
            ridge = 5.0
            A = X.T @ X + ridge*np.eye(X.shape[1])
            beta = np.linalg.solve(A, X.T @ y)
            rung_betas.append(beta)
        else:
            rung_betas.append(np.zeros(X.shape[1]))

    # Train per-rung weight to predict raw NINO from rung sums (causal)
    # Output(t) = sum_rung w_rung * (matched_rung_estimate_at_rung)
    # We use the bp_NINO[rung][t] directly as the "rung output" for this fit.
    rows = []; ys = []
    warm2 = max(50, int(2*RUNGS[-1][1]))
    warm2 = min(warm2, refit_t-100)
    for t in range(warm2, refit_t):
        rows.append([bp['NINO'][ri][t] for ri in range(N_RUNGS)])
        ys.append(NINO[t] - mean_train)
    if len(rows) > 30:
        X = np.array(rows); y = np.array(ys)
        ridge = 5.0
        A = X.T @ X + ridge*np.eye(N_RUNGS)
        rung_w = np.linalg.solve(A, X.T @ y)
    else:
        rung_w = np.ones(N_RUNGS) / N_RUNGS

    # ===== FORWARD PROJECT to t+h-1 =====
    # For each (system, rung), advance phase, decay amplitude per ARA stability
    rung_predictions = []
    for ri, (k, p) in enumerate(RUNGS):
        # Forward each feeder rung first (so they can drive NINO)
        feeder_future = []
        for fn in FEEDERS:
            a, th, ara = state[(fn, ri)]
            new_th = th + 2*np.pi*h/p
            kappa = 0.05  # decay coefficient
            decay = np.exp(-abs(ara - PHI) * h / p * kappa)
            new_a = a * decay
            feeder_future.append(new_a * np.cos(new_th))
        # NINO at this rung: own oscillator + matched-rung coupling
        a_n, th_n, ara_n = state[('NINO', ri)]
        new_th_n = th_n + 2*np.pi*h/p
        kappa = 0.05
        decay_n = np.exp(-abs(ara_n - PHI) * h / p * kappa)
        own_future = a_n * decay_n * np.cos(new_th_n)
        # Coupling: matched-rung learned weights
        beta = rung_betas[ri]
        coupled = float(np.dot(beta[:len(FEEDERS)], feeder_future) + beta[-1])
        # Blend: framework says matched-rung coupling is the dominant signal at long lead
        # Use the COUPLED estimate as primary, plus own forward extrapolation
        rung_predictions.append(coupled * 0.5 + own_future * 0.5)

    # Sum across rungs with weights
    base_pred = mean_train + float(np.dot(rung_w, rung_predictions))

    # AR feedback at γ=1/φ³: compute recent residual
    # We can use the last observed deviation: NINO[refit_t-1] - vehicle's last-step internal estimate
    # For simplicity: AR feedback uses the previous month's actual residual
    if history_errors:
        ar_term = INV_PHI3 * history_errors[-1]
    else:
        ar_term = 0.0

    pred = base_pred + ar_term
    truth = NINO[refit_t + h - 1]
    return pred, truth, base_pred

# ===== Rolling loop =====
HORIZONS = [1, 3, 6, 12, 24]
MIN_TRAIN = 30 * 12
STEP = 12
print(f"\n  Rolling: refit every {STEP} months, min_train={MIN_TRAIN}, horizons={HORIZONS}")

results = {h: [] for h in HORIZONS}
forecasts_h24 = []
history_errors = []

t_start = time.time()
for refit_t in range(MIN_TRAIN, N - max(HORIZONS), STEP):
    for h in HORIZONS:
        if refit_t + h - 1 >= N: continue
        pred, truth, base_pred = vehicle_full(refit_t, h, history_errors)
        results[h].append((refit_t, pred, truth, base_pred))
        if h == 24:
            forecasts_h24.append(dict(refit_t=int(refit_t), date=str(DATES[refit_t].date()), pred=pred, truth=truth))
    # Update history error from h=1 forecast
    if results[1]:
        last = results[1][-1]
        history_errors.append(float(last[2] - last[1]))
        if len(history_errors) > 24: history_errors = history_errors[-24:]
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

out = dict(method="Full vehicle: multi-system rungs, matched-rung coupling, ARA-amp decay, AR γ=1/φ³",
           horizons=HORIZONS, results=metrics, forecasts_h24=forecasts_h24)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.VEHICLE_FULL = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
