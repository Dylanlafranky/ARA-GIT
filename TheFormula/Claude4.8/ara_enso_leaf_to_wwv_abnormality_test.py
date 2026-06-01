"""Strict-causal brown leaf-fall marker versus measured WWV abnormality.

This is a diagnostic, not a predictor. It does not inject a synthetic leaf
packet into the ENSO formula. It asks whether a causal brown crossover marker
derived from NINO is followed by unusual motion in the measured WWV lower rung.

Visible inputs at month t:
  - NINO values at or before t, used by the existing causal leaf marker.
  - WWV west/east values before t, used to estimate ordinary WWV motion.
  - Measured WWV west/east values at t + delay, used only as scored outcomes.

The WWV abnormality is the magnitude of the residual after a training-only
autoregressive baseline. A 30-month delayed leaf series is the wrong-time null.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import ara_enso_causal_leaf_fall_ablation as leaf
import ara_joint_enso_topology_direction_test as joint
import ara_unified_layered_framework_test as base


HERE = Path(__file__).resolve().parent
OUT = HERE / "ara_enso_leaf_to_wwv_abnormality_result.json"

AR_LAGS = (1, 2, 3, 6)
MAX_DELAY = 60
ANCHOR_DELAYS = (0, 3, 6, 9, 12, 18, 24, 30, 36, 48, 60)
WRONG_TIME_NULL_LAGS = (6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 72)


def correlation(left: np.ndarray, right: np.ndarray) -> float:
    valid = np.isfinite(left) & np.isfinite(right)
    left = left[valid]
    right = right[valid]
    if len(left) < 3 or np.std(left) < 1e-12 or np.std(right) < 1e-12:
        return float("nan")
    return float(np.corrcoef(left, right)[0, 1])


def ar_innovation(series: np.ndarray, cutoff: int) -> tuple[np.ndarray, list[float]]:
    """Return residuals from a WWV-history-only AR model fitted before cutoff."""
    start = max(AR_LAGS)
    months = np.arange(start, len(series))
    design = np.asarray(
        [[1.0, *[float(series[month - lag]) for lag in AR_LAGS]] for month in months],
        dtype=float,
    )
    target = series[months]
    training = months < cutoff
    beta = np.linalg.lstsq(design[training], target[training], rcond=None)[0]

    residual = np.full(len(series), np.nan, dtype=float)
    residual[months] = target - design @ beta
    return residual, [float(value) for value in beta]


def build_abnormalities(nodes: list, cutoff: int) -> tuple[dict[str, np.ndarray], dict]:
    west = base.standardize_from_training(nodes[2].values, cutoff)
    east = base.standardize_from_training(nodes[3].values, cutoff)
    orientation = east - west
    battery = 0.5 * (east + west)

    west_residual, west_beta = ar_innovation(west, cutoff)
    east_residual, east_beta = ar_innovation(east, cutoff)
    orientation_residual, orientation_beta = ar_innovation(orientation, cutoff)
    battery_residual, battery_beta = ar_innovation(battery, cutoff)

    abnormalities = {
        "orientation_abnormality": np.abs(orientation_residual),
        "battery_abnormality": np.abs(battery_residual),
        "vector_abnormality": np.sqrt(
            west_residual**2 + east_residual**2
        )
        / math.sqrt(2.0),
    }
    models = {
        "west_wwv_ar": west_beta,
        "east_wwv_ar": east_beta,
        "orientation_ar": orientation_beta,
        "battery_ar": battery_beta,
    }
    return abnormalities, models


def delay_curve(
    marker: np.ndarray,
    null_marker: np.ndarray,
    timing_nulls: dict[int, np.ndarray],
    outcome: np.ndarray,
    cutoff: int,
) -> list[dict]:
    start = max(leaf.MIN_HISTORY, max(AR_LAGS) + 1)
    possible = np.arange(start, len(outcome))
    rows = []
    for delay in range(MAX_DELAY + 1):
        origins = possible[(possible >= cutoff) & (possible + delay < len(outcome))]
        real_corr = correlation(marker[origins], outcome[origins + delay])
        null_corr = correlation(null_marker[origins], outcome[origins + delay])
        timing_null_corrs = {
            str(lag): correlation(values[origins], outcome[origins + delay])
            for lag, values in timing_nulls.items()
        }
        timing_values = np.asarray(list(timing_null_corrs.values()), dtype=float)
        timing_median = float(np.nanmedian(timing_values))
        timing_max = float(np.nanmax(timing_values))
        timing_min = float(np.nanmin(timing_values))
        rows.append(
            {
                "delay_months": delay,
                "n": int(len(origins)),
                "leaf_corr": real_corr,
                "wrong_time_null_corr": null_corr,
                "delta_vs_null": float(real_corr - null_corr),
                "timing_null_corrs": timing_null_corrs,
                "timing_null_median_corr": timing_median,
                "timing_null_max_corr": timing_max,
                "timing_null_min_corr": timing_min,
                "delta_vs_timing_null_median": float(real_corr - timing_median),
                "exceeds_all_timing_nulls": bool(real_corr > timing_max),
            }
        )
    return rows


def strongest(rows: list[dict], key: str) -> dict:
    valid = [row for row in rows if math.isfinite(row[key])]
    return max(valid, key=lambda row: row[key])


def anchor_rows(rows: list[dict]) -> list[dict]:
    return [row for row in rows if row["delay_months"] in ANCHOR_DELAYS]


def split_window_curve(
    marker: np.ndarray,
    outcome: np.ndarray,
    origin_lo: int,
    origin_hi: int,
) -> list[dict]:
    rows = []
    for delay in range(MAX_DELAY + 1):
        origins = np.arange(origin_lo, min(origin_hi, len(outcome) - delay))
        rows.append(
            {
                "delay_months": delay,
                "n": int(len(origins)),
                "leaf_corr": correlation(marker[origins], outcome[origins + delay]),
            }
        )
    return rows


def split_window_checks(
    marker: np.ndarray,
    outcome: np.ndarray,
    cutoff: int,
) -> dict:
    heldout_mid = cutoff + (len(outcome) - cutoff) // 2
    windows = {
        "visible_pre_cutoff_after_marker_warmup": (leaf.MIN_HISTORY, cutoff),
        "heldout_early": (cutoff, heldout_mid),
        "heldout_late": (heldout_mid, len(outcome)),
    }
    result = {}
    for name, (origin_lo, origin_hi) in windows.items():
        rows = split_window_curve(marker, outcome, origin_lo, origin_hi)
        result[name] = {
            "origin_start_index": origin_lo,
            "origin_stop_index_exclusive": origin_hi,
            "peak_exploratory": strongest(rows, "leaf_corr"),
            "selected_delay_rows": [
                row for row in rows if row["delay_months"] in (15, 24, 30, 31, 32, 33, 34, 36)
            ],
        }
    return result


def null_peak_panel(rows: list[dict]) -> list[dict]:
    result = []
    for null_lag in WRONG_TIME_NULL_LAGS:
        key = str(null_lag)
        best = max(rows, key=lambda row: row["timing_null_corrs"][key])
        result.append(
            {
                "marker_delay_months": null_lag,
                "peak_corr": best["timing_null_corrs"][key],
                "peak_outcome_delay_months": best["delay_months"],
            }
        )
    return result


def event_study(
    marker: np.ndarray,
    null_marker: np.ndarray,
    outcome: np.ndarray,
    cutoff: int,
) -> dict:
    """Describe strong events using a threshold fixed from the training period."""
    start = max(leaf.MIN_HISTORY, max(AR_LAGS) + 1)
    threshold = float(np.quantile(marker[start:cutoff], 0.90))
    rows = []
    for delay in ANCHOR_DELAYS:
        origins = np.arange(cutoff, len(outcome) - delay)
        real_events = origins[marker[origins] >= threshold]
        null_events = origins[null_marker[origins] >= threshold]
        rows.append(
            {
                "delay_months": delay,
                "leaf_event_n": int(len(real_events)),
                "leaf_event_mean_abnormality": float(
                    np.mean(outcome[real_events + delay])
                )
                if len(real_events)
                else float("nan"),
                "wrong_time_event_n": int(len(null_events)),
                "wrong_time_event_mean_abnormality": float(
                    np.mean(outcome[null_events + delay])
                )
                if len(null_events)
                else float("nan"),
            }
        )
    return {"training_only_event_threshold": threshold, "anchors": rows}


def main() -> None:
    nodes = joint.build_nodes()
    n = len(nodes[0].values)
    cutoff = int(n * 0.60)

    nino = base.standardize_from_training(nodes[0].values, cutoff)
    leaf_state = leaf.causal_leaf_state(nino)
    marker = np.asarray(leaf_state["leaf"], dtype=float)
    null_marker = leaf.causal_lag_null(marker, leaf.LEAF_NULL_LAG)
    timing_nulls = {
        lag: leaf.causal_lag_null(marker, lag) for lag in WRONG_TIME_NULL_LAGS
    }

    abnormalities, ar_models = build_abnormalities(nodes, cutoff)
    outcomes = {}
    for name, outcome in abnormalities.items():
        rows = delay_curve(marker, null_marker, timing_nulls, outcome, cutoff)
        outcomes[name] = {
            "anchor_delays": anchor_rows(rows),
            "peak_leaf_corr_exploratory": strongest(rows, "leaf_corr"),
            "peak_delta_vs_null_exploratory": strongest(rows, "delta_vs_null"),
            "peak_delta_vs_timing_null_median_exploratory": strongest(
                rows, "delta_vs_timing_null_median"
            ),
            "wrong_time_null_peak_panel": null_peak_panel(rows),
            "split_window_checks": split_window_checks(marker, outcome, cutoff),
            "strong_event_study": event_study(
                marker, null_marker, outcome, cutoff
            ),
            "full_delay_curve": rows,
        }

    result = {
        "test": "causal brown leaf marker versus measured lower-rung WWV abnormality",
        "status": "diagnostic association test; not a predictor and not causal proof",
        "strict_causal_checklist": {
            "leaf_marker": (
                "existing causal harmonic marker from NINO values at or before origin"
            ),
            "wwv_baseline": (
                "training-only AR baseline using prior WWV values at lags 1,2,3,6"
            ),
            "scored_outcomes": (
                "measured future WWV residual magnitudes; used only after markers exist"
            ),
            "synthetic_leaf_injection": False,
            "future_value_used_to_construct_marker": False,
            "smoothing": False,
            "fft_or_hilbert": False,
            "wrong_time_null": f"same causal leaf marker delayed {leaf.LEAF_NULL_LAG} months",
            "timing_control_panel": (
                "same causal marker delayed only backward in time by "
                f"{WRONG_TIME_NULL_LAGS} months"
            ),
        },
        "data": {
            "n_months": n,
            "training_months": cutoff,
            "heldout_months": n - cutoff,
            "max_delay_months": MAX_DELAY,
            "anchor_delays_months": list(ANCHOR_DELAYS),
        },
        "leaf_marker": {
            "heldout_positive_months": int(np.sum(marker[cutoff:] > 0.0)),
            "timing_null_marker_delays_months": list(WRONG_TIME_NULL_LAGS),
            "heldout_autocorrelation_by_delay": {
                str(lag): correlation(marker[cutoff:], values[cutoff:])
                for lag, values in timing_nulls.items()
            },
        },
        "wwv_ar_models": ar_models,
        "outcomes": outcomes,
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("strict causal checklist")
    print(json.dumps(result["strict_causal_checklist"], indent=2))
    print()
    for name, payload in outcomes.items():
        peak = payload["peak_leaf_corr_exploratory"]
        delta_peak = payload["peak_delta_vs_null_exploratory"]
        panel_peak = payload["peak_delta_vs_timing_null_median_exploratory"]
        print(name)
        print(
            "  peak leaf corr exploratory:",
            f"{peak['delay_months']}m corr={peak['leaf_corr']:.3f}",
            f"null={peak['wrong_time_null_corr']:.3f}",
        )
        print(
            "  peak delta vs null exploratory:",
            f"{delta_peak['delay_months']}m delta={delta_peak['delta_vs_null']:.3f}",
            f"corr={delta_peak['leaf_corr']:.3f}",
        )
        print(
            "  peak delta vs timing-panel median exploratory:",
            f"{panel_peak['delay_months']}m",
            f"delta={panel_peak['delta_vs_timing_null_median']:.3f}",
            f"corr={panel_peak['leaf_corr']:.3f}",
            f"panel_max={panel_peak['timing_null_max_corr']:.3f}",
        )
        print("  anchors")
        for row in payload["anchor_delays"]:
            print(
                f"    {row['delay_months']:>2}m"
                f" n={row['n']:>3}"
                f" corr={row['leaf_corr']:+.3f}"
                f" null={row['wrong_time_null_corr']:+.3f}"
                f" delta={row['delta_vs_null']:+.3f}"
                f" panel_med={row['timing_null_median_corr']:+.3f}"
                f" panel_max={row['timing_null_max_corr']:+.3f}"
            )


if __name__ == "__main__":
    main()
