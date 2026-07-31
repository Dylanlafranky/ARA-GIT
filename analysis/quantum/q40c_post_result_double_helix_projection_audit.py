"""Post-result audit of the two-strand structure visible in the Q40 ARA cut.

The upper-left Q40 diagnostic is a two-dimensional phase-plane projection:

    u = closure side
    v = closure flow

This script restores sample order as a third coordinate and asks a narrower
question: does the sampled orbit close after one apparent turn, or only after
two turns?  A two-turn closure would create two interleaved sampled phase
tracks in the flattened view.

This is descriptive post-result work.  It cannot alter Q40/T295 or establish
that the two tracks are two independent physical waves.
"""

from __future__ import annotations

import csv
import gzip
import json
import math
import os
import pathlib
import sys


HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / "public_data" / "_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(HERE / ".mplconfig"))

import matplotlib.pyplot as plt
import numpy as np

from q40_return_flow_relation_reversal_test import (
    DERIVED,
    EPS,
    EVENTS,
    PAIRS,
    PREDICTIONS,
    coordinates,
)


OUTPUT = HERE / "Q40C_POST_RESULT_DOUBLE_HELIX_RESULTS.json"
FIGURE_PNG = HERE / "Q40C_POST_RESULT_DOUBLE_HELIX_DIAGNOSTICS.png"
FIGURE_SVG = HERE / "Q40C_POST_RESULT_DOUBLE_HELIX_DIAGNOSTICS.svg"

SAMPLE_SEED = 0
SAMPLE_PAIR = (2, 5)
EVAL_FIRST = 250
EVAL_LAST_EXCLUSIVE = 499

BLUE = "#4F79B8"
GOLD = "#D89B2B"
INK = "#202936"
MID = "#687383"
GRID = "#D9DEE5"
LIGHT = "#F6F8FA"
RED = "#D85C4A"


def safe_correlation(a: np.ndarray, b: np.ndarray) -> float:
    left = np.asarray(a, dtype=np.float64).ravel()
    right = np.asarray(b, dtype=np.float64).ravel()
    if left.size < 3 or right.size != left.size:
        return float("nan")
    left = left - np.mean(left)
    right = right - np.mean(right)
    denom = np.linalg.norm(left) * np.linalg.norm(right)
    if denom <= EPS:
        return float("nan")
    return float(np.dot(left, right) / denom)


def lag_metrics(
    u: np.ndarray,
    v: np.ndarray,
    theta: np.ndarray,
    lag: int,
) -> dict[str, float | int]:
    if lag <= 0 or lag >= len(u) - 2:
        return {
            "lag": int(lag),
            "coordinate_correlation": float("nan"),
            "phase_return_mean_radians": float("nan"),
            "phase_return_locking": float("nan"),
            "coordinate_rmse": float("nan"),
        }
    first = np.column_stack((u[:-lag], v[:-lag]))
    second = np.column_stack((u[lag:], v[lag:]))
    phase_delta = theta[lag:] - theta[:-lag]
    phase_vector = np.mean(np.exp(1j * phase_delta))
    return {
        "lag": int(lag),
        "coordinate_correlation": safe_correlation(first, second),
        "phase_return_mean_radians": float(np.angle(phase_vector)),
        "phase_return_locking": float(abs(phase_vector)),
        "coordinate_rmse": float(np.sqrt(np.mean((second - first) ** 2))),
    }


