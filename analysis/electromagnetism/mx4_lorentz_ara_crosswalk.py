"""MX4 Lorentz-force <-> ARA crosswalk on a public PIConGPU snapshot.

This is a development/recovery test.  It evaluates:

1. an exact per-particle two-channel ARA reparameterisation of Lorentz force;
2. electric versus magnetic work identities;
3. preservation of the force relation under a declared particle-to-grid
   cloud-in-cell coarse-graining operator.

It does not infer particle acceleration because the public source contains one
time snapshot only.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import h5py
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr


EXPECTED_SOURCE_SHA256 = (
    "6f2cd696312c7dcec4567463ef45fd61b5343a06983add505b9c4b7234ae1db5"
)
COMPONENTS = ("x", "y", "z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def as_text(value) -> str:
    if isinstance(value, (bytes, np.bytes_)):
        return value.decode("utf-8")
    return str(value)


def percentile_dict(values: np.ndarray) -> dict[str, float]:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    levels = (0, 1, 5, 25, 50, 75, 95, 99, 100)
    if not len(values):
        return {f"p{level}": float("nan") for level in levels}
    result = np.percentile(values, levels)
    return {f"p{level}": float(value) for level, value in zip(levels, result)}


def pearson(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=float).ravel()
    b = np.asarray(b, dtype=float).ravel()
    keep = np.isfinite(a) & np.isfinite(b)
    a = a[keep]
    b = b[keep]
    if len(a) < 3 or np.std(a) == 0 or np.std(b) == 0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def trilinear_sample(
    array_zyx: np.ndarray,
    coordinates_xyz: np.ndarray,
    component_offset_xyz: np.ndarray,
) -> np.ndarray:
    """Sample one Yee component with edge-clamped trilinear interpolation."""
    nz, ny, nx = array_zyx.shape
    shape_xyz = np.array([nx, ny, nz], dtype=int)
    u = coordinates_xyz - np.asarray(component_offset_xyz, dtype=float)
    lower = np.floor(u).astype(np.int64)
    frac = u - lower

    below = u <= 0.0
    above = u >= (shape_xyz - 1)
    lower = np.clip(lower, 0, shape_xyz - 2)
    frac = np.where(below, 0.0, frac)
    frac = np.where(above, 1.0, frac)

    result = np.zeros(len(coordinates_xyz), dtype=float)
    for dx in (0, 1):
        wx = (1.0 - frac[:, 0]) if dx == 0 else frac[:, 0]
        ix = lower[:, 0] + dx
        for dy in (0, 1):
            wy = (1.0 - frac[:, 1]) if dy == 0 else frac[:, 1]
            iy = lower[:, 1] + dy
            for dz in (0, 1):
                wz = (1.0 - frac[:, 2]) if dz == 0 else frac[:, 2]
                iz = lower[:, 2] + dz
                result += wx * wy * wz * array_zyx[iz, iy, ix]
    return result


def collocate_to_integer_grid(
    array_zyx: np.ndarray, component_offset_xyz: np.ndarray
) -> np.ndarray:
    """Linearly collocate a Yee component to integer-position grid points."""
    output = np.asarray(array_zyx, dtype=float)
    axis_for_xyz = (2, 1, 0)
    for offset, axis in zip(component_offset_xyz, axis_for_xyz):
        if math.isclose(float(offset), 0.0, abs_tol=1e-12):
            continue
        if not math.isclose(float(offset), 0.5, abs_tol=1e-12):
            raise ValueError(f"Unsupported Yee offset {offset}; expected 0 or 0.5")
        previous = np.take(output, np.maximum(np.arange(output.shape[axis]) - 1, 0), axis=axis)
        output = 0.5 * (output + previous)
    return output


def deposit_cic(
    coordinates_xyz: np.ndarray,
    values: np.ndarray,
    grid_shape_zyx: tuple[int, int, int],
) -> np.ndarray:
    """Deposit one or more particle values to integer grid points via CIC."""
    values = np.asarray(values, dtype=float)
    if values.ndim == 1:
        values = values[:, None]
    nz, ny, nx = grid_shape_zyx
    n_cells = nx * ny * nz
    base = np.floor(coordinates_xyz).astype(np.int64)
    frac = coordinates_xyz - base
    output = np.zeros((n_cells, values.shape[1]), dtype=float)

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
                weights = (wx * wy * wz)[keep]
                flat_index = ((iz[keep] * ny + iy[keep]) * nx + ix[keep]).astype(int)
                for column in range(values.shape[1]):
                    output[:, column] += np.bincount(
                        flat_index,
                        weights=weights * values[keep, column],
                        minlength=n_cells,
                    )
    return output.reshape(grid_shape_zyx + (values.shape[1],))


def vector_metrics(target: np.ndarray, estimate: np.ndarray, mask: np.ndarray) -> dict:
    target = np.asarray(target, dtype=float)[mask]
    estimate = np.asarray(estimate, dtype=float)[mask]
    target_flat = target.ravel()
    estimate_flat = estimate.ravel()
    error_flat = estimate_flat - target_flat

    dot = float(np.dot(target_flat, estimate_flat))
    target_norm = float(np.linalg.norm(target_flat))
    estimate_norm = float(np.linalg.norm(estimate_flat))
    vector_correlation = dot / (target_norm * estimate_norm) if target_norm and estimate_norm else float("nan")
    target_std = float(np.std(target_flat))
    nrmse = float(np.sqrt(np.mean(error_flat**2)) / target_std) if target_std else float("nan")

    target_magnitude = np.linalg.norm(target, axis=1)
    estimate_magnitude = np.linalg.norm(estimate, axis=1)
    scale = max(float(np.max(target_magnitude)), float(np.max(estimate_magnitude)), np.finfo(float).tiny)
    active = (target_magnitude > scale * 1e-12) & (estimate_magnitude > scale * 1e-12)
    cosine = np.full(len(target), np.nan)
    cosine[active] = np.sum(target[active] * estimate[active], axis=1) / (
        target_magnitude[active] * estimate_magnitude[active]
    )
    angle = np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))

    return {
        "n_cells": int(len(target)),
        "vector_correlation": float(vector_correlation),
        "flattened_pearson": pearson(target_flat, estimate_flat),
        "component_pearson": {
            component: pearson(target[:, index], estimate[:, index])
            for index, component in enumerate(COMPONENTS)
        },
        "nrmse_by_target_std": nrmse,
        "l2_magnitude_ratio": estimate_norm / target_norm if target_norm else float("nan"),
        "median_angular_error_deg": float(np.nanmedian(angle)),
        "p95_angular_error_deg": float(np.nanpercentile(angle, 95)),
        "target_magnitude": percentile_dict(target_magnitude),
        "estimate_magnitude": percentile_dict(estimate_magnitude),
        "residual_magnitude": percentile_dict(np.linalg.norm(estimate - target, axis=1)),
    }


def scalar_metrics(target: np.ndarray, estimate: np.ndarray, mask: np.ndarray) -> dict:
    target = np.asarray(target, dtype=float)[mask]
    estimate = np.asarray(estimate, dtype=float)[mask]
    error = estimate - target
    std = float(np.std(target))
    return {
        "n_cells": int(len(target)),
        "pearson": pearson(target, estimate),
        "nrmse_by_target_std": float(np.sqrt(np.mean(error**2)) / std) if std else float("nan"),
        "l2_magnitude_ratio": float(np.linalg.norm(estimate) / np.linalg.norm(target))
        if np.linalg.norm(target)
        else float("nan"),
    }


def load_fields(iteration: h5py.Group) -> tuple[dict, dict]:
    fields = iteration["fields"]
    arrays: dict[str, dict[str, np.ndarray]] = {"E": {}, "B": {}}
    offsets: dict[str, dict[str, np.ndarray]] = {"E": {}, "B": {}}
    for field_name in ("E", "B"):
        for component in COMPONENTS:
            dataset = fields[f"{field_name}/{component}"]
            arrays[field_name][component] = dataset[...].astype(float) * float(dataset.attrs["unitSI"])
            offsets[field_name][component] = np.asarray(dataset.attrs["position"], dtype=float)
    return arrays, offsets


def load_particle_species(iteration: h5py.Group, species: str) -> dict:
    group = iteration[f"particles/{species}"]
    weighting = group["weighting"][...].astype(float) * float(group["weighting"].attrs["unitSI"])
    coordinates = np.column_stack(
        [
            group[f"positionOffset/{component}"][...].astype(float)
            + group[f"position/{component}"][...].astype(float)
            for component in COMPONENTS
        ]
    )

    momentum_raw = np.column_stack(
        [group[f"momentum/{component}"][...].astype(float) for component in COMPONENTS]
    )
    momentum_unit = float(group["momentum/x"].attrs["unitSI"])
    momentum = momentum_raw * momentum_unit / weighting[:, None]
    charge = float(group["charge"].attrs["value"]) * float(group["charge"].attrs["unitSI"])
    mass = float(group["mass"].attrs["value"]) * float(group["mass"].attrs["unitSI"])

    c = 299_792_458.0
    dimensionless_p = momentum / (mass * c)
    gamma = np.sqrt(1.0 + np.sum(dimensionless_p**2, axis=1))
    velocity = momentum / (gamma[:, None] * mass)
    return {
        "name": species,
        "group": group,
        "coordinates": coordinates,
        "momentum": momentum,
        "velocity": velocity,
        "gamma": gamma,
        "weighting": weighting,
        "charge": charge,
        "mass": mass,
    }


def relative_rms(residual: np.ndarray, scale: np.ndarray) -> float:
    numerator = float(np.sqrt(np.mean(np.asarray(residual, dtype=float) ** 2)))
    denominator = float(np.sqrt(np.mean(np.asarray(scale, dtype=float) ** 2)))
    return numerator / denominator if denominator else float("nan")


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

        all_field_values = np.concatenate(
            [fields[name][component].ravel() for name in ("E", "B") for component in COMPONENTS]
        )
        if not np.all(np.isfinite(all_field_values)):
            raise ValueError("Non-finite field values found")

        grid_spacing_si = (
            np.asarray(iteration["fields/E"].attrs["gridSpacing"], dtype=float)
            * float(iteration["fields/E"].attrs["gridUnitSI"])
        )
        cell_volume = float(np.prod(grid_spacing_si))
        e_center = np.stack(
            [collocate_to_integer_grid(fields["E"][c], offsets["E"][c]) for c in COMPONENTS],
            axis=-1,
        )
        b_center = np.stack(
            [collocate_to_integer_grid(fields["B"][c], offsets["B"][c]) for c in COMPONENTS],
            axis=-1,
        )

        n_columns = 11
        deposited = np.zeros(field_shape + (n_columns,), dtype=float)
        species_rho: dict[str, np.ndarray] = {}
        particle_summaries: dict[str, dict] = {}
        particle_samples: list[dict] = []
        all_x: list[np.ndarray] = []
        all_cosine: list[np.ndarray] = []
        all_force_magnitude: list[np.ndarray] = []
        all_species_label: list[np.ndarray] = []

        for species_name in ("e", "i"):
            particles = load_particle_species(iteration, species_name)
            coordinates = particles["coordinates"]
            velocity = particles["velocity"]
            weighting = particles["weighting"]
            charge = particles["charge"]

            if not (
                np.all(np.isfinite(coordinates))
                and np.all(np.isfinite(velocity))
                and np.all(np.isfinite(weighting))
                and np.all(weighting > 0)
                and particles["mass"] > 0
            ):
                raise ValueError(f"Invalid particle data in species {species_name}")

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
            force = force_e + force_b
            magnitude_e = np.linalg.norm(force_e, axis=1)
            magnitude_b = np.linalg.norm(force_b, axis=1)
            magnitude = np.linalg.norm(force, axis=1)
            envelope = magnitude_e + magnitude_b
            valid_envelope = envelope > 0
            x_force = np.full(len(envelope), np.nan)
            x_force[valid_envelope] = 2.0 * magnitude_b[valid_envelope] / envelope[valid_envelope]
            valid_pair = (magnitude_e > 0) & (magnitude_b > 0)
            cosine = np.full(len(envelope), np.nan)
            cosine[valid_pair] = np.sum(force_e[valid_pair] * force_b[valid_pair], axis=1) / (
                magnitude_e[valid_pair] * magnitude_b[valid_pair]
            )
            reconstructed = 0.5 * envelope * np.sqrt(
                np.maximum(
                    0.0,
                    (2.0 - x_force) ** 2
                    + x_force**2
                    + 2.0 * x_force * (2.0 - x_force) * cosine,
                )
            )

            reconstruction_relative_l2 = float(
                np.linalg.norm(reconstructed - magnitude) / np.linalg.norm(magnitude)
            )
            magnetic_power = np.sum(velocity * force_b, axis=1)
            total_power = np.sum(velocity * force, axis=1)
            electric_power = np.sum(velocity * force_e, axis=1)
            magnetic_work_leakage = relative_rms(
                magnetic_power, np.linalg.norm(velocity, axis=1) * magnitude_b
            )
            power_identity_error = relative_rms(
                total_power - electric_power,
                np.linalg.norm(velocity, axis=1) * magnitude,
            )

            particle_summaries[species_name] = {
                "n_particles": int(len(coordinates)),
                "charge_C": float(charge),
                "mass_kg": float(particles["mass"]),
                "weighting": percentile_dict(weighting),
                "gamma": percentile_dict(particles["gamma"]),
                "speed_over_c": percentile_dict(
                    np.linalg.norm(velocity, axis=1) / 299_792_458.0
                ),
                "force_e_N": percentile_dict(magnitude_e),
                "force_b_N": percentile_dict(magnitude_b),
                "force_total_N": percentile_dict(magnitude),
                "x_force": percentile_dict(x_force),
                "cosine_force_channels": percentile_dict(cosine),
                "reconstruction_relative_l2": reconstruction_relative_l2,
                "magnetic_work_normalised_rms": magnetic_work_leakage,
                "total_power_identity_normalised_rms": power_identity_error,
                "interior_fraction": float(
                    np.mean(np.all((coordinates >= 1.0) & (coordinates < 31.0), axis=1))
                ),
            }

            macro_charge = weighting * charge
            macro_current = macro_charge[:, None] * velocity
            macro_force_e = weighting[:, None] * force_e
            macro_force_b = weighting[:, None] * force_b
            deposited_values = np.column_stack(
                [
                    macro_charge,
                    macro_current,
                    macro_force_e,
                    macro_force_b,
                    np.ones(len(coordinates)),
                ]
            )
            species_deposit = deposit_cic(coordinates, deposited_values, field_shape)
            deposited += species_deposit
            species_rho[species_name] = species_deposit[..., 0] / cell_volume

            sample_indices = np.linspace(0, len(coordinates) - 1, min(10_000, len(coordinates)), dtype=int)
            for index in sample_indices:
                particle_samples.append(
                    {
                        "species": species_name,
                        "particle_index": int(index),
                        "x_force": float(x_force[index]),
                        "channel_cosine": float(cosine[index]),
                        "electric_force_N": float(magnitude_e[index]),
                        "magnetic_force_N": float(magnitude_b[index]),
                        "resultant_force_N": float(magnitude[index]),
                        "reconstructed_force_N": float(reconstructed[index]),
                        "magnetic_power_W": float(magnetic_power[index]),
                    }
                )

            all_x.append(x_force)
            all_cosine.append(cosine)
            all_force_magnitude.append(magnitude)
            all_species_label.append(np.full(len(coordinates), species_name))

        rho_deposited = deposited[..., 0] / cell_volume
        current_deposited = deposited[..., 1:4] / cell_volume
        particle_first_e = deposited[..., 4:7] / cell_volume
        particle_first_b = deposited[..., 7:10] / cell_volume
        occupancy = deposited[..., 10]
        field_first_e = rho_deposited[..., None] * e_center
        field_first_b = np.cross(current_deposited, b_center)

        interior = np.zeros(field_shape, dtype=bool)
        interior[1:-1, 1:-1, 1:-1] = True
        active_mask = interior & (occupancy > 0)

        channels = {
            "electric": vector_metrics(particle_first_e, field_first_e, active_mask),
            "magnetic": vector_metrics(particle_first_b, field_first_b, active_mask),
            "total": vector_metrics(
                particle_first_e + particle_first_b,
                field_first_e + field_first_b,
                active_mask,
            ),
        }
        total_metrics = channels["total"]
        if (
            total_metrics["vector_correlation"] >= 0.90
            and total_metrics["nrmse_by_target_std"] <= 0.50
            and total_metrics["median_angular_error_deg"] <= 15.0
        ):
            rung_classification = "strong rung preservation"
        elif total_metrics["vector_correlation"] >= 0.70:
            rung_classification = "partial rung preservation"
        else:
            rung_classification = "not recovered by this operator"

        recorded_rho = {
            "e": iteration["fields/e_chargeDensity"][...].astype(float)
            * float(iteration["fields/e_chargeDensity"].attrs["unitSI"]),
            "i": iteration["fields/i_chargeDensity"][...].astype(float)
            * float(iteration["fields/i_chargeDensity"].attrs["unitSI"]),
        }
        charge_density_validation = {
            species: scalar_metrics(recorded_rho[species], species_rho[species], active_mask)
            for species in ("e", "i")
        }
        charge_density_validation["total"] = scalar_metrics(
            recorded_rho["e"] + recorded_rho["i"], rho_deposited, active_mask
        )

        e_rms = float(np.sqrt(np.mean(e_center**2)))
        b_rms = float(np.sqrt(np.mean(b_center**2)))
        gradient_e_sq = np.zeros(field_shape)
        gradient_b_sq = np.zeros(field_shape)
        for component in range(3):
            for gradient in np.gradient(e_center[..., component]):
                gradient_e_sq += (gradient / max(e_rms, np.finfo(float).tiny)) ** 2
            for gradient in np.gradient(b_center[..., component]):
                gradient_b_sq += (gradient / max(b_rms, np.finfo(float).tiny)) ** 2
        gradient_strength = np.sqrt(gradient_e_sq + gradient_b_sq)
        residual = np.linalg.norm(
            (field_first_e + field_first_b) - (particle_first_e + particle_first_b), axis=-1
        )
        spearman_gradient = spearmanr(
            residual[active_mask], gradient_strength[active_mask], nan_policy="omit"
        )
        spearman_occupancy = spearmanr(
            residual[active_mask], occupancy[active_mask], nan_policy="omit"
        )

        root_attrs = {key: as_text(value) for key, value in handle.attrs.items()}
        results = {
            "test": "MX4 Lorentz-force <-> ARA crosswalk",
            "status": "development recovery/crosswalk; not independent acceleration confirmation",
            "source": {
                "path": str(source),
                "bytes": int(source.stat().st_size),
                "sha256": observed_hash,
                "repository": "https://github.com/openPMD/openPMD-example-datasets",
                "archive": "legacy_datasets.tar.gz",
                "producer": root_attrs.get("software"),
                "producer_version": root_attrs.get("softwareVersion"),
                "openPMD": root_attrs.get("openPMD"),
                "iteration": 200,
                "time_s": float(iteration.attrs["time"] * iteration.attrs["timeUnitSI"]),
                "field_shape_zyx": list(field_shape),
                "grid_spacing_m": grid_spacing_si.tolist(),
                "cell_volume_m3": cell_volume,
                "snapshot_count": 1,
            },
            "data_quality": {
                "hash_match": True,
                "all_fields_finite": True,
                "field_solver": as_text(iteration["fields"].attrs["fieldSolver"]),
                "particle_shape": float(iteration["particles/e"].attrs["particleShape"]),
                "particle_interpolation_recorded": as_text(
                    iteration["particles/e"].attrs["particleInterpolation"]
                ),
                "particle_push": as_text(iteration["particles/e"].attrs["particlePush"]),
                "analysis_interpolation": "trilinear with recorded Yee offsets; edge clamp",
                "analysis_deposition": "cloud-in-cell to integer grid positions",
                "charge_density_validation": charge_density_validation,
                "limitation": (
                    "The source records quadratic particle shape but this frozen development bridge uses "
                    "CIC; one snapshot prevents observed acceleration testing."
                ),
            },
            "mx4_l1_particle_rung": particle_summaries,
            "mx4_l1_gates": {
                "relative_reconstruction_le_1e-12": bool(
                    all(v["reconstruction_relative_l2"] <= 1e-12 for v in particle_summaries.values())
                ),
                "magnetic_work_leakage_le_1e-12": bool(
                    all(v["magnetic_work_normalised_rms"] <= 1e-12 for v in particle_summaries.values())
                ),
                "power_identity_error_le_1e-12": bool(
                    all(v["total_power_identity_normalised_rms"] <= 1e-12 for v in particle_summaries.values())
                ),
            },
            "mx4_l2_grid_rung": {
                "mask": "one-cell interior and occupancy > 0",
                "channels": channels,
                "classification": rung_classification,
                "residual_spearman_vs_relative_field_gradient": {
                    "rho": float(spearman_gradient.statistic),
                    "p_value": float(spearman_gradient.pvalue),
                },
                "residual_spearman_vs_occupancy": {
                    "rho": float(spearman_occupancy.statistic),
                    "p_value": float(spearman_occupancy.pvalue),
                },
            },
            "mx4_l3_acceleration_confirmation": {
                "status": "NOT RUN",
                "reason": "The public source contains one time snapshot only.",
            },
            "interpretation_ceiling": (
                "Passing L1 validates the ARA reparameterisation/implementation, not a new law. "
                "L2 evaluates one declared coarse-graining operator. L3 remains required for an "
                "independent dynamical confirmation."
            ),
        }

        arrays = {
            "particle_samples": particle_samples,
            "all_x": np.concatenate(all_x),
            "all_cosine": np.concatenate(all_cosine),
            "all_force_magnitude": np.concatenate(all_force_magnitude),
            "all_species_label": np.concatenate(all_species_label),
            "occupancy": occupancy,
            "gradient_strength": gradient_strength,
            "particle_first_e": particle_first_e,
            "particle_first_b": particle_first_b,
            "field_first_e": field_first_e,
            "field_first_b": field_first_b,
            "active_mask": active_mask,
        }
        return results, arrays


def write_grid_csv(path: Path, arrays: dict) -> None:
    target_e = arrays["particle_first_e"]
    target_b = arrays["particle_first_b"]
    estimate_e = arrays["field_first_e"]
    estimate_b = arrays["field_first_b"]
    occupancy = arrays["occupancy"]
    gradient = arrays["gradient_strength"]
    active = arrays["active_mask"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "z_index",
                "y_index",
                "x_index",
                "active_interior",
                "occupancy_cic",
                "relative_field_gradient",
                "particle_first_e_magnitude_N_per_m3",
                "field_first_e_magnitude_N_per_m3",
                "particle_first_b_magnitude_N_per_m3",
                "field_first_b_magnitude_N_per_m3",
                "particle_first_total_magnitude_N_per_m3",
                "field_first_total_magnitude_N_per_m3",
                "total_residual_magnitude_N_per_m3",
                "particle_first_total_x_N_per_m3",
                "particle_first_total_y_N_per_m3",
                "particle_first_total_z_N_per_m3",
                "field_first_total_x_N_per_m3",
                "field_first_total_y_N_per_m3",
                "field_first_total_z_N_per_m3",
            ]
        )
        for z, y, x in np.ndindex(occupancy.shape):
            p_e = target_e[z, y, x]
            p_b = target_b[z, y, x]
            f_e = estimate_e[z, y, x]
            f_b = estimate_b[z, y, x]
            particle_total = p_e + p_b
            field_total = f_e + f_b
            writer.writerow(
                [
                    z,
                    y,
                    x,
                    int(active[z, y, x]),
                    occupancy[z, y, x],
                    gradient[z, y, x],
                    np.linalg.norm(p_e),
                    np.linalg.norm(f_e),
                    np.linalg.norm(p_b),
                    np.linalg.norm(f_b),
                    np.linalg.norm(particle_total),
                    np.linalg.norm(field_total),
                    np.linalg.norm(field_total - particle_total),
                    *particle_total,
                    *field_total,
                ]
            )


def write_particle_sample(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def make_figure(path: Path, results: dict, arrays: dict) -> None:
    x_force = arrays["all_x"]
    cosine = arrays["all_cosine"]
    force = arrays["all_force_magnitude"]
    labels = arrays["all_species_label"]
    mask = arrays["active_mask"]
    target_total = (arrays["particle_first_e"] + arrays["particle_first_b"])[mask]
    estimate_total = (arrays["field_first_e"] + arrays["field_first_b"])[mask]
    target_mag = np.linalg.norm(target_total, axis=1)
    estimate_mag = np.linalg.norm(estimate_total, axis=1)
    residual = np.linalg.norm(estimate_total - target_total, axis=1)

    figure, axes = plt.subplots(2, 2, figsize=(13, 10), constrained_layout=True)
    bins = np.linspace(0, 2, 81)
    for species, colour, label in (("e", "#2878b5", "electrons"), ("i", "#d95f02", "ions")):
        axes[0, 0].hist(
            x_force[labels == species], bins=bins, density=True, histtype="step", linewidth=2, color=colour, label=label
        )
    axes[0, 0].axvline(1.0, color="black", linestyle="--", linewidth=1)
    axes[0, 0].set(xlabel="ARA force-channel coordinate $x_F$", ylabel="density", title="Particle-rung channel mixture")
    axes[0, 0].legend()

    sample = np.linspace(0, len(x_force) - 1, min(25_000, len(x_force)), dtype=int)
    scatter = axes[0, 1].scatter(
        x_force[sample], cosine[sample], c=np.log10(np.maximum(force[sample], np.finfo(float).tiny)),
        s=5, alpha=0.35, cmap="viridis"
    )
    axes[0, 1].set(xlabel="$x_F$", ylabel=r"$\cos(\theta_F)$", title="Magnitude coordinate retains a separate direction coordinate")
    figure.colorbar(scatter, ax=axes[0, 1], label=r"$\log_{10}|f|$ [N]")

    positive = (target_mag > 0) & (estimate_mag > 0)
    axes[1, 0].loglog(target_mag[positive], estimate_mag[positive], ".", alpha=0.25, markersize=3)
    bounds = [
        min(float(np.min(target_mag[positive])), float(np.min(estimate_mag[positive]))),
        max(float(np.max(target_mag[positive])), float(np.max(estimate_mag[positive]))),
    ]
    axes[1, 0].plot(bounds, bounds, "k--", linewidth=1)
    total = results["mx4_l2_grid_rung"]["channels"]["total"]
    axes[1, 0].set(
        xlabel="particle-first $|f_V|$ [N m$^{-3}$]",
        ylabel="field-first $|f_V|$ [N m$^{-3}$]",
        title=f"Grid-rung bridge: corr={total['vector_correlation']:.3f}, NRMSE={total['nrmse_by_target_std']:.3f}",
    )

    z_mid = arrays["occupancy"].shape[0] // 2
    residual_grid = np.linalg.norm(
        (arrays["field_first_e"] + arrays["field_first_b"])
        - (arrays["particle_first_e"] + arrays["particle_first_b"]),
        axis=-1,
    )
    image = axes[1, 1].imshow(np.log10(np.maximum(residual_grid[z_mid], np.finfo(float).tiny)), origin="lower", cmap="magma")
    axes[1, 1].set(xlabel="x cell", ylabel="y cell", title=f"Coarse-graining residual, z={z_mid}")
    figure.colorbar(image, ax=axes[1, 1], label=r"$\log_{10}$ residual [N m$^{-3}$]")

    figure.suptitle("MX4 Lorentz-force ↔ ARA crosswalk on public PIConGPU data", fontsize=15)
    figure.savefig(path, dpi=180)
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    results, arrays = run_analysis(args.source)
    results_path = args.output_dir / "MX4_LORENTZ_ARA_RESULTS.json"
    particle_path = args.output_dir / "MX4_LORENTZ_ARA_PARTICLE_SAMPLE.csv"
    grid_path = args.output_dir / "MX4_LORENTZ_ARA_GRID_CELLS.csv"
    figure_path = args.output_dir / "MX4_LORENTZ_ARA_CROSSWALK.png"
    results_path.write_text(json.dumps(results, indent=2, allow_nan=False), encoding="utf-8")
    write_particle_sample(particle_path, arrays["particle_samples"])
    write_grid_csv(grid_path, arrays)
    make_figure(figure_path, results, arrays)
    print(json.dumps(results, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
