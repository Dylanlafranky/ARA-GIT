#!/usr/bin/env python3
"""Descriptive post-result localization of Q40's visible-flag failures.

This is not part of the frozen Q40 prediction. It reads the already-scored
cycle table and groups the frozen flag's confusion counts by the fourth
quadrant. The output is intended to specify a later untouched-data test,
not to rescue or rescore Q40.
"""

from __future__ import annotations

import csv
import gzip
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
INPUT = HERE / "Q40_RETURN_FLOW_RELATION_REVERSAL_CYCLES.csv.gz"
OUTPUT = HERE / "Q40_POST_RESULT_QUADRANT_LOCALIZATION.json"

ARA_QUADRANTS = {
    0: {"ara": "Ab", "signed": "Q++"},
    1: {"ara": "Ba", "signed": "Q-+"},
    2: {"ara": "bA", "signed": "Q--"},
    3: {"ara": "aB", "signed": "Q+-"},
}


def main() -> None:
    grouped: dict[int, Counter[str]] = {
        quadrant: Counter() for quadrant in ARA_QUADRANTS
    }
    directions: Counter[int] = Counter()

    with gzip.open(INPUT, "rt", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            q4 = int(row["q4"])
            flag = int(row["flag"])
            negative = int(row["target_negative_orientation"])
            directions[int(row["direction"])] += 1

            bucket = grouped[q4]
            bucket["cycles"] += 1
            bucket["flagged"] += flag
            bucket["negative_targets"] += negative
            if flag and negative:
                bucket["true_positive"] += 1
            elif flag and not negative:
                bucket["false_positive"] += 1
            elif not flag and negative:
                bucket["false_negative"] += 1
            else:
                bucket["true_negative"] += 1

    quadrants = []
    for q4 in sorted(grouped):
        bucket = grouped[q4]
        for key in (
            "cycles",
            "flagged",
            "negative_targets",
            "true_positive",
            "false_positive",
            "false_negative",
            "true_negative",
        ):
            bucket[key] += 0
        negatives = bucket["negative_targets"]
        positives = bucket["flagged"]
        quadrants.append(
            {
                "q4_index": q4,
                **ARA_QUADRANTS[q4],
                **dict(bucket),
                "recall": (
                    bucket["true_positive"] / negatives if negatives else None
                ),
                "precision": (
                    bucket["true_positive"] / positives if positives else None
                ),
            }
        )

    total_false_negatives = sum(q["false_negative"] for q in quadrants)
    ba_false_negatives = next(
        q["false_negative"] for q in quadrants if q["ara"] == "Ba"
    )

    result = {
        "analysis_id": "Q40-POST-RESULT-QUADRANT-LOCALIZATION-v1",
        "status": "DESCRIPTIVE POST-RESULT; CANNOT RESCORE Q40",
        "source": INPUT.name,
        "directions": {str(key): value for key, value in sorted(directions.items())},
        "quadrants": quadrants,
        "localization": {
            "total_false_negatives": total_false_negatives,
            "ba_false_negatives": ba_false_negatives,
            "ba_share_of_false_negatives": (
                ba_false_negatives / total_false_negatives
                if total_false_negatives
                else None
            ),
        },
        "boundary": (
            "The Ba concentration was discovered after Q40 outcomes were open. "
            "It may define a new frozen hypothesis on another untouched archive, "
            "but it cannot rescue or alter Q40's frozen verdict."
        ),
    }

    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
