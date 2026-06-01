"""Strict-causal first pass at a transferable layered ARA prediction equation.

This is deliberately one operator with three input adapters.  It does not use
future samples, historical nearest-neighbour averaging, smoothed targets, or a
future-origin shift.  Every feature at origin t is calculated from samples at
or before t.

The equation tests the layered-sand interpretation:

    lower fast contacts --(orientation flip)--> measured layer roll
    measured layer own spin ------------------> measured layer roll
    upper slow layer pressure ----------------> measured layer brake
    recursive ARA terrain --------------------> local valley / ridge response

The fixed equation is:

    roll_t = (
        phi^-1 * lower_torque_t
      + phi^-2 * own_spin_t
      + phi^-3 * contact_wobble_t
      + phi^-2 * terrain_slope_t
      - phi^-2 * upper_pressure_t
    ) / (
        1 + ridge_pressure_t + abs(upper_pressure_t) / phi
    )

The native-unit fixed forecast is:

    yhat_(t+h) = y_t + train_scale_h * roll_t * sqrt(h / home_period)

The train_scale term only converts a dimensionless roll into native units.
It is fitted on the training segment without seeing any held-out target.

Two diagnostic readouts are also scored:

* ARA roll readout: a train-only ridge readout of the declared ARA terms.
* Home + ARA: the same readout with ordinary causal home lags added.

Those diagnostics ask whether the equation exposes useful predictive state.
They are not substitutes for the fixed physical forecast.
"""

from __future__ import annotations

import json
import math
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PHI = (1.0 + math.sqrt(5.0)) / 2.0

sys.path.insert(0, str(HERE))


@dataclass
class Contact:
    name: str
    values: np.ndarray
    period: float
    window: int
    layer: int = 1


@dataclass
class System:
    name: str
    unit: str
    home: np.ndarray
    home_period: float
    horizons: tuple[int, ...]
    home_lags: tuple[int, ...]
    lower: tuple[Contact, ...]
    upper: tuple[Contact, ...]


def shifted(x: np.ndarray, lag: int) -> np.ndarray:
    result = np.full_like(x, np.nan, dtype=float)
    if lag == 0:
        result[:] = x
    elif lag < len(x):
        result[lag:] = x[:-lag]
    return result


def trailing_mean(x: np.ndarray, window: int) -> np.ndarray:
    result = np.full_like(x, np.nan, dtype=float)
    for i in range(window - 1, len(x)):
        block = x[i - window + 1 : i + 1]
        if np.all(np.isfinite(block)):
            result[i] = float(np.mean(block))
    return result


def standardize_from_training(x: np.ndarray, cutoff: int) -> np.ndarray:
    train = x[:cutoff]
    train = train[np.isfinite(train)]
    mean = float(np.mean(train))
    std = float(np.std(train))
    if not np.isfinite(std) or std < 1e-12:
        std = 1.0
    return (x - mean) / std


def recursive_terrain(ara: np.ndarray, depth: int = 5) -> tuple[np.ndarray, np.ndarray]:
    """Read local phi valleys and recursive ridge pressure on a filled 0..2 grid."""
    slope = np.zeros_like(ara, dtype=float)
    ridge = np.zeros_like(ara, dtype=float)
    for i, value in enumerate(ara):
        if not np.isfinite(value):
            slope[i] = np.nan
            ridge[i] = np.nan
            continue
        x = float(np.clip(value, 0.0, 2.0))
        for level in range(depth):
            cells = 2**level
            width = 2.0 / cells
            cell = min(cells - 1, int(x / width))
            lo = cell * width
            hi = lo + width
            left_phi = lo + width / PHI
            right_phi = hi - width / PHI
            target = left_phi if abs(x - left_phi) <= abs(x - right_phi) else right_phi
            weight = PHI ** (-(level + 1))
            slope[i] += weight * (target - x) / width
            edge_distance = min(x - lo, hi - x) / width
            ridge[i] += weight * (1.0 - 2.0 * edge_distance)
    return slope, np.maximum(0.0, ridge)


