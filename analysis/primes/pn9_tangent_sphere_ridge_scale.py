"""Run PN9: tangent-sphere ridge balance plus logarithmic sphere scale.

The protocol was frozen before this script was executed.  R12 and the p31
primorial wheel are intentionally untouched.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN9_TANGENT_SPHERE_RIDGE_SCALE_PROTOCOL.md"
DEVELOPMENT = HERE / "PN7C_DEVELOPMENT_GAPS.npz"
TARGET = HERE / "PN7C_R11_TARGET_GAPS.npz"

EXPECTED = {
    PROTOCOL.name: "EF0E28DCC5F447D5F13D0DC3DFAFFD91286A34E39BCC8277E711C34A88475C27",
    DEVELOPMENT.name: "A791D771481523E8331EC241C2F762A1700526F32F663238C1A767D810E67230",
    TARGET.name: "D60EEDFA2F3A5DF4C8FA45B45D2B478EDB39B6D54001302F84041989C8D0CF2F",
}

OUT_JSON = HERE / "PN9_TANGENT_SPHERE_RIDGE_SCALE_RESULTS.json"
OUT_SCORES = HERE / "PN9_TANGENT_SPHERE_RIDGE_SCALE_SCORES.csv"
OUT_BLOCKS = HERE / "PN9_TANGENT_SPHERE_RIDGE_SCALE_BLOCKS.csv"
OUT_CONTROLS = HERE / "PN9_TANGENT_SPHERE_RIDGE_SCALE_CONTROLS.csv"
OUT_DISTRIBUTIONS = HERE / "PN9_TANGENT_SPHERE_RIDGE_SCALE_DISTRIBUTIONS.csv"
OUT_FIGURE = HERE / "PN9_TANGENT_SPHERE_RIDGE_SCALE_FIGURE.png"

BINS_SET = (12, 24, 48)
PRIMARY_BINS = 24
ALPHA = 0.5
RAW_LAMBDA = 64.0
RAW_ALPHABET = 1025
CHUNK = 500_000
SHUFFLE_SEEDS = tuple(range(2026071941, 2026071946))
BOOTSTRAP_SEED = 2026071949
BOOTSTRAP_DRAWS = 10_000

RUNG_META = {
    "R9": {"first": 1_000_000_007, "low": 1_000_000_000, "high": 1_010_000_000},
    "R10": {"first": 10_000_000_019, "low": 10_000_000_000, "high": 10_100_000_000},
    "R11": {"first": 100_000_000_003, "low": 100_000_000_000, "high": 101_000_000_000},
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest().upper()


def is_prime_64(n: int) -> bool:
    if n < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in small:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


def validate_rung(name: str, gaps: np.ndarray) -> dict:
    meta = RUNG_META[name]
    first = meta["first"]
    last = first + int(gaps.astype(np.uint64).sum())
    earlier = [n for n in range(meta["low"] + 1, first) if is_prime_64(n)]
    later = [n for n in range(last + 1, meta["high"]) if is_prime_64(n)]
    if not is_prime_64(first) or earlier:
        raise AssertionError(f"{name} first-prime reconciliation failed")
    if not is_prime_64(last) or later:
        raise AssertionError(f"{name} last-prime reconciliation failed")
    if int(gaps.max()) >= RAW_ALPHABET:
        raise AssertionError(f"{name} exceeds frozen raw-gap alphabet")
    return {
        "interval": [meta["low"], meta["high"]],
        "first_prime": first,
        "last_prime": last,
        "prime_count": int(len(gaps) + 1),
        "gap_count": int(len(gaps)),
        "gap_sum": int(gaps.astype(np.uint64).sum()),
        "max_gap": int(gaps.max()),
        "boundary_reconciled": True,
    }


def states_from_gaps(
    gaps: np.ndarray,
    first_prime: int,
    bins: int,
    home_gaps: np.ndarray | None = None,
    diagnostics: bool = False,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """Return binned x/y states; home_gaps fixes positions for shuffle controls."""
    if home_gaps is None:
        home_gaps = gaps
    n = len(gaps) - 1
    x_state = np.empty(n, dtype=np.uint8)
    y_state = np.empty(n, dtype=np.uint8)
    cumulative_home = 0
    stats = {
        "x_min": math.inf,
        "x_max": -math.inf,
        "y_min": math.inf,
        "y_max": -math.inf,
        "x_sum": 0.0,
        "y_sum": 0.0,
        "max_gap_reconstruction_error": 0.0,
        "max_tangency_error": 0.0,
        "states": n,
    }
    for start in range(0, n, CHUNK):
        stop = min(n, start + CHUNK)
        left = gaps[start:stop].astype(np.float64)
        right = gaps[start + 1:stop + 1].astype(np.float64)
        total = left + right
        local_scale = total / 2.0

        home_left = home_gaps[start:stop].astype(np.int64)
        node_position = first_prime + cumulative_home + np.cumsum(home_left, dtype=np.int64)
        cumulative_home += int(home_left.sum(dtype=np.int64))
        home = np.log(node_position.astype(np.float64))

        x = 2.0 * right / total
        y = 2.0 * local_scale / (local_scale + home)
        x_state[start:stop] = np.minimum((bins * right.astype(np.uint32)) // total.astype(np.uint32), bins - 1)
        # y/2 = L/(L+h); this keeps the fixed equal-bin [0,2] map.
        y_state[start:stop] = np.minimum(
            np.floor(bins * local_scale / (local_scale + home)).astype(np.int64), bins - 1
        ).astype(np.uint8)

        if diagnostics:
            recovered_scale = home * y / (2.0 - y)
            recovered_right = x * recovered_scale
            recovered_left = (2.0 - x) * recovered_scale
            error = max(
                float(np.max(np.abs(recovered_left - left))),
                float(np.max(np.abs(recovered_right - right))),
            )
            stats["max_gap_reconstruction_error"] = max(stats["max_gap_reconstruction_error"], error)
            stats["x_min"] = min(stats["x_min"], float(x.min()))
            stats["x_max"] = max(stats["x_max"], float(x.max()))
            stats["y_min"] = min(stats["y_min"], float(y.min()))
            stats["y_max"] = max(stats["y_max"], float(y.max()))
            stats["x_sum"] += float(x.sum())
            stats["y_sum"] += float(y.sum())

    if diagnostics:
        stats["x_mean"] = stats.pop("x_sum") / n
        stats["y_mean"] = stats.pop("y_sum") / n
    else:
        stats = {}
    return x_state, y_state, stats


def add_state_counts(x: np.ndarray, y: np.ndarray, bins: int, x2: np.ndarray, xy: np.ndarray) -> None:
    events = len(x) - 2
    for start in range(0, events, CHUNK):
        stop = min(events, start + CHUNK)
        previous = x[start:stop].astype(np.int64)
        current = x[start + 1:stop + 1].astype(np.int64)
        scale = y[start + 1:stop + 1].astype(np.int64)
        target = x[start + 2:stop + 2].astype(np.int64)
        code_x = (previous * bins + current) * bins + target
        code_xy = ((previous * bins + current) * bins + scale) * bins + target
        x2 += np.bincount(code_x, minlength=bins ** 3).reshape(x2.shape)
        xy += np.bincount(code_xy, minlength=bins ** 4).reshape(xy.shape)


def add_raw_counts(gaps: np.ndarray, marginal: np.ndarray, transition: np.ndarray) -> None:
    marginal += np.bincount(gaps.astype(np.int64), minlength=RAW_ALPHABET)
    for start in range(0, len(gaps) - 1, CHUNK):
        stop = min(len(gaps) - 1, start + CHUNK)
        code = gaps[start:stop].astype(np.int64) * RAW_ALPHABET + gaps[start + 1:stop + 1].astype(np.int64)
        transition += np.bincount(code, minlength=RAW_ALPHABET ** 2).reshape(transition.shape)


def fit_models(rungs: list[tuple[np.ndarray, np.ndarray, np.ndarray]], bins: int) -> dict:
    x2 = np.zeros((bins, bins, bins), dtype=np.int64)
    xy = np.zeros((bins, bins, bins, bins), dtype=np.int64)
    marginal = np.zeros(RAW_ALPHABET, dtype=np.int64)
    transition = np.zeros((RAW_ALPHABET, RAW_ALPHABET), dtype=np.int64)
    for gaps, x, y in rungs:
        add_state_counts(x, y, bins, x2, xy)
        add_raw_counts(gaps, marginal, transition)

    x2_p = (x2 + ALPHA) / (x2.sum(axis=2, keepdims=True) + ALPHA * bins)
    xy_p = (xy + ALPHA) / (xy.sum(axis=3, keepdims=True) + ALPHA * bins)

    marginal_p = np.zeros(RAW_ALPHABET, dtype=np.float64)
    marginal_p[1:] = (marginal[1:] + ALPHA) / (marginal[1:].sum() + ALPHA * (RAW_ALPHABET - 1))
    row_sum = transition.sum(axis=1, keepdims=True)
    raw_p = (transition + RAW_LAMBDA * marginal_p[None, :]) / (row_sum + RAW_LAMBDA)
    raw_p[row_sum[:, 0] == 0] = marginal_p
    raw_p[:, 0] = 0.0
    raw_p /= raw_p.sum(axis=1, keepdims=True)
    return {"x2": x2_p, "xy": xy_p, "raw": raw_p}


def raw_projection(raw_p: np.ndarray, bins: int) -> np.ndarray:
    projection = np.zeros((RAW_ALPHABET, bins), dtype=np.float64)
    nxt = np.arange(RAW_ALPHABET, dtype=np.int64)
    for current in range(1, RAW_ALPHABET):
        denominator = current + nxt
        mapped = np.zeros(RAW_ALPHABET, dtype=np.int64)
        valid = denominator > 0
        mapped[valid] = np.minimum((bins * nxt[valid]) // denominator[valid], bins - 1)
        projection[current] = np.bincount(mapped, weights=raw_p[current], minlength=bins)
    projection[0] = projection[1]
    return projection


def helpers(prob: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return np.sum(prob * prob, axis=-1), np.argmax(prob, axis=-1), np.argpartition(prob, -3, axis=-1)[..., -3:]


def score_models(
    gaps: np.ndarray,
    x: np.ndarray,
    y: np.ndarray,
    model: dict,
    bins: int,
    blocks: bool = False,
) -> tuple[dict, np.ndarray | None]:
    raw_p = raw_projection(model["raw"], bins)
    probs = {"X-M2": model["x2"], "XY-M2": model["xy"], "RawGap-M1": raw_p}
    aux = {name: helpers(p) for name, p in probs.items()}
    totals = {name: {"ll": 0.0, "brier": 0.0, "top1": 0, "top3": 0} for name in probs}
    events = len(x) - 2
    block_sum = np.zeros(100, dtype=np.float64) if blocks else None
    block_count = np.zeros(100, dtype=np.int64) if blocks else None

    for start in range(0, events, CHUNK):
        stop = min(events, start + CHUNK)
        previous = x[start:stop].astype(np.int64)
        current = x[start + 1:stop + 1].astype(np.int64)
        scale = y[start + 1:stop + 1].astype(np.int64)
        target = x[start + 2:stop + 2].astype(np.int64)
        shared_gap = gaps[start + 2:stop + 2].astype(np.int64)
        rows = {
            "X-M2": (previous, current),
            "XY-M2": (previous, current, scale),
            "RawGap-M1": shared_gap,
        }
        p_target = {
            "X-M2": probs["X-M2"][previous, current, target],
            "XY-M2": probs["XY-M2"][previous, current, scale, target],
            "RawGap-M1": probs["RawGap-M1"][shared_gap, target],
        }
        for name in probs:
            p = p_target[name]
            square, top1, top3 = aux[name]
            row = rows[name]
            row_square = square[row]
            pred1 = top1[row]
            pred3 = top3[row]
            totals[name]["ll"] += float(np.sum(-np.log2(p)))
            totals[name]["brier"] += float(np.sum(1.0 + row_square - 2.0 * p))
            totals[name]["top1"] += int(np.count_nonzero(pred1 == target))
            totals[name]["top3"] += int(np.count_nonzero(np.any(pred3 == target[:, None], axis=1)))

        if blocks:
            gain = np.log2(p_target["XY-M2"] / p_target["X-M2"])
            index = np.arange(start, stop, dtype=np.int64)
            block = np.minimum((100 * index) // events, 99)
            block_sum += np.bincount(block, weights=gain, minlength=100)
            block_count += np.bincount(block, minlength=100)

    result = {}
    for name, values in totals.items():
        ce = values["ll"] / events
        result[name] = {
            "events": events,
            "cross_entropy_bits": ce,
            "brier_score": values["brier"] / events,
            "top1_accuracy": values["top1"] / events,
            "top3_accuracy": values["top3"] / events,
            "perplexity": 2.0 ** ce,
        }
    return result, None if not blocks else block_sum / block_count


def conditional_entropy(joint: np.ndarray) -> float:
    rows = joint.reshape(-1, joint.shape[-1]).astype(np.float64)
    totals = rows.sum(axis=1)
    rows = rows[totals > 0]
    totals = totals[totals > 0]
    p = rows / totals[:, None]
    terms = np.zeros_like(p)
    positive = p > 0
    terms[positive] = p[positive] * np.log2(p[positive])
    return float(-np.sum(totals * terms.sum(axis=1)) / totals.sum())


def empirical_scale_information(x: np.ndarray, y: np.ndarray, bins: int) -> dict:
    x2 = np.zeros((bins, bins, bins), dtype=np.int64)
    xy = np.zeros((bins, bins, bins, bins), dtype=np.int64)
    add_state_counts(x, y, bins, x2, xy)
    h_x = conditional_entropy(x2)
    h_xy = conditional_entropy(xy)
    return {
        "events": int(x2.sum()),
        "h_next_given_previous_current_bits": h_x,
        "h_next_given_previous_current_scale_bits": h_xy,
        "conditional_scale_information_bits": h_x - h_xy,
    }


def js_divergence(count_a: np.ndarray, count_b: np.ndarray) -> float:
    p = count_a.astype(np.float64) / count_a.sum()
    q = count_b.astype(np.float64) / count_b.sum()
    m = (p + q) / 2.0
    kl_p = np.sum(p[p > 0] * np.log2(p[p > 0] / m[p > 0]))
    kl_q = np.sum(q[q > 0] * np.log2(q[q > 0] / m[q > 0]))
    return float((kl_p + kl_q) / 2.0)


def bootstrap_blocks(gains: np.ndarray) -> dict:
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    means = np.empty(BOOTSTRAP_DRAWS, dtype=np.float64)
    for start in range(0, BOOTSTRAP_DRAWS, 1000):
        stop = min(BOOTSTRAP_DRAWS, start + 1000)
        choices = rng.integers(0, len(gains), size=(stop - start, len(gains)))
        means[start:stop] = gains[choices].mean(axis=1)
    low, high = np.percentile(means, (2.5, 97.5))
    return {
        "seed": BOOTSTRAP_SEED,
        "draws": BOOTSTRAP_DRAWS,
        "positive_blocks": int(np.count_nonzero(gains > 0)),
        "mean_gain_bits": float(gains.mean()),
        "bootstrap_95_percentile_interval_bits": [float(low), float(high)],
    }


def get_font(size: int, bold: bool = False):
    path = Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def draw_figure(distributions: dict, scores: dict, blocks: np.ndarray, criteria: dict) -> None:
    image = Image.new("RGB", (1600, 1040), "#F7F4EE")
    draw = ImageDraw.Draw(image)
    ink, muted, blue, gold, orange, pale = "#20262B", "#687078", "#28658A", "#C39A32", "#C96E3B", "#E4E0D8"
    draw.text((62, 40), "PN9 tangent-sphere ridge and scale", fill=ink, font=get_font(38, True))
    draw.text((62, 92), "Actual-prime gaps; R9/R10 development and already-opened R11 transfer", fill=muted, font=get_font(21))

    # Distribution panel: the adult scale coordinate on its native 0-2 line.
    x0, y0, w, h = 80, 200, 680, 300
    draw.text((x0, y0 - 48), "Adult scale coordinate y", fill=ink, font=get_font(24, True))
    draw.text((x0, y0 - 18), "Share of internal prime nodes in each fixed 0–2 bin", fill=muted, font=get_font(17))
    colors = {"R9": blue, "R10": gold, "R11": orange}
    max_y = max(float(np.max(v)) for v in distributions.values()) * 1.08
    for name, values in distributions.items():
        points = []
        for i, value in enumerate(values):
            px = x0 + int(i / (len(values) - 1) * w)
            py = y0 + h - int(float(value) / max_y * h)
            points.append((px, py))
        draw.line(points, fill=colors[name], width=4)
        draw.text((x0 + w - 120, y0 + 18 + 30 * list(distributions).index(name)), name, fill=colors[name], font=get_font(18, True))
    draw.line((x0, y0 + h, x0 + w, y0 + h), fill=ink, width=2)
    draw.line((x0 + w // 2, y0, x0 + w // 2, y0 + h), fill="#9AA0A4", width=2)
    draw.text((x0 - 8, y0 + h + 12), "0", fill=muted, font=get_font(16))
    draw.text((x0 + w // 2 - 8, y0 + h + 12), "1", fill=muted, font=get_font(16))
    draw.text((x0 + w - 8, y0 + h + 12), "2", fill=muted, font=get_font(16))

    # CE comparison.
    bx, by, bw = 880, 200, 560
    draw.text((bx, by - 48), "R11 next-ridge prediction", fill=ink, font=get_font(24, True))
    draw.text((bx, by - 18), "24-bin cross-entropy; lower is better", fill=muted, font=get_font(17))
    primary = scores["R11"][str(PRIMARY_BINS)]
    names = ("X-M2", "XY-M2", "RawGap-M1")
    values = [primary[n]["cross_entropy_bits"] for n in names]
    floor = min(values) - 0.03
    ceiling = max(values) + 0.03
    for i, (name, value, color) in enumerate(zip(names, values, (blue, orange, gold))):
        yy = by + i * 88
        draw.text((bx, yy + 14), name, fill=ink, font=get_font(20, name == "XY-M2"))
        length = int((value - floor) / (ceiling - floor) * 330)
        draw.rectangle((bx + 150, yy + 10, bx + 150 + max(length, 3), yy + 48), fill=color)
        draw.text((bx + 495, yy + 14), f"{value:.5f}", fill=ink, font=get_font(18))

    # R11 blocks.
    px, py, pw, ph = 80, 650, 1000, 250
    draw.text((px, py - 52), "Scale-coordinate gain across R11", fill=ink, font=get_font(24, True))
    draw.text((px, py - 22), "100 contiguous blocks; positive means XY-M2 improves on X-M2", fill=muted, font=get_font(17))
    maximum = max(float(np.max(np.abs(blocks))), 1e-9)
    mid = py + ph // 2
    draw.line((px, mid, px + pw, mid), fill="#858B90", width=2)
    for i, value in enumerate(blocks):
        left = px + int(i * pw / 100)
        top = mid - int(float(value) / maximum * (ph * 0.44))
        draw.rectangle((left, min(top, mid), left + 7, max(top, mid)), fill=blue if value >= 0 else orange)

    # Criteria summary.
    cx, cy = 1180, 610
    draw.rounded_rectangle((cx, cy, 1515, 935), radius=18, fill=pale, outline="#C4BFB5", width=2)
    draw.text((cx + 24, cy + 22), "Registered gates", fill=ink, font=get_font(22, True))
    for i in range(1, 8):
        passed = criteria[f"P{i}"]["passed"]
        draw.text((cx + 26, cy + 66 + (i - 1) * 32), f"P{i}", fill=ink, font=get_font(18, True))
        draw.text((cx + 82, cy + 66 + (i - 1) * 32), "PASS" if passed else "FAIL", fill=blue if passed else orange, font=get_font(18, True))
    core = all(criteria[f"P{i}"]["passed"] for i in range(1, 6))
    draw.line((cx + 24, cy + 294, cx + 307, cy + 294), fill="#B9B3A9", width=2)
    draw.text((cx + 24, cy + 301), f"Core P1–P5: {'PASS' if core else 'FAIL'}", fill=blue if core else orange, font=get_font(17, True))
    image.save(OUT_FIGURE)


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    source_paths = (PROTOCOL, DEVELOPMENT, TARGET)
    actual_hashes = {path.name: sha256(path) for path in source_paths}
    if actual_hashes != EXPECTED:
        raise AssertionError(f"Source hash mismatch: {actual_hashes}")

    with np.load(DEVELOPMENT) as data:
        gaps = {
            "R9": data["r9__gaps"].astype(np.uint16),
            "R10": data["r10__gaps"].astype(np.uint16),
        }
    with np.load(TARGET) as data:
        gaps["R11"] = data["r11__gaps"].astype(np.uint16)
    reconciliations = {name: validate_rung(name, value) for name, value in gaps.items()}

    scores: dict[str, dict] = {"R10": {}, "R11": {}}
    gains: dict[str, dict] = {"R10": {}, "R11": {}}
    primary_states: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    diagnostics: dict[str, dict] = {}
    primary_models: dict[str, dict] = {}
    r11_blocks = None

    for bins in BINS_SET:
        states = {}
        for name in ("R9", "R10", "R11"):
            x, y, diag = states_from_gaps(
                gaps[name], RUNG_META[name]["first"], bins, diagnostics=(bins == PRIMARY_BINS)
            )
            states[name] = (x, y)
            if bins == PRIMARY_BINS:
                primary_states[name] = (x, y)
                diagnostics[name] = diag

        model_r9 = fit_models([(gaps["R9"], *states["R9"])], bins)
        model_r9r10 = fit_models(
            [(gaps["R9"], *states["R9"]), (gaps["R10"], *states["R10"])], bins
        )
        score_r10, _ = score_models(gaps["R10"], *states["R10"], model_r9, bins)
        score_r11, blocks = score_models(
            gaps["R11"], *states["R11"], model_r9r10, bins, blocks=(bins == PRIMARY_BINS)
        )
        scores["R10"][str(bins)] = score_r10
        scores["R11"][str(bins)] = score_r11
        gains["R10"][str(bins)] = score_r10["X-M2"]["cross_entropy_bits"] - score_r10["XY-M2"]["cross_entropy_bits"]
        gains["R11"][str(bins)] = score_r11["X-M2"]["cross_entropy_bits"] - score_r11["XY-M2"]["cross_entropy_bits"]
        if bins == PRIMARY_BINS:
            r11_blocks = blocks
            primary_models = {"R9": model_r9, "R9+R10": model_r9r10}

    del primary_models
    distributions = {}
    distribution_counts = {}
    for name, (_, y) in primary_states.items():
        count = np.bincount(y.astype(np.int64), minlength=PRIMARY_BINS)
        distribution_counts[name] = count
        distributions[name] = count.astype(np.float64) / count.sum()
    js = {
        "R9_R10_bits": js_divergence(distribution_counts["R9"], distribution_counts["R10"]),
        "R10_R11_bits": js_divergence(distribution_counts["R10"], distribution_counts["R11"]),
    }

    observed_info = empirical_scale_information(*primary_states["R11"], PRIMARY_BINS)
    controls = [{"label": "Observed R11", "seed": None, **observed_info}]
    for seed in SHUFFLE_SEEDS:
        rng = np.random.default_rng(seed)
        shuffled = gaps["R11"].copy()
        rng.shuffle(shuffled)
        sx, sy, _ = states_from_gaps(
            shuffled,
            RUNG_META["R11"]["first"],
            PRIMARY_BINS,
            home_gaps=gaps["R11"],
        )
        info = empirical_scale_information(sx, sy, PRIMARY_BINS)
        controls.append({"label": f"Shuffle {seed}", "seed": seed, **info})
        del shuffled, sx, sy

    block_summary = bootstrap_blocks(r11_blocks)
    shuffle_max = max(row["conditional_scale_information_bits"] for row in controls[1:])
    primary_r11 = scores["R11"][str(PRIMARY_BINS)]
    criteria = {
        "P1": {
            "passed": gains["R11"][str(PRIMARY_BINS)] >= 0.010,
            "value_bits": gains["R11"][str(PRIMARY_BINS)],
            "threshold_bits": 0.010,
        },
        "P2": {
            "passed": gains["R10"][str(PRIMARY_BINS)] > 0 and gains["R11"][str(PRIMARY_BINS)] > 0,
            "R10_gain_bits": gains["R10"][str(PRIMARY_BINS)],
            "R11_gain_bits": gains["R11"][str(PRIMARY_BINS)],
        },
        "P3": {
            "passed": all(gains["R11"][str(b)] > 0 for b in BINS_SET),
            "R11_gains_bits": {str(b): gains["R11"][str(b)] for b in BINS_SET},
        },
        "P4": {
            "passed": block_summary["positive_blocks"] >= 80
            and block_summary["bootstrap_95_percentile_interval_bits"][0] > 0,
            **block_summary,
        },
        "P5": {
            "passed": js["R9_R10_bits"] <= 0.005 and js["R10_R11_bits"] <= 0.005,
            **js,
            "threshold_bits": 0.005,
        },
        "P6": {
            "passed": observed_info["conditional_scale_information_bits"] - shuffle_max >= 0.010,
            "observed_bits": observed_info["conditional_scale_information_bits"],
            "maximum_shuffle_bits": shuffle_max,
            "residual_bits": observed_info["conditional_scale_information_bits"] - shuffle_max,
            "threshold_bits": 0.010,
        },
        "P7": {
            "passed": primary_r11["XY-M2"]["cross_entropy_bits"] < primary_r11["RawGap-M1"]["cross_entropy_bits"],
            "XY_M2_cross_entropy_bits": primary_r11["XY-M2"]["cross_entropy_bits"],
            "RawGap_M1_cross_entropy_bits": primary_r11["RawGap-M1"]["cross_entropy_bits"],
        },
    }
    core_pass = all(criteria[f"P{i}"]["passed"] for i in range(1, 6))

    result = {
        "test_id": "PN9/TANGENT-SPHERE-RIDGE-SCALE/OPENED-R9-R11-v1",
        "declared_date": "2026-07-19",
        "evidence_class": "registered retrospective transfer/structural test on already-opened actual-prime gaps",
        "protected_material": {"R12_opened": False, "p31_wheel_constructed": False},
        "hashes_verified": actual_hashes,
        "rungs": reconciliations,
        "coordinate_definition": {
            "x": "2*g_out/(g_in+g_out)",
            "L": "(g_in+g_out)/2",
            "home": "ln(p_i)",
            "y": "2*L/(L+ln(p_i))",
            "unbinned_inverse": "L=ln(p_i)*y/(2-y); g_out=x*L; g_in=(2-x)*L",
        },
        "coordinate_diagnostics": diagnostics,
        "scores": scores,
        "cross_entropy_gains_bits": gains,
        "scale_distribution_js": js,
        "conditional_scale_information_controls": controls,
        "block_summary": block_summary,
        "criteria": criteria,
        "ridge_plus_scale_core_P1_P5": "PASS" if core_pass else "FAIL",
        "allowed_interpretation": (
            "On already-opened R9-R11 actual-prime gaps, the native ARA factorisation into tangent-ridge balance "
            "and logarithmic sphere scale recurs across the tested rungs, and the scale coordinate improves "
            "out-of-rung prediction of the next relative gap state."
            if core_pass
            else "The registered ridge-plus-scale transfer core did not fully pass."
        ),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    score_rows = []
    for target_name, by_bins in scores.items():
        for bins, by_model in by_bins.items():
            for model_name, values in by_model.items():
                score_rows.append({"target": target_name, "bins": bins, "model": model_name, **values})
    write_csv(OUT_SCORES, score_rows)
    write_csv(
        OUT_BLOCKS,
        [{"block": i + 1, "X_M2_minus_XY_M2_cross_entropy_gain_bits": float(value)} for i, value in enumerate(r11_blocks)],
    )
    write_csv(OUT_CONTROLS, controls)
    distribution_rows = []
    for i in range(PRIMARY_BINS):
        distribution_rows.append(
            {
                "bin": i,
                "ara_low": 2 * i / PRIMARY_BINS,
                "ara_high": 2 * (i + 1) / PRIMARY_BINS,
                "R9_share": distributions["R9"][i],
                "R10_share": distributions["R10"][i],
                "R11_share": distributions["R11"][i],
            }
        )
    write_csv(OUT_DISTRIBUTIONS, distribution_rows)
    draw_figure(distributions, scores, r11_blocks, criteria)
    print(json.dumps({
        "result": str(OUT_JSON),
        "core": result["ridge_plus_scale_core_P1_P5"],
        "criteria": {key: value["passed"] for key, value in criteria.items()},
        "R11_primary_gain_bits": gains["R11"][str(PRIMARY_BINS)],
        "R10_primary_gain_bits": gains["R10"][str(PRIMARY_BINS)],
        "JSD": js,
        "scale_information_observed": observed_info["conditional_scale_information_bits"],
        "scale_information_shuffle_max": shuffle_max,
    }, indent=2))


if __name__ == "__main__":
    main()
