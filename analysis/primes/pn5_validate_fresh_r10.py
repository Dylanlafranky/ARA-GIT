from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
FROZEN = HERE / "PN5_FROZEN_PREDICTIONS.json"
FREEZE_MANIFEST = HERE / "PN5_FROZEN_PREDICTION_MANIFEST.json"
TARGET = HERE / "PN5_R10_TARGET_AGGREGATES.json"
RESULTS = HERE / "PN5_MULTIPLICATIVE_RUNG_RESULTS.json"
PN4_PATHS = HERE / "PN4_DIRECT_SIEVE_STATE_PATHS.csv"
OUTPUT = HERE / "PN5_FRESH_R10_VALIDATION.json"
SMALL = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29)
CHUNK = 3_000_001
EPS = 1e-12


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(786_432):
            h.update(block)
    return h.hexdigest().upper()


def prime_list(limit: int) -> np.ndarray:
    flags = bytearray(b"\x01") * (limit + 1)
    flags[:2] = b"\x00\x00"
    for value in range(2, math.isqrt(limit) + 1):
        if flags[value]:
            count = (limit - value * value) // value + 1
            flags[value * value : limit + 1 : value] = b"\x00" * count
    return np.fromiter((number for number, flag in enumerate(flags) if flag), dtype=np.int64)


