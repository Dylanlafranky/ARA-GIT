#!/usr/bin/env python3
"""T368: frozen event-level muon decay handover information test.

The protocol was frozen before the source event values were downloaded. This
script intentionally uses only NumPy, pandas and the Python standard library so
the public-data reproduction path remains lightweight.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "T368_SUPERK_DECAYES_AND_NEUTRONS_SOURCE.csv"
RESULTS = HERE / "T368_MUON_DECAY_HANDOVER_RESULTS.json"
COORDS = HERE / "T368_MUON_DECAY_HANDOVER_COORDINATES.npz"
CONTINGENCY = HERE / "T368_MUON_DECAY_HANDOVER_CONTINGENCY.csv"
ENTROPY_CSV = HERE / "T368_MUON_DECAY_HANDOVER_ENTROPY.csv"
CONTROLS_CSV = HERE / "T368_MUON_DECAY_HANDOVER_CONTROLS.csv"
GATES_CSV = HERE / "T368_MUON_DECAY_HANDOVER_GATES.csv"
FIGURE = HERE / "T368_MUON_DECAY_HANDOVER_FIGURE.svg"
REPORT = HERE / "T368_MUON_DECAY_HANDOVER_REPORT_2026-08-12.md"

EXPECTED_ROWS = 1_986_465
EXPECTED_MD5 = "59056d97657ed04b3d19c7766a976519"
EXPECTED_SHA256 = "b6bb10270e6c604935b47687293470caeafd01172288170d83349043566cd05a"
SEED = 368
N_BINS = 8
N_RESAMPLES = 1_000


def file_hash(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stable_row_hashes(n_rows: int) -> np.ndarray:
    values = np.empty(n_rows, dtype=np.uint64)
    for index in range(n_rows):
        digest = hashlib.sha256(f"T368|{index + 1}".encode("ascii")).digest()
        values[index] = int.from_bytes(digest[:8], "big", signed=False)
    return values


def ecdf_coordinate(values: np.ndarray, reference: np.ndarray) -> np.ndarray:
    ordered = np.sort(reference)
    return 2.0 * np.searchsorted(ordered, values, side="right") / len(ordered)


def bin_edges(reference: np.ndarray) -> np.ndarray:
    return np.quantile(reference, np.arange(1, N_BINS) / N_BINS)


def assign_bins(values: np.ndarray, edges: np.ndarray) -> np.ndarray:
    return np.digitize(values, edges, right=False).astype(np.int8)


def contingency(parent_bin: np.ndarray, daughter_bin: np.ndarray) -> np.ndarray:
    return np.bincount(
        parent_bin.astype(np.int64) * N_BINS + daughter_bin.astype(np.int64),
        minlength=N_BINS * N_BINS,
    ).reshape(N_BINS, N_BINS)


def entropy_from_counts(counts: np.ndarray) -> float:
    counts = np.asarray(counts, dtype=float)
    total = counts.sum()
    if total <= 0:
        return float("nan")
    p = counts[counts > 0] / total
    return float(-(p * np.log(p)).sum())


def row_entropies(table: np.ndarray) -> np.ndarray:
    return np.array([entropy_from_counts(row) for row in table], dtype=float)


def cramer_v_2x2(table: np.ndarray) -> float:
    table = np.asarray(table, dtype=float)
    n = table.sum()
    if n <= 0:
        return float("nan")
    expected = np.outer(table.sum(axis=1), table.sum(axis=0)) / n
    valid = expected > 0
    chi2 = np.sum(((table - expected) ** 2)[valid] / expected[valid])
    return float(math.sqrt(chi2 / n))


def rank_average(values: np.ndarray) -> np.ndarray:
    return pd.Series(values).rank(method="average").to_numpy(dtype=float)


def spearman(values_a: np.ndarray, values_b: np.ndarray) -> float:
    return float(np.corrcoef(rank_average(values_a), rank_average(values_b))[0, 1])


def probabilities_from_development(table: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    conditional = (table + 1.0) / (table.sum(axis=1, keepdims=True) + N_BINS)
    totals = table.sum(axis=0)
    unconditional = (totals + 1.0) / (totals.sum() + N_BINS)
    return conditional, unconditional


def cross_entropy_metrics(
    table: np.ndarray, conditional: np.ndarray, unconditional: np.ndarray
) -> dict[str, float]:
    n = float(table.sum())
    cond_loss = -float(np.sum(table * np.log(conditional))) / n
    base_loss = -float(np.sum(table * np.log(unconditional)[None, :])) / n
    improvement = (base_loss - cond_loss) / base_loss
    return {
        "conditional_cross_entropy": cond_loss,
        "unconditional_cross_entropy": base_loss,
        "relative_improvement": float(improvement),
    }


def narrowing(table: np.ndarray) -> dict[str, float]:
    early_counts = table[:2].sum(axis=0)
    late_counts = table[-2:].sum(axis=0)
    early = entropy_from_counts(early_counts)
    late = entropy_from_counts(late_counts)
    relative = (late - early) / early
    return {
        "early_entropy": early,
        "late_entropy": late,
        "relative_change": float(relative),
    }


def bootstrap_tables(
    table: np.ndarray,
    conditional: np.ndarray,
    unconditional: np.ndarray,
    rng: np.random.Generator,
) -> dict[str, list[float]]:
    n = int(table.sum())
    p = table.ravel().astype(float) / n
    improvements = np.empty(N_RESAMPLES)
    narrowings = np.empty(N_RESAMPLES)
    for index in range(N_RESAMPLES):
        sampled = rng.multinomial(n, p).reshape(N_BINS, N_BINS)
        improvements[index] = cross_entropy_metrics(
            sampled, conditional, unconditional
        )["relative_improvement"]
        narrowings[index] = narrowing(sampled)["relative_change"]
    return {
        "improvement_ci95": np.quantile(improvements, [0.025, 0.975]).tolist(),
        "narrowing_ci95": np.quantile(narrowings, [0.025, 0.975]).tolist(),
    }


def softmax(logits: np.ndarray) -> np.ndarray:
    shifted = logits - logits.max(axis=1, keepdims=True)
    exp = np.exp(shifted)
    return exp / exp.sum(axis=1, keepdims=True)


def fit_time_logistic(
    train_time: np.ndarray,
    train_class: np.ndarray,
    test_time: np.ndarray,
    test_class: np.ndarray,
) -> dict[str, Any]:
    """Fit a small multinomial logistic baseline with Adam.

    The only predictor is standardized raw decay time. The intercept and slope
    for class 7 are fixed to zero to identify the model.
    """

    mean = float(train_time.mean())
    scale = float(train_time.std())
    x_train = np.column_stack((np.ones(len(train_time)), (train_time - mean) / scale))
    x_test = np.column_stack((np.ones(len(test_time)), (test_time - mean) / scale))
    beta = np.zeros((2, N_BINS - 1), dtype=float)
    m = np.zeros_like(beta)
    v = np.zeros_like(beta)
    learning_rate = 0.08
    previous = float("inf")
    converged = False

    for iteration in range(1, 401):
        logits = np.column_stack((x_train @ beta, np.zeros(len(x_train))))
        probs = softmax(logits)
        probs[np.arange(len(train_class)), train_class] -= 1.0
        gradient = x_train.T @ probs[:, : N_BINS - 1] / len(x_train)
        m = 0.9 * m + 0.1 * gradient
        v = 0.999 * v + 0.001 * (gradient * gradient)
        m_hat = m / (1.0 - 0.9**iteration)
        v_hat = v / (1.0 - 0.999**iteration)
        beta -= learning_rate * m_hat / (np.sqrt(v_hat) + 1e-8)

        if iteration % 10 == 0:
            check_logits = np.column_stack((x_train @ beta, np.zeros(len(x_train))))
            check_probs = softmax(check_logits)
            loss = -float(np.log(check_probs[np.arange(len(train_class)), train_class]).mean())
            if abs(previous - loss) < 1e-10:
                converged = True
                break
            previous = loss

    test_logits = np.column_stack((x_test @ beta, np.zeros(len(x_test))))
    test_probs = softmax(test_logits)
    test_loss = -float(np.log(test_probs[np.arange(len(test_class)), test_class]).mean())
    return {
        "test_cross_entropy": test_loss,
        "iterations": iteration,
        "converged": converged,
        "time_mean": mean,
        "time_std": scale,
        "coefficients": beta.tolist(),
    }


def analyse_population(
    dev_time: np.ndarray,
    dev_momentum: np.ndarray,
    hold_time: np.ndarray,
    hold_momentum: np.ndarray,
    rng: np.random.Generator,
    run_resamples: bool = True,
) -> dict[str, Any]:
    time_edges = bin_edges(dev_time)
    momentum_edges = bin_edges(dev_momentum)
    dev_parent_bin = assign_bins(dev_time, time_edges)
    dev_daughter_bin = assign_bins(dev_momentum, momentum_edges)
    hold_parent_bin = assign_bins(hold_time, time_edges)
    hold_daughter_bin = assign_bins(hold_momentum, momentum_edges)
    dev_table = contingency(dev_parent_bin, dev_daughter_bin)
    hold_table = contingency(hold_parent_bin, hold_daughter_bin)
    conditional, unconditional = probabilities_from_development(dev_table)
    ce = cross_entropy_metrics(hold_table, conditional, unconditional)
    narrow = narrowing(hold_table)
    quadrant = contingency((hold_parent_bin >= 4).astype(np.int8), (hold_daughter_bin >= 4).astype(np.int8))[:2, :2]

    output: dict[str, Any] = {
        "development_n": int(len(dev_time)),
        "holdout_n": int(len(hold_time)),
        "time_edges": time_edges.tolist(),
        "momentum_edges": momentum_edges.tolist(),
        "development_table": dev_table.tolist(),
        "holdout_table": hold_table.tolist(),
        "conditional_probabilities": conditional.tolist(),
        "unconditional_probabilities": unconditional.tolist(),
        "cross_entropy": ce,
        "narrowing": narrow,
        "row_entropies": row_entropies(hold_table).tolist(),
        "quadrant_table": quadrant.tolist(),
        "cramers_v": cramer_v_2x2(quadrant),
        "spearman_raw": spearman(hold_time, hold_momentum),
        "hold_parent_bin": hold_parent_bin,
        "hold_daughter_bin": hold_daughter_bin,
        "dev_parent_bin": dev_parent_bin,
        "dev_daughter_bin": dev_daughter_bin,
    }
    if run_resamples:
        output["bootstrap"] = bootstrap_tables(hold_table, conditional, unconditional, rng)
    return output


def permutation_null(
    parent_bin: np.ndarray,
    daughter_bin: np.ndarray,
    conditional: np.ndarray,
    unconditional: np.ndarray,
    observed: float,
    rng: np.random.Generator,
) -> dict[str, Any]:
    shuffled = daughter_bin.copy()
    effects = np.empty(N_RESAMPLES)
    for index in range(N_RESAMPLES):
        rng.shuffle(shuffled)
        table = contingency(parent_bin, shuffled)
        effects[index] = cross_entropy_metrics(table, conditional, unconditional)[
            "relative_improvement"
        ]
    return {
        "n": N_RESAMPLES,
        "equal_or_greater": int(np.sum(effects >= observed)),
        "null_median": float(np.median(effects)),
        "null_ci95": np.quantile(effects, [0.025, 0.975]).tolist(),
    }


def scan_neutron_qa(path: Path) -> dict[str, Any]:
    multiplicities: dict[int, int] = {}
    tagged_neutron_rows = 0
    total_neutron_tags = 0
    min_time = float("inf")
    max_time = float("-inf")
    with path.open("r", newline="", encoding="utf-8") as handle:
        for row in csv.reader(handle):
            neutron_values = []
            for item in row[2:]:
                if item.strip() and float(item) > 0:
                    neutron_values.append(float(item))
            count = len(neutron_values)
            multiplicities[count] = multiplicities.get(count, 0) + 1
            if count:
                tagged_neutron_rows += 1
                total_neutron_tags += count
                min_time = min(min_time, min(neutron_values))
                max_time = max(max_time, max(neutron_values))
    return {
        "rows_with_tagged_neutrons": tagged_neutron_rows,
        "total_neutron_tags": total_neutron_tags,
        "observed_multiplicity_counts": {str(k): v for k, v in sorted(multiplicities.items())},
        "neutron_time_min_us": min_time if math.isfinite(min_time) else None,
        "neutron_time_max_us": max_time if math.isfinite(max_time) else None,
    }


def svg_figure(
    parent_x: np.ndarray,
    daughter_x: np.ndarray,
    hold_table: np.ndarray,
    entropies: np.ndarray,
    time_values: np.ndarray,
    result: dict[str, Any],
) -> None:
    width, height = 1500, 1040
    bg = "#f6f7f9"
    ink = "#182231"
    muted = "#667085"
    blue = "#2f6db0"
    orange = "#dc8b25"
    green = "#2d8a62"
    lines: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="100%" height="100%" fill="{bg}"/>',
        f'<text x="55" y="58" font-family="Segoe UI,Arial" font-size="31" font-weight="700" fill="{ink}">T368 — stopped-muon parent → daughter handover</text>',
        f'<text x="55" y="91" font-family="Segoe UI,Arial" font-size="17" fill="{muted}">{html.escape(result["verdict"])} · holdout n={len(parent_x):,}</text>',
    ]

    panels = [(55, 130, 670, 375), (775, 130, 670, 375), (55, 555, 670, 375), (775, 555, 670, 375)]
    for x, y, w, h in panels:
        lines.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="white" stroke="#d5dae2"/>')

    # Panel 1: 8x8 conditional heatmap.
    x0, y0, w, h = panels[0]
    lines.append(f'<text x="{x0+24}" y="{y0+35}" font-family="Segoe UI,Arial" font-size="20" font-weight="600" fill="{ink}">Parent/daughter ARA mixing</text>')
    cell = 34
    hx, hy = x0 + 92, y0 + 64
    row_norm = hold_table / np.maximum(hold_table.sum(axis=1, keepdims=True), 1)
    lo, hi = float(row_norm.min()), float(row_norm.max())
    for i in range(N_BINS):
        for j in range(N_BINS):
            q = (row_norm[i, j] - lo) / max(hi - lo, 1e-12)
            r = int(235 - 155 * q)
            g = int(241 - 105 * q)
            b = int(249 - 35 * q)
            lines.append(f'<rect x="{hx+j*cell}" y="{hy+(7-i)*cell}" width="{cell-1}" height="{cell-1}" fill="rgb({r},{g},{b})"/>')
    lines.extend([
        f'<line x1="{hx+4*cell}" y1="{hy}" x2="{hx+4*cell}" y2="{hy+8*cell}" stroke="{orange}" stroke-width="2"/>',
        f'<line x1="{hx}" y1="{hy+4*cell}" x2="{hx+8*cell}" y2="{hy+4*cell}" stroke="{orange}" stroke-width="2"/>',
        f'<text x="{hx+90}" y="{hy+8*cell+29}" font-family="Segoe UI,Arial" font-size="14" fill="{muted}">daughter xD: 0 → 2</text>',
        f'<text transform="translate({hx-45},{hy+205}) rotate(-90)" font-family="Segoe UI,Arial" font-size="14" fill="{muted}">parent xP: 0 → 2</text>',
        f'<text x="{x0+410}" y="{y0+105}" font-family="Segoe UI,Arial" font-size="16" fill="{ink}">Cramér V</text>',
        f'<text x="{x0+410}" y="{y0+140}" font-family="Segoe UI,Arial" font-size="27" font-weight="700" fill="{blue}">{result["primary"]["cramers_v"]:.4f}</text>',
        f'<text x="{x0+410}" y="{y0+190}" font-family="Segoe UI,Arial" font-size="16" fill="{ink}">Spearman ρ</text>',
        f'<text x="{x0+410}" y="{y0+225}" font-family="Segoe UI,Arial" font-size="27" font-weight="700" fill="{blue}">{result["primary"]["spearman_raw"]:.4f}</text>',
    ])

    # Panel 2: daughter entropy by parent phase.
    x0, y0, w, h = panels[1]
    lines.append(f'<text x="{x0+24}" y="{y0+35}" font-family="Segoe UI,Arial" font-size="20" font-weight="600" fill="{ink}">Does the daughter narrow before closure?</text>')
    px, py, pw, ph = x0 + 62, y0 + 70, 555, 245
    ymin = min(entropies) - 0.02
    ymax = max(entropies) + 0.02
    points = []
    for i, value in enumerate(entropies):
        xx = px + i * pw / 7
        yy = py + ph * (ymax - value) / (ymax - ymin)
        points.append((xx, yy))
    lines.append('<polyline points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in points) + f'" fill="none" stroke="{green}" stroke-width="4"/>')
    for i, (xx, yy) in enumerate(points):
        lines.append(f'<circle cx="{xx}" cy="{yy}" r="6" fill="{green}"/>')
        lines.append(f'<text x="{xx}" y="{py+ph+28}" text-anchor="middle" font-family="Segoe UI,Arial" font-size="13" fill="{muted}">{i+1}</text>')
    lines.extend([
        f'<line x1="{px}" y1="{py+ph}" x2="{px+pw}" y2="{py+ph}" stroke="#9aa4b2"/>',
        f'<text x="{px+185}" y="{py+ph+52}" font-family="Segoe UI,Arial" font-size="14" fill="{muted}">parent ARA bin: early → late</text>',
        f'<text x="{px}" y="{py-18}" font-family="Segoe UI,Arial" font-size="14" fill="{muted}">daughter entropy (lower = more determined)</text>',
        f'<text x="{x0+390}" y="{y0+350}" font-family="Segoe UI,Arial" font-size="16" fill="{ink}">late vs early: {100*result["primary"]["narrowing"]["relative_change"]:+.3f}%</text>',
    ])

    # Panel 3: release/survival and hazard.
    x0, y0, w, h = panels[2]
    lines.append(f'<text x="{x0+24}" y="{y0+35}" font-family="Segoe UI,Arial" font-size="20" font-weight="600" fill="{ink}">Observed parent waiting field</text>')
    t_grid = np.linspace(1.1, 5.0, 100)
    ordered = np.sort(time_values)
    cdf = np.searchsorted(ordered, t_grid, side="right") / len(ordered)
    px, py, pw, ph = x0 + 62, y0 + 70, 555, 245
    release_points = []
    survival_points = []
    for t, f in zip(t_grid, cdf):
        xx = px + (t - 1.1) / 3.9 * pw
        release_points.append((xx, py + ph * (1 - f)))
        survival_points.append((xx, py + ph * f))
    lines.append('<polyline points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in release_points) + f'" fill="none" stroke="{blue}" stroke-width="4"/>')
    lines.append('<polyline points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in survival_points) + f'" fill="none" stroke="{orange}" stroke-width="4"/>')
    lines.extend([
        f'<line x1="{px}" y1="{py+ph/2}" x2="{px+pw}" y2="{py+ph/2}" stroke="#adb5c1" stroke-dasharray="5 5"/>',
        f'<text x="{px+pw+7}" y="{py+ph/2+5}" font-family="Segoe UI,Arial" font-size="13" fill="{muted}">ridge</text>',
        f'<text x="{px+12}" y="{py+20}" font-family="Segoe UI,Arial" font-size="14" fill="{blue}">released</text>',
        f'<text x="{px+12}" y="{py+42}" font-family="Segoe UI,Arial" font-size="14" fill="{orange}">surviving</text>',
        f'<text x="{px+190}" y="{py+ph+42}" font-family="Segoe UI,Arial" font-size="14" fill="{muted}">time after stopped muon (μs)</text>',
    ])

    # Panel 4: effect and controls.
    x0, y0, w, h = panels[3]
    lines.append(f'<text x="{x0+24}" y="{y0+35}" font-family="Segoe UI,Arial" font-size="20" font-weight="600" fill="{ink}">Prediction against controls</text>')
    bars = [
        ("ARA relation", result["primary"]["cross_entropy"]["relative_improvement"], blue),
        ("mismatched daughters", result["controls"]["mismatched_relative_improvement"], "#9aa4b2"),
        ("permutation 97.5%", result["controls"]["permutation"]["null_ci95"][1], "#9aa4b2"),
        ("inner window", result["controls"]["inner_window"]["cross_entropy"]["relative_improvement"], green),
    ]
    max_abs = max(max(abs(v) for _, v, _ in bars), 0.01)
    bx, by, bw = x0 + 220, y0 + 88, 360
    zero_x = bx + bw / 2
    lines.append(f'<line x1="{zero_x}" y1="{by-20}" x2="{zero_x}" y2="{by+230}" stroke="#7d8795"/>')
    for i, (label, value, color) in enumerate(bars):
        yy = by + i * 61
        length = value / max_abs * (bw / 2 - 12)
        xx = zero_x if length >= 0 else zero_x + length
        lines.append(f'<rect x="{xx}" y="{yy}" width="{abs(length)}" height="24" fill="{color}"/>')
        lines.append(f'<text x="{x0+24}" y="{yy+18}" font-family="Segoe UI,Arial" font-size="14" fill="{ink}">{html.escape(label)}</text>')
        anchor = "start" if length >= 0 else "end"
        tx = zero_x + length + (7 if length >= 0 else -7)
        lines.append(f'<text x="{tx}" y="{yy+18}" text-anchor="{anchor}" font-family="Segoe UI,Arial" font-size="14" fill="{ink}">{100*value:+.4f}%</text>')
    lines.append(f'<text x="{x0+24}" y="{y0+342}" font-family="Segoe UI,Arial" font-size="15" fill="{muted}">Positive means parent time predicts daughter bin beyond its marginal distribution.</text>')

    lines.append(f'<text x="55" y="1005" font-family="Segoe UI,Arial" font-size="14" fill="{muted}">Source: Super-Kamiokande, Zenodo 10.5281/zenodo.15081911 · frozen before event values · exact event count and hashes recorded</text>')
    lines.append("</svg>")
    FIGURE.write_text("\n".join(lines), encoding="utf-8")


def strip_arrays(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: strip_arrays(item) for key, item in value.items() if not isinstance(item, np.ndarray)}
    if isinstance(value, list):
        return [strip_arrays(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    return value


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Missing {SOURCE}. Download from https://zenodo.org/records/15081911/files/decayes_and_neutrons.csv?download=1"
        )

    md5 = file_hash(SOURCE, "md5")
    sha256 = file_hash(SOURCE, "sha256")
    frame = pd.read_csv(
        SOURCE,
        header=None,
        usecols=[0, 1],
        names=["electron_momentum_mev", "electron_time_us"],
        dtype=float,
    )
    n_rows = len(frame)
    hashes = stable_row_hashes(n_rows)
    residues = hashes % 10

    momentum = frame["electron_momentum_mev"].to_numpy()
    time = frame["electron_time_us"].to_numpy()
    finite = np.isfinite(momentum) & np.isfinite(time)
    primary = finite & (momentum > 15.0) & (time >= 1.1) & (time <= 5.0)
    development = primary & (residues <= 5)
    holdout = primary & (residues >= 6)

    rng = np.random.default_rng(SEED)
    primary_result = analyse_population(
        time[development], momentum[development], time[holdout], momentum[holdout], rng
    )

    conditional = np.asarray(primary_result["conditional_probabilities"])
    unconditional = np.asarray(primary_result["unconditional_probabilities"])
    hold_parent_bin = primary_result["hold_parent_bin"]
    hold_daughter_bin = primary_result["hold_daughter_bin"]
    shift = len(hold_daughter_bin) // 3 + 17
    mismatched = np.roll(hold_daughter_bin, shift)
    mismatched_table = contingency(hold_parent_bin, mismatched)
    mismatched_effect = cross_entropy_metrics(mismatched_table, conditional, unconditional)
    permutation = permutation_null(
        hold_parent_bin,
        hold_daughter_bin,
        conditional,
        unconditional,
        primary_result["cross_entropy"]["relative_improvement"],
        rng,
    )

    inner = primary & (momentum > 20.0) & (momentum < 50.0) & (time > 1.3) & (time < 4.5)
    inner_dev = inner & (residues <= 5)
    inner_hold = inner & (residues >= 6)
    inner_result = analyse_population(
        time[inner_dev], momentum[inner_dev], time[inner_hold], momentum[inner_hold], rng
    )

    half_results = {}
    for parity, name in [(0, "even_hash"), (1, "odd_hash")]:
        mask = holdout & ((hashes & 1) == parity)
        pbin = assign_bins(time[mask], np.asarray(primary_result["time_edges"]))
        dbin = assign_bins(momentum[mask], np.asarray(primary_result["momentum_edges"]))
        table = contingency(pbin, dbin)
        half_results[name] = {
            "n": int(mask.sum()),
            "cross_entropy": cross_entropy_metrics(table, conditional, unconditional),
            "narrowing": narrowing(table),
        }

    logistic = fit_time_logistic(
        time[development],
        primary_result["dev_daughter_bin"],
        time[holdout],
        hold_daughter_bin,
    )

    neutron_qa = scan_neutron_qa(SOURCE)
    source_qa = {
        "doi": "10.5281/zenodo.15081911",
        "path": str(SOURCE),
        "rows": n_rows,
        "expected_rows": EXPECTED_ROWS,
        "md5": md5,
        "expected_md5": EXPECTED_MD5,
        "sha256": sha256,
        "expected_sha256": EXPECTED_SHA256,
        "finite_rows": int(finite.sum()),
        "zero_electron_rows": int(((momentum == 0) & (time == 0)).sum()),
        "primary_rows": int(primary.sum()),
        "development_rows": int(development.sum()),
        "holdout_rows": int(holdout.sum()),
        "inner_development_rows": int(inner_dev.sum()),
        "inner_holdout_rows": int(inner_hold.sum()),
        "neutron_qa": neutron_qa,
    }

    improvement = primary_result["cross_entropy"]["relative_improvement"]
    improvement_ci = primary_result["bootstrap"]["improvement_ci95"]
    narrow_value = primary_result["narrowing"]["relative_change"]
    narrow_ci = primary_result["bootstrap"]["narrowing_ci95"]
    inner_improvement = inner_result["cross_entropy"]["relative_improvement"]
    inner_narrowing = inner_result["narrowing"]["relative_change"]

    gates = {
        "G1_source_and_implementation_QA": (
            n_rows == EXPECTED_ROWS and md5 == EXPECTED_MD5 and sha256 == EXPECTED_SHA256
        ),
        "G2_coverage": int(holdout.sum()) >= 100_000,
        "G3_predictive_imprint": improvement >= 0.01 and improvement_ci[0] > 0,
        "G4_not_shuffled": permutation["equal_or_greater"] <= 10,
        "G5_progressive_determination": narrow_value <= -0.05 and narrow_ci[1] < 0,
        "G6_nontrivial_quadrant_effect": primary_result["cramers_v"] >= 0.05,
        "G7_robustness": (
            inner_improvement > 0
            and inner_narrowing < 0
            and all(item["cross_entropy"]["relative_improvement"] > 0 for item in half_results.values())
            and all(item["narrowing"]["relative_change"] < 0 for item in half_results.values())
        ),
        "G8_added_relational_value": (
            primary_result["cross_entropy"]["conditional_cross_entropy"]
            <= logistic["test_cross_entropy"]
        ),
    }

    if all(gates.values()):
        verdict = "OBSERVABLE PRE-HANDOVER IMPRINT SUPPORTED IN THIS RECORD"
    elif permutation["equal_or_greater"] <= 10 and primary_result["cramers_v"] >= 0.01:
        verdict = "PARENT-DAUGHTER DEPENDENCE WITHOUT PREFORMATION SUPPORT"
    else:
        verdict = "NO OBSERVABLE PREFORMATION IN THE RELEASED VARIABLES"

    result = {
        "test": "T368 muon decay handover information test",
        "frozen_protocol": str(HERE / "T368_MUON_DECAY_HANDOVER_PROTOCOL_v1_FROZEN.md"),
        "source_qa": source_qa,
        "primary": strip_arrays(primary_result),
        "controls": {
            "mismatched_relative_improvement": mismatched_effect["relative_improvement"],
            "permutation": permutation,
            "inner_window": strip_arrays(inner_result),
            "hash_halves": half_results,
            "smooth_time_logistic": logistic,
        },
        "gates": gates,
        "verdict": verdict,
        "boundary": (
            "The archive does not continuously observe individual muons before decay; "
            "the primary test is limited to whether waiting duration predicts tagged "
            "electron momentum. Missing neutrinos and per-event muon charge prevent a "
            "complete decay TE-ARA reconstruction."
        ),
    }
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")

    parent_x = ecdf_coordinate(time[holdout], time[development])
    daughter_x = ecdf_coordinate(momentum[holdout], momentum[development])
    np.savez_compressed(
        COORDS,
        source_row=np.flatnonzero(holdout) + 1,
        row_hash=hashes[holdout],
        electron_time_us=time[holdout],
        electron_momentum_mev=momentum[holdout],
        parent_x=parent_x,
        daughter_x=daughter_x,
        parent_bin=hold_parent_bin,
        daughter_bin=hold_daughter_bin,
    )

    hold_table = np.asarray(primary_result["holdout_table"])
    pd.DataFrame(
        hold_table,
        index=[f"parent_{i+1}" for i in range(N_BINS)],
        columns=[f"daughter_{i+1}" for i in range(N_BINS)],
    ).to_csv(CONTINGENCY)
    pd.DataFrame(
        {
            "parent_bin": np.arange(1, N_BINS + 1),
            "daughter_entropy": primary_result["row_entropies"],
            "event_count": hold_table.sum(axis=1),
        }
    ).to_csv(ENTROPY_CSV, index=False)
    control_rows = [
        {"control": "primary_ARA", "relative_improvement": improvement, "narrowing": narrow_value},
        {"control": "mismatched_daughters", "relative_improvement": mismatched_effect["relative_improvement"], "narrowing": narrowing(mismatched_table)["relative_change"]},
        {"control": "inner_window", "relative_improvement": inner_improvement, "narrowing": inner_narrowing},
    ]
    for name, item in half_results.items():
        control_rows.append({"control": name, "relative_improvement": item["cross_entropy"]["relative_improvement"], "narrowing": item["narrowing"]["relative_change"]})
    pd.DataFrame(control_rows).to_csv(CONTROLS_CSV, index=False)
    pd.DataFrame([{"gate": key, "passed": value} for key, value in gates.items()]).to_csv(GATES_CSV, index=False)

    svg_figure(
        parent_x,
        daughter_x,
        hold_table,
        np.asarray(primary_result["row_entropies"]),
        time[holdout],
        result,
    )

    gate_lines = "\n".join(
        f"| {name.replace('_', ' ')} | **{'PASS' if passed else 'FAIL'}** |"
        for name, passed in gates.items()
    )
    report = f"""# T368 - Muon decay handover information test

