#!/usr/bin/env python3
"""T369: frozen prompt/delayed daughter closure test in stopped-muon data."""

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
RESULTS = HERE / "T369_MUON_CAPTURE_DAUGHTER_CLOSURE_RESULTS.json"
DERIVED = HERE / "T369_MUON_CAPTURE_DAUGHTER_CLOSURE_DERIVED.npz"
MIXING = HERE / "T369_MUON_CAPTURE_DAUGHTER_MIXING.csv"
CONTROLS = HERE / "T369_MUON_CAPTURE_DAUGHTER_CONTROLS.csv"
GATES = HERE / "T369_MUON_CAPTURE_DAUGHTER_GATES.csv"
FIGURE = HERE / "T369_MUON_CAPTURE_DAUGHTER_CLOSURE_FIGURE.svg"
REPORT = HERE / "T369_MUON_CAPTURE_DAUGHTER_CLOSURE_REPORT_2026-08-12.md"

EXPECTED_ROWS = 1_986_465
EXPECTED_MD5 = "59056d97657ed04b3d19c7766a976519"
EXPECTED_SHA256 = "b6bb10270e6c604935b47687293470caeafd01172288170d83349043566cd05a"
SEED = 369
N_RESAMPLES = 1_000
N_BINS = 8


def digest_file(path: Path, algorithm: str) -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stable_hashes(n: int) -> np.ndarray:
    result = np.empty(n, dtype=np.uint64)
    for index in range(n):
        result[index] = int.from_bytes(
            hashlib.sha256(f"T369|{index + 1}".encode("ascii")).digest()[:8],
            "big",
        )
    return result


