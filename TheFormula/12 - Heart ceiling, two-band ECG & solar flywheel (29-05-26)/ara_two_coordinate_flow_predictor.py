"""
ara_two_coordinate_flow_predictor.py

Two-coordinate velocity-field predictor on the ARA sphere.

WHAT THIS IS
------------
The sphere has two coordinates:

    latitude  = ARA          (depth)         y = 1 - ARA,  equator at ARA = 1.0
    longitude = phase clock  (circumference)

A forecast is a flow on that sphere: from the current (ARA, phase) at origin t,
advance to a future (ARA, phase) at t+h, then read the value off the latitude.

This script fits the flow ONE COORDINATE AT A TIME so each half can be judged
on its own, against honest baselines, with a strict pre-cutoff / post-cutoff
split. No future row is ever used to fit or to predict its own target.

STATUS OF THE TWO HALVES (read before trusting anything)
--------------------------------------------------------
LATITUDE / DEPTH FLOW  -- IMPLEMENTED AND VALIDATED.
    dARA over the horizon is a near-linear, mean-reverting function of starting
    ARA, with the zero-crossing (the attractor the depth flow rolls toward) at
    ARA ~ 1.0, i.e. the equator, NOT phi. Fit on pre-cutoff, tested after.
    FINDING: it beats persistence strongly at long lead, but that is because
    persistence is a bad long-lead baseline. Against CLIMATOLOGY and AR(1) it
    adds ~0. The depth flow IS damped persistence / regression to the mean.
    It reproduces the shape weakly (correct timing, collapsed amplitude) and
    misses the El Nino / La Nina peaks, because those peaks are the orbit
    swinging wide in LONGITUDE, which this half does not contain.

LONGITUDE / CIRCUMFERENCE FLOW  -- IMPLEMENTED, NOT YET VALIDATED.
    Requires a phase series (`phase_clock_origin`) or a physical conjugate that
    leads SST. For ENSO the right conjugate is equatorial sub-surface ocean heat
    content / warm-water-volume (the recharge-oscillator variable), which leads
    SST by ~a season. SOI is the atmospheric partner but sits roughly in phase
    with SST, so it gives less lead. If the phase clock is a calendar/time clock
    or is computed from the SST series itself, this half cannot add skill: the
    path is then 1-D drawn on a 2-D sphere. The test is whether advancing phase
    forward and reading ARA off the orbit bends the forecast toward the peaks
    where the depth-only line stays flat. Run it; do not assume it.

INPUT
-----
Either:
  (a) a terrain-spin-standin style result JSON with top-level "records":
        records[h] = [{origin, target, actual, current, ...}, ...]
      (no phase -> longitude half is skipped), or
  (b) an atlas JSON with "records_by_horizon":
        records_by_horizon[h] = [{origin, target, actual, current,
                                  ara_current, phase_clock_origin, ...}, ...]
      (phase present -> longitude half runs).

USAGE
-----
    python ara_two_coordinate_flow_predictor.py INPUT.json [--cutoff 2017-01-01]
        [--horizons 3 6 12 18 24] [--out OUT_PREFIX]

Outputs:
  OUT_PREFIX_scores.json   -- per-horizon scores for every model + baseline
  OUT_PREFIX_series.json   -- per-row {date, actual, depth, persist, clim, ...}
                              (this is "the shape": feed it to any plotter)
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np

# ---- sphere coordinates (must match the framework's single-formula file) ----
VALUE_SCALE = 1.5
EPS = 1e-9


def value_to_ara(v):
    return np.clip(1.0 + np.tanh(np.asarray(v, float) / VALUE_SCALE), 0.0, 2.0)


def ara_to_value(a):
    x = np.clip(np.asarray(a, float) - 1.0, -0.985, 0.985)
    return VALUE_SCALE * np.arctanh(x)


def ara_y(a):
    return 1.0 - np.clip(np.asarray(a, float), 0.0, 2.0)


def ring(a):
    """Circumference factor at the latitude of an ARA value. Max (=1) at ARA=1."""
    y = ara_y(a)
    return np.sqrt(np.maximum(0.0, 1.0 - y * y))


def month_index(date_str):
    d = datetime.strptime(str(date_str)[:10], "%Y-%m-%d")
    return d.year * 12 + d.month - 1


def corr(a, b):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    if len(a) < 3 or np.std(a) <= EPS or np.std(b) <= EPS:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


# ----------------------------- data loading ---------------------------------
def load_rows(path):
    """Normalise either input shape into rows grouped by horizon.

    Each row: origin, target, v_cur (value at origin), v_act (value at t+h),
    ara_cur (measured if present else reconstructed), phase_cur (or None).
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if "records" in data:
        raw, has_phase = data["records"], False
    elif "records_by_horizon" in data:
        raw, has_phase = data["records_by_horizon"], True
    else:
        raise ValueError("input must have 'records' or 'records_by_horizon'")

    by_h = {}
    for h, rows in raw.items():
        out = []
        for r in rows:
            v_cur = float(r["current"])
            ara_cur = float(r["ara_current"]) if "ara_current" in r else float(value_to_ara(v_cur))
            phase = float(r["phase_clock_origin"]) if r.get("phase_clock_origin") is not None and has_phase else None
            out.append(
                {
                    "origin": r["origin"],
                    "target": r["target"],
                    "v_cur": v_cur,
                    "v_act": float(r["actual"]),
                    "ara_cur": ara_cur,
                    "phase_cur": phase,
                }
            )
        by_h[str(int(h))] = out
    phase_present = any(any(x["phase_cur"] is not None for x in v) for v in by_h.values())
    return by_h, phase_present


