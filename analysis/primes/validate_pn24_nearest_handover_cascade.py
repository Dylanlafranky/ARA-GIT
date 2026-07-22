"""Independent validation for PN24 nearest-handover outputs."""

from __future__ import annotations

import bisect
import csv
import json
import math
import random
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "PN24_NEAREST_HANDOVER_CASCADE_RESULTS.json"
ANCHORS = HERE / "PN24_NEAREST_HANDOVER_CASCADE_ANCHORS.csv"
EVENTS = HERE / "PN24_NEAREST_HANDOVER_CASCADE_EVENTS.csv"
RUNGS = HERE / "PN24_NEAREST_HANDOVER_CASCADE_RUNGS.csv"
OUTPUT = HERE / "PN24_NEAREST_HANDOVER_CASCADE_VALIDATION.json"
MR_BASES = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)


def prime_test(n: int) -> bool:
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in MR_BASES:
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def prime_table(limit: int) -> list[int]:
    flags = bytearray(b"\x01") * (limit + 1)
    flags[:2] = b"\x00\x00"
    for p in range(2, math.isqrt(limit) + 1):
        if flags[p]:
            flags[p * p : limit + 1 : p] = b"\x00" * (((limit - p * p) // p) + 1)
    return [n for n, flag in enumerate(flags) if flag]


def direct_next_prime(n: int) -> int:
    value = n + 1
    if value <= 2:
        return 2
    if value % 2 == 0:
        value += 1
    while not prime_test(value):
        value += 2
    return value


def direct_survives(value: int, gates: list[int]) -> bool:
    return all(value % p != 0 for p in gates)


def direct_pair(anchor: int, gates: list[int]) -> tuple[int, int]:
    low = anchor
    while not direct_survives(low, gates):
        low -= 1
    high = anchor + 1
    while not direct_survives(high, gates):
        high += 1
    return low, high


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def record(checks: list[dict], name: str, passed: bool, detail: str = "") -> None:
    checks.append({"name": name, "pass": bool(passed), "detail": detail})


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError(f"refusing to overwrite {OUTPUT.name}")
    saved = json.loads(RESULTS.read_text(encoding="utf-8"))
    anchors = read_csv(ANCHORS)
    events = read_csv(EVENTS)
    rungs = read_csv(RUNGS)
    gate_primes = prime_table(1_000_000)
    checks: list[dict] = []

    expected_sample = sorted(random.Random(240722).sample(range(4_000_000_000, 4_001_000_000), 2_000))
    actual_sample = sorted(int(row["anchor"]) for row in anchors if row["cohort"] == "sample")
    record(checks, "deterministic sample reproduced", actual_sample == expected_sample)
    record(checks, "anchor row count", len(anchors) == 2007, str(len(anchors)))
    record(checks, "all anchors below one trillion", all(int(row["anchor"]) < 10**12 for row in anchors))
    record(checks, "protected anchor flag false", saved["data"]["protected_87_bit_anchor_used"] is False)

    truth_failures = []
    pair_failures = []
    for row in anchors:
        anchor = int(row["anchor"])
        final = int(row["final_candidate"])
        truth = direct_next_prime(anchor)
        if final != truth or int(row["true_next_prime"]) != truth:
            truth_failures.append((anchor, final, truth))
        low, high = direct_pair(anchor, [2, 7])
        if low != int(row["initial_lower"]) or high != int(row["initial_upper"]):
            pair_failures.append((anchor, low, high))
    record(checks, "all final candidates equal independently scanned next primes", not truth_failures, str(truth_failures[:3]))
    record(checks, "all base nearest pairs reproduced", not pair_failures, str(pair_failures[:3]))

    rung_failures = []
    for row in rungs:
        anchor = int(row["anchor"])
        gates = [int(value) for value in row["gates"].split("|")]
        low, high = direct_pair(anchor, gates)
        if low != int(row["lower"]) or high != int(row["candidate"]):
            rung_failures.append((anchor, row["rung"], low, high))
        truth = direct_next_prime(anchor)
        if int(row["location_error"]) != truth - high:
            rung_failures.append((anchor, row["rung"], "location_error"))
    record(checks, "all fixed-rung nearest candidates reproduced", not rung_failures, str(rung_failures[:3]))

    by_anchor: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_anchor[int(row["anchor"])].append(row)
    event_failures = []
    for anchor_row in anchors:
        anchor = int(anchor_row["anchor"])
        current = int(anchor_row["initial_upper"])
        processed = [2, 7]
        event_path = sorted(by_anchor[anchor], key=lambda row: int(row["event_index"]))
        previous_gate = 0
        for event in event_path:
            gate = int(event["gate"])
            old = int(event["old_candidate"])
            new = int(event["new_candidate"])
            if old != current or old % gate != 0 or gate <= previous_gate:
                event_failures.append((anchor, "bad collision", gate, old, current))
            # Add every prime gate between the old frontier and this event gate.
            lo = bisect.bisect_right(gate_primes, previous_gate)
            hi = bisect.bisect_right(gate_primes, gate)
            for p in gate_primes[lo:hi]:
                if p in (2, 7):
                    continue
                processed.append(p)
            low, high = direct_pair(anchor, processed)
            if high != new or low != int(event["lower_child_after_gate"]):
                event_failures.append((anchor, "bad nearest update", gate, low, high, new))
            current = new
            previous_gate = gate
        if current != int(anchor_row["final_candidate"]):
            event_failures.append((anchor, "path terminal mismatch", current))
        if len(event_path) != int(anchor_row["handover_events"]):
            event_failures.append((anchor, "event count mismatch"))
    record(checks, "every handover collision and nearest update reproduced", not event_failures, str(event_failures[:3]))

    sample_rows = [row for row in anchors if row["cohort"] == "sample"]
    within_three_states = sum(int(row["candidate_states"]) <= 3 for row in sample_rows) / len(sample_rows)
    within_three_events = sum(int(row["handover_events"]) <= 3 for row in sample_rows) / len(sample_rows)
    record(
        checks,
        "sample within-three-candidate rate reproduced",
        abs(within_three_states - saved["cascade_sample"]["within_three_candidate_states_rate"]) < 1e-15,
        str(within_three_states),
    )
    record(
        checks,
        "sample within-three-handover rate reproduced",
        abs(within_three_events - saved["cascade_sample"]["within_three_handover_events_rate"]) < 1e-15,
        str(within_three_events),
    )
    record(
        checks,
        "frozen 90 percent compact threshold correctly failed",
        within_three_states < 0.90 and saved["decision"]["compact_three_candidate_threshold_passed"] is False,
    )
    record(
        checks,
        "visible events not conflated with gate work",
        saved["cascade_sample"]["median_handover_events"] == 2.0
        and saved["cascade_sample"]["median_total_nonbase_gate_crossings"] > 6000,
    )

    passed = sum(check["pass"] for check in checks)
    payload = {
        "validation_id": "PN24/INDEPENDENT-VALIDATION/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if payload["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
