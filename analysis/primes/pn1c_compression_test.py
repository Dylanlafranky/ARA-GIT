"""PN1C parameter-matched primorial-wheel compression competition.

Registration: T228 in MASTER_PREDICTION_LEDGER.md
Frozen protocol: PN1C_COMPRESSION_PROTOCOL_v1_FROZEN.md
Protocol SHA256: 7DAA061BA790B12461ED60136FD9C50F3A36C10BED472819CFCC08B4B3462DBF

The exact 19->23 target is streamed in ordered lift blocks.  The prime-23
wheel must not be generated or inspected before the protocol and ledger entry
above exist.
"""

from __future__ import annotations

import hashlib
import json
import math
import platform
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from pn1_sieve_rung_test import Wheel, generate_wheel, js_divergence_bits


HERE = Path(__file__).resolve().parent
PROTOCOL_PATH = HERE / "PN1C_COMPRESSION_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA256 = "7DAA061BA790B12461ED60136FD9C50F3A36C10BED472819CFCC08B4B3462DBF"
PRIMES_TO_PARENT = (2, 3, 5, 7, 11, 13, 17, 19)
NEXT_PRIME = 23
FINE_BINS = 24
PRIMARY_COARSE_BINS = 6
PRIMARY_SLOT_CEILING = 36
TOP_CONSTELLATIONS = 9
LOG_RANGE = math.log(32.0)
EXPECTED_CHILD_PERIOD = 223_092_870
EXPECTED_CHILD_SLOTS = 36_495_360
INDEPENDENT_RESIDUE_CHUNK = 137_911
POST_OPEN_REPAIR = (
    "2026-07-17: serialization-only repair after the first complete target run; "
    "pandas converted the zero-slot Uniform reference's undefined gain-per-slot "
    "from None to NaN, which strict JSON rejects. No counts, predictions, scores, "
    "model definitions, budgets, or pass criteria changed."
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def json_safe(value: object) -> object:
    """Convert NumPy scalars and non-finite display values to strict JSON values."""
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return float(value) if math.isfinite(float(value)) else None
    return value


def relation_bin(left: np.ndarray, right: np.ndarray, bins: int) -> np.ndarray:
    values = 2.0 * right.astype(np.float64) / (left.astype(np.float64) + right)
    return np.minimum((values * (bins / 2.0)).astype(np.int64), bins - 1)


def triple_count_matrix(gaps: np.ndarray, bins: int = FINE_BINS) -> np.ndarray:
    first = gaps.astype(np.int64, copy=False)
    second = np.roll(first, -1)
    third = np.roll(first, -2)
    row = relation_bin(first, second, bins)
    column = relation_bin(second, third, bins)
    return np.bincount(row * bins + column, minlength=bins * bins).reshape(bins, bins)


@dataclass
class StreamedTarget:
    counts: np.ndarray
    half_counts: np.ndarray
    survivor_count: int
    gap_count: int
    gap_sum: int
    min_gap: int
    max_gap: int
    all_even: bool
    gap_sha256: str


class TripleStreamAccumulator:
    def __init__(self, bins: int, expected_count: int):
        self.bins = bins
        self.expected_count = expected_count
        self.counts = np.zeros((bins, bins), dtype=np.int64)
        self.half_counts = np.zeros((2, bins, bins), dtype=np.int64)
        self.carry = np.empty(0, dtype=np.int32)
        self.first_two = np.empty(0, dtype=np.int32)
        self.completed = 0

    def add(self, gap_chunk: np.ndarray) -> None:
        chunk = np.asarray(gap_chunk, dtype=np.int32)
        if chunk.size == 0:
            return
        if self.first_two.size < 2:
            needed = 2 - self.first_two.size
            self.first_two = np.concatenate((self.first_two, chunk[:needed]))
        combined = np.concatenate((self.carry, chunk)) if self.carry.size else chunk
        triple_count = max(0, combined.size - 2)
        if triple_count:
            first = combined[:-2].astype(np.int64, copy=False)
            second = combined[1:-1].astype(np.int64, copy=False)
            third = combined[2:].astype(np.int64, copy=False)
            row = relation_bin(first, second, self.bins)
            column = relation_bin(second, third, self.bins)
            codes = row * self.bins + column
            self.counts += np.bincount(
                codes, minlength=self.bins * self.bins
            ).reshape(self.bins, self.bins)

            start = self.completed
            stop = start + triple_count
            half_boundary = self.expected_count // 2
            if start < half_boundary:
                take = min(stop, half_boundary) - start
                self.half_counts[0] += np.bincount(
                    codes[:take], minlength=self.bins * self.bins
                ).reshape(self.bins, self.bins)
            if stop > half_boundary:
                offset = max(0, half_boundary - start)
                self.half_counts[1] += np.bincount(
                    codes[offset:], minlength=self.bins * self.bins
                ).reshape(self.bins, self.bins)
            self.completed = stop
        self.carry = combined[-2:].astype(np.int32, copy=True)

    def close_circle(self) -> None:
        if self.first_two.size != 2:
            raise AssertionError("Insufficient gaps to close the circular relation")
        self.add(self.first_two)
        if self.completed != self.expected_count:
            raise AssertionError(
                f"Circular triple count {self.completed} != {self.expected_count}"
            )


def stream_child_target(
    parent: Wheel, residue_chunk_size: int | None, label: str
) -> StreamedTarget:
    accumulator = TripleStreamAccumulator(FINE_BINS, EXPECTED_CHILD_SLOTS)
    digest = hashlib.sha256()
    survivor_count = 0
    gap_count = 0
    gap_sum = 0
    min_gap = np.iinfo(np.int32).max
    max_gap = 0
    all_even = True
    first_survivor: int | None = None
    previous_survivor: int | None = None

    def emit_survivors(survivors: np.ndarray) -> None:
        nonlocal survivor_count, gap_count, gap_sum, min_gap, max_gap
        nonlocal all_even, first_survivor, previous_survivor
        if survivors.size == 0:
            return
        survivors = np.asarray(survivors, dtype=np.int64)
        survivor_count += int(survivors.size)
        if first_survivor is None:
            first_survivor = int(survivors[0])
            gaps = np.diff(survivors)
        else:
            boundary = np.array([int(survivors[0]) - int(previous_survivor)], dtype=np.int64)
            gaps = np.concatenate((boundary, np.diff(survivors)))
        previous_survivor = int(survivors[-1])
        if gaps.size:
            gaps32 = gaps.astype(np.int32)
            digest.update(gaps32.tobytes(order="C"))
            accumulator.add(gaps32)
            gap_count += int(gaps32.size)
            gap_sum += int(gaps32.sum(dtype=np.int64))
            min_gap = min(min_gap, int(gaps32.min()))
            max_gap = max(max_gap, int(gaps32.max()))
            all_even = bool(all_even and np.all(gaps32 % 2 == 0))

    for lift in range(NEXT_PRIME):
        offset = lift * parent.period
        if residue_chunk_size is None:
            candidates = parent.residues + offset
            emit_survivors(candidates[candidates % NEXT_PRIME != 0])
        else:
            for start in range(0, len(parent.residues), residue_chunk_size):
                candidates = parent.residues[start : start + residue_chunk_size] + offset
                emit_survivors(candidates[candidates % NEXT_PRIME != 0])
        if lift in (0, 5, 11, 17, 22):
            print(
                f"  {label}: completed lift {lift + 1}/{NEXT_PRIME}; "
                f"survivors={survivor_count:,}",
                flush=True,
            )

    if first_survivor is None or previous_survivor is None:
        raise AssertionError("No child survivors generated")
    wrap = np.array(
        [EXPECTED_CHILD_PERIOD + first_survivor - previous_survivor], dtype=np.int32
    )
    digest.update(wrap.tobytes(order="C"))
    accumulator.add(wrap)
    gap_count += 1
    gap_sum += int(wrap[0])
    min_gap = min(min_gap, int(wrap[0]))
    max_gap = max(max_gap, int(wrap[0]))
    all_even = bool(all_even and int(wrap[0]) % 2 == 0)
    accumulator.close_circle()

    return StreamedTarget(
        counts=accumulator.counts,
        half_counts=accumulator.half_counts,
        survivor_count=survivor_count,
        gap_count=gap_count,
        gap_sum=gap_sum,
        min_gap=min_gap,
        max_gap=max_gap,
        all_even=all_even,
        gap_sha256=digest.hexdigest().upper(),
    )


def normalize(matrix: np.ndarray) -> np.ndarray:
    result = np.asarray(matrix, dtype=np.float64)
    if not np.all(np.isfinite(result)) or np.any(result < 0):
        raise AssertionError("Prediction contains invalid probability mass")
    total = float(result.sum())
    if total <= 0:
        raise AssertionError("Prediction has no probability mass")
    return result / total


def decode_partition(parent: np.ndarray, assignments: np.ndarray, groups: int) -> np.ndarray:
    parent = normalize(parent)
    coarse = np.zeros((groups, groups), dtype=np.float64)
    for row in range(parent.shape[0]):
        for column in range(parent.shape[1]):
            coarse[assignments[row], assignments[column]] += parent[row, column]
    sizes = np.bincount(assignments, minlength=groups)
    if np.any(sizes == 0):
        raise AssertionError("Partition created an empty group")
    decoded = np.zeros_like(parent)
    for row in range(parent.shape[0]):
        for column in range(parent.shape[1]):
            group_row = assignments[row]
            group_column = assignments[column]
            decoded[row, column] = coarse[group_row, group_column] / (
                sizes[group_row] * sizes[group_column]
            )
    return normalize(decoded)


def ara_assignments(fine_bins: int, groups: int) -> np.ndarray:
    return np.minimum(np.arange(fine_bins) * groups // fine_bins, groups - 1)


def log_assignments(fine_bins: int, groups: int) -> np.ndarray:
    centers = 2.0 * (np.arange(fine_bins) + 0.5) / fine_bins
    log_ratio = np.log(centers / (2.0 - centers))
    internal_edges = LOG_RANGE * (2.0 * np.arange(1, groups) / groups - 1.0)
    return np.digitize(log_ratio, internal_edges).astype(np.int64)


def dct_basis(size: int) -> np.ndarray:
    points = np.arange(size, dtype=np.float64)
    frequencies = np.arange(size, dtype=np.float64)[:, None]
    basis = np.cos(math.pi * (points + 0.5) * frequencies / size)
    basis[0] *= math.sqrt(1.0 / size)
    basis[1:] *= math.sqrt(2.0 / size)
    return basis


def dct_prediction(parent: np.ndarray, retained: int) -> np.ndarray:
    parent = normalize(parent)
    basis = dct_basis(parent.shape[0])
    coefficients = basis @ parent @ basis.T
    truncated = np.zeros_like(coefficients)
    truncated[:retained, :retained] = coefficients[:retained, :retained]
    decoded = basis.T @ truncated @ basis
    decoded = np.clip(decoded, 0.0, None)
    return normalize(decoded)


def learned_quantile_assignments(
    development_wheels: list[Wheel], fine_bins: int, groups: int
) -> tuple[np.ndarray, list[int]]:
    pooled = np.zeros((fine_bins, fine_bins), dtype=np.int64)
    for wheel in development_wheels:
        pooled += triple_count_matrix(wheel.gaps, fine_bins)
    weights = pooled.sum(axis=0) + pooled.sum(axis=1)
    cumulative = np.cumsum(weights, dtype=np.float64)
    cumulative /= cumulative[-1]
    cuts: list[int] = []
    previous = 0
    for group_index in range(1, groups):
        raw = int(np.searchsorted(cumulative, group_index / groups, side="left") + 1)
        lower = previous + 1
        upper = fine_bins - (groups - group_index)
        cut = min(max(raw, lower), upper)
        cuts.append(cut)
        previous = cut
    assignments = np.digitize(np.arange(fine_bins), cuts).astype(np.int64)
    return assignments, cuts


def gap_alphabet(gaps: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    labels, inverse, counts = np.unique(gaps, return_inverse=True, return_counts=True)
    probabilities = counts.astype(np.float64) / counts.sum()
    return labels.astype(np.int32), inverse.astype(np.int32), probabilities


def project_gap_process(
    labels: np.ndarray,
    marginal: np.ndarray,
    transition: np.ndarray | None,
    bins: int,
) -> np.ndarray:
    matrix = np.zeros((bins, bins), dtype=np.float64)
    for a_index, a in enumerate(labels):
        for b_index, b in enumerate(labels):
            first_probability = (
                marginal[a_index] * marginal[b_index]
                if transition is None
                else marginal[a_index] * transition[a_index, b_index]
            )
            if first_probability == 0:
                continue
            for c_index, c in enumerate(labels):
                probability = (
                    first_probability * marginal[c_index]
                    if transition is None
                    else first_probability * transition[b_index, c_index]
                )
                if probability == 0:
                    continue
                row = min(int((2.0 * float(b) / (float(a) + float(b))) * bins / 2.0), bins - 1)
                column = min(int((2.0 * float(c) / (float(b) + float(c))) * bins / 2.0), bins - 1)
                matrix[row, column] += probability
    return normalize(matrix)


def markov_transition(inverse: np.ndarray, alphabet_size: int) -> np.ndarray:
    following = np.roll(inverse, -1)
    counts = np.bincount(
        inverse.astype(np.int64) * alphabet_size + following,
        minlength=alphabet_size * alphabet_size,
    ).reshape(alphabet_size, alphabet_size)
    row_sums = counts.sum(axis=1, keepdims=True)
    if np.any(row_sums == 0):
        raise AssertionError("Gap Markov model has an empty row")
    return counts / row_sums


def constellation_prediction(
    gaps: np.ndarray,
    labels: np.ndarray,
    inverse: np.ndarray,
    bins: int,
    top_k: int,
) -> tuple[np.ndarray, list[dict[str, object]]]:
    alphabet_size = len(labels)
    codes = (
        inverse.astype(np.int64) * alphabet_size * alphabet_size
        + np.roll(inverse, -1).astype(np.int64) * alphabet_size
        + np.roll(inverse, -2)
    )
    counts = np.bincount(codes, minlength=alphabet_size**3)
    order = np.lexsort((np.arange(counts.size), -counts))
    selected = order[:top_k]
    selected_probability = counts[selected].astype(np.float64) / len(gaps)
    residual = 1.0 - float(selected_probability.sum())
    prediction = np.full((bins, bins), residual / (bins * bins), dtype=np.float64)
    details: list[dict[str, object]] = []
    for code, probability in zip(selected, selected_probability, strict=True):
        a_index = int(code // (alphabet_size * alphabet_size))
        remainder = int(code % (alphabet_size * alphabet_size))
        b_index = remainder // alphabet_size
        c_index = remainder % alphabet_size
        a, b, c = int(labels[a_index]), int(labels[b_index]), int(labels[c_index])
        row = min(int((2.0 * b / (a + b)) * bins / 2.0), bins - 1)
        column = min(int((2.0 * c / (b + c)) * bins / 2.0), bins - 1)
        prediction[row, column] += float(probability)
        details.append(
            {
                "g1": a,
                "g2": b,
                "g3": c,
                "parent_probability": float(probability),
                "row_bin": row,
                "column_bin": column,
            }
        )
    return normalize(prediction), details


def pair_jsd_mean(target: np.ndarray, prediction: np.ndarray) -> float:
    return 0.5 * (
        js_divergence_bits(target.sum(axis=0), prediction.sum(axis=0))
        + js_divergence_bits(target.sum(axis=1), prediction.sum(axis=1))
    )


def build_primary_models(
    parent_probability: np.ndarray,
    parent: Wheel,
    development_wheels: list[Wheel],
) -> tuple[dict[str, np.ndarray], dict[str, int], list[int], list[dict[str, object]], int]:
    labels, inverse, marginal = gap_alphabet(parent.gaps)
    iid_slots = 2 * len(labels) - 1
    if iid_slots > PRIMARY_SLOT_CEILING:
        raise AssertionError(
            f"Frozen Gap-IID budget breached: {iid_slots} > {PRIMARY_SLOT_CEILING}"
        )
    learned, learned_cuts = learned_quantile_assignments(
        development_wheels, FINE_BINS, 5
    )
    constellation, constellation_details = constellation_prediction(
        parent.gaps, labels, inverse, FINE_BINS, TOP_CONSTELLATIONS
    )
    transition = markov_transition(inverse, len(labels))
    models = {
        "ARA-linear-6": decode_partition(
            parent_probability,
            ara_assignments(FINE_BINS, PRIMARY_COARSE_BINS),
            PRIMARY_COARSE_BINS,
        ),
        "Log-ratio-6": decode_partition(
            parent_probability,
            log_assignments(FINE_BINS, PRIMARY_COARSE_BINS),
            PRIMARY_COARSE_BINS,
        ),
        "DCT-6": dct_prediction(parent_probability, PRIMARY_COARSE_BINS),
        "Learned-quantile-5": decode_partition(parent_probability, learned, 5),
        "Gap-IID": project_gap_process(labels, marginal, None, FINE_BINS),
        "Top-9 constellations": constellation,
        "Uniform": np.full((FINE_BINS, FINE_BINS), 1.0 / (FINE_BINS**2)),
        "Gap-Markov": project_gap_process(labels, marginal, transition, FINE_BINS),
        "Exact parent relation": normalize(parent_probability),
    }
    slots = {
        "ARA-linear-6": 35,
        "Log-ratio-6": 35,
        "DCT-6": 36,
        "Learned-quantile-5": 28,
        "Gap-IID": iid_slots,
        "Top-9 constellations": 36,
        "Uniform": 0,
        "Gap-Markov": len(labels) ** 2 + len(labels) - 1,
        "Exact parent relation": FINE_BINS**2 - 1,
    }
    return models, slots, learned_cuts, constellation_details, len(labels)


def make_figure(scores: pd.DataFrame, frontier: pd.DataFrame, path: Path) -> None:
    width, height = 1800, 880
    image = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(image)

    def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
        candidates = (
            [Path("C:/Windows/Fonts/arialbd.ttf"), Path("C:/Windows/Fonts/arial.ttf")]
            if bold
            else [Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/calibri.ttf")]
        )
        for candidate in candidates:
            if candidate.exists():
                return ImageFont.truetype(str(candidate), size=size)
        return ImageFont.load_default()

    title_font = font(34, True)
    panel_font = font(23, True)
    label_font = font(17)
    small_font = font(14)
    ink, muted, grid = "#20262e", "#616975", "#d9dde3"
    blue, blue_dark = "#2f6f9f", "#244c6a"
    gold, gold_dark = "#e7b65a", "#8f6725"
    grey, grey_dark = "#c8cdd4", "#6d737c"
    orange = "#d77942"

    draw.text((55, 28), "PN1C parameter-matched compression test", fill=ink, font=title_font)
    draw.text(
        (55, 72),
        "Held-out primorial transition 19→23; primary target is the 24×24 overlapping relation distribution",
        fill=muted,
        font=label_font,
    )
    left = (55, 125, 920, 825)
    right = (950, 125, 1745, 825)
    for panel in (left, right):
        draw.rounded_rectangle(panel, radius=10, outline="#c8cdd4", width=2, fill="#fbfcfd")

    draw.text((85, 150), "Held-out prediction distance", fill=ink, font=panel_font)
    ordered = scores.sort_values("jsd_bits", ascending=True).reset_index(drop=True)
    plot_left, plot_right = 340, 875
    plot_top, plot_bottom = 215, 765
    maximum = float(ordered["jsd_bits"].max()) * 1.08
    for tick in range(6):
        value = maximum * tick / 5
        x = int(plot_left + value / maximum * (plot_right - plot_left))
        draw.line((x, plot_top, x, plot_bottom), fill=grid, width=1)
        draw.text((x - 18, plot_bottom + 12), f"{value:.3f}", fill=muted, font=small_font)
    row_height = (plot_bottom - plot_top) / len(ordered)
    for index, row in ordered.iterrows():
        center = int(plot_top + row_height * (index + 0.5))
        bar_end = int(plot_left + row["jsd_bits"] / maximum * (plot_right - plot_left))
        if row["model"] == "ARA-linear-6":
            fill, outline = blue, blue_dark
        elif bool(row["eligible_primary"]):
            fill, outline = gold, gold_dark
        else:
            fill, outline = grey, grey_dark
        draw.rectangle((plot_left, center - 13, bar_end, center + 13), fill=fill, outline=outline)
        draw.text((75, center - 10), str(row["model"]), fill=ink, font=small_font)
        draw.text((bar_end + 8, center - 10), f"{row['jsd_bits']:.5f}", fill=outline, font=small_font)
    draw.text((390, 795), "Jensen–Shannon divergence (bits; lower is better)", fill=muted, font=small_font)

    draw.text((980, 150), "Budget frontier for fixed coordinate summaries", fill=ink, font=panel_font)
    plot = (1030, 230, 1690, 700)
    max_frontier = float(frontier["jsd_bits"].max()) * 1.10
    for tick in range(6):
        value = max_frontier * tick / 5
        y = int(plot[3] - value / max_frontier * (plot[3] - plot[1]))
        draw.line((plot[0], y, plot[2], y), fill=grid, width=1)
        draw.text((plot[0] - 55, y - 8), f"{value:.3f}", fill=muted, font=small_font)
    draw.line((plot[0], plot[1], plot[0], plot[3]), fill=ink, width=2)
    draw.line((plot[0], plot[3], plot[2], plot[3]), fill=ink, width=2)
    palette = {"ARA-linear": blue, "Log-ratio": gold_dark, "DCT": orange}
    for model, group in frontier.groupby("family", sort=False):
        group = group.sort_values("retained_side")
        points = []
        for _, row in group.iterrows():
            x = int(plot[0] + (row["retained_side"] - 4) / 4 * (plot[2] - plot[0]))
            y = int(plot[3] - row["jsd_bits"] / max_frontier * (plot[3] - plot[1]))
            points.append((x, y))
            draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill=palette[model], outline=ink)
            draw.text((x - 10, plot[3] + 12), str(int(row["retained_side"])), fill=muted, font=small_font)
        draw.line(points, fill=palette[model], width=4)
    legend_x = 1110
    for index, model in enumerate(("ARA-linear", "Log-ratio", "DCT")):
        y = 770 + index * 24
        draw.line((legend_x, y, legend_x + 28, y), fill=palette[model], width=4)
        draw.text((legend_x + 38, y - 9), model, fill=ink, font=small_font)
    draw.text(
        ((plot[0] + plot[2]) // 2, plot[3] + 35),
        "retained grid/basis side (4, 6, 8)",
        fill=muted,
        font=small_font,
        anchor="mm",
    )
    image.save(path, format="PNG")


def run_analysis(output_dir: Path | None = None) -> dict[str, object]:
    output_dir = Path(output_dir) if output_dir is not None else HERE
    output_dir.mkdir(parents=True, exist_ok=True)
    protocol_hash = sha256_file(PROTOCOL_PATH)
    if protocol_hash != PROTOCOL_SHA256:
        raise RuntimeError(f"Protocol hash mismatch: {protocol_hash} != {PROTOCOL_SHA256}")

    wheels: dict[int, Wheel] = {}
    active: list[int] = []
    for prime in PRIMES_TO_PARENT:
        active.append(prime)
        if prime in (13, 17, 19):
            wheels[prime] = generate_wheel(tuple(active))
    parent = wheels[19]
    parent_counts = triple_count_matrix(parent.gaps, FINE_BINS)
    parent_probability = normalize(parent_counts)

    models, slots, learned_cuts, constellation_details, alphabet_size = build_primary_models(
        parent_probability, parent, [wheels[13], wheels[17], wheels[19]]
    )

    # This line opens the held-out prime-23 target for the first and only primary run.
    target_primary = stream_child_target(parent, residue_chunk_size=None, label="primary stream")
    target_independent = stream_child_target(
        parent,
        residue_chunk_size=INDEPENDENT_RESIDUE_CHUNK,
        label="independent chunked stream",
    )
    target_probability = normalize(target_primary.counts)

    exact_checks = {
        "protocol_hash_matches": protocol_hash == PROTOCOL_SHA256,
        "parent_gap_count_exact": len(parent.gaps) == math.prod(p - 1 for p in PRIMES_TO_PARENT),
        "parent_gap_sum_exact": int(parent.gaps.sum(dtype=np.int64)) == parent.period,
        "child_survivor_count_exact": target_primary.survivor_count == EXPECTED_CHILD_SLOTS,
        "child_gap_count_exact": target_primary.gap_count == EXPECTED_CHILD_SLOTS,
        "child_gap_sum_exact": target_primary.gap_sum == EXPECTED_CHILD_PERIOD,
        "child_gaps_positive": target_primary.min_gap > 0,
        "child_gaps_even": target_primary.all_even,
        "child_survivor_multiplier_exact": target_primary.survivor_count
        == (NEXT_PRIME - 1) * len(parent.residues),
        "independent_target_counts_equal": np.array_equal(
            target_primary.counts, target_independent.counts
        ),
        "independent_half_counts_equal": np.array_equal(
            target_primary.half_counts, target_independent.half_counts
        ),
        "independent_gap_hash_equal": target_primary.gap_sha256
        == target_independent.gap_sha256,
        "all_predictions_valid": all(
            np.all(np.isfinite(prediction))
            and np.all(prediction >= 0)
            and abs(float(prediction.sum()) - 1.0) <= 1e-12
            for prediction in models.values()
        ),
    }
    all_exact_checks_pass = all(exact_checks.values())

    eligible_names = {
        "ARA-linear-6",
        "Log-ratio-6",
        "DCT-6",
        "Learned-quantile-5",
        "Gap-IID",
        "Top-9 constellations",
    }
    uniform_jsd = js_divergence_bits(target_probability.ravel(), models["Uniform"].ravel())
    score_rows: list[dict[str, object]] = []
    orientation_errors: list[float] = []
    for model_name, prediction in models.items():
        jsd = js_divergence_bits(target_probability.ravel(), prediction.ravel())
        reversed_jsd = js_divergence_bits(
            target_probability[::-1, ::-1].ravel(), prediction[::-1, ::-1].ravel()
        )
        orientation_error = abs(jsd - reversed_jsd)
        orientation_errors.append(orientation_error)
        slot_count = slots[model_name]
        score_rows.append(
            {
                "model": model_name,
                "slots": slot_count,
                "eligible_primary": model_name in eligible_names,
                "jsd_bits": jsd,
                "pair_jsd_mean_bits": pair_jsd_mean(target_probability, prediction),
                "gain_over_uniform_bits": uniform_jsd - jsd,
                "gain_over_uniform_per_slot": (
                    (uniform_jsd - jsd) / slot_count if slot_count else None
                ),
                "orientation_reversal_abs_error": orientation_error,
            }
        )
    scores = pd.DataFrame(score_rows).sort_values("jsd_bits").reset_index(drop=True)

    ara_jsd = float(scores.loc[scores["model"] == "ARA-linear-6", "jsd_bits"].iloc[0])
    rival_scores = scores[
        scores["eligible_primary"] & (scores["model"] != "ARA-linear-6")
    ]
    best_rival_row = rival_scores.sort_values("jsd_bits").iloc[0]
    best_rival_jsd = float(best_rival_row["jsd_bits"])
    relative_margin = (best_rival_jsd - ara_jsd) / best_rival_jsd
    split_rows: list[dict[str, object]] = []
    for half_index in range(2):
        half_target = normalize(target_primary.half_counts[half_index])
        ara_half_jsd = js_divergence_bits(
            half_target.ravel(), models["ARA-linear-6"].ravel()
        )
        iid_half_jsd = js_divergence_bits(half_target.ravel(), models["Gap-IID"].ravel())
        split_rows.append(
            {
                "half": half_index + 1,
                "target_triples": int(target_primary.half_counts[half_index].sum()),
                "ara_jsd_bits": ara_half_jsd,
                "gap_iid_jsd_bits": iid_half_jsd,
                "ara_beats_gap_iid": ara_half_jsd < iid_half_jsd,
            }
        )
    split_df = pd.DataFrame(split_rows)
    split_robustness_pass = bool(split_df["ara_beats_gap_iid"].all())

    frontier_rows: list[dict[str, object]] = []
    for retained in (4, 6, 8):
        frontier_models = {
            "ARA-linear": decode_partition(
                parent_probability, ara_assignments(FINE_BINS, retained), retained
            ),
            "Log-ratio": decode_partition(
                parent_probability, log_assignments(FINE_BINS, retained), retained
            ),
            "DCT": dct_prediction(parent_probability, retained),
        }
        for family, prediction in frontier_models.items():
            frontier_rows.append(
                {
                    "family": family,
                    "retained_side": retained,
                    "slots": retained * retained - (0 if family == "DCT" else 1),
                    "jsd_bits": js_divergence_bits(
                        target_probability.ravel(), prediction.ravel()
                    ),
                }
            )
    frontier_df = pd.DataFrame(frontier_rows)

    exact_checks["orientation_reversal_all_invariant"] = max(orientation_errors) <= 1e-12
    all_exact_checks_pass = all(exact_checks.values())
    primary_claim_pass = bool(
        all_exact_checks_pass
        and ara_jsd < best_rival_jsd
        and relative_margin >= 0.01
        and int(scores[scores["eligible_primary"]]["slots"].max()) <= PRIMARY_SLOT_CEILING
    )
    if not all_exact_checks_pass:
        rating = "INVALID IMPLEMENTATION"
    elif primary_claim_pass:
        rating = (
            "SUPPORTED [pre-registered, arithmetic, unreplicated]"
            if split_robustness_pass
            else "SUPPORTED PRIMARY / SPLIT ROBUSTNESS FAILED"
        )
    else:
        rating = "NOT SUPPORTED [pre-registered compression advantage]"

    calibration_rows = [
        {"check": name, "passes": bool(value)} for name, value in exact_checks.items()
    ]
    results: dict[str, object] = {
        "test_id": "T228 / PN1C/v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "orientation": "up = larger primorial period / later sieve rung",
        "protocol_path": "analysis/primes/PN1C_COMPRESSION_PROTOCOL_v1_FROZEN.md",
        "protocol_sha256_expected": PROTOCOL_SHA256,
        "protocol_sha256_observed": protocol_hash,
        "post_open_implementation_repair": POST_OPEN_REPAIR,
        "holdout_transition": "19->23",
        "target": {
            "fine_bins": FINE_BINS,
            "child_period": EXPECTED_CHILD_PERIOD,
            "child_slots": target_primary.survivor_count,
            "gap_count": target_primary.gap_count,
            "gap_sum": target_primary.gap_sum,
            "min_gap": target_primary.min_gap,
            "max_gap": target_primary.max_gap,
            "gap_sha256": target_primary.gap_sha256,
        },
        "budget": {
            "unit": "declared scalar slots",
            "primary_ceiling": PRIMARY_SLOT_CEILING,
            "learned_boundary_bins": learned_cuts,
            "parent_gap_alphabet_size": alphabet_size,
        },
        "scores": scores.to_dict(orient="records"),
        "frontier": frontier_df.to_dict(orient="records"),
        "split_half": split_rows,
        "top_constellations": constellation_details,
        "calibration": calibration_rows,
        "summary": {
            "all_exact_checks_pass": all_exact_checks_pass,
            "primary_claim_pass": primary_claim_pass,
            "ara_jsd_bits": ara_jsd,
            "best_rival": str(best_rival_row["model"]),
            "best_rival_jsd_bits": best_rival_jsd,
            "ara_relative_margin_vs_best_rival": relative_margin,
            "split_robustness_pass": split_robustness_pass,
            "rating": rating,
            "evidence_ceiling": (
                "One finite deterministic arithmetic transition; compression slots are a "
                "parameter-count proxy, not literal bytes. No RH or physical inference."
            ),
        },
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
        },
    }

    scores.to_csv(output_dir / "PN1C_MODEL_SCORES.csv", index=False)
    frontier_df.to_csv(output_dir / "PN1C_BUDGET_FRONTIER.csv", index=False)
    split_df.to_csv(output_dir / "PN1C_SPLIT_HALF.csv", index=False)
    pd.DataFrame(calibration_rows).to_csv(
        output_dir / "PN1C_CALIBRATION_CHECKS.csv", index=False
    )
    pd.DataFrame(constellation_details).to_csv(
        output_dir / "PN1C_TOP_CONSTELLATIONS.csv", index=False
    )
    np.savez_compressed(
        output_dir / "PN1C_TARGET_AND_PREDICTIONS.npz",
        target_counts=target_primary.counts,
        target_half_counts=target_primary.half_counts,
        parent_counts=parent_counts,
        **{f"prediction_{name.replace(' ', '_').replace('-', '_')}": prediction for name, prediction in models.items()},
    )
    with (output_dir / "PN1C_COMPRESSION_RESULTS.json").open("w", encoding="utf-8") as handle:
        json.dump(json_safe(results), handle, indent=2, allow_nan=False)
    make_figure(scores, frontier_df, output_dir / "PN1C_COMPRESSION_FIGURE.png")

    print("PN1C provenance")
    print(f"  protocol_sha256: {protocol_hash}")
    print(f"  target_gap_sha256: {target_primary.gap_sha256}")
    print(f"  target slots: {target_primary.survivor_count:,}")
    print(f"  exact checks: {all_exact_checks_pass}")
    print(f"  primary pass: {primary_claim_pass}")
    print(f"  split robustness: {split_robustness_pass}")
    print(f"  rating: {rating}")
    print(scores.to_string(index=False))
    return results


if __name__ == "__main__":
    run_analysis()
