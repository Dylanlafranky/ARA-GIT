"""
242 connection field test — framework-derived feeder assignments.

For ENSO as seed at φ⁸ (~47mo) with ARA ≈ 2.0, the connection field predicts
6 partners at specific (period, ARA) coordinates:
  Partner 1: same rung, ARA mirror (φ⁸, ARA=0)
  Partner 2: one rung down — PDO sits here (φ⁹, ARA=1.24)
  Partner 3: one rung up — QBO scale (φ⁷, ARA=2.0)
  Partner 4: two rungs down — AMO scale (φ¹⁰, ARA=0.76)
  Partner 5: two rungs up — annual scale (φ⁶, ARA=2.0)
  Partner 6: Gleissberg-distance — Moon nodal (φ¹², ARA=0.5)

Test:
  Use ENSO's own data + each feeder bandpassed at its FRAMEWORK-PREDICTED
  partner period (one bandpass per feeder, not all rungs).

Compare to baseline (per-rung regression with all feeders at all rungs).

If the framework's 6-connection geometry correctly identifies which feeder
sits at which partner role, this MORE FOCUSED test should match or beat
the brute-force baseline at fewer parameters.

DATA: real NOAA Niño 3.4, AMO, TNA, PDO, IOD + JPL Moon (verified sources).
"""
import json, os, re, math
import numpy as np, pandas as pd

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
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\connection_field_data.js")

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

# ========================================
# CONNECTION FIELD: derive 6 partner predictions for ENSO
# ========================================
ENSO_PERIOD = PHI**8  # 47mo
ENSO_ARA = 2.0  # class-level

partners = {
    'P1_horizontal':       dict(period=ENSO_PERIOD,           ara=2.0 - ENSO_ARA, role='same rung mirror'),
    'P2_vertical_child':   dict(period=ENSO_PERIOD * PHI,     ara=ENSO_ARA / PHI, role='one rung down'),
    'P3_vertical_parent':  dict(period=ENSO_PERIOD / PHI,     ara=min(2.0, ENSO_ARA * PHI), role='one rung up'),
    'P4_two_down':         dict(period=ENSO_PERIOD * PHI**2,  ara=ENSO_ARA / PHI**2, role='two rungs down'),
    'P5_two_up':           dict(period=ENSO_PERIOD / PHI**2,  ara=min(2.0, ENSO_ARA * PHI**2), role='two rungs up'),
    'P6_gleissberg':       dict(period=ENSO_PERIOD * PHI**4,  ara=1.0/ENSO_ARA, role='Gleissberg-distance complement'),
}

print("\n=== CONNECTION FIELD — predicted partners for ENSO ===")
for name, p in partners.items():
    print(f"  {name:<22} period={p['period']:>7.1f}mo  ARA={p['ara']:>5.2f}  role: {p['role']}")

# Best-match each feeder to a connection field partner
# We do this by spectral analysis: find each feeder's dominant rung period
def dominant_rung(arr):
    F = np.abs(np.fft.rfft(arr - np.mean(arr)))**2
    freqs = np.fft.rfftfreq(len(arr), d=1.0)
    # ignore DC
    F[0] = 0
    if F.max() < 1e-9: return None
    f_peak = freqs[np.argmax(F)]
    return 1.0 / f_peak if f_peak > 0 else None

print("\n=== Each feeder's dominant period (spectral peak) ===")
feeders = dict(AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD)
feeder_periods = {}
for nm, arr in feeders.items():
    dp = dominant_rung(arr)
    feeder_periods[nm] = dp
    print(f"  {nm}: peak at {dp:.1f}mo")

# Match feeders to partners by period proximity (log-space)
print("\n=== Best-match feeder → connection field partner ===")
def log_distance(a, b):
    return abs(math.log(a) - math.log(b))

assignments = {}
for nm, p in feeder_periods.items():
    if p is None: continue
    # Find closest partner by period
    best = None; best_dist = 999
    for pname, pred in partners.items():
        d = log_distance(p, pred['period'])
        if d < best_dist:
            best_dist = d; best = pname
    assignments[nm] = (best, best_dist)
    print(f"  {nm} (peak {p:.1f}mo) → {best} (predicted {partners[best]['period']:.1f}mo, log-dist {best_dist:.2f})")

# ========================================
# TEST: Use feeders bandpassed at their predicted partner periods
# vs baseline (all feeders bandpassed at all rungs)
# ========================================

# Connection-field-derived feature set: each feeder bandpassed AT its assigned partner period
# (not at all rungs)
def cf_feature(arr, period):
    return bandpass(arr, period)

cf_features = {}
for nm in feeders:
    period = partners[assignments[nm][0]]['period']
    cf_features[nm] = cf_feature(feeders[nm], period)

