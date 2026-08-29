#!/usr/bin/env python3
"""T416 dual Irrationality Di-ARA tracking on the resolved ISIS muon archive."""

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
T414 = MUON / "T414_spin_child_lifespan_parent"
PROTOCOL = HERE / "T416_FROZEN_PROTOCOL.md"
RESULTS = HERE / "results"
FREEZE = HERE / "T416_DEVELOPMENT_FREEZE.json"

sys.path.insert(0, str(T414))
import t414_spin_child_lifespan_parent as t414  # noqa: E402


GAMMA_MHZ_PER_G = 0.013549
TAU_US = 2.203
CALIBRATION_END_US = 2.25
PATH_WINDOW = 128
PATH_STEP = 4
CONTROL_STEP = 16
RESOLUTIONS = np.asarray((8, 16, 32, 64), dtype=int)
MAX_LAG = 32
K_NEIGHBOURS = 5
WRONG_K = np.asarray((4, 8), dtype=float)
LENGTH_US = 5.75
BOOTSTRAPS = 10000
SEED = 416


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def circular_mean(values: np.ndarray) -> float:
    vector = np.mean(np.exp(2j * np.pi * values))
    return 0.0 if abs(vector) < 1e-15 else float((np.angle(vector) / (2 * np.pi)) % 1.0)


def circular_loss(actual: np.ndarray, predicted: np.ndarray) -> np.ndarray:
    return 1.0 - np.cos(2.0 * np.pi * (actual - predicted))


def knn_predict(train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray) -> np.ndarray:
    order = np.argsort(train_x)
    sx, sy = train_x[order], train_y[order]
    insertion = np.searchsorted(sx, test_x)
    radius = max(K_NEIGHBOURS + 2, 7)
    offsets = np.arange(-radius, radius + 1)
    candidates = (insertion[:, None] + offsets[None, :]) % len(sx)
    candidate_x = sx[candidates]
    distance = np.abs(candidate_x - test_x[:, None])
    distance = np.minimum(distance, 1.0 - distance)
    nearest_positions = np.argpartition(distance, K_NEIGHBOURS - 1, axis=1)[:, :K_NEIGHBOURS]
    nearest = np.take_along_axis(candidates, nearest_positions, axis=1)
    vectors = np.mean(np.exp(2j * np.pi * sy[nearest]), axis=1)
    predicted = (np.angle(vectors) / (2 * np.pi)) % 1.0
    predicted[np.abs(vectors) < 1e-12] = circular_mean(train_y)
    return predicted


def address_openness(z: np.ndarray) -> float:
    occupied = []
    for bins in RESOLUTIONS:
        index = np.minimum((z * bins).astype(int), bins - 1)
        occupied.append(int(np.unique(index).size))
    beta = float(np.polyfit(np.log(RESOLUTIONS), np.log(occupied), 1)[0])
    return 2.0 * float(np.clip(beta, 0.0, 1.0))


def stochastic_residual(z: np.ndarray) -> tuple[float, float, float]:
    split = len(z) // 2
    train_x, train_y = z[: split - 1], z[1:split]
    test_x, test_y = z[split:-1], z[split + 1 :]
    prediction = knn_predict(train_x, train_y, test_x)
    null_prediction = np.full_like(test_y, circular_mean(train_y))
    local = float(np.mean(circular_loss(test_y, prediction)))
    null = float(np.mean(circular_loss(test_y, null_prediction)))
    return 2.0 * min(1.0, local / max(null, 1e-12)), local, null


