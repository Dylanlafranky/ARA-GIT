"""Independent validator for PN10.

This file does not import the PN10 primary implementation. It reconstructs prime
labels by a segmented Eratosthenes mask and reconstructs partial survival by
marking qualifying prime-divisor multiples directly at every registered cutoff.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT / "PN10_FACTOR_SPHERE_PRIME_RECOVERY_PROTOCOL.md"
FREEZE = ROOT / "PN10_FREEZE_MANIFEST.json"
RESULTS = ROOT / "PN10_FACTOR_SPHERE_RESULTS.json"
PATHS = ROOT / "PN10_FACTOR_SPHERE_PATHS.csv"
TRANSFERS = ROOT / "PN10_FACTOR_SPHERE_TRANSFER.csv"
FIGURE = ROOT / "PN10_FACTOR_SPHERE_FIGURE.png"
OUTPUT = ROOT / "PN10_FACTOR_SPHERE_VALIDATION.json"

GRID = [round(i * 0.05, 2) for i in range(21)]
PRIMARY = [0.25, 0.50, 0.75, 0.90]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def ordinary_primes(limit: int) -> list[int]:
    marked = bytearray(limit + 1)
    out: list[int] = []
    for value in range(2, limit + 1):
        if not marked[value]:
            out.append(value)
            if value <= math.isqrt(limit):
                marked[value * value : limit + 1 : value] = b"\x01" * (((limit - value * value) // value) + 1)
    return out


def segment(low: int, high: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[int]]:
    numbers = np.arange(low, high, dtype=np.int64)
    prime_mask = np.ones(high - low, dtype=bool)
    first_divisor = np.zeros(high - low, dtype=np.int64)
    primes = ordinary_primes(math.isqrt(high - 1))
    for p in primes:
        start = max(p * p, ((low + p - 1) // p) * p)
        if start >= high:
            continue
        indexes = np.arange(start - low, high - low, p, dtype=np.int64)
        prime_mask[indexes] = False
        empty = first_divisor[indexes] == 0
        first_divisor[indexes[empty]] = p
    return numbers, prime_mask, first_divisor, primes


def direct_scaled_survival(numbers: np.ndarray, primes: list[int], cutoff: float) -> np.ndarray:
    survive = np.ones(len(numbers), dtype=bool)
    low, high = int(numbers[0]), int(numbers[-1]) + 1
    for p in primes:
        start = max(p * p, ((low + p - 1) // p) * p)
        if start >= high:
            continue
        indexes = np.arange(start - low, high - low, p, dtype=np.int64)
        if cutoff >= 1.0:
            survive[indexes] = False
        else:
            values = numbers[indexes]
            qualifies = (2.0 * math.log(p) / np.log(values)) <= cutoff + 1e-14
            survive[indexes[qualifies]] = False
    return survive


def direct_fixed_survival(numbers: np.ndarray, primes: list[int], q: int) -> np.ndarray:
    survive = np.ones(len(numbers), dtype=bool)
    low, high = int(numbers[0]), int(numbers[-1]) + 1
    for p in primes:
        if p > q:
            break
        start = max(p * p, ((low + p - 1) // p) * p)
        if start < high:
            survive[start - low :: p] = False
    return survive


def scores(labels: np.ndarray, survive: np.ndarray, p: float) -> tuple[float, float]:
    pred = np.where(survive, p, 0.0)
    brier = float(np.mean((pred - labels) ** 2))
    pred = np.clip(pred, 1e-15, 1.0 - 1e-15)
    loss = float(-np.mean(labels * np.log2(pred) + (1.0 - labels) * np.log2(1.0 - pred)))
    return brier, loss


def close(a: float, b: float, tolerance: float = 5e-13) -> bool:
    return abs(a - b) <= tolerance


def main() -> None:
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    stored = json.loads(RESULTS.read_text(encoding="utf-8"))
    path_rows = list(csv.DictReader(PATHS.open(encoding="utf-8")))
    transfer_rows = list(csv.DictReader(TRANSFERS.open(encoding="utf-8")))
    checks: list[dict] = []

    def check(name: str, passed: bool, detail: object = None) -> None:
        checks.append({"name": name, "pass": bool(passed), "detail": detail})

    check("protocol hash matches freeze", digest(PROTOCOL) == freeze["protocol_sha256"], digest(PROTOCOL))

    d_low, d_high = freeze["development_interval"]
    e_low, e_high = freeze["evaluation_interval"]
    d_n, d_prime, d_lpf, d_base = segment(d_low, d_high)
    e_n, e_prime, e_lpf, e_base = segment(e_low, e_high)

    check("development prime count", int(d_prime.sum()) == stored["intervals"]["development"]["primes"], int(d_prime.sum()))
    check("evaluation prime count", int(e_prime.sum()) == stored["intervals"]["evaluation"]["primes"], int(e_prime.sum()))
    first_25 = e_n[e_prime][:25].astype(int).tolist()
    check("first 25 fresh primes", first_25 == stored["exact_recovery"]["first_25_evaluation_primes"], first_25)
    check("all composite labels have a first divisor", bool(np.all(d_lpf[~d_prime] > 0) and np.all(e_lpf[~e_prime] > 0)))

    max_pair_error = 0.0
    for numbers, prime_mask, lpf in [(d_n, d_prime, d_lpf), (e_n, e_prime, e_lpf)]:
        comp = ~prime_mask
        partner = numbers[comp] // lpf[comp]
        pair_sum = 2.0 * np.log(lpf[comp]) / np.log(numbers[comp]) + 2.0 * np.log(partner) / np.log(numbers[comp])
        max_pair_error = max(max_pair_error, float(np.max(np.abs(pair_sum - 2.0))))
    check("factor-pair closure", max_pair_error <= 1e-12 and close(max_pair_error, stored["criteria"]["P2_reversible_factor_pair_closure"]["max_abs_error"]), max_pair_error)

    roots = np.array(ordinary_primes(10_000), dtype=float)
    square_error = float(np.max(np.abs(2.0 * np.log(roots) / np.log(roots * roots) - 1.0)))
    check("prime-square ridge", square_error <= 1e-12, square_error)

    path_lookup = {(r["interval"], float(r["cutoff"])): r for r in path_rows}
    computed_survival: dict[tuple[str, float], np.ndarray] = {}
    purity_paths: dict[str, list[float]] = {"development": [], "evaluation": []}
    for name, numbers, labels, primes in [
        ("development", d_n, d_prime, d_base),
        ("evaluation", e_n, e_prime, e_base),
    ]:
        for cutoff in GRID:
            survive = direct_scaled_survival(numbers, primes, cutoff)
            computed_survival[(name, cutoff)] = survive
            row = path_lookup[(name, cutoff)]
            survivors = int(survive.sum())
            purity = float(labels.sum() / survivors)
            purity_paths[name].append(purity)
            check(f"{name} path c={cutoff:.2f}", survivors == int(row["survivors"]) and close(purity, float(row["prime_purity"])), {"survivors": survivors, "purity": purity})

    monotone = all(all(b >= a - 1e-15 for a, b in zip(values, values[1:])) and close(values[-1], 1.0) for values in purity_paths.values())
    check("monotone purity and exact ridge", monotone)

    transfer_lookup = {(r["method"], float(r["cutoff"])): r for r in transfer_rows}
    d_centre = math.sqrt(d_low * (d_high - 1))
    ara_briers, fixed_briers, ara_errors, fixed_errors = [], [], [], []
    for cutoff in PRIMARY:
        d_survive = computed_survival[("development", cutoff)]
        e_survive = computed_survival[("evaluation", cutoff)]
        dp = float(d_prime.sum() / d_survive.sum())
        ep = float(e_prime.sum() / e_survive.sum())
        brier, loss = scores(e_prime.astype(float), e_survive, dp)
        row = transfer_lookup[("ARA scaled", cutoff)]
        ok = (
            int(row["development_survivors"]) == int(d_survive.sum())
            and int(row["evaluation_survivors"]) == int(e_survive.sum())
            and close(float(row["development_purity"]), dp)
            and close(float(row["evaluation_purity"]), ep)
            and close(float(row["evaluation_brier"]), brier)
            and close(float(row["evaluation_log_loss_bits"]), loss)
        )
        check(f"ARA transfer c={cutoff}", ok, {"development_purity": dp, "evaluation_purity": ep, "brier": brier})
        ara_briers.append(brier)
        ara_errors.append(abs(dp - ep))

        q = int(math.floor(d_centre ** (cutoff / 2.0)))
        d_fixed = direct_fixed_survival(d_n, d_base, q)
        e_fixed = direct_fixed_survival(e_n, e_base, q)
        dp_fixed = float(d_prime.sum() / d_fixed.sum())
        ep_fixed = float(e_prime.sum() / e_fixed.sum())
        brier_fixed, loss_fixed = scores(e_prime.astype(float), e_fixed, dp_fixed)
        row_fixed = transfer_lookup[("fixed Q", cutoff)]
        ok_fixed = (
            int(row_fixed["absolute_q"]) == q
            and int(row_fixed["development_survivors"]) == int(d_fixed.sum())
            and int(row_fixed["evaluation_survivors"]) == int(e_fixed.sum())
            and close(float(row_fixed["development_purity"]), dp_fixed)
            and close(float(row_fixed["evaluation_purity"]), ep_fixed)
            and close(float(row_fixed["evaluation_brier"]), brier_fixed)
            and close(float(row_fixed["evaluation_log_loss_bits"]), loss_fixed)
        )
        check(f"fixed-Q transfer c={cutoff}", ok_fixed, {"q": q, "development_purity": dp_fixed, "evaluation_purity": ep_fixed, "brier": brier_fixed})
        fixed_briers.append(brier_fixed)
        fixed_errors.append(abs(dp_fixed - ep_fixed))

    check("P5 mean Brier ordering", float(np.mean(ara_briers)) < float(np.mean(fixed_briers)), {"ARA": float(np.mean(ara_briers)), "fixed_Q": float(np.mean(fixed_briers))})
    check("P6 mean calibration ordering", float(np.mean(ara_errors)) < float(np.mean(fixed_errors)), {"ARA": float(np.mean(ara_errors)), "fixed_Q": float(np.mean(fixed_errors))})
    check("all six stored support criteria pass", stored["passed_support_criteria"] == 6 and all(v["pass"] for k, v in stored["criteria"].items() if k.startswith("P")))
    check("early cutoffs retain composites", all(int(transfer_lookup[("ARA scaled", c)]["evaluation_remaining_composites"]) > 0 for c in PRIMARY))

    with Image.open(FIGURE) as image:
        check("figure dimensions", image.size == (1600, 1100), image.size)
    check("protected material unchanged", stored["protected_material"] == {"p31_primorial_wheel_constructed": False, "r12_opened": False})

    validation = {
        "test_id": stored["test_id"],
        "validator": "independent segmented prime mask plus direct per-cutoff multiple marking",
        "status": "PASS" if all(c["pass"] for c in checks) else "FAIL",
        "passed_checks": sum(c["pass"] for c in checks),
        "total_checks": len(checks),
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps({k: validation[k] for k in ["status", "passed_checks", "total_checks"]}, indent=2))


if __name__ == "__main__":
    main()
