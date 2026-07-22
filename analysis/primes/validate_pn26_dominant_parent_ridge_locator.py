"""Independent PN26 reconstruction and truth validator."""

from __future__ import annotations

import bisect
import csv
import hashlib
import json
import math
import random
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN26_DOMINANT_PARENT_RIDGE_LOCATOR_PROTOCOL_v1_FROZEN.md"
FREEZE = HERE / "PN26_TARGET_FREEZE_MANIFEST.json"
PREDICTIONS = HERE / "PN26_DOMINANT_PARENT_RIDGE_PREDICTIONS.csv"
PRIMARY = HERE / "PN26_DOMINANT_PARENT_RIDGE_PRIMARY.json"
VALIDATED_ROWS = HERE / "PN26_DOMINANT_PARENT_RIDGE_VALIDATED_ROWS.csv"
VALIDATION = HERE / "PN26_DOMINANT_PARENT_RIDGE_VALIDATION.json"

TARGET_RANGES = (
    ("low", 71_000_000, 71_500_000, 26001),
    ("middle", 71_000_000_000, 71_000_500_000, 26002),
    ("high", 710_000_000_000, 710_000_500_000, 26003),
)
N_PER_RANGE = 2_000
MAX_OFFSET = 4_096
RANKED_CANDIDATES = 3
P29 = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def independent_primes(limit: int) -> list[int]:
    composite = bytearray(limit + 1)
    primes: list[int] = []
    for value in range(2, limit + 1):
        if not composite[value]:
            primes.append(value)
            if value <= limit // value:
                for multiple in range(value * value, limit + 1, value):
                    composite[multiple] = 1
    return primes


def independent_split(scale_anchor: int, primes: list[int]) -> tuple[list[int], list[int], float, float]:
    child_limit = math.isqrt(2 * scale_anchor)
    children = primes[: bisect.bisect_right(primes, child_limit)]
    logs = [math.log(value) for value in children]
    total = math.fsum(logs)
    running = 0.0
    best_index = 1
    best_error = float("inf")
    for index, weight in enumerate(logs[:-1], start=1):
        running += weight
        error = abs(running - total / 2.0)
        if error < best_error:
            best_error = error
            best_index = index
    phase_a = children[:best_index]
    phase_b = children[best_index:]
    e_a = 2.0 * math.fsum(math.log(value) for value in phase_a) / total
    return phase_a, phase_b, e_a, 2.0 - e_a


