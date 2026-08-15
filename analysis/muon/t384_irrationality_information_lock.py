#!/usr/bin/env python3
"""T384: combine the T382 muon parent/child with Irrationality Di-ARA.

The calibration-only recorder follows the frozen T384 protocol.  It tests
whether ordered parent/child path information improves untouched child
navigation or recursive restoration.  It does not observe neutrinos.
"""

from __future__ import annotations

import html
import json
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

import t382_ral_silver_detector_share as detector
import t382_ral_silver_traversal_child as base


HERE = Path(__file__).resolve().parent
OUT = HERE / "T384_irrationality_information_lock"
OUT.mkdir(exist_ok=True)

PROTOCOL = HERE / "T384_IRRATIONALITY_INFORMATION_LOCK_PROTOCOL_2026-08-15.md"
RESULTS = OUT / "T384_RESULTS.json"
VALIDATION = OUT / "T384_VALIDATION.json"
RUN_METRICS = OUT / "T384_RUN_METRICS.csv"
CYCLE_METRICS = OUT / "T384_CYCLE_METRICS.csv"
NAVIGATOR_METRICS = OUT / "T384_NAVIGATOR_METRICS.csv"
EXAMPLE_PATH = OUT / "T384_EXAMPLE_PATH.csv"
TAIL_AUDIT = OUT / "T384_7P5_TAIL_AUDIT.csv"
FIGURE_PNG = OUT / "T384_INFORMATION_LOCK_FIGURE.png"
FIGURE_SVG = OUT / "T384_INFORMATION_LOCK_FIGURE.svg"
REPORT = OUT / "T384_INFORMATION_LOCK_REPORT.html"

M = 17
K = 9
FLAT = 0.01
SEED = 384
TAIL_MAX = 9.5

METHODS = (
    "open_loop_t382",
    "linear_persistence",
    "state_only",
    "direction_only",
    "wrong_relation",
    "full_irrationality",
)


def load_records() -> dict[str, dict]:
    split_lookup: dict[str, str] = {}
    for run in base.CALIBRATION:
        split_lookup[run] = "calibration"
    for run in base.VALIDATION:
        split_lookup[run] = "validation"
    for run in base.HOLDOUT:
        split_lookup[run] = "holdout"
    for run in base.DIAGNOSTIC:
        split_lookup[run] = "diagnostic"
    return {
        run: base.load_run(run, field, split_lookup[run])
        for run, field in base.ALL_RUNS.items()
    }


def fit_parent(calibration: list[dict]) -> float:
    tau0, _, _ = base.fit_parent(calibration, np.arange(1.5, 3.0001, 0.002))
    tau, _, _ = base.fit_parent(
        calibration,
        np.arange(max(0.5, tau0 - 0.02), tau0 + 0.02001, 0.0001),
    )
    return float(tau)


def detector_latent(record: dict, child: dict, end: float = TAIL_MAX) -> dict:
    """Project raw 96-detector shares into the frozen two-axis child plane."""
    time = np.asarray(record["time"], dtype=float)
    mask = (time >= base.T_MIN) & (time < end)
    analysis = record["analysis_mask"]
    counts = np.asarray(record["counts"], dtype=float)
    baseline_total = float(counts[:, analysis].sum())
    baseline = counts[:, analysis].sum(axis=1) / max(baseline_total, 1.0)
    selected = counts[:, mask]
    total = selected.sum(axis=0)
    shares = np.divide(
        selected,
        total[None, :],
        out=np.zeros_like(selected),
        where=total[None, :] > 0,
    )
    y = shares.T - baseline[None, :]
    beta = np.asarray(child["beta"], dtype=float)
    gram_inv = np.linalg.pinv(beta @ beta.T, rcond=1e-12)
    coefficient = y @ beta.T @ gram_inv
    z = coefficient[:, 0] + 1j * coefficient[:, 1]
    return {
        "time": time[mask],
        "z": z,
        "amplitude": np.abs(z),
        "counts": total,
        "baseline": baseline,
    }


def cycle_bounds(field: float, child: dict, start: float, end: float) -> list[tuple[int, float, float]]:
    rate = float(child["gamma_mhz_per_g"]) * field
    phi0 = float(child["phi0_rad"])
    lo = int(math.ceil((2.0 * math.pi * rate * start + phi0) / (2.0 * math.pi)))
    hi = int(math.floor((2.0 * math.pi * rate * end + phi0) / (2.0 * math.pi))) - 1
    rows = []
    for cycle in range(lo, hi + 1):
        t0 = (2.0 * math.pi * cycle - phi0) / (2.0 * math.pi * rate)
        t1 = (2.0 * math.pi * (cycle + 1) - phi0) / (2.0 * math.pi * rate)
        if t0 >= start - 1e-10 and t1 <= end + 1e-10:
            rows.append((cycle, float(t0), float(t1)))
    return rows


