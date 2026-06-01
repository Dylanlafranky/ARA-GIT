"""Strict-causal 3D ARA pose advance with local recycling.

This extends ara_unified_layered_framework_test.py without replacing it.
The scalar roll is split into a 3D local motion:

    forward = phi^-1 * lower_torque
    lateral = phi^-3 * contact_wobble
    twist   = phi^-2 * (retained_own_spin - upper_pressure)

The measured sphere is advanced on a unit surface.  Its terrain is read on:

    space axis = [0, 0, 1]
    time axis  = rotate_x(36 degrees) @ space_axis

where phi = 2 cos(36 degrees).  Recursive ARA terrain is filled at every
coordinate: each depth pulls toward the nearest in-bounds phi valley and
contributes phi^-(depth+1).

EnergyRatio is used conservatively.  The system's local recycling is estimated
from trailing, origin-safe autocorrelation one declared home period apart.  It
controls only carried own-spin.  It is not set to 2-phi: the EnergyRatio notes
explicitly reject 2-phi as a universal measured loss constant.

The direct pose forecast is fully deterministic after a raw origin sample:

    pose_(t+h) = integrate(pose_t, forward_t, lateral_t, twist_t, recycling_t)
    yhat_(t+h) = inverse_ARA(read_space_axis(pose_(t+h)))

Train-only pose readouts are also scored as diagnostics.  They ask whether the
arrived coordinate exposes useful state; they are not the direct formula.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import ara_unified_layered_framework_test as base

HERE = Path(__file__).resolve().parent
PHI = base.PHI
SHEAR = math.pi / 5.0
SPACE_AXIS = np.asarray([0.0, 0.0, 1.0])
TIME_AXIS = np.asarray([0.0, -math.sin(SHEAR), math.cos(SHEAR)])
ANGLE_STEP = 0.12


def unit(x: np.ndarray) -> np.ndarray:
    length = float(np.linalg.norm(x))
    if length < 1e-12:
        return np.zeros(3)
    return x / length


def trailing_recycling(x: np.ndarray, period: float) -> np.ndarray:
    """Origin-safe local cycle memory: abs corr(recent block, period-ago block)."""
    lag = max(1, int(round(period)))
    window = max(8, int(round(period / 2.0)))
    result = np.full(len(x), np.nan)
    for t in range(lag + window - 1, len(x)):
        recent = x[t - window + 1 : t + 1]
        earlier = x[t - lag - window + 1 : t - lag + 1]
        if not np.all(np.isfinite(recent)) or not np.all(np.isfinite(earlier)):
            continue
        a = recent - np.mean(recent)
        b = earlier - np.mean(earlier)
        denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
        if denominator > 1e-12:
            result[t] = abs(float(np.dot(a, b) / denominator))
    return result


def causal_phase(home_z: np.ndarray, period: float) -> np.ndarray:
    """Causal oscillator address from current level and one-step velocity."""
    velocity = home_z - base.shifted(home_z, 1)
    scaled_velocity = velocity * period / (2.0 * math.pi)
    return np.arctan2(home_z, scaled_velocity)


def pose_from_ara_phase(ara: float, longitude: float) -> np.ndarray:
    z = float(np.clip(ara - 1.0, -1.0, 1.0))
    radius = math.sqrt(max(0.0, 1.0 - z * z))
    return np.asarray([radius * math.cos(longitude), radius * math.sin(longitude), z])


def local_basis(pose: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    east = np.cross(SPACE_AXIS, pose)
    if np.linalg.norm(east) < 1e-10:
        east = np.asarray([1.0, 0.0, 0.0])
    east = unit(east)
    north = unit(np.cross(pose, east))
    return north, east


def recursive_terrain_scalar(value: float, depth: int = 5) -> tuple[float, float]:
    """Scalar equivalent of base.recursive_terrain for the pose-integration hot loop."""
    x = float(np.clip(value, 0.0, 2.0))
    slope = 0.0
    ridge = 0.0
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
        slope += weight * (target - x) / width
        edge_distance = min(x - lo, hi - x) / width
        ridge += weight * (1.0 - 2.0 * edge_distance)
    return slope, max(0.0, ridge)


def terrain_tangent(pose: np.ndarray) -> tuple[np.ndarray, float, float, float, float]:
    space_ara = 1.0 + float(np.dot(pose, SPACE_AXIS))
    time_ara = 1.0 + float(np.dot(pose, TIME_AXIS))
    space_slope, space_ridge = recursive_terrain_scalar(space_ara)
    time_slope, time_ridge = recursive_terrain_scalar(time_ara)
    space_grad = unit(SPACE_AXIS - np.dot(pose, SPACE_AXIS) * pose)
    time_grad = unit(TIME_AXIS - np.dot(pose, TIME_AXIS) * pose)
    tangent = space_slope * space_grad + time_slope * time_grad / PHI
    ridge = space_ridge + time_ridge / PHI
    return tangent, ridge, space_ara, time_ara, space_slope


def rotate_surface(pose: np.ndarray, tangent: np.ndarray, angle: float) -> np.ndarray:
    direction = unit(tangent)
    if np.linalg.norm(direction) < 1e-12 or abs(angle) < 1e-12:
        return pose
    return unit(math.cos(angle) * pose + math.sin(angle) * direction)


def advance_pose(
    state: dict[str, np.ndarray],
    phase: np.ndarray,
    recycling: np.ndarray,
    origin: int,
    horizon: int,
    home_period: float,
) -> dict[str, float]:
    pose = pose_from_ara_phase(float(state["ara"][origin]), float(phase[origin]))
    retention = float(recycling[origin]) if np.isfinite(recycling[origin]) else 0.5
    per_step_retention = max(1e-6, retention) ** (1.0 / home_period)
    forward = (PHI**-1) * float(state["lower_torque"][origin])
    lateral = (PHI**-3) * float(state["contact_wobble"][origin])
    twist = (PHI**-2) * (
        retention * float(state["own_spin"][origin]) - float(state["upper_pressure"][origin])
    )
    cumulative = 0.0
    for _ in range(horizon):
        terrain, ridge, _, _, _ = terrain_tangent(pose)
        north, east = local_basis(pose)
        # Twist changes the direction of roll rather than the native amplitude.
        contact_direction = (
            (forward * math.cos(twist) - lateral * math.sin(twist)) * north
            + (forward * math.sin(twist) + lateral * math.cos(twist)) * east
        )
        brake = 1.0 + ridge + abs(float(state["upper_pressure"][origin])) / PHI
        tangent = contact_direction / brake + (PHI**-2) * terrain
        distance = ANGLE_STEP * math.tanh(float(np.linalg.norm(tangent)) / 4.0)
        pose = rotate_surface(pose, tangent, distance)
        cumulative += distance
        forward *= per_step_retention
        lateral *= per_step_retention
    _, ridge, space_ara, time_ara, slope = terrain_tangent(pose)
    return {
        "x": float(pose[0]),
        "y": float(pose[1]),
        "z": float(pose[2]),
        "space_ara": space_ara,
        "time_ara": time_ara,
        "ridge": ridge,
        "terrain_slope": slope,
        "distance": cumulative,
        "recycling": retention,
    }


def inverse_ara(ara: np.ndarray, home: np.ndarray, cutoff: int) -> np.ndarray:
    train = home[:cutoff]
    train = train[np.isfinite(train)]
    mean = float(np.mean(train))
    std = float(np.std(train))
    clipped = np.clip(ara - 1.0, -0.995, 0.995)
    return mean + std * 2.0 * np.arctanh(clipped)


def pose_matrix(
    state: dict[str, np.ndarray],
    phase: np.ndarray,
    recycling: np.ndarray,
    origins: np.ndarray,
    horizon: int,
    home_period: float,
) -> tuple[np.ndarray, np.ndarray]:
    packets = [advance_pose(state, phase, recycling, int(t), horizon, home_period) for t in origins]
    x = np.asarray(
        [
            [
                p["x"],
                p["y"],
                p["z"],
                p["space_ara"],
                p["time_ara"],
                p["ridge"],
                p["terrain_slope"],
                p["distance"],
                p["recycling"],
            ]
            for p in packets
        ],
        dtype=float,
    )
    ara = np.asarray([p["space_ara"] for p in packets], dtype=float)
    return x, ara


def evaluate(system: base.System) -> dict:
    n = len(system.home)
    cutoff = int(n * 0.60)
    state = base.layer_state(system, cutoff)
    phase = causal_phase(state["home_z"], system.home_period)
    recycling = trailing_recycling(state["home_z"], system.home_period)
    start = max(
        max(system.home_lags),
        int(round(system.home_period * 1.5)),
        *(contact.window + 2 for contact in system.lower + system.upper),
    )
    result = {"cutoff_index": cutoff, "samples": n, "horizons": {}}
    for horizon in system.horizons:
        train_origins = np.arange(start, cutoff - horizon)
        test_origins = np.arange(cutoff, n - horizon)
        train_target = system.home[train_origins + horizon]
        test_target = system.home[test_origins + horizon]
        train_current = system.home[train_origins]
        test_current = system.home[test_origins]
        train_delta = train_target - train_current

        pose_train, _ = pose_matrix(state, phase, recycling, train_origins, horizon, system.home_period)
        pose_test, arrived_ara = pose_matrix(state, phase, recycling, test_origins, horizon, system.home_period)
        direct_pred = inverse_ara(arrived_ara, system.home, cutoff)
        pose_pred = test_current + base.ridge_readout(pose_train, train_delta, pose_test)

        home_train = np.asarray(
            [[system.home[t - lag] for lag in system.home_lags] for t in train_origins], dtype=float
        )
        home_test = np.asarray(
            [[system.home[t - lag] for lag in system.home_lags] for t in test_origins], dtype=float
        )
        home_pred = test_current + base.ridge_readout(home_train, train_delta, home_test)
        combined_train = np.column_stack([home_train, pose_train])
        combined_test = np.column_stack([home_test, pose_test])
        combined_pred = test_current + base.ridge_readout(combined_train, train_delta, combined_test)
        result["horizons"][str(horizon)] = {
            "persistence": base.metrics(test_target, test_current, test_current),
            "pose_direct": base.metrics(test_target, direct_pred, test_current),
            "pose_readout": base.metrics(test_target, pose_pred, test_current),
            "home_ar": base.metrics(test_target, home_pred, test_current),
            "home_plus_pose": base.metrics(test_target, combined_pred, test_current),
            "mean_test_recycling": float(np.nanmean(recycling[test_origins])),
        }
    return result


def main() -> None:
    systems = (base.build_solar(), base.build_enso(), base.build_ecg())
    payload = {
        "phi": PHI,
        "shear_degrees": 36.0,
        "angle_step": ANGLE_STEP,
        "equation": {
            "forward": "phi^-1 * lower_torque",
            "lateral": "phi^-3 * contact_wobble",
            "twist": "phi^-2 * (local_recycling * own_spin - upper_pressure)",
            "pose": "integrate surface roll; read ARA on z and rotate_x(36deg) axes",
        },
        "systems": {},
    }
    for system in systems:
        print(f"\n## {system.name}")
        scores = evaluate(system)
        payload["systems"][system.name] = scores
        for horizon, row in scores["horizons"].items():
            print(f"{horizon:>4}{system.unit[0]} ", end="")
            for model in ("persistence", "pose_direct", "pose_readout", "home_ar", "home_plus_pose"):
                score = row[model]
                print(f"{model}={score['corr']:+.3f}/{score['mae']:.3f}/{score['turn']:.3f} ", end="")
            print(f" recycle={row['mean_test_recycling']:.3f}")
    output = HERE / "ara_vector_pose_energy_ratio_result.json"
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nWrote {output}")


if __name__ == "__main__":
    main()
