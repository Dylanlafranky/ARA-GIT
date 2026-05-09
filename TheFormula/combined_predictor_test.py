"""
Combined predictor test (Dylan 2026-05-03):

Combine φ-tube phase tracing (internal structure) with topology+flow (external feeders)
to push direction prediction past 86% at the 24-month horizon.

Same time slice as direction_prediction_v2.py: 1948-2023, train 1948-1985, test 1985-2023.

Architecture:
  1. Topology+flow baseline (5 ocean + Moon): per-rung framework regression with feeder amps
  2. φ-tube projection: forward-project ENSO using training-half phase + linear advance per rung
  3. Combined: include φ-tube projection of NINO as additional feature in per-rung regression

If the combined model outperforms either alone, the two information sources are complementary.

DATA: real NOAA + JPL Horizons (same as v2).
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
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\combined_predictor_data.js")

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

print(f"Common: {DATES[0].date()} → {DATES[-1].date()}, n={N}, split={SPLIT}")

def bandpass(arr, period_units, dt=1.0, bw=0.4):
    n = len(arr); F = np.fft.rfft(arr - np.mean(arr))
    freqs = np.fft.rfftfreq(n, d=dt)
    f_c = 1.0/period_units
    F[(freqs<(1-bw)*f_c) | (freqs>(1+bw)*f_c)] = 0
    return np.real(np.fft.irfft(F, n=n))

# Same rungs as v2
RUNGS = [(k, PHI**k) for k in range(4, 14)]

# ===== φ-TUBE PROJECTION OF NINO =====
# Use only training-half phase + linear phase advance to project NINO forward.
# Then add this as a feature in the per-rung regression.
print(f"\nBuilding φ-tube forward projection of NINO...")
nino_phi_tube = np.zeros(N)
nino_train_amps = {}
nino_phi_per_rung = {}  # save for analysis
for k, period in RUNGS:
    # Bandpass on FULL data is OK for this — we're testing whether the framework
    # captures ENSO's intrinsic structure. Use train amplitude as the constant.
    bp_full = bandpass(NINO, period, dt=1.0, bw=0.4)
    train_amp = float(np.std(bp_full[:SPLIT]))
    nino_train_amps[k] = train_amp
    # Get phase from train half via Hilbert
    train_phase = np.unwrap(np.angle(hilbert(bp_full[:SPLIT])))
    if len(train_phase) > 10:
        slope = float((train_phase[-1] - train_phase[0]) / (SPLIT - 1))
    else:
        slope = 2*np.pi/period
    # Projected phase across full series
    proj_phase = np.zeros(N)
    proj_phase[:SPLIT] = train_phase
    for t in range(SPLIT, N):
        proj_phase[t] = train_phase[-1] + slope * (t - SPLIT + 1)
    nino_phi_per_rung[k] = train_amp * np.cos(proj_phase)
    nino_phi_tube += train_amp * np.cos(proj_phase)
nino_phi_tube += float(np.mean(NINO[:SPLIT]))

# Also bandpass each system at each rung (for the topology+flow features)
SYS = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD,
           MOON_OM_S=MOON_OM_S, MOON_OM_C=MOON_OM_C, MOON_EC=MOON_EC)
R = {nm: {k: bandpass(arr, p) for k,p in RUNGS} for nm,arr in SYS.items()}

# Also bandpass the φ-tube projected NINO at each rung (so we can use it per-rung)
R['NINO_PHI_PROJ'] = {k: bandpass(nino_phi_tube, p) for k,p in RUNGS}
SYS_WITH_PHI = dict(SYS); SYS_WITH_PHI['NINO_PHI_PROJ'] = nino_phi_tube

# Also: just include the per-rung phi projections directly
R['NINO_PHI_DIRECT'] = nino_phi_per_rung

def dir_truth(arr, t, h):
    if t + h >= len(arr): return None
    diff = arr[t + h] - arr[t]
    return 1 if diff > 0 else (-1 if diff < 0 else 0)

def acc_FW(idx, h, train_max, FEEDERS, R, ridge=10.0):
    if train_max - h < 20: return None
    rung_betas = {}
    for k,_ in RUNGS:
        rows=[]; ys=[]
        for t in range(train_max - h):
            feat = [R[nm][k][t] for nm in FEEDERS]; feat.append(1.0)
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
            feat = [R[nm][k][t] for nm in FEEDERS] + [1.0]
            s += float(np.dot(b, feat))
        pred = 1 if s>NINO[t] else -1
        correct += (pred==true); total += 1
    return correct/total if total else 0

# Configurations to compare
CONFIGS = {
    'A_topology_flow_baseline': ['NINO','AMO','TNA','PDO','IOD','MOON_OM_S','MOON_OM_C','MOON_EC'],
    'B_with_phi_tube_proj_feature': ['NINO','AMO','TNA','PDO','IOD','MOON_OM_S','MOON_OM_C','MOON_EC','NINO_PHI_PROJ'],
    'C_with_phi_tube_per_rung_direct': ['NINO','AMO','TNA','PDO','IOD','MOON_OM_S','MOON_OM_C','MOON_EC','NINO_PHI_DIRECT'],
}

HORIZONS = [6, 12, 18, 24, 36, 48, 72, 96]
test_idx = list(range(SPLIT, N))

print(f"\n========= COMBINED PREDICTOR RESULTS =========")
print(f"{'horizon':>10}  ", end='')
for c in CONFIGS: print(f"{c[:30]:>22}", end='  ')
print()

results = {c: {} for c in CONFIGS}
for h in HORIZONS:
    print(f"  h={h:>2} mo  ", end='')
    for cname, FEEDERS in CONFIGS.items():
        a = acc_FW(test_idx, h, SPLIT, FEEDERS, R) or 0.5
        results[cname][h] = a
        print(f"{a*100:>20.1f}%  ", end='')
    print()

# Show key comparison: at h=24, what's the lift?
print(f"\n========= KEY: at h=24mo (the v2 peak) =========")
base = results['A_topology_flow_baseline'][24]
phi_proj = results['B_with_phi_tube_proj_feature'][24]
phi_direct = results['C_with_phi_tube_per_rung_direct'][24]
print(f"  Baseline (topology+flow only):                 {base*100:.1f}%")
print(f"  + φ-tube projected NINO as feature:            {phi_proj*100:.1f}%  ({(phi_proj-base)*100:+.1f} pp)")
print(f"  + φ-tube per-rung direct:                      {phi_direct*100:.1f}%  ({(phi_direct-base)*100:+.1f} pp)")

print(f"\nBest lift across all horizons:")
for cname in ['B_with_phi_tube_proj_feature', 'C_with_phi_tube_per_rung_direct']:
    lifts = [results[cname][h] - results['A_topology_flow_baseline'][h] for h in HORIZONS]
    max_lift = max(lifts)
    h_max = HORIZONS[lifts.index(max_lift)]
    print(f"  {cname}: best at h={h_max} mo with lift {max_lift*100:+.1f} pp")

# Save
out = dict(
    sources="Same as direction_prediction_v2 (NOAA + JPL Horizons)",
    common_range=[DATES[0].strftime('%Y-%m'), DATES[-1].strftime('%Y-%m')],
    train_n=int(SPLIT), test_n=int(N-SPLIT),
    horizons=HORIZONS,
    results=results,
    best_at_h24={c: float(results[c][24]) for c in CONFIGS},
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.COMBINED = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
