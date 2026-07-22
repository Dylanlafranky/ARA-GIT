"""PN25 prospective test of the corrected mod-14 pair-ridge coordinate."""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

from pn24_nearest_handover_cascade import cascade, next_prime, sieve_primes


HERE = Path(__file__).resolve().parent
PROTOCOL = "PN25_PAIR_RIDGE_COMPRESSION_PROTOCOL_v1_FROZEN.md"
DEVELOPMENT = HERE / "PN24_NEAREST_HANDOVER_CASCADE_ANCHORS.csv"
RESULTS = HERE / "PN25_PAIR_RIDGE_COMPRESSION_RESULTS.json"
TARGETS = HERE / "PN25_PAIR_RIDGE_COMPRESSION_TARGETS.csv"
GROUPS = HERE / "PN25_PAIR_RIDGE_COMPRESSION_GROUPS.csv"
SCORES = HERE / "PN25_PAIR_RIDGE_COMPRESSION_SCORES.csv"

TARGET_RANGES = (
    ("low", 61_000_000, 61_500_000, 25001),
    ("middle", 61_000_000_000, 61_000_500_000, 25002),
    ("high", 610_000_000_000, 610_000_500_000, 25003),
)
N_PER_RANGE = 2_000
PERMUTATIONS = 10_000
PERMUTATION_SEED = 25100
PAIR_REPS = (1, 3, 5)
LANES = (1, 3, 5, 9, 11, 13)


def lane_state(value: int) -> dict:
    residue = value % 14
    if residue not in LANES:
        raise ValueError(f"{value} is not a mod-14 survivor")
    representative = min(residue, 14 - residue)
    orientation = "left" if residue < 7 else "right"
    odds = Fraction(representative, 14 - representative)
    closeness = Fraction(representative, 7)
    ara_oriented = Fraction(residue, 7)
    return {
        "residue": residue,
        "pair_representative": representative,
        "orientation": orientation,
        "odds": odds,
        "closeness": closeness,
        "ara_oriented": ara_oriented,
    }


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def correlation(xs: list[float], ys: list[float]) -> float:
    mx = statistics.fmean(xs)
    my = statistics.fmean(ys)
    numerator = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    denominator = math.sqrt(
        sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)
    )
    return numerator / denominator if denominator else 0.0


def fit_rates(rows: list[dict], outcome: str, model: str) -> dict[str, float]:
    groups: dict[str, list[int]] = defaultdict(list)
    for row in rows:
        if model == "global":
            key = "all"
        elif model == "orientation":
            key = row["orientation"]
        elif model == "pair":
            key = str(row["pair_representative"])
        elif model == "lane":
            key = str(row["residue"])
        else:
            raise ValueError(model)
        groups[key].append(int(row[outcome]))
    return {key: statistics.fmean(values) for key, values in groups.items()}


def prediction_key(row: dict, model: str) -> str:
    if model == "global":
        return "all"
    if model == "orientation":
        return row["orientation"]
    if model == "pair":
        return str(row["pair_representative"])
    if model == "lane":
        return str(row["residue"])
    raise ValueError(model)


def brier(rows: list[dict], outcome: str, model: str, rates: dict[str, float]) -> float:
    return statistics.fmean(
        (rates[prediction_key(row, model)] - int(row[outcome])) ** 2
        for row in rows
    )


def development_rows() -> list[dict]:
    rows = []
    for source in read_csv(DEVELOPMENT):
        if source["cohort"] != "sample":
            continue
        state = lane_state(int(source["initial_upper"]))
        h = int(source["handover_events"])
        rows.append({
            "residue": state["residue"],
            "pair_representative": state["pair_representative"],
            "orientation": state["orientation"],
            "Y0": int(h == 0),
            "Y3": int(h <= 2),
        })
    if len(rows) != 2_000:
        raise AssertionError("unexpected PN24 development row count")
    return rows


