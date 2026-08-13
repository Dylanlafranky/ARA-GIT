"""Pre-score source extraction QA for T360 magnetic Plinko.

This script extracts only source geometry. It does not calculate ARA coordinates,
controls, p-values, gates, or a verdict.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter
from scipy.optimize import differential_evolution
from scipy.signal import savgol_filter


HERE = Path(__file__).resolve().parent
VIDEO = HERE / "T360_SOURCE_GEORGIA_TECH_MAGNETIC_PLINKO_EXPERIMENT.mp4"
PARENT_IMAGE = HERE / "T360_SOURCE_PUBLISHED_TRAJECTORIES.png"
OUT_PATHS = HERE / "T360_MAGNETIC_PLINKO_EXTRACTED_PATHS.csv"
OUT_MAGNETS = HERE / "T360_MAGNETIC_PLINKO_REGISTERED_MAGNETS.csv"
OUT_ANCHORS = HERE / "T360_MAGNETIC_PLINKO_MARKER_ANCHORS.csv"
OUT_FIGURE = HERE / "T360_MAGNETIC_PLINKO_EXTRACTION_QA.png"

# Frozen source-frame and colour declarations from the v2 extraction amendment.
RUNS = (
    # The active run is always red. Use its last frame before each reset so
    # all five paths are recovered under the identical source colour rule.
    (1, "red", 0, 22, 22),
    (2, "red", 26, 44, 44),
    (3, "red", 45, 67, 67),
    (4, "red", 69, 101, 101),
    (5, "red", 103, 122, 122),
)
ROI_X = (178, 304)
ROI_Y = (98, 316)
SMOOTH_WINDOW = 11


@dataclass(frozen=True)
class AggregateGeometry:
    magnets_px: np.ndarray
    magnets_uv: np.ndarray
    affine_uv_to_px: np.ndarray


def read_video() -> list[np.ndarray]:
    cap = cv2.VideoCapture(str(VIDEO))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {VIDEO}")
    frames: list[np.ndarray] = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frames.append(frame)
    cap.release()
    if len(frames) != 123:
        raise RuntimeError(f"Expected 123 public frames, found {len(frames)}")
    return frames


def trace_mask(frame: np.ndarray, colour: str, baseline: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    if colour == "red":
        mask = (((h <= 10) | (h >= 170)) & (s >= 105) & (v >= 75))
    elif colour == "cyan":
        mask = ((h >= 84) & (h <= 105) & (s >= 90) & (v >= 80))
    elif colour == "green":
        mask = ((h >= 40) & (h <= 84) & (s >= 85) & (v >= 65))
    elif colour == "yellow":
        mask = ((h >= 18) & (h <= 40) & (s >= 100) & (v >= 85))
    elif colour == "white":
        base_gray = cv2.cvtColor(baseline, cv2.COLOR_BGR2GRAY).astype(np.int16)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.int16)
        mask = ((s <= 65) & (v >= 155) & ((gray - base_gray) >= 22))
    else:
        raise ValueError(colour)
    roi = np.zeros(mask.shape, dtype=bool)
    roi[ROI_Y[0] : ROI_Y[1] + 1, ROI_X[0] : ROI_X[1] + 1] = True
    mask &= roi
    result = mask.astype(np.uint8)
    result = cv2.morphologyEx(result, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    return result.astype(bool)


def path_from_mask(mask: np.ndarray, colour: str) -> pd.DataFrame:
    """Recover one monotonic-downstream curve by row-wise colour medians."""
    rows: list[tuple[int, float, int]] = []
    previous_x: float | None = None
    for y in range(ROI_Y[0], ROI_Y[1] + 1):
        xs = np.flatnonzero(mask[y])
        if len(xs) == 0:
            continue
        # Split disjoint same-colour features; continue through the nearest run.
        groups = np.split(xs, np.where(np.diff(xs) > 2)[0] + 1)
        options = [(float(np.median(group)), len(group)) for group in groups if len(group)]
        if not options:
            continue
        if previous_x is None:
            options = [item for item in options if 225 <= item[0] <= 285] or options
            selected = max(options, key=lambda item: item[1])
        else:
            selected = min(options, key=lambda item: abs(item[0] - previous_x) - 0.04 * item[1])
            if abs(selected[0] - previous_x) > 14:
                continue
        previous_x = selected[0]
        rows.append((y, selected[0], selected[1]))
    if len(rows) < 30:
        raise RuntimeError(f"{colour} trace produced only {len(rows)} row observations")
    frame = pd.DataFrame(rows, columns=["y_px", "x_raw_px", "mask_width_px"])
    # Keep the longest downstream block after allowing short compression gaps.
    gaps = frame["y_px"].diff().fillna(1)
    block = (gaps > 16).cumsum()
    frame = frame.loc[block == block.value_counts().idxmax()].copy()
    full_y = np.arange(int(frame.y_px.min()), int(frame.y_px.max()) + 1)
    x_interp = np.interp(full_y, frame.y_px, frame.x_raw_px)
    window = min(SMOOTH_WINDOW, len(full_y) if len(full_y) % 2 else len(full_y) - 1)
    window = max(5, window)
    x_smooth = savgol_filter(x_interp, window_length=window, polyorder=2, mode="interp")
    return pd.DataFrame(
        {
            "y_px": full_y.astype(int),
            "x_raw_px": x_interp,
            "x_smooth_px": x_smooth,
            "observed_mask_row": np.isin(full_y, frame.y_px),
        }
    )


def aggregate_geometry(image: np.ndarray) -> AggregateGeometry:
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    red = (((hsv[:, :, 0] <= 10) | (hsv[:, :, 0] >= 170)) & (hsv[:, :, 1] >= 100) & (hsv[:, :, 2] >= 100)).astype(np.uint8)
    n, labels, stats, centroids = cv2.connectedComponentsWithStats(red)
    centres = []
    for i in range(1, n):
        area = int(stats[i, cv2.CC_STAT_AREA])
        if 40 <= area <= 120:
            centres.append(centroids[i])
    magnets_px = np.asarray(sorted(centres, key=lambda p: p[1]), dtype=float)
    if len(magnets_px) != 28:
        raise RuntimeError(f"Expected 28 aggregate magnets, recovered {len(magnets_px)}")

    # Five rows are separated by gaps much larger than each row's plotting tilt.
    order = np.argsort(magnets_px[:, 1])
    sorted_points = magnets_px[order]
    gaps = np.diff(sorted_points[:, 1])
    break_after = set((np.argsort(gaps)[-4:] + 1).tolist())
    row_chunks = np.split(sorted_points, sorted(break_after))
    row_chunks = sorted(row_chunks, key=lambda chunk: float(np.mean(chunk[:, 1])))
    expected_counts = [6, 5, 6, 5, 6]
    if [len(chunk) for chunk in row_chunks] != expected_counts:
        raise RuntimeError(f"Unexpected aggregate row counts: {[len(chunk) for chunk in row_chunks]}")

    pixels = []
    ideals = []
    for row_index, chunk in enumerate(row_chunks):
        chunk = chunk[np.argsort(chunk[:, 0])]
        u_values = np.linspace(0.0, 1.0, 6) if len(chunk) == 6 else np.linspace(0.1, 0.9, 5)
        v_value = row_index / 4.0
        for pixel, u_value in zip(chunk, u_values):
            pixels.append(pixel)
            ideals.append((u_value, v_value))
    magnets_px = np.asarray(pixels)
    magnets_uv = np.asarray(ideals)
    design = np.column_stack([np.ones(len(magnets_uv)), magnets_uv])
    coef_x, *_ = np.linalg.lstsq(design, magnets_px[:, 0], rcond=None)
    coef_y, *_ = np.linalg.lstsq(design, magnets_px[:, 1], rcond=None)
    affine = np.vstack([coef_x, coef_y])
    return AggregateGeometry(magnets_px, magnets_uv, affine)


def magnetness_map(frame: np.ndarray) -> np.ndarray:
    b, g, r = cv2.split(frame.astype(float))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(float)
    dark = gaussian_filter(gray, 4.0) - gaussian_filter(gray, 0.8)
    red = r - 0.5 * (g + b)
    score = dark + 0.45 * red
    score = gaussian_filter(score, 1.0)
    med = float(np.median(score[105:300, 150:335]))
    mad = float(np.median(np.abs(score[105:300, 150:335] - med))) + 1e-6
    return (score - med) / (1.4826 * mad)


def register_video_magnets(frame0: np.ndarray, geometry: AggregateGeometry) -> tuple[np.ndarray, np.ndarray]:
    """Register the known 6/5/6/5/6 lattice to the raw video background."""
    uv = geometry.magnets_uv
    score = magnetness_map(frame0)

    def objective(parameters: np.ndarray) -> float:
        x0, sx, sh, y0, sy, tilt = parameters
        xs = x0 + sx * uv[:, 0] + sh * uv[:, 1]
        ys = y0 + sy * uv[:, 1] + tilt * uv[:, 0]
        if np.any(xs < 145) or np.any(xs > 342) or np.any(ys < 105) or np.any(ys > 300):
            return 1e6
        values = []
        for x, y in zip(xs, ys):
            xi, yi = int(round(x)), int(round(y))
            patch = score[max(0, yi - 2) : yi + 3, max(0, xi - 2) : xi + 3]
            values.append(float(np.max(patch)))
        # Light regularization prevents a texture-only very narrow fit.
        regularization = 0.0005 * ((sx - 150) ** 2 + (sy - 145) ** 2)
        return -float(np.mean(values)) + regularization

    bounds = [(150, 205), (120, 180), (-18, 18), (118, 150), (125, 175), (-14, 14)]
    result = differential_evolution(
        objective,
        bounds=bounds,
        seed=360,
        maxiter=280,
        popsize=18,
        polish=True,
        updating="immediate",
        workers=1,
    )
    x0, sx, sh, y0, sy, tilt = result.x
    transform = np.array([[x0, sx, sh], [y0, tilt, sy]], dtype=float)
    design = np.column_stack([np.ones(len(uv)), uv])
    video_px = design @ transform.T
    return video_px, transform


def extract_marker_anchors(frames: list[np.ndarray], paths: dict[int, pd.DataFrame]) -> pd.DataFrame:
    """Locate the thick active marker along each already-declared run trace."""
    rows = []
    for run_id, colour, start, stop, _end_frame in RUNS:
        path = paths[run_id]
        ys = path.y_px.to_numpy(dtype=int)
        xs = path.x_smooth_px.to_numpy(dtype=float)
        last_y = -np.inf
        for frame_index in range(start, stop + 1):
            gray = cv2.cvtColor(frames[frame_index], cv2.COLOR_BGR2GRAY).astype(float)
            small = gaussian_filter(gray, 1.8)
            broad = gaussian_filter(gray, 6.5)
            dog = small - broad
            valid = (ys >= ROI_Y[0]) & (ys <= ROI_Y[1])
            sample_y = ys[valid]
            sample_x = np.rint(xs[valid]).astype(int)
            local_scores = []
            for x, y in zip(sample_x, sample_y):
                patch = dog[max(0, y - 4) : y + 5, max(0, x - 4) : x + 5]
                local_scores.append(float(np.max(patch)))
            local_scores = np.asarray(local_scores)
            if len(local_scores) == 0:
                continue
            # The physical marker moves downstream; tolerate short stalls but not resets inside a run.
            allowed = sample_y >= last_y - 5
            if not np.any(allowed):
                continue
            masked_scores = np.where(allowed, local_scores, -np.inf)
            index = int(np.argmax(masked_scores))
            score_value = float(masked_scores[index])
            if not np.isfinite(score_value) or score_value < 8.0:
                continue
            path_y = int(sample_y[index])
            path_x = float(xs[valid][index])
            x0 = int(round(path_x))
            patch = dog[max(0, path_y - 4) : path_y + 5, max(0, x0 - 4) : x0 + 5]
            py, px = np.unravel_index(int(np.argmax(patch)), patch.shape)
            actual_y = max(0, path_y - 4) + int(py)
            actual_x = max(0, x0 - 4) + int(px)
            path_x_at_actual_y = float(np.interp(actual_y, ys, xs))
            last_y = max(last_y, actual_y)
            rows.append(
                {
                    "run_id": run_id,
                    "colour": colour,
                    "frame": frame_index,
                    "x_anchor_px": actual_x,
                    "y_anchor_px": actual_y,
                    "path_x_at_anchor_px": path_x_at_actual_y,
                    "lateral_discrepancy_px": abs(actual_x - path_x_at_actual_y),
                    "blob_score": score_value,
                }
            )
    return pd.DataFrame(rows)


def normalize_paths(paths: dict[int, pd.DataFrame], transform: np.ndarray) -> pd.DataFrame:
    # transform maps [1,u,v] -> [x,y]; invert the 2x2 linear part.
    offset = transform[:, 0]
    linear = transform[:, 1:]
    inverse = np.linalg.inv(linear)
    out = []
    for run_id, frame in paths.items():
        pixels = frame[["x_smooth_px", "y_px"]].to_numpy(dtype=float)
        uv = (pixels - offset) @ inverse.T
        block = frame.copy()
        block.insert(0, "run_id", run_id)
        block["u"] = uv[:, 0]
        block["v"] = uv[:, 1]
        out.append(block)
    return pd.concat(out, ignore_index=True)


def make_figure(
    frames: list[np.ndarray],
    masks: dict[int, np.ndarray],
    paths_px: dict[int, pd.DataFrame],
    paths: pd.DataFrame,
    magnets_video: np.ndarray,
    anchors: pd.DataFrame,
    geometry: AggregateGeometry,
    parent_image: np.ndarray,
) -> None:
    colours = {1: "#f5f5f5", 2: "#d62728", 3: "#22b8cf", 4: "#2ca02c", 5: "#e6bf25"}
    fig = plt.figure(figsize=(16, 13), constrained_layout=True)
    grid = fig.add_gridspec(2, 2)

    ax = fig.add_subplot(grid[0, 0])
    ax.imshow(cv2.cvtColor(frames[122], cv2.COLOR_BGR2RGB))
    for run_id, frame in paths_px.items():
        ax.plot(frame.x_smooth_px, frame.y_px, color=colours[run_id], lw=2.2, label=f"run {run_id}")
    ax.scatter(magnets_video[:, 0], magnets_video[:, 1], facecolors="none", edgecolors="#ff8c42", s=42, lw=1.2, label="registered magnets")
    for run_id, group in anchors.groupby("run_id"):
        ax.scatter(group.x_anchor_px, group.y_anchor_px, s=11, color="#111111", marker="x", alpha=0.8)
    ax.set_xlim(150, 325)
    ax.set_ylim(320, 90)
    ax.set_title("Public video geometry and extraction", loc="left", fontweight="bold")
    ax.set_xlabel("video x (pixels)")
    ax.set_ylabel("video y (pixels; downstream increases)")
    ax.legend(ncol=2, fontsize=8, frameon=False)

    ax = fig.add_subplot(grid[0, 1])
    ax.imshow(cv2.cvtColor(parent_image, cv2.COLOR_BGR2RGB))
    ax.scatter(geometry.magnets_px[:, 0], geometry.magnets_px[:, 1], s=18, facecolors="none", edgecolors="#f08a24", lw=0.9)
    ax.set_xlim(45, 850)
    ax.set_ylim(630, 135)
    ax.set_title("Published parent field: 400 physical runs", loc="left", fontweight="bold")
    ax.set_axis_off()

    ax = fig.add_subplot(grid[1, 0])
    for run_id, group in paths.groupby("run_id"):
        ax.plot(group.u, group.v, lw=2.1, color=colours[run_id], label=f"run {run_id}")
    for (u, v) in geometry.magnets_uv:
        ax.scatter(u, v, s=36, facecolors="none", edgecolors="#f08a24", lw=1.1)
    ax.set_xlim(-0.12, 1.12)
    ax.set_ylim(1.18, -0.22)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(alpha=0.2)
    ax.set_title("Five child paths in normalized lattice coordinates", loc="left", fontweight="bold")
    ax.set_xlabel("lateral lattice coordinate u")
    ax.set_ylabel("downstream lattice coordinate v")

    ax = fig.add_subplot(grid[1, 1])
    anchor_counts = anchors.groupby("run_id").size().reindex(range(1, 6), fill_value=0)
    spans = paths.groupby("run_id").v.agg(lambda values: float(values.max() - values.min()))
    x = np.arange(1, 6)
    ax.bar(x - 0.18, anchor_counts.values, width=0.36, color="#d39b34", label="marker anchors")
    ax.set_ylabel("detected anchor count")
    ax.set_xticks(x, [f"run {value}" for value in x])
    ax2 = ax.twinx()
    ax2.bar(x + 0.18, spans.reindex(x).values, width=0.36, color="#4c78a8", label="lattice-row span")
    ax2.axhline(0.8, color="#4c78a8", ls="--", lw=1)
    ax2.set_ylabel("normalized first-to-fifth-row span")
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, frameon=False, fontsize=8, loc="upper left")
    ax.set_title("Pre-score extraction QA", loc="left", fontweight="bold")
    ax.grid(axis="y", alpha=0.2)

    fig.suptitle(
        "T360 magnetic-Plinko extraction QA — no ARA gate has been scored",
        fontsize=17,
        fontweight="bold",
    )
    fig.savefig(OUT_FIGURE, dpi=180, facecolor="white")
    plt.close(fig)


def main() -> None:
    frames = read_video()
    baseline = frames[0]
    masks: dict[int, np.ndarray] = {}
    paths_px: dict[int, pd.DataFrame] = {}
    for run_id, colour, _start, _stop, end_frame in RUNS:
        mask = trace_mask(frames[end_frame], colour, baseline)
        masks[run_id] = mask
        paths_px[run_id] = path_from_mask(mask, colour)

    parent_image = cv2.imread(str(PARENT_IMAGE))
    if parent_image is None:
        raise RuntimeError(f"Could not read {PARENT_IMAGE}")
    geometry = aggregate_geometry(parent_image)
    magnets_video, transform = register_video_magnets(frames[0], geometry)
    paths = normalize_paths(paths_px, transform)
    anchors = extract_marker_anchors(frames, paths_px)

    magnet_rows = []
    for index, ((u, v), (x, y)) in enumerate(zip(geometry.magnets_uv, magnets_video), start=1):
        magnet_rows.append(
            {
                "magnet_id": index,
                "u": u,
                "v": v,
                "video_x_px": x,
                "video_y_px": y,
            }
        )
    pd.DataFrame(magnet_rows).to_csv(OUT_MAGNETS, index=False)
    paths.to_csv(OUT_PATHS, index=False)
    anchors.to_csv(OUT_ANCHORS, index=False)
    make_figure(frames, masks, paths_px, paths, magnets_video, anchors, geometry, parent_image)

    print(
        pd.DataFrame(
            {
                "trace_rows": paths.groupby("run_id").size(),
                "v_span": paths.groupby("run_id").v.agg(lambda values: float(values.max() - values.min())),
                "marker_anchors": anchors.groupby("run_id").size(),
            }
        ).to_string()
    )
    print("video transform [x/y rows; offset,u,v columns]:")
    print(transform)


if __name__ == "__main__":
    main()
