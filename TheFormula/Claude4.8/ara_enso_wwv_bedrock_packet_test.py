"""Raw WWV event medoid test: recurring geometry versus packet size.

This script separates:

    geometric bedrock = one real train-only WWV discharge episode (the medoid)
    energy-flow proxy = each episode's native WWV volume motion

It does not smooth or average raw event waveforms into a template. Event onsets
are causal: the prior WWV battery level is above its train-only median, then
monthly WWV motion turns downward. A causal cooldown prevents one discharge
episode from being counted several times.

Held-out events are compared with ordinary held-out months matched by calendar
month and prior WWV battery level. The result is a descriptive geometry test,
not a forecast and not a measurement of energy in joules.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import ara_enso_causal_leaf_fall_ablation as leaf
import ara_enso_leaf_to_wwv_abnormality_test as prior
import ara_enso_two_flow_window_test as two_flow
import ara_joint_enso_topology_direction_test as joint
import ara_unified_layered_framework_test as base


HERE = Path(__file__).resolve().parent
OUT = HERE / "ara_enso_wwv_bedrock_packet_result.json"

PROFILE_MONTHS = 7
COOLDOWN_MONTHS = PROFILE_MONTHS - 1
EARLY_WINDOW = two_flow.EARLY_WINDOW
LATE_WINDOW = two_flow.LATE_WINDOW


def shifted(values: np.ndarray, lag: int = 1) -> np.ndarray:
    result = np.full_like(values, np.nan, dtype=float)
    if lag < len(values):
        result[lag:] = values[:-lag]
    return result


def correlation(left: np.ndarray, right: np.ndarray) -> float:
    return prior.correlation(np.asarray(left, dtype=float), np.asarray(right, dtype=float))


def cosine(left: np.ndarray, right: np.ndarray) -> float:
    denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
    if denominator < 1e-12:
        return float("nan")
    return float(np.dot(left, right) / denominator)


def normalize(profile: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(profile))
    if norm < 1e-12:
        return np.zeros_like(profile)
    return profile / norm


def detect_discharge_onsets(battery: np.ndarray, cutoff: int) -> tuple[np.ndarray, dict]:
    """Causally accept the first downward turn, then wait one full profile."""
    motion = battery - shifted(battery)
    previous_motion = shifted(motion)
    previous_battery = shifted(battery)
    threshold = float(np.nanmedian(battery[:cutoff]))
    candidates = np.where(
        (previous_battery >= threshold)
        & (previous_motion >= 0.0)
        & (motion < 0.0)
    )[0]
    accepted = []
    for month in candidates:
        if not accepted or month - accepted[-1] > COOLDOWN_MONTHS:
            accepted.append(int(month))
    return np.asarray(accepted, dtype=int), {
        "rule": (
            "previous battery >= train median; previous monthly motion >= 0; "
            "current monthly motion < 0; then causal 6-month cooldown"
        ),
        "training_battery_median": threshold,
        "candidate_n_before_cooldown": int(len(candidates)),
        "accepted_n_after_cooldown": int(len(accepted)),
    }


def profile_at(values: np.ndarray, onset: int) -> np.ndarray:
    """Return seven raw monthly increments beginning at the causal onset."""
    return values[onset : onset + PROFILE_MONTHS] - values[
        onset - 1 : onset + PROFILE_MONTHS - 1
    ]


def event_record(
    onset: int,
    keys: list[str],
    battery: np.ndarray,
    orientation: np.ndarray,
) -> dict:
    battery_profile = profile_at(battery, onset)
    orientation_profile = profile_at(orientation, onset)
    return {
        "onset_index": int(onset),
        "onset_month": keys[onset],
        "calendar_month": int(keys[onset][4:6]),
        "previous_battery": float(battery[onset - 1]),
        "battery_profile_raw": [float(value) for value in battery_profile],
        "battery_profile_normalized": [float(value) for value in normalize(battery_profile)],
        "orientation_profile_raw": [float(value) for value in orientation_profile],
        "total_abs_battery_motion": float(np.sum(np.abs(battery_profile))),
        "net_battery_motion": float(np.sum(battery_profile)),
        "total_abs_orientation_motion": float(np.sum(np.abs(orientation_profile))),
        "discharge_month_count": int(np.sum(battery_profile < 0.0)),
    }


def medoid_record(records: list[dict]) -> tuple[dict, list[float]]:
    profiles = np.asarray([record["battery_profile_normalized"] for record in records])
    matrix = profiles @ profiles.T
    means = np.mean(matrix, axis=1)
    index = int(np.argmax(means))
    return records[index], [float(value) for value in means]


def circular_month_distance(left: int, right: int) -> int:
    distance = abs(left - right)
    return min(distance, 12 - distance)


def select_matched_controls(
    events: list[dict],
    event_onsets: np.ndarray,
    keys: list[str],
    battery: np.ndarray,
    cutoff: int,
) -> list[int]:
    """Match ordinary held-out months by season and prior battery level."""
    all_onsets = set(int(value) for value in event_onsets)
    eligible = []
    battery_scale = float(np.nanstd(battery[:cutoff]))
    if battery_scale < 1e-12:
        battery_scale = 1.0
    for month in range(max(cutoff, 1), len(battery) - PROFILE_MONTHS + 1):
        if month in all_onsets:
            continue
        if any(abs(month - onset) <= COOLDOWN_MONTHS for onset in all_onsets):
            continue
        eligible.append(month)

    chosen = []
    used = set()
    for event in events:
        candidates = [month for month in eligible if month not in used]
        if not candidates:
            break
        event_month = int(event["calendar_month"])
        event_level = float(event["previous_battery"])

        def score(month: int) -> tuple[float, float]:
            candidate_month = int(keys[month][4:6])
            season = circular_month_distance(event_month, candidate_month)
            level = abs(float(battery[month - 1]) - event_level) / battery_scale
            return season, level

        selected = min(candidates, key=score)
        used.add(selected)
        chosen.append(selected)
    return chosen


def paired_sign_flip_pvalue(differences: np.ndarray, iterations: int = 20000) -> float:
    """Deterministic paired sign-flip test for event versus control similarity."""
    differences = differences[np.isfinite(differences)]
    if len(differences) == 0:
        return float("nan")
    observed = float(np.mean(differences))
    rng = np.random.default_rng(20260601)
    signs = rng.choice((-1.0, 1.0), size=(iterations, len(differences)))
    null = np.mean(signs * differences[None, :], axis=1)
    return float((1 + np.sum(null >= observed)) / (iterations + 1))


def event_similarity_summary(
    event_records: list[dict],
    control_records: list[dict],
    medoid: dict,
) -> dict:
    bedrock = np.asarray(medoid["battery_profile_normalized"], dtype=float)
    event_similarity = np.asarray(
        [
            cosine(np.asarray(record["battery_profile_normalized"], dtype=float), bedrock)
            for record in event_records
        ]
    )
    control_similarity = np.asarray(
        [
            cosine(np.asarray(record["battery_profile_normalized"], dtype=float), bedrock)
            for record in control_records
        ]
    )
    pair_n = min(len(event_similarity), len(control_similarity))
    differences = event_similarity[:pair_n] - control_similarity[:pair_n]
    return {
        "event_n": int(len(event_similarity)),
        "control_n": int(len(control_similarity)),
        "mean_event_cosine_similarity": float(np.nanmean(event_similarity)),
        "mean_matched_control_cosine_similarity": float(np.nanmean(control_similarity)),
        "event_minus_control_similarity": float(
            np.nanmean(event_similarity) - np.nanmean(control_similarity)
        ),
        "paired_sign_flip_pvalue_one_sided": paired_sign_flip_pvalue(differences),
        "event_cosine_similarity": [float(value) for value in event_similarity],
        "matched_control_cosine_similarity": [float(value) for value in control_similarity],
    }


def packet_size_groups(train_records: list[dict], heldout_records: list[dict], medoid: dict) -> dict:
    training_sizes = np.asarray([record["total_abs_battery_motion"] for record in train_records])
    low, high = np.quantile(training_sizes, [1.0 / 3.0, 2.0 / 3.0])
    bedrock = np.asarray(medoid["battery_profile_normalized"], dtype=float)
    groups: dict[str, list[dict]] = {"small": [], "middle": [], "large": []}
    for record in heldout_records:
        size = float(record["total_abs_battery_motion"])
        name = "small" if size <= low else "middle" if size <= high else "large"
        groups[name].append(record)

    payload = {}
    for name, records in groups.items():
        similarities = [
            cosine(np.asarray(record["battery_profile_normalized"], dtype=float), bedrock)
            for record in records
        ]
        payload[name] = {
            "n": int(len(records)),
            "mean_native_total_abs_battery_motion": float(
                np.mean([record["total_abs_battery_motion"] for record in records])
            )
            if records
            else float("nan"),
            "mean_bedrock_cosine_similarity": float(np.mean(similarities))
            if similarities
            else float("nan"),
        }
    return {
        "training_native_motion_tercile_thresholds": [float(low), float(high)],
        "heldout_groups": payload,
    }


def preceding_marker_score(marker: np.ndarray, onset: int, delays: tuple[int, ...]) -> float:
    indices = np.asarray([onset - delay for delay in delays if onset - delay >= 0])
    if len(indices) == 0:
        return float("nan")
    return float(np.mean(marker[indices]))


def frozen_leaf_overlay(records: list[dict], marker: np.ndarray) -> dict:
    packet = np.asarray([record["total_abs_battery_motion"] for record in records])
    early = np.asarray(
        [preceding_marker_score(marker, int(record["onset_index"]), EARLY_WINDOW) for record in records]
    )
    late = np.asarray(
        [preceding_marker_score(marker, int(record["onset_index"]), LATE_WINDOW) for record in records]
    )
    return {
        "n": int(len(records)),
        "possible_lower_upflow_12_18m": {
            "marker_to_native_packet_size_corr": correlation(early, packet),
            "mean_preceding_marker": float(np.nanmean(early)),
        },
        "possible_recycled_return_30_34m": {
            "marker_to_native_packet_size_corr": correlation(late, packet),
            "mean_preceding_marker": float(np.nanmean(late)),
        },
    }


def descriptive_profile_length_sensitivity(
    keys: list[str],
    battery: np.ndarray,
    orientation: np.ndarray,
    cutoff: int,
) -> list[dict]:
    """Show whether the geometry result depends on the declared seven-month box."""
    global PROFILE_MONTHS, COOLDOWN_MONTHS
    original_profile = PROFILE_MONTHS
    original_cooldown = COOLDOWN_MONTHS
    rows = []
    try:
        for profile_months in (3, 5, 7, 9):
            PROFILE_MONTHS = profile_months
            COOLDOWN_MONTHS = profile_months - 1
            onsets, _ = detect_discharge_onsets(battery, cutoff)
            train_onsets = onsets[
                (onsets > 0) & (onsets + PROFILE_MONTHS <= cutoff)
            ]
            heldout_onsets = onsets[
                (onsets >= cutoff) & (onsets + PROFILE_MONTHS <= len(battery))
            ]
            train_records = [
                event_record(int(onset), keys, battery, orientation)
                for onset in train_onsets
            ]
            heldout_records = [
                event_record(int(onset), keys, battery, orientation)
                for onset in heldout_onsets
            ]
            medoid, _ = medoid_record(train_records)
            controls = select_matched_controls(
                heldout_records, onsets, keys, battery, cutoff
            )
            control_records = [
                event_record(int(onset), keys, battery, orientation)
                for onset in controls
            ]
            geometry = event_similarity_summary(
                heldout_records, control_records, medoid
            )
            bedrock = np.asarray(medoid["battery_profile_normalized"])
            packet_sizes = np.asarray(
                [record["total_abs_battery_motion"] for record in heldout_records]
            )
            similarities = np.asarray(
                [
                    cosine(
                        np.asarray(record["battery_profile_normalized"]),
                        bedrock,
                    )
                    for record in heldout_records
                ]
            )
            rows.append(
                {
                    "profile_months": profile_months,
                    "status": "descriptive sensitivity only; not a selected winner",
                    "train_event_n": int(len(train_records)),
                    "heldout_event_n": int(len(heldout_records)),
                    "mean_event_cosine_similarity": geometry[
                        "mean_event_cosine_similarity"
                    ],
                    "mean_matched_control_cosine_similarity": geometry[
                        "mean_matched_control_cosine_similarity"
                    ],
                    "event_minus_control_similarity": geometry[
                        "event_minus_control_similarity"
                    ],
                    "paired_sign_flip_pvalue_one_sided": geometry[
                        "paired_sign_flip_pvalue_one_sided"
                    ],
                    "packet_size_to_bedrock_similarity_corr": correlation(
                        packet_sizes, similarities
                    ),
                }
            )
    finally:
        PROFILE_MONTHS = original_profile
        COOLDOWN_MONTHS = original_cooldown
    return rows


def main() -> None:
    nodes = joint.build_nodes()
    keys = two_flow.aligned_keys()
    if len(keys) != len(nodes[0].values):
        raise RuntimeError("Reconstructed ENSO keys do not match unified aligned series")

    n = len(keys)
    cutoff = int(n * 0.60)
    west = np.asarray(nodes[2].values, dtype=float)
    east = np.asarray(nodes[3].values, dtype=float)
    battery = west + east
    orientation = east - west

    nino = base.standardize_from_training(nodes[0].values, cutoff)
    marker = np.asarray(leaf.causal_leaf_state(nino)["leaf"], dtype=float)

    onsets, detector = detect_discharge_onsets(battery, cutoff)
    train_onsets = onsets[(onsets > 0) & (onsets + PROFILE_MONTHS <= cutoff)]
    heldout_onsets = onsets[
        (onsets >= cutoff) & (onsets + PROFILE_MONTHS <= n)
    ]
    train_records = [
        event_record(int(onset), keys, battery, orientation) for onset in train_onsets
    ]
    heldout_records = [
        event_record(int(onset), keys, battery, orientation) for onset in heldout_onsets
    ]
    medoid, medoid_similarity = medoid_record(train_records)

    controls = select_matched_controls(heldout_records, onsets, keys, battery, cutoff)
    control_records = [
        event_record(int(onset), keys, battery, orientation) for onset in controls
    ]

    result = {
        "test": "raw WWV geometric bedrock medoid versus variable native packet size",
        "status": "descriptive heldout geometry test; not a predictor and not causal proof",
        "strict_causal_checklist": {
            "event_onset": "current and previous raw monthly WWV battery values only",
            "cooldown": f"first accepted onset then {COOLDOWN_MONTHS}-month causal cooldown",
            "bedrock": "single real train-only medoid event; not an averaged waveform",
            "heldout_control": "ordinary heldout month matched by season and prior WWV battery level",
            "raw_profile": f"{PROFILE_MONTHS} raw monthly WWV increments beginning at onset",
            "smoothing": False,
            "fft_or_hilbert": False,
            "synthetic_energy_injection": False,
            "formula_modified": False,
        },
        "measurement_limits": {
            "wwv_is_energy_joules": False,
            "packet_size_meaning": "native WWV volume motion scaled by source loader / 1e14",
            "event_family_meaning": "monthly WWV discharge-turn family only",
        },
        "event_detector": detector,
        "counts": {
            "train_event_n": int(len(train_records)),
            "heldout_event_n": int(len(heldout_records)),
            "heldout_matched_control_n": int(len(control_records)),
        },
        "train_only_bedrock_medoid": medoid,
        "train_medoid_mean_similarity_by_event": medoid_similarity,
        "heldout_geometry": event_similarity_summary(heldout_records, control_records, medoid),
        "heldout_packet_size_groups": packet_size_groups(train_records, heldout_records, medoid),
        "heldout_frozen_leaf_overlay": frozen_leaf_overlay(heldout_records, marker),
        "descriptive_profile_length_sensitivity": descriptive_profile_length_sensitivity(
            keys, battery, orientation, cutoff
        ),
        "heldout_events": heldout_records,
        "heldout_matched_controls": control_records,
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("strict causal checklist")
    print(json.dumps(result["strict_causal_checklist"], indent=2))
    print()
    print("counts", result["counts"])
    medoid = result["train_only_bedrock_medoid"]
    print("train-only raw medoid", medoid["onset_month"], medoid["battery_profile_raw"])
    geometry = result["heldout_geometry"]
    print(
        "heldout geometry",
        f"events={geometry['mean_event_cosine_similarity']:+.3f}",
        f"controls={geometry['mean_matched_control_cosine_similarity']:+.3f}",
        f"lift={geometry['event_minus_control_similarity']:+.3f}",
        f"p={geometry['paired_sign_flip_pvalue_one_sided']:.4f}",
    )
    print("heldout size groups")
    for name, payload in result["heldout_packet_size_groups"]["heldout_groups"].items():
        print(
            " ",
            name,
            f"n={payload['n']}",
            f"native_motion={payload['mean_native_total_abs_battery_motion']:.3f}",
            f"bedrock_similarity={payload['mean_bedrock_cosine_similarity']:+.3f}",
        )
    print("frozen leaf overlay")
    for name, payload in result["heldout_frozen_leaf_overlay"].items():
        if name == "n":
            continue
        print(
            " ",
            name,
            f"marker_to_packet_corr={payload['marker_to_native_packet_size_corr']:+.3f}",
        )
    print("descriptive profile-length sensitivity")
    for payload in result["descriptive_profile_length_sensitivity"]:
        print(
            " ",
            f"{payload['profile_months']}m",
            f"event={payload['mean_event_cosine_similarity']:+.3f}",
            f"control={payload['mean_matched_control_cosine_similarity']:+.3f}",
            f"lift={payload['event_minus_control_similarity']:+.3f}",
            f"p={payload['paired_sign_flip_pvalue_one_sided']:.4f}",
            f"size_shape={payload['packet_size_to_bedrock_similarity_corr']:+.3f}",
        )


if __name__ == "__main__":
    main()
