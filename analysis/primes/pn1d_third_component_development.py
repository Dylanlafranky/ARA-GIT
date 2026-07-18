"""PN1D development study: third plane mode versus third-step memory.

Prime 23 is already-open development data.  This script does not construct the
prime-29 wheel.  See PN1D_THIRD_COMPONENT_DEVELOPMENT_PROTOCOL.md.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from pn1c_independent_validator import child_gap_cycle, reduced_residues


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN1D_THIRD_COMPONENT_DEVELOPMENT_PROTOCOL.md"
PROTOCOL_SHA256 = "9D6F2EFC3774B84F04AFBCCEBD0782F3B02F62A53A783712408112F5642A60DF"
PN1C_ARCHIVE = HERE / "PN1C_TARGET_AND_PREDICTIONS.npz"
EXPECTED_GAP_HASH = "F68A8E707D9836C03C8FE5A84AD3FD3CA397F1736562CC2279094B631585923C"
PARENT_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19)
CHILD_PERIOD = 223_092_870
CHILD_SLOTS = 36_495_360
SEED = 20_260_717
NMF_RANKS = tuple(range(1, 7))
NMF_RESTARTS = 12
NMF_ITERATIONS = 2_000
PLANE_BINS = 24
SEQUENCE_BINS = 12
CHUNK = 1_000_000


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def array_hash(values: np.ndarray) -> str:
    digest = hashlib.sha256()
    for start in range(0, len(values), CHUNK):
        digest.update(values[start : start + CHUNK].tobytes(order="C"))
    return digest.hexdigest().upper()


def normalize(values: np.ndarray) -> np.ndarray:
    result = np.asarray(values, dtype=np.float64)
    if np.any(result < 0) or not np.all(np.isfinite(result)):
        raise AssertionError("Invalid probability values")
    total = float(result.sum())
    if total <= 0:
        raise AssertionError("Zero probability mass")
    return result / total


def jsd_bits(first: np.ndarray, second: np.ndarray) -> float:
    first = normalize(first.ravel())
    second = normalize(second.ravel())
    midpoint = 0.5 * (first + second)

    def kl(values: np.ndarray) -> float:
        active = values > 0
        return float(np.sum(values[active] * np.log2(values[active] / midpoint[active])))

    return 0.5 * kl(first) + 0.5 * kl(second)


def relation_bin(left: np.ndarray | int, right: np.ndarray | int, bins: int) -> np.ndarray:
    left_values = np.asarray(left, dtype=np.float64)
    right_values = np.asarray(right, dtype=np.float64)
    coordinate = 2.0 * right_values / (left_values + right_values)
    return np.minimum((coordinate * bins / 2.0).astype(np.int64), bins - 1)


def relation_sequence(gaps: np.ndarray, bins: int) -> np.ndarray:
    output = np.empty(len(gaps), dtype=np.uint8)
    size = len(gaps)
    for start in range(0, size, CHUNK):
        stop = min(start + CHUNK, size)
        index = np.arange(start, stop, dtype=np.int64)
        output[start:stop] = relation_bin(
            np.take(gaps, index), np.take(gaps, (index + 1) % size), bins
        ).astype(np.uint8)
    return output


def sequence_tensor(values: np.ndarray, bins: int, start: int, stop: int) -> np.ndarray:
    counts = np.zeros((bins, bins, bins), dtype=np.int64)
    size = len(values)
    for chunk_start in range(start, stop, CHUNK):
        chunk_stop = min(chunk_start + CHUNK, stop)
        index = np.arange(chunk_start, chunk_stop, dtype=np.int64)
        first = np.take(values, index % size).astype(np.int64)
        second = np.take(values, (index + 1) % size).astype(np.int64)
        third = np.take(values, (index + 2) % size).astype(np.int64)
        code = first * bins * bins + second * bins + third
        counts += np.bincount(code, minlength=bins**3).reshape(bins, bins, bins)
    return counts


def conditional_mutual_information(probability: np.ndarray) -> float:
    probability = normalize(probability)
    ab = probability.sum(axis=2)
    bc = probability.sum(axis=0)
    b = probability.sum(axis=(0, 2))
    expected = np.zeros_like(probability)
    for middle in range(probability.shape[1]):
        if b[middle] > 0:
            expected[:, middle, :] = (
                ab[:, middle, None] * bc[middle, None, :] / b[middle]
            )
    active = probability > 0
    return float(
        np.sum(probability[active] * np.log2(probability[active] / expected[active]))
    )


def gap_model_tensor(
    labels: np.ndarray,
    marginal: np.ndarray,
    transition: np.ndarray | None,
    bins: int,
) -> np.ndarray:
    tensor = np.zeros((bins, bins, bins), dtype=np.float64)
    for ia, a in enumerate(labels):
        for ib, b in enumerate(labels):
            pab = marginal[ia] * (marginal[ib] if transition is None else transition[ia, ib])
            if pab == 0:
                continue
            x0 = int(relation_bin(int(a), int(b), bins))
            for ic, c in enumerate(labels):
                pabc = pab * (marginal[ic] if transition is None else transition[ib, ic])
                if pabc == 0:
                    continue
                x1 = int(relation_bin(int(b), int(c), bins))
                for id_value, d in enumerate(labels):
                    probability = pabc * (
                        marginal[id_value]
                        if transition is None
                        else transition[ic, id_value]
                    )
                    if probability == 0:
                        continue
                    x2 = int(relation_bin(int(c), int(d), bins))
                    tensor[x0, x1, x2] += probability
    return normalize(tensor)


def nmf_fit(
    matrix: np.ndarray, rank: int, seed: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    matrix = normalize(matrix)
    best: tuple[np.ndarray, np.ndarray, np.ndarray, float] | None = None
    epsilon = 1e-15
    for restart in range(NMF_RESTARTS):
        rng = np.random.default_rng(seed + 10_007 * rank + restart)
        scale = math.sqrt(float(matrix.mean()) / rank)
        left = rng.random((matrix.shape[0], rank)) * scale + 1e-8
        right = rng.random((rank, matrix.shape[1])) * scale + 1e-8
        for _ in range(NMF_ITERATIONS):
            right *= (left.T @ matrix) / (left.T @ left @ right + epsilon)
            left *= (matrix @ right.T) / (left @ right @ right.T + epsilon)
            column_scale = np.maximum(left.sum(axis=0), epsilon)
            left /= column_scale
            right *= column_scale[:, None]
        reconstruction = normalize(left @ right)
        error = float(np.linalg.norm(matrix - reconstruction))
        if best is None or error < best[3]:
            best = (left.copy(), right.copy(), reconstruction, error)
    if best is None:
        raise AssertionError("NMF failed")
    return best


def component_matrices(left: np.ndarray, right: np.ndarray) -> list[np.ndarray]:
    return [normalize(np.outer(left[:, index], right[index])) for index in range(left.shape[1])]


def cosine(first: np.ndarray, second: np.ndarray) -> float:
    a = first.ravel()
    b = second.ravel()
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.dot(a, b) / denominator) if denominator else 0.0


def best_component_match(
    first: list[np.ndarray], second: list[np.ndarray]
) -> tuple[list[int], list[float]]:
    similarities = np.array(
        [[cosine(a, b) for b in second] for a in first], dtype=np.float64
    )
    best_permutation: tuple[int, ...] | None = None
    best_values: list[float] = []
    best_mean = -1.0
    for permutation in itertools.permutations(range(len(second))):
        values = [float(similarities[index, permutation[index]]) for index in range(len(first))]
        mean_value = float(np.mean(values))
        if mean_value > best_mean:
            best_mean = mean_value
            best_permutation = permutation
            best_values = values
    if best_permutation is None:
        raise AssertionError("Component matching failed")
    return list(best_permutation), best_values


def span_histogram(gaps: np.ndarray) -> np.ndarray:
    histogram = np.zeros(512, dtype=np.int64)
    size = len(gaps)
    for start in range(0, size, CHUNK):
        stop = min(start + CHUNK, size)
        index = np.arange(start, stop, dtype=np.int64)
        spans = (
            np.take(gaps, index).astype(np.int64)
            + np.take(gaps, (index + 1) % size).astype(np.int64)
            + np.take(gaps, (index + 2) % size).astype(np.int64)
        )
        if int(spans.max()) >= len(histogram):
            raise AssertionError("Span histogram range too small")
        histogram += np.bincount(spans, minlength=len(histogram))
    return histogram


def scale_stratum_counts(
    gaps: np.ndarray, boundaries: tuple[int, int]
) -> tuple[np.ndarray, np.ndarray]:
    counts = np.zeros((3, PLANE_BINS, PLANE_BINS), dtype=np.int64)
    half_counts = np.zeros((2, 3, PLANE_BINS, PLANE_BINS), dtype=np.int64)
    size = len(gaps)
    half = size // 2
    for start in range(0, size, CHUNK):
        stop = min(start + CHUNK, size)
        index = np.arange(start, stop, dtype=np.int64)
        first_gap = np.take(gaps, index).astype(np.int64)
        second_gap = np.take(gaps, (index + 1) % size).astype(np.int64)
        third_gap = np.take(gaps, (index + 2) % size).astype(np.int64)
        span = first_gap + second_gap + third_gap
        stratum = np.digitize(span, boundaries, right=True)
        row = relation_bin(first_gap, second_gap, PLANE_BINS)
        column = relation_bin(second_gap, third_gap, PLANE_BINS)
        half_index = (index >= half).astype(np.int64)
        for level in range(3):
            mask = stratum == level
            codes = row[mask] * PLANE_BINS + column[mask]
            counts[level] += np.bincount(
                codes, minlength=PLANE_BINS**2
            ).reshape(PLANE_BINS, PLANE_BINS)
            for child_half in range(2):
                local = mask & (half_index == child_half)
                local_codes = row[local] * PLANE_BINS + column[local]
                half_counts[child_half, level] += np.bincount(
                    local_codes, minlength=PLANE_BINS**2
                ).reshape(PLANE_BINS, PLANE_BINS)
    return counts, half_counts


def make_figure(
    nmf_table: pd.DataFrame,
    singular_values: np.ndarray,
    rank3_components: list[np.ndarray],
    scale_matrices: list[np.ndarray],
    scale_match: list[int],
    scale_cosines: list[float],
    path: Path,
) -> None:
    width, height = 1900, 1180
    image = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(image)

    def get_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
        name = "arialbd.ttf" if bold else "arial.ttf"
        candidate = Path("C:/Windows/Fonts") / name
        return ImageFont.truetype(str(candidate), size=size) if candidate.exists() else ImageFont.load_default()

    title_font, panel_font = get_font(38, True), get_font(24, True)
    body_font, small_font = get_font(19), get_font(16)
    ink, muted, grid = "#202731", "#5d6878", "#d9dee6"
    blue, gold = "#3479a9", "#a06d13"
    draw.text((55, 30), "PN1D third-component development diagnostics", fill=ink, font=title_font)
    draw.text(
        (55, 82),
        "Prime-23 development data; a stable third matrix mode and irreducible third-step memory are separate questions",
        fill=muted,
        font=body_font,
    )

    # Cross-fitted NMF frontier.
    draw.text((70, 135), "Cross-fitted non-negative plane modes", fill=ink, font=panel_font)
    plot = (90, 190, 850, 490)
    max_jsd = float(nmf_table["mean_heldout_jsd_bits"].max()) * 1.08
    for tick in range(6):
        value = max_jsd * tick / 5
        y = int(plot[3] - value / max_jsd * (plot[3] - plot[1]))
        draw.line((plot[0], y, plot[2], y), fill=grid, width=1)
        draw.text((plot[0] - 58, y - 8), f"{value:.3f}", fill=muted, font=small_font)
    draw.line((plot[0], plot[1], plot[0], plot[3]), fill=ink, width=2)
    draw.line((plot[0], plot[3], plot[2], plot[3]), fill=ink, width=2)
    points = []
    for _, row in nmf_table.iterrows():
        x = int(plot[0] + (row["rank"] - 1) / 5 * (plot[2] - plot[0]))
        y = int(plot[3] - row["mean_heldout_jsd_bits"] / max_jsd * (plot[3] - plot[1]))
        points.append((x, y))
        draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill=blue, outline=ink)
        draw.text((x - 4, plot[3] + 12), str(int(row["rank"])), fill=muted, font=small_font)
    draw.line(points, fill=blue, width=4)
    draw.text((360, 515), "NMF rank K", fill=muted, font=body_font)
    draw.text((100, 550), "Held-out JSD; lower is better", fill=muted, font=small_font)

    # Singular value spectrum.
    draw.text((1010, 135), "Linear singular-value spectrum", fill=ink, font=panel_font)
    spectrum_plot = (1030, 190, 1780, 490)
    values = singular_values[:10] / singular_values[0]
    for index, value in enumerate(values):
        x0 = spectrum_plot[0] + index * 70
        height_value = int(value * (spectrum_plot[3] - spectrum_plot[1]))
        draw.rectangle(
            (x0, spectrum_plot[3] - height_value, x0 + 42, spectrum_plot[3]),
            fill=gold if index == 2 else blue,
            outline=ink,
        )
        draw.text((x0 + 13, spectrum_plot[3] + 12), str(index + 1), fill=muted, font=small_font)
    draw.line((spectrum_plot[0], spectrum_plot[3], spectrum_plot[2], spectrum_plot[3]), fill=ink, width=2)
    draw.text((1240, 515), "mode number", fill=muted, font=body_font)
    draw.text((1040, 550), "Singular value relative to mode 1; mode 3 highlighted", fill=muted, font=small_font)

    # Heatmaps: components and their best scale-stratum matches.
    draw.text((70, 615), "Rank-3 components and closest three-gap scale strata", fill=ink, font=panel_font)
    component_max = max(float(matrix.max()) for matrix in rank3_components + scale_matrices)

    def color(value: float) -> tuple[int, int, int]:
        fraction = min(max(value / component_max, 0.0), 1.0) ** 0.42
        low = np.array([247, 249, 252], dtype=np.float64)
        high = np.array([36, 112, 158], dtype=np.float64)
        return tuple(np.rint(low + fraction * (high - low)).astype(int))

    cell = 13
    for index, component in enumerate(rank3_components):
        stratum_index = scale_match[index]
        matrices = (("NMF component", component), (f"scale stratum {stratum_index + 1}", scale_matrices[stratum_index]))
        base_x = 75 + index * 610
        for pair_index, (label, matrix) in enumerate(matrices):
            x0 = base_x + pair_index * 285
            y0 = 700
            draw.text((x0, 660), label, fill=ink, font=body_font)
            for row in range(24):
                for column in range(24):
                    x = x0 + column * cell
                    y = y0 + (23 - row) * cell
                    draw.rectangle((x, y, x + cell - 1, y + cell - 1), fill=color(float(matrix[row, column])))
            draw.rectangle((x0 - 1, y0 - 1, x0 + 24 * cell, y0 + 24 * cell), outline="#667386", width=2)
        draw.text(
            (base_x, 1035),
            f"component {index + 1} ↔ stratum {stratum_index + 1}: cosine {scale_cosines[index]:.3f}",
            fill=muted,
            font=small_font,
        )
    draw.text(
        (70, 1100),
        "Component matching is descriptive: weak scale-stratum cosine alignment means the three modes do not reduce to three simple span bands.",
        fill=muted,
        font=body_font,
    )
    image.save(path, format="PNG")


def main() -> dict[str, object]:
    if file_hash(PROTOCOL) != PROTOCOL_SHA256:
        raise RuntimeError("PN1D protocol hash mismatch")

    _, parent_residues = reduced_residues(PARENT_PRIMES)
    gaps = child_gap_cycle(parent_residues)
    gap_sha256 = array_hash(gaps)
    midpoint = len(gaps) // 2
    exact_checks: dict[str, bool] = {
        "protocol_hash_matches": file_hash(PROTOCOL) == PROTOCOL_SHA256,
        "child_gap_count_exact": len(gaps) == CHILD_SLOTS,
        "child_gap_sum_exact": int(gaps.sum(dtype=np.int64)) == CHILD_PERIOD,
        "child_gap_hash_matches_pn1c": gap_sha256 == EXPECTED_GAP_HASH,
        "child_gaps_positive_even": bool(np.all(gaps > 0) and np.all(gaps % 2 == 0)),
    }

    with np.load(PN1C_ARCHIVE) as archive:
        plane_counts = archive["target_counts"].copy()
        plane_halves = archive["target_half_counts"].copy()
    plane_probability = normalize(plane_counts)
    half_probabilities = [normalize(plane_halves[index]) for index in range(2)]

    nmf_rows: list[dict[str, object]] = []
    fitted: dict[tuple[int, int], tuple[np.ndarray, np.ndarray, np.ndarray, float]] = {}
    for rank in NMF_RANKS:
        for half_index in range(2):
            fitted[(rank, half_index)] = nmf_fit(
                half_probabilities[half_index], rank, SEED + 1_000_000 * half_index
            )
        first_components = component_matrices(fitted[(rank, 0)][0], fitted[(rank, 0)][1])
        second_components = component_matrices(fitted[(rank, 1)][0], fitted[(rank, 1)][1])
        _, matched_cosines = best_component_match(first_components, second_components)
        forward_jsd = jsd_bits(half_probabilities[1], fitted[(rank, 0)][2])
        reverse_jsd = jsd_bits(half_probabilities[0], fitted[(rank, 1)][2])
        nmf_rows.append(
            {
                "rank": rank,
                "half1_fit_to_half2_jsd_bits": forward_jsd,
                "half2_fit_to_half1_jsd_bits": reverse_jsd,
                "mean_heldout_jsd_bits": 0.5 * (forward_jsd + reverse_jsd),
                "mean_component_cosine": float(np.mean(matched_cosines)),
                "min_component_cosine": float(np.min(matched_cosines)),
                "half1_training_frobenius": fitted[(rank, 0)][3],
                "half2_training_frobenius": fitted[(rank, 1)][3],
            }
        )
        print(f"NMF rank {rank} complete", flush=True)
    nmf_table = pd.DataFrame(nmf_rows)
    rank_values = nmf_table.set_index("rank")
    gain_12 = float(rank_values.loc[1, "mean_heldout_jsd_bits"] - rank_values.loc[2, "mean_heldout_jsd_bits"])
    gain_23 = float(rank_values.loc[2, "mean_heldout_jsd_bits"] - rank_values.loc[3, "mean_heldout_jsd_bits"])
    gain_ratio = gain_23 / gain_12 if gain_12 > 0 else float("nan")
    rank3_both_improve = bool(
        rank_values.loc[3, "half1_fit_to_half2_jsd_bits"] < rank_values.loc[2, "half1_fit_to_half2_jsd_bits"]
        and rank_values.loc[3, "half2_fit_to_half1_jsd_bits"] < rank_values.loc[2, "half2_fit_to_half1_jsd_bits"]
    )
    rank3_min_cosine = float(rank_values.loc[3, "min_component_cosine"])
    if rank3_both_improve and gain_ratio >= 0.25 and rank3_min_cosine >= 0.90:
        third_mode_classification = "STRONG DEVELOPMENT SIGN"
    elif rank3_both_improve and gain_ratio >= 0.10 and rank3_min_cosine >= 0.80:
        third_mode_classification = "SUGGESTIVE DEVELOPMENT SIGN"
    else:
        third_mode_classification = "WEAK OR ABSENT BY FIXED DEVELOPMENT RULE"

    singular_values = np.linalg.svd(plane_probability, compute_uv=False)
    singular_energy = singular_values**2 / np.sum(singular_values**2)

    x12 = relation_sequence(gaps, SEQUENCE_BINS)
    empirical_tensor_counts = sequence_tensor(x12, SEQUENCE_BINS, 0, len(x12))
    half_tensor_counts = np.stack(
        (
            sequence_tensor(x12, SEQUENCE_BINS, 0, midpoint),
            sequence_tensor(x12, SEQUENCE_BINS, midpoint, len(x12)),
        )
    )
    labels, inverse, label_counts = np.unique(gaps, return_inverse=True, return_counts=True)
    marginal = label_counts.astype(np.float64) / len(gaps)
    following = np.roll(inverse, -1)
    transition_counts = np.bincount(
        inverse.astype(np.int64) * len(labels) + following,
        minlength=len(labels) ** 2,
    ).reshape(len(labels), len(labels))
    transition = transition_counts / transition_counts.sum(axis=1, keepdims=True)
    iid_tensor = gap_model_tensor(labels, marginal, None, SEQUENCE_BINS)
    markov_tensor = gap_model_tensor(labels, marginal, transition, SEQUENCE_BINS)
    empirical_probability = normalize(empirical_tensor_counts)
    sequence_rows = [
        {
            "model": "Empirical ordered child",
            "conditional_mutual_information_bits": conditional_mutual_information(empirical_probability),
            "jsd_from_empirical_bits": 0.0,
        },
        {
            "model": "IID gaps, exact overlap projection",
            "conditional_mutual_information_bits": conditional_mutual_information(iid_tensor),
            "jsd_from_empirical_bits": jsd_bits(empirical_probability, iid_tensor),
        },
        {
            "model": "First-order gap Markov projection",
            "conditional_mutual_information_bits": conditional_mutual_information(markov_tensor),
            "jsd_from_empirical_bits": jsd_bits(empirical_probability, markov_tensor),
        },
        {
            "model": "Empirical child half 1",
            "conditional_mutual_information_bits": conditional_mutual_information(half_tensor_counts[0]),
            "jsd_from_empirical_bits": jsd_bits(empirical_probability, half_tensor_counts[0]),
        },
        {
            "model": "Empirical child half 2",
            "conditional_mutual_information_bits": conditional_mutual_information(half_tensor_counts[1]),
            "jsd_from_empirical_bits": jsd_bits(empirical_probability, half_tensor_counts[1]),
        },
    ]
    sequence_table = pd.DataFrame(sequence_rows)

    histogram = span_histogram(gaps)
    cumulative = np.cumsum(histogram)
    first_boundary = int(np.searchsorted(cumulative, len(gaps) / 3, side="left"))
    second_boundary = int(np.searchsorted(cumulative, 2 * len(gaps) / 3, side="left"))
    boundaries = (first_boundary, second_boundary)
    stratum_counts, stratum_halves = scale_stratum_counts(gaps, boundaries)
    exact_checks["scale_strata_reconstruct_target"] = bool(
        np.array_equal(stratum_counts.sum(axis=0), plane_counts)
    )
    exact_checks["scale_half_strata_reconstruct_halves"] = bool(
        np.array_equal(stratum_halves.sum(axis=1), plane_halves)
    )
    scale_matrices = [normalize(stratum_counts[index]) for index in range(3)]
    scale_rows: list[dict[str, object]] = []
    for level in range(3):
        scale_rows.append(
            {
                "record": f"stratum_{level + 1}",
                "stratum": level + 1,
                "lower_exclusive": None if level == 0 else boundaries[level - 1],
                "upper_inclusive": boundaries[level] if level < 2 else None,
                "count": int(stratum_counts[level].sum()),
                "weight": float(stratum_counts[level].sum() / len(gaps)),
                "half_to_half_jsd_bits": jsd_bits(
                    stratum_halves[0, level], stratum_halves[1, level]
                ),
            }
        )
    for first, second in ((0, 1), (0, 2), (1, 2)):
        scale_rows.append(
            {
                "record": f"pair_{first + 1}_{second + 1}",
                "stratum": None,
                "lower_exclusive": None,
                "upper_inclusive": None,
                "count": None,
                "weight": None,
                "half_to_half_jsd_bits": None,
                "pairwise_stratum_jsd_bits": jsd_bits(
                    scale_matrices[first], scale_matrices[second]
                ),
            }
        )
    scale_table = pd.DataFrame(scale_rows)

    rank3_first = component_matrices(fitted[(3, 0)][0], fitted[(3, 0)][1])
    rank3_second = component_matrices(fitted[(3, 1)][0], fitted[(3, 1)][1])
    second_permutation, _ = best_component_match(rank3_first, rank3_second)
    rank3_average = [
        normalize(rank3_first[index] + rank3_second[second_permutation[index]])
        for index in range(3)
    ]
    scale_match, scale_cosines = best_component_match(rank3_average, scale_matrices)

    exact_checks["all_saved_probabilities_valid"] = all(
        np.all(np.isfinite(matrix))
        and np.all(matrix >= 0)
        and abs(float(matrix.sum()) - 1.0) <= 1e-12
        for matrix in [
            plane_probability,
            empirical_probability,
            iid_tensor,
            markov_tensor,
            *scale_matrices,
            *rank3_average,
        ]
    )
    all_exact_checks_pass = all(exact_checks.values())

    empirical_cmi = float(sequence_table.loc[sequence_table["model"] == "Empirical ordered child", "conditional_mutual_information_bits"].iloc[0])
    iid_cmi = float(sequence_table.loc[sequence_table["model"] == "IID gaps, exact overlap projection", "conditional_mutual_information_bits"].iloc[0])
    markov_cmi = float(sequence_table.loc[sequence_table["model"] == "First-order gap Markov projection", "conditional_mutual_information_bits"].iloc[0])

    results: dict[str, object] = {
        "development_id": "PN1D/DEV/v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "DEVELOPMENT / EXPLORATORY — NOT CONFIRMATION",
        "protocol_sha256": file_hash(PROTOCOL),
        "prime29_opened": False,
        "target": {
            "child_gap_count": len(gaps),
            "child_gap_sum": int(gaps.sum(dtype=np.int64)),
            "child_gap_sha256": gap_sha256,
            "gap_alphabet_size": int(len(labels)),
        },
        "plane_mode": {
            "classification": third_mode_classification,
            "rank1_to_rank2_gain_bits": gain_12,
            "rank2_to_rank3_gain_bits": gain_23,
            "rank3_gain_ratio": gain_ratio,
            "rank3_improves_both_directions": rank3_both_improve,
            "rank3_min_component_cosine": rank3_min_cosine,
            "rank3_mean_component_cosine": float(rank_values.loc[3, "mean_component_cosine"]),
            "singular_values": singular_values.tolist(),
            "singular_energy_fractions": singular_energy.tolist(),
        },
        "third_step": {
            "empirical_cmi_bits": empirical_cmi,
            "iid_overlap_cmi_bits": iid_cmi,
            "markov_overlap_cmi_bits": markov_cmi,
            "empirical_excess_over_iid_bits": empirical_cmi - iid_cmi,
            "empirical_excess_over_markov_bits": empirical_cmi - markov_cmi,
            "empirical_jsd_from_iid_bits": float(sequence_table.loc[sequence_table["model"] == "IID gaps, exact overlap projection", "jsd_from_empirical_bits"].iloc[0]),
            "empirical_jsd_from_markov_bits": float(sequence_table.loc[sequence_table["model"] == "First-order gap Markov projection", "jsd_from_empirical_bits"].iloc[0]),
        },
        "scale_strata": {
            "span_boundaries_upper_inclusive": list(boundaries),
            "rank3_to_scale_assignment": [value + 1 for value in scale_match],
            "rank3_to_scale_cosines": scale_cosines,
            "mean_rank3_to_scale_cosine": float(np.mean(scale_cosines)),
            "min_rank3_to_scale_cosine": float(np.min(scale_cosines)),
        },
        "exact_checks": exact_checks,
        "all_exact_checks_pass": all_exact_checks_pass,
        "evidence_ceiling": (
            "One already-open finite deterministic arithmetic object. Modes and conditional "
            "dependencies are mathematical appearances, not proof of a third physical wave."
        ),
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
        },
    }

    nmf_table.to_csv(HERE / "PN1D_NMF_CROSSFIT.csv", index=False)
    sequence_table.to_csv(HERE / "PN1D_THIRD_STEP_MODELS.csv", index=False)
    scale_table.to_csv(HERE / "PN1D_SCALE_STRATA.csv", index=False)
    pd.DataFrame(
        [{"check": key, "passes": bool(value)} for key, value in exact_checks.items()]
    ).to_csv(HERE / "PN1D_EXACT_CHECKS.csv", index=False)
    np.savez_compressed(
        HERE / "PN1D_MATRICES.npz",
        empirical_sequence_tensor=empirical_probability,
        iid_sequence_tensor=iid_tensor,
        markov_sequence_tensor=markov_tensor,
        scale_strata=np.stack(scale_matrices),
        rank3_components=np.stack(rank3_average),
        singular_values=singular_values,
        singular_energy=singular_energy,
    )
    with (HERE / "PN1D_RESULTS.json").open("w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2, allow_nan=False)
    make_figure(
        nmf_table,
        singular_values,
        rank3_average,
        scale_matrices,
        scale_match,
        scale_cosines,
        HERE / "PN1D_THIRD_COMPONENT_DIAGNOSTIC.png",
    )

    print(json.dumps({
        "plane_mode": results["plane_mode"],
        "third_step": results["third_step"],
        "scale_strata": results["scale_strata"],
        "all_exact_checks_pass": all_exact_checks_pass,
    }, indent=2))
    if not all_exact_checks_pass:
        raise SystemExit(1)
    return results


if __name__ == "__main__":
    main()