def pair_gate(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    large = np.uint32(4_294_967_295)
    aa = np.where(a == 0, large, a)
    bb = np.where(b == 0, large, b)
    answer = np.minimum(aa, bb).astype(np.uint32)
    answer[(a == 0) & (b == 0)] = 0
    return answer


def tally(values: np.ndarray, lookup: np.ndarray, output: np.ndarray) -> None:
    factors = values[values != 0].astype(np.int64)
    if len(factors):
        output += np.bincount(lookup[factors], minlength=len(output))[: len(output)]


def rebuild_target(frozen: dict[str, Any]) -> dict[str, Any]:
    low = int(frozen["target"]["low"])
    high = int(frozen["target"]["high"])
    cell_count = int(frozen["target"]["cells"])
    primes = prime_list(math.isqrt(high - 1))
    gates = primes[primes > 29]
    qmax = int(gates[-1])
    normalized = np.log(gates.astype(float) / 31.0) / math.log(qmax / 31.0)
    gate_cells = np.minimum((normalized * cell_count).astype(np.int16), cell_count - 1)
    lookup = np.full(qmax + 1, -1, dtype=np.int16)
    lookup[gates] = gate_cells
    deaths_candidate = np.zeros(cell_count, dtype=np.int64)
    deaths_pair = np.zeros(cell_count, dtype=np.int64)
    n_candidate = 0
    n_pair = 0
    alive_candidate = 0
    alive_pair = 0
    carry: np.uint32 | None = None

    for left in range(low, high, CHUNK):
        right = min(high, left + CHUNK)
        length = right - left
        least = np.zeros(length, dtype=np.uint32)
        for q_value in gates:
            q = int(q_value)
            first = ((left + q - 1) // q) * q
            if first < q * q:
                first = q * q
            if first >= right:
                continue
            positions = np.arange(first - left, length, q, dtype=np.int64)
            unassigned = least[positions] == 0
            least[positions[unassigned]] = q
        permitted = np.ones(length, dtype=bool)
        for q in SMALL:
            first_index = (-left) % q
            permitted[first_index::q] = False
        sequence = least[np.flatnonzero(permitted)]
        if not len(sequence):
            continue
        n_candidate += len(sequence)
        alive_candidate += int((sequence == 0).sum())
        tally(sequence, lookup, deaths_candidate)
        if carry is not None:
            bridge = pair_gate(np.array([carry], dtype=np.uint32), sequence[:1])
            n_pair += 1
            alive_pair += int(bridge[0] == 0)
            tally(bridge, lookup, deaths_pair)
        if len(sequence) > 1:
            pairs = pair_gate(sequence[:-1], sequence[1:])
            n_pair += len(pairs)
            alive_pair += int((pairs == 0).sum())
            tally(pairs, lookup, deaths_pair)
        carry = sequence[-1]

    def path(total: int, deaths: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        before = np.empty(cell_count, dtype=np.int64)
        survival = np.empty(cell_count, dtype=float)
        remaining = total
        for cell in range(cell_count):
            before[cell] = remaining
            remaining -= int(deaths[cell])
            survival[cell] = remaining / total
        return before, survival

    cb, cs = path(n_candidate, deaths_candidate)
    eb, es = path(n_pair, deaths_pair)
    return {
        "candidate_n0": n_candidate,
        "candidate_alive": alive_candidate,
        "candidate_deaths": deaths_candidate,
        "candidate_before": cb,
        "candidate_survival": cs,
        "edge_n0": n_pair,
        "edge_alive": alive_pair,
        "edge_deaths": deaths_pair,
        "edge_before": eb,
        "edge_survival": es,
        "qmax": qmax,
    }


def score(prediction: np.ndarray, before: np.ndarray, deaths: np.ndarray, survival: np.ndarray) -> dict[str, float]:
    previous = np.concatenate(([1.0], prediction[:-1]))
    probability = np.clip(1.0 - prediction / previous, EPS, 1.0 - EPS)
    n, d = before.astype(float), deaths.astype(float)
    bits = -(d * np.log2(probability) + (n - d) * np.log2(1.0 - probability))
    return {
        "log_loss_bits_per_at_risk_event": float(bits.sum() / n.sum()),
        "survival_rmse": float(np.sqrt(np.mean((prediction - survival) ** 2))),
        "terminal_absolute_relative_error": float(abs(prediction[-1] - survival[-1]) / survival[-1]),
    }


def close(a: float, b: float, tolerance: float = 5e-12) -> bool:
    return abs(a - b) <= tolerance * max(1.0, abs(a), abs(b))


def omega_reference(values: np.ndarray, step: float = 5e-5) -> np.ndarray:
    maximum = float(max(2.0, np.max(values))) + step
    grid = 1.0 + np.arange(int(math.ceil((maximum - 1.0) / step)) + 1) * step
    answer = np.empty(len(grid), dtype=float)
    shift = int(round(1.0 / step))
    answer[: shift + 1] = 1.0 / grid[: shift + 1]
    product = np.ones(len(grid), dtype=float)
    for index in range(shift + 1, len(grid)):
        product[index] = product[index - 1] + 0.5 * step * (answer[index - shift - 1] + answer[index - shift])
        answer[index] = product[index] / grid[index]
    return np.interp(values, grid, answer)


def main() -> None:
    checks: dict[str, bool] = {}
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE_MANIFEST.read_text(encoding="utf-8"))
    saved_target = json.loads(TARGET.read_text(encoding="utf-8"))
    saved_results = json.loads(RESULTS.read_text(encoding="utf-8"))
    checks["freeze_packet_hash"] = digest(FROZEN) == freeze["files"][FROZEN.name]
    checks["builder_verified_same_hash"] = saved_target["freeze_evidence"]["prediction_packet_sha256_observed_before_open"] == digest(FROZEN)
    rebuilt = rebuild_target(frozen)
    checks["qmax"] = rebuilt["qmax"] == frozen["gate_path"]["qmax"]
    checks["candidate_n0"] = rebuilt["candidate_n0"] == saved_target["candidate"]["n0"]
    checks["candidate_alive"] = rebuilt["candidate_alive"] == saved_target["candidate"]["terminal_survivors"]
    checks["edge_n0"] = rebuilt["edge_n0"] == saved_target["edge"]["n0"]
    checks["edge_alive"] = rebuilt["edge_alive"] == saved_target["edge"]["terminal_survivors"]
    checks["edge_is_candidate_minus_one"] = rebuilt["edge_n0"] == rebuilt["candidate_n0"] - 1
    for entity, prefix in (("candidate", "candidate"), ("edge", "edge")):
        for field in ("deaths", "before", "survival"):
            new = rebuilt[f"{prefix}_{field}"]
            old = np.asarray(saved_target[entity][field], dtype=new.dtype)
            checks[f"{entity}_{field}"] = bool(np.allclose(new, old, rtol=0.0, atol=1e-14))

    predictions = {
        entity: {model: np.asarray(values, dtype=float) for model, values in models.items()}
        for entity, models in frozen["predictions"].items()
    }
    r9_rows = [row for row in csv.DictReader(PN4_PATHS.open("r", encoding="utf-8", newline="")) if row["rung"] == "r9"]
    r9_c = np.array([float(row["candidate_survival"]) for row in r9_rows])
    r9_ci = np.array([float(row["candidate_independent"]) for row in r9_rows])
    r9_j = np.array([float(row["coupling_j"]) for row in r9_rows])
    target_ind = predictions["candidate"]["independent_sieve"]
    primary_c = target_ind * r9_c / r9_ci
    primary_e = primary_c**2 * np.exp(r9_j)
    checks["primary_candidate_formula"] = bool(np.allclose(primary_c, predictions["candidate"]["ara_multiplicative_primary"], rtol=0.0, atol=2e-14))
    checks["primary_edge_formula"] = bool(np.allclose(primary_e, predictions["edge"]["ara_multiplicative_primary"], rtol=0.0, atol=2e-14))
    omega_spot = omega_reference(np.array([2.0, 3.0]))
    checks["buchstab_omega_2"] = close(float(omega_spot[0]), 0.5, tolerance=2e-10)
    checks["buchstab_omega_3"] = close(float(omega_spot[1]), (1.0 + math.log(2.0)) / 3.0, tolerance=2e-9)
    q_end = np.asarray(frozen["gate_path"]["q_end"], dtype=float)
    midpoint = 0.5 * (float(frozen["target"]["low"]) + float(frozen["target"]["high"]))
    u = np.log(midpoint) / np.log(q_end)
    buchstab_path = target_ind * math.exp(0.5772156649015329) * omega_reference(u)
    checks["buchstab_candidate_path"] = bool(np.allclose(buchstab_path, predictions["candidate"]["buchstab_established"], rtol=0.0, atol=2e-9))

    entities = {
        "candidate": (rebuilt["candidate_before"], rebuilt["candidate_deaths"], rebuilt["candidate_survival"]),
        "edge": (rebuilt["edge_before"], rebuilt["edge_deaths"], rebuilt["edge_survival"]),
    }
    for entity, (before, deaths, survival) in entities.items():
        for model, prediction in predictions[entity].items():
            metrics = score(prediction, before, deaths, survival)
            for metric, value in metrics.items():
                checks[f"score__{entity}__{model}__{metric}"] = close(value, saved_results["scores"][entity][model][metric])

    actual_k = np.log(rebuilt["candidate_survival"] / target_ind)
    actual_j = np.log(rebuilt["edge_survival"] / rebuilt["candidate_survival"]**2)
    source = {key: np.asarray(value, dtype=float) for key, value in frozen["source_coordinates"].items()}
    relation = {
        "k_r9_to_r10": float(np.sqrt(np.mean((source["r9_k_candidate"] - actual_k) ** 2))),
        "k_r8_to_r10": float(np.sqrt(np.mean((source["r8_k_candidate"] - actual_k) ** 2))),
        "j_r9_to_r10": float(np.sqrt(np.mean((source["r9_j_pair"] - actual_j) ** 2))),
        "j_r8_to_r10": float(np.sqrt(np.mean((source["r8_j_pair"] - actual_j) ** 2))),
    }
    for key, value in relation.items():
        checks[f"relation__{key}"] = close(value, saved_results["relation_path_rmse"][key])

    failed = sorted(key for key, passed in checks.items() if not passed)
    output = {
        "test_id": frozen["test_id"],
        "validator_independence": "Does not import PN5 primary modules; repeats the 100-million-integer target with a different chunk size and independently recomputes formulas and scores.",
        "validation_chunk_size": CHUNK,
        "checks_passed": int(sum(checks.values())),
        "checks_total": len(checks),
        "all_passed": not failed,
        "failed": failed,
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: output[key] for key in ("checks_passed", "checks_total", "all_passed", "failed")}, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
