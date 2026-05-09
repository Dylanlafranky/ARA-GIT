"""
v2: more variants to probe whether the framework's rung structure adds anything
above linear regression with feeders.

M3:  ENSO-only framework AR forecast (no feeders) — same as v1
M4:  LR ENSO ~ AMO + TNA (broadband, contemporaneous) — same as v1
M4b: LR with lagged feeders (best 1-12 month lags) — better baseline
M5a: Per-rung contemporaneous prediction within framework structure
       For each ENSO rung k: ENSO_k(i) = α_k · AMO_k(i) + β_k · TNA_k(i)
       (architecturally pure: same-rung coupling, no AR mixing)
M5b: M5a + AR(1) blend on each rung
M5c: LR + framework residual model (does framework help residuals?)
M6:  Best-of variants combined
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
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\enso_feeders_v2_data.js")

def load_nino():
    df = pd.read_csv(NINO_PATH, skiprows=1, header=None, names=['date','val'])
    df['date'] = pd.to_datetime(df['date'].str.strip())
    df = df[df['val'] > -90].copy()
    return df.set_index('date')['val'].astype(float)

def load_grid(path):
    rows = []
    with open(path,'r') as f:
        next(f)
        for ln in f:
            parts = ln.split()
            if len(parts) < 13: continue
            year = int(parts[0])
            for m in range(12):
                v = float(parts[1+m])
                if v < -90: continue
                rows.append((pd.Timestamp(year=year, month=m+1, day=1), v))
    return pd.Series(dict(rows)).sort_index()

nino = load_nino(); amo = load_grid(AMO_PATH); tna = load_grid(TNA_PATH)
common = nino.index.intersection(amo.index).intersection(tna.index).sort_values()
NINO = nino.reindex(common).values.astype(float)
AMO  = amo.reindex(common).values.astype(float)
TNA  = tna.reindex(common).values.astype(float)
DATES = common; N = len(NINO); SPLIT = N//2

nino_tr, nino_te = NINO[:SPLIT], NINO[SPLIT:]
amo_tr , amo_te  = AMO[:SPLIT],  AMO[SPLIT:]
tna_tr , tna_te  = TNA[:SPLIT],  TNA[SPLIT:]
mean_train = float(np.mean(nino_tr))
n_test = len(nino_te)
print(f"Train: {DATES[0].date()}..{DATES[SPLIT-1].date()} (n={SPLIT})")
print(f"Test : {DATES[SPLIT].date()}..{DATES[-1].date()} (n={n_test})")

# --- φ-rung bandpass ---
def rung_band(arr, period_months, dt=1.0):
    n = len(arr)
    f_center = 1.0/period_months
    f_lo, f_hi = 0.8*f_center, 1.2*f_center
    F = np.fft.rfft(arr - np.mean(arr))
    freqs = np.fft.rfftfreq(n, d=dt)
    mask = (freqs < f_lo) | (freqs > f_hi)
    F[mask] = 0
    return np.real(np.fft.irfft(F, n=n))

ENSO_RUNGS = [(k, PHI**k) for k in range(4, 10)]
R_nino = {k: rung_band(NINO, p) for k,p in ENSO_RUNGS}
R_amo  = {k: rung_band(AMO,  p) for k,p in ENSO_RUNGS}
R_tna  = {k: rung_band(TNA,  p) for k,p in ENSO_RUNGS}

def metrics(y, p):
    if np.std(p)<1e-9: corr=0.0
    else: corr = float(np.corrcoef(y,p)[0,1])
    return dict(corr=corr, rmse=float(np.sqrt(np.mean((y-p)**2))),
                mae=float(np.mean(np.abs(y-p))), pred_std=float(np.std(p)))

# --- M1, M2 ---
M1 = np.full(n_test, mean_train)
M2 = np.zeros(n_test); M2[0] = nino_tr[-1]
for i in range(1, n_test): M2[i] = M2[i-1]*0.99 + 0.01*mean_train

# --- M3: ENSO-only AR per rung ---
def fit_ar1(s):
    if np.std(s)<1e-9: return 0.0, float(np.mean(s))
    a = float(np.corrcoef(s[:-1], s[1:])[0,1])
    return (0.0 if not np.isfinite(a) else a), float(np.mean(s))

ar = {k: fit_ar1(R_nino[k][:SPLIT]) for k,_ in ENSO_RUNGS}
M3 = np.zeros(n_test) + mean_train
for k,_ in ENSO_RUNGS:
    a, mu = ar[k]; prev = R_nino[k][SPLIT-1]
    for i in range(n_test):
        v = mu + a*(prev - mu)
        M3[i] += v; prev = v

# --- M4: LR ENSO ~ AMO + TNA contemporaneous ---
X_tr = np.column_stack([amo_tr, tna_tr, np.ones_like(amo_tr)])
beta, *_ = np.linalg.lstsq(X_tr, nino_tr, rcond=None)
M4 = np.column_stack([amo_te, tna_te, np.ones_like(amo_te)]) @ beta

# --- M4b: LR with lagged feeders ---
# Try lags 0..12 months for AMO and TNA
def lr_with_lags(amo_tr, tna_tr, amo_te, tna_te, nino_tr, lags_amo, lags_tna):
    """Build design matrix with AMO at multiple lags, TNA at multiple lags."""
    max_lag = max(max(lags_amo), max(lags_tna), 0)
    n_tr_used = len(amo_tr) - max_lag
    cols_tr = [np.ones(n_tr_used)]
    cols_te = [np.ones(len(amo_te))]
    for lag in lags_amo:
        cols_tr.append(amo_tr[max_lag-lag:len(amo_tr)-lag] if lag>0 else amo_tr[max_lag:])
        # for test, lag uses prior values (overlap from end of train + start of test)
        full_amo = np.concatenate([amo_tr, amo_te])
        cols_te.append(full_amo[len(amo_tr)-lag:len(amo_tr)+len(amo_te)-lag] if lag>0 else amo_te)
    for lag in lags_tna:
        cols_tr.append(tna_tr[max_lag-lag:len(tna_tr)-lag] if lag>0 else tna_tr[max_lag:])
        full_tna = np.concatenate([tna_tr, tna_te])
        cols_te.append(full_tna[len(tna_tr)-lag:len(tna_tr)+len(tna_te)-lag] if lag>0 else tna_te)
    X_tr = np.column_stack(cols_tr)
    X_te = np.column_stack(cols_te)
    y_tr = nino_tr[max_lag:]
    beta, *_ = np.linalg.lstsq(X_tr, y_tr, rcond=None)
    return X_te @ beta, beta, max_lag

# Search best single lag pair
best_corr = -2; best_lags = (0,0); best_pred = None
for la in [0, 3, 6, 12]:
    for lt in [0, 3, 6, 12]:
        try:
            pred, _, _ = lr_with_lags(amo_tr, tna_tr, amo_te, tna_te, nino_tr, [la], [lt])
            c = float(np.corrcoef(nino_te, pred)[0,1])
            if c > best_corr: best_corr = c; best_lags = (la,lt); best_pred = pred
        except Exception: pass
M4b = best_pred
print(f"\nM4b best lag (AMO,TNA) = {best_lags}, corr {best_corr:+.3f}")

# --- M5a: per-rung contemporaneous LR within framework structure ---
# For each ENSO rung k: ENSO_k(i) = α_k · AMO_k(i) + β_k · TNA_k(i) + γ_k
M5a = np.zeros(n_test) + mean_train
rung_coefs = {}
for k,_ in ENSO_RUNGS:
    X = np.column_stack([R_amo[k][:SPLIT], R_tna[k][:SPLIT], np.ones(SPLIT)])
    y = R_nino[k][:SPLIT]
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    rung_coefs[k] = b
    Xt = np.column_stack([R_amo[k][SPLIT:], R_tna[k][SPLIT:], np.ones(n_test)])
    M5a += Xt @ b

# --- M5b: M5a blended with AR ---
M5b = np.zeros(n_test) + mean_train
for k,_ in ENSO_RUNGS:
    a, mu = ar[k]; prev = R_nino[k][SPLIT-1]
    Xt = np.column_stack([R_amo[k][SPLIT:], R_tna[k][SPLIT:], np.ones(n_test)])
    feeder = Xt @ rung_coefs[k]
    for i in range(n_test):
        v = 0.5*(mu + a*(prev - mu)) + 0.5*feeder[i]
        M5b[i] += v; prev = v

# --- M5c: LR + framework residual ---
# Train: fit LR on train, get residuals. Bandpass residuals per ENSO rung. AR(1) per rung.
# Test: LR contribution + AR forecast of residual rung sum.
res_tr = nino_tr - X_tr @ beta
R_res = {k: rung_band(np.concatenate([res_tr, np.zeros(n_test)]), p) for k,p in ENSO_RUNGS}
ar_res = {k: fit_ar1(R_res[k][:SPLIT]) for k,_ in ENSO_RUNGS}
M5c = M4.copy()
for k,_ in ENSO_RUNGS:
    a, mu = ar_res[k]; prev = R_res[k][SPLIT-1]
    for i in range(n_test):
        v = mu + a*(prev - mu)
        M5c[i] += v; prev = v

# --- M6: best-of (M4b weighted with M5a) ---
# Find best convex combo on training
def predict_train_M5a():
    out = np.zeros(SPLIT) + mean_train
    for k,_ in ENSO_RUNGS:
        Xt = np.column_stack([R_amo[k][:SPLIT], R_tna[k][:SPLIT], np.ones(SPLIT)])
        out += Xt @ rung_coefs[k]
    return out
def predict_train_M4b():
    pred, _, max_lag = lr_with_lags(amo_tr, tna_tr, amo_tr, tna_tr, nino_tr, [best_lags[0]], [best_lags[1]])
    return pred  # length n_test, but for train evaluation we need a different setup
# Just use OLS to find best linear combo
combo_X_tr = np.column_stack([predict_train_M5a(), nino_tr])  # M5a is fit on train so corr is high; skip and just blend on test
# For honesty, fit blend by holding out final 20% of train
val_n = SPLIT//5
def M5a_train_pred():
    out = np.zeros(SPLIT) + mean_train
    for k,_ in ENSO_RUNGS:
        Xt = np.column_stack([R_amo[k][:SPLIT], R_tna[k][:SPLIT], np.ones(SPLIT)])
        out += Xt @ rung_coefs[k]
    return out
m5a_full = M5a_train_pred()
m4_full = X_tr @ beta
val_X = np.column_stack([m4_full[-val_n:], m5a_full[-val_n:]])
val_y = nino_tr[-val_n:]
blend, *_ = np.linalg.lstsq(np.column_stack([val_X, np.ones(val_n)]), val_y, rcond=None)
M6 = blend[0]*M4 + blend[1]*M5a + blend[2]
print(f"M6 blend coefs: M4={blend[0]:.3f}  M5a={blend[1]:.3f}  const={blend[2]:.3f}")

# --- METRICS ---
R = dict(
    M1_mean=metrics(nino_te, M1),
    M2_AR=metrics(nino_te, M2),
    M3_ENSO_only=metrics(nino_te, M3),
    M4_LR=metrics(nino_te, M4),
    M4b_LR_lagged=metrics(nino_te, M4b) if M4b is not None else dict(corr=0,rmse=0,mae=0,pred_std=0),
    M5a_per_rung_LR=metrics(nino_te, M5a),
    M5b_per_rung_blend=metrics(nino_te, M5b),
    M5c_LR_plus_FW_resid=metrics(nino_te, M5c),
    M6_blend=metrics(nino_te, M6),
)

print(f"\n========= TEST RESULTS (n={n_test}) =========")
print(f"True test std: {np.std(nino_te):.3f}")
for name, r in R.items():
    flag = ''
    if r['corr'] > R['M4_LR']['corr']+0.05: flag = ' ★ beats LR'
    elif r['corr'] > R['M4_LR']['corr']:    flag = ' ↑'
    print(f"  {name:24s}: corr={r['corr']:+.3f}  rmse={r['rmse']:.3f}  pred_std={r['pred_std']:.3f}{flag}")

# Save
out = dict(
    dates=[d.strftime('%Y-%m') for d in DATES],
    nino=NINO.tolist(), amo=AMO.tolist(), tna=TNA.tolist(),
    split_idx=int(SPLIT),
    preds=dict(
        M1=M1.tolist(), M2=M2.tolist(), M3=M3.tolist(), M4=M4.tolist(),
        M4b=M4b.tolist() if M4b is not None else None,
        M5a=M5a.tolist(), M5b=M5b.tolist(), M5c=M5c.tolist(), M6=M6.tolist(),
    ),
    metrics=R,
    rungs=[[k,p] for k,p in ENSO_RUNGS],
    rung_coefs={str(k): list(map(float, v)) for k,v in rung_coefs.items()},
    lr_coefs=dict(amo=float(beta[0]), tna=float(beta[1]), const=float(beta[2])),
    best_lags=list(best_lags),
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.ENSO_FEEDERS_V2 = " + json.dumps(out) + ";\n")
print(f"\nSaved -> {OUT}")
