"""
Multi-feeder climate test: predict ENSO using AMO + TNA + PDO as upstream feeders.

DATA SOURCES (all verifiable public NOAA):
  ENSO Niño 3.4: F:/SystemFormulaFolder/Nino34/nino34.long.anom.csv
                 (NOAA PSL, https://psl.noaa.gov/data/timeseries/month/)
  AMO unsmoothed: F:/SystemFormulaFolder/HURDAT2/Temp/amonuslong.txt
                 (NOAA PSL)
  TNA: F:/SystemFormulaFolder/HURDAT2/Temp/tna.txt
                 (NOAA PSL)
  PDO: F:/SystemFormulaFolder/PDO_NOAA/ersst.v5.pdo.dat
                 (NOAA NCEI ERSST V5, https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/index/ersst.v5.pdo.dat)

Question: does adding a third feeder (PDO) increase prediction lift?
Hypothesis (per Dylan's principle): more upstream topologies → more lift.

Models:
  M1  mean-only baseline
  M2  AR-blind (persistence)
  M3  ENSO-only framework (no feeders)
  M4  LR with all 3 feeders broadband (contemporaneous)
  M4b LR with all 3 feeders, hand-searched lags
  M5_2feeder framework with AMO+TNA only (the prior result, recomputed on this overlap)
  M5_3feeder framework with AMO+TNA+PDO
  M5b_3feeder framework + AR memory blend
"""
import json, os, math
import numpy as np, pandas as pd

PHI = 1.6180339887498949

def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
AMO_PATH  = _resolve(r"F:\SystemFormulaFolder\HURDAT2\Temp\amonuslong.txt")
TNA_PATH  = _resolve(r"F:\SystemFormulaFolder\HURDAT2\Temp\tna.txt")
PDO_PATH  = _resolve(r"F:\SystemFormulaFolder\PDO_NOAA\ersst.v5.pdo.dat")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\enso_three_feeders_data.js")

# --- LOADERS ---
def load_nino():
    df = pd.read_csv(NINO_PATH, skiprows=1, header=None, names=['date','val'])
    df['date'] = pd.to_datetime(df['date'].str.strip())
    df = df[df['val'] > -90].copy()
    return df.set_index('date')['val'].astype(float)

def load_grid_text(path, header_lines=1):
    """For amonuslong/tna format: first row is range; subsequent rows are year + 12 monthly values."""
    rows = []
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

def load_pdo():
    """ERSST PDO format: 2 header lines, then year + 12 monthly columns; missing=99.99"""
    return load_grid_text(PDO_PATH, header_lines=2)

nino = load_nino()
amo  = load_grid_text(AMO_PATH, header_lines=1)
tna  = load_grid_text(TNA_PATH, header_lines=1)
pdo  = load_pdo()
print(f"NINO: {nino.index.min().date()} → {nino.index.max().date()}, n={len(nino)}")
print(f"AMO : {amo.index.min().date()} → {amo.index.max().date()}, n={len(amo)}")
print(f"TNA : {tna.index.min().date()} → {tna.index.max().date()}, n={len(tna)}")
print(f"PDO : {pdo.index.min().date()} → {pdo.index.max().date()}, n={len(pdo)}")

# --- COMMON OVERLAP ---
common = nino.index.intersection(amo.index).intersection(tna.index).intersection(pdo.index).sort_values()
print(f"\nCommon overlap: {common.min().date()} → {common.max().date()}, n={len(common)}")

NINO = nino.reindex(common).values.astype(float)
AMO  = amo.reindex(common).values.astype(float)
TNA  = tna.reindex(common).values.astype(float)
PDO  = pdo.reindex(common).values.astype(float)
DATES = common
N = len(NINO); SPLIT = N//2

nino_tr, nino_te = NINO[:SPLIT], NINO[SPLIT:]
amo_tr , amo_te  = AMO[:SPLIT],  AMO[SPLIT:]
tna_tr , tna_te  = TNA[:SPLIT],  TNA[SPLIT:]
pdo_tr , pdo_te  = PDO[:SPLIT],  PDO[SPLIT:]
mean_train = float(np.mean(nino_tr))
n_test = len(nino_te)
print(f"Train: {DATES[0].date()}..{DATES[SPLIT-1].date()} (n={SPLIT})")
print(f"Test : {DATES[SPLIT].date()}..{DATES[-1].date()} (n={n_test})")

# --- φ-rung bandpass ---
def rung_band(arr, period_months, dt=1.0, bw=0.2):
    n = len(arr); F = np.fft.rfft(arr - np.mean(arr))
    freqs = np.fft.rfftfreq(n, d=dt)
    f_c = 1.0/period_months
    F[(freqs<(1-bw)*f_c) | (freqs>(1+bw)*f_c)] = 0
    return np.real(np.fft.irfft(F, n=n))

ENSO_RUNGS = [(k, PHI**k) for k in range(4, 10)]
print(f"\nENSO rungs (months): {[(k, round(p,1)) for k,p in ENSO_RUNGS]}")

