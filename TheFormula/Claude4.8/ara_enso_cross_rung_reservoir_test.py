"""Strict-causal ENSO cross-rung reservoir ablation.

This is the first minimal test of the corrected recycling architecture:

    Space-pipe width:       2
    Time-pipe width:        phi
    normalized gap share:   g = (2 - phi) / 2
    intrinsic rung size:    x2 octave
    Space-axis reading:     2 per rung down
    Time-axis reading:      2*cos(36deg) = phi per projected handoff stage

The axis readings remain separate without inventing two unrelated ladders.
The underlying rung size is x2.  Head-on Space x2 controls the relative density
of a falling packet.  The same octave viewed through the 36-degree Time shear
reads as xphi and controls the staged return through handoff gates.

The return path is hierarchical, not same-junction:

    measured surface -> one-rung lower reservoir -> two-rung lower reservoir

Adjacent physical contact returns with opposite orientation.  Two-rung return
recovers the original orientation.  WWV west/east provide an observed lower
reservoir input; the two-rung store is a latent causal state.

This is an ablation, not a complete ENSO fluid model.  It intentionally tests
only four declared variants:

    no reservoir
    one-rung reservoir
    one-rung + two-rung reservoir
    one-rung + causal randomized-prior two-rung null

All features at origin t use observations <= t.  No FFT, Hilbert transform,
future lookup, smoothing, analog averaging, or future-origin shift is used.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import ara_joint_enso_topology_direction_test as joint
import ara_unified_layered_framework_test as base

HERE = Path(__file__).resolve().parent
PHI = base.PHI
GAP_SHARE = (2.0 - PHI) / 2.0
DIRECT_SHARE = PHI / 2.0
RETAIN = 1.0 / PHI
RELEASE = 1.0 / (PHI * PHI)
DENSITY_ONE = 2.0
DENSITY_TWO = 4.0


def causal_prior_null(values: np.ndarray, seed: int = 20260531) -> np.ndarray:
    """Replace each point with an earlier point only; preserves scale but breaks timing."""
    rng = np.random.default_rng(seed)
    result = np.zeros_like(values)
    result[0] = values[0]
    for t in range(1, len(values)):
        result[t] = values[int(rng.integers(0, t))]
    return result


def build_reservoirs(nodes: list[joint.Node], cutoff: int) -> dict[str, np.ndarray]:
    nino = base.standardize_from_training(nodes[0].values, cutoff)
    soi = base.standardize_from_training(nodes[1].values, cutoff)
    west = base.standardize_from_training(nodes[2].values, cutoff)
    east = base.standardize_from_training(nodes[3].values, cutoff)
    iod = base.standardize_from_training(nodes[4].values, cutoff)
    pdo = base.standardize_from_training(nodes[5].values, cutoff)

    nino_spin = np.nan_to_num(nino - base.shifted(nino, 1))
    wwv_oriented = np.nan_to_num(east - west)
    lower_packet = nino_spin + wwv_oriented / PHI

    one_store = np.zeros(len(nino))
    two_store = np.zeros(len(nino))
    one_release = np.zeros(len(nino))
    two_release = np.zeros(len(nino))
    for t in range(len(nino) - 1):
        one_release[t] = RELEASE * one_store[t]
        two_release[t] = RELEASE * two_store[t]
        one_deposit = DENSITY_ONE * GAP_SHARE * lower_packet[t]
        two_deposit = DENSITY_TWO * (GAP_SHARE**2) * one_store[t]
        one_store[t + 1] = RETAIN * one_store[t] + one_deposit
        two_store[t + 1] = RETAIN * two_store[t] + two_deposit
    one_release[-1] = RELEASE * one_store[-1]
    two_release[-1] = RELEASE * two_store[-1]

    null_two_release = causal_prior_null(two_release)
    upper_grip = 1.0 + np.abs(pdo) / PHI
    direct_surface = (
        DIRECT_SHARE * wwv_oriented
        + (PHI**-1) * (-soi)
        + (PHI**-2) * iod
    ) / upper_grip
    no_reservoir = direct_surface
    one_rung = direct_surface - one_release / upper_grip
    two_rung = direct_surface - one_release / upper_grip + two_release / upper_grip
    null_two_rung = direct_surface - one_release / upper_grip + null_two_release / upper_grip
    return {
        "nino_spin": nino_spin,
        "wwv_oriented": wwv_oriented,
        "upper_grip": upper_grip,
        "one_store": one_store,
        "two_store": two_store,
        "one_release": one_release,
        "two_release": two_release,
        "null_two_release": null_two_release,
        "no_reservoir": no_reservoir,
        "one_rung": one_rung,
        "two_rung": two_rung,
        "null_two_rung": null_two_rung,
    }


def lag_matrix(values: np.ndarray, origins: np.ndarray, lags: tuple[int, ...]) -> np.ndarray:
    return np.asarray([[values[t - lag] for lag in lags] for t in origins], dtype=float)


def direct_prediction(
    pressure: np.ndarray,
    home: np.ndarray,
    train_origins: np.ndarray,
    test_origins: np.ndarray,
    horizon: int,
) -> np.ndarray:
    """Train-scale only: converts dimensionless pressure into native NINO units."""
    train_delta = home[train_origins + horizon] - home[train_origins]
    train_pressure = pressure[train_origins] * math.sqrt(horizon / 48.0)
    test_pressure = pressure[test_origins] * math.sqrt(horizon / 48.0)
    std = float(np.std(train_pressure))
    scale = float(np.std(train_delta) / std) if std > 1e-12 else 0.0
    return home[test_origins] + scale * test_pressure


def reservoir_features(
    state: dict[str, np.ndarray],
    origins: np.ndarray,
    variant: str,
    lags: tuple[int, ...],
) -> np.ndarray:
    names = {
        "no_reservoir": ("no_reservoir",),
        "one_rung": ("one_rung", "one_store", "one_release"),
        "two_rung": ("two_rung", "one_store", "one_release", "two_store", "two_release"),
        "null_two_rung": (
            "null_two_rung",
            "one_store",
            "one_release",
            "null_two_release",
        ),
    }[variant]
    blocks = [lag_matrix(state[name], origins, lags) for name in names]
    return np.column_stack(blocks)


def evaluate() -> dict:
    nodes = joint.build_nodes()
    home = nodes[0].values
    n = len(home)
    cutoff = int(n * 0.60)
    state = build_reservoirs(nodes, cutoff)
    raw_lags = (0, 1, 3, 6, 12)
    reservoir_lags = (0, 1, 3, 6)
    horizons = (1, 3, 6, 9, 12, 18, 24)
    origins = np.arange(max(raw_lags + reservoir_lags) + 2, n)
    raw = joint.raw_lag_matrix(nodes, origins, raw_lags)
    result = {
        "constants": {
            "phi": PHI,
            "gap_share_normalized": GAP_SHARE,
            "direct_share_normalized": DIRECT_SHARE,
            "retain_per_tick": RETAIN,
            "release_per_tick": RELEASE,
            "one_rung_density": DENSITY_ONE,
            "two_rung_density": DENSITY_TWO,
        },
        "horizons": {},
    }
    for horizon in horizons:
        valid = origins + horizon < n
        train = valid & (origins + horizon < cutoff)
        test = valid & (origins >= cutoff)
        train_origins = origins[train]
        test_origins = origins[test]
        train_target = home[train_origins + horizon]
        test_target = home[test_origins + horizon]
        train_current = home[train_origins]
        test_current = home[test_origins]
        train_delta = train_target - train_current
        raw_train = raw[train]
        raw_test = raw[test]
        raw_pred = test_current + base.ridge_readout(raw_train, train_delta, raw_test)
        row = {
            "persistence": base.metrics(test_target, test_current, test_current),
            "raw_topology_var": base.metrics(test_target, raw_pred, test_current),
        }
        for variant in ("no_reservoir", "one_rung", "two_rung", "null_two_rung"):
            direct = direct_prediction(state[variant], home, train_origins, test_origins, horizon)
            feature_train = reservoir_features(state, train_origins, variant, reservoir_lags)
            feature_test = reservoir_features(state, test_origins, variant, reservoir_lags)
            readout = test_current + base.ridge_readout(feature_train, train_delta, feature_test)
            combined = test_current + base.ridge_readout(
                np.column_stack([raw_train, feature_train]),
                train_delta,
                np.column_stack([raw_test, feature_test]),
            )
            row[f"direct_{variant}"] = base.metrics(test_target, direct, test_current)
            row[f"readout_{variant}"] = base.metrics(test_target, readout, test_current)
            row[f"var_plus_{variant}"] = base.metrics(test_target, combined, test_current)
        result["horizons"][str(horizon)] = row
    return result


def main() -> None:
    result = evaluate()
    print("## ENSO cross-rung reservoir ablation: corr / MAE / direction\n")
    for horizon, row in result["horizons"].items():
        print(f"{horizon:>3}m ", end="")
        for model in (
            "persistence",
            "raw_topology_var",
            "direct_no_reservoir",
            "direct_one_rung",
            "direct_two_rung",
            "direct_null_two_rung",
            "var_plus_one_rung",
            "var_plus_two_rung",
            "var_plus_null_two_rung",
        ):
            score = row[model]
            print(f"{model}={score['corr']:+.3f}/{score['mae']:.3f}/{score['turn']:.3f} ", end="")
        print()
    output = HERE / "ara_enso_cross_rung_reservoir_result.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"\nWrote {output}")


if __name__ == "__main__":
    main()
