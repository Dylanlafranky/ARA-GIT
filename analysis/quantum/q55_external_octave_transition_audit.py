#!/usr/bin/env python3
"""Q55 retrospective audit of octave-like external-direction transitions.

The script reads the exact twelve compact trajectories used by the saved Q49-
Q52 3D visual. It then audits chronological step growth, the independently
declared Q52 slice-500 continuation boundary, movement-strength sensitivities,
quadrant transitions, and power-of-two specificity against rival scale
lattices.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import rankdata


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
VISUAL = REPO / "3D models" / "q49_q52_partial_external_rotation_3d.html"
PROTOCOL = HERE / "Q55_EXTERNAL_OCTAVE_TRANSITION_AUDIT_PROTOCOL_v1_FROZEN.md"
PATHS_CSV = HERE / "Q55_EXTERNAL_OCTAVE_TRANSITION_PATHS.csv"
STEPS_CSV = HERE / "Q55_EXTERNAL_OCTAVE_TRANSITION_STEPS.csv"
RUNS_CSV = HERE / "Q55_EXTERNAL_OCTAVE_TRANSITION_RUNS.csv"
RESULTS_JSON = HERE / "Q55_EXTERNAL_OCTAVE_TRANSITION_RESULTS.json"
FIGURE_PNG = HERE / "Q55_EXTERNAL_OCTAVE_TRANSITION_AUDIT.png"
FIGURE_SVG = HERE / "Q55_EXTERNAL_OCTAVE_TRANSITION_AUDIT.svg"
REPORT_MD = HERE / "Q55_EXTERNAL_OCTAVE_TRANSITION_REPORT_2026-07-31.md"

EXPECTED_VISUAL_SHA256 = (
    "780f9f19cde8e6a69ce3031c88356ef6c703beb4e0129c81ae9b499c8d40f489"
)
REFERENCE_HEADING = 0.4929567149606686
Q52_BOUNDARY = 500.0
SEED = 20260731
DRAWS = 50_000
THRESHOLDS = (0.0, 0.05, 0.10, 0.25)
BASES = {
    "2": 2.0,
    "phi": (1.0 + math.sqrt(5.0)) / 2.0,
    "e": math.e,
    "3": 3.0,
    "10": 10.0,
}

ORDER = [
    "q49_q50",
    "q51_greedy",
    "q51_landmax",
    "q51_mimic",
    "q52_fixed_A",
    "q52_fixed_B",
    "q52_alternating_AB",
    "q52_alternating_BA",
    "q52_random_520101",
    "q52_random_520102",
    "q52_random_520103",
    "q52_random_520104",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_visual_data() -> dict:
    observed_hash = sha256(VISUAL)
    if observed_hash != EXPECTED_VISUAL_SHA256:
        raise RuntimeError(
            "Frozen 3D path source changed: "
            f"expected {EXPECTED_VISUAL_SHA256}, observed {observed_hash}"
        )
    source = html.unescape(VISUAL.read_text(encoding="utf-8"))
    marker = "const DATA = "
    start = source.index(marker) + len(marker)
    data, _ = json.JSONDecoder().raw_decode(source[start:])
    if data["order"] != ORDER:
        raise RuntimeError("Frozen path order does not match Q55 protocol.")
    if abs(float(data["referenceHeading"]) - REFERENCE_HEADING) > 1e-15:
        raise RuntimeError("Frozen reference heading does not match Q55 protocol.")
    return data


def circular_step(a: float, b: float) -> float:
    return abs(((b - a + 0.5) % 1.0) - 0.5)


def quadrant(heading: float) -> int:
    relative = (heading - REFERENCE_HEADING + 0.125) % 1.0
    return int(math.floor(relative / 0.25)) % 4


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 3 or np.allclose(y, y[0]):
        return float("nan")
    rx = rankdata(x)
    ry = rankdata(y)
    return float(np.corrcoef(rx, ry)[0, 1])


def safe_ratio(numerator: float, denominator: float) -> float:
    if not (np.isfinite(numerator) and np.isfinite(denominator)):
        return float("nan")
    if denominator <= 0.0:
        return float("nan")
    return float(numerator / denominator)


def threshold_key(threshold: float) -> str:
    return f"{int(round(threshold * 100)):02d}pct"


def base_distance(values: np.ndarray, base: float) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    out = np.full(values.shape, np.nan, dtype=float)
    valid = np.isfinite(values) & (values > 0.0)
    if not np.any(valid):
        return out
    magnitudes = np.maximum(values[valid], 1.0 / values[valid])
    logs = np.log(magnitudes) / math.log(base)
    exponents = np.maximum(1.0, np.rint(logs))
    out[valid] = 2.0 * np.abs(logs - exponents)
    return out


def p_upper(null: np.ndarray, observed: float) -> float:
    finite = null[np.isfinite(null)]
    if not np.isfinite(observed) or len(finite) == 0:
        return float("nan")
    return float((1 + np.count_nonzero(finite >= observed)) / (len(finite) + 1))


def p_lower(null: np.ndarray, observed: float) -> float:
    finite = null[np.isfinite(null)]
    if not np.isfinite(observed) or len(finite) == 0:
        return float("nan")
    return float((1 + np.count_nonzero(finite <= observed)) / (len(finite) + 1))


def split_masks(n: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    groups = np.array_split(np.arange(n), 3)
    masks = []
    for group in groups:
        mask = np.zeros(n, dtype=bool)
        mask[group] = True
        masks.append(mask)
    return masks[0], masks[1], masks[2]


def median_masked(values: np.ndarray, mask: np.ndarray) -> float:
    chosen = values[mask]
    if len(chosen) == 0:
        return float("nan")
    return float(np.median(chosen))


def build_tables(data: dict) -> tuple[list[dict], dict[str, dict]]:
    path_rows: list[dict] = []
    paths: dict[str, dict] = {}
    for path_id in ORDER:
        record = data["datasets"][path_id]
        points = record["points"]
        group = (
            "Q52 continuation"
            if path_id.startswith("q52_")
            else ("Q51 cross-archive" if path_id.startswith("q51_") else "Q49/Q50")
        )
        for index, point in enumerate(points):
            path_rows.append(
                {
                    "path_id": path_id,
                    "label": record["label"],
                    "group": group,
                    "index": index,
                    "source_time": float(point["t"]),
                    "ara_x": float(point["x"]),
                    "heading_turns": float(point["h"]),
                    "mean_relative_movement": float(point["m"]),
                }
            )

        headings = np.array([float(p["h"]) for p in points])
        times = np.array([float(p["t"]) for p in points])
        xs = np.array([float(p["x"]) for p in points])
        movements = np.array([float(p["m"]) for p in points])
        step_sizes = np.array(
            [circular_step(headings[i - 1], headings[i]) for i in range(1, len(points))]
        )
        step_movements = (movements[:-1] + movements[1:]) / 2.0
        peak = float(np.max(step_movements)) if len(step_movements) else float("nan")
        movement_norm = step_movements / peak if peak > 0.0 else np.zeros_like(step_movements)
        q0 = np.array([quadrant(h) for h in headings[:-1]], dtype=int)
        q1 = np.array([quadrant(h) for h in headings[1:]], dtype=int)
        paths[path_id] = {
            "label": record["label"],
            "group": group,
            "times": times,
            "xs": xs,
            "headings": headings,
            "movements": movements,
            "step_sizes": step_sizes,
            "step_movements": step_movements,
            "movement_norm": movement_norm,
            "q0": q0,
            "q1": q1,
            "quadrant_cross": q0 != q1,
            "large": step_sizes >= 0.125,
        }
    return path_rows, paths


def observed_run_metrics(path_id: str, path: dict, threshold: float) -> dict:
    steps = path["step_sizes"]
    movement_mask = path["movement_norm"] >= threshold
    early, middle, late = split_masks(len(steps))
    med_early = median_masked(steps, early & movement_mask)
    med_middle = median_masked(steps, middle & movement_mask)
    med_late = median_masked(steps, late & movement_mask)
    ratio = safe_ratio(med_late, med_early)
    active_indices = np.flatnonzero(movement_mask)
    rho_step = spearman(active_indices.astype(float), steps[movement_mask])
    rho_movement = spearman(steps[movement_mask], path["movement_norm"][movement_mask])
    large_active = path["large"] & movement_mask
    large_count = int(np.count_nonzero(large_active))
    large_cross = int(np.count_nonzero(large_active & path["quadrant_cross"]))
    metrics = {
        "active_steps": int(np.count_nonzero(movement_mask)),
        "median_early_step_turns": med_early,
        "median_middle_step_turns": med_middle,
        "median_late_step_turns": med_late,
        "late_early_ratio": ratio,
        "log2_late_early_ratio": float(math.log2(ratio))
        if np.isfinite(ratio) and ratio > 0.0
        else float("nan"),
        "spearman_step_vs_order": rho_step,
        "spearman_step_vs_movement": rho_movement,
        "quadrant_transitions": int(np.count_nonzero(path["quadrant_cross"] & movement_mask)),
        "large_steps": large_count,
        "large_step_quadrant_transitions": large_cross,
        "large_step_quadrant_transition_share": safe_ratio(large_cross, large_count),
    }
    if path_id.startswith("q52_"):
        pre = path["times"][1:] <= Q52_BOUNDARY
        post = path["times"][1:] > Q52_BOUNDARY
        med_pre = median_masked(steps, pre & movement_mask)
        med_post = median_masked(steps, post & movement_mask)
        boundary_ratio = safe_ratio(med_post, med_pre)
        metrics.update(
            {
                "median_pre_boundary_step_turns": med_pre,
                "median_post_boundary_step_turns": med_post,
                "post_pre_ratio": boundary_ratio,
                "log2_post_pre_ratio": float(math.log2(boundary_ratio))
                if np.isfinite(boundary_ratio) and boundary_ratio > 0.0
                else float("nan"),
            }
        )
    return metrics


def permutation_distributions(
    paths: dict[str, dict], rng: np.random.Generator
) -> tuple[dict[str, dict], dict[str, dict]]:
    """Return per-threshold generic and Q52 path-level null arrays."""
    generic = {
        threshold_key(t): {"log_ratios": [], "positive": []} for t in THRESHOLDS
    }
    q52 = {
        threshold_key(t): {"log_ratios": [], "positive": []} for t in THRESHOLDS
    }

    for path_id in ORDER:
        path = paths[path_id]
        steps = path["step_sizes"]
        moves = path["movement_norm"]
        n = len(steps)
        perm = np.argsort(rng.random((DRAWS, n)), axis=1)
        perm_steps = steps[perm]
        perm_moves = moves[perm]
        early, _, late = split_masks(n)

        for threshold in THRESHOLDS:
            key = threshold_key(threshold)
            active = perm_moves >= threshold
            early_values = np.where(active[:, early], perm_steps[:, early], np.nan)
            late_values = np.where(active[:, late], perm_steps[:, late], np.nan)
            with warnings.catch_warnings(), np.errstate(all="ignore"):
                warnings.simplefilter("ignore", category=RuntimeWarning)
                med_early = np.nanmedian(early_values, axis=1)
                med_late = np.nanmedian(late_values, axis=1)
                ratios = med_late / med_early
                logs = np.log2(ratios)
            generic[key]["log_ratios"].append(logs)
            generic[key]["positive"].append(logs > 0.0)

            if path_id.startswith("q52_"):
                pre = path["times"][1:] <= Q52_BOUNDARY
                post = path["times"][1:] > Q52_BOUNDARY
                pre_values = np.where(active[:, pre], perm_steps[:, pre], np.nan)
                post_values = np.where(active[:, post], perm_steps[:, post], np.nan)
                with warnings.catch_warnings(), np.errstate(all="ignore"):
                    warnings.simplefilter("ignore", category=RuntimeWarning)
                    med_pre = np.nanmedian(pre_values, axis=1)
                    med_post = np.nanmedian(post_values, axis=1)
                    boundary_ratios = med_post / med_pre
                    boundary_logs = np.log2(boundary_ratios)
                q52[key]["log_ratios"].append(boundary_logs)
                q52[key]["positive"].append(boundary_logs > 0.0)

    for collection in (generic, q52):
        for key in collection:
            collection[key]["log_ratios"] = np.array(collection[key]["log_ratios"])
            collection[key]["positive"] = np.array(collection[key]["positive"])
    return generic, q52


def summarize_growth(
    run_metrics: dict[str, dict],
    null: dict[str, dict],
    q52_only: bool,
) -> dict:
    selected = [p for p in ORDER if p.startswith("q52_")] if q52_only else ORDER
    summary: dict[str, dict] = {}
    ratio_name = "post_pre_ratio" if q52_only else "late_early_ratio"
    log_name = "log2_post_pre_ratio" if q52_only else "log2_late_early_ratio"
    for threshold in THRESHOLDS:
        key = threshold_key(threshold)
        logs = np.array([run_metrics[p][key][log_name] for p in selected], dtype=float)
        ratios = np.array([run_metrics[p][key][ratio_name] for p in selected], dtype=float)
        finite = np.isfinite(logs)
        observed_median = float(np.median(logs[finite])) if np.any(finite) else float("nan")
        observed_positive = int(np.count_nonzero(ratios[finite] > 1.0))
        null_median = np.nanmedian(null[key]["log_ratios"], axis=0)
        null_positive = np.nansum(null[key]["positive"], axis=0)
        summary[key] = {
            "eligible_paths": int(np.count_nonzero(finite)),
            "paths_with_growth": observed_positive,
            "median_log2_ratio": observed_median,
            "median_ratio": float(2.0**observed_median)
            if np.isfinite(observed_median)
            else float("nan"),
            "permutation_p_median_growth": p_upper(null_median, observed_median),
            "permutation_p_growth_count": p_upper(
                null_positive.astype(float), float(observed_positive)
            ),
            "null_median_log2_ratio_mean": float(np.nanmean(null_median)),
            "null_growth_count_mean": float(np.nanmean(null_positive)),
        }
    return summary


def summarize_specificity(
    run_metrics: dict[str, dict],
    q52_null: dict[str, dict],
    rng: np.random.Generator,
) -> dict:
    selected = [p for p in ORDER if p.startswith("q52_")]
    output: dict[str, dict] = {}
    for threshold in THRESHOLDS:
        key = threshold_key(threshold)
        ratios = np.array(
            [run_metrics[p][key]["post_pre_ratio"] for p in selected], dtype=float
        )
        valid = np.isfinite(ratios) & (ratios > 0.0)
        observed_by_base = {}
        nearest = {}
        for name, base in BASES.items():
            distances = base_distance(ratios[valid], base)
            observed_by_base[name] = {
                "median_normalized_distance": float(np.nanmedian(distances)),
                "mean_normalized_distance": float(np.nanmean(distances)),
            }
        for path_id, ratio in zip(selected, ratios):
            if not np.isfinite(ratio) or ratio <= 0.0:
                nearest[path_id] = None
                continue
            magnitude = max(ratio, 1.0 / ratio)
            z = math.log(magnitude, 2.0)
            exponent = max(1, int(round(z)))
            nearest[path_id] = {
                "ratio": float(ratio),
                "nearest_power_of_two": float(2.0**exponent),
                "octave_exponent": exponent,
                "normalized_distance": float(base_distance(np.array([ratio]), 2.0)[0]),
            }

        perm_ratios = 2.0 ** q52_null[key]["log_ratios"]
        perm_distance = base_distance(perm_ratios, 2.0)
        perm_median = np.nanmedian(perm_distance, axis=0)
        observed_distance = observed_by_base["2"]["median_normalized_distance"]
        mantissa_null = np.median(
            rng.random((DRAWS, int(np.count_nonzero(valid)))), axis=1
        )
        ordered_bases = sorted(
            observed_by_base,
            key=lambda b: observed_by_base[b]["median_normalized_distance"],
        )
        output[key] = {
            "valid_q52_paths": int(np.count_nonzero(valid)),
            "base_distances": observed_by_base,
            "best_base": ordered_bases[0] if ordered_bases else None,
            "base_order": ordered_bases,
            "base2_permutation_p": p_lower(perm_median, observed_distance),
            "base2_scale_free_mantissa_p": p_lower(mantissa_null, observed_distance),
            "nearest_power_of_two_by_path": nearest,
        }
    return output


def write_csvs(path_rows: list[dict], paths: dict[str, dict], run_metrics: dict) -> None:
    with PATHS_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(path_rows[0]))
        writer.writeheader()
        writer.writerows(path_rows)

    step_rows = []
    for path_id in ORDER:
        path = paths[path_id]
        for i, step in enumerate(path["step_sizes"]):
            step_rows.append(
                {
                    "path_id": path_id,
                    "group": path["group"],
                    "step_index": i,
                    "source_time_start": path["times"][i],
                    "source_time_end": path["times"][i + 1],
                    "heading_start_turns": path["headings"][i],
                    "heading_end_turns": path["headings"][i + 1],
                    "ara_x_start": path["xs"][i],
                    "ara_x_end": path["xs"][i + 1],
                    "absolute_circular_step_turns": step,
                    "step_mean_relative_movement": path["step_movements"][i],
                    "path_normalized_movement": path["movement_norm"][i],
                    "quadrant_start": path["q0"][i],
                    "quadrant_end": path["q1"][i],
                    "quadrant_transition": int(path["quadrant_cross"][i]),
                    "large_step_ge_0_125_turn": int(path["large"][i]),
                    "q52_period": (
                        "historical"
                        if path_id.startswith("q52_")
                        and path["times"][i + 1] <= Q52_BOUNDARY
                        else (
                            "continuation"
                            if path_id.startswith("q52_")
                            else "not_applicable"
                        )
                    ),
                }
            )
    with STEPS_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(step_rows[0]))
        writer.writeheader()
        writer.writerows(step_rows)

    run_rows = []
    for path_id in ORDER:
        for threshold in THRESHOLDS:
            key = threshold_key(threshold)
            row = {
                "path_id": path_id,
                "label": paths[path_id]["label"],
                "group": paths[path_id]["group"],
                "movement_threshold": threshold,
            }
            row.update(run_metrics[path_id][key])
            run_rows.append(row)
    fieldnames = sorted({key for row in run_rows for key in row})
    preferred = ["path_id", "label", "group", "movement_threshold"]
    fieldnames = preferred + [f for f in fieldnames if f not in preferred]
    with RUNS_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(run_rows)


def make_figure(
    paths: dict[str, dict],
    run_metrics: dict[str, dict],
    specificity: dict[str, dict],
) -> None:
    plt.rcParams.update({"font.size": 9, "axes.titleweight": "bold"})
    fig, axes = plt.subplots(2, 2, figsize=(15, 10), constrained_layout=True)

    ax = axes[0, 0]
    y = np.arange(len(ORDER))
    early = [run_metrics[p]["00pct"]["median_early_step_turns"] for p in ORDER]
    middle = [run_metrics[p]["00pct"]["median_middle_step_turns"] for p in ORDER]
    late = [run_metrics[p]["00pct"]["median_late_step_turns"] for p in ORDER]
    eps = 1e-5
    ax.scatter(np.maximum(early, eps), y, label="early third", marker="o")
    ax.scatter(np.maximum(middle, eps), y, label="middle third", marker="s")
    ax.scatter(np.maximum(late, eps), y, label="late third", marker="D")
    for row, a, c in zip(y, early, late):
        ax.plot([max(a, eps), max(c, eps)], [row, row], color="#9ca3af", lw=0.8)
    ax.set_xscale("log")
    ax.set_yticks(y, [p.replace("q52_", "").replace("q51_", "Q51 ") for p in ORDER])
    ax.invert_yaxis()
    ax.set_xlabel("median absolute external-heading step (turns, log scale)")
    ax.set_title("A. Small-to-large step audit by path")
    ax.legend(frameon=False)

    ax = axes[0, 1]
    q52 = [p for p in ORDER if p.startswith("q52_")]
    ratios = [run_metrics[p]["00pct"]["post_pre_ratio"] for p in q52]
    colors = ["#2563eb" if r > 1 else "#dc2626" for r in ratios]
    ax.bar(np.arange(len(q52)), ratios, color=colors)
    for power in (2, 4, 8, 16, 32, 64, 128, 256, 512):
        ax.axhline(power, color="#6b7280", lw=0.6, alpha=0.45)
        ax.text(len(q52) - 0.45, power, f"×{power}", va="bottom", ha="right", fontsize=7)
    ax.set_yscale("log")
    ax.set_xticks(
        np.arange(len(q52)),
        [p.replace("q52_", "") for p in q52],
        rotation=35,
        ha="right",
    )
    ax.set_ylabel("median post/pre step-size ratio (log scale)")
    ax.set_title("B. Q52 response across the frozen slice-500 boundary")

    ax = axes[1, 0]
    bases = specificity["00pct"]["base_order"]
    distances = [
        specificity["00pct"]["base_distances"][b]["median_normalized_distance"]
        for b in bases
    ]
    ax.bar(bases, distances, color=["#2563eb" if b == "2" else "#9ca3af" for b in bases])
    ax.axhline(0.5, color="#d97706", linestyle="--", lw=1, label="random mantissa median")
    ax.set_ylabel("median normalized distance (lower is closer)")
    ax.set_title("C. Scale-lattice specificity")
    ax.legend(frameon=False)

    ax = axes[1, 1]
    large = np.array([np.count_nonzero(paths[p]["large"]) for p in ORDER])
    crossed = np.array(
        [np.count_nonzero(paths[p]["large"] & paths[p]["quadrant_cross"]) for p in ORDER]
    )
    shares = np.divide(crossed, large, out=np.zeros_like(crossed, dtype=float), where=large > 0)
    ax.bar(np.arange(len(ORDER)), shares, color="#7c3aed")
    ax.set_ylim(0, 1.05)
    ax.set_xticks(
        np.arange(len(ORDER)),
        [p.replace("q52_", "").replace("q51_", "Q51 ") for p in ORDER],
        rotation=40,
        ha="right",
    )
    ax.set_ylabel("share of large steps crossing quadrant")
    ax.set_title("D. Large steps and quadrant change")
    for i, (num, den) in enumerate(zip(crossed, large)):
        ax.text(i, shares[i] + 0.025, f"{num}/{den}", ha="center", fontsize=7)

    fig.suptitle(
        "Q55 — retrospective external octave-transition audit\n"
        "Growth, quadrant change and ×2 specificity are separate questions",
        fontsize=15,
        fontweight="bold",
    )
    fig.savefig(FIGURE_PNG, dpi=180)
    fig.savefig(FIGURE_SVG)
    plt.close(fig)


def clean_json(value):
    if isinstance(value, dict):
        return {k: clean_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json(v) for v in value]
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def make_report(results: dict) -> str:
    generic = results["generic_growth"]["00pct"]
    generic10 = results["generic_growth"]["10pct"]
    q52 = results["q52_boundary_growth"]["00pct"]
    q5210 = results["q52_boundary_growth"]["10pct"]
    spec = results["octave_specificity"]["00pct"]
    spec10 = results["octave_specificity"]["10pct"]
    quadrant = results["quadrant_summary"]
    return f"""# Q55 — external octave-transition audit

