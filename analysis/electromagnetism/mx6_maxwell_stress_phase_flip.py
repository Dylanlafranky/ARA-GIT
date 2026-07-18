"""MX6 Maxwell-stress / paired-phase test on a public PIConGPU snapshot.

The test deliberately separates exact Maxwell transformation identities from
descriptive field geometry.  The source contains one time snapshot, so the
sign flips are algebraic interventions rather than observed temporal changes.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import h5py
import matplotlib.pyplot as plt
import numpy as np
from scipy.constants import c as C_LIGHT
from scipy.constants import epsilon_0 as EPSILON_0
from scipy.constants import mu_0 as MU_0

from mx4_lorentz_ara_crosswalk import (
    COMPONENTS,
    EXPECTED_SOURCE_SHA256,
    collocate_to_integer_grid,
    load_fields,
    percentile_dict,
    sha256,
)


THRESHOLDS = (0.05, 0.10, 0.20)
ACTIVITY_RELATIVE_FLOOR = 1e-12


def finite_float(value: float) -> float | None:
    value = float(value)
    return value if np.isfinite(value) else None


def relative_l2(observed: np.ndarray, expected: np.ndarray) -> float:
    observed = np.asarray(observed, dtype=float)
    expected = np.asarray(expected, dtype=float)
    denominator = float(np.linalg.norm(expected.ravel()))
    return float(np.linalg.norm((observed - expected).ravel()) / denominator) if denominator else 0.0


def max_scaled_error(observed: np.ndarray, expected: np.ndarray) -> float:
    observed = np.asarray(observed, dtype=float)
    expected = np.asarray(expected, dtype=float)
    denominator = max(float(np.max(np.abs(expected))), np.finfo(float).tiny)
    return float(np.max(np.abs(observed - expected)) / denominator)


def vector_norm(values: np.ndarray) -> np.ndarray:
    return np.linalg.norm(np.asarray(values, dtype=float), axis=-1)


def maxwell_quantities(e_field: np.ndarray, b_field: np.ndarray) -> dict[str, np.ndarray]:
    e_field = np.asarray(e_field, dtype=float)
    b_field = np.asarray(b_field, dtype=float)
    e2 = np.sum(e_field**2, axis=-1)
    b2 = np.sum(b_field**2, axis=-1)
    identity = np.eye(3)
    stress_e = EPSILON_0 * (
        e_field[..., :, None] * e_field[..., None, :]
        - 0.5 * e2[..., None, None] * identity
    )
    stress_b = (1.0 / MU_0) * (
        b_field[..., :, None] * b_field[..., None, :]
        - 0.5 * b2[..., None, None] * identity
    )
    return {
        "u_e": 0.5 * EPSILON_0 * e2,
        "u_b": 0.5 * b2 / MU_0,
        "poynting": np.cross(e_field, b_field) / MU_0,
        "stress_e": stress_e,
        "stress_b": stress_b,
        "stress": stress_e + stress_b,
    }


def shear_fraction(stress: np.ndarray) -> np.ndarray:
    off_diagonal = np.sqrt(
        2.0
        * (
            stress[..., 0, 1] ** 2
            + stress[..., 0, 2] ** 2
            + stress[..., 1, 2] ** 2
        )
    )
    denominator = np.linalg.norm(stress, axis=(-2, -1))
    return np.divide(
        off_diagonal,
        denominator,
        out=np.full_like(off_diagonal, np.nan),
        where=denominator > 0,
    )


def axis_alignment_angle(stress: np.ndarray, poynting: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    eigenvalues, eigenvectors = np.linalg.eigh(stress)
    minimum_axis = eigenvectors[..., :, 0]
    s_magnitude = vector_norm(poynting)
    cosine = np.divide(
        np.abs(np.sum(minimum_axis * poynting, axis=-1)),
        s_magnitude,
        out=np.full_like(s_magnitude, np.nan),
        where=s_magnitude > 0,
    )
    angle = np.degrees(np.arccos(np.clip(cosine, 0.0, 1.0)))
    return eigenvalues, angle


def rotation_matrix(axis: np.ndarray, angle: float) -> np.ndarray:
    axis = np.asarray(axis, dtype=float)
    axis = axis / np.linalg.norm(axis)
    x, y, z = axis
    skew = np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])
    return np.eye(3) * np.cos(angle) + (1.0 - np.cos(angle)) * np.outer(axis, axis) + np.sin(angle) * skew


def subset_summary(values: np.ndarray, mask: np.ndarray) -> dict:
    selected = np.asarray(values, dtype=float)[mask]
    selected = selected[np.isfinite(selected)]
    return {
        "n": int(len(selected)),
        "percentiles": percentile_dict(selected),
        "mean": finite_float(np.mean(selected)) if len(selected) else None,
    }


def geometry_summary(
    mask: np.ndarray,
    cos_eb_abs: np.ndarray,
    impedance_ratio: np.ndarray,
    alignment_angle: np.ndarray,
    i1: np.ndarray,
    i2: np.ndarray,
) -> dict:
    return {
        "n_cells": int(np.sum(mask)),
        "abs_cos_EB": subset_summary(cos_eb_abs, mask),
        "impedance_ratio_cB_over_E": subset_summary(impedance_ratio, mask),
        "poynting_to_minimum_stress_axis_angle_deg": subset_summary(alignment_angle, mask),
        "i1_normalized": subset_summary(i1, mask),
        "i2_normalized": subset_summary(i2, mask),
    }


def analytic_control(name: str, e_field: np.ndarray, b_field: np.ndarray) -> dict:
    e_field = np.asarray(e_field, dtype=float)
    b_field = np.asarray(b_field, dtype=float)
    quantities = maxwell_quantities(e_field, b_field)
    e_norm = float(np.linalg.norm(e_field))
    b_norm = float(np.linalg.norm(b_field))
    denominator = e_norm**2 + (C_LIGHT * b_norm) ** 2
    dot = float(np.dot(e_field, b_field))
    eigenvalues, angle = axis_alignment_angle(
        quantities["stress"][None, ...], quantities["poynting"][None, ...]
    )
    cos_eb = abs(dot) / (e_norm * b_norm) if e_norm and b_norm else None
    return {
        "name": name,
        "E_V_per_m": e_field.tolist(),
        "B_T": b_field.tolist(),
        "abs_cos_EB": finite_float(cos_eb) if cos_eb is not None else None,
        "i1_normalized": abs(e_norm**2 - (C_LIGHT * b_norm) ** 2) / denominator if denominator else None,
        "i2_normalized": 2.0 * C_LIGHT * abs(dot) / denominator if denominator else None,
        "energy_density_J_per_m3": float(quantities["u_e"] + quantities["u_b"]),
        "poynting_W_per_m2": quantities["poynting"].tolist(),
        "poynting_magnitude_W_per_m2": float(np.linalg.norm(quantities["poynting"])),
        "stress_Pa": quantities["stress"].tolist(),
        "stress_eigenvalues_Pa": eigenvalues[0].tolist(),
        "poynting_to_minimum_stress_axis_angle_deg": finite_float(angle[0]),
    }


def run_analysis(source: Path) -> tuple[dict, dict[str, np.ndarray]]:
    source = source.resolve()
    observed_hash = sha256(source)
    if observed_hash.lower() != EXPECTED_SOURCE_SHA256:
        raise ValueError(
            f"Source hash mismatch: expected {EXPECTED_SOURCE_SHA256}, got {observed_hash}"
        )

    with h5py.File(source, "r") as handle:
        iteration = handle["data/200"]
        fields, offsets = load_fields(iteration)
        e_field = np.stack(
            [collocate_to_integer_grid(fields["E"][component], offsets["E"][component]) for component in COMPONENTS],
            axis=-1,
        )
        b_field = np.stack(
            [collocate_to_integer_grid(fields["B"][component], offsets["B"][component]) for component in COMPONENTS],
            axis=-1,
        )
        iteration_time = float(iteration.attrs["time"] * iteration.attrs["timeUnitSI"])
        grid_spacing = (
            np.asarray(iteration["fields/E"].attrs["gridSpacing"], dtype=float)
            * float(iteration["fields/E"].attrs["gridUnitSI"])
        )

    if e_field.shape != (32, 32, 32, 3) or b_field.shape != e_field.shape:
        raise ValueError(f"Unexpected field shapes: E={e_field.shape}, B={b_field.shape}")
    if not np.all(np.isfinite(e_field)) or not np.all(np.isfinite(b_field)):
        raise ValueError("Non-finite field values found")

    base = maxwell_quantities(e_field, b_field)
    paired = maxwell_quantities(-e_field, -b_field)
    electric_flip = maxwell_quantities(-e_field, b_field)
    magnetic_flip = maxwell_quantities(e_field, -b_field)

    part_a = {
        "paired_flip": {
            "stress_relative_l2_to_original": relative_l2(paired["stress"], base["stress"]),
            "stress_max_scaled_error": max_scaled_error(paired["stress"], base["stress"]),
            "poynting_relative_l2_to_original": relative_l2(paired["poynting"], base["poynting"]),
            "poynting_max_scaled_error": max_scaled_error(paired["poynting"], base["poynting"]),
        },
        "electric_only_flip": {
            "stress_relative_l2_to_original": relative_l2(electric_flip["stress"], base["stress"]),
            "poynting_relative_l2_to_negative_original": relative_l2(electric_flip["poynting"], -base["poynting"]),
        },
        "magnetic_only_flip": {
            "stress_relative_l2_to_original": relative_l2(magnetic_flip["stress"], base["stress"]),
            "poynting_relative_l2_to_negative_original": relative_l2(magnetic_flip["poynting"], -base["poynting"]),
        },
    }
    all_a_errors = [value for section in part_a.values() for key, value in section.items() if "relative_l2" in key]
    part_a["all_relative_l2_errors_le_1e-12"] = bool(all(value <= 1e-12 for value in all_a_errors))

    e_norm = vector_norm(e_field)
    cb_norm = C_LIGHT * vector_norm(b_field)
    e_floor = ACTIVITY_RELATIVE_FLOOR * float(np.max(e_norm))
    cb_floor = ACTIVITY_RELATIVE_FLOOR * float(np.max(cb_norm))
    active = (e_norm > e_floor) & (cb_norm > cb_floor)
    energy_denominator = e_norm**2 + cb_norm**2
    dot_eb = np.sum(e_field * b_field, axis=-1)
    cos_eb_abs = np.divide(
        np.abs(dot_eb),
        e_norm * (cb_norm / C_LIGHT),
        out=np.full_like(e_norm, np.nan),
        where=(e_norm > 0) & (cb_norm > 0),
    )
    impedance_ratio = np.divide(cb_norm, e_norm, out=np.full_like(e_norm, np.nan), where=e_norm > 0)
    i1 = np.divide(
        np.abs(e_norm**2 - cb_norm**2),
        energy_denominator,
        out=np.full_like(e_norm, np.nan),
        where=energy_denominator > 0,
    )
    i2 = np.divide(
        2.0 * C_LIGHT * np.abs(dot_eb),
        energy_denominator,
        out=np.full_like(e_norm, np.nan),
        where=energy_denominator > 0,
    )
    eigenvalues, alignment_angle = axis_alignment_angle(base["stress"], base["poynting"])

    threshold_results = {}
    for threshold in THRESHOLDS:
        null_like = active & (i1 <= threshold) & (i2 <= threshold)
        non_null = active & ~null_like
        threshold_results[f"{threshold:.2f}"] = {
            "threshold": threshold,
            "null_like_fraction_of_active": float(np.mean(null_like[active])) if np.any(active) else None,
            "null_like": geometry_summary(null_like, cos_eb_abs, impedance_ratio, alignment_angle, i1, i2),
            "non_null_active": geometry_summary(non_null, cos_eb_abs, impedance_ratio, alignment_angle, i1, i2),
        }

    part_b = {
        "activity_relative_floor": ACTIVITY_RELATIVE_FLOOR,
        "electric_floor_V_per_m": e_floor,
        "cB_floor_V_per_m": cb_floor,
        "active_cell_count": int(np.sum(active)),
        "active_fraction_of_grid": float(np.mean(active)),
        "threshold_sensitivity": threshold_results,
        "primary_threshold": "0.10",
    }

    shear_total = shear_fraction(base["stress"])
    shear_e = shear_fraction(base["stress_e"])
    shear_b = shear_fraction(base["stress_b"])
    total_energy = base["u_e"] + base["u_b"]
    electric_fraction = np.divide(
        base["u_e"], total_energy, out=np.full_like(total_energy, np.nan), where=total_energy > 0
    )
    energy_active = total_energy > ACTIVITY_RELATIVE_FLOOR * float(np.max(total_energy))
    electric_dominant = energy_active & (electric_fraction >= 0.90)
    magnetic_dominant = energy_active & (electric_fraction <= 0.10)
    mixed_energy = energy_active & (electric_fraction > 0.10) & (electric_fraction < 0.90)

    rotation = rotation_matrix(np.array([1.0, 2.0, 3.0]), 0.731)
    e_rotated = np.einsum("ij,...j->...i", rotation, e_field)
    b_rotated = np.einsum("ij,...j->...i", rotation, b_field)
    rotated = maxwell_quantities(e_rotated, b_rotated)
    covariance_expected = np.einsum("ia,...ab,jb->...ij", rotation, base["stress"], rotation)
    eigenvalues_rotated = np.linalg.eigvalsh(rotated["stress"])
    covariance_error = relative_l2(rotated["stress"], covariance_expected)
    eigenvalue_error = relative_l2(eigenvalues_rotated, eigenvalues)

    part_c = {
        "normalized_off_diagonal_content": {
            "total_active": subset_summary(shear_total, energy_active),
            "electric_channel_active": subset_summary(shear_e, energy_active),
            "magnetic_channel_active": subset_summary(shear_b, energy_active),
            "total_electric_dominant": subset_summary(shear_total, electric_dominant),
            "total_magnetic_dominant": subset_summary(shear_total, magnetic_dominant),
            "total_mixed_energy": subset_summary(shear_total, mixed_energy),
        },
        "energy_partition": {
            "electric_fraction": subset_summary(electric_fraction, energy_active),
            "electric_dominant_n": int(np.sum(electric_dominant)),
            "magnetic_dominant_n": int(np.sum(magnetic_dominant)),
            "mixed_n": int(np.sum(mixed_energy)),
        },
        "rotation": {
            "axis": [1.0, 2.0, 3.0],
            "angle_rad": 0.731,
            "matrix": rotation.tolist(),
            "tensor_covariance_relative_l2": covariance_error,
            "eigenvalue_invariance_relative_l2": eigenvalue_error,
            "both_errors_le_1e-12": bool(covariance_error <= 1e-12 and eigenvalue_error <= 1e-12),
        },
    }

    e0 = 100_000.0
    controls = {
        "plane_wave": analytic_control(
            "plane wave", np.array([e0, 0.0, 0.0]), np.array([0.0, e0 / C_LIGHT, 0.0])
        ),
        "capacitor_like": analytic_control(
            "capacitor-like electric field", np.array([e0, 0.0, 0.0]), np.zeros(3)
        ),
        "parallel_fields": analytic_control(
            "parallel E and B", np.array([e0, 0.0, 0.0]), np.array([e0 / C_LIGHT, 0.0, 0.0])
        ),
    }

    results = {
        "test": "MX6 Maxwell-stress / paired-phase public-data crosswalk",
        "status": "Maxwell recovery/crosswalk; not independent ARA confirmation",
        "source": {
            "path": str(source),
            "bytes": source.stat().st_size,
            "sha256": observed_hash,
            "hash_match": observed_hash == EXPECTED_SOURCE_SHA256,
            "repository": "https://github.com/openPMD/openPMD-example-datasets",
            "archive": "legacy_datasets.tar.gz",
            "license": "CC0-1.0",
            "producer": "PIConGPU",
            "producer_version": "0.5.0",
            "iteration": 200,
            "time_s": iteration_time,
            "field_shape_zyx": list(e_field.shape[:3]),
            "grid_spacing_m": grid_spacing.tolist(),
            "snapshot_count": 1,
        },
        "data_quality": {
            "all_fields_finite": True,
            "field_solver": "Yee",
            "collocation": "linear to integer grid using recorded component offsets",
            "electric_magnitude_V_per_m": percentile_dict(e_norm),
            "cB_magnitude_V_per_m": percentile_dict(cb_norm),
        },
        "part_a_exact_transformations": part_a,
        "part_b_public_field_geometry": part_b,
        "part_c_directional_stress": part_c,
        "analytic_controls": controls,
        "interpretation": {
            "recovered": "Exact Maxwell sign transformation and tensor covariance identities; measured separation of null-like and non-null field sectors.",
            "ara_crosswalk": "Joint E/B sign reversal preserves parent energy-flow and stress identity, while single-channel reversal preserves stress but reverses flow.",
            "claim_ceiling": "One snapshot cannot observe temporal phase swapping, and exact Maxwell identities are implementation/calibration evidence rather than independent confirmation of ARA.",
        },
    }

    cells = {
        "e_norm": e_norm,
        "cb_norm": cb_norm,
        "u_e": base["u_e"],
        "u_b": base["u_b"],
        "electric_fraction": electric_fraction,
        "cos_eb_abs": cos_eb_abs,
        "impedance_ratio": impedance_ratio,
        "i1": i1,
        "i2": i2,
        "poynting_magnitude": vector_norm(base["poynting"]),
        "alignment_angle": alignment_angle,
        "shear_total": shear_total,
        "shear_e": shear_e,
        "shear_b": shear_b,
        "eigenvalues": eigenvalues,
        "active": active,
        "null_005": active & (i1 <= 0.05) & (i2 <= 0.05),
        "null_010": active & (i1 <= 0.10) & (i2 <= 0.10),
        "null_020": active & (i1 <= 0.20) & (i2 <= 0.20),
    }
    return results, cells


def write_cells(path: Path, cells: dict[str, np.ndarray]) -> None:
    fieldnames = [
        "z", "y", "x", "active", "null_005", "null_010", "null_020",
        "E_magnitude_V_per_m", "cB_magnitude_V_per_m", "u_E_J_per_m3", "u_B_J_per_m3",
        "electric_energy_fraction", "abs_cos_EB", "impedance_ratio_cB_over_E", "i1", "i2",
        "poynting_magnitude_W_per_m2", "poynting_to_min_stress_axis_angle_deg",
        "shear_fraction_total", "shear_fraction_E", "shear_fraction_B",
        "stress_eigenvalue_min_Pa", "stress_eigenvalue_mid_Pa", "stress_eigenvalue_max_Pa",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        shape = cells["e_norm"].shape
        for z, y, x in np.ndindex(shape):
            index = (z, y, x)
            eigenvalues = cells["eigenvalues"][index]
            writer.writerow({
                "z": z, "y": y, "x": x,
                "active": int(cells["active"][index]),
                "null_005": int(cells["null_005"][index]),
                "null_010": int(cells["null_010"][index]),
                "null_020": int(cells["null_020"][index]),
                "E_magnitude_V_per_m": cells["e_norm"][index],
                "cB_magnitude_V_per_m": cells["cb_norm"][index],
                "u_E_J_per_m3": cells["u_e"][index],
                "u_B_J_per_m3": cells["u_b"][index],
                "electric_energy_fraction": cells["electric_fraction"][index],
                "abs_cos_EB": cells["cos_eb_abs"][index],
                "impedance_ratio_cB_over_E": cells["impedance_ratio"][index],
                "i1": cells["i1"][index],
                "i2": cells["i2"][index],
                "poynting_magnitude_W_per_m2": cells["poynting_magnitude"][index],
                "poynting_to_min_stress_axis_angle_deg": cells["alignment_angle"][index],
                "shear_fraction_total": cells["shear_total"][index],
                "shear_fraction_E": cells["shear_e"][index],
                "shear_fraction_B": cells["shear_b"][index],
                "stress_eigenvalue_min_Pa": eigenvalues[0],
                "stress_eigenvalue_mid_Pa": eigenvalues[1],
                "stress_eigenvalue_max_Pa": eigenvalues[2],
            })


def make_figure(path: Path, results: dict, cells: dict[str, np.ndarray]) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    figure, axes = plt.subplots(2, 3, figsize=(16, 10), constrained_layout=True)
    active = cells["active"]
    null = cells["null_010"]
    non_null = active & ~null

    scatter = axes[0, 0].scatter(
        cells["i1"][active], cells["i2"][active],
        c=np.log10(np.maximum(cells["u_e"][active] + cells["u_b"][active], np.finfo(float).tiny)),
        s=5, alpha=0.35, cmap="viridis", rasterized=True,
    )
    axes[0, 0].axvline(0.10, color="#c23b22", linestyle="--")
    axes[0, 0].axhline(0.10, color="#c23b22", linestyle="--")
    axes[0, 0].set(xlabel=r"$i_1$ balance residual", ylabel=r"$i_2$ non-perpendicularity", title="Public field cells: null-sector map")
    figure.colorbar(scatter, ax=axes[0, 0], label=r"$\log_{10}$ energy density (J m$^{-3}$)")

    bins = np.linspace(0, 1, 41)
    axes[0, 1].hist(cells["cos_eb_abs"][non_null], bins=bins, density=True, alpha=0.55, label="non-null active")
    axes[0, 1].hist(cells["cos_eb_abs"][null], bins=bins, density=True, alpha=0.70, label="null-like (0.10)")
    axes[0, 1].set(xlabel=r"$|\cos\theta_{EB}|$", ylabel="density", title="E/B perpendicularity")
    axes[0, 1].legend()

    ratio_bins = np.linspace(-2, 2, 61)
    axes[0, 2].hist(np.log10(cells["impedance_ratio"][non_null]), bins=ratio_bins, density=True, alpha=0.55, label="non-null active")
    axes[0, 2].hist(np.log10(cells["impedance_ratio"][null]), bins=ratio_bins, density=True, alpha=0.70, label="null-like (0.10)")
    axes[0, 2].axvline(0.0, color="black", linewidth=1)
    axes[0, 2].set(xlabel=r"$\log_{10}(c|B|/|E|)$", ylabel="density", title="Electric/magnetic balance")
    axes[0, 2].legend()

    angle_bins = np.linspace(0, 90, 46)
    axes[1, 0].hist(cells["alignment_angle"][non_null], bins=angle_bins, density=True, alpha=0.55, label="non-null active")
    axes[1, 0].hist(cells["alignment_angle"][null], bins=angle_bins, density=True, alpha=0.70, label="null-like (0.10)")
    axes[1, 0].set(xlabel="unsigned angle (degrees)", ylabel="density", title="Poynting vs minimum-stress axis")
    axes[1, 0].legend()

    shear_bins = np.linspace(0, 0.82, 42)
    axes[1, 1].hist(cells["shear_total"][active], bins=shear_bins, density=True, histtype="step", linewidth=2, label="total")
    axes[1, 1].hist(cells["shear_e"][active], bins=shear_bins, density=True, histtype="step", linewidth=2, label="electric channel")
    axes[1, 1].hist(cells["shear_b"][active], bins=shear_bins, density=True, histtype="step", linewidth=2, label="magnetic channel")
    axes[1, 1].set(xlabel="normalized off-diagonal stress", ylabel="density", title="Direction retained beyond scalar energy")
    axes[1, 1].legend()

    transformation = results["part_a_exact_transformations"]
    rotation = results["part_c_directional_stress"]["rotation"]
    labels = ["paired T", "paired S", "E-only T", "E-only −S", "B-only T", "B-only −S", "rotation T", "rotation eig"]
    values = [
        transformation["paired_flip"]["stress_relative_l2_to_original"],
        transformation["paired_flip"]["poynting_relative_l2_to_original"],
        transformation["electric_only_flip"]["stress_relative_l2_to_original"],
        transformation["electric_only_flip"]["poynting_relative_l2_to_negative_original"],
        transformation["magnetic_only_flip"]["stress_relative_l2_to_original"],
        transformation["magnetic_only_flip"]["poynting_relative_l2_to_negative_original"],
        rotation["tensor_covariance_relative_l2"],
        rotation["eigenvalue_invariance_relative_l2"],
    ]
    plotted = np.maximum(values, 1e-18)
    axes[1, 2].barh(labels, plotted, color=["#4472c4"] * 6 + ["#70ad47"] * 2)
    axes[1, 2].axvline(1e-12, color="#c23b22", linestyle="--", label="frozen gate")
    axes[1, 2].set_xscale("log")
    axes[1, 2].set(xlabel="relative L2 error (zeros plotted at 1e-18)", title="Exact calibration checks")
    axes[1, 2].legend()

    primary = results["part_b_public_field_geometry"]["threshold_sensitivity"]["0.10"]
    figure.suptitle(
        f"MX6 Maxwell stress / paired phase — {primary['null_like']['n_cells']:,} null-like of {results['part_b_public_field_geometry']['active_cell_count']:,} active cells",
        fontsize=15,
    )
    figure.savefig(path, dpi=180)
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    results, cells = run_analysis(args.source)
    results_path = args.output_dir / "MX6_MAXWELL_STRESS_PHASE_FLIP_RESULTS.json"
    cells_path = args.output_dir / "MX6_MAXWELL_STRESS_PHASE_FLIP_CELLS.csv"
    figure_path = args.output_dir / "MX6_MAXWELL_STRESS_PHASE_FLIP.png"
    results_path.write_text(json.dumps(results, indent=2, allow_nan=False), encoding="utf-8")
    write_cells(cells_path, cells)
    make_figure(figure_path, results, cells)
    print(json.dumps({
        "results": str(results_path),
        "cells": str(cells_path),
        "figure": str(figure_path),
        "paired_transform_pass": results["part_a_exact_transformations"]["all_relative_l2_errors_le_1e-12"],
        "rotation_pass": results["part_c_directional_stress"]["rotation"]["both_errors_le_1e-12"],
        "primary_null_like_fraction": results["part_b_public_field_geometry"]["threshold_sensitivity"]["0.10"]["null_like_fraction_of_active"],
    }, indent=2))


if __name__ == "__main__":
    main()
