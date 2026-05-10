"""
phi_base_ablation.py — does the canonical predictor specifically need φ?

Test: run the canonical predictor with rung_base ∈ {sqrt(2), 1.5, 1.6, φ, 1.7, e, 2}.
Use the same home period in months (so the predictor is "tuned" the same way),
just change which other rungs (faster/slower neighbours) get included.

If φ wins clearly: that's a defense against the "any log base would work" objection.
If φ ties or loses: that's a critical thing to know — the framework's structural claim weakens.
"""
import os, sys, json, math
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfilt

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, REPO_ROOT)
from ara_framework import (
    Topology, causal_bandpass, _measure_rung,
    _predict_act, _predict_old, crossover_horizon
)

PHI = (1 + 5**0.5) / 2

# ---------------- Generic predictor with arbitrary base ----------------
def extract_topology_with_base(data, t, rung_base, rungs_k, home_k, pin_factor=4):
    """Same as ara_framework.extract_topology, but the rung period is base^k."""
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


def predict_with_base(topo, h, rung_base, closed=False, steepness=4.0):
    """Canonical predictor blend, parameterised by rung_base for the home_period."""
    if topo is None:
        return float('nan')
    home_period = float(rung_base ** topo.home_k)
    if closed:
        h_cross = home_period * (rung_base ** (-7 / 4))
    else:
        h_cross = home_period * (rung_base ** (7 / 4))
    z = steepness * (h_cross - h) / max(h_cross, 1e-9)
    weight_act = 1.0 / (1.0 + math.exp(-z))
    return weight_act * _predict_act(topo, h) + (1 - weight_act) * _predict_old(topo, h)


# ---------------- Load ENSO ----------------
print("[1/4] Loading ENSO data ...")
df = pd.read_csv(os.path.join(REPO_ROOT, 'Nino34/nino34.long.anom.csv'),
                 skiprows=1, names=['date', 'val'], header=None, sep=',', engine='python')
NINO = pd.to_numeric(df['val'], errors='coerce').dropna().values.astype(float)
NINO = NINO[NINO > -50]  # drop -99.99 missing-value flags
print(f"  loaded {len(NINO)} months of ENSO data")

# ---------------- Define bases to compare ----------------
BASES = [
    ('sqrt(2)', math.sqrt(2)),    # 1.414
    ('1.5',     1.5),
    ('1.6',     1.6),
    ('phi',     PHI),              # 1.618
    ('1.7',     1.7),
    ('e/2*1',   1.7183),           # 1.718, ~e but adjusted
    ('phi^1.05', PHI ** 1.05),     # 1.66 — close cousin to phi
    ('2.0',     2.0),
]

# Home period in months: ENSO ground cycle ~47 months (4 years)
HOME_PERIOD_MONTHS = 47.0
# Anchors: 76 evenly-spaced points across last 30 years of data
N_ANCHORS = 60
HORIZONS = [1, 3, 6, 12]

def score_base(base_name, rung_base, NINO):
    home_k = round(math.log(HOME_PERIOD_MONTHS) / math.log(rung_base))
    # Choose rungs_k so periods cover ~3 months to ~30 years
    # base^k_lo ≈ 3 → k_lo = log(3)/log(base)
    # base^k_hi ≈ 360 → k_hi = log(360)/log(base)
    k_lo = max(2, int(math.log(3.0) / math.log(rung_base)))
    k_hi = int(math.log(360.0) / math.log(rung_base)) + 1
    rungs_k = list(range(k_lo, k_hi + 1))

    n = len(NINO)
    test_start = n - 30 * 12   # last 30 years for testing
    if test_start < 240:
        test_start = 240
    anchor_idxs = np.linspace(test_start, n - max(HORIZONS) - 1, N_ANCHORS).astype(int)

    out = {h: {'preds': [], 'truths': []} for h in HORIZONS}
    persistence_preds = {h: [] for h in HORIZONS}

    for t in anchor_idxs:
        topo = extract_topology_with_base(NINO, t, rung_base, rungs_k, home_k)
        if topo is None:
            continue
        for h in HORIZONS:
            if t + h >= n: continue
            pred = predict_with_base(topo, h, rung_base, closed=False)
            truth = float(NINO[t + h - 1])
            if not np.isfinite(pred): continue
            out[h]['preds'].append(pred)
            out[h]['truths'].append(truth)
            persistence_preds[h].append(float(NINO[t - 1]))  # current value as next-month prediction

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
        skill = 1 - mae / per_mae if per_mae > 0 else float('nan')
        metrics[h] = dict(n=len(p), mae=round(mae, 3), corr=round(corr, 3),
                          per_mae=round(per_mae, 3), skill_vs_per=round(skill, 3),
                          home_k=int(home_k), n_rungs=len(rungs_k))
    return metrics


# ---------------- Run ablation ----------------
print("[2/4] Running ENSO ablation across bases ...")
results = {}
for name, base in BASES:
    print(f"  base={name:>10} ({base:.4f})")
    results[name] = dict(base=base, scores=score_base(name, base, NINO))

# ---------------- Print summary ----------------
print()
print("[3/4] ENSO ablation summary (last 30y, 60 anchors per base):")
print(f"{'base':>10} | {'h':>2} | {'n':>3} | {'MAE':>6} | {'corr':>6} | {'persMAE':>8} | {'skill':>6} | rungs")
print('-' * 78)
for name, info in results.items():
    for h, m in info['scores'].items():
        if 'mae' not in m:
            continue
        print(f"{name:>10} | {h:>2} | {m['n']:>3} | {m['mae']:>6.3f} | "
              f"{m['corr']:>6.3f} | {m['per_mae']:>8.3f} | {m['skill_vs_per']:>+6.3f} | "
              f"k={m['home_k']}, n_rungs={m['n_rungs']}")
    print()

# ---------------- Save ----------------
OUT = os.path.join(_HERE, 'phi_base_ablation_data.js')
with open(OUT, 'w') as f:
    f.write("window.PHI_BASE_ABLATION = " + json.dumps(dict(
        bases=[dict(name=n, value=b) for n, b in BASES],
        home_period_months=HOME_PERIOD_MONTHS,
        horizons=HORIZONS,
        results=results,
    ), default=str) + ";\n")
print(f"\nSaved -> {OUT}")

# Brief verdict
print("\n[4/4] Phi vs nearest rivals at h=1 mo (lower MAE = better):")
sorted_h1 = sorted(
    [(n, info['scores'][1].get('mae', float('inf'))) for n, info in results.items()],
    key=lambda x: x[1])
for name, mae in sorted_h1:
    marker = " ← phi" if name == 'phi' else ''
    print(f"  {name:>10}  MAE={mae:.3f}{marker}")
