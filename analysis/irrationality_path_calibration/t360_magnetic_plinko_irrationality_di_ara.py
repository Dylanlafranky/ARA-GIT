"""Run the frozen T360 magnetic-Plinko Irrationality Di-ARA test.

Active protocol chain: v1 + extraction amendment v2 + uniform trace amendment
v4 + non-degenerate control amendment v5. V3 is preserved but superseded.
"""

from __future__ import annotations

from itertools import product
import json
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator
from scipy.ndimage import gaussian_filter
from scipy.stats import spearmanr, wilcoxon


HERE = Path(__file__).resolve().parent
PATHS_FILE = HERE / "T360_MAGNETIC_PLINKO_EXTRACTED_PATHS.csv"
MAGNETS_FILE = HERE / "T360_MAGNETIC_PLINKO_REGISTERED_MAGNETS.csv"
ANCHORS_FILE = HERE / "T360_MAGNETIC_PLINKO_MARKER_ANCHORS.csv"
PARENT_IMAGE_FILE = HERE / "T360_SOURCE_PUBLISHED_TRAJECTORIES.png"
VIDEO_FILE = HERE / "T360_SOURCE_GEORGIA_TECH_MAGNETIC_PLINKO_EXPERIMENT.mp4"

PREFIX = "T360_MAGNETIC_PLINKO_IRRATIONALITY_DI_ARA"
POINTS_OUT = HERE / f"{PREFIX}_POINTS.csv"
EVENTS_OUT = HERE / f"{PREFIX}_EVENTS.csv"
CONTROLS_OUT = HERE / f"{PREFIX}_CONTROLS.csv"
GATES_OUT = HERE / f"{PREFIX}_FROZEN_GATES.csv"
RESULTS_OUT = HERE / f"{PREFIX}_RESULTS.json"
FIGURE_OUT = HERE / f"{PREFIX}_FIGURE.png"

EVENT_ROWS = np.asarray([0.0, 0.25, 0.5, 0.75, 1.0])
TANGENT_WINDOW = (0.02, 0.11)
DENSITY_U_RANGE = (-0.25, 1.25)
DENSITY_V_RANGE = (-0.35, 1.35)
DENSITY_BINS = (300, 340)  # u, v
DENSITY_SIGMA_BINS = 2.5
VISUAL_QA_COMPLETED = True