def layer_state(system: System, cutoff: int) -> dict[str, np.ndarray]:
    home_z = standardize_from_training(system.home, cutoff)
    own_spin = home_z - shifted(home_z, 1)

    torque = np.zeros_like(home_z)
    wobble = np.zeros_like(home_z)
    lower_terms: list[np.ndarray] = []
    for index, contact in enumerate(system.lower):
        z = standardize_from_training(contact.values, cutoff)
        fast = z - trailing_mean(z, contact.window)
        velocity = fast - shifted(fast, 1)
        frequency_gain = math.sqrt(system.home_period / contact.period)
        parity = -1.0 if contact.layer % 2 else 1.0
        term = parity * (PHI ** (-(contact.layer - 1))) * frequency_gain * velocity
        torque += np.nan_to_num(term)
        lower_terms.append(term)
        wobble += ((-1.0) ** index) * (PHI**(-index)) * np.nan_to_num(term)

    upper_pressure = np.zeros_like(home_z)
    for contact in system.upper:
        z = standardize_from_training(contact.values, cutoff)
        envelope = trailing_mean(z, contact.window)
        upper_pressure += (
            (PHI ** (-contact.layer))
            * math.sqrt(contact.period / system.home_period)
            * np.nan_to_num(envelope)
        )

    ara = 1.0 + np.tanh(home_z / 2.0)
    terrain_slope, ridge_pressure = recursive_terrain(ara)
    denominator = 1.0 + ridge_pressure + np.abs(upper_pressure) / PHI
    roll = (
        (PHI**-1) * torque
        + (PHI**-2) * np.nan_to_num(own_spin)
        + (PHI**-3) * wobble
        + (PHI**-2) * terrain_slope
        - (PHI**-2) * upper_pressure
    ) / denominator
    return {
        "home_z": home_z,
        "ara": ara,
        "own_spin": own_spin,
        "lower_torque": torque,
        "contact_wobble": wobble,
        "upper_pressure": upper_pressure,
        "terrain_slope": terrain_slope,
        "ridge_pressure": ridge_pressure,
        "roll": roll,
    }


def metrics(truth: np.ndarray, pred: np.ndarray, current: np.ndarray) -> dict[str, float]:
    valid = np.isfinite(truth) & np.isfinite(pred) & np.isfinite(current)
    truth = truth[valid]
    pred = pred[valid]
    current = current[valid]
    if len(truth) < 3:
        return {"n": int(len(truth)), "corr": float("nan"), "mae": float("nan"), "turn": float("nan")}
    corr = float(np.corrcoef(truth, pred)[0, 1])
    mae = float(np.mean(np.abs(truth - pred)))
    turn = float(np.mean(np.sign(truth - current) == np.sign(pred - current)))
    return {"n": int(len(truth)), "corr": corr, "mae": mae, "turn": turn}


def feature_matrix(
    system: System,
    state: dict[str, np.ndarray],
    origins: Iterable[int],
    include_home_lags: bool,
) -> np.ndarray:
    rows = []
    for t in origins:
        row = []
        if include_home_lags:
            row.extend(float(system.home[t - lag]) for lag in system.home_lags)
        torque = state["lower_torque"][t]
        upper = state["upper_pressure"][t]
        terrain = state["terrain_slope"][t]
        ridge = state["ridge_pressure"][t]
        roll = state["roll"][t]
        row.extend(
            [
                roll,
                torque,
                state["own_spin"][t],
                state["contact_wobble"][t],
                upper,
                terrain,
                ridge,
                torque * terrain,
                torque * upper,
                roll * ridge,
            ]
        )
        rows.append(row)
    return np.asarray(rows, dtype=float)


