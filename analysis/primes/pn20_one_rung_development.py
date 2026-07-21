"""PN20 development-only audit of the literal one-rung two-child proposal.

No fresh target is touched.  The immediate children are the two largest prime
gates at or below sqrt(N), matching the PN15 factor-sphere boundary while
retaining only one A child and one B child in the final state.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "PN20_ONE_RUNG_DEVELOPMENT.json"
OPENED_ANCHORS = (
    100_000_000,
    1_000_000_000,
    10_000_000_000,
    100_000_000_000,
    400_000_000_000,
    700_000_000_000,
    900_000_000_000,
)


def is_prime_64(number: int) -> bool:
    if number < 2:
        return False
    for small in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if number % small == 0:
            return number == small
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


def previous_prime(start: int) -> int:
    candidate = start if start % 2 else start - 1
    while candidate >= 2 and not is_prime_64(candidate):
        candidate -= 2
    return candidate


def next_prime(anchor: int) -> int:
    candidate = anchor + 1
    if candidate > 2 and candidate % 2 == 0:
        candidate += 1
    while not is_prime_64(candidate):
        candidate += 2
    return candidate


def immediate_children(anchor: int) -> tuple[int, int]:
    phase_a = previous_prime(math.isqrt(anchor))
    phase_b = previous_prime(phase_a - 1)
    return phase_a, phase_b


def state(anchor: int) -> dict:
    phase_a, phase_b = immediate_children(anchor)
    raw_ab = phase_a * phase_b
    child_a = 2.0 * math.log(phase_a) / math.log(anchor)
    child_b = 2.0 * math.log(phase_b) / math.log(anchor)
    compressed_ab = (child_a + child_b) / 2.0
    compressed_ba = 2.0 - compressed_ab
    return {
        "anchor": anchor,
        "phase_a_child": phase_a,
        "phase_b_child": phase_b,
        "raw_phase_ab": raw_ab,
        "anchor_minus_raw_phase_ab": anchor - raw_ab,
        "child_a_coordinate": child_a,
        "child_b_coordinate": child_b,
        "compressed_phase_ab": compressed_ab,
        "reflected_phase_ba": compressed_ba,
        "ab_plus_ba": compressed_ab + compressed_ba,
        "signed_ridge_distance": compressed_ab - 1.0,
    }


def safe_round(value: float) -> int | None:
    return round(value) if math.isfinite(value) else None


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError("PN20 development artifact already exists; refusing overwrite")
    rows: list[dict] = []
    for anchor in OPENED_ANCHORS:
        current = state(anchor)
        doubled = state(2 * anchor)
        phase_ab = current["compressed_phase_ab"]
        phase_ba = current["reflected_phase_ba"]
        signed_0 = current["signed_ridge_distance"]
        signed_1 = doubled["signed_ridge_distance"]
        denominator = signed_1 - signed_0
        secant_location = (
            anchor - signed_0 * anchor / denominator if denominator else float("nan")
        )
        true_prime = next_prime(anchor)
        true_gap = true_prime - anchor
        candidate_gaps = {
            "three_minus_ab": safe_round((2.0 - phase_ab) + 1.0),
            "two_ab_over_two_minus_ab_plus_one": safe_round(
                2.0 * phase_ab / (2.0 - phase_ab) + 1.0
            ),
            "two_ab_over_parenthesized_ba_plus_one": safe_round(
                2.0 * phase_ab / ((2.0 - phase_ab) + 1.0)
            ),
            "secant_n_to_2n": safe_round(secant_location - anchor),
            "raw_ab_deficit": current["anchor_minus_raw_phase_ab"],
        }
        rows.append({
            **current,
            "double_anchor_compressed_phase_ab": doubled["compressed_phase_ab"],
            "double_anchor_reflected_phase_ba": doubled["reflected_phase_ba"],
            "true_next_prime": true_prime,
            "true_next_prime_gap": true_gap,
            "candidate_gaps": candidate_gaps,
            "absolute_gap_errors": {
                name: abs(value - true_gap) if value is not None else None
                for name, value in candidate_gaps.items()
            },
        })

    formula_names = list(rows[0]["candidate_gaps"])
    formula_summary = {}
    for name in formula_names:
        values = [row["candidate_gaps"][name] for row in rows]
        errors = [row["absolute_gap_errors"][name] for row in rows]
        formula_summary[name] = {
            "exact_count": sum(value == row["true_next_prime_gap"] for value, row in zip(values, rows)),
            "anchor_count": len(rows),
            "mean_absolute_gap_error": sum(error for error in errors if error is not None) / len(rows),
            "predicted_gaps": values,
        }
    payload = {
        "test_id": "PN20/ONE-RUNG-TWO-CHILD/DEVELOPMENT-ONLY/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "development only; supplied 87-bit anchor remains unopened",
        "extractor": (
            "Phase A is the largest prime gate <= sqrt(N); Phase B is the next-largest prime gate. "
            "Only those two immediate children remain in the computed state."
        ),
        "normalization": (
            "child x=2log(p)/log(N); compressed AB is half the two-child sum; BA=2-AB."
        ),
        "rows": rows,
        "formula_summary": formula_summary,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(formula_summary, indent=2))


if __name__ == "__main__":
    main()
