"""Q43 frozen descriptive child-ridge and Phi-handover test.

Part A asks whether Q42's exposed scalar residual is centred on the
parent-view child ridge 0.5, before and after the already-defined symmetric
sampling control. Part B tests the exact directional Phi landmark pair
against a fixed grid of ordinary symmetric ARA landmark pairs.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import os
import pathlib
import sys
from collections import defaultdict


HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / "public_data" / "_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(HERE / ".mplconfig"))

import matplotlib.pyplot as plt
import numpy as np

import q40_return_flow_relation_reversal_test as base
import q42_ara_dual_strand_flow_test as q42


TEST_ID = "Q43-CHILD-RIDGE-PHI-HANDOVER-v1"
PROTOCOL = HERE / "Q43_CHILD_RIDGE_AND_PHI_HANDOVER_PROTOCOL_v1_FROZEN.md"
Q42_ROWS = HERE / "Q42_ARA_DUAL_STRAND_FLOW_STRANDS.csv.gz"
Q42_PROFILES = HERE / "Q42_ARA_DUAL_STRAND_FLOW_PROFILES.npz"
RESULTS = HERE / "Q43_CHILD_RIDGE_AND_PHI_HANDOVER_RESULTS.json"
CONTROL_ROWS = HERE / "Q43_CHILD_RIDGE_SAMPLING_CONTROL.csv.gz"
GRID_ROWS = HERE / "Q43_PHI_HANDOVER_GRID.csv"
FIGURE_PNG = HERE / "Q43_CHILD_RIDGE_AND_PHI_HANDOVER_DIAGNOSTICS.png"
FIGURE_SVG = HERE / "Q43_CHILD_RIDGE_AND_PHI_HANDOVER_DIAGNOSTICS.svg"

MID_INDEX = 16
CHILD_RIDGE = 0.5
EQUIVALENCE_BAND = (0.45, 0.55)
PHI = (1 + math.sqrt(5)) / 2
PHI_LOW = 2 - PHI
GRID = np.round(np.arange(0.20, 0.5000001, 0.005), 12)
REFERENCES = {
    "quarter": 0.25,
    "third": 1 / 3,
    "phi": PHI_LOW,
    "two_fifths": 0.40,
    "half": 0.50,
}
BOOTSTRAP_DRAWS = 20_000
BOOTSTRAP_SEED = 430028
EPS = 1e-12

BLUE = "#537DB8"
GOLD = "#D99B31"
ORANGE = "#D85C4A"
INK = "#17212B"
MID = "#647180"
LIGHT = "#DCE4EC"
GRID_COLOR = "#D9E0E7"
BG = "#FAFBFC"


def digest(path: pathlib.Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def finite_summary(values) -> dict:
    data = np.asarray(list(values), dtype=np.float64)
    data = data[np.isfinite(data)]
    if not len(data):
        return {"count": 0}
    return {
        "count": int(len(data)),
        "mean": float(np.mean(data)),
        "p25": float(np.quantile(data, 0.25)),
        "median": float(np.median(data)),
        "p75": float(np.quantile(data, 0.75)),
        "min": float(np.min(data)),
        "max": float(np.max(data)),
    }


def read_q42():
    rows = []
    with gzip.open(Q42_ROWS, "rt", newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            rows.append(
                {
                    "archive": row["archive"],
                    "seed": int(row["seed"]),
                    "pair": int(row["pair"]),
                    "family": row["family"],
                    "cycle": int(row["cycle"]),
                }
            )
    profiles = np.load(Q42_PROFILES)
    progress = np.asarray(profiles["progress"], dtype=np.float64)
    forward = np.asarray(profiles["forward"], dtype=np.float64)
    returning = np.asarray(profiles["returning"], dtype=np.float64)
    residual = np.asarray(profiles["residual"], dtype=np.float64)
    if not (
        len(rows) == len(forward) == len(returning) == len(residual)
        and np.allclose(progress, q42.PROGRESS)
    ):
        raise RuntimeError("Q42 row/profile alignment failed")
    return rows, progress, forward, returning, residual


def bootstrap_seed_median(seed_values: np.ndarray, salt: int) -> dict:
    values = np.asarray(seed_values, dtype=np.float64)
    values = values[np.isfinite(values)]
    if not len(values):
        return {"seeds": 0}
    rng = np.random.default_rng(BOOTSTRAP_SEED + salt)
    estimates = np.empty(BOOTSTRAP_DRAWS, dtype=np.float64)
    for index in range(BOOTSTRAP_DRAWS):
        estimates[index] = float(
            np.median(rng.choice(values, size=len(values), replace=True))
        )
    return {
        "seeds": int(len(values)),
        "estimate": float(np.median(values)),
        "ci95": [
            float(np.quantile(estimates, 0.025)),
            float(np.quantile(estimates, 0.975)),
        ],
        "seed_values": finite_summary(values),
    }


def seed_balanced_cycle_summary(
    rows: list[dict],
    values: np.ndarray,
    archive: str,
    family: str,
    salt: int,
) -> dict:
    grouped = defaultdict(list)
    for index, row in enumerate(rows):
        if row["archive"] == archive and row["family"] == family:
            grouped[row["seed"]].append(float(values[index]))
    seed_values = np.asarray(
        [np.median(items) for items in grouped.values()],
        dtype=np.float64,
    )
    output = bootstrap_seed_median(seed_values, salt)
    output["pairs"] = int(sum(len(items) for items in grouped.values()))
    if output.get("seeds", 0):
        low, high = output["ci95"]
        output["equivalent_to_0_5"] = bool(
            low >= EQUIVALENCE_BAND[0] and high <= EQUIVALENCE_BAND[1]
        )
        output["offset_from_0_5"] = float(output["estimate"] - CHILD_RIDGE)
    return output


def observed_lineage_medians(
    rows: list[dict],
    tau_mid: np.ndarray,
) -> dict:
    grouped = defaultdict(list)
    families = {}
    for row, value in zip(rows, tau_mid):
        key = (row["archive"], row["seed"], row["pair"])
        grouped[key].append(float(value))
        families[key] = row["family"]
    return {
        key: {
            "family": families[key],
            "tau_mid": float(np.median(values)),
            "cycles": len(values),
        }
        for key, values in grouped.items()
    }


def sampling_control(observed: dict) -> list[dict]:
    output = []
    sample = np.arange(500, dtype=np.float64)
    development_sample = sample[:250]
    for archive, paths in q42.DATASETS.items():
        closure = np.asarray(np.load(paths["derived"])["closure"], dtype=np.float32)
        for seed in range(closure.shape[0]):
            for pair in range(closure.shape[2]):
                key = (archive, seed, pair)
                if key not in observed:
                    continue
                coordinate = base.coordinates(closure[seed, :, pair])
                if coordinate is None:
                    continue
                u, v, _labels, _direction, coherence, occupancy = coordinate
                if coherence < 0.80 or occupancy < 0.05:
                    continue
                family, fit = q42.cadence_family(u, v)
                period = float(fit["angular_period_samples"])
                if not np.isfinite(period) or period <= 0:
                    continue
                omega = 2 * np.pi / period
                design = np.column_stack(
                    (
                        np.ones(250),
                        np.cos(omega * development_sample),
                        np.sin(omega * development_sample),
                    )
                )
                coefficients = np.linalg.lstsq(
                    design,
                    np.asarray(closure[seed, :250, pair], dtype=np.float64),
                    rcond=None,
                )[0]
                synthetic = (
                    coefficients[0]
                    + coefficients[1] * np.cos(omega * sample)
                    + coefficients[2] * np.sin(omega * sample)
                )
                (
                    synthetic_rows,
                    _synthetic_forward,
                    _synthetic_return,
                    synthetic_residual,
                ) = q42.extract_strand_pairs(
                    archive,
                    seed,
                    pair,
                    synthetic,
                    family,
                )
                if not synthetic_rows:
                    continue
                synthetic_mid = float(
                    np.median(
                        np.asarray(synthetic_residual, dtype=np.float64)[
                            :, MID_INDEX
                        ]
                    )
                )
                observed_mid = observed[key]["tau_mid"]
                output.append(
                    {
                        "archive": archive,
                        "seed": seed,
                        "pair": pair,
                        "family": family,
                        "period": period,
                        "observed_tau_mid": observed_mid,
                        "symmetric_sampling_tau_mid": synthetic_mid,
                        "corrected_tau_mid": observed_mid - synthetic_mid,
                        "observed_cycles": observed[key]["cycles"],
                        "synthetic_cycles": len(synthetic_rows),
                    }
                )
    return output


def corrected_seed_summary(
    controls: list[dict],
    archive: str,
    family: str,
    salt: int,
) -> dict:
    grouped = defaultdict(list)
    for row in controls:
        if row["archive"] == archive and row["family"] == family:
            grouped[row["seed"]].append(row["corrected_tau_mid"])
    seed_values = np.asarray(
        [np.median(items) for items in grouped.values()],
        dtype=np.float64,
    )
    output = bootstrap_seed_median(seed_values, salt)
    output["lineages"] = int(sum(len(items) for items in grouped.values()))
    if output.get("seeds", 0):
        low, high = output["ci95"]
        output["equivalent_to_0_5"] = bool(
            low >= EQUIVALENCE_BAND[0] and high <= EQUIVALENCE_BAND[1]
        )
        output["offset_from_0_5"] = float(output["estimate"] - CHILD_RIDGE)
    return output


def matched_control_components(
    controls: list[dict],
    archive: str,
    family: str,
) -> dict:
    fields = (
        "observed_tau_mid",
        "symmetric_sampling_tau_mid",
        "corrected_tau_mid",
    )
    output = {}
    for field in fields:
        grouped = defaultdict(list)
        for row in controls:
            if row["archive"] == archive and row["family"] == family:
                grouped[row["seed"]].append(row[field])
        seed_values = np.asarray(
            [np.median(items) for items in grouped.values()],
            dtype=np.float64,
        )
        output[field] = finite_summary(seed_values)
    output["lineages"] = int(
        sum(
            row["archive"] == archive and row["family"] == family
            for row in controls
        )
    )
    return output


def interpolate_progress_and_speed(
    path: np.ndarray,
    progress: np.ndarray,
    coordinates: np.ndarray,
    increasing: bool,
) -> tuple[np.ndarray, np.ndarray]:
    speed = np.abs(np.gradient(path, progress))
    if increasing:
        x_order = path
        p_order = progress
        v_order = speed
    else:
        x_order = path[::-1]
        p_order = progress[::-1]
        v_order = speed[::-1]
    return (
        np.interp(coordinates, x_order, p_order),
        np.interp(coordinates, x_order, v_order),
    )


def candidate_scores(
    forward: np.ndarray,
    returning: np.ndarray,
    progress: np.ndarray,
    lows: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    highs = 2 - lows
    pf_low, vf_low = interpolate_progress_and_speed(
        forward, progress, lows, True
    )
    pf_high, vf_high = interpolate_progress_and_speed(
        forward, progress, highs, True
    )
    pr_low, vr_low = interpolate_progress_and_speed(
        returning, progress, lows, False
    )
    pr_high, vr_high = interpolate_progress_and_speed(
        returning, progress, highs, False
    )
    temporal = 0.5 * (
        np.abs(pf_high - pr_low) + np.abs(pf_low - pr_high)
    )
    speed = 0.5 * (
        np.abs(vf_high - vr_low) / (vf_high + vr_low + EPS)
        + np.abs(vf_low - vr_high) / (vf_low + vr_high + EPS)
    )
    return temporal, speed


def phi_grid_analysis(
    rows: list[dict],
    progress: np.ndarray,
    forward: np.ndarray,
    returning: np.ndarray,
) -> tuple[list[dict], dict]:
    all_candidates = np.unique(
        np.concatenate((GRID, np.asarray(list(REFERENCES.values()))))
    )
    common = (
        (np.min(forward, axis=1) <= 0.20)
        & (np.max(forward, axis=1) >= 1.80)
        & (np.min(returning, axis=1) <= 0.20)
        & (np.max(returning, axis=1) >= 1.80)
    )
    grid_rows = []
    summary = {}
    salt = 1000
    for archive in q42.DATASETS:
        summary[archive] = {}
        for family in ("two_turn_7_5", "one_turn_15"):
            selected = np.asarray(
                [
                    index
                    for index, row in enumerate(rows)
                    if common[index]
                    and row["archive"] == archive
                    and row["family"] == family
                ],
                dtype=np.int64,
            )
            by_seed = defaultdict(list)
            for index in selected:
                by_seed[rows[index]["seed"]].append(index)
            seed_ids = sorted(by_seed)
            temporal_matrix = np.empty(
                (len(selected), len(all_candidates)), dtype=np.float64
            )
            speed_matrix = np.empty_like(temporal_matrix)
            local_by_global = {}
            for local_index, global_index in enumerate(selected):
                temporal, speed = candidate_scores(
                    forward[global_index],
                    returning[global_index],
                    progress,
                    all_candidates,
                )
                temporal_matrix[local_index] = temporal
                speed_matrix[local_index] = speed
                local_by_global[int(global_index)] = local_index
            temporal_by_candidate = []
            speed_by_candidate = []
            for candidate_index, low in enumerate(all_candidates):
                cycle_temporal = {}
                cycle_speed = {}
                for seed in seed_ids:
                    local_indices = np.asarray(
                        [
                            local_by_global[int(index)]
                            for index in by_seed[seed]
                        ],
                        dtype=np.int64,
                    )
                    cycle_temporal[seed] = float(
                        np.median(
                            temporal_matrix[local_indices, candidate_index]
                        )
                    )
                    cycle_speed[seed] = float(
                        np.median(speed_matrix[local_indices, candidate_index])
                    )
                temporal_seed = np.asarray(
                    [cycle_temporal[seed] for seed in seed_ids],
                    dtype=np.float64,
                )
                speed_seed = np.asarray(
                    [cycle_speed[seed] for seed in seed_ids],
                    dtype=np.float64,
                )
                temporal_estimate = float(np.median(temporal_seed))
                speed_estimate = float(np.median(speed_seed))
                temporal_by_candidate.append(temporal_estimate)
                speed_by_candidate.append(speed_estimate)
                grid_rows.append(
                    {
                        "archive": archive,
                        "family": family,
                        "low_landmark": float(low),
                        "high_landmark": float(2 - low),
                        "pairs": int(len(selected)),
                        "seeds": int(len(seed_ids)),
                        "temporal_tension": temporal_estimate,
                        "speed_tension": speed_estimate,
                    }
                )
            temporal_by_candidate = np.asarray(
                temporal_by_candidate, dtype=np.float64
            )
            speed_by_candidate = np.asarray(
                speed_by_candidate, dtype=np.float64
            )
            phi_index = int(np.argmin(np.abs(all_candidates - PHI_LOW)))
            phi_temporal = float(temporal_by_candidate[phi_index])
            phi_speed = float(speed_by_candidate[phi_index])
            grid_mask = np.asarray(
                [np.any(np.isclose(low, GRID, atol=1e-12)) for low in all_candidates]
            )
            grid_temporal = temporal_by_candidate[grid_mask]
            grid_lows = all_candidates[grid_mask]
            fraction_grid_worse = float(np.mean(grid_temporal >= phi_temporal))
            best_index = int(np.argmin(grid_temporal))
            reference_output = {}
            for name, low in REFERENCES.items():
                index = int(np.argmin(np.abs(all_candidates - low)))
                reference_output[name] = {
                    "low_landmark": float(all_candidates[index]),
                    "temporal_tension": float(temporal_by_candidate[index]),
                    "speed_tension": float(speed_by_candidate[index]),
                }
            phi_seed_temporal = []
            phi_seed_speed = []
            for seed in seed_ids:
                local_indices = np.asarray(
                    [
                        local_by_global[int(index)]
                        for index in by_seed[seed]
                    ],
                    dtype=np.int64,
                )
                phi_seed_temporal.append(
                    float(np.median(temporal_matrix[local_indices, phi_index]))
                )
                phi_seed_speed.append(
                    float(np.median(speed_matrix[local_indices, phi_index]))
                )
            phi_bootstrap = bootstrap_seed_median(
                np.asarray(phi_seed_temporal), salt
            )
            salt += 1
            summary[archive][family] = {
                "common_support_pairs": int(len(selected)),
                "seeds": int(len(seed_ids)),
                "exact_phi": {
                    "low_landmark": PHI_LOW,
                    "high_landmark": PHI,
                    "temporal_tension": phi_temporal,
                    "speed_tension": phi_speed,
                    "temporal_bootstrap": phi_bootstrap,
                },
                "fraction_grid_with_equal_or_higher_temporal_tension": (
                    fraction_grid_worse
                ),
                "phi_passes_90_percent_gate": bool(
                    fraction_grid_worse >= 0.90
                ),
                "best_grid": {
                    "low_landmark": float(grid_lows[best_index]),
                    "high_landmark": float(2 - grid_lows[best_index]),
                    "temporal_tension": float(grid_temporal[best_index]),
                },
                "references": reference_output,
                "phi_seed_speed": finite_summary(phi_seed_speed),
            }
    return grid_rows, summary


def write_gzip_csv(path: pathlib.Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"No rows for {path.name}")
    with gzip.open(path, "wt", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_csv(path: pathlib.Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"No rows for {path.name}")
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def style_axis(axis) -> None:
    axis.set_facecolor(BG)
    axis.grid(color=GRID_COLOR, linewidth=0.7, alpha=0.72)
    axis.tick_params(colors=MID, labelsize=9)
    axis.title.set_color(INK)
    axis.xaxis.label.set_color(INK)
    axis.yaxis.label.set_color(INK)
    for spine in axis.spines.values():
        spine.set_color("#8995A3")


def make_figure(
    rows: list[dict],
    progress: np.ndarray,
    residual: np.ndarray,
    child_summary: dict,
    corrected_summary: dict,
    grid_rows: list[dict],
    phi_summary: dict,
) -> None:
    figure, axes = plt.subplots(2, 2, figsize=(14.5, 10.5))
    figure.patch.set_facecolor(BG)
    figure.suptitle(
        "Q43 — projected child ridge and directional Phi handover",
        fontsize=19,
        fontweight="bold",
        color=INK,
        y=0.982,
    )
    figure.text(
        0.5,
        0.949,
        (
            "Q42 scalar strands · two independent revealed archives · "
            "frozen descriptive definitions"
        ),
        ha="center",
        color=MID,
        fontsize=10.5,
    )

    axis = axes[0, 0]
    positions = [0, 1, 3, 4]
    labels = ["greedy\nraw", "greedy\ncorrected", "landmax\nraw", "landmax\ncorrected"]
    colors = [BLUE, BLUE, GOLD, GOLD]
    summaries = [
        child_summary["greedy"]["two_turn_7_5"],
        corrected_summary["greedy"]["two_turn_7_5"],
        child_summary["landmax"]["two_turn_7_5"],
        corrected_summary["landmax"]["two_turn_7_5"],
    ]
    for position, color, item in zip(positions, colors, summaries):
        estimate = item["estimate"]
        low, high = item["ci95"]
        filled = "corrected" not in labels[positions.index(position)]
        axis.errorbar(
            position,
            estimate,
            yerr=[[estimate - low], [high - estimate]],
            fmt="o" if filled else "D",
            color=color,
            markerfacecolor=color if filled else BG,
            markeredgecolor=color,
            markersize=8,
            capsize=4,
            linewidth=1.7,
        )
        axis.text(position, high + 0.012, f"{estimate:.3f}", ha="center", color=INK)
    axis.axhspan(0.45, 0.55, color=LIGHT, alpha=0.75, label="frozen ±0.05 band")
    axis.axhline(0.5, color=INK, linewidth=1.1, linestyle="--", label="child ridge 0.5")
    axis.set_xticks(positions, labels)
    axis.set(
        title="Two-turn residual at matched half-progress",
        ylabel="parent-view residual coordinate",
    )
    axis.legend(frameon=False, fontsize=8)
    style_axis(axis)

    axis = axes[0, 1]
    for archive, color in (("greedy", BLUE), ("landmax", GOLD)):
        selected = np.asarray(
            [
                index
                for index, row in enumerate(rows)
                if row["archive"] == archive
                and row["family"] == "two_turn_7_5"
            ],
            dtype=np.int64,
        )
        median = np.median(residual[selected], axis=0)
        lo = np.quantile(residual[selected], 0.25, axis=0)
        hi = np.quantile(residual[selected], 0.75, axis=0)
        axis.fill_between(progress, lo, hi, color=color, alpha=0.15)
        axis.plot(progress, median, color=color, linewidth=2.1, label=archive)
    axis.axhline(0.5, color=INK, linewidth=1.1, linestyle="--")
    axis.axvline(0.5, color=MID, linewidth=0.9, linestyle=":")
    axis.set(
        title="Exposed residual across the two-turn half-wave",
        xlabel="matched within-half-wave progress",
        ylabel="forward + return − 2",
    )
    axis.legend(frameon=False)
    style_axis(axis)

    axis = axes[1, 0]
    for archive, color in (("greedy", BLUE), ("landmax", GOLD)):
        selected = [
            row
            for row in grid_rows
            if row["archive"] == archive
            and row["family"] == "two_turn_7_5"
            and np.any(np.isclose(row["low_landmark"], GRID, atol=1e-12))
        ]
        selected.sort(key=lambda row: row["low_landmark"])
        axis.plot(
            [row["low_landmark"] for row in selected],
            [row["temporal_tension"] for row in selected],
            color=color,
            linewidth=2,
            label=archive,
        )
        phi_item = phi_summary[archive]["two_turn_7_5"]["exact_phi"]
        axis.scatter(
            [PHI_LOW],
            [phi_item["temporal_tension"]],
            color=color,
            edgecolor=INK,
            linewidth=0.7,
            s=62,
            zorder=5,
        )
    axis.axvline(PHI_LOW, color=ORANGE, linewidth=1.2, linestyle="--")
    axis.text(
        PHI_LOW + 0.004,
        axis.get_ylim()[1] if axis.get_ylim()[1] > 0 else 0,
        "2−φ",
        color=ORANGE,
        va="top",
        fontsize=9,
    )
    axis.set(
        title="Directional passage tension across symmetric landmark pairs",
        xlabel="low landmark a (paired with 2−a)",
        ylabel="median seed-balanced Hₜ (lower is smoother)",
    )
    axis.legend(frameon=False)
    style_axis(axis)

    axis = axes[1, 1]
    archives = ["greedy", "landmax"]
    ranks = [
        phi_summary[archive]["two_turn_7_5"][
            "fraction_grid_with_equal_or_higher_temporal_tension"
        ]
        for archive in archives
    ]
    bars = axis.bar(
        archives,
        ranks,
        color=[BLUE, GOLD],
        edgecolor=INK,
        linewidth=0.7,
        alpha=0.78,
    )
    axis.axhline(0.90, color=ORANGE, linewidth=1.2, linestyle="--", label="frozen 90% gate")
    axis.set(
        title="Exact Phi rank against the fixed symmetric grid",
        ylabel="fraction of grid with equal/higher tension",
        ylim=(0, 1.05),
    )
    for bar, rank in zip(bars, ranks):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            rank + 0.025,
            f"{rank:.1%}",
            ha="center",
            color=INK,
            fontweight="bold",
        )
    axis.legend(frameon=False, fontsize=8)
    style_axis(axis)

    figure.text(
        0.02,
        0.012,
        (
            "Source: Zenodo 10.5281/zenodo.16753415 · Q43 uses already-revealed "
            "Q40/Q41B archives; results are descriptive, not prospective."
        ),
        fontsize=8.8,
        color=MID,
    )
    figure.tight_layout(rect=(0.02, 0.04, 0.985, 0.925))
    figure.savefig(FIGURE_PNG, dpi=180, facecolor=figure.get_facecolor())
    figure.savefig(FIGURE_SVG, facecolor=figure.get_facecolor())
    plt.close(figure)


def main() -> None:
    if not PROTOCOL.exists():
        raise RuntimeError(f"Missing frozen protocol: {PROTOCOL}")
    protocol_sha = digest(PROTOCOL)
    rows, progress, forward, returning, residual = read_q42()
    tau_mid = residual[:, MID_INDEX]

    child_summary = {}
    salt = 0
    for archive in q42.DATASETS:
        child_summary[archive] = {}
        for family in ("two_turn_7_5", "one_turn_15"):
            child_summary[archive][family] = seed_balanced_cycle_summary(
                rows, tau_mid, archive, family, salt
            )
            salt += 1

    observed = observed_lineage_medians(rows, tau_mid)
    controls = sampling_control(observed)
    corrected_summary = {}
    matched_components = {}
    for archive in q42.DATASETS:
        corrected_summary[archive] = {}
        matched_components[archive] = {}
        for family in ("two_turn_7_5", "one_turn_15"):
            corrected_summary[archive][family] = corrected_seed_summary(
                controls, archive, family, salt
            )
            matched_components[archive][family] = matched_control_components(
                controls, archive, family
            )
            salt += 1

    grid_rows, phi_summary = phi_grid_analysis(
        rows, progress, forward, returning
    )
    write_gzip_csv(CONTROL_ROWS, controls)
    write_csv(GRID_ROWS, grid_rows)

    raw_support = all(
        child_summary[archive]["two_turn_7_5"].get(
            "equivalent_to_0_5", False
        )
        for archive in q42.DATASETS
    )
    corrected_support = all(
        corrected_summary[archive]["two_turn_7_5"].get(
            "equivalent_to_0_5", False
        )
        for archive in q42.DATASETS
    )
    phi_support = all(
        phi_summary[archive]["two_turn_7_5"][
            "phi_passes_90_percent_gate"
        ]
        for archive in q42.DATASETS
    )
    output = {
        "test_id": TEST_ID,
        "date": "2026-07-28",
        "status": "FROZEN DESCRIPTIVE CROSS-ARCHIVE TEST",
        "protocol_sha256": protocol_sha,
        "source_hashes": {
            "q42_rows_sha256": digest(Q42_ROWS),
            "q42_profiles_sha256": digest(Q42_PROFILES),
        },
        "definitions": {
            "projected_child_ridge": CHILD_RIDGE,
            "equivalence_band": list(EQUIVALENCE_BAND),
            "tau_mid": "forward(p=0.5)+return(p=0.5)-2",
            "sampling_corrected_tau": "observed_tau-symmetric_sampling_tau",
            "phi": PHI,
            "phi_low": PHI_LOW,
            "temporal_tension": (
                "0.5*(|pf(2-a)-pr(a)|+|pf(a)-pr(2-a)|)"
            ),
            "common_support": (
                "both independently observed paths span x=0.20 through 1.80"
            ),
            "phi_gate": (
                "exact Phi lower temporal tension than at least 90% of "
                "fixed grid in two-turn family, independently in both archives"
            ),
        },
        "inventory": {
            "q42_pairs": len(rows),
            "sampling_control_lineages": len(controls),
            "grid_rows": len(grid_rows),
        },
        "child_ridge": {
            "raw": child_summary,
            "sampling_corrected": corrected_summary,
            "sampling_matched_components": matched_components,
            "raw_two_archive_support": raw_support,
            "corrected_two_archive_support": corrected_support,
        },
        "phi_handover": {
            "archives": phi_summary,
            "two_archive_primary_support": phi_support,
        },
        "artifacts": {
            "sampling_control_rows": str(CONTROL_ROWS),
            "phi_grid_rows": str(GRID_ROWS),
            "figure_png": str(FIGURE_PNG),
            "figure_svg": str(FIGURE_SVG),
        },
        "claim_boundary": (
            "Q43 uses already-revealed simulator archives. It tests one frozen "
            "child-ridge projection and one frozen temporal-handover definition; "
            "it does not establish a physical hidden child or universal Phi law."
        ),
    }
    RESULTS.write_text(
        json.dumps(output, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    make_figure(
        rows,
        progress,
        residual,
        child_summary,
        corrected_summary,
        grid_rows,
        phi_summary,
    )
    print(
        json.dumps(
            {
                "raw_child_ridge": {
                    archive: child_summary[archive]["two_turn_7_5"]
                    for archive in q42.DATASETS
                },
                "corrected_child_ridge": {
                    archive: corrected_summary[archive]["two_turn_7_5"]
                    for archive in q42.DATASETS
                },
                "phi_handover": {
                    archive: phi_summary[archive]["two_turn_7_5"]
                    for archive in q42.DATASETS
                },
                "gates": {
                    "raw_child": raw_support,
                    "corrected_child": corrected_support,
                    "phi": phi_support,
                },
            },
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
