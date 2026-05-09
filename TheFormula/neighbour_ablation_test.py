"""
neighbour_ablation_test.py

Test Dylan's "1 + 0.25×N" derivation of the predictor crossover exponent.

Hypothesis: the crossover sits at  h = home_period × φ^(±E)  where
  E = 1 + 0.25 × N
  N = number of active rung-neighbour bands beyond the home rung itself

Predicted crossover exponents (in φ-rungs from home):
  N = 0  (home only):       E = 1.00     → cross at φ^±1.00 × home
  N = 1  (home + 1 band):   E = 1.25     → cross at φ^±1.25 × home
  N = 2  (home + 2 bands):  E = 1.50     → cross at φ^±1.50 × home
  N = 3  (home + 3 bands):  E = 1.75     → cross at φ^±1.75 × home  ← matches measured

Bands:
  Below:  rungs k < home_k
  Same:   matched-rung partner at home_k (only meaningful for closed systems)
  Above:  rungs k > home_k

Run the same predictor under each ablation, sweep horizons, find crossover,
compare to predicted E.
"""
import json, os, time, sys
sys.path.insert(0, '/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder')
from ara_framework import extract_topology, _predict_act, _predict_old, PHI
import numpy as np, pandas as pd
import wfdb

OUT = '/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder/TheFormula/neighbour_ablation_data.js'

# === Load ENSO ===
print("Loading NINO 3.4 + SOI...")
df = pd.read_csv('/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder/Nino34/nino34.long.anom.csv',
                 skiprows=1, header=None, names=['date','val'])
df['date'] = pd.to_datetime(df['date'].str.strip())
df = df[df['val'] > -90].copy()
nino = df.set_index('date')['val'].astype(float)
nino.index = pd.to_datetime(nino.index).to_period('M').to_timestamp()
nino = nino.groupby(nino.index).first()

soi_rows=[]
with open('/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder/SOI_NOAA/soi.data') as f:
    next(f)
    for ln in f:
        parts = ln.split()
        if len(parts) < 13: continue
        try: y = int(parts[0])
        except: continue
        if y < 1900 or y > 2100: continue
        for m in range(12):
            try: v = float(parts[1+m])
            except: continue
            if v < -90: continue
            soi_rows.append((pd.Timestamp(year=y, month=m+1, day=1), v))
soi = pd.Series(dict(soi_rows)).sort_index()
soi.index = pd.to_datetime(soi.index).to_period('M').to_timestamp()
soi = soi.groupby(soi.index).first()
common = nino.index.intersection(soi.index).sort_values()
NINO = nino.reindex(common).values.astype(float)
SOI  = soi.reindex(common).values.astype(float)
N_ENSO = len(NINO)

# === Load ECG ===
print("Loading ECG nsr001...")
ann = wfdb.rdann('/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder/normal-sinus-rhythm-rr-interval-database-1.0.0/nsr001', 'ecg')
RR = (np.diff(ann.sample) / ann.fs * 1000).astype(float)
N_ECG = len(RR)
print(f"  ENSO: {N_ENSO} months   ECG: {N_ECG} beats")

HOME_K = 8

# === Ablation: which rungs are present? ===
def rungs_for_config(config, home_k=HOME_K):
    """Returns the rung-k indices included for each ablation config."""
    if config == 'HOME_ONLY':         return [home_k]
    if config == 'HOME_BELOW':        return list(range(2, home_k + 1))
    if config == 'HOME_ABOVE':        return list(range(home_k, 22))
    if config == 'HOME_BELOW_ABOVE':  return list(range(2, 22))
    raise ValueError(config)

CONFIG_N_BANDS = {
    'HOME_ONLY':         0,   # E = 1.00
    'HOME_BELOW':        1,   # E = 1.25
    'HOME_ABOVE':        1,   # E = 1.25
    'HOME_BELOW_ABOVE':  2,   # E = 1.50
}

# === Predictor (uses ara_framework's internal halves) ===
# Cache topology per anchor with the FULL rung range, then filter rungs
# at predict time — much faster than recomputing bandpass per config.
from dataclasses import replace as dc_replace
from ara_framework import Topology