**Date:** 31 July 2026  
**Status:** {results["verdict"]}  
**Evidence class:** retrospective / exploratory

## Answer first

The visual impression contained a real structural effect, but the strict
claim needs two parts.

1. **Step scale grows:** {generic["paths_with_growth"]}/{generic["eligible_paths"]}
   paths had larger late than early steps. The pooled median increase was
   `{generic["median_ratio"]:.3f}×` (`p={generic["permutation_p_median_growth"]:.5f}`).
   With the 10% movement guard it was
   `{generic10["paths_with_growth"]}/{generic10["eligible_paths"]}` paths and
   `{generic10["median_ratio"]:.3f}×`
   (`p={generic10["permutation_p_median_growth"]:.5f}`).
2. **Q52 boundary response is especially strong:** all
   `{q52["paths_with_growth"]}/{q52["eligible_paths"]}` continuation families
   increased after the independently declared slice-500 boundary. The median
   increase was `{q52["median_ratio"]:.3f}×`
   (`p={q52["permutation_p_median_growth"]:.5f}`); with the 10% guard it was
   `{q5210["median_ratio"]:.3f}×`
   (`p={q5210["permutation_p_median_growth"]:.5f}`).
3. **Large steps usually change quadrant:** `{quadrant["large_crossings"]}` of
   `{quadrant["large_steps"]}` large steps did so
   (`{100*quadrant["large_crossing_share"]:.1f}%`).
