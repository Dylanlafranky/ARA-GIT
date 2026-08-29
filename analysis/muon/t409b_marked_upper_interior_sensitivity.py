#!/usr/bin/env python3
"""T409B: post-hoc local-crest sensitivity for the user-marked upper structure."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", r"F:\SystemFormulaFolder\.matplotlib_cache")

PKG = Path(r"F:\SystemFormulaFolder\.codex_python_packages")
if PKG.exists():
    sys.path.insert(0, str(PKG))

import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

import t409_chronological_parent_ridge_tracking as base


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "T409_chronological_parent_ridge_tracking"
PROTOCOL = ROOT / "T409B_MARKED_UPPER_INTERIOR_SENSITIVITY_PROTOCOL_2026-08-18.md"
LEFT, RIGHT = 1.25, 1.50
N_PERM = 5000
SEED = 4091


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def crest(values: np.ndarray, density: np.ndarray) -> dict:
    zone = (values >= LEFT) & (values <= RIGHT)
    mask = (base.GRID >= LEFT) & (base.GRID <= RIGHT)
    d = density[mask]
    g = base.GRID[mask]
    peaks, _ = find_peaks(d)
    if len(peaks):
        pick = int(peaks[np.argmax(d[peaks])])
        centre = float(g[pick])
        peak = float(d[pick])
        interior = True
    else:
        centre = None
        peak = 0.0
        interior = False
    positive = d[d > 1e-15]
    median = float(np.median(positive)) if len(positive) else 0.0
    contrast = peak / median if median > 0 else 0.0
    count = int(np.sum(zone))
    return {
        "centre": centre,
        "count": count,
        "share": count / len(values) if len(values) else 0.0,
        "peak_to_median": contrast,
        "interior_peak": interior,
        "resolved": bool(interior and count >= base.MIN_COUNT and contrast >= base.MIN_CONTRAST),
    }


def actual_track(rows: list[dict]) -> tuple[list[dict], dict, np.ndarray]:
    blocks, slot_block = base.make_blocks(rows)
    x = np.asarray([r["x_mu"] for r in rows], dtype=float)
    valid = (x > 0) & (x < 2)
    pooled = crest(x[valid], base.smooth_hist(x[valid]))
    out = []
    for b, meta in enumerate(blocks):
        vals = x[(slot_block == b) & valid]
        out.append({**meta, **crest(vals, base.smooth_hist(vals))})
    resolved = [r for r in out if r["resolved"]]
    centres = np.asarray([r["centre"] for r in resolved], float)
    weights = np.asarray([r["count"] for r in resolved], float)
    motion = float(np.sqrt(np.average((centres - pooled["centre"]) ** 2, weights=weights))) if len(resolved) >= 2 and pooled["centre"] is not None else math.nan
    summary = {
        "pooled": pooled,
        "resolved_blocks": len(resolved),
        "motion_M": motion,
        "centre_min": float(np.min(centres)) if len(centres) else None,
        "centre_max": float(np.max(centres)) if len(centres) else None,
        "centre_range": float(np.ptp(centres)) if len(centres) else None,
    }
    return out, summary, slot_block


def motion_hist(hist: np.ndarray, pooled_centre: float) -> float:
    density = gaussian_filter1d(hist, base.SIGMA_BINS, axis=1, mode="constant")
    mask = (base.GRID >= LEFT) & (base.GRID <= RIGHT)
    g = base.GRID[mask]
    centres, weights = [], []
    for i in range(hist.shape[0]):
        d = density[i, mask]
        peaks, _ = find_peaks(d)
        count = float(hist[i, mask].sum())
        if not len(peaks) or count < base.MIN_COUNT:
            continue
        p = int(peaks[np.argmax(d[peaks])])
        positive = d[d > 1e-15]
        median = float(np.median(positive)) if len(positive) else 0.0
        contrast = float(d[p] / median) if median > 0 else 0.0
        if contrast < base.MIN_CONTRAST:
            continue
        centres.append(float(g[p]))
        weights.append(count)
    if len(centres) < 2:
        return math.nan
    c = np.asarray(centres)
    w = np.asarray(weights)
    return float(np.sqrt(np.average((c - pooled_centre) ** 2, weights=w)))


def permutations(rows: list[dict], slot_block: np.ndarray, observed: float, pooled: float) -> dict:
    x = np.asarray([r["x_mu"] for r in rows], dtype=float)
    ids = np.clip(np.rint(x / base.GRID_STEP).astype(int), 0, len(base.GRID) - 1)
    run_slots = {run: np.asarray([i for i, r in enumerate(rows) if r["file"] == run], int) for run in base.RUNS}
    rng = np.random.default_rng(SEED)
    global_null, within_null = [], []
    hist = np.zeros((12, len(base.GRID)), float)
    for _ in range(N_PERM):
        perm = rng.permutation(ids)
        hist.fill(0)
        np.add.at(hist, (slot_block, perm), 1.0)
        stat = motion_hist(hist, pooled)
        if math.isfinite(stat):
            global_null.append(stat)

        perm = ids.copy()
        for run in base.RUNS:
            idx = run_slots[run]
            perm[idx] = rng.permutation(perm[idx])
        hist.fill(0)
        np.add.at(hist, (slot_block, perm), 1.0)
        stat = motion_hist(hist, pooled)
        if math.isfinite(stat):
            within_null.append(stat)

    g, w = np.asarray(global_null), np.asarray(within_null)
    return {
        "observed_motion_M": observed,
        "global_draws_valid": len(g),
        "global_median": float(np.median(g)),
        "global_q95": float(np.quantile(g, 0.95)),
        "global_p_upper_add_one": float((1 + np.sum(g >= observed)) / (1 + len(g))),
        "within_run_draws_valid": len(w),
        "within_run_median": float(np.median(w)),
        "within_run_q95": float(np.quantile(w, 0.95)),
        "within_run_p_upper_add_one": float((1 + np.sum(w >= observed)) / (1 + len(w))),
    }


def main() -> None:
    rows = base.load_events()
    track, summary, slot_block = actual_track(rows)
    perm = permutations(rows, slot_block, summary["motion_M"], summary["pooled"]["centre"])
    t409 = json.loads((OUT / "T409_RESULTS.json").read_text(encoding="utf-8"))
    lower_max = max(t409["full"]["R1"]["motion_M"], t409["full"]["R2"]["motion_M"])
    result = {
        "test": "T409B marked upper-interior local-crest sensitivity",
        "date": "2026-08-18",
        "protocol_sha256": sha256(PROTOCOL),
        "event_source_sha256": sha256(base.EVENT_SOURCE),
        "post_hoc": True,
        "search_interval": [LEFT, RIGHT],
        "summary": summary,
        "permutation": perm,
        "comparison_to_T409_lower_ridges": {
            "max_R1_R2_motion_M": lower_max,
            "ratio_to_max_lower": summary["motion_M"] / lower_max,
        },
        "reading": (
            "INTERIOR CREST CHRONOLOGICALLY MOBILE"
            if summary["resolved_blocks"] >= 8 and summary["motion_M"] >= 1.5 * lower_max and perm["global_p_upper_add_one"] <= 0.05 and perm["within_run_p_upper_add_one"] <= 0.05
            else "INTERIOR CREST PRESENT BUT TRAVEL NOT RESOLVED"
            if summary["resolved_blocks"] >= 8
            else "INTERIOR CREST TOO SPARSE TO TRACK"
        ),
        "boundary": "This is a post-hoc repair of the T409 R3 edge capture and cannot by itself establish a new travelling branch.",
    }
    (OUT / "T409B_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    with (OUT / "T409B_BLOCK_CRESTS.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(track[0].keys()))
        writer.writeheader()
        writer.writerows(track)

    fig, ax = plt.subplots(figsize=(11, 5.8), constrained_layout=True)
    for run, color in zip(base.RUNS, ("#4E79A7", "#B56576")):
        rr = [r for r in track if r["run"] == run]
        ax.plot([r["global_block"] for r in rr], [r["centre"] if r["resolved"] else np.nan for r in rr], marker="o", lw=2, color=color, label=run)
    ax.axhline(summary["pooled"]["centre"], color="#263238", ls="--", lw=1.5, label=f"pooled local crest {summary['pooled']['centre']:.3f}")
    ax.axvline(6.5, color="#777", lw=1)
    ax.set(xlim=(0.5, 12.5), ylim=(LEFT - 0.02, RIGHT + 0.02), xticks=range(1, 13), xlabel="chronological block", ylabel="marked upper-interior crest on x_mu", title="T409B — post-hoc tracking of the marked ~1.35 interior crest")
    ax.legend(frameon=False)
    fig.savefig(OUT / "T409B_MARKED_UPPER_INTERIOR_SENSITIVITY.png", dpi=190)
    plt.close(fig)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
