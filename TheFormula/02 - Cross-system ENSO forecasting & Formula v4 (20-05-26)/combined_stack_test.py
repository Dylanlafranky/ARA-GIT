"""
Combined stack test — stack ALL positive-effect concepts together.

Layer 1 (per-rung): for each rung k, regress R['NINO'][k][t+h] on:
  - 8 base feeders bandpassed at rung k
  - 8 camshaft phase-gated feeders (var A from camshaft_gate_test)
  - 1 diamond main_valve modulator
  - 1 horizontal mirror synthetic
  - 1 amp_scale-multiplied NINO at rung k
  - 1 gate-inertia lag feature
  - 1 reverse-gate adjacent-rung feature

Layer 2 (global): predict NINO[t+h] - mean from:
  - per-rung sum over Layer 1 predictions
  - 8 CF v2 partner-bandpassed features
  - 9 φ⁹ atom channels × 3 features (env, cos, sin) = 27

Compare to baseline (per-rung only, no extras).
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
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\combined_stack_data.js")

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
N = len(NINO); SPLIT = N//2

def detrend_linear(arr):
    x = np.arange(len(arr))
    p = np.polyfit(x, arr, 1)
    return arr - np.polyval(p, x)

def bandpass(arr, period_units, dt=1.0, bw=0.4):
    n = len(arr); F = np.fft.rfft(arr - np.mean(arr))
    freqs = np.fft.rfftfreq(n, d=dt)
    f_c = 1.0/period_units
    F[(freqs<(1-bw)*f_c) | (freqs>(1+bw)*f_c)] = 0
    return np.real(np.fft.irfft(F, n=n))

def per_rung_ARA(raw_signal, period):
    n = len(raw_signal); F = np.fft.rfft(raw_signal - np.mean(raw_signal))
    freqs = np.fft.rfftfreq(n, d=1.0)
    f_c = 1.0/period; bw = 0.85
    F[(freqs<(1-bw)*f_c) | (freqs>(1+bw)*f_c)] = 0
    wide = np.real(np.fft.irfft(F, n=n))
    smoothed = gaussian_filter1d(wide, max(1, int(period * 0.05)))
    peaks, _ = find_peaks(smoothed, distance=max(2, int(period * 0.7)))
    if len(peaks) < 2: return 1.0
    aras = []
    for i in range(len(peaks)-1):
        seg = smoothed[peaks[i]:peaks[i+1]+1]
        if len(seg) < 3: continue
        f_t = max(0.15, min(0.85, int(np.argmin(seg)) / max(1, len(seg)-1)))
        aras.append((1 - f_t) / f_t)
    if not aras: return 1.0
    return float(np.mean(np.clip(aras, 0.3, 3.0)))

# ===== Per-rung bandpasses =====
RUNGS = [(k, PHI**k) for k in range(4, 14)]
SYS = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD,
           MOON_OM_S=MOON_OM_S, MOON_OM_C=MOON_OM_C, MOON_EC=MOON_EC)
R = {nm: {k: bandpass(arr, p) for k,p in RUNGS} for nm,arr in SYS.items()}

# Per-rung ARA + valve
RUNG_ARA = {k: per_rung_ARA(NINO[:SPLIT], p) for k,p in RUNGS}
VALVE = {k: 1.0/(1.0 + RUNG_ARA[k]) for k,_ in RUNGS}

# Hilbert phase
NINO_CP = {}
for k,_ in RUNGS:
    a = hilbert(R['NINO'][k]); NINO_CP[k] = (np.angle(a) + np.pi)/(2*np.pi)

# Phase gate (smooth tanh)
GATE = {k: -np.tanh(20.0*(NINO_CP[k]-VALVE[k])) for k,_ in RUNGS}

# Amp_scale per rung from cycle ARA
def amp_scale(ARA):
    # 243AJ: scale = 1 + 0.5*(ARA-1) bounded
    return 1.0 + 0.5*(np.clip(ARA, 0.3, 3.0) - 1.0)
AMP_SCALE = {k: amp_scale(RUNG_ARA[k]) for k,_ in RUNGS}

# Diamond valves per rung
DIAMOND_MAIN = {k: 1.0/(1.0+RUNG_ARA[k]) for k,_ in RUNGS}
DIAMOND_REV  = {k: RUNG_ARA[k]/(1.0+RUNG_ARA[k]) for k,_ in RUNGS}

# Horizontal mirror synthetic
HMIRROR = {k: -R['NINO'][k] * (2.0 - RUNG_ARA[k]) / max(0.2, RUNG_ARA[k]) for k,_ in RUNGS}

# Gate inertia: lagged ENSO bandpass at rung k by 1/4 period (smoothed)
GATE_INERT = {}
for k,p in RUNGS:
    lag = max(1, int(p/4))
    arr = R['NINO'][k]
    GATE_INERT[k] = np.concatenate([np.zeros(lag), arr[:-lag]])

# Reverse-gate adjacent rung product (k & k+1)
RGATE = {}
for k,_ in RUNGS:
    if k+1 < 14:
        RGATE[k] = R['NINO'][k] * R['NINO'][k+1]
    else:
        RGATE[k] = np.zeros(N)

# ===== CF v2 partner features =====
ENSO_PERIOD = PHI**8
partners = {
    'P1': ENSO_PERIOD, 'P2': ENSO_PERIOD*PHI, 'P3': ENSO_PERIOD/PHI,
    'P4': ENSO_PERIOD*PHI**2, 'P5': ENSO_PERIOD/PHI**2, 'P6': ENSO_PERIOD*PHI**4,
}
def variance_match_partner(arr):
    arr_dt = detrend_linear(arr)
    best_p = 'P1'; best_v = -1
    for pn, per in partners.items():
        v = float(np.var(bandpass(arr_dt, per)))
        if v > best_v: best_v = v; best_p = pn
    return best_p

CF_FEAT = {}
for nm, arr in [('AMO',AMO),('TNA',TNA),('PDO',PDO),('IOD',IOD),
                ('MOON_OM_S',MOON_OM_S),('MOON_OM_C',MOON_OM_C),('MOON_EC',MOON_EC)]:
    pn = variance_match_partner(arr)
    CF_FEAT[nm] = bandpass(detrend_linear(arr), partners[pn])
CF_FEAT['NINO_self'] = bandpass(detrend_linear(NINO), ENSO_PERIOD)

# ===== φ⁹ atom features (3 systems × 3 rungs × 3 channels = 27) =====
ATOM_RUNGS = [PHI**7, PHI**8, PHI**9]
ATOM_SYS = [('NINO', NINO), ('PDO', PDO), ('IOD', IOD)]
ATOM_FEAT = {}
for nm, arr in ATOM_SYS:
    for ai, p in enumerate(ATOM_RUNGS):
        bp = bandpass(arr, p)
        a = hilbert(bp)
        env = np.abs(a)
        ph = np.angle(a)
        ATOM_FEAT[f'{nm}_r{ai}_env'] = env
        ATOM_FEAT[f'{nm}_r{ai}_cos'] = np.cos(ph)
        ATOM_FEAT[f'{nm}_r{ai}_sin'] = np.sin(ph)

# ===== Direction prediction =====
def dir_truth(arr, t, h):
    if t + h >= len(arr): return None
    diff = arr[t + h] - arr[t]
    return 1 if diff > 0 else (-1 if diff < 0 else 0)

FEEDERS = list(SYS.keys())

def per_rung_features(t, k, mode='base'):
    """mode: 'base' or 'full' (includes all per-rung extras)."""
    feat = [R[nm][k][t] for nm in FEEDERS]
    if mode == 'full':
        # Camshaft phase-gate × each feeder
        g = GATE[k][t]
        feat += [R[nm][k][t] * g for nm in FEEDERS]
        # Amp_scale × NINO (single)
        feat.append(R['NINO'][k][t] * AMP_SCALE[k])
        # Diamond valves × NINO
        feat.append(R['NINO'][k][t] * DIAMOND_MAIN[k])
        feat.append(R['NINO'][k][t] * DIAMOND_REV[k])
        # Horizontal mirror
        feat.append(HMIRROR[k][t])
        # Gate inertia
        feat.append(GATE_INERT[k][t])
        # Reverse-gate adjacent
        feat.append(RGATE[k][t])
    return feat

def fit_layer1(mode, train_max, h, ridge=10.0):
    rung_betas = {}
    for k,_ in RUNGS:
        rows=[]; ys=[]
        for t in range(train_max - h):
            feat = per_rung_features(t, k, mode)
            feat.append(1.0)
            rows.append(feat); ys.append(R['NINO'][k][t+h])
        X = np.array(rows); y = np.array(ys)
        nf = X.shape[1]
        A = X.T @ X + ridge*np.eye(nf); A[-1,-1] -= ridge
        b = np.linalg.solve(A, X.T @ y)
        rung_betas[k] = b
    return rung_betas

def per_rung_predict(rung_betas, t, mode):
    s = 0.0
    for k,_ in RUNGS:
        feat = per_rung_features(t, k, mode); feat.append(1.0)
        s += float(np.dot(rung_betas[k], feat))
    return s

def fit_layer2(rung_betas, mode, train_max, h, include_cf, include_atom, ridge=20.0):
    """Layer 2 combiner: per-rung sum + global features → NINO[t+h] - mean_train."""
    mean_n = float(np.mean(NINO[:train_max]))
    rows=[]; ys=[]
    for t in range(train_max - h):
        feat = [per_rung_predict(rung_betas, t, mode)]
        if include_cf:
            for nm in CF_FEAT: feat.append(CF_FEAT[nm][t])
        if include_atom:
            for nm in ATOM_FEAT: feat.append(ATOM_FEAT[nm][t])
        feat.append(1.0)
        rows.append(feat); ys.append(NINO[t+h] - mean_n)
    X = np.array(rows); y = np.array(ys)
    nf = X.shape[1]
    A = X.T @ X + ridge*np.eye(nf); A[-1,-1] -= ridge
    b = np.linalg.solve(A, X.T @ y)
    return b, mean_n

def predict_full(rung_betas, b2, mean_n, mode, idx, h, include_cf, include_atom):
    correct=0; total=0
    for t in idx:
        true = dir_truth(NINO, t, h)
        if true is None or true==0: continue
        feat = [per_rung_predict(rung_betas, t, mode)]
        if include_cf:
            for nm in CF_FEAT: feat.append(CF_FEAT[nm][t])
        if include_atom:
            for nm in ATOM_FEAT: feat.append(ATOM_FEAT[nm][t])
        feat.append(1.0)
        pred_val = mean_n + float(np.dot(b2, feat))
        pred = 1 if pred_val > NINO[t] else -1
        correct += (pred==true); total += 1
    return correct/total if total else 0

HORIZONS = [12, 24, 36, 48]
test_idx = list(range(SPLIT, N))

print("\n========= COMBINED STACK RESULTS =========")
print(f"{'horizon':>8}  {'baseline':>9}  {'L1 full':>9}  {'+CF':>7}  {'+atom':>7}  {'+all':>7}")
results = {}
for h in HORIZONS:
    # Baseline: per-rung base only (no Layer 2 — direct rung sum vs NINO[t])
    rb_base = fit_layer1('base', SPLIT, h, ridge=10.0)
    correct=0; total=0
    mean_n = float(np.mean(NINO[:SPLIT]))
    for t in test_idx:
        true = dir_truth(NINO, t, h)
        if true is None or true==0: continue
        s = mean_n + per_rung_predict(rb_base, t, 'base') - mean_n  # rung_betas absorb mean
        # wait actually layer1 fits R['NINO'][k][t+h] — bandpass target, not raw NINO
        # so per_rung_predict is already the bandpass sum prediction
        # baseline original used NINO[t] threshold
        s = mean_n + per_rung_predict(rb_base, t, 'base')
        pred = 1 if s > NINO[t] else -1
        correct += (pred==true); total += 1
    a_base = correct/total if total else 0

    # L1 full: per-rung with all extras, no Layer 2
    rb_full = fit_layer1('full', SPLIT, h, ridge=10.0)
    correct=0; total=0
    for t in test_idx:
        true = dir_truth(NINO, t, h)
        if true is None or true==0: continue
        s = mean_n + per_rung_predict(rb_full, t, 'full')
        pred = 1 if s > NINO[t] else -1
        correct += (pred==true); total += 1
    a_l1 = correct/total if total else 0

    # L1 full + CF (Layer 2 with CF only)
    b2, mn = fit_layer2(rb_full, 'full', SPLIT, h, include_cf=True, include_atom=False)
    a_cf = predict_full(rb_full, b2, mn, 'full', test_idx, h, True, False)

    # L1 full + atom
    b2, mn = fit_layer2(rb_full, 'full', SPLIT, h, include_cf=False, include_atom=True)
    a_atom = predict_full(rb_full, b2, mn, 'full', test_idx, h, False, True)

    # L1 full + CF + atom
    b2, mn = fit_layer2(rb_full, 'full', SPLIT, h, include_cf=True, include_atom=True)
    a_all = predict_full(rb_full, b2, mn, 'full', test_idx, h, True, True)

    print(f"  h={h:>2} mo  {a_base*100:>8.1f}%  {a_l1*100:>8.1f}%  {a_cf*100:>6.1f}%  {a_atom*100:>6.1f}%  {a_all*100:>6.1f}%")
    results[h] = dict(baseline=a_base, l1_full=a_l1, plus_cf=a_cf, plus_atom=a_atom, all=a_all)

print(f"\nLifts vs baseline:")
for h in HORIZONS:
    r = results[h]; bd = r['baseline']
    print(f"  h={h:>2} mo  L1 {(r['l1_full']-bd)*100:+.1f}  +CF {(r['plus_cf']-bd)*100:+.1f}  +atom {(r['plus_atom']-bd)*100:+.1f}  +all {(r['all']-bd)*100:+.1f}")

out = dict(method="combined stack: per-rung extras + global CF + φ⁹ atom",
           horizons=HORIZONS, results=results)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.COMBINED = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
