"""
amplitude_residual_horizon_test.py

Two cheap tests targeting the 12-24mo dead zone on the amplitude vehicle:

  (A) Does the SOI_MATCHED amplitude vehicle's residual time series at h=12 and
      h=24 have framework structure (Hurst != 0.5, lag-h autocorr near +/-1/phi^k,
      phi-rung bandpass amplitudes)?  If yes, a corrector should lift it.

  (B) gamma=1/phi residual corrector (causal, lag-h):
        pred_corrected(t,h) = pred(t,h) - gamma * residual(t-h, h)
      residual(t-h, h) is fully closed at origin t (truth at t was observed).
      Apply for each horizon, compare to BASE.

  (C) Horizon-aware gamma_eff(h) in the AR-feedback term itself:
        pred(t,h) = structural(t,h) + gamma_eff(h) * last_h1_residual
      Try three decay shapes:
        gamma_phi:  gamma_eff(h) = (1/phi^3) * (1/phi)^((h-1)/3)
        gamma_exp:  gamma_eff(h) = (1/phi^3) * exp(-(h-1)/3)
        gamma_pers: gamma_eff(h) = (1/phi^3) * 1/(1+(h-1)/phi^3)

Vehicle architecture vendored from rolling_vehicle_closed_test.py (SOI_MATCHED).
Rolling MONTHLY refit so we get a residual time series long enough for stats.
"""
import json, os, time
import numpy as np, pandas as pd
from scipy.signal import butter, lfilter, find_peaks
from scipy.ndimage import gaussian_filter1d

PHI = 1.6180339887498949
INV_PHI  = 1.0 / PHI
INV_PHI3 = 1.0 / (PHI**3)
INV_PHI4 = 1.0 / (PHI**4)

# ---------- IO ----------
def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
AMO_PATH  = _resolve(r"F:\SystemFormulaFolder\HURDAT2\Temp\amonuslong.txt")
TNA_PATH  = _resolve(r"F:\SystemFormulaFolder\HURDAT2\Temp\tna.txt")
PDO_PATH  = _resolve(r"F:\SystemFormulaFolder\PDO_NOAA\ersst.v5.pdo.dat")
IOD_PATH  = _resolve(r"F:\SystemFormulaFolder\IOD_NOAA\dmi.had.long.data")
SOI_PATH  = _resolve(r"F:\SystemFormulaFolder\SOI_NOAA\soi.data")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\amplitude_residual_horizon_data.js")

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

print("Loading data...")
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

# ---------- vehicle internals ----------
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

# ---------- framework constants ----------
RUNGS = [(k, PHI**k) for k in range(4, 14)]
N_RUNGS = len(RUNGS)
K_REF = 8
K_REF_IDX = next(i for i,(k,_) in enumerate(RUNGS) if k == K_REF)
RUNG_WEIGHTS = np.array([PHI**(-abs(k - K_REF)) for k,_ in RUNGS])
RUNG_WEIGHTS = RUNG_WEIGHTS / np.sum(RUNG_WEIGHTS)

# ---------- gamma decay schedules ----------
def gamma_const(h):     return INV_PHI3
def gamma_phi(h):       return INV_PHI3 * (INV_PHI ** ((h-1)/3.0))
def gamma_exp(h):       return INV_PHI3 * np.exp(-(h-1)/3.0)
def gamma_pers(h):      return INV_PHI3 / (1.0 + (h-1)/(PHI**3))

GAMMA_SCHEDULES = {
    'CONST':     gamma_const,
    'GAMMA_PHI': gamma_phi,
    'GAMMA_EXP': gamma_exp,
    'GAMMA_PERS':gamma_pers,
}

