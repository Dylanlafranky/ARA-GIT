"""Independent reconstruction and truth scoring for sealed PN34 predictions."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
FREEZE = HERE / "PN34_PROTOCOL_FREEZE_MANIFEST.json"
PREDICTIONS = HERE / "PN34_FILL_RANK_BUDGET_PREDICTIONS.csv"
PRIMARY = HERE / "PN34_FILL_RANK_BUDGET_PRIMARY.json"
ROWS_OUT = HERE / "PN34_FILL_RANK_BUDGET_VALIDATED_ROWS.csv"
RESULTS_OUT = HERE / "PN34_FILL_RANK_BUDGET_RESULTS.json"
VALIDATION_OUT = HERE / "PN34_FILL_RANK_BUDGET_VALIDATION.json"

TARGET_RANGES = (
    ("low", 89_000_000, 89_500_000),
    ("middle", 89_000_000_000, 89_000_500_000),
    ("high", 8_900_000_000_000, 8_900_000_500_000),
)
MAX_OFFSET = 4_096


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def odd_sieve(limit: int) -> list[int]:
    if limit < 2:
        return []
    flags = bytearray(b"\x01") * ((limit // 2) + 1)
    flags[0] = 0
    for odd in range(3, math.isqrt(limit) + 1, 2):
        if flags[odd // 2]:
            start = odd * odd
            flags[start // 2 :: odd] = b"\x00" * (((len(flags) - 1 - start // 2) // odd) + 1)
    return [2] + [2 * index + 1 for index in range(1, len(flags)) if flags[index] and 2 * index + 1 <= limit]


def independent_parent(scale_anchor: int, primes: list[int]) -> dict:
    child_limit = math.isqrt(2 * scale_anchor)
    children = [prime for prime in primes if prime <= child_limit]
    total = math.fsum(math.log(prime) for prime in children)
    target = total / 2.0
    running = 0.0
    best_index = 1
    best_error = float("inf")
    for index, prime in enumerate(children[:-1], start=1):
        running += math.log(prime)
        error = abs(running - target)
        if error < best_error:
            best_error = error
            best_index = index
    phase_a = children[:best_index]
    phase_b = children[best_index:]
    log_r_b = math.fsum(-math.log1p(-1.0 / prime) for prime in phase_b)
    log_d_a = math.fsum(-math.log1p(-1.0 / prime) for prime in phase_a)
    r_b = math.exp(log_r_b)
    p1 = 1.0 / r_b
    return {
        "phase_a": phase_a,
        "phase_b": phase_b,
        "phase_a_last_child": phase_a[-1],
        "phase_b_first_child": phase_b[0],
        "remaining_fill_ratio": r_b,
        "remaining_fill_x": 2.0 * log_r_b / math.log(2.0),
        "predicted": [p1, 1.0 - (1.0 - p1) ** 2, 1.0 - (1.0 - p1) ** 3],
        "conditional_pnt_top1": min(1.0, math.exp(log_d_a) / math.log(scale_anchor)),
    }


def survivor_mask(base: int, endpoint: int, children: list[int]) -> bytearray:
    mask = bytearray(b"\x01") * (endpoint - base + 1)
    for child in children:
        first = (-base) % child
        if first >= len(mask):
            continue
        for index in range(first, len(mask), child):
            mask[index] = 0
    return mask


def segmented_prime_mask(base: int, endpoint: int, primes: list[int]) -> bytearray:
    mask = bytearray(b"\x01") * (endpoint - base + 1)
    for prime in primes:
        if prime * prime > endpoint:
            break
        first_value = max(prime * prime, ((base + prime - 1) // prime) * prime)
        for value in range(first_value, endpoint + 1, prime):
            mask[value - base] = 0
    return mask


def is_prime_64(value: int) -> bool:
    if value < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for prime in small:
        if value % prime == 0:
            return value == prime
    d = value - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    for base in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if base % value == 0:
            continue
        x = pow(base, d, value)
        if x in (1, value - 1):
            continue
        for _ in range(s - 1):
            x = (x * x) % value
            if x == value - 1:
                break
        else:
            return False
    return True


def wilson(successes: int, trials: int, z: float = 1.959963984540054) -> list[float]:
    p = successes / trials
    z2 = z * z
    denominator = 1.0 + z2 / trials
    centre = (p + z2 / (2.0 * trials)) / denominator
    half = z * math.sqrt((p * (1.0 - p) + z2 / (4.0 * trials)) / trials) / denominator
    return [centre - half, centre + half]


def log_loss(labels: list[int], predictions: list[float]) -> float:
    eps = 1e-15
    return sum(
        -(label * math.log(min(1 - eps, max(eps, pred))) + (1 - label) * math.log(min(1 - eps, max(eps, 1 - pred))))
        for label, pred in zip(labels, predictions)
    ) / len(labels)


def brier(labels: list[int], predictions: list[float]) -> float:
    return sum((label - pred) ** 2 for label, pred in zip(labels, predictions)) / len(labels)


def main() -> None:
    for path in (ROWS_OUT, RESULTS_OUT, VALIDATION_OUT):
        if path.exists():
            raise RuntimeError(f"refusing to overwrite {path.name}")

    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    primary = json.loads(PRIMARY.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {
        "prediction_hash_matches_primary": sha256(PREDICTIONS) == primary["prediction_sha256"],
        "freeze_hash_matches_primary": sha256(FREEZE) == primary["protocol_freeze_sha256"],
        "row_count_is_6000": primary["row_count"] == 6000,
        "primary_truth_fields_absent": primary["truth_fields_present"] is False,
        "individual_classifier_not_registered": primary["individual_candidate_classifier_registered"] is False,
    }
    for name, expected in freeze["files"].items():
        checks[f"frozen_{name}_unchanged"] = sha256(HERE / name) == expected

    with PREDICTIONS.open(encoding="utf-8", newline="") as handle:
        predictions = list(csv.DictReader(handle))
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in predictions:
        grouped[row["cohort"]].append(row)

    max_prime_needed = math.isqrt(2 * max(low for _, low, _ in TARGET_RANGES)) + 10
    primes = odd_sieve(max_prime_needed)
    validated: list[dict] = []
    cohort_results: list[dict] = []
    all_labels: list[int] = []
    all_fill: list[float] = []
    all_flat: list[float] = []
    all_pnt: list[float] = []

    for cohort, low, high in TARGET_RANGES:
        rows = grouped[cohort]
        parent = independent_parent(low, primes)
        base = low + 1
        endpoint = high + MAX_OFFSET
        phase_a_mask = survivor_mask(base, endpoint, parent["phase_a"])
        truth_mask = segmented_prime_mask(base, endpoint, primes)
        reconstruction_ok = True
        prior_ok = True
        hits = [0, 0, 0]
        rank_counts = [0, 0, 0, 0]

        for row in rows:
            anchor = int(row["anchor"])
            candidates: list[int] = []
            for value in range(anchor + 1, anchor + MAX_OFFSET + 1):
                if phase_a_mask[value - base]:
                    candidates.append(value)
                    if len(candidates) == 3:
                        break
            sealed = [int(row[f"candidate_{index}"]) for index in (1, 2, 3)]
            reconstruction_ok &= candidates == sealed
            prior_ok &= (
                abs(float(row["remaining_fill_ratio"]) - parent["remaining_fill_ratio"]) < 1e-12
                and abs(float(row["remaining_fill_x"]) - parent["remaining_fill_x"]) < 1e-12
                and all(abs(float(row[f"predicted_top{index}"]) - parent["predicted"][index - 1]) < 1e-12 for index in (1, 2, 3))
            )

            actual = None
            for value in range(anchor + 1, anchor + MAX_OFFSET + 1):
                if truth_mask[value - base]:
                    actual = value
                    break
            if actual is None:
                raise RuntimeError(f"no truth prime within offset for {anchor}")
            rank = sealed.index(actual) + 1 if actual in sealed else 4
            for depth in (1, 2, 3):
                hit = int(rank <= depth)
                hits[depth - 1] += hit
            rank_counts[rank - 1] += 1
            label = int(rank == 1)
            all_labels.append(label)
            all_fill.append(parent["predicted"][0])
            all_flat.append(float(row["flat_pn26_top1"]))
            all_pnt.append(parent["conditional_pnt_top1"])
            validated.append(
                {
                    **row,
                    "actual_next_prime": actual,
                    "actual_delta": actual - anchor,
                    "actual_rank": rank if rank <= 3 else ">3",
                    "top1_hit": int(rank <= 1),
                    "top2_hit": int(rank <= 2),
                    "top3_hit": int(rank <= 3),
                }
            )

        checks[f"{cohort}_candidate_reconstruction"] = reconstruction_ok
        checks[f"{cohort}_prior_reconstruction"] = prior_ok
        sample_actuals = [int(row["actual_next_prime"]) for row in validated if row["cohort"] == cohort][::80]
        checks[f"{cohort}_miller_rabin_prime_spots"] = all(is_prime_64(value) for value in sample_actuals)

        observed = [hit / len(rows) for hit in hits]
        errors = [abs(obs - pred) for obs, pred in zip(observed, parent["predicted"])]
        cohort_results.append(
            {
                "cohort": cohort,
                "scale_anchor": low,
                "rows": len(rows),
                "phase_a_count": len(parent["phase_a"]),
                "phase_b_count": len(parent["phase_b"]),
                "remaining_fill_ratio": parent["remaining_fill_ratio"],
                "remaining_fill_x": parent["remaining_fill_x"],
                "predicted_top1": parent["predicted"][0],
                "predicted_top2": parent["predicted"][1],
                "predicted_top3": parent["predicted"][2],
                "observed_top1": observed[0],
                "observed_top2": observed[1],
                "observed_top3": observed[2],
                "absolute_errors": errors,
                "wilson95": [wilson(hit, len(rows)) for hit in hits],
                "rank_counts_1_2_3_over3": rank_counts,
                "conditional_pnt_top1": parent["conditional_pnt_top1"],
                "calibration_passes": [errors[0] <= 0.015, errors[1] <= 0.005, errors[2] <= 0.0015],
                "budget_passes": [observed[1] >= 0.99, observed[2] >= 0.999],
            }
        )

    predicted_order = [row["cohort"] for row in sorted(cohort_results, key=lambda row: row["predicted_top1"])]
    observed_order = [row["cohort"] for row in sorted(cohort_results, key=lambda row: row["observed_top1"])]
    direction_pass = predicted_order == observed_order
    calibration_pass = all(all(row["calibration_passes"]) for row in cohort_results)
    budget_pass = all(all(row["budget_passes"]) for row in cohort_results)
    checks["registered_calibration_thresholds_pass"] = calibration_pass
    checks["registered_rank_budgets_pass"] = budget_pass
    checks["registered_scale_direction_pass"] = direction_pass
    checks["all_actual_primes_spot_checked"] = all(value for key, value in checks.items() if key.endswith("miller_rabin_prime_spots"))

    verdict = (
        "SUPPORTED POPULATION RANK-BUDGET CROSSWALK"
        if calibration_pass and budget_pass and direction_pass and all(checks.values())
        else "PARTIAL OR NULL — SEE REGISTERED ENDPOINTS"
    )
    benchmarks = {
        "fill_prior": {"brier": brier(all_labels, all_fill), "log_loss": log_loss(all_labels, all_fill)},
        "flat_pn26_prior": {"brier": brier(all_labels, all_flat), "log_loss": log_loss(all_labels, all_flat)},
        "conditional_pnt_prior": {"brier": brier(all_labels, all_pnt), "log_loss": log_loss(all_labels, all_pnt)},
    }
    results = {
        "test_id": "PN34/FILL-RANK-BUDGET/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "cohorts": cohort_results,
        "predicted_scale_order": predicted_order,
        "observed_scale_order": observed_order,
        "direction_pass": direction_pass,
        "benchmark_top1": benchmarks,
        "individual_candidate_classifier_tested": False,
        "scientific_boundary": (
            "The fill coordinate calibrates a population rank budget. Because it is constant inside each cohort, "
            "it supplies no within-cohort rule for identifying which first quiet candidate is composite."
        ),
    }

    with ROWS_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(validated[0]))
        writer.writeheader()
        writer.writerows(validated)
    RESULTS_OUT.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    validation = {
        "test_id": "PN34/FILL-RANK-BUDGET/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "passed": sum(checks.values()),
        "total": len(checks),
        "all_passed": all(checks.values()),
        "validated_rows_sha256": sha256(ROWS_OUT),
        "results_sha256": sha256(RESULTS_OUT),
    }
    VALIDATION_OUT.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"results": results, "validation": validation}, indent=2))


if __name__ == "__main__":
    main()
