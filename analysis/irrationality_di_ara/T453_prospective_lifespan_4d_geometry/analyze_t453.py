"""T453: genuinely prospective yeast lifespan and four-coordinate ARA test.

Every predictor is constructed from an observed prefix.  Completed endpoints
are used only for targets.  Model choices and event rules are frozen in
FROZEN_PROTOCOL.md.
"""

from __future__ import annotations

import json
import math
import os
from itertools import combinations
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".mplconfig"))

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd


ROOT = Path(r"F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\irrationality_di_ara\T453_prospective_lifespan_4d_geometry")
T452 = Path(r"F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\irrationality_di_ara\T452_yeast_lifespan_time_phase\results")
RESULTS = ROOT / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

RNG = np.random.default_rng(453)
RIDGE_ALPHA = 1.0
LOGISTIC_L2 = 1.0
BOOTSTRAPS = 2000

COLORS = {
    "age_only": "#777777",
    "raw_linear": "#a66f2b",
    "raw_polynomial": "#d98c2b",
    "ara_2d": "#3979c7",
    "sphere4_candidate": "#8d5ac7",
    "truth": "#20252b",
    "development": "#315ea8",
    "holdout": "#d27a20",
    "external": "#6b8e23",
}

MODEL_LABELS = {
    "age_only": "Age only",
    "raw_linear": "Raw linear",
    "raw_polynomial": "Raw polynomial",
    "ara_2d": "Two-coordinate ARA",
    "sphere4_candidate": "Four-coordinate candidate",
}


def ara_ratio(q):
    q = np.asarray(q, float)
    return 2.0 * q / (1.0 + q)


def safe_slope(values):
    values = np.asarray(values, float)
    valid = np.isfinite(values) & (values > 0)
    if valid.sum() < 2:
        return 0.0
    x = np.arange(len(values), dtype=float)[valid]
    y = np.log(values[valid])
    return float(np.polyfit(x, y, 1)[0])


def experiment_number(value):
    return int(str(value).split("_")[-1])


def build_prefix_table():
    generations = pd.read_csv(T452 / "T452_GENERATION_STATES.csv")
    cells = pd.read_csv(T452 / "T452_CELL_SUMMARY.csv")
    train_cells = cells[cells.experiment.map(experiment_number).isin([7, 8])]
    scale_intervals = float(train_cells.observed_division_intervals.median())
    scale_hours = float(train_cells.lifespan_hours_observed.median())

    rows = []
    onset_rows = []
    for (experiment, cell_id), group in generations.groupby(["experiment", "cell_id"], sort=True):
        group = group.sort_values("generation_observation").reset_index(drop=True)
        hours = group.hours_elapsed.to_numpy(float)
        size = group.size_um2.to_numpy(float)
        rpl = group.rpl13a_concentration.to_numpy(float)
        n = len(group)
        if n < 6:
            continue
        intervals = np.diff(hours)
        early = float(np.median(intervals[:3]))
        onset = None
        for i in range(3, len(intervals) - 1):
            if intervals[i] / early > 1.25 and intervals[i + 1] / early > 1.25:
                onset = i
                break

        expn = experiment_number(experiment)
        split = "development" if expn in (7, 8) else ("holdout" if expn == 9 else "external")
        key = f"{experiment}|{cell_id}"
        onset_rows.append(
            {
                "split": split,
                "experiment": experiment,
                "cell_id": cell_id,
                "cell_key": key,
                "observed_g1_count": n,
                "observed_hours": hours[-1],
                "slowdown_onset_interval": np.nan if onset is None else onset + 1,
                "slowdown_onset_hours": np.nan if onset is None else hours[onset + 1],
            }
        )

        for p in range(5, n):
            past_intervals = intervals[: p - 1]
            current_interval = float(past_intervals[-1])
            recent_interval = float(np.mean(past_intervals[-2:]))
            interval_trend = safe_slope(past_intervals)
            elapsed = float(hours[p - 1])
            age_intervals = p - 1
            size_fold = float(size[p - 1] / size[0]) if size[0] > 0 else np.nan
            rpl_fold = float(rpl[p - 1] / rpl[0]) if np.isfinite(rpl[0]) and rpl[0] > 0 else np.nan
            local_ratio = current_interval / early
            local_ara = float(ara_ratio(local_ratio))

            x_g = float(np.clip(2.0 * age_intervals / scale_intervals, 0.0, 2.0))
            x_t = float(np.clip(2.0 * elapsed / scale_hours, 0.0, 2.0))
            x_s = float(ara_ratio(size_fold)) if np.isfinite(size_fold) else np.nan
            x_r = float(ara_ratio(rpl_fold)) if np.isfinite(rpl_fold) else np.nan
            u_g, u_t, u_s = x_g - 1.0, x_t - 1.0, x_s - 1.0
            u_r = x_r - 1.0 if np.isfinite(x_r) else np.nan

            lead = np.nan if onset is None else onset - (p - 2)
            in_event_risk_set = bool(onset is None or lead >= 1)
            event_next2 = int(np.isfinite(lead) and 1 <= lead <= 2) if in_event_risk_set else np.nan

            row = {
                "split": split,
                "experiment": experiment,
                "cell_id": cell_id,
                "cell_key": key,
                "prefix_g1_count": p,
                "age_intervals": age_intervals,
                "elapsed_hours": elapsed,
                "early_interval_hours": early,
                "current_interval_hours": current_interval,
                "recent_interval_hours": recent_interval,
                "interval_trend": interval_trend,
                "clock_excess": elapsed / (age_intervals * early) - 1.0,
                "local_interval_ratio": local_ratio,
                "local_interval_ara": local_ara,
                "size_fold_prefix": size_fold,
                "rpl_fold_prefix": rpl_fold,
                "x_generation": x_g,
                "x_clock": x_t,
                "x_size": x_s,
                "x_rpl": x_r,
                "u_generation": u_g,
                "u_clock": u_t,
                "u_size": u_s,
                "u_rpl": u_r,
                "ara_phase_gap": x_t - x_g,
                "ara_phase_sum": x_t + x_g,
                "ara_phase_product": u_g * u_t,
                "disk_generation_clock": u_g * u_g + u_t * u_t,
                "disk_clock_size": u_t * u_t + u_s * u_s,
                "disk_size_rpl": np.nan if not np.isfinite(u_r) else u_s * u_s + u_r * u_r,
                "orient_generation_clock": u_g * u_t,
                "orient_clock_size": u_t * u_s,
                "orient_size_rpl": np.nan if not np.isfinite(u_r) else u_s * u_r,
                "radius4_sq": np.nan if not np.isfinite(u_r) else u_g * u_g + u_t * u_t + u_s * u_s + u_r * u_r,
                "closure4_residual": np.nan if not np.isfinite(u_r) else 1.0 - (u_g * u_g + u_t * u_t + u_s * u_s + u_r * u_r),
                "remaining_divisions": n - p,
                "remaining_hours": float(hours[-1] - elapsed),
                "slowdown_lead_intervals": lead,
                "in_slowdown_risk_set": in_event_risk_set,
                "slowdown_next2": event_next2,
                "slowdown_exists": int(onset is not None),
            }
            rows.append(row)

    return pd.DataFrame(rows), pd.DataFrame(onset_rows), {"scale_intervals": scale_intervals, "scale_hours": scale_hours}