def filter_topology(topo, allowed_ks):
    """Return a copy of topo with only the rungs whose k is in allowed_ks."""
    filtered = [r for r in topo.rungs if r['k'] in allowed_ks]
    return Topology(v_now=topo.v_now, mean_train=topo.mean_train,
                    home_k=topo.home_k, rungs=filtered)

def project_act(topo, h, rungs_k, partner_topo_at_home=None, host_std=None, partner_std=None):
    sub = filter_topology(topo, set(rungs_k))
    pred = _predict_act(sub, h)
    if partner_topo_at_home is not None and partner_topo_at_home.rungs:
        s = partner_topo_at_home.rungs[0]
        partner_delta = s['amp'] * (np.cos(s['theta'] + 2*np.pi*h/s['period']) - np.cos(s['theta']))
        scale = (host_std + 1e-9) / (partner_std + 1e-9)
        pred += -1.0 * partner_delta * scale * 0.5
    return pred

def project_old(topo, h, rungs_k):
    sub = filter_topology(topo, set(rungs_k))
    return _predict_old(sub, h)

# === Sweep horizons, find crossover ===
def find_crossover(arr, anchors, horizons, rungs_k, partner_arr=None, label='',
                    full_rungs=range(2, 22)):
    print(f"\n--- {label} ---")
    print(f"  rungs included: k={list(rungs_k)} (count: {len(rungs_k)})")
    if partner_arr is not None:
        print(f"  + same-rung partner at home_k={HOME_K}")

    # Cache topology per anchor once
    cached = {}
    for t_a in anchors:
        topo = extract_topology(arr, t=t_a, rungs_k=full_rungs, home_k=HOME_K)
        host_std = float(np.std(arr[:t_a])) + 1e-9
        partner_at_home = None
        partner_std = None
        if partner_arr is not None:
            partner_at_home = extract_topology(partner_arr, t=t_a, rungs_k=[HOME_K], home_k=HOME_K)
            partner_std = float(np.std(partner_arr[:t_a])) + 1e-9
        cached[t_a] = (topo, partner_at_home, host_std, partner_std)

    points = []
    for h in horizons:
        act_recs = []
        old_recs = []
        for t_a in anchors:
            if t_a + h - 1 >= len(arr): continue
            truth = float(arr[t_a + h - 1])
            topo, partner_at_home, host_std, partner_std = cached[t_a]
            act_recs.append((project_act(topo, h, rungs_k,
                                          partner_topo_at_home=partner_at_home,
                                          host_std=host_std, partner_std=partner_std), truth))
            old_recs.append((project_old(topo, h, rungs_k), truth))
        if len(act_recs) < 5: continue
        ap = np.array([r[0] for r in act_recs]); at = np.array([r[1] for r in act_recs])
        op = np.array([r[0] for r in old_recs]); ot = np.array([r[1] for r in old_recs])
        a_corr = float(np.corrcoef(ap, at)[0,1]) if np.std(ap) > 1e-9 else 0
        o_corr = float(np.corrcoef(op, ot)[0,1]) if np.std(op) > 1e-9 else 0
        points.append((h, a_corr, o_corr))
    # crossover by linear interp in log-h space
    cross_h = None
    for i in range(1, len(points)):
        prev_h, prev_a, prev_o = points[i-1]
        h, a, o = points[i]
        if (prev_a > prev_o) and (a <= o):
            d_prev = prev_a - prev_o; d_now = a - o
            frac = d_prev / (d_prev - d_now) if (d_prev - d_now) != 0 else 0.5
            log_cross = np.log(prev_h) + frac * (np.log(h) - np.log(prev_h))
            cross_h = float(np.exp(log_cross))
            break
    return cross_h, points

# === Run ablations ===
HOME_PERIOD = PHI ** HOME_K   # 47

# ENSO: anchors every 6 months from year 30, horizons 1..36
ENSO_ANCHORS = list(range(360, N_ENSO - 36, 6))
ENSO_HORIZONS = [1,2,3,4,5,6,8,10,12,15,18,21,24,28,32,36]
print(f"\n========== ENSO (home_period {HOME_PERIOD:.1f} mo) ==========")
print(f"  {len(ENSO_ANCHORS)} anchors")