**Date:** 12 August 2026  
**Frozen verdict:** **{verdict}**

## Result first

The event-level Super-Kamiokande record was used to ask whether the duration of
the open muon-parent interval predicts the momentum class of the electron
observed at closure. The primary untouched holdout contained
**{int(holdout.sum()):,}** eligible decays.

The ARA parent/daughter table changed holdout cross-entropy by
**{100*improvement:+.6f}%** relative to the unconditional daughter model
(95% bootstrap interval **[{100*improvement_ci[0]:+.6f}%,
{100*improvement_ci[1]:+.6f}%]**). The daughter entropy changed by
**{100*narrow_value:+.6f}%** from the first to the final parent quartile
(95% interval **[{100*narrow_ci[0]:+.6f}%, {100*narrow_ci[1]:+.6f}%]**).

The coarse quadrant association was **Cramer's V =
{primary_result['cramers_v']:.6f}** and the raw time/momentum Spearman
correlation was **{primary_result['spearman_raw']:.6f}**. The permutation
control had **{permutation['equal_or_greater']} / {N_RESAMPLES}** effects at
least as large as the observed effect.

## Plain-language translation

The test treats the time between stopping and decay as the open parent path,
and the tagged electron momentum as one visible part of the daughter state. A
positive result would mean that where the parent sits along its waiting path
contains advance information about the daughter. A null result places the
observable organisation at the decay handover or in the daughter products,
not progressively inside the recorded waiting interval.

