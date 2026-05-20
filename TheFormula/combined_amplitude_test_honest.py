"""HONEST audit of combined_amplitude_test.py — Combined Stack at h=24.

Past code claimed corr +0.75 at h=24. That script used:
  - FFT bandpass on full signal (test data influences "past" bandpassed values)
  - Hilbert transform on full signal (also non-causal)
  - Linear detrend across full signal
  - Partner selection based on full-signal variance

All non-causal. The corr +0.75 was inflated by features that know the future.

This script fixes those leaks:
  - Causal Butterworth bandpass (lfilter)
  - Causal phase estimation (no Hilbert on full signal)
  - Detrend using only training data
  - Partner selection using only training-data variance

Then runs the same train/test split (N//2) and reports HONEST correlation.
"""
import os, math
import numpy as np, pandas as pd
from scipy.signal import butter, lfilter, find_peaks
from scipy.ndimage import gaussian_filter1d

PHI = 1.6180339887498949

def _resolve(p):
    pl = p.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return pl if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p

NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
AMO_PATH  = _resolve(r"F:\SystemFormulaFolder\HURDAT2\Temp\amonuslong.txt")
TNA_PATH  = _resolve(r"F:\SystemFormulaFolder\HURDAT2\Temp\tna.txt")
PDO_PATH  = _resolve(r"F:\SystemFormulaFolder\PDO_NOAA\ersst.v5.pdo.dat")
IOD_PATH  = _resolve(r"F:\SystemFormulaFolder\IOD_NOAA\dmi.had.long.data")

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
    with open(IOD_PATH) as f:
        next(f)
        for ln in f:
            parts = ln.split()
            if len(parts) < 13: continue
            try: year = int(parts[0])
            except: continue
            for m in range(12):
                try: v = float(parts[1+m])
                except: continue
                if v < -90: continue
                rows.append((pd.Timestamp(year=year, month=m+1, day=1), v))
    return pd.Series(dict(rows)).sort_index()

print("Loading...")
nino = load_nino()
amo = load_grid_text(AMO_PATH); tna = load_grid_text(TNA_PATH)
pdo = load_grid_text(PDO_PATH, header_lines=2); iod = load_iod()
def to_m(s):
    s = s.copy(); s.index = pd.to_datetime(s.index).to_period('M').to_timestamp()
    return s.groupby(s.index).first()
nino,amo,tna,pdo,iod = [to_m(x) for x in [nino,amo,tna,pdo,iod]]
common = nino.index
for s in [amo, tna, pdo, iod]:
    common = common.intersection(s.index)
common = common.sort_values()
NINO = nino.reindex(common).values.astype(float)
AMO  = amo.reindex(common).values.astype(float)
TNA  = tna.reindex(common).values.astype(float)
PDO  = pdo.reindex(common).values.astype(float)
IOD  = iod.reindex(common).values.astype(float)
N = len(NINO); SPLIT = N // 2
print(f"  N={N} months, SPLIT={SPLIT} (train {SPLIT} mo / test {N-SPLIT} mo)")

# ===== CAUSAL bandpass (replaces non-causal FFT version) =====
def causal_bandpass(arr, period_units, bw=0.4, order=2):
    """Butterworth + lfilter — strictly causal. No future leakage."""
    n = len(arr); fc = 1.0/period_units; nyq = 0.5
    Wn_lo = max(1e-6, (1-bw)*fc/nyq); Wn_hi = min(0.999, (1+bw)*fc/nyq)
    if Wn_lo >= Wn_hi: return np.zeros(n)
    b, a = butter(order, [Wn_lo, Wn_hi], btype='bandpass')
    return lfilter(b, a, arr - np.mean(arr))

# ===== HONEST detrend — uses only training data =====
def detrend_linear_train_only(arr, split):
    """Fit linear trend on training data only, subtract from full signal."""
    x_train = np.arange(split)
    p = np.polyfit(x_train, arr[:split], 1)
    return arr - np.polyval(p, np.arange(len(arr)))

# ===== HONEST per-rung ARA — training only =====
def per_rung_ARA_causal(arr_train, period):
    bp = causal_bandpass(arr_train, period, bw=0.85)
    if len(bp) < 3 * int(period): return 1.0
    smoothed = gaussian_filter1d(bp, max(1, int(period * 0.05)))
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

# ===== Build CAUSAL features =====
RUNGS = [(k, PHI**k) for k in range(4, 14)]
K_REF = 8
SYS_RAW = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD)

# Detrend each signal using TRAINING ONLY trend
SYS = {nm: detrend_linear_train_only(arr, SPLIT) for nm, arr in SYS_RAW.items()}

