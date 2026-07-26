#!/usr/bin/env python3
"""Outcome-blind ARA diameter selection for Q20 Willow detector records."""

from __future__ import annotations

import hashlib
import json
import pathlib
from dataclasses import dataclass

import numpy as np


ROOT = pathlib.Path(__file__).parent
SOURCE_ROOT = ROOT / "public_data" / "q20_willow_105q" / "d5_at_q4_7"
OUTPUT_JSON = ROOT / "Q20_WILLOW_ARA_GEOMETRY_CALIBRATION.json"
OUTPUT_CSV = ROOT / "Q20_WILLOW_ARA_GEOMETRY_CALIBRATION.csv"
DEVELOPMENT_ROUNDS = "r13"
AXES = ("x", "y", "t")
PAIRS = ((0, 1), (0, 2), (1, 2))


@dataclass(frozen=True)
class DevelopmentData:
    basis: str
    rounds: int
    shots: int
    detectors: np.ndarray
    coordinates: np.ndarray
    source_hashes: dict[str, str]


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_detector_coordinates(path: pathlib.Path) -> np.ndarray:
    coordinates = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("DETECTOR("):
            continue
        raw = line.split("(", 1)[1].split(")", 1)[0]
        values = [float(value) for value in raw.split(",")]
        if len(values) < 3:
            raise ValueError(f"Detector lacks x/y/t coordinates: {line}")
        coordinates.append(values[:3])
    return np.asarray(coordinates, dtype=np.float64)


def load_development(basis: str) -> DevelopmentData:
    path = SOURCE_ROOT / basis / DEVELOPMENT_ROUNDS
    metadata_path = path / "metadata.json"
    circuit_path = path / "circuit_ideal.stim"
    detector_path = path / "detection_events.b8"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    shots = int(metadata["shots"])
    rounds = int(metadata["rounds"])
    coordinates = parse_detector_coordinates(circuit_path)
    detector_count = coordinates.shape[0]
    bytes_per_shot = (detector_count + 7) // 8
    packed = np.fromfile(detector_path, dtype=np.uint8)
    if packed.size != shots * bytes_per_shot:
        raise ValueError(
            f"{basis}: {packed.size} bytes do not match "
            f"{shots} shots x {bytes_per_shot} bytes."
        )
    packed = packed.reshape(shots, bytes_per_shot)
    detectors = np.unpackbits(packed, axis=1, bitorder="little")[:, :detector_count]
    if detector_count != 24 * rounds:
        raise ValueError(
            f"{basis}: expected 24 detectors per round, found "
            f"{detector_count}/{rounds}."
        )
    return DevelopmentData(
        basis=basis,
        rounds=rounds,
        shots=shots,
        detectors=detectors.astype(np.float64),
        coordinates=coordinates,
        source_hashes={
            "metadata.json": sha256(metadata_path),
            "circuit_ideal.stim": sha256(circuit_path),
            "detection_events.b8": sha256(detector_path),
        },
    )


def normalize_axis(coordinates: np.ndarray, axis: int) -> np.ndarray:
    values = coordinates[:, axis]
    span = float(values.max() - values.min())
    if span <= 0:
        raise ValueError(f"Axis {AXES[axis]} has no span.")
    return 2.0 * (values - values.min()) / span - 1.0


def relation_coordinates(
    detectors: np.ndarray, coordinates: np.ndarray, axis_a: int, axis_b: int
) -> tuple[np.ndarray, np.ndarray]:
    first = normalize_axis(coordinates, axis_a)
    second = normalize_axis(coordinates, axis_b)
    first_a = (1.0 - first) / 2.0
    first_b = (1.0 + first) / 2.0
    second_a = (1.0 - second) / 2.0
    second_b = (1.0 + second) / 2.0
    child_weights = np.column_stack(
        (
            detectors @ (first_a * second_a),
            detectors @ (first_a * second_b),
            detectors @ (first_b * second_a),
            detectors @ (first_b * second_b),
        )
    )
    totals = child_weights.sum(axis=1, keepdims=True)
    empty = totals[:, 0] == 0
    totals[empty] = 1.0
    child_weights /= totals
    child_weights[empty] = 0.25
    parent_first = 2.0 * (child_weights[:, 2] + child_weights[:, 3])
    parent_second = 2.0 * (child_weights[:, 1] + child_weights[:, 3])
    relation = 2.0 * (child_weights[:, 1] + child_weights[:, 2])
    coordinates_ara = np.column_stack((parent_first, parent_second, relation))
    return coordinates_ara, child_weights


