"""
Direction prediction v2 — add IOD (Indian Ocean Dipole) and Moon orbital data
to the 4-ocean topology. Test if expanded topology pushes accuracy past 80%.

DATA SOURCES (all real, verifiable):
  ENSO Niño 3.4: NOAA PSL
  AMO unsmoothed: NOAA PSL
  TNA: NOAA PSL
  PDO ERSST V5: https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/index/ersst.v5.pdo.dat
  IOD/DMI: NOAA PSL https://psl.noaa.gov/gcos_wgsp/Timeseries/Data/dmi.had.long.data
  Moon orbital elements: NASA JPL Horizons API (target=301, geocenter, 1948-2023 monthly)

Lunar features extracted:
  - OM (ascending node longitude) — primary 18.6-year lunar nodal cycle signal
  - EC (orbital eccentricity) — modulated by Sun perturbation, ~6 month + secular
  - IN (orbital inclination) — small variation around 5.14°

Hypothesis: adding the lunar tidal driver pushes direction prediction to ~80% or beyond.
"""
import json, os, math, re
import numpy as np, pandas as pd

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
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\direction_prediction_v2_data.js")

def load_nino():
    df = pd.read_csv(NINO_PATH, skiprows=1, header=None, names=['date','val'])
    df['date'] = pd.to_datetime(df['date'].str.strip())
    df = df[df['val'] > -90].copy()
    return df.set_index('date')['val'].astype(float)

def load_grid_text(path, header_lines=1, missing_threshold=-90):
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
                if v < missing_threshold or v > -missing_threshold: continue
                rows.append((pd.Timestamp(year=year, month=m+1, day=1), v))
    return pd.Series(dict(rows)).sort_index()

# IOD has -9999 missing marker
def load_iod():
    rows=[]
    with open(IOD_PATH,'r') as f:
        next(f)  # header line "1870 2025"
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

# Parse JPL Horizons elements
def load_moon():
    """Parse JPL Horizons orbital elements text file. Returns DataFrame with date + orbital elements."""
    rows = []
    in_data = False
    cur = None
    with open(MOON_PATH,'r') as f:
        for ln in f:
            ln = ln.rstrip()
            if ln.strip() == '$$SOE': in_data = True; continue
            if ln.strip() == '$$EOE': break
            if not in_data: continue
            # Date line: "2432703.500000000 = A.D. 1948-Jun-01 00:00:00.0000 TDB"
            m = re.match(r'^\s*(\d+\.\d+)\s*=\s*A\.D\.\s+(\d{4})-(\w{3})-(\d{1,2})', ln)
            if m:
                if cur is not None: rows.append(cur)
                year = int(m.group(2))
                mon  = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}[m.group(3)]
                day  = int(m.group(4))
                cur = dict(date=pd.Timestamp(year=year, month=mon, day=day))
                continue
            # Element lines: "EC= 6.420090790771259E-02 QR= 3.558002092365299E+05 IN= 5.236010795228347E+00"
            for key, val in re.findall(r'([A-Z]+)\s*=\s*([+\-]?\d+\.?\d*E?[+\-]?\d*)', ln):
                if cur is None: continue
                try: cur[key] = float(val)
                except: pass
        if cur is not None: rows.append(cur)
    df = pd.DataFrame(rows).set_index('date').sort_index()
    return df

print("Loading datasets...")
nino = load_nino()
amo  = load_grid_text(AMO_PATH, header_lines=1)
tna  = load_grid_text(TNA_PATH, header_lines=1)
pdo  = load_grid_text(PDO_PATH, header_lines=2)
iod  = load_iod()
moon = load_moon()
print(f"NINO: n={len(nino)}  AMO: n={len(amo)}  TNA: n={len(tna)}")
print(f"PDO : n={len(pdo)}   IOD: n={len(iod)}  Moon: n={len(moon)}")

# All to first-of-month monthly index
def to_monthly_first(s):
    s = s.copy()
    s.index = pd.to_datetime(s.index).to_period('M').to_timestamp()
    return s.groupby(s.index).first()

# Snap moon dates to first of month for alignment
moon.index = pd.to_datetime(moon.index).to_period('M').to_timestamp()
moon = moon.groupby(moon.index).first()
nino = to_monthly_first(nino); amo = to_monthly_first(amo); tna = to_monthly_first(tna)
pdo = to_monthly_first(pdo); iod = to_monthly_first(iod)

