"""Build the final PN18 file manifest after all artifacts pass validation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "PN18_COMPLETE_MANIFEST.json"
FILES = [
    "PN18_RECURSIVE_TEARA_PRODUCT_TREE_PROTOCOL_v1_FROZEN.md",
    "PN18_TARGET_FREEZE_MANIFEST.json",
    "pn18_recursive_teara_product_tree.py",
    "PN18_RECURSIVE_TEARA_PRODUCT_TREE_PREDICTION.json",
    "PN18_TARGET_CHILD_PRODUCT_ROOT.bin",
    "validate_pn18_recursive_teara_product_tree.py",
    "PN18_VALIDATOR_SERIALIZATION_AMENDMENT.json",
    "validate_pn18_recursive_teara_product_tree_v1_1.py",
    "PN18_RECURSIVE_TEARA_PRODUCT_TREE_VALIDATION.json",
    "pn18_cost_audit.py",
    "PN18_COST_AUDIT.json",
    "build_pn18_notebook.py",
    "PN18_RECURSIVE_TEARA_PRODUCT_TREE.ipynb",
    "PN18_NOTEBOOK_EXECUTION_VALIDATION.json",
    "PN18_RECURSIVE_TEARA_PRODUCT_TREE_REPORT.md",
    "PRIME_TEST_RELATIONAL_GLOSSARY.md",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError("PN18 complete manifest already exists; refusing to overwrite")
    prediction = json.loads((HERE / "PN18_RECURSIVE_TEARA_PRODUCT_TREE_PREDICTION.json").read_text(encoding="utf-8"))
    validation = json.loads((HERE / "PN18_RECURSIVE_TEARA_PRODUCT_TREE_VALIDATION.json").read_text(encoding="utf-8"))
    notebook = json.loads((HERE / "PN18_NOTEBOOK_EXECUTION_VALIDATION.json").read_text(encoding="utf-8"))
    if not validation["all_passed"] or notebook["status"] != "PASS":
        raise RuntimeError("PN18 validation is not complete")
    payload = {
        "test_id": "PN18/RECURSIVE-TEARA-PRODUCT-TREE/v1",
        "status": "complete_with_documented_v1_validator_serialization_amendment",
        "anchor": prediction["target"]["anchor"],
        "sealed_correction": prediction["target"]["correction"],
        "sealed_prediction": prediction["target"]["predicted_integer"],
        "independent_validation": f"{validation['passed_count']}/{validation['check_count']}",
        "headline": (
            "Exact recursive product-tree/GCD crosswalk on a fresh anchor; operational repackaging, "
            "not genuine information compression or a speed improvement."
        ),
        "files": [
            {"path": name, "bytes": (HERE / name).stat().st_size, "sha256": sha256(HERE / name)}
            for name in FILES
        ],
        "protected_material": "The p31 full primorial wheel and unrelated R12 prime-gap target remain unopened.",
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