def fit_orbit(u: np.ndarray, v: np.ndarray) -> dict:
    theta = np.unwrap(np.arctan2(v, u))
    sample = np.arange(len(theta), dtype=np.float64)
    slope, intercept = np.polyfit(sample, theta, 1)
    fitted = intercept + slope * sample
    residual = theta - fitted
    total = theta - np.mean(theta)
    r2 = 1.0 - float(np.dot(residual, residual)) / (
        float(np.dot(total, total)) + EPS
    )
    period = float(2 * np.pi / abs(slope))
    one_floor = max(1, int(math.floor(period)))
    one_ceil = max(1, int(math.ceil(period)))
    two_turn = max(1, int(round(2 * period)))
    lag_floor = lag_metrics(u, v, theta, one_floor)
    lag_ceil = lag_metrics(u, v, theta, one_ceil)
    lag_two = lag_metrics(u, v, theta, two_turn)
    fixed_lag_15 = lag_metrics(u, v, theta, 15)
    one_turn_candidates = np.asarray(
        [
            lag_floor["coordinate_correlation"],
            lag_ceil["coordinate_correlation"],
        ],
        dtype=np.float64,
    )
    one_turn_candidates = one_turn_candidates[np.isfinite(one_turn_candidates)]
    one_turn_best = (
        float(np.max(one_turn_candidates))
        if len(one_turn_candidates)
        else float("nan")
    )
    half_integer_distance = float(abs(period - (math.floor(period) + 0.5)))
    two_turn_7_5_family = bool(
        7.35 <= period <= 7.65
        and fixed_lag_15["coordinate_correlation"] >= 0.95
    )
    one_turn_15_family = bool(
        14.8 <= period <= 15.2
        and fixed_lag_15["coordinate_correlation"] >= 0.95
    )
    return {
        "theta": theta,
        "sample": sample,
        "fitted": fitted,
        "slope_radians_per_sample": float(slope),
        "intercept_radians": float(intercept),
        "rotation_direction": "counterclockwise" if slope > 0 else "clockwise",
        "angular_period_samples": period,
        "angle_time_r_squared": r2,
        "half_integer_period_distance": half_integer_distance,
        "lag_one_turn_floor": lag_floor,
        "lag_one_turn_ceil": lag_ceil,
        "lag_two_turn": lag_two,
        "fixed_lag_15": fixed_lag_15,
        "two_turn_correlation_advantage": float(
            lag_two["coordinate_correlation"] - one_turn_best
        ),
        "posthoc_two_turn_7_5_family": two_turn_7_5_family,
        "posthoc_one_turn_15_family": one_turn_15_family,
        "posthoc_two_turn_signature": bool(
            r2 >= 0.98
            and half_integer_distance <= 0.10
            and lag_two["coordinate_correlation"] >= 0.95
            and lag_two["coordinate_correlation"] - one_turn_best >= 0.20
        ),
    }


def clean_fit(fit: dict) -> dict:
    return {
        key: value
        for key, value in fit.items()
        if key not in {"theta", "sample", "fitted"}
    }


def finite_summary(values: list[float]) -> dict[str, float | int]:
    array = np.asarray(values, dtype=np.float64)
    array = array[np.isfinite(array)]
    if not len(array):
        return {"n": 0}
    quantiles = np.quantile(array, [0.05, 0.25, 0.5, 0.75, 0.95])
    return {
        "n": int(len(array)),
        "mean": float(np.mean(array)),
        "standard_deviation": float(np.std(array)),
        "minimum": float(np.min(array)),
        "q05": float(quantiles[0]),
        "q25": float(quantiles[1]),
        "median": float(quantiles[2]),
        "q75": float(quantiles[3]),
        "q95": float(quantiles[4]),
        "maximum": float(np.max(array)),
    }


