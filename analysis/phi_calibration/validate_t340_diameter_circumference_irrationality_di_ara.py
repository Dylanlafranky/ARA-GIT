"""Independent structural validation for T340 outputs."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
STEM = "T340_DIAMETER_CIRCUMFERENCE_IRRATIONALITY_DI_ARA"
RESULTS = HERE / f"{STEM}_RESULTS.json"
SUMMARY = HERE / f"{STEM}_SUMMARY.csv"
CELLS = HERE / f"{STEM}_CELLS.csv"
FIGURE = HERE / f"{STEM}_FIGURE.png"
REPORT = HERE / f"{STEM}_REPORT_2026-08-04.md"
PROTOCOL = HERE / f"{STEM}_PROTOCOL_v1_FROZEN.md"
OUT = HERE / f"{STEM}_VALIDATION.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    summary = pd.read_csv(SUMMARY)
    cells = pd.read_csv(CELLS)
    checks: dict[str, bool] = {}
    checks["protocol_hash"] = sha256(PROTOCOL) == result["protocol_sha256"]
    checks["declared_outputs_exist"] = all(path.exists() and path.stat().st_size > 0 for path in (SUMMARY, CELLS, FIGURE, REPORT))
    checks["summary_row_count"] = len(summary) == int(result["summary_rows"])
    checks["cell_row_count"] = len(cells) == int(result["cell_rows"])
    checks["all_four_directions"] = bool(
        (summary[["n_contracting", "n_expanding", "n_reverse", "n_forward"]] > 0).all().all()
    )
    radial_columns = [column for column in summary if column.startswith("radial_score_") and column not in {"radial_score_fitted_cal"}]
    angular_columns = [column for column in summary if column.startswith("angular_score_") and column not in {"angular_score_fitted_cal"}]
    radial_winners = summary[radial_columns].idxmin(axis=1).str.removeprefix("radial_score_")
    angular_winners = summary[angular_columns].idxmin(axis=1).str.removeprefix("angular_score_")
    checks["radial_winners_recomputed"] = bool((radial_winners == summary["radial_fixed_winner"]).all())
    checks["angular_winners_recomputed"] = bool((angular_winners == summary["angular_fixed_winner"]).all())
    recomputed_joint = (summary["radial_fixed_winner"] == "e") & (summary["angular_fixed_winner"] == "phi_inverse_squared")
    checks["joint_flags_recomputed"] = bool((recomputed_joint == summary["joint_fixed_pass"]).all())
    primary = summary[
        summary["domain"].isin(["recorded_qutrit", "recorded_bubbles", "recorded_river"])
        & summary["population"].isin(["three_planes_circle", "octave_relative_roots", "thalweg_rank1"])
        & (summary["split"] == "holdout")
    ]
    count = int(primary["joint_fixed_pass"].sum())
    checks["cross_domain_count"] = count == int(result["joint_holdout_domains"])
    checks["cross_domain_verdict"] = bool(result["cross_domain_supported"]) == (count >= 2)
    checks["finite_primary_metrics"] = bool(
        np.isfinite(
            primary[
                [
                    "radial_implied_alpha",
                    "angular_implied_tau",
                    "radial_score_e",
                    "angular_score_phi_inverse_squared",
                ]
            ].to_numpy(float)
        ).all()
    )
    validation = {
        "test": "T340 independent output validation",
        "all_pass": all(checks.values()),
        "checks": checks,
        "summary_sha256": sha256(SUMMARY),
        "cells_sha256": sha256(CELLS),
        "figure_sha256": sha256(FIGURE),
        "report_sha256": sha256(REPORT),
    }
    OUT.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, indent=2))
    if not validation["all_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
