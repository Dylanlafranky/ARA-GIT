"""Q51 cross-archive external reversal construct-holdout."""

from __future__ import annotations

import hashlib
import json
import math
import pathlib

import numpy as np

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    plt = None

from q49_external_time_vector import build_events, extract_centres
from q50_same_lineage_external_flip_diagnostic import (
    aggregate_coordinate,
    bin_rows,
    circular_distance,
    fixed_lineages,
    group_lineages,
    ordered_classification,
    paired_lineage_summary,
    seed_cluster_bootstrap,
    stratum_rows,
)


HERE = pathlib.Path(__file__).resolve().parent
PUBLIC = HERE / "public_data"
PROTOCOL_PATH = HERE / "Q51_CROSS_ARCHIVE_EXTERNAL_REVERSAL_PROTOCOL_v1_FROZEN.md"
RESULTS_PATH = HERE / "Q51_CROSS_ARCHIVE_EXTERNAL_REVERSAL_RESULTS.json"
FIGURE_PATH = HERE / "Q51_CROSS_ARCHIVE_EXTERNAL_REVERSAL.png"

ARCHIVES = {
    "random": PUBLIC / "q27_network_reconstruction" / "q27_derived_cache.npz",
    "greedy": PUBLIC / "q34_cross_archive_greedy" / "q34_derived_cache.npz",
    "landmax": PUBLIC / "q37_signed_crossing_landmax" / "q37_derived_cache.npz",
    "mimic": PUBLIC / "q38_fixed_anchor_mimic" / "q38_derived_cache.npz",
}
BRANCH_SHORT = {
    "c2_2local connectivity": "c2",
    "c4_2local connectivity": "c4",
}
EPS = 1e-15


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def movement_by_stratum(
    grouped: dict[tuple[int, int], list[dict[str, object]]],
    fixed: set[tuple[int, int]],
    estimator: str,
) -> tuple[dict[str, object], dict[str, object]]:
    development_rows = [
        row
        for key in fixed
        for row in stratum_rows(grouped[key], "development")
    ]
    evaluation_rows = [
        row
        for key in fixed
        for row in stratum_rows(grouped[key], "evaluation")
    ]
    return (
        aggregate_coordinate(development_rows, estimator),
        aggregate_coordinate(evaluation_rows, estimator),
    )


def movement_recovery(
    bins: list[dict[str, object]], ordered: dict[str, object]
) -> dict[str, object]:
    crossing = next(
        (
            item
            for item in ordered["crossings"]
            if item["direction"] == "0_to_2"
        ),
        None,
    )
    if crossing is None:
        return {
            "crossing_available": False,
            "recovery_ratio": math.nan,
            "recovers_25pct": False,
        }
    index = int(crossing["between_bins"][1])
    movement = np.asarray(
        [float(row["mean_relative_movement"]) for row in bins], dtype=np.float64
    )
    pre_indices = [
        value for value in (index - 2, index - 1) if 0 <= value < len(movement)
    ]
    pre = float(np.nanmean(movement[pre_indices]))
    later = movement[index + 1 :]
    later = later[np.isfinite(later)]
    peak = float(np.max(later)) if later.size else math.nan
    ratio = peak / pre if pre > EPS else math.nan
    return {
        "crossing_available": True,
        "crossing_bin_index": index,
        "pre_crossing_two_bin_mean": pre,
        "maximum_later_mean_movement": peak,
        "recovery_ratio": ratio,
        "recovers_25pct": bool(math.isfinite(ratio) and ratio >= 0.25),
    }


