#!/usr/bin/env python3
"""Build the outcome-blind Q21 recursive child/topology calibration.

This file deliberately has no observable-label loader.  It reads only detector
coordinates, detector events, metadata and the selective-extraction manifest.
"""

from __future__ import annotations

import hashlib
import json
import pathlib

import numpy as np


ROOT = pathlib.Path(__file__).parent
DEVELOPMENT_ROOT = ROOT / "public_data" / "q20_willow_105q"
FRESH_ROOT = ROOT / "public_data" / "q21_willow_105q"
FRESH_MANIFEST = (
    ROOT / "public_data" / "q21_willow_105q" / "SOURCE_MANIFEST.json"
)
OUTPUT = ROOT / "Q21_WILLOW_CHILD_TOPOLOGY_CALIBRATION.json"
CHILDREN = ("AA", "AB", "BB", "BA")


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_detector_coordinates(path: pathlib.Path) -> np.ndarray:
    coordinates = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("DETECTOR("):
            raw = line.split("(", 1)[1].split(")", 1)[0]
            coordinates.append([float(value) for value in raw.split(",")[:3]])
    return np.asarray(coordinates, dtype=np.float64)


def normalize_axis(coordinates: np.ndarray, axis: int) -> np.ndarray:
    values = coordinates[:, axis]
    span = float(values.max() - values.min())
    if span <= 0:
        raise ValueError(f"Axis {axis} has no span.")
    return 2.0 * (values - values.min()) / span - 1.0


def unpack_detectors(
    path: pathlib.Path, shots: int, detector_count: int
) -> np.ndarray:
    bytes_per_shot = (detector_count + 7) // 8
    packed = np.fromfile(path, dtype=np.uint8)
    expected = shots * bytes_per_shot
    if packed.size != expected:
        raise ValueError(f"{path}: {packed.size} bytes; expected {expected}.")
    packed = packed.reshape(shots, bytes_per_shot)
    return np.unpackbits(packed, axis=1, bitorder="little")[
        :, :detector_count
    ]


def spatial_weights(coordinates: np.ndarray) -> np.ndarray:
    x = normalize_axis(coordinates, 0)
    y = normalize_axis(coordinates, 1)
    xa, xb = (1.0 - x) / 2.0, (1.0 + x) / 2.0
    ya, yb = (1.0 - y) / 2.0, (1.0 + y) / 2.0
    # Circular order around the x-y relation plane.
    return np.column_stack((xa * ya, xa * yb, xb * yb, xb * ya))