R_nino = {k: rung_band(NINO, p) for k,p in ENSO_RUNGS}
R_amo  = {k: rung_band(AMO,  p) for k,p in ENSO_RUNGS}
R_tna  = {k: rung_band(TNA,  p) for k,p in ENSO_RUNGS}
R_pdo  = {k: rung_band(PDO,  p) for k,p in ENSO_RUNGS}

# --- COUPLING MATRICES (training half) ---
def cm(target_R, source_R, train_end):
    out = {}
    for tk in target_R:
        for sk in source_R:
            a = target_R[tk][:train_end]; b = source_R[sk][:train_end]
            out[(tk,sk)] = float(np.corrcoef(a,b)[0,1]) if (np.std(a)>1e-12 and np.std(b)>1e-12) else 0.0
    return out

CM_amo = cm(R_nino, R_amo, SPLIT)
CM_tna = cm(R_nino, R_tna, SPLIT)
CM_pdo = cm(R_nino, R_pdo, SPLIT)

print("\nDiagonal couplings (matched-rung) ENSO ← feeder:")
print(f"{'k':>3}  {'AMO':>7}  {'TNA':>7}  {'PDO':>7}")
for tk,_ in ENSO_RUNGS:
    print(f"{tk:>3}  {CM_amo[(tk,tk)]:+7.3f}  {CM_tna[(tk,tk)]:+7.3f}  {CM_pdo[(tk,tk)]:+7.3f}")

# --- METRICS ---
def metrics(y, p):
    if np.std(p)<1e-12: corr=0.0
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
M3 = np.full(n_test, mean_train)
for k,_ in ENSO_RUNGS:
    a, mu = ar[k]; prev = R_nino[k][SPLIT-1]
    for i in range(n_test):
        v = mu + a*(prev - mu); M3[i] += v; prev = v

# --- M4: LR with all 3 feeders broadband ---
X_tr3 = np.column_stack([amo_tr, tna_tr, pdo_tr, np.ones_like(amo_tr)])
beta3, *_ = np.linalg.lstsq(X_tr3, nino_tr, rcond=None)
M4 = np.column_stack([amo_te, tna_te, pdo_te, np.ones_like(amo_te)]) @ beta3
print(f"\nLR3 coefs: AMO={beta3[0]:+.3f}  TNA={beta3[1]:+.3f}  PDO={beta3[2]:+.3f}  const={beta3[3]:+.3f}")

# --- M4b: LR with all 3 feeders, hand-searched lags ---
def lr_with_lags(arrs_tr, arrs_te, y_tr, lags):
    """arrs_tr, arrs_te: list of arrays. lags: list of int per source."""
    max_lag = max(max(lags), 0)
    n_used = len(arrs_tr[0]) - max_lag
    cols_tr = [np.ones(n_used)]; cols_te = [np.ones(len(arrs_te[0]))]
    for src_tr, src_te, lag in zip(arrs_tr, arrs_te, lags):
        full = np.concatenate([src_tr, src_te])
        cols_tr.append(src_tr[max_lag-lag:len(src_tr)-lag] if lag>0 else src_tr[max_lag:])
        cols_te.append(full[len(src_tr)-lag:len(src_tr)+len(src_te)-lag] if lag>0 else src_te)
    X_tr = np.column_stack(cols_tr); X_te = np.column_stack(cols_te)
    y = y_tr[max_lag:]
    beta, *_ = np.linalg.lstsq(X_tr, y, rcond=None)
    return X_te @ beta, beta

best_corr = -2; best_lags = (0,0,0); best_pred = None
for la in [0,3,6,12]:
    for lt in [0,3,6,12]:
        for lp in [0,3,6,12]:
            try:
                pred, _ = lr_with_lags([amo_tr,tna_tr,pdo_tr],[amo_te,tna_te,pdo_te],nino_tr,[la,lt,lp])
                c = float(np.corrcoef(nino_te, pred)[0,1])
                if c > best_corr: best_corr=c; best_lags=(la,lt,lp); best_pred=pred
            except Exception: pass
M4b = best_pred
print(f"M4b best lags (AMO,TNA,PDO) = {best_lags}, corr = {best_corr:+.3f}")

# --- M5 helper: per-rung framework with N feeders ---
def framework_with_feeders(target_R, feeders_R_list):
    """For each ENSO rung, fit OLS on training: ENSO_k ~ Σ feeder_k. Apply to test."""
    pred = np.full(n_test, mean_train)
    coefs_per_rung = {}
    for k,_ in ENSO_RUNGS:
        cols_tr = [target_R[k][:SPLIT]*0+1]  # constant
        cols_te = [np.ones(n_test)]
        for FR in feeders_R_list:
            cols_tr.append(FR[k][:SPLIT])
            cols_te.append(FR[k][SPLIT:])
        X_tr = np.column_stack(cols_tr); X_te = np.column_stack(cols_te)
        y = target_R[k][:SPLIT]
        b, *_ = np.linalg.lstsq(X_tr, y, rcond=None)
        coefs_per_rung[k] = b
        pred += X_te @ b
    return pred, coefs_per_rung