def vehicle(refit_t, h, last_h1_residual, gamma_fn):
    """SOI_MATCHED amplitude vehicle, parametrised by horizon-aware gamma."""
    arr_train = NINO[:refit_t]
    mean_train = float(np.mean(arr_train))
    n_train = float(np.std(arr_train)) + 1e-9

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
        f_scale = float(np.std(SYS_local[fn][:refit_t])) + 1e-9
        feeder_arr_norm = feeder_arr / f_scale * n_train
        if fn == 'SOI':
            soi_at_match = feeder_arr_norm[K_REF_IDX]
            feeder_pred += sign * 1.0 * soi_at_match * RUNG_WEIGHTS[K_REF_IDX] * 5
            for ri in range(N_RUNGS):
                if ri == K_REF_IDX: continue
                feeder_pred += sign * (1.0/PHI**abs(RUNGS[ri][0]-K_REF)) * INV_PHI4 * feeder_arr_norm[ri] * RUNG_WEIGHTS[ri]
        else:
            feeder_pred += INV_PHI4 * sign * float(np.dot(RUNG_WEIGHTS, feeder_arr_norm)) / len(feeders)

    structural_pred = mean_train + own_pred + feeder_pred
    pred = structural_pred + gamma_fn(h) * last_h1_residual
    truth = NINO[refit_t + h - 1] if refit_t + h - 1 < N else np.nan
    return pred, truth, structural_pred

# ---------- run rolling forecast ----------
HORIZONS = [1, 3, 6, 12, 24]
MIN_TRAIN = 30 * 12
STEP = 3   # quarterly refit (still plenty of points for residual stats; faster)
import sys
PHASE = sys.argv[1] if len(sys.argv) > 1 else 'ALL'  # 'A' / 'BCD' / 'ALL'
INTERMED = OUT.replace('.js', '_intermediate.npz')

def run_variant(gamma_fn, label):
    print(f"\n--- {label} ---  gamma sample: " +
          ", ".join(f"h={h}:{gamma_fn(h):.4f}" for h in HORIZONS))
    results = {h: [] for h in HORIZONS}
    structural = {h: [] for h in HORIZONS}
    last_h1_residual = 0.0
    t_start = time.time()
    for refit_t in range(MIN_TRAIN, N - max(HORIZONS), STEP):
        for h in HORIZONS:
            if refit_t + h - 1 >= N: continue
            pred, truth, struct = vehicle(refit_t, h, last_h1_residual, gamma_fn)
            results[h].append((refit_t, pred, truth))
            structural[h].append((refit_t, struct, truth))
        if results[1]:
            last_h1_residual = float(results[1][-1][2] - results[1][-1][1])
    print(f"  ran in {time.time()-t_start:.1f}s")
    return results, structural

def metrics(results, label):
    print(f"  {'h':>4}  {'corr':>7}  {'MAE':>6}  {'R2(pers)':>9}  {'dir':>6}  n")
    out = {}
    for h in HORIZONS:
        if not results[h]: continue
        preds  = np.array([r[1] for r in results[h]])
        truths = np.array([r[2] for r in results[h]])
        pers   = np.array([NINO[r[0]-1] for r in results[h]])
        corr   = float(np.corrcoef(preds, truths)[0,1]) if np.std(preds)>1e-9 and np.std(truths)>1e-9 else 0.0
        mae    = float(np.mean(np.abs(preds-truths)))
        ss_res = np.sum((truths-preds)**2); ss_pers = np.sum((truths-pers)**2)
        r2p    = float(1 - ss_res/ss_pers) if ss_pers > 0 else 0.0
        dir_a  = float(np.mean(np.sign(preds-pers) == np.sign(truths-pers)))
        print(f"  h={h:>2}  {corr:+.3f}  {mae:.3f}    {r2p:+.3f}    {dir_a*100:5.1f}%  {len(preds)}")
        out[h] = dict(corr=corr, mae=mae, r2_pers=r2p, dir_acc=dir_a, n=len(preds))
    return out

# =====================================================================
# PHASE A — residual structure on BASE (constant gamma=1/phi^3)
# =====================================================================
if PHASE in ('A','ALL'):
    print("\n=== PHASE A: residual structure of BASE amplitude vehicle ===")
    base_res, base_struct = run_variant(gamma_const, 'BASE (gamma=1/phi^3)')
    base_metrics = metrics(base_res, 'BASE')
    # save intermediate for phase B/C/D
    save = {}
    for h in HORIZONS:
        if base_res[h]:
            arr = np.array(base_res[h], dtype=float)
            save[f'h{h}'] = arr
    np.savez(INTERMED, **save)
    print(f"  saved BASE forecasts -> {INTERMED}")
