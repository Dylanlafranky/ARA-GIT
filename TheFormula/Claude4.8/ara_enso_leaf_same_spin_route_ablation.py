"""Strict-causal ENSO leaf-fall route ablation.

This tests one narrow refinement of the recursive recycling geometry:

    contact transfer is not automatically coherent absorption

Adjacent rolling layers counterspin.  A packet shed from an upper sphere may
touch the adjacent lower sphere but settle coherently only after falling two
physical rungs, where orientation matches again.

The causal brown-to-green leaf pulse from
ara_enso_causal_leaf_fall_ablation.py is therefore routed into storage rather
than subtracted directly from the measured ENSO pressure:

    ordinary_recursive_gate
        no upper leaf packet

    leaf_one_rung_opposite
        leaf packet settles in the adjacent counterspinning reservoir

    leaf_two_rung_same
        leaf packet bypasses the adjacent store and settles two rungs down,
        where spin orientation matches again

    leaf_two_rung_same_null
        same two-rung geometry, but leaf timing delayed by one green rung

The ordinary recursive gate is a required reference.  The three leaf routes
are the declared ablation variants.

Each stored packet returns only when the pre-existing local recursive ARA gate
opens.  No immediate leaf-to-surface amplitude correction is applied.

All origin features use observations <= t.  No FFT, Hilbert transform,
future lookup, smoothing, analog averaging, future-origin shift, or held-out
hyperparameter selection is used.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import ara_enso_causal_leaf_fall_ablation as leaf
import ara_enso_cross_rung_reservoir_test as fixed
import ara_enso_recursive_gate_reservoir_test as gated
import ara_joint_enso_topology_direction_test as joint
import ara_unified_layered_framework_test as base

HERE = Path(__file__).resolve().parent
PHI = base.PHI
GAP_SHARE = (2.0 - PHI) / 2.0
RELEASE = 1.0 / (PHI * PHI)
DISSIPATE = GAP_SHARE**2
DENSITY_ONE = 2.0
DENSITY_TWO = 4.0


def simulate_routed_stores(
    lower_packet: np.ndarray,
    one_gate: np.ndarray,
    two_gate: np.ndarray,
    leaf_packet: np.ndarray,
    route: str,
) -> dict[str, np.ndarray]:
    """Store a falling leaf at the selected physical depth, then wait for its gate."""
    n = len(lower_packet)
    one_store = np.zeros(n)
    two_store = np.zeros(n)
    one_release = np.zeros(n)
    two_release = np.zeros(n)
    one_leaf_deposit = np.zeros(n)
    two_leaf_deposit = np.zeros(n)

    if route == "one_rung_opposite":
        one_leaf_deposit = DENSITY_ONE * GAP_SHARE * leaf_packet
    elif route == "two_rung_same":
        two_leaf_deposit = DENSITY_TWO * (GAP_SHARE**2) * leaf_packet
    elif route != "none":
        raise ValueError(f"unknown leaf route: {route}")

    for t in range(n - 1):
        one_fill = math.tanh(abs(float(one_store[t])))
        two_fill = math.tanh(abs(float(two_store[t])))
        one_release[t] = RELEASE * one_gate[t] * one_fill * one_store[t]
        two_release[t] = RELEASE * two_gate[t] * two_fill * two_store[t]

        one_deposit = DENSITY_ONE * GAP_SHARE * lower_packet[t] + one_leaf_deposit[t]
        two_deposit = DENSITY_TWO * (GAP_SHARE**2) * lower_packet[t] + two_leaf_deposit[t]
        one_store[t + 1] = (
            (1.0 - DISSIPATE) * one_store[t] + one_deposit - one_release[t]
        )
        two_store[t + 1] = (
            (1.0 - DISSIPATE) * two_store[t] + two_deposit - two_release[t]
        )

    one_fill = math.tanh(abs(float(one_store[-1])))
    two_fill = math.tanh(abs(float(two_store[-1])))
    one_release[-1] = RELEASE * one_gate[-1] * one_fill * one_store[-1]
    two_release[-1] = RELEASE * two_gate[-1] * two_fill * two_store[-1]
    return {
        "one_store": one_store,
        "two_store": two_store,
        "one_release": one_release,
        "two_release": two_release,
        "one_leaf_deposit": one_leaf_deposit,
        "two_leaf_deposit": two_leaf_deposit,
    }


def build_route_state(
    fixed_state: dict[str, np.ndarray],
    lower_packet: np.ndarray,
    one_gate: np.ndarray,
    two_gate: np.ndarray,
    leaf_packet: np.ndarray,
    route: str,
) -> dict[str, np.ndarray]:
    """Build one route without altering the common direct surface or lower gates."""
    state = simulate_routed_stores(lower_packet, one_gate, two_gate, leaf_packet, route)
    upper_grip = fixed_state["upper_grip"]
    direct_surface = fixed_state["no_reservoir"]
    state.update(
        {
            "one_gate": one_gate,
            "two_gate": two_gate,
            "leaf": leaf_packet,
            "pressure": (
                direct_surface
                - state["one_release"] / upper_grip
                + state["two_release"] / upper_grip
            ),
        }
    )
    return state


def build_states(nodes: list[joint.Node], cutoff: int) -> dict[str, dict[str, np.ndarray]]:
    fixed_state = fixed.build_reservoirs(nodes, cutoff)
    existing_gate = gated.build_states(nodes, cutoff)["recursive_gate"]
    nino = base.standardize_from_training(nodes[0].values, cutoff)
    west = base.standardize_from_training(nodes[2].values, cutoff)
    east = base.standardize_from_training(nodes[3].values, cutoff)
    wwv_oriented = np.nan_to_num(east - west)
    nino_spin = np.nan_to_num(nino - base.shifted(nino, 1))
    lower_packet = nino_spin + wwv_oriented / PHI
    leaf_state = leaf.causal_leaf_state(nino)
    null_leaf = leaf.causal_lag_null(leaf_state["leaf"], leaf.LEAF_NULL_LAG)
    one_gate = existing_gate["one_gate"]
    two_gate = existing_gate["two_gate"]
    zeros = np.zeros(len(nino))
    return {
        "ordinary_recursive_gate": build_route_state(
            fixed_state, lower_packet, one_gate, two_gate, zeros, "none"
        ),
        "leaf_one_rung_opposite": build_route_state(
            fixed_state, lower_packet, one_gate, two_gate, leaf_state["leaf"], "one_rung_opposite"
        ),
        "leaf_two_rung_same": build_route_state(
            fixed_state, lower_packet, one_gate, two_gate, leaf_state["leaf"], "two_rung_same"
        ),
        "leaf_two_rung_same_null": build_route_state(
            fixed_state, lower_packet, one_gate, two_gate, null_leaf, "two_rung_same"
        ),
    }


def variant_features(
    state: dict[str, np.ndarray],
    origins: np.ndarray,
    variant: str,
    lags: tuple[int, ...],
) -> np.ndarray:
    """Expose routed storage and release only, not the raw leaf pulse shortcut."""
    names = [
        "pressure",
        "one_store",
        "one_release",
        "two_store",
        "two_release",
        "one_gate",
        "two_gate",
    ]
    return np.column_stack([fixed.lag_matrix(state[name], origins, lags) for name in names])


def evaluate() -> dict:
    nodes = joint.build_nodes()
    home = nodes[0].values
    n = len(home)
    cutoff = int(n * 0.60)
    states = build_states(nodes, cutoff)
    raw_lags = (0, 1, 3, 6, 12)
    route_lags = (0, 1, 3, 6)
    horizons = (1, 3, 6, 9, 12, 18, 24, 30, 36, 48, 60)
    origins = np.arange(max(leaf.MIN_HISTORY, max(raw_lags + route_lags) + 2), n)
    raw = joint.raw_lag_matrix(nodes, origins, raw_lags)
    result = {
        "constants": {
            "phi": PHI,
            "gap_share_normalized": GAP_SHARE,
            "one_rung_density": DENSITY_ONE,
            "two_rung_density": DENSITY_TWO,
            "release_when_gate_open": RELEASE,
            "irrecoverable_loss_proxy_per_tick": DISSIPATE,
            "leaf_null_lag_months": leaf.LEAF_NULL_LAG,
        },
        "formula_visibility": {
            "sees_at_origin_or_earlier": [
                "NINO",
                "SOI",
                "WWV west",
                "WWV east",
                "IOD",
                "PDO",
                "stored recursive-gate reservoir state",
                "past-only raw-NINO causal leaf pulse",
            ],
            "does_not_see": [
                "future NINO",
                "full-series FFT bands",
                "Hilbert envelopes",
                "future-origin features",
                "held-out tuning scores during formula construction",
            ],
            "direct_formula": "upper leaf enters selected lower store; surface changes only after the selected store releases through its existing causal gate",
            "var_plus_diagnostic": "train-only ridge readout; not the physical formula",
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
        for variant in (
            "ordinary_recursive_gate",
            "leaf_one_rung_opposite",
            "leaf_two_rung_same",
            "leaf_two_rung_same_null",
        ):
            state = states[variant]
            direct = fixed.direct_prediction(
                state["pressure"],
                home,
                train_origins,
                test_origins,
                horizon,
            )
            feature_train = variant_features(state, train_origins, variant, route_lags)
            feature_test = variant_features(state, test_origins, variant, route_lags)
            combined = test_current + base.ridge_readout(
                np.column_stack([raw_train, feature_train]),
                train_delta,
                np.column_stack([raw_test, feature_test]),
            )
            row[f"direct_{variant}"] = base.metrics(test_target, direct, test_current)
            row[f"var_plus_{variant}"] = base.metrics(test_target, combined, test_current)
        result["horizons"][str(horizon)] = row
    return result


def main() -> None:
    result = evaluate()
    print("## ENSO causal leaf same-spin route: corr / MAE / direction\n")
    for horizon, row in result["horizons"].items():
        print(f"{horizon:>3}m ", end="")
        for model in (
            "persistence",
            "raw_topology_var",
            "direct_ordinary_recursive_gate",
            "direct_leaf_one_rung_opposite",
            "direct_leaf_two_rung_same",
            "direct_leaf_two_rung_same_null",
            "var_plus_ordinary_recursive_gate",
            "var_plus_leaf_one_rung_opposite",
            "var_plus_leaf_two_rung_same",
            "var_plus_leaf_two_rung_same_null",
        ):
            score = row[model]
            print(f"{model}={score['corr']:+.3f}/{score['mae']:.3f}/{score['turn']:.3f} ", end="")
        print()
    output = HERE / "ara_enso_leaf_same_spin_route_ablation_result.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"\nWrote {output}")


if __name__ == "__main__":
    main()
