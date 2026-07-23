#!/usr/bin/env python3
"""Independent bounded-output audit for the hidden-Other residual test.

This validator does not call the simulation or recovery implementation.  It
checks the frozen protocol hash, the complete summary, and recomputes the
location/sign/waveform/parent-closure diagnostics from the bounded CSV sample.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT / "HIDDEN_OTHER_RESIDUAL_PROTOCOL_2026-07-23.md"
RESULTS = ROOT / "ARA_HIDDEN_OTHER_RESIDUAL_RESULTS.json"
SUMMARY = ROOT / "ARA_HIDDEN_OTHER_RESIDUAL_SUMMARY.csv"
SAMPLE = ROOT / "ARA_HIDDEN_OTHER_RESIDUAL_BOUNDED_SAMPLE.csv"
OUTPUT = ROOT / "ARA_HIDDEN_OTHER_RESIDUAL_VALIDATION.json"

EXPECTED_MODELS = {
    "Damped coupled oscillators": "oscillator 2",
    "Resistive capacitor coupling": "coupling relation",
    "Open two-level probability": "quantum state 2",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def correlation(xs: list[float], ys: list[float]) -> float:
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    den = math.sqrt(sum(x * x for x in dx) * sum(y * y for y in dy))
    return sum(x * y for x, y in zip(dx, dy)) / den if den else 1.0


def main() -> None:
    errors: list[str] = []
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    protocol_hash = sha256(PROTOCOL)

    if result.get("protocol_sha256") != protocol_hash:
        errors.append("Protocol hash differs from the hash recorded by the primary run.")
    if result.get("status") != "passed":
        errors.append("Primary result did not report passed status.")
    if result.get("models_passed") != 3 or result.get("models_total") != 3:
        errors.append("Primary result did not contain three passing systems.")

    with SUMMARY.open(newline="", encoding="utf-8") as handle:
        summary_rows = list(csv.DictReader(handle))
    if {row["model"] for row in summary_rows} != set(EXPECTED_MODELS):
        errors.append("Summary model set is incomplete or unexpected.")

    threshold_audit = []
    for row in summary_rows:
        passed = (
            row["native_hidden_location"] == EXPECTED_MODELS[row["model"]]
            and row["predicted_hidden_location"] == EXPECTED_MODELS[row["model"]]
            and float(row["sign_accuracy"]) >= 0.999
            and float(row["source_correlation"]) >= 0.999
            and float(row["source_nrmse"]) <= 0.001
            and float(row["integrated_relative_error"]) <= 0.001
            and float(row["inactive_rms_fraction"]) <= 0.001
            and row["beats_all_controls"].lower() == "true"
            and row["passed"].lower() == "true"
        )
        if not passed:
            errors.append(f"Frozen threshold audit failed for {row['model']}.")
        threshold_audit.append({"model": row["model"], "passed": passed})

    with SAMPLE.open(newline="", encoding="utf-8") as handle:
        sample_rows = list(csv.DictReader(handle))

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in sample_rows:
        grouped[row["model"]].append(row)

    bounded_audit = []
    for model, expected_location in EXPECTED_MODELS.items():
        rows = grouped.get(model, [])
        if not rows:
            errors.append(f"No bounded sample rows for {model}.")
            continue

        integrated_abs: dict[str, float] = defaultdict(float)
        by_time: dict[float, list[dict[str, str]]] = defaultdict(list)
        for row in rows:
            integrated_abs[row["identity"]] += abs(float(row["estimated_other"]))
            by_time[float(row["time"])].append(row)
        predicted_location = max(integrated_abs, key=integrated_abs.get)

        hidden_rows = [row for row in rows if row["identity"] == expected_location]
        est = [float(row["estimated_other"]) for row in hidden_rows]
        native = [float(row["native_other_revealed"]) for row in hidden_rows]
        peak = max(abs(value) for value in native)
        active = [i for i, value in enumerate(native) if abs(value) >= 1e-6 * peak]
        sign_accuracy = (
            sum(
                1
                for i in active
                if math.copysign(1.0, est[i]) == math.copysign(1.0, native[i])
            )
            / len(active)
        )
        corr = correlation(est, native)
        nrmse = math.sqrt(
            sum((a - b) ** 2 for a, b in zip(est, native)) / len(est)
        ) / peak

        inactive = [
            float(row["estimated_other"])
            for row in rows
            if row["identity"] != expected_location
        ]
        inactive_rms_fraction = math.sqrt(
            sum(value * value for value in inactive) / len(inactive)
        ) / peak

        parent_errors = []
        for time_rows in by_time.values():
            parent_errors.append(
                abs(
                    sum(float(row["estimated_other"]) for row in time_rows)
                    - sum(float(row["native_other_revealed"]) for row in time_rows)
                )
            )
        parent_nmae = sum(parent_errors) / len(parent_errors) / peak

        passed = (
            predicted_location == expected_location
            and sign_accuracy >= 0.999
            and corr >= 0.999
            and nrmse <= 1e-6
            and inactive_rms_fraction <= 1e-6
            and parent_nmae <= 1e-6
        )
        if not passed:
            errors.append(f"Independent bounded-sample audit failed for {model}.")
        bounded_audit.append(
            {
                "model": model,
                "expected_location": expected_location,
                "predicted_location": predicted_location,
                "sign_accuracy": sign_accuracy,
                "source_correlation": corr,
                "source_nrmse": nrmse,
                "inactive_rms_fraction": inactive_rms_fraction,
                "parent_total_nmae": parent_nmae,
                "passed": passed,
            }
        )

    validation = {
        "status": "passed" if not errors else "failed",
        "validation_scope": (
            "Independent audit of frozen thresholds, file integrity and bounded-output "
            "location/sign/waveform/parent-closure calculations. The validator does not "
            "reuse the simulation or recovery functions."
        ),
        "protocol_sha256": protocol_hash,
        "results_sha256": sha256(RESULTS),
        "summary_sha256": sha256(SUMMARY),
        "bounded_sample_sha256": sha256(SAMPLE),
        "summary_threshold_audit": threshold_audit,
        "bounded_sample_audit": bounded_audit,
        "errors": errors,
    }
    OUTPUT.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
