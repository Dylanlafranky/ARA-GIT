#!/usr/bin/env python3
"""T397: frozen spin-phase maturity-versus-orientation test.

Run with the bundled Python 3.12 runtime. NumPy is intentionally imported
before the legacy HDF4 reader path is added by the T382 source loader.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

import t382_ral_silver_traversal_child as base


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "T397_SPIN_PHASE_MATURITY_VS_ORIENTATION_PROTOCOL_2026-08-17.md"
OUT = HERE / "T397_spin_phase_maturity_vs_orientation"
OUT.mkdir(exist_ok=True)

RESULTS = OUT / "T397_RESULTS.json"
RUN_SCORES = OUT / "T397_RUN_SCORES.csv"
CONTROLS = OUT / "T397_WRONG_CADENCE_CONTROLS.csv"
PHASE_PROFILES = OUT / "T397_PHASE_PROFILES.csv"
BOOTSTRAP = OUT / "T397_BOOTSTRAP.csv"
SOURCE_MANIFEST = OUT / "T397_SOURCE_MANIFEST.csv"

TAU_US = 2.1928
GAMMA_MHZ_PER_G = 0.01382
T_MIN = 0.25
T_MAX = 8.0
N_PHASE_BINS = 48
N_BOOT = 10000
SEED = 397
WRONG_MULTIPLIERS = np.r_[np.arange(0.5, 1.0, 0.1), np.arange(1.1, 1.51, 0.1)]


def protocol_hash() -> str:
    return hashlib.sha256(PROTOCOL.read_bytes()).hexdigest().upper()


def load_sources() -> tuple[list[dict], list[dict], list[dict]]:
    calibration = [base.load_run(run, field, "calibration") for run, field in base.CALIBRATION.items()]
    validation = [base.load_run(run, field, "validation") for run, field in base.VALIDATION.items()]
    holdout = [base.load_run(run, field, "holdout") for run, field in base.HOLDOUT.items()]
    return calibration, validation, holdout


def calibration_acceptance(calibration: list[dict]) -> tuple[float, np.ndarray, np.ndarray]:
    detector_totals = np.zeros(96, dtype=float)
    forward = 0.0
    backward = 0.0
    for record in calibration:
        mask = record["analysis_mask"]
        detector_totals += record["counts"][:, mask].sum(axis=1)
        forward += float(record["forward"][mask].sum())
        backward += float(record["backward"][mask].sum())
    shares = detector_totals / detector_totals.sum()
    weights = np.median(shares) / shares
    alpha = forward / backward
    return float(alpha), weights, shares


def channel_series(record: dict, channel: str, alpha: float, detector_weights: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    counts = np.asarray(record["counts"], dtype=float)
    if channel == "U":
        series = counts.sum(axis=0)
    elif channel == "V":
        series = counts[:48].sum(axis=0) + alpha * counts[48:].sum(axis=0)
    elif channel == "W":
        series = np.sum(detector_weights[:, None] * counts, axis=0)
    else:
        raise ValueError(channel)
    background = float(np.mean(series[record["background_mask"]]))
    mask = (record["time"] >= T_MIN) & (record["time"] < T_MAX)
    return record["time"][mask], series[mask], background


def cycle_partition(time: np.ndarray, field_g: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    turns = GAMMA_MHZ_PER_G * field_g * time
    cycles = np.floor(turns).astype(int)
    odd = cycles % 2 == 1
    even = ~odd
    return turns, cycles, odd, even


def fit_amplitude_subset(observed: np.ndarray, time: np.ndarray, background: float, mask: np.ndarray) -> float:
    shape = np.exp(-time[mask] / TAU_US)
    return float(base.fit_amplitude(observed[mask], shape, background))


def scalar_fit_score(record: dict, channel: str, alpha: float, detector_weights: np.ndarray,
                     cadence_multiplier: float = 1.0, train_parity: str = "odd") -> dict:
    time, observed, background = channel_series(record, channel, alpha, detector_weights)
    turns, cycles, odd, even = cycle_partition(time, float(record["field_g"]))
    train = odd if train_parity == "odd" else even
    test = even if train_parity == "odd" else odd
    amplitude = fit_amplitude_subset(observed, time, background, train)
    parent = amplitude * np.exp(-time / TAU_US) + background
    phase = 2.0 * np.pi * GAMMA_MHZ_PER_G * float(record["field_g"]) * cadence_multiplier * time
    design = parent[:, None] * np.column_stack([np.cos(phase), np.sin(phase)])
    root_weight = 1.0 / np.sqrt(np.maximum(parent[train], 1.0))
    beta = np.linalg.lstsq(design[train] * root_weight[:, None],
                           (observed[train] - parent[train]) * root_weight, rcond=None)[0]
    phase_prediction = np.maximum(parent + design @ beta, 1e-9)
    null_error = (observed[test] - parent[test]) ** 2 / np.maximum(parent[test], 1.0)
    phase_error = (observed[test] - phase_prediction[test]) ** 2 / np.maximum(parent[test], 1.0)
    null_sse = float(null_error.sum())
    phase_sse = float(phase_error.sum())
    amplitude_fraction = float(np.hypot(beta[0], beta[1]))
    phase_angle = float(np.mod(np.arctan2(beta[1], beta[0]), 2.0 * np.pi))
    null_nll = float(base.poisson_nll(observed[test], parent[test])) if channel == "U" else None
    phase_nll = float(base.poisson_nll(observed[test], phase_prediction[test])) if channel == "U" else None
    return {
        "run": record["run"],
        "field_g": float(record["field_g"]),
        "channel": channel,
        "train_parity": train_parity,
        "cadence_multiplier": float(cadence_multiplier),
        "n_train_bins": int(train.sum()),
        "n_test_bins": int(test.sum()),
        "n_train_cycles": int(np.unique(cycles[train]).size),
        "n_test_cycles": int(np.unique(cycles[test]).size),
        "amplitude": float(amplitude),
        "background": float(background),
        "beta_cos": float(beta[0]),
        "beta_sin": float(beta[1]),
        "phase_amplitude_fraction": amplitude_fraction,
        "phase_angle_rad": phase_angle,
        "null_sse": null_sse,
        "phase_sse": phase_sse,
        "gain": float(1.0 - phase_sse / max(null_sse, 1e-30)),
        "poisson_nll_gain_per_test_bin": None if channel != "U" else float((null_nll - phase_nll) / max(int(test.sum()), 1)),
        "time": time,
        "observed": observed,
        "parent_prediction": parent,
        "phase_prediction": phase_prediction,
        "test_mask": test,
        "test_cycles": cycles[test],
        "null_error": null_error,
        "phase_error": phase_error,
        "turn_fraction": np.mod(turns, 1.0),
    }


def orientation_fit_score(record: dict, cadence_multiplier: float = 1.0,
                          train_parity: str = "odd") -> dict:
    mask = (record["time"] >= T_MIN) & (record["time"] < T_MAX)
    time = np.asarray(record["time"][mask], dtype=float)
    counts = np.asarray(record["counts"][:, mask], dtype=float)
    total = counts.sum(axis=0)
    shares = np.divide(counts, total[None, :], out=np.zeros_like(counts), where=total[None, :] > 0)
    baseline = counts.sum(axis=1) / max(float(total.sum()), 1.0)
    y = shares.T - baseline[None, :]
    turns, cycles, odd, even = cycle_partition(time, float(record["field_g"]))
    train = odd if train_parity == "odd" else even
    test = even if train_parity == "odd" else odd
    phase = 2.0 * np.pi * GAMMA_MHZ_PER_G * float(record["field_g"]) * cadence_multiplier * time
    design = np.column_stack([np.cos(phase), np.sin(phase)])
    design -= np.average(design[train], axis=0, weights=total[train])[None, :]
    xtwx = design[train].T @ (total[train, None] * design[train])
    xtwy = design[train].T @ (total[train, None] * y[train])
    beta = np.linalg.solve(xtwx + np.eye(2) * 1e-18, xtwy)
    prediction = design @ beta
    null_parts = total[test] * np.sum(y[test] ** 2, axis=1)
    phase_parts = total[test] * np.sum((y[test] - prediction[test]) ** 2, axis=1)
    null_sse = float(null_parts.sum())
    phase_sse = float(phase_parts.sum())
    return {
        "run": record["run"],
        "field_g": float(record["field_g"]),
        "channel": "O",
        "train_parity": train_parity,
        "cadence_multiplier": float(cadence_multiplier),
        "n_train_bins": int(train.sum()),
        "n_test_bins": int(test.sum()),
        "n_train_cycles": int(np.unique(cycles[train]).size),
        "n_test_cycles": int(np.unique(cycles[test]).size),
        "phase_amplitude_fraction": float(np.sqrt(np.sum(beta * beta))),
        "phase_angle_rad": None,
        "null_sse": null_sse,
        "phase_sse": phase_sse,
        "gain": float(1.0 - phase_sse / max(null_sse, 1e-30)),
        "test_cycles": cycles[test],
        "null_error": null_parts,
        "phase_error": phase_parts,
    }


def stripped(score: dict) -> dict:
    omit = {"time", "observed", "parent_prediction", "phase_prediction", "test_mask",
            "test_cycles", "null_error", "phase_error", "turn_fraction"}
    return {key: value for key, value in score.items() if key not in omit}


def pooled_gain(scores: list[dict]) -> float:
    null = sum(float(score["null_sse"]) for score in scores)
    phase = sum(float(score["phase_sse"]) for score in scores)
    return float(1.0 - phase / max(null, 1e-30))


def hierarchical_bootstrap(scores_by_channel: dict[str, list[dict]]) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    fields = [str(score["run"]) for score in scores_by_channel["W"]]
    lookup = {channel: {str(score["run"]): score for score in scores}
              for channel, scores in scores_by_channel.items()}
    rows = []
    for replicate in range(N_BOOT):
        selected_fields = rng.choice(fields, size=len(fields), replace=True)
        sums = {channel: [0.0, 0.0] for channel in scores_by_channel}
        for run in selected_fields:
            for channel, run_lookup in lookup.items():
                score = run_lookup[str(run)]
                cycles = np.asarray(score["test_cycles"], dtype=int)
                unique = np.unique(cycles)
                chosen = rng.choice(unique, size=len(unique), replace=True)
                for cycle in chosen:
                    idx = cycles == cycle
                    sums[channel][0] += float(np.asarray(score["null_error"])[idx].sum())
                    sums[channel][1] += float(np.asarray(score["phase_error"])[idx].sum())
        row = {"replicate": replicate}
        for channel, (null, phase) in sums.items():
            row[f"gain_{channel}"] = 1.0 - phase / max(null, 1e-30)
        rows.append(row)
    return pd.DataFrame(rows)


def circular_resultant(angles: list[float]) -> tuple[float, float]:
    values = np.exp(1j * np.asarray(angles, dtype=float))
    mean = values.mean()
    return float(np.mod(np.angle(mean), 2.0 * np.pi)), float(abs(mean))


def phase_profile_rows(score: dict, channel: str) -> list[dict]:
    phase = np.asarray(score["turn_fraction"])[score["test_mask"]]
    observed = np.asarray(score["observed"])[score["test_mask"]]
    parent = np.asarray(score["parent_prediction"])[score["test_mask"]]
    fitted = np.asarray(score["phase_prediction"])[score["test_mask"]]
    residual = observed / np.maximum(parent, 1.0) - 1.0
    predicted_residual = fitted / np.maximum(parent, 1.0) - 1.0
    index = np.minimum((phase * N_PHASE_BINS).astype(int), N_PHASE_BINS - 1)
    rows = []
    for j in range(N_PHASE_BINS):
        selected = index == j
        if not np.any(selected):
            continue
        weights = np.maximum(parent[selected], 1.0)
        rows.append({
            "run": score["run"],
            "field_g": score["field_g"],
            "channel": channel,
            "phase_turn": (j + 0.5) / N_PHASE_BINS,
            "n_bins": int(selected.sum()),
            "observed_fractional_residual": float(np.average(residual[selected], weights=weights)),
            "predicted_fractional_residual": float(np.average(predicted_residual[selected], weights=weights)),
        })
    return rows


def main() -> None:
    calibration, validation, holdout = load_sources()
    all_records = calibration + validation + holdout
    if not all(all(record["quality"].values()) for record in all_records):
        raise RuntimeError("A frozen source quality gate failed")

    alpha, detector_weights, calibration_shares = calibration_acceptance(calibration)

    primary: dict[str, list[dict]] = {channel: [] for channel in ["O", "U", "V", "W"]}
    reverse: dict[str, list[dict]] = {channel: [] for channel in ["O", "U", "V", "W"]}
    for record in holdout:
        primary["O"].append(orientation_fit_score(record, 1.0, "odd"))
        reverse["O"].append(orientation_fit_score(record, 1.0, "even"))
        for channel in ["U", "V", "W"]:
            primary[channel].append(scalar_fit_score(record, channel, alpha, detector_weights, 1.0, "odd"))
            reverse[channel].append(scalar_fit_score(record, channel, alpha, detector_weights, 1.0, "even"))

    control_rows: list[dict] = []
    control_sets: dict[str, dict[str, list[dict]]] = {}
    for multiplier in WRONG_MULTIPLIERS:
        key = f"multiplier_{multiplier:.2f}"
        control_sets[key] = {channel: [] for channel in ["O", "W"]}
        for record in holdout:
            control_sets[key]["O"].append(orientation_fit_score(record, float(multiplier), "odd"))
            control_sets[key]["W"].append(scalar_fit_score(record, "W", alpha, detector_weights, float(multiplier), "odd"))

    runs = [record["run"] for record in holdout]
    fields = [float(record["field_g"]) for record in holdout]
    by_run = {record["run"]: record for record in holdout}
    for permutation in itertools.permutations(fields):
        if list(permutation) == fields:
            continue
        key = "field_permutation_" + "_".join(str(int(v)) for v in permutation)
        control_sets[key] = {channel: [] for channel in ["O", "W"]}
        for run, timing_field in zip(runs, permutation):
            record = by_run[run]
            multiplier = float(timing_field / record["field_g"])
            control_sets[key]["O"].append(orientation_fit_score(record, multiplier, "odd"))
            control_sets[key]["W"].append(scalar_fit_score(record, "W", alpha, detector_weights, multiplier, "odd"))

    for name, channels in control_sets.items():
        for channel, scores in channels.items():
            for score in scores:
                control_rows.append({"control": name, "channel": channel, **stripped(score)})
            control_rows.append({
                "control": name,
                "channel": channel,
                "run": "POOLED",
                "field_g": np.nan,
                "gain": pooled_gain(scores),
                "cadence_multiplier": np.nan,
                "train_parity": "odd",
            })
    control_frame = pd.DataFrame(control_rows)

    boot_frame = hierarchical_bootstrap(primary)
    boot_ci = {
        channel: [float(boot_frame[f"gain_{channel}"].quantile(0.025)),
                  float(boot_frame[f"gain_{channel}"].quantile(0.975))]
        for channel in primary
    }

    run_rows = []
    for family, collection in [("primary", primary), ("reverse_parity", reverse)]:
        for channel, scores in collection.items():
            run_rows.extend({"score_family": family, **stripped(score)} for score in scores)
            run_rows.append({
                "score_family": family,
                "run": "POOLED",
                "field_g": np.nan,
                "channel": channel,
                "train_parity": "odd" if family == "primary" else "even",
                "cadence_multiplier": 1.0,
                "gain": pooled_gain(scores),
            })
    run_frame = pd.DataFrame(run_rows)

    profile_rows = []
    for score in primary["W"]:
        profile_rows.extend(phase_profile_rows(score, "W"))
    profile_frame = pd.DataFrame(profile_rows)

    w_angles = [float(score["phase_angle_rad"]) for score in primary["W"]]
    w_mean_angle, w_resultant = circular_resultant(w_angles)
    wrong_w = control_frame[(control_frame.channel == "W") & (control_frame.run == "POOLED")].gain.to_numpy(dtype=float)
    wrong_o = control_frame[(control_frame.channel == "O") & (control_frame.run == "POOLED")].gain.to_numpy(dtype=float)
    primary_gains = {channel: pooled_gain(scores) for channel, scores in primary.items()}
    reverse_gains = {channel: pooled_gain(scores) for channel, scores in reverse.items()}
    u_amp = float(np.mean([score["phase_amplitude_fraction"] for score in primary["U"]]))
    w_amp = float(np.mean([score["phase_amplitude_fraction"] for score in primary["W"]]))

    orientation_gates = {
        "positive_each_field": all(score["gain"] > 0 for score in primary["O"]),
        "bootstrap_lower_above_zero": boot_ci["O"][0] > 0,
        "beats_every_wrong_cadence": primary_gains["O"] > float(np.max(wrong_o)),
    }
    orientation_pass = all(orientation_gates.values())
    maturity_gates = {
        "orientation_recovered": orientation_pass,
        "w_positive_each_field": all(score["gain"] > 0 for score in primary["W"]),
        "w_bootstrap_lower_above_zero": boot_ci["W"][0] > 0,
        "w_beats_wrong_cadence_97_5": primary_gains["W"] > float(np.quantile(wrong_w, 0.975)),
        "w_phase_resultant_at_least_0_70": w_resultant >= 0.70,
        "w_survives_acceptance_ladder": (w_amp >= 0.5 * u_amp) or (primary_gains["W"] > primary_gains["U"]),
        "reverse_w_nonnegative_each_field": all(score["gain"] >= 0 for score in reverse["W"]),
    }
    maturity_pass = all(maturity_gates.values())
    if maturity_pass:
        status = "POPULATION_SPIN_MATURITY_SUPPORTED_REPLICATION_REQUIRED"
    elif orientation_pass:
        status = "ORIENTATION_SUPPORTED_MATURITY_NOT_SUPPORTED"
    else:
        status = "INCONCLUSIVE_ORIENTATION_POSITIVE_CONTROL_FAILED"

    source_rows = []
    for record in all_records:
        source_rows.append({
            "run": record["run"], "split": record["split"], "field_g": record["field_g"],
            "temperature_k": record["temperature_k"], "orientation": record["orientation"],
            "native_bins": len(record["time"]), "detectors": record["counts"].shape[0],
            "sha256": record["sha256"], "all_quality_gates_pass": all(record["quality"].values()),
        })
    source_frame = pd.DataFrame(source_rows)

    results = {
        "test": "T397 spin phase maturity versus orientation",
        "status": status,
        "protocol_sha256": protocol_hash(),
        "source": {
            "doi": "10.5286/ISIS.E.RB1620201",
            "instrument": "ISIS EMU",
            "medium": "300 K RAL Silver",
            "grain": "aggregate 96-detector population histograms",
            "previously_inspected_source": True,
        },
        "frozen": {
            "tau_us": TAU_US,
            "gamma_mhz_per_g": GAMMA_MHZ_PER_G,
            "analysis_window_us": [T_MIN, T_MAX],
            "phase_bins_for_display": N_PHASE_BINS,
            "primary_train_cycles": "odd",
            "primary_test_cycles": "even",
            "wrong_multipliers": [float(value) for value in WRONG_MULTIPLIERS],
        },
        "acceptance": {
            "forward_backward_alpha": alpha,
            "detector_weight_min": float(detector_weights.min()),
            "detector_weight_median": float(np.median(detector_weights)),
            "detector_weight_max": float(detector_weights.max()),
            "calibration_share_min": float(calibration_shares.min()),
            "calibration_share_max": float(calibration_shares.max()),
        },
        "primary_pooled_gain": primary_gains,
        "reverse_parity_pooled_gain": reverse_gains,
        "bootstrap_95_gain": boot_ci,
        "w_common_mode": {
            "mean_phase_amplitude_fraction": w_amp,
            "raw_u_mean_phase_amplitude_fraction": u_amp,
            "mean_phase_angle_rad": w_mean_angle,
            "phase_resultant_length": w_resultant,
            "wrong_cadence_97_5_gain": float(np.quantile(wrong_w, 0.975)),
            "wrong_cadence_max_gain": float(np.max(wrong_w)),
        },
        "orientation": {
            "wrong_cadence_max_gain": float(np.max(wrong_o)),
        },
        "gates": {
            "orientation_components": orientation_gates,
            "orientation_pass": orientation_pass,
            "maturity_components": maturity_gates,
            "maturity_pass": maturity_pass,
        },
        "per_field": {
            channel: [stripped(score) for score in scores] for channel, scores in primary.items()
        },
        "plain_language": (
            "The spin phase predicts the changing detector-direction pattern and also survives the strict "
            "acceptance-balanced parent common mode, supporting a population maturity modulation that needs replication."
            if maturity_pass else
            "The spin phase predicts the detector-direction pattern, but the stricter balanced parent common mode does not pass the frozen maturity gates. "
            "In this source the recovered spin wave acts as an orientation organiser, not a measurable population release clock."
            if orientation_pass else
            "The within-run orientation positive control did not pass all frozen gates, so this source cannot decide maturity versus orientation under T397."
        ),
        "claim_boundary": (
            "Population-level phase-dependent release only. No individual muon, neutrino, deterministic lifetime or causal spin trigger is observed."
        ),
        "artifacts": {
            "run_scores": str(RUN_SCORES),
            "controls": str(CONTROLS),
            "phase_profiles": str(PHASE_PROFILES),
            "bootstrap": str(BOOTSTRAP),
            "source_manifest": str(SOURCE_MANIFEST),
        },
    }

    run_frame.to_csv(RUN_SCORES, index=False)
    control_frame.to_csv(CONTROLS, index=False)
    profile_frame.to_csv(PHASE_PROFILES, index=False)
    boot_frame.to_csv(BOOTSTRAP, index=False)
    source_frame.to_csv(SOURCE_MANIFEST, index=False)
    RESULTS.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": status,
        "primary_pooled_gain": primary_gains,
        "bootstrap_95_gain": boot_ci,
        "w_phase_resultant": w_resultant,
        "w_wrong_97_5": float(np.quantile(wrong_w, 0.975)),
    }, indent=2))


if __name__ == "__main__":
    main()