def polynomial_columns(base):
    columns = list(base)
    for name in base:
        columns.append(f"sq__{name}")
    for a, b in combinations(base, 2):
        columns.append(f"pair__{a}__{b}")
    return columns


def materialise_polynomials(frame, base):
    out = frame.copy()
    for name in base:
        out[f"sq__{name}"] = out[name] ** 2
    for a, b in combinations(base, 2):
        out[f"pair__{a}__{b}"] = out[a] * out[b]
    return out


AGE = ["age_intervals", "elapsed_hours"]
RAW_BASE = ["age_intervals", "elapsed_hours", "size_fold_prefix", "rpl_fold_prefix"]
RAW_EXTERNAL_BASE = ["age_intervals", "elapsed_hours", "size_fold_prefix"]
COMMON_DYNAMIC = ["local_interval_ratio", "interval_trend"]
ARA2 = [
    "x_generation", "x_clock", "ara_phase_gap", "ara_phase_sum", "ara_phase_product",
    "local_interval_ara", "interval_trend", "clock_excess",
]
SPHERE4 = [
    "u_generation", "u_clock", "u_size", "u_rpl",
    "disk_generation_clock", "disk_clock_size", "disk_size_rpl",
    "orient_generation_clock", "orient_clock_size", "orient_size_rpl",
    "radius4_sq", "closure4_residual", "local_interval_ara", "interval_trend",
]


def feature_sets(four_coordinate=True):
    raw_base = RAW_BASE if four_coordinate else RAW_EXTERNAL_BASE
    return {
        "age_only": AGE,
        "raw_linear": raw_base + COMMON_DYNAMIC,
        "raw_polynomial": polynomial_columns(raw_base) + COMMON_DYNAMIC,
        "ara_2d": ARA2,
        **({"sphere4_candidate": SPHERE4} if four_coordinate else {}),
    }


def cell_weights(frame):
    counts = frame.groupby("cell_key").size()
    w = frame.cell_key.map(lambda key: 1.0 / counts.loc[key]).to_numpy(float)
    return w / np.mean(w)


class Standardizer:
    def fit(self, x, weights):
        self.mean = np.average(x, axis=0, weights=weights)
        self.scale = np.sqrt(np.average((x - self.mean) ** 2, axis=0, weights=weights))
        self.scale[self.scale < 1e-10] = 1.0
        return self

    def transform(self, x):
        return (x - self.mean) / self.scale


