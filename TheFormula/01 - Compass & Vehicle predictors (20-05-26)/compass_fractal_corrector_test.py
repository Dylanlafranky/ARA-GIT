"""
Fractal residual correction — apply γ=1/φ recursively.

Dylan's insight (2026-05-02): if the compass residual is itself ARA-structured
with γ ≈ 1/φ, applying that correction leaves a NEW residual. That new residual
might also have framework structure, correctable at γ=1/φ² or 1/φ at the next
level. Like a half-life — each correction takes ~1/φ of what's left.

Test: apply N successive corrections, each using prev-residual at the
appropriate level. After each level, measure:
  - Hurst exponent of remaining residual (should approach 0.5 = Brownian as we converge)
  - Lag-1 autocorrelation (should approach 0)
  - φ-rung structure (should flatten as Brownian limit reached)
  - MAE / direction at each level

If structure persists across multiple levels, framework is fractal in errors all
the way down. If it converges to Brownian quickly, we've reached the prediction
limit at level N.
"""
import json, os, time
import numpy as np, pandas as pd
from scipy.signal import butter, lfilter, find_peaks
from scipy.ndimage import gaussian_filter1d

PHI = 1.6180339887498949
INV_PHI = 1.0 / PHI
INV_PHI3 = 1.0 / (PHI**3)
INV_PHI4 = 1.0 / (PHI**4)

def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
SOI_PATH  = _resolve(r"F:\SystemFormulaFolder\SOI_NOAA\soi.data")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\compass_fractal_data.js")

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
nino = load_nino(); soi = load_soi()
def to_m(s):
    s=s.copy(); s.index=pd.to_datetime(s.index).to_period('M').to_timestamp()
    return s.groupby(s.index).first()
nino,soi = to_m(nino),to_m(soi)
common = nino.index.intersection(soi.index).sort_values()
NINO = nino.reindex(common).values.astype(float)
SOI = soi.reindex(common).values.astype(float)
DATES = common; N = len(NINO)

def causal_bandpass(arr, period_units, bw=0.4, order=2):
    n = len(arr); f_c = 1.0/period_units; nyq = 0.5
    Wn_lo = max(1e-6, (1-bw)*f_c/nyq); Wn_hi = min(0.999, (1+bw)*f_c/nyq)
    if Wn_lo >= Wn_hi: return np.zeros(n)
    b, a = butter(order, [Wn_lo, Wn_hi], btype='bandpass')
    return lfilter(b, a, arr - np.mean(arr))

def read_amp_theta(bp_to_t):
    if len(bp_to_t) < 2: return 0.0, 0.0
    n_recent = min(50, len(bp_to_t))
    amp = float(np.std(bp_to_t[-n_recent:]) * np.sqrt(2)) + 1e-9
    last = bp_to_t[-1]; rate = bp_to_t[-1] - bp_to_t[-2]
    ratio = max(-0.99, min(0.99, last/amp))
    return amp, np.arccos(ratio) * (-1 if rate > 0 else 1)

RUNGS = [(k, PHI**k) for k in range(4, 14)]
N_RUNGS = len(RUNGS)
K_REF = 8
K_REF_IDX = next(i for i,(k,_) in enumerate(RUNGS) if k == K_REF)
RUNG_WEIGHTS = np.array([PHI**(-abs(k - K_REF)) for k,_ in RUNGS])
RUNG_WEIGHTS = RUNG_WEIGHTS / np.sum(RUNG_WEIGHTS)

def amp_predict(refit_t, h, last_residual_internal, state, soi_scale, nino_scale, mean_train):
    nino_rung_future = []; soi_rung_future = []
    for ri, (k, p) in enumerate(RUNGS):
        a_n, th_n, _ = state[('NINO', ri)]
        new_th_n = th_n + 2*np.pi*h/p
        nino_rung_future.append(a_n * np.cos(new_th_n))
        a_f, th_f, _ = state[('SOI', ri)]
        soi_rung_future.append(a_f * np.cos(th_f + 2*np.pi*h/p))
    nino_rung_future = np.array(nino_rung_future)
    own_pred = float(np.dot(RUNG_WEIGHTS, nino_rung_future))
    soi_norm = np.array(soi_rung_future) / soi_scale * nino_scale
    walker = -1.0 * 1.0 * soi_norm[K_REF_IDX] * RUNG_WEIGHTS[K_REF_IDX] * 5
    for ri in range(N_RUNGS):
        if ri == K_REF_IDX: continue
        walker += -1.0 * (1.0/PHI**abs(RUNGS[ri][0]-K_REF)) * INV_PHI4 * soi_norm[ri] * RUNG_WEIGHTS[ri]
    return mean_train + own_pred + walker + INV_PHI3 * last_residual_internal