# ----------------------------- scoring --------------------------------------
def score(pred, actual, current, train_mean):
    """Honest scoreboard. skill_* = 1 - MSE_model / MSE_baseline (baseline=0)."""
    pred = np.asarray(pred, float)
    actual = np.asarray(actual, float)
    current = np.asarray(current, float)
    mse_m = np.mean((pred - actual) ** 2)
    mse_persist = np.mean((current - actual) ** 2)
    mse_clim = np.mean((train_mean - actual) ** 2)
    td = actual - current
    pd_ = pred - current
    mask = np.abs(td) > EPS
    return {
        "n": int(len(pred)),
        "mae": float(np.mean(np.abs(pred - actual))),
        "corr_with_actual": corr(pred, actual),
        "corr_with_current": corr(pred, current),
        "anomaly_corr": corr(pd_, td),  # corr of (pred-now) with (truth-now)
        "direction": float(np.mean(np.sign(pd_[mask]) == np.sign(td[mask]))) if mask.any() else None,
        "amp_ratio": float(np.std(pd_) / np.std(td)) if np.std(td) > EPS else None,
        "skill_vs_persistence": float(1 - mse_m / mse_persist) if mse_persist > EPS else None,
        "skill_vs_climatology": float(1 - mse_m / mse_clim) if mse_clim > EPS else None,
    }


# ----------------- LATITUDE / DEPTH flow (validated) ------------------------
def fit_depth_flow(train):
    """dARA over the horizon ~ slope * ARA_origin + intercept (mean reversion).

    Returns (slope, intercept, attractor) where attractor is the ARA the flow
    rolls toward (zero of the drift). Fit on TRAIN ONLY.
    """
    a0 = np.array([r["ara_cur"] for r in train], float)
    a1 = value_to_ara([r["v_act"] for r in train])
    slope, intercept = np.polyfit(a0, a1 - a0, 1)
    attractor = -intercept / slope if abs(slope) > EPS else float("nan")
    return float(slope), float(intercept), float(attractor)


def depth_predict(rows, slope, intercept, k=1.0):
    """ARA_pred = ARA + k * drift(ARA); k is the floor-tick multiplier."""
    a = np.array([r["ara_cur"] for r in rows], float)
    ara_pred = np.clip(a + k * (slope * a + intercept), 0.0, 2.0)
    return ara_to_value(ara_pred)


def ar1_baseline(train, holdout):
    """Damped persistence in value space, fit on train. The real long-lead baseline."""
    vc_tr = np.array([r["v_cur"] for r in train], float)
    va_tr = np.array([r["v_act"] for r in train], float)
    m = float(np.mean(vc_tr))
    rho = float(np.polyfit(vc_tr - m, va_tr - m, 1)[0])
    vc_ho = np.array([r["v_cur"] for r in holdout], float)
    return m + rho * (vc_ho - m)


