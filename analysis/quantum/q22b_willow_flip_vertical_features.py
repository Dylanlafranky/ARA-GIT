#!/usr/bin/env python3
"""Flip-aware Tier-4 to Tier-1 ARA features for Q22B."""

from __future__ import annotations

import json
import pathlib

import numpy as np

from q21_willow_child_topology_calibrate import (
    parse_detector_coordinates,
    recursive_features,
    spatial_weights,
    unpack_detectors,
)
from q22_willow_vertical_relation_features import (
    identity_features,
    slice_geometry,
    static_relation_features,
    travel_relation_features,
)


ROOT = pathlib.Path(__file__).parent
GEOMETRY_ROOT = (
    ROOT
    / "public_data"
    / "q22b_willow_105q_geometry"
    / "d5_at_q8_7"
)
RUNG_CROSSINGS = 3


def parent_facing_geometry(geometry: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    lifted = dict(geometry)
    # Three completed boundaries produce one net orientation inversion.
    lifted["tier4"] = 2.0 - geometry["tier4"]
    return lifted


def build_flip_feature_sets(
    detectors: np.ndarray,
    coordinates: np.ndarray,
    weights: np.ndarray,
) -> tuple[dict[str, np.ndarray], dict]:
    geometry = slice_geometry(detectors, coordinates, weights)
    lifted = parent_facing_geometry(geometry)
    identity, identity_names = identity_features(geometry)
    static, static_names, static_quality = static_relation_features(lifted)
    future, past, future_names, past_names, travel_quality = (
        travel_relation_features(lifted)
    )

    # Broken Information³ lock: local Tier 4 remains with shot s, while the
    # Tier-1 series comes from the next shot.
    broken_parent = dict(geometry)
    broken_parent["tier1"] = np.roll(geometry["tier1"], -1, axis=0)
    broken_parent["active"] = np.roll(geometry["active"], -1, axis=0)
    broken_static, _, broken_static_quality = static_relation_features(
        lifted, broken_parent
    )
    broken_future, _, _, _, broken_travel_quality = (
        travel_relation_features(lifted, broken_parent)
    )

    # Frozen even/no-flip control from the mistaken Q22A orientation.
    unflipped_static, _, _ = static_relation_features(geometry)
    unflipped_future, _, _, _, _ = travel_relation_features(geometry)
    q21, q21_quality = recursive_features(detectors, coordinates, weights)
    event_fraction = detectors.mean(axis=1, keepdims=True)

    feature_sets = {
        "flip_vertical_state": np.column_stack((identity, static)),
        "flip_vertical_travel": np.column_stack((identity, future)),
        "flip_vertical_both": np.column_stack((identity, static, future)),
        "flip_past_control": np.column_stack((identity, past)),
        "flip_broken_control": np.column_stack(
            (identity, broken_static, broken_future)
        ),
        "unflipped_control": np.column_stack(
            (identity, unflipped_static, unflipped_future)
        ),
        "q21_child_topology": q21["topology"],
        "event_fraction": event_fraction,
        "flip_vertical_both_plus_count": np.column_stack(
            (identity, static, future, event_fraction)
        ),
    }
    feature_names = {
        "flip_vertical_state": identity_names + static_names,
        "flip_vertical_travel": identity_names + future_names,
        "flip_vertical_both": identity_names + static_names + future_names,
        "flip_past_control": identity_names + past_names,
        "flip_broken_control": identity_names + static_names + future_names,
        "unflipped_control": identity_names + static_names + future_names,
        "q21_child_topology": [
            f"q21_feature_{index:02d}"
            for index in range(q21["topology"].shape[1])
        ],
        "event_fraction": ["event_fraction"],
        "flip_vertical_both_plus_count": (
            identity_names + static_names + future_names + ["event_fraction"]
        ),
    }
    quality = {
        "rung_crossings": RUNG_CROSSINGS,
        "net_flip": True,
        "coordinate_transform": "tier1_facing_tier4 = 2 - local_tier4",
        "time_slice_count": int(len(geometry["time_values"])),
        "tier1_active_fraction": float(geometry["active"].mean()),
        "tier4_valid_fraction": float(geometry["tier4_valid"].mean()),
        "local_tier4_min": float(
            geometry["tier4"][geometry["tier4_valid"]].min()
        ),
        "local_tier4_max": float(
            geometry["tier4"][geometry["tier4_valid"]].max()
        ),
        "lifted_tier4_min": float(
            lifted["tier4"][geometry["tier4_valid"]].min()
        ),
        "lifted_tier4_max": float(
            lifted["tier4"][geometry["tier4_valid"]].max()
        ),
        "static_quality": static_quality,
        "travel_quality": travel_quality,
        "broken_static_quality": broken_static_quality,
        "broken_travel_quality": broken_travel_quality,
        "future_ridge_distance_mean": float(future[:, 1::2].mean()),
        "past_ridge_distance_mean": float(past[:, 1::2].mean()),
        "future_minus_past_ridge_distance": float(
            future[:, 1::2].mean() - past[:, 1::2].mean()
        ),
        "broken_future_ridge_distance_mean": float(
            broken_future[:, 1::2].mean()
        ),
        "q21_quality": q21_quality,
        "feature_names": feature_names,
        "feature_shapes": {
            name: list(values.shape) for name, values in feature_sets.items()
        },
    }
    return feature_sets, quality


def load_geometry_dataset(
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
