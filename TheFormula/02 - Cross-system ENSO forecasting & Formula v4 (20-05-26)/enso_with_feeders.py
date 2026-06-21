"""
TOPOLOGY + FLOW test: predict ENSO using AMO + TNA as upstream feeders.

Per Dylan 2026-05-01:
  Open systems → map the next 2 closest ARA systems that feed in.
  Their structures + state become forcing input to the target.

Setup:
  - 3 monthly time series 1948-2023 (76 years, 912 months)
  - Train: first half (1948-1985, 38yr)   Test: second half (1986-2023, 38yr)

Comparisons (all on TEST half):
  M1 - ENSO mean-only baseline
  M2 - AR-blind on ENSO (decay to mean)
  M3 - ENSO-only φ-rung framework forecast (no feeders)
  M4 - Linear regression of ENSO ~ AMO + TNA contemporaneous (uses observed test feeders, no framework structure)
  M5 - Framework with feeders: ENSO each-rung-ARA driven by AR(1) + coupling-weighted pull from AMO + TNA contemporaneous rung-ARAs (uses observed test feeders + framework structure)

If M5 > M4 > M3, the topology+flow architecture adds value beyond
both "no feeders" and "feeders without structure".
"""
import json, re, math, os
import numpy as np, pandas as pd

PHI = 1.6180339887498949

def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
AMO_PATH  = _resolve(r"F:\SystemFormulaFolder\HURDAT2\Temp\amonuslong.txt")
TNA_PATH  = _resolve(r"F:\SystemFormulaFolder\HURDAT2\Temp\tna.txt")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\enso_feeders_data.js")

# --- LOAD ---
def load_nino():
    df = pd.read_csv(NINO_PATH, skiprows=1, header=None, names=['date','val'])
    df['date'] = pd.to_datetime(df['date'].str.strip())
    df = df[df['val'] > -90].copy()
    return df.set_index('date')['val'].astype(float)

def load_grid(path):
    """Load 12-column-per-year format."""
    rows = []
    with open(path,'r') as f:
        next(f)  # header
        for ln in f:
            parts = ln.split()
            if len(parts) < 13: continue
            year = int(parts[0])
            for m in range(12):
                v = float(parts[1+m])
                if v < -90: continue  # missing
                rows.append((pd.Timestamp(year=year, month=m+1, day=1), v))
    s = pd.Series(dict(rows)).sort_index()
    return s

nino = load_nino()
amo  = load_grid(AMO_PATH)
tna  = load_grid(TNA_PATH)
print(f"NINO: {nino.index.min().date()} → {nino.index.max().date()}, n={len(nino)}")
print(f"AMO : {amo.index.min().date()} → {amo.index.max().date()}, n={len(amo)}")
print(f"TNA : {tna.index.min().date()} → {tna.index.max().date()}, n={len(tna)}")

# Common date range
common = nino.index.intersection(amo.index).intersection(tna.index)
common = common.sort_values()
print(f"Overlap: {common.min().date()} → {common.max().date()}, n={len(common)}")

NINO = nino.reindex(common).values.astype(float)
AMO  = amo.reindex(common).values.astype(float)
TNA  = tna.reindex(common).values.astype(float)
DATES = common

N = len(NINO); SPLIT = N//2
def split(arr):
    return arr[:SPLIT], arr[SPLIT:]
nino_tr, nino_te = split(NINO)
amo_tr , amo_te  = split(AMO)
tna_tr , tna_te  = split(TNA)
dates_tr, dates_te = split(DATES)
print(f"Train: {dates_tr[0].date()}..{dates_tr[-1].date()} (n={len(nino_tr)})")
print(f"Test : {dates_te[0].date()}..{dates_te[-1].date()} (n={len(nino_te)})")

