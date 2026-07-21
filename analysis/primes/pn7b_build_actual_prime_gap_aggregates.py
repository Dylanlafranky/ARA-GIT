"""Build exact streaming actual-prime node/gap aggregates for PN7B.

The protocol hash is embedded so the registered geometry predates every PN7B
actual-prime gap result.  Only counts are retained; no sampled prime sequence is
used in the primary analysis.
"""

from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN7B_ACTUAL_PRIME_NODE_GAP_PROTOCOL.md"
EXPECTED_PROTOCOL_SHA256 = "9B42C13E4042B7698FC95A3A32B203CFAE5BE2873F28C0BD3ACC4653BC866F26"
PN3A_PACKET = HERE / "PN3A_ADULT_SIEVE_DIAGNOSTIC_DATA.npz"
PN5_TARGET = HERE / "PN5_R10_TARGET_AGGREGATES.json"
PN6_TARGET = HERE / "PN6_R11_TARGET_AGGREGATES.json"
OUTPUT_NPZ = HERE / "PN7B_ACTUAL_PRIME_NODE_GAP_AGGREGATES.npz"
OUTPUT_JSON = HERE / "PN7B_ACTUAL_PRIME_NODE_GAP_AGGREGATES.json"

RUNG_INTERVALS = {
    "r7": (10_000_000, 10_100_000),
    "r8": (100_000_000, 101_000_000),
    "r9": (1_000_000_000, 1_010_000_000),
    "r10": (10_000_000_000, 10_100_000_000),
    "r11": (100_000_000_000, 101_000_000_000),
}
BASE_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29)
CHUNK_SIZE = 10_000_000
MAX_BINS = 48
CONTROL_OFFSET = 257


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest().upper()


def primes_through(limit: int) -> np.ndarray:
    sieve = np.ones(limit + 1, dtype=bool)
    sieve[:2] = False
    for p in range(2, math.isqrt(limit) + 1):
        if sieve[p]:
            sieve[p * p :: p] = False
    return np.flatnonzero(sieve).astype(np.int64)


def add_exact_hist(existing: np.ndarray, values: np.ndarray) -> np.ndarray:
    if values.size == 0:
        return existing
    counts = np.bincount(values.astype(np.int64))
    if counts.size > existing.size:
        existing = np.pad(existing, (0, counts.size - existing.size))
    existing[: counts.size] += counts.astype(np.int64)
    return existing


def add_exact_pair_hist(existing: np.ndarray, left: np.ndarray, right: np.ndarray) -> np.ndarray:
    if left.size == 0:
        return existing
    needed = int(max(left.max(), right.max())) + 1
    if needed > existing.shape[0]:
        expanded = np.zeros((needed, needed), dtype=np.int64)
        expanded[: existing.shape[0], : existing.shape[1]] = existing
        existing = expanded
    width = existing.shape[1]
    indices = left.astype(np.int64) * width + right.astype(np.int64)
    existing += np.bincount(indices, minlength=width * width).reshape(width, width)
    return existing


def ara_bins(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    # floor(MAX_BINS*x/2) with x=2*right/(left+right), calculated exactly.
    bins = (MAX_BINS * right.astype(np.int64)) // (left.astype(np.int64) + right.astype(np.int64))
    return np.minimum(bins, MAX_BINS - 1).astype(np.int16)


def json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): json_ready(v) for k, v in value.items()}
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    return value


