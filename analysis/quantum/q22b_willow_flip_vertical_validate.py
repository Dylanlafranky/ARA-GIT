#!/usr/bin/env python3
"""Independent arithmetic/provenance validation for Q22B."""

from __future__ import annotations

import hashlib
import json
import pathlib

import numpy as np

from q22b_willow_flip_vertical_features import (
    GEOMETRY_ROOT,
    build_flip_feature_sets,
    load_geometry_dataset,
)


ROOT = pathlib.Path(__file__).parent
RESULTS = ROOT / "Q22B_WILLOW_FLIP_VERTICAL_RESULTS.json"
CALIBRATION = ROOT / "Q22B_WILLOW_FLIP_VERTICAL_CALIBRATION.json"
FREEZE = ROOT / "Q22B_WILLOW_FLIP_VERTICAL_FREEZE_MANIFEST.json"
OUTCOME_ROOT = (
    ROOT
    / "public_data"
    / "q22b_willow_105q_outcomes"
    / "d5_at_q8_7"
)
OUTCOME_MANIFEST = (
    ROOT
    / "public_data"
    / "q22b_willow_105q_outcomes"
    / "SOURCE_MANIFEST.json"
)
OUTPUT = ROOT / "Q22B_WILLOW_FLIP_VERTICAL_VALIDATION.json"
MODELS = (
    "flip_vertical_state",
    "flip_vertical_travel",
    "flip_vertical_both",
    "flip_past_control",
    "flip_broken_control",
    "unflipped_control",
    "q21_child_topology",
    "event_fraction",
    "flip_vertical_both_plus_count",
)


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def labels(path: pathlib.Path, shots: int) -> np.ndarray:
    packed = np.fromfile(path, dtype=np.uint8)
    if packed.size != shots or np.any(packed & 0b11111110):
        raise ValueError(path)
    return (packed & 1).astype(np.uint8)


def auc(target: np.ndarray, score: np.ndarray) -> float:
    order = np.argsort(score, kind="mergesort")
    values = score[order]
    ranks = np.empty(score.size, dtype=float)
    start = 0
    while start < len(values):
        stop = start + 1
        while stop < len(values) and values[stop] == values[start]:
            stop += 1
        ranks[order[start:stop]] = (start + 1 + stop) / 2
        start = stop
    positive = target == 1
    n1 = int(positive.sum())
    n0 = int((~positive).sum())
    return float(
        (ranks[positive].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)
    )


