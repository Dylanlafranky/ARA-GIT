"""T410 geometric Irrationality Di-ARA on registered water-droplet handovers.

The development pass extracts only E1/E2/E5/E7.  Holdout extraction and
scoring are disabled until a development signature has been registered in the
frozen protocol.  The geometric instrument is the polar decomposition of the
same robust affine optical-flow fit used by T409:

    q_t = s_t exp(i dtheta_t)

The cumulative relation to the event start is then mapped to exact ARA cuts

    X = 2 s / (1 + s),       Y = 1 + theta / pi.

No Phi/e landmark is fitted or forced.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter1d, median_filter


HERE = Path(__file__).resolve().parent
T409 = HERE.parent / "T409_combined_handover_droplets"
VIDEO_DIR = T409 / "source_videos"
OUT_DIR = HERE / "results"


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


def silhouette(frame: np.ndarray) -> tuple[np.ndarray, int]:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(float)
    h, w = gray.shape
    row_darkness = np.mean(gray[:, int(0.08 * w) : int(0.92 * w)], axis=1)
    centre = int(np.argmin(gaussian_filter1d(row_darkness, 2.0)))
    border_h = max(8, h // 12)
    border = np.concatenate(
        [gray[:border_h, : w // 2].ravel(), gray[-border_h:, : w // 2].ravel()]
    )
    threshold = float(np.median(border)) - 32.0
    y0 = max(0, centre - int(0.42 * h))
    y1 = min(h, centre + int(0.42 * h) + 1)
    local = gray[y0:y1]
    ys = np.arange(y0, y1)[:, None]
    distances = np.where(local < threshold, np.abs(ys - centre), -1.0)
    half_height = np.maximum(np.max(distances, axis=0), 0.0)
    half_height = median_filter(half_height, size=5, mode="nearest")
    return gaussian_filter1d(half_height, 4.0), centre


def droplet_mask(frame: np.ndarray, x0: int, x1: int) -> np.ndarray:
    profile, centre = silhouette(frame)
    profile = profile[x0:x1]
    baseline = float(np.percentile(profile, 12))
    ys = np.arange(frame.shape[0])[:, None]
    distance = np.abs(ys - centre)
    outer = distance <= (profile[None, :] + 3.0)
    outside_fibre = distance >= max(2.0, baseline + 1.5)
    return (outer & outside_fibre).astype(np.uint8)


def robust_affine_linear(
    previous: np.ndarray, current: np.ndarray, mask: np.ndarray
) -> tuple[np.ndarray, float, int]:
    prev = cv2.GaussianBlur(cv2.cvtColor(previous, cv2.COLOR_BGR2GRAY), (5, 5), 0)
    curr = cv2.GaussianBlur(cv2.cvtColor(current, cv2.COLOR_BGR2GRAY), (5, 5), 0)
    flow = cv2.calcOpticalFlowFarneback(
        prev, curr, None, 0.5, 3, 21, 5, 7, 1.5, 0
    )
    gx = cv2.Sobel(prev, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(prev, cv2.CV_32F, 0, 1, ksize=3)
    texture = np.hypot(gx, gy)
    sample = np.zeros_like(mask, dtype=bool)
    sample[::4, ::4] = True
    masked_texture = texture[mask > 0]
    threshold = np.percentile(masked_texture, 35) if len(masked_texture) else 0.0
    valid = (mask > 0) & sample & (texture > threshold)
    yy, xx = np.nonzero(valid)
    if len(xx) < 40:
        yy, xx = np.nonzero((mask > 0) & sample)
    p = np.column_stack([xx, yy]).astype(np.float32)
    q = p + flow[yy, xx].astype(np.float32)
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
        return np.eye(2), 0.0, int(len(xx))
    inlier_fraction = float(np.mean(inliers)) if inliers is not None else np.nan
    return affine[:, :2].astype(float), inlier_fraction, int(len(xx))


def proper_polar(linear: np.ndarray) -> tuple[float, float, float]:
    """Return isotropic scale, proper-rotation angle and anisotropy diagnostic."""
    u, singular, vt = np.linalg.svd(linear)
    rotation = u @ vt
    if np.linalg.det(rotation) < 0:
        u[:, -1] *= -1
        singular[-1] *= -1
        rotation = u @ vt
    determinant = float(np.linalg.det(linear))
    scale = float(np.sqrt(max(abs(determinant), 1e-12)))
    angle = float(np.arctan2(rotation[1, 0], rotation[0, 0]))
    positive = np.abs(singular)
    anisotropy = float(abs(np.log(max(positive[0], 1e-12) / max(positive[-1], 1e-12))))
    return scale, angle, anisotropy


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

    cap = cv2.VideoCapture(str(VIDEO_DIR / event.video))
    cap.set(cv2.CAP_PROP_POS_FRAMES, event.start)
    ok, start_full = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError(f"Could not decode start frame for {event.event_id}")
    start_full = orient(start_full, event)
    mask = droplet_mask(start_full, event.x0, event.x1)

    rows: list[dict[str, object]] = []
    cumulative_log_scale = 0.0
    cumulative_angle = 0.0
    for offset in range(1, len(frames)):
        frame_index = event.start + offset
        linear, inlier_fraction, valid_vectors = robust_affine_linear(
            frames[offset - 1], frames[offset], mask
        )
        scale, angle, anisotropy = proper_polar(linear)
        log_scale = float(np.log(scale))
        cumulative_log_scale += log_scale
        cumulative_angle += angle
        cumulative_scale = float(np.exp(np.clip(cumulative_log_scale, -20, 20)))
        x_radial = 2.0 * cumulative_scale / (1.0 + cumulative_scale)
        y_angular = 1.0 + np.arctan2(
            np.sin(cumulative_angle), np.cos(cumulative_angle)
        ) / np.pi
        rows.append(
            {
                "event_id": event.event_id,
                "video": event.video,
                "split": event.split,
                "frame": frame_index,
                "u_event": (frame_index - event.start) / (event.target - event.start),
                "direct_handover_frame": event.target,
                "step_scale": scale,
                "step_log_scale": log_scale,
                "step_angle_rad": angle,
                "step_turn_fraction": angle / (2.0 * np.pi),
                "cumulative_log_scale": cumulative_log_scale,
                "cumulative_angle_rad": cumulative_angle,
                "x_radial_ara": x_radial,
                "y_angular_ara": y_angular,
                "mixing_angle_deg": np.degrees(
                    np.arctan2(abs(y_angular - 1.0), abs(x_radial - 1.0) + 1e-15)
                ),
                "anisotropy_log_ratio": anisotropy,
                "inlier_fraction": inlier_fraction,
                "valid_vectors": valid_vectors,
            }
        )
    return pd.DataFrame(rows)


def geometry_figure(data: pd.DataFrame, filename: str, title: str) -> None:
    events = sorted(data.event_id.unique())
    fig, axes = plt.subplots(len(events), 3, figsize=(15, 3.4 * len(events)), constrained_layout=True)
    if len(events) == 1:
        axes = np.asarray([axes])
    for row, event_id in enumerate(events):
        g = data[data.event_id == event_id]
        axes[row, 0].plot(g.x_radial_ara, g.y_angular_ara, color="#3569b0", lw=1.8)
        target_i = int(np.argmin(np.abs(g.u_event.to_numpy() - 1.0)))
        axes[row, 0].scatter(
            [g.x_radial_ara.iloc[target_i]], [g.y_angular_ara.iloc[target_i]],
            s=75, color="#e45756", edgecolor="white", zorder=4, label="direct handover"
        )
        axes[row, 0].axvline(1, color="#555", lw=1)
        axes[row, 0].axhline(1, color="#555", lw=1)
        axes[row, 0].set(
            title=f"{event_id}: geometric Di-ARA trajectory",
            xlabel="radial/diameter ARA X (0 contraction, 1 ridge, 2 expansion)",
            ylabel="angular/circumference ARA Y (0 reverse, 1 ridge, 2 forward)",
        )
        axes[row, 0].legend(loc="best", fontsize=8)

        axes[row, 1].plot(g.u_event, g.x_radial_ara, label="radial X", color="#2ca02c")
        axes[row, 1].plot(g.u_event, g.y_angular_ara, label="angular Y", color="#9467bd")
        axes[row, 1].axvline(1, color="#e45756", ls="--", label="direct handover u=1")
        axes[row, 1].axhline(1, color="#555", lw=1)
        axes[row, 1].set(
            title="ARA coordinates through event time",
            xlabel="normalised event position u",
            ylabel="ARA coordinate (0–2)",
        )
        axes[row, 1].legend(loc="best", fontsize=8)

        axes[row, 2].plot(g.u_event, g.mixing_angle_deg, color="#f28e2b")
        axes[row, 2].axhline(15, color="#4e79a7", ls=":", label="line cone edge 15°")
        axes[row, 2].axhline(75, color="#af7aa1", ls=":", label="circle cone edge 75°")
        axes[row, 2].axvline(1, color="#e45756", ls="--", label="handover")
        axes[row, 2].set(
            title="Line ↔ circle mixing",
            xlabel="normalised event position u",
            ylabel="mixing angle γ (degrees; 0 line, 90 circle)",
            ylim=(-2, 92),
        )
        axes[row, 2].legend(loc="best", fontsize=8)
        for ax in axes[row]:
            ax.grid(alpha=0.22)
    fig.suptitle(title, fontsize=16)
    fig.savefig(OUT_DIR / filename, dpi=170)
    plt.close(fig)


def target_rows(data: pd.DataFrame) -> pd.DataFrame:
    rows: list[pd.Series] = []
    for _, group in data.groupby("event_id", sort=True):
        rows.append(group.iloc[int(np.argmin(np.abs(group.u_event.to_numpy() - 1.0)))])
    result = pd.DataFrame(rows).reset_index(drop=True)
    result["hit_20deg"] = (
        (result.x_radial_ara < 1.0) & (result.mixing_angle_deg <= 20.0)
    )
    for cone in (15.0, 25.0):
        result[f"hit_{int(cone)}deg"] = (
            (result.x_radial_ara < 1.0) & (result.mixing_angle_deg <= cone)
        )
    transition_rows = []
    for event_id, group in data.groupby("event_id", sort=True):
        pre = group[(group.u_event >= 0.70) & (group.u_event < 1.00)]
        post = group[(group.u_event > 1.00) & (group.u_event <= 1.30)]
        transition_rows.append(
            {
                "event_id": event_id,
                "gamma_pre_median": float(pre.mixing_angle_deg.median()),
                "gamma_post_median": float(post.mixing_angle_deg.median()),
                "became_more_line_like": bool(
                    post.mixing_angle_deg.median() < pre.mixing_angle_deg.median()
                ),
            }
        )
    return result.merge(pd.DataFrame(transition_rows), on="event_id", how="left")


def circular_shift_control(
    data: pd.DataFrame, observed_hits: int, n_rep: int = 10_000
) -> tuple[np.ndarray, float]:
    rng = np.random.default_rng(4102026)
    candidate_hits: list[np.ndarray] = []
    for _, group in data.groupby("event_id", sort=True):
        window = group[(group.u_event >= 0.20) & (group.u_event <= 1.35)]
        hits = (
            (window.x_radial_ara.to_numpy() < 1.0)
            & (window.mixing_angle_deg.to_numpy() <= 20.0)
        ).astype(int)
        if len(hits) == 0:
            raise RuntimeError("Empty registered shift-control window")
        candidate_hits.append(hits)
    null = np.zeros(n_rep, dtype=int)
    for i in range(n_rep):
        null[i] = sum(int(hits[rng.integers(0, len(hits))]) for hits in candidate_hits)
    p_value = float((1 + np.count_nonzero(null >= observed_hits)) / (n_rep + 1))
    return null, p_value


def gate_figure(summary: pd.DataFrame, null: np.ndarray, observed_hits: int) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2), constrained_layout=True)
    x = np.arange(0, 5)
    counts = np.bincount(null, minlength=5)
    axes[0].bar(x, counts, color="#9ecae1", edgecolor="#3569b0")
    axes[0].axvline(observed_hits, color="#e45756", lw=2.4, label=f"observed = {observed_hits}/4")
    axes[0].set(
        title="Within-event target-shift control (10,000 draws)",
        xlabel="line-contraction hits among four holdouts",
        ylabel="control draws (count)",
        xticks=x,
    )
    axes[0].legend()
    axes[0].grid(axis="y", alpha=0.22)

    colors = np.where(summary.hit_20deg, "#59a14f", "#e15759")
    axes[1].bar(summary.event_id, summary.mixing_angle_deg, color=colors)
    axes[1].axhline(20, color="#f28e2b", ls="--", lw=2, label="frozen line cone 20°")
    for i, row in summary.reset_index(drop=True).iterrows():
        axes[1].text(
            i,
            row.mixing_angle_deg + 1.2,
            f"X={row.x_radial_ara:.4f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    axes[1].set(
        title="Direct handover address by held-out event",
        xlabel="held-out droplet handover",
        ylabel="mixing angle γ (degrees; 0 line, 90 circle)",
        ylim=(0, max(30, float(summary.mixing_angle_deg.max()) + 8)),
    )
    axes[1].legend()
    axes[1].grid(axis="y", alpha=0.22)
    fig.suptitle("T410 frozen geometric Irrationality Di-ARA holdout gate", fontsize=15)
    fig.savefig(OUT_DIR / "T410_HOLDOUT_GATE.png", dpi=180)
    plt.close(fig)


def score_holdout(data: pd.DataFrame) -> dict[str, object]:
    summary = target_rows(data)
    observed_hits = int(summary.hit_20deg.sum())
    median_gamma = float(summary.mixing_angle_deg.median())
    null, p_value = circular_shift_control(data, observed_hits)
    pass_count = observed_hits >= 3
    pass_median = median_gamma <= 20.0
    pass_shift = p_value < 0.05
    summary.to_csv(OUT_DIR / "T410_HOLDOUT_EVENT_SUMMARY.csv", index=False)
    pd.DataFrame({"shift_hit_count": null}).to_csv(
        OUT_DIR / "T410_HOLDOUT_SHIFT_CONTROL.csv", index=False
    )
    gate_figure(summary, null, observed_hits)
    result = {
        "protocol_sha256": "E9C820A2684680A80C4615FB97EAED626C116E7327F73A7DD7FEC07B054133D0",
        "n_holdout": int(len(summary)),
        "observed_hits_20deg": observed_hits,
        "median_target_gamma_deg": median_gamma,
        "circular_shift_p": p_value,
        "gate_count_pass": bool(pass_count),
        "gate_median_pass": bool(pass_median),
        "gate_shift_pass": bool(pass_shift),
        "primary_supported": bool(pass_count and pass_median and pass_shift),
        "sensitivity_hits_15deg": int(summary.hit_15deg.sum()),
        "sensitivity_hits_25deg": int(summary.hit_25deg.sum()),
        "secondary_more_line_like_count": int(summary.became_more_line_like.sum()),
        "events": summary[
            [
                "event_id", "x_radial_ara", "y_angular_ara", "mixing_angle_deg",
                "hit_20deg", "gamma_pre_median", "gamma_post_median",
                "became_more_line_like", "inlier_fraction", "valid_vectors",
                "anisotropy_log_ratio",
            ]
        ].to_dict(orient="records"),
    }
    (OUT_DIR / "T410_RESULTS.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode", choices=("development", "holdout"), default="development",
        help="Holdout mode is enabled only after T410_FROZEN_PROTOCOL.md was hashed.",
    )
    args = parser.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frames = [extract_event(e) for e in EVENTS if e.split == args.mode]
    data = pd.concat(frames, ignore_index=True)
    if args.mode == "development":
        data.to_csv(OUT_DIR / "T410_DEVELOPMENT_GEOMETRY.csv", index=False)
        geometry_figure(
            data,
            "T410_DEVELOPMENT_GEOMETRY.png",
            "T410 development-only geometric Irrationality Di-ARA — water droplets",
        )
        print(target_rows(data)[
            ["event_id", "x_radial_ara", "y_angular_ara", "mixing_angle_deg"]
        ].to_string(index=False))
    else:
        data.to_csv(OUT_DIR / "T410_HOLDOUT_GEOMETRY.csv", index=False)
        geometry_figure(
            data,
            "T410_HOLDOUT_GEOMETRY.png",
            "T410 held-out geometric Irrationality Di-ARA — water droplets",
        )
        result = score_holdout(data)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
