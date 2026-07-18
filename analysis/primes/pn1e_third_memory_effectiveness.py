"""PN1E/DEV/v1: practical effect and attribution of two-step ARA memory.

Prime 23 is development data. Prime 29 is deliberately untouched.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from pn1c_independent_validator import child_gap_cycle, reduced_residues


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN1E_THIRD_MEMORY_EFFECTIVENESS_PROTOCOL.md"
PN1D_MATRICES = HERE / "PN1D_MATRICES.npz"
PROTOCOL_SHA256 = "484B45190DCDC3823CDF6B2F644FCC87FCD925DA22B45321D2C334E56B8C77EB"
GAP_SHA256 = "F68A8E707D9836C03C8FE5A84AD3FD3CA397F1736562CC2279094B631585923C"
PARENT_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19)
CHILD_SLOTS = 36_495_360
CHILD_PERIOD = 223_092_870
ALPHA = 0.5
PRIMARY_BINS = 12
SENSITIVITY_BINS = (8, 12, 16)
CHUNK = 750_000


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
    values = np.asarray(values, dtype=np.float64)
    total = float(values.sum())
    if total <= 0:
        raise ValueError("Cannot normalize zero mass")
    return values / total


def relation_bins(left: np.ndarray | int, right: np.ndarray | int, bins: int) -> np.ndarray:
    left = np.asarray(left, dtype=np.float64)
    right = np.asarray(right, dtype=np.float64)
    coordinate = 2.0 * right / (left + right)
    return np.minimum((coordinate * bins / 2.0).astype(np.int64), bins - 1)


def relation_sequence(gaps: np.ndarray, bins: int) -> np.ndarray:
    output = np.empty(len(gaps), dtype=np.uint8)
    size = len(gaps)
    for start in range(0, size, CHUNK):
        stop = min(start + CHUNK, size)
        index = np.arange(start, stop, dtype=np.int64)
        output[start:stop] = relation_bins(
            np.take(gaps, index), np.take(gaps, (index + 1) % size), bins
        ).astype(np.uint8)
    return output


def sequence_counts(values: np.ndarray, bins: int) -> np.ndarray:
    counts = np.zeros((bins, bins, bins), dtype=np.int64)
    size = len(values)
    for start in range(0, size, CHUNK):
        stop = min(start + CHUNK, size)
        index = np.arange(start, stop, dtype=np.int64)
        a = np.take(values, index).astype(np.int64)
        b = np.take(values, (index + 1) % size).astype(np.int64)
        c = np.take(values, (index + 2) % size).astype(np.int64)
        code = a * bins * bins + b * bins + c
        counts += np.bincount(code, minlength=bins**3).reshape(bins, bins, bins)
    return counts


def fit_probabilities(train: np.ndarray, bins: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    marginal_counts = np.bincount(train, minlength=bins).astype(np.float64)
    pair_counts = np.zeros((bins, bins), dtype=np.float64)
    triple_counts = np.zeros((bins, bins, bins), dtype=np.float64)
    for start in range(0, len(train) - 2, CHUNK):
        stop = min(start + CHUNK, len(train) - 2)
        a = train[start:stop].astype(np.int64)
        b = train[start + 1 : stop + 1].astype(np.int64)
        c = train[start + 2 : stop + 2].astype(np.int64)
        pair_counts += np.bincount(
            b * bins + c, minlength=bins**2
        ).reshape(bins, bins)
        triple_counts += np.bincount(
            a * bins * bins + b * bins + c, minlength=bins**3
        ).reshape(bins, bins, bins)
    marginal = (marginal_counts + ALPHA) / (marginal_counts.sum() + ALPHA * bins)
    markov1 = (pair_counts + ALPHA) / (pair_counts.sum(axis=1, keepdims=True) + ALPHA * bins)
    markov2 = (triple_counts + ALPHA) / (
        triple_counts.sum(axis=2, keepdims=True) + ALPHA * bins
    )
    return marginal, markov1, markov2


def score_probabilities(
    test: np.ndarray,
    marginal: np.ndarray,
    markov1: np.ndarray,
    markov2: np.ndarray,
    bins: int,
) -> dict[str, dict[str, float]]:
    totals = {
        name: {"logloss": 0.0, "brier": 0.0, "top1": 0, "top3": 0}
        for name in ("ARA-IID", "ARA-Markov-1", "ARA-Markov-2")
    }
    observations = len(test) - 2
    top3_iid = np.argpartition(marginal, -3)[-3:]
    top1_iid = int(np.argmax(marginal))
    for start in range(2, len(test), CHUNK):
        stop = min(start + CHUNK, len(test))
        target = test[start:stop].astype(np.int64)
        previous = test[start - 1 : stop - 1].astype(np.int64)
        earlier = test[start - 2 : stop - 2].astype(np.int64)
        probability_sets = {
            "ARA-Markov-1": markov1[previous],
            "ARA-Markov-2": markov2[earlier, previous],
        }

        actual_iid = marginal[target]
        totals["ARA-IID"]["logloss"] += float(-np.log2(actual_iid).sum())
        totals["ARA-IID"]["brier"] += float(
            len(target) * np.sum(marginal**2) - 2.0 * actual_iid.sum() + len(target)
        )
        totals["ARA-IID"]["top1"] += int(np.sum(target == top1_iid))
        totals["ARA-IID"]["top3"] += int(np.isin(target, top3_iid).sum())

        for name, probabilities in probability_sets.items():
            actual = probabilities[np.arange(len(target)), target]
            totals[name]["logloss"] += float(-np.log2(actual).sum())
            totals[name]["brier"] += float(
                np.sum(probabilities**2) - 2.0 * actual.sum() + len(target)
            )
            prediction = np.argmax(probabilities, axis=1)
            top3 = np.argpartition(probabilities, -3, axis=1)[:, -3:]
            totals[name]["top1"] += int(np.sum(prediction == target))
            totals[name]["top3"] += int(np.sum(np.any(top3 == target[:, None], axis=1)))

    return {
        name: {
            "cross_entropy_bits_per_reading": values["logloss"] / observations,
            "perplexity": 2.0 ** (values["logloss"] / observations),
            "brier_score": values["brier"] / observations,
            "top1_accuracy": values["top1"] / observations,
            "top3_accuracy": values["top3"] / observations,
            "observations": observations,
        }
        for name, values in totals.items()
    }


def entropy(values: np.ndarray) -> float:
    probability = normalize(values.ravel())
    active = probability > 0
    return float(-np.sum(probability[active] * np.log2(probability[active])))


def conditional_entropy_scale(tensor: np.ndarray) -> dict[str, float]:
    probability = normalize(tensor)
    h_xyz = entropy(probability)
    h_xy = entropy(probability.sum(axis=2))
    h_yz = entropy(probability.sum(axis=0))
    h_y = entropy(probability.sum(axis=(0, 2)))
    one = h_yz - h_y
    two = h_xyz - h_xy
    gain = one - two
    return {
        "one_neighbor_entropy_bits": one,
        "two_neighbor_entropy_bits": two,
        "memory_gain_bits": gain,
        "one_neighbor_uncertainty_removed_fraction": gain / one,
        "one_neighbor_perplexity": 2.0**one,
        "two_neighbor_perplexity": 2.0**two,
        "perplexity_reduction_fraction": 1.0 - 2.0**two / 2.0**one,
    }


def context_attribution(tensor: np.ndarray) -> pd.DataFrame:
    p = normalize(tensor)
    p_ab = p.sum(axis=2)
    p_bc = p.sum(axis=0)
    p_b = p.sum(axis=(0, 2))
    rows: list[dict[str, object]] = []
    for a in range(p.shape[0]):
        for b in range(p.shape[1]):
            if p_ab[a, b] <= 0:
                continue
            conditional_two = p[a, b] / p_ab[a, b]
            conditional_one = p_bc[b] / p_b[b]
            active = conditional_two > 0
            contribution = float(
                p_ab[a, b]
                * np.sum(
                    conditional_two[active]
                    * np.log2(conditional_two[active] / conditional_one[active])
                )
            )
            dominant_two = int(np.argmax(conditional_two))
            dominant_one = int(np.argmax(conditional_one))
            rows.append(
                {
                    "first_context_bin": a,
                    "second_context_bin": b,
                    "first_context_center": (a + 0.5) * 2.0 / p.shape[0],
                    "second_context_center": (b + 0.5) * 2.0 / p.shape[1],
                    "context_probability": float(p_ab[a, b]),
                    "contribution_bits_per_reading": contribution,
                    "dominant_next_bin_markov2": dominant_two,
                    "dominant_next_center_markov2": (dominant_two + 0.5) * 2.0 / p.shape[2],
                    "dominant_next_bin_markov1": dominant_one,
                    "dominant_next_center_markov1": (dominant_one + 0.5) * 2.0 / p.shape[2],
                    "top_prediction_changes": dominant_two != dominant_one,
                }
            )
    frame = pd.DataFrame(rows).sort_values(
        "contribution_bits_per_reading", ascending=False
    ).reset_index(drop=True)
    frame.insert(0, "rank", np.arange(1, len(frame) + 1))
    return frame


def quadruple_attribution(gaps: np.ndarray, tensor: np.ndarray) -> pd.DataFrame:
    labels, counts = np.unique(gaps, return_counts=True)
    alphabet = len(labels)
    lookup = np.full(int(gaps.max()) + 1, 255, dtype=np.uint8)
    lookup[labels.astype(np.int64)] = np.arange(alphabet, dtype=np.uint8)
    inverse = lookup[gaps]
    if np.any(inverse == 255):
        raise AssertionError("Gap lookup failed")
    quad_counts = np.zeros(alphabet**4, dtype=np.int64)
    size = len(gaps)
    for start in range(0, size, CHUNK):
        stop = min(start + CHUNK, size)
        index = np.arange(start, stop, dtype=np.int64)
        i0 = np.take(inverse, index).astype(np.int64)
        i1 = np.take(inverse, (index + 1) % size).astype(np.int64)
        i2 = np.take(inverse, (index + 2) % size).astype(np.int64)
        i3 = np.take(inverse, (index + 3) % size).astype(np.int64)
        code = i0 * alphabet**3 + i1 * alphabet**2 + i2 * alphabet + i3
        quad_counts += np.bincount(code, minlength=alphabet**4)

    p = normalize(tensor)
    p_ab = p.sum(axis=2)
    p_bc = p.sum(axis=0)
    p_b = p.sum(axis=(0, 2))
    conditional_two = np.divide(
        p, p_ab[:, :, None], out=np.zeros_like(p), where=p_ab[:, :, None] > 0
    )
    conditional_one = np.divide(
        p_bc, p_b[:, None], out=np.zeros_like(p_bc), where=p_b[:, None] > 0
    )
    dominant_two = np.argmax(conditional_two, axis=2)
    dominant_one = np.argmax(conditional_one, axis=1)

    active_codes = np.flatnonzero(quad_counts)
    rows: list[dict[str, object]] = []
    for code in active_codes:
        remainder = int(code)
        i0, remainder = divmod(remainder, alphabet**3)
        i1, remainder = divmod(remainder, alphabet**2)
        i2, i3 = divmod(remainder, alphabet)
        g0, g1, g2, g3 = (int(labels[index]) for index in (i0, i1, i2, i3))
        x0 = int(relation_bins(g0, g1, PRIMARY_BINS))
        x1 = int(relation_bins(g1, g2, PRIMARY_BINS))
        x2 = int(relation_bins(g2, g3, PRIMARY_BINS))
        p_two = float(conditional_two[x0, x1, x2])
        p_one = float(conditional_one[x1, x2])
        local_bits = math.log2(p_two / p_one)
        probability = int(quad_counts[code]) / size
        rows.append(
            {
                "gap_0": g0,
                "gap_1": g1,
                "gap_2": g2,
                "gap_3": g3,
                "ara_0_bin": x0,
                "ara_1_bin": x1,
                "ara_2_bin": x2,
                "ara_0_center": (x0 + 0.5) * 2.0 / PRIMARY_BINS,
                "ara_1_center": (x1 + 0.5) * 2.0 / PRIMARY_BINS,
                "ara_2_center": (x2 + 0.5) * 2.0 / PRIMARY_BINS,
                "count": int(quad_counts[code]),
                "probability": probability,
                "local_information_bits": local_bits,
                "signed_contribution_bits_per_reading": probability * local_bits,
                "top_prediction_changes": int(dominant_two[x0, x1])
                != int(dominant_one[x1]),
            }
        )
    frame = pd.DataFrame(rows).sort_values(
        "signed_contribution_bits_per_reading", ascending=False
    ).reset_index(drop=True)
    frame.insert(0, "rank", np.arange(1, len(frame) + 1))
    return frame


def make_figure(
    scores: pd.DataFrame,
    entropy_table: pd.DataFrame,
    contexts: pd.DataFrame,
    path: Path,
) -> None:
    width, height = 1800, 1080
    image = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(image)

    def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
        name = "arialbd.ttf" if bold else "arial.ttf"
        candidate = Path("C:/Windows/Fonts") / name
        return ImageFont.truetype(str(candidate), size) if candidate.exists() else ImageFont.load_default()

    title, heading, body, small = font(38, True), font(24, True), font(18), font(15)
    ink, muted, grid = "#202731", "#5d6878", "#d9dee6"
    blue, gold, pale = "#3479a9", "#a06d13", "#dceaf3"
    draw.text((55, 28), "PN1E practical effectiveness of the informative third", fill=ink, font=title)
    draw.text((55, 78), "Prime-23 development data; scores are bits per next 12-bin ARA reading", fill=muted, font=body)

    mean = scores[(scores["bins"] == PRIMARY_BINS) & (scores["direction"] == "mean")]
    draw.text((60, 135), "Held-out next-reading cross-entropy", fill=ink, font=heading)
    x0, y0, x1, y1 = 85, 205, 560, 500
    maximum = float(mean["cross_entropy_bits_per_reading"].max()) * 1.08
    for tick in range(6):
        value = maximum * tick / 5
        y = int(y1 - value / maximum * (y1 - y0))
        draw.line((x0, y, x1, y), fill=grid, width=1)
        draw.text((x0 - 62, y - 8), f"{value:.2f}", fill=muted, font=small)
    bar_width = 105
    for index, (_, row) in enumerate(mean.iterrows()):
        bx = x0 + 35 + index * 145
        top = int(y1 - row["cross_entropy_bits_per_reading"] / maximum * (y1 - y0))
        color = gold if row["model"] == "ARA-Markov-2" else blue if row["model"] == "ARA-Markov-1" else pale
        draw.rectangle((bx, top, bx + bar_width, y1), fill=color, outline=ink)
        draw.text((bx + 7, top - 25), f"{row['cross_entropy_bits_per_reading']:.3f}", fill=ink, font=small)
        label = row["model"].replace("ARA-", "")
        draw.text((bx, y1 + 12), label, fill=ink, font=small)
    draw.text((85, 535), "Lower means a less surprising next ARA bin", fill=muted, font=body)

    draw.text((650, 135), "One-neighbour vs two-neighbour uncertainty", fill=ink, font=heading)
    plot_x0, plot_y0, plot_x1 = 685, 220, 1240
    max_entropy = float(entropy_table["one_neighbor_entropy_bits"].max()) * 1.08
    for row_index, (_, row) in enumerate(entropy_table.iterrows()):
        y = plot_y0 + row_index * 90
        full = int(row["one_neighbor_entropy_bits"] / max_entropy * (plot_x1 - plot_x0))
        reduced = int(row["two_neighbor_entropy_bits"] / max_entropy * (plot_x1 - plot_x0))
        draw.rectangle((plot_x0, y, plot_x0 + full, y + 26), fill=pale, outline=ink)
        draw.rectangle((plot_x0, y, plot_x0 + reduced, y + 26), fill=blue, outline=ink)
        draw.text((plot_x0, y - 25), str(row["model"]), fill=ink, font=body)
        draw.text((plot_x0 + full + 10, y + 2), f"-{row['memory_gain_bits']:.3f} bits", fill=gold, font=small)
    draw.text((685, 510), "Pale = one neighbour; blue = two neighbours", fill=muted, font=body)

    draw.text((60, 625), "Largest ARA-context contributions to the third-step gain", fill=ink, font=heading)
    top = contexts.head(10).iloc[::-1]
    bx0, by0, bx1 = 310, 695, 1660
    maximum_context = float(top["contribution_bits_per_reading"].max()) * 1.05
    for index, (_, row) in enumerate(top.iterrows()):
        y = by0 + index * 32
        length = int(row["contribution_bits_per_reading"] / maximum_context * (bx1 - bx0))
        draw.rectangle((bx0, y, bx0 + length, y + 20), fill=blue, outline=ink)
        label = f"({row['first_context_center']:.2f}, {row['second_context_center']:.2f})"
        draw.text((65, y), label, fill=ink, font=small)
        draw.text((bx0 + length + 8, y), f"{row['contribution_bits_per_reading']:.4f}", fill=ink, font=small)
    draw.text((60, 1032), "Context labels are the centres of the two preceding 0-2 ARA bins; bars sum toward the 0.474-bit total.", fill=muted, font=body)
    image.save(path, format="PNG")


def main() -> dict[str, object]:
    if file_hash(PROTOCOL) != PROTOCOL_SHA256:
        raise RuntimeError("PN1E protocol hash mismatch")
    _, parent = reduced_residues(PARENT_PRIMES)
    gaps = child_gap_cycle(parent)
    midpoint = len(gaps) // 2
    exact_checks: dict[str, bool] = {
        "protocol_hash_matches": file_hash(PROTOCOL) == PROTOCOL_SHA256,
        "gap_count_exact": len(gaps) == CHILD_SLOTS,
        "gap_period_exact": int(gaps.sum(dtype=np.int64)) == CHILD_PERIOD,
        "gap_hash_exact": array_hash(gaps) == GAP_SHA256,
        "gaps_positive_even": bool(np.all(gaps > 0) and np.all(gaps % 2 == 0)),
    }

    score_rows: list[dict[str, object]] = []
    for bins in SENSITIVITY_BINS:
        sequence = relation_sequence(gaps, bins)
        directions = (
            ("half1_to_half2", sequence[:midpoint], sequence[midpoint:]),
            ("half2_to_half1", sequence[midpoint:], sequence[:midpoint]),
        )
        direction_rows: list[dict[str, object]] = []
        for direction, train, test in directions:
            probabilities = fit_probabilities(train, bins)
            scored = score_probabilities(test, *probabilities, bins)
            for model, metrics in scored.items():
                row = {"bins": bins, "direction": direction, "model": model, **metrics}
                score_rows.append(row)
                direction_rows.append(row)
        for model in ("ARA-IID", "ARA-Markov-1", "ARA-Markov-2"):
            selected = [row for row in direction_rows if row["model"] == model]
            score_rows.append(
                {
                    "bins": bins,
                    "direction": "mean",
                    "model": model,
                    **{
                        key: float(np.mean([float(row[key]) for row in selected]))
                        for key in (
                            "cross_entropy_bits_per_reading",
                            "perplexity",
                            "brier_score",
                            "top1_accuracy",
                            "top3_accuracy",
                            "observations",
                        )
                    },
                }
            )
        print(f"B={bins} cross-fit complete")
    scores = pd.DataFrame(score_rows)
    scores.to_csv(HERE / "PN1E_EFFECTIVENESS_SCORES.csv", index=False)

    primary_mean = scores[(scores["bins"] == PRIMARY_BINS) & (scores["direction"] == "mean")]
    primary_m1 = primary_mean[primary_mean["model"] == "ARA-Markov-1"].iloc[0]
    primary_m2 = primary_mean[primary_mean["model"] == "ARA-Markov-2"].iloc[0]
    gain = float(primary_m1["cross_entropy_bits_per_reading"] - primary_m2["cross_entropy_bits_per_reading"])
    relative_gain = gain / float(primary_m1["cross_entropy_bits_per_reading"])
    perplexity_reduction = 1.0 - float(primary_m2["perplexity"] / primary_m1["perplexity"])
    direction_gain = []
    for direction in ("half1_to_half2", "half2_to_half1"):
        selected = scores[(scores["bins"] == PRIMARY_BINS) & (scores["direction"] == direction)]
        m1 = float(selected[selected["model"] == "ARA-Markov-1"]["cross_entropy_bits_per_reading"].iloc[0])
        m2 = float(selected[selected["model"] == "ARA-Markov-2"]["cross_entropy_bits_per_reading"].iloc[0])
        direction_gain.append(m1 - m2)
    if all(value > 0 for value in direction_gain) and gain >= 0.05 and relative_gain >= 0.02:
        classification = "STRONG PRACTICAL EFFECT"
    elif all(value > 0 for value in direction_gain) and (gain >= 0.01 or relative_gain >= 0.005):
        classification = "SUGGESTIVE PRACTICAL EFFECT"
    else:
        classification = "WEAK OR ABSENT"

    matrices = np.load(PN1D_MATRICES)
    tensor_models = {
        "Empirical p23": matrices["empirical_sequence_tensor"],
        "IID-gap overlap": matrices["iid_sequence_tensor"],
        "First-order gap Markov": matrices["markov_sequence_tensor"],
    }
    entropy_rows = [
        {"model": name, **conditional_entropy_scale(tensor)}
        for name, tensor in tensor_models.items()
    ]
    entropy_table = pd.DataFrame(entropy_rows)
    entropy_table.to_csv(HERE / "PN1E_ENTROPY_SCALE.csv", index=False)

    primary_sequence = relation_sequence(gaps, PRIMARY_BINS)
    empirical_counts = sequence_counts(primary_sequence, PRIMARY_BINS)
    empirical_probability = normalize(empirical_counts)
    exact_checks["empirical_tensor_matches_pn1d"] = bool(
        np.allclose(empirical_probability, matrices["empirical_sequence_tensor"], rtol=0.0, atol=1e-15)
    )
    contexts = context_attribution(empirical_probability)
    contexts.to_csv(HERE / "PN1E_CONTEXT_ATTRIBUTION.csv", index=False)
    empirical_memory = float(entropy_table.loc[entropy_table["model"] == "Empirical p23", "memory_gain_bits"].iloc[0])
    exact_checks["context_contributions_sum_to_cmi"] = math.isclose(
        float(contexts["contribution_bits_per_reading"].sum()), empirical_memory, rel_tol=0.0, abs_tol=1e-12
    )

    quadruples = quadruple_attribution(gaps, empirical_probability)
    quadruples.to_csv(HERE / "PN1E_GAP_QUADRUPLE_ATTRIBUTION.csv", index=False)
    quadruples.head(30).to_csv(HERE / "PN1E_TOP30_GAP_QUADRUPLES.csv", index=False)
    quadruple_sum = float(quadruples["signed_contribution_bits_per_reading"].sum())
    exact_checks["quadruple_contributions_sum_to_cmi"] = math.isclose(
        quadruple_sum, empirical_memory, rel_tol=0.0, abs_tol=1e-12
    )

    context_shares = {
        f"top_{count}_share": float(contexts.head(count)["contribution_bits_per_reading"].sum() / empirical_memory)
        for count in (5, 10, 20)
    }
    positive_quadruple_mass = float(
        quadruples.loc[quadruples["signed_contribution_bits_per_reading"] > 0, "signed_contribution_bits_per_reading"].sum()
    )
    negative_quadruple_mass = float(
        quadruples.loc[quadruples["signed_contribution_bits_per_reading"] < 0, "signed_contribution_bits_per_reading"].sum()
    )

    all_checks = all(exact_checks.values())
    results = {
        "protocol": "PN1E/DEV/v1",
        "protocol_sha256": PROTOCOL_SHA256,
        "data": {
            "prime": 23,
            "gap_count": len(gaps),
            "gap_period": int(gaps.sum(dtype=np.int64)),
            "gap_sha256": array_hash(gaps),
            "prime29_opened": False,
        },
        "primary_effectiveness": {
            "classification": classification,
            "scale": "bits per next 12-bin ARA reading",
            "markov1_cross_entropy_bits": float(primary_m1["cross_entropy_bits_per_reading"]),
            "markov2_cross_entropy_bits": float(primary_m2["cross_entropy_bits_per_reading"]),
            "gain_bits_per_reading": gain,
            "relative_logloss_reduction": relative_gain,
            "perplexity_reduction": perplexity_reduction,
            "markov1_top1_accuracy": float(primary_m1["top1_accuracy"]),
            "markov2_top1_accuracy": float(primary_m2["top1_accuracy"]),
            "markov1_top3_accuracy": float(primary_m1["top3_accuracy"]),
            "markov2_top3_accuracy": float(primary_m2["top3_accuracy"]),
            "markov1_brier": float(primary_m1["brier_score"]),
            "markov2_brier": float(primary_m2["brier_score"]),
            "direction_gains_bits": direction_gain,
        },
        "control_scale": {
            row["model"]: {
                key: float(row[key])
                for key in (
                    "one_neighbor_entropy_bits",
                    "two_neighbor_entropy_bits",
                    "memory_gain_bits",
                    "one_neighbor_uncertainty_removed_fraction",
                    "perplexity_reduction_fraction",
                )
            }
            for row in entropy_rows
        },
        "attribution": {
            **context_shares,
            "active_ara_contexts": len(contexts),
            "active_gap_quadruples": len(quadruples),
            "positive_quadruple_contribution_bits": positive_quadruple_mass,
            "negative_quadruple_contribution_bits": negative_quadruple_mass,
            "net_quadruple_contribution_bits": quadruple_sum,
            "top_context": contexts.iloc[0].to_dict(),
            "top_gap_quadruple": quadruples.iloc[0].to_dict(),
        },
        "exact_checks": exact_checks,
        "all_exact_checks_pass": all_checks,
        "evidence_boundary": (
            "Development evidence for predictive value and attribution on p23. "
            "Not evidence of exactly three waves, a physical third wave, or transfer to p29."
        ),
    }
    with (HERE / "PN1E_RESULTS.json").open("w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2, allow_nan=False)
    pd.DataFrame([{"check": key, "passes": value} for key, value in exact_checks.items()]).to_csv(
        HERE / "PN1E_EXACT_CHECKS.csv", index=False
    )
    make_figure(scores, entropy_table, contexts, HERE / "PN1E_EFFECTIVENESS_DIAGNOSTIC.png")
    print(json.dumps({
        "primary_effectiveness": results["primary_effectiveness"],
        "control_scale": results["control_scale"],
        "attribution": results["attribution"],
        "all_exact_checks_pass": all_checks,
    }, indent=2, allow_nan=False))
    if not all_checks:
        raise SystemExit(1)
    return results


if __name__ == "__main__":
    main()
