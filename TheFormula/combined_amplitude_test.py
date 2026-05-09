"""
Combined amplitude test — combined stack + φ^k amplitude scaling.

Goal: measure not just direction (sign) but actual magnitude of NINO[t+h].
Apply the φ^k amplitude scaling rule from ECG (amp_rung_k = base × φ^(k-k_ref))
to constrain per-rung amplitudes.

Three modes:
  V1 — combined stack as-is, measure magnitude (corr, MAE, R²)
  V2 — combined stack + φ^k amplitude scaling on Layer 1 (constrain rung amps)
  V3 — V2 + φ^k amplitude scaling on the final output (sanity rescale)

Compare to:
  - Baseline (per-rung framework regression, no extras)
  - Persistence (predict NINO[t+h] = NINO[t])
  - Climatology (predict mean)
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
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\combined_amplitude_data.js")

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
    freqs = np.fft.rfftfreq(n, d=1.0); f_c = 1.0/period; bw = 0.85
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

# ===== Build features (same as combined_stack_test) =====
RUNGS = [(k, PHI**k) for k in range(4, 14)]
K_REF = 8  # ENSO home rung
SYS = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD,
           MOON_OM_S=MOON_OM_S, MOON_OM_C=MOON_OM_C, MOON_EC=MOON_EC)
R = {nm: {k: bandpass(arr, p) for k,p in RUNGS} for nm,arr in SYS.items()}
RUNG_ARA = {k: per_rung_ARA(NINO[:SPLIT], p) for k,p in RUNGS}
VALVE = {k: 1.0/(1.0 + RUNG_ARA[k]) for k,_ in RUNGS}
NINO_CP = {}
for k,_ in RUNGS:
    a = hilbert(R['NINO'][k]); NINO_CP[k] = (np.angle(a) + np.pi)/(2*np.pi)
GATE = {k: -np.tanh(20.0*(NINO_CP[k]-VALVE[k])) for k,_ in RUNGS}
def amp_scale(ARA): return 1.0 + 0.5*(np.clip(ARA, 0.3, 3.0) - 1.0)
AMP_SCALE = {k: amp_scale(RUNG_ARA[k]) for k,_ in RUNGS}
DIAMOND_MAIN = {k: 1.0/(1.0+RUNG_ARA[k]) for k,_ in RUNGS}
DIAMOND_REV  = {k: RUNG_ARA[k]/(1.0+RUNG_ARA[k]) for k,_ in RUNGS}
HMIRROR = {k: -R['NINO'][k] * (2.0 - RUNG_ARA[k]) / max(0.2, RUNG_ARA[k]) for k,_ in RUNGS}
GATE_INERT = {}
for k,p in RUNGS:
    lag = max(1, int(p/4)); GATE_INERT[k] = np.concatenate([np.zeros(lag), R['NINO'][k][:-lag]])
RGATE = {}
for k,_ in RUNGS:
    if k+1 < 14: RGATE[k] = R['NINO'][k] * R['NINO'][k+1]
    else: RGATE[k] = np.zeros(N)

# CF v2
ENSO_PERIOD = PHI**8
partners = {'P1':ENSO_PERIOD,'P2':ENSO_PERIOD*PHI,'P3':ENSO_PERIOD/PHI,
            'P4':ENSO_PERIOD*PHI**2,'P5':ENSO_PERIOD/PHI**2,'P6':ENSO_PERIOD*PHI**4}
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

# φ⁹ atom
ATOM_RUNGS = [PHI**7, PHI**8, PHI**9]
ATOM_SYS = [('NINO', NINO), ('PDO', PDO), ('IOD', IOD)]
ATOM_FEAT = {}
for nm, arr in ATOM_SYS:
    for ai, p in enumerate(ATOM_RUNGS):
        bp = bandpass(arr, p); a = hilbert(bp)
        ATOM_FEAT[f'{nm}_r{ai}_env'] = np.abs(a)
        ATOM_FEAT[f'{nm}_r{ai}_cos'] = np.cos(np.angle(a))
        ATOM_FEAT[f'{nm}_r{ai}_sin'] = np.sin(np.angle(a))

FEEDERS = list(SYS.keys())

def per_rung_features_full(t, k):
    feat = [R[nm][k][t] for nm in FEEDERS]
    g = GATE[k][t]
    feat += [R[nm][k][t] * g for nm in FEEDERS]
    feat.append(R['NINO'][k][t] * AMP_SCALE[k])
    feat.append(R['NINO'][k][t] * DIAMOND_MAIN[k])
    feat.append(R['NINO'][k][t] * DIAMOND_REV[k])
    feat.append(HMIRROR[k][t])
    feat.append(GATE_INERT[k][t])
    feat.append(RGATE[k][t])
    return feat

def fit_layer1(train_max, h, ridge=10.0, phi_k_constraint=False):
    """If phi_k_constraint: scale each rung's features by φ^(k-K_REF) before fit
    so the regression sees a normalised magnitude across rungs. The β still
    absorbs the optimal weight, but feature scale is now consistent."""
    rung_betas = {}
    for k,_ in RUNGS:
        scale = PHI**(k - K_REF) if phi_k_constraint else 1.0
        rows=[]; ys=[]
        for t in range(train_max - h):
            feat = per_rung_features_full(t, k)
            if phi_k_constraint:
                feat = [v / scale for v in feat]
            feat.append(1.0)
            rows.append(feat); ys.append(R['NINO'][k][t+h] / scale)
        X = np.array(rows); y = np.array(ys)
        nf = X.shape[1]
        A = X.T @ X + ridge*np.eye(nf); A[-1,-1] -= ridge
        b = np.linalg.solve(A, X.T @ y)
        rung_betas[k] = b
    return rung_betas

def per_rung_predict(rung_betas, t, phi_k_constraint=False):
    s = 0.0
    for k,_ in RUNGS:
        scale = PHI**(k - K_REF) if phi_k_constraint else 1.0
        feat = per_rung_features_full(t, k)
        if phi_k_constraint:
            feat = [v / scale for v in feat]
        feat.append(1.0)
        # Output scaled back up by φ^k for amplitude scaling
        s += scale * float(np.dot(rung_betas[k], feat))
    return s

def fit_layer2(rung_betas, train_max, h, phi_k_constraint, ridge=20.0):
    mean_n = float(np.mean(NINO[:train_max]))
    rows=[]; ys=[]
    for t in range(train_max - h):
        feat = [per_rung_predict(rung_betas, t, phi_k_constraint)]
        for nm in CF_FEAT: feat.append(CF_FEAT[nm][t])
        for nm in ATOM_FEAT: feat.append(ATOM_FEAT[nm][t])
        feat.append(1.0)
        rows.append(feat); ys.append(NINO[t+h] - mean_n)
    X = np.array(rows); y = np.array(ys)
    nf = X.shape[1]
    A = X.T @ X + ridge*np.eye(nf); A[-1,-1] -= ridge
    b = np.linalg.solve(A, X.T @ y)
    return b, mean_n

def predict_continuous(rung_betas, b2, mean_n, idx, h, phi_k_constraint):
    """Return arrays of (predicted, actual) values for magnitude assessment."""
    preds=[]; truths=[]
    for t in idx:
        if t + h >= N: continue
        feat = [per_rung_predict(rung_betas, t, phi_k_constraint)]
        for nm in CF_FEAT: feat.append(CF_FEAT[nm][t])
        for nm in ATOM_FEAT: feat.append(ATOM_FEAT[nm][t])
        feat.append(1.0)
        pred_val = mean_n + float(np.dot(b2, feat))
        preds.append(pred_val); truths.append(NINO[t+h])
    return np.array(preds), np.array(truths)

def metrics(preds, truths, baseline_for_R2):
    err = preds - truths
    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err**2)))
    if np.std(preds) > 1e-9 and np.std(truths) > 1e-9:
        corr = float(np.corrcoef(preds, truths)[0,1])
    else: corr = 0.0
    ss_res = np.sum((truths - preds)**2)
    ss_tot = np.sum((truths - baseline_for_R2)**2)
    r2 = float(1 - ss_res/ss_tot) if ss_tot > 0 else 0.0
    # Direction accuracy
    dir_correct = int(np.sum(np.sign(preds - baseline_for_R2) == np.sign(truths - baseline_for_R2)))
    dir_acc = dir_correct / len(truths) if len(truths) else 0.0
    return dict(mae=mae, rmse=rmse, corr=corr, r2=r2, dir_acc=dir_acc)

HORIZONS = [12, 24, 36, 48]
test_idx = list(range(SPLIT, N))

print("\n========= COMBINED AMPLITUDE RESULTS =========\n")
all_results = {}
for h in HORIZONS:
    # Persistence baseline at this horizon
    pers_preds = np.array([NINO[t] for t in test_idx if t+h < N])
    pers_truths = np.array([NINO[t+h] for t in test_idx if t+h < N])
    pers = metrics(pers_preds, pers_truths, pers_preds)  # R² vs persistence itself

    # Climatology
    clim_pred = float(np.mean(NINO[:SPLIT]))
    clim_preds = np.full_like(pers_truths, clim_pred)
    clim = metrics(clim_preds, pers_truths, clim_preds)

    # Combined V1 (no phi_k)
    rb1 = fit_layer1(SPLIT, h, ridge=10.0, phi_k_constraint=False)
    b2, mn = fit_layer2(rb1, SPLIT, h, phi_k_constraint=False)
    p1, t1 = predict_continuous(rb1, b2, mn, test_idx, h, phi_k_constraint=False)
    m1 = metrics(p1, t1, np.full_like(t1, clim_pred))

    # Combined V2 (phi_k)
    rb2 = fit_layer1(SPLIT, h, ridge=10.0, phi_k_constraint=True)
    b22, mn2 = fit_layer2(rb2, SPLIT, h, phi_k_constraint=True)
    p2, t2 = predict_continuous(rb2, b22, mn2, test_idx, h, phi_k_constraint=True)
    m2 = metrics(p2, t2, np.full_like(t2, clim_pred))

    print(f"h={h} mo:")
    print(f"  Climatology       MAE={clim['mae']:.3f}  corr={clim['corr']:+.3f}  dir={clim['dir_acc']*100:.1f}%")
    print(f"  Persistence       MAE={pers['mae']:.3f}  corr={pers['corr']:+.3f}  (predict NINO[t+h]=NINO[t])")
    print(f"  Combined V1       MAE={m1['mae']:.3f}  RMSE={m1['rmse']:.3f}  corr={m1['corr']:+.3f}  R²(vs clim)={m1['r2']:+.3f}  dir={m1['dir_acc']*100:.1f}%")
    print(f"  Combined V2 (φ^k) MAE={m2['mae']:.3f}  RMSE={m2['rmse']:.3f}  corr={m2['corr']:+.3f}  R²(vs clim)={m2['r2']:+.3f}  dir={m2['dir_acc']*100:.1f}%")
    print()
    all_results[h] = dict(climatology=clim, persistence=pers, v1=m1, v2_phi_k=m2)

with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.AMP_TEST = " + json.dumps(all_results, default=str) + ";\n")
print(f"Saved -> {OUT}")
