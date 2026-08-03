#!/usr/bin/env python3
"""Run T332: frozen Information^3 zipper test at bubble-merger closure."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
from collections import defaultdict
from pathlib import Path

import numpy as np

from bubble_lineage import Bubble, load_run


HERE = Path(__file__).resolve().parents[1]
SOURCE = HERE / "source_data"
RESULTS = HERE / "results"
T329_EVENTS = RESULTS / "T329_ACTUAL_HANDOVER_PHI_SEAM_EVENTS.csv"
PROTOCOL = HERE / "T332_INFORMATION3_ZIPPER_BUBBLE_CLOSURE_PROTOCOL_v1_FROZEN.md"
PREFIX = "T332_INFORMATION3_ZIPPER_BUBBLE_CLOSURE"

MIN_STEP_M = 0.0005
BOOTSTRAPS = 5_000
SEED = 20260803 + 332


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def vector(left: Bubble, right: Bubble) -> np.ndarray:
    return np.asarray([right.x - left.x, right.y - left.y], dtype=float)


def magnitude(value: np.ndarray) -> float:
    return float(np.linalg.norm(value))


def heading(value: np.ndarray) -> float:
    return math.atan2(float(value[1]), float(value[0]))


def circular_separation(left: float, right: float) -> float:
    return abs(math.atan2(math.sin(right - left), math.cos(right - left))) / math.pi


def rankdata(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    start = 0
    while start < len(values):
        end = start + 1
        while end < len(values) and values[order[end]] == values[order[start]]:
            end += 1
        ranks[order[start:end]] = 0.5 * (start + end - 1) + 1.0
        start = end
    return ranks


def spearman(left: list[float] | np.ndarray, right: list[float] | np.ndarray) -> float:
    x = np.asarray(left, dtype=float)
    y = np.asarray(right, dtype=float)
    finite = np.isfinite(x) & np.isfinite(y)
    x = x[finite]
    y = y[finite]
    if len(x) < 3:
        return float("nan")
    rx = rankdata(x)
    ry = rankdata(y)
    if np.std(rx) == 0.0 or np.std(ry) == 0.0:
        return float("nan")
    return float(np.corrcoef(rx, ry)[0, 1])


def read_t329_events() -> list[dict[str, str]]:
    with T329_EVENTS.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def extract_rows() -> tuple[list[dict], dict]:
    source_rows = read_t329_events()
    by_file: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source_rows:
        by_file[row["file"]].append(row)

    output: list[dict] = []
    diagnostics: dict[str, int] = defaultdict(int)
    for filename, event_rows in sorted(by_file.items()):
        run = load_run(SOURCE / filename)
        for item in sorted(event_rows, key=lambda row: int(row["frame"])):
            split = item["split"]
            frame = int(item["frame"])
            inherited_id = int(item["inherited_id"])
            joining_id = int(item["joining_id"])
            inherited = run.tracks[inherited_id]
            joining = run.tracks[joining_id]
            diagnostics[f"{split}_source"] += 1

            required_i = (frame - 1, frame, frame + 1, frame + 2, frame + 3)
            required_j = (frame - 1, frame)
            if any(value not in inherited for value in required_i) or any(
                value not in joining for value in required_j
            ):
                diagnostics[f"{split}_missing_primary_window"] += 1
                continue

            v_i = vector(inherited[frame - 1], inherited[frame])
            v_j = vector(joining[frame - 1], joining[frame])
            v_p1 = vector(inherited[frame + 1], inherited[frame + 2])
            v_p2 = vector(inherited[frame + 2], inherited[frame + 3])
            magnitudes = [magnitude(value) for value in (v_i, v_j, v_p1, v_p2)]
            if any(value < MIN_STEP_M for value in magnitudes):
                diagnostics[f"{split}_subresolution_primary_window"] += 1
                continue

            theta_i = heading(v_i)
            theta_j = heading(v_j)
            theta_p1 = heading(v_p1)
            theta_p2 = heading(v_p2)
            f_child = circular_separation(theta_i, theta_j)
            f_parent = circular_separation(theta_p1, theta_p2)

            f_ordinary = float("nan")
            event_specificity = float("nan")
            if frame - 2 in inherited:
                v_previous = vector(inherited[frame - 2], inherited[frame - 1])
                if magnitude(v_previous) >= MIN_STEP_M:
                    f_ordinary = circular_separation(heading(v_previous), theta_i)
                    event_specificity = f_ordinary - f_parent
                    diagnostics[f"{split}_ordinary_control"] += 1

            output.append(
                {
                    "split": split,
                    "video": item["video"],
                    "file": filename,
                    "amplitude": run.amplitude,
                    "umf": run.umf,
                    "frame": frame,
                    "inherited_id": inherited_id,
                    "joining_id": joining_id,
                    "f_child": f_child,
                    "f_parent": f_parent,
                    "zipper_contraction": f_child - f_parent,
                    "f_ordinary": f_ordinary,
                    "event_specificity": event_specificity,
                    "theta_inherited_pre": theta_i,
                    "theta_joining_pre": theta_j,
                    "theta_parent_first": theta_p1,
                    "theta_parent_second": theta_p2,
                    "inherited_pre_step_m": magnitudes[0],
                    "joining_pre_step_m": magnitudes[1],
                    "parent_first_step_m": magnitudes[2],
                    "parent_second_step_m": magnitudes[3],
                }
            )
            diagnostics[f"{split}_eligible_primary"] += 1

    diagnostics["total_eligible_primary"] = len(output)
    return output, dict(diagnostics)


def summarize(values: list[float]) -> dict:
    array = np.asarray([value for value in values if math.isfinite(value)], dtype=float)
    return {
        "n": int(len(array)),
        "mean": float(np.mean(array)) if len(array) else float("nan"),
        "median": float(np.median(array)) if len(array) else float("nan"),
        "q25": float(np.quantile(array, 0.25)) if len(array) else float("nan"),
        "q75": float(np.quantile(array, 0.75)) if len(array) else float("nan"),
        "positive_share": float(np.mean(array > 0.0)) if len(array) else float("nan"),
    }


def cluster_bootstrap_mean(
    rows: list[dict], field: str, *, seed_offset: int
) -> tuple[float, float, np.ndarray]:
    by_video: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        value = float(row[field])
        if math.isfinite(value):
            by_video[row["video"]].append(value)
    videos = sorted(by_video)
    rng = np.random.default_rng(SEED + seed_offset)
    draws: list[float] = []
    for _ in range(BOOTSTRAPS):
        selected = rng.choice(videos, size=len(videos), replace=True)
        sample = [value for video in selected for value in by_video[str(video)]]
        draws.append(float(np.mean(sample)))
    array = np.asarray(draws, dtype=float)
    return float(np.quantile(array, 0.025)), float(np.quantile(array, 0.975)), array


def residual_rows(rows: list[dict]) -> list[dict]:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[row["video"]] += 1
    return [row for row in rows if counts[row["video"]] >= 2]


def cluster_bootstrap_spearman(
    rows: list[dict], *, seed_offset: int
) -> tuple[float, float, np.ndarray]:
    by_video: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_video[row["video"]].append(row)
    videos = sorted(by_video)
    rng = np.random.default_rng(SEED + seed_offset)
    draws: list[float] = []
    for _ in range(BOOTSTRAPS):
        selected = rng.choice(videos, size=len(videos), replace=True)
        sample = [row for video in selected for row in by_video[str(video)]]
        value = spearman(
            [float(row["f_child"]) for row in sample],
            [float(row["f_parent"]) for row in sample],
        )
        if math.isfinite(value):
            draws.append(value)
    array = np.asarray(draws, dtype=float)
    if not len(array):
        return float("nan"), float("nan"), array
    return float(np.quantile(array, 0.025)), float(np.quantile(array, 0.975)), array


def cyclic_residual_null(rows: list[dict], *, seed_offset: int) -> np.ndarray:
    by_video: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_video[row["video"]].append(row)
    for group in by_video.values():
        group.sort(key=lambda row: (int(row["frame"]), int(row["inherited_id"])))

    rng = np.random.default_rng(SEED + seed_offset)
    draws: list[float] = []
    for _ in range(BOOTSTRAPS):
        child: list[float] = []
        shifted_parent: list[float] = []
        for video in sorted(by_video):
            group = by_video[video]
            shift = int(rng.integers(1, len(group)))
            parent = [float(row["f_parent"]) for row in group]
            child.extend(float(row["f_child"]) for row in group)
            shifted_parent.extend(parent[shift:] + parent[:shift])
        value = spearman(child, shifted_parent)
        if math.isfinite(value):
            draws.append(value)
    return np.asarray(draws, dtype=float)


def split_rows(rows: list[dict], split: str) -> list[dict]:
    return [row for row in rows if row["split"] == split]


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"No rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build_figure(rows: list[dict], null: np.ndarray, observed_rho: float, output: Path) -> None:
    os.environ.setdefault("MPLCONFIGDIR", str(HERE / ".mplconfig"))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    blue = "#3F76B5"
    gold = "#D89B2B"
    ink = "#29313D"
    grid = "#D9DEE6"
    pale = "#EEF2F7"
    split_colors = {"calibration": "#8AA7C8", "evaluation": blue, "holdout": gold}

    fig, axes = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=False)
    fig.subplots_adjust(left=0.07, right=0.985, bottom=0.075, top=0.86, wspace=0.13, hspace=0.27)
    fig.patch.set_facecolor("#FAFBFD")
    for axis in axes.ravel():
        axis.set_facecolor("#FFFFFF")
        axis.grid(True, color=grid, linewidth=0.8, alpha=0.7)
        axis.tick_params(colors=ink)
        for spine in axis.spines.values():
            spine.set_color("#AEB7C4")

    # Panel 1: same-grain freedom before and after.
    axis = axes[0, 0]
    splits = ["calibration", "evaluation", "holdout"]
    for index, split in enumerate(splits):
        group = split_rows(rows, split)
        child = np.asarray([row["f_child"] for row in group], dtype=float)
        parent = np.asarray([row["f_parent"] for row in group], dtype=float)
        x0 = index * 3.0
        for left, right in zip(child, parent):
            axis.plot([x0, x0 + 1], [left, right], color="#C9D1DC", alpha=0.32, linewidth=0.8)
        axis.scatter([x0] * len(child), child, s=16, color=blue, alpha=0.55, zorder=2)
        axis.scatter([x0 + 1] * len(parent), parent, s=16, color=gold, alpha=0.55, zorder=2)
        axis.plot([x0, x0 + 1], [np.mean(child), np.mean(parent)], color=ink, linewidth=3, zorder=3)
        axis.scatter([x0, x0 + 1], [np.mean(child), np.mean(parent)], s=55, color=ink, zorder=4)
    axis.set_xticks([0, 1, 3, 4, 6, 7])
    axis.set_xticklabels(["child", "parent"] * 3)
    for index, split in enumerate(splits):
        axis.text(index * 3 + 0.5, 1.035, split, ha="center", va="bottom", color=ink, fontsize=10)
    axis.set_ylim(-0.03, 1.08)
    axis.set_ylabel("directional freedom (ARA half-turns)")
    axis.set_title("Child relation and parent turning", loc="left", color=ink, weight="bold")

    # Panel 2: evaluation relation.
    axis = axes[0, 1]
    evaluation = split_rows(rows, "evaluation")
    x = np.asarray([row["f_child"] for row in evaluation], dtype=float)
    y = np.asarray([row["f_parent"] for row in evaluation], dtype=float)
    axis.scatter(x, y, s=42, color=blue, alpha=0.72, edgecolor="white", linewidth=0.5)
    axis.plot([0, 1], [0, 1], color=ink, linestyle="--", linewidth=1.3, label="no contraction")
    axis.set_xlim(-0.03, 1.03)
    axis.set_ylim(-0.03, 1.03)
    axis.set_xlabel("pre-merger child freedom")
    axis.set_ylabel("post-merger parent freedom")
    axis.set_title("Evaluation seam-level contraction", loc="left", color=ink, weight="bold")
    axis.legend(frameon=False, loc="upper left")

    # Panel 3: post-result forcing-condition diagnostic.
    axis = axes[1, 0]
    amplitudes = sorted({float(row["amplitude"]) for row in rows})
    values = [
        np.asarray(
            [row["zipper_contraction"] for row in rows if float(row["amplitude"]) == amplitude]
        )
        for amplitude in amplitudes
    ]
    labels = [f"{value:g}" for value in amplitudes]
    box = axis.boxplot(values, tick_labels=labels, patch_artist=True, showfliers=False, widths=0.55)
    amplitude_colors = ["#B7C9DD", "#91B0D2", blue, "#DDB66C", gold]
    for patch, color in zip(box["boxes"], amplitude_colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
        patch.set_edgecolor(ink)
    for key in ("whiskers", "caps", "medians"):
        for item in box[key]:
            item.set_color(ink)
    axis.axhline(0.0, color=ink, linestyle="--", linewidth=1.2)
    axis.set_ylabel("Z = child freedom − parent freedom")
    axis.set_xlabel("forcing amplitude setting")
    axis.set_title("Contraction by forcing amplitude", loc="left", color=ink, weight="bold")

    # Panel 4: residual correlation null.
    axis = axes[1, 1]
    axis.hist(null, bins=35, color="#A9B4C2", edgecolor="white", linewidth=0.5)
    axis.axvline(observed_rho, color=gold, linewidth=3, label=f"observed ρ = {observed_rho:.3f}")
    axis.axvline(0.0, color=ink, linestyle="--", linewidth=1.2)
    axis.set_xlabel("Spearman ρ after within-video cyclic shift")
    axis.set_ylabel("null draws")
    axis.set_title("Evaluation residual-inheritance control", loc="left", color=ink, weight="bold")
    axis.legend(frameon=False, loc="upper left")

    fig.suptitle(
        "T332 — Information³ zipper at bubble-merger closure",
        fontsize=18,
        color=ink,
        weight="bold",
        x=0.02,
        ha="left",
    )
    fig.text(
        0.02,
        0.935,
        "91 independently detected merger seams · frozen local-contraction gate not supported",
        fontsize=10.5,
        color="#5F6978",
        ha="left",
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)


def format_ci(record: dict) -> str:
    return f"[{record['ci_low']:+.6f}, {record['ci_high']:+.6f}]"


def main() -> None:
    rows, diagnostics = extract_rows()
    RESULTS.mkdir(parents=True, exist_ok=True)

    summaries: dict[str, dict] = {}
    bootstrap_rows: list[dict] = []
    residual: dict[str, dict] = {}
    null_by_split: dict[str, np.ndarray] = {}

    for split_index, split in enumerate(("calibration", "evaluation", "holdout")):
        group = split_rows(rows, split)
        split_summary: dict[str, dict] = {}
        for field_index, field in enumerate(("f_child", "f_parent", "zipper_contraction")):
            record = summarize([float(row[field]) for row in group])
            if field == "zipper_contraction":
                low, high, _ = cluster_bootstrap_mean(
                    group, field, seed_offset=100 * split_index + field_index
                )
                record.update({"ci_low": low, "ci_high": high})
                bootstrap_rows.append(
                    {
                        "split": split,
                        "metric": field,
                        "mean": record["mean"],
                        "ci_low": low,
                        "ci_high": high,
                        "n": record["n"],
                    }
                )
            split_summary[field] = record

        ordinary = [row for row in group if math.isfinite(float(row["event_specificity"]))]
        event_record = summarize([float(row["event_specificity"]) for row in ordinary])
        low, high, _ = cluster_bootstrap_mean(
            ordinary, "event_specificity", seed_offset=500 + split_index
        )
        event_record.update({"ci_low": low, "ci_high": high})
        split_summary["event_specificity"] = event_record
        bootstrap_rows.append(
            {
                "split": split,
                "metric": "event_specificity",
                "mean": event_record["mean"],
                "ci_low": low,
                "ci_high": high,
                "n": event_record["n"],
            }
        )

        residual_group = residual_rows(group)
        rho = spearman(
            [float(row["f_child"]) for row in residual_group],
            [float(row["f_parent"]) for row in residual_group],
        )
        rho_low, rho_high, _ = cluster_bootstrap_spearman(
            residual_group, seed_offset=900 + split_index
        )
        null = cyclic_residual_null(residual_group, seed_offset=1200 + split_index)
        null_by_split[split] = null
        p_one_sided = float((1 + np.sum(null >= rho)) / (len(null) + 1))
        residual[split] = {
            "n": len(residual_group),
            "videos": len({row["video"] for row in residual_group}),
            "spearman": rho,
            "ci_low": rho_low,
            "ci_high": rho_high,
            "cyclic_null_mean": float(np.mean(null)),
            "cyclic_null_q025": float(np.quantile(null, 0.025)),
            "cyclic_null_q975": float(np.quantile(null, 0.975)),
            "p_one_sided": p_one_sided,
        }
        summaries[split] = split_summary

    amplitude_summary: dict[str, dict] = {}
    for amplitude_index, amplitude in enumerate(sorted({float(row["amplitude"]) for row in rows})):
        group = [row for row in rows if float(row["amplitude"]) == amplitude]
        record = summarize([float(row["zipper_contraction"]) for row in group])
        low, high, _ = cluster_bootstrap_mean(
            group, "zipper_contraction", seed_offset=1500 + amplitude_index
        )
        record.update({"ci_low": low, "ci_high": high})
        amplitude_summary[f"{amplitude:g}"] = record

    evaluation = summaries["evaluation"]
    holdout = summaries["holdout"]
    gate1 = (
        evaluation["zipper_contraction"]["ci_low"] > 0.0
        and holdout["zipper_contraction"]["mean"] > 0.0
    )
    gate2 = (
        evaluation["event_specificity"]["ci_low"] > 0.0
        and holdout["event_specificity"]["mean"] > 0.0
    )
    gate3 = (
        residual["evaluation"]["spearman"] > 0.0
        and residual["evaluation"]["ci_low"] > 0.0
        and residual["evaluation"]["p_one_sided"] < 0.05
        and residual["holdout"]["spearman"] > 0.0
    )

    if not gate1:
        verdict = "NOT SUPPORTED — LOCAL ZIPPER CONTRACTION"
    elif not gate2:
        verdict = "CONTRACTION OBSERVED — EVENT SPECIFICITY NOT SUPPORTED"
    elif not gate3:
        verdict = "CLOSURE CONTRACTION SUPPORTED — IMMEDIATE RESIDUAL INHERITANCE NOT SUPPORTED"
    else:
        verdict = "CLOSURE CONTRACTION AND IMMEDIATE RESIDUAL INHERITANCE SUPPORTED"

    event_path = RESULTS / f"{PREFIX}_EVENTS.csv"
    bootstrap_path = RESULTS / f"{PREFIX}_BOOTSTRAP_SUMMARY.csv"
    null_path = RESULTS / f"{PREFIX}_EVALUATION_RESIDUAL_NULL.csv"
    result_path = HERE / f"{PREFIX}_RESULTS.json"
    report_path = HERE / f"{PREFIX}_REPORT_2026-08-03.md"
    figure_path = HERE / f"{PREFIX}_FIGURE.png"

    write_csv(event_path, rows)
    write_csv(bootstrap_path, bootstrap_rows)
    write_csv(
        null_path,
        [{"draw": index, "spearman": float(value)} for index, value in enumerate(null_by_split["evaluation"])],
    )
    build_figure(
        rows,
        null_by_split["evaluation"],
        residual["evaluation"]["spearman"],
        figure_path,
    )

    result = {
        "test": "T332 Information3 zipper at bubble-merger closure",
        "run_date": "2026-08-03",
        "verdict": verdict,
        "protocol": PROTOCOL.name,
        "protocol_sha256": sha256(PROTOCOL),
        "source_t329_events_sha256": sha256(T329_EVENTS),
        "constants": {
            "min_step_m": MIN_STEP_M,
            "bootstraps": BOOTSTRAPS,
            "seed": SEED,
        },
        "diagnostics": diagnostics,
        "summaries": summaries,
        "residual_inheritance": residual,
        "post_result_amplitude_summary": amplitude_summary,
        "gates": {
            "local_contraction": gate1,
            "event_specificity": gate2,
            "immediate_residual_inheritance": gate3,
            "later_ordered_closure_available": False,
            "full_information3_zipper_confirmed": False,
        },
        "boundaries": [
            "This is a post-result mechanism probe in a previously used bubble archive.",
            "F_child is inter-child disagreement; F_parent is intra-parent turning.",
            "The metric is magnitude-only, so reversal is non-discriminating.",
            "No Phi, 3/8, 1/e or rational-grid target was scored.",
            "Only three repeated primary merger lineages exist; later seam timing is not inferentially testable.",
        ],
        "artifacts": {
            "events": event_path.name,
            "bootstrap_summary": bootstrap_path.name,
            "evaluation_residual_null": null_path.name,
            "figure": figure_path.name,
            "report": report_path.name,
        },
    }
    result_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    eval_z = summaries["evaluation"]["zipper_contraction"]
    hold_z = summaries["holdout"]["zipper_contraction"]
    eval_e = summaries["evaluation"]["event_specificity"]
    hold_e = summaries["holdout"]["event_specificity"]
    eval_r = residual["evaluation"]
    hold_r = residual["holdout"]

    report = f"""# T332 Information³ zipper at bubble-merger closure