# --- ROLLING ARA (a system's slow ARA over time, our key descriptor) ---
def rolling_ARA(arr, win=12):
    """Per-window ARA: T_acc/T_rel approximated by ratio of mean-above-window-mean to mean-below."""
    out = np.full(len(arr), np.nan)
    for i in range(win, len(arr)-win):
        seg = arr[i-win:i+win]
        m = np.mean(seg)
        above = seg[seg>m] - m
        below = m - seg[seg<m]
        if len(above)>0 and len(below)>0 and np.sum(below)>0:
            out[i] = float(np.sum(above)/np.sum(below))
    # fill NaN with mean
    out[np.isnan(out)] = np.nanmean(out) if np.any(~np.isnan(out)) else 1.0
    return out

# --- φ-RUNG SCALE DECOMPOSITION (band-power per rung) ---
def rung_band_signal(arr, period_months, dt_months=1.0):
    """Bandpass arr around target period (±20%) using FFT zeroing."""
    n = len(arr)
    f_center = 1.0/period_months  # cycles/month
    f_lo, f_hi = 0.8*f_center, 1.2*f_center
    F = np.fft.rfft(arr - np.mean(arr))
    freqs = np.fft.rfftfreq(n, d=dt_months)
    mask = (freqs < f_lo) | (freqs > f_hi)
    F[mask] = 0
    return np.real(np.fft.irfft(F, n=n))

# Rung months for ENSO (φ³ ≈ 4.24 months pump, then up the ladder)
# Use rungs from φ^4 (~7 months, intra-annual) to φ^9 (~76 months ≈ 6.3 yr) — covers ENSO 2-7yr span
def phi_rungs_months(k_min, k_max):
    return [(k, PHI**k) for k in range(k_min, k_max+1)]

ENSO_RUNGS = phi_rungs_months(4, 9)  # φ^4..φ^9 in months: 7, 11, 18, 29, 47, 76
print(f"\nENSO rungs (months): {[(k, round(p,1)) for k,p in ENSO_RUNGS]}")

# --- BUILD per-rung "rung amplitude" series for each system ---
def build_rung_series(arr, rungs):
    """Returns dict {k: bandpassed signal at that rung}."""
    return {k: rung_band_signal(arr, p) for k,p in rungs}

R_nino = build_rung_series(NINO, ENSO_RUNGS)
R_amo  = build_rung_series(AMO,  ENSO_RUNGS)
R_tna  = build_rung_series(TNA,  ENSO_RUNGS)

# --- COUPLING MAP (per ENSO rung, find which AMO/TNA rungs correlate on training half) ---
def coupling_map_train(target_rungs, source_rungs, train_end_idx):
    """Returns dict {(target_k, source_k): correlation on training half}."""
    out = {}
    for tk, ts in target_rungs.items():
        for sk, ss in source_rungs.items():
            ts_tr = ts[:train_end_idx]; ss_tr = ss[:train_end_idx]
            if np.std(ts_tr)<1e-9 or np.std(ss_tr)<1e-9:
                out[(tk,sk)] = 0.0
            else:
                out[(tk,sk)] = float(np.corrcoef(ts_tr, ss_tr)[0,1])
    return out

CM_amo = coupling_map_train(R_nino, R_amo, SPLIT)
CM_tna = coupling_map_train(R_nino, R_tna, SPLIT)

print("\nENSO ← AMO coupling matrix (training corr by rung):")
print("  ENSOk\\AMOk  " + "  ".join([f"{k:>6d}" for k,_ in ENSO_RUNGS]))
for tk,_ in ENSO_RUNGS:
    row = "  k=" + str(tk).rjust(8) + "  " + "  ".join([f"{CM_amo[(tk,sk)]:+.3f}" for sk,_ in ENSO_RUNGS])
    print(row)
print("\nENSO ← TNA coupling matrix:")
for tk,_ in ENSO_RUNGS:
    row = "  k=" + str(tk).rjust(8) + "  " + "  ".join([f"{CM_tna[(tk,sk)]:+.3f}" for sk,_ in ENSO_RUNGS])
    print(row)

