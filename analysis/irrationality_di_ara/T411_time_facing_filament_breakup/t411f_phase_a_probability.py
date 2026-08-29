"""Frozen T411F one-sided child Phase A probability diagnostic."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
SRC = HERE / "results" / "T411D_causal_child_prediction"
OUT = HERE / "results" / "T411F_phase_a_probability"
SEED = 411006
STRIDE = 5
BINS = np.array([0, .3, .5, .7, .9, 1.0, 1.1, 1.3, 1.5, 1.7, 2.000001])
CONTROL_THRESHOLDS = [.7, .8, .9, 1.0, 1.1, 1.2]


def load_partition(stem: str, partition: str):
    events = pd.read_csv(SRC / f"T411D_{stem}_EVENTS.csv")
    series = pd.read_csv(SRC / f"T411D_{stem}_TIMESERIES.csv")
    events["partition"] = partition
    series["partition"] = partition
    return events, series


def make_snapshots(events: pd.DataFrame, series: pd.DataFrame):
    rows = []
    event_meta = []
    for _, e in events.iterrows():
        if bool(e.excluded) or not np.isfinite(e.target_t_s) or not np.isfinite(e.child_window_frames):
            continue
        g = series[series.Name == e.Name].sort_values("Time_s").copy()
        t_all = g.Time_s.to_numpy(float)
        a_all = g.x_child_connection_ara.to_numpy(float)
        finite_dt = np.diff(t_all[np.isfinite(t_all)])
        finite_dt = finite_dt[finite_dt > 0]
        if len(finite_dt) == 0:
            continue
        dt = float(np.median(finite_dt))
        horizon = float(e.child_window_frames * dt)
        valid = np.isfinite(t_all) & np.isfinite(a_all) & (t_all < float(e.target_t_s))
        idx = np.flatnonzero(valid)
        if len(idx) < STRIDE:
            continue
        idx = idx[::STRIDE]
        t = t_all[idx]
        a = np.clip(a_all[idx], 0, 2)
        lag_idx = np.maximum(idx-STRIDE, 0)
        previous = a_all[lag_idx]
        direction = np.where(np.isfinite(previous), a-a_all[lag_idx], np.nan)
        lead = float(e.target_t_s)-t
        y = ((lead > 0) & (lead <= horizon)).astype(int)
        w = np.repeat(1/len(idx), len(idx))
        for j in range(len(idx)):
            rows.append({
                "Name": e.Name, "fluid": e.fluid, "partition": e.partition,
                "time_s": t[j], "target_t_s": float(e.target_t_s),
                "lead_s": lead[j], "child_horizon_s": horizon,
                "phase_a": a[j], "phase_b_budget": 2-a[j],
                "phase_a_delta_5": direction[j], "approaching": bool(direction[j] > 0),
                "handover_within_child_window": int(y[j]), "event_weight": w[j],
            })
        event_meta.append({
            "Name": e.Name, "fluid": e.fluid, "partition": e.partition,
            "snapshots": len(idx), "dt_s": dt, "child_horizon_s": horizon,
            "target_t_s": float(e.target_t_s),
        })
    return pd.DataFrame(rows), pd.DataFrame(event_meta)


def weighted_probability(frame, mask=None):
    if mask is not None:
        frame = frame[mask]
    if len(frame) == 0 or frame.event_weight.sum() <= 0:
        return np.nan
    return float(np.average(frame.handover_within_child_window, weights=frame.event_weight))


def contrast(frame, threshold=.9, approaching_only=False):
    q = frame[frame.approaching] if approaching_only else frame
    high = q.phase_a >= threshold
    p_high = weighted_probability(q, high)
    p_low = weighted_probability(q, ~high)
    return {
        "threshold": threshold,
        "p_at_or_above": p_high,
        "p_below": p_low,
        "risk_difference": p_high-p_low if np.isfinite(p_high) and np.isfinite(p_low) else np.nan,
        "risk_ratio": p_high/p_low if np.isfinite(p_high) and np.isfinite(p_low) and p_low > 0 else np.nan,
        "event_count": int(q.Name.nunique()),
        "snapshot_count": int(len(q)),
    }


def bin_table(frame, label):
    q = frame.copy()
    q["bin"] = pd.cut(q.phase_a, BINS, right=False, include_lowest=True)
    rows = []
    for interval, g in q.groupby("bin", observed=False):
        if len(g) == 0:
            rows.append({"partition": label, "bin": str(interval), "lo": interval.left,
                         "hi": interval.right, "mid": (interval.left+interval.right)/2,
                         "probability": np.nan, "events": 0, "snapshots": 0,
                         "weight": 0.0})
        else:
            rows.append({"partition": label, "bin": str(interval), "lo": interval.left,
                         "hi": interval.right, "mid": (interval.left+interval.right)/2,
                         "probability": weighted_probability(g), "events": int(g.Name.nunique()),
                         "snapshots": int(len(g)), "weight": float(g.event_weight.sum())})
    return pd.DataFrame(rows)


def development_calibration(dev, diag):
    dev_bins = bin_table(dev, "development")
    base = weighted_probability(dev)
    probs = dev_bins.probability.fillna(base).to_numpy(float)
    idx = np.clip(np.digitize(diag.phase_a.to_numpy(float), BINS)-1, 0, len(probs)-1)
    pred = probs[idx]
    y = diag.handover_within_child_window.to_numpy(float)
    w = diag.event_weight.to_numpy(float)
    brier = float(np.average((pred-y)**2, weights=w))
    base_brier = float(np.average((base-y)**2, weights=w))
    return dev_bins, pred, {
        "development_base_probability": base,
        "diagnostic_brier": brier,
        "diagnostic_constant_brier": base_brier,
        "brier_improvement_fraction": (base_brier-brier)/base_brier if base_brier > 0 else np.nan,
    }


def weighted_auc(y, score, weight):
    data = pd.DataFrame({"y": y, "score": score, "w": weight}).sort_values("score")
    pos_total = float(data.loc[data.y == 1, "w"].sum())
    neg_total = float(data.loc[data.y == 0, "w"].sum())
    if pos_total <= 0 or neg_total <= 0:
        return np.nan
    concordant = 0.0
    neg_before = 0.0
    for _, group in data.groupby("score", sort=True):
        wp = float(group.loc[group.y == 1, "w"].sum())
        wn = float(group.loc[group.y == 0, "w"].sum())
        concordant += wp*(neg_before+0.5*wn)
        neg_before += wn
    return float(concordant/(pos_total*neg_total))


def circular_shift_null(frame, reps=1000):
    groups = []
    for _, g in frame.groupby("Name", sort=False):
        groups.append((g.phase_a.to_numpy(float),
                       g.handover_within_child_window.to_numpy(int),
                       g.event_weight.to_numpy(float)))
    observed = contrast(frame, .9)["risk_difference"]
    rng = np.random.default_rng(SEED)
    null = np.empty(reps, float)
    for rep in range(reps):
        high_y = high_w = low_y = low_w = 0.0
        for a, y, w in groups:
            if len(a) < 3:
                shifted = a
            else:
                shifted = np.roll(a, int(rng.integers(1, len(a))))
            high = shifted >= .9
            high_y += float(np.sum(w[high]*y[high])); high_w += float(np.sum(w[high]))
            low_y += float(np.sum(w[~high]*y[~high])); low_w += float(np.sum(w[~high]))
        null[rep] = high_y/high_w-low_y/low_w if high_w > 0 and low_w > 0 else np.nan
    null = null[np.isfinite(null)]
    return null, {
        "observed_risk_difference": observed,
        "reps": int(len(null)),
        "null_median": float(np.median(null)),
        "null_q95": float(np.quantile(null, .95)),
        "p_ge_observed": float((1+np.sum(null >= observed))/(1+len(null))),
    }


def event_bootstrap(frame, reps=1000):
    grouped = {name: g for name, g in frame.groupby("Name")}
    names = np.array(list(grouped))
    rng = np.random.default_rng(SEED+1)
    values = []
    for _ in range(reps):
        sample = rng.choice(names, size=len(names), replace=True)
        pieces = [grouped[name] for name in sample]
        q = pd.concat(pieces, ignore_index=True)
        values.append(contrast(q, .9)["risk_difference"])
    values = np.asarray(values, float)
    return {"reps": reps, "q025": float(np.nanquantile(values, .025)),
            "median": float(np.nanmedian(values)), "q975": float(np.nanquantile(values, .975))}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    de, ds = load_partition("DEVELOPMENT", "development")
    he, hs = load_partition("HOLDOUT", "diagnostic")
    dev, dev_meta = make_snapshots(de, ds)
    diag, diag_meta = make_snapshots(he, hs)
    pooled = pd.concat([dev, diag], ignore_index=True)
    meta = pd.concat([dev_meta, diag_meta], ignore_index=True)

    dev_bins, diag_pred, calibration = development_calibration(dev, diag)
    diag = diag.copy()
    diag["development_probability"] = diag_pred
    auc = weighted_auc(diag.handover_within_child_window.to_numpy(float),
                       diag_pred, diag.event_weight.to_numpy(float))
    calibration["diagnostic_auc"] = auc

    pooled_bins = bin_table(pooled, "pooled")
    diag_bins = bin_table(diag, "diagnostic")
    bin_out = pd.concat([dev_bins, diag_bins, pooled_bins], ignore_index=True)

    null, null_summary = circular_shift_null(pooled)
    threshold_rows = []
    for label, frame in [("development", dev), ("diagnostic", diag), ("pooled", pooled)]:
        for threshold in CONTROL_THRESHOLDS:
            threshold_rows.append({"partition": label, **contrast(frame, threshold)})
    thresholds = pd.DataFrame(threshold_rows)

    result = {
        "status": "frozen_posthoc_probability_diagnostic",
        "definition": {"phase_a": "T411D x_child_connection_ara", "ridge_threshold": .9,
                       "phase_b_budget": "2 - phase_a", "snapshot_stride_frames": STRIDE,
                       "prediction_horizon": "one frozen child window"},
        "snapshots": {"development": int(len(dev)), "diagnostic": int(len(diag)),
                      "pooled": int(len(pooled)), "development_events": int(dev.Name.nunique()),
                      "diagnostic_events": int(diag.Name.nunique())},
        "primary": {"development": contrast(dev, .9), "diagnostic": contrast(diag, .9),
                    "pooled": contrast(pooled, .9)},
        "approaching_comparator": {"development": contrast(dev, .9, True),
                                   "diagnostic": contrast(diag, .9, True),
                                   "pooled": contrast(pooled, .9, True)},
        "calibration": calibration,
        "circular_shift": null_summary,
        "bootstrap_pooled_risk_difference": event_bootstrap(pooled),
    }
    result["by_fluid"] = {
        fluid: {
            "primary": contrast(group, .9),
            "approaching_comparator": contrast(group, .9, True),
        }
        for fluid, group in pooled.groupby("fluid")
    }
    gates = {
        "positive_development": result["primary"]["development"]["risk_difference"] > 0,
        "positive_diagnostic": result["primary"]["diagnostic"]["risk_difference"] > 0,
        "shift_p_le_0_05": null_summary["p_ge_observed"] <= .05,
        "diagnostic_brier_beats_constant": calibration["diagnostic_brier"] < calibration["diagnostic_constant_brier"],
        "diagnostic_auc_gt_0_50": auc > .5,
    }
    result["gates"] = gates
    result["gate_count"] = f"{sum(gates.values())}/{len(gates)}"
    result["verdict"] = "SUPPORTED_IN_ARCHIVE" if all(gates.values()) else "NOT_FULLY_SUPPORTED"

    pooled.to_csv(OUT / "T411F_SNAPSHOTS.csv", index=False)
    diag.to_csv(OUT / "T411F_DIAGNOSTIC_PREDICTIONS.csv", index=False)
    meta.to_csv(OUT / "T411F_EVENTS.csv", index=False)
    bin_out.to_csv(OUT / "T411F_PROBABILITY_BINS.csv", index=False)
    thresholds.to_csv(OUT / "T411F_THRESHOLD_CONTROLS.csv", index=False)
    pd.DataFrame({"null_risk_difference": null}).to_csv(OUT / "T411F_SHIFT_NULL.csv", index=False)
    (OUT / "T411F_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
