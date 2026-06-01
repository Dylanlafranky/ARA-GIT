"""Strict-causal forward ablation for the inferred ENSO brown leaf transit.

Prior diagnostics froze a candidate travel-time window:

    visible brown/green leaf-drop marker now
        -> unusual measured WWV soil response 30..34 months later

This script turns that retrospective timing observation into a forward test
without modifying the main formula.

Two questions are scored:

1. Does a leaf marker visible at origin t improve held-out prediction of the
   measured WWV battery-abnormality window at t + 30..34?
2. Does an arrived-packet state, calculated only from leaf markers observed
   30..34 months earlier, improve held-out NINO forecasts?

Wrong-time controls delay the marker using earlier values only. No future
values, smoothing, FFT, Hilbert transform, analog averaging, or synthetic
energy packets are used.
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
OUT = HERE / "ara_enso_leaf_transit_forward_ablation_result.json"

ARRIVAL_WINDOW = tuple(range(30, 35))
STATE_LAGS = (0, 1, 3, 6, 12)
PACKET_LAGS = (0, 1, 3, 6)
WRONG_TIME_LAGS = (6, 12, 18, 24, 30, 36, 42, 48)
NINO_HORIZONS = (1, 3, 6, 9, 12, 18, 24, 30, 36, 48, 60)
LONG_NINO_HORIZONS = (24, 30, 32, 34, 36, 42, 48, 60)
NEIGHBORING_HORIZONS = tuple(range(24, 37))


def lag_matrix(values: np.ndarray, origins: np.ndarray, lags: tuple[int, ...]) -> np.ndarray:
    return np.asarray(
        [[float(values[origin - lag]) for lag in lags] for origin in origins],
        dtype=float,
    )


def soil_state_matrix(nodes: list[joint.Node], origins: np.ndarray) -> np.ndarray:
    west = np.asarray(nodes[2].values, dtype=float)
    east = np.asarray(nodes[3].values, dtype=float)
    battery = west + east
    orientation = east - west
    return np.column_stack(
        [
            lag_matrix(west, origins, STATE_LAGS),
            lag_matrix(east, origins, STATE_LAGS),
            lag_matrix(battery, origins, STATE_LAGS),
            lag_matrix(orientation, origins, STATE_LAGS),
        ]
    )


def causal_arrival_state(marker: np.ndarray) -> np.ndarray:
    """Read packets due now from markers observed 30..34 months earlier."""
    result = np.zeros_like(marker)
    for month in range(max(ARRIVAL_WINDOW), len(marker)):
        result[month] = float(np.mean([marker[month - delay] for delay in ARRIVAL_WINDOW]))
    return result


def window_target(values: np.ndarray, origins: np.ndarray) -> np.ndarray:
    return np.asarray(
        [float(np.mean([values[origin + delay] for delay in ARRIVAL_WINDOW])) for origin in origins],
        dtype=float,
    )


def scalar_metrics(truth: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    valid = np.isfinite(truth) & np.isfinite(pred)
    truth = truth[valid]
    pred = pred[valid]
    if len(truth) < 3:
        return {"n": int(len(truth)), "corr": float("nan"), "mae": float("nan")}
    return {
        "n": int(len(truth)),
        "corr": prior.correlation(truth, pred),
        "mae": float(np.mean(np.abs(truth - pred))),
    }


def fit_scalar(
    train_features: np.ndarray,
    train_target: np.ndarray,
    test_features: np.ndarray,
) -> np.ndarray:
    return base.ridge_readout(train_features, train_target, test_features)


def block_bootstrap_corr_lift(
    truth: np.ndarray,
    baseline: np.ndarray,
    real: np.ndarray,
    *,
    block_months: int = 12,
    iterations: int = 4000,
) -> dict:
    """Describe sampling uncertainty while preserving short serial blocks."""
    valid = np.isfinite(truth) & np.isfinite(baseline) & np.isfinite(real)
    truth = truth[valid]
    baseline = baseline[valid]
    real = real[valid]
    n = len(truth)
    if n < block_months + 2:
        return {
            "block_months": block_months,
            "iterations": iterations,
            "median_corr_lift": float("nan"),
            "ci95_corr_lift": [float("nan"), float("nan")],
            "positive_lift_fraction": float("nan"),
        }
    rng = np.random.default_rng(20260601)
    starts = np.arange(0, n - block_months + 1)
    lifts = []
    for _ in range(iterations):
        pieces = []
        while sum(len(piece) for piece in pieces) < n:
            start = int(rng.choice(starts))
            pieces.append(np.arange(start, start + block_months))
        indices = np.concatenate(pieces)[:n]
        lifts.append(
            prior.correlation(truth[indices], real[indices])
            - prior.correlation(truth[indices], baseline[indices])
        )
    values = np.asarray(lifts, dtype=float)
    return {
        "block_months": block_months,
        "iterations": iterations,
        "median_corr_lift": float(np.nanmedian(values)),
        "ci95_corr_lift": [
            float(np.nanquantile(values, 0.025)),
            float(np.nanquantile(values, 0.975)),
        ],
        "positive_lift_fraction": float(np.nanmean(values > 0.0)),
    }


def split_half_nino_metrics(
    truth: np.ndarray,
    current: np.ndarray,
    baseline: np.ndarray,
    real: np.ndarray,
) -> dict:
    midpoint = len(truth) // 2
    slices = {
        "heldout_early_half": slice(0, midpoint),
        "heldout_late_half": slice(midpoint, len(truth)),
    }
    result = {}
    for name, part in slices.items():
        baseline_score = base.metrics(truth[part], baseline[part], current[part])
        real_score = base.metrics(truth[part], real[part], current[part])
        result[name] = {
            "raw_topology_var": baseline_score,
            "raw_topology_var_plus_real_packet": real_score,
            "corr_lift": float(real_score["corr"] - baseline_score["corr"]),
        }
    return result


def soil_arrival_ablation(
    nodes: list[joint.Node],
    marker: np.ndarray,
    wrong_markers: dict[int, np.ndarray],
    cutoff: int,
) -> dict:
    abnormalities, _ = prior.build_abnormalities(nodes, cutoff)
    battery_abnormality = abnormalities["battery_abnormality"]
    start = max(leaf.MIN_HISTORY, max(STATE_LAGS + PACKET_LAGS) + 1)
    origins = np.arange(start, len(marker) - max(ARRIVAL_WINDOW))
    train_origins = origins[origins + max(ARRIVAL_WINDOW) < cutoff]
    test_origins = origins[origins >= cutoff]

    train_target = window_target(battery_abnormality, train_origins)
    test_target = window_target(battery_abnormality, test_origins)
    state_train = soil_state_matrix(nodes, train_origins)
    state_test = soil_state_matrix(nodes, test_origins)
    leaf_train = lag_matrix(marker, train_origins, PACKET_LAGS)
    leaf_test = lag_matrix(marker, test_origins, PACKET_LAGS)

    constant_pred = np.full(len(test_target), float(np.mean(train_target)))
    state_pred = fit_scalar(state_train, train_target, state_test)
    leaf_only_pred = fit_scalar(leaf_train, train_target, leaf_test)
    state_plus_leaf_pred = fit_scalar(
        np.column_stack([state_train, leaf_train]),
        train_target,
        np.column_stack([state_test, leaf_test]),
    )
    wrong_time = {}
    for lag, values in wrong_markers.items():
        wrong_train = lag_matrix(values, train_origins, PACKET_LAGS)
        wrong_test = lag_matrix(values, test_origins, PACKET_LAGS)
        wrong_pred = fit_scalar(
            np.column_stack([state_train, wrong_train]),
            train_target,
            np.column_stack([state_test, wrong_test]),
        )
        wrong_time[str(lag)] = scalar_metrics(test_target, wrong_pred)

    wrong_corrs = np.asarray([score["corr"] for score in wrong_time.values()])
    real = scalar_metrics(test_target, state_plus_leaf_pred)
    baseline = scalar_metrics(test_target, state_pred)
    return {
        "target": "mean measured WWV battery abnormality at origin + 30..34 months",
        "train_origin_n": int(len(train_origins)),
        "heldout_origin_n": int(len(test_origins)),
        "models": {
            "training_mean": scalar_metrics(test_target, constant_pred),
            "leaf_only": scalar_metrics(test_target, leaf_only_pred),
            "wwv_state_only": baseline,
            "wwv_state_plus_real_leaf": real,
        },
        "wrong_time_panel": wrong_time,
        "direct_marker_to_soil_corr": {
            "training": prior.correlation(marker[train_origins], train_target),
            "heldout": prior.correlation(marker[test_origins], test_target),
        },
        "real_leaf_corr_lift_vs_wwv_state": float(real["corr"] - baseline["corr"]),
        "real_leaf_corr_minus_wrong_time_median": float(real["corr"] - np.nanmedian(wrong_corrs)),
        "real_leaf_exceeds_all_wrong_times": bool(real["corr"] > np.nanmax(wrong_corrs)),
    }


def nino_models_at_horizon(
    nodes: list[joint.Node],
    base_features: np.ndarray,
    packet: np.ndarray,
    wrong_packets: dict[int, np.ndarray],
    origins: np.ndarray,
    cutoff: int,
    horizon: int,
    *,
    include_robustness: bool = False,
) -> dict:
    home = np.asarray(nodes[0].values, dtype=float)
    valid = origins + horizon < len(home)
    train = valid & (origins + horizon < cutoff)
    test = valid & (origins >= cutoff)
    train_origins = origins[train]
    test_origins = origins[test]
    train_current = home[train_origins]
    test_current = home[test_origins]
    train_target = home[train_origins + horizon]
    test_target = home[test_origins + horizon]
    train_delta = train_target - train_current

    raw_train = base_features[train]
    raw_test = base_features[test]
    packet_train = lag_matrix(packet, train_origins, PACKET_LAGS)
    packet_test = lag_matrix(packet, test_origins, PACKET_LAGS)
    raw_pred = test_current + base.ridge_readout(raw_train, train_delta, raw_test)
    plus_pred = test_current + base.ridge_readout(
        np.column_stack([raw_train, packet_train]),
        train_delta,
        np.column_stack([raw_test, packet_test]),
    )

    wrong_time = {}
    for lag, values in wrong_packets.items():
        wrong_train = lag_matrix(values, train_origins, PACKET_LAGS)
        wrong_test = lag_matrix(values, test_origins, PACKET_LAGS)
        pred = test_current + base.ridge_readout(
            np.column_stack([raw_train, wrong_train]),
            train_delta,
            np.column_stack([raw_test, wrong_test]),
        )
        wrong_time[str(lag)] = base.metrics(test_target, pred, test_current)

    baseline = base.metrics(test_target, raw_pred, test_current)
    real = base.metrics(test_target, plus_pred, test_current)
    wrong_corrs = np.asarray([score["corr"] for score in wrong_time.values()])
    result = {
        "raw_topology_var": baseline,
        "raw_topology_var_plus_real_packet": real,
        "wrong_time_panel": wrong_time,
        "direct_packet_to_future_nino_corr": prior.correlation(
            packet[test_origins], test_target
        ),
        "real_packet_corr_lift_vs_raw": float(real["corr"] - baseline["corr"]),
        "real_packet_corr_minus_wrong_time_median": float(real["corr"] - np.nanmedian(wrong_corrs)),
        "real_packet_exceeds_all_wrong_times": bool(real["corr"] > np.nanmax(wrong_corrs)),
    }
    if include_robustness:
        result["heldout_split_halves"] = split_half_nino_metrics(
            test_target, test_current, raw_pred, plus_pred
        )
        result["block_bootstrap_corr_lift"] = block_bootstrap_corr_lift(
            test_target, raw_pred, plus_pred
        )
    return result


def downstream_nino_arrival_ablation(
    nodes: list[joint.Node],
    marker: np.ndarray,
    wrong_markers: dict[int, np.ndarray],
    cutoff: int,
) -> dict:
    """Score packets already due to arrive at the origin."""
    packet = causal_arrival_state(marker)
    wrong_packets = {
        lag: causal_arrival_state(values) for lag, values in wrong_markers.items()
    }
    start = max(leaf.MIN_HISTORY + max(ARRIVAL_WINDOW), max(STATE_LAGS + PACKET_LAGS) + 1)
    origins = np.arange(start, len(marker))
    raw = joint.raw_lag_matrix(nodes, origins, STATE_LAGS)
    return {
        str(horizon): nino_models_at_horizon(
            nodes,
            raw,
            packet,
            wrong_packets,
            origins,
            cutoff,
            horizon,
            include_robustness=horizon == 30,
        )
        for horizon in NINO_HORIZONS
    }


def downstream_nino_drop_now_ablation(
    nodes: list[joint.Node],
    marker: np.ndarray,
    wrong_markers: dict[int, np.ndarray],
    cutoff: int,
) -> dict:
    """Score the long-range downstream effect of a leaf visibly dropping now."""
    start = max(leaf.MIN_HISTORY, max(STATE_LAGS + PACKET_LAGS) + 1)
    origins = np.arange(start, len(marker))
    raw = joint.raw_lag_matrix(nodes, origins, STATE_LAGS)
    return {
        str(horizon): nino_models_at_horizon(
            nodes, raw, marker, wrong_markers, origins, cutoff, horizon
        )
        for horizon in LONG_NINO_HORIZONS
    }


def descriptive_neighboring_horizon_scan(
    nodes: list[joint.Node],
    marker: np.ndarray,
    wrong_markers: dict[int, np.ndarray],
    cutoff: int,
) -> dict:
    """Inspect the shape around the frozen arrival ridge without selecting a winner."""
    packet = causal_arrival_state(marker)
    wrong_packets = {
        lag: causal_arrival_state(values) for lag, values in wrong_markers.items()
    }
    start = max(leaf.MIN_HISTORY + max(ARRIVAL_WINDOW), max(STATE_LAGS + PACKET_LAGS) + 1)
    origins = np.arange(start, len(marker))
    raw = joint.raw_lag_matrix(nodes, origins, STATE_LAGS)
    return {
        str(horizon): nino_models_at_horizon(
            nodes, raw, packet, wrong_packets, origins, cutoff, horizon
        )
        for horizon in NEIGHBORING_HORIZONS
    }


def best_lifts(rows: dict[str, dict], key: str, top_n: int = 3) -> list[dict]:
    ranked = sorted(
        (
            {"horizon_months": int(horizon), "lift": float(payload[key])}
            for horizon, payload in rows.items()
        ),
        key=lambda row: row["lift"],
        reverse=True,
    )
    return ranked[:top_n]


def main() -> None:
    nodes = joint.build_nodes()
    n = len(nodes[0].values)
    cutoff = int(n * 0.60)
    nino = base.standardize_from_training(nodes[0].values, cutoff)
    marker = np.asarray(leaf.causal_leaf_state(nino)["leaf"], dtype=float)
    wrong_markers = {
        lag: leaf.causal_lag_null(marker, lag) for lag in WRONG_TIME_LAGS
    }

    soil = soil_arrival_ablation(nodes, marker, wrong_markers, cutoff)
    arrived = downstream_nino_arrival_ablation(nodes, marker, wrong_markers, cutoff)
    dropped = downstream_nino_drop_now_ablation(nodes, marker, wrong_markers, cutoff)
    neighborhood = descriptive_neighboring_horizon_scan(
        nodes, marker, wrong_markers, cutoff
    )

    result = {
        "test": "strict-causal brown-leaf packet-in-transit forward ablation",
        "status": "forward diagnostic ablation; main formula unchanged",
        "strict_causal_checklist": {
            "leaf_marker": "past-only causal NINO brown/green harmonic crossover marker",
            "frozen_arrival_window_months": list(ARRIVAL_WINDOW),
            "arrived_packet_state": "mean markers observed 30..34 months earlier",
            "wrong_time_controls": f"same markers delayed only backward by {WRONG_TIME_LAGS} months",
            "heldout_tuning": False,
            "synthetic_energy_injection": False,
            "formula_modified": False,
            "smoothing": False,
            "fft_or_hilbert": False,
            "future_values_used_as_features": False,
        },
        "measurement_limits": {
            "leaf_marker_independent_of_nino": False,
            "leaf_marker_note": "valid causal forecast input, but not independent physical proof",
            "wwv_arrival_target": "measured future soil outcome scored only after prediction exists",
            "nino_models": "train-only ridge channel ablations; diagnostics, not the final physical operator",
            "independent_confirmation_set": False,
            "post_selection_note": (
                "the 30..34 month window was discovered from this historical record; "
                "results are exploratory until scored on new or independent data"
            ),
        },
        "soil_arrival_30_34m": soil,
        "downstream_nino_from_packet_arriving_now": arrived,
        "downstream_nino_from_leaf_dropping_now": dropped,
        "descriptive_arrived_packet_neighboring_horizon_scan": neighborhood,
        "top_nino_lifts": {
            "packet_arriving_now": best_lifts(arrived, "real_packet_corr_lift_vs_raw"),
            "leaf_dropping_now": best_lifts(dropped, "real_packet_corr_lift_vs_raw"),
        },
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("strict causal checklist")
    print(json.dumps(result["strict_causal_checklist"], indent=2))
    print()
    print("soil arrival 30..34m")
    for name, score in soil["models"].items():
        print(" ", name, f"corr={score['corr']:+.3f}", f"mae={score['mae']:.3f}")
    print(
        " ",
        "real leaf lift vs WWV state",
        f"{soil['real_leaf_corr_lift_vs_wwv_state']:+.3f}",
        "minus timing-panel median",
        f"{soil['real_leaf_corr_minus_wrong_time_median']:+.3f}",
        "beats all wrong times",
        soil["real_leaf_exceeds_all_wrong_times"],
    )
    print(
        " ",
        "direct marker -> soil corr",
        f"train={soil['direct_marker_to_soil_corr']['training']:+.3f}",
        f"heldout={soil['direct_marker_to_soil_corr']['heldout']:+.3f}",
    )
    print()
    print("downstream NINO: packet arriving now")
    for horizon, row in arrived.items():
        base_score = row["raw_topology_var"]
        real_score = row["raw_topology_var_plus_real_packet"]
        print(
            f"  {int(horizon):>2}m",
            f"raw={base_score['corr']:+.3f}",
            f"+packet={real_score['corr']:+.3f}",
            f"lift={row['real_packet_corr_lift_vs_raw']:+.3f}",
            f"vs_panel_med={row['real_packet_corr_minus_wrong_time_median']:+.3f}",
            f"beats_all={row['real_packet_exceeds_all_wrong_times']}",
        )
        if int(horizon) == 30:
            bootstrap = row["block_bootstrap_corr_lift"]
            print(
                "      30m robustness",
                f"direct_packet_corr={row['direct_packet_to_future_nino_corr']:+.3f}",
                f"bootstrap_median_lift={bootstrap['median_corr_lift']:+.3f}",
                f"ci95={bootstrap['ci95_corr_lift']}",
                f"positive={bootstrap['positive_lift_fraction']:.3f}",
            )
            for split_name, split in row["heldout_split_halves"].items():
                print(
                    "     ",
                    split_name,
                    f"raw={split['raw_topology_var']['corr']:+.3f}",
                    f"+packet={split['raw_topology_var_plus_real_packet']['corr']:+.3f}",
                    f"lift={split['corr_lift']:+.3f}",
                )
    print()
    print("downstream NINO: leaf dropping now")
    for horizon, row in dropped.items():
        base_score = row["raw_topology_var"]
        real_score = row["raw_topology_var_plus_real_packet"]
        print(
            f"  {int(horizon):>2}m",
            f"raw={base_score['corr']:+.3f}",
            f"+leaf={real_score['corr']:+.3f}",
            f"lift={row['real_packet_corr_lift_vs_raw']:+.3f}",
            f"vs_panel_med={row['real_packet_corr_minus_wrong_time_median']:+.3f}",
            f"beats_all={row['real_packet_exceeds_all_wrong_times']}",
        )
    print()
    print("descriptive neighboring-horizon scan: packet arriving now")
    for horizon, row in neighborhood.items():
        print(
            f"  {int(horizon):>2}m",
            f"raw={row['raw_topology_var']['corr']:+.3f}",
            f"+packet={row['raw_topology_var_plus_real_packet']['corr']:+.3f}",
            f"lift={row['real_packet_corr_lift_vs_raw']:+.3f}",
            f"vs_panel_med={row['real_packet_corr_minus_wrong_time_median']:+.3f}",
            f"beats_all={row['real_packet_exceeds_all_wrong_times']}",
        )


if __name__ == "__main__":
    main()
