"""Strict-causal joint ENSO sphere-topology direction test.

The earlier ARA pose prototype asked one NINO coordinate to summarize ENSO.
This test advances a small connected topology instead:

    NINO surface target
    SOI matched-rung partner
    WWV west/east faster lower feeders
    IOD feeder
    PDO slower upper constraint

Every node has its own ARA sphere pose and causal own-spin.  Three direct modes
are compared:

    independent: nodes roll without contact transfer
    same:        contacts pull in the same orientation
    parity:      touching layers roll in opposing orientation

The parity comparison directly tests the layered-sand claim.  Fixed graph
weights are phi-derived and declared below.  No future sample is used to
advance the graph.  Train-only readouts and raw VAR-like baselines are labeled
as diagnostics; direction accuracy is the primary score.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

import ara_recycling_landmark_ablation as batch
import ara_unified_layered_framework_test as base
import ara_vector_pose_energy_ratio_test as pose

HERE = Path(__file__).resolve().parent
PHI = base.PHI
TARGET_PERIOD = 48.0


@dataclass
class Node:
    name: str
    values: np.ndarray
    period: float
    role: str


@dataclass
class Edge:
    source: int
    target: int
    kind: str
    weight: float


def build_nodes() -> list[Node]:
    system = base.build_enso()
    return [
        Node("NINO3.4", system.home, 48.0, "measured surface"),
        Node("SOI", system.lower[0].values, 48.0, "matched-rung partner"),
        Node("WWV west", system.lower[1].values, 6.0, "faster lower feeder"),
        Node("WWV east", system.lower[2].values, 6.0, "faster lower feeder"),
        Node("IOD", system.lower[3].values, 12.0, "lower feeder"),
        Node("PDO", system.upper[0].values, 60.0, "slower upper constraint"),
    ]


EDGES = (
    Edge(1, 0, "matched pair SOI -> NINO", PHI**-1),
    Edge(0, 1, "matched pair NINO -> SOI", PHI**-1),
    Edge(2, 0, "lower WWV west -> NINO", PHI**-1),
    Edge(3, 0, "lower WWV east -> NINO", PHI**-1),
    Edge(4, 0, "lower IOD -> NINO", PHI**-2),
    Edge(5, 0, "upper PDO -> NINO", PHI**-2),
)


def initial_state(nodes: list[Node], cutoff: int, origins: np.ndarray) -> dict[str, np.ndarray]:
    points = []
    drives = []
    retentions = []
    standardized = []
    for node in nodes:
        z = base.standardize_from_training(node.values, cutoff)
        phase = pose.causal_phase(z, node.period)
        ara = 1.0 + np.tanh(z / 2.0)
        zz = np.clip(ara[origins] - 1.0, -1.0, 1.0)
        radius = np.sqrt(np.maximum(0.0, 1.0 - zz * zz))
        points.append(np.column_stack([radius * np.cos(phase[origins]), radius * np.sin(phase[origins]), zz]))
        velocity = np.nan_to_num(z - base.shifted(z, 1))
        rho = pose.trailing_recycling(z, node.period)
        retention = np.clip(np.nan_to_num(rho[origins], nan=0.5), 0.0, 1.0)
        frequency_gain = math.sqrt(TARGET_PERIOD / node.period)
        drives.append(frequency_gain * retention * velocity[origins])
        retentions.append(np.maximum(1e-6, retention) ** (1.0 / node.period))
        standardized.append(z)
    return {
        "points": np.stack(points, axis=1),
        "drives": np.stack(drives, axis=1),
        "retentions": np.stack(retentions, axis=1),
        "standardized": np.stack(standardized, axis=1),
    }


def topology_packets(nodes: list[Node], mode: str, origins: np.ndarray, horizons: tuple[int, ...]) -> dict[int, np.ndarray]:
    cutoff = int(len(nodes[0].values) * 0.60)
    state = initial_state(nodes, cutoff, origins)
    points = state["points"].copy()
    drives = state["drives"].copy()
    distance = np.zeros((len(origins), len(nodes)))
    wanted = set(horizons)
    packets: dict[int, np.ndarray] = {}
    for step in range(1, max(horizons) + 1):
        flat = points.reshape(-1, 3)
        terrain, ridge, _, _ = batch.terrain_tangent_batch(flat)
        terrain = terrain.reshape(points.shape)
        ridge = ridge.reshape(len(origins), len(nodes))
        east = np.cross(np.broadcast_to(pose.SPACE_AXIS, points.shape), points)
        weak = np.linalg.norm(east, axis=2) < 1e-10
        east[weak] = np.asarray([1.0, 0.0, 0.0])
        east = batch.batch_unit(east.reshape(-1, 3)).reshape(points.shape)
        north = batch.batch_unit(np.cross(points, east).reshape(-1, 3)).reshape(points.shape)
        tangent = drives[:, :, None] * north + (PHI**-2) * terrain

        if mode != "independent":
            sign = 1.0 if mode == "same" else -1.0
            for edge in EDGES:
                source = points[:, edge.source, :]
                target = points[:, edge.target, :]
                desired = sign * source
                projected = desired - np.sum(desired * target, axis=1)[:, None] * target
                tangent[:, edge.target, :] += edge.weight * projected

        # The slow upper PDO shell presses on the measured NINO sphere.
        pdo_pressure = np.abs(state["standardized"][origins, 5])
        brake = 1.0 + ridge
        brake[:, 0] += pdo_pressure / PHI
        tangent = tangent / brake[:, :, None]
        angle = pose.ANGLE_STEP * np.tanh(np.linalg.norm(tangent, axis=2) / 4.0)
        direction = batch.batch_unit(tangent.reshape(-1, 3)).reshape(points.shape)
        points = (
            np.cos(angle)[:, :, None] * points
            + np.sin(angle)[:, :, None] * direction
        )
        points = batch.batch_unit(points.reshape(-1, 3)).reshape(points.shape)
        distance += angle
        drives *= state["retentions"]
        if step in wanted:
            flat_points = points.reshape(len(origins), -1)
            ara = 1.0 + points[:, :, 2]
            edge_geometry = np.column_stack(
                [np.sum(points[:, edge.source, :] * points[:, edge.target, :], axis=1) for edge in EDGES]
            )
            packets[step] = np.column_stack([flat_points, ara, distance, edge_geometry])
    return packets


def raw_lag_matrix(nodes: list[Node], origins: np.ndarray, lags: tuple[int, ...]) -> np.ndarray:
    return np.asarray(
        [[node.values[t - lag] for node in nodes for lag in lags] for t in origins],
        dtype=float,
    )


def evaluate() -> dict:
    nodes = build_nodes()
    n = len(nodes[0].values)
    cutoff = int(n * 0.60)
    lags = (0, 1, 3, 6, 12)
    horizons = (1, 3, 6, 9, 12, 18, 24)
    start = max(lags) + 2
    origins = np.arange(start, n)
    packets = {mode: topology_packets(nodes, mode, origins, horizons) for mode in ("independent", "same", "parity")}
    result = {
        "cutoff_index": cutoff,
        "samples": n,
        "nodes": [{"name": node.name, "period": node.period, "role": node.role} for node in nodes],
        "edges": [edge.__dict__ for edge in EDGES],
        "horizons": {},
    }
    for horizon in horizons:
        valid = origins + horizon < n
        train = valid & (origins + horizon < cutoff)
        test = valid & (origins >= cutoff)
        train_origins = origins[train]
        test_origins = origins[test]
        train_target = nodes[0].values[train_origins + horizon]
        test_target = nodes[0].values[test_origins + horizon]
        train_current = nodes[0].values[train_origins]
        test_current = nodes[0].values[test_origins]
        train_delta = train_target - train_current

        raw_train = raw_lag_matrix(nodes, train_origins, lags)
        raw_test = raw_lag_matrix(nodes, test_origins, lags)
        home_train = raw_lag_matrix(nodes[:1], train_origins, lags)
        home_test = raw_lag_matrix(nodes[:1], test_origins, lags)
        home_pred = test_current + base.ridge_readout(home_train, train_delta, home_test)
        raw_pred = test_current + base.ridge_readout(raw_train, train_delta, raw_test)

        row = {
            "persistence": base.metrics(test_target, test_current, test_current),
            "home_ar": base.metrics(test_target, home_pred, test_current),
            "raw_topology_var": base.metrics(test_target, raw_pred, test_current),
        }
        for mode in ("independent", "same", "parity"):
            train_pose = packets[mode][horizon][train]
            test_pose = packets[mode][horizon][test]
            arrived_ara = 1.0 + packets[mode][horizon][test][:, 2]
            direct = pose.inverse_ara(arrived_ara, nodes[0].values, cutoff)
            readout = test_current + base.ridge_readout(train_pose, train_delta, test_pose)
            combined = test_current + base.ridge_readout(
                np.column_stack([raw_train, train_pose]),
                train_delta,
                np.column_stack([raw_test, test_pose]),
            )
            row[f"direct_{mode}"] = base.metrics(test_target, direct, test_current)
            row[f"pose_readout_{mode}"] = base.metrics(test_target, readout, test_current)
            row[f"var_plus_pose_{mode}"] = base.metrics(test_target, combined, test_current)
        result["horizons"][str(horizon)] = row
    return result


def main() -> None:
    result = evaluate()
    print("## Joint ENSO topology: held-out correlation / MAE / direction\n")
    for horizon, row in result["horizons"].items():
        print(f"{horizon:>3}m ", end="")
        for model in (
            "persistence",
            "home_ar",
            "raw_topology_var",
            "direct_independent",
            "direct_same",
            "direct_parity",
            "pose_readout_parity",
            "var_plus_pose_parity",
        ):
            score = row[model]
            print(f"{model}={score['corr']:+.3f}/{score['mae']:.3f}/{score['turn']:.3f} ", end="")
        print()
    output = HERE / "ara_joint_enso_topology_direction_result.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"\nWrote {output}")


if __name__ == "__main__":
    main()
