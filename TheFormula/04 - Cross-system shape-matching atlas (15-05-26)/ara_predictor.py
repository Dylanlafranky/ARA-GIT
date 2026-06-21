#!/usr/bin/env python3
"""
ara_predictor.py — predict future values of a time series under the ARA framework.

Uses the canonical predictor (ACT/OLD blend) anchored at the most recent
observation. Optionally loads a mapper JSON to skip re-mapping.

Usage:
    python ara_predictor.py path/to/data.csv [--col VALUE_COL]
                                              [--horizons 1,3,6,12,24,60]
                                              [--mapper-json mapper.json]
                                              [--closed]
                                              [--out predictions.json]

Output: JSON with predictions at each horizon plus ACT/OLD components.
"""
import os, sys, json, math, argparse
import numpy as np
from scipy.signal import butter, sosfilt, find_peaks
from scipy.ndimage import gaussian_filter1d

# Import from ara_mapper for consistency
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ara_mapper import (PHI, causal_bandpass, measure_rung_ara,
                        measure_rung_amplitude, detect_dominant_period,
                        classify_ara, map_system)

CROSSOVER_EXPONENT = 7.0 / 4.0  # 1.75 — framework constant


# ---------- Topology extraction ----------
def extract_topology(data, rungs_k, home_k, pin_factor=4):
    """Build per-rung records (period, amp, theta) from training data."""
    arr = np.asarray(data, dtype=float)
    if len(arr) < 5:
        return None
    v_now = float(arr[-1])
    mean_train = float(np.mean(arr))
    rungs = []
    for k in rungs_k:
        period = PHI ** int(k)
        if period < 2 or pin_factor * period > len(arr):
            continue
        bp = causal_bandpass(arr, period)
        p_int = max(2, int(period))
        if len(bp) < 2*p_int + 5:
            continue
        last_cycle = bp[-p_int:]
        amp = float((np.max(last_cycle) - np.min(last_cycle)) / 2.0)
        if amp < 1e-9: continue
        v_recent = float(bp[-1]); v_prev = float(bp[-2])
        norm_v = max(amp, 1e-9)
        ratio = max(-0.99, min(0.99, v_recent / norm_v))
        theta = float(np.arccos(ratio) * (-1.0 if (v_recent - v_prev) > 0 else 1.0))
        rungs.append(dict(k=int(k), period=float(period), amp=amp, theta=theta))
    return dict(v_now=v_now, mean_train=mean_train, home_k=home_k, rungs=rungs)


# ---------- ACT / OLD predictors ----------
def predict_act(topo, h):
    """v(h) = v_now + Σ amp × (cos(θ + 2π·h/p) − cos(θ))."""
    if not topo['rungs']: return topo['v_now']
    delta = sum(r['amp'] * (math.cos(r['theta'] + 2*math.pi*h/r['period']) - math.cos(r['theta']))
                for r in topo['rungs'])
    return topo['v_now'] + delta


def predict_old(topo, h):
    """v(h) = mean + Σ w_k × amp × cos(θ + 2π·h/p),  w_k = φ^(-|k-home_k|), normed."""
    if not topo['rungs']: return topo['mean_train']
    weights = np.array([PHI ** (-abs(r['k'] - topo['home_k'])) for r in topo['rungs']])
    weights = weights / weights.sum()
    contrib = sum(w * r['amp'] * math.cos(r['theta'] + 2*math.pi*h/r['period'])
                  for w, r in zip(weights, topo['rungs']))
    return topo['mean_train'] + contrib


def predict_canonical(topo, h, closed=False, blend_steepness=2.0):
    """Sigmoid-blended ACT/OLD prediction."""
    home_period = PHI ** topo['home_k']
    sign = -1.0 if closed else +1.0
    cross_h = home_period * (PHI ** (sign * CROSSOVER_EXPONENT))
    z = blend_steepness * (cross_h - h) / max(cross_h, 1e-9)
    weight_act = 1.0 / (1.0 + math.exp(-z))
    p_act = predict_act(topo, h)
    p_old = predict_old(topo, h)
    blended = weight_act * p_act + (1.0 - weight_act) * p_old
    return dict(prediction=blended, act=p_act, old=p_old,
                weight_act=weight_act, crossover_h=cross_h)


