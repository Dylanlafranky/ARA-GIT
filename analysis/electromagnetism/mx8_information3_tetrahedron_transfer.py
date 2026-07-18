"""Frozen MX8 held-out Information^3 tetrahedron transfer test.

This uses the public Warp openPMD example-2d time series.  It tests whether
the xy interaction in a four-route phase table transfers from early to late
snapshots after the separate x and y effects are already represented.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import h5py
import matplotlib.pyplot as plt
import numpy as np


COMPONENTS = ("x", "y", "z")
ROUTES = ("AA", "AB", "BA", "BB")
ROUTE_X = np.array([1.0, 1.0, -1.0, -1.0])
ROUTE_Y = np.array([1.0, -1.0, 1.0, -1.0])
ROUTE_RELATION = ROUTE_X * ROUTE_Y
DEVELOPMENT = tuple(range(255, 321, 5))
QUARANTINE = tuple(range(325, 351, 5))
TEST = tuple(range(355, 401, 5))
BOOTSTRAP_SEED = 20260715
BOOTSTRAP_REPLICATES = 10_000


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def constant_or_array(record, component: str, n: int) -> np.ndarray:
    item = record[component]
    if isinstance(item, h5py.Dataset):
        return item[...].astype(float) * float(item.attrs.get("unitSI", 1.0))
    value = float(item.attrs["value"]) * float(item.attrs.get("unitSI", 1.0))
    return np.full(n, value, dtype=float)


def scalar_constant_or_array(item, n: int) -> np.ndarray:
    if isinstance(item, h5py.Dataset):
        return item[...].astype(float) * float(item.attrs.get("unitSI", 1.0))
    value = float(item.attrs["value"]) * float(item.attrs.get("unitSI", 1.0))
    return np.full(n, value, dtype=float)


def bilinear_sample(array_xz: np.ndarray, coordinates_xz: np.ndarray, offset_xz: np.ndarray) -> np.ndarray:
    """Edge-clamped bilinear sample on the recorded x,z mesh order."""
    shape = np.asarray(array_xz.shape, dtype=int)
    u = coordinates_xz - np.asarray(offset_xz, dtype=float)
    lower = np.floor(u).astype(np.int64)
    frac = u - lower
    below = u <= 0.0
    above = u >= (shape - 1)
    lower = np.clip(lower, 0, shape - 2)
    frac = np.where(below, 0.0, frac)
    frac = np.where(above, 1.0, frac)
    result = np.zeros(len(coordinates_xz), dtype=float)
    for dx in (0, 1):
        wx = (1.0 - frac[:, 0]) if dx == 0 else frac[:, 0]
        ix = lower[:, 0] + dx
        for dz in (0, 1):
            wz = (1.0 - frac[:, 1]) if dz == 0 else frac[:, 1]
            iz = lower[:, 1] + dz
            result += wx * wz * array_xz[ix, iz]
    return result


def deposit_bilinear(coordinates_xz: np.ndarray, values: np.ndarray, shape_xz: tuple[int, int]) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    if values.ndim == 1:
        values = values[:, None]
    nx, nz = shape_xz
    base = np.floor(coordinates_xz).astype(np.int64)
    frac = coordinates_xz - base
    output = np.zeros((nx * nz, values.shape[1]), dtype=float)
    for dx in (0, 1):
        wx = (1.0 - frac[:, 0]) if dx == 0 else frac[:, 0]
        ix = base[:, 0] + dx
        for dz in (0, 1):
            wz = (1.0 - frac[:, 1]) if dz == 0 else frac[:, 1]
            iz = base[:, 1] + dz
            keep = (ix >= 0) & (ix < nx) & (iz >= 0) & (iz < nz)
            flat = (ix[keep] * nz + iz[keep]).astype(int)
            weights = (wx * wz)[keep]
            for column in range(values.shape[1]):
                output[:, column] += np.bincount(
                    flat,
                    weights=weights * values[keep, column],
                    minlength=nx * nz,
                )
    return output.reshape((nx, nz, values.shape[1]))


def iteration_path(source_dir: Path, iteration: int) -> Path:
    return source_dir / f"data{iteration:08d}.h5"


def load_snapshot(source_dir: Path, iteration_number: int) -> dict[str, np.ndarray]:
    path = iteration_path(source_dir, iteration_number)
    with h5py.File(path, "r") as handle:
        iteration = handle[f"data/{iteration_number}"]
        e_group = iteration["fields/E"]
        axis_labels = tuple(
            value.decode("utf-8") if isinstance(value, bytes) else str(value)
            for value in e_group.attrs["axisLabels"]
        )
        if axis_labels != ("x", "z"):
            raise ValueError(f"Unexpected mesh axes {axis_labels}")
        spacing = np.asarray(e_group.attrs["gridSpacing"], dtype=float) * float(
            e_group.attrs["gridUnitSI"]
        )
        origin = np.asarray(e_group.attrs["gridGlobalOffset"], dtype=float) * float(
            e_group.attrs["gridUnitSI"]
        )
        e_fields = {}
        e_offsets = {}
        for component in COMPONENTS:
            dataset = e_group[component]
            e_fields[component] = dataset[...].astype(float) * float(dataset.attrs["unitSI"])
            e_offsets[component] = np.asarray(dataset.attrs["position"], dtype=float)
        shape = e_fields["x"].shape
        if any(array.shape != shape for array in e_fields.values()):
            raise ValueError("Electric components do not share a mesh shape")

        # Columns: absolute charge activity, then route activity and |E|-weighted
        # route activity for each vector component.
        deposited = np.zeros(shape + (1 + 3 * 8,), dtype=float)
        counts = {}
        for species_name in ("Hydrogen1+", "electrons"):
            group = iteration[f"particles/{species_name}"]
            n = int(group["weighting"].shape[0])
            counts[species_name] = n
            weighting = scalar_constant_or_array(group["weighting"], n)
            charge = scalar_constant_or_array(group["charge"], n)
            charge_sign = np.sign(charge)
            position_x = constant_or_array(group["position"], "x", n) + constant_or_array(
                group["positionOffset"], "x", n
            )
            position_z = constant_or_array(group["position"], "z", n) + constant_or_array(
                group["positionOffset"], "z", n
            )
            physical_xz = np.column_stack([position_x, position_z])
            coordinates = (physical_xz - origin) / spacing
            absolute_macro_charge = weighting * np.abs(charge)
            values = np.zeros((n, deposited.shape[-1]), dtype=float)
            values[:, 0] = absolute_macro_charge
            for component_index, component in enumerate(COMPONENTS):
                sampled = bilinear_sample(e_fields[component], coordinates, e_offsets[component])
                field_sign = np.sign(sampled)
                magnitude = np.abs(sampled)
                start = 1 + component_index * 8
                indicators = (
                    (charge_sign > 0) & (field_sign > 0),
                    (charge_sign > 0) & (field_sign < 0),
                    (charge_sign < 0) & (field_sign > 0),
                    (charge_sign < 0) & (field_sign < 0),
                )
                for route_index, indicator in enumerate(indicators):
                    values[:, start + route_index] = absolute_macro_charge * indicator
                    values[:, start + 4 + route_index] = (
                        absolute_macro_charge * magnitude * indicator
                    )
            deposited += deposit_bilinear(coordinates, values, shape)

    q = deposited[..., 0]
    route_weight = np.zeros(shape + (3, 4), dtype=float)
    route_magnitude_sum = np.zeros_like(route_weight)
    for component_index in range(3):
        start = 1 + component_index * 8
        route_weight[..., component_index, :] = deposited[..., start : start + 4]
        route_magnitude_sum[..., component_index, :] = deposited[..., start + 4 : start + 8]
    probabilities = np.divide(
        route_weight,
        q[..., None, None],
        out=np.zeros_like(route_weight),
        where=q[..., None, None] > 0,
    )
    route_magnitudes = np.divide(
        route_magnitude_sum,
        route_weight,
        out=np.full_like(route_weight, np.nan),
        where=route_weight > 0,
    )
    common_magnitude = np.divide(
        np.sum(route_magnitude_sum, axis=-1),
        q[..., None],
        out=np.zeros(shape + (3,), dtype=float),
        where=q[..., None] > 0,
    )
    target = np.sum(route_magnitude_sum * ROUTE_RELATION, axis=-1)
    interior = np.zeros(shape, dtype=bool)
    interior[1:-1, 1:-1] = True
    active = interior & (q > 0) & np.all(np.isfinite(target), axis=-1)
    return {
        "q": q,
        "route_weight": route_weight,
        "probabilities": probabilities,
        "route_magnitudes": route_magnitudes,
        "common_magnitude": common_magnitude,
        "target": target,
        "active": active,
        "particle_counts": counts,
        "shape": np.asarray(shape),
    }


def design_matrix(model: str) -> np.ndarray:
    columns = [np.ones(4)]
    if model in ("additive", "relation"):
        columns.extend([ROUTE_X, ROUTE_Y])
    if model == "relation":
        columns.append(ROUTE_RELATION)
    return np.column_stack(columns)


def fit_models(source_dir: Path) -> tuple[dict[str, np.ndarray], dict]:
    models = ("blind", "additive", "relation")
    normal = {
        model: [np.zeros((design_matrix(model).shape[1],) * 2).reshape(
            design_matrix(model).shape[1], design_matrix(model).shape[1]
        ) for _ in COMPONENTS]
        for model in models
    }
    rhs = {
        model: [np.zeros(design_matrix(model).shape[1]) for _ in COMPONENTS]
        for model in models
    }
    fit_rows = np.zeros((3, 4), dtype=np.int64)
    fit_weight = np.zeros((3, 4), dtype=float)
    snapshot_counts = {}
    for iteration in DEVELOPMENT:
        snapshot = load_snapshot(source_dir, iteration)
        snapshot_counts[str(iteration)] = snapshot["particle_counts"]
        active = snapshot["active"]
        for component_index in range(3):
            common = snapshot["common_magnitude"][..., component_index]
            for route_index in range(4):
                magnitude = snapshot["route_magnitudes"][..., component_index, route_index]
                weight = snapshot["route_weight"][..., component_index, route_index]
                keep = active & (common > 0) & (magnitude > 0) & (weight > 0)
                if not np.any(keep):
                    continue
                response = np.log(magnitude[keep] / common[keep])
                row_weight = weight[keep]
                fit_rows[component_index, route_index] += int(np.sum(keep))
                fit_weight[component_index, route_index] += float(np.sum(row_weight))
                for model in models:
                    row = design_matrix(model)[route_index]
                    normal[model][component_index] += np.outer(row, row) * float(
                        np.sum(row_weight)
                    )
                    rhs[model][component_index] += row * float(np.sum(row_weight * response))
    coefficients = {}
    for model in models:
        coefficients[model] = np.stack(
            [
                np.linalg.solve(normal[model][component], rhs[model][component])
                for component in range(3)
            ]
        )
    diagnostics = {
        "fit_rows_by_component_route": {
            component: {route: int(fit_rows[c, r]) for r, route in enumerate(ROUTES)}
            for c, component in enumerate(COMPONENTS)
        },
        "fit_weight_by_component_route_C": {
            component: {route: float(fit_weight[c, r]) for r, route in enumerate(ROUTES)}
            for c, component in enumerate(COMPONENTS)
        },
        "development_particle_counts": snapshot_counts,
    }
    return coefficients, diagnostics


def estimates(snapshot: dict[str, np.ndarray], coefficients: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    q = snapshot["q"]
    p = snapshot["probabilities"]
    common = snapshot["common_magnitude"]
    mean_x = np.sum(p * ROUTE_X, axis=-1)
    mean_y = np.sum(p * ROUTE_Y, axis=-1)
    mean_relation = np.sum(p * ROUTE_RELATION, axis=-1)
    result = {
        "independent_marginals": q[..., None] * common * mean_x * mean_y,
        "joint_sign": q[..., None] * common * mean_relation,
        "exact_conditioned_ceiling": snapshot["target"].copy(),
    }
    for model in ("blind", "additive", "relation"):
        route_design = design_matrix(model)
        predicted_height = coefficients[model] @ route_design.T
        multipliers = np.exp(predicted_height)
        result[model] = q[..., None] * common * np.sum(
            p * ROUTE_RELATION * multipliers[None, None, ...], axis=-1
        )
    return result


def metric_bundle(target: np.ndarray, estimate: np.ndarray) -> dict:
    target_flat = target.ravel()
    estimate_flat = estimate.ravel()
    residual = estimate - target
    target_norm = float(np.linalg.norm(target_flat))
    estimate_norm = float(np.linalg.norm(estimate_flat))
    relative_l2 = float(np.linalg.norm(residual.ravel()) / target_norm)
    target_std = float(np.std(target_flat))
    dot = float(np.dot(target_flat, estimate_flat))
    vector_correlation = dot / (target_norm * estimate_norm) if target_norm and estimate_norm else float("nan")
    target_mag = np.linalg.norm(target, axis=1)
    estimate_mag = np.linalg.norm(estimate, axis=1)
    keep = (target_mag > 0) & (estimate_mag > 0)
    angle = np.full(len(target), np.nan)
    angle[keep] = np.degrees(
        np.arccos(
            np.clip(
                np.sum(target[keep] * estimate[keep], axis=1)
                / (target_mag[keep] * estimate_mag[keep]),
                -1.0,
                1.0,
            )
        )
    )
    return {
        "n_cells": int(len(target)),
        "relative_l2": relative_l2,
        "nrmse_by_target_std": float(np.sqrt(np.mean(residual.ravel() ** 2)) / target_std),
        "vector_correlation": float(vector_correlation),
        "median_angular_error_deg": float(np.nanmedian(angle)),
        "l2_magnitude_ratio": estimate_norm / target_norm,
    }


def local_relation_diagnostic(source_dir: Path, iterations: tuple[int, ...]) -> dict:
    """Post-gate diagnostic only: local Hadamard interaction in fully occupied cells."""
    values: list[list[np.ndarray]] = [[], [], []]
    for iteration in iterations:
        snapshot = load_snapshot(source_dir, iteration)
        for component_index in range(3):
            route_magnitude = snapshot["route_magnitudes"][..., component_index, :]
            common = snapshot["common_magnitude"][..., component_index]
            keep = (
                snapshot["active"]
                & (common > 0)
                & np.all(route_magnitude > 0, axis=-1)
                & np.all(np.isfinite(route_magnitude), axis=-1)
            )
            height = np.log(route_magnitude[keep] / common[keep, None])
            gamma = (height[:, 0] - height[:, 1] - height[:, 2] + height[:, 3]) / 4.0
            values[component_index].append(gamma)
    output = {}
    for component_index, component in enumerate(COMPONENTS):
        combined = np.concatenate(values[component_index])
        output[component] = {
            "n_fully_occupied_cell_components": int(len(combined)),
            "percentiles_p0_p5_p25_p50_p75_p95_p100": np.percentile(
                combined, [0, 5, 25, 50, 75, 95, 100]
            ).tolist(),
            "standard_deviation": float(np.std(combined)),
            "positive_fraction": float(np.mean(combined > 0)),
        }
    return output


def run(source_dir: Path) -> dict:
    expected = DEVELOPMENT + QUARANTINE + TEST
    missing = [iteration for iteration in expected if not iteration_path(source_dir, iteration).exists()]
    if missing:
        raise FileNotFoundError(f"Missing frozen source iterations: {missing}")
    coefficients, fit_diagnostics = fit_models(source_dir)
    model_names = (
        "independent_marginals",
        "joint_sign",
        "blind",
        "additive",
        "relation",
        "exact_conditioned_ceiling",
    )
    all_target = []
    all_estimates = {name: [] for name in model_names}
    per_snapshot_sums = []
    test_counts = {}
    for iteration in TEST:
        snapshot = load_snapshot(source_dir, iteration)
        test_counts[str(iteration)] = snapshot["particle_counts"]
        mask = snapshot["active"]
        target = snapshot["target"][mask]
        predicted = estimates(snapshot, coefficients)
        all_target.append(target)
        for name in model_names:
            all_estimates[name].append(predicted[name][mask])
        per_snapshot_sums.append(
            {
                "iteration": iteration,
                "target_sq": float(np.sum(target**2)),
                "additive_error_sq": float(np.sum((predicted["additive"][mask] - target) ** 2)),
                "relation_error_sq": float(np.sum((predicted["relation"][mask] - target) ** 2)),
            }
        )
    target = np.concatenate(all_target, axis=0)
    model_metrics = {
        name: metric_bundle(target, np.concatenate(all_estimates[name], axis=0))
        for name in model_names
    }

    sums = {
        key: np.asarray([row[key] for row in per_snapshot_sums], dtype=float)
        for key in ("target_sq", "additive_error_sq", "relation_error_sq")
    }
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    indices = rng.integers(0, len(TEST), size=(BOOTSTRAP_REPLICATES, len(TEST)))
    target_sq = np.sum(sums["target_sq"][indices], axis=1)
    additive_l2 = np.sqrt(np.sum(sums["additive_error_sq"][indices], axis=1) / target_sq)
    relation_l2 = np.sqrt(np.sum(sums["relation_error_sq"][indices], axis=1) / target_sq)
    improvement = (additive_l2 - relation_l2) / additive_l2
    observed_improvement = (
        model_metrics["additive"]["relative_l2"] - model_metrics["relation"]["relative_l2"]
    ) / model_metrics["additive"]["relative_l2"]
    interval = np.percentile(improvement, [2.5, 50.0, 97.5])
    secondary_nonworse = bool(
        model_metrics["relation"]["vector_correlation"]
        >= model_metrics["additive"]["vector_correlation"]
        and model_metrics["relation"]["nrmse_by_target_std"]
        <= model_metrics["additive"]["nrmse_by_target_std"]
        and model_metrics["relation"]["median_angular_error_deg"]
        <= model_metrics["additive"]["median_angular_error_deg"]
    )
    gate = {
        "observed_relative_l2_improvement_fraction": float(observed_improvement),
        "bootstrap_improvement_p2_5_p50_p97_5": interval.tolist(),
        "improvement_ge_5_percent": bool(observed_improvement >= 0.05),
        "bootstrap_interval_entirely_above_zero": bool(interval[0] > 0),
        "secondary_metrics_all_nonworse": secondary_nonworse,
    }
    gate["frozen_gate_pass"] = bool(
        gate["improvement_ge_5_percent"]
        and gate["bootstrap_interval_entirely_above_zero"]
        and secondary_nonworse
    )
    hashes = {
        str(iteration): sha256(iteration_path(source_dir, iteration)) for iteration in expected
    }
    return {
        "test": "MX8 Information^3 tetrahedron temporal transfer",
        "status": "held-out cross-simulator conditional-height test",
        "source": {
            "directory": str(source_dir.resolve()),
            "repository": "https://github.com/openPMD/openPMD-example-datasets",
            "producer": "Warp 4",
            "iterations": list(expected),
            "sha256": hashes,
        },
        "frozen_split": {
            "development": list(DEVELOPMENT),
            "quarantined_unused": list(QUARANTINE),
            "test": list(TEST),
        },
        "coefficients_by_component": {
            model: {
                component: coefficients[model][index].tolist()
                for index, component in enumerate(COMPONENTS)
            }
            for model in ("blind", "additive", "relation")
        },
        "fit_diagnostics": fit_diagnostics,
        "test_particle_counts": test_counts,
        "models": model_metrics,
        "primary_relation_vs_additive_gate": gate,
        "per_snapshot_error_sums": per_snapshot_sums,
        "posthoc_local_relation_diagnostic": {
            "status": "exploratory explanation after the frozen gate; not part of confirmation",
            "development": local_relation_diagnostic(source_dir, DEVELOPMENT),
            "test": local_relation_diagnostic(source_dir, TEST),
        },
        "mathematical_identity": {
            "vertices_xyz": [
                [int(x), int(y), int(x * y)] for x, y in zip(ROUTE_X, ROUTE_Y)
            ],
            "closure": "x*y*r = 1",
            "pairwise_dot_product": -1,
            "edge_length": float(2 * np.sqrt(2)),
            "interpretation": "regular tetrahedron / parity lift; exact algebra, not a fitted result",
        },
        "claim_boundary": {
            "tested": "whether the xy relation term adds reusable held-out route-strength information",
            "not_tested": "universal fractality, novel Maxwell dynamics, or prediction without held-out common magnitude and route occupancy",
        },
    }


def make_figure(path: Path, results: dict) -> None:
    names = ("independent_marginals", "joint_sign", "blind", "additive", "relation")
    labels = ("marginals", "joint sign", "route blind", "two axes", "+ relation")
    colours = ("#999999", "#6f8faf", "#b98c4a", "#577590", "#1b7f79")
    figure, axes = plt.subplots(1, 3, figsize=(14, 4.5), constrained_layout=True)
    for axis, metric, title in (
        (axes[0], "relative_l2", "Held-out relative L2 (lower is better)"),
        (axes[1], "vector_correlation", "Held-out vector correlation"),
        (axes[2], "median_angular_error_deg", "Median direction error (degrees)"),
    ):
        values = [results["models"][name][metric] for name in names]
        axis.bar(labels, values, color=colours)
        axis.set_title(title)
        axis.tick_params(axis="x", rotation=25)
        axis.set_ylim(bottom=0)
        for index, value in enumerate(values):
            axis.text(index, value, f"{value:.3g}", ha="center", va="bottom", fontsize=8)
    gate = results["primary_relation_vs_additive_gate"]
    figure.suptitle(
        "MX8 frozen temporal transfer — relation vs additive L2 change "
        f"{100 * gate['observed_relative_l2_improvement_fraction']:+.2f}% "
        f"({'PASS' if gate['frozen_gate_pass'] else 'FAIL'})"
    )
    figure.savefig(path, dpi=180)
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results = run(args.source_dir)
    result_path = args.output_dir / "MX8_INFORMATION3_TETRAHEDRON_TRANSFER_RESULTS.json"
    figure_path = args.output_dir / "MX8_INFORMATION3_TETRAHEDRON_TRANSFER.png"
    result_path.write_text(json.dumps(results, indent=2, allow_nan=False), encoding="utf-8")
    make_figure(figure_path, results)
    print(
        json.dumps(
            {
                "result": str(result_path),
                "figure": str(figure_path),
                "gate": results["primary_relation_vs_additive_gate"],
                "additive": results["models"]["additive"],
                "relation": results["models"]["relation"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
