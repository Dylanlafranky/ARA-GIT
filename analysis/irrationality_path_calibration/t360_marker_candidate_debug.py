"""Inspect compact low-chroma bright components in the T360 public video."""

from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent
VIDEO = HERE / "T360_SOURCE_GEORGIA_TECH_MAGNETIC_PLINKO_EXPERIMENT.mp4"
RUN_RANGES = [(0, 22), (26, 44), (45, 67), (69, 101), (103, 122)]


def candidates(frame: np.ndarray) -> list[tuple[float, float, int, int, int, float]]:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mask = ((gray >= 145) & (hsv[:, :, 1] <= 95)).astype(np.uint8) * 255
    mask[:82, :] = 0
    mask[344:, :] = 0
    mask[:, :105] = 0
    mask[:, 330:] = 0
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    n, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)
    out = []
    for i in range(1, n):
        x, y, w, h, area = map(int, stats[i])
        if not (20 <= area <= 450 and 4 <= w <= 34 and 4 <= h <= 34):
            continue
        aspect = max(w / h, h / w)
        if aspect > 2.2:
            continue
        fill = area / (w * h)
        if fill < 0.18:
            continue
        cx, cy = centroids[i]
        out.append((float(cx), float(cy), area, w, h, float(fill)))
    return out


def distance_peaks(frame: np.ndarray) -> list[tuple[float, float, float]]:
    """Return thick bright-region centres; thin accumulated trails have low radius."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mask = (gray >= 145).astype(np.uint8)
    mask[:82, :] = 0
    mask[344:, :] = 0
    mask[:, :105] = 0
    mask[:, 330:] = 0
    dist = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
    dilated = cv2.dilate(dist, np.ones((9, 9), np.uint8))
    peak_mask = ((dist >= dilated - 1e-6) & (dist >= 3.0)).astype(np.uint8)
    n, labels, stats, centroids = cv2.connectedComponentsWithStats(peak_mask)
    out = []
    for i in range(1, n):
        ys, xs = np.where(labels == i)
        if len(xs) == 0:
            continue
        values = dist[ys, xs]
        j = int(np.argmax(values))
        out.append((float(xs[j]), float(ys[j]), float(values[j])))
    return sorted(out, key=lambda row: row[2], reverse=True)


def main() -> None:
    cap = cv2.VideoCapture(str(VIDEO))
    if not cap.isOpened():
        raise RuntimeError("video did not open")
    frame_index = 0
    frames = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frames.append(frame)
        cands = candidates(frame)
        compact = sorted(cands, key=lambda row: row[2], reverse=True)[:8]
        print(frame_index, compact, "DIST", distance_peaks(frame)[:8])
        frame_index += 1
    cap.release()

    for run_id, (start, stop) in enumerate(RUN_RANGES, start=1):
        indices = list(range(start, stop + 1))
        cols = 6
        rows = int(np.ceil(len(indices) / cols))
        fig, axes = plt.subplots(rows, cols, figsize=(13, 2.25 * rows), constrained_layout=True)
        axes = np.atleast_1d(axes).ravel()
        for ax, frame_index in zip(axes, indices):
            frame = frames[frame_index].copy()
            for cx, cy, area, w, h, _fill in candidates(frame):
                cv2.rectangle(
                    frame,
                    (int(cx - w / 2), int(cy - h / 2)),
                    (int(cx + w / 2), int(cy + h / 2)),
                    (0, 255, 0),
                    1,
                )
            for cx, cy, radius in distance_peaks(frame):
                cv2.circle(frame, (int(cx), int(cy)), max(3, int(radius)), (255, 255, 0), 1)
            ax.imshow(cv2.cvtColor(frame[80:344, 105:330], cv2.COLOR_BGR2RGB))
            ax.set_title(f"frame {frame_index}", fontsize=8)
            ax.set_axis_off()
        for ax in axes[len(indices):]:
            ax.set_axis_off()
        fig.suptitle(f"T360 marker candidates — run {run_id}", fontsize=13, fontweight="bold")
        fig.savefig(HERE / f"T360_DEBUG_RUN_{run_id}_CANDIDATES.png", dpi=160, facecolor="white")
        plt.close(fig)


if __name__ == "__main__":
    main()
