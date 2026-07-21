"""Hash the complete PN10B artifact packet."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT = HERE / "PN10B_COMPLETE_MANIFEST.json"

local_files = [
    "PN10B_CHILD_PHASE_PRIME_RANKING_PROTOCOL.md",
    "PN10B_FREEZE_MANIFEST.json",
    "pn10b_child_phase_prime_ranking.py",
    "PN10B_CHILD_PHASE_RESULTS.json",
    "PN10B_FRESH_TARGET_SCORES.csv",
    "PN10B_MODEL_METRICS.csv",
    "PN10B_FRESH_COMPARISONS.csv",
    "PN10B_CHILD_PHASE_FIGURE.png",
    "pn10b_validate_child_phase.py",
    "PN10B_CHILD_PHASE_VALIDATION.json",
    "PN10B_CHILD_PHASE_PRIME_RANKING_REPORT.md",
    "pn10b_build_notebook.py",
    "PN10B_CHILD_PHASE_PRIME_RANKING.ipynb",
    "PN10B_NOTEBOOK_EXECUTION_VALIDATION.json",
    "pn10b_build_report_artifact.py",
    "pn10b_report_metrics.sql",
    "pn10b_report_comparisons.sql",
    "PN10B_REPORT_ARTIFACT.json",
    "PN10B_REPORT_ARTIFACT_VALIDATION.json",
    "PN10B_REPORT_ARTIFACT_RENDER_RECEIPT.json",
    "pn10b_event_geometry_diagnostic.py",
    "PN10B_EVENT_GEOMETRY_RESULTS.json",
    "PN10B_EVENT_CENTERED_TRACES.csv",
    "PN10B_CHILD_LANDMARK_COUNTS.csv",
    "PN10B_PRIME_CHILD_EXAMPLES.csv",
    "PN10B_EXAMPLE_NEIGHBORHOODS.csv",
    "PN10B_EVENT_GEOMETRY_FIGURE.png",
    "pn10b_validate_event_geometry.py",
    "PN10B_EVENT_GEOMETRY_VALIDATION.json",
    "PN10B_EVENT_CENTERED_GEOMETRY_REPORT.md",
    "pn10b_build_event_geometry_notebook.py",
    "PN10B_EVENT_GEOMETRY_DIAGNOSTIC.ipynb",
    "PN10B_EVENT_NOTEBOOK_VALIDATION.json",
    "pn10b_report_event_trace.sql",
    "pn10b_report_child_rank.sql",
    "pn10b_report_geometry_population.sql",
    "pn10b_report_worked_prime.sql",
    "pn10b_build_complete_manifest.py",
    "PRIME_TEST_RELATIONAL_GLOSSARY.md",
]
shared_files = [
    REPO / "MASTER_PREDICTION_LEDGER.md",
    REPO / "FableConvo" / "ARA_MAPPING_PRIMES.md",
    REPO / "FableConvo" / "TEST_PROTOCOL.md",
    REPO / "FableConvo" / "CANON_FOR_AI.md",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


artifacts = {name: sha(HERE / name) for name in local_files}
for path in shared_files:
    artifacts[str(path.relative_to(REPO)).replace("\\", "/")] = sha(path)

result = json.loads((HERE / "PN10B_CHILD_PHASE_RESULTS.json").read_text(encoding="utf-8"))
validation = json.loads((HERE / "PN10B_CHILD_PHASE_VALIDATION.json").read_text(encoding="utf-8"))
notebook_validation = json.loads((HERE / "PN10B_NOTEBOOK_EXECUTION_VALIDATION.json").read_text(encoding="utf-8"))
geometry_validation = json.loads((HERE / "PN10B_EVENT_GEOMETRY_VALIDATION.json").read_text(encoding="utf-8"))
geometry_notebook_validation = json.loads((HERE / "PN10B_EVENT_NOTEBOOK_VALIDATION.json").read_text(encoding="utf-8"))
payload = {
    "test_id": result["test_id"],
    "created": "2026-07-20",
    "evidence_class": "registered development transfer plus fresh untouched-interval evaluation, with separately labelled post-hoc descriptive geometry disclosure",
    "registered_criteria": result["criteria"],
    "registered_verdict": result["verdict"],
    "protected_material": result["protected_material"],
    "artifacts": artifacts,
    "validation": {
        "independent_status": "PASS" if validation["all_passed"] else "FAIL",
        "independent_checks": f"{validation['checks_passed']}/{validation['checks_total']}",
        "notebook_status": notebook_validation["status"],
        "notebook_code_cells": notebook_validation["code_cells"],
        "notebook_error_outputs": notebook_validation["error_outputs"],
        "report_artifact_status": "PASS",
        "report_delivery": "single successful Data Analytics MCP report render after validation",
        "post_hoc_geometry_status": "PASS" if geometry_validation["passed"] else "FAIL",
        "post_hoc_geometry_checks": f"{geometry_validation['checks_passed']}/{geometry_validation['checks_total']}",
        "post_hoc_notebook_status": geometry_notebook_validation["status"],
        "post_hoc_notebook_code_cells": geometry_notebook_validation["code_cells"],
        "post_hoc_notebook_error_outputs": geometry_notebook_validation["error_outputs"],
    },
    "post_hoc_geometry_boundary": {
        "registered_verdict_changed": False,
        "claim": "Exact parent event ridge plus broad but non-discriminating paid-gate child geometry",
        "report": "PN10B_EVENT_CENTERED_GEOMETRY_REPORT.md",
    },
}
OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(OUT)