M5_2feed, coefs_2 = framework_with_feeders(R_nino, [R_amo, R_tna])
M5_3feed, coefs_3 = framework_with_feeders(R_nino, [R_amo, R_tna, R_pdo])

# --- M5b: M5_3feed + AR memory blend ---
M5b_3feed = np.full(n_test, mean_train)
for k,_ in ENSO_RUNGS:
    a, mu = ar[k]; prev = R_nino[k][SPLIT-1]
    cols_te = [np.ones(n_test), R_amo[k][SPLIT:], R_tna[k][SPLIT:], R_pdo[k][SPLIT:]]
    feeder = np.column_stack(cols_te) @ coefs_3[k]
    for i in range(n_test):
        v = 0.5*(mu + a*(prev - mu)) + 0.5*feeder[i]
        M5b_3feed[i] += v; prev = v

# --- METRICS ---
R = dict(
    M1_mean=metrics(nino_te, M1),
    M2_AR=metrics(nino_te, M2),
    M3_ENSO_only=metrics(nino_te, M3),
    M4_LR_3feed_broadband=metrics(nino_te, M4),
    M4b_LR_3feed_lagged=metrics(nino_te, M4b) if M4b is not None else dict(corr=0,rmse=0,mae=0,pred_std=0),
    M5_FW_2feed=metrics(nino_te, M5_2feed),
    M5_FW_3feed=metrics(nino_te, M5_3feed),
    M5b_FW_3feed_AR=metrics(nino_te, M5b_3feed),
)

print(f"\n========= TEST RESULTS (n={n_test} months) =========")
print(f"True test std: {np.std(nino_te):.3f}")
for name, r in R.items():
    flag = ''
    if r['corr'] > R['M4_LR_3feed_broadband']['corr']+0.05: flag = ' ★ beats LR3-broadband'
    elif r['corr'] > R['M4_LR_3feed_broadband']['corr']: flag = ' ↑'
    print(f"  {name:25s}: corr={r['corr']:+.3f}  rmse={r['rmse']:.3f}  pred_std={r['pred_std']:.3f}{flag}")
print(f"\nKey deltas:")
print(f"  M5_3feed - M5_2feed  (3rd feeder lift):     {R['M5_FW_3feed']['corr'] - R['M5_FW_2feed']['corr']:+.3f}")
print(f"  M5_3feed - M4_LR3    (framework vs LR3):    {R['M5_FW_3feed']['corr'] - R['M4_LR_3feed_broadband']['corr']:+.3f}")
print(f"  M5_3feed - M4b_LR3   (framework vs LR3-lag):{R['M5_FW_3feed']['corr'] - R['M4b_LR_3feed_lagged']['corr']:+.3f}")
print(f"  M5b_3feed - M5_3feed (AR memory help):     {R['M5b_FW_3feed_AR']['corr'] - R['M5_FW_3feed']['corr']:+.3f}")
print(f"  M5_3feed - M3_ENSO   (feeders vs no-feed): {R['M5_FW_3feed']['corr'] - R['M3_ENSO_only']['corr']:+.3f}")

# --- SAVE ---
out = dict(
    sources=dict(
        nino="https://psl.noaa.gov/data/timeseries/month/ (Nino 3.4 long anomaly)",
        amo="NOAA PSL AMO unsmoothed long",
        tna="NOAA PSL TNA",
        pdo="https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/index/ersst.v5.pdo.dat",
    ),
    dates=[d.strftime('%Y-%m') for d in DATES],
    nino=NINO.tolist(), amo=AMO.tolist(), tna=TNA.tolist(), pdo=PDO.tolist(),
    split_idx=int(SPLIT),
    preds=dict(
        M1=M1.tolist(), M2=M2.tolist(), M3=M3.tolist(),
        M4=M4.tolist(), M4b=M4b.tolist() if M4b is not None else None,
        M5_2feed=M5_2feed.tolist(),
        M5_3feed=M5_3feed.tolist(),
        M5b_3feed=M5b_3feed.tolist(),
    ),
    metrics=R,
    rungs=[[k,p] for k,p in ENSO_RUNGS],
    coupling_amo={f"{k1}_{k2}":v for (k1,k2),v in CM_amo.items()},
    coupling_tna={f"{k1}_{k2}":v for (k1,k2),v in CM_tna.items()},
    coupling_pdo={f"{k1}_{k2}":v for (k1,k2),v in CM_pdo.items()},
    lr3_coefs=dict(amo=float(beta3[0]), tna=float(beta3[1]), pdo=float(beta3[2]), const=float(beta3[3])),
    best_lags=list(best_lags),
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.ENSO_3F = " + json.dumps(out) + ";\n")
print(f"\nSaved -> {OUT}")
