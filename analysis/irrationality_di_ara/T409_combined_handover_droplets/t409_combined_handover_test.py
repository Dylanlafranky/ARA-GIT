"""Run frozen T409 combined Rationality/Irrationality Di-ARA test."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import permutations
import csv
import json
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter1d, median_filter


HERE = Path(__file__).resolve().parent
VIDEO_DIR = HERE / "source_videos"
OUT_DIR = HERE / "results"
RNG = np.random.default_rng(4092026)


@dataclass(frozen=True)
class Event:
    event_id: str
    video: str
    x0: int
    x1: int
    start: int
    target: int
    end: int
    split: str
    rotate_clockwise: bool = False


EVENTS = (
    Event("E1", "Video_S2.mp4", 70, 900, 0, 198, 300, "development"),
    Event("E2", "Video_S3.mp4", 70, 570, 0, 55, 90, "development"),
    Event("E3", "Video_S3.mp4", 180, 800, 60, 136, 165, "holdout"),
    Event("E4", "Video_S3.mp4", 320, 1000, 142, 182, 225, "holdout"),
    Event("E5", "Video_S4.mp4", 40, 660, 0, 48, 95, "development", True),
    Event("E6", "Video_S5.mp4", 70, 900, 0, 75, 125, "holdout"),
    Event("E7", "Video_S6.mp4", 70, 950, 0, 45, 105, "development"),
    Event("E8", "Video_S7.mp4", 70, 950, 0, 95, 160, "holdout"),
)


def orient(frame: np.ndarray, event: Event) -> np.ndarray:
    if event.rotate_clockwise:
        return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    return frame


def silhouette(frame: np.ndarray) -> tuple[np.ndarray, int, float]:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(float)
    h, w = gray.shape
    row_darkness = np.mean(gray[:, int(0.08 * w) : int(0.92 * w)], axis=1)
    centre = int(np.argmin(gaussian_filter1d(row_darkness, 2.0)))
    border_h = max(8, h // 12)
    border = np.concatenate(
        [gray[:border_h, : w // 2].ravel(), gray[-border_h:, : w // 2].ravel()]
    )
    background = float(np.median(border))
    threshold = background - 32.0
    y0 = max(0, centre - int(0.42 * h))
    y1 = min(h, centre + int(0.42 * h) + 1)
    local = gray[y0:y1]
    ys = np.arange(y0, y1)[:, None]
    dark = local < threshold
    distances = np.where(dark, np.abs(ys - centre), -1.0)
    half_height = np.maximum(np.max(distances, axis=0), 0.0)
    half_height = median_filter(half_height, size=5, mode="nearest")
    half_height = gaussian_filter1d(half_height, 4.0)
    return half_height, centre, background


def droplet_mask(frame: np.ndarray, x0: int, x1: int) -> tuple[np.ndarray, float]:
    profile, centre, _ = silhouette(frame)
    profile = profile[x0:x1]
    baseline = float(np.percentile(profile, 12))
    h = frame.shape[0]
    ys = np.arange(h)[:, None]
    dist = np.abs(ys - centre)
    outer = dist <= (profile[None, :] + 3.0)
    outside_bare_fibre = dist >= max(2.0, baseline + 1.5)
    mask = outer & outside_bare_fibre
    excess = np.maximum(profile - baseline, 0.0)
    characteristic_radius = max(float(np.percentile(excess, 95)), 8.0)
    return mask.astype(np.uint8), characteristic_radius


def affine_decomposition(
    previous: np.ndarray,
    current: np.ndarray,
    mask: np.ndarray,
    characteristic_radius: float,
) -> dict[str, float]:
    prev_gray = cv2.cvtColor(previous, cv2.COLOR_BGR2GRAY)
    curr_gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)
    prev_gray = cv2.GaussianBlur(prev_gray, (5, 5), 0)
    curr_gray = cv2.GaussianBlur(curr_gray, (5, 5), 0)

    flow = cv2.calcOpticalFlowFarneback(
        prev_gray,
        curr_gray,
        None,
        pyr_scale=0.5,
        levels=3,
        winsize=21,
        iterations=5,
        poly_n=7,
        poly_sigma=1.5,
        flags=0,
    )

    grad_x = cv2.Sobel(prev_gray, cv2.CV_32F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(prev_gray, cv2.CV_32F, 0, 1, ksize=3)
    texture = np.hypot(grad_x, grad_y)
    sample = np.zeros_like(mask, dtype=bool)
    sample[::4, ::4] = True
    valid = (mask > 0) & sample & (texture > np.percentile(texture[mask > 0], 35))
    yy, xx = np.nonzero(valid)
    if len(xx) < 40:
        valid = (mask > 0) & sample
        yy, xx = np.nonzero(valid)

    p = np.column_stack([xx, yy]).astype(np.float32)
    observed = flow[yy, xx].astype(np.float32)
    q = p + observed
    affine, inliers = cv2.estimateAffine2D(
        p,
        q,
        method=cv2.RANSAC,
        ransacReprojThreshold=1.5,
        maxIters=2000,
        confidence=0.99,
        refineIters=10,
    )
    if affine is None:
        translation = np.median(observed, axis=0)
        affine = np.array([[1.0, 0.0, translation[0]], [0.0, 1.0, translation[1]]])
        inlier_fraction = 0.0
    else:
        inlier_fraction = float(np.mean(inliers)) if inliers is not None else float("nan")

    predicted_q = np.column_stack(
        [
            affine[0, 0] * xx + affine[0, 1] * yy + affine[0, 2],
            affine[1, 0] * xx + affine[1, 1] * yy + affine[1, 2],
        ]
    )
    predicted = predicted_q - p
    residual = observed - predicted
    r_mag = np.linalg.norm(predicted, axis=1)
    i_mag = np.linalg.norm(residual, axis=1)
    obs_mag = np.linalg.norm(observed, axis=1)

    linear = affine[:, :2]
    area_scale = float(np.sqrt(max(abs(np.linalg.det(linear)), 1e-12)))
    signed_convergence = 1.0 - area_scale
    return {
        "r_raw": float(np.median(r_mag) / characteristic_radius),
        "i_raw": float(np.median(i_mag) / characteristic_radius),
        "observed_raw": float(np.median(obs_mag) / characteristic_radius),
        "signed_convergence": signed_convergence,
        "inlier_fraction": inlier_fraction,
        "valid_vectors": int(len(xx)),
        "characteristic_radius_px": characteristic_radius,
    }


def extract_event(event: Event) -> pd.DataFrame:
    cap = cv2.VideoCapture(str(VIDEO_DIR / event.video))
    frames: list[np.ndarray] = []
    for frame_index in range(event.start, event.end + 1):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok:
            raise RuntimeError(f"Could not decode {event.video} frame {frame_index}")
        frame = orient(frame, event)
        frames.append(frame[:, event.x0 : event.x1])
    cap.release()

    # Re-read the event start to define one fixed mask and physical length scale.
    cap = cv2.VideoCapture(str(VIDEO_DIR / event.video))
    cap.set(cv2.CAP_PROP_POS_FRAMES, event.start)
    ok, start_full = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError(f"Could not decode start frame for {event.event_id}")
    start_full = orient(start_full, event)
    mask, radius = droplet_mask(start_full, event.x0, event.x1)

    rows: list[dict[str, object]] = []
    for offset in range(1, len(frames)):
        frame_index = event.start + offset
        values = affine_decomposition(frames[offset - 1], frames[offset], mask, radius)
        rows.append(
            {
                "event_id": event.event_id,
                "video": event.video,
                "split": event.split,
                "frame": frame_index,
                "u_event": (frame_index - event.start) / (event.target - event.start),
                "direct_handover_frame": event.target,
                **values,
            }
        )
    return pd.DataFrame(rows)


def causal_ema(values: np.ndarray, alpha: float = 0.25) -> np.ndarray:
    out = np.empty_like(values, dtype=float)
    out[0] = values[0]
    for i in range(1, len(values)):
        out[i] = alpha * values[i] + (1.0 - alpha) * out[i - 1]
    return out


def robust_scale(values: np.ndarray) -> tuple[float, float]:
    logged = np.log1p(values)
    return float(np.quantile(logged, 0.05)), float(np.quantile(logged, 0.95))


def ara_map(values: np.ndarray, low: float, high: float) -> np.ndarray:
    logged = np.log1p(values)
    denom = max(high - low, 1e-12)
    return 2.0 * np.clip((logged - low) / denom, 0.0, 1.0)


def crossings(u: np.ndarray, r: np.ndarray, i: np.ndarray) -> np.ndarray:
    d = r - i
    xs: list[float] = []
    for k in range(len(d) - 1):
        if d[k] == 0:
            xs.append(float(u[k]))
        elif d[k] * d[k + 1] < 0:
            frac = abs(d[k]) / (abs(d[k]) + abs(d[k + 1]))
            xs.append(float(u[k] + frac * (u[k + 1] - u[k])))
    return np.asarray(xs, dtype=float)


def nearest_crossing_error(u: np.ndarray, r: np.ndarray, i: np.ndarray) -> tuple[float, float, int]:
    keep = (u >= 0.20) & (u <= 1.35)
    xs = crossings(u[keep], r[keep], i[keep])
    if not len(xs):
        return float("nan"), float("inf"), 0
    index = int(np.argmin(np.abs(xs - 1.0)))
    return float(xs[index]), float(abs(xs[index] - 1.0)), int(len(xs))


def score_event(group: pd.DataFrame) -> dict[str, object]:
    u = group["u_event"].to_numpy(float)
    r = group["x_r"].to_numpy(float)
    i = group["x_i"].to_numpy(float)
    x_cross, error, count = nearest_crossing_error(u, r, i)
    keep = (u >= 0.20) & (u <= 1.35)
    d1 = np.hypot(r - 1.0, i - 1.0)
    kept_indices = np.flatnonzero(keep)
    ridge_local = kept_indices[int(np.argmin(d1[keep]))]
    grad_r = np.gradient(r, u)
    grad_i = np.gradient(i, u)
    cross_idx = int(np.argmin(abs(u - x_cross))) if np.isfinite(x_cross) else -1
    return {
        "event_id": group["event_id"].iloc[0],
        "video": group["video"].iloc[0],
        "split": group["split"].iloc[0],
        "selected_crossing_u": x_cross,
        "crossing_error_abs_u": error,
        "candidate_crossing_count": count,
        "joint_ridge_min_u": float(u[ridge_local]),
        "joint_ridge_min_distance": float(d1[ridge_local]),
        "r_slope_at_crossing": float(grad_r[cross_idx]) if cross_idx >= 0 else float("nan"),
        "i_slope_at_crossing": float(grad_i[cross_idx]) if cross_idx >= 0 else float("nan"),
        "locking_orientation": bool(grad_r[cross_idx] > 0 and grad_i[cross_idx] < 0) if cross_idx >= 0 else False,
    }


def circular_shift_control(holdout_groups: list[pd.DataFrame], draws: int = 10_000) -> np.ndarray:
    medians = np.empty(draws, dtype=float)
    for draw in range(draws):
        errors: list[float] = []
        for group in holdout_groups:
            u = group["u_event"].to_numpy(float)
            r = group["x_r"].to_numpy(float)
            i = group["x_i"].to_numpy(float)
            shift = int(RNG.integers(1, len(i)))
            _, error, _ = nearest_crossing_error(u, r, np.roll(i, shift))
            errors.append(error)
        finite = [x for x in errors if np.isfinite(x)]
        medians[draw] = float(np.median(finite)) if finite else float("inf")
    return medians


def event_pair_shuffle(holdout_groups: list[pd.DataFrame]) -> list[dict[str, object]]:
    grid = np.linspace(0.20, 1.35, 500)
    records: list[dict[str, object]] = []
    n = len(holdout_groups)
    for perm in permutations(range(n)):
        if any(i == perm[i] for i in range(n)):
            continue
        errors: list[float] = []
        for i, j in enumerate(perm):
            left = holdout_groups[i]
            right = holdout_groups[j]
            r = np.interp(grid, left["u_event"], left["x_r"])
            irr = np.interp(grid, right["u_event"], right["x_i"])
            _, error, _ = nearest_crossing_error(grid, r, irr)
            errors.append(error)
        records.append(
            {
                "permutation": "-".join(str(x) for x in perm),
                "median_crossing_error_abs_u": float(np.median(errors)),
            }
        )
    return records


def make_figures(frame_df: pd.DataFrame, event_df: pd.DataFrame, controls: np.ndarray) -> None:
    colors = {"r": "#e98b2a", "i": "#7652c7"}
    fig, axes = plt.subplots(4, 2, figsize=(16, 17), sharey=True)
    for ax, event in zip(axes.flat, EVENTS):
        group = frame_df[frame_df["event_id"] == event.event_id]
        result = event_df[event_df["event_id"] == event.event_id].iloc[0]
        ax.plot(group["u_event"], group["x_r"], color=colors["r"], lw=2.0, label="Rationality R: coherent affine flow")
        ax.plot(group["u_event"], group["x_i"], color=colors["i"], lw=2.0, label="Irrationality I: non-affine residual")
        ax.axhline(1.0, color="#4c956c", lw=1.2, ls="--", label="ARA ridge = 1")
        ax.axvline(1.0, color="#111111", lw=1.5, label="direct droplet handover")
        if np.isfinite(result["selected_crossing_u"]):
            ax.axvline(result["selected_crossing_u"], color="#d14b4b", ls=":", lw=1.8, label="selected R=I crossing")
        ax.set_xlim(0, max(1.40, float(group["u_event"].max())))
        ax.set_ylim(-0.05, 2.05)
        crossing_label = (
            f"crossing error |Δu|={result['crossing_error_abs_u']:.3f}"
            if np.isfinite(result["crossing_error_abs_u"])
            else "no R=I crossing in frozen window"
        )
        ax.set_title(f"{event.event_id} · {event.video} · {event.split}\n{crossing_label}")
        ax.set_xlabel("event position u (direct handover = 1.0)")
        ax.set_ylabel("independent ARA participation (0–2)")
        ax.grid(alpha=0.25)
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.subplots_adjust(top=0.90, hspace=0.48, wspace=0.16)
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.955), ncol=4, frameon=False)
    fig.suptitle(
        "T409 combined Rationality/Irrationality Di-ARA — all registered droplet handovers",
        fontsize=18,
        y=0.995,
    )
    fig.savefig(OUT_DIR / "T409_ALL_EVENT_WAVES.png", dpi=170)
    plt.close(fig)

    hold = event_df[event_df["split"] == "holdout"].copy()
    observed = float(hold["crossing_error_abs_u"].median())
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5), constrained_layout=True)
    finite_errors = hold["crossing_error_abs_u"].replace([np.inf, -np.inf], np.nan)
    axes[0].bar(hold["event_id"], finite_errors.fillna(0.0), color="#5a80b8")
    for event_id, error in zip(hold["event_id"], hold["crossing_error_abs_u"]):
        if not np.isfinite(error):
            axes[0].text(
                event_id,
                0.02,
                "NO\nCROSSING",
                ha="center",
                va="bottom",
                color="#d14b4b",
                weight="bold",
            )
    axes[0].axhline(0.15, color="#d14b4b", ls="--", label="frozen per-event tolerance 0.15")
    axes[0].set(
        title="Held-out crossing timing error",
        xlabel="held-out droplet handover",
        ylabel="absolute event-position error |u_cross − 1|",
    )
    axes[0].legend(frameon=False)
    axes[0].grid(axis="y", alpha=0.25)

    finite_controls = controls[np.isfinite(controls)]
    axes[1].hist(finite_controls, bins=50, color="#b4bcc8", edgecolor="white")
    if np.isfinite(observed):
        axes[1].axvline(observed, color="#d14b4b", lw=2.2, label=f"observed holdout median = {observed:.3f}")
    else:
        axes[1].text(
            0.98,
            0.93,
            "Observed median = ∞\n(two holdouts had no crossing)",
            transform=axes[1].transAxes,
            ha="right",
            va="top",
            color="#d14b4b",
            fontsize=11,
            weight="bold",
        )
    axes[1].axvline(np.median(finite_controls), color="#222222", ls="--", label=f"shift median = {np.median(finite_controls):.3f}")
    axes[1].set(
        title="10,000 autocorrelation-preserving circular shifts",
        xlabel="median held-out crossing error |Δu|",
        ylabel="control draws",
    )
    axes[1].legend(frameon=False)
    axes[1].grid(axis="y", alpha=0.2)
    fig.suptitle("T409 frozen holdout gate", fontsize=17)
    fig.savefig(OUT_DIR / "T409_HOLDOUT_CONTROL.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 6), constrained_layout=True)
    for event in EVENTS:
        group = frame_df[frame_df["event_id"] == event.event_id]
        ax.plot(group["x_r"], group["x_i"], lw=1.8, alpha=0.85, label=event.event_id)
        nearest = int(np.argmin(abs(group["u_event"].to_numpy() - 1.0)))
        ax.scatter(group["x_r"].iloc[nearest], group["x_i"].iloc[nearest], s=48, edgecolor="black", zorder=4)
    ax.axvline(1.0, color="#4c956c", ls="--")
    ax.axhline(1.0, color="#4c956c", ls="--")
    ax.plot([0, 2], [0, 2], color="#d14b4b", ls=":", label="R = I")
    ax.set(
        title="Combined Di-ARA relation plane (black-edged points are direct handovers)",
        xlabel="Rationality R — coherent affine flow (ARA 0–2)",
        ylabel="Irrationality I — non-affine residual (ARA 0–2)",
        xlim=(-0.05, 2.05),
        ylim=(-0.05, 2.05),
    )
    ax.grid(alpha=0.25)
    ax.legend(ncol=3, frameon=False)
    fig.savefig(OUT_DIR / "T409_COMBINED_RELATION_PLANE.png", dpi=180)
    plt.close(fig)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw_cache = OUT_DIR / "T409_RAW_FEATURES.csv"
    existing_frame_file = OUT_DIR / "T409_FRAME_WAVES.csv"
    if raw_cache.exists():
        frame_df = pd.read_csv(raw_cache)
    elif existing_frame_file.exists():
        columns = [
            "event_id",
            "video",
            "split",
            "frame",
            "u_event",
            "direct_handover_frame",
            "r_raw",
            "i_raw",
            "observed_raw",
            "signed_convergence",
            "inlier_fraction",
            "valid_vectors",
            "characteristic_radius_px",
        ]
        frame_df = pd.read_csv(existing_frame_file)[columns]
        frame_df.to_csv(raw_cache, index=False)
    else:
        parts = [extract_event(event) for event in EVENTS]
        frame_df = pd.concat(parts, ignore_index=True)
        frame_df.to_csv(raw_cache, index=False)

    development = frame_df[frame_df["split"] == "development"]
    r_low, r_high = robust_scale(development["r_raw"].to_numpy(float))
    i_low, i_high = robust_scale(development["i_raw"].to_numpy(float))
    frame_df["x_r_unsmoothed"] = ara_map(frame_df["r_raw"].to_numpy(float), r_low, r_high)
    frame_df["x_i_unsmoothed"] = ara_map(frame_df["i_raw"].to_numpy(float), i_low, i_high)

    smoothed: list[pd.DataFrame] = []
    for event in EVENTS:
        group = frame_df[frame_df["event_id"] == event.event_id].copy()
        group["x_r"] = causal_ema(group["x_r_unsmoothed"].to_numpy(float))
        group["x_i"] = causal_ema(group["x_i_unsmoothed"].to_numpy(float))
        smoothed.append(group)
    frame_df = pd.concat(smoothed, ignore_index=True)

    event_records = [score_event(frame_df[frame_df["event_id"] == event.event_id]) for event in EVENTS]
    event_df = pd.DataFrame(event_records)
    holdout_groups = [frame_df[frame_df["event_id"] == e.event_id] for e in EVENTS if e.split == "holdout"]
    controls = circular_shift_control(holdout_groups)
    pair_shuffle = event_pair_shuffle(holdout_groups)

    hold = event_df[event_df["split"] == "holdout"]
    missing_crossings = int(np.sum(~np.isfinite(hold["crossing_error_abs_u"])))
    finite_observed = hold.loc[np.isfinite(hold["crossing_error_abs_u"]), "crossing_error_abs_u"]
    observed_finite_median = float(finite_observed.median()) if len(finite_observed) else None
    observed_median = float(hold["crossing_error_abs_u"].median())
    control_finite = controls[np.isfinite(controls)]
    control_median = float(np.median(control_finite))
    empirical_p = float((1 + np.sum(control_finite <= observed_median)) / (1 + len(control_finite)))
    improvement = float(1.0 - observed_median / control_median) if control_median else float("nan")
    per_event_passes = int(np.sum(hold["crossing_error_abs_u"] <= 0.15))
    gate_pass = bool(per_event_passes >= 3 and improvement >= 0.25 and empirical_p < 0.05)

    results = {
        "test": "T409 combined Rationality/Irrationality Di-ARA at droplet handover",
        "protocol_sha256": "A3899462E5DFF426A0CA10A5418A7AAB4194093301BE3C66162C9B06B77E7A65",
        "development_events": [e.event_id for e in EVENTS if e.split == "development"],
        "holdout_events": [e.event_id for e in EVENTS if e.split == "holdout"],
        "scaling": {
            "r_log1p_q05": r_low,
            "r_log1p_q95": r_high,
            "i_log1p_q05": i_low,
            "i_log1p_q95": i_high,
        },
        "primary_holdout": {
            "events_with_error_le_0_15": per_event_passes,
            "required_events": 3,
            "missing_crossing_events": missing_crossings,
            "observed_median_error_abs_u": None if not np.isfinite(observed_median) else observed_median,
            "observed_finite_only_median_error_abs_u": observed_finite_median,
            "circular_shift_median_error_abs_u": control_median,
            "improvement_fraction": None if not np.isfinite(improvement) else improvement,
            "empirical_p": empirical_p,
            "frozen_gate_pass": gate_pass,
        },
        "limitations": [
            "The fibre is pre-wetted; the direct target is persistent lobe merger, not first molecular bridge.",
            "Four holdout events are a small exploratory sample.",
            "No near-miss footage is available.",
            "The closest-crossing endpoint is diagnostic and not a deployable forecaster.",
        ],
    }

    frame_df.to_csv(OUT_DIR / "T409_FRAME_WAVES.csv", index=False)
    event_df.to_csv(OUT_DIR / "T409_EVENT_SUMMARY.csv", index=False)
    pd.DataFrame({"circular_shift_median_error_abs_u": controls}).to_csv(
        OUT_DIR / "T409_CIRCULAR_SHIFT_CONTROLS.csv", index=False
    )
    pd.DataFrame(pair_shuffle).to_csv(OUT_DIR / "T409_EVENT_PAIR_SHUFFLES.csv", index=False)
    with (OUT_DIR / "T409_RESULTS.json").open("w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)

    make_figures(frame_df, event_df, controls)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
