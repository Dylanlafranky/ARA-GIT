from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN6_NATIVE_ARA_CIRCUMFERENCE_PROTOCOL.md"
PN4_PATHS = HERE / "PN4_DIRECT_SIEVE_STATE_PATHS.csv"
PN5_PATHS = HERE / "PN5_MULTIPLICATIVE_RUNG_PATHS.csv"
PACKET = HERE / "PN6_NATIVE_ARA_FROZEN_PREDICTIONS.json"
MANIFEST = HERE / "PN6_NATIVE_ARA_FREEZE_MANIFEST.json"
TARGET_LOW = 100_000_000_000
TARGET_HIGH = 101_000_000_000
CELLS = 24


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def read_sources() -> dict[str, dict[str, np.ndarray]]:
    rows4 = list(csv.DictReader(PN4_PATHS.open("r", encoding="utf-8", newline="")))
    rows5 = list(csv.DictReader(PN5_PATHS.open("r", encoding="utf-8", newline="")))
    sources: dict[str, dict[str, np.ndarray]] = {}
    for rung in ("r7", "r8", "r9"):
        rows = [row for row in rows4 if row["rung"] == rung]
        if len(rows) != CELLS:
            raise AssertionError(f"Expected {CELLS} rows for {rung}, found {len(rows)}")
        sources[rung] = {
            "candidate": np.array([float(row["candidate_survival"]) for row in rows]),
            "edge": np.array([float(row["edge_survival"]) for row in rows]),
            "j": np.array([float(row["coupling_j"]) for row in rows]),
        }
    if len(rows5) != CELLS:
        raise AssertionError(f"Expected {CELLS} R10 rows, found {len(rows5)}")
    sources["r10"] = {
        "candidate": np.array([float(row["candidate_survival"]) for row in rows5]),
        "edge": np.array([float(row["edge_survival"]) for row in rows5]),
        "j": np.array([float(row["edge_j"]) for row in rows5]),
    }
    return sources


def phase(survival: np.ndarray) -> np.ndarray:
    return np.arccos(np.clip(2.0 * survival - 1.0, -1.0, 1.0))


def fitted_rho(delta_previous: np.ndarray, delta_current: np.ndarray) -> float:
    denominator = float(delta_previous @ delta_previous)
    if denominator <= 0.0:
        raise AssertionError("Zero phase-increment denominator")
    return float(delta_previous @ delta_current / denominator)


def survival_from_phase(theta: np.ndarray) -> np.ndarray:
    return (1.0 + np.cos(theta)) / 2.0


def path_validity(values: np.ndarray) -> dict[str, Any]:
    return {
        "finite": bool(np.all(np.isfinite(values))),
        "within_unit_interval": bool(np.all((values > 0.0) & (values < 1.0))),
        "nonincreasing": bool(np.all(np.diff(values) <= 0.0)),
        "minimum": float(values.min()),
        "maximum": float(values.max()),
    }


def ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): ready(item) for key, item in value.items()}
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    return value