def population_audit(closure: np.ndarray) -> tuple[list[dict], dict]:
    with np.load(PREDICTIONS, allow_pickle=False) as frozen:
        lineages = sorted(
            {
                (int(seed), int(pair))
                for seed, pair in zip(frozen["seed"], frozen["pair"])
            }
        )
    rows: list[dict] = []
    for seed, pair_index in lineages:
        coord = coordinates(closure[seed, :, pair_index])
        if coord is None:
            continue
        u, v = coord[0][EVAL_FIRST:EVAL_LAST_EXCLUSIVE], coord[1][
            EVAL_FIRST:EVAL_LAST_EXCLUSIVE
        ]
        fit = fit_orbit(u, v)
        rows.append(
            {
                "seed": seed,
                "pair_index": pair_index,
                "pair": list(PAIRS[pair_index]),
                **clean_fit(fit),
            }
        )

    two_turn_family_count = int(
        sum(row["posthoc_two_turn_7_5_family"] for row in rows)
    )
    one_turn_family_count = int(
        sum(row["posthoc_one_turn_15_family"] for row in rows)
    )
    common_lag_15_count = int(
        sum(
            row["fixed_lag_15"]["coordinate_correlation"] >= 0.95
            for row in rows
        )
    )
    summaries = {
        "eligible_unique_lineages": len(lineages),
        "audited_lineages": len(rows),
        "angular_period_samples": finite_summary(
            [row["angular_period_samples"] for row in rows]
        ),
        "angle_time_r_squared": finite_summary(
            [row["angle_time_r_squared"] for row in rows]
        ),
        "half_integer_period_distance": finite_summary(
            [row["half_integer_period_distance"] for row in rows]
        ),
        "one_turn_best_coordinate_correlation": finite_summary(
            [
                max(
                    row["lag_one_turn_floor"]["coordinate_correlation"],
                    row["lag_one_turn_ceil"]["coordinate_correlation"],
                )
                for row in rows
            ]
        ),
        "two_turn_coordinate_correlation": finite_summary(
            [
                row["lag_two_turn"]["coordinate_correlation"]
                for row in rows
            ]
        ),
        "two_turn_correlation_advantage": finite_summary(
            [row["two_turn_correlation_advantage"] for row in rows]
        ),
        "fixed_lag_15_coordinate_correlation": finite_summary(
            [
                row["fixed_lag_15"]["coordinate_correlation"]
                for row in rows
            ]
        ),
        "posthoc_period_families": {
            "two_turn_7_5_sample_family_count": two_turn_family_count,
            "two_turn_7_5_sample_family_fraction": float(
                two_turn_family_count / len(rows)
            )
            if rows
            else float("nan"),
            "one_turn_15_sample_family_count": one_turn_family_count,
            "one_turn_15_sample_family_fraction": float(
                one_turn_family_count / len(rows)
            )
            if rows
            else float("nan"),
            "other_count": int(
                len(rows) - two_turn_family_count - one_turn_family_count
            ),
            "fixed_lag_15_return_at_least_0_95_count": common_lag_15_count,
            "fixed_lag_15_return_at_least_0_95_fraction": float(
                common_lag_15_count / len(rows)
            )
            if rows
            else float("nan"),
        },
        "posthoc_two_turn_signature_count": int(
            sum(row["posthoc_two_turn_signature"] for row in rows)
        ),
        "posthoc_two_turn_signature_fraction": float(
            np.mean([row["posthoc_two_turn_signature"] for row in rows])
        )
        if rows
        else float("nan"),
    }
    return rows, summaries


