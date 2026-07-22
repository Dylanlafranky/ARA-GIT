"""Validate PN25's durable recording and source linkage."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "PN25_RECORDING_VALIDATION.json"
REQUIRED = (
    "PN25_PAIR_RIDGE_COMPRESSION_PROTOCOL_v1_FROZEN.md",
    "pn25_pair_ridge_compression.py",
    "PN25_PAIR_RIDGE_COMPRESSION_RESULTS.json",
    "PN25_PAIR_RIDGE_COMPRESSION_TARGETS.csv",
    "PN25_PAIR_RIDGE_COMPRESSION_GROUPS.csv",
    "PN25_PAIR_RIDGE_COMPRESSION_SCORES.csv",
    "validate_pn25_pair_ridge_compression.py",
    "PN25_PAIR_RIDGE_COMPRESSION_VALIDATION.json",
    "PN25_PAIR_RIDGE_COMPRESSION_REPORT.md",
    "build_pn25_notebook.py",
    "PN25_PAIR_RIDGE_COMPRESSION_REPRODUCIBILITY.ipynb",
    "PN25_NOTEBOOK_EXECUTION_VALIDATION.json",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError(f"refusing to overwrite {OUTPUT.name}")
    checks: list[dict] = []

    def add(name: str, passed: bool, detail: str = "") -> None:
        checks.append({"name": name, "pass": bool(passed), "detail": detail})

    missing = [name for name in REQUIRED if not (HERE / name).exists()]
    add("all primary artifacts exist", not missing, str(missing))
    results = json.loads((HERE / "PN25_PAIR_RIDGE_COMPRESSION_RESULTS.json").read_text(encoding="utf-8"))
    validation = json.loads((HERE / "PN25_PAIR_RIDGE_COMPRESSION_VALIDATION.json").read_text(encoding="utf-8"))
    notebook = json.loads((HERE / "PN25_NOTEBOOK_EXECUTION_VALIDATION.json").read_text(encoding="utf-8"))
    report = (HERE / "PN25_PAIR_RIDGE_COMPRESSION_REPORT.md").read_text(encoding="utf-8")

    add("status recorded correctly", results["status"] == "GEOMETRIC-ONLY SUPPORT / DYNAMIC NULL")
    add("independent validation passed", validation["status"] == "PASS" and validation["checks_passed"] == 14)
    add("notebook executed cleanly", notebook["status"] == "PASS" and notebook["code_cells_executed"] == notebook["code_cells_total"])
    add(
        "report records exact conversion",
        "\\frac{2q}{1+q}" in report and "\\frac a7" in report and "x_A+x_B=2" in report,
    )
    add("report records pooled correlation", "+0.003335" in report)
    add("report records permutation result", "p=0.6110" in report)
    add("report records 0 of 4 dynamic pass", "P4 — paths move upward toward the ridge | **FAILED**" in report)
    add("report preserves lateral versus vertical distinction", "lateral coordinate inside the mod-14 wheel" in report)

    docs = {
        ROOT / "CLAIMS_STATUS.md": "PN25",
        ROOT / "ARA_AXIOMATIC_PROOFS_AND_DOMAIN_SUBSETS.md": "Theorem 29",
        ROOT / "ARA_FOUNDATIONS_FROM_ESTABLISHED_MECHANICS.md": "Pair odds are a lateral wheel coordinate",
        HERE / "PRIME_TEST_RELATIONAL_GLOSSARY.md": "Odds-to-ARA transform",
        HERE / "PRIME_THREAD_CAPSTONE_AND_CLOSURE_2026-07-21.md": "| PN25 |",
    }
    for path, needle in docs.items():
        add(f"{path.name} records PN25", needle in path.read_text(encoding="utf-8"))
    add("protected anchor remains unused", results["data"]["protected_87_bit_anchor_used"] is False)

    passed = sum(check["pass"] for check in checks)
    payload = {
        "validation_id": "PN25/RECORDING-VALIDATION/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "checks": checks,
        "sha256": {name: sha(HERE / name) for name in REQUIRED if (HERE / name).exists()},
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if payload["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
