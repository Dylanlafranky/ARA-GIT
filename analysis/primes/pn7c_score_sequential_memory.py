"""Score the frozen PN7C sequential-memory models on code-isolated R11."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN7C_ACTUAL_GAP_SEQUENTIAL_MEMORY_PROTOCOL.md"
MODEL = HERE / "PN7C_FROZEN_MODELS.npz"
TARGET = HERE / "PN7C_R11_TARGET_GAPS.npz"
EXPECTED_PROTOCOL = "7884D02A19A753DFD2582BEEDC6AFBE38B15E04E44DDD6F5B6B11116F518A67C"
EXPECTED_MODEL = "9141AA398C6A6694C3C5F3ECA954681D4AD8091C01310D13C6703DB30668F3A2"
EXPECTED_TARGET = "D60EEDFA2F3A5DF4C8FA45B45D2B478EDB39B6D54001302F84041989C8D0CF2F"
OUT_JSON = HERE / "PN7C_ACTUAL_GAP_SEQUENTIAL_MEMORY_RESULTS.json"
OUT_SCORES = HERE / "PN7C_ACTUAL_GAP_SEQUENTIAL_MEMORY_SCORES.csv"
OUT_BLOCKS = HERE / "PN7C_ACTUAL_GAP_SEQUENTIAL_MEMORY_BLOCKS.csv"
OUT_CONTROLS = HERE / "PN7C_ACTUAL_GAP_SEQUENTIAL_MEMORY_CONTROLS.csv"
OUT_FIGURE = HERE / "PN7C_ACTUAL_GAP_SEQUENTIAL_MEMORY_FIGURE.png"
BINS = (12, 24, 48)
PRIMARY_BINS = 24
ALPHA = 0.5
RAW_LAMBDA = 64.0
RAW_ALPHABET = 1025
SHUFFLE_SEEDS = tuple(range(2026071901, 2026071906))
MARKOV_SEED = 2026071917
MARKOV_PATHS = 10_000_000
BOOTSTRAP_SEED = 2026071923
BOOTSTRAP_DRAWS = 10_000
CHUNK = 500_000


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest().upper()


def ara_bins(gaps: np.ndarray, bins: int) -> np.ndarray:
    left = gaps[:-1].astype(np.uint32)
    right = gaps[1:].astype(np.uint32)
    out = (bins * right) // (left + right)
    return np.minimum(out, bins - 1).astype(np.uint8)


def conditional_entropy_bits(joint: np.ndarray) -> float:
    rows = joint.reshape(-1, joint.shape[-1]).astype(np.float64)
    totals = rows.sum(axis=1)
    rows = rows[totals > 0]
    totals = totals[totals > 0]
    probs = rows / totals[:, None]
    terms = np.zeros_like(probs)
    positive = probs > 0
    terms[positive] = probs[positive] * np.log2(probs[positive])
    return float(-np.sum(totals * terms.sum(axis=1)) / totals.sum())


def triple_counts(states: np.ndarray, bins: int) -> np.ndarray:
    counts = np.zeros(bins ** 3, dtype=np.int64)
    events = len(states) - 2
    for start in range(0, events, CHUNK):
        stop = min(events, start + CHUNK)
        prev = states[start:stop].astype(np.int64)
        current = states[start + 1:stop + 1].astype(np.int64)
        nxt = states[start + 2:stop + 2].astype(np.int64)
        code = (prev * bins + current) * bins + nxt
        counts += np.bincount(code, minlength=bins ** 3)
    return counts.reshape(bins, bins, bins)


def empirical_memory(states: np.ndarray, bins: int) -> dict:
    triple = triple_counts(states, bins)
    m1 = triple.sum(axis=0)
    h1 = conditional_entropy_bits(m1)
    h2 = conditional_entropy_bits(triple)
    return {
        "events": int(triple.sum()),
        "h_next_given_current_bits": h1,
        "h_next_given_previous_current_bits": h2,
        "conditional_memory_gain_bits": h1 - h2,
    }


def frozen_probabilities(model: np.lib.npyio.NpzFile, bins: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    marginal = model[f"b{bins}__marginal"].astype(np.float64)
    m1 = model[f"b{bins}__m1"].astype(np.float64)
    m2 = model[f"b{bins}__m2"].astype(np.float64)
    iid_p = (marginal + ALPHA) / (marginal.sum() + ALPHA * bins)
    m1_p = (m1 + ALPHA) / (m1.sum(axis=1, keepdims=True) + ALPHA * bins)
    m2_p = (m2 + ALPHA) / (m2.sum(axis=2, keepdims=True) + ALPHA * bins)
    return iid_p, m1_p, m2_p


def raw_transition_probabilities(model: np.lib.npyio.NpzFile) -> tuple[np.ndarray, np.ndarray]:
    marginal = model["raw__marginal"].astype(np.float64)
    transition = model["raw__transition"].astype(np.float64)
    # The protocol freezes additive categorical smoothing at alpha=0.5 and a
    # raw alphabet of gaps 1..1024.  Index zero is storage-only and impossible.
    marginal_p = np.zeros_like(marginal)
    marginal_p[1:] = (marginal[1:] + ALPHA) / (marginal[1:].sum() + ALPHA * (RAW_ALPHABET - 1))
    row_sum = transition.sum(axis=1, keepdims=True)
    raw_p = (transition + RAW_LAMBDA * marginal_p[None, :]) / (row_sum + RAW_LAMBDA)
    unseen = row_sum[:, 0] == 0
    raw_p[unseen] = marginal_p
    return marginal_p, raw_p


def project_raw_rows(raw_p: np.ndarray, bins: int) -> np.ndarray:
    projection = np.zeros((RAW_ALPHABET, bins), dtype=np.float64)
    next_gap = np.arange(RAW_ALPHABET, dtype=np.int64)
    for current in range(RAW_ALPHABET):
        denominator = current + next_gap
        mapped = np.zeros(RAW_ALPHABET, dtype=np.int64)
        valid = denominator > 0
        mapped[valid] = np.minimum((bins * next_gap[valid]) // denominator[valid], bins - 1)
        projection[current] = np.bincount(mapped, weights=raw_p[current], minlength=bins)
    return projection


def model_helpers(prob: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    square_sum = np.sum(prob * prob, axis=-1)
    top1 = np.argmax(prob, axis=-1)
    top3 = np.argpartition(prob, -3, axis=-1)[..., -3:]
    return square_sum, top1, top3


def score_models(states: np.ndarray, gaps: np.ndarray, model: np.lib.npyio.NpzFile, bins: int,
                 raw_p: np.ndarray) -> tuple[dict, np.ndarray]:
    iid_p, m1_p, m2_p = frozen_probabilities(model, bins)
    raw_projection = project_raw_rows(raw_p, bins)
    names = ("ARA-IID", "ARA-M1", "ARA-M2", "RawGap-M1")
    helpers = {
        "ARA-IID": model_helpers(iid_p),
        "ARA-M1": model_helpers(m1_p),
        "ARA-M2": model_helpers(m2_p),
        "RawGap-M1": model_helpers(raw_projection),
    }
    totals = {name: {"logloss": 0.0, "brier": 0.0, "top1": 0, "top3": 0} for name in names}
    n_events = len(states) - 2
    block_sum = np.zeros(100, dtype=np.float64)
    block_count = np.zeros(100, dtype=np.int64)

    for start in range(0, n_events, CHUNK):
        stop = min(n_events, start + CHUNK)
        previous = states[start:stop].astype(np.int64)
        current = states[start + 1:stop + 1].astype(np.int64)
        target = states[start + 2:stop + 2].astype(np.int64)
        shared_gap = gaps[start + 2:stop + 2].astype(np.int64)
        if np.any(shared_gap >= RAW_ALPHABET):
            raise AssertionError("Target current gap exceeds frozen raw alphabet")

        rows = {
            "ARA-IID": None,
            "ARA-M1": current,
            "ARA-M2": (previous, current),
            "RawGap-M1": shared_gap,
        }
        probabilities = {
            "ARA-IID": iid_p[target],
            "ARA-M1": m1_p[current, target],
            "ARA-M2": m2_p[previous, current, target],
            "RawGap-M1": raw_projection[shared_gap, target],
        }
        for name in names:
            p_target = probabilities[name]
            square_sum, top1, top3 = helpers[name]
            row = rows[name]
            if row is None:
                row_square = np.full(len(target), square_sum)
                pred1 = np.full(len(target), top1)
                pred3 = np.broadcast_to(top3, (len(target), 3))
            elif isinstance(row, tuple):
                row_square = square_sum[row]
                pred1 = top1[row]
                pred3 = top3[row]
            else:
                row_square = square_sum[row]
                pred1 = top1[row]
                pred3 = top3[row]
            totals[name]["logloss"] += float(np.sum(-np.log2(p_target)))
            totals[name]["brier"] += float(np.sum(1.0 + row_square - 2.0 * p_target))
            totals[name]["top1"] += int(np.count_nonzero(pred1 == target))
            totals[name]["top3"] += int(np.count_nonzero(np.any(pred3 == target[:, None], axis=1)))

        gain = np.log2(probabilities["ARA-M2"] / probabilities["ARA-M1"])
        global_index = np.arange(start, stop, dtype=np.int64)
        block = np.minimum((100 * global_index) // n_events, 99)
        block_sum += np.bincount(block, weights=gain, minlength=100)
        block_count += np.bincount(block, minlength=100)

    result = {}
    for name in names:
        ce = totals[name]["logloss"] / n_events
        result[name] = {
            "events": n_events,
            "cross_entropy_bits": ce,
            "brier_score": totals[name]["brier"] / n_events,
            "top1_accuracy": totals[name]["top1"] / n_events,
            "top3_accuracy": totals[name]["top3"] / n_events,
            "perplexity": 2.0 ** ce,
        }
    return result, block_sum / block_count


def sample_next(current: np.ndarray, active: np.ndarray, raw_p: np.ndarray,
                rng: np.random.Generator) -> np.ndarray:
    order = np.argsort(current, kind="stable")
    sorted_current = current[order]
    values, starts, counts = np.unique(sorted_current, return_index=True, return_counts=True)
    out = np.empty_like(current)
    for value, start, count in zip(values, starts, counts):
        positions = order[start:start + count]
        probabilities = raw_p[int(value), active]
        probabilities = probabilities / probabilities.sum()
        out[positions] = rng.choice(active, size=int(count), p=probabilities)
    return out


def markov_world_memory(marginal_p: np.ndarray, raw_p: np.ndarray, bins: int) -> dict:
    rng = np.random.default_rng(MARKOV_SEED)
    active = np.flatnonzero(marginal_p > 0).astype(np.uint16)
    active_p = marginal_p[active]
    active_p = active_p / active_p.sum()
    g0 = rng.choice(active, size=MARKOV_PATHS, p=active_p).astype(np.uint16)
    g1 = sample_next(g0, active, raw_p, rng)
    x0 = np.minimum((bins * g1.astype(np.uint32)) // (g0.astype(np.uint32) + g1), bins - 1).astype(np.uint8)
    del g0
    g2 = sample_next(g1, active, raw_p, rng)
    x1 = np.minimum((bins * g2.astype(np.uint32)) // (g1.astype(np.uint32) + g2), bins - 1).astype(np.uint8)
    del g1
    g3 = sample_next(g2, active, raw_p, rng)
    x2 = np.minimum((bins * g3.astype(np.uint32)) // (g2.astype(np.uint32) + g3), bins - 1).astype(np.uint8)
    del g2, g3
    code = (x0.astype(np.int64) * bins + x1.astype(np.int64)) * bins + x2.astype(np.int64)
    triple = np.bincount(code, minlength=bins ** 3).reshape(bins, bins, bins)
    h1 = conditional_entropy_bits(triple.sum(axis=0))
    h2 = conditional_entropy_bits(triple)
    return {
        "seed": MARKOV_SEED,
        "independent_four_gap_paths": MARKOV_PATHS,
        "h_next_given_current_bits": h1,
        "h_next_given_previous_current_bits": h2,
        "conditional_memory_gain_bits": h1 - h2,
    }


def bootstrap_blocks(block_gain: np.ndarray) -> dict:
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    means = np.empty(BOOTSTRAP_DRAWS, dtype=np.float64)
    for start in range(0, BOOTSTRAP_DRAWS, 1000):
        stop = min(BOOTSTRAP_DRAWS, start + 1000)
        selections = rng.integers(0, len(block_gain), size=(stop - start, len(block_gain)))
        means[start:stop] = block_gain[selections].mean(axis=1)
    low, high = np.percentile(means, [2.5, 97.5])
    return {
        "seed": BOOTSTRAP_SEED,
        "draws": BOOTSTRAP_DRAWS,
        "positive_blocks": int(np.count_nonzero(block_gain > 0)),
        "mean_gain_bits": float(block_gain.mean()),
        "bootstrap_95_percentile_interval_bits": [float(low), float(high)],
    }


def font(size: int, bold: bool = False):
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def draw_figure(scores: dict, controls: list[dict], blocks: np.ndarray, criteria: dict) -> None:
    width, height = 1500, 960
    image = Image.new("RGB", (width, height), "#F5F1E8")
    draw = ImageDraw.Draw(image)
    navy, rust, ink, muted, green, red = "#17324D", "#C66A3D", "#202428", "#6C706F", "#377A57", "#A33F3F"
    draw.text((58, 36), "PN7C — Does arrival direction survive the controls?", fill=ink, font=font(36, True))
    draw.text((58, 84), "R9–R10 frozen models → code-isolated R11 actual-prime gaps", fill=muted, font=font(21))

    # Cross-entropy panel.
    x0, y0, w, h = 70, 170, 630, 310
    draw.text((x0, y0 - 42), "24-bin predictive cross-entropy (lower is better)", fill=ink, font=font(23, True))
    primary = scores[str(PRIMARY_BINS)]
    names = ["ARA-IID", "ARA-M1", "ARA-M2", "RawGap-M1"]
    values = [primary[name]["cross_entropy_bits"] for name in names]
    finite_values = [value for value in values if math.isfinite(value)]
    floor = min(finite_values) - 0.03
    ceiling = max(finite_values) + 0.03
    colors = ["#9EA8AE", navy, rust, "#6C7086"]
    for i, (name, value, color) in enumerate(zip(names, values, colors)):
        yy = y0 + i * 69
        draw.text((x0, yy + 10), name, fill=ink, font=font(19, name == "ARA-M2"))
        left = x0 + 170
        length = int((value - floor) / (ceiling - floor) * 390) if math.isfinite(value) else 390
        draw.rectangle((left, yy + 8, left + max(length, 2), yy + 39), fill=color)
        label = f"{value:.5f} bits" if math.isfinite(value) else "infinite"
        draw.text((left + 405, yy + 9), label, fill=ink, font=font(18))

    # Memory controls panel.
    x1, y1 = 790, 170
    draw.text((x1, y1 - 42), "Empirical conditional-memory gain", fill=ink, font=font(23, True))
    control_names = [row["label"] for row in controls]
    control_values = [row["conditional_memory_gain_bits"] for row in controls]
    maximum = max(control_values) * 1.12
    for i, (name, value) in enumerate(zip(control_names, control_values)):
        yy = y1 + i * 42
        bar = int(value / maximum * 430) if maximum > 0 else 0
        color = rust if name == "Observed R11" else navy if name == "Raw Markov" else "#AAB2B5"
        draw.text((x1, yy), name, fill=ink, font=font(16, name == "Observed R11"))
        draw.rectangle((x1 + 165, yy + 2, x1 + 165 + max(bar, 2), yy + 23), fill=color)
        draw.text((x1 + 610, yy), f"{value:.5f}", fill=ink, font=font(15))

    # Block panel.
    x0, y2 = 70, 585
    draw.text((x0, y2 - 48), "R11 transfer is distributed across the record", fill=ink, font=font(23, True))
    base = y2 + 180
    scale = 150 / max(float(np.max(np.abs(blocks))), 1e-12)
    draw.line((x0, base, x0 + 940, base), fill=muted, width=2)
    for i, value in enumerate(blocks):
        left = x0 + int(i * 9.4)
        top = base - int(value * scale)
        draw.rectangle((left, min(base, top), left + 7, max(base, top)), fill=green if value > 0 else red)
    draw.text((x0, base + 20), "100 contiguous equal-observation blocks; bar = ARA-M1 CE − ARA-M2 CE", fill=muted, font=font(17))

    # Criteria panel.
    cx, cy = 1060, 545
    draw.rounded_rectangle((cx, cy, 1440, 885), radius=18, fill="#E8E2D6", outline="#C8C0B2", width=2)
    draw.text((cx + 26, cy + 24), "Registered conditions", fill=ink, font=font(22, True))
    for i in range(1, 8):
        key = f"P{i}"
        passed = bool(criteria[key]["passed"])
        symbol = "PASS" if passed else "FAIL"
        color = green if passed else red
        draw.text((cx + 28, cy + 68 + (i - 1) * 31), key, fill=ink, font=font(18, True))
        draw.text((cx + 84, cy + 68 + (i - 1) * 31), symbol, fill=color, font=font(18, True))
    core = all(criteria[f"P{i}"]["passed"] for i in range(1, 6))
    draw.line((cx + 26, cy + 292, cx + 354, cy + 292), fill="#C8C0B2", width=2)
    draw.text((cx + 28, cy + 303), f"Residual core P1–P5: {'PASS' if core else 'FAIL'}", fill=green if core else red, font=font(18, True))
    image.save(OUT_FIGURE)


def main() -> None:
    for path, expected, label in (
        (PROTOCOL, EXPECTED_PROTOCOL, "protocol"),
        (MODEL, EXPECTED_MODEL, "model"),
        (TARGET, EXPECTED_TARGET, "target"),
    ):
        if sha256(path) != expected:
            raise RuntimeError(f"{label} hash mismatch")

    model = np.load(MODEL, allow_pickle=False)
    gaps = np.load(TARGET, allow_pickle=False)["r11__gaps"]
    marginal_p, raw_p = raw_transition_probabilities(model)
    all_scores = {}
    all_blocks = {}
    observed_memory = {}
    for bins in BINS:
        states = ara_bins(gaps, bins)
        scores, blocks = score_models(states, gaps, model, bins, raw_p)
        all_scores[str(bins)] = scores
        all_blocks[str(bins)] = blocks.tolist()
        observed_memory[str(bins)] = empirical_memory(states, bins)
        print(json.dumps({"bins": bins, "scores": scores, "memory": observed_memory[str(bins)]}, indent=2), flush=True)

    primary_states = ara_bins(gaps, PRIMARY_BINS)
    shuffles = []
    for seed in SHUFFLE_SEEDS:
        shuffled = gaps.copy()
        np.random.default_rng(seed).shuffle(shuffled)
        result = empirical_memory(ara_bins(shuffled, PRIMARY_BINS), PRIMARY_BINS)
        result["seed"] = seed
        shuffles.append(result)
        print(json.dumps({"shuffle": result}, indent=2), flush=True)
        del shuffled
    markov = markov_world_memory(marginal_p, raw_p, PRIMARY_BINS)
    print(json.dumps({"raw_markov_world": markov}, indent=2), flush=True)

    block_primary = np.asarray(all_blocks[str(PRIMARY_BINS)], dtype=np.float64)
    block_summary = bootstrap_blocks(block_primary)
    primary = all_scores[str(PRIMARY_BINS)]
    predictive_gain = primary["ARA-M1"]["cross_entropy_bits"] - primary["ARA-M2"]["cross_entropy_bits"]
    observed_gain = observed_memory[str(PRIMARY_BINS)]["conditional_memory_gain_bits"]
    max_shuffle = max(row["conditional_memory_gain_bits"] for row in shuffles)
    markov_gain = markov["conditional_memory_gain_bits"]
    sensitivity_gains = {
        str(b): all_scores[str(b)]["ARA-M1"]["cross_entropy_bits"] - all_scores[str(b)]["ARA-M2"]["cross_entropy_bits"]
        for b in BINS
    }
    criteria = {
        "P1": {"passed": predictive_gain >= 0.010, "value_bits": predictive_gain, "threshold_bits": 0.010},
        "P2": {"passed": block_summary["positive_blocks"] >= 80 and block_summary["bootstrap_95_percentile_interval_bits"][0] > 0,
               "positive_blocks": block_summary["positive_blocks"], "bootstrap_interval_bits": block_summary["bootstrap_95_percentile_interval_bits"]},
        "P3": {"passed": all(value > 0 for value in sensitivity_gains.values()), "gains_bits": sensitivity_gains},
        "P4": {"passed": observed_gain - max_shuffle >= 0.010, "observed_bits": observed_gain,
               "maximum_shuffle_bits": max_shuffle, "margin_bits": observed_gain - max_shuffle, "threshold_bits": 0.010},
        "P5": {"passed": observed_gain - markov_gain >= 0.010, "observed_bits": observed_gain,
               "raw_markov_bits": markov_gain, "margin_bits": observed_gain - markov_gain, "threshold_bits": 0.010},
        "P6": {"passed": primary["ARA-M2"]["cross_entropy_bits"] < primary["RawGap-M1"]["cross_entropy_bits"],
               "ara_m2_bits": primary["ARA-M2"]["cross_entropy_bits"], "raw_gap_m1_bits": primary["RawGap-M1"]["cross_entropy_bits"]},
        "P7": {"passed": primary["ARA-M2"]["brier_score"] < primary["ARA-M1"]["brier_score"] and
                          primary["ARA-M2"]["top3_accuracy"] > primary["ARA-M1"]["top3_accuracy"],
               "ara_m1_brier": primary["ARA-M1"]["brier_score"], "ara_m2_brier": primary["ARA-M2"]["brier_score"],
               "ara_m1_top3": primary["ARA-M1"]["top3_accuracy"], "ara_m2_top3": primary["ARA-M2"]["top3_accuracy"]},
    }

    controls_for_figure = [{"label": "Observed R11", "conditional_memory_gain_bits": observed_gain}]
    controls_for_figure += [{"label": f"Shuffle {i + 1}", "conditional_memory_gain_bits": row["conditional_memory_gain_bits"]} for i, row in enumerate(shuffles)]
    controls_for_figure += [{"label": "Raw Markov", "conditional_memory_gain_bits": markov_gain}]
    draw_figure(all_scores, controls_for_figure, block_primary, criteria)

    packet = {
        "test_id": "PN7C/ACTUAL-GAP-SEQUENTIAL-MEMORY/CODE-ISOLATED-R11-v1",
        "hashes": {"protocol": EXPECTED_PROTOCOL, "model_npz": EXPECTED_MODEL, "target_npz": EXPECTED_TARGET,
                   "scorer": sha256(Path(__file__))},
        "target": {"gap_count": int(len(gaps)), "state_count": int(len(gaps) - 1), "scored_events": int(len(gaps) - 3)},
        "scores": all_scores,
        "predictive_m1_minus_m2_gain_bits": sensitivity_gains,
        "block_summary_24_bins": block_summary,
        "empirical_target_memory": observed_memory,
        "exact_inventory_shuffles_24_bins": shuffles,
        "raw_gap_markov_world_24_bins": markov,
        "criteria": criteria,
        "residual_ordered_memory_core_passed": all(criteria[f"P{i}"]["passed"] for i in range(1, 6)),
        "all_seven_passed": all(value["passed"] for value in criteria.values()),
        "boundaries": {
            "exact_next_prime_location_prediction": False,
            "physical_wave_cause_established": False,
            "information_beyond_raw_gaps_created": False,
            "blind_test": False,
            "r12_opened": False,
            "p31_wheel_opened": False,
        },
    }
    OUT_JSON.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")

    with OUT_SCORES.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["bins", "model", "events", "cross_entropy_bits", "brier_score", "top1_accuracy", "top3_accuracy", "perplexity"])
        writer.writeheader()
        for bins, by_model in all_scores.items():
            for name, row in by_model.items():
                writer.writerow({"bins": bins, "model": name, **row})
    with OUT_BLOCKS.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["block", "ara_m1_minus_ara_m2_gain_bits"])
        writer.writerows((i + 1, value) for i, value in enumerate(block_primary))
    with OUT_CONTROLS.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["control", "seed", "events", "conditional_memory_gain_bits"])
        writer.writerow(["observed_r11", "", observed_memory[str(PRIMARY_BINS)]["events"], observed_gain])
        for row in shuffles:
            writer.writerow(["exact_inventory_shuffle", row["seed"], row["events"], row["conditional_memory_gain_bits"]])
        writer.writerow(["raw_gap_markov_world", markov["seed"], markov["independent_four_gap_paths"], markov_gain])

    print(json.dumps({"criteria": criteria, "residual_core": packet["residual_ordered_memory_core_passed"],
                      "results_sha256": sha256(OUT_JSON), "figure": OUT_FIGURE.name}, indent=2), flush=True)


if __name__ == "__main__":
    main()
