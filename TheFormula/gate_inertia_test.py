"""
Gate inertia test (resurrecting 243BG concept) — applied to ENSO direction prediction.

Mechanism:
  gate_ara[t] = gate_ara[t-1] + clamp(inst_ara[t] - gate_ara[t-1], ±max_delta)

The gate cannot follow inst_ara instantly; it has bounded rate of change per step.

LAG signal:
  lag[t] = inst_ara[t] - gate_ara[t]
  Positive lag → tension backing up (about to overshoot)
  Negative lag → energy bled out (about to undershoot)

Test plan:
  1. Compute rolling ARA on ENSO from data (no fitting)
  2. Compute gate_ara with inertia at multiple max_delta values
  3. Use gate_lag at time t as a NEW FEATURE in the per-rung framework regression
  4. Compare h=24mo direction accuracy to baseline (86% from direction_prediction_v2)

If gate inertia adds value, the LAG feature gives us information about
when extreme peaks/valleys are coming — exactly the amplitude reach we've been missing.

DATA: real PhysioNet (nsr001) + real NOAA Niño 3.4, AMO, TNA, PDO, IOD + JPL Moon.
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
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\gate_inertia_data.js")

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

# === Cycle-based ARA computation (correct version) ===
# For each peak-to-peak cycle, ARA = (1 - trough_fraction) / trough_fraction
# Then propagate per-cycle ARA to every time step within that cycle.
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d

def cycle_based_inst_ara(arr, target_period, dt=1.0):
    """For each peak-to-peak cycle, compute ARA from trough position.
       ARA = T_acc/T_rel = (1 - f_trough)/f_trough where f_trough is the trough's fraction within cycle."""
    smooth_sigma = max(1, int(target_period * 0.15 / dt))
    smoothed = gaussian_filter1d(arr - np.mean(arr), smooth_sigma)
    min_dist = int(target_period * 0.7 / dt)
    peaks, _ = find_peaks(smoothed, distance=min_dist)
    n = len(arr)
    out = np.full(n, 1.0)
    for i in range(len(peaks)-1):
        seg = arr[peaks[i]:peaks[i+1]]
        if len(seg) < 4: continue
        trough_pos = int(np.argmin(seg))
        f_trough = trough_pos / max(1, len(seg)-1)
        # Avoid edge cases
        f_trough = max(0.05, min(0.95, f_trough))
        ara = (1 - f_trough) / f_trough
        out[peaks[i]:peaks[i+1]] = ara
    return out, peaks

# Compute inst_ara from actual ENSO cycles (peak-to-peak at φ⁸ ~47mo)
NINO_inst_ara, nino_peaks = cycle_based_inst_ara(NINO, PHI**8, dt=1.0)
print(f"\nNINO instantaneous ARA: mean={np.mean(NINO_inst_ara):.3f}, range=[{np.min(NINO_inst_ara):.2f}, {np.max(NINO_inst_ara):.2f}]")

# === Gate inertia: bounded chase ===
def gate_inertia(inst_ara, max_delta):
    n = len(inst_ara); gate = np.full(n, 1.0)
    gate[0] = inst_ara[0]
    for t in range(1, n):
        delta = inst_ara[t] - gate[t-1]
        delta = max(-max_delta, min(max_delta, delta))
        gate[t] = gate[t-1] + delta
    return gate

# Three max_delta values at φ-powers (per 243BG)
DELTAS = {
    'phi_-2': 1/PHI**2,
    'phi_-3': 1/PHI**3,
    'phi_-4': 1/PHI**4,
}

gate_aras = {}
gate_lags = {}
for name, md in DELTAS.items():
    g = gate_inertia(NINO_inst_ara, md)
    gate_aras[name] = g
    gate_lags[name] = NINO_inst_ara - g
    print(f"  max_delta = {name} ({md:.4f}): gate range [{np.min(g):.2f}, {np.max(g):.2f}], lag std={np.std(gate_lags[name]):.4f}")

# === Direction prediction: baseline + each gate-inertia variant ===
def bandpass(arr, period_units, dt=1.0, bw=0.4):
    n = len(arr); F = np.fft.rfft(arr - np.mean(arr))
    freqs = np.fft.rfftfreq(n, d=dt)
    f_c = 1.0/period_units
    F[(freqs<(1-bw)*f_c) | (freqs>(1+bw)*f_c)] = 0
    return np.real(np.fft.irfft(F, n=n))

