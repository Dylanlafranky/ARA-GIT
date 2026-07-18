"""Independent validation for PN3A adult sieve-path diagnostic.

This validator does not import pn3a_adult_sieve_path.py. It independently
rebuilds primality, child coordinates, survival products, and cross-rung
adult-stage scores from the sealed packet and saved diagnostic arrays.
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
PROTOCOL = HERE / "PN3A_ADULT_SIEVE_PATH_DIAGNOSTIC_PROTOCOL.md"
RESULTS = HERE / "PN3A_ADULT_SIEVE_PATH_RESULTS.json"
PACKET = HERE / "PN3_STANDALONE_ARA_TARGET_PACKET.npz"
DEV_SUMMARY = HERE / "PN3_STANDALONE_ARA_DEVELOPMENT_SUMMARY.json"
DATA = HERE / "PN3A_ADULT_SIEVE_DIAGNOSTIC_DATA.npz"
CURVES = HERE / "PN3A_ADULT_SIEVE_CURVES.csv"
TRANSFERS = HERE / "PN3A_ADULT_STAGE_TRANSFER.csv"
SURFACES = HERE / "PN3A_ADULT_CHILD_SURFACES.csv"
OUTPUT = HERE / "PN3A_INDEPENDENT_VALIDATION.json"

WINDOWS = {
    "r6": (1_000_000, 1_010_000),
    "r7": (10_000_000, 10_100_000),
    "r8": (100_000_000, 101_000_000),
    "r9": (1_000_000_000, 1_010_000_000),
}
BINS = 12
STAGES = 12
SHRINKAGE = 64.0


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def primes_through(limit: int) -> np.ndarray:
    keep = np.ones(limit + 1, dtype=bool)
    keep[:2] = False
    for value in range(2, math.isqrt(limit) + 1):
        if keep[value]:
            keep[value * value :: value] = False
    return np.flatnonzero(keep).astype(np.int64)


def segmented_prime_mask(low: int, high: int) -> np.ndarray:
    mask = np.ones(high - low, dtype=bool)
    for prime_value in primes_through(math.isqrt(high - 1)):
        prime = int(prime_value)
        start = max(prime * prime, ((low + prime - 1) // prime) * prime)
        if start < high:
            mask[start - low :: prime] = False
    return mask


def stage_from_death(death: np.ndarray, high: int) -> np.ndarray:
    stage = np.full(len(death), STAGES, dtype=np.uint8)
    composite = death > 0
    progress = np.log(death[composite].astype(float) / 31.0) / math.log(math.sqrt(high - 1) / 31.0)
    stage[composite] = np.minimum((np.clip(progress, 0.0, 1.0 - np.finfo(float).eps) * STAGES).astype(np.uint8), STAGES - 1)
    return stage


def edge_death_from_candidate(death: np.ndarray, expected_count: int) -> np.ndarray:
    if expected_count == len(death):
        raise ValueError("terminal development edge requires its saved edge-death array")
    left = death[:-1]
    right = death[1:]
    infinity = np.iinfo(np.uint16).max
    output = np.minimum(np.where(left == 0, infinity, left), np.where(right == 0, infinity, right)).astype(np.uint16)
    output[(left == 0) & (right == 0)] = 0
    return output


def fit_lookup(state: np.ndarray, stage: np.ndarray, state_count: int) -> tuple[np.ndarray, np.ndarray]:
    global_counts = np.bincount(stage.astype(np.int64), minlength=STAGES + 1).astype(float) + 0.5
    global_probability = global_counts / global_counts.sum()
    counts = np.zeros((state_count, STAGES + 1), dtype=float)
    np.add.at(counts, (state.astype(np.int64), stage.astype(np.int64)), 1.0)
    totals = counts.sum(axis=1)
    conditional = (counts + SHRINKAGE * global_probability) / (totals[:, None] + SHRINKAGE)
    return global_probability, conditional


def loss(probability: np.ndarray, stage: np.ndarray) -> float:
    selected = probability[stage.astype(np.int64)] if probability.ndim == 1 else probability[np.arange(len(stage)), stage.astype(np.int64)]
    return float(-np.mean(np.log2(np.clip(selected, 1e-15, 1.0))))


def main() -> None:
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    dev_summary = json.loads(DEV_SUMMARY.read_text(encoding="utf-8"))
    packet = np.load(PACKET, allow_pickle=False)
    diagnostic = np.load(DATA, allow_pickle=False)
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, detail: Any = None) -> None:
        checks.append({"name": name, "passed": bool(condition), "detail": detail})
        if not condition:
            raise AssertionError(name)

    check("protocol hash", sha256_file(PROTOCOL) == results["protocol_sha256"])
    check("PN3 packet hash", sha256_file(PACKET) == results["pn3_packet_sha256"])
    check("p31 remains inaccessible", results["p31_accessed"] is False)

    low, high = WINDOWS["r9"]
    exact_prime_mask = segmented_prime_mask(low, high)
    numbers = packet["candidate_numbers"].astype(np.int64)
    exact_labels = exact_prime_mask[numbers - low].astype(np.uint8)
    check("R9 packet labels independently rebuilt", np.array_equal(exact_labels, packet["candidate_labels"]))
    r9_death = diagnostic["r9__candidate_death"].astype(np.uint16)
    check("R9 death survivors equal packet labels", np.array_equal((r9_death == 0).astype(np.uint8), packet["candidate_labels"]))
    nonzero = r9_death > 0
    check("R9 death factors divide their candidates", bool(np.all(numbers[nonzero] % r9_death[nonzero].astype(np.int64) == 0)))
    prime_lookup = np.zeros(int(r9_death.max()) + 1, dtype=bool)
    prime_lookup[primes_through(int(r9_death.max()))] = True
    check("R9 death factors are prime", bool(np.all(prime_lookup[r9_death[nonzero]])))

    r9_edge = diagnostic["r9__edge_death"].astype(np.uint16)
    rebuilt_edge = edge_death_from_candidate(r9_death, len(r9_edge))
    check("R9 edge death rebuilt", np.array_equal(rebuilt_edge, r9_edge))
    check("R9 edge labels equal packet", np.array_equal((r9_edge == 0).astype(np.uint8), packet["edge_labels"]))

    gm1 = packet["candidate_gm1"].astype(float)
    g0 = packet["candidate_g0"].astype(float)
    gp1 = packet["candidate_gp1"].astype(float)
    x = 2.0 * g0 / (gm1 + g0)
    y = 2.0 * gp1 / (g0 + gp1)
    u = (x + y) / 2.0
    v = (y - x) / 2.0
    rebuilt_u = np.minimum((np.clip(u, 0.0, 2.0 - np.finfo(float).eps) * BINS / 2.0).astype(np.uint8), BINS - 1)
    rebuilt_v = np.minimum(((np.clip(v, -1.0, 1.0 - np.finfo(float).eps) + 1.0) * BINS / 2.0).astype(np.uint8), BINS - 1)
    check("R9 U bins independently rebuilt", np.array_equal(rebuilt_u, diagnostic["r9__u_bin"]))
    check("R9 V bins independently rebuilt", np.array_equal(rebuilt_v, diagnostic["r9__v_bin"]))

    for name in ("r6", "r7", "r8"):
        candidate_death = diagnostic[f"{name}__candidate_death"]
        edge_death = diagnostic[f"{name}__edge_death"]
        recorded = dev_summary["rung_rates"][name]
        check(f"{name} candidate count", len(candidate_death) == int(recorded["candidate_events"]))
        check(f"{name} candidate positives", int(np.sum(candidate_death == 0)) == int(recorded["candidate_positives"]))
        check(f"{name} edge count", len(edge_death) == int(recorded["edge_events"]))
        check(f"{name} edge positives", int(np.sum(edge_death == 0)) == int(recorded["edge_positives"]))

    curve_rows = list(csv.DictReader(CURVES.open("r", encoding="utf-8", newline="")))
    for name in WINDOWS:
        rows = [row for row in curve_rows if row["rung"] == name]
        candidate_survival = np.array([float(row["candidate_survival"]) for row in rows])
        edge_survival = np.array([float(row["edge_survival"]) for row in rows])
        check(f"{name} candidate survival monotone", bool(np.all(np.diff(candidate_survival) <= 1e-15)))
        check(f"{name} edge survival monotone", bool(np.all(np.diff(edge_survival) <= 1e-15)))
        check(f"{name} candidate release complement", bool(np.allclose(candidate_survival + np.array([float(row["candidate_cumulative_release"]) for row in rows]), 1.0, atol=1e-15)))
        check(f"{name} edge release complement", bool(np.allclose(edge_survival + np.array([float(row["edge_cumulative_release"]) for row in rows]), 1.0, atol=1e-15)))
        product = 1.0
        maximum_product_error = 0.0
        for row in rows[1:]:
            product *= 1.0 - 1.0 / int(float(row["q"]))
            maximum_product_error = max(maximum_product_error, abs(product - float(row["independence_product"])))
        check(f"{name} product recurrence", maximum_product_error < 2e-14, {"maximum_absolute_error": maximum_product_error})
        summary = results["rung_summaries"][name]
        check(f"{name} candidate terminal", abs(candidate_survival[-1] - float(summary["candidate_terminal_survival"])) < 1e-15)
        check(f"{name} edge terminal", abs(edge_survival[-1] - float(summary["edge_terminal_survival"])) < 1e-15)

    transfer_rows = list(csv.DictReader(TRANSFERS.open("r", encoding="utf-8", newline="")))
    transfer_lookup = {(row["train_rung"], row["test_rung"], row["entity"], row["model"]): row for row in transfer_rows}
    for train_name, test_name in (("r7", "r8"), ("r8", "r9")):
        for entity in ("candidate", "edge"):
            train_death = diagnostic[f"{train_name}__{'candidate_death' if entity == 'candidate' else 'edge_death'}"]
            test_death = diagnostic[f"{test_name}__{'candidate_death' if entity == 'candidate' else 'edge_death'}"]
            train_stage = stage_from_death(train_death, WINDOWS[train_name][1])
            test_stage = stage_from_death(test_death, WINDOWS[test_name][1])
            global_probability, _ = fit_lookup(np.zeros(len(train_stage), dtype=np.uint8), train_stage, 1)
            baseline_loss = loss(global_probability, test_stage)
            for model in ("u", "v", "uv"):
                train_u = diagnostic[f"{train_name}__u_bin"][: len(train_stage)].astype(np.int64)
                train_v = diagnostic[f"{train_name}__v_bin"][: len(train_stage)].astype(np.int64)
                test_u = diagnostic[f"{test_name}__u_bin"][: len(test_stage)].astype(np.int64)
                test_v = diagnostic[f"{test_name}__v_bin"][: len(test_stage)].astype(np.int64)
                if model == "u":
                    train_state, test_state, state_count = train_u, test_u, BINS
                elif model == "v":
                    train_state, test_state, state_count = train_v, test_v, BINS
                else:
                    train_state, test_state, state_count = train_u * BINS + train_v, test_u * BINS + test_v, BINS * BINS
                _, conditional = fit_lookup(train_state, train_stage, state_count)
                model_loss = loss(conditional[test_state], test_stage)
                row = transfer_lookup[(train_name, test_name, entity, model)]
                check(f"{train_name}->{test_name} {entity} {model} baseline", abs(baseline_loss - float(row["baseline_loss_bits"])) < 2e-13)
                check(f"{train_name}->{test_name} {entity} {model} model", abs(model_loss - float(row["model_loss_bits"])) < 2e-13)
                check(f"{train_name}->{test_name} {entity} {model} gain", abs((baseline_loss - model_loss) - float(row["gain_bits_per_event"])) < 2e-13)

    surface_rows = list(csv.DictReader(SURFACES.open("r", encoding="utf-8", newline="")))
    finite_surface_rows = [row for row in surface_rows if math.isfinite(float(row["conditional_survival"]))]
    for index in np.linspace(0, len(finite_surface_rows) - 1, 25, dtype=int):
        row = finite_surface_rows[int(index)]
        expected = math.log2(max(float(row["conditional_survival"]), 1e-15) / float(row["global_survival"]))
        check(f"surface identity finite row {int(index)}", abs(expected - float(row["redistribution_log2"])) < 2e-13)

    for filename, expected_hash in results["output_hashes"].items():
        check(f"output hash {filename}", sha256_file(HERE / filename) == expected_hash)

    payload = {
        "test_id": results["test_id"],
        "validator": "independent code; primary analysis module not imported",
        "passed": sum(int(item["passed"]) for item in checks),
        "total": len(checks),
        "all_passed": all(item["passed"] for item in checks),
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("test_id", "passed", "total", "all_passed")}, indent=2))


if __name__ == "__main__":
    main()
