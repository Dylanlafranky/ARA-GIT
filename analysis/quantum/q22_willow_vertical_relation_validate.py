#!/usr/bin/env python3
"""Independent arithmetic and provenance validation for Q22."""

from __future__ import annotations

import hashlib
import json
import pathlib

import numpy as np

from q22_willow_vertical_relation_features import (
    GEOMETRY_ROOT,
    build_feature_sets,
    load_geometry_dataset,
)


ROOT = pathlib.Path(__file__).parent
RESULTS = ROOT / "Q22_WILLOW_VERTICAL_TIER4_TIER1_RESULTS.json"
CALIBRATION = ROOT / "Q22_WILLOW_VERTICAL_RELATION_CALIBRATION.json"
FREEZE = ROOT / "Q22_WILLOW_VERTICAL_TIER4_TIER1_FREEZE_MANIFEST.json"
OUTCOME_ROOT = (
    ROOT
    / "public_data"
    / "q22_willow_105q_outcomes"
    / "d5_at_q6_9"
)
OUTCOME_MANIFEST = (
    ROOT
    / "public_data"
    / "q22_willow_105q_outcomes"
    / "SOURCE_MANIFEST.json"
)
OUTPUT = ROOT / "Q22_WILLOW_VERTICAL_TIER4_TIER1_VALIDATION.json"
MODELS = (
    "vertical_state",
    "vertical_travel",
    "vertical_both",
    "past_travel_control",
    "broken_vertical_both",
    "q21_child_topology",
    "event_fraction",
    "vertical_both_plus_count",
)


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def labels(path: pathlib.Path, shots: int) -> np.ndarray:
    packed = np.fromfile(path, dtype=np.uint8)
    if packed.size != shots or np.any(packed & 0b11111110):
        raise ValueError(f"Invalid label file: {path}")
    return (packed & 1).astype(np.uint8)


def auc(y: np.ndarray, score: np.ndarray) -> float:
    order = np.argsort(score, kind="mergesort")
    sorted_score = score[order]
    ranks = np.empty(score.size, dtype=np.float64)
    start = 0
    while start < score.size:
        stop = start + 1
        while stop < score.size and sorted_score[stop] == sorted_score[start]:
            stop += 1
        ranks[order[start:stop]] = (start + 1 + stop) / 2.0
        start = stop
    positive = y == 1
    n1 = int(positive.sum())
    n0 = int((~positive).sum())
    return float(
        (ranks[positive].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0)
    )


