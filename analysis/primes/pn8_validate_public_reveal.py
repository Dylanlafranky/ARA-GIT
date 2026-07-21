"""Independent numerical validator for PN8; does not import the prediction or scoring scripts."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
PATHS = {
    "protocol": HERE / "PN8_POWER_OF_TEN_PUBLIC_REVEAL_PROTOCOL.md",
    "inputs": HERE / "PN8_BELOW_BOUNDARY_INPUTS.json",
    "model": HERE / "PN7C_FROZEN_MODELS.npz",
    "predictions": HERE / "PN8_PRE_REVEAL_PREDICTIONS.json",
    "reveal": HERE / "PN8_PUBLIC_REVEAL_SOURCE.json",
    "results": HERE / "PN8_POWER_OF_TEN_PUBLIC_REVEAL_RESULTS.json",
    "prime_validation": HERE / "PN8_PRIME_BOUNDARY_VALIDATION.json",
}
EXPECTED = {
    "protocol": "E6FB6D621DB98298E9D14E167EDB6345EB114199BD06DA54258C6F4D38813AE9",
    "inputs": "327E14D1CEF9EE4770889D565DEE2C36B41FF078204FFE3574166F887FFFD7FC",
    "model": "9141AA398C6A6694C3C5F3ECA954681D4AD8091C01310D13C6703DB30668F3A2",
    "predictions": "AA26297D54D1BB52203A9A77B1F981977D893C6630D739C521E906459391A7BA",
    "reveal": "E73183E4573D426CA2E8D874E1BD64054DDA5758335879EE68B3C39595C85004",
    "results": "CA82E944280B7138283B1924BE945ACF32D087226A79AED85FE1BE805164338B",
    "prime_validation": "BB4BCE63A1632578090FEB8187092EA78DB712554316C65E0B37801D14209E22",
}
BINS = 24
ALPHA = 0.5
RAW_LAMBDA = 64.0
RAW_ALPHABET = 1025
MODELS = ("ARA-IID", "ARA-M1", "ARA-M2", "RawGap-M1")
OUTPUT = HERE / "PN8_POWER_OF_TEN_PUBLIC_REVEAL_VALIDATION.json"


def sha256(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(3_000_001), b""):
            state.update(block)
    return state.hexdigest().upper()


def bin_state(left: int, right: int) -> int:
    return min(BINS * right // (left + right), BINS - 1)


def independent_models(model):
    count0 = np.asarray(model["b24__marginal"], dtype=np.longdouble)
    count1 = np.asarray(model["b24__m1"], dtype=np.longdouble)
    count2 = np.asarray(model["b24__m2"], dtype=np.longdouble)
    iid = (count0 + ALPHA) / (count0.sum() + ALPHA * BINS)
    m1 = (count1 + ALPHA) / (count1.sum(axis=1, keepdims=True) + ALPHA * BINS)
    m2 = (count2 + ALPHA) / (count2.sum(axis=2, keepdims=True) + ALPHA * BINS)
    raw_counts = np.asarray(model["raw__marginal"], dtype=np.longdouble)
    raw_pair = np.asarray(model["raw__transition"], dtype=np.longdouble)
    raw_base = np.zeros(RAW_ALPHABET, dtype=np.longdouble)
    raw_base[1:] = (raw_counts[1:] + ALPHA) / (raw_counts[1:].sum() + ALPHA * (RAW_ALPHABET - 1))
    row_sum = raw_pair.sum(axis=1, keepdims=True)
    raw = (raw_pair + RAW_LAMBDA * raw_base[None, :]) / (row_sum + RAW_LAMBDA)
    raw[row_sum[:, 0] == 0] = raw_base
    return iid, m1, m2, raw_base, raw


def raw_projection(current: int, base: np.ndarray, transition: np.ndarray) -> np.ndarray:
    source = transition[current] if current < RAW_ALPHABET else base
    answer = np.zeros(BINS, dtype=np.longdouble)
    for next_gap, probability in enumerate(source):
        if probability == 0:
            continue
        category = bin_state(current, next_gap) if current + next_gap > 0 else 0
        answer[category] += probability
    return answer


def main() -> None:
    checks = []

    def check(name: str, passed: bool, observed=None, expected=None):
        checks.append({"name": name, "passed": bool(passed), "observed": observed, "expected": expected})

    for label, path in PATHS.items():
        observed = sha256(path)
        check(f"hash_{label}", observed == EXPECTED[label], observed, EXPECTED[label])
    check("prediction_file_precedes_reveal_file", PATHS["predictions"].stat().st_mtime_ns < PATHS["reveal"].stat().st_mtime_ns)

    inputs = json.loads(PATHS["inputs"].read_text(encoding="utf-8"))
    predictions = json.loads(PATHS["predictions"].read_text(encoding="utf-8"))
    reveal = json.loads(PATHS["reveal"].read_text(encoding="utf-8"))
    results = json.loads(PATHS["results"].read_text(encoding="utf-8"))
    prime_validation = json.loads(PATHS["prime_validation"].read_text(encoding="utf-8"))
    check("post_reveal_prime_checks", prime_validation["all_passed"], prime_validation["checks_passed"], prime_validation["checks_total"])
    check("directional_barrier", inputs["directional_barrier"]["candidates_at_or_above_boundary_tested"] == 0)
    check("prediction_lookup_barrier", predictions["boundaries"]["public_target_source_queried"] is False)
    check("public_lookup_after_freeze_flag", reveal["lookup_performed_after_prediction_freeze"] is True)

    input_by_n = {row["exponent"]: row for row in inputs["targets"]}
    prediction_by_n = {row["exponent"]: row for row in predictions["forecasts"]}
    reveal_by_n = {row["exponent"]: row for row in reveal["reveals"]}
    result_by_n = {row["exponent"]: row for row in results["targets"]}
    check("target_exponents", list(input_by_n) == [50, 100, 150, 200, 250], list(input_by_n), [50, 100, 150, 200, 250])
    model = np.load(PATHS["model"], allow_pickle=False)
    iid, m1, m2, raw_base, raw = independent_models(model)
    log_sums = {name: 0.0 for name in MODELS}
    zero_counts = {name: 0 for name in MODELS}
    top1 = {name: 0 for name in MODELS}
    top3 = {name: 0 for name in MODELS}
    m2_wins = 0
    for exponent in input_by_n:
        source = input_by_n[exponent]
        saved_prediction = prediction_by_n[exponent]
        public = reveal_by_n[exponent]
        scored = result_by_n[exponent]
        known_primes = [int(value) for value in source["primes"]]
        gaps = [known_primes[i + 1] - known_primes[i] for i in range(3)]
        previous = bin_state(gaps[0], gaps[1])
        current = bin_state(gaps[1], gaps[2])
        check(f"n{exponent}_known_gaps", gaps == saved_prediction["known_gaps"], gaps, saved_prediction["known_gaps"])
        check(f"n{exponent}_previous_context", previous == saved_prediction["known_context_bins"]["previous"])
        check(f"n{exponent}_current_context", current == saved_prediction["known_context_bins"]["current"])
        distributions = {
            "ARA-IID": iid,
            "ARA-M1": m1[current],
            "ARA-M2": m2[previous, current],
            "RawGap-M1": raw_projection(gaps[2], raw_base, raw),
        }
        boundary = 10 ** exponent
        target_prime = int(public["first_prime_above_boundary"])
        crossing = target_prime - known_primes[-1]
        check(f"n{exponent}_public_offset", target_prime - boundary == public["oeis_offset_above_10_power"])
        check(f"n{exponent}_crossing_gap", crossing == scored["crossing_gap"], crossing, scored["crossing_gap"])
        target_bin = bin_state(gaps[2], crossing)
        check(f"n{exponent}_target_bin", target_bin == scored["target_bin"], target_bin, scored["target_bin"])
        for name, distribution in distributions.items():
            saved_values = np.asarray(saved_prediction["distributions"][name]["probabilities"], dtype=np.longdouble)
            maximum_error = float(np.max(np.abs(distribution - saved_values)))
            check(f"n{exponent}_{name}_distribution", maximum_error < 2e-16, maximum_error, 2e-16)
            probability = float(distribution[target_bin])
            saved_score = scored["models"][name]
            check(f"n{exponent}_{name}_target_probability", abs(probability - saved_score["target_probability"]) < 2e-16,
                  probability, saved_score["target_probability"])
            if probability == 0:
                zero_counts[name] += 1
                check(f"n{exponent}_{name}_infinite_log_loss", saved_score["infinite_log_loss"] and saved_score["log_loss_bits"] is None)
            else:
                loss = -math.log2(probability)
                log_sums[name] += loss
                check(f"n{exponent}_{name}_log_loss", abs(loss - saved_score["log_loss_bits"]) < 2e-13, loss, saved_score["log_loss_bits"])
            order = np.argsort(-distribution, kind="stable")
            hit1 = target_bin == int(order[0])
            hit3 = target_bin in [int(value) for value in order[:3]]
            top1[name] += int(hit1)
            top3[name] += int(hit3)
            check(f"n{exponent}_{name}_top1", hit1 == saved_score["top1_hit"])
            check(f"n{exponent}_{name}_top3", hit3 == saved_score["top3_hit"])
        m2_wins += int(float(distributions["ARA-M2"][target_bin]) > float(distributions["ARA-M1"][target_bin]))

    reconstructed_aggregate = {}
    for name in MODELS:
        mean = log_sums[name] / 5 if zero_counts[name] == 0 else None
        reconstructed_aggregate[name] = {"mean": mean, "top1": top1[name], "top3": top3[name], "zero": zero_counts[name]}
        expected = results["aggregate"][name]
        check(f"aggregate_{name}_mean", (mean is None and expected["mean_log_loss_bits"] is None) or
              (mean is not None and abs(mean - expected["mean_log_loss_bits"]) < 2e-13), mean, expected["mean_log_loss_bits"])
        check(f"aggregate_{name}_top1", top1[name] == expected["top1_hits"], top1[name], expected["top1_hits"])
        check(f"aggregate_{name}_top3", top3[name] == expected["top3_hits"], top3[name], expected["top3_hits"])
        check(f"aggregate_{name}_zero", zero_counts[name] == expected["zero_probability_targets"], zero_counts[name], expected["zero_probability_targets"])
    q = {
        "Q1": top3["ARA-M2"] >= 2,
        "Q2": reconstructed_aggregate["ARA-M2"]["mean"] < reconstructed_aggregate["ARA-M1"]["mean"],
        "Q3": reconstructed_aggregate["ARA-M2"]["mean"] < reconstructed_aggregate["ARA-IID"]["mean"],
        "Q4": m2_wins >= 3,
    }
    for name, passed in q.items():
        check(f"condition_{name}", passed == results["conditions"][name]["passed"], passed, results["conditions"][name]["passed"])
    check("overall_gate", all(q.values()) == results["promising_enough_to_scale_under_registered_Q1_Q4"])

    packet = {
        "test_id": "PN8/INDEPENDENT-NUMERICAL-VALIDATION-v1",
        "validator_sha256": sha256(Path(__file__)),
        "checks_total": len(checks),
        "checks_passed": sum(row["passed"] for row in checks),
        "all_passed": all(row["passed"] for row in checks),
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: packet[key] for key in ("checks_total", "checks_passed", "all_passed")}, indent=2))
    if not packet["all_passed"]:
        raise AssertionError("PN8 independent numerical validation failed")


if __name__ == "__main__":
    main()
