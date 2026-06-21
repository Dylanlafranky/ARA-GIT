"""
243N camshaft gate test — per-rung valve weighting for direction prediction.

The camshaft valve from 243N: valve = 1/(1 + ARA).
For accumulation phase (cp < valve), system is consuming.
For release phase  (cp >= valve), system is emitting.

Translation to direction prediction:
  At each rung k, ENSO has its own per-rung ARA → its own valve_k.
  ENSO's bandpassed signal at rung k is currently at phase cp_k(t).
  If cp_k < valve_k: rung is in ACCUMULATION → feeders contribute one way
  If cp_k >= valve_k: rung is in RELEASE → feeders contribute the other way

Variant A — phase-gated features:
  For each rung k, multiply all that rung's features by gate_k(t) ∈ {+1, -1}
  (sign flips at the valve threshold).

Variant B — valve-weighted feeders:
  For each rung k, weight each feeder's contribution by accumulation/release
  state. Accumulation favours consumer-class feeders; release favours engines.
  Use feeder's per-rung ARA to choose role.

Variant C — A+B.

Compare to baseline.
"""
import json, os, re, math
import numpy as np, pandas as pd
from scipy.signal import find_peaks, hilbert
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
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\camshaft_gate_data.js")

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

def per_rung_ARA(raw_signal, period):
    n = len(raw_signal); F = np.fft.rfft(raw_signal - np.mean(raw_signal))
    freqs = np.fft.rfftfreq(n, d=1.0)
    f_c = 1.0/period
    bw = 0.85
    F[(freqs<(1-bw)*f_c) | (freqs>(1+bw)*f_c)] = 0
    wide = np.real(np.fft.irfft(F, n=n))
    smooth_sigma = max(1, int(period * 0.05))
    smoothed = gaussian_filter1d(wide, smooth_sigma)
    min_dist = max(2, int(period * 0.7))
    peaks, _ = find_peaks(smoothed, distance=min_dist)
    if len(peaks) < 2: return 1.0
    aras = []
    for i in range(len(peaks)-1):
        seg = smoothed[peaks[i]:peaks[i+1]+1]
        if len(seg) < 3: continue
        trough_idx = int(np.argmin(seg))
        f_t = trough_idx / max(1, len(seg)-1)
        f_t = max(0.15, min(0.85, f_t))
        aras.append((1 - f_t) / f_t)
    if not aras: return 1.0
    return float(np.mean(np.clip(aras, 0.3, 3.0)))

# === Per-rung bandpasses + Hilbert phase ===
RUNGS = [(k, PHI**k) for k in range(4, 14)]
SYS = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD,
           MOON_OM_S=MOON_OM_S, MOON_OM_C=MOON_OM_C, MOON_EC=MOON_EC)
R = {nm: {k: bandpass(arr, p) for k,p in RUNGS} for nm,arr in SYS.items()}

# Phase of NINO bandpass at each rung (cycle position in [0,1])
NINO_CP = {}
for k, p in RUNGS:
    analytic = hilbert(R['NINO'][k])
    phase = np.angle(analytic)  # [-pi, pi]
    cp = (phase + np.pi) / (2 * np.pi)  # [0, 1)
    NINO_CP[k] = cp

# Per-rung ARA → valve = 1/(1+ARA)
print("\n=== Per-rung ARA + camshaft valve ===")
RUNG_ARA = {}; VALVE = {}
for k, p in RUNGS:
    a = per_rung_ARA(NINO[:SPLIT], p)
    RUNG_ARA[k] = a
    VALVE[k] = 1.0 / (1.0 + a)
    print(f"  k={k:>2} P={p:>6.1f}mo  ARA={a:.2f}  valve={VALVE[k]:.3f}  acc-frac={VALVE[k]*100:.0f}%")

# Per-rung feeder ARAs (for variant B role assignment)
FEEDER_ARA = {}
for k, p in RUNGS:
    FEEDER_ARA[k] = {nm: per_rung_ARA(SYS[nm][:SPLIT], p) for nm in SYS}

# ========================================
# Variant A: phase-gate per rung (smooth)
# ========================================
# gate_k(t) = +1 inside accumulation window, -1 inside release
# Smooth via tanh transition near valve threshold
def phase_gate(cp, valve, slope=20.0):
    # Returns +1 if cp < valve, -1 if cp > valve, smooth around boundary
    return -np.tanh(slope * (cp - valve))

GATE = {}
for k,_ in RUNGS:
    GATE[k] = phase_gate(NINO_CP[k], VALVE[k])

