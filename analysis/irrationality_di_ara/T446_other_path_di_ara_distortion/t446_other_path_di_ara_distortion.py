from __future__ import annotations

import json
import math
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)
T445 = ROOT.parent / "T445_lens_te_ara_other_recovery" / "results"

PAIR_ORDER = ["AC", "AB", "AD"]  # spatial order A -> C -> B -> D, after origin A
SCENARIOS = {
    "selected_AC_-5.3d": 0.0,
    "alternate_AC_+7.9d": 13.2,
}
COLORS = {
    "known": "#357ABD",
    "selected": "#E69F00",
    "alternate": "#CC79A7",
    "target": "#111111",
    "straight": "#7F8C8D",
    "distorted": "#009E73",
    "opposite": "#D55E00",
}


def wrap(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))


def signed_turn(p0: np.ndarray, p1: np.ndarray, p2: np.ndarray) -> float:
    v1 = p1 - p0
    v2 = p2 - p1
    cross_z = float(v1[0] * v2[1] - v1[1] * v2[0])
    return math.atan2(cross_z, float(np.dot(v1, v2)))


def rotate(vector: np.ndarray, angle: float) -> np.ndarray:
    c, s = math.cos(angle), math.sin(angle)
    return np.array([c * vector[0] - s * vector[1], s * vector[0] + c * vector[1]])


