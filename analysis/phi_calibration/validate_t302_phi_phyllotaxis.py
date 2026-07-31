#!/usr/bin/env python3
"""Independent arithmetic and artifact validation for T302."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
WORKBOOK = HERE / "data" / "Source Data 21.xlsx"
RESULT = HERE / "T302_PHI_PHYLLOTAXIS_RESULTS.json"
EVENTS = HERE / "T302_PHI_PHYLLOTAXIS_EVENT_GEOMETRY.csv"
PLANTS = HERE / "T302_PHI_PHYLLOTAXIS_PLANT_SUMMARY.csv"
CANDIDATES = HERE / "T302_PHI_PHYLLOTAXIS_CANDIDATES.csv"
VISUAL = HERE / "T302_PHI_PHYLLOTAXIS_VISUALIZATION.html"
OUTPUT = HERE / "T302_PHI_PHYLLOTAXIS_VALIDATION.json"

EXPECTED_WORKBOOK_HASH = (
    "E78372214B1386A486B25C8340C19F22BC74D3382F80A9B36A2972CC3D35ADFB"
)
PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_A = PHI ** -2
SEED = 302
SHUFFLES = 10_000

FIXED = {
    "one_third": 1.0 / 3.0,
    "one_over_e": 1.0 / math.e,
    "three_eighths": 3.0 / 8.0,
    "phi": PHI_A,
    "eight_twenty_firsts": 8.0 / 21.0,
    "two_fifths": 2.0 / 5.0,
    "silver_conjugate": math.sqrt(2.0) - 1.0,
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def circle_distance(a: float, b: float) -> float:
    value = abs(a - b) % 1.0
    return min(value, 1.0 - value)


def geometry(turns: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    previous = [0.0]
    positions = []
    scores = []
    current = 0.0
    for turn in turns:
        ordered = sorted(previous)
        gaps = [
            ordered[index + 1] - ordered[index]
            for index in range(len(ordered) - 1)
        ]
        gaps.append(ordered[0] + 1.0 - ordered[-1])
        optimum = max(gaps) / 2.0
        current = (current + float(turn)) % 1.0
        nearest = min(circle_distance(current, old) for old in previous)
        positions.append(current)
        scores.append(nearest / optimum)
        previous.append(current)
    return np.asarray(positions), np.asarray(scores)


def assert_close(name: str, observed: float, expected: float, tolerance=1e-10) -> dict:
    passed = bool(abs(observed - expected) <= tolerance)
    return {
        "name": name,
        "pass": passed,
        "observed": float(observed),
        "expected": float(expected),
        "absolute_difference": float(abs(observed - expected)),
        "tolerance": tolerance,
    }


def main() -> None:
    source = pd.read_excel(WORKBOOK, sheet_name="EPFL_phyllo-angle")
    saved = json.loads(RESULT.read_text(encoding="utf-8"))
    event_file = pd.read_csv(EVENTS)
    plant_file = pd.read_csv(PLANTS)
    candidate_file = pd.read_csv(CANDIDATES)

    ids = []
    counts: dict[str, int] = {}
    for row in source.itertuples(index=False):
        if row.genotype not in counts or int(row.meristem) == 1:
            counts[row.genotype] = counts.get(row.genotype, 0) + 1
        ids.append(counts[row.genotype])
    source["plant"] = ids
    source["split"] = np.where(source["plant"] % 2, "development", "confirmation")
    source["x_A"] = source["angle"] / 360.0
    source["heldout"] = source["meristem"] >= 3

    sequential = True
    for (_, _), group in source.groupby(["genotype", "plant"], sort=False):
        sequence = group["meristem"].astype(int).tolist()
        sequential &= sequence == list(range(1, len(sequence) + 1))

    plant_rows = []
    candidate_rows = []
    for (genotype, plant), group in source.groupby(["genotype", "plant"], sort=False):
        group = group.sort_values("meristem")
        turns = group["x_A"].to_numpy()
        positions, clearance = geometry(turns)
        held = group["heldout"].to_numpy(dtype=bool)
        plant_rows.append(
            {
                "genotype": genotype,
                "plant": int(plant),
                "split": group["split"].iloc[0],
                "x_A_median": float(np.median(turns[held])),
                "clearance_median": float(np.median(clearance[held])),
            }
        )
        for name, step in FIXED.items():
            step_error = np.abs(turns[held] - step) * 360.0
            indices = np.flatnonzero(held)
            predicted = (positions[1] + (indices - 1) * step) % 1.0
            cumulative = np.asarray(
                [
                    360.0 * circle_distance(actual, estimate)
                    for actual, estimate in zip(positions[held], predicted)
                ]
            )
            candidate_rows.append(
                {
                    "genotype": genotype,
                    "plant": int(plant),
                    "split": group["split"].iloc[0],
                    "candidate": name,
                    "step": float(np.median(step_error)),
                    "cumulative": float(np.median(cumulative)),
                }
            )

    recomputed_plants = pd.DataFrame(plant_rows)
    recomputed_candidates = pd.DataFrame(candidate_rows)
    wt_confirm = recomputed_plants[
        (recomputed_plants["genotype"] == "Col")
        & (recomputed_plants["split"] == "confirmation")
    ]
    p1 = float(wt_confirm["x_A_median"].median())
    candidate_medians = (
        recomputed_candidates[
            (recomputed_candidates["genotype"] == "Col")
            & (recomputed_candidates["split"] == "confirmation")
        ]
        .groupby("candidate")[["step", "cumulative"]]
        .median()
    )
    p2_winner = str(candidate_medians["step"].idxmin())
    p3_winner = str(candidate_medians["cumulative"].idxmin())
    clearance = (
        recomputed_plants[recomputed_plants["split"] == "confirmation"]
        .groupby("genotype")["clearance_median"]
        .median()
        .to_dict()
    )

    rng = np.random.default_rng(SEED)
    wt_groups = [
        group.sort_values("meristem")
        for (_, _), group in source[
            (source["genotype"] == "Col") & (source["split"] == "confirmation")
        ].groupby(["genotype", "plant"], sort=False)
    ]
    null = np.empty(SHUFFLES)
    for draw in range(SHUFFLES):
        values = []
        for group in wt_groups:
            _, score = geometry(rng.permutation(group["x_A"].to_numpy()))
            values.append(float(np.median(score[2:])))
        null[draw] = np.median(values)
    shuffle_p = float((1 + np.sum(null >= clearance["Col"])) / (SHUFFLES + 1))

    checks = [
        {
            "name": "workbook SHA-256",
            "pass": digest(WORKBOOK) == EXPECTED_WORKBOOK_HASH,
            "observed": digest(WORKBOOK),
            "expected": EXPECTED_WORKBOOK_HASH,
        },
        {
            "name": "source row count",
            "pass": len(source) == 359,
            "observed": len(source),
            "expected": 359,
        },
        {
            "name": "plant sequences are exact resets",
            "pass": bool(sequential),
            "observed": bool(sequential),
            "expected": True,
        },
        {
            "name": "event CSV row count",
            "pass": len(event_file) == 359,
            "observed": len(event_file),
            "expected": 359,
        },
        {
            "name": "event ARA measured coordinate",
            "pass": bool(
                np.allclose(event_file["x_A"], event_file["angle_deg"] / 360.0)
            ),
            "observed": "all rows" if np.allclose(
                event_file["x_A"], event_file["angle_deg"] / 360.0
            ) else "mismatch",
            "expected": "all rows",
        },
        {
            "name": "event assigned mirror",
            "pass": bool(
                np.allclose(event_file["x_B_assigned"], 2.0 - event_file["x_A"])
            ),
            "observed": "all rows" if np.allclose(
                event_file["x_B_assigned"], 2.0 - event_file["x_A"]
            ) else "mismatch",
            "expected": "all rows",
        },
        assert_close(
            "P1 confirmation coordinate",
            p1,
            saved["frozen"]["P1_confirmation_wt_coordinate"],
        ),
        {
            "name": "P2 fixed winner",
            "pass": p2_winner == saved["frozen"]["P2_fixed_step_winner"],
            "observed": p2_winner,
            "expected": saved["frozen"]["P2_fixed_step_winner"],
        },
        {
            "name": "P3 fixed winner",
            "pass": p3_winner == saved["frozen"]["P3_fixed_cumulative_winner"],
            "observed": p3_winner,
            "expected": saved["frozen"]["P3_fixed_cumulative_winner"],
        },
        assert_close(
            "P4 wild-type clearance",
            clearance["Col"],
            saved["frozen"]["P4_confirmation_clearance_medians"]["Col"],
        ),
        assert_close(
            "P4 e2 clearance",
            clearance["e2"],
            saved["frozen"]["P4_confirmation_clearance_medians"]["e2"],
        ),
        assert_close(
            "P4 e1e2 clearance",
            clearance["e1e2"],
            saved["frozen"]["P4_confirmation_clearance_medians"]["e1e2"],
        ),
        assert_close(
            "P4 deterministic shuffle p",
            shuffle_p,
            saved["frozen"]["P4_shuffle_p_one_sided"],
        ),
        {
            "name": "plant summary rows",
            "pass": len(plant_file) == 58,
            "observed": len(plant_file),
            "expected": 58,
        },
        {
            "name": "fixed candidate rows",
            "pass": int((candidate_file["candidate_type"] == "fixed").sum()) == 7,
            "observed": int((candidate_file["candidate_type"] == "fixed").sum()),
            "expected": 7,
        },
        {
            "name": "visualization contains all five panels",
            "pass": all(
                marker in VISUAL.read_text(encoding="utf-8")
                for marker in [
                    'id="ara"',
                    'id="candidates"',
                    'id="clearance"',
                    'id="trajectories"',
                    'id="compensation"',
                ]
            ),
            "observed": "all panels present",
            "expected": "all panels present",
        },
    ]
    passed = sum(check["pass"] for check in checks)
    report = {
        "test_id": "T302-PHI-PHYLLOTAXIS-v1",
        "validator": "independent formulas; no import from analysis script",
        "checks_passed": passed,
        "checks_total": len(checks),
        "all_passed": passed == len(checks),
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
