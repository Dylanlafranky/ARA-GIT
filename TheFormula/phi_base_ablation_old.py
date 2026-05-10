"""
phi_base_ablation_old.py — companion to phi_base_ablation.py, but force pure-OLD regime.

The earlier ablation showed φ wins at h=1, 3, 6, 12 months among ACT-regime
predictions. But for ENSO with home_period=47 and `closed=False`, the sigmoid
crossover sits at h ≈ 100 months — so the OLD regime ("structured wave from
training mean") never engages in that horizon range.

This test runs PURE-OLD predictions at:
  (a) the same short horizons 1, 3, 6, 12 (so we can compare directly to ACT)
  (b) long horizons 24, 60, 120 (where OLD would naturally dominate)

Question: does φ still win under OLD? If yes, that's evidence the rung-base
choice matters across both regimes. If a different base wins under OLD, that
tells us the regime-specific tuning matters.
"""
import os, sys, json, math
import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, REPO_ROOT)
from ara_framework import (
    Topology, causal_bandpass, _measure_rung, _predict_old,
)

PHI = (1 + 5**0.5) / 2

def extract_topology_with_base(data, t, rung_base, rungs_k, home_k, pin_factor=4):
    arr = np.asarray(data, dtype=float)
    if t < 5 or t > len(arr):
        return None
    v_now = float(arr[t - 1])
    mean_train = float(np.mean(arr[:t]))
    rungs = []
    for k in rungs_k:
        period = rung_base ** int(k)
        if period < 2 or pin_factor * period > t:
            continue
        bp = causal_bandpass(arr[:t], period)
        rec = _measure_rung(bp, period, k)
        if rec is not None:
            rungs.append(rec)
    return Topology(v_now=v_now, mean_train=mean_train, home_k=home_k, rungs=rungs)


def predict_old_only(topo, h, rung_base):
    """Pure OLD regime — no sigmoid blend, just structured wave from training mean.
       v(h) = mean + Σ w_k × amp × cos(θ + 2π·h/p)  with  w_k = base^(-|k - home_k|)"""
    if topo is None or not topo.rungs:
        return float('nan') if topo is None else topo.mean_train
    weights = np.array([rung_base ** (-abs(s['k'] - topo.home_k)) for s in topo.rungs])
    weights = weights / weights.sum()
    contrib = 0.0
    for j, s in enumerate(topo.rungs):
        new_th = s['theta'] + 2 * np.pi * h / s['period']
        contrib += weights[j] * s['amp'] * np.cos(new_th)
    return topo.mean_train + contrib


# Load ENSO
print("[1/4] Loading ENSO data ...")
df = pd.read_csv(os.path.join(REPO_ROOT, 'Nino34/nino34.long.anom.csv'),
                 skiprows=1, names=['date', 'val'], header=None, sep=',', engine='python')
NINO = pd.to_numeric(df['val'], errors='coerce').dropna().values.astype(float)
NINO = NINO[NINO > -50]
print(f"  loaded {len(NINO)} months")

BASES = [
    ('sqrt(2)', math.sqrt(2)),
    ('1.5',     1.5),
    ('1.6',     1.6),
    ('phi',     PHI),
    ('1.7',     1.7),
    ('e',       math.e / 1.5797),  # ~1.7183, but let me use the same e cousin as before
    ('phi^1.05',PHI ** 1.05),
    ('2.0',     2.0),
]

HOME_PERIOD = 47.0
N_ANCHORS = 60
HORIZONS = [1, 3, 6, 12, 24, 60, 120]

