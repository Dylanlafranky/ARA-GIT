#!/usr/bin/env python3
"""Run the frozen T338 Pythia training Di-ARA forecast.

Only raw checkpoint statistics are read.  Publisher-fitted curves and
capability labels are deliberately excluded from the primary calculation.
"""

from __future__ import annotations

import ast
import hashlib
import json
import math
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SOURCE_COMMIT = "c4c539ac4f8c8fc9694603895d00c1f1af940a20"
MODEL_ORDER = ["14m", "70m", "160m", "410m", "1b", "1.4b", "2.8b", "6.9b", "12b"]
MODEL_SPLIT = {
    "14m": "calibration", "70m": "calibration", "160m": "calibration",
    "410m": "evaluation", "1b": "evaluation", "1.4b": "evaluation",
    "2.8b": "holdout", "6.9b": "holdout", "12b": "holdout",
}
PARAMS_M = {"14m": 14, "70m": 70, "160m": 160, "410m": 410,
            "1b": 1000, "1.4b": 1400, "2.8b": 2800, "6.9b": 6900,
            "12b": 12000}
PREDICTORS = ["ara", "persistence", "local_flow", "parent_flow", "local_trend", "broken_lineage"]
STREAMS = ["top1", "median"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest().upper()


def find_source() -> Path:
    env = os.environ.get("ARA_PYTHIA_ACTIVATIONS")
    candidates = [
        Path(env) if env else None,
        REPO.parents[1] / "external_data" / "pythia-massive-activations",
        HERE / "data" / "pythia-massive-activations",
    ]
    for candidate in candidates:
        if candidate and (candidate / "README.md").exists():
            return candidate
    raise FileNotFoundError(
        "Set ARA_PYTHIA_ACTIVATIONS to a clone of "
        "https://huggingface.co/datasets/Aimpoint-Digital/pythia-massive-activations"
    )


def parse_stats(path: Path) -> np.ndarray:
    obj = ast.literal_eval(path.read_text(encoding="utf-8"))
    arr = np.asarray(obj, dtype=float)
    if arr.ndim != 3 or arr.shape[0] != 10 or arr.shape[1] != 4:
        raise ValueError(f"unexpected shape {arr.shape}")
    if not np.isfinite(arr).all() or (arr[:, [0, 3], :] <= 0).any():
        raise ValueError("non-positive or non-finite primary values")
    return arr


def load_raw(source: Path) -> tuple[pd.DataFrame, dict]:
    rows: list[dict] = []
    audit = {"source": str(source), "clean_files": 0, "excluded_files": []}
    pat = re.compile(r"_step(\d+)$")
    for model in MODEL_ORDER:
        stats_dir = source / f"pythia_{model}" / "stats"
        for path in sorted(stats_dir.glob("exp2_*_step*")):
            match = pat.search(path.name)
            if not match:
                audit["excluded_files"].append({"path": str(path), "reason": "no_step"})
                continue
            try:
                arr = parse_stats(path)
            except Exception as exc:  # schema exclusion is part of the frozen protocol
                audit["excluded_files"].append({"path": str(path), "reason": type(exc).__name__})
                continue
            step = int(match.group(1))
            top1 = np.median(arr[:, 0, :], axis=0)
            background = np.median(arr[:, 3, :], axis=0)
            for layer, (large, bg) in enumerate(zip(top1, background)):
                rows.append({
                    "model": model, "params_m": PARAMS_M[model], "split": MODEL_SPLIT[model],
                    "step": step, "tau": math.log2(step + 1), "layer": layer,
                    "n_layers": arr.shape[2], "top1": float(large), "median": float(bg),
                    "relation": float(large / bg),
                })
            audit["clean_files"] += 1
    frame = pd.DataFrame(rows).sort_values(["model", "step", "layer"]).reset_index(drop=True)
    audit["rows"] = int(len(frame))
    audit["models"] = sorted(frame.model.unique().tolist(), key=MODEL_ORDER.index)
    audit["checkpoint_counts"] = {m: int(frame[frame.model == m].step.nunique()) for m in MODEL_ORDER}
    return frame, audit


def ara_coord_from_log_delta(delta: float) -> float:
    return float(1.0 + math.tanh(delta / 2.0))


def model_predictions(g: pd.DataFrame) -> list[dict]:
    model = str(g.model.iloc[0])
    split = str(g.split.iloc[0])
    steps = sorted(g.step.unique())
    layers = sorted(g.layer.unique())
    index = g.set_index(["step", "layer"])
    out: list[dict] = []
    for stream in STREAMS:
        values = np.array([[float(index.loc[(step, layer), stream]) for layer in layers] for step in steps])
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
                broken_child = float(np.median(velocities[k - 4:k - 1, (j + 1) % len(layers)]))
                slope = float(np.polyfit(taus[k - 4:k], logs[k - 4:k, j], 1)[0])
                flows = {
                    "ara": 0.5 * recent_child + 0.5 * recent_parent,
                    "persistence": 0.0,
                    "local_flow": recent_child,
                    "parent_flow": recent_parent,
                    "local_trend": slope,
                    "broken_lineage": 0.5 * broken_child + 0.5 * recent_parent,
                }
                actual_log = float(logs[k, j])
                current_log = float(logs[k - 1, j])
                actual_delta = actual_log - current_log
                for predictor, flow in flows.items():
                    pred_log = current_log + flow * dt
                    pred_delta = pred_log - current_log
                    out.append({
                        "model": model, "split": split, "stream": stream,
                        "target_step": int(steps[k]), "previous_step": int(steps[k - 1]),
                        "layer": int(layer), "n_layers": len(layers), "predictor": predictor,
                        "actual_log": actual_log, "pred_log": pred_log,
                        "abs_error": abs(pred_log - actual_log),
                        "sq_error": (pred_log - actual_log) ** 2,
                        "actual_delta": actual_delta, "pred_delta": pred_delta,
                        "direction_correct": float(np.sign(pred_delta) == np.sign(actual_delta))
                        if abs(actual_delta) > 1e-12 else np.nan,
                        "actual_ara": ara_coord_from_log_delta(actual_delta),
                        "pred_ara": ara_coord_from_log_delta(pred_delta),
                        "ara_abs_error": abs(ara_coord_from_log_delta(pred_delta) - ara_coord_from_log_delta(actual_delta)),
                    })
    return out


def summarize(pred: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    per_model = (pred.groupby(["split", "model", "stream", "predictor"], as_index=False)
                 .agg(mae=("abs_error", "mean"), rmse=("sq_error", lambda x: float(np.sqrt(np.mean(x)))),
                      direction_accuracy=("direction_correct", "mean"),
                      ara_mae=("ara_abs_error", "mean"), n=("abs_error", "size")))
    split_stream = (per_model.groupby(["split", "stream", "predictor"], as_index=False)
                    .agg(mae=("mae", "mean"), rmse=("rmse", "mean"),
                         direction_accuracy=("direction_accuracy", "mean"),
                         ara_mae=("ara_mae", "mean"), models=("model", "nunique")))
    joint = (split_stream.groupby(["split", "predictor"], as_index=False)
             .agg(mae=("mae", "mean"), rmse=("rmse", "mean"),
                  direction_accuracy=("direction_accuracy", "mean"),
                  ara_mae=("ara_mae", "mean"), streams=("stream", "nunique")))
    lookup = joint.set_index(["split", "predictor"])
    ss = split_stream.set_index(["split", "stream", "predictor"])
    gates = {
        "G0_integrity": True,
        "G1_eval_vs_persistence": bool(lookup.loc[("evaluation", "ara"), "mae"] < lookup.loc[("evaluation", "persistence"), "mae"]),
        "G1_holdout_vs_persistence": bool(lookup.loc[("holdout", "ara"), "mae"] < lookup.loc[("holdout", "persistence"), "mae"]),
        "G2_eval_vs_local_trend": bool(lookup.loc[("evaluation", "ara"), "mae"] < lookup.loc[("evaluation", "local_trend"), "mae"]),
        "G2_holdout_vs_local_trend": bool(lookup.loc[("holdout", "ara"), "mae"] < lookup.loc[("holdout", "local_trend"), "mae"]),
        "G3_eval_vs_broken": bool(lookup.loc[("evaluation", "ara"), "mae"] < lookup.loc[("evaluation", "broken_lineage"), "mae"]),
        "G3_holdout_vs_broken": bool(lookup.loc[("holdout", "ara"), "mae"] < lookup.loc[("holdout", "broken_lineage"), "mae"]),
        "G4_holdout_top1_vs_persistence": bool(ss.loc[("holdout", "top1", "ara"), "mae"] < ss.loc[("holdout", "top1", "persistence"), "mae"]),
        "G4_holdout_median_vs_persistence": bool(ss.loc[("holdout", "median", "ara"), "mae"] < ss.loc[("holdout", "median", "persistence"), "mae"]),
        "G5_holdout_direction_vs_local": bool(lookup.loc[("holdout", "ara"), "direction_accuracy"] > lookup.loc[("holdout", "local_flow"), "direction_accuracy"]),
    }
    g1 = gates["G1_eval_vs_persistence"] and gates["G1_holdout_vs_persistence"]
    g2 = gates["G2_eval_vs_local_trend"] and gates["G2_holdout_vs_local_trend"]
    g3 = gates["G3_eval_vs_broken"] and gates["G3_holdout_vs_broken"]
    g4 = gates["G4_holdout_top1_vs_persistence"] and gates["G4_holdout_median_vs_persistence"]
    g5 = gates["G5_holdout_direction_vs_local"]
    if gates["G0_integrity"] and g1 and g2 and g3 and g4 and g5:
        verdict = "SUPPORTED"
    elif gates["G0_integrity"] and g1 and g3:
        verdict = "MIXED/PARTIAL"
    else:
        verdict = "NOT SUPPORTED IN THIS FORM"
    return per_model, pd.concat([split_stream.assign(level="stream"), joint.assign(stream="joint", level="joint")], ignore_index=True), {"gates": gates, "verdict": verdict}


def bootstrap_model_differences(per_model: pd.DataFrame, draws: int = 10000) -> list[dict]:
    """Equal-model bootstrap; positive differences favour ARA."""
    rng = np.random.default_rng(338)
    joint = (per_model.groupby(["split", "model", "predictor"], as_index=False)
             .agg(mae=("mae", "mean"), direction_accuracy=("direction_accuracy", "mean")))
    results: list[dict] = []
    comparisons = [
        ("persistence", "mae"), ("local_trend", "mae"),
        ("broken_lineage", "mae"), ("local_flow", "direction_accuracy"),
    ]
    for split in ["evaluation", "holdout"]:
        q = joint[joint.split == split]
        models = sorted(q.model.unique())
        for comparator, metric in comparisons:
            ara = q[q.predictor == "ara"].set_index("model")[metric].loc[models].to_numpy()
            other = q[q.predictor == comparator].set_index("model")[metric].loc[models].to_numpy()
            diff = (other - ara) if metric == "mae" else (ara - other)
            boot = np.mean(diff[rng.integers(0, len(diff), size=(draws, len(diff)))], axis=1)
            results.append({
                "split": split, "comparator": comparator, "metric": metric,
                "difference_favouring_ara": float(np.mean(diff)),
                "ci95_low": float(np.quantile(boot, 0.025)),
                "ci95_high": float(np.quantile(boot, 0.975)),
                "models": len(models), "draws": draws,
            })
    return results


def main() -> None:
    source = find_source()
    raw, audit = load_raw(source)
    all_predictions: list[dict] = []
    for model in MODEL_ORDER:
        all_predictions.extend(model_predictions(raw[raw.model == model]))
    pred = pd.DataFrame(all_predictions)
    per_model, summary, verdict = summarize(pred)
    bootstrap = bootstrap_model_differences(per_model)
    protocol = HERE / "T338_LLM_TRAINING_DI_ARA_PROTOCOL_v1_FROZEN.md"
    claim = HERE / "T338_LLM_TRAINING_DI_ARA_CLAIM_PACKET_v1.md"
    audit.update({
        "protocol_sha256": sha256(protocol), "claim_sha256": sha256(claim),
        "prediction_rows": int(len(pred)), "source_commit_expected": SOURCE_COMMIT,
    })
    raw.to_csv(HERE / "T338_RAW_REDUCED.csv.gz", index=False, compression="gzip")
    pred.to_csv(HERE / "T338_PREDICTIONS.csv.gz", index=False, compression="gzip")
    per_model.to_csv(HERE / "T338_PER_MODEL_METRICS.csv", index=False)
    summary.to_csv(HERE / "T338_SUMMARY_METRICS.csv", index=False)
    (HERE / "T338_AUDIT.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    (HERE / "T338_VERDICT.json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")
    (HERE / "T338_MODEL_BOOTSTRAP.json").write_text(json.dumps(bootstrap, indent=2), encoding="utf-8")
    print(json.dumps({"audit": audit, **verdict}, indent=2))
    print(summary[(summary.level == "joint") & (summary.predictor.isin(["ara", "persistence", "local_trend", "broken_lineage"]))].to_string(index=False))


if __name__ == "__main__":
    main()
