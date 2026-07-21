"""Independent PN7C validator; does not import the scorer."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN7C_ACTUAL_GAP_SEQUENTIAL_MEMORY_PROTOCOL.md"
MODEL_PATH = HERE / "PN7C_FROZEN_MODELS.npz"
TARGET_PATH = HERE / "PN7C_R11_TARGET_GAPS.npz"
RESULT_PATH = HERE / "PN7C_ACTUAL_GAP_SEQUENTIAL_MEMORY_RESULTS.json"
FIGURE_PATH = HERE / "PN7C_ACTUAL_GAP_SEQUENTIAL_MEMORY_FIGURE.png"
OUT = HERE / "PN7C_ACTUAL_GAP_SEQUENTIAL_MEMORY_VALIDATION.json"
EXPECTED = {
    "protocol": "7884D02A19A753DFD2582BEEDC6AFBE38B15E04E44DDD6F5B6B11116F518A67C",
    "model": "9141AA398C6A6694C3C5F3ECA954681D4AD8091C01310D13C6703DB30668F3A2",
    "target": "D60EEDFA2F3A5DF4C8FA45B45D2B478EDB39B6D54001302F84041989C8D0CF2F",
}
LOW, HIGH = 100_000_000_000, 101_000_000_000
REBUILD_CHUNK = 8_000_003
COUNT_CHUNK = 777_777
BINS = 24
ALPHA = 0.5
RAW_LAMBDA = 64.0
RAW_ALPHABET = 1025
SHUFFLE_SEEDS = tuple(range(2026071901, 2026071906))
MARKOV_SEED = 2026071917
MARKOV_PATHS = 10_000_000


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda: f.read(3_000_001), b""):
            h.update(part)
    return h.hexdigest().upper()


def primes_up_to(limit: int) -> np.ndarray:
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for prime in range(2, math.isqrt(limit) + 1):
        if sieve[prime]:
            start = prime * prime
            sieve[start::prime] = b"\x00" * (((limit - start) // prime) + 1)
    return np.flatnonzero(np.frombuffer(sieve, dtype=np.uint8)).astype(np.int64)


def rebuild_target() -> np.ndarray:
    divisors = primes_up_to(math.isqrt(HIGH - 1))
    pieces = []
    previous = None
    for start in range(LOW, HIGH, REBUILD_CHUNK):
        stop = min(HIGH, start + REBUILD_CHUNK)
        flags = np.ones(stop - start, dtype=bool)
        for qv in divisors:
            q = int(qv)
            multiple = max(q * q, ((start + q - 1) // q) * q)
            if multiple < stop:
                flags[multiple - start::q] = False
        values = np.flatnonzero(flags).astype(np.int64) + start
        difference = np.diff(values) if previous is None else np.diff(np.r_[previous, values])
        if difference.size:
            pieces.append(difference.astype(np.uint16))
        if values.size:
            previous = int(values[-1])
    return np.concatenate(pieces)


def states_from_gaps(gaps: np.ndarray) -> np.ndarray:
    left = gaps[:-1].astype(np.uint64)
    right = gaps[1:].astype(np.uint64)
    return np.minimum((BINS * right) // (left + right), BINS - 1).astype(np.uint8)


def conditional_entropy(table: np.ndarray) -> float:
    rows = table.reshape(-1, BINS).astype(np.longdouble)
    totals = rows.sum(axis=1)
    rows = rows[totals > 0]
    totals = totals[totals > 0]
    p = rows / totals[:, None]
    logs = np.zeros_like(p)
    positive = p > 0
    logs[positive] = np.log2(p[positive])
    return float(-np.sum(totals[:, None] * p * logs) / np.sum(totals))


def memory_gain(states: np.ndarray) -> float:
    counts = np.zeros(BINS ** 3, dtype=np.int64)
    total = len(states) - 2
    for a in range(0, total, COUNT_CHUNK):
        b = min(total, a + COUNT_CHUNK)
        code = ((states[a:b].astype(np.int64) * BINS + states[a + 1:b + 1]) * BINS
                + states[a + 2:b + 2])
        counts += np.bincount(code, minlength=BINS ** 3)
    cube = counts.reshape(BINS, BINS, BINS)
    return conditional_entropy(cube.sum(axis=0)) - conditional_entropy(cube)


def probabilities(model) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    marginal = model["b24__marginal"].astype(np.float64)
    one = model["b24__m1"].astype(np.float64)
    two = model["b24__m2"].astype(np.float64)
    iid = (marginal + ALPHA) / (marginal.sum() + ALPHA * BINS)
    m1 = (one + ALPHA) / (one.sum(axis=1, keepdims=True) + ALPHA * BINS)
    m2 = (two + ALPHA) / (two.sum(axis=2, keepdims=True) + ALPHA * BINS)

    gap_marginal = model["raw__marginal"].astype(np.float64)
    gap_transition = model["raw__transition"].astype(np.float64)
    gap_p = np.zeros(RAW_ALPHABET, dtype=np.float64)
    gap_p[1:] = (gap_marginal[1:] + ALPHA) / (gap_marginal[1:].sum() + ALPHA * (RAW_ALPHABET - 1))
    row_total = gap_transition.sum(axis=1, keepdims=True)
    raw = (gap_transition + RAW_LAMBDA * gap_p[None, :]) / (row_total + RAW_LAMBDA)
    raw[row_total[:, 0] == 0] = gap_p
    projected = np.zeros((RAW_ALPHABET, BINS), dtype=np.float64)
    candidates = np.arange(RAW_ALPHABET, dtype=np.int64)
    for current in range(RAW_ALPHABET):
        denominator = current + candidates
        category = np.zeros(RAW_ALPHABET, dtype=np.int64)
        possible = denominator > 0
        category[possible] = np.minimum(BINS * candidates[possible] // denominator[possible], BINS - 1)
        np.add.at(projected[current], category, raw[current])
    return iid, m1, m2, raw, projected


def metric_parts(prob: np.ndarray):
    return np.sum(prob * prob, axis=-1), np.argmax(prob, axis=-1), np.argpartition(prob, -3, axis=-1)[..., -3:]


def score_primary(states: np.ndarray, gaps: np.ndarray, model) -> tuple[dict, np.ndarray]:
    iid, m1, m2, raw, projected = probabilities(model)
    probs = {"ARA-IID": iid, "ARA-M1": m1, "ARA-M2": m2, "RawGap-M1": projected}
    parts = {name: metric_parts(value) for name, value in probs.items()}
    total = len(states) - 2
    sums = {name: np.zeros(4, dtype=np.longdouble) for name in probs}
    block_sum = np.zeros(100, dtype=np.longdouble)
    block_n = np.zeros(100, dtype=np.int64)
    for a in range(0, total, COUNT_CHUNK):
        b = min(total, a + COUNT_CHUNK)
        previous = states[a:b].astype(np.int64)
        current = states[a + 1:b + 1].astype(np.int64)
        target = states[a + 2:b + 2].astype(np.int64)
        gap = gaps[a + 2:b + 2].astype(np.int64)
        p_target = {
            "ARA-IID": iid[target],
            "ARA-M1": m1[current, target],
            "ARA-M2": m2[previous, current, target],
            "RawGap-M1": projected[gap, target],
        }
        row = {"ARA-IID": None, "ARA-M1": current, "ARA-M2": (previous, current), "RawGap-M1": gap}
        for name in probs:
            square, top1, top3 = parts[name]
            selector = row[name]
            if selector is None:
                row_square = square
                pred1 = top1
                hit3 = np.any(top3 == target[:, None], axis=1)
            else:
                row_square = square[selector]
                pred1 = top1[selector]
                hit3 = np.any(top3[selector] == target[:, None], axis=1)
            sums[name][0] += np.sum(-np.log2(p_target[name]), dtype=np.longdouble)
            sums[name][1] += np.sum(1 + row_square - 2 * p_target[name], dtype=np.longdouble)
            sums[name][2] += np.count_nonzero(pred1 == target)
            sums[name][3] += np.count_nonzero(hit3)
        gain = np.log2(p_target["ARA-M2"] / p_target["ARA-M1"])
        groups = np.minimum(100 * np.arange(a, b, dtype=np.int64) // total, 99)
        block_sum += np.bincount(groups, weights=gain, minlength=100)
        block_n += np.bincount(groups, minlength=100)
    output = {}
    for name, values in sums.items():
        ce = float(values[0] / total)
        output[name] = {
            "cross_entropy_bits": ce,
            "brier_score": float(values[1] / total),
            "top1_accuracy": float(values[2] / total),
            "top3_accuracy": float(values[3] / total),
            "perplexity": float(2 ** ce),
        }
    return output, np.asarray(block_sum / block_n, dtype=np.float64)


def sample_step(current: np.ndarray, active: np.ndarray, raw: np.ndarray, rng) -> np.ndarray:
    ordering = np.argsort(current, kind="stable")
    sorted_values = current[ordering]
    values, starts, sizes = np.unique(sorted_values, return_index=True, return_counts=True)
    following = np.empty_like(current)
    for value, start, size in zip(values, starts, sizes):
        positions = ordering[start:start + size]
        weights = raw[int(value), active]
        following[positions] = rng.choice(active, int(size), p=weights / weights.sum())
    return following


def reproduce_markov(model) -> float:
    _, _, _, raw, _ = probabilities(model)
    marginal = model["raw__marginal"].astype(np.float64)
    gap_p = np.zeros(RAW_ALPHABET, dtype=np.float64)
    gap_p[1:] = (marginal[1:] + ALPHA) / (marginal[1:].sum() + ALPHA * (RAW_ALPHABET - 1))
    active = np.flatnonzero(gap_p > 0).astype(np.uint16)
    rng = np.random.default_rng(MARKOV_SEED)
    a = rng.choice(active, MARKOV_PATHS, p=gap_p[active] / gap_p[active].sum()).astype(np.uint16)
    b = sample_step(a, active, raw, rng)
    x = np.minimum(BINS * b.astype(np.uint32) // (a.astype(np.uint32) + b), BINS - 1).astype(np.uint8)
    c = sample_step(b, active, raw, rng)
    y = np.minimum(BINS * c.astype(np.uint32) // (b.astype(np.uint32) + c), BINS - 1).astype(np.uint8)
    d = sample_step(c, active, raw, rng)
    z = np.minimum(BINS * d.astype(np.uint32) // (c.astype(np.uint32) + d), BINS - 1).astype(np.uint8)
    code = (x.astype(np.int64) * BINS + y.astype(np.int64)) * BINS + z.astype(np.int64)
    cube = np.bincount(code, minlength=BINS ** 3).reshape(BINS, BINS, BINS)
    return conditional_entropy(cube.sum(axis=0)) - conditional_entropy(cube)


def main() -> None:
    checks = []

    def check(name: str, passed: bool, observed=None, expected=None):
        checks.append({"name": name, "passed": bool(passed), "observed": observed, "expected": expected})

    for label, path in (("protocol", PROTOCOL), ("model", MODEL_PATH), ("target", TARGET_PATH)):
        value = digest(path)
        check(f"{label}_hash", value == EXPECTED[label], value, EXPECTED[label])
    recorded = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    stored_gaps = np.load(TARGET_PATH, allow_pickle=False)["r11__gaps"]
    rebuilt_gaps = rebuild_target()
    check("independent_target_length", len(rebuilt_gaps) == len(stored_gaps), len(rebuilt_gaps), len(stored_gaps))
    check("independent_target_sequence_exact", np.array_equal(rebuilt_gaps, stored_gaps))
    del rebuilt_gaps

    states = states_from_gaps(stored_gaps)
    model = np.load(MODEL_PATH, allow_pickle=False)
    scores, blocks = score_primary(states, stored_gaps, model)
    for name, values in scores.items():
        for metric, observed in values.items():
            expected = recorded["scores"]["24"][name][metric]
            check(f"score_{name}_{metric}", abs(observed - expected) < 1e-10, observed, expected)
    expected_blocks = np.asarray(recorded["block_summary_24_bins"]["positive_blocks"])
    check("positive_blocks", int(np.count_nonzero(blocks > 0)) == int(expected_blocks), int(np.count_nonzero(blocks > 0)), int(expected_blocks))
    check("block_mean", abs(float(blocks.mean()) - recorded["block_summary_24_bins"]["mean_gain_bits"]) < 1e-12,
          float(blocks.mean()), recorded["block_summary_24_bins"]["mean_gain_bits"])

    observed_memory = memory_gain(states)
    expected_memory = recorded["empirical_target_memory"]["24"]["conditional_memory_gain_bits"]
    check("observed_memory", abs(observed_memory - expected_memory) < 1e-12, observed_memory, expected_memory)
    shuffle_values = []
    for index, seed in enumerate(SHUFFLE_SEEDS):
        copy = stored_gaps.copy()
        np.random.default_rng(seed).shuffle(copy)
        value = memory_gain(states_from_gaps(copy))
        shuffle_values.append(value)
        expected = recorded["exact_inventory_shuffles_24_bins"][index]["conditional_memory_gain_bits"]
        check(f"shuffle_{index + 1}_memory", abs(value - expected) < 1e-12, value, expected)
    markov_value = reproduce_markov(model)
    expected_markov = recorded["raw_gap_markov_world_24_bins"]["conditional_memory_gain_bits"]
    check("raw_markov_memory", abs(markov_value - expected_markov) < 1e-12, markov_value, expected_markov)

    gain = scores["ARA-M1"]["cross_entropy_bits"] - scores["ARA-M2"]["cross_entropy_bits"]
    reconstructed = {
        "P1": gain >= 0.010,
        "P2": np.count_nonzero(blocks > 0) >= 80 and recorded["block_summary_24_bins"]["bootstrap_95_percentile_interval_bits"][0] > 0,
        "P3": all(value > 0 for value in recorded["predictive_m1_minus_m2_gain_bits"].values()),
        "P4": observed_memory - max(shuffle_values) >= 0.010,
        "P5": observed_memory - markov_value >= 0.010,
        "P6": scores["ARA-M2"]["cross_entropy_bits"] < scores["RawGap-M1"]["cross_entropy_bits"],
        "P7": scores["ARA-M2"]["brier_score"] < scores["ARA-M1"]["brier_score"] and scores["ARA-M2"]["top3_accuracy"] > scores["ARA-M1"]["top3_accuracy"],
    }
    for key, value in reconstructed.items():
        expected = recorded["criteria"][key]["passed"]
        check(f"criterion_{key}", value == expected, value, expected)
    check("residual_core", all(reconstructed[f"P{i}"] for i in range(1, 6)) == recorded["residual_ordered_memory_core_passed"])
    with Image.open(FIGURE_PATH) as image:
        check("figure_dimensions", image.size == (1500, 960), list(image.size), [1500, 960])

    packet = {
        "test_id": "PN7C/INDEPENDENT-VALIDATION-v1",
        "validator_sha256": digest(Path(__file__)),
        "independent_target_rebuild_chunk": REBUILD_CHUNK,
        "independent_count_chunk": COUNT_CHUNK,
        "checks_total": len(checks),
        "checks_passed": sum(row["passed"] for row in checks),
        "all_passed": all(row["passed"] for row in checks),
        "checks": checks,
    }
    OUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: packet[key] for key in ("checks_total", "checks_passed", "all_passed")}, indent=2))
    if not packet["all_passed"]:
        raise AssertionError("Independent validation failed")


if __name__ == "__main__":
    main()