def exact_coordinate_checks() -> list[dict]:
    checks = []
    for representative in PAIR_REPS:
        odds = Fraction(representative, 14 - representative)
        converted = Fraction(2) * odds / (1 + odds)
        expected = Fraction(representative, 7)
        opposite = Fraction(14 - representative, 7)
        checks.append({
            "pair": [representative, 14 - representative],
            "odds": str(odds),
            "converted_A": str(converted),
            "converted_B": str(opposite),
            "expected_A": str(expected),
            "conversion_exact": converted == expected,
            "te_ara_sum_exact": converted + opposite == 2,
            "mirror_closeness_exact": (
                lane_state(representative)["closeness"]
                == lane_state(14 - representative)["closeness"]
            ),
            "mirror_orientation_opposite": (
                lane_state(representative)["orientation"]
                != lane_state(14 - representative)["orientation"]
            ),
        })
    ridge_odds = Fraction(7, 7)
    ridge_A = Fraction(2) * ridge_odds / (1 + ridge_odds)
    checks.append({
        "pair": [7, 7],
        "odds": str(ridge_odds),
        "converted_A": str(ridge_A),
        "converted_B": str(2 - ridge_A),
        "expected_A": "1",
        "conversion_exact": ridge_A == 1,
        "te_ara_sum_exact": ridge_A + (2 - ridge_A) == 2,
        "excluded_by_gate_7": 7 % 7 == 0,
    })
    return checks


def build_targets(primes: list[int]) -> list[dict]:
    rows = []
    for scale, low, high, seed in TARGET_RANGES:
        anchors = sorted(random.Random(seed).sample(range(low, high), N_PER_RANGE))
        for anchor in anchors:
            result, events = cascade(anchor, primes)
            truth = next_prime(anchor)
            if result["final_candidate"] != truth:
                raise AssertionError("cascade/truth mismatch")
            candidates = [result["initial_upper"]] + [event["new_candidate"] for event in events]
            states = [lane_state(value) for value in candidates]
            initial = states[0]
            final = states[-1]
            h = len(events)
            closeness_path = [float(state["closeness"]) for state in states]
            increases = sum(b > a for a, b in zip(closeness_path, closeness_path[1:]))
            decreases = sum(b < a for a, b in zip(closeness_path, closeness_path[1:]))
            rows.append({
                "scale": scale,
                "anchor": anchor,
                "initial_candidate": result["initial_upper"],
                "true_next_prime": truth,
                "initial_delta": result["initial_forward_delta"],
                "final_delta": result["final_delta"],
                "handover_events": h,
                "candidate_states": h + 1,
                "Y0": int(h == 0),
                "Y3": int(h <= 2),
                "residue": initial["residue"],
                "pair_representative": initial["pair_representative"],
                "orientation": initial["orientation"],
                "odds": str(initial["odds"]),
                "ara_oriented": str(initial["ara_oriented"]),
                "closeness": str(initial["closeness"]),
                "closeness_float": float(initial["closeness"]),
                "final_residue": final["residue"],
                "final_pair_representative": final["pair_representative"],
                "final_closeness": str(final["closeness"]),
                "final_closeness_float": float(final["closeness"]),
                "delta_closeness": float(final["closeness"] - initial["closeness"]),
                "closeness_increase_steps": increases,
                "closeness_decrease_steps": decreases,
                "candidate_path": "|".join(map(str, candidates)),
                "closeness_path": "|".join(str(state["closeness"]) for state in states),
                "gate_path": "|".join(str(event["gate"]) for event in events),
                "total_nonbase_gate_crossings": result["total_nonbase_gate_crossings"],
            })
    return rows


def group_summaries(rows: list[dict]) -> list[dict]:
    output = []
    for scale in [name for name, *_ in TARGET_RANGES] + ["pooled"]:
        subset = rows if scale == "pooled" else [row for row in rows if row["scale"] == scale]
        for representative in PAIR_REPS:
            group = [row for row in subset if row["pair_representative"] == representative]
            output.append({
                "scale": scale,
                "pair_representative": representative,
                "odds": str(Fraction(representative, 14 - representative)),
                "closeness": str(Fraction(representative, 7)),
                "n": len(group),
                "mean_handovers": statistics.fmean(row["handover_events"] for row in group),
                "median_handovers": statistics.median(row["handover_events"] for row in group),
                "base_prime_rate_Y0": statistics.fmean(row["Y0"] for row in group),
                "three_state_rate_Y3": statistics.fmean(row["Y3"] for row in group),
                "mean_delta_closeness": statistics.fmean(row["delta_closeness"] for row in group),
            })
    return output