def score_base(rung_base):
    home_k = round(math.log(HOME_PERIOD) / math.log(rung_base))
    k_lo = max(2, int(math.log(3.0) / math.log(rung_base)))
    k_hi = int(math.log(360.0) / math.log(rung_base)) + 1
    rungs_k = list(range(k_lo, k_hi + 1))

    n = len(NINO)
    test_start = max(240, n - 30 * 12)
    anchor_idxs = np.linspace(test_start, n - max(HORIZONS) - 1, N_ANCHORS).astype(int)

    out = {h: {'preds': [], 'truths': []} for h in HORIZONS}
    persistence_preds = {h: [] for h in HORIZONS}

    for t in anchor_idxs:
        topo = extract_topology_with_base(NINO, t, rung_base, rungs_k, home_k)
        if topo is None:
            continue
        for h in HORIZONS:
            if t + h >= n: continue
            pred = predict_old_only(topo, h, rung_base)
            truth = float(NINO[t + h - 1])
            if not np.isfinite(pred): continue
            out[h]['preds'].append(pred)
            out[h]['truths'].append(truth)
            persistence_preds[h].append(float(NINO[t - 1]))

    metrics = {}
    for h in HORIZONS:
        p = np.array(out[h]['preds'])
        T = np.array(out[h]['truths'])
        per = np.array(persistence_preds[h][:len(p)])
        if len(p) < 5:
            metrics[h] = dict(n=len(p))
            continue
        mae = float(np.mean(np.abs(p - T)))
        if T.std() > 0 and p.std() > 0:
            corr = float(np.corrcoef(p, T)[0, 1])
        else:
            corr = float('nan')
        per_mae = float(np.mean(np.abs(per - T)))
        # Mean baseline (predict the climatology mean instead of last value)
        mean_baseline_mae = float(np.mean(np.abs(np.zeros_like(T) - T)))  # zeros = anomaly mean
        metrics[h] = dict(n=len(p), mae=round(mae, 3), corr=round(corr, 3),
                          per_mae=round(per_mae, 3),
                          skill_vs_per=round(1 - mae/per_mae, 3) if per_mae > 0 else None,
                          mean_baseline_mae=round(mean_baseline_mae, 3),
                          skill_vs_mean=round(1 - mae/mean_baseline_mae, 3) if mean_baseline_mae > 0 else None,
                          home_k=int(home_k), n_rungs=len(rungs_k))
    return metrics


print("[2/4] Running pure-OLD ablation across bases ...")
results = {}
for name, base in BASES:
    print(f"  base={name:>10} ({base:.4f})")
    results[name] = dict(base=base, scores=score_base(base))

print()
print("[3/4] Pure-OLD ENSO ablation summary (60 anchors, 30y test):")
print(f"{'base':>10} | {'h':>3} | {'n':>3} | {'MAE':>6} | {'corr':>6} | {'persMAE':>8} | {'meanMAE':>8} | {'skill_per':>9} | {'skill_mean':>10}")
print('-' * 110)
for name, info in results.items():
    for h, m in info['scores'].items():
        if 'mae' not in m: continue
        print(f"{name:>10} | {h:>3} | {m['n']:>3} | {m['mae']:>6.3f} | {m['corr']:>6.3f} | "
              f"{m['per_mae']:>8.3f} | {m['mean_baseline_mae']:>8.3f} | "
              f"{m['skill_vs_per']:>+9.3f} | {m['skill_vs_mean']:>+10.3f}")
    print()

print("[4/4] Per-horizon winner under OLD:")
print(f"{'horizon':>8} | {'best base':>12} | {'best MAE':>9} | {'φ MAE':>7} | {'φ rank':>7}")
print('-' * 60)
for h in HORIZONS:
    by_base = []
    for name, info in results.items():
        m = info['scores'].get(h, {})
        if 'mae' in m:
            by_base.append((name, m['mae']))
    by_base.sort(key=lambda x: x[1])
    if not by_base: continue
    phi_idx = next((i for i, (n, _) in enumerate(by_base) if n == 'phi'), None)
    phi_mae = by_base[phi_idx][1] if phi_idx is not None else float('nan')
    print(f"{h:>8} | {by_base[0][0]:>12} | {by_base[0][1]:>9.3f} | {phi_mae:>7.3f} | "
          f"{phi_idx+1 if phi_idx is not None else '-':>7}/{len(by_base)}")

OUT = os.path.join(_HERE, 'phi_base_ablation_old_data.js')
with open(OUT, 'w') as f:
    f.write("window.PHI_BASE_ABLATION_OLD = " + json.dumps(dict(
        bases=[dict(name=n, value=b) for n, b in BASES],
        home_period_months=HOME_PERIOD,
        horizons=HORIZONS,
        results=results,
        regime='pure_OLD',
    ), default=str) + ";\n")
print(f"\nSaved -> {OUT}")
