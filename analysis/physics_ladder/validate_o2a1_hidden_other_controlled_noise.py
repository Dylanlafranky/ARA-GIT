#!/usr/bin/env python3
"""Independent validation of O2-A1 saved outputs and primary verdict."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from ara_hidden_other_residual_test import (
    simulate_classical,
    simulate_electromagnetic,
    simulate_quantum,
)


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "O2A1_HIDDEN_OTHER_CONTROLLED_NOISE_PROTOCOL_v1_FROZEN.md"
RECEIPT = HERE / "O2A1_HIDDEN_OTHER_CONTROLLED_NOISE_PROTOCOL_v1_FROZEN.sha256"
RESULTS = HERE / "O2A1_HIDDEN_OTHER_CONTROLLED_NOISE_RESULTS.json"
DEVELOPMENT = HERE / "O2A1_HIDDEN_OTHER_CONTROLLED_NOISE_DEVELOPMENT.csv"
TRIALS = HERE / "O2A1_HIDDEN_OTHER_CONTROLLED_NOISE_TRIALS.csv.gz"
AGGREGATES = HERE / "O2A1_HIDDEN_OTHER_CONTROLLED_NOISE_AGGREGATES.csv"
WAVEFORMS = HERE / "O2A1_HIDDEN_OTHER_CONTROLLED_NOISE_WAVEFORMS.csv"
OUTPUT = HERE / "O2A1_HIDDEN_OTHER_CONTROLLED_NOISE_VALIDATION.json"

EXPECTED_PROTOCOL_SHA256 = "d16485a828d4396e3ced05ce04fd7ca784a7e662fb9f6f46e078b83cb12add49"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path, compressed: bool = False) -> list[dict]:
    opener = gzip.open if compressed else open
    with opener(path, "rt" if compressed else "r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def to_float(row: dict, key: str) -> float:
    return float(row[key])


def direct_local_poly_clean_metrics(model: dict, fraction: float) -> dict:
    times = np.asarray(model["times"], dtype=float)
    stored = np.asarray(model["stored"], dtype=float)
    transfer = np.asarray(model["net_internal"], dtype=float)
    native = np.asarray(model["native_other"], dtype=float)
    sample_count = times.size
    window = max(5, int(round(sample_count * fraction)))
    if window % 2 == 0:
        window += 1
    if window > sample_count:
        window = sample_count if sample_count % 2 else sample_count - 1
    half = window // 2
    offsets = np.arange(-half, half + 1, dtype=float)
    design = np.column_stack([offsets**power for power in range(4)])
    step = float(times[1] - times[0])
    weights = np.linalg.pinv(design)[1] / step
    derivative = np.column_stack(
        [
            np.convolve(stored[:, channel], weights[::-1], mode="valid")
            for channel in range(stored.shape[1])
        ]
    )
    valid_times = times[half : sample_count - half]
    estimated = derivative - transfer[half : sample_count - half]
    native = native[half : sample_count - half]
    hidden = int(model["hidden_index"])
    native_hidden = native[:, hidden]
    estimated_hidden = estimated[:, hidden]
    peak = float(np.max(np.abs(native_hidden)))
    active = np.abs(native_hidden) >= 0.05 * peak
    integrated_abs = np.trapezoid(np.abs(estimated), valid_times, axis=0)
    inactive = [index for index in range(estimated.shape[1]) if index != hidden]
    return {
        "window_samples": window,
        "location_accuracy": float(int(np.argmax(integrated_abs)) == hidden),
        "sign_accuracy": float(
            np.mean(np.sign(estimated_hidden[active]) == np.sign(native_hidden[active]))
        ),
        "correlation": float(np.corrcoef(estimated_hidden, native_hidden)[0, 1]),
        "nrmse": float(
            np.sqrt(np.mean(np.square(estimated_hidden - native_hidden))) / peak
        ),
        "integrated_error": float(
            abs(
                np.trapezoid(estimated_hidden, valid_times)
                - np.trapezoid(native_hidden, valid_times)
            )
            / abs(np.trapezoid(native_hidden, valid_times))
        ),
        "inactive_rms_fraction": max(
            float(np.sqrt(np.mean(np.square(estimated[:, index]))) / peak)
            for index in inactive
        ),
    }


def main() -> None:
    checks: list[dict] = []

    protocol_hash = file_hash(PROTOCOL)
    receipt_hash = RECEIPT.read_text(encoding="utf-8").split()[0]
    checks.append(
        {
            "check": "frozen protocol hash",
            "passed": protocol_hash == EXPECTED_PROTOCOL_SHA256 == receipt_hash,
            "observed": protocol_hash,
        }
    )

    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    checks.append(
        {
            "check": "result embeds protocol hash",
            "passed": results["protocol_sha256"] == EXPECTED_PROTOCOL_SHA256,
            "observed": results["protocol_sha256"],
        }
    )

    development = read_csv(DEVELOPMENT)
    by_method: dict[str, list[dict]] = defaultdict(list)
    for row in development:
        by_method[row["method"]].append(row)
    for method, rows in by_method.items():
        selected = [row for row in rows if row["selected"] == "1"]
        minimum = min(float(row["selection_objective"]) for row in rows)
        checks.append(
            {
                "check": f"{method} development minimum selected",
                "passed": len(selected) == 1
                and abs(float(selected[0]["selection_objective"]) - minimum) < 1e-12
                and abs(
                    float(selected[0]["window_fraction"])
                    - float(results["selected_window_fractions"][method])
                )
                < 1e-12,
                "observed": selected,
            }
        )

    trials = read_csv(TRIALS, compressed=True)
    aggregates = read_csv(AGGREGATES)
    waveforms = read_csv(WAVEFORMS)
    checks.extend(
        [
            {
                "check": "trial row count",
                "passed": len(trials) == int(results["trial_rows"]),
                "observed": len(trials),
            },
            {
                "check": "aggregate row count",
                "passed": len(aggregates) == int(results["aggregate_rows"]),
                "observed": len(aggregates),
            },
            {
                "check": "bounded waveform row count",
                "passed": len(waveforms)
                == int(results["representative_waveform_rows"])
                == 362,
                "observed": len(waveforms),
            },
        ]
    )

    primary = [
        row
        for row in trials
        if row["suite"] == "additive"
        and row["model"]
        in ("Resistive capacitor coupling", "Open two-level probability")
        and row["corruption"] == "white"
        and row["injection_mode"] == "q_and_g"
        and row["level_value"] == "12"
        and row["method"] == "local_poly"
    ]
    raw = [
        row
        for row in trials
        if row["suite"] == "additive"
        and row["model"]
        in ("Resistive capacitor coupling", "Open two-level probability")
        and row["corruption"] == "white"
        and row["injection_mode"] == "q_and_g"
        and row["level_value"] == "12"
        and row["method"] == "raw_fd"
    ]
    recomputed_metrics = {
        "target_runs": len(primary),
        "location_accuracy": float(np.mean([to_float(row, "location_correct") for row in primary])),
        "median_sign_accuracy": float(
            np.median([to_float(row, "sign_accuracy") for row in primary])
        ),
        "median_correlation": float(
            np.median([to_float(row, "correlation") for row in primary])
        ),
        "median_nrmse": float(np.median([to_float(row, "nrmse") for row in primary])),
        "median_integrated_error": float(
            np.median([to_float(row, "integrated_error") for row in primary])
        ),
        "median_inactive_rms_fraction": float(
            np.median([to_float(row, "inactive_rms_fraction") for row in primary])
        ),
        "raw_fd_median_nrmse": float(
            np.median([to_float(row, "nrmse") for row in raw])
        ),
        "zero_other_median_nrmse": float(
            np.median([to_float(row, "zero_other_nrmse") for row in primary])
        ),
    }
    saved_metrics = results["primary_verdict"]["metrics"]
    metric_checks = {
        key: (
            int(value) == int(saved_metrics[key])
            if key == "target_runs"
            else abs(value - float(saved_metrics[key])) < 1e-12
        )
        for key, value in recomputed_metrics.items()
    }
    checks.append(
        {
            "check": "primary metrics independently recomputed from trial rows",
            "passed": all(metric_checks.values()),
            "observed": recomputed_metrics,
            "per_metric": metric_checks,
        }
    )

    thresholds = results["primary_verdict"]["thresholds"]
    recomputed_gates = {
        "location": recomputed_metrics["location_accuracy"]
        >= thresholds["location_accuracy_min"],
        "sign": recomputed_metrics["median_sign_accuracy"]
        >= thresholds["median_sign_accuracy_min"],
        "correlation": recomputed_metrics["median_correlation"]
        >= thresholds["median_correlation_min"],
        "nrmse": recomputed_metrics["median_nrmse"] <= thresholds["median_nrmse_max"],
        "integrated_error": recomputed_metrics["median_integrated_error"]
        <= thresholds["median_integrated_error_max"],
        "inactive_spill": recomputed_metrics["median_inactive_rms_fraction"]
        <= thresholds["median_inactive_rms_fraction_max"],
        "beats_raw_fd": recomputed_metrics["median_nrmse"]
        < recomputed_metrics["raw_fd_median_nrmse"],
        "beats_zero_other": recomputed_metrics["median_nrmse"]
        < recomputed_metrics["zero_other_median_nrmse"],
    }
    checks.append(
        {
            "check": "primary gates and verdict independently recomputed",
            "passed": recomputed_gates == results["primary_verdict"]["gates"]
            and results["primary_verdict"]["status"]
            == ("SUPPORTED" if all(recomputed_gates.values()) else "NOT SUPPORTED"),
            "observed": recomputed_gates,
        }
    )

    clean_aggregate = {
        row["model"]: row
        for row in aggregates
        if row["suite"] == "clean" and row["method"] == "local_poly"
    }
    models = [simulate_classical(), simulate_electromagnetic(), simulate_quantum()]
    direct_checks = []
    for model in models:
        fraction = float(results["selected_window_fractions"]["local_poly"])
        independent = direct_local_poly_clean_metrics(model, fraction)
        saved = clean_aggregate[model["model"]]
        comparisons = {
            "location_accuracy": abs(
                independent["location_accuracy"] - float(saved["location_accuracy"])
            )
            < 1e-12,
            "sign_accuracy": abs(
                independent["sign_accuracy"] - float(saved["median_sign_accuracy"])
            )
            < 1e-10,
            "correlation": abs(
                independent["correlation"] - float(saved["median_correlation"])
            )
            < 1e-10,
            "nrmse": abs(independent["nrmse"] - float(saved["median_nrmse"])) < 1e-10,
            "integrated_error": abs(
                independent["integrated_error"] - float(saved["median_integrated_error"])
            )
            < 1e-10,
            "inactive_rms_fraction": abs(
                independent["inactive_rms_fraction"]
                - float(saved["median_inactive_rms_fraction"])
            )
            < 1e-10,
        }
        direct_checks.append(
            {
                "model": model["model"],
                "passed": all(comparisons.values()),
                "comparisons": comparisons,
                "independent_metrics": independent,
            }
        )
    checks.append(
        {
            "check": "direct non-FFT clean local-polynomial reproduction",
            "passed": all(item["passed"] for item in direct_checks),
            "observed": direct_checks,
        }
    )

    primary_location_counts = Counter(row["predicted_location"] for row in primary)
    validation = {
        "status": "passed" if all(check["passed"] for check in checks) else "failed",
        "checks_passed": sum(int(check["passed"]) for check in checks),
        "checks_total": len(checks),
        "protocol_sha256": protocol_hash,
        "artifact_sha256": {
            path.name: file_hash(path)
            for path in (RESULTS, DEVELOPMENT, TRIALS, AGGREGATES, WAVEFORMS)
        },
        "primary_location_counts": dict(primary_location_counts),
        "checks": checks,
    }
    OUTPUT.write_text(
        json.dumps(validation, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, indent=2, ensure_ascii=False))
    if validation["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