**Run date:** 3 August 2026  
**Frozen protocol:** `{PROTOCOL.name}`  
**Verdict:** **{verdict}**

## Technical summary

T332 asked whether an independently detected two-child-to-one-parent merger
compresses directional freedom, whether that change exceeds ordinary local
persistence, and whether the remaining post-merger freedom still carries the
rank ordering of the pre-merger child relation.

The local contraction gate was **{'passed' if gate1 else 'not passed'}**. In
evaluation, mean `Z = F_child - F_parent` was `{eval_z['mean']:+.6f}` with a
95% whole-video interval of `{format_ci(eval_z)}`. Holdout mean `Z` was
`{hold_z['mean']:+.6f}`.

The event-specificity gate was **{'passed' if gate2 else 'not passed'}**. In
evaluation, the parent turn was smaller than the inherited lineage's prior
ordinary turn by mean `{eval_e['mean']:+.6f}` with interval
`{format_ci(eval_e)}`. Holdout mean was `{hold_e['mean']:+.6f}`.

Immediate residual inheritance was **{'supported' if gate3 else 'not supported'}**.
Evaluation Spearman `rho` was `{eval_r['spearman']:+.6f}` with interval
`[{eval_r['ci_low']:+.6f}, {eval_r['ci_high']:+.6f}]` and one-sided cyclic-null
`p={eval_r['p_one_sided']:.6f}`. Holdout `rho` was
`{hold_r['spearman']:+.6f}`.

