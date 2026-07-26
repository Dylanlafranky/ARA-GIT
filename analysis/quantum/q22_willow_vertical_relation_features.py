#!/usr/bin/env python3
"""Outcome-blind ARA Tier-4 to Tier-1 feature construction for Q22."""

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


ROOT = pathlib.Path(__file__).parent
GEOMETRY_ROOT = (
    ROOT
    / "public_data"
    / "q22_willow_105q_geometry"
    / "d5_at_q6_9"
)
CHILDREN = ("AA", "AB", "BB", "BA")
DELAYS = (1, 2, 3)


def masked_mean(values: np.ndarray, valid: np.ndarray) -> np.ndarray:
    count = valid.sum(axis=1)
    total = np.where(valid, values, 0.0).sum(axis=1)
    output = np.ones(values.shape[0], dtype=np.float64)
    np.divide(total, count, out=output, where=count > 0)
    return output


def masked_sd(values: np.ndarray, valid: np.ndarray) -> np.ndarray:
    mean = masked_mean(values, valid)
    count = valid.sum(axis=1)
    squared = np.where(valid, (values - mean[:, None]) ** 2, 0.0).sum(axis=1)
    output = np.zeros(values.shape[0], dtype=np.float64)
    np.divide(squared, count, out=output, where=count > 0)
    return np.sqrt(output)


