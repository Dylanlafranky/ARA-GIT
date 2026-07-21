from __future__ import annotations

import json
import math
import sqlite3
from pathlib import Path


HERE = Path(__file__).resolve().parent
ARTIFACT = HERE / "PN8_REPORT_ARTIFACT.json"
OUTPUT = HERE / "PN8_REPORT_SOURCE_VALIDATION.json"


def query_rows(path: Path) -> list[dict[str, object]]:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in connection.execute(path.read_text(encoding="utf-8"))]
    finally:
        connection.close()


def rows_equal(actual: list[dict[str, object]], expected: list[dict[str, object]]) -> bool:
    if len(actual) != len(expected):
        return False
    for actual_row, expected_row in zip(actual, expected):
        if actual_row.keys() != expected_row.keys():
            return False
        for key in actual_row:
            left, right = actual_row[key], expected_row[key]
            if isinstance(left, float) or isinstance(right, float):
                if not math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=1e-12):
                    return False
            elif left != right:
                return False
    return True


def main() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    expected = artifact["snapshot"]["datasets"]
    checks = {
        "model_metrics_sql_matches_snapshot": rows_equal(
            query_rows(HERE / "pn8_report_model_metrics.sql"), expected["model_metrics"]
        ),
        "target_results_sql_matches_snapshot": rows_equal(
            query_rows(HERE / "pn8_report_target_results.sql"), expected["target_results"]
        ),
    }
    report = {
        "artifact": ARTIFACT.name,
        "checks": checks,
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "all_passed": all(checks.values()),
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

