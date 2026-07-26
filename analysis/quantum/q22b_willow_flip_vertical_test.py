#!/usr/bin/env python3
"""Run checksum-frozen flip-aware Q22B."""

from __future__ import annotations

import csv
import hashlib
import json
import pathlib

import numpy as np

from q21_willow_recursive_child_topology_test import (
    auroc,
    fit_model,
    metrics,
    model_scores,
    serialize_model,
)
from q22b_willow_flip_vertical_features import (
    GEOMETRY_ROOT,
    build_flip_feature_sets,
    load_geometry_dataset,
)


ROOT = pathlib.Path(__file__).parent
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
FREEZE = ROOT / "Q22B_WILLOW_FLIP_VERTICAL_FREEZE_MANIFEST.json"
CALIBRATION = ROOT / "Q22B_WILLOW_FLIP_VERTICAL_CALIBRATION.json"
RESULTS = ROOT / "Q22B_WILLOW_FLIP_VERTICAL_RESULTS.json"
METRICS_CSV = ROOT / "Q22B_WILLOW_FLIP_VERTICAL_METRICS.csv"
CONTROLS_CSV = ROOT / "Q22B_WILLOW_FLIP_VERTICAL_CONTROLS.csv"
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


def unpack_labels(path: pathlib.Path, shots: int) -> np.ndarray:
    packed = np.fromfile(path, dtype=np.uint8)
    if packed.size != shots or np.any(packed & 0b11111110):
        raise ValueError(f"Invalid one-bit target: {path}")
    return (packed & 1).astype(np.uint8)


def verify_freeze() -> dict:
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    for relative, expected in freeze["frozen_files_sha256"].items():
        actual = sha256(ROOT / relative)
        if actual != expected:
            raise RuntimeError(f"Freeze mismatch: {relative}")
    calibration = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    if (
        not calibration["outcome_blind"]
        or not calibration["all_construction_checks_pass"]
    ):
        raise RuntimeError("Q22B calibration is not a clean blind freeze.")
    if list(GEOMETRY_ROOT.rglob("obs_flips_actual.b8")):
        raise RuntimeError("Labels contaminated the geometry tree.")
    manifest = json.loads(OUTCOME_MANIFEST.read_text(encoding="utf-8"))
    if (
        manifest["stage"] != "outcomes"
        or len(manifest["members"]) != 4
        or any(
            not item["name"].endswith("/obs_flips_actual.b8")
            for item in manifest["members"]
        )
    ):
        raise RuntimeError("Unexpected outcome manifest.")
    return freeze


def load(basis: str, rounds: str) -> tuple[dict, np.ndarray, dict, dict]:
    detectors, coordinates, weights, metadata = load_geometry_dataset(
        basis, rounds
    )
    features, quality = build_flip_feature_sets(
        detectors, coordinates, weights
    )
    target_path = (
        OUTCOME_ROOT / basis / rounds / "obs_flips_actual.b8"
    )
    target = unpack_labels(target_path, int(metadata["shots"]))
    return features, target, quality, metadata


