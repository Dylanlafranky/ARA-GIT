from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHARED_PYDEPS = HERE.parents[1] / "pulsar" / "T442_ng15_optimal_geometry" / ".pydeps"
if SHARED_PYDEPS.exists():
    sys.path.insert(0, str(SHARED_PYDEPS))

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


RESULTS = HERE / "results"
DATA = HERE / "data"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    frame = pd.read_csv(RESULTS / "T444_SYSTEM_RESULTS.csv")
    summary = json.loads((RESULTS / "T444_SUMMARY.json").read_text(encoding="utf-8"))
    artifact = json.loads((RESULTS / "artifact.json").read_text(encoding="utf-8"))
    checks: dict[str, dict] = {}

    def check(name: str, passed: bool, detail) -> None:
        checks[name] = {"passed": bool(passed), "detail": detail}

    expected_hashes = summary["quality"]["source_hashes"]
    actual_hashes = {name: sha256(DATA / name) for name in expected_hashes}
    check("source_hashes", actual_hashes == expected_hashes, actual_hashes)
    check("eligible_row_count", len(frame) == summary["quality"]["eligible_systems"], int(len(frame)))
    check("unique_systems", frame["name"].nunique() == len(frame), int(frame["name"].nunique()))
    check("opening_threshold", bool((frame["opening_angle_deg"] >= 150.0).all()), float(frame["opening_angle_deg"].min()))
    check("positive_native_values", bool((frame[["observed_days", "r_A_arcsec", "r_B_arcsec", "time_delay_distance_mpc"]] > 0).all().all()), "observed delay, radii and Ddt are positive")

    pm_sum_error = float(np.max(np.abs(frame["pm_total_days"] - frame["pm_geo_days"] - frame["pm_potential_days"])))
    sis_sum_error = float(np.max(np.abs(frame["sis_total_days"] - frame["sis_geo_days"] - frame["sis_potential_days"])))
    check("point_mass_component_sum", pm_sum_error < 1e-10, pm_sum_error)
    check("sis_component_sum", sis_sum_error < 1e-10, sis_sum_error)
    check("sis_geometric_cancellation", float(np.max(np.abs(frame["sis_geo_days"]))) == 0.0, float(np.max(np.abs(frame["sis_geo_days"]))))

    ara_errors = {}
    for model in ["pm", "sis"]:
        error = float(np.max(np.abs(frame[f"{model}_path_ara"] + frame[f"{model}_connection_ara"] - 2.0)))
        ara_errors[model] = error
    check("ara_contribution_sum", max(ara_errors.values()) < 1e-12, ara_errors)

    residual_errors = {}
    factor_errors = {}
    for model in ["pm", "sis"]:
        residual_errors[model] = float(np.max(np.abs(frame[f"{model}_residual_days"] - (frame["observed_days"] - frame[f"{model}_total_days"]))))
        recomputed_factor = 10 ** np.abs(np.log10(frame[f"{model}_total_days"] / frame["observed_days"]))
        factor_errors[model] = float(np.max(np.abs(frame[f"{model}_factor_error"] - recomputed_factor)))
    check("residual_formula", max(residual_errors.values()) < 1e-10, residual_errors)
    check("factor_error_formula", max(factor_errors.values()) < 1e-10, factor_errors)

    metric_errors = {}
    for model in ["pm", "sis"]:
        rho = float(spearmanr(frame["observed_days"], frame[f"{model}_total_days"]).statistic)
        factor = float(10 ** np.median(np.abs(np.log10(frame[f"{model}_total_days"] / frame["observed_days"]))))
        metric_errors[f"{model}_rho"] = abs(rho - summary["models"][model]["spearman_rho"])
        metric_errors[f"{model}_factor"] = abs(factor - summary["models"][model]["median_factor_error"])
    check("summary_metrics", max(metric_errors.values()) < 1e-12, metric_errors)

    artifact_rows = artifact["snapshot"]["datasets"]["system_detail"]
    check("artifact_system_rows", len(artifact_rows) == len(frame), len(artifact_rows))
    check("artifact_status", artifact["snapshot"]["status"] == "ready", artifact["snapshot"]["status"])
    check("required_visuals", all((RESULTS / name).exists() and (RESULTS / name).stat().st_size > 10_000 for name in ["T444_GEOMETRY_FIRST.png", "T444_SKY_GEOMETRIES.png"]), "both PNGs exist and exceed 10 kB")

    validation = {
        "test": "T444",
        "all_passed": all(item["passed"] for item in checks.values()),
        "checks": checks,
    }
    (RESULTS / "T444_VALIDATION.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))
    if not validation["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