def angle_between(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom <= 0:
        return float("nan")
    cosine = float(np.clip(np.dot(a, b) / denom, -1.0, 1.0))
    return math.degrees(math.acos(cosine))


def path_metrics(points: np.ndarray) -> dict[str, float]:
    steps = np.diff(points, axis=0)
    lengths = np.linalg.norm(steps, axis=1)
    total_length = float(lengths.sum())
    direct = float(np.linalg.norm(points[-1] - points[0]))
    directness = direct / total_length if total_length > 0 else float("nan")
    turns = np.array(
        [signed_turn(points[i], points[i + 1], points[i + 2]) for i in range(len(points) - 2)]
    )
    total_turn = float(np.abs(turns).sum())
    signed_net_turn = float(turns.sum())
    turn_consistency = abs(signed_net_turn) / total_turn if total_turn > 0 else 0.0
    circularity = (1.0 - directness) * turn_consistency
    return {
        "directness_D": directness,
        "turn_consistency_G": turn_consistency,
        "historical_circularity_C": circularity,
        "signed_net_turn_deg": math.degrees(signed_net_turn),
        "absolute_turn_deg": math.degrees(total_turn),
        "path_length_arcsec2": total_length,
        "endpoint_displacement_arcsec2": direct,
    }


def quantile_summary(frame: pd.DataFrame, group_cols: list[str], value_cols: list[str]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for key, group in frame.groupby(group_cols, sort=False):
        if not isinstance(key, tuple):
            key = (key,)
        row = dict(zip(group_cols, key))
        for column in value_cols:
            values = group[column].to_numpy(dtype=float)
            row[f"{column}_q16"] = float(np.nanquantile(values, 0.16))
            row[f"{column}_median"] = float(np.nanmedian(values))
            row[f"{column}_q84"] = float(np.nanquantile(values, 0.84))
        rows.append(row)
    return pd.DataFrame(rows)


def build_draws(samples: pd.DataFrame, decomposition: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    dphi_per_day = float(
        decomposition.loc[decomposition["pair"] == "AB", "observed_dphi_arcsec2"].iloc[0]
        / decomposition.loc[decomposition["pair"] == "AB", "observed_delay_days"].iloc[0]
    )
    path_rows: list[dict[str, object]] = []
    transfer_rows: list[dict[str, object]] = []
    origin = np.zeros(2)

    for draw, draw_frame in samples.groupby("draw", sort=True):
        indexed = draw_frame.set_index("pair")
        known = {
            pair: np.array(
                [indexed.loc[pair, "geometric_a_arcsec2"], indexed.loc[pair, "potential_b_arcsec2"]],
                dtype=float,
            )
            for pair in PAIR_ORDER
        }

        known_points = np.vstack([origin] + [known[pair] for pair in PAIR_ORDER])
        known_metrics = path_metrics(known_points)

        for scenario, ac_shift_days in SCENARIOS.items():
            outcome: dict[str, np.ndarray] = {}
            for pair in PAIR_ORDER:
                observed_dphi = float(indexed.loc[pair, "observed_dphi_arcsec2"])
                if pair == "AC":
                    observed_dphi += ac_shift_days * dphi_per_day
                a_value = float(indexed.loc[pair, "geometric_a_arcsec2"])
                outcome[pair] = np.array([a_value, observed_dphi - a_value], dtype=float)

            outcome_points = np.vstack([origin] + [outcome[pair] for pair in PAIR_ORDER])
            outcome_metrics = path_metrics(outcome_points)
            path_rows.append(
                {
                    "draw": int(draw),
                    "scenario": scenario,
                    **{f"known_{key}": value for key, value in known_metrics.items()},
                    **{f"outcome_{key}": value for key, value in outcome_metrics.items()},
                }
            )

            for holdout in PAIR_ORDER:
                calibration_pairs = [pair for pair in PAIR_ORDER if pair != holdout]
                known_turn = signed_turn(origin, known[calibration_pairs[0]], known[calibration_pairs[1]])
                outcome_turn = signed_turn(
                    origin, outcome[calibration_pairs[0]], outcome[calibration_pairs[1]]
                )
                delta = wrap(outcome_turn - known_turn)

                endpoint = known[holdout]
                target = outcome[holdout]
                residual = target - endpoint
                magnitude = float(np.linalg.norm(residual))
                tangent = np.array(
                    [indexed.loc[holdout, "tangent_x"], indexed.loc[holdout, "tangent_y"]], dtype=float
                )
                tangent /= np.linalg.norm(tangent)
                orientation_sign = 1.0 if float(np.dot(residual, tangent)) >= 0 else -1.0
                tangent *= orientation_sign

                distorted_direction = rotate(tangent, delta)
                opposite_direction = rotate(tangent, -delta)
                straight_prediction = endpoint + magnitude * tangent
                distorted_prediction = endpoint + magnitude * distorted_direction
                opposite_prediction = endpoint + magnitude * opposite_direction

                baseline_error = float(np.linalg.norm(straight_prediction - target))
                distorted_error = float(np.linalg.norm(distorted_prediction - target))
                opposite_error = float(np.linalg.norm(opposite_prediction - target))
                ratio = distorted_error / baseline_error if baseline_error > 1e-15 else float("nan")

                transfer_rows.append(
                    {
                        "draw": int(draw),
                        "scenario": scenario,
                        "holdout_pair": holdout,
                        "calibration_pair_1": calibration_pairs[0],
                        "calibration_pair_2": calibration_pairs[1],
                        "known_turn_deg": math.degrees(known_turn),
                        "outcome_turn_deg": math.degrees(outcome_turn),
                        "distortion_delta_deg": math.degrees(delta),
                        "residual_magnitude_arcsec2": magnitude,
                        "orientation_sign_from_te_ara": orientation_sign,
                        "target_direction_x": residual[0] / magnitude,
                        "target_direction_y": residual[1] / magnitude,
                        "straight_direction_x": tangent[0],
                        "straight_direction_y": tangent[1],
                        "distorted_direction_x": distorted_direction[0],
                        "distorted_direction_y": distorted_direction[1],
                        "opposite_direction_x": opposite_direction[0],
                        "opposite_direction_y": opposite_direction[1],
                        "baseline_landing_error_arcsec2": baseline_error,
                        "distorted_landing_error_arcsec2": distorted_error,
                        "opposite_landing_error_arcsec2": opposite_error,
                        "distorted_to_straight_error_ratio": ratio,
                        "straight_angular_error_deg": angle_between(tangent, residual),
                        "distorted_angular_error_deg": angle_between(distorted_direction, residual),
                        "opposite_angular_error_deg": angle_between(opposite_direction, residual),
                        "distorted_improves": bool(distorted_error < baseline_error),
                        "distorted_beats_opposite": bool(distorted_error < opposite_error),
                    }
                )

    return pd.DataFrame(path_rows), pd.DataFrame(transfer_rows)


def build_summaries(path_draws: pd.DataFrame, transfer_draws: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    path_values = [
        "known_directness_D",
        "known_turn_consistency_G",
        "known_historical_circularity_C",
        "known_signed_net_turn_deg",
        "outcome_directness_D",
        "outcome_turn_consistency_G",
        "outcome_historical_circularity_C",
        "outcome_signed_net_turn_deg",
    ]
    path_summary = quantile_summary(path_draws, ["scenario"], path_values)

    transfer_values = [
        "distortion_delta_deg",
        "baseline_landing_error_arcsec2",
        "distorted_landing_error_arcsec2",
        "opposite_landing_error_arcsec2",
        "distorted_to_straight_error_ratio",
        "straight_angular_error_deg",
        "distorted_angular_error_deg",
        "opposite_angular_error_deg",
    ]
    transfer_summary = quantile_summary(
        transfer_draws, ["scenario", "holdout_pair"], transfer_values
    )
    rates = (
        transfer_draws.groupby(["scenario", "holdout_pair"], sort=False)
        .agg(
            fraction_improved=("distorted_improves", "mean"),
            fraction_beats_opposite=("distorted_beats_opposite", "mean"),
            draws=("draw", "count"),
        )
        .reset_index()
    )
    transfer_summary = transfer_summary.merge(rates, on=["scenario", "holdout_pair"], how="left")
    role_map = {
        "AC": "first-child reconstruction",
        "AB": "internal-child interpolation",
        "AD": "terminal forward continuation",
    }
    transfer_summary.insert(2, "holdout_role", transfer_summary["holdout_pair"].map(role_map))
    return path_summary, transfer_summary


def central_paths(samples: pd.DataFrame, decomposition: pd.DataFrame) -> pd.DataFrame:
    central = samples.groupby("pair", sort=False).median(numeric_only=True)
    dphi_per_day = float(
        decomposition.loc[decomposition["pair"] == "AB", "observed_dphi_arcsec2"].iloc[0]
        / decomposition.loc[decomposition["pair"] == "AB", "observed_delay_days"].iloc[0]
    )
    rows: list[dict[str, object]] = [
        {"scenario": "known", "point_order": 0, "relation": "O", "A_arcsec2": 0.0, "B_arcsec2": 0.0}
    ]
    for order, pair in enumerate(PAIR_ORDER, start=1):
        rows.append(
            {
                "scenario": "known",
                "point_order": order,
                "relation": pair,
                "A_arcsec2": float(central.loc[pair, "geometric_a_arcsec2"]),
                "B_arcsec2": float(central.loc[pair, "potential_b_arcsec2"]),
            }
        )
    for scenario, shift_days in SCENARIOS.items():
        rows.append(
            {"scenario": scenario, "point_order": 0, "relation": "O", "A_arcsec2": 0.0, "B_arcsec2": 0.0}
        )
        for order, pair in enumerate(PAIR_ORDER, start=1):
            observed_dphi = float(central.loc[pair, "observed_dphi_arcsec2"])
            if pair == "AC":
                observed_dphi += shift_days * dphi_per_day
            a_value = float(central.loc[pair, "geometric_a_arcsec2"])
            rows.append(
                {
                    "scenario": scenario,
                    "point_order": order,
                    "relation": pair,
                    "A_arcsec2": a_value,
                    "B_arcsec2": observed_dphi - a_value,
                }
            )
    return pd.DataFrame(rows)


def metric_text(points: pd.DataFrame) -> str:
    values = path_metrics(points[["A_arcsec2", "B_arcsec2"]].to_numpy())
    return f"D={values['directness_D']:.3f}   G={values['turn_consistency_G']:.3f}   C={values['historical_circularity_C']:.3f}"


def style_axis(ax: plt.Axes) -> None:
    ax.grid(True, color="#DDE3EA", linewidth=0.7, alpha=0.8)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_color("#AAB4C0")


def plot_path_geometry(
    central: pd.DataFrame, path_draws: pd.DataFrame, path_summary: pd.DataFrame
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(15, 12), constrained_layout=True)
    fig.suptitle(
        "T446 — Other-section path Irrationality Di-ARA\nSpatial child-ring cut; not chronological time",
        fontsize=18,
        fontweight="bold",
    )

    panels = [
        ("selected_AC_-5.3d", "Selected AC solution (−5.3 d)"),
        ("alternate_AC_+7.9d", "AC sign sensitivity (+7.9 d)"),
    ]
    for ax, (scenario, title) in zip(axes[0], panels):
        known = central[central["scenario"] == "known"].sort_values("point_order")
        outcome = central[central["scenario"] == scenario].sort_values("point_order")
        ax.plot(
            known["A_arcsec2"], known["B_arcsec2"], "o-", color=COLORS["known"], lw=2.5,
            label=f"Known A/B path   {metric_text(known)}",
        )
        ax.plot(
            outcome["A_arcsec2"], outcome["B_arcsec2"], "o-", color=COLORS["selected"] if "selected" in scenario else COLORS["alternate"], lw=2.5,
            label=f"Outcome-compatible Other   {metric_text(outcome)}",
        )
        for _, row in outcome.iterrows():
            ax.annotate(
                row["relation"], (row["A_arcsec2"], row["B_arcsec2"]), xytext=(5, 6),
                textcoords="offset points", fontsize=10, fontweight="bold",
            )
        ax.axhline(0, color="#555555", lw=0.8)
        ax.axvline(0, color="#555555", lw=0.8)
        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.set_xlabel("Te-ARA Phase A / geometric component (arcsec²)")
        ax.set_ylabel("Te-ARA Phase B / potential component (arcsec²)")
        ax.legend(fontsize=8, loc="best")
        style_axis(ax)

    ax = axes[1, 0]
    known_d = path_draws["known_directness_D"]
    known_g = path_draws["known_turn_consistency_G"]
    ax.scatter(known_d[::8], known_g[::8], s=12, alpha=0.22, color=COLORS["known"], label="Known path")
    for scenario, label, color in [
        ("selected_AC_-5.3d", "Selected Other", COLORS["selected"]),
        ("alternate_AC_+7.9d", "Alternate-AC Other", COLORS["alternate"]),
    ]:
        subset = path_draws[path_draws["scenario"] == scenario]
        ax.scatter(
            subset["outcome_directness_D"].iloc[::4], subset["outcome_turn_consistency_G"].iloc[::4],
            s=13, alpha=0.25, color=color, label=label,
        )
    ax.set_xlim(0, 1.03)
    ax.set_ylim(0, 1.03)
    ax.set_xlabel("Directness D = endpoint displacement / path length")
    ax.set_ylabel("One-way turn consistency G")
    ax.set_title("Line-versus-coherent-curve coordinates (2,000 draws)", fontweight="bold")
    ax.legend(fontsize=9)
    style_axis(ax)

    ax = axes[1, 1]
    series = [path_draws["known_historical_circularity_C"]]
    labels = ["Known"]
    colors = [COLORS["known"]]
    for scenario, label, color in [
        ("selected_AC_-5.3d", "Other selected", COLORS["selected"]),
        ("alternate_AC_+7.9d", "Other alt-AC", COLORS["alternate"]),
    ]:
        series.append(path_draws.loc[path_draws["scenario"] == scenario, "outcome_historical_circularity_C"])
        labels.append(label)
        colors.append(color)
    parts = ax.violinplot(series, showmedians=True, showextrema=False)
    for body, color in zip(parts["bodies"], colors):
        body.set_facecolor(color)
        body.set_alpha(0.65)
    parts["cmedians"].set_color("#111111")
    ax.set_xticks(range(1, len(labels) + 1), labels)
    ax.set_ylabel("Historical circularity C = (1 − D)G")
    ax.set_title("Recovered curvature history", fontweight="bold")
    style_axis(ax)

    fig.savefig(RESULTS / "T446_OTHER_PATH_GEOMETRY.png", dpi=180)
    plt.close(fig)


def plot_transfer(transfer_draws: pd.DataFrame, transfer_summary: pd.DataFrame) -> None:
    clean = transfer_draws[transfer_draws["holdout_pair"].isin(["AB", "AD"])].copy()
    fig, axes = plt.subplots(2, 2, figsize=(15, 12), constrained_layout=True)
    fig.suptitle(
        "T446 — Apply the Other-path distortion angle to the known A/B path",
        fontsize=18,
        fontweight="bold",
    )

    categories = [
        ("selected_AC_-5.3d", "AB"),
        ("selected_AC_-5.3d", "AD"),
        ("alternate_AC_+7.9d", "AB"),
        ("alternate_AC_+7.9d", "AD"),
    ]
    labels = [
        "Selected\nAB (internal)",
        "Selected\nAD (terminal)",
        "Alt AC\nAB (internal)",
        "Alt AC\nAD (terminal)",
    ]
    palette = [COLORS["selected"], COLORS["selected"], COLORS["alternate"], COLORS["alternate"]]

    ax = axes[0, 0]
    data = [
        clean[(clean["scenario"] == scenario) & (clean["holdout_pair"] == pair)]["distortion_delta_deg"]
        for scenario, pair in categories
    ]
    boxes = ax.boxplot(data, tick_labels=labels, showfliers=False, patch_artist=True)
    for box, color in zip(boxes["boxes"], palette):
        box.set_facecolor(color)
        box.set_alpha(0.65)
    ax.axhline(0, color="#555555", lw=1)
    ax.set_ylabel("Transferred bend δ (degrees)")
    ax.set_title("Bend learned from the other two children", fontweight="bold")
    style_axis(ax)

    ax = axes[0, 1]
    ratio_data = [
        clean[(clean["scenario"] == scenario) & (clean["holdout_pair"] == pair)]["distorted_to_straight_error_ratio"]
        for scenario, pair in categories
    ]
    boxes = ax.boxplot(ratio_data, tick_labels=labels, showfliers=False, patch_artist=True)
    for box, color in zip(boxes["boxes"], palette):
        box.set_facecolor(color)
        box.set_alpha(0.65)
    ax.axhline(1, color="#111111", ls="--", lw=1.5, label="1 = no improvement")
    ax.set_ylabel("Distorted landing error / straight landing error")
    ax.set_title("Below 1 means the transferred curvature helps", fontweight="bold")
    ax.legend(fontsize=9)
    style_axis(ax)

    ax = axes[1, 0]
    x = np.arange(len(categories))
    width = 0.24
    modes = [
        ("straight_angular_error_deg_median", "Straight", COLORS["straight"]),
        ("distorted_angular_error_deg_median", "Transferred bend", COLORS["distorted"]),
        ("opposite_angular_error_deg_median", "Opposite bend", COLORS["opposite"]),
    ]
    for offset, (column, label, color) in enumerate(modes):
        values = []
        for scenario, pair in categories:
            row = transfer_summary[
                (transfer_summary["scenario"] == scenario) & (transfer_summary["holdout_pair"] == pair)
            ].iloc[0]
            values.append(float(row[column]))
        bars = ax.bar(x + (offset - 1) * width, values, width, label=label, color=color, alpha=0.85)
        ax.bar_label(bars, fmt="%.1f°", fontsize=8, padding=2)
    ax.set_xticks(x, labels)
    ax.set_ylabel("Median angular error to held-out outcome (degrees)")
    ax.set_title("Direction reconstruction, with opposite-sign control", fontweight="bold")
    ax.legend(fontsize=9)
    style_axis(ax)

    ax = axes[1, 1]
    direction_colors = {
        "Target outcome": COLORS["target"],
        "Straight": COLORS["straight"],
        "Transferred bend": COLORS["distorted"],
        "Opposite bend": COLORS["opposite"],
    }
    offsets = {"AB": np.array([0.0, 0.0]), "AD": np.array([2.6, 0.0])}
    selected = clean[clean["scenario"] == "selected_AC_-5.3d"]
    for pair in ["AB", "AD"]:
        subset = selected[selected["holdout_pair"] == pair]
        origin = offsets[pair]
        vectors = {
            "Target outcome": np.array([subset["target_direction_x"].median(), subset["target_direction_y"].median()]),
            "Straight": np.array([subset["straight_direction_x"].median(), subset["straight_direction_y"].median()]),
            "Transferred bend": np.array([subset["distorted_direction_x"].median(), subset["distorted_direction_y"].median()]),
            "Opposite bend": np.array([subset["opposite_direction_x"].median(), subset["opposite_direction_y"].median()]),
        }
        for label, vector in vectors.items():
            vector = vector / np.linalg.norm(vector)
            ax.arrow(
                origin[0], origin[1], vector[0], vector[1], width=0.012, head_width=0.08,
                length_includes_head=True, color=direction_colors[label], alpha=0.88,
                label=label if pair == "AB" else None,
            )
        ax.text(origin[0], -1.28, f"Held-out {pair}", ha="center", fontweight="bold")
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-1.3, 3.9)
    ax.set_ylim(-1.45, 1.45)
    ax.set_xlabel("Unit direction in Te-ARA A/B plane")
    ax.set_ylabel("Unit direction in Te-ARA A/B plane")
    ax.set_title("Selected-AC median direction vectors", fontweight="bold")
    ax.legend(fontsize=8, loc="upper center", ncol=2)
    style_axis(ax)

    fig.savefig(RESULTS / "T446_DISTORTION_TRANSFER.png", dpi=180)
    plt.close(fig)


def verdict(transfer_summary: pd.DataFrame) -> dict[str, object]:
    clean = transfer_summary[transfer_summary["holdout_pair"].isin(["AB", "AD"])].copy()
    rows = clean.to_dict(orient="records")
    robust = bool(
        (clean["distorted_to_straight_error_ratio_median"] < 1.0).all()
        and (clean["fraction_improved"] > 0.5).all()
    )
    selected = clean[clean["scenario"] == "selected_AC_-5.3d"]
    alternate = clean[clean["scenario"] == "alternate_AC_+7.9d"]
    selected_help = bool(
        (selected["distorted_to_straight_error_ratio_median"] < 1.0).all()
        and (selected["fraction_improved"] > 0.5).all()
    )
    alternate_help = bool(
        (alternate["distorted_to_straight_error_ratio_median"] < 1.0).all()
        and (alternate["fraction_improved"] > 0.5).all()
    )
    terminal = clean[clean["holdout_pair"] == "AD"]
    terminal_selected = terminal[terminal["scenario"] == "selected_AC_-5.3d"].iloc[0]
    terminal_alternate = terminal[terminal["scenario"] == "alternate_AC_+7.9d"].iloc[0]
    terminal_selected_help = bool(
        terminal_selected["distorted_to_straight_error_ratio_median"] < 1.0
        and terminal_selected["fraction_improved"] > 0.5
    )
    terminal_alternate_help = bool(
        terminal_alternate["distorted_to_straight_error_ratio_median"] < 1.0
        and terminal_alternate["fraction_improved"] > 0.5
    )
    if robust:
        frozen_status = "directionally_robust_under_AC_sensitivity"
    elif selected_help != alternate_help:
        frozen_status = "AC_sign_sensitive_unresolved"
    else:
        frozen_status = "transferred_bend_not_consistently_helpful"
    if terminal_selected_help and not terminal_alternate_help:
        geometry_status = "terminal_continuation_improves_only_for_selected_AC; AC_sign_sensitive"
    elif terminal_selected_help and terminal_alternate_help:
        geometry_status = "terminal_continuation_robustly_improves"
    else:
        geometry_status = "terminal_continuation_not_supported"
    return {
        "status": f"{frozen_status}; {geometry_status}",
        "frozen_all_clean_pair_status": frozen_status,
        "geometry_first_terminal_status": geometry_status,
        "robust_under_both_AC_solutions": robust,
        "selected_solution_helps_both_clean_pairs": selected_help,
        "alternate_solution_helps_both_clean_pairs": alternate_help,
        "terminal_selected_solution_helps": terminal_selected_help,
        "terminal_alternate_solution_helps": terminal_alternate_help,
        "clean_pair_summaries": rows,
    }


def write_findings(result: dict[str, object], path_summary: pd.DataFrame, transfer_summary: pd.DataFrame) -> None:
    lines = [
        "# T446 findings — Other-path Irrationality Di-ARA and distortion transfer",
        "",
        f"**Frozen all-clean-pair result:** `{result['verdict']['frozen_all_clean_pair_status']}`",
        "",
        f"**Geometry-first terminal-continuation result:** `{result['verdict']['geometry_first_terminal_status']}`",
        "",
        "## What was actually measured",
        "",
        "The original T345 path instrument (D directness, G one-way turn consistency, C conservative historical circularity) was applied to the spatial child-relation order `O → AC → AB → AD`. This is the available multi-point Other path in WGD 2038−4008. It is a spatial relation-field reconstruction, not chronological time and not one photon trajectory.",
        "",
        "An individual pair still supplies only one Other displacement. Its D=1 value is definitional and has no identifiable turn, so it is not evidence that the individual Other is straight.",
        "",
        "## Path geometry",
        "",
    ]
    for _, row in path_summary.iterrows():
        lines.append(
            f"- `{row['scenario']}`: known median D/G/C = "
            f"{row['known_directness_D_median']:.3f} / {row['known_turn_consistency_G_median']:.3f} / {row['known_historical_circularity_C_median']:.3f}; "
            f"Other median D/G/C = {row['outcome_directness_D_median']:.3f} / "
            f"{row['outcome_turn_consistency_G_median']:.3f} / {row['outcome_historical_circularity_C_median']:.3f}."
        )
    lines.extend(["", "## Held-out distortion transfer", ""])
    for _, row in transfer_summary[transfer_summary["holdout_pair"].isin(["AB", "AD"])].iterrows():
        lines.append(
            f"- `{row['scenario']}`, held-out {row['holdout_pair']} ({row['holdout_role']}): δ median "
            f"{row['distortion_delta_deg_median']:.1f}°; distorted/straight landing-error ratio "
            f"{row['distorted_to_straight_error_ratio_median']:.3f}; improved in "
            f"{100*row['fraction_improved']:.1f}% of 2,000 draws; median angular error "
            f"{row['straight_angular_error_deg_median']:.1f}° → {row['distorted_angular_error_deg_median']:.1f}°."
        )
    lines.extend(
        [
            "",
            "## Boundary on the claim",
            "",
            "The held-out child’s bend is learned from the other two children, but Te-ARA supplies the held-out residual magnitude and its forward/backward half-plane. Therefore this is a curvature-direction reconstruction test, not a blind delay or event forecast.",
            "",
            "AB and AD both depend on AC in this three-child leave-one-out geometry. The selected −5.3 d and alternate +7.9 d AC solutions are therefore displayed as separate required sensitivity cases; the verdict above refuses a robust conclusion if that choice reverses the direction result.",
            "",
            "A topology audit after calculation distinguishes the two clean holdouts: AD is the only true forward continuation of `O → AC → AB`; AB is an internal interpolation because removing it joins non-adjacent AC directly to AD. The frozen all-clean-pair verdict is retained, while the terminal AD result is reported separately rather than silently treating those geometries as equivalent.",
        ]
    )
    (RESULTS / "T446_FINDINGS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    samples = pd.read_csv(T445 / "T445_UNCERTAINTY_SAMPLES.csv")
    decomposition = pd.read_csv(T445 / "T445_DECOMPOSITION.csv")
    path_draws, transfer_draws = build_draws(samples, decomposition)
    path_summary, transfer_summary = build_summaries(path_draws, transfer_draws)
    central = central_paths(samples, decomposition)
    result = {
        "test": "T446",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "question": "Does the Other-section path bend, learned from sibling children, improve the known A/B continuation direction?",
        "identity": "WGD 2038-4008 spatial child-relation field",
        "path_order": ["O", *PAIR_ORDER],
        "per_pair_identifiability": "one displacement only: D=1 by definition; G and C not identifiable",
        "method": "T345 D/G/C path Irrationality Di-ARA plus leave-one-child-out distortion-angle transfer",
        "verdict": verdict(transfer_summary),
        "limits": [
            "spatial child-ring, not chronological time",
            "not one photon trajectory",
            "Te-ARA supplies held-out residual magnitude and forward/backward half-plane",
            "local 2,000-draw uncertainty approximation because the full posterior is unavailable",
            "clean AB and AD transfer estimates are load-bearing on the AC sign solution",
        ],
    }

    path_draws.to_csv(RESULTS / "T446_PATH_DRAWS.csv", index=False)
    transfer_draws.to_csv(RESULTS / "T446_TRANSFER_DRAWS.csv", index=False)
    path_summary.to_csv(RESULTS / "T446_PATH_SUMMARY.csv", index=False)
    transfer_summary.to_csv(RESULTS / "T446_TRANSFER_SUMMARY.csv", index=False)
    central.to_csv(RESULTS / "T446_CENTRAL_PATHS.csv", index=False)
    with sqlite3.connect(RESULTS / "T446_ANALYSIS.sqlite") as connection:
        path_draws.to_sql("path_draws", connection, if_exists="replace", index=False)
        transfer_draws.to_sql("transfer_draws", connection, if_exists="replace", index=False)
        path_summary.to_sql("path_summary", connection, if_exists="replace", index=False)
        transfer_summary.to_sql("transfer_summary", connection, if_exists="replace", index=False)
        central.to_sql("central_paths", connection, if_exists="replace", index=False)
    (RESULTS / "T446_RESULT.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    plot_path_geometry(central, path_draws, path_summary)
    plot_transfer(transfer_draws, transfer_summary)
    write_findings(result, path_summary, transfer_summary)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