def run_compass(refit_t, horizon, last_residual_internal, state, soi_scale, nino_scale, mean_train, step_mean):
    cur_pos = NINO[refit_t - 1]
    prev_amp = NINO[refit_t - 1]
    for tau in range(1, horizon + 1):
        amp = amp_predict(refit_t, tau, last_residual_internal, state, soi_scale, nino_scale, mean_train)
        delta = amp - prev_amp
        direction = 1 if delta > 0 else -1
        cur_pos += direction * min(abs(delta), step_mean * PHI)
        prev_amp = amp
    return cur_pos

def hurst_exponent(arr):
    arr = np.asarray(arr).flatten()
    n = len(arr)
    if n < 20: return None
    rs_values = []
    for lag in [4, 8, 16, 32]:
        if lag >= n: continue
        rs_chunks = []
        for start in range(0, n - lag, lag):
            chunk = arr[start:start+lag]
            cumdev = np.cumsum(chunk - np.mean(chunk))
            R = np.max(cumdev) - np.min(cumdev)
            S = np.std(chunk)
            if S > 0: rs_chunks.append(R/S)
        if rs_chunks: rs_values.append((lag, np.mean(rs_chunks)))
    if len(rs_values) < 2: return None
    log_lags = np.log([rv[0] for rv in rs_values])
    log_rs = np.log([rv[1] for rv in rs_values])
    H, _ = np.polyfit(log_lags, log_rs, 1)
    return float(H)

def lag_autocorr(arr, lag=1):
    arr = np.asarray(arr) - np.mean(arr)
    var = np.var(arr)
    if var < 1e-9: return 0.0
    return float(np.mean(arr[:-lag] * arr[lag:]) / var)

# ===== Generate compass forecasts =====
HORIZON = 6  # mid-lead — where residual structure was strongest
MIN_TRAIN = 30 * 12
STEP = 12
N_LEVELS = 4  # how many fractal correction levels to test

print(f"\nGenerating compass forecasts at h={HORIZON}...")
forecast_records = []  # (refit_t, base_pred, truth)
last_residual_internal = 0.0
for refit_t in range(MIN_TRAIN, N - HORIZON, STEP):
    arr_train = NINO[:refit_t]
    mean_train = float(np.mean(arr_train))
    nino_scale = float(np.std(arr_train)) + 1e-9
    soi_scale = float(np.std(SOI[:refit_t])) + 1e-9
    step_mean = float(np.mean(np.abs(np.diff(arr_train))))
    bp = {nm: [causal_bandpass({'NINO':NINO,'SOI':SOI}[nm][:refit_t], p) for k,p in RUNGS] for nm in ['NINO','SOI']}
    state = {}
    for nm in ['NINO','SOI']:
        for ri, (k, p) in enumerate(RUNGS):
            a, th = read_amp_theta(bp[nm][ri])
            state[(nm, ri)] = (a, th, 1.0)
    base_pred = run_compass(refit_t, HORIZON, last_residual_internal, state, soi_scale, nino_scale, mean_train, step_mean)
    truth = NINO[refit_t + HORIZON - 1]
    forecast_records.append((refit_t, base_pred, truth))
    if results_h1 := []: pass  # placeholder; not used
    last_residual_internal = float(truth - base_pred)
print(f"  {len(forecast_records)} forecasts")

base_preds = np.array([r[1] for r in forecast_records])
truths = np.array([r[2] for r in forecast_records])
clim_pred = float(np.mean(NINO))
pers_preds = np.array([NINO[r[0]-1] for r in forecast_records])

def metrics(preds, truths, pers_preds):
    m = {}
    m['corr'] = float(np.corrcoef(preds, truths)[0,1]) if np.std(preds)>1e-9 and np.std(truths)>1e-9 else 0.0
    m['mae'] = float(np.mean(np.abs(preds - truths)))
    m['rmse'] = float(np.sqrt(np.mean((preds-truths)**2)))
    ss_res = np.sum((truths - preds)**2)
    ss_clim = np.sum((truths - clim_pred)**2)
    ss_pers = np.sum((truths - pers_preds)**2)
    m['r2_clim'] = float(1 - ss_res/ss_clim) if ss_clim > 0 else 0.0
    m['r2_pers'] = float(1 - ss_res/ss_pers) if ss_pers > 0 else 0.0
    m['dir'] = float(np.mean(np.sign(preds - pers_preds) == np.sign(truths - pers_preds)))
    return m

