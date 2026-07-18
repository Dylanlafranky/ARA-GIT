"""MX5 child-ARA / TE-ARA closure test on the MX4 PIConGPU snapshot.

Version A: exact child-ARA vector reassembly before deposition (identity check).
Version B: flat parent plus exact Other (identity check and diagnostics).
Version C: compressed first positional moment / field-gradient closure.

The protocol was frozen before this script was first executed.  Version C is
standard Taylor/moment closure mathematics expressed in ARA bookkeeping; it is
not represented as a new physical law.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import h5py
import matplotlib.pyplot as plt
import numpy as np

from mx4_lorentz_ara_crosswalk import (
    COMPONENTS,
    EXPECTED_SOURCE_SHA256,
    collocate_to_integer_grid,
    deposit_cic,
    load_fields,
    load_particle_species,
    percentile_dict,
    scalar_metrics,
    sha256,
    trilinear_sample,
    vector_metrics,
)


BASELINE = {
    "vector_correlation": 0.4770623591995614,
    "nrmse_by_target_std": 0.8878462480931429,
    "median_angular_error_deg": 61.67518108939487,
}


def relative_l2(target: np.ndarray, estimate: np.ndarray, mask: np.ndarray) -> float:
    target_values = np.asarray(target, dtype=float)[mask]
    estimate_values = np.asarray(estimate, dtype=float)[mask]
    denominator = float(np.linalg.norm(target_values))
    return (
        float(np.linalg.norm(estimate_values - target_values) / denominator)
        if denominator
        else float("nan")
    )


def deposit_cic_first_moments(
    coordinates_xyz: np.ndarray,
    macro_charge: np.ndarray,
    velocity_xyz: np.ndarray,
    grid_shape_zyx: tuple[int, int, int],
    grid_spacing_xyz_m: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Deposit charge and current first positional moments to CIC nodes.

    Returns P_rho[..., displacement_axis] and
    M_J[..., displacement_axis, current_component].
    """
    nz, ny, nx = grid_shape_zyx
    n_cells = nx * ny * nz
    base = np.floor(coordinates_xyz).astype(np.int64)
    frac = coordinates_xyz - base
    p_rho = np.zeros((n_cells, 3), dtype=float)
    m_j = np.zeros((n_cells, 3, 3), dtype=float)

    for dx in (0, 1):
        wx = (1.0 - frac[:, 0]) if dx == 0 else frac[:, 0]
        ix = base[:, 0] + dx
        for dy in (0, 1):
            wy = (1.0 - frac[:, 1]) if dy == 0 else frac[:, 1]
            iy = base[:, 1] + dy
            for dz in (0, 1):
                wz = (1.0 - frac[:, 2]) if dz == 0 else frac[:, 2]
                iz = base[:, 2] + dz
                keep = (
                    (ix >= 0)
                    & (ix < nx)
                    & (iy >= 0)
                    & (iy < ny)
                    & (iz >= 0)
                    & (iz < nz)
                )
                if not np.any(keep):
                    continue

                flat_index = ((iz[keep] * ny + iy[keep]) * nx + ix[keep]).astype(int)
                cic_weight = (wx * wy * wz)[keep]
                corner_xyz = np.column_stack((ix[keep], iy[keep], iz[keep]))
                delta_m = (
                    coordinates_xyz[keep] - corner_xyz
                ) * grid_spacing_xyz_m[None, :]
                charge_weight = macro_charge[keep] * cic_weight

                for displacement_axis in range(3):
                    coefficient = charge_weight * delta_m[:, displacement_axis]
                    p_rho[:, displacement_axis] += np.bincount(
                        flat_index, weights=coefficient, minlength=n_cells
                    )
                    for component in range(3):
                        m_j[:, displacement_axis, component] += np.bincount(
                            flat_index,
                            weights=coefficient * velocity_xyz[keep, component],
                            minlength=n_cells,
                        )

    return (
        p_rho.reshape(grid_shape_zyx + (3,)),
        m_j.reshape(grid_shape_zyx + (3, 3)),
    )


