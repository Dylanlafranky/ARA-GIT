#!/usr/bin/env python3
"""Independent validation of T315/H2 outputs using stdlib CSV arithmetic."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source_ronne_aa"
SECTIONS = (1, 2, 3, 5, 6)
PHI = (1 + math.sqrt(5)) / 2
ANTI = 2 - PHI
THREE = 3 / 8
CANDIDATES = {
    "one_third": 1 / 3,
    "three_eighths": THREE,
    "anti_phi": ANTI,
    "two_fifths": 0.4,
    "half": 0.5,
    "ridge": 1.0,
}


def digest(path: Path, algorithm: str = "md5") -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def locate(stem: str, pattern: str) -> dict[int, Path]:
    root = SOURCE / stem
    if (root / stem).exists():
        root = root / stem
    out = {}
    for path in root.glob(pattern):
        label = path.name.split("_")[0]
        out[int(label.replace("XS", ""))] = path
    return out


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return [{k.strip(): v for k, v in row.items()} for row in csv.DictReader(f)]


def ara(pos: float, left: float, right: float) -> float:
    return 2 * (pos - left) / (right - left)


def distance(x: float, low: float) -> float:
    return abs(x - 1) if low == 1 else min(abs(x - low), abs(x - (2 - low)))


def winner(values: list[float]) -> str:
    scores = {
        name: statistics.mean(distance(x, value) for x in values)
        for name, value in CANDIDATES.items()
    }
    return min(scores, key=scores.get)


def main() -> None:
    checks: dict[str, bool] = {}
    expected_hashes = {
        "Readme.txt": "9c75f7b197e9c19450346af41c8f553c",
        "Ground_truth_bathymetry_Level_3.zip": "5b1dd21c4f8f47f1314d9187f6552751",
        "Ground_truth_velocimetry_OttMFPro_Level_3.zip": "fe3987c878caa430627c76418ed20db3",
        "Image_velocimetry_Level_3.zip": "51abc7e2198f87c682fec7c36db890e8",
    }
    for name, expected in expected_hashes.items():
        checks[f"source_md5_{name}"] = digest(SOURCE / name) == expected

    vfiles = locate("Ground_truth_velocimetry_OttMFPro_Level_3", "*.csv")
    bfiles = locate("Ground_truth_bathymetry_Level_3", "*.csv")
    with (HERE / "H2_RONNE_AA_PHI_THREE_EIGHTHS_SECTION_RESULTS.csv").open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        saved = {int(row["section_number"]): row for row in csv.DictReader(f)}

    flow_values, depth_values = [], []
    for section in SECTIONS:
        velocity = read_csv(vfiles[section])
        xs = [float(row["Distance along line (m)"]) for row in velocity]
        speeds = [float(row["Surface velocity (cm/s)"]) for row in velocity]
        left, right = min(xs), max(xs)
        checks[f"XS{section}_zero_bank_endpoints"] = (
            speeds[xs.index(left)] == 0 and speeds[xs.index(right)] == 0
        )
        top_speed = max(speeds)
        flow_pos = statistics.median(x for x, v in zip(xs, speeds) if v == top_speed)
        flow_value = ara(flow_pos, left, right)

        bathy = read_csv(bfiles[section])
        wet = [
            row
            for row in bathy
            if left <= float(row["XS coordinate (m)"]) <= right
        ]
        low_elevation = min(float(row["Elevation"]) for row in wet)
        depth_pos = statistics.median(
            float(row["XS coordinate (m)"])
            for row in wet
            if float(row["Elevation"]) == low_elevation
        )
        depth_value = ara(depth_pos, left, right)
        flow_values.append(flow_value)
        depth_values.append(depth_value)
        checks[f"XS{section}_flow_coordinate"] = math.isclose(
            flow_value, float(saved[section]["flow_ara"]), abs_tol=1e-12
        )
        checks[f"XS{section}_depth_coordinate"] = math.isclose(
            depth_value, float(saved[section]["depth_ara"]), abs_tol=1e-12
        )

    checks["direct_flow_winner_is_ridge"] = winner(flow_values) == "ridge"
    checks["bed_structure_winner_is_half"] = winner(depth_values) == "half"
    checks["all_direct_folded_points_above_anti_phi"] = all(
        min(x, 2 - x) >= ANTI for x in flow_values
    )
    checks["all_depth_folded_points_above_anti_phi"] = all(
        min(x, 2 - x) >= ANTI for x in depth_values
    )
    checks["nested_delta_is_forced_for_direct"] = all(
        math.isclose(
            distance(x, ANTI) - distance(x, THREE),
            -(ANTI - THREE),
            abs_tol=1e-12,
        )
        for x in flow_values
    )
    checks["nested_delta_is_forced_for_depth"] = all(
        math.isclose(
            distance(x, ANTI) - distance(x, THREE),
            -(ANTI - THREE),
            abs_tol=1e-12,
        )
        for x in depth_values
    )

    with (HERE / "H2_RONNE_AA_PHI_THREE_EIGHTHS_RESULTS.json").open(
        "r", encoding="utf-8"
    ) as f:
        result = json.load(f)
    checks["primary_resolution_gate_zero_of_five"] = (
        result["resolution_gate"]["direct_flow_sections_passing"] == 0
        and result["resolution_gate"]["bed_sections_passing"] == 0
    )
    checks["result_records_not_supported_and_inconclusive_parts"] = (
        "NOT SUPPORTED" in result["geometry_verdict"]
        and "INCONCLUSIVE" in result["geometry_verdict"]
    )
    checks["figure_exists"] = (
        HERE / "H2_RONNE_AA_PHI_THREE_EIGHTHS_FIGURE.png"
    ).exists()

    validation = {
        "test_id": "T315/H2 independent validation",
        "passed": all(checks.values()),
        "passed_checks": sum(checks.values()),
        "total_checks": len(checks),
        "checks": checks,
        "output_sha256": {
            name: digest(HERE / name, "sha256")
            for name in [
                "H2_RONNE_AA_PHI_THREE_EIGHTHS_RESULTS.json",
                "H2_RONNE_AA_PHI_THREE_EIGHTHS_SECTION_RESULTS.csv",
                "H2_RONNE_AA_PHI_THREE_EIGHTHS_CANDIDATE_SUMMARY.csv",
                "H2_RONNE_AA_PHI_THREE_EIGHTHS_FIGURE.png",
            ]
        },
    }
    with (HERE / "H2_RONNE_AA_PHI_THREE_EIGHTHS_VALIDATION.json").open(
        "w", encoding="utf-8"
    ) as f:
        json.dump(validation, f, indent=2)
    print(json.dumps(validation, indent=2))
    if not validation["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

