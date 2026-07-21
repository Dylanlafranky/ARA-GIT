"""PN20 branch-aware one-rung/two-child development test.

This corrects the directional definition audited in the preceding PN20 file.
The supplied 87-bit target remains absent.

For each PN10B immediate child, a=2*(N mod q)/q.  A child on the left branch
(a <= 1) has progress a from pole 0 toward the ridge.  A child on the right
branch (a >= 1) has progress 2-a from pole 2 toward the ridge.  Retain only
the maximum-progress child from each branch.  Their completed whole is the
mean progress AB in [0,1]; BA is the same closure viewed from the reverse
direction.  The prime hypothesis predicts a common AB=BA=1 ridge.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

from pn20_directional_two_child_development import (
    OPENED_ANCHORS,
    is_prime_64,
    next_prime,
    paid_gates,
)


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "PN20_BRANCH_TWO_CHILD_DEVELOPMENT.json"


def branch_state(anchor: int) -> dict:
    children = []
    for gate in paid_gates(anchor):
        remainder = anchor % gate
        axis = 2.0 * remainder / gate
        if axis <= 1.0:
            branch = "A_from_0"
            progress = axis
        else:
            branch = "B_from_2"
            progress = 2.0 - axis
        children.append({
            "gate": gate,
            "remainder": remainder,
            "axis_coordinate": axis,
            "branch": branch,
            "progress_to_ridge": progress,
            "ridge_deficit": 1.0 - progress,
        })

    left = [row for row in children if row["branch"] == "A_from_0"]
    right = [row for row in children if row["branch"] == "B_from_2"]
    if not left or not right:
        return {
            "anchor": anchor,
            "valid_two_branch_state": False,
            "immediate_siblings_inspected": len(children),
            "retained_child_count": 0,
            "reason": "one immediate branch had no representative",
        }

    phase_a = max(left, key=lambda row: (row["progress_to_ridge"], row["gate"]))
    phase_b = max(right, key=lambda row: (row["progress_to_ridge"], row["gate"]))
    phase_ab = (phase_a["progress_to_ridge"] + phase_b["progress_to_ridge"]) / 2.0
    phase_ba = 2.0 - phase_ab
    return {
        "anchor": anchor,
        "valid_two_branch_state": True,
        "immediate_siblings_inspected": len(children),
        "retained_child_count": 2,
        "phase_a_child": phase_a,
        "phase_b_child": phase_b,
        "phase_ab": phase_ab,
        "phase_ba": phase_ba,
        "ab_plus_ba": phase_ab + phase_ba,
        "te_ara_decompressed_sum": (
            phase_a["progress_to_ridge"] + phase_b["progress_to_ridge"]
        ),
        "signed_ridge_distance": phase_ab - 1.0,
    }


def nearest_forward_odd(anchor: int, value: float) -> int | None:
    if not math.isfinite(value) or value <= anchor:
        return None
    rounded = round(value)
    if rounded % 2 == 0:
        low, high = rounded - 1, rounded + 1
        rounded = low if abs(value - low) <= abs(value - high) else high
    return rounded


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError("development artifact already exists; refusing overwrite")
    rows = []
    for anchor in OPENED_ANCHORS:
        first = branch_state(anchor)
        second = branch_state(2 * anchor)
        raw_prediction = None
        predicted = None
        if first["valid_two_branch_state"] and second["valid_two_branch_state"]:
            s0 = first["signed_ridge_distance"]
            s1 = second["signed_ridge_distance"]
            denominator = s1 - s0
            if denominator:
                candidate = anchor - s0 * anchor / denominator
                if math.isfinite(candidate):
                    raw_prediction = candidate
                    predicted = nearest_forward_odd(anchor, candidate)
        truth = next_prime(anchor)
        confirmation = branch_state(predicted) if predicted is not None else None
        rows.append({
            "anchor": anchor,
            "landmark_1": first,
            "landmark_2": second,
            "secant_raw_prediction": raw_prediction,
            "predicted_integer": predicted,
            "predicted_gap": predicted - anchor if predicted is not None else None,
            "confirmation_state_at_prediction": confirmation,
            "true_next_prime": truth,
            "true_gap": truth - anchor,
            "exact_next_prime": predicted == truth,
            "predicted_integer_is_prime": (
                is_prime_64(predicted) if predicted is not None and predicted < 2**64 else None
            ),
        })

    predictions = [row for row in rows if row["predicted_integer"] is not None]
    errors = [abs(row["predicted_integer"] - row["true_next_prime"]) for row in predictions]
    payload = {
        "test_id": "PN20/BRANCH-AWARE-ONE-RUNG-TWO-CHILD/DEVELOPMENT-ONLY/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "development only; supplied 87-bit anchor remains unopened",
        "extractor": (
            "Among nine PN10B immediate paid-gate children, retain maximum progress toward "
            "the ridge from the A/0 branch and maximum progress from the B/2 branch."
        ),
        "closure": (
            "AB=mean(two retained branch progresses); BA=2-AB; target ridge AB=BA=1."
        ),
        "decoder": "Secant through AB(N)-1 and AB(2N)-1, rounded to nearest forward odd.",
        "summary": {
            "anchor_count": len(rows),
            "two_branch_states_at_both_landmarks": sum(
                row["landmark_1"]["valid_two_branch_state"]
                and row["landmark_2"]["valid_two_branch_state"]
                for row in rows
            ),
            "forward_predictions": len(predictions),
            "exact_next_primes": sum(row["exact_next_prime"] for row in rows),
            "prime_predictions": sum(row["predicted_integer_is_prime"] is True for row in rows),
            "mean_absolute_integer_error": sum(errors) / len(errors) if errors else None,
        },
        "rows": rows,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2))
    for row in rows:
        print(
            row["anchor"],
            row["landmark_1"].get("phase_ab"),
            row["landmark_2"].get("phase_ab"),
            row["predicted_integer"],
            row["true_next_prime"],
        )


if __name__ == "__main__":
    main()