def physical_vector_gradients(
    vector_zyx: np.ndarray, grid_spacing_xyz_m: np.ndarray
) -> np.ndarray:
    """Return gradients[physical_axis_xyz, z, y, x, vector_component]."""
    gradients = np.zeros((3,) + vector_zyx.shape, dtype=float)
    spacing_x, spacing_y, spacing_z = grid_spacing_xyz_m
    for component in range(3):
        dz, dy, dx = np.gradient(
            vector_zyx[..., component], spacing_z, spacing_y, spacing_x
        )
        gradients[0, ..., component] = dx
        gradients[1, ..., component] = dy
        gradients[2, ..., component] = dz
    return gradients


def finite_percentile(values: np.ndarray) -> dict[str, float]:
    return percentile_dict(np.asarray(values, dtype=float))


def channel_angle(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    magnitude_a = np.linalg.norm(a, axis=-1)
    magnitude_b = np.linalg.norm(b, axis=-1)
    angle = np.full(magnitude_a.shape, np.nan, dtype=float)
    valid = (magnitude_a > 0) & (magnitude_b > 0)
    cosine = np.sum(a[valid] * b[valid], axis=-1) / (
        magnitude_a[valid] * magnitude_b[valid]
    )
    angle[valid] = np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))
    return angle


def improvement_fraction(metric: str, new_value: float) -> float:
    baseline = BASELINE[metric]
    if metric == "vector_correlation":
        return (new_value - baseline) / abs(baseline)
    return (baseline - new_value) / abs(baseline)


def classify_first_moment(metrics: dict) -> tuple[str, dict]:
    comparison = {
        key: {
            "mx4_flat_baseline": BASELINE[key],
            "mx5_first_moment": float(metrics[key]),
            "favourable_relative_improvement": improvement_fraction(
                key, float(metrics[key])
            ),
        }
        for key in BASELINE
    }
    all_better = all(
        comparison[key]["favourable_relative_improvement"] > 0 for key in BASELINE
    )
    useful = (
        metrics["vector_correlation"] >= 0.70
        and metrics["nrmse_by_target_std"] <= 0.70
        and metrics["median_angular_error_deg"] <= 45.0
        and all_better
    )
    improved_five_percent = sum(
        comparison[key]["favourable_relative_improvement"] >= 0.05
        for key in BASELINE
    )
    if useful:
        classification = "useful compact recovery"
    elif improved_five_percent >= 2:
        classification = "partial compact recovery"
    else:
        classification = "not recovered by this first-moment closure"
    return classification, comparison