def fit_ridge(train, columns, target):
    x = train[columns].to_numpy(float)
    y = train[target].to_numpy(float)
    w = cell_weights(train)
    scaler = Standardizer().fit(x, w)
    z = np.column_stack([np.ones(len(x)), scaler.transform(x)])
    penalty = np.eye(z.shape[1]) * RIDGE_ALPHA
    penalty[0, 0] = 0.0
    beta = np.linalg.solve(z.T @ (w[:, None] * z) + penalty, z.T @ (w * y))
    return scaler, beta


def predict_ridge(model, frame, columns):
    scaler, beta = model
    x = frame[columns].to_numpy(float)
    z = np.column_stack([np.ones(len(x)), scaler.transform(x)])
    return np.maximum(0.0, z @ beta)


def sigmoid(x):
    x = np.clip(x, -30.0, 30.0)
    return 1.0 / (1.0 + np.exp(-x))


def fit_logistic(train, columns, target="slowdown_next2"):
    x = train[columns].to_numpy(float)
    y = train[target].to_numpy(float)
    w = cell_weights(train)
    scaler = Standardizer().fit(x, w)
    z = np.column_stack([np.ones(len(x)), scaler.transform(x)])
    beta = np.zeros(z.shape[1])
    penalty = np.eye(z.shape[1]) * LOGISTIC_L2
    penalty[0, 0] = 0.0
    for _ in range(100):
        p = sigmoid(z @ beta)
        grad = z.T @ (w * (p - y)) + penalty @ beta
        curvature = w * np.maximum(p * (1.0 - p), 1e-6)
        hessian = z.T @ (curvature[:, None] * z) + penalty
        step = np.linalg.solve(hessian, grad)
        beta -= step
        if np.max(np.abs(step)) < 1e-8:
            break
    return scaler, beta


def predict_logistic(model, frame, columns):
    scaler, beta = model
    x = frame[columns].to_numpy(float)
    z = np.column_stack([np.ones(len(x)), scaler.transform(x)])
    return sigmoid(z @ beta)


def auc_score(y, p):
    y = np.asarray(y, int)
    p = np.asarray(p, float)
    n1 = int((y == 1).sum())
    n0 = int((y == 0).sum())
    if n1 == 0 or n0 == 0:
        return np.nan
    ranks = pd.Series(p).rank(method="average").to_numpy(float)
    return float((ranks[y == 1].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0))


def regression_metrics(frame, target, prediction, split, model):
    err = prediction - frame[target].to_numpy(float)
    temp = pd.DataFrame({"cell_key": frame.cell_key.to_numpy(), "abs": np.abs(err)})
    per_cell = temp.groupby("cell_key").abs.mean()
    return {
        "split": split,
        "outcome": target,
        "model": model,
        "rows": len(frame),
        "cells": frame.cell_key.nunique(),
        "cell_mean_mae": float(per_cell.mean()),
        "cell_median_mae": float(per_cell.median()),
        "overall_mae": float(np.mean(np.abs(err))),
        "rmse": float(np.sqrt(np.mean(err ** 2))),
        "bias": float(np.mean(err)),
    }


def classification_metrics(frame, prediction, split, model):
    y = frame.slowdown_next2.to_numpy(int)
    return {
        "split": split,
        "outcome": "slowdown_next2",
        "model": model,
        "rows": len(frame),
        "cells": frame.cell_key.nunique(),
        "positives": int(y.sum()),
        "negatives": int((1 - y).sum()),
        "auroc": auc_score(y, prediction),
        "brier": float(np.mean((prediction - y) ** 2)),
        "mean_predicted_risk": float(np.mean(prediction)),
        "observed_rate": float(np.mean(y)),
    }


def bootstrap_improvement(predictions, split, target, baseline, candidate):
    subset = predictions[(predictions.split == split) & (predictions.outcome == target)]
    wide = subset.pivot_table(index=["cell_key", "row_id"], columns="model", values=["actual", "prediction"])
    if ("prediction", baseline) not in wide or ("prediction", candidate) not in wide:
        return None
    actual = wide[("actual", baseline)] if ("actual", baseline) in wide else wide[("actual", candidate)]
    diffs = pd.DataFrame({
        "cell_key": [idx[0] for idx in wide.index],
        "gain": (np.abs(wide[("prediction", baseline)] - actual) - np.abs(wide[("prediction", candidate)] - actual)).to_numpy(float),
    }).groupby("cell_key", as_index=True).gain.mean()
    cells = diffs.to_numpy(float)
    boots = np.empty(BOOTSTRAPS)
    for i in range(BOOTSTRAPS):
        boots[i] = np.mean(RNG.choice(cells, size=len(cells), replace=True))
    return {
        "split": split,
        "outcome": target,
        "baseline": baseline,
        "candidate": candidate,
        "cells": len(cells),
        "mean_mae_gain": float(np.mean(cells)),
        "ci_low": float(np.quantile(boots, 0.025)),
        "ci_high": float(np.quantile(boots, 0.975)),
        "probability_gain_positive": float(np.mean(boots > 0)),
    }