def frozen_spatial_shuffle(
    weights: np.ndarray, coordinates: np.ndarray
) -> np.ndarray:
    """Misassign spatial positions while preserving each slice's weight set."""
    shuffled = weights.copy()
    for time_value in np.unique(coordinates[:, 2]):
        indices = np.flatnonzero(coordinates[:, 2] == time_value)
        ordered = indices[
            np.lexsort((coordinates[indices, 1], coordinates[indices, 0]))
        ]
        shift = max(1, len(ordered) // 2 - 1)
        shuffled[ordered] = weights[np.roll(ordered, shift)]
    return shuffled


def recursive_features(
    detectors: np.ndarray,
    coordinates: np.ndarray,
    weights: np.ndarray,
) -> tuple[dict[str, np.ndarray], dict]:
    time = normalize_axis(coordinates, 2)
    time_a, time_b = (1.0 - time) / 2.0, (1.0 + time) / 2.0

    grandchildren_unscaled = np.column_stack(
        [
            detectors @ (weights[:, child] * time_weight)
            for child in range(4)
            for time_weight in (time_a, time_b)
        ]
    ).astype(np.float64)
    totals = grandchildren_unscaled.sum(axis=1, keepdims=True)
    empty_cloud = totals[:, 0] == 0
    totals[empty_cloud] = 1.0
    grandchildren = 2.0 * grandchildren_unscaled / totals
    grandchildren[empty_cloud] = 0.25  # eight equal children sum to TE-ARA 2

    # Preserve every directed child-to-child handover between adjacent slices.
    time_values = np.unique(coordinates[:, 2])
    slice_shares = np.zeros(
        (detectors.shape[0], len(time_values), 4), dtype=np.float64
    )
    slice_active = np.zeros(
        (detectors.shape[0], len(time_values)), dtype=bool
    )
    for time_index, time_value in enumerate(time_values):
        indices = np.flatnonzero(coordinates[:, 2] == time_value)
        activity = detectors[:, indices] @ weights[indices]
        activity_total = activity.sum(axis=1)
        active = activity_total > 0
        slice_shares[active, time_index] = (
            activity[active] / activity_total[active, None]
        )
        slice_active[:, time_index] = active

    handovers = np.zeros((detectors.shape[0], 4, 4), dtype=np.float64)
    valid_pair_count = np.zeros(detectors.shape[0], dtype=np.int32)
    for time_index in range(len(time_values) - 1):
        valid = (
            slice_active[:, time_index]
            & slice_active[:, time_index + 1]
        )
        if not np.any(valid):
            continue
        handovers[valid] += (
            slice_shares[valid, time_index, :, None]
            * slice_shares[valid, time_index + 1, None, :]
        )
        valid_pair_count[valid] += 1

    handover_totals = handovers.sum(axis=(1, 2), keepdims=True)
    empty_handover = handover_totals[:, 0, 0] == 0
    handover_totals[empty_handover] = 1.0
    handovers = 2.0 * handovers / handover_totals
    handovers[empty_handover] = 0.125  # sixteen equal paths sum to 2
    handovers_flat = handovers.reshape(detectors.shape[0], 16)

    # Recompress only for explicit parent controls/diagnostics.
    child_totals = grandchildren.reshape(-1, 4, 2).sum(axis=2)
    parent_x = child_totals[:, 2] + child_totals[:, 3]
    parent_y = child_totals[:, 1] + child_totals[:, 2]
    parent_xy_relation = child_totals[:, 1] + child_totals[:, 3]
    parent_time = grandchildren[:, 1::2].sum(axis=1)
    parent_xt_relation = (
        grandchildren[:, 1]
        + grandchildren[:, 3]
        + grandchildren[:, 4]
        + grandchildren[:, 6]
    )
    parent_xy = np.column_stack(
        (parent_x, parent_y, parent_xy_relation)
    )
    q20_global_xt = np.column_stack(
        (parent_x, parent_time, parent_xt_relation)
    )
    topology = np.column_stack((grandchildren, handovers_flat))

    quality = {
        "empty_cloud_fraction": float(empty_cloud.mean()),
        "empty_handover_fraction": float(empty_handover.mean()),
        "mean_valid_adjacent_time_pairs": float(valid_pair_count.mean()),
        "grandchild_sum_max_error": float(
            np.max(np.abs(grandchildren.sum(axis=1) - 2.0))
        ),
        "handover_sum_max_error": float(
            np.max(np.abs(handovers_flat.sum(axis=1) - 2.0))
        ),
        "grandchild_min": float(grandchildren.min()),
        "grandchild_max": float(grandchildren.max()),
        "handover_min": float(handovers_flat.min()),
        "handover_max": float(handovers_flat.max()),
        "parent_xy_mean": [
            float(value) for value in parent_xy.mean(axis=0)
        ],
        "parent_xy_sd": [
            float(value) for value in parent_xy.std(axis=0)
        ],
        "q20_global_xt_mean": [
            float(value) for value in q20_global_xt.mean(axis=0)
        ],
        "grandchild_means": [
            float(value) for value in grandchildren.mean(axis=0)
        ],
        "handover_means": [
            float(value) for value in handovers_flat.mean(axis=0)
        ],
    }
    return {
        "grandchildren": grandchildren,
        "handovers": handovers_flat,
        "topology": topology,
        "parent_xy": parent_xy,
        "q20_global_xt": q20_global_xt,
    }, quality


def inspect_dataset(
    source_root: pathlib.Path,
    patch: str,
    basis: str,
    rounds_name: str,
) -> dict:
    path = source_root / patch / basis / rounds_name
    metadata_path = path / "metadata.json"
    circuit_path = path / "circuit_ideal.stim"
    detector_path = path / "detection_events.b8"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    shots = int(metadata["shots"])
    rounds = int(metadata["rounds"])
    coordinates = parse_detector_coordinates(circuit_path)
    detectors = unpack_detectors(detector_path, shots, len(coordinates))
    weights = spatial_weights(coordinates)
    _, quality = recursive_features(detectors, coordinates, weights)
    _, shuffled_quality = recursive_features(
        detectors, coordinates, frozen_spatial_shuffle(weights, coordinates)
    )
    return {
        "patch": patch,
        "basis": basis,
        "rounds": rounds,
        "shots": shots,
        "detector_count": int(len(coordinates)),
        "time_slice_count": int(len(np.unique(coordinates[:, 2]))),
        "mean_event_count": float(detectors.sum(axis=1).mean()),
        "quality": quality,
        "frozen_spatial_shuffle_quality": shuffled_quality,
        "source_hashes": {
            "metadata.json": sha256(metadata_path),
            "circuit_ideal.stim": sha256(circuit_path),
            "detection_events.b8": sha256(detector_path),
        },
    }


def main() -> None:
    manifest = json.loads(FRESH_MANIFEST.read_text(encoding="utf-8"))
    member_names = [item["name"] for item in manifest["members"]]
    if any("obs_flips" in name for name in member_names):
        raise RuntimeError("Fresh-patch manifest contains an outcome member.")
    if len(member_names) != 6:
        raise RuntimeError("Fresh-patch manifest must contain exactly six files.")
    # The original pre-freeze manifest hash is historical provenance and
    # includes its extraction timestamp. Preserve it on later reproductions;
    # the immutable member contents are verified independently below.
    original_manifest_sha256 = sha256(FRESH_MANIFEST)
    if OUTPUT.exists():
        locked = json.loads(OUTPUT.read_text(encoding="utf-8"))
        original_manifest_sha256 = locked["fresh_manifest_sha256"]

    datasets = []
    for basis in ("X", "Z"):
        datasets.append(
            inspect_dataset(
                DEVELOPMENT_ROOT, "d5_at_q4_7", basis, "r13"
            )
        )
        datasets.append(
            inspect_dataset(FRESH_ROOT, "d5_at_q6_5", basis, "r30")
        )

    calibration = {
        "claim": "Q21-WILLOW-RECURSIVE-CHILD-TOPOLOGY-v1",
        "created": "2026-07-26",
        "outcome_blind_fresh_patch": True,
        "fresh_outcome_files_extracted": False,
        "development_patch": "d5_at_q4_7/r13",
        "fresh_holdout_patch": "d5_at_q6_5/r30",
        "spatial_children_circular_order": list(CHILDREN),
        "grandchild_order": [
            f"{child}_{phase}"
            for child in CHILDREN
            for phase in ("timeA", "timeB")
        ],
        "handover_order": [
            f"{source}_to_{target}"
            for source in CHILDREN
            for target in CHILDREN
        ],
        "primary_feature_count": 24,
        "parent_rule": (
            "A near-1.0 recompressed parent is expected; prediction retains "
            "eight time-grandchildren and sixteen directed local handovers."
        ),
        "fresh_manifest_sha256": original_manifest_sha256,
        "fresh_manifest_members": member_names,
        "datasets": datasets,
    }
    OUTPUT.write_text(
        json.dumps(calibration, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "fresh_outcome_files_extracted": False,
                "datasets": [
                    {
                        "patch": item["patch"],
                        "basis": item["basis"],
                        "rounds": item["rounds"],
                        "parent_xy_mean": item["quality"][
                            "parent_xy_mean"
                        ],
                        "grandchild_sum_max_error": item["quality"][
                            "grandchild_sum_max_error"
                        ],
                        "handover_sum_max_error": item["quality"][
                            "handover_sum_max_error"
                        ],
                    }
                    for item in datasets
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
