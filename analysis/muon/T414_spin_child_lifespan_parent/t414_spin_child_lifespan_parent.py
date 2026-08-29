#!/usr/bin/env python3
"""T414 spin-child / lifespan-parent analysis.

The protocol is frozen in T414_FROZEN_PROTOCOL.md.  The script reads the
public HDF4/NeXus histograms already downloaded for T413.  It keeps detector
shares (directional/spin channel) separate from detector totals (release
channel) throughout.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
MUON = HERE.parent
T413 = MUON / "T413_live_state_handover"
MANIFEST = T413 / "source" / "T413_SOURCE_MANIFEST.csv"
RAW = T413 / "source" / "raw"
RESULTS = HERE / "results"
PROTOCOL = HERE / "T414_FROZEN_PROTOCOL.md"

# Import runtime NumPy before exposing the legacy pyhdf vendor directory.
sys.path.insert(0, str(MUON / "_vendor"))
from pyhdf.SD import SD, SDC


GAMMA_DEV_MHZ_PER_G = 0.013549
T_MIN = 0.25
T_MAX = 6.00
LENGTH_US = T_MAX - T_MIN
PHASE_BINS = 32
BLOCK_SIZE = 8
NYQUIST_MHZ = 31.25
TAU_GRID = np.arange(1.80, 2.6001, 0.001)
SIDE_K = np.asarray([2, 3, 4, 5, 6, 8, 10, 12, 15, 18, 22, 26, 30], dtype=float)
SEED = 414


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_manifest() -> list[dict]:
    with MANIFEST.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["field_G"] = float(row["field_G"])
        row["temperature_K"] = float(row["temperature_K"])
        row["file_size"] = int(row["file_size"])
    return rows


def load_run(row: dict) -> dict:
    path = RAW / f"{row['run']}.nxs"
    if not path.exists() or path.stat().st_size != row["file_size"]:
        raise FileNotFoundError(f"missing or size-mismatched source: {path}")
    handle = SD(str(path), SDC.READ)
    counts = np.asarray(handle.select("counts")[:], dtype=float)
    time = np.asarray(handle.select("corrected_time")[:], dtype=float)
    frames = np.asarray(handle.select("frames_period")[:], dtype=float).reshape(-1)
    recorded_field = float(np.asarray(handle.select("magnetic_field")[:]).reshape(-1)[0])
    recorded_temperature = float(np.asarray(handle.select("temperature")[:]).reshape(-1)[0])
    if counts.shape != (192, 2048) or len(frames) != 2 or np.any(frames <= 0):
        raise ValueError(f"unexpected source structure in {path.name}")
    if abs(recorded_field - row["field_G"]) >= 0.51 or abs(recorded_temperature - row["temperature_K"]) >= 0.51:
        raise ValueError(f"manifest/source identity mismatch in {path.name}")
    eligible = (time >= T_MIN) & (time < T_MAX)
    return {
        "path": path,
        "time": time[eligible],
        "counts": (counts[:96, eligible], counts[96:, eligible]),
        "frames": frames,
    }


def fit_ab(rate: np.ndarray, time: np.ndarray, tau: float) -> tuple[float, float, np.ndarray]:
    decay = np.exp(-time / tau)
    design = np.column_stack((decay, np.ones(len(time))))
    beta = np.linalg.lstsq(design, rate, rcond=None)[0]
    candidates: list[tuple[float, float]] = []
    if beta[0] >= 0 and beta[1] >= 0:
        candidates.append((float(beta[0]), float(beta[1])))
    candidates.append((max(0.0, float(np.dot(decay, rate) / np.dot(decay, decay))), 0.0))
    candidates.append((0.0, max(0.0, float(np.mean(rate)))))
    best = min(candidates, key=lambda ab: float(np.sum((rate - (ab[0] * decay + ab[1])) ** 2)))
    fitted = best[0] * decay + best[1]
    return best[0], best[1], fitted


def calibrate_tau(rows: list[dict]) -> tuple[float, list[dict]]:
    development = [row for row in rows if row["split"] == "development"]
    series = []
    for row in development:
        data = load_run(row)
        for period, counts in zip(("RF on", "RF off"), data["counts"]):
            total_counts = counts.sum(axis=0)
            rate = total_counts / data["frames"][0 if period == "RF on" else 1]
            series.append((row["run"], period, data["time"], total_counts, rate, data["frames"][0 if period == "RF on" else 1]))

    objective = np.zeros(len(TAU_GRID), dtype=float)
    for index, tau in enumerate(TAU_GRID):
        score = 0.0
        for _, _, time, total_counts, rate, frames in series:
            _, _, fitted_rate = fit_ab(rate, time, float(tau))
            expected = np.maximum(frames * fitted_rate, 1.0)
            score += float(np.sum((total_counts - expected) ** 2 / expected))
        objective[index] = score
    best_index = int(np.argmin(objective))
    tau = float(TAU_GRID[best_index])
    curve = [{"tau_us": float(t), "objective": float(v)} for t, v in zip(TAU_GRID, objective)]
    return tau, curve


def sideband_frequencies(target: float) -> np.ndarray:
    offsets = SIDE_K / LENGTH_US
    values = np.concatenate((target - offsets, target + offsets))
    return values[values > 0.05]


def weighted_lstsq(design: np.ndarray, response: np.ndarray, weights: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray, float]:
    if weights is None:
        root = np.ones(len(design), dtype=float)
    else:
        root = np.sqrt(np.maximum(weights, 0.0) / max(float(np.mean(weights)), 1e-15))
    xw = design * root[:, None]
    yw = response * root[:, None] if response.ndim == 2 else response * root
    beta = np.linalg.lstsq(xw, yw, rcond=None)[0]
    fitted = design @ beta
    residual = response - fitted
    if response.ndim == 2:
        sse = float(np.sum(weights[:, None] * residual**2)) if weights is not None else float(np.sum(residual**2))
    else:
        sse = float(np.sum(weights * residual**2)) if weights is not None else float(np.sum(residual**2))
    return beta, fitted, sse


def harmonic_improvement_multi(share: np.ndarray, time: np.ndarray, frequency: float, weights: np.ndarray) -> tuple[float, np.ndarray, np.ndarray, float]:
    response = share.T
    u = time - float(np.mean(time))
    base = np.column_stack((np.ones(len(time)), u))
    _, _, sse0 = weighted_lstsq(base, response, weights)
    phase = 2.0 * np.pi * frequency * time
    full = np.column_stack((base, np.cos(phase), np.sin(phase)))
    beta, fitted, sse1 = weighted_lstsq(full, response, weights)
    improvement = max(0.0, (sse0 - sse1) / max(sse0, 1e-30))
    return float(improvement), beta[-2], beta[-1], sse1


def harmonic_improvement_scalar(values: np.ndarray, time: np.ndarray, frequency: float) -> tuple[float, np.ndarray, float, float]:
    u = time - float(np.mean(time))
    base = np.column_stack((np.ones(len(time)), u))
    _, _, sse0 = weighted_lstsq(base, values)
    phase = 2.0 * np.pi * frequency * time
    full = np.column_stack((base, np.cos(phase), np.sin(phase)))
    beta, fitted, sse1 = weighted_lstsq(full, values)
    improvement = max(0.0, (sse0 - sse1) / max(sse0, 1e-30))
    amplitude = float(math.hypot(float(beta[-2]), float(beta[-1])))
    peak_phase = float((math.atan2(float(beta[-1]), float(beta[-2])) / math.pi) % 2.0)
    return float(improvement), fitted, amplitude, peak_phase


def shuffled_blocks(values: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    count = len(values)
    blocks = [np.arange(i, min(i + BLOCK_SIZE, count)) for i in range(0, count, BLOCK_SIZE)]
    order = rng.permutation(len(blocks))
    indices = np.concatenate([blocks[i] for i in order])
    return values[indices]


def analyse_period(row: dict, period: str, counts: np.ndarray, frames: float, time: np.ndarray, tau: float) -> tuple[dict, list[dict]]:
    total_counts = counts.sum(axis=0)
    valid = total_counts > 0
    counts = counts[:, valid]
    total_counts = total_counts[valid]
    time = time[valid]
    rate = total_counts / frames
    field = row["field_G"]
    frequency = GAMMA_DEV_MHZ_PER_G * field
    alias_class = "primary" if frequency <= NYQUIST_MHZ else "alias_sensitivity"

    share = 96.0 * counts / total_counts[None, :]
    direction_target, coeff_cos, coeff_sin, _ = harmonic_improvement_multi(share, time, frequency, total_counts)
    sides = sideband_frequencies(frequency)
    direction_side = np.asarray([harmonic_improvement_multi(share, time, f, total_counts)[0] for f in sides])

    rng = np.random.default_rng(SEED + int(row["run"][-5:]) + (0 if period == "RF on" else 100000))
    broken_detector = np.empty_like(share)
    for column in range(share.shape[1]):
        broken_detector[:, column] = share[rng.permutation(share.shape[0]), column]
    direction_broken_detector = harmonic_improvement_multi(broken_detector, time, frequency, total_counts)[0]
    broken_share = shuffled_blocks(share.T, rng).T
    direction_broken_time = harmonic_improvement_multi(broken_share, time, frequency, total_counts)[0]

    a, b, fitted_rate = fit_ab(rate, time, tau)
    expected_counts = np.maximum(frames * fitted_rate, 1.0)
    release_residual = (total_counts - expected_counts) / np.sqrt(expected_counts)
    release_target, _, release_amplitude, release_peak_phase = harmonic_improvement_scalar(release_residual, time, frequency)
    release_side = np.asarray([harmonic_improvement_scalar(release_residual, time, f)[0] for f in sides])
    broken_release = shuffled_blocks(release_residual[:, None], rng)[:, 0]
    release_broken_time = harmonic_improvement_scalar(broken_release, time, frequency)[0]

    # Directional quadratures are normalized only for visualization; inferential
    # statistics above use the full 96-detector response.
    u = time - float(np.mean(time))
    base = np.column_stack((np.ones(len(time)), u))
    _, fitted_base, _ = weighted_lstsq(base, share.T, total_counts)
    share_residual = share.T - fitted_base
    norm_cos = max(float(np.linalg.norm(coeff_cos)), 1e-15)
    norm_sin = max(float(np.linalg.norm(coeff_sin)), 1e-15)
    direction_cos = share_residual @ coeff_cos / norm_cos
    direction_sin = share_residual @ coeff_sin / norm_sin

    x_spin = np.mod(2.0 * frequency * time, 2.0)
    x_parent = 2.0 * (1.0 - np.exp(-time / tau))
    phase_bin = np.minimum((x_spin / 2.0 * PHASE_BINS).astype(int), PHASE_BINS - 1)
    profile_rows = []
    for bin_index in range(PHASE_BINS):
        selected = phase_bin == bin_index
        if not np.any(selected):
            continue
        profile_rows.append({
            "split": row["split"],
            "alias_class": alias_class,
            "run": row["run"],
            "period": period,
            "field_G": field,
            "frequency_MHz": frequency,
            "phase_bin": bin_index,
            "x_spin_mid": 2.0 * (bin_index + 0.5) / PHASE_BINS,
            "direction_cos": float(np.average(direction_cos[selected], weights=total_counts[selected])),
            "direction_sin": float(np.average(direction_sin[selected], weights=total_counts[selected])),
            "release_residual": float(np.mean(release_residual[selected])),
            "parent_release_ARA": float(np.average(x_parent[selected], weights=total_counts[selected])),
            "time_us": float(np.average(time[selected], weights=total_counts[selected])),
            "count_weight": float(np.sum(total_counts[selected])),
            "sample_bins": int(np.sum(selected)),
        })

    metric = {
        "split": row["split"],
        "alias_class": alias_class,
        "run": row["run"],
        "period": period,
        "temperature_K": row["temperature_K"],
        "field_G": field,
        "frequency_MHz": frequency,
        "tau_dev_us": tau,
        "envelope_amplitude_rate": a,
        "envelope_background_rate": b,
        "direction_target": direction_target,
        "direction_sideband_median": float(np.median(direction_side)),
        "direction_target_sideband_ratio": float(direction_target / max(float(np.median(direction_side)), 1e-30)),
        "direction_sideband_percentile": float(np.mean(direction_target > direction_side)),
        "direction_broken_detector": direction_broken_detector,
        "direction_broken_time": direction_broken_time,
        "release_target": release_target,
        "release_sideband_median": float(np.median(release_side)),
        "release_target_sideband_ratio": float(release_target / max(float(np.median(release_side)), 1e-30)),
        "release_sideband_percentile": float(np.mean(release_target > release_side)),
        "release_broken_time": release_broken_time,
        "release_amplitude_z": release_amplitude,
        "release_peak_x_spin": release_peak_phase,
        "raw_total_counts": float(np.sum(total_counts)),
        "time_bins": int(len(time)),
    }
    return metric, profile_rows


def circular_resultant(phases: list[float]) -> tuple[float, float]:
    if not phases:
        return float("nan"), float("nan")
    angles = np.pi * np.asarray(phases)
    mean_vector = np.mean(np.exp(1j * angles))
    return float(abs(mean_vector)), float((np.angle(mean_vector) / np.pi) % 2.0)


def aggregate_metrics(metrics: list[dict]) -> dict:
    output: dict[str, dict] = {}
    groups = sorted({(m["split"], m["alias_class"], m["period"]) for m in metrics})
    for split, alias_class, period in groups:
        selected = [m for m in metrics if (m["split"], m["alias_class"], m["period"]) == (split, alias_class, period)]
        key = f"{split}|{alias_class}|{period}"
        resultant, peak = circular_resultant([m["release_peak_x_spin"] for m in selected])
        output[key] = {
            "run_count": len(selected),
            "median_direction_target_sideband_ratio": float(np.median([m["direction_target_sideband_ratio"] for m in selected])),
            "direction_run_win_fraction": float(np.mean([m["direction_target_sideband_ratio"] > 1 for m in selected])),
            "direction_broken_detector_win_fraction": float(np.mean([m["direction_target"] > m["direction_broken_detector"] for m in selected])),
            "direction_broken_time_win_fraction": float(np.mean([m["direction_target"] > m["direction_broken_time"] for m in selected])),
            "median_release_target_sideband_ratio": float(np.median([m["release_target_sideband_ratio"] for m in selected])),
            "release_run_win_fraction": float(np.mean([m["release_target_sideband_ratio"] > 1 for m in selected])),
            "release_broken_time_win_fraction": float(np.mean([m["release_target"] > m["release_broken_time"] for m in selected])),
            "release_phase_resultant": resultant,
            "release_phase_peak_x_spin": peak,
            "median_release_amplitude_z": float(np.median([m["release_amplitude_z"] for m in selected])),
        }

    gates: dict[str, dict] = {}
    for split in ("validation", "holdout"):
        split_key = "primary"
        period_results = [output.get(f"{split}|{split_key}|{period}") for period in ("RF on", "RF off")]
        if any(item is None for item in period_results):
            continue
        assert period_results[0] is not None and period_results[1] is not None
        direction = all(
            item["median_direction_target_sideband_ratio"] > 1
            and item["direction_run_win_fraction"] > 0.5
            and item["direction_broken_detector_win_fraction"] > 0.5
            and item["direction_broken_time_win_fraction"] > 0.5
            for item in period_results
        )
        release = all(
            item["median_release_target_sideband_ratio"] > 1
            and item["release_run_win_fraction"] > 0.5
            and item["release_broken_time_win_fraction"] > 0.5
            for item in period_results
        )
        on_peak = period_results[0]["release_phase_peak_x_spin"]
        off_peak = period_results[1]["release_phase_peak_x_spin"]
        phase_distance = min(abs(on_peak - off_peak), 2.0 - abs(on_peak - off_peak))
        phase_reproduction = (
            period_results[0]["release_phase_resultant"] > 0.5
            and period_results[1]["release_phase_resultant"] > 0.5
            and phase_distance < 0.25
        )
        gates[split] = {
            "spin_child_calibration_supported": bool(direction),
            "release_statistical_gate_without_phase": bool(release),
            "release_phase_reproduction": bool(phase_reproduction),
            "release_phase_distance_ARA": float(phase_distance),
            "total_release_phase_lock_supported": bool(release and phase_reproduction),
        }
    output["frozen_gates"] = gates
    return output


def aggregate_profiles(rows: list[dict]) -> list[dict]:
    output = []
    keys = sorted({(r["split"], r["alias_class"], r["period"], r["phase_bin"]) for r in rows})
    for split, alias_class, period, phase_bin in keys:
        selected = [r for r in rows if (r["split"], r["alias_class"], r["period"], r["phase_bin"]) == (split, alias_class, period, phase_bin)]
        for measure in ("direction_cos", "direction_sin", "release_residual", "parent_release_ARA", "time_us"):
            values = np.asarray([r[measure] for r in selected], dtype=float)
            output.append({
                "split": split,
                "alias_class": alias_class,
                "period": period,
                "phase_bin": phase_bin,
                "x_spin_mid": 2.0 * (phase_bin + 0.5) / PHASE_BINS,
                "measure": measure,
                "mean": float(np.mean(values)),
                "se": float(np.std(values, ddof=1) / math.sqrt(len(values))) if len(values) > 1 else 0.0,
                "run_count": len(values),
                "count_weight": float(np.sum([r["count_weight"] for r in selected])),
            })
    return output


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--splits", default="development,validation,holdout")
    parser.add_argument("--suffix", default="FULL")
    args = parser.parse_args()
    requested = {part.strip() for part in args.splits.split(",") if part.strip()}
    rows = read_manifest()

    tau, tau_curve = calibrate_tau(rows)
    selected = [row for row in rows if row["split"] in requested]
    metrics: list[dict] = []
    profiles: list[dict] = []
    source_hashes: list[dict] = []
    for index, row in enumerate(selected, start=1):
        print(f"[{index}/{len(selected)}] {row['split']} {row['run']} B={row['field_G']:g} G", flush=True)
        data = load_run(row)
        for p_index, (period, counts) in enumerate(zip(("RF on", "RF off"), data["counts"])):
            metric, profile = analyse_period(row, period, counts, float(data["frames"][p_index]), data["time"], tau)
            metrics.append(metric)
            profiles.extend(profile)
        source_hashes.append({"run": row["run"], "bytes": data["path"].stat().st_size, "sha256": sha256(data["path"])})

    aggregate = aggregate_metrics(metrics)
    aggregate_profile = aggregate_profiles(profiles)
    suffix = args.suffix.upper()
    RESULTS.mkdir(parents=True, exist_ok=True)
    write_csv(RESULTS / f"T414_{suffix}_RUN_PERIOD_METRICS.csv", metrics)
    write_csv(RESULTS / f"T414_{suffix}_RUN_PHASE_PROFILES.csv", profiles)
    write_csv(RESULTS / f"T414_{suffix}_AGGREGATE_PHASE_PROFILES.csv", aggregate_profile)
    write_csv(RESULTS / f"T414_{suffix}_TAU_CALIBRATION.csv", tau_curve)
    write_csv(RESULTS / f"T414_{suffix}_SOURCE_HASHES.csv", source_hashes)
    result = {
        "test": "T414 spin-child / lifespan-parent",
        "protocol_sha256": sha256(PROTOCOL),
        "requested_splits": sorted(requested),
        "run_count": len(selected),
        "run_period_count": len(metrics),
        "gamma_dev_MHz_per_G": GAMMA_DEV_MHZ_PER_G,
        "tau_dev_us": tau,
        "nyquist_MHz": NYQUIST_MHZ,
        "aggregate": aggregate,
    }
    with (RESULTS / f"T414_{suffix}_RESULTS.json").open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, allow_nan=False)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
