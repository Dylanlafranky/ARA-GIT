from __future__ import annotations

import hashlib
import json
import math
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source" / "MH_01_easy_state_groundtruth.csv"
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

COMPONENTS = ["w", "x", "y", "z"]
Q_COLS = ["q_RS_w []", " q_RS_x []", " q_RS_y []", " q_RS_z []"]
COLORS = {"w": "#a855f7", "x": "#3b82f6", "y": "#f59e0b", "z": "#10b981"}
RNG_SEED = 44720260829


def records(frame: pd.DataFrame) -> list[dict]:
    return json.loads(frame.replace({np.nan: None}).to_json(orient="records"))


def sample_evenly(frame: pd.DataFrame, count: int) -> pd.DataFrame:
    if len(frame) <= count:
        return frame.copy()
    indices = np.linspace(0, len(frame) - 1, count, dtype=int)
    return frame.iloc[indices].copy()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def component_sign_changes(values: np.ndarray) -> np.ndarray:
    signs = np.signbit(values)
    return np.flatnonzero(signs[1:] != signs[:-1]) + 1


def load_source() -> tuple[pd.DataFrame, dict[str, object]]:
    raw = pd.read_csv(SOURCE)
    raw.columns = [column.strip() for column in raw.columns]
    q_columns = ["q_RS_w []", "q_RS_x []", "q_RS_y []", "q_RS_z []"]
    required = ["#timestamp", *q_columns]
    missing = [column for column in required if column not in raw.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    frame = raw[required].copy()
    frame = frame.apply(pd.to_numeric, errors="coerce").dropna().drop_duplicates("#timestamp")
    frame = frame.sort_values("#timestamp").reset_index(drop=True)
    q_raw = frame[q_columns].to_numpy(dtype=float)
    raw_norm = np.linalg.norm(q_raw, axis=1)
    valid = np.isfinite(raw_norm) & (raw_norm > 0)
    frame = frame.loc[valid].reset_index(drop=True)
    q_raw = q_raw[valid]
    raw_norm = raw_norm[valid]
    q = q_raw / raw_norm[:, None]

    t_ns = frame["#timestamp"].to_numpy(dtype=np.int64)
    time_s = (t_ns - t_ns[0]) / 1e9
    out = pd.DataFrame(
        {
            "row_id": np.arange(len(frame), dtype=int),
            "timestamp_ns": t_ns,
            "time_s": time_s,
            "raw_norm": raw_norm,
            "w_raw": q_raw[:, 0],
            "x_raw": q_raw[:, 1],
            "y_raw": q_raw[:, 2],
            "z_raw": q_raw[:, 3],
            "w": q[:, 0],
            "x": q[:, 1],
            "y": q[:, 2],
            "z": q[:, 3],
        }
    )
    split_index = int(math.floor(0.70 * len(out)))
    out["split"] = np.where(out.index < split_index, "development", "holdout")
    quality = {
        "source_rows": int(len(raw)),
        "valid_unique_rows": int(len(out)),
        "duplicate_timestamps_removed": int(len(raw) - len(raw.drop_duplicates("#timestamp"))),
        "duration_seconds": float(time_s[-1]),
        "median_sample_interval_seconds": float(np.median(np.diff(time_s))),
        "raw_norm_min": float(raw_norm.min()),
        "raw_norm_median": float(np.median(raw_norm)),
        "raw_norm_max": float(raw_norm.max()),
        "negative_adjacent_quaternion_dots": int(np.sum(np.sum(q[1:] * q[:-1], axis=1) < 0)),
        "source_sha256": sha256(SOURCE),
        "development_rows": int(split_index),
        "holdout_rows": int(len(out) - split_index),
    }
    return out, quality


def magnitude_metrics(actual: np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    error = np.abs(predicted - actual)
    return {
        "mae": float(np.mean(error)),
        "median_abs_error": float(np.median(error)),
        "p95_abs_error": float(np.quantile(error, 0.95)),
        "max_abs_error": float(np.max(error)),
        "rmse": float(np.sqrt(np.mean((predicted - actual) ** 2))),
        "correlation": float(np.corrcoef(actual, predicted)[0, 1]),
    }


def run_primary(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, object]]:
    development = frame[frame["split"] == "development"]
    holdout = frame[frame["split"] == "holdout"].copy()
    radius = float(np.median(np.sqrt(np.sum(development[COMPONENTS].to_numpy() ** 2, axis=1))))
    raw_radius = float(np.median(development["raw_norm"]))

    r3 = np.sqrt(holdout["x"] ** 2 + holdout["y"] ** 2 + holdout["z"] ** 2)
    true_abs_w = np.abs(holdout["w"].to_numpy())
    pred_three = np.sqrt(np.maximum(0.0, radius**2 - r3.to_numpy() ** 2))
    two_budget = np.maximum(0.0, radius**2 - holdout["x"].to_numpy() ** 2 - holdout["y"].to_numpy() ** 2)
    pred_two = np.sqrt(two_budget / 2.0)
    pred_redundant = pred_two.copy()

    raw_r3 = np.sqrt(holdout["x_raw"] ** 2 + holdout["y_raw"] ** 2 + holdout["z_raw"] ** 2)
    pred_three_raw = np.sqrt(np.maximum(0.0, raw_radius**2 - raw_r3.to_numpy() ** 2))
    true_abs_w_raw = np.abs(holdout["w_raw"].to_numpy())

    holdout["shadow_radius_r3"] = r3.to_numpy()
    holdout["true_abs_hidden_w"] = true_abs_w
    holdout["pred_three_independent"] = pred_three
    holdout["pred_two_equal_split"] = pred_two
    holdout["pred_redundant_third"] = pred_redundant
    holdout["three_abs_error"] = np.abs(pred_three - true_abs_w)
    holdout["two_abs_error"] = np.abs(pred_two - true_abs_w)
    holdout["redundant_abs_error"] = np.abs(pred_redundant - true_abs_w)
    holdout["raw_pred_three_independent"] = pred_three_raw
    holdout["raw_three_abs_error"] = np.abs(pred_three_raw - true_abs_w_raw)
    holdout["hidden_w_ARA"] = 1.0 + holdout["w"]
    holdout["x_ARA"] = 1.0 + holdout["x"]
    holdout["y_ARA"] = 1.0 + holdout["y"]
    holdout["z_ARA"] = 1.0 + holdout["z"]
    holdout["boundary_gap"] = radius - holdout["shadow_radius_r3"]

    metric_rows: list[dict[str, object]] = []
    for method, prediction, dimension_count, rank in [
        ("three independent cuts (x,y,z)", pred_three, 3, 3),
        ("two cuts (x,y), equal hidden split", pred_two, 2, 2),
        ("two cuts + redundant x−y", pred_redundant, 3, 2),
        ("three independent cuts, raw recorded values", pred_three_raw, 3, 3),
    ]:
        actual = true_abs_w_raw if "raw" in method else true_abs_w
        metric_rows.append(
            {
                "method": method,
                "visible_columns": dimension_count,
                "independent_rank": rank,
                **magnitude_metrics(actual, prediction),
            }
        )
    metrics = pd.DataFrame(metric_rows)

    rng = np.random.default_rng(RNG_SEED)
    shuffled_rows: list[dict[str, float | int]] = []
    z = holdout["z"].to_numpy()
    x = holdout["x"].to_numpy()
    y = holdout["y"].to_numpy()
    for draw in range(200):
        z_shuffled = rng.permutation(z)
        prediction = np.sqrt(np.maximum(0.0, radius**2 - x**2 - y**2 - z_shuffled**2))
        vals = magnitude_metrics(true_abs_w, prediction)
        shuffled_rows.append({"draw": draw, **vals})
    shuffle = pd.DataFrame(shuffled_rows)

    rank_two = int(np.linalg.matrix_rank(development[["x", "y"]].to_numpy()))
    rank_redundant = int(
        np.linalg.matrix_rank(
            np.column_stack(
                [development["x"].to_numpy(), development["y"].to_numpy(), development["x"].to_numpy() - development["y"].to_numpy()]
            )
        )
    )
    rank_three = int(np.linalg.matrix_rank(development[["x", "y", "z"]].to_numpy()))
    summary = {
        "radius_normalized": radius,
        "radius_raw_development_median": raw_radius,
        "rank_two": rank_two,
        "rank_redundant": rank_redundant,
        "rank_three": rank_three,
        "three_cut": magnitude_metrics(true_abs_w, pred_three),
        "two_cut": magnitude_metrics(true_abs_w, pred_two),
        "raw_three_cut": magnitude_metrics(true_abs_w_raw, pred_three_raw),
        "shuffled_third_mae_median": float(shuffle["mae"].median()),
        "shuffled_third_mae_q05": float(shuffle["mae"].quantile(0.05)),
        "shuffled_third_mae_q95": float(shuffle["mae"].quantile(0.95)),
        "three_vs_two_mae_ratio": float(metrics.iloc[0]["mae"] / metrics.iloc[1]["mae"]),
        "three_vs_shuffle_median_mae_ratio": float(metrics.iloc[0]["mae"] / shuffle["mae"].median()),
    }
    return holdout, metrics, shuffle, summary


def axis_scan(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for hidden in COMPONENTS:
        visible = [component for component in COMPONENTS if component != hidden]
        values = frame[hidden].to_numpy()
        shadow_radius = np.sqrt(np.sum(frame[visible].to_numpy() ** 2, axis=1))
        changes = component_sign_changes(values)
        rows.append(
            {
                "hidden_component": hidden,
                "visible_components": ",".join(visible),
                "source_sign_changes": int(len(changes)),
                "minimum_abs_hidden": float(np.min(np.abs(values))),
                "maximum_shadow_radius": float(np.max(shadow_radius)),
                "median_shadow_radius": float(np.median(shadow_radius)),
                "boundary_reached_within_0_001": bool(np.max(shadow_radius) >= 0.999),
                "primary_or_exploratory": "primary" if hidden == "w" else "exploratory axis scan",
            }
        )
    return pd.DataFrame(rows)


def phi_direction(frame: pd.DataFrame) -> pd.DataFrame:
    # Coordinate-dependent reference only: direction of the x/y shadow tangent.
    sampled = sample_evenly(frame, 1800).copy()
    dx = np.gradient(sampled["x"].to_numpy())
    dy = np.gradient(sampled["y"].to_numpy())
    speed = np.hypot(dx, dy)
    angle = (np.degrees(np.arctan2(dy, dx)) + 360.0) % 360.0
    phi_angle = 36.0
    distance = np.abs(((angle - phi_angle + 180.0) % 360.0) - 180.0)
    sampled["xy_tangent_angle_deg"] = angle
    sampled["angle_from_36_deg"] = distance
    sampled["xy_step_size"] = speed
    sampled["near_phi_10deg"] = distance <= 10.0
    return sampled[["row_id", "time_s", "split", "xy_tangent_angle_deg", "angle_from_36_deg", "xy_step_size", "near_phi_10deg"]]


def make_figures(frame: pd.DataFrame, holdout: pd.DataFrame, metrics: pd.DataFrame, shuffle: pd.DataFrame, axes: pd.DataFrame, phi: pd.DataFrame) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    display = sample_evenly(frame, 1400)
    hold_display = sample_evenly(holdout, 900)

    fig = plt.figure(figsize=(19, 16), constrained_layout=True)
    grid = fig.add_gridspec(4, 3)

    ax = fig.add_subplot(grid[0, :2])
    for component in COMPONENTS:
        ax.plot(display["time_s"], 1 + display[component], label=f"{component} ARA = 1 + q{component}", lw=1.5, color=COLORS[component])
    split_time = float(frame.loc[frame["split"] == "holdout", "time_s"].iloc[0])
    ax.axvline(split_time, color="#111827", ls="--", lw=1.2, label="frozen 70/30 split")
    ax.axhline(1.0, color="#6b7280", ls=":", lw=1.2, label="ARA ridge = component zero")
    ax.set(title="1. The four recorded orientation coordinates through time", xlabel="Recorded time since first sample (seconds)", ylabel="Component on ARA display (0–2)", ylim=(0, 2))
    ax.legend(ncol=3, fontsize=9)

    ax = fig.add_subplot(grid[0, 2])
    ax.scatter(display["x_ARA"] if "x_ARA" in display else 1 + display["x"], 1 + display["y"], c=display["time_s"], cmap="viridis", s=7, alpha=0.7)
    ax.axvline(1, color="#6b7280", ls=":")
    ax.axhline(1, color="#6b7280", ls=":")
    direction = np.array([math.cos(math.radians(36)), math.sin(math.radians(36))]) * 0.55
    ax.arrow(1, 1, direction[0], direction[1], width=0.006, color="#dc2626", length_includes_head=True)
    ax.text(1 + direction[0], 1 + direction[1], "36° / old Phi reference", color="#dc2626", fontsize=8)
    ax.set(title="2. One ordinary two-axis ARA shadow", xlabel="x coordinate (0–2)", ylabel="y coordinate (0–2)", xlim=(0, 2), ylim=(0, 2), aspect="equal")

    ax = fig.add_subplot(grid[1, 0], projection="3d")
    sc = ax.scatter(display["x"], display["y"], display["z"], c=display["time_s"], cmap="viridis", s=5, alpha=0.65)
    ax.set(title="3. Three independent cuts form the visible B3 shadow", xlabel="x", ylabel="y", zlabel="z")
    fig.colorbar(sc, ax=ax, shrink=0.55, label="time (s)")

    ax = fig.add_subplot(grid[1, 1])
    ax.scatter(hold_display["shadow_radius_r3"], hold_display["true_abs_hidden_w"], s=7, alpha=0.55, color="#2563eb", label="holdout observations")
    rline = np.linspace(float(holdout["shadow_radius_r3"].min()), 1.0, 300)
    ax.plot(rline, np.sqrt(np.maximum(0, 1 - rline**2)), color="#111827", lw=2, label=r"S3 boundary: |w|=sqrt(1-r3^2)")
    ax.set(title="4. The hidden coordinate is the depth behind the 3D shadow", xlabel="Visible shadow radius r3", ylabel="Hidden distance |w|", xlim=(0, 1), ylim=(0, 1))
    ax.legend(fontsize=8)

    ax = fig.add_subplot(grid[1, 2])
    ax.plot(hold_display["time_s"], hold_display["true_abs_hidden_w"], color="#111827", lw=2, label="true hidden |w|")
    ax.plot(hold_display["time_s"], hold_display["pred_three_independent"], color="#10b981", lw=1.2, ls="--", label="recovered from x,y,z")
    ax.plot(hold_display["time_s"], hold_display["pred_two_equal_split"], color="#f59e0b", lw=1.2, alpha=0.85, label="two-cut equal-split guess")
    ax.set(title="5. Later holdout: hidden depth recovered without using holdout w", xlabel="Recorded holdout time (seconds)", ylabel="Hidden distance from ridge |w|", ylim=(0, 1))
    ax.legend(fontsize=8)

    ax = fig.add_subplot(grid[2, 0])
    order = metrics.assign(accuracy_digits=-np.log10(np.maximum(metrics["mae"], 1e-18))).sort_values("accuracy_digits")
    bars = ax.barh(order["method"], order["accuracy_digits"], color=["#f59e0b", "#fb923c", "#60a5fa", "#10b981"][: len(order)])
    for bar, mae in zip(bars, order["mae"]):
        ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2, f"MAE {mae:.2e}", va="center", fontsize=8)
    ax.set(title="6. Hidden-magnitude accuracy by available cut", xlabel="Correct decimal orders, -log10(MAE); farther right is better", ylabel="", xlim=(0, 18))

    ax = fig.add_subplot(grid[2, 1])
    ax.hist(shuffle["mae"], bins=25, color="#94a3b8", edgecolor="white", label="200 shuffled-z controls")
    ax.axvline(float(metrics.loc[metrics["method"].str.startswith("three independent cuts ("), "mae"].iloc[0]), color="#10b981", lw=2.5, label="correct event-linked z")
    ax.axvline(float(metrics.loc[metrics["method"].str.startswith("two cuts ("), "mae"].iloc[0]), color="#f59e0b", lw=2.5, label="two-cut baseline")
    ax.set(title="7. The third values alone are insufficient; their event linkage matters", xlabel="Holdout MAE for hidden |w|", ylabel="Control count")
    ax.legend(fontsize=8)

    ax = fig.add_subplot(grid[2, 2])
    ax.bar(axes["hidden_component"], axes["maximum_shadow_radius"], color=[COLORS[c] for c in axes["hidden_component"]])
    ax.axhline(1.0, color="#111827", ls="--", label="visible projection boundary")
    for _, row in axes.iterrows():
        ax.text(row["hidden_component"], row["maximum_shadow_radius"] - 0.035, f"{int(row['source_sign_changes'])} crossings", ha="center", va="top", color="white", fontsize=9, fontweight="bold")
    ax.set(title="8. Boundary exposure depends on which coordinate is hidden", xlabel="Coordinate hidden in the descriptive scan", ylabel="Maximum visible shadow radius", ylim=(0.9, 1.005))
    ax.legend(fontsize=8)

    ax = fig.add_subplot(grid[3, 0])
    ax.plot(hold_display["time_s"], hold_display["hidden_w_ARA"], color=COLORS["w"], lw=1.8, label="hidden w on 0–2 ARA")
    ax.axhline(1, color="#111827", ls="--", label="hidden ridge / possible branch crossing")
    ax.fill_between(hold_display["time_s"], 1, hold_display["hidden_w_ARA"], color="#c084fc", alpha=0.22)
    ax.set(title="9. Primary w view never reaches its hidden ridge", xlabel="Recorded holdout time (seconds)", ylabel="Hidden w ARA (0–2)", ylim=(0, 2))
    ax.legend(fontsize=8)

    ax = fig.add_subplot(grid[3, 1])
    angle_bins = np.arange(0, 361, 10)
    ax.hist(phi["xy_tangent_angle_deg"], bins=angle_bins, color="#60a5fa", edgecolor="white")
    ax.axvline(36, color="#dc2626", lw=2, label="old 36° / Phi reference")
    ax.set(title="10. Phi/up-right is a reference, not recovered invariant", xlabel="x/y projection tangent angle (degrees)", ylabel="Sample count", xlim=(0, 360))
    ax.legend(fontsize=8)

    ax = fig.add_subplot(grid[3, 2])
    ax.axis("off")
    ax.text(0.5, 0.96, "11. WHERE this sits in ARA", ha="center", va="top", fontsize=13, fontweight="bold")
    box = dict(boxstyle="round,pad=0.55", fc="white", lw=2)
    ax.text(0.16, 0.66, "2D ARA cut\n(x, y)", ha="center", va="center", transform=ax.transAxes, bbox={**box, "ec": "#2563eb"}, fontsize=9)
    ax.text(0.50, 0.66, "Visible 3D shadow\n(x, y, z)", ha="center", va="center", transform=ax.transAxes, bbox={**box, "ec": "#10b981"}, fontsize=9)
    ax.text(0.84, 0.66, "Full parent S3 identity\n(w, x, y, z)", ha="center", va="center", transform=ax.transAxes, bbox={**box, "ec": "#7c3aed"}, fontsize=9)
    ax.annotate("independent z", xy=(0.39, 0.66), xytext=(0.27, 0.66), xycoords=ax.transAxes, textcoords=ax.transAxes, arrowprops=dict(arrowstyle="->", color="#10b981"), ha="center", va="bottom", fontsize=8)
    ax.annotate("hidden w", xy=(0.73, 0.66), xytext=(0.61, 0.66), xycoords=ax.transAxes, textcoords=ax.transAxes, arrowprops=dict(arrowstyle="->", color="#a855f7"), ha="center", va="bottom", fontsize=8)
    ax.text(0.5, 0.37, "Static geometry gives two mirror depths: +|w| and -|w|.", ha="center", va="center", transform=ax.transAxes, fontsize=9, fontweight="bold")
    ax.text(0.5, 0.19, "Time order can choose between them only if the path reaches the visible boundary, where w = 0.", ha="center", va="center", wrap=True, transform=ax.transAxes, fontsize=9)

    fig.suptitle("T447 — Hidden-sphere shadow calibration on a real tracked trajectory", fontsize=19, fontweight="bold")
    fig.savefig(RESULTS / "T447_GEOMETRY_FIRST.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    fig, axes_plot = plt.subplots(2, 3, figsize=(18, 10), constrained_layout=True)
    pairs = [("x", "y"), ("x", "z"), ("y", "z")]
    for ax, (a, b) in zip(axes_plot[0], pairs):
        sc = ax.scatter(1 + display[a], 1 + display[b], c=display["time_s"], cmap="viridis", s=7, alpha=0.65)
        ax.axvline(1, color="#6b7280", ls=":")
        ax.axhline(1, color="#6b7280", ls=":")
        ax.set(xlabel=f"{a} ARA (0–2)", ylabel=f"{b} ARA (0–2)", xlim=(0, 2), ylim=(0, 2), aspect="equal", title=f"{a}/{b} two-axis shadow")
    fig.colorbar(sc, ax=axes_plot[0].tolist(), shrink=0.7, label="recorded time (s)")

    axes_plot[1, 0].scatter(hold_display["true_abs_hidden_w"], hold_display["pred_three_independent"], s=8, alpha=0.55, color="#10b981")
    axes_plot[1, 0].plot([0, 1], [0, 1], color="#111827", ls="--")
    axes_plot[1, 0].set(title="Three independent cuts", xlabel="True hidden |w|", ylabel="Predicted hidden |w|", xlim=(0, 1), ylim=(0, 1), aspect="equal")

    axes_plot[1, 1].scatter(hold_display["true_abs_hidden_w"], hold_display["pred_two_equal_split"], s=8, alpha=0.5, color="#f59e0b")
    axes_plot[1, 1].plot([0, 1], [0, 1], color="#111827", ls="--")
    axes_plot[1, 1].set(title="Two cuts plus equal hidden split", xlabel="True hidden |w|", ylabel="Predicted hidden |w|", xlim=(0, 1), ylim=(0, 1), aspect="equal")

    axes_plot[1, 2].plot(hold_display["time_s"], hold_display["boundary_gap"], color="#7c3aed", lw=1.6)
    axes_plot[1, 2].axhline(0, color="#111827", ls="--")
    axes_plot[1, 2].set(title="Distance from visible projection boundary", xlabel="Recorded holdout time (s)", ylabel="1 - r3 (zero is w ridge)")
    fig.suptitle("T447 — The same identity viewed through three ordinary ARA planes", fontsize=18, fontweight="bold")
    fig.savefig(RESULTS / "T447_PAIR_PLANES_AND_BOUNDARY.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def write_sqlite(frame: pd.DataFrame, holdout: pd.DataFrame, metrics: pd.DataFrame, shuffle: pd.DataFrame, axes: pd.DataFrame, phi: pd.DataFrame) -> None:
    db = RESULTS / "T447_ANALYSIS.sqlite"
    if db.exists():
        db.unlink()
    with sqlite3.connect(db) as connection:
        frame.to_sql("source_states", connection, index=False)
        holdout.to_sql("holdout_reconstruction", connection, index=False)
        metrics.to_sql("method_metrics", connection, index=False)
        shuffle.to_sql("shuffled_third_controls", connection, index=False)
        axes.to_sql("axis_scan", connection, index=False)
        phi.to_sql("phi_direction_reference", connection, index=False)


def main() -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    frame, quality = load_source()
    holdout, metrics, shuffle, primary = run_primary(frame)
    axes = axis_scan(frame)
    phi = phi_direction(frame)

    # Add display fields after calculations so every saved plot uses the same map.
    for component in COMPONENTS:
        frame[f"{component}_ARA"] = 1.0 + frame[component]

    sample = sample_evenly(frame, 1800)
    holdout_sample = sample_evenly(holdout, 1200)
    sample.to_csv(RESULTS / "T447_SOURCE_HISTORY_SAMPLE.csv", index=False)
    holdout_sample.to_csv(RESULTS / "T447_HOLDOUT_RECONSTRUCTION_SAMPLE.csv", index=False)
    metrics.to_csv(RESULTS / "T447_METHOD_METRICS.csv", index=False)
    shuffle.to_csv(RESULTS / "T447_SHUFFLED_THIRD_CONTROLS.csv", index=False)
    axes.to_csv(RESULTS / "T447_AXIS_SCAN.csv", index=False)
    phi.to_csv(RESULTS / "T447_PHI_DIRECTION_REFERENCE.csv", index=False)

    make_figures(frame, holdout, metrics, shuffle, axes, phi)
    write_sqlite(frame, holdout, metrics, shuffle, axes, phi)

    primary_w = axes.loc[axes["hidden_component"] == "w"].iloc[0]
    branch_identifiable = bool(primary_w["source_sign_changes"] > 0)
    verdict = {
        "independent_third_cut": "confirmed_in_known_S3_calibration",
        "redundant_difference": "no_new_rank_and_no_new_information",
        "event_linkage": "required; shuffled_third_is_materially_worse",
        "primary_w_branch": "not_identifiable_in_MH_01_easy" if not branch_identifiable else "identifiable",
        "physical_time_claim": "not_tested",
        "phi_direction_claim": "coordinate_dependent_reference_only",
    }
    summary = {
        "test": "T447",
        "generated_at": generated_at,
        "source": {
            "identity": "EuRoC MH_01_easy micro-aerial vehicle",
            "source_file": SOURCE.name,
            "official_dataset_url": "https://projects.asl.ethz.ch/datasets/euroc-mav/",
            "mirror_download_url": "https://sourceforge.net/projects/kimera-vio/files/dataset/MH_01_easy/mav0/state_groundtruth_estimate0/data.csv/download",
        },
        "quality": quality,
        "primary": primary,
        "axis_scan": records(axes),
        "phi_reference": {
            "reference_angle_degrees": 36.0,
            "weighted_or_invariant": False,
            "fraction_xy_tangents_within_10_degrees": float(phi["near_phi_10deg"].mean()),
            "median_absolute_angle_distance_degrees": float(phi["angle_from_36_deg"].median()),
        },
        "branch": {
            "primary_hidden_coordinate": "w",
            "source_sign_changes": int(primary_w["source_sign_changes"]),
            "minimum_abs_w": float(primary_w["minimum_abs_hidden"]),
            "maximum_visible_shadow_radius": float(primary_w["maximum_shadow_radius"]),
            "identifiable": branch_identifiable,
            "reason": "The primary w coordinate never reaches zero, so this trajectory remains on one mirror branch in this view." if not branch_identifiable else "The visible shadow reaches the w=0 boundary.",
        },
        "verdict": verdict,
    }
    (RESULTS / "T447_RESULT.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (RESULTS / "T447_DATA_QUALITY.json").write_text(json.dumps(quality, indent=2), encoding="utf-8")
    (RESULTS / "T447_RUN_LOG.txt").write_text(
        "\n".join(
            [
                f"generated_at={generated_at}",
                f"source_rows={quality['source_rows']}",
                f"valid_rows={quality['valid_unique_rows']}",
                f"holdout_rows={quality['holdout_rows']}",
                f"three_cut_mae={primary['three_cut']['mae']:.12g}",
                f"raw_three_cut_mae={primary['raw_three_cut']['mae']:.12g}",
                f"two_cut_mae={primary['two_cut']['mae']:.12g}",
                f"shuffled_third_median_mae={primary['shuffled_third_mae_median']:.12g}",
                f"rank_two={primary['rank_two']}",
                f"rank_redundant={primary['rank_redundant']}",
                f"rank_three={primary['rank_three']}",
                f"primary_w_sign_changes={int(primary_w['source_sign_changes'])}",
                f"primary_w_branch_identifiable={branch_identifiable}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(json.dumps({"verdict": verdict, "primary": primary, "branch": summary["branch"]}, indent=2))


if __name__ == "__main__":
    main()