def ordering_checks(group_rows: list[dict]) -> dict:
    checks = {}
    for scale in [name for name, *_ in TARGET_RANGES] + ["pooled"]:
        group = sorted(
            [row for row in group_rows if row["scale"] == scale],
            key=lambda row: row["pair_representative"],
        )
        handovers = [row["mean_handovers"] for row in group]
        y0 = [row["base_prime_rate_Y0"] for row in group]
        y3 = [row["three_state_rate_Y3"] for row in group]
        checks[scale] = {
            "mean_handovers": handovers,
            "Y0_rates": y0,
            "Y3_rates": y3,
            "P1_strict_decrease": handovers[0] > handovers[1] > handovers[2],
            "P2_strict_increase": y0[0] < y0[1] < y0[2],
            "P3_strict_increase": y3[0] < y3[1] < y3[2],
        }
    return checks


def stratified_permutation(rows: list[dict]) -> dict:
    xs = [row["closeness_float"] for row in rows]
    ys = [float(row["handover_events"]) for row in rows]
    observed = correlation(xs, ys)
    mean_x = statistics.fmean(xs)
    mean_y = statistics.fmean(ys)
    denominator = math.sqrt(
        sum((x - mean_x) ** 2 for x in xs) * sum((y - mean_y) ** 2 for y in ys)
    )
    scale_indices = {
        scale: [index for index, row in enumerate(rows) if row["scale"] == scale]
        for scale, *_ in TARGET_RANGES
    }
    rng = random.Random(PERMUTATION_SEED)
    null_at_or_below = 0
    permuted = xs.copy()
    for _ in range(PERMUTATIONS):
        for indices in scale_indices.values():
            values = [xs[index] for index in indices]
            rng.shuffle(values)
            for index, value in zip(indices, values):
                permuted[index] = value
        numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(permuted, ys))
        statistic = numerator / denominator if denominator else 0.0
        null_at_or_below += statistic <= observed
    return {
        "observed_pearson_c_vs_H": observed,
        "alternative": "negative",
        "permutations": PERMUTATIONS,
        "seed": PERMUTATION_SEED,
        "null_at_or_below_observed": null_at_or_below,
        "one_sided_p": (null_at_or_below + 1) / (PERMUTATIONS + 1),
    }


def model_scores(development: list[dict], targets: list[dict]) -> tuple[list[dict], dict]:
    score_rows = []
    rates_payload = {}
    for outcome in ("Y0", "Y3"):
        rates_payload[outcome] = {}
        for model in ("global", "orientation", "pair", "lane"):
            rates = fit_rates(development, outcome, model)
            rates_payload[outcome][model] = rates
            score_rows.append({
                "outcome": outcome,
                "model": model,
                "target_n": len(targets),
                "brier": brier(targets, outcome, model, rates),
                "development_rates": json.dumps(rates, sort_keys=True),
            })
    return score_rows, rates_payload


