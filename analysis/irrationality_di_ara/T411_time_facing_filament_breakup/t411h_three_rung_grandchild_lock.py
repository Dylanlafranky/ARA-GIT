"""Frozen T411H three-rung grandchild-lock transfer test."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import t411c_source_qualified_rate as t411c
import t411d_causal_child_predictor as t411d
import t411g_causal_di_ara as scoring


HERE = Path(__file__).resolve().parent
T411D = HERE / "results" / "T411D_causal_child_prediction"
OUT = HERE / "results" / "T411H_three_rung_grandchild_lock"
SEED = 411008
SHIFT_REPS = 1000
STRIDE = 5

MODELS = {
    "constant": [],
    "parent_state": ["v", "dv"],
    "parent_child": ["v", "dv", "u", "du"],
    "parent_grandchild": ["v", "dv", "w", "dw"],
    "three_rung_additive": ["v", "dv", "u", "du", "w", "dw"],
    "three_point_lock": ["v", "dv", "u", "du", "w", "dw", "vw", "uw"],
}


def odd_half_window(child_window: int) -> int:
    window = max(3, int(child_window) // 2)
    if window % 2 == 0:
        window += 1
    return window


def load_sources():
    events = pd.concat([
        pd.read_csv(T411D / "T411D_DEVELOPMENT_EVENTS.csv"),
        pd.read_csv(T411D / "T411D_HOLDOUT_EVENTS.csv"),
    ], ignore_index=True).drop_duplicates("Name")
    series = pd.concat([
        pd.read_csv(T411D / "T411D_DEVELOPMENT_TIMESERIES.csv"),
        pd.read_csv(T411D / "T411D_HOLDOUT_TIMESERIES.csv"),
    ], ignore_index=True)
    metadata = t411c.load_metadata().set_index("Name")
    return events, series, metadata


def event_snapshots(event: pd.Series, group: pd.DataFrame, metadata: pd.Series):
    if bool(event.excluded) or not np.isfinite(event.target_t_s):
        return pd.DataFrame(), None
    group = group.sort_values("Time_s").copy()
    t = group.Time_s.to_numpy(float)
    d = group.D_mm.to_numpy(float)
    if len(t) < 10:
        return pd.DataFrame(), None
    dt = float(np.median(np.diff(t)))
    child_window = int(event.child_window_frames)
    grandchild_window = odd_half_window(child_window)
    r_grandchild_observed = -t411d.causal_slope(d, grandchild_window, dt)
    d0 = float(metadata.D0_mm)
    h0 = d0 * float(metadata.H0_D0)
    velocity = float(metadata.v_mm_s)
    r_mechanical = (
        0.75 * (velocity / h0) * d0
        * np.power(1 + velocity * t / h0, -1.75)
    )
    r_grandchild = r_grandchild_observed - r_mechanical
    r_parent = group.r_parent_unresolved_mm_s.to_numpy(float)
    r_child = group.r_child_unresolved_mm_s.to_numpy(float)
    d_pc = np.abs(r_child - r_parent)
    d_cg = np.abs(r_grandchild - r_child)
    detail_total = d_pc + d_cg
    x_grandchild = np.full(len(t), np.nan)
    valid_grandchild = np.isfinite(detail_total) & (detail_total > 0)
    x_grandchild[valid_grandchild] = 2 * d_pc[valid_grandchild] / detail_total[valid_grandchild]
    x_parent = group.x_parent_causal_ara.to_numpy(float)
    x_child = group.x_child_connection_ara.to_numpy(float)

    target_t = float(event.target_t_s)
    base_valid = (
        np.isfinite(x_parent) & np.isfinite(x_child) & np.isfinite(x_grandchild)
        & (t < target_t)
    )
    candidate = np.flatnonzero(base_valid)
    if len(candidate) == 0:
        return pd.DataFrame(), None
    candidate = candidate[::STRIDE]
    candidate = candidate[
        (candidate >= STRIDE)
        & np.isfinite(x_parent[candidate - STRIDE])
        & np.isfinite(x_child[candidate - STRIDE])
        & np.isfinite(x_grandchild[candidate - STRIDE])
    ]
    if len(candidate) == 0:
        return pd.DataFrame(), None

    horizon = child_window * dt
    lead = target_t - t[candidate]
    outcome = ((lead > 0) & (lead <= horizon)).astype(int)
    x_p = np.clip(x_parent[candidate], 0, 2)
    x_c = np.clip(x_child[candidate], 0, 2)
    x_g = np.clip(x_grandchild[candidate], 0, 2)
    previous = candidate - STRIDE
    dx_p = x_p - np.clip(x_parent[previous], 0, 2)
    dx_c = x_c - np.clip(x_child[previous], 0, 2)
    dx_g = x_g - np.clip(x_grandchild[previous], 0, 2)
    weight = np.repeat(1 / len(candidate), len(candidate))
    frame = pd.DataFrame({
        "Name": str(event.Name),
        "fluid": str(event.fluid),
        "partition": str(event.partition),
        "time_s": t[candidate],
        "target_t_s": target_t,
        "lead_s": lead,
        "child_horizon_s": horizon,
        "parent_window_frames": int(event.parent_window_frames),
        "child_window_frames": child_window,
        "grandchild_window_frames": grandchild_window,
        "x_parent": x_p,
        "x_child": x_c,
        "x_grandchild": x_g,
        "d_pc_mm_s": d_pc[candidate],
        "d_cg_mm_s": d_cg[candidate],
        "y": outcome,
        "event_weight": weight,
    })
    frame["v"] = frame.x_parent - 1
    frame["u"] = frame.x_child - 1
    frame["w"] = frame.x_grandchild - 1
    frame["dv"] = dx_p
    frame["du"] = dx_c
    frame["dw"] = dx_g
    frame["vw"] = frame.v * frame.w
    frame["uw"] = frame.u * frame.w
    summary = {
        "Name": str(event.Name),
        "fluid": str(event.fluid),
        "partition": str(event.partition),
        "parent_window_frames": int(event.parent_window_frames),
        "child_window_frames": child_window,
        "grandchild_window_frames": grandchild_window,
        "snapshots": int(len(frame)),
        "positive_snapshots": int(frame.y.sum()),
        "child_horizon_s": horizon,
        "target_t_s": target_t,
    }
    return frame, summary


def build_geometry():
    events, series, metadata = load_sources()
    events = events.copy()
    events["partition"] = np.where(events.fluid.isin(["S1", "S3"]), "development", "diagnostic")
    frames = []
    summaries = []
    for _, event in events.iterrows():
        if event.Name not in metadata.index:
            continue
        group = series[series.Name == event.Name]
        frame, summary = event_snapshots(event, group, metadata.loc[event.Name])
        if len(frame):
            frames.append(frame)
            summaries.append(summary)
    return pd.concat(frames, ignore_index=True), pd.DataFrame(summaries)


def fit_leave_one_fluid_out(frame: pd.DataFrame):
    predictions = []
    fitted = {}
    coefficient_rows = []
    for heldout in sorted(frame.fluid.unique()):
        train = frame[frame.fluid != heldout]
        test = frame[frame.fluid == heldout].copy()
        for name, features in MODELS.items():
            model = scoring.fit_model(train, features)
            fitted[(heldout, name)] = model
            x_test = test[features].to_numpy(float) if features else np.empty((len(test), 0))
            test[f"p_{name}"] = scoring.predict_model(model, x_test)
            if features:
                coefficient_rows.append({
                    "heldout_fluid": heldout, "model": name,
                    "term": "intercept",
                    "coefficient_standardized": float(model["beta"][0]),
                })
                for feature, coefficient in zip(features, model["beta"][1:]):
                    coefficient_rows.append({
                        "heldout_fluid": heldout, "model": name,
                        "term": feature,
                        "coefficient_standardized": float(coefficient),
                    })
        predictions.append(test)
    return pd.concat(predictions, ignore_index=True), fitted, pd.DataFrame(coefficient_rows)


def performance_tables(predictions: pd.DataFrame):
    overall_rows = []
    fluid_rows = []
    for name in MODELS:
        column = f"p_{name}"
        overall_rows.append({"model": name, **scoring.metrics(predictions, column)})
        for fluid, group in predictions.groupby("fluid"):
            fluid_rows.append({"fluid": fluid, "model": name, **scoring.metrics(group, column)})
    return pd.DataFrame(overall_rows), pd.DataFrame(fluid_rows)


def grandchild_alignment_null(predictions: pd.DataFrame, fitted: dict, reps: int = SHIFT_REPS):
    rng = np.random.default_rng(SEED)
    squared_error = np.zeros(reps, float)
    total_weight = 0.0
    features = MODELS["three_point_lock"]
    for (_, fluid), group in predictions.groupby(["Name", "fluid"], sort=False):
        group = group.sort_values("time_s")
        n = len(group)
        if n < 2:
            continue
        v = group.v.to_numpy(float)
        dv = group.dv.to_numpy(float)
        u = group.u.to_numpy(float)
        du = group.du.to_numpy(float)
        w = group.w.to_numpy(float)
        dw = group.dw.to_numpy(float)
        y = group.y.to_numpy(float)
        weight = group.event_weight.to_numpy(float)
        model = fitted[(fluid, "three_point_lock")]
        for start in range(0, reps, 100):
            stop = min(start + 100, reps)
            count = stop - start
            offsets = rng.integers(1, n, size=count)
            indices = (np.arange(n)[None, :] - offsets[:, None]) % n
            w_shift = w[indices]
            dw_shift = dw[indices]
            v_grid = np.broadcast_to(v, w_shift.shape)
            dv_grid = np.broadcast_to(dv, w_shift.shape)
            u_grid = np.broadcast_to(u, w_shift.shape)
            du_grid = np.broadcast_to(du, w_shift.shape)
            x = np.stack([
                v_grid, dv_grid, u_grid, du_grid, w_shift, dw_shift,
                v_grid * w_shift, u_grid * w_shift,
            ], axis=2)
            z = (x - model["mean"]) / model["scale"]
            linear = model["beta"][0] + np.einsum("rnf,f->rn", z, model["beta"][1:])
            probability = scoring.sigmoid(linear)
            squared_error[start:stop] += np.sum(
                weight[None, :] * (probability - y[None, :]) ** 2, axis=1,
            )
        total_weight += float(weight.sum())
    null_brier = squared_error / total_weight
    parent_child_brier = scoring.metrics(predictions, "p_parent_child")["brier"]
    observed_lock_brier = scoring.metrics(predictions, "p_three_point_lock")["brier"]
    observed_improvement = parent_child_brier - observed_lock_brier
    null_improvement = parent_child_brier - null_brier
    p_value = float((1 + np.sum(null_improvement >= observed_improvement)) / (1 + reps))
    table = pd.DataFrame({
        "replicate": np.arange(reps),
        "shifted_lock_brier": null_brier,
        "improvement_over_parent_child": null_improvement,
    })
    summary = {
        "reps": reps,
        "observed_parent_child_brier": parent_child_brier,
        "observed_three_point_lock_brier": observed_lock_brier,
        "observed_improvement_over_parent_child": observed_improvement,
        "null_improvement_median": float(np.median(null_improvement)),
        "null_improvement_q95": float(np.quantile(null_improvement, .95)),
        "p_ge_observed": p_value,
    }
    return table, summary


def parent_grandchild_alignment_audit(predictions: pd.DataFrame, fitted: dict, reps: int = SHIFT_REPS):
    """Post-hoc audit of the predeclared parent+grandchild comparator."""
    rng = np.random.default_rng(SEED + 1)
    squared_error = np.zeros(reps, float)
    total_weight = 0.0
    for (_, fluid), group in predictions.groupby(["Name", "fluid"], sort=False):
        group = group.sort_values("time_s")
        n = len(group)
        if n < 2:
            continue
        v = group.v.to_numpy(float)
        dv = group.dv.to_numpy(float)
        w = group.w.to_numpy(float)
        dw = group.dw.to_numpy(float)
        y = group.y.to_numpy(float)
        weight = group.event_weight.to_numpy(float)
        model = fitted[(fluid, "parent_grandchild")]
        for start in range(0, reps, 100):
            stop = min(start + 100, reps)
            count = stop - start
            offsets = rng.integers(1, n, size=count)
            indices = (np.arange(n)[None, :] - offsets[:, None]) % n
            w_shift = w[indices]
            dw_shift = dw[indices]
            v_grid = np.broadcast_to(v, w_shift.shape)
            dv_grid = np.broadcast_to(dv, w_shift.shape)
            x = np.stack([v_grid, dv_grid, w_shift, dw_shift], axis=2)
            z = (x - model["mean"]) / model["scale"]
            linear = model["beta"][0] + np.einsum("rnf,f->rn", z, model["beta"][1:])
            probability = scoring.sigmoid(linear)
            squared_error[start:stop] += np.sum(
                weight[None, :] * (probability - y[None, :]) ** 2, axis=1,
            )
        total_weight += float(weight.sum())
    null_brier = squared_error / total_weight
    parent_brier = scoring.metrics(predictions, "p_parent_state")["brier"]
    observed_brier = scoring.metrics(predictions, "p_parent_grandchild")["brier"]
    observed_improvement = parent_brier - observed_brier
    null_improvement = parent_brier - null_brier
    p_value = float((1 + np.sum(null_improvement >= observed_improvement)) / (1 + reps))
    table = pd.DataFrame({
        "replicate": np.arange(reps),
        "shifted_parent_grandchild_brier": null_brier,
        "improvement_over_parent_state": null_improvement,
    })
    summary = {
        "status": "posthoc_audit_not_frozen_gate",
        "reps": reps,
        "observed_parent_state_brier": parent_brier,
        "observed_parent_grandchild_brier": observed_brier,
        "observed_improvement_over_parent_state": observed_improvement,
        "null_improvement_median": float(np.median(null_improvement)),
        "null_improvement_q95": float(np.quantile(null_improvement, .95)),
        "p_ge_observed": p_value,
    }
    return table, summary


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    frame, events = build_geometry()
    predictions, fitted, coefficients = fit_leave_one_fluid_out(frame)
    overall, by_fluid = performance_tables(predictions)
    null_table, null_summary = grandchild_alignment_null(predictions, fitted)
    pg_null_table, pg_null_summary = parent_grandchild_alignment_audit(predictions, fitted)

    score = overall.set_index("model")
    fluid_score = by_fluid.pivot(index="fluid", columns="model", values="brier")
    improves_parent = fluid_score.three_point_lock < fluid_score.parent_state
    gates = {
        "lock_brier_below_parent_state": bool(score.loc["three_point_lock", "brier"] < score.loc["parent_state", "brier"]),
        "lock_brier_below_parent_child": bool(score.loc["three_point_lock", "brier"] < score.loc["parent_child", "brier"]),
        "lock_auc_above_parent_state": bool(score.loc["three_point_lock", "auc"] > score.loc["parent_state", "auc"]),
        "improves_parent_in_three_of_four_fluids": bool(int(improves_parent.sum()) >= 3),
        "aligned_grandchild_beats_shift_control_p_le_005": bool(null_summary["p_ge_observed"] <= .05),
    }
    result = {
        "status": "frozen_diagnostic_three_rung_grandchild_lock",
        "geometry": {
            "d_pc": "abs(r_child - r_parent)",
            "d_cg": "abs(r_grandchild - r_child)",
            "x_grandchild": "2*d_pc/(d_pc+d_cg)",
            "grandchild_window": "odd(max(3, child_window//2))",
            "outcome": "parent handover within one frozen child window",
        },
        "data": {
            "source_eligible_events": 123,
            "events_with_three_rung_snapshots": int(predictions.Name.nunique()),
            "snapshots": int(len(predictions)),
            "fluids": sorted(predictions.fluid.unique().tolist()),
            "event_counts": predictions.groupby("fluid").Name.nunique().astype(int).to_dict(),
            "snapshot_counts": predictions.groupby("fluid").size().astype(int).to_dict(),
        },
        "overall": overall.set_index("model").to_dict(orient="index"),
        "by_fluid_lock": by_fluid[by_fluid.model == "three_point_lock"].set_index("fluid").to_dict(orient="index"),
        "by_fluid_parent": by_fluid[by_fluid.model == "parent_state"].set_index("fluid").to_dict(orient="index"),
        "grandchild_alignment_null": null_summary,
        "posthoc_parent_grandchild_alignment": pg_null_summary,
        "gates": gates,
        "gate_count": int(sum(gates.values())),
        "supported": bool(all(gates.values())),
    }

    predictions.to_csv(OUT / "T411H_PREDICTIONS.csv", index=False)
    events.to_csv(OUT / "T411H_EVENTS.csv", index=False)
    overall.to_csv(OUT / "T411H_MODEL_PERFORMANCE.csv", index=False)
    by_fluid.to_csv(OUT / "T411H_FLUID_PERFORMANCE.csv", index=False)
    coefficients.to_csv(OUT / "T411H_COEFFICIENTS.csv", index=False)
    null_table.to_csv(OUT / "T411H_GRANDCHILD_SHIFT_NULL.csv", index=False)
    pg_null_table.to_csv(OUT / "T411H_PARENT_GRANDCHILD_SHIFT_AUDIT.csv", index=False)
    (OUT / "T411H_RESULTS.json").write_text(
        json.dumps(scoring.to_native(result), indent=2), encoding="utf-8",
    )
    print(json.dumps(scoring.to_native(result), indent=2))


if __name__ == "__main__":
    main()