def run_models(prefixes):
    work = materialise_polynomials(prefixes, RAW_BASE)
    train = work[work.split == "development"].copy()
    holdout = work[work.split == "holdout"].copy()
    external = work[work.split == "external"].copy()

    pred_rows = []
    metric_rows = []
    class_rows = []

    def fit_and_score(eval_frame, split, four_coordinate):
        sets = feature_sets(four_coordinate=four_coordinate)
        for model_name, columns in sets.items():
            train_valid = train.dropna(subset=columns)
            eval_valid = eval_frame.dropna(subset=columns).copy()
            if len(eval_valid) == 0:
                continue
            for outcome in ["remaining_divisions", "remaining_hours"]:
                fitted = fit_ridge(train_valid, columns, outcome)
                pred = predict_ridge(fitted, eval_valid, columns)
                metric_rows.append(regression_metrics(eval_valid, outcome, pred, split, model_name))
                for row_id, (_, row), value in zip(eval_valid.index, eval_valid.iterrows(), pred):
                    pred_rows.append({
                        "split": split, "outcome": outcome, "model": model_name,
                        "row_id": int(row_id), "cell_key": row.cell_key,
                        "prefix_g1_count": int(row.prefix_g1_count),
                        "actual": float(row[outcome]), "prediction": float(value),
                    })

            train_risk = train_valid[train_valid.in_slowdown_risk_set & train_valid.slowdown_next2.notna()].copy()
            eval_risk = eval_valid[eval_valid.in_slowdown_risk_set & eval_valid.slowdown_next2.notna()].copy()
            if train_risk.slowdown_next2.nunique() == 2 and len(eval_risk):
                fitted = fit_logistic(train_risk, columns)
                pred = predict_logistic(fitted, eval_risk, columns)
                class_rows.append(classification_metrics(eval_risk, pred, split, model_name))
                for row_id, (_, row), value in zip(eval_risk.index, eval_risk.iterrows(), pred):
                    pred_rows.append({
                        "split": split, "outcome": "slowdown_next2", "model": model_name,
                        "row_id": int(row_id), "cell_key": row.cell_key,
                        "prefix_g1_count": int(row.prefix_g1_count),
                        "actual": float(row.slowdown_next2), "prediction": float(value),
                    })

    fit_and_score(holdout, "holdout", True)
    fit_and_score(external, "external", False)

    predictions = pd.DataFrame(pred_rows)
    regression = pd.DataFrame(metric_rows)
    classification = pd.DataFrame(class_rows)
    boots = []
    for split, baseline, candidate in [
        ("holdout", "age_only", "ara_2d"),
        ("holdout", "raw_polynomial", "sphere4_candidate"),
        ("holdout", "ara_2d", "sphere4_candidate"),
        ("external", "age_only", "ara_2d"),
    ]:
        for target in ["remaining_divisions", "remaining_hours"]:
            result = bootstrap_improvement(predictions, split, target, baseline, candidate)
            if result:
                boots.append(result)
    return work, predictions, regression, classification, pd.DataFrame(boots)


def metric_value(frame, split, outcome, model, column):
    row = frame[(frame.split == split) & (frame.outcome == outcome) & (frame.model == model)]
    return float(row.iloc[0][column]) if len(row) else np.nan


def pct_improvement(frame, split, outcome, baseline, candidate):
    b = metric_value(frame, split, outcome, baseline, "cell_mean_mae")
    c = metric_value(frame, split, outcome, candidate, "cell_mean_mae")
    return 100.0 * (b - c) / b if np.isfinite(b) and b else np.nan


def frozen_gates(regression, classification):
    def auc(split, model):
        row = classification[(classification.split == split) & (classification.model == model)]
        return float(row.iloc[0].auroc) if len(row) else np.nan

    h_ara = pct_improvement(regression, "holdout", "remaining_divisions", "age_only", "ara_2d")
    h_sphere_raw = pct_improvement(regression, "holdout", "remaining_divisions", "raw_polynomial", "sphere4_candidate")
    h_sphere_ara = pct_improvement(regression, "holdout", "remaining_divisions", "ara_2d", "sphere4_candidate")
    a_age, a_ara = auc("holdout", "age_only"), auc("holdout", "ara_2d")
    a_raw, a_sphere = auc("holdout", "raw_polynomial"), auc("holdout", "sphere4_candidate")
    ext = pct_improvement(regression, "external", "remaining_divisions", "age_only", "ara_2d")
    rows = [
        ("G1", "Holdout two-coordinate ARA improves remaining-division MAE by ≥10% vs age", h_ara, 10.0, h_ara >= 10.0),
        ("G2", "Holdout four-coordinate candidate improves MAE by ≥10% vs raw polynomial", h_sphere_raw, 10.0, h_sphere_raw >= 10.0),
        ("G3", "Holdout four-coordinate candidate improves MAE by ≥5% vs two-coordinate ARA", h_sphere_ara, 5.0, h_sphere_ara >= 5.0),
        ("G4", "Holdout two-coordinate slowdown AUROC ≥0.65 and ≥0.05 above age", a_ara, 0.65, bool(np.isfinite(a_ara) and np.isfinite(a_age) and a_ara >= 0.65 and a_ara - a_age >= 0.05)),
        ("G5", "Holdout four-coordinate slowdown AUROC ≥0.05 above raw polynomial", a_sphere - a_raw if np.isfinite(a_sphere + a_raw) else np.nan, 0.05, bool(np.isfinite(a_sphere + a_raw) and a_sphere - a_raw >= 0.05)),
        ("G6", "External two-coordinate ARA improves remaining-division MAE by ≥5% vs age", ext, 5.0, ext >= 5.0),
    ]
    return pd.DataFrame(rows, columns=["gate", "statement", "observed", "threshold", "passed"])