def independent_score(
    development: np.ndarray,
    development_labels: np.ndarray,
    holdout: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    mean = development.mean(axis=0)
    sd = development.std(axis=0)
    z_development = (development - mean) / sd
    z_holdout = (holdout - mean) / sd
    zero = z_development[development_labels == 0].mean(axis=0)
    one = z_development[development_labels == 1].mean(axis=0)
    direction = one - zero
    midpoint = (zero + one) / 2.0
    return (
        (z_development - midpoint) @ direction,
        (z_holdout - midpoint) @ direction,
    )


def check(
    checks: list[dict], name: str, passed: bool, detail: object
) -> None:
    checks.append({"check": name, "passed": bool(passed), "detail": detail})


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    calibration = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    checks: list[dict] = []

    for relative, expected in freeze["frozen_files_sha256"].items():
        actual = sha256(ROOT / relative)
        check(
            checks,
            f"freeze::{relative}",
            actual == expected,
            {"expected": expected, "actual": actual},
        )
    check(
        checks,
        "geometry_tree_has_no_outcomes",
        not list(GEOMETRY_ROOT.rglob("obs_flips_actual.b8")),
        0,
    )
    outcome_manifest = json.loads(
        OUTCOME_MANIFEST.read_text(encoding="utf-8")
    )
    check(
        checks,
        "outcome_manifest_has_exactly_four_labels",
        outcome_manifest["stage"] == "outcomes"
        and len(outcome_manifest["members"]) == 4
        and all(
            item["name"].endswith("/obs_flips_actual.b8")
            for item in outcome_manifest["members"]
        ),
        [item["name"] for item in outcome_manifest["members"]],
    )
    check(
        checks,
        "calibration_checksum",
        sha256(CALIBRATION) == result["calibration_sha256"],
        sha256(CALIBRATION),
    )
    check(
        checks,
        "outcome_manifest_checksum",
        sha256(OUTCOME_MANIFEST) == result["outcome_manifest_sha256"],
        sha256(OUTCOME_MANIFEST),
    )
    check(
        checks,
        "calibration_outcome_blind",
        calibration["outcome_blind"],
        calibration["outcome_blind"],
    )
    check(
        checks,
        "calibration_construction_passed",
        calibration["all_construction_checks_pass"],
        calibration["all_construction_checks_pass"],
    )

    recalculated_auc: dict[str, dict[str, float]] = {
        name: {} for name in MODELS
    }
    recalculated_development_auc: dict[str, dict[str, float]] = {
        name: {} for name in MODELS
    }
    for basis in ("X", "Z"):
        dev_detectors, dev_coordinates, dev_weights, dev_meta = (
            load_geometry_dataset(basis, "r13")
        )
        hold_detectors, hold_coordinates, hold_weights, hold_meta = (
            load_geometry_dataset(basis, "r30")
        )
        dev_features, dev_quality = build_feature_sets(
            dev_detectors, dev_coordinates, dev_weights
        )
        hold_features, hold_quality = build_feature_sets(
            hold_detectors, hold_coordinates, hold_weights
        )
        y_dev = labels(
            OUTCOME_ROOT / basis / "r13" / "obs_flips_actual.b8",
            int(dev_meta["shots"]),
        )
        y_hold = labels(
            OUTCOME_ROOT / basis / "r30" / "obs_flips_actual.b8",
            int(hold_meta["shots"]),
        )

        for name in MODELS:
            dev_score, hold_score = independent_score(
                dev_features[name], y_dev, hold_features[name]
            )
            dev_auc = auc(y_dev, dev_score)
            hold_auc = auc(y_hold, hold_score)
            recalculated_development_auc[name][basis] = dev_auc
            recalculated_auc[name][basis] = hold_auc
            recorded = result["holdout_auroc"][name][basis]
            check(
                checks,
                f"auroc::{basis}::{name}",
                abs(hold_auc - recorded) <= 1e-12,
                {"recorded": recorded, "recalculated": hold_auc},
            )

        recorded_quality = calibration["datasets"][f"{basis}_r30"][
            "quality"
        ]
        for field in (
            "future_ridge_distance_mean",
            "past_ridge_distance_mean",
            "broken_future_ridge_distance_mean",
        ):
            check(
                checks,
                f"geometry::{basis}::{field}",
                abs(hold_quality[field] - recorded_quality[field]) <= 1e-12,
                {
                    "recorded": recorded_quality[field],
                    "recalculated": hold_quality[field],
                },
            )
        for quality, split in ((dev_quality, "r13"), (hold_quality, "r30")):
            check(
                checks,
                f"bounds::{basis}::{split}",
                quality["tier1_min"] >= -1e-12
                and quality["tier1_max"] <= 2.0 + 1e-12
                and quality["tier4_min"] >= -1e-12
                and quality["tier4_max"] <= 2.0 + 1e-12,
                {
                    "tier1": [quality["tier1_min"], quality["tier1_max"]],
                    "tier4": [quality["tier4_min"], quality["tier4_max"]],
                },
            )

    mean_auc = {
        name: float(np.mean(list(values.values())))
        for name, values in recalculated_auc.items()
    }
    geometry = {
        basis: calibration["datasets"][f"{basis}_r30"]["quality"]
        for basis in ("X", "Z")
    }
    reconstructed_gates = {
        "future_closer_than_past_both_holdout_bases": all(
            q["future_ridge_distance_mean"] < q["past_ridge_distance_mean"]
            for q in geometry.values()
        ),
        "future_closer_than_broken_future_both_holdout_bases": all(
            q["future_ridge_distance_mean"]
            < q["broken_future_ridge_distance_mean"]
            for q in geometry.values()
        ),
        "vertical_state_auroc_at_least_0_52_both_bases": all(
            value >= 0.52
            for value in recalculated_auc["vertical_state"].values()
        ),
        "vertical_travel_auroc_at_least_0_52_both_bases": all(
            value >= 0.52
            for value in recalculated_auc["vertical_travel"].values()
        ),
        "vertical_both_auroc_at_least_0_55_both_bases": all(
            value >= 0.55
            for value in recalculated_auc["vertical_both"].values()
        ),
        "mean_vertical_both_minus_q21_at_least_0_01": (
            mean_auc["vertical_both"] - mean_auc["q21_child_topology"]
            >= 0.01
        ),
        "mean_vertical_both_minus_count_at_least_0_01": (
            mean_auc["vertical_both"] - mean_auc["event_fraction"] >= 0.01
        ),
        "mean_vertical_both_minus_past_at_least_0_01": (
            mean_auc["vertical_both"] - mean_auc["past_travel_control"]
            >= 0.01
        ),
        "mean_vertical_both_minus_broken_at_least_0_01": (
            mean_auc["vertical_both"] - mean_auc["broken_vertical_both"]
            >= 0.01
        ),
        "permutation_p_at_most_0_01_both_bases": all(
            row["one_sided_empirical_p"] <= 0.01
            for row in result["permutation_controls"]
        ),
        "count_changes_mean_auroc_by_less_than_0_01": abs(
            mean_auc["vertical_both_plus_count"] - mean_auc["vertical_both"]
        )
        < 0.01,
        "vertical_both_direction_concordant_both_bases": all(
            recalculated_development_auc["vertical_both"][basis] >= 0.5
            and recalculated_auc["vertical_both"][basis] >= 0.5
            for basis in ("X", "Z")
        ),
    }
    for name, recorded in result["gates"].items():
        check(
            checks,
            f"gate::{name}",
            reconstructed_gates[name] == recorded,
            {
                "recorded": recorded,
                "recalculated": reconstructed_gates[name],
            },
        )
    check(
        checks,
        "gate_count",
        sum(reconstructed_gates.values()) == result["gate_count_passed"],
        {
            "recorded": result["gate_count_passed"],
            "recalculated": sum(reconstructed_gates.values()),
        },
    )
    check(
        checks,
        "strict_verdict",
        result["overall_verdict"]
        == (
            "SUPPORTED"
            if all(reconstructed_gates.values())
            else "NOT SUPPORTED"
        ),
        result["overall_verdict"],
    )
    for row in result["permutation_controls"]:
        check(
            checks,
            f"permutation_summary::{row['basis']}",
            row["count"] == 999
            and row["seed"] == 20260726
            and 0.001 <= row["one_sided_empirical_p"] <= 1.0
            and row["null_sd_auroc"] > 0,
            row,
        )

    passed = sum(item["passed"] for item in checks)
    validation = {
        "test": "Q22",
        "validation_status": (
            "PASS" if passed == len(checks) else "NEEDS REVISION"
        ),
        "checks_passed": int(passed),
        "checks_total": int(len(checks)),
        "independent_recalculated_holdout_auroc": recalculated_auc,
        "independent_recalculated_development_auroc": (
            recalculated_development_auc
        ),
        "reconstructed_gates": reconstructed_gates,
        "checks": checks,
        "caveat": (
            "The 999 individual permutation AUROCs were not persisted, so "
            "their reported aggregate statistics are provenance-checked but "
            "not independently reconstructed."
        ),
    }
    OUTPUT.write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        validation["validation_status"],
        f"{passed}/{len(checks)} checks",
    )
    if passed != len(checks):
        raise SystemExit("Q22 validation found discrepancies.")


if __name__ == "__main__":
    main()