def extract_cycles(
    records: dict[str, dict],
    latent: dict[str, dict],
    child: dict,
    tau: float,
    amplitude_threshold: float,
    end: float = base.T_MAX,
) -> list[dict]:
    cycles: list[dict] = []
    phi0 = float(child["phi0_rad"])
    gamma = float(child["gamma_mhz_per_g"])
    for run, record in records.items():
        series = latent[run]
        source_time = series["time"]
        z = series["z"]
        amp = series["amplitude"]
        for cycle, t0, t1 in cycle_bounds(record["field_g"], child, base.T_MIN, end):
            native_bins = int(np.sum((source_time >= t0) & (source_time <= t1)))
            if native_bins < 8:
                continue
            grid = np.linspace(t0, t1, M)
            zr = np.interp(grid, source_time, z.real)
            zi = np.interp(grid, source_time, z.imag)
            za = zr + 1j * zi
            amplitude = np.abs(za)
            valid_fraction = float(np.mean(amplitude >= amplitude_threshold))
            if valid_fraction < 0.75:
                continue
            observed_phase = np.angle(za) + phi0
            x_child = 1.0 - np.cos(observed_phase)
            theta_model = 2.0 * np.pi * gamma * record["field_g"] * grid + phi0
            x_open = 1.0 - np.cos(theta_model)
            x_parent = 2.0 * (1.0 - np.exp(-grid / tau))
            cycles.append(
                {
                    "run": run,
                    "split": record["split"],
                    "field_g": float(record["field_g"]),
                    "cycle": int(cycle),
                    "t0": t0,
                    "t1": t1,
                    "native_bins": native_bins,
                    "valid_fraction": valid_fraction,
                    "median_amplitude": float(np.median(amplitude)),
                    "time": grid,
                    "x_parent": x_parent,
                    "x_child": x_child,
                    "x_open": x_open,
                    "amplitude": amplitude,
                }
            )
    return cycles


def direction(delta: float) -> int:
    if delta > FLAT:
        return 1
    if delta < -FLAT:
        return -1
    return 0


def quadrant(parent_out: float, child_in: float) -> str:
    return ("+" if parent_out >= 0 else "-") + ("+" if child_in >= 0 else "-")


def path_coordinates(xp_prev: float, xc_prev: float, xp: float, xc: float) -> tuple[float, float]:
    previous = complex(xp_prev - 1.0, xc_prev - 1.0)
    current = complex(xp - 1.0, xc - 1.0)
    if abs(previous) < 1e-8 or abs(current) < 1e-8:
        return 1.0, 1.0
    ratio = current / previous
    x_l = 2.0 * abs(ratio) / (1.0 + abs(ratio))
    x_t = 1.0 + float(np.angle(ratio)) / math.pi
    return float(x_l), float(x_t)


@dataclass
class RelationRecorder:
    scale_parent: float
    features: np.ndarray
    target: np.ndarray
    states: np.ndarray
    use_path: bool
    use_state: bool
    all_tree: cKDTree
    state_trees: dict[str, tuple[cKDTree, np.ndarray]]

    @classmethod
    def build(
        cls,
        cycles: list[dict],
        *,
        use_path: bool,
        use_state: bool,
        wrong_relation: bool = False,
    ) -> "RelationRecorder":
        raw_parent = np.concatenate([np.diff(c["x_parent"]) for c in cycles])
        nonzero = np.abs(raw_parent[np.abs(raw_parent) > 1e-12])
        scale = max(float(np.percentile(nonzero, 90.0)) if len(nonzero) else 1.0, 1e-6)
        features: list[list[float]] = []
        targets: list[float] = []
        states: list[str] = []
        for cycle in cycles:
            xp = cycle["x_parent"]
            xc = cycle["x_child"]
            for t in range(1, M - 1):
                parent_out = float(xp[t + 1] - xp[t])
                child_in = float(xc[t] - xc[t - 1])
                state = quadrant(parent_out, child_in)
                row = [float(xp[t] / 2.0), float(xc[t] / 2.0), parent_out / scale]
                if use_path:
                    x_l, x_t = path_coordinates(xp[t - 1], xc[t - 1], xp[t], xc[t])
                    row.extend([x_l / 2.0, x_t / 2.0])
                features.append(row)
                targets.append(float(xc[t + 1] - xc[t]))
                states.append(state)
        x = np.asarray(features, dtype=float)
        y = np.asarray(targets, dtype=float)
        q = np.asarray(states, dtype="U2")
        if wrong_relation:
            rng = np.random.default_rng(SEED)
            for state in np.unique(q):
                index = np.flatnonzero(q == state)
                y[index] = y[rng.permutation(index)]
        state_trees: dict[str, tuple[cKDTree, np.ndarray]] = {}
        if use_state:
            for state in np.unique(q):
                index = np.flatnonzero(q == state)
                if len(index):
                    state_trees[state] = (cKDTree(x[index]), index)
        return cls(scale, x, y, q, use_path, use_state, cKDTree(x), state_trees)

    def feature(
        self,
        xp_prev: float,
        xc_prev: float,
        xp: float,
        xc: float,
        parent_out: float,
    ) -> np.ndarray:
        row = [xp / 2.0, xc / 2.0, parent_out / self.scale_parent]
        if self.use_path:
            x_l, x_t = path_coordinates(xp_prev, xc_prev, xp, xc)
            row.extend([x_l / 2.0, x_t / 2.0])
        return np.asarray(row, dtype=float)

    def step(
        self,
        xp_prev: float,
        xc_prev: float,
        xp: float,
        xc: float,
        parent_out: float,
        child_in: float,
    ) -> tuple[float, bool]:
        point = self.feature(xp_prev, xc_prev, xp, xc, parent_out)
        state = quadrant(parent_out, child_in)
        fallback = False
        if self.use_state and state in self.state_trees:
            tree, source = self.state_trees[state]
            k = min(K, len(source))
            _, local = tree.query(point, k=k)
            index = source[np.atleast_1d(local)]
        else:
            fallback = self.use_state
            k = min(K, len(self.features))
            _, index = self.all_tree.query(point, k=k)
            index = np.atleast_1d(index)
        return float(np.median(self.target[index])), fallback


