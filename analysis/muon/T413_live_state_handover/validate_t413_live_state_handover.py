#!/usr/bin/env python3
"""Independent recomputation checks for T413 saved outputs."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
METRICS = RESULTS / "T413_FULL_RUN_METRICS.csv"
PREDICTIONS = RESULTS / "T413_FULL_PREDICTIONS.csv"
RESULT_JSON = RESULTS / "T413_FULL_RESULTS.json"
MANIFEST = HERE / "source" / "T413_SOURCE_MANIFEST.csv"
RAW = HERE / "source" / "raw"
PROTOCOL = HERE / "T413_FROZEN_PROTOCOL.md"
PROTOCOL_HASH = HERE / "T413_FROZEN_PROTOCOL.sha256"
CODE_FREEZE = HERE / "T413_PREHOLDOUT_FREEZE.sha256"
CODE = HERE / "t413_live_state_handover.py"
OUTPUT = RESULTS / "T413_VALIDATION.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_hash_file(path: Path) -> dict[str, str]:
    output = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, name = line.split(None, 1)
        output[name.strip()] = digest.upper()
    return output


def main() -> None:
    metric_rows = rows(METRICS)
    prediction_rows = rows(PREDICTIONS)
    manifest_rows = rows(MANIFEST)
    result = json.loads(RESULT_JSON.read_text(encoding="utf-8"))

    checks: dict[str, bool] = {}
    details: dict[str, object] = {}

    frozen_protocol = parse_hash_file(PROTOCOL_HASH)
    frozen_code = parse_hash_file(CODE_FREEZE)
    checks["protocol_hash_matches_freeze"] = sha256(PROTOCOL).upper() == frozen_protocol["T413_FROZEN_PROTOCOL.md"]
    checks["code_hash_matches_preholdout_freeze"] = sha256(CODE).upper() == frozen_code["t413_live_state_handover.py"]
    checks["result_records_frozen_protocol"] = result["protocol_sha256"].upper() == sha256(PROTOCOL).upper()

    split_counts = defaultdict(int)
    runs = set()
    for row in manifest_rows:
        split_counts[row["split"]] += 1
        runs.add(row["run"])
        path = RAW / f"{row['run']}.nxs"
        if not path.exists() or path.stat().st_size != int(row["file_size"]):
            checks[f"source_size_{row['run']}"] = False
    checks["manifest_split_counts"] = dict(split_counts) == {"development": 13, "validation": 13, "holdout": 20}
    checks["manifest_runs_unique"] = len(runs) == len(manifest_rows) == 46
    checks["all_source_sizes_match"] = not any(name.startswith("source_size_") and not value for name, value in checks.items())

    metric_index = {(row["run"], model): float(row[f"rmse_{model}"])
                    for row in metric_rows
                    for model in ("ara_full", "persistence", "ar1", "diagonal", "harmonic", "wrong_orientation", "broken_order")}
    grouped: dict[tuple[str, str], list[tuple[float, float, float]]] = defaultdict(list)
    for row in prediction_rows:
        grouped[(row["run"], row["model"])].append((
            float(row["observed_A"]), float(row["predicted_A"]), float(row["weight"])
        ))
    maximum_error = 0.0
    for key, triples in grouped.items():
        array = np.asarray(triples, dtype=float)
        recomputed = float(np.sqrt(np.sum(array[:, 2] * (array[:, 0] - array[:, 1]) ** 2) / np.sum(array[:, 2])))
        maximum_error = max(maximum_error, abs(recomputed - metric_index[key]))
    checks["all_primary_rmse_recompute"] = maximum_error < 1e-12
    details["maximum_rmse_recompute_error"] = maximum_error

    holdout = [row for row in metric_rows if row["split"] == "holdout"]
    median_rmse = {}
    for model in ("ara_full", "persistence", "ar1", "diagonal", "harmonic", "wrong_orientation", "broken_order"):
        median_rmse[model] = float(np.median([float(row[f"rmse_{model}"]) for row in holdout]))
    saved = result["aggregate"]["holdout"]["median_rmse"]
    checks["holdout_medians_recompute"] = all(abs(median_rmse[name] - saved[name]) < 1e-12 for name in median_rmse)
    details["holdout_median_rmse"] = median_rmse

    simple_advantage = np.asarray([
        min(float(row["rmse_persistence"]), float(row["rmse_ar1"]), float(row["rmse_diagonal"]))
        - float(row["rmse_ara_full"])
        for row in holdout
    ])
    harmonic_advantage = np.asarray([
        float(row["rmse_harmonic"]) - float(row["rmse_ara_full"])
        for row in holdout
    ])
    checks["primary_relational_gate_recomputes_false"] = (
        np.median(simple_advantage) < 0
        and result["aggregate"]["frozen_gates"]["relational_predictive_support"] is False
    )
    checks["harmonic_advantage_positive"] = float(np.median(harmonic_advantage)) > 0
    checks["holdout_not_used_in_preholdout_file"] = "holdout" not in json.loads(
        (RESULTS / "T413_PREHOLDOUT_RESULTS.json").read_text(encoding="utf-8")
    )["aggregate"]

    output = {
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "details": details,
    }
    OUTPUT.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))
    if output["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
