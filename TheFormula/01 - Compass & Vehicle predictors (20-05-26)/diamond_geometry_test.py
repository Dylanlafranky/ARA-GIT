"""
Diamond geometry test (resurrecting 243AV reverse triangle).

Concept:
  Main triangle: apex at φ, singularity at base.
    main_valve = 1/(1+ARA) = "acc fraction"
    Energy flowing AWAY from singularity, TOWARD φ.

  Reverse triangle: apex at base singularity reaching UP.
    reverse_valve = ARA/(1+ARA) = "snap fraction"
    Energy flowing TOWARD singularity (release direction).

  Together = diamond.

For each rung's per-cycle ARA, compute BOTH valves. Use as features alongside
bandpass amplitudes in the per-rung regression. Tests whether the diamond
geometry (twin landmarks) gives information the single bandpass misses.

For ENSO direction prediction at h=24mo (current baseline 85.9%).

DATA: real NOAA + JPL Horizons (verified sources, same as direction_v2).
"""
import json, os, re, math
import numpy as np, pandas as pd
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d

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
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\diamond_geometry_data.js")

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

print("Loading...")
nino = load_nino()
amo = load_grid_text(AMO_PATH); tna = load_grid_text(TNA_PATH)
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
moon_a = moon.reindex(common); OM = moon_a['OM'].values.astype(float)
MOON_OM_S = np.sin(np.deg2rad(OM)); MOON_OM_C = np.cos(np.deg2rad(OM))
MOON_EC = moon_a['EC'].values.astype(float)
DATES = common; N = len(NINO); SPLIT = N//2

def bandpass(arr, period_units, dt=1.0, bw=0.4):
    n = len(arr); F = np.fft.rfft(arr - np.mean(arr))
    freqs = np.fft.rfftfreq(n, d=dt)
    f_c = 1.0/period_units
    F[(freqs<(1-bw)*f_c) | (freqs>(1+bw)*f_c)] = 0
    return np.real(np.fft.irfft(F, n=n))

# === Cycle-based ARA + diamond valves ===
# CRITICAL: clip ARA to a sane range to avoid the amp_scale outliers we saw
def cycle_diamond_valves(arr, target_period, dt=1.0):
    """For each peak-to-peak cycle, compute:
       ARA = (1 - f_trough) / f_trough (clipped to [0.2, 5])
       main_valve = 1/(1+ARA)
       reverse_valve = ARA/(1+ARA)
    """
    smooth_sigma = max(1, int(target_period * 0.15 / dt))
    smoothed = gaussian_filter1d(arr - np.mean(arr), smooth_sigma)
    min_dist = int(target_period * 0.7 / dt)
    peaks, _ = find_peaks(smoothed, distance=min_dist)
    n = len(arr)
    main_arr = np.full(n, 0.5)
    rev_arr = np.full(n, 0.5)
    for i in range(len(peaks)-1):
        seg = arr[peaks[i]:peaks[i+1]]
        if len(seg) < 4: continue
        trough_pos = int(np.argmin(seg))
        f_trough = trough_pos / max(1, len(seg)-1)
        f_trough = max(0.1, min(0.9, f_trough))  # tighter clip
        ara = (1 - f_trough) / f_trough
        ara = max(0.2, min(5.0, ara))  # sane range
        main = 1.0/(1.0 + ara)
        rev = ara/(1.0 + ara)
        main_arr[peaks[i]:peaks[i+1]] = main
        rev_arr[peaks[i]:peaks[i+1]] = rev
    return main_arr, rev_arr

# Compute diamond valves at multiple ENSO rungs
RUNGS = [(k, PHI**k) for k in range(4, 14)]
NINO_main = {}
NINO_rev = {}
print("Computing diamond valves per rung for ENSO...")
for k, p in RUNGS:
    main, rev = cycle_diamond_valves(NINO, p)
    NINO_main[k] = main
    NINO_rev[k] = rev
    print(f"  k={k:>2} (T={p:>5.1f}mo): main_valve range [{main.min():.3f}, {main.max():.3f}], reverse range [{rev.min():.3f}, {rev.max():.3f}]")

