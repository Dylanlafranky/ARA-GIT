#!/usr/bin/env python3
"""Outcome-blind construction audit for flip-aware Q22B."""

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
OUTPUT = ROOT / "Q22B_WILLOW_FLIP_VERTICAL_CALIBRATION.json"
MANIFEST = (
    ROOT
    / "public_data"
    / "q22b_willow_105q_geometry"
    / "SOURCE_MANIFEST.json"
)
EXPECTED = {
    "flip_vertical_state": 18,
    "flip_vertical_travel": 34,
    "flip_vertical_both": 42,
    "flip_past_control": 34,
    "flip_broken_control": 42,
    "unflipped_control": 42,
    "q21_child_topology": 24,
    "event_fraction": 1,
    "flip_vertical_both_plus_count": 43,
}


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    if list(GEOMETRY_ROOT.rglob("obs_flips_actual.b8")):
        raise RuntimeError("Labels exist in the Q22B geometry tree.")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["stage"] != "geometry" or len(manifest["members"]) != 12:
        raise RuntimeError("Unexpected geometry manifest.")

    datasets = {}
    all_ok = True
    names_reference = None
    for basis in ("X", "Z"):
        for rounds in ("r13", "r30"):
            detectors, coordinates, weights, metadata = load_geometry_dataset(
                basis, rounds
            )
            features, quality = build_flip_feature_sets(
                detectors, coordinates, weights
            )
            counts = {
                name: int(values.shape[1])
                for name, values in features.items()
            }
            finite = {
                name: bool(np.isfinite(values).all())
                for name, values in features.items()
            }
            bounds_ok = bool(
                quality["local_tier4_min"] >= -1e-12
                and quality["local_tier4_max"] <= 2.0 + 1e-12
                and quality["lifted_tier4_min"] >= -1e-12
                and quality["lifted_tier4_max"] <= 2.0 + 1e-12
                and quality["static_quality"]["_relation_min"] >= -1e-12
                and quality["static_quality"]["_relation_max"]
                <= 2.0 + 1e-12
                and quality["travel_quality"]["_future_relation_min"]
                >= -1e-12
                and quality["travel_quality"]["_future_relation_max"]
                <= 2.0 + 1e-12
                and quality["travel_quality"]["_past_relation_min"]
                >= -1e-12
                and quality["travel_quality"]["_past_relation_max"]
                <= 2.0 + 1e-12
            )
            coverage_ok = all(
                value > 0
                for key, value in quality["travel_quality"].items()
                if key.endswith("_valid_fraction")
            )
            dataset_ok = bool(
                counts == EXPECTED
                and all(finite.values())
                and bounds_ok
                and coverage_ok
                and quality["rung_crossings"] == 3
                and quality["net_flip"]
            )
            all_ok &= dataset_ok
            if names_reference is None:
                names_reference = quality["feature_names"]
            elif names_reference != quality["feature_names"]:
                raise RuntimeError("Feature names differ across datasets.")

            source = GEOMETRY_ROOT / basis / rounds
            datasets[f"{basis}_{rounds}"] = {
                "basis": basis,
                "rounds": int(metadata["rounds"]),
                "shots": int(metadata["shots"]),
                "detector_count": int(coordinates.shape[0]),
                "dataset_ok": dataset_ok,
                "feature_counts": counts,
                "finite": finite,
                "bounds_ok": bounds_ok,
                "coverage_ok": coverage_ok,
                "quality": quality,
                "feature_means": {
                    name: [float(value) for value in values.mean(axis=0)]
                    for name, values in features.items()
                },
                "feature_sds": {
                    name: [float(value) for value in values.std(axis=0)]
                    for name, values in features.items()
                },
                "source_sha256": {
                    name: sha256(source / name)
                    for name in (
                        "metadata.json",
                        "circuit_ideal.stim",
                        "detection_events.b8",
                    )
                },
            }
            print(
                basis,
                rounds,
                "future-past",
                quality["future_minus_past_ridge_distance"],
                "OK" if dataset_ok else "FAIL",
            )

    result = {
        "test": "Q22B",
        "outcome_blind": True,
        "source_doi": "10.5281/zenodo.13273331",
        "patch": "d5_at_q8_7",
        "geometry_manifest_sha256": sha256(MANIFEST),
        "expected_feature_counts": EXPECTED,
        "feature_names": names_reference,
        "datasets": datasets,
        "all_construction_checks_pass": bool(all_ok),
    }
    OUTPUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if not all_ok:
        raise SystemExit("Q22B construction audit failed.")
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
