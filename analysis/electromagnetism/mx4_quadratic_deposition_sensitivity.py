"""Post-freeze MX4 sensitivity: quadratic/TSC deposition instead of CIC.

The field gather remains the frozen trilinear gather.  This isolates whether the
failed MX4-L2 bridge was mainly caused by using CIC with a source that records a
quadratic particle shape.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import h5py
import numpy as np

from mx4_lorentz_ara_crosswalk import (
    COMPONENTS,
    EXPECTED_SOURCE_SHA256,
    collocate_to_integer_grid,
    load_fields,
    load_particle_species,
    scalar_metrics,
    sha256,
    trilinear_sample,
    vector_metrics,
)


def quadratic_weights(coordinate: np.ndarray) -> tuple[np.ndarray, list[np.ndarray]]:
    nearest = np.floor(coordinate + 0.5).astype(np.int64)
    weights: list[np.ndarray] = []
    for shift in (-1, 0, 1):
        distance = np.abs(coordinate - (nearest + shift))
        weight = np.where(
            distance < 0.5,
            0.75 - distance**2,
            np.where(distance < 1.5, 0.5 * (1.5 - distance) ** 2, 0.0),
        )
        weights.append(weight)
    return nearest, weights


def deposit_tsc(
    coordinates_xyz: np.ndarray,
    values: np.ndarray,
    grid_shape_zyx: tuple[int, int, int],
) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    if values.ndim == 1:
        values = values[:, None]
    nz, ny, nx = grid_shape_zyx
    n_cells = nx * ny * nz
    centers = []
    axis_weights = []
    for axis in range(3):
        center, weights = quadratic_weights(coordinates_xyz[:, axis])
        centers.append(center)
        axis_weights.append(weights)
    output = np.zeros((n_cells, values.shape[1]), dtype=float)

    for sx_index, sx in enumerate((-1, 0, 1)):
        ix = centers[0] + sx
        wx = axis_weights[0][sx_index]
        for sy_index, sy in enumerate((-1, 0, 1)):
            iy = centers[1] + sy
            wy = axis_weights[1][sy_index]
            for sz_index, sz in enumerate((-1, 0, 1)):
                iz = centers[2] + sz
                wz = axis_weights[2][sz_index]
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


def run(source: Path, primary_results: Path) -> dict:
    observed_hash = sha256(source)
    if observed_hash != EXPECTED_SOURCE_SHA256:
        raise ValueError("Source hash mismatch")
    primary = json.loads(primary_results.read_text(encoding="utf-8"))

    with h5py.File(source, "r") as handle:
        iteration = handle["data/200"]
        fields, offsets = load_fields(iteration)
        shape = fields["E"]["x"].shape
        spacing = (
            np.asarray(iteration["fields/E"].attrs["gridSpacing"], dtype=float)
            * float(iteration["fields/E"].attrs["gridUnitSI"])
        )
        volume = float(np.prod(spacing))
        e_center = np.stack(
            [collocate_to_integer_grid(fields["E"][c], offsets["E"][c]) for c in COMPONENTS], axis=-1
        )
        b_center = np.stack(
            [collocate_to_integer_grid(fields["B"][c], offsets["B"][c]) for c in COMPONENTS], axis=-1
        )

        deposited = np.zeros(shape + (11,), dtype=float)
        species_rho = {}
        for species in ("e", "i"):
            particle = load_particle_species(iteration, species)
            coordinate = particle["coordinates"]
            velocity = particle["velocity"]
            charge = particle["charge"]
            weighting = particle["weighting"]
            e_particle = np.column_stack(
                [trilinear_sample(fields["E"][c], coordinate, offsets["E"][c]) for c in COMPONENTS]
            )
            b_particle = np.column_stack(
                [trilinear_sample(fields["B"][c], coordinate, offsets["B"][c]) for c in COMPONENTS]
            )
            force_e = charge * e_particle
            force_b = charge * np.cross(velocity, b_particle)
            macro_charge = weighting * charge
            values = np.column_stack(
                [
                    macro_charge,
                    macro_charge[:, None] * velocity,
                    weighting[:, None] * force_e,
                    weighting[:, None] * force_b,
                    np.ones(len(coordinate)),
                ]
            )
            species_deposit = deposit_tsc(coordinate, values, shape)
            deposited += species_deposit
            species_rho[species] = species_deposit[..., 0] / volume

        rho = deposited[..., 0] / volume
        current = deposited[..., 1:4] / volume
        particle_e = deposited[..., 4:7] / volume
        particle_b = deposited[..., 7:10] / volume
        occupancy = deposited[..., 10]
        field_e = rho[..., None] * e_center
        field_b = np.cross(current, b_center)
        mask = np.zeros(shape, dtype=bool)
        mask[1:-1, 1:-1, 1:-1] = True
        mask &= occupancy > 0

        channels = {
            "electric": vector_metrics(particle_e, field_e, mask),
            "magnetic": vector_metrics(particle_b, field_b, mask),
            "total": vector_metrics(particle_e + particle_b, field_e + field_b, mask),
        }
        total = channels["total"]
        if (
            total["vector_correlation"] >= 0.90
            and total["nrmse_by_target_std"] <= 0.50
            and total["median_angular_error_deg"] <= 15.0
        ):
            classification = "strong rung preservation"
        elif total["vector_correlation"] >= 0.70:
            classification = "partial rung preservation"
        else:
            classification = "not recovered by this operator"

        recorded = {
            species: iteration[f"fields/{species}_chargeDensity"][...].astype(float)
            * float(iteration[f"fields/{species}_chargeDensity"].attrs["unitSI"])
            for species in ("e", "i")
        }
        validation = {
            species: scalar_metrics(recorded[species], species_rho[species], mask)
            for species in ("e", "i")
        }
        validation["total"] = scalar_metrics(recorded["e"] + recorded["i"], rho, mask)

    return {
        "status": "post-freeze sensitivity; does not replace the frozen CIC result",
        "change_from_primary": "quadratic/TSC particle deposition; field gather remains trilinear",
        "source_sha256": observed_hash,
        "charge_density_validation": validation,
        "channels": channels,
        "classification": classification,
        "comparison_with_primary_cic": {
            "primary_classification": primary["mx4_l2_grid_rung"]["classification"],
            "primary_total": primary["mx4_l2_grid_rung"]["channels"]["total"],
            "quadratic_total": total,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.source.resolve(), args.results_dir / "MX4_LORENTZ_ARA_RESULTS.json")
    output = args.results_dir / "MX4_QUADRATIC_DEPOSITION_SENSITIVITY_RESULTS.json"
    output.write_text(json.dumps(result, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
