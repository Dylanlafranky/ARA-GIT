"""PN24 development test of the nearest-child handover cascade.

The protected 87-bit anchor is deliberately absent.  This script uses only
previously opened scale anchors and a deterministic sample from the opened
PN19 interval.
"""

from __future__ import annotations

import bisect
import csv
import json
import math
import random
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL = "PN24_NEAREST_HANDOVER_CASCADE_PROTOCOL_v1_FROZEN.md"
RESULTS = HERE / "PN24_NEAREST_HANDOVER_CASCADE_RESULTS.json"
ANCHORS_CSV = HERE / "PN24_NEAREST_HANDOVER_CASCADE_ANCHORS.csv"
EVENTS_CSV = HERE / "PN24_NEAREST_HANDOVER_CASCADE_EVENTS.csv"
RUNGS_CSV = HERE / "PN24_NEAREST_HANDOVER_CASCADE_RUNGS.csv"

SCALE_ANCHORS = (
    100_000_000,
    1_000_000_000,
    10_000_000_000,
    100_000_000_000,
    400_000_000_000,
    700_000_000_000,
    900_000_000_000,
)
SAMPLE_LOW = 4_000_000_000
SAMPLE_HIGH = 4_001_000_000
SAMPLE_SIZE = 2_000
SAMPLE_SEED = 240722

FIXED_RUNGS = (
    ("odd", (2,)),
    ("mod14", (2, 7)),
    ("through_3", (2, 3, 7)),
    ("through_5", (2, 3, 5, 7)),
    ("through_11", (2, 3, 5, 7, 11)),
    ("through_13", (2, 3, 5, 7, 11, 13)),
    ("through_17", (2, 3, 5, 7, 11, 13, 17)),
)

# Deterministic Miller-Rabin bases for unsigned 64-bit integers.
MR_BASES = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)


