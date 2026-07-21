#!/usr/bin/env python3
"""PN15: full-square-root child closure, adult growth ridge, and phase transfer.

Deterministic integer arithmetic is the only data source. Development mode calculates
scales 8-11. Target mode refuses to calculate scale 12 unless the frozen manifest
matches and the explicit unlock token is supplied.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from pn14_adult_wave_ridge import (
    base_primes,
    circular_mean,
    correlation,
    describe,
    first_forward_phase_position,
    periodic_regrid,
    phase_at,
    rmse,
)


HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "PN15_TARGET_FREEZE_MANIFEST.json"
DEV_RESULTS = HERE / "PN15_DEVELOPMENT_RESULTS.json"
DEV_TEMPLATE = HERE / "PN15_DEVELOPMENT_TEMPLATE.json"
DEV_CSV = HERE / "PN15_DEVELOPMENT_SECTORS.csv"
TARGET_RESULTS = HERE / "PN15_TARGET_RESULTS.json"
TARGET_CSV = HERE / "PN15_TARGET_SECTORS.csv"

DEVELOPMENT_SCALES = (8, 9, 10, 11)
TARGET_SCALE = 12
TARGET_UNLOCK = "PN15_TARGET_FROZEN"
K_GATES = 9
SECTORS = 16
BLOCK_MULTIPLIER = 2
SEED = 15072126
MIN_TARGET_PRIMES = 1_000


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def anchor(scale: int) -> int:
    return 4 * 10**scale


def gate_geometry(scale: int) -> dict[str, Any]:
    parent = anchor(scale)
    boundary = math.sqrt(parent)
    table = base_primes(int(math.ceil(boundary)) + 1_000)
    last = int(np.searchsorted(table, boundary, side="right") - 1)
    gates = table[last - np.arange(K_GATES, dtype=np.int64)]
    first_omitted_above = int(table[last + 1])
    log_parent = math.log(parent)
    pairs: list[dict[str, Any]] = []
    for index, (q64, r64) in enumerate(zip(gates[:-1], gates[1:])):
        q, r = int(q64), int(r64)
        joint = q * r
        child_a = 2.0 * math.log(q) / log_parent
        child_b = 2.0 * math.log(r) / log_parent
        pairs.append(
            {
                "pair_index": index,
                "q": q,
                "r": r,
                "gap": abs(q - r),
                "child_A_coordinate": child_a,
                "child_B_coordinate": child_b,
                "adult_coordinate_sum": child_a + child_b,
                "joint_period": joint,
                "adult_fill_of_anchor": joint / parent,
                "relative_phase_period": joint / abs(q - r),
            }
        )
    joint_values = np.asarray([row["joint_period"] for row in pairs], dtype=np.float64)
    median_joint = float(np.median(joint_values))
    representative_index = min(
        range(len(pairs)), key=lambda index: (abs(pairs[index]["joint_period"] - median_joint), index)
    )
    return {
        "scale": scale,
        "anchor": parent,
        "sqrt_anchor": boundary,
        "gates_descending": [int(value) for value in gates],
        "first_omitted_prime_above_boundary": first_omitted_above,
        "pairs": pairs,
        "median_joint_period": median_joint,
        "median_adult_fill": median_joint / parent,
        "representative_pair_index": representative_index,
        "representative_pair": pairs[representative_index],
    }


def prime_mask_for_block(low: int, high: int, prime_table: np.ndarray) -> np.ndarray:
    mask = np.ones(high - low, dtype=bool)
    for p64 in prime_table:
        p = int(p64)
        if p * p >= high:
            break
        start = max(p * p, ((low + p - 1) // p) * p)
        if start < high:
            mask[start - low :: p] = False
    return mask


def sector_measurement(
    scale: int, geometry: dict[str, Any], sector: int, prime_table: np.ndarray
) -> dict[str, Any]:
    representative = geometry["representative_pair"]
    q, r = int(representative["q"]), int(representative["r"])
    distant = int(geometry["gates_descending"][-1])
    desired = (sector + 0.5) / SECTORS
    center_number, center_phase = first_forward_phase_position(int(geometry["anchor"]), q, r, desired)
    half_width = BLOCK_MULTIPLIER * max(q, r) // 2
    low, high = center_number - half_width, center_number + half_width + 1
    numbers = np.arange(low, high, dtype=np.int64)
    is_prime = prime_mask_for_block(low, high, prime_table)
    theta = np.asarray(phase_at(numbers, q, r), dtype=np.float64)
    theta_wrong = np.asarray(phase_at(numbers, q, distant), dtype=np.float64)
    a_q = 2.0 * (numbers % q).astype(np.float64) / q
    a_r = 2.0 * (numbers % r).astype(np.float64) / r
    product = (a_q - 1.0) * (a_r - 1.0)
    selected = np.minimum((theta * SECTORS).astype(np.int64), SECTORS - 1) == sector
    populations = {"raw": selected, "prime": selected & is_prime, "composite": selected & (~is_prime)}
    output: dict[str, Any] = {
        "scale": scale,
        "sector": sector,
        "theta_center": desired,
        "center_number": center_number,
        "center_theta": center_phase,
        "block_low": low,
        "block_high": high,
        "q": q,
        "r": r,
        "distant_gate": distant,
        "closure_error": float(
            max(
                np.max(np.abs(a_q + (2.0 - a_q) - 2.0)),
                np.max(np.abs(a_r + (2.0 - a_r) - 2.0)),
            )
        ),
        "populations": {},
    }
    for name, mask in populations.items():
        values = product[mask]
        summary = describe(values)
        summary["mean_theta"] = circular_mean(theta[mask])
        summary["mean_wrong_theta"] = circular_mean(theta_wrong[mask])
        output["populations"][name] = summary
    return output


def curve_from_sectors(rows: list[dict[str, Any]], population: str) -> dict[str, Any]:
    centers = np.asarray([row["theta_center"] for row in rows], dtype=np.float64)
    means = np.asarray([row["populations"][population]["mean"] for row in rows], dtype=np.float64)
    wrong_x = np.asarray([row["populations"][population]["mean_wrong_theta"] for row in rows], dtype=np.float64)
    return {
        "theta_centers": centers.tolist(),
        "means": means.tolist(),
        "counts": [int(row["populations"][population]["n"]) for row in rows],
        "wrong_coordinate_theta": wrong_x.tolist(),
        "wrong_coordinate_regridded_means": periodic_regrid(wrong_x, means, centers).tolist(),
    }


def run_scale(scale: int) -> dict[str, Any]:
    geometry = gate_geometry(scale)
    pair = geometry["representative_pair"]
    max_forward = int(math.ceil(float(pair["relative_phase_period"])))
    max_high = int(geometry["anchor"]) + max_forward + BLOCK_MULTIPLIER * int(pair["q"])
    prime_table = base_primes(math.isqrt(max_high) + 1)
    sectors = [sector_measurement(scale, geometry, sector, prime_table) for sector in range(SECTORS)]
    curves = {name: curve_from_sectors(sectors, name) for name in ("raw", "prime", "composite")}
    return {"scale": scale, "geometry": geometry, "sectors": sectors, "curves": curves}


def write_csv(path: Path, scales: list[dict[str, Any]]) -> None:
    fields = [
        "scale", "sector", "theta_center", "center_number", "q", "r", "population", "n", "mean", "sd",
        "p05", "median", "p95", "mean_theta", "mean_wrong_theta",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for scale in scales:
            for sector in scale["sectors"]:
                for population, summary in sector["populations"].items():
                    writer.writerow(
                        {
                            "scale": scale["scale"],
                            "sector": sector["sector"],
                            "theta_center": sector["theta_center"],
                            "center_number": sector["center_number"],
                            "q": sector["q"],
                            "r": sector["r"],
                            "population": population,
                            **summary,
                        }
                    )


def development_metrics(scales: list[dict[str, Any]], template: np.ndarray) -> dict[str, Any]:
    centers = np.asarray(scales[0]["curves"]["prime"]["theta_centers"], dtype=np.float64)
    analytic = 1.0 / 3.0 - 2.0 * centers + 2.0 * centers**2
    leave_one_out: list[dict[str, float | int]] = []
    for index, row in enumerate(scales):
        held = np.asarray(row["curves"]["prime"]["means"], dtype=np.float64)
        peer = np.mean(
            [
                np.asarray(other["curves"]["prime"]["means"], dtype=np.float64)
                for other_index, other in enumerate(scales)
                if other_index != index
            ],
            axis=0,
        )
        leave_one_out.append(
            {"scale": int(row["scale"]), "correlation": correlation(held, peer), "rmse": rmse(held, peer)}
        )
    return {
        "leave_one_scale_out_prime": leave_one_out,
        "template_analytic_correlation": correlation(template, analytic),
        "template_analytic_rmse": rmse(template, analytic),
    }


def run_development() -> None:
    scales = [run_scale(scale) for scale in DEVELOPMENT_SCALES]
    prime_curves = [np.asarray(row["curves"]["prime"]["means"], dtype=np.float64) for row in scales]
    template = np.mean(prime_curves, axis=0)
    centers = scales[0]["curves"]["prime"]["theta_centers"]
    result = {
        "test_id": "PN15/SQRT-CHILD-ADULT-RIDGE/v1",
        "mode": "DEVELOPMENT ONLY; SCALE 12 NOT CALCULATED",
        "constants": {
            "development_scales": list(DEVELOPMENT_SCALES),
            "target_scale": TARGET_SCALE,
            "boundary_exponent": 0.5,
            "expected_adult_growth": 10.0,
            "sectors": SECTORS,
            "block_multiplier": BLOCK_MULTIPLIER,
        },
        "scales": scales,
        "development_metrics": development_metrics(scales, template),
    }
    template_result = {
        "test_id": "PN15/SQRT-CHILD-ADULT-RIDGE/v1",
        "status": "FROZEN DEVELOPMENT TEMPLATE; NO SCALE-12 VALUES",
        "theta_centers": centers,
        "prime_template": template.tolist(),
        "prime_grand_mean": float(np.mean(template)),
        "development_scales": list(DEVELOPMENT_SCALES),
    }
    DEV_RESULTS.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    DEV_TEMPLATE.write_text(json.dumps(template_result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(DEV_CSV, scales)
    print(json.dumps({"wrote": [DEV_RESULTS.name, DEV_TEMPLATE.name, DEV_CSV.name], "target_opened": False}, indent=2))


def verify_manifest() -> None:
    frozen = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures: list[str] = []
    for name, expected in frozen["files"].items():
        actual = sha256(HERE / name)
        if actual != expected:
            failures.append(f"{name}: expected {expected}, got {actual}")
    if failures:
        raise RuntimeError("PN15 target freeze mismatch:\n" + "\n".join(failures))


def target_metrics(target: dict[str, Any], template_data: dict[str, Any], development: dict[str, Any]) -> dict[str, Any]:
    geometries = {int(row["scale"]): row["geometry"] for row in development["scales"]}
    j10 = float(geometries[10]["median_joint_period"])
    j11 = float(geometries[11]["median_joint_period"])
    j12 = float(target["geometry"]["median_joint_period"])
    g10, g11 = j11 / j10, j12 / j11
    ridge_a = 2.0 * g10 / (g10 + g11)
    ridge_b = 2.0 - ridge_a
    pair = target["geometry"]["representative_pair"]
    arm_a_checks = {
        "target_growth_within_one_percent_of_10": abs(g11 / 10.0 - 1.0) <= 0.01,
        "ridge_entries_within_0p995_1p005": 0.995 <= ridge_a <= 1.005 and 0.995 <= ridge_b <= 1.005,
        "children_and_sum_in_frozen_ranges": (
            0.995 <= pair["child_A_coordinate"] <= 1.0
            and 0.995 <= pair["child_B_coordinate"] <= 1.0
            and 1.99 <= pair["adult_coordinate_sum"] <= 2.0
        ),
        "adult_fill_in_frozen_range": 0.999 <= j12 / anchor(12) < 1.0,
    }

    template = np.asarray(template_data["prime_template"], dtype=np.float64)
    curve = np.asarray(target["curves"]["prime"]["means"], dtype=np.float64)
    wrong = np.asarray(target["curves"]["prime"]["wrong_coordinate_regridded_means"], dtype=np.float64)
    correct_rmse = rmse(curve, template)
    zero_rmse = rmse(curve, np.zeros_like(curve))
    rng = np.random.default_rng(SEED)
    permutation = rng.permutation(SECTORS)
    permuted_rmse = rmse(curve[permutation], template)
    minimum_count = min(target["curves"]["prime"]["counts"])
    arm_b_checks = {
        "minimum_prime_count": minimum_count >= MIN_TARGET_PRIMES,
        "correlation_at_least_0p95": correlation(curve, template) >= 0.95,
        "rmse_at_most_0p025": correct_rmse <= 0.025,
        "sixty_percent_better_than_zero": correct_rmse <= 0.40 * zero_rmse,
        "better_than_wrong_coordinate": correct_rmse < rmse(wrong, template),
    }
    return {
        "full_sqrt_adult_ridge": {
            "J10": j10,
            "J11": j11,
            "J12": j12,
            "G10": g10,
            "G11": g11,
            "G11_over_G10": g11 / g10,
            "ridge_A": ridge_a,
            "ridge_B": ridge_b,
            "target_adult_fill": j12 / anchor(12),
            "representative_child_A": pair["child_A_coordinate"],
            "representative_child_B": pair["child_B_coordinate"],
            "representative_adult_sum": pair["adult_coordinate_sum"],
            "checks": arm_a_checks,
            "verdict": "SUPPORTED" if all(arm_a_checks.values()) else "NOT SUPPORTED",
        },
        "phase_transfer": {
            "target_template_correlation": correlation(curve, template),
            "target_template_rmse": correct_rmse,
            "target_zero_rmse": zero_rmse,
            "target_wrong_coordinate_template_rmse": rmse(wrong, template),
            "target_permutation_template_rmse": permuted_rmse,
            "minimum_target_prime_sector_count": minimum_count,
            "checks": arm_b_checks,
            "verdict": (
                "INCONCLUSIVE"
                if not arm_b_checks["minimum_prime_count"]
                else "SUPPORTED"
                if all(arm_b_checks.values())
                else "NOT SUPPORTED"
            ),
        },
    }


def run_target(unlock: str) -> None:
    if unlock != TARGET_UNLOCK:
        raise RuntimeError("Target locked: supply --unlock PN15_TARGET_FROZEN only after the manifest is sealed")
    verify_manifest()
    development = json.loads(DEV_RESULTS.read_text(encoding="utf-8"))
    template = json.loads(DEV_TEMPLATE.read_text(encoding="utf-8"))
    target = run_scale(TARGET_SCALE)
    metrics = target_metrics(target, template, development)
    result = {
        "test_id": "PN15/SQRT-CHILD-ADULT-RIDGE/v1",
        "mode": "FROZEN SCALE-12 TARGET",
        "manifest_sha256": sha256(MANIFEST),
        "target": target,
        "metrics": metrics,
    }
    TARGET_RESULTS.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(TARGET_CSV, [target])
    print(json.dumps({"wrote": [TARGET_RESULTS.name, TARGET_CSV.name], "metrics": metrics}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("development", "target"), required=True)
    parser.add_argument("--unlock", default="")
    arguments = parser.parse_args()
    if arguments.mode == "development":
        run_development()
    else:
        run_target(arguments.unlock)


if __name__ == "__main__":
    main()
