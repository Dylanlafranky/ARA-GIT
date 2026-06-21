"""
Climbing the rung ladder test (Dylan 2026-05-02):

Add SILSO sunspot number (~11-year Schwabe cycle) as an upstream feeder.
Tests if a longer-cycle real driver pushes the predictability cliff further out.

DATA SOURCES (all real, verifiable):
  ENSO Niño 3.4: NOAA PSL
  AMO, TNA: NOAA PSL
  PDO: NOAA NCEI ERSST V5
  IOD: NOAA PSL
  Moon: NASA JPL Horizons
  Sunspots: SILSO https://www.sidc.be/SILSO/INFO/snmtotcsv.php (monthly mean total, V2.0)
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
SUN_PATH  = _resolve(r"F:\SystemFormulaFolder\SILSO_Solar\SN_m_tot_V2.0.csv")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\horizon_with_solar_data.js")

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
                mon = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}[m.group(3)]
                day = int(m.group(4))
                cur = dict(date=pd.Timestamp(year=year, month=mon, day=day))
                continue
            for key, val in re.findall(r'([A-Z]+)\s*=\s*([+\-]?\d+\.?\d*E?[+\-]?\d*)', ln):
                if cur is None: continue
                try: cur[key] = float(val)
                except: pass
        if cur is not None: rows.append(cur)
    return pd.DataFrame(rows).set_index('date').sort_index()

def load_sun():
    """SILSO format: year;month;decimal_year;sunspot_num;std;n_obs;provisional"""
    rows = []
    with open(SUN_PATH,'r') as f:
        for ln in f:
            parts = ln.strip().split(';')
            if len(parts) < 4: continue
            try:
                year = int(parts[0]); mon = int(parts[1])
                v = float(parts[3])
                if v < 0: continue
                rows.append((pd.Timestamp(year=year, month=mon, day=1), v))
            except: continue
    return pd.Series(dict(rows)).sort_index()

print("Loading...")
nino = load_nino(); amo = load_grid_text(AMO_PATH); tna = load_grid_text(TNA_PATH)
pdo = load_grid_text(PDO_PATH, header_lines=2); iod = load_iod(); moon = load_moon(); sun = load_sun()
def to_monthly(s):
    s = s.copy(); s.index = pd.to_datetime(s.index).to_period('M').to_timestamp()
    return s.groupby(s.index).first()
nino = to_monthly(nino); amo = to_monthly(amo); tna = to_monthly(tna)
pdo = to_monthly(pdo); iod = to_monthly(iod); sun = to_monthly(sun)
moon.index = pd.to_datetime(moon.index).to_period('M').to_timestamp()
moon = moon.groupby(moon.index).first()

common = nino.index
for s in [amo, tna, pdo, iod, moon.index, sun]:
    common = common.intersection(s.index if hasattr(s,'index') else s)
common = common.sort_values()
print(f"Common: {common.min().date()} → {common.max().date()}, n={len(common)}")

NINO = nino.reindex(common).values.astype(float)
AMO  = amo.reindex(common).values.astype(float)
TNA  = tna.reindex(common).values.astype(float)
PDO  = pdo.reindex(common).values.astype(float)
IOD  = iod.reindex(common).values.astype(float)
moon_a = moon.reindex(common)
OM = moon_a['OM'].values.astype(float)
MOON_OM_S = np.sin(np.deg2rad(OM)); MOON_OM_C = np.cos(np.deg2rad(OM))
MOON_EC = moon_a['EC'].values.astype(float)
SUN = sun.reindex(common).values.astype(float)
DATES = common; N = len(NINO); SPLIT = N//2

print(f"SUN range: {SUN.min():.1f} to {SUN.max():.1f}")

RUNGS = [(k, PHI**k) for k in range(4, 14)]

def rung_band(arr, period_months, bw=0.2):
    n = len(arr); F = np.fft.rfft(arr - np.mean(arr))
    freqs = np.fft.rfftfreq(n, d=1.0)
    f_c = 1.0/period_months
    F[(freqs<(1-bw)*f_c) | (freqs>(1+bw)*f_c)] = 0
    return np.real(np.fft.irfft(F, n=n))

# Two configs: with and without solar
SYS_BASE = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD,
                MOON_OM_S=MOON_OM_S, MOON_OM_C=MOON_OM_C, MOON_EC=MOON_EC)
SYS_SUN  = dict(SYS_BASE)
SYS_SUN['SUN'] = SUN

R_BASE = {name: {k: rung_band(arr, p) for k,p in RUNGS} for name,arr in SYS_BASE.items()}
R_SUN  = {name: {k: rung_band(arr, p) for k,p in RUNGS} for name,arr in SYS_SUN.items()}

# Quick check: solar Schwabe should show up at φ⁷ (~29mo) — wait that's too short. φ⁹ (~76mo = 6yr)?
# Schwabe period is ~132 months ≈ 11yr → between φ¹⁰ (123mo) and φ¹¹ (199mo)
# Let's see where solar power concentrates
print("\nSolar power by rung (training half, ratio of band power to total):")
for k,p in RUNGS:
    band_var = float(np.var(R_SUN['SUN'][k][:SPLIT]))
    total_var = float(np.var(SUN[:SPLIT]))
    frac = band_var/total_var
    print(f"  k={k:>2} (T={p:>5.0f}mo): {frac*100:>5.1f}%")

def dir_truth(arr, t, h):
    if t + h >= len(arr): return None
    diff = arr[t + h] - arr[t]
    return 1 if diff > 0 else (-1 if diff < 0 else 0)

def acc_FW(idx, h, train_max, FEEDERS, R, ridge=0.0):
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

HORIZONS = [12, 18, 24, 36, 48, 60, 72, 96, 120, 150, 180]
test_idx = list(range(SPLIT, N))

print(f"\n========= ADD-SOLAR TEST (test n={len(test_idx)}) =========")
print(f"{'horizon':>10}  {'no_solar':>9}  {'+solar':>7}  {'no_solar_R':>11}  {'+solar_R':>9}  {'delta_R':>8}")

results = {}
for h in HORIZONS:
    a_base    = acc_FW(test_idx, h, SPLIT, list(SYS_BASE.keys()), R_BASE) or 0.5
    a_sun     = acc_FW(test_idx, h, SPLIT, list(SYS_SUN.keys()),  R_SUN)  or 0.5
    a_base_r  = acc_FW(test_idx, h, SPLIT, list(SYS_BASE.keys()), R_BASE, ridge=10.0) or 0.5
    a_sun_r   = acc_FW(test_idx, h, SPLIT, list(SYS_SUN.keys()),  R_SUN,  ridge=10.0) or 0.5
    delta_r = a_sun_r - a_base_r
    flag = ' ★' if delta_r > 0.02 else ('  ' if abs(delta_r) <= 0.02 else ' ↓')
    print(f"  h={h:>3} mo  {a_base:>9.1%}  {a_sun:>7.1%}  {a_base_r:>11.1%}  {a_sun_r:>9.1%}  {delta_r:+.3f}{flag}")
    results[h] = dict(no_solar=a_base, with_solar=a_sun, no_solar_ridge=a_base_r, with_solar_ridge=a_sun_r, delta_ridge=delta_r)

# Save
out = dict(
    sources=dict(
        nino="NOAA PSL", amo="NOAA PSL", tna="NOAA PSL", pdo="NOAA NCEI ERSST V5",
        iod="NOAA PSL DMI", moon="NASA JPL Horizons",
        sun="SILSO Royal Observatory Belgium https://www.sidc.be/SILSO/INFO/snmtotcsv.php",
    ),
    common_range=[DATES[0].strftime('%Y-%m'), DATES[-1].strftime('%Y-%m')],
    train_n=int(SPLIT), test_n=int(N-SPLIT),
    horizons=HORIZONS,
    feeders_base=list(SYS_BASE.keys()),
    feeders_sun=list(SYS_SUN.keys()),
    rungs=[[k,p] for k,p in RUNGS],
    results={str(h):r for h,r in results.items()},
    solar_band_distribution={str(k): float(np.var(R_SUN['SUN'][k][:SPLIT])/np.var(SUN[:SPLIT])) for k,_ in RUNGS},
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.HORIZON_SOLAR = " + json.dumps(out) + ";\n")
print(f"\nSaved -> {OUT}")