def write_csv(path: pathlib.Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    freeze = verify_freeze()
    calibration = json.loads(CALIBRATION.read_text(encoding="utf-8"))
    by_basis = {}
    metric_rows = []

    for basis in ("X", "Z"):
        dev_x, dev_y, dev_quality, dev_meta = load(basis, "r13")
        hold_x, hold_y, hold_quality, hold_meta = load(basis, "r30")
        fitted = {
            name: fit_model(dev_x[name], dev_y) for name in MODELS
        }
        model_results = {}
        for name in MODELS:
            dev_score = model_scores(fitted[name], dev_x[name])
            hold_score = model_scores(fitted[name], hold_x[name])
            dev_metrics = metrics(dev_y, dev_score)
            hold_metrics = metrics(hold_y, hold_score)
            model_results[name] = {
                "feature_count": int(dev_x[name].shape[1]),
                "development": dev_metrics,
                "holdout": hold_metrics,
                "fitted_model": serialize_model(fitted[name]),
            }
            for split, values in (
                ("development", dev_metrics),
                ("holdout", hold_metrics),
            ):
                metric_rows.append(
                    {
                        "basis": basis,
                        "split": split,
                        "model": name,
                        "feature_count": int(dev_x[name].shape[1]),
                        **values,
                    }
                )

        rng = np.random.default_rng(20260726)
        observed = model_results["flip_vertical_both"]["holdout"][
            "auroc"
        ]
        null = np.empty(499)
        for index in range(499):
            permuted = rng.permutation(dev_y)
            null_model = fit_model(
                dev_x["flip_vertical_both"], permuted
            )
            null[index] = auroc(
                hold_y,
                model_scores(null_model, hold_x["flip_vertical_both"]),
            )
        permutation = {
            "count": 499,
            "seed": 20260726,
            "observed_holdout_auroc": observed,
            "null_mean_auroc": float(null.mean()),
            "null_sd_auroc": float(null.std()),
            "null_max_auroc": float(null.max()),
            "one_sided_empirical_p": float(
                (1 + np.sum(null >= observed)) / 500
            ),
        }
        model_results["flip_vertical_both"][
            "permutation_control"
        ] = permutation
        by_basis[basis] = {
            "development": {
                "rounds": int(dev_meta["rounds"]),
                "shots": int(dev_meta["shots"]),
                "prevalence": float(dev_y.mean()),
                "quality": dev_quality,
            },
            "holdout": {
                "rounds": int(hold_meta["rounds"]),
                "shots": int(hold_meta["shots"]),
                "prevalence": float(hold_y.mean()),
                "quality": hold_quality,
            },
            "models": model_results,
        }

    auc = {
        name: {
            basis: by_basis[basis]["models"][name]["holdout"]["auroc"]
            for basis in ("X", "Z")
        }
        for name in MODELS
    }
    mean_auc = {
        name: float(np.mean(list(values.values())))
        for name, values in auc.items()
    }
    geometry = {
        basis: calibration["datasets"][f"{basis}_r30"]["quality"]
        for basis in ("X", "Z")
    }
    gates = {
        "future_closer_than_past_both_holdout_bases": all(
            q["future_ridge_distance_mean"] < q["past_ridge_distance_mean"]
            for q in geometry.values()
        ),
        "future_closer_than_broken_both_holdout_bases": all(
            q["future_ridge_distance_mean"]
            < q["broken_future_ridge_distance_mean"]
            for q in geometry.values()
        ),
        "flip_state_auroc_at_least_0_52_both_bases": all(
            value >= 0.52
            for value in auc["flip_vertical_state"].values()
        ),
        "flip_travel_auroc_at_least_0_52_both_bases": all(
            value >= 0.52
            for value in auc["flip_vertical_travel"].values()
        ),
        "flip_both_auroc_at_least_0_55_both_bases": all(
            value >= 0.55
            for value in auc["flip_vertical_both"].values()
        ),
        "mean_flip_minus_unflipped_at_least_0_01": (
            mean_auc["flip_vertical_both"]
            - mean_auc["unflipped_control"]
            >= 0.01
        ),
        "mean_flip_minus_q21_at_least_0_01": (
            mean_auc["flip_vertical_both"]
            - mean_auc["q21_child_topology"]
            >= 0.01
        ),
        "mean_flip_minus_count_at_least_0_01": (
            mean_auc["flip_vertical_both"] - mean_auc["event_fraction"]
            >= 0.01
        ),
        "mean_flip_minus_past_at_least_0_01": (
            mean_auc["flip_vertical_both"]
            - mean_auc["flip_past_control"]
            >= 0.01
        ),
        "mean_flip_minus_broken_at_least_0_01": (
            mean_auc["flip_vertical_both"]
            - mean_auc["flip_broken_control"]
            >= 0.01
        ),
        "permutation_p_at_most_0_01_both_bases": all(
            by_basis[basis]["models"]["flip_vertical_both"][
                "permutation_control"
            ]["one_sided_empirical_p"]
            <= 0.01
            for basis in ("X", "Z")
        ),
        "count_changes_mean_auroc_by_less_than_0_01": abs(
            mean_auc["flip_vertical_both_plus_count"]
            - mean_auc["flip_vertical_both"]
        )
        < 0.01,
        "flip_direction_concordant_both_bases": all(
            by_basis[basis]["models"]["flip_vertical_both"][
                "development"
            ]["auroc"]
            >= 0.5
            and by_basis[basis]["models"]["flip_vertical_both"][
                "holdout"
            ]["auroc"]
            >= 0.5
            for basis in ("X", "Z")
        ),
    }
    geometry_supported = all(list(gates.values())[:2])
    prediction_supported = all(list(gates.values())[2:])
    strict = bool(geometry_supported and prediction_supported)
    result = {
        "test": "Q22B",
        "title": "Flip-aware Tier-4 to Tier-1 vertical ARA",
        "source_doi": "10.5281/zenodo.13273331",
        "patch": "d5_at_q8_7",
        "freeze_manifest": freeze,
        "calibration_sha256": sha256(CALIBRATION),
        "outcome_manifest_sha256": sha256(OUTCOME_MANIFEST),
        "results_by_basis": by_basis,
        "holdout_auroc": auc,
        "mean_holdout_auroc": mean_auc,
        "holdout_directional_geometry": geometry,
        "gates": gates,
        "gate_count_passed": int(sum(gates.values())),
        "gate_count_total": len(gates),
        "geometry_supported": bool(geometry_supported),
        "prediction_supported": bool(prediction_supported),
        "overall_verdict": "SUPPORTED" if strict else "NOT SUPPORTED",
        "claim_boundary": (
            "Tests a net three-boundary orientation flip on normalized ARA "
            "phase coordinates. It does not test absolute inter-tier "
            "amplitude scaling or prove universal fractality."
        ),
    }
    RESULTS.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_csv(METRICS_CSV, metric_rows)
    control_rows = [
        {
            "control": name,
            "X_holdout_auroc": auc[name]["X"],
            "Z_holdout_auroc": auc[name]["Z"],
            "mean_holdout_auroc": mean_auc[name],
        }
        for name in MODELS
    ]
    control_rows.extend(
        {
            "control": f"gate::{name}",
            "X_holdout_auroc": "",
            "Z_holdout_auroc": "",
            "mean_holdout_auroc": int(value),
        }
        for name, value in gates.items()
    )
    write_csv(CONTROLS_CSV, control_rows)
    print(
        result["overall_verdict"],
        f"{result['gate_count_passed']}/{result['gate_count_total']} gates",
    )
    for name, values in auc.items():
        print(name, values, "mean", mean_auc[name])
    print("geometry_supported", geometry_supported)
    print("prediction_supported", prediction_supported)


if __name__ == "__main__":
    main()