def main() -> None:
    for output in (RESULTS, TARGETS, GROUPS, SCORES):
        if output.exists():
            raise RuntimeError(f"refusing to overwrite {output.name}")

    exact_checks = exact_coordinate_checks()
    exact_pass = all(
        row.get("conversion_exact", False)
        and row.get("te_ara_sum_exact", False)
        and (row.get("excluded_by_gate_7", True))
        for row in exact_checks
    )

    max_target = max(high for _, _, high, _ in TARGET_RANGES)
    primes = sieve_primes(math.isqrt(max_target + 10_000) + 100)
    targets = build_targets(primes)
    development = development_rows()
    groups = group_summaries(targets)
    order = ordering_checks(groups)
    permutation = stratified_permutation(targets)
    scores, development_rates = model_scores(development, targets)

    def score(outcome: str, model: str) -> float:
        return next(row["brier"] for row in scores if row["outcome"] == outcome and row["model"] == model)

    compression = {}
    compression_pass = True
    for outcome in ("Y0", "Y3"):
        pair_brier = score(outcome, "pair")
        lane_brier = score(outcome, "lane")
        relative_loss = (pair_brier - lane_brier) / lane_brier
        passed = relative_loss <= 0.02
        compression[outcome] = {
            "global_brier": score(outcome, "global"),
            "orientation_brier": score(outcome, "orientation"),
            "pair_brier": pair_brier,
            "lane_brier": lane_brier,
            "pair_relative_loss_vs_lane": relative_loss,
            "pair_within_2_percent_of_lane": passed,
            "pair_beats_global": pair_brier < score(outcome, "global"),
            "lane_beats_global": lane_brier < score(outcome, "global"),
        }
        compression_pass &= passed

    scale_correlations = {
        scale: correlation(
            [row["closeness_float"] for row in targets if row["scale"] == scale],
            [row["handover_events"] for row in targets if row["scale"] == scale],
        )
        for scale, *_ in TARGET_RANGES
    }
    p1 = (
        all(order[scale]["P1_strict_decrease"] for scale, *_ in TARGET_RANGES)
        and all(value < 0 for value in scale_correlations.values())
        and permutation["observed_pearson_c_vs_H"] < 0
        and permutation["one_sided_p"] < 0.01
    )
    p2 = all(order[scale]["P2_strict_increase"] for scale, *_ in TARGET_RANGES)
    p3 = all(order[scale]["P3_strict_increase"] for scale, *_ in TARGET_RANGES)
    mean_delta = statistics.fmean(row["delta_closeness"] for row in targets)
    positive_delta = sum(row["delta_closeness"] > 0 for row in targets)
    negative_delta = sum(row["delta_closeness"] < 0 for row in targets)
    zero_delta = len(targets) - positive_delta - negative_delta
    p4 = mean_delta > 0 and positive_delta > negative_delta
    dynamic_passes = sum((p1, p2, p3, p4))

    if not exact_pass or not compression_pass:
        status = "FAILURE"
    elif all((p1, p2, p3, p4)):
        status = "STRONG DYNAMIC SUPPORT"
    elif dynamic_passes >= 2:
        status = "PARTIAL SUPPORT"
    else:
        status = "GEOMETRIC-ONLY SUPPORT / DYNAMIC NULL"

    write_csv(TARGETS, targets)
    write_csv(GROUPS, groups)
    write_csv(SCORES, scores)
    payload = {
        "test_id": "PN25/PAIR-RIDGE-COMPRESSION/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "protocol": PROTOCOL,
        "status": status,
        "data": {
            "development_source": DEVELOPMENT.name,
            "development_n": len(development),
            "target_ranges": [
                {"scale": scale, "low": low, "high_exclusive": high, "seed": seed, "n": N_PER_RANGE}
                for scale, low, high, seed in TARGET_RANGES
            ],
            "target_n": len(targets),
            "target_distinct_next_prime_labels": len(set(row["true_next_prime"] for row in targets)),
            "protected_87_bit_anchor_used": False,
        },
        "exact_coordinate_checks": exact_checks,
        "exact_coordinate_pass": exact_pass,
        "group_summaries": groups,
        "ordering_checks": order,
        "scale_correlations_c_vs_H": scale_correlations,
        "permutation_test": permutation,
        "path_progression": {
            "mean_delta_closeness": mean_delta,
            "positive_delta_count": positive_delta,
            "negative_delta_count": negative_delta,
            "zero_delta_count": zero_delta,
            "positive_rate": positive_delta / len(targets),
            "negative_rate": negative_delta / len(targets),
        },
        "development_frozen_rates": development_rates,
        "compression_scores": compression,
        "compression_fidelity_pass": compression_pass,
        "predictions": {
            "P1_ordered_handover": p1,
            "P2_immediate_ridge": p2,
            "P3_three_state_closure": p3,
            "P4_upward_path": p4,
            "dynamic_predictions_passed": dynamic_passes,
        },
        "decision": {
            "exact_coordinate_supported": exact_pass,
            "pair_compression_fidelity_supported": compression_pass,
            "dynamic_ridge_prediction_supported": all((p1, p2, p3, p4)),
            "interpretation": (
                "The pair odds and total-2 conversion are exact arithmetic. The prospective targets decide whether "
                "that coordinate orders future handover dynamics and whether discarding orientation preserves the "
                "limited outcome information present in the six raw mod-14 lanes."
            ),
            "new_prime_algorithm_supported": False,
        },
    }
    RESULTS.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "exact_coordinate_pass": exact_pass,
        "ordering_checks": order,
        "scale_correlations": scale_correlations,
        "permutation_test": permutation,
        "path_progression": payload["path_progression"],
        "compression_scores": compression,
        "predictions": payload["predictions"],
    }, indent=2))


if __name__ == "__main__":
    main()