def ridge_readout(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_test: np.ndarray,
    penalty: float = 0.1,
) -> np.ndarray:
    means = np.nanmean(x_train, axis=0)
    stds = np.nanstd(x_train, axis=0)
    stds[~np.isfinite(stds) | (stds < 1e-12)] = 1.0
    a = np.nan_to_num((x_train - means) / stds)
    b = np.nan_to_num((x_test - means) / stds)
    a = np.column_stack([np.ones(len(a)), a])
    b = np.column_stack([np.ones(len(b)), b])
    reg = np.eye(a.shape[1]) * penalty
    reg[0, 0] = 0.0
    beta = np.linalg.solve(a.T @ a + reg, a.T @ y_train)
    return b @ beta


def evaluate(system: System) -> dict:
    n = len(system.home)
    cutoff = int(n * 0.60)
    state = layer_state(system, cutoff)
    start = max(max(system.home_lags), *(contact.window + 2 for contact in system.lower + system.upper))
    result = {"cutoff_index": cutoff, "samples": n, "horizons": {}}
    for horizon in system.horizons:
        train_origins = np.arange(start, cutoff - horizon)
        test_origins = np.arange(cutoff, n - horizon)
        train_target = system.home[train_origins + horizon]
        test_target = system.home[test_origins + horizon]
        train_current = system.home[train_origins]
        test_current = system.home[test_origins]
        train_delta = train_target - train_current

        raw_train_roll = state["roll"][train_origins] * math.sqrt(horizon / system.home_period)
        raw_test_roll = state["roll"][test_origins] * math.sqrt(horizon / system.home_period)
        raw_std = float(np.std(raw_train_roll))
        native_scale = float(np.std(train_delta) / raw_std) if raw_std > 1e-12 else 0.0
        fixed_pred = test_current + native_scale * raw_test_roll

        home_x_train = np.asarray(
            [[system.home[t - lag] for lag in system.home_lags] for t in train_origins],
            dtype=float,
        )
        home_x_test = np.asarray(
            [[system.home[t - lag] for lag in system.home_lags] for t in test_origins],
            dtype=float,
        )
        ara_x_train = feature_matrix(system, state, train_origins, include_home_lags=False)
        ara_x_test = feature_matrix(system, state, test_origins, include_home_lags=False)
        combined_x_train = feature_matrix(system, state, train_origins, include_home_lags=True)
        combined_x_test = feature_matrix(system, state, test_origins, include_home_lags=True)

        home_pred = test_current + ridge_readout(home_x_train, train_delta, home_x_test)
        ara_pred = test_current + ridge_readout(ara_x_train, train_delta, ara_x_test)
        combined_pred = test_current + ridge_readout(combined_x_train, train_delta, combined_x_test)
        persistence = test_current.copy()

        result["horizons"][str(horizon)] = {
            "native_scale": native_scale,
            "persistence": metrics(test_target, persistence, test_current),
            "ara_fixed_roll": metrics(test_target, fixed_pred, test_current),
            "ara_roll_readout": metrics(test_target, ara_pred, test_current),
            "home_ar": metrics(test_target, home_pred, test_current),
            "home_plus_ara": metrics(test_target, combined_pred, test_current),
        }
    return result


def build_solar() -> System:
    path = ROOT / "SILSO_Solar" / "SN_m_tot_V2.0.csv"
    data = np.genfromtxt(path, delimiter=";")
    home = np.asarray(data[:, 3], dtype=float)
    home[home < 0] = np.nan
    valid = np.isfinite(home)
    first = int(np.flatnonzero(valid)[0])
    home = home[first:]
    return System(
        name="Solar monthly sunspots",
        unit="month",
        home=home,
        home_period=132.0,
        horizons=(12, 24, 48, 96, 132),
        home_lags=(0, 1, 2, 3, 6, 12, 24, 48, 72, 96, 120, 132),
        lower=(
            Contact("sunspot micro-spin 3m", home, 3.0, 3),
            Contact("sunspot micro-spin 11m", home, 11.0, 11),
        ),
        upper=(Contact("sunspot slow envelope", home, 264.0, 132),),
    )