# Causal bandpass per rung — feeds work because lfilter sees only past
R = {nm: {k: causal_bandpass(arr, p) for k, p in RUNGS} for nm, arr in SYS.items()}

# ARA computed from training only
RUNG_ARA = {k: per_rung_ARA_causal(SYS['NINO'][:SPLIT], p) for k, p in RUNGS}
VALVE = {k: 1.0/(1.0 + RUNG_ARA[k]) for k, _ in RUNGS}

# Causal phase estimate per rung: at time t, use the most recent ~50 samples of bandpass
# to estimate amplitude + phase. We'll inline a simpler causal approach: use atan2 of
# (current, current-quarter-period-back) which is roughly the analytic signal causally.
def causal_phase_amp_series(bp, period):
    """Return phase[t] and amp[t] estimated causally from bandpass values."""
    n = len(bp)
    phase = np.zeros(n); amp = np.zeros(n)
    quarter = max(1, int(period / 4))
    for t in range(n):
        if t < quarter:
            phase[t] = 0.0; amp[t] = abs(bp[t])
            continue
        x = bp[t]; y = bp[t - quarter]
        amp[t] = math.sqrt(x*x + y*y) + 1e-9
        phase[t] = math.atan2(x, y)  # 0 to 2π-like
    return phase, amp

NINO_PHASE = {}; NINO_AMP = {}
for k, p in RUNGS:
    ph, am = causal_phase_amp_series(R['NINO'][k], p)
    NINO_PHASE[k] = (ph + np.pi) / (2*np.pi)  # 0..1
    NINO_AMP[k] = am

GATE = {k: -np.tanh(20.0*(NINO_PHASE[k] - VALVE[k])) for k, _ in RUNGS}

def amp_scale(ARA): return 1.0 + 0.5*(np.clip(ARA, 0.3, 3.0) - 1.0)
AMP_SCALE = {k: amp_scale(RUNG_ARA[k]) for k, _ in RUNGS}
DIAMOND_MAIN = {k: 1.0/(1.0+RUNG_ARA[k]) for k, _ in RUNGS}
DIAMOND_REV  = {k: RUNG_ARA[k]/(1.0+RUNG_ARA[k]) for k, _ in RUNGS}
HMIRROR = {k: -R['NINO'][k] * (2.0 - RUNG_ARA[k]) / max(0.2, RUNG_ARA[k]) for k, _ in RUNGS}
GATE_INERT = {}
for k, p in RUNGS:
    lag = max(1, int(p/4))
    GATE_INERT[k] = np.concatenate([np.zeros(lag), R['NINO'][k][:-lag]])
RGATE = {}
for k, _ in RUNGS:
    if k+1 < 14: RGATE[k] = R['NINO'][k] * R['NINO'][k+1]
    else: RGATE[k] = np.zeros(N)

# ===== CF features: causal bandpass on TRAIN-DETRENDED signals,
# partner selection uses TRAINING variance only =====
ENSO_PERIOD = PHI**8
partners = {'P1':ENSO_PERIOD, 'P2':ENSO_PERIOD*PHI, 'P3':ENSO_PERIOD/PHI,
            'P4':ENSO_PERIOD*PHI**2, 'P5':ENSO_PERIOD/PHI**2, 'P6':ENSO_PERIOD*PHI**4}

def variance_match_partner_train(arr_full):
    """Pick partner period by variance — TRAINING DATA ONLY."""
    arr_train = arr_full[:SPLIT]
    best_p = 'P1'; best_v = -1
    for pn, per in partners.items():
        v = float(np.var(causal_bandpass(arr_train, per)))
        if v > best_v: best_v = v; best_p = pn
    return best_p

CF_FEAT = {}
for nm, arr in [('AMO',SYS['AMO']),('TNA',SYS['TNA']),('PDO',SYS['PDO']),('IOD',SYS['IOD'])]:
    pn = variance_match_partner_train(arr)
    CF_FEAT[nm] = causal_bandpass(arr, partners[pn])
CF_FEAT['NINO_self'] = causal_bandpass(SYS['NINO'], ENSO_PERIOD)

# φ⁹ atom — causal bandpass + causal phase
ATOM_RUNGS = [PHI**7, PHI**8, PHI**9]
ATOM_SYS = [('NINO', SYS['NINO']), ('PDO', SYS['PDO']), ('IOD', SYS['IOD'])]
ATOM_FEAT = {}
for nm, arr in ATOM_SYS:
    for ai, p in enumerate(ATOM_RUNGS):
        bp = causal_bandpass(arr, p)
        ph, am = causal_phase_amp_series(bp, p)
        ATOM_FEAT[f'{nm}_r{ai}_env'] = am
        ATOM_FEAT[f'{nm}_r{ai}_cos'] = np.cos(ph)
        ATOM_FEAT[f'{nm}_r{ai}_sin'] = np.sin(ph)

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

