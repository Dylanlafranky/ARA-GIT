"""Attach direct labels and score the frozen PN32 double-lock endpoints."""

from __future__ import annotations

import csv
import hashlib
import json
import random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
COORDINATES = HERE / "PN32_DOUBLE_INFORMATION_LOCK_FROZEN_COORDINATES.csv"
BROKEN_MAPS = HERE / "PN32_RELATION_BROKEN_PARENT_INDEXES.json"
FREEZE = HERE / "PN32_COORDINATE_FREEZE_MANIFEST.json"
SCORED = HERE / "PN32_DOUBLE_INFORMATION_LOCK_SCORED.csv"
RESULTS = HERE / "PN32_DOUBLE_INFORMATION_LOCK_RESULTS.json"
PERMUTATIONS = 10_000


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def is_prime_trial(number: int) -> bool:
    if number < 2:
        return False
    if number % 2 == 0:
        return number == 2
    divisor = 3
    while divisor * divisor <= number:
        if number % divisor == 0:
            return False
        divisor += 2
    return True


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def total_variation(positive: list[str], negative: list[str]) -> float:
    p = Counter(positive)
    n = Counter(negative)
    return 0.5 * sum(
        abs(p[key] / len(positive) - n[key] / len(negative))
        for key in set(p) | set(n)
    )


def categorical_permutation(positive: list[str], negative: list[str], seed: int) -> dict:
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
    return {
        "statistic": "total_variation_distance",
        "observed": observed,
        "permutations": PERMUTATIONS,
        "seed": seed,
        "null_mean": null_sum / PERMUTATIONS,
        "p_value": (at_or_above + 1) / (PERMUTATIONS + 1),
        "prime_category_count": len(set(positive)),
        "composite_category_count": len(set(negative)),
        "combined_category_count": len(set(combined)),
        "prime_counts": dict(Counter(positive)),
        "composite_counts": dict(Counter(negative)),
    }


def unique_order(text: str) -> tuple[int, ...]:
    if "+" in text:
        raise ValueError(f"tied order not valid in hard comparison: {text}")
    return tuple(int(item) for item in text.split(">"))


def relative_permutation(child_text: str, parent_text: str) -> str:
    child = unique_order(child_text)
    parent = unique_order(parent_text)
    parent_rank = {wave: rank + 1 for rank, wave in enumerate(parent)}
    return "-".join(str(parent_rank[wave]) for wave in child)


def closure_tv(rows: list[dict], parent_indices: list[int] | None = None) -> float:
    signatures = []
    for local_index, row in enumerate(rows):
        parent_row = row if parent_indices is None else rows[parent_indices[local_index]]
        signatures.append(relative_permutation(row["child_order"], parent_row["parent_order"]))
    primes = [value for value, row in zip(signatures, rows) if row["is_prime"]]
    composites = [value for value, row in zip(signatures, rows) if not row["is_prime"]]
    return total_variation(primes, composites)