def scores(
    development: np.ndarray,
    target: np.ndarray,
    holdout: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    mean = development.mean(axis=0)
    sd = development.std(axis=0)
    zd = (development - mean) / sd
    zh = (holdout - mean) / sd
    c0 = zd[target == 0].mean(axis=0)
    c1 = zd[target == 1].mean(axis=0)
    direction = c1 - c0
    midpoint = (c0 + c1) / 2
    return (zd - midpoint) @ direction, (zh - midpoint) @ direction


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    calibration = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    checks = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append(
            {"check": name, "passed": bool(passed), "detail": detail}
        )

    for relative, expected in freeze["frozen_files_sha256"].items():
        actual = sha256(ROOT / relative)
        check(
            f"freeze::{relative}",
            actual == expected,
            {"expected": expected, "actual": actual},
        )
    check(
        "no_labels_in_geometry",
        not list(GEOMETRY_ROOT.rglob("obs_flips_actual.b8")),
        0,
    )
    manifest = json.loads(OUTCOME_MANIFEST.read_text(encoding="utf-8"))
    check(
        "outcome_manifest",
        manifest["stage"] == "outcomes"
        and len(manifest["members"]) == 4
        and all(
            row["name"].endswith("/obs_flips_actual.b8")
            for row in manifest["members"]
        ),
        [row["name"] for row in manifest["members"]],
    )
    check(
        "calibration_hash",
        sha256(CALIBRATION) == result["calibration_sha256"],
        sha256(CALIBRATION),
    )
    check(
        "outcome_manifest_hash",
        sha256(OUTCOME_MANIFEST) == result["outcome_manifest_sha256"],
        sha256(OUTCOME_MANIFEST),
    )
    check(
        "blind_calibration",
        calibration["outcome_blind"]
        and calibration["all_construction_checks_pass"],
        {
            "outcome_blind": calibration["outcome_blind"],
            "construction": calibration["all_construction_checks_pass"],
        },
    )

    hold_auc = {name: {} for name in MODELS}
    dev_auc = {name: {} for name in MODELS}
    for basis in ("X", "Z"):
        dd, dc, dw, dm = load_geometry_dataset(basis, "r13")
        hd, hc, hw, hm = load_geometry_dataset(basis, "r30")
        dx, dq = build_flip_feature_sets(dd, dc, dw)
        hx, hq = build_flip_feature_sets(hd, hc, hw)
        dy = labels(
            OUTCOME_ROOT / basis / "r13" / "obs_flips_actual.b8",
            int(dm["shots"]),
        )
        hy = labels(
            OUTCOME_ROOT / basis / "r30" / "obs_flips_actual.b8",
            int(hm["shots"]),
        )
        for name in MODELS:
            ds, hs = scores(dx[name], dy, hx[name])
            dev_auc[name][basis] = auc(dy, ds)
            hold_auc[name][basis] = auc(hy, hs)
            recorded = result["holdout_auroc"][name][basis]
            check(
                f"auroc::{basis}::{name}",
                abs(hold_auc[name][basis] - recorded) <= 1e-12,
                {
                    "recorded": recorded,
                    "recalculated": hold_auc[name][basis],
                },
            )
        cq = calibration["datasets"][f"{basis}_r30"]["quality"]
        for field in (
            "future_ridge_distance_mean",
            "past_ridge_distance_mean",
            "broken_future_ridge_distance_mean",
        ):
            check(
                f"geometry::{basis}::{field}",
                abs(hq[field] - cq[field]) <= 1e-12,
                {"recorded": cq[field], "recalculated": hq[field]},
            )
        check(
            f"three_crossing_flip::{basis}",
            hq["rung_crossings"] == 3
            and hq["net_flip"]
            and hq["coordinate_transform"]
            == "tier1_facing_tier4 = 2 - local_tier4",
            {
                "crossings": hq["rung_crossings"],
                "net_flip": hq["net_flip"],
            },
        )

    mean = {
        name: float(np.mean(list(values.values())))
        for name, values in hold_auc.items()
    }
    geom = {
        basis: calibration["datasets"][f"{basis}_r30"]["quality"]
        for basis in ("X", "Z")
    }
    gates = {
        "future_closer_than_past_both_holdout_bases": all(
            q["future_ridge_distance_mean"] < q["past_ridge_distance_mean"]
            for q in geom.values()
        ),
        "future_closer_than_broken_both_holdout_bases": all(
            q["future_ridge_distance_mean"]
            < q["broken_future_ridge_distance_mean"]
            for q in geom.values()
        ),
        "flip_state_auroc_at_least_0_52_both_bases": all(
            value >= 0.52
            for value in hold_auc["flip_vertical_state"].values()
        ),
        "flip_travel_auroc_at_least_0_52_both_bases": all(
            value >= 0.52
            for value in hold_auc["flip_vertical_travel"].values()
        ),
        "flip_both_auroc_at_least_0_55_both_bases": all(
            value >= 0.55
            for value in hold_auc["flip_vertical_both"].values()
        ),
        "mean_flip_minus_unflipped_at_least_0_01": (
            mean["flip_vertical_both"] - mean["unflipped_control"] >= 0.01
        ),
        "mean_flip_minus_q21_at_least_0_01": (
            mean["flip_vertical_both"] - mean["q21_child_topology"] >= 0.01
        ),
        "mean_flip_minus_count_at_least_0_01": (
            mean["flip_vertical_both"] - mean["event_fraction"] >= 0.01
        ),
        "mean_flip_minus_past_at_least_0_01": (
            mean["flip_vertical_both"] - mean["flip_past_control"] >= 0.01
        ),
        "mean_flip_minus_broken_at_least_0_01": (
            mean["flip_vertical_both"] - mean["flip_broken_control"] >= 0.01
        ),
        "permutation_p_at_most_0_01_both_bases": all(
            result["results_by_basis"][basis]["models"][
                "flip_vertical_both"
            ]["permutation_control"]["one_sided_empirical_p"]
            <= 0.01
            for basis in ("X", "Z")
        ),
        "count_changes_mean_auroc_by_less_than_0_01": abs(
            mean["flip_vertical_both_plus_count"]
            - mean["flip_vertical_both"]
        )
        < 0.01,
        "flip_direction_concordant_both_bases": all(
            dev_auc["flip_vertical_both"][basis] >= 0.5
            and hold_auc["flip_vertical_both"][basis] >= 0.5
            for basis in ("X", "Z")
        ),
    }
    for name, recorded in result["gates"].items():
        check(
            f"gate::{name}",
            gates[name] == recorded,
            {"recorded": recorded, "recalculated": gates[name]},
        )
    check(
        "gate_count",
        sum(gates.values()) == result["gate_count_passed"],
        {
            "recorded": result["gate_count_passed"],
            "recalculated": sum(gates.values()),
        },
    )
    check(
        "verdict",
        result["overall_verdict"]
        == ("SUPPORTED" if all(gates.values()) else "NOT SUPPORTED"),
        result["overall_verdict"],
    )
    for basis in ("X", "Z"):
        null = result["results_by_basis"][basis]["models"][
            "flip_vertical_both"
        ]["permutation_control"]
        check(
            f"permutation_summary::{basis}",
            null["count"] == 499
            and null["seed"] == 20260726
            and 0.002 <= null["one_sided_empirical_p"] <= 1
            and null["null_sd_auroc"] > 0,
            null,
        )

    passed = sum(row["passed"] for row in checks)
    output = {
        "test": "Q22B",
        "validation_status": (
            "PASS" if passed == len(checks) else "NEEDS REVISION"
        ),
        "checks_passed": int(passed),
        "checks_total": len(checks),
        "independent_holdout_auroc": hold_auc,
        "independent_development_auroc": dev_auc,
        "reconstructed_gates": gates,
        "checks": checks,
        "caveat": (
            "Individual permutation AUROCs were not persisted; their frozen "
            "aggregate summaries are provenance-checked but not regenerated."
        ),
    }
    OUTPUT.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(output["validation_status"], f"{passed}/{len(checks)} checks")
    if passed != len(checks):
        raise SystemExit("Validation discrepancy.")


if __name__ == "__main__":
    main()