def analyse_branch(
    closure: np.ndarray,
    pairs: np.ndarray,
) -> tuple[dict[str, object], dict[str, list[dict[str, object]]]]:
    centres, extraction = extract_centres(closure, pairs)
    events = build_events(centres)
    grouped = group_lineages(events)
    fixed = fixed_lineages(grouped)
    if not fixed:
        empty_bins = {
            estimator: bin_rows(grouped, fixed, estimator)
            for estimator in ("circle", "centroid", "extrema")
        }
        empty_primary = {
            "eligible": False,
            "reason": "No lineage has at least three development and three evaluation events.",
            "centres": len(centres),
            "events": len(events),
            "fixed_lineages": 0,
            "fixed_seeds": 0,
            "gates": {
                "R1_opposing_strata": False,
                "R2_half_turn": False,
                "R3_same_lineage": False,
                "R4_active_movement": False,
                "R5_complete_return": False,
            },
        }
        return (
            {
                "extraction": extraction,
                "primary": empty_primary,
                "estimators": {
                    estimator: empty_primary
                    for estimator in ("circle", "centroid", "extrema")
                },
            },
            empty_bins,
        )
    estimator_results: dict[str, object] = {}
    bins_by_estimator: dict[str, list[dict[str, object]]] = {}
    for estimator in ("circle", "centroid", "extrema"):
        lineage_rows, paired = paired_lineage_summary(grouped, fixed, estimator)
        bootstrap = seed_cluster_bootstrap(lineage_rows)
        development, evaluation = movement_by_stratum(
            grouped, fixed, estimator
        )
        bins = bin_rows(grouped, fixed, estimator)
        bins_by_estimator[estimator] = bins
        ordered = ordered_classification(bins)
        recovery = movement_recovery(bins, ordered)
        separation = circular_distance(
            float(development["heading"]), float(evaluation["heading"])
        )
        dev_mean = float(development["movement"]) / int(development["events"])
        eval_mean = float(evaluation["movement"]) / int(evaluation["events"])
        movement_ratio = eval_mean / dev_mean if dev_mean > EPS else math.nan
        r1 = float(development["x"]) < 1.0 < float(evaluation["x"])
        r2 = abs(separation - 0.5) <= 0.10
        r3 = (
            int(paired["declared_to_opposite"])
            > int(paired["opposite_to_declared"])
            and float(bootstrap["ci95"][0]) > 0.0
        )
        r4 = (
            math.isfinite(movement_ratio)
            and movement_ratio >= 0.10
        ) or bool(recovery["recovers_25pct"])
        r5 = bool(ordered["complete_0_to_2_to_0"])
        estimator_results[estimator] = {
            "eligible": True,
            "centres": len(centres),
            "events": len(events),
            "fixed_lineages": len(fixed),
            "fixed_seeds": len({key[0] for key in fixed}),
            "paired": paired,
            "bootstrap": bootstrap,
            "development": development,
            "evaluation": evaluation,
            "heading_separation_turns": separation,
            "distance_to_half_turn": abs(separation - 0.5),
            "evaluation_to_development_mean_movement_ratio": movement_ratio,
            "ordered": ordered,
            "recovery": recovery,
            "gates": {
                "R1_opposing_strata": bool(r1),
                "R2_half_turn": bool(r2),
                "R3_same_lineage": bool(r3),
                "R4_active_movement": bool(r4),
                "R5_complete_return": bool(r5),
            },
        }
    return (
        {
            "extraction": extraction,
            "primary": estimator_results["circle"],
            "estimators": estimator_results,
        },
        bins_by_estimator,
    )


def make_figure(
    branch_results: dict[str, dict[str, object]],
    branch_bins: dict[str, list[dict[str, object]]],
) -> None:
    if plt is None:
        return
    plt.style.use("seaborn-v0_8-whitegrid")
    strategies = list(ARCHIVES)
    figure, axes = plt.subplots(
        len(strategies),
        2,
        figsize=(15, 13),
        sharex=True,
        sharey=True,
        constrained_layout=True,
    )
    colours = {"c2": "#4C78A8", "c4": "#E45756"}
    for row_index, strategy in enumerate(strategies):
        for column_index, branch in enumerate(("c2", "c4")):
            key = f"{strategy}:{branch}"
            ax = axes[row_index, column_index]
            bins = branch_bins[key]
            eligible = bool(branch_results[key]["primary"].get("eligible", False))
            if not eligible:
                ax.text(
                    0.5,
                    0.5,
                    "NOT TESTABLE\nno lineage spans both halves",
                    ha="center",
                    va="center",
                    transform=ax.transAxes,
                    color="#666666",
                    fontsize=11,
                )
            x = np.asarray([float(item["x"]) for item in bins])
            movement = np.asarray(
                [float(item["mean_relative_movement"]) for item in bins]
            )
            finite = np.isfinite(movement)
            scaled = (
                2.0 * movement / np.nanmax(movement)
                if np.any(finite) and np.nanmax(movement) > 0
                else movement
            )
            ax.plot(
                [item["mid"] for item in bins],
                x,
                marker="o",
                ms=3.5,
                lw=1.8,
                color=colours[branch],
                label="external ARA x",
            )
            ax.plot(
                [item["mid"] for item in bins],
                scaled,
                ls="--",
                lw=1.2,
                color="#666666",
                alpha=0.75,
                label="movement (scaled 0–2)",
            )
            ax.axhline(1.0, color="#222222", lw=1)
            ax.set_ylim(-0.05, 2.05)
            gates = branch_results[key]["primary"]["gates"]
            gate_text = " ".join(
                "P" if gates[f"R{i}_{name}"] else "F"
                for i, name in (
                    (1, "opposing_strata"),
                    (2, "half_turn"),
                    (3, "same_lineage"),
                    (4, "active_movement"),
                    (5, "complete_return"),
                )
            )
            ax.set_title(f"{strategy} · {branch} · R1–R5: {gate_text}")
            if column_index == 0:
                ax.set_ylabel("external directional ARA x")
            if row_index == len(strategies) - 1:
                ax.set_xlabel("source slice")
            if row_index == 0 and column_index == 0:
                ax.legend(fontsize=8, loc="center right")
    figure.suptitle(
        "Q51 — external reversal across network strategies and connectivity branches\n"
        "Solid: directional ARA; dashed: movement magnitude scaled within panel",
        fontsize=16,
        fontweight="bold",
    )
    figure.savefig(FIGURE_PATH, dpi=180)
    plt.close(figure)