# ----------- LONGITUDE / CIRCUMFERENCE flow (implemented, UNVALIDATED) -------
def fit_phase_flow(train):
    """Fit angular velocity omega (deg/month) and an orbit map ARA(phase).

    omega: slope of unwrapped phase vs month index on train.
    orbit: ARA ~ a0 + a1*cos(phase) + b1*sin(phase)  (first harmonic).
    Both fit on TRAIN ONLY, from origin-time (phase, ARA) pairs -> no leakage.
    Returns None if phase is unavailable.
    """
    pts = [(month_index(r["origin"]), r["phase_cur"], r["ara_cur"]) for r in train if r["phase_cur"] is not None]
    if len(pts) < 8:
        return None
    months = np.array([p[0] for p in pts], float)
    phase = np.deg2rad(np.array([p[1] for p in pts], float))
    ara = np.array([p[2] for p in pts], float)
    order = np.argsort(months)
    unwrapped = np.unwrap(phase[order])
    omega_rad = float(np.polyfit(months[order], unwrapped, 1)[0])  # rad / month
    X = np.column_stack([np.ones_like(phase), np.cos(phase), np.sin(phase)])
    coef, *_ = np.linalg.lstsq(X, ara, rcond=None)
    return {"omega_deg_per_month": math.degrees(omega_rad), "orbit_coef": coef.tolist()}


def longitude_predict(rows, flow, horizon):
    """Advance phase by omega*h, read ARA off the fitted orbit, decode to value.

    UNVALIDATED. Only meaningful if the phase clock tracks a leading physical
    conjugate (e.g. sub-surface heat content). Score on holdout before trusting.
    """
    omega = math.radians(flow["omega_deg_per_month"])
    a0, a1, b1 = flow["orbit_coef"]
    out = []
    for r in rows:
        if r["phase_cur"] is None:
            out.append(float("nan"))
            continue
        ph = math.radians(r["phase_cur"]) + omega * float(horizon)
        ara_future = np.clip(a0 + a1 * math.cos(ph) + b1 * math.sin(ph), 0.0, 2.0)
        out.append(float(ara_to_value(ara_future)))
    return np.array(out, float)