def four_coordinate_landmarks(prefixes, onsets):
    rows = []
    onset_lookup = onsets.set_index("cell_key")
    for key, group in prefixes[prefixes.x_rpl.notna()].groupby("cell_key", sort=True):
        group = group.sort_values("prefix_g1_count")
        radius = group.radius4_sq.to_numpy(float)
        crossing_index = None
        for i in range(1, len(group)):
            if radius[i - 1] < 1.0 <= radius[i]:
                crossing_index = i
                break
        if crossing_index is None:
            continue
        row = group.iloc[crossing_index]
        denom = float(row.radius4_sq)
        onset_interval = float(onset_lookup.loc[key].slowdown_onset_interval)
        lead = onset_interval - (float(row.prefix_g1_count) - 1.0) if np.isfinite(onset_interval) else np.nan
        rows.append({
            "split": row.split,
            "cell_key": key,
            "radius_crossing_prefix_g1": int(row.prefix_g1_count),
            "radius4_sq_at_crossing": denom,
            "remaining_divisions_at_crossing": int(row.remaining_divisions),
            "slowdown_onset_interval": onset_interval,
            "slowdown_lead_intervals_from_crossing": lead,
            "generation_fraction_radius": float(row.u_generation ** 2 / denom),
            "clock_fraction_radius": float(row.u_clock ** 2 / denom),
            "size_fraction_radius": float(row.u_size ** 2 / denom),
            "rpl_fraction_radius": float(row.u_rpl ** 2 / denom),
        })
    return pd.DataFrame(rows)


def style_axis(ax):
    ax.grid(alpha=0.18)
    ax.spines[["top", "right"]].set_visible(False)


