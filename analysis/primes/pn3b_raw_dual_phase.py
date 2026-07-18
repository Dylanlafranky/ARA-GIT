"""PN3B opened-data raw integer dual-phase diagnostic.

The raw prime/composite sequence is transformed before any sieve control is
applied. Deterministic connection masks are then added as explicit comparison
layers. No p31 primorial-wheel object is generated or accessed.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN3B_RAW_DUAL_PHASE_DIAGNOSTIC_PROTOCOL.md"
PN3_PACKET = HERE / "PN3_STANDALONE_ARA_TARGET_PACKET.npz"
PN3_DEV_SUMMARY = HERE / "PN3_STANDALONE_ARA_DEVELOPMENT_SUMMARY.json"
RESULTS = HERE / "PN3B_RAW_DUAL_PHASE_RESULTS.json"
SPECTRUM_CSV = HERE / "PN3B_DUAL_SPECTRUM.csv"
LADDER_CSV = HERE / "PN3B_CONNECTION_LADDER.csv"
BLOCK_CSV = HERE / "PN3B_BLOCK_PHASE.csv"
GATE_CSV = HERE / "PN3B_POSITION_GATE_MAP.csv"
CROSS_CSV = HERE / "PN3B_CROSS_RUNG_PHASE.csv"
DATA_NPZ = HERE / "PN3B_DUAL_PHASE_DATA.npz"
SPECTRUM_FIGURE = HERE / "PN3B_RAW_DUAL_SPECTRUM.png"
GATE_FIGURE = HERE / "PN3B_PHASE_GATE_MAP.png"

WINDOWS = {
    "r6": (1_000_000, 1_010_000),
    "r7": (10_000_000, 10_100_000),
    "r8": (100_000_000, 101_000_000),
    "r9": (1_000_000_000, 1_010_000_000),
}
SIEVE_BUDGETS = (1, 2, 3, 5, 7, 11, 29, 97, 313, 997)
PRIMARY_BLOCKS = 256
BLOCK_SENSITIVITIES = (128, 512)
LOW_MODES = 64
SPECTRUM_BINS = 512
JOINT_BLOCKS = 128
JOINT_STAGES = 32
PERMUTATIONS = 500
SEED = 20260718

INK = (37, 42, 46)
MUTED = (100, 108, 115)
GRID = (220, 224, 227)
PAPER = (250, 250, 248)
BLUE = (48, 104, 162)
BLUE_OPEN = (153, 188, 220)
ORANGE = (211, 124, 52)
ORANGE_OPEN = (239, 191, 145)
NEUTRAL = (86, 91, 95)
RUNG_COLORS = {
    "r6": (174, 201, 225),
    "r7": (113, 161, 202),
    "r8": (61, 119, 174),
    "r9": (30, 75, 120),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return float(value) if math.isfinite(float(value)) else None
    if isinstance(value, Path):
        return str(value)
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(json_ready(payload), indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path.name}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = list(rows[0])
        for row in rows[1:]:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def simple_primes(limit: int) -> np.ndarray:
    keep = np.ones(limit + 1, dtype=bool)
    keep[:2] = False
    for value in range(2, math.isqrt(limit) + 1):
        if keep[value]:
            keep[value * value :: value] = False
    return np.flatnonzero(keep).astype(np.int64)


def segmented_smallest_factor(low: int, high: int) -> np.ndarray:
    smallest = np.zeros(high - low, dtype=np.uint32)
    for prime_value in simple_primes(math.isqrt(high - 1)):
        prime = int(prime_value)
        start = max(prime * prime, ((low + prime - 1) // prime) * prime)
        if start >= high:
            continue
        view = smallest[start - low :: prime]
        view[view == 0] = prime
    return smallest


def block_sum(values: np.ndarray, blocks: int) -> np.ndarray:
    boundaries = np.floor(np.arange(blocks + 1, dtype=float) * len(values) / blocks).astype(np.int64)
    prefix = np.concatenate(([0.0], np.cumsum(values, dtype=float)))
    return prefix[boundaries[1:]] - prefix[boundaries[:-1]]


def standardized_block_residual(prime_counts: np.ndarray, candidate_counts: np.ndarray) -> np.ndarray:
    total_candidates = float(candidate_counts.sum())
    probability = float(prime_counts.sum() / total_candidates)
    denominator = np.sqrt(np.maximum(probability * (1.0 - probability) * candidate_counts, 1e-15))
    residual = (prime_counts - probability * candidate_counts) / denominator
    residual[candidate_counts <= 0] = 0.0
    return residual


def normalized_power(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    centered = np.asarray(values, dtype=float) - float(np.mean(values))
    coefficients = np.fft.rfft(centered)
    power = np.abs(coefficients) ** 2
    power[0] = 0.0
    total = float(power.sum())
    if total > 0:
        power /= total
    return coefficients, power


def spectral_entropy(power: np.ndarray) -> float:
    positive = power[power > 0]
    if len(positive) <= 1:
        return 0.0
    positive = positive / positive.sum()
    return float(-np.sum(positive * np.log2(positive)) / math.log2(len(power) - 1))


def spectrum_envelope(values: np.ndarray, rung: str, signal: str, hann: bool = False) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    centered = np.asarray(values, dtype=np.float64) - float(np.mean(values))
    if hann:
        centered *= np.hanning(len(centered))
    coefficients = np.fft.rfft(centered)
    power = np.abs(coefficients) ** 2
    power[0] = 0.0
    total = float(power.sum())
    mean_reference = total / max(len(power) - 1, 1)
    maximum_index = len(power) - 1
    raw_edges = np.geomspace(1, maximum_index + 1, SPECTRUM_BINS + 1)
    edges = np.unique(np.clip(np.rint(raw_edges).astype(np.int64), 1, maximum_index + 1))
    rows: list[dict[str, Any]] = []
    for left, right in zip(edges[:-1], edges[1:]):
        if right <= left:
            continue
        segment = power[left:right]
        centre = math.sqrt(left * max(left, right - 1))
        rows.append({
            "rung": rung,
            "signal": signal,
            "window": "hann" if hann else "rectangular",
            "bin_left_k": int(left),
            "bin_right_k": int(right - 1),
            "frequency": centre / len(centered),
            "period": len(centered) / centre,
            "power_fraction": float(segment.sum() / total) if total > 0 else 0.0,
            "normalized_mean_power": float(segment.mean() / mean_reference) if mean_reference > 0 else 0.0,
        })
    low = coefficients[1 : min(129, len(coefficients))]
    low_power = power[1 : min(129, len(power))]
    summary = {
        "variance": float(np.mean(centered * centered)),
        "spectral_entropy": spectral_entropy(power),
        "top_global_mode": int(np.argmax(power[1:]) + 1) if len(power) > 1 else 0,
        "top_global_frequency": float((np.argmax(power[1:]) + 1) / len(centered)) if len(power) > 1 else 0.0,
        "top_low_mode": int(np.argmax(low_power[:LOW_MODES]) + 1) if len(low_power) else 0,
        "top_low_power_fraction": float(np.max(low_power[:LOW_MODES], initial=0.0)),
        "low_coefficients_real": low.real,
        "low_coefficients_imag": low.imag,
    }
    del coefficients, power, centered
    return rows, summary


def draw_nulls(candidate_counts: np.ndarray, prime_counts: np.ndarray, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    total_primes = int(round(float(prime_counts.sum())))
    global_counts = rng.multivariate_hypergeometric(candidate_counts.astype(np.int64), total_primes, size=PERMUTATIONS)
    macro_counts = np.zeros((PERMUTATIONS, len(candidate_counts)), dtype=np.int64)
    macro_size = len(candidate_counts) // 16
    for macro in range(16):
        left = macro * macro_size
        right = len(candidate_counts) if macro == 15 else (macro + 1) * macro_size
        colors = candidate_counts[left:right].astype(np.int64)
        sample = int(round(float(prime_counts[left:right].sum())))
        macro_counts[:, left:right] = rng.multivariate_hypergeometric(colors, sample, size=PERMUTATIONS)
    return global_counts, macro_counts


def null_phase_summary(prime_counts: np.ndarray, candidate_counts: np.ndarray, rng: np.random.Generator) -> dict[str, Any]:
    observed = standardized_block_residual(prime_counts, candidate_counts)
    observed_coefficients, observed_power = normalized_power(observed)
    global_counts, macro_counts = draw_nulls(candidate_counts, prime_counts, rng)
    probability = float(prime_counts.sum() / candidate_counts.sum())
    denominator = np.sqrt(np.maximum(probability * (1.0 - probability) * candidate_counts, 1e-15))

    def transform(draws: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        residual = (draws - probability * candidate_counts[None, :]) / denominator[None, :]
        residual -= residual.mean(axis=1, keepdims=True)
        coefficients = np.fft.rfft(residual, axis=1)
        power = np.abs(coefficients) ** 2
        power[:, 0] = 0.0
        totals = power.sum(axis=1, keepdims=True)
        power = np.divide(power, totals, out=np.zeros_like(power), where=totals > 0)
        return coefficients, power

    global_coefficients, global_power = transform(global_counts)
    macro_coefficients, macro_power = transform(macro_counts)
    observed_max = float(np.max(observed_power[1 : LOW_MODES + 1]))
    global_max = np.max(global_power[:, 1 : LOW_MODES + 1], axis=1)
    macro_max = np.max(macro_power[:, 1 : LOW_MODES + 1], axis=1)
    return {
        "observed_z": observed,
        "observed_coefficients": observed_coefficients,
        "observed_power": observed_power,
        "global_coefficients": global_coefficients,
        "global_power": global_power,
        "macro_coefficients": macro_coefficients,
        "macro_power": macro_power,
        "top_mode": int(np.argmax(observed_power[1 : LOW_MODES + 1]) + 1),
        "top_power": observed_max,
        "global_familywise_p": float((1 + np.sum(global_max >= observed_max)) / (PERMUTATIONS + 1)),
        "macro_familywise_p": float((1 + np.sum(macro_max >= observed_max)) / (PERMUTATIONS + 1)),
        "global_99_max": float(np.quantile(global_max, 0.99)),
        "macro_99_max": float(np.quantile(macro_max, 0.99)),
        "global_mode_99": np.quantile(global_power[:, 1 : LOW_MODES + 1], 0.99, axis=0),
        "macro_mode_99": np.quantile(macro_power[:, 1 : LOW_MODES + 1], 0.99, axis=0),
    }


def joint_gate_map(candidate_mask: np.ndarray, prime_mask: np.ndarray, smallest: np.ndarray, high: int, rng: np.random.Generator) -> dict[str, Any]:
    candidate_indices = np.flatnonzero(candidate_mask)
    candidate_smallest = smallest[candidate_indices]
    blocks = np.minimum((candidate_indices.astype(np.int64) * JOINT_BLOCKS // len(candidate_mask)), JOINT_BLOCKS - 1)
    stages = np.full(len(candidate_indices), JOINT_STAGES, dtype=np.int64)
    composite = candidate_smallest > 0
    denominator = math.log(math.sqrt(high - 1) / 31.0)
    progress = np.log(candidate_smallest[composite].astype(float) / 31.0) / denominator
    stages[composite] = np.minimum((np.clip(progress, 0.0, 1.0 - np.finfo(float).eps) * JOINT_STAGES).astype(np.int64), JOINT_STAGES - 1)
    matrix = np.bincount(blocks * (JOINT_STAGES + 1) + stages, minlength=JOINT_BLOCKS * (JOINT_STAGES + 1)).reshape(JOINT_BLOCKS, JOINT_STAGES + 1)
    row = matrix.sum(axis=1).astype(float)
    column = matrix.sum(axis=0).astype(float)
    expected = np.outer(row, column) / matrix.sum()
    residual = np.divide(matrix - expected, np.sqrt(expected), out=np.zeros_like(expected), where=expected > 0)
    singular_u, singular_s, singular_vh = np.linalg.svd(residual, full_matrices=False)
    probability = matrix / matrix.sum()
    independent = np.outer(row / row.sum(), column / column.sum())
    positive = probability > 0
    mutual_information = float(np.sum(probability[positive] * np.log2(probability[positive] / independent[positive])))
    leading_energy = float(singular_s[0] ** 2 / np.sum(singular_s ** 2)) if np.sum(singular_s ** 2) > 0 else 0.0

    null_mi = np.empty(PERMUTATIONS, dtype=float)
    null_leading = np.empty(PERMUTATIONS, dtype=float)
    null_u = np.empty((PERMUTATIONS, JOINT_BLOCKS), dtype=float)
    null_v = np.empty((PERMUTATIONS, JOINT_STAGES + 1), dtype=float)
    shuffled_stages = stages.copy()
    for simulation in range(PERMUTATIONS):
        rng.shuffle(shuffled_stages)
        simulated = np.bincount(
            blocks * (JOINT_STAGES + 1) + shuffled_stages,
            minlength=JOINT_BLOCKS * (JOINT_STAGES + 1),
        ).reshape(JOINT_BLOCKS, JOINT_STAGES + 1)
        simulated_row = simulated.sum(axis=1).astype(float)
        simulated_expected = np.outer(simulated_row, column) / simulated.sum()
        simulated_residual = np.divide(simulated - simulated_expected, np.sqrt(simulated_expected), out=np.zeros_like(simulated_expected), where=simulated_expected > 0)
        u0, s0, vh0 = np.linalg.svd(simulated_residual, full_matrices=False)
        simulated_probability = simulated / simulated.sum()
        simulated_independent = np.outer(simulated_row / simulated_row.sum(), column / column.sum())
        mask = simulated_probability > 0
        null_mi[simulation] = np.sum(simulated_probability[mask] * np.log2(simulated_probability[mask] / simulated_independent[mask]))
        null_leading[simulation] = s0[0] ** 2 / np.sum(s0 ** 2) if np.sum(s0 ** 2) > 0 else 0.0
        null_u[simulation] = u0[:, 0]
        null_v[simulation] = vh0[0]
    return {
        "matrix": matrix,
        "expected": expected,
        "pearson_residual": residual,
        "mutual_information_bits": mutual_information,
        "leading_energy_fraction": leading_energy,
        "leading_spatial_mode": singular_u[:, 0],
        "leading_gate_mode": singular_vh[0],
        "singular_values": singular_s,
        "mi_p": float((1 + np.sum(null_mi >= mutual_information)) / (PERMUTATIONS + 1)),
        "leading_energy_p": float((1 + np.sum(null_leading >= leading_energy)) / (PERMUTATIONS + 1)),
        "null_mi": null_mi,
        "null_leading": null_leading,
        "null_u": null_u,
        "null_v": null_v,
        "candidate_count": int(candidate_mask.sum()),
        "prime_count": int(prime_mask.sum()),
    }


def phase_pair_metrics(first: dict[str, Any], second: dict[str, Any], null_kind: str) -> dict[str, Any]:
    first_z = first["observed_z"]
    second_z = second["observed_z"]
    first_coefficients = first["observed_coefficients"][1 : LOW_MODES + 1]
    second_coefficients = second["observed_coefficients"][1 : LOW_MODES + 1]
    first_power = first["observed_power"][1 : LOW_MODES + 1]
    second_power = second["observed_power"][1 : LOW_MODES + 1]
    def safe_correlation(a: np.ndarray, b: np.ndarray) -> float:
        centred_a = a - np.mean(a)
        centred_b = b - np.mean(b)
        denominator = math.sqrt(float(np.sum(centred_a * centred_a) * np.sum(centred_b * centred_b)))
        return float(np.sum(centred_a * centred_b) / denominator) if denominator > 0 else float("nan")

    position_signed = safe_correlation(first_z, second_z)
    power_correlation = safe_correlation(np.log(first_power + 1e-15), np.log(second_power + 1e-15))
    observed_denominator = math.sqrt(float(np.vdot(first_coefficients, first_coefficients).real * np.vdot(second_coefficients, second_coefficients).real))
    phase_coherence = float(abs(np.vdot(second_coefficients, first_coefficients)) / observed_denominator) if observed_denominator > 0 else float("nan")

    key = "global" if null_kind == "global" else "macro"
    first_null_z = np.fft.irfft(first[f"{key}_coefficients"], n=len(first_z), axis=1)
    second_null_z = np.fft.irfft(second[f"{key}_coefficients"], n=len(second_z), axis=1)
    first_null_coeff = first[f"{key}_coefficients"][:, 1 : LOW_MODES + 1]
    second_null_coeff = second[f"{key}_coefficients"][:, 1 : LOW_MODES + 1]
    first_null_power = first[f"{key}_power"][:, 1 : LOW_MODES + 1]
    second_null_power = second[f"{key}_power"][:, 1 : LOW_MODES + 1]
    first_null_centred = first_null_z - first_null_z.mean(axis=1, keepdims=True)
    second_null_centred = second_null_z - second_null_z.mean(axis=1, keepdims=True)
    position_denominator = np.sqrt(np.sum(first_null_centred ** 2, axis=1) * np.sum(second_null_centred ** 2, axis=1))
    null_position = np.divide(np.abs(np.sum(first_null_centred * second_null_centred, axis=1)), position_denominator, out=np.full(PERMUTATIONS, np.nan), where=position_denominator > 0)
    null_power_correlation = np.array([safe_correlation(np.log(a + 1e-15), np.log(b + 1e-15)) for a, b in zip(first_null_power, second_null_power)])
    numerator = np.abs(np.sum(first_null_coeff * np.conj(second_null_coeff), axis=1))
    coherence_denominator = np.sqrt(np.sum(np.abs(first_null_coeff) ** 2, axis=1) * np.sum(np.abs(second_null_coeff) ** 2, axis=1))
    null_coherence = np.divide(numerator, coherence_denominator, out=np.zeros_like(numerator), where=coherence_denominator > 0)
    def empirical_p(null_values: np.ndarray, observed: float) -> float:
        finite = null_values[np.isfinite(null_values)]
        if not math.isfinite(observed) or len(finite) == 0:
            return 1.0
        return float((1 + np.sum(finite >= observed)) / (len(finite) + 1))

    finite_coherence = null_coherence[np.isfinite(null_coherence)]
    return {
        "position_signed_correlation": position_signed,
        "position_absolute_correlation": abs(position_signed),
        "position_p": empirical_p(null_position, abs(position_signed)),
        "power_log_correlation": power_correlation,
        "power_p": empirical_p(null_power_correlation, power_correlation),
        "phase_coherence": phase_coherence,
        "phase_p": empirical_p(null_coherence, phase_coherence),
        "phase_null_99": float(np.quantile(finite_coherence, 0.99)) if len(finite_coherence) else float("nan"),
    }


def gate_pair_metrics(first: dict[str, Any], second: dict[str, Any]) -> dict[str, Any]:
    spatial = float(abs(np.dot(first["leading_spatial_mode"], second["leading_spatial_mode"])))
    gate = float(abs(np.dot(first["leading_gate_mode"], second["leading_gate_mode"])))
    null_spatial = np.abs(np.sum(first["null_u"] * second["null_u"], axis=1))
    null_gate = np.abs(np.sum(first["null_v"] * second["null_v"], axis=1))
    return {
        "spatial_alignment": spatial,
        "spatial_p": float((1 + np.sum(null_spatial >= spatial)) / (PERMUTATIONS + 1)),
        "spatial_null_99": float(np.quantile(null_spatial, 0.99)),
        "gate_alignment": gate,
        "gate_p": float((1 + np.sum(null_gate >= gate)) / (PERMUTATIONS + 1)),
        "gate_null_99": float(np.quantile(null_gate, 0.99)),
    }


def analyze_rung(name: str, low: int, high: int, rng: np.random.Generator, packet: Any, development: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    smallest = segmented_smallest_factor(low, high)
    prime_mask = smallest == 0
    raw_integer_count = high - low
    raw_prime_count = int(prime_mask.sum())
    masks = {budget: (smallest == 0) | (smallest > budget) for budget in SIEVE_BUDGETS}
    p29_mask = masks[29]
    checks: dict[str, bool] = {"raw_prime_subset_p29": bool(np.all(p29_mask[prime_mask]))}
    if name == "r9":
        numbers = packet["candidate_numbers"].astype(np.int64)
        checks["r9_candidate_numbers"] = np.array_equal(np.flatnonzero(p29_mask).astype(np.int64) + low, numbers)
        checks["r9_candidate_labels"] = np.array_equal(prime_mask[numbers - low].astype(np.uint8), packet["candidate_labels"])
    else:
        recorded = development["rung_rates"][name]
        checks["development_candidate_count"] = int(p29_mask.sum()) == int(recorded["candidate_events"])
        checks["development_prime_count"] = raw_prime_count == int(recorded["candidate_positives"])

    spectrum_rows: list[dict[str, Any]] = []
    spectrum_summaries: dict[str, Any] = {}
    raw_values = prime_mask.astype(np.float64)
    p29_probability = raw_prime_count / int(p29_mask.sum())
    q997_mask = masks[997]
    q997_probability = raw_prime_count / int(q997_mask.sum())
    signals = {
        "raw_prime_indicator": raw_values,
        "p29_connection_mask": p29_mask.astype(np.float64),
        "p29_connection_residual": raw_values - p29_probability * p29_mask,
        "q997_connection_residual": raw_values - q997_probability * q997_mask,
    }
    for signal_name, signal_values in signals.items():
        rows, summary = spectrum_envelope(signal_values, name, signal_name)
        spectrum_rows.extend(rows)
        spectrum_summaries[signal_name] = summary
    if name == "r9":
        for signal_name in ("raw_prime_indicator", "p29_connection_residual"):
            rows, summary = spectrum_envelope(signals[signal_name], name, signal_name, hann=True)
            spectrum_rows.extend(rows)
            spectrum_summaries[f"{signal_name}_hann"] = summary

    ladder_rows: list[dict[str, Any]] = []
    raw_variance = float(np.var(raw_values))
    ladder_summary: dict[str, Any] = {}
    for budget in SIEVE_BUDGETS:
        mask = masks[budget]
        probability = raw_prime_count / int(mask.sum())
        residual = raw_values - probability * mask
        candidate_counts = block_sum(mask.astype(float), PRIMARY_BLOCKS)
        prime_counts = block_sum(raw_values, PRIMARY_BLOCKS)
        z = standardized_block_residual(prime_counts, candidate_counts)
        _, phase_power = normalized_power(z)
        top_mode = int(np.argmax(phase_power[1 : LOW_MODES + 1]) + 1)
        row = {
            "rung": name,
            "budget": budget,
            "surviving_mask_events": int(mask.sum()),
            "conditional_prime_rate": probability,
            "variance_explained": float(1.0 - np.var(residual) / raw_variance),
            "top_low_mode": top_mode,
            "top_low_power_fraction": float(phase_power[top_mode]),
            "block_phase_entropy": spectral_entropy(phase_power),
        }
        ladder_rows.append(row)
        ladder_summary[str(budget)] = row

    block_rows: list[dict[str, Any]] = []
    block_diagnostics: dict[str, Any] = {}
    sensitivity: dict[str, Any] = {}
    for budget in (29, 997):
        mask = masks[budget]
        candidate_counts = block_sum(mask.astype(float), PRIMARY_BLOCKS)
        prime_counts = block_sum(raw_values, PRIMARY_BLOCKS)
        diagnostic = null_phase_summary(prime_counts, candidate_counts, rng)
        block_diagnostics[str(budget)] = diagnostic
        for block in range(PRIMARY_BLOCKS):
            block_rows.append({
                "rung": name,
                "budget": budget,
                "block": block,
                "progress": (block + 0.5) / PRIMARY_BLOCKS,
                "candidate_events": int(round(candidate_counts[block])),
                "prime_events": int(round(prime_counts[block])),
                "standardized_residual": float(diagnostic["observed_z"][block]),
            })
    for blocks in BLOCK_SENSITIVITIES:
        candidate_counts = block_sum(p29_mask.astype(float), blocks)
        prime_counts = block_sum(raw_values, blocks)
        z = standardized_block_residual(prime_counts, candidate_counts)
        _, power = normalized_power(z)
        sensitivity[str(blocks)] = {
            "top_mode": int(np.argmax(power[1 : min(LOW_MODES + 1, len(power))]) + 1),
            "top_power": float(np.max(power[1 : min(LOW_MODES + 1, len(power))], initial=0.0)),
            "entropy": spectral_entropy(power),
        }

    gate = joint_gate_map(p29_mask, prime_mask, smallest, high, rng)
    gate_rows: list[dict[str, Any]] = []
    for block in range(JOINT_BLOCKS):
        for stage in range(JOINT_STAGES + 1):
            gate_rows.append({
                "rung": name,
                "position_block": block,
                "position_progress": (block + 0.5) / JOINT_BLOCKS,
                "gate_stage": stage,
                "gate_progress": 1.0 if stage == JOINT_STAGES else (stage + 0.5) / JOINT_STAGES,
                "survivor_class": stage == JOINT_STAGES,
                "observed_count": int(gate["matrix"][block, stage]),
                "expected_count": float(gate["expected"][block, stage]),
                "pearson_residual": float(gate["pearson_residual"][block, stage]),
            })

    summary = {
        "interval": [low, high],
        "raw_integer_events": raw_integer_count,
        "raw_prime_events": raw_prime_count,
        "raw_prime_rate": raw_prime_count / raw_integer_count,
        "p29_candidate_events": int(p29_mask.sum()),
        "p29_conditional_prime_rate": p29_probability,
        "q997_candidate_events": int(q997_mask.sum()),
        "q997_conditional_prime_rate": q997_probability,
        "checks": checks,
        "spectrum": spectrum_summaries,
        "post_result_connection_line_crosswalk": {
            "q29_residual_top_frequency": spectrum_summaries["p29_connection_residual"]["top_global_frequency"],
            "period_62_harmonic": int(round(spectrum_summaries["p29_connection_residual"]["top_global_frequency"] * 62.0)),
            "period_62_frequency": int(round(spectrum_summaries["p29_connection_residual"]["top_global_frequency"] * 62.0)) / 62.0,
            "absolute_frequency_error": abs(
                spectrum_summaries["p29_connection_residual"]["top_global_frequency"]
                - int(round(spectrum_summaries["p29_connection_residual"]["top_global_frequency"] * 62.0)) / 62.0
            ),
            "within_one_fourier_bin": abs(
                spectrum_summaries["p29_connection_residual"]["top_global_frequency"]
                - int(round(spectrum_summaries["p29_connection_residual"]["top_global_frequency"] * 62.0)) / 62.0
            ) <= 1.0 / raw_integer_count,
            "interpretation": "post-result arithmetic crosswalk to 2 x 31; not a registered endpoint",
        },
        "connection_ladder": ladder_summary,
        "block_phase": block_diagnostics,
        "block_sensitivity": sensitivity,
        "joint_gate": gate,
    }
    del smallest, prime_mask, masks, signals, raw_values
    return summary, spectrum_rows, ladder_rows, block_rows, gate_rows


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def panel_title(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, subtitle: str) -> tuple[int, int, int, int]:
    left, top, right, bottom = box
    draw.text((left, top), title, fill=INK, font=font(20, True))
    draw.text((left, top + 27), subtitle, fill=MUTED, font=font(13))
    return left + 70, top + 72, right - 18, bottom - 45


def draw_line_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    subtitle: str,
    series: list[dict[str, Any]],
    x_log: bool = False,
    y_log: bool = False,
    y_zero: bool = False,
    x_label: str = "Ordered coordinate",
    y_label: str = "Value",
) -> None:
    x0, y0, x1, y1 = panel_title(draw, box, title, subtitle)
    all_x = np.concatenate([np.asarray(item["x"], dtype=float) for item in series])
    all_y = np.concatenate([np.asarray(item["y"], dtype=float) for item in series])
    if x_log:
        all_x = np.log10(np.maximum(all_x, 1e-300))
    if y_log:
        all_y = np.log10(np.maximum(all_y, 1e-300))
    xmin, xmax = float(np.min(all_x)), float(np.max(all_x))
    ymin, ymax = float(np.min(all_y)), float(np.max(all_y))
    if y_zero and not y_log:
        ymin = min(0.0, ymin)
    if ymax <= ymin:
        ymax = ymin + 1.0
    for fraction in np.linspace(0, 1, 5):
        y = y1 - fraction * (y1 - y0)
        draw.line((x0, y, x1, y), fill=GRID, width=1)
        value = ymin + fraction * (ymax - ymin)
        label = f"{10 ** value:.1e}" if y_log else f"{value:.2g}"
        draw.text((x0 - 62, y - 7), label, fill=MUTED, font=font(10))
    draw.line((x0, y0, x0, y1), fill=INK, width=2)
    draw.line((x0, y1, x1, y1), fill=INK, width=2)
    for fraction in np.linspace(0, 1, 5):
        x_position = x0 + fraction * (x1 - x0)
        value = xmin + fraction * (xmax - xmin)
        label = f"{10 ** value:.2g}" if x_log else f"{value:.2g}"
        draw.line((x_position, y1, x_position, y1 + 5), fill=INK, width=1)
        draw.text((x_position - 18, y1 + 8), label, fill=MUTED, font=font(10))
    draw.text(((x0 + x1) / 2 - 55, y1 + 25), x_label, fill=MUTED, font=font(11))
    legend_x = x0
    for item in series:
        x = np.asarray(item["x"], dtype=float)
        y = np.asarray(item["y"], dtype=float)
        if x_log:
            x = np.log10(np.maximum(x, 1e-300))
        if y_log:
            y = np.log10(np.maximum(y, 1e-300))
        px = x0 + (x - xmin) / max(xmax - xmin, 1e-15) * (x1 - x0)
        py = y1 - (y - ymin) / (ymax - ymin) * (y1 - y0)
        points = [(float(a), float(b)) for a, b in zip(px, py) if math.isfinite(a) and math.isfinite(b)]
        if len(points) >= 2:
            draw.line(points, fill=item["color"], width=item.get("width", 3))
        draw.line((legend_x, y0 - 19, legend_x + 24, y0 - 19), fill=item["color"], width=4)
        draw.text((legend_x + 30, y0 - 27), item["label"], fill=INK, font=font(11))
        legend_x += 145


def diverging_color(value: float, maximum: float) -> tuple[int, int, int]:
    if not math.isfinite(value):
        return (235, 235, 232)
    strength = min(abs(value) / max(maximum, 1e-12), 1.0)
    target = ORANGE if value >= 0 else BLUE
    return tuple(int(PAPER[index] * (1.0 - strength) + target[index] * strength) for index in range(3))


def draw_heatmap(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, subtitle: str, matrix: np.ndarray, maximum: float) -> None:
    x0, y0, x1, y1 = panel_title(draw, box, title, subtitle)
    rows, columns = matrix.shape
    cell_width = (x1 - x0) / columns
    cell_height = (y1 - y0) / rows
    for row in range(rows):
        for column in range(columns):
            left = x0 + column * cell_width
            top = y0 + row * cell_height
            draw.rectangle((left, top, left + cell_width + 1, top + cell_height + 1), fill=diverging_color(float(matrix[row, column]), maximum))
    draw.rectangle((x0, y0, x1, y1), outline=INK, width=2)
    draw.text((x0, y1 + 10), "future gate stage -> survivor", fill=MUTED, font=font(11))
    draw.text((x0 - 58, y0 + (y1 - y0) / 2), "number", fill=MUTED, font=font(11))


def make_figures(spectrum_rows: list[dict[str, Any]], ladder_rows: list[dict[str, Any]], summaries: dict[str, Any], cross_rows: list[dict[str, Any]]) -> None:
    image = Image.new("RGB", (1600, 1180), PAPER)
    draw = ImageDraw.Draw(image)
    draw.text((45, 24), "PN3B raw integer dual spectrum", fill=INK, font=font(31, True))
    draw.text((45, 64), "Complete opened integer sequence first; connection masks and residuals shown separately", fill=MUTED, font=font(17))
    panels = [(45, 110, 785, 590), (815, 110, 1555, 590), (45, 630, 785, 1135), (815, 630, 1555, 1135)]
    signal_style = {
        "raw_prime_indicator": ("Raw prime indicator", NEUTRAL),
        "p29_connection_mask": ("p29 mask", ORANGE),
        "p29_connection_residual": ("Residual Q29", BLUE),
        "q997_connection_residual": ("Residual Q997", BLUE_OPEN),
    }
    spectral_series = []
    for signal, (label, color) in signal_style.items():
        selected = [row for row in spectrum_rows if row["rung"] == "r9" and row["signal"] == signal and row["window"] == "rectangular"]
        spectral_series.append({"label": label, "color": color, "x": [row["period"] for row in selected], "y": [row["normalized_mean_power"] for row in selected]})
    draw_line_panel(draw, panels[0], "R9 full dual spectrum", "Normalized mean spectral power; logarithmic period and power", spectral_series, x_log=True, y_log=True, x_label="Period (integers)", y_label="Normalized spectral power")

    ladder_series = []
    for rung in ("r7", "r8", "r9"):
        selected = [row for row in ladder_rows if row["rung"] == rung]
        ladder_series.append({"label": rung.upper(), "color": RUNG_COLORS[rung], "x": [row["budget"] for row in selected], "y": [row["variance_explained"] for row in selected]})
    draw_line_panel(draw, panels[1], "Connection ladder", "Fraction of raw prime-indicator variance captured as sieve budget rises", ladder_series, x_log=True, y_zero=True, x_label="Sieve budget Q", y_label="Variance fraction")

    block_series = []
    for budget, color in ((29, BLUE), (997, ORANGE)):
        diagnostic = summaries["r9"]["block_phase"][str(budget)]
        block_series.append({"label": f"Q{budget} residual", "color": color, "x": (np.arange(PRIMARY_BLOCKS) + 0.5) / PRIMARY_BLOCKS, "y": diagnostic["observed_z"]})
    draw_line_panel(draw, panels[2], "R9 scale-normalized phase path", "Standardized prime excess in 256 equal number-line cells", block_series, y_zero=True, x_label="Window progress", y_label="Standardized residual")

    diagnostic = summaries["r9"]["block_phase"]["29"]
    modes = np.arange(1, LOW_MODES + 1)
    mode_series = [
        {"label": "Observed Q29", "color": BLUE, "x": modes, "y": diagnostic["observed_power"][1 : LOW_MODES + 1]},
        {"label": "Global-null 99%", "color": NEUTRAL, "x": modes, "y": diagnostic["global_mode_99"]},
        {"label": "Macro-null 99%", "color": ORANGE_OPEN, "x": modes, "y": diagnostic["macro_mode_99"]},
    ]
    draw_line_panel(draw, panels[3], "R9 low phase modes", "Per-mode normalized power compared with conditional nulls", mode_series, y_zero=True, x_label="Scaled Fourier mode", y_label="Power fraction")
    image.save(SPECTRUM_FIGURE)

    image = Image.new("RGB", (1600, 1180), PAPER)
    draw = ImageDraw.Draw(image)
    draw.text((45, 24), "PN3B phase x future-gate map", fill=INK, font=font(31, True))
    draw.text((45, 64), "Pearson residual after removing independent position and death-stage margins", fill=MUTED, font=font(17))
    panels = [(45, 110, 785, 590), (815, 110, 1555, 590), (45, 630, 785, 1135), (815, 630, 1555, 1135)]
    maximum = max(float(np.quantile(np.abs(summaries[rung]["joint_gate"]["pearson_residual"]), 0.99)) for rung in ("r8", "r9"))
    draw_heatmap(draw, panels[0], "R8 joint gate map", "128 number cells x 32 log-sieve stages plus survivors", summaries["r8"]["joint_gate"]["pearson_residual"], maximum)
    draw_heatmap(draw, panels[1], "R9 joint gate map", "Same axes and shared signed scale as R8", summaries["r9"]["joint_gate"]["pearson_residual"], maximum)
    spatial_series = [
        {"label": rung.upper(), "color": RUNG_COLORS[rung], "x": (np.arange(JOINT_BLOCKS) + 0.5) / JOINT_BLOCKS, "y": summaries[rung]["joint_gate"]["leading_spatial_mode"]}
        for rung in ("r7", "r8", "r9")
    ]
    draw_line_panel(draw, panels[2], "Leading number-line mode", "Sign is arbitrary; recurrence requires sign-invariant alignment", spatial_series, y_zero=True, x_label="Window progress", y_label="SVD loading")
    gate_series = [
        {"label": rung.upper(), "color": RUNG_COLORS[rung], "x": np.arange(JOINT_STAGES + 1), "y": summaries[rung]["joint_gate"]["leading_gate_mode"]}
        for rung in ("r7", "r8", "r9")
    ]
    draw_line_panel(draw, panels[3], "Leading future-gate mode", "Stages 0-31 are later-factor death; final stage is survival", gate_series, y_zero=True, x_label="Gate stage", y_label="SVD loading")
    image.save(GATE_FIGURE)


def compact_summary(summary: dict[str, Any]) -> dict[str, Any]:
    output = dict(summary)
    output["spectrum"] = {
        name: {key: value for key, value in values.items() if not key.startswith("low_coefficients")}
        for name, values in summary["spectrum"].items()
    }
    output["block_phase"] = {
        budget: {
            key: value
            for key, value in diagnostic.items()
            if key in ("top_mode", "top_power", "global_familywise_p", "macro_familywise_p", "global_99_max", "macro_99_max")
        }
        for budget, diagnostic in summary["block_phase"].items()
    }
    gate = summary["joint_gate"]
    output["joint_gate"] = {
        "mutual_information_bits": gate["mutual_information_bits"],
        "leading_energy_fraction": gate["leading_energy_fraction"],
        "mi_p": gate["mi_p"],
        "leading_energy_p": gate["leading_energy_p"],
        "candidate_count": gate["candidate_count"],
        "prime_count": gate["prime_count"],
    }
    return output


def run() -> dict[str, Any]:
    protocol_sha = sha256_file(PROTOCOL)
    packet_sha = sha256_file(PN3_PACKET)
    packet = np.load(PN3_PACKET, allow_pickle=False)
    development = json.loads(PN3_DEV_SUMMARY.read_text(encoding="utf-8"))
    rng = np.random.default_rng(SEED)
    summaries: dict[str, Any] = {}
    spectrum_rows: list[dict[str, Any]] = []
    ladder_rows: list[dict[str, Any]] = []
    block_rows: list[dict[str, Any]] = []
    gate_rows: list[dict[str, Any]] = []
    for name, (low, high) in WINDOWS.items():
        summary, rung_spectrum, rung_ladder, rung_blocks, rung_gate = analyze_rung(name, low, high, rng, packet, development)
        summaries[name] = summary
        spectrum_rows.extend(rung_spectrum)
        ladder_rows.extend(rung_ladder)
        block_rows.extend(rung_blocks)
        gate_rows.extend(rung_gate)

    cross_rows: list[dict[str, Any]] = []
    cross_summary: dict[str, Any] = {}
    for first_name, second_name in (("r6", "r7"), ("r7", "r8"), ("r8", "r9")):
        for budget in (29, 997):
            for null_kind in ("global", "macro"):
                metrics = phase_pair_metrics(summaries[first_name]["block_phase"][str(budget)], summaries[second_name]["block_phase"][str(budget)], null_kind)
                row = {"first_rung": first_name, "second_rung": second_name, "analysis": "block_phase", "budget": budget, "null": null_kind, **metrics}
                cross_rows.append(row)
                cross_summary[f"{first_name}_to_{second_name}__q{budget}__{null_kind}"] = metrics
        gate_metrics = gate_pair_metrics(summaries[first_name]["joint_gate"], summaries[second_name]["joint_gate"])
        row = {"first_rung": first_name, "second_rung": second_name, "analysis": "joint_gate", "budget": "", "null": "multinomial", **gate_metrics}
        cross_rows.append(row)
        cross_summary[f"{first_name}_to_{second_name}__joint_gate"] = gate_metrics

    r8_q29 = summaries["r8"]["block_phase"]["29"]
    r9_q29 = summaries["r9"]["block_phase"]["29"]
    r8_q997 = summaries["r8"]["block_phase"]["997"]
    r9_q997 = summaries["r9"]["block_phase"]["997"]
    phase_cross = cross_summary["r8_to_r9__q29__global"]
    phase_cross_macro = cross_summary["r8_to_r9__q29__macro"]
    gate_cross = cross_summary["r8_to_r9__joint_gate"]
    candidate_time_like = bool(
        r8_q29["global_familywise_p"] <= 0.01
        and r9_q29["global_familywise_p"] <= 0.01
        and phase_cross["phase_p"] <= 0.01
        and phase_cross_macro["phase_p"] <= 0.01
        and r8_q997["global_familywise_p"] <= 0.01
        and r9_q997["global_familywise_p"] <= 0.01
        and summaries["r8"]["joint_gate"]["leading_energy_p"] <= 0.01
        and summaries["r9"]["joint_gate"]["leading_energy_p"] <= 0.01
        and gate_cross["spatial_p"] <= 0.01
        and gate_cross["gate_p"] <= 0.01
    )

    write_csv(SPECTRUM_CSV, spectrum_rows)
    write_csv(LADDER_CSV, ladder_rows)
    write_csv(BLOCK_CSV, block_rows)
    write_csv(GATE_CSV, gate_rows)
    write_csv(CROSS_CSV, cross_rows)
    np.savez_compressed(
        DATA_NPZ,
        **{
            **{f"{rung}__q{budget}__z": summaries[rung]["block_phase"][str(budget)]["observed_z"] for rung in WINDOWS for budget in (29, 997)},
            **{f"{rung}__joint_matrix": summaries[rung]["joint_gate"]["matrix"] for rung in WINDOWS},
            **{f"{rung}__joint_residual": summaries[rung]["joint_gate"]["pearson_residual"] for rung in WINDOWS},
            **{f"{rung}__spatial_mode": summaries[rung]["joint_gate"]["leading_spatial_mode"] for rung in WINDOWS},
            **{f"{rung}__gate_mode": summaries[rung]["joint_gate"]["leading_gate_mode"] for rung in WINDOWS},
        },
    )
    make_figures(spectrum_rows, ladder_rows, summaries, cross_rows)
    results = {
        "test_id": "PN3B/RAW-DUAL-PHASE/OPENED-DEVELOPMENT-v1",
        "evidence_class": "opened-data exploratory diagnostic; not blind confirmation",
        "protocol_sha256": protocol_sha,
        "pn3_packet_sha256": packet_sha,
        "p31_accessed": False,
        "parameters": {
            "windows": WINDOWS,
            "sieve_budgets": SIEVE_BUDGETS,
            "primary_blocks": PRIMARY_BLOCKS,
            "block_sensitivities": BLOCK_SENSITIVITIES,
            "low_modes": LOW_MODES,
            "spectrum_bins": SPECTRUM_BINS,
            "joint_blocks": JOINT_BLOCKS,
            "joint_stages": JOINT_STAGES,
            "permutations": PERMUTATIONS,
            "seed": SEED,
        },
        "rung_summaries": {name: compact_summary(summary) for name, summary in summaries.items()},
        "cross_rung": cross_summary,
        "candidate_time_like_phase_coordinate_supported": candidate_time_like,
        "outputs": {
            "spectrum_csv": str(SPECTRUM_CSV),
            "ladder_csv": str(LADDER_CSV),
            "block_csv": str(BLOCK_CSV),
            "gate_csv": str(GATE_CSV),
            "cross_csv": str(CROSS_CSV),
            "data_npz": str(DATA_NPZ),
            "spectrum_figure": str(SPECTRUM_FIGURE),
            "gate_figure": str(GATE_FIGURE),
        },
    }
    write_json(RESULTS, results)
    results["output_hashes"] = {path.name: sha256_file(path) for path in (SPECTRUM_CSV, LADDER_CSV, BLOCK_CSV, GATE_CSV, CROSS_CSV, DATA_NPZ, SPECTRUM_FIGURE, GATE_FIGURE)}
    write_json(RESULTS, results)
    return results


if __name__ == "__main__":
    result = run()
    print(json.dumps({
        "test_id": result["test_id"],
        "candidate_time_like_phase_coordinate_supported": result["candidate_time_like_phase_coordinate_supported"],
        "r8_q29": result["rung_summaries"]["r8"]["block_phase"]["29"],
        "r9_q29": result["rung_summaries"]["r9"]["block_phase"]["29"],
        "r8_to_r9_q29_global": result["cross_rung"]["r8_to_r9__q29__global"],
        "r8_to_r9_joint_gate": result["cross_rung"]["r8_to_r9__joint_gate"],
    }, indent=2))
