"""Score the PN8 pre-reveal probability packets against the saved OEIS reveal."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN8_POWER_OF_TEN_PUBLIC_REVEAL_PROTOCOL.md"
INPUTS = HERE / "PN8_BELOW_BOUNDARY_INPUTS.json"
PREDICTIONS = HERE / "PN8_PRE_REVEAL_PREDICTIONS.json"
REVEAL = HERE / "PN8_PUBLIC_REVEAL_SOURCE.json"
OUTPUT = HERE / "PN8_POWER_OF_TEN_PUBLIC_REVEAL_RESULTS.json"
CSV_OUTPUT = HERE / "PN8_POWER_OF_TEN_PUBLIC_REVEAL_SCORES.csv"
EXPECTED = {
    "protocol": "E6FB6D621DB98298E9D14E167EDB6345EB114199BD06DA54258C6F4D38813AE9",
    "inputs": "327E14D1CEF9EE4770889D565DEE2C36B41FF078204FFE3574166F887FFFD7FC",
    "predictions": "AA26297D54D1BB52203A9A77B1F981977D893C6630D739C521E906459391A7BA",
    "reveal": "E73183E4573D426CA2E8D874E1BD64054DDA5758335879EE68B3C39595C85004",
}
MODELS = ("ARA-IID", "ARA-M1", "ARA-M2", "RawGap-M1")
BINS = 24


def sha256(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as handle:
        for part in iter(lambda: handle.read(1 << 20), b""):
            state.update(part)
    return state.hexdigest().upper()


def category(left: int, right: int) -> int:
    return min(BINS * right // (left + right), BINS - 1)


def score_distribution(probabilities: list[float], target: int, top1: int, top3: list[int]) -> dict:
    probability = float(probabilities[target])
    rank = 1 + sum(value > probability for value in probabilities)
    return {
        "target_probability": probability,
        "log_loss_bits": -math.log2(probability) if probability > 0 else None,
        "infinite_log_loss": probability == 0,
        "top1_hit": target == top1,
        "top3_hit": target in top3,
        "target_bin_rank_best_tie": rank,
    }


def main() -> None:
    for label, path in (("protocol", PROTOCOL), ("inputs", INPUTS), ("predictions", PREDICTIONS), ("reveal", REVEAL)):
        observed = sha256(path)
        if observed != EXPECTED[label]:
            raise RuntimeError(f"{label} hash mismatch: {observed}")

    inputs = json.loads(INPUTS.read_text(encoding="utf-8"))
    predictions = json.loads(PREDICTIONS.read_text(encoding="utf-8"))
    reveal = json.loads(REVEAL.read_text(encoding="utf-8"))
    input_by_n = {int(row["exponent"]): row for row in inputs["targets"]}
    forecast_by_n = {int(row["exponent"]): row for row in predictions["forecasts"]}
    reveal_by_n = {int(row["exponent"]): row for row in reveal["reveals"]}
    if list(input_by_n) != [50, 100, 150, 200, 250] or set(input_by_n) != set(forecast_by_n) or set(input_by_n) != set(reveal_by_n):
        raise AssertionError("Target-set mismatch")

    rows = []
    aggregate = {name: {"log_loss_sum": 0.0, "zero_probability_targets": 0, "top1_hits": 0, "top3_hits": 0} for name in MODELS}
    m2_beats_m1_cases = 0
    for exponent in input_by_n:
        input_row = input_by_n[exponent]
        forecast = forecast_by_n[exponent]
        revealed = reveal_by_n[exponent]
        boundary = int(input_row["boundary"])
        previous_prime = int(input_row["greatest_prime_below_boundary"])
        target_prime = int(revealed["first_prime_above_boundary"])
        crossing_gap = target_prime - previous_prime
        expected_crossing = int(input_row["distance_from_boundary"]) + int(revealed["oeis_offset_above_10_power"])
        if crossing_gap != expected_crossing or not (previous_prime < boundary < target_prime):
            raise AssertionError("Crossing-gap reconstruction failed")
        current_gap = int(forecast["known_gaps"][-1])
        target_bin = category(current_gap, crossing_gap)
        continuous_state = 2 * crossing_gap / (current_gap + crossing_gap)
        model_scores = {}
        for name in MODELS:
            distribution = forecast["distributions"][name]
            score = score_distribution(
                distribution["probabilities"], target_bin, distribution["top1_bin"], distribution["top3_bins"]
            )
            model_scores[name] = score
            if score["log_loss_bits"] is None:
                aggregate[name]["zero_probability_targets"] += 1
            else:
                aggregate[name]["log_loss_sum"] += score["log_loss_bits"]
            aggregate[name]["top1_hits"] += int(score["top1_hit"])
            aggregate[name]["top3_hits"] += int(score["top3_hit"])
        if model_scores["ARA-M2"]["target_probability"] > model_scores["ARA-M1"]["target_probability"]:
            m2_beats_m1_cases += 1

        top3_range_hit = False
        for interval in forecast["ara_m2_top3_gap_and_number_ranges"]:
            low = interval["gap_range"]["all_positive_even_gaps"]["minimum"]
            high = interval["gap_range"]["all_positive_even_gaps"]["maximum"]
            if crossing_gap >= low and (high is None or crossing_gap <= high):
                top3_range_hit = True
        rows.append({
            "exponent": exponent,
            "boundary": str(boundary),
            "prior_prime": str(previous_prime),
            "public_offset_above_boundary": int(revealed["oeis_offset_above_10_power"]),
            "revealed_prime": str(target_prime),
            "known_current_gap": current_gap,
            "crossing_gap": crossing_gap,
            "target_continuous_ara_state": continuous_state,
            "target_bin": target_bin,
            "ara_m2_top3_range_hit": top3_range_hit,
            "models": model_scores,
        })
        print(json.dumps({
            "exponent": exponent,
            "crossing_gap": crossing_gap,
            "target_state": continuous_state,
            "target_bin": target_bin,
            "ARA-M2": model_scores["ARA-M2"],
        }, indent=2), flush=True)

    for name in MODELS:
        zero_probability_targets = aggregate[name]["zero_probability_targets"]
        aggregate[name] = {
            "mean_log_loss_bits": aggregate[name]["log_loss_sum"] / len(rows) if zero_probability_targets == 0 else None,
            "infinite_mean_log_loss": zero_probability_targets > 0,
            "zero_probability_targets": zero_probability_targets,
            "top1_hits": aggregate[name]["top1_hits"],
            "top3_hits": aggregate[name]["top3_hits"],
            "targets": len(rows),
        }
    conditions = {
        "Q1": {"passed": aggregate["ARA-M2"]["top3_hits"] >= 2, "ara_m2_top3_hits": aggregate["ARA-M2"]["top3_hits"], "required": 2},
        "Q2": {"passed": aggregate["ARA-M2"]["mean_log_loss_bits"] < aggregate["ARA-M1"]["mean_log_loss_bits"],
               "ara_m2_bits": aggregate["ARA-M2"]["mean_log_loss_bits"], "ara_m1_bits": aggregate["ARA-M1"]["mean_log_loss_bits"]},
        "Q3": {"passed": aggregate["ARA-M2"]["mean_log_loss_bits"] < aggregate["ARA-IID"]["mean_log_loss_bits"],
               "ara_m2_bits": aggregate["ARA-M2"]["mean_log_loss_bits"], "ara_iid_bits": aggregate["ARA-IID"]["mean_log_loss_bits"]},
        "Q4": {"passed": m2_beats_m1_cases >= 3, "m2_higher_target_probability_cases": m2_beats_m1_cases, "required": 3},
        "Q5_diagnostic": {"ara_m2_mean_log_loss_bits": aggregate["ARA-M2"]["mean_log_loss_bits"],
                          "raw_gap_m1_mean_log_loss_bits": aggregate["RawGap-M1"]["mean_log_loss_bits"],
                          "raw_gap_m1_infinite_mean_log_loss": aggregate["RawGap-M1"]["infinite_mean_log_loss"],
                          "ara_m2_top3_hits": aggregate["ARA-M2"]["top3_hits"], "raw_gap_m1_top3_hits": aggregate["RawGap-M1"]["top3_hits"]},
    }
    packet = {
        "test_id": "PN8/POWER-OF-TEN-PUBLIC-REVEAL/PILOT-v1",
        "hashes": {**EXPECTED, "scorer": sha256(Path(__file__))},
        "source": reveal["source"],
        "targets": rows,
        "aggregate": aggregate,
        "uniform_24_bin_log_loss_bits": math.log2(BINS),
        "conditions": conditions,
        "promising_enough_to_scale_under_registered_Q1_Q4": all(conditions[f"Q{i}"]["passed"] for i in range(1, 5)),
        "boundaries": {
            "effectiveness_estimate_from_five_cases": False,
            "exact_prime_generation_test": False,
            "adult_slow_wave_test": False,
            "r12_opened": False,
            "p31_wheel_opened": False,
        },
    }
    OUTPUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    with CSV_OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["exponent", "model", "target_bin", "target_probability", "log_loss_bits", "top1_hit", "top3_hit", "target_bin_rank_best_tie"])
        for row in rows:
            for name in MODELS:
                score = row["models"][name]
                writer.writerow([row["exponent"], name, row["target_bin"], score["target_probability"], score["log_loss_bits"], score["top1_hit"], score["top3_hit"], score["target_bin_rank_best_tie"]])
    print(json.dumps({"aggregate": aggregate, "conditions": conditions, "results_sha256": sha256(OUTPUT)}, indent=2), flush=True)


if __name__ == "__main__":
    main()
