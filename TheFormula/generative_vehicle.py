#!/usr/bin/env python3
"""
generative_vehicle.py - Truly blind generative vehicle (system-agnostic core)

===========================================================================
TRANSPARENCY STATEMENT (per feedback_formula_transparency rule):

  This formula sees:    ARA, amplitude_at_t0, dominant period, time span (4 numbers)
  It generates by:      Closed-form cascade evaluation (ARASystem.predict_continuous
                        with observed_peaks=None), then anchored so the wave
                        passes through amplitude_at_t0 exactly at t=0.

  It does NOT see:      Real data values beyond the single anchor point.
                        Real peak times. Mean of the data. Anything else
                        about the dataset during generation.

  Method:               GENERATIVE VEHICLE - given (ARA, amplitude_at_t0,
                        period, time_span), produce a continuous waveform
                        anchored at t=0 to amplitude_at_t0.
                        NOT LOO. NOT a fit. NOT a one-step-ahead echo.

  Comparison:           Real data is loaded ONLY AFTER the wave is generated.
                        Used solely for visual overlay.
===========================================================================

Inputs per Dylan's spec (28 April 2026):
  ara              : the system's ARA value
  amplitude_at_t0  : the amplitude observed AT t=0; the wave passes through
                     this value exactly. Cascade modulations ride relative to it.
  period           : dominant period (system identifier - same units as time_span)
  time_span        : how long to generate for, in the same units as period

Optional:
  t_ref            : phase anchor (default 0.0 - "t=0 is when you started watching")
  n_points         : sampling density of the output curve (default 2000)

CONTRACT:
  generated_wave[0] == amplitude_at_t0   (always, by construction)
  generated_wave[i] for i > 0 follows the cascade geometry from that anchor

Returns: (times_array, values_array) of length n_points.

Drop-in dynamic: generate() works on any dataset. The test harness at the
bottom is a thin shell - add a new dataset by appending one entry to SYSTEMS.
"""

import os
import math
import json
import csv
import numpy as np

# --- Paths ----------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
COMP_DIR = os.path.join(PROJECT_ROOT, "computations")
BRIDGE_PATH = os.path.join(COMP_DIR, "226_ara_bridge.py")
ECG_CSV = os.path.join(COMP_DIR, "real_ecg_rr.csv")

PHI = (1 + math.sqrt(5)) / 2

# ===================================================================
# Load ARASystem class from 226_ara_bridge.py (just the class, no main)
# ===================================================================

def load_ara_system_class():
    """Load only the ARASystem class definition. Stops before any main code."""
    with open(BRIDGE_PATH, "r") as f:
        code = f.read()
    cut_at = code.find("class ARABridge")
    if cut_at < 0:
        raise RuntimeError("Could not find class boundary in 226_ara_bridge.py")
    namespace = {}
    exec(code[:cut_at], namespace)
    if "ARASystem" not in namespace:
        raise RuntimeError("ARASystem class not loaded from 226_ara_bridge.py")
    return namespace["ARASystem"]

ARASystem = load_ara_system_class()


# ===================================================================
# THE GENERATIVE FUNCTION - completely dynamic, no per-system code
# ===================================================================