# Common date range
common = nino.index
for s in [amo, tna, pdo, iod, moon.index]:
    common = common.intersection(s.index if hasattr(s,'index') else s)
common = common.sort_values()
print(f"\nCommon overlap: {common.min().date()} → {common.max().date()}, n={len(common)}")

NINO = nino.reindex(common).values.astype(float)
AMO  = amo.reindex(common).values.astype(float)
TNA  = tna.reindex(common).values.astype(float)
PDO  = pdo.reindex(common).values.astype(float)
IOD  = iod.reindex(common).values.astype(float)

# Lunar features: OM (ascending node longitude — but unwrap), EC (eccentricity), IN (inclination)
moon_aligned = moon.reindex(common)
# OM is in degrees 0..360 — we want a continuous signal. Use sin(OM) and cos(OM)
OM = moon_aligned['OM'].values.astype(float)
MOON_OM_SIN = np.sin(np.deg2rad(OM))
MOON_OM_COS = np.cos(np.deg2rad(OM))
MOON_EC = moon_aligned['EC'].values.astype(float)
MOON_IN = moon_aligned['IN'].values.astype(float)

print(f"Moon OM range: {OM.min():.1f}° to {OM.max():.1f}°")
print(f"Moon EC range: {MOON_EC.min():.4f} to {MOON_EC.max():.4f}")

DATES = common; N = len(NINO); SPLIT = N//2

# φ-rungs
def rung_band(arr, period_months, dt=1.0, bw=0.2):
    n = len(arr); F = np.fft.rfft(arr - np.mean(arr))
    freqs = np.fft.rfftfreq(n, d=dt)
    f_c = 1.0/period_months
    F[(freqs<(1-bw)*f_c) | (freqs>(1+bw)*f_c)] = 0
    return np.real(np.fft.irfft(F, n=n))

RUNGS = [(k, PHI**k) for k in range(4, 12)]  # extend to k=11 (~322 mo = 27 yr) to capture lunar nodal
print(f"Rungs (months): {[(k, round(p,1)) for k,p in RUNGS]}")

SYS = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD,
           MOON_OM_S=MOON_OM_SIN, MOON_OM_C=MOON_OM_COS, MOON_EC=MOON_EC)
R = {name: {k: rung_band(arr, p) for k,p in RUNGS} for name,arr in SYS.items()}

# Direction utility
HORIZONS = [1, 3, 6, 12]
def dir_truth(arr, t, h):
    if t + h >= len(arr): return None
    diff = arr[t + h] - arr[t]
    return 1 if diff > 0 else (-1 if diff < 0 else 0)

# === Methods ===
def acc_persistence(arr, idx, h):
    correct = 0; total = 0
    for t in idx:
        if t - h < 0: continue
        true = dir_truth(arr, t, h)
        if true is None or true==0: continue
        prev_diff = arr[t] - arr[t - h]
        if prev_diff == 0: continue
        pred = 1 if prev_diff > 0 else -1
        correct += (pred == true); total += 1
    return correct / total if total else 0

def acc_LR(idx, h, train_max, feeder_names):
    """Predict NINO[t+h] from joint state at t using listed feeders."""
    rows = []; ys = []
    for t in range(train_max - h):
        feat = [SYS[nm][t] for nm in feeder_names]
        feat.append(1.0)
        rows.append(feat); ys.append(NINO[t+h])
    X = np.array(rows); y = np.array(ys)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    correct = 0; total = 0
    for t in idx:
        true = dir_truth(NINO, t, h)
        if true is None or true==0: continue
        feat = [SYS[nm][t] for nm in feeder_names] + [1.0]
        pred_val = float(np.dot(beta, feat))
        pred = 1 if pred_val > NINO[t] else -1
        correct += (pred == true); total += 1
    return correct / total if total else 0

def acc_VAR(idx, h, train_max, feeder_names, p_lags=3):
    rows = []; ys = []
    for t in range(p_lags, train_max - h):
        feat = []
        for lag in range(p_lags):
            for nm in feeder_names:
                feat.append(SYS[nm][t-lag])
        feat.append(1.0)
        rows.append(feat); ys.append(NINO[t+h])
    X = np.array(rows); y = np.array(ys)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    correct = 0; total = 0
    for t in idx:
        if t - p_lags + 1 < 0: continue
        true = dir_truth(NINO, t, h)
        if true is None or true==0: continue
        feat = []
        for lag in range(p_lags):
            for nm in feeder_names:
                feat.append(SYS[nm][t-lag])
        feat.append(1.0)
        pred_val = float(np.dot(beta, feat))
        pred = 1 if pred_val > NINO[t] else -1
        correct += (pred == true); total += 1
    return correct / total if total else 0