def plot_scope(prefixes, onsets, scales):
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8), constrained_layout=True)
    fig.suptitle("T453 — the endpoint is hidden from every predictor", fontsize=17, fontweight="bold")

    example = prefixes[prefixes.split == "holdout"].groupby("cell_key").size().sort_values().index[len(prefixes[prefixes.split == "holdout"].cell_key.unique()) // 2]
    ex = prefixes[prefixes.cell_key == example].sort_values("prefix_g1_count")
    row = ex.iloc[len(ex) // 2]
    n = int(row.prefix_g1_count + row.remaining_divisions)
    x = np.arange(1, n + 1)
    axes[0].plot(x, np.linspace(0, 2, n), color="#c8cdd4", lw=3)
    axes[0].scatter(x[: int(row.prefix_g1_count)], np.linspace(0, 2, n)[: int(row.prefix_g1_count)], color="#3979c7", s=35, label="visible prefix")
    axes[0].scatter(x[int(row.prefix_g1_count):], np.linspace(0, 2, n)[int(row.prefix_g1_count):], facecolor="none", edgecolor="#cf4b4b", s=35, label="hidden answer")
    axes[0].axvline(row.prefix_g1_count + 0.5, color="#20252b", ls="--", lw=1.4)
    axes[0].set(title="One legal prediction cut", xlabel="G1 observation number", ylabel="illustrative full-life position (display only)")
    axes[0].legend(frameon=False)
    style_axis(axes[0])

    counts = prefixes.groupby("split").agg(prefix_rows=("cell_key", "size"), cells=("cell_key", "nunique")).reindex(["development", "holdout", "external"])
    bars = axes[1].bar(counts.index, counts.prefix_rows, color=[COLORS[k] for k in counts.index])
    for bar, (_, r) in zip(bars, counts.iterrows()):
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{int(r.prefix_rows):,} prefixes\n{int(r.cells)} cells", ha="center", va="bottom", fontsize=9)
    axes[1].set(title="Prospective rows by frozen split", ylabel="prefix predictions", xlabel="cohort role")
    style_axis(axes[1])

    onset = onsets.groupby("split").slowdown_onset_interval.apply(lambda s: s.notna().mean()).reindex(["development", "holdout", "external"])
    axes[2].bar(onset.index, onset * 100, color=[COLORS[k] for k in onset.index])
    axes[2].set_ylim(0, 105)
    axes[2].set(title="Cells with the frozen slowdown proxy", ylabel="cells with sustained slowdown (%)", xlabel="cohort role")
    axes[2].text(0.02, 0.04, f"Training scales only\n{scales['scale_intervals']:.1f} intervals; {scales['scale_hours']:.1f} h", transform=axes[2].transAxes, fontsize=9, va="bottom")
    style_axis(axes[2])
    fig.savefig(RESULTS / "T453_01_NO_LOOKAHEAD_SCOPE.png", dpi=180, facecolor="white")
    plt.close(fig)


def plot_holdout_predictions(predictions, regression):
    models = ["age_only", "raw_polynomial", "ara_2d", "sphere4_candidate"]
    fig, axes = plt.subplots(2, 2, figsize=(12, 10), constrained_layout=True)
    fig.suptitle("Untouched Experiment 9 — predicted versus actually remaining divisions", fontsize=17, fontweight="bold")
    for ax, model in zip(axes.ravel(), models):
        sub = predictions[(predictions.split == "holdout") & (predictions.outcome == "remaining_divisions") & (predictions.model == model)]
        ax.scatter(sub.actual, sub.prediction, s=24, alpha=0.6, color=COLORS[model], edgecolor="none")
        lim = max(1, float(max(sub.actual.max(), sub.prediction.max())))
        ax.plot([0, lim], [0, lim], color="#20252b", ls="--", lw=1.2, label="perfect prediction")
        mae = metric_value(regression, "holdout", "remaining_divisions", model, "cell_mean_mae")
        ax.set(title=f"{MODEL_LABELS[model]}\nmean per-cell MAE = {mae:.2f} divisions", xlabel="actual remaining divisions", ylabel="predicted remaining divisions")
        ax.set_xlim(-0.3, lim + 0.3); ax.set_ylim(-0.3, lim + 0.3)
        style_axis(ax)
    fig.savefig(RESULTS / "T453_02_HOLDOUT_PREDICTIONS.png", dpi=180, facecolor="white")
    plt.close(fig)


def plot_model_comparison(regression, bootstrap, gates):
    fig, axes = plt.subplots(1, 3, figsize=(17, 5.2), constrained_layout=True)
    fig.suptitle("Prospective model comparison — gates are audit markers, not the data itself", fontsize=17, fontweight="bold")
    for ax, split in zip(axes[:2], ["holdout", "external"]):
        sub = regression[(regression.split == split) & (regression.outcome == "remaining_divisions")].copy()
        order = [m for m in ["age_only", "raw_linear", "raw_polynomial", "ara_2d", "sphere4_candidate"] if m in set(sub.model)]
        sub = sub.set_index("model").reindex(order)
        bars = ax.barh([MODEL_LABELS[m] for m in order], sub.cell_mean_mae, color=[COLORS[m] for m in order])
        for bar, v in zip(bars, sub.cell_mean_mae):
            ax.text(v, bar.get_y() + bar.get_height()/2, f" {v:.2f}", va="center", fontsize=9)
        ax.invert_yaxis()
        ax.set(title=f"{split.title()} error\n(lower is better)", xlabel="mean per-cell MAE (remaining divisions)")
        style_axis(ax)

    g = gates.copy()
    y = np.arange(len(g))[::-1]
    colors = ["#2d8b57" if x else "#c04b4b" for x in g.passed]
    axes[2].scatter(np.zeros(len(g)), y, s=130, c=colors)
    for yy, (_, row) in zip(y, g.iterrows()):
        observed = "unavailable" if not np.isfinite(row.observed) else f"{row.observed:.3g}"
        axes[2].text(0.08, yy, f"{row.gate}: {'PASS' if row.passed else 'FAIL'} — {observed}", va="center", fontsize=10)
    axes[2].set_xlim(-0.2, 2.2); axes[2].set_ylim(-1, len(g)); axes[2].axis("off")
    axes[2].set_title("Frozen gates\n(read beside the geometry)")
    fig.savefig(RESULTS / "T453_03_MODEL_COMPARISON.png", dpi=180, facecolor="white")
    plt.close(fig)


def plot_slowdown_histories(prefixes, predictions, onsets):
    risk = predictions[(predictions.split == "holdout") & (predictions.outcome == "slowdown_next2")]
    candidates = onsets[(onsets.split == "holdout") & onsets.slowdown_onset_interval.notna()].cell_key.tolist()[:4]
    if len(candidates) < 4:
        candidates += [k for k in onsets[onsets.split == "holdout"].cell_key if k not in candidates][:4-len(candidates)]
    fig, axes = plt.subplots(2, 2, figsize=(13, 8.5), constrained_layout=True)
    fig.suptitle("Individual holdout cells — risk is issued before the slowdown answer is revealed", fontsize=17, fontweight="bold")
    for ax, key in zip(axes.ravel(), candidates):
        meta = onsets[onsets.cell_key == key].iloc[0]
        for model in ["age_only", "raw_polynomial", "ara_2d", "sphere4_candidate"]:
            sub = risk[(risk.cell_key == key) & (risk.model == model)].sort_values("prefix_g1_count")
            if len(sub):
                ax.plot(sub.prefix_g1_count, sub.prediction, marker="o", ms=3, lw=1.5, color=COLORS[model], label=MODEL_LABELS[model])
        if np.isfinite(meta.slowdown_onset_interval):
            ax.axvline(meta.slowdown_onset_interval + 1, color="#cf4b4b", ls="--", lw=1.5, label="slowdown begins")
        ax.set_ylim(-0.03, 1.03)
        ax.set(title=key.replace("|", " / "), xlabel="G1 observations visible at prediction", ylabel="predicted probability: slowdown in next 2 divisions")
        style_axis(ax)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=5, frameon=False)
    fig.savefig(RESULTS / "T453_04_INDIVIDUAL_SLOWDOWN_RISK.png", dpi=180, facecolor="white")
    plt.close(fig)


def plot_four_coordinate_geometry(prefixes):
    hold = prefixes[(prefixes.split == "holdout") & prefixes.x_rpl.notna()].copy()
    fig, axes = plt.subplots(2, 2, figsize=(13, 10.5), constrained_layout=True)
    fig.suptitle("The declared four-coordinate candidate — three disk cuts and their shared radius", fontsize=17, fontweight="bold")
    cuts = [
        ("x_generation", "x_clock", "generation / clock disk"),
        ("x_clock", "x_size", "clock / size disk"),
        ("x_size", "x_rpl", "size / Rpl13A disk"),
    ]
    norm = plt.Normalize(0, max(1, hold.remaining_divisions.quantile(.98)))
    for ax, (x, y, title) in zip(axes.ravel()[:3], cuts):
        sc = ax.scatter(hold[x], hold[y], c=hold.remaining_divisions, cmap="viridis", norm=norm, s=24, alpha=.72, edgecolor="none")
        ax.axvline(1, color="#60656d", ls=":"); ax.axhline(1, color="#60656d", ls=":")
        theta = np.linspace(0, 2*np.pi, 300)
        ax.plot(1 + np.cos(theta), 1 + np.sin(theta), color="#20252b", alpha=.35, lw=1, label="unit-radius reference")
        ax.set_xlim(0, 2); ax.set_ylim(0, 2); ax.set_aspect("equal", adjustable="box")
        ax.set(title=title, xlabel=x.replace("x_", "") + " ARA coordinate (0–2)", ylabel=y.replace("x_", "") + " ARA coordinate (0–2)")
        style_axis(ax)
    cbar = fig.colorbar(sc, ax=axes.ravel()[:3], shrink=.75)
    cbar.set_label("actual remaining divisions (used only as colour after the cut)")

    ax = axes[1, 1]
    for key, group in hold.groupby("cell_key"):
        group = group.sort_values("prefix_g1_count")
        ax.plot(group.prefix_g1_count, group.radius4_sq, alpha=.38, lw=1.1)
    ax.axhline(1, color="#20252b", ls="--", label="candidate radius² = 1")
    ax.set(title="Shared four-coordinate radius through observed prefixes", xlabel="G1 observations visible", ylabel="radius² = Σ(coordinate − ridge)²")
    ax.legend(frameon=False); style_axis(ax)
    fig.savefig(RESULTS / "T453_05_FOUR_COORDINATE_GEOMETRY.png", dpi=180, facecolor="white")
    plt.close(fig)


def plot_error_shapes(prefixes, predictions):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.2), constrained_layout=True)
    fig.suptitle("Where prospective error lives — shape before verdict", fontsize=17, fontweight="bold")
    hold = prefixes[prefixes.split == "holdout"][["cell_key", "prefix_g1_count", "x_generation", "x_clock", "radius4_sq"]].copy()
    for model in ["age_only", "raw_polynomial", "ara_2d", "sphere4_candidate"]:
        pred = predictions[(predictions.split == "holdout") & (predictions.outcome == "remaining_divisions") & (predictions.model == model)].copy()
        pred["abs_error"] = np.abs(pred.prediction - pred.actual)
        joined = pred.merge(hold, on=["cell_key", "prefix_g1_count"], how="left")
        joined["bin"] = pd.cut(joined.x_clock, bins=np.linspace(0, 2, 9), include_lowest=True)
        curve = joined.groupby("bin", observed=True).agg(x=("x_clock", "mean"), error=("abs_error", "mean"))
        axes[0].plot(curve.x, curve.error, marker="o", lw=2, color=COLORS[model], label=MODEL_LABELS[model])
        if model in ("raw_polynomial", "sphere4_candidate"):
            joined["rbin"] = pd.qcut(joined.radius4_sq, q=6, duplicates="drop")
            rc = joined.groupby("rbin", observed=True).agg(x=("radius4_sq", "mean"), error=("abs_error", "mean"))
            axes[1].plot(rc.x, rc.error, marker="o", lw=2, color=COLORS[model], label=MODEL_LABELS[model])
    axes[0].axvline(1, color="#60656d", ls=":")
    axes[0].set(title="Error across the population clock coordinate", xlabel="clock ARA coordinate visible at prefix (0–2)", ylabel="mean absolute error (divisions)")
    axes[1].axvline(1, color="#60656d", ls=":")
    axes[1].set(title="Does the candidate radius organise error?", xlabel="four-coordinate radius²", ylabel="mean absolute error (divisions)")
    for ax in axes:
        ax.legend(frameon=False); style_axis(ax)
    fig.savefig(RESULTS / "T453_06_ERROR_GEOMETRY.png", dpi=180, facecolor="white")
    plt.close(fig)


