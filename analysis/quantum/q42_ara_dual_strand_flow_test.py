"""Q42 frozen descriptive test of ARA dual-strand closure and matrix flow.

The scalar forward and return paths are measured independently from the
connected-closure trajectory.  The matrix calculation then projects the
actual fourth movement onto the visible relation axis and retains the
orthogonal remainder as Other.
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
from q40c_post_result_double_helix_projection_audit import fit_orbit


TEST_ID = "Q42-ARA-DUAL-STRAND-FLOW-v1"
PROTOCOL = HERE / "Q42_ARA_DUAL_STRAND_FLOW_PROTOCOL_v1_FROZEN.md"
RESULTS = HERE / "Q42_ARA_DUAL_STRAND_FLOW_RESULTS.json"
STRANDS = HERE / "Q42_ARA_DUAL_STRAND_FLOW_STRANDS.csv.gz"
MATRICES = HERE / "Q42_ARA_DUAL_STRAND_FLOW_MATRICES.csv.gz"
PROFILES = HERE / "Q42_ARA_DUAL_STRAND_FLOW_PROFILES.npz"
FIGURE_PNG = HERE / "Q42_ARA_DUAL_STRAND_FLOW_DIAGNOSTICS.png"
FIGURE_SVG = HERE / "Q42_ARA_DUAL_STRAND_FLOW_DIAGNOSTICS.svg"

DATASETS = {
    "greedy": {
        "derived": (
            HERE
            / "public_data"
            / "q40_return_flow_inhomo_v1_greedy"
            / "q40_derived_cache.npz"
        ),
        "connected": (
            HERE
            / "public_data"
            / "q40_return_flow_inhomo_v1_greedy"
            / "q40_connected_cache.npy"
        ),
    },
    "landmax": {
        "derived": (
            HERE
            / "public_data"
            / "q41b_cadence_strand_inhomo_v1_landmax"
            / "q41b_derived_cache.npz"
        ),
        "connected": (
            HERE
            / "public_data"
            / "q41b_cadence_strand_inhomo_v1_landmax"
            / "q41b_connected_cache.npy"
        ),
    },
}

PROGRESS = np.linspace(0.0, 1.0, 33)
EPS = 1e-12
BOOTSTRAP_SEED = 420028
BOOTSTRAP_DRAWS = 20_000

BLUE = "#537DB8"
GOLD = "#D99B31"
ORANGE = "#D85C4A"
INK = "#17212B"
MID = "#647180"
LIGHT = "#DCE4EC"
GRID = "#D9E0E7"
BG = "#FAFBFC"


def digest(path: pathlib.Path, algorithm: str = "sha256") -> str:
    value = hashlib.new(algorithm)
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
        "std": float(np.std(data)),
        "p05": float(np.quantile(data, 0.05)),
        "p25": float(np.quantile(data, 0.25)),
        "median": float(np.median(data)),
        "p75": float(np.quantile(data, 0.75)),
        "p95": float(np.quantile(data, 0.95)),
        "min": float(np.min(data)),
        "max": float(np.max(data)),
    }


def average_ranks(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=np.float64)
    start = 0
    while start < len(values):
        end = start + 1
        while end < len(values) and values[order[end]] == values[order[start]]:
            end += 1
        ranks[order[start:end]] = (start + end - 1) / 2
        start = end
    return ranks


def spearman(first, second) -> float:
    first = np.asarray(first, dtype=np.float64)
    second = np.asarray(second, dtype=np.float64)
    finite = np.isfinite(first) & np.isfinite(second)
    if np.sum(finite) < 3:
        return float("nan")
    a = average_ranks(first[finite])
    b = average_ranks(second[finite])
    if np.std(a) <= EPS or np.std(b) <= EPS:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def cadence_family(u: np.ndarray, v: np.ndarray) -> tuple[str, dict]:
    fit = fit_orbit(u[250:499], v[250:499])
    if (
        7.35 <= fit["angular_period_samples"] <= 7.65
        and fit["fixed_lag_15"]["coordinate_correlation"] >= 0.95
    ):
        return "two_turn_7_5", fit
    if (
        14.8 <= fit["angular_period_samples"] <= 15.2
        and fit["fixed_lag_15"]["coordinate_correlation"] >= 0.95
    ):
        return "one_turn_15", fit
    return "other", fit


def fill_zero_signs(signs: np.ndarray) -> np.ndarray:
    signs = np.asarray(signs, dtype=np.int8).copy()
    previous = 0
    for index in range(len(signs)):
        if signs[index]:
            previous = int(signs[index])
        elif previous:
            signs[index] = previous
    following = 0
    for index in range(len(signs) - 1, -1, -1):
        if signs[index]:
            following = int(signs[index])
        elif following:
            signs[index] = following
    return signs


def transition_runs(line: np.ndarray, first: int = 250, last: int = 497):
    delta = np.diff(np.asarray(line, dtype=np.float64))
    signs = fill_zero_signs(np.sign(delta[first : last + 1]))
    output = []
    start = 0
    for index in range(1, len(signs) + 1):
        if index == len(signs) or signs[index] != signs[start]:
            output.append(
                {
                    "sign": int(signs[start]),
                    "start": int(first + start),
                    "end": int(first + index - 1),
                }
            )
            start = index
    return [item for item in output if item["sign"] != 0]


def run_positions(x: np.ndarray, run: dict) -> np.ndarray:
    return np.asarray(
        x[run["start"] : run["end"] + 2],
        dtype=np.float64,
    )


def qualifying_half(values: np.ndarray, run: dict) -> bool:
    transitions = run["end"] - run["start"] + 1
    return bool(
        transitions >= 3
        and np.min(values) <= 0.5
        and np.max(values) >= 1.5
    )


def resample_path(values: np.ndarray) -> np.ndarray:
    source = np.linspace(0.0, 1.0, len(values))
    return np.interp(PROGRESS, source, np.asarray(values, dtype=np.float64))


def extract_strand_pairs(
    archive: str,
    seed: int,
    pair: int,
    line: np.ndarray,
    family: str,
):
    development = np.asarray(line[:250], dtype=np.float64)
    lo, hi = np.quantile(development, [0.05, 0.95])
    if not np.isfinite(lo) or not np.isfinite(hi) or hi - lo <= EPS:
        return [], [], [], []
    x = 2 * (np.asarray(line, dtype=np.float64) - lo) / (hi - lo)
    runs = transition_runs(line)
    records = []
    forward_profiles = []
    return_profiles = []
    residual_profiles = []
    index = 0
    cycle = 0
    while index < len(runs) - 1:
        forward_run = runs[index]
        return_run = runs[index + 1]
        if forward_run["sign"] <= 0:
            index += 1
            continue
        if return_run["sign"] >= 0:
            index += 1
            continue
        forward_raw = run_positions(x, forward_run)
        return_raw = run_positions(x, return_run)
        if not (
            qualifying_half(forward_raw, forward_run)
            and qualifying_half(return_raw, return_run)
        ):
            index += 1
            continue
        forward = resample_path(forward_raw)
        returning = resample_path(return_raw)
        residual = forward + returning - 2
        wrong = forward + returning[::-1] - 2
        forward_duration = float(forward_run["end"] - forward_run["start"] + 1)
        return_duration = float(return_run["end"] - return_run["start"] + 1)
        forward_speed = float(
            (forward_raw[-1] - forward_raw[0]) / forward_duration
        )
        return_speed = float(
            (return_raw[0] - return_raw[-1]) / return_duration
        )
        duration_coordinate = float(
            2 * forward_duration / (forward_duration + return_duration)
        )
        speed_coordinate = float(
            2
            * forward_speed
            / (forward_speed + return_speed + EPS)
        )
        residual_flow = np.gradient(residual, PROGRESS)
        record = {
            "archive": archive,
            "seed": seed,
            "pair": pair,
            "family": family,
            "cycle": cycle,
            "forward_start": forward_run["start"],
            "forward_end": forward_run["end"] + 1,
            "return_start": return_run["start"],
            "return_end": return_run["end"] + 1,
            "forward_duration": forward_duration,
            "return_duration": return_duration,
            "forward_speed": forward_speed,
            "return_speed": return_speed,
            "duration_coordinate": duration_coordinate,
            "speed_coordinate": speed_coordinate,
            "closure_signed_mean": float(np.mean(residual)),
            "closure_mae": float(np.mean(np.abs(residual))),
            "closure_max_abs": float(np.max(np.abs(residual))),
            "wrong_orientation_mae": float(np.mean(np.abs(wrong))),
            "mixing_flow_rms": float(np.sqrt(np.mean(residual_flow**2))),
            "forward_min": float(np.min(forward_raw)),
            "forward_max": float(np.max(forward_raw)),
            "forward_first": float(forward_raw[0]),
            "forward_last": float(forward_raw[-1]),
            "return_min": float(np.min(return_raw)),
            "return_max": float(np.max(return_raw)),
            "return_first": float(return_raw[0]),
            "return_last": float(return_raw[-1]),
        }
        records.append(record)
        forward_profiles.append(forward)
        return_profiles.append(returning)
        residual_profiles.append(residual)
        cycle += 1
        index += 2
    return records, forward_profiles, return_profiles, residual_profiles


def extract_matrix_cycles(
    archive: str,
    seed: int,
    pair: int,
    closure_line: np.ndarray,
    connected: np.ndarray,
    coordinate,
    family: str,
):
    u, _v, labels, direction, _coherence, _occupancy = coordinate
    development = np.asarray(closure_line[:250], dtype=np.float64)
    lo, hi = np.quantile(development, [0.05, 0.95])
    x = 2 * (np.asarray(closure_line, dtype=np.float64) - lo) / (hi - lo)
    lineage_scale = float(
        np.median(np.linalg.norm(connected[seed, :250, pair], axis=(1, 2)))
    )
    records = []
    windows = base.complete_windows(labels, direction, 250, 498)
    for cycle, window in enumerate(windows):
        c1, c2, c3, c4 = base.identities_for_window(
            connected, seed, pair, window
        )
        relation = c1 - c2
        movement = c4 - c3
        relation_sq = float(np.sum(relation * relation))
        relation_norm = math.sqrt(max(relation_sq, 0.0))
        movement_norm = float(np.linalg.norm(movement))
        if relation_sq <= EPS:
            alpha = float("nan")
            matrix_x = float("nan")
            residual_norm = float("nan")
            along_sq = float("nan")
            residual_sq = float("nan")
            along_teara = float("nan")
            other_teara = float("nan")
            orthogonality = float("nan")
        else:
            alpha = float(np.sum(movement * relation) / relation_sq)
            matrix_x = 1 - alpha
            residual = movement - alpha * relation
            residual_sq = float(np.sum(residual * residual))
            residual_norm = math.sqrt(max(residual_sq, 0.0))
            along_sq = float(alpha * alpha * relation_sq)
            total_participation = along_sq + residual_sq
            along_teara = float(2 * along_sq / (total_participation + EPS))
            other_teara = float(2 - along_teara)
            orthogonality = float(
                abs(np.sum(residual * relation))
                / (residual_norm * relation_norm + EPS)
            )
        q4, q4_start, q4_end = window[3]
        q4_start = int(q4_start)
        q4_end = int(q4_end)
        scalar_q4 = float(np.mean(x[q4_start : q4_end + 1]))
        midpoint = float((q4_start + q4_end) / 2)
        stable = bool(relation_norm >= 0.10 * lineage_scale)
        records.append(
            {
                "archive": archive,
                "seed": seed,
                "pair": pair,
                "family": family,
                "cycle": cycle,
                "q4": int(q4),
                "q4_start": q4_start,
                "q4_end": q4_end,
                "midpoint": midpoint,
                "lineage_scale": lineage_scale,
                "relation_norm": relation_norm,
                "movement_norm": movement_norm,
                "relation_to_lineage_scale": float(
                    relation_norm / (lineage_scale + EPS)
                ),
                "stable": int(stable),
                "alpha": alpha,
                "matrix_x": matrix_x,
                "scalar_q4_x": scalar_q4,
                "along_teara": along_teara,
                "other_teara": other_teara,
                "residual_norm": residual_norm,
                "orthogonality_error": orthogonality,
                "target_negative": int(alpha < 0) if np.isfinite(alpha) else -1,
                "near_forward": (
                    int(abs(matrix_x - 0) <= 0.25)
                    if np.isfinite(matrix_x)
                    else -1
                ),
                "near_ridge": (
                    int(abs(matrix_x - 1) <= 0.25)
                    if np.isfinite(matrix_x)
                    else -1
                ),
                "near_reverse": (
                    int(abs(matrix_x - 2) <= 0.25)
                    if np.isfinite(matrix_x)
                    else -1
                ),
                "matrix_flow_per_sample": float("nan"),
            }
        )
    return records


def add_matrix_flow(rows: list[dict]) -> None:
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["archive"], row["seed"], row["pair"])].append(row)
    for values in grouped.values():
        values.sort(key=lambda row: row["midpoint"])
        for prior, current in zip(values[:-1], values[1:]):
            delta_t = current["midpoint"] - prior["midpoint"]
            if (
                delta_t > 0
                and np.isfinite(prior["matrix_x"])
                and np.isfinite(current["matrix_x"])
            ):
                current["matrix_flow_per_sample"] = float(
                    (current["matrix_x"] - prior["matrix_x"]) / delta_t
                )


def write_csv(path: pathlib.Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"No rows for {path.name}")
    with gzip.open(path, "wt", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def cluster_bootstrap_difference(rows: list[dict], first: str, second: str):
    by_seed = defaultdict(list)
    for row in rows:
        if np.isfinite(row[first]) and np.isfinite(row[second]):
            by_seed[(row["archive"], row["seed"])].append(
                float(row[first] - row[second])
            )
    seed_values = np.asarray(
        [np.mean(values) for values in by_seed.values()],
        dtype=np.float64,
    )
    if not len(seed_values):
        return {"clusters": 0}
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    estimates = np.empty(BOOTSTRAP_DRAWS, dtype=np.float64)
    for index in range(BOOTSTRAP_DRAWS):
        sample = rng.choice(seed_values, size=len(seed_values), replace=True)
        estimates[index] = np.mean(sample)
    return {
        "clusters": int(len(seed_values)),
        "mean_difference": float(np.mean(seed_values)),
        "ci95": [
            float(np.quantile(estimates, 0.025)),
            float(np.quantile(estimates, 0.975)),
        ],
        "fraction_bootstrap_above_zero": float(np.mean(estimates > 0)),
    }


def scalar_summary(rows: list[dict]) -> dict:
    output = {}
    for archive in DATASETS:
        selected = [row for row in rows if row["archive"] == archive]
        output[archive] = {
            "pairs": len(selected),
            "closure_mae": finite_summary(row["closure_mae"] for row in selected),
            "closure_signed_mean": finite_summary(
                row["closure_signed_mean"] for row in selected
            ),
            "closure_max_abs": finite_summary(
                row["closure_max_abs"] for row in selected
            ),
            "wrong_orientation_mae": finite_summary(
                row["wrong_orientation_mae"] for row in selected
            ),
            "duration_coordinate": finite_summary(
                row["duration_coordinate"] for row in selected
            ),
            "speed_coordinate": finite_summary(
                row["speed_coordinate"] for row in selected
            ),
            "mixing_flow_rms": finite_summary(
                row["mixing_flow_rms"] for row in selected
            ),
        }
        output[archive]["families"] = {}
        for family in ("two_turn_7_5", "one_turn_15", "other"):
            family_rows = [
                row for row in selected if row["family"] == family
            ]
            output[archive]["families"][family] = {
                "pairs": len(family_rows),
                "closure_mae": finite_summary(
                    row["closure_mae"] for row in family_rows
                ),
                "signed_residual": finite_summary(
                    row["closure_signed_mean"] for row in family_rows
                ),
                "duration_coordinate": finite_summary(
                    row["duration_coordinate"] for row in family_rows
                ),
                "speed_coordinate": finite_summary(
                    row["speed_coordinate"] for row in family_rows
                ),
            }
    output["orientation_control"] = cluster_bootstrap_difference(
        rows,
        "wrong_orientation_mae",
        "closure_mae",
    )
    return output


def matrix_group(rows: list[dict]) -> dict:
    stable = [row for row in rows if row["stable"] and np.isfinite(row["matrix_x"])]
    if not stable:
        return {"cycles": 0}
    return {
        "cycles": len(stable),
        "matrix_x": finite_summary(row["matrix_x"] for row in stable),
        "alpha": finite_summary(row["alpha"] for row in stable),
        "scalar_q4_x": finite_summary(row["scalar_q4_x"] for row in stable),
        "along_teara": finite_summary(row["along_teara"] for row in stable),
        "other_teara": finite_summary(row["other_teara"] for row in stable),
        "matrix_flow_per_sample": finite_summary(
            row["matrix_flow_per_sample"] for row in stable
        ),
        "negative_fraction": float(
            np.mean([row["target_negative"] for row in stable])
        ),
        "near_forward_fraction": float(
            np.mean([row["near_forward"] for row in stable])
        ),
        "near_ridge_fraction": float(
            np.mean([row["near_ridge"] for row in stable])
        ),
        "near_reverse_fraction": float(
            np.mean([row["near_reverse"] for row in stable])
        ),
        "scalar_matrix_spearman": spearman(
            [row["scalar_q4_x"] for row in stable],
            [row["matrix_x"] for row in stable],
        ),
        "orthogonality_error": finite_summary(
            row["orthogonality_error"] for row in stable
        ),
    }


def matrix_summary(rows: list[dict]) -> dict:
    output = {}
    for archive in DATASETS:
        selected = [row for row in rows if row["archive"] == archive]
        stable = [row for row in selected if row["stable"]]
        item = matrix_group(selected)
        item["all_cycles"] = len(selected)
        item["stable_cycles"] = len(stable)
        item["stable_fraction"] = len(stable) / max(len(selected), 1)
        item["families"] = {}
        for family in ("two_turn_7_5", "one_turn_15", "other"):
            family_rows = [
                row for row in selected if row["family"] == family
            ]
            family_item = matrix_group(family_rows)
            family_item["quadrants"] = {}
            for q4 in range(4):
                family_item["quadrants"][str(q4)] = matrix_group(
                    [row for row in family_rows if row["q4"] == q4]
                )
            item["families"][family] = family_item
        output[archive] = item
    output["combined"] = matrix_group(rows)
    return output


def profile_band(values: np.ndarray):
    return (
        np.quantile(values, 0.25, axis=0),
        np.median(values, axis=0),
        np.quantile(values, 0.75, axis=0),
    )


def style_axis(axis):
    axis.set_facecolor(BG)
    axis.grid(color=GRID, linewidth=0.7, alpha=0.72)
    axis.tick_params(colors=MID, labelsize=9)
    for spine in axis.spines.values():
        spine.set_color("#8995A3")
    axis.title.set_color(INK)
    axis.xaxis.label.set_color(INK)
    axis.yaxis.label.set_color(INK)


def make_figure(
    strand_rows: list[dict],
    matrix_rows: list[dict],
    forward_profiles: np.ndarray,
    return_profiles: np.ndarray,
    residual_profiles: np.ndarray,
):
    figure, axes = plt.subplots(2, 3, figsize=(17, 10.5))
    figure.patch.set_facecolor(BG)
    figure.suptitle(
        "Q42 — independently measured ARA strand flow and mixing",
        fontsize=20,
        fontweight="bold",
        color=INK,
        y=0.985,
    )
    figure.text(
        0.5,
        0.952,
        (
            f"{len(strand_rows):,} scalar half-wave pairs · "
            f"{len(matrix_rows):,} four-quadrant matrix cycles · "
            "greedy + landmax public simulator archives"
        ),
        ha="center",
        color=MID,
        fontsize=11,
    )

    axis = axes[0, 0]
    f_lo, f_med, f_hi = profile_band(forward_profiles)
    r_lo, r_med, r_hi = profile_band(return_profiles)
    axis.fill_between(PROGRESS, f_lo, f_hi, color=BLUE, alpha=0.18)
    axis.plot(PROGRESS, f_med, color=BLUE, linewidth=2.2, label="forward")
    axis.fill_between(PROGRESS, r_lo, r_hi, color=GOLD, alpha=0.20)
    axis.plot(PROGRESS, r_med, color=GOLD, linewidth=2.2, label="return")
    for level, label in ((0, "0"), (1, "ridge 1"), (2, "2")):
        axis.axhline(level, color=INK if level == 1 else MID, linewidth=0.8)
        axis.text(1.01, level, label, va="center", fontsize=8, color=MID)
    axis.set(
        title="Forward and return paths on the ARA diameter",
        xlabel="within-half-wave progress",
        ylabel="ARA coordinate x",
    )
    axis.legend(frameon=False, loc="center right")
    style_axis(axis)

    axis = axes[0, 1]
    e_lo, e_med, e_hi = profile_band(residual_profiles)
    axis.fill_between(PROGRESS, e_lo, e_hi, color=ORANGE, alpha=0.18)
    axis.plot(PROGRESS, e_med, color=ORANGE, linewidth=2.2)
    axis.axhline(0, color=INK, linewidth=1)
    axis.set(
        title="Independent closure residual",
        xlabel="within-half-wave progress",
        ylabel="forward + return − 2",
    )
    style_axis(axis)

    axis = axes[0, 2]
    forward_speed = np.gradient(forward_profiles, PROGRESS, axis=1)
    return_speed = -np.gradient(return_profiles, PROGRESS, axis=1)
    fs_lo, fs_med, fs_hi = profile_band(forward_speed)
    rs_lo, rs_med, rs_hi = profile_band(return_speed)
    axis.fill_between(PROGRESS, fs_lo, fs_hi, color=BLUE, alpha=0.18)
    axis.plot(PROGRESS, fs_med, color=BLUE, linewidth=2, label="forward")
    axis.fill_between(PROGRESS, rs_lo, rs_hi, color=GOLD, alpha=0.20)
    axis.plot(PROGRESS, rs_med, color=GOLD, linewidth=2, label="return")
    axis.axhline(0, color=INK, linewidth=0.8)
    axis.set(
        title="Traversal shape before sample-time scaling",
        xlabel="within-half-wave progress",
        ylabel="dx / d(progress)",
    )
    axis.legend(frameon=False)
    style_axis(axis)

    stable = [
        row
        for row in matrix_rows
        if row["stable"] and np.isfinite(row["matrix_x"])
    ]
    labels = []
    groups = []
    colors = []
    for archive, color in (("greedy", BLUE), ("landmax", GOLD)):
        selected_archive = [row for row in stable if row["archive"] == archive]
        definitions = (
            (
                "2-turn Ba",
                [
                    row
                    for row in selected_archive
                    if row["family"] == "two_turn_7_5" and row["q4"] == 1
                ],
            ),
            (
                "2-turn other",
                [
                    row
                    for row in selected_archive
                    if row["family"] == "two_turn_7_5" and row["q4"] != 1
                ],
            ),
            (
                "1-turn",
                [
                    row
                    for row in selected_archive
                    if row["family"] == "one_turn_15"
                ],
            ),
        )
        for name, selected in definitions:
            labels.append(f"{archive}\n{name}")
            groups.append([row["matrix_x"] for row in selected])
            colors.append(color)
    axis = axes[1, 0]
    boxes = axis.boxplot(
        groups,
        patch_artist=True,
        showfliers=False,
        widths=0.62,
        medianprops={"color": INK, "linewidth": 1.5},
        whiskerprops={"color": MID},
        capprops={"color": MID},
    )
    for patch, color in zip(boxes["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.38)
        patch.set_edgecolor(color)
    axis.axhline(0, color=MID, linewidth=0.8)
    axis.axhline(1, color=INK, linewidth=1, linestyle="--")
    axis.axhline(2, color=MID, linewidth=0.8)
    axis.set_xticklabels(labels, rotation=18, ha="right")
    axis.set(
        title="Actual fourth movement on the frozen 0–2 relation axis",
        ylabel="matrix ARA coordinate (1 − α)",
    )
    style_axis(axis)

    axis = axes[1, 1]
    sample = stable
    if len(sample) > 20_000:
        rng = np.random.default_rng(420028)
        sample = list(rng.choice(sample, size=20_000, replace=False))
    for archive, color, marker in (
        ("greedy", BLUE, "o"),
        ("landmax", GOLD, "^"),
    ):
        values = [row for row in sample if row["archive"] == archive]
        axis.scatter(
            [row["scalar_q4_x"] for row in values],
            [row["matrix_x"] for row in values],
            s=8,
            alpha=0.18,
            color=color,
            marker=marker,
            linewidths=0,
            label=archive,
        )
    axis.axhline(1, color=INK, linewidth=0.9, linestyle="--")
    axis.axvline(1, color=INK, linewidth=0.9, linestyle="--")
    axis.set(
        title="Scalar state versus matrix relation movement",
        xlabel="scalar ARA coordinate during fourth visit",
        ylabel="matrix ARA coordinate",
    )
    axis.legend(frameon=False)
    axis.set_xlim(-0.5, 2.5)
    matrix_limits = np.quantile(
        np.asarray([row["matrix_x"] for row in stable]), [0.01, 0.99]
    )
    axis.set_ylim(matrix_limits[0], matrix_limits[1])
    style_axis(axis)

    axis = axes[1, 2]
    bar_labels = []
    along = []
    other = []
    bar_colors = []
    for archive, color in (("greedy", BLUE), ("landmax", GOLD)):
        archive_rows = [row for row in stable if row["archive"] == archive]
        definitions = (
            (
                "2-turn Ba",
                [
                    row
                    for row in archive_rows
                    if row["family"] == "two_turn_7_5" and row["q4"] == 1
                ],
            ),
            (
                "all stable",
                archive_rows,
            ),
        )
        for name, values in definitions:
            bar_labels.append(f"{archive}\n{name}")
            along.append(float(np.median([row["along_teara"] for row in values])))
            other.append(float(np.median([row["other_teara"] for row in values])))
            bar_colors.append(color)
    positions = np.arange(len(bar_labels))
    axis.bar(
        positions,
        along,
        color=bar_colors,
        alpha=0.72,
        edgecolor=INK,
        linewidth=0.6,
        label="along visible relation",
    )
    axis.bar(
        positions,
        other,
        bottom=along,
        color=LIGHT,
        edgecolor=INK,
        linewidth=0.6,
        hatch="//",
        label="perpendicular Other",
    )
    axis.axhline(2, color=INK, linewidth=0.9)
    axis.set_xticks(positions, bar_labels, rotation=18, ha="right")
    axis.set(
        title="Descriptive TE-ARA participation",
        ylabel="normalized participation (total = 2)",
        ylim=(0, 2.08),
    )
    axis.legend(frameon=False, fontsize=8)
    style_axis(axis)

    figure.text(
        0.02,
        0.012,
        (
            "Source: Zenodo 10.5281/zenodo.16753415 · Q42 is frozen before "
            "calculation but descriptive because both archives were previously revealed."
        ),
        fontsize=9,
        color=MID,
    )
    figure.tight_layout(rect=(0.02, 0.04, 0.985, 0.935))
    figure.savefig(FIGURE_PNG, dpi=180, facecolor=figure.get_facecolor())
    figure.savefig(FIGURE_SVG, facecolor=figure.get_facecolor())
    plt.close(figure)


def main() -> None:
    if not PROTOCOL.exists():
        raise RuntimeError(f"Missing frozen protocol: {PROTOCOL}")
    protocol_sha = digest(PROTOCOL)
    strand_rows = []
    matrix_rows = []
    forward_profiles = []
    return_profiles = []
    residual_profiles = []
    inventory = {}

    for archive, paths in DATASETS.items():
        if not paths["derived"].exists() or not paths["connected"].exists():
            raise RuntimeError(f"Missing Q42 source cache for {archive}")
        derived = np.load(paths["derived"])
        closure = np.asarray(derived["closure"], dtype=np.float32)
        connected = np.load(paths["connected"], mmap_mode="r")
        eligible = 0
        family_counts = defaultdict(int)
        for seed in range(closure.shape[0]):
            for pair in range(closure.shape[2]):
                coordinate = base.coordinates(closure[seed, :, pair])
                if coordinate is None:
                    continue
                u, v, _labels, _direction, coherence, occupancy = coordinate
                if coherence < 0.80 or occupancy < 0.05:
                    continue
                eligible += 1
                family, _fit = cadence_family(u, v)
                family_counts[family] += 1
                (
                    pair_rows,
                    pair_forward,
                    pair_return,
                    pair_residual,
                ) = extract_strand_pairs(
                    archive,
                    seed,
                    pair,
                    closure[seed, :, pair],
                    family,
                )
                strand_rows.extend(pair_rows)
                forward_profiles.extend(pair_forward)
                return_profiles.extend(pair_return)
                residual_profiles.extend(pair_residual)
                matrix_rows.extend(
                    extract_matrix_cycles(
                        archive,
                        seed,
                        pair,
                        closure[seed, :, pair],
                        connected,
                        coordinate,
                        family,
                    )
                )
        inventory[archive] = {
            "eligible_lineages": eligible,
            "family_lineages": dict(family_counts),
            "scalar_pairs": int(
                sum(row["archive"] == archive for row in strand_rows)
            ),
            "matrix_cycles": int(
                sum(row["archive"] == archive for row in matrix_rows)
            ),
        }

    if not strand_rows or not matrix_rows:
        raise RuntimeError("Q42 produced no analyzable rows")
    add_matrix_flow(matrix_rows)
    forward_array = np.asarray(forward_profiles, dtype=np.float64)
    return_array = np.asarray(return_profiles, dtype=np.float64)
    residual_array = np.asarray(residual_profiles, dtype=np.float64)

    write_csv(STRANDS, strand_rows)
    write_csv(MATRICES, matrix_rows)
    np.savez_compressed(
        PROFILES,
        progress=PROGRESS,
        forward=forward_array,
        returning=return_array,
        residual=residual_array,
    )

    scalar = scalar_summary(strand_rows)
    matrix = matrix_summary(matrix_rows)
    stable = [
        row
        for row in matrix_rows
        if row["stable"] and np.isfinite(row["matrix_x"])
    ]
    validation = {
        "max_interpolation_endpoint_error": float(
            max(
                max(
                    abs(forward_array[index, 0] - row["forward_first"]),
                    abs(forward_array[index, -1] - row["forward_last"]),
                    abs(return_array[index, 0] - row["return_first"]),
                    abs(return_array[index, -1] - row["return_last"]),
                )
                for index, row in enumerate(strand_rows)
            )
        ),
        "max_matrix_orthogonality_error": float(
            np.max([row["orthogonality_error"] for row in stable])
        ),
        "max_teara_sum_error": float(
            np.max(
                [
                    abs(row["along_teara"] + row["other_teara"] - 2)
                    for row in stable
                ]
            )
        ),
        "finite_scalar_rows": int(
            sum(
                np.isfinite(row["closure_mae"])
                and np.isfinite(row["wrong_orientation_mae"])
                for row in strand_rows
            )
        ),
        "finite_stable_matrix_rows": len(stable),
    }

    output = {
        "test_id": TEST_ID,
        "date": "2026-07-28",
        "status": "DESCRIPTIVE CROSS-ARCHIVE MEASUREMENT",
        "protocol_sha256": protocol_sha,
        "sources": {
            archive: {
                "derived": str(paths["derived"]),
                "connected": str(paths["connected"]),
            }
            for archive, paths in DATASETS.items()
        },
        "definitions": {
            "scalar_x": "2*(h-h05)/(h95-h05), development samples 0..249",
            "scalar_closure": "x_forward(p)+x_return(p)-2",
            "matrix_alpha": "<C4-C3,C1-C2>/<C1-C2,C1-C2>",
            "matrix_x": "1-alpha",
            "matrix_other": "2*||R||^2/(||alpha D||^2+||R||^2)",
            "stability": "||D|| >= 0.10 * development median matrix norm",
        },
        "inventory": inventory,
        "scalar_strands": scalar,
        "matrix_decomposition": matrix,
        "validation": validation,
        "artifacts": {
            "strand_rows": str(STRANDS),
            "matrix_rows": str(MATRICES),
            "profiles": str(PROFILES),
            "figure_png": str(FIGURE_PNG),
            "figure_svg": str(FIGURE_SVG),
        },
        "claim_boundary": (
            "Both source targets were previously revealed. Q42 measures a "
            "pre-calculation-frozen decomposition; predictive transfer requires "
            "a separately frozen operator on an untouched archive."
        ),
    }
    RESULTS.write_text(
        json.dumps(output, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    make_figure(
        strand_rows,
        matrix_rows,
        forward_array,
        return_array,
        residual_array,
    )
    print(json.dumps(output["inventory"], indent=2), flush=True)
    print(
        json.dumps(
            {
                "scalar": {
                    archive: {
                        "closure_mae_median": scalar[archive]["closure_mae"][
                            "median"
                        ],
                        "signed_residual_median": scalar[archive][
                            "closure_signed_mean"
                        ]["median"],
                        "duration_coordinate_median": scalar[archive][
                            "duration_coordinate"
                        ]["median"],
                        "speed_coordinate_median": scalar[archive][
                            "speed_coordinate"
                        ]["median"],
                    }
                    for archive in DATASETS
                },
                "orientation_control": scalar["orientation_control"],
                "matrix_two_turn_ba": {
                    archive: matrix[archive]["families"]["two_turn_7_5"][
                        "quadrants"
                    ]["1"]
                    for archive in DATASETS
                },
                "validation": validation,
            },
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
