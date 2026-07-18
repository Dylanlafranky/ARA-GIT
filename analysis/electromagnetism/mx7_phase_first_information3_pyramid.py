"""MX7 phase-first Information^3 / pyramid electric-closure analysis.

The analysis compares two separately compressed phase marginals with their
joint four-quadrant relation, then restores relation-conditioned amplitude as
an exact decompression ceiling.  The source contains one public PIConGPU
snapshot; this is a closure autopsy, not a time-dynamic confirmation.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import h5py
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr

from mx4_lorentz_ara_crosswalk import (
    COMPONENTS,
    EXPECTED_SOURCE_SHA256,
    collocate_to_integer_grid,
    deposit_cic,
    load_fields,
    load_particle_species,
    percentile_dict,
    sha256,
    trilinear_sample,
    vector_metrics,
)
from mx5_child_ara_teara_closure import (
    deposit_cic_first_moments,
    physical_vector_gradients,
    relative_l2,
)


QUADRANTS = ("AA", "AB", "BA", "BB")
QUADRANT_SIGNS = np.array([1.0, -1.0, -1.0, 1.0])


def safe_divide(numerator: np.ndarray, denominator: np.ndarray) -> np.ndarray:
    return np.divide(
        numerator,
        denominator,
        out=np.full_like(np.asarray(numerator, dtype=float), np.nan, dtype=float),
        where=np.asarray(denominator) != 0,
    )


def finite_percentiles(values: np.ndarray) -> dict[str, float]:
    values = np.asarray(values, dtype=float)
    return percentile_dict(values[np.isfinite(values)])


def mutual_information_from_quadrants(probabilities: np.ndarray) -> np.ndarray:
    """Mutual information in bits for p[AA, AB, BA, BB]."""
    probabilities = np.asarray(probabilities, dtype=float)
    total = np.sum(probabilities, axis=-1, keepdims=True)
    p = np.divide(
        probabilities,
        total,
        out=np.zeros_like(probabilities),
        where=total > 0,
    )
    p_q_a = p[..., 0] + p[..., 1]
    p_q_b = p[..., 2] + p[..., 3]
    p_e_a = p[..., 0] + p[..., 2]
    p_e_b = p[..., 1] + p[..., 3]
    independent = np.stack(
        [p_q_a * p_e_a, p_q_a * p_e_b, p_q_b * p_e_a, p_q_b * p_e_b],
        axis=-1,
    )
    terms = np.zeros_like(p)
    valid = (p > 0) & (independent > 0)
    terms[valid] = p[valid] * np.log2(p[valid] / independent[valid])
    return np.sum(terms, axis=-1)


def model_comparison(target: np.ndarray, estimate: np.ndarray, mask: np.ndarray) -> dict:
    metrics = vector_metrics(target, estimate, mask)
    metrics["relative_l2"] = relative_l2(target, estimate, mask)
    return metrics


def favourable_relative_change(metric: str, baseline: float, candidate: float) -> float:
    denominator = max(abs(float(baseline)), np.finfo(float).tiny)
    if metric == "vector_correlation":
        return (float(candidate) - float(baseline)) / denominator
    return (float(baseline) - float(candidate)) / denominator


def classify_joint(
    marginal: dict,
    joint: dict,
    marginal_l2: float,
    joint_l2: float,
    half_metrics: dict,
) -> tuple[str, dict]:
    keys = ("vector_correlation", "nrmse_by_target_std", "median_angular_error_deg")
    changes = {
        key: favourable_relative_change(key, marginal[key], joint[key]) for key in keys
    }
    l2_reduction = (marginal_l2 - joint_l2) / marginal_l2 if marginal_l2 else float("nan")
    all_favourable = all(value > 0 for value in changes.values())
    two_material = sum(value >= 0.05 for value in changes.values()) >= 2
    halves_pass = all(
        values["joint"]["vector_correlation"] > values["marginal"]["vector_correlation"]
        and values["joint"]["nrmse_by_target_std"] < values["marginal"]["nrmse_by_target_std"]
        for values in half_metrics.values()
    )
    material = bool(all_favourable and two_material and l2_reduction >= 0.10 and halves_pass)
    strong = bool(
        material
        and joint["vector_correlation"] >= 0.70
        and joint["nrmse_by_target_std"] <= 0.70
        and joint["median_angular_error_deg"] <= 45.0
    )
    if strong:
        classification = "strong compact electric recovery"
    elif material:
        classification = "material phase-first improvement"
    elif all_favourable:
        classification = "directional improvement below frozen materiality gate"
    else:
        classification = "joint quadrant relation did not improve all frozen metrics"
    return classification, {
        "favourable_relative_changes": changes,
        "residual_relative_l2_reduction": float(l2_reduction),
        "all_three_metrics_favourable": bool(all_favourable),
        "at_least_two_metrics_improve_ge_5_percent": bool(two_material),
        "both_z_halves_corr_and_nrmse_improve": bool(halves_pass),
        "material_phase_first_gate": material,
        "strong_compact_gate": strong,
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
        field_shape = fields["E"]["x"].shape
        if field_shape != (32, 32, 32):
            raise ValueError(f"Unexpected field shape {field_shape}")
        grid_spacing_xyz_m = (
            np.asarray(iteration["fields/E"].attrs["gridSpacing"], dtype=float)
            * float(iteration["fields/E"].attrs["gridUnitSI"])
        )
        cell_volume = float(np.prod(grid_spacing_xyz_m))
        e_parent = np.stack(
            [
                collocate_to_integer_grid(fields["E"][component], offsets["E"][component])
                for component in COMPONENTS
            ],
            axis=-1,
        )

        # Shared columns: absolute charge activity, signed charge, occupancy.
        # Each component then has: |E|, sign(E), joint sign, |E|*joint sign,
        # four quadrant weights, and four quadrant amplitude sums.
        per_component_columns = 12
        deposited = np.zeros(field_shape + (3 + 3 * per_component_columns,), dtype=float)
        p_rho_total = np.zeros(field_shape + (3,), dtype=float)
        particle_counts: dict[str, int] = {}
        neutral_counts = np.zeros(3, dtype=np.int64)
        total_particle_component_count = 0

        for species_name in ("e", "i"):
            particles = load_particle_species(iteration, species_name)
            coordinates = particles["coordinates"]
            weighting = particles["weighting"]
            charge = float(particles["charge"])
            velocity = particles["velocity"]
            particle_counts[species_name] = int(len(coordinates))
            e_particle = np.column_stack(
                [
                    trilinear_sample(fields["E"][component], coordinates, offsets["E"][component])
                    for component in COMPONENTS
                ]
            )

            absolute_macro_charge = weighting * abs(charge)
            charge_sign = np.sign(charge) * np.ones(len(coordinates), dtype=float)
            values = np.zeros((len(coordinates), deposited.shape[-1]), dtype=float)
            values[:, 0] = absolute_macro_charge
            values[:, 1] = absolute_macro_charge * charge_sign
            values[:, 2] = 1.0

            for component_index in range(3):
                start = 3 + component_index * per_component_columns
                field_component = e_particle[:, component_index]
                magnitude = np.abs(field_component)
                field_sign = np.sign(field_component)
                relation_sign = charge_sign * field_sign
                neutral_counts[component_index] += int(np.sum(field_sign == 0))
                total_particle_component_count += len(field_component)
                values[:, start + 0] = absolute_macro_charge * magnitude
                values[:, start + 1] = absolute_macro_charge * field_sign
                values[:, start + 2] = absolute_macro_charge * relation_sign
                values[:, start + 3] = absolute_macro_charge * magnitude * relation_sign

                indicators = (
                    (charge_sign > 0) & (field_sign > 0),
                    (charge_sign > 0) & (field_sign < 0),
                    (charge_sign < 0) & (field_sign > 0),
                    (charge_sign < 0) & (field_sign < 0),
                )
                for quadrant_index, indicator in enumerate(indicators):
                    values[:, start + 4 + quadrant_index] = absolute_macro_charge * indicator
                    values[:, start + 8 + quadrant_index] = (
                        absolute_macro_charge * magnitude * indicator
                    )

            deposited += deposit_cic(coordinates, values, field_shape)
            p_rho, _ = deposit_cic_first_moments(
                coordinates,
                weighting * charge,
                velocity,
                field_shape,
                grid_spacing_xyz_m,
            )
            p_rho_total += p_rho

        absolute_charge_sum = deposited[..., 0]
        signed_charge_density = deposited[..., 1] / cell_volume
        occupancy = deposited[..., 2]
        charge_sign_mean = safe_divide(deposited[..., 1], absolute_charge_sum)
        absolute_charge_density = absolute_charge_sum / cell_volume
        p_rho_total /= cell_volume

        mean_magnitude = np.zeros(field_shape + (3,), dtype=float)
        field_sign_mean = np.zeros_like(mean_magnitude)
        relation_sign_mean = np.zeros_like(mean_magnitude)
        mean_magnitude_relation = np.zeros_like(mean_magnitude)
        quadrant_probabilities = np.zeros(field_shape + (3, 4), dtype=float)
        quadrant_amplitudes = np.full(field_shape + (3, 4), np.nan, dtype=float)

        for component_index in range(3):
            start = 3 + component_index * per_component_columns
            mean_magnitude[..., component_index] = safe_divide(
                deposited[..., start + 0], absolute_charge_sum
            )
            field_sign_mean[..., component_index] = safe_divide(
                deposited[..., start + 1], absolute_charge_sum
            )
            relation_sign_mean[..., component_index] = safe_divide(
                deposited[..., start + 2], absolute_charge_sum
            )
            mean_magnitude_relation[..., component_index] = safe_divide(
                deposited[..., start + 3], absolute_charge_sum
            )
            for quadrant_index in range(4):
                quadrant_weight = deposited[..., start + 4 + quadrant_index]
                quadrant_probabilities[..., component_index, quadrant_index] = safe_divide(
                    quadrant_weight, absolute_charge_sum
                )
                quadrant_amplitudes[..., component_index, quadrant_index] = safe_divide(
                    deposited[..., start + 8 + quadrant_index], quadrant_weight
                )

        marginal = (
            absolute_charge_density[..., None]
            * mean_magnitude
            * charge_sign_mean[..., None]
            * field_sign_mean
        )
        joint = (
            absolute_charge_density[..., None]
            * mean_magnitude
            * relation_sign_mean
        )
        target = absolute_charge_density[..., None] * mean_magnitude_relation

        conditional_terms = np.nan_to_num(
            quadrant_probabilities * quadrant_amplitudes, nan=0.0
        )
        pyramid = absolute_charge_density[..., None] * np.sum(
            conditional_terms * QUADRANT_SIGNS,
            axis=-1,
        )
        phase_coupling = relation_sign_mean - charge_sign_mean[..., None] * field_sign_mean
        phase_correction = absolute_charge_density[..., None] * mean_magnitude * phase_coupling
        amplitude_relation_coupling = mean_magnitude_relation - mean_magnitude * relation_sign_mean
        amplitude_correction = absolute_charge_density[..., None] * amplitude_relation_coupling
        reassembled = marginal + phase_correction + amplitude_correction

        flat = signed_charge_density[..., None] * e_parent
        gradients_e = physical_vector_gradients(e_parent, grid_spacing_xyz_m)
        predicted_other_e = np.zeros_like(target)
        for axis in range(3):
            predicted_other_e += p_rho_total[..., axis, None] * gradients_e[axis]
        first_moment = flat + predicted_other_e

        interior = np.zeros(field_shape, dtype=bool)
        interior[1:-1, 1:-1, 1:-1] = True
        active_mask = interior & (occupancy > 0)
        lower_mask = active_mask.copy()
        lower_mask[field_shape[0] // 2 :] = False
        upper_mask = active_mask.copy()
        upper_mask[: field_shape[0] // 2] = False

        metrics = {
            "flat_parent": model_comparison(target, flat, active_mask),
            "mx5_first_moment": model_comparison(target, first_moment, active_mask),
            "independent_phase_marginals": model_comparison(target, marginal, active_mask),
            "joint_quadrant_triangle": model_comparison(target, joint, active_mask),
            "conditioned_amplitude_pyramid": model_comparison(target, pyramid, active_mask),
        }
        half_metrics = {}
        for name, mask in (("lower_z_half", lower_mask), ("upper_z_half", upper_mask)):
            half_metrics[name] = {
                "n_cells": int(np.sum(mask)),
                "marginal": model_comparison(target, marginal, mask),
                "joint": model_comparison(target, joint, mask),
            }

        classification, frozen_gates = classify_joint(
            metrics["independent_phase_marginals"],
            metrics["joint_quadrant_triangle"],
            metrics["independent_phase_marginals"]["relative_l2"],
            metrics["joint_quadrant_triangle"]["relative_l2"],
            half_metrics,
        )

        pyramid_error = relative_l2(target, pyramid, active_mask)
        reassembly_error = relative_l2(target, reassembled, active_mask)
        direct_deposition_error = relative_l2(target, pyramid, active_mask)
        mutual_information = mutual_information_from_quadrants(quadrant_probabilities)
        active_component_mask = np.repeat(active_mask[..., None], 3, axis=-1)
        mi_values = mutual_information[active_component_mask]
        phase_correction_values = np.abs(phase_correction[active_component_mask])
        amplitude_correction_values = np.abs(amplitude_correction[active_component_mask])
        valid_mi = np.isfinite(mi_values) & np.isfinite(phase_correction_values)
        mi_phase_spearman = (
            float(spearmanr(mi_values[valid_mi], phase_correction_values[valid_mi]).statistic)
            if np.sum(valid_mi) >= 3
            else float("nan")
        )

        quadrant_weighted_shares = np.zeros((3, 4), dtype=float)
        for component_index in range(3):
            weights = absolute_charge_sum[active_mask]
            probabilities = quadrant_probabilities[..., component_index, :][active_mask]
            denominator = float(np.sum(weights))
            quadrant_weighted_shares[component_index] = (
                np.sum(probabilities * weights[:, None], axis=0) / denominator
                if denominator
                else np.nan
            )

        component_diagnostics = {}
        for component_index, component in enumerate(COMPONENTS):
            mask = active_mask
            component_diagnostics[component] = {
                "mutual_information_bits": finite_percentiles(
                    mutual_information[..., component_index][mask]
                ),
                "phase_coupling_covariance": finite_percentiles(
                    phase_coupling[..., component_index][mask]
                ),
                "amplitude_relation_covariance_V_per_m": finite_percentiles(
                    amplitude_relation_coupling[..., component_index][mask]
                ),
                "weighted_quadrant_shares": {
                    quadrant: float(quadrant_weighted_shares[component_index, quadrant_index])
                    for quadrant_index, quadrant in enumerate(QUADRANTS)
                },
            }

        representation_budget = {
            "flat_parent": "signed charge density plus one parent E vector",
            "independent_phase_marginals": (
                "per component: absolute-charge activity, common |E| amplitude, charge-sign mean, field-sign mean"
            ),
            "joint_quadrant_triangle": (
                "adds the four joint quadrant occupancies (three independent probabilities)"
            ),
            "conditioned_amplitude_pyramid": (
                "adds one conditional |E| mean for every occupied quadrant; identity ceiling"
            ),
        }

        results = {
            "test": "MX7 phase-first Information^3 / pyramid electric closure",
            "status": "post-MX4/MX5 closure autopsy; not independent ARA confirmation",
            "source": {
                "path": str(source),
                "bytes": source.stat().st_size,
                "sha256": observed_hash,
                "hash_match": observed_hash == EXPECTED_SOURCE_SHA256,
                "repository": "https://github.com/openPMD/openPMD-example-datasets",
                "archive": "legacy_datasets.tar.gz",
                "producer": "PIConGPU",
                "iteration": 200,
                "field_shape_zyx": list(field_shape),
                "grid_spacing_m": grid_spacing_xyz_m.tolist(),
                "cell_volume_m3": cell_volume,
                "snapshot_count": 1,
            },
            "data_quality": {
                "particle_counts": particle_counts,
                "active_interior_cells": int(np.sum(active_mask)),
                "exact_zero_field_component_counts": {
                    component: int(neutral_counts[index])
                    for index, component in enumerate(COMPONENTS)
                },
                "particle_component_neutral_fraction": float(
                    np.sum(neutral_counts) / total_particle_component_count
                ),
                "all_primary_arrays_finite_on_active_mask": bool(
                    all(
                        np.all(np.isfinite(array[active_mask]))
                        for array in (target, flat, first_moment, marginal, joint, pyramid)
                    )
                ),
                "analysis_interpolation": "trilinear with recorded Yee offsets; edge clamp",
                "analysis_deposition": "cloud-in-cell to integer grid positions",
                "recorded_particle_shape": float(iteration["particles/e"].attrs["particleShape"]),
            },
            "models": metrics,
            "joint_phase_result": {
                "classification": classification,
                "frozen_gates": frozen_gates,
                "spatial_sensitivity": half_metrics,
                "phase_correction_relative_l2_of_target": float(
                    np.linalg.norm(phase_correction[active_mask])
                    / np.linalg.norm(target[active_mask])
                ),
                "mutual_information_bits": finite_percentiles(mi_values),
                "spearman_mutual_information_vs_abs_phase_correction": mi_phase_spearman,
                "component_diagnostics": component_diagnostics,
            },
            "pyramid_identity": {
                "conditioned_quadrant_reconstruction_relative_l2": pyramid_error,
                "marginal_plus_phase_plus_amplitude_relative_l2": reassembly_error,
                "direct_deposition_crosscheck_relative_l2": direct_deposition_error,
                "all_identity_errors_le_1e-12": bool(
                    pyramid_error <= 1e-12
                    and reassembly_error <= 1e-12
                    and direct_deposition_error <= 1e-12
                ),
                "amplitude_correction_relative_l2_of_target": float(
                    np.linalg.norm(amplitude_correction[active_mask])
                    / np.linalg.norm(target[active_mask])
                ),
                "interpretation": (
                    "exact decompression ceiling: the post-joint residual is amplitude-relation covariance, not a prediction"
                ),
            },
            "representation_budget": representation_budget,
            "claim_boundary": {
                "supported": (
                    "Measures whether joint phase occupancy improves on separately compressed signs and whether the remaining residual is relation-conditioned amplitude."
                ),
                "not_supported": (
                    "Does not establish a new information theorem, a literal physical pyramid, universal fractality, or unseen time dynamics."
                ),
            },
        }

        arrays = {
            "active_mask": active_mask,
            "target": target,
            "flat": flat,
            "first_moment": first_moment,
            "marginal": marginal,
            "joint": joint,
            "pyramid": pyramid,
            "reassembled": reassembled,
            "absolute_charge_density": absolute_charge_density,
            "mean_magnitude": mean_magnitude,
            "charge_sign_mean": np.repeat(charge_sign_mean[..., None], 3, axis=-1),
            "field_sign_mean": field_sign_mean,
            "relation_sign_mean": relation_sign_mean,
            "phase_coupling": phase_coupling,
            "amplitude_relation_coupling": amplitude_relation_coupling,
            "phase_correction": phase_correction,
            "amplitude_correction": amplitude_correction,
            "mutual_information": mutual_information,
            "quadrant_probabilities": quadrant_probabilities,
            "quadrant_amplitudes": quadrant_amplitudes,
        }
        return results, arrays


def write_cells(path: Path, arrays: dict[str, np.ndarray]) -> None:
    fields = [
        "z", "y", "x", "component", "target_N_per_m3", "flat_N_per_m3",
        "first_moment_N_per_m3", "marginal_N_per_m3", "joint_N_per_m3",
        "pyramid_N_per_m3", "reassembled_N_per_m3", "absolute_charge_density_C_per_m3",
        "mean_abs_E_V_per_m", "charge_sign_mean", "field_sign_mean", "joint_sign_mean",
        "phase_coupling_covariance", "amplitude_relation_covariance_V_per_m",
        "phase_correction_N_per_m3", "amplitude_correction_N_per_m3", "mutual_information_bits",
    ]
    fields.extend([f"p_{quadrant}" for quadrant in QUADRANTS])
    fields.extend([f"mean_abs_E_{quadrant}_V_per_m" for quadrant in QUADRANTS])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        active_indices = np.argwhere(arrays["active_mask"])
        for z, y, x in active_indices:
            for component_index, component in enumerate(COMPONENTS):
                index = (z, y, x, component_index)
                row = {
                    "z": int(z), "y": int(y), "x": int(x), "component": component,
                    "target_N_per_m3": arrays["target"][index],
                    "flat_N_per_m3": arrays["flat"][index],
                    "first_moment_N_per_m3": arrays["first_moment"][index],
                    "marginal_N_per_m3": arrays["marginal"][index],
                    "joint_N_per_m3": arrays["joint"][index],
                    "pyramid_N_per_m3": arrays["pyramid"][index],
                    "reassembled_N_per_m3": arrays["reassembled"][index],
                    "absolute_charge_density_C_per_m3": arrays["absolute_charge_density"][z, y, x],
                    "mean_abs_E_V_per_m": arrays["mean_magnitude"][index],
                    "charge_sign_mean": arrays["charge_sign_mean"][index],
                    "field_sign_mean": arrays["field_sign_mean"][index],
                    "joint_sign_mean": arrays["relation_sign_mean"][index],
                    "phase_coupling_covariance": arrays["phase_coupling"][index],
                    "amplitude_relation_covariance_V_per_m": arrays["amplitude_relation_coupling"][index],
                    "phase_correction_N_per_m3": arrays["phase_correction"][index],
                    "amplitude_correction_N_per_m3": arrays["amplitude_correction"][index],
                    "mutual_information_bits": arrays["mutual_information"][index],
                }
                for quadrant_index, quadrant in enumerate(QUADRANTS):
                    row[f"p_{quadrant}"] = arrays["quadrant_probabilities"][index + (quadrant_index,)]
                    row[f"mean_abs_E_{quadrant}_V_per_m"] = arrays["quadrant_amplitudes"][index + (quadrant_index,)]
                writer.writerow(row)


def make_figure(path: Path, results: dict, arrays: dict[str, np.ndarray]) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    figure, axes = plt.subplots(2, 3, figsize=(16, 10), constrained_layout=True)
    model_order = (
        "flat_parent",
        "mx5_first_moment",
        "independent_phase_marginals",
        "joint_quadrant_triangle",
        "conditioned_amplitude_pyramid",
    )
    model_labels = ("flat", "first moment", "two marginals", "joint 4Q", "conditioned ceiling")
    colours = ("#777777", "#d28e2d", "#7f8c8d", "#3973ac", "#222222")
    metrics = results["models"]
    for axis, metric, title in (
        (axes[0, 0], "vector_correlation", "Vector correlation"),
        (axes[0, 1], "nrmse_by_target_std", "NRMSE by target standard deviation"),
        (axes[0, 2], "median_angular_error_deg", "Median directional error (degrees)"),
    ):
        values = [metrics[name][metric] for name in model_order]
        axis.bar(model_labels, values, color=colours)
        axis.set_title(title)
        axis.tick_params(axis="x", rotation=25)
        axis.set_ylim(bottom=0)
        for index, value in enumerate(values):
            axis.text(index, value, f"{value:.3g}", ha="center", va="bottom", fontsize=8)

    shares = np.mean(
        [
            [
                results["joint_phase_result"]["component_diagnostics"][component]["weighted_quadrant_shares"][quadrant]
                for quadrant in QUADRANTS
            ]
            for component in COMPONENTS
        ],
        axis=0,
    ).reshape(2, 2)
    image = axes[1, 0].imshow(shares, cmap="Blues", vmin=0, vmax=max(0.5, float(np.max(shares))))
    axes[1, 0].set_xticks((0, 1), labels=("Field A (+)", "Field B (−)"))
    axes[1, 0].set_yticks((0, 1), labels=("Charge A (+)", "Charge B (−)"))
    axes[1, 0].set_title("Weighted four-quadrant occupancy")
    for row in range(2):
        for column in range(2):
            axes[1, 0].text(column, row, f"{shares[row, column]:.3f}", ha="center", va="center")
    figure.colorbar(image, ax=axes[1, 0], label="share")

    active_components = np.repeat(arrays["active_mask"][..., None], 3, axis=-1)
    mi = arrays["mutual_information"][active_components]
    axes[1, 1].hist(mi[np.isfinite(mi)], bins=60, color="#3973ac", alpha=0.85)
    axes[1, 1].set(
        xlabel="mutual information between phase signs (bits)",
        ylabel="cell-components",
        title="Information carried by the joint relation",
    )

    z_mid = arrays["active_mask"].shape[0] // 2
    marginal_residual = np.linalg.norm(arrays["marginal"] - arrays["target"], axis=-1)
    joint_residual = np.linalg.norm(arrays["joint"] - arrays["target"], axis=-1)
    ratio = np.log10(
        np.maximum(joint_residual[z_mid], np.finfo(float).tiny)
        / np.maximum(marginal_residual[z_mid], np.finfo(float).tiny)
    )
    image = axes[1, 2].imshow(ratio, origin="lower", cmap="coolwarm", vmin=-1, vmax=1)
    axes[1, 2].set(
        xlabel="x cell",
        ylabel="y cell",
        title=f"log10(joint residual / marginal residual), z={z_mid}",
    )
    figure.colorbar(image, ax=axes[1, 2], label="negative = joint improvement")

    joint = metrics["joint_quadrant_triangle"]
    classification = results["joint_phase_result"]["classification"]
    figure.suptitle(
        "MX7 phase-first closure — "
        f"joint corr={joint['vector_correlation']:.3f}, NRMSE={joint['nrmse_by_target_std']:.3f}; "
        f"{classification}",
        fontsize=14,
    )
    figure.savefig(path, dpi=180)
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    results, arrays = run_analysis(args.source)
    results_path = args.output_dir / "MX7_PHASE_FIRST_INFORMATION3_PYRAMID_RESULTS.json"
    cells_path = args.output_dir / "MX7_PHASE_FIRST_INFORMATION3_PYRAMID_CELLS.csv"
    figure_path = args.output_dir / "MX7_PHASE_FIRST_INFORMATION3_PYRAMID.png"
    results_path.write_text(json.dumps(results, indent=2, allow_nan=False), encoding="utf-8")
    write_cells(cells_path, arrays)
    make_figure(figure_path, results, arrays)
    print(json.dumps({
        "results": str(results_path),
        "cells": str(cells_path),
        "figure": str(figure_path),
        "classification": results["joint_phase_result"]["classification"],
        "joint_metrics": {
            key: results["models"]["joint_quadrant_triangle"][key]
            for key in ("vector_correlation", "nrmse_by_target_std", "median_angular_error_deg", "relative_l2")
        },
        "pyramid_identity_pass": results["pyramid_identity"]["all_identity_errors_le_1e-12"],
    }, indent=2))


if __name__ == "__main__":
    main()
