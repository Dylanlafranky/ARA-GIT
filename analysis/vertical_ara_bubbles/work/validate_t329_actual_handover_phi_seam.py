#!/usr/bin/env python3
"""Independent structural and numerical validator for T329."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parents[1]
SOURCE = HERE / "source_data"
RESULTS = HERE / "results"
PREFIX = "T329_ACTUAL_HANDOVER_PHI_SEAM"
RESULT_PATH = HERE / f"{PREFIX}_RESULTS.json"
EVENT_PATH = RESULTS / f"{PREFIX}_EVENTS.csv"
SCORE_PATH = RESULTS / f"{PREFIX}_CANDIDATE_SCORES.csv"
CONTROL_PATH = RESULTS / f"{PREFIX}_CONTROLS.csv"
VALIDATION_PATH = HERE / f"{PREFIX}_VALIDATION.json"
FIGURE_PATH = HERE / f"{PREFIX}_FIGURE.png"

BOOTSTRAPS = 5_000
SEED = 20260802 + 329
PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_DELTA = 2.0 / PHI


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def d2(left: float, right: float) -> float:
    difference = abs(left - right)
    return min(difference, 2.0 - difference)


def signed_angle(left: float, right: float) -> float:
    return math.atan2(math.sin(right - left), math.cos(right - left))


def oriented_coordinate(start: float, end: float, sign: float) -> float:
    return (sign * signed_angle(start, end) / math.pi) % 2.0


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def cluster_bootstrap(records: list[tuple[str, float]], offset: int) -> dict:
    by_video: dict[str, list[float]] = defaultdict(list)
    for video, value in records:
        if math.isfinite(value):
            by_video[video].append(value)
    videos = sorted(by_video)
    sums = np.asarray([sum(by_video[video]) for video in videos], dtype=float)
    counts = np.asarray([len(by_video[video]) for video in videos], dtype=float)
    rng = np.random.default_rng(SEED + offset)
    draws = rng.integers(0, len(videos), size=(BOOTSTRAPS, len(videos)))
    sampled = np.sum(sums[draws], axis=1) / np.sum(counts[draws], axis=1)
    return {
        "mean": float(sums.sum() / counts.sum()),
        "ci_low": float(np.quantile(sampled, 0.025)),
        "ci_high": float(np.quantile(sampled, 0.975)),
        "events": int(counts.sum()),
        "videos": len(videos),
    }


def main() -> None:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    events = read_csv(EVENT_PATH)
    scores = read_csv(SCORE_PATH)
    controls = read_csv(CONTROL_PATH)
    candidates = {key: float(value) for key, value in result["candidates"].items()}
    checks: list[dict] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    protocol = HERE / result["protocol"]
    check("protocol exists", protocol.exists(), str(protocol))
    check(
        "protocol hash",
        sha256(protocol) == result["protocol_sha256"],
        f"calculated={sha256(protocol)} recorded={result['protocol_sha256']}",
    )
    check("figure exists", FIGURE_PATH.exists() and FIGURE_PATH.stat().st_size > 10_000, str(FIGURE_PATH))
    check("event count", len(events) == 91, f"events={len(events)}")
    split_counts = defaultdict(int)
    for row in events:
        split_counts[row["split"]] += 1
    check("calibration count", split_counts["calibration"] == 23, str(dict(split_counts)))
    check("evaluation count", split_counts["evaluation"] == 52, str(dict(split_counts)))
    check("holdout count", split_counts["holdout"] == 16, str(dict(split_counts)))

    max_coordinate_error = 0.0
    max_identity_error = 0.0
    min_magnitude = float("inf")
    by_source: dict[str, dict[tuple[int, int], dict[str, str]]] = {}
    for row in events:
        source_name = row["file"]
        if source_name not in by_source:
            source_rows = read_csv(SOURCE / source_name)
            by_source[source_name] = {
                (int(item["frame_number"]), int(item["ID"])): item for item in source_rows
            }
        index = by_source[source_name]
        frame = int(row["frame"])
        inherited = int(row["inherited_id"])
        joining = int(row["joining_id"])
        pre0 = index[(frame - 1, inherited)]
        pre1 = index[(frame, inherited)]
        post0 = index[(frame + 1, inherited)]
        post1 = index[(frame + 2, inherited)]
        join = index[(frame, joining)]

        def xy(item: dict[str, str]) -> np.ndarray:
            return np.asarray([float(item["cx_pos [m]"]), float(item["cy_pos [m]"])], dtype=float)

        v_pre = xy(pre1) - xy(pre0)
        v_post = xy(post1) - xy(post0)
        v_contact = xy(join) - xy(pre1)
        theta_pre = math.atan2(float(v_pre[1]), float(v_pre[0]))
        theta_post = math.atan2(float(v_post[1]), float(v_post[0]))
        theta_contact = math.atan2(float(v_contact[1]), float(v_contact[0]))
        sign = 1.0 if math.sin(theta_contact - theta_pre) > 0 else -1.0
        x_aa = oriented_coordinate(theta_pre, theta_post, sign)
        x_ab = oriented_coordinate(theta_pre, theta_contact, sign)
        x_ba = oriented_coordinate(theta_contact, theta_post, sign)
        max_coordinate_error = max(max_coordinate_error, d2(x_aa, float(row["x_AA"])))
        max_coordinate_error = max(max_coordinate_error, d2(x_ab, float(row["x_AB"])))
        max_coordinate_error = max(max_coordinate_error, d2(x_ba, float(row["x_BA"])))
        max_identity_error = max(max_identity_error, d2(x_aa, (x_ab + x_ba) % 2.0))
        min_magnitude = min(min_magnitude, float(np.linalg.norm(v_pre)), float(np.linalg.norm(v_post)))

    check("raw-coordinate reconstruction", max_coordinate_error < 1e-12, f"max={max_coordinate_error:.3e}")
    check("Information3 identity", max_identity_error < 1e-12, f"max={max_identity_error:.3e}")
    check("movement threshold", min_magnitude >= 0.0005 - 1e-15, f"min={min_magnitude:.12f}")

    expected_score_rows = len(events) * len(candidates)
    check("candidate score row count", len(scores) == expected_score_rows, f"rows={len(scores)}")
    max_loss_error = 0.0
    event_index = {
        (row["split"], row["video"], int(row["frame"]), int(row["inherited_id"])): row for row in events
    }
    for row in scores:
        event = event_index[(row["split"], row["video"], int(row["frame"]), int(row["inherited_id"]))]
        expected = d2(float(event["x_AA"]), candidates[row["candidate"]])
        max_loss_error = max(max_loss_error, abs(expected - float(row["loss"])))
    check("candidate loss formulas", max_loss_error < 1e-12, f"max={max_loss_error:.3e}")

    score_groups: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in scores:
        score_groups[(row["split"], row["candidate"])].append(float(row["loss"]))
    max_summary_error = 0.0
    for split in ("calibration", "evaluation", "holdout"):
        recomputed = {}
        for candidate in candidates:
            values = score_groups[(split, candidate)]
            recomputed[candidate] = statistics.mean(values)
            max_summary_error = max(
                max_summary_error,
                abs(recomputed[candidate] - result["candidate_summary"][split][candidate]["mean"]),
                abs(statistics.median(values) - result["candidate_summary"][split][candidate]["median"]),
            )
        winner = min(candidates, key=lambda name: recomputed[name])
        check(f"{split} winner", winner == result["candidate_summary"][split]["winner_mean"], f"winner={winner}")
    check("candidate summaries", max_summary_error < 1e-12, f"max={max_summary_error:.3e}")

    indexed_scores = {
        (row["split"], row["video"], int(row["frame"]), int(row["inherited_id"]), row["candidate"]): row
        for row in scores
    }
    max_comparison_error = 0.0
    for split_index, split in enumerate(("evaluation", "holdout")):
        phi_rows = [row for row in scores if row["split"] == split and row["candidate"] == "phi"]
        for candidate_index, candidate in enumerate(candidates):
            if candidate == "phi":
                continue
            differences = []
            for row in phi_rows:
                rival = indexed_scores[(split, row["video"], int(row["frame"]), int(row["inherited_id"]), candidate)]
                differences.append((row["video"], float(row["loss"]) - float(rival["loss"])))
            expected = cluster_bootstrap(differences, 100 + split_index * 20 + candidate_index)
            recorded = result["phi_candidate_comparisons"][split][candidate]
            for field in ("mean", "ci_low", "ci_high"):
                max_comparison_error = max(max_comparison_error, abs(expected[field] - recorded[field]))
    check("cluster comparison reproduction", max_comparison_error < 1e-12, f"max={max_comparison_error:.3e}")

    max_control_formula_error = 0.0
    for row in controls:
        real = float(row["phi_real"])
        for control, difference in (
            ("phi_broken", "real_minus_broken"),
            ("phi_contact_scramble", "real_minus_contact_scramble"),
            ("phi_preordinary", "real_minus_preordinary"),
        ):
            control_value = float(row[control])
            difference_value = float(row[difference])
            if math.isfinite(control_value):
                max_control_formula_error = max(max_control_formula_error, abs((real - control_value) - difference_value))
    check("control difference formulas", max_control_formula_error < 1e-12, f"max={max_control_formula_error:.3e}")

    check("verdict logic", result["verdict"].startswith("NOT SUPPORTED"), result["verdict"])
    check("Phi not evaluation winner", result["candidate_summary"]["evaluation"]["winner_mean"] != "phi", result["candidate_summary"]["evaluation"]["winner_mean"])
    check("Phi not holdout winner", result["candidate_summary"]["holdout"]["winner_mean"] != "phi", result["candidate_summary"]["holdout"]["winner_mean"])
    check("exact resolution failed", not result["resolution"]["one_step_exact_phi_resolution"], json.dumps(result["resolution"]))

    passed = sum(item["passed"] for item in checks)
    validation = {
        "test": "T329 independent validation",
        "run_date": "2026-08-02",
        "status": "PASS" if passed == len(checks) else "FAIL",
        "passed": passed,
        "total": len(checks),
        "checks": checks,
        "max_raw_coordinate_error": max_coordinate_error,
        "max_information3_identity_error": max_identity_error,
        "max_candidate_loss_error": max_loss_error,
        "max_candidate_summary_error": max_summary_error,
        "max_cluster_comparison_error": max_comparison_error,
        "max_control_formula_error": max_control_formula_error,
        "artifacts": {
            "result": str(RESULT_PATH),
            "events": str(EVENT_PATH),
            "scores": str(SCORE_PATH),
            "controls": str(CONTROL_PATH),
            "figure": str(FIGURE_PATH),
        },
    }
    VALIDATION_PATH.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps({"status": validation["status"], "passed": passed, "total": len(checks)}, indent=2))
    if validation["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

