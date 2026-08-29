#!/usr/bin/env python3
"""Post-hoc T415 diagnostic: does share strength beat parent history?

This file does not alter the frozen T415 result. It tests whether the apparent
gain from lagged detector-share strength remains after current total rate and
its one-bin slope are included in the parent baseline.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
sys.path.insert(0, str(HERE))
import t415_multichannel_state_array as t415


HORIZON = 4
MODELS = {
    "D0 parent + history": ["parent", "parent2", "current_rate", "rate_change"],
    "D1 + spin": [
        "parent", "parent2", "current_rate", "rate_change",
        "spin_a", "spin_b", "parent_spin_a", "parent_spin_b",
    ],
    "D2 + strength": [
        "parent", "parent2", "current_rate", "rate_change",
        "spin_a", "spin_b", "parent_spin_a", "parent_spin_b",
        "strength", "strength_change", "strength_spin_a", "strength_spin_b",
    ],
    "D3 full diagnostic": [
        "parent", "parent2", "current_rate", "rate_change",
        "spin_a", "spin_b", "parent_spin_a", "parent_spin_b",
        "strength", "strength_change", "strength_spin_a", "strength_spin_b",
        "field", "rf", "field_spin_a", "field_spin_b", "rf_spin_a", "rf_spin_b",
        "lock_a", "lock_b", "parent_strength_change",
    ],
}


def prepare(rows: list[dict]) -> dict:
    records: list[dict] = []
    matrices = {name: [] for name in MODELS}
    targets = []
    for row in rows:
        for period in ("RF on", "RF off"):
            data = t415.period_arrays(row, period)
            time = data["time"]
            current_index = np.arange(1, len(time) - HORIZON)
            current_index = current_index[time[current_index] >= t415.PREDICT_MIN_US]
            target_index = current_index + HORIZON
            current_time = time[current_index]
            parent = 2.0 * (1.0 - np.exp(-current_time / t415.TAU_US))
            theta = 2.0 * np.pi * t415.GAMMA_MHZ_PER_G * float(row["field_G"]) * current_time
            spin_a = np.sin(theta)
            spin_b = np.cos(theta)
            strength = np.asarray(data["strength"])[current_index]
            strength_change = np.asarray(data["strength_change"])[current_index]
            rf = 1.0 if period == "RF on" else 0.0
            values = t415.feature_values(
                parent, spin_a, spin_b, strength, strength_change,
                float(row["field_G"]), rf,
            )
            log_rate = np.log(np.maximum(data["rate"], 1e-15) / float(data["reference_rate"]))
            values["current_rate"] = log_rate[current_index]
            values["rate_change"] = log_rate[current_index] - log_rate[current_index - 1]
            for model, names in MODELS.items():
                matrices[model].append(np.column_stack([values[name] for name in names]))
            targets.append(log_rate[target_index])
            for local, index in enumerate(current_index):
                records.append({
                    "run": row["run"],
                    "period": period,
                    "field_G": float(row["field_G"]),
                    "current_log_rate": float(values["current_rate"][local]),
                    "strength": float(strength[local]),
                })
    return {
        "records": records,
        "X": {name: np.vstack(parts) for name, parts in matrices.items()},
        "y": np.concatenate(targets),
    }


def choose_lambda(dataset: dict, model: str) -> float:
    records = dataset["records"]
    runs = sorted({row["run"] for row in records})
    x = dataset["X"][model]
    y = dataset["y"]
    candidates = []
    for lam in t415.LAMBDAS:
        scores = []
        for run in runs:
            mask = np.asarray([row["run"] == run for row in records], dtype=bool)
            fitted = t415.fit_ridge(x[~mask], y[~mask], lam)
            pred = t415.predict(fitted, x[mask])
            scores.append(float(np.sqrt(np.mean((y[mask] - pred) ** 2))))
        candidates.append((float(np.median(scores)), float(lam)))
    return min(candidates)[1]


def main() -> None:
    manifest = t415.t414.read_manifest()
    development_rows = [row for row in manifest if row["split"] == "development"]
    validation_rows = [row for row in manifest if row["split"] == "validation"]
    development = prepare(development_rows)
    validation = prepare(validation_rows)
    predictions = {}
    fitted_models = {}
    summary = []
    for model, names in MODELS.items():
        lam = choose_lambda(development, model)
        fitted = t415.fit_ridge(development["X"][model], development["y"], lam)
        pred = t415.predict(fitted, validation["X"][model])
        predictions[model] = pred
        fitted_models[model] = {"lambda": lam, "features": names}
    base = t415.field_rmse(validation["records"], validation["y"], predictions["D0 parent + history"])
    field_rows = []
    for model in MODELS:
        scores = t415.field_rmse(validation["records"], validation["y"], predictions[model])
        improvements = []
        for run, rmse in scores.items():
            field = next(row["field_G"] for row in validation_rows if row["run"] == run)
            improvement = 1.0 - rmse / base[run]
            improvements.append(improvement)
            field_rows.append({
                "run": run,
                "field_G": field,
                "model": model,
                "rmse_log_rate": rmse,
                "parent_history_rmse_log_rate": base[run],
                "improvement_fraction": improvement,
            })
        summary.append({
            "model": model,
            "lambda": fitted_models[model]["lambda"],
            "median_field_improvement_fraction": float(np.median(improvements)),
            "mean_field_improvement_fraction": float(np.mean(improvements)),
            "field_wins": int(np.sum(np.asarray(improvements) > 0)),
            "field_count": len(improvements),
            "median_field_rmse_log_rate": float(np.median(list(scores.values()))),
        })
    current_rate = np.asarray([row["current_log_rate"] for row in validation["records"]])
    strength = np.asarray([row["strength"] for row in validation["records"]])
    edges = np.quantile(strength, np.linspace(0.0, 1.0, 11))
    edges = np.maximum.accumulate(edges)
    strength_rate_rows = []
    for index in range(10):
        if index == 9:
            mask = (strength >= edges[index]) & (strength <= edges[index + 1])
        else:
            mask = (strength >= edges[index]) & (strength < edges[index + 1])
        values = current_rate[mask]
        strength_rate_rows.append({
            "strength_decile": index + 1,
            "mean_strength": float(np.mean(strength[mask])),
            "mean_current_log_rate": float(np.mean(values)),
            "se_current_log_rate": float(np.std(values, ddof=1) / np.sqrt(len(values))),
            "sample_bins": int(len(values)),
        })
    diagnostics = {
        "status": "post-hoc diagnostic; does not alter frozen T415",
        "horizon_bins": HORIZON,
        "horizon_us": HORIZON * 0.016,
        "strength_vs_current_log_rate_correlation": float(np.corrcoef(strength, current_rate)[0, 1]),
        "models": summary,
    }
    (RESULTS / "T415_POSTHOC_PARENT_HISTORY.json").write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
    t415.write_csv(RESULTS / "T415_POSTHOC_PARENT_HISTORY_SUMMARY.csv", summary)
    t415.write_csv(RESULTS / "T415_POSTHOC_PARENT_HISTORY_FIELDS.csv", field_rows)
    t415.write_csv(RESULTS / "T415_POSTHOC_STRENGTH_RATE_DECILES.csv", strength_rate_rows)
    print(json.dumps(diagnostics, indent=2))


if __name__ == "__main__":
    main()
