"""Independent integrity checks for the scored T336 artifacts."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "t336_enso_di_ara_handover.py"
PROTOCOL = HERE / "T336_ENSO_DI_ARA_HANDOVER_PROTOCOL_v1_FROZEN.md"
HASH_FILE = HERE / "T336_ENSO_DI_ARA_HANDOVER_PROTOCOL_v1_FROZEN.sha256"
RESULTS = HERE / "T336_ENSO_DI_ARA_HANDOVER_RESULTS.json"
FORECASTS = HERE / "T336_ENSO_DI_ARA_HANDOVER_FORECASTS.csv"
OUT = HERE / "T336_ENSO_DI_ARA_HANDOVER_VALIDATION.json"
TOL = 1e-10


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_module():
    spec = importlib.util.spec_from_file_location("t336", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def metric(rows: list[dict[str, str]], model: str) -> dict[str, float]:
    pred = np.asarray([float(r[model]) for r in rows])
    truth = np.asarray([float(r["truth"]) for r in rows])
    current = np.asarray([float(r["current"]) for r in rows])
    clim = np.asarray([float(r["climatology"]) for r in rows])
    mse = float(np.mean((pred - truth) ** 2))
    cmse = float(np.mean((clim - truth) ** 2))
    corr = float(np.corrcoef(pred, truth)[0, 1]) if np.std(pred) > 1e-9 else float("nan")
    change = truth - current
    mask = np.abs(change) > 1e-9
    direction = float(np.mean(np.sign(pred[mask] - current[mask]) == np.sign(change[mask])))
    return {
        "mse": mse,
        "skill_vs_climatology": 1.0 - mse / cmse,
        "mae": float(np.mean(np.abs(pred - truth))),
        "corr": corr,
        "direction": direction,
    }


def main() -> None:
    checks: list[dict] = []

    expected = {}
    for line in HASH_FILE.read_text(encoding="utf-8").splitlines():
        digest, name = line.split(maxsplit=1)
        expected[name.strip()] = digest
    for path in (PROTOCOL, SCRIPT):
        actual = sha256(path)
        want = expected[path.name]
        checks.append({"name": f"frozen_hash_{path.name}", "passed": actual == want, "actual": actual, "expected": want})

    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    rows = list(csv.DictReader(FORECASTS.open(encoding="utf-8")))
    checks.append({"name": "forecast_rows_present", "passed": len(rows) > 0, "rows": len(rows)})

    mod = load_module()
    nino = mod.load_nino(mod.NINO_PATH)
    west = mod.load_wwv(mod.WWV_WEST_PATH)
    east = mod.load_wwv(mod.WWV_EAST_PATH)
    keys = sorted(set(nino) & set(west) & set(east))
    month_ids = np.asarray([int(k[:4]) * 12 + int(k[4:6]) - 1 for k in keys])
    checks.append({"name": "common_months_are_strictly_contiguous", "passed": bool(np.all(np.diff(month_ids) == 1)), "first": keys[0], "last": keys[-1], "months": len(keys)})
    checks.append({"name": "result_range_matches_source", "passed": result["data"]["first_common_month"] == keys[0] and result["data"]["last_common_month"] == keys[-1] and result["data"]["months"] == len(keys)})

    models = (
        "climatology", "persistence", "base_levels", "base_raw_movement",
        "base_diara", "base_radius", "base_turn", "base_quadrant", "base_broken_diara",
    )
    metric_ok = True
    max_metric_diff = 0.0
    count_ok = True
    horizon_ok = True
    split_ok = True
    key_index = {k: i for i, k in enumerate(keys)}
    for split in ("evaluation", "holdout"):
        for horizon in mod.HORIZONS:
            subset = [r for r in rows if r["split"] == split and int(r["horizon"]) == horizon]
            stored = result["scores"][split][str(horizon)]
            if len(subset) != stored["base_diara"]["n"]:
                count_ok = False
            for row in subset:
                oi = key_index[row["origin"]]
                ti = key_index[row["target"]]
                horizon_ok &= ti - oi == horizon
                split_ok &= (split == "holdout") == (float(row["origin_year"]) >= mod.HOLDOUT_START)
            for model in models:
                got = metric(subset, model)
                for name, value in got.items():
                    expected_value = float(stored[model][name])
                    diff = abs(value - expected_value)
                    max_metric_diff = max(max_metric_diff, diff)
                    metric_ok &= diff <= TOL
    checks.append({"name": "row_counts_match_json", "passed": bool(count_ok)})
    checks.append({"name": "targets_are_exact_declared_horizons", "passed": bool(horizon_ok)})
    checks.append({"name": "split_labels_match_2017_boundary", "passed": bool(split_ok)})
    checks.append({"name": "all_metrics_recompute_from_forecast_rows", "passed": bool(metric_ok), "max_absolute_difference": max_metric_diff})

    # Prefix invariance: an origin's feature vectors must not change if all
    # later observations are perturbed, because the implementation standardises
    # only through the declared origin.
    t = np.asarray([nino[k] for k in keys], dtype=float)
    w = np.asarray([west[k] for k in keys], dtype=float)
    e = np.asarray([east[k] for k in keys], dtype=float)
    months = np.asarray([int(k[4:6]) for k in keys], dtype=int)
    origin = key_index["201201"]
    before = mod.feature_sets(origin, t, w, e, months, origin)
    t2, w2, e2 = t.copy(), w.copy(), e.copy()
    t2[origin + 1 :] += 999.0
    w2[origin + 1 :] -= 777.0
    e2[origin + 1 :] += 555.0
    after = mod.feature_sets(origin, t2, w2, e2, months, origin)
    prefix_diff = max(float(np.max(np.abs(before[k] - after[k]))) for k in before)
    checks.append({"name": "feature_prefix_invariance", "passed": prefix_diff == 0.0, "max_absolute_difference": prefix_diff})

    primary = result["scores"]["holdout"]["6"]
    di = primary["base_diara"]
    raw = primary["base_raw_movement"]
    levels = primary["base_levels"]
    broken = primary["base_broken_diara"]
    gates = {
        "point_estimates_beat_levels_and_raw_movement": (
            di["skill_vs_climatology"] > levels["skill_vs_climatology"]
            and di["mae"] < levels["mae"]
            and di["skill_vs_climatology"] > raw["skill_vs_climatology"]
            and di["mae"] < raw["mae"]
        ),
        "bootstrap_ci_above_zero_vs_raw_movement": result["bootstrap_primary_h6_holdout"]["vs_base_raw_movement"]["ci95_low"] > 0.0,
        "intact_not_matched_on_both_metrics_by_broken_relation": not (
            broken["skill_vs_climatology"] >= di["skill_vs_climatology"]
            and broken["mae"] <= di["mae"]
        ),
    }
    checks.append({"name": "stored_gates_recompute", "passed": gates == result["gates"], "recomputed": gates})
    expected_verdict = "SUPPORTED_ON_FIXED_REPLAY" if all(gates.values()) else (
        "PROVISIONAL_ON_FIXED_REPLAY"
        if gates["point_estimates_beat_levels_and_raw_movement"] and gates["intact_not_matched_on_both_metrics_by_broken_relation"]
        else "NOT_SUPPORTED_IN_THIS_FORM"
    )
    checks.append({"name": "stored_verdict_recomputes", "passed": expected_verdict == result["verdict"], "expected": expected_verdict, "stored": result["verdict"]})

    out = {
        "test": "T336",
        "passed": all(c["passed"] for c in checks),
        "checks_passed": sum(bool(c["passed"]) for c in checks),
        "checks_total": len(checks),
        "checks": checks,
    }
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