def build_enso() -> System:
    from enso_combined_horizon_feeder import load_dmi
    from enso_pdo_feeder_test import load_nino, load_pdo, load_soi, load_wwv

    west_data = load_wwv("wwv_west.dat")
    east_data = load_wwv("wwv_east.dat")
    nino = load_nino("nino34_long_anom.csv")
    soi_data = load_soi("soi.data")
    pdo = load_pdo("../../../../PDO_NOAA/ersst.v5.pdo.dat")
    dmi = load_dmi("../../../../IOD_NOAA/dmi.had.long.data")
    keys = sorted(set(west_data) & set(east_data) & set(nino) & set(soi_data) & set(pdo) & set(dmi))
    home = np.asarray([nino[key] for key in keys], dtype=float)
    west = np.asarray([west_data[key] for key in keys], dtype=float)
    east = np.asarray([east_data[key] for key in keys], dtype=float)
    soi = np.asarray([soi_data[key] for key in keys], dtype=float)
    pdo_values = np.asarray([pdo[key] for key in keys], dtype=float)
    iod = np.asarray([dmi[key] for key in keys], dtype=float)
    return System(
        name="ENSO NINO3.4",
        unit="month",
        home=home,
        home_period=48.0,
        horizons=(3, 6, 12, 18, 24),
        home_lags=(0, 1, 2, 3, 6, 9, 12, 18, 24, 36),
        lower=(
            Contact("SOI fast atmosphere", soi, 3.0, 3),
            Contact("WWV west feeder", west, 6.0, 6),
            Contact("WWV east feeder", east, 6.0, 6),
            Contact("IOD feeder", iod, 12.0, 6),
        ),
        upper=(Contact("PDO slow pressure", pdo_values, 60.0, 24),),
    )


def build_ecg() -> System:
    old_cwd = Path.cwd()
    try:
        os.chdir(HERE)
        import heart_info_exchange_R as heart

        rr, feed = heart.per_beat_series()
    finally:
        os.chdir(old_cwd)
    home = np.asarray(rr, dtype=float)
    return System(
        name="ECG RR interval slp01a",
        unit="beat",
        home=home,
        home_period=8.0,
        horizons=(1, 3, 5, 8, 13),
        home_lags=(0, 1, 2, 3, 4, 5, 8, 13),
        lower=(
            Contact("BP fast feeder", np.asarray(feed["BP"], dtype=float), 1.0, 8),
            Contact("Respiration feeder", np.asarray(feed["Resp"], dtype=float), 4.0, 8),
        ),
        upper=(Contact("EEG slow pressure", np.asarray(feed["EEG"], dtype=float), 13.0, 13),),
    )


def main() -> None:
    systems = (build_solar(), build_enso(), build_ecg())
    payload = {
        "phi": PHI,
        "equation": (
            "roll=(phi^-1*lower_torque + phi^-2*own_spin + phi^-3*wobble "
            "+ phi^-2*terrain_slope - phi^-2*upper_pressure) "
            "/ (1 + ridge_pressure + abs(upper_pressure)/phi)"
        ),
        "systems": {},
    }
    for system in systems:
        print(f"\n## {system.name}")
        payload["systems"][system.name] = {
            "adapter": {
                "unit": system.unit,
                "home_period": system.home_period,
                "lower": [asdict(contact) | {"values": "<raw causal series>"} for contact in system.lower],
                "upper": [asdict(contact) | {"values": "<raw causal series>"} for contact in system.upper],
            },
            "evaluation": evaluate(system),
        }
        horizons = payload["systems"][system.name]["evaluation"]["horizons"]
        for horizon, scores in horizons.items():
            print(f"{horizon:>4}{system.unit[0]} ", end="")
            for model in ("persistence", "ara_fixed_roll", "ara_roll_readout", "home_ar", "home_plus_ara"):
                score = scores[model]
                print(f"{model}={score['corr']:+.3f}/{score['mae']:.3f} ", end="")
            print()
    output = HERE / "ara_unified_layered_framework_result.json"
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nWrote {output}")


if __name__ == "__main__":
    main()
