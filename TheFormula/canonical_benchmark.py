"""
canonical_benchmark.py — verify ara_framework's canonical predict() against
ACT-only and OLD-only baselines, on both ENSO (closed) and ECG (open).

The released formula is the BLEND. We want to show:
  - BLEND ≥ max(ACT, OLD) at every horizon, OR
  - BLEND ≈ ACT short, BLEND ≈ OLD long, smoothly transitioning at h_cross.
"""
import sys, os, json, time
sys.path.insert(0, '/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder')
from ara_framework import extract_topology, predict_components, _predict_act, _predict_old, PHI
import numpy as np, pandas as pd
import wfdb

OUT = '/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder/TheFormula/canonical_benchmark_data.js'

# ===== Load ENSO =====
print("Loading NINO 3.4...")
df = pd.read_csv('/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder/Nino34/nino34.long.anom.csv',
                 skiprows=1, header=None, names=['date','val'])
df['date'] = pd.to_datetime(df['date'].str.strip())
df = df[df['val'] > -90].copy()
nino = df.set_index('date')['val'].astype(float)
nino.index = pd.to_datetime(nino.index).to_period('M').to_timestamp()
NINO = nino.groupby(nino.index).first().values.astype(float)
N_NINO = len(NINO)

# ===== Load ECG =====
print("Loading ECG nsr001...")
ann = wfdb.rdann('/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder/normal-sinus-rhythm-rr-interval-database-1.0.0/nsr001', 'ecg')
RR = (np.diff(ann.sample) / ann.fs * 1000).astype(float)
N_ECG = len(RR)
print(f"  ENSO: {N_NINO} months   ECG: {N_ECG} beats")

def benchmark(arr, anchors, horizons, rungs_k, closed, label):
    print(f"\n=== {label} (closed={closed}) ===")
    res = {h: dict(act=[], old=[], blend=[]) for h in horizons}
    for t_a in anchors:
        topo = extract_topology(arr, t=t_a, rungs_k=rungs_k, home_k=8)
        for h in horizons:
            if t_a + h - 1 >= len(arr): continue
            truth = float(arr[t_a + h - 1])
            c = predict_components(topo, h, closed=closed)
            res[h]['act'].append((c['act'], truth, float(arr[t_a-1])))
            res[h]['old'].append((c['old'], truth, float(arr[t_a-1])))
            res[h]['blend'].append((c['prediction'], truth, float(arr[t_a-1])))
    out = {}
    print(f"  {'h':>4}  {'method':>5}  {'corr':>7}  {'MAE':>7}  {'R2(pers)':>9}  n")
    for h in horizons:
        h_metrics = {}
        for method in ['act','old','blend']:
            recs = res[h][method]
            if len(recs) < 5: continue
            preds = np.array([r[0] for r in recs])
            truths = np.array([r[1] for r in recs])
            pers = np.array([r[2] for r in recs])
            c = float(np.corrcoef(preds, truths)[0,1]) if np.std(preds)>1e-9 else 0
            mae = float(np.mean(np.abs(preds - truths)))
            r2p = float(1 - np.sum((truths-preds)**2)/np.sum((truths-pers)**2))
            print(f"  {h:>4}  {method:>5}  {c:+.3f}    {mae:.3f}    {r2p:>+.3f}    {len(recs)}")
            h_metrics[method] = dict(corr=c, mae=mae, r2p=r2p, n=int(len(recs)))
        out[h] = h_metrics
    return out

# Benchmark ENSO
ENSO_HORIZONS = [1, 3, 6, 12, 24, 36, 60]
ENSO_ANCHORS = list(range(360, N_NINO - max(ENSO_HORIZONS), 6))   # 6-month STEP for speed
t0 = time.time()
enso_results = benchmark(NINO, ENSO_ANCHORS, ENSO_HORIZONS,
                          rungs_k=range(3, 13), closed=True, label='ENSO')
print(f"  ran in {time.time()-t0:.1f}s, {len(ENSO_ANCHORS)} anchors")

# Benchmark ECG
ECG_HORIZONS = [1, 3, 10, 30, 100, 300, 1000, 3000]
ECG_ANCHORS = list(range(20000, N_ECG - max(ECG_HORIZONS), 5000))
t0 = time.time()
ecg_results = benchmark(RR, ECG_ANCHORS, ECG_HORIZONS,
                         rungs_k=range(2, 22), closed=False, label='ECG (nsr001)')
print(f"  ran in {time.time()-t0:.1f}s, {len(ECG_ANCHORS)} anchors")

with open(OUT, 'w') as f:
    f.write("window.CANONICAL = " + json.dumps(dict(enso=enso_results, ecg=ecg_results), default=str) + ";\n")
print(f"\nSaved -> {OUT}")