# --- M3: ENSO-only framework forecast ---
# For each rung, fit AR(1) on training rung-amp signal, project forward
def fit_ar1(series_tr):
    if np.std(series_tr) < 1e-9: return 0.0, np.mean(series_tr), 0.0
    a = float(np.corrcoef(series_tr[:-1], series_tr[1:])[0,1])
    if not np.isfinite(a): a = 0.0
    mu = float(np.mean(series_tr))
    sigma_resid = float(np.std(series_tr) * math.sqrt(max(1e-9, 1.0-a*a)))
    return a, mu, sigma_resid

ar_params = {k: fit_ar1(R_nino[k][:SPLIT]) for k,_ in ENSO_RUNGS}

def forecast_rung_ar1(k, n_test, last_train_val):
    a, mu, _ = ar_params[k]
    out = np.zeros(n_test)
    prev = last_train_val
    for i in range(n_test):
        out[i] = mu + a*(prev - mu)  # noiseless mean-forecast
        prev = out[i]
    return out

n_test = len(nino_te)
nino_pred_local = np.zeros(n_test)
for k,_ in ENSO_RUNGS:
    last = R_nino[k][SPLIT-1]
    pred_k = forecast_rung_ar1(k, n_test, last)
    nino_pred_local += pred_k
mean_train = float(np.mean(nino_tr))
nino_pred_local += mean_train

# --- M5: framework with feeders ---
# Each ENSO rung's prediction at month i =
#   AR(1) projection from previous step
#   + Σ_sk α(tk,sk) * (R_amo[sk][i] - mean_amo_rung_train) * coupling_weight(amo)
#   + Σ_sk α(tk,sk) * (R_tna[sk][i] - mean_tna_rung_train) * coupling_weight(tna)
# coupling weight = corr on training; only include |corr|>0.20

def feeder_pull(k_target, sk_source, R_source, mean_source_rung, idx, CM):
    c = CM.get((k_target, sk_source), 0.0)
    if abs(c) < 0.20: return 0.0
    return c * (R_source[sk_source][idx] - mean_source_rung)

mean_amo_rung_tr = {sk: float(np.mean(R_amo[sk][:SPLIT])) for sk,_ in ENSO_RUNGS}
mean_tna_rung_tr = {sk: float(np.mean(R_tna[sk][:SPLIT])) for sk,_ in ENSO_RUNGS}
mean_nino_rung_tr = {tk: float(np.mean(R_nino[tk][:SPLIT])) for tk,_ in ENSO_RUNGS}

# Calibrate the feeder gain on training data (one global gain)
# For each rung, predict training values from AR(1) + sum of feeder pulls; OLS for global gain
def predict_rung_feeders(k_target, indices, gain):
    a, mu, _ = ar_params[k_target]
    n_idx = len(indices); out = np.zeros(n_idx)
    prev = R_nino[k_target][indices[0]-1] if indices[0]>0 else mu
    for j, i in enumerate(indices):
        ar_proj = mu + a*(prev - mu)
        pull_amo = sum(feeder_pull(k_target, sk, R_amo, mean_amo_rung_tr[sk], i, CM_amo) for sk,_ in ENSO_RUNGS)
        pull_tna = sum(feeder_pull(k_target, sk, R_tna, mean_tna_rung_tr[sk], i, CM_tna) for sk,_ in ENSO_RUNGS)
        out[j] = ar_proj + gain * (pull_amo + pull_tna)
        prev = out[j]
    return out

# Find gain by minimizing training-period error across all rungs
def total_train_err(gain):
    e = 0.0
    train_idx = list(range(1, SPLIT))
    for k,_ in ENSO_RUNGS:
        pred = predict_rung_feeders(k, train_idx, gain)
        truth = R_nino[k][1:SPLIT]
        e += np.sum((pred - truth)**2)
    return e

# Simple golden-section / grid search
gains = np.linspace(0.0, 2.0, 41)
errs = [total_train_err(g) for g in gains]
best_gain = float(gains[int(np.argmin(errs))])
print(f"\nBest training gain: {best_gain:.3f}")