else:
    print(f"\n--- loading BASE from {INTERMED} ---")
    z = np.load(INTERMED)
    base_res = {}
    for h in HORIZONS:
        key = f'h{h}'
        if key in z:
            base_res[h] = [tuple(row) for row in z[key]]
    base_metrics = metrics(base_res, 'BASE (loaded)')

def hurst(ts, max_lag=20):
    ts = np.asarray(ts, dtype=float)
    if len(ts) < max_lag*4: return None
    lags = range(2, max_lag)
    rs = []
    for lag in lags:
        d = ts[lag:] - ts[:-lag]
        if np.std(d) < 1e-9: continue
        rs.append(np.std(d))
    if len(rs) < 5: return None
    log_lags = np.log(list(lags)[:len(rs)])
    log_rs = np.log(rs)
    slope, _ = np.polyfit(log_lags, log_rs, 1)
    return float(slope)

def autocorr(ts, lag):
    ts = np.asarray(ts, dtype=float)
    if len(ts) <= lag+1: return 0.0
    a = ts[:-lag] - np.mean(ts[:-lag])
    b = ts[lag:] - np.mean(ts[lag:])
    den = (np.std(a)*np.std(b))
    return float(np.mean(a*b)/den) if den > 1e-9 else 0.0

if PHASE in ('A','ALL','BCD'):
    print("\n--- residual structure per horizon ---")
    print(f"  {'h':>3}  {'lag-1':>7}  {'lag-h':>7}  {'Hurst':>7}  {'std':>6}  n")
    res_stats = {}
    for h in HORIZONS:
        rec = base_res[h]
        if len(rec) < 60: continue
        resid = np.array([r[2]-r[1] for r in rec])
        l1 = autocorr(resid, 1)
        lh = autocorr(resid, h)
        hu = hurst(resid)
        print(f"  {h:>3}  {l1:+.3f}    {lh:+.3f}    "
              f"{hu if hu is None else f'{hu:+.3f}':>7}    {np.std(resid):.3f}  {len(resid)}")
        res_stats[h] = dict(lag1=l1, lagh=lh, hurst=hu, std=float(np.std(resid)), n=len(resid))

    # Reference: 1/phi = 0.618, 1/phi^2 = 0.382, 1/phi^3 = 0.236, 1/phi^4 = 0.146
    print("  reference: 1/phi=0.618  1/phi^2=0.382  1/phi^3=0.236  1/phi^4=0.146")

# =====================================================================
# PHASE B — apply causal lag-h corrector gamma=1/phi to BASE predictions
# =====================================================================
# corrected(t,h) = pred(t,h) - gamma * residual(t-h, h)
# residual(t-h, h) is fully closed at origin t (truth at time (t-h)+h = t).
print("\n=== PHASE B: causal lag-h corrector gamma=1/phi on BASE ===")

