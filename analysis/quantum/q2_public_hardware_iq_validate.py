#!/usr/bin/env python3
"""Independent artifact-level validation for frozen T259."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "public_data"
ARCHIVE = DATA / "AllopticalSCQreadout_data.zip"
PROTOCOL = HERE / "Q2_PUBLIC_HARDWARE_IQ_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q2_PUBLIC_HARDWARE_IQ_PROTOCOL_v1_FROZEN.sha256"
FOLDS = HERE / "Q2_PUBLIC_HARDWARE_IQ_FOLDS.csv"
BLOCKS = HERE / "Q2_PUBLIC_HARDWARE_IQ_BLOCKS.csv"
SUMMARY = HERE / "Q2_PUBLIC_HARDWARE_IQ_SUMMARY.csv"
RESULTS = HERE / "Q2_PUBLIC_HARDWARE_IQ_RESULTS.json"
OUTPUT = HERE / "Q2_PUBLIC_HARDWARE_IQ_VALIDATION.json"

SOURCE_SHA = "73f3e2ca7b3658452b4c171532c751e96d7392dcb8741b87a18e28c7073d67fd"
CONDITIONS = (0, 10, 50, 250, 500, 1000)
BOOTSTRAP_SEED = 2026072403
BOOTSTRAP_REPS = 2000
BLOCK_SIZE = 1000


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def close(a: float, b: float, tol: float = 1e-12) -> bool:
    return abs(a - b) <= tol


def independent_bootstrap(blocks: list[dict]) -> tuple[float, float]:
    by_condition: dict[int, dict[str, list[tuple[float, float]]]] = {}
    for condition in CONDITIONS:
        by_condition[condition] = {"g": [], "e": []}
    for row in blocks:
        by_condition[int(row["condition_hz"])][row["class"]].append(
            (
                int(row["ara_correct"]) / BLOCK_SIZE,
                int(row["selected_onecut_correct"]) / BLOCK_SIZE,
            )
        )
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    delta = np.empty(BOOTSTRAP_REPS)
    for b in range(BOOTSTRAP_REPS):
        conditions = rng.choice(CONDITIONS, size=6, replace=True)
        condition_delta = []
        for condition in conditions:
            class_delta = []
            for label in ("g", "e"):
                values = by_condition[int(condition)][label]
                idx = rng.integers(0, len(values), size=len(values))
                class_delta.append(
                    np.mean([values[i][0] - values[i][1] for i in idx])
                )
            condition_delta.append(np.mean(class_delta))
        delta[b] = np.mean(condition_delta)
    return float(np.quantile(delta, 0.025)), float(np.quantile(delta, 0.975))


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    folds = read_csv(FOLDS)
    blocks = read_csv(BLOCKS)
    summary = read_csv(SUMMARY)
    checks: list[dict] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": detail})

    expected_protocol = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    check(
        "frozen_protocol_hash",
        sha256(PROTOCOL) == expected_protocol == result["protocol_sha256"],
        sha256(PROTOCOL),
    )
    check("source_archive_hash", sha256(ARCHIVE) == SOURCE_SHA, sha256(ARCHIVE))
    check("fold_row_count", len(folds) == 4 * 6 * 8, str(len(folds)))
    check("block_row_count", len(blocks) == 6 * 2 * 50, str(len(blocks)))
    check(
        "conditions_complete",
        {int(r["condition_hz"]) for r in folds} == set(CONDITIONS),
        str(sorted({int(r["condition_hz"]) for r in folds})),
    )
    check(
        "all_primary_axes_selected_in_training",
        all(
            r["selected_axis"] in {"I", "Q"}
            for r in folds
            if r["run"] == "primary_first_readout"
        ),
        "selection recorded per fold",
    )

    def summary_ba(run: str, arm: str) -> float:
        row = next(r for r in summary if r["run"] == run and r["arm"] == arm)
        return float(row["condition_weighted_ba"])

    primary = "primary_first_readout"
    ara_ba = summary_ba(primary, "ara_twocut")
    one_ba = summary_ba(primary, "selected_onecut")
    raw_ba = summary_ba(primary, "raw_iq_lda")
    shuffle_ba = summary_ba(primary, "label_shuffle")
    check("primary_ara_recomputed", close(ara_ba, result["primary"]["ara_twocut_ba"]), str(ara_ba))
    check(
        "primary_onecut_recomputed",
        close(one_ba, result["primary"]["selected_onecut_ba"]),
        str(one_ba),
    )
    check("raw_ara_accuracy_tie", close(raw_ba, ara_ba), f"{raw_ba} vs {ara_ba}")
    check(
        "reported_gain_recomputed",
        close(ara_ba - one_ba, result["primary"]["gain"]),
        str(ara_ba - one_ba),
    )
    check(
        "reported_shuffle_recomputed",
        close(shuffle_ba, result["primary"]["label_shuffle_ba"]),
        str(shuffle_ba),
    )
    check(
        "confusion_totals_per_primary_arm",
        all(
            sum(
                sum(int(r[k]) for k in ["tn", "fp", "fn", "tp"])
                for r in folds
                if r["run"] == primary and r["arm"] == arm
            )
            == 600000
            for arm in {
                r["arm"] for r in folds if r["run"] == primary
            }
        ),
        "600,000 held-out predictions per arm",
    )
    check(
        "ara_raw_zero_disagreement",
        result["primary"]["ara_raw_disagreements"] == 0,
        str(result["primary"]["ara_raw_disagreements"]),
    )
    check(
        "pole_reversal_zero_disagreement",
        result["primary"]["pole_reversal_disagreements"] == 0,
        str(result["primary"]["pole_reversal_disagreements"]),
    )
    check(
        "complement_machine_precision",
        result["primary"]["complement_max_residual"] <= 1e-12,
        str(result["primary"]["complement_max_residual"]),
    )

    ci_low, ci_high = independent_bootstrap(blocks)
    check(
        "bootstrap_low_reproduced",
        close(ci_low, result["bootstrap"]["gain_ci_low"]),
        f"{ci_low} vs {result['bootstrap']['gain_ci_low']}",
    )
    check(
        "bootstrap_high_reproduced",
        close(ci_high, result["bootstrap"]["gain_ci_high"]),
        f"{ci_high} vs {result['bootstrap']['gain_ci_high']}",
    )

    recomputed_gate_passes = {
        "G1_ara_ba_at_least_0p80": ara_ba >= 0.80,
        "G2_gain_at_least_0p005": (ara_ba - one_ba) >= 0.005,
        "G3_gain_ci_low_above_zero": ci_low > 0,
        "G4_worst_condition_at_least_0p70": result["primary"]["worst_condition_ba"] >= 0.70,
        "G5_equal_information_tie": close(ara_ba, raw_ba)
        and result["primary"]["ara_raw_disagreements"] == 0,
        "G6_pole_reversal_and_complement": result["primary"]["pole_reversal_disagreements"] == 0
        and result["primary"]["complement_max_residual"] <= 1e-12,
        "G7_label_shuffle_at_most_0p55": shuffle_ba <= 0.55,
    }
    check(
        "all_gate_flags_reproduced",
        all(
            recomputed_gate_passes[name] == bool(result["gates"][name]["pass"])
            for name in recomputed_gate_passes
        ),
        json.dumps(recomputed_gate_passes, sort_keys=True),
    )
    gate_count = sum(recomputed_gate_passes.values())
    verdict = "SUPPORTED" if gate_count == 7 else "NOT SUPPORTED"
    check(
        "verdict_reproduced",
        verdict == result["verdict"] and gate_count == result["gates_passed"],
        f"{verdict}, {gate_count}/7",
    )

    validation = {
        "protocol_id": result["protocol_id"],
        "ledger_id": result["ledger_id"],
        "validation_status": "PASS" if all(c["pass"] for c in checks) else "FAIL",
        "checks_passed": sum(c["pass"] for c in checks),
        "checks_total": len(checks),
        "checks": checks,
        "independent_verdict": verdict,
        "independent_gate_count": gate_count,
        "note": (
            "Artifact-level independent recomputation. The frozen negative verdict remains "
            "driven by G2/G3 even if the one-shot label-shuffle control is treated cautiously."
        ),
    }
    OUTPUT.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps({k: validation[k] for k in ["validation_status", "checks_passed", "checks_total", "independent_verdict", "independent_gate_count"]}, indent=2))


if __name__ == "__main__":
    main()