print(f"\n========= FRACTAL RESIDUAL CORRECTION at h={HORIZON} =========")
print(f"\n--- Level 0 (no correction) ---")
m0 = metrics(base_preds, truths, pers_preds)
res0 = truths - base_preds
H0 = hurst_exponent(res0)
ac0 = lag_autocorr(res0, 1)
sigma_res0 = float(np.std(res0))
print(f"  corr {m0['corr']:+.3f}  MAE {m0['mae']:.3f}  R²(pers) {m0['r2_pers']:+.3f}  dir {m0['dir']*100:.1f}%")
print(f"  Residual: σ={sigma_res0:.3f}, Hurst={H0:.3f}, lag-1 autocorr={ac0:+.3f}")

# Apply N levels of correction iteratively
# At each level, use the lag-1 autocorr of the CURRENT residual, but with γ = 1/φ^L (level-L framework constant)
# Simpler: γ = 1/φ at each level (constant), but applied to the level-L residual
preds_per_level = [base_preds.copy()]
residuals_per_level = [res0]
metrics_per_level = [m0]
hurst_per_level = [H0]
ac_per_level = [ac0]
sigma_per_level = [sigma_res0]

for level in range(1, N_LEVELS + 1):
    prev_residuals = residuals_per_level[-1]
    # Determine sign of correction from residual's lag-1 autocorrelation
    ac_prev = ac_per_level[-1]
    # If autocorr negative (mean-reverting): subtract |γ| × prev_res
    # If autocorr positive (persistent): add |γ| × prev_res
    correction_sign = -1.0 if ac_prev < 0 else 1.0
    # Use γ = 1/φ as the fractal-level coefficient (Dylan's framework constant)
    gamma_level = INV_PHI

    # Apply correction to each forecast: new_pred[t] = old_pred[t] + sign*γ * residual[t-1]
    # We need lagged residuals; for t=0 use 0
    new_preds = preds_per_level[-1].copy()
    prev_res_t = 0.0
    for i, _ in enumerate(forecast_records):
        new_preds[i] = preds_per_level[-1][i] + correction_sign * gamma_level * prev_res_t
        prev_res_t = float(prev_residuals[i])  # update for NEXT iteration

    # Compute new residual
    new_res = truths - new_preds
    m_new = metrics(new_preds, truths, pers_preds)
    H_new = hurst_exponent(new_res)
    ac_new = lag_autocorr(new_res, 1)
    sigma_new = float(np.std(new_res))

    preds_per_level.append(new_preds)
    residuals_per_level.append(new_res)
    metrics_per_level.append(m_new)
    hurst_per_level.append(H_new)
    ac_per_level.append(ac_new)
    sigma_per_level.append(sigma_new)

    print(f"\n--- Level {level} (γ={gamma_level:.3f}, sign={correction_sign:+.0f} from prev autocorr {ac_prev:+.3f}) ---")
    print(f"  corr {m_new['corr']:+.3f}  MAE {m_new['mae']:.3f}  R²(pers) {m_new['r2_pers']:+.3f}  dir {m_new['dir']*100:.1f}%")
    print(f"  Residual: σ={sigma_new:.3f} (was {sigma_per_level[-2]:.3f}, ratio {sigma_new/sigma_per_level[-2]:.3f}), Hurst={H_new:.3f}, lag-1 autocorr={ac_new:+.3f}")

print(f"\n=== Half-life convergence test ===")
print(f"  Level   σ_res    Hurst    lag-1    σ ratio (decay per level)")
for level in range(N_LEVELS + 1):
    sigma = sigma_per_level[level]
    H = hurst_per_level[level]
    ac = ac_per_level[level]
    ratio = sigma / sigma_per_level[level-1] if level > 0 else 1.0
    print(f"  {level:>5}    {sigma:.3f}   {H:+.3f}   {ac:+.3f}   {ratio:.3f}")

# Theoretical prediction: if framework is fractal with γ=1/φ at each level,
# σ should decay by factor √(1 − γ²) ≈ √(1 − 0.382) = √0.618 ≈ 0.786 per level
target_decay = np.sqrt(1 - INV_PHI**2)
print(f"\n  Theoretical decay per level if perfect γ=1/φ correction: {target_decay:.3f}")
print(f"  → If empirical decay matches this, framework's fractal residual claim confirmed.")

out = dict(method=f"Fractal residual correction at h={HORIZON}, N_levels={N_LEVELS}, γ=1/φ each level",
           horizon=HORIZON, n_levels=N_LEVELS,
           metrics_per_level=metrics_per_level,
           hurst_per_level=hurst_per_level,
           ac_per_level=ac_per_level,
           sigma_per_level=sigma_per_level,
           target_decay_theoretical=target_decay)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.COMPASS_FRACTAL = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
