"""
phi_base_ablation_solar.py — repeat the φ-vs-bases ablation on solar sunspots.

Solar sunspot cycles are *intrinsic* (produced by the dynamo) rather than
externally-clocked. Per the substrate-vs-operating ARA hypothesis, this is
where φ should win more cleanly than on ENSO — no orbital octave to compete.

Same 8 bases. Both ACT-blend and pure-OLD regimes. SILSO monthly record (1749+).
"""
import os, sys, json, math
import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, REPO_ROOT)
from ara_framework import (
    Topology, causal_bandpass, _measure_rung,
    _predict_act, _predict_old,
)

PHI = (1 + 5**0.5) / 2

def extract_topology_with_base(data, t, rung_base, rungs_k, home_k, pin_factor=4):
    arr = np.asarray(data, dtype=float)
    if t < 5 or t > len(arr): return None
    v_now = float(arr[t - 1])
    mean_train = float(np.mean(arr[:t]))
    rungs = []
    for k in rungs_k:
        period = rung_base ** int(k)
        if period < 2 or pin_factor * period > t: continue
        bp = causal_bandpass(arr[:t], period)
        rec = _measure_rung(bp, period, k)
        if rec is not None: rungs.append(rec)
    return Topology(v_now=v_now, mean_train=mean_train, home_k=home_k, rungs=rungs)


def predict_act_blend(topo, h, rung_base, steepness=4.0):
    """ACT-OLD blend, same as canonical (closed=False)."""
    if topo is None: return float('nan')
    home_period = float(rung_base ** topo.home_k)
    h_cross = home_period * (rung_base ** (7 / 4))
    z = steepness * (h_cross - h) / max(h_cross, 1e-9)
    weight_act = 1.0 / (1.0 + math.exp(-z))
    return weight_act * _predict_act(topo, h) + (1 - weight_act) * _predict_old(topo, h)


def predict_old_only(topo, h, rung_base):
    """Pure OLD (no blend)."""
    if topo is None or not topo.rungs:
        return float('nan') if topo is None else topo.mean_train
    weights = np.array([rung_base ** (-abs(s['k'] - topo.home_k)) for s in topo.rungs])
    weights = weights / weights.sum()
    contrib = 0.0
    for j, s in enumerate(topo.rungs):
        new_th = s['theta'] + 2 * np.pi * h / s['period']
        contrib += weights[j] * s['amp'] * np.cos(new_th)
    return topo.mean_train + contrib


# ---------------- Load SILSO sunspot data ----------------
print("[1/4] Loading SILSO sunspot data ...")
SILSO_PATH = os.path.join(REPO_ROOT, 'SILSO_Solar/SN_m_tot_V2.0.csv')
# Format: year;month;decyear;monthly_value;std;n_obs;marker (semicolon-separated)
df = pd.read_csv(SILSO_PATH, sep=';', header=None,
                 names=['year', 'month', 'decyear', 'val', 'std', 'n_obs', 'marker'])
SUN = pd.to_numeric(df['val'], errors='coerce').dropna().values.astype(float)
SUN = SUN[SUN >= 0]  # drop -1 missing flags
print(f"  loaded {len(SUN)} months ({len(SUN)/12:.1f} years), range {SUN.min():.1f} to {SUN.max():.1f}")

BASES = [
    ('sqrt(2)', math.sqrt(2)),
    ('1.5',     1.5),
    ('1.6',     1.6),
    ('phi',     PHI),
    ('1.7',     1.7),
    ('e_alt',   1.7183),
    ('phi^1.05',PHI ** 1.05),
    ('2.0',     2.0),
]

HOME_PERIOD = 132.0   # 11 years = sunspot cycle
N_ANCHORS = 60
HORIZONS_ACT = [1, 6, 12, 60]    # short-mid range for ACT
HORIZONS_OLD = [6, 12, 60, 132, 264]   # mid-long for OLD (1 cycle, 2 cycles)

