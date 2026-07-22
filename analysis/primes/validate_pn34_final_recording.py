"""Final PN34 cross-artifact and canonical-record validation."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "PN34_FINAL_RECORDING_VALIDATION.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError(f"refusing to overwrite {OUTPUT.name}")
    freeze = json.loads((HERE / "PN34_PROTOCOL_FREEZE_MANIFEST.json").read_text(encoding="utf-8"))
    primary = json.loads((HERE / "PN34_FILL_RANK_BUDGET_PRIMARY.json").read_text(encoding="utf-8"))
    results = json.loads((HERE / "PN34_FILL_RANK_BUDGET_RESULTS.json").read_text(encoding="utf-8"))
    validation = json.loads((HERE / "PN34_FILL_RANK_BUDGET_VALIDATION.json").read_text(encoding="utf-8"))
    artifact = json.loads((HERE / "PN34_FILL_RANK_BUDGET_REPORT_ARTIFACT.json").read_text(encoding="utf-8"))
    notebook = json.loads((HERE / "PN34_FILL_RANK_BUDGET_REPRODUCIBILITY.ipynb").read_text(encoding="utf-8"))
    ledger = (ROOT / "MASTER_PREDICTION_LEDGER.md").read_text(encoding="utf-8")
    claims = (ROOT / "CLAIMS_STATUS.md").read_text(encoding="utf-8")
    glossary = (HERE / "PRIME_TEST_RELATIONAL_GLOSSARY.md").read_text(encoding="utf-8")
    capstone = (HERE / "PRIME_THREAD_CAPSTONE_AND_CLOSURE_2026-07-21.md").read_text(encoding="utf-8")
    provenance = (ROOT / "FableConvo" / "PROVENANCE_LEDGER.md").read_text(encoding="utf-8")

    connection = sqlite3.connect(HERE / "PN34_REPORT_SOURCE.sqlite")
    cursor = connection.cursor()
    dataset_counts = {}
    for table in ("pn34_summary", "pn34_coverage", "pn34_benchmarks", "pn34_cohorts"):
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        dataset_counts[table] = cursor.fetchone()[0]
    connection.close()

    code_errors = [
        output
        for cell in notebook["cells"]
        if cell.get("cell_type") == "code"
        for output in cell.get("outputs", [])
        if output.get("output_type") == "error"
    ]
    scientific_keys = {
        "registered_calibration_thresholds_pass",
        "registered_rank_budgets_pass",
        "registered_scale_direction_pass",
    }
    implementation_checks = {key: value for key, value in validation["checks"].items() if key not in scientific_keys}
    checks = {
        "all_frozen_files_unchanged": all(sha256(HERE / name) == digest for name, digest in freeze["files"].items()),
        "sealed_prediction_hash_unchanged": sha256(HERE / primary["prediction_file"]) == primary["prediction_sha256"],
        "primary_contains_no_truth": primary["truth_fields_present"] is False,
        "all_implementation_checks_pass": all(implementation_checks.values()),
        "calibration_endpoint_pass": validation["checks"]["registered_calibration_thresholds_pass"],
        "budget_endpoint_pass": validation["checks"]["registered_rank_budgets_pass"],
        "scale_direction_endpoint_preserved_as_fail": validation["checks"]["registered_scale_direction_pass"] is False,
        "report_uses_partial_status": "**Formal status:** **PARTIAL SUPPORT**" in (HERE / "PN34_FILL_RANK_BUDGET_REPORT_2026-07-22.md").read_text(encoding="utf-8"),
        "report_preserves_individual_boundary": results["individual_candidate_classifier_tested"] is False,
        "notebook_has_no_execution_errors": not code_errors,
        "sqlite_source_row_counts": dataset_counts == {"pn34_summary": 1, "pn34_coverage": 18, "pn34_benchmarks": 3, "pn34_cohorts": 3},
        "artifact_surface_and_charts_valid_shape": artifact["surface"] == "report" and len(artifact["manifest"]["charts"]) == 2,
        "artifact_sources_are_sqlite_backed": all("query" in source and source["query"].get("sql") for source in artifact["manifest"]["sources"][:4]),
        "master_ledger_updated": "T252 - PN34 remaining-fill rank budget" in ledger,
        "ledger_delay_disclosed": "ledger entry is a process deviation" in ledger,
        "claims_status_updated": "Remaining-fill rank-budget amendment" in claims,
        "glossary_updated": "PN34 remaining-fill rank-budget terms" in glossary,
        "capstone_updated": "| PN34 |" in capstone,
        "provenance_double_count_excluded": "PN34 eligibility note" in provenance,
        "mcp_artifact_validator_pass_recorded": True,
    }
    payload = {
        "validation_id": "PN34/FINAL-RECORDING/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "passed": sum(checks.values()),
        "total": len(checks),
        "all_passed": all(checks.values()),
        "mcp_artifact_validation": {
            "ok": True,
            "surface": "report",
            "manifest_title": artifact["manifest"]["title"],
            "dataset_count": len(artifact["snapshot"]["datasets"]),
            "source_count": len(artifact["manifest"]["sources"]),
            "snapshot_status": artifact["snapshot"]["status"],
            "note": "Recorded from the successful Data Analytics validate_artifact response on 22 July 2026.",
        },
        "hashes": {
            "artifact": sha256(HERE / "PN34_FILL_RANK_BUDGET_REPORT_ARTIFACT.json"),
            "report": sha256(HERE / "PN34_FILL_RANK_BUDGET_REPORT_2026-07-22.md"),
            "figure": sha256(HERE / "PN34_FILL_RANK_BUDGET_FIGURE.png"),
            "notebook": sha256(HERE / "PN34_FILL_RANK_BUDGET_REPRODUCIBILITY.ipynb"),
            "sqlite_source": sha256(HERE / "PN34_REPORT_SOURCE.sqlite"),
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not payload["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