The full Information³ zipper remains unconfirmed under every outcome because
only three repeated merger lineages are available; later closure timing cannot
be inferred from this archive.

## The measurable zipper result

The primary comparison uses the same two-vector angular grain on each side of
the merger. `F_child` is the disagreement between the inherited and joining
child headings immediately before contact. `F_parent` is the turn between the
new parent's first two resolved outgoing headings. Positive `Z` means the
relation became directionally tighter after closure.

| split | events | mean child freedom | mean parent freedom | mean Z | 95% video interval | positive share |
|---|---:|---:|---:|---:|---:|---:|
"""
    for split in ("calibration", "evaluation", "holdout"):
        child = summaries[split]["f_child"]
        parent = summaries[split]["f_parent"]
        zipper = summaries[split]["zipper_contraction"]
        report += (
            f"| {split} | {zipper['n']} | {child['mean']:.6f} | {parent['mean']:.6f} | "
            f"{zipper['mean']:+.6f} | {format_ci(zipper)} | {zipper['positive_share']:.3f} |\n"
        )

    report += f"""

![T332 zipper diagnostics]({figure_path.name})

## The failure changes with forcing condition

The negative result is not uniform across the archive. The low-amplitude files
lean toward contraction, whereas the two highest settings lean toward
expansion. This is a post-result descriptive cut, not a frozen gate. Amplitude
is also confounded with the calibration/evaluation/holdout split, so it cannot
identify a cause or rescue the failed universal prediction.

