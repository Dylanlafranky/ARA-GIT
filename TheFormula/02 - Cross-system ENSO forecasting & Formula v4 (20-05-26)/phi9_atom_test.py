"""
phi9 atom test (resurrecting 243_phi9_atom concept).

Architecture: 3 systems × 3 rungs (parent/target/child) = 9 coupled oscillators.

For ENSO direction prediction:
  3 NODES (the strongest contributors to ENSO):
    - NINO (target system itself)
    - PDO  (Pacific decadal — strongest matched-rung partner)
    - AMO  (Atlantic — strong horizontal coupler)
  3 RUNGS (parent / target / child relative to ENSO's main cycle):
    - PARENT  rung = φ⁹ (~76 mo, decadal scale above ENSO)
    - TARGET  rung = φ⁸ (~47 mo, ENSO's own cycle)
    - CHILD   rung = φ⁷ (~29 mo, sub-cycle, QBO-scale)

For each of the 9 (system, rung) channels at each timestep:
  Get Hilbert envelope (amplitude) + cos(phase) + sin(phase) = 3 features
  → 27 features total per timestep, used as inputs to direction regression.

Compare to baseline (the 86% direction prediction with bandpass amplitudes only).

Tests Dylan's "missing a phi system" intuition: maybe the 9-channel atom IS
the missing structural unit that pushes past the 86% ceiling.

DATA: real NOAA Niño 3.4, AMO, PDO + JPL Horizons Moon (same time slice as v2).
"""
import json, os, re, math
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
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\phi9_atom_data.js")

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

# === 9-ATOM: 3 nodes × 3 rungs ===
NODES = ['NINO', 'PDO', 'AMO']  # 3 systems
RUNGS_3 = [(7, PHI**7), (8, PHI**8), (9, PHI**9)]  # child / target / parent
NODE_DATA = {'NINO': NINO, 'PDO': PDO, 'AMO': AMO}

# Compute Hilbert envelope, cos(phase), sin(phase) for each (node, rung) channel
phi9_features = {}
for nm in NODES:
    phi9_features[nm] = {}
    for k, p in RUNGS_3:
        bp = bandpass(NODE_DATA[nm], p)
        analytic = hilbert(bp)
        phi9_features[nm][k] = dict(
            envelope=np.abs(analytic),
            cos_phase=np.cos(np.angle(analytic)),
            sin_phase=np.sin(np.angle(analytic)),
            bp=bp,
        )

print(f"\n9-atom built: {len(NODES)} nodes × {len(RUNGS_3)} rungs = {len(NODES)*len(RUNGS_3)} channels")
print(f"Per channel: envelope + cos(phase) + sin(phase) = 3 features")
print(f"Total features per timestep: {len(NODES)*len(RUNGS_3)*3} = 27")

# === BASELINE: same as direction_prediction_v2 (full 8 feeders, bandpass amplitudes) ===
RUNGS_FULL = [(k, PHI**k) for k in range(4, 14)]
SYS_FULL = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD,
                MOON_OM_S=MOON_OM_S, MOON_OM_C=MOON_OM_C, MOON_EC=MOON_EC)
R_FULL = {nm: {k: bandpass(arr, p) for k,p in RUNGS_FULL} for nm,arr in SYS_FULL.items()}

def dir_truth(arr, t, h):
    if t + h >= len(arr): return None
    diff = arr[t + h] - arr[t]
    return 1 if diff > 0 else (-1 if diff < 0 else 0)

def acc_baseline(idx, h, train_max, ridge=10.0):
    """Per-rung framework regression with all 8 feeders."""
    if train_max - h < 20: return None
    rung_betas = {}
    feeders = list(SYS_FULL.keys())
    for k,_ in RUNGS_FULL:
        rows=[]; ys=[]
        for t in range(train_max - h):
            feat = [R_FULL[nm][k][t] for nm in feeders]; feat.append(1.0)
            rows.append(feat); ys.append(R_FULL['NINO'][k][t+h])
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
        for k,_ in RUNGS_FULL:
            b = rung_betas[k]
            feat = [R_FULL[nm][k][t] for nm in feeders] + [1.0]
            s += float(np.dot(b, feat))
        pred = 1 if s>NINO[t] else -1
        correct += (pred==true); total += 1
    return correct/total if total else 0

# === 9-ATOM: single regression with 27 features predicting NINO[t+h] ===
def acc_phi9_atom(idx, h, train_max, ridge=10.0, include_baseline=True):
    """Single regression with 27 phi9-atom features (+ optional baseline rung amps)."""
    if train_max - h < 20: return None
    rows=[]; ys=[]
    for t in range(train_max - h):
        feat = []
        for nm in NODES:
            for k, _ in RUNGS_3:
                d = phi9_features[nm][k]
                feat.append(d['envelope'][t])
                feat.append(d['cos_phase'][t])
                feat.append(d['sin_phase'][t])
        if include_baseline:
            # Also include the baseline NINO bandpass at all rungs for direct anchor
            for k,_ in RUNGS_FULL:
                feat.append(R_FULL['NINO'][k][t])
        feat.append(1.0)
        rows.append(feat); ys.append(NINO[t+h])
    X = np.array(rows); y = np.array(ys)
    n_features = X.shape[1]
    A = X.T @ X + ridge * np.eye(n_features); A[-1,-1] -= ridge
    b = np.linalg.solve(A, X.T @ y)

    correct=0; total=0
    for t in idx:
        true = dir_truth(NINO, t, h)
        if true is None or true==0: continue
        feat = []
        for nm in NODES:
            for k, _ in RUNGS_3:
                d = phi9_features[nm][k]
                feat.append(d['envelope'][t])
                feat.append(d['cos_phase'][t])
                feat.append(d['sin_phase'][t])
        if include_baseline:
            for k,_ in RUNGS_FULL:
                feat.append(R_FULL['NINO'][k][t])
        feat.append(1.0)
        s = float(np.dot(b, feat))
        pred = 1 if s>NINO[t] else -1
        correct += (pred==true); total += 1
    return correct/total if total else 0

HORIZONS = [12, 24, 36, 48]
test_idx = list(range(SPLIT, N))

print(f"\n========= phi9 ATOM RESULTS =========")
print(f"{'horizon':>10}  {'baseline':>9}  {'phi9_atom':>10}  {'phi9 + baseline':>16}")
results = {}
for h in HORIZONS:
    a_base = acc_baseline(test_idx, h, SPLIT)
    a_phi9 = acc_phi9_atom(test_idx, h, SPLIT, include_baseline=False)
    a_phi9_plus = acc_phi9_atom(test_idx, h, SPLIT, include_baseline=True)
    print(f"  h={h:>2} mo  {a_base*100:>8.1f}%  {a_phi9*100:>9.1f}%  {a_phi9_plus*100:>14.1f}%")
    results[h] = dict(baseline=a_base, phi9_only=a_phi9, phi9_plus_baseline=a_phi9_plus)
    delta = a_phi9_plus - a_base
    flag = ' ★' if delta > 0.005 else ('  ↓' if delta < -0.005 else '')
    print(f"          {' '*8}     {' '*8}     {' '*9}    Δ vs baseline: {delta*100:+.1f} pp {flag}")

# Save
out = dict(
    sources="Same as direction_prediction_v2",
    architecture=dict(nodes=NODES, rungs=[k for k,_ in RUNGS_3], features_per_channel=3, total_features=27),
    horizons=HORIZONS,
    results=results,
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.PHI9_ATOM = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
