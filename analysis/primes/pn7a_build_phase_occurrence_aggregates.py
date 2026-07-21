from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN7A_PHASE_REFERENCED_OCCURRENCE_PROTOCOL.md"
PN3A_PACKET = HERE / "PN3A_ADULT_SIEVE_DIAGNOSTIC_DATA.npz"
PN5_TARGET = HERE / "PN5_R10_TARGET_AGGREGATES.json"
PN6_TARGET = HERE / "PN6_R11_TARGET_AGGREGATES.json"
OUTPUT_NPZ = HERE / "PN7A_PHASE_REFERENCED_OCCURRENCE_AGGREGATES.npz"
OUTPUT_JSON = HERE / "PN7A_PHASE_REFERENCED_OCCURRENCE_AGGREGATES.json"

RUNG_INTERVALS = {
    "r7": (10_000_000, 10_100_000),
    "r8": (100_000_000, 101_000_000),
    "r9": (1_000_000_000, 1_010_000_000),
    "r10": (10_000_000_000, 10_100_000_000),
    "r11": (100_000_000_000, 101_000_000_000),
}
BASE_PRIMES = np.array([2, 3, 5, 7, 11, 13, 17, 19, 23, 29], dtype=np.int64)
GATE_CELLS = 24
POSITION_BINS = 64
TERMINAL_STAGE = GATE_CELLS
CHUNK_SIZE = 10_000_000


