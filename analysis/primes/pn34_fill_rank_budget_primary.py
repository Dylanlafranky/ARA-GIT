"""PN34 primary builder: seal candidates and fill priors without prime labels."""

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
FREEZE = HERE / "PN34_PROTOCOL_FREEZE_MANIFEST.json"
PREDICTIONS = HERE / "PN34_FILL_RANK_BUDGET_PREDICTIONS.csv"
RECEIPT = HERE / "PN34_FILL_RANK_BUDGET_PRIMARY.json"

TARGET_RANGES = (
    ("low", 89_000_000, 89_500_000, 34001),
    ("middle", 89_000_000_000, 89_000_500_000, 34002),
    ("high", 8_900_000_000_000, 8_900_000_500_000, 34003),
)
ROWS_PER_COHORT = 2_000
MAX_OFFSET = 4_096
RANKED_CANDIDATES = 3
FLAT_PN26_TOP1 = 0.9398333333333333


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sieve_primes(limit: int) -> list[int]:
    flags = bytearray(b"\x01") * (limit + 1)
    flags[0:2] = b"\x00\x00"
    for value in range(2, math.isqrt(limit) + 1):
        if flags[value]:
            start = value * value
            flags[start : limit + 1 : value] = b"\x00" * (((limit - start) // value) + 1)
    return [value for value in range(2, limit + 1) if flags[value]]


def parent_split(scale_anchor: int, primes: list[int], prefix_logs: list[float]) -> dict:
    child_limit = math.isqrt(2 * scale_anchor)
    child_end = bisect.bisect_right(primes, child_limit)
    total_log = prefix_logs[child_end]
    half_log = total_log / 2.0
    cut = bisect.bisect_left(prefix_logs, half_log, 1, child_end)
    options = [max(1, cut - 1), min(child_end - 1, cut)]
    cut = min(options, key=lambda index: abs(prefix_logs[index] - half_log))

    log_d_a = sum(-math.log1p(-1.0 / prime) for prime in primes[:cut])
    log_r_b = sum(-math.log1p(-1.0 / prime) for prime in primes[cut:child_end])
    r_b = math.exp(log_r_b)
    p1 = 1.0 / r_b
    return {
        "child_limit": child_limit,
        "child_count": child_end,
        "phase_a_count": cut,
        "phase_b_count": child_end - cut,
        "phase_a_last_child": primes[cut - 1],
        "phase_b_first_child": primes[cut],
        "remaining_fill_ratio": r_b,
        "remaining_fill_x": 2.0 * log_r_b / math.log(2.0),
        "predicted_top1": p1,
        "predicted_top2": 1.0 - (1.0 - p1) ** 2,
        "predicted_top3": 1.0 - (1.0 - p1) ** 3,
        "conditional_pnt_top1": min(1.0, math.exp(log_d_a) / math.log(scale_anchor)),
        "flat_pn26_top1": FLAT_PN26_TOP1,
    }


def phase_a_mask(low: int, high: int, phase_a: list[int]) -> tuple[int, bytearray]:
    base = low + 1
    endpoint = high + MAX_OFFSET
    mask = bytearray(b"\x01") * (endpoint - base + 1)
    for child in phase_a:
        first = (-base) % child
        if first >= len(mask):
            continue
        count = ((len(mask) - 1 - first) // child) + 1
        mask[first::child] = b"\x00" * count
    return base, mask


def first_candidates(anchor: int, base: int, mask: bytearray) -> list[int]:
    found: list[int] = []
    start = anchor + 1 - base
    stop = min(anchor + MAX_OFFSET - base + 1, len(mask))
    for index in range(start, stop):
        if mask[index]:
            found.append(base + index)
            if len(found) == RANKED_CANDIDATES:
                return found
    raise RuntimeError(f"not enough Phase A quiet candidates above {anchor}")


def verify_freeze() -> dict:
    manifest = json.loads(FREEZE.read_text(encoding="utf-8"))
    expected = manifest["files"]
    for name, expected_hash in expected.items():
        if sha256(HERE / name) != expected_hash:
            raise RuntimeError(f"freeze mismatch for {name}")
    expected_parameters = {
        "target_ranges": [list(item) for item in TARGET_RANGES],
        "rows_per_cohort": ROWS_PER_COHORT,
        "maximum_offset": MAX_OFFSET,
        "ranked_candidates": RANKED_CANDIDATES,
    }
    if manifest["parameters"] != expected_parameters:
        raise RuntimeError("PN34 frozen parameters do not match primary source")
    return manifest


def main() -> None:
    for path in (PREDICTIONS, RECEIPT):
        if path.exists():
            raise RuntimeError(f"refusing to overwrite sealed artifact {path.name}")
    verify_freeze()

    max_child = math.isqrt(2 * max(low for _, low, _, _ in TARGET_RANGES)) + 10
    primes = sieve_primes(max_child)
    prefix_logs = [0.0]
    for prime in primes:
        prefix_logs.append(prefix_logs[-1] + math.log(prime))

    rows: list[dict] = []
    cohort_metadata: list[dict] = []
    for cohort, low, high, seed in TARGET_RANGES:
        parent = parent_split(low, primes, prefix_logs)
        phase_a = primes[: parent["phase_a_count"]]
        base, mask = phase_a_mask(low, high, phase_a)
        anchors = sorted(random.Random(seed).sample(range(low, high), ROWS_PER_COHORT))
        cohort_metadata.append({"cohort": cohort, "scale_anchor": low, **parent})
        for anchor in anchors:
            candidates = first_candidates(anchor, base, mask)
            rows.append(
                {
                    "test_id": "PN34/FILL-RANK-BUDGET/v1",
                    "cohort": cohort,
                    "scale_anchor": low,
                    "anchor": anchor,
                    "candidate_1": candidates[0],
                    "candidate_2": candidates[1],
                    "candidate_3": candidates[2],
                    "delta_1": candidates[0] - anchor,
                    "delta_2": candidates[1] - anchor,
                    "delta_3": candidates[2] - anchor,
                    "phase_a_count": parent["phase_a_count"],
                    "phase_b_count": parent["phase_b_count"],
                    "phase_a_last_child": parent["phase_a_last_child"],
                    "phase_b_first_child": parent["phase_b_first_child"],
                    "remaining_fill_ratio": parent["remaining_fill_ratio"],
                    "remaining_fill_x": parent["remaining_fill_x"],
                    "predicted_top1": parent["predicted_top1"],
                    "predicted_top2": parent["predicted_top2"],
                    "predicted_top3": parent["predicted_top3"],
                    "conditional_pnt_top1": parent["conditional_pnt_top1"],
                    "flat_pn26_top1": parent["flat_pn26_top1"],
                }
            )

    with PREDICTIONS.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    payload = {
        "test_id": "PN34/FILL-RANK-BUDGET/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PREDICTIONS SEALED; FRESH TARGET TRUTH UNOPENED BY PRIMARY",
        "protocol_freeze_sha256": sha256(FREEZE),
        "prediction_file": PREDICTIONS.name,
        "prediction_sha256": sha256(PREDICTIONS),
        "row_count": len(rows),
        "cohorts": cohort_metadata,
        "truth_fields_present": False,
        "individual_candidate_classifier_registered": False,
    }
    RECEIPT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

