#!/usr/bin/env python3
"""Independent artifact and arithmetic validator for T385."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "T385_buap_causal_irrationality_di_ara"
RAW = Path(
    r"F:\SystemFormulaFolder\DataTEsted(TOBEDELETEDBEFOREGIT)\muon_buap\MD10000Last.csv"
)
PROTOCOL = HERE / "T385_BUAP_CAUSAL_IRRATIONALITY_DI_ARA_PROTOCOL_2026-08-15.md"
EXPECTED_RAW = "C2DC1E012FBDF0F3C5EC305E2D8E4DD1D87B05DF5CBA39B492189C0F7D5454CD"
EXPECTED_PROTOCOL = "8ADFC0A09DC03E70B07F2A68B8EE950F87CCA218A344B21DDED1FAAE2003499C"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def close(a: float, b: float, tol: float = 1e-12) -> bool:
    return math.isclose(float(a), float(b), rel_tol=tol, abs_tol=tol)


def main() -> int:
    results = json.loads((OUT / "T385_RESULTS.json").read_text(encoding="utf-8"))
    scores = read_csv(OUT / "T385_MODEL_SCORES.csv")
    leads = read_csv(OUT / "T385_LEAD_PROFILE.csv")
    boot = read_csv(OUT / "T385_BOOTSTRAP_LOGLOSS_DELTA.csv")

    checks: dict[str, bool] = {}
    checks["raw_hash"] = sha256(RAW) == EXPECTED_RAW == results["source"]["sha256"]
    checks["protocol_hash"] = (
        sha256(PROTOCOL) == EXPECTED_PROTOCOL == results["source"]["protocol_sha256"]
    )
    with RAW.open("r", encoding="utf-8", errors="replace") as handle:
        checks["row_count"] = sum(1 for line in handle if line.strip()) == 5001

    score_lookup = {(r["split"], r["model"]): r for r in scores}
    score_match = True
    for split, models in results["metrics"].items():
        for model, metrics in models.items():
            row = score_lookup[(split, model)]
            for key in ("auc", "logloss", "brier"):
                score_match &= close(float(row[key]), float(metrics[key]))
            score_match &= int(row["n_events"]) == int(metrics["n_events"])
            score_match &= int(row["n_windows"]) == int(metrics["n_windows"])
    checks["score_csv_matches_json"] = score_match

    delta = [float(r["delta_logloss"]) for r in boot]
    delta.sort()
    try:
        import numpy as np

        quantiles = np.quantile(np.asarray(delta), [0.025, 0.5, 0.975])
    except Exception:
        def quantile(q: float) -> float:
            pos = q * (len(delta) - 1)
            lo = int(math.floor(pos))
            hi = int(math.ceil(pos))
            return delta[lo] * (hi - pos) + delta[hi] * (pos - lo)

        quantiles = [quantile(0.025), quantile(0.5), quantile(0.975)]
    stored = results["bootstrap_logloss_delta"]
    checks["bootstrap_quantiles"] = all(
        close(a, b, 1e-10)
        for a, b in zip(quantiles, [stored["q025"], stored["median"], stored["q975"]])
    )

    checks["status_matches_gates"] = (
        (results["decision"]["status"] == "SUPPORTED")
        == all(results["decision"]["gates"].values())
    )
    checks["512ns_profile_present"] = all(
        int(r["n"]) > 0 for r in leads if int(r["lead_ns"]) == 512
    ) and len([r for r in leads if int(r["lead_ns"]) == 512]) == 2
    checks["secondary_1p25_not_a_gate"] = not any(
        "1p25" in key or "1.25" in key for key in results["decision"]["gates"]
    )
    checks["movement_prediction_frozen"] = (
        results["secondary_landmarks"]["weighted_median_x_radial_imminent"] == 1.0
        and not results["decision"]["gates"]["movement_side_and_positive_gradient"]
    )
    checks["acquisition_leak_visible"] = results["controls"]["forbidden leakage"] > 0.99
    checks["primary_excludes_forbidden_fields"] = True
    script_text = (HERE / "t385_buap_causal_irrationality_di_ara.py").read_text(encoding="utf-8")
    ma_block = script_text.split('"MA": [', 1)[1].split('],', 1)[0]
    checks["primary_excludes_forbidden_fields"] = (
        "row_samples" not in ma_block and "remaining_to_end_us" not in ma_block
    )

    checks["figure_exists"] = (OUT / "T385_BUAP_CAUSAL_IRRATIONALITY_DI_ARA_FIGURE.png").stat().st_size > 100_000
    report = (OUT / "T385_BUAP_CAUSAL_IRRATIONALITY_DI_ARA_REPORT.html").read_text(encoding="utf-8")
    checks["report_claim_ceiling"] = "Class-D detector proxy" in report and "Neutrinos were not observed" in report

    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"validator": "T385", "status": status, "checks": checks}
    (OUT / "T385_VALIDATION.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
