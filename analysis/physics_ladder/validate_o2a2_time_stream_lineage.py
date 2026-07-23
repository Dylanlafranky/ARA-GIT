#!/usr/bin/env python3
"""Independent checks for the frozen O2-A2 downstream time-stream test."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

import o2a2_time_stream_lineage as runner
from ara_hidden_other_residual_test import simulate_electromagnetic


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "O2A2_TIME_STREAM_LINEAGE_RESULTS.json"
TRIALS = HERE / "O2A2_TIME_STREAM_LINEAGE_TRIALS.csv"
AGGREGATES = HERE / "O2A2_TIME_STREAM_LINEAGE_AGGREGATES.csv"
DEVELOPMENT = HERE / "O2A2_TIME_STREAM_LINEAGE_DEVELOPMENT.csv"
WAVEFORMS = HERE / "O2A2_TIME_STREAM_LINEAGE_WAVEFORMS.csv"
RECEIPT = HERE / "O2A2_TIME_STREAM_LINEAGE_VALIDATION.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def close(left: float, right: float, tolerance: float = 1e-12) -> bool:
    return bool(np.isclose(left, right, atol=tolerance, rtol=tolerance))


def median(rows: list[dict], method: str, field: str) -> float:
    values = [float(row[field]) for row in rows if row["method"] == method]
    if not values:
        raise RuntimeError(f"Missing {method}/{field}")
    return float(np.median(values))


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    trials = read_csv(TRIALS)
    aggregates = read_csv(AGGREGATES)
    development = read_csv(DEVELOPMENT)
    waveforms = read_csv(WAVEFORMS)
    checks: list[dict] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    protocol_hash = sha256(runner.PROTOCOL)
    fidelity_hash = sha256(runner.FIDELITY)
    check(
        "protocol_hash",
        protocol_hash == runner.EXPECTED_PROTOCOL_SHA256 == result["protocol_sha256"],
        protocol_hash,
    )
    check(
        "fidelity_hash",
        fidelity_hash == runner.EXPECTED_FIDELITY_SHA256 == result["fidelity_sha256"],
        fidelity_hash,
    )
    check(
        "artifact_row_counts",
        len(trials) == result["trial_rows"] == 2016
        and len(aggregates) == result["aggregate_rows"] == 126
        and len(waveforms) == result["waveform_rows"] == 549,
        f"trials={len(trials)}, aggregates={len(aggregates)}, waveforms={len(waveforms)}",
    )

    selected_rows = [row for row in development if row["selected"] == "1"]
    minimum = min(
        development,
        key=lambda row: (
            float(row["selection_objective"]),
            float(row["derivative_fraction"]),
            float(row["half_life_fraction"]),
        ),
    )
    selected = result["selected_settings"]
    check(
        "development_selection",
        len(selected_rows) == 1
        and selected_rows[0] == minimum
        and close(float(minimum["derivative_fraction"]), selected["derivative_fraction"])
        and close(float(minimum["half_life_fraction"]), selected["half_life_fraction"]),
        (
            f"selected derivative={selected['derivative_fraction']}, "
            f"half-life={selected['half_life_fraction']}, "
            f"objective={minimum['selection_objective']}"
        ),
    )

    primary = [
        row
        for row in trials
        if int(float(row["snr_db"])) == 12
        and row["model"]
        in ("Resistive capacitor coupling", "Open two-level probability")
    ]
    method_counts = {
        method: sum(row["method"] == method for row in primary) for method in runner.METHODS
    }
    check(
        "primary_method_counts",
        all(count == 32 for count in method_counts.values()),
        json.dumps(method_counts, sort_keys=True),
    )

    metrics = {
        "median_fixed_correlation": median(
            primary, "fixed_time_lineage", "correlation"
        ),
        "median_fixed_nrmse": median(primary, "fixed_time_lineage", "nrmse"),
        "median_fixed_sign_accuracy": median(
            primary, "fixed_time_lineage", "sign_accuracy"
        ),
        "median_fixed_integrated_error": median(
            primary, "fixed_time_lineage", "integrated_error"
        ),
        "median_reselection_correlation": median(
            primary, "repeated_parent_reselection", "correlation"
        ),
        "median_reselection_nrmse": median(
            primary, "repeated_parent_reselection", "nrmse"
        ),
        "median_zero_other_nrmse": median(primary, "zero_other", "nrmse"),
    }
    metrics["correlation_advantage"] = (
        metrics["median_fixed_correlation"]
        - metrics["median_reselection_correlation"]
    )
    metrics["nrmse_relative_improvement"] = (
        1.0
        - metrics["median_fixed_nrmse"] / metrics["median_reselection_nrmse"]
    )
    saved_metrics = result["primary_verdict"]["metrics"]
    check(
        "independent_primary_metrics",
        all(close(value, float(saved_metrics[name])) for name, value in metrics.items()),
        json.dumps(metrics, sort_keys=True),
    )

    system_nrmse = {}
    for model in ("Resistive capacitor coupling", "Open two-level probability"):
        subset = [row for row in primary if row["model"] == model]
        system_nrmse[model] = {
            "fixed": median(subset, "fixed_time_lineage", "nrmse"),
            "reselection": median(
                subset, "repeated_parent_reselection", "nrmse"
            ),
        }
    check(
        "independent_system_comparison",
        all(
            close(
                system_nrmse[model][method],
                float(saved_metrics["system_nrmse"][model][method]),
            )
            for model in system_nrmse
            for method in system_nrmse[model]
        ),
        json.dumps(system_nrmse, sort_keys=True),
    )

    thresholds = result["primary_verdict"]["thresholds"]
    gates = {
        "correlation": metrics["median_fixed_correlation"]
        >= thresholds["correlation_min"],
        "nrmse": metrics["median_fixed_nrmse"] <= thresholds["nrmse_max"],
        "sign": metrics["median_fixed_sign_accuracy"]
        >= thresholds["sign_accuracy_min"],
        "integrated_error": metrics["median_fixed_integrated_error"]
        <= thresholds["integrated_error_max"],
        "correlation_advantage": metrics["correlation_advantage"]
        >= thresholds["correlation_advantage_min"],
        "nrmse_relative_improvement": metrics["nrmse_relative_improvement"]
        >= thresholds["nrmse_relative_improvement_min"],
        "beats_zero_other": metrics["median_fixed_nrmse"]
        < metrics["median_zero_other_nrmse"],
        "beats_reselection_in_both_systems": all(
            values["fixed"] < values["reselection"] for values in system_nrmse.values()
        ),
    }
    check(
        "independent_gates",
        gates == result["primary_verdict"]["gates"]
        and sum(gates.values()) == result["primary_verdict"]["passed_gates"] == 6,
        json.dumps(gates, sort_keys=True),
    )
    check(
        "independent_status",
        result["primary_verdict"]["status"] == "NOT SUPPORTED",
        result["primary_verdict"]["status"],
    )

    # Direct deterministic reproduction of one untouched target run.
    model = simulate_electromagnetic()
    q, g = runner.noisy_observations(
        model, snr_db=12, replicates=runner.TARGET_REPLICATES, seed_label="fresh_target"
    )
    methods, selected_channels, times, truth, _ = runner.construct_causal_methods(
        model,
        q,
        g,
        selected["derivative_fraction"],
        selected["half_life_fraction"],
    )
    direct_score = runner.score_series(methods["fixed_time_lineage"][0], truth, times)
    saved_row = next(
        row
        for row in primary
        if row["model"] == model["model"]
        and row["method"] == "fixed_time_lineage"
        and int(row["replicate"]) == 0
    )
    check(
        "direct_representative_reproduction",
        all(close(value, float(saved_row[name])) for name, value in direct_score.items()),
        json.dumps(direct_score, sort_keys=True),
    )

    reselect_row = next(
        row
        for row in primary
        if row["model"] == model["model"]
        and row["method"] == "repeated_parent_reselection"
        and int(row["replicate"]) == 0
    )
    occupancy = float(np.mean(selected_channels[0] == model["hidden_index"]))
    switches = int(
        np.sum(selected_channels[0, 1:] != selected_channels[0, :-1])
    )
    check(
        "direct_reselection_path",
        close(occupancy, float(reselect_row["declared_child_occupancy"]))
        and switches == int(reselect_row["switch_count"]),
        f"occupancy={occupancy}, switches={switches}",
    )

    # Aggregate spot check from independently filtered trial rows.
    aggregate_row = next(
        row
        for row in aggregates
        if row["model"] == model["model"]
        and int(float(row["snr_db"])) == 12
        and row["method"] == "fixed_time_lineage"
    )
    target_subset = [
        row
        for row in trials
        if row["model"] == model["model"]
        and int(float(row["snr_db"])) == 12
        and row["method"] == "fixed_time_lineage"
    ]
    aggregate_median = float(np.median([float(row["nrmse"]) for row in target_subset]))
    check(
        "aggregate_spot_check",
        close(aggregate_median, float(aggregate_row["median_nrmse"])),
        f"median_nrmse={aggregate_median}",
    )

    paired_descriptive = {}
    for model_name in (
        "pooled",
        "Resistive capacitor coupling",
        "Open two-level probability",
    ):
        subset = primary if model_name == "pooled" else [
            row for row in primary if row["model"] == model_name
        ]
        keyed = {
            (row["method"], int(row["replicate"]), row["model"]): row for row in subset
        }
        identities = sorted(
            {(int(row["replicate"]), row["model"]) for row in subset}
        )
        correlation_gains = []
        nrmse_reductions = []
        for replicate, model in identities:
            fixed = keyed[("fixed_time_lineage", replicate, model)]
            reselected = keyed[("repeated_parent_reselection", replicate, model)]
            correlation_gains.append(
                float(fixed["correlation"]) - float(reselected["correlation"])
            )
            nrmse_reductions.append(
                float(reselected["nrmse"]) - float(fixed["nrmse"])
            )
        correlation_gains = np.asarray(correlation_gains)
        nrmse_reductions = np.asarray(nrmse_reductions)
        rng = np.random.default_rng(20260723)
        bootstrap = np.empty((20_000, 2))
        for index in range(bootstrap.shape[0]):
            selected_indices = rng.integers(0, len(identities), len(identities))
            bootstrap[index] = (
                np.median(correlation_gains[selected_indices]),
                np.median(nrmse_reductions[selected_indices]),
            )
        paired_descriptive[model_name] = {
            "n": len(identities),
            "median_paired_correlation_gain": float(np.median(correlation_gains)),
            "correlation_gain_90_bootstrap_interval": [
                float(value) for value in np.quantile(bootstrap[:, 0], (0.05, 0.95))
            ],
            "correlation_win_rate": float(np.mean(correlation_gains > 0)),
            "median_paired_nrmse_reduction": float(np.median(nrmse_reductions)),
            "nrmse_reduction_90_bootstrap_interval": [
                float(value) for value in np.quantile(bootstrap[:, 1], (0.05, 0.95))
            ],
            "nrmse_win_rate": float(np.mean(nrmse_reductions > 0)),
        }

    passed = sum(int(item["passed"]) for item in checks)
    output = {
        "test": result["test"],
        "validated_at": "2026-07-23",
        "checks_passed": passed,
        "checks_total": len(checks),
        "all_passed": passed == len(checks),
        "checks": checks,
        "post_hoc_paired_descriptive": paired_descriptive,
        "artifact_sha256": {
            "results": sha256(RESULTS),
            "trials": sha256(TRIALS),
            "aggregates": sha256(AGGREGATES),
            "development": sha256(DEVELOPMENT),
            "waveforms": sha256(WAVEFORMS),
        },
    }
    RECEIPT.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))
    if not output["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