def score_base(rung_base, regime):
    """regime: 'act_blend' or 'pure_old'"""
    home_k = round(math.log(HOME_PERIOD) / math.log(rung_base))
    k_lo = max(2, int(math.log(3.0) / math.log(rung_base)))
    k_hi = int(math.log(720.0) / math.log(rung_base)) + 1   # up to ~60 years
    rungs_k = list(range(k_lo, k_hi + 1))

    horizons = HORIZONS_ACT if regime == 'act_blend' else HORIZONS_OLD
    n = len(SUN)
    test_start = max(600, n - 100 * 12)   # last 100 years for test
    anchor_idxs = np.linspace(test_start, n - max(horizons) - 1, N_ANCHORS).astype(int)

    out = {h: {'preds': [], 'truths': []} for h in horizons}
    persistence_preds = {h: [] for h in horizons}
    mean_baseline_preds = {h: [] for h in horizons}

    for t in anchor_idxs:
        topo = extract_topology_with_base(SUN, t, rung_base, rungs_k, home_k)
        if topo is None: continue
        for h in horizons:
            if t + h >= n: continue
            if regime == 'act_blend':
                pred = predict_act_blend(topo, h, rung_base)
            else:
                pred = predict_old_only(topo, h, rung_base)
            truth = float(SUN[t + h - 1])
            if not np.isfinite(pred): continue
            out[h]['preds'].append(pred)
            out[h]['truths'].append(truth)
            persistence_preds[h].append(float(SUN[t - 1]))
            mean_baseline_preds[h].append(topo.mean_train)

    metrics = {}
    for h in horizons:
        p = np.array(out[h]['preds'])
        T = np.array(out[h]['truths'])
        per = np.array(persistence_preds[h][:len(p)])
        meanp = np.array(mean_baseline_preds[h][:len(p)])
        if len(p) < 5:
            metrics[h] = dict(n=len(p))
            continue
        mae = float(np.mean(np.abs(p - T)))
        corr = float(np.corrcoef(p, T)[0, 1]) if T.std() > 0 and p.std() > 0 else float('nan')
        per_mae = float(np.mean(np.abs(per - T)))
        mean_mae = float(np.mean(np.abs(meanp - T)))
        metrics[h] = dict(
            n=len(p), mae=round(mae, 2), corr=round(corr, 3),
            per_mae=round(per_mae, 2), mean_mae=round(mean_mae, 2),
            skill_per=round(1 - mae/per_mae, 3) if per_mae > 0 else None,
            skill_mean=round(1 - mae/mean_mae, 3) if mean_mae > 0 else None,
            home_k=int(home_k), n_rungs=len(rungs_k))
    return metrics


print("[2/4] Running ACT-blend ablation on solar ...")
act_results = {}
for name, base in BASES:
    print(f"  base={name:>10} ({base:.4f})")
    act_results[name] = dict(base=base, scores=score_base(base, 'act_blend'))

print()
print("[3/4] Running pure-OLD ablation on solar ...")
old_results = {}
for name, base in BASES:
    old_results[name] = dict(base=base, scores=score_base(base, 'pure_old'))

# ---------- Print summaries ----------
def print_summary(results, regime_name, horizons):
    print()
    print(f"=== Solar {regime_name} ({len(BASES)} bases × {len(horizons)} horizons) ===")
    print(f"{'base':>10} | {'h':>3} | {'MAE':>5} | {'corr':>6} | {'persMAE':>7} | {'meanMAE':>7} | {'skill_p':>8} | {'skill_m':>8}")
    print('-' * 95)
    for name, info in results.items():
        for h, m in info['scores'].items():
            if 'mae' not in m: continue
            sp = f"{m['skill_per']:>+8.3f}" if m['skill_per'] is not None else "       —"
            sm = f"{m['skill_mean']:>+8.3f}" if m['skill_mean'] is not None else "       —"
            print(f"{name:>10} | {h:>3} | {m['mae']:>5.1f} | {m['corr']:>+6.3f} | "
                  f"{m['per_mae']:>7.1f} | {m['mean_mae']:>7.1f} | {sp} | {sm}")
        print()

    print(f"--- per-horizon winner under {regime_name} ---")
    for h in horizons:
        ranked = sorted(
            [(n, info['scores'].get(h, {}).get('mae', float('inf'))) for n, info in results.items()],
            key=lambda x: x[1])
        phi_idx = next((i for i, (n, _) in enumerate(ranked) if n == 'phi'), None)
        winner, winner_mae = ranked[0]
        phi_mae = ranked[phi_idx][1] if phi_idx is not None else float('nan')
        print(f"  h={h:>3} mo: best={winner:>10} (MAE {winner_mae:.1f}), φ rank {phi_idx+1 if phi_idx is not None else '-'}/8 (MAE {phi_mae:.1f})")

print_summary(act_results, "ACT-blend", HORIZONS_ACT)
print_summary(old_results, "pure-OLD", HORIZONS_OLD)

# ---------- Save ----------
OUT = os.path.join(_HERE, 'phi_base_ablation_solar_data.js')
with open(OUT, 'w') as f:
    f.write("window.PHI_BASE_ABLATION_SOLAR = " + json.dumps(dict(
        domain='solar_sunspots_silso',
        n_months=int(len(SUN)),
        home_period_months=HOME_PERIOD,
        bases=[dict(name=n, value=b) for n, b in BASES],
        horizons_act=HORIZONS_ACT,
        horizons_old=HORIZONS_OLD,
        act_blend_results=act_results,
        pure_old_results=old_results,
    ), default=str) + ";\n")
print(f"\n[4/4] Saved -> {OUT}")
