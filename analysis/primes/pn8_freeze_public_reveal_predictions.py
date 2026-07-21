"""Freeze PN8 forecasts before any public lookup of above-boundary primes."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN8_POWER_OF_TEN_PUBLIC_REVEAL_PROTOCOL.md"
INPUTS = HERE / "PN8_BELOW_BOUNDARY_INPUTS.json"
MODEL = HERE / "PN7C_FROZEN_MODELS.npz"
OUTPUT = HERE / "PN8_PRE_REVEAL_PREDICTIONS.json"
EXPECTED_PROTOCOL = "E6FB6D621DB98298E9D14E167EDB6345EB114199BD06DA54258C6F4D38813AE9"
EXPECTED_INPUTS = "327E14D1CEF9EE4770889D565DEE2C36B41FF078204FFE3574166F887FFFD7FC"
EXPECTED_MODEL = "9141AA398C6A6694C3C5F3ECA954681D4AD8091C01310D13C6703DB30668F3A2"
BINS = 24
ALPHA = 0.5
RAW_LAMBDA = 64.0
RAW_ALPHABET = 1025


def sha256(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as handle:
        for part in iter(lambda: handle.read(1 << 20), b""):
            state.update(part)
    return state.hexdigest().upper()


def ara_bin(left: int, right: int) -> int:
    return min((BINS * right) // (left + right), BINS - 1)


def probability_models(model: np.lib.npyio.NpzFile):
    marginal = model["b24__marginal"].astype(np.float64)
    m1 = model["b24__m1"].astype(np.float64)
    m2 = model["b24__m2"].astype(np.float64)
    iid_p = (marginal + ALPHA) / (marginal.sum() + ALPHA * BINS)
    m1_p = (m1 + ALPHA) / (m1.sum(axis=1, keepdims=True) + ALPHA * BINS)
    m2_p = (m2 + ALPHA) / (m2.sum(axis=2, keepdims=True) + ALPHA * BINS)

    raw_marginal = model["raw__marginal"].astype(np.float64)
    raw_transition = model["raw__transition"].astype(np.float64)
    raw_marginal_p = np.zeros(RAW_ALPHABET, dtype=np.float64)
    raw_marginal_p[1:] = (raw_marginal[1:] + ALPHA) / (
        raw_marginal[1:].sum() + ALPHA * (RAW_ALPHABET - 1)
    )
    row_total = raw_transition.sum(axis=1, keepdims=True)
    raw_p = (raw_transition + RAW_LAMBDA * raw_marginal_p[None, :]) / (row_total + RAW_LAMBDA)
    raw_p[row_total[:, 0] == 0] = raw_marginal_p
    return iid_p, m1_p, m2_p, raw_marginal_p, raw_p


def projected_raw_distribution(current_gap: int, marginal_p: np.ndarray, raw_p: np.ndarray) -> np.ndarray:
    source = raw_p[current_gap] if current_gap < RAW_ALPHABET else marginal_p
    next_gaps = np.arange(RAW_ALPHABET, dtype=np.int64)
    categories = np.zeros(RAW_ALPHABET, dtype=np.int64)
    denominator = current_gap + next_gaps
    possible = denominator > 0
    categories[possible] = np.minimum((BINS * next_gaps[possible]) // denominator[possible], BINS - 1)
    return np.bincount(categories, weights=source, minlength=BINS)


def first_even_at_or_above(value: int) -> int:
    return value if value % 2 == 0 else value + 1


def last_even_at_or_below(value: int) -> int:
    return value if value % 2 == 0 else value - 1


def gap_range(current_gap: int, category: int, crossing_minimum: int) -> dict:
    if category == 0:
        low_integer = 1
    else:
        low_integer = math.ceil(category * current_gap / (BINS - category))
    low_even = first_even_at_or_above(max(2, low_integer))
    if category == BINS - 1:
        high_even = None
    else:
        strict_bound_numerator = (category + 1) * current_gap
        strict_bound_denominator = BINS - category - 1
        high_integer = math.ceil(strict_bound_numerator / strict_bound_denominator) - 1
        high_even = last_even_at_or_below(high_integer)

    if ara_bin(current_gap, low_even) != category:
        raise AssertionError("Lower gap-range endpoint does not map to its bin")
    if high_even is not None and high_even >= low_even and ara_bin(current_gap, high_even) != category:
        raise AssertionError("Upper gap-range endpoint does not map to its bin")

    crossing_low = first_even_at_or_above(max(low_even, crossing_minimum))
    crossing_exists = high_even is None or crossing_low <= high_even
    return {
        "all_positive_even_gaps": {"minimum": low_even, "maximum": high_even},
        "crossing_boundary_intersection": {
            "minimum": crossing_low if crossing_exists else None,
            "maximum": high_even if crossing_exists else None,
            "nonempty": crossing_exists,
        },
    }


def summarize_distribution(probabilities: np.ndarray) -> dict:
    order = np.argsort(-probabilities, kind="stable")
    return {
        "probabilities": [float(value) for value in probabilities],
        "top1_bin": int(order[0]),
        "top3_bins": [int(value) for value in order[:3]],
        "probability_sum": float(probabilities.sum()),
    }


def main() -> None:
    for path, expected, label in (
        (PROTOCOL, EXPECTED_PROTOCOL, "protocol"),
        (INPUTS, EXPECTED_INPUTS, "input"),
        (MODEL, EXPECTED_MODEL, "model"),
    ):
        if sha256(path) != expected:
            raise RuntimeError(f"{label} hash mismatch")

    inputs = json.loads(INPUTS.read_text(encoding="utf-8"))
    frozen = np.load(MODEL, allow_pickle=False)
    iid_p, m1_p, m2_p, raw_marginal_p, raw_p = probability_models(frozen)
    forecasts = []
    for target in inputs["targets"]:
        primes = [int(value) for value in target["primes"]]
        gaps = [primes[i + 1] - primes[i] for i in range(3)]
        previous_bin = ara_bin(gaps[0], gaps[1])
        current_bin = ara_bin(gaps[1], gaps[2])
        distributions = {
            "ARA-IID": summarize_distribution(iid_p),
            "ARA-M1": summarize_distribution(m1_p[current_bin]),
            "ARA-M2": summarize_distribution(m2_p[previous_bin, current_bin]),
            "RawGap-M1": summarize_distribution(projected_raw_distribution(gaps[2], raw_marginal_p, raw_p)),
        }
        distance = int(target["distance_from_boundary"])
        top_ranges = []
        for category in distributions["ARA-M2"]["top3_bins"]:
            interval = gap_range(gaps[2], category, distance + 1)
            crossing = interval["crossing_boundary_intersection"]
            top_ranges.append({
                "bin": category,
                "x_interval": [2 * category / BINS, 2 * (category + 1) / BINS],
                "probability": distributions["ARA-M2"]["probabilities"][category],
                "gap_range": interval,
                "crossing_prime_interval": {
                    "minimum": str(primes[-1] + crossing["minimum"]) if crossing["nonempty"] else None,
                    "maximum": str(primes[-1] + crossing["maximum"]) if crossing["nonempty"] and crossing["maximum"] is not None else None,
                    "nonempty": crossing["nonempty"],
                },
            })
        record = {
            "exponent": int(target["exponent"]),
            "boundary": target["boundary"],
            "known_primes_below": target["primes"],
            "known_gaps": gaps,
            "known_continuous_states": [2 * gaps[1] / (gaps[0] + gaps[1]), 2 * gaps[2] / (gaps[1] + gaps[2])],
            "known_context_bins": {"previous": previous_bin, "current": current_bin},
            "distance_from_boundary": distance,
            "distributions": distributions,
            "ara_m2_top3_gap_and_number_ranges": top_ranges,
        }
        forecasts.append(record)
        print(json.dumps({
            "exponent": record["exponent"],
            "known_gaps": gaps,
            "context_bins": record["known_context_bins"],
            "ARA-M2_top3": distributions["ARA-M2"]["top3_bins"],
            "RawGap-M1_top3": distributions["RawGap-M1"]["top3_bins"],
        }, indent=2), flush=True)

    packet = {
        "test_id": "PN8/PRE-REVEAL-PREDICTIONS-v1",
        "created_before_public_target_lookup": True,
        "hashes": {"protocol": EXPECTED_PROTOCOL, "inputs": EXPECTED_INPUTS, "model": EXPECTED_MODEL},
        "settings": {"bins": BINS, "alpha": ALPHA, "raw_lambda": RAW_LAMBDA, "raw_alphabet": "1..1024"},
        "forecasts": forecasts,
        "boundaries": {
            "above_boundary_numbers_tested": 0,
            "public_target_source_queried": False,
            "target_prime_values_present": False,
            "r12_opened": False,
            "p31_wheel_opened": False,
        },
        "builder_sha256": sha256(Path(__file__)),
    }
    OUTPUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": OUTPUT.name, "sha256": sha256(OUTPUT)}, indent=2), flush=True)


if __name__ == "__main__":
    main()
