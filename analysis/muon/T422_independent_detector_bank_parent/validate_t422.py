#!/usr/bin/env python3
"""Independent saved-artifact audit for T422."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
MUON = HERE.parent
T421_DIR = MUON / "T421_child_singularity_parent_ridge"
sys.path.insert(0, str(T421_DIR))
import t421_child_singularity_parent_ridge as t421  # noqa: E402

SEED = 422
BOOTSTRAPS = 10000
STAGES = ("DEVELOPMENT", "VALIDATION", "HOLDOUT")
DIRECTIONS = (("F", "B", 0), ("B", "F", 20))


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def close(a, b, atol: float = 1e-12) -> bool:
    if a is None or b is None:
        return a is None and b is None
    return bool(math.isclose(float(a), float(b), rel_tol=1e-10, abs_tol=atol))


def groups(rows: list[dict], partition: str) -> dict[tuple[str, str], list[dict]]:
    output = {}
    for row in rows:
        if row["partition"] != partition:
            continue
        output.setdefault((row["run"], row["period"]), []).append(row)
    for key in output:
        output[key].sort(key=lambda item: float(item["time_us"]))
    return output


def field_values(rows: list[dict], key: str, period: str | None = None) -> dict[float, float]:
    output = {}
    for field in sorted({float(row["field_G"]) for row in rows if period is None or row["period"] == period}):
        values = [
            float(row[key]) for row in rows
            if float(row["field_G"]) == field
            and (period is None or row["period"] == period)
            and math.isfinite(float(row[key]))
        ]
        if values:
            output[field] = float(np.median(values))
    return output


def aggregate(rows: list[dict], key: str, period: str | None = None) -> float | None:
    values = list(field_values(rows, key, period).values())
    return float(np.median(values)) if values else None


def bootstrap(rows: list[dict], key: str, seed: int) -> dict:
    fields = field_values(rows, key)
    values = np.asarray([fields[name] for name in sorted(fields)], dtype=float)
    if len(values) == 0:
        return {"median": None, "ci95": [None, None], "field_count": 0}
    rng = np.random.default_rng(seed)
    draws = rng.choice(values, size=(BOOTSTRAPS, len(values)), replace=True)
    medians = np.median(draws, axis=1)
    return {
        "median": float(np.median(values)),
        "ci95": [float(np.percentile(medians, 2.5)), float(np.percentile(medians, 97.5))],
        "field_count": len(values),
    }


def same_bootstrap(a: dict, b: dict) -> bool:
    return (
        a["field_count"] == b["field_count"]
        and close(a["median"], b["median"])
        and close(a["ci95"][0], b["ci95"][0])
        and close(a["ci95"][1], b["ci95"][1])
    )


def main() -> None:
    freeze = json.loads((HERE / "T422_DEVELOPMENT_FREEZE.json").read_text(encoding="utf-8"))
    analysis = HERE / "t422_independent_detector_bank_parent.py"
    protocol = HERE / "T422_FROZEN_PROTOCOL.md"
    checks: list[dict] = []

    def check(name: str, passed: bool, detail: str = "") -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": detail})

    check("frozen protocol hash", freeze["protocol_sha256"] == sha256(protocol))
    check("frozen analysis hash", freeze["analysis_sha256"] == sha256(analysis))
    f_set = set(freeze["partitions_zero_based"]["F"])
    b_set = set(freeze["partitions_zero_based"]["B"])
    check("primary detector banks are disjoint", not (f_set & b_set), f"overlap={sorted(f_set & b_set)}")
    check("primary detector banks cover 96 spectra", len(f_set | b_set) == 96)

    population_audit = []
    for stage in STAGES:
        tag = stage
        result = json.loads((RESULTS / f"T422_{tag}_RESULTS.json").read_text(encoding="utf-8"))
        timeline = read_csv(RESULTS / f"T422_{tag}_TIMELINE.csv")
        events = read_csv(RESULTS / f"T422_{tag}_EVENTS.csv")
        calibration = read_csv(RESULTS / f"T422_{tag}_CALIBRATION.csv")
        shifts = read_csv(RESULTS / f"T422_{tag}_SHIFT_NULL.csv")
        check(f"{tag}: causal timeline boundary", all(float(row["time_us"]) >= 2.25 for row in timeline))
        check(f"{tag}: calibration row count", len(calibration) == int(result["calibration_rows"]))
        check(f"{tag}: timeline row count", len(timeline) == int(result["timeline_rows"]))
        check(f"{tag}: event crossings interpolate U=R", all(abs(float(row["crossing_U"]) - float(row["crossing_R"])) < 1e-10 for row in events))
        check(
            f"{tag}: event ridge-exposure arithmetic",
            all(close(float(row["ridge_exposure"]), float(row["history_parent_distance"]) - abs(float(row["parent_H"]) - 1.0)) for row in events),
        )
        check(
            f"{tag}: wrong-frequency arithmetic",
            all(close(float(row["wrong_frequency_minus_correct_distance"]), abs(float(row["wrong_parent_H"]) - 1.0) - abs(float(row["parent_H"]) - 1.0)) for row in events),
        )
        check(
            f"{tag}: lineage-control arithmetic",
            all(close(float(row["mismatch_lineage_minus_correct_distance"]), abs(float(row["mismatch_parent_H"]) - 1.0) - abs(float(row["parent_H"]) - 1.0)) for row in events),
        )

        for child, parent, seed_offset in DIRECTIONS:
            direction = f"{child}_to_{parent}"
            summary = result["directions"][direction]
            selected = [row for row in events if row["direction"] == direction]
            check(f"{tag} {direction}: saved event count", len(selected) == int(summary["event_count"]))
            check(
                f"{tag} {direction}: exposure bootstrap",
                same_bootstrap(bootstrap(selected, "ridge_exposure", SEED + seed_offset + 1), summary["ridge_exposure"]),
            )
            check(
                f"{tag} {direction}: wrong-frequency bootstrap",
                same_bootstrap(bootstrap(selected, "wrong_frequency_minus_correct_distance", SEED + seed_offset + 3), summary["wrong_frequency_effect"]),
            )
            check(
                f"{tag} {direction}: lineage bootstrap",
                same_bootstrap(bootstrap(selected, "mismatch_lineage_minus_correct_distance", SEED + seed_offset + 4), summary["mismatch_lineage_effect"]),
            )
            for period in ("RF on", "RF off"):
                check(
                    f"{tag} {direction}: {period} exposure",
                    close(aggregate(selected, "ridge_exposure", period), summary["rf_exposure"][period]),
                )

            child_groups = groups(timeline, child)
            crossing_keys = {key for key, rows in child_groups.items() if t421.crossing_positions(rows)}
            event_keys = {(row["run"], row["period"]) for row in selected}
            population_match = crossing_keys == event_keys
            population_audit.append({
                "stage": tag.title(), "direction": direction,
                "all_crossing_sequences": len(crossing_keys),
                "real_event_sequences": len(event_keys),
                "same_population_for_shift": int(population_match),
            })
            check(
                f"{tag} {direction}: shift-null population matches real events",
                population_match,
                f"crossing={len(crossing_keys)}, real={len(event_keys)}",
            )

            stage_shifts = np.asarray([
                float(row["parent_ridge_distance"]) for row in shifts if row["direction"] == direction
            ])
            if len(selected):
                real = aggregate(selected, "parent_ridge_distance")
                empirical_p = float((1 + np.count_nonzero(stage_shifts <= real)) / (1 + len(stage_shifts)))
                check(f"{tag} {direction}: saved timing p", close(empirical_p, summary["shift"]["empirical_p"]))
            else:
                check(f"{tag} {direction}: empty timing result", summary["shift"]["empirical_p"] is None)

        for run, expected in result["source_hashes"].items():
            raw = t421.t416.t414.RAW / f"{run}.nxs"
            check(f"{tag}: source hash {run}", raw.exists() and sha256(raw) == expected)

    all_pass = all(item["pass"] for item in checks)
    output = {
        "test": "T422 independent saved-artifact validation",
        "all_checks_pass": all_pass,
        "check_count": len(checks),
        "passed_count": sum(item["pass"] for item in checks),
        "checks": checks,
        "shift_population_audit": population_audit,
        "validator_sha256": sha256(Path(__file__).resolve()),
    }
    path = RESULTS / "T422_INDEPENDENT_VALIDATION.json"
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))
    raise SystemExit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
