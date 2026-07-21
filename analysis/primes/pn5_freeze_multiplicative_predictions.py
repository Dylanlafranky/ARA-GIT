from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN5_MULTIPLICATIVE_RUNG_TRANSFER_PROTOCOL.md"
SOURCE_PATHS = HERE / "PN4_DIRECT_SIEVE_STATE_PATHS.csv"
PACKET = HERE / "PN5_FROZEN_PREDICTIONS.json"
MANIFEST = HERE / "PN5_FROZEN_PREDICTION_MANIFEST.json"

TARGET_LOW = 10_000_000_000
TARGET_HIGH = 10_100_000_000
CELLS = 24
EPS = 1e-12
GAMMA = 0.5772156649015329


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def primes_through(limit: int) -> np.ndarray:
    sieve = np.ones(limit + 1, dtype=bool)
    sieve[:2] = False
    for p in range(2, math.isqrt(limit) + 1):
        if sieve[p]:
            sieve[p * p :: p] = False
    return np.flatnonzero(sieve).astype(np.int64)


def target_gate_path() -> dict[str, np.ndarray | int]:
    gates = primes_through(math.isqrt(TARGET_HIGH - 1))
    gates = gates[gates > 29]
    qmax = int(gates[-1])
    progress = np.log(gates.astype(float) / 31.0) / math.log(qmax / 31.0)
    cell = np.minimum((progress * CELLS).astype(int), CELLS - 1)
    products = np.ones(CELLS, dtype=float)
    q_end = np.zeros(CELLS, dtype=np.int64)
    q_count = np.zeros(CELLS, dtype=np.int64)
    for j in range(CELLS):
        q = gates[cell == j]
        if len(q):
            products[j] = np.prod(1.0 - 1.0 / q.astype(float))
            q_end[j] = int(q[-1])
            q_count[j] = len(q)
        elif j:
            q_end[j] = q_end[j - 1]
        else:
            q_end[j] = 29
    return {
        "qmax": qmax,
        "progress": (np.arange(CELLS, dtype=float) + 1.0) / CELLS,
        "q_end": q_end,
        "q_count": q_count,
        "cell_product": products,
        "candidate_independent": np.cumprod(products),
    }


def buchstab(values: np.ndarray, step: float = 1e-4) -> np.ndarray:
    maximum = max(2.0, float(np.max(values))) + step
    size = int(math.ceil((maximum - 1.0) / step)) + 1
    u = 1.0 + np.arange(size, dtype=float) * step
    omega = np.empty(size, dtype=float)
    base_end = int(round(1.0 / step))
    omega[: base_end + 1] = 1.0 / u[: base_end + 1]
    g = np.ones(size, dtype=float)
    shift = base_end
    for i in range(base_end + 1, size):
        current_integrand = omega[i - shift]
        previous_integrand = omega[i - shift - 1]
        g[i] = g[i - 1] + 0.5 * step * (previous_integrand + current_integrand)
        omega[i] = g[i] / u[i]
    return np.interp(values, u, omega)


def source_rung(rung: str) -> dict[str, np.ndarray]:
    rows = [row for row in csv.DictReader(SOURCE_PATHS.open("r", encoding="utf-8", newline="")) if row["rung"] == rung]
    if len(rows) != CELLS:
        raise AssertionError(f"Expected {CELLS} {rung} rows, found {len(rows)}")
    return {
        key: np.array([float(row[key]) for row in rows], dtype=float)
        for key in ("candidate_survival", "candidate_independent", "edge_survival", "edge_independent", "coupling_j")
    }


