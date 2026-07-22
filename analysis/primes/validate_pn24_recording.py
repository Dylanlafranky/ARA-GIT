"""Validate PN24's durable recording and artifact linkage."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "PN24_RECORDING_VALIDATION.json"

REQUIRED = (
    "PN24_NEAREST_HANDOVER_CASCADE_PROTOCOL_v1_FROZEN.md",
    "pn24_nearest_handover_cascade.py",
    "PN24_NEAREST_HANDOVER_CASCADE_RESULTS.json",
    "PN24_NEAREST_HANDOVER_CASCADE_ANCHORS.csv",
    "PN24_NEAREST_HANDOVER_CASCADE_EVENTS.csv",
    "PN24_NEAREST_HANDOVER_CASCADE_RUNGS.csv",
    "validate_pn24_nearest_handover_cascade.py",
    "PN24_NEAREST_HANDOVER_CASCADE_VALIDATION.json",
    "PN24_NEAREST_HANDOVER_CASCADE_REPORT.md",
    "build_pn24_notebook.py",
    "PN24_NEAREST_HANDOVER_CASCADE_REPRODUCIBILITY.ipynb",
    "PN24_NOTEBOOK_EXECUTION_VALIDATION.json",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError(f"refusing to overwrite {OUTPUT.name}")
    checks: list[dict] = []

    def add(name: str, passed: bool, detail: str = "") -> None:
        checks.append({"name": name, "pass": bool(passed), "detail": detail})

    missing = [name for name in REQUIRED if not (HERE / name).exists()]
    add("all primary PN24 artifacts exist", not missing, str(missing))

    results = json.loads((HERE / "PN24_NEAREST_HANDOVER_CASCADE_RESULTS.json").read_text(encoding="utf-8"))
    validation = json.loads((HERE / "PN24_NEAREST_HANDOVER_CASCADE_VALIDATION.json").read_text(encoding="utf-8"))
    notebook = json.loads((HERE / "PN24_NOTEBOOK_EXECUTION_VALIDATION.json").read_text(encoding="utf-8"))
    report = (HERE / "PN24_NEAREST_HANDOVER_CASCADE_REPORT.md").read_text(encoding="utf-8")

    add("primary result is partial structural support", results["status"] == "PARTIAL STRUCTURAL SUPPORT")
    add("independent validation passed", validation["status"] == "PASS" and validation["checks_passed"] == 12)
    add("notebook executed cleanly", notebook["status"] == "PASS" and notebook["code_cells_executed"] == notebook["code_cells_total"])
    add("report records 63.65 percent compact result", "63.65%" in report)
    add("report records 83.85 percent three-handover result", "83.85%" in report)
    add("report records 6,336 median gate count", "6,336" in report)
    add("report preserves no-shortcut fence", "not constitute a three-operation prime algorithm" in report)

    root_docs = {
        "CLAIMS_STATUS.md": "PN24",
        "ARA_AXIOMATIC_PROOFS_AND_DOMAIN_SUBSETS.md": "Theorem 28",
        "ARA_FOUNDATIONS_FROM_ESTABLISHED_MECHANICS.md": "Nearest-child handovers",
    }
    for relative, needle in root_docs.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        add(f"{relative} records PN24", needle in text)
    glossary = (HERE / "PRIME_TEST_RELATIONAL_GLOSSARY.md").read_text(encoding="utf-8")
    capstone = (HERE / "PRIME_THREAD_CAPSTONE_AND_CLOSURE_2026-07-21.md").read_text(encoding="utf-8")
    add("relational glossary includes PN24 terms", "Visible handover event" in glossary and "Silent gate" in glossary)
    add("prime capstone includes PN24", "| PN24 |" in capstone)
    add("protected anchor remains unused", results["data"]["protected_87_bit_anchor_used"] is False)

    passed = sum(check["pass"] for check in checks)
    payload = {
        "validation_id": "PN24/RECORDING-VALIDATION/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "checks": checks,
        "sha256": {name: digest(HERE / name) for name in REQUIRED if (HERE / name).exists()},
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if payload["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