def fit_layer1(train_max, h, ridge=10.0):
    rung_betas = {}
    for k, _ in RUNGS:
        rows=[]; ys=[]
        for t in range(train_max - h):
            feat = per_rung_features_full(t, k)
            feat.append(1.0)
            rows.append(feat); ys.append(R['NINO'][k][t+h])
        X = np.array(rows); y = np.array(ys)
        nf = X.shape[1]
        A = X.T @ X + ridge*np.eye(nf); A[-1,-1] -= ridge
        b = np.linalg.solve(A, X.T @ y)
        rung_betas[k] = b
    return rung_betas

def per_rung_predict(rung_betas, t):
    s = 0.0
    for k, _ in RUNGS:
        feat = per_rung_features_full(t, k)
        feat.append(1.0)
        s += float(np.dot(rung_betas[k], feat))
    return s

def fit_layer2(rung_betas, train_max, h, ridge=20.0):
    mean_n = float(np.mean(NINO[:train_max]))
    rows=[]; ys=[]
    for t in range(train_max - h):
        feat = [per_rung_predict(rung_betas, t)]
        for nm in CF_FEAT: feat.append(CF_FEAT[nm][t])
        for nm in ATOM_FEAT: feat.append(ATOM_FEAT[nm][t])
        feat.append(1.0)
        rows.append(feat); ys.append(NINO[t+h] - mean_n)
    X = np.array(rows); y = np.array(ys)
    nf = X.shape[1]
    A = X.T @ X + ridge*np.eye(nf); A[-1,-1] -= ridge
    b = np.linalg.solve(A, X.T @ y)
    return b, mean_n

def predict_continuous(rung_betas, b2, mean_n, test_indices, h):
    preds=[]; truths=[]; perss=[]
    for t in test_indices:
        if t + h >= N: continue
        feat = [per_rung_predict(rung_betas, t)]
        for nm in CF_FEAT: feat.append(CF_FEAT[nm][t])
        for nm in ATOM_FEAT: feat.append(ATOM_FEAT[nm][t])
        feat.append(1.0)
        pred = mean_n + float(np.dot(b2, feat))
        preds.append(pred); truths.append(NINO[t+h]); perss.append(NINO[t])
    return np.array(preds), np.array(truths), np.array(perss)

def metrics(preds, truths, pers):
    err = preds - truths
    mae = float(np.mean(np.abs(err)))
    if np.std(preds) > 1e-9 and np.std(truths) > 1e-9:
        corr = float(np.corrcoef(preds, truths)[0, 1])
    else: corr = 0.0
    p_mae = float(np.mean(np.abs(pers - truths)))
    p_corr = float(np.corrcoef(pers, truths)[0, 1]) if np.std(pers) > 1e-9 else 0.0
    return dict(mae=mae, corr=corr, pers_mae=p_mae, pers_corr=p_corr)


print('\n========= COMBINED STACK — HONEST AUDIT =========\n')
print('Test set: months SPLIT..N-h. Train: 0..SPLIT.')
print('All bandpass causal (lfilter). All phase causal. Detrend train-only. Partner select train-only.\n')
print(f'{"h":>3}  {"corr":>7}  {"MAE":>6}  {"persCorr":>9}  {"persMAE":>8}  {"Δcorr_vs_pers":>15}  {"verdict":>8}')
print('-' * 80)
test_idx = list(range(SPLIT, N))
for h in [12, 24, 36, 48]:
    rb = fit_layer1(SPLIT, h, ridge=10.0)
    b2, mn = fit_layer2(rb, SPLIT, h, ridge=20.0)
    p, t, pp = predict_continuous(rb, b2, mn, test_idx, h)
    m = metrics(p, t, pp)
    dc = m['corr'] - m['pers_corr']
    v = 'WIN' if m['corr'] > m['pers_corr'] else 'lose'
    print(f'{h:>3}  {m["corr"]:>+.3f}  {m["mae"]:>.3f}  {m["pers_corr"]:>+9.3f}  {m["pers_mae"]:>8.3f}  {dc:>+15.3f}  {v:>8}')

print('\nPast claim from project_enso_24mo_amplitude.md (LEAKY version):')
print(' h=12:  corr +0.86  MAE 0.36')
print(' h=24:  corr +0.75  MAE 0.47  <-- the headline')
print(' h=36:  corr +0.47  MAE 0.60')
print(' h=48:  corr +0.34  MAE 0.67')
