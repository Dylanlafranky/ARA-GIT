"""
Ensemble compass — Monte Carlo over many stochastic runs.

Idea (Dylan, 2 May 2026): each tick output is essentially binary (+1/-1 with
some probability). Run 200 stochastic ensemble members and take the mean.
The ensemble mean should be more stable than any single deterministic compass run,
and the spread gives an uncertainty estimate.

Each ensemble member:
  - At each tick, compute amplitude framework prediction
  - direction_prob = sigmoid(scale × Δ_amp)  — confidence-weighted probability of "up"
  - sample direction (binary +1/-1) from this prob
  - step magnitude drawn from N(mean_step, sigma_step) clipped to >0
  - integrate forward

Output:
  - mean wave across 200 members = final prediction
  - std wave = uncertainty band

Compare to:
  - Deterministic compass (single run)
  - Amplitude vehicle
  - Persistence and climatology baselines
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
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\rolling_vehicle_ensemble_compass_data.js")

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
def load_iod_or_soi(p, hdr=1):
    rows=[]
    with open(p) as f:
        for _ in range(hdr): next(f)
        for ln in f:
            parts = ln.split()
            if len(parts)<13: continue
            try: year=int(parts[0])
            except: continue
            if year<1900 or year>2100: continue
            for m in range(12):
                try: v=float(parts[1+m])
                except: continue
                if v<-90: continue
                rows.append((pd.Timestamp(year=year,month=m+1,day=1),v))
    return pd.Series(dict(rows)).sort_index()

print("Loading...")
nino = load_nino()
amo = load_grid_text(AMO_PATH); tna = load_grid_text(TNA_PATH)
pdo = load_grid_text(PDO_PATH, header_lines=2); iod = load_iod_or_soi(IOD_PATH)
soi = load_iod_or_soi(SOI_PATH)
def to_monthly(s):
    s = s.copy(); s.index = pd.to_datetime(s.index).to_period('M').to_timestamp()
    return s.groupby(s.index).first()
nino,amo,tna,pdo,iod,soi = [to_monthly(x) for x in [nino,amo,tna,pdo,iod,soi]]
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
K_REF_IDX = next(i for i,(k,_) in enumerate(RUNGS) if k == K_REF)
RUNG_WEIGHTS = np.array([PHI**(-abs(k - K_REF)) for k,_ in RUNGS])
RUNG_WEIGHTS = RUNG_WEIGHTS / np.sum(RUNG_WEIGHTS)

SYS_ALL = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD, SOI=SOI)

def amp_predict_at_h(refit_t, h, last_residual, state, soi_scale, nino_scale, mean_train):
    """Compute amplitude prediction at horizon h using pre-computed state."""
    nino_rung_future = []
    soi_rung_future = []
    for ri, (k, p) in enumerate(RUNGS):
        a_n, th_n, ara_n = state[('NINO', ri)]
        new_th_n = th_n + 2*np.pi*h/p
        kappa = 0.05
        decay_n = np.exp(-abs(ara_n - PHI) * h / p * kappa)
        nino_rung_future.append(a_n * decay_n * np.cos(new_th_n))
        a_f, th_f, _ = state[('SOI', ri)]
        new_th_f = th_f + 2*np.pi*h/p
        soi_rung_future.append(a_f * np.cos(new_th_f))
    nino_rung_future = np.array(nino_rung_future)
    soi_rung_future = np.array(soi_rung_future)
    own_pred = float(np.dot(RUNG_WEIGHTS, nino_rung_future))
    soi_norm = soi_rung_future / soi_scale * nino_scale
    walker = -1.0 * 1.0 * soi_norm[K_REF_IDX] * RUNG_WEIGHTS[K_REF_IDX] * 5
    for ri in range(N_RUNGS):
        if ri == K_REF_IDX: continue
        walker += -1.0 * (1.0/PHI**abs(RUNGS[ri][0]-K_REF)) * INV_PHI4 * soi_norm[ri] * RUNG_WEIGHTS[ri]
    return mean_train + own_pred + walker + INV_PHI3 * last_residual

# ===== Rolling ensemble compass =====
HORIZONS = [1, 3, 6, 12, 24]
MIN_TRAIN = 30 * 12
STEP = 12
N_ENSEMBLE = 200

print(f"\n  Rolling ensemble compass: {N_ENSEMBLE} stochastic members per forecast")

results = {h: dict(amp=[], compass_det=[], ensemble_mean=[], ensemble_std=[]) for h in HORIZONS}
last_residual = 0.0

t_start = time.time()
n_refits = 0
for refit_t in range(MIN_TRAIN, N - max(HORIZONS), STEP):
    arr_train = NINO[:refit_t]
    mean_train = float(np.mean(arr_train))
    nino_scale = float(np.std(arr_train)) + 1e-9
    soi_scale = float(np.std(SOI[:refit_t])) + 1e-9
    step_mean = float(np.mean(np.abs(np.diff(arr_train))))
    step_sigma = float(np.std(np.abs(np.diff(arr_train))))

    # Pre-compute state
    bp = {}
    for nm in SYS_ALL:
        bp[nm] = [causal_bandpass(SYS_ALL[nm][:refit_t], p) for k,p in RUNGS]
    state = {}
    for nm in SYS_ALL:
        for ri, (k, p) in enumerate(RUNGS):
            a, th = read_amp_theta(bp[nm][ri])
            ara = per_rung_ARA_causal(SYS_ALL[nm][:refit_t], p) if nm == 'NINO' else 1.0
            state[(nm, ri)] = (a, th, ara)

    # Amplitude prediction at each horizon (deterministic)
    amp_at_h = {}
    for h in HORIZONS:
        if refit_t + h - 1 < N:
            amp_at_h[h] = amp_predict_at_h(refit_t, h, last_residual, state, soi_scale, nino_scale, mean_train)

    # Pre-compute amp prediction at each tau from 1..max(HORIZONS)
    amp_per_tau = []
    for tau in range(0, max(HORIZONS) + 1):
        if refit_t + tau - 1 >= N:
            amp_per_tau.append(np.nan)
        else:
            amp_per_tau.append(amp_predict_at_h(refit_t, max(1, tau), last_residual, state, soi_scale, nino_scale, mean_train))

    # === DETERMINISTIC compass (no noise) ===
    cur_pos = NINO[refit_t - 1] if refit_t > 0 else 0.0
    prev_amp = NINO[refit_t - 1] if refit_t > 0 else 0.0
    compass_det_at_h = {}
    for tau in range(1, max(HORIZONS) + 1):
        if np.isnan(amp_per_tau[tau]): break
        delta = amp_per_tau[tau] - prev_amp
        direction = 1 if delta > 0 else -1
        cur_pos += direction * min(abs(delta), step_mean * PHI)
        prev_amp = amp_per_tau[tau]
        if tau in HORIZONS:
            compass_det_at_h[tau] = cur_pos

    # === ENSEMBLE compass: 200 stochastic runs ===
    rng = np.random.default_rng(refit_t)  # seed for reproducibility
    ensemble_paths = np.zeros((N_ENSEMBLE, max(HORIZONS) + 1))
    ensemble_paths[:, 0] = NINO[refit_t - 1] if refit_t > 0 else 0.0

    for tau in range(1, max(HORIZONS) + 1):
        if np.isnan(amp_per_tau[tau]): break
        # Probability of "up": sigmoid of (Δ_amp / step_mean)
        # Confident step (large Δ) → near-certain direction; small Δ → near 50/50
        delta = amp_per_tau[tau] - amp_per_tau[tau-1] if tau > 0 else 0
        # Sigmoid: high when delta>>0, low when delta<<0
        scale = 2.0 / max(step_mean, 1e-3)
        p_up = 1.0 / (1.0 + np.exp(-scale * delta))
        # Sample binary direction
        directions = rng.choice([-1, 1], size=N_ENSEMBLE, p=[1-p_up, p_up])
        # Sample step magnitude per member
        step_sizes = np.clip(rng.normal(step_mean, step_sigma, size=N_ENSEMBLE), 0.01, step_mean*PHI*2)
        # Integrate
        ensemble_paths[:, tau] = ensemble_paths[:, tau-1] + directions * step_sizes

    # At each horizon, mean and std of ensemble
    for h in HORIZONS:
        if refit_t + h - 1 >= N: continue
        truth = NINO[refit_t + h - 1]
        results[h]['amp'].append((refit_t, amp_at_h[h], truth))
        if h in compass_det_at_h:
            results[h]['compass_det'].append((refit_t, compass_det_at_h[h], truth))
        ens_mean = float(np.mean(ensemble_paths[:, h]))
        ens_std = float(np.std(ensemble_paths[:, h]))
        results[h]['ensemble_mean'].append((refit_t, ens_mean, truth))
        results[h]['ensemble_std'].append((refit_t, ens_std, truth))

    if results[1]['amp']:
        last_residual = float(results[1]['amp'][-1][2] - results[1]['amp'][-1][1])
    n_refits += 1

print(f"  {n_refits} refits, {time.time()-t_start:.1f}s")

print(f"\n========= ENSEMBLE COMPASS RESULTS =========")
clim_pred = float(np.mean(NINO))
metrics_out = {}
for variant in ['amp', 'compass_det', 'ensemble_mean']:
    print(f"\n--- {variant} ---")
    print(f"  {'horizon':>10}  {'corr':>7}  {'MAE':>7}  {'R²(clim)':>9}  {'R²(pers)':>9}  {'dir':>6}")
    metrics_out[variant] = {}
    for h in HORIZONS:
        recs = results[h][variant]
        if not recs: continue
        preds = np.array([r[1] for r in recs])
        truths = np.array([r[2] for r in recs])
        pers_preds = np.array([NINO[r[0]-1] for r in recs])
        corr = float(np.corrcoef(preds, truths)[0,1]) if np.std(preds)>1e-9 and np.std(truths)>1e-9 else 0.0
        mae = float(np.mean(np.abs(preds - truths)))
        ss_res = np.sum((truths - preds)**2)
        ss_clim = np.sum((truths - clim_pred)**2)
        ss_pers = np.sum((truths - pers_preds)**2)
        r2_clim = float(1 - ss_res/ss_clim) if ss_clim > 0 else 0.0
        r2_pers = float(1 - ss_res/ss_pers) if ss_pers > 0 else 0.0
        dir_acc = float(np.mean(np.sign(preds - pers_preds) == np.sign(truths - pers_preds)))
        print(f"  h={h:>2} mo  {corr:+.3f}  {mae:.3f}    {r2_clim:+.3f}    {r2_pers:+.3f}    {dir_acc*100:5.1f}%")
        metrics_out[variant][h] = dict(corr=corr, mae=mae, r2_clim=r2_clim, r2_pers=r2_pers, dir_acc=dir_acc, n=len(recs))

# Mean ensemble std (uncertainty)
print(f"\n  Mean ensemble std (uncertainty band) by horizon:")
for h in HORIZONS:
    stds = [r[1] for r in results[h]['ensemble_std']]
    if stds:
        print(f"    h={h:>2} mo: mean σ = {np.mean(stds):.3f} °C")

out = dict(method=f"Ensemble compass: {N_ENSEMBLE} stochastic Monte Carlo runs, take ensemble mean",
           n_ensemble=N_ENSEMBLE,
           variants=dict(amp='amplitude prediction', compass_det='deterministic compass (single run)',
                         ensemble_mean=f'mean of {N_ENSEMBLE} stochastic compass runs'),
           results=metrics_out)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.VEHICLE_ENSEMBLE = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
