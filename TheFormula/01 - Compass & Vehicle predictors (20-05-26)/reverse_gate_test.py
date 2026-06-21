"""
Reverse gate test (resurrecting 243AS concept).

Hypothesis: adjacent φ-rungs breathe in OPPOSITION.
When rung k is in accumulation phase, rung k+1 is in release phase.
The "inverse gate" relation: inv_gate = 2 - gate.

Tests:
  1. Compute Hilbert phase of ENSO at each φ-rung (and other systems)
  2. Measure phase correlation between adjacent rungs (k vs k+1)
  3. If anti-phase → correlation should be NEGATIVE
  4. If in-phase → correlation should be POSITIVE
  5. Test if anti-phase prior helps direction prediction (constrain rung k+1's phase = π - rung k's phase + offset)

Three sub-tests:
  A. Direct phase correlation between adjacent rungs (across all systems)
  B. Use phase OF NEIGHBOR as a feature in direction regression
  C. Apply anti-phase reconstruction (add inverse-phase signal) to see if it adds lift

DATA: real NOAA Niño 3.4, AMO, TNA, PDO, IOD + JPL Moon (same as direction_v2).
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
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\reverse_gate_data.js")

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

# === SUB-TEST A: phase correlation between adjacent rungs ===
RUNGS = [(k, PHI**k) for k in range(4, 14)]
SYS = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD)

phases = {nm: {} for nm in SYS}
for nm, arr in SYS.items():
    for k, p in RUNGS:
        bp = bandpass(arr, p)
        phases[nm][k] = np.angle(hilbert(bp))

# For each system, compute correlation between adjacent rung phases
# Use cos(phase) as the comparable real signal
print("\n========= ADJACENT RUNG PHASE RELATIONSHIPS =========")
print(f"For each system, correlation between cos(phase_k) and cos(phase_k+1)")
print(f"Negative → ANTI-PHASE (243AS prediction). Positive → in-phase. Near zero → independent.\n")
print(f"{'system':>8}  ", end='')
for k,_ in RUNGS[:-1]: print(f"{f'k={k}→{k+1}':>11}", end='  ')
print()

phase_corrs = {}
for nm in SYS:
    print(f"  {nm:>6}  ", end='')
    phase_corrs[nm] = {}
    for i in range(len(RUNGS)-1):
        k1, k2 = RUNGS[i][0], RUNGS[i+1][0]
        c1 = np.cos(phases[nm][k1]); c2 = np.cos(phases[nm][k2])
        if np.std(c1) > 1e-9 and np.std(c2) > 1e-9:
            corr = float(np.corrcoef(c1, c2)[0,1])
        else: corr = 0
        phase_corrs[nm][f"{k1}_{k2}"] = corr
        print(f"{corr:>+10.3f}  ", end='')
    print()

# Aggregate across systems
print("\nAggregate across systems (mean ± std):")
for i in range(len(RUNGS)-1):
    k1, k2 = RUNGS[i][0], RUNGS[i+1][0]
    corrs = [phase_corrs[nm][f"{k1}_{k2}"] for nm in SYS]
    print(f"  k={k1:>2}→{k2:<2}: mean={np.mean(corrs):+.3f} ± {np.std(corrs):.3f}")

# === SUB-TEST B: include neighbor-rung phase as feature in direction regression ===
print(f"\n========= USING NEIGHBOR-RUNG PHASE AS FEATURE =========")
R = {nm: {k: bandpass(arr, p) for k,p in RUNGS} for nm,arr in SYS.items()}
# Add Moon
SYS_full = dict(SYS); SYS_full['MOON_OM_S'] = MOON_OM_S; SYS_full['MOON_OM_C'] = MOON_OM_C; SYS_full['MOON_EC'] = MOON_EC
R['MOON_OM_S'] = {k: bandpass(MOON_OM_S, p) for k,p in RUNGS}
R['MOON_OM_C'] = {k: bandpass(MOON_OM_C, p) for k,p in RUNGS}
R['MOON_EC']  = {k: bandpass(MOON_EC, p) for k,p in RUNGS}

# Inverse phase: -cos(phase)  (the "anti-phase" signal at each rung)
inv_phase_R = {}
for nm in SYS:
    inv_phase_R[nm] = {}
    for k,_ in RUNGS:
        inv_phase_R[nm][k] = -np.cos(phases[nm][k])

def dir_truth(arr, t, h):
    if t + h >= len(arr): return None
    diff = arr[t + h] - arr[t]
    return 1 if diff > 0 else (-1 if diff < 0 else 0)

def acc_FW(idx, h, train_max, FEEDERS, R, extra_feature_per_rung=None, ridge=10.0):
    """If extra_feature_per_rung[k][t] is provided, add as feature at each rung."""
    if train_max - h < 20: return None
    rung_betas = {}
    for k,_ in RUNGS:
        rows=[]; ys=[]
        for t in range(train_max - h):
            feat = [R[nm][k][t] for nm in FEEDERS]
            if extra_feature_per_rung is not None:
                feat.append(extra_feature_per_rung[k][t])
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
            if extra_feature_per_rung is not None:
                feat.append(extra_feature_per_rung[k][t])
            feat.append(1.0)
            s += float(np.dot(b, feat))
        pred = 1 if s>NINO[t] else -1
        correct += (pred==true); total += 1
    return correct/total if total else 0

FEEDERS = list(SYS_full.keys())
HORIZONS = [12, 24, 36, 48]
test_idx = list(range(SPLIT, N))

# Build extra feature: at each rung k, use cos(phase) at neighbor rung k+1 (inverted)
# i.e., for predicting rung k, also feed in -cos(phase_k+1) — the anti-phase signal of the next rung up
neighbor_inv_phase = {}
for k,_ in RUNGS:
    if k+1 in [kk for kk,_ in RUNGS]:
        neighbor_inv_phase[k] = -np.cos(phases['NINO'].get(k+1, phases['NINO'][k]))
    else:
        neighbor_inv_phase[k] = -np.cos(phases['NINO'][k])

# Also baseline (no extra feature)
print(f"\n{'horizon':>10}  {'baseline':>9}  {'+inv_phase_neighbor':>22}")
results = {}
for h in HORIZONS:
    a_base = acc_FW(test_idx, h, SPLIT, FEEDERS, R, extra_feature_per_rung=None)
    a_inv = acc_FW(test_idx, h, SPLIT, FEEDERS, R, extra_feature_per_rung=neighbor_inv_phase)
    diff = a_inv - a_base
    flag = ' ★' if diff > 0.005 else ('  ↓' if diff < -0.005 else '')
    print(f"  h={h:>2} mo  {a_base*100:>8.1f}%  {a_inv*100:>20.1f}%  ({diff*100:+.1f} pp){flag}")
    results[h] = dict(baseline=a_base, with_inv_phase=a_inv, diff=diff)

# Save
out = dict(
    sources="Same as direction_prediction_v2 (NOAA + JPL Horizons)",
    horizons=HORIZONS,
    phase_correlations_per_system={nm: phase_corrs[nm] for nm in SYS},
    direction_results=results,
    aggregate_phase_corr_per_pair={
        f"{RUNGS[i][0]}_{RUNGS[i+1][0]}": dict(
            mean=float(np.mean([phase_corrs[nm][f"{RUNGS[i][0]}_{RUNGS[i+1][0]}"] for nm in SYS])),
            std=float(np.std([phase_corrs[nm][f"{RUNGS[i][0]}_{RUNGS[i+1][0]}"] for nm in SYS])),
        ) for i in range(len(RUNGS)-1)
    },
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.REVERSE_GATE = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
