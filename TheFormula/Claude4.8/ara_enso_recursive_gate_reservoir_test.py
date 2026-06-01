"""Strict-causal ENSO recursive gate reservoir ablation.

This is the dynamic follow-up to ara_enso_cross_rung_reservoir_test.py.
The earlier reservoir released a fixed fraction every month.  This version
stores diverted energy until a local handoff gate opens.

One repeated gate is applied recursively:

    handoff_gate(local, receiver)
        = recursive_ARA_boundary_pressure(local)
        * projected_phase_window(local, receiver, 36 degrees)

    release(store, gate)
        = (1 / phi^2) * gate * tanh(abs(store)) * store

The two physical depths retain the same intrinsic x2 octave ladder:

    measured surface -> one-rung lower reservoir -> two-rung lower reservoir

Adjacent contact reverses orientation.  A two-rung return recovers the
measured orientation after two reversals.  WWV east-west is the observed
one-rung coordinate.  The lower packet is a latent two-rung proxy until a
better observed lower-lower candidate is identified.

Three declared reservoir variants are tested:

    fixed_release          old fixed-duty two-rung reservoir
    recursive_gate         dynamic two-rung recursive handoff gates
    recursive_gate_null    same dynamic stores with gate timing replaced by
                           causally selected earlier gate values

The direct formula and train-only raw-topology readout are reported separately.
All origin features use observations <= t.  No FFT, Hilbert transform,
future lookup, smoothing, analog averaging, future-origin shift, or held-out
hyperparameter selection is used.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import ara_enso_cross_rung_reservoir_test as fixed
import ara_joint_enso_topology_direction_test as joint
import ara_unified_layered_framework_test as base
import ara_vector_pose_energy_ratio_test as pose

HERE = Path(__file__).resolve().parent
PHI = base.PHI
SHEAR = math.pi / 5.0
GAP_SHARE = (2.0 - PHI) / 2.0
DIRECT_SHARE = PHI / 2.0
RELEASE = 1.0 / (PHI * PHI)
DISSIPATE = GAP_SHARE**2
DENSITY_ONE = 2.0
DENSITY_TWO = 4.0
HOME_PERIOD = 48.0
ONE_PERIOD = HOME_PERIOD / 2.0
TWO_PERIOD = ONE_PERIOD / 2.0
TERRAIN_DEPTH = 5
RIDGE_CEILING = sum(PHI ** (-(level + 1)) for level in range(TERRAIN_DEPTH))


def ara_from_z(values: np.ndarray) -> np.ndarray:
    """Map a train-standardized local coordinate into the bounded ARA range."""
    return 1.0 + np.tanh(values / 2.0)


def recursive_boundary_pressure(values: np.ndarray) -> np.ndarray:
    """Read the filled recursive ARA grid: high near a local handoff boundary."""
    result = np.zeros(len(values))
    for index, value in enumerate(ara_from_z(values)):
        _, ridge = pose.recursive_terrain_scalar(float(value), depth=TERRAIN_DEPTH)
        result[index] = float(np.clip(ridge / RIDGE_CEILING, 0.0, 1.0))
    return result


def handoff_gate(
    local_z: np.ndarray,
    local_phase: np.ndarray,
    receiver_phase: np.ndarray,
) -> dict[str, np.ndarray]:
    """Same projected handoff gate at every adjacent physical contact."""
    terrain = recursive_boundary_pressure(local_z)
    # Adjacent spheres roll in opposite orientations.  The same 36-degree
    # Time-axis shear is applied again at every recursive contact.
    phase_error = local_phase - receiver_phase - math.pi - SHEAR
    phase_window = np.nan_to_num(0.5 + 0.5 * np.cos(phase_error))
    openness = terrain * phase_window
    return {
        "terrain": terrain,
        "phase_window": phase_window,
        "openness": openness,
    }


def simulate_gated_stores(
    lower_packet: np.ndarray,
    one_gate: np.ndarray,
    two_gate: np.ndarray,
) -> dict[str, np.ndarray]:
    """Store diverted flow and release it only through the repeated local gate."""
    n = len(lower_packet)
    one_store = np.zeros(n)
    two_store = np.zeros(n)
    one_release = np.zeros(n)
    two_release = np.zeros(n)
    for t in range(n - 1):
        one_fill = math.tanh(abs(float(one_store[t])))
        two_fill = math.tanh(abs(float(two_store[t])))
        one_release[t] = RELEASE * one_gate[t] * one_fill * one_store[t]
        two_release[t] = RELEASE * two_gate[t] * two_fill * two_store[t]

        # Falling packets get denser on the head-on x2 Space reading.  The
        # same normalized gap is applied again one depth lower.
        one_deposit = DENSITY_ONE * GAP_SHARE * lower_packet[t]
        two_deposit = DENSITY_TWO * (GAP_SHARE**2) * lower_packet[t]
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
    }


def build_states(nodes: list[joint.Node], cutoff: int) -> dict[str, dict[str, np.ndarray]]:
    """Build the old fixed state and the new dynamic gate state."""
    fixed_state = fixed.build_reservoirs(nodes, cutoff)
    nino = base.standardize_from_training(nodes[0].values, cutoff)
    west = base.standardize_from_training(nodes[2].values, cutoff)
    east = base.standardize_from_training(nodes[3].values, cutoff)
    wwv_oriented = np.nan_to_num(east - west)
    nino_spin = np.nan_to_num(nino - base.shifted(nino, 1))
    lower_packet = nino_spin + wwv_oriented / PHI

    home_phase = pose.causal_phase(nino, HOME_PERIOD)
    one_phase = pose.causal_phase(wwv_oriented, ONE_PERIOD)
    two_phase = pose.causal_phase(lower_packet, TWO_PERIOD)
    one_gate_parts = handoff_gate(wwv_oriented, one_phase, home_phase)
    two_gate_parts = handoff_gate(lower_packet, two_phase, one_phase)
    gated = simulate_gated_stores(
        lower_packet,
        one_gate_parts["openness"],
        two_gate_parts["openness"],
    )

    null_one_gate = fixed.causal_prior_null(one_gate_parts["openness"], seed=20260531)
    null_two_gate = fixed.causal_prior_null(two_gate_parts["openness"], seed=20260601)
    gate_null = simulate_gated_stores(lower_packet, null_one_gate, null_two_gate)

    upper_grip = fixed_state["upper_grip"]
    direct_surface = fixed_state["no_reservoir"]
    gated["pressure"] = (
        direct_surface - gated["one_release"] / upper_grip + gated["two_release"] / upper_grip
    )
    gate_null["pressure"] = (
        direct_surface
        - gate_null["one_release"] / upper_grip
        + gate_null["two_release"] / upper_grip
    )
    gated.update(
        {
            "one_gate": one_gate_parts["openness"],
            "two_gate": two_gate_parts["openness"],
            "one_terrain": one_gate_parts["terrain"],
            "two_terrain": two_gate_parts["terrain"],
            "one_phase_window": one_gate_parts["phase_window"],
            "two_phase_window": two_gate_parts["phase_window"],
        }
    )
    gate_null.update({"one_gate": null_one_gate, "two_gate": null_two_gate})
    return {"fixed_release": fixed_state, "recursive_gate": gated, "recursive_gate_null": gate_null}


def variant_pressure(state: dict[str, np.ndarray], variant: str) -> np.ndarray:
    if variant == "fixed_release":
        return state["two_rung"]
    return state["pressure"]


def variant_features(
    state: dict[str, np.ndarray],
    origins: np.ndarray,
    variant: str,
    lags: tuple[int, ...],
) -> np.ndarray:
    if variant == "fixed_release":
        names = ("two_rung", "one_store", "one_release", "two_store", "two_release")
    else:
        names = (
            "pressure",
            "one_store",
            "one_release",
            "two_store",
            "two_release",
            "one_gate",
            "two_gate",
        )
    return np.column_stack(
        [fixed.lag_matrix(state[name], origins, lags) for name in names]
    )


def evaluate() -> dict:
    nodes = joint.build_nodes()
    home = nodes[0].values
    n = len(home)
    cutoff = int(n * 0.60)
    states = build_states(nodes, cutoff)
    raw_lags = (0, 1, 3, 6, 12)
    reservoir_lags = (0, 1, 3, 6)
    horizons = (1, 3, 6, 9, 12, 18, 24)
    origins = np.arange(max(raw_lags + reservoir_lags) + 2, n)
    raw = joint.raw_lag_matrix(nodes, origins, raw_lags)
    result = {
        "constants": {
            "phi": PHI,
            "time_projection_identity": "2*cos(36 degrees)=phi",
            "gap_share_normalized": GAP_SHARE,
            "release_when_gate_open": RELEASE,
            "irrecoverable_loss_proxy_per_tick": DISSIPATE,
            "home_period_months": HOME_PERIOD,
            "one_rung_period_months": ONE_PERIOD,
            "two_rung_period_months": TWO_PERIOD,
            "terrain_depth": TERRAIN_DEPTH,
        },
        "formula_visibility": {
            "sees_at_origin_or_earlier": [
                "NINO",
                "SOI",
                "WWV west",
                "WWV east",
                "IOD",
                "PDO",
            ],
            "does_not_see": [
                "future NINO",
                "future-origin features",
                "smoothed future envelopes",
                "held-out tuning scores during formula construction",
            ],
            "direct_formula": "dimensionless pressure converted with training-only scale",
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
        for variant in ("fixed_release", "recursive_gate", "recursive_gate_null"):
            state = states[variant]
            direct = fixed.direct_prediction(
                variant_pressure(state, variant),
                home,
                train_origins,
                test_origins,
                horizon,
            )
            feature_train = variant_features(state, train_origins, variant, reservoir_lags)
            feature_test = variant_features(state, test_origins, variant, reservoir_lags)
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
    print("## ENSO recursive gate reservoir: corr / MAE / direction\n")
    for horizon, row in result["horizons"].items():
        print(f"{horizon:>3}m ", end="")
        for model in (
            "persistence",
            "raw_topology_var",
            "direct_fixed_release",
            "direct_recursive_gate",
            "direct_recursive_gate_null",
            "var_plus_fixed_release",
            "var_plus_recursive_gate",
            "var_plus_recursive_gate_null",
        ):
            score = row[model]
            print(f"{model}={score['corr']:+.3f}/{score['mae']:.3f}/{score['turn']:.3f} ", end="")
        print()
    output = HERE / "ara_enso_recursive_gate_reservoir_result.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"\nWrote {output}")


if __name__ == "__main__":
    main()
