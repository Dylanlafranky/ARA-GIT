#!/usr/bin/env python3
"""map_systems_v3.py — Run the events_v4 hierarchical formula on Solar, ENSO,
EQ Sanriku, and ECG. Each gets a pump rung appropriate to its scale.

CAVEATS:
  Solar: 25 samples spanning 263 years — fits richly.
  ENSO:  23 samples spanning  74 years — fits moderately.
  EQ:    10 samples spanning 130 years — extremely sparse; events layer
         is heavily overfit risk, so we cap basis functions tightly.
  ECG:  200 samples spanning 145 sec — full pipeline OK.
"""

import os, sys, math, json, csv
import numpy as np

# Re-use everything from map_heart_v3 by importing
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from map_heart_v3 import (
    PHI, value_at_times, overflow_envelope,
    coupling_strength, classify_coupling,
    fit_subsystems, add_e_event_layer,
)

PROJECT_ROOT = os.path.dirname(HERE)


# ============================================================
# DATA LOADERS
# ============================================================

SOLAR_CYCLES = [
    (1, 1761.5, 144.1), (2, 1769.7, 193.0), (3, 1778.4, 264.3),
    (4, 1788.1, 235.3), (5, 1805.2,  82.0), (6, 1816.4,  81.2),
    (7, 1829.9, 119.2), (8, 1837.2, 244.9), (9, 1848.1, 219.9),
    (10, 1860.1, 186.2), (11, 1870.6, 234.0), (12, 1883.9, 124.4),
    (13, 1894.1, 146.5), (14, 1906.2, 107.1), (15, 1917.6, 175.7),
    (16, 1928.4, 130.2), (17, 1937.4, 198.6), (18, 1947.5, 218.7),
    (19, 1957.9, 285.0), (20, 1968.9, 156.6), (21, 1979.9, 232.9),
    (22, 1989.6, 212.5), (23, 2001.9, 180.3), (24, 2014.3, 116.4),
    (25, 2024.5, 173.0),
]

ENSO_EVENTS = [
    (1951.9, 1.2), (1953.2, 0.6), (1957.8, 1.7), (1963.8, 1.1),
    (1965.4, 1.4), (1968.9, 1.0), (1972.8, 2.0), (1976.7, 0.8),
    (1977.7, 0.8), (1979.7, 0.6), (1982.8, 2.1), (1986.9, 1.5),
    (1991.6, 1.6), (1994.8, 1.2), (1997.8, 2.3), (2002.8, 1.3),
    (2004.7, 0.7), (2006.8, 0.9), (2009.7, 1.5), (2015.0, 2.6),
    (2018.9, 0.8), (2023.9, 2.0), (2025.2, 0.9),
]

SANRIKU_EVENTS = [
    (1896.46, 8.5), (1933.17, 8.4), (1938.88, 7.7),
    (1968.42, 7.9), (1994.97, 7.7), (2011.19, 9.1),
    (2021.12, 7.1), (2022.21, 7.4), (2025.94, 7.6),
    (2026.30, 7.5),
]


def load_solar():
    return (np.array([c[1] - SOLAR_CYCLES[0][1] for c in SOLAR_CYCLES]),
            np.array([c[2] for c in SOLAR_CYCLES]))

def load_enso():
    return (np.array([e[0] - ENSO_EVENTS[0][0] for e in ENSO_EVENTS]),
            np.array([e[1] for e in ENSO_EVENTS]))

def load_eq():
    return (np.array([e[0] - SANRIKU_EVENTS[0][0] for e in SANRIKU_EVENTS]),
            np.array([e[1] for e in SANRIKU_EVENTS]))

def load_ecg():
    rows = []
    with open(os.path.join(PROJECT_ROOT, "computations", "real_ecg_rr.csv")) as f:
        for r in csv.DictReader(f):
            rows.append((float(r["time_s"]), float(r["rr_ms"])))
    rows.sort(key=lambda x: x[0])
    return (np.array([r[0] for r in rows]) - rows[0][0],
            np.array([r[1] for r in rows]))


# ============================================================
# RUNNER
# ============================================================

