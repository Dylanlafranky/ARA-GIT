"""Frozen post-hoc T411E parent-child coarse-ridge drop diagnostic."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SRC = HERE / "results" / "T411D_causal_child_prediction"
OUT = HERE / "results" / "T411E_parent_child_ridge_drop"
PERSIST = 5
SEED = 411005


def confirmed_cross(t, x, start_t, direction):
    use = np.isfinite(t) & np.isfinite(x) & (t >= start_t)
    armed = False
    for i in range(len(x)):
        if not use[i]:
            continue
        if direction == "down" and x[i] > 1:
            armed = True
        if direction == "up" and x[i] < 1:
            armed = True
        if not armed or i + 1 < PERSIST:
            continue
        tail = x[i-PERSIST+1:i+1]
        passed = np.all(np.isfinite(tail)) and (
            np.all(tail <= 1) if direction == "down" else np.all(tail >= 1)
        )
        if not passed:
            continue
        j = i-PERSIST+1
        if j > 0 and np.isfinite(x[j-1]) and x[j] != x[j-1]:
            f = (1-x[j-1])/(x[j]-x[j-1])
            cross = t[j-1] + np.clip(f, 0, 1)*(t[j]-t[j-1])
        else:
            cross = t[j]
        return float(cross), float(t[i])
    return np.nan, np.nan


def confirmed_issue_fast(t, x, start_t, direction):
    """Vectorised equivalent of confirmed_cross when only issue time is needed."""
    finite = np.isfinite(t) & np.isfinite(x)
    use = finite & (t >= start_t)
    if direction == "down":
        armed = np.maximum.accumulate(use & (x > 1))
        passed_sample = finite & (x <= 1)
    else:
        armed = np.maximum.accumulate(use & (x < 1))
        passed_sample = finite & (x >= 1)
    rolling_count = np.convolve(
        passed_sample.astype(np.int16), np.ones(PERSIST, dtype=np.int16), mode="full"
    )[: len(x)]
    candidate = use & armed & (rolling_count == PERSIST)
    idx = np.flatnonzero(candidate)
    return float(t[idx[0]]) if len(idx) else np.nan


def load_all():
    events = []
    series = []
    for mode, stem, identities in [("development", "DEVELOPMENT", {"S1", "S3"}), ("diagnostic", "HOLDOUT", {"S2", "S4"})]:
        e = pd.read_csv(SRC / f"T411D_{stem}_EVENTS.csv")
        s = pd.read_csv(SRC / f"T411D_{stem}_TIMESERIES.csv")
        e["partition"] = mode
        s["partition"] = mode
        events.append(e[e.fluid.isin(identities)])
        series.append(s[s.fluid.isin(identities)])
    return pd.concat(events, ignore_index=True), pd.concat(series, ignore_index=True)


def evaluate(events, series):
    rows = []
    enriched = []
    for _, e in events.iterrows():
        base = e.to_dict()
        if bool(e.excluded) or not np.isfinite(e.child_issue_t_s) or not np.isfinite(e.target_t_s):
            rows.append({**base, "t411e_eligible": False, "t411e_reason": "missing_child_or_target"})
            continue
        g = series[series.Name == e.Name].sort_values("Time_s").copy()
        t = g.Time_s.to_numpy(float)
        xc = g.x_child_connection_ara.to_numpy(float)
        xp = g.x_parent_causal_ara.to_numpy(float)
        pair = (xc+xp)/2
        down_cross, down_issue = confirmed_cross(t, pair, float(e.child_issue_t_s), "down")
        up_cross, up_issue = confirmed_cross(t, pair, float(e.child_issue_t_s), "up")
        g["x_parent_child_coarse"] = pair
        g["t411e_down_issue_t_s"] = down_issue
        enriched.append(g)
        pred = down_issue
        rows.append({
            **base, "t411e_eligible": True, "t411e_reason": "",
            "pair_down_cross_t_s": down_cross, "pair_down_issue_t_s": down_issue,
            "pair_up_cross_t_s": up_cross, "pair_up_issue_t_s": up_issue,
            "pair_prediction_t_s": pred,
            "pair_issue_lead_s": float(e.target_t_s-pred) if np.isfinite(pred) else np.nan,
            "pair_abs_error_s": abs(float(pred-e.target_t_s)) if np.isfinite(pred) else np.nan,
            "pair_abs_error_u": abs(float(pred-e.target_t_s))/float(e.tbrk_s) if np.isfinite(pred) else np.nan,
            "up_abs_error_u": abs(float(up_issue-e.target_t_s))/float(e.tbrk_s) if np.isfinite(up_issue) else np.nan,
        })
    return pd.DataFrame(rows), pd.concat(enriched, ignore_index=True) if enriched else pd.DataFrame()


def metric_block(e):
    q = e[e.t411e_eligible]
    p = q[q.pair_prediction_t_s.notna()]
    return {
        "eligible": int(len(q)), "predictions": int(len(p)),
        "coverage": float(len(p)/len(q)) if len(q) else np.nan,
        "pre_target_fraction": float((p.pair_prediction_t_s < p.target_t_s).mean()) if len(p) else np.nan,
        "median_lead_s": float(p.pair_issue_lead_s.median()) if len(p) else np.nan,
        "median_abs_error_u": float(p.pair_abs_error_u.median()) if len(p) else np.nan,
        "median_t411d_child_error_u": float(p.child_abs_error_u.median()) if len(p) else np.nan,
        "median_parent_error_u": float(p.parent_abs_error_u.median()) if len(p) else np.nan,
        "median_upward_error_u": float(p.up_abs_error_u.median()) if len(p) else np.nan,
    }


def shift_control(e, s, reps=1000):
    q = e[e.t411e_eligible & e.pair_prediction_t_s.notna()]
    target = q.set_index("Name").target_t_s.to_dict()
    tbrk = q.set_index("Name").tbrk_s.to_dict()
    start = q.set_index("Name").child_issue_t_s.to_dict()
    groups = [(n, g.sort_values("Time_s")) for n,g in s[s.Name.isin(q.Name)].groupby("Name")]
    obs = float(q.pair_abs_error_u.median())
    rng = np.random.default_rng(SEED)
    null = []
    for _ in range(reps):
        errs = []
        for name,g in groups:
            t = g.Time_s.to_numpy(float)
            x = g.x_parent_child_coarse.to_numpy(float)
            if np.isfinite(x).sum() < 12:
                continue
            xs = np.roll(x, int(rng.integers(PERSIST, len(x)-1)))
            issue = confirmed_issue_fast(t, xs, start[name], "down")
            if np.isfinite(issue):
                errs.append(abs(issue-target[name])/tbrk[name])
        if errs:
            null.append(float(np.median(errs)))
    null = np.asarray(null)
    return {
        "observed_median_abs_error_u": obs, "reps": int(len(null)),
        "null_median": float(np.median(null)), "null_q05": float(np.quantile(null,.05)),
        "p_le_observed": float((1+np.sum(null <= obs))/(1+len(null))),
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    events, series = load_all()
    scored, enriched = evaluate(events, series)
    result = {"status": "frozen_posthoc_mechanism_test", "all": metric_block(scored), "by_fluid": {}}
    for fluid, g in scored.groupby("fluid"):
        result["by_fluid"][fluid] = metric_block(g)
    result["shift_control_all"] = shift_control(scored, enriched)
    result["shift_control_diagnostic_S2_S4"] = shift_control(scored[scored.fluid.isin(["S2","S4"])], enriched[enriched.fluid.isin(["S2","S4"])])
    scored.to_csv(OUT / "T411E_EVENTS.csv", index=False)
    enriched.to_csv(OUT / "T411E_TIMESERIES.csv", index=False)
    (OUT / "T411E_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
