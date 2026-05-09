"""
Direction prediction test (Dylan 2026-05-02 stronger claim):

Given the joint topology of 4 ocean regions (ENSO, AMO, TNA, PDO) at time t,
predict whether ENSO will go UP or DOWN by time t+h, for h in {1, 3, 6, 12} months.

Compare:
  M1 random  : random ±1 (50% baseline)
  M2 persist : sign(ENSO[t] - ENSO[t-h])  (current trend continues)
  M3 LR      : predict ENSO[t+h] from joint state (multivariate LR), then take sign
  M4 VAR     : vector autoregression — proper multivariate version
  M5 framework: evolve joint per-rung state forward; take sign

Direction accuracy = fraction of times predicted_sign == true_sign.
Dylan's claim: ~80% achievable for a mostly-closed system.

DATA SOURCES (all real NOAA, verifiable):
  ENSO Niño 3.4: NOAA PSL
  AMO: NOAA PSL
  TNA: NOAA PSL
  PDO: https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/index/ersst.v5.pdo.dat
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
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\direction_prediction_data.js")

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
print(f"Common overlap: {DATES[0].date()} → {DATES[-1].date()}, n={N}")
print(f"Train n={SPLIT}, Test n={N-SPLIT}")

# φ-rungs
def rung_band(arr, period_months, dt=1.0, bw=0.2):
    n = len(arr); F = np.fft.rfft(arr - np.mean(arr))
    freqs = np.fft.rfftfreq(n, d=dt)
    f_c = 1.0/period_months
    F[(freqs<(1-bw)*f_c) | (freqs>(1+bw)*f_c)] = 0
    return np.real(np.fft.irfft(F, n=n))

RUNGS = [(k, PHI**k) for k in range(4, 10)]
SYS = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO)
R = {name: {k: rung_band(arr, p) for k,p in RUNGS} for name,arr in SYS.items()}

# === Build direction targets ===
HORIZONS = [1, 3, 6, 12]

def dir_truth(arr, t_idx, h):
    """Sign of arr[t+h] - arr[t]. Skip if out of range."""
    if t_idx + h >= len(arr): return None
    diff = arr[t_idx + h] - arr[t_idx]
    return 1 if diff > 0 else (-1 if diff < 0 else 0)

# === M1: random ===
np.random.seed(42)
def acc_random(arr, idx_set, h):
    correct = 0; total = 0
    for t in idx_set:
        true = dir_truth(arr, t, h)
        if true is None or true==0: continue
        pred = np.random.choice([-1,1])
        correct += (pred == true); total += 1
    return correct / total if total else 0

# === M2: persistence direction ===
def acc_persistence(arr, idx_set, h):
    correct = 0; total = 0
    for t in idx_set:
        if t - h < 0: continue
        true = dir_truth(arr, t, h)
        if true is None or true==0: continue
        prev_diff = arr[t] - arr[t - h]
        pred = 1 if prev_diff > 0 else (-1 if prev_diff < 0 else 0)
        if pred == 0: continue
        correct += (pred == true); total += 1
    return correct / total if total else 0

# === M3: LR predict ENSO[t+h] from joint state at t ===
def fit_LR_h(h, train_idx_max):
    """Fit ENSO[t+h] ~ ENSO[t] + AMO[t] + TNA[t] + PDO[t] on training data."""
    rows = []; ys = []
    for t in range(train_idx_max - h):
        rows.append([NINO[t], AMO[t], TNA[t], PDO[t], 1.0])
        ys.append(NINO[t+h])
    X = np.array(rows); y = np.array(ys)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta

def predict_LR_h(beta, t):
    return beta[0]*NINO[t] + beta[1]*AMO[t] + beta[2]*TNA[t] + beta[3]*PDO[t] + beta[4]

def acc_LR(idx_set, h, train_idx_max):
    beta = fit_LR_h(h, train_idx_max)
    correct = 0; total = 0
    for t in idx_set:
        true = dir_truth(NINO, t, h)
        if true is None or true==0: continue
        pred_val = predict_LR_h(beta, t)
        pred = 1 if pred_val > NINO[t] else (-1 if pred_val < NINO[t] else 0)
        if pred == 0: continue
        correct += (pred == true); total += 1
    return correct / total if total else 0

# === M4: VAR (vector autoregression) — uses lagged terms too ===
def fit_VAR_h(h, train_idx_max, p_lags=3):
    """Fit ENSO[t+h] ~ Σ over each system at lags 0..p-1."""
    rows = []; ys = []
    for t in range(p_lags, train_idx_max - h):
        feat = []
        for lag in range(p_lags):
            for nm in ('NINO','AMO','TNA','PDO'):
                feat.append(SYS[nm][t-lag])
        feat.append(1.0)
        rows.append(feat); ys.append(NINO[t+h])
    X = np.array(rows); y = np.array(ys)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta, p_lags

def predict_VAR_h(beta_p, t):
    beta, p_lags = beta_p
    feat = []
    for lag in range(p_lags):
        for nm in ('NINO','AMO','TNA','PDO'):
            feat.append(SYS[nm][t-lag])
    feat.append(1.0)
    return float(np.dot(beta, feat))

def acc_VAR(idx_set, h, train_idx_max, p_lags=3):
    beta_p = fit_VAR_h(h, train_idx_max, p_lags)
    correct = 0; total = 0
    for t in idx_set:
        if t - p_lags + 1 < 0: continue
        true = dir_truth(NINO, t, h)
        if true is None or true==0: continue
        pred_val = predict_VAR_h(beta_p, t)
        pred = 1 if pred_val > NINO[t] else -1
        correct += (pred == true); total += 1
    return correct / total if total else 0

# === M5: Framework — evolve joint per-rung state forward ===
# For each rung k, learn ENSO_k[t+h] ~ NINO_k[t] + AMO_k[t] + TNA_k[t] + PDO_k[t]
# Sum across rungs to get predicted ENSO[t+h].
def fit_FW_h(h, train_idx_max):
    rung_betas = {}
    for k,_ in RUNGS:
        rows = []; ys = []
        for t in range(train_idx_max - h):
            rows.append([R['NINO'][k][t], R['AMO'][k][t], R['TNA'][k][t], R['PDO'][k][t], 1.0])
            ys.append(R['NINO'][k][t+h])
        X = np.array(rows); y = np.array(ys)
        b, *_ = np.linalg.lstsq(X, y, rcond=None)
        rung_betas[k] = b
    return rung_betas

def predict_FW_h(rung_betas, t):
    """Sum predicted rung amplitudes + train mean."""
    s = float(np.mean(NINO[:SPLIT]))
    for k,_ in RUNGS:
        b = rung_betas[k]
        s += b[0]*R['NINO'][k][t] + b[1]*R['AMO'][k][t] + b[2]*R['TNA'][k][t] + b[3]*R['PDO'][k][t] + b[4]
    return s

def acc_FW(idx_set, h, train_idx_max):
    rung_betas = fit_FW_h(h, train_idx_max)
    correct = 0; total = 0
    for t in idx_set:
        true = dir_truth(NINO, t, h)
        if true is None or true==0: continue
        pred_val = predict_FW_h(rung_betas, t)
        pred = 1 if pred_val > NINO[t] else -1
        correct += (pred == true); total += 1
    return correct / total if total else 0

# === RUN ALL ===
test_idx = list(range(SPLIT, N))
print(f"\n========= DIRECTION ACCURACY (test n={len(test_idx)}) =========")
print(f"{'horizon':>10}  {'random':>7}  {'persist':>7}  {'LR':>7}  {'VAR3':>7}  {'FW':>7}")
results = {}
for h in HORIZONS:
    a_rand = acc_random(NINO, test_idx, h)
    a_pers = acc_persistence(NINO, test_idx, h)
    a_lr   = acc_LR(test_idx, h, SPLIT)
    a_var  = acc_VAR(test_idx, h, SPLIT, p_lags=3)
    a_fw   = acc_FW(test_idx, h, SPLIT)
    print(f"  h={h:>2} months  {a_rand:>7.1%}  {a_pers:>7.1%}  {a_lr:>7.1%}  {a_var:>7.1%}  {a_fw:>7.1%}")
    results[h] = dict(random=a_rand, persistence=a_pers, LR=a_lr, VAR3=a_var, FW=a_fw)

# Best at each horizon
print("\nBest method per horizon:")
for h, r in results.items():
    best_name, best_val = max(r.items(), key=lambda kv: kv[1])
    print(f"  h={h:>2}m: best={best_name} ({best_val:.1%})")

# Save
out = dict(
    sources=dict(
        nino="NOAA PSL Nino 3.4 long anomaly",
        amo="NOAA PSL AMO unsmoothed long",
        tna="NOAA PSL TNA",
        pdo="https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/index/ersst.v5.pdo.dat",
    ),
    common_range=[DATES[0].strftime('%Y-%m'), DATES[-1].strftime('%Y-%m')],
    train_n=int(SPLIT), test_n=int(N-SPLIT),
    horizons=HORIZONS,
    results={str(h):r for h,r in results.items()},
    rungs=[[k,p] for k,p in RUNGS],
    target_threshold=0.80,
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.DIR_PRED = " + json.dumps(out) + ";\n")
print(f"\nSaved -> {OUT}")