def inherited_directions(values: np.ndarray) -> np.ndarray:
    raw = np.diff(values)
    out = np.zeros(len(raw), dtype=int)
    out[raw > FLAT] = 1
    out[raw < -FLAT] = -1
    nonzero = np.flatnonzero(out)
    if not len(nonzero):
        return np.ones(len(raw), dtype=int)
    first = int(nonzero[0])
    out[:first] = out[first]
    for i in range(first + 1, len(out)):
        if out[i] == 0:
            out[i] = out[i - 1]
    return out


def waveform_r(actual: np.ndarray, predicted: np.ndarray) -> float:
    if np.std(actual) < 1e-9 or np.std(predicted) < 1e-9:
        return 0.0
    return float(np.corrcoef(actual, predicted)[0, 1])


def turning_error(actual: np.ndarray, predicted: np.ndarray) -> float:
    a_dir = inherited_directions(actual)
    p_dir = inherited_directions(predicted)
    a = np.flatnonzero(a_dir[1:] != a_dir[:-1]) + 1
    p = np.flatnonzero(p_dir[1:] != p_dir[:-1]) + 1
    if not len(a) and not len(p):
        return 0.0
    if not len(a) or not len(p):
        return 1.0
    distances = [float(np.min(np.abs(p - index))) for index in a]
    return float(np.median(distances) / (M - 1))


def path_metrics(xp: np.ndarray, actual: np.ndarray, predicted: np.ndarray) -> dict:
    actual_dir = inherited_directions(actual)
    pred_dir = inherited_directions(predicted)
    parent_dir = inherited_directions(xp)
    actual_q = np.asarray(
        [quadrant(parent_dir[min(i, len(parent_dir) - 1)], actual_dir[i]) for i in range(len(actual_dir))]
    )
    pred_q = np.asarray(
        [quadrant(parent_dir[min(i, len(parent_dir) - 1)], pred_dir[i]) for i in range(len(pred_dir))]
    )
    return {
        "rmse": float(np.sqrt(np.mean((actual - predicted) ** 2))),
        "mae": float(np.mean(np.abs(actual - predicted))),
        "waveform_r": waveform_r(actual, predicted),
        "direction_agreement": float(np.mean(actual_dir == pred_dir)),
        "quadrant_agreement": float(np.mean(actual_q == pred_q)),
        "turn_error": turning_error(actual, predicted),
        "endpoint_error": float(abs(actual[-1] - predicted[-1])),
    }


def recursive_prediction(cycle: dict, method: str, recorders: dict[str, RelationRecorder]) -> tuple[np.ndarray, int]:
    xp = cycle["x_parent"]
    actual = cycle["x_child"]
    if method == "open_loop_t382":
        return np.asarray(cycle["x_open"], dtype=float), 0
    predicted = np.empty_like(actual)
    predicted[:2] = actual[:2]
    if method == "linear_persistence":
        for t in range(1, M - 1):
            predicted[t + 1] = np.clip(predicted[t] + predicted[t] - predicted[t - 1], 0.0, 2.0)
        return predicted, 0
    recorder = recorders[method]
    fallback = 0
    for t in range(1, M - 1):
        parent_out = float(xp[t + 1] - xp[t])
        child_in = float(predicted[t] - predicted[t - 1])
        delta, used_fallback = recorder.step(
            float(xp[t - 1]),
            float(predicted[t - 1]),
            float(xp[t]),
            float(predicted[t]),
            parent_out,
            child_in,
        )
        predicted[t + 1] = np.clip(predicted[t] + delta, 0.0, 2.0)
        fallback += int(used_fallback)
    return predicted, fallback


def teacher_forced(cycle: dict, method: str, recorders: dict[str, RelationRecorder]) -> dict:
    xp = cycle["x_parent"]
    actual = cycle["x_child"]
    predicted = []
    target = []
    pred_delta = []
    actual_delta = []
    fallback = 0
    for t in range(1, M - 1):
        if method == "open_loop_t382":
            value = float(cycle["x_open"][t + 1])
        elif method == "linear_persistence":
            value = float(np.clip(actual[t] + actual[t] - actual[t - 1], 0.0, 2.0))
        else:
            parent_out = float(xp[t + 1] - xp[t])
            child_in = float(actual[t] - actual[t - 1])
            delta, used_fallback = recorders[method].step(
                float(xp[t - 1]),
                float(actual[t - 1]),
                float(xp[t]),
                float(actual[t]),
                parent_out,
                child_in,
            )
            value = float(np.clip(actual[t] + delta, 0.0, 2.0))
            fallback += int(used_fallback)
        predicted.append(value)
        target.append(float(actual[t + 1]))
        pred_delta.append(value - float(actual[t]))
        actual_delta.append(float(actual[t + 1] - actual[t]))
    predicted_array = np.asarray(predicted)
    target_array = np.asarray(target)
    pred_direction = inherited_directions(np.r_[actual[1], predicted_array])
    true_direction = inherited_directions(np.r_[actual[1], target_array])
    return {
        "rmse": float(np.sqrt(np.mean((target_array - predicted_array) ** 2))),
        "mae": float(np.mean(np.abs(target_array - predicted_array))),
        "direction_agreement": float(np.mean(pred_direction == true_direction)),
        "fallbacks": fallback,
    }