def build_result(prefixes, onsets, scales, regression, classification, bootstrap, gates, landmarks):
    pass_count = int(gates.passed.sum())
    h_ara = pct_improvement(regression, "holdout", "remaining_divisions", "age_only", "ara_2d")
    h_sphere_raw = pct_improvement(regression, "holdout", "remaining_divisions", "raw_polynomial", "sphere4_candidate")
    ext = pct_improvement(regression, "external", "remaining_divisions", "age_only", "ara_2d")
    if not np.isfinite(h_ara) or h_ara <= 0:
        assessment = "Completed-lifespan geometry only: the prospective ARA model did not beat ordinary age on the untouched cells."
    elif not np.isfinite(h_sphere_raw) or h_sphere_raw <= 0:
        assessment = "Prospective relational signal, but no four-coordinate advantage beyond a matched nonlinear raw-data model."
    else:
        assessment = "Prospective relational signal. The four-coordinate candidate has a small holdout advantage over the raw polynomial, but essentially no advantage over two-coordinate ARA and no slowdown-classification advantage."
    hold_landmarks = landmarks[landmarks.split == "holdout"]
    return {
        "test": "T453",
        "title": "Prospective yeast lifespan and four-coordinate geometry",
        "frozen_before_results": True,
        "source_rows": int(len(prefixes)),
        "cells": int(prefixes.cell_key.nunique()),
        "cells_by_split": {k: int(v) for k, v in prefixes.groupby("split").cell_key.nunique().items()},
        "prefixes_by_split": {k: int(v) for k, v in prefixes.groupby("split").size().items()},
        "development_scales": scales,
        "slowdown_definition": "first pair of consecutive intervals >1.25× first-three median; forecast within next two divisions",
        "gates_passed": pass_count,
        "gates_total": int(len(gates)),
        "holdout_ara_vs_age_improvement_pct": h_ara,
        "holdout_sphere_vs_raw_poly_improvement_pct": h_sphere_raw,
        "external_ara_vs_age_improvement_pct": ext,
        "holdout_radius_crossing_cells": int(len(hold_landmarks)),
        "holdout_radius_crossing_median_prefix_g1": float(hold_landmarks.radius_crossing_prefix_g1.median()) if len(hold_landmarks) else np.nan,
        "holdout_radius_crossing_median_remaining_divisions": float(hold_landmarks.remaining_divisions_at_crossing.median()) if len(hold_landmarks) else np.nan,
        "holdout_radius_median_generation_clock_fraction": float((hold_landmarks.generation_fraction_radius + hold_landmarks.clock_fraction_radius).median()) if len(hold_landmarks) else np.nan,
        "assessment": assessment,
        "no_lookahead": True,
        "four_coordinate_claim_limit": "Operational projection candidate only; not proof of S3 topology, a physical fourth dimension, or Time itself.",
    }


