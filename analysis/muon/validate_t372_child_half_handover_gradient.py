"""Independent artifact/arithmetic checks for T372."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULT = HERE / "T372_CHILD_HALF_HANDOVER_GRADIENT_RESULTS.json"


def main() -> None:
    r = json.loads(RESULT.read_text(encoding="utf-8"))
    with (HERE / "T372_CHILD_HALF_HANDOVER_GRADIENT.csv").open(encoding="utf-8") as f:
        gradient = list(csv.DictReader(f))
    with (HERE / "T372_CHILD_HALF_HANDOVER_ENERGY_CUTS.csv").open(encoding="utf-8") as f:
        energy = list(csv.DictReader(f))

    x = np.array([float(z["cumulative_ara_at_handover"]) for z in gradient])
    x = x[np.isfinite(x)]
    nf = r["native_fit"]
    ci = nf["bootstrap_95pct"]["cumulative_ara_at_handover"]
    checks = {
        "result_identity": r["test"] == "T372",
        "native_coordinate_range": 0.0 < nf["cumulative_ara_at_handover"] < 2.0,
        "displacement_arithmetic": abs(nf["displacement_from_child_half"] - (nf["cumulative_ara_at_handover"] - 0.5)) < 1e-12,
        "coarse_value_distinct_from_native": abs(r["coarse_plot_audit"]["cumulative_ara_at_handover"] - nf["cumulative_ara_at_handover"]) > 0.02,
        "bootstrap_contains_native": ci[0] <= nf["cumulative_ara_at_handover"] <= ci[1],
        "bootstrap_contains_half": ci[0] <= 0.5 <= ci[1],
        "source_model_inside_interval": r["collaboration_source_crosscheck"]["inside_fit_bootstrap_interval"],
        "gradient_rows": len(gradient) == 193,
        "gradient_monotone": bool(np.all(np.diff(x) > 0)),
        "exact_half_share_range": 0.0 < r["identity_specific_gradient"]["share_that_places_handover_at_exact_half"] < 1.0,
        "energy_cut_rows": len(energy) == 6,
        "artifacts_present": all((HERE / p).exists() for p in [
            "T372_CHILD_HALF_HANDOVER_ASYMMETRY_THEORY_2026-08-13.md",
            "T372_CHILD_HALF_HANDOVER_GRADIENT_AUDIT_PROTOCOL_2026-08-13.md",
            "T372_CHILD_HALF_HANDOVER_GRADIENT_REPORT_2026-08-13.md",
            "T372_CHILD_HALF_HANDOVER_GRADIENT_FIGURE.png",
            "T372_CHILD_HALF_HANDOVER_GRADIENT_FIGURE.svg",
            "T372_CHILD_HALF_HANDOVER_NATIVE_SERIES.csv",
        ]),
    }
    out = {"test": "T372", "validation": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "T372_CHILD_HALF_HANDOVER_GRADIENT_VALIDATION.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
    if out["validation"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

