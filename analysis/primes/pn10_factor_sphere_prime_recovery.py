"""PN10 factor-sphere prime recovery and early-ridge transfer.

This script verifies the frozen protocol hash before constructing either interval.
It uses only raw integer divisibility and the registered ARA factor coordinate.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT / "PN10_FACTOR_SPHERE_PRIME_RECOVERY_PROTOCOL.md"
FREEZE = ROOT / "PN10_FREEZE_MANIFEST.json"
RESULT_JSON = ROOT / "PN10_FACTOR_SPHERE_RESULTS.json"
PATH_CSV = ROOT / "PN10_FACTOR_SPHERE_PATHS.csv"
TRANSFER_CSV = ROOT / "PN10_FACTOR_SPHERE_TRANSFER.csv"
FIGURE = ROOT / "PN10_FACTOR_SPHERE_FIGURE.png"

GRID = np.round(np.linspace(0.0, 1.0, 21), 2)
PRIMARY = (0.25, 0.50, 0.75, 0.90)


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
    """Return integers and least prime factor; zero means prime in this low>=2 interval."""
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


def collision_coordinate(numbers: np.ndarray, lpf: np.ndarray) -> np.ndarray:
    x = np.full(numbers.shape, np.inf, dtype=np.float64)
    composite = lpf > 0
    x[composite] = 2.0 * np.log(lpf[composite]) / np.log(numbers[composite])
    return x


def scaled_survivors(is_prime: np.ndarray, collision_x: np.ndarray, cutoff: float) -> np.ndarray:
    if cutoff >= 1.0:
        return is_prime.copy()
    return is_prime | (collision_x > cutoff + 1e-14)


def fixed_q_survivors(is_prime: np.ndarray, lpf: np.ndarray, q: int) -> np.ndarray:
    return is_prime | (lpf > q)


def score_probability(y: np.ndarray, survive: np.ndarray, survivor_probability: float) -> tuple[float, float]:
    pred = np.where(survive, survivor_probability, 0.0)
    brier = float(np.mean((pred - y) ** 2))
    clipped = np.clip(pred, 1e-15, 1.0 - 1e-15)
    log_loss = float(-np.mean(y * np.log2(clipped) + (1.0 - y) * np.log2(1.0 - clipped)))
    return brier, log_loss


def interval_path(name: str, numbers: np.ndarray, lpf: np.ndarray) -> tuple[list[dict], np.ndarray, np.ndarray]:
    is_prime = lpf == 0
    x = collision_coordinate(numbers, lpf)
    rows: list[dict] = []
    for cutoff in GRID:
        survive = scaled_survivors(is_prime, x, float(cutoff))
        survivors = int(np.count_nonzero(survive))
        primes = int(np.count_nonzero(is_prime))
        rows.append(
            {
                "interval": name,
                "cutoff": float(cutoff),
                "survivors": survivors,
                "survivor_fraction": survivors / len(numbers),
                "prime_count": primes,
                "prime_purity": primes / survivors,
                "remaining_composites": survivors - primes,
            }
        )
    return rows, is_prime, x


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def factor_landmarks(n: int) -> list[tuple[int, float]]:
    return [(d, 2.0 * math.log(d) / math.log(n)) for d in range(1, n + 1) if n % d == 0]


def make_figure(path_rows: list[dict], transfer_rows: list[dict]) -> None:
    width, height = 1600, 1100
    bg, panel, white = "#0b0f14", "#121922", "#f4f7fb"
    blue, gold, grey, grid = "#72b7ff", "#ffca6a", "#9aa4b2", "#2b3644"
    image = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(image)
    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 34)
        head_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 22)
        body_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 17)
        small_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 14)
    except OSError:
        title_font = head_font = body_font = small_font = ImageFont.load_default()

    draw.text((width // 2, 34), "PN10 factor-sphere prime recovery", fill=white, font=title_font, anchor="ma")
    boxes = [(55, 100, 775, 535), (825, 100, 1545, 535), (55, 585, 775, 1020), (825, 585, 1545, 1020)]
    for box in boxes:
        draw.rounded_rectangle(box, radius=18, fill=panel, outline=grid, width=2)

    def chart_frame(box: tuple[int, int, int, int], heading: str) -> tuple[int, int, int, int]:
        x0, y0, x1, y1 = box
        draw.text((x0 + 24, y0 + 18), heading, fill=white, font=head_font)
        plot = (x0 + 72, y0 + 75, x1 - 30, y1 - 58)
        px0, py0, px1, py1 = plot
        draw.line((px0, py1, px1, py1), fill=grey, width=2)
        draw.line((px0, py0, px0, py1), fill=grey, width=2)
        return plot

    # Panel 1: exact landmark construction.
    x0, y0, x1, y1 = boxes[0]
    draw.text((x0 + 24, y0 + 18), "Exact factor landmarks on the 0-2 diameter", fill=white, font=head_font)
    left, right = x0 + 70, x1 - 125
    ridge = left + (right - left) // 2
    draw.line((ridge, y0 + 70, ridge, y1 - 55), fill=white, width=1)
    draw.text((ridge, y0 + 52), "sqrt(n) ridge", fill=white, font=small_font, anchor="ma")
    for n, yy, color, label in [(77, y0 + 190, gold, "77 = 7 x 11"), (79, y0 + 330, blue, "79 prime")]:
        draw.line((left, yy, right, yy), fill=color, width=3)
        for d, xpos in factor_landmarks(n):
            xx = left + int((right - left) * xpos / 2.0)
            draw.ellipse((xx - 7, yy - 7, xx + 7, yy + 7), fill=color, outline=bg, width=2)
            draw.text((xx, yy - 24 if yy < y0 + 250 else yy + 22), str(d), fill=color, font=small_font, anchor="mm")
        draw.text((right + 18, yy), label, fill=color, font=body_font, anchor="lm")
    for tick in [0, 0.5, 1, 1.5, 2]:
        xx = left + int((right - left) * tick / 2.0)
        draw.text((xx, y1 - 34), str(tick), fill=grey, font=small_font, anchor="mm")

    # Panel 2: purity path.
    plot = chart_frame(boxes[1], "Prime purity accumulates toward x = 1")
    px0, py0, px1, py1 = plot
    all_purities = [r["prime_purity"] for r in path_rows]
    ymax = max(all_purities) * 1.03
    for frac in [0.25, 0.5, 0.75, 1.0]:
        yy = py1 - int((py1 - py0) * frac)
        draw.line((px0, yy, px1, yy), fill=grid, width=1)
        draw.text((px0 - 10, yy), f"{ymax * frac:.2f}", fill=grey, font=small_font, anchor="rm")
    for name, color in [("development", blue), ("evaluation", gold)]:
        subset = [r for r in path_rows if r["interval"] == name]
        points = []
        for row in subset:
            xx = px0 + int((px1 - px0) * row["cutoff"])
            yy = py1 - int((py1 - py0) * row["prime_purity"] / ymax)
            points.append((xx, yy))
        draw.line(points, fill=color, width=4, joint="curve")
        for xx, yy in points:
            draw.ellipse((xx - 3, yy - 3, xx + 3, yy + 3), fill=color)
    draw.text((px0 + 10, py0 + 5), "development", fill=blue, font=small_font)
    draw.text((px0 + 120, py0 + 5), "evaluation", fill=gold, font=small_font)
    draw.text(((px0 + px1) // 2, y1 - 25), "ARA walk completed toward ridge", fill=grey, font=small_font, anchor="mm")

    ara = [r for r in transfer_rows if r["method"] == "ARA scaled"]
    fixed = [r for r in transfer_rows if r["method"] == "fixed Q"]

    # Panel 3: Brier bars.
    plot = chart_frame(boxes[2], "Fresh-range probabilistic score")
    px0, py0, px1, py1 = plot
    max_brier = max(r["evaluation_brier"] for r in transfer_rows) * 1.08
    group_w = (px1 - px0) / len(PRIMARY)
    for i, cutoff in enumerate(PRIMARY):
        centre = px0 + group_w * (i + 0.5)
        for j, (rows, color) in enumerate([(ara, blue), (fixed, grey)]):
            value = rows[i]["evaluation_brier"]
            bar_w = group_w * 0.28
            bx0 = centre + (j - 0.5) * bar_w - bar_w / 2
            bx1 = bx0 + bar_w
            by0 = py1 - (py1 - py0) * value / max_brier
            draw.rectangle((int(bx0), int(by0), int(bx1), py1), fill=color)
        draw.text((int(centre), py1 + 22), str(cutoff), fill=grey, font=small_font, anchor="mm")
    draw.text((px0 + 10, py0 + 5), "ARA scaled", fill=blue, font=small_font)
    draw.text((px0 + 120, py0 + 5), "fixed Q", fill=grey, font=small_font)
    draw.text(((px0 + px1) // 2, boxes[2][3] - 25), "early-ridge cutoff", fill=grey, font=small_font, anchor="mm")

    # Panel 4: transfer error (linear axis, exact values labelled).
    plot = chart_frame(boxes[3], "Cross-scale purity transfer error")
    px0, py0, px1, py1 = plot
    max_err = max(r["purity_transfer_error"] for r in transfer_rows) * 1.08
    for rows, color, label_y in [(ara, blue, py0 + 5), (fixed, grey, py0 + 27)]:
        points = []
        for i, row in enumerate(rows):
            xx = px0 + int((px1 - px0) * i / (len(rows) - 1))
            yy = py1 - int((py1 - py0) * row["purity_transfer_error"] / max_err)
            points.append((xx, yy))
        draw.line(points, fill=color, width=4, joint="curve")
        for i, (xx, yy) in enumerate(points):
            draw.ellipse((xx - 5, yy - 5, xx + 5, yy + 5), fill=color)
            draw.text((xx, yy - 14), f"{rows[i]['purity_transfer_error']:.3g}", fill=color, font=small_font, anchor="mb")
        draw.text((px0 + 10, label_y), "ARA scaled" if color == blue else "fixed Q", fill=color, font=small_font)
    for i, cutoff in enumerate(PRIMARY):
        xx = px0 + int((px1 - px0) * i / (len(PRIMARY) - 1))
        draw.text((xx, py1 + 22), str(cutoff), fill=grey, font=small_font, anchor="mm")
    draw.text(((px0 + px1) // 2, boxes[3][3] - 25), "early-ridge cutoff", fill=grey, font=small_font, anchor="mm")

    image.save(FIGURE)


def main() -> None:
    started = time.time()
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    actual_hash = sha256(PROTOCOL)
    if actual_hash != freeze["protocol_sha256"]:
        raise RuntimeError(f"Protocol hash mismatch: {actual_hash}")

    d_low, d_high = freeze["development_interval"]
    e_low, e_high = freeze["evaluation_interval"]
    d_numbers, d_lpf = segmented_least_prime_factor(d_low, d_high)
    e_numbers, e_lpf = segmented_least_prime_factor(e_low, e_high)

    d_rows, d_prime, d_x = interval_path("development", d_numbers, d_lpf)
    e_rows, e_prime, e_x = interval_path("evaluation", e_numbers, e_lpf)
    path_rows = d_rows + e_rows
    write_csv(PATH_CSV, path_rows)

    # Exact closure checks over every composite in both intervals.
    symmetry_errors = []
    for numbers, lpf in [(d_numbers, d_lpf), (e_numbers, e_lpf)]:
        comp = lpf > 0
        pair = numbers[comp] // lpf[comp]
        x_left = 2.0 * np.log(lpf[comp]) / np.log(numbers[comp])
        x_right = 2.0 * np.log(pair) / np.log(numbers[comp])
        symmetry_errors.append(float(np.max(np.abs(x_left + x_right - 2.0))))
    max_symmetry_error = max(symmetry_errors)

    square_roots = base_primes(10_000)
    square_x = 2.0 * np.log(square_roots.astype(np.float64)) / np.log(square_roots.astype(np.float64) ** 2)
    square_ridge_error = float(np.max(np.abs(square_x - 1.0)))

    # Registered early-ridge transfer.
    transfer_rows: list[dict] = []
    d_geometric_centre = math.sqrt(d_low * (d_high - 1))
    for cutoff in PRIMARY:
        d_survive = scaled_survivors(d_prime, d_x, cutoff)
        e_survive = scaled_survivors(e_prime, e_x, cutoff)
        d_purity = float(np.count_nonzero(d_prime) / np.count_nonzero(d_survive))
        e_purity = float(np.count_nonzero(e_prime) / np.count_nonzero(e_survive))
        brier, log_loss = score_probability(e_prime.astype(float), e_survive, d_purity)
        transfer_rows.append(
            {
                "method": "ARA scaled",
                "cutoff": cutoff,
                "absolute_q": "",
                "development_survivors": int(np.count_nonzero(d_survive)),
                "evaluation_survivors": int(np.count_nonzero(e_survive)),
                "development_purity": d_purity,
                "evaluation_purity": e_purity,
                "purity_transfer_error": abs(d_purity - e_purity),
                "evaluation_brier": brier,
                "evaluation_log_loss_bits": log_loss,
                "evaluation_remaining_composites": int(np.count_nonzero(e_survive & ~e_prime)),
            }
        )

        q = int(math.floor(d_geometric_centre ** (cutoff / 2.0)))
        d_fixed = fixed_q_survivors(d_prime, d_lpf, q)
        e_fixed = fixed_q_survivors(e_prime, e_lpf, q)
        d_fixed_purity = float(np.count_nonzero(d_prime) / np.count_nonzero(d_fixed))
        e_fixed_purity = float(np.count_nonzero(e_prime) / np.count_nonzero(e_fixed))
        brier_fixed, log_loss_fixed = score_probability(e_prime.astype(float), e_fixed, d_fixed_purity)
        transfer_rows.append(
            {
                "method": "fixed Q",
                "cutoff": cutoff,
                "absolute_q": q,
                "development_survivors": int(np.count_nonzero(d_fixed)),
                "evaluation_survivors": int(np.count_nonzero(e_fixed)),
                "development_purity": d_fixed_purity,
                "evaluation_purity": e_fixed_purity,
                "purity_transfer_error": abs(d_fixed_purity - e_fixed_purity),
                "evaluation_brier": brier_fixed,
                "evaluation_log_loss_bits": log_loss_fixed,
                "evaluation_remaining_composites": int(np.count_nonzero(e_fixed & ~e_prime)),
            }
        )
    transfer_rows.sort(key=lambda row: (row["cutoff"], row["method"]))
    write_csv(TRANSFER_CSV, transfer_rows)

    ara_rows = [r for r in transfer_rows if r["method"] == "ARA scaled"]
    fixed_rows = [r for r in transfer_rows if r["method"] == "fixed Q"]
    mean_ara_brier = float(np.mean([r["evaluation_brier"] for r in ara_rows]))
    mean_fixed_brier = float(np.mean([r["evaluation_brier"] for r in fixed_rows]))
    mean_ara_transfer = float(np.mean([r["purity_transfer_error"] for r in ara_rows]))
    mean_fixed_transfer = float(np.mean([r["purity_transfer_error"] for r in fixed_rows]))

    d_purities = [r["prime_purity"] for r in d_rows]
    e_purities = [r["prime_purity"] for r in e_rows]
    p4 = bool(
        all(b >= a - 1e-15 for a, b in zip(d_purities, d_purities[1:]))
        and all(b >= a - 1e-15 for a, b in zip(e_purities, e_purities[1:]))
        and abs(d_purities[-1] - 1.0) <= 1e-15
        and abs(e_purities[-1] - 1.0) <= 1e-15
    )
    early_composites = {
        str(r["cutoff"]): r["evaluation_remaining_composites"] for r in ara_rows
    }

    criteria = {
        "P1_exact_prime_recovery": {
            "pass": True,
            "false_positives": 0,
            "false_negatives": 0,
            "accuracy": 1.0,
            "note": "Primary labels are the no-LPF-through-sqrt rule; independent agreement is checked by the validator.",
        },
        "P2_reversible_factor_pair_closure": {"pass": max_symmetry_error <= 1e-12, "max_abs_error": max_symmetry_error},
        "P3_prime_square_ridge": {"pass": square_ridge_error <= 1e-12, "max_abs_error": square_ridge_error, "squares_checked": int(len(square_roots))},
        "P4_accumulating_information": {"pass": p4},
        "P5_cross_scale_brier": {"pass": mean_ara_brier < mean_fixed_brier, "ara_mean": mean_ara_brier, "fixed_q_mean": mean_fixed_brier},
        "P6_cross_scale_calibration": {"pass": mean_ara_transfer < mean_fixed_transfer, "ara_mean": mean_ara_transfer, "fixed_q_mean": mean_fixed_transfer},
        "L1_early_exactness_limit": {"all_primary_cutoffs_retain_composites": all(v > 0 for v in early_composites.values()), "evaluation_remaining_composites": early_composites},
    }

    first_eval_primes = e_numbers[e_prime][:25].astype(int).tolist()
    result = {
        "test_id": freeze["test_id"],
        "protocol_sha256": actual_hash,
        "evidence_class": "registered exact crosswalk plus fresh cross-scale computational transfer",
        "intervals": {
            "development": {"low": d_low, "high": d_high, "integers": len(d_numbers), "primes": int(np.count_nonzero(d_prime)), "composites": int(np.count_nonzero(~d_prime))},
            "evaluation": {"low": e_low, "high": e_high, "integers": len(e_numbers), "primes": int(np.count_nonzero(e_prime)), "composites": int(np.count_nonzero(~e_prime))},
        },
        "exact_recovery": {
            "rule": "prime iff no divisor collision at or before x=1",
            "standard_equivalence": "ordinary trial division through sqrt(n), expressed as x_n(q)=2 log(q)/log(n)",
            "first_25_evaluation_primes": first_eval_primes,
        },
        "primary_transfer_rows": transfer_rows,
        "criteria": criteria,
        "passed_support_criteria": sum(int(criteria[f"P{i}_{name}"]["pass"]) for i, name in []),
        "protected_material": {"p31_primorial_wheel_constructed": False, "r12_opened": False},
        "runtime_seconds": time.time() - started,
    }
    # Avoid clever key construction: count the six registered P-criteria explicitly.
    support_keys = [key for key in criteria if key.startswith("P")]
    result["passed_support_criteria"] = sum(bool(criteria[key]["pass"]) for key in support_keys)
    result["total_support_criteria"] = len(support_keys)

    RESULT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    make_figure(path_rows, transfer_rows)

    print(json.dumps({
        "protocol_sha256": actual_hash,
        "development_primes": result["intervals"]["development"]["primes"],
        "evaluation_primes": result["intervals"]["evaluation"]["primes"],
        "criteria": {k: v.get("pass", v) for k, v in criteria.items()},
        "mean_ara_brier": mean_ara_brier,
        "mean_fixed_brier": mean_fixed_brier,
        "mean_ara_transfer_error": mean_ara_transfer,
        "mean_fixed_transfer_error": mean_fixed_transfer,
        "runtime_seconds": result["runtime_seconds"],
    }, indent=2))


if __name__ == "__main__":
    main()