def aggregate_run_metrics(cycle_frame: pd.DataFrame, navigator_frame: pd.DataFrame) -> pd.DataFrame:
    recursive = (
        cycle_frame.groupby(["run", "split", "field_g", "method"], as_index=False)
        .median(numeric_only=True)
        .rename(columns={
            "rmse": "recursive_rmse",
            "mae": "recursive_mae",
            "waveform_r": "recursive_waveform_r",
            "direction_agreement": "recursive_direction_agreement",
            "quadrant_agreement": "recursive_quadrant_agreement",
            "turn_error": "recursive_turn_error",
            "endpoint_error": "recursive_endpoint_error",
        })
    )
    navigator = (
        navigator_frame.groupby(["run", "split", "field_g", "method"], as_index=False)
        .median(numeric_only=True)
        .rename(columns={
            "rmse": "navigator_rmse",
            "mae": "navigator_mae",
            "direction_agreement": "navigator_direction_agreement",
            "fallbacks": "navigator_fallbacks",
        })
    )
    return recursive.merge(navigator, on=["run", "split", "field_g", "method"], how="outer")


def gate_lookup(run_frame: pd.DataFrame, run: str, method: str) -> pd.Series | None:
    rows = run_frame[(run_frame.run == run) & (run_frame.method == method)]
    return None if rows.empty else rows.iloc[0]


def score_gates(run_frame: pd.DataFrame, readability: dict, threshold: float) -> dict:
    validation_runs = list(base.VALIDATION)
    holdout_runs = list(base.HOLDOUT)

    readable = all(readability[r] > threshold for r in list(base.CALIBRATION) + validation_runs)

    def navigation_pass(run: str) -> bool:
        full = gate_lookup(run_frame, run, "full_irrationality")
        state = gate_lookup(run_frame, run, "state_only")
        direction_row = gate_lookup(run_frame, run, "direction_only")
        if full is None or state is None or direction_row is None:
            return False
        return bool(
            full.navigator_rmse <= state.navigator_rmse - 0.05
            and full.navigator_rmse <= direction_row.navigator_rmse - 0.05
            and full.navigator_direction_agreement >= 0.75
        )

    def wrong_pass(run: str) -> bool:
        full = gate_lookup(run_frame, run, "full_irrationality")
        wrong = gate_lookup(run_frame, run, "wrong_relation")
        return bool(full is not None and wrong is not None and full.navigator_rmse <= wrong.navigator_rmse - 0.05)

    def restoration_pass(run: str) -> bool:
        full = gate_lookup(run_frame, run, "full_irrationality")
        return bool(full is not None and full.recursive_waveform_r >= 0.80 and full.recursive_rmse <= 0.30)

    def contribution_pass(run: str) -> bool:
        full = gate_lookup(run_frame, run, "full_irrationality")
        direction_row = gate_lookup(run_frame, run, "direction_only")
        if full is None or direction_row is None:
            return False
        return bool(
            full.recursive_rmse <= direction_row.recursive_rmse - 0.05
            or full.recursive_direction_agreement >= direction_row.recursive_direction_agreement + 0.05
        )

    nav_by_run = {r: navigation_pass(r) for r in validation_runs + holdout_runs}
    wrong_by_run = {r: wrong_pass(r) for r in validation_runs + holdout_runs}
    restore_by_run = {r: restoration_pass(r) for r in validation_runs + holdout_runs}
    contribution_by_run = {r: contribution_pass(r) for r in validation_runs + holdout_runs}
    local = all(nav_by_run[r] for r in validation_runs) and sum(nav_by_run[r] for r in holdout_runs) >= 2
    wrong = all(wrong_by_run[r] for r in validation_runs + holdout_runs)
    restore = all(restore_by_run[r] for r in validation_runs) and sum(restore_by_run[r] for r in holdout_runs) >= 2
    contribution = all(contribution_by_run[r] for r in validation_runs) and sum(contribution_by_run[r] for r in holdout_runs) >= 2
    return {
        "g1_observed_child_readability": readable,
        "g2_local_navigation": local,
        "g3_wrong_relation": wrong,
        "g4_recursive_restoration": restore,
        "g5_information_lock_contribution": contribution,
        "by_run": {
            "navigation": nav_by_run,
            "wrong_relation": wrong_by_run,
            "restoration": restore_by_run,
            "contribution": contribution_by_run,
        },
    }