def valid_path(values: np.ndarray) -> tuple[np.ndarray, int]:
    clipped = np.clip(values.astype(float), EPS, 1.0)
    fixed = np.minimum.accumulate(clipped)
    return fixed, int(np.count_nonzero(np.abs(fixed - values) > 1e-12))


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
    target = target_gate_path()
    r8 = source_rung("r8")
    r9 = source_rung("r9")
    independent = target["candidate_independent"]
    assert isinstance(independent, np.ndarray)
    edge_independent = independent**2
    k8 = np.log(r8["candidate_survival"] / r8["candidate_independent"])
    k9 = np.log(r9["candidate_survival"] / r9["candidate_independent"])
    j8 = r8["coupling_j"]
    j9 = r9["coupling_j"]

    midpoint = 0.5 * (TARGET_LOW + TARGET_HIGH)
    q_end = target["q_end"]
    assert isinstance(q_end, np.ndarray)
    u = np.log(midpoint) / np.log(q_end.astype(float))
    established_candidate = independent * math.exp(GAMMA) * buchstab(u)

    candidate_raw = {
        "independent_sieve": independent,
        "ara_additive_previous_rule": independent + (r9["candidate_survival"] - r9["candidate_independent"]),
        "ara_multiplicative_primary": independent * np.exp(k9),
        "ara_log_gradient_secondary": independent * np.exp(2.0 * k9 - k8),
        "buchstab_established": established_candidate,
    }
    candidate: dict[str, np.ndarray] = {}
    adjustments: dict[str, int] = {}
    for model, values in candidate_raw.items():
        candidate[model], adjustments[f"candidate__{model}"] = valid_path(values)

    edge_raw = {
        "independent_pair": edge_independent,
        "ara_additive_edge_previous_rule": edge_independent + (r9["edge_survival"] - r9["edge_independent"]),
        "ara_multiplicative_primary": candidate["ara_multiplicative_primary"] ** 2 * np.exp(j9),
        "ara_log_gradient_secondary": candidate["ara_log_gradient_secondary"] ** 2 * np.exp(2.0 * j9 - j8),
        "buchstab_squared": candidate["buchstab_established"] ** 2,
        "buchstab_plus_source_relation": candidate["buchstab_established"] ** 2 * np.exp(j9),
    }
    edge: dict[str, np.ndarray] = {}
    for model, values in edge_raw.items():
        edge[model], adjustments[f"edge__{model}"] = valid_path(values)

    packet = {
        "test_id": "PN5/MULTIPLICATIVE-RUNG/FRESH-R10-v1",
        "freeze_state": "PREDICTIONS WRITTEN BEFORE TARGET CONSTRUCTION",
        "target": {"low": TARGET_LOW, "high": TARGET_HIGH, "cells": CELLS},
        "source_hashes": {
            PROTOCOL.name: sha256(PROTOCOL),
            SOURCE_PATHS.name: sha256(SOURCE_PATHS),
            Path(__file__).name: sha256(Path(__file__)),
        },
        "gate_path": target,
        "source_coordinates": {
            "r8_k_candidate": k8,
            "r9_k_candidate": k9,
            "r8_j_pair": j8,
            "r9_j_pair": j9,
        },
        "predictions": {"candidate": candidate, "edge": edge},
        "clipping_adjustments": adjustments,
        "terminal_constants": {
            "euler_gamma": GAMMA,
            "mertens_pnt_factor": math.exp(GAMMA) / 2.0,
            "candidate_mertens_pnt_prediction": independent[-1] * math.exp(GAMMA) / 2.0,
            "edge_mertens_pnt_squared_prediction": edge_independent[-1] * (math.exp(GAMMA) / 2.0) ** 2,
        },
        "equivalence_disclosure": {
            "candidate": "ara_multiplicative_primary equals prior-rung raw survival-ratio transfer",
            "edge": "ara_multiplicative_primary equals prior-rung raw edge-ratio transfer after decomposing candidate squared and J",
        },
    }
    PACKET.write_text(json.dumps(ready(packet), indent=2) + "\n", encoding="utf-8")
    manifest = {
        "test_id": packet["test_id"],
        "freeze_state": packet["freeze_state"],
        "files": {
            path.name: sha256(path)
            for path in (PROTOCOL, SOURCE_PATHS, Path(__file__), PACKET)
        },
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "freeze_state": packet["freeze_state"],
        "target": packet["target"],
        "prediction_packet_sha256": manifest["files"][PACKET.name],
        "clipping_adjustments": adjustments,
    }, indent=2))


if __name__ == "__main__":
    main()