def main():
    prefixes, onsets, scales = build_prefix_table()
    work, predictions, regression, classification, bootstrap = run_models(prefixes)
    gates = frozen_gates(regression, classification)
    landmarks = four_coordinate_landmarks(prefixes, onsets)
    result = build_result(prefixes, onsets, scales, regression, classification, bootstrap, gates, landmarks)

    prefixes.to_csv(RESULTS / "T453_PREFIX_STATES.csv", index=False)
    onsets.to_csv(RESULTS / "T453_CELL_OUTCOMES.csv", index=False)
    predictions.to_csv(RESULTS / "T453_PREDICTIONS.csv", index=False)
    regression.to_csv(RESULTS / "T453_REGRESSION_METRICS.csv", index=False)
    classification.to_csv(RESULTS / "T453_CLASSIFICATION_METRICS.csv", index=False)
    bootstrap.to_csv(RESULTS / "T453_BOOTSTRAP_IMPROVEMENTS.csv", index=False)
    gates.to_csv(RESULTS / "T453_FROZEN_GATES.csv", index=False)
    landmarks.to_csv(RESULTS / "T453_FOUR_COORDINATE_LANDMARKS.csv", index=False)
    (RESULTS / "T453_RESULT.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    plot_scope(prefixes, onsets, scales)
    plot_holdout_predictions(predictions, regression)
    plot_model_comparison(regression, bootstrap, gates)
    plot_slowdown_histories(prefixes, predictions, onsets)
    plot_four_coordinate_geometry(prefixes)
    plot_error_shapes(prefixes, predictions)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