4. **Specific ×2 octave spacing is not established:** base 2 ranked
   `{spec["base_order"].index("2")+1}` of {len(spec["base_order"])} rival
   lattices and had median normalized distance
   `{spec["base_distances"]["2"]["median_normalized_distance"]:.4f}`. Its
   permutation `p` was `{spec["base2_permutation_p"]:.5f}` and scale-free
   mantissa `p` was `{spec["base2_scale_free_mantissa_p"]:.5f}`. Under the
   10% movement guard, the corresponding values were
   `{spec10["base2_permutation_p"]:.5f}` and
   `{spec10["base2_scale_free_mantissa_p"]:.5f}`.

The clean conclusion is therefore: the unguarded twelve-path audit contains a
strong small-to-large transition, and in Q52 that transition remains strong
after the movement guard and is coupled to the change in the allowed
continuation environment. Only six of twelve paths retained both an early and
late section under the generic 10% guard, so the strict generic gate remains
under-covered. The current data do **not** uniquely identify the scale change
as powers of two.

## Plain ARA interpretation

The paths begin with local movement inside a directional neighbourhood. After
the coupling boundary, the same measured external identity begins making much
larger directional moves, and those moves usually carry it into another
quadrant. That part matches Dylan's visual reading.

What the audit cannot honestly add is “each move is one ×2 rung.” The sizes
are irregular. Several whole pre/post scale ratios sit near powers of two,
but not tightly enough to beat the frozen specificity controls. The strongest
current ARA wording is **up-rung-like expansion under changed coupling**, not
yet a measured octave ladder.