| forcing amplitude | events | mean Z | median Z | 95% video interval | positive share |
|---:|---:|---:|---:|---:|---:|
"""
    for amplitude, record in amplitude_summary.items():
        report += (
            f"| {amplitude} | {record['n']} | {record['mean']:+.6f} | "
            f"{record['median']:+.6f} | {format_ci(record)} | {record['positive_share']:.3f} |\n"
        )

    report += """

## Ordinary-turn control

The event-specificity control compares the post-merger parent turn with the
same inherited lineage's immediately preceding ordinary turn. It is available
for 20 calibration, 42 evaluation and 11 holdout events.

| split | events | mean ordinary-minus-parent | 95% video interval | positive share |
|---|---:|---:|---:|---:|
"""
    for split in ("calibration", "evaluation", "holdout"):
        record = summaries[split]["event_specificity"]
        report += (
            f"| {split} | {record['n']} | {record['mean']:+.6f} | "
            f"{format_ci(record)} | {record['positive_share']:.3f} |\n"
        )

    report += """

## Residual-inheritance control

The residual test asks a stricter question than contraction: after the parent
tightens, do events with more child disagreement retain more parent turning?
Singleton videos are excluded because their lineage pairing cannot be broken.
The observed Spearman correlation is compared with within-video cyclic shifts
of the parent values.

