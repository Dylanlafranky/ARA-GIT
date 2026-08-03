#!/usr/bin/env python3
"""Independent reconstruction checks for frozen T338 outputs."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

import run_t338_llm_training_di_ara as run


HERE = Path(__file__).resolve().parent


def digest(path: Path) -> str:
    h = hashlib.sha256(path.read_bytes()).hexdigest().upper()
    return h


def main() -> None:
    checks: list[dict] = []

    def check(name: str, passed: bool, detail: str = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    source = run.find_source()
    head = subprocess.check_output(
        ["git", "-c", f"safe.directory={source.as_posix()}", "-C", str(source), "rev-parse", "HEAD"],
        text=True,
    ).strip()
    check("source_commit", head == run.SOURCE_COMMIT, head)
    check("protocol_hash", digest(HERE / "T338_LLM_TRAINING_DI_ARA_PROTOCOL_v1_FROZEN.md") ==
          "8A908E8488169F3460F1FC7105BF6590D65BE341E4E832247FEE76F3730203C0")
    check("claim_hash", digest(HERE / "T338_LLM_TRAINING_DI_ARA_CLAIM_PACKET_v1.md") ==
          "AF7759430D3DF537855A8A332A3A23A8AB66CAEBE545F9A9F709282D75B8FC50")

    raw_disk = pd.read_csv(HERE / "T338_RAW_REDUCED.csv.gz")
    raw_fresh, audit = run.load_raw(source)
    check("clean_file_count", audit["clean_files"] == 335, str(audit["clean_files"]))
    check("single_schema_exclusion", len(audit["excluded_files"]) == 1 and
          "pythia_1b_step0" in audit["excluded_files"][0]["path"])
    key = ["model", "step", "layer", "top1", "median", "relation"]
    check("raw_reduction_reproduces", np.allclose(raw_disk[key].select_dtypes("number"),
                                                   raw_fresh[key].select_dtypes("number"),
                                                   rtol=0, atol=1e-12) and
          raw_disk[["model"]].equals(raw_fresh[["model"]]))

    pred = pd.read_csv(HERE / "T338_PREDICTIONS.csv.gz")
    regenerated = []
    for model in run.MODEL_ORDER:
        regenerated.extend(run.model_predictions(raw_fresh[raw_fresh.model == model]))
    pred_fresh = pd.DataFrame(regenerated)
    numeric = ["actual_log", "pred_log", "abs_error", "sq_error", "actual_delta",
               "pred_delta", "actual_ara", "pred_ara", "ara_abs_error"]
    check("prediction_rows", len(pred) == len(pred_fresh) == 70752, str(len(pred)))
    check("predictions_reproduce", np.allclose(pred[numeric], pred_fresh[numeric], rtol=0, atol=1e-12))

    _, summary_fresh, verdict_fresh = run.summarize(pred_fresh)
    summary_disk = pd.read_csv(HERE / "T338_SUMMARY_METRICS.csv")
    measures = ["mae", "rmse", "direction_accuracy", "ara_mae"]
    check("summary_reproduces", np.allclose(summary_disk[measures], summary_fresh[measures],
                                             equal_nan=True, rtol=0, atol=1e-12))
    verdict_disk = json.loads((HERE / "T338_VERDICT.json").read_text(encoding="utf-8"))
    check("verdict_reproduces", verdict_disk == verdict_fresh, verdict_fresh["verdict"])
    bootstrap_disk = json.loads((HERE / "T338_MODEL_BOOTSTRAP.json").read_text(encoding="utf-8"))
    bootstrap_fresh = run.bootstrap_model_differences(
        pd.read_csv(HERE / "T338_PER_MODEL_METRICS.csv"))
    boot_keys = ["difference_favouring_ara", "ci95_low", "ci95_high"]
    boot_labels = ["split", "comparator", "metric", "models", "draws"]
    check("model_bootstrap_reproduces",
          len(bootstrap_disk) == len(bootstrap_fresh) and
          all(all(a[k] == b[k] for k in boot_labels) and
              np.allclose([a[k] for k in boot_keys], [b[k] for k in boot_keys],
                          rtol=0, atol=1e-12)
              for a, b in zip(bootstrap_disk, bootstrap_fresh)))

    # Causal-prefix test: alter a target and all later values, then verify the
    # forecast for that target is unchanged because it may use only its prefix.
    model = "12b"
    original_model = raw_fresh[raw_fresh.model == model].copy()
    first_target = int(pred_fresh[(pred_fresh.model == model) & (pred_fresh.predictor == "ara")].target_step.min())
    original_forecast = pd.DataFrame(run.model_predictions(original_model))
    altered = original_model.copy()
    altered.loc[altered.step >= first_target, ["top1", "median"]] *= 100.0
    altered.loc[altered.step >= first_target, "relation"] = altered.loc[altered.step >= first_target, "top1"] / altered.loc[altered.step >= first_target, "median"]
    altered_forecast = pd.DataFrame(run.model_predictions(altered))
    selector = lambda x: x[(x.target_step == first_target) & (x.predictor == "ara")].sort_values(["stream", "layer"])
    check("causal_prefix_invariance", np.allclose(selector(original_forecast).pred_log,
                                                   selector(altered_forecast).pred_log,
                                                   rtol=0, atol=1e-12), str(first_target))

    check("model_splits", set(raw_fresh[raw_fresh.split == "holdout"].model.unique()) == {"2.8b", "6.9b", "12b"})
    check("positive_primary_values", bool((raw_fresh[["top1", "median"]] > 0).all().all()))
    check("ara_range", bool(pred_fresh[["actual_ara", "pred_ara"]].ge(0).all().all() and
                            pred_fresh[["actual_ara", "pred_ara"]].le(2).all().all()))

    result = {"passed": sum(c["passed"] for c in checks), "total": len(checks),
              "all_passed": all(c["passed"] for c in checks), "checks": checks}
    (HERE / "T338_VALIDATION.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not result["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
