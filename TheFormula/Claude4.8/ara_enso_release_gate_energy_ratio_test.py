"""Frozen ENSO release-gate and native WWV-motion diagnostic.

This follows the two-flow window test without changing its windows:

    12..18 months  possible smaller/faster upflow into WWV
    30..34 months  possible slower recycled battery disturbance

The test asks:

1. Does either pulse concentrate when a transparent causal release/end gate is
   open?
2. How large is the observed WWV volume motion in the early pulse relative to
   the late pulse?

WWV is a warm-water-volume proxy, not energy in joules. Ratios reported here
are ratios of measured native WWV volume motion. This is a diagnostic
association test, not a predictor and not a causal proof.
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
OUT = HERE / "ara_enso_release_gate_energy_ratio_result.json"

EARLY_WINDOW = two_flow.EARLY_WINDOW
LATE_WINDOW = two_flow.LATE_WINDOW


def shifted(values: np.ndarray, lag: int = 1) -> np.ndarray:
    result = np.full_like(values, np.nan, dtype=float)
    if lag < len(values):
        result[lag:] = values[:-lag]
    return result


def delta(values: np.ndarray) -> np.ndarray:
    return values - shifted(values, 1)


def standardize(values: np.ndarray, cutoff: int) -> np.ndarray:
    return base.standardize_from_training(values, cutoff)


def magnitude_release_gate(values: np.ndarray, cutoff: int) -> tuple[np.ndarray, dict]:
    """Gate when an active signed feeder is relaxing toward zero."""
    z = standardize(values, cutoff)
    previous = shifted(z)
    threshold = float(np.nanmedian(np.abs(z[:cutoff])))
    gate = (np.abs(previous) >= threshold) & (np.abs(z) < np.abs(previous))
    return gate, {
        "rule": "abs(previous_z) >= train_median_abs_z and abs(current_z) < abs(previous_z)",
        "training_threshold": threshold,
    }


def positive_burst_release_gate(values: np.ndarray, cutoff: int) -> tuple[np.ndarray, dict]:
    """Gate when a positive activity burst has started to decay."""
    z = standardize(values, cutoff)
    previous = shifted(z)
    threshold = float(np.nanmedian(z[:cutoff]))
    gate = (previous >= threshold) & (z < previous)
    return gate, {
        "rule": "previous_z >= train_median_z and current_z < previous_z",
        "training_threshold": threshold,
    }


def battery_discharge_gate(values: np.ndarray, cutoff: int) -> tuple[np.ndarray, dict]:
    """Gate when an above-median WWV battery is discharging."""
    previous = shifted(values)
    threshold = float(np.nanmedian(values[:cutoff]))
    gate = (previous >= threshold) & (values < previous)
    return gate, {
        "rule": "previous_battery >= train_median_battery and current_battery < previous_battery",
        "training_threshold": threshold,
    }


def safe_weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    valid = np.isfinite(values) & np.isfinite(weights) & (weights >= 0.0)
    values = values[valid]
    weights = weights[valid]
    if len(values) == 0 or np.sum(weights) < 1e-12:
        return float("nan")
    return float(np.sum(values * weights) / np.sum(weights))


def ratio(numerator: float, denominator: float) -> float:
    if not math.isfinite(numerator) or not math.isfinite(denominator) or abs(denominator) < 1e-12:
        return float("nan")
    return float(numerator / denominator)


def complete_origins(origins: np.ndarray, delays: tuple[int, ...], n: int) -> np.ndarray:
    return origins[origins + max(delays) < n]


def native_window_motion(
    marker: np.ndarray,
    battery_delta: np.ndarray,
    orientation_delta: np.ndarray,
    origins: np.ndarray,
    delays: tuple[int, ...],
) -> dict:
    origins = complete_origins(origins, delays, len(marker))
    battery_abs_rows = []
    battery_signed_rows = []
    orientation_abs_rows = []
    for origin in origins:
        months = origin + np.asarray(delays)
        battery_abs_rows.append(float(np.sum(np.abs(battery_delta[months]))))
        battery_signed_rows.append(float(np.sum(battery_delta[months])))
        orientation_abs_rows.append(float(np.sum(np.abs(orientation_delta[months]))))
    battery_abs = np.asarray(battery_abs_rows, dtype=float)
    battery_signed = np.asarray(battery_signed_rows, dtype=float)
    orientation_abs = np.asarray(orientation_abs_rows, dtype=float)
    weights = marker[origins]
    duration = float(len(delays))
    return {
        "complete_origin_n": int(len(origins)),
        "window_months": list(delays),
        "marker_weighted_total_abs_battery_motion": safe_weighted_mean(battery_abs, weights),
        "marker_weighted_mean_monthly_abs_battery_motion": safe_weighted_mean(
            battery_abs / duration, weights
        ),
        "plain_total_abs_battery_motion": float(np.nanmean(battery_abs)),
        "plain_mean_monthly_abs_battery_motion": float(np.nanmean(battery_abs / duration)),
        "marker_weighted_total_signed_battery_motion": safe_weighted_mean(battery_signed, weights),
        "marker_weighted_total_abs_orientation_motion": safe_weighted_mean(
            orientation_abs, weights
        ),
        "native_unit_note": "WWV source values are scaled by loader to source_volume / 1e14",
    }


def gate_concentration(
    marker: np.ndarray,
    battery_delta: np.ndarray,
    battery_abnormality: np.ndarray,
    origins: np.ndarray,
    delays: tuple[int, ...],
    gate: np.ndarray,
) -> dict:
    origins = complete_origins(origins, delays, len(marker))
    response_months = np.concatenate([origin + np.asarray(delays) for origin in origins])
    weights = np.repeat(marker[origins], len(delays))
    gate_cells = gate[response_months]
    abs_motion = np.abs(battery_delta[response_months])
    abnormality = battery_abnormality[response_months]

    plain_open_fraction = float(np.mean(gate_cells))
    weighted_open_fraction = safe_weighted_mean(gate_cells.astype(float), weights)
    open_weights = weights * gate_cells
    closed_weights = weights * (~gate_cells)
    return {
        "response_cell_n": int(len(response_months)),
        "plain_gate_open_fraction": plain_open_fraction,
        "marker_weighted_gate_open_fraction": weighted_open_fraction,
        "marker_weighted_gate_concentration_lift": ratio(
            weighted_open_fraction, plain_open_fraction
        ),
        "marker_weighted_native_abs_battery_motion_gate_open": safe_weighted_mean(
            abs_motion, open_weights
        ),
        "marker_weighted_native_abs_battery_motion_gate_closed": safe_weighted_mean(
            abs_motion, closed_weights
        ),
        "gate_open_to_closed_native_motion_ratio": ratio(
            safe_weighted_mean(abs_motion, open_weights),
            safe_weighted_mean(abs_motion, closed_weights),
        ),
        "marker_weighted_battery_abnormality_gate_open": safe_weighted_mean(
            abnormality, open_weights
        ),
        "marker_weighted_battery_abnormality_gate_closed": safe_weighted_mean(
            abnormality, closed_weights
        ),
    }


def characterize_window(
    marker: np.ndarray,
    battery_delta: np.ndarray,
    orientation_delta: np.ndarray,
    battery_abnormality: np.ndarray,
    origins: np.ndarray,
    delays: tuple[int, ...],
    gates: dict[str, np.ndarray],
) -> dict:
    return {
        "native_wwv_motion": native_window_motion(
            marker, battery_delta, orientation_delta, origins, delays
        ),
        "release_gate_concentration": {
            name: gate_concentration(
                marker, battery_delta, battery_abnormality, origins, delays, gate
            )
            for name, gate in gates.items()
        },
    }


def compare_motion(early: dict, late: dict) -> dict:
    left = early["native_wwv_motion"]
    right = late["native_wwv_motion"]
    return {
        "early_to_late_total_abs_battery_motion_ratio": ratio(
            left["marker_weighted_total_abs_battery_motion"],
            right["marker_weighted_total_abs_battery_motion"],
        ),
        "early_to_late_mean_monthly_abs_battery_motion_ratio": ratio(
            left["marker_weighted_mean_monthly_abs_battery_motion"],
            right["marker_weighted_mean_monthly_abs_battery_motion"],
        ),
        "early_to_late_total_abs_orientation_motion_ratio": ratio(
            left["marker_weighted_total_abs_orientation_motion"],
            right["marker_weighted_total_abs_orientation_motion"],
        ),
    }


def main() -> None:
    nodes = joint.build_nodes()
    keys = two_flow.aligned_keys()
    if len(keys) != len(nodes[0].values):
        raise RuntimeError("Reconstructed ENSO keys do not match unified aligned series")

    n = len(keys)
    cutoff = int(n * 0.60)
    nino = standardize(nodes[0].values, cutoff)
    marker = np.asarray(leaf.causal_leaf_state(nino)["leaf"], dtype=float)
    abnormalities, _ = prior.build_abnormalities(nodes, cutoff)

    # Native WWV source values have already been divided by 1e14 by the loader.
    west = np.asarray(nodes[2].values, dtype=float)
    east = np.asarray(nodes[3].values, dtype=float)
    battery = west + east
    orientation = east - west
    battery_delta = delta(battery)
    orientation_delta = delta(orientation)

    mjo = two_flow.fill_missing_from_training_mean(
        two_flow.values_for_keys(two_flow.load_mjo_monthly_max_amp("mjo_rmm.txt"), keys),
        cutoff,
    )
    iod = np.asarray(nodes[4].values, dtype=float)

    iod_gate, iod_gate_meta = magnitude_release_gate(iod, cutoff)
    mjo_gate, mjo_gate_meta = positive_burst_release_gate(mjo, cutoff)
    wwv_gate, wwv_gate_meta = battery_discharge_gate(battery, cutoff)
    gates = {
        "IOD_lateral_magnitude_release": iod_gate,
        "MJO_candidate_burst_release": mjo_gate,
        "WWV_battery_discharge": wwv_gate,
    }

    periods = {
        "visible_pre_cutoff_after_marker_warmup": np.arange(leaf.MIN_HISTORY, cutoff),
        "heldout": np.arange(cutoff, n),
    }
    result = {
        "test": "frozen release-gate concentration and native WWV-motion ratio",
        "status": "diagnostic association test; not a predictor and not causal proof",
        "strict_causal_checklist": {
            "windows_frozen_before_scoring": {
                "possible_lower_upflow_months": list(EARLY_WINDOW),
                "possible_recycled_return_months": list(LATE_WINDOW),
            },
            "release_gates": "current and previous raw measured channel values only",
            "native_wwv_motion": "raw monthly WWV source-volume motion; no smoothing",
            "synthetic_energy_injection": False,
            "formula_modified": False,
            "future_value_used_to_construct_marker": False,
            "fft_or_hilbert": False,
            "smoothing": False,
        },
        "measurement_limits": {
            "wwv_is_energy_joules": False,
            "wwv_ratio_meaning": "relative measured warm-water-volume motion, not an energy fraction",
            "direct_measured_rung_beneath_wwv_available": False,
            "mjo_role": "finer/faster activity candidate only",
            "iod_role": "lateral feeder comparison only",
        },
        "gate_definitions": {
            "IOD_lateral_magnitude_release": iod_gate_meta,
            "MJO_candidate_burst_release": mjo_gate_meta,
            "WWV_battery_discharge": wwv_gate_meta,
        },
        "periods": {},
    }

    for period_name, origins in periods.items():
        early = characterize_window(
            marker,
            battery_delta,
            orientation_delta,
            abnormalities["battery_abnormality"],
            origins,
            EARLY_WINDOW,
            gates,
        )
        late = characterize_window(
            marker,
            battery_delta,
            orientation_delta,
            abnormalities["battery_abnormality"],
            origins,
            LATE_WINDOW,
            gates,
        )
        result["periods"][period_name] = {
            "possible_lower_upflow_12_18m": early,
            "possible_recycled_return_30_34m": late,
            "native_motion_comparison": compare_motion(early, late),
        }

    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("strict causal checklist")
    print(json.dumps(result["strict_causal_checklist"], indent=2))
    for period_name, payload in result["periods"].items():
        print()
        print(period_name)
        comparison = payload["native_motion_comparison"]
        print(
            "  early/late native WWV volume motion",
            f"total={comparison['early_to_late_total_abs_battery_motion_ratio']:.3f}",
            f"per_month={comparison['early_to_late_mean_monthly_abs_battery_motion_ratio']:.3f}",
            f"orientation_total={comparison['early_to_late_total_abs_orientation_motion_ratio']:.3f}",
        )
        for window_name in ("possible_lower_upflow_12_18m", "possible_recycled_return_30_34m"):
            print(" ", window_name)
            window = payload[window_name]
            native = window["native_wwv_motion"]
            print(
                "    native",
                f"total_abs={native['marker_weighted_total_abs_battery_motion']:.3f}",
                f"per_month_abs={native['marker_weighted_mean_monthly_abs_battery_motion']:.3f}",
                f"signed_total={native['marker_weighted_total_signed_battery_motion']:+.3f}",
            )
            for gate_name, gate in window["release_gate_concentration"].items():
                print(
                    "   ",
                    gate_name,
                    f"concentration={gate['marker_weighted_gate_concentration_lift']:.3f}",
                    f"open/closed_motion={gate['gate_open_to_closed_native_motion_ratio']:.3f}",
                )


if __name__ == "__main__":
    main()
