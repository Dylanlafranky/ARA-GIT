"""Post-hoc PN10B geometry disclosure.

This script does not alter or extend the registered PN10B prediction test.
It exposes the descriptive ARA geometry that the registered verdict compressed:

* the nine paid-gate child A/B readings at prime and survivor-composite nodes;
* event-centred lead/at/lag traces around prime nodes;
* ARA landmark occupancy, ridge crossings, and individual examples; and
* the PN10 parent factor-survival coordinate around the same events.

All results are explicitly post-hoc and descriptive.  They must not be read as
fresh predictive confirmation.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from pn10b_child_phase_prime_ranking import base_primes, segmented_least_prime_factor


ROOT = Path(__file__).resolve().parent
LOW = 4_000_000_000
HIGH = 4_001_000_000
K = 9
WINDOW = 32
PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_LEFT = 2.0 - PHI

RESULTS = ROOT / "PN10B_EVENT_GEOMETRY_RESULTS.json"
TRACES = ROOT / "PN10B_EVENT_CENTERED_TRACES.csv"
LANDMARKS = ROOT / "PN10B_CHILD_LANDMARK_COUNTS.csv"
EXAMPLES = ROOT / "PN10B_PRIME_CHILD_EXAMPLES.csv"
NEIGHBORHOODS = ROOT / "PN10B_EXAMPLE_NEIGHBORHOODS.csv"
FIGURE = ROOT / "PN10B_EVENT_GEOMETRY_FIGURE.png"


def child_coordinates(numbers: np.ndarray, chunk_size: int = 100_000) -> dict[str, np.ndarray]:
    """Return native child coordinates for every supplied integer."""
    thresholds = numbers.astype(np.float64) ** 0.45
    prime_table = base_primes(int(math.ceil(float(np.max(thresholds)))) + 2)
    count = len(numbers)
    centroid = np.empty(count, dtype=np.float64)
    dispersion = np.empty(count, dtype=np.float64)
    coupling = np.empty(count, dtype=np.float64)
    flips = np.empty(count, dtype=np.int16)
    minimum = np.empty(count, dtype=np.float64)
    maximum = np.empty(count, dtype=np.float64)

    for start in range(0, count, chunk_size):
        stop = min(start + chunk_size, count)
        n = numbers[start:stop]
        t = thresholds[start:stop]
        last = np.searchsorted(prime_table, t, side="right") - 1
        gate_indices = last[:, None] - np.arange(K, dtype=np.int64)[None, :]
        gates = prime_table[gate_indices]
        a = 2.0 * (n[:, None] % gates).astype(np.float64) / gates.astype(np.float64)
        s = a - 1.0
        centroid[start:stop] = np.mean(a, axis=1)
        dispersion[start:stop] = np.mean(np.abs(s), axis=1)
        coupling[start:stop] = np.mean(s[:, :-1] * s[:, 1:], axis=1)
        flips[start:stop] = np.count_nonzero(s[:, :-1] * s[:, 1:] < 0.0, axis=1)
        minimum[start:stop] = np.min(a, axis=1)
        maximum[start:stop] = np.max(a, axis=1)

    return {
        "centroid": centroid,
        "dispersion": dispersion,
        "coupling": coupling,
        "flips": flips,
        "minimum": minimum,
        "maximum": maximum,
    }


def exact_children(n: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    threshold = n**0.45
    prime_table = base_primes(int(math.ceil(threshold)) + 2)
    last = int(np.searchsorted(prime_table, threshold, side="right") - 1)
    gates = prime_table[last - np.arange(K, dtype=np.int64)]
    remainders = n % gates
    a = 2.0 * remainders.astype(np.float64) / gates.astype(np.float64)
    b = 2.0 - a
    return gates, remainders, a, b


def describe(values: np.ndarray) -> dict[str, float | int]:
    q = np.quantile(values.astype(np.float64), [0, 0.01, 0.05, 0.10, 0.25, 0.5, 0.75, 0.90, 0.95, 0.99, 1])
    return {
        "n": int(len(values)),
        "mean": float(np.mean(values)),
        "sd": float(np.std(values)),
        "min": float(q[0]),
        "p01": float(q[1]),
        "p05": float(q[2]),
        "p10": float(q[3]),
        "p25": float(q[4]),
        "median": float(q[5]),
        "p75": float(q[6]),
        "p90": float(q[7]),
        "p95": float(q[8]),
        "p99": float(q[9]),
        "max": float(q[10]),
    }


def standardized_difference(first: np.ndarray, second: np.ndarray) -> dict[str, float]:
    first = first.astype(np.float64)
    second = second.astype(np.float64)
    difference = float(np.mean(first) - np.mean(second))
    pooled_sd = math.sqrt((float(np.var(first)) + float(np.var(second))) / 2.0)
    return {
        "prime_minus_survivor_composite_mean": difference,
        "pooled_sd": pooled_sd,
        "standardized_mean_difference": difference / pooled_sd if pooled_sd else 0.0,
    }


def frequency_table(values: np.ndarray) -> list[dict[str, float | int]]:
    unique, counts = np.unique(values, return_counts=True)
    return [
        {"value": int(value), "count": int(count), "share": float(count / len(values))}
        for value, count in zip(unique, counts)
    ]


def event_profile(
    centers: np.ndarray,
    event_name: str,
    numbers: np.ndarray,
    is_prime: np.ndarray,
    survivors: np.ndarray,
    parent_progress: np.ndarray,
    child: dict[str, np.ndarray],
) -> list[dict[str, float | int | str]]:
    centers = centers[(centers >= LOW + WINDOW) & (centers < HIGH - WINDOW)]
    center_indices = centers - LOW
    rows: list[dict[str, float | int | str]] = []
    for offset in range(-WINDOW, WINDOW + 1):
        idx = center_indices + offset
        p = parent_progress[idx]
        c = child["centroid"][idx]
        d = child["dispersion"][idx]
        h = child["coupling"][idx]
        f = child["flips"][idx].astype(np.float64)
        rows.append(
            {
                "event": event_name,
                "offset": offset,
                "center_count": int(len(centers)),
                "prime_rate": float(np.mean(is_prime[idx])),
                "survivor_rate": float(np.mean(survivors[idx])),
                "parent_progress_mean": float(np.mean(p)),
                "parent_progress_median": float(np.median(p)),
                "parent_progress_p10": float(np.quantile(p, 0.10)),
                "parent_progress_p90": float(np.quantile(p, 0.90)),
                "child_centroid_mean": float(np.mean(c)),
                "child_centroid_median": float(np.median(c)),
                "child_centroid_p10": float(np.quantile(c, 0.10)),
                "child_centroid_p90": float(np.quantile(c, 0.90)),
                "child_dispersion_mean": float(np.mean(d)),
                "child_coupling_mean": float(np.mean(h)),
                "child_flip_count_mean": float(np.mean(f)),
            }
        )
    return rows


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def line_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    subtitle: str,
    series: list[tuple[str, np.ndarray, np.ndarray, tuple[int, int, int]]],
    y_bounds: tuple[float, float] | None = None,
    ridge: float | None = None,
) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=16, fill=(248, 250, 252), outline=(211, 218, 226), width=2)
    draw.text((x0 + 22, y0 + 16), title, font=font(22, True), fill=(24, 34, 48))
    draw.text((x0 + 22, y0 + 48), subtitle, font=font(15), fill=(79, 91, 106))
    left, top, right, bottom = x0 + 72, y0 + 94, x1 - 28, y1 - 54
    all_x = np.concatenate([s[1] for s in series])
    all_y = np.concatenate([s[2] for s in series])
    xmin, xmax = float(np.min(all_x)), float(np.max(all_x))
    if y_bounds is None:
        ymin, ymax = float(np.min(all_y)), float(np.max(all_y))
        padding = max((ymax - ymin) * 0.08, 1e-8)
        ymin -= padding
        ymax += padding
    else:
        ymin, ymax = y_bounds

    def px(x: float) -> float:
        return left + (x - xmin) * (right - left) / (xmax - xmin)

    def py(y: float) -> float:
        return bottom - (y - ymin) * (bottom - top) / (ymax - ymin)

    for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
        yy = top + frac * (bottom - top)
        value = ymax - frac * (ymax - ymin)
        draw.line((left, yy, right, yy), fill=(224, 229, 235), width=1)
        draw.text((x0 + 10, yy - 8), f"{value:.4f}", font=font(12), fill=(92, 102, 115))
    if xmin <= 0 <= xmax:
        draw.line((px(0), top, px(0), bottom), fill=(42, 48, 56), width=2)
    if ridge is not None and ymin <= ridge <= ymax:
        draw.line((left, py(ridge), right, py(ridge)), fill=(83, 91, 101), width=2)
        draw.text((right - 78, py(ridge) - 20), f"ridge {ridge:g}", font=font(12), fill=(83, 91, 101))
    for name, xs, ys, color in series:
        points = [(px(float(x)), py(float(y))) for x, y in zip(xs, ys)]
        draw.line(points, fill=color, width=4, joint="curve")
    legend_x = left
    for name, _, _, color in series:
        draw.line((legend_x, y1 - 26, legend_x + 26, y1 - 26), fill=color, width=4)
        draw.text((legend_x + 34, y1 - 36), name, font=font(13), fill=(47, 57, 69))
        legend_x += 34 + int(draw.textlength(name, font=font(13))) + 28


def histogram_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    prime_values: np.ndarray,
    composite_values: np.ndarray,
) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=16, fill=(248, 250, 252), outline=(211, 218, 226), width=2)
    draw.text((x0 + 22, y0 + 16), "Child-centroid distribution", font=font(22, True), fill=(24, 34, 48))
    draw.text((x0 + 22, y0 + 48), "Each node is the mean of its nine paid-gate A readings", font=font(15), fill=(79, 91, 106))
    left, top, right, bottom = x0 + 72, y0 + 94, x1 - 28, y1 - 54
    bins = np.linspace(0.15, 1.85, 35)
    hp, edges = np.histogram(prime_values, bins=bins, density=True)
    hc, _ = np.histogram(composite_values, bins=bins, density=True)
    ymax = max(float(np.max(hp)), float(np.max(hc))) * 1.08

    def px(x: float) -> float:
        return left + (x - bins[0]) * (right - left) / (bins[-1] - bins[0])

    def py(y: float) -> float:
        return bottom - y * (bottom - top) / ymax

    draw.line((left, bottom, right, bottom), fill=(98, 108, 120), width=2)
    draw.line((px(1.0), top, px(1.0), bottom), fill=(42, 48, 56), width=2)
    for values, color in ((hc, (211, 149, 74)), (hp, (61, 121, 190))):
        pts = [(px(float((edges[i] + edges[i + 1]) / 2)), py(float(values[i]))) for i in range(len(values))]
        draw.line(pts, fill=color, width=4, joint="curve")
    for tick in (0.25, PHI_LEFT, 1.0, PHI, 1.75):
        draw.line((px(tick), bottom, px(tick), bottom + 7), fill=(98, 108, 120), width=2)
        draw.text((px(tick) - 18, bottom + 11), f"{tick:.2f}", font=font(12), fill=(92, 102, 115))
    draw.line((left, y1 - 26, left + 26, y1 - 26), fill=(61, 121, 190), width=4)
    draw.text((left + 34, y1 - 36), "prime", font=font(13), fill=(47, 57, 69))
    draw.line((left + 118, y1 - 26, left + 144, y1 - 26), fill=(211, 149, 74), width=4)
    draw.text((left + 152, y1 - 36), "survivor composite", font=font(13), fill=(47, 57, 69))


def make_figure(
    trace_rows: list[dict[str, float | int | str]],
    prime_centroid: np.ndarray,
    composite_centroid: np.ndarray,
    rank_summary: list[dict[str, float | int]],
    first_a: np.ndarray,
) -> None:
    image = Image.new("RGB", (1660, 1220), (239, 243, 247))
    draw = ImageDraw.Draw(image)
    draw.text((44, 30), "PN10B post-hoc event geometry", font=font(34, True), fill=(20, 30, 45))
    draw.text(
        (44, 77),
        "Registered prediction remains NULL; this figure restores the descriptive crest/trough structure that verdict did not show.",
        font=font(18),
        fill=(65, 78, 94),
    )

    prime_rows = [r for r in trace_rows if r["event"] == "prime_center"]
    composite_rows = [r for r in trace_rows if r["event"] == "survivor_composite_center"]
    xs = np.array([int(r["offset"]) for r in prime_rows], dtype=np.float64)
    line_panel(
        draw,
        (38, 122, 816, 606),
        "Parent factor-survival coordinate around an event",
        "Raw integer offset; a prime reaches the 1.0 square-root ridge at offset 0",
        [
            ("prime-centred", xs, np.array([float(r["parent_progress_mean"]) for r in prime_rows]), (61, 121, 190)),
            (
                "late-composite-centred",
                xs,
                np.array([float(r["parent_progress_mean"]) for r in composite_rows]),
                (211, 149, 74),
            ),
        ],
        y_bounds=(0.0, 1.02),
        ridge=1.0,
    )
    line_panel(
        draw,
        (844, 122, 1622, 606),
        "Nine-child centroid around the same event",
        "Focused scale: the paid-gate child phase drifts slowly and has no special offset-0 crest",
        [
            ("prime-centred", xs, np.array([float(r["child_centroid_mean"]) for r in prime_rows]), (61, 121, 190)),
            (
                "late-composite-centred",
                xs,
                np.array([float(r["child_centroid_mean"]) for r in composite_rows]),
                (211, 149, 74),
            ),
        ],
        ridge=1.0,
    )
    histogram_panel(draw, (38, 632, 816, 1158), prime_centroid, composite_centroid)

    rank_x = np.arange(1, K + 1, dtype=np.float64)
    rank_mean = np.array([float(r["prime_mean_a"]) for r in rank_summary])
    line_panel(
        draw,
        (844, 632, 1622, 1158),
        "Nine child phases at prime nodes",
        "Population mean hugs 1.0; one actual prime contains strong alternating asymmetry",
        [
            ("mean across primes", rank_x, rank_mean, (61, 121, 190)),
            ("prime 4,000,000,007", rank_x, first_a, (176, 92, 81)),
        ],
        y_bounds=(0.0, 2.0),
        ridge=1.0,
    )
    image.save(FIGURE)


def main() -> None:
    numbers, lpf = segmented_least_prime_factor(LOW, HIGH)
    is_prime = lpf == 0
    thresholds = numbers.astype(np.float64) ** 0.45
    survivors = is_prime | (lpf.astype(np.float64) > thresholds)
    survivor_composite = survivors & ~is_prime

    parent_progress = np.empty(len(numbers), dtype=np.float64)
    parent_progress[is_prime] = 1.0
    composite = ~is_prime
    parent_progress[composite] = 2.0 * np.log(lpf[composite].astype(np.float64)) / np.log(
        numbers[composite].astype(np.float64)
    )

    child = child_coordinates(numbers)
    prime_idx = np.flatnonzero(is_prime)
    survivor_composite_idx = np.flatnonzero(survivor_composite)
    prime_numbers = numbers[prime_idx]
    survivor_composite_numbers = numbers[survivor_composite_idx]

    # Exact nine-child matrices for the survivor population.
    survivor_numbers = numbers[survivors]
    threshold_survivors = survivor_numbers.astype(np.float64) ** 0.45
    prime_table = base_primes(int(math.ceil(float(np.max(threshold_survivors)))) + 2)
    last = np.searchsorted(prime_table, threshold_survivors, side="right") - 1
    gate_indices = last[:, None] - np.arange(K, dtype=np.int64)[None, :]
    gates = prime_table[gate_indices]
    remainders = survivor_numbers[:, None] % gates
    a = 2.0 * remainders.astype(np.float64) / gates.astype(np.float64)
    b = 2.0 - a
    s = a - 1.0
    survivor_labels = is_prime[survivors]
    prime_a = a[survivor_labels]
    composite_a = a[~survivor_labels]

    rank_summary: list[dict[str, float | int]] = []
    for rank in range(K):
        rank_summary.append(
            {
                "gate_rank": rank + 1,
                "prime_mean_a": float(np.mean(prime_a[:, rank])),
                "prime_median_a": float(np.median(prime_a[:, rank])),
                "prime_p10_a": float(np.quantile(prime_a[:, rank], 0.10)),
                "prime_p90_a": float(np.quantile(prime_a[:, rank], 0.90)),
                "prime_below_ridge_share": float(np.mean(prime_a[:, rank] < 1.0)),
                "composite_mean_a": float(np.mean(composite_a[:, rank])),
                "composite_median_a": float(np.median(composite_a[:, rank])),
            }
        )

    landmark_ranges = [
        ("left_singularity_well", 0.0, 0.25),
        ("left_inner_to_phi", 0.25, PHI_LEFT),
        ("left_phi_to_ridge", PHI_LEFT, 1.0),
        ("ridge_to_right_phi", 1.0, PHI),
        ("right_phi_to_inner", PHI, 1.75),
        ("right_singularity_well", 1.75, 2.0 + 1e-12),
    ]
    landmark_rows: list[dict[str, float | int | str]] = []
    for population, values in (("prime", prime_a.ravel()), ("survivor_composite", composite_a.ravel())):
        for name, lower, upper in landmark_ranges:
            count = int(np.count_nonzero((values >= lower) & (values < upper)))
            landmark_rows.append(
                {
                    "population": population,
                    "landmark_region": name,
                    "lower_inclusive": lower,
                    "upper_exclusive": upper,
                    "count": count,
                    "share": count / len(values),
                }
            )

    prime_centroid = child["centroid"][prime_idx]
    survivor_composite_centroid = child["centroid"][survivor_composite_idx]
    prime_dispersion = child["dispersion"][prime_idx]
    survivor_composite_dispersion = child["dispersion"][survivor_composite_idx]
    prime_coupling = child["coupling"][prime_idx]
    survivor_composite_coupling = child["coupling"][survivor_composite_idx]
    prime_flips = child["flips"][prime_idx]
    survivor_composite_flips = child["flips"][survivor_composite_idx]

    example_specs = [
        ("first_prime", 0),
        ("child_centroid_trough", int(np.argmin(prime_centroid))),
        ("child_centroid_ridge_nearest", int(np.argmin(np.abs(prime_centroid - 1.0)))),
        ("child_centroid_crest", int(np.argmax(prime_centroid))),
        ("maximum_child_spread", int(np.argmax(prime_dispersion))),
    ]
    example_rows: list[dict[str, float | int | str]] = []
    neighborhood_rows: list[dict[str, float | int | str]] = []
    example_summary: list[dict[str, float | int | str]] = []
    for example_name, local_prime_index in example_specs:
        n = int(prime_numbers[local_prime_index])
        idx = n - LOW
        q, r, aa, bb = exact_children(n)
        example_summary.append(
            {
                "example": example_name,
                "n": n,
                "child_centroid": float(child["centroid"][idx]),
                "child_dispersion": float(child["dispersion"][idx]),
                "child_coupling": float(child["coupling"][idx]),
                "child_flip_count": int(child["flips"][idx]),
                "child_minimum": float(child["minimum"][idx]),
                "child_maximum": float(child["maximum"][idx]),
            }
        )
        for rank in range(K):
            next_coupling = ""
            if rank < K - 1:
                next_coupling = float((aa[rank] - 1.0) * (aa[rank + 1] - 1.0))
            example_rows.append(
                {
                    "example": example_name,
                    "n": n,
                    "gate_rank": rank + 1,
                    "gate_q": int(q[rank]),
                    "remainder": int(r[rank]),
                    "phase_a": float(aa[rank]),
                    "phase_b": float(bb[rank]),
                    "signed_orientation": float(aa[rank] - 1.0),
                    "coupling_to_next_rank": next_coupling,
                }
            )
        for offset in range(-16, 17):
            j = idx + offset
            if j < 0 or j >= len(numbers):
                continue
            neighborhood_rows.append(
                {
                    "example": example_name,
                    "center_prime": n,
                    "offset": offset,
                    "n": int(numbers[j]),
                    "is_prime": int(is_prime[j]),
                    "is_c090_survivor": int(survivors[j]),
                    "least_prime_factor": int(lpf[j]),
                    "parent_factor_progress": float(parent_progress[j]),
                    "child_centroid": float(child["centroid"][j]),
                    "child_dispersion": float(child["dispersion"][j]),
                    "child_coupling": float(child["coupling"][j]),
                    "child_flip_count": int(child["flips"][j]),
                }
            )

    trace_rows = event_profile(
        prime_numbers,
        "prime_center",
        numbers,
        is_prime,
        survivors,
        parent_progress,
        child,
    )
    trace_rows.extend(
        event_profile(
            survivor_composite_numbers,
            "survivor_composite_center",
            numbers,
            is_prime,
            survivors,
            parent_progress,
            child,
        )
    )

    prime_trace = [r for r in trace_rows if r["event"] == "prime_center"]
    parent_values = np.array([float(r["parent_progress_mean"]) for r in prime_trace])
    child_values = np.array([float(r["child_centroid_mean"]) for r in prime_trace])
    parent_crest = prime_trace[int(np.argmax(parent_values))]
    parent_trough = prime_trace[int(np.argmin(parent_values))]
    child_crest = prime_trace[int(np.argmax(child_values))]
    child_trough = prime_trace[int(np.argmin(child_values))]

    results = {
        "status": "post_hoc_descriptive_only",
        "registered_pn10b_verdict_unchanged": "NULL",
        "scope": {
            "low_inclusive": LOW,
            "high_exclusive": HIGH,
            "raw_integer_count": int(len(numbers)),
            "prime_count": int(np.count_nonzero(is_prime)),
            "c090_survivor_count": int(np.count_nonzero(survivors)),
            "c090_survivor_composite_count": int(np.count_nonzero(survivor_composite)),
            "child_gate_count": K,
            "event_window_each_side": WINDOW,
        },
        "definitions": {
            "child_phase_a": "A_j(n)=2*(n mod q_j)/q_j for the nine largest already-paid gates q_j<=n^0.45",
            "child_phase_b": "B_j(n)=2-A_j(n)",
            "child_centroid": "mean_j A_j(n)",
            "child_dispersion": "mean_j abs(A_j(n)-1)",
            "child_coupling": "mean_j ((A_j-1)*(A_{j+1}-1))",
            "child_flip_count": "number of adjacent gate ranks whose signed orientations have opposite sign",
            "parent_factor_progress": "1 for a prime; 2*log(least_prime_factor)/log(n) for a composite",
        },
        "node_distributions": {
            "prime": {
                "child_centroid": describe(prime_centroid),
                "child_dispersion": describe(prime_dispersion),
                "child_coupling": describe(prime_coupling),
                "child_flip_count": describe(prime_flips.astype(np.float64)),
                "pooled_child_phase_a": describe(prime_a.ravel()),
            },
            "survivor_composite": {
                "child_centroid": describe(survivor_composite_centroid),
                "child_dispersion": describe(survivor_composite_dispersion),
                "child_coupling": describe(survivor_composite_coupling),
                "child_flip_count": describe(survivor_composite_flips.astype(np.float64)),
                "pooled_child_phase_a": describe(composite_a.ravel()),
            },
        },
        "population_contrasts": {
            "child_centroid": standardized_difference(prime_centroid, survivor_composite_centroid),
            "child_dispersion": standardized_difference(prime_dispersion, survivor_composite_dispersion),
            "child_coupling": standardized_difference(prime_coupling, survivor_composite_coupling),
            "child_flip_count": standardized_difference(
                prime_flips.astype(np.float64), survivor_composite_flips.astype(np.float64)
            ),
        },
        "child_flip_count_frequencies": {
            "prime": frequency_table(prime_flips),
            "survivor_composite": frequency_table(survivor_composite_flips),
        },
        "prime_gate_rank_summary": rank_summary,
        "landmark_regions": landmark_rows,
        "event_centered_extrema": {
            "parent_progress_crest": parent_crest,
            "parent_progress_trough": parent_trough,
            "child_centroid_crest": child_crest,
            "child_centroid_trough": child_trough,
        },
        "example_summary": example_summary,
        "interpretation_guards": [
            "The parent 1.0 crest at a prime is exact but definitional: primality is known only after all factor gates through sqrt(n) are survived.",
            "The alternating neighboring troughs are dominated by parity and ordinary sieve structure.",
            "The paid-gate child phases show strong individual asymmetry but nearly uniform population coverage; survivor composites show nearly the same distribution.",
            "No event-centred child-phase crest at offset zero was established by this representation.",
            "These diagnostics were chosen after the PN10B target was opened and therefore cannot promote the registered NULL verdict.",
        ],
    }

    RESULTS.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    with TRACES.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(trace_rows[0].keys()))
        writer.writeheader()
        writer.writerows(trace_rows)
    with LANDMARKS.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(landmark_rows[0].keys()))
        writer.writeheader()
        writer.writerows(landmark_rows)
    with EXAMPLES.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(example_rows[0].keys()))
        writer.writeheader()
        writer.writerows(example_rows)
    with NEIGHBORHOODS.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(neighborhood_rows[0].keys()))
        writer.writeheader()
        writer.writerows(neighborhood_rows)
    make_figure(trace_rows, prime_centroid, survivor_composite_centroid, rank_summary, prime_a[0])
    print(json.dumps({"results": str(RESULTS), "figure": str(FIGURE), "prime_count": len(prime_numbers)}, indent=2))


if __name__ == "__main__":
    main()