def q40_outcomes_by_period_family(rows: list[dict]) -> dict:
    if not EVENTS.exists():
        return {"status": "Q40 cycle table unavailable"}
    family = {
        (int(row["seed"]), int(row["pair_index"])): (
            "two_turn_7_5"
            if row["posthoc_two_turn_7_5_family"]
            else "one_turn_15"
            if row["posthoc_one_turn_15_family"]
            else "other"
        )
        for row in rows
    }
    grouped: dict[str, list[dict[str, str]]] = {
        "two_turn_7_5": [],
        "one_turn_15": [],
        "other": [],
    }
    with gzip.open(EVENTS, "rt", newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            key = (int(row["seed"]), int(row["pair_index"]))
            grouped[family[key]].append(row)

    output = {}
    for name, values in grouped.items():
        flag = np.asarray([int(row["flag"]) for row in values], dtype=bool)
        target = np.asarray(
            [int(row["target_negative_orientation"]) for row in values],
            dtype=bool,
        )
        tp = int(np.sum(flag & target))
        fp = int(np.sum(flag & ~target))
        fn = int(np.sum(~flag & target))
        tn = int(np.sum(~flag & ~target))
        fn_by_q4 = {
            str(q4): int(
                sum(
                    not bool(int(row["flag"]))
                    and bool(int(row["target_negative_orientation"]))
                    and int(row["q4"]) == q4
                    for row in values
                )
            )
            for q4 in range(4)
        }
        output[name] = {
            "cycles": len(values),
            "lineages": len(
                {
                    (int(row["seed"]), int(row["pair_index"]))
                    for row in values
                }
            ),
            "true_positive": tp,
            "false_positive": fp,
            "false_negative": fn,
            "true_negative": tn,
            "precision": float(tp / max(tp + fp, 1)),
            "recall": float(tp / max(tp + fn, 1)),
            "specificity": float(tn / max(tn + fp, 1)),
            "target_negative_fraction": float((tp + fn) / max(len(values), 1)),
            "flag_fraction": float((tp + fp) / max(len(values), 1)),
            "mean_q40_scaled_error": float(
                np.mean([float(row["q40_scaled_error"]) for row in values])
            ),
            "mean_forward_scaled_error": float(
                np.mean([float(row["forward_scaled_error"]) for row in values])
            ),
            "false_negative_by_q4": fn_by_q4,
        }
    total_false_negatives = sum(
        value["false_negative"] for value in output.values()
    )
    output["failure_concentration"] = {
        "total_false_negatives": total_false_negatives,
        "two_turn_7_5_false_negative_share": float(
            output["two_turn_7_5"]["false_negative"]
            / max(total_false_negatives, 1)
        ),
        "two_turn_7_5_q4_1_false_negative_share_of_all": float(
            output["two_turn_7_5"]["false_negative_by_q4"]["1"]
            / max(total_false_negatives, 1)
        ),
    }
    return output


def rotation_parity(theta: np.ndarray, slope: float) -> np.ndarray:
    direction = 1.0 if slope >= 0 else -1.0
    progress = direction * (theta - theta[0]) / (2 * np.pi)
    rotation = np.floor(progress + 1e-9).astype(int)
    return np.mod(rotation, 2)


def style_axis(axis) -> None:
    axis.set_facecolor("white")
    axis.tick_params(colors=MID, labelsize=9)
    for spine in axis.spines.values():
        spine.set_color(MID)
        spine.set_linewidth(0.8)


def make_figure(
    u: np.ndarray,
    v: np.ndarray,
    fit: dict,
    population: dict,
) -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titleweight": "semibold",
            "axes.labelcolor": INK,
            "text.color": INK,
        }
    )
    parity = rotation_parity(fit["theta"], fit["slope_radians_per_sample"])
    colors = np.where(parity == 0, BLUE, GOLD)
    samples = np.arange(len(u))

    figure = plt.figure(figsize=(15, 12), facecolor=LIGHT)
    grid = figure.add_gridspec(
        2,
        2,
        left=0.07,
        right=0.96,
        bottom=0.08,
        top=0.88,
        hspace=0.31,
        wspace=0.24,
    )
    axis_flat = figure.add_subplot(grid[0, 0])
    axis_3d = figure.add_subplot(grid[0, 1], projection="3d")
    axis_angle = figure.add_subplot(grid[1, 0])
    axis_lag = figure.add_subplot(grid[1, 1])

    figure.suptitle(
        "Q40C — post-result two-turn projection audit",
        x=0.5,
        y=0.965,
        fontsize=20,
        fontweight="bold",
        color=INK,
    )
    families = population["posthoc_period_families"]
    figure.text(
        0.5,
        0.925,
        (
            "Seed 0, pair (2, 5) · closure side × closure flow · "
            "sample order restored as height"
        ),
        ha="center",
        fontsize=11,
        color=MID,
    )

    axis_flat.plot(u, v, color="#AAB2BD", linewidth=0.8, alpha=0.8, zorder=1)
    for state, color, label in (
        (0, BLUE, "alternate turn A"),
        (1, GOLD, "alternate turn B"),
    ):
        mask = parity == state
        axis_flat.scatter(
            u[mask],
            v[mask],
            s=24,
            c=color,
            edgecolors="white",
            linewidths=0.35,
            alpha=0.88,
            label=label,
            zorder=2,
        )
    axis_flat.axhline(0, color=INK, linewidth=0.9)
    axis_flat.axvline(0, color=INK, linewidth=0.9)
    axis_flat.set(
        title="Flattened ARA cut with alternating sampled turns",
        xlabel="closure side u",
        ylabel="closure flow v",
    )
    axis_flat.grid(color=GRID, linewidth=0.7, alpha=0.75)
    axis_flat.legend(frameon=False, loc="lower right", fontsize=9)
    axis_flat.set_aspect("equal", adjustable="box")
    style_axis(axis_flat)

    display = min(len(u), 75)
    axis_3d.plot(
        u[:display],
        v[:display],
        samples[:display],
        color="#9AA3AE",
        linewidth=1.0,
        alpha=0.75,
    )
    for state, color, label in (
        (0, BLUE, "alternate turn A"),
        (1, GOLD, "alternate turn B"),
    ):
        mask = parity[:display] == state
        axis_3d.scatter(
            u[:display][mask],
            v[:display][mask],
            samples[:display][mask],
            color=color,
            s=22,
            depthshade=False,
            label=label,
        )
    axis_3d.set(
        title="Same path with sample order restored",
        xlabel="closure side u",
        ylabel="closure flow v",
        zlabel="sample order",
    )
    axis_3d.view_init(elev=22, azim=-58)
    axis_3d.legend(frameon=False, loc="upper left", fontsize=8)
    axis_3d.grid(True, color=GRID, linewidth=0.6)
    axis_3d.xaxis.pane.set_facecolor((1, 1, 1, 1))
    axis_3d.yaxis.pane.set_facecolor((1, 1, 1, 1))
    axis_3d.zaxis.pane.set_facecolor((1, 1, 1, 1))
    axis_3d.tick_params(colors=MID, labelsize=8)

    axis_angle.plot(
        fit["sample"],
        fit["theta"],
        color=BLUE,
        linewidth=1.8,
        label="unwrapped angle",
    )
    axis_angle.plot(
        fit["sample"],
        fit["fitted"],
        color=INK,
        linestyle="--",
        linewidth=1.3,
        label="linear rotation fit",
    )
    axis_angle.set(
        title=(
            "Unwrapped orbit angle "
            f"(period {fit['angular_period_samples']:.3f} samples; "
            f"R² {fit['angle_time_r_squared']:.6f})"
        ),
        xlabel="sample order",
        ylabel="unwrapped angle (radians)",
    )
    axis_angle.grid(color=GRID, linewidth=0.7, alpha=0.75)
    axis_angle.legend(frameon=False, fontsize=9)
    style_axis(axis_angle)

    lags = np.arange(1, 31)
    correlations = [
        lag_metrics(u, v, fit["theta"], int(lag))["coordinate_correlation"]
        for lag in lags
    ]
    axis_lag.plot(
        lags,
        correlations,
        color=BLUE,
        marker="o",
        markersize=3.5,
        linewidth=1.5,
    )
    floor_lag = fit["lag_one_turn_floor"]["lag"]
    ceil_lag = fit["lag_one_turn_ceil"]["lag"]
    two_lag = fit["lag_two_turn"]["lag"]
    axis_lag.axvspan(
        floor_lag - 0.12,
        ceil_lag + 0.12,
        color=GOLD,
        alpha=0.18,
        label="one-turn bracket",
    )
    axis_lag.axvline(
        two_lag,
        color=RED,
        linestyle="--",
        linewidth=1.4,
        label=f"two-turn return (lag {two_lag})",
    )
    axis_lag.axhline(0, color=INK, linewidth=0.8)
    axis_lag.set(
        title="Coordinate return by sample lag",
        xlabel="lag (samples)",
        ylabel="u–v coordinate correlation",
        xlim=(1, 30),
        ylim=(-1.05, 1.05),
    )
    axis_lag.grid(color=GRID, linewidth=0.7, alpha=0.75)
    axis_lag.legend(frameon=False, fontsize=9, loc="lower right")
    style_axis(axis_lag)

    sample_two = fit["lag_two_turn"]["coordinate_correlation"]
    sample_one = max(
        fit["lag_one_turn_floor"]["coordinate_correlation"],
        fit["lag_one_turn_ceil"]["coordinate_correlation"],
    )
    figure.text(
        0.07,
        0.025,
        (
            f"Sample: one-turn best r={sample_one:.3f}; "
            f"two-turn r={sample_two:.6f}.  "
            f"Population: {families['two_turn_7_5_sample_family_count']}/"
            f"{population['audited_lineages']} lineages use the 7.5-sample "
            "two-turn family; "
            f"{families['one_turn_15_sample_family_count']} use one 15-sample "
            "turn.  This is post-result geometry, not a Q40 rescore."
        ),
        ha="left",
        fontsize=9.5,
        color=MID,
    )

    figure.savefig(FIGURE_PNG, dpi=180, facecolor=figure.get_facecolor())
    figure.savefig(FIGURE_SVG, facecolor=figure.get_facecolor())
    plt.close(figure)


