#!/usr/bin/env python3
"""Run the frozen T339 corrected parent-plus-child forecast.

T338's source parser and exact ARA coordinate are reused without alteration.
Only the prospectively corrected cross-rung composition is new here.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import run_t338_llm_training_di_ara as base


HERE = Path(__file__).resolve().parent
SOURCE_COMMIT = base.SOURCE_COMMIT
MODEL_ORDER = base.MODEL_ORDER
STREAMS = base.STREAMS
PREDICTORS = [
    "ara_corrected",
    "equal_average_t338",
    "persistence",
    "local_flow",
    "parent_flow",
    "local_trend",
    "broken_lineage",
]


def model_predictions(g: pd.DataFrame) -> list[dict]:
    model = str(g.model.iloc[0])
    split = str(g.split.iloc[0])
    steps = sorted(g.step.unique())
    layers = sorted(g.layer.unique())
    index = g.set_index(["step", "layer"])
    out: list[dict] = []
    for stream in STREAMS:
        values = np.array([
            [float(index.loc[(step, layer), stream]) for layer in layers]
            for step in steps
        ])
        taus = np.array([float(index.loc[(step, layers[0]), "tau"]) for step in steps])
        logs = np.log(values)
        dtaus = np.diff(taus)
        velocities = np.diff(logs, axis=0) / dtaus[:, None]
        parent_v = np.median(velocities, axis=1)
        for k in range(4, len(steps)):
            dt = taus[k] - taus[k - 1]
            recent_parent = float(np.median(parent_v[k - 4:k - 1]))
            for j, layer in enumerate(layers):
                recent_child = float(np.median(velocities[k - 4:k - 1, j]))
                broken_child = float(np.median(
                    velocities[k - 4:k - 1, (j + 1) % len(layers)]
                ))
                slope = float(np.polyfit(taus[k - 4:k], logs[k - 4:k, j], 1)[0])
                flows = {
                    # Intended cross-rung budget: full parent + half child.
                    "ara_corrected": recent_parent + 0.5 * recent_child,
                    # Frozen T338 mistranslation, retained as a direct control.
                    "equal_average_t338": 0.5 * recent_parent + 0.5 * recent_child,
                    "persistence": 0.0,
                    "local_flow": recent_child,
                    "parent_flow": recent_parent,
                    "local_trend": slope,
                    "broken_lineage": recent_parent + 0.5 * broken_child,
                }
                actual_log = float(logs[k, j])
                current_log = float(logs[k - 1, j])
                actual_delta = actual_log - current_log
                for predictor, flow in flows.items():
                    pred_log = current_log + flow * dt
                    pred_delta = pred_log - current_log
                    actual_ara = base.ara_coord_from_log_delta(actual_delta)
                    pred_ara = base.ara_coord_from_log_delta(pred_delta)
                    out.append({
                        "model": model,
                        "split": split,
                        "stream": stream,
                        "target_step": int(steps[k]),
                        "previous_step": int(steps[k - 1]),
                        "layer": int(layer),
                        "n_layers": len(layers),
                        "predictor": predictor,
                        "delta_tau": float(dt),
                        "parent_flow_input": recent_parent,
                        "child_flow_input": recent_child,
                        "actual_log": actual_log,
                        "pred_log": pred_log,
                        "abs_error": abs(pred_log - actual_log),
                        "sq_error": (pred_log - actual_log) ** 2,
                        "actual_delta": actual_delta,
                        "pred_delta": pred_delta,
                        "direction_correct": (
                            float(np.sign(pred_delta) == np.sign(actual_delta))
                            if abs(actual_delta) > 1e-12 else np.nan
                        ),
                        "actual_ara": actual_ara,
                        "pred_ara": pred_ara,
                        "ara_abs_error": abs(pred_ara - actual_ara),
                    })
    return out


def summarize(pred: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    per_model = (
        pred.groupby(["split", "model", "stream", "predictor"], as_index=False)
        .agg(
            mae=("abs_error", "mean"),
            rmse=("sq_error", lambda x: float(np.sqrt(np.mean(x)))),
            direction_accuracy=("direction_correct", "mean"),
            ara_mae=("ara_abs_error", "mean"),
            n=("abs_error", "size"),
        )
    )
    split_stream = (
        per_model.groupby(["split", "stream", "predictor"], as_index=False)
        .agg(
            mae=("mae", "mean"),
            rmse=("rmse", "mean"),
            direction_accuracy=("direction_accuracy", "mean"),
            ara_mae=("ara_mae", "mean"),
            models=("model", "nunique"),
        )
    )
    joint = (
        split_stream.groupby(["split", "predictor"], as_index=False)
        .agg(
            mae=("mae", "mean"),
            rmse=("rmse", "mean"),
            direction_accuracy=("direction_accuracy", "mean"),
            ara_mae=("ara_mae", "mean"),
            streams=("stream", "nunique"),
        )
    )
    lookup = joint.set_index(["split", "predictor"])
    ss = split_stream.set_index(["split", "stream", "predictor"])
    corrected = "ara_corrected"
    gates = {
        "G0_integrity": True,
        "G1_eval_vs_persistence": bool(
            lookup.loc[("evaluation", corrected), "mae"]
            < lookup.loc[("evaluation", "persistence"), "mae"]
        ),
        "G1_holdout_vs_persistence": bool(
            lookup.loc[("holdout", corrected), "mae"]
            < lookup.loc[("holdout", "persistence"), "mae"]
        ),
        "G2_eval_vs_local_trend": bool(
            lookup.loc[("evaluation", corrected), "mae"]
            < lookup.loc[("evaluation", "local_trend"), "mae"]
        ),
        "G2_holdout_vs_local_trend": bool(
            lookup.loc[("holdout", corrected), "mae"]
            < lookup.loc[("holdout", "local_trend"), "mae"]
        ),
        "G3_eval_vs_broken": bool(
            lookup.loc[("evaluation", corrected), "mae"]
            < lookup.loc[("evaluation", "broken_lineage"), "mae"]
        ),
        "G3_holdout_vs_broken": bool(
            lookup.loc[("holdout", corrected), "mae"]
            < lookup.loc[("holdout", "broken_lineage"), "mae"]
        ),
        "G4_holdout_top1_vs_persistence": bool(
            ss.loc[("holdout", "top1", corrected), "mae"]
            < ss.loc[("holdout", "top1", "persistence"), "mae"]
        ),
        "G4_holdout_median_vs_persistence": bool(
            ss.loc[("holdout", "median", corrected), "mae"]
            < ss.loc[("holdout", "median", "persistence"), "mae"]
        ),
        "G5_holdout_direction_vs_local": bool(
            lookup.loc[("holdout", corrected), "direction_accuracy"]
            > lookup.loc[("holdout", "local_flow"), "direction_accuracy"]
        ),
        "G6_eval_vs_equal_average": bool(
            lookup.loc[("evaluation", corrected), "mae"]
            < lookup.loc[("evaluation", "equal_average_t338"), "mae"]
        ),
        "G6_holdout_vs_equal_average": bool(
            lookup.loc[("holdout", corrected), "mae"]
            < lookup.loc[("holdout", "equal_average_t338"), "mae"]
        ),
    }
    g1 = gates["G1_eval_vs_persistence"] and gates["G1_holdout_vs_persistence"]
    g2 = gates["G2_eval_vs_local_trend"] and gates["G2_holdout_vs_local_trend"]
    g3 = gates["G3_eval_vs_broken"] and gates["G3_holdout_vs_broken"]
    g4 = (
        gates["G4_holdout_top1_vs_persistence"]
        and gates["G4_holdout_median_vs_persistence"]
    )
    g5 = gates["G5_holdout_direction_vs_local"]
    g6 = gates["G6_eval_vs_equal_average"] and gates["G6_holdout_vs_equal_average"]
    if gates["G0_integrity"] and g1 and g2 and g3 and g4 and g5 and g6:
        verdict = "SUPPORTED"
    elif gates["G0_integrity"] and g1 and g3 and g6:
        verdict = "MIXED/PARTIAL"
    else:
        verdict = "NOT SUPPORTED IN THIS FORM"
    combined = pd.concat(
        [
            split_stream.assign(level="stream"),
            joint.assign(stream="joint", level="joint"),
        ],
        ignore_index=True,
    )
    return per_model, combined, {"gates": gates, "verdict": verdict}


def bootstrap_model_differences(per_model: pd.DataFrame, draws: int = 10_000) -> list[dict]:
    """Equal-model bootstrap; positive paired differences favour corrected ARA."""
    rng = np.random.default_rng(339)
    joint = (
        per_model.groupby(["split", "model", "predictor"], as_index=False)
        .agg(mae=("mae", "mean"), direction_accuracy=("direction_accuracy", "mean"))
    )
    results: list[dict] = []
    comparisons = [
        ("equal_average_t338", "mae"),
        ("persistence", "mae"),
        ("local_trend", "mae"),
        ("broken_lineage", "mae"),
        ("local_flow", "direction_accuracy"),
    ]
    for split in ["evaluation", "holdout"]:
        q = joint[joint.split == split]
        models = sorted(q.model.unique())
        for comparator, metric in comparisons:
            ara = q[q.predictor == "ara_corrected"].set_index("model")[metric].loc[models].to_numpy()
            other = q[q.predictor == comparator].set_index("model")[metric].loc[models].to_numpy()
            diff = (other - ara) if metric == "mae" else (ara - other)
            boot = np.mean(
                diff[rng.integers(0, len(diff), size=(draws, len(diff)))], axis=1
            )
            results.append({
                "split": split,
                "comparator": comparator,
                "metric": metric,
                "difference_favouring_corrected_ara": float(np.mean(diff)),
                "ci95_low": float(np.quantile(boot, 0.025)),
                "ci95_high": float(np.quantile(boot, 0.975)),
                "models": len(models),
                "draws": draws,
            })
    return results


def main() -> None:
    source = base.find_source()
    raw, audit = base.load_raw(source)
    all_predictions: list[dict] = []
    for model in MODEL_ORDER:
        all_predictions.extend(model_predictions(raw[raw.model == model]))
    pred = pd.DataFrame(all_predictions)
    per_model, summary, verdict = summarize(pred)
    bootstrap = bootstrap_model_differences(per_model)
    protocol = HERE / "T339_LLM_TRAINING_PARENT_PLUS_CHILD_PROTOCOL_v1_FROZEN.md"
    claim = HERE / "T339_LLM_TRAINING_PARENT_PLUS_CHILD_CLAIM_PACKET_v1.md"
    audit.update({
        "protocol_sha256": base.sha256(protocol),
        "claim_sha256": base.sha256(claim),
        "prediction_rows": int(len(pred)),
        "source_commit_expected": SOURCE_COMMIT,
        "corrected_formula": "1.0*v_parent + 0.5*v_child",
        "wrong_translation_control": "0.5*v_parent + 0.5*v_child",
    })
    raw.to_csv(HERE / "T339_RAW_REDUCED.csv.gz", index=False, compression="gzip")
    pred.to_csv(HERE / "T339_PREDICTIONS.csv.gz", index=False, compression="gzip")
    per_model.to_csv(HERE / "T339_PER_MODEL_METRICS.csv", index=False)
    summary.to_csv(HERE / "T339_SUMMARY_METRICS.csv", index=False)
    (HERE / "T339_AUDIT.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    (HERE / "T339_VERDICT.json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")
    (HERE / "T339_MODEL_BOOTSTRAP.json").write_text(
        json.dumps(bootstrap, indent=2), encoding="utf-8"
    )
    focus = [
        "ara_corrected",
        "equal_average_t338",
        "persistence",
        "local_trend",
        "broken_lineage",
    ]
    print(json.dumps({"audit": audit, **verdict}, indent=2))
    print(
        summary[(summary.level == "joint") & (summary.predictor.isin(focus))]
        .sort_values(["split", "mae"])
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