| split | events | videos | observed rho | 95% video interval | cyclic-null mean | one-sided p |
|---|---:|---:|---:|---:|---:|---:|
"""
    for split in ("calibration", "evaluation", "holdout"):
        record = residual[split]
        report += (
            f"| {split} | {record['n']} | {record['videos']} | {record['spearman']:+.6f} | "
            f"[{record['ci_low']:+.6f}, {record['ci_high']:+.6f}] | "
            f"{record['cyclic_null_mean']:+.6f} | {record['p_one_sided']:.6f} |\n"
        )

    report += f"""

## Scope, definitions and limitations

- `F_child` and `F_parent` share units and two-vector grain, but they are not
  identical physical observables: one is between children and one is within
  the parent.
- The analysis uses released centroids without smoothing, Fourier processing,
  trajectory fitting or Phi-target selection.
- A positive merger-aligned contraction is descriptive. The ordinary-turn
  control is required before calling it event-specific.
- Circular-separation magnitude is symmetric under time/order reversal, so
  this test makes no directional zipper claim.
- The holdout has 16 events across three videos and is directional only.
- The archive cannot test the next-seam timing prediction. A longer archive
  with repeated mergers along the same inherited lineage is required.

## Recommended next step

Do not move this failed coordinate to a Phi or rational-spacing target. Freeze
a balanced-forcing replication that estimates the sign of `Z` at several
forcing settings within the same acquisition regime. Separately, seek a bubble
archive with at least 20 repeated merger lineages before testing ordered later
reclosure. A signed orientation coordinate may be tested as a different ARA
cut, but it must be registered independently of T332.

## Reproduction

- production: `work/run_t332_information3_zipper_bubble_closure.py`
- independent validation: `work/validate_t332_information3_zipper_bubble_closure.py`
- events: `results/{event_path.name}`
- bootstrap summary: `results/{bootstrap_path.name}`
- residual null: `results/{null_path.name}`
- result JSON: `{result_path.name}`
- figure: `{figure_path.name}`
"""
    report_path.write_text(report, encoding="utf-8")

    print(json.dumps({"verdict": verdict, "gates": result["gates"], "summaries": summaries, "residual": residual}, indent=2))


if __name__ == "__main__":
    main()