# Now produce M5 prediction on test half
test_idx = list(range(SPLIT, N))
nino_pred_feeders = np.zeros(n_test)
for k,_ in ENSO_RUNGS:
    nino_pred_feeders += predict_rung_feeders(k, test_idx, best_gain)
nino_pred_feeders += mean_train

# --- M4: linear regression of ENSO on AMO+TNA contemporaneous ---
# Fit on training, apply to test
X_tr = np.column_stack([amo_tr, tna_tr, np.ones_like(amo_tr)])
beta, *_ = np.linalg.lstsq(X_tr, nino_tr, rcond=None)
X_te = np.column_stack([amo_te, tna_te, np.ones_like(amo_te)])
nino_pred_lr = X_te @ beta
print(f"Linear regression coefs: AMO={beta[0]:.3f} TNA={beta[1]:.3f} const={beta[2]:.3f}")

# --- M2: AR-blind ---
nino_pred_ar = np.zeros(n_test)
nino_pred_ar[0] = nino_tr[-1]
for i in range(1, n_test):
    nino_pred_ar[i] = nino_pred_ar[i-1]*0.99 + 0.01*mean_train

# --- M1: mean-only ---
nino_pred_mean = np.full(n_test, mean_train)

# --- METRICS ---
def metrics(y, p):
    if np.std(p)<1e-9: corr=0.0
    else: corr = float(np.corrcoef(y,p)[0,1])
    return dict(corr=corr, rmse=float(np.sqrt(np.mean((y-p)**2))),
                mae=float(np.mean(np.abs(y-p))), pred_std=float(np.std(p)))

R = dict(
    M1_mean       = metrics(nino_te, nino_pred_mean),
    M2_AR_blind   = metrics(nino_te, nino_pred_ar),
    M3_ENSO_only  = metrics(nino_te, nino_pred_local),
    M4_LR_feeders = metrics(nino_te, nino_pred_lr),
    M5_FW_feeders = metrics(nino_te, nino_pred_feeders),
)
print(f"\n========= TEST RESULTS (n={n_test} months) =========")
print(f"True test std: {np.std(nino_te):.3f}")
for name, r in R.items():
    print(f"  {name:18s}: corr={r['corr']:+.3f}  rmse={r['rmse']:.3f}  mae={r['mae']:.3f}  pred_std={r['pred_std']:.3f}")
print(f"\nKey deltas:")
print(f"  M5 - M4 (framework adds beyond LR): {R['M5_FW_feeders']['corr'] - R['M4_LR_feeders']['corr']:+.3f}")
print(f"  M5 - M3 (feeders add beyond ENSO-only): {R['M5_FW_feeders']['corr'] - R['M3_ENSO_only']['corr']:+.3f}")
print(f"  M4 - M3 (any feeders add anything): {R['M4_LR_feeders']['corr'] - R['M3_ENSO_only']['corr']:+.3f}")

# --- SAVE ---
out = dict(
    dates=[d.strftime('%Y-%m') for d in DATES],
    nino=NINO.tolist(), amo=AMO.tolist(), tna=TNA.tolist(),
    split_idx=int(SPLIT),
    nino_pred=dict(
        mean=nino_pred_mean.tolist(),
        ar=nino_pred_ar.tolist(),
        local=nino_pred_local.tolist(),
        lr=nino_pred_lr.tolist(),
        feeders=nino_pred_feeders.tolist(),
    ),
    metrics=R,
    rungs=[[k, p] for k,p in ENSO_RUNGS],
    best_gain=best_gain,
    coupling_amo={f"{k1}_{k2}":v for (k1,k2),v in CM_amo.items()},
    coupling_tna={f"{k1}_{k2}":v for (k1,k2),v in CM_tna.items()},
    lr_coefs=dict(amo=float(beta[0]), tna=float(beta[1]), const=float(beta[2])),
)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write("window.ENSO_FEEDERS = " + json.dumps(out) + ";\n")
print(f"\nSaved -> {OUT}")