def generate(ara, amplitude_at_t0, period, time_span,
             t_ref=0.0, n_points=2000):
    """
    Generate a continuous waveform anchored at t=0 to amplitude_at_t0.

    The cascade computes its natural value at every t. We then offset
    the entire wave by (amplitude_at_t0 - wave[0]) so the curve passes
    through amplitude_at_t0 at t=0 by construction. Shape is preserved.

    No real data is consulted during generation beyond the anchor value.

    Args:
      ara             : system's ARA value (governs the cascade gate, tension, etc.)
      amplitude_at_t0 : the amplitude observed at t=0 (anchor value)
      period          : dominant period of the system (same units as time_span)
      time_span       : length of trajectory to generate
      t_ref           : phase anchor (default 0.0)
      n_points        : output sampling density (default 2000)

    Returns: (times, values) numpy arrays of length n_points.
             values[0] == amplitude_at_t0 exactly.
    """
    # Dummy placeholders - never inspected when use_weierstrass=False.
    dummy_times = np.array([t_ref])
    dummy_values = np.array([amplitude_at_t0])

    sys_obj = ARASystem(
        name="generative",
        ara=ara,
        dominant_period=period,
        data_times=dummy_times,
        data_values=dummy_values,
        use_weierstrass=False,
    )

    times, values = sys_obj.predict_continuous(
        t_start=t_ref,
        t_end=t_ref + time_span,
        t_ref=t_ref,
        base_amp=amplitude_at_t0,
        n_points=n_points,
        observed_peaks=None,   # NO REAL DATA
        peak_times=None,       # NO REAL DATA
    )

    # Anchor: shift the entire wave so values[0] == amplitude_at_t0.
    # This preserves cascade shape but locks the starting value to
    # what the user observed at t=0.
    offset = amplitude_at_t0 - values[0]
    values = values + offset

    return times, values


# ===================================================================
# DATA LOADERS - used ONLY for post-hoc visual comparison
# (separate from the generative core; loading happens AFTER generation)
# ===================================================================

# Real data sources:
#  - SILSO/Royal Observatory of Belgium (solar SSN peaks)
#  - NOAA Climate Prediction Center (ENSO ONI peaks)
#  - PhysioNet Subject 402, doi:10.13026/kcn5-hj87 (ECG R-R)

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


def load_solar():
    t = np.array([c[1] for c in SOLAR_CYCLES])
    v = np.array([c[2] for c in SOLAR_CYCLES])
    return t, v

def load_enso():
    t = np.array([e[0] for e in ENSO_EVENTS])
    v = np.array([e[1] for e in ENSO_EVENTS])
    return t, v

def load_ecg():
    if not os.path.exists(ECG_CSV):
        return np.array([]), np.array([])
    rows = []
    with open(ECG_CSV) as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append((float(r["time_s"]), float(r["rr_ms"])))
    if not rows:
        return np.array([]), np.array([])
    rows.sort(key=lambda x: x[0])
    return (np.array([r[0] for r in rows]),
            np.array([r[1] for r in rows]))


# ===================================================================
# TEST HARNESS - one entry per dataset to test against
# ===================================================================
# Add a new dataset by appending one dict here:
#   - name      : display name
#   - ara       : system's ARA value
#   - period    : dominant period of the system (same units as data_times)
#   - units     : label for time axis
#   - load      : function returning (times_array, values_array)

SYSTEMS = [
    {"name": "Solar (SSN)",            "ara": PHI,    "period": PHI**5, "units": "years",   "load": load_solar},
    {"name": "ENSO (ONI peaks)",       "ara": 2.0,    "period": PHI**3, "units": "years",   "load": load_enso},
    {"name": "ECG R-R (PhysioNet 402)", "ara": 0.918, "period": PHI,    "units": "seconds", "load": load_ecg},
]