# ---------- CLI ----------
def main():
    ap = argparse.ArgumentParser(description='ARA framework predictor')
    ap.add_argument('csv', help='Path to CSV with time-series data')
    ap.add_argument('--col', default=None, help='Column name or index')
    ap.add_argument('--horizons', default='1,3,6,12,24,60,120',
                    help='Comma-separated horizons (in samples)')
    ap.add_argument('--closed', action='store_true',
                    help='System has matched-rung partner (uses negative crossover)')
    ap.add_argument('--mapper-json', default=None,
                    help='Pre-computed mapper output (skips re-mapping)')
    ap.add_argument('--out', default=None, help='Output JSON path')
    args = ap.parse_args()

    import pandas as pd
    df = pd.read_csv(args.csv)
    if args.col is None:
        col = df.select_dtypes(include='number').columns[0]
    elif args.col.isdigit():
        col = df.columns[int(args.col)]
    else:
        col = args.col
    data = df[col].dropna().values
    print(f"Loaded {len(data)} samples from {args.csv} (column: {col})")

    # Load or compute mapping
    if args.mapper_json:
        with open(args.mapper_json) as f:
            mapping = json.load(f)
        print(f"  Using pre-computed mapping from {args.mapper_json}")
    else:
        print(f"  Running mapper...")
        mapping = map_system(data)
    if 'error' in mapping:
        print(f"ERROR: {mapping['error']}"); return

    home_k = mapping['home_k']
    rung_ks = [r['k'] for r in mapping['rung_breakdown'] if r['valid']]
    if not rung_ks:
        print("ERROR: no valid rungs"); return

    # Extract topology from full data
    topo = extract_topology(data, rung_ks, home_k)
    if topo is None:
        print("ERROR: could not extract topology"); return

    horizons = [int(h) for h in args.horizons.split(',')]
    print(f"\n  Generating predictions at horizons {horizons} (samples)...")
    print(f"  Crossover horizon: {(PHI**home_k) * (PHI**(-CROSSOVER_EXPONENT if args.closed else CROSSOVER_EXPONENT)):.1f} samples")
    print()

    predictions = []
    for h in horizons:
        c = predict_canonical(topo, h, closed=args.closed)
        predictions.append(dict(horizon=int(h), **{k: float(v) for k, v in c.items()}))

    # Pretty print
    print(f"  {'h':>5} {'ACT':>10} {'OLD':>10} {'BLEND':>10} {'w_act':>7}")
    print('-' * 55)
    for p in predictions:
        print(f"  {p['horizon']:>5} {p['act']:>10.3f} {p['old']:>10.3f} "
              f"{p['prediction']:>10.3f} {p['weight_act']:>7.3f}")

    print(f"\n  Current value (anchor): {topo['v_now']:.3f}")
    print(f"  Training mean: {topo['mean_train']:.3f}")

    out_path = args.out or os.path.splitext(args.csv)[0] + '_predictions.json'
    with open(out_path, 'w') as f:
        json.dump(dict(
            source_file=args.csv,
            source_column=col,
            n_samples=len(data),
            home_k=int(home_k),
            home_period=float(PHI**home_k),
            v_now=topo['v_now'],
            mean_train=topo['mean_train'],
            closed=bool(args.closed),
            crossover_horizon=float((PHI**home_k) * (PHI**(-CROSSOVER_EXPONENT if args.closed else CROSSOVER_EXPONENT))),
            mapping_summary=dict(
                system_class=mapping.get('system_class'),
                system_mean_ara=mapping.get('system_mean_ara'),
                ara_of_ara=mapping.get('ara_of_ara'),
                dominant_period=mapping.get('dominant_period_samples'),
            ),
            predictions=predictions,
            phi=PHI,
        ), f, indent=2, default=str)
    print(f"\n  Saved -> {out_path}")


if __name__ == '__main__':
    main()