def main() -> None:
    datasets = [load_development("X"), load_development("Z")]
    rows = []
    summaries: dict[str, dict] = {}
    for data in datasets:
        summaries[data.basis] = {
            "rounds": data.rounds,
            "shots": data.shots,
            "detector_count": int(data.detectors.shape[1]),
            "mean_detection_events_per_shot": float(data.detectors.sum(axis=1).mean()),
            "zero_event_fraction": float(
                np.mean(data.detectors.sum(axis=1) == 0)
            ),
            "source_hashes": data.source_hashes,
            "axis_pairs": {},
        }
        for axis_a, axis_b in PAIRS:
            ara, children = relation_coordinates(
                data.detectors, data.coordinates, axis_a, axis_b
            )
            pair = AXES[axis_a] + AXES[axis_b]
            result = {
                "parent_a_mean": float(ara[:, 0].mean()),
                "parent_a_sd": float(ara[:, 0].std()),
                "parent_b_mean": float(ara[:, 1].mean()),
                "parent_b_sd": float(ara[:, 1].std()),
                "relation_mean": float(ara[:, 2].mean()),
                "relation_sd": float(ara[:, 2].std()),
                "child_means": [float(value) for value in children.mean(axis=0)],
            }
            summaries[data.basis]["axis_pairs"][pair] = result
            rows.append(
                (
                    data.basis,
                    pair,
                    result["parent_a_mean"],
                    result["parent_a_sd"],
                    result["parent_b_mean"],
                    result["parent_b_sd"],
                    result["relation_mean"],
                    result["relation_sd"],
                )
            )

    pooled_relation_sd = {}
    for axis_a, axis_b in PAIRS:
        pair = AXES[axis_a] + AXES[axis_b]
        pooled = []
        for data in datasets:
            ara, _ = relation_coordinates(
                data.detectors, data.coordinates, axis_a, axis_b
            )
            pooled.append(ara[:, 2])
        pooled_relation_sd[pair] = float(np.concatenate(pooled).std())
    selected_pair = max(pooled_relation_sd, key=pooled_relation_sd.get)

    result = {
        "claim": "Q20-WILLOW-ARA-GEOMETRY-v1",
        "created": "2026-07-26",
        "outcome_blind": True,
        "outcome_files_read": [],
        "source_doi": "10.5281/zenodo.13273331",
        "source_archive": "google_105Q_surface_code_d3_d5_d7.zip",
        "development_patch": "d5_at_q4_7",
        "development_rounds": DEVELOPMENT_ROUNDS,
        "selection_rule": (
            "Choose the physical diameter pair with the largest pooled "
            "development standard deviation of the ARA crossed-versus-aligned "
            "relation coordinate. No observable-flip labels enter selection."
        ),
        "axis_pair_relation_sd_pooled": pooled_relation_sd,
        "selected_axis_pair": selected_pair,
        "datasets": summaries,
    }
    OUTPUT_JSON.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    header = (
        "basis,axis_pair,parent_a_mean,parent_a_sd,parent_b_mean,parent_b_sd,"
        "relation_mean,relation_sd\n"
    )
    lines = [header]
    lines.extend(
        ",".join(
            (basis, pair)
            + tuple(f"{value:.12f}" for value in numeric)
        )
        + "\n"
        for basis, pair, *numeric in rows
    )
    OUTPUT_CSV.write_text("".join(lines), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
