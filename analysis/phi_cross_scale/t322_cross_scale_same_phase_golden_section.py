"""T322: cross-scale same-phase golden-section test.

This deliberately excludes the intervening opposite-phase turn from the
measured object.  The primary observable is the elapsed time from one turning
point to the next turning point of the same sign, compared across adjacent
pendulum-arm scales.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import pathlib
import sys
from dataclasses import asdict, dataclass

import numpy as np
from scipy.signal import find_peaks


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PENDULUM = ROOT / "analysis" / "pendulum_scripts"
sys.path.insert(0, str(PENDULUM))
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(HERE / ".mplconfig"))

import matplotlib.pyplot as plt

from pendulum_common import DATA_DIR, DRIVEN, RUNS, load_triple, load_triple_driven, rest_centered


TEST_ID = "T322-CROSS-SCALE-SAME-PHASE-GOLDEN-SECTION-v1"
PROTOCOL = HERE / "T322_CROSS_SCALE_SAME_PHASE_GOLDEN_SECTION_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA256 = "8e47f1c4bed2641e63bb959293ad1d197abbff1ccf52415741cd96f0f470b79a"
RESULTS = HERE / "T322_CROSS_SCALE_SAME_PHASE_GOLDEN_SECTION_RESULTS.json"
EVENTS = HERE / "T322_CROSS_SCALE_SAME_PHASE_GOLDEN_SECTION_EVENTS.csv"
FIGURE = HERE / "T322_CROSS_SCALE_SAME_PHASE_GOLDEN_SECTION.png"
FIGURE_SVG = HERE / "T322_CROSS_SCALE_SAME_PHASE_GOLDEN_SECTION.svg"
SCALE_FIGURE = HERE / "T322A_POSTHOC_SAME_PHASE_SCALE_RATIOS.png"
SCALE_FIGURE_SVG = HERE / "T322A_POSTHOC_SAME_PHASE_SCALE_RATIOS.svg"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
DECIMATE = 20
PDOM_S = 1.333
PROM_RAD = 0.02 * math.pi
SHIFT_FRACTIONS = (0.17, 0.31, 0.47)
EPS = 1e-12
CANDIDATES = {
    "1": 1.0,
    "sqrt2": math.sqrt(2.0),
    "1.5": 1.5,
    "phi": PHI,
    "sqrt3": math.sqrt(3.0),
    "2": 2.0,
}
LINEAGES = ((1, 2), (2, 3))
BRANCHES = ("positive", "negative")


@dataclass(frozen=True)
class Recurrence:
    arm: int
    branch: str
    index: int
    start_sample: int
    end_sample: int
    start_s: float
    end_s: float
    midpoint_s: float
    duration_s: float
    motion_rad: float


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def same_phase_turns(angle: np.ndarray, fs: float) -> dict[str, np.ndarray]:
    distance = max(1, int(0.4 * PDOM_S * fs))
    high, _ = find_peaks(angle, prominence=PROM_RAD, distance=distance)
    low, _ = find_peaks(-angle, prominence=PROM_RAD, distance=distance)
    return {"positive": high.astype(int), "negative": low.astype(int)}


def integrate_abs_motion(time: np.ndarray, velocity: np.ndarray, start: int, end: int) -> float:
    t = np.asarray(time[start : end + 1], dtype=np.float64)
    v = np.abs(np.asarray(velocity[start : end + 1], dtype=np.float64))
    if hasattr(np, "trapezoid"):
        return float(np.trapezoid(v, t))
    return float(np.trapz(v, t))


def make_recurrences(
    arm: int,
    branch: str,
    turns: np.ndarray,
    time: np.ndarray,
    velocity: np.ndarray,
) -> list[Recurrence]:
    out: list[Recurrence] = []
    for index, (start, end) in enumerate(zip(turns[:-1], turns[1:])):
        start, end = int(start), int(end)
        if end <= start:
            continue
        start_s = float(time[start])
        end_s = float(time[end])
        duration_s = end_s - start_s
        if duration_s <= EPS:
            continue
        out.append(
            Recurrence(
                arm=arm,
                branch=branch,
                index=index,
                start_sample=start,
                end_sample=end,
                start_s=start_s,
                end_s=end_s,
                midpoint_s=0.5 * (start_s + end_s),
                duration_s=duration_s,
                motion_rad=integrate_abs_motion(time, velocity, start, end),
            )
        )
    return out


def temporal_overlap(a: Recurrence, b: Recurrence) -> float:
    return max(0.0, min(a.end_s, b.end_s) - max(a.start_s, b.start_s))


def match_child(parent: Recurrence, children: list[Recurrence]) -> Recurrence:
    if not children:
        raise RuntimeError("No child recurrences available")
    return max(
        children,
        key=lambda child: (
            temporal_overlap(parent, child),
            -abs(parent.midpoint_s - child.midpoint_s),
            -child.start_s,
        ),
    )


def metrics(a: float, b: float) -> dict[str, float]:
    if a <= EPS or b <= EPS:
        raise RuntimeError("Non-positive golden-section length")
    ratio = a / b
    whole_ratio = (a + b) / a
    return {
        "ratio": ratio,
        "whole_ratio": whole_ratio,
        "phi_error": max(abs(ratio - PHI), abs(whole_ratio - PHI)),
        "golden_residual": abs(a * a - b * (a + b)) / (a * a + b * (a + b)),
    }


def load_recurrences(run: str, driven: bool = False) -> tuple[dict, dict[int, dict[str, list[Recurrence]]]]:
    loader = load_triple_driven if driven else load_triple
    time, theta, velocity, fs = loader(run, decimate=DECIMATE)
    centered = rest_centered(theta)
    all_rec: dict[int, dict[str, list[Recurrence]]] = {}
    meta = {
        "run": run,
        "dataset": "driven_triple1" if driven else f"free_{run}",
        "samples": int(len(time)),
        "fs_hz": float(fs),
        "duration_s": float(time[-1] - time[0]),
        "turn_counts": {},
        "recurrence_counts": {},
        "median_recurrence_s": {},
        "median_motion_rad": {},
    }
    for arm in (1, 2, 3):
        turns = same_phase_turns(np.asarray(centered[arm], dtype=np.float64), fs)
        all_rec[arm] = {}
        meta["turn_counts"][str(arm)] = {}
        meta["recurrence_counts"][str(arm)] = {}
        for branch in BRANCHES:
            rec = make_recurrences(
                arm,
                branch,
                turns[branch],
                np.asarray(time, dtype=np.float64),
                np.asarray(velocity[arm], dtype=np.float64),
            )
            all_rec[arm][branch] = rec
            meta["turn_counts"][str(arm)][branch] = int(len(turns[branch]))
            meta["recurrence_counts"][str(arm)][branch] = int(len(rec))
            meta["median_recurrence_s"][f"arm{arm}|{branch}"] = float(
                np.median([item.duration_s for item in rec])
            )
            meta["median_motion_rad"][f"arm{arm}|{branch}"] = float(
                np.median([item.motion_rad for item in rec])
            )
    return meta, all_rec


def build_rows(dataset: str, recurrences: dict[int, dict[str, list[Recurrence]]]) -> list[dict]:
    rows: list[dict] = []
    for parent_arm, child_arm in LINEAGES:
        lineage = f"{parent_arm}->{child_arm}"
        for branch in BRANCHES:
            parents = recurrences[parent_arm][branch]
            children = recurrences[child_arm][branch]
            for parent in parents:
                child = match_child(parent, children)
                tm = metrics(parent.duration_s, child.duration_s)
                mm = metrics(parent.motion_rad, child.motion_rad)
                rows.append(
                    {
                        "dataset": dataset,
                        "lineage": lineage,
                        "parent_arm": parent_arm,
                        "child_arm": child_arm,
                        "branch": branch,
                        "parent_index": parent.index,
                        "child_index": child.index,
                        "parent_midpoint_s": parent.midpoint_s,
                        "child_midpoint_s": child.midpoint_s,
                        "midpoint_offset_s": child.midpoint_s - parent.midpoint_s,
                        "overlap_s": temporal_overlap(parent, child),
                        "parent_duration_s": parent.duration_s,
                        "child_duration_s": child.duration_s,
                        "r_time": tm["ratio"],
                        "s_time": tm["whole_ratio"],
                        "e_phi_time": tm["phi_error"],
                        "e_golden_time": tm["golden_residual"],
                        "parent_motion_rad": parent.motion_rad,
                        "child_motion_rad": child.motion_rad,
                        "r_motion": mm["ratio"],
                        "s_motion": mm["whole_ratio"],
                        "e_phi_motion": mm["phi_error"],
                        "e_golden_motion": mm["golden_residual"],
                    }
                )
    return rows


def shifted_errors(recurrences: dict[int, dict[str, list[Recurrence]]]) -> dict[str, dict]:
    output: dict[str, dict] = {}
    for fraction in SHIFT_FRACTIONS:
        values: list[float] = []
        per_group: dict[str, list[float]] = {}
        for parent_arm, child_arm in LINEAGES:
            lineage = f"{parent_arm}->{child_arm}"
            for branch in BRANCHES:
                children = recurrences[child_arm][branch]
                if not children:
                    continue
                shift = max(1, int(round(fraction * len(children))))
                key = f"{lineage}|{branch}"
                per_group[key] = []
                for parent in recurrences[parent_arm][branch]:
                    real_child = match_child(parent, children)
                    replacement = children[(real_child.index + shift) % len(children)]
                    value = metrics(parent.duration_s, replacement.duration_s)["phi_error"]
                    values.append(value)
                    per_group[key].append(value)
        output[f"{fraction:.2f}"] = {
            "median_e_phi": float(np.median(values)),
            "n": int(len(values)),
            "groups": {k: float(np.median(v)) for k, v in per_group.items()},
        }
    return output


def closest_landmark(value: float) -> tuple[str, dict[str, float]]:
    errors = {name: abs(value - candidate) for name, candidate in CANDIDATES.items()}
    return min(errors, key=errors.get), errors


def bootstrap_median(values: np.ndarray, seed: int = 322, draws: int = 10000) -> list[float]:
    values = np.asarray(values, dtype=np.float64)
    rng = np.random.default_rng(seed)
    medians = np.empty(draws, dtype=np.float64)
    for i in range(draws):
        medians[i] = np.median(rng.choice(values, size=len(values), replace=True))
    return [float(x) for x in np.quantile(medians, [0.025, 0.5, 0.975])]


def summarize(rows: list[dict]) -> dict:
    def one(subset: list[dict]) -> dict:
        r_time = np.asarray([row["r_time"] for row in subset], dtype=np.float64)
        s_time = np.asarray([row["s_time"] for row in subset], dtype=np.float64)
        e_phi = np.asarray([row["e_phi_time"] for row in subset], dtype=np.float64)
        e_golden = np.asarray([row["e_golden_time"] for row in subset], dtype=np.float64)
        r_motion = np.asarray([row["r_motion"] for row in subset], dtype=np.float64)
        median_r = float(np.median(r_time))
        winner, errors = closest_landmark(median_r)
        return {
            "n": int(len(subset)),
            "time": {
                "median_parent_child_ratio": median_r,
                "median_whole_parent_ratio": float(np.median(s_time)),
                "median_e_phi": float(np.median(e_phi)),
                "median_golden_residual": float(np.median(e_golden)),
                "fraction_e_phi_le_0_08": float(np.mean(e_phi <= 0.08)),
                "bootstrap_median_ratio_ci95": bootstrap_median(r_time),
                "closest_landmark": winner,
                "candidate_absolute_errors": errors,
            },
            "motion": {
                "median_parent_child_ratio": float(np.median(r_motion)),
                "median_whole_parent_ratio": float(np.median([row["s_motion"] for row in subset])),
                "median_e_phi": float(np.median([row["e_phi_motion"] for row in subset])),
                "median_golden_residual": float(np.median([row["e_golden_motion"] for row in subset])),
                "closest_landmark": closest_landmark(float(np.median(r_motion)))[0],
            },
        }

    result = {"pooled": one(rows), "by_lineage": {}, "by_branch": {}, "by_group": {}}
    for lineage in ("1->2", "2->3"):
        result["by_lineage"][lineage] = one([r for r in rows if r["lineage"] == lineage])
    for branch in BRANCHES:
        result["by_branch"][branch] = one([r for r in rows if r["branch"] == branch])
    for lineage in ("1->2", "2->3"):
        for branch in BRANCHES:
            key = f"{lineage}|{branch}"
            result["by_group"][key] = one(
                [r for r in rows if r["lineage"] == lineage and r["branch"] == branch]
            )
    return result


def scale_summary(meta: dict) -> dict:
    """Descriptive ratio of branch medians; not part of T322 frozen gates."""
    medians = meta["median_recurrence_s"]
    output: dict[str, dict] = {}
    for parent_arm, child_arm in ((1, 2), (2, 3), (1, 3)):
        lineage = f"{parent_arm}->{child_arm}"
        output[lineage] = {}
        for branch in BRANCHES:
            a = float(medians[f"arm{parent_arm}|{branch}"])
            b = float(medians[f"arm{child_arm}|{branch}"])
            m = metrics(a, b)
            winner, errors = closest_landmark(m["ratio"])
            output[lineage][branch] = {
                "parent_branch_median_s": a,
                "child_branch_median_s": b,
                "parent_child_ratio": m["ratio"],
                "whole_parent_ratio": m["whole_ratio"],
                "e_phi": m["phi_error"],
                "golden_residual": m["golden_residual"],
                "closest_landmark": winner,
                "candidate_absolute_errors": errors,
            }
    return output


def gates(summary: dict, real_error: float, shifted: dict[str, dict]) -> dict:
    g1 = summary["pooled"]["time"]["closest_landmark"] == "phi"
    g2 = all(v["time"]["closest_landmark"] == "phi" for v in summary["by_lineage"].values())
    g3 = all(v["time"]["closest_landmark"] == "phi" for v in summary["by_branch"].values())
    g4 = summary["pooled"]["time"]["median_e_phi"] <= 0.08
    g5 = all(real_error < v["median_e_phi"] for v in shifted.values())
    values = {"G1": bool(g1), "G2": bool(g2), "G3": bool(g3), "G4": bool(g4), "G5": bool(g5)}
    passed = sum(values.values())
    verdict = "SUPPORTED" if passed == 5 else "MIXED" if passed >= 3 else "NOT SUPPORTED"
    return {"values": values, "passed": passed, "total": 5, "verdict": verdict}


def write_csv(rows: list[dict]) -> None:
    with EVENTS.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def draw(rows: list[dict], summary: dict, controls: dict[str, dict]) -> None:
    plt.rcParams.update({"font.size": 9, "axes.titlesize": 11, "axes.labelsize": 9})
    fig, axes = plt.subplots(2, 2, figsize=(13.4, 9.2), constrained_layout=True)
    colors = {"1->2": "#4F79B7", "2->3": "#D99B32"}
    markers = {"positive": "o", "negative": "^"}

    ax = axes[0, 0]
    max_b = max(row["child_duration_s"] for row in rows)
    x = np.linspace(0, max_b * 1.05, 200)
    ax.plot(x, x, color="#777777", linestyle=":", label="identity a=b")
    ax.plot(x, PHI * x, color="#222222", linestyle="--", label="golden a=φb")
    ax.plot(x, 2.0 * x, color="#B45A45", linestyle="-.", label="octave a=2b")
    for lineage in colors:
        for branch in BRANCHES:
            sub = [r for r in rows if r["lineage"] == lineage and r["branch"] == branch]
            ax.scatter(
                [r["child_duration_s"] for r in sub],
                [r["parent_duration_s"] for r in sub],
                s=18,
                alpha=0.55,
                color=colors[lineage],
                marker=markers[branch],
                label=f"{lineage} {branch}",
            )
    ax.set(xlabel="child A→A time b (s)", ylabel="parent A→A time a (s)", title="Matched same-phase recurrence times")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.legend(fontsize=7, ncol=2, frameon=False)
    ax.grid(alpha=0.18)

    ax = axes[0, 1]
    positions = []
    data = []
    labels = []
    pos = 1
    for lineage in ("1->2", "2->3"):
        for branch in BRANCHES:
            sub = [r["r_time"] for r in rows if r["lineage"] == lineage and r["branch"] == branch]
            positions.append(pos)
            data.append(sub)
            labels.append(f"{lineage}\n{branch[:3]}")
            pos += 1
        pos += 0.5
    bp = ax.boxplot(data, positions=positions, widths=0.62, patch_artist=True, showfliers=False)
    for patch, label in zip(bp["boxes"], labels):
        patch.set_facecolor(colors[label.split("\n")[0]])
        patch.set_alpha(0.65)
    ax.axhline(PHI, color="#222222", linestyle="--", label="φ")
    ax.axhline(2.0, color="#B45A45", linestyle="-.", label="2")
    ax.set_xticks(positions, labels)
    ax.set(ylabel="a/b", title="Parent/child ratios by lineage and mirror branch")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.18)

    ax = axes[1, 0]
    r = np.asarray([row["r_time"] for row in rows])
    s = np.asarray([row["s_time"] for row in rows])
    for lineage in colors:
        mask = np.asarray([row["lineage"] == lineage for row in rows])
        ax.scatter(r[mask], s[mask], s=18, alpha=0.55, color=colors[lineage], label=lineage)
    curve_x = np.linspace(max(0.4, float(np.min(r)) * 0.9), float(np.max(r)) * 1.05, 300)
    ax.plot(curve_x, 1.0 + 1.0 / curve_x, color="#777777", linewidth=1.0, label="forced identity s=1+1/r")
    ax.scatter([PHI], [PHI], s=90, facecolor="none", edgecolor="#111111", linewidth=2, label="golden fixed point")
    ax.axvline(2.0, color="#B45A45", linestyle=":", alpha=0.8)
    ax.set(xlabel="a/b", ylabel="(a+b)/a", title="Golden-section fixed-point check")
    ax.legend(frameon=False)
    ax.grid(alpha=0.18)

    ax = axes[1, 1]
    categories = ["observed"] + [f"shift {k}" for k in controls]
    observed = summary["pooled"]["time"]["median_e_phi"]
    values = [observed] + [controls[k]["median_e_phi"] for k in controls]
    ax.bar(categories, values, color=["#4F79B7"] + ["#B9C0C8"] * len(controls), edgecolor="#444444", linewidth=0.8)
    ax.axhline(0.08, color="#222222", linestyle="--", label="frozen tolerance 0.08")
    ax.set(ylabel="median max golden error", title="Observed local matching versus shifted controls")
    ax.tick_params(axis="x", rotation=20)
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.18)

    fig.suptitle(
        "T322 — cross-scale same-phase golden-section test\n"
        "Run 3 primary evaluation · A(parent) / A(child) · no opposite-phase vertex",
        fontsize=15,
        fontweight="bold",
    )
    fig.savefig(FIGURE, dpi=190, facecolor="white")
    fig.savefig(FIGURE_SVG, facecolor="white")
    plt.close(fig)


def draw_scale_summary(summaries: dict[str, dict]) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(14.2, 5.4), sharey=True)
    fig.subplots_adjust(left=0.06, right=0.99, bottom=0.16, top=0.77, wspace=0.04)
    run_labels = list(summaries)
    palette = {"positive": "#4F79B7", "negative": "#D99B32"}
    for ax, lineage in zip(axes, ("1->2", "2->3", "1->3")):
        x = np.arange(len(run_labels), dtype=float)
        for offset, branch in ((-0.08, "positive"), (0.08, "negative")):
            values = [summaries[run][lineage][branch]["parent_child_ratio"] for run in run_labels]
            ax.plot(
                x + offset,
                values,
                marker="o" if branch == "positive" else "^",
                color=palette[branch],
                linewidth=1.2,
                label=branch,
            )
        ax.axhline(1.0, color="#777777", linestyle=":", label="1" if lineage == "1->2" else None)
        ax.axhline(PHI, color="#222222", linestyle="--", label="φ" if lineage == "1->2" else None)
        ax.axhline(2.0, color="#B45A45", linestyle="-.", label="2" if lineage == "1->2" else None)
        ax.set_xticks(x, run_labels, rotation=20)
        ax.set_title(f"arm {lineage}")
        ax.set_ylim(0.85, 2.08)
        ax.grid(axis="y", alpha=0.18)
    axes[0].set_ylabel("ratio of branch-median A→A periods")
    axes[0].legend(loc="upper left", ncol=2, frameon=False, fontsize=8)
    fig.suptitle(
        "T322A — post-hoc scale-summary audit\n"
        "Phi-like run-3 depth ratio is not stable across records",
        fontsize=14,
        fontweight="bold",
        y=0.97,
    )
    fig.savefig(SCALE_FIGURE, dpi=190, facecolor="white")
    fig.savefig(SCALE_FIGURE_SVG, facecolor="white")
    plt.close(fig)


def main() -> None:
    if sha256(PROTOCOL) != PROTOCOL_SHA256:
        raise RuntimeError("Frozen protocol hash mismatch")

    data_hashes = {}
    for filename in set(RUNS.values()) | set(DRIVEN.values()):
        path = pathlib.Path(DATA_DIR) / filename
        data_hashes[filename] = sha256(path)

    development = {}
    for run in ("run1", "run2"):
        meta, rec = load_recurrences(run)
        development[run] = {
            "metadata": meta,
            "median_recurrence_s": {
                f"arm{arm}|{branch}": float(np.median([x.duration_s for x in rec[arm][branch]]))
                for arm in (1, 2, 3)
                for branch in BRANCHES
            },
            "posthoc_scale_summary": scale_summary(meta),
        }

    primary_meta, primary_rec = load_recurrences("run3")
    primary_rows = build_rows("free_run3", primary_rec)
    primary_summary = summarize(primary_rows)
    controls = shifted_errors(primary_rec)
    primary_gates = gates(primary_summary, primary_summary["pooled"]["time"]["median_e_phi"], controls)

    transfer_meta, transfer_rec = load_recurrences("triple1", driven=True)
    transfer_rows = build_rows("driven_triple1", transfer_rec)
    transfer_summary = summarize(transfer_rows)

    posthoc_scale_summaries = {
        "free run 1": development["run1"]["posthoc_scale_summary"],
        "free run 2": development["run2"]["posthoc_scale_summary"],
        "free run 3": scale_summary(primary_meta),
        "driven": scale_summary(transfer_meta),
    }

    all_rows = primary_rows + transfer_rows
    write_csv(all_rows)
    draw(primary_rows, primary_summary, controls)
    draw_scale_summary(posthoc_scale_summaries)

    payload = {
        "test_id": TEST_ID,
        "protocol": {"path": str(PROTOCOL), "sha256": PROTOCOL_SHA256},
        "source": {
            "name": "dynamicslab MultiArm-Pendulum",
            "doi": "10.5281/zenodo.6633719",
            "local_data_hashes_sha256": data_hashes,
            "decimate": DECIMATE,
        },
        "definitions": {
            "a": "parent-arm elapsed time or accumulated motion between consecutive same-sign turning points",
            "b": "child-arm elapsed time or accumulated motion between consecutive same-sign turning points",
            "lineages": ["arm1->arm2", "arm2->arm3"],
            "branches": list(BRANCHES),
            "phi": PHI,
            "candidates": CANDIDATES,
        },
        "development_audit": development,
        "primary": {
            "metadata": primary_meta,
            "summary": primary_summary,
            "shift_controls": controls,
            "gates": primary_gates,
            "posthoc_scale_summary": scale_summary(primary_meta),
        },
        "transfer": {
            "metadata": transfer_meta,
            "summary": transfer_summary,
            "posthoc_scale_summary": scale_summary(transfer_meta),
        },
        "posthoc_scale_summary_all_records": posthoc_scale_summaries,
        "artifacts": {
            "events_csv": str(EVENTS),
            "figure_png": str(FIGURE),
            "figure_svg": str(FIGURE_SVG),
            "posthoc_scale_figure_png": str(SCALE_FIGURE),
            "posthoc_scale_figure_svg": str(SCALE_FIGURE_SVG),
        },
    }
    RESULTS.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({
        "verdict": primary_gates,
        "pooled": primary_summary["pooled"],
        "by_lineage": primary_summary["by_lineage"],
        "by_branch": primary_summary["by_branch"],
        "shift_controls": controls,
        "transfer_pooled": transfer_summary["pooled"],
    }, indent=2))


if __name__ == "__main__":
    main()