enso_results = {}
for config, N_bands in CONFIG_N_BANDS.items():
    rungs = rungs_for_config(config)
    cross_h, pts = find_crossover(NINO, ENSO_ANCHORS, ENSO_HORIZONS, rungs, partner_arr=None,
                                    label=f'{config} (N={N_bands} bands, no SOI)')
    if cross_h:
        E_emp = float(np.log(cross_h / HOME_PERIOD) / np.log(PHI))
        E_pred = -(1 + 0.25 * N_bands)  # closed → negative side; ENSO closed
        print(f"  cross_h ≈ {cross_h:.2f} mo   |   E_emp={E_emp:+.3f}   E_pred={E_pred:+.3f}   diff={E_emp - E_pred:+.3f}")
    else:
        print(f"  no clean crossover")
        E_emp = None
    enso_results[config] = dict(N_bands=N_bands, cross_h=cross_h, points=pts, E_emp=E_emp)

# ENSO with SOI partner — N_bands += 1 (same-rung)
print(f"\n--- adding SOI same-rung partner to each ENSO config ---")
for config, N_bands in CONFIG_N_BANDS.items():
    rungs = rungs_for_config(config)
    cross_h, pts = find_crossover(NINO, ENSO_ANCHORS, ENSO_HORIZONS, rungs, partner_arr=SOI,
                                    label=f'{config} + SOI (N={N_bands+1} bands)')
    if cross_h:
        E_emp = float(np.log(cross_h / HOME_PERIOD) / np.log(PHI))
        E_pred = -(1 + 0.25 * (N_bands + 1))
        print(f"  cross_h ≈ {cross_h:.2f} mo   |   E_emp={E_emp:+.3f}   E_pred={E_pred:+.3f}   diff={E_emp - E_pred:+.3f}")
    else:
        print(f"  no clean crossover")
        E_emp = None
    enso_results[config + '+SOI'] = dict(N_bands=N_bands+1, cross_h=cross_h, points=pts, E_emp=E_emp)

# ECG (open, no same-rung partner available)
ECG_ANCHORS = list(range(20000, N_ECG - 4000, 5000))
ECG_HORIZONS = [1, 2, 3, 5, 8, 13, 21, 35, 50, 80, 130, 210, 350, 550, 900, 1500, 2500, 4000]
print(f"\n========== ECG (home_period {HOME_PERIOD:.1f} beats) ==========")
print(f"  {len(ECG_ANCHORS)} anchors")

ecg_results = {}
for config, N_bands in CONFIG_N_BANDS.items():
    rungs = rungs_for_config(config)
    cross_h, pts = find_crossover(RR, ECG_ANCHORS, ECG_HORIZONS, rungs, partner_arr=None,
                                    label=f'{config} (N={N_bands} bands)')
    if cross_h:
        E_emp = float(np.log(cross_h / HOME_PERIOD) / np.log(PHI))
        E_pred = +(1 + 0.25 * N_bands)
        print(f"  cross_h ≈ {cross_h:.2f} beats   |   E_emp={E_emp:+.3f}   E_pred={E_pred:+.3f}   diff={E_emp - E_pred:+.3f}")
    else:
        print(f"  no clean crossover")
        E_emp = None
    ecg_results[config] = dict(N_bands=N_bands, cross_h=cross_h, points=pts, E_emp=E_emp)

# === Summary ===
print(f"\n========== SUMMARY ==========")
print(f"  Hypothesis: crossover exponent E = ±(1 + 0.25 × N_bands)")
print(f"  {'system':>15}  {'config':>20}  {'N':>2}  {'cross_h':>10}  {'E_emp':>8}  {'E_pred':>8}  {'diff':>7}")
for sys_name, results in [('ENSO', enso_results), ('ECG', ecg_results)]:
    sign = -1 if sys_name == 'ENSO' else +1
    for config, info in results.items():
        if info['cross_h'] is None: continue
        E_pred = sign * (1 + 0.25 * info['N_bands'])
        E_emp = info['E_emp']
        diff = E_emp - E_pred
        print(f"  {sys_name:>15}  {config:>20}  {info['N_bands']:>2}  {info['cross_h']:>10.2f}  {E_emp:>+8.3f}  {E_pred:>+8.3f}  {diff:>+7.3f}")

with open(OUT, 'w') as f:
    f.write("window.NEIGHBOUR_ABLATION = " + json.dumps(dict(enso=enso_results, ecg=ecg_results), default=str) + ";\n")
print(f"\nSaved -> {OUT}")
