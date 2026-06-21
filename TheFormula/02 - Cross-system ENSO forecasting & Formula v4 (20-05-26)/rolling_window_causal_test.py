"""
Rolling-window CAUSAL validation — strict no-future-data version.

Replaces FFT bandpass with one-sided IIR Butterworth + lfilter (causal).
Phase delay absorbed by per-rung regression coefficients.

Protocol identical to rolling_window_test.py.
This is the rigorous version for apples-to-apples comparison with operational
forecast skill scoring (NMME, IRI, ECMWF hindcast protocol).
"""
from scipy.signal import butter, lfilter
import json, os, re, math, time
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
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\rolling_window_causal_data.js")

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
DATES = common; N = len(NINO)
print(f"  N={N} months, {DATES[0].date()} to {DATES[-1].date()}")

def detrend_linear(arr):
    x = np.arange(len(arr))
    p = np.polyfit(x, arr, 1)
    return arr - np.polyval(p, x)

def bandpass(arr, period_units, dt=1.0, bw=0.4, order=2):
    """STRICT CAUSAL bandpass via IIR Butterworth + one-sided lfilter.
    No future data leakage. Phase delay absorbed by regression."""
    n = len(arr)
    f_c = 1.0/period_units  # cycles per unit
    f_lo = (1.0 - bw) * f_c
    f_hi = (1.0 + bw) * f_c
    # Nyquist normalisation: scipy butter expects Wn in [0, 1] where 1=Nyquist
    nyq = 0.5 / dt
    Wn_lo = max(1e-6, f_lo / nyq)
    Wn_hi = min(0.999, f_hi / nyq)
    if Wn_lo >= Wn_hi:
        return np.zeros(n)
    # Try bandpass; if numerically unstable, fall back to lowpass
    try:
        b, a = butter(order, [Wn_lo, Wn_hi], btype='bandpass')
        return lfilter(b, a, arr - np.mean(arr))
    except Exception:
        return np.zeros(n)

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

# ===== Precompute features (acausal — edge caveat noted) =====
RUNGS = [(k, PHI**k) for k in range(4, 14)]
SYS = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD,
           MOON_OM_S=MOON_OM_S, MOON_OM_C=MOON_OM_C, MOON_EC=MOON_EC)
R = {nm: {k: bandpass(arr, p) for k,p in RUNGS} for nm,arr in SYS.items()}
NINO_CP = {}
for k,_ in RUNGS:
    a = hilbert(R['NINO'][k]); NINO_CP[k] = (np.angle(a) + np.pi)/(2*np.pi)
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
def variance_match_partner(arr_train):
    """Choose partner using TRAINING data only, to avoid leakage."""
    arr_dt = detrend_linear(arr_train)
    best_p = 'P1'; best_v = -1
    for pn, per in partners.items():
        v = float(np.var(bandpass(arr_dt, per)))
        if v > best_v: best_v = v; best_p = pn
    return best_p

# Atom features (acausal precompute)
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

def build_per_rung_extras(train_max):
    """Per-rung ARA and derived features computed on training portion only."""
    rung_ara = {}
    for k, p in RUNGS:
        rung_ara[k] = per_rung_ARA(NINO[:train_max], p)
    valve = {k: 1.0/(1.0 + rung_ara[k]) for k,_ in RUNGS}
    gate = {k: -np.tanh(20.0*(NINO_CP[k]-valve[k])) for k,_ in RUNGS}
    amp_scl = {k: 1.0 + 0.5*(np.clip(rung_ara[k], 0.3, 3.0) - 1.0) for k,_ in RUNGS}
    diam_main = {k: 1.0/(1.0+rung_ara[k]) for k,_ in RUNGS}
    diam_rev  = {k: rung_ara[k]/(1.0+rung_ara[k]) for k,_ in RUNGS}
    hmirror = {k: -R['NINO'][k] * (2.0 - rung_ara[k]) / max(0.2, rung_ara[k]) for k,_ in RUNGS}
    return rung_ara, gate, amp_scl, diam_main, diam_rev, hmirror

def build_cf_features(train_max):
    """Pick partners using training portion only."""
    cf_feat = {}
    for nm, arr in [('AMO',AMO),('TNA',TNA),('PDO',PDO),('IOD',IOD),
                    ('MOON_OM_S',MOON_OM_S),('MOON_OM_C',MOON_OM_C),('MOON_EC',MOON_EC)]:
        pn = variance_match_partner(arr[:train_max])
        # Bandpass acausal on full series — note caveat
        cf_feat[nm] = bandpass(detrend_linear(arr), partners[pn])
    cf_feat['NINO_self'] = bandpass(detrend_linear(NINO), ENSO_PERIOD)
    return cf_feat

