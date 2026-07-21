"""Construct the code-isolated PN7C R11 actual-prime gap target."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN7C_ACTUAL_GAP_SEQUENTIAL_MEMORY_PROTOCOL.md"
MODEL = HERE / "PN7C_FROZEN_MODELS.npz"
PN6 = HERE / "PN6_R11_TARGET_AGGREGATES.json"
EXPECTED_PROTOCOL = "7884D02A19A753DFD2582BEEDC6AFBE38B15E04E44DDD6F5B6B11116F518A67C"
EXPECTED_MODEL = "9141AA398C6A6694C3C5F3ECA954681D4AD8091C01310D13C6703DB30668F3A2"
OUT_NPZ = HERE / "PN7C_R11_TARGET_GAPS.npz"
OUT_JSON = HERE / "PN7C_R11_TARGET_GAPS.json"
LOW, HIGH = 100_000_000_000, 101_000_000_000
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


def interval_gaps() -> tuple[np.ndarray, int, int, int]:
    divisors = primes_to(math.isqrt(HIGH - 1))
    pieces = []
    previous = None
    first_prime = None
    last_prime = None
    prime_count = 0
    for start in range(LOW, HIGH, CHUNK):
        stop = min(HIGH, start + CHUNK)
        flags = np.ones(stop - start, dtype=bool)
        for qv in divisors:
            q = int(qv)
            first = ((start + q - 1) // q) * q
            if first < stop:
                flags[first - start :: q] = False
        primes = np.flatnonzero(flags).astype(np.int64) + start
        if primes.size and first_prime is None:
            first_prime = int(primes[0])
        prime_count += len(primes)
        gaps = np.diff(primes) if previous is None else np.diff(np.r_[previous, primes])
        if gaps.size:
            if int(gaps.max()) >= 65536:
                raise AssertionError("Gap exceeds uint16 storage")
            pieces.append(gaps.astype(np.uint16))
        if primes.size:
            previous = int(primes[-1])
            last_prime = previous
    sequence = np.concatenate(pieces)
    if len(sequence) != prime_count - 1:
        raise AssertionError("Gap sequence does not close to prime count")
    return sequence, prime_count, int(first_prime), int(last_prime)


def main() -> None:
    if sha256(PROTOCOL) != EXPECTED_PROTOCOL:
        raise RuntimeError("Protocol hash mismatch")
    if sha256(MODEL) != EXPECTED_MODEL:
        raise RuntimeError("Frozen-model hash mismatch")

    gaps, count, first_prime, last_prime = interval_gaps()
    pn6 = json.loads(PN6.read_text(encoding="utf-8"))
    expected_count = int(pn6["candidate"]["terminal_survivors"])
    if count != expected_count:
        raise AssertionError(f"R11 count {count} != independently recorded {expected_count}")

    np.savez_compressed(OUT_NPZ, r11__gaps=gaps)
    packet = {
        "test_id": "PN7C/CODE-ISOLATED-R11-TARGET-GAPS",
        "protocol_sha256": EXPECTED_PROTOCOL,
        "frozen_model_npz_sha256": EXPECTED_MODEL,
        "interval": [LOW, HIGH],
        "prime_count": count,
        "gap_count": len(gaps),
        "first_prime": first_prime,
        "last_prime": last_prime,
        "gap_sum": int(gaps.sum(dtype=np.int64)),
        "max_gap": int(gaps.max()),
        "prime_count_reconciliation": {
            "expected_from_pn6": expected_count,
            "observed": count,
            "matches": count == expected_count,
        },
        "target_npz_sha256": sha256(OUT_NPZ),
        "builder_sha256": sha256(Path(__file__)),
        "r12_opened": False,
        "p31_wheel_opened": False,
    }
    OUT_JSON.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(packet, indent=2), flush=True)


if __name__ == "__main__":
    main()