def sha256(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            state.update(block)
    return state.hexdigest().upper()


def primes_through(limit: int) -> np.ndarray:
    sieve = np.ones(limit + 1, dtype=bool)
    sieve[:2] = False
    for p in range(2, math.isqrt(limit) + 1):
        if sieve[p]:
            sieve[p * p :: p] = False
    return np.flatnonzero(sieve).astype(np.int64)


def first_edge_factor(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    sentinel = np.iinfo(np.uint32).max
    left_effective = np.where(left == 0, sentinel, left)
    right_effective = np.where(right == 0, sentinel, right)
    result = np.minimum(left_effective, right_effective).astype(np.uint32)
    result[(left == 0) & (right == 0)] = 0
    return result


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


def build_rung(rung: str, low: int, high: int) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    width = high - low
    qmax = math.isqrt(high - 1)
    active = primes_through(qmax)
    active = active[active > 29]
    gate_progress = np.log(active.astype(float) / 31.0) / math.log(qmax / 31.0)
    active_cell = np.minimum((gate_progress * GATE_CELLS).astype(np.int16), GATE_CELLS - 1)
    factor_cell = np.full(qmax + 1, -1, dtype=np.int16)
    factor_cell[active] = active_cell
    q_end = np.asarray([active[active_cell <= cell][-1] for cell in range(GATE_CELLS)], dtype=np.int64)

    candidate_exposure = np.zeros(POSITION_BINS, dtype=np.int64)
    candidate_stage_position = np.zeros((GATE_CELLS + 1, POSITION_BINS), dtype=np.int64)
    edge_exposure = np.zeros(POSITION_BINS, dtype=np.int64)
    edge_stage_position = np.zeros((GATE_CELLS + 1, POSITION_BINS), dtype=np.int64)
    previous_death: int | None = None
    previous_relative: int | None = None
    chunks = 0
    started = time.perf_counter()

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

        eligible = np.ones(length, dtype=bool)
        for p_value in BASE_PRIMES:
            p = int(p_value)
            eligible[(-chunk_low) % p :: p] = False
        local_indices = np.flatnonzero(eligible).astype(np.int64)
        deaths = smallest[eligible]
        del smallest, eligible
        relative = local_indices + (chunk_low - low)
        positions = np.minimum(relative * POSITION_BINS // width, POSITION_BINS - 1).astype(np.int16)

        candidate_exposure += np.bincount(positions, minlength=POSITION_BINS)[:POSITION_BINS]
        stages = np.full(len(deaths), TERMINAL_STAGE, dtype=np.int16)
        removed = deaths > 0
        stages[removed] = factor_cell[deaths[removed].astype(np.int64)]
        candidate_stage_position += np.bincount(
            stages.astype(np.int64) * POSITION_BINS + positions.astype(np.int64),
            minlength=(GATE_CELLS + 1) * POSITION_BINS,
        ).reshape(GATE_CELLS + 1, POSITION_BINS)

        if previous_death is not None:
            joined_deaths = np.r_[np.uint32(previous_death), deaths]
            joined_relative = np.r_[np.int64(previous_relative), relative]
        else:
            joined_deaths = deaths
            joined_relative = relative
        if len(joined_deaths) > 1:
            edge_factors = first_edge_factor(joined_deaths[:-1], joined_deaths[1:])
            edge_relative = joined_relative[:-1]
            edge_positions = np.minimum(edge_relative * POSITION_BINS // width, POSITION_BINS - 1).astype(np.int16)
            edge_exposure += np.bincount(edge_positions, minlength=POSITION_BINS)[:POSITION_BINS]
            edge_stages = np.full(len(edge_factors), TERMINAL_STAGE, dtype=np.int16)
            edge_removed = edge_factors > 0
            edge_stages[edge_removed] = factor_cell[edge_factors[edge_removed].astype(np.int64)]
            edge_stage_position += np.bincount(
                edge_stages.astype(np.int64) * POSITION_BINS + edge_positions.astype(np.int64),
                minlength=(GATE_CELLS + 1) * POSITION_BINS,
            ).reshape(GATE_CELLS + 1, POSITION_BINS)
        previous_death = int(deaths[-1])
        previous_relative = int(relative[-1])
        chunks += 1
        if rung in ("r10", "r11") and chunks % 10 == 0:
            print(f"{rung}: processed {chunk_high - low:,} / {width:,}", flush=True)

    elapsed = time.perf_counter() - started
    candidate_total = int(candidate_exposure.sum())
    edge_total = int(edge_exposure.sum())
    candidate_terminal = int(candidate_stage_position[TERMINAL_STAGE].sum())
    edge_terminal = int(edge_stage_position[TERMINAL_STAGE].sum())
    checks = {
        "candidate_matrix_closes": int(candidate_stage_position.sum()) == candidate_total,
        "edge_matrix_closes": int(edge_stage_position.sum()) == edge_total,
        "edge_is_candidate_minus_one": edge_total == candidate_total - 1,
        "candidate_position_closes": bool(np.array_equal(candidate_stage_position.sum(axis=0), candidate_exposure)),
        "edge_position_closes": bool(np.array_equal(edge_stage_position.sum(axis=0), edge_exposure)),
    }
    if not all(checks.values()):
        raise AssertionError(f"{rung} accounting failure: {checks}")

    arrays = {
        f"{rung}__candidate_exposure": candidate_exposure,
        f"{rung}__candidate_stage_position": candidate_stage_position,
        f"{rung}__edge_exposure": edge_exposure,
        f"{rung}__edge_stage_position": edge_stage_position,
        f"{rung}__q_end": q_end,
    }
    metadata = {
        "interval": [low, high],
        "width": width,
        "qmax": qmax,
        "active_gate_count": len(active),
        "chunks": chunks,
        "chunk_size": CHUNK_SIZE,
        "elapsed_seconds": elapsed,
        "candidate_total": candidate_total,
        "candidate_terminal": candidate_terminal,
        "edge_total": edge_total,
        "edge_terminal": edge_terminal,
        "checks": checks,
    }
    return arrays, metadata


def main() -> None:
    source_hashes = {
        PROTOCOL.name: sha256(PROTOCOL),
        PN3A_PACKET.name: sha256(PN3A_PACKET),
        PN5_TARGET.name: sha256(PN5_TARGET),
        PN6_TARGET.name: sha256(PN6_TARGET),
        Path(__file__).name: sha256(Path(__file__)),
    }
    arrays: dict[str, np.ndarray] = {}
    rung_metadata: dict[str, Any] = {}
    for rung, (low, high) in RUNG_INTERVALS.items():
        rung_arrays, metadata = build_rung(rung, low, high)
        arrays.update(rung_arrays)
        rung_metadata[rung] = metadata
        print(json.dumps({rung: metadata}, indent=2), flush=True)

    pn3a = np.load(PN3A_PACKET, allow_pickle=False)
    pn5 = json.loads(PN5_TARGET.read_text(encoding="utf-8"))
    pn6 = json.loads(PN6_TARGET.read_text(encoding="utf-8"))
    reconciliation: dict[str, dict[str, Any]] = {}
    for rung in ("r7", "r8", "r9"):
        expected_total = len(pn3a[f"{rung}__candidate_death"])
        expected_terminal = int(np.count_nonzero(pn3a[f"{rung}__candidate_death"] == 0))
        observed = rung_metadata[rung]
        reconciliation[rung] = {
            "candidate_total_expected": expected_total,
            "candidate_total_observed": observed["candidate_total"],
            "candidate_total_matches": expected_total == observed["candidate_total"],
            "candidate_terminal_expected": expected_terminal,
            "candidate_terminal_observed": observed["candidate_terminal"],
            "candidate_terminal_matches": expected_terminal == observed["candidate_terminal"],
        }
    for rung, target in (("r10", pn5), ("r11", pn6)):
        observed = rung_metadata[rung]
        reconciliation[rung] = {
            "candidate_total_expected": target["candidate"]["n0"],
            "candidate_total_observed": observed["candidate_total"],
            "candidate_total_matches": target["candidate"]["n0"] == observed["candidate_total"],
            "candidate_terminal_expected": target["candidate"]["terminal_survivors"],
            "candidate_terminal_observed": observed["candidate_terminal"],
            "candidate_terminal_matches": target["candidate"]["terminal_survivors"] == observed["candidate_terminal"],
            "edge_total_expected": target["edge"]["n0"],
            "edge_total_observed": observed["edge_total"],
            "edge_total_matches": target["edge"]["n0"] == observed["edge_total"],
            "edge_terminal_expected": target["edge"]["terminal_survivors"],
            "edge_terminal_observed": observed["edge_terminal"],
            "edge_terminal_matches": target["edge"]["terminal_survivors"] == observed["edge_terminal"],
        }
    if not all(value for rung in reconciliation.values() for key, value in rung.items() if key.endswith("_matches")):
        raise AssertionError(f"Historical reconciliation failed: {reconciliation}")

    np.savez_compressed(OUTPUT_NPZ, **arrays)
    packet = {
        "test_id": "PN7A/PHASE-REFERENCED-OCCURRENCE/OPENED-DEVELOPMENT-v1",
        "evidence_class": "opened-data structural diagnostic",
        "r12_opened": False,
        "pn1h_p31_opened": False,
        "gate_cells": GATE_CELLS,
        "position_bins": POSITION_BINS,
        "terminal_stage": TERMINAL_STAGE,
        "rungs": rung_metadata,
        "historical_reconciliation": reconciliation,
        "source_hashes": source_hashes,
        "aggregate_npz_sha256": sha256(OUTPUT_NPZ),
    }
    OUTPUT_JSON.write_text(json.dumps(json_ready(packet), indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": OUTPUT_NPZ.name,
        "npz_sha256": packet["aggregate_npz_sha256"],
        "metadata_sha256": sha256(OUTPUT_JSON),
        "reconciled": True,
    }, indent=2))


if __name__ == "__main__":
    main()
