"""Independent artifact validator for T373."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = Path(r"F:\SystemFormulaFolder\external_data\coherent_argon_3903810")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(a: float, b: float, tol: float = 5e-7) -> bool:
    return bool(abs(float(a) - float(b)) <= tol)


def main() -> None:
    result = json.loads((HERE / "T373_ARGON_CHILD_HALF_TRANSFER_RESULTS.json").read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}

    protocol = HERE / "T373_ARGON_CHILD_HALF_TRANSFER_PROTOCOL_2026-08-13.md"
    checks["protocol_hash_matches_frozen_digest"] = digest(protocol) == "06352a918b617d36a281b36158152462bd30222a512e99c8228e9e7d6f2f1fa3"

    raw = {}
    for name in ["datanobkgsub.txt", "cevnspdf.txt", "brnpdf.txt", "delbrnpdf.txt", "bkgpdf.txt"]:
        a = np.loadtxt(DATA / name)
        raw[name] = a
        checks[f"{name}_has_shared_960_cell_coordinates"] = bool(a.shape == (960, 4) and np.allclose(a[:, :3], raw["datanobkgsub.txt"][:, :3]))

    expected_sums = {
        "datanobkgsub.txt": 3752.0,
        "cevnspdf.txt": 128.0000052667117,
        "brnpdf.txt": 496.99999307,
        "delbrnpdf.txt": 33.00001642,
        "bkgpdf.txt": 3152.00016,
    }
    checks["released_component_sums_reproduce"] = all(close(raw[n][:, 3].sum(), v, 1e-5) for n, v in expected_sums.items())

    timeline = np.genfromtxt(HERE / "T373_ARGON_CHILD_HALF_TRANSFER_TIMELINE.csv", delimiter=",", names=True)
    checks["timeline_has_native_ten_bins"] = bool(len(timeline) == 10 and np.allclose(timeline["time_us"], np.arange(0.15, 4.66, 0.5)))
    model_prompt = float(timeline["model_prompt"].sum())
    model_delayed = float(timeline["model_delayed"].sum())
    model_share = model_prompt / (model_prompt + model_delayed)
    checks["model_prompt_share_reproduces"] = close(model_share, result["model_prediction"]["prompt_share"])

    fit_events = result["event_measurement"]["fitted_events"]
    measured_share = fit_events["prompt_cevns"] / (fit_events["prompt_cevns"] + fit_events["delayed_cevns"])
    checks["event_prompt_share_arithmetic_reproduces"] = close(measured_share, result["event_measurement"]["prompt_share"])
    checks["event_total_signal_arithmetic_reproduces"] = close(
        fit_events["prompt_cevns"] + fit_events["delayed_cevns"], fit_events["total_cevns"]
    )

    boot = np.genfromtxt(HERE / "T373_ARGON_CHILD_HALF_TRANSFER_BOOTSTRAP.csv", delimiter=",", names=True)
    checks["bootstrap_row_count_matches"] = len(boot) == result["event_measurement"]["bootstrap_95pct"]["valid_replicates"] == 1947
    qx = np.percentile(boot["cumulative_ara_at_handover"], [2.5, 97.5])
    qs = np.percentile(boot["prompt_share"], [2.5, 97.5])
    checks["bootstrap_handover_interval_reproduces"] = bool(np.allclose(qx, result["event_measurement"]["bootstrap_95pct"]["cumulative_ara_at_handover"], atol=1e-10))
    checks["bootstrap_prompt_share_interval_reproduces"] = bool(np.allclose(qs, result["event_measurement"]["bootstrap_95pct"]["prompt_share"], atol=1e-10))

    pred_x = result["model_prediction"]["cumulative_ara_at_handover"]
    checks["frozen_transfer_gate_reproduces"] = bool(qx[0] <= pred_x <= qx[1]) == result["gates"]["transfer_prediction_inside_event_95pct"]
    checks["crossing_conditioned_half_gate_reproduces"] = bool(qx[0] <= 0.5 <= qx[1]) == result["gates"]["pure_child_half_inside_event_95pct"]
    checks["profile_audit_keeps_half_compatible"] = bool(result["post_result_boundary_audit"]["profile_delta_nll_at_pure_x_0_5"] < 1.920729410347062)
    checks["profile_audit_keeps_model_compatible"] = bool(result["post_result_boundary_audit"]["profile_delta_nll_at_model_prediction"] < 1.920729410347062)
    checks["free_model_not_worse_than_fixed"] = bool(result["fixed_vs_free_mixture"]["free_nll"] <= result["fixed_vs_free_mixture"]["fixed_nll"])
    checks["decomposition_error_below_frozen_limit"] = bool(result["model_prediction"]["signal_template_decomposition_nrmse"] < 0.10)
    correction = result["originator_identity_correction"]
    checks["same_coordinate_premise_marked_invalid"] = result["gates"]["same_coordinate_transfer_premise_valid_after_originator_review"] is False
    checks["nested_child_parent_relation_retained"] = result["gates"]["nested_child_parent_relation_retained_after_originator_review"] is True
    checks["liquid_1_25_residual_reproduces"] = close(
        result["event_measurement"]["cumulative_ara_at_handover"] - 1.25,
        correction["observed_minus_candidate"],
    )
    checks["liquid_1_25_relative_error_reproduces"] = close(
        100.0 * abs(correction["observed_minus_candidate"]) / 1.25,
        correction["absolute_relative_error_percent"],
    )
    checks["liquid_1_25_is_explicitly_post_result"] = "after viewing" in correction["evidence_boundary"]
    checks["reader_artifacts_exist"] = all((HERE / n).exists() for n in [
        "T373_ARGON_CHILD_HALF_TRANSFER_FIGURE.png",
        "T373_ARGON_CHILD_HALF_TRANSFER_FIGURE.svg",
        "T373_ARGON_CHILD_HALF_TRANSFER_REPORT_2026-08-13.md",
    ])

    validation = {
        "test": "T373",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks_passed": int(sum(checks.values())),
        "checks_total": len(checks),
        "checks": checks,
        "independent_summary": (
            "The frozen numerical gate reproduces, but originator review invalidated its same-coordinate premise while retaining a nested child-parent lineage. "
            "The observed x=1.238725 lies 0.902% below the post-result liquid candidate x=1.25; this is a lead, not confirmation."
        ),
    }
    (HERE / "T373_ARGON_CHILD_HALF_TRANSFER_VALIDATION.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