def run_system(name, t, v, pump_rung, candidate_rungs, max_subs,
                events_enabled=True, events_min_run=1, events_sigma_thresh=1.0):
    """Run the full pipeline. If events_enabled=False, stop at full_ladder."""
    print()
    print("=" * 70)
    print(f"{name}: N={len(t)} samples, span {t[-1]:.2f}, pump rung phi^{pump_rung}")
    print(f"  data range [{v.min():.2f}, {v.max():.2f}], std {v.std():.3f}")

    # Override the global PUMP_RUNG by monkey-patching the imported module
    import map_heart_v3 as M
    M.PUMP_RUNG = pump_rung
    M.PUMP_PERIOD = PHI ** pump_rung

    fit_full = fit_subsystems(t, v, candidate_rungs, max_subs, allow_neighbours=True)
    print(f"  full_ladder:  corr={fit_full['corr']:+.4f}  MAE={fit_full['mae']:.4f}  N_sub={len(fit_full['subsystems'])}")
    for s in fit_full['subsystems']:
        print(f"    rung phi^{s['rung']:+d}  T{s['ctype']}  P={s['period']:6.3f}  ARA={s['ara']:.2f}  amp={s['amp']:+.3f}")

    if events_enabled:
        ev = add_e_event_layer(t, fit_full['pred'], v,
                                with_rebound=True, with_peak_boost=True,
                                min_run=events_min_run, sigma_threshold=events_sigma_thresh)
        print(f"  events_v4:    corr={ev['corr']:+.4f}  MAE={ev['mae']:.4f}  N_events={len(ev['events'])}")
    else:
        ev = {"pred": fit_full['pred'], "corr": fit_full['corr'], "mae": fit_full['mae'],
              "events": [], "pulses": [0.0]*len(t)}
        print(f"  events_v4:    SKIPPED (too few samples for safe basis count)")

    return {
        "name": name,
        "t": t.tolist(),
        "v": v.tolist(),
        "pump_rung": pump_rung,
        "candidate_rungs": candidate_rungs,
        "centerline": fit_full['centerline'],
        "fits": {
            "full_ladder": {
                "pred": fit_full['pred'].tolist(),
                "corr": fit_full['corr'],
                "mae": fit_full['mae'],
                "subsystems": fit_full['subsystems'],
                "std_ratio": float(fit_full['pred'].std() / v.std()) if v.std() > 0 else 0.0,
            },
            "events_v4": {
                "pred": (ev['pred'].tolist() if hasattr(ev['pred'], 'tolist') else ev['pred']),
                "corr": ev['corr'],
                "mae": ev['mae'],
                "events": ev.get('events', []),
                "std_ratio": float(np.array(ev['pred']).std() / v.std()) if v.std() > 0 else 0.0,
            },
        },
    }


def main():
    results = {}

    # SOLAR — pump at phi^5 (Schwabe), 25 samples — full pipeline OK
    t, v = load_solar()
    results["solar"] = run_system(
        "Solar (SSN)", t, v,
        pump_rung=5,
        candidate_rungs=[3, 4, 6, 7, 8, 9],   # around phi^5
        max_subs=4,
        events_enabled=True, events_min_run=1, events_sigma_thresh=1.0,
    )

    # ENSO — pump at phi^3, 23 samples — events with stricter threshold
    t, v = load_enso()
    results["enso"] = run_system(
        "ENSO (ONI peaks)", t, v,
        pump_rung=3,
        candidate_rungs=[1, 2, 4, 5, 6, 7],
        max_subs=4,
        events_enabled=True, events_min_run=2, events_sigma_thresh=1.2,
    )

    # EQ — pump at phi^6, only 10 samples — DISABLE events to avoid overfitting
    t, v = load_eq()
    results["eq"] = run_system(
        "EQ Sanriku (Mw)", t, v,
        pump_rung=6,
        candidate_rungs=[4, 5, 7, 8, 9],
        max_subs=2,                        # only 2 subsystems on 10 samples
        events_enabled=False,
    )

    # ECG — pump at phi^1, 200 samples — full pipeline (already proven)
    t, v = load_ecg()
    results["ecg"] = run_system(
        "ECG R-R (PhysioNet 402)", t, v,
        pump_rung=1,
        candidate_rungs=[-1, 0, 2, 3, 4, 5, 6, 7, 8],
        max_subs=6,
        events_enabled=True, events_min_run=1, events_sigma_thresh=1.0,
    )

    # Save
    out_path = os.path.join(HERE, "systems_map_v3.json")
    with open(out_path, "w") as f: json.dump(results, f)
    js_path = os.path.join(HERE, "systems_map_v3_data.js")
    with open(js_path, "w") as f:
        f.write("window.SYSTEMS_DATA_V3 = ")
        json.dump(results, f)
        f.write(";")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"{'system':>22} {'N':>4} {'pump':>6} {'corr_full':>10} {'corr_v4':>10} {'std_full':>9} {'std_v4':>8}")
    for k, r in results.items():
        ff = r['fits']['full_ladder']; ev = r['fits']['events_v4']
        print(f"{r['name']:>22} {len(r['t']):>4} phi^{r['pump_rung']:<2} "
              f"{ff['corr']:>+10.4f} {ev['corr']:>+10.4f} "
              f"{ff['std_ratio']:>9.2f} {ev['std_ratio']:>8.2f}")
    print(f"\nSaved {out_path}")
    print(f"Saved {js_path}")


if __name__ == "__main__":
    main()
