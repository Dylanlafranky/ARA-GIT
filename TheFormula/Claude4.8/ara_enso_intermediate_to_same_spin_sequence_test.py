"""Historical ENSO route signature: intermediate disturbance then later deposit.

The prospective refinement is:

    visible upper leaf marker
        -> adjacent anti-phase use / cancellation / dissipation
        -> surviving same-spin deposit
        -> possible gated recycled return

There is no directly measured ENSO lower-lower same-spin coordinate in the
current loader. This diagnostic therefore uses WWV carefully:

    12..18 months  candidate intermediate WWV orientation disturbance
    30..34 months  candidate later WWV battery-deposit proxy

The windows were frozen by earlier diagnostics. They are not rescanned here.
The test uses raw monthly WWV motion and a training-only WWV-history residual.
Matched ordinary origins use only season and prior WWV battery level. Future
months are scored outcomes only.

This is a descriptive route-signature test. It does not prove the physical
identity of either proxy, inject energy into the formula, or measure joules.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import ara_enso_causal_leaf_fall_ablation as leaf
import ara_enso_large_leaf_shape_loss_test as rare
import ara_enso_leaf_to_wwv_abnormality_test as soil
import ara_enso_two_flow_window_test as two_flow
import ara_joint_enso_topology_direction_test as joint
import ara_unified_layered_framework_test as base


HERE = Path(__file__).resolve().parent
OUT = HERE / "ara_enso_intermediate_to_same_spin_sequence_result.json"

EARLY_WINDOW = two_flow.EARLY_WINDOW
LATE_WINDOW = two_flow.LATE_WINDOW
CONTROL_EXCLUSION_RADIUS = 6


def shifted(values: np.ndarray, lag: int = 1) -> np.ndarray:
    result = np.full_like(values, np.nan, dtype=float)
    if lag < len(values):
        result[lag:] = values[:-lag]
    return result


def delta(values: np.ndarray) -> np.ndarray:
    return values - shifted(values)


def safe_ratio(numerator: float, denominator: float) -> float:
    if not math.isfinite(numerator) or not math.isfinite(denominator):
        return float("nan")
    if abs(denominator) < 1e-12:
        return float("nan")
    return float(numerator / denominator)


def safe_corr(left: list[float], right: list[float]) -> float:
    return soil.correlation(np.asarray(left, dtype=float), np.asarray(right, dtype=float))


def window_total_abs(values: np.ndarray, origin: int, delays: tuple[int, ...]) -> float:
    indices = origin + np.asarray(delays)
    if np.max(indices) >= len(values):
        return float("nan")
    return float(np.sum(np.abs(values[indices])))


def window_mean_abs(values: np.ndarray, origin: int, delays: tuple[int, ...]) -> float:
    return window_total_abs(values, origin, delays) / float(len(delays))


def window_sum(values: np.ndarray, origin: int, delays: tuple[int, ...]) -> float:
    indices = origin + np.asarray(delays)
    if np.max(indices) >= len(values):
        return float("nan")
    return float(np.sum(values[indices]))


def month_distance(left: int, right: int) -> int:
    distance = abs(left - right)
    return min(distance, 12 - distance)


def split_name(month: int, cutoff: int) -> str:
    return "train" if month < cutoff else "heldout"


def response_record(
    origin: int,
    keys: list[str],
    marker: np.ndarray,
    cutoff: int,
    battery: np.ndarray,
    orientation: np.ndarray,
    battery_abnormality: np.ndarray,
    orientation_abnormality: np.ndarray,
) -> dict:
    early_battery_mean = window_mean_abs(delta(battery), origin, EARLY_WINDOW)
    late_battery_mean = window_mean_abs(delta(battery), origin, LATE_WINDOW)
    return {
        "origin_index": int(origin),
        "origin_month": keys[origin],
        "split": split_name(origin, cutoff),
        "leaf_marker_size": float(marker[origin]),
        "prior_native_wwv_battery": float(battery[origin - 1]),
        "early_intermediate_12_18m": {
            "total_abs_native_orientation_motion": window_total_abs(
                delta(orientation), origin, EARLY_WINDOW
            ),
            "signed_native_orientation_motion": window_sum(
                delta(orientation), origin, EARLY_WINDOW
            ),
            "mean_abs_orientation_abnormality": window_mean_abs(
                orientation_abnormality, origin, EARLY_WINDOW
            ),
            "mean_abs_native_battery_motion": early_battery_mean,
        },
        "late_candidate_deposit_30_34m": {
            "mean_abs_battery_abnormality": window_mean_abs(
                battery_abnormality, origin, LATE_WINDOW
            ),
            "mean_abs_native_battery_motion": late_battery_mean,
        },
        "late_to_early_native_battery_motion_ratio": safe_ratio(
            late_battery_mean, early_battery_mean
        ),
    }


def choose_controls(
    event_origins: list[int],
    keys: list[str],
    cutoff: int,
    battery: np.ndarray,
) -> list[int]:
    """Choose one ordinary origin per event from the same era, season, and level."""
    occupied = set(event_origins)
    eligible = [
        origin
        for origin in range(max(rare.leaf.MIN_HISTORY + 1, 1), len(keys) - max(LATE_WINDOW))
        if all(abs(origin - event) > CONTROL_EXCLUSION_RADIUS for event in occupied)
    ]
    battery_scale = float(np.std(battery[:cutoff]))
    if battery_scale < 1e-12:
        battery_scale = 1.0

    controls = []
    used = set()
    for event in event_origins:
        event_calendar_month = int(keys[event][4:6])
        event_level = float(battery[event - 1])
        event_split = split_name(event, cutoff)
        candidates = [
            origin
            for origin in eligible
            if origin not in used and split_name(origin, cutoff) == event_split
        ]
        if not candidates:
            continue

        def score(origin: int) -> tuple[float, float, int]:
            calendar = int(keys[origin][4:6])
            season = float(month_distance(event_calendar_month, calendar))
            level = abs(float(battery[origin - 1]) - event_level) / battery_scale
            return season, level, origin

        selected = min(candidates, key=score)
        used.add(selected)
        controls.append(selected)
    return controls


def mean(records: list[dict], path: tuple[str, ...]) -> float:
    values = []
    for record in records:
        current = record
        for key in path:
            current = current[key]
        values.append(float(current))
    return float(np.mean(values))


def paired_lift(
    events: list[dict], controls: list[dict], path: tuple[str, ...]
) -> dict:
    count = min(len(events), len(controls))
    event_values = []
    control_values = []
    for event, control in zip(events[:count], controls[:count]):
        event_value = event
        control_value = control
        for key in path:
            event_value = event_value[key]
            control_value = control_value[key]
        event_values.append(float(event_value))
        control_values.append(float(control_value))
    differences = np.asarray(event_values) - np.asarray(control_values)
    return {
        "pair_n": int(count),
        "event_mean": float(np.mean(event_values)),
        "matched_control_mean": float(np.mean(control_values)),
        "event_minus_control": float(np.mean(differences)),
        "event_greater_than_control_fraction": float(np.mean(differences > 0.0)),
    }


def sequence_summary(events: list[dict], controls: list[dict]) -> dict:
    early_orientation_path = (
        "early_intermediate_12_18m",
        "mean_abs_orientation_abnormality",
    )
    early_native_battery_path = (
        "early_intermediate_12_18m",
        "mean_abs_native_battery_motion",
    )
    late_deposit_path = (
        "late_candidate_deposit_30_34m",
        "mean_abs_battery_abnormality",
    )
    late_native_battery_path = (
        "late_candidate_deposit_30_34m",
        "mean_abs_native_battery_motion",
    )
    count = min(len(events), len(controls))
    sequence_hits = []
    for event, control in zip(events[:count], controls[:count]):
        early_event = event["early_intermediate_12_18m"][
            "mean_abs_orientation_abnormality"
        ]
        early_control = control["early_intermediate_12_18m"][
            "mean_abs_orientation_abnormality"
        ]
        late_event = event["late_candidate_deposit_30_34m"][
            "mean_abs_battery_abnormality"
        ]
        late_control = control["late_candidate_deposit_30_34m"][
            "mean_abs_battery_abnormality"
        ]
        sequence_hits.append(bool(early_event > early_control and late_event > late_control))

    early_orientation = [
        record["early_intermediate_12_18m"]["mean_abs_orientation_abnormality"]
        for record in events
    ]
    early_signed = [
        record["early_intermediate_12_18m"]["signed_native_orientation_motion"]
        for record in events
    ]
    late_deposit = [
        record["late_candidate_deposit_30_34m"]["mean_abs_battery_abnormality"]
        for record in events
    ]
    return {
        "event_n": int(len(events)),
        "matched_control_n": int(len(controls)),
        "paired_early_orientation_disturbance": paired_lift(
            events, controls, early_orientation_path
        ),
        "paired_early_native_battery_motion": paired_lift(
            events, controls, early_native_battery_path
        ),
        "paired_late_candidate_deposit": paired_lift(events, controls, late_deposit_path),
        "paired_late_native_battery_motion": paired_lift(
            events, controls, late_native_battery_path
        ),
        "early_disturbance_to_late_deposit_corr": safe_corr(
            early_orientation, late_deposit
        ),
        "leaf_size_to_early_disturbance_corr": safe_corr(
            [record["leaf_marker_size"] for record in events], early_orientation
        ),
        "leaf_size_to_late_deposit_corr": safe_corr(
            [record["leaf_marker_size"] for record in events], late_deposit
        ),
        "early_signed_orientation_motion": {
            "mean": float(np.mean(early_signed)),
            "positive_fraction": float(np.mean(np.asarray(early_signed) > 0.0)),
            "negative_fraction": float(np.mean(np.asarray(early_signed) < 0.0)),
            "note": "mixed sign would mean the monthly proxy does not isolate one stable observed polarity",
        },
        "late_to_early_native_battery_motion_ratio": {
            "event_mean": mean(events, ("late_to_early_native_battery_motion_ratio",)),
            "matched_control_mean": mean(
                controls, ("late_to_early_native_battery_motion_ratio",)
            ),
            "event_fraction_below_one": float(
                np.mean(
                    [
                        record["late_to_early_native_battery_motion_ratio"] < 1.0
                        for record in events
                    ]
                )
            ),
            "interpretation": "below one means later per-month WWV battery motion is smaller than earlier per-month WWV battery motion",
        },
        "paired_sequence_hit_fraction": float(np.mean(sequence_hits)),
    }


def main() -> None:
    nodes = joint.build_nodes()
    keys = two_flow.aligned_keys()
    if len(keys) != len(nodes[0].values):
        raise RuntimeError("Reconstructed ENSO keys do not match unified aligned series")
    n = len(keys)
    cutoff = int(n * 0.60)

    nino = base.standardize_from_training(nodes[0].values, cutoff)
    marker = np.asarray(leaf.causal_leaf_state(nino)["leaf"], dtype=float)
    peak_origins = [
        month
        for month in rare.leaf_peaks(marker)
        if month + max(LATE_WINDOW) < n
    ]

    # Native WWV source values were divided by 1e14 by the loader.
    west_native = np.asarray(nodes[2].values, dtype=float)
    east_native = np.asarray(nodes[3].values, dtype=float)
    battery_native = west_native + east_native
    orientation_native = east_native - west_native

    west_z = base.standardize_from_training(west_native, cutoff)
    east_z = base.standardize_from_training(east_native, cutoff)
    battery_residual, _ = soil.ar_innovation(0.5 * (west_z + east_z), cutoff)
    orientation_residual, _ = soil.ar_innovation(east_z - west_z, cutoff)
    battery_abnormality = np.abs(battery_residual)
    orientation_abnormality = np.abs(orientation_residual)

    control_origins = choose_controls(peak_origins, keys, cutoff, battery_native)
    events = [
        response_record(
            origin,
            keys,
            marker,
            cutoff,
            battery_native,
            orientation_native,
            battery_abnormality,
            orientation_abnormality,
        )
        for origin in peak_origins
    ]
    controls = [
        response_record(
            origin,
            keys,
            marker,
            cutoff,
            battery_native,
            orientation_native,
            battery_abnormality,
            orientation_abnormality,
        )
        for origin in control_origins
    ]

    result = {
        "test": "historical intermediate-disturbance then later-deposit ENSO route signature",
        "status": "descriptive proxy test; not a predictor and not causal proof",
        "strict_causal_checklist": {
            "leaf_marker": "existing causal harmonic marker from NINO values at or before origin",
            "event_rule": "local causal leaf-marker peaks after fixed marker warmup",
            "frozen_windows": {
                "candidate_intermediate_orientation_disturbance_months": list(EARLY_WINDOW),
                "candidate_later_same_spin_deposit_proxy_months": list(LATE_WINDOW),
            },
            "wwv_history_baseline": "training-only AR using prior WWV values at lags 1,2,3,6",
            "matched_controls": "same-era ordinary origins matched by calendar month then prior raw WWV battery level",
            "future_outcomes": "used only after event and control origins are declared",
            "smoothing": False,
            "fft_or_hilbert": False,
            "synthetic_energy_injection": False,
            "formula_modified": False,
            "january_2024_outcome_used": False,
        },
        "measurement_limits": {
            "direct_lower_lower_same_spin_coordinate_available": False,
            "intermediate_proxy": "12-18m WWV east-west orientation disturbance",
            "later_deposit_proxy": "30-34m WWV battery disturbance",
            "wwv_is_energy_joules": False,
            "ratio_meaning": "relative native WWV volume motion per month, not an energy fraction",
        },
        "data": {
            "overlapping_months": n,
            "training_cutoff_index": cutoff,
            "completed_leaf_peak_event_n": len(events),
            "matched_control_n": len(controls),
            "excluded_prospective_event": "2024-01",
        },
        "summary": sequence_summary(events, controls),
        "events": events,
        "matched_controls": controls,
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("strict causal checklist")
    print(json.dumps(result["strict_causal_checklist"], indent=2))
    print()
    print("measurement limits")
    print(json.dumps(result["measurement_limits"], indent=2))
    print()
    print("summary")
    print(json.dumps(result["summary"], indent=2))
    print()
    print("events")
    for event in events:
        early = event["early_intermediate_12_18m"]
        late = event["late_candidate_deposit_30_34m"]
        print(
            " ",
            event["origin_month"],
            f"leaf={event['leaf_marker_size']:.4f}",
            f"early_orient_abn={early['mean_abs_orientation_abnormality']:.3f}",
            f"late_battery_abn={late['mean_abs_battery_abnormality']:.3f}",
            f"late/early_native={event['late_to_early_native_battery_motion_ratio']:.3f}",
        )


if __name__ == "__main__":
    main()