def main() -> None:
    archive_results: dict[str, object] = {}
    branch_results: dict[str, dict[str, object]] = {}
    branch_bins: dict[str, list[dict[str, object]]] = {}
    for strategy, path in ARCHIVES.items():
        data = np.load(path, allow_pickle=False)
        closure = np.asarray(data["closure"], dtype=np.float64)
        pairs = np.asarray(data["pairs"], dtype=np.int8)
        names = [str(value) for value in data["branch_names"].tolist()]
        archive_results[strategy] = {
            "path": str(path),
            "sha256": sha256(path),
            "closure_shape": list(closure.shape),
            "branches": names,
        }
        for branch_index, name in enumerate(names):
            short = BRANCH_SHORT[name]
            key = f"{strategy}:{short}"
            print(f"Analysing {key}", flush=True)
            result, bins = analyse_branch(closure[branch_index], pairs)
            result["strategy"] = strategy
            result["branch"] = short
            result["branch_name"] = name
            branch_results[key] = result
            branch_bins[key] = bins["circle"]

    c2_primary = [branch_results[f"{strategy}:c2"]["primary"] for strategy in ARCHIVES]
    orientation_passes = sum(
        all(
            item["gates"][gate]
            for gate in (
                "R1_opposing_strata",
                "R2_half_turn",
                "R3_same_lineage",
            )
        )
        for item in c2_primary
    )
    active_passes = sum(
        all(
            item["gates"][gate]
            for gate in (
                "R1_opposing_strata",
                "R2_half_turn",
                "R3_same_lineage",
                "R4_active_movement",
            )
        )
        for item in c2_primary
    )
    complete_passes = sum(all(item["gates"].values()) for item in c2_primary)
    results = {
        "test": "Q51 cross-archive external reversal replication",
        "status": "CONSTRUCT HOLDOUT; ARCHIVES PREVIOUSLY USED FOR OTHER QUESTIONS",
        "protocol_sha256": sha256(PROTOCOL_PATH),
        "archives": archive_results,
        "branches": branch_results,
        "primary_c2_summary": {
            "strategies": len(ARCHIVES),
            "orientation_reversal_passes": orientation_passes,
            "active_traversal_passes": active_passes,
            "complete_cycle_passes": complete_passes,
            "orientation_reversal_replication": orientation_passes >= 3,
            "active_traversal_replication": active_passes >= 3,
            "complete_cycle_replication": complete_passes >= 3,
        },
        "boundaries": [
            "Previously downloaded simulator archives; not fully blind new data.",
            "External centreline construct was frozen before calculation on these archives.",
            "A repeated residual reversal is not equivalent to an active 0→2→0 wave.",
            "All results concern a deterministic simulator, not hardware.",
        ],
    }
    RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    make_figure(branch_results, branch_bins)
    print(json.dumps(results["primary_c2_summary"], indent=2))


if __name__ == "__main__":
    main()
