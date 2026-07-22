"""PN26 primary prediction builder.

This file intentionally contains no primality test and no next-prime routine.
It seals the first three quiet states of a frozen Phase A parent on fresh
anchor ranges. Target truth is opened only by the independent validator.
"""

from __future__ import annotations

import bisect
import csv
import hashlib
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN26_DOMINANT_PARENT_RIDGE_LOCATOR_PROTOCOL_v1_FROZEN.md"
FREEZE = HERE / "PN26_TARGET_FREEZE_MANIFEST.json"
PREDICTIONS = HERE / "PN26_DOMINANT_PARENT_RIDGE_PREDICTIONS.csv"
RESULTS = HERE / "PN26_DOMINANT_PARENT_RIDGE_PRIMARY.json"

TARGET_RANGES = (
    ("low", 71_000_000, 71_500_000, 26001),
    ("middle", 71_000_000_000, 71_000_500_000, 26002),
    ("high", 710_000_000_000, 710_000_500_000, 26003),
)
N_PER_RANGE = 2_000
MAX_OFFSET = 4_096
RANKED_CANDIDATES = 3


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sieve_primes(limit: int) -> list[int]:
    flags = bytearray(b"\x01") * (limit + 1)
    flags[0:2] = b"\x00\x00"
    for value in range(2, math.isqrt(limit) + 1):
        if flags[value]:
            start = value * value
            flags[start : limit + 1 : value] = b"\x00" * (((limit - start) // value) + 1)
    return [value for value in range(2, limit + 1) if flags[value]]


def split_parent(scale_anchor: int, primes: list[int], prefix_logs: list[float]) -> dict:
    child_limit = math.isqrt(2 * scale_anchor)
    child_end = bisect.bisect_right(primes, child_limit)
    total_log = prefix_logs[child_end]
    half_log = total_log / 2.0
    cut = bisect.bisect_left(prefix_logs, half_log, 1, child_end)
    options = [max(1, cut - 1), min(child_end - 1, cut)]
    cut = min(options, key=lambda index: abs(prefix_logs[index] - half_log))
    phase_a_log = prefix_logs[cut]
    return {
        "child_limit": child_limit,
        "child_count": child_end,
        "split_index": cut,
        "phase_a_count": cut,
        "phase_b_count": child_end - cut,
        "phase_a_last_child": primes[cut - 1],
        "phase_b_first_child": primes[cut],
        "teara_phase_a": 2.0 * phase_a_log / total_log,
        "teara_phase_b": 2.0 - (2.0 * phase_a_log / total_log),
    }


def parent_survival_mask(low: int, high: int, phase_a: list[int]) -> tuple[int, bytearray]:
    base = low + 1
    endpoint = high + MAX_OFFSET
    mask = bytearray(b"\x01") * (endpoint - base + 1)
    for child in phase_a:
        first_index = (-base) % child
        count = ((len(mask) - 1 - first_index) // child) + 1
        mask[first_index::child] = b"\x00" * count
    return base, mask


def first_quiet_candidates(anchor: int, base: int, mask: bytearray) -> list[int]:
    candidates: list[int] = []
    start = anchor + 1 - base
    stop = min(anchor + MAX_OFFSET - base + 1, len(mask))
    for index in range(start, stop):
        if mask[index]:
            candidates.append(base + index)
            if len(candidates) == RANKED_CANDIDATES:
                return candidates
    raise RuntimeError(f"fewer than {RANKED_CANDIDATES} Phase A quiet states above {anchor}")


def verify_freeze() -> dict:
    manifest = json.loads(FREEZE.read_text(encoding="utf-8"))
    expected = manifest["hashes"]
    actual = {
        "protocol_sha256": sha256_file(PROTOCOL),
        "primary_sha256": sha256_file(Path(__file__).resolve()),
        "validator_sha256": sha256_file(HERE / "validate_pn26_dominant_parent_ridge_locator.py"),
    }
    if actual != expected:
        raise RuntimeError(f"PN26 freeze mismatch: {actual} != {expected}")
    if manifest["parameters"] != {
        "target_ranges": [list(item) for item in TARGET_RANGES],
        "n_per_range": N_PER_RANGE,
        "maximum_offset": MAX_OFFSET,
        "ranked_candidates": RANKED_CANDIDATES,
    }:
        raise RuntimeError("PN26 frozen parameters differ from primary source")
    return manifest


def main() -> None:
    for output in (PREDICTIONS, RESULTS):
        if output.exists():
            raise RuntimeError(f"refusing to overwrite sealed artifact {output.name}")
    manifest = verify_freeze()

    maximum_child = math.isqrt(2 * max(low for _, low, _, _ in TARGET_RANGES)) + 10
    primes = sieve_primes(maximum_child)
    prefix_logs = [0.0]
    for prime in primes:
        prefix_logs.append(prefix_logs[-1] + math.log(prime))

    rows: list[dict] = []
    scale_metadata: list[dict] = []
    for cohort, low, high, seed in TARGET_RANGES:
        parent = split_parent(low, primes, prefix_logs)
        phase_a = primes[: parent["split_index"]]
        base, mask = parent_survival_mask(low, high, phase_a)
        anchors = sorted(random.Random(seed).sample(range(low, high), N_PER_RANGE))
        scale_metadata.append({"cohort": cohort, "scale_anchor": low, **parent})
        for anchor in anchors:
            candidates = first_quiet_candidates(anchor, base, mask)
            first_residue = candidates[0] % 14
            representative = min(first_residue, 14 - first_residue)
            rows.append({
                "cohort": cohort,
                "scale_anchor": low,
                "anchor": anchor,
                "phase_a_candidate_1": candidates[0],
                "phase_a_delta_1": candidates[0] - anchor,
                "phase_a_candidate_2": candidates[1],
                "phase_a_delta_2": candidates[1] - anchor,
                "phase_a_candidate_3": candidates[2],
                "phase_a_delta_3": candidates[2] - anchor,
                "first_mod14_lane": first_residue,
                "first_pair_representative": representative,
                "first_pair_closeness": representative / 7.0,
                "cross_rung_frame": 3.5,
                "phase_a_child_count": parent["phase_a_count"],
                "phase_b_child_count": parent["phase_b_count"],
                "teara_phase_a": parent["teara_phase_a"],
                "teara_phase_b": parent["teara_phase_b"],
            })

    with PREDICTIONS.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    payload = {
        "test_id": "PN26/DOMINANT-PARENT-RIDGE-LOCATOR/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PREDICTIONS SEALED; TARGET TRUTH UNOPENED BY PRIMARY",
        "freeze_manifest_sha256": sha256_file(FREEZE),
        "protocol_sha256": manifest["hashes"]["protocol_sha256"],
        "prediction_file": PREDICTIONS.name,
        "prediction_sha256": sha256_file(PREDICTIONS),
        "row_count": len(rows),
        "scale_metadata": scale_metadata,
        "cross_rung_frame": {
            "rung_span": 2,
            "current_identity": 1,
            "same_identity_at_doubled_scale": 0.5,
            "route_total": 3.5,
            "predictive_use": False,
            "reason": "constant across all targets; child-wave quiet-state location supplies the correction",
        },
        "protected_87_bit_anchor_used": False,
        "truth_fields_present": False,
    }
    RESULTS.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