This record cannot see a hidden internal muon trajectory. It can only test the
information exposed in waiting duration and electron momentum.

## Data QA

- Source: Super-Kamiokande data release `10.5281/zenodo.15081911`
- Rows: **{n_rows:,}** (published: {EXPECTED_ROWS:,})
- MD5: `{md5}`
- SHA256: `{sha256}`
- Development decays: **{int(development.sum()):,}**
- Holdout decays: **{int(holdout.sum()):,}**
- Rows with tagged neutrons: **{neutron_qa['rows_with_tagged_neutrons']:,}**

## Frozen gates

| gate | result |
|---|---:|
{gate_lines}

## Controls

- Mismatched-daughter improvement: **{100*mismatched_effect['relative_improvement']:+.6f}%**
- Permutation-null 95% interval: **[{100*permutation['null_ci95'][0]:+.6f}%, {100*permutation['null_ci95'][1]:+.6f}%]**
- Inner-window improvement: **{100*inner_improvement:+.6f}%**
- Inner-window narrowing: **{100*inner_narrowing:+.6f}%**
- Smooth raw-time logistic cross-entropy: **{logistic['test_cross_entropy']:.8f}**
- ARA-table cross-entropy: **{primary_result['cross_entropy']['conditional_cross_entropy']:.8f}**

## Scientific boundary

The released variables do not include the neutrinos, the electron direction,
the per-event muon charge or a continuous measurement of the muon during the
waiting interval. The archive also mixes positive-muon decay, negative-muon
decay and negative-muon nuclear capture. Consequently, this is not a complete
TE-ARA of muon decay and cannot rule out unmeasured internal geometry.

Neutrons are a separate delayed nuclear-capture branch. Their presence is
reported for post-handover context but is not combined with the primary
electron daughter as if it were one decay identity.

## Reproduction

```powershell
& 'C:\\Users\\Dylan\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe' `
  'F:\\SystemFormulaFolder\\GIT\\ARA-GIT\\analysis\\muon\\t368_muon_decay_handover.py'
```

The source CSV can be restored from:

`https://zenodo.org/records/15081911/files/decayes_and_neutrons.csv?download=1`
"""
    REPORT.write_text(report, encoding="utf-8")

    print(json.dumps({"verdict": verdict, "gates": gates, "holdout_n": int(holdout.sum())}, indent=2))


if __name__ == "__main__":
    main()
