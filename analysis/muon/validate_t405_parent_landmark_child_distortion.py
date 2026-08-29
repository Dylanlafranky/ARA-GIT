from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

EXTRA = Path(r"F:\SystemFormulaFolder\.codex_python_packages")
if EXTRA.exists() and str(EXTRA) not in sys.path:
    sys.path.insert(0, str(EXTRA))

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "T405_parent_landmark_child_distortion"
PROTOCOL = ROOT / "T405_PARENT_LANDMARK_CHILD_DISTORTION_PROTOCOL_2026-08-18.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


results = json.loads((OUT / "T405_RESULTS.json").read_text(encoding="utf-8"))
splits = pd.read_csv(OUT / "T405_SPLIT_PARTICIPATION.csv")
loo = pd.read_csv(OUT / "T405_LEAVE_ONE_OUT.csv")
diagnostics = pd.read_csv(OUT / "T405_DIAGNOSTICS.csv")

x = splits["prompt_participation"].to_numpy(float)
y = splits["child_displacement_from_0p5"].to_numpy(float)
left = splits["left_time_us"].to_numpy(float)
rho = float(spearmanr(x, y).statistic)
rho_x_left = float(spearmanr(x, left).statistic)
rho_left_y = float(spearmanr(left, y).statistic)

checks = {
    "protocol_hash_matches": results["protocol_sha256"] == sha256(PROTOCOL),
    "twenty_valid_splits": len(splits) == 20,
    "prompt_fraction_recomputes": np.allclose(
        splits["prompt_participation"],
        splits["n_prompt"] / (splits["n_prompt"] + splits["n_delayed"]),
        atol=1e-12,
    ),
    "displacement_recomputes": np.allclose(
        splits["child_displacement_from_0p5"],
        splits["population_local_mode"] - 0.5,
        atol=1e-12,
    ),
    "primary_rho_recomputes": np.isclose(rho, results["primary"]["spearman_rho"], atol=1e-12),
    "all_loo_rho_one": np.allclose(loo["rho"], 1.0, atol=1e-12),
    "boundary_relations_are_rank_identical": np.isclose(rho_x_left, 1.0, atol=1e-12)
    and np.isclose(rho_left_y, 1.0, atol=1e-12),
    "partial_relation_marked_non_identifiable": results["boundary_mediation_diagnostic"]["partial_rank_rho_prompt_vs_displacement_given_left_boundary"] is None,
    "structural_boundary_is_explicit": any(
        "structurally encoded" in item.lower() for item in results["boundaries"]
    ),
    "all_registered_gates_pass": all(results["gates"].values()),
    "diagnostics_saved": len(diagnostics) == 5,
}
checks = {key: bool(value) for key, value in checks.items()}

validation = {
    "test": "T405 independent saved-output validation",
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks": checks,
    "recomputed": {
        "rho_prompt_vs_displacement": rho,
        "rho_prompt_vs_left_boundary": rho_x_left,
        "rho_left_boundary_vs_displacement": rho_left_y,
    },
    "interpretation": "The parent-to-child displacement is perfectly monotonic in participation inside T400, but the same rank is carried by the equality boundary that constructs the local coordinate. This validates the distortion-aware ARA instrument; it is not independent physical confirmation.",
}

(OUT / "T405_VALIDATION.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
print(json.dumps(validation, indent=2))
raise SystemExit(0 if validation["status"] == "PASS" else 1)
