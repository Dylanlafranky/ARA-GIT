"""T411J: frozen parity-oriented, coefficient-free three-rung closure test."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import t411g_causal_di_ara as scoring


HERE = Path(__file__).resolve().parent
INPUT = HERE / "results" / "T411H_three_rung_grandchild_lock" / "T411H_PREDICTIONS.csv"
OUT = HERE / "results" / "T411J_parity_oriented_closure"
SEED = 411010
SHIFT_REPS = 1000
BOOTSTRAP_REPS = 2000

PARITIES = {
    "no_flip": (1.0, 1.0),
    "child_flip": (-1.0, 1.0),
    "grandchild_flip": (1.0, -1.0),
    "both_lower_flip": (-1.0, -1.0),
}


def closure(v: np.ndarray, u: np.ndarray, w: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    spread = (np.abs(v - u) + np.abs(u - w) + np.abs(w - v)) / 4.0
    agreement = np.clip(1.0 - spread, 0.0, 1.0)
    common_coordinate = (v + u + w) / 3.0
    ridge_gate = np.clip(1.0 - np.abs(common_coordinate), 0.0, 1.0)
    return agreement, ridge_gate, agreement * ridge_gate


def weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    return float(np.average(values, weights=weights))


def weighted_auc(y: np.ndarray, score: np.ndarray, weight: np.ndarray) -> float:
    """Vectorized weighted AUC with half credit for tied scores."""
    order = np.argsort(score, kind="mergesort")
    sorted_score = score[order]
    sorted_y = y[order]
    sorted_weight = weight[order]
    starts = np.r_[0, 1 + np.flatnonzero(np.diff(sorted_score) != 0)]
    positive_weight = np.add.reduceat(sorted_weight * (sorted_y == 1), starts)
    negative_weight = np.add.reduceat(sorted_weight * (sorted_y == 0), starts)
    positive_total = float(positive_weight.sum())
    negative_total = float(negative_weight.sum())
    if positive_total <= 0 or negative_total <= 0:
        return np.nan
    negative_before = np.cumsum(negative_weight) - negative_weight
    concordant = np.sum(positive_weight * (negative_before + 0.5 * negative_weight))
    return float(concordant / (positive_total * negative_total))


def score_metrics(frame: pd.DataFrame, column: str) -> dict[str, float | int]:
    y = frame["y"].to_numpy(float)
    score = frame[column].to_numpy(float)
    weight = frame["event_weight"].to_numpy(float)
    positive = y == 1
    negative = ~positive
    return {
        "auc": weighted_auc(y, score, weight),
        "positive_weighted_mean": weighted_mean(score[positive], weight[positive]),
        "negative_weighted_mean": weighted_mean(score[negative], weight[negative]),
        "mean_difference_positive_minus_negative": (
            weighted_mean(score[positive], weight[positive])
            - weighted_mean(score[negative], weight[negative])
        ),
        "events": int(frame["Name"].nunique()),
        "snapshots": int(len(frame)),
    }


def build_scores(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.sort_values(["Name", "time_s"]).reset_index(drop=True).copy()
    v = frame["v"].to_numpy(float)
    u = frame["u"].to_numpy(float)
    w = frame["w"].to_numpy(float)
    for name, (u_sign, w_sign) in PARITIES.items():
        agreement, ridge, handover = closure(v, u_sign * u, w_sign * w)
        frame[f"agreement_{name}"] = agreement
        frame[f"ridge_{name}"] = ridge
        frame[f"handover_{name}"] = handover
    frame["posthoc_channel_switch"] = (
        frame["handover_grandchild_flip"] - frame["handover_child_flip"]
    )
    frame["lead_child_horizons"] = frame["lead_s"] / frame["child_horizon_s"]
    return frame


def performance_tables(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    overall_rows = []
    fluid_rows = []
    for parity in PARITIES:
        for component in ("agreement", "handover"):
            column = f"{component}_{parity}"
            overall_rows.append({
                "parity": parity,
                "component": component,
                **score_metrics(frame, column),
            })
            for fluid, group in frame.groupby("fluid", sort=True):
                fluid_rows.append({
                    "fluid": fluid,
                    "parity": parity,
                    "component": component,
                    **score_metrics(group, column),
                })
    return pd.DataFrame(overall_rows), pd.DataFrame(fluid_rows)


def lead_profile(frame: pd.DataFrame) -> pd.DataFrame:
    bins = [0.0, 1.0, 2.0, 4.0, 8.0, np.inf]
    labels = ["(0,1]", "(1,2]", "(2,4]", "(4,8]", ">8"]
    frame = frame.copy()
    frame["lead_bin"] = pd.cut(
        frame["lead_child_horizons"], bins=bins, labels=labels,
        include_lowest=False, right=True,
    )
    rows = []
    columns = [f"handover_{name}" for name in PARITIES]
    for lead_bin, group in frame.groupby("lead_bin", observed=True, sort=False):
        weight = group["event_weight"].to_numpy(float)
        for column in columns:
            rows.append({
                "lead_bin": str(lead_bin),
                "parity": column.removeprefix("handover_"),
                "weighted_mean_score": weighted_mean(group[column].to_numpy(float), weight),
                "events": int(group["Name"].nunique()),
                "snapshots": int(len(group)),
            })
    return pd.DataFrame(rows)


def shifted_child_null(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    rng = np.random.default_rng(SEED)
    frame = frame.sort_values(["Name", "time_s"]).reset_index(drop=True)
    v = frame["v"].to_numpy(float)
    u = frame["u"].to_numpy(float)
    w = frame["w"].to_numpy(float)
    y = frame["y"].to_numpy(float)
    weight = frame["event_weight"].to_numpy(float)
    groups = [indices.to_numpy(int) for _, indices in frame.groupby("Name", sort=True).groups.items()]
    observed = weighted_auc(y, frame["handover_child_flip"].to_numpy(float), weight)
    null_auc = np.empty(SHIFT_REPS, float)
    shifted_u = np.empty_like(u)
    for repetition in range(SHIFT_REPS):
        for indices in groups:
            if len(indices) <= 1:
                shifted_u[indices] = u[indices]
                continue
            offset = int(rng.integers(1, len(indices)))
            shifted_u[indices] = np.roll(u[indices], offset)
        _, _, shifted_score = closure(v, -shifted_u, w)
        null_auc[repetition] = weighted_auc(y, shifted_score, weight)
    table = pd.DataFrame({"repetition": np.arange(SHIFT_REPS), "shifted_child_auc": null_auc})
    summary = {
        "observed_auc": float(observed),
        "null_mean_auc": float(np.mean(null_auc)),
        "null_median_auc": float(np.median(null_auc)),
        "null_95_low": float(np.quantile(null_auc, 0.025)),
        "null_95_high": float(np.quantile(null_auc, 0.975)),
        "null_max_auc": float(np.max(null_auc)),
        "p_null_ge_observed": float((1 + np.sum(null_auc >= observed)) / (SHIFT_REPS + 1)),
    }
    return table, summary


def shifted_grandchild_audit(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    """Post-hoc timing audit for the best fixed control, grandchild flip."""
    rng = np.random.default_rng(SEED + 1)
    frame = frame.sort_values(["Name", "time_s"]).reset_index(drop=True)
    v = frame["v"].to_numpy(float)
    u = frame["u"].to_numpy(float)
    w = frame["w"].to_numpy(float)
    y = frame["y"].to_numpy(float)
    weight = frame["event_weight"].to_numpy(float)
    groups = [indices.to_numpy(int) for _, indices in frame.groupby("Name", sort=True).groups.items()]
    observed = weighted_auc(y, frame["handover_grandchild_flip"].to_numpy(float), weight)
    null_auc = np.empty(SHIFT_REPS, float)
    shifted_w = np.empty_like(w)
    for repetition in range(SHIFT_REPS):
        for indices in groups:
            if len(indices) <= 1:
                shifted_w[indices] = w[indices]
                continue
            offset = int(rng.integers(1, len(indices)))
            shifted_w[indices] = np.roll(w[indices], offset)
        _, _, shifted_score = closure(v, u, -shifted_w)
        null_auc[repetition] = weighted_auc(y, shifted_score, weight)
    table = pd.DataFrame({"repetition": np.arange(SHIFT_REPS), "shifted_grandchild_auc": null_auc})
    summary = {
        "status": "posthoc_best_control_timing_audit",
        "observed_auc": float(observed),
        "null_mean_auc": float(np.mean(null_auc)),
        "null_median_auc": float(np.median(null_auc)),
        "null_95_low": float(np.quantile(null_auc, 0.025)),
        "null_95_high": float(np.quantile(null_auc, 0.975)),
        "null_max_auc": float(np.max(null_auc)),
        "p_null_ge_observed": float((1 + np.sum(null_auc >= observed)) / (SHIFT_REPS + 1)),
    }
    return table, summary


def parity_difference_bootstrap(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    """Event-cluster bootstrap of grandchild-flip minus child-flip AUC."""
    rng = np.random.default_rng(SEED + 2)
    frame = frame.sort_values(["Name", "time_s"]).reset_index(drop=True)
    names = frame["Name"].drop_duplicates().to_numpy(str)
    groups = {name: group.index.to_numpy(int) for name, group in frame.groupby("Name", sort=False)}
    y = frame["y"].to_numpy(float)
    weight = frame["event_weight"].to_numpy(float)
    child = frame["handover_child_flip"].to_numpy(float)
    grandchild = frame["handover_grandchild_flip"].to_numpy(float)
    observed = weighted_auc(y, grandchild, weight) - weighted_auc(y, child, weight)
    differences = np.empty(BOOTSTRAP_REPS, float)
    for repetition in range(BOOTSTRAP_REPS):
        sampled_names = rng.choice(names, len(names), replace=True)
        indices = np.concatenate([groups[name] for name in sampled_names])
        differences[repetition] = (
            weighted_auc(y[indices], grandchild[indices], weight[indices])
            - weighted_auc(y[indices], child[indices], weight[indices])
        )
    table = pd.DataFrame({
        "repetition": np.arange(BOOTSTRAP_REPS),
        "auc_grandchild_flip_minus_child_flip": differences,
    })
    summary = {
        "status": "posthoc_event_cluster_bootstrap",
        "observed_auc_difference": float(observed),
        "bootstrap_mean": float(np.mean(differences)),
        "bootstrap_95_low": float(np.quantile(differences, 0.025)),
        "bootstrap_95_high": float(np.quantile(differences, 0.975)),
        "fraction_difference_le_zero": float(np.mean(differences <= 0)),
    }
    return table, summary


def channel_switch_audit(
    frame: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, float]]:
    """Post-hoc audit of the child-lock to grandchild-lock crossing suggested by the lead profile."""
    overall = pd.DataFrame([{"scope": "overall", **score_metrics(frame, "posthoc_channel_switch")}])
    fluid_rows = []
    for fluid, group in frame.groupby("fluid", sort=True):
        fluid_rows.append({"fluid": fluid, **score_metrics(group, "posthoc_channel_switch")})
    by_fluid = pd.DataFrame(fluid_rows)

    profile = frame.copy()
    bins = [0.0, 1.0, 2.0, 4.0, 8.0, np.inf]
    labels = ["(0,1]", "(1,2]", "(2,4]", "(4,8]", ">8"]
    profile["lead_bin"] = pd.cut(
        profile["lead_child_horizons"], bins=bins, labels=labels,
        include_lowest=False, right=True,
    )
    profile_rows = []
    for lead_bin, group in profile.groupby("lead_bin", observed=True, sort=False):
        profile_rows.append({
            "lead_bin": str(lead_bin),
            "weighted_mean_switch": weighted_mean(
                group["posthoc_channel_switch"].to_numpy(float),
                group["event_weight"].to_numpy(float),
            ),
            "events": int(group["Name"].nunique()),
            "snapshots": int(len(group)),
        })
    profile_table = pd.DataFrame(profile_rows)

    rng = np.random.default_rng(SEED + 3)
    ordered = frame.sort_values(["Name", "time_s"]).reset_index(drop=True)
    v = ordered["v"].to_numpy(float)
    u = ordered["u"].to_numpy(float)
    w = ordered["w"].to_numpy(float)
    y = ordered["y"].to_numpy(float)
    weight = ordered["event_weight"].to_numpy(float)
    groups = [indices.to_numpy(int) for _, indices in ordered.groupby("Name", sort=True).groups.items()]
    observed = weighted_auc(y, ordered["posthoc_channel_switch"].to_numpy(float), weight)
    shifted_u = np.empty_like(u)
    shifted_w = np.empty_like(w)
    null_auc = np.empty(SHIFT_REPS, float)
    for repetition in range(SHIFT_REPS):
        for indices in groups:
            if len(indices) <= 1:
                shifted_u[indices] = u[indices]
                shifted_w[indices] = w[indices]
                continue
            offset = int(rng.integers(1, len(indices)))
            shifted_u[indices] = np.roll(u[indices], offset)
            shifted_w[indices] = np.roll(w[indices], offset)
        _, _, child_score = closure(v, -shifted_u, shifted_w)
        _, _, grandchild_score = closure(v, shifted_u, -shifted_w)
        null_auc[repetition] = weighted_auc(y, grandchild_score - child_score, weight)
    null_table = pd.DataFrame({"repetition": np.arange(SHIFT_REPS), "shifted_bundle_auc": null_auc})
    summary = {
        "status": "posthoc_channel_crossing_audit",
        "definition": "handover_grandchild_flip - handover_child_flip",
        "observed_auc": float(observed),
        "null_mean_auc": float(np.mean(null_auc)),
        "null_median_auc": float(np.median(null_auc)),
        "null_95_low": float(np.quantile(null_auc, 0.025)),
        "null_95_high": float(np.quantile(null_auc, 0.975)),
        "null_max_auc": float(np.max(null_auc)),
        "p_null_ge_observed": float((1 + np.sum(null_auc >= observed)) / (SHIFT_REPS + 1)),
    }
    return overall, by_fluid, profile_table, null_table, summary


def validate_source(frame: pd.DataFrame) -> dict[str, bool | int]:
    per_event_weight = frame.groupby("Name")["event_weight"].sum()
    return {
        "rows": int(len(frame)),
        "events": int(frame["Name"].nunique()),
        "fluids": int(frame["fluid"].nunique()),
        "unique_name_time": bool(not frame.duplicated(["Name", "time_s"]).any()),
        "all_predictors_precede_target": bool((frame["time_s"] < frame["target_t_s"]).all()),
        "event_weights_sum_to_one": bool(np.allclose(per_event_weight.to_numpy(float), 1.0)),
        "coordinates_inside_0_2": bool(
            frame[["x_parent", "x_child", "x_grandchild"]].ge(0).all().all()
            and frame[["x_parent", "x_child", "x_grandchild"]].le(2).all().all()
        ),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    frame = build_scores(pd.read_csv(INPUT))
    checks = validate_source(frame)
    if not all(value for key, value in checks.items() if isinstance(value, bool)):
        raise RuntimeError(f"Source validation failed: {checks}")

    overall, by_fluid = performance_tables(frame)
    profile = lead_profile(frame)
    null_table, null_summary = shifted_child_null(frame)
    grandchild_null_table, grandchild_null_summary = shifted_grandchild_audit(frame)
    parity_bootstrap_table, parity_bootstrap_summary = parity_difference_bootstrap(frame)
    switch_overall, switch_fluid, switch_profile, switch_null, switch_summary = channel_switch_audit(frame)

    primary = overall.loc[overall.component == "handover"].set_index("parity")
    fluid_primary = by_fluid.loc[
        (by_fluid.component == "handover") & (by_fluid.parity == "child_flip")
    ]
    gates = {
        "child_flip_auc_above_chance": bool(primary.loc["child_flip", "auc"] > 0.5),
        "child_flip_auc_best_of_four": bool(
            primary.loc["child_flip", "auc"] == primary["auc"].max()
            and (primary["auc"] == primary["auc"].max()).sum() == 1
        ),
        "child_flip_auc_above_chance_in_at_least_three_fluids": bool(
            (fluid_primary["auc"] > 0.5).sum() >= 3
        ),
        "aligned_child_beats_shift_control_p_le_005": bool(
            null_summary["p_null_ge_observed"] <= 0.05
        ),
    }
    results = {
        "status": "frozen_coefficient_free_parity_closure",
        "formula": {
            "oriented_triplet": "(v,-u,w)",
            "agreement": "1-(abs(z1-z2)+abs(z2-z3)+abs(z3-z1))/4",
            "ridge_gate": "1-abs((z1+z2+z3)/3)",
            "handover_score": "agreement*ridge_gate",
        },
        "checks": checks,
        "gates": gates,
        "gates_passed": int(sum(gates.values())),
        "gates_total": int(len(gates)),
        "shift_null": null_summary,
        "posthoc_grandchild_shift_audit": grandchild_null_summary,
        "posthoc_grandchild_minus_child_auc_bootstrap": parity_bootstrap_summary,
        "posthoc_channel_switch": switch_summary,
    }

    frame.to_csv(OUT / "T411J_SCORED_SNAPSHOTS.csv", index=False)
    overall.to_csv(OUT / "T411J_OVERALL_PERFORMANCE.csv", index=False)
    by_fluid.to_csv(OUT / "T411J_FLUID_PERFORMANCE.csv", index=False)
    profile.to_csv(OUT / "T411J_LEAD_PROFILE.csv", index=False)
    null_table.to_csv(OUT / "T411J_CHILD_SHIFT_NULL.csv", index=False)
    grandchild_null_table.to_csv(OUT / "T411J_GRANDCHILD_SHIFT_AUDIT.csv", index=False)
    parity_bootstrap_table.to_csv(OUT / "T411J_PARITY_DIFFERENCE_BOOTSTRAP.csv", index=False)
    switch_overall.to_csv(OUT / "T411J_POSTHOC_SWITCH_OVERALL.csv", index=False)
    switch_fluid.to_csv(OUT / "T411J_POSTHOC_SWITCH_FLUID.csv", index=False)
    switch_profile.to_csv(OUT / "T411J_POSTHOC_SWITCH_PROFILE.csv", index=False)
    switch_null.to_csv(OUT / "T411J_POSTHOC_SWITCH_NULL.csv", index=False)
    (OUT / "T411J_RESULTS.json").write_text(json.dumps(results, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