def main() -> None:
    if not DERIVED.exists() or not PREDICTIONS.exists():
        raise RuntimeError("Q40 caches and frozen predictions are required")
    with np.load(DERIVED, allow_pickle=False) as derived:
        closure = np.asarray(derived["closure"], dtype=np.float64)

    pair_index = PAIRS.index(SAMPLE_PAIR)
    coord = coordinates(closure[SAMPLE_SEED, :, pair_index])
    if coord is None:
        raise RuntimeError("Frozen Q40 plane sample is not eligible")
    u = np.asarray(coord[0][EVAL_FIRST:EVAL_LAST_EXCLUSIVE])
    v = np.asarray(coord[1][EVAL_FIRST:EVAL_LAST_EXCLUSIVE])
    sample_fit = fit_orbit(u, v)

    rows, population = population_audit(closure)
    q40_outcomes = q40_outcomes_by_period_family(rows)
    make_figure(u, v, sample_fit, population)

    payload = {
        "audit_id": "Q40C-POST-RESULT-DOUBLE-HELIX-PROJECTION-v1",
        "status": "DESCRIPTIVE POST-RESULT; Q40/T295 VERDICT UNCHANGED",
        "question": (
            "Does the flattened Q40 ARA path contain two interleaved sampled "
            "turns that close only after a two-turn return?"
        ),
        "coordinate_definition": {
            "u": "development-normalised closure side",
            "v": "development-normalised first difference of closure",
            "third_axis": "evaluation sample order",
        },
        "sample": {
            "seed": SAMPLE_SEED,
            "pair_index": pair_index,
            "pair": list(SAMPLE_PAIR),
            "evaluation_slice": [EVAL_FIRST, EVAL_LAST_EXCLUSIVE],
            **clean_fit(sample_fit),
        },
        "population_summary": population,
        "q40_outcomes_by_period_family": q40_outcomes,
        "population_rows": rows,
        "descriptive_signature_definition": {
            "angle_time_r_squared_minimum": 0.98,
            "distance_from_half_integer_period_maximum": 0.10,
            "two_turn_coordinate_correlation_minimum": 0.95,
            "two_turn_advantage_over_best_adjacent_one_turn_lag_minimum": 0.20,
            "period_family_windows": {
                "two_turn_7_5_sample_family": [7.35, 7.65],
                "one_turn_15_sample_family": [14.8, 15.2],
                "both_require_fixed_lag_15_coordinate_correlation_minimum": 0.95,
            },
        },
        "interpretation_boundary": (
            "A two-turn sampled closure supports the visual presence of two "
            "interleaved phase tracks in this projection.  It does not by "
            "itself prove two independent physical waves; the structure may "
            "also arise from stroboscopic sampling or the simulator cadence."
        ),
        "artifacts": {
            "png": FIGURE_PNG.name,
            "svg": FIGURE_SVG.name,
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["sample"], indent=2))
    print(json.dumps(population, indent=2))
    print(f"wrote {OUTPUT}")
    print(f"wrote {FIGURE_PNG}")


if __name__ == "__main__":
    main()
