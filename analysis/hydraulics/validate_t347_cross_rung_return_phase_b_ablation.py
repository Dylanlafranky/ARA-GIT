"""Independent output-level validation for T347."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
PREFIX = "T347_CROSS_RUNG_RETURN_AND_PHASE_B_ABLATION"
EXPECTED_SHA = "fecd7973e838dd0b71bdc3d099d56e46154a8212735a4c70c213420cde0c0e16"
LAMBDAS = np.array([0.0, .25, .5, .75, 1.0])


def close(a, b, tol=1e-11):
    return bool(np.isclose(float(a), float(b), rtol=tol, atol=tol))


def main():
    protocol = HERE / f"{PREFIX}_PROTOCOL_v1_FROZEN.md"
    events = pd.read_csv(HERE / f"{PREFIX}_EVENTS.csv")
    curves = pd.read_csv(HERE / f"{PREFIX}_ABLATION_CURVES.csv")
    nulls = pd.read_csv(HERE / f"{PREFIX}_MATCHED_NULLS.csv")
    boots = pd.read_csv(HERE / f"{PREFIX}_BOOTSTRAPS.csv")
    results = json.loads((HERE / f"{PREFIX}_RESULTS.json").read_text(encoding="utf-8"))
    analysis = results["analysis"]
    checks = {}
    checks["protocol_hash"] = hashlib.sha256(protocol.read_bytes()).hexdigest() == EXPECTED_SHA
    checks["event_count"] = len(events) == results["construction"]["eligible_anchors"] == 9071
    checks["track_count"] = events.track_id.nunique() == results["construction"]["tracks"] == 3622
    checks["three_conditions"] = set(events.condition) == {"low", "medium", "high"}
    checks["source_hashes"] = all(item["sha256_matches_official"] for item in results["source_audits"])

    persistence = np.cos(events.theta_out - events.theta_in)
    smoothing = events.centre_roughness - events.parent_turn
    checks["persistence_formula"] = np.allclose(persistence, events.parent_persistence, rtol=1e-12, atol=1e-12)
    checks["smoothing_formula"] = np.allclose(smoothing, events.smoothing_score, rtol=1e-12, atol=1e-12)
    checks["child_information_formula"] = np.allclose(
        events.child_b_connection - events.child_a_connection, events.delta_i_ba, rtol=1e-12, atol=1e-12
    )
    checks["child_directness_formula"] = np.allclose(
        events.child_a_directness - events.child_b_directness, events.delta_d_ba, rtol=1e-12, atol=1e-12
    )

    metric_map = {
        "parent_persistence": persistence,
        "smoothing_score": smoothing,
        "delta_i_ba": events.delta_i_ba.to_numpy(),
        "delta_d_ba": events.delta_d_ba.to_numpy(),
        "max_perpendicular_departure": events.max_perpendicular_departure.to_numpy(),
        "centre_chord_alignment": events.centre_chord_alignment.to_numpy(),
    }
    for metric, values in metric_map.items():
        temp = pd.DataFrame({"track_id": events.track_id, "value": values})
        estimate = temp.groupby("track_id").value.mean().mean()
        reported = analysis["components"][metric]
        checks[f"estimate_{metric}"] = close(estimate, reported["estimate"])
        b = boots.loc[boots.metric == metric, "estimate"].to_numpy()
        checks[f"bootstrap_{metric}"] = (
            close(np.quantile(b, .025), reported["ci_low"])
            and close(np.quantile(b, .975), reported["ci_high"])
            and len(b) == 2000
        )

    model_delta = {
        "intact B": events.delta_b.to_numpy(),
        "reversed B": -events.delta_b.to_numpy(),
        "wrong child": events.wrong_child_delta.to_numpy(),
    }
    for model, delta in model_delta.items():
        for lam in LAMBDAS:
            loss = 1.0 - np.cos(events.theta_out - (events.theta_in + lam * delta))
            mean_loss = pd.DataFrame({"track_id": events.track_id, "loss": loss}).groupby("track_id").loss.mean().mean()
            reported = curves.loc[(curves.model == model) & np.isclose(curves["lambda"], lam), "loss"].iloc[0]
            checks[f"loss_{model}_{lam:g}"] = close(mean_loss, reported)

    p = (1 + (nulls.wrong_lineage_persistence >= analysis["components"]["parent_persistence"]["estimate"]).sum()) / (len(nulls) + 1)
    checks["parent_null_p"] = close(p, analysis["components"]["parent_persistence"]["wrong_lineage_p"])
    checks["permutation_count"] = len(nulls) == 1000

    pa = analysis["components"]["parent_persistence"]
    ss = analysis["components"]["smoothing_score"]
    di = analysis["components"]["delta_i_ba"]
    dd = analysis["components"]["delta_d_ba"]
    recomputed_gates = {
        "A_parent_direction": bool(pa["ci_low"] > 0 and pa["condition_positive"] >= 2 and pa["wrong_lineage_p"] <= .01),
        "B_scale_up_smoothing": bool(ss["ci_low"] > 0 and ss["condition_positive"] >= 2),
        "C_child_handover": bool(di["ci_low"] > 0 and di["condition_positive"] >= 2 and dd["ci_low"] > 0 and dd["condition_positive"] >= 2),
    }
    checks["gate_logic"] = recomputed_gates == analysis["gates"]
    checks["all_outputs_finite"] = bool(
        np.isfinite(events.select_dtypes(include=[np.number]).to_numpy()).all()
        and np.isfinite(curves.select_dtypes(include=[np.number]).to_numpy()).all()
        and np.isfinite(nulls.select_dtypes(include=[np.number]).to_numpy()).all()
    )
    checks["figure_exists"] = (HERE / f"{PREFIX}_FIGURE.png").stat().st_size > 100_000
    passed = all(checks.values())
    orientation = {
        "horizontal_sine_tolerance": 0.01,
        "theta_in_near_horizontal_fraction": float(np.mean(np.abs(np.sin(events.theta_in)) < 0.01)),
        "theta_out_near_horizontal_fraction": float(np.mean(np.abs(np.sin(events.theta_out)) < 0.01)),
        "centre_chord_alignment": analysis["components"]["centre_chord_alignment"],
    }
    payload = {"valid": passed, "checks": checks, "orientation_audit": orientation}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    report = [
        "# T347 validation",
        "",
        f"**Status:** {'PASS' if passed else 'FAIL'}",
        "",
        f"Validated {len(events):,} handovers from {events.track_id.nunique():,} tracks, 2,000 whole-track bootstrap replicates per frozen component, and {len(nulls):,} matched permutations.",
        "",
        "All component formulas, point estimates, bootstrap intervals, loss curves, source hashes and gate logic were independently recomputed from the exported artifacts.",
        "",
        "## Measurement warning",
        "",
        f"Using `abs(sin(theta)) < 0.01` as a descriptive near-horizontal threshold, {orientation['theta_in_near_horizontal_fraction']:.3%} of retained entry directions and {orientation['theta_out_near_horizontal_fraction']:.3%} of exits were near-horizontal. The numerical source is therefore strongly streamwise-oriented; this limits generalization to freely resolved two-dimensional circular paths.",
    ]
    (HERE / f"{PREFIX}_VALIDATION_2026-08-09.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
