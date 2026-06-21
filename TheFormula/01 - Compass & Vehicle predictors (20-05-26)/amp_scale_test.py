"""
amp_scale test (resurrecting 243AJ concept).

Original formula:
  midline    = 1 + acc_frac × (ARA - 1)         [where wave centers]
  amp_scale  = 1 + snap_frac × (ARA - 1) × φ   [how far wave swings]
  acc_frac   = 1 / (1 + ARA)
  snap_frac  = ARA / (1 + ARA)

For Solar (ARA = φ):
  acc_frac  = 0.382, snap_frac = 0.618
  midline   = 1 + 0.382 × 0.618 = 1.236
  amp_scale = 1 + 0.618 × 0.618 × 1.618 = 1.618 = φ
  midline × amp_scale = 1.236 × 1.618 = 2.0 (perfect framework symmetry)

For Clock (ARA = 1):  midline = 1.0, amp_scale = 1.0
For Snap (ARA = 2):   midline = 1.333, amp_scale = 2.0+

Test on ENSO direction prediction:
  1. Compute per-cycle ARA from trough position
  2. Compute amp_scale per cycle
  3. Use amp_scale as additional feature OR as rescaling factor
  4. Compare to baseline (86% at h=24mo)

Hypothesis: amp_scale gives the framework structural amplitude information
that the bandpass-only approach misses. Could close the trough-undershoot gap.
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
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\amp_scale_data.js")

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

# === Per-cycle ARA + amp_scale computation ===
def cycle_based_amp_scale(arr, target_period, dt=1.0):
    """For each peak-to-peak cycle:
       1. ARA = (1 - f_trough) / f_trough
       2. acc_frac = 1/(1+ARA), snap_frac = ARA/(1+ARA)
       3. midline = 1 + acc_frac × (ARA - 1)
       4. amp_scale = 1 + snap_frac × (ARA - 1) × φ
       Return both as per-time-step arrays (constant within each cycle)."""
    smooth_sigma = max(1, int(target_period * 0.15 / dt))
    smoothed = gaussian_filter1d(arr - np.mean(arr), smooth_sigma)
    min_dist = int(target_period * 0.7 / dt)
    peaks, _ = find_peaks(smoothed, distance=min_dist)
    n = len(arr)
    ara_arr = np.full(n, 1.0)
    midline_arr = np.full(n, 1.0)
    amp_scale_arr = np.full(n, 1.0)
    for i in range(len(peaks)-1):
        seg = arr[peaks[i]:peaks[i+1]]
        if len(seg) < 4: continue
        trough_pos = int(np.argmin(seg))
        f_trough = trough_pos / max(1, len(seg)-1)
        f_trough = max(0.05, min(0.95, f_trough))
        ara = (1 - f_trough) / f_trough
        acc = 1.0/(1.0 + ara)
        snap = ara/(1.0 + ara)
        midline = 1.0 + acc * (ara - 1.0)
        amp_scale = 1.0 + snap * (ara - 1.0) * PHI
        ara_arr[peaks[i]:peaks[i+1]] = ara
        midline_arr[peaks[i]:peaks[i+1]] = midline
        amp_scale_arr[peaks[i]:peaks[i+1]] = amp_scale
    return ara_arr, midline_arr, amp_scale_arr

# Compute amp_scale at multiple rungs for ENSO
RUNGS = [(k, PHI**k) for k in range(4, 14)]
print(f"Computing per-rung amp_scale for ENSO...")
NINO_amp_scales = {}  # by rung
for k, p in RUNGS:
    ara_arr, midline_arr, amp_arr = cycle_based_amp_scale(NINO, p)
    NINO_amp_scales[k] = dict(ara=ara_arr, midline=midline_arr, amp_scale=amp_arr)
    print(f"  k={k:>2} (T={p:>5.1f}mo): mean ARA={np.mean(ara_arr):.3f}, mean amp_scale={np.mean(amp_arr):.3f}, range=[{np.min(amp_arr):.2f}, {np.max(amp_arr):.2f}]")

# === Direction prediction with amp_scale as per-rung feature ===
SYS = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD,
           MOON_OM_S=MOON_OM_S, MOON_OM_C=MOON_OM_C, MOON_EC=MOON_EC)
R = {nm: {k: bandpass(arr, p) for k,p in RUNGS} for nm,arr in SYS.items()}

def dir_truth(arr, t, h):
    if t + h >= len(arr): return None
    diff = arr[t + h] - arr[t]
    return 1 if diff > 0 else (-1 if diff < 0 else 0)

def acc_FW(idx, h, train_max, FEEDERS, R, extra_feature_per_rung=None, ridge=10.0):
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

FEEDERS = list(SYS.keys())
HORIZONS = [12, 24, 36, 48]
test_idx = list(range(SPLIT, N))

# Build feature dict: at rung k, the amp_scale at that rung
amp_scale_features = {k: NINO_amp_scales[k]['amp_scale'] for k,_ in RUNGS}
midline_features = {k: NINO_amp_scales[k]['midline'] for k,_ in RUNGS}
ara_features = {k: NINO_amp_scales[k]['ara'] for k,_ in RUNGS}

print(f"\n========= AMP_SCALE TEST RESULTS =========")
print(f"{'horizon':>10}  {'baseline':>9}  {'+amp_scale':>11}  {'+midline':>10}  {'+ara':>7}  {'+all 3':>8}")
results = {}
for h in HORIZONS:
    a_base = acc_FW(test_idx, h, SPLIT, FEEDERS, R, extra_feature_per_rung=None)
    a_amp = acc_FW(test_idx, h, SPLIT, FEEDERS, R, extra_feature_per_rung=amp_scale_features)
    a_mid = acc_FW(test_idx, h, SPLIT, FEEDERS, R, extra_feature_per_rung=midline_features)
    a_ara = acc_FW(test_idx, h, SPLIT, FEEDERS, R, extra_feature_per_rung=ara_features)

    # All three: include amp_scale + midline + ara at each rung
    def acc_FW_three(idx, h, train_max, ridge=10.0):
        if train_max - h < 20: return None
        rung_betas = {}
        for k,_ in RUNGS:
            rows=[]; ys=[]
            for t in range(train_max - h):
                feat = [R[nm][k][t] for nm in FEEDERS]
                feat.append(amp_scale_features[k][t])
                feat.append(midline_features[k][t])
                feat.append(ara_features[k][t])
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
                feat.append(amp_scale_features[k][t])
                feat.append(midline_features[k][t])
                feat.append(ara_features[k][t])
                feat.append(1.0)
                s += float(np.dot(b, feat))
            pred = 1 if s>NINO[t] else -1
            correct += (pred==true); total += 1
        return correct/total if total else 0
    a_three = acc_FW_three(test_idx, h, SPLIT)

    print(f"  h={h:>2} mo  {a_base*100:>8.1f}%  {a_amp*100:>10.1f}%  {a_mid*100:>9.1f}%  {a_ara*100:>6.1f}%  {a_three*100:>7.1f}%")
    results[h] = dict(baseline=a_base, with_amp_scale=a_amp, with_midline=a_mid,
                      with_ara=a_ara, with_all_three=a_three)

# Show deltas
print(f"\nLifts vs baseline:")
for h in HORIZONS:
    r = results[h]
    bd = r['baseline']
    print(f"  h={h:>2} mo  amp_scale {(r['with_amp_scale']-bd)*100:+.1f}  midline {(r['with_midline']-bd)*100:+.1f}  ara {(r['with_ara']-bd)*100:+.1f}  all3 {(r['with_all_three']-bd)*100:+.1f}")

out = dict(
    sources="Same as direction_prediction_v2",
    horizons=HORIZONS,
    formula="amp_scale = 1 + snap_frac × (ARA - 1) × φ",
    nino_amp_scale_stats={
        str(k): dict(
            mean_ara=float(np.mean(NINO_amp_scales[k]['ara'])),
            mean_amp_scale=float(np.mean(NINO_amp_scales[k]['amp_scale'])),
            mean_midline=float(np.mean(NINO_amp_scales[k]['midline'])),
        ) for k,_ in RUNGS
    },
    results=results,
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.AMP_SCALE = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