def tail_audit(
    records: dict[str, dict],
    latent: dict[str, dict],
    child: dict,
    tau: float,
    full_recorder: RelationRecorder,
    amplitude_threshold: float,
) -> pd.DataFrame:
    t383 = json.loads(
        (HERE / "T383_7p5_child_before_parent_pole" / "T383_RESULTS.json").read_text(encoding="utf-8")
    )
    t_star = float(t383["discovery"]["t_star_us"])
    rows = []
    for run, field in base.HOLDOUT.items():
        record = records[run]
        _, fits = base.parent_fit_for_tau([record], tau)
        parent_fit = fits[run]
        signal = float(parent_fit["amplitude"] * math.exp(-t_star / tau))
        background = float(parent_fit["background"])
        snr = signal / math.sqrt(max(signal + background, 1e-12))
        model_theta = 2.0 * math.pi * child["gamma_mhz_per_g"] * field * t_star + child["phi0_rad"]
        open_value = 1.0 - math.cos(model_theta)
        cycle = int(math.floor(model_theta / (2.0 * math.pi)))
        rate = child["gamma_mhz_per_g"] * field
        t0 = (2.0 * math.pi * cycle - child["phi0_rad"]) / (2.0 * math.pi * rate)
        t1 = (2.0 * math.pi * (cycle + 1) - child["phi0_rad"]) / (2.0 * math.pi * rate)
        grid = np.linspace(t0, t1, M)
        series = latent[run]
        zr = np.interp(grid, series["time"], series["z"].real)
        zi = np.interp(grid, series["time"], series["z"].imag)
        amplitude = np.abs(zr + 1j * zi)
        x_observed = 1.0 - np.cos(np.angle(zr + 1j * zi) + child["phi0_rad"])
        x_parent = 2.0 * (1.0 - np.exp(-grid / tau))
        cycle_record = {
            "x_parent": x_parent,
            "x_child": x_observed,
            "x_open": 1.0 - np.cos(2.0 * np.pi * rate * grid + child["phi0_rad"]),
        }
        reconstructed, fallback = recursive_prediction(
            cycle_record,
            "full_irrationality",
            {"full_irrationality": full_recorder},
        )
        observed_value = float(np.interp(t_star, grid, x_observed))
        reconstructed_value = float(np.interp(t_star, grid, reconstructed))
        amplitude_ok = float(np.mean(amplitude >= amplitude_threshold)) >= 0.75
        admissible = bool(snr >= 3.0 and amplitude_ok and t0 >= base.T_MIN and t1 <= TAIL_MAX)
        rows.append(
            {
                "run": run,
                "field_g": field,
                "t_star_us": t_star,
                "parent_ara": 2.0 * (1.0 - math.exp(-t_star / tau)),
                "signal_counts_per_bin": signal,
                "background_counts_per_bin": background,
                "snr": snr,
                "amplitude_valid_fraction": float(np.mean(amplitude >= amplitude_threshold)),
                "admissible": admissible,
                "open_loop_child_ara": open_value,
                "observed_child_ara": observed_value if admissible else np.nan,
                "reconstructed_child_ara": reconstructed_value if admissible else np.nan,
                "distance_observed_to_pole_2": abs(2.0 - observed_value) if admissible else np.nan,
                "distance_reconstructed_to_pole_2": abs(2.0 - reconstructed_value) if admissible else np.nan,
                "fallbacks": fallback,
            }
        )
    return pd.DataFrame(rows)


