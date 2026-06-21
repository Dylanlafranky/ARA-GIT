"""
How far into the future does the framework hold (Dylan 2026-05-02)?

Extend direction prediction horizons way out: 1, 3, 6, 12, 18, 24, 36, 48, 60, 72, 96, 120 months.
Use the best config (5 ocean + Moon, framework with high-res descriptors).
Compare to VAR (3 lags) and persistence at every horizon.
Find the predictability cliff.

DATA: same real NOAA + JPL Horizons. All verifiable.
"""
import json, os, math, re
import numpy as np, pandas as pd
from scipy.signal import hilbert

PHI = 1.6180339887498949

def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
AMO_PATH  = _resolve(r"F:\SystemFormulaFolder\HURDAT2\Temp\amonuslong.txt")
TNA_PATH  = _resolve(r"F:\SystemFormulaFolder\HURDAT2\Temp\tna.txt")
PDO_PATH  = _resolve(r"F:\SystemFormulaFolder\PDO_NOAA\ersst.v5.pdo.dat")
IOD_PATH  = _resolve(r"F:\SystemFormulaFolder\IOD_NOAA\dmi.had.long.data")
MOON_PATH = _resolve(r"F:\SystemFormulaFolder\Moon_JPL\moon_elements_1948_2023.txt")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\horizon_extension_data.js")

# Loaders (compact, same as before)
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
def load_moon():
    rows = []; in_data = False; cur = None
    with open(MOON_PATH,'r') as f:
        for ln in f:
            ln = ln.rstrip()
            if ln.strip() == '$$SOE': in_data = True; continue
            if ln.strip() == '$$EOE': break
            if not in_data: continue
            m = re.match(r'^\s*(\d+\.\d+)\s*=\s*A\.D\.\s+(\d{4})-(\w{3})-(\d{1,2})', ln)
            if m:
                if cur is not None: rows.append(cur)
                year = int(m.group(2))
                mon  = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}[m.group(3)]
                day  = int(m.group(4))
                cur = dict(date=pd.Timestamp(year=year, month=mon, day=day))
                continue
            for key, val in re.findall(r'([A-Z]+)\s*=\s*([+\-]?\d+\.?\d*E?[+\-]?\d*)', ln):
                if cur is None: continue
                try: cur[key] = float(val)
                except: pass
        if cur is not None: rows.append(cur)
    return pd.DataFrame(rows).set_index('date').sort_index()

print("Loading...")
nino = load_nino(); amo = load_grid_text(AMO_PATH); tna = load_grid_text(TNA_PATH)
pdo = load_grid_text(PDO_PATH, header_lines=2); iod = load_iod(); moon = load_moon()
def to_monthly(s):
    s = s.copy(); s.index = pd.to_datetime(s.index).to_period('M').to_timestamp()
    return s.groupby(s.index).first()
nino = to_monthly(nino); amo = to_monthly(amo); tna = to_monthly(tna)
pdo = to_monthly(pdo); iod = to_monthly(iod)
moon.index = pd.to_datetime(moon.index).to_period('M').to_timestamp()
moon = moon.groupby(moon.index).first()
common = nino.index
for s in [amo, tna, pdo, iod, moon.index]:
    common = common.intersection(s.index if hasattr(s,'index') else s)
common = common.sort_values()

NINO = nino.reindex(common).values.astype(float)
AMO  = amo.reindex(common).values.astype(float)
TNA  = tna.reindex(common).values.astype(float)
PDO  = pdo.reindex(common).values.astype(float)
IOD  = iod.reindex(common).values.astype(float)
moon_a = moon.reindex(common)
OM = moon_a['OM'].values.astype(float)
MOON_OM_S = np.sin(np.deg2rad(OM)); MOON_OM_C = np.cos(np.deg2rad(OM))
MOON_EC = moon_a['EC'].values.astype(float)
DATES = common; N = len(NINO); SPLIT = N//2
print(f"Common: {DATES[0].date()} → {DATES[-1].date()}, n={N}, train={SPLIT}, test={N-SPLIT}")

# Extend rungs to capture longer cycles (φ¹⁵ ≈ 1364 months ≈ 114 years)
RUNGS = [(k, PHI**k) for k in range(4, 14)]
SYS = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD,
           MOON_OM_S=MOON_OM_S, MOON_OM_C=MOON_OM_C, MOON_EC=MOON_EC)

def rung_band(arr, period_months, bw=0.2):
    n = len(arr); F = np.fft.rfft(arr - np.mean(arr))
    freqs = np.fft.rfftfreq(n, d=1.0)
    f_c = 1.0/period_months
    F[(freqs<(1-bw)*f_c) | (freqs>(1+bw)*f_c)] = 0
    return np.real(np.fft.irfft(F, n=n))

R = {name: {k: rung_band(arr, p) for k,p in RUNGS} for name,arr in SYS.items()}