def build_rung(rung: str, low: int, high: int):
    qmax = math.isqrt(high - 1)
    active = primes_through(qmax)
    active = active[active > 29]
    midpoint = low + (high - low) // 2

    frequency = np.zeros(MAX_BINS, dtype=np.int64)
    frequency_half = np.zeros((2, MAX_BINS), dtype=np.int64)
    transition = np.zeros((MAX_BINS, MAX_BINS), dtype=np.int64)
    transition_half = np.zeros((2, MAX_BINS, MAX_BINS), dtype=np.int64)
    gap_offset_frequency = np.zeros(MAX_BINS, dtype=np.int64)
    state_offset_transition = np.zeros((MAX_BINS, MAX_BINS), dtype=np.int64)
    gap_inventory = np.zeros(1, dtype=np.int64)
    span_inventory = np.zeros(1, dtype=np.int64)
    gap_pair_inventory = np.zeros((1, 1), dtype=np.int64)

    carry_primes = np.empty(0, dtype=np.int64)
    last_prime: int | None = None
    gap_carry = np.empty(0, dtype=np.int64)
    state_carry = np.empty(0, dtype=np.int16)
    previous_state: int | None = None
    previous_center: int | None = None
    prime_total = 0
    asymmetry_sum = 0.0
    asymmetry_square_sum = 0.0
    chunks = 0
    started = time.perf_counter()

    for chunk_low in range(low, high, CHUNK_SIZE):
        chunk_high = min(high, chunk_low + CHUNK_SIZE)
        length = chunk_high - chunk_low
        is_prime = np.ones(length, dtype=bool)
        for p in BASE_PRIMES:
            is_prime[(-chunk_low) % p :: p] = False
        for p_value in active:
            p = int(p_value)
            start = ((chunk_low + p - 1) // p) * p
            if start < chunk_high:
                is_prime[start - chunk_low :: p] = False
        primes = np.flatnonzero(is_prime).astype(np.int64) + chunk_low
        del is_prime
        prime_total += int(primes.size)

        if last_prime is None:
            new_gaps = np.diff(primes)
        else:
            new_gaps = np.diff(np.r_[np.int64(last_prime), primes])
        gap_inventory = add_exact_hist(gap_inventory, new_gaps)

        if gap_carry.size:
            all_gaps = np.r_[gap_carry, new_gaps]
        else:
            all_gaps = new_gaps
        if all_gaps.size > CONTROL_OFFSET:
            control_left = all_gaps[:-CONTROL_OFFSET]
            control_right = all_gaps[CONTROL_OFFSET:]
            control_bins = ara_bins(control_left, control_right)
            gap_offset_frequency += np.bincount(control_bins, minlength=MAX_BINS)[:MAX_BINS]
        gap_carry = all_gaps[-CONTROL_OFFSET:].copy()

        combined = np.r_[carry_primes, primes] if carry_primes.size else primes
        if combined.size >= 3:
            gaps = np.diff(combined)
            left = gaps[:-1]
            right = gaps[1:]
            centers = combined[1:-1]
            bins = ara_bins(left, right)
            frequency += np.bincount(bins, minlength=MAX_BINS)[:MAX_BINS]
            sides = (centers >= midpoint).astype(np.int8)
            for side in (0, 1):
                frequency_half[side] += np.bincount(bins[sides == side], minlength=MAX_BINS)[:MAX_BINS]

            asymmetry = (right.astype(float) - left.astype(float)) / (right.astype(float) + left.astype(float))
            asymmetry_sum += float(asymmetry.sum())
            asymmetry_square_sum += float(np.dot(asymmetry, asymmetry))
            span_inventory = add_exact_hist(span_inventory, left + right)
            gap_pair_inventory = add_exact_pair_hist(gap_pair_inventory, left, right)

            if previous_state is not None:
                joined_bins = np.r_[np.int16(previous_state), bins]
                joined_centers = np.r_[np.int64(previous_center), centers]
            else:
                joined_bins = bins
                joined_centers = centers
            if joined_bins.size > 1:
                pair_index = joined_bins[:-1].astype(np.int64) * MAX_BINS + joined_bins[1:].astype(np.int64)
                transition += np.bincount(pair_index, minlength=MAX_BINS * MAX_BINS).reshape(MAX_BINS, MAX_BINS)
                pair_sides = (joined_centers[:-1] >= midpoint).astype(np.int8)
                for side in (0, 1):
                    transition_half[side] += np.bincount(
                        pair_index[pair_sides == side], minlength=MAX_BINS * MAX_BINS
                    ).reshape(MAX_BINS, MAX_BINS)
            previous_state = int(bins[-1])
            previous_center = int(centers[-1])

            if state_carry.size:
                all_states = np.r_[state_carry, bins]
            else:
                all_states = bins
            if all_states.size > CONTROL_OFFSET:
                pair_index = (
                    all_states[:-CONTROL_OFFSET].astype(np.int64) * MAX_BINS
                    + all_states[CONTROL_OFFSET:].astype(np.int64)
                )
                state_offset_transition += np.bincount(
                    pair_index, minlength=MAX_BINS * MAX_BINS
                ).reshape(MAX_BINS, MAX_BINS)
            state_carry = all_states[-CONTROL_OFFSET:].copy()

        if primes.size:
            last_prime = int(primes[-1])
            carry_primes = combined[-2:].copy()
        chunks += 1
        if rung in ("r10", "r11") and chunks % 10 == 0:
            print(f"{rung}: processed {chunk_high-low:,} / {high-low:,}", flush=True)

    node_total = int(frequency.sum())
    transition_total = int(transition.sum())
    checks = {
        "node_count_is_prime_count_minus_two": node_total == prime_total - 2,
        "transition_count_is_node_count_minus_one": transition_total == node_total - 1,
        "frequency_halves_close": int(frequency_half.sum()) == node_total,
        "transition_halves_close": int(transition_half.sum()) == transition_total,
        "gap_count_is_prime_count_minus_one": int(gap_inventory.sum()) == prime_total - 1,
        "span_count_is_node_count": int(span_inventory.sum()) == node_total,
        "gap_pair_count_is_node_count": int(gap_pair_inventory.sum()) == node_total,
        "gap_offset_count": int(gap_offset_frequency.sum()) == max(0, prime_total - 1 - CONTROL_OFFSET),
        "state_offset_count": int(state_offset_transition.sum()) == max(0, node_total - CONTROL_OFFSET),
    }
    if not all(checks.values()):
        raise AssertionError(f"{rung}: {checks}")

    arrays = {
        f"{rung}__frequency48": frequency,
        f"{rung}__frequency_half48": frequency_half,
        f"{rung}__transition48": transition,
        f"{rung}__transition_half48": transition_half,
        f"{rung}__gap_offset_frequency48": gap_offset_frequency,
        f"{rung}__state_offset_transition48": state_offset_transition,
        f"{rung}__gap_inventory": gap_inventory,
        f"{rung}__span_inventory": span_inventory,
        f"{rung}__gap_pair_inventory": gap_pair_inventory,
    }
    metadata = {
        "interval": [low, high],
        "qmax": qmax,
        "active_primes_above_29": int(active.size),
        "chunk_size": CHUNK_SIZE,
        "chunks": chunks,
        "prime_total": prime_total,
        "node_total": node_total,
        "transition_total": transition_total,
        "mean_asymmetry": asymmetry_sum / node_total,
        "rms_asymmetry": math.sqrt(asymmetry_square_sum / node_total),
        "max_gap": int(len(gap_inventory) - 1),
        "max_local_span": int(len(span_inventory) - 1),
        "exact_equal_gap_nodes": int(np.trace(gap_pair_inventory)),
        "incoming_gap_larger_nodes": int(np.tril(gap_pair_inventory, -1).sum()),
        "outgoing_gap_larger_nodes": int(np.triu(gap_pair_inventory, 1).sum()),
        "elapsed_seconds": time.perf_counter() - started,
        "checks": checks,
    }
    return arrays, metadata


def main() -> None:
    protocol_hash = sha256(PROTOCOL)
    if protocol_hash != EXPECTED_PROTOCOL_SHA256:
        raise RuntimeError(f"Protocol hash mismatch: {protocol_hash}")

    arrays: dict[str, np.ndarray] = {}
    metadata: dict[str, Any] = {}
    for rung, (low, high) in RUNG_INTERVALS.items():
        rung_arrays, rung_metadata = build_rung(rung, low, high)
        arrays.update(rung_arrays)
        metadata[rung] = rung_metadata
        print(json.dumps({rung: rung_metadata}, indent=2), flush=True)

    pn3a = np.load(PN3A_PACKET, allow_pickle=False)
    pn5 = json.loads(PN5_TARGET.read_text(encoding="utf-8"))
    pn6 = json.loads(PN6_TARGET.read_text(encoding="utf-8"))
    expected = {
        "r7": int(np.count_nonzero(pn3a["r7__candidate_death"] == 0)),
        "r8": int(np.count_nonzero(pn3a["r8__candidate_death"] == 0)),
        "r9": int(np.count_nonzero(pn3a["r9__candidate_death"] == 0)),
        "r10": int(pn5["candidate"]["terminal_survivors"]),
        "r11": int(pn6["candidate"]["terminal_survivors"]),
    }
    reconciliation = {
        rung: {
            "expected_prime_total": expected[rung],
            "observed_prime_total": metadata[rung]["prime_total"],
            "matches": expected[rung] == metadata[rung]["prime_total"],
        }
        for rung in RUNG_INTERVALS
    }
    if not all(item["matches"] for item in reconciliation.values()):
        raise AssertionError(f"Historical prime-count reconciliation failed: {reconciliation}")

    np.savez_compressed(OUTPUT_NPZ, **arrays)
    packet = {
        "test_id": "PN7B/ACTUAL-PRIME-NODE-GAP/OPENED-R10-R11-v1",
        "evidence_class": "registered structural test on already-open windows",
        "protocol_sha256": protocol_hash,
        "r12_opened": False,
        "p31_primorial_wheel_opened": False,
        "max_bins": MAX_BINS,
        "control_offset": CONTROL_OFFSET,
        "rungs": metadata,
        "historical_reconciliation": reconciliation,
    }
    packet["aggregate_npz_sha256"] = sha256(OUTPUT_NPZ)
    OUTPUT_JSON.write_text(json.dumps(json_ready(packet), indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": OUTPUT_NPZ.name,
        "sha256": packet["aggregate_npz_sha256"],
        "reconciled": True,
    }, indent=2))


if __name__ == "__main__":
    main()
