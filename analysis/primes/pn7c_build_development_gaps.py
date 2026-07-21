"""Construct PN7C R9/R10 actual-prime gap sequences only."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN7C_ACTUAL_GAP_SEQUENTIAL_MEMORY_PROTOCOL.md"
EXPECTED_PROTOCOL = "7884D02A19A753DFD2582BEEDC6AFBE38B15E04E44DDD6F5B6B11116F518A67C"
PN3A = HERE / "PN3A_ADULT_SIEVE_DIAGNOSTIC_DATA.npz"
PN5 = HERE / "PN5_R10_TARGET_AGGREGATES.json"
OUT_NPZ = HERE / "PN7C_DEVELOPMENT_GAPS.npz"
OUT_JSON = HERE / "PN7C_DEVELOPMENT_GAPS.json"
INTERVALS = {
    "r9": (1_000_000_000, 1_010_000_000),
    "r10": (10_000_000_000, 10_100_000_000),
}
CHUNK = 10_000_000


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest().upper()


def primes_to(limit: int) -> np.ndarray:
    flags = np.ones(limit + 1, dtype=bool)
    flags[:2] = False
    for p in range(2, math.isqrt(limit) + 1):
        if flags[p]:
            flags[p * p :: p] = False
    return np.flatnonzero(flags).astype(np.int64)


def interval_gaps(low: int, high: int) -> tuple[np.ndarray, int]:
    divisors = primes_to(math.isqrt(high - 1))
    pieces = []
    previous = None
    prime_count = 0
    for start in range(low, high, CHUNK):
        stop = min(high, start + CHUNK)
        flags = np.ones(stop - start, dtype=bool)
        for qv in divisors:
            q = int(qv)
            first = ((start + q - 1) // q) * q
            if first < stop:
                flags[first - start :: q] = False
        primes = np.flatnonzero(flags).astype(np.int64) + start
        prime_count += len(primes)
        gaps = np.diff(primes) if previous is None else np.diff(np.r_[previous, primes])
        if gaps.size:
            if int(gaps.max()) >= 65536:
                raise AssertionError("Gap exceeds uint16 storage")
            pieces.append(gaps.astype(np.uint16))
        if primes.size:
            previous = int(primes[-1])
    sequence = np.concatenate(pieces)
    if len(sequence) != prime_count - 1:
        raise AssertionError("Gap sequence does not close to prime count")
    return sequence, prime_count


def main():
    if sha256(PROTOCOL) != EXPECTED_PROTOCOL:
        raise RuntimeError("Protocol hash mismatch")
    arrays = {}
    metadata = {}
    for rung, (low, high) in INTERVALS.items():
        gaps, count = interval_gaps(low, high)
        arrays[f"{rung}__gaps"] = gaps
        metadata[rung] = {
            "interval": [low, high],
            "prime_count": count,
            "gap_count": len(gaps),
            "gap_sum": int(gaps.sum(dtype=np.int64)),
            "max_gap": int(gaps.max()),
        }
        print(json.dumps({rung: metadata[rung]}, indent=2), flush=True)

    pn3a = np.load(PN3A, allow_pickle=False)
    pn5 = json.loads(PN5.read_text(encoding="utf-8"))
    expected = {
        "r9": int(np.count_nonzero(pn3a["r9__candidate_death"] == 0)),
        "r10": int(pn5["candidate"]["terminal_survivors"]),
    }
    reconciliation = {
        r: {"expected": expected[r], "observed": metadata[r]["prime_count"], "matches": expected[r] == metadata[r]["prime_count"]}
        for r in INTERVALS
    }
    if not all(v["matches"] for v in reconciliation.values()):
        raise AssertionError(reconciliation)
    np.savez_compressed(OUT_NPZ, **arrays)
    packet = {
        "test_id": "PN7C/DEVELOPMENT-GAPS/R9-R10",
        "protocol_sha256": EXPECTED_PROTOCOL,
        "r11_constructed": False,
        "r12_opened": False,
        "p31_wheel_opened": False,
        "rungs": metadata,
        "reconciliation": reconciliation,
        "npz_sha256": sha256(OUT_NPZ),
    }
    OUT_JSON.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": OUT_NPZ.name, "sha256": packet["npz_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
