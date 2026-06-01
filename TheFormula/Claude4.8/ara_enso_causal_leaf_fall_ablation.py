"""Strict-causal ENSO upper leaf-fall pressure ablation.

This extends ara_enso_recursive_gate_reservoir_test.py with one ENSO-specific
upper-shock channel.  The lower WWV gate remains unchanged:

    WWV / green lower feed -> frequent lower-rung input and return timing

The new channel is separate:

    brown-to-green crossover -> intermittent upper-rung leaf-fall pressure

The older green/brown descriptive scripts used full-series FFT bands and
Hilbert envelopes.  Those are useful clues but are not legal forecast inputs.
This script rebuilds a minimal causal crossover state from raw NINO history.

At each month t:

    1. Fit only NINO[0:t] plus the current observed NINO[t].
    2. Use two geometry-declared periods:
           brown = home period = 48 months
           green = home period / phi
    3. Read current brown and green components and their one-step motion.
    4. Emit a leaf pulse when brown is falling near the brown/green crossover.

The leaf pressure is applied as an upper downward shock plus brake:

    leaf_brake = 1 + leaf / phi
    pressure_with_leaf = (recursive_gate_pressure - g * leaf) / leaf_brake

where g = (2 - phi) / 2.

Three declared variants are tested:

    recursive_gate       no upper leaf channel
    causal_leaf          real past-only brown-to-green crossover timing
    causal_leaf_null     same leaf series delayed by one green rung to break
                         timing while preserving pulse shape and scale

The direct formula and train-only raw-topology diagnostics are reported
separately.  No FFT, Hilbert transform, full-series period selection, smoothing,
future lookup, analog averaging, future-origin shift, or held-out
hyperparameter selection is used.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import ara_enso_cross_rung_reservoir_test as fixed
import ara_enso_recursive_gate_reservoir_test as gated
import ara_joint_enso_topology_direction_test as joint
import ara_unified_layered_framework_test as base

HERE = Path(__file__).resolve().parent
PHI = base.PHI
GAP_SHARE = (2.0 - PHI) / 2.0
HOME_PERIOD = 48.0
BROWN_PERIOD = HOME_PERIOD
GREEN_PERIOD = HOME_PERIOD / PHI
MIN_HISTORY = int(round(4.0 * HOME_PERIOD))
LEAF_NULL_LAG = int(round(GREEN_PERIOD))


def harmonic_design(months: np.ndarray) -> np.ndarray:
    """Declared two-wave basis: trend, green phi-rung, and brown home rung."""
    green_angle = 2.0 * math.pi * months / GREEN_PERIOD
    brown_angle = 2.0 * math.pi * months / BROWN_PERIOD
    return np.column_stack(
        [
            np.ones(len(months)),
            months,
            np.cos(green_angle),
            np.sin(green_angle),
            np.cos(brown_angle),
            np.sin(brown_angle),
        ]
    )


def split_components(months: np.ndarray, coefficients: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Read only the green and brown parts of the declared causal harmonic fit."""
    design = harmonic_design(months)
    green = design[:, 2:4] @ coefficients[2:4]
    brown = design[:, 4:6] @ coefficients[4:6]
    return green, brown


def causal_leaf_state(nino_z: np.ndarray) -> dict[str, np.ndarray]:
    """Build the upper leaf pulse with a fresh past-only fit at every month."""
    n = len(nino_z)
    green = np.zeros(n)
    brown = np.zeros(n)
    brown_shed = np.zeros(n)
    crossover_proximity = np.zeros(n)
    leaf = np.zeros(n)
    months = np.arange(n, dtype=float)

    for t in range(MIN_HISTORY, n):
        observed = np.arange(t + 1)
        coefficients, *_ = np.linalg.lstsq(
            harmonic_design(months[observed]),
            nino_z[observed],
            rcond=None,
        )
        current_months = np.asarray([months[t - 1], months[t]])
        green_pair, brown_pair = split_components(current_months, coefficients)
        green[t] = float(green_pair[1])
        brown[t] = float(brown_pair[1])
        brown_shed[t] = max(0.0, float(brown_pair[0] - brown_pair[1]))
        separation = float(brown_pair[1] - green_pair[1])
        crossover_proximity[t] = math.exp(-abs(separation))
        leaf[t] = math.tanh(brown_shed[t]) * crossover_proximity[t]

    return {
        "green": green,
        "brown": brown,
        "brown_shed": brown_shed,
        "crossover_proximity": crossover_proximity,
        "leaf": leaf,
    }


def add_leaf_pressure(
    lower_state: dict[str, np.ndarray],
    leaf_state: dict[str, np.ndarray],
    leaf_values: np.ndarray,
) -> dict[str, np.ndarray]:
    """Apply the upper packet as pressure and braking, not as steady lower fuel."""
    state = dict(lower_state)
    brake = 1.0 + leaf_values / PHI
    state.update(leaf_state)
    state["leaf"] = leaf_values
    state["leaf_brake"] = brake
    state["pressure"] = (lower_state["pressure"] - GAP_SHARE * leaf_values) / brake
    return state


