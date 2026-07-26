#!/usr/bin/env python3
"""Outcome-blind calibration and construction audit for Q22."""

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
OUTPUT = ROOT / "Q22_WILLOW_VERTICAL_RELATION_CALIBRATION.json"
MANIFEST = (
    ROOT
    / "public_data"
    / "q22_willow_105q_geometry"
    / "SOURCE_MANIFEST.json"
)
EXPECTED_FEATURE_COUNTS = {
    "vertical_state": 18,
    "vertical_travel": 34,
    "vertical_both": 42,
    "past_travel_control": 34,
    "broken_vertical_both": 42,
    "q21_child_topology": 24,
    "event_fraction": 1,
    "vertical_both_plus_count": 43,
}


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    if list(GEOMETRY_ROOT.rglob("obs_flips_actual.b8")):
        raise RuntimeError("Outcome labels exist in the geometry staging tree.")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["stage"] != "geometry" or len(manifest["members"]) != 12:
        raise RuntimeError("Unexpected Q22 geometry extraction manifest.")

    datasets = {}
    all_ok = True
    feature_names_reference: dict[str, list[str]] | None = None
    for basis in ("X", "Z"):
        for rounds in ("r13", "r30"):
            detectors, coordinates, weights, metadata = load_geometry_dataset(
                basis, rounds
            )
            features, quality = build_feature_sets(
                detectors, coordinates, weights
            )
            construction = {
                "finite": {
                    name: bool(np.isfinite(values).all())
                    for name, values in features.items()
                },
                "feature_counts": {
                    name: int(values.shape[1])
                    for name, values in features.items()
                },
                "ara_bounds_ok": bool(
                    quality["tier1_min"] >= -1e-12
                    and quality["tier1_max"] <= 2.0 + 1e-12
                    and quality["tier4_min"] >= -1e-12
                    and quality["tier4_max"] <= 2.0 + 1e-12
                    and quality["static_valid_fractions"]["_relation_min"]
                    >= -1e-12
                    and quality["static_valid_fractions"]["_relation_max"]
                    <= 2.0 + 1e-12
                    and quality["travel_valid_fractions"][
                        "_future_relation_min"
                    ]
                    >= -1e-12
                    and quality["travel_valid_fractions"][
                        "_future_relation_max"
                    ]
                    <= 2.0 + 1e-12
                    and quality["travel_valid_fractions"][
                        "_past_relation_min"
                    ]
                    >= -1e-12
                    and quality["travel_valid_fractions"][
                        "_past_relation_max"
                    ]
                    <= 2.0 + 1e-12
                ),
                "nonzero_valid_coverage": bool(
                    all(
                        value > 0
                        for key, value in quality[
                            "travel_valid_fractions"
                        ].items()
                        if key.endswith("_valid_fraction")
                    )
                ),
            }
            construction["feature_counts_match_protocol"] = (
                construction["feature_counts"] == EXPECTED_FEATURE_COUNTS
            )
            dataset_ok = bool(
                all(construction["finite"].values())
                and construction["ara_bounds_ok"]
                and construction["nonzero_valid_coverage"]
                and construction["feature_counts_match_protocol"]
            )
            all_ok &= dataset_ok

            if feature_names_reference is None:
                feature_names_reference = quality["feature_names"]
            elif quality["feature_names"] != feature_names_reference:
                raise RuntimeError("Feature names differ across datasets.")

            path = GEOMETRY_ROOT / basis / rounds
            key = f"{basis}_{rounds}"
            datasets[key] = {
                "basis": basis,
                "rounds": int(metadata["rounds"]),
                "shots": int(metadata["shots"]),
                "detector_count": int(coordinates.shape[0]),
                "dataset_ok": dataset_ok,
                "construction": construction,
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
                    name: sha256(path / name)
                    for name in (
                        "metadata.json",
                        "circuit_ideal.stim",
                        "detection_events.b8",
                    )
                },
            }
            print(
                key,
                "future-past distance",
                quality["future_minus_past_ridge_distance"],
                "OK" if dataset_ok else "FAIL",
            )

    output = {
        "test": "Q22",
        "outcome_blind": True,
        "source_doi": "10.5281/zenodo.13273331",
        "patch": "d5_at_q6_9",
        "geometry_manifest_sha256": sha256(MANIFEST),
        "expected_feature_counts": EXPECTED_FEATURE_COUNTS,
        "feature_names": feature_names_reference,
        "datasets": datasets,
        "all_construction_checks_pass": bool(all_ok),
    }
    OUTPUT.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if not all_ok:
        raise SystemExit("Q22 outcome-blind construction audit failed.")
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
