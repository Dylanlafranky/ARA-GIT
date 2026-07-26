#!/usr/bin/env python3
"""ARA-native connection-web and logical-bit identities for Q23."""

from __future__ import annotations

import json
import pathlib

import numpy as np

from q21_willow_child_topology_calibrate import (
    frozen_spatial_shuffle,
    parse_detector_coordinates,
    recursive_features,
    spatial_weights,
    unpack_detectors,
)


ROOT = pathlib.Path(__file__).parent
GEOMETRY_ROOT = (
    ROOT / "public_data" / "q23_willow_d7_geometry" / "d7_at_q6_7"
)
OUTCOME_ROOT = (
    ROOT / "public_data" / "q23_willow_d7_outcomes" / "d7_at_q6_7"
)
BLOCK_SIZE = 250
BASES = ("X", "Z")
ROUNDS = ("r13", "r30")


def rank_diameter(values: np.ndarray) -> np.ndarray:
    """Map one identity's ordered block states onto the open ARA 0-2 diameter.

    Mid-ranks preserve ties. Midpoint placement avoids artificial exact
    singularities at 0 and 2. The mapping uses only the marginal identity,
    never its pairing to the other identity.
    """

    values = np.asarray(values, dtype=np.float64)
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=np.float64)
    sorted_values = values[order]
    start = 0
    while start < len(values):
        stop = start + 1
        while stop < len(values) and sorted_values[stop] == sorted_values[start]:
            stop += 1
        ranks[order[start:stop]] = (start + stop - 1) / 2.0
        start = stop
    return 2.0 * (ranks + 0.5) / len(values)


def parent_ara(connection: np.ndarray, bit: np.ndarray) -> np.ndarray:
    """One-rung-up ARA relation; ridge 1 means equal normalized positions."""

    denominator = connection + bit
    output = np.ones_like(connection, dtype=np.float64)
    np.divide(2.0 * bit, denominator, out=output, where=denominator > 0)
    return output


def _block_web_values(handovers: np.ndarray) -> dict[str, np.ndarray]:
    shots = handovers.shape[0]
    block_count = shots // BLOCK_SIZE
    used = block_count * BLOCK_SIZE
    web = handovers[:used].reshape(block_count, BLOCK_SIZE, 4, 4)
    block_mean = web.mean(axis=1)

    diagonal = np.trace(block_mean, axis1=1, axis2=2)
    anti_diagonal = np.trace(
        np.flip(block_mean, axis=2), axis1=1, axis2=2
    )
    probabilities = block_mean.reshape(block_count, 16) / 2.0
    hhi = np.square(probabilities).sum(axis=1)
    concentration = 2.0 * (hhi - 1.0 / 16.0) / (15.0 / 16.0)

    first = web[:, : BLOCK_SIZE // 2].mean(axis=1)
    second = web[:, BLOCK_SIZE // 2 :].mean(axis=1)
    l1 = np.abs(second - first).sum(axis=(1, 2))
    stability = 2.0 * (1.0 - l1 / 4.0)

    return {
        # Primary connection-heavy identity: recurrence of the complete
        # sixteen-path relation web between the two halves of a block.
        "web_stability": np.clip(stability, 0.0, 2.0),
        # Declared decompressions of that web.
        "same_child_persistence": np.clip(diagonal, 0.0, 2.0),
        "anti_child_handover": np.clip(anti_diagonal, 0.0, 2.0),
        "web_concentration": np.clip(concentration, 0.0, 2.0),
    }


def load_geometry(
    basis: str, rounds: str
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    path = GEOMETRY_ROOT / basis / rounds
    metadata = json.loads(
        (path / "metadata.json").read_text(encoding="utf-8")
    )
    coordinates = parse_detector_coordinates(path / "circuit_ideal.stim")
    detectors = unpack_detectors(
        path / "detection_events.b8",
        int(metadata["shots"]),
        len(coordinates),
    )
    return detectors, coordinates, spatial_weights(coordinates), metadata


def connection_identities(
    detectors: np.ndarray,
    coordinates: np.ndarray,
    weights: np.ndarray,
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], dict]:
    native, native_quality = recursive_features(
        detectors, coordinates, weights
    )
    broken, broken_quality = recursive_features(
        detectors,
        coordinates,
        frozen_spatial_shuffle(weights, coordinates),
    )
    native_web = native["handovers"].reshape(-1, 4, 4)
    broken_web = broken["handovers"].reshape(-1, 4, 4)
    values = _block_web_values(native_web)
    broken_values = _block_web_values(broken_web)
    quality = {
        "shots": int(len(detectors)),
        "block_size": BLOCK_SIZE,
        "block_count": int(len(detectors) // BLOCK_SIZE),
        "unused_shots": int(len(detectors) % BLOCK_SIZE),
        "native_recursive_quality": native_quality,
        "broken_recursive_quality": broken_quality,
        "raw_summaries": {
            name: {
                "min": float(raw.min()),
                "max": float(raw.max()),
                "mean": float(raw.mean()),
                "sd": float(raw.std()),
            }
            for name, raw in values.items()
        },
        "broken_raw_summaries": {
            name: {
                "min": float(raw.min()),
                "max": float(raw.max()),
                "mean": float(raw.mean()),
                "sd": float(raw.std()),
            }
            for name, raw in broken_values.items()
        },
    }
    return values, broken_values, quality


def unpack_labels(path: pathlib.Path, shots: int) -> np.ndarray:
    packed = np.fromfile(path, dtype=np.uint8)
    labels = np.unpackbits(packed, bitorder="little")[:shots]
    if len(labels) != shots:
        raise ValueError(f"{path}: insufficient outcome bits")
    return labels.astype(np.uint8)


def bit_identities(labels: np.ndarray) -> dict[str, np.ndarray]:
    block_count = len(labels) // BLOCK_SIZE
    used = block_count * BLOCK_SIZE
    flip_rate = labels[:used].reshape(block_count, BLOCK_SIZE).mean(axis=1)
    return {
        "retention": 2.0 * (1.0 - flip_rate),
        "flip": 2.0 * flip_rate,
    }


def paired_closure(
    connection_raw: np.ndarray,
    bit_raw: np.ndarray,
) -> dict[str, np.ndarray | float]:
    connection = rank_diameter(connection_raw)
    bit = rank_diameter(bit_raw)
    parent = parent_ara(connection, bit)
    ridge_distance = np.abs(parent - 1.0)
    return {
        "connection": connection,
        "bit": bit,
        "parent": parent,
        "ridge_distance": ridge_distance,
        "mean_ridge_distance": float(ridge_distance.mean()),
        "median_parent": float(np.median(parent)),
        "near_ridge_fraction_0_10": float((ridge_distance <= 0.10).mean()),
        "rank_correlation": float(np.corrcoef(connection, bit)[0, 1]),
    }
