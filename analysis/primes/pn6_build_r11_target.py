from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
PREDICTIONS = HERE / "PN6_NATIVE_ARA_FROZEN_PREDICTIONS.json"
FREEZE_MANIFEST = HERE / "PN6_NATIVE_ARA_FREEZE_MANIFEST.json"
TARGET_PACKET = HERE / "PN6_R11_TARGET_AGGREGATES.json"

SMALL_PRIMES = np.array([2, 3, 5, 7, 11, 13, 17, 19, 23, 29], dtype=np.int64)
CHUNK_SIZE = 10_000_000


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


def add_death_counts(death: np.ndarray, factor_cell: np.ndarray, counts: np.ndarray) -> None:
    positive = death[death > 0]
    if len(positive):
        cells = factor_cell[positive.astype(np.int64)]
        counts += np.bincount(cells, minlength=len(counts))[: len(counts)]


def edge_death(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    sentinel = np.iinfo(np.uint32).max
    left_effective = np.where(left == 0, sentinel, left)
    right_effective = np.where(right == 0, sentinel, right)
    out = np.minimum(left_effective, right_effective).astype(np.uint32)
    out[(left == 0) & (right == 0)] = 0
    return out


def json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    return value


def main() -> None:
    manifest = json.loads(FREEZE_MANIFEST.read_text(encoding="utf-8"))
    expected_hash = manifest["files"][PREDICTIONS.name]
    actual_hash = sha256(PREDICTIONS)
    if actual_hash != expected_hash:
        raise AssertionError("Frozen prediction packet hash mismatch; refusing to construct target")

    frozen = json.loads(PREDICTIONS.read_text(encoding="utf-8"))
    low = int(frozen["target"]["low"])
    high = int(frozen["target"]["high"])
    cells = int(frozen["target"]["cells"])
    qmax = math.isqrt(high - 1)

    all_primes = primes_through(qmax)
    active = all_primes[all_primes > 29]
    progress = np.log(active.astype(float) / 31.0) / math.log(qmax / 31.0)
    gate_cell = np.minimum((progress * cells).astype(np.int16), cells - 1)
    factor_cell = np.full(qmax + 1, -1, dtype=np.int16)
    factor_cell[active] = gate_cell
    q_end = np.array([int(active[gate_cell <= cell][-1]) for cell in range(cells)], dtype=np.int64)

    candidate_deaths = np.zeros(cells, dtype=np.int64)
    edge_deaths = np.zeros(cells, dtype=np.int64)
    candidate_count = 0
    edge_count = 0
    candidate_survivors = 0
    edge_survivors = 0
    previous_death: np.uint32 | None = None
    started = time.perf_counter()
    chunks = 0

    for chunk_low in range(low, high, CHUNK_SIZE):
        chunk_high = min(high, chunk_low + CHUNK_SIZE)
        length = chunk_high - chunk_low
        smallest = np.zeros(length, dtype=np.uint32)

        for p_value in active:
            p = int(p_value)
            start = ((chunk_low + p - 1) // p) * p
            if start >= chunk_high:
                continue
            view = smallest[start - chunk_low :: p]
            empty = view == 0
            view[empty] = p

        candidate_mask = np.ones(length, dtype=bool)
        for p_value in SMALL_PRIMES:
            p = int(p_value)
            candidate_mask[(-chunk_low) % p :: p] = False
        death = smallest[candidate_mask]
        del smallest, candidate_mask
        if not len(death):
            continue

        candidate_count += len(death)
        candidate_survivors += int(np.count_nonzero(death == 0))
        add_death_counts(death, factor_cell, candidate_deaths)

        if previous_death is not None:
            bridge = edge_death(np.asarray([previous_death], dtype=np.uint32), death[:1])
            edge_count += 1
            if bridge[0] == 0:
                edge_survivors += 1
            else:
                add_death_counts(bridge, factor_cell, edge_deaths)
        if len(death) > 1:
            local_edges = edge_death(death[:-1], death[1:])
            edge_count += len(local_edges)
            edge_survivors += int(np.count_nonzero(local_edges == 0))
            add_death_counts(local_edges, factor_cell, edge_deaths)
        previous_death = death[-1]
        chunks += 1
        if chunks % 10 == 0:
            print(f"processed {chunk_high - low:,} / {high - low:,} integers", flush=True)

    if candidate_count != candidate_survivors + int(candidate_deaths.sum()):
        raise AssertionError("Candidate accounting does not close")
    if edge_count != edge_survivors + int(edge_deaths.sum()):
        raise AssertionError("Edge accounting does not close")
    if edge_count != candidate_count - 1:
        raise AssertionError("Edge count is not candidate count minus one")

    def make_path(total: int, deaths: np.ndarray) -> dict[str, np.ndarray]:
        before = np.empty(cells, dtype=np.int64)
        survival = np.empty(cells, dtype=float)
        alive = total
        for cell in range(cells):
            before[cell] = alive
            alive -= int(deaths[cell])
            survival[cell] = alive / total
        return {
            "before": before,
            "deaths": deaths,
            "survival": survival,
            "hazard": deaths / before,
        }

    candidate_path = make_path(candidate_count, candidate_deaths)
    edge_path = make_path(edge_count, edge_deaths)
    elapsed = time.perf_counter() - started
    packet = {
        "test_id": frozen["test_id"],
        "target_state": "OPENED AFTER FROZEN NATIVE ARA PREDICTION HASH VERIFIED",
        "target": {"low": low, "high": high, "width": high - low},
        "construction": {
            "algorithm": "exact chunked segmented Eratosthenes smallest-factor sieve",
            "chunk_size": CHUNK_SIZE,
            "chunks": chunks,
            "elapsed_seconds": elapsed,
            "active_gate_count": len(active),
            "qmax": qmax,
        },
        "freeze_evidence": {
            "prediction_packet_sha256_expected": expected_hash,
            "prediction_packet_sha256_observed_before_open": actual_hash,
            "matched": expected_hash == actual_hash,
        },
        "q_end": q_end,
        "candidate": {"n0": candidate_count, "terminal_survivors": candidate_survivors, **candidate_path},
        "edge": {"n0": edge_count, "terminal_survivors": edge_survivors, **edge_path},
        "accounting_checks": {
            "candidate_closes": candidate_count == candidate_survivors + int(candidate_deaths.sum()),
            "edge_closes": edge_count == edge_survivors + int(edge_deaths.sum()),
            "edge_count_is_candidate_minus_one": edge_count == candidate_count - 1,
        },
        "builder_sha256": sha256(Path(__file__)),
    }
    TARGET_PACKET.write_text(json.dumps(json_ready(packet), indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "target_state": packet["target_state"],
        "elapsed_seconds": elapsed,
        "candidate_n0": candidate_count,
        "candidate_survivors": candidate_survivors,
        "edge_n0": edge_count,
        "edge_survivors": edge_survivors,
        "target_packet_sha256": sha256(TARGET_PACKET),
    }, indent=2))


if __name__ == "__main__":
    main()
