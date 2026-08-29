"""T426: frozen macro-handover sequence on the T424 hourglass holdout."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
T424_RESULTS = HERE.parent / "T424_hourglass_handover" / "results"
PROTOCOL = HERE / "T426_FROZEN_PROTOCOL.md"
EXPECTED_PROTOCOL_SHA256 = "72B932779A2E46EAD291AABE6D2BE21868C937D0A6EEE15DFFBCA8E22D013638"

PERSISTENCE = 3
NULL_REPLICATES = 10_000
RNG_SEED = 42620260824
GRID = np.linspace(0.0, 1.0, 101)

BLUE = "#4c78a8"
GOLD = "#d79a2b"
ORANGE = "#f28e2b"
OLIVE = "#6f8f61"
PINK = "#d88390"
INK = "#252a31"
GREY = "#68717b"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def preclosure(group: pd.DataFrame) -> pd.DataFrame:
    group = group.sort_values("frame").reset_index(drop=True)
    closure = min(int(group["closure_index"].iloc[0]), len(group) - 1)
    return group.iloc[: closure + 1].copy().reset_index(drop=True)


def persistent_starts(mask: np.ndarray, width: int = PERSISTENCE) -> np.ndarray:
    mask = np.asarray(mask, dtype=bool)
    if len(mask) < width:
        return np.array([], dtype=int)
    windows = np.convolve(mask.astype(int), np.ones(width, dtype=int), mode="valid")
    return np.flatnonzero(windows == width)


def score_sequence(
    x: np.ndarray, y: np.ndarray, onset: int, persistence: int = PERSISTENCE
) -> dict[str, object]:
    n = len(x)
    connection = (x < 1.0) & (y > 1.0)
    movement = (x > 1.0) & (y < 1.0)
    connection_starts = persistent_starts(connection, persistence)
    movement_starts = persistent_starts(movement, persistence)

    pre = connection_starts[connection_starts + persistence - 1 < onset]
    pre_index = int(pre[-1]) if len(pre) else None

    opening = bool(
        0 <= onset < n
        and abs(float(x[onset]) - 0.5) <= 0.25
        and abs(float(y[onset]) - 1.5) <= 0.25
    )

    post_move = movement_starts[movement_starts > onset]
    move_index = int(post_move[0]) if len(post_move) else None

    reclose_index = None
    if move_index is not None:
        after_move = connection_starts[
            connection_starts > move_index + persistence - 1
        ]
        if len(after_move):
            reclose_index = int(after_move[0])

    complete = bool(
        pre_index is not None
        and opening
        and move_index is not None
        and reclose_index is not None
    )
    return {
        "pre_connection_index": pre_index,
        "opening_in_box": opening,
        "movement_index": move_index,
        "reclosure_index": reclose_index,
        "complete_loop": complete,
    }


def history_for_run(group: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    history = preclosure(group)
    active = np.flatnonzero(history["direct_active"].to_numpy(int) == 1)
    if not len(active):
        raise RuntimeError(f"No direct onset inside pre-closure history for {history['run_id'].iloc[0]}")
    return history, int(active[0])


def stage_record(history: pd.DataFrame, onset: int, score: dict[str, object]) -> dict[str, object]:
    n = len(history)
    run_id = str(history["run_id"].iloc[0])
    x = history["x_trav"].to_numpy(float)
    y = history["x_conn"].to_numpy(float)

    def value(index: int | None, field: str) -> float | int | None:
        if index is None:
            return None
        if field == "fraction":
            return float(index / max(1, n - 1))
        if field == "index":
            return int(index)
        return history.iloc[index][field]

    move = score["movement_index"]
    reclose = score["reclosure_index"]
    opening_distance = float(np.hypot(x[onset] - 0.5, y[onset] - 1.5))
    return {
        "run_id": run_id,
        "video": str(history["video"].iloc[0]),
        "gravity_index": int(history["gravity_index"].iloc[0]),
        "fps": float(history["fps"].iloc[0]),
        "frames_preclosure": n,
        "complete_loop": bool(score["complete_loop"]),
        "pre_connection_found": score["pre_connection_index"] is not None,
        "opening_in_box": bool(score["opening_in_box"]),
        "movement_found": move is not None,
        "reclosure_found": reclose is not None,
        "pre_connection_index": value(score["pre_connection_index"], "index"),
        "pre_connection_fraction": value(score["pre_connection_index"], "fraction"),
        "opening_index": onset,
        "opening_frame": int(history.iloc[onset]["frame"]),
        "opening_time_s": float(history.iloc[onset]["run_time_s"]),
        "opening_fraction": float(onset / max(1, n - 1)),
        "opening_x_trav": float(x[onset]),
        "opening_x_conn": float(y[onset]),
        "opening_s_joint": float((x[onset] + y[onset]) / 2.0),
        "opening_distance_to_0_5_1_5": opening_distance,
        "movement_index": value(move, "index"),
        "movement_frame": value(move, "frame"),
        "movement_time_s": value(move, "run_time_s"),
        "movement_fraction": value(move, "fraction"),
        "movement_x_trav": float(x[move]) if move is not None else None,
        "movement_x_conn": float(y[move]) if move is not None else None,
        "reclosure_index": value(reclose, "index"),
        "reclosure_frame": value(reclose, "frame"),
        "reclosure_time_s": value(reclose, "run_time_s"),
        "reclosure_fraction": value(reclose, "fraction"),
        "reclosure_x_trav": float(x[reclose]) if reclose is not None else None,
        "reclosure_x_conn": float(y[reclose]) if reclose is not None else None,
        "closure_frame": int(history.iloc[-1]["frame"]),
        "closure_time_s": float(history.iloc[-1]["run_time_s"]),
        "movement_to_reclosure_s": (
            float(history.iloc[reclose]["run_time_s"] - history.iloc[move]["run_time_s"])
            if move is not None and reclose is not None else None
        ),
        "opening_to_movement_s": (
            float(history.iloc[move]["run_time_s"] - history.iloc[onset]["run_time_s"])
            if move is not None else None
        ),
        "reclosure_to_closure_s": (
            float(history.iloc[-1]["run_time_s"] - history.iloc[reclose]["run_time_s"])
            if reclose is not None else None
        ),
    }


def interpolate_curves(histories: list[pd.DataFrame]) -> dict[str, np.ndarray]:
    x_curves = []
    y_curves = []
    for history in histories:
        native = np.linspace(0.0, 1.0, len(history))
        x_curves.append(np.interp(GRID, native, history["x_trav"].to_numpy(float)))
        y_curves.append(np.interp(GRID, native, history["x_conn"].to_numpy(float)))
    x_stack = np.vstack(x_curves)
    y_stack = np.vstack(y_curves)
    return {
        "fraction": GRID,
        "x": np.median(x_stack, axis=0),
        "x_lo": np.quantile(x_stack, 0.25, axis=0),
        "x_hi": np.quantile(x_stack, 0.75, axis=0),
        "y": np.median(y_stack, axis=0),
        "y_lo": np.quantile(y_stack, 0.25, axis=0),
        "y_hi": np.quantile(y_stack, 0.75, axis=0),
    }


def run_nulls(
    run_arrays: list[tuple[np.ndarray, np.ndarray, int]], rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    pseudo_counts = np.zeros(NULL_REPLICATES, dtype=int)
    shift_counts = np.zeros(NULL_REPLICATES, dtype=int)
    conditional_box_counts = np.zeros(NULL_REPLICATES, dtype=int)
    reverse_count = 0

    for x, y, onset in run_arrays:
        n = len(x)
        eligible = np.arange(PERSISTENCE, max(PERSISTENCE + 1, n - 2 * PERSISTENCE))
        if not len(eligible):
            raise RuntimeError("Run is too short for frozen pseudo-onset control")
        pseudo_onsets = rng.choice(eligible, size=NULL_REPLICATES, replace=True)
        in_box = eligible[
            (np.abs(x[eligible] - 0.5) <= 0.25)
            & (np.abs(y[eligible] - 1.5) <= 0.25)
        ]
        if not len(in_box):
            raise RuntimeError("Run has no eligible frame inside the frozen opening box")
        conditional_onsets = rng.choice(in_box, size=NULL_REPLICATES, replace=True)
        shifts = rng.integers(1, n, size=NULL_REPLICATES)
        for replicate in range(NULL_REPLICATES):
            pseudo_counts[replicate] += int(score_sequence(x, y, int(pseudo_onsets[replicate]))["complete_loop"])
            conditional_box_counts[replicate] += int(
                score_sequence(x, y, int(conditional_onsets[replicate]))["complete_loop"]
            )
            shifted_x = np.roll(x, int(shifts[replicate]))
            shifted_y = np.roll(y, int(shifts[replicate]))
            shift_counts[replicate] += int(score_sequence(shifted_x, shifted_y, onset)["complete_loop"])

        reversed_score = score_sequence(x[::-1], y[::-1], n - 1 - onset)
        reverse_count += int(reversed_score["complete_loop"])

    return pseudo_counts, shift_counts, conditional_box_counts, reverse_count


def persistence_sensitivity(
    run_arrays: list[tuple[np.ndarray, np.ndarray, int]], widths: tuple[int, ...] = (1, 3, 5, 8)
) -> dict[str, int]:
    """Post-freeze diagnostic only; the frozen primary width remains three frames."""
    return {
        str(width): int(sum(score_sequence(x, y, onset, width)["complete_loop"]
                            for x, y, onset in run_arrays))
        for width in widths
    }


def empirical_p(null: np.ndarray, observed: int) -> float:
    return float((1 + np.sum(null >= observed)) / (1 + len(null)))


def add_plane_guides(ax: plt.Axes) -> None:
    ax.axvline(1.0, color=GREY, linestyle="--", linewidth=1.0)
    ax.axhline(1.0, color=GREY, linestyle="--", linewidth=1.0)
    ax.add_patch(Rectangle((0.25, 1.25), 0.5, 0.5, fill=False, edgecolor=GOLD,
                           linewidth=1.8, linestyle="--"))
    ax.scatter([0.5], [1.5], marker="+", s=100, linewidth=2.0, color=GOLD, zorder=8)
    ax.set(xlim=(0, 2), ylim=(0, 2))
    ax.set_aspect("equal", adjustable="box")
    ax.grid(alpha=0.15)


def median_stage_fractions(stage: pd.DataFrame) -> dict[str, float]:
    passed = stage[stage["complete_loop"]].copy()
    if passed.empty:
        passed = stage.copy()
    result = {
        "opening": float(passed["opening_fraction"].median()),
        "movement": float(passed["movement_fraction"].dropna().median()),
        "reclosure": float(passed["reclosure_fraction"].dropna().median()),
    }
    return result


def plot_summary(
    curves: dict[str, np.ndarray], stage: pd.DataFrame,
    pseudo: np.ndarray, shift: np.ndarray, conditional_box: np.ndarray,
    reverse_count: int,
    observed: int, output: Path,
) -> None:
    stage_fraction = median_stage_fractions(stage)
    fig, axes = plt.subplots(2, 2, figsize=(16.5, 12.0), constrained_layout=True)
    fig.suptitle("T426 — main hourglass Irrationality Di-ARA macro-handover", fontsize=21)

    ax = axes[0, 0]
    f = curves["fraction"]
    ax.fill_between(f, curves["x_lo"], curves["x_hi"], color=BLUE, alpha=0.16)
    ax.plot(f, curves["x"], color=BLUE, linewidth=2.5, label="C1 movement / traversal")
    ax.fill_between(f, curves["y_lo"], curves["y_hi"], color=GOLD, alpha=0.16)
    ax.plot(f, curves["y"], color=ORANGE, linewidth=2.5, label="C2 connection / packing")
    ax.axhline(1.0, color=GREY, linestyle="--", linewidth=1.0, label="ARA ridge")
    stage_style = {
        "opening": (GOLD, "D"),
        "movement": (BLUE, "^"),
        "reclosure": (OLIVE, "s"),
    }
    for label, fraction in stage_fraction.items():
        color, marker = stage_style[label]
        ax.axvline(fraction, color=color, linestyle=":", linewidth=1.3)
        ax.scatter([fraction], [np.interp(fraction, f, curves["x"])], marker=marker,
                   color=BLUE, edgecolor="white", s=75, zorder=6)
        ax.scatter([fraction], [np.interp(fraction, f, curves["y"])], marker=marker,
                   color=ORANGE, edgecolor="white", s=75, zorder=6,
                   label=f"median {label}")
    ax.set(xlim=(0, 1), ylim=(0, 2), xlabel="Fraction of discharge-to-closure history",
           ylabel="Independent ARA coordinate (0–2)")
    ax.set_title("Median histories; band = middle 50% of 16 held-out runs")
    ax.grid(alpha=0.18)
    ax.legend(frameon=False, fontsize=9, ncol=2)

    ax = axes[0, 1]
    ax.plot(curves["x"], curves["y"], color=INK, linewidth=2.5, label="median path")
    arrow_indices = np.arange(8, len(f) - 1, 12)
    for index in arrow_indices:
        ax.annotate("", xy=(curves["x"][index + 1], curves["y"][index + 1]),
                    xytext=(curves["x"][index - 1], curves["y"][index - 1]),
                    arrowprops=dict(arrowstyle="->", color=INK, lw=1.2))
    for label, fraction in stage_fraction.items():
        color, marker = stage_style[label]
        px = np.interp(fraction, f, curves["x"])
        py = np.interp(fraction, f, curves["y"])
        ax.scatter(px, py, marker=marker, s=115, color=color, edgecolor="white",
                   linewidth=0.9, label=label, zorder=8)
    add_plane_guides(ax)
    ax.set(xlabel="C1 movement / traversal ARA (0–2)",
           ylabel="C2 connection / packing ARA (0–2)")
    ax.set_title("Median directed Di-ARA trajectory and frozen opening box")
    ax.legend(frameon=False, fontsize=9, loc="lower left")

    ax = axes[1, 0]
    ordered = stage.sort_values(["video", "gravity_index"]).reset_index(drop=True)
    y_pos = np.arange(len(ordered))
    for row, record in ordered.iterrows():
        values = [record["opening_fraction"], record["movement_fraction"], record["reclosure_fraction"]]
        finite = [float(value) for value in values if pd.notna(value)]
        if finite:
            ax.plot([min(finite), max(finite)], [row, row], color="#c4c9ce", linewidth=1.5)
        for value, color, marker in zip(values, [GOLD, BLUE, OLIVE], ["D", "^", "s"]):
            if pd.notna(value):
                ax.scatter(float(value), row, color=color, marker=marker, s=55,
                           edgecolor="white", linewidth=0.6, zorder=4)
    labels = [f"{r.video.replace('SN103_ToyouraSand_', '').replace('.mp4', '')} · g{r.gravity_index}"
              for r in ordered.itertuples()]
    ax.set_yticks(y_pos, labels)
    ax.invert_yaxis()
    ax.set(xlim=(0, 1), xlabel="Fraction of each run's pre-closure history")
    ax.set_title("Per-run stage order: opening ◆, movement ▲, reclosure ■")
    ax.grid(axis="x", alpha=0.18)

    ax = axes[1, 1]
    bins = np.arange(-0.5, 16.6, 1.0)
    ax.hist(pseudo, bins=bins, alpha=0.55, color=GOLD, edgecolor="white", label="random pseudo-onset")
    ax.hist(shift, bins=bins, alpha=0.48, color=BLUE, edgecolor="white", label="joint path shifted")
    ax.hist(conditional_box, bins=bins, histtype="step", linewidth=2.2, color=OLIVE,
            label="post-freeze: random frame inside opening box")
    ax.axvline(reverse_count, color=PINK, linestyle=":", linewidth=2.2,
               label=f"time reversed = {reverse_count}/16")
    ax.axvline(observed, color=INK, linewidth=2.6, label=f"observed = {observed}/16")
    ax.set(xlim=(-0.5, 16.5), xlabel="Runs completing the frozen four-stage loop",
           ylabel="Null replicate count")
    ax.set_title(f"Matched controls · 10,000 replicates · seed {RNG_SEED}")
    ax.legend(frameon=False, fontsize=9)
    ax.grid(axis="y", alpha=0.18)

    fig.savefig(output, dpi=180, facecolor="white")
    plt.close(fig)


def plot_gallery(histories: list[pd.DataFrame], stage: pd.DataFrame, output: Path) -> None:
    stage_by_run = stage.set_index("run_id")
    fig, axes = plt.subplots(4, 4, figsize=(16, 16), constrained_layout=True)
    fig.suptitle(
        "T426 — every held-out hourglass trajectory\n"
        "◆ opening · ▲ movement excursion · ■ connection reclosure",
        fontsize=20,
    )
    for ax, history in zip(axes.ravel(), histories):
        run_id = str(history["run_id"].iloc[0])
        record = stage_by_run.loc[run_id]
        x = history["x_trav"].to_numpy(float)
        y = history["x_conn"].to_numpy(float)
        ax.plot(x, y, color="#aab1b8", linewidth=1.2)
        for index in np.arange(6, len(history) - 1, max(8, len(history) // 8)):
            ax.annotate("", xy=(x[index + 1], y[index + 1]), xytext=(x[index - 1], y[index - 1]),
                        arrowprops=dict(arrowstyle="->", color=GREY, lw=0.9))
        markers = [
            (record["opening_index"], GOLD, "D"),
            (record["movement_index"], BLUE, "^"),
            (record["reclosure_index"], OLIVE, "s"),
        ]
        for index, color, marker in markers:
            if pd.notna(index):
                index = int(index)
                ax.scatter(x[index], y[index], color=color, marker=marker, s=45,
                           edgecolor="white", linewidth=0.5, zorder=5)
        add_plane_guides(ax)
        status = "PASS" if bool(record["complete_loop"]) else "incomplete"
        short = run_id.replace("SN103_ToyouraSand_", "").replace("_g", " · g")
        ax.set_title(f"{short} — {status}", fontsize=10)
        ax.tick_params(labelsize=8)
    for row in range(4):
        axes[row, 0].set_ylabel("C2 connection ARA")
    for column in range(4):
        axes[-1, column].set_xlabel("C1 movement ARA")
    fig.savefig(output, dpi=175, facecolor="white")
    plt.close(fig)


def main() -> None:
    if sha256(PROTOCOL) != EXPECTED_PROTOCOL_SHA256:
        raise RuntimeError("Frozen T426 protocol hash mismatch")
    RESULTS.mkdir(parents=True, exist_ok=True)

    frame = pd.read_csv(T424_RESULTS / "T424_HOLDOUT_ARA_COORDINATES.csv")
    histories: list[pd.DataFrame] = []
    stage_rows: list[dict[str, object]] = []
    run_arrays: list[tuple[np.ndarray, np.ndarray, int]] = []

    for _, group in frame.groupby("run_id", sort=False):
        history, onset = history_for_run(group)
        x = history["x_trav"].to_numpy(float)
        y = history["x_conn"].to_numpy(float)
        score = score_sequence(x, y, onset)
        histories.append(history)
        stage_rows.append(stage_record(history, onset, score))
        run_arrays.append((x, y, onset))

    stage = pd.DataFrame(stage_rows)
    observed = int(stage["complete_loop"].sum())
    rng = np.random.default_rng(RNG_SEED)
    pseudo, shift, conditional_box, reverse_count = run_nulls(run_arrays, rng)
    pseudo_p = empirical_p(pseudo, observed)
    shift_p = empirical_p(shift, observed)
    conditional_box_p = empirical_p(conditional_box, observed)
    sensitivity = persistence_sensitivity(run_arrays)
    primary_pass = bool(
        observed >= 12
        and pseudo_p < 0.05
        and shift_p < 0.05
        and observed > reverse_count
    )

    stage.to_csv(RESULTS / "T426_RUN_STAGE_REGISTER.csv", index=False)
    pd.DataFrame({"replicate": np.arange(NULL_REPLICATES),
                  "pseudo_onset_completed_runs": pseudo,
                  "joint_shift_completed_runs": shift,
                  "conditional_in_box_completed_runs": conditional_box}).to_csv(
        RESULTS / "T426_NULL_DISTRIBUTIONS.csv", index=False
    )

    curves = interpolate_curves(histories)
    plot_summary(curves, stage, pseudo, shift, conditional_box, reverse_count, observed,
                 RESULTS / "T426_MAIN_HANDOVER_SUMMARY.png")
    plot_gallery(histories, stage, RESULTS / "T426_ALL_RUN_TRAJECTORIES.png")

    completed = stage[stage["complete_loop"]]
    summary = {
        "status": "STRUCTURAL_GATE_PASS" if primary_pass else "STRUCTURAL_GATE_FAIL",
        "protocol_sha256": EXPECTED_PROTOCOL_SHA256,
        "runs": int(len(stage)),
        "complete_loops": observed,
        "complete_loop_fraction": float(observed / len(stage)),
        "stage_counts": {
            "pre_connection": int(stage["pre_connection_found"].sum()),
            "opening_in_frozen_box": int(stage["opening_in_box"].sum()),
            "movement_excursion": int(stage["movement_found"].sum()),
            "connection_reclosure": int(stage["reclosure_found"].sum()),
        },
        "median_stage_history_fractions_complete_runs": {
            "opening": float(completed["opening_fraction"].median()) if len(completed) else None,
            "movement": float(completed["movement_fraction"].median()) if len(completed) else None,
            "reclosure": float(completed["reclosure_fraction"].median()) if len(completed) else None,
        },
        "median_opening_coordinates": {
            "x_trav": float(stage["opening_x_trav"].median()),
            "x_conn": float(stage["opening_x_conn"].median()),
            "s_joint": float(stage["opening_s_joint"].median()),
            "distance_to_0_5_1_5": float(stage["opening_distance_to_0_5_1_5"].median()),
        },
        "median_movement_to_reclosure_s": float(completed["movement_to_reclosure_s"].median()) if len(completed) else None,
        "median_opening_to_movement_s": float(completed["opening_to_movement_s"].median()) if len(completed) else None,
        "median_reclosure_to_terminal_closure_s": float(completed["reclosure_to_closure_s"].median()) if len(completed) else None,
        "null_controls": {
            "pseudo_onset_mean_completed_runs": float(np.mean(pseudo)),
            "pseudo_onset_95pct_completed_runs": float(np.quantile(pseudo, 0.95)),
            "pseudo_onset_empirical_p": pseudo_p,
            "joint_shift_mean_completed_runs": float(np.mean(shift)),
            "joint_shift_95pct_completed_runs": float(np.quantile(shift, 0.95)),
            "joint_shift_empirical_p": shift_p,
            "conditional_in_box_mean_completed_runs": float(np.mean(conditional_box)),
            "conditional_in_box_95pct_completed_runs": float(np.quantile(conditional_box, 0.95)),
            "conditional_in_box_empirical_p": conditional_box_p,
            "time_reversal_completed_runs": reverse_count,
        },
        "post_freeze_persistence_sensitivity_complete_runs": sensitivity,
        "primary_gate_pass": primary_pass,
        "interpretation_boundary": (
            "Tests the frozen T424 macro-handover order; does not establish a universal quadrant sequence or causality."
        ),
    }
    (RESULTS / "T426_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
