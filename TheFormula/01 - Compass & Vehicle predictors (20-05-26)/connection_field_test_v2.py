"""
242 connection field test — v2 (FIXED dominant-period detection).

Bug in v1: dominant_rung() picked up secular ~900mo trend in every NOAA series,
making every feeder map to the longest partner (P6 Gleissberg). The framework's
connection-field structure was hidden by the secular drift dominating FFT power.

Fix: restrict the candidate periods to the connection field's predicted rungs
themselves (P1..P6), and pick the rung where the feeder shows MAX bandpassed
variance. This forces each feeder to land on a φ-rung, not on the trend.

Method:
  1. Detrend each feeder (linear).
  2. Bandpass at each connection-field partner period.
  3. The partner period with the largest bandpassed variance = the assignment.

Same train/test split, same ridge=10, same baseline.

DATA: real NOAA Niño 3.4, AMO, TNA, PDO, IOD + JPL Moon (verified).
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
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\connection_field_v2_data.js")

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

# ========================================
# CONNECTION FIELD: 6 partner predictions
# ========================================
ENSO_PERIOD = PHI**8
ENSO_ARA = 2.0

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

# === FIX: dominant rung among connection-field candidates only ===
def dominant_partner(arr, partners_dict):
    """Detrend, then for each partner period compute bandpassed variance.
    Pick the partner with max variance. This forces assignment to a φ-rung."""
    arr_dt = detrend_linear(arr)
    best_name = None; best_var = -1.0
    for pname, pred in partners_dict.items():
        bp = bandpass(arr_dt, pred['period'])
        v = float(np.var(bp))
        if v > best_var:
            best_var = v; best_name = pname
    return best_name, best_var

print("\n=== Each feeder's strongest connection-field partner (variance-matched) ===")
feeders = dict(AMO=AMO, TNA=TNA, PDO=PDO, IOD=IOD)
assignments = {}
for nm, arr in feeders.items():
    pname, v = dominant_partner(arr, partners)
    assignments[nm] = (pname, v)
    print(f"  {nm}: → {pname}  (predicted period {partners[pname]['period']:.1f}mo, bp_var={v:.3e})")

# Moon — try OM_S/OM_C/EC and pick best partner per channel
print("\n=== Moon channels ===")
moon_assignments = {}
for nm, arr in [('MOON_OM_S', MOON_OM_S), ('MOON_OM_C', MOON_OM_C), ('MOON_EC', MOON_EC)]:
    pname, v = dominant_partner(arr, partners)
    moon_assignments[nm] = (pname, v)
    print(f"  {nm}: → {pname}  (predicted period {partners[pname]['period']:.1f}mo, bp_var={v:.3e})")

# ========================================
# Build connection-field feature set: each feeder bandpassed at ITS partner period
# ========================================
cf_features = {}
for nm in feeders:
    period = partners[assignments[nm][0]]['period']
    cf_features[nm] = bandpass(detrend_linear(feeders[nm]), period)
for nm, (pname, _) in moon_assignments.items():
    period = partners[pname]['period']
    arr = {'MOON_OM_S': MOON_OM_S, 'MOON_OM_C': MOON_OM_C, 'MOON_EC': MOON_EC}[nm]
    cf_features[nm] = bandpass(detrend_linear(arr), period)
# Self at ENSO own period
cf_features['NINO'] = bandpass(detrend_linear(NINO), ENSO_PERIOD)

# ========================================
# Baseline: per-rung framework regression with all feeders at all rungs
# ========================================
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

print(f"\n========= CONNECTION FIELD V2 RESULTS =========")
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
    method="v2: dominant-partner via bandpass variance over CF candidates only",
    seed_system='ENSO',
    seed_period_months=ENSO_PERIOD,
    seed_ara=ENSO_ARA,
    partners=partners,
    feeder_assignments={nm: dict(partner=v[0], bp_var=v[1]) for nm,v in assignments.items()},
    moon_assignments={nm: dict(partner=v[0], bp_var=v[1]) for nm,v in moon_assignments.items()},
    horizons=HORIZONS,
    results=results,
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.CONN_FIELD_V2 = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
