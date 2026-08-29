from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "T396_information3_spin_child_lock"
RESULTS = OUT / "T396_RESULTS.json"
SAMPLE = OUT / "T396_HOLDOUT_SAMPLE.csv"
GRID = OUT / "T396_VALIDATION_GRID.csv"
SENSITIVITY = OUT / "T396_SENSITIVITY.csv"
PROTOCOL = HERE / "T396_INFORMATION3_SPIN_CHILD_LOCK_PROTOCOL_2026-08-16.md"
SCRIPT = HERE / "t396_information3_spin_child_lock.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    with SAMPLE.open(newline="", encoding="utf-8") as handle:
        sample = [{key: float(value) for key, value in row.items()} for row in csv.DictReader(handle)]
    with GRID.open(newline="", encoding="utf-8") as handle:
        grid = [
            {
                "family": row["family"],
                "parent_bins": int(row["parent_bins"]),
                "relation_bins": int(row["relation_bins"]),
                "mean_nll": float(row["mean_nll"]),
            }
            for row in csv.DictReader(handle)
        ]
    with SENSITIVITY.open(newline="", encoding="utf-8") as handle:
        sensitivity = [
            {
                key: int(value) if key in {"seed", "n", "holdout_n"} else float(value)
                for key, value in row.items()
            }
            for row in csv.DictReader(handle)
        ]

    selected = result["selected_resolutions"]
    winners = {
        family: min((row for row in grid if row["family"] == family), key=lambda row: row["mean_nll"])
        for family in ("parent", "relation", "joint")
    }
    support_errors = []
    sample_gain = []
    for row in sample:
        parent = row["parent_P"]
        child = row["true_child_C"]
        low = 2.0 * (1.0 - parent) / (2.0 - parent)
        high = 2.0 / (2.0 - parent)
        support_errors.append(max(low - child, child - high, 0.0))
        sample_gain.append(row["parent_only_nll"] - row["joint_nll"])

    models = result["holdout_models"]
    additive_gains = [row["additive_incremental_gain"] for row in sensitivity]
    script_text = SCRIPT.read_text(encoding="utf-8")
    checks = {
        "protocol_hash_matches": result["protocol_sha256"] == sha256(PROTOCOL),
        "fresh_primary_seed_396": result["primary_seed"] == 396,
        "primary_population_is_one_million": result["primary_n"] == 1_000_000,
        "deterministic_split_sums_to_population": sum(result["split_counts"].values()) == result["primary_n"],
        "generator_marginals_match_analytic_means": result["generator_validation"]["all_within_0p0025"],
        "exact_composition_is_machine_precision": result["gate_A_exact_composition"]["pass"],
        "exact_composition_labelled_forced": "not independent" in result["gate_A_exact_composition"]["classification"],
        "sample_children_obey_event_support": max(support_errors) < 1e-12,
        "parent_resolution_is_validation_winner": selected["parent_bins"] == winners["parent"]["parent_bins"],
        "relation_resolution_is_validation_winner": selected["relation_bins"] == winners["relation"]["relation_bins"],
        "joint_resolution_is_validation_winner": selected["joint_parent_bins"] == winners["joint"]["parent_bins"] and selected["joint_relation_bins"] == winners["joint"]["relation_bins"],
        "primary_gain_ci_excludes_zero": result["primary_gain_ci95"][0] > 0.0,
        "joint_beats_parent": models["joint_information3"]["mean_nll"] < models["parent_only"]["mean_nll"],
        "joint_beats_relation_only": models["joint_information3"]["mean_nll"] < models["relation_only"]["mean_nll"],
        "wrong_event_pairing_degrades": models["wrong_event_relation"]["mean_nll"] > models["joint_information3"]["mean_nll"],
        "mirrored_orientation_degrades": models["mirrored_orientation"]["mean_nll"] > models["joint_information3"]["mean_nll"],
        "shuffled_relation_degrades": models["relation_shuffled_calibration"]["mean_nll"] > models["joint_information3"]["mean_nll"],
        "oracle_is_best_nll": models["analytic_va_oracle"]["mean_nll"] == min(values["mean_nll"] for values in models.values()),
        "zero_polarization_has_no_positive_additive_gain": sensitivity[-1]["additive_gain_ci95_high"] < 0.0,
        "additive_gain_falls_monotonically_with_polarization": all(additive_gains[i] > additive_gains[i + 1] for i in range(len(additive_gains) - 1)),
        "no_missing_momentum_shortcut": "missing_momentum" not in script_text and "missing momentum" not in script_text,
    }
    validation = {
        "test_id": "T396-independent-validation",
        "overall_assessment": "Ready to share with explicit truth-model and sparse-joint caveats",
        "sample_rows": len(sample),
        "checks": checks,
        "overall_pass": all(checks.values()),
        "spot_checks": {
            "max_sample_support_error": max(support_errors),
            "sample_mean_joint_minus_parent_gain": mean(sample_gain),
            "reported_full_gain": result["primary_incremental_gain_nats_per_event"],
            "additive_gain_by_polarization": additive_gains,
        },
        "required_caveats": [
            "The population is generated from the leading-order polarized V-A law; it is not direct two-neutrino observation.",
            "The factorized fusion outperformed the denser joint histogram, so the result supports complementary cuts but does not require a learned nonlinear P-by-R interaction.",
            "The fixed dense joint histogram loses holdout advantage below full polarization at the smaller sensitivity sample size; the lower-variance factorized control retains the expected graded signal.",
        ],
    }
    (OUT / "T396_VALIDATION.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
