"""Ablate simple retained-spin recycling against the 2-phi landmark refinement.

Both models use the same strict-causal local recycling proxy:

    rho_t = abs(corr(recent trailing block, one-period-earlier trailing block))

The proxy is interpreted in two ways:

    simple retention:
        retention = rho

    repeated recycling:
        B = 2 - phi
        effective_loss = B * (1 - rho) / (1 - rho * B)
        retention = 1 - effective_loss

The second expression is a candidate repeated-pass interpretation of the
bedrock landmark.  It is not assumed to be true; this script tests whether it
improves held-out forecasts.  All state at origin t uses samples <= t.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import ara_unified_layered_framework_test as base
import ara_vector_pose_energy_ratio_test as pose

HERE = Path(__file__).resolve().parent
PHI = base.PHI
BEDROCK_SHED = 2.0 - PHI


def batch_unit(values: np.ndarray) -> np.ndarray:
    lengths = np.linalg.norm(values, axis=1)
    lengths[lengths < 1e-12] = 1.0
    return values / lengths[:, None]


def terrain_batch(values: np.ndarray, depth: int = 5) -> tuple[np.ndarray, np.ndarray]:
    x = np.clip(values, 0.0, 2.0)
    slope = np.zeros_like(x)
    ridge = np.zeros_like(x)
    for level in range(depth):
        cells = 2**level
        width = 2.0 / cells
        cell = np.minimum(cells - 1, (x / width).astype(int))
        lo = cell * width
        hi = lo + width
        left_phi = lo + width / PHI
        right_phi = hi - width / PHI
        target = np.where(np.abs(x - left_phi) <= np.abs(x - right_phi), left_phi, right_phi)
        weight = PHI ** (-(level + 1))
        slope += weight * (target - x) / width
        edge_distance = np.minimum(x - lo, hi - x) / width
        ridge += weight * (1.0 - 2.0 * edge_distance)
    return slope, np.maximum(0.0, ridge)


def terrain_tangent_batch(points: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    space_ara = 1.0 + points @ pose.SPACE_AXIS
    time_ara = 1.0 + points @ pose.TIME_AXIS
    space_slope, space_ridge = terrain_batch(space_ara)
    time_slope, time_ridge = terrain_batch(time_ara)
    space_grad = batch_unit(pose.SPACE_AXIS[None, :] - (points @ pose.SPACE_AXIS)[:, None] * points)
    time_grad = batch_unit(pose.TIME_AXIS[None, :] - (points @ pose.TIME_AXIS)[:, None] * points)
    tangent = space_slope[:, None] * space_grad + (time_slope / PHI)[:, None] * time_grad
    ridge = space_ridge + time_ridge / PHI
    return tangent, ridge, space_ara, time_ara


def retention_from_proxy(rho: np.ndarray, mode: str) -> np.ndarray:
    rho = np.clip(np.nan_to_num(rho, nan=0.5), 0.0, 1.0)
    if mode == "simple":
        return rho
    if mode == "repeated":
        effective_loss = BEDROCK_SHED * (1.0 - rho) / (1.0 - rho * BEDROCK_SHED)
        return 1.0 - effective_loss
    raise ValueError(f"unknown retention mode: {mode}")


def pose_trajectories(
    system: base.System,
    mode: str,
) -> tuple[np.ndarray, dict[int, np.ndarray], dict[int, np.ndarray], np.ndarray, np.ndarray]:
    cutoff = int(len(system.home) * 0.60)
    state = base.layer_state(system, cutoff)
    phase = pose.causal_phase(state["home_z"], system.home_period)
    rho = pose.trailing_recycling(state["home_z"], system.home_period)
    start = max(
        max(system.home_lags),
        int(round(system.home_period * 1.5)),
        *(contact.window + 2 for contact in system.lower + system.upper),
    )
    origins = np.arange(start, len(system.home))
    ara = state["ara"][origins]
    longitude = phase[origins]
    z = np.clip(ara - 1.0, -1.0, 1.0)
    radius = np.sqrt(np.maximum(0.0, 1.0 - z * z))
    points = np.column_stack([radius * np.cos(longitude), radius * np.sin(longitude), z])

    rho_at_origin = rho[origins]
    retention = retention_from_proxy(rho_at_origin, mode)
    per_step_retention = np.maximum(1e-6, retention) ** (1.0 / system.home_period)
    forward = (PHI**-1) * state["lower_torque"][origins]
    lateral = (PHI**-3) * state["contact_wobble"][origins]
    twist = (PHI**-2) * (
        retention * np.nan_to_num(state["own_spin"][origins]) - state["upper_pressure"][origins]
    )
    distance = np.zeros(len(origins))
    packets: dict[int, np.ndarray] = {}
    ara_by_horizon: dict[int, np.ndarray] = {}
    wanted = set(system.horizons)
    for step in range(1, max(system.horizons) + 1):
        terrain, ridge, _, _ = terrain_tangent_batch(points)
        east = np.cross(np.broadcast_to(pose.SPACE_AXIS, points.shape), points)
        weak = np.linalg.norm(east, axis=1) < 1e-10
        east[weak] = np.asarray([1.0, 0.0, 0.0])
        east = batch_unit(east)
        north = batch_unit(np.cross(points, east))
        direction = (
            (forward * np.cos(twist) - lateral * np.sin(twist))[:, None] * north
            + (forward * np.sin(twist) + lateral * np.cos(twist))[:, None] * east
        )
        brake = 1.0 + ridge + np.abs(state["upper_pressure"][origins]) / PHI
        tangent = direction / brake[:, None] + (PHI**-2) * terrain
        angle = pose.ANGLE_STEP * np.tanh(np.linalg.norm(tangent, axis=1) / 4.0)
        points = batch_unit(np.cos(angle)[:, None] * points + np.sin(angle)[:, None] * batch_unit(tangent))
        distance += angle
        forward *= per_step_retention
        lateral *= per_step_retention
        if step in wanted:
            _, ridge, space_ara, time_ara = terrain_tangent_batch(points)
            packets[step] = np.column_stack(
                [
                    points,
                    space_ara,
                    time_ara,
                    ridge,
                    distance,
                    rho_at_origin,
                    retention,
                ]
            )
            ara_by_horizon[step] = space_ara.copy()
    return origins, packets, ara_by_horizon, rho_at_origin, retention


def evaluate_mode(system: base.System, mode: str) -> dict:
    cutoff = int(len(system.home) * 0.60)
    origins, packets, ara_by_horizon, rho, retention = pose_trajectories(system, mode)
    result = {
        "mean_local_recycling_proxy": float(np.nanmean(rho)),
        "mean_effective_retention": float(np.nanmean(retention)),
        "horizons": {},
    }
    for horizon in system.horizons:
        valid = origins + horizon < len(system.home)
        train = valid & (origins + horizon < cutoff)
        test = valid & (origins >= cutoff)
        train_origins = origins[train]
        test_origins = origins[test]
        train_target = system.home[train_origins + horizon]
        test_target = system.home[test_origins + horizon]
        train_current = system.home[train_origins]
        test_current = system.home[test_origins]
        train_delta = train_target - train_current
        pose_train = packets[horizon][train]
        pose_test = packets[horizon][test]
        direct_pred = pose.inverse_ara(ara_by_horizon[horizon][test], system.home, cutoff)
        pose_pred = test_current + base.ridge_readout(pose_train, train_delta, pose_test)
        result["horizons"][str(horizon)] = {
            "direct_pose": base.metrics(test_target, direct_pred, test_current),
            "pose_readout": base.metrics(test_target, pose_pred, test_current),
        }
    return result


def main() -> None:
    payload = {
        "phi": PHI,
        "bedrock_one_pass_shed": BEDROCK_SHED,
        "repeated_equation": "effective_loss=B*(1-rho)/(1-rho*B); retention=1-effective_loss",
        "systems": {},
    }
    for system in (base.build_solar(), base.build_enso(), base.build_ecg()):
        print(f"\n## {system.name}")
        system_result = {}
        for mode in ("simple", "repeated"):
            scores = evaluate_mode(system, mode)
            system_result[mode] = scores
            print(
                f"{mode:>8} proxy={scores['mean_local_recycling_proxy']:.3f} "
                f"retention={scores['mean_effective_retention']:.3f}"
            )
            for horizon, row in scores["horizons"].items():
                direct = row["direct_pose"]
                readout = row["pose_readout"]
                print(
                    f"  {horizon:>4}{system.unit[0]} "
                    f"direct={direct['corr']:+.3f}/{direct['mae']:.3f}/{direct['turn']:.3f} "
                    f"readout={readout['corr']:+.3f}/{readout['mae']:.3f}/{readout['turn']:.3f}"
                )
        payload["systems"][system.name] = system_result
    output = HERE / "ara_recycling_landmark_ablation_result.json"
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nWrote {output}")


if __name__ == "__main__":
    main()
