"""PN20 development audit of a directional, one-rung, two-child ARA decoder.

The supplied 87-bit target is deliberately absent.  This script uses only
anchors whose next-prime labels were already opened in earlier development.

The immediate rung follows PN10B: the nine largest already-paid prime gates
q <= N**0.45.  Every gate supplies one reversible coordinate

    A_q = 2 (N mod q) / q,       B_q = 2 - A_q.

The compressed state retains exactly two children:

* the child with the largest A_q reading;
* the (different, unless unavoidable) child with the largest B_q reading.

Their directed closure is AB=(A_max+B_max)/2.  BA=2-AB is the reflected
whole.  The registered location decoder uses the two requested landmarks N
and 2N and takes the secant intersection with the AB=1 ridge.  A third state
is evaluated only at the frozen prediction as a confirmation diagnostic; it
does not move the prediction.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "PN20_DIRECTIONAL_TWO_CHILD_DEVELOPMENT.json"
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
    if start == 2:
        return 2
    candidate = start if start % 2 else start - 1
    while candidate >= 3 and not is_prime_64(candidate):
        candidate -= 2
    if candidate >= 3:
        return candidate
    return 2


def next_prime(anchor: int) -> int:
    candidate = anchor + 1
    if candidate > 2 and candidate % 2 == 0:
        candidate += 1
    while not is_prime_64(candidate):
        candidate += 2
    return candidate


def paid_gates(anchor: int, count: int = 9) -> list[int]:
    boundary = int(anchor ** 0.45)
    gates: list[int] = []
    cursor = previous_prime(boundary)
    while len(gates) < count:
        gates.append(cursor)
        cursor = previous_prime(cursor - 1)
    return gates


def directional_state(anchor: int) -> dict:
    children = []
    for gate in paid_gates(anchor):
        remainder = anchor % gate
        phase_a = 2.0 * remainder / gate
        phase_b = 2.0 - phase_a
        children.append({
            "gate": gate,
            "remainder": remainder,
            "phase_a": phase_a,
            "phase_b": phase_b,
            "signed_orientation": phase_a - 1.0,
        })

    a_child = max(children, key=lambda row: (row["phase_a"], row["gate"]))
    b_child = max(children, key=lambda row: (row["phase_b"], row["gate"]))
    phase_ab = (a_child["phase_a"] + b_child["phase_b"]) / 2.0
    phase_ba = 2.0 - phase_ab
    return {
        "anchor": anchor,
        "immediate_siblings_inspected": len(children),
        "retained_child_count": 2,
        "phase_a_child": a_child,
        "phase_b_child": b_child,
        "phase_ab": phase_ab,
        "phase_ba": phase_ba,
        "ab_plus_ba": phase_ab + phase_ba,
        "signed_ridge_distance": phase_ab - 1.0,
    }


def nearest_odd(value: float) -> int | None:
    if not math.isfinite(value):
        return None
    rounded = round(value)
    if rounded % 2:
        return rounded
    lower = rounded - 1
    upper = rounded + 1
    return lower if abs(value - lower) <= abs(value - upper) else upper


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError("development artifact already exists; refusing overwrite")

    rows = []
    for anchor in OPENED_ANCHORS:
        first = directional_state(anchor)
        second = directional_state(2 * anchor)
        s0 = first["signed_ridge_distance"]
        s1 = second["signed_ridge_distance"]
        denominator = s1 - s0
        raw_prediction = (
            anchor - s0 * anchor / denominator if denominator else float("nan")
        )
        predicted_integer = nearest_odd(raw_prediction)
        true_prime = next_prime(anchor)
        third = (
            directional_state(predicted_integer)
            if predicted_integer is not None and predicted_integer >= 3
            else None
        )
        rows.append({
            "anchor": anchor,
            "landmark_1": first,
            "landmark_2": second,
            "secant_raw_prediction": raw_prediction if math.isfinite(raw_prediction) else None,
            "predicted_integer": predicted_integer,
            "prediction_is_forward_of_anchor": (
                predicted_integer is not None and predicted_integer > anchor
            ),
            "confirmation_state_at_prediction": third,
            "true_next_prime": true_prime,
            "true_gap": true_prime - anchor,
            "predicted_gap": (
                predicted_integer - anchor if predicted_integer is not None else None
            ),
            "exact_next_prime": predicted_integer == true_prime,
            "predicted_integer_is_prime": (
                is_prime_64(predicted_integer)
                if predicted_integer is not None and 0 <= predicted_integer < 2**64
                else None
            ),
        })

    forward = [row for row in rows if row["prediction_is_forward_of_anchor"]]
    finite_errors = [
        abs(row["predicted_integer"] - row["true_next_prime"])
        for row in rows
        if row["predicted_integer"] is not None
    ]
    payload = {
        "test_id": "PN20/DIRECTIONAL-ONE-RUNG-TWO-CHILD/DEVELOPMENT-ONLY/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "development only; supplied 87-bit anchor remains unopened",
        "extractor": (
            "Inspect the nine largest PN10B paid gates q<=N^0.45; retain only the child "
            "with maximum A_q and the child with maximum B_q."
        ),
        "closure": "AB=(max A_q + max B_q)/2; BA=2-AB.",
        "decoder": (
            "Evaluate signed AB ridge distance at N and 2N; take their secant crossing "
            "with AB=1; round to nearest odd integer. A third state only confirms."
        ),
        "cost_disclosure": (
            "The retained state has two children, but selecting them inspects nine immediate "
            "siblings and finding those gates has its own computation cost."
        ),
        "summary": {
            "anchor_count": len(rows),
            "forward_predictions": len(forward),
            "exact_next_primes": sum(row["exact_next_prime"] for row in rows),
            "prime_predictions": sum(row["predicted_integer_is_prime"] is True for row in rows),
            "mean_absolute_integer_error": (
                sum(finite_errors) / len(finite_errors) if finite_errors else None
            ),
        },
        "rows": rows,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2))
    for row in rows:
        print(
            row["anchor"],
            row["landmark_1"]["phase_ab"],
            row["landmark_2"]["phase_ab"],
            row["predicted_integer"],
            row["true_next_prime"],
        )


if __name__ == "__main__":
    main()
