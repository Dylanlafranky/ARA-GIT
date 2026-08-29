from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "T395_information3_parent_child_lock"
RESULTS = OUT / "T395_RESULTS.json"
SAMPLE = OUT / "T395_HOLDOUT_SAMPLE.csv"
GRID = OUT / "T395_VALIDATION_GRID.csv"
PROTOCOL = HERE / "T395_INFORMATION3_PARENT_CHILD_LOCK_PROTOCOL_2026-08-15.md"
SCRIPT = HERE / "t395_information3_parent_child_lock.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    with SAMPLE.open(newline="", encoding="utf-8") as handle:
        rows = [
            {key: float(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]
    with GRID.open(newline="", encoding="utf-8") as handle:
        grid = [
            {
                "parent_bins": int(row["parent_bins"]),
                "mean_nll": float(row["mean_nll"]),
            }
            for row in csv.DictReader(handle)
        ]

    parent_closure = []
    child_coordinate_error = []
    predicted_nue_composition_error = []
    predicted_anumu_composition_error = []
    child_abs_error = []
    nue_abs_error = []
    anumu_abs_error = []
    for row in rows:
        parent = row["parent_x_e"]
        neutral = 2.0 - parent
        true_nue = row["true_x_nu_e"]
        true_anumu = row["true_x_anti_nu_mu"]
        true_child = row["true_child_y_nu_e"]
        predicted_child = row["predicted_child_y_nu_e"]
        predicted_nue = row["predicted_x_nu_e"]
        predicted_anumu = row["predicted_x_anti_nu_mu"]
        parent_closure.append(abs(parent + true_nue + true_anumu - 2.0))
        child_coordinate_error.append(abs(true_child - 2.0 * true_nue / neutral))
        predicted_nue_composition_error.append(
            abs(predicted_nue - neutral * predicted_child / 2.0)
        )
        predicted_anumu_composition_error.append(
            abs(predicted_anumu - neutral * (2.0 - predicted_child) / 2.0)
        )
        child_abs_error.append(abs(predicted_child - true_child))
        nue_abs_error.append(abs(predicted_nue - true_nue))
        anumu_abs_error.append(abs(predicted_anumu - true_anumu))

    selected = result["selected_parent_bins"]
    grid_winner = min(grid, key=lambda row: row["mean_nll"])["parent_bins"]
    models = result["holdout_models"]
    source_text = SCRIPT.read_text(encoding="utf-8")
    checks = {
        "protocol_hash_matches": result["protocol_sha256"] == sha256(PROTOCOL),
        "exact_gate_passes": result["gate_A_exact_composition"]["pass"],
        "exact_gate_is_labelled_forced": "not independent" in result["gate_A_exact_composition"]["classification"],
        "sample_parent_closure_max_lt_1e_12": max(parent_closure) < 1e-12,
        "sample_child_coordinate_max_error_lt_1e_12": max(child_coordinate_error) < 1e-12,
        "sample_prediction_composition_max_error_lt_1e_12": max(
            predicted_nue_composition_error + predicted_anumu_composition_error
        ) < 1e-12,
        "validation_selected_actual_nll_winner": selected == grid_winner,
        "primary_gain_ci_excludes_zero": result["primary_gain_ci95"][0] > 0.0,
        "conditional_beats_unconditional_nll": models["conditional_information_lock"]["mean_nll"] < models["unconditional_child"]["mean_nll"],
        "conditional_beats_parent_shuffle_nll": models["conditional_information_lock"]["mean_nll"] < models["parent_shuffled"]["mean_nll"],
        "conditional_beats_phase_space_nll": models["conditional_information_lock"]["mean_nll"] < models["phase_space"]["mean_nll"],
        "no_superk_population_time_join_in_t395": "load_superk" not in source_text and "decayes_and_neutrons" not in source_text,
    }

    validation = {
        "test_id": "T395-independent-validation",
        "sample_rows": len(rows),
        "checks": checks,
        "sample_spot_checks": {
            "max_parent_closure_error": max(parent_closure),
            "max_child_coordinate_error": max(child_coordinate_error),
            "max_prediction_composition_error": max(
                predicted_nue_composition_error + predicted_anumu_composition_error
            ),
            "sample_child_mae": mean(child_abs_error),
            "reported_full_child_mae": models["conditional_information_lock"]["child_mae"],
            "sample_nu_e_absolute_mae": mean(nue_abs_error),
            "reported_full_nu_e_absolute_mae": models["conditional_information_lock"]["nu_e_absolute_mae"],
            "sample_anti_nu_mu_absolute_mae": mean(anumu_abs_error),
            "reported_full_anti_nu_mu_absolute_mae": models["conditional_information_lock"]["anti_nu_mu_absolute_mae"],
        },
        "overall_pass": all(checks.values()),
        "claim_boundary": (
            "Validation supports the frozen truth-model statistical lock and exact "
            "nested coordinate composition, not direct neutrino observation or an "
            "individual pre-decay forecast."
        ),
    }
    (OUT / "T395_VALIDATION.json").write_text(
        json.dumps(validation, indent=2), encoding="utf-8"
    )
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()

