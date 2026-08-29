"""T424 frozen real-hourglass Irrationality Di-ARA test.

Run in two stages so the Toyoura-sand material holdout is not scored until the
development calibration and models have been written and hashed:

    python t424_hourglass_test.py develop
    python t424_hourglass_test.py holdout
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import minimize


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source_data"
RESULTS = ROOT / "results"
EMA_ALPHA = 0.25
RNG_SEED = 42420260823
EXPECTED_RUNS_PER_MOVIE = 8

DEVELOPMENT_FILES = [
    "SN101_Alumina_060.mp4",
    "SN101_Alumina_120.mp4",
    "SN102_SilicaSandNo5_060.mp4",
    "SN102_SilicaSandNo5_120.mp4",
]
HOLDOUT_FILES = [
    "SN103_ToyouraSand_060.mp4",
    "SN103_ToyouraSand_120.mp4",
]

# Source-only condition boundaries, verified from the published on-screen
# "AG = ... G" label before any Toyoura ARA coordinate was extracted. The
# development montages use equal 200-frame blocks; the Toyoura montages have
# unequal block durations.
CONDITION_BOUNDARIES = {
    "SN101_Alumina_060.mp4": [200, 400, 600, 800, 1000, 1200, 1400],
    "SN101_Alumina_120.mp4": [200, 400, 600, 800, 1000, 1200, 1400],
    "SN102_SilicaSandNo5_060.mp4": [200, 400, 600, 800, 1000, 1200, 1400],
    "SN102_SilicaSandNo5_120.mp4": [200, 400, 600, 800, 1000, 1200, 1400],
    "SN103_ToyouraSand_060.mp4": [271, 551, 823, 1117, 1396, 1691, 1974],
    "SN103_ToyouraSand_120.mp4": [304, 576, 859, 1130, 1409, 1689, 1967],
}


@dataclass(frozen=True)
class Regions:
    analysis: tuple[float, float, float, float] = (0.28, 0.18, 0.72, 0.82)
    throat: tuple[float, float, float, float] = (0.43, 0.44, 0.57, 0.58)
    upstream: tuple[float, float, float, float] = (0.32, 0.27, 0.68, 0.45)
    downstream: tuple[float, float, float, float] = (0.32, 0.58, 0.68, 0.76)


REGIONS = Regions()


def rect(shape: tuple[int, int], bounds: tuple[float, float, float, float]) -> tuple[slice, slice]:
    h, w = shape
    x0, y0, x1, y1 = bounds
    return slice(int(y0 * h), int(y1 * h)), slice(int(x0 * w), int(x1 * w))


def causal_ema(values: np.ndarray, alpha: float = EMA_ALPHA) -> np.ndarray:
    out = np.empty_like(values, dtype=float)
    out[0] = values[0]
    for i in range(1, len(values)):
        out[i] = alpha * values[i] + (1.0 - alpha) * out[i - 1]
    return out


def top_fraction_mean(values: np.ndarray, fraction: float = 0.20) -> float:
    flat = np.asarray(values, dtype=float).ravel()
    if flat.size == 0:
        return float("nan")
    n = max(1, int(math.ceil(flat.size * fraction)))
    return float(np.mean(np.partition(flat, flat.size - n)[-n:]))


def safe_corr(a: np.ndarray, b: np.ndarray) -> float:
    aa = a.astype(np.float32).ravel()
    bb = b.astype(np.float32).ravel()
    aa -= float(np.mean(aa))
    bb -= float(np.mean(bb))
    denom = float(np.linalg.norm(aa) * np.linalg.norm(bb))
    if denom <= 1e-12:
        return 1.0 if float(np.mean(np.abs(a.astype(float) - b.astype(float)))) < 1e-6 else 0.0
    return float(np.clip(np.dot(aa, bb) / denom, -0.999, 0.999))


def shifted_texture_correlation(
    prev_gray: np.ndarray,
    gray: np.ndarray,
    flow: np.ndarray,
    mask_slice: tuple[slice, slice],
) -> float:
    ys, xs = mask_slice
    prev_roi = prev_gray[ys, xs]
    curr_roi = gray[ys, xs]
    flow_roi = flow[ys, xs]
    dx = float(np.median(flow_roi[..., 0]))
    dy = float(np.median(flow_roi[..., 1]))
    transform = np.float32([[1.0, 0.0, dx], [0.0, 1.0, dy]])
    shifted = cv2.warpAffine(
        prev_roi,
        transform,
        (prev_roi.shape[1], prev_roi.shape[0]),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT,
    )
    hp_prev = cv2.Laplacian(shifted, cv2.CV_32F, ksize=3)
    hp_curr = cv2.Laplacian(curr_roi, cv2.CV_32F, ksize=3)
    return safe_corr(hp_prev, hp_curr)


def current_texture_amount(gray: np.ndarray, mask_slice: tuple[slice, slice]) -> float:
    ys, xs = mask_slice
    hp = cv2.Laplacian(gray[ys, xs], cv2.CV_32F, ksize=3)
    return float(np.mean(np.abs(hp)))


def extract_raw(path: Path) -> tuple[pd.DataFrame, np.ndarray]:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {path}")
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    max_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    ok, first = cap.read()
    if not ok:
        raise RuntimeError(f"Could not read first frame from {path}")
    scale = 445.0 / first.shape[1]
    first_small = cv2.resize(first, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    first_gray_full = cv2.cvtColor(first_small, cv2.COLOR_BGR2GRAY)
    analysis_slice = rect(first_gray_full.shape, REGIONS.analysis)
    prev = first_gray_full[analysis_slice]
    ah, aw = prev.shape

    def local_bounds(bounds: tuple[float, float, float, float]) -> tuple[slice, slice]:
        ax0, ay0, ax1, ay1 = REGIONS.analysis
        x0, y0, x1, y1 = bounds
        local = (
            (x0 - ax0) / (ax1 - ax0),
            (y0 - ay0) / (ay1 - ay0),
            (x1 - ax0) / (ax1 - ax0),
            (y1 - ay0) / (ay1 - ay0),
        )
        return rect((ah, aw), local)

    throat = local_bounds(REGIONS.throat)
    upstream = local_bounds(REGIONS.upstream)
    downstream = local_bounds(REGIONS.downstream)
    records: list[dict[str, float | int | str]] = []
    preview = first_small.copy()

    for frame_index in range(1, max_frames):
        ok, frame = cap.read()
        if not ok:
            break
        small = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        gray_full = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        gray = gray_full[analysis_slice]
        flow = cv2.calcOpticalFlowFarneback(
            prev,
            gray,
            None,
            pyr_scale=0.5,
            levels=3,
            winsize=17,
            iterations=3,
            poly_n=5,
            poly_sigma=1.2,
            flags=0,
        )
        speed = np.linalg.norm(flow, axis=2)
        tys, txs = throat
        uys, uxs = upstream
        dys, dxs = downstream
        trav_raw = top_fraction_mean(np.abs(flow[tys, txs, 1]))
        receive_raw = top_fraction_mean(np.abs(flow[dys, dxs, 1]))
        upper_motion_raw = top_fraction_mean(speed[uys, uxs])
        conn_raw = shifted_texture_correlation(prev, gray, flow, upstream)
        amount_raw = current_texture_amount(gray, upstream)
        global_diff = float(np.mean(np.abs(gray.astype(float) - prev.astype(float))))
        records.append(
            {
                "video": path.name,
                "frame": frame_index,
                "time_s": frame_index / fps,
                "fps": fps,
                "trav_raw": trav_raw,
                "conn_raw": conn_raw,
                "receive_raw": receive_raw,
                "upper_motion_raw": upper_motion_raw,
                "amount_raw": amount_raw,
                "global_diff": global_diff,
            }
        )
        prev = gray
    cap.release()

    colors = {
        "analysis": (180, 180, 180),
        "throat": (0, 160, 255),
        "upstream": (100, 220, 100),
        "downstream": (255, 130, 80),
    }
    for name, bounds in (
        ("analysis", REGIONS.analysis),
        ("throat", REGIONS.throat),
        ("upstream", REGIONS.upstream),
        ("downstream", REGIONS.downstream),
    ):
        x0, y0, x1, y1 = bounds
        p0 = (int(x0 * preview.shape[1]), int(y0 * preview.shape[0]))
        p1 = (int(x1 * preview.shape[1]), int(y1 * preview.shape[0]))
        cv2.rectangle(preview, p0, p1, colors[name], 2)
        cv2.putText(preview, name, (p0[0] + 3, p0[1] + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, colors[name], 1, cv2.LINE_AA)
    return pd.DataFrame.from_records(records), preview


def split_montage(frame: pd.DataFrame, cuts: list[int]) -> tuple[pd.DataFrame, list[int]]:
    """Register published AG-condition changes without using an ARA coordinate."""
    out = frame.copy()
    if len(cuts) != EXPECTED_RUNS_PER_MOVIE - 1:
        raise ValueError(f"Expected seven AG-condition boundaries, got {cuts}")
    out["edit_cut"] = out["frame"].isin(cuts)
    out["gravity_index"] = np.searchsorted(np.asarray(cuts, dtype=int), out["frame"].to_numpy(int), side="right")
    starts = [1] + [cut + 1 for cut in cuts]
    local_frame = np.zeros(len(out), dtype=int)
    for gravity_index, start in enumerate(starts):
        mask = out["gravity_index"].to_numpy(int) == gravity_index
        local_frame[mask] = out.loc[mask, "frame"].to_numpy(int) - start
    out["local_frame"] = local_frame
    out["run_time_s"] = local_frame / out["fps"].to_numpy(float)
    stem = Path(str(out["video"].iloc[0])).stem
    out["run_id"] = [f"{stem}_g{int(i)}" for i in out["gravity_index"]]
    out = out[~out["edit_cut"] & (out["local_frame"] >= 1)].reset_index(drop=True)
    return out, cuts


def robust_threshold(values: np.ndarray) -> float:
    finite = np.asarray(values, dtype=float)
    finite = finite[np.isfinite(finite)]
    if not len(finite):
        return 0.0
    noise = finite[int(0.75 * len(finite)) :]
    median = float(np.median(noise))
    mad = float(np.median(np.abs(noise - median))) + 1e-9
    return max(median + 6.0 * mad, 0.12 * float(np.quantile(finite, 0.95)))


def label_events(frame: pd.DataFrame) -> tuple[pd.DataFrame, list[dict[str, float | int | str]]]:
    out = frame.copy()
    smooth_receive = causal_ema(out["receive_raw"].to_numpy(float), 0.35)
    threshold = robust_threshold(smooth_receive)
    active = smooth_receive > threshold
    fps = float(out["fps"].iloc[0])
    persistence = max(8, int(round(0.30 * fps)))
    peak = int(np.argmax(smooth_receive))
    closure = len(out) - 1
    for i in range(peak + 1, len(out) - persistence):
        if not np.any(active[i : i + persistence]) and np.count_nonzero(active[i + persistence :]) <= 2:
            closure = i
            break

    events: list[dict[str, float | int | str]] = [
        {
            "video": str(out["video"].iloc[0]),
            "run_id": str(out["run_id"].iloc[0]),
            "gravity_index": int(out["gravity_index"].iloc[0]),
            "event_type": "terminal_closure",
            "frame": int(out["frame"].iloc[closure]),
            "time_s": float(out["run_time_s"].iloc[closure]),
            "threshold": threshold,
        }
    ]
    min_jam = max(4, int(round(0.16 * fps)))
    i = peak + 1
    while i < closure - min_jam:
        if active[i]:
            i += 1
            continue
        j = i
        while j < closure and not active[j]:
            j += 1
        if j - i >= min_jam and j < closure and np.count_nonzero(active[j : min(j + 3, closure)]) >= 2:
            events.append(
                {
                    "video": str(out["video"].iloc[0]),
                    "run_id": str(out["run_id"].iloc[0]),
                    "gravity_index": int(out["gravity_index"].iloc[0]),
                    "event_type": "microjam_release",
                    "frame": int(out["frame"].iloc[j]),
                    "time_s": float(out["run_time_s"].iloc[j]),
                    "threshold": threshold,
                }
            )
        i = max(j + 1, i + 1)

    out["receive_smooth"] = smooth_receive
    out["receive_threshold"] = threshold
    out["direct_active"] = active.astype(int)
    out["closure_index"] = closure
    return out, events


def calibration_from_development(frame: pd.DataFrame) -> dict[str, float]:
    trav = np.log1p(frame["trav_raw"].to_numpy(float))
    conn = np.arctanh(np.clip(frame["conn_raw"].to_numpy(float), -0.995, 0.995))
    return {
        "trav_q05": float(np.quantile(trav, 0.05)),
        "trav_q95": float(np.quantile(trav, 0.95)),
        "conn_q05": float(np.quantile(conn, 0.05)),
        "conn_q95": float(np.quantile(conn, 0.95)),
        "ema_alpha": EMA_ALPHA,
    }


def map_ara(frame: pd.DataFrame, calibration: dict[str, float]) -> pd.DataFrame:
    out = frame.copy()
    trav = np.log1p(out["trav_raw"].to_numpy(float))
    conn = np.arctanh(np.clip(out["conn_raw"].to_numpy(float), -0.995, 0.995))
    x_trav = 2.0 * np.clip(
        (trav - calibration["trav_q05"]) / (calibration["trav_q95"] - calibration["trav_q05"]),
        0.0,
        1.0,
    )
    x_conn = 2.0 * np.clip(
        (conn - calibration["conn_q05"]) / (calibration["conn_q95"] - calibration["conn_q05"]),
        0.0,
        1.0,
    )
    out["x_trav"] = causal_ema(x_trav)
    out["x_conn"] = causal_ema(x_conn)
    fps = float(out["fps"].iloc[0])
    out["dx_trav_dt"] = np.gradient(out["x_trav"].to_numpy(float)) * fps
    out["dx_conn_dt"] = np.gradient(out["x_conn"].to_numpy(float)) * fps
    out["d_eq"] = np.abs(out["x_trav"] - out["x_conn"]) / math.sqrt(2.0)
    out["s_joint"] = (out["x_trav"] + out["x_conn"]) / 2.0
    quadrants = (out["x_trav"].to_numpy() >= 1).astype(int) * 2 + (out["x_conn"].to_numpy() >= 1).astype(int)
    out["quadrant"] = quadrants
    last_change = 0
    ages = np.zeros(len(out), dtype=float)
    for i in range(1, len(out)):
        if quadrants[i] != quadrants[i - 1]:
            last_change = i
        ages[i] = (i - last_change) / fps
    out["quadrant_age_s"] = ages
    amount = np.log1p(out["amount_raw"].to_numpy(float))
    out["amount_proxy"] = amount
    out["elapsed_s"] = out["run_time_s"]
    return out


FEATURE_SETS = {
    "joint_di_ara": ["x_trav", "x_conn", "dx_trav_dt", "dx_conn_dt", "d_eq", "s_joint", "quadrant_age_s"],
    "traversal_only": ["x_trav", "dx_trav_dt"],
    "connection_only": ["x_conn", "dx_conn_dt"],
    "amount_only": ["amount_proxy"],
    "elapsed_only": ["elapsed_s"],
}


def build_target(frame: pd.DataFrame, events: list[dict[str, float | int | str]]) -> np.ndarray:
    target = np.zeros(len(frame), dtype=int)
    fps = float(frame["fps"].iloc[0])
    lead_min = max(1, int(round(3 * fps / 25.0)))
    lead_max = max(lead_min + 1, int(round(12 * fps / 25.0)))
    frames = frame["frame"].to_numpy(int)
    for event in events:
        event_frame = int(event["frame"])
        if event["event_type"] == "terminal_closure" or event["event_type"] == "microjam_release":
            target[(frames >= event_frame - lead_max) & (frames <= event_frame - lead_min)] = 1
    return target


def logistic_fit(x: np.ndarray, y: np.ndarray, l2: float = 0.10) -> tuple[np.ndarray, float]:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mean = np.mean(x, axis=0)
    scale = np.std(x, axis=0)
    scale[scale < 1e-9] = 1.0
    z = (x - mean) / scale

    def objective(beta: np.ndarray) -> tuple[float, np.ndarray]:
        logits = beta[0] + z @ beta[1:]
        loss = np.sum(np.logaddexp(0.0, logits) - y * logits) + 0.5 * l2 * np.sum(beta[1:] ** 2)
        probs = 1.0 / (1.0 + np.exp(-np.clip(logits, -40, 40)))
        error = probs - y
        grad = np.r_[np.sum(error), z.T @ error + l2 * beta[1:]]
        return float(loss), grad

    initial = np.zeros(x.shape[1] + 1)
    initial[0] = math.log((np.mean(y) + 1e-4) / (1.0 - np.mean(y) + 1e-4))
    fitted = minimize(lambda b: objective(b)[0], initial, jac=lambda b: objective(b)[1], method="L-BFGS-B")
    if not fitted.success:
        raise RuntimeError(f"Logistic fit failed: {fitted.message}")
    return fitted.x, float(fitted.fun)


def logistic_predict(x: np.ndarray, model: dict[str, object]) -> np.ndarray:
    mean = np.asarray(model["mean"], dtype=float)
    scale = np.asarray(model["scale"], dtype=float)
    beta = np.asarray(model["beta"], dtype=float)
    z = (np.asarray(x, dtype=float) - mean) / scale
    logits = beta[0] + z @ beta[1:]
    return 1.0 / (1.0 + np.exp(-np.clip(logits, -40, 40)))


def average_precision(y: np.ndarray, p: np.ndarray) -> float:
    y = np.asarray(y, dtype=int)
    if np.sum(y) == 0:
        return float("nan")
    order = np.argsort(-p)
    ranked = y[order]
    precision = np.cumsum(ranked) / (np.arange(len(ranked)) + 1)
    return float(np.sum(precision * ranked) / np.sum(ranked))


def f1_threshold(y: np.ndarray, p: np.ndarray) -> float:
    best = (0.0, 0.5)
    for threshold in np.unique(np.quantile(p, np.linspace(0.05, 0.99, 100))):
        pred = p >= threshold
        tp = int(np.sum(pred & (y == 1)))
        fp = int(np.sum(pred & (y == 0)))
        fn = int(np.sum((~pred) & (y == 1)))
        score = 2 * tp / max(1, 2 * tp + fp + fn)
        if score > best[0]:
            best = (score, float(threshold))
    return best[1]


def prepare_stage(files: list[str], calibration: dict[str, float] | None = None) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, np.ndarray]]:
    all_frames: list[pd.DataFrame] = []
    events: list[dict[str, float | int | str]] = []
    previews: dict[str, np.ndarray] = {}
    montage_register: dict[str, list[int]] = {}
    for filename in files:
        raw, preview = extract_raw(SOURCE / filename)
        cuts = CONDITION_BOUNDARIES[filename]
        segmented, cuts = split_montage(raw, cuts)
        montage_register[filename] = cuts
        for _, run in segmented.groupby("run_id", sort=False):
            labelled, run_events = label_events(run.reset_index(drop=True))
            all_frames.append(labelled)
            events.extend(run_events)
        previews[filename] = preview
    combined = pd.concat(all_frames, ignore_index=True)
    if calibration is not None:
        combined = pd.concat(
            [map_ara(group.reset_index(drop=True), calibration) for _, group in combined.groupby("run_id", sort=False)],
            ignore_index=True,
        )
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "T424_MONTAGE_CUT_REGISTER.json").write_text(json.dumps(montage_register, indent=2) + "\n", encoding="utf-8")
    return combined, pd.DataFrame(events), previews


def save_previews(previews: dict[str, np.ndarray], suffix: str) -> None:
    out = RESULTS / "source_geometry"
    out.mkdir(parents=True, exist_ok=True)
    for filename, image in previews.items():
        cv2.imwrite(str(out / f"{Path(filename).stem}_{suffix}_regions.jpg"), image)


def train_models(frame: pd.DataFrame, events: pd.DataFrame) -> dict[str, object]:
    targets = []
    rows = []
    for run_id, group in frame.groupby("run_id", sort=False):
        group = group.reset_index(drop=True)
        event_rows = events[events["run_id"] == run_id].to_dict("records")
        y = build_target(group, event_rows)
        # closure_index is local to this segmented gravity run, whereas
        # frame is the source-movie frame number. Compare like with like so
        # every run—not only the first montage segment—contributes correctly.
        valid = np.arange(len(group)) <= int(group["closure_index"].iloc[0])
        rows.append(group.loc[valid].copy())
        targets.append(y[valid])
    train = pd.concat(rows, ignore_index=True)
    y_train = np.concatenate(targets)
    models: dict[str, object] = {}
    for name, columns in FEATURE_SETS.items():
        x = train[columns].to_numpy(float)
        mean = np.mean(x, axis=0)
        scale = np.std(x, axis=0)
        scale[scale < 1e-9] = 1.0
        beta, loss = logistic_fit(x, y_train)
        model = {
            "columns": columns,
            "mean": mean.tolist(),
            "scale": scale.tolist(),
            "beta": beta.tolist(),
            "loss": loss,
        }
        probs = logistic_predict(x, model)
        model["development_ap"] = average_precision(y_train, probs)
        model["development_brier"] = float(np.mean((probs - y_train) ** 2))
        model["threshold"] = f1_threshold(y_train, probs)
        models[name] = model
    return {"models": models, "positive_frames": int(np.sum(y_train)), "total_frames": int(len(y_train))}


def score_models(frame: pd.DataFrame, events: pd.DataFrame, model_packet: dict[str, object]) -> tuple[pd.DataFrame, pd.DataFrame]:
    scored_frames: list[pd.DataFrame] = []
    y_parts: list[np.ndarray] = []
    for run_id, group in frame.groupby("run_id", sort=False):
        group = group.reset_index(drop=True)
        event_rows = events[events["run_id"] == run_id].to_dict("records")
        y = build_target(group, event_rows)
        valid = np.arange(len(group)) <= int(group["closure_index"].iloc[0])
        out = group.loc[valid].copy()
        out["target_next_handover"] = y[valid]
        for name, model in model_packet["models"].items():
            out[f"p_{name}"] = logistic_predict(out[model["columns"]].to_numpy(float), model)
        scored_frames.append(out)
        y_parts.append(y[valid])
    scored = pd.concat(scored_frames, ignore_index=True)
    y_all = np.concatenate(y_parts)
    metrics = []
    for name, model in model_packet["models"].items():
        p = scored[f"p_{name}"].to_numpy(float)
        pred = p >= float(model["threshold"])
        metrics.append(
            {
                "model": name,
                "average_precision": average_precision(y_all, p),
                "brier": float(np.mean((p - y_all) ** 2)),
                "positive_frames": int(np.sum(y_all)),
                "total_frames": int(len(y_all)),
                "threshold": float(model["threshold"]),
                "flagged_frames": int(np.sum(pred)),
            }
        )
    return scored, pd.DataFrame(metrics)


def instrument_checks(frame: pd.DataFrame) -> dict[str, float | bool]:
    x = frame["x_trav"].to_numpy(float)
    y = frame["x_conn"].to_numpy(float)
    corr = float(np.corrcoef(x, y)[0, 1])
    complement_rmse = float(np.sqrt(np.mean((y - (2.0 - x)) ** 2)))
    sum_std = float(np.std(x + y))
    return {
        "correlation": corr,
        "absolute_correlation_below_0_98": abs(corr) < 0.98,
        "sum_std": sum_std,
        "sum_std_above_0_05": sum_std > 0.05,
        "complement_rmse": complement_rmse,
        "not_exact_complements": complement_rmse > 1e-6,
    }


def structural_null(frame: pd.DataFrame, events: pd.DataFrame, permutations: int = 10_000) -> dict[str, float | int]:
    event_distances = []
    grouped = {name: group.reset_index(drop=True) for name, group in frame.groupby("run_id", sort=False)}
    event_indices: dict[str, list[int]] = {}
    for run_id, group in grouped.items():
        event_indices[run_id] = []
        for event in events[events["run_id"] == run_id].to_dict("records"):
            idx = int(np.argmin(np.abs(group["frame"].to_numpy(int) - int(event["frame"]))))
            event_indices[run_id].append(idx)
            event_distances.append(float(group["d_eq"].iloc[idx]))
    observed = float(np.median(event_distances))
    rng = np.random.default_rng(RNG_SEED)
    null = np.empty(permutations, dtype=float)
    for p in range(permutations):
        distances = []
        for run_id, group in grouped.items():
            x_trav = group["x_trav"].to_numpy(float)
            x_conn = group["x_conn"].to_numpy(float)
            if len(group) < 20:
                continue
            shift = int(rng.integers(10, len(group) - 9))
            shifted = np.roll(x_conn, shift)
            for idx in event_indices[run_id]:
                distances.append(abs(x_trav[idx] - shifted[idx]) / math.sqrt(2.0))
        null[p] = np.median(distances)
    null_median = float(np.median(null))
    return {
        "event_count": len(event_distances),
        "observed_median_d_eq": observed,
        "null_median_d_eq": null_median,
        "improvement_fraction": (null_median - observed) / null_median if null_median else float("nan"),
        "empirical_p": float((1 + np.count_nonzero(null <= observed)) / (permutations + 1)),
        "permutations": permutations,
    }


def warning_leads(scored: pd.DataFrame, events: pd.DataFrame, model_packet: dict[str, object]) -> pd.DataFrame:
    rows = []
    threshold = float(model_packet["models"]["joint_di_ara"]["threshold"])
    for run_id, group in scored.groupby("run_id", sort=False):
        group = group.reset_index(drop=True)
        fps = float(group["fps"].iloc[0])
        p = group["p_joint_di_ara"].to_numpy(float)
        frames = group["frame"].to_numpy(int)
        for event in events[events["run_id"] == run_id].to_dict("records"):
            event_frame = int(event["frame"])
            candidates = np.where((frames < event_frame) & (frames >= event_frame - int(2.5 * fps)) & (p >= threshold))[0]
            if len(candidates):
                first = int(candidates[0])
                lead_frames = event_frame - int(frames[first])
                rows.append({"video": str(group["video"].iloc[0]), "run_id": run_id, "gravity_index": int(group["gravity_index"].iloc[0]), "event_type": event["event_type"], "lead_frames": lead_frames, "lead_s": lead_frames / fps, "forecast_found": True})
            else:
                rows.append({"video": str(group["video"].iloc[0]), "run_id": run_id, "gravity_index": int(group["gravity_index"].iloc[0]), "event_type": event["event_type"], "lead_frames": np.nan, "lead_s": np.nan, "forecast_found": False})
    return pd.DataFrame(rows)


def representative_runs(frame: pd.DataFrame) -> list[str]:
    chosen: list[str] = []
    for _, video_frame in frame.groupby("video", sort=False):
        available = sorted(video_frame["gravity_index"].unique())
        for index in [available[0], available[len(available) // 2], available[-1]]:
            run_id = str(video_frame.loc[video_frame["gravity_index"] == index, "run_id"].iloc[0])
            if run_id not in chosen:
                chosen.append(run_id)
    return chosen


def plot_timeseries(frame: pd.DataFrame, events: pd.DataFrame, path: Path, title: str, probability: bool = False) -> None:
    runs = representative_runs(frame)
    fig, axes = plt.subplots(len(runs), 1, figsize=(12, 2.8 * len(runs)), sharex=False, constrained_layout=True)
    if len(runs) == 1:
        axes = [axes]
    for ax, run_id in zip(axes, runs):
        group = frame[frame["run_id"] == run_id]
        ax.plot(group["run_time_s"], group["x_trav"], color="#377eb8", label="C1 traversal / movement ARA")
        ax.plot(group["run_time_s"], group["x_conn"], color="#e68613", label="C2 connection / packing ARA")
        ax.axhline(1.0, color="#555555", lw=1, ls="--", label="ARA ridge 1.0")
        for _, event in events[events["run_id"] == run_id].iterrows():
            ax.axvline(event["time_s"], color="#7b3294", lw=1.5, ls=":" if event["event_type"] == "microjam_release" else "--")
        if probability and "p_joint_di_ara" in group:
            ax2 = ax.twinx()
            ax2.plot(group["run_time_s"], group["p_joint_di_ara"], color="#4daf4a", alpha=0.7, label="Frozen joint handover probability")
            ax2.set_ylabel("Forecast probability (0–1)")
            ax2.set_ylim(0, 1)
        ax.set_title(run_id)
        ax.set_ylabel("Independent ARA coordinate (0–2)")
        ax.set_ylim(-0.03, 2.03)
        ax.grid(alpha=0.22)
    axes[-1].set_xlabel("Time from published clip start (s)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, frameon=False)
    fig.suptitle(title, fontsize=15)
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_plane(frame: pd.DataFrame, events: pd.DataFrame, path: Path, title: str) -> None:
    runs = representative_runs(frame)
    columns = 3
    rows = int(math.ceil(len(runs) / columns))
    fig, axes_grid = plt.subplots(rows, columns, figsize=(16, 5.2 * rows), constrained_layout=True)
    axes = np.atleast_1d(axes_grid).ravel()
    for ax, run_id in zip(axes, runs):
        group = frame[frame["run_id"] == run_id].reset_index(drop=True)
        points = ax.scatter(group["x_trav"], group["x_conn"], c=group["run_time_s"], s=14, cmap="viridis", alpha=0.72)
        step = max(1, len(group) // 18)
        ax.quiver(
            group["x_trav"].to_numpy()[::step][:-1],
            group["x_conn"].to_numpy()[::step][:-1],
            np.diff(group["x_trav"].to_numpy()[::step]),
            np.diff(group["x_conn"].to_numpy()[::step]),
            angles="xy",
            scale_units="xy",
            scale=1,
            width=0.004,
            color="#444444",
            alpha=0.65,
        )
        for _, event in events[events["run_id"] == run_id].iterrows():
            idx = int(np.argmin(np.abs(group["frame"].to_numpy() - int(event["frame"]))))
            ax.scatter(group["x_trav"].iloc[idx], group["x_conn"].iloc[idx], marker="*", s=180, color="#7b3294", edgecolor="white", linewidth=0.8, zorder=5)
        ax.axvline(1.0, color="#666666", ls="--", lw=1)
        ax.axhline(1.0, color="#666666", ls="--", lw=1)
        ax.plot([0, 2], [0, 2], color="#999999", ls=":", lw=1)
        ax.set_xlim(0, 2)
        ax.set_ylim(0, 2)
        ax.set_aspect("equal", adjustable="box")
        ax.set_title(run_id)
        ax.set_xlabel("C1 traversal / movement ARA (0–2)")
        ax.set_ylabel("C2 connection / packing ARA (0–2)")
        fig.colorbar(points, ax=ax, label="Time (s)", fraction=0.046, pad=0.04)
    for ax in axes[len(runs) :]:
        ax.remove()
    fig.suptitle(title, fontsize=15)
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_model_metrics(metrics: pd.DataFrame, path: Path) -> None:
    order = ["joint_di_ara", "traversal_only", "connection_only", "amount_only", "elapsed_only"]
    shown = metrics.set_index("model").loc[order].reset_index()
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3), constrained_layout=True)
    colors = ["#d99a27"] + ["#aeb7c2"] * 4
    axes[0].barh(shown["model"], shown["average_precision"], color=colors)
    axes[0].set_xlabel("Average precision (higher is better)")
    axes[0].set_xlim(0, max(1.0, float(shown["average_precision"].max()) * 1.1))
    axes[0].invert_yaxis()
    axes[0].grid(axis="x", alpha=0.22)
    axes[1].barh(shown["model"], shown["brier"], color=colors)
    axes[1].set_xlabel("Brier score (lower is better)")
    axes[1].invert_yaxis()
    axes[1].grid(axis="x", alpha=0.22)
    fig.suptitle("Frozen Toyoura-sand holdout: joint Di-ARA against named baselines", fontsize=14)
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def develop() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    raw, events, previews = prepare_stage(DEVELOPMENT_FILES)
    calibration = calibration_from_development(raw)
    mapped = pd.concat(
        [map_ara(group.reset_index(drop=True), calibration) for _, group in raw.groupby("run_id", sort=False)],
        ignore_index=True,
    )
    model_packet = train_models(mapped, events)
    packet = {
        "stage": "development_frozen",
        "source_files": DEVELOPMENT_FILES,
        "calibration": calibration,
        **model_packet,
    }
    raw.to_csv(RESULTS / "T424_DEVELOPMENT_RAW_SIGNALS.csv", index=False)
    mapped.to_csv(RESULTS / "T424_DEVELOPMENT_ARA_COORDINATES.csv", index=False)
    events.to_csv(RESULTS / "T424_DEVELOPMENT_DIRECT_EVENTS.csv", index=False)
    save_previews(previews, "development")
    model_path = RESULTS / "T424_FROZEN_MODEL.json"
    model_path.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    (RESULTS / "T424_FROZEN_MODEL.sha256").write_text(digest(model_path) + "  " + model_path.name + "\n", encoding="utf-8")
    checks = instrument_checks(mapped)
    (RESULTS / "T424_DEVELOPMENT_INSTRUMENT_CHECKS.json").write_text(json.dumps(checks, indent=2) + "\n", encoding="utf-8")
    plot_timeseries(mapped, events, RESULTS / "T424_DEVELOPMENT_TIMESERIES.png", "T424 development: independent hourglass child histories")
    plot_plane(mapped, events, RESULTS / "T424_DEVELOPMENT_DI_ARA_PLANE.png", "T424 development: hourglass Irrationality Di-ARA trajectories")
    print(json.dumps({"calibration": calibration, "instrument_checks": checks, "events": events.to_dict("records"), "model_summary": {k: {"ap": v["development_ap"], "brier": v["development_brier"], "threshold": v["threshold"]} for k, v in packet["models"].items()}, "model_sha256": digest(model_path)}, indent=2))


def holdout() -> None:
    model_path = RESULTS / "T424_FROZEN_MODEL.json"
    if not model_path.exists():
        raise RuntimeError("Run the development stage first")
    packet = json.loads(model_path.read_text(encoding="utf-8"))
    expected_hash = (RESULTS / "T424_FROZEN_MODEL.sha256").read_text(encoding="utf-8").split()[0]
    if digest(model_path) != expected_hash:
        raise RuntimeError("Frozen model hash mismatch")
    frame, events, previews = prepare_stage(HOLDOUT_FILES, packet["calibration"])
    scored, metrics = score_models(frame, events, packet)
    checks = instrument_checks(frame)
    structural = structural_null(frame, events)
    leads = warning_leads(scored, events, packet)
    joint = metrics[metrics["model"] == "joint_di_ara"].iloc[0]
    baselines = metrics[metrics["model"] != "joint_di_ara"]
    best_ap = float(baselines["average_precision"].max())
    best_brier = float(baselines["brier"].min())
    gates = {
        "instrument_valid": bool(checks["absolute_correlation_below_0_98"] and checks["sum_std_above_0_05"] and checks["not_exact_complements"]),
        "structural_improvement_at_least_20pct": bool(structural["improvement_fraction"] >= 0.20),
        "structural_p_below_0_05": bool(structural["empirical_p"] < 0.05),
        "joint_ap_beats_every_baseline": bool(float(joint["average_precision"]) > best_ap),
        "joint_brier_improves_at_least_10pct": bool(float(joint["brier"]) <= 0.90 * best_brier),
        "positive_median_warning_lead": bool(leads["lead_s"].dropna().median() > 0 if leads["lead_s"].notna().any() else False),
    }
    outcome = {
        "stage": "material_holdout_scored",
        "frozen_model_sha256": expected_hash,
        "source_files": HOLDOUT_FILES,
        "instrument_checks": checks,
        "structural_null": structural,
        "metrics": metrics.to_dict("records"),
        "warning_leads": leads.to_dict("records"),
        "gates": gates,
        "primary_gate_pass": bool(all(gates.values())),
    }
    frame.to_csv(RESULTS / "T424_HOLDOUT_ARA_COORDINATES.csv", index=False)
    scored.to_csv(RESULTS / "T424_HOLDOUT_SCORED_FRAMES.csv", index=False)
    events.to_csv(RESULTS / "T424_HOLDOUT_DIRECT_EVENTS.csv", index=False)
    metrics.to_csv(RESULTS / "T424_HOLDOUT_MODEL_METRICS.csv", index=False)
    leads.to_csv(RESULTS / "T424_HOLDOUT_WARNING_LEADS.csv", index=False)
    (RESULTS / "T424_HOLDOUT_OUTCOME.json").write_text(json.dumps(outcome, indent=2) + "\n", encoding="utf-8")
    save_previews(previews, "holdout")
    plot_timeseries(scored, events, RESULTS / "T424_HOLDOUT_TIMESERIES.png", "T424 untouched Toyoura-sand holdout: ARA histories and direct handovers", probability=True)
    plot_plane(scored, events, RESULTS / "T424_HOLDOUT_DI_ARA_PLANE.png", "T424 untouched Toyoura-sand holdout: Irrationality Di-ARA trajectories")
    plot_model_metrics(metrics, RESULTS / "T424_HOLDOUT_MODEL_COMPARISON.png")
    print(json.dumps(outcome, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["develop", "holdout"])
    args = parser.parse_args()
    if args.stage == "develop":
        develop()
    else:
        holdout()


if __name__ == "__main__":
    main()
