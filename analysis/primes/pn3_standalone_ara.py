"""PN3 standalone ARA parent/child prime-survival model.

This file deliberately contains no established analytic prime-density model.
It learns only from opened development intervals, transfers the aggregate rate
between decimal rungs with the frozen ARA rule, and redistributes that total
with local ARA child states under an exact TE-ARA conservation constraint.

Run order:
    python pn3_standalone_ara.py --mode development
    # freeze PN3_TARGET_RUN_CONFIG_v1_FROZEN.json
    python pn3_standalone_ara.py --mode target
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN3_STANDALONE_ARA_PARENT_CHILD_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA256 = "DB6BE581908BA336A02F2481CEAB21FAACEF137F8773E9FC74CCF605E5E5A2EB"
TARGET_CONFIG = HERE / "PN3_TARGET_RUN_CONFIG_v1_FROZEN.json"
MODEL_PATH = HERE / "PN3_STANDALONE_ARA_DEVELOPMENT_MODEL.npz"
DEV_SUMMARY_PATH = HERE / "PN3_STANDALONE_ARA_DEVELOPMENT_SUMMARY.json"
PACKET_PATH = HERE / "PN3_STANDALONE_ARA_TARGET_PACKET.npz"
TARGET_SUMMARY_PATH = HERE / "PN3_STANDALONE_ARA_TARGET_SUMMARY.json"

CONTEXT_MARGIN = 2_000
SIEVE_PRIMES = np.array([2, 3, 5, 7, 11, 13, 17, 19, 23, 29], dtype=np.int64)
RUNG_WINDOWS = {
    "r6": (1_000_000, 1_010_000),
    "r7": (10_000_000, 10_100_000),
    "r8": (100_000_000, 101_000_000),
}
CHILD_INTERVALS = {
    "c7": (10_000_000, 20_000_000),
    "c8": (100_000_000, 110_000_000),
}
TARGET_INTERVAL = (1_000_000_000, 1_010_000_000)
PRIMARY_BINS = 12
SHRINKAGE = 64.0
EPS = 1e-9

CANDIDATE_CHILD_MODELS = (
    "ara_plain_child",
    "ara_i3_child",
    "ara_decompressed_child",
    "raw_pair_child",
    "raw_stencil_child",
)
EDGE_CHILD_MODELS = (
    "ara_endpoints_child",
    "ara_decompressed_edge_child",
    "raw_edge_child",
)


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
        p_int = int(p)
        start = max(p_int * p_int, ((low + p_int - 1) // p_int) * p_int)
        if start < high:
            mask[start - low :: p_int] = False
    return mask


def p29_candidate_mask(low: int, high: int) -> np.ndarray:
    mask = np.ones(high - low, dtype=bool)
    for p in SIEVE_PRIMES:
        start = (-low) % int(p)
        mask[start :: int(p)] = False
    return mask


def ara_coordinate(left_gap: np.ndarray, right_gap: np.ndarray) -> np.ndarray:
    return 2.0 * right_gap.astype(float) / (left_gap.astype(float) + right_gap.astype(float))


def ara_bin(values: np.ndarray, bins: int = PRIMARY_BINS) -> np.ndarray:
    bounded = np.clip(values, 0.0, 2.0 - np.finfo(float).eps)
    return np.minimum((bounded * bins / 2.0).astype(np.uint8), bins - 1)


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


def clip_probability(value: np.ndarray | float) -> np.ndarray:
    return np.clip(np.asarray(value, dtype=float), EPS, 1.0 - EPS)


def logit(value: np.ndarray | float) -> np.ndarray:
    probability = clip_probability(value)
    return np.log(probability / (1.0 - probability))


def logistic(value: np.ndarray | float) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    output = np.empty_like(array, dtype=float)
    positive = array >= 0
    output[positive] = 1.0 / (1.0 + np.exp(-array[positive]))
    exp_value = np.exp(array[~positive])
    output[~positive] = exp_value / (1.0 + exp_value)
    return clip_probability(output)


def build_interval(low: int, high: int) -> dict[str, np.ndarray]:
    extended_low = low - CONTEXT_MARGIN
    extended_high = high + CONTEXT_MARGIN
    candidate_mask = p29_candidate_mask(extended_low, extended_high)
    prime_mask = segmented_prime_mask(extended_low, extended_high)
    candidates = np.flatnonzero(candidate_mask).astype(np.int64) + extended_low
    candidate_is_prime = prime_mask[candidates - extended_low].astype(np.uint8)
    gaps = np.diff(candidates).astype(np.uint8)
    if int(np.max(gaps, initial=0)) >= 64:
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


def candidate_keys(data: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    bprev = ara_bin(data["x_prev"])
    bcurrent = ara_bin(data["x_current"])
    bnext = ara_bin(data["x_next"])
    wprev = data["gm2"].astype(np.uint16) + data["gm1"].astype(np.uint16)
    wcurrent = data["gm1"].astype(np.uint16) + data["g0"].astype(np.uint16)
    wnext = data["g0"].astype(np.uint16) + data["gp1"].astype(np.uint16)
    if max(int(np.max(wprev)), int(np.max(wcurrent)), int(np.max(wnext))) >= 128:
        raise AssertionError("candidate local width exceeded packing range")
    return {
        "ara_plain_child": bcurrent.astype(np.uint64),
        "ara_i3_child": pack_fixed([bprev, bcurrent, bnext], PRIMARY_BINS),
        "ara_decompressed_child": pack_mixed(
            [bprev, bcurrent, bnext, wprev, wcurrent, wnext],
            [PRIMARY_BINS, PRIMARY_BINS, PRIMARY_BINS, 128, 128, 128],
        ),
        "raw_pair_child": pack_fixed([data["gm1"], data["g0"]], 64),
        "raw_stencil_child": pack_fixed([data["gm2"], data["gm1"], data["g0"], data["gp1"]], 64),
    }


def edge_view(data: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    count = len(data["numbers"]) - 1
    bcurrent = ara_bin(data["x_current"][:count])
    bnext = ara_bin(data["x_next"][:count])
    central_gap = data["g0"][:count]
    labels = (data["labels"][:count] * data["labels"][1 : count + 1]).astype(np.uint8)
    if not np.array_equal(data["numbers"][1 : count + 1] - data["numbers"][:count], central_gap.astype(np.int64)):
        raise AssertionError("edge central gap mismatch")
    return {
        "numbers": data["numbers"][:count],
        "labels": labels,
        "central_gap": central_gap,
        "ara_endpoints_child": pack_fixed([bcurrent, bnext], PRIMARY_BINS),
        "ara_decompressed_edge_child": pack_mixed(
            [bcurrent, bnext, central_gap], [PRIMARY_BINS, PRIMARY_BINS, 64]
        ),
        "raw_edge_child": pack_fixed(
            [data["gm1"][:count], central_gap, data["gp1"][:count]], 64
        ),
    }


def interval_aggregates(keys: np.ndarray, labels: np.ndarray, base_rate: float) -> dict[str, np.ndarray]:
    unique, inverse = np.unique(keys, return_inverse=True)
    counts = np.bincount(inverse).astype(np.float64)
    successes = np.bincount(inverse, weights=labels.astype(float))
    posterior = (successes + SHRINKAGE * base_rate) / (counts + SHRINKAGE)
    offsets = logit(posterior) - logit(base_rate)
    return {
        "keys": unique.astype(np.uint64),
        "counts": counts,
        "successes": successes,
        "offsets": offsets.astype(np.float64),
    }


def combine_interval_offsets(parts: list[dict[str, np.ndarray]]) -> dict[str, np.ndarray]:
    all_keys = np.unique(np.concatenate([part["keys"] for part in parts])).astype(np.uint64)
    weighted = np.zeros(len(all_keys), dtype=float)
    total_counts = np.zeros(len(all_keys), dtype=float)
    total_successes = np.zeros(len(all_keys), dtype=float)
    for part in parts:
        positions = np.searchsorted(all_keys, part["keys"])
        weighted[positions] += part["offsets"] * part["counts"]
        total_counts[positions] += part["counts"]
        total_successes[positions] += part["successes"]
    offsets = np.divide(weighted, total_counts, out=np.zeros_like(weighted), where=total_counts > 0)
    return {
        "keys": all_keys,
        "offsets": offsets,
        "counts": total_counts,
        "successes": total_successes,
    }


def apply_state_offsets(keys: np.ndarray, model: dict[str, np.ndarray]) -> tuple[np.ndarray, float]:
    positions = np.searchsorted(model["keys"], keys)
    valid = positions < len(model["keys"])
    matched = np.zeros(len(keys), dtype=bool)
    matched[valid] = model["keys"][positions[valid]] == keys[valid]
    offsets = np.zeros(len(keys), dtype=float)
    offsets[matched] = model["offsets"][positions[matched]]
    return offsets, float(np.mean(matched))


def te_ara_conserved_prediction(base_rate: float, offsets: np.ndarray) -> tuple[np.ndarray, float, float]:
    base_logit = float(logit(base_rate))
    lower, upper = -30.0, 30.0
    for _ in range(100):
        middle = (lower + upper) / 2.0
        mean_prediction = float(np.mean(logistic(base_logit + offsets + middle)))
        if mean_prediction < base_rate:
            lower = middle
        else:
            upper = middle
    intercept = (lower + upper) / 2.0
    prediction = logistic(base_logit + offsets + intercept)
    residual = float(np.mean(prediction) - base_rate)
    if abs(residual) > 1e-12:
        raise AssertionError(f"TE-ARA conservation failed: {residual}")
    return prediction, intercept, residual


def constant_loss(rate: float, labels: np.ndarray) -> float:
    probability = float(clip_probability(rate))
    return float(-np.mean(labels * np.log2(probability) + (1 - labels) * np.log2(1.0 - probability)))


def geometric_transfer(previous: float, current: float) -> float:
    return float(clip_probability((current * current) / previous))


def additive_transfer(previous: float, current: float) -> float:
    return float(clip_probability(2.0 * current - previous))


def log_ols_transfer(rates: list[float]) -> float:
    coordinates = np.arange(len(rates), dtype=float)
    slope, intercept = np.polyfit(coordinates, np.log(np.asarray(rates, dtype=float)), 1)
    return float(clip_probability(np.exp(intercept + slope * len(rates))))


def curvature_transfer(rates: list[float]) -> float:
    r67 = rates[1] / rates[0]
    r78 = rates[2] / rates[1]
    return float(clip_probability(rates[2] * (r78 * r78 / r67)))


def subset_rates(data: dict[str, np.ndarray], low: int, high: int) -> dict[str, float | int]:
    candidate_mask = (data["numbers"] >= low) & (data["numbers"] < high)
    edges = edge_view(data)
    edge_mask = (edges["numbers"] >= low) & (edges["numbers"] < high)
    return {
        "candidate_events": int(np.sum(candidate_mask)),
        "candidate_positives": int(np.sum(data["labels"][candidate_mask])),
        "candidate_rate": float(np.mean(data["labels"][candidate_mask])),
        "edge_events": int(np.sum(edge_mask)),
        "edge_positives": int(np.sum(edges["labels"][edge_mask])),
        "edge_rate": float(np.mean(edges["labels"][edge_mask])),
    }


def save_model_bundle(models: dict[str, dict[str, np.ndarray]], metadata: dict[str, Any]) -> None:
    arrays: dict[str, np.ndarray] = {"metadata_json": np.array(json.dumps(json_ready(metadata), sort_keys=True))}
    for name, model in models.items():
        arrays[f"{name}__keys"] = model["keys"].astype(np.uint64)
        arrays[f"{name}__offsets"] = model["offsets"].astype(np.float64)
        arrays[f"{name}__counts"] = model["counts"].astype(np.float64)
        arrays[f"{name}__successes"] = model["successes"].astype(np.float64)
    np.savez_compressed(MODEL_PATH, **arrays)


def load_model_bundle() -> tuple[dict[str, dict[str, np.ndarray]], dict[str, Any]]:
    archive = np.load(MODEL_PATH, allow_pickle=False)
    metadata = json.loads(str(archive["metadata_json"]))
    models: dict[str, dict[str, np.ndarray]] = {}
    for name in metadata["child_model_names"]:
        models[name] = {
            "keys": archive[f"{name}__keys"],
            "offsets": archive[f"{name}__offsets"],
            "counts": archive[f"{name}__counts"],
            "successes": archive[f"{name}__successes"],
        }
    return models, metadata


def run_development() -> None:
    if sha256_file(PROTOCOL) != PROTOCOL_SHA256:
        raise AssertionError("frozen protocol hash mismatch")
    if TARGET_CONFIG.exists() or PACKET_PATH.exists() or TARGET_SUMMARY_PATH.exists():
        raise AssertionError("target artifacts already exist; development mode refuses to overwrite the freeze boundary")

    interval_parts: dict[str, dict[str, dict[str, np.ndarray]]] = {}
    rung_rates: dict[str, dict[str, float | int]] = {}

    r6_data = build_interval(*RUNG_WINDOWS["r6"])
    rung_rates["r6"] = subset_rates(r6_data, *RUNG_WINDOWS["r6"])
    del r6_data

    for interval_name, interval in CHILD_INTERVALS.items():
        data = build_interval(*interval)
        local_candidate_rate = float(np.mean(data["labels"]))
        edges = edge_view(data)
        local_edge_rate = float(np.mean(edges["labels"]))
        parts: dict[str, dict[str, np.ndarray]] = {}
        for name, keys in candidate_keys(data).items():
            parts[name] = interval_aggregates(keys, data["labels"], local_candidate_rate)
        for name in EDGE_CHILD_MODELS:
            parts[name] = interval_aggregates(edges[name], edges["labels"], local_edge_rate)
        interval_parts[interval_name] = parts
        rung_name = "r7" if interval_name == "c7" else "r8"
        rung_rates[rung_name] = subset_rates(data, *RUNG_WINDOWS[rung_name])
        del data, edges

    child_models: dict[str, dict[str, np.ndarray]] = {}
    for name in CANDIDATE_CHILD_MODELS + EDGE_CHILD_MODELS:
        child_models[name] = combine_interval_offsets(
            [interval_parts["c7"][name], interval_parts["c8"][name]]
        )

    candidate_rates = [float(rung_rates[name]["candidate_rate"]) for name in ("r6", "r7", "r8")]
    edge_rates = [float(rung_rates[name]["edge_rate"]) for name in ("r6", "r7", "r8")]
    candidate_backtest = {
        "actual_r8": candidate_rates[2],
        "ara_from_r6_r7": geometric_transfer(candidate_rates[0], candidate_rates[1]),
        "home_r7": candidate_rates[1],
        "raw_additive_r6_r7": additive_transfer(candidate_rates[0], candidate_rates[1]),
    }
    edge_backtest = {
        "actual_r8": edge_rates[2],
        "ara_from_r6_r7": geometric_transfer(edge_rates[0], edge_rates[1]),
        "home_r7": edge_rates[1],
        "raw_additive_r6_r7": additive_transfer(edge_rates[0], edge_rates[1]),
    }

    for backtest, rate_key in ((candidate_backtest, "candidate"), (edge_backtest, "edge")):
        labels_rate = backtest["actual_r8"]
        backtest["ara_relative_rate_error"] = abs(backtest["ara_from_r6_r7"] - labels_rate) / labels_rate
        # Bernoulli cross-entropy at the observed aggregate rate is sufficient for the parent-only check.
        pseudo_labels = np.array([labels_rate], dtype=float)
        backtest["ara_cross_entropy_bits"] = float(
            -(labels_rate * np.log2(backtest["ara_from_r6_r7"]) + (1 - labels_rate) * np.log2(1 - backtest["ara_from_r6_r7"]))
        )
        backtest["home_cross_entropy_bits"] = float(
            -(labels_rate * np.log2(backtest["home_r7"]) + (1 - labels_rate) * np.log2(1 - backtest["home_r7"]))
        )
        backtest["raw_additive_cross_entropy_bits"] = float(
            -(labels_rate * np.log2(backtest["raw_additive_r6_r7"]) + (1 - labels_rate) * np.log2(1 - backtest["raw_additive_r6_r7"]))
        )

    candidate_parent = {
        "ara": geometric_transfer(candidate_rates[1], candidate_rates[2]),
        "home": candidate_rates[2],
        "raw_additive": additive_transfer(candidate_rates[1], candidate_rates[2]),
        "log_ols_3rung": log_ols_transfer(candidate_rates),
        "ara_curvature": curvature_transfer(candidate_rates),
    }
    edge_parent = {
        "ara": geometric_transfer(edge_rates[1], edge_rates[2]),
        "home": edge_rates[2],
        "raw_additive": additive_transfer(edge_rates[1], edge_rates[2]),
        "log_ols_3rung": log_ols_transfer(edge_rates),
        "ara_curvature": curvature_transfer(edge_rates),
    }

    diagnostics = {}
    for name, model in child_models.items():
        diagnostics[name] = {
            "states": int(len(model["keys"])),
            "singleton_states": int(np.sum(model["counts"] == 1)),
            "minimum_count": int(np.min(model["counts"])),
            "median_count": float(np.median(model["counts"])),
            "maximum_count": int(np.max(model["counts"])),
        }

    metadata = {
        "test_id": "PN3/STANDALONE-ARA-PARENT-CHILD/v1",
        "protocol_sha256": PROTOCOL_SHA256,
        "rung_rates": rung_rates,
        "candidate_parent_predictions": candidate_parent,
        "edge_parent_predictions": edge_parent,
        "candidate_backtest": candidate_backtest,
        "edge_backtest": edge_backtest,
        "child_model_names": list(CANDIDATE_CHILD_MODELS + EDGE_CHILD_MODELS),
        "child_diagnostics": diagnostics,
        "primary_bins": PRIMARY_BINS,
        "shrinkage": SHRINKAGE,
        "target_interval": TARGET_INTERVAL,
        "target_accessed": False,
    }
    save_model_bundle(child_models, metadata)
    summary = dict(metadata)
    summary["model_path"] = str(MODEL_PATH)
    summary["model_sha256"] = sha256_file(MODEL_PATH)
    write_json(DEV_SUMMARY_PATH, summary)
    print(json.dumps(json_ready(summary), indent=2))


def validate_target_config() -> dict[str, Any]:
    config = json.loads(TARGET_CONFIG.read_text(encoding="utf-8"))
    expected = {
        "test_id": "PN3/STANDALONE-ARA-PARENT-CHILD/v1",
        "protocol_sha256": PROTOCOL_SHA256,
        "standalone_script_sha256": sha256_file(Path(__file__)),
        "development_model_sha256": sha256_file(MODEL_PATH),
        "target_low": TARGET_INTERVAL[0],
        "target_high": TARGET_INTERVAL[1],
    }
    for key, value in expected.items():
        if config.get(key) != value:
            raise AssertionError(f"target config mismatch for {key}: {config.get(key)!r} != {value!r}")
    comparison_path = HERE / str(config["comparison_script_name"])
    if sha256_file(comparison_path) != config["comparison_script_sha256"]:
        raise AssertionError("comparison script hash mismatch")
    return config


def run_target() -> None:
    if sha256_file(PROTOCOL) != PROTOCOL_SHA256:
        raise AssertionError("frozen protocol hash mismatch")
    if not TARGET_CONFIG.exists():
        raise FileNotFoundError("freeze the target configuration before target mode")
    if PACKET_PATH.exists() or TARGET_SUMMARY_PATH.exists():
        raise AssertionError("target artifacts already exist; refusing to overwrite a sealed target")
    config = validate_target_config()
    child_models, metadata = load_model_bundle()
    target = build_interval(*TARGET_INTERVAL)
    candidate_state = candidate_keys(target)
    edges = edge_view(target)

    candidate_parent = metadata["candidate_parent_predictions"]
    edge_parent = metadata["edge_parent_predictions"]
    packet: dict[str, np.ndarray] = {
        "metadata_json": np.array(json.dumps({
            "test_id": metadata["test_id"],
            "protocol_sha256": PROTOCOL_SHA256,
            "target_config_sha256": sha256_file(TARGET_CONFIG),
            "target_low": TARGET_INTERVAL[0],
            "target_high": TARGET_INTERVAL[1],
            "candidate_models": [],
            "edge_models": [],
        }, sort_keys=True)),
        "candidate_numbers": target["numbers"].astype(np.int64),
        "candidate_labels": target["labels"].astype(np.uint8),
        "candidate_gm2": target["gm2"].astype(np.uint8),
        "candidate_gm1": target["gm1"].astype(np.uint8),
        "candidate_g0": target["g0"].astype(np.uint8),
        "candidate_gp1": target["gp1"].astype(np.uint8),
        "edge_numbers": edges["numbers"].astype(np.int64),
        "edge_labels": edges["labels"].astype(np.uint8),
        "edge_gaps": edges["central_gap"].astype(np.uint8),
    }
    packet_metadata = json.loads(str(packet["metadata_json"]))
    conservation: dict[str, Any] = {"candidate": {}, "edge": {}}

    candidate_constant_models = {
        "ara_parent_only": candidate_parent["ara"],
        "parent_home": candidate_parent["home"],
        "parent_raw_additive": candidate_parent["raw_additive"],
        "parent_log_ols_3rung": candidate_parent["log_ols_3rung"],
        "parent_ara_curvature": candidate_parent["ara_curvature"],
    }
    for name, rate in candidate_constant_models.items():
        packet[f"candidate_prediction__{name}"] = np.full(len(target["labels"]), rate, dtype=np.float32)
        packet_metadata["candidate_models"].append(name)
    for child_name in CANDIDATE_CHILD_MODELS:
        offsets, match_rate = apply_state_offsets(candidate_state[child_name], child_models[child_name])
        prediction, intercept, residual = te_ara_conserved_prediction(candidate_parent["ara"], offsets)
        full_name = f"ara_parent_{child_name}"
        packet[f"candidate_prediction__{full_name}"] = prediction.astype(np.float32)
        packet_metadata["candidate_models"].append(full_name)
        conservation["candidate"][full_name] = {
            "target_mean": float(candidate_parent["ara"]),
            "actual_mean": float(np.mean(prediction)),
            "residual": residual,
            "label_free_intercept": intercept,
            "state_match_fraction": match_rate,
        }

    edge_constant_models = {
        "ara_parent_only": edge_parent["ara"],
        "parent_home": edge_parent["home"],
        "parent_raw_additive": edge_parent["raw_additive"],
        "parent_log_ols_3rung": edge_parent["log_ols_3rung"],
        "parent_ara_curvature": edge_parent["ara_curvature"],
    }
    for name, rate in edge_constant_models.items():
        packet[f"edge_prediction__{name}"] = np.full(len(edges["labels"]), rate, dtype=np.float32)
        packet_metadata["edge_models"].append(name)
    for child_name in EDGE_CHILD_MODELS:
        offsets, match_rate = apply_state_offsets(edges[child_name], child_models[child_name])
        prediction, intercept, residual = te_ara_conserved_prediction(edge_parent["ara"], offsets)
        full_name = f"ara_parent_{child_name}"
        packet[f"edge_prediction__{full_name}"] = prediction.astype(np.float32)
        packet_metadata["edge_models"].append(full_name)
        conservation["edge"][full_name] = {
            "target_mean": float(edge_parent["ara"]),
            "actual_mean": float(np.mean(prediction)),
            "residual": residual,
            "label_free_intercept": intercept,
            "state_match_fraction": match_rate,
        }

    packet["metadata_json"] = np.array(json.dumps(packet_metadata, sort_keys=True))
    np.savez_compressed(PACKET_PATH, **packet)
    summary = {
        "test_id": metadata["test_id"],
        "protocol_sha256": PROTOCOL_SHA256,
        "target_config": config,
        "target_config_sha256": sha256_file(TARGET_CONFIG),
        "development_model_sha256": sha256_file(MODEL_PATH),
        "packet_path": str(PACKET_PATH),
        "packet_sha256": sha256_file(PACKET_PATH),
        "candidate_events": int(len(target["labels"])),
        "edge_events": int(len(edges["labels"])),
        "candidate_parent_predictions": candidate_parent,
        "edge_parent_predictions": edge_parent,
        "te_ara_conservation": conservation,
        "target_labels_used_for_fitting_or_normalization": False,
    }
    write_json(TARGET_SUMMARY_PATH, summary)
    print(json.dumps(json_ready(summary), indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("development", "target"), required=True)
    arguments = parser.parse_args()
    if arguments.mode == "development":
        run_development()
    else:
        run_target()


if __name__ == "__main__":
    main()