def causal_lag_null(values: np.ndarray, lag: int) -> np.ndarray:
    """Shift the leaf series later using earlier values only."""
    result = np.zeros_like(values)
    result[lag:] = values[:-lag]
    return result


def build_states(nodes: list[joint.Node], cutoff: int) -> dict[str, dict[str, np.ndarray]]:
    lower = gated.build_states(nodes, cutoff)["recursive_gate"]
    nino_z = base.standardize_from_training(nodes[0].values, cutoff)
    leaf_state = causal_leaf_state(nino_z)
    null_leaf = causal_lag_null(leaf_state["leaf"], LEAF_NULL_LAG)
    return {
        "recursive_gate": lower,
        "causal_leaf": add_leaf_pressure(lower, leaf_state, leaf_state["leaf"]),
        "causal_leaf_null": add_leaf_pressure(lower, leaf_state, null_leaf),
    }


def variant_features(
    state: dict[str, np.ndarray],
    origins: np.ndarray,
    variant: str,
    lags: tuple[int, ...],
) -> np.ndarray:
    names = [
        "pressure",
        "one_store",
        "one_release",
        "two_store",
        "two_release",
        "one_gate",
        "two_gate",
    ]
    if variant != "recursive_gate":
        names.extend(["leaf", "leaf_brake"])
    return np.column_stack([fixed.lag_matrix(state[name], origins, lags) for name in names])


def evaluate() -> dict:
    nodes = joint.build_nodes()
    home = nodes[0].values
    n = len(home)
    cutoff = int(n * 0.60)
    states = build_states(nodes, cutoff)
    raw_lags = (0, 1, 3, 6, 12)
    event_lags = (0, 1, 3, 6)
    horizons = (1, 3, 6, 9, 12, 18, 24)
    origins = np.arange(max(MIN_HISTORY, max(raw_lags + event_lags) + 2), n)
    raw = joint.raw_lag_matrix(nodes, origins, raw_lags)
    result = {
        "constants": {
            "phi": PHI,
            "gap_share_normalized": GAP_SHARE,
            "brown_period_months": BROWN_PERIOD,
            "green_period_months": GREEN_PERIOD,
            "period_rule": "brown=home; green=home/phi",
            "minimum_history_months": MIN_HISTORY,
            "causal_null_lag_months": LEAF_NULL_LAG,
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
                "past-only raw-NINO green/brown harmonic fit",
            ],
            "does_not_see": [
                "future NINO",
                "full-series FFT bands",
                "Hilbert envelopes",
                "future-origin features",
                "held-out tuning scores during formula construction",
            ],
            "direct_formula": "recursive lower-gate pressure with declared upper leaf shock and training-only native-unit scale",
            "var_plus_diagnostic": "train-only ridge readout; not the physical formula",
        },
        "leaf_summary": {},
        "horizons": {},
    }
    real_leaf = states["causal_leaf"]["leaf"]
    null_leaf = states["causal_leaf_null"]["leaf"]
    for name, values in (("real", real_leaf), ("causal_lag_null", null_leaf)):
        result["leaf_summary"][name] = {
            "mean": float(np.mean(values)),
            "std": float(np.std(values)),
            "max": float(np.max(values)),
            "positive_months": int(np.sum(values > 0.0)),
            "strong_months_above_0_05": int(np.sum(values > 0.05)),
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
        for variant in ("recursive_gate", "causal_leaf", "causal_leaf_null"):
            state = states[variant]
            direct = fixed.direct_prediction(
                state["pressure"],
                home,
                train_origins,
                test_origins,
                horizon,
            )
            feature_train = variant_features(state, train_origins, variant, event_lags)
            feature_test = variant_features(state, test_origins, variant, event_lags)
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
    print("## ENSO causal brown-to-green leaf fall: corr / MAE / direction\n")
    for horizon, row in result["horizons"].items():
        print(f"{horizon:>3}m ", end="")
        for model in (
            "persistence",
            "raw_topology_var",
            "direct_recursive_gate",
            "direct_causal_leaf",
            "direct_causal_leaf_null",
            "var_plus_recursive_gate",
            "var_plus_causal_leaf",
            "var_plus_causal_leaf_null",
        ):
            score = row[model]
            print(f"{model}={score['corr']:+.3f}/{score['mae']:.3f}/{score['turn']:.3f} ", end="")
        print()
    print("\nLeaf pulse summary:")
    for name, row in result["leaf_summary"].items():
        print(
            f"  {name}: mean={row['mean']:.4f} std={row['std']:.4f} "
            f"max={row['max']:.4f} strong_months={row['strong_months_above_0_05']}"
        )
    output = HERE / "ara_enso_causal_leaf_fall_ablation_result.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"\nWrote {output}")


if __name__ == "__main__":
    main()