# Also include Moon at P6 (Gleissberg distance)
cf_features['MOON_OM_S'] = cf_feature(MOON_OM_S, partners['P6_gleissberg']['period'])
cf_features['MOON_OM_C'] = cf_feature(MOON_OM_C, partners['P6_gleissberg']['period'])
cf_features['MOON_EC']  = cf_feature(MOON_EC,  partners['P6_gleissberg']['period'])

# Self at ENSO's own period
cf_features['NINO'] = cf_feature(NINO, ENSO_PERIOD)

# === Baseline: per-rung framework regression ===
RUNGS_FULL = [(k, PHI**k) for k in range(4, 14)]
SYS_FULL = dict(NINO=NINO, AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD,
                MOON_OM_S=MOON_OM_S, MOON_OM_C=MOON_OM_C, MOON_EC=MOON_EC)
R_FULL = {nm: {k: bandpass(arr, p) for k,p in RUNGS_FULL} for nm,arr in SYS_FULL.items()}

def dir_truth(arr, t, h):
    if t + h >= len(arr): return None
    diff = arr[t + h] - arr[t]
    return 1 if diff > 0 else (-1 if diff < 0 else 0)

def acc_baseline(idx, h, train_max, ridge=10.0):
    if train_max - h < 20: return None
    rung_betas = {}
    feeders_list = list(SYS_FULL.keys())
    for k,_ in RUNGS_FULL:
        rows=[]; ys=[]
        for t in range(train_max - h):
            feat = [R_FULL[nm][k][t] for nm in feeders_list]; feat.append(1.0)
            rows.append(feat); ys.append(R_FULL['NINO'][k][t+h])
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
        for k,_ in RUNGS_FULL:
            b = rung_betas[k]
            feat = [R_FULL[nm][k][t] for nm in feeders_list] + [1.0]
            s += float(np.dot(b, feat))
        pred = 1 if s>NINO[t] else -1
        correct += (pred==true); total += 1
    return correct/total if total else 0

def acc_connection_field(idx, h, train_max, include_baseline=False, ridge=10.0):
    if train_max - h < 20: return None
    cf_feeder_names = list(cf_features.keys())
    rows=[]; ys=[]
    for t in range(train_max - h):
        feat = [cf_features[nm][t] for nm in cf_feeder_names]
        if include_baseline:
            for k,_ in RUNGS_FULL:
                feat.append(R_FULL['NINO'][k][t])
        feat.append(1.0)
        rows.append(feat); ys.append(NINO[t+h])
    X = np.array(rows); y = np.array(ys)
    n_features = X.shape[1]
    A = X.T @ X + ridge * np.eye(n_features); A[-1,-1] -= ridge
    b = np.linalg.solve(A, X.T @ y)
    correct=0; total=0
    for t in idx:
        true = dir_truth(NINO, t, h)
        if true is None or true==0: continue
        feat = [cf_features[nm][t] for nm in cf_feeder_names]
        if include_baseline:
            for k,_ in RUNGS_FULL:
                feat.append(R_FULL['NINO'][k][t])
        feat.append(1.0)
        pred_val = float(np.dot(b, feat))
        pred = 1 if pred_val > NINO[t] else -1
        correct += (pred==true); total += 1
    return correct/total if total else 0

HORIZONS = [12, 24, 36, 48]
test_idx = list(range(SPLIT, N))

print(f"\n========= CONNECTION FIELD RESULTS =========")
print(f"{'horizon':>10}  {'baseline':>9}  {'CF only':>9}  {'CF + base':>10}")
results = {}
for h in HORIZONS:
    a_base = acc_baseline(test_idx, h, SPLIT)
    a_cf = acc_connection_field(test_idx, h, SPLIT, include_baseline=False)
    a_cf_plus = acc_connection_field(test_idx, h, SPLIT, include_baseline=True)
    print(f"  h={h:>2} mo  {a_base*100:>8.1f}%  {a_cf*100:>8.1f}%  {a_cf_plus*100:>9.1f}%")
    results[h] = dict(baseline=a_base, cf_only=a_cf, cf_plus_baseline=a_cf_plus)

print(f"\nLifts vs baseline:")
for h in HORIZONS:
    r = results[h]
    bd = r['baseline']
    print(f"  h={h:>2} mo  CF only {(r['cf_only']-bd)*100:+.1f}  CF+base {(r['cf_plus_baseline']-bd)*100:+.1f}")

out = dict(
    sources="Same as direction_prediction_v2 (verified NOAA + JPL Horizons)",
    seed_system='ENSO',
    seed_period_months=ENSO_PERIOD,
    seed_ara=ENSO_ARA,
    partners=partners,
    feeder_assignments={nm: dict(partner=v[0], log_dist=v[1]) for nm,v in assignments.items()},
    horizons=HORIZONS,
    results=results,
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.CONN_FIELD = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