def apply_lagh_corrector(base_results, gamma_value, base_metrics_label="BASE"):
    out_metrics = {}
    print(f"\n--- corrector gamma={gamma_value:.4f} (=1/phi if 0.618) ---")
    print(f"  {'h':>4}  {'BASE corr':>10}  {'CORR corr':>10}  {'BASE MAE':>9}  {'CORR MAE':>9}  {'BASE R2p':>9}  {'CORR R2p':>9}")
    for h in HORIZONS:
        recs = base_results[h]
        if len(recs) < h+30: continue
        # build aligned arrays indexed by origin index in recs
        origins = np.array([r[0] for r in recs])
        preds   = np.array([r[1] for r in recs])
        truths  = np.array([r[2] for r in recs])
        # For each forecast origin t, find the residual at the origin t-h with same horizon h.
        # That older forecast's truth is at time (t-h)+h = t — fully observed by origin t.
        origin_to_idx = {ot:i for i,ot in enumerate(origins)}
        corrected = preds.copy()
        for i, t in enumerate(origins):
            t_back = t - h
            if t_back in origin_to_idx:
                j = origin_to_idx[t_back]
                resid_back = truths[j] - preds[j]
                corrected[i] = preds[i] + gamma_value * resid_back
        pers   = np.array([NINO[t-1] for t in origins])
        cb = base_metrics.get(h, {})
        c_corr = float(np.corrcoef(corrected, truths)[0,1]) if np.std(corrected)>1e-9 else 0.0
        c_mae  = float(np.mean(np.abs(corrected-truths)))
        ss_res_c = np.sum((truths-corrected)**2); ss_pers = np.sum((truths-pers)**2)
        c_r2p  = float(1 - ss_res_c/ss_pers) if ss_pers > 0 else 0.0
        c_dir  = float(np.mean(np.sign(corrected-pers) == np.sign(truths-pers)))
        print(f"  h={h:>2}  {cb.get('corr',0):+.3f}      {c_corr:+.3f}      "
              f"{cb.get('mae',0):.3f}     {c_mae:.3f}     "
              f"{cb.get('r2_pers',0):+.3f}    {c_r2p:+.3f}")
        out_metrics[h] = dict(corr=c_corr, mae=c_mae, r2_pers=c_r2p, dir_acc=c_dir,
                              base_corr=cb.get('corr',0), base_mae=cb.get('mae',0),
                              base_r2p=cb.get('r2_pers',0))
    return out_metrics

if PHASE in ('BCD','ALL'):
    corr_metrics = apply_lagh_corrector(base_res, INV_PHI)
    # also try gamma=1/phi^2 and 1/phi^3 to see which lifts at long lead
    corr_phi2_metrics = apply_lagh_corrector(base_res, 1.0/PHI**2)
    corr_phi3_metrics = apply_lagh_corrector(base_res, INV_PHI3)
else:
    corr_metrics = corr_phi2_metrics = corr_phi3_metrics = {}

# =====================================================================
# PHASE C — horizon-aware gamma_eff(h) in the AR-feedback term
# =====================================================================
schedule_metrics = {'CONST': base_metrics}
if PHASE in ('BCD','ALL'):
    print("\n=== PHASE C: horizon-aware gamma_eff(h) on AR-feedback term ===")
    for label, gfn in GAMMA_SCHEDULES.items():
        if label == 'CONST': continue
        res, _ = run_variant(gfn, label)
        schedule_metrics[label] = metrics(res, label)

# =====================================================================
# PHASE D — best stack: best gamma_eff schedule + lag-h corrector
# =====================================================================
stacked_metrics = {}
best_label = 'CONST'
if PHASE in ('BCD','ALL'):
    print("\n=== PHASE D: best gamma schedule + lag-h corrector at h>=12 ===")
    best_score = -1e9
    for label, m in schedule_metrics.items():
        score = m.get(12,{}).get('r2_pers',-1e9) + m.get(24,{}).get('r2_pers',-1e9)
        if score > best_score:
            best_score = score; best_label = label
    print(f"  best gamma schedule (by sum h12 + h24 R2(pers)): {best_label}")
    if best_label != 'CONST':
        best_res, _ = run_variant(GAMMA_SCHEDULES[best_label], f'{best_label} (best)')
        _ = metrics(best_res, best_label)
        stacked_metrics = apply_lagh_corrector(best_res, INV_PHI)
    else:
        stacked_metrics = apply_lagh_corrector(base_res, INV_PHI)

out = dict(
    method="amplitude vehicle gamma corrector + horizon-aware schedule test",
    base_metrics=base_metrics,
    residual_structure=res_stats,
    corrector_phi=corr_metrics,
    corrector_phi2=corr_phi2_metrics,
    corrector_phi3=corr_phi3_metrics,
    schedule_metrics=schedule_metrics,
    best_schedule=best_label,
    stacked_best_plus_corrector=stacked_metrics,
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.AMP_RES_HORIZON = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
