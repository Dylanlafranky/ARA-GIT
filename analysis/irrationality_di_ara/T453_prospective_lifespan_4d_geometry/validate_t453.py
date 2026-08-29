"""Independent arithmetic and packaging checks for T453."""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(r"F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\irrationality_di_ara\T453_prospective_lifespan_4d_geometry")
RESULTS = ROOT / "results"


def check(name, passed, detail):
    return {"check": name, "passed": bool(passed), "detail": detail}


def main():
    checks = []
    prefixes = pd.read_csv(RESULTS / "T453_PREFIX_STATES.csv")
    predictions = pd.read_csv(RESULTS / "T453_PREDICTIONS.csv")
    regression = pd.read_csv(RESULTS / "T453_REGRESSION_METRICS.csv")
    classification = pd.read_csv(RESULTS / "T453_CLASSIFICATION_METRICS.csv")
    gates = pd.read_csv(RESULTS / "T453_FROZEN_GATES.csv")
    result = json.loads((RESULTS / "T453_RESULT.json").read_text(encoding="utf-8"))

    forbidden_predictor_columns = {"observed_g1_count", "lifespan_hours_observed", "maturity_A", "time_elapsed_B", "time_remaining_B", "time_shadow"}
    overlap = forbidden_predictor_columns.intersection(prefixes.columns)
    checks.append(check("no completed-life predictor columns", not overlap, f"forbidden columns present: {sorted(overlap)}"))
    checks.append(check("all prefixes retain an unseen future", bool((prefixes.remaining_divisions > 0).all() and (prefixes.remaining_hours > 0).all()), f"minimum remainder: {prefixes.remaining_divisions.min()} divisions, {prefixes.remaining_hours.min():.3f} hours"))
    checks.append(check("frozen split counts", result["cells_by_split"] == {"development": 86, "external": 119, "holdout": 12}, str(result["cells_by_split"])))
    checks.append(check("four-coordinate model limited to Rpl13A holdout", not ((predictions.split == "external") & (predictions.model == "sphere4_candidate")).any(), "no external sphere4 rows expected"))
    checks.append(check("prediction key uniqueness", not predictions.duplicated(["split", "outcome", "model", "row_id"]).any(), f"rows={len(predictions):,}"))

    max_metric_diff = 0.0
    for _, row in regression.iterrows():
        sub = predictions[(predictions.split == row.split) & (predictions.outcome == row.outcome) & (predictions.model == row.model)]
        err = sub.prediction - sub.actual
        per_cell = pd.DataFrame({"cell": sub.cell_key, "ae": np.abs(err)}).groupby("cell").ae.mean().mean()
        max_metric_diff = max(max_metric_diff, abs(float(per_cell) - float(row.cell_mean_mae)))
    checks.append(check("regression metrics reproduce from prediction ledger", max_metric_diff < 1e-10, f"maximum absolute difference={max_metric_diff:.3g}"))

    auc_ok = classification.auroc.dropna().between(0, 1).all()
    brier_ok = classification.brier.dropna().between(0, 1).all()
    checks.append(check("classification metric ranges", bool(auc_ok and brier_ok), f"AUROC [{classification.auroc.min():.3f}, {classification.auroc.max():.3f}], Brier [{classification.brier.min():.3f}, {classification.brier.max():.3f}]"))
    checks.append(check("frozen gate total", len(gates) == 6 and int(gates.passed.astype(str).str.lower().eq("true").sum()) == result["gates_passed"], f"{result['gates_passed']}/6 pass"))

    report = RESULTS / "T453_PROSPECTIVE_LIFESPAN_4D_REPORT.html"
    text = report.read_text(encoding="utf-8")
    image_refs = re.findall(r"<img[^>]+src=['\"]([^'\"]+)", text)
    missing = [ref for ref in image_refs if not (RESULTS / ref).exists()]
    checks.append(check("report image references resolve", not missing and len(image_refs) == 6, f"{len(image_refs)} images; missing={missing}"))
    checks.append(check("report contains essential limits", all(term in text for term in ["not yet a hidden Time wave", "not a metaphysical death time", "not an independent sphere discovery"]), "three interpretation boundaries present"))

    passed = sum(c["passed"] for c in checks)
    validation = {
        "test": "T453",
        "checks_passed": passed,
        "checks_total": len(checks),
        "all_passed": passed == len(checks),
        "assessment": "Share with caveats" if passed == len(checks) else "Do not share until failed checks are resolved",
        "checks": checks,
    }
    (RESULTS / "T453_VALIDATION.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))
    raise SystemExit(0 if validation["all_passed"] else 1)


if __name__ == "__main__":
    main()