def aggregate_magnets_and_affine(image: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    red = (((hsv[:, :, 0] <= 10) | (hsv[:, :, 0] >= 170)) & (hsv[:, :, 1] >= 100) & (hsv[:, :, 2] >= 100)).astype(np.uint8)
    n, _labels, stats, centroids = cv2.connectedComponentsWithStats(red)
    centres = []
    for i in range(1, n):
        area = int(stats[i, cv2.CC_STAT_AREA])
        if 40 <= area <= 120:
            centres.append(centroids[i])
    points = np.asarray(sorted(centres, key=lambda p: p[1]), dtype=float)
    if len(points) != 28:
        raise RuntimeError(f"Expected 28 aggregate magnets, recovered {len(points)}")

    sorted_points = points[np.argsort(points[:, 1])]
    gaps = np.diff(sorted_points[:, 1])
    breaks = sorted((np.argsort(gaps)[-4:] + 1).tolist())
    chunks = sorted(np.split(sorted_points, breaks), key=lambda block: float(np.mean(block[:, 1])))
    if [len(block) for block in chunks] != [6, 5, 6, 5, 6]:
        raise RuntimeError("Aggregate magnet rows did not recover as 6/5/6/5/6")
    px = []
    uv = []
    for row, block in enumerate(chunks):
        block = block[np.argsort(block[:, 0])]
        us = np.linspace(0, 1, 6) if len(block) == 6 else np.linspace(0.1, 0.9, 5)
        for point, u in zip(block, us):
            px.append(point)
            uv.append((float(u), row / 4.0))
    px = np.asarray(px)
    uv = np.asarray(uv)
    design = np.column_stack([np.ones(len(uv)), uv])
    coef_x, *_ = np.linalg.lstsq(design, px[:, 0], rcond=None)
    coef_y, *_ = np.linalg.lstsq(design, px[:, 1], rcond=None)
    affine = np.vstack([coef_x, coef_y])
    return px, uv, affine


def parent_density(image: np.ndarray) -> tuple[RegularGridInterpolator, np.ndarray, np.ndarray, np.ndarray]:
    _mag_px, _mag_uv, affine = aggregate_magnets_and_affine(image)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    blue = ((hsv[:, :, 0] >= 90) & (hsv[:, :, 0] <= 135) & (hsv[:, :, 1] >= 35) & (hsv[:, :, 2] >= 45))
    ys, xs = np.where(blue)
    pixels = np.column_stack([xs, ys]).astype(float)
    offset = affine[:, 0]
    linear = affine[:, 1:]
    uv = (pixels - offset) @ np.linalg.inv(linear).T
    keep = (
        (uv[:, 0] >= DENSITY_U_RANGE[0])
        & (uv[:, 0] <= DENSITY_U_RANGE[1])
        & (uv[:, 1] >= DENSITY_V_RANGE[0])
        & (uv[:, 1] <= DENSITY_V_RANGE[1])
    )
    uv = uv[keep]
    u_edges = np.linspace(*DENSITY_U_RANGE, DENSITY_BINS[0] + 1)
    v_edges = np.linspace(*DENSITY_V_RANGE, DENSITY_BINS[1] + 1)
    histogram, _, _ = np.histogram2d(uv[:, 1], uv[:, 0], bins=[v_edges, u_edges])
    smooth = gaussian_filter(histogram.astype(float), DENSITY_SIGMA_BINS)
    u_centres = 0.5 * (u_edges[:-1] + u_edges[1:])
    v_centres = 0.5 * (v_edges[:-1] + v_edges[1:])
    uu, vv = np.meshgrid(u_centres, v_centres)
    board = (uu >= 0) & (uu <= 1) & (vv >= 0) & (vv <= 1)
    scale = float(np.percentile(smooth[board], 99.0))
    normalized = np.clip(smooth / max(scale, 1e-12), 0, 1)
    interpolator = RegularGridInterpolator(
        (v_centres, u_centres), normalized, bounds_error=False, fill_value=0.0
    )
    return interpolator, u_centres, v_centres, normalized


def sample_density(interpolator: RegularGridInterpolator, u: np.ndarray, v: np.ndarray) -> np.ndarray:
    return interpolator(np.column_stack([v, u])).astype(float)


def nearest_distance_and_id(points: np.ndarray, magnets: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    differences = points[:, None, :] - magnets[None, :, :]
    distances = np.linalg.norm(differences, axis=2)
    ids = np.argmin(distances, axis=1)
    return distances[np.arange(len(points)), ids], ids


def wrong_layouts(real: np.ndarray) -> dict[str, np.ndarray]:
    mirror = real.copy()
    mirror[:, 0] = 1 - mirror[:, 0]

    shift = real.copy()
    shift[:, 0] = np.mod(shift[:, 0] + 0.1, 1.0)

    row_cycle = real.copy()
    row_cycle[:, 1] = np.mod(row_cycle[:, 1] + 0.25, 1.25)

    stagger = real.copy()
    row_index = np.rint(stagger[:, 1] * 4).astype(int)
    stagger[:, 0] = np.mod(stagger[:, 0] + np.where(row_index % 2 == 0, 0.1, -0.1), 1.0)
    return {
        "mirror": mirror,
        "half_column_shift": shift,
        "cyclic_row_shift": row_cycle,
        "stagger_inversion": stagger,
    }


def fit_slope(group: pd.DataFrame, low: float, high: float) -> float | None:
    block = group[(group.v >= low) & (group.v <= high)]
    if len(block) < 5:
        return None
    return float(np.polyfit(block.v.to_numpy(), block.u.to_numpy(), 1)[0])


def unit_tangent(slope: float) -> np.ndarray:
    vector = np.asarray([slope, 1.0], dtype=float)
    return vector / np.linalg.norm(vector)


def event_table(points: pd.DataFrame, magnets: np.ndarray, layouts: dict[str, np.ndarray]) -> pd.DataFrame:
    rows = []
    for run_id, group in points.groupby("run_id"):
        group = group.sort_values("v")
        for row_index, row_v in enumerate(EVENT_ROWS):
            inner, outer = TANGENT_WINDOW
            slope_in = fit_slope(group, row_v - outer, row_v - inner)
            slope_out = fit_slope(group, row_v + inner, row_v + outer)
            if slope_in is None or slope_out is None:
                continue
            tangent_in = unit_tangent(slope_in)
            tangent_out = unit_tangent(slope_out)
            delta = tangent_out - tangent_in
            approach_v = row_v - inner
            approach_u = float(np.interp(approach_v, group.v, group.u))
            approach = np.asarray([approach_u, approach_v])

            layout_scores = {}
            nearest_real_id = None
            for name, layout in {"real": magnets, **layouts}.items():
                distances = np.linalg.norm(layout - approach[None, :], axis=1)
                nearest = int(np.argmin(distances))
                vector = layout[nearest] - approach
                vector /= max(np.linalg.norm(vector), 1e-12)
                layout_scores[name] = float(np.dot(delta, vector))
                if name == "real":
                    nearest_real_id = nearest

            approach_density = float(group.loc[(group.v >= row_v - outer) & (group.v <= row_v - inner), "x_P"].median())
            exit_density = float(group.loc[(group.v >= row_v + inner) & (group.v <= row_v + outer), "x_P"].median())
            delta_x_p = exit_density - approach_density
            rows.append(
                {
                    "run_id": int(run_id),
                    "row_index": row_index,
                    "row_v": row_v,
                    "approach_u": approach_u,
                    "approach_v": approach_v,
                    "slope_in": slope_in,
                    "slope_out": slope_out,
                    "delta_tau_u": float(delta[0]),
                    "delta_tau_v": float(delta[1]),
                    "nearest_real_magnet_id": int(nearest_real_id) + 1,
                    "A_real": layout_scores["real"],
                    "A_mirror": layout_scores["mirror"],
                    "A_half_column_shift": layout_scores["half_column_shift"],
                    "A_cyclic_row_shift": layout_scores["cyclic_row_shift"],
                    "A_stagger_inversion": layout_scores["stagger_inversion"],
                    "x_P_approach": approach_density,
                    "x_P_exit": exit_density,
                    "delta_x_P": delta_x_p,
                    "joint_positive": bool(layout_scores["real"] > 0 and delta_x_p > 0),
                }
            )
    return pd.DataFrame(rows)


def exact_within_run_label_p(matrix: np.ndarray) -> tuple[float, float]:
    """Exact one-sided 4^n label randomization; first column is declared real."""
    observed = float(np.mean(matrix[:, 0] - matrix[:, 1:].mean(axis=1)))
    null = []
    for choices in product(range(matrix.shape[1]), repeat=matrix.shape[0]):
        values = []
        for row, choice in zip(matrix, choices):
            others = np.delete(row, choice)
            values.append(row[choice] - float(np.mean(others)))
        null.append(float(np.mean(values)))
    null = np.asarray(null)
    p_value = float(np.mean(null >= observed - 1e-12))
    return observed, p_value


def parent_controls(points: pd.DataFrame, density: RegularGridInterpolator) -> pd.DataFrame:
    rows = []
    for run_id, group in points.groupby("run_id"):
        block = group[(group.v >= 0) & (group.v <= 1)]
        u = block.u.to_numpy()
        v = block.v.to_numpy()
        variants = {
            "real": u,
            "mirror": 1 - u,
            "shift_minus": u - 0.1,
            "shift_plus": u + 0.1,
        }
        for name, variant_u in variants.items():
            values = sample_density(density, variant_u, v)
            rows.append(
                {
                    "control_family": "parent_channel",
                    "run_id": int(run_id),
                    "condition": name,
                    "value": float(np.median(values)),
                }
            )
    return pd.DataFrame(rows)


def chronology_controls(events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    detail = []
    summary = []
    run_ids = sorted(events.run_id.unique())
    event_map = {run: events[events.run_id == run].sort_values("row_index").copy() for run in run_ids}
    for index, run_id in enumerate(run_ids):
        block = event_map[run_id]
        a = block.A_real.to_numpy()
        dx = block.delta_x_P.to_numpy()
        other = event_map[run_ids[(index + 1) % len(run_ids)]]
        other_dx_by_row = dict(zip(other.row_index, other.delta_x_P))
        wrong_lineage = np.asarray([other_dx_by_row.get(row, np.nan) for row in block.row_index])
        conditions = {
            "real": dx,
            "row_reversal": dx[::-1],
            "cyclic_row_shift": np.roll(dx, 1),
            "wrong_lineage": wrong_lineage,
        }
        for condition, paired_dx in conditions.items():
            valid = np.isfinite(paired_dx)
            joint = (a[valid] > 0) & (paired_dx[valid] > 0)
            rate = float(np.mean(joint)) if len(joint) else np.nan
            summary.append(
                {
                    "control_family": "chronology",
                    "run_id": int(run_id),
                    "condition": condition,
                    "value": rate,
                }
            )
            for row_index, a_value, dx_value, joint_value in zip(
                block.row_index.to_numpy()[valid], a[valid], paired_dx[valid], joint
            ):
                detail.append(
                    {
                        "run_id": int(run_id),
                        "condition": condition,
                        "row_index": int(row_index),
                        "A_real": float(a_value),
                        "paired_delta_x_P": float(dx_value),
                        "joint_positive": bool(joint_value),
                    }
                )
    return pd.DataFrame(summary), pd.DataFrame(detail)


def read_source_frame(index: int = 122) -> np.ndarray:
    cap = cv2.VideoCapture(str(VIDEO_FILE))
    cap.set(cv2.CAP_PROP_POS_FRAMES, index)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError(f"Could not read source frame {index}")
    return frame


def make_figure(
    points: pd.DataFrame,
    events: pd.DataFrame,
    magnets: np.ndarray,
    u_grid: np.ndarray,
    v_grid: np.ndarray,
    density_grid: np.ndarray,
    controls: pd.DataFrame,
    gates: pd.DataFrame,
    verdict: str,
) -> None:
    blue = "#4c78a8"
    gold = "#d39b34"
    green = "#4f9d69"
    red = "#c75b5b"
    grey = "#9aa1a9"
    run_colours = ["#355c7d", "#6c5b7b", "#c06c84", "#d39b34", "#4f9d69"]
    cmap = LinearSegmentedColormap.from_list("parent", ["#ffffff", "#d8e5f2", "#4c78a8", "#243f5a"])

    fig = plt.figure(figsize=(17, 16), constrained_layout=True)
    gs = fig.add_gridspec(3, 2)

    ax = fig.add_subplot(gs[0, 0])
    source = cv2.cvtColor(read_source_frame(122), cv2.COLOR_BGR2RGB)
    ax.imshow(source)
    for run_id, group in points.groupby("run_id"):
        ax.plot(group.x_smooth_px, group.y_px, lw=2.0, color=run_colours[int(run_id) - 1], label=f"run {run_id}")
    ax.scatter(
        pd.read_csv(MAGNETS_FILE).video_x_px,
        pd.read_csv(MAGNETS_FILE).video_y_px,
        s=34,
        facecolors="none",
        edgecolors="#f08a24",
        lw=1.0,
    )
    ax.set_xlim(150, 325)
    ax.set_ylim(320, 90)
    ax.set_xlabel("video x (pixels)")
    ax.set_ylabel("video y (pixels; downstream increases)")
    ax.set_title("Source surface and five recovered physical paths", loc="left", fontweight="bold")
    ax.legend(ncol=3, fontsize=8, frameon=False)

    ax = fig.add_subplot(gs[0, 1])
    ax.imshow(
        density_grid,
        origin="lower",
        extent=[u_grid.min(), u_grid.max(), v_grid.min(), v_grid.max()],
        aspect="auto",
        cmap=cmap,
        vmin=0,
        vmax=1,
    )
    for run_id, group in points.groupby("run_id"):
        ax.plot(group.u, group.v, lw=1.8, color=run_colours[int(run_id) - 1])
    ax.scatter(magnets[:, 0], magnets[:, 1], s=34, facecolors="none", edgecolors="#f08a24", lw=1.0)
    ax.set_xlim(-0.12, 1.12)
    ax.set_ylim(1.15, -0.2)
    ax.set_xlabel("lateral lattice coordinate u")
    ax.set_ylabel("downstream lattice coordinate v")
    ax.set_title("Five child paths against the 400-run parent field", loc="left", fontweight="bold")

    ax = fig.add_subplot(gs[1, 0])
    for run_id, group in points.groupby("run_id"):
        colour = run_colours[int(run_id) - 1]
        ax.plot(group.v, group.x_C, color=gold, alpha=0.22, lw=1.2)
        ax.plot(group.v, group.x_P, color=blue, alpha=0.22, lw=1.2)
        # Run-colour endpoints make the five traces distinguishable without changing coordinate colour.
        ax.scatter(group.v.iloc[-1], group.x_C.iloc[-1], s=22, color=colour, marker="o")
        ax.scatter(group.v.iloc[-1], group.x_P.iloc[-1], s=22, color=colour, marker="s")
    ax.axhline(1, color="#555555", lw=1, ls="--")
    ax.set_xlim(-0.2, 1.2)
    ax.set_ylim(0, 2)
    ax.set_xlabel("downstream position v")
    ax.set_ylabel("ARA coordinate (0–2)")
    ax.set_title("Connection state and parent-channel history", loc="left", fontweight="bold")
    ax.plot([], [], color=gold, label="x_C: free → connection-loaded")
    ax.plot([], [], color=blue, label="x_P: open → reused parent channel")
    ax.legend(frameon=False, fontsize=8)

    ax = fig.add_subplot(gs[1, 1])
    for run_id, group in points.groupby("run_id"):
        ax.plot(group.u, group.v, color="#c8ccd0", lw=1.0, zorder=1)
    ax.scatter(magnets[:, 0], magnets[:, 1], s=30, facecolors="none", edgecolors="#f08a24", lw=1.0, zorder=2)
    for _, event in events.iterrows():
        supportive = bool(event.joint_positive)
        colour = green if supportive else red
        ax.arrow(
            event.approach_u,
            event.approach_v,
            1.7 * event.delta_tau_u,
            1.7 * event.delta_tau_v,
            width=0.002,
            head_width=0.018,
            length_includes_head=True,
            color=colour,
            alpha=0.85,
            zorder=3,
        )
    ax.set_xlim(-0.12, 1.12)
    ax.set_ylim(1.12, -0.15)
    ax.set_xlabel("lateral lattice coordinate u")
    ax.set_ylabel("downstream lattice coordinate v")
    ax.set_title("Row handovers: turn + parent-channel change", loc="left", fontweight="bold")
    ax.scatter([], [], color=green, label="both positive")
    ax.scatter([], [], color=red, label="one/both non-positive")
    ax.legend(frameon=False, fontsize=8)

    ax = fig.add_subplot(gs[2, 0])
    layout_cols = ["A_real", "A_mirror", "A_half_column_shift", "A_cyclic_row_shift", "A_stagger_inversion"]
    layout_labels = ["real", "mirror", "half shift", "row shift", "stagger flip"]
    layout_values = [float(events[column].median()) for column in layout_cols]
    parent = controls[controls.control_family == "parent_channel"].groupby("condition").value.mean()
    chronology = controls[controls.control_family == "chronology"].groupby("condition").value.mean()
    sections = [
        (layout_labels, layout_values, "median turn alignment", gold),
        (["real", "mirror", "shift −", "shift +"], [parent.get(k, np.nan) for k in ["real", "mirror", "shift_minus", "shift_plus"]], "median parent density", blue),
        (["real", "reverse", "row shift", "wrong lineage"], [chronology.get(k, np.nan) for k in ["real", "row_reversal", "cyclic_row_shift", "wrong_lineage"]], "joint-positive rate", green),
    ]
    x0 = 0
    tick_positions = []
    tick_labels = []
    for labels, values, title, colour in sections:
        xs = np.arange(len(labels)) + x0
        bars = ax.bar(xs, values, width=0.72, color=[colour] + [grey] * (len(values) - 1), alpha=0.9)
        for bar, value in zip(bars, values):
            if np.isfinite(value):
                ax.text(bar.get_x() + bar.get_width() / 2, value, f"{value:.2f}", ha="center", va="bottom", fontsize=7)
        ax.text(float(np.mean(xs)), ax.get_ylim()[0], title, transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=8, fontweight="bold")
        tick_positions.extend(xs)
        tick_labels.extend(labels)
        x0 += len(labels) + 1
    ax.axhline(0, color="#333333", lw=0.8)
    ax.set_xticks(tick_positions, tick_labels, rotation=38, ha="right", fontsize=7)
    ax.set_title("Frozen real-versus-control comparisons", loc="left", fontweight="bold")
    ax.set_ylabel("declared metric value")
    ax.grid(axis="y", alpha=0.2)

    ax = fig.add_subplot(gs[2, 1])
    ax.set_axis_off()
    y = 0.96
    ax.text(0.0, y, "Frozen gate audit", fontsize=14, fontweight="bold", transform=ax.transAxes)
    y -= 0.09
    for _, gate in gates.iterrows():
        marker = "PASS" if bool(gate["pass"]) else "FAIL"
        colour = green if bool(gate["pass"]) else red
        ax.text(0.0, y, f"{gate.gate}: {marker}", color=colour, fontsize=11, fontweight="bold", transform=ax.transAxes)
        ax.text(0.02, y - 0.042, gate.display_value, color="#333333", fontsize=8.4, transform=ax.transAxes)
        y -= 0.13
    ax.text(0.0, y - 0.005, f"Benchmark verdict: {verdict}", fontsize=12, fontweight="bold", transform=ax.transAxes)
    ax.text(
        0.0,
        y - 0.12,
        "Magnetic nearest-connection steering only.\nFive public paths; parent field is an aggregate from the same experiment.",
        fontsize=9,
        color="#555555",
        transform=ax.transAxes,
    )

    fig.suptitle(
        f"T360 magnetic-Plinko Irrationality Di-ARA frozen test — {verdict}",
        fontsize=17,
        fontweight="bold",
    )
    fig.savefig(FIGURE_OUT, dpi=190, facecolor="white")
    plt.close(fig)


def main() -> None:
    points = pd.read_csv(PATHS_FILE)
    magnets_frame = pd.read_csv(MAGNETS_FILE)
    anchors = pd.read_csv(ANCHORS_FILE)
    magnets = magnets_frame[["u", "v"]].to_numpy(dtype=float)
    parent_image = cv2.imread(str(PARENT_IMAGE_FILE))
    if parent_image is None:
        raise RuntimeError(f"Could not read {PARENT_IMAGE_FILE}")
    density, u_grid, v_grid, density_grid = parent_density(parent_image)

    points["parent_density"] = sample_density(density, points.u.to_numpy(), points.v.to_numpy())
    points["x_P"] = 2 * np.clip(points.parent_density, 0, 1)
    distances, nearest_ids = nearest_distance_and_id(points[["u", "v"]].to_numpy(), magnets)
    d90 = float(np.percentile(distances[(points.v >= 0) & (points.v <= 1)], 90))
    points["nearest_magnet_distance"] = distances
    points["nearest_magnet_id"] = nearest_ids + 1
    points["x_C"] = 2 * np.clip(1 - distances / d90, 0, 1)

    layouts = wrong_layouts(magnets)
    events = event_table(points, magnets, layouts)

    parent_control = parent_controls(points, density)
    chronology_summary, chronology_detail = chronology_controls(events)
    controls = pd.concat([parent_control, chronology_summary], ignore_index=True)

    # G0
    spans = points.groupby("run_id").v.agg(lambda values: float(values.max() - values.min()))
    tangent_counts = events.groupby("run_id").size().reindex(range(1, 6), fill_value=0)
    anchor_counts = anchors.groupby("run_id").size().reindex(range(1, 6), fill_value=0)
    anchor_medians = anchors.groupby("run_id").lateral_discrepancy_px.median().reindex(range(1, 6))
    g0 = bool(
        (spans >= 0.8).all()
        and (tangent_counts >= 4).all()
        and (anchor_counts >= 6).all()
        and (anchor_medians <= 8).all()
        and len(magnets) == 28
        and VISUAL_QA_COMPLETED
    )

    # G1
    wrong_columns = ["A_mirror", "A_half_column_shift", "A_cyclic_row_shift", "A_stagger_inversion"]
    events["A_wrong_mean"] = events[wrong_columns].mean(axis=1)
    real_alignment_median = float(events.A_real.median())
    real_alignment_positive_rate = float((events.A_real > 0).mean())
    real_beats_each = all(real_alignment_median > float(events[column].median()) for column in wrong_columns)
    g1_wilcoxon = wilcoxon(
        events.A_real.to_numpy(),
        events.A_wrong_mean.to_numpy(),
        alternative="greater",
        method="exact",
    )
    g1_p = float(g1_wilcoxon.pvalue)
    g1 = bool(real_alignment_median > 0 and real_alignment_positive_rate >= 0.70 and real_beats_each and g1_p <= 0.05)

    # G2
    parent_matrix_frame = parent_control.pivot(index="run_id", columns="condition", values="value")
    parent_matrix = parent_matrix_frame[["real", "mirror", "shift_minus", "shift_plus"]].to_numpy()
    real_run_wins = int(sum(row[0] > np.max(row[1:]) for row in parent_matrix))
    g2_effect, g2_p = exact_within_run_label_p(parent_matrix)
    g2 = bool(real_run_wins >= 4 and g2_effect > 0 and g2_p <= 0.05)

    # G3
    chronology_matrix_frame = chronology_summary.pivot(index="run_id", columns="condition", values="value")
    chronology_matrix = chronology_matrix_frame[["real", "row_reversal", "cyclic_row_shift", "wrong_lineage"]].to_numpy()
    real_joint_rate = float(events.joint_positive.mean())
    chronology_rates = chronology_summary.groupby("condition").value.mean()
    g3_beats_each = all(real_joint_rate > float(chronology_rates[condition]) for condition in ["row_reversal", "cyclic_row_shift", "wrong_lineage"])
    g3_effect, g3_p = exact_within_run_label_p(chronology_matrix)
    g3 = bool(real_joint_rate >= 0.65 and g3_beats_each and g3_p <= 0.05)

    # G4
    analysis_points = points[(points.v >= 0) & (points.v <= 1)].copy()
    rho, rho_p = spearmanr(analysis_points.x_C, analysis_points.x_P)
    iqr_c = float(analysis_points.x_C.quantile(0.75) - analysis_points.x_C.quantile(0.25))
    iqr_p = float(analysis_points.x_P.quantile(0.75) - analysis_points.x_P.quantile(0.25))
    g4 = bool(abs(float(rho)) < 0.90 and iqr_c > 0 and iqr_p > 0)

    gates = pd.DataFrame(
        [
            {
                "gate": "G0 extraction/lattice QA",
                "pass": g0,
                "display_value": f"5 paths; spans {spans.min():.2f}–{spans.max():.2f}; anchors {anchor_counts.min()}–{anchor_counts.max()}; 28 magnets",
            },
            {
                "gate": "G1 real connection geometry",
                "pass": g1,
                "display_value": f"median A={real_alignment_median:.3f}; positive={real_alignment_positive_rate:.1%}; exact p={g1_p:.4f}",
            },
            {
                "gate": "G2 parent-channel inheritance",
                "pass": g2,
                "display_value": f"run wins={real_run_wins}/5; effect={g2_effect:.3f}; exact p={g2_p:.4f}",
            },
            {
                "gate": "G3 connection-to-lock order",
                "pass": g3,
                "display_value": f"joint positive={real_joint_rate:.1%}; effect={g3_effect:.3f}; exact p={g3_p:.4f}",
            },
            {
                "gate": "G4 coordinate non-redundancy",
                "pass": g4,
                "display_value": f"Spearman ρ={float(rho):.3f}; IQR x_C={iqr_c:.3f}; IQR x_P={iqr_p:.3f}",
            },
        ]
    )
    verdict = "SUPPORTED [small physical calibration]" if bool(gates["pass"].all()) else "NOT SUPPORTED"

    controls_detail = pd.concat(
        [
            controls,
            pd.DataFrame(
                [
                    {
                        "control_family": "connection_layout",
                        "run_id": 0,
                        "condition": name,
                        "value": float(events[column].median()),
                    }
                    for name, column in zip(
                        ["real", "mirror", "half_column_shift", "cyclic_row_shift", "stagger_inversion"],
                        ["A_real", *wrong_columns],
                    )
                ]
            ),
        ],
        ignore_index=True,
    )

    points.to_csv(POINTS_OUT, index=False)
    events.to_csv(EVENTS_OUT, index=False)
    controls_detail.to_csv(CONTROLS_OUT, index=False)
    gates.to_csv(GATES_OUT, index=False)
    chronology_detail.to_csv(HERE / f"{PREFIX}_CHRONOLOGY_EVENT_CONTROLS.csv", index=False)

    results = {
        "test": "T360 magnetic-Plinko Irrationality Di-ARA",
        "active_protocol": "v1 + v2 + v4 + v5",
        "verdict": verdict,
        "n_paths": 5,
        "n_events": int(len(events)),
        "n_parent_runs_published": 400,
        "d90_nearest_magnet": d90,
        "gates": {row.gate: bool(row["pass"]) for _, row in gates.iterrows()},
        "G1": {
            "real_median_alignment": real_alignment_median,
            "positive_rate": real_alignment_positive_rate,
            "real_beats_each_wrong_layout": bool(real_beats_each),
            "exact_wilcoxon_p": g1_p,
            "layout_medians": {
                "real": real_alignment_median,
                **{column.removeprefix("A_"): float(events[column].median()) for column in wrong_columns},
            },
        },
        "G2": {
            "run_wins": real_run_wins,
            "effect": g2_effect,
            "exact_label_randomization_p": g2_p,
            "condition_means": parent_control.groupby("condition").value.mean().to_dict(),
        },
        "G3": {
            "joint_positive_rate": real_joint_rate,
            "real_beats_each_control": bool(g3_beats_each),
            "effect": g3_effect,
            "exact_label_randomization_p": g3_p,
            "condition_means": chronology_rates.to_dict(),
        },
        "G4": {
            "spearman_rho": float(rho),
            "spearman_p": float(rho_p),
            "iqr_x_C": iqr_c,
            "iqr_x_P": iqr_p,
        },
        "limitations": [
            "Five public source paths only.",
            "Published tracker overlays supply spatial paths; no clock-time or force is inferred.",
            "The 400-run parent field is aggregate and from the same experiment.",
            "Magnetic steering is not discrete peg-collision physics.",
        ],
    }
    RESULTS_OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    make_figure(points, events, magnets, u_grid, v_grid, density_grid, controls, gates, verdict)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
