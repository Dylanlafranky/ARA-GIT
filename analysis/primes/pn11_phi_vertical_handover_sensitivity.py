#!/usr/bin/env python3
"""Required PN11 sensitivities, run after the frozen primary target."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import mean, median

from pn11_phi_vertical_handover import (
    PHI,
    STAGES,
    enumerate_families,
    landmark_table,
    quantiles,
)


ROOT = Path(__file__).resolve().parent


def summarize(rows: list[dict]) -> dict:
    values = [row["event_x_old_lock"] for row in rows]
    return {
        "n": len(rows),
        "event_x": quantiles(values),
        "phi_mean_absolute_distance": mean(abs(value - PHI) for value in values),
        "nine_fifths_mean_absolute_distance": mean(abs(value - 1.8) for value in values),
        "phi_crossed_before_expansion_count": sum(
            row["phi_crossed_before_expansion"] for row in rows
        ),
        "phi_crossed_before_expansion_fraction": sum(
            row["phi_crossed_before_expansion"] for row in rows
        )
        / len(rows),
    }


def main() -> None:
    start, end = STAGES["target"]
    primary, all_rows, checks = enumerate_families(start, end)

    by_q = []
    for q in sorted({row["first_missing_prime"] for row in all_rows}):
        subset = [row for row in all_rows if row["first_missing_prime"] == q]
        summary = summarize(subset)
        by_q.append(
            {
                "first_missing_prime": q,
                "n": summary["n"],
                "event_x_mean": summary["event_x"]["mean"],
                "event_x_median": summary["event_x"]["median"],
                "phi_mae": summary["phi_mean_absolute_distance"],
                "nine_fifths_mae": summary["nine_fifths_mean_absolute_distance"],
                "phi_cross_count": summary["phi_crossed_before_expansion_count"],
                "phi_cross_fraction": summary["phi_crossed_before_expansion_fraction"],
            }
        )

    all_table = landmark_table(all_rows)
    all_order = sorted(all_table, key=lambda item: item["mean_absolute_event_distance"])
    output = {
        "test_id": "PN11/PHI-VERTICAL-HANDOVER/v3",
        "artifact": "required target sensitivities",
        "range": [start, end],
        "checks": checks,
        "primary_q_ge_3": summarize(primary),
        "all_fundamental_including_q_2": summarize(all_rows),
        "all_fundamental_landmark_order": [
            {
                "landmark": item["landmark"],
                "mae": item["mean_absolute_event_distance"],
                "rank": item["mean_distance_rank"],
            }
            for item in all_order
        ],
        "by_first_missing_prime": by_q,
        "note": (
            "q=2 families have no nontrivial harmonic repeat before expansion and are excluded from the primary; "
            "including them moves the event distribution still closer to the unchanged 2 pole."
        ),
    }
    (ROOT / "PN11_TARGET_SENSITIVITY.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )
    with (ROOT / "PN11_TARGET_BY_Q.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(by_q[0]))
        writer.writeheader()
        writer.writerows(by_q)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