def closure_history(z: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    vector = np.exp(2j * np.pi * z)
    relations = np.asarray([
        np.mean(vector[lag:] * np.conj(vector[:-lag]))
        for lag in range(1, MAX_LAG + 1)
    ])
    return np.abs(relations), np.abs(np.angle(relations)) / np.pi


def path_metrics(z: np.ndarray) -> dict:
    x_r, local_loss, null_loss = stochastic_residual(z)
    rho, miss = closure_history(z)
    coherent = rho > 0.90
    if np.any(coherent):
        coherent_indices = np.flatnonzero(coherent)
        positive = coherent_indices[miss[coherent_indices] > 1e-12]
        chosen = int(positive[np.argmin(miss[positive])]) if len(positive) else int(coherent_indices[0])
        best_miss = float(miss[chosen])
        best_lag = chosen + 1
    else:
        best_miss = float("nan")
        best_lag = 0
    peak = int(np.argmax(rho))
    return {
        "x_P": address_openness(z),
        "x_R": x_r,
        "median_closure_rho": float(np.median(rho)),
        "peak_closure_rho": float(rho[peak]),
        "peak_closure_lag_bins": peak + 1,
        "best_coherent_miss": best_miss,
        "best_coherent_lag_bins": best_lag,
        "local_loss": local_loss,
        "null_loss": null_loss,
    }


def smooth_three(values: np.ndarray) -> np.ndarray:
    padded = np.pad(values, (1, 1), mode="edge")
    return np.median(np.vstack((padded[:-2], padded[1:-1], padded[2:])), axis=0)


def extract_spin_path(time: np.ndarray, counts: np.ndarray, frequency: float) -> dict:
    total = counts.sum(axis=0)
    valid = total > 0
    time = time[valid]
    counts = counts[:, valid]
    total = total[valid]
    share = 96.0 * counts / total[None, :]
    calibration = time < CALIBRATION_END_US
    centered = time - float(np.mean(time[calibration]))
    theta = 2.0 * np.pi * frequency * time
    design = np.column_stack((np.ones(len(time)), centered, np.cos(theta), np.sin(theta)))
    beta = np.linalg.lstsq(design[calibration], share[:, calibration].T, rcond=None)[0]
    baseline = design[:, :2] @ beta[:2]
    residual = share.T - baseline
    basis = beta[2:4].T
    condition = float(np.linalg.cond(basis.T @ basis))
    coordinate = residual @ np.linalg.pinv(basis.T)
    radius = smooth_three(np.linalg.norm(coordinate, axis=1))
    phase = (np.angle(coordinate[:, 0] + 1j * coordinate[:, 1]) / (2.0 * np.pi)) % 1.0
    fitted = design @ beta
    sse0 = float(np.sum((share[:, calibration].T - baseline[calibration]) ** 2))
    sse1 = float(np.sum((share[:, calibration].T - fitted[calibration]) ** 2))
    improvement = max(0.0, (sse0 - sse1) / max(sse0, 1e-30))
    return {
        "time": time,
        "total": total,
        "radius": radius,
        "phase": phase,
        "basis_condition": condition,
        "calibration_improvement": improvement,
    }


def state_coordinates(radius: np.ndarray, phase: np.ndarray, end: int, cycle_bins: int) -> tuple[float, float]:
    start = end - cycle_bins
    scale = float(radius[end] / max(radius[start], 1e-12))
    x_l = 2.0 * scale / (1.0 + scale)
    window = phase[start : end + 1]
    delta = np.angle(np.exp(2j * np.pi * np.diff(window)))
    denominator = float(np.sum(np.abs(np.sin(delta))))
    orientation = 0.0 if denominator < 1e-15 else float(np.sum(np.sin(delta)) / denominator)
    return x_l, 1.0 + orientation


def sector(x: float, y: float) -> str:
    if x == 1 or y == 1:
        return "ridge"
    if x < 1 and y > 1:
        return "Ba"
    if x > 1 and y > 1:
        return "Ab"
    if x < 1 and y < 1:
        return "bA"
    return "aB"


def analyse_run_period(row: dict, period: str) -> tuple[list[dict], dict]:
    data = t414.load_run(row)
    period_index = 0 if period == "RF on" else 1
    counts = data["counts"][period_index]
    time = data["time"]
    frequency = GAMMA_MHZ_PER_G * float(row["field_G"])
    correct = extract_spin_path(time, counts, frequency)
    dt = float(np.median(np.diff(correct["time"])))
    cycle_bins = max(4, int(round(1.0 / max(frequency * dt, 1e-12))))
    wrong_frequencies = []
    for k in WRONG_K:
        for sign in (-1.0, 1.0):
            candidate = frequency + sign * float(k) / LENGTH_US
            if candidate > 0.05:
                wrong_frequencies.append(candidate)
    wrong_paths = [extract_spin_path(time, counts, candidate) for candidate in wrong_frequencies]

    start = max(PATH_WINDOW - 1, cycle_bins)
    timeline: list[dict] = []
    control_samples: list[dict] = []
    run_number = int(str(row["run"])[-5:])
    period_seed = 0 if period == "RF on" else 100000
    for end in range(start, len(correct["time"]), PATH_STEP):
        x_l, x_c = state_coordinates(correct["radius"], correct["phase"], end, cycle_bins)
        history = correct["phase"][end - PATH_WINDOW + 1 : end + 1]
        measured = path_metrics(history)
        parent = 2.0 * (1.0 - math.exp(-float(correct["time"][end]) / TAU_US))
        timeline.append({
            "split": row["split"],
            "run": row["run"],
            "period": period,
            "field_G": float(row["field_G"]),
            "time_us": float(correct["time"][end]),
            "parent_ARA": parent,
            "state_x_L": x_l,
            "state_x_C": x_c,
            "state_sector": sector(x_l, x_c),
            "history_x_P": measured["x_P"],
            "history_x_R": measured["x_R"],
            "history_sector": sector(measured["x_P"], measured["x_R"]),
            "median_closure_rho": measured["median_closure_rho"],
            "peak_closure_rho": measured["peak_closure_rho"],
            "peak_closure_lag_bins": measured["peak_closure_lag_bins"],
            "best_coherent_miss": measured["best_coherent_miss"],
            "best_coherent_lag_bins": measured["best_coherent_lag_bins"],
            "spin_radius": float(correct["radius"][end]),
            "observed_phase_ARA": 2.0 * float(correct["phase"][end]),
            "cycle_bins": cycle_bins,
        })
        if (end - start) % CONTROL_STEP != 0:
            continue
        rng = np.random.default_rng(SEED + run_number + period_seed + end * 1009)
        shuffled = path_metrics(history[rng.permutation(PATH_WINDOW)])
        reversed_path = path_metrics(history[::-1])
        wrong_metrics = [
            path_metrics(path["phase"][end - PATH_WINDOW + 1 : end + 1])
            for path in wrong_paths
        ]
        control_samples.append({
            "target_x_P": measured["x_P"],
            "target_x_R": measured["x_R"],
            "target_rho": measured["median_closure_rho"],
            "shuffle_x_P": shuffled["x_P"],
            "shuffle_x_R": shuffled["x_R"],
            "shuffle_rho": shuffled["median_closure_rho"],
            "reverse_x_P": reversed_path["x_P"],
            "reverse_x_R": reversed_path["x_R"],
            "reverse_rho": reversed_path["median_closure_rho"],
            "wrong_x_P": float(np.median([item["x_P"] for item in wrong_metrics])),
            "wrong_x_R": float(np.median([item["x_R"] for item in wrong_metrics])),
            "wrong_rho": float(np.median([item["median_closure_rho"] for item in wrong_metrics])),
        })

    def med(key: str) -> float:
        return float(np.median([item[key] for item in control_samples]))

    summary = {
        "split": row["split"],
        "run": row["run"],
        "period": period,
        "field_G": float(row["field_G"]),
        "frequency_MHz": frequency,
        "cycle_bins": cycle_bins,
        "timeline_points": len(timeline),
        "control_windows": len(control_samples),
        "basis_condition": correct["basis_condition"],
        "calibration_improvement": correct["calibration_improvement"],
        "median_state_x_L": float(np.median([item["state_x_L"] for item in timeline])),
        "median_state_x_C": float(np.median([item["state_x_C"] for item in timeline])),
        "median_history_x_P": float(np.median([item["history_x_P"] for item in timeline])),
        "median_history_x_R": float(np.median([item["history_x_R"] for item in timeline])),
        "target_x_P": med("target_x_P"),
        "target_x_R": med("target_x_R"),
        "target_rho": med("target_rho"),
        "shuffle_x_P": med("shuffle_x_P"),
        "shuffle_x_R": med("shuffle_x_R"),
        "shuffle_rho": med("shuffle_rho"),
        "reverse_x_P": med("reverse_x_P"),
        "reverse_x_R": med("reverse_x_R"),
        "reverse_rho": med("reverse_rho"),
        "wrong_x_P": med("wrong_x_P"),
        "wrong_x_R": med("wrong_x_R"),
        "wrong_rho": med("wrong_rho"),
    }
    return timeline, summary


def rankdata(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    sorted_values = values[order]
    start = 0
    while start < len(values):
        stop = start + 1
        while stop < len(values) and sorted_values[stop] == sorted_values[start]:
            stop += 1
        ranks[order[start:stop]] = 0.5 * (start + stop - 1) + 1.0
        start = stop
    return ranks


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    ra, rb = rankdata(a), rankdata(b)
    return float(np.corrcoef(ra, rb)[0, 1])


def parent_adjusted_correlation(timeline: list[dict]) -> float:
    left, right = [], []
    keys = sorted({(item["run"], item["period"]) for item in timeline})
    for key in keys:
        part = [item for item in timeline if (item["run"], item["period"]) == key]
        parent = np.asarray([item["parent_ARA"] for item in part])
        design = np.column_stack((np.ones(len(parent)), parent, parent**2))
        x_l = np.asarray([item["state_x_L"] for item in part])
        x_r = np.asarray([item["history_x_R"] for item in part])
        left.extend(x_l - design @ np.linalg.lstsq(design, x_l, rcond=None)[0])
        right.extend(x_r - design @ np.linalg.lstsq(design, x_r, rcond=None)[0])
    return spearman(np.asarray(left), np.asarray(right))


def bootstrap_field_median(values: dict[float, float], seed: int) -> tuple[float, float, float]:
    fields = np.asarray(sorted(values), dtype=float)
    data = np.asarray([values[field] for field in fields], dtype=float)
    rng = np.random.default_rng(seed)
    samples = rng.choice(data, size=(BOOTSTRAPS, len(data)), replace=True)
    medians = np.median(samples, axis=1)
    return float(np.median(data)), float(np.quantile(medians, 0.025)), float(np.quantile(medians, 0.975))


def field_effects(summaries: list[dict], expression) -> dict[float, float]:
    output = {}
    for field in sorted({float(item["field_G"]) for item in summaries}):
        values = [float(expression(item)) for item in summaries if float(item["field_G"]) == field]
        output[field] = float(np.median(values))
    return output


def summarize(stage: str, timeline: list[dict], summaries: list[dict]) -> dict:
    shuffle_xr = bootstrap_field_median(field_effects(summaries, lambda r: r["shuffle_x_R"] - r["target_x_R"]), SEED + 1)
    support = bootstrap_field_median(field_effects(summaries, lambda r: abs(r["shuffle_x_P"] - r["target_x_P"])), SEED + 2)
    closure = bootstrap_field_median(field_effects(summaries, lambda r: r["target_rho"] - r["shuffle_rho"]), SEED + 3)
    wrong_xr = bootstrap_field_median(field_effects(summaries, lambda r: r["wrong_x_R"] - r["target_x_R"]), SEED + 4)
    state_xl = bootstrap_field_median(field_effects(summaries, lambda r: r["median_state_x_L"]), SEED + 5)
    rf_state = {
        period: {
            "median_x_L": float(np.median([r["median_state_x_L"] for r in summaries if r["period"] == period])),
            "median_x_C": float(np.median([r["median_state_x_C"] for r in summaries if r["period"] == period])),
            "median_x_P": float(np.median([r["median_history_x_P"] for r in summaries if r["period"] == period])),
            "median_x_R": float(np.median([r["median_history_x_R"] for r in summaries if r["period"] == period])),
        }
        for period in ("RF on", "RF off")
    }
    correlation = parent_adjusted_correlation(timeline)
    result = {
        "stage": stage,
        "run_count": len({item["run"] for item in summaries}),
        "run_period_count": len(summaries),
        "timeline_rows": len(timeline),
        "rf_state": rf_state,
        "paired_field_effects": {
            "shuffle_minus_target_x_R": {"median": shuffle_xr[0], "ci_low": shuffle_xr[1], "ci_high": shuffle_xr[2]},
            "abs_shuffle_minus_target_x_P": {"median": support[0], "ci_low": support[1], "ci_high": support[2]},
            "target_minus_shuffle_closure_rho": {"median": closure[0], "ci_low": closure[1], "ci_high": closure[2]},
            "wrong_minus_target_x_R": {"median": wrong_xr[0], "ci_low": wrong_xr[1], "ci_high": wrong_xr[2]},
            "state_x_L": {"median": state_xl[0], "ci_low": state_xl[1], "ci_high": state_xl[2]},
        },
        "parent_adjusted_spearman_state_x_L_history_x_R": correlation,
    }
    if stage == "validation":
        gates = {
            "G1_observed_state_orientation": all(value["median_x_C"] > 1.0 for value in rf_state.values()),
            "G2_observed_contraction": state_xl[0] < 1.0 and state_xl[2] < 1.0,
            "G3_chronology_determinacy": shuffle_xr[1] > 0.0,
            "G4_support_preservation": support[0] < 0.10,
            "G5_closure_history": closure[1] > 0.0,
            "G6_frequency_specificity": wrong_xr[1] > 0.0,
            "G7_nonredundancy_diagnostic": abs(correlation) < 0.80,
        }
        gates["dual_instrument_supported"] = all(gates.values())
        result["gates"] = gates
    return result


def run_stage(stage: str) -> None:
    rows = [row for row in t414.read_manifest() if row["split"] == stage]
    timeline: list[dict] = []
    summaries: list[dict] = []
    for index, row in enumerate(rows, start=1):
        print(f"{stage}: {index}/{len(rows)} {row['run']} {row['field_G']:.0f} G", flush=True)
        for period in ("RF on", "RF off"):
            time_rows, summary = analyse_run_period(row, period)
            timeline.extend(time_rows)
            summaries.append(summary)
    output = summarize(stage, timeline, summaries)
    output.update({
        "test": "T416 dual Irrationality Di-ARA muon time tracking",
        "boundary": "resolved population spin path; not individual muon or neutrino timing",
        "protocol_sha256": sha256(PROTOCOL),
        "analysis_sha256": sha256(Path(__file__).resolve()),
        "source_hashes": {row["run"]: sha256(t414.RAW / f"{row['run']}.nxs") for row in rows},
    })
    RESULTS.mkdir(parents=True, exist_ok=True)
    prefix = f"T416_{stage.upper()}"
    write_csv(RESULTS / f"{prefix}_TIMELINE.csv", timeline)
    write_csv(RESULTS / f"{prefix}_RUN_PERIOD_SUMMARY.csv", summaries)
    (RESULTS / f"{prefix}_RESULTS.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    if stage == "development":
        freeze = {
            "test": output["test"],
            "frozen_after_development_before_validation": True,
            "protocol_sha256": output["protocol_sha256"],
            "analysis_sha256": output["analysis_sha256"],
            "constants": {
                "gamma_MHz_per_G": GAMMA_MHZ_PER_G,
                "tau_us": TAU_US,
                "calibration_end_us": CALIBRATION_END_US,
                "path_window_bins": PATH_WINDOW,
                "path_step_bins": PATH_STEP,
                "control_step_bins": CONTROL_STEP,
                "resolutions": RESOLUTIONS.tolist(),
                "max_lag": MAX_LAG,
                "k_neighbours": K_NEIGHBOURS,
                "wrong_k": WRONG_K.tolist(),
            },
            "development_result": output,
        }
        FREEZE.write_text(json.dumps(freeze, indent=2), encoding="utf-8")
    else:
        if not FREEZE.exists():
            raise FileNotFoundError("development freeze missing")
        frozen = json.loads(FREEZE.read_text(encoding="utf-8"))
        for key in ("protocol_sha256", "analysis_sha256"):
            if frozen[key] != output[key]:
                raise RuntimeError(f"validation refused: frozen {key} mismatch")
    print(json.dumps(output, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("development", "validation"), required=True)
    args = parser.parse_args()
    run_stage(args.stage)


if __name__ == "__main__":
    main()
