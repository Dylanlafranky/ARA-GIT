"""Frozen-window diagnostic for two possible ENSO cross-rung flows.

The prior leaf-to-WWV diagnostic exposed two candidate delay regions:

    12..18 months  possible lower-rung upflow
    30..34 months  possible recycled brown-leaf return

Those windows are frozen before this script scores them. This remains a
diagnostic association test, not a predictor. It does not inject energy,
modify the formula, smooth the target, or use future values to construct the
causal brown marker.

The measured WWV outcomes are raw monthly residual magnitudes after removing
ordinary WWV history with a training-only AR baseline. The finer feeder check
uses the maximum raw daily MJO RMM amplitude inside each calendar month. WWV
is monthly, so daily activity must be reduced to one monthly reading; using
the maximum preserves bursts rather than averaging them away.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import ara_enso_causal_leaf_fall_ablation as leaf
import ara_enso_leaf_to_wwv_abnormality_test as prior
import ara_joint_enso_topology_direction_test as joint
import ara_unified_layered_framework_test as base
from enso_combined_horizon_feeder import load_dmi
from enso_pdo_feeder_test import load_nino, load_pdo, load_soi, load_wwv
from ara_finer_feeders_test import load_qbo


HERE = Path(__file__).resolve().parent
OUT = HERE / "ara_enso_two_flow_window_result.json"

EARLY_WINDOW = tuple(range(12, 19))
LATE_WINDOW = tuple(range(30, 35))
FEEDER_LEADS = tuple(range(0, 7))


def load_mjo_monthly_max_amp(path: str) -> dict[str, float]:
    """Use raw daily RMM amplitudes but keep the sharpest day in each month."""
    monthly: dict[str, list[float]] = {}
    for line in open(path, encoding="utf-8"):
        fields = line.split()
        if len(fields) < 7 or not fields[0].isdigit():
            continue
        year = int(fields[0])
        month = int(fields[1])
        amplitude = float(fields[6])
        if amplitude > 900:
            continue
        monthly.setdefault(f"{year}{month:02d}", []).append(amplitude)
    return {key: float(np.max(values)) for key, values in monthly.items()}


def aligned_keys() -> list[str]:
    """Reconstruct the exact key order used by build_enso()."""
    west = load_wwv("wwv_west.dat")
    east = load_wwv("wwv_east.dat")
    nino = load_nino("nino34_long_anom.csv")
    soi = load_soi("soi.data")
    pdo = load_pdo("../../../../PDO_NOAA/ersst.v5.pdo.dat")
    iod = load_dmi("../../../../IOD_NOAA/dmi.had.long.data")
    return sorted(set(west) & set(east) & set(nino) & set(soi) & set(pdo) & set(iod))


def values_for_keys(data: dict[str, float], keys: list[str]) -> np.ndarray:
    return np.asarray([data.get(key, np.nan) for key in keys], dtype=float)


def fill_missing_from_training_mean(values: np.ndarray, cutoff: int) -> np.ndarray:
    """Fill rare missing candidate-feeder months without looking beyond cutoff."""
    result = values.copy()
    training = result[:cutoff]
    training = training[np.isfinite(training)]
    replacement = float(np.mean(training)) if len(training) else 0.0
    result[~np.isfinite(result)] = replacement
    return result


def window_values(series: np.ndarray, origins: np.ndarray, delays: tuple[int, ...]) -> np.ndarray:
    rows = []
    for origin in origins:
        values = [series[origin + delay] for delay in delays if origin + delay < len(series)]
        rows.append(float(np.mean(values)) if values else float("nan"))
    return np.asarray(rows, dtype=float)


def weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    valid = np.isfinite(values) & np.isfinite(weights) & (weights >= 0.0)
    values = values[valid]
    weights = weights[valid]
    if len(values) == 0 or np.sum(weights) < 1e-12:
        return float("nan")
    return float(np.sum(values * weights) / np.sum(weights))


def profile(
    marker: np.ndarray,
    series: np.ndarray,
    origins: np.ndarray,
    delays: tuple[int, ...],
) -> list[dict]:
    rows = []
    for delay in delays:
        valid_origins = origins[origins + delay < len(series)]
        target = series[valid_origins + delay]
        rows.append(
            {
                "delay_months": delay,
                "n": int(len(valid_origins)),
                "corr": prior.correlation(marker[valid_origins], target),
                "marker_weighted_mean": weighted_mean(target, marker[valid_origins]),
                "plain_mean": float(np.nanmean(target)),
            }
        )
    return rows


def pulse_summary(
    marker: np.ndarray,
    series: np.ndarray,
    origins: np.ndarray,
    delays: tuple[int, ...],
) -> dict:
    rows = profile(marker, series, origins, delays)
    peak = max(rows, key=lambda row: row["corr"] if math.isfinite(row["corr"]) else -999.0)
    positive = [row for row in rows if row["corr"] > 0.0]
    half_peak = [
        row
        for row in rows
        if peak["corr"] > 0.0 and row["corr"] >= 0.5 * peak["corr"]
    ]
    window_target = window_values(series, origins, delays)
    window_corr = prior.correlation(marker[origins], window_target)
    weighted = weighted_mean(window_target, marker[origins])
    plain = float(np.nanmean(window_target))
    return {
        "delays_months": list(delays),
        "mean_corr_across_delays": float(np.nanmean([row["corr"] for row in rows])),
        "window_mean_corr": window_corr,
        "marker_weighted_window_mean": weighted,
        "plain_window_mean": plain,
        "marker_weighted_excess": float(weighted - plain),
        "peak": peak,
        "positive_delay_count": len(positive),
        "half_peak_delay_count": len(half_peak),
        "profile": rows,
    }


def signed_window_response(
    marker: np.ndarray,
    series: np.ndarray,
    origins: np.ndarray,
    delays: tuple[int, ...],
) -> dict:
    target = window_values(series, origins, delays)
    weighted = weighted_mean(target, marker[origins])
    plain = float(np.nanmean(target))
    return {
        "marker_weighted_mean": weighted,
        "plain_mean": plain,
        "marker_weighted_shift": float(weighted - plain),
        "corr": prior.correlation(marker[origins], target),
    }


def feeder_alignment(
    feeder_abnormality: np.ndarray,
    wwv_abnormality: np.ndarray,
    origins: np.ndarray,
    delays: tuple[int, ...],
) -> dict:
    rows = []
    wwv_response = window_values(wwv_abnormality, origins, delays)
    for lead in FEEDER_LEADS:
        feeder_delays = tuple(delay - lead for delay in delays if delay - lead >= 0)
        feeder_response = window_values(feeder_abnormality, origins, feeder_delays)
        rows.append(
            {
                "feeder_lead_months": lead,
                "corr": prior.correlation(feeder_response, wwv_response),
                "n": int(np.sum(np.isfinite(feeder_response) & np.isfinite(wwv_response))),
            }
        )
    peak = max(rows, key=lambda row: row["corr"] if math.isfinite(row["corr"]) else -999.0)
    return {
        "fixed_contemporaneous_corr": rows[0]["corr"],
        "peak_exploratory": peak,
        "lead_scan": rows,
    }


def describe_window(
    marker: np.ndarray,
    abnormalities: dict[str, np.ndarray],
    signed: dict[str, np.ndarray],
    feeders: dict[str, np.ndarray],
    origins: np.ndarray,
    delays: tuple[int, ...],
) -> dict:
    complete_origins = origins[origins + max(delays) < len(marker)]
    return {
        "complete_origin_n": int(len(complete_origins)),
        "wwv_pulses": {
            name: pulse_summary(marker, values, complete_origins, delays)
            for name, values in abnormalities.items()
        },
        "wwv_signed_response": {
            name: signed_window_response(marker, values, complete_origins, delays)
            for name, values in signed.items()
        },
        "candidate_feeder_alignment_to_wwv_battery": {
            name: feeder_alignment(
                values, abnormalities["battery_abnormality"], complete_origins, delays
            )
            for name, values in feeders.items()
        },
    }


def main() -> None:
    nodes = joint.build_nodes()
    keys = aligned_keys()
    if len(keys) != len(nodes[0].values):
        raise RuntimeError("Reconstructed ENSO keys do not match the unified aligned series")

    n = len(keys)
    cutoff = int(n * 0.60)
    nino = base.standardize_from_training(nodes[0].values, cutoff)
    marker = np.asarray(leaf.causal_leaf_state(nino)["leaf"], dtype=float)

    abnormalities, _ = prior.build_abnormalities(nodes, cutoff)

    west = base.standardize_from_training(nodes[2].values, cutoff)
    east = base.standardize_from_training(nodes[3].values, cutoff)
    orientation_residual, _ = prior.ar_innovation(east - west, cutoff)
    battery_residual, _ = prior.ar_innovation(0.5 * (east + west), cutoff)
    signed = {
        "orientation_residual": orientation_residual,
        "battery_residual": battery_residual,
    }

    mjo = fill_missing_from_training_mean(
        values_for_keys(load_mjo_monthly_max_amp("mjo_rmm.txt"), keys), cutoff
    )
    qbo30 = fill_missing_from_training_mean(values_for_keys(load_qbo("qbo_u30.txt"), keys), cutoff)
    qbo50 = fill_missing_from_training_mean(values_for_keys(load_qbo("qbo_u50.txt"), keys), cutoff)
    iod = base.standardize_from_training(nodes[4].values, cutoff)

    mjo_residual, _ = prior.ar_innovation(base.standardize_from_training(mjo, cutoff), cutoff)
    qbo30_residual, _ = prior.ar_innovation(base.standardize_from_training(qbo30, cutoff), cutoff)
    qbo50_residual, _ = prior.ar_innovation(base.standardize_from_training(qbo50, cutoff), cutoff)
    iod_residual, _ = prior.ar_innovation(iod, cutoff)
    feeders = {
        "MJO_monthly_max_daily_amp_candidate_finer_feeder": np.abs(mjo_residual),
        "IOD_lateral_feeder_comparison": np.abs(iod_residual),
        "QBO_vector_slower_clock_control": np.sqrt(qbo30_residual**2 + qbo50_residual**2)
        / math.sqrt(2.0),
    }

    windows = {
        "visible_pre_cutoff_after_marker_warmup": np.arange(leaf.MIN_HISTORY, cutoff),
        "heldout": np.arange(cutoff, n),
    }
    result = {
        "test": "frozen early-versus-late ENSO WWV pulse comparison",
        "status": "diagnostic association test; not a predictor and not causal proof",
        "strict_causal_checklist": {
            "frozen_windows_before_scoring": {
                "possible_lower_upflow_months": list(EARLY_WINDOW),
                "possible_recycled_return_months": list(LATE_WINDOW),
            },
            "leaf_marker": "existing causal harmonic marker from NINO values at or before origin",
            "wwv_abnormality": "raw monthly WWV residual magnitude after training-only WWV-history AR",
            "mjo_candidate": "maximum raw daily RMM amplitude in each month; secondary diagnostic only",
            "synthetic_energy_injection": False,
            "formula_modified": False,
            "smoothing": False,
            "fft_or_hilbert": False,
            "future_value_used_to_construct_marker": False,
        },
        "data_limits": {
            "observed_rung_directly_below_wwv_available": False,
            "mjo_role": "measured finer/faster candidate activity proxy, not a proven direct WWV-below rung",
            "iod_role": "measured lateral feeder comparison",
            "qbo_role": "measured slower timing control, not a direct WWV-below rung",
            "overlapping_months": n,
            "training_cutoff_month_index": cutoff,
        },
        "windows": {},
    }
    for period_name, origins in windows.items():
        result["windows"][period_name] = {
            "origin_n": int(len(origins)),
            "possible_lower_upflow_12_18m": describe_window(
                marker, abnormalities, signed, feeders, origins, EARLY_WINDOW
            ),
            "possible_recycled_return_30_34m": describe_window(
                marker, abnormalities, signed, feeders, origins, LATE_WINDOW
            ),
        }

    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("strict causal checklist")
    print(json.dumps(result["strict_causal_checklist"], indent=2))
    for period_name, payload in result["windows"].items():
        print()
        print(period_name, "n=", payload["origin_n"])
        for window_name in ("possible_lower_upflow_12_18m", "possible_recycled_return_30_34m"):
            detail = payload[window_name]
            battery = detail["wwv_pulses"]["battery_abnormality"]
            vector = detail["wwv_pulses"]["vector_abnormality"]
            orient = detail["wwv_signed_response"]["orientation_residual"]
            mjo_align = detail["candidate_feeder_alignment_to_wwv_battery"][
                "MJO_monthly_max_daily_amp_candidate_finer_feeder"
            ]
            print(" ", window_name)
            print(
                "    battery",
                f"corr={battery['window_mean_corr']:+.3f}",
                f"excess={battery['marker_weighted_excess']:+.3f}",
                f"peak={battery['peak']['delay_months']}m/{battery['peak']['corr']:+.3f}",
                f"halfwidth={battery['half_peak_delay_count']}",
            )
            print(
                "    vector ",
                f"corr={vector['window_mean_corr']:+.3f}",
                f"excess={vector['marker_weighted_excess']:+.3f}",
            )
            print(
                "    orientation",
                f"weighted_shift={orient['marker_weighted_shift']:+.3f}",
                f"corr={orient['corr']:+.3f}",
            )
            print(
                "    MJO->WWV battery",
                f"fixed0={mjo_align['fixed_contemporaneous_corr']:+.3f}",
                f"best={mjo_align['peak_exploratory']['feeder_lead_months']}m/"
                f"{mjo_align['peak_exploratory']['corr']:+.3f}",
            )


if __name__ == "__main__":
    main()
