#!/usr/bin/env python3
"""PN14: child-to-adult modular wave, adult-growth ridge, and phase collapse.

Source data are deterministic raw integers and exact prime arithmetic. No download is
required. Development mode opens only the previously inspected scales 8-10. Target
mode refuses to calculate scale 11 unless the frozen file hashes match and the
explicit unlock token is supplied.
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


HERE = Path(__file__).resolve().parent
FIDELITY = HERE / "PN14_ADULT_WAVE_RIDGE_FIDELITY_PACKET_v1.md"
PROTOCOL = HERE / "PN14_ADULT_WAVE_RIDGE_PROTOCOL_v1_FROZEN.md"
SOURCE = HERE / "pn14_adult_wave_ridge.py"
VALIDATOR = HERE / "validate_pn14_adult_wave_ridge.py"
MANIFEST = HERE / "PN14_TARGET_FREEZE_MANIFEST.json"
DEV_RESULTS = HERE / "PN14_DEVELOPMENT_RESULTS.json"
DEV_TEMPLATE = HERE / "PN14_DEVELOPMENT_TEMPLATE.json"
DEV_CSV = HERE / "PN14_DEVELOPMENT_SECTORS.csv"
TARGET_RESULTS = HERE / "PN14_TARGET_RESULTS.json"
TARGET_CSV = HERE / "PN14_TARGET_SECTORS.csv"
FIGURE = HERE / "PN14_ADULT_WAVE_RIDGE.png"

TARGET_UNLOCK = "PN14_TARGET_FROZEN"
SCALES_DEVELOPMENT = (8, 9, 10)
SCALE_TARGET = 11
K_GATES = 9
PHASE_SECTORS = 16
BLOCK_MULTIPLIER = 8
SEED = 14072126
MIN_TARGET_PRIMES = 100


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def base_primes(limit: int) -> np.ndarray:
    sieve = np.ones(limit + 1, dtype=bool)
    sieve[:2] = False
    for number in range(2, math.isqrt(limit) + 1):
        if sieve[number]:
            sieve[number * number : limit + 1 : number] = False
    return np.flatnonzero(sieve).astype(np.int64)


def segmented_prime_and_paid_masks(low: int, high: int, paid_limit: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return raw numbers, exact prime mask, and survival through primes <= paid_limit."""
    numbers = np.arange(low, high, dtype=np.int64)
    prime_mask = np.ones(high - low, dtype=bool)
    paid_mask = np.ones(high - low, dtype=bool)
    for p64 in base_primes(math.isqrt(high - 1)):
        p = int(p64)
        start = max(p * p, ((low + p - 1) // p) * p)
        if start >= high:
            continue
        offset = start - low
        prime_mask[offset::p] = False
        if p <= paid_limit:
            paid_mask[offset::p] = False
    return numbers, prime_mask, paid_mask


def scale_anchor(scale: int) -> int:
    return 4 * 10**scale


def gate_geometry(scale: int) -> dict[str, Any]:
    anchor = scale_anchor(scale)
    threshold = anchor**0.45
    table = base_primes(int(math.ceil(threshold)) + 2)
    last = int(np.searchsorted(table, threshold, side="right") - 1)
    gates = table[last - np.arange(K_GATES, dtype=np.int64)]
    pairs: list[dict[str, Any]] = []
    for index, (q64, r64) in enumerate(zip(gates[:-1], gates[1:])):
        q, r = int(q64), int(r64)
        joint = q * r
        gap = abs(q - r)
        pairs.append(
            {
                "pair_index": index,
                "q": q,
                "r": r,
                "gap": gap,
                "joint_period": joint,
                "relative_phase_period": joint / gap,
            }
        )
    joint_values = np.asarray([row["joint_period"] for row in pairs], dtype=np.float64)
    median_joint = float(np.median(joint_values))
    representative_index = min(
        range(len(pairs)), key=lambda index: (abs(pairs[index]["joint_period"] - median_joint), index)
    )
    return {
        "scale": scale,
        "anchor": anchor,
        "threshold_n_pow_0p45": threshold,
        "gates_descending": [int(value) for value in gates],
        "pairs": pairs,
        "median_joint_period": median_joint,
        "representative_pair_index": representative_index,
        "representative_pair": pairs[representative_index],
    }


def circular_distance(first: float, second: float) -> float:
    distance = abs(first - second) % 1.0
    return min(distance, 1.0 - distance)


def phase_at(number: int | np.ndarray, q: int, r: int) -> float | np.ndarray:
    period = q * r
    delta = r - q
    return np.mod(np.asarray(number, dtype=np.int64) * delta, period).astype(np.float64) / period


def first_forward_phase_position(anchor: int, q: int, r: int, target: float) -> tuple[int, float]:
    """Nearest point to target on the first local relative-phase revolution after anchor."""
    period = q * r
    delta = r - q
    start_phase = float(phase_at(anchor, q, r))
    if delta < 0:
        distance = (start_phase - target) % 1.0
    else:
        distance = (target - start_phase) % 1.0
    estimate = int(round(distance * period / abs(delta)))
    candidates = [max(0, estimate + shift) for shift in range(-3, 4)]
    offset = min(candidates, key=lambda value: circular_distance(float(phase_at(anchor + value, q, r)), target))
    position = anchor + offset
    return position, float(phase_at(position, q, r))


def describe(values: np.ndarray) -> dict[str, float | int | None]:
    if len(values) == 0:
        return {"n": 0, "mean": None, "sd": None, "p05": None, "median": None, "p95": None}
    quantiles = np.quantile(values, (0.05, 0.5, 0.95))
    return {
        "n": int(len(values)),
        "mean": float(np.mean(values)),
        "sd": float(np.std(values)),
        "p05": float(quantiles[0]),
        "median": float(quantiles[1]),
        "p95": float(quantiles[2]),
    }


def circular_mean(turns: np.ndarray) -> float | None:
    if len(turns) == 0:
        return None
    vector = np.mean(np.exp(2j * math.pi * turns))
    return float((np.angle(vector) / (2 * math.pi)) % 1.0)


def sector_measurement(
    scale: int, geometry: dict[str, Any], sector: int, prime_table: np.ndarray
) -> dict[str, Any]:
    anchor = int(geometry["anchor"])
    gates = geometry["gates_descending"]
    representative = geometry["representative_pair"]
    q, r = int(representative["q"]), int(representative["r"])
    distant = int(gates[-1])
    center_target = (sector + 0.5) / PHASE_SECTORS
    center_number, center_phase = first_forward_phase_position(anchor, q, r, center_target)
    half_width = BLOCK_MULTIPLIER * max(q, r) // 2
    low = center_number - half_width
    high = center_number + half_width + 1

    numbers = np.arange(low, high, dtype=np.int64)
    prime_mask = np.ones(high - low, dtype=bool)
    paid_mask = np.ones(high - low, dtype=bool)
    for p64 in prime_table:
        p = int(p64)
        if p * p >= high and p > max(q, r):
            break
        start = max(p * p, ((low + p - 1) // p) * p)
        if start >= high:
            continue
        offset = start - low
        prime_mask[offset::p] = False
        if p <= max(q, r):
            paid_mask[offset::p] = False

    theta = np.asarray(phase_at(numbers, q, r), dtype=np.float64)
    wrong_theta = np.asarray(phase_at(numbers, q, distant), dtype=np.float64)
    a_q = 2.0 * (numbers % q).astype(np.float64) / q
    a_r = 2.0 * (numbers % r).astype(np.float64) / r
    product = (a_q - 1.0) * (a_r - 1.0)
    sector_mask = np.minimum((theta * PHASE_SECTORS).astype(np.int64), PHASE_SECTORS - 1) == sector
    populations = {
        "raw": sector_mask,
        "prime": sector_mask & prime_mask,
        "late_composite": sector_mask & paid_mask & (~prime_mask),
    }
    output: dict[str, Any] = {
        "scale": scale,
        "sector": sector,
        "theta_center": center_target,
        "center_number": center_number,
        "center_theta": center_phase,
        "block_low": low,
        "block_high": high,
        "q": q,
        "r": r,
        "distant_gate": distant,
        "theta_span": [float(np.min(theta)), float(np.max(theta))],
        "closure_error": float(max(np.max(np.abs(a_q + (2.0 - a_q) - 2.0)), np.max(np.abs(a_r + (2.0 - a_r) - 2.0)))),
        "populations": {},
    }
    for name, mask in populations.items():
        values = product[mask]
        summary = describe(values)
        summary["mean_theta"] = circular_mean(theta[mask])
        summary["mean_wrong_theta"] = circular_mean(wrong_theta[mask])
        output["populations"][name] = summary
    return output


def periodic_regrid(x: np.ndarray, y: np.ndarray, target: np.ndarray) -> np.ndarray:
    order = np.argsort(x)
    x_sorted = x[order]
    y_sorted = y[order]
    unique_x: list[float] = []
    unique_y: list[float] = []
    for value in np.unique(x_sorted):
        selected = np.isclose(x_sorted, value, rtol=0.0, atol=1e-12)
        unique_x.append(float(np.mean(x_sorted[selected])))
        unique_y.append(float(np.mean(y_sorted[selected])))
    x_base = np.asarray(unique_x, dtype=np.float64)
    y_base = np.asarray(unique_y, dtype=np.float64)
    if len(x_base) < 2:
        return np.full_like(target, float(y_base[0]) if len(y_base) else np.nan)
    x_extended = np.concatenate([x_base - 1.0, x_base, x_base + 1.0])
    y_extended = np.tile(y_base, 3)
    return np.interp(target, x_extended, y_extended)


def curve_from_sectors(rows: list[dict[str, Any]], population: str) -> dict[str, Any]:
    centers = np.asarray([row["theta_center"] for row in rows], dtype=np.float64)
    means = np.asarray([row["populations"][population]["mean"] for row in rows], dtype=np.float64)
    wrong_x = np.asarray([row["populations"][population]["mean_wrong_theta"] for row in rows], dtype=np.float64)
    wrong_curve = periodic_regrid(wrong_x, means, centers)
    return {
        "theta_centers": centers.tolist(),
        "means": means.tolist(),
        "wrong_coordinate_theta": wrong_x.tolist(),
        "wrong_coordinate_regridded_means": wrong_curve.tolist(),
        "counts": [int(row["populations"][population]["n"]) for row in rows],
    }


def run_scale(scale: int) -> dict[str, Any]:
    geometry = gate_geometry(scale)
    representative = geometry["representative_pair"]
    max_forward = int(math.ceil(float(representative["relative_phase_period"])))
    max_high = int(geometry["anchor"]) + max_forward + BLOCK_MULTIPLIER * int(representative["q"])
    prime_table = base_primes(math.isqrt(max_high) + 1)
    sectors = [sector_measurement(scale, geometry, sector, prime_table) for sector in range(PHASE_SECTORS)]
    curves = {name: curve_from_sectors(sectors, name) for name in ("raw", "prime", "late_composite")}
    return {"scale": scale, "geometry": geometry, "sectors": sectors, "curves": curves}


def rmse(first: np.ndarray, second: np.ndarray) -> float:
    return float(np.sqrt(np.mean((first - second) ** 2)))


def correlation(first: np.ndarray, second: np.ndarray) -> float:
    return float(np.corrcoef(first, second)[0, 1])


def development_metrics(scales: list[dict[str, Any]], template: np.ndarray) -> dict[str, Any]:
    centers = np.asarray(scales[0]["curves"]["prime"]["theta_centers"], dtype=np.float64)
    analytic = 1.0 / 3.0 - 2.0 * centers + 2.0 * centers**2
    leave_one_out: list[dict[str, float | int]] = []
    for index, scale in enumerate(scales):
        others = [
            np.asarray(row["curves"]["prime"]["means"], dtype=np.float64)
            for other_index, row in enumerate(scales)
            if other_index != index
        ]
        held = np.asarray(scale["curves"]["prime"]["means"], dtype=np.float64)
        peer = np.mean(others, axis=0)
        leave_one_out.append(
            {"scale": int(scale["scale"]), "correlation": correlation(held, peer), "rmse": rmse(held, peer)}
        )
    return {
        "leave_one_scale_out_prime": leave_one_out,
        "template_analytic_correlation": correlation(template, analytic),
        "template_analytic_rmse": rmse(template, analytic),
    }


def write_sector_csv(path: Path, scales: list[dict[str, Any]]) -> None:
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
                            "scale": scale["scale"], "sector": sector["sector"],
                            "theta_center": sector["theta_center"], "center_number": sector["center_number"],
                            "q": sector["q"], "r": sector["r"], "population": population, **summary,
                        }
                    )


def run_development() -> None:
    scales = [run_scale(scale) for scale in SCALES_DEVELOPMENT]
    prime_curves = [np.asarray(row["curves"]["prime"]["means"], dtype=np.float64) for row in scales]
    template = np.mean(prime_curves, axis=0)
    centers = np.asarray(scales[0]["curves"]["prime"]["theta_centers"], dtype=np.float64)
    result = {
        "test_id": "PN14/CHILD-ADULT-RIDGE/v1",
        "mode": "DEVELOPMENT ONLY; SCALE 11 NOT CALCULATED",
        "constants": {
            "development_scales": list(SCALES_DEVELOPMENT), "target_scale": SCALE_TARGET,
            "phase_sectors": PHASE_SECTORS, "block_multiplier": BLOCK_MULTIPLIER,
            "gate_exponent": 0.45, "expected_adult_growth": 10.0**0.9,
        },
        "scales": scales,
        "development_metrics": development_metrics(scales, template),
    }
    template_result = {
        "test_id": "PN14/CHILD-ADULT-RIDGE/v1",
        "status": "FROZEN DEVELOPMENT TEMPLATE; NO SCALE-11 VALUES",
        "theta_centers": centers.tolist(),
        "prime_template": template.tolist(),
        "prime_grand_mean": float(np.mean(template)),
        "development_scales": list(SCALES_DEVELOPMENT),
    }
    DEV_RESULTS.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    DEV_TEMPLATE.write_text(json.dumps(template_result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_sector_csv(DEV_CSV, scales)
    print(json.dumps({"wrote": [DEV_RESULTS.name, DEV_TEMPLATE.name, DEV_CSV.name], "target_opened": False}, indent=2))


def verify_manifest() -> None:
    frozen = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures: list[str] = []
    for name, expected in frozen["files"].items():
        actual = sha256(HERE / name)
        if actual != expected:
            failures.append(f"{name}: expected {expected}, got {actual}")
    if failures:
        raise RuntimeError("PN14 target freeze mismatch:\n" + "\n".join(failures))


def target_metrics(target: dict[str, Any], template_data: dict[str, Any], development: dict[str, Any]) -> dict[str, Any]:
    template = np.asarray(template_data["prime_template"], dtype=np.float64)
    curve = np.asarray(target["curves"]["prime"]["means"], dtype=np.float64)
    wrong = np.asarray(target["curves"]["prime"]["wrong_coordinate_regridded_means"], dtype=np.float64)
    zero = np.zeros_like(curve)
    correct_rmse = rmse(curve, template)
    zero_rmse = rmse(curve, zero)

    dev_geometries = {int(row["scale"]): row["geometry"] for row in development["scales"]}
    j9 = float(dev_geometries[9]["median_joint_period"])
    j10 = float(dev_geometries[10]["median_joint_period"])
    j11 = float(target["geometry"]["median_joint_period"])
    g9 = j10 / j9
    g10 = j11 / j10
    ridge_a = 2.0 * g9 / (g9 + g10)
    ridge_b = 2.0 - ridge_a
    expected = 10.0**0.9
    minimum_count = min(target["curves"]["prime"]["counts"])
    arm_a_checks = {
        "growth_within_five_percent": abs(g10 / expected - 1.0) <= 0.05,
        "ridge_within_0p98_1p02": 0.98 <= ridge_a <= 1.02,
    }
    arm_b_checks = {
        "minimum_prime_count": minimum_count >= MIN_TARGET_PRIMES,
        "correlation_at_least_0p90": correlation(curve, template) >= 0.90,
        "rmse_at_most_0p075": correct_rmse <= 0.075,
        "forty_percent_better_than_zero": correct_rmse <= 0.60 * zero_rmse,
        "better_than_wrong_coordinate": correct_rmse < rmse(wrong, template),
    }
    return {
        "adult_scale_ridge": {
            "J9": j9, "J10": j10, "J11": j11, "G9": g9, "G10": g10,
            "G10_over_G9": g10 / g9, "ridge_A": ridge_a, "ridge_B": ridge_b,
            "expected_10_pow_0p9": expected, "relative_error_G10": g10 / expected - 1.0,
            "checks": arm_a_checks, "verdict": "SUPPORTED" if all(arm_a_checks.values()) else "NOT SUPPORTED",
        },
        "phase_collapse": {
            "target_template_correlation": correlation(curve, template),
            "target_template_rmse": correct_rmse,
            "target_zero_rmse": zero_rmse,
            "target_wrong_coordinate_template_rmse": rmse(wrong, template),
            "minimum_target_prime_sector_count": minimum_count,
            "checks": arm_b_checks,
            "verdict": (
                "INCONCLUSIVE" if not arm_b_checks["minimum_prime_count"]
                else "SUPPORTED" if all(arm_b_checks.values()) else "NOT SUPPORTED"
            ),
        },
    }


def make_figure(development: dict[str, Any], target: dict[str, Any], metrics: dict[str, Any]) -> None:
    import matplotlib.pyplot as plt

    centers = np.asarray(target["curves"]["prime"]["theta_centers"], dtype=np.float64)
    template_data = json.loads(DEV_TEMPLATE.read_text(encoding="utf-8"))
    template = np.asarray(template_data["prime_template"], dtype=np.float64)
    target_prime = np.asarray(target["curves"]["prime"]["means"], dtype=np.float64)
    target_late = np.asarray(target["curves"]["late_composite"]["means"], dtype=np.float64)
    target_raw = np.asarray(target["curves"]["raw"]["means"], dtype=np.float64)
    analytic = 1.0 / 3.0 - 2.0 * centers + 2.0 * centers**2

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))
    ax = axes[0]
    ax.plot(centers * 2.0, analytic, color="0.5", linestyle="--", label="analytic raw sawtooth")
    ax.plot(centers * 2.0, template, color="#1f77b4", marker="o", label="scales 8-10 prime template")
    ax.plot(centers * 2.0, target_prime, color="#d62728", marker="o", label="scale 11 primes")
    ax.plot(centers * 2.0, target_late, color="#ff9f1c", alpha=0.85, label="scale 11 late composites")
    ax.plot(centers * 2.0, target_raw, color="#2ca02c", alpha=0.75, label="scale 11 raw")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.axvline(1, color="black", linewidth=0.8, alpha=0.4)
    ax.set(xlabel="adult relative phase on ARA 0-2", ylabel="signed child product Z", title="Equal-phase adult-wave shape")
    ax.legend(fontsize=8)

    ax = axes[1]
    adult = metrics["adult_scale_ridge"]
    growths = [
        development["scales"][1]["geometry"]["median_joint_period"] / development["scales"][0]["geometry"]["median_joint_period"],
        adult["G9"], adult["G10"],
    ]
    ax.plot([8.5, 9.5, 10.5], growths, marker="o", color="#7b2cbf", label="observed adult growth")
    ax.axhline(10.0**0.9, color="0.4", linestyle="--", label="10^0.9")
    ax.set(xlabel="decimal rung transition", ylabel="J(d+1) / J(d)", title="Adult growth factors meet near one ridge")
    ax.set_xticks([8.5, 9.5, 10.5], ["8->9", "9->10", "10->11"])
    ax.legend(fontsize=8)
    fig.suptitle("PN14 child-to-adult wave and adult-rung ridge", fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIGURE, dpi=180)
    plt.close(fig)


def run_target(unlock: str) -> None:
    if unlock != TARGET_UNLOCK:
        raise RuntimeError("Target locked: supply --unlock PN14_TARGET_FROZEN only after the freeze manifest exists")
    verify_manifest()
    development = json.loads(DEV_RESULTS.read_text(encoding="utf-8"))
    template = json.loads(DEV_TEMPLATE.read_text(encoding="utf-8"))
    target = run_scale(SCALE_TARGET)
    metrics = target_metrics(target, template, development)
    result = {
        "test_id": "PN14/CHILD-ADULT-RIDGE/v1", "mode": "FROZEN SCALE-11 TARGET",
        "manifest_sha256": sha256(MANIFEST), "target": target, "metrics": metrics,
    }
    TARGET_RESULTS.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_sector_csv(TARGET_CSV, [target])
    make_figure(development, target, metrics)
    print(json.dumps({"wrote": [TARGET_RESULTS.name, TARGET_CSV.name, FIGURE.name], "metrics": metrics}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("development", "target"), required=True)
    parser.add_argument("--unlock", default="")
    args = parser.parse_args()
    if args.mode == "development":
        run_development()
    else:
        run_target(args.unlock)


if __name__ == "__main__":
    main()
