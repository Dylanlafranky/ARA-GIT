"""
River prediction test (Dylan 2026-05-02):

Vertical ARA's practical claim: fast cycle's NOW = slow cycle's NEAR FUTURE
(time-stretched). Like measuring the same river at mountain/foothills/ocean —
different time-positions in the same flow.

Two variants tested on real data:

Test A — within-system vertical translation:
  Compute Hilbert phase of ENSO at each rung. For each rung pair (k_fast, k_slow),
  ask: at what time-offset h does phase[k_fast](t) best correlate with phase[k_slow](t+h)?
  If the optimal h matches the time-stretch (φ^k_slow − φ^k_fast), vertical-ARA prediction works.

Test B — cross-system prediction lift:
  Use SUN (φ¹⁰ Schwabe) NOW as the only feeder for predicting AMO direction at h=120 months.
  Use lunar nodal (φ¹¹) NOW to predict ENSO direction at horizons matching its scale.
  Compare to single-system baselines.

Test C — augment direction prediction with vertical-translation features:
  For each rung k of ENSO, add features that are HILBERT PHASE/AMP of OTHER systems' faster rungs (k-2, k-1).
  See if these "river-translated" features lift direction prediction beyond v2.
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
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\river_prediction_data.js")

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

NINO = nino.reindex(common).values.astype(float)
AMO  = amo.reindex(common).values.astype(float)
TNA  = tna.reindex(common).values.astype(float)
PDO  = pdo.reindex(common).values.astype(float)
IOD  = iod.reindex(common).values.astype(float)
moon_a = moon.reindex(common); OM = moon_a['OM'].values.astype(float)
MOON_OM_S = np.sin(np.deg2rad(OM)); MOON_OM_C = np.cos(np.deg2rad(OM))
SUN = sun.reindex(common).values.astype(float)
DATES = common; N = len(NINO); SPLIT = N//2
print(f"Common: {DATES[0].date()} → {DATES[-1].date()}, n={N}")

def rung_band(arr, period_months, bw=0.2):
    n = len(arr); F = np.fft.rfft(arr - np.mean(arr))
    freqs = np.fft.rfftfreq(n, d=1.0)
    f_c = 1.0/period_months
    F[(freqs<(1-bw)*f_c) | (freqs>(1+bw)*f_c)] = 0
    return np.real(np.fft.irfft(F, n=n))

def hilbert_phase_amp(arr):
    a = hilbert(arr)
    return np.angle(a), np.abs(a)

RUNGS = [(k, PHI**k) for k in range(4, 12)]

# Compute bandpass + Hilbert phase for ENSO at each rung
ENSO_BAND = {k: rung_band(NINO, p) for k,p in RUNGS}
ENSO_PHASE = {k: hilbert_phase_amp(ENSO_BAND[k])[0] for k,_ in RUNGS}
ENSO_AMP   = {k: hilbert_phase_amp(ENSO_BAND[k])[1] for k,_ in RUNGS}

# === TEST A: within-system phase lag — does fast rung lead slow rung? ===
print("\n========= TEST A: within-system vertical phase translation =========")
print("For each rung pair, find offset h (months) maximizing corr(phase_fast(t), phase_slow(t+h))")
print(f"{'pair':>10}  {'period_fast':>12}  {'period_slow':>12}  {'expected h (slow-fast)':>22}  {'best h':>8}  {'best corr':>10}")
test_A_results = []
for i in range(len(RUNGS)-1):
    k_fast, p_fast = RUNGS[i]
    k_slow, p_slow = RUNGS[i+1]
    expected_h = int(round(p_slow - p_fast))
    # use sin/cos of phase to do a circular correlation via real-valued LR
    fast_s = np.sin(ENSO_PHASE[k_fast]); fast_c = np.cos(ENSO_PHASE[k_fast])
    slow_s = np.sin(ENSO_PHASE[k_slow]); slow_c = np.cos(ENSO_PHASE[k_slow])
    best_h = 0; best_corr = -2
    for h in range(0, min(int(p_slow), 100), 1):
        n_use = N - h
        if n_use < 20: break
        # circular phase predictor: phase_slow ≈ phase_fast + offset → cos(phase_slow - phase_fast) high
        delta = ENSO_PHASE[k_slow][h:] - ENSO_PHASE[k_fast][:n_use]
        c = float(np.mean(np.cos(delta)))
        if c > best_corr: best_corr = c; best_h = h
    print(f"  φ{k_fast:>2}→φ{k_slow:>2}  {p_fast:>12.1f}  {p_slow:>12.1f}  {expected_h:>22d}  {best_h:>8d}  {best_corr:>10.3f}")
    test_A_results.append(dict(k_fast=k_fast, k_slow=k_slow, p_fast=p_fast, p_slow=p_slow,
                                 expected_h=expected_h, best_h=best_h, best_phase_corr=best_corr))

# === TEST B: cross-system — use Sun (φ¹⁰ at AMO/PDO scale) to predict AMO direction ===
print("\n========= TEST B: cross-system vertical translation =========")
SUN_BAND = {k: rung_band(SUN, p) for k,p in RUNGS}
AMO_BAND = {k: rung_band(AMO, p) for k,p in RUNGS}

def dir_truth(arr, t, h):
    if t + h >= len(arr): return None
    diff = arr[t + h] - arr[t]
    return 1 if diff > 0 else (-1 if diff < 0 else 0)

# Predict AMO direction at h=120 months using ONLY Sun's φ¹⁰ rung at time t
# (matched-rung translation)
def acc_single_feeder(target_arr, target_band, feeder_band, h, train_max, idx, k_match):
    """Train a tiny per-rung LR: target_k_band[t+h] ~ feeder_k_band[t]. Use only matched rung."""
    rows=[]; ys=[]
    for t in range(train_max - h):
        rows.append([feeder_band[k_match][t], 1.0])
        ys.append(target_band[k_match][t+h])
    X = np.array(rows); y = np.array(ys)
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    correct=0; total=0
    for t in idx:
        true = dir_truth(target_arr, t, h)
        if true is None or true==0: continue
        pred_val_band = b[0]*feeder_band[k_match][t] + b[1]
        # Compare predicted band to current target (sign of change)
        # Need to convert band prediction to direction of total signal
        # Simpler: compare predicted band[t+h] to band[t] sign
        cur_band = target_band[k_match][t]
        pred_dir_band = 1 if pred_val_band > cur_band else -1
        # treat predicted band direction as the prediction direction
        correct += (pred_dir_band == true); total += 1
    return correct/total if total else 0

test_idx = list(range(SPLIT, N))
print("AMO direction at h=120mo using ONLY Sun matched-rung:")
for k,p in RUNGS:
    a = acc_single_feeder(AMO, AMO_BAND, SUN_BAND, 120, SPLIT, test_idx, k)
    print(f"  Sun φ{k} → AMO φ{k} match: {a:.1%}")

# Same for ENSO at h=24 using only solar
print("\nENSO direction at h=24mo using ONLY Sun matched-rung:")
NINO_BAND = ENSO_BAND
for k,p in RUNGS:
    a = acc_single_feeder(NINO, NINO_BAND, SUN_BAND, 24, SPLIT, test_idx, k)
    print(f"  Sun φ{k} → ENSO φ{k} match: {a:.1%}")

# === TEST C: vertical-translation augmentation — add cross-rung features ===
# For target rung k, add HILBERT amp/phase of feeders at rung (k-2) — the "fast cycle now" prediction
print("\n========= TEST C: Vertical translation augmentation =========")
print("Augment per-rung framework with feeders' amp+phase at rung-2 (the 'river fast' translation)")

SYS = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD,
           MOON_OM_S=MOON_OM_S, MOON_OM_C=MOON_OM_C, SUN=SUN)
SYS_BAND = {nm: {k: rung_band(arr, p) for k,p in RUNGS} for nm,arr in SYS.items()}
SYS_HILB = {nm: {k: hilbert_phase_amp(SYS_BAND[nm][k]) for k,_ in RUNGS} for nm in SYS}

def acc_FW(idx, h, train_max, augment=False, ridge=10.0):
    if train_max - h < 20: return None
    rung_betas = {}
    for k,_ in RUNGS:
        rows=[]; ys=[]
        # baseline features per rung
        for t in range(train_max - h):
            feat = [SYS_BAND[nm][k][t] for nm in SYS]
            if augment and k >= 6:
                # add fast-rung phase + amp from k-2
                kfast = k - 2
                for nm in SYS:
                    ph, am = SYS_HILB[nm][kfast]
                    feat.extend([np.sin(ph[t]), np.cos(ph[t]), am[t]])
            feat.append(1.0)
            rows.append(feat); ys.append(SYS_BAND['NINO'][k][t+h])
        X = np.array(rows); y = np.array(ys)
        if ridge > 0:
            n_features = X.shape[1]
            A = X.T @ X + ridge * np.eye(n_features); A[-1,-1] -= ridge
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
            feat = [SYS_BAND[nm][k][t] for nm in SYS]
            if augment and k >= 6:
                kfast = k - 2
                for nm in SYS:
                    ph, am = SYS_HILB[nm][kfast]
                    feat.extend([np.sin(ph[t]), np.cos(ph[t]), am[t]])
            feat.append(1.0)
            s += float(np.dot(b, feat))
        pred = 1 if s>NINO[t] else -1
        correct += (pred==true); total += 1
    return correct/total if total else 0

HORIZONS = [12, 24, 48, 72, 96, 120]
print(f"\n  {'horizon':>10}  {'baseline':>9}  {'+vert_aug':>10}  {'delta':>7}")
test_C = {}
for h in HORIZONS:
    a_base = acc_FW(test_idx, h, SPLIT, augment=False, ridge=10.0)
    a_aug  = acc_FW(test_idx, h, SPLIT, augment=True, ridge=10.0)
    delta = a_aug - a_base
    flag = ' ★' if delta > 0.02 else ('  ' if abs(delta) <= 0.02 else ' ↓')
    print(f"  h={h:>3} mo  {a_base:>9.1%}  {a_aug:>10.1%}  {delta:+.3f}{flag}")
    test_C[h] = dict(baseline=a_base, augmented=a_aug, delta=delta)

out = dict(
    test_A=test_A_results,
    test_C=test_C,
    sources="NOAA + JPL Horizons + SILSO, all real",
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.RIVER = " + json.dumps(out) + ";\n")
print(f"\nSaved -> {OUT}")