def main() -> None:
    source = read_sources()
    theta = {
        rung: {entity: phase(values) for entity, values in paths.items() if entity in ("candidate", "edge")}
        for rung, paths in source.items()
    }
    delta_9 = np.concatenate([
        theta["r9"][entity] - theta["r8"][entity]
        for entity in ("candidate", "edge")
    ])
    delta_10 = np.concatenate([
        theta["r10"][entity] - theta["r9"][entity]
        for entity in ("candidate", "edge")
    ])
    rho_shared = fitted_rho(delta_9, delta_10)
    rho_candidate = fitted_rho(theta["r9"]["candidate"] - theta["r8"]["candidate"], theta["r10"]["candidate"] - theta["r9"]["candidate"])
    rho_edge = fitted_rho(theta["r9"]["edge"] - theta["r8"]["edge"], theta["r10"]["edge"] - theta["r9"]["edge"])

    back_delta_8 = np.concatenate([
        theta["r8"][entity] - theta["r7"][entity]
        for entity in ("candidate", "edge")
    ])
    back_delta_9 = np.concatenate([
        theta["r9"][entity] - theta["r8"][entity]
        for entity in ("candidate", "edge")
    ])
    rho_backtest = fitted_rho(back_delta_8, back_delta_9)
    backtest: dict[str, Any] = {"shared_rho_r7_r9": rho_backtest}
    for entity in ("candidate", "edge"):
        predicted_theta = theta["r9"][entity] + rho_backtest * (theta["r9"][entity] - theta["r8"][entity])
        predicted_survival = survival_from_phase(predicted_theta)
        backtest[entity] = {
            "phase_rmse": float(np.sqrt(np.mean((predicted_theta - theta["r10"][entity]) ** 2))),
            "survival_rmse": float(np.sqrt(np.mean((predicted_survival - source["r10"][entity]) ** 2))),
            "terminal_absolute_relative_error": float(abs(predicted_survival[-1] - source["r10"][entity][-1]) / source["r10"][entity][-1]),
        }

    predictions: dict[str, dict[str, np.ndarray]] = {"candidate": {}, "edge": {}}
    for entity in ("candidate", "edge"):
        s9 = source["r9"][entity]
        s10 = source["r10"][entity]
        t9 = theta["r9"][entity]
        t10 = theta["r10"][entity]
        entity_rho = rho_candidate if entity == "candidate" else rho_edge
        predictions[entity] = {
            "home_r10": s10.copy(),
            "direct_log_rung": s10 * s10 / s9,
            "circle_secant_rho1": survival_from_phase(t10 + (t10 - t9)),
            "circle_shared_rho_primary": survival_from_phase(t10 + rho_shared * (t10 - t9)),
            f"circle_{entity}_rho_sensitivity": survival_from_phase(t10 + entity_rho * (t10 - t9)),
        }

    j_prediction = source["r10"]["j"] + rho_shared * (source["r10"]["j"] - source["r9"]["j"])
    predictions["edge"]["circle_candidate_plus_j_secondary"] = predictions["candidate"]["circle_shared_rho_primary"] ** 2 * np.exp(j_prediction)
    route_rmse = float(np.sqrt(np.mean((
        predictions["edge"]["circle_shared_rho_primary"]
        - predictions["edge"]["circle_candidate_plus_j_secondary"]
    ) ** 2)))
    validity = {
        f"{entity}__{model}": path_validity(values)
        for entity, models in predictions.items()
        for model, values in models.items()
    }
    primary_valid = all(
        all(validity[f"{entity}__circle_shared_rho_primary"][key] for key in ("finite", "within_unit_interval", "nonincreasing"))
        for entity in ("candidate", "edge")
    )
    if not primary_valid:
        raise AssertionError("Native primary path is invalid before target freeze")

    packet = {
        "test_id": "PN6/NATIVE-ARA-CIRCUMFERENCE/FRESH-R11-v1",
        "freeze_state": "NATIVE ARA PREDICTIONS WRITTEN BEFORE R11 TARGET CONSTRUCTION",
        "target": {"low": TARGET_LOW, "high": TARGET_HIGH, "width": TARGET_HIGH - TARGET_LOW, "cells": CELLS},
        "native_model_quarantine": {
            "uses_independent_sieve_product": False,
            "uses_pnt_or_mertens": False,
            "uses_buchstab": False,
            "uses_hardy_littlewood": False,
            "uses_fourier_svd_or_nmf": False,
            "uses_future_target_labels": False,
        },
        "source_hashes": {
            PROTOCOL.name: sha256(PROTOCOL),
            PN4_PATHS.name: sha256(PN4_PATHS),
            PN5_PATHS.name: sha256(PN5_PATHS),
            Path(__file__).name: sha256(Path(__file__)),
        },
        "progress": (np.arange(CELLS, dtype=float) + 1.0) / CELLS,
        "source_survival": source,
        "source_phase": theta,
        "fitted_parameters": {
            "rho_shared": rho_shared,
            "rho_candidate_sensitivity": rho_candidate,
            "rho_edge_sensitivity": rho_edge,
            "j_prediction": j_prediction,
            "pretarget_pair_route_rmse": route_rmse,
        },
        "development_backtest": backtest,
        "predictions": predictions,
        "path_validity": validity,
    }
    PACKET.write_text(json.dumps(ready(packet), indent=2) + "\n", encoding="utf-8")
    manifest = {
        "test_id": packet["test_id"],
        "freeze_state": packet["freeze_state"],
        "files": {
            path.name: sha256(path)
            for path in (PROTOCOL, PN4_PATHS, PN5_PATHS, Path(__file__), PACKET)
        },
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "freeze_state": packet["freeze_state"],
        "target": packet["target"],
        "rho_shared": rho_shared,
        "rho_candidate_sensitivity": rho_candidate,
        "rho_edge_sensitivity": rho_edge,
        "development_backtest": backtest,
        "pretarget_pair_route_rmse": route_rmse,
        "prediction_packet_sha256": manifest["files"][PACKET.name],
    }, indent=2))


if __name__ == "__main__":
    main()
