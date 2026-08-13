"""T345: frozen post-T344 line/circle and two-information-ledger diagnostic."""

from __future__ import annotations

import json
import math
import os
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, TwoSlopeNorm
import numpy as np
import pandas as pd
from scipy.optimize import minimize


REPRESENTATION = os.environ.get("T345_REPRESENTATION", "lab").strip().lower()
if REPRESENTATION not in {"lab", "num"}:
    raise ValueError("T345_REPRESENTATION must be 'lab' or 'num'")
os.environ["T344_REPRESENTATION"] = REPRESENTATION

import t344_baw_weir_irrationality_di_ara as base  # noqa: E402


HERE = Path(__file__).resolve().parent
PREFIX = "T345_LINE_CIRCLE_TWO_LEDGER" + ("" if REPRESENTATION == "lab" else "_NUMERICAL_REPLICATION")
PROTOCOL = HERE / "T345_LINE_CIRCLE_TWO_LEDGER_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = "65770ca22b4be2cdca94eecbb976f31d139b9df30847bec509b26920f52a7a23"
PRIMARY_W = 15
SENSITIVITY_WINDOWS = (8, 30)
BOOTSTRAPS = 2000
RNG_SEED = 34520260807
PATH_NAMES = {0: "mixed", 1: "circle-like", 2: "crooked/random-like"}
CLASS_NAMES = base.CLASS_NAMES


class ChunkedSoftmaxL2:
    """Algebraically identical to T344 SoftmaxL2 with bounded temporaries.

    The numerical representation contains more than eight million primary
    windows.  T344's vectorised implementation materialises several complete
    probability/residual matrices during every optimiser evaluation.  This
    implementation accumulates the same mean loss and gradient in chunks; it
    changes memory scheduling, not the model, features, rows or regulariser.
    """

    def __init__(self, c: float = 1.0, chunk_size: int = 250_000):
        self.c = c
        self.chunk_size = chunk_size

    def _chunks(self, indices: np.ndarray):
        for start in range(0, len(indices), self.chunk_size):
            yield indices[start : start + self.chunk_size]

    def fit_indexed(self, x: np.ndarray, y: np.ndarray, indices: np.ndarray) -> "ChunkedSoftmaxL2":
        n, d = len(indices), x.shape[1]
        sums = np.zeros(d, dtype=np.float64)
        sums_sq = np.zeros(d, dtype=np.float64)
        for idx in self._chunks(indices):
            block = x[idx]
            sums += block.sum(axis=0)
            sums_sq += np.square(block).sum(axis=0)
        self.mean_ = sums / n
        variance = np.maximum(sums_sq / n - np.square(self.mean_), 0.0)
        self.std_ = np.sqrt(variance)
        self.std_[self.std_ == 0] = 1.0
        k_minus_one = 3

        def objective(flat: np.ndarray):
            beta = flat.reshape(d + 1, k_minus_one)
            loss_sum = 0.0
            grad = np.zeros_like(beta)
            for idx in self._chunks(indices):
                xs = (x[idx] - self.mean_) / self.std_
                logits = xs @ beta[:-1] + beta[-1]
                row_max = np.maximum(logits.max(axis=1), 0.0)
                probability = np.exp(logits - row_max[:, None])
                fourth = np.exp(-row_max)
                denominator = probability.sum(axis=1) + fourth
                probability /= denominator[:, None]
                labels = y[idx]
                rows = np.arange(len(idx))
                target_probability = np.where(
                    labels < k_minus_one,
                    probability[rows, np.minimum(labels, k_minus_one - 1)],
                    fourth / denominator,
                )
                loss_sum -= np.log(np.clip(target_probability, 1e-15, 1.0)).sum()
                active = labels < k_minus_one
                probability[rows[active], labels[active]] -= 1.0
                grad[:-1] += xs.T @ probability
                grad[-1] += probability.sum(axis=0)
            loss = loss_sum / n + 0.5 * np.square(beta[:-1]).sum() / (self.c * n)
            grad /= n
            grad[:-1] += beta[:-1] / (self.c * n)
            return float(loss), grad.ravel()

        initial = np.zeros((d + 1) * k_minus_one, dtype=np.float64)
        result = minimize(
            objective,
            initial,
            method="L-BFGS-B",
            jac=True,
            options={"maxiter": 1000, "ftol": 1e-12, "gtol": 1e-9},
        )
        self.beta_ = result.x.reshape(d + 1, k_minus_one)
        self.optimisation_ = {
            "success": bool(result.success),
            "status": int(result.status),
            "message": str(result.message),
            "iterations": int(result.nit),
            "objective": float(result.fun),
            "gradient_max_abs": float(np.max(np.abs(result.jac))),
        }
        return self

    def target_probability_indexed(
        self, x: np.ndarray, y: np.ndarray, indices: np.ndarray
    ) -> np.ndarray:
        values = np.empty(len(indices), dtype=np.float64)
        k_minus_one = 3
        for start in range(0, len(indices), self.chunk_size):
            idx = indices[start : start + self.chunk_size]
            xs = (x[idx] - self.mean_) / self.std_
            logits = xs @ self.beta_[:-1] + self.beta_[-1]
            row_max = np.maximum(logits.max(axis=1), 0.0)
            probability = np.exp(logits - row_max[:, None])
            fourth = np.exp(-row_max)
            denominator = probability.sum(axis=1) + fourth
            probability /= denominator[:, None]
            labels = y[idx]
            rows = np.arange(len(idx))
            block = np.where(
                labels < k_minus_one,
                probability[rows, np.minimum(labels, k_minus_one - 1)],
                fourth / denominator,
            )
            values[start : start + len(idx)] = block
        return values


