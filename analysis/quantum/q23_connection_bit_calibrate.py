#!/usr/bin/env python3
"""Outcome-blind geometry calibration for Q23."""

from __future__ import annotations

import hashlib
import json
import pathlib

from q23_connection_bit_features import (
    BASES,
    BLOCK_SIZE,
    GEOMETRY_ROOT,
    ROUNDS,
    connection_identities,
    load_geometry,
)


ROOT = pathlib.Path(__file__).parent
MANIFEST = (
    ROOT / "public_data" / "q23_willow_d7_geometry" / "SOURCE_MANIFEST.json"
)
OUTPUT = ROOT / "Q23_WILLOW_CONNECTION_BIT_CALIBRATION.json"


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    outcome_members = list(GEOMETRY_ROOT.rglob("obs_flips_actual.b8"))
    if outcome_members:
        raise RuntimeError(f"Outcome leak in geometry root: {outcome_members}")
    outcome_root = ROOT / "public_data" / "q23_willow_d7_outcomes"
    if outcome_root.exists() and list(outcome_root.rglob("obs_flips_actual.b8")):
        raise RuntimeError("Q23 outcomes already exist; calibration is not blind.")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    names = [member["name"] for member in manifest["members"]]
    if len(names) != 12 or any("obs_flips" in name for name in names):
        raise RuntimeError("Geometry manifest is incomplete or outcome-contaminated.")

    datasets = []
    for basis in BASES:
        for rounds in ROUNDS:
            detectors, coordinates, weights, metadata = load_geometry(
                basis, rounds
            )
            _, _, quality = connection_identities(
                detectors, coordinates, weights
            )
            datasets.append(
                {
                    "basis": basis,
                    "rounds": rounds,
                    "shots": int(metadata["shots"]),
                    "distance": int(metadata["distance"]),
                    "detector_count": int(len(coordinates)),
                    "quality": quality,
                    "source_hashes": {
                        name: sha256(GEOMETRY_ROOT / basis / rounds / name)
                        for name in (
                            "metadata.json",
                            "circuit_ideal.stim",
                            "detection_events.b8",
                        )
                    },
                }
            )

    result = {
        "claim": "Q23-WILLOW-CONNECTION-WEB-BIT-CLOSURE-v1",
        "created": "2026-07-26",
        "source_doi": "10.5281/zenodo.13273331",
        "patch": "d7_at_q6_7",
        "outcome_blind": True,
        "outcome_files_present": False,
        "block_size": BLOCK_SIZE,
        "primary_connection_identity": "web_stability",
        "bit_identity": "retention",
        "connection_decompressions": [
            "same_child_persistence",
            "anti_child_handover",
            "web_concentration",
        ],
        "rank_diameter_rule": "2*(midrank+0.5)/block_count",
        "parent_rule": "2*bit/(connection+bit)",
        "manifest_sha256": sha256(MANIFEST),
        "manifest_members": names,
        "datasets": datasets,
    }
    OUTPUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(OUTPUT)


if __name__ == "__main__":
    main()