def vertical_ara(
    child: np.ndarray,
    parent: np.ndarray,
    valid: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    denominator = child + parent
    valid = valid & (denominator > 0)
    relation = np.ones_like(child, dtype=np.float64)
    np.divide(2.0 * child, denominator, out=relation, where=valid)
    return relation, valid


def slice_geometry(
    detectors: np.ndarray,
    coordinates: np.ndarray,
    weights: np.ndarray,
) -> dict[str, np.ndarray]:
    time_values = np.unique(coordinates[:, 2])
    activities = np.zeros(
        (detectors.shape[0], len(time_values), 4), dtype=np.float64
    )
    active = np.zeros((detectors.shape[0], len(time_values)), dtype=bool)
    shares = np.zeros_like(activities)

    for index, time_value in enumerate(time_values):
        detector_indices = np.flatnonzero(coordinates[:, 2] == time_value)
        activity = detectors[:, detector_indices] @ weights[detector_indices]
        total = activity.sum(axis=1)
        is_active = total > 0
        activities[:, index] = activity
        shares[is_active, index] = (
            activity[is_active] / total[is_active, None]
        )
        active[:, index] = is_active

    # Tier 1: the whole crossed-versus-aligned spatial relation.
    tier1 = 2.0 * (shares[:, :, 1] + shares[:, :, 3])
    tier1[~active] = 1.0

    # Tier 4: each Tier-3 child decompressed into earlier/later grandchildren.
    before = activities[:, :-1, :]
    after = activities[:, 1:, :]
    denominator = before + after
    tier4_valid = denominator > 0
    tier4 = np.ones_like(denominator)
    np.divide(2.0 * after, denominator, out=tier4, where=tier4_valid)

    return {
        "time_values": time_values,
        "activities": activities,
        "active": active,
        "shares": shares,
        "tier1": tier1,
        "tier4": tier4,
        "tier4_valid": tier4_valid,
    }


def identity_features(geometry: dict[str, np.ndarray]) -> tuple[np.ndarray, list[str]]:
    tier1 = geometry["tier1"]
    active = geometry["active"]
    tier4 = geometry["tier4"]
    tier4_valid = geometry["tier4_valid"]

    columns = [
        masked_mean(tier1, active),
        masked_sd(tier1, active),
    ]
    names = ["tier1_J_mean", "tier1_J_sd"]
    for child_index, child in enumerate(CHILDREN):
        values = tier4[:, :, child_index]
        valid = tier4_valid[:, :, child_index]
        columns.extend((masked_mean(values, valid), masked_sd(values, valid)))
        names.extend((f"tier4_{child}_mean", f"tier4_{child}_sd"))
    return np.column_stack(columns), names


def static_relation_features(
    child_geometry: dict[str, np.ndarray],
    parent_geometry: dict[str, np.ndarray] | None = None,
) -> tuple[np.ndarray, list[str], dict]:
    if parent_geometry is None:
        parent_geometry = child_geometry
    tier4 = child_geometry["tier4"]
    tier4_valid = child_geometry["tier4_valid"]
    tier1 = parent_geometry["tier1"]
    active = parent_geometry["active"]
    parent_window = (tier1[:, :-1] + tier1[:, 1:]) / 2.0
    parent_valid = active[:, :-1] & active[:, 1:]

    columns: list[np.ndarray] = []
    names: list[str] = []
    valid_fractions: dict[str, float] = {}
    relation_min = 2.0
    relation_max = 0.0
    for child_index, child_name in enumerate(CHILDREN):
        child = tier4[:, :, child_index]
        valid = tier4_valid[:, :, child_index] & parent_valid
        relation, valid = vertical_ara(child, parent_window, valid)
        if np.any(valid):
            relation_min = min(relation_min, float(relation[valid].min()))
            relation_max = max(relation_max, float(relation[valid].max()))
        columns.extend(
            (
                masked_mean(relation, valid),
                masked_mean(np.abs(relation - 1.0), valid),
            )
        )
        names.extend(
            (
                f"static_{child_name}_vertical_mean",
                f"static_{child_name}_ridge_distance",
            )
        )
        valid_fractions[child_name] = float(valid.mean())
    valid_fractions["_relation_min"] = relation_min
    valid_fractions["_relation_max"] = relation_max
    return np.column_stack(columns), names, valid_fractions


def travel_relation_features(
    child_geometry: dict[str, np.ndarray],
    parent_geometry: dict[str, np.ndarray] | None = None,
) -> tuple[np.ndarray, np.ndarray, list[str], list[str], dict]:
    if parent_geometry is None:
        parent_geometry = child_geometry
    tier4 = child_geometry["tier4"]
    tier4_valid = child_geometry["tier4_valid"]
    tier1 = parent_geometry["tier1"]
    active = parent_geometry["active"]
    shot_count, window_count, _ = tier4.shape

    positive_columns: list[np.ndarray] = []
    negative_columns: list[np.ndarray] = []
    positive_names: list[str] = []
    negative_names: list[str] = []
    quality: dict[str, float] = {
        "_future_relation_min": 2.0,
        "_future_relation_max": 0.0,
        "_past_relation_min": 2.0,
        "_past_relation_max": 0.0,
    }

    for child_index, child_name in enumerate(CHILDREN):
        child_all = tier4[:, :, child_index]
        child_valid_all = tier4_valid[:, :, child_index]
        for delay in DELAYS:
            positive_relation = np.ones((shot_count, window_count))
            negative_relation = np.ones((shot_count, window_count))
            positive_valid = np.zeros((shot_count, window_count), dtype=bool)
            negative_valid = np.zeros((shot_count, window_count), dtype=bool)

            # A completed Tier-4 window is (t,t+1). Future Tier 1 begins at
            # t+1+delay; past Tier 1 ends at t-delay. Neither reuses the
            # completed window, and both are equally far from its midpoint.
            positive_windows = window_count - delay
            if positive_windows > 0:
                child = child_all[:, :positive_windows]
                valid = (
                    child_valid_all[:, :positive_windows]
                    & active[:, 1 + delay : 1 + delay + positive_windows]
                )
                relation, valid = vertical_ara(
                    child,
                    tier1[:, 1 + delay : 1 + delay + positive_windows],
                    valid,
                )
                positive_relation[:, :positive_windows] = relation
                positive_valid[:, :positive_windows] = valid
                if np.any(valid):
                    quality["_future_relation_min"] = min(
                        quality["_future_relation_min"],
                        float(relation[valid].min()),
                    )
                    quality["_future_relation_max"] = max(
                        quality["_future_relation_max"],
                        float(relation[valid].max()),
                    )

            negative_windows = window_count - delay
            if negative_windows > 0:
                child = child_all[:, delay:]
                valid = (
                    child_valid_all[:, delay:]
                    & active[:, :negative_windows]
                )
                relation, valid = vertical_ara(
                    child, tier1[:, :negative_windows], valid
                )
                negative_relation[:, delay:] = relation
                negative_valid[:, delay:] = valid
                if np.any(valid):
                    quality["_past_relation_min"] = min(
                        quality["_past_relation_min"],
                        float(relation[valid].min()),
                    )
                    quality["_past_relation_max"] = max(
                        quality["_past_relation_max"],
                        float(relation[valid].max()),
                    )

            positive_columns.extend(
                (
                    masked_mean(positive_relation, positive_valid),
                    masked_mean(
                        np.abs(positive_relation - 1.0), positive_valid
                    ),
                )
            )
            negative_columns.extend(
                (
                    masked_mean(negative_relation, negative_valid),
                    masked_mean(
                        np.abs(negative_relation - 1.0), negative_valid
                    ),
                )
            )
            positive_names.extend(
                (
                    f"future_d{delay}_{child_name}_vertical_mean",
                    f"future_d{delay}_{child_name}_ridge_distance",
                )
            )
            negative_names.extend(
                (
                    f"past_d{delay}_{child_name}_vertical_mean",
                    f"past_d{delay}_{child_name}_ridge_distance",
                )
            )
            quality[f"future_d{delay}_{child_name}_valid_fraction"] = float(
                positive_valid.mean()
            )
            quality[f"past_d{delay}_{child_name}_valid_fraction"] = float(
                negative_valid.mean()
            )

    return (
        np.column_stack(positive_columns),
        np.column_stack(negative_columns),
        positive_names,
        negative_names,
        quality,
    )


def build_feature_sets(
    detectors: np.ndarray,
    coordinates: np.ndarray,
    weights: np.ndarray,
) -> tuple[dict[str, np.ndarray], dict]:
    geometry = slice_geometry(detectors, coordinates, weights)
    identity, identity_names = identity_features(geometry)
    static, static_names, static_valid = static_relation_features(geometry)
    future, past, future_names, past_names, travel_valid = (
        travel_relation_features(geometry)
    )

    # Information^3 control: retain the Tier-4 child, but pair it with the
    # next shot's Tier-1 parent. Marginal distributions survive; the local
    # vertical relation does not.
    parent_geometry = dict(geometry)
    parent_geometry["tier1"] = np.roll(geometry["tier1"], -1, axis=0)
    parent_geometry["active"] = np.roll(geometry["active"], -1, axis=0)
    broken_identity, _ = identity_features(parent_geometry)
    broken_static, _, broken_static_valid = static_relation_features(
        geometry, parent_geometry
    )
    broken_future, broken_past, _, _, broken_travel_valid = (
        travel_relation_features(geometry, parent_geometry)
    )
    # Preserve the original Tier-4 identity while replacing only Tier 1.
    broken_identity[:, 2:] = identity[:, 2:]

    q21_features, q21_quality = recursive_features(
        detectors, coordinates, weights
    )
    event_fraction = detectors.mean(axis=1, keepdims=True)

    feature_names = {
        "vertical_state": identity_names + static_names,
        "vertical_travel": identity_names + future_names,
        "vertical_both": identity_names + static_names + future_names,
        "past_travel_control": identity_names + past_names,
        "broken_vertical_both": identity_names + static_names + future_names,
        "q21_child_topology": [
            f"q21_feature_{index:02d}"
            for index in range(q21_features["topology"].shape[1])
        ],
        "event_fraction": ["event_fraction"],
        "vertical_both_plus_count": (
            identity_names + static_names + future_names + ["event_fraction"]
        ),
    }
    feature_sets = {
        "vertical_state": np.column_stack((identity, static)),
        "vertical_travel": np.column_stack((identity, future)),
        "vertical_both": np.column_stack((identity, static, future)),
        "past_travel_control": np.column_stack((identity, past)),
        "broken_vertical_both": np.column_stack(
            (broken_identity, broken_static, broken_future)
        ),
        "q21_child_topology": q21_features["topology"],
        "event_fraction": event_fraction,
        "vertical_both_plus_count": np.column_stack(
            (identity, static, future, event_fraction)
        ),
    }
    quality = {
        "time_slice_count": int(len(geometry["time_values"])),
        "tier1_active_fraction": float(geometry["active"].mean()),
        "tier4_valid_fraction": float(geometry["tier4_valid"].mean()),
        "tier1_mean": float(
            masked_mean(geometry["tier1"], geometry["active"]).mean()
        ),
        "tier1_min": float(geometry["tier1"][geometry["active"]].min()),
        "tier1_max": float(geometry["tier1"][geometry["active"]].max()),
        "tier4_min": float(
            geometry["tier4"][geometry["tier4_valid"]].min()
        ),
        "tier4_max": float(
            geometry["tier4"][geometry["tier4_valid"]].max()
        ),
        "tier4_means": [
            float(
                masked_mean(
                    geometry["tier4"][:, :, index],
                    geometry["tier4_valid"][:, :, index],
                ).mean()
            )
            for index in range(4)
        ],
        "static_valid_fractions": static_valid,
        "travel_valid_fractions": travel_valid,
        "broken_static_valid_fractions": broken_static_valid,
        "broken_travel_valid_fractions": broken_travel_valid,
        "future_ridge_distance_mean": float(future[:, 1::2].mean()),
        "past_ridge_distance_mean": float(past[:, 1::2].mean()),
        "future_minus_past_ridge_distance": float(
            future[:, 1::2].mean() - past[:, 1::2].mean()
        ),
        "broken_future_ridge_distance_mean": float(
            broken_future[:, 1::2].mean()
        ),
        "broken_past_ridge_distance_mean": float(
            broken_past[:, 1::2].mean()
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
    weights = spatial_weights(coordinates)
    return detectors, coordinates, weights, metadata
