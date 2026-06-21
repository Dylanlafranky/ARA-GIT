"""
Brownian vs ARA analysis of compass residuals.

Dylan's insight: Brownian motion is an ARA-class signature. If our compass error
is pure Brownian, we've reached the framework's prediction ceiling. If the error
has its own ARA structure (peaks at φ-rungs, deviation from exp-decay autocorr),
we can extract and correct it.

Tests on compass residuals:
  1. Hurst exponent (H ≈ 0.5 = Brownian, H > 0.5 = persistent, H < 0.5 = mean-reverting)
  2. Autocorrelation function vs pure Brownian expectation
  3. Bandpass at φ-rungs to see if residual has rung-structured power
  4. Residual ARA at home rung — what class of system is the leftover error?

If the residual has framework structure → build error-corrector and re-test
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
SOI_PATH  = _resolve(r"F:\SystemFormulaFolder\SOI_NOAA\soi.data")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\compass_residual_brownian_data.js")

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
nino = load_nino()
soi = load_soi()
def to_monthly(s):
    s = s.copy(); s.index = pd.to_datetime(s.index).to_period('M').to_timestamp()
    return s.groupby(s.index).first()
nino,soi = to_monthly(nino), to_monthly(soi)
common = nino.index.intersection(soi.index).sort_values()
NINO = nino.reindex(common).values.astype(float)
SOI = soi.reindex(common).values.astype(float)
DATES = common; N = len(NINO)
print(f"  N={N} months, {DATES[0].date()} to {DATES[-1].date()}")

def causal_bandpass(arr, period_units, bw=0.4, order=2):
    n = len(arr); f_c = 1.0/period_units; nyq = 0.5
    Wn_lo = max(1e-6, (1-bw)*f_c/nyq); Wn_hi = min(0.999, (1+bw)*f_c/nyq)
    if Wn_lo >= Wn_hi: return np.zeros(n)
    try:
        b, a = butter(order, [Wn_lo, Wn_hi], btype='bandpass')
        return lfilter(b, a, arr - np.mean(arr))
    except: return np.zeros(n)

def read_amp_theta(bp_to_t):
    if len(bp_to_t) < 2: return 0.0, 0.0
    n_recent = min(50, len(bp_to_t))
    amp = float(np.std(bp_to_t[-n_recent:]) * np.sqrt(2)) + 1e-9
    last = bp_to_t[-1]; rate = bp_to_t[-1] - bp_to_t[-2]
    ratio = max(-0.99, min(0.99, last/amp))
    return amp, np.arccos(ratio) * (-1 if rate > 0 else 1)

# ===== Generate compass residuals at multiple horizons =====
# Use yearly refit, deterministic compass, output raw forecast time series + residuals
RUNGS = [(k, PHI**k) for k in range(4, 14)]
N_RUNGS = len(RUNGS)
K_REF = 8
K_REF_IDX = next(i for i,(k,_) in enumerate(RUNGS) if k == K_REF)
RUNG_WEIGHTS = np.array([PHI**(-abs(k - K_REF)) for k,_ in RUNGS])
RUNG_WEIGHTS = RUNG_WEIGHTS / np.sum(RUNG_WEIGHTS)

def amp_predict(refit_t, h, last_residual, state, soi_scale, nino_scale, mean_train):
    nino_rung_future = []; soi_rung_future = []
    for ri, (k, p) in enumerate(RUNGS):
        a_n, th_n, ara_n = state[('NINO', ri)]
        new_th_n = th_n + 2*np.pi*h/p
        decay_n = np.exp(-abs(ara_n - PHI) * h / p * 0.05)
        nino_rung_future.append(a_n * decay_n * np.cos(new_th_n))
        a_f, th_f, _ = state[('SOI', ri)]
        soi_rung_future.append(a_f * np.cos(th_f + 2*np.pi*h/p))
    nino_rung_future = np.array(nino_rung_future)
    own_pred = float(np.dot(RUNG_WEIGHTS, nino_rung_future))
    soi_norm = np.array(soi_rung_future) / soi_scale * nino_scale
    walker = -1.0 * 1.0 * soi_norm[K_REF_IDX] * RUNG_WEIGHTS[K_REF_IDX] * 5
    for ri in range(N_RUNGS):
        if ri == K_REF_IDX: continue
        walker += -1.0 * (1.0/PHI**abs(RUNGS[ri][0]-K_REF)) * INV_PHI4 * soi_norm[ri] * RUNG_WEIGHTS[ri]
    return mean_train + own_pred + walker + INV_PHI3 * last_residual

print("\nGenerating compass forecasts...")
HORIZON = 6  # use h=6 — interesting horizon where we have real signal
MIN_TRAIN = 30 * 12
STEP = 12

residuals_h = []  # (refit_t, residual at horizon HORIZON)
last_residual = 0.0
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
            ara = 1.0  # simplified
            state[(nm, ri)] = (a, th, ara)

    # Deterministic compass
    cur_pos = NINO[refit_t - 1]
    prev_amp = NINO[refit_t - 1]
    for tau in range(1, HORIZON + 1):
        amp = amp_predict(refit_t, tau, last_residual, state, soi_scale, nino_scale, mean_train)
        delta = amp - prev_amp
        direction = 1 if delta > 0 else -1
        cur_pos += direction * min(abs(delta), step_mean * PHI)
        prev_amp = amp

    truth = NINO[refit_t + HORIZON - 1]
    residual = truth - cur_pos  # positive = compass under-predicted
    residuals_h.append((refit_t, residual, cur_pos, truth))
    last_residual = float(residual)

residual_arr = np.array([r[1] for r in residuals_h])
print(f"  {len(residual_arr)} residuals at h={HORIZON}: mean={residual_arr.mean():+.3f}, std={residual_arr.std():.3f}")

# ===== Brownian vs ARA tests on residuals =====
print("\n=== Test 1: Hurst exponent (H=0.5 → pure Brownian) ===")
def hurst_exponent(arr):
    """Estimate Hurst exponent via R/S analysis."""
    arr = np.asarray(arr).flatten()
    n = len(arr)
    if n < 20: return None
    rs_values = []
    lags = [4, 8, 16, 32]
    for lag in lags:
        if lag >= n: continue
        # Split series into chunks of size lag
        rs_chunks = []
        for start in range(0, n - lag, lag):
            chunk = arr[start:start+lag]
            mean_chunk = np.mean(chunk)
            cumdev = np.cumsum(chunk - mean_chunk)
            R = np.max(cumdev) - np.min(cumdev)
            S = np.std(chunk)
            if S > 0: rs_chunks.append(R/S)
        if rs_chunks: rs_values.append((lag, np.mean(rs_chunks)))
    if len(rs_values) < 2: return None
    log_lags = np.log([rv[0] for rv in rs_values])
    log_rs = np.log([rv[1] for rv in rs_values])
    H, _ = np.polyfit(log_lags, log_rs, 1)
    return float(H)

H = hurst_exponent(residual_arr)
print(f"  Compass residual Hurst H = {H:.3f}" if H is not None else "  Insufficient data")
if H is not None:
    if 0.4 < H < 0.6:
        print(f"  → Near-Brownian (random walk-like). Compass error has no exploitable trend structure.")
    elif H > 0.6:
        print(f"  → Persistent (H>0.5). Errors have momentum — large errors stay large. Could correct.")
    else:
        print(f"  → Mean-reverting (H<0.5). Errors flip sign quickly. Suggests overfit corrections.")

# ===== Test 2: Autocorrelation function =====
print("\n=== Test 2: Autocorrelation of residuals (Brownian → exp decay) ===")
def acf(arr, max_lag=20):
    arr = arr - np.mean(arr); n = len(arr)
    var = np.var(arr)
    if var < 1e-9: return [0.0]*max_lag
    out = []
    for k in range(1, min(max_lag, n//2) + 1):
        c = np.mean(arr[:-k] * arr[k:])
        out.append(c / var)
    return out
ac = acf(residual_arr, 15)
print(f"  Lag 1: {ac[0]:+.3f}, Lag 2: {ac[1]:+.3f}, Lag 3: {ac[2]:+.3f}, Lag 5: {ac[4]:+.3f}, Lag 10: {ac[9]:+.3f}")
# Significance threshold ~ 2/sqrt(N)
sig = 2.0 / np.sqrt(len(residual_arr))
sig_lags = [(i+1, c) for i, c in enumerate(ac) if abs(c) > sig]
print(f"  Significance threshold: ±{sig:.3f}")
if sig_lags:
    print(f"  Significant autocorrelation at lags: {sig_lags[:5]}")
else:
    print(f"  No significant autocorrelation — residual is white-noise-like (pure Brownian footprint)")

# ===== Test 3: Bandpass residual at φ-rungs (look for structure) =====
print("\n=== Test 3: Residual amplitude at φ-rungs (looking for non-Brownian peaks) ===")
# For Brownian noise, bandpass amplitude should follow ~constant power per octave (1/f² spectrum)
# For framework-structured residuals, peaks at specific φ-rungs
# Note: residual series is sparse (yearly refit), so we use coarse bandpass at the YEAR scale.
# Multiply lag positions to convert to year units.
sample_period_years = STEP / 12  # 1 year per sample
print(f"  Residual sample spacing: {sample_period_years} years")
RUNG_PERIODS_SAMPLES = []
for k in range(2, 6):  # in sample units (×1 year)
    p = PHI**k
    if p < len(residual_arr) / 3:
        RUNG_PERIODS_SAMPLES.append((k, p))
for k, p in RUNG_PERIODS_SAMPLES:
    bp_res = causal_bandpass(residual_arr, p)
    if len(bp_res) > p*2:
        amp = float(np.std(bp_res[int(len(bp_res)*0.3):]))
        print(f"  φ^{k} ({p:.1f} years): amp={amp:.3f}")

# ===== Test 4: ARA class of residual time series =====
print("\n=== Test 4: ARA of compass residual time series ===")
# Use residual itself as a 'system' and measure its asymmetric ARA at the dominant scale
res_smoothed = gaussian_filter1d(residual_arr, max(1, len(residual_arr)//20))
peaks, _ = find_peaks(res_smoothed)
troughs, _ = find_peaks(-res_smoothed)
if len(peaks) >= 2:
    aras = []
    for i in range(len(peaks)-1):
        seg = residual_arr[peaks[i]:peaks[i+1]+1]
        if len(seg) < 3: continue
        f_t = max(0.15, min(0.85, int(np.argmin(seg)) / max(1, len(seg)-1)))
        aras.append((1 - f_t) / f_t)
    if aras:
        ara_res = float(np.mean(np.clip(aras, 0.3, 3.0)))
        print(f"  Residual mean ARA: {ara_res:.3f}")
        if abs(ara_res - 1.0) < 0.15:
            print(f"  → Clock-class (ARA≈1) — residual is symmetric oscillation, no asymmetric energy bias")
        elif ara_res > 1.2:
            print(f"  → Engine-class (ARA>1.2) — residual has slow-rise/fast-fall structure")
        elif ara_res < 0.8:
            print(f"  → Consumer-class (ARA<0.8) — residual has fast-rise/slow-fall, mean-reverting bias")
    else:
        print(f"  Insufficient cycles for ARA estimation")

print(f"\n=== Summary ===")
print(f"  Compass residual at h={HORIZON} months:")
print(f"  Hurst H = {H:.3f}" if H is not None else "  H unavailable")
print(f"  σ = {residual_arr.std():.3f}°C")
print(f"  N = {len(residual_arr)} forecasts")

# Save
out = dict(method=f"Brownian vs ARA analysis of compass residuals at h={HORIZON}",
           horizon=HORIZON,
           n_forecasts=len(residual_arr),
           residuals=residual_arr.tolist(),
           predictions=[r[2] for r in residuals_h],
           truths=[r[3] for r in residuals_h],
           hurst_exponent=H,
           autocorrelation=ac,
           significance_threshold=float(sig))
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.COMPASS_RESIDUAL = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
