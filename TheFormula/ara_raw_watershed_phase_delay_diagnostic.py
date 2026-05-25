"""
ara_raw_watershed_phase_delay_diagnostic.py

Diagnostic-only phase-delay scan for the raw watershed lower-spin forecast wave.

This does not refit or improve the forecast. It asks:

    If we compare the generated wave to truth shifted by N months, where does
    correlation/MAE look best?

Negative best shifts mean the generated wave resembles earlier truth, i.e. the
forecast shape is arriving late on the visual timeline.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
IN_JSON = HERE / "ara_raw_watershed_lower_spin_result.json"
OUT_JSON = HERE / "ara_raw_watershed_phase_delay_result.json"
OUT_JS = HERE / "ara_raw_watershed_phase_delay_result.js"

MODELS = ["lower_spin_formula", "lower_spin_scaled", "lower_spin_decoder", "persistence"]
SHIFT_MONTHS = list(range(-60, 61))
FOCUS_HORIZONS = ["6", "12", "24"]


def clean(value):
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean(v) for v in value]
    if isinstance(value, tuple):
        return [clean(v) for v in value]
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, (np.floating, float)):
        value = float(value)
        return value if math.isfinite(value) else None
    return value


def add_months(date_str, months):
    date = datetime.strptime(date_str, "%Y-%m-%d")
    month_index = date.year * 12 + (date.month - 1) + int(months)
    year = month_index // 12
    month = month_index % 12 + 1
    return f"{year:04d}-{month:02d}-01"


def corr(xs, ys):
    if len(xs) < 3:
        return None
    x = np.asarray(xs, dtype=float)
    y = np.asarray(ys, dtype=float)
    if float(np.std(x)) < 1e-12 or float(np.std(y)) < 1e-12:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def score_shift(records, observed, model, shift):
    pred = []
    truth = []
    for record in records:
        shifted_date = add_months(record["target"], shift)
        if shifted_date not in observed:
            continue
        pred.append(float(record[model]))
        truth.append(float(observed[shifted_date]))
    if len(pred) < 8:
        return {"n": len(pred), "corr": None, "mae": None, "rmse": None}
    p = np.asarray(pred, dtype=float)
    y = np.asarray(truth, dtype=float)
    return {
        "n": int(len(pred)),
        "corr": corr(pred, truth),
        "mae": float(np.mean(np.abs(p - y))),
        "rmse": float(np.sqrt(np.mean((p - y) ** 2))),
    }


def best_scan(records, observed, model):
    scan = []
    for shift in SHIFT_MONTHS:
        row = score_shift(records, observed, model, shift)
        row["truth_shift_months"] = int(shift)
        scan.append(row)
    corr_rows = [row for row in scan if row["corr"] is not None]
    mae_rows = [row for row in scan if row["mae"] is not None]
    best_corr = max(corr_rows, key=lambda r: r["corr"]) if corr_rows else None
    best_mae = min(mae_rows, key=lambda r: r["mae"]) if mae_rows else None
    zero = next((row for row in scan if row["truth_shift_months"] == 0), None)
    return {
        "zero_shift": zero,
        "best_corr_shift": best_corr,
        "best_mae_shift": best_mae,
        "scan": scan,
    }


def aggregate_focus(results, model, best_key):
    rows = [results[h][model][best_key] for h in FOCUS_HORIZONS if results.get(h, {}).get(model, {}).get(best_key)]
    if not rows:
        return None
    return {
        "mean_truth_shift_months": float(np.mean([r["truth_shift_months"] for r in rows])),
        "median_truth_shift_months": float(np.median([r["truth_shift_months"] for r in rows])),
        "mean_corr": float(np.mean([r["corr"] for r in rows if r["corr"] is not None])),
        "mean_mae": float(np.mean([r["mae"] for r in rows if r["mae"] is not None])),
    }


def run():
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))
    observed = {row["date"]: row["nino"] for row in data["observed_series"]}
    results = {}
    for horizon, records in data["viz_records"].items():
        results[horizon] = {}
        for model in MODELS:
            results[horizon][model] = best_scan(records, observed, model)

    focus = {
        model: {
            "best_corr_shift": aggregate_focus(results, model, "best_corr_shift"),
            "best_mae_shift": aggregate_focus(results, model, "best_mae_shift"),
        }
        for model in MODELS
    }
    out = {
        "date": "2026-05-25",
        "method": "diagnostic-only phase-delay scan for raw watershed lower-spin wave",
        "interpretation": {
            "truth_shift_months": "Truth date compared to a fixed forecast target date. Negative means the generated wave resembles earlier truth, so the generated wave is visually late.",
            "visual_shift_months": "Use the same value to shift the generated forecast line on the visualizer.",
            "not_a_forecast": "This is a post-hoc diagnostic of timing error, not a causal prediction improvement.",
        },
        "models": MODELS,
        "shift_months": SHIFT_MONTHS,
        "focus_horizons": FOCUS_HORIZONS,
        "focus": focus,
        "by_horizon": results,
    }
    OUT_JSON.write_text(json.dumps(clean(out), indent=2), encoding="utf-8")
    OUT_JS.write_text(
        "window.ARA_RAW_WATERSHED_PHASE_DELAY = " + json.dumps(clean(out), allow_nan=False) + ";\n",
        encoding="utf-8",
    )
    print("Phase-delay scan")
    print("=" * 80)
    for horizon in data["horizons_months"]:
        h = str(horizon)
        print(f"h={h} months")
        for model in MODELS:
            info = results[h][model]
            z = info["zero_shift"]
            bc = info["best_corr_shift"]
            bm = info["best_mae_shift"]
            print(
                f"  {model:20s}"
                f" zero_corr={z['corr'] if z['corr'] is not None else float('nan'):+.3f}"
                f" best_corr_shift={bc['truth_shift_months']:+d} corr={bc['corr']:+.3f}"
                f" best_mae_shift={bm['truth_shift_months']:+d} mae={bm['mae']:.3f}"
            )
    print("Focus 6/12/24:")
    for model, info in focus.items():
        bc = info["best_corr_shift"]
        bm = info["best_mae_shift"]
        print(
            f"  {model:20s}"
            f" corr_shift_mean={bc['mean_truth_shift_months']:+.1f}"
            f" mae_shift_mean={bm['mean_truth_shift_months']:+.1f}"
            f" mean_corr={bc['mean_corr']:+.3f}"
            f" mean_mae={bm['mean_mae']:.3f}"
        )
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    run()
