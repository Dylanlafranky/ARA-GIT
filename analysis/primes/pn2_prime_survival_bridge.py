"""PN2 fixed-budget bridge from the p29 wheel to actual-prime survival.

Run order:
    python pn2_prime_survival_bridge.py --mode development
    # freeze PN2_TARGET_RUN_CONFIG_v1_FROZEN.json with script/model hashes
    python pn2_prime_survival_bridge.py --mode target

The target interval is never touched in development mode.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN2_PRIME_SURVIVAL_BRIDGE_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA256 = "2F70766D0335C34C01ADCDABE512540415CAF37E6A176C546B16E955806DA664"
TARGET_CONFIG = HERE / "PN2_TARGET_RUN_CONFIG_v1_FROZEN.json"
MODEL_PATH = HERE / "PN2_DEVELOPMENT_MODEL.npz"
DEV_SUMMARY_PATH = HERE / "PN2_DEVELOPMENT_SUMMARY.json"
RESULTS_PATH = HERE / "PN2_RESULTS.json"
SCORES_PATH = HERE / "PN2_MODEL_SCORES.csv"
BLOCKS_PATH = HERE / "PN2_BLOCK_SCORES.csv"
GAPS_PATH = HERE / "PN2_GAP_CLASS_SURVIVAL.csv"
LOCATIONS_PATH = HERE / "PN2_LOCATION_CALIBRATION.csv"
PACKET_PATH = HERE / "PN2_TARGET_PACKET.npz"
MODEL_FIGURE = HERE / "PN2_SURVIVAL_MODEL_COMPARISON.png"
GAP_FIGURE = HERE / "PN2_GAP_CLASS_CALIBRATION.png"

DEVELOPMENT_INTERVAL = (10_000_000, 20_000_000)
TARGET_INTERVAL = (100_000_000, 110_000_000)
CONTEXT_MARGIN = 2_000
SIEVE_PRIMES = np.array([2, 3, 5, 7, 11, 13, 17, 19, 23, 29], dtype=np.int64)
W29 = float(np.prod(1.0 - 1.0 / SIEVE_PRIMES.astype(float)))
TWIN_PRIME_CONSTANT = 0.6601618158468696
PRIMARY_BINS = 12
SENSITIVITY_BINS = (8, 16, 24)
PRIMARY_LAMBDA = 64.0
SENSITIVITY_LAMBDAS = (16.0, 32.0, 128.0)
EPS = 1e-9
BOOTSTRAP_SEED = 20_260_717


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): json_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, Path):
        return str(value)
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(json_ready(payload), indent=2) + "\n", encoding="utf-8")


def simple_primes(limit: int) -> np.ndarray:
    sieve = np.ones(limit + 1, dtype=bool)
    sieve[:2] = False
    for p in range(2, int(math.isqrt(limit)) + 1):
        if sieve[p]:
            sieve[p * p :: p] = False
    return np.flatnonzero(sieve).astype(np.int64)


def segmented_prime_mask(low: int, high: int) -> np.ndarray:
    mask = np.ones(high - low, dtype=bool)
    if low <= 1:
        mask[: max(0, 2 - low)] = False
    for p in simple_primes(math.isqrt(high - 1)):
        start = max(int(p * p), ((low + int(p) - 1) // int(p)) * int(p))
        if start < high:
            mask[start - low :: int(p)] = False
    return mask


def p29_candidate_mask(low: int, high: int) -> np.ndarray:
    mask = np.ones(high - low, dtype=bool)
    for p in SIEVE_PRIMES:
        start = (-low) % int(p)
        mask[start:: int(p)] = False
    return mask


def ara_coordinate(left_gap: np.ndarray, right_gap: np.ndarray) -> np.ndarray:
    return 2.0 * right_gap.astype(float) / (left_gap.astype(float) + right_gap.astype(float))


def ara_bin(values: np.ndarray, bins: int) -> np.ndarray:
    return np.minimum((np.clip(values, 0.0, 2.0 - np.finfo(float).eps) * bins / 2.0).astype(np.uint8), bins - 1)


def pack_fixed(columns: list[np.ndarray], base: int) -> np.ndarray:
    key = np.zeros(len(columns[0]), dtype=np.uint64)
    for column in columns:
        if int(np.max(column, initial=0)) >= base or int(np.min(column, initial=0)) < 0:
            raise AssertionError(f"value outside packing base {base}")
        key = key * np.uint64(base) + column.astype(np.uint64)
    return key


def pack_mixed(columns: list[np.ndarray], bases: list[int]) -> np.ndarray:
    if len(columns) != len(bases):
        raise ValueError("columns/bases mismatch")
    key = np.zeros(len(columns[0]), dtype=np.uint64)
    for column, base in zip(columns, bases):
        if int(np.max(column, initial=0)) >= base or int(np.min(column, initial=0)) < 0:
            raise AssertionError(f"value outside packing base {base}")
        key = key * np.uint64(base) + column.astype(np.uint64)
    return key


def clip_probability(values: np.ndarray) -> np.ndarray:
    return np.clip(values.astype(float), EPS, 1.0 - EPS)


def logit(values: np.ndarray) -> np.ndarray:
    values = clip_probability(values)
    return np.log(values / (1.0 - values))


def logistic(values: np.ndarray) -> np.ndarray:
    output = np.empty_like(values, dtype=float)
    positive = values >= 0
    output[positive] = 1.0 / (1.0 + np.exp(-values[positive]))
    exp_values = np.exp(values[~positive])
    output[~positive] = exp_values / (1.0 + exp_values)
    return clip_probability(output)


def pnt29_probability(numbers: np.ndarray) -> np.ndarray:
    return clip_probability(1.0 / (np.log(numbers.astype(float)) * W29))


def prime_factors(number: int) -> list[int]:
    factors: list[int] = []
    remaining = int(number)
    for p in simple_primes(math.isqrt(remaining) + 1):
        p_int = int(p)
        if remaining % p_int == 0:
            factors.append(p_int)
            while remaining % p_int == 0:
                remaining //= p_int
        if p_int * p_int > remaining:
            break
    if remaining > 1:
        factors.append(remaining)
    return factors


def hl29_multiplier(gap: int) -> float:
    singular = 2.0 * TWIN_PRIME_CONSTANT
    for factor in prime_factors(gap):
        if factor > 2:
            singular *= (factor - 1.0) / (factor - 2.0)
    pass_probability = 1.0
    for prime in SIEVE_PRIMES:
        q = int(prime)
        forbidden = 1 if gap % q == 0 else 2
        pass_probability *= 1.0 - forbidden / q
    return singular / pass_probability


def hl29_probability(numbers: np.ndarray, gaps: np.ndarray) -> np.ndarray:
    unique_gaps = np.unique(gaps)
    multiplier = {int(g): hl29_multiplier(int(g)) for g in unique_gaps}
    factors = np.array([multiplier[int(g)] for g in gaps], dtype=float)
    return clip_probability(factors / (np.log(numbers.astype(float)) * np.log((numbers + gaps).astype(float))))


def build_interval(low: int, high: int) -> dict[str, np.ndarray]:
    extended_low = low - CONTEXT_MARGIN
    extended_high = high + CONTEXT_MARGIN
    candidate_mask = p29_candidate_mask(extended_low, extended_high)
    prime_mask = segmented_prime_mask(extended_low, extended_high)
    candidates = np.flatnonzero(candidate_mask).astype(np.int64) + extended_low
    candidate_is_prime = prime_mask[candidates - extended_low].astype(np.uint8)
    gaps = np.diff(candidates).astype(np.uint8)
    if int(np.max(gaps)) >= 64:
        raise AssertionError("raw gap exceeded six-bit packing range")

    indices = np.arange(2, len(candidates) - 2, dtype=np.int64)
    numbers = candidates[indices]
    in_range = (numbers >= low) & (numbers < high)
    indices = indices[in_range]
    numbers = candidates[indices]
    labels = candidate_is_prime[indices]

    gm2 = gaps[indices - 2]
    gm1 = gaps[indices - 1]
    g0 = gaps[indices]
    gp1 = gaps[indices + 1]
    x_prev = ara_coordinate(gm2, gm1)
    x_current = ara_coordinate(gm1, g0)
    x_next = ara_coordinate(g0, gp1)

    for prime in SIEVE_PRIMES:
        if np.any(numbers % int(prime) == 0):
            raise AssertionError(f"candidate divisible by sieve prime {int(prime)}")

    return {
        "numbers": numbers,
        "labels": labels,
        "gm2": gm2,
        "gm1": gm1,
        "g0": g0,
        "gp1": gp1,
        "x_prev": x_prev,
        "x_current": x_current,
        "x_next": x_next,
    }


def candidate_keys(data: dict[str, np.ndarray], bins: int) -> dict[str, np.ndarray]:
    bprev = ara_bin(data["x_prev"], bins)
    bcurrent = ara_bin(data["x_current"], bins)
    bnext = ara_bin(data["x_next"], bins)
    width = data["gm1"].astype(np.uint16) + data["g0"].astype(np.uint16)
    if int(np.max(width)) >= 128:
        raise AssertionError("candidate width exceeded packing range")
    keys = {
        "raw_local": pack_fixed([data["gm1"], data["g0"]], 64),
        "raw_stencil": pack_fixed([data["gm2"], data["gm1"], data["g0"], data["gp1"]], 64),
        f"ara_plain_b{bins}": bcurrent.astype(np.uint64),
        f"ara_i3_b{bins}": pack_fixed([bprev, bcurrent, bnext], bins),
        f"ara_decompressed_b{bins}": pack_mixed([bprev, bcurrent, bnext, width], [bins, bins, bins, 128]),
        f"logratio_i3_b{bins}": pack_fixed([bprev, bcurrent, bnext], bins),
    }
    return keys


def edge_view(data: dict[str, np.ndarray], bins: int) -> dict[str, np.ndarray]:
    count = len(data["numbers"]) - 1
    bcurrent = ara_bin(data["x_current"][:count], bins)
    bnext = ara_bin(data["x_next"][:count], bins)
    central_gap = data["g0"][:count]
    labels = (data["labels"][:count] * data["labels"][1 : count + 1]).astype(np.uint8)
    if not np.array_equal(data["numbers"][1 : count + 1] - data["numbers"][:count], central_gap.astype(np.int64)):
        raise AssertionError("edge central gap mismatch")
    return {
        "numbers": data["numbers"][:count],
        "labels": labels,
        "central_gap": central_gap,
        "raw_edge": pack_fixed([data["gm1"][:count], central_gap, data["gp1"][:count]], 64),
        f"ara_edge_b{bins}": pack_fixed([bcurrent, bnext], bins),
        f"ara_edge_decompressed_b{bins}": pack_mixed([bcurrent, bnext, central_gap], [bins, bins, 64]),
        f"logratio_edge_b{bins}": pack_fixed([bcurrent, bnext], bins),
    }


def fit_offset_family(keys: np.ndarray, labels: np.ndarray, baseline: np.ndarray, shrinkages: tuple[float, ...]) -> tuple[np.ndarray, dict[float, np.ndarray], dict[str, float]]:
    unique_keys, inverse = np.unique(keys, return_inverse=True)
    counts = np.bincount(inverse).astype(float)
    successes = np.bincount(inverse, weights=labels.astype(float))
    baseline_sum = np.bincount(inverse, weights=baseline.astype(float))
    baseline_mean = baseline_sum / counts
    offsets_by_shrinkage: dict[float, np.ndarray] = {}
    for shrinkage in shrinkages:
        posterior = (successes + shrinkage * baseline_mean) / (counts + shrinkage)
        offsets_by_shrinkage[shrinkage] = (logit(posterior) - logit(baseline_mean)).astype(np.float64)
    diagnostics = {
        "states": int(len(unique_keys)),
        "singleton_states": int(np.sum(counts == 1)),
        "minimum_count": int(np.min(counts)),
        "median_count": float(np.median(counts)),
        "maximum_count": int(np.max(counts)),
    }
    return unique_keys.astype(np.uint64), offsets_by_shrinkage, diagnostics


def apply_offsets(keys: np.ndarray, baseline: np.ndarray, model_keys: np.ndarray, offsets: np.ndarray) -> np.ndarray:
    positions = np.searchsorted(model_keys, keys)
    valid = positions < len(model_keys)
    matched = np.zeros(len(keys), dtype=bool)
    matched[valid] = model_keys[positions[valid]] == keys[valid]
    delta = np.zeros(len(keys), dtype=float)
    delta[matched] = offsets[positions[matched]]
    return logistic(logit(baseline) + delta)


def per_event_loss(labels: np.ndarray, probabilities: np.ndarray) -> np.ndarray:
    probabilities = clip_probability(probabilities)
    return -(labels * np.log2(probabilities) + (1 - labels) * np.log2(1.0 - probabilities))


def score_model(task: str, name: str, labels: np.ndarray, probabilities: np.ndarray, analytic_baseline_loss: float, bins: int | None, shrinkage: float | None) -> dict[str, Any]:
    losses = per_event_loss(labels, probabilities)
    return {
        "task": task,
        "model": name,
        "bins": bins,
        "shrinkage": shrinkage,
        "events": int(len(labels)),
        "positives": int(np.sum(labels)),
        "actual_rate": float(np.mean(labels)),
        "mean_prediction": float(np.mean(probabilities)),
        "calibration_error": float(np.mean(probabilities) - np.mean(labels)),
        "log_loss_bits": float(np.mean(losses)),
        "gain_vs_analytic_bits": float(analytic_baseline_loss - np.mean(losses)),
        "brier_score": float(np.mean((probabilities - labels) ** 2)),
    }


def build_model_registry(development: dict[str, np.ndarray]) -> tuple[dict[str, tuple[np.ndarray, np.ndarray]], dict[str, Any]]:
    labels = development["labels"]
    candidate_baseline = pnt29_probability(development["numbers"])
    edge_primary = edge_view(development, PRIMARY_BINS)
    edge_baseline = hl29_probability(edge_primary["numbers"], edge_primary["central_gap"])
    registry: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    diagnostics: dict[str, Any] = {}

    bin_options = (PRIMARY_BINS,) + SENSITIVITY_BINS
    for bins in bin_options:
        ckeys = candidate_keys(development, bins)
        eview = edge_view(development, bins)
        shrinkages = (PRIMARY_LAMBDA,) + SENSITIVITY_LAMBDAS if bins == PRIMARY_BINS else (PRIMARY_LAMBDA,)
        for key_name, keys in ckeys.items():
            if bins != PRIMARY_BINS and key_name in {"raw_local", "raw_stencil"}:
                continue
            model_keys, offsets_by_shrinkage, diag = fit_offset_family(keys, labels, candidate_baseline, shrinkages)
            for shrinkage, offsets in offsets_by_shrinkage.items():
                model_name = f"candidate__{key_name}__l{int(shrinkage)}"
                registry[model_name] = (model_keys, offsets)
                diagnostics[model_name] = diag
        for key_name, keys in eview.items():
            if key_name in {"numbers", "labels", "central_gap"}:
                continue
            if bins != PRIMARY_BINS and key_name == "raw_edge":
                continue
            model_keys, offsets_by_shrinkage, diag = fit_offset_family(keys, eview["labels"], edge_baseline, shrinkages)
            for shrinkage, offsets in offsets_by_shrinkage.items():
                model_name = f"edge__{key_name}__l{int(shrinkage)}"
                registry[model_name] = (model_keys, offsets)
                diagnostics[model_name] = diag
    return registry, diagnostics


def save_registry(registry: dict[str, tuple[np.ndarray, np.ndarray]], metadata: dict[str, Any]) -> None:
    payload: dict[str, np.ndarray] = {"metadata_json": np.array(json.dumps(json_ready(metadata)))}
    for name, (keys, offsets) in registry.items():
        payload[f"{name}__keys"] = keys
        payload[f"{name}__offsets"] = offsets
    np.savez_compressed(MODEL_PATH, **payload)


def load_registry() -> tuple[dict[str, tuple[np.ndarray, np.ndarray]], dict[str, Any]]:
    registry: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    with np.load(MODEL_PATH, allow_pickle=False) as archive:
        metadata = json.loads(str(archive["metadata_json"].item()))
        for field in archive.files:
            if not field.endswith("__keys"):
                continue
            name = field[: -len("__keys")]
            registry[name] = (archive[field].copy(), archive[f"{name}__offsets"].copy())
    return registry, metadata


def evaluate_registry(target: dict[str, np.ndarray], registry: dict[str, tuple[np.ndarray, np.ndarray]]) -> tuple[pd.DataFrame, dict[str, np.ndarray], dict[str, np.ndarray], dict[str, Any]]:
    candidate_baseline = pnt29_probability(target["numbers"])
    candidate_predictions: dict[str, np.ndarray] = {"candidate_pnt29": candidate_baseline}
    edge_primary = edge_view(target, PRIMARY_BINS)
    edge_baseline = hl29_probability(edge_primary["numbers"], edge_primary["central_gap"])
    edge_predictions: dict[str, np.ndarray] = {"edge_hl29": edge_baseline}

    all_bins = (PRIMARY_BINS,) + SENSITIVITY_BINS
    candidate_keys_by_bins = {bins: candidate_keys(target, bins) for bins in all_bins}
    edge_views_by_bins = {bins: edge_view(target, bins) for bins in all_bins}
    rows: list[dict[str, Any]] = []
    candidate_analytic_loss = float(np.mean(per_event_loss(target["labels"], candidate_baseline)))
    edge_analytic_loss = float(np.mean(per_event_loss(edge_primary["labels"], edge_baseline)))
    rows.append(score_model("candidate", "candidate_pnt29", target["labels"], candidate_baseline, candidate_analytic_loss, None, None))
    rows.append(score_model("edge", "edge_hl29", edge_primary["labels"], edge_baseline, edge_analytic_loss, None, None))

    for model_name, (model_keys, offsets) in registry.items():
        parts = model_name.split("__")
        task, key_name, lambda_part = parts
        shrinkage = float(lambda_part[1:])
        if "_b" in key_name:
            bins = int(key_name.split("_b")[-1])
        else:
            bins = PRIMARY_BINS
        if task == "candidate":
            keys = candidate_keys_by_bins[bins][key_name]
            prediction = apply_offsets(keys, candidate_baseline, model_keys, offsets)
            public_name = f"{key_name}_l{int(shrinkage)}"
            if bins == PRIMARY_BINS and shrinkage == PRIMARY_LAMBDA:
                candidate_predictions[public_name] = prediction
            rows.append(score_model(task, public_name, target["labels"], prediction, candidate_analytic_loss, bins if "ara" in key_name or "logratio" in key_name else None, shrinkage))
        else:
            view = edge_views_by_bins[bins]
            keys = view[key_name]
            prediction = apply_offsets(keys, edge_baseline, model_keys, offsets)
            public_name = f"{key_name}_l{int(shrinkage)}"
            if bins == PRIMARY_BINS and shrinkage == PRIMARY_LAMBDA:
                edge_predictions[public_name] = prediction
            rows.append(score_model(task, public_name, view["labels"], prediction, edge_analytic_loss, bins if "ara" in key_name or "logratio" in key_name else None, shrinkage))

    scores = pd.DataFrame(rows)
    checks = {
        "candidate_logratio_prediction_max_abs_error": float(np.max(np.abs(
            candidate_predictions["ara_i3_b12_l64"] - candidate_predictions["logratio_i3_b12_l64"]
        ))),
        "edge_logratio_prediction_max_abs_error": float(np.max(np.abs(
            edge_predictions["ara_edge_b12_l64"] - edge_predictions["logratio_edge_b12_l64"]
        ))),
    }
    return scores, candidate_predictions, edge_predictions, checks


def bootstrap_delta(numbers: np.ndarray, labels: np.ndarray, baseline_prediction: np.ndarray, ara_prediction: np.ndarray, low: int, high: int) -> tuple[pd.DataFrame, dict[str, float]]:
    block_ids = np.minimum(((numbers - low) * 40 // (high - low)).astype(int), 39)
    baseline_losses = per_event_loss(labels, baseline_prediction)
    ara_losses = per_event_loss(labels, ara_prediction)
    rows = []
    counts = np.zeros(40, dtype=np.int64)
    baseline_sums = np.zeros(40, dtype=float)
    ara_sums = np.zeros(40, dtype=float)
    for block in range(40):
        mask = block_ids == block
        counts[block] = int(np.sum(mask))
        baseline_sums[block] = float(np.sum(baseline_losses[mask]))
        ara_sums[block] = float(np.sum(ara_losses[mask]))
        rows.append({
            "block": block,
            "start": int(low + block * (high - low) // 40),
            "end": int(low + (block + 1) * (high - low) // 40),
            "events": int(counts[block]),
            "baseline_loss_bits": float(baseline_sums[block] / counts[block]),
            "ara_loss_bits": float(ara_sums[block] / counts[block]),
            "delta_bits": float((baseline_sums[block] - ara_sums[block]) / counts[block]),
        })
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    samples = rng.integers(0, 40, size=(10_000, 40), endpoint=False)
    sample_counts = np.sum(counts[samples], axis=1)
    sample_delta = (
        np.sum(baseline_sums[samples], axis=1) - np.sum(ara_sums[samples], axis=1)
    ) / sample_counts
    summary = {
        "observed_delta_bits": float((np.sum(baseline_sums) - np.sum(ara_sums)) / np.sum(counts)),
        "bootstrap_lower_95_bits": float(np.quantile(sample_delta, 0.025)),
        "bootstrap_upper_95_bits": float(np.quantile(sample_delta, 0.975)),
        "positive_block_share": float(np.mean((baseline_sums - ara_sums) / counts > 0)),
    }
    return pd.DataFrame(rows), summary


def poisson_deviance(observed: np.ndarray, expected: np.ndarray) -> float:
    expected = np.clip(expected.astype(float), EPS, None)
    observed = observed.astype(float)
    term = np.where(observed > 0, observed * np.log(observed / expected) - (observed - expected), expected)
    return float(2.0 * np.sum(term))


def build_gap_class_table(target: dict[str, np.ndarray], edge_predictions: dict[str, np.ndarray]) -> tuple[pd.DataFrame, dict[str, Any]]:
    edge = edge_view(target, PRIMARY_BINS)
    gaps = edge["central_gap"].astype(int)
    labels = edge["labels"].astype(int)
    models = {
        "hl29": edge_predictions["edge_hl29"],
        "raw_edge": edge_predictions["raw_edge_l64"],
        "ara_edge": edge_predictions["ara_edge_b12_l64"],
        "ara_edge_decompressed": edge_predictions["ara_edge_decompressed_b12_l64"],
    }
    rows: list[dict[str, Any]] = []
    for gap in np.unique(gaps):
        mask = gaps == gap
        row: dict[str, Any] = {
            "gap": int(gap),
            "candidate_edges": int(np.sum(mask)),
            "survivor_edges": int(np.sum(labels[mask])),
            "actual_survival_rate": float(np.mean(labels[mask])),
        }
        for name, prediction in models.items():
            row[f"{name}_expected_survivors"] = float(np.sum(prediction[mask]))
            row[f"{name}_mean_probability"] = float(np.mean(prediction[mask]))
        rows.append(row)
    table = pd.DataFrame(rows).sort_values("gap").reset_index(drop=True)
    eligible = table.survivor_edges >= 100
    summary: dict[str, Any] = {"eligible_gap_classes": int(np.sum(eligible))}
    observed = table.loc[eligible, "survivor_edges"].to_numpy(float)
    for name in models:
        expected = table.loc[eligible, f"{name}_expected_survivors"].to_numpy(float)
        summary[name] = {
            "poisson_deviance": poisson_deviance(observed, expected),
            "weighted_absolute_relative_error": float(np.sum(np.abs(expected - observed)) / np.sum(observed)),
        }
    return table, summary


def build_location_table(target: dict[str, np.ndarray], candidate_predictions: dict[str, np.ndarray], low: int, high: int) -> tuple[pd.DataFrame, dict[str, Any]]:
    models = {
        "pnt29": candidate_predictions["candidate_pnt29"],
        "raw_stencil": candidate_predictions["raw_stencil_l64"],
        "ara_i3": candidate_predictions["ara_i3_b12_l64"],
        "ara_decompressed": candidate_predictions["ara_decompressed_b12_l64"],
    }
    block_ids = np.minimum(((target["numbers"] - low) * 20 // (high - low)).astype(int), 19)
    rows: list[dict[str, Any]] = []
    for block in range(20):
        mask = block_ids == block
        row: dict[str, Any] = {
            "block": block,
            "start": int(low + block * (high - low) // 20),
            "end": int(low + (block + 1) * (high - low) // 20),
            "candidates": int(np.sum(mask)),
            "actual_primes": int(np.sum(target["labels"][mask])),
        }
        for name, prediction in models.items():
            row[f"{name}_predicted_primes"] = float(np.sum(prediction[mask]))
        rows.append(row)
    table = pd.DataFrame(rows)
    summary: dict[str, Any] = {}
    actual = table.actual_primes.to_numpy(float)
    for name in models:
        predicted = table[f"{name}_predicted_primes"].to_numpy(float)
        summary[name] = {
            "mean_absolute_percentage_error": float(np.mean(np.abs(predicted - actual) / actual)),
            "signed_calibration_error_share": float(np.sum(predicted - actual) / np.sum(actual)),
        }
    return table, summary


def make_figures(scores: pd.DataFrame, blocks: pd.DataFrame, locations: pd.DataFrame, gap_classes: pd.DataFrame, results: dict[str, Any]) -> None:
    ink = "#202733"
    blue = "#2E7DBA"
    orange = "#E67E22"
    grey = "#8C98A4"
    gold = "#D9A514"
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 12, "axes.labelsize": 10})

    fig, axes = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=True)
    core_candidate = ["candidate_pnt29", "raw_local_l64", "raw_stencil_l64", "ara_plain_b12_l64", "ara_i3_b12_l64", "ara_decompressed_b12_l64"]
    labels_candidate = ["PNT29", "Raw pair", "Raw stencil", "Plain ARA", "ARA I³", "ARA decompressed"]
    candidate_frame = scores[(scores.task == "candidate") & scores.model.isin(core_candidate)].set_index("model")
    baseline_loss = float(candidate_frame.loc["candidate_pnt29", "log_loss_bits"])
    gains = [baseline_loss - float(candidate_frame.loc[name, "log_loss_bits"]) for name in core_candidate]
    axes[0, 0].bar(labels_candidate, gains, color=[grey, grey, grey, blue, blue, gold], edgecolor=ink, linewidth=0.5)
    axes[0, 0].axhline(0, color=ink, linewidth=0.8)
    axes[0, 0].set_title("Candidate-survival gain over PNT29")
    axes[0, 0].set_ylabel("Held-out gain (bits/candidate)")
    axes[0, 0].tick_params(axis="x", rotation=25)

    core_edge = ["edge_hl29", "raw_edge_l64", "ara_edge_b12_l64", "ara_edge_decompressed_b12_l64"]
    labels_edge = ["HL29", "Raw stencil", "ARA endpoints", "ARA decompressed"]
    edge_frame = scores[(scores.task == "edge") & scores.model.isin(core_edge)].set_index("model")
    edge_baseline_loss = float(edge_frame.loc["edge_hl29", "log_loss_bits"])
    edge_gains = [edge_baseline_loss - float(edge_frame.loc[name, "log_loss_bits"]) for name in core_edge]
    axes[0, 1].bar(labels_edge, edge_gains, color=[grey, grey, blue, gold], edgecolor=ink, linewidth=0.5)
    axes[0, 1].axhline(0, color=ink, linewidth=0.8)
    axes[0, 1].set_title("Adjacent-edge survival gain over HL29")
    axes[0, 1].set_ylabel("Held-out gain (bits/edge)")
    axes[0, 1].tick_params(axis="x", rotation=20)

    centers = (locations.start.to_numpy() + locations.end.to_numpy()) / 2 / 1e6
    axes[1, 0].plot(centers, locations.actual_primes, marker="o", color=ink, label="Actual")
    axes[1, 0].plot(centers, locations.pnt29_predicted_primes, linestyle="--", color=grey, label="PNT29")
    axes[1, 0].plot(centers, locations.raw_stencil_predicted_primes, marker="s", color=orange, label="Raw stencil")
    axes[1, 0].plot(centers, locations.ara_i3_predicted_primes, marker="o", color=blue, label="ARA I³")
    axes[1, 0].set_title("Prime-candidate survivor counts by target block")
    axes[1, 0].set_xlabel("Block midpoint (millions)")
    axes[1, 0].set_ylabel("Prime survivors")
    axes[1, 0].legend(frameon=False, ncol=2)

    candidate_blocks = blocks[blocks.task == "candidate"]
    edge_blocks = blocks[blocks.task == "edge"]
    axes[1, 1].plot(candidate_blocks.block, candidate_blocks.delta_bits, marker="o", color=blue, label="Candidate P1")
    axes[1, 1].plot(edge_blocks.block, edge_blocks.delta_bits, marker="s", color=orange, label="Edge P2")
    axes[1, 1].axhline(0, color=ink, linewidth=0.8)
    axes[1, 1].set_title("ARA minus best non-ARA block gain")
    axes[1, 1].set_xlabel("Contiguous target block")
    axes[1, 1].set_ylabel("Gain (bits/event)")
    axes[1, 1].legend(frameon=False)
    fig.suptitle("PN2 fixed-budget prime-survival model comparison", fontsize=16, color=ink)
    fig.savefig(MODEL_FIGURE, dpi=180, bbox_inches="tight")
    plt.close(fig)

    eligible = gap_classes[gap_classes.survivor_edges >= 100]
    fig, ax = plt.subplots(figsize=(13, 7), constrained_layout=True)
    ax.plot(eligible.gap, eligible.survivor_edges, marker="o", color=ink, label="Actual survivors")
    ax.plot(eligible.gap, eligible.hl29_expected_survivors, linestyle="--", marker="s", color=grey, label="HL29")
    ax.plot(eligible.gap, eligible.raw_edge_expected_survivors, marker="s", color=orange, label="Raw stencil")
    ax.plot(eligible.gap, eligible.ara_edge_expected_survivors, marker="o", color=blue, label="ARA endpoints")
    ax.set_title("Adjacent p29-wheel edge survival by gap class")
    ax.set_xlabel("Candidate-edge gap")
    ax.set_ylabel("Surviving consecutive-prime edges")
    ax.legend(frameon=False, ncol=4)
    ax.grid(axis="y", color="#D8DEE5", linewidth=0.7)
    fig.savefig(GAP_FIGURE, dpi=180, bbox_inches="tight")
    plt.close(fig)


def run_development() -> None:
    if sha256_file(PROTOCOL) != PROTOCOL_SHA256:
        raise AssertionError("PN2 protocol hash mismatch")
    development = build_interval(*DEVELOPMENT_INTERVAL)
    registry, diagnostics = build_model_registry(development)
    metadata = {
        "protocol_sha256": PROTOCOL_SHA256,
        "development_interval": DEVELOPMENT_INTERVAL,
        "target_interval_not_accessed": True,
        "sieve_budget_max_prime": 29,
        "candidate_events": int(len(development["labels"])),
        "candidate_primes": int(np.sum(development["labels"])),
        "edge_events": int(len(development["labels"]) - 1),
        "edge_survivors": int(np.sum(development["labels"][:-1] * development["labels"][1:])),
        "model_count": len(registry),
        "diagnostics": diagnostics,
    }
    save_registry(registry, metadata)
    metadata["model_sha256"] = sha256_file(MODEL_PATH)
    write_json(DEV_SUMMARY_PATH, metadata)
    print(json.dumps({"status": "DEVELOPMENT_COMPLETE", "target_accessed": False, "candidate_events": metadata["candidate_events"], "model_sha256": metadata["model_sha256"]}, indent=2))


def validate_target_config() -> dict[str, Any]:
    if not TARGET_CONFIG.exists():
        raise FileNotFoundError("frozen target config is missing")
    config = json.loads(TARGET_CONFIG.read_text(encoding="utf-8"))
    if config["protocol_sha256"] != PROTOCOL_SHA256 or sha256_file(PROTOCOL) != PROTOCOL_SHA256:
        raise AssertionError("protocol hash mismatch")
    if config["analysis_script_sha256"] != sha256_file(Path(__file__).resolve()):
        raise AssertionError("analysis script hash mismatch")
    if config["development_model_sha256"] != sha256_file(MODEL_PATH):
        raise AssertionError("development model hash mismatch")
    if tuple(config["target_interval"]) != TARGET_INTERVAL:
        raise AssertionError("target interval mismatch")
    return config


def run_target() -> None:
    config = validate_target_config()
    registry, metadata = load_registry()
    if not metadata.get("target_interval_not_accessed", False):
        raise AssertionError("development metadata does not preserve target seal")
    target = build_interval(*TARGET_INTERVAL)
    scores, candidate_predictions, edge_predictions, exact_checks = evaluate_registry(target, registry)

    primary_candidate_models = ["candidate_pnt29", "raw_local_l64", "raw_stencil_l64"]
    candidate_score_index = scores[(scores.task == "candidate") & scores.model.isin(primary_candidate_models)].set_index("model")
    best_candidate_nonara = str(candidate_score_index.log_loss_bits.idxmin())
    primary_candidate_ara = "ara_i3_b12_l64"
    candidate_blocks, candidate_bootstrap = bootstrap_delta(
        target["numbers"], target["labels"], candidate_predictions[best_candidate_nonara], candidate_predictions[primary_candidate_ara], *TARGET_INTERVAL
    )
    candidate_blocks.insert(0, "task", "candidate")
    candidate_blocks.insert(1, "baseline_model", best_candidate_nonara)
    candidate_blocks.insert(2, "ara_model", primary_candidate_ara)

    edge_primary = edge_view(target, PRIMARY_BINS)
    primary_edge_models = ["edge_hl29", "raw_edge_l64"]
    edge_score_index = scores[(scores.task == "edge") & scores.model.isin(primary_edge_models)].set_index("model")
    best_edge_nonara = str(edge_score_index.log_loss_bits.idxmin())
    primary_edge_ara = "ara_edge_b12_l64"
    edge_blocks, edge_bootstrap = bootstrap_delta(
        edge_primary["numbers"], edge_primary["labels"], edge_predictions[best_edge_nonara], edge_predictions[primary_edge_ara], *TARGET_INTERVAL
    )
    edge_blocks.insert(0, "task", "edge")
    edge_blocks.insert(1, "baseline_model", best_edge_nonara)
    edge_blocks.insert(2, "ara_model", primary_edge_ara)
    block_table = pd.concat([candidate_blocks, edge_blocks], ignore_index=True)

    gap_table, gap_summary = build_gap_class_table(target, edge_predictions)
    location_table, location_summary = build_location_table(target, candidate_predictions, *TARGET_INTERVAL)

    candidate_bootstrap["baseline_model"] = best_candidate_nonara
    candidate_bootstrap["ara_model"] = primary_candidate_ara
    candidate_bootstrap["support"] = bool(candidate_bootstrap["observed_delta_bits"] > 0 and candidate_bootstrap["bootstrap_lower_95_bits"] > 0)
    edge_bootstrap["baseline_model"] = best_edge_nonara
    edge_bootstrap["ara_model"] = primary_edge_ara
    edge_bootstrap["support"] = bool(edge_bootstrap["observed_delta_bits"] > 0 and edge_bootstrap["bootstrap_lower_95_bits"] > 0)

    results = {
        "test_id": "PN2/PRIME-SURVIVAL/v1",
        "status": "TARGET_COMPLETE",
        "protocol_sha256": PROTOCOL_SHA256,
        "target_config_sha256": sha256_file(TARGET_CONFIG),
        "analysis_script_sha256": sha256_file(Path(__file__).resolve()),
        "development_model_sha256": sha256_file(MODEL_PATH),
        "development_interval": DEVELOPMENT_INTERVAL,
        "target_interval": TARGET_INTERVAL,
        "sieve_budget_max_prime": 29,
        "pn1h_p31_wheel_accessed": False,
        "candidate_events": int(len(target["labels"])),
        "candidate_primes": int(np.sum(target["labels"])),
        "candidate_survival_rate": float(np.mean(target["labels"])),
        "edge_events": int(len(edge_primary["labels"])),
        "edge_survivors": int(np.sum(edge_primary["labels"])),
        "edge_survival_rate": float(np.mean(edge_primary["labels"])),
        "primary_candidate_endpoint": candidate_bootstrap,
        "primary_edge_endpoint": edge_bootstrap,
        "gap_class_frequency": gap_summary,
        "location_calibration": location_summary,
        "exact_checks": exact_checks,
        "allowed_interpretation": "fixed-budget probabilistic survival forecasting only",
        "outputs": {
            "scores": SCORES_PATH.name,
            "blocks": BLOCKS_PATH.name,
            "gap_classes": GAPS_PATH.name,
            "locations": LOCATIONS_PATH.name,
            "target_packet": PACKET_PATH.name,
            "model_figure": MODEL_FIGURE.name,
            "gap_figure": GAP_FIGURE.name,
        },
    }

    scores.to_csv(SCORES_PATH, index=False)
    block_table.to_csv(BLOCKS_PATH, index=False)
    gap_table.to_csv(GAPS_PATH, index=False)
    location_table.to_csv(LOCATIONS_PATH, index=False)
    np.savez_compressed(
        PACKET_PATH,
        numbers=target["numbers"].astype(np.uint32),
        labels=target["labels"].astype(np.uint8),
        gm2=target["gm2"].astype(np.uint8),
        gm1=target["gm1"].astype(np.uint8),
        g0=target["g0"].astype(np.uint8),
        gp1=target["gp1"].astype(np.uint8),
    )
    write_json(RESULTS_PATH, results)
    make_figures(scores, block_table, location_table, gap_table, results)
    print(json.dumps({
        "status": results["status"],
        "candidate_endpoint": candidate_bootstrap,
        "edge_endpoint": edge_bootstrap,
        "candidate_events": results["candidate_events"],
        "edge_events": results["edge_events"],
        "p31_wheel_accessed": False,
    }, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("development", "target"), required=True)
    args = parser.parse_args()
    if args.mode == "development":
        run_development()
    else:
        run_target()


if __name__ == "__main__":
    main()
