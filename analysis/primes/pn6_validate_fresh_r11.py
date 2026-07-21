from __future__ import annotations

import csv
import hashlib
import json
import math
import time
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parent
FREEZE = ROOT / "PN6_NATIVE_ARA_FROZEN_PREDICTIONS.json"
FREEZE_MANIFEST = ROOT / "PN6_NATIVE_ARA_FREEZE_MANIFEST.json"
TARGET = ROOT / "PN6_R11_TARGET_AGGREGATES.json"
RESULTS = ROOT / "PN6_NATIVE_ARA_RESULTS.json"
PN4 = ROOT / "PN4_DIRECT_SIEVE_STATE_PATHS.csv"
PN5 = ROOT / "PN5_MULTIPLICATIVE_RUNG_PATHS.csv"
OUTPUT = ROOT / "PN6_NATIVE_ARA_VALIDATION.json"
CHUNK = 12_345_679
BASE_FILTERS = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29)


def digest(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(1_048_576)
            if not block:
                break
            state.update(block)
    return state.hexdigest().upper()


def prime_list(limit: int) -> np.ndarray:
    flags = bytearray(b"\x01") * (limit + 1)
    flags[0:2] = b"\x00\x00"
    for p in range(2, math.isqrt(limit) + 1):
        if flags[p]:
            count = ((limit - p * p) // p) + 1
            flags[p * p : limit + 1 : p] = b"\x00" * count
    return np.fromiter((i for i, flag in enumerate(flags) if flag), dtype=np.int64)


def canonical_phase(values: np.ndarray) -> np.ndarray:
    return np.arccos(np.clip(2.0 * values - 1.0, -1.0, 1.0))


def phase_prediction(theta_previous: np.ndarray, theta_current: np.ndarray, rho: float) -> np.ndarray:
    theta_next = theta_current + rho * (theta_current - theta_previous)
    return (1.0 + np.cos(theta_next)) / 2.0


def path_score(predicted: np.ndarray, actual: np.ndarray, risk: np.ndarray, removed: np.ndarray) -> dict[str, float]:
    start_survival = np.r_[1.0, predicted[:-1]]
    conditional_death = 1.0 - predicted / start_survival
    retained = risk - removed
    loss = -np.sum(removed * np.log2(conditional_death) + retained * np.log2(1.0 - conditional_death)) / risk.sum()
    return {
        "log_loss_bits_per_at_risk_event": float(loss),
        "survival_rmse": float(np.sqrt(np.mean((predicted - actual) ** 2))),
        "phase_rmse_radians": float(np.sqrt(np.mean((canonical_phase(predicted) - canonical_phase(actual)) ** 2))),
        "terminal_prediction": float(predicted[-1]),
        "terminal_observed": float(actual[-1]),
        "terminal_absolute_relative_error": float(abs(predicted[-1] - actual[-1]) / actual[-1]),
    }


def read_sources() -> dict[str, dict[str, np.ndarray]]:
    source: dict[str, dict[str, list[float]]] = {
        rung: {"candidate": [], "edge": [], "j": []} for rung in ("r7", "r8", "r9", "r10")
    }
    with PN4.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rung = row["rung"]
            if rung in ("r7", "r8", "r9"):
                source[rung]["candidate"].append(float(row["candidate_survival"]))
                source[rung]["edge"].append(float(row["edge_survival"]))
                source[rung]["j"].append(float(row["coupling_j"]))
    with PN5.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            source["r10"]["candidate"].append(float(row["candidate_survival"]))
            source["r10"]["edge"].append(float(row["edge_survival"]))
            source["r10"]["j"].append(float(row["edge_j"]))
    return {
        rung: {entity: np.asarray(values, dtype=float) for entity, values in entities.items()}
        for rung, entities in source.items()
    }


def serial(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    return value


def main() -> None:
    frozen = json.loads(FREEZE.read_text(encoding="utf-8"))
    manifest = json.loads(FREEZE_MANIFEST.read_text(encoding="utf-8"))
    target_saved = json.loads(TARGET.read_text(encoding="utf-8"))
    results_saved = json.loads(RESULTS.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, expected: Any = None, observed: Any = None) -> None:
        checks.append({"name": name, "passed": bool(passed), "expected": serial(expected), "observed": serial(observed)})

    check("frozen packet hash", digest(FREEZE) == manifest["files"][FREEZE.name], manifest["files"][FREEZE.name], digest(FREEZE))
    check("PN4 source hash", digest(PN4) == manifest["files"][PN4.name], manifest["files"][PN4.name], digest(PN4))
    check("PN5 source hash", digest(PN5) == manifest["files"][PN5.name], manifest["files"][PN5.name], digest(PN5))
    check("target opened after hash match", target_saved["freeze_evidence"]["matched"] is True, True, target_saved["freeze_evidence"]["matched"])

    low = int(frozen["target"]["low"])
    high = int(frozen["target"]["high"])
    cell_count = int(frozen["target"]["cells"])
    qmax = math.isqrt(high - 1)
    primes = prime_list(qmax)
    active = primes[primes >= 31]
    coordinate = np.log(active / 31.0) / math.log(qmax / 31.0)
    prime_cell = np.minimum(np.floor(coordinate * cell_count).astype(np.int16), cell_count - 1)
    lookup = np.full(qmax + 1, -1, dtype=np.int16)
    lookup[active] = prime_cell
    q_end = np.asarray([active[prime_cell <= c][-1] for c in range(cell_count)], dtype=np.int64)

    cand_death = np.zeros(cell_count, dtype=np.int64)
    edge_death = np.zeros(cell_count, dtype=np.int64)
    cand_total = cand_alive = edge_total = edge_alive = 0
    carry: int | None = None
    chunks = 0
    start_clock = time.perf_counter()

    for lo in range(low, high, CHUNK):
        hi = min(high, lo + CHUNK)
        width = hi - lo
        first = np.zeros(width, dtype=np.uint32)
        for prime_value in active:
            p = int(prime_value)
            offset = ((lo + p - 1) // p) * p - lo
            if offset < width:
                slots = first[offset::p]
                slots[slots == 0] = p

        eligible = np.ones(width, dtype=bool)
        for p in BASE_FILTERS:
            eligible[(-lo) % p :: p] = False
        deaths = first[eligible]
        del first, eligible

        cand_total += int(deaths.size)
        cand_alive += int(np.count_nonzero(deaths == 0))
        positive = deaths[deaths != 0]
        if positive.size:
            cand_death += np.bincount(lookup[positive].astype(np.int64), minlength=cell_count)[:cell_count]

        joined = deaths if carry is None else np.r_[np.uint32(carry), deaths]
        left, right = joined[:-1], joined[1:]
        infinity = np.iinfo(np.uint32).max
        edge_first = np.minimum(np.where(left == 0, infinity, left), np.where(right == 0, infinity, right)).astype(np.uint32)
        edge_first[(left == 0) & (right == 0)] = 0
        edge_total += int(edge_first.size)
        edge_alive += int(np.count_nonzero(edge_first == 0))
        positive_edge = edge_first[edge_first != 0]
        if positive_edge.size:
            edge_death += np.bincount(lookup[positive_edge].astype(np.int64), minlength=cell_count)[:cell_count]
        carry = int(deaths[-1])
        chunks += 1
        if chunks % 10 == 0:
            print(f"validator processed {hi - low:,} / {high - low:,}", flush=True)

    def survival(total: int, removed: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        risk = np.empty(cell_count, dtype=np.int64)
        path = np.empty(cell_count, dtype=float)
        alive = total
        for c in range(cell_count):
            risk[c] = alive
            alive -= int(removed[c])
            path[c] = alive / total
        return risk, path

    cand_risk, cand_path = survival(cand_total, cand_death)
    edge_risk, edge_path = survival(edge_total, edge_death)
    elapsed = time.perf_counter() - start_clock

    check("validator uses distinct chunk size", CHUNK != int(target_saved["construction"]["chunk_size"]), "different", {"primary": target_saved["construction"]["chunk_size"], "validator": CHUNK})
    check("qmax", qmax == int(target_saved["construction"]["qmax"]), target_saved["construction"]["qmax"], qmax)
    check("q_end", np.array_equal(q_end, np.asarray(target_saved["q_end"])), target_saved["q_end"], q_end)
    check("candidate initial", cand_total == target_saved["candidate"]["n0"], target_saved["candidate"]["n0"], cand_total)
    check("candidate terminal", cand_alive == target_saved["candidate"]["terminal_survivors"], target_saved["candidate"]["terminal_survivors"], cand_alive)
    check("candidate deaths", np.array_equal(cand_death, np.asarray(target_saved["candidate"]["deaths"])), target_saved["candidate"]["deaths"], cand_death)
    check("candidate risk", np.array_equal(cand_risk, np.asarray(target_saved["candidate"]["before"])), target_saved["candidate"]["before"], cand_risk)
    check("candidate path", np.allclose(cand_path, np.asarray(target_saved["candidate"]["survival"]), atol=0, rtol=0), target_saved["candidate"]["survival"], cand_path)
    check("edge initial", edge_total == target_saved["edge"]["n0"], target_saved["edge"]["n0"], edge_total)
    check("edge is candidate minus one", edge_total == cand_total - 1, cand_total - 1, edge_total)
    check("edge terminal", edge_alive == target_saved["edge"]["terminal_survivors"], target_saved["edge"]["terminal_survivors"], edge_alive)
    check("edge deaths", np.array_equal(edge_death, np.asarray(target_saved["edge"]["deaths"])), target_saved["edge"]["deaths"], edge_death)
    check("edge risk", np.array_equal(edge_risk, np.asarray(target_saved["edge"]["before"])), target_saved["edge"]["before"], edge_risk)
    check("edge path", np.allclose(edge_path, np.asarray(target_saved["edge"]["survival"]), atol=0, rtol=0), target_saved["edge"]["survival"], edge_path)
    check("candidate accounting", cand_total == cand_alive + int(cand_death.sum()), cand_total, cand_alive + int(cand_death.sum()))
    check("edge accounting", edge_total == edge_alive + int(edge_death.sum()), edge_total, edge_alive + int(edge_death.sum()))

    source = read_sources()
    theta = {
        rung: {entity: canonical_phase(source[rung][entity]) for entity in ("candidate", "edge")}
        for rung in ("r7", "r8", "r9", "r10")
    }
    d9 = {entity: theta["r9"][entity] - theta["r8"][entity] for entity in ("candidate", "edge")}
    d10 = {entity: theta["r10"][entity] - theta["r9"][entity] for entity in ("candidate", "edge")}
    numerator = sum(float(np.dot(d9[entity], d10[entity])) for entity in ("candidate", "edge"))
    denominator = sum(float(np.dot(d9[entity], d9[entity])) for entity in ("candidate", "edge"))
    rho = numerator / denominator
    rho_candidate = float(np.dot(d9["candidate"], d10["candidate"]) / np.dot(d9["candidate"], d9["candidate"]))
    rho_edge = float(np.dot(d9["edge"], d10["edge"]) / np.dot(d9["edge"], d9["edge"]))
    check("shared rho", math.isclose(rho, frozen["fitted_parameters"]["rho_shared"], abs_tol=1e-14), frozen["fitted_parameters"]["rho_shared"], rho)
    check("candidate rho", math.isclose(rho_candidate, frozen["fitted_parameters"]["rho_candidate_sensitivity"], abs_tol=1e-14), frozen["fitted_parameters"]["rho_candidate_sensitivity"], rho_candidate)
    check("edge rho", math.isclose(rho_edge, frozen["fitted_parameters"]["rho_edge_sensitivity"], abs_tol=1e-14), frozen["fitted_parameters"]["rho_edge_sensitivity"], rho_edge)

    predictions = {
        "candidate": {
            "home_r10": source["r10"]["candidate"],
            "direct_log_rung": source["r10"]["candidate"] ** 2 / source["r9"]["candidate"],
            "circle_secant_rho1": phase_prediction(theta["r9"]["candidate"], theta["r10"]["candidate"], 1.0),
            "circle_shared_rho_primary": phase_prediction(theta["r9"]["candidate"], theta["r10"]["candidate"], rho),
            "circle_candidate_rho_sensitivity": phase_prediction(theta["r9"]["candidate"], theta["r10"]["candidate"], rho_candidate),
        },
        "edge": {
            "home_r10": source["r10"]["edge"],
            "direct_log_rung": source["r10"]["edge"] ** 2 / source["r9"]["edge"],
            "circle_secant_rho1": phase_prediction(theta["r9"]["edge"], theta["r10"]["edge"], 1.0),
            "circle_shared_rho_primary": phase_prediction(theta["r9"]["edge"], theta["r10"]["edge"], rho),
            "circle_edge_rho_sensitivity": phase_prediction(theta["r9"]["edge"], theta["r10"]["edge"], rho_edge),
        },
    }
    j11 = source["r10"]["j"] + rho * (source["r10"]["j"] - source["r9"]["j"])
    predictions["edge"]["circle_candidate_plus_j_secondary"] = predictions["candidate"]["circle_shared_rho_primary"] ** 2 * np.exp(j11)

    for entity, models in predictions.items():
        for model, values in models.items():
            expected = np.asarray(frozen["predictions"][entity][model])
            check(f"prediction {entity}/{model}", np.allclose(values, expected, atol=1e-14, rtol=1e-14), expected, values)

    actual = {"candidate": cand_path, "edge": edge_path}
    risk = {"candidate": cand_risk, "edge": edge_risk}
    removed = {"candidate": cand_death, "edge": edge_death}
    scores: dict[str, dict[str, dict[str, float]]] = {"candidate": {}, "edge": {}}
    for entity, models in predictions.items():
        for model, values in models.items():
            scores[entity][model] = path_score(values, actual[entity], risk[entity], removed[entity])
            for metric, observed_value in scores[entity][model].items():
                expected_value = results_saved["scores"][entity][model][metric]
                check(f"score {entity}/{model}/{metric}", math.isclose(observed_value, expected_value, abs_tol=1e-13, rel_tol=1e-13), expected_value, observed_value)

    observed_theta = {entity: canonical_phase(actual[entity]) for entity in ("candidate", "edge")}
    rho_next = {}
    for entity in ("candidate", "edge"):
        next_delta = observed_theta[entity] - theta["r10"][entity]
        rho_next[entity] = float(np.dot(d10[entity], next_delta) / np.dot(d10[entity], d10[entity]))
        check(f"observed rho {entity}", math.isclose(rho_next[entity], results_saved["observed_rho"][entity], abs_tol=1e-13), results_saved["observed_rho"][entity], rho_next[entity])

    primary_c = scores["candidate"]["circle_shared_rho_primary"]
    primary_e = scores["edge"]["circle_shared_rho_primary"]
    criteria = {
        "P1_candidate_primary_beats_home_terminal_under_1pct_phase_under_0_015": primary_c["log_loss_bits_per_at_risk_event"] < scores["candidate"]["home_r10"]["log_loss_bits_per_at_risk_event"] and primary_c["terminal_absolute_relative_error"] < .01 and primary_c["phase_rmse_radians"] < .015,
        "P2_edge_primary_beats_home_terminal_under_1pct_phase_under_0_015": primary_e["log_loss_bits_per_at_risk_event"] < scores["edge"]["home_r10"]["log_loss_bits_per_at_risk_event"] and primary_e["terminal_absolute_relative_error"] < .01 and primary_e["phase_rmse_radians"] < .015,
        "P3_candidate_primary_beats_direct_native_log": primary_c["log_loss_bits_per_at_risk_event"] < scores["candidate"]["direct_log_rung"]["log_loss_bits_per_at_risk_event"],
        "P4_edge_primary_beats_direct_native_log": primary_e["log_loss_bits_per_at_risk_event"] < scores["edge"]["direct_log_rung"]["log_loss_bits_per_at_risk_event"],
        "P5_shared_withdrawal_recurs": abs(rho_next["candidate"] - rho) < .15 and abs(rho_next["edge"] - rho) < .15 and abs(rho_next["candidate"] - rho_next["edge"]) < .10,
        "P6_primary_paths_valid_monotone_unrepaired": all(np.all(np.isfinite(predictions[e]["circle_shared_rho_primary"])) and np.all((predictions[e]["circle_shared_rho_primary"] >= 0) & (predictions[e]["circle_shared_rho_primary"] <= 1)) and np.all(np.diff(predictions[e]["circle_shared_rho_primary"]) <= 0) for e in ("candidate", "edge")),
        "P7_native_pair_routes_close": frozen["fitted_parameters"]["pretarget_pair_route_rmse"] < .002 and primary_e["terminal_absolute_relative_error"] < .01 and scores["edge"]["circle_candidate_plus_j_secondary"]["terminal_absolute_relative_error"] < .01,
    }
    for name, value in criteria.items():
        check(f"criterion {name}", value == results_saved["criteria"][name], results_saved["criteria"][name], value)

    complete = all(item["passed"] for item in checks)
    validation = {
        "test_id": frozen["test_id"],
        "validator_independence": {
            "imports_primary_builder_or_scorer": False,
            "prime_generation": "standard-library bytearray sieve",
            "target_construction": "independently coded segmented smallest-factor sieve",
            "chunk_size": CHUNK,
            "primary_chunk_size": target_saved["construction"]["chunk_size"],
            "elapsed_seconds": elapsed,
            "native_only": True,
        },
        "summary": {"checks_passed": sum(item["passed"] for item in checks), "checks_total": len(checks), "complete": complete},
        "recomputed_counts": {"candidate_initial": cand_total, "candidate_terminal": cand_alive, "edge_initial": edge_total, "edge_terminal": edge_alive},
        "recomputed_rho": {"frozen_shared": rho, "observed_candidate": rho_next["candidate"], "observed_edge": rho_next["edge"]},
        "recomputed_criteria": criteria,
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(serial(validation), indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "summary": validation["summary"],
        "elapsed_seconds": elapsed,
        "recomputed_counts": validation["recomputed_counts"],
        "recomputed_rho": validation["recomputed_rho"],
        "validation_sha256": digest(OUTPUT),
    }, indent=2))
    if not complete:
        raise AssertionError("Independent validation failed; inspect output")


if __name__ == "__main__":
    main()