## Scope and dependence

- Q49–Q52 are simulator-derived trajectory analyses.
- The eight Q52 families share the same historical source construction; they
  are eight coupling conditions, not eight independent experiments.
- The effect is not a blind discovery because the visual pattern was noticed
  before Q55 was registered.
- Q53 and Q54 are not silently pooled: Q53 has a different recorded-hardware
  sampling object and Q54 lacks a trajectory.

## Reproduction

Run:

```powershell
F:\\SystemFormulaFolder\\.venv_ara_verify\\Scripts\\python.exe `
  analysis\\quantum\\q55_external_octave_transition_audit.py
```

Primary artifacts:

- `Q55_EXTERNAL_OCTAVE_TRANSITION_RESULTS.json`
- `Q55_EXTERNAL_OCTAVE_TRANSITION_RUNS.csv`
- `Q55_EXTERNAL_OCTAVE_TRANSITION_STEPS.csv`
- `Q55_EXTERNAL_OCTAVE_TRANSITION_AUDIT.png`

Frozen protocol:
`Q55_EXTERNAL_OCTAVE_TRANSITION_AUDIT_PROTOCOL_v1_FROZEN.md`.
"""


def main() -> None:
    data = load_visual_data()
    path_rows, paths = build_tables(data)
    run_metrics: dict[str, dict] = {}
    for path_id in ORDER:
        run_metrics[path_id] = {
            threshold_key(t): observed_run_metrics(path_id, paths[path_id], t)
            for t in THRESHOLDS
        }

    rng = np.random.default_rng(SEED)
    generic_null, q52_null = permutation_distributions(paths, rng)
    generic_growth = summarize_growth(run_metrics, generic_null, q52_only=False)
    q52_growth = summarize_growth(run_metrics, q52_null, q52_only=True)
    specificity = summarize_specificity(run_metrics, q52_null, rng)

    primary_growth = generic_growth["00pct"]
    guard_growth = generic_growth["10pct"]
    growth_gate = (
        primary_growth["paths_with_growth"] >= 9
        and primary_growth["median_log2_ratio"] > 0.0
        and primary_growth["permutation_p_median_growth"] <= 0.05
        and guard_growth["paths_with_growth"] >= 9
        and guard_growth["median_log2_ratio"] > 0.0
        and guard_growth["permutation_p_median_growth"] <= 0.05
    )
    primary_q52 = q52_growth["00pct"]
    guard_q52 = q52_growth["10pct"]
    q52_growth_gate = (
        primary_q52["paths_with_growth"] == primary_q52["eligible_paths"] == 8
        and primary_q52["permutation_p_median_growth"] <= 0.05
        and guard_q52["paths_with_growth"] == guard_q52["eligible_paths"] == 8
        and guard_q52["permutation_p_median_growth"] <= 0.05
    )
    primary_spec = specificity["00pct"]
    guard_spec = specificity["10pct"]
    octave_gate = (
        growth_gate
        and primary_spec["best_base"] == "2"
        and primary_spec["base2_permutation_p"] <= 0.05
        and primary_spec["base2_scale_free_mantissa_p"] <= 0.05
        and guard_spec["best_base"] == "2"
        and guard_spec["base2_permutation_p"] <= 0.05
        and guard_spec["base2_scale_free_mantissa_p"] <= 0.05
    )

    all_large = sum(int(np.count_nonzero(paths[p]["large"])) for p in ORDER)
    all_large_cross = sum(
        int(np.count_nonzero(paths[p]["large"] & paths[p]["quadrant_cross"]))
        for p in ORDER
    )
    all_steps = sum(len(paths[p]["step_sizes"]) for p in ORDER)
    all_cross = sum(int(np.count_nonzero(paths[p]["quadrant_cross"])) for p in ORDER)
    positive_movement_association = sum(
        run_metrics[p]["00pct"]["spearman_step_vs_movement"] > 0.0 for p in ORDER
    )

    if octave_gate:
        verdict = "SUPPORTED ×2 OCTAVE TRANSITION (RETROSPECTIVE)"
    elif growth_gate:
        verdict = "SUPPORTED SCALE TRANSITION; ×2 OCTAVE SPECIFICITY NOT SUPPORTED"
    elif q52_growth_gate:
        verdict = "LARGER Q52 POST-BOUNDARY RESPONSE; ×2 OCTAVE NOT SUPPORTED"
    else:
        verdict = "NOT SUPPORTED"

    results = {
        "test_id": "T315/Q55",
        "verdict": verdict,
        "evidence_class": "retrospective / exploratory",
        "source": {
            "visual": str(VISUAL.relative_to(REPO)),
            "visual_sha256": sha256(VISUAL),
            "protocol": str(PROTOCOL.relative_to(REPO)),
            "protocol_sha256": sha256(PROTOCOL),
            "reference_heading_turns": REFERENCE_HEADING,
            "paths": len(ORDER),
            "q52_paths": 8,
            "permutation_draws": DRAWS,
            "seed": SEED,
        },
        "measured_object": (
            "wrapped absolute change in fitted whole-circle external heading "
            "between adjacent source-time bins"
        ),
        "run_metrics": run_metrics,
        "generic_growth": generic_growth,
        "q52_boundary_growth": q52_growth,
        "octave_specificity": specificity,
        "quadrant_summary": {
            "all_steps": all_steps,
            "all_quadrant_transitions": all_cross,
            "all_quadrant_transition_share": safe_ratio(all_cross, all_steps),
            "large_step_threshold_turns": 0.125,
            "large_steps": all_large,
            "large_crossings": all_large_cross,
            "large_crossing_share": safe_ratio(all_large_cross, all_large),
            "paths_with_positive_step_movement_association": int(
                positive_movement_association
            ),
        },
        "gates": {
            "generic_scale_transition": bool(growth_gate),
            "q52_boundary_scale_transition": bool(q52_growth_gate),
            "power_of_two_octave_specificity": bool(octave_gate),
        },
        "boundaries": [
            "The visual pattern was inspected before this audit; Q55 is retrospective.",
            "Q49-Q52 are simulator-derived analyses, not recorded quantum hardware.",
            "The eight Q52 conditions share one historical source construction.",
            "Quadrant crossing is descriptive and not independent octave evidence.",
            "Q53 and Q54 are excluded because their measured trajectory objects differ.",
        ],
    }
    results = clean_json(results)
    RESULTS_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")
    write_csvs(path_rows, paths, run_metrics)
    make_figure(paths, run_metrics, specificity)
    REPORT_MD.write_text(make_report(results), encoding="utf-8")
    print(json.dumps(
        {
            "verdict": verdict,
            "generic_growth": generic_growth["00pct"],
            "generic_growth_10pct": generic_growth["10pct"],
            "q52_growth": q52_growth["00pct"],
            "q52_growth_10pct": q52_growth["10pct"],
            "specificity": specificity["00pct"],
            "specificity_10pct": specificity["10pct"],
            "quadrant": results["quadrant_summary"],
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()
