"""Independent validation of PN1I opened-rung development outputs.

The validator does not import the PN1I implementation or its wheel generator.
It reconstructs parent reduced residues by repeated filtering and finds excluded
lifts by explicit enumeration rather than modular inversion.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN1I_PRIME_PYRAMID_ARA_DEVELOPMENT_PROTOCOL.md"
PRIMARY = HERE / "PN1I_RESULTS.json"
GATE_CSV = HERE / "PN1I_GATE_METRICS.csv"
LOCK_CSV = HERE / "PN1I_LOCK_MODEL_SCORES.csv"
BASE_CSV = HERE / "PN1I_BASE_ARA_CROSSWALK.csv"
OUTPUT = HERE / "PN1I_INDEPENDENT_VALIDATION.json"
PROTOCOL_SHA256 = "B713DAB0803545F201F2C712303E1C5E11BABC4538740381421AFF1BCBBE9F5C"
PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23)
TRANSITIONS = (7, 11, 13, 17, 19, 23)
BINS = 12
FOLDS = 8
ALPHA = 0.5


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def array_hash(*arrays: np.ndarray) -> str:
    digest = hashlib.sha256()
    for values in arrays:
        data = np.ascontiguousarray(values)
        digest.update(str(data.dtype).encode("ascii"))
        digest.update(np.asarray(data.shape, dtype=np.int64).tobytes())
        for start in range(0, len(data), 1_000_000):
            digest.update(data[start : start + 1_000_000].tobytes(order="C"))
    return digest.hexdigest().upper()


def reduced_residues(primes: tuple[int, ...]) -> tuple[int, np.ndarray, np.ndarray]:
    period = math.prod(primes)
    residues = np.arange(1, period, dtype=np.int64)
    for prime in primes:
        residues = residues[residues % prime != 0]
    gaps = np.empty(len(residues), dtype=np.int32)
    gaps[:-1] = np.diff(residues).astype(np.int32)
    gaps[-1] = period + int(residues[0]) - int(residues[-1])
    return period, residues, gaps


def explicit_gate(next_prime: int) -> dict[str, np.ndarray | int | str | bool]:
    parent_primes = tuple(prime for prime in PRIMES if prime < next_prime)
    period, residues, gaps = reduced_residues(parent_primes)
    excluded = np.full(len(residues), -1, dtype=np.int16)
    hit_count = np.zeros(len(residues), dtype=np.uint8)
    for lift in range(next_prime):
        hits = (residues + lift * period) % next_prime == 0
        excluded[hits] = lift
        hit_count[hits] += 1
    left = np.roll(gaps, 1).astype(np.int32, copy=False)
    right = gaps.astype(np.int32, copy=False)
    ranks = np.sort(excluded.astype(np.int64) * len(residues) + np.arange(len(residues), dtype=np.int64))
    steps = np.diff(np.concatenate((ranks, ranks[:1] + next_prime * len(residues))))
    return {
        "period": period,
        "residues": residues,
        "gaps": gaps,
        "excluded": excluded,
        "left": left,
        "right": right,
        "one_hit_each": bool(np.all(hit_count == 1)),
        "no_adjacent": bool(np.all(steps > 1)),
        "event_sha256": array_hash(residues, excluded, left, right),
    }


def probability(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    return values / values.sum()


def transition_counts(values: np.ndarray, state_count: int) -> np.ndarray:
    following = np.roll(values.astype(np.int64), -1)
    keys = values.astype(np.int64) * state_count + following
    return np.bincount(keys, minlength=state_count**2).reshape(state_count, state_count)


def mutual_information(counts: np.ndarray) -> float:
    joint = probability(counts)
    expected = joint.sum(axis=1, keepdims=True) @ joint.sum(axis=0, keepdims=True)
    active = joint > 0
    return float(np.sum(joint[active] * np.log2(joint[active] / expected[active])))


def coordinate_and_bin(left: np.ndarray, right: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    coordinate = 2.0 * right.astype(np.float64) / (left.astype(np.float64) + right.astype(np.float64))
    bins = np.minimum((coordinate * BINS / 2.0).astype(np.int64), BINS - 1)
    return coordinate, bins


def encode(values: np.ndarray) -> tuple[np.ndarray, int]:
    _, inverse = np.unique(values, return_inverse=True)
    return inverse.astype(np.int64), int(inverse.max()) + 1


def independent_cv_loss(states: np.ndarray, state_count: int, target: np.ndarray) -> float:
    total_key = states * BINS + target
    total = np.bincount(total_key, minlength=state_count * BINS).reshape(state_count, BINS)
    weighted_loss = 0.0
    total_events = 0
    size = len(target)
    for fold in range(FOLDS):
        start = (fold * size + FOLDS - 1) // FOLDS
        stop = ((fold + 1) * size + FOLDS - 1) // FOLDS
        test_key = states[start:stop] * BINS + target[start:stop]
        test = np.bincount(test_key, minlength=state_count * BINS).reshape(state_count, BINS)
        train = total - test
        conditional = (train + ALPHA) / (train.sum(axis=1, keepdims=True) + ALPHA * BINS)
        fold_size = stop - start
        weighted_loss += -float(np.sum(test * np.log2(conditional)))
        total_events += fold_size
    return weighted_loss / total_events


def lock_losses(gate: dict[str, np.ndarray | int | str | bool], lag: int) -> dict[str, float]:
    left = np.asarray(gate["left"], dtype=np.int64)
    right = np.asarray(gate["right"], dtype=np.int64)
    excluded = np.asarray(gate["excluded"], dtype=np.int64)
    merged = left + right
    _, coordinate_bin = coordinate_and_bin(left, right)
    target = np.roll(coordinate_bin, -lag)
    left_code, left_states = encode(left)
    right_code, right_states = encode(right)
    merged_code, merged_states = encode(merged)
    pair = left_code * right_states + right_code
    pair_states = left_states * right_states
    pair_gate = pair * (int(excluded.max()) + 1) + excluded
    pair_gate_states = pair_states * (int(excluded.max()) + 1)
    states = {
        "marginal": (np.zeros(len(left), dtype=np.int64), 1),
        "left_gap": (left_code, left_states),
        "right_gap": (right_code, right_states),
        "merged_sum": (merged_code, merged_states),
        "ordered_pair": (pair, pair_states),
        "gate_branch": (excluded, int(excluded.max()) + 1),
        "pair_plus_gate": (pair_gate, pair_gate_states),
    }
    return {
        name: independent_cv_loss(model_state, state_count, target)
        for name, (model_state, state_count) in states.items()
    }


def main() -> dict[str, object]:
    primary = json.loads(PRIMARY.read_text(encoding="utf-8"))
    gate_csv = pd.read_csv(GATE_CSV).set_index("child_prime")
    lock_csv = pd.read_csv(LOCK_CSV).set_index(["child_prime", "lag", "model"])
    base_csv = pd.read_csv(BASE_CSV)
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, observed: object = None, expected: object = None) -> None:
        checks.append({"name": name, "pass": bool(passed), "observed": observed, "expected": expected})

    check("protocol hash", file_hash(PROTOCOL) == PROTOCOL_SHA256, file_hash(PROTOCOL), PROTOCOL_SHA256)
    check("primary records no prime31 access", primary["prime31_accessed"] is False, primary["prime31_accessed"], False)

    recomputed_pair_positive = 0
    recomputed_gate_positive = 0
    for next_prime in TRANSITIONS:
        print(f"Independent PN1I validation p{next_prime}")
        gate = explicit_gate(next_prime)
        row = gate_csv.loc[next_prime]
        excluded = np.asarray(gate["excluded"], dtype=np.int64)
        left = np.asarray(gate["left"], dtype=np.int64)
        right = np.asarray(gate["right"], dtype=np.int64)
        coordinate, coordinate_bin = coordinate_and_bin(left, right)
        branch_counts = np.bincount(excluded, minlength=next_prime)
        branch_tv = 0.5 * float(np.abs(probability(branch_counts) - 1.0 / next_prime).sum())
        branch_mi = mutual_information(transition_counts(excluded, next_prime))
        ara_mi = mutual_information(transition_counts(coordinate_bin, BINS))
        gap_labels = np.unique(np.concatenate((left, right)))
        left_code = np.searchsorted(gap_labels, left)
        right_code = np.searchsorted(gap_labels, right)
        pair_counts = np.bincount(
            left_code * len(gap_labels) + right_code,
            minlength=len(gap_labels) ** 2,
        ).reshape(len(gap_labels), len(gap_labels))
        reflection_tv = 0.5 * float(np.abs(pair_counts - pair_counts.T).sum()) / float(pair_counts.sum())
        inverse = pow(int(gate["period"]) % next_prime, -1, next_prime)
        internal_step = np.mod(np.diff(excluded), next_prime)
        internal_expected = np.mod(-right[:-1] * inverse, next_prime)
        seam_raw = int((excluded[0] - excluded[-1]) % next_prime)
        seam_expected = int((-right[-1] * inverse) % next_prime)
        seam_holonomy = int((seam_raw - seam_expected) % next_prime)
        check(f"p{next_prime} one excluded lift per parent", bool(gate["one_hit_each"]))
        check(f"p{next_prime} no adjacent exclusions", bool(gate["no_adjacent"]))
        check(f"p{next_prime} event hash", str(gate["event_sha256"]) == row.event_sha256, gate["event_sha256"], row.event_sha256)
        check(f"p{next_prime} parent slots", len(excluded) == int(row.parent_slots), len(excluded), int(row.parent_slots))
        check(f"p{next_prime} child slots", (next_prime - 1) * len(excluded) == int(row.child_slots), (next_prime - 1) * len(excluded), int(row.child_slots))
        check(f"p{next_prime} branch TV", abs(branch_tv - row.gate_branch_tv_from_uniform) < 1e-14, branch_tv, row.gate_branch_tv_from_uniform)
        check(f"p{next_prime} branch MI", abs(branch_mi - row.gate_phase_transition_mi_bits) < 1e-12, branch_mi, row.gate_phase_transition_mi_bits)
        check(f"p{next_prime} plain ARA mean", abs(float(coordinate.mean()) - row.plain_ara_mean) < 1e-14, float(coordinate.mean()), row.plain_ara_mean)
        check(f"p{next_prime} plain ARA MI", abs(ara_mi - row.plain_ara_transition_mi_bits) < 1e-12, ara_mi, row.plain_ara_transition_mi_bits)
        check(f"p{next_prime} exact pair reflection", abs(reflection_tv - row.plain_ara_reflection_tv) < 1e-14, reflection_tv, row.plain_ara_reflection_tv)
        check(f"p{next_prime} internal gate-step identity", bool(np.array_equal(internal_step, internal_expected)))
        check(f"p{next_prime} seam holonomy", seam_holonomy == int(row.seam_holonomy_lift_shift) == 1, seam_holonomy, 1)

        losses = lock_losses(gate, lag=2)
        singles = min(losses[name] for name in ("left_gap", "right_gap", "merged_sum"))
        pair_delta = singles - losses["ordered_pair"]
        gate_delta = min(losses["ordered_pair"], losses["gate_branch"]) - losses["pair_plus_gate"]
        recomputed_pair_positive += int(pair_delta > 0)
        recomputed_gate_positive += int(gate_delta > 0)
        for model, loss in losses.items():
            expected = float(lock_csv.loc[(next_prime, 2, model), "mean_cross_entropy_bits"])
            check(f"p{next_prime} lag2 {model} loss", abs(loss - expected) < 1e-12, loss, expected)

    check(
        "lag2 pair-positive rung count",
        recomputed_pair_positive == primary["test_C_double_pyramid_lock"]["lag2_pair_positive_count"],
        recomputed_pair_positive,
        primary["test_C_double_pyramid_lock"]["lag2_pair_positive_count"],
    )
    check(
        "lag2 gate-positive rung count",
        recomputed_gate_positive == primary["test_C_double_pyramid_lock"]["lag2_gate_positive_count"],
        recomputed_gate_positive,
        primary["test_C_double_pyramid_lock"]["lag2_gate_positive_count"],
    )
    check("base crosswalk has seven opened child rungs", len(base_csv) == 7, len(base_csv), 7)
    check("base crosswalk includes p23", 23 in set(base_csv.rung_prime), sorted(base_csv.rung_prime.tolist()), "contains 23")
    check(
        "child ARA MI strictly decreases",
        bool(np.all(np.diff(base_csv.ordered_adjacent_mi_bits.to_numpy()) < 0)),
    )
    residual = base_csv.dropna(subset=["markov_residual_l2"])
    check(
        "Markov residual L2 strictly decreases",
        bool(np.all(np.diff(residual.markov_residual_l2.to_numpy()) < 0)),
    )
    for filename in ("PN1I_PRIME_GATE_ARA_FIGURE.png", "PN1I_PYRAMID_LOCK_FIGURE.png"):
        path = HERE / filename
        with Image.open(path) as image:
            check(f"{filename} readable", image.width >= 2000 and image.height >= 1200, [image.width, image.height], ">=2000x1200")

    passed = sum(item["pass"] for item in checks)
    result = {
        "validation_id": "PN1I/INDEPENDENT/v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if passed == len(checks) else "FAIL",
        "maximum_reconstructed_prime": 23,
        "prime29_generated": False,
        "prime31_accessed": False,
        "passed_check_count": passed,
        "check_count": len(checks),
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("status", "passed_check_count", "check_count")}, indent=2))
    return result


if __name__ == "__main__":
    main()
