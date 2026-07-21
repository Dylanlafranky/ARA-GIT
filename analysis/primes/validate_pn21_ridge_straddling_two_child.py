"""Independent numerical validation of PN21."""

from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULT_PATH = HERE / "PN21_RIDGE_STRADDLING_TWO_CHILD_RESULTS.json"
OUTPUT = HERE / "PN21_RIDGE_STRADDLING_TWO_CHILD_VALIDATION.json"
LOW, HIGH, MID = 4_000_000_000, 4_001_000_000, 4_000_500_000


def independent_primes(limit: int) -> np.ndarray:
    flags = bytearray(b"\x01") * (limit + 1)
    flags[0:2] = b"\x00\x00"
    for value in range(2, math.isqrt(limit) + 1):
        if flags[value]:
            start = value * value
            flags[start : limit + 1 : value] = b"\x00" * (((limit - start) // value) + 1)
    return np.fromiter((i for i, flag in enumerate(flags) if flag), dtype=np.int64)


def independent_parent(primes: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    numbers = np.arange(LOW + 1, HIGH, 2, dtype=np.int64)
    least = np.zeros(numbers.size, dtype=np.int32)
    for prime_value in primes:
        prime = int(prime_value)
        if prime == 2:
            continue
        if prime * prime >= HIGH:
            break
        first = ((LOW + 1 + prime - 1) // prime) * prime
        if first % 2 == 0:
            first += prime
        start_index = (first - (LOW + 1)) // 2
        if start_index < 0:
            start_index += ((-start_index + prime - 1) // prime) * prime
        indices = np.arange(start_index, numbers.size, prime, dtype=np.int64)
        unassigned = least[indices] == 0
        least[indices[unassigned]] = prime
    labels = least == 0
    parent = np.ones(numbers.size, dtype=np.float64)
    mask = ~labels
    parent[mask] = 2.0 * np.log(least[mask]) / np.log(numbers[mask])
    return numbers, labels, parent


def independent_pair(numbers: np.ndarray, primes: np.ndarray, straddling: bool) -> tuple[np.ndarray, np.ndarray]:
    root = np.array([math.isqrt(int(number)) for number in numbers], dtype=np.int64)
    insertion = np.searchsorted(primes, root, side="right")
    below = primes[insertion - 1]
    other = primes[insertion] if straddling else primes[insertion - 2]
    phase_a = 2.0 * (numbers % below) / below
    phase_b = 2.0 - 2.0 * (numbers % other) / other
    return phase_a, phase_b


def independent_retention(parent: np.ndarray, a: np.ndarray, b: np.ndarray) -> float:
    bins_a = np.clip(np.floor(a * 16).astype(np.int64), 0, 31)
    bins_b = np.clip(np.floor(b * 16).astype(np.int64), 0, 31)
    cells = bins_a * 32 + bins_b
    train = np.arange(parent.size) < parent.size // 2
    test = ~train
    global_mean = float(parent[train].mean())
    means = {}
    for cell in np.unique(cells[train]):
        means[int(cell)] = float(parent[train & (cells == cell)].mean())
    prediction = np.fromiter((means.get(int(cell), global_mean) for cell in cells[test]), dtype=np.float64)
    mse = float(np.mean((parent[test] - prediction) ** 2))
    baseline = float(np.mean((parent[test] - global_mean) ** 2))
    return 1.0 - mse / baseline


def independent_auc(labels: np.ndarray, score: np.ndarray) -> float:
    order = np.argsort(score, kind="mergesort")
    sorted_score = score[order]
    ranks = np.empty(score.size, dtype=np.float64)
    left = 0
    while left < score.size:
        right = left + 1
        while right < score.size and sorted_score[right] == sorted_score[left]:
            right += 1
        ranks[order[left:right]] = (left + 1 + right) / 2.0
        left = right
    positive = labels.astype(bool)
    count_positive = int(positive.sum())
    count_negative = int(labels.size - count_positive)
    return (
        float(ranks[positive].sum()) - count_positive * (count_positive + 1) / 2.0
    ) / (count_positive * count_negative)


def add(checks: list[dict], label: str, passed: bool, observed: object) -> None:
    checks.append({"label": label, "passed": bool(passed), "observed": observed})


def close(left: float, right: float, tolerance: float = 1e-12) -> bool:
    return abs(left - right) <= tolerance


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError("validation output exists; refusing overwrite")
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    primes = independent_primes(math.isqrt(HIGH - 1) + 200)
    numbers, labels, parent = independent_parent(primes)
    straddle_a, straddle_b = independent_pair(numbers, primes, True)
    same_a, same_b = independent_pair(numbers, primes, False)
    straddle_r2 = independent_retention(parent, straddle_a, straddle_b)
    same_r2 = independent_retention(parent, same_a, same_b)
    closure = (straddle_a + straddle_b) / 2.0
    joint_score = -(np.abs(straddle_a - 1.0) + np.abs(straddle_b - 1.0))
    closure_score = -np.abs(closure - 1.0)
    joint_auc = independent_auc(labels, joint_score)
    closure_auc = independent_auc(labels, closure_score)
    checks: list[dict] = []

    add(checks, "odd population count", numbers.size == 500_000, int(numbers.size))
    add(checks, "independent prime count", int(labels.sum()) == 45_166, int(labels.sum()))
    add(
        checks,
        "straddling heldout R2",
        close(straddle_r2, result["straddling_pair"]["retention"]["heldout_retained_r2"]),
        straddle_r2,
    )
    add(
        checks,
        "same-side heldout R2",
        close(same_r2, result["same_side_control"]["retention"]["heldout_retained_r2"]),
        same_r2,
    )
    add(
        checks,
        "joint ridge AUC",
        close(joint_auc, result["straddling_pair"]["prime_diagnostics"]["joint_ridge_auc"]),
        joint_auc,
    )
    add(
        checks,
        "closure ridge AUC",
        close(closure_auc, result["straddling_pair"]["prime_diagnostics"]["closure_ridge_auc"]),
        closure_auc,
    )
    add(checks, "retention below frozen 90%", straddle_r2 < 0.90, straddle_r2)
    add(checks, "straddling does not beat control", straddle_r2 <= same_r2, [straddle_r2, same_r2])
    add(checks, "joint AUC is chance-like", abs(joint_auc - 0.5) < 0.01, joint_auc)
    add(checks, "closure AUC is chance-like", abs(closure_auc - 0.5) < 0.01, closure_auc)
    add(checks, "result keeps target sealed", result["decision"]["blind_target_authorized"] is False, False)

    inspected = [
        HERE / "PN21_RIDGE_STRADDLING_TWO_CHILD_PROTOCOL_v1_FROZEN.md",
        HERE / "pn21_ridge_straddling_two_child.py",
        RESULT_PATH,
    ]
    long_decimal = re.compile(r"(?<![0-9a-f])\d{25,}(?![0-9a-f])", re.IGNORECASE)
    exposed = {
        path.name: long_decimal.findall(path.read_text(encoding="utf-8"))
        for path in inspected
        if long_decimal.findall(path.read_text(encoding="utf-8"))
    }
    add(checks, "no raw sealed anchor in PN21 artifacts", not exposed, exposed)

    passed = sum(item["passed"] for item in checks)
    payload = {
        "validation_id": "PN21/RIDGE-STRADDLING-TWO-CHILD/INDEPENDENT/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("status", "checks_passed", "checks_total")}, indent=2))
    if payload["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