def sieve_primes(limit: int) -> list[int]:
    flags = bytearray(b"\x01") * (limit + 1)
    flags[:2] = b"\x00\x00"
    for p in range(2, math.isqrt(limit) + 1):
        if flags[p]:
            flags[p * p : limit + 1 : p] = b"\x00" * (((limit - p * p) // p) + 1)
    return [n for n, flag in enumerate(flags) if flag]


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in small:
        if n % p == 0:
            return n == p
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    for a in MR_BASES:
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


def next_prime(n: int) -> int:
    candidate = n + 1
    if candidate <= 2:
        return 2
    if candidate % 2 == 0:
        candidate += 1
    while not is_prime(candidate):
        candidate += 2
    return candidate


def survives(value: int, gates: list[int] | tuple[int, ...]) -> bool:
    return all(value % p for p in gates)


def nearest_pair(anchor: int, gates: list[int] | tuple[int, ...]) -> tuple[int, int]:
    lower = anchor
    while not survives(lower, gates):
        lower -= 1
    upper = anchor + 1
    while not survives(upper, gates):
        upper += 1
    return lower, upper


def first_upper_after(start: int, gates: list[int]) -> int:
    candidate = start + 1
    while not survives(candidate, gates):
        candidate += 1
    return candidate


def count_survivor_candidates(first: int, last: int, gates: tuple[int, ...]) -> int:
    return sum(survives(value, gates) for value in range(first, last + 1))


def cascade(anchor: int, all_primes: list[int]) -> tuple[dict, list[dict]]:
    missing = [p for p in all_primes if p not in (2, 7)]
    lower, current = nearest_pair(anchor, (2, 7))
    initial_lower = lower
    initial_upper = current
    gate_frontier = 0  # missing[:gate_frontier] have been processed.
    events: list[dict] = []
    total_gate_crossings = 0

    while True:
        if is_prime(current):
            proof_frontier = bisect.bisect_right(missing, math.isqrt(current))
            if proof_frontier < gate_frontier:
                raise AssertionError("proof frontier moved backwards")
            total_gate_crossings += proof_frontier - gate_frontier
            gate_frontier = proof_frontier
            break

        factor_index = None
        for index in range(gate_frontier, len(missing)):
            p = missing[index]
            if p * p > current:
                break
            if current % p == 0:
                factor_index = index
                break
        if factor_index is None:
            raise AssertionError(f"composite candidate {current} has no unprocessed factor")

        p = missing[factor_index]
        gates_crossed_this_event = factor_index - gate_frontier + 1
        silent_before_event = gates_crossed_this_event - 1
        total_gate_crossings += gates_crossed_this_event
        gate_frontier = factor_index + 1
        processed = [2, 7] + missing[:gate_frontier]
        new_lower, direct_upper = nearest_pair(anchor, processed)
        new_candidate = first_upper_after(current, processed)
        if new_candidate != direct_upper:
            raise AssertionError("incremental and direct upper survivor disagree")
        if current % p != 0:
            raise AssertionError("named handover gate does not kill current candidate")
        events.append({
            "anchor": anchor,
            "event_index": len(events) + 1,
            "gate": p,
            "old_candidate": current,
            "old_delta": current - anchor,
            "new_candidate": new_candidate,
            "new_delta": new_candidate - anchor,
            "candidate_shift": new_candidate - current,
            "lower_child_after_gate": new_lower,
            "lower_delta_after_gate": anchor - new_lower,
            "upper_child_after_gate": direct_upper,
            "gates_crossed_this_event": gates_crossed_this_event,
            "silent_gates_before_event": silent_before_event,
            "processed_nonbase_gate_count": gate_frontier,
        })
        lower = new_lower
        current = new_candidate

    final_delta = current - anchor
    anti_pairs = {(1, 13), (3, 11), (5, 9)}
    residue_pair = tuple(sorted((initial_lower % 14, initial_upper % 14)))
    result = {
        "anchor": anchor,
        "initial_lower": initial_lower,
        "initial_upper": initial_upper,
        "initial_lower_residue_mod14": initial_lower % 14,
        "initial_upper_residue_mod14": initial_upper % 14,
        "initial_pair_is_mod14_antipair": residue_pair in anti_pairs,
        "initial_backward_delta": anchor - initial_lower,
        "initial_forward_delta": initial_upper - anchor,
        "final_candidate": current,
        "final_delta": final_delta,
        "initial_to_final_delta_ratio": (initial_upper - anchor) / final_delta,
        "handover_events": len(events),
        "candidate_states": len(events) + 1,
        "total_nonbase_gate_crossings": total_gate_crossings,
        "silent_gate_crossings": total_gate_crossings - len(events),
        "final_gate_frontier": missing[gate_frontier - 1] if gate_frontier else None,
    }
    return result, events


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("empty percentile")
    position = (len(ordered) - 1) * fraction
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return float(ordered[low])
    weight = position - low
    return float(ordered[low] * (1.0 - weight) + ordered[high] * weight)


def fixed_rung_rows(anchors: list[int], truth: dict[int, int]) -> tuple[list[dict], list[dict]]:
    summaries: list[dict] = []
    details: list[dict] = []
    for name, gates in FIXED_RUNGS:
        errors: list[int] = []
        inspections: list[int] = []
        exact = 0
        prime = 0
        for anchor in anchors:
            lower, candidate = nearest_pair(anchor, gates)
            target = truth[anchor]
            error = target - candidate
            if error < 0:
                raise AssertionError("wheel candidate passed the next prime")
            exact += candidate == target
            prime += is_prime(candidate)
            errors.append(error)
            inspection_count = count_survivor_candidates(candidate, target, gates)
            inspections.append(inspection_count)
            details.append({
                "anchor": anchor,
                "rung": name,
                "gates": "|".join(map(str, gates)),
                "lower": lower,
                "candidate": candidate,
                "candidate_delta": candidate - anchor,
                "true_next_prime": target,
                "true_delta": target - anchor,
                "location_error": error,
                "candidate_is_prime": is_prime(candidate),
                "exact_next_prime": candidate == target,
                "survivor_candidates_through_prime": inspection_count,
            })
        summaries.append({
            "rung": name,
            "gates": list(gates),
            "n": len(anchors),
            "exact_count": exact,
            "exact_rate": exact / len(anchors),
            "candidate_prime_count": prime,
            "candidate_prime_rate": prime / len(anchors),
            "mean_location_error": statistics.fmean(errors),
            "median_location_error": statistics.median(errors),
            "mean_survivor_candidates_through_prime": statistics.fmean(inspections),
            "median_survivor_candidates_through_prime": statistics.median(inspections),
        })
    return summaries, details


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def summarize_cascade(rows: list[dict]) -> dict:
    event_counts = Counter(row["handover_events"] for row in rows)
    states = [row["candidate_states"] for row in rows]
    events = [row["handover_events"] for row in rows]
    ratios = [row["initial_to_final_delta_ratio"] for row in rows]
    gates = [row["total_nonbase_gate_crossings"] for row in rows]
    silent = [row["silent_gate_crossings"] for row in rows]
    n = len(rows)
    within_three = sum(value <= 3 for value in states) / n
    if within_three >= 0.90:
        verdict = "STRONG COMPACT SUPPORT"
    elif within_three >= 0.50:
        verdict = "PARTIAL STRUCTURAL SUPPORT"
    else:
        verdict = "COMPACT NULL"
    return {
        "n": n,
        "handover_event_distribution": {str(k): event_counts[k] for k in sorted(event_counts)},
        "zero_handover_rate": event_counts[0] / n,
        "within_one_candidate_state_rate": sum(value <= 1 for value in states) / n,
        "within_two_candidate_states_rate": sum(value <= 2 for value in states) / n,
        "within_three_candidate_states_rate": within_three,
        "within_three_handover_events_rate": sum(value <= 3 for value in events) / n,
        "more_than_three_handover_events_rate": sum(value > 3 for value in events) / n,
        "mean_handover_events": statistics.fmean(events),
        "median_handover_events": statistics.median(events),
        "p90_handover_events": percentile(events, 0.90),
        "max_handover_events": max(events),
        "mean_candidate_states": statistics.fmean(states),
        "mean_initial_to_final_delta_ratio": statistics.fmean(ratios),
        "median_initial_to_final_delta_ratio": statistics.median(ratios),
        "mean_total_nonbase_gate_crossings": statistics.fmean(gates),
        "median_total_nonbase_gate_crossings": statistics.median(gates),
        "mean_silent_gate_crossings": statistics.fmean(silent),
        "median_silent_gate_crossings": statistics.median(silent),
        "verdict_against_frozen_thresholds": verdict,
    }


def main() -> None:
    for output in (RESULTS, ANCHORS_CSV, EVENTS_CSV, RUNGS_CSV):
        if output.exists():
            raise RuntimeError(f"refusing to overwrite {output.name}")

    rng = random.Random(SAMPLE_SEED)
    sampled = sorted(rng.sample(range(SAMPLE_LOW, SAMPLE_HIGH), SAMPLE_SIZE))
    all_anchors = list(SCALE_ANCHORS) + sampled
    max_needed = math.isqrt(max(all_anchors) + 10_000) + 100
    primes = sieve_primes(max_needed)
    truth = {anchor: next_prime(anchor) for anchor in all_anchors}

    rung_summaries, rung_details = fixed_rung_rows(all_anchors, truth)
    anchor_rows: list[dict] = []
    event_rows: list[dict] = []
    for cohort, anchors in (("scale", list(SCALE_ANCHORS)), ("sample", sampled)):
        for anchor in anchors:
            row, events = cascade(anchor, primes)
            row["cohort"] = cohort
            row["true_next_prime"] = truth[anchor]
            row["true_delta"] = truth[anchor] - anchor
            row["final_matches_truth"] = row["final_candidate"] == truth[anchor]
            anchor_rows.append(row)
            for event in events:
                event["cohort"] = cohort
                event_rows.append(event)

    if not all(row["final_matches_truth"] for row in anchor_rows):
        raise AssertionError("cascade did not recover every independently calculated next prime")

    scale_rows = [row for row in anchor_rows if row["cohort"] == "scale"]
    sample_rows = [row for row in anchor_rows if row["cohort"] == "sample"]
    all_summary = summarize_cascade(anchor_rows)
    sample_summary = summarize_cascade(sample_rows)
    scale_summary = summarize_cascade(scale_rows)
    distinct_truth = len(set(truth[anchor] for anchor in sampled))

    write_csv(ANCHORS_CSV, anchor_rows)
    write_csv(EVENTS_CSV, event_rows)
    write_csv(RUNGS_CSV, rung_details)

    payload = {
        "test_id": "PN24/NEAREST-HANDOVER-CASCADE/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "protocol": PROTOCOL,
        "status": sample_summary["verdict_against_frozen_thresholds"],
        "data": {
            "scale_anchors": list(SCALE_ANCHORS),
            "sample_interval": [SAMPLE_LOW, SAMPLE_HIGH],
            "sample_size": SAMPLE_SIZE,
            "sample_seed": SAMPLE_SEED,
            "sample_distinct_next_prime_labels": distinct_truth,
            "sample_rows_are_independent": False,
            "protected_87_bit_anchor_used": False,
        },
        "fixed_rungs_all_anchors": rung_summaries,
        "cascade_all_anchors": all_summary,
        "cascade_sample": sample_summary,
        "cascade_scale_anchors": scale_summary,
        "scale_anchor_paths": scale_rows,
        "decision": {
            "all_final_candidates_match_independent_next_prime": True,
            "compact_three_candidate_threshold_passed": (
                sample_summary["within_three_candidate_states_rate"] >= 0.90
            ),
            "interpretation": (
                "The cascade is an exact monotone incremental-wheel/trial-division crosswalk. "
                "Its visible handover count measures candidate lineage, not arithmetic cost: silent prime gates "
                "still have to be crossed to identify collisions and prove the terminal candidate."
            ),
            "new_prime_theorem_supported": False,
            "constant_operation_prime_locator_supported": False,
        },
    }
    RESULTS.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "sample": sample_summary,
        "scale_anchors": scale_rows,
        "fixed_rungs": rung_summaries,
    }, indent=2))


if __name__ == "__main__":
    main()