# ----------------------------- driver ---------------------------------------
def run(input_path, cutoff="2017-01-01", horizons=(3, 6, 12, 18, 24), out_prefix=None):
    by_h, phase_present = load_rows(input_path)
    scores, series = {}, {}
    tick_grid = np.round(np.linspace(0.0, 2.0, 41), 3)

    print(f"Two-coordinate ARA flow predictor   input={Path(input_path).name}")
    print(f"train < {cutoff} <= holdout   phase_available={phase_present}")
    print("=" * 92)

    for h in horizons:
        rows = by_h.get(str(h))
        if not rows:
            continue
        train = [r for r in rows if r["origin"] < cutoff]
        hold = [r for r in rows if r["origin"] >= cutoff]
        if len(train) < 8 or len(hold) < 5:
            continue
        train_mean = float(np.mean([r["v_cur"] for r in train]))

        slope, intercept, attractor = fit_depth_flow(train)

        actual = np.array([r["v_act"] for r in hold], float)
        current = np.array([r["v_cur"] for r in hold], float)

        # latitude / depth, tick swept on TRAIN, frozen, scored on HOLDOUT
        best_k, best_skill = 1.0, -1e9
        for k in tick_grid:
            tr_pred = depth_predict(train, slope, intercept, k)
            tr_act = np.array([r["v_act"] for r in train], float)
            sk = 1 - np.mean((tr_pred - tr_act) ** 2) / max(
                np.mean((np.array([r["v_cur"] for r in train]) - tr_act) ** 2), EPS
            )
            if sk > best_skill:
                best_skill, best_k = sk, float(k)

        depth_pred = depth_predict(hold, slope, intercept, k=1.0)
        depth_pred_bestk = depth_predict(hold, slope, intercept, k=best_k)
        persist = current
        clim = np.full_like(actual, train_mean)
        ar1 = ar1_baseline(train, hold)

        h_scores = {
            "depth_flow_k1": score(depth_pred, actual, current, train_mean),
            "depth_flow_best_k": score(depth_pred_bestk, actual, current, train_mean),
            "persistence": score(persist, actual, current, train_mean),
            "climatology": score(clim, actual, current, train_mean),
            "ar1_damped_persistence": score(ar1, actual, current, train_mean),
            "depth_flow_fit": {
                "slope": slope,
                "intercept": intercept,
                "attractor_ara": attractor,
                "best_tick_k_on_train": best_k,
            },
        }

        # longitude / circumference (only if a phase clock exists)
        long_pred = None
        flow = fit_phase_flow(train) if phase_present else None
        if flow is not None:
            long_pred = longitude_predict(hold, flow, h)
            if np.isfinite(long_pred).all():
                h_scores["longitude_flow_UNVALIDATED"] = score(long_pred, actual, current, train_mean)
                # two-coordinate combo: latitude relaxation blended with orbit read
                combo = 0.5 * depth_pred + 0.5 * long_pred
                h_scores["two_coordinate_combo_UNVALIDATED"] = score(combo, actual, current, train_mean)
                h_scores["longitude_flow_fit"] = flow

        scores[str(h)] = h_scores

        # per-row series for plotting (origin-sorted by target date)
        idx = np.argsort([r["target"] for r in hold])
        series[str(h)] = {
            "date": [hold[i]["target"] for i in idx],
            "origin": [hold[i]["origin"] for i in idx],
            "actual": [round(float(actual[i]), 4) for i in idx],
            "depth": [round(float(depth_pred[i]), 4) for i in idx],
            "persist": [round(float(persist[i]), 4) for i in idx],
            "clim": round(train_mean, 4),
            "longitude": [round(float(long_pred[i]), 4) for i in idx] if long_pred is not None else None,
            "cutoff": cutoff,
        }

        d = h_scores["depth_flow_k1"]
        print(
            f"h={h:>2}  attractor={attractor:5.2f}  depth: skill_vs_persist={d['skill_vs_persistence']:+.3f}"
            f"  skill_vs_clim={d['skill_vs_climatology']:+.3f}  anomaly_corr={d['anomaly_corr']:+.3f}"
            f"  amp={d['amp_ratio']:.2f}  best_tick={best_k:.2f}"
        )
        if "longitude_flow_UNVALIDATED" in h_scores:
            lo = h_scores["longitude_flow_UNVALIDATED"]
            print(
                f"      longitude(UNVALIDATED): skill_vs_clim={lo['skill_vs_climatology']:+.3f}"
                f"  anomaly_corr={lo['anomaly_corr']:+.3f}  amp={lo['amp_ratio']:.2f}"
            )

    if out_prefix is None:
        out_prefix = str(Path(input_path).with_suffix("")) + "_two_coord"
    Path(out_prefix + "_scores.json").write_text(json.dumps(scores, indent=2), encoding="utf-8")
    Path(out_prefix + "_series.json").write_text(json.dumps(series, indent=2), encoding="utf-8")
    print("=" * 92)
    print("KEY: depth_flow == mean reversion. If skill_vs_climatology ~ 0 it is NOT")
    print("     adding event skill, only beating persistence (a weak long-lead baseline).")
    print("     The peaks live in the longitude flow, which needs a LEADING conjugate")
    print("     (sub-surface heat content / warm-water-volume), not a time clock.")
    print(f"saved -> {out_prefix}_scores.json")
    print(f"saved -> {out_prefix}_series.json")
    return scores, series


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Two-coordinate ARA sphere flow predictor")
    ap.add_argument("input", help="terrain-spin-standin result JSON or atlas JSON")
    ap.add_argument("--cutoff", default="2017-01-01")
    ap.add_argument("--horizons", type=int, nargs="+", default=[3, 6, 12, 18, 24])
    ap.add_argument("--out", default=None, help="output prefix")
    args = ap.parse_args()
    run(args.input, cutoff=args.cutoff, horizons=tuple(args.horizons), out_prefix=args.out)