def parse_source(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    momentum: list[float] = []
    prompt_time: list[float] = []
    multiplicity: list[int] = []
    first_neutron: list[float] = []
    with path.open("r", newline="", encoding="utf-8") as handle:
        for row in csv.reader(handle):
            momentum.append(float(row[0]))
            prompt_time.append(float(row[1]))
            neutrons = [float(item) for item in row[2:] if item and float(item) > 0]
            multiplicity.append(len(neutrons))
            first_neutron.append(min(neutrons) if neutrons else 0.0)
    return (
        np.asarray(momentum, dtype=float),
        np.asarray(prompt_time, dtype=float),
        np.asarray(multiplicity, dtype=np.int16),
        np.asarray(first_neutron, dtype=float),
    )


def edges(values: np.ndarray) -> np.ndarray:
    return np.quantile(values, np.arange(1, N_BINS) / N_BINS)


def bins(values: np.ndarray, cutpoints: np.ndarray) -> np.ndarray:
    return np.digitize(values, cutpoints, right=False).astype(np.int16)


def address(
    present: np.ndarray,
    prompt_time: np.ndarray,
    momentum: np.ndarray,
    time_edges: np.ndarray,
    energy_edges: np.ndarray,
) -> np.ndarray:
    result = np.zeros(len(present), dtype=np.int16)
    time_bin = bins(prompt_time[present], time_edges)
    energy_bin = bins(momentum[present], energy_edges)
    result[present] = 1 + time_bin * N_BINS + energy_bin
    return result


def count_table(category: np.ndarray, target: np.ndarray, n_category: int, n_target: int) -> np.ndarray:
    return np.bincount(
        category.astype(np.int64) * n_target + target.astype(np.int64),
        minlength=n_category * n_target,
    ).reshape(n_category, n_target)


def probabilities(train_table: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    n_target = train_table.shape[1]
    conditional = (train_table + 1.0) / (
        train_table.sum(axis=1, keepdims=True) + n_target
    )
    counts = train_table.sum(axis=0)
    unconditional = (counts + 1.0) / (counts.sum() + n_target)
    return conditional, unconditional


def cross_entropy(
    test_table: np.ndarray,
    conditional: np.ndarray,
    unconditional: np.ndarray,
) -> dict[str, float]:
    total = test_table.sum()
    conditional_loss = -float(np.sum(test_table * np.log(conditional))) / total
    unconditional_loss = -float(
        np.sum(test_table * np.log(unconditional)[None, :])
    ) / total
    return {
        "conditional": conditional_loss,
        "unconditional": unconditional_loss,
        "relative_improvement": (unconditional_loss - conditional_loss)
        / unconditional_loss,
    }


def evaluate(
    development_category: np.ndarray,
    development_target: np.ndarray,
    holdout_category: np.ndarray,
    holdout_target: np.ndarray,
    n_category: int,
    n_target: int,
) -> dict[str, Any]:
    train_table = count_table(
        development_category, development_target, n_category, n_target
    )
    test_table = count_table(holdout_category, holdout_target, n_category, n_target)
    conditional, unconditional = probabilities(train_table)
    return {
        "development_table": train_table,
        "holdout_table": test_table,
        "conditional": conditional,
        "unconditional": unconditional,
        "cross_entropy": cross_entropy(test_table, conditional, unconditional),
    }


def effect_against_reference(candidate_loss: float, reference_loss: float) -> float:
    return (reference_loss - candidate_loss) / reference_loss


def bootstrap_binary(
    holdout_table: np.ndarray,
    conditional: np.ndarray,
    unconditional: np.ndarray,
    rng: np.random.Generator,
) -> list[float]:
    n = int(holdout_table.sum())
    p = holdout_table.ravel() / n
    effects = np.empty(N_RESAMPLES)
    for index in range(N_RESAMPLES):
        sampled = rng.multinomial(n, p).reshape(holdout_table.shape)
        effects[index] = cross_entropy(sampled, conditional, unconditional)[
            "relative_improvement"
        ]
    return np.quantile(effects, [0.025, 0.975]).tolist()


def permute_binary_presence(
    prompt_present: np.ndarray,
    neutron_present: np.ndarray,
    conditional: np.ndarray,
    unconditional: np.ndarray,
    observed: float,
    rng: np.random.Generator,
) -> dict[str, Any]:
    n = len(prompt_present)
    n_prompt = int(prompt_present.sum())
    n_neutron = int(neutron_present.sum())
    effects = np.empty(N_RESAMPLES)
    for index in range(N_RESAMPLES):
        overlap = int(rng.hypergeometric(n_neutron, n - n_neutron, n_prompt))
        test_table = np.array(
            [
                [n - n_prompt - (n_neutron - overlap), n_neutron - overlap],
                [n_prompt - overlap, overlap],
            ],
            dtype=np.int64,
        )
        effects[index] = cross_entropy(test_table, conditional, unconditional)[
            "relative_improvement"
        ]
    return {
        "equal_or_greater": int(np.sum(effects >= observed)),
        "median": float(np.median(effects)),
        "ci95": np.quantile(effects, [0.025, 0.975]).tolist(),
    }


def packet_permutation_null(
    category: np.ndarray,
    target: np.ndarray,
    conditional: np.ndarray,
    unconditional: np.ndarray,
    observed: float,
    n_category: int,
    n_target: int,
    rng: np.random.Generator,
) -> dict[str, Any]:
    shuffled = target.copy()
    effects = np.empty(N_RESAMPLES)
    for index in range(N_RESAMPLES):
        rng.shuffle(shuffled)
        test_table = count_table(category, shuffled, n_category, n_target)
        effects[index] = cross_entropy(test_table, conditional, unconditional)[
            "relative_improvement"
        ]
    return {
        "equal_or_greater": int(np.sum(effects >= observed)),
        "median": float(np.median(effects)),
        "ci95": np.quantile(effects, [0.025, 0.975]).tolist(),
    }


def timing_shuffle_by_multiplicity(
    address_value: np.ndarray,
    timing_bin: np.ndarray,
    multiplicity_class: np.ndarray,
    conditional: np.ndarray,
    unconditional: np.ndarray,
    observed: float,
    rng: np.random.Generator,
) -> dict[str, Any]:
    effects = np.empty(N_RESAMPLES)
    working = timing_bin.copy()
    indices = [np.flatnonzero(multiplicity_class == value) for value in range(3)]
    for iteration in range(N_RESAMPLES):
        for index in indices:
            working[index] = rng.permutation(timing_bin[index])
        test_table = count_table(address_value, working, 65, N_BINS)
        effects[iteration] = cross_entropy(test_table, conditional, unconditional)[
            "relative_improvement"
        ]
    return {
        "equal_or_greater": int(np.sum(effects >= observed)),
        "median": float(np.median(effects)),
        "ci95": np.quantile(effects, [0.025, 0.975]).tolist(),
    }


def ecdf(values: np.ndarray, reference: np.ndarray) -> np.ndarray:
    ordered = np.sort(reference)
    return 2 * np.searchsorted(ordered, values, side="right") / len(ordered)


def serializable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, dict):
        return {key: serializable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [serializable(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    return value


def make_svg(result: dict[str, Any]) -> None:
    width, height = 1500, 1040
    ink, muted = "#182231", "#667085"
    blue, orange, green = "#2f6db0", "#dc8b25", "#2d8a62"
    primary = result["primary"]
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f6f7f9"/>',
        f'<text x="55" y="58" font-family="Segoe UI,Arial" font-size="31" font-weight="700" fill="{ink}">T369 — muon-capture daughter closure</text>',
        f'<text x="55" y="91" font-family="Segoe UI,Arial" font-size="17" fill="{muted}">{html.escape(result["verdict"])} · capture-enriched holdout n={result["source_qa"]["holdout_capture_enriched"]:,}</text>',
    ]
    panels = [(55, 130, 670, 375), (775, 130, 670, 375), (55, 555, 670, 375), (775, 555, 670, 375)]
    for x, y, w, h in panels:
        lines.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="white" stroke="#d5dae2"/>')

    # Common-parent 2x2.
    x, y, w, h = panels[0]
    table = np.asarray(primary["common_parent"]["holdout_table"])
    row_p = table / table.sum(axis=1, keepdims=True)
    lines.append(f'<text x="{x+24}" y="{y+35}" font-family="Segoe UI,Arial" font-size="20" font-weight="600" fill="{ink}">Known relation recovery</text>')
    for i in range(2):
        for j in range(2):
            intensity = row_p[i, j]
            color = blue if j else "#dce8f5"
            opacity = 0.3 + 0.7 * intensity
            lines.append(f'<rect x="{x+85+j*170}" y="{y+82+i*112}" width="154" height="96" rx="8" fill="{color}" fill-opacity="{opacity:.3f}"/>')
            lines.append(f'<text x="{x+162+j*170}" y="{y+135+i*112}" text-anchor="middle" font-family="Segoe UI,Arial" font-size="20" font-weight="700" fill="{ink}">{100*intensity:.2f}%</text>')
    lines.extend([
        f'<text x="{x+108}" y="{y+318}" font-family="Segoe UI,Arial" font-size="14" fill="{muted}">prompt absent</text>',
        f'<text x="{x+278}" y="{y+318}" font-family="Segoe UI,Arial" font-size="14" fill="{muted}">prompt present</text>',
        f'<text x="{x+430}" y="{y+105}" font-family="Segoe UI,Arial" font-size="15" fill="{ink}">CE improvement</text>',
        f'<text x="{x+430}" y="{y+145}" font-family="Segoe UI,Arial" font-size="28" font-weight="700" fill="{green}">{100*primary["common_parent"]["cross_entropy"]["relative_improvement"]:+.3f}%</text>',
        f'<text x="{x+430}" y="{y+202}" font-family="Segoe UI,Arial" font-size="15" fill="{ink}">same-row enrichment</text>',
        f'<text x="{x+430}" y="{y+242}" font-family="Segoe UI,Arial" font-size="28" font-weight="700" fill="{green}">{primary["neutron_enrichment_ratio"]:.2f}×</text>',
    ])

    # Joint address heatmap of neutron probability.
    x, y, w, h = panels[1]
    heat = np.asarray(primary["joint_prompt_neutron_probability"])
    lines.append(f'<text x="{x+24}" y="{y+35}" font-family="Segoe UI,Arial" font-size="20" font-weight="600" fill="{ink}">Prompt-child Di-ARA → neutron probability</text>')
    hx, hy, cell = x + 74, y + 64, 34
    lo, hi = float(np.nanmin(heat)), float(np.nanmax(heat))
    for ti in range(8):
        for ei in range(8):
            value = heat[ti, ei]
            q = 0 if not np.isfinite(value) else (value - lo) / max(hi - lo, 1e-12)
            r, g, b = int(240-155*q), int(242-110*q), int(248-35*q)
            lines.append(f'<rect x="{hx+ei*cell}" y="{hy+(7-ti)*cell}" width="{cell-1}" height="{cell-1}" fill="rgb({r},{g},{b})"/>')
    lines.extend([
        f'<text x="{hx+80}" y="{hy+8*cell+28}" font-family="Segoe UI,Arial" font-size="14" fill="{muted}">prompt energy: 0 → 2</text>',
        f'<text transform="translate({hx-42},{hy+220}) rotate(-90)" font-family="Segoe UI,Arial" font-size="14" fill="{muted}">prompt time: 0 → 2</text>',
        f'<text x="{x+405}" y="{y+105}" font-family="Segoe UI,Arial" font-size="15" fill="{ink}">added vs presence</text>',
        f'<text x="{x+405}" y="{y+145}" font-family="Segoe UI,Arial" font-size="28" font-weight="700" fill="{blue}">{100*primary["continuous_added_value"]:+.4f}%</text>',
        f'<text x="{x+405}" y="{y+205}" font-family="Segoe UI,Arial" font-size="15" fill="{ink}">joint vs unconditional</text>',
        f'<text x="{x+405}" y="{y+245}" font-family="Segoe UI,Arial" font-size="28" font-weight="700" fill="{blue}">{100*primary["joint_binary"]["cross_entropy"]["relative_improvement"]:+.4f}%</text>',
    ])

    # Multiplicity distribution.
    x, y, w, h = panels[2]
    counts = np.asarray(primary["multiplicity_by_prompt_presence"])
    probs = counts / counts.sum(axis=1, keepdims=True)
    lines.append(f'<text x="{x+24}" y="{y+35}" font-family="Segoe UI,Arial" font-size="20" font-weight="600" fill="{ink}">Observed neutron multiplicity branch</text>')
    colors = ["#d9e2ec", blue, orange]
    labels = ["0", "1", "2+"]
    for i, row in enumerate(probs):
        yy = y + 100 + i * 100
        cursor = x + 125
        for j, value in enumerate(row):
            length = 430 * value
            lines.append(f'<rect x="{cursor}" y="{yy}" width="{length}" height="38" fill="{colors[j]}"/>')
            if length > 45:
                lines.append(f'<text x="{cursor+length/2}" y="{yy+25}" text-anchor="middle" font-family="Segoe UI,Arial" font-size="13" fill="{ink}">{100*value:.2f}%</text>')
            cursor += length
        lines.append(f'<text x="{x+24}" y="{yy+25}" font-family="Segoe UI,Arial" font-size="14" fill="{ink}">{"prompt absent" if i==0 else "prompt present"}</text>')
    for j, label in enumerate(labels):
        lines.append(f'<rect x="{x+155+j*120}" y="{y+326}" width="18" height="18" fill="{colors[j]}"/><text x="{x+180+j*120}" y="{y+341}" font-family="Segoe UI,Arial" font-size="14" fill="{muted}">{label} neutron</text>')

    # Gate/effect panel.
    x, y, w, h = panels[3]
    lines.append(f'<text x="{x+24}" y="{y+35}" font-family="Segoe UI,Arial" font-size="20" font-weight="600" fill="{ink}">How deep does the relation survive?</text>')
    effects = [
        ("prompt presence → neutron", primary["common_parent"]["cross_entropy"]["relative_improvement"], green),
        ("joint address added value", primary["continuous_added_value"], blue),
        ("address → multiplicity", primary["joint_multiplicity"]["cross_entropy"]["relative_improvement"], blue),
        ("address → neutron timing", primary["timing"]["cross_entropy"]["relative_improvement"], orange),
    ]
    maximum = max(abs(v) for _, v, _ in effects)
    bx, by, bw = x + 255, y + 92, 330
    zero = bx + 35
    lines.append(f'<line x1="{zero}" y1="{by-20}" x2="{zero}" y2="{by+225}" stroke="#8993a1"/>')
    for i, (label, value, color) in enumerate(effects):
        yy = by + i * 62
        length = value / maximum * (bw - 55)
        start = zero if length >= 0 else zero + length
        lines.append(f'<rect x="{start}" y="{yy}" width="{abs(length)}" height="25" fill="{color}"/>')
        lines.append(f'<text x="{x+24}" y="{yy+18}" font-family="Segoe UI,Arial" font-size="14" fill="{ink}">{html.escape(label)}</text>')
        lines.append(f'<text x="{zero+length+8}" y="{yy+18}" font-family="Segoe UI,Arial" font-size="14" fill="{ink}">{100*value:+.4f}%</text>')

    lines.append(f'<text x="55" y="1005" font-family="Segoe UI,Arial" font-size="14" fill="{muted}">Source: Super-Kamiokande, Zenodo 10.5281/zenodo.15081911 · known prompt-gamma/neutron association separated from added ARA value</text>')
    lines.append("</svg>")
    FIGURE.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    momentum, prompt_time, multiplicity, first_neutron = parse_source(SOURCE)
    n = len(momentum)
    md5 = digest_file(SOURCE, "md5")
    sha256 = digest_file(SOURCE, "sha256")
    row_hash = stable_hashes(n)
    residue = row_hash % 10
    finite = np.isfinite(momentum) & np.isfinite(prompt_time)
    capture_enriched = finite & (momentum <= 15)
    development = capture_enriched & (residue <= 5)
    holdout = capture_enriched & (residue >= 6)
    prompt_present = (
        (momentum > 0)
        & (momentum <= 15)
        & (prompt_time >= 1.1)
        & (prompt_time <= 5.0)
    )
    neutron_present = multiplicity > 0
    multiplicity_class = np.minimum(multiplicity, 2).astype(np.int16)

    dev_prompt = development & prompt_present
    hold_prompt = holdout & prompt_present
    dev_both = dev_prompt & neutron_present
    hold_both = hold_prompt & neutron_present
    rng = np.random.default_rng(SEED)

    time_edges = edges(prompt_time[dev_prompt])
    energy_edges = edges(momentum[dev_prompt])
    dev_address = address(
        prompt_present[development],
        prompt_time[development],
        momentum[development],
        time_edges,
        energy_edges,
    )
    hold_address = address(
        prompt_present[holdout],
        prompt_time[holdout],
        momentum[holdout],
        time_edges,
        energy_edges,
    )
    dev_presence = prompt_present[development].astype(np.int16)
    hold_presence = prompt_present[holdout].astype(np.int16)
    dev_neutron = neutron_present[development].astype(np.int16)
    hold_neutron = neutron_present[holdout].astype(np.int16)
    dev_mult = multiplicity_class[development]
    hold_mult = multiplicity_class[holdout]

    common = evaluate(dev_presence, dev_neutron, hold_presence, hold_neutron, 2, 2)
    common_ci = bootstrap_binary(
        common["holdout_table"], common["conditional"], common["unconditional"], rng
    )
    common_perm = permute_binary_presence(
        hold_presence.astype(bool),
        hold_neutron.astype(bool),
        common["conditional"],
        common["unconditional"],
        common["cross_entropy"]["relative_improvement"],
        rng,
    )
    joint_binary = evaluate(dev_address, dev_neutron, hold_address, hold_neutron, 65, 2)
    continuous_added = effect_against_reference(
        joint_binary["cross_entropy"]["conditional"],
        common["cross_entropy"]["conditional"],
    )
    joint_multiplicity = evaluate(dev_address, dev_mult, hold_address, hold_mult, 65, 3)

    # Time-only and energy-only baselines, with zero reserved for prompt absence.
    dev_time_cat = np.zeros(development.sum(), dtype=np.int16)
    hold_time_cat = np.zeros(holdout.sum(), dtype=np.int16)
    dev_energy_cat = np.zeros(development.sum(), dtype=np.int16)
    hold_energy_cat = np.zeros(holdout.sum(), dtype=np.int16)
    dev_time_cat[dev_presence.astype(bool)] = 1 + bins(prompt_time[dev_prompt], time_edges)
    hold_time_cat[hold_presence.astype(bool)] = 1 + bins(prompt_time[hold_prompt], time_edges)
    dev_energy_cat[dev_presence.astype(bool)] = 1 + bins(momentum[dev_prompt], energy_edges)
    hold_energy_cat[hold_presence.astype(bool)] = 1 + bins(momentum[hold_prompt], energy_edges)
    time_only = evaluate(dev_time_cat, dev_neutron, hold_time_cat, hold_neutron, 9, 2)
    energy_only = evaluate(dev_energy_cat, dev_neutron, hold_energy_cat, hold_neutron, 9, 2)

    neutron_time_edges = edges(first_neutron[dev_both])
    dev_timing_address = 1 + bins(prompt_time[dev_both], time_edges) * 8 + bins(momentum[dev_both], energy_edges)
    hold_timing_address = 1 + bins(prompt_time[hold_both], time_edges) * 8 + bins(momentum[hold_both], energy_edges)
    dev_neutron_time_bin = bins(first_neutron[dev_both], neutron_time_edges)
    hold_neutron_time_bin = bins(first_neutron[hold_both], neutron_time_edges)
    timing = evaluate(
        dev_timing_address,
        dev_neutron_time_bin,
        hold_timing_address,
        hold_neutron_time_bin,
        65,
        8,
    )
    timing_shuffle = timing_shuffle_by_multiplicity(
        hold_timing_address,
        hold_neutron_time_bin,
        multiplicity_class[hold_both],
        timing["conditional"],
        timing["unconditional"],
        timing["cross_entropy"]["relative_improvement"],
        rng,
    )

    # Strict prompt-gamma window, with development-only coordinate maps.
    strict = prompt_present & (momentum > 5) & (momentum <= 15)
    strict_dev = development & strict
    strict_hold = holdout & strict
    strict_dev_both = strict_dev & neutron_present
    strict_hold_both = strict_hold & neutron_present
    strict_time_edges = edges(prompt_time[strict_dev])
    strict_energy_edges = edges(momentum[strict_dev])
    strict_neutron_edges = edges(first_neutron[strict_dev_both])
    strict_dev_address = 1 + bins(prompt_time[strict_dev_both], strict_time_edges) * 8 + bins(momentum[strict_dev_both], strict_energy_edges)
    strict_hold_address = 1 + bins(prompt_time[strict_hold_both], strict_time_edges) * 8 + bins(momentum[strict_hold_both], strict_energy_edges)
    strict_timing = evaluate(
        strict_dev_address,
        bins(first_neutron[strict_dev_both], strict_neutron_edges),
        strict_hold_address,
        bins(first_neutron[strict_hold_both], strict_neutron_edges),
        65,
        8,
    )

    # Same-row packet mismatch: circularly shift target packets on holdout.
    shift = len(hold_neutron) // 3 + 19
    mismatched_neutron = np.roll(hold_neutron, shift)
    mismatch_table = count_table(hold_presence, mismatched_neutron, 2, 2)
    mismatch_common = cross_entropy(
        mismatch_table, common["conditional"], common["unconditional"]
    )
    joint_packet_perm = packet_permutation_null(
        hold_address,
        hold_neutron,
        joint_binary["conditional"],
        joint_binary["unconditional"],
        joint_binary["cross_entropy"]["relative_improvement"],
        65,
        2,
        rng,
    )

    # Replication halves for the known common-parent relation.
    halves = {}
    for parity, name in [(0, "even_hash"), (1, "odd_hash")]:
        selection = holdout & ((row_hash & 1) == parity)
        test_table = count_table(
            prompt_present[selection].astype(np.int16),
            neutron_present[selection].astype(np.int16),
            2,
            2,
        )
        halves[name] = {
            "n": int(selection.sum()),
            "cross_entropy": cross_entropy(
                test_table, common["conditional"], common["unconditional"]
            ),
        }

    common_table = common["holdout_table"]
    neutron_rate_absent = common_table[0, 1] / common_table[0].sum()
    neutron_rate_present = common_table[1, 1] / common_table[1].sum()
    enrichment = neutron_rate_present / neutron_rate_absent

    # 8x8 probability map among prompt-present holdout events.
    prompt_table = np.zeros((8, 8), dtype=float)
    prompt_counts = np.zeros((8, 8), dtype=float)
    prompt_address = hold_address[hold_presence.astype(bool)] - 1
    for addr, target in zip(prompt_address, hold_neutron[hold_presence.astype(bool)]):
        t_bin, e_bin = divmod(int(addr), 8)
        prompt_table[t_bin, e_bin] += target
        prompt_counts[t_bin, e_bin] += 1
    prompt_probability = np.divide(
        prompt_table,
        prompt_counts,
        out=np.full_like(prompt_table, np.nan),
        where=prompt_counts > 0,
    )

    source_qa = {
        "rows": n,
        "expected_rows": EXPECTED_ROWS,
        "md5": md5,
        "sha256": sha256,
        "capture_enriched_rows": int(capture_enriched.sum()),
        "development_capture_enriched": int(development.sum()),
        "holdout_capture_enriched": int(holdout.sum()),
        "prompt_present_rows": int((capture_enriched & prompt_present).sum()),
        "prompt_present_holdout": int(hold_prompt.sum()),
        "prompt_plus_neutron_holdout": int(hold_both.sum()),
        "strict_prompt_plus_neutron_holdout": int(strict_hold_both.sum()),
        "neutron_rows": int(neutron_present.sum()),
    }
    timing_effect = timing["cross_entropy"]["relative_improvement"]
    strict_timing_effect = strict_timing["cross_entropy"]["relative_improvement"]
    gates = {
        "G1_source_QA": n == EXPECTED_ROWS and md5 == EXPECTED_MD5 and sha256 == EXPECTED_SHA256,
        "G2_coverage": int(hold_prompt.sum()) >= 5_000 and int(hold_both.sum()) >= 1_000,
        "G3_common_parent_recovery": common["cross_entropy"]["relative_improvement"] >= 0.01 and common_ci[0] > 0,
        "G4_same_row_specificity": common_perm["equal_or_greater"] <= 10,
        "G5_replication": all(value["cross_entropy"]["relative_improvement"] > 0 for value in halves.values()),
        "G6_continuous_added_value": continuous_added >= 0.005,
        "G7_multiplicity_information": joint_multiplicity["cross_entropy"]["relative_improvement"] >= 0.005,
        "G8_timing_relation": timing_effect >= 0.005 and timing_shuffle["equal_or_greater"] <= 10 and strict_timing_effect > 0,
    }
    if all(gates.values()):
        verdict = "DAUGHTER CLOSURE AND ADDED ARA RELATION SUPPORTED"
    elif all(gates[key] for key in list(gates)[:5]):
        if any(gates[key] for key in list(gates)[5:]):
            verdict = "COMMON-PARENT RECOVERED; PARTIAL ADDED RELATION; FULL CLOSURE NOT SUPPORTED"
        else:
            verdict = "COMMON-PARENT RELATION RECOVERED WITHOUT ADDED ARA VALUE"
    else:
        verdict = "COMMON-PARENT RELATION NOT RECOVERED"

    result = {
        "test": "T369 muon-capture daughter closure",
        "verdict": verdict,
        "source_qa": source_qa,
        "coordinate_edges": {
            "prompt_time_us": time_edges.tolist(),
            "prompt_momentum_mev": energy_edges.tolist(),
            "first_neutron_time_us": neutron_time_edges.tolist(),
        },
        "primary": {
            "common_parent": serializable(common),
            "common_parent_bootstrap_ci95": common_ci,
            "neutron_rate_prompt_absent": neutron_rate_absent,
            "neutron_rate_prompt_present": neutron_rate_present,
            "neutron_enrichment_ratio": enrichment,
            "joint_binary": serializable(joint_binary),
            "continuous_added_value": continuous_added,
            "joint_multiplicity": serializable(joint_multiplicity),
            "timing": serializable(timing),
            "joint_prompt_neutron_probability": prompt_probability.tolist(),
            "multiplicity_by_prompt_presence": count_table(hold_presence, hold_mult, 2, 3).tolist(),
        },
        "controls": {
            "common_parent_permutation": common_perm,
            "mismatched_common_parent": mismatch_common,
            "joint_packet_permutation": joint_packet_perm,
            "timing_multiplicity_preserving_shuffle": timing_shuffle,
            "strict_timing": serializable(strict_timing),
            "hash_halves": halves,
            "time_only": serializable(time_only),
            "energy_only": serializable(energy_only),
        },
        "gates": gates,
        "boundary": (
            "Prompt and neutron absence include detector non-detection; the source "
            "does not label true capture per row. P1 is a known-relation recovery."
        ),
    }
    result = serializable(result)
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")

    np.savez_compressed(
        DERIVED,
        source_row=np.flatnonzero(holdout) + 1,
        row_hash=row_hash[holdout],
        prompt_momentum_mev=momentum[holdout],
        prompt_time_us=prompt_time[holdout],
        neutron_multiplicity=multiplicity[holdout],
        first_neutron_time_us=first_neutron[holdout],
        prompt_address=hold_address,
    )
    pd.DataFrame(prompt_probability).to_csv(MIXING, index_label="prompt_time_bin")
    control_rows = [
        {"model": "prompt_presence", "relative_improvement": common["cross_entropy"]["relative_improvement"]},
        {"model": "joint_address", "relative_improvement": joint_binary["cross_entropy"]["relative_improvement"]},
        {"model": "joint_added_vs_presence", "relative_improvement": continuous_added},
        {"model": "time_only", "relative_improvement": time_only["cross_entropy"]["relative_improvement"]},
        {"model": "energy_only", "relative_improvement": energy_only["cross_entropy"]["relative_improvement"]},
        {
            "model": "joint_vs_energy_only",
            "relative_improvement": effect_against_reference(
                joint_binary["cross_entropy"]["conditional"],
                energy_only["cross_entropy"]["conditional"],
            ),
        },
        {"model": "multiplicity", "relative_improvement": joint_multiplicity["cross_entropy"]["relative_improvement"]},
        {"model": "neutron_timing", "relative_improvement": timing_effect},
        {"model": "strict_neutron_timing", "relative_improvement": strict_timing_effect},
    ]
    pd.DataFrame(control_rows).to_csv(CONTROLS, index=False)
    pd.DataFrame([{"gate": key, "passed": value} for key, value in gates.items()]).to_csv(GATES, index=False)
    make_svg(result)

    gate_lines = "\n".join(
        f"| {key.replace('_', ' ')} | **{'PASS' if value else 'FAIL'}** |"
        for key, value in gates.items()
    )
    report = f"""# T369 - Muon-capture daughter closure

**Date:** 12 August 2026  
**Frozen verdict:** **{verdict}**

## Result first

The known same-parent relation was tested on **{int(holdout.sum()):,}** untouched
capture-enriched stopped-muon rows. Prompt gamma-like presence improved
neutron-presence cross-entropy by
**{100*common['cross_entropy']['relative_improvement']:+.4f}%**
(bootstrap 95% interval **[{100*common_ci[0]:+.4f}%, {100*common_ci[1]:+.4f}%]**).
Prompt-present rows had a tagged-neutron rate of **{100*neutron_rate_present:.3f}%**,
versus **{100*neutron_rate_absent:.3f}%** when the prompt child was absent: an
enrichment of **{enrichment:.3f}x**.

The frozen joint prompt-time x prompt-energy Di-ARA address added
**{100*continuous_added:+.4f}%** predictive value beyond prompt presence alone.
It improved three-class neutron-multiplicity prediction by
**{100*joint_multiplicity['cross_entropy']['relative_improvement']:+.4f}%** over
the unconditional model, and first-neutron timing prediction by
**{100*timing_effect:+.4f}%**.

However, prompt energy alone performed **{100*energy_only['cross_entropy']['relative_improvement']:+.4f}%**,
slightly better than the joint address's **{100*joint_binary['cross_entropy']['relative_improvement']:+.4f}%**.
The observed added signal is therefore energy-led; this test did not recover a
two-coordinate timing-energy mixing advantage.

## Plain-language ARA reading

The public record clearly retains the common-parent handover: seeing the prompt
capture child changes the probability of seeing the delayed neutron child from
that stopped muon. This is expected physics and validates the cut.

The stronger question is whether the precise prompt child's position carries
additional relation beyond its mere presence. The frozen gates below decide
that separately; recovering the known relation cannot rescue a failed deeper
claim.

## Population QA

- Source rows: **{n:,}**
- Capture-enriched holdout: **{int(holdout.sum()):,}**
- Prompt-present holdout: **{int(hold_prompt.sum()):,}**
- Prompt-plus-neutron holdout: **{int(hold_both.sum()):,}**
- Source MD5: `{md5}`
- Source SHA256: `{sha256}`

## Frozen gates

| gate | result |
|---|---:|
{gate_lines}

## Controls

- Common-parent permutation exceedances: **{common_perm['equal_or_greater']} / {N_RESAMPLES}**
- Mismatched-packet common-parent effect: **{100*mismatch_common['relative_improvement']:+.4f}%**
- Timing-shuffle exceedances: **{timing_shuffle['equal_or_greater']} / {N_RESAMPLES}**
- Strict `5-15 MeV` timing effect: **{100*strict_timing_effect:+.4f}%**
- Time-only neutron-presence effect: **{100*time_only['cross_entropy']['relative_improvement']:+.4f}%**
- Energy-only neutron-presence effect: **{100*energy_only['cross_entropy']['relative_improvement']:+.4f}%**

## Scientific boundary

The source does not label true nuclear capture per row. Prompt absence and
neutron absence include detector inefficiency, and first-neutron time is a
thermalisation/detection coordinate long after the prompt handover. The source
paper itself uses high-energy gamma candidates as a predominantly
single-neutron reference, so recovering the binary association is a crosswalk,
not a new discovery.

## Reproduction

```powershell
& 'C:\\Users\\Dylan\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe' `
  'F:\\SystemFormulaFolder\\GIT\\ARA-GIT\\analysis\\muon\\t369_muon_capture_daughter_closure.py'
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(serializable({"verdict": verdict, "gates": gates, "qa": source_qa}), indent=2))


if __name__ == "__main__":
    main()
