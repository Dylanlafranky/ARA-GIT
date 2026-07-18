"""Independent validator for PN3; does not import either PN3 analysis script."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
PROTOCOL_HASH = "DB6BE581908BA336A02F2481CEAB21FAACEF137F8773E9FC74CCF605E5E5A2EB"
PACKET = HERE / "PN3_STANDALONE_ARA_TARGET_PACKET.npz"
TARGET_SUMMARY = HERE / "PN3_STANDALONE_ARA_TARGET_SUMMARY.json"
TARGET_CONFIG = HERE / "PN3_TARGET_RUN_CONFIG_v1_FROZEN.json"
COMPARATOR_CONFIG = HERE / "PN3_COMPARATOR_RUN_CONFIG_v1_FROZEN.json"
SCORES = HERE / "PN3_STANDALONE_ARA_MODEL_SCORES.csv"
BOOTSTRAP = HERE / "PN3_STANDALONE_ARA_BOOTSTRAP.csv"
BLOCKS = HERE / "PN3_STANDALONE_ARA_BLOCK_CALIBRATION.csv"
RESULTS = HERE / "PN3_STANDALONE_ARA_RESULTS.json"
OUTPUT = HERE / "PN3_INDEPENDENT_VALIDATION.json"

SIEVE_PRIMES = np.array([2, 3, 5, 7, 11, 13, 17, 19, 23, 29], dtype=np.int64)
W29 = float(np.prod(1.0 - 1.0 / SIEVE_PRIMES.astype(float)))
TWIN_CONSTANT = 0.6601618158468696
REPLICATES = 10_000
SEED = 20_260_717


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def simple_primes(limit: int) -> np.ndarray:
    sieve = np.ones(limit + 1, dtype=bool)
    sieve[:2] = False
    for p in range(2, int(math.isqrt(limit)) + 1):
        if sieve[p]:
            sieve[p * p :: p] = False
    return np.flatnonzero(sieve).astype(np.int64)


def segmented_prime_mask(low: int, high: int) -> np.ndarray:
    mask = np.ones(high - low, dtype=bool)
    for p in simple_primes(math.isqrt(high - 1)):
        p_int = int(p)
        start = max(p_int * p_int, ((low + p_int - 1) // p_int) * p_int)
        if start < high:
            mask[start - low :: p_int] = False
    return mask


def p29_mask(low: int, high: int) -> np.ndarray:
    mask = np.ones(high - low, dtype=bool)
    for p in SIEVE_PRIMES:
        mask[(-low) % int(p) :: int(p)] = False
    return mask


def factors(number: int) -> list[int]:
    answer: list[int] = []
    remaining = int(number)
    for p in simple_primes(math.isqrt(remaining) + 1):
        p_int = int(p)
        if remaining % p_int == 0:
            answer.append(p_int)
            while remaining % p_int == 0:
                remaining //= p_int
        if p_int * p_int > remaining:
            break
    if remaining > 1:
        answer.append(remaining)
    return answer


def edge_multiplier(gap: int) -> float:
    singular = 2.0 * TWIN_CONSTANT
    for factor in factors(gap):
        if factor > 2:
            singular *= (factor - 1.0) / (factor - 2.0)
    conditioned = 1.0
    for p in SIEVE_PRIMES:
        q = int(p)
        conditioned *= 1.0 - (1 if gap % q == 0 else 2) / q
    return singular / conditioned


def loss(labels: np.ndarray, probabilities: np.ndarray) -> np.ndarray:
    p = np.clip(probabilities.astype(float), 1e-9, 1.0 - 1e-9)
    return -(labels * np.log2(p) + (1 - labels) * np.log2(1.0 - p))


def main() -> None:
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, detail: Any = None) -> None:
        checks.append({"name": name, "passed": bool(condition), "detail": detail})
        if not condition:
            raise AssertionError(f"validation failed: {name}: {detail}")

    target_config = json.loads(TARGET_CONFIG.read_text(encoding="utf-8"))
    comparator_config = json.loads(COMPARATOR_CONFIG.read_text(encoding="utf-8"))
    target_summary = json.loads(TARGET_SUMMARY.read_text(encoding="utf-8"))
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    check("protocol hash in target config", target_config["protocol_sha256"] == PROTOCOL_HASH)
    check("protocol hash in comparator config", comparator_config["protocol_sha256"] == PROTOCOL_HASH)
    check("sealed packet hash", sha256(PACKET) == comparator_config["packet_sha256"], sha256(PACKET))
    check("target config hash", sha256(TARGET_CONFIG) == comparator_config["target_config_sha256"])
    check("target summary hash", sha256(TARGET_SUMMARY) == comparator_config["target_summary_sha256"])
    check("standalone script hash", sha256(HERE / "pn3_standalone_ara.py") == target_config["standalone_script_sha256"])
    check("comparison script hash", sha256(HERE / "pn3_established_comparison.py") == comparator_config["comparison_script_sha256"])

    forbidden = ("hardy", "littlewood", "twin_prime", "singular_series", "pnt29", "hl29")
    standalone_text = (HERE / "pn3_standalone_ara.py").read_text(encoding="utf-8").lower()
    check("standalone analytic-reference quarantine", not any(term in standalone_text for term in forbidden))

    archive = np.load(PACKET, allow_pickle=False)
    metadata = json.loads(str(archive["metadata_json"]))
    low, high = int(metadata["target_low"]), int(metadata["target_high"])
    numbers = archive["candidate_numbers"].astype(np.int64)
    labels = archive["candidate_labels"].astype(np.uint8)
    edge_numbers = archive["edge_numbers"].astype(np.int64)
    edge_labels = archive["edge_labels"].astype(np.uint8)
    gaps = archive["edge_gaps"].astype(np.int64)

    independent_candidates = np.flatnonzero(p29_mask(low, high)).astype(np.int64) + low
    independent_prime_mask = segmented_prime_mask(low, high)
    independent_labels = independent_prime_mask[independent_candidates - low].astype(np.uint8)
    check("candidate number population", np.array_equal(numbers, independent_candidates), len(numbers))
    check("candidate labels from independent sieve", np.array_equal(labels, independent_labels), int(np.sum(labels)))
    check("edge number population", np.array_equal(edge_numbers, numbers[:-1]))
    check("edge gaps", np.array_equal(gaps, np.diff(numbers)))
    check("edge labels", np.array_equal(edge_labels, labels[:-1] * labels[1:]))

    for task, model_names, prefix, expected_mean in (
        ("candidate", metadata["candidate_models"], "candidate", target_summary["candidate_parent_predictions"]["ara"]),
        ("edge", metadata["edge_models"], "edge", target_summary["edge_parent_predictions"]["ara"]),
    ):
        for model in model_names:
            prediction = archive[f"{prefix}_prediction__{model}"].astype(float)
            check(f"finite probabilities {task}/{model}", bool(np.all(np.isfinite(prediction))))
            check(f"bounded probabilities {task}/{model}", bool(np.all((prediction > 0) & (prediction < 1))))
            if model.startswith("ara_parent_ara_") or model.startswith("ara_parent_raw_"):
                check(
                    f"TE-ARA mean conservation {task}/{model}",
                    abs(float(np.mean(prediction)) - float(expected_mean)) < 2e-8,
                    float(np.mean(prediction)) - float(expected_mean),
                )

    candidate_reference = 1.0 / (np.log(numbers.astype(float)) * W29)
    multipliers = {int(gap): edge_multiplier(int(gap)) for gap in np.unique(gaps)}
    edge_reference = np.array([multipliers[int(gap)] for gap in gaps]) / (
        np.log(edge_numbers.astype(float)) * np.log((edge_numbers + gaps).astype(float))
    )
    check("conditioned edge multiplier constant", len({round(value, 12) for value in multipliers.values()}) == 1)

    scores = pd.read_csv(SCORES)
    prediction_sets: dict[tuple[str, str], tuple[np.ndarray, np.ndarray]] = {}
    for model in metadata["candidate_models"]:
        prediction_sets[("candidate", model)] = (labels, archive[f"candidate_prediction__{model}"].astype(float))
    for model in metadata["edge_models"]:
        prediction_sets[("edge", model)] = (edge_labels, archive[f"edge_prediction__{model}"].astype(float))
    prediction_sets[("candidate", "pnt29_reference")] = (labels, candidate_reference)
    prediction_sets[("edge", "hl29_reference")] = (edge_labels, edge_reference)
    for _, row in scores.iterrows():
        row_labels, prediction = prediction_sets[(row["task"], row["model"])]
        check(
            f"score log loss {row['task']}/{row['model']}",
            abs(float(np.mean(loss(row_labels, prediction))) - float(row["log_loss_bits"])) < 2e-12,
        )
        check(
            f"score mean prediction {row['task']}/{row['model']}",
            abs(float(np.mean(prediction)) - float(row["mean_prediction"])) < 2e-12,
        )

    block_table = pd.read_csv(BLOCKS)
    bootstrap_table = pd.read_csv(BOOTSTRAP)
    rng = np.random.default_rng(SEED)
    for _, row in bootstrap_table.iterrows():
        task_blocks = block_table[block_table["task"] == row["task"]].sort_values("block")
        weights = task_blocks["events"].to_numpy(float)
        delta = (
            task_blocks[f"loss__{row['comparator']}"] - task_blocks[f"loss__{row['model']}"]
        ).to_numpy(float)
        observed = float(np.average(delta, weights=weights))
        samples = rng.integers(0, len(delta), size=(REPLICATES, len(delta)))
        distribution = np.sum(delta[samples] * weights[samples], axis=1) / np.sum(weights[samples], axis=1)
        check(f"bootstrap observed {row['task']}/{row['comparator']}", abs(observed - row["observed_gain_bits"]) < 2e-12)
        check(f"bootstrap low {row['task']}/{row['comparator']}", abs(float(np.quantile(distribution, 0.025)) - row["ci95_low_bits"]) < 2e-12)
        check(f"bootstrap high {row['task']}/{row['comparator']}", abs(float(np.quantile(distribution, 0.975)) - row["ci95_high_bits"]) < 2e-12)

    check("packet unchanged after independent read", sha256(PACKET) == comparator_config["packet_sha256"])
    check("all registered criteria are negative", not any(results["criteria"].values()), results["criteria"])
    output = {
        "test_id": results["test_id"],
        "validator_imported_primary_scripts": False,
        "checks_passed": int(sum(item["passed"] for item in checks)),
        "checks_total": len(checks),
        "all_checks_passed": all(item["passed"] for item in checks),
        "packet_sha256": sha256(PACKET),
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in output.items() if key != "checks"}, indent=2))


if __name__ == "__main__":
    main()
