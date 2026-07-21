"""Exploratory post-target robustness audit for PN19's second-go behavior.

This analysis was written only after the fresh PN19 prediction was sealed and
validated. It cannot upgrade the confirmatory target result; it explains how
often the Phase A parent alone reaches the joint lock on a deterministic grid.
"""

from __future__ import annotations

import bisect
import json
import math
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "PN19_POST_TARGET_SECOND_GO_ROBUSTNESS.json"
SCALES = (10**8, 10**9, 10**10, 10**11, 10**12)
ANCHORS_PER_SCALE = 200
GRID_STEP = 1_000_003
MAX_OFFSET = 4096
P29 = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29)


def eratosthenes(limit: int) -> list[int]:
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for prime in range(2, math.isqrt(limit) + 1):
        if sieve[prime]:
            start = prime * prime
            sieve[start : limit + 1 : prime] = b"\x00" * (((limit - start) // prime) + 1)
    return [value for value in range(2, limit + 1) if sieve[value]]


def miller_rabin_64(number: int) -> bool:
    if number < 2:
        return False
    for prime in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if number % prime == 0:
            return number == prime
    remainder = number - 1
    power = 0
    while remainder % 2 == 0:
        power += 1
        remainder //= 2
    for base in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if base % number == 0:
            continue
        witness = pow(base, remainder, number)
        if witness in (1, number - 1):
            continue
        for _ in range(power - 1):
            witness = pow(witness, 2, number)
            if witness == number - 1:
                break
        else:
            return False
    return True


def survives(number: int, children: list[int]) -> bool:
    return all(number % child for child in children)


def first_offset(anchor: int, predicate) -> int:
    for offset in range(1, MAX_OFFSET + 1):
        if predicate(anchor + offset):
            return offset
    raise RuntimeError(f"No event within {MAX_OFFSET} integers above {anchor}")


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError("PN19 robustness artifact already exists; refusing to overwrite")
    primes = eratosthenes(math.isqrt(2 * (10**12 + ANCHORS_PER_SCALE * GRID_STEP)) + 1)
    prefix_logs = [0.0]
    for prime in primes:
        prefix_logs.append(prefix_logs[-1] + math.log(prime))

    rows: list[dict] = []
    for scale in SCALES:
        for index in range(ANCHORS_PER_SCALE):
            anchor = scale + index * GRID_STEP
            child_end = bisect.bisect_right(primes, math.isqrt(2 * anchor))
            half_log = prefix_logs[child_end] / 2.0
            cut = bisect.bisect_left(prefix_logs, half_log, 1, child_end)
            candidates = [max(1, cut - 1), min(child_end - 1, cut)]
            cut = min(candidates, key=lambda value: abs(prefix_logs[value] - half_log))
            phase_a = primes[:cut]
            phase_b = primes[cut:child_end]

            actual = first_offset(anchor, miller_rabin_64)
            first_a = first_offset(anchor, lambda value: survives(value, phase_a))
            first_b = first_offset(anchor, lambda value: survives(value, phase_b))
            first_p29 = first_offset(anchor, lambda value: survives(value, list(P29)))
            false_a = sum(survives(anchor + offset, phase_a) for offset in range(1, actual))
            false_b = sum(survives(anchor + offset, phase_b) for offset in range(1, actual))
            rows.append({
                "scale": scale,
                "grid_index": index,
                "anchor": anchor,
                "actual_first_prime_offset": actual,
                "phase_a_first_survivor_offset": first_a,
                "phase_b_first_survivor_offset": first_b,
                "p29_first_survivor_offset": first_p29,
                "phase_a_second_go_success": first_a == actual,
                "phase_b_second_go_success": first_b == actual,
                "either_parent_second_go_success": first_a == actual or first_b == actual,
                "p29_first_survivor_success": first_p29 == actual,
                "phase_a_false_survivors_before_lock": false_a,
                "phase_b_false_survivors_before_lock": false_b,
                "phase_a_child_count": len(phase_a),
                "phase_b_child_count": len(phase_b),
                "phase_a_last_child": phase_a[-1],
                "phase_b_first_child": phase_b[0],
                "phase_a_cut_over_sqrt_n": phase_a[-1] / math.sqrt(anchor),
            })

    summaries: list[dict] = []
    for scale in SCALES:
        group = [row for row in rows if row["scale"] == scale]
        summaries.append({
            "scale": scale,
            "anchor_count": len(group),
            "phase_a_success_rate": sum(row["phase_a_second_go_success"] for row in group) / len(group),
            "phase_b_success_rate": sum(row["phase_b_second_go_success"] for row in group) / len(group),
            "either_parent_success_rate": sum(row["either_parent_second_go_success"] for row in group) / len(group),
            "p29_success_rate": sum(row["p29_first_survivor_success"] for row in group) / len(group),
            "mean_phase_a_false_survivors_before_lock": sum(row["phase_a_false_survivors_before_lock"] for row in group) / len(group),
            "mean_phase_b_false_survivors_before_lock": sum(row["phase_b_false_survivors_before_lock"] for row in group) / len(group),
            "mean_phase_a_cut_over_sqrt_n": sum(row["phase_a_cut_over_sqrt_n"] for row in group) / len(group),
        })
    overall = {
        "anchor_count": len(rows),
        "phase_a_success_rate": sum(row["phase_a_second_go_success"] for row in rows) / len(rows),
        "phase_b_success_rate": sum(row["phase_b_second_go_success"] for row in rows) / len(rows),
        "either_parent_success_rate": sum(row["either_parent_second_go_success"] for row in rows) / len(rows),
        "p29_success_rate": sum(row["p29_first_survivor_success"] for row in rows) / len(rows),
        "mean_phase_a_false_survivors_before_lock": sum(row["phase_a_false_survivors_before_lock"] for row in rows) / len(rows),
        "mean_phase_b_false_survivors_before_lock": sum(row["phase_b_false_survivors_before_lock"] for row in rows) / len(rows),
    }
    payload = {
        "test_id": "PN19/POST-TARGET-SECOND-GO-ROBUSTNESS/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "exploratory post-target; not part of the frozen confirmatory target",
        "grid": {
            "scales": list(SCALES),
            "anchors_per_scale": ANCHORS_PER_SCALE,
            "grid_step": GRID_STEP,
            "maximum_offset": MAX_OFFSET,
        },
        "interpretation_control": (
            "Phase A contains all prime children through approximately sqrt(N/2), so it is an intentionally strong "
            "partial sieve. High second-go success is useful operational behavior, not evidence of independence from established sieving."
        ),
        "overall": overall,
        "by_scale": summaries,
        "rows": rows,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"overall": overall, "by_scale": summaries}, indent=2))


if __name__ == "__main__":
    main()
