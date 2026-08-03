#!/usr/bin/env python3
"""T325: ARA Phi circle-train test in ordered Arabidopsis phyllotaxis.

Frozen protocol:
  T325_PHI_CIRCLE_TRAIN_PHYLLOTAXIS_PROTOCOL_v2_FROZEN.md

This is a calibration/re-analysis of the checksum-locked public source used in
T302. It does not download data and it does not import T302 calculations.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import OrderedDict
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
WORKBOOK_PATH = DATA_DIR / "Source Data 21.xlsx"
PROTOCOL_PATH = HERE / "T325_PHI_CIRCLE_TRAIN_PHYLLOTAXIS_PROTOCOL_v2_FROZEN.md"

EVENT_CSV = HERE / "T325_PHI_CIRCLE_TRAIN_PHYLLOTAXIS_EVENTS.csv"
PLANT_CSV = HERE / "T325_PHI_CIRCLE_TRAIN_PHYLLOTAXIS_PLANT_SCORES.csv"
CANDIDATE_CSV = HERE / "T325_PHI_CIRCLE_TRAIN_PHYLLOTAXIS_CANDIDATES.csv"
HORIZON_CSV = HERE / "T325_PHI_CIRCLE_TRAIN_PHYLLOTAXIS_HORIZONS.csv"
FIBONACCI_CSV = HERE / "T325_PHI_CIRCLE_TRAIN_PHYLLOTAXIS_FIBONACCI.csv"
NULL_CSV = HERE / "T325_PHI_CIRCLE_TRAIN_PHYLLOTAXIS_NULLS.csv"
RESULT_JSON = HERE / "T325_PHI_CIRCLE_TRAIN_PHYLLOTAXIS_RESULTS.json"
VALIDATION_JSON = HERE / "T325_PHI_CIRCLE_TRAIN_PHYLLOTAXIS_VALIDATION.json"
REPORT_MD = HERE / "T325_PHI_CIRCLE_TRAIN_PHYLLOTAXIS_REPORT_2026-08-02.md"

WORKBOOK_SHA256 = "E78372214B1386A486B25C8340C19F22BC74D3382F80A9B36A2972CC3D35ADFB"
PROTOCOL_SHA256 = "3CFD1A0BE552DF7BECBF69087462BF8C2C3A974EBD7ED15340A4696306536593"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_MINOR = 2.0 / (PHI * PHI)
RNG_SEED = 325
SHUFFLES = 10_000
BOOTSTRAPS = 10_000
FIT_BOOTSTRAPS = 5_000
GRID = np.arange(0.60, 0.9000001, 0.00001, dtype=float)

FIXED_CANDIDATES = OrderedDict(
    [
        ("persistence", 0.0),
        ("one_third_phase", 2.0 / 3.0),
        ("one_over_e", 2.0 / math.e),
        ("nearest_eighth_3_8", 3.0 / 4.0),
        ("fibonacci_8_21", 16.0 / 21.0),
        ("phi", PHI_MINOR),
        ("two_fifths_phase", 4.0 / 5.0),
        ("silver_conjugate", 2.0 * (math.sqrt(2.0) - 1.0)),
        ("half_turn_ridge", 1.0),
    ]
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def d2(a: np.ndarray | float, b: np.ndarray | float) -> np.ndarray:
    delta = np.abs(np.asarray(a, dtype=float) - np.asarray(b, dtype=float))
    return np.minimum(delta, 2.0 - delta)


def add_plant_ids(raw: pd.DataFrame) -> pd.DataFrame:
    output = raw.copy()
    counts: dict[str, int] = {}
    plant_ids: list[int] = []
    for row in output.itertuples(index=False):
        genotype = str(row.genotype)
        meristem = int(row.meristem)
        if genotype not in counts or meristem == 1:
            counts[genotype] = counts.get(genotype, 0) + 1
        plant_ids.append(counts[genotype])
    output["plant"] = plant_ids
    output["split"] = np.where(output["plant"] % 2 == 1, "development", "confirmation")

    for (genotype, plant), group in output.groupby(["genotype", "plant"], sort=False):
        observed = group["meristem"].astype(int).tolist()
        expected = list(range(1, len(observed) + 1))
        if observed != expected:
            raise RuntimeError(
                f"Ineligible lineage {genotype} plant {plant}: {observed} != {expected}"
            )
    return output


def positions_from_steps(steps: np.ndarray) -> np.ndarray:
    return np.mod(np.cumsum(np.asarray(steps, dtype=float)), 2.0)


def plant_candidate_losses(group: pd.DataFrame, delta: float) -> dict[str, float | int]:
    group = group.sort_values("meristem")
    steps = group["u_ara"].to_numpy(dtype=float)
    positions = group["position_ara"].to_numpy(dtype=float)
    held_indices = np.flatnonzero(group["heldout"].to_numpy(dtype=bool))
    if len(held_indices) == 0:
        raise RuntimeError("Every retained plant must have at least one held-out event")
    one_step = d2(steps[held_indices], delta)
    anchor = positions[1]
    horizons = held_indices - 1
    predicted = np.mod(anchor + horizons * delta, 2.0)
    carrier = d2(positions[held_indices], predicted)
    return {
        "heldout_n": int(len(held_indices)),
        "one_step_median_ara": float(np.median(one_step)),
        "one_step_mean_ara": float(np.mean(one_step)),
        "carrier_median_ara": float(np.median(carrier)),
        "carrier_mean_ara": float(np.mean(carrier)),
    }


def grid_loss_for_plant(group: pd.DataFrame, grid: np.ndarray) -> np.ndarray:
    group = group.sort_values("meristem")
    positions = group["position_ara"].to_numpy(dtype=float)
    held_indices = np.flatnonzero(group["heldout"].to_numpy(dtype=bool))
    anchor = positions[1]
    horizons = (held_indices - 1).astype(float)
    predicted = np.mod(anchor + grid[:, None] * horizons[None, :], 2.0)
    errors = d2(predicted, positions[held_indices][None, :])
    return np.median(errors, axis=1)


def fit_carrier(
    groups: list[pd.DataFrame], rng: np.random.Generator
) -> tuple[float, np.ndarray, np.ndarray]:
    loss_matrix = np.vstack([grid_loss_for_plant(group, GRID) for group in groups])
    objective = np.median(loss_matrix, axis=0)
    fitted = float(GRID[int(np.argmin(objective))])

    n_plants = len(groups)
    fitted_bootstrap = np.empty(FIT_BOOTSTRAPS, dtype=float)
    batch = 25
    for start in range(0, FIT_BOOTSTRAPS, batch):
        stop = min(start + batch, FIT_BOOTSTRAPS)
        indices = rng.integers(0, n_plants, size=(stop - start, n_plants))
        objectives = np.median(loss_matrix[indices], axis=1)
        fitted_bootstrap[start:stop] = GRID[np.argmin(objectives, axis=1)]
    return fitted, fitted_bootstrap, loss_matrix


def aggregate_candidate_table(plant_scores: pd.DataFrame) -> pd.DataFrame:
    selected = plant_scores[
        (plant_scores["genotype"] == "Col")
        & (plant_scores["split"] == "confirmation")
    ]
    summary = (
        selected.groupby(["candidate", "candidate_type", "increment_ara"], as_index=False)
        .agg(
            n_plants=("plant", "nunique"),
            one_step_median_ara=("one_step_median_ara", "median"),
            one_step_mean_ara=("one_step_mean_ara", "mean"),
            carrier_median_ara=("carrier_median_ara", "median"),
            carrier_mean_ara=("carrier_mean_ara", "mean"),
        )
    )
    summary["one_step_median_deg"] = summary["one_step_median_ara"] * 180.0
    summary["carrier_median_deg"] = summary["carrier_median_ara"] * 180.0
    summary["one_step_rank"] = summary["one_step_median_ara"].rank(method="min")
    summary["carrier_rank"] = summary["carrier_median_ara"].rank(method="min")
    return summary.sort_values(["candidate_type", "increment_ara"]).reset_index(drop=True)


def horizon_table(
    groups: list[pd.DataFrame], candidates: OrderedDict[str, float]
) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    for name, delta in candidates.items():
        for horizon in range(1, 6):
            plant_losses: list[float] = []
            prediction_count = 0
            for group in groups:
                group = group.sort_values("meristem")
                positions = group["position_ara"].to_numpy(dtype=float)
                target_index = 1 + horizon
                if target_index >= len(positions):
                    continue
                predicted = (positions[1] + horizon * delta) % 2.0
                plant_losses.append(float(d2(positions[target_index], predicted)))
                prediction_count += 1
            if plant_losses:
                rows.append(
                    {
                        "candidate": name,
                        "increment_ara": float(delta),
                        "horizon": horizon,
                        "n_plants": len(plant_losses),
                        "n_predictions": prediction_count,
                        "median_error_ara": float(np.median(plant_losses)),
                        "mean_error_ara": float(np.mean(plant_losses)),
                        "median_error_deg": float(np.median(plant_losses) * 180.0),
                    }
                )
    return pd.DataFrame(rows)


def order_shuffle_test(
    groups: list[pd.DataFrame], delta: float, rng: np.random.Generator
) -> tuple[float, np.ndarray, float]:
    prepared: list[tuple[float, np.ndarray, np.ndarray]] = []
    true_losses: list[float] = []
    for group in groups:
        group = group.sort_values("meristem")
        steps = group["u_ara"].to_numpy(dtype=float)
        positions = group["position_ara"].to_numpy(dtype=float)
        anchor = float(positions[1])
        held_steps = steps[2:].copy()
        horizons = np.arange(1, len(held_steps) + 1, dtype=float)
        prediction = np.mod(anchor + horizons * delta, 2.0)
        true_losses.append(float(np.median(d2(positions[2:], prediction))))
        prepared.append((anchor, held_steps, prediction))

    observed = float(np.median(true_losses))
    null = np.empty(SHUFFLES, dtype=float)
    for draw in range(SHUFFLES):
        losses: list[float] = []
        for anchor, held_steps, prediction in prepared:
            permuted = rng.permutation(held_steps)
            synthetic = np.mod(anchor + np.cumsum(permuted), 2.0)
            losses.append(float(np.median(d2(synthetic, prediction))))
        null[draw] = float(np.median(losses))
    p_lower = float((1 + np.sum(null <= observed)) / (len(null) + 1))
    return observed, null, p_lower


def compensation_ratio(x: np.ndarray, y: np.ndarray) -> float:
    numerator = float(np.median(np.abs(0.5 * (x + y))))
    denominator = float(np.median(0.5 * (np.abs(x) + np.abs(y))))
    return numerator / denominator if denominator > 0.0 else float("nan")


def compensation_tests(
    groups: list[pd.DataFrame], delta: float, rng: np.random.Generator
) -> dict[str, object]:
    residuals: list[np.ndarray] = []
    labels: list[int] = []
    x_parts: list[np.ndarray] = []
    y_parts: list[np.ndarray] = []
    pair_labels: list[np.ndarray] = []
    for plant_index, group in enumerate(groups):
        group = group.sort_values("meristem")
        values = group.loc[group["heldout"], "u_ara"].to_numpy(dtype=float) - delta
        residuals.append(values)
        labels.extend([plant_index] * len(values))
        if len(values) >= 2:
            x_parts.append(values[:-1])
            y_parts.append(values[1:])
            pair_labels.append(np.full(len(values) - 1, plant_index, dtype=int))

    x = np.concatenate(x_parts)
    y = np.concatenate(y_parts)
    x_labels = np.concatenate(pair_labels)
    pool = np.concatenate(residuals)
    pool_labels = np.asarray(labels, dtype=int)
    observed = compensation_ratio(x, y)

    within_null = np.empty(SHUFFLES, dtype=float)
    for draw in range(SHUFFLES):
        nx: list[float] = []
        ny: list[float] = []
        for values in residuals:
            permuted = rng.permutation(values)
            if len(permuted) >= 2:
                nx.extend(permuted[:-1].tolist())
                ny.extend(permuted[1:].tolist())
        within_null[draw] = compensation_ratio(np.asarray(nx), np.asarray(ny))

    allowed = [np.flatnonzero(pool_labels != plant) for plant in x_labels]
    broken_null = np.empty(SHUFFLES, dtype=float)
    for draw in range(SHUFFLES):
        broken_y = np.asarray(
            [pool[index_set[rng.integers(0, len(index_set))]] for index_set in allowed]
        )
        broken_null[draw] = compensation_ratio(x, broken_y)

    return {
        "pairs": int(len(x)),
        "observed_ratio": float(observed),
        "within_order": {
            "p_lower": float((1 + np.sum(within_null <= observed)) / (SHUFFLES + 1)),
            "null_median": float(np.median(within_null)),
            "null_95": [
                float(np.quantile(within_null, 0.025)),
                float(np.quantile(within_null, 0.975)),
            ],
        },
        "broken_lineage": {
            "p_lower": float((1 + np.sum(broken_null <= observed)) / (SHUFFLES + 1)),
            "null_median": float(np.median(broken_null)),
            "null_95": [
                float(np.quantile(broken_null, 0.025)),
                float(np.quantile(broken_null, 0.975)),
            ],
        },
    }


def fibonacci_table(
    groups: list[pd.DataFrame], candidates: OrderedDict[str, float]
) -> tuple[pd.DataFrame, dict[str, float]]:
    observed_by_lag: dict[int, dict[str, float | int]] = {}
    for lag in (2, 3, 5):
        plant_returns: list[float] = []
        pair_count = 0
        for group in groups:
            positions = np.r_[0.0, group.sort_values("meristem")["position_ara"].to_numpy(dtype=float)]
            if len(positions) <= lag:
                continue
            returns = d2(positions[lag:], positions[:-lag])
            plant_returns.append(float(np.median(returns)))
            pair_count += len(returns)
        observed_by_lag[lag] = {
            "observed_median_ara": float(np.median(plant_returns)),
            "observed_mean_ara": float(np.mean(plant_returns)),
            "n_plants": int(len(plant_returns)),
            "n_pairs": int(pair_count),
        }

    rows: list[dict[str, float | int | str]] = []
    profile_mae: dict[str, float] = {}
    for name, delta in candidates.items():
        errors: list[float] = []
        for lag, observed in observed_by_lag.items():
            predicted = float(d2((lag * delta) % 2.0, 0.0))
            absolute_error = abs(float(observed["observed_median_ara"]) - predicted)
            errors.append(absolute_error)
            rows.append(
                {
                    "candidate": name,
                    "increment_ara": float(delta),
                    "lag": lag,
                    **observed,
                    "predicted_return_ara": predicted,
                    "absolute_error_ara": absolute_error,
                }
            )
        profile_mae[name] = float(np.mean(errors))
    frame = pd.DataFrame(rows)
    frame["profile_mae_ara"] = frame["candidate"].map(profile_mae)
    return frame, profile_mae


def bootstrap_paired_difference(
    differences: np.ndarray, rng: np.random.Generator
) -> tuple[list[float], float]:
    differences = np.asarray(differences, dtype=float)
    indices = rng.integers(0, len(differences), size=(BOOTSTRAPS, len(differences)))
    estimates = np.median(differences[indices], axis=1)
    interval = [float(np.quantile(estimates, 0.025)), float(np.quantile(estimates, 0.975))]
    p_positive = float((1 + np.sum(estimates <= 0.0)) / (len(estimates) + 1))
    return interval, p_positive


def robust_exclusion_winner(
    groups: list[pd.DataFrame], candidates: OrderedDict[str, float], remove: str
) -> dict[str, object]:
    sizes = np.asarray([len(group) for group in groups])
    target = int(sizes.max() if remove == "longest" else sizes.min())
    retained = [group for group in groups if len(group) != target]
    losses: dict[str, float] = {}
    for name, delta in candidates.items():
        losses[name] = float(
            np.median([plant_candidate_losses(group, delta)["carrier_median_ara"] for group in retained])
        )
    winner = min(losses, key=losses.get)
    return {"removed_length": target, "retained_plants": len(retained), "winner": winner, "losses": losses}


def json_ready(value):
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    return value


def main() -> None:
    if sha256(WORKBOOK_PATH) != WORKBOOK_SHA256:
        raise RuntimeError("Workbook SHA-256 mismatch")
    if sha256(PROTOCOL_PATH) != PROTOCOL_SHA256:
        raise RuntimeError("Frozen protocol SHA-256 mismatch")

    raw = pd.read_excel(WORKBOOK_PATH, sheet_name="EPFL_phyllo-angle")
    if raw.columns.tolist() != ["genotype", "meristem", "angle"]:
        raise RuntimeError(f"Unexpected columns: {raw.columns.tolist()}")
    if len(raw) != 359:
        raise RuntimeError(f"Unexpected row count: {len(raw)}")
    if not np.isfinite(raw["angle"].astype(float)).all():
        raise RuntimeError("Non-finite angle")
    if not raw["angle"].astype(float).between(0.0, 360.0, inclusive="both").all():
        raise RuntimeError("Angle outside recorded directed cycle")

    events = add_plant_ids(raw)
    events["angle_deg"] = events["angle"].astype(float)
    events["u_ara"] = events["angle_deg"] / 180.0
    events["heldout"] = events["meristem"].astype(int) >= 3
    events["position_ara"] = np.nan
    for _, group in events.groupby(["genotype", "plant"], sort=False):
        events.loc[group.index, "position_ara"] = positions_from_steps(group["u_ara"].to_numpy(dtype=float))

    dev_col_groups = [
        group.sort_values("meristem").copy()
        for _, group in events[
            (events["genotype"] == "Col") & (events["split"] == "development")
        ].groupby("plant", sort=True)
    ]
    confirm_col_groups = [
        group.sort_values("meristem").copy()
        for _, group in events[
            (events["genotype"] == "Col") & (events["split"] == "confirmation")
        ].groupby("plant", sort=True)
    ]

    step_fit = float(
        np.median(
            [
                np.median(group.loc[group["heldout"], "u_ara"].to_numpy(dtype=float))
                for group in dev_col_groups
            ]
        )
    )
    fit_rng = np.random.default_rng(RNG_SEED + 1)
    carrier_fit, carrier_fit_bootstrap, _ = fit_carrier(dev_col_groups, fit_rng)

    all_candidates = OrderedDict(FIXED_CANDIDATES)
    all_candidates["development_step_fit"] = step_fit
    all_candidates["development_carrier_fit"] = carrier_fit
    candidate_types = {
        name: ("fixed" if name in FIXED_CANDIDATES else "development_fit")
        for name in all_candidates
    }

    plant_rows: list[dict[str, object]] = []
    for (genotype, plant), group in events.groupby(["genotype", "plant"], sort=False):
        for name, delta in all_candidates.items():
            plant_rows.append(
                {
                    "genotype": str(genotype),
                    "plant": int(plant),
                    "split": str(group["split"].iloc[0]),
                    "n_events": int(len(group)),
                    "candidate": name,
                    "candidate_type": candidate_types[name],
                    "increment_ara": float(delta),
                    **plant_candidate_losses(group, delta),
                }
            )
    plant_scores = pd.DataFrame(plant_rows)
    candidate_summary = aggregate_candidate_table(plant_scores)

    fixed_summary = candidate_summary[candidate_summary["candidate_type"] == "fixed"]
    step_winner = str(fixed_summary.loc[fixed_summary["one_step_median_ara"].idxmin(), "candidate"])
    carrier_winner = str(fixed_summary.loc[fixed_summary["carrier_median_ara"].idxmin(), "candidate"])

    horizons = horizon_table(confirm_col_groups, all_candidates)
    fibonacci, fibonacci_mae = fibonacci_table(confirm_col_groups, FIXED_CANDIDATES)
    fibonacci_winner = min(fibonacci_mae, key=fibonacci_mae.get)

    order_rng = np.random.default_rng(RNG_SEED + 2)
    order_observed, order_null, order_p = order_shuffle_test(confirm_col_groups, PHI_MINOR, order_rng)

    compensation_rng = np.random.default_rng(RNG_SEED + 3)
    compensation = compensation_tests(confirm_col_groups, PHI_MINOR, compensation_rng)

    confirm_phi = plant_scores[
        (plant_scores["genotype"] == "Col")
        & (plant_scores["split"] == "confirmation")
        & (plant_scores["candidate"] == "phi")
    ].sort_values("plant")
    confirm_fit = plant_scores[
        (plant_scores["genotype"] == "Col")
        & (plant_scores["split"] == "confirmation")
        & (plant_scores["candidate"] == "development_carrier_fit")
    ].sort_values("plant")
    if confirm_phi["plant"].tolist() != confirm_fit["plant"].tolist():
        raise RuntimeError("Paired confirmation plants do not align")
    differences = (
        confirm_phi["carrier_median_ara"].to_numpy(dtype=float)
        - confirm_fit["carrier_median_ara"].to_numpy(dtype=float)
    )
    diff_rng = np.random.default_rng(RNG_SEED + 4)
    fit_difference_ci, fit_advantage_p = bootstrap_paired_difference(differences, diff_rng)
    fit_ci = [
        float(np.quantile(carrier_fit_bootstrap, 0.025)),
        float(np.quantile(carrier_fit_bootstrap, 0.975)),
    ]
    fit_compatible = bool(fit_ci[0] <= PHI_MINOR <= fit_ci[1])
    fit_advantage_significant = bool(fit_difference_ci[0] > 0.0)

    null_rows = [
        {
            "control": "within_plant_order_carrier",
            "observed": order_observed,
            "null_median": float(np.median(order_null)),
            "null_lo": float(np.quantile(order_null, 0.025)),
            "null_hi": float(np.quantile(order_null, 0.975)),
            "p_lower": order_p,
        },
        {
            "control": "within_plant_order_compensation",
            "observed": compensation["observed_ratio"],
            "null_median": compensation["within_order"]["null_median"],
            "null_lo": compensation["within_order"]["null_95"][0],
            "null_hi": compensation["within_order"]["null_95"][1],
            "p_lower": compensation["within_order"]["p_lower"],
        },
        {
            "control": "broken_lineage_compensation",
            "observed": compensation["observed_ratio"],
            "null_median": compensation["broken_lineage"]["null_median"],
            "null_lo": compensation["broken_lineage"]["null_95"][0],
            "null_hi": compensation["broken_lineage"]["null_95"][1],
            "p_lower": compensation["broken_lineage"]["p_lower"],
        },
    ]
    null_summary = pd.DataFrame(null_rows)

    genotype_phi = (
        plant_scores[
            (plant_scores["split"] == "confirmation")
            & (plant_scores["candidate"] == "phi")
        ]
        .groupby("genotype", as_index=False)
        .agg(
            n_plants=("plant", "nunique"),
            one_step_median_ara=("one_step_median_ara", "median"),
            carrier_median_ara=("carrier_median_ara", "median"),
        )
    )

    result = {
        "test_id": "T325-PHI-CIRCLE-TRAIN-PHYLLOTAXIS-v2",
        "status": "calibration/re-analysis; not independent replication",
        "source": {
            "doi": "10.1038/s41467-025-65792-y",
            "workbook": str(WORKBOOK_PATH.relative_to(HERE)),
            "workbook_sha256": sha256(WORKBOOK_PATH),
            "protocol_sha256": sha256(PROTOCOL_PATH),
            "rows": int(len(events)),
            "plants": int(events[["genotype", "plant"]].drop_duplicates().shape[0]),
            "genotype_counts": events.groupby("genotype").size().astype(int).to_dict(),
            "recorded_angle_precision_deg": 0.001,
            "measurement_uncertainty_reported_in_workbook": False,
        },
        "ara_mapping": {
            "parent_cycle_deg": 360.0,
            "parent_cycle_ara": 2.0,
            "living_directed_increment": 2.0 / PHI,
            "source_compatible_minor_increment": PHI_MINOR,
            "source_compatible_angle_deg": PHI_MINOR * 180.0,
            "handedness_tested": False,
            "phi_vs_three_eighths_separation_ara": abs(PHI_MINOR - 0.75),
            "phi_vs_three_eighths_separation_deg": abs(PHI_MINOR - 0.75) * 180.0,
        },
        "development_fits": {
            "step_fit_ara": step_fit,
            "carrier_fit_ara": carrier_fit,
            "carrier_fit_bootstrap_95": fit_ci,
            "phi_inside_carrier_fit_95": fit_compatible,
            "confirmation_phi_minus_fit_median_plant_difference_ara": float(np.median(differences)),
            "confirmation_phi_minus_fit_bootstrap_95": fit_difference_ci,
            "fit_advantage_p_positive": fit_advantage_p,
            "fit_advantage_significant": fit_advantage_significant,
        },
        "headline": {
            "fixed_one_step_winner": step_winner,
            "fixed_carrier_winner": carrier_winner,
            "fibonacci_profile_winner": fibonacci_winner,
            "order_carrier_p_lower": order_p,
            "compensation_ratio": compensation["observed_ratio"],
            "compensation_order_p_lower": compensation["within_order"]["p_lower"],
            "compensation_broken_lineage_p_lower": compensation["broken_lineage"]["p_lower"],
        },
        "gates": {
            "eligibility": True,
            "recorded_resolution": True,
            "physical_measurement_uncertainty": "not reported",
            "one_step_phi_wins_fixed": step_winner == "phi",
            "carrier_phi_wins_fixed": carrier_winner == "phi",
            "fit_compatible_and_not_significantly_better": bool(
                fit_compatible and not fit_advantage_significant
            ),
            "real_order_beats_shuffle": order_p < 0.05,
            "ordered_compensation_beats_shuffle": compensation["within_order"]["p_lower"] < 0.05,
            "ordered_compensation_beats_broken_lineage": compensation["broken_lineage"]["p_lower"] < 0.05,
            "fibonacci_profile_phi_wins_fixed": fibonacci_winner == "phi",
            "independent_replication": False,
        },
        "order_control": {
            "observed_carrier_loss_ara": order_observed,
            "shuffle_median_ara": float(np.median(order_null)),
            "shuffle_95": [
                float(np.quantile(order_null, 0.025)),
                float(np.quantile(order_null, 0.975)),
            ],
            "p_lower": order_p,
        },
        "compensation": compensation,
        "fibonacci_profile_mae": fibonacci_mae,
        "genotype_phi_summary": genotype_phi.to_dict(orient="records"),
        "robustness": {
            "remove_longest_sequence": robust_exclusion_winner(confirm_col_groups, FIXED_CANDIDATES, "longest"),
            "remove_shortest_sequence": robust_exclusion_winner(confirm_col_groups, FIXED_CANDIDATES, "shortest"),
        },
        "artifacts": {
            "event_csv": EVENT_CSV.name,
            "plant_scores_csv": PLANT_CSV.name,
            "candidate_csv": CANDIDATE_CSV.name,
            "horizon_csv": HORIZON_CSV.name,
            "fibonacci_csv": FIBONACCI_CSV.name,
            "null_csv": NULL_CSV.name,
            "validation_json": VALIDATION_JSON.name,
            "technical_report": REPORT_MD.name,
        },
    }

    event_columns = [
        "genotype",
        "meristem",
        "plant",
        "split",
        "angle_deg",
        "u_ara",
        "position_ara",
        "heldout",
    ]
    events[event_columns].to_csv(EVENT_CSV, index=False, float_format="%.12g")
    plant_scores.to_csv(PLANT_CSV, index=False, float_format="%.12g")
    candidate_summary.to_csv(CANDIDATE_CSV, index=False, float_format="%.12g")
    horizons.to_csv(HORIZON_CSV, index=False, float_format="%.12g")
    fibonacci.to_csv(FIBONACCI_CSV, index=False, float_format="%.12g")
    null_summary.to_csv(NULL_CSV, index=False, float_format="%.12g")
    RESULT_JSON.write_text(json.dumps(json_ready(result), indent=2), encoding="utf-8")

    print(json.dumps(json_ready(result["headline"]), indent=2))
    print(f"Wrote {RESULT_JSON.name}")


if __name__ == "__main__":
    main()