# Direction utility
def dir_truth(arr, t, h):
    if t + h >= len(arr): return None
    diff = arr[t + h] - arr[t]
    return 1 if diff > 0 else (-1 if diff < 0 else 0)

FEEDERS = list(SYS.keys())

def acc_persistence(arr, idx, h):
    correct=0; total=0
    for t in idx:
        if t-h<0: continue
        true = dir_truth(arr, t, h)
        if true is None or true==0: continue
        prev = arr[t]-arr[t-h]
        if prev==0: continue
        pred = 1 if prev>0 else -1
        correct += (pred==true); total += 1
    return correct/total if total else 0

def acc_VAR(idx, h, train_max, p_lags=3):
    if train_max - h - p_lags < 10: return None
    rows=[]; ys=[]
    for t in range(p_lags, train_max - h):
        feat = []
        for lag in range(p_lags):
            for nm in FEEDERS:
                feat.append(SYS[nm][t-lag])
        feat.append(1.0)
        rows.append(feat); ys.append(NINO[t+h])
    X = np.array(rows); y = np.array(ys)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    correct=0; total=0
    for t in idx:
        if t-p_lags+1<0: continue
        true = dir_truth(NINO, t, h)
        if true is None or true==0: continue
        feat=[]
        for lag in range(p_lags):
            for nm in FEEDERS:
                feat.append(SYS[nm][t-lag])
        feat.append(1.0)
        pred_val = float(np.dot(beta, feat))
        pred = 1 if pred_val>NINO[t] else -1
        correct += (pred==true); total += 1
    return correct/total if total else 0

def acc_FW(idx, h, train_max, ridge=0.0):
    if train_max - h < 20: return None
    rung_betas = {}
    for k,_ in RUNGS:
        rows=[]; ys=[]
        for t in range(train_max - h):
            feat = [R[nm][k][t] for nm in FEEDERS]
            feat.append(1.0)
            rows.append(feat); ys.append(R['NINO'][k][t+h])
        X = np.array(rows); y = np.array(ys)
        if ridge > 0:
            n_features = X.shape[1]
            A = X.T @ X + ridge * np.eye(n_features)
            A[-1,-1] -= ridge
            b = np.linalg.solve(A, X.T @ y)
        else:
            b, *_ = np.linalg.lstsq(X, y, rcond=None)
        rung_betas[k] = b
    correct=0; total=0
    mean_n = float(np.mean(NINO[:train_max]))
    for t in idx:
        true = dir_truth(NINO, t, h)
        if true is None or true==0: continue
        s = mean_n
        for k,_ in RUNGS:
            b = rung_betas[k]
            feat = [R[nm][k][t] for nm in FEEDERS] + [1.0]
            s += float(np.dot(b, feat))
        pred = 1 if s>NINO[t] else -1
        correct += (pred==true); total += 1
    return correct/total if total else 0

# Run across many horizons
HORIZONS = [1, 3, 6, 12, 18, 24, 36, 48, 60, 72, 96, 120, 150, 180]
test_idx = list(range(SPLIT, N))

print(f"\n========= HORIZON EXTENSION (test n={len(test_idx)}) =========")
print(f"{'horizon':>10}  {'persist':>7}  {'VAR':>7}  {'FW':>7}  {'FW_ridge':>9}  {'n_test_used':>11}")
results = {}
for h in HORIZONS:
    n_used = max(0, len(test_idx) - h)
    a_pers = acc_persistence(NINO, test_idx, h)
    a_var  = acc_VAR(test_idx, h, SPLIT) or 0.5
    a_fw   = acc_FW(test_idx, h, SPLIT) or 0.5
    a_fwr  = acc_FW(test_idx, h, SPLIT, ridge=10.0) or 0.5
    print(f"  h={h:>3} mo  {a_pers:>7.1%}  {a_var:>7.1%}  {a_fw:>7.1%}  {a_fwr:>9.1%}  {n_used:>11d}")
    results[h] = dict(persistence=a_pers, VAR=a_var, FW=a_fw, FW_ridge=a_fwr, n_test_used=n_used)

# Summary
print("\nWhere does each method drop below 60%?")
for method in ['persistence','VAR','FW','FW_ridge']:
    cliff = None
    for h in HORIZONS:
        if results[h][method] < 0.60:
            cliff = h; break
    print(f"  {method:>10}: {('h>'+str(HORIZONS[-1])+'mo') if cliff is None else f'h={cliff}mo'}")

# Save
out = dict(
    sources="Same as v2 (NOAA + JPL Horizons)",
    common_range=[DATES[0].strftime('%Y-%m'), DATES[-1].strftime('%Y-%m')],
    train_n=int(SPLIT), test_n=int(N-SPLIT),
    horizons=HORIZONS,
    feeders=FEEDERS,
    rungs=[[k,p] for k,p in RUNGS],
    results={str(h):r for h,r in results.items()},
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.HORIZON_EXT = " + json.dumps(out) + ";\n")
print(f"\nSaved -> {OUT}")
