#!/usr/bin/env python3
"""
ara_predictor.py — forecast a time series under the ARA framework (current standard).

Runs the validated STRICT-CAUSAL LAYERED OPERATOR (the "one operator, three input
adapters" method) and scores it out-of-sample against a persistence baseline at every
horizon — exactly the procedure behind the published solar / ENSO / heart numbers.
No future samples are ever used: features at origin t come only from samples <= t;
the model is fit on the first 1/phi (61.8%, the golden handover) and scored on the shed 38.2%.

Usage:
    # Self-forecast from a single column (like the solar flywheel result):
    python ara_predictor.py data.csv --col VALUE --home-period 132 --horizons 12,24,48,96,132

    # Full forecast with real external drivers (reproduces e.g. the ENSO result):
    python ara_predictor.py enso.csv --col NINO34 --home-period 48 \
        --feeders SOI:3,WWV_W:6,WWV_E:6,IOD:6 --upper PDO:60 --horizons 3,6,12,18,24

Feeder syntax:  COLUMN:PERIOD  (period in samples; the contact window defaults to the period).
Output: per-horizon corr/MAE for persistence and for the framework models, plus a JSON file.

The framework EARNS its keep when 'home+ara' (framework features + ordinary causal memory)
beats persistence. The parameter-free 'ara_fixed_roll' alone is usually weaker than
persistence — that is expected and reported honestly.

Author: Dylan La Franchi (with Claude). Engine: ara_framework.run_forecast.
"""
import os, sys, json, argparse
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ara_framework as F


def _parse_feeders(spec):
    """'SOI:3,WWV:6' -> [(name, period), ...]"""
    out = []
    if not spec:
        return out
    for part in spec.split(','):
        if ':' not in part:
            raise ValueError(f"feeder '{part}' must be COLUMN:PERIOD")
        col, per = part.rsplit(':', 1)
        out.append((col.strip(), float(per)))
    return out


def main():
    ap = argparse.ArgumentParser(description='ARA framework forecaster (strict-causal layered operator)')
    ap.add_argument('csv', help='CSV with time-series data')
    ap.add_argument('--col', default=None, help='Target column name or index')
    ap.add_argument('--home-period', type=float, default=None,
                    help="System's home period in samples (e.g. solar=132, ENSO=48, heartbeat=8). "
                         "If omitted, it is auto-detected by FFT.")
    ap.add_argument('--horizons', default=None,
                    help='Comma-separated forecast horizons in samples (default: scaled to home period)')
    ap.add_argument('--feeders', default=None,
                    help='Lower (faster) driver columns as COLUMN:PERIOD,COLUMN:PERIOD')
    ap.add_argument('--upper', default=None,
                    help='Upper (slower) driver columns as COLUMN:PERIOD,COLUMN:PERIOD')
    ap.add_argument('--out', default=None, help='Output JSON path')
    args = ap.parse_args()

    import pandas as pd
    df = pd.read_csv(args.csv)

    def pick(c):
        if c is None:
            return df.select_dtypes(include='number').columns[0]
        return df.columns[int(c)] if str(c).isdigit() else c

    tcol = pick(args.col)
    home = df[tcol].astype(float).values
    home = home[np.isfinite(home)]
    print(f"Loaded {len(home)} samples from {args.csv} (target column: {tcol})")

    # home period
    P = args.home_period
    if P is None:
        P = F.detect_dominant_period(home) if hasattr(F, 'detect_dominant_period') else None
        if P is None:
            from ara_mapper import detect_dominant_period
            P = detect_dominant_period(home)
        print(f"  Auto-detected home period: {P:.1f} samples (pass --home-period to override)")
    P = float(P)

    horizons = tuple(int(h) for h in args.horizons.split(',')) if args.horizons else None

    # build system (self-feeder or full)
    lower = _parse_feeders(args.feeders)
    upper = _parse_feeders(args.upper)
    if lower or upper:
        lf = [(nm, df[pick(nm)].astype(float).values[:len(home)], per, max(2, int(per))) for nm, per in lower]
        uf = [(nm, df[pick(nm)].astype(float).values[:len(home)], per, max(2, int(per))) for nm, per in upper]
        if not uf:  # need at least one upper for the operator; derive a slow envelope of home
            uf = [("slow envelope", home, P * 2, max(2, int(P)))]
        if not lf:
            lf = [("micro-spin", home, max(3.0, P / 12), max(3, int(P / 12) or 3))]
        hl = tuple(sorted(set(l for l in [0, 1, 2, 3, 6, 12, 24, 48, 72, 96, 120, int(round(P))] if l < len(home) // 3)))
        system = F.build_system(home, lf, uf, P, horizons or tuple(int(round(P * f)) for f in (0.1, 0.25, 0.5, 1.0)),
                                hl, name=tcol, unit='step')
        mode = f"FULL ({len(lf)} lower + {len(uf)} upper drivers)"
    else:
        system = F.build_self_system(home, P, horizons=horizons, name=tcol)
        mode = "SELF (single-series flywheel forecast)"

    print(f"  Mode: {mode}   home period {P:.1f}   horizons {system.horizons}")
    print("  Running strict-causal layered operator (golden split: train 61.8% / test 38.2%)...\n")
    res = F.run_forecast(system)

    # report
    print(f"  {'h':>6} | {'persist':>14} | {'home+ara (framework)':>22} | verdict")
    print('  ' + '-' * 64)
    rows = []
    for h, sc in res['horizons'].items():
        if sc is None:
            continue
        p = sc['persistence']; hp = sc['home_plus_ara']
        beat = 'BEATS persistence' if hp['corr'] > p['corr'] else 'below persistence'
        print(f"  {h:>6} | corr {p['corr']:+.3f} mae {p['mae']:.3g} | corr {hp['corr']:+.3f} mae {hp['mae']:.3g} | {beat}")
        rows.append(h)
    nbeat = sum(res['horizons'][h]['home_plus_ara']['corr'] > res['horizons'][h]['persistence']['corr']
                for h in rows)
    print(f"\n  Framework beats persistence at {nbeat}/{len(rows)} horizons.")
    print("  (ara_fixed_roll = parameter-free; ara_roll_readout = framework-only; "
          "home_ar = causal memory; home_plus_ara = headline. All in the JSON.)")

    out_path = args.out or os.path.splitext(args.csv)[0] + '_forecast.json'
    json.dump(dict(source_file=args.csv, target_column=tcol, home_period=P,
                   mode=mode, samples=int(len(home)), result=res, phi=F.PHI),
              open(out_path, 'w'), indent=2, default=float)
    print(f"\n  Saved -> {out_path}")


if __name__ == '__main__':
    main()
