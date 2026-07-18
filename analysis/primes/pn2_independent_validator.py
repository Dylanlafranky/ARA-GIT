"""Independent validation of PN2 target outputs.

This file does not import pn2_prime_survival_bridge. It reconstructs target
primality with a separate bytearray segmented sieve and recomputes the stored
probabilistic scores from the frozen model tables and compact target packet.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from PIL import Image


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN2_PRIME_SURVIVAL_BRIDGE_PROTOCOL_v1_FROZEN.md"
CONFIG = HERE / "PN2_TARGET_RUN_CONFIG_v1_FROZEN.json"
SCRIPT = HERE / "pn2_prime_survival_bridge.py"
MODEL = HERE / "PN2_DEVELOPMENT_MODEL.npz"
RESULTS = HERE / "PN2_RESULTS.json"
SCORES = HERE / "PN2_MODEL_SCORES.csv"
BLOCKS = HERE / "PN2_BLOCK_SCORES.csv"
GAPS = HERE / "PN2_GAP_CLASS_SURVIVAL.csv"
LOCATIONS = HERE / "PN2_LOCATION_CALIBRATION.csv"
PACKET = HERE / "PN2_TARGET_PACKET.npz"
OUTPUT = HERE / "PN2_INDEPENDENT_VALIDATION.json"
FIGURES = [HERE / "PN2_SURVIVAL_MODEL_COMPARISON.png", HERE / "PN2_GAP_CLASS_CALIBRATION.png"]

EXPECTED_PROTOCOL = "2F70766D0335C34C01ADCDABE512540415CAF37E6A176C546B16E955806DA664"
SIEVE_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
W29 = math.prod(1.0 - 1.0 / p for p in SIEVE_PRIMES)
C2 = 0.6601618158468696
LOW, HIGH = 100_000_000, 110_000_000
EPS = 1e-9
SEED = 20_260_717


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1 << 20)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest().upper()


def small_primes(limit: int) -> list[int]:
    flags = bytearray(b"\x01") * (limit + 1)
    flags[0:2] = b"\x00\x00"
    for candidate in range(2, math.isqrt(limit) + 1):
        if flags[candidate]:
            count = ((limit - candidate * candidate) // candidate) + 1
            flags[candidate * candidate :: candidate] = b"\x00" * count
    return [i for i, flag in enumerate(flags) if flag]


def independent_prime_mask(low: int, high: int) -> np.ndarray:
    flags = bytearray(b"\x01") * (high - low)
    for prime in small_primes(math.isqrt(high - 1)):
        start = max(prime * prime, ((low + prime - 1) // prime) * prime)
        if start < high:
            count = ((high - 1 - start) // prime) + 1
            flags[start - low :: prime] = b"\x00" * count
    return np.frombuffer(flags, dtype=np.uint8)


def clip(values: np.ndarray) -> np.ndarray:
    return np.clip(values.astype(float), EPS, 1.0 - EPS)


def logit(values: np.ndarray) -> np.ndarray:
    values = clip(values)
    return np.log(values / (1.0 - values))


def logistic(values: np.ndarray) -> np.ndarray:
    return clip(1.0 / (1.0 + np.exp(-np.clip(values, -700, 700))))


def ara(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return 2.0 * right.astype(float) / (left.astype(float) + right.astype(float))


def bins(values: np.ndarray, count: int) -> np.ndarray:
    clipped = np.clip(values, 0.0, 2.0 - np.finfo(float).eps)
    return np.minimum((clipped * count / 2.0).astype(np.uint8), count - 1)


def pack_fixed(columns: list[np.ndarray], base: int) -> np.ndarray:
    output = np.zeros(len(columns[0]), dtype=np.uint64)
    for column in columns:
        output = output * np.uint64(base) + column.astype(np.uint64)
    return output


def pack_mixed(columns: list[np.ndarray], bases: list[int]) -> np.ndarray:
    output = np.zeros(len(columns[0]), dtype=np.uint64)
    for column, base in zip(columns, bases):
        output = output * np.uint64(base) + column.astype(np.uint64)
    return output


def factorize(number: int) -> list[int]:
    output: list[int] = []
    remaining = number
    divisor = 2
    while divisor * divisor <= remaining:
        if remaining % divisor == 0:
            output.append(divisor)
            while remaining % divisor == 0:
                remaining //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if remaining > 1:
        output.append(remaining)
    return output


def hl_probability(numbers: np.ndarray, gaps: np.ndarray) -> np.ndarray:
    cache: dict[int, float] = {}
    for gap in np.unique(gaps):
        gap_int = int(gap)
        singular = 2.0 * C2
        for factor in factorize(gap_int):
            if factor > 2:
                singular *= (factor - 1.0) / (factor - 2.0)
        passed = 1.0
        for prime in SIEVE_PRIMES:
            passed *= 1.0 - (1 if gap_int % prime == 0 else 2) / prime
        cache[gap_int] = singular / passed
    multiplier = np.array([cache[int(g)] for g in gaps], dtype=float)
    return clip(multiplier / (np.log(numbers.astype(float)) * np.log((numbers + gaps).astype(float))))


def pnt_probability(numbers: np.ndarray) -> np.ndarray:
    return clip(1.0 / (np.log(numbers.astype(float)) * W29))


def candidate_key(name: str, gm2: np.ndarray, gm1: np.ndarray, g0: np.ndarray, gp1: np.ndarray) -> np.ndarray:
    if name == "raw_local":
        return pack_fixed([gm1, g0], 64)
    if name == "raw_stencil":
        return pack_fixed([gm2, gm1, g0, gp1], 64)
    count = int(name.split("_b")[-1])
    previous = bins(ara(gm2, gm1), count)
    current = bins(ara(gm1, g0), count)
    following = bins(ara(g0, gp1), count)
    if name.startswith("ara_plain"):
        return current.astype(np.uint64)
    if name.startswith("ara_i3") or name.startswith("logratio_i3"):
        return pack_fixed([previous, current, following], count)
    if name.startswith("ara_decompressed"):
        width = gm1.astype(np.uint16) + g0.astype(np.uint16)
        return pack_mixed([previous, current, following, width], [count, count, count, 128])
    raise KeyError(name)


def edge_key(name: str, gm1: np.ndarray, g0: np.ndarray, gp1: np.ndarray) -> np.ndarray:
    if name == "raw_edge":
        return pack_fixed([gm1, g0, gp1], 64)
    count = int(name.split("_b")[-1])
    left = bins(ara(gm1, g0), count)
    right = bins(ara(g0, gp1), count)
    if name.startswith("ara_edge_b") or name.startswith("logratio_edge"):
        return pack_fixed([left, right], count)
    if name.startswith("ara_edge_decompressed"):
        return pack_mixed([left, right, g0], [count, count, 64])
    raise KeyError(name)


def apply(keys: np.ndarray, baseline: np.ndarray, model_keys: np.ndarray, offsets: np.ndarray) -> np.ndarray:
    positions = np.searchsorted(model_keys, keys)
    valid = positions < len(model_keys)
    matched = np.zeros(len(keys), dtype=bool)
    matched[valid] = model_keys[positions[valid]] == keys[valid]
    delta = np.zeros(len(keys), dtype=float)
    delta[matched] = offsets[positions[matched]]
    return logistic(logit(baseline) + delta)


def loss(labels: np.ndarray, prediction: np.ndarray) -> np.ndarray:
    prediction = clip(prediction)
    return -(labels * np.log2(prediction) + (1 - labels) * np.log2(1.0 - prediction))


def main() -> None:
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, detail: Any = None) -> None:
        checks.append({"name": name, "passed": bool(condition), "detail": detail})
        if not condition:
            raise AssertionError(f"validation failed: {name}: {detail}")

    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    stored_scores = pd.read_csv(SCORES)
    stored_blocks = pd.read_csv(BLOCKS)
    stored_gaps = pd.read_csv(GAPS)
    stored_locations = pd.read_csv(LOCATIONS)
    check("protocol hash", file_hash(PROTOCOL) == EXPECTED_PROTOCOL, file_hash(PROTOCOL))
    check("config protocol hash", config["protocol_sha256"] == EXPECTED_PROTOCOL)
    check("analysis script hash", file_hash(SCRIPT) == config["analysis_script_sha256"], file_hash(SCRIPT))
    check("development model hash", file_hash(MODEL) == config["development_model_sha256"], file_hash(MODEL))
    check("target interval", tuple(config["target_interval"]) == (LOW, HIGH))
    check("sieve budget", config["sieve_budget_max_prime"] == 29)
    check("p31 wheel false", results["pn1h_p31_wheel_accessed"] is False)

    with np.load(PACKET, allow_pickle=False) as packet:
        numbers = packet["numbers"].astype(np.int64)
        labels = packet["labels"].astype(np.uint8)
        gm2 = packet["gm2"].astype(np.uint8)
        gm1 = packet["gm1"].astype(np.uint8)
        g0 = packet["g0"].astype(np.uint8)
        gp1 = packet["gp1"].astype(np.uint8)
    check("packet row lengths", len({len(numbers), len(labels), len(gm2), len(gm1), len(g0), len(gp1)}) == 1)
    check("candidate event count", len(numbers) == results["candidate_events"], len(numbers))
    check("candidate positive count", int(np.sum(labels)) == results["candidate_primes"], int(np.sum(labels)))
    check("strict candidate order", bool(np.all(np.diff(numbers) > 0)))
    check("candidate bounds", int(numbers[0]) >= LOW and int(numbers[-1]) < HIGH, [int(numbers[0]), int(numbers[-1])])
    for prime in SIEVE_PRIMES:
        check(f"coprime to {prime}", bool(np.all(numbers % prime != 0)))
    check("right gap continuity", bool(np.array_equal(np.diff(numbers), g0[:-1].astype(np.int64))))
    check("left gap shift", bool(np.array_equal(gm1[1:], g0[:-1])))
    check("two-left gap shift", bool(np.array_equal(gm2[2:], g0[:-2])))
    check("right-context shift", bool(np.array_equal(gp1[:-1], g0[1:])))

    independent_mask = independent_prime_mask(LOW, HIGH)
    independent_labels = independent_mask[numbers - LOW]
    check("independent full primality labels", bool(np.array_equal(independent_labels, labels)), int(np.sum(independent_labels != labels)))

    candidate_baseline = pnt_probability(numbers)
    edge_numbers = numbers[:-1]
    edge_labels = (labels[:-1] * labels[1:]).astype(np.uint8)
    edge_gaps = g0[:-1]
    edge_baseline = hl_probability(edge_numbers, edge_gaps)
    check("edge event count", len(edge_labels) == results["edge_events"], len(edge_labels))
    check("edge positive count", int(np.sum(edge_labels)) == results["edge_survivors"], int(np.sum(edge_labels)))

    predictions: dict[str, np.ndarray] = {
        "candidate_pnt29": candidate_baseline,
        "edge_hl29": edge_baseline,
    }
    with np.load(MODEL, allow_pickle=False) as archive:
        for field in archive.files:
            if not field.endswith("__keys"):
                continue
            internal_name = field[: -len("__keys")]
            task, state_name, lambda_name = internal_name.split("__")
            model_keys = archive[field]
            offsets = archive[f"{internal_name}__offsets"]
            if task == "candidate":
                key = candidate_key(state_name, gm2, gm1, g0, gp1)
                prediction = apply(key, candidate_baseline, model_keys, offsets)
            else:
                key = edge_key(state_name, gm1[:-1], g0[:-1], gp1[:-1])
                prediction = apply(key, edge_baseline, model_keys, offsets)
            predictions[f"{state_name}_{lambda_name}"] = prediction

    check("candidate mapped log-ratio equality", float(np.max(np.abs(predictions["ara_i3_b12_l64"] - predictions["logratio_i3_b12_l64"]))) == 0.0)
    check("edge mapped log-ratio equality", float(np.max(np.abs(predictions["ara_edge_b12_l64"] - predictions["logratio_edge_b12_l64"]))) == 0.0)

    analytic_losses = {
        "candidate": float(np.mean(loss(labels, candidate_baseline))),
        "edge": float(np.mean(loss(edge_labels, edge_baseline))),
    }
    for row in stored_scores.itertuples(index=False):
        task = row.task
        target_labels = labels if task == "candidate" else edge_labels
        prediction = predictions[row.model]
        computed_loss = float(np.mean(loss(target_labels, prediction)))
        computed_brier = float(np.mean((prediction - target_labels) ** 2))
        check(f"score loss {task}/{row.model}", abs(computed_loss - float(row.log_loss_bits)) < 2e-12, [computed_loss, row.log_loss_bits])
        check(f"score brier {task}/{row.model}", abs(computed_brier - float(row.brier_score)) < 2e-12, [computed_brier, row.brier_score])
        check(f"score analytic gain {task}/{row.model}", abs((analytic_losses[task] - computed_loss) - float(row.gain_vs_analytic_bits)) < 2e-12)

    for task, target_labels, target_numbers in [("candidate", labels, numbers), ("edge", edge_labels, edge_numbers)]:
        endpoint = results[f"primary_{task}_endpoint"]
        baseline_prediction = predictions[endpoint["baseline_model"]]
        ara_prediction = predictions[endpoint["ara_model"]]
        block_ids = np.minimum(((target_numbers - LOW) * 40 // (HIGH - LOW)).astype(int), 39)
        baseline_loss = loss(target_labels, baseline_prediction)
        ara_loss = loss(target_labels, ara_prediction)
        counts = np.bincount(block_ids, minlength=40)
        baseline_sums = np.bincount(block_ids, weights=baseline_loss, minlength=40)
        ara_sums = np.bincount(block_ids, weights=ara_loss, minlength=40)
        observed = float((np.sum(baseline_sums) - np.sum(ara_sums)) / np.sum(counts))
        rng = np.random.default_rng(SEED)
        sample = rng.integers(0, 40, size=(10_000, 40), endpoint=False)
        bootstrap = (np.sum(baseline_sums[sample], axis=1) - np.sum(ara_sums[sample], axis=1)) / np.sum(counts[sample], axis=1)
        check(f"{task} endpoint delta", abs(observed - endpoint["observed_delta_bits"]) < 2e-12, observed)
        check(f"{task} bootstrap lower", abs(float(np.quantile(bootstrap, 0.025)) - endpoint["bootstrap_lower_95_bits"]) < 2e-12)
        check(f"{task} bootstrap upper", abs(float(np.quantile(bootstrap, 0.975)) - endpoint["bootstrap_upper_95_bits"]) < 2e-12)
        stored_task_blocks = stored_blocks[stored_blocks.task == task].sort_values("block")
        computed_delta = (baseline_sums - ara_sums) / counts
        check(f"{task} block deltas", float(np.max(np.abs(computed_delta - stored_task_blocks.delta_bits.to_numpy(float)))) < 2e-12)

    for gap in np.unique(edge_gaps):
        mask = edge_gaps == gap
        row = stored_gaps[stored_gaps.gap == int(gap)].iloc[0]
        check(f"gap {int(gap)} events", int(np.sum(mask)) == int(row.candidate_edges))
        check(f"gap {int(gap)} survivors", int(np.sum(edge_labels[mask])) == int(row.survivor_edges))
        for model, column in [
            ("edge_hl29", "hl29_expected_survivors"),
            ("raw_edge_l64", "raw_edge_expected_survivors"),
            ("ara_edge_b12_l64", "ara_edge_expected_survivors"),
            ("ara_edge_decompressed_b12_l64", "ara_edge_decompressed_expected_survivors"),
        ]:
            expected = float(np.sum(predictions[model][mask]))
            check(f"gap {int(gap)} {model}", abs(expected - float(row[column])) < 2e-8)

    location_ids = np.minimum(((numbers - LOW) * 20 // (HIGH - LOW)).astype(int), 19)
    for block in range(20):
        mask = location_ids == block
        row = stored_locations[stored_locations.block == block].iloc[0]
        check(f"location {block} candidates", int(np.sum(mask)) == int(row.candidates))
        check(f"location {block} actual", int(np.sum(labels[mask])) == int(row.actual_primes))
        for model, column in [
            ("candidate_pnt29", "pnt29_predicted_primes"),
            ("raw_stencil_l64", "raw_stencil_predicted_primes"),
            ("ara_i3_b12_l64", "ara_i3_predicted_primes"),
            ("ara_decompressed_b12_l64", "ara_decompressed_predicted_primes"),
        ]:
            expected = float(np.sum(predictions[model][mask]))
            check(f"location {block} {model}", abs(expected - float(row[column])) < 2e-7)

    for figure in FIGURES:
        with Image.open(figure) as image:
            width, height = image.size
            check(f"{figure.name} readable", width >= 1600 and height >= 900, [width, height])

    payload = {
        "validation_id": "PN2/INDEPENDENT/v1",
        "status": "PASS",
        "passed_check_count": int(sum(item["passed"] for item in checks)),
        "check_count": len(checks),
        "full_target_primality_reconstructed": True,
        "primary_script_imported": False,
        "pn1h_p31_wheel_accessed": False,
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ["status", "passed_check_count", "check_count"]}, indent=2))


if __name__ == "__main__":
    main()
