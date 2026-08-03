#!/usr/bin/env python3
"""Independent validation for T332 bubble-closure zipper calculations."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

from bubble_lineage import load_run


HERE = Path(__file__).resolve().parents[1]
SOURCE = HERE / "source_data"
RESULTS = HERE / "results"
PREFIX = "T332_INFORMATION3_ZIPPER_BUBBLE_CLOSURE"
PROTOCOL = HERE / f"{PREFIX}_PROTOCOL_v1_FROZEN.md"
T329 = RESULTS / "T329_ACTUAL_HANDOVER_PHI_SEAM_EVENTS.csv"
EVENTS = RESULTS / f"{PREFIX}_EVENTS.csv"
NULL = RESULTS / f"{PREFIX}_EVALUATION_RESIDUAL_NULL.csv"
RESULT_JSON = HERE / f"{PREFIX}_RESULTS.json"
FIGURE = HERE / f"{PREFIX}_FIGURE.png"
VALIDATION = HERE / f"{PREFIX}_VALIDATION.json"

BOOTSTRAPS = 5_000
SEED = 20260803 + 332
MIN_STEP_M = 0.0005


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest().upper()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def vec(left, right) -> tuple[float, float]:
    return right.x - left.x, right.y - left.y


def mag(value: tuple[float, float]) -> float:
    return math.hypot(value[0], value[1])


def theta(value: tuple[float, float]) -> float:
    return math.atan2(value[1], value[0])


def sep(left: float, right: float) -> float:
    return abs(math.atan2(math.sin(right - left), math.cos(right - left))) / math.pi


def ranks(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    result = np.empty(len(values), dtype=float)
    cursor = 0
    while cursor < len(values):
        end = cursor + 1
        while end < len(values) and values[order[end]] == values[order[cursor]]:
            end += 1
        result[order[cursor:end]] = (cursor + end - 1) / 2.0 + 1.0
        cursor = end
    return result


def rho(rows: list[dict]) -> float:
    left = ranks(np.asarray([float(row["f_child"]) for row in rows]))
    right = ranks(np.asarray([float(row["f_parent"]) for row in rows]))
    return float(np.corrcoef(left, right)[0, 1])


def mean_ci(rows: list[dict], field: str, offset: int) -> tuple[float, float]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        value = float(row[field])
        if math.isfinite(value):
            grouped[row["video"]].append(value)
    videos = sorted(grouped)
    random = np.random.default_rng(SEED + offset)
    draws = []
    for _ in range(BOOTSTRAPS):
        chosen = random.choice(videos, size=len(videos), replace=True)
        sample = [value for video in chosen for value in grouped[str(video)]]
        draws.append(float(np.mean(sample)))
    return tuple(float(value) for value in np.quantile(draws, [0.025, 0.975]))


def rho_ci(rows: list[dict], offset: int) -> tuple[float, float]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["video"]].append(row)
    videos = sorted(grouped)
    random = np.random.default_rng(SEED + offset)
    draws = []
    for _ in range(BOOTSTRAPS):
        chosen = random.choice(videos, size=len(videos), replace=True)
        sample = [row for video in chosen for row in grouped[str(video)]]
        value = rho(sample)
        if math.isfinite(value):
            draws.append(value)
    return tuple(float(value) for value in np.quantile(draws, [0.025, 0.975]))


def main() -> None:
    production = read_csv(EVENTS)
    source_events = read_csv(T329)
    result = json.loads(RESULT_JSON.read_text(encoding="utf-8"))
    production_by_key = {
        (row["video"], int(row["frame"]), int(row["inherited_id"]), int(row["joining_id"])): row
        for row in production
    }

    max_errors = defaultdict(float)
    valid_steps = True
    for filename in sorted({row["file"] for row in source_events}):
        run = load_run(SOURCE / filename)
        for item in [row for row in source_events if row["file"] == filename]:
            key = (
                item["video"],
                int(item["frame"]),
                int(item["inherited_id"]),
                int(item["joining_id"]),
            )
            row = production_by_key[key]
            frame = key[1]
            inherited = run.tracks[key[2]]
            joining = run.tracks[key[3]]
            v_i = vec(inherited[frame - 1], inherited[frame])
            v_j = vec(joining[frame - 1], joining[frame])
            v_p1 = vec(inherited[frame + 1], inherited[frame + 2])
            v_p2 = vec(inherited[frame + 2], inherited[frame + 3])
            valid_steps &= all(mag(value) >= MIN_STEP_M for value in (v_i, v_j, v_p1, v_p2))
            f_child = sep(theta(v_i), theta(v_j))
            f_parent = sep(theta(v_p1), theta(v_p2))
            max_errors["f_child"] = max(max_errors["f_child"], abs(f_child - float(row["f_child"])))
            max_errors["f_parent"] = max(max_errors["f_parent"], abs(f_parent - float(row["f_parent"])))
            max_errors["zipper_contraction"] = max(
                max_errors["zipper_contraction"],
                abs((f_child - f_parent) - float(row["zipper_contraction"])),
            )
            if frame - 2 in inherited:
                prior = vec(inherited[frame - 2], inherited[frame - 1])
                if mag(prior) >= MIN_STEP_M:
                    expected = sep(theta(prior), theta(v_i)) - f_parent
                    max_errors["event_specificity"] = max(
                        max_errors["event_specificity"],
                        abs(expected - float(row["event_specificity"])),
                    )

    checks: dict[str, bool] = {
        "protocol_hash": digest(PROTOCOL) == result["protocol_sha256"],
        "source_hash": digest(T329) == result["source_t329_events_sha256"],
        "event_count_91": len(production) == len(source_events) == 91,
        "all_primary_steps_above_floor": bool(valid_steps),
        "raw_metric_recalculation": max(max_errors.values(), default=0.0) < 1e-12,
    }

    split_offsets = {"calibration": 0, "evaluation": 100, "holdout": 200}
    residual_offsets = {"calibration": 900, "evaluation": 901, "holdout": 902}
    for split in ("calibration", "evaluation", "holdout"):
        group = [row for row in production if row["split"] == split]
        source_summary = result["summaries"][split]
        mean_z = float(np.mean([float(row["zipper_contraction"]) for row in group]))
        checks[f"{split}_mean_z"] = abs(mean_z - source_summary["zipper_contraction"]["mean"]) < 1e-12
        low, high = mean_ci(group, "zipper_contraction", split_offsets[split] + 2)
        checks[f"{split}_z_ci"] = (
            abs(low - source_summary["zipper_contraction"]["ci_low"]) < 1e-12
            and abs(high - source_summary["zipper_contraction"]["ci_high"]) < 1e-12
        )
        ordinary = [row for row in group if math.isfinite(float(row["event_specificity"]))]
        low, high = mean_ci(ordinary, "event_specificity", 500 + list(("calibration", "evaluation", "holdout")).index(split))
        checks[f"{split}_ordinary_ci"] = (
            abs(low - source_summary["event_specificity"]["ci_low"]) < 1e-12
            and abs(high - source_summary["event_specificity"]["ci_high"]) < 1e-12
        )

        counts = defaultdict(int)
        for row in group:
            counts[row["video"]] += 1
        residual_rows = [row for row in group if counts[row["video"]] >= 2]
        observed = rho(residual_rows)
        source_residual = result["residual_inheritance"][split]
        checks[f"{split}_rho"] = abs(observed - source_residual["spearman"]) < 1e-12
        low, high = rho_ci(residual_rows, residual_offsets[split])
        checks[f"{split}_rho_ci"] = (
            abs(low - source_residual["ci_low"]) < 1e-12
            and abs(high - source_residual["ci_high"]) < 1e-12
        )

    null = np.asarray([float(row["spearman"]) for row in read_csv(NULL)], dtype=float)
    eval_rho = result["residual_inheritance"]["evaluation"]["spearman"]
    p_value = float((1 + np.sum(null >= eval_rho)) / (len(null) + 1))
    checks["evaluation_null_count"] = len(null) == BOOTSTRAPS
    checks["evaluation_null_p"] = abs(
        p_value - result["residual_inheritance"]["evaluation"]["p_one_sided"]
    ) < 1e-12

    amplitude_checks = []
    for amplitude_index, amplitude in enumerate(
        sorted({float(row["amplitude"]) for row in production})
    ):
        group = [row for row in production if float(row["amplitude"]) == amplitude]
        source = result["post_result_amplitude_summary"][f"{amplitude:g}"]
        mean_z = float(np.mean([float(row["zipper_contraction"]) for row in group]))
        low, high = mean_ci(group, "zipper_contraction", 1500 + amplitude_index)
        amplitude_checks.append(
            abs(mean_z - source["mean"]) < 1e-12
            and abs(low - source["ci_low"]) < 1e-12
            and abs(high - source["ci_high"]) < 1e-12
        )
    checks["post_result_amplitude_summary"] = all(amplitude_checks)

    eval_z = result["summaries"]["evaluation"]["zipper_contraction"]
    hold_z = result["summaries"]["holdout"]["zipper_contraction"]
    eval_e = result["summaries"]["evaluation"]["event_specificity"]
    hold_e = result["summaries"]["holdout"]["event_specificity"]
    eval_r = result["residual_inheritance"]["evaluation"]
    hold_r = result["residual_inheritance"]["holdout"]
    gates = {
        "local_contraction": eval_z["ci_low"] > 0 and hold_z["mean"] > 0,
        "event_specificity": eval_e["ci_low"] > 0 and hold_e["mean"] > 0,
        "immediate_residual_inheritance": (
            eval_r["spearman"] > 0
            and eval_r["ci_low"] > 0
            and eval_r["p_one_sided"] < 0.05
            and hold_r["spearman"] > 0
        ),
    }
    checks["gate_recalculation"] = all(
        gates[name] == result["gates"][name] for name in gates
    )

    with Image.open(FIGURE) as image:
        checks["figure_dimensions"] = image.width >= 2000 and image.height >= 1400

    validation = {
        "test": "T332 independent validation",
        "run_date": "2026-08-03",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "max_absolute_metric_errors": dict(max_errors),
        "recalculated_gates": gates,
        "boundaries": [
            "Validation confirms implementation and frozen-gate arithmetic, not the truth of ARA.",
            "The later ordered-closure claim remains unavailable in this archive.",
        ],
    }
    VALIDATION.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, indent=2))
    if validation["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
