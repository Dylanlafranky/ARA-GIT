"""Independent arithmetic validation for the saved MX6 output packet."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np


EXPECTED_SOURCE_SHA256 = "6f2cd696312c7dcec4567463ef45fd61b5343a06983add505b9c4b7234ae1db5"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_cells(path: Path) -> dict[str, np.ndarray]:
    numeric_names = [
        "abs_cos_EB",
        "impedance_ratio_cB_over_E",
        "i1",
        "i2",
        "poynting_to_min_stress_axis_angle_deg",
        "shear_fraction_total",
        "shear_fraction_E",
        "shear_fraction_B",
    ]
    flag_names = ["active", "null_005", "null_010", "null_020"]
    values = {name: [] for name in numeric_names + flag_names}
    with path.open("r", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            for name in numeric_names:
                values[name].append(float(row[name]))
            for name in flag_names:
                values[name].append(int(row[name]))
    return {
        name: np.asarray(column, dtype=bool if name in flag_names else float)
        for name, column in values.items()
    }


def absolute_difference(recalculated: float, reported: float) -> float:
    return abs(float(recalculated) - float(reported))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()

    results = json.loads(
        (args.results_dir / "MX6_MAXWELL_STRESS_PHASE_FLIP_RESULTS.json").read_text(encoding="utf-8")
    )
    cells = read_cells(args.results_dir / "MX6_MAXWELL_STRESS_PHASE_FLIP_CELLS.csv")
    active = cells["active"]
    primary = cells["null_010"]

    recalculated = {
        "row_count": int(len(active)),
        "active_count": int(np.sum(active)),
        "null_counts": {
            "0.05": int(np.sum(cells["null_005"])),
            "0.10": int(np.sum(cells["null_010"])),
            "0.20": int(np.sum(cells["null_020"])),
        },
        "null_fractions_of_active": {
            "0.05": float(np.mean(cells["null_005"][active])),
            "0.10": float(np.mean(cells["null_010"][active])),
            "0.20": float(np.mean(cells["null_020"][active])),
        },
        "primary_null_abs_cos_EB_p50": float(np.nanmedian(cells["abs_cos_EB"][primary])),
        "primary_null_impedance_ratio_p50": float(
            np.nanmedian(cells["impedance_ratio_cB_over_E"][primary])
        ),
        "total_shear_p50": float(np.nanmedian(cells["shear_fraction_total"])),
        "electric_shear_p50": float(np.nanmedian(cells["shear_fraction_E"])),
        "magnetic_shear_p50": float(np.nanmedian(cells["shear_fraction_B"])),
        "maximum_poynting_axis_angle_deg": float(
            np.nanmax(cells["poynting_to_min_stress_axis_angle_deg"])
        ),
    }

    reported_geometry = results["part_b_public_field_geometry"]
    reported_stress = results["part_c_directional_stress"]["normalized_off_diagonal_content"]
    differences = {
        "active_count": abs(recalculated["active_count"] - int(reported_geometry["active_cell_count"])),
        "null_counts": {},
        "null_fractions": {},
        "primary_null_abs_cos_EB_p50": absolute_difference(
            recalculated["primary_null_abs_cos_EB_p50"],
            reported_geometry["threshold_sensitivity"]["0.10"]["null_like"]["abs_cos_EB"]["percentiles"]["p50"],
        ),
        "primary_null_impedance_ratio_p50": absolute_difference(
            recalculated["primary_null_impedance_ratio_p50"],
            reported_geometry["threshold_sensitivity"]["0.10"]["null_like"]["impedance_ratio_cB_over_E"]["percentiles"]["p50"],
        ),
        "total_shear_p50": absolute_difference(
            recalculated["total_shear_p50"], reported_stress["total_active"]["percentiles"]["p50"]
        ),
        "electric_shear_p50": absolute_difference(
            recalculated["electric_shear_p50"], reported_stress["electric_channel_active"]["percentiles"]["p50"]
        ),
        "magnetic_shear_p50": absolute_difference(
            recalculated["magnetic_shear_p50"], reported_stress["magnetic_channel_active"]["percentiles"]["p50"]
        ),
    }
    for threshold, flag in (("0.05", "null_005"), ("0.10", "null_010"), ("0.20", "null_020")):
        reported = reported_geometry["threshold_sensitivity"][threshold]
        differences["null_counts"][threshold] = abs(
            recalculated["null_counts"][threshold] - int(reported["null_like"]["n_cells"])
        )
        differences["null_fractions"][threshold] = absolute_difference(
            recalculated["null_fractions_of_active"][threshold], reported["null_like_fraction_of_active"]
        )

    flags_recalculated = {
        "0.05": active & (cells["i1"] <= 0.05) & (cells["i2"] <= 0.05),
        "0.10": active & (cells["i1"] <= 0.10) & (cells["i2"] <= 0.10),
        "0.20": active & (cells["i1"] <= 0.20) & (cells["i2"] <= 0.20),
    }
    flag_matches = {
        "0.05": bool(np.array_equal(flags_recalculated["0.05"], cells["null_005"])),
        "0.10": bool(np.array_equal(flags_recalculated["0.10"], cells["null_010"])),
        "0.20": bool(np.array_equal(flags_recalculated["0.20"], cells["null_020"])),
    }

    transform = results["part_a_exact_transformations"]
    transform_errors = [
        transform["paired_flip"]["stress_relative_l2_to_original"],
        transform["paired_flip"]["poynting_relative_l2_to_original"],
        transform["electric_only_flip"]["stress_relative_l2_to_original"],
        transform["electric_only_flip"]["poynting_relative_l2_to_negative_original"],
        transform["magnetic_only_flip"]["stress_relative_l2_to_original"],
        transform["magnetic_only_flip"]["poynting_relative_l2_to_negative_original"],
    ]
    rotation = results["part_c_directional_stress"]["rotation"]
    controls = results["analytic_controls"]
    control_checks = {
        "plane_wave_null": bool(
            controls["plane_wave"]["i1_normalized"] <= 1e-12
            and controls["plane_wave"]["i2_normalized"] <= 1e-12
            and controls["plane_wave"]["poynting_magnitude_W_per_m2"] > 0
        ),
        "capacitor_stress_without_flux": bool(
            controls["capacitor_like"]["poynting_magnitude_W_per_m2"] == 0
            and np.linalg.norm(controls["capacitor_like"]["stress_Pa"]) > 0
        ),
        "parallel_fields_nonperpendicular_without_flux": bool(
            controls["parallel_fields"]["abs_cos_EB"] == 1.0
            and controls["parallel_fields"]["poynting_magnitude_W_per_m2"] == 0
        ),
    }

    scalar_differences = [
        value for key, value in differences.items() if key not in ("null_counts", "null_fractions")
    ]
    scalar_differences.extend(differences["null_counts"].values())
    scalar_differences.extend(differences["null_fractions"].values())
    source_hash = sha256(args.source)
    validation_pass = bool(
        source_hash == EXPECTED_SOURCE_SHA256
        and recalculated["row_count"] == 32**3
        and all(flag_matches.values())
        and all(value <= 1e-12 for value in scalar_differences)
        and all(value <= 1e-12 for value in transform_errors)
        and rotation["tensor_covariance_relative_l2"] <= 1e-12
        and rotation["eigenvalue_invariance_relative_l2"] <= 1e-12
        and all(control_checks.values())
    )
    validation = {
        "source_sha256": source_hash,
        "source_hash_match": source_hash == EXPECTED_SOURCE_SHA256,
        "recalculated_from_cell_csv": recalculated,
        "absolute_differences_from_reported_json": differences,
        "null_flags_match_frozen_rules": flag_matches,
        "exact_transform_errors_le_1e-12": bool(all(value <= 1e-12 for value in transform_errors)),
        "rotation_errors_le_1e-12": bool(
            rotation["tensor_covariance_relative_l2"] <= 1e-12
            and rotation["eigenvalue_invariance_relative_l2"] <= 1e-12
        ),
        "analytic_control_checks": control_checks,
        "validation_pass": validation_pass,
    }
    output = args.results_dir / "MX6_MAXWELL_STRESS_PHASE_FLIP_VALIDATION.json"
    output.write_text(json.dumps(validation, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps(validation, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
