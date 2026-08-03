#!/usr/bin/env python3
"""Independent reconstruction checks for frozen T339 outputs."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

import run_t339_llm_training_parent_plus_child as run


HERE = Path(__file__).resolve().parent
PROTOCOL_HASH = "591A88345849F9D7D4377A59BDA53E05B00549D6E91ADA12C77E06A15BE97F23"
CLAIM_HASH = "047D8F558AD1692E178E7C35FBAFC2318B421C8FE889EB915576B4A9FBCB8600"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    checks: list[dict] = []

    def check(name: str, passed: bool, detail: str = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    source = run.base.find_source()
    head = subprocess.check_output(
        [
            "git", "-c", f"safe.directory={source.as_posix()}",
            "-C", str(source), "rev-parse", "HEAD",
        ],
        text=True,
    ).strip()
    check("source_commit", head == run.SOURCE_COMMIT, head)
    check(
        "protocol_hash",
        digest(HERE / "T339_LLM_TRAINING_PARENT_PLUS_CHILD_PROTOCOL_v1_FROZEN.md")
        == PROTOCOL_HASH,
    )
    check(
        "claim_hash",
        digest(HERE / "T339_LLM_TRAINING_PARENT_PLUS_CHILD_CLAIM_PACKET_v1.md")
        == CLAIM_HASH,
    )

    raw_disk = pd.read_csv(HERE / "T339_RAW_REDUCED.csv.gz")
    raw_fresh, audit = run.base.load_raw(source)
    check("clean_file_count", audit["clean_files"] == 335, str(audit["clean_files"]))
    check(
        "single_schema_exclusion",
        len(audit["excluded_files"]) == 1
        and "pythia_1b_step0" in audit["excluded_files"][0]["path"],
    )
    key = ["model", "step", "layer", "top1", "median", "relation"]
    check(
        "raw_reduction_reproduces",
        np.allclose(
            raw_disk[key].select_dtypes("number"),
            raw_fresh[key].select_dtypes("number"),
            rtol=0,
            atol=1e-12,
        )
        and raw_disk[["model"]].equals(raw_fresh[["model"]]),
    )

    pred = pd.read_csv(HERE / "T339_PREDICTIONS.csv.gz")
    regenerated: list[dict] = []
    for model in run.MODEL_ORDER:
        regenerated.extend(run.model_predictions(raw_fresh[raw_fresh.model == model]))
    pred_fresh = pd.DataFrame(regenerated)
    numeric = [
        "delta_tau", "parent_flow_input", "child_flow_input", "actual_log", "pred_log",
        "abs_error", "sq_error", "actual_delta", "pred_delta", "actual_ara",
        "pred_ara", "ara_abs_error",
    ]
    check("prediction_rows", len(pred) == len(pred_fresh) == 82544, str(len(pred)))
    check(
        "predictions_reproduce",
        np.allclose(pred[numeric], pred_fresh[numeric], rtol=0, atol=1e-12),
    )

    # The direct formula check does not depend on the prediction generator's
    # named implementation: derive both flows from saved inputs.
    corrected = pred[pred.predictor == "ara_corrected"].reset_index(drop=True)
    equal = pred[pred.predictor == "equal_average_t338"].reset_index(drop=True)
    current_log = corrected.pred_log - corrected.pred_delta
    expected_corrected_delta = (
        corrected.parent_flow_input + 0.5 * corrected.child_flow_input
    ) * corrected.delta_tau
    expected_equal_delta = (
        0.5 * equal.parent_flow_input + 0.5 * equal.child_flow_input
    ) * equal.delta_tau
    check(
        "corrected_formula_exact",
        np.allclose(
            corrected.pred_delta, expected_corrected_delta, rtol=0, atol=1e-12
        )
        and np.allclose(equal.pred_delta, expected_equal_delta, rtol=0, atol=1e-12)
        and np.allclose(
            corrected.pred_log.to_numpy() - current_log.to_numpy(),
            corrected.pred_delta.to_numpy(), rtol=0, atol=1e-12,
        ),
    )
    residual_child = corrected.child_flow_input - corrected.parent_flow_input
    residual_rule_delta = (
        corrected.parent_flow_input + 0.5 * residual_child
    ) * corrected.delta_tau
    check(
        "post_result_residual_reconciliation_exact",
        np.allclose(
            residual_rule_delta, equal.pred_delta, rtol=0, atol=1e-12
        ),
        "P + 0.5*(C_total-P) = 0.5*P + 0.5*C_total",
    )

    _, summary_fresh, verdict_fresh = run.summarize(pred_fresh)
    summary_disk = pd.read_csv(HERE / "T339_SUMMARY_METRICS.csv")
    measures = ["mae", "rmse", "direction_accuracy", "ara_mae"]
    check(
        "summary_reproduces",
        np.allclose(
            summary_disk[measures], summary_fresh[measures],
            equal_nan=True, rtol=0, atol=1e-12,
        ),
    )
    verdict_disk = json.loads((HERE / "T339_VERDICT.json").read_text(encoding="utf-8"))
    check("verdict_reproduces", verdict_disk == verdict_fresh, verdict_fresh["verdict"])

    bootstrap_disk = json.loads(
        (HERE / "T339_MODEL_BOOTSTRAP.json").read_text(encoding="utf-8")
    )
    bootstrap_fresh = run.bootstrap_model_differences(
        pd.read_csv(HERE / "T339_PER_MODEL_METRICS.csv")
    )
    boot_keys = ["difference_favouring_corrected_ara", "ci95_low", "ci95_high"]
    boot_labels = ["split", "comparator", "metric", "models", "draws"]
    check(
        "model_bootstrap_reproduces",
        len(bootstrap_disk) == len(bootstrap_fresh)
        and all(
            all(a[k] == b[k] for k in boot_labels)
            and np.allclose(
                [a[k] for k in boot_keys], [b[k] for k in boot_keys],
                rtol=0, atol=1e-12,
            )
            for a, b in zip(bootstrap_disk, bootstrap_fresh)
        ),
    )

    # Alter the target and all later data. The target forecast must remain
    # unchanged because only its chronological prefix is admissible.
    model = "12b"
    original_model = raw_fresh[raw_fresh.model == model].copy()
    first_target = int(
        pred_fresh[
            (pred_fresh.model == model)
            & (pred_fresh.predictor == "ara_corrected")
        ].target_step.min()
    )
    original_forecast = pd.DataFrame(run.model_predictions(original_model))
    altered = original_model.copy()
    altered.loc[altered.step >= first_target, ["top1", "median"]] *= 100.0
    altered.loc[altered.step >= first_target, "relation"] = (
        altered.loc[altered.step >= first_target, "top1"]
        / altered.loc[altered.step >= first_target, "median"]
    )
    altered_forecast = pd.DataFrame(run.model_predictions(altered))

    def select_first(x: pd.DataFrame) -> pd.DataFrame:
        return x[
            (x.target_step == first_target)
            & (x.predictor == "ara_corrected")
        ].sort_values(["stream", "layer"])

    check(
        "causal_prefix_invariance",
        np.allclose(
            select_first(original_forecast).pred_log,
            select_first(altered_forecast).pred_log,
            rtol=0, atol=1e-12,
        ),
        str(first_target),
    )
    check(
        "model_splits",
        set(raw_fresh[raw_fresh.split == "holdout"].model.unique())
        == {"2.8b", "6.9b", "12b"},
    )
    check("positive_primary_values", bool((raw_fresh[["top1", "median"]] > 0).all().all()))
    check(
        "ara_range",
        bool(
            pred_fresh[["actual_ara", "pred_ara"]].ge(0).all().all()
            and pred_fresh[["actual_ara", "pred_ara"]].le(2).all().all()
        ),
    )

    result = {
        "passed": sum(c["passed"] for c in checks),
        "total": len(checks),
        "all_passed": all(c["passed"] for c in checks),
        "checks": checks,
    }
    (HERE / "T339_VALIDATION.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, indent=2))
    if not result["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