def run_analysis(source: Path) -> tuple[dict, dict]:
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
                collocate_to_integer_grid(fields["E"][c], offsets["E"][c])
                for c in COMPONENTS
            ],
            axis=-1,
        )
        b_parent = np.stack(
            [
                collocate_to_integer_grid(fields["B"][c], offsets["B"][c])
                for c in COMPONENTS
            ],
            axis=-1,
        )

        # charge, current xyz, child electric xyz, child magnetic xyz,
        # exact ARA-reassembled total xyz, child activity, occupancy
        deposited = np.zeros(field_shape + (15,), dtype=float)
        p_rho_total = np.zeros(field_shape + (3,), dtype=float)
        m_j_total = np.zeros(field_shape + (3, 3), dtype=float)
        species_rho: dict[str, np.ndarray] = {}
        species_child_force: dict[str, np.ndarray] = {}
        species_child_activity: dict[str, np.ndarray] = {}
        particle_counts: dict[str, int] = {}
        particle_version_a_errors: dict[str, float] = {}

        for species_name in ("e", "i"):
            particles = load_particle_species(iteration, species_name)
            coordinates = particles["coordinates"]
            velocity = particles["velocity"]
            weighting = particles["weighting"]
            charge = particles["charge"]
            particle_counts[species_name] = int(len(coordinates))

            e_particle = np.column_stack(
                [
                    trilinear_sample(fields["E"][c], coordinates, offsets["E"][c])
                    for c in COMPONENTS
                ]
            )
            b_particle = np.column_stack(
                [
                    trilinear_sample(fields["B"][c], coordinates, offsets["B"][c])
                    for c in COMPONENTS
                ]
            )
            force_e = charge * e_particle
            force_b = charge * np.cross(velocity, b_particle)
            force_total = force_e + force_b
            magnitude_e = np.linalg.norm(force_e, axis=1)
            magnitude_b = np.linalg.norm(force_b, axis=1)
            activity = magnitude_e + magnitude_b

            x_channel = np.zeros(len(activity), dtype=float)
            valid_activity = activity > 0
            x_channel[valid_activity] = (
                2.0 * magnitude_b[valid_activity] / activity[valid_activity]
            )
            unit_e = np.zeros_like(force_e)
            unit_b = np.zeros_like(force_b)
            valid_e = magnitude_e > 0
            valid_b = magnitude_b > 0
            unit_e[valid_e] = force_e[valid_e] / magnitude_e[valid_e, None]
            unit_b[valid_b] = force_b[valid_b] / magnitude_b[valid_b, None]
            ara_reassembled = 0.5 * activity[:, None] * (
                (2.0 - x_channel)[:, None] * unit_e
                + x_channel[:, None] * unit_b
            )
            particle_version_a_errors[species_name] = float(
                np.linalg.norm(ara_reassembled - force_total)
                / np.linalg.norm(force_total)
            )

            macro_charge = weighting * charge
            deposited_values = np.column_stack(
                [
                    macro_charge,
                    macro_charge[:, None] * velocity,
                    weighting[:, None] * force_e,
                    weighting[:, None] * force_b,
                    weighting[:, None] * ara_reassembled,
                    weighting * activity,
                    np.ones(len(coordinates)),
                ]
            )
            species_deposit = deposit_cic(coordinates, deposited_values, field_shape)
            deposited += species_deposit
            species_rho[species_name] = species_deposit[..., 0] / cell_volume
            species_child_force[species_name] = (
                species_deposit[..., 4:7] + species_deposit[..., 7:10]
            ) / cell_volume
            species_child_activity[species_name] = (
                species_deposit[..., 13] / cell_volume
            )

            p_rho, m_j = deposit_cic_first_moments(
                coordinates,
                macro_charge,
                velocity,
                field_shape,
                grid_spacing_xyz_m,
            )
            p_rho_total += p_rho
            m_j_total += m_j

        rho_parent = deposited[..., 0] / cell_volume
        current_parent = deposited[..., 1:4] / cell_volume
        child_e = deposited[..., 4:7] / cell_volume
        child_b = deposited[..., 7:10] / cell_volume
        child_total = child_e + child_b
        child_ara = deposited[..., 10:13] / cell_volume
        child_activity = deposited[..., 13] / cell_volume
        occupancy = deposited[..., 14]
        p_rho_total /= cell_volume
        m_j_total /= cell_volume

        flat_e = rho_parent[..., None] * e_parent
        flat_b = np.cross(current_parent, b_parent)
        flat_total = flat_e + flat_b
        other_e = child_e - flat_e
        other_b = child_b - flat_b
        other_total = other_e + other_b
        exact_recovered = flat_total + other_total

        gradients_e = physical_vector_gradients(e_parent, grid_spacing_xyz_m)
        gradients_b = physical_vector_gradients(b_parent, grid_spacing_xyz_m)
        predicted_other_e = np.zeros_like(child_e)
        predicted_other_b = np.zeros_like(child_b)
        for axis in range(3):
            predicted_other_e += p_rho_total[..., axis, None] * gradients_e[axis]
            predicted_other_b += np.cross(
                m_j_total[..., axis, :], gradients_b[axis]
            )
        first_moment_e = flat_e + predicted_other_e
        first_moment_b = flat_b + predicted_other_b
        first_moment_total = first_moment_e + first_moment_b

        interior = np.zeros(field_shape, dtype=bool)
        interior[1:-1, 1:-1, 1:-1] = True
        active_mask = interior & (occupancy > 0)

        activity_safe = np.where(child_activity > 0, child_activity, np.nan)
        te_force_coherence = 2.0 * np.linalg.norm(child_total, axis=-1) / activity_safe
        other_magnitude = np.linalg.norm(other_total, axis=-1)
        flat_magnitude = np.linalg.norm(flat_total, axis=-1)
        parent_other_denominator = flat_magnitude + other_magnitude
        x_other = np.divide(
            2.0 * other_magnitude,
            parent_other_denominator,
            out=np.full(field_shape, np.nan, dtype=float),
            where=parent_other_denominator > 0,
        )
        other_e_magnitude = np.linalg.norm(other_e, axis=-1)
        other_b_magnitude = np.linalg.norm(other_b, axis=-1)
        other_channel_denominator = other_e_magnitude + other_b_magnitude
        x_other_b = np.divide(
            2.0 * other_b_magnitude,
            other_channel_denominator,
            out=np.full(field_shape, np.nan, dtype=float),
            where=other_channel_denominator > 0,
        )
        other_channel_angle = channel_angle(other_e, other_b)

        species_te_force = {}
        for species_name in ("e", "i"):
            species_activity_safe = np.where(
                species_child_activity[species_name] > 0,
                species_child_activity[species_name],
                np.nan,
            )
            species_te_force[species_name] = (
                2.0
                * np.linalg.norm(species_child_force[species_name], axis=-1)
                / species_activity_safe
            )
        species_e_magnitude = np.linalg.norm(species_child_force["e"], axis=-1)
        species_i_magnitude = np.linalg.norm(species_child_force["i"], axis=-1)
        species_pair_denominator = species_e_magnitude + species_i_magnitude
        te_species_pair = np.divide(
            2.0 * np.linalg.norm(
                species_child_force["e"] + species_child_force["i"], axis=-1
            ),
            species_pair_denominator,
            out=np.full(field_shape, np.nan, dtype=float),
            where=species_pair_denominator > 0,
        )
        x_species_ion = np.divide(
            2.0 * species_i_magnitude,
            species_pair_denominator,
            out=np.full(field_shape, np.nan, dtype=float),
            where=species_pair_denominator > 0,
        )
        species_pair_angle = channel_angle(
            species_child_force["e"], species_child_force["i"]
        )

        version_a_relative_l2 = relative_l2(child_total, child_ara, active_mask)
        version_b_relative_l2 = relative_l2(
            child_total, exact_recovered, active_mask
        )
        flat_metrics = {
            "electric": vector_metrics(child_e, flat_e, active_mask),
            "magnetic": vector_metrics(child_b, flat_b, active_mask),
            "total": vector_metrics(child_total, flat_total, active_mask),
        }
        first_moment_metrics = {
            "electric": vector_metrics(child_e, first_moment_e, active_mask),
            "magnetic": vector_metrics(child_b, first_moment_b, active_mask),
            "total": vector_metrics(child_total, first_moment_total, active_mask),
        }
        exact_other_prediction_metrics = {
            "electric": vector_metrics(other_e, predicted_other_e, active_mask),
            "magnetic": vector_metrics(other_b, predicted_other_b, active_mask),
            "total": vector_metrics(other_total, predicted_other_e + predicted_other_b, active_mask),
        }
        classification, comparison = classify_first_moment(
            first_moment_metrics["total"]
        )

        lower_mask = active_mask.copy()
        lower_mask[field_shape[0] // 2 :] = False
        upper_mask = active_mask.copy()
        upper_mask[: field_shape[0] // 2] = False
        spatial_sensitivity = {
            "lower_z_half": {
                "n_cells": int(np.sum(lower_mask)),
                "flat": vector_metrics(child_total, flat_total, lower_mask),
                "first_moment": vector_metrics(
                    child_total, first_moment_total, lower_mask
                ),
            },
            "upper_z_half": {
                "n_cells": int(np.sum(upper_mask)),
                "flat": vector_metrics(child_total, flat_total, upper_mask),
                "first_moment": vector_metrics(
                    child_total, first_moment_total, upper_mask
                ),
            },
        }

        recorded_rho = {
            species: iteration[f"fields/{species}_chargeDensity"][...].astype(float)
            * float(iteration[f"fields/{species}_chargeDensity"].attrs["unitSI"])
            for species in ("e", "i")
        }
        charge_density_validation = {
            species: scalar_metrics(
                recorded_rho[species], species_rho[species], active_mask
            )
            for species in ("e", "i")
        }
        charge_density_validation["total"] = scalar_metrics(
            recorded_rho["e"] + recorded_rho["i"], rho_parent, active_mask
        )

        te_active = te_force_coherence[active_mask]
        x_other_active = x_other[active_mask]
        te_bands = {
            "low_lt_0_1": te_active < 0.1,
            "middle_0_1_to_1": (te_active >= 0.1) & (te_active < 1.0),
            "high_ge_1": te_active >= 1.0,
        }
        diagnostics = {
            "te_force_coherence": finite_percentile(te_active),
            "te_force_coherence_definition": "2*|F_child|/sum_child(|f_E|+|f_B|)",
            "te_force_coherence_outside_0_2_count": int(
                np.sum((te_active < -1e-12) | (te_active > 2.0 + 1e-12))
            ),
            "te_force_coherence_fraction_lt_0_1": float(np.mean(te_active < 0.1)),
            "te_force_coherence_fraction_ge_1": float(np.mean(te_active >= 1.0)),
            "x_other_median_by_te_force_band": {
                name: float(np.median(x_other_active[band])) if np.any(band) else None
                for name, band in te_bands.items()
            },
            "species_internal_te_force_coherence": {
                species: finite_percentile(species_te_force[species][active_mask])
                for species in ("e", "i")
            },
            "species_pair_te_force_coherence": finite_percentile(
                te_species_pair[active_mask]
            ),
            "species_pair_te_definition": (
                "2*|F_e_child+F_i_child|/(|F_e_child|+|F_i_child|) at the parent cell"
            ),
            "species_pair_ion_coordinate": finite_percentile(
                x_species_ion[active_mask]
            ),
            "species_pair_angle_deg": finite_percentile(
                species_pair_angle[active_mask]
            ),
            "species_decomposition_status": (
                "post-freeze descriptive drill added after the combined TE-force distribution was inspected; "
                "not an outcome gate"
            ),
            "x_other": finite_percentile(x_other_active),
            "x_other_definition": "2*|Other|/(|flat parent|+|Other|)",
            "fraction_other_dominant_x_gt_1": float(
                np.mean(x_other_active > 1.0)
            ),
            "x_other_b_channel": finite_percentile(x_other_b[active_mask]),
            "other_e_b_angle_deg": finite_percentile(
                other_channel_angle[active_mask]
            ),
            "warning": (
                "These are dimensionless force/activity diagnostics, not joules. "
                "x_other is magnitude-only and is not an additive energy percentage."
            ),
        }

        results = {
            "test": "MX5 child-ARA / TE-ARA closure",
            "status": "post-MX4 development follow-up; protocol frozen before MX5 outcomes",
            "source": {
                "path": str(source),
                "bytes": int(source.stat().st_size),
                "sha256": observed_hash,
                "repository": "https://github.com/openPMD/openPMD-example-datasets",
                "iteration": 200,
                "field_shape_zyx": list(field_shape),
                "grid_spacing_xyz_m": grid_spacing_xyz_m.tolist(),
                "cell_volume_m3": cell_volume,
                "snapshot_count": 1,
                "particle_counts": particle_counts,
            },
            "data_quality": {
                "hash_match": True,
                "all_derived_arrays_finite_on_active_mask": bool(
                    all(
                        np.all(np.isfinite(array[active_mask]))
                        for array in (
                            child_total,
                            flat_total,
                            first_moment_total,
                            other_total,
                        )
                    )
                ),
                "analysis_interpolation": "trilinear with recorded Yee offsets; edge clamp",
                "analysis_deposition": "cloud-in-cell to integer grid positions",
                "recorded_particle_shape": float(
                    iteration["particles/e"].attrs["particleShape"]
                ),
                "charge_density_validation": charge_density_validation,
                "active_interior_cells": int(np.sum(active_mask)),
            },
            "version_a_exact_child_ara": {
                "description": "retain both child channel vectors and reassemble before CIC deposition",
                "particle_relative_l2_by_species": particle_version_a_errors,
                "grid_relative_l2": version_a_relative_l2,
                "gate_le_1e-12": bool(version_a_relative_l2 <= 1e-12),
                "interpretation": "identity/decompression check only",
            },
            "version_b_parent_plus_exact_other": {
                "description": "flat parent + exact child-minus-parent Other",
                "grid_relative_l2": version_b_relative_l2,
                "gate_le_1e-12": bool(version_b_relative_l2 <= 1e-12),
                "diagnostics": diagnostics,
                "interpretation": "identity check and measurement of omitted relation; not a prediction",
            },
            "version_c_first_moment_gradient": {
                "description": "unfitted first positional moments times local parent-field gradients",
                "channels": first_moment_metrics,
                "predicted_other_vs_exact_other": exact_other_prediction_metrics,
                "classification": classification,
                "comparison_to_frozen_mx4": comparison,
                "spatial_sensitivity": spatial_sensitivity,
                "interpretation": (
                    "standard first-order Taylor/moment closure expressed as child/parent/Other bookkeeping"
                ),
            },
            "flat_parent_recalculation": {
                "channels": flat_metrics,
                "frozen_mx4_total_reference": BASELINE,
            },
            "limitations": [
                "one public simulation snapshot and one plasma configuration",
                "no time-resolved momentum-change/acceleration confirmation",
                "CIC analysis operator differs from the source's recorded quadratic particle shape",
                "Versions A and B are identities retaining or defining the missing information",
                "Version C is an unfitted first-order closure, not an ARA-specific new law",
            ],
            "claim_boundary": (
                "The test can assess bookkeeping and compact closure performance on this snapshot. "
                "It cannot by itself prove universal ARA geometry or new plasma physics."
            ),
        }

        arrays = {
            "active_mask": active_mask,
            "occupancy": occupancy,
            "child_activity": child_activity,
            "te_force_coherence": te_force_coherence,
            "x_other": x_other,
            "x_other_b": x_other_b,
            "other_channel_angle": other_channel_angle,
            "te_species_pair": te_species_pair,
            "te_species_e": species_te_force["e"],
            "te_species_i": species_te_force["i"],
            "x_species_ion": x_species_ion,
            "species_pair_angle": species_pair_angle,
            "child_total": child_total,
            "child_e": child_e,
            "child_b": child_b,
            "child_ara": child_ara,
            "flat_total": flat_total,
            "flat_e": flat_e,
            "flat_b": flat_b,
            "other_total": other_total,
            "other_e": other_e,
            "other_b": other_b,
            "predicted_other_total": predicted_other_e + predicted_other_b,
            "predicted_other_e": predicted_other_e,
            "predicted_other_b": predicted_other_b,
            "first_moment_total": first_moment_total,
            "first_moment_e": first_moment_e,
            "first_moment_b": first_moment_b,
        }
        return results, arrays


def write_grid_csv(path: Path, arrays: dict) -> None:
    scalar_columns = (
        "occupancy",
        "child_activity",
        "te_force_coherence",
        "x_other",
        "x_other_b",
        "other_channel_angle",
        "te_species_pair",
        "x_species_ion",
        "species_pair_angle",
    )
    vector_columns = (
        "child_total",
        "child_e",
        "child_b",
        "child_ara",
        "flat_total",
        "flat_e",
        "flat_b",
        "other_total",
        "other_e",
        "other_b",
        "predicted_other_total",
        "predicted_other_e",
        "predicted_other_b",
        "first_moment_total",
        "first_moment_e",
        "first_moment_b",
    )
    active = arrays["active_mask"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        header = ["z_index", "y_index", "x_index", "active_interior"]
        header.extend(scalar_columns)
        for name in vector_columns:
            header.extend([f"{name}_{component}" for component in COMPONENTS])
        writer.writerow(header)
        for z, y, x in np.ndindex(active.shape):
            row = [z, y, x, int(active[z, y, x])]
            row.extend(float(arrays[name][z, y, x]) for name in scalar_columns)
            for name in vector_columns:
                row.extend(float(value) for value in arrays[name][z, y, x])
            writer.writerow(row)


def make_figure(path: Path, results: dict, arrays: dict) -> None:
    mask = arrays["active_mask"]
    te_force = arrays["te_force_coherence"][mask]
    x_other = arrays["x_other"][mask]
    target = arrays["child_total"][mask]
    flat = arrays["flat_total"][mask]
    first = arrays["first_moment_total"][mask]
    target_magnitude = np.linalg.norm(target, axis=1)
    flat_magnitude = np.linalg.norm(flat, axis=1)
    first_magnitude = np.linalg.norm(first, axis=1)

    figure, axes = plt.subplots(2, 2, figsize=(13, 10), constrained_layout=True)
    bins = np.linspace(0, 2, 81)
    for values, colour, label in (
        (te_force, "#111111", "all particles"),
        (arrays["te_species_pair"][mask], "#9467bd", "electron/ion pair"),
        (arrays["te_species_e"][mask], "#2878b5", "electrons internally"),
        (arrays["te_species_i"][mask], "#d95f02", "ions internally"),
    ):
        axes[0, 0].hist(
            values[np.isfinite(values)], bins=bins, density=True,
            histtype="step", linewidth=2, color=colour, label=label
        )
    axes[0, 0].axvline(1.0, color="black", linestyle="--", linewidth=1)
    axes[0, 0].set(
        xlabel=r"TE-ARA force coherence $T^F=2|F_{child}|/A$",
        ylabel="density",
        title="TE-ARA separates internal and paired coherence",
    )
    axes[0, 0].legend(fontsize=8)

    axes[0, 1].hist(x_other[np.isfinite(x_other)], bins=np.linspace(0, 2, 81), color="#d95f02", alpha=0.85)
    axes[0, 1].axvline(1.0, color="black", linestyle="--", linewidth=1)
    fraction = results["version_b_parent_plus_exact_other"]["diagnostics"]["fraction_other_dominant_x_gt_1"]
    axes[0, 1].set(
        xlabel=r"Parent/Other coordinate $x_O$",
        ylabel="active grid cells",
        title=f"Exact Other dominates magnitude in {fraction:.1%} of cells",
    )

    positive = (target_magnitude > 0) & (flat_magnitude > 0) & (first_magnitude > 0)
    axes[1, 0].loglog(target_magnitude[positive], flat_magnitude[positive], ".", alpha=0.18, markersize=3, label="flat parent")
    axes[1, 0].loglog(target_magnitude[positive], first_magnitude[positive], ".", alpha=0.18, markersize=3, label="first moment")
    bounds = [
        min(float(np.min(target_magnitude[positive])), float(np.min(flat_magnitude[positive])), float(np.min(first_magnitude[positive]))),
        max(float(np.max(target_magnitude[positive])), float(np.max(flat_magnitude[positive])), float(np.max(first_magnitude[positive]))),
    ]
    axes[1, 0].plot(bounds, bounds, "k--", linewidth=1)
    axes[1, 0].set(
        xlabel=r"child-first $|F|$ [N m$^{-3}$]",
        ylabel=r"estimate $|F|$ [N m$^{-3}$]",
        title="Does a compressed child moment repair the parent?",
    )
    axes[1, 0].legend()

    z_mid = arrays["active_mask"].shape[0] // 2
    flat_residual = np.linalg.norm(arrays["flat_total"] - arrays["child_total"], axis=-1)
    first_residual = np.linalg.norm(arrays["first_moment_total"] - arrays["child_total"], axis=-1)
    ratio = np.log10(
        np.maximum(first_residual[z_mid], np.finfo(float).tiny)
        / np.maximum(flat_residual[z_mid], np.finfo(float).tiny)
    )
    image = axes[1, 1].imshow(ratio, origin="lower", cmap="coolwarm", vmin=-1, vmax=1)
    axes[1, 1].set(
        xlabel="x cell",
        ylabel="y cell",
        title=f"log10(first-moment residual / flat residual), z={z_mid}",
    )
    figure.colorbar(image, ax=axes[1, 1], label="negative = improvement")

    total = results["version_c_first_moment_gradient"]["channels"]["total"]
    figure.suptitle(
        "MX5 child-ARA / TE-ARA closure: "
        f"first-moment corr={total['vector_correlation']:.3f}, "
        f"NRMSE={total['nrmse_by_target_std']:.3f}",
        fontsize=15,
    )
    figure.savefig(path, dpi=180)
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument(
        "--output-dir", type=Path, default=Path(__file__).resolve().parent
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    results, arrays = run_analysis(args.source)
    results_path = args.output_dir / "MX5_CHILD_ARA_TEARA_CLOSURE_RESULTS.json"
    grid_path = args.output_dir / "MX5_CHILD_ARA_TEARA_GRID_CELLS.csv"
    figure_path = args.output_dir / "MX5_CHILD_ARA_TEARA_CLOSURE.png"
    results_path.write_text(
        json.dumps(results, indent=2, allow_nan=False), encoding="utf-8"
    )
    write_grid_csv(grid_path, arrays)
    make_figure(figure_path, results, arrays)
    print(json.dumps(results, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