def score_window_information_memory_safe(windows: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    """T344 held-out information score with chunked numerical allocation."""

    windows = windows.copy()
    columns = ["ara_x", "ara_y", "interaction", "dominance"]
    features = np.empty((len(windows), len(columns)), dtype=np.float64)
    for column_index, column in enumerate(columns):
        features[:, column_index] = windows[column].to_numpy(dtype=np.float64)
    features[:, :2] -= 1.0
    target = windows["target_sector"].to_numpy(dtype=np.int64)
    speed = windows["speed_px_s"].to_numpy(dtype=np.float64)
    condition_code = windows["condition"].map({name: i for i, name in enumerate(base.CONDITIONS)}).to_numpy(dtype=np.int8)
    information_all = np.full(len(windows), np.nan, dtype=np.float64)
    speed_quintile_all = np.full(len(windows), -1, dtype=np.int8)
    optimiser = []
    for test_code, test_condition in enumerate(base.CONDITIONS):
        train_index = np.flatnonzero(condition_code != test_code)
        test_index = np.flatnonzero(condition_code == test_code)
        model = ChunkedSoftmaxL2().fit_indexed(features, target, train_index)
        probability = model.target_probability_indexed(features, target, test_index)
        counts = np.ones(4) + np.bincount(target[train_index], minlength=4)
        baseline = counts / counts.sum()
        information_all[test_index] = np.log(np.clip(probability, 1e-15, 1.0)) - np.log(baseline[target[test_index]])
        edges = np.quantile(speed[train_index], [0.2, 0.4, 0.6, 0.8])
        speed_quintile_all[test_index] = np.searchsorted(edges, speed[test_index], side="right")
        optimiser.append(
            {
                "test_condition": test_condition,
                "model": f"window_{int(windows['window'].iloc[0])}_intact",
                **model.optimisation_,
            }
        )
    windows["information_nats"] = information_all
    windows["speed_quintile"] = speed_quintile_all
    return windows, optimiser


def rolling_sum(values: np.ndarray, width: int) -> np.ndarray:
    if width <= 0 or len(values) < width:
        return np.empty(0, dtype=np.float64)
    cs = np.concatenate(([0.0], np.cumsum(values, dtype=np.float64)))
    return cs[width:] - cs[:-width]


def wrapped_distances(values: np.ndarray, candidates: np.ndarray) -> np.ndarray:
    raw = np.abs(values[:, None] - candidates[None, :])
    return np.minimum(raw, 1.0 - raw).min(axis=1)


def connection_information(sectors: np.ndarray, window: int, m: int) -> np.ndarray:
    left, right = sectors[:-1], sectors[1:]
    valid = (left >= 0) & (right >= 0)
    edge = np.where(valid, left * 4 + right, -1)
    counts = np.zeros((m, 16), dtype=np.float64)
    for code in range(16):
        counts[:, code] = rolling_sum((edge == code).astype(np.float64), window - 1)[:m]
    n = counts.sum(axis=1)
    p = np.divide(counts, n[:, None], out=np.zeros_like(counts), where=n[:, None] > 0)
    entropy = -np.sum(np.where(p > 0, p * np.log(np.clip(p, 1e-300, None)), 0.0), axis=1)
    occupied = (counts > 0).sum(axis=1)
    correction = np.divide(occupied - 1, 2.0 * n, out=np.zeros_like(n), where=n > 0)
    hmm = np.minimum(math.log(16.0), entropy + correction)
    info = math.log(16.0) - hmm
    info[n == 0] = np.nan
    return info


def classify_closure(delta: np.ndarray, window: int, m: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    real = rolling_sum(np.cos(delta), window)[:m] / window
    imag = rolling_sum(np.sin(delta), window)[:m] / window
    coherence = np.hypot(real, imag)
    rho = (np.arctan2(imag, real) / (2.0 * np.pi)) % 1.0
    distance = wrapped_distances(rho, base.RATIONALS_8)
    threshold = 1.0 / (2.0 * window)
    closure = np.full(m, 3, dtype=np.int8)
    closure[(coherence >= 0.75) & (distance <= threshold)] = 0
    closure[(coherence >= 0.75) & (distance > threshold)] = 1
    closure[coherence <= 0.25] = 2
    return closure, coherence, distance


def normalise_example(points: np.ndarray) -> np.ndarray:
    points = points.astype(np.float64) - points[0]
    steps = np.linalg.norm(np.diff(points, axis=0), axis=1)
    length = float(steps.sum())
    if length > 0:
        points /= length
    first = points[1] if len(points) > 1 else np.array([1.0, 0.0])
    angle = math.atan2(float(first[1]), float(first[0]))
    rotation = np.array([[math.cos(-angle), -math.sin(-angle)], [math.sin(-angle), math.cos(-angle)]])
    return points @ rotation.T


def build_windows(events: list[dict], window: int, collect_examples: bool = False) -> tuple[pd.DataFrame, dict]:
    frames = []
    best = {
        "straight closure": (-np.inf, None),
        "circle-like": (-np.inf, None),
        "crooked/random-like": (-np.inf, None),
    }
    for event in events:
        tmin, tmax = float(event["time"].min()), float(event["time"].max())
        span = max(tmax - tmin, 1e-12)
        for run_number, run in enumerate(base.contiguous_runs(event["frame"])):
            length = len(run)
            m = length - window
            if m <= 0:
                continue
            pos = np.column_stack([event["x_pos"][run], event["z_pos"][run]])
            steps = np.diff(pos, axis=0)
            step_length = np.linalg.norm(steps, axis=1)
            path_length = rolling_sum(step_length, window)[:m]
            chord = np.linalg.norm(pos[window:] - pos[:-window], axis=1)[:m]
            directness = np.divide(chord, path_length, out=np.full(m, np.nan), where=path_length > 0)

            if len(steps) >= 2:
                cross = steps[:-1, 0] * steps[1:, 1] - steps[:-1, 1] * steps[1:, 0]
                dot = np.sum(steps[:-1] * steps[1:], axis=1)
                turns = np.arctan2(cross, dot)
                net_turn = rolling_sum(turns, window - 1)[:m]
                total_turn = rolling_sum(np.abs(turns), window - 1)[:m]
                turn_consistency = np.divide(
                    np.abs(net_turn), total_turn, out=np.zeros(m, dtype=np.float64), where=total_turn > 1e-15
                )
            else:
                net_turn = np.zeros(m)
                total_turn = np.zeros(m)
                turn_consistency = np.zeros(m)
            circularity = (1.0 - directness) * turn_consistency

            delta = event["delta"][run]
            closure, coherence, rational_distance = classify_closure(delta, window, m)
            sectors = event["sector"][run]
            target = sectors[window : window + m]
            current = sectors[:m]
            conn = connection_information(sectors, window, m)

            path_class = np.zeros(m, dtype=np.int8)
            path_class[(directness <= 0.75) & (turn_consistency >= 0.75)] = 1
            path_class[(directness <= 0.75) & (turn_consistency <= 0.25)] = 2

            delta_conn = np.full(m, np.nan)
            if m > window:
                delta_conn[:-window] = conn[window:] - conn[:-window]

            start = np.arange(m, dtype=np.int32)
            source_index = run[:m]
            xc = event["ara_x"][source_index] - 1.0
            yc = event["ara_y"][source_index] - 1.0
            progress = (event["time"][source_index] - tmin) / span
            valid = (current >= 0) & (target >= 0) & np.isfinite(directness) & np.isfinite(conn)
            if not valid.any():
                continue
            frame = pd.DataFrame(
                {
                    "condition": event["condition"],
                    "particle_id": event["particle_id"],
                    "track_id": event["track_id"],
                    "run_id": f"{event['track_id']}:{run_number}",
                    "offset": start,
                    "window": window,
                    "frame": event["frame"][source_index],
                    "time_s": event["time"][source_index],
                    "ara_x": event["ara_x"][source_index],
                    "ara_y": event["ara_y"][source_index],
                    "interaction": xc * yc,
                    "dominance": np.abs(xc) - np.abs(yc),
                    "sector": current,
                    "target_sector": target,
                    "closure_class": closure,
                    "coherence": coherence,
                    "rational_distance_q8": rational_distance,
                    "directness": directness,
                    "turn_consistency": turn_consistency,
                    "net_turn_rad": net_turn,
                    "total_turn_rad": total_turn,
                    "circularity": circularity,
                    "connection_info_nats": conn,
                    "delta_connection_info_nats": delta_conn,
                    "path_class": path_class,
                    "path_length": path_length,
                    "progress": progress,
                    "progress_decile": np.minimum((progress * 10).astype(int), 9),
                    "speed_px_s": event["speed"][source_index],
                }
            )
            frames.append(frame.loc[valid])

            if collect_examples:
                candidates = {
                    "straight closure": np.where(valid & (closure == 0))[0],
                    "circle-like": np.where(valid & (path_class == 1))[0],
                    "crooked/random-like": np.where(valid & (path_class == 2))[0],
                }
                scores = {
                    "straight closure": directness,
                    "circle-like": circularity,
                    "crooked/random-like": (1.0 - directness) * (1.0 - turn_consistency),
                }
                for name, indices in candidates.items():
                    if not len(indices):
                        continue
                    local = int(indices[np.nanargmax(scores[name][indices])])
                    score = float(scores[name][local])
                    if score > best[name][0]:
                        points = normalise_example(pos[local : local + window + 1])
                        best[name] = (
                            score,
                            {
                                "path_type": name,
                                "condition": event["condition"],
                                "track_id": event["track_id"],
                                "frame": int(event["frame"][run[local]]),
                                "score": score,
                                "points": points,
                            },
                        )
    if not frames:
        return pd.DataFrame(), {}
    return pd.concat(frames, ignore_index=True), {name: item for name, (_, item) in best.items() if item is not None}


def generic_point_difference(frame: pd.DataFrame, group_col: str, a: int, b: int, metric: str) -> tuple[float, int]:
    # The frozen handover rule leaves end-of-track windows unavailable by
    # construction.  Exclude those missing outcomes before aggregation so a
    # zero bootstrap weight cannot propagate ``0 * NaN`` through a replicate.
    selected = frame[frame[group_col].isin([a, b])].dropna(subset=[metric])
    aggregate = (
        selected.groupby(["condition", "progress_decile", "speed_quintile", group_col, "track_id"], observed=True)[metric]
        .mean()
        .reset_index()
    )
    differences = []
    for _, group in aggregate.groupby(["condition", "progress_decile", "speed_quintile"], observed=True):
        va = group.loc[group[group_col] == a, metric]
        vb = group.loc[group[group_col] == b, metric]
        if len(va) and len(vb):
            differences.append(float(va.mean() - vb.mean()))
    return (float(np.mean(differences)) if differences else np.nan, len(differences))


def cluster_bootstrap_contrast(frame: pd.DataFrame, group_col: str, a: int, b: int, metric: str) -> dict:
    selected = frame[frame[group_col].isin([a, b])].dropna(subset=[metric])
    aggregate = (
        selected.groupby(["condition", "progress_decile", "speed_quintile", group_col, "track_id"], observed=True)[metric]
        .mean()
        .reset_index()
    )
    track_ids = sorted(aggregate["track_id"].unique())
    track_index = {track: i for i, track in enumerate(track_ids)}
    condition_tracks = {
        c: [track_index[t] for t in aggregate.loc[aggregate["condition"] == c, "track_id"].unique()]
        for c in base.CONDITIONS
    }
    groups = {}
    for key, group in aggregate.groupby(["condition", "progress_decile", "speed_quintile", group_col], observed=True):
        groups[key] = (
            np.array([track_index[t] for t in group["track_id"]], dtype=np.int32),
            group[metric].to_numpy(dtype=np.float64),
        )
    strata = sorted(set(key[:3] for key in groups))

    def calculate(weights: np.ndarray) -> tuple[float, int]:
        values = []
        for stratum in strata:
            ka, kb = (*stratum, a), (*stratum, b)
            if ka not in groups or kb not in groups:
                continue
            ia, va = groups[ka]
            ib, vb = groups[kb]
            wa, wb = weights[ia], weights[ib]
            if wa.sum() and wb.sum():
                values.append(float(np.dot(wa, va) / wa.sum() - np.dot(wb, vb) / wb.sum()))
        return (float(np.mean(values)) if values else np.nan, len(values))

    estimate, n_strata = calculate(np.ones(len(track_ids), dtype=np.int32))
    rng = np.random.default_rng(RNG_SEED)
    samples = []
    for _ in range(BOOTSTRAPS):
        weights = np.zeros(len(track_ids), dtype=np.int32)
        for indices in condition_tracks.values():
            if indices:
                draw = rng.choice(indices, size=len(indices), replace=True)
                weights += np.bincount(draw, minlength=len(track_ids)).astype(np.int32)
        value, _ = calculate(weights)
        if np.isfinite(value):
            samples.append(value)
    return {
        "estimate": estimate,
        "ci_low": float(np.quantile(samples, 0.025)) if samples else np.nan,
        "ci_high": float(np.quantile(samples, 0.975)) if samples else np.nan,
        "n_tracks": len(track_ids),
        "n_strata": n_strata,
        "bootstrap_valid": len(samples),
    }


def cluster_bootstrap_one(frame: pd.DataFrame, group_col: str, group_value: int, metric: str) -> dict:
    selected = frame[frame[group_col] == group_value].dropna(subset=[metric])
    aggregate = (
        selected.groupby(["condition", "progress_decile", "speed_quintile", "track_id"], observed=True)[metric]
        .mean()
        .reset_index()
    )
    track_ids = sorted(aggregate["track_id"].unique())
    track_index = {track: i for i, track in enumerate(track_ids)}
    condition_tracks = {
        c: [track_index[t] for t in aggregate.loc[aggregate["condition"] == c, "track_id"].unique()]
        for c in base.CONDITIONS
    }
    groups = {}
    for key, group in aggregate.groupby(["condition", "progress_decile", "speed_quintile"], observed=True):
        groups[key] = (
            np.array([track_index[t] for t in group["track_id"]], dtype=np.int32),
            group[metric].to_numpy(dtype=np.float64),
        )

    def calculate(weights: np.ndarray) -> float:
        values = []
        for idx, vals in groups.values():
            w = weights[idx]
            if w.sum():
                values.append(float(np.dot(w, vals) / w.sum()))
        return float(np.mean(values)) if values else np.nan

    estimate = calculate(np.ones(len(track_ids), dtype=np.int32))
    rng = np.random.default_rng(RNG_SEED + 1)
    samples = []
    for _ in range(BOOTSTRAPS):
        weights = np.zeros(len(track_ids), dtype=np.int32)
        for indices in condition_tracks.values():
            if indices:
                draw = rng.choice(indices, size=len(indices), replace=True)
                weights += np.bincount(draw, minlength=len(track_ids)).astype(np.int32)
        value = calculate(weights)
        if np.isfinite(value):
            samples.append(value)
    return {
        "estimate": estimate,
        "ci_low": float(np.quantile(samples, 0.025)) if samples else np.nan,
        "ci_high": float(np.quantile(samples, 0.975)) if samples else np.nan,
        "n_tracks": len(track_ids),
        "n_strata": len(groups),
        "bootstrap_valid": len(samples),
    }


def eligibility(frame: pd.DataFrame, group_col: str, groups: tuple[int, ...], metric: str) -> tuple[bool, dict]:
    detail = {}
    ok = True
    for condition in base.CONDITIONS:
        for group_value in groups:
            part = frame[(frame["condition"] == condition) & (frame[group_col] == group_value) & frame[metric].notna()]
            key = f"{condition}:{group_value}"
            detail[key] = {"windows": int(len(part)), "tracks": int(part["track_id"].nunique())}
            ok &= len(part) >= 100 and part["track_id"].nunique() >= 20
    return bool(ok), detail


def component(frame: pd.DataFrame, name: str, group_col: str, a: int, b: int, metric: str) -> dict:
    eligible, detail = eligibility(frame, group_col, (a, b), metric)
    condition_effects = {}
    for condition in base.CONDITIONS:
        value, strata = generic_point_difference(frame[frame["condition"] == condition], group_col, a, b, metric)
        condition_effects[condition] = {"estimate": value, "strata": strata}
    pooled = cluster_bootstrap_contrast(frame, group_col, a, b, metric)
    directions = sum(v["estimate"] > 0 for v in condition_effects.values() if np.isfinite(v["estimate"]))
    passed = bool(eligible and directions >= 2 and pooled["ci_low"] > 0)
    return {
        "name": name,
        "group_col": group_col,
        "a": a,
        "b": b,
        "metric": metric,
        "eligible": eligible,
        "eligibility": detail,
        "condition_effects": condition_effects,
        "pooled": pooled,
        "direction_wins": directions,
        "pass": passed,
    }


def one_group_component(frame: pd.DataFrame, name: str, group_col: str, group_value: int, metric: str) -> dict:
    eligible, detail = eligibility(frame, group_col, (group_value,), metric)
    condition_effects = {}
    for condition in base.CONDITIONS:
        part = frame[(frame["condition"] == condition) & (frame[group_col] == group_value)]
        track_means = part.groupby(["progress_decile", "speed_quintile", "track_id"], observed=True)[metric].mean().reset_index()
        stratum_means = track_means.groupby(["progress_decile", "speed_quintile"], observed=True)[metric].mean()
        condition_effects[condition] = {
            "estimate": float(stratum_means.mean()) if len(stratum_means) else np.nan,
            "strata": int(len(stratum_means)),
        }
    pooled = cluster_bootstrap_one(frame, group_col, group_value, metric)
    directions = sum(v["estimate"] > 0 for v in condition_effects.values() if np.isfinite(v["estimate"]))
    passed = bool(eligible and directions >= 2 and pooled["ci_low"] > 0)
    return {
        "name": name,
        "group_col": group_col,
        "group_value": group_value,
        "metric": metric,
        "eligible": eligible,
        "eligibility": detail,
        "condition_effects": condition_effects,
        "pooled": pooled,
        "direction_wins": directions,
        "pass": passed,
    }


def summaries(primary: pd.DataFrame, sensitivity: list[pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    all_windows = pd.concat([primary, *sensitivity], ignore_index=True, sort=False)
    closure = (
        all_windows.assign(class_name=all_windows["closure_class"].map(CLASS_NAMES))
        .groupby(["window", "condition", "closure_class", "class_name"], observed=True)
        .agg(
            windows=("track_id", "size"),
            tracks=("track_id", "nunique"),
            directness=("directness", "mean"),
            turn_consistency=("turn_consistency", "mean"),
            circularity=("circularity", "mean"),
            connection_info_nats=("connection_info_nats", "mean"),
            movement_info_nats=("information_nats", "mean"),
        )
        .reset_index()
    )
    path = (
        primary[primary["path_class"].isin([1, 2])]
        .assign(path_name=lambda x: x["path_class"].map(PATH_NAMES))
        .groupby(["condition", "path_class", "path_name"], observed=True)
        .agg(
            windows=("track_id", "size"),
            tracks=("track_id", "nunique"),
            directness=("directness", "mean"),
            turn_consistency=("turn_consistency", "mean"),
            circularity=("circularity", "mean"),
            connection_info_nats=("connection_info_nats", "mean"),
            movement_info_nats=("information_nats", "mean"),
            delta_connection_info_nats=("delta_connection_info_nats", "mean"),
        )
        .reset_index()
    )
    edges = np.linspace(0.0, 1.0, 21)
    surface_frame = primary.copy()
    surface_frame["d_bin"] = np.clip(np.digitize(surface_frame["directness"], edges) - 1, 0, 19)
    surface_frame["g_bin"] = np.clip(np.digitize(surface_frame["turn_consistency"], edges) - 1, 0, 19)
    surface = (
        surface_frame.groupby(["d_bin", "g_bin"], observed=True)
        .agg(
            windows=("track_id", "size"),
            tracks=("track_id", "nunique"),
            directness=("directness", "mean"),
            turn_consistency=("turn_consistency", "mean"),
            circularity=("circularity", "mean"),
            connection_info_nats=("connection_info_nats", "mean"),
            movement_info_nats=("information_nats", "mean"),
        )
        .reset_index()
    )
    return closure, path, surface


def surface_matrix(surface: pd.DataFrame, column: str, fill=np.nan) -> np.ndarray:
    matrix = np.full((20, 20), fill, dtype=np.float64)
    for row in surface.itertuples():
        matrix[int(row.g_bin), int(row.d_bin)] = float(getattr(row, column))
    return matrix


def make_figure(
    primary: pd.DataFrame,
    closure_summary: pd.DataFrame,
    path_summary: pd.DataFrame,
    surface: pd.DataFrame,
    examples: dict,
    path: Path,
):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
    fig, axes = plt.subplots(3, 3, figsize=(18, 15), constrained_layout=True)
    blue, gold, grey, ink = "#3B6FB6", "#D99A2B", "#7B8794", "#202833"

    ax = axes[0, 0]
    colors = {"straight closure": blue, "circle-like": gold, "crooked/random-like": grey}
    for name in ("straight closure", "circle-like", "crooked/random-like"):
        item = examples.get(name)
        if not item:
            continue
        pts = np.asarray(item["points"])
        ax.plot(pts[:, 0], pts[:, 1], marker="o", ms=2.5, lw=1.8, color=colors[name], label=name)
        ax.scatter(pts[0, 0], pts[0, 1], s=35, facecolor="white", edgecolor=colors[name], zorder=4)
    ax.axhline(0, color="#D8DDE5", lw=0.8)
    ax.axvline(0, color="#D8DDE5", lw=0.8)
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_title("Example native path histories")
    ax.set_xlabel("x displacement / path length")
    ax.set_ylabel("z displacement / path length")
    ax.legend(frameon=False, fontsize=8)

    count = surface_matrix(surface, "windows", fill=0.0)
    im = axes[0, 1].imshow(count, origin="lower", extent=[0, 1, 0, 1], aspect="auto", cmap="Blues", norm=LogNorm(vmin=1, vmax=max(1, np.nanmax(count))))
    axes[0, 1].set_title("Window density on the line × turn plane")
    axes[0, 1].set_xlabel("line directness D")
    axes[0, 1].set_ylabel("turn consistency G")
    fig.colorbar(im, ax=axes[0, 1], label="windows (log scale)")

    circle = surface_matrix(surface, "circularity")
    im = axes[0, 2].imshow(circle, origin="lower", extent=[0, 1, 0, 1], aspect="auto", cmap="YlOrBr", vmin=0, vmax=max(0.01, np.nanmax(circle)))
    axes[0, 2].set_title("Historical circularity C=(1−D)G")
    axes[0, 2].set_xlabel("line directness D")
    axes[0, 2].set_ylabel("turn consistency G")
    fig.colorbar(im, ax=axes[0, 2], label="mean circularity")

    conn = surface_matrix(surface, "connection_info_nats")
    im = axes[1, 0].imshow(conn, origin="lower", extent=[0, 1, 0, 1], aspect="auto", cmap="Blues", vmin=np.nanmin(conn), vmax=np.nanmax(conn))
    axes[1, 0].set_title("Connection-relation information")
    axes[1, 0].set_xlabel("line directness D")
    axes[1, 0].set_ylabel("turn consistency G")
    fig.colorbar(im, ax=axes[1, 0], label="mean I_conn (nats)")

    movement = surface_matrix(surface, "movement_info_nats")
    bound = max(abs(float(np.nanmin(movement))), abs(float(np.nanmax(movement))), 1e-6)
    im = axes[1, 1].imshow(movement, origin="lower", extent=[0, 1, 0, 1], aspect="auto", cmap="PuOr", norm=TwoSlopeNorm(vmin=-bound, vcenter=0, vmax=bound))
    axes[1, 1].set_title("Future movement-address information")
    axes[1, 1].set_xlabel("line directness D")
    axes[1, 1].set_ylabel("turn consistency G")
    fig.colorbar(im, ax=axes[1, 1], label="mean I_move (nats)")

    primary_closure = closure_summary[closure_summary["window"] == PRIMARY_W]
    pooled = primary_closure.groupby(["closure_class", "class_name"], observed=True).agg(
        directness=("directness", "mean"), circularity=("circularity", "mean"), windows=("windows", "sum")
    ).reset_index()
    x = np.arange(len(pooled))
    axes[1, 2].bar(x - 0.18, pooled["directness"], width=0.36, color=blue, label="directness D")
    axes[1, 2].bar(x + 0.18, pooled["circularity"], width=0.36, color=gold, label="circularity C")
    axes[1, 2].set_xticks(x, [f"{n}\n(n={int(w):,})" for n, w in zip(pooled["class_name"], pooled["windows"])], rotation=12, ha="right")
    axes[1, 2].set_ylim(0, 1)
    axes[1, 2].set_title("Geometry by T344 closure class")
    axes[1, 2].set_ylabel("mean coordinate")
    axes[1, 2].legend(frameon=False)

    conn_pooled = primary_closure.groupby(["closure_class", "class_name"], observed=True).agg(
        connection_info_nats=("connection_info_nats", "mean"), windows=("windows", "sum")
    ).reset_index()
    axes[2, 0].bar(np.arange(len(conn_pooled)), conn_pooled["connection_info_nats"], color=blue)
    axes[2, 0].set_xticks(np.arange(len(conn_pooled)), [f"{n}\n(n={int(w):,})" for n, w in zip(conn_pooled["class_name"], conn_pooled["windows"])], rotation=12, ha="right")
    axes[2, 0].set_ylim(0, max(0.01, float(conn_pooled["connection_info_nats"].max()) * 1.15))
    axes[2, 0].set_title("Connection storage by closure class")
    axes[2, 0].set_ylabel("mean I_conn (nats)")

    path_pooled = path_summary.groupby(["path_class", "path_name"], observed=True).agg(
        movement_info_nats=("movement_info_nats", "mean"),
        delta_connection_info_nats=("delta_connection_info_nats", "mean"),
        windows=("windows", "sum"),
        tracks=("tracks", "sum"),
    ).reset_index()
    pcolors = [gold if value == 1 else grey for value in path_pooled["path_class"]]
    axes[2, 1].bar(np.arange(len(path_pooled)), path_pooled["movement_info_nats"], color=pcolors)
    axes[2, 1].axhline(0, color=ink, lw=0.9)
    axes[2, 1].set_xticks(np.arange(len(path_pooled)), [f"{n}\n(n={int(w):,})" for n, w in zip(path_pooled["path_name"], path_pooled["windows"])], rotation=12, ha="right")
    axes[2, 1].set_title("Future movement information by path type")
    axes[2, 1].set_ylabel("mean I_move (nats)")

    axes[2, 2].bar(np.arange(len(path_pooled)), path_pooled["delta_connection_info_nats"], color=pcolors)
    axes[2, 2].axhline(0, color=ink, lw=0.9)
    axes[2, 2].set_xticks(np.arange(len(path_pooled)), [f"{n}\n(n={int(w):,})" for n, w in zip(path_pooled["path_name"], path_pooled["windows"])], rotation=12, ha="right")
    axes[2, 2].set_title("Non-overlapping connection-information change")
    axes[2, 2].set_ylabel("mean ΔI_conn (nats)")

    for ax in axes.flat:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color="#E5E8ED", lw=0.6, alpha=0.7)
    fig.suptitle(
        f"T345 — line/circle geometry and two information ledgers ({REPRESENTATION})\n"
        f"Primary W=15; {len(primary):,} windows; whole trajectories remain the inference unit",
        fontsize=16,
        weight="bold",
        color=ink,
    )
    fig.savefig(path, dpi=180, facecolor="white")
    plt.close(fig)


def flatten_components(components: dict) -> pd.DataFrame:
    rows = []
    for name, item in components.items():
        row = {"component": name, "pass": item["pass"], "eligible": item["eligible"], **item["pooled"]}
        for condition, value in item["condition_effects"].items():
            row[condition] = value["estimate"]
            row[f"{condition}_strata"] = value["strata"]
        rows.append(row)
    return pd.DataFrame(rows)


def report(results: dict, path: Path):
    gates = results["gates"]
    lines = [
        "# T345 line–circle / two-ledger diagnostic report",
        "",
        "**Date:** 7 August 2026  ",
        f"**Representation:** {REPRESENTATION}  ",
        "**Status:** frozen post-T344 diagnostic; not an independent confirmation  ",
        f"**Protocol SHA-256:** `{PROTOCOL_SHA}`",
        "",
        "## Answer first",
        "",
        f"Gates A/B/C/D: **{' / '.join('PASS' if gates[k]['pass'] else 'FAIL' for k in ['A','B','C','D'])}**.",
        "",
        "T345 separates path straightness from historical circularity and future movement",
        "information from concentration in repeated ARA-sector relations. T344 remains frozen",
        "and is not rescued by this diagnostic.",
        "",
        "## Frozen component results",
        "",
        "| Component | Pooled estimate | 95% whole-track CI | Direction wins | Verdict |",
        "|---|---:|---:|---:|---|",
    ]
    for name, item in results["components"].items():
        pooled = item["pooled"]
        lines.append(
            f"| {name} | `{pooled['estimate']:.6f}` | "
            f"`[{pooled['ci_low']:.6f}, {pooled['ci_high']:.6f}]` | "
            f"`{item['direction_wins']}/3` | **{'PASS' if item['pass'] else 'FAIL'}** |"
        )
    lines += [
        "",
        "## Frozen gate composition",
        "",
        f"- Gate A — line/circle geometry: **{'PASS' if gates['A']['pass'] else 'FAIL'}**.",
        f"- Gate B — connection-storage ladder: **{'PASS' if gates['B']['pass'] else 'FAIL'}**.",
        f"- Gate C — coherent curve versus random crookedness: **{'PASS' if gates['C']['pass'] else 'FAIL'}**.",
        f"- Gate D — delayed connection accumulation: **{'PASS' if gates['D']['pass'] else 'FAIL'}**.",
        "",
        "## Boundaries",
        "",
        "- Historical circularity is a conservative circulation score, not proof of a perfect circle.",
        "- `I_conn` is relation-channel concentration relative to 16 uniform ordered ARA edges;",
        "  it is not total thermodynamic information.",
        "- `I_move` is realised information about one named future ARA movement address.",
        "- The source was opened in T344. These results are diagnostic even though the new",
        "  formulas and gates were frozen before T345 calculation.",
        "- No exact irrational constant participates in a primary result.",
        "",
        "## Artifacts",
        "",
        f"- `{PREFIX}_FIGURE.png`",
        f"- `{PREFIX}_CONTRASTS.csv`",
        f"- `{PREFIX}_CLOSURE_SUMMARY.csv`",
        f"- `{PREFIX}_PATH_SUMMARY.csv`",
        f"- `{PREFIX}_SURFACE.csv`",
        f"- `{PREFIX}_EXAMPLES.csv`",
        f"- `{PREFIX}_RESULTS.json`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    import hashlib

    actual_hash = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    if actual_hash != PROTOCOL_SHA:
        raise RuntimeError(f"Frozen protocol hash mismatch: {actual_hash}")

    tracks = []
    audits = []
    for condition in base.CONDITIONS:
        print(f"[T345:{REPRESENTATION}] loading {condition}", flush=True)
        loaded, audit = base.load_condition(condition)
        tracks.extend(loaded)
        audits.append(audit)
    print(f"[T345:{REPRESENTATION}] deriving event tracks: {len(tracks):,}", flush=True)
    events = [base.derive_track_events(track) for track in tracks]

    print(f"[T345:{REPRESENTATION}] building W={PRIMARY_W}", flush=True)
    primary, examples = build_windows(events, PRIMARY_W, collect_examples=True)
    print(f"[T345:{REPRESENTATION}] scoring movement information: {len(primary):,} windows", flush=True)
    scorer = score_window_information_memory_safe if REPRESENTATION == "num" else base.score_window_information
    primary, optimiser = scorer(primary)

    sensitivity = []
    for window in SENSITIVITY_WINDOWS:
        print(f"[T345:{REPRESENTATION}] building sensitivity W={window}", flush=True)
        frame, _ = build_windows(events, window)
        frame["information_nats"] = np.nan
        frame["speed_quintile"] = -1
        sensitivity.append(frame)

    print(f"[T345:{REPRESENTATION}] evaluating frozen contrasts", flush=True)
    components = {
        "A1 structured minus random circularity": component(primary, "A1", "closure_class", 1, 2, "circularity"),
        "A2 closure minus structured directness": component(primary, "A2", "closure_class", 0, 1, "directness"),
        "B1 closure minus structured connection": component(primary, "B1", "closure_class", 0, 1, "connection_info_nats"),
        "B2 structured minus random connection": component(primary, "B2", "closure_class", 1, 2, "connection_info_nats"),
        "C circle-like minus crooked movement info": component(primary, "C", "path_class", 1, 2, "information_nats"),
        "D1 circle-like future connection change": one_group_component(primary, "D1", "path_class", 1, "delta_connection_info_nats"),
        "D2 circle-like minus crooked connection change": component(primary, "D2", "path_class", 1, 2, "delta_connection_info_nats"),
    }
    gates = {
        "A": {"pass": components["A1 structured minus random circularity"]["pass"] and components["A2 closure minus structured directness"]["pass"]},
        "B": {"pass": components["B1 closure minus structured connection"]["pass"] and components["B2 structured minus random connection"]["pass"]},
        "C": {"pass": components["C circle-like minus crooked movement info"]["pass"]},
        "D": {"pass": components["D1 circle-like future connection change"]["pass"] and components["D2 circle-like minus crooked connection change"]["pass"]},
    }

    closure_summary, path_summary, surface = summaries(primary, sensitivity)
    contrasts = flatten_components(components)
    example_rows = []
    serial_examples = {}
    for name, item in examples.items():
        serial = {k: v for k, v in item.items() if k != "points"}
        serial["points"] = item["points"].tolist()
        serial_examples[name] = serial
        for order, point in enumerate(item["points"]):
            example_rows.append({**{k: v for k, v in item.items() if k != "points"}, "order": order, "x": point[0], "z": point[1]})

    results = {
        "test": "T345_LINE_CIRCLE_TWO_LEDGER",
        "representation": REPRESENTATION,
        "status": "frozen_post_T344_diagnostic",
        "protocol_sha256": PROTOCOL_SHA,
        "tracks": len(tracks),
        "primary_windows": len(primary),
        "sensitivity_windows": {str(f["window"].iloc[0]): len(f) for f in sensitivity if len(f)},
        "optimisers_all_converged": bool(all(item["success"] for item in optimiser)),
        "gates": gates,
        "components": components,
        "examples": serial_examples,
        "source_audits": audits,
    }

    closure_summary.to_csv(HERE / f"{PREFIX}_CLOSURE_SUMMARY.csv", index=False)
    path_summary.to_csv(HERE / f"{PREFIX}_PATH_SUMMARY.csv", index=False)
    surface.to_csv(HERE / f"{PREFIX}_SURFACE.csv", index=False)
    contrasts.to_csv(HERE / f"{PREFIX}_CONTRASTS.csv", index=False)
    pd.DataFrame(example_rows).to_csv(HERE / f"{PREFIX}_EXAMPLES.csv", index=False)
    pd.DataFrame(optimiser).to_csv(HERE / f"{PREFIX}_OPTIMISERS.csv", index=False)
    (HERE / f"{PREFIX}_RESULTS.json").write_text(json.dumps(results, indent=2, allow_nan=False), encoding="utf-8")
    make_figure(primary, closure_summary, path_summary, surface, examples, HERE / f"{PREFIX}_FIGURE.png")
    report(results, HERE / f"{PREFIX}_REPORT_2026-08-07.md")
    print(json.dumps({"gates": gates, "tracks": len(tracks), "windows": len(primary)}, indent=2), flush=True)


if __name__ == "__main__":
    main()
