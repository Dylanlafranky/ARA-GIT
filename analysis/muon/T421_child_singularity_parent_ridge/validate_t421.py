#!/usr/bin/env python3
"""Independent saved-artifact validation for T421."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
FREEZE = HERE / "T421_DEVELOPMENT_FREEZE.json"
PROTOCOL = HERE / "T421_FROZEN_PROTOCOL.md"
ANALYSIS = HERE / "t421_child_singularity_parent_ridge.py"
STAGES = ("DEVELOPMENT", "VALIDATION", "HOLDOUT")
SEED = 421
BOOTSTRAPS = 10_000


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def groups(rows: list[dict[str, str]]) -> dict[tuple[str, str], list[dict[str, str]]]:
    output: dict[tuple[str, str], list[dict[str, str]]] = {}
    for row in rows:
        output.setdefault((row["run"], row["period"]), []).append(row)
    for key in output:
        output[key].sort(key=lambda item: float(item["time_us"]))
    return output


def at(series: np.ndarray, position: float) -> float:
    lo = int(np.floor(position))
    hi = min(lo + 1, len(series) - 1)
    fraction = position - lo
    return float(series[lo] + fraction * (series[hi] - series[lo]))


def zero_lag_events(rows: list[dict[str, str]]) -> list[dict[str, float]]:
    events: list[dict[str, float]] = []
    for _, trace in sorted(groups(rows).items()):
        u = np.asarray([float(row["openness_U"]) for row in trace])
        r = np.asarray([float(row["closure_R"]) for row in trace])
        h = np.asarray([float(row["parent_H"]) for row in trace])
        field = float(trace[0]["field_G"])
        history = float(np.median(np.abs(h - 1.0)))
        for index in range(1, len(trace)):
            da = u[index - 1] - r[index - 1]
            db = u[index] - r[index]
            if da == 0.0:
                fraction = 0.0
            elif db == 0.0:
                fraction = 1.0
            elif da * db > 0.0:
                continue
            else:
                fraction = float(-da / (db - da))
            if not 0.0 <= fraction <= 1.0:
                continue
            position = index - 1 + fraction
            distance = abs(at(h, position) - 1.0)
            events.append({"field_G": field, "distance": distance, "exposure": history - distance})
    return events


def field_medians(rows: list[dict[str, float]], key: str) -> np.ndarray:
    values = []
    for field in sorted({row["field_G"] for row in rows}):
        sample = [row[key] for row in rows if row["field_G"] == field and np.isfinite(row[key])]
        if sample:
            values.append(float(np.median(sample)))
    return np.asarray(values, dtype=float)


def bootstrap(values: np.ndarray, seed: int) -> dict:
    if len(values) == 0:
        return {"median": None, "ci95": [None, None], "field_count": 0}
    rng = np.random.default_rng(seed)
    draws = rng.choice(values, size=(BOOTSTRAPS, len(values)), replace=True)
    medians = np.median(draws, axis=1)
    return {
        "median": float(np.median(values)),
        "ci95": [float(np.percentile(medians, 2.5)), float(np.percentile(medians, 97.5))],
        "field_count": int(len(values)),
    }


def close(a: float, b: float, tolerance: float = 1e-12) -> bool:
    return bool(np.isclose(a, b, rtol=0.0, atol=tolerance))


def main() -> None:
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    checks = {
        "freeze_analysis_hash": freeze["analysis_sha256"] == sha256(ANALYSIS),
        "freeze_protocol_hash": freeze["protocol_sha256"] == sha256(PROTOCOL),
        "selected_lag_is_development_frozen": int(freeze["selected_lag_reads"]) == -6,
        "orientation_is_development_frozen": int(freeze["orientation_sign"]) == -1,
    }
    stages = {}
    for index, stage in enumerate(STAGES):
        result = json.loads((RESULTS / f"T421_{stage}_RESULTS.json").read_text(encoding="utf-8"))
        timeline = read_csv(RESULTS / f"T421_{stage}_TIMELINE.csv")
        lag_events = read_csv(RESULTS / f"T421_{stage}_EVENTS.csv")
        events = zero_lag_events(timeline)
        estimate = bootstrap(field_medians(events, "exposure"), SEED + 1)
        reported = result["crossing"]["zero_lag_exposure"]
        stage_checks = {
            "analysis_hash": result["analysis_sha256"] == sha256(ANALYSIS),
            "protocol_hash": result["protocol_sha256"] == sha256(PROTOCOL),
            "zero_event_count": len(events) == int(result["zero_lag_event_count"]),
            "lag_event_count": len(lag_events) == int(result["event_count"]),
            "literal_median": close(estimate["median"], float(reported["median"])),
            "literal_ci_lower": close(estimate["ci95"][0], float(reported["ci95"][0])),
            "literal_ci_upper": close(estimate["ci95"][1], float(reported["ci95"][1])),
            "literal_gate": bool(result["gates"]["G2_literal_hierarchy"]["pass"]) == (estimate["ci95"][0] > 0.0),
        }
        if stage == "HOLDOUT":
            stage_checks["frozen_offset_unavailable"] = (
                len(lag_events) == 0
                and not result["gates"]["G3_frozen_offset_hierarchy"]["pass"]
                and not result["gates"]["G4_timing_specificity"]["available"]
                and not result["gates"]["G4_timing_specificity"]["pass"]
            )
        stages[stage.lower()] = {
            "checks": stage_checks,
            "recomputed_zero_lag_exposure": estimate,
            "reported_zero_lag_exposure": reported,
            "zero_lag_event_count": len(events),
            "frozen_lag_event_count": len(lag_events),
        }
        checks[f"{stage.lower()}_all"] = all(stage_checks.values())
    payload = {
        "test": "T421 independent saved-artifact validation",
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "stages": stages,
    }
    path = RESULTS / "T421_INDEPENDENT_VALIDATION.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