def make_figure(
    run_frame: pd.DataFrame,
    example: pd.DataFrame,
    tail: pd.DataFrame,
    gates: dict,
) -> None:
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 12, "axes.labelsize": 10})
    fig, axes = plt.subplots(2, 2, figsize=(15, 10), constrained_layout=True)
    blue, gold, orange, ink, grey = "#3d79bd", "#d99a2b", "#d66b32", "#17202b", "#9aa5b1"

    ax = axes[0, 0]
    ax.plot(example.phase_fraction, example.x_parent, color=ink, lw=2.2, label="parent xP")
    ax.plot(example.phase_fraction, example.x_child_observed, color=blue, lw=2.0, label="observed child xC")
    ax.plot(example.phase_fraction, example.x_child_full, color=gold, lw=2.0, ls="--", label="full Di-ARA reconstruction")
    ax.plot(example.phase_fraction, example.x_child_open, color=grey, lw=1.5, ls=":", label="open-loop T382")
    ax.axhline(1.0, color="#65717e", lw=1, ls="--")
    ax.set(xlabel="within-child-cycle phase fraction", ylabel="ARA coordinate (0–2)", ylim=(-0.05, 2.05),
           title=f"Example holdout cycle: {example.run.iloc[0]} · {example.field_g.iloc[0]:.0f} G")
    ax.set_xticks(np.linspace(0, 1, 9))
    ax.set_yticks([0, 0.5, 1, 1.5, 2])
    ax.legend(fontsize=8, loc="best")
    ax.grid(alpha=0.2)

    ax = axes[0, 1]
    path = example.dropna(subset=["x_L", "x_T"])
    scatter = ax.scatter(path.x_L, path.x_T, c=path.phase_fraction, cmap="cividis", s=48, edgecolor=ink, linewidth=0.4)
    ax.plot(path.x_L, path.x_T, color=blue, alpha=0.55, lw=1.2)
    ax.axvline(1.0, color="#65717e", lw=1, ls="--")
    ax.axhline(1.0, color="#65717e", lw=1, ls="--")
    ax.set(xlim=(0, 2), ylim=(0, 2), xlabel="xL: contraction ← 1 → expansion",
           ylabel="xT: reverse ← 1 → forward", title="Observed Irrationality Di-ARA relation path")
    ax.set_xticks([0, 0.5, 1, 1.5, 2])
    ax.set_yticks([0, 0.5, 1, 1.5, 2])
    fig.colorbar(scatter, ax=ax, label="within-cycle phase fraction")
    ax.grid(alpha=0.2)

    ax = axes[1, 0]
    scored = run_frame[run_frame.split.isin(["validation", "holdout"])].copy()
    order = list(base.VALIDATION) + list(base.HOLDOUT)
    methods = ["open_loop_t382", "direction_only", "full_irrationality", "wrong_relation"]
    labels = ["open-loop", "direction-only", "full Irr. Di-ARA", "wrong relation"]
    colors = [grey, orange, blue, "#b55a71"]
    x = np.arange(len(order), dtype=float)
    width = 0.19
    for j, (method, label, color) in enumerate(zip(methods, labels, colors)):
        values = []
        for run in order:
            row = scored[(scored.run == run) & (scored.method == method)]
            values.append(float(row.recursive_rmse.iloc[0]) if len(row) else np.nan)
        ax.bar(x + (j - 1.5) * width, values, width=width, color=color, edgecolor=ink, linewidth=0.5, label=label)
    ax.axhline(0.30, color=ink, lw=1, ls="--", label="frozen restoration RMSE gate")
    ax.set_xticks(x, [f"{run[-3:]}\n{base.ALL_RUNS[run]:.0f}G" for run in order])
    ax.set(xlabel="validation then holdout run", ylabel="median recursive RMSE (ARA units)",
           title="Hidden-cycle restoration by method")
    ax.legend(fontsize=7, ncol=2)
    ax.grid(axis="y", alpha=0.2)

    ax = axes[1, 1]
    admissible = tail[tail.admissible].copy()
    if len(admissible):
        x = np.arange(len(admissible), dtype=float)
        ax.bar(x - 0.24, admissible.open_loop_child_ara, width=0.24, color=grey, edgecolor=ink, label="open-loop")
        ax.bar(x, admissible.observed_child_ara, width=0.24, color=blue, edgecolor=ink, label="observed")
        ax.bar(x + 0.24, admissible.reconstructed_child_ara, width=0.24, color=gold, edgecolor=ink, label="reconstructed")
        ax.set_xticks(x, [f"{r.field_g:.0f} G\nSNR {r.snr:.1f}" for r in admissible.itertuples()])
        ax.axhline(2.0, color=ink, lw=1, ls="--", label="child pole 2")
        ax.set_ylim(0, 2.1)
        ax.legend(fontsize=8)
    else:
        ax.text(0.5, 0.57, "7.5 tail unavailable", ha="center", va="center", fontsize=15, color=ink, transform=ax.transAxes)
        ax.text(0.5, 0.43, "No field passed both SNR ≥ 3 and child-amplitude coverage.", ha="center", va="center", fontsize=9, color="#596574", transform=ax.transAxes)
        ax.set_xticks([])
        ax.set_yticks([])
    ax.set(xlabel="field at T383 common parent coordinate", ylabel="child ARA coordinate (0–2)",
           title="Separately gated 7.5-cycle tail audit")
    ax.grid(axis="y", alpha=0.2)

    verdict = "SUPPORTED" if all(gates[k] for k in ["g1_observed_child_readability", "g2_local_navigation", "g3_wrong_relation", "g4_recursive_restoration", "g5_information_lock_contribution"]) else "NOT SUPPORTED"
    fig.suptitle(f"T384 — parent + child + Irrationality Di-ARA information lock · {verdict}", fontsize=17, color=ink)
    fig.savefig(FIGURE_PNG, dpi=180, facecolor="white")
    fig.savefig(FIGURE_SVG, facecolor="white")
    plt.close(fig)


