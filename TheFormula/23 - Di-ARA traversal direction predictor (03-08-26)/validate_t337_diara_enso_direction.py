"""Independent consistency validator for frozen T337 outputs."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "T337_DI_ARA_ENSO_DIRECTION_RESULTS.json"
ROWS = HERE / "T337_DI_ARA_ENSO_DIRECTION_SCORES.csv"
HASHES = HERE / "T337_DI_ARA_ENSO_DIRECTION_PROTOCOL_v1_FROZEN.sha256"
OUTPUT = HERE / "T337_DI_ARA_ENSO_DIRECTION_VALIDATION.json"
EPS = 1e-12


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def import_test_module():
    path = HERE / "t337_diara_enso_direction.py"
    spec = importlib.util.spec_from_file_location("t337_frozen", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load frozen script")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def auc_rank(scores: np.ndarray, labels: np.ndarray) -> float:
    positive = scores[labels > 0]
    negative = scores[labels < 0]
    comparisons = positive[:, None] - negative[None, :]
    return float((np.sum(comparisons > 0) + 0.5 * np.sum(comparisons == 0)) / comparisons.size)


def metrics(rows: list[dict[str, str]], model: str) -> dict[str, float | int]:
    scores = np.asarray([float(row[model]) for row in rows])
    labels = np.asarray([float(row["label"]) for row in rows])
    predictions = np.where(scores >= 0.0, 1.0, -1.0)
    pos = labels > 0
    neg = labels < 0
    pos_recall = float(np.mean(predictions[pos] == labels[pos]))
    neg_recall = float(np.mean(predictions[neg] == labels[neg]))
    return {
        "n": len(rows),
        "positive_n": int(np.sum(pos)),
        "negative_n": int(np.sum(neg)),
        "balanced_accuracy": 0.5 * (pos_recall + neg_recall),
        "accuracy": float(np.mean(predictions == labels)),
        "positive_recall": pos_recall,
        "negative_recall": neg_recall,
        "auc": auc_rank(scores, labels),
    }


def main() -> dict:
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    with ROWS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    expected_hashes = {}
    for line in HASHES.read_text(encoding="utf-8").splitlines():
        digest, name = line.split(maxsplit=1)
        expected_hashes[name.strip()] = digest

    checks: list[dict] = []

    def add(name: str, passed: bool, **detail):
        checks.append({"name": name, "passed": bool(passed), **detail})

    for name, expected in expected_hashes.items():
        actual = sha256(HERE / name)
        add(f"frozen_hash_{name}", actual == expected, actual=actual, expected=expected)

    add("score_rows_present", len(rows) > 0, rows=len(rows))
    horizons = {int(row["horizon"]) for row in rows}
    add("only_declared_horizons", horizons == {3, 6, 9, 12}, horizons=sorted(horizons))
    split_ok = all((row["split"] == "holdout") == (float(row["origin_year"]) >= 2017.0) for row in rows)
    add("split_boundary_exact", split_ok)
    label_ok = all(float(row["label"]) == float(np.sign(float(row["change"]))) and abs(float(row["change"])) > 0 for row in rows)
    add("labels_match_nonzero_future_change", label_ok)

    models = (
        "past_trend",
        "base_levels",
        "base_raw_movement",
        "base_turn",
        "base_diara",
        "base_radius",
        "base_quadrant",
        "base_broken_diara",
    )
    max_difference = 0.0
    for split in ("evaluation", "holdout"):
        for horizon in (3, 6, 9, 12):
            selected = [row for row in rows if row["split"] == split and int(row["horizon"]) == horizon]
            for model in models:
                calculated = metrics(selected, model)
                stored = results["scores"][split][str(horizon)][model]
                for field, value in calculated.items():
                    difference = abs(float(value) - float(stored[field]))
                    max_difference = max(max_difference, difference)
    add("all_direction_metrics_recompute", max_difference <= EPS, max_absolute_difference=max_difference)

    module = import_test_module()
    nino = module.load_nino(module.NINO_PATH)
    west = module.load_wwv(module.WWV_WEST_PATH)
    east = module.load_wwv(module.WWV_EAST_PATH)
    keys = sorted(set(nino) & set(west) & set(east))
    t = np.asarray([nino[key] for key in keys], dtype=float)
    w = np.asarray([west[key] for key in keys], dtype=float)
    e = np.asarray([east[key] for key in keys], dtype=float)
    months = np.asarray([int(key[4:6]) for key in keys], dtype=int)
    origin = keys.index("201806")
    before = module.feature_sets(origin, t, w, e, months, origin)
    t2, w2, e2 = t.copy(), w.copy(), e.copy()
    t2[origin + 1 :] += 1000.0
    w2[origin + 1 :] -= 1000.0
    e2[origin + 1 :] += 500.0
    after = module.feature_sets(origin, t2, w2, e2, months, origin)
    prefix_difference = max(float(np.max(np.abs(before[name] - after[name]))) for name in before)
    add("feature_prefix_invariance", prefix_difference <= EPS, max_absolute_difference=prefix_difference)

    primary = results["scores"]["holdout"]["6"]
    turn = primary["base_turn"]
    levels = primary["base_levels"]
    raw = primary["base_raw_movement"]
    broken = primary["base_broken_diara"]
    gates = {
        "turn_beats_levels_and_raw_by_0_02_balanced_accuracy": (
            turn["balanced_accuracy"] >= levels["balanced_accuracy"] + 0.02
            and turn["balanced_accuracy"] >= raw["balanced_accuracy"] + 0.02
        ),
        "ordinary_accuracy_not_lower": turn["accuracy"] >= levels["accuracy"] and turn["accuracy"] >= raw["accuracy"],
        "bootstrap_ci_above_zero_vs_raw_movement": results["bootstrap_primary_h6_holdout"]["vs_base_raw_movement"]["ci95_low"] > 0,
        "intact_turn_beats_broken_full_relation": turn["balanced_accuracy"] > broken["balanced_accuracy"],
    }
    add("stored_gates_recompute", gates == results["gates"], recomputed=gates)
    if all(gates.values()):
        verdict = "SUPPORTED_ON_FIXED_REPLAY"
    elif gates["turn_beats_levels_and_raw_by_0_02_balanced_accuracy"] and gates["ordinary_accuracy_not_lower"] and gates["intact_turn_beats_broken_full_relation"]:
        verdict = "PROVISIONAL_ON_FIXED_REPLAY"
    else:
        verdict = "NOT_SUPPORTED_IN_THIS_FORM"
    add("stored_verdict_recomputes", verdict == results["verdict"], expected=verdict, stored=results["verdict"])

    validation = {
        "test": "T337",
        "passed": all(check["passed"] for check in checks),
        "checks_passed": sum(check["passed"] for check in checks),
        "checks_total": len(checks),
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))
    return validation


if __name__ == "__main__":
    main()