def acc_FW(idx, h, train_max, feeder_names):
    """For each rung k, learn NINO_k[t+h] ~ Σ feeder_k[t]. Sum across rungs."""
    rung_betas = {}
    for k,_ in RUNGS:
        rows=[]; ys=[]
        for t in range(train_max - h):
            feat = [R[nm][k][t] for nm in feeder_names]
            feat.append(1.0)
            rows.append(feat); ys.append(R['NINO'][k][t+h])
        X = np.array(rows); y = np.array(ys)
        b, *_ = np.linalg.lstsq(X, y, rcond=None)
        rung_betas[k] = b
    correct = 0; total = 0
    mean_n = float(np.mean(NINO[:train_max]))
    for t in idx:
        true = dir_truth(NINO, t, h)
        if true is None or true==0: continue
        s = mean_n
        for k,_ in RUNGS:
            b = rung_betas[k]
            feat = [R[nm][k][t] for nm in feeder_names] + [1.0]
            s += float(np.dot(b, feat))
        pred = 1 if s > NINO[t] else -1
        correct += (pred == true); total += 1
    return correct / total if total else 0

# Configurations: which feeders go in
CONFIGS = {
    '4_ocean':       ['NINO','AMO','TNA','PDO'],
    '5_ocean':       ['NINO','AMO','TNA','PDO','IOD'],
    '4_ocean_+moon': ['NINO','AMO','TNA','PDO','MOON_OM_S','MOON_OM_C','MOON_EC'],
    '5_ocean_+moon': ['NINO','AMO','TNA','PDO','IOD','MOON_OM_S','MOON_OM_C','MOON_EC'],
}

test_idx = list(range(SPLIT, N))
print(f"\n========= DIRECTION ACCURACY (test n={len(test_idx)}) =========\n")

results = {}
for cfg_name, feeders in CONFIGS.items():
    print(f"---- Config: {cfg_name}  ({len(feeders)} feeders: {feeders}) ----")
    print(f"  {'horizon':>10}  {'persist':>7}  {'VAR':>7}  {'FW':>7}")
    cfg_results = {}
    for h in HORIZONS:
        a_pers = acc_persistence(NINO, test_idx, h)
        a_var  = acc_VAR(test_idx, h, SPLIT, feeders, p_lags=3)
        a_fw   = acc_FW(test_idx, h, SPLIT, feeders)
        delta = a_fw - a_var
        flag = ' ★' if delta > 0.02 else ('  ' if delta > -0.02 else ' ↓')
        print(f"  h={h:>2} months  {a_pers:>7.1%}  {a_var:>7.1%}  {a_fw:>7.1%}{flag}")
        cfg_results[h] = dict(persistence=a_pers, VAR=a_var, FW=a_fw, delta=delta)
    results[cfg_name] = cfg_results
    print()

# Best config at each horizon
print("Best (config, method) at each horizon:")
for h in HORIZONS:
    best = max(((c, m, results[c][h][m]) for c in CONFIGS for m in ['VAR','FW']),
               key=lambda x: x[2])
    print(f"  h={h:>2}m: {best[0]} {best[1]} → {best[2]:.1%}")

# Save
out = dict(
    sources=dict(
        nino="NOAA PSL Nino 3.4",
        amo="NOAA PSL AMO unsmoothed long",
        tna="NOAA PSL TNA",
        pdo="https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/index/ersst.v5.pdo.dat",
        iod="https://psl.noaa.gov/gcos_wgsp/Timeseries/Data/dmi.had.long.data",
        moon="NASA JPL Horizons API, Moon (301), geocentric orbital elements, 1948-2023 monthly",
    ),
    common_range=[DATES[0].strftime('%Y-%m'), DATES[-1].strftime('%Y-%m')],
    train_n=int(SPLIT), test_n=int(N-SPLIT),
    horizons=HORIZONS,
    configs={c: {str(h):r for h,r in cfg.items()} for c,cfg in results.items()},
    rungs=[[k,p] for k,p in RUNGS],
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.DIR_PRED_V2 = " + json.dumps(out) + ";\n")
print(f"\nSaved -> {OUT}")