# === Direction prediction with diamond features ===
SYS = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD,
           MOON_OM_S=MOON_OM_S, MOON_OM_C=MOON_OM_C, MOON_EC=MOON_EC)
R = {nm: {k: bandpass(arr, p) for k,p in RUNGS} for nm,arr in SYS.items()}

def dir_truth(arr, t, h):
    if t + h >= len(arr): return None
    diff = arr[t + h] - arr[t]
    return 1 if diff > 0 else (-1 if diff < 0 else 0)

def acc_FW(idx, h, train_max, FEEDERS, R, extra_features=None, ridge=10.0):
    """extra_features: list of dicts, each {k: array_indexed_by_time} per rung."""
    if train_max - h < 20: return None
    rung_betas = {}
    for k,_ in RUNGS:
        rows=[]; ys=[]
        for t in range(train_max - h):
            feat = [R[nm][k][t] for nm in FEEDERS]
            if extra_features is not None:
                for ef in extra_features:
                    feat.append(ef[k][t])
            feat.append(1.0)
            rows.append(feat); ys.append(R['NINO'][k][t+h])
        X = np.array(rows); y = np.array(ys)
        n_features = X.shape[1]
        A = X.T @ X + ridge * np.eye(n_features); A[-1,-1] -= ridge
        b = np.linalg.solve(A, X.T @ y)
        rung_betas[k] = b
    correct=0; total=0
    mean_n = float(np.mean(NINO[:train_max]))
    for t in idx:
        true = dir_truth(NINO, t, h)
        if true is None or true==0: continue
        s = mean_n
        for k,_ in RUNGS:
            b = rung_betas[k]
            feat = [R[nm][k][t] for nm in FEEDERS]
            if extra_features is not None:
                for ef in extra_features:
                    feat.append(ef[k][t])
            feat.append(1.0)
            s += float(np.dot(b, feat))
        pred = 1 if s>NINO[t] else -1
        correct += (pred==true); total += 1
    return correct/total if total else 0

FEEDERS = list(SYS.keys())
HORIZONS = [12, 24, 36, 48]
test_idx = list(range(SPLIT, N))

print(f"\n========= DIAMOND GEOMETRY RESULTS =========")
print(f"{'horizon':>10}  {'baseline':>9}  {'+main':>7}  {'+reverse':>9}  {'+both':>7}")
results = {}
for h in HORIZONS:
    a_base = acc_FW(test_idx, h, SPLIT, FEEDERS, R, extra_features=None)
    a_main = acc_FW(test_idx, h, SPLIT, FEEDERS, R, extra_features=[NINO_main])
    a_rev  = acc_FW(test_idx, h, SPLIT, FEEDERS, R, extra_features=[NINO_rev])
    a_both = acc_FW(test_idx, h, SPLIT, FEEDERS, R, extra_features=[NINO_main, NINO_rev])
    print(f"  h={h:>2} mo  {a_base*100:>8.1f}%  {a_main*100:>6.1f}%  {a_rev*100:>8.1f}%  {a_both*100:>6.1f}%")
    results[h] = dict(baseline=a_base, with_main=a_main, with_reverse=a_rev, with_both=a_both)

print(f"\nLifts vs baseline:")
for h in HORIZONS:
    r = results[h]
    bd = r['baseline']
    flag_main = ' ★' if r['with_main']-bd > 0.005 else ('  ↓' if r['with_main']-bd < -0.005 else '')
    flag_rev = ' ★' if r['with_reverse']-bd > 0.005 else ('  ↓' if r['with_reverse']-bd < -0.005 else '')
    flag_both = ' ★' if r['with_both']-bd > 0.005 else ('  ↓' if r['with_both']-bd < -0.005 else '')
    print(f"  h={h:>2} mo  main {(r['with_main']-bd)*100:+.1f}{flag_main}  rev {(r['with_reverse']-bd)*100:+.1f}{flag_rev}  both {(r['with_both']-bd)*100:+.1f}{flag_both}")

out = dict(
    sources="Same as direction_prediction_v2 (verified NOAA + JPL Horizons)",
    horizons=HORIZONS,
    formula=dict(main_valve="1/(1+ARA)", reverse_valve="ARA/(1+ARA)"),
    results=results,
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.DIAMOND = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
