"""Frozen T411G causal child-parent Di-ARA transfer test."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
T411D = HERE / "results" / "T411D_causal_child_prediction"
T411F = HERE / "results" / "T411F_phase_a_probability"
OUT = HERE / "results" / "T411G_causal_di_ara"
SEED = 411007
SHIFT_REPS = 1000
L2 = 1e-3

MODELS = {
    "constant": [],
    "child_position": ["u"],
    "child_state": ["u", "du"],
    "parent_state": ["v", "dv"],
    "additive": ["u", "v", "du", "dv"],
    "di_ara": ["u", "v", "du", "dv", "uv", "radial_flow", "circulation"],
}


def sigmoid(z: np.ndarray) -> np.ndarray:
    z = np.clip(z, -35.0, 35.0)
    return 1.0 / (1.0 + np.exp(-z))


def weighted_auc(y: np.ndarray, score: np.ndarray, weight: np.ndarray) -> float:
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
        concordant += wp * (neg_before + 0.5 * wn)
        neg_before += wn
    return float(concordant / (pos_total * neg_total))


def metrics(frame: pd.DataFrame, prediction: str) -> dict:
    y = frame.y.to_numpy(float)
    p = frame[prediction].to_numpy(float)
    w = frame.event_weight.to_numpy(float)
    return {
        "brier": float(np.average((p - y) ** 2, weights=w)),
        "auc": weighted_auc(y, p, w),
        "base_probability": float(np.average(y, weights=w)),
        "events": int(frame.Name.nunique()),
        "snapshots": int(len(frame)),
        "weight": float(w.sum()),
    }


def standardize_fit(x: np.ndarray, weight: np.ndarray):
    mean = np.average(x, axis=0, weights=weight)
    var = np.average((x - mean) ** 2, axis=0, weights=weight)
    scale = np.sqrt(np.maximum(var, 1e-12))
    return mean, scale


def fit_logistic(x: np.ndarray, y: np.ndarray, weight: np.ndarray) -> np.ndarray:
    design = np.column_stack([np.ones(len(x)), x])
    w = weight / np.mean(weight)
    base = float(np.clip(np.average(y, weights=w), 1e-6, 1 - 1e-6))
    beta = np.zeros(design.shape[1], float)
    beta[0] = np.log(base / (1 - base))
    penalty = np.ones(design.shape[1], float)
    penalty[0] = 0.0
    for _ in range(100):
        p = sigmoid(design @ beta)
        working = w * p * (1 - p)
        hessian = design.T @ (working[:, None] * design)
        hessian += L2 * np.diag(penalty)
        gradient = design.T @ (w * (y - p)) - L2 * penalty * beta
        try:
            delta = np.linalg.solve(hessian, gradient)
        except np.linalg.LinAlgError:
            delta = np.linalg.lstsq(hessian, gradient, rcond=None)[0]
        beta += delta
        if float(np.max(np.abs(delta))) < 1e-9:
            break
    return beta


def predict_model(model: dict, x: np.ndarray) -> np.ndarray:
    if model["features"] == []:
        return np.repeat(model["probability"], len(x))
    z = (x - model["mean"]) / model["scale"]
    design = np.column_stack([np.ones(len(z)), z])
    return sigmoid(design @ model["beta"])


def fit_model(frame: pd.DataFrame, features: list[str]) -> dict:
    y = frame.y.to_numpy(float)
    w = frame.event_weight.to_numpy(float)
    if features == []:
        return {
            "features": [],
            "probability": float(np.average(y, weights=w)),
        }
    x = frame[features].to_numpy(float)
    mean, scale = standardize_fit(x, w)
    z = (x - mean) / scale
    beta = fit_logistic(z, y, w)
    return {
        "features": features,
        "mean": mean,
        "scale": scale,
        "beta": beta,
    }


def load_geometry() -> pd.DataFrame:
    snapshots = pd.read_csv(T411F / "T411F_SNAPSHOTS.csv")
    development = pd.read_csv(T411D / "T411D_DEVELOPMENT_TIMESERIES.csv")
    diagnostic = pd.read_csv(T411D / "T411D_HOLDOUT_TIMESERIES.csv")
    parent = pd.concat([development, diagnostic], ignore_index=True)
    snapshots["_time_key"] = snapshots.time_s.round(9)
    parent["_time_key"] = parent.Time_s.round(9)
    frame = snapshots.merge(
        parent[["Name", "_time_key", "x_parent_causal_ara"]],
        on=["Name", "_time_key"], how="left", validate="many_to_one",
    )
    frame = frame.rename(columns={
        "handover_within_child_window": "y",
        "phase_a": "x_child",
        "x_parent_causal_ara": "x_parent",
    })
    frame = frame[np.isfinite(frame.x_child) & np.isfinite(frame.x_parent)].copy()
    frame["x_child"] = frame.x_child.clip(0, 2)
    frame["x_parent"] = frame.x_parent.clip(0, 2)
    frame = frame.sort_values(["Name", "time_s"]).reset_index(drop=True)
    frame["du"] = frame.groupby("Name", sort=False).x_child.diff()
    frame["dv"] = frame.groupby("Name", sort=False).x_parent.diff()
    frame = frame[np.isfinite(frame.du) & np.isfinite(frame.dv)].copy()
    frame["u"] = frame.x_child - 1.0
    frame["v"] = frame.x_parent - 1.0
    frame["uv"] = frame.u * frame.v
    frame["radial_flow"] = frame.u * frame.du + frame.v * frame.dv
    frame["circulation"] = frame.u * frame.dv - frame.v * frame.du
    return frame.reset_index(drop=True)


def leave_one_fluid_out(frame: pd.DataFrame):
    fluids = sorted(frame.fluid.unique())
    predictions = []
    fitted: dict[tuple[str, str], dict] = {}
    coefficient_rows = []
    for heldout in fluids:
        train = frame[frame.fluid != heldout]
        test = frame[frame.fluid == heldout].copy()
        test["heldout_fluid"] = heldout
        for model_name, features in MODELS.items():
            model = fit_model(train, features)
            fitted[(heldout, model_name)] = model
            x_test = test[features].to_numpy(float) if features else np.empty((len(test), 0))
            test[f"p_{model_name}"] = predict_model(model, x_test)
            if features:
                coefficient_rows.append({
                    "heldout_fluid": heldout,
                    "model": model_name,
                    "term": "intercept",
                    "coefficient_standardized": float(model["beta"][0]),
                })
                for feature, coefficient in zip(features, model["beta"][1:]):
                    coefficient_rows.append({
                        "heldout_fluid": heldout,
                        "model": model_name,
                        "term": feature,
                        "coefficient_standardized": float(coefficient),
                    })
        predictions.append(test)
    return pd.concat(predictions, ignore_index=True), fitted, pd.DataFrame(coefficient_rows)


def performance_tables(predictions: pd.DataFrame):
    overall_rows = []
    fluid_rows = []
    for model_name in MODELS:
        pred_col = f"p_{model_name}"
        overall_rows.append({"model": model_name, **metrics(predictions, pred_col)})
        for fluid, group in predictions.groupby("fluid"):
            fluid_rows.append({
                "fluid": fluid,
                "model": model_name,
                **metrics(group, pred_col),
            })
    return pd.DataFrame(overall_rows), pd.DataFrame(fluid_rows)


def parent_alignment_null(predictions: pd.DataFrame, fitted: dict, reps: int = SHIFT_REPS):
    rng = np.random.default_rng(SEED)
    squared_error = np.zeros(reps, float)
    total_weight = 0.0
    features = MODELS["di_ara"]
    for (_, fluid), group in predictions.groupby(["Name", "fluid"], sort=False):
        group = group.sort_values("time_s")
        n = len(group)
        if n < 2:
            continue
        u = group.u.to_numpy(float)
        du = group.du.to_numpy(float)
        v = group.v.to_numpy(float)
        dv = group.dv.to_numpy(float)
        y = group.y.to_numpy(float)
        w = group.event_weight.to_numpy(float)
        model = fitted[(fluid, "di_ara")]
        for start in range(0, reps, 100):
            stop = min(start + 100, reps)
            count = stop - start
            offsets = rng.integers(1, n, size=count)
            indices = (np.arange(n)[None, :] - offsets[:, None]) % n
            v_shift = v[indices]
            dv_shift = dv[indices]
            u_grid = np.broadcast_to(u, v_shift.shape)
            du_grid = np.broadcast_to(du, v_shift.shape)
            x = np.stack([
                u_grid,
                v_shift,
                du_grid,
                dv_shift,
                u_grid * v_shift,
                u_grid * du_grid + v_shift * dv_shift,
                u_grid * dv_shift - v_shift * du_grid,
            ], axis=2)
            z = (x - model["mean"]) / model["scale"]
            linear = model["beta"][0] + np.einsum("rnf,f->rn", z, model["beta"][1:])
            p = sigmoid(linear)
            squared_error[start:stop] += np.sum(w[None, :] * (p - y[None, :]) ** 2, axis=1)
        total_weight += float(w.sum())
    null_brier = squared_error / total_weight
    child_brier = metrics(predictions, "p_child_state")["brier"]
    observed_di_brier = metrics(predictions, "p_di_ara")["brier"]
    observed_improvement = child_brier - observed_di_brier
    null_improvement = child_brier - null_brier
    p_value = float((1 + np.sum(null_improvement >= observed_improvement)) / (1 + reps))
    table = pd.DataFrame({
        "replicate": np.arange(reps),
        "shifted_di_ara_brier": null_brier,
        "improvement_over_child_state": null_improvement,
    })
    summary = {
        "reps": reps,
        "observed_child_state_brier": child_brier,
        "observed_di_ara_brier": observed_di_brier,
        "observed_improvement_over_child_state": observed_improvement,
        "null_improvement_median": float(np.median(null_improvement)),
        "null_improvement_q95": float(np.quantile(null_improvement, .95)),
        "p_ge_observed": p_value,
    }
    return table, summary


def to_native(value):
    if isinstance(value, dict):
        return {str(key): to_native(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_native(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    return value


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    frame = load_geometry()
    predictions, fitted, coefficients = leave_one_fluid_out(frame)
    overall, by_fluid = performance_tables(predictions)
    null_table, null_summary = parent_alignment_null(predictions, fitted)

    score = overall.set_index("model")
    fluid_score = by_fluid.pivot(index="fluid", columns="model", values="brier")
    improves_by_fluid = fluid_score.di_ara < fluid_score.constant
    gates = {
        "di_ara_brier_below_constant": bool(score.loc["di_ara", "brier"] < score.loc["constant", "brier"]),
        "di_ara_auc_above_half": bool(score.loc["di_ara", "auc"] > .5),
        "di_ara_brier_below_child_state": bool(score.loc["di_ara", "brier"] < score.loc["child_state", "brier"]),
        "di_ara_brier_below_additive": bool(score.loc["di_ara", "brier"] < score.loc["additive", "brier"]),
        "improves_constant_in_three_of_four_fluids": bool(int(improves_by_fluid.sum()) >= 3),
        "aligned_parent_beats_shift_control_p_le_005": bool(null_summary["p_ge_observed"] <= .05),
    }
    result = {
        "status": "frozen_diagnostic_cross_identity_di_ara",
        "geometry": {
            "child_axis": "u = x_child - 1",
            "parent_axis": "v = x_parent - 1",
            "radial_flow": "u*du + v*dv",
            "circulation": "u*dv - v*du",
            "outcome": "parent handover within one frozen child window",
        },
        "data": {
            "events": int(predictions.Name.nunique()),
            "snapshots": int(len(predictions)),
            "fluids": sorted(predictions.fluid.unique().tolist()),
        },
        "overall": overall.set_index("model").to_dict(orient="index"),
        "by_fluid_di_ara": by_fluid[by_fluid.model == "di_ara"].set_index("fluid").to_dict(orient="index"),
        "by_fluid_constant": by_fluid[by_fluid.model == "constant"].set_index("fluid").to_dict(orient="index"),
        "parent_alignment_null": null_summary,
        "gates": gates,
        "gate_count": int(sum(gates.values())),
        "supported": bool(all(gates.values())),
    }

    keep = [
        "Name", "fluid", "partition", "time_s", "target_t_s", "lead_s",
        "child_horizon_s", "y", "event_weight", "x_child", "x_parent",
        "u", "v", "du", "dv", "uv", "radial_flow", "circulation",
    ] + [f"p_{name}" for name in MODELS]
    predictions[keep].to_csv(OUT / "T411G_PREDICTIONS.csv", index=False)
    overall.to_csv(OUT / "T411G_MODEL_PERFORMANCE.csv", index=False)
    by_fluid.to_csv(OUT / "T411G_FLUID_PERFORMANCE.csv", index=False)
    coefficients.to_csv(OUT / "T411G_COEFFICIENTS.csv", index=False)
    null_table.to_csv(OUT / "T411G_PARENT_SHIFT_NULL.csv", index=False)
    (OUT / "T411G_RESULTS.json").write_text(
        json.dumps(to_native(result), indent=2), encoding="utf-8",
    )
    print(json.dumps(to_native(result), indent=2))


if __name__ == "__main__":
    main()