def mark_survivors(base: int, endpoint: int, children: list[int]) -> bytearray:
    survives = bytearray(b"\x01") * (endpoint - base + 1)
    for child in children:
        first_value = ((base + child - 1) // child) * child
        for value in range(first_value, endpoint + 1, child):
            survives[value - base] = 0
    return survives


def next_values(anchor: int, base: int, mask: bytearray, count: int) -> list[int]:
    output: list[int] = []
    for value in range(anchor + 1, min(anchor + MAX_OFFSET, base + len(mask) - 1) + 1):
        if mask[value - base]:
            output.append(value)
            if len(output) == count:
                return output
    raise RuntimeError(f"insufficient survivors above {anchor}")


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


def first_p29_candidates(anchor: int, count: int) -> list[int]:
    values: list[int] = []
    for candidate in range(anchor + 1, anchor + MAX_OFFSET + 1):
        if all(candidate % child for child in P29):
            values.append(candidate)
            if len(values) == count:
                return values
    raise RuntimeError("p29 control exhausted")


def first_odd_candidates(anchor: int, count: int) -> list[int]:
    candidate = anchor + 1
    if candidate % 2 == 0:
        candidate += 1
    return [candidate + 2 * index for index in range(count)]


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> list[float]:
    rate = successes / total
    denominator = 1.0 + z * z / total
    centre = (rate + z * z / (2 * total)) / denominator
    margin = z * math.sqrt(rate * (1.0 - rate) / total + z * z / (4 * total * total)) / denominator
    return [centre - margin, centre + margin]


def summarize(rows: list[dict], cohort: str) -> dict:
    group = rows if cohort == "pooled" else [row for row in rows if row["cohort"] == cohort]
    n = len(group)
    rank_counts = Counter(int(row["phase_a_rank_of_prime"]) for row in group)
    output = {"cohort": cohort, "n": n, "rank_counts": dict(sorted(rank_counts.items()))}
    for k in (1, 2, 3):
        successes = sum(int(row["phase_a_rank_of_prime"]) <= k for row in group)
        output[f"phase_a_top{k}_successes"] = successes
        output[f"phase_a_top{k}_rate"] = successes / n
        output[f"phase_a_top{k}_wilson95"] = wilson(successes, n)
        output[f"p29_top{k}_rate"] = statistics.fmean(int(row[f"p29_top{k}_hit"]) for row in group)
        output[f"odd_top{k}_rate"] = statistics.fmean(int(row[f"odd_top{k}_hit"]) for row in group)
    output["mean_phase_a_rank"] = statistics.fmean(int(row["phase_a_rank_of_prime"]) for row in group)
    output["max_phase_a_rank"] = max(int(row["phase_a_rank_of_prime"]) for row in group)
    return output


def main() -> None:
    for output in (VALIDATED_ROWS, VALIDATION):
        if output.exists():
            raise RuntimeError(f"refusing to overwrite {output.name}")

    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    primary = json.loads(PRIMARY.read_text(encoding="utf-8"))
    if sha256_file(PREDICTIONS) != primary["prediction_sha256"]:
        raise RuntimeError("sealed prediction CSV hash mismatch")
    if freeze["hashes"]["protocol_sha256"] != sha256_file(PROTOCOL):
        raise RuntimeError("protocol hash mismatch")

    with PREDICTIONS.open("r", encoding="utf-8", newline="") as handle:
        prediction_rows = list(csv.DictReader(handle))
    if len(prediction_rows) != N_PER_RANGE * len(TARGET_RANGES):
        raise RuntimeError("unexpected prediction row count")

    maximum_value = max(high for _, _, high, _ in TARGET_RANGES) + MAX_OFFSET
    primes = independent_primes(math.isqrt(maximum_value) + 2)
    prediction_lookup = {(row["cohort"], int(row["anchor"])): row for row in prediction_rows}
    validated: list[dict] = []
    checks: list[dict] = []

    for cohort, low, high, seed in TARGET_RANGES:
        expected_anchors = sorted(random.Random(seed).sample(range(low, high), N_PER_RANGE))
        phase_a, phase_b, e_a, e_b = independent_split(low, primes)
        base = low + 1
        endpoint = high + MAX_OFFSET
        a_mask = mark_survivors(base, endpoint, phase_a)
        truth_mask = mark_survivors(base, endpoint, primes)

        cohort_prediction_match = True
        cohort_truth_mr = True
        for anchor in expected_anchors:
            source = prediction_lookup[(cohort, anchor)]
            rebuilt = next_values(anchor, base, a_mask, RANKED_CANDIDATES)
            sealed = [int(source[f"phase_a_candidate_{index}"]) for index in range(1, 4)]
            cohort_prediction_match &= rebuilt == sealed

            actual_prime = next_values(anchor, base, truth_mask, 1)[0]
            cohort_truth_mr &= miller_rabin_64(actual_prime)
            rank = sum(
                bool(a_mask[value - base])
                for value in range(anchor + 1, actual_prime + 1)
            )
            if rank < 1:
                raise AssertionError("prime does not survive Phase A")
            p29 = first_p29_candidates(anchor, RANKED_CANDIDATES)
            odd = first_odd_candidates(anchor, RANKED_CANDIDATES)
            row = {
                "cohort": cohort,
                "anchor": anchor,
                "actual_next_prime": actual_prime,
                "actual_delta": actual_prime - anchor,
                "phase_a_candidate_1": sealed[0],
                "phase_a_candidate_2": sealed[1],
                "phase_a_candidate_3": sealed[2],
                "phase_a_rank_of_prime": rank,
                "phase_a_top1_hit": int(rank <= 1),
                "phase_a_top2_hit": int(rank <= 2),
                "phase_a_top3_hit": int(rank <= 3),
                "p29_candidate_1": p29[0],
                "p29_candidate_2": p29[1],
                "p29_candidate_3": p29[2],
                "odd_candidate_1": odd[0],
                "odd_candidate_2": odd[1],
                "odd_candidate_3": odd[2],
                "p29_top1_hit": int(actual_prime in p29[:1]),
                "p29_top2_hit": int(actual_prime in p29[:2]),
                "p29_top3_hit": int(actual_prime in p29[:3]),
                "odd_top1_hit": int(actual_prime in odd[:1]),
                "odd_top2_hit": int(actual_prime in odd[:2]),
                "odd_top3_hit": int(actual_prime in odd[:3]),
                "cross_rung_frame": float(source["cross_rung_frame"]),
                "phase_a_child_count": len(phase_a),
                "phase_b_child_count": len(phase_b),
                "teara_phase_a": e_a,
                "teara_phase_b": e_b,
            }
            validated.append(row)

        checks.extend([
            {"name": f"{cohort}: anchors reproduced", "passed": len(expected_anchors) == N_PER_RANGE},
            {"name": f"{cohort}: primary predictions reconstructed", "passed": cohort_prediction_match},
            {"name": f"{cohort}: actual primes pass Miller-Rabin", "passed": cohort_truth_mr},
            {"name": f"{cohort}: TE-ARA closes to two", "passed": abs((e_a + e_b) - 2.0) < 1e-14},
        ])

    with VALIDATED_ROWS.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(validated[0]))
        writer.writeheader()
        writer.writerows(validated)

    summaries = [summarize(validated, cohort) for cohort, *_ in TARGET_RANGES]
    pooled = summarize(validated, "pooled")
    summaries.append(pooled)
    frame_values = [row["cross_rung_frame"] for row in validated]
    frame_exact = all(value == 3.5 for value in frame_values)
    frame_variance = statistics.pvariance(frame_values)

    predictions = {
        "P1_top1_at_least_90_percent": pooled["phase_a_top1_rate"] >= 0.90,
        "P2_top2_at_least_99_percent": pooled["phase_a_top2_rate"] >= 0.99,
        "P3_top3_at_least_99_9_percent": pooled["phase_a_top3_rate"] >= 0.999,
        "P4_top3_beats_p29_by_50pp": (
            pooled["phase_a_top3_rate"] - pooled["p29_top3_rate"] >= 0.50
        ),
        "P5_frame_exact_zero_variance": frame_exact and frame_variance == 0.0,
        "P6_reconstruction_and_truth_checks": all(check["passed"] for check in checks),
    }
    predictive_passes = sum(predictions[key] for key in predictions if key.startswith(("P1", "P2", "P3", "P4")))
    if not predictions["P6_reconstruction_and_truth_checks"]:
        status = "IMPLEMENTATION FAILURE"
    elif all(predictions.values()):
        status = "STRONG DOMINANT-PARENT SUPPORT"
    elif predictive_passes:
        status = "PARTIAL DOMINANT-PARENT SUPPORT"
    else:
        status = "DYNAMIC NULL"

    checks.extend([
        {"name": "all 6,000 rows validated", "passed": len(validated) == 6_000},
        {"name": "all actual primes occur within frozen offset", "passed": all(row["actual_delta"] <= MAX_OFFSET for row in validated)},
        {"name": "protected 87-bit anchor unused", "passed": not primary["protected_87_bit_anchor_used"]},
        {"name": "3.5 frame exact and constant", "passed": frame_exact and frame_variance == 0.0},
    ])

    payload = {
        "test_id": "PN26/DOMINANT-PARENT-RIDGE-LOCATOR/VALIDATION/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "source_hashes": {
            "freeze_manifest_sha256": sha256_file(FREEZE),
            "prediction_csv_sha256": sha256_file(PREDICTIONS),
            "primary_json_sha256": sha256_file(PRIMARY),
            "validated_rows_sha256": sha256_file(VALIDATED_ROWS),
        },
        "registered_predictions": predictions,
        "summaries": summaries,
        "cross_rung_frame": {
            "value": 3.5,
            "variance": frame_variance,
            "exact_all_rows": frame_exact,
            "interpretation": "scale/context coordinate only; it cannot rank targets because it is constant",
        },
        "checks": checks,
        "checks_passed": sum(check["passed"] for check in checks),
        "checks_total": len(checks),
        "protected_87_bit_anchor_used": False,
        "scientific_boundary": (
            "Phase A is a strong partial sieve containing many prime children. Ranked visible states are not the "
            "same as arithmetic operation count, and exact primality still requires the omitted Phase B/full truth relation."
        ),
    }
    VALIDATION.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "registered_predictions": predictions,
        "pooled": pooled,
        "checks": f"{payload['checks_passed']}/{payload['checks_total']}",
    }, indent=2))


if __name__ == "__main__":
    main()