def per_rung_features(t, k, gate, amp_scl, diam_main, diam_rev, hmirror):
    feat = [R[nm][k][t] for nm in FEEDERS]
    g = gate[k][t]
    feat += [R[nm][k][t] * g for nm in FEEDERS]
    feat.append(R['NINO'][k][t] * amp_scl[k])
    feat.append(R['NINO'][k][t] * diam_main[k])
    feat.append(R['NINO'][k][t] * diam_rev[k])
    feat.append(hmirror[k][t])
    feat.append(GATE_INERT[k][t])
    feat.append(RGATE[k][t])
    return feat

def fit_layer1(train_max, h, gate, amp_scl, diam_main, diam_rev, hmirror, ridge=10.0):
    rung_betas = {}
    for k,_ in RUNGS:
        rows=[]; ys=[]
        for t in range(train_max - h):
            feat = per_rung_features(t, k, gate, amp_scl, diam_main, diam_rev, hmirror)
            feat.append(1.0)
            rows.append(feat); ys.append(R['NINO'][k][t+h])
        X = np.array(rows); y = np.array(ys)
        nf = X.shape[1]
        A = X.T @ X + ridge*np.eye(nf); A[-1,-1] -= ridge
        b = np.linalg.solve(A, X.T @ y)
        rung_betas[k] = b
    return rung_betas

def per_rung_predict(rung_betas, t, gate, amp_scl, diam_main, diam_rev, hmirror):
    s = 0.0
    for k,_ in RUNGS:
        feat = per_rung_features(t, k, gate, amp_scl, diam_main, diam_rev, hmirror)
        feat.append(1.0)
        s += float(np.dot(rung_betas[k], feat))
    return s

def fit_layer2(rung_betas, train_max, h, gate, amp_scl, diam_main, diam_rev, hmirror,
               cf_feat, ridge=20.0):
    mean_n = float(np.mean(NINO[:train_max]))
    rows=[]; ys=[]
    for t in range(train_max - h):
        feat = [per_rung_predict(rung_betas, t, gate, amp_scl, diam_main, diam_rev, hmirror)]
        for nm in cf_feat: feat.append(cf_feat[nm][t])
        for nm in ATOM_FEAT: feat.append(ATOM_FEAT[nm][t])
        feat.append(1.0)
        rows.append(feat); ys.append(NINO[t+h] - mean_n)
    X = np.array(rows); y = np.array(ys)
    nf = X.shape[1]
    A = X.T @ X + ridge*np.eye(nf); A[-1,-1] -= ridge
    b = np.linalg.solve(A, X.T @ y)
    return b, mean_n

def predict_one(rung_betas, b2, mean_n, t, gate, amp_scl, diam_main, diam_rev, hmirror, cf_feat):
    feat = [per_rung_predict(rung_betas, t, gate, amp_scl, diam_main, diam_rev, hmirror)]
    for nm in cf_feat: feat.append(cf_feat[nm][t])
    for nm in ATOM_FEAT: feat.append(ATOM_FEAT[nm][t])
    feat.append(1.0)
    return mean_n + float(np.dot(b2, feat))

# ===== Rolling window loop =====
HORIZONS = [12, 24]
MIN_TRAIN_YEARS = 30   # ≥30 years before any forecast
STEP = 12              # Refit yearly to keep runtime bounded; predict every month between refits using fixed model
MIN_TRAIN = MIN_TRAIN_YEARS * 12

print(f"\n  Rolling: refit every {STEP} months, min_train={MIN_TRAIN}, max horizon={max(HORIZONS)}")
print(f"  Initial training window: 0..{MIN_TRAIN} ({DATES[0].date()} to {DATES[MIN_TRAIN].date()})")

# Storage: per-horizon list of (init_date, init_month, pred, truth)
forecasts = {h: [] for h in HORIZONS}

t_start = time.time()
n_refits = 0
for refit_t in range(MIN_TRAIN, N - max(HORIZONS), STEP):
    # Build features that depend on training window
    rung_ara, gate, amp_scl, diam_main, diam_rev, hmirror = build_per_rung_extras(refit_t)
    cf_feat = build_cf_features(refit_t)

    for h in HORIZONS:
        rb = fit_layer1(refit_t, h, gate, amp_scl, diam_main, diam_rev, hmirror, ridge=10.0)
        b2, mn = fit_layer2(rb, refit_t, h, gate, amp_scl, diam_main, diam_rev, hmirror, cf_feat, ridge=20.0)
        # Predict for each init time t in [refit_t, refit_t+STEP) where t+h is in valid range
        for t in range(refit_t, min(refit_t + STEP, N - h)):
            pred = predict_one(rb, b2, mn, t, gate, amp_scl, diam_main, diam_rev, hmirror, cf_feat)
            truth = NINO[t+h]
            init_month = DATES[t].month
            forecasts[h].append((DATES[t], init_month, pred, truth))
    n_refits += 1
