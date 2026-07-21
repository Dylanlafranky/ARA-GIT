"""PN10B registered child-phase prime-ranking test.

Deterministic arithmetic source: complete integer intervals declared in
PN10B_CHILD_PHASE_PRIME_RANKING_PROTOCOL.md. No external data are required.
The script refuses to run unless both protocol and source hashes match the
freeze manifest written before the fresh target is opened.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT / "PN10B_CHILD_PHASE_PRIME_RANKING_PROTOCOL.md"
SOURCE = ROOT / "pn10b_child_phase_prime_ranking.py"
FREEZE = ROOT / "PN10B_FREEZE_MANIFEST.json"
RESULT_JSON = ROOT / "PN10B_CHILD_PHASE_RESULTS.json"
SCORES_CSV = ROOT / "PN10B_FRESH_TARGET_SCORES.csv"
METRICS_CSV = ROOT / "PN10B_MODEL_METRICS.csv"
COMPARISONS_CSV = ROOT / "PN10B_FRESH_COMPARISONS.csv"
FIGURE = ROOT / "PN10B_CHILD_PHASE_FIGURE.png"

K = 9
L2 = 0.01
MAX_STEPS = 40
BOOTSTRAP_BLOCKS = 100
BOOTSTRAP_DRAWS = 2000
BOOTSTRAP_SEED = 20260720
MODEL_ORDER = (
    "parent_empirical",
    "buchstab_parent",
    "ara_compact",
    "raw_compact",
    "ara_full",
    "raw_full",
    "ara_order_scrambled",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def base_primes(limit: int) -> np.ndarray:
    sieve = np.ones(limit + 1, dtype=bool)
    sieve[:2] = False
    for p in range(2, math.isqrt(limit) + 1):
        if sieve[p]:
            sieve[p * p : limit + 1 : p] = False
    return np.flatnonzero(sieve).astype(np.int64)


def segmented_least_prime_factor(low: int, high: int) -> tuple[np.ndarray, np.ndarray]:
    numbers = np.arange(low, high, dtype=np.int64)
    lpf = np.zeros(high - low, dtype=np.int64)
    for p64 in base_primes(math.isqrt(high - 1)):
        p = int(p64)
        start = max(p * p, ((low + p - 1) // p) * p)
        if start >= high:
            continue
        view = lpf[start - low :: p]
        unset = view == 0
        view[unset] = p
    return numbers, lpf


def row_rotate(values: np.ndarray, shifts: np.ndarray) -> np.ndarray:
    columns = np.arange(values.shape[1], dtype=np.int64)[None, :]
    source_columns = (columns + shifts[:, None]) % values.shape[1]
    return np.take_along_axis(values, source_columns, axis=1)


@dataclass
class IntervalData:
    name: str
    numbers: np.ndarray
    labels: np.ndarray
    features: dict[str, np.ndarray]
    guards: dict[str, float | int | bool]
    prevalence: float
    survivor_count: int
    prime_count: int
    composite_count: int
    sample_rows: list[dict]


def build_interval(name: str, low: int, high: int) -> IntervalData:
    numbers_all, lpf = segmented_least_prime_factor(low, high)
    thresholds = numbers_all.astype(np.float64) ** 0.45
    is_prime_all = lpf == 0
    survivors = is_prime_all | (lpf.astype(np.float64) > thresholds)

    numbers = numbers_all[survivors]
    labels = is_prime_all[survivors].astype(np.float64)
    threshold_survivors = thresholds[survivors]

    prime_table = base_primes(int(math.ceil(float(np.max(threshold_survivors)))) + 2)
    last_gate_index = np.searchsorted(prime_table, threshold_survivors, side="right") - 1
    if int(np.min(last_gate_index)) < K - 1:
        raise RuntimeError("Not enough already-tested gates for the registered K=9 child representation")
    gate_indices = last_gate_index[:, None] - np.arange(K, dtype=np.int64)[None, :]
    gates = prime_table[gate_indices]
    remainders = numbers[:, None] % gates
    u = remainders.astype(np.float64) / gates.astype(np.float64)
    a = 2.0 * u
    b = 2.0 - a
    s = a - 1.0
    h = s[:, :-1] * s[:, 1:]

    ara_compact = np.column_stack(
        [np.mean(s, axis=1), np.mean(np.abs(s), axis=1), np.std(s, axis=1), np.mean(h, axis=1)]
    )
    raw_compact = np.column_stack(
        [np.mean(u, axis=1), np.std(u, axis=1), np.min(u, axis=1), np.max(u, axis=1)]
    )
    ara_full = np.column_stack([s, h])
    raw_full = np.column_stack([u, u[:, :-1] - u[:, 1:]])
    scrambled_s = row_rotate(s, numbers % K)
    scrambled_h = scrambled_s[:, :-1] * scrambled_s[:, 1:]
    ara_order_scrambled = np.column_stack([scrambled_s, scrambled_h])

    features = {
        "ara_compact": ara_compact,
        "raw_compact": raw_compact,
        "ara_full": ara_full,
        "raw_full": raw_full,
        "ara_order_scrambled": ara_order_scrambled,
    }

    closure_error = float(np.max(np.abs(a + b - 2.0)))
    max_gate_overrun = float(np.max(gates[:, 0].astype(np.float64) - threshold_survivors))
    zero_remainders = int(np.count_nonzero(remainders == 0))
    guards = {
        "max_abs_a_plus_b_minus_2": closure_error,
        "max_gate_minus_threshold": max_gate_overrun,
        "zero_remainders": zero_remainders,
        "all_gates_already_tested": bool(max_gate_overrun <= 0.0),
    }

    sample_rows = []
    for i in np.linspace(0, len(numbers) - 1, 10, dtype=int):
        sample_rows.append(
            {
                "n": int(numbers[i]),
                "label_prime": int(labels[i]),
                "parent_threshold": float(threshold_survivors[i]),
                "largest_child_gate": int(gates[i, 0]),
                "smallest_child_gate": int(gates[i, -1]),
                "phase_a_largest_gate": float(a[i, 0]),
                "phase_b_largest_gate": float(b[i, 0]),
                "mean_signed_child_orientation": float(ara_compact[i, 0]),
                "mean_adjacent_child_coupling": float(ara_compact[i, 3]),
            }
        )

    prime_count = int(np.count_nonzero(labels))
    survivor_count = int(len(numbers))
    return IntervalData(
        name=name,
        numbers=numbers,
        labels=labels,
        features=features,
        guards=guards,
        prevalence=prime_count / survivor_count,
        survivor_count=survivor_count,
        prime_count=prime_count,
        composite_count=survivor_count - prime_count,
        sample_rows=sample_rows,
    )


@dataclass
class LogisticModel:
    mean: np.ndarray
    scale: np.ndarray
    beta: np.ndarray
    iterations: int


def sigmoid(z: np.ndarray) -> np.ndarray:
    z = np.clip(z, -40.0, 40.0)
    return 1.0 / (1.0 + np.exp(-z))


def fit_logistic(x: np.ndarray, y: np.ndarray) -> LogisticModel:
    mean = np.mean(x, axis=0)
    scale = np.std(x, axis=0)
    scale[scale < 1e-12] = 1.0
    z = (x - mean) / scale
    design = np.column_stack([np.ones(len(z)), z])
    prevalence = float(np.clip(np.mean(y), 1e-9, 1.0 - 1e-9))
    beta = np.zeros(design.shape[1], dtype=np.float64)
    beta[0] = math.log(prevalence / (1.0 - prevalence))
    penalty = np.ones(design.shape[1], dtype=np.float64)
    penalty[0] = 0.0

    iterations = MAX_STEPS
    for step in range(MAX_STEPS):
        prediction = sigmoid(design @ beta)
        weights = np.maximum(prediction * (1.0 - prediction), 1e-9)
        gradient = design.T @ (prediction - y) / len(y) + L2 * penalty * beta
        hessian = (design.T * weights) @ design / len(y) + L2 * np.diag(penalty)
        delta = np.linalg.solve(hessian, gradient)
        beta -= delta
        if float(np.max(np.abs(delta))) < 1e-9:
            iterations = step + 1
            break
    return LogisticModel(mean=mean, scale=scale, beta=beta, iterations=iterations)


def predict_logistic(model: LogisticModel, x: np.ndarray) -> np.ndarray:
    z = (x - model.mean) / model.scale
    design = np.column_stack([np.ones(len(z)), z])
    return sigmoid(design @ model.beta)


def buchstab_parent_probability() -> float:
    u = 2.0 / 0.90
    omega = (1.0 + math.log(u - 1.0)) / u
    return 0.45 / omega


def per_event_log_loss(y: np.ndarray, prediction: np.ndarray) -> np.ndarray:
    p = np.clip(prediction, 1e-12, 1.0 - 1e-12)
    return -(y * np.log2(p) + (1.0 - y) * np.log2(1.0 - p))


def auc_rank(y: np.ndarray, score: np.ndarray) -> float:
    order = np.argsort(score, kind="mergesort")
    sorted_scores = score[order]
    ranks = np.empty(len(score), dtype=np.float64)
    start = 0
    while start < len(score):
        end = start + 1
        while end < len(score) and sorted_scores[end] == sorted_scores[start]:
            end += 1
        average_rank = 0.5 * ((start + 1) + end)
        ranks[order[start:end]] = average_rank
        start = end
    positives = y == 1
    n_pos = int(np.count_nonzero(positives))
    n_neg = len(y) - n_pos
    return float((np.sum(ranks[positives]) - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def metric_row(stage: str, model: str, y: np.ndarray, prediction: np.ndarray) -> dict:
    loss = per_event_log_loss(y, prediction)
    base = float(np.mean(y))
    k = max(1, int(math.ceil(0.10 * len(y))))
    top = np.argsort(-prediction, kind="mergesort")[:k]
    top_precision = float(np.mean(y[top]))
    return {
        "stage": stage,
        "model": model,
        "events": int(len(y)),
        "primes": int(np.count_nonzero(y)),
        "prevalence": base,
        "log_loss_bits": float(np.mean(loss)),
        "brier": float(np.mean((prediction - y) ** 2)),
        "auc": auc_rank(y, prediction),
        "top_decile_precision": top_precision,
        "top_decile_lift": top_precision / base,
        "calibration_error": float(np.mean(prediction) - base),
        "prediction_min": float(np.min(prediction)),
        "prediction_max": float(np.max(prediction)),
    }


def fit_and_score(train: IntervalData | tuple[IntervalData, IntervalData], test: IntervalData) -> tuple[dict, dict]:
    if isinstance(train, tuple):
        train_labels = np.concatenate([train[0].labels, train[1].labels])
        train_features = {
            name: np.vstack([train[0].features[name], train[1].features[name]]) for name in train[0].features
        }
    else:
        train_labels = train.labels
        train_features = train.features

    parent_probability = float(np.mean(train_labels))
    predictions: dict[str, np.ndarray] = {
        "parent_empirical": np.full(len(test.labels), parent_probability, dtype=np.float64),
        "buchstab_parent": np.full(len(test.labels), buchstab_parent_probability(), dtype=np.float64),
    }
    fitted = {}
    for name in ("ara_compact", "raw_compact", "ara_full", "raw_full", "ara_order_scrambled"):
        model = fit_logistic(train_features[name], train_labels)
        predictions[name] = predict_logistic(model, test.features[name])
        fitted[name] = {
            "iterations": model.iterations,
            "feature_count": int(train_features[name].shape[1]),
            "intercept": float(model.beta[0]),
            "coefficients": [float(v) for v in model.beta[1:]],
            "standardization_mean": [float(v) for v in model.mean],
            "standardization_scale": [float(v) for v in model.scale],
        }
    return predictions, {"training_prevalence": parent_probability, "models": fitted}


def paired_block_bootstrap(
    y: np.ndarray,
    first: np.ndarray,
    second: np.ndarray,
    rng: np.random.Generator,
) -> dict:
    difference = per_event_log_loss(y, second) - per_event_log_loss(y, first)
    blocks = np.array_split(difference, BOOTSTRAP_BLOCKS)
    block_means = np.array([np.mean(block) for block in blocks], dtype=np.float64)
    draws = np.empty(BOOTSTRAP_DRAWS, dtype=np.float64)
    for i in range(BOOTSTRAP_DRAWS):
        selected = rng.integers(0, BOOTSTRAP_BLOCKS, size=BOOTSTRAP_BLOCKS)
        draws[i] = float(np.mean(block_means[selected]))
    return {
        "gain_bits_per_event": float(np.mean(difference)),
        "ci95_low": float(np.quantile(draws, 0.025)),
        "ci95_high": float(np.quantile(draws, 0.975)),
        "positive_blocks": int(np.count_nonzero(block_means > 0.0)),
        "blocks": BOOTSTRAP_BLOCKS,
        "draws": BOOTSTRAP_DRAWS,
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def calibration_rows(y: np.ndarray, prediction: np.ndarray, bins: int = 10) -> list[dict]:
    order = np.argsort(prediction, kind="mergesort")
    rows = []
    for index, block in enumerate(np.array_split(order, bins), start=1):
        rows.append(
            {
                "bin": index,
                "events": int(len(block)),
                "mean_prediction": float(np.mean(prediction[block])),
                "observed_prime_rate": float(np.mean(y[block])),
            }
        )
    return rows


def make_figure(metrics: list[dict], comparisons: list[dict], calibration: list[dict], result: dict) -> None:
    width, height = 1600, 1060
    white, ink, muted = "#ffffff", "#1f2937", "#667085"
    grid, blue, gold, orange, pale = "#d9e1ea", "#2f6fbb", "#c08a24", "#d97706", "#eef3f8"
    image = Image.new("RGB", (width, height), white)
    draw = ImageDraw.Draw(image)
    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 34)
        head_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 22)
        body_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 17)
        small_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 14)
    except OSError:
        title_font = head_font = body_font = small_font = ImageFont.load_default()

    draw.text((60, 34), "PN10B child-phase prime ranking", fill=ink, font=title_font)
    draw.text(
        (60, 78),
        "Fresh target [4,000,000,000, 4,001,000,000); lower log loss is better",
        fill=muted,
        font=body_font,
    )
    panels = [(55, 125, 765, 535), (835, 125, 1545, 535), (55, 590, 765, 1005), (835, 590, 1545, 1005)]
    for panel in panels:
        draw.rounded_rectangle(panel, radius=16, fill=white, outline=grid, width=2)

    fresh = {r["model"]: r for r in metrics if r["stage"] == "pooled_D_E_to_fresh_F"}
    names = ["parent_empirical", "buchstab_parent", "ara_compact", "raw_compact", "ara_full", "raw_full", "ara_order_scrambled"]
    labels = ["Parent", "Buchstab", "ARA compact", "Raw compact", "ARA full", "Raw full", "ARA scrambled"]

    # Panel 1: exact log-loss comparison.
    x0, y0, x1, y1 = panels[0]
    draw.text((x0 + 22, y0 + 18), "Fresh-target log loss", fill=ink, font=head_font)
    draw.text((x0 + 22, y0 + 48), "Bits per surviving integer", fill=muted, font=small_font)
    values = [fresh[n]["log_loss_bits"] for n in names]
    vmin, vmax = min(values), max(values)
    lo = vmin - max(1e-5, 0.15 * (vmax - vmin))
    hi = vmax + max(1e-5, 0.10 * (vmax - vmin))
    px0, py0, px1, py1 = x0 + 150, y0 + 80, x1 - 40, y1 - 38
    for i, (label, value, name) in enumerate(zip(labels, values, names)):
        yy = py0 + i * (py1 - py0) / (len(names) - 1)
        draw.text((px0 - 12, yy), label, fill=ink, font=small_font, anchor="rm")
        xx = px0 + (px1 - px0) * (value - lo) / (hi - lo)
        color = blue if name.startswith("ara_") and name != "ara_order_scrambled" else gold if name == "buchstab_parent" else muted
        draw.line((px0, yy, px1, yy), fill=pale, width=8)
        draw.ellipse((xx - 7, yy - 7, xx + 7, yy + 7), fill=color, outline=ink, width=1)
        draw.text((xx + 12, yy), f"{value:.6f}", fill=ink, font=small_font, anchor="lm")

    # Panel 2: paired gains and intervals.
    x0, y0, x1, y1 = panels[1]
    draw.text((x0 + 22, y0 + 18), "Fresh paired log-loss gains", fill=ink, font=head_font)
    draw.text((x0 + 22, y0 + 48), "Positive means first named model is better; 95% block-bootstrap CI", fill=muted, font=small_font)
    comparison_labels = {
        "ara_full_vs_parent_empirical": "ARA full - Parent",
        "ara_full_vs_raw_full": "ARA full - Raw full",
        "ara_full_vs_ara_order_scrambled": "ARA full - Scrambled",
        "ara_compact_vs_parent_empirical": "ARA compact - Parent",
        "ara_compact_vs_raw_compact": "ARA compact - Raw compact",
    }
    chosen = [c for c in comparisons if c["comparison"] in comparison_labels]
    bound = max(abs(c["ci95_low"]) for c in chosen) if chosen else 1e-4
    bound = max(bound, max(abs(c["ci95_high"]) for c in chosen) if chosen else bound) * 1.15
    px0, py0, px1, py1 = x0 + 170, y0 + 88, x1 - 38, y1 - 45
    zero_x = px0 + (px1 - px0) / 2
    draw.line((zero_x, py0 - 20, zero_x, py1 + 15), fill=ink, width=2)
    for i, row in enumerate(chosen):
        yy = py0 + i * (py1 - py0) / max(1, len(chosen) - 1)
        draw.text((px0 - 12, yy), comparison_labels[row["comparison"]], fill=ink, font=small_font, anchor="rm")
        def gx(v: float) -> float:
            return px0 + (px1 - px0) * (v + bound) / (2 * bound)
        draw.line((gx(row["ci95_low"]), yy, gx(row["ci95_high"]), yy), fill=blue, width=4)
        draw.ellipse((gx(row["gain_bits_per_event"]) - 6, yy - 6, gx(row["gain_bits_per_event"]) + 6, yy + 6), fill=blue)

    # Panel 3: calibration.
    x0, y0, x1, y1 = panels[2]
    draw.text((x0 + 22, y0 + 18), "ARA full calibration", fill=ink, font=head_font)
    draw.text((x0 + 22, y0 + 48), "Ten equal-count bins on the fresh target", fill=muted, font=small_font)
    px0, py0, px1, py1 = x0 + 75, y0 + 84, x1 - 35, y1 - 58
    vals = [r["mean_prediction"] for r in calibration] + [r["observed_prime_rate"] for r in calibration]
    cal_lo, cal_hi = min(vals) - 0.002, max(vals) + 0.002
    draw.line((px0, py1, px1, py0), fill=grid, width=2)
    points = []
    for row in calibration:
        xx = px0 + (px1 - px0) * (row["mean_prediction"] - cal_lo) / (cal_hi - cal_lo)
        yy = py1 - (py1 - py0) * (row["observed_prime_rate"] - cal_lo) / (cal_hi - cal_lo)
        points.append((xx, yy))
    draw.line(points, fill=orange, width=3)
    for xx, yy in points:
        draw.ellipse((xx - 5, yy - 5, xx + 5, yy + 5), fill=orange, outline=ink)
    draw.text(((px0 + px1) / 2, y1 - 30), "Mean predicted prime probability", fill=muted, font=small_font, anchor="mm")

    # Panel 4: plain-language registered outcome.
    x0, y0, x1, y1 = panels[3]
    draw.text((x0 + 22, y0 + 18), "Registered result", fill=ink, font=head_font)
    verdict = result["verdict"]
    draw.text((x0 + 22, y0 + 66), verdict, fill=blue if verdict in ("SUPPORTED", "SUGGESTIVE") else orange, font=title_font)
    fresh_summary = result["intervals"]["F"]
    lines = [
        f"Survivors at c=0.90: {fresh_summary['survivor_count']:,}",
        f"Primes / composites: {fresh_summary['prime_count']:,} / {fresh_summary['composite_count']:,}",
        f"ARA full AUC: {fresh['ara_full']['auc']:.6f}",
        f"ARA full vs parent: {result['fresh_comparisons']['ara_full_vs_parent_empirical']['gain_bits_per_event']:+.6g} bits/event",
        "The test ranks survivors only; exact primality still requires the remaining gates.",
    ]
    yy = y0 + 135
    for line in lines:
        draw.text((x0 + 22, yy), line, fill=ink if not line.startswith("The test") else muted, font=body_font)
        yy += 45
    image.save(FIGURE)


def main() -> None:
    started = time.time()
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    if sha256(PROTOCOL) != freeze["protocol_sha256"]:
        raise RuntimeError("Protocol hash mismatch; PN10B is not allowed to open data")
    if sha256(SOURCE) != freeze["source_sha256"]:
        raise RuntimeError("Source hash mismatch; PN10B is not allowed to open data")

    intervals = freeze["intervals"]
    d = build_interval("D", *intervals["D"])
    e = build_interval("E", *intervals["E"])
    # The fresh interval is opened only after D-to-E model definitions are fixed by the source hash.
    f = build_interval("F", *intervals["F"])

    stage_a_predictions, stage_a_fit = fit_and_score(d, e)
    stage_b_predictions, stage_b_fit = fit_and_score((d, e), f)

    metric_rows = []
    for model in MODEL_ORDER:
        metric_rows.append(metric_row("D_to_E", model, e.labels, stage_a_predictions[model]))
        metric_rows.append(metric_row("pooled_D_E_to_fresh_F", model, f.labels, stage_b_predictions[model]))
    write_csv(METRICS_CSV, metric_rows)

    rng = np.random.default_rng(BOOTSTRAP_SEED)
    pairs = [
        ("ara_full_vs_parent_empirical", "ara_full", "parent_empirical"),
        ("ara_full_vs_raw_full", "ara_full", "raw_full"),
        ("ara_full_vs_ara_order_scrambled", "ara_full", "ara_order_scrambled"),
        ("ara_compact_vs_parent_empirical", "ara_compact", "parent_empirical"),
        ("ara_compact_vs_raw_compact", "ara_compact", "raw_compact"),
        ("raw_full_vs_parent_empirical", "raw_full", "parent_empirical"),
    ]
    comparison_rows = []
    fresh_comparisons = {}
    for comparison, first, second in pairs:
        row = paired_block_bootstrap(f.labels, stage_b_predictions[first], stage_b_predictions[second], rng)
        row = {"comparison": comparison, "first_model": first, "second_model": second, **row}
        comparison_rows.append(row)
        fresh_comparisons[comparison] = {k: v for k, v in row.items() if k not in ("comparison", "first_model", "second_model")}
    write_csv(COMPARISONS_CSV, comparison_rows)

    with SCORES_CSV.open("w", newline="", encoding="utf-8") as handle:
        fields = ["n", "label_prime", *MODEL_ORDER]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for i, n in enumerate(f.numbers):
            writer.writerow(
                {
                    "n": int(n),
                    "label_prime": int(f.labels[i]),
                    **{model: f"{stage_b_predictions[model][i]:.17g}" for model in MODEL_ORDER},
                }
            )

    metric_lookup = {(r["stage"], r["model"]): r for r in metric_rows}
    fresh_ara = metric_lookup[("pooled_D_E_to_fresh_F", "ara_full")]
    fresh_parent = metric_lookup[("pooled_D_E_to_fresh_F", "parent_empirical")]
    fresh_raw = metric_lookup[("pooled_D_E_to_fresh_F", "raw_full")]
    fresh_scrambled = metric_lookup[("pooled_D_E_to_fresh_F", "ara_order_scrambled")]
    fresh_ara_compact = metric_lookup[("pooled_D_E_to_fresh_F", "ara_compact")]
    fresh_raw_compact = metric_lookup[("pooled_D_E_to_fresh_F", "raw_compact")]
    stage_a_ara = metric_lookup[("D_to_E", "ara_full")]
    stage_a_parent = metric_lookup[("D_to_E", "parent_empirical")]

    all_guards = [d.guards, e.guards, f.guards]
    p1 = bool(
        max(g["max_abs_a_plus_b_minus_2"] for g in all_guards) <= 1e-12
        and max(g["max_gate_minus_threshold"] for g in all_guards) <= 0.0
        and sum(g["zero_remainders"] for g in all_guards) == 0
    )
    p2_comparison = fresh_comparisons["ara_full_vs_parent_empirical"]
    p2 = bool(
        fresh_ara["log_loss_bits"] < fresh_parent["log_loss_bits"]
        and fresh_ara["auc"] > 0.5
        and p2_comparison["ci95_low"] > 0.0
    )
    p3 = bool(stage_a_ara["log_loss_bits"] < stage_a_parent["log_loss_bits"] and p2_comparison["gain_bits_per_event"] > 0.0)
    p4_comparison = fresh_comparisons["ara_full_vs_raw_full"]
    p4 = bool(fresh_ara["log_loss_bits"] < fresh_raw["log_loss_bits"] and p4_comparison["ci95_low"] > 0.0)
    p5_comparison = fresh_comparisons["ara_full_vs_ara_order_scrambled"]
    p5 = bool(fresh_ara["log_loss_bits"] < fresh_scrambled["log_loss_bits"] and p5_comparison["ci95_low"] > 0.0)
    p6 = bool(
        fresh_ara_compact["log_loss_bits"] < fresh_parent["log_loss_bits"]
        and fresh_ara_compact["log_loss_bits"] < fresh_raw_compact["log_loss_bits"]
    )

    if not p1:
        verdict = "INCONCLUSIVE"
    elif p2 and p3 and p4 and p5:
        verdict = "SUPPORTED"
    elif p2 and p3:
        verdict = "SUGGESTIVE"
    elif fresh_ara["log_loss_bits"] > fresh_parent["log_loss_bits"] and p2_comparison["ci95_high"] < 0.0:
        verdict = "NOT SUPPORTED"
    else:
        verdict = "NULL"

    calibration = calibration_rows(f.labels, stage_b_predictions["ara_full"])
    result = {
        "test_id": freeze["test_id"],
        "declared_date": freeze["declared_date"],
        "run_date": "2026-07-20",
        "protocol_sha256": freeze["protocol_sha256"],
        "source_sha256": freeze["source_sha256"],
        "parameters": {
            "parent_cutoff": 0.90,
            "child_gates": K,
            "l2": L2,
            "max_newton_steps": MAX_STEPS,
            "bootstrap_blocks": BOOTSTRAP_BLOCKS,
            "bootstrap_draws": BOOTSTRAP_DRAWS,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "buchstab_parent_probability": buchstab_parent_probability(),
        },
        "intervals": {
            item.name: {
                "range": intervals[item.name],
                "survivor_count": item.survivor_count,
                "prime_count": item.prime_count,
                "composite_count": item.composite_count,
                "prime_prevalence": item.prevalence,
                "guards": item.guards,
                "sample_rows": item.sample_rows,
            }
            for item in (d, e, f)
        },
        "stage_a_fit": stage_a_fit,
        "stage_b_fit": stage_b_fit,
        "metrics": metric_rows,
        "fresh_comparisons": fresh_comparisons,
        "fresh_ara_full_calibration": calibration,
        "criteria": {"P1": p1, "P2": p2, "P3": p3, "P4": p4, "P5": p5, "P6": p6},
        "verdict": verdict,
        "interpretation_boundary": (
            "All child features are deterministic functions of already-tested residues. A positive ranking result "
            "would establish useful organisation at the fixed gate budget, not new Shannon information or exact "
            "early primality."
        ),
        "protected_material": {"p31_primorial_wheel_constructed": False, "r12_opened": False},
        "runtime_seconds": time.time() - started,
    }
    RESULT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    make_figure(metric_rows, comparison_rows, calibration, result)
    print(json.dumps({"verdict": verdict, "criteria": result["criteria"], "runtime_seconds": result["runtime_seconds"]}, indent=2))


if __name__ == "__main__":
    main()