# ========================================
# Variant B: feeder-role weighting per rung
# ========================================
# Engine-class feeders (ARA > 1.2) emphasised in release phase
# Consumer-class feeders (ARA < 0.8) emphasised in accumulation phase
# Clock-class (~1.0) neutral
def role_weight(feeder_ara, gate_val):
    """gate_val ∈ [-1, +1]: +1 = accumulation, -1 = release"""
    if feeder_ara > 1.2:    # engine
        return (1 - gate_val) / 2.0  # 1 in release, 0 in accumulation
    elif feeder_ara < 0.8:  # consumer
        return (1 + gate_val) / 2.0  # 1 in accumulation, 0 in release
    else:                   # clock
        return 0.5

# ========================================
# Direction prediction
# ========================================
def dir_truth(arr, t, h):
    if t + h >= len(arr): return None
    diff = arr[t + h] - arr[t]
    return 1 if diff > 0 else (-1 if diff < 0 else 0)

def fit_per_rung(extra_feature_fn, train_max, h, ridge=10.0):
    rung_betas = {}
    feeders_list = list(SYS.keys())
    for k,_ in RUNGS:
        rows=[]; ys=[]
        for t in range(train_max - h):
            feat = [R[nm][k][t] for nm in feeders_list]
            feat += extra_feature_fn(t, k, feeders_list)
            feat.append(1.0)
            rows.append(feat); ys.append(R['NINO'][k][t+h])
        X = np.array(rows); y = np.array(ys)
        nf = X.shape[1]
        A = X.T @ X + ridge*np.eye(nf); A[-1,-1] -= ridge
        b = np.linalg.solve(A, X.T @ y)
        rung_betas[k] = b
    return rung_betas, feeders_list

def predict(rung_betas, feeders_list, extra_feature_fn, idx, h):
    correct=0; total=0
    mean_n = float(np.mean(NINO[:SPLIT]))
    for t in idx:
        true = dir_truth(NINO, t, h)
        if true is None or true==0: continue
        s = mean_n
        for k,_ in RUNGS:
            b = rung_betas[k]
            feat = [R[nm][k][t] for nm in feeders_list]
            feat += extra_feature_fn(t, k, feeders_list)
            feat.append(1.0)
            s += float(np.dot(b, feat))
        pred = 1 if s > NINO[t] else -1
        correct += (pred==true); total += 1
    return correct/total if total else 0

def base_extra(t, k, fl): return []

# Variant A: each feeder × gate as extra feature
def gateA_extra(t, k, fl):
    g = GATE[k][t]
    return [R[nm][k][t] * g for nm in fl]

# Variant B: each feeder × role-weight as extra feature
def gateB_extra(t, k, fl):
    g = GATE[k][t]
    out = []
    for nm in fl:
        w = role_weight(FEEDER_ARA[k][nm], g)
        out.append(R[nm][k][t] * w)
    return out

# Variant C: A + B
def gateC_extra(t, k, fl):
    return gateA_extra(t,k,fl) + gateB_extra(t,k,fl)

HORIZONS = [12, 24, 36, 48]
test_idx = list(range(SPLIT, N))

print(f"\n========= CAMSHAFT GATE RESULTS =========")
print(f"{'horizon':>10}  {'baseline':>9}  {'+A phase':>10}  {'+B role':>9}  {'+C both':>9}")
results = {}
for h in HORIZONS:
    rb_b, fl = fit_per_rung(base_extra, SPLIT, h)
    rb_a, _ = fit_per_rung(gateA_extra, SPLIT, h)
    rb_br,_ = fit_per_rung(gateB_extra, SPLIT, h)
    rb_c, _ = fit_per_rung(gateC_extra, SPLIT, h)
    a_b = predict(rb_b, fl, base_extra, test_idx, h)
    a_a = predict(rb_a, fl, gateA_extra, test_idx, h)
    a_r = predict(rb_br, fl, gateB_extra, test_idx, h)
    a_c = predict(rb_c, fl, gateC_extra, test_idx, h)
    print(f"  h={h:>2} mo  {a_b*100:>8.1f}%  {a_a*100:>9.1f}%  {a_r*100:>8.1f}%  {a_c*100:>8.1f}%")
    results[h] = dict(baseline=a_b, phaseA=a_a, roleB=a_r, bothC=a_c)

print(f"\nLifts vs baseline:")
for h in HORIZONS:
    r = results[h]; bd = r['baseline']
    print(f"  h={h:>2} mo  +A {(r['phaseA']-bd)*100:+.1f}  +B {(r['roleB']-bd)*100:+.1f}  +C {(r['bothC']-bd)*100:+.1f}")

out = dict(
    method="243N camshaft gate: valve=1/(1+ARA), phase-gated and role-weighted features",
    rung_ara={int(k): float(v) for k,v in RUNG_ARA.items()},
    valve={int(k): float(v) for k,v in VALVE.items()},
    horizons=HORIZONS, results=results,
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.CAM_GATE = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
