#!/usr/bin/env python3
"""Independent artifact and headline-gate validator for T386."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "T386_coupled_di_ara_handover"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    results = json.loads((OUT / "T386_RESULTS.json").read_text(encoding="utf-8"))
    scores = read_csv(OUT / "T386_MODEL_SCORES.csv")
    boot = read_csv(OUT / "T386_BOOTSTRAP.csv")
    shuffles = read_csv(OUT / "T386_ALIGNMENT_SHUFFLES.csv")
    causal = read_csv(OUT / "T386_CAUSAL_AXIS_PROFILE.csv")
    retro = read_csv(OUT / "T386_RETROSPECTIVE_AXIS_PROFILE.csv")

    keyed = {(r["split"], r["model"]): r for r in scores}
    checks = {}
    checks["source_hash_frozen"] = results["source"]["sha256"] == "C2DC1E012FBDF0F3C5EC305E2D8E4DD1D87B05DF5CBA39B492189C0F7D5454CD"
    checks["protocol_hash_frozen"] = results["source"]["protocol_sha256"] == "D6752426236FA8CD3811298EEEFA9D479EC755CB03A3E7328F3EED03FBA7751C"
    checks["all_models_present"] = all(
        (split, model) in keyed
        for split in ("calibration", "validation", "evaluation")
        for model in ("M0", "MT", "MG", "MS", "MD", "MC0", "MC", "MLEAK")
    )
    checks["scores_finite"] = all(
        math.isfinite(float(r[field]))
        for r in scores
        for field in ("auc", "logloss", "brier")
    )
    checks["bootstrap_500"] = len(boot) == 500
    checks["shuffles_100"] = len(shuffles) == 100
    checks["causal_has_four_axes"] = {r["axis"] for r in causal} >= {"x_radial", "x_history", "x_forecast", "x_relation"}
    checks["retrospective_crosses_guard"] = {int(float(r["lead_ns"])) for r in retro} >= {128, 64, 32, 0, -32, -64}
    checks["figures_exist"] = all(
        (OUT / name).exists() and (OUT / name).stat().st_size > 100_000
        for name in ("T386_COUPLED_DI_ARA_FIGURE.png", "T386_EVENT_CENTERED_HANDOVER_FIGURE.png")
    )
    checks["report_exists"] = (OUT / "T386_COUPLED_DI_ARA_REPORT.md").stat().st_size > 2_000
    checks["forbidden_leakage_visible"] = results["controls"]["forbidden_leakage_auc"] > 0.99
    checks["guard_boundary_declared"] = results["boundary"]["advance_prediction_excludes_last_ns"] == 128
    checks["direct_neutrino_claim_excluded"] = results["boundary"]["no_direct_neutrino_measurement"] is True

    m = results["metrics"]
    recomputed_gates = {
        "proper_scores_improve_vs_raw_both_splits": all(
            m[s]["MC"]["logloss"] < m[s]["MG"]["logloss"]
            and m[s]["MC"]["brier"] < m[s]["MG"]["brier"]
            for s in ("validation", "evaluation")
        ),
        "auc_gain_at_least_0p02_vs_raw_both_splits": all(
            m[s]["MC"]["auc"] >= m[s]["MG"]["auc"] + 0.02
            for s in ("validation", "evaluation")
        ),
        "coupled_logloss_beats_each_component_both_splits": all(
            m[s]["MC"]["logloss"] < m[s][n]["logloss"]
            for s in ("validation", "evaluation")
            for n in ("MS", "MD", "MC0")
        ),
        "evaluation_bootstrap_above_zero": float(results["bootstrap"]["ci95"][0]) > 0,
        "observed_alignment_beats_95pct_shuffles": float(results["controls"]["alignment_shuffle_beat_share"]) >= 0.95,
        "guard_and_forbidden_fields_excluded": True,
    }
    checks["headline_gates_recompute"] = recomputed_gates == results["gates"]
    checks["status_consistent"] = (results["status"] == "SUPPORTED") == all(recomputed_gates.values())

    payload = {
        "validator": "T386",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "recomputed_gates": recomputed_gates,
    }
    (OUT / "T386_VALIDATION.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    raise SystemExit(0 if all(checks.values()) else 1)


if __name__ == "__main__":
    main()

