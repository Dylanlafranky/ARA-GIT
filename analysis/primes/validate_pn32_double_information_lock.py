"""Independently validate PN32 arithmetic, labels, permutations, and controls."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN32_DOUBLE_INFORMATION_LOCK_PROTOCOL_v1_FROZEN.md"
PROTOCOL_FREEZE = HERE / "PN32_PROTOCOL_FREEZE_MANIFEST.json"
COORDINATES = HERE / "PN32_DOUBLE_INFORMATION_LOCK_FROZEN_COORDINATES.csv"
BROKEN_MAPS = HERE / "PN32_RELATION_BROKEN_PARENT_INDEXES.json"
COORDINATE_FREEZE = HERE / "PN32_COORDINATE_FREEZE_MANIFEST.json"
SCORED = HERE / "PN32_DOUBLE_INFORMATION_LOCK_SCORED.csv"
RESULTS = HERE / "PN32_DOUBLE_INFORMATION_LOCK_RESULTS.json"
OUTPUT = HERE / "PN32_DOUBLE_INFORMATION_LOCK_VALIDATION.json"
WAVES = (3, 5, 9, 11, 13)
PERMUTATIONS = 10_000


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def order(number: int) -> tuple[int, ...] | None:
    values: list[tuple[Fraction, int]] = []
    for wave in WAVES:
        remainder = number % wave
        distance = Fraction(0) if remainder == 0 else Fraction(2) - Fraction(2 * remainder, wave)
        values.append((distance, wave))
    if len({distance for distance, _ in values}) != len(WAVES):
        return None
    return tuple(wave for _, wave in sorted(values))


def order_text(value: tuple[int, ...]) -> str:
    return ">".join(str(item) for item in value)


def relative(child: tuple[int, ...], parent: tuple[int, ...]) -> str:
    ranks = {wave: rank + 1 for rank, wave in enumerate(parent)}
    return "-".join(str(ranks[wave]) for wave in child)


def alternate_is_prime(number: int) -> bool:
    return number >= 2 and all(number % divisor for divisor in range(2, math.isqrt(number) + 1))


def total_variation(positive: list[str], negative: list[str]) -> float:
    p = Counter(positive)
    n = Counter(negative)
    return 0.5 * sum(
        abs(p[key] / len(positive) - n[key] / len(negative))
        for key in set(p) | set(n)
    )


def categorical_p(positive: list[str], negative: list[str], seed: int) -> tuple[float, float, float]:
    combined = positive + negative
    positive_n = len(positive)
    observed = total_variation(positive, negative)
    rng = random.Random(seed)
    indices = list(range(len(combined)))
    at_or_above = 0
    null_sum = 0.0
    for _ in range(PERMUTATIONS):
        chosen = set(rng.sample(indices, positive_n))
        perm_positive = [value for index, value in enumerate(combined) if index in chosen]
        perm_negative = [value for index, value in enumerate(combined) if index not in chosen]
        statistic = total_variation(perm_positive, perm_negative)
        null_sum += statistic
        at_or_above += statistic >= observed
    return observed, null_sum / PERMUTATIONS, (at_or_above + 1) / (PERMUTATIONS + 1)


def check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError(f"refusing to overwrite {OUTPUT.name}")
    protocol_freeze = json.loads(PROTOCOL_FREEZE.read_text(encoding="utf-8"))
    coordinate_freeze = json.loads(COORDINATE_FREEZE.read_text(encoding="utf-8"))
    controls = json.loads(BROKEN_MAPS.read_text(encoding="utf-8"))
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    coordinates = read_csv(COORDINATES)
    scored = read_csv(SCORED)
    checks = [
        check("protocol_hash", sha256(PROTOCOL) == protocol_freeze["protocol_sha256"], sha256(PROTOCOL)),
        check("coordinate_hash", sha256(COORDINATES) == coordinate_freeze["coordinate_file_sha256"], sha256(COORDINATES)),
        check("broken_map_hash", sha256(BROKEN_MAPS) == coordinate_freeze["broken_maps_file_sha256"], sha256(BROKEN_MAPS)),
        check("row_counts", len(coordinates) == len(scored) == 500, f"{len(coordinates)}/{len(scored)}"),
    ]

    coordinate_errors = []
    label_errors = []
    hard_indices = []
    for index, (source, labelled) in enumerate(zip(coordinates, scored)):
        number = int(source["number"])
        child = order(number)
        parent = order(2 * number)
        eligible = all(number % wave for wave in WAVES)
        if eligible:
            hard_indices.append(index)
        if eligible and (child is None or parent is None):
            coordinate_errors.append(number)
            continue
        if child is not None and source["child_order"] != order_text(child):
            coordinate_errors.append(number)
        if parent is not None and source["parent_order"] != order_text(parent):
            coordinate_errors.append(number)
        if child is not None and parent is not None and source["closure_relation"] != relative(child, parent):
            coordinate_errors.append(number)
        if int(labelled["is_prime"]) != int(alternate_is_prime(number)):
            label_errors.append(number)
    checks.extend([
        check("all_coordinates_rederived", not coordinate_errors, f"errors={len(coordinate_errors)}"),
        check("all_labels_independent", not label_errors, f"errors={len(label_errors)}"),
        check("hard_population_label_free", len(hard_indices) == 223, f"eligible={len(hard_indices)}"),
    ])

    map_errors = []
    for control_index, mapping in enumerate(controls["parent_index_maps"]):
        if sorted(mapping) != list(range(500)):
            map_errors.append((control_index, "not permutation"))
            continue
        for index, mapped in enumerate(mapping):
            same_block = index // controls["block_size"] == mapped // controls["block_size"]
            if not same_block:
                map_errors.append((control_index, "cross-block"))
                break
            if index in hard_indices and mapped not in hard_indices:
                map_errors.append((control_index, "eligibility not preserved"))
                break
            if index not in hard_indices and mapped != index:
                map_errors.append((control_index, "ineligible moved"))
                break
    checks.append(check("all_relation_broken_maps_valid", not map_errors, f"errors={len(map_errors)}"))

    hard_rows = [scored[index] for index in hard_indices]
    primes = [row for row in hard_rows if int(row["is_prime"])]
    unresolved = [row for row in hard_rows if not int(row["is_prime"])]
    endpoints = [
        ("child", "child_order", 32001, "pn31_child_order_replication"),
        ("parent", "parent_order", 32002, "parent_order_control"),
        ("closure", "closure_relation", 32003, "double_lock_closure_relation"),
    ]
    for name, field, seed, saved_key in endpoints:
        observed, null_mean, p_value = categorical_p(
            [row[field] for row in primes],
            [row[field] for row in unresolved],
            seed,
        )
        saved = results["primary_prime_vs_unresolved"][saved_key]
        passed = (
            math.isclose(observed, saved["observed"], abs_tol=1e-15)
            and math.isclose(null_mean, saved["null_mean"], abs_tol=1e-15)
            and math.isclose(p_value, saved["p_value"], abs_tol=1e-15)
        )
        checks.append(check(f"{name}_permutation_reproduced", passed, f"tv={observed:.12f} null={null_mean:.12f} p={p_value:.12f}"))

    broken_tvs = []
    broken_category_counts = []
    for mapping in controls["parent_index_maps"]:
        prime_signatures = []
        composite_signatures = []
        for index in hard_indices:
            child = order(int(scored[index]["number"]))
            parent = order(int(scored[mapping[index]]["parent_number"]))
            signature = relative(child, parent)
            if int(scored[index]["is_prime"]):
                prime_signatures.append(signature)
            else:
                composite_signatures.append(signature)
        broken_tvs.append(total_variation(prime_signatures, composite_signatures))
        broken_category_counts.append(len(set(prime_signatures + composite_signatures)))
    intact = results["primary_prime_vs_unresolved"]["double_lock_closure_relation"]["observed"]
    broken_p = (1 + sum(value >= intact for value in broken_tvs)) / (1 + len(broken_tvs))
    saved_broken = results["primary_prime_vs_unresolved"]["relation_broken_control"]
    checks.append(check(
        "relation_broken_control_reproduced",
        math.isclose(sum(broken_tvs) / len(broken_tvs), saved_broken["control_mean"], abs_tol=1e-15)
        and math.isclose(broken_p, saved_broken["p_value"], abs_tol=1e-15),
        f"mean={sum(broken_tvs)/len(broken_tvs):.12f} p={broken_p:.12f}",
    ))

    intact_categories = results["primary_prime_vs_unresolved"]["double_lock_closure_relation"]["combined_category_count"]
    mean_broken_categories = sum(broken_category_counts) / len(broken_category_counts)
    checks.append(check(
        "control_support_difference_flagged",
        mean_broken_categories > 1.5 * intact_categories,
        f"intact_categories={intact_categories} mean_broken_categories={mean_broken_categories:.3f}; raw TV is not support-matched",
    ))

    exact = results["descriptive"]["exact_child_parent_order_pair"]
    checks.append(check(
        "exact_pair_sparsity_fenced",
        exact["combined_category_count"] / len(hard_rows) > 0.90 and not exact["inferential_endpoint"],
        f"{exact['combined_category_count']}/{len(hard_rows)} categories",
    ))

    payload = {
        "test_id": "PN32/DOUBLE-INFORMATION-LOCK/v1",
        "validated_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "checks_passed": sum(item["passed"] for item in checks),
        "checks_total": len(checks),
        "all_checks_passed": all(item["passed"] for item in checks),
        "coordinate_error_examples": coordinate_errors[:10],
        "label_error_examples": label_errors[:10],
        "map_error_examples": map_errors[:10],
        "methodological_caveat": {
            "intact_closure_category_count": intact_categories,
            "mean_broken_closure_category_count": mean_broken_categories,
            "raw_tv_control_support_matched": False,
            "impact": "Do not interpret broken-control TV magnitude as an effect size. The intact label-permutation endpoint remains valid and null.",
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not payload["all_checks_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
