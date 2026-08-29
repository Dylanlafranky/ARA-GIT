#!/usr/bin/env python3
"""Independent saved-artifact validation for T423.

This validator checks arithmetic and provenance separately from scientific
interpretation.  It also records two design-availability warnings that are not
allowed to disappear merely because the saved calculations are internally
consistent.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
T421_RESULTS = HERE.parent / "T421_child_singularity_parent_ridge" / "results"
PROTOCOL = HERE / "T423_FROZEN_PROTOCOL.md"
ANALYSIS = HERE / "t423_parent_di_ara_temporal_architecture.py"
FREEZE = HERE / "T423_DEVELOPMENT_FREEZE.json"
STAGES = ("DEVELOPMENT", "VALIDATION", "HOLDOUT")
TOL = 1e-10


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def close(a: float, b: float, tolerance: float = TOL) -> bool:
    return math.isclose(float(a), float(b), rel_tol=tolerance, abs_tol=tolerance)


def model_predict(row: dict, model: dict, source: str = "correct") -> float:
    values = []
    for feature in model["features"]:
        if source == "correct" or feature in {
            "U", "R", "dU", "dR", "elapsed_us", "parent_lifespan_ARA",
            "field_turn_log2", "rf_flag", "direction_code",
        }:
            key = feature
        elif feature in {"H", "dH", "H_distance", "Q", "dQ", "Q_distance"}:
            key = f"{source}_{feature}"
        else:
            raise KeyError(feature)
        values.append(float(row[key]))
    standardized = [
        (value - float(mean)) / float(scale)
        for value, mean, scale in zip(values, model["x_mean"], model["x_scale"])
    ]
    return float(model["beta"][0]) + sum(
        float(beta) * value for beta, value in zip(model["beta"][1:], standardized)
    )


def independent_crossings(rows: list[dict]) -> list[dict]:
    found: list[dict] = []
    difference = [float(row["openness_U"]) - float(row["closure_R"]) for row in rows]
    for index in range(1, len(rows)):
        left, right = difference[index - 1], difference[index]
        if left == 0.0:
            fraction = 0.0
        elif right == 0.0:
            fraction = 1.0
        elif left * right > 0.0:
            continue
        else:
            fraction = -left / (right - left)
        if not 0.0 <= fraction <= 1.0:
            continue
        position = index - 1 + fraction
        if found and abs(position - found[-1]["position"]) < 1e-9:
            continue
        time_left = float(rows[index - 1]["time_us"])
        time_right = float(rows[index]["time_us"])
        found.append({
            "position": position,
            "time_us": time_left + fraction * (time_right - time_left),
            "direction": "R_to_U" if left < right else "U_to_R",
        })
    return found


def main() -> None:
    freeze = read_json(FREEZE)
    checks: list[dict] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    check("protocol hash", sha256(PROTOCOL) == freeze["protocol_sha256"], freeze["protocol_sha256"])
    check("analysis hash", sha256(ANALYSIS) == freeze["analysis_sha256"], freeze["analysis_sha256"])

    stage_diagnostics = {}
    for stage in STAGES:
        stage_lower = stage.lower()
        result = read_json(RESULTS / f"T423_{stage}_RESULTS.json")
        intervals = read_csv(RESULTS / f"T423_{stage}_INTERVALS.csv")
        predictions = read_csv(RESULTS / f"T423_{stage}_PREDICTIONS.csv")
        source_path = T421_RESULTS / f"T421_{stage}_TIMELINE.csv"
        summary = result["summary"]

        check(f"{stage} source hash", sha256(source_path) == result["source_sha256"], result["source_sha256"])
        check(f"{stage} protocol hash", result["protocol_sha256"] == freeze["protocol_sha256"], result["protocol_sha256"])
        check(f"{stage} analysis hash", result["analysis_sha256"] == freeze["analysis_sha256"], result["analysis_sha256"])
        check(f"{stage} interval count", len(intervals) == int(summary["interval_count"]), f"saved={len(intervals)} summary={summary['interval_count']}")
        check(f"{stage} prediction row count", len(predictions) == int(summary["prediction_row_count"]), f"saved={len(predictions)} summary={summary['prediction_row_count']}")

        groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
        for row in read_csv(source_path):
            groups[(row["run"], row["period"])].append(row)
        for rows in groups.values():
            rows.sort(key=lambda item: float(item["time_us"]))

        expected_intervals = []
        for (run, period), rows in sorted(groups.items()):
            crossing = independent_crossings(rows)
            for index in range(len(crossing) - 1):
                start, end = crossing[index], crossing[index + 1]
                if start["direction"] == end["direction"]:
                    continue
                expected_intervals.append((run, period, index, start, end))
        check(
            f"{stage} independent crossing interval count",
            len(expected_intervals) == len(intervals),
            f"independent={len(expected_intervals)} saved={len(intervals)}",
        )

        saved_by_key = {(row["run"], row["period"], int(row["interval_index"])): row for row in intervals}
        for run, period, index, start, end in expected_intervals:
            key = (run, period, index)
            saved = saved_by_key.get(key)
            check(f"{stage} interval present {run}|{period}|{index}", saved is not None, str(key))
            if saved is None:
                continue
            check(f"{stage} start time {run}|{period}|{index}", close(saved["start_time_us"], start["time_us"]), saved["start_time_us"])
            check(f"{stage} end time {run}|{period}|{index}", close(saved["end_time_us"], end["time_us"]), saved["end_time_us"])
            check(f"{stage} direction {run}|{period}|{index}", saved["start_direction"] == start["direction"] and saved["end_direction"] == end["direction"], f"{saved['start_direction']}->{saved['end_direction']}")

        usable_intervals = set()
        for row in predictions:
            remaining = float(row["end_time_us"]) - float(row["time_us"])
            check(f"{stage} causal remaining {row['interval_id']}@{row['sample_index']}", remaining > 0 and close(remaining, row["remaining_us"]), row["remaining_us"])
            usable_intervals.add(row["interval_id"])
            for model_name in ("M0", "M1", "M2"):
                predicted = model_predict(row, freeze["models"][model_name])
                check(f"{stage} {model_name} prediction {row['interval_id']}@{row['sample_index']}", close(predicted, row[f"prediction_{model_name}"]), row[f"prediction_{model_name}"])
                error = abs(predicted - remaining)
                check(f"{stage} {model_name} error {row['interval_id']}@{row['sample_index']}", close(error, row[f"absolute_error_{model_name}"]), row[f"absolute_error_{model_name}"])
            for source in ("wrong", "reverse", "shift"):
                predicted = model_predict(row, freeze["models"]["M2"], source)
                check(f"{stage} M2 {source} prediction {row['interval_id']}@{row['sample_index']}", close(predicted, row[f"prediction_M2_{source}"]), row[f"prediction_M2_{source}"])

        stage_diagnostics[stage_lower] = {
            "opposite_crossing_intervals": len(intervals),
            "intervals_with_causal_rows": len(usable_intervals),
            "causal_prediction_rows": len(predictions),
            "return_C1_intervals": int(summary["return_C1_count"]),
            "q_crossing_available_share": summary["parent_q_available_share"],
            "raw_sequences": len(groups),
        }

    check("development model training rows", all(int(model["training_rows"]) == 4 for model in freeze["models"].values()), "all frozen models use four rows")

    warnings = [
        {
            "code": "UNDERDETERMINED_DEVELOPMENT_FIT",
            "severity": "critical",
            "detail": "All three models were fitted to four causal rows from two intervals while M2 has 15 features plus an intercept. Ridge regularization makes a numerical solution possible but does not make the comparison empirically identified.",
        },
        {
            "code": "NO_OUT_OF_SAMPLE_PREDICTION_ROWS",
            "severity": "critical",
            "detail": "Validation and holdout have zero intervals containing at least two native samples between successive crossings, so no frozen model can be scored out of sample.",
        },
        {
            "code": "NO_PARENT_Q_HANDOVER",
            "severity": "critical",
            "detail": "No selected child interval in any split contains a Q=1 crossing. The proposed PA→PB internal parent traversal is therefore unobserved in this archive under the frozen cut.",
        },
        {
            "code": "G1_DOES_NOT_GUARD_MODEL_GRAIN",
            "severity": "methodological",
            "detail": "Frozen G1 counts opposite-direction crossing intervals, but the causal primary additionally needs native prediction slices inside them. G1 can therefore count an interval that supplies no model row.",
        },
    ]

    failed = [item for item in checks if not item["passed"]]
    payload = {
        "test": "T423 parent Di-ARA temporal architecture",
        "arithmetic_status": "PASS" if not failed else "FAIL",
        "scientific_adjudication": "UNAVAILABLE",
        "reason": "The saved arithmetic is reproducible, but the archive contains four development rows and no out-of-sample prediction rows or Q=1 parent handover events.",
        "check_count": len(checks),
        "passed_count": len(checks) - len(failed),
        "failed_count": len(failed),
        "stage_diagnostics": stage_diagnostics,
        "warnings": warnings,
        "checks": checks,
    }
    output = RESULTS / "T423_INDEPENDENT_VALIDATION.json"
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(output)
    print(json.dumps({key: payload[key] for key in ("arithmetic_status", "scientific_adjudication", "check_count", "passed_count", "failed_count")}, indent=2))


if __name__ == "__main__":
    main()
