"""Independent PN10B validator.

This file does not import the primary implementation. It rebuilds prime and
survivor masks by direct multiple marking, reconstructs every registered feature,
checks fitted-score equations and gradients, and recomputes all reported metrics.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
RESULT_PATH = ROOT / "PN10B_CHILD_PHASE_RESULTS.json"
SCORES_PATH = ROOT / "PN10B_FRESH_TARGET_SCORES.csv"
METRICS_PATH = ROOT / "PN10B_MODEL_METRICS.csv"
COMPARISONS_PATH = ROOT / "PN10B_FRESH_COMPARISONS.csv"
OUTPUT_PATH = ROOT / "PN10B_CHILD_PHASE_VALIDATION.json"
PROTOCOL_PATH = ROOT / "PN10B_CHILD_PHASE_PRIME_RANKING_PROTOCOL.md"
SOURCE_PATH = ROOT / "pn10b_child_phase_prime_ranking.py"
FREEZE_PATH = ROOT / "PN10B_FREEZE_MANIFEST.json"

K = 9
L2 = 0.01
MODEL_ORDER = (
    "parent_empirical",
    "buchstab_parent",
    "ara_compact",
    "raw_compact",
    "ara_full",
    "raw_full",
    "ara_order_scrambled",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def primes_through(limit: int) -> np.ndarray:
    flags = np.ones(limit + 1, dtype=np.bool_)
    flags[0:2] = False
    candidate = 2
    while candidate * candidate <= limit:
        if flags[candidate]:
            flags[candidate * candidate :: candidate] = False
        candidate += 1
    return np.nonzero(flags)[0].astype(np.int64)


def direct_interval(low: int, high: int) -> tuple[np.ndarray, np.ndarray, dict[str, np.ndarray], dict]:
    all_numbers = np.arange(low, high, dtype=np.int64)
    composite = np.zeros(high - low, dtype=np.bool_)
    for prime64 in primes_through(math.isqrt(high - 1)):
        prime = int(prime64)
        first = max(prime * prime, ((low + prime - 1) // prime) * prime)
        if first < high:
            composite[first - low :: prime] = True
    prime_mask = ~composite

    threshold = all_numbers.astype(np.float64) ** 0.45
    removed = np.zeros(high - low, dtype=np.bool_)
    gate_table = primes_through(int(math.ceil(float(np.max(threshold)))) + 2)
    for prime64 in gate_table:
        prime = int(prime64)
        first = ((low + prime - 1) // prime) * prime
        if first >= high:
            continue
        positions = np.arange(first, high, prime, dtype=np.int64)
        legal = prime <= positions.astype(np.float64) ** 0.45
        removed[positions[legal] - low] = True
    survivor_mask = ~removed
    numbers = all_numbers[survivor_mask]
    labels = prime_mask[survivor_mask].astype(np.float64)
    thresholds = threshold[survivor_mask]

    last = np.searchsorted(gate_table, thresholds, side="right") - 1
    indices = last[:, None] - np.arange(K, dtype=np.int64)[None, :]
    gates = gate_table[indices]
    remainder = numbers[:, None] % gates
    unit = remainder.astype(np.float64) / gates.astype(np.float64)
    signed = 2.0 * unit - 1.0
    coupling = signed[:, :-1] * signed[:, 1:]

    compact_ara = np.column_stack(
        [signed.mean(1), np.abs(signed).mean(1), signed.std(1), coupling.mean(1)]
    )
    compact_raw = np.column_stack([unit.mean(1), unit.std(1), unit.min(1), unit.max(1)])
    full_ara = np.column_stack([signed, coupling])
    full_raw = np.column_stack([unit, unit[:, :-1] - unit[:, 1:]])
    rotated = np.empty_like(signed)
    for row in range(len(signed)):
        rotated[row] = np.roll(signed[row], -int(numbers[row] % K))
    rotated_coupling = rotated[:, :-1] * rotated[:, 1:]
    scrambled = np.column_stack([rotated, rotated_coupling])

    features = {
        "ara_compact": compact_ara,
        "raw_compact": compact_raw,
        "ara_full": full_ara,
        "raw_full": full_raw,
        "ara_order_scrambled": scrambled,
    }
    guards = {
        "closure": float(np.max(np.abs((2.0 * unit) + (2.0 - 2.0 * unit) - 2.0))),
        "gate_overrun": float(np.max(gates[:, 0] - thresholds)),
        "zero_remainders": int(np.count_nonzero(remainder == 0)),
    }
    return numbers, labels, features, guards


def probability_from_saved_fit(fit: dict, features: np.ndarray) -> np.ndarray:
    mean = np.asarray(fit["standardization_mean"], dtype=np.float64)
    scale = np.asarray(fit["standardization_scale"], dtype=np.float64)
    beta = np.asarray([fit["intercept"], *fit["coefficients"]], dtype=np.float64)
    standardized = (features - mean) / scale
    design = np.column_stack([np.ones(len(features)), standardized])
    linear = np.clip(design @ beta, -40.0, 40.0)
    return 1.0 / (1.0 + np.exp(-linear))


def gradient_residual(fit: dict, features: np.ndarray, labels: np.ndarray) -> float:
    mean = np.asarray(fit["standardization_mean"], dtype=np.float64)
    scale = np.asarray(fit["standardization_scale"], dtype=np.float64)
    beta = np.asarray([fit["intercept"], *fit["coefficients"]], dtype=np.float64)
    design = np.column_stack([np.ones(len(features)), (features - mean) / scale])
    probability = 1.0 / (1.0 + np.exp(-np.clip(design @ beta, -40.0, 40.0)))
    penalty = beta.copy()
    penalty[0] = 0.0
    gradient = design.T @ (probability - labels) / len(labels) + L2 * penalty
    return float(np.max(np.abs(gradient)))


def losses(labels: np.ndarray, probability: np.ndarray) -> np.ndarray:
    p = np.clip(probability, 1e-12, 1.0 - 1e-12)
    return -(labels * np.log2(p) + (1.0 - labels) * np.log2(1.0 - p))


def tied_auc(labels: np.ndarray, score: np.ndarray) -> float:
    order = np.argsort(score, kind="mergesort")
    sorted_score = score[order]
    rank = np.empty(len(score), dtype=np.float64)
    left = 0
    while left < len(score):
        right = left + 1
        while right < len(score) and sorted_score[right] == sorted_score[left]:
            right += 1
        rank[order[left:right]] = ((left + 1) + right) / 2.0
        left = right
    positive = labels == 1
    n_positive = int(positive.sum())
    n_negative = len(labels) - n_positive
    return float((rank[positive].sum() - n_positive * (n_positive + 1) / 2.0) / (n_positive * n_negative))


def metrics(labels: np.ndarray, probability: np.ndarray) -> dict:
    count = len(labels)
    top_count = max(1, math.ceil(count / 10))
    top = np.argsort(-probability, kind="mergesort")[:top_count]
    prevalence = float(labels.mean())
    return {
        "log_loss_bits": float(losses(labels, probability).mean()),
        "brier": float(np.mean((probability - labels) ** 2)),
        "auc": tied_auc(labels, probability),
        "top_decile_precision": float(labels[top].mean()),
        "top_decile_lift": float(labels[top].mean() / prevalence),
        "calibration_error": float(probability.mean() - prevalence),
    }


def main() -> None:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    checks: list[dict] = []

    def check(name: str, passed: bool, observed=None, expected=None, tolerance=None) -> None:
        checks.append(
            {
                "name": name,
                "passed": bool(passed),
                "observed": observed,
                "expected": expected,
                "tolerance": tolerance,
            }
        )

    check("protocol hash", digest(PROTOCOL_PATH) == freeze["protocol_sha256"], digest(PROTOCOL_PATH), freeze["protocol_sha256"])
    check("source hash", digest(SOURCE_PATH) == freeze["source_sha256"], digest(SOURCE_PATH), freeze["source_sha256"])

    rebuilt = {}
    for name in ("D", "E", "F"):
        rebuilt[name] = direct_interval(*freeze["intervals"][name])
        numbers, labels, _, guards = rebuilt[name]
        saved = result["intervals"][name]
        check(f"{name} survivor count", len(numbers) == saved["survivor_count"], len(numbers), saved["survivor_count"])
        check(f"{name} prime count", int(labels.sum()) == saved["prime_count"], int(labels.sum()), saved["prime_count"])
        check(f"{name} child closure", guards["closure"] <= 1e-12, guards["closure"], "<=1e-12")
        check(f"{name} gate guard", guards["gate_overrun"] <= 0.0, guards["gate_overrun"], "<=0")
        check(f"{name} nonzero paid remainders", guards["zero_remainders"] == 0, guards["zero_remainders"], 0)

    d_numbers, d_labels, d_features, _ = rebuilt["D"]
    e_numbers, e_labels, e_features, _ = rebuilt["E"]
    f_numbers, f_labels, f_features, _ = rebuilt["F"]

    score_rows = list(csv.DictReader(SCORES_PATH.open(encoding="utf-8")))
    saved_numbers = np.asarray([int(row["n"]) for row in score_rows], dtype=np.int64)
    saved_labels = np.asarray([int(row["label_prime"]) for row in score_rows], dtype=np.float64)
    check("fresh score integer population", np.array_equal(saved_numbers, f_numbers))
    check("fresh score labels", np.array_equal(saved_labels, f_labels))

    d_e_labels = np.concatenate([d_labels, e_labels])
    d_e_features = {name: np.vstack([d_features[name], e_features[name]]) for name in d_features}
    independent_predictions = {
        "parent_empirical": np.full(len(f_labels), d_e_labels.mean()),
        "buchstab_parent": np.full(len(f_labels), result["parameters"]["buchstab_parent_probability"]),
    }
    max_gradient = 0.0
    for name, feature_matrix in d_e_features.items():
        fit = result["stage_b_fit"]["models"][name]
        independent_predictions[name] = probability_from_saved_fit(fit, f_features[name])
        residual = gradient_residual(fit, feature_matrix, d_e_labels)
        max_gradient = max(max_gradient, residual)
        check(f"{name} fitted gradient", residual <= 1e-8, residual, "<=1e-8")

    for model in MODEL_ORDER:
        saved_probability = np.asarray([float(row[model]) for row in score_rows], dtype=np.float64)
        error = float(np.max(np.abs(saved_probability - independent_predictions[model])))
        check(f"{model} fresh prediction reconstruction", error <= 5e-15, error, "<=5e-15")

    saved_metric_rows = list(csv.DictReader(METRICS_PATH.open(encoding="utf-8")))
    saved_fresh_metrics = {row["model"]: row for row in saved_metric_rows if row["stage"] == "pooled_D_E_to_fresh_F"}
    max_metric_error = 0.0
    for model in MODEL_ORDER:
        recalculated = metrics(f_labels, independent_predictions[model])
        for field, value in recalculated.items():
            expected = float(saved_fresh_metrics[model][field])
            error = abs(value - expected)
            max_metric_error = max(max_metric_error, error)
            check(f"{model} {field}", error <= 2e-14, value, expected, "2e-14")

    comparison_rows = list(csv.DictReader(COMPARISONS_PATH.open(encoding="utf-8")))
    for row in comparison_rows:
        first = row["first_model"]
        second = row["second_model"]
        gain = float(np.mean(losses(f_labels, independent_predictions[second]) - losses(f_labels, independent_predictions[first])))
        expected = float(row["gain_bits_per_event"])
        check(f"{row['comparison']} exact gain", abs(gain - expected) <= 2e-14, gain, expected, "2e-14")

    output = {
        "test_id": result["test_id"],
        "validation_method": "independent direct-multiple masks, feature reconstruction, fit-gradient checks and score replay",
        "checks_passed": int(sum(item["passed"] for item in checks)),
        "checks_total": len(checks),
        "all_passed": bool(all(item["passed"] for item in checks)),
        "max_fitted_gradient": max_gradient,
        "max_metric_error": max_metric_error,
        "checks": checks,
        "protected_material": {"p31_primorial_wheel_constructed": False, "r12_opened": False},
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps({key: output[key] for key in ("checks_passed", "checks_total", "all_passed", "max_fitted_gradient", "max_metric_error")}, indent=2))


if __name__ == "__main__":
    main()