def main() -> None:
    for output in (SCORED, RESULTS):
        if output.exists():
            raise RuntimeError(f"refusing to overwrite {output.name}")
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    if sha256(COORDINATES) != freeze["coordinate_file_sha256"]:
        raise RuntimeError("coordinate freeze hash mismatch")
    if sha256(BROKEN_MAPS) != freeze["broken_maps_file_sha256"]:
        raise RuntimeError("broken-map freeze hash mismatch")

    rows = []
    for source in read_csv(COORDINATES):
        number = int(source["number"])
        rows.append({
            **source,
            "number": number,
            "parent_number": int(source["parent_number"]),
            "unresolved_by_five_children": int(source["unresolved_by_five_children"]),
            "is_prime": int(is_prime_trial(number)),
        })
    primes = [row for row in rows if row["is_prime"]]
    composites = [row for row in rows if not row["is_prime"]]
    unresolved = [row for row in composites if row["unresolved_by_five_children"]]
    hard_rows = [row for row in rows if row["is_prime"] or (not row["is_prime"] and row["unresolved_by_five_children"])]

    child_order = categorical_permutation(
        [row["child_order"] for row in primes],
        [row["child_order"] for row in unresolved],
        32001,
    )
    parent_order = categorical_permutation(
        [row["parent_order"] for row in primes],
        [row["parent_order"] for row in unresolved],
        32002,
    )
    closure = categorical_permutation(
        [row["closure_relation"] for row in primes],
        [row["closure_relation"] for row in unresolved],
        32003,
    )

    exact_pair_prime = [f"{row['child_order']}||{row['parent_order']}" for row in primes]
    exact_pair_unresolved = [f"{row['child_order']}||{row['parent_order']}" for row in unresolved]
    exact_pair = {
        "observed_tv": total_variation(exact_pair_prime, exact_pair_unresolved),
        "prime_category_count": len(set(exact_pair_prime)),
        "composite_category_count": len(set(exact_pair_unresolved)),
        "combined_category_count": len(set(exact_pair_prime + exact_pair_unresolved)),
        "inferential_endpoint": False,
        "reason": "exact six-component pairs are sparse; protocol marks this descriptive only",
    }

    maps_payload = json.loads(BROKEN_MAPS.read_text(encoding="utf-8"))
    number_to_hard_index = {row["number"]: index for index, row in enumerate(hard_rows)}
    full_index_to_hard = {
        full_index: number_to_hard_index[row["number"]]
        for full_index, row in enumerate(rows)
        if row["number"] in number_to_hard_index
    }
    broken_tvs = []
    for mapping in maps_payload["parent_index_maps"]:
        # The parent was shuffled in 50-row blocks before labels. Restrict both sides to
        # the frozen hard population while retaining the mapped parent from the full table.
        signatures = []
        labels = []
        for full_index, row in enumerate(rows):
            if full_index not in full_index_to_hard:
                continue
            parent_row = rows[mapping[full_index]]
            signatures.append(relative_permutation(row["child_order"], parent_row["parent_order"]))
            labels.append(row["is_prime"])
        broken_tvs.append(total_variation(
            [value for value, label in zip(signatures, labels) if label],
            [value for value, label in zip(signatures, labels) if not label],
        ))
    intact_tv = closure["observed"]
    at_or_above = sum(value >= intact_tv for value in broken_tvs)
    relation_broken = {
        "statistic": "closure total variation under pre-frozen blockwise parent reassignment",
        "intact_tv": intact_tv,
        "control_count": len(broken_tvs),
        "seed": maps_payload["seed"],
        "block_size": maps_payload["block_size"],
        "control_mean": sum(broken_tvs) / len(broken_tvs),
        "control_min": min(broken_tvs),
        "control_max": max(broken_tvs),
        "controls_at_or_above_intact": at_or_above,
        "p_value": (at_or_above + 1) / (len(broken_tvs) + 1),
    }

    endpoint_transitions = Counter(
        f"{row['child_phase_a']}->{row['parent_phase_a']}|{row['child_phase_b']}->{row['parent_phase_b']}"
        for row in hard_rows
    )

    replication_pass = child_order["p_value"] < 0.01
    closure_label_pass = closure["p_value"] < 0.01
    closure_break_pass = relation_broken["p_value"] < 0.01
    if replication_pass and closure_label_pass and closure_break_pass:
        status = "DOUBLE-LOCK CLOSURE SUPPORT"
    elif closure_label_pass and closure_break_pass:
        status = "CLOSURE-SPECIFIC SIGNAL WITHOUT PN31 REPLICATION"
    elif replication_pass:
        status = "CHILD-ORDER REPLICATION ONLY"
    elif min(child_order["p_value"], closure["p_value"], relation_broken["p_value"]) < 0.05:
        status = "SUGGESTIVE"
    else:
        status = "NULL"

    write_csv(SCORED, rows)
    payload = {
        "test_id": "PN32/DOUBLE-INFORMATION-LOCK/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "population": {
            "n": len(rows),
            "prime_n": len(primes),
            "odd_composite_n": len(composites),
            "unresolved_composite_n": len(unresolved),
            "hard_comparison_n": len(hard_rows),
            "range": "odd integers 3001 through 3999 inclusive",
            "waves": [3, 5, 9, 11, 13],
            "parent_transform": "2N",
            "sieve_used": False,
            "label_method": "direct trial division after coordinate and control freeze",
        },
        "primary_prime_vs_unresolved": {
            "pn31_child_order_replication": child_order,
            "parent_order_control": parent_order,
            "double_lock_closure_relation": closure,
            "relation_broken_control": relation_broken,
        },
        "descriptive": {
            "exact_child_parent_order_pair": exact_pair,
            "endpoint_transition_counts": dict(endpoint_transitions),
        },
        "decision": {
            "status": status,
            "child_order_replication_pass": replication_pass,
            "closure_label_pass": closure_label_pass,
            "closure_break_pass": closure_break_pass,
            "prime_generator_tested": False,
            "prime_certification_tested": False,
            "literal_physical_hexagon_proved": False,
        },
    }
    RESULTS.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