def make_report(results: dict, run_frame: pd.DataFrame, tail: pd.DataFrame) -> None:
    methods = ["open_loop_t382", "direction_only", "full_irrationality", "wrong_relation"]
    table_rows = []
    for row in run_frame[run_frame.method.isin(methods)].itertuples():
        table_rows.append(
            f"<tr><td>{html.escape(row.run)}</td><td>{html.escape(row.split)}</td><td>{row.field_g:.0f}</td>"
            f"<td>{html.escape(row.method)}</td><td>{row.navigator_rmse:.4f}</td><td>{row.navigator_direction_agreement:.3f}</td>"
            f"<td>{row.recursive_rmse:.4f}</td><td>{row.recursive_waveform_r:.3f}</td><td>{row.recursive_direction_agreement:.3f}</td></tr>"
        )
    tail_rows = []
    for row in tail.itertuples():
        observed = "—" if not row.admissible else f"{row.observed_child_ara:.4f}"
        reconstructed = "—" if not row.admissible else f"{row.reconstructed_child_ara:.4f}"
        tail_rows.append(
            f"<tr><td>{row.field_g:.0f}</td><td>{row.t_star_us:.4f}</td><td>{row.snr:.3f}</td><td>{'yes' if row.admissible else 'no'}</td>"
            f"<td>{row.open_loop_child_ara:.4f}</td><td>{observed}</td><td>{reconstructed}</td></tr>"
        )
    gate_rows = "".join(
        f"<li><b>{html.escape(key)}</b>: {'PASS' if value else 'FAIL'}</li>"
        for key, value in results["gates"].items() if key != "by_run"
    )
    report = f"""<!doctype html><html><head><meta charset="utf-8"><title>T384 information lock</title>
<style>body{{font:16px/1.5 Arial;background:#f3f5f8;color:#17202b;margin:0}}main{{max-width:1380px;margin:auto;padding:34px}}.card{{background:white;border:1px solid #d8dee8;border-radius:12px;padding:22px;margin:18px 0}}table{{border-collapse:collapse;width:100%;font-size:13px}}th,td{{padding:7px;border-bottom:1px solid #e2e6ec;text-align:left}}img{{width:100%;height:auto}}code{{background:#eef1f5;padding:2px 5px}}.boundary{{border-left:6px solid #d58a20}}</style></head><body><main>
<h1>T384 — Irrationality Di-ARA information-lock test</h1>
<div class="card"><h2>Answer first</h2><p><b>{html.escape(results['status'])}</b></p><p>{html.escape(results['plain_language'])}</p><ul>{gate_rows}</ul></div>
<div class="card"><h2>Exact geometry tested</h2><p>Parent: <code>xP=2(1−exp(−t/τ))</code>. Observed child: the raw 96-detector pattern projected into the calibration-frozen two-axis child plane. Relation: adjacent parent/child complex ratios mapped to radial <code>xL</code> and turning <code>xT</code> ARA coordinates.</p><p>The third coordinate was never defined as <code>2−parent−child</code>. It had to improve future held-out reconstruction.</p></div>
<div class="card"><img src="{FIGURE_PNG.name}" alt="T384 information lock visual report"></div>
<div class="card"><h2>Run-level results</h2><table><tr><th>run</th><th>split</th><th>G</th><th>method</th><th>one-step RMSE</th><th>one-step direction</th><th>recursive RMSE</th><th>recursive r</th><th>recursive direction</th></tr>{''.join(table_rows)}</table></div>
<div class="card"><h2>7.5-cycle tail audit</h2><table><tr><th>G</th><th>time μs</th><th>SNR</th><th>admissible</th><th>open-loop xC</th><th>observed xC</th><th>reconstructed xC</th></tr>{''.join(tail_rows)}</table></div>
<div class="card boundary"><h2>Boundary</h2><p>{html.escape(results['claim_boundary'])}</p></div>
<div class="card"><h2>Reproduce</h2><p>Run <code>analysis/muon/t384_irrationality_information_lock.py</code>. Frozen protocol: <code>{PROTOCOL.name}</code>.</p></div>
</main></body></html>"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    records = load_records()
    calibration_records = [records[r] for r in base.CALIBRATION]
    tau = fit_parent(calibration_records)
    child = detector.fit_detector_child(calibration_records)

    latent = {run: detector_latent(record, child) for run, record in records.items()}
    calibration_amplitudes = np.concatenate([
        latent[r]["amplitude"][latent[r]["time"] < base.T_MAX] for r in base.CALIBRATION
    ])
    amplitude_threshold = float(np.quantile(calibration_amplitudes, 0.10))
    readability = {
        run: float(np.median(series["amplitude"][series["time"] < base.T_MAX]))
        for run, series in latent.items()
    }

    cycles = extract_cycles(records, latent, child, tau, amplitude_threshold)
    calibration_cycles = [c for c in cycles if c["split"] == "calibration"]
    if not calibration_cycles:
        raise RuntimeError("No admissible calibration cycles")
    recorders = {
        "state_only": RelationRecorder.build(calibration_cycles, use_path=False, use_state=False),
        "direction_only": RelationRecorder.build(calibration_cycles, use_path=False, use_state=True),
        "full_irrationality": RelationRecorder.build(calibration_cycles, use_path=True, use_state=True),
        "wrong_relation": RelationRecorder.build(calibration_cycles, use_path=True, use_state=True, wrong_relation=True),
    }

    cycle_rows: list[dict] = []
    navigator_rows: list[dict] = []
    prediction_lookup: dict[tuple[str, int, str], np.ndarray] = {}
    for cycle in cycles:
        for method in METHODS:
            predicted, fallback = recursive_prediction(cycle, method, recorders)
            prediction_lookup[(cycle["run"], cycle["cycle"], method)] = predicted
            metrics = path_metrics(cycle["x_parent"], cycle["x_child"], predicted)
            cycle_rows.append({
                "run": cycle["run"], "split": cycle["split"], "field_g": cycle["field_g"],
                "cycle": cycle["cycle"], "t0_us": cycle["t0"], "t1_us": cycle["t1"],
                "native_bins": cycle["native_bins"], "valid_fraction": cycle["valid_fraction"],
                "method": method, "fallbacks": fallback, **metrics,
            })
            nav = teacher_forced(cycle, method, recorders)
            navigator_rows.append({
                "run": cycle["run"], "split": cycle["split"], "field_g": cycle["field_g"],
                "cycle": cycle["cycle"], "method": method, **nav,
            })

    cycle_frame = pd.DataFrame(cycle_rows)
    navigator_frame = pd.DataFrame(navigator_rows)
    run_frame = aggregate_run_metrics(cycle_frame, navigator_frame)
    cycle_frame.to_csv(CYCLE_METRICS, index=False)
    navigator_frame.to_csv(NAVIGATOR_METRICS, index=False)
    run_frame.to_csv(RUN_METRICS, index=False)

    gates = score_gates(run_frame, readability, amplitude_threshold)

    example_candidates = [c for c in cycles if c["run"] == "EMU00066578"]
    if not example_candidates:
        example_candidates = [c for c in cycles if c["split"] == "holdout"]
    example_cycle = min(example_candidates, key=lambda c: abs(float(np.mean(c["x_parent"])) - 1.0))
    full_example = prediction_lookup[(example_cycle["run"], example_cycle["cycle"], "full_irrationality")]
    example_rows = []
    for i in range(M):
        if i == 0:
            x_l = x_t = np.nan
        else:
            x_l, x_t = path_coordinates(
                example_cycle["x_parent"][i - 1], example_cycle["x_child"][i - 1],
                example_cycle["x_parent"][i], example_cycle["x_child"][i],
            )
        example_rows.append({
            "run": example_cycle["run"], "field_g": example_cycle["field_g"],
            "cycle": example_cycle["cycle"], "phase_fraction": i / (M - 1),
            "time_us": example_cycle["time"][i], "x_parent": example_cycle["x_parent"][i],
            "x_child_observed": example_cycle["x_child"][i], "x_child_full": full_example[i],
            "x_child_open": example_cycle["x_open"][i], "x_L": x_l, "x_T": x_t,
        })
    example_frame = pd.DataFrame(example_rows)
    example_frame.to_csv(EXAMPLE_PATH, index=False)

    tail = tail_audit(records, latent, child, tau, recorders["full_irrationality"], amplitude_threshold)
    tail.to_csv(TAIL_AUDIT, index=False)

    all_primary = all(gates[k] for k in [
        "g1_observed_child_readability", "g2_local_navigation", "g3_wrong_relation",
        "g4_recursive_restoration", "g5_information_lock_contribution",
    ])
    navigator_only = bool(
        gates["g1_observed_child_readability"] and gates["g2_local_navigation"]
        and gates["g3_wrong_relation"] and not (gates["g4_recursive_restoration"] and gates["g5_information_lock_contribution"])
    )
    if all_primary:
        status = "IRRATIONALITY_INFORMATION_LOCK_SUPPORTED_ON_RAL_SILVER"
        plain = "The raw parent/child path added held-out information and supported both local navigation and recursive child restoration on the frozen source splits."
    elif navigator_only:
        status = "LOCAL_NAVIGATOR_ONLY_FULL_INFORMATION_LOCK_NOT_SUPPORTED"
        plain = "The Irrationality Di-ARA improved the next local child movement, but accumulated errors prevented the stronger hidden-cycle information lock."
    else:
        status = "IRRATIONALITY_INFORMATION_LOCK_NOT_SUPPORTED"
        plain = "Adding the raw Irrationality Di-ARA path did not satisfy the frozen held-out information-lock gates."

    results = {
        "test": "T384 Irrationality Di-ARA information lock on RAL Silver",
        "status": status,
        "plain_language": plain,
        "source": "same RAL Silver 96-detector archive as T382/T383",
        "medium_change": False,
        "parent": {"tau_us": tau, "coordinate": "xP=2(1-exp(-t/tau))"},
        "child": {
            "gamma_mhz_per_g": float(child["gamma_mhz_per_g"]),
            "phi0_rad": float(child["phi0_rad"]),
            "amplitude_threshold": amplitude_threshold,
            "coordinate": "xC=1-cos(arg(zC)+phi0)",
        },
        "relation": {
            "radial": "xL=2*abs(q)/(1+abs(q))",
            "turning": "xT=1+arg(q)/pi",
            "q": "((xP-1)+i(xC-1))_t / ((xP-1)+i(xC-1))_(t-1)",
            "samples_per_cycle": M,
            "nearest_relations": K,
        },
        "cycle_counts": pd.DataFrame(cycles).groupby("split").size().to_dict(),
        "readability_median_amplitude": readability,
        "gates": gates,
        "tail_admissible_fields": tail.loc[tail.admissible, "field_g"].astype(float).tolist(),
        "claim_boundary": "This source can test population-scale detector-pattern navigation. It contains no directly linked individual muon, charged daughter and neutrino record, so it cannot establish event-level neutrino timing.",
        "artifacts": {
            "protocol": str(PROTOCOL), "run_metrics": str(RUN_METRICS),
            "cycle_metrics": str(CYCLE_METRICS), "navigator_metrics": str(NAVIGATOR_METRICS),
            "example_path": str(EXAMPLE_PATH), "tail_audit": str(TAIL_AUDIT),
            "figure_png": str(FIGURE_PNG), "figure_svg": str(FIGURE_SVG), "report": str(REPORT),
        },
    }
    validation = {
        "protocol_exists": PROTOCOL.exists(),
        "source_hashes_checked_by_loader": all(all(r["quality"].values()) for r in records.values()),
        "calibration_only_fit": True,
        "no_medium_change": True,
        "no_forced_remainder_relation": True,
        "cycle_boundary_source": "frozen T382 gamma/field/phi0",
        "validation_and_holdout_refit": False,
        "tail_requires_snr_3": True,
    }
    RESULTS.write_text(json.dumps(results, indent=2), encoding="utf-8")
    VALIDATION.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    make_figure(run_frame, example_frame, tail, gates)
    make_report(results, run_frame, tail)
    print(json.dumps({
        "status": status,
        "gates": {k: v for k, v in gates.items() if k != "by_run"},
        "cycle_counts": results["cycle_counts"],
        "tail_admissible_fields": results["tail_admissible_fields"],
        "report": str(REPORT),
    }, indent=2))


if __name__ == "__main__":
    main()
