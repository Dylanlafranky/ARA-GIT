"""
242b horizontal map test — mirror partner = 2 - ARA_self.

For each φ-rung k:
  1. Bandpass NINO at PHI^k.
  2. Measure ARA_self at rung k from cycle trough asymmetry.
  3. Mirror target ARA at rung k = 2 - ARA_self_k.

Two variants:
  A. SYNTHETIC mirror — anti-phase signal scaled by mirror strength factor:
       mirror_k(t) = -bp_NINO_k(t) * (mirror_strength_k)
     where mirror_strength_k = (2 - ARA_self_k) / max(ARA_self_k, 0.1)
     Add as one feature per rung on top of baseline.

  B. MATCHED-feeder — at each rung, pick the feeder whose ARA at that rung
     is closest to the mirror target. Use only matched partners as features.

Compare to baseline (per-rung regression with all feeders at all rungs).

DATA: real NOAA Niño 3.4, AMO, TNA, PDO, IOD + JPL Moon.
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
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\horizontal_map_data.js")

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
    """Measure asymmetric ARA from the original signal at this period scale.
    Use wider bandpass (bw=0.8) to keep cycle asymmetry intact, then segment
    peak-to-peak and compute ARA = (1-f_trough)/f_trough per cycle.
    >1 = engine (slow rise / fast fall), <1 = consumer (fast rise / slow fall)."""
    # Wide bandpass keeps harmonics so cycle shape survives
    n = len(raw_signal); F = np.fft.rfft(raw_signal - np.mean(raw_signal))
    freqs = np.fft.rfftfreq(n, d=1.0)
    f_c = 1.0/period
    bw = 0.85
    F[(freqs<(1-bw)*f_c) | (freqs>(1+bw)*f_c)] = 0
    wide = np.real(np.fft.irfft(F, n=n))
    # Light smoothing only
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

# === Build per-rung bandpasses ===
RUNGS = [(k, PHI**k) for k in range(4, 14)]
SYS = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD,
           MOON_OM_S=MOON_OM_S, MOON_OM_C=MOON_OM_C, MOON_EC=MOON_EC)
R = {nm: {k: bandpass(arr, p) for k,p in RUNGS} for nm,arr in SYS.items()}

# Measure per-rung ARA for ENSO and each feeder using TRAINING DATA only
print("\n=== Per-rung ARA measurements (training half) ===")
rung_ara = {}
for k, p in RUNGS:
    row = {}
    for nm in SYS:
        # Use raw signal at training half — wide bandpass inside per_rung_ARA
        row[nm] = per_rung_ARA(SYS[nm][:SPLIT], p)
    rung_ara[k] = row
    mirror_target = 2.0 - row['NINO']
    print(f"  k={k:>2} P={p:>6.1f}mo  NINO_ARA={row['NINO']:.2f}  mirror={mirror_target:.2f}  "
          f"AMO={row['AMO']:.2f} TNA={row['TNA']:.2f} PDO={row['PDO']:.2f} IOD={row['IOD']:.2f}")

# ========================================
# Variant A: SYNTHETIC mirror per rung
# ========================================
print("\n=== Variant A: synthetic anti-phase mirror per rung ===")
synth_mirror = {}
for k, p in RUNGS:
    ara_self = max(0.2, rung_ara[k]['NINO'])
    mirror_strength = (2.0 - rung_ara[k]['NINO']) / ara_self  # could be negative if ARA>2
    synth_mirror[k] = -R['NINO'][k] * mirror_strength

# ========================================
# Variant B: MATCHED-feeder per rung
# ========================================
print("\n=== Variant B: feeder matched to mirror target per rung ===")
matched_feeder = {}
for k, p in RUNGS:
    mirror_target = 2.0 - rung_ara[k]['NINO']
    best_nm = None; best_diff = 1e9
    for nm in ['AMO','TNA','PDO','IOD','MOON_OM_S','MOON_OM_C','MOON_EC']:
        diff = abs(rung_ara[k][nm] - mirror_target)
        if diff < best_diff:
            best_diff = diff; best_nm = nm
    matched_feeder[k] = best_nm
    print(f"  k={k:>2} mirror_tgt={mirror_target:.2f}  best={best_nm} (ARA={rung_ara[k][best_nm]:.2f}, diff={best_diff:.2f})")

# ========================================
# Direction prediction
# ========================================
def dir_truth(arr, t, h):
    if t + h >= len(arr): return None
    diff = arr[t + h] - arr[t]
    return 1 if diff > 0 else (-1 if diff < 0 else 0)

def fit_per_rung(extra_feature_fn, train_max, h, ridge=10.0):
    """extra_feature_fn(t, k) -> list of extra scalar features for rung k at time t."""
    rung_betas = {}
    feeders_list = list(SYS.keys())
    for k,_ in RUNGS:
        rows=[]; ys=[]
        for t in range(train_max - h):
            feat = [R[nm][k][t] for nm in feeders_list]
            feat += extra_feature_fn(t, k)
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
            feat += extra_feature_fn(t, k)
            feat.append(1.0)
            s += float(np.dot(b, feat))
        pred = 1 if s > NINO[t] else -1
        correct += (pred==true); total += 1
    return correct/total if total else 0

# Baseline (no extra features)
def base_extra(t, k): return []

# Variant A: add synthetic mirror as 1 extra feature per rung
def synth_extra(t, k): return [synth_mirror[k][t]]

# Variant B: add matched-feeder signal as 1 extra feature per rung
def matched_extra(t, k):
    nm = matched_feeder[k]
    return [R[nm][k][t]]

# Variant A+B: both
def both_extra(t, k):
    nm = matched_feeder[k]
    return [synth_mirror[k][t], R[nm][k][t]]

HORIZONS = [12, 24, 36, 48]
test_idx = list(range(SPLIT, N))

print(f"\n========= HORIZONTAL MAP RESULTS =========")
print(f"{'horizon':>10}  {'baseline':>9}  {'+synth(A)':>10}  {'+matched(B)':>12}  {'+both':>9}")
results = {}
for h in HORIZONS:
    rb_base, fl = fit_per_rung(base_extra, SPLIT, h)
    rb_a, _ = fit_per_rung(synth_extra, SPLIT, h)
    rb_b, _ = fit_per_rung(matched_extra, SPLIT, h)
    rb_ab,_ = fit_per_rung(both_extra, SPLIT, h)
    a_base = predict(rb_base, fl, base_extra, test_idx, h)
    a_a   = predict(rb_a, fl, synth_extra, test_idx, h)
    a_b   = predict(rb_b, fl, matched_extra, test_idx, h)
    a_ab  = predict(rb_ab, fl, both_extra, test_idx, h)
    print(f"  h={h:>2} mo  {a_base*100:>8.1f}%  {a_a*100:>9.1f}%  {a_b*100:>11.1f}%  {a_ab*100:>8.1f}%")
    results[h] = dict(baseline=a_base, synth=a_a, matched=a_b, both=a_ab)

print(f"\nLifts vs baseline:")
for h in HORIZONS:
    r = results[h]; bd = r['baseline']
    print(f"  h={h:>2} mo  +synth {(r['synth']-bd)*100:+.1f}  +matched {(r['matched']-bd)*100:+.1f}  +both {(r['both']-bd)*100:+.1f}")

out = dict(
    method="242b horizontal map: mirror_ARA = 2 - ARA_self per rung",
    rung_ara={int(k): {nm: float(v) for nm,v in row.items()} for k,row in rung_ara.items()},
    matched_feeder={int(k): v for k,v in matched_feeder.items()},
    horizons=HORIZONS,
    results=results,
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.HORIZ_MAP = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