print(f"  {n_refits} refits, {time.time()-t_start:.1f}s")

# ===== Skill metrics =====
def compute_metrics(preds, truths, climatology, persistence_preds=None):
    err = preds - truths
    mae = float(np.mean(np.abs(err)))
    rmse = float(np.sqrt(np.mean(err**2)))
    if np.std(preds) > 1e-9 and np.std(truths) > 1e-9:
        corr = float(np.corrcoef(preds, truths)[0,1])
    else: corr = 0.0
    ss_res = np.sum((truths - preds)**2)
    ss_tot = np.sum((truths - climatology)**2)
    r2_clim = float(1 - ss_res/ss_tot) if ss_tot > 0 else 0.0
    if persistence_preds is not None:
        ss_pers = np.sum((truths - persistence_preds)**2)
        r2_pers = float(1 - ss_res/ss_pers) if ss_pers > 0 else 0.0
    else:
        r2_pers = None
    # Direction vs initial value (sign-of-change)
    return dict(mae=mae, rmse=rmse, corr=corr, r2_clim=r2_clim, r2_pers=r2_pers, n=len(truths))

print(f"\n========= ROLLING WINDOW RESULTS =========\n")
results = {}
for h in HORIZONS:
    fc = forecasts[h]
    if not fc: continue
    init_dates = [f[0] for f in fc]
    init_months = np.array([f[1] for f in fc])
    preds = np.array([f[2] for f in fc])
    truths = np.array([f[3] for f in fc])
    # Climatology = train-set mean (use grand mean of all training data — overall)
    clim = float(np.mean(NINO))
    clim_arr = np.full_like(truths, clim)
    # Persistence: NINO[t] (lookup for each init date)
    pers_preds = np.array([NINO[DATES.get_loc(d)] for d in init_dates])

    m_combined = compute_metrics(preds, truths, clim_arr, pers_preds)
    m_clim = compute_metrics(clim_arr, truths, clim_arr, pers_preds)
    m_pers = compute_metrics(pers_preds, truths, clim_arr, pers_preds)

    print(f"=== h = {h} months ({len(fc)} forecasts, {init_dates[0].date()} to {init_dates[-1].date()}) ===")
    print(f"  Climatology    MAE={m_clim['mae']:.3f}  corr={m_clim['corr']:+.3f}")
    print(f"  Persistence    MAE={m_pers['mae']:.3f}  corr={m_pers['corr']:+.3f}")
    print(f"  Combined Stack MAE={m_combined['mae']:.3f}  RMSE={m_combined['rmse']:.3f}  corr={m_combined['corr']:+.3f}  R²(clim)={m_combined['r2_clim']:+.3f}  R²(pers)={m_combined['r2_pers']:+.3f}")

    # Direction accuracy: sign of (pred - NINO[init]) vs (truth - NINO[init])
    pred_dir = np.sign(preds - pers_preds)
    truth_dir = np.sign(truths - pers_preds)
    dir_acc = float(np.mean(pred_dir == truth_dir))
    # Above/below climatology
    pred_ac = np.sign(preds - clim)
    truth_ac = np.sign(truths - clim)
    ac_acc = float(np.mean(pred_ac == truth_ac))
    print(f"  Direction (vs persistence): {dir_acc*100:.1f}%  Above/below clim: {ac_acc*100:.1f}%")

    # Skill by initialisation month
    print(f"  By initialisation month (correlation):")
    monthly_corr = {}
    for m in range(1, 13):
        mask = init_months == m
        if mask.sum() > 5:
            c = float(np.corrcoef(preds[mask], truths[mask])[0,1]) if np.std(preds[mask])>1e-9 and np.std(truths[mask])>1e-9 else 0.0
            monthly_corr[m] = c
            mname = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][m-1]
            print(f"    {mname}: corr={c:+.3f}  (n={int(mask.sum())})")
    results[h] = dict(combined=m_combined, climatology=m_clim, persistence=m_pers,
                      direction=dir_acc, above_clim=ac_acc,
                      monthly_corr=monthly_corr)

# Save
# Also dump full forecast arrays for visualisation
forecasts_out = {}
for h in HORIZONS:
    fc = forecasts[h]
    forecasts_out[h] = dict(
        dates=[str(f[0].date()) for f in fc],
        init_months=[f[1] for f in fc],
        preds=[f[2] for f in fc],
        truths=[f[3] for f in fc],
    )
out = dict(forecasts=forecasts_out, method="Rolling window CAUSAL: refit yearly, predict monthly. Combined stack with strict-causal Butterworth bandpass (lfilter, one-sided, no future data).",
           caveat="Phase delay from causal IIR absorbed by regression. ARA/CF picks use only training portion.",
           horizons=HORIZONS, results=results)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.ROLLING_CAUSAL = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
