"""
Reverse inference test (Dylan's articulation 2026-05-02):

Hide AMO. Reconstruct it from the OTHER three measured systems (ENSO, TNA, PDO).
Compare framework matched-rung reconstruction vs plain LR.

Then test SPARSE training: shrink the available AMO training data
(100%, 50%, 25%, 10%, 5%, 1%) and see how each method degrades.

Hypothesis: framework holds up better as data gets sparse, because its
matched-rung structural prior compensates for missing measurements.

DATA SOURCES (all real NOAA, verifiable):
  ENSO Niño 3.4: NOAA PSL
  AMO unsmoothed: NOAA PSL
  TNA: NOAA PSL
  PDO ERSST V5: https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/index/ersst.v5.pdo.dat
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
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\reverse_inference_data.js")

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

nino = load_nino()
amo  = load_grid_text(AMO_PATH, header_lines=1)
tna  = load_grid_text(TNA_PATH, header_lines=1)
pdo  = load_grid_text(PDO_PATH, header_lines=2)

common = nino.index.intersection(amo.index).intersection(tna.index).intersection(pdo.index).sort_values()
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
n_test = len(amo_te)
print(f"Common overlap: {DATES[0].date()} → {DATES[-1].date()}, n={N}")
print(f"Train n={SPLIT}, Test n={n_test}, AMO test std = {np.std(amo_te):.3f}")

# φ-rung bandpass
def rung_band(arr, period_months, dt=1.0, bw=0.2):
    n = len(arr); F = np.fft.rfft(arr - np.mean(arr))
    freqs = np.fft.rfftfreq(n, d=dt)
    f_c = 1.0/period_months
    F[(freqs<(1-bw)*f_c) | (freqs>(1+bw)*f_c)] = 0
    return np.real(np.fft.irfft(F, n=n))

RUNGS = [(k, PHI**k) for k in range(4, 10)]
R_nino = {k: rung_band(NINO, p) for k,p in RUNGS}
R_amo  = {k: rung_band(AMO,  p) for k,p in RUNGS}
R_tna  = {k: rung_band(TNA,  p) for k,p in RUNGS}
R_pdo  = {k: rung_band(PDO,  p) for k,p in RUNGS}

def metrics(y_true, y_pred):
    if np.std(y_pred)<1e-12: corr=0.0
    else: corr=float(np.corrcoef(y_true,y_pred)[0,1])
    rmse = float(np.sqrt(np.mean((y_true-y_pred)**2)))
    return dict(corr=corr, rmse=rmse, pred_std=float(np.std(y_pred)))

# === Reconstruction methods ===
# Both methods learn AMO from the OTHER three on a SUBSET of training,
# then predict AMO on the test half (where we pretend AMO is hidden).

def reconstruct_LR(amo_train_avail, idx_train_avail,
                   nino_tr_full, tna_tr_full, pdo_tr_full,
                   nino_te, tna_te, pdo_te):
    """Plain LR: AMO ~ ENSO + TNA + PDO. Trained on the available AMO subset."""
    nino_t = nino_tr_full[idx_train_avail]
    tna_t  = tna_tr_full[idx_train_avail]
    pdo_t  = pdo_tr_full[idx_train_avail]
    X_tr = np.column_stack([nino_t, tna_t, pdo_t, np.ones_like(nino_t)])
    beta, *_ = np.linalg.lstsq(X_tr, amo_train_avail, rcond=None)
    X_te = np.column_stack([nino_te, tna_te, pdo_te, np.ones(len(nino_te))])
    return X_te @ beta

def reconstruct_FW(amo_train_avail, idx_train_avail,
                   R_nino, R_tna, R_pdo, R_amo,
                   SPLIT, n_test, RUNGS):
    """Framework: per-rung LR. For each AMO rung k, learn AMO_k ~ ENSO_k + TNA_k + PDO_k
       on the AVAILABLE training subset. Sum across rungs.
       This uses the full bandpassed series (computed once on the FULL data — the
       bandpass output for the available subset is just R_amo[k][idx])."""
    pred = np.zeros(n_test) + np.mean(amo_train_avail)
    for k,_ in RUNGS:
        nino_k = R_nino[k][idx_train_avail]
        tna_k  = R_tna[k][idx_train_avail]
        pdo_k  = R_pdo[k][idx_train_avail]
        amo_k  = R_amo[k][idx_train_avail]
        X = np.column_stack([nino_k, tna_k, pdo_k, np.ones_like(nino_k)])
        b, *_ = np.linalg.lstsq(X, amo_k, rcond=None)
        Xt = np.column_stack([R_nino[k][SPLIT:], R_tna[k][SPLIT:], R_pdo[k][SPLIT:], np.ones(n_test)])
        pred += Xt @ b
    return pred

# === Try hiding each variable in turn (full training data) ===
def hide_and_reconstruct(target_name, target_arr, target_R,
                          others, others_R):
    """others: list of (name, arr); others_R: list of dicts. target_arr full series."""
    n_te = len(target_arr) - SPLIT
    # LR
    nino_tr_full = others[0][1][:SPLIT]; tna_tr_full = others[1][1][:SPLIT]; pdo_tr_full = others[2][1][:SPLIT]
    nino_te = others[0][1][SPLIT:]; tna_te = others[1][1][SPLIT:]; pdo_te = others[2][1][SPLIT:]
    target_te = target_arr[SPLIT:]
    target_train = target_arr[:SPLIT]
    idx_full = np.arange(SPLIT)
    pred_LR = reconstruct_LR(target_train, idx_full, nino_tr_full, tna_tr_full, pdo_tr_full,
                              nino_te, tna_te, pdo_te)
    # Framework
    pred = np.zeros(n_te) + np.mean(target_train)
    for k,_ in RUNGS:
        cols_tr = [others_R[0][k][:SPLIT], others_R[1][k][:SPLIT], others_R[2][k][:SPLIT], np.ones(SPLIT)]
        cols_te = [others_R[0][k][SPLIT:], others_R[1][k][SPLIT:], others_R[2][k][SPLIT:], np.ones(n_te)]
        X_tr = np.column_stack(cols_tr); y = target_R[k][:SPLIT]
        b, *_ = np.linalg.lstsq(X_tr, y, rcond=None)
        pred += np.column_stack(cols_te) @ b
    pred_FW = pred
    m_LR = metrics(target_te, pred_LR); m_FW = metrics(target_te, pred_FW)
    return m_LR, m_FW, pred_LR, pred_FW

print(f"\n========= REVERSE INFERENCE — hide each variable in turn =========")
print(f"{'hidden':>10}  {'true_std':>9}  {'LR_corr':>8}  {'FW_corr':>8}  {'delta':>8}")
hide_results = {}
hide_preds = {}
configs = [
    ('AMO', AMO, R_amo, [('ENSO',NINO),('TNA',TNA),('PDO',PDO)], [R_nino, R_tna, R_pdo]),
    ('ENSO', NINO, R_nino, [('AMO',AMO),('TNA',TNA),('PDO',PDO)], [R_amo, R_tna, R_pdo]),
    ('TNA', TNA, R_tna, [('ENSO',NINO),('AMO',AMO),('PDO',PDO)], [R_nino, R_amo, R_pdo]),
    ('PDO', PDO, R_pdo, [('ENSO',NINO),('AMO',AMO),('TNA',TNA)], [R_nino, R_amo, R_tna]),
]
for name, arr, RR, others, others_R in configs:
    m_LR, m_FW, p_LR, p_FW = hide_and_reconstruct(name, arr, RR, others, others_R)
    delta = m_FW['corr'] - m_LR['corr']

for name, arr, RR, others, others_R in configs:
    m_LR, m_FW, p_LR, p_FW = hide_and_reconstruct(name, arr, RR, others, others_R)
    delta = m_FW['corr'] - m_LR['corr']
    flag = ' * FW wins' if delta > 0.03 else ('  ~tie' if delta > -0.03 else ' v LR wins')
    print(f"  {name:>10}  {np.std(arr[SPLIT:]):8.3f}  {m_LR['corr']:+.4f}  {m_FW['corr']:+.4f}  {delta:+.4f}{flag}")
    hide_results[name] = dict(LR=m_LR, FW=m_FW, delta=delta, true_std=float(np.std(arr[SPLIT:])))
    hide_preds[name] = dict(LR=p_LR.tolist(), FW=p_FW.tolist(), truth=arr[SPLIT:].tolist())

# === Sparse-training sweep on AMO (the original test) ===
fractions = [1.0, 0.5, 0.25, 0.10, 0.05, 0.02, 0.01]
results = {}
predictions = {}

print(f"\n========= SPARSE TRAINING — reconstruct AMO from ENSO+TNA+PDO =========")
print(f"{'frac':>6}  {'n_obs':>6}  {'LR_corr':>8}  {'FW_corr':>8}  {'LR_rmse':>8}  {'FW_rmse':>8}  delta")
for frac in fractions:
    n_obs = max(8, int(SPLIT * frac))
    idx = np.linspace(0, SPLIT-1, n_obs).astype(int)
    amo_avail = AMO[idx]
    pred_LR = reconstruct_LR(amo_avail, idx, NINO[:SPLIT], TNA[:SPLIT], PDO[:SPLIT],
                              NINO[SPLIT:], TNA[SPLIT:], PDO[SPLIT:])
    pred_FW = reconstruct_FW(amo_avail, idx, R_nino, R_tna, R_pdo, R_amo,
                              SPLIT, n_test, RUNGS)
    m_LR = metrics(amo_te, pred_LR)
    m_FW = metrics(amo_te, pred_FW)
    delta = m_FW['corr'] - m_LR['corr']
    print(f"  {frac*100:5.1f}% {n_obs:6d}  {m_LR['corr']:+.4f}  {m_FW['corr']:+.4f}  {m_LR['rmse']:.4f}  {m_FW['rmse']:.4f}  {delta:+.4f}")
    results[frac] = dict(n_obs=n_obs, LR=m_LR, FW=m_FW, delta=delta)
    predictions[frac] = dict(LR=pred_LR.tolist(), FW=pred_FW.tolist())

print(f"\nTrue AMO test: mean={np.mean(amo_te):+.4f}, std={np.std(amo_te):.4f}")

out = dict(
    sources=dict(
        nino="NOAA PSL Nino 3.4 long anomaly",
        amo="NOAA PSL AMO unsmoothed long",
        tna="NOAA PSL TNA",
        pdo="https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/index/ersst.v5.pdo.dat",
    ),
    dates=[d.strftime('%Y-%m') for d in DATES],
    truth=AMO.tolist(),
    split_idx=int(SPLIT),
    hide_results=hide_results,
    hide_preds=hide_preds,
    fractions=fractions,
    results={str(f): r for f,r in results.items()},
    preds={str(f): p for f,p in predictions.items()},
    rungs=[[k,p] for k,p in RUNGS],
    other_systems_test=dict(nino=nino_te.tolist(), tna=tna_te.tolist(), pdo=pdo_te.tolist()),
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.REV_INFER = " + json.dumps(out) + ";\n")
print(f"Saved -> " + OUT)
