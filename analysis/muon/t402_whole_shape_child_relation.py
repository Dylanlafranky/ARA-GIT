#!/usr/bin/env python3
"""T402: test the complete two-sided child relation seen after T401.

The frozen target is the whole C/AC shape on the unchanged T400 local child
coordinate.  The script measures raw flanking lobes, the C-minus-AC axis,
continuous topology, static reflected mean shape, cyclic alignment controls,
and bin/bandwidth sensitivity on fresh deterministic partitions.
"""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENDOR = HERE / "_vendor"
EXTRA = Path(r"F:\SystemFormulaFolder\.codex_python_packages")
for entry in (EXTRA, VENDOR):
    if entry.exists():
        sys.path.insert(0, str(entry))

os.environ.setdefault("MPLCONFIGDIR", str(HERE / "_mplconfig"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter1d

import t400_nested_child_window_population_to_event as t400


OUT = HERE / "T402_whole_shape_child_relation"
PROTOCOL = HERE / "T402_WHOLE_SHAPE_CHILD_RELATION_PROTOCOL_2026-08-17.md"
SEED_START = 600
N_SPLITS = 400
PRIMARY_BINS = 8
BIN_COUNTS = (6, 8, 10, 12)
BANDWIDTHS = (0.10, 0.15, 0.20, 0.25)
GRID = np.linspace(0.0, 2.0, 401)
GRID_DX = float(GRID[1] - GRID[0])
GRID_EDGES = np.concatenate(([GRID[0] - GRID_DX / 2], (GRID[:-1] + GRID[1:]) / 2, [GRID[-1] + GRID_DX / 2]))
N_BOOT = 5000


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"No rows for {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def effective_sample_size(weights: np.ndarray) -> float:
    total = float(np.sum(weights))
    squared = float(np.sum(np.square(weights)))
    return total * total / squared if squared > 0 else 0.0


def normalized_hist(x: np.ndarray, weights: np.ndarray, n_bins: int) -> np.ndarray:
    edges = np.linspace(0.0, 2.0, n_bins + 1)
    counts, _ = np.histogram(x, bins=edges, weights=weights)
    total = float(np.sum(counts))
    return counts / total if total > 0 else np.full(n_bins, np.nan)


def normalized_kde(x: np.ndarray, weights: np.ndarray, bandwidth: float) -> np.ndarray:
    counts, _ = np.histogram(x, bins=GRID_EDGES, weights=weights)
    density = gaussian_filter1d(counts.astype(float), sigma=bandwidth / GRID_DX, mode="nearest")
    area = float(np.trapezoid(density, GRID))
    return density / area if area > 0 else np.full(len(GRID), np.nan)


def fit_split(
    c_events: np.ndarray,
    ac_events: np.ndarray,
    static: tuple[list[np.ndarray], np.ndarray, np.ndarray, np.ndarray],
    salt: int,
) -> tuple[dict[str, object], dict[str, dict[str, np.ndarray | float]]] | None:
    base_templates, native_time, native_prompt, native_delayed = static
    c_mask = t400.event_split(c_events, "C", salt)
    ac_mask = t400.event_split(ac_events, "AC", salt)
    c_cal, c_hold = c_events[c_mask], c_events[~c_mask]
    ac_cal, ac_hold = ac_events[ac_mask], ac_events[~ac_mask]
    templates = list(base_templates)
    fit = t400.fit_calibration(t400.hist_time(c_cal), t400.hist_time(ac_cal), templates, t400.CAL_FRACTION)
    params = np.asarray(fit["params"], dtype=float)
    window = t400.child_window(native_time, native_prompt, native_delayed, float(params[3]), float(params[4]))
    if not bool(window.get("valid", False)):
        return None
    views = {
        "C": t400.event_membership(c_hold, params, templates, window, native_time, True),
        "AC": t400.event_membership(ac_hold, params, templates, window, native_time, False),
    }
    if any(len(np.asarray(view["local_x"])) == 0 or float(np.sum(np.asarray(view["weight"]))) <= 0 for view in views.values()):
        return None
    meta = {
        "salt": salt,
        "fit_success": bool(fit["success"]),
        "left_time_us": float(window["left_time_us"]),
        "crest_time_us": float(window["mode_time_us"]),
        "right_time_us": float(window["right_time_us"]),
        "population_local_crest": float(window["local_mode_ara"]),
        "population_local_mean": float(window["local_weighted_mean"]),
    }
    return meta, views


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.dot(a, b) / denominator) if denominator > 0 else float("nan")


def reflection_metrics(d: np.ndarray) -> dict[str, float]:
    half = len(d) // 2
    lower = np.asarray(d[:half], dtype=float)
    upper = np.asarray(d[half:], dtype=float)
    reflected = -upper[::-1]
    similarity = cosine(lower, reflected)
    denominator = float(np.linalg.norm(d))
    error = float(np.linalg.norm(lower + upper[::-1]) / denominator) if denominator > 0 else float("nan")
    return {"cosine": similarity, "normalized_error": error}


def bootstrap_interval(values: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    draws = rng.integers(0, len(values), size=(N_BOOT, len(values)))
    means = np.mean(values[draws], axis=1)
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def zero_crossings(x: np.ndarray, y: np.ndarray) -> list[float]:
    crossings: list[float] = []
    for i in range(len(y) - 1):
        if y[i] == 0:
            crossings.append(float(x[i]))
        elif y[i] * y[i + 1] < 0:
            crossings.append(float(x[i] - y[i] * (x[i + 1] - x[i]) / (y[i + 1] - y[i])))
    return crossings


def topology(density_difference: np.ndarray) -> dict[str, object]:
    positive_x = float(GRID[int(np.argmax(density_difference))])
    negative_x = float(GRID[int(np.argmin(density_difference))])
    crossings = zero_crossings(GRID, density_difference)
    near = float(min(crossings, key=lambda value: abs(value - 1.0))) if crossings else float("nan")
    return {
        "positive_crest_x": positive_x,
        "positive_crest_value": float(np.max(density_difference)),
        "negative_trough_x": negative_x,
        "negative_trough_value": float(np.min(density_difference)),
        "crossing_nearest_ridge_x": near,
        "crossing_count": len(crossings),
        "all_crossings": crossings,
        "passes_registered_windows": bool(
            0.40 <= positive_x <= 1.00
            and math.isfinite(near)
            and 0.85 <= near <= 1.30
            and 1.35 <= negative_x <= 2.00
        ),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    c_events = np.loadtxt(t400.DATA / "dataBeamOnC.txt")
    ac_events = np.loadtxt(t400.DATA / "dataBeamOnAC.txt")
    static = t400.build_templates()

    matrices: dict[int, dict[str, list[np.ndarray]]] = {
        n: {"C": [], "AC": []} for n in BIN_COUNTS
    }
    kde_matrices: dict[float, dict[str, list[np.ndarray]]] = {
        h: {"C": [], "AC": []} for h in BANDWIDTHS
    }
    split_rows: list[dict[str, object]] = []
    invalid_rows: list[dict[str, object]] = []
    primary_bin_rows: list[dict[str, object]] = []

    for salt in range(SEED_START, SEED_START + N_SPLITS):
        fitted = fit_split(c_events, ac_events, static, salt)
        if fitted is None:
            invalid_rows.append({"salt": salt, "reason": "unordered_or_empty_child_window"})
            continue
        meta, views = fitted
        split_hists: dict[str, np.ndarray] = {}
        for source, view in views.items():
            x = np.asarray(view["local_x"], dtype=float)
            w = np.asarray(view["weight"], dtype=float)
            for n_bins in BIN_COUNTS:
                matrices[n_bins][source].append(normalized_hist(x, w, n_bins))
            for bandwidth in BANDWIDTHS:
                kde_matrices[bandwidth][source].append(normalized_kde(x, w, bandwidth))
            split_hists[source] = matrices[PRIMARY_BINS][source][-1]
            for index, proportion in enumerate(split_hists[source]):
                primary_bin_rows.append(
                    {
                        "salt": salt,
                        "source": source,
                        "bin_low": index * 2.0 / PRIMARY_BINS,
                        "bin_high": (index + 1) * 2.0 / PRIMARY_BINS,
                        "bin_center": (index + 0.5) * 2.0 / PRIMARY_BINS,
                        "proportion_of_split_weight": float(proportion),
                    }
                )
        c = split_hists["C"]
        ac = split_hists["AC"]
        d = c - ac
        c_lower = float(np.mean(c[2:4]))
        c_saddle = float(np.mean(c[4:6]))
        c_upper = float(np.mean(c[6:8]))
        ac_lower = float(np.mean(ac[2:4]))
        ac_saddle = float(np.mean(ac[4:6]))
        ac_upper = float(np.mean(ac[6:8]))
        split_rows.append(
            {
                **meta,
                "C_effective_sample_size": effective_sample_size(np.asarray(views["C"]["weight"], dtype=float)),
                "AC_effective_sample_size": effective_sample_size(np.asarray(views["AC"]["weight"], dtype=float)),
                "C_lower_minus_saddle": c_lower - c_saddle,
                "C_upper_minus_saddle": c_upper - c_saddle,
                "AC_lower_minus_saddle": ac_lower - ac_saddle,
                "AC_upper_minus_saddle": ac_upper - ac_saddle,
                "C_lower_advantage_over_AC": (c_lower - c_saddle) - (ac_lower - ac_saddle),
                "mean_lower_C_minus_AC": float(np.mean(d[:4])),
                "mean_upper_C_minus_AC": float(np.mean(d[4:])),
            }
        )

    valid = len(split_rows)
    if valid == 0:
        raise RuntimeError("No valid T402 partitions")

    primary_c = np.vstack(matrices[PRIMARY_BINS]["C"])
    primary_ac = np.vstack(matrices[PRIMARY_BINS]["AC"])
    mean_c = np.mean(primary_c, axis=0)
    mean_ac = np.mean(primary_ac, axis=0)
    mean_d = mean_c - mean_ac
    sd_c = np.std(primary_c, axis=0, ddof=1)
    sd_ac = np.std(primary_ac, axis=0, ddof=1)
    centers = (np.arange(PRIMARY_BINS) + 0.5) * 2.0 / PRIMARY_BINS

    bin_summary_rows: list[dict[str, object]] = []
    for source, mean, sd in (("C", mean_c, sd_c), ("AC", mean_ac, sd_ac)):
        other = mean_ac if source == "C" else mean_c
        for index in range(PRIMARY_BINS):
            bin_summary_rows.append(
                {
                    "source": source,
                    "bin_center": float(centers[index]),
                    "mean_occupancy": float(mean[index]),
                    "sd_across_splits": float(sd[index]),
                    "mean_C_minus_AC": float(mean_c[index] - mean_ac[index]),
                    "other_source_mean": float(other[index]),
                }
            )

    split_array = {key: np.array([float(row[key]) for row in split_rows]) for key in (
        "C_lower_minus_saddle",
        "C_upper_minus_saddle",
        "AC_lower_minus_saddle",
        "AC_upper_minus_saddle",
        "C_lower_advantage_over_AC",
        "mean_lower_C_minus_AC",
        "mean_upper_C_minus_AC",
    )}
    rng = np.random.default_rng(402)
    l_ci = bootstrap_interval(split_array["C_lower_minus_saddle"], rng)
    u_ci = bootstrap_interval(split_array["C_upper_minus_saddle"], rng)

    exact_reflection = reflection_metrics(mean_d)
    lower = mean_d[:4]
    upper = mean_d[4:]
    permutation_rows: list[dict[str, object]] = []
    perm_scores: list[tuple[tuple[int, ...], float]] = []
    exact_assignment = (3, 2, 1, 0)
    for assignment in itertools.permutations(range(4)):
        score = cosine(lower, -upper[list(assignment)])
        perm_scores.append((assignment, score))
    exact_score = next(score for assignment, score in perm_scores if assignment == exact_assignment)
    exact_rank = 1 + sum(score > exact_score + 1e-12 for _, score in perm_scores)
    for assignment, score in sorted(perm_scores, key=lambda item: item[1], reverse=True):
        rank = 1 + sum(other > score + 1e-12 for _, other in perm_scores)
        permutation_rows.append(
            {
                "rank": rank,
                "assignment": " | ".join(f"{centers[i]:.3f}->{centers[4 + j]:.3f}" for i, j in enumerate(assignment)),
                "is_exact_reflection": assignment == exact_assignment,
                "cosine_similarity": score,
            }
        )

    alignment_rows: list[dict[str, object]] = []
    alignment_errors: list[tuple[int, float]] = []
    for shift in range(PRIMARY_BINS):
        shifted_d = mean_c - np.roll(mean_ac, shift)
        metrics = reflection_metrics(shifted_d)
        alignment_errors.append((shift, float(metrics["normalized_error"])))
        alignment_rows.append(
            {
                "AC_cyclic_shift_bins": shift,
                "shift_ara_units": shift * 2.0 / PRIMARY_BINS,
                "reflected_cosine": float(metrics["cosine"]),
                "normalized_reflection_error": float(metrics["normalized_error"]),
                "is_unshifted": shift == 0,
            }
        )
    unshifted_error = next(error for shift, error in alignment_errors if shift == 0)
    unshifted_rank = 1 + sum(error < unshifted_error - 1e-12 for _, error in alignment_errors)
    for row in alignment_rows:
        row["error_rank_lower_is_better"] = 1 + sum(
            error < float(row["normalized_reflection_error"]) - 1e-12 for _, error in alignment_errors
        )

    sensitivity_rows: list[dict[str, object]] = []
    sensitivity_pass_count = 0
    for n_bins in BIN_COUNTS:
        c_mean = np.mean(np.vstack(matrices[n_bins]["C"]), axis=0)
        ac_mean = np.mean(np.vstack(matrices[n_bins]["AC"]), axis=0)
        d_mean = c_mean - ac_mean
        metrics = reflection_metrics(d_mean)
        half = n_bins // 2
        lower_positive = int(np.sum(d_mean[:half] > 0))
        upper_negative = int(np.sum(d_mean[half:] < 0))
        passes = bool(float(metrics["cosine"]) >= 0.65)
        sensitivity_pass_count += int(passes)
        sensitivity_rows.append(
            {
                "bin_count": n_bins,
                "reflected_cosine": float(metrics["cosine"]),
                "normalized_reflection_error": float(metrics["normalized_error"]),
                "lower_positive_bins": lower_positive,
                "lower_bin_count": half,
                "upper_negative_bins": upper_negative,
                "upper_bin_count": half,
                "passes_cosine_0_65": passes,
            }
        )

    topology_rows: list[dict[str, object]] = []
    kde_mean_curves: dict[float, dict[str, np.ndarray]] = {}
    topology_pass_count = 0
    for bandwidth in BANDWIDTHS:
        c_curve = np.mean(np.vstack(kde_matrices[bandwidth]["C"]), axis=0)
        ac_curve = np.mean(np.vstack(kde_matrices[bandwidth]["AC"]), axis=0)
        difference = c_curve - ac_curve
        metrics = topology(difference)
        kde_mean_curves[bandwidth] = {"C": c_curve, "AC": ac_curve, "difference": difference}
        topology_pass_count += int(bool(metrics["passes_registered_windows"]))
        topology_rows.append(
            {
                "bandwidth": bandwidth,
                "positive_crest_x": metrics["positive_crest_x"],
                "positive_crest_value": metrics["positive_crest_value"],
                "crossing_nearest_ridge_x": metrics["crossing_nearest_ridge_x"],
                "negative_trough_x": metrics["negative_trough_x"],
                "negative_trough_value": metrics["negative_trough_value"],
                "crossing_count": metrics["crossing_count"],
                "all_crossings": " | ".join(f"{value:.6f}" for value in metrics["all_crossings"]),
                "passes_registered_windows": metrics["passes_registered_windows"],
            }
        )

    gates = {
        "G1_raw_whole_shape": bool(
            float(np.mean(split_array["C_lower_minus_saddle"])) > 0
            and l_ci[0] > 0
            and float(np.mean(split_array["C_upper_minus_saddle"])) > 0
            and u_ci[0] > 0
            and float(np.mean(split_array["C_lower_minus_saddle"] > 0)) >= 0.60
            and float(np.mean(split_array["C_upper_minus_saddle"] > 0)) >= 0.60
        ),
        "G2_source_specific_two_sided_difference": bool(
            int(np.sum(mean_d[:4] > 0)) >= 3
            and int(np.sum(mean_d[4:] < 0)) >= 3
            and float(np.mean(split_array["mean_lower_C_minus_AC"] > 0)) >= 0.65
            and float(np.mean(split_array["mean_upper_C_minus_AC"] < 0)) >= 0.65
        ),
        "G3_continuous_topology": bool(topology_pass_count >= 3),
        "G4_exact_static_reflection": bool(
            exact_reflection["cosine"] >= 0.75
            and exact_rank <= 3
            and sensitivity_pass_count >= 3
        ),
        "G5_correct_source_alignment": bool(
            unshifted_rank <= 2
            and float(np.mean(split_array["C_lower_advantage_over_AC"] > 0)) >= 0.70
        ),
    }
    if all(gates.values()):
        verdict = "SOURCE-SPECIFIC TWO-SIDED CHILD RELATION WITH STATIC REFLECTION SUPPORTED"
    elif gates["G1_raw_whole_shape"] and gates["G2_source_specific_two_sided_difference"] and gates["G3_continuous_topology"]:
        verdict = "SOURCE-SPECIFIC TWO-SIDED CHILD RELATION; EXACT ANTI-PHASE NOT IDENTIFIED"
    elif gates["G1_raw_whole_shape"] and gates["G2_source_specific_two_sided_difference"]:
        verdict = "BINNED TWO-SIDED SOURCE RELATION; CONTINUOUS TOPOLOGY UNRESOLVED"
    elif gates["G1_raw_whole_shape"]:
        verdict = "COMMON TWO-SIDED SHAPE; SOURCE-SPECIFIC RELATION NOT IDENTIFIED"
    else:
        verdict = "NO STABLE WHOLE SHAPE"

    results = {
        "test": "T402",
        "protocol_sha256": sha256(PROTOCOL),
        "identity": "COHERENT CsI delayed-child identity; C and AC source records; unchanged T400 local child rung",
        "coordinate": "calibration-frozen local child ARA 0-2 between branch equality L and delayed-rate return R",
        "fresh_salts": [SEED_START, SEED_START + N_SPLITS - 1],
        "splits": {
            "requested": N_SPLITS,
            "valid": valid,
            "invalid": len(invalid_rows),
            "valid_fraction": valid / N_SPLITS,
            "interpretation": "overlapping deterministic resampling stability probes, not independent experiments",
        },
        "raw_C_shape": {
            "mean_lower_minus_saddle": float(np.mean(split_array["C_lower_minus_saddle"])),
            "lower_resampling_interval_95": list(l_ci),
            "fraction_splits_lower_positive": float(np.mean(split_array["C_lower_minus_saddle"] > 0)),
            "mean_upper_minus_saddle": float(np.mean(split_array["C_upper_minus_saddle"])),
            "upper_resampling_interval_95": list(u_ci),
            "fraction_splits_upper_positive": float(np.mean(split_array["C_upper_minus_saddle"] > 0)),
        },
        "source_difference": {
            "mean_C_minus_AC_by_bin": [float(value) for value in mean_d],
            "lower_positive_bin_count": int(np.sum(mean_d[:4] > 0)),
            "upper_negative_bin_count": int(np.sum(mean_d[4:] < 0)),
            "fraction_splits_mean_lower_positive": float(np.mean(split_array["mean_lower_C_minus_AC"] > 0)),
            "fraction_splits_mean_upper_negative": float(np.mean(split_array["mean_upper_C_minus_AC"] < 0)),
            "fraction_splits_C_lower_contrast_exceeds_AC": float(np.mean(split_array["C_lower_advantage_over_AC"] > 0)),
        },
        "reflection": {
            "primary_eight_bin_cosine": float(exact_reflection["cosine"]),
            "primary_normalized_error": float(exact_reflection["normalized_error"]),
            "exact_mapping_rank_of_24": int(exact_rank),
            "bin_sensitivities_passing_cosine_0_65": sensitivity_pass_count,
        },
        "alignment": {
            "unshifted_error": unshifted_error,
            "unshifted_rank_of_8": int(unshifted_rank),
        },
        "continuous_topology": {
            "bandwidths_passing_registered_windows": topology_pass_count,
            "bandwidth_count": len(BANDWIDTHS),
        },
        "gates": gates,
        "verdict": verdict,
        "boundaries": [
            "The broad shape was selected after inspecting T401 and is a registered follow-up.",
            "C and AC acquisition context can differ; subtraction does not automatically isolate one physical component.",
            "Probability closure forces each differential to sum to zero; location, topology and controls carry the evidence.",
            "This population/statistical relation does not directly show individual neutrino creation.",
        ],
    }

    write_csv(OUT / "T402_SPLITS.csv", split_rows)
    write_csv(OUT / "T402_INVALID_SPLITS.csv", invalid_rows)
    write_csv(OUT / "T402_PRIMARY_BIN_DISTRIBUTIONS.csv", primary_bin_rows)
    write_csv(OUT / "T402_BIN_SUMMARY.csv", bin_summary_rows)
    write_csv(OUT / "T402_KDE_TOPOLOGY.csv", topology_rows)
    write_csv(OUT / "T402_REFLECTION_PERMUTATIONS.csv", permutation_rows)
    write_csv(OUT / "T402_ALIGNMENT_CONTROLS.csv", alignment_rows)
    write_csv(OUT / "T402_BIN_SENSITIVITY.csv", sensitivity_rows)
    (OUT / "T402_RESULTS.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    figure = plt.figure(figsize=(16, 15), constrained_layout=True)
    grid_spec = figure.add_gridspec(3, 2)

    ax = figure.add_subplot(grid_spec[0, 0])
    width = 0.105
    ax.bar(centers - width / 2, mean_c, width=width, color="#3975b8", alpha=0.85, label="C mean")
    ax.bar(centers + width / 2, mean_ac, width=width, color="#d99a2b", alpha=0.80, label="AC mean")
    ax.errorbar(centers - width / 2, mean_c, yerr=sd_c, fmt="none", ecolor="#163c69", capsize=3, alpha=0.7)
    ax.errorbar(centers + width / 2, mean_ac, yerr=sd_ac, fmt="none", ecolor="#805000", capsize=3, alpha=0.7)
    ax.axvline(1.0, color="black", linestyle="--", linewidth=1.4, label="ARA ridge 1.0")
    ax.axvspan(0.5, 1.0, color="#5ea769", alpha=0.08)
    ax.axvspan(1.0, 1.5, color="#888888", alpha=0.08)
    ax.axvspan(1.5, 2.0, color="#8959a8", alpha=0.08)
    ax.set(title="Complete child distributions", xlabel="local child ARA x", ylabel="mean share of split weight", xlim=(0, 2))
    ax.legend(frameon=False, ncol=2)

    ax = figure.add_subplot(grid_spec[0, 1])
    colors = ["#2e8b57" if value >= 0 else "#b5483f" for value in mean_d]
    ax.bar(centers, mean_d, width=0.21, color=colors, alpha=0.9)
    for x, y in zip(centers, mean_d):
        ax.text(x, y + (0.0015 if y >= 0 else -0.0015), f"{y:+.3f}", ha="center", va="bottom" if y >= 0 else "top", fontsize=9)
    ax.axhline(0, color="black", linewidth=1)
    ax.axvline(1.0, color="black", linestyle="--", linewidth=1.4)
    ax.set(title="Source-specific axis: C minus AC", xlabel="local child ARA x", ylabel="mean occupancy difference", xlim=(0, 2))

    ax = figure.add_subplot(grid_spec[1, 0])
    for bandwidth, color in zip(BANDWIDTHS, ("#183d69", "#367bb5", "#6aa3c8", "#9bc5d9")):
        curve = kde_mean_curves[bandwidth]["difference"]
        ax.plot(GRID, curve, color=color, linewidth=2, label=f"h={bandwidth:.2f}")
    ax.axhline(0, color="black", linewidth=1)
    ax.axvline(1.0, color="black", linestyle="--", linewidth=1.4, label="ridge 1.0")
    ax.set(title="Continuous C−AC topology", xlabel="local child ARA x", ylabel="KDE density difference", xlim=(0, 2))
    ax.legend(frameon=False, ncol=2)

    ax = figure.add_subplot(grid_spec[1, 1])
    lower_contrast = split_array["C_lower_minus_saddle"]
    upper_contrast = split_array["C_upper_minus_saddle"]
    ax.scatter(lower_contrast, upper_contrast, s=18, alpha=0.45, color="#3975b8", edgecolors="none")
    ax.axvline(0, color="black", linewidth=1)
    ax.axhline(0, color="black", linewidth=1)
    ax.scatter([np.mean(lower_contrast)], [np.mean(upper_contrast)], s=130, marker="*", color="#d99a2b", edgecolor="black", label="mean split")
    ax.set(
        title="Fresh-partition whole-shape stability",
        xlabel="C lower lobe minus saddle",
        ylabel="C upper lobe minus saddle",
    )
    ax.legend(frameon=False)

    ax = figure.add_subplot(grid_spec[2, 0])
    reflected_upper = -mean_d[4:][::-1]
    pair_index = np.arange(4)
    labels = [f"{centers[i]:.3f}↔{centers[7-i]:.3f}" for i in range(4)]
    ax.plot(pair_index, mean_d[:4], marker="o", linewidth=2.5, color="#3975b8", label="lower C−AC")
    ax.plot(pair_index, reflected_upper, marker="s", linewidth=2.5, color="#d99a2b", label="negative reflected upper")
    ax.set_xticks(pair_index, labels, rotation=20)
    ax.set(title=f"Static reflected mean shape: cosine {exact_reflection['cosine']:.3f}, rank {exact_rank}/24", xlabel="predeclared reflected pair", ylabel="differential amplitude")
    ax.legend(frameon=False)

    ax = figure.add_subplot(grid_spec[2, 1])
    gate_names = ["G1\nwhole", "G2\nsource", "G3\ntopology", "G4\nreflection", "G5\nalignment"]
    gate_values = [1 if value else 0 for value in gates.values()]
    gate_colors = ["#2e8b57" if value else "#b5483f" for value in gate_values]
    ax.bar(gate_names, gate_values, color=gate_colors)
    for index, value in enumerate(gate_values):
        ax.text(index, 0.5 if value else 0.08, "PASS" if value else "FAIL", ha="center", va="center", color="white" if value else "black", fontweight="bold")
    ax.set_ylim(0, 1.05)
    ax.set_yticks([0, 1], ["fail", "pass"])
    ax.set(title="Frozen gates", ylabel="registered result")

    figure.suptitle(f"T402 — Whole-shape child relation\n{verdict}\n{valid}/{N_SPLITS} valid fresh partitions", fontsize=17, fontweight="bold")
    figure.savefig(OUT / "T402_WHOLE_SHAPE_CHILD_RELATION.png", dpi=180)
    plt.close(figure)

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