def run_one_system(spec, n_points=2000):
    """Run the generative vehicle on one system and prepare visualization data.

    The ONLY data the formula sees: ARA, amplitude (= first observed value),
    period, time span. Everything else is comparison-only.
    """
    name = spec["name"]
    ara = spec["ara"]
    period = spec["period"]
    units = spec["units"]

    actual_t, actual_v = spec["load"]()
    if len(actual_t) == 0:
        return None

    # Shift data to t=0 reference (alignment, not fitting)
    t_offset = float(actual_t[0])
    actual_t_shifted = actual_t - t_offset

    # Inputs to the generative vehicle. Only 4 numbers.
    amplitude_at_t0 = float(actual_v[0])           # the value at t=0
    time_span = float(actual_t_shifted[-1])        # length of test window

    # Generate the wave - this is the only call that "predicts."
    times, values = generate(
        ara=ara,
        amplitude_at_t0=amplitude_at_t0,
        period=period,
        time_span=time_span,
        t_ref=0.0,
        n_points=n_points,
    )

    # Sanity: verify the contract held (values[0] == amplitude_at_t0)
    anchor_err = float(values[0] - amplitude_at_t0)

    # ----- Post-hoc comparison only, NOT used by formula -----
    pred_at_actual = []
    for at in actual_t_shifted:
        if at < 0 or at > time_span:
            pred_at_actual.append(None)
        else:
            i = int(round(at / time_span * (len(times) - 1)))
            i = max(0, min(len(times) - 1, i))
            pred_at_actual.append(float(values[i]))

    valid = [(p, a) for p, a in zip(pred_at_actual, actual_v) if p is not None]
    if valid:
        ps = np.array([p for p, _ in valid])
        acs = np.array([a for _, a in valid])
        mae = float(np.mean(np.abs(ps - acs)))
        if len(ps) > 1 and np.std(ps) > 0 and np.std(acs) > 0:
            corr = float(np.corrcoef(ps, acs)[0, 1])
        else:
            corr = None
    else:
        mae, corr = None, None

    return {
        "name": name,
        "ara": ara,
        "amplitude": amplitude_at_t0,
        "period": period,
        "time_span": time_span,
        "units": units,
        "anchor_err": anchor_err,
        "predicted_t": times.tolist(),
        "predicted_v": [float(v) for v in values],
        "actual_t": [float(t) for t in actual_t_shifted],
        "actual_v": [float(v) for v in actual_v],
        "predicted_at_actual": pred_at_actual,
        "comparison_mae": mae,
        "comparison_corr": corr,
    }


def main():
    print("=" * 78)
    print("generative_vehicle.py - blind continuous generation, anchored at t=0")
    print("=" * 78)
    print()
    print("Per system: (ARA, amplitude_at_t0, period, time_span)")
    print("Wave is offset so values[0] = amplitude_at_t0 exactly.")
    print("Real data loaded only after generation, for visual overlay.")
    print()

    results = []
    for spec in SYSTEMS:
        r = run_one_system(spec)
        if r is None:
            print("Skipping {} (no data)".format(spec["name"]))
            continue
        print("{:<26}  ARA={:>5.3f}  amp(t=0)={:>9.3f}  P={:>7.3f}{:s}  span={:>7.2f}".format(
            r["name"], r["ara"], r["amplitude"], r["period"],
            " " + r["units"][:3], r["time_span"]))
        results.append(r)

    print()
    print("--- Anchor sanity (values[0] - amplitude_at_t0 should be ~0) ---")
    for r in results:
        print("  {:<26}  anchor_err = {:+.6e}".format(r["name"], r["anchor_err"]))

    print()
    print("--- Honest post-hoc comparison (NOT used by formula) ---")
    for r in results:
        mae_str = "{:.4f}".format(r["comparison_mae"]) if r["comparison_mae"] is not None else "n/a"
        corr_str = "{:+.3f}".format(r["comparison_corr"]) if r["comparison_corr"] is not None else "n/a"
        print("  {:<26}  N_actual={:>3}  MAE={:>10}  corr={}".format(
            r["name"], len(r["actual_t"]), mae_str, corr_str))

    payload = {
        "transparency": {
            "method": "Closed-form cascade (ARASystem.predict_continuous, observed_peaks=None) + t=0 anchor",
            "inputs_per_system": ["ARA", "amplitude_at_t0", "period", "time_span"],
            "real_data_seen_during_generation": False,
            "anchor_rule": "values[0] == amplitude_at_t0 exactly (offset preserves cascade shape)",
            "comparison_alignment": "actual_t shifted so first observation = t=0; amplitude_at_t0 = actual[0]",
        },
        "systems": results,
    }

    out_json = os.path.join(HERE, "generative_vehicle_data.json")
    with open(out_json, "w") as f:
        json.dump(payload, f)
    print()
    print("Wrote", out_json)

    out_js = os.path.join(HERE, "generative_vehicle_data.js")
    with open(out_js, "w", encoding="utf-8") as f:
        f.write("window.EMBEDDED_DATA = " + json.dumps(payload) + ";\n")
    print("Wrote", out_js, "(loaded by HTML viewer via <script src>)")


if __name__ == "__main__":
    main()
