#!/usr/bin/env python3
"""T409: chronological tracking of the three parent-coordinate structures marked in T408."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import sys
from collections import Counter
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", r"F:\SystemFormulaFolder\.matplotlib_cache")

PKG = Path(r"F:\SystemFormulaFolder\.codex_python_packages")
if PKG.exists():
    sys.path.insert(0, str(PKG))

import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter1d


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "T409_chronological_parent_ridge_tracking"
PROTOCOL = ROOT / "T409_CHRONOLOGICAL_PARENT_RIDGE_TRACKING_PROTOCOL_2026-08-18.md"
EVENT_SOURCE = ROOT / "T379_individual_muon_child" / "T379_INDIVIDUAL_MUON_CHILD_HANDOVER_EVENTS.csv"
WINDOW_SOURCE = ROOT / "T408_nested_windows_individual_muon" / "T408_WINDOWS.csv"

RUNS = ("6845.2020.0317.0", "6845.2020.0318.0")
RIDGES = {
    "R1": (0.60, 0.90),
    "R2": (0.90, 1.18),
    "R3": (1.18, 1.55),
}
GRID_STEP = 0.001
GRID = np.arange(0.0, 2.0 + GRID_STEP / 2, GRID_STEP)
SIGMA_BINS = 0.035 / GRID_STEP
BLOCKS_PER_RUN = 6
MIN_COUNT = 5
MIN_CONTRAST = 1.10
N_PERM = 5000
SEED = 409


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_events() -> list[dict]:
    out: list[dict] = []
    with EVENT_SOURCE.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["split"] != "holdout":
                continue
            out.append(
                {
                    "file": row["file"],
                    "event_index": int(row["event_index"]),
                    "delay_us": float(row["delay_us"]),
                    "x_mu": float(row["x_mu"]),
                    "x_wrong": float(row["x_wrong"]),
                    "multiplicity": float(row["multiplicity"]),
                    "depth": float(row["depth"]),
                }
            )
    out.sort(key=lambda r: (RUNS.index(r["file"]), r["event_index"]))
    return out


def load_parent_window() -> tuple[float, float]:
    with WINDOW_SOURCE.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["window"] == "parent":
                return float(row["left_us"]), float(row["right_us"])
    raise RuntimeError("T408 parent window not found")


def make_blocks(rows: list[dict]) -> tuple[list[dict], np.ndarray]:
    blocks: list[dict] = []
    slot_block = np.empty(len(rows), dtype=int)
    global_block = 0
    for run_i, run in enumerate(RUNS):
        idx = np.asarray([i for i, row in enumerate(rows) if row["file"] == run], dtype=int)
        for local_block, block_idx in enumerate(np.array_split(idx, BLOCKS_PER_RUN), start=1):
            slot_block[block_idx] = global_block
            blocks.append(
                {
                    "global_block": global_block + 1,
                    "run": run,
                    "run_order": run_i + 1,
                    "block": local_block,
                    "n_events": int(len(block_idx)),
                    "event_index_min": int(min(rows[i]["event_index"] for i in block_idx)),
                    "event_index_max": int(max(rows[i]["event_index"] for i in block_idx)),
                }
            )
            global_block += 1
    return blocks, slot_block


def smooth_hist(values: np.ndarray) -> np.ndarray:
    ids = np.clip(np.rint(values / GRID_STEP).astype(int), 0, len(GRID) - 1)
    hist = np.bincount(ids, minlength=len(GRID)).astype(float)
    return gaussian_filter1d(hist, SIGMA_BINS, mode="constant")


def ridge_from_density(values: np.ndarray, density: np.ndarray, ridge: str) -> dict:
    lo, hi = RIDGES[ridge]
    right_closed = ridge == "R3"
    in_zone = (values >= lo) & ((values <= hi) if right_closed else (values < hi))
    mask = (GRID >= lo) & ((GRID <= hi) if right_closed else (GRID < hi))
    d = density[mask]
    g = GRID[mask]
    centre = float(g[int(np.argmax(d))])
    positive = d[d > 1e-15]
    median = float(np.median(positive)) if len(positive) else 0.0
    peak = float(np.max(d)) if len(d) else 0.0
    contrast = peak / median if median > 0 else math.inf if peak > 0 else 0.0
    count = int(np.sum(in_zone))
    return {
        "centre": centre,
        "count": count,
        "share": float(count / len(values)) if len(values) else 0.0,
        "peak_density": peak,
        "peak_to_median": contrast,
        "resolved": bool(count >= MIN_COUNT and contrast >= MIN_CONTRAST),
    }


def analyse_population(rows: list[dict], population: str) -> tuple[list[dict], dict, np.ndarray, list[dict]]:
    blocks, slot_block = make_blocks(rows)
    x = np.asarray([r["x_mu"] for r in rows], dtype=float)
    valid = (x > 0.0) & (x < 2.0)
    pooled_density = smooth_hist(x[valid])
    pooled = {ridge: ridge_from_density(x[valid], pooled_density, ridge) for ridge in RIDGES}
    block_rows: list[dict] = []
    for b, meta in enumerate(blocks):
        vals = x[(slot_block == b) & valid]
        density = smooth_hist(vals)
        for ridge in RIDGES:
            item = ridge_from_density(vals, density, ridge)
            block_rows.append({"population": population, **meta, "ridge": ridge, **item})

    summaries: dict[str, dict] = {}
    for ridge in RIDGES:
        rr = [r for r in block_rows if r["ridge"] == ridge and r["resolved"]]
        centres = np.asarray([r["centre"] for r in rr], dtype=float)
        weights = np.asarray([r["count"] for r in rr], dtype=float)
        pooled_c = pooled[ridge]["centre"]
        motion = float(np.sqrt(np.average((centres - pooled_c) ** 2, weights=weights))) if len(rr) else math.nan
        successive = []
        for run in RUNS:
            run_centres = [r["centre"] for r in rr if r["run"] == run]
            successive.extend(abs(b - a) for a, b in zip(run_centres, run_centres[1:]))
        run_centres = {}
        for run in RUNS:
            vals = x[np.asarray([row["file"] == run for row in rows]) & valid]
            run_centres[run] = ridge_from_density(vals, smooth_hist(vals), ridge)
        summaries[ridge] = {
            "pooled": pooled[ridge],
            "resolved_blocks": len(rr),
            "motion_M": motion,
            "centre_min": float(np.min(centres)) if len(centres) else None,
            "centre_max": float(np.max(centres)) if len(centres) else None,
            "centre_range": float(np.ptp(centres)) if len(centres) else None,
            "mean_absolute_successive_movement": float(np.mean(successive)) if successive else None,
            "per_run": run_centres,
        }
    return block_rows, summaries, slot_block, blocks


def motion_from_hist_matrix(hist: np.ndarray, pooled_centres: dict[str, float]) -> dict[str, float]:
    density = gaussian_filter1d(hist, SIGMA_BINS, axis=1, mode="constant")
    out: dict[str, float] = {}
    for ridge, (lo, hi) in RIDGES.items():
        mask = (GRID >= lo) & ((GRID <= hi) if ridge == "R3" else (GRID < hi))
        zone_bins = np.where(mask)[0]
        counts = hist[:, mask].sum(axis=1)
        sub = density[:, mask]
        centres = GRID[zone_bins[np.argmax(sub, axis=1)]]
        positive_median = np.asarray([
            np.median(row[row > 1e-15]) if np.any(row > 1e-15) else 0.0 for row in sub
        ])
        peaks = np.max(sub, axis=1)
        contrast = np.divide(peaks, positive_median, out=np.zeros_like(peaks), where=positive_median > 0)
        resolved = (counts >= MIN_COUNT) & (contrast >= MIN_CONTRAST)
        if np.sum(resolved) < 2:
            out[ridge] = math.nan
        else:
            out[ridge] = float(
                np.sqrt(
                    np.average(
                        (centres[resolved] - pooled_centres[ridge]) ** 2,
                        weights=counts[resolved],
                    )
                )
            )
    return out


def permutation_tests(rows: list[dict], slot_block: np.ndarray, observed: dict) -> dict:
    x = np.asarray([r["x_mu"] for r in rows], dtype=float)
    bin_ids = np.clip(np.rint(x / GRID_STEP).astype(int), 0, len(GRID) - 1)
    n_blocks = int(np.max(slot_block)) + 1
    pooled_centres = {ridge: observed[ridge]["pooled"]["centre"] for ridge in RIDGES}
    run_slots = {run: np.asarray([i for i, r in enumerate(rows) if r["file"] == run], dtype=int) for run in RUNS}
    rng = np.random.default_rng(SEED)
    null_global = {ridge: [] for ridge in RIDGES}
    null_within = {ridge: [] for ridge in RIDGES}

    for _ in range(N_PERM):
        perm_global = rng.permutation(bin_ids)
        hist = np.zeros((n_blocks, len(GRID)), dtype=float)
        np.add.at(hist, (slot_block, perm_global), 1.0)
        stats = motion_from_hist_matrix(hist, pooled_centres)
        for ridge in RIDGES:
            if math.isfinite(stats[ridge]):
                null_global[ridge].append(stats[ridge])

        perm_within = bin_ids.copy()
        for run in RUNS:
            idx = run_slots[run]
            perm_within[idx] = rng.permutation(perm_within[idx])
        hist.fill(0.0)
        np.add.at(hist, (slot_block, perm_within), 1.0)
        stats = motion_from_hist_matrix(hist, pooled_centres)
        for ridge in RIDGES:
            if math.isfinite(stats[ridge]):
                null_within[ridge].append(stats[ridge])

    result = {}
    for ridge in RIDGES:
        obs = float(observed[ridge]["motion_M"])
        g = np.asarray(null_global[ridge], dtype=float)
        w = np.asarray(null_within[ridge], dtype=float)
        result[ridge] = {
            "observed_motion_M": obs,
            "global_shuffle_draws_valid": int(len(g)),
            "global_shuffle_median": float(np.median(g)),
            "global_shuffle_q95": float(np.quantile(g, 0.95)),
            "global_shuffle_p_upper_add_one": float((1 + np.sum(g >= obs)) / (1 + len(g))),
            "within_run_shuffle_draws_valid": int(len(w)),
            "within_run_shuffle_median": float(np.median(w)),
            "within_run_shuffle_q95": float(np.quantile(w, 0.95)),
            "within_run_shuffle_p_upper_add_one": float((1 + np.sum(w >= obs)) / (1 + len(w))),
        }
    return result


def wrong_lineage_summary(rows: list[dict]) -> dict:
    x = np.asarray([r["x_wrong"] for r in rows], dtype=float)
    valid = (x > 0) & (x < 2)
    density = smooth_hist(x[valid])
    return {ridge: ridge_from_density(x[valid], density, ridge) for ridge in RIDGES}


def quantization_summary(rows: list[dict]) -> list[dict]:
    out = []
    for ridge, (lo, hi) in RIDGES.items():
        vals = [r["x_mu"] for r in rows if lo <= r["x_mu"] <= hi]
        rounded = Counter(round(v, 3) for v in vals)
        for rank, (value, count) in enumerate(rounded.most_common(8), start=1):
            out.append(
                {
                    "ridge": ridge,
                    "rank": rank,
                    "x_mu_rounded_0p001": value,
                    "count": count,
                    "share_of_zone": count / len(vals) if vals else 0.0,
                    "zone_events": len(vals),
                    "unique_rounded_values": len(rounded),
                }
            )
    return out


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def make_figure(rows: list[dict], block_rows: list[dict], summaries: dict, permutations: dict, parent_window: tuple[float, float]) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(15.5, 10.5), constrained_layout=True)
    blue, gold, olive, pink, ink = "#4E79A7", "#D89B2B", "#718355", "#B56576", "#263238"
    colors = {"R1": blue, "R2": gold, "R3": pink}

    ax = axes[0, 0]
    x = np.asarray([r["x_mu"] for r in rows])
    y = np.asarray([r["delay_us"] for r in rows])
    ax.scatter(x, y, s=8, alpha=0.23, color=blue, linewidths=0, rasterized=True)
    for ridge, (lo, hi) in RIDGES.items():
        ax.axvspan(lo, hi, color=colors[ridge], alpha=0.06)
        ax.axvline(summaries[ridge]["pooled"]["centre"], color=colors[ridge], lw=2.1, label=f"{ridge} centre {summaries[ridge]['pooled']['centre']:.3f}")
    ax.axhspan(parent_window[0], parent_window[1], color=olive, alpha=0.08, label="T408 parent delay window")
    ax.set(xlim=(0, 2), ylim=(0.3, 8.0), xlabel="incoming parent ARA x_mu (0–2)", ylabel="linked charged-daughter delay (microseconds)", title="Full held-out individual-event population")
    ax.legend(frameon=False, fontsize=8, ncol=2)

    ax = axes[0, 1]
    for ridge in RIDGES:
        rr = [r for r in block_rows if r["ridge"] == ridge]
        for run in RUNS:
            rrun = [r for r in rr if r["run"] == run]
            xx = [r["global_block"] for r in rrun]
            yy = [r["centre"] if r["resolved"] else np.nan for r in rrun]
            ax.plot(xx, yy, color=colors[ridge], marker="o", lw=2, ms=5)
        ax.axhline(summaries[ridge]["pooled"]["centre"], color=colors[ridge], ls="--", lw=1, alpha=0.65)
    ax.axvline(6.5, color=ink, lw=1.2, alpha=0.6)
    ax.text(3.5, 1.575, "0317 run", ha="center", va="bottom", fontsize=9)
    ax.text(9.5, 1.575, "0318 run", ha="center", va="bottom", fontsize=9)
    ax.set(xlim=(0.5, 12.5), ylim=(0.55, 1.60), xticks=range(1, 13), xlabel="chronological block (six per run)", ylabel="resolved ridge centre on x_mu", title="Ridge centres through chronological order")

    ax = axes[1, 0]
    bins_x = np.linspace(0, 2, 161)
    block_ids = np.asarray([1 + i // max(1, len(rows) // 12) for i in range(len(rows))])
    # Use the exact fixed block assignments instead of the visual convenience approximation above.
    blocks, slot_block = make_blocks(rows)
    h, xe, ye = np.histogram2d(x, slot_block + 1, bins=[bins_x, np.arange(0.5, 13.5, 1)])
    ax.imshow(np.log1p(h.T), origin="lower", aspect="auto", extent=[0, 2, 0.5, 12.5], cmap="Blues")
    for ridge in RIDGES:
        rr = [r for r in block_rows if r["ridge"] == ridge and r["resolved"]]
        ax.scatter([r["centre"] for r in rr], [r["global_block"] for r in rr], s=26, color=colors[ridge], edgecolor="white", linewidth=0.6)
    ax.set(xlim=(0.45, 1.65), ylim=(0.5, 12.5), xlabel="incoming parent ARA x_mu", ylabel="chronological block", title="Event-density heatmap with resolved centres")

    ax = axes[1, 1]
    xpos = np.arange(3)
    observed = [permutations[r]["observed_motion_M"] for r in RIDGES]
    q95_global = [permutations[r]["global_shuffle_q95"] for r in RIDGES]
    q95_within = [permutations[r]["within_run_shuffle_q95"] for r in RIDGES]
    ax.bar(xpos - 0.22, observed, width=0.22, color=[colors[r] for r in RIDGES], label="observed M")
    ax.bar(xpos, q95_global, width=0.22, color="#AAB2BD", label="global shuffle q95")
    ax.bar(xpos + 0.22, q95_within, width=0.22, color="#D5D8DC", label="within-run shuffle q95")
    for i, ridge in enumerate(RIDGES):
        ax.text(i - 0.22, observed[i] + 0.003, f"p={permutations[ridge]['global_shuffle_p_upper_add_one']:.3f}", ha="center", va="bottom", fontsize=8, rotation=90)
    ax.set(xticks=xpos, xticklabels=list(RIDGES), ylabel="chronological motion M (ARA units)", title="Observed movement against shuffled-order controls")
    ax.legend(frameon=False, fontsize=8)

    fig.suptitle("T409 — chronological tracking of the marked parent-coordinate structures", fontsize=18, fontweight="bold")
    fig.savefig(OUT / "T409_CHRONOLOGICAL_PARENT_RIDGES.png", dpi=190)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = load_events()
    if len(rows) != 2109:
        raise RuntimeError(f"Expected 2,109 held-out events, found {len(rows)}")
    parent_window = load_parent_window()
    conditioned = [r for r in rows if parent_window[0] <= r["delay_us"] <= parent_window[1]]
    if len(conditioned) != 527:
        raise RuntimeError(f"Expected 527 parent-window events, found {len(conditioned)}")

    full_blocks, full_summary, full_slot_block, block_meta = analyse_population(rows, "full_2109")
    control_blocks, control_summary, _, _ = analyse_population(conditioned, "parent_window_527")
    permutations = permutation_tests(rows, full_slot_block, full_summary)
    wrong = wrong_lineage_summary(rows)
    quantized = quantization_summary(rows)

    m1, m2, m3 = (full_summary[r]["motion_M"] for r in ("R1", "R2", "R3"))
    gates = {
        "G1_R1_resolved_at_least_10_of_12": full_summary["R1"]["resolved_blocks"] >= 10,
        "G2_R2_resolved_at_least_10_of_12": full_summary["R2"]["resolved_blocks"] >= 10,
        "G3_R3_resolved_at_least_8_of_12": full_summary["R3"]["resolved_blocks"] >= 8,
        "G4_R3_motion_at_least_1p5x_both_lower": m3 >= 1.5 * max(m1, m2),
        "G5_R3_global_shuffle_p_at_most_0p05": permutations["R3"]["global_shuffle_p_upper_add_one"] <= 0.05,
        "G6_R3_within_run_shuffle_p_at_most_0p05": permutations["R3"]["within_run_shuffle_p_upper_add_one"] <= 0.05,
    }
    if all(gates.values()):
        verdict = "TRAVELLING UPPER BRANCH SUPPORTED"
    elif all(gates[k] for k in list(gates)[:5]) and not gates["G6_R3_within_run_shuffle_p_at_most_0p05"]:
        verdict = "RUN/REGIME-SHIFTING UPPER BRANCH"
    elif gates["G3_R3_resolved_at_least_8_of_12"]:
        verdict = "UPPER STRUCTURE RESOLVED BUT NOT CHRONOLOGICALLY TRAVELLING"
    else:
        verdict = "UPPER STRUCTURE NOT RESOLVED"

    results = {
        "test": "T409 chronological parent-ridge tracking",
        "date": "2026-08-18",
        "protocol_sha256": sha256(PROTOCOL),
        "event_source_sha256": sha256(EVENT_SOURCE),
        "window_source_sha256": sha256(WINDOW_SOURCE),
        "verdict": verdict,
        "population": {"full_holdout": len(rows), "parent_window_control": len(conditioned), "runs": list(RUNS)},
        "frozen": {
            "ridges": {k: list(v) for k, v in RIDGES.items()},
            "blocks_per_run": BLOCKS_PER_RUN,
            "kde_bandwidth_ara": 0.035,
            "grid_step_ara": GRID_STEP,
            "resolved_min_count": MIN_COUNT,
            "resolved_min_peak_to_median": MIN_CONTRAST,
            "permutation_draws": N_PERM,
            "seed": SEED,
        },
        "full": full_summary,
        "parent_window_control": control_summary,
        "wrong_lineage_control": wrong,
        "permutations": permutations,
        "gates": gates,
        "boundaries": [
            "T409 is diagnostic because the bands were selected after visual inspection of T408.",
            "The incoming x_mu coordinate is a charged-detector relation, not a direct observation of either neutrino.",
            "A stable vertical band can reflect a stable relation, charge/channel discretization, or both.",
            "A between-run displacement is a regime shift unless within-run chronological motion also exceeds the frozen shuffle control.",
        ],
    }

    ridge_rows = []
    for population, summary in (("full_2109", full_summary), ("parent_window_527", control_summary)):
        for ridge, item in summary.items():
            ridge_rows.append(
                {
                    "population": population,
                    "ridge": ridge,
                    "zone_left": RIDGES[ridge][0],
                    "zone_right": RIDGES[ridge][1],
                    "pooled_centre": item["pooled"]["centre"],
                    "pooled_count": item["pooled"]["count"],
                    "pooled_share": item["pooled"]["share"],
                    "pooled_peak_to_median": item["pooled"]["peak_to_median"],
                    "resolved_blocks": item["resolved_blocks"],
                    "motion_M": item["motion_M"],
                    "centre_range": item["centre_range"],
                    "mean_absolute_successive_movement": item["mean_absolute_successive_movement"],
                    "run_0317_centre": item["per_run"][RUNS[0]]["centre"],
                    "run_0318_centre": item["per_run"][RUNS[1]]["centre"],
                    "run_centre_shift": item["per_run"][RUNS[1]]["centre"] - item["per_run"][RUNS[0]]["centre"],
                }
            )
    perm_rows = [{"ridge": ridge, **item} for ridge, item in permutations.items()]
    write_csv(OUT / "T409_BLOCK_RIDGES.csv", full_blocks + control_blocks)
    write_csv(OUT / "T409_RIDGE_SUMMARY.csv", ridge_rows)
    write_csv(OUT / "T409_PERMUTATION_SUMMARY.csv", perm_rows)
    write_csv(OUT / "T409_QUANTIZATION_DIAGNOSTIC.csv", quantized)
    (OUT / "T409_RESULTS.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    make_figure(rows, full_blocks, full_summary, permutations, parent_window)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