RUNGS = [(k, PHI**k) for k in range(4, 14)]
SYS = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD,
           MOON_OM_S=MOON_OM_S, MOON_OM_C=MOON_OM_C, MOON_EC=MOON_EC)
R = {nm: {k: bandpass(arr, p) for k,p in RUNGS} for nm,arr in SYS.items()}

# Add gate-lag as a non-banded feature (single value per timestep)
# But we apply per rung: for each rung k, include (NINO_lag at that time) as one extra feature
# Actually simplest: include the gate_lag at each test time as a per-rung scalar (broadcasted)

def dir_truth(arr, t, h):
    if t + h >= len(arr): return None
    diff = arr[t + h] - arr[t]
    return 1 if diff > 0 else (-1 if diff < 0 else 0)

def acc_FW_with_lag(idx, h, train_max, FEEDERS, R, lag_signal=None, ridge=10.0):
    """If lag_signal is provided, include it as additional feature in EVERY rung's regression."""
    if train_max - h < 20: return None
    rung_betas = {}
    for k,_ in RUNGS:
        rows=[]; ys=[]
        for t in range(train_max - h):
            feat = [R[nm][k][t] for nm in FEEDERS]
            if lag_signal is not None:
                feat.append(lag_signal[t])
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
            if lag_signal is not None:
                feat.append(lag_signal[t])
            feat.append(1.0)
            s += float(np.dot(b, feat))
        pred = 1 if s>NINO[t] else -1
        correct += (pred==true); total += 1
    return correct/total if total else 0

FEEDERS = list(SYS.keys())
HORIZONS = [12, 24, 36, 48]
test_idx = list(range(SPLIT, N))

print(f"\n========= GATE INERTIA — DIRECTION PREDICTION RESULTS =========")
print(f"{'horizon':>10}  {'baseline':>9}  ", end='')
for name in DELTAS: print(f"{'+lag_'+name:>14}", end='  ')
print()

results = {}
for h in HORIZONS:
    a_base = acc_FW_with_lag(test_idx, h, SPLIT, FEEDERS, R, lag_signal=None)
    print(f"  h={h:>2} mo  {a_base*100:>8.1f}%  ", end='')
    horizon_results = dict(baseline=a_base)
    for name, md in DELTAS.items():
        a = acc_FW_with_lag(test_idx, h, SPLIT, FEEDERS, R, lag_signal=gate_lags[name])
        horizon_results[name] = a
        diff = a - a_base
        flag = ' ★' if diff > 0.005 else ''
        print(f"{a*100:>11.1f}% {flag}", end='  ')
    print()
    results[h] = horizon_results

# Also test inst_ara as feature directly (without inertia) for comparison
print(f"\nDirect inst_ara (no inertia) as feature:")
for h in HORIZONS:
    a_inst = acc_FW_with_lag(test_idx, h, SPLIT, FEEDERS, R, lag_signal=NINO_inst_ara)
    base = results[h]['baseline']
    print(f"  h={h:>2} mo: baseline {base*100:.1f}%  +inst_ara {a_inst*100:.1f}%  ({(a_inst-base)*100:+.1f} pp)")
    results[h]['inst_ara_direct'] = a_inst

# Save
out = dict(
    sources="Same as direction_prediction_v2 (NOAA + JPL Horizons)",
    horizons=HORIZONS,
    deltas={k: float(v) for k,v in DELTAS.items()},
    nino_inst_ara=dict(
        mean=float(np.mean(NINO_inst_ara)),
        std=float(np.std(NINO_inst_ara)),
        min=float(np.min(NINO_inst_ara)),
        max=float(np.max(NINO_inst_ara)),
    ),
    gate_lag_stats={
        name: dict(std=float(np.std(gate_lags[name])),
                   range=[float(np.min(gate_lags[name])), float(np.max(gate_lags[name]))])
        for name in DELTAS
    },
    results=results,
    nino_inst_ara_traj=NINO_inst_ara.tolist(),
    gate_aras={name: g.tolist() for name, g in gate_aras.items()},
    gate_lags_traj={name: l.tolist() for name, l in gate_lags.items()},
    nino_actual=NINO.tolist(),
    dates=[d.strftime('%Y-%m') for d in DATES],
    split=int(SPLIT),
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.GATE_INERTIA = " + json.dumps(out, default=str) + ";\n")
print("Saved -> " + OUT)
