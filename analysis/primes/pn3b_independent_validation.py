"""Independent deterministic validation for PN3B.

This validator deliberately does not import the primary analysis module.  It
rebuilds the integer windows with a Boolean segmented sieve, checks the saved
block coordinates and connection-line crosswalk, and verifies output hashes.
The Monte Carlo p-values are checked for internal consistency and range, but
are not regenerated here.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "PN3B_RAW_DUAL_PHASE_RESULTS.json"
DATA = HERE / "PN3B_DUAL_PHASE_DATA.npz"
VALIDATION = HERE / "PN3B_INDEPENDENT_VALIDATION.json"
WINDOWS = {
    "r6": (1_000_000, 1_010_000),
    "r7": (10_000_000, 10_100_000),
    "r8": (100_000_000, 101_000_000),
    "r9": (1_000_000_000, 1_010_000_000),
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            value.update(chunk)
    return value.hexdigest().upper()


def base_primes(limit: int) -> list[int]:
    composite = bytearray(limit + 1)
    for number in range(2, math.isqrt(limit) + 1):
        if not composite[number]:
            composite[number * number : limit + 1 : number] = b"\x01" * (((limit - number * number) // number) + 1)
    return [number for number in range(2, limit + 1) if not composite[number]]


def segmented_prime_mask(low: int, high: int) -> np.ndarray:
    composite = np.zeros(high - low, dtype=bool)
    for prime in base_primes(math.isqrt(high - 1)):
        start = max(prime * prime, ((low + prime - 1) // prime) * prime)
        composite[start - low :: prime] = True
    return ~composite


def connection_mask(low: int, high: int, budget: int) -> np.ndarray:
    values = np.arange(low, high, dtype=np.int64)
    mask = np.ones(high - low, dtype=bool)
    for prime in base_primes(budget):
        mask &= values % prime != 0
    return mask


def block_sum(values: np.ndarray, blocks: int) -> np.ndarray:
    bounds = np.floor(np.arange(blocks + 1) * len(values) / blocks).astype(np.int64)
    prefix = np.concatenate(([0.0], np.cumsum(values, dtype=float)))
    return prefix[bounds[1:]] - prefix[bounds[:-1]]


def block_z(prime: np.ndarray, candidate: np.ndarray, blocks: int = 256) -> np.ndarray:
    p_count = block_sum(prime.astype(float), blocks)
    c_count = block_sum(candidate.astype(float), blocks)
    probability = float(prime.sum() / candidate.sum())
    denominator = np.sqrt(np.maximum(probability * (1 - probability) * c_count, 1e-15))
    output = (p_count - probability * c_count) / denominator
    output[c_count == 0] = 0.0
    return output


def q29_top_frequency(prime: np.ndarray, candidate: np.ndarray) -> float:
    residual = prime.astype(float) - float(prime.sum() / candidate.sum()) * candidate.astype(float)
    power = np.abs(np.fft.rfft(residual - residual.mean())) ** 2
    power[0] = 0.0
    return float(np.argmax(power[1:]) + 1) / len(residual)


def main() -> dict[str, Any]:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    saved = np.load(DATA, allow_pickle=False)
    checks: dict[str, bool] = {}
    details: dict[str, Any] = {}

    for rung, (low, high) in WINDOWS.items():
        prime = segmented_prime_mask(low, high)
        q29 = connection_mask(low, high, 29)
        q997 = connection_mask(low, high, 997)
        summary = result["rung_summaries"][rung]
        checks[f"{rung}_prime_count"] = int(prime.sum()) == summary["raw_prime_events"]
        checks[f"{rung}_q29_count"] = int(q29.sum()) == summary["p29_candidate_events"]
        checks[f"{rung}_q997_count"] = int(q997.sum()) == summary["q997_candidate_events"]
        checks[f"{rung}_prime_subset_q29"] = bool(np.all(~prime | q29))
        checks[f"{rung}_prime_subset_q997"] = bool(np.all(~prime | q997))
        for budget, candidate in ((29, q29), (997, q997)):
            observed = block_z(prime, candidate)
            key = f"{rung}__q{budget}__z"
            checks[f"{rung}_q{budget}_block_coordinate"] = bool(np.allclose(observed, saved[key], atol=1e-12, rtol=1e-12))
        frequency = q29_top_frequency(prime, q29)
        crosswalk = summary["post_result_connection_line_crosswalk"]
        checks[f"{rung}_q29_top_frequency"] = abs(frequency - crosswalk["q29_residual_top_frequency"]) <= 1e-15
        harmonic = round(frequency * 62)
        within_bin = abs(frequency - harmonic / 62) <= 1 / (high - low)
        checks[f"{rung}_period62_crosswalk"] = bool(within_bin == crosswalk["within_one_fourier_bin"])
        details[rung] = {
            "prime_count": int(prime.sum()),
            "q29_count": int(q29.sum()),
            "q997_count": int(q997.sum()),
            "q29_top_frequency": frequency,
            "period62_harmonic": harmonic,
            "within_one_bin": within_bin,
        }

    spatial = float(abs(np.dot(saved["r8__spatial_mode"], saved["r9__spatial_mode"])))
    gate = float(abs(np.dot(saved["r8__gate_mode"], saved["r9__gate_mode"])))
    cross = result["cross_rung"]["r8_to_r9__joint_gate"]
    checks["r8_r9_spatial_alignment"] = abs(spatial - cross["spatial_alignment"]) <= 1e-12
    checks["r8_r9_gate_alignment"] = abs(gate - cross["gate_alignment"]) <= 1e-12
    checks["candidate_flag_false"] = result["candidate_time_like_phase_coordinate_supported"] is False
    checks["p31_not_accessed_flag"] = result["p31_accessed"] is False

    for name, expected in result["output_hashes"].items():
        path = HERE / name
        checks[f"hash_{name}"] = path.exists() and digest(path) == expected

    relevant_p = [
        result["rung_summaries"][rung]["block_phase"][budget][kind]
        for rung in ("r8", "r9")
        for budget in ("29", "997")
        for kind in ("global_familywise_p", "macro_familywise_p")
    ]
    checks["p_values_in_unit_interval"] = all(0 <= value <= 1 for value in relevant_p)
    payload = {
        "validation_target": result["test_id"],
        "validator_imports_primary_module": False,
        "all_checks_pass": all(checks.values()),
        "checks": checks,
        "details": details,
        "interpretation_checked": {
            "q29_period62_line_present_at_r8_r9": details["r8"]["within_one_bin"] and details["r9"]["within_one_bin"],
            "candidate_time_like_coordinate_supported": result["candidate_time_like_phase_coordinate_supported"],
            "monte_carlo_values_recomputed": False,
        },
    }
    VALIDATION.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"all_checks_pass": payload["all_checks_pass"], "failed": [name for name, ok in checks.items() if not ok]}, indent=2))
    return payload


if __name__ == "__main__":
    main()
