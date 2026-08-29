"""Pre-score geometric extraction QA for T409 fibre coalescence events.

The script extracts the droplet/fibre silhouette envelope and counts persistent
lobes.  It is used only to register the independent physical handover target
(two lobes becoming one).  It does not calculate optical flow, ARA waves,
crossings, controls, or a test verdict.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter1d, median_filter
from scipy.signal import find_peaks


HERE = Path(__file__).resolve().parent
VIDEO_DIR = HERE / "source_videos"
OUT_DIR = HERE / "geometry_qa"


@dataclass(frozen=True)
class Config:
    name: str
    rotate_clockwise: bool = False
    min_prominence_px: float = 9.0
    min_distance_px: int = 70


CONFIGS = (
    Config("Video_S2.mp4", min_prominence_px=8.0, min_distance_px=90),
    Config("Video_S3.mp4", min_prominence_px=8.0, min_distance_px=90),
    Config("Video_S4.mp4", rotate_clockwise=True, min_prominence_px=7.0, min_distance_px=65),
    Config("Video_S5.mp4", min_prominence_px=8.0, min_distance_px=90),
    Config("Video_S6.mp4", min_prominence_px=10.0, min_distance_px=110),
    Config("Video_S7.mp4", min_prominence_px=10.0, min_distance_px=110),
)


def orient(frame: np.ndarray, cfg: Config) -> np.ndarray:
    if cfg.rotate_clockwise:
        return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    return frame


def silhouette_profile(frame: np.ndarray) -> tuple[np.ndarray, int, float]:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(float)
    h, w = gray.shape
    # The pre-wetted fibre is the darkest long horizontal structure.
    row_darkness = np.mean(gray[:, int(0.08 * w) : int(0.92 * w)], axis=1)
    centre = int(np.argmin(gaussian_filter1d(row_darkness, 2.0)))

    border = np.concatenate(
        [
            gray[: max(8, h // 12), : w // 2].ravel(),
            gray[-max(8, h // 12) :, : w // 2].ravel(),
        ]
    )
    background = float(np.median(border))
    dark_threshold = background - 32.0

    y0 = max(0, centre - int(0.42 * h))
    y1 = min(h, centre + int(0.42 * h) + 1)
    local = gray[y0:y1]
    ys = np.arange(y0, y1)[:, None]
    dark = local < dark_threshold
    distances = np.where(dark, np.abs(ys - centre), -1.0)
    half_height = np.max(distances, axis=0)
    half_height = np.maximum(half_height, 0.0)
    half_height = median_filter(half_height, size=5, mode="nearest")
    half_height = gaussian_filter1d(half_height, 4.0)
    return half_height, centre, background


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary_rows: list[dict[str, object]] = []

    for cfg in CONFIGS:
        path = VIDEO_DIR / cfg.name
        cap = cv2.VideoCapture(str(path))
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        profiles: list[np.ndarray] = []
        peak_counts: list[int] = []
        centres: list[int] = []
        peak_positions: list[np.ndarray] = []

        for frame_index in range(frame_count):
            ok, frame = cap.read()
            if not ok:
                raise RuntimeError(f"Could not decode {cfg.name} frame {frame_index}")
            frame = orient(frame, cfg)
            profile, centre, _ = silhouette_profile(frame)
            baseline = float(np.percentile(profile, 12))
            excess = np.maximum(profile - baseline, 0.0)
            peaks, _ = find_peaks(
                excess,
                prominence=cfg.min_prominence_px,
                distance=cfg.min_distance_px,
            )
            profiles.append(excess)
            peak_counts.append(len(peaks))
            centres.append(centre)
            peak_positions.append(peaks)

        cap.release()
        profile_arr = np.vstack(profiles)
        counts = median_filter(np.asarray(peak_counts, dtype=float), size=5, mode="nearest")

        # Candidate handovers are persistent decreases in the lobe count.
        candidates: list[int] = []
        persistence = 8
        for i in range(1, frame_count - persistence):
            before = int(round(np.median(counts[max(0, i - persistence) : i])))
            after = int(round(np.median(counts[i : i + persistence])))
            if before > after and (not candidates or i - candidates[-1] > persistence):
                candidates.append(i)

        for order, frame_index in enumerate(candidates, start=1):
            summary_rows.append(
                {
                    "video": cfg.name,
                    "candidate_order": order,
                    "candidate_frame": frame_index,
                    "playback_time_s": frame_index / fps,
                    "count_before": int(round(np.median(counts[max(0, frame_index - persistence) : frame_index]))),
                    "count_after": int(round(np.median(counts[frame_index : frame_index + persistence]))),
                    "status": "QA candidate only",
                }
            )

        fig, axes = plt.subplots(2, 1, figsize=(15, 9), constrained_layout=True)
        x = np.arange(frame_count)
        axes[0].plot(x, counts, color="#1f77b4", lw=1.8)
        for c in candidates:
            axes[0].axvline(c, color="#d62728", ls="--", alpha=0.75)
        axes[0].set(
            title=f"{cfg.name}: independent silhouette lobe count (pre-score QA)",
            xlabel="encoded video frame",
            ylabel="persistent lobe count",
        )
        axes[0].grid(alpha=0.25)

        image = axes[1].imshow(
            profile_arr.T,
            aspect="auto",
            origin="lower",
            cmap="magma",
            interpolation="nearest",
        )
        for c in candidates:
            axes[1].axvline(c, color="cyan", ls="--", alpha=0.8)
        axes[1].set(
            title="Silhouette height above the pre-wetted fibre baseline",
            xlabel="encoded video frame",
            ylabel="position along fibre (pixels)",
        )
        fig.colorbar(image, ax=axes[1], label="half-height excess (pixels)")
        fig.savefig(OUT_DIR / f"{Path(cfg.name).stem}_GEOMETRY_QA.png", dpi=160)
        plt.close(fig)

    fields = [
        "video",
        "candidate_order",
        "candidate_frame",
        "playback_time_s",
        "count_before",
        "count_after",
        "status",
    ]
    with (OUT_DIR / "T409_GEOMETRY_QA_CANDIDATES.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(summary_rows)


if __name__ == "__main__":
    main()
