"""Independent full-window validator for PN7B.

Uses different chunk boundaries, constructs 24-bin objects directly, and does
not import either the PN7B builder or scorer.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN7B_ACTUAL_PRIME_NODE_GAP_PROTOCOL.md"
AGG = HERE / "PN7B_ACTUAL_PRIME_NODE_GAP_AGGREGATES.npz"
META = HERE / "PN7B_ACTUAL_PRIME_NODE_GAP_AGGREGATES.json"
RESULT = HERE / "PN7B_ACTUAL_PRIME_NODE_GAP_RESULTS.json"
OUT = HERE / "PN7B_ACTUAL_PRIME_NODE_GAP_VALIDATION.json"
EXPECTED_PROTOCOL = "9B42C13E4042B7698FC95A3A32B203CFAE5BE2873F28C0BD3ACC4653BC866F26"
INTERVALS = {
    7: (10_000_000, 10_100_000),
    8: (100_000_000, 101_000_000),
    9: (1_000_000_000, 1_010_000_000),
    10: (10_000_000_000, 10_100_000_000),
    11: (100_000_000_000, 101_000_000_000),
}
BINS = 24
OFFSET = 257
CHUNK = 8_000_003


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            block = f.read(1 << 20)
            if not block:
                break
            h.update(block)
    return h.hexdigest().upper()


def small_primes(limit: int) -> np.ndarray:
    flags = np.ones(limit + 1, dtype=bool)
    flags[:2] = False
    for p in range(2, math.isqrt(limit) + 1):
        if flags[p]:
            flags[p * p :: p] = False
    return np.flatnonzero(flags).astype(np.int64)


def bins24(left, right):
    return np.minimum((BINS * right) // (left + right), BINS - 1).astype(np.int16)


def aggregate_hist48(a):
    return a.reshape(24, 2).sum(axis=1)


def aggregate_plane48(a):
    return a.reshape(24, 2, 24, 2).sum(axis=(1, 3))


def rebuild(low, high):
    divisors = small_primes(math.isqrt(high - 1))
    midpoint = low + (high - low) // 2
    f = np.zeros(24, dtype=np.int64)
    fh = np.zeros((2, 24), dtype=np.int64)
    t = np.zeros((24, 24), dtype=np.int64)
    th = np.zeros((2, 24, 24), dtype=np.int64)
    fc = np.zeros(24, dtype=np.int64)
    tc = np.zeros((24, 24), dtype=np.int64)
    carry_primes = np.empty(0, dtype=np.int64)
    previous_prime = None
    previous_state = None
    previous_center = None
    gap_tail = np.empty(0, dtype=np.int64)
    state_tail = np.empty(0, dtype=np.int16)
    prime_count = 0
    equal_count = 0
    incoming_larger = 0
    outgoing_larger = 0

    for start in range(low, high, CHUNK):
        stop = min(high, start + CHUNK)
        flags = np.ones(stop - start, dtype=bool)
        for qv in divisors:
            q = int(qv)
            first = ((start + q - 1) // q) * q
            if first < stop:
                flags[first - start :: q] = False
        current = np.flatnonzero(flags).astype(np.int64) + start
        prime_count += len(current)

        fresh_gaps = np.diff(current) if previous_prime is None else np.diff(np.r_[previous_prime, current])
        gap_stream = np.r_[gap_tail, fresh_gaps] if gap_tail.size else fresh_gaps
        if len(gap_stream) > OFFSET:
            cb = bins24(gap_stream[:-OFFSET], gap_stream[OFFSET:])
            fc += np.bincount(cb, minlength=24)[:24]
        gap_tail = gap_stream[-OFFSET:].copy()

        joined = np.r_[carry_primes, current] if carry_primes.size else current
        if len(joined) >= 3:
            dg = np.diff(joined)
            left, right = dg[:-1], dg[1:]
            centers = joined[1:-1]
            xb = bins24(left, right)
            f += np.bincount(xb, minlength=24)[:24]
            side = (centers >= midpoint).astype(np.int8)
            fh[0] += np.bincount(xb[side == 0], minlength=24)[:24]
            fh[1] += np.bincount(xb[side == 1], minlength=24)[:24]
            equal_count += int(np.count_nonzero(left == right))
            incoming_larger += int(np.count_nonzero(left > right))
            outgoing_larger += int(np.count_nonzero(right > left))

            if previous_state is None:
                state_join, center_join = xb, centers
            else:
                state_join = np.r_[np.int16(previous_state), xb]
                center_join = np.r_[np.int64(previous_center), centers]
            if len(state_join) > 1:
                index = state_join[:-1].astype(np.int64) * 24 + state_join[1:].astype(np.int64)
                t += np.bincount(index, minlength=576).reshape(24, 24)
                source_side = (center_join[:-1] >= midpoint).astype(np.int8)
                th[0] += np.bincount(index[source_side == 0], minlength=576).reshape(24, 24)
                th[1] += np.bincount(index[source_side == 1], minlength=576).reshape(24, 24)
            previous_state, previous_center = int(xb[-1]), int(centers[-1])

            full_states = np.r_[state_tail, xb] if state_tail.size else xb
            if len(full_states) > OFFSET:
                index = full_states[:-OFFSET].astype(np.int64) * 24 + full_states[OFFSET:].astype(np.int64)
                tc += np.bincount(index, minlength=576).reshape(24, 24)
            state_tail = full_states[-OFFSET:].copy()

        if len(current):
            previous_prime = int(current[-1])
            carry_primes = joined[-2:].copy()

    return {
        "f": f, "fh": fh, "t": t, "th": th, "fc": fc, "tc": tc,
        "prime_count": prime_count, "equal": equal_count,
        "incoming_larger": incoming_larger, "outgoing_larger": outgoing_larger,
    }


def prob(a):
    a = np.asarray(a, dtype=float)
    return a / a.sum()


def corr(a, b):
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    a, b = a - a.mean(), b - b.mean()
    return float(np.dot(a, b) / math.sqrt(float(np.dot(a, a) * np.dot(b, b))))


def cosine(a, b):
    a, b = np.asarray(a, dtype=float).ravel(), np.asarray(b, dtype=float).ravel()
    return float(np.dot(a, b) / math.sqrt(float(np.dot(a, a) * np.dot(b, b))))


def jsd(a, b):
    p, q = prob(a), prob(b)
    m = (p + q) / 2
    ip, iq = p > 0, q > 0
    return float((np.sum(p[ip] * np.log2(p[ip] / m[ip])) + np.sum(q[iq] * np.log2(q[iq] / m[iq]))) / 2)


def tv(a, b):
    return float(np.abs(prob(a).ravel() - prob(b).ravel()).sum() / 2)


def ce(model, target):
    model = np.asarray(model, dtype=float)
    p = (model + 0.5) / (model.sum() + 0.5 * model.size)
    return float(-np.sum(prob(target) * np.log2(p)))


def close(a, b, tol=2e-12):
    return abs(float(a) - float(b)) <= tol * max(1.0, abs(float(a)), abs(float(b)))


def main():
    official = json.loads(RESULT.read_text(encoding="utf-8"))
    metadata = json.loads(META.read_text(encoding="utf-8"))
    saved = np.load(AGG)
    checks = []

    def check(name, passed, detail=""):
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    check("protocol hash", file_hash(PROTOCOL) == EXPECTED_PROTOCOL)
    check("aggregate hash metadata", file_hash(AGG) == metadata["aggregate_npz_sha256"])
    check("aggregate hash result", file_hash(AGG) == official["aggregate_sha256"])
    rebuilt = {}
    for rung, (low, high) in INTERVALS.items():
        print(f"validating r{rung}", flush=True)
        x = rebuild(low, high)
        rebuilt[rung] = x
        prefix = f"r{rung}__"
        comparisons = {
            "frequency": (x["f"], aggregate_hist48(saved[prefix + "frequency48"])),
            "frequency halves": (x["fh"], np.stack([aggregate_hist48(v) for v in saved[prefix + "frequency_half48"]])),
            "transition": (x["t"], aggregate_plane48(saved[prefix + "transition48"])),
            "transition halves": (x["th"], np.stack([aggregate_plane48(v) for v in saved[prefix + "transition_half48"]])),
            "gap offset": (x["fc"], aggregate_hist48(saved[prefix + "gap_offset_frequency48"])),
            "state offset": (x["tc"], aggregate_plane48(saved[prefix + "state_offset_transition48"])),
        }
        for label, (a, b) in comparisons.items():
            check(f"r{rung} {label} exact", np.array_equal(a, b), f"max_diff={int(np.max(np.abs(a-b)))}")
        check(f"r{rung} prime count", x["prime_count"] == metadata["rungs"][f"r{rung}"]["prime_total"])
        check(f"r{rung} equal ridge count", x["equal"] == metadata["rungs"][f"r{rung}"]["exact_equal_gap_nodes"])
        check(f"r{rung} incoming larger count", x["incoming_larger"] == metadata["rungs"][f"r{rung}"]["incoming_gap_larger_nodes"])
        check(f"r{rung} outgoing larger count", x["outgoing_larger"] == metadata["rungs"][f"r{rung}"]["outgoing_gap_larger_nodes"])

    pair_metrics = {}
    for a, b in ((9, 10), (10, 11)):
        pair_metrics[f"r{a}_r{b}"] = {
            "frequency_correlation": corr(rebuilt[a]["f"], rebuilt[b]["f"]),
            "frequency_jsd_bits": jsd(rebuilt[a]["f"], rebuilt[b]["f"]),
            "transition_cosine": cosine(rebuilt[a]["t"], rebuilt[b]["t"]),
            "transition_jsd_bits": jsd(rebuilt[a]["t"], rebuilt[b]["t"]),
        }
        for metric, value in pair_metrics[f"r{a}_r{b}"].items():
            check(
                f"r{a}/r{b} {metric}",
                close(value, official["primary"]["rung_pairs"][f"r{a}_r{b}"][metric]),
            )

    local = {}
    for rung in (10, 11):
        x = rebuilt[rung]
        local[rung] = {
            "frequency_direct_control_tv": tv(x["f"], x["fc"]),
            "frequency_split_half_tv": tv(x["fh"][0], x["fh"][1]),
            "transition_direct_control_tv": tv(x["t"], x["tc"]),
            "transition_split_half_tv": tv(x["th"][0], x["th"][1]),
            "mirror_correlation": corr(x["f"], x["f"][::-1]),
        }
        local[rung]["frequency_control_to_noise_ratio"] = local[rung]["frequency_direct_control_tv"] / local[rung]["frequency_split_half_tv"]
        local[rung]["transition_control_to_noise_ratio"] = local[rung]["transition_direct_control_tv"] / local[rung]["transition_split_half_tv"]
        for metric, value in local[rung].items():
            check(f"r{rung} {metric}", close(value, official["primary"]["local"][f"r{rung}"][metric]))

    transfer = {
        "r10_model_on_r11_bits": ce(rebuilt[10]["f"], rebuilt[11]["f"]),
        "r9_model_on_r11_bits": ce(rebuilt[9]["f"], rebuilt[11]["f"]),
        "r10_offset_control_on_r11_bits": ce(rebuilt[10]["fc"], rebuilt[11]["f"]),
    }
    for metric, value in transfer.items():
        check(metric, close(value, official["primary"]["transfer"][metric]))

    criteria = {
        "P1_frequency_recurrence": pair_metrics["r10_r11"]["frequency_correlation"] >= 0.995 and pair_metrics["r10_r11"]["frequency_jsd_bits"] <= 0.002,
        "P2_ordered_handover_recurrence": pair_metrics["r10_r11"]["transition_cosine"] >= 0.990 and pair_metrics["r10_r11"]["transition_jsd_bits"] <= 0.010,
        "P3_local_pair_not_inventory_only": all(local[r]["frequency_control_to_noise_ratio"] > 5 for r in (10, 11)),
        "P4_immediate_handover_not_frequency_only": all(local[r]["transition_control_to_noise_ratio"] > 5 for r in (10, 11)),
        "P5_rung_transfer": transfer["r10_model_on_r11_bits"] < transfer["r9_model_on_r11_bits"] and transfer["r10_model_on_r11_bits"] < transfer["r10_offset_control_on_r11_bits"],
        "P6_scale_convergence": pair_metrics["r10_r11"]["frequency_jsd_bits"] < pair_metrics["r9_r10"]["frequency_jsd_bits"] and pair_metrics["r10_r11"]["transition_jsd_bits"] < pair_metrics["r9_r10"]["transition_jsd_bits"],
        "P7_reversible_ridge_symmetry": all(local[r]["mirror_correlation"] >= 0.995 and abs(metadata["rungs"][f"r{r}"]["mean_asymmetry"]) <= 0.002 for r in (10, 11)),
    }
    check("registered criteria exact", criteria == official["registered_conditions"], json.dumps(criteria, sort_keys=True))
    check("pass count exact", sum(criteria.values()) == official["criteria_passed"])

    passed = sum(c["passed"] for c in checks)
    report = {
        "validator": "independent full-window sieve with chunk size 8,000,003; direct 24-bin construction",
        "checks_passed": passed,
        "checks_total": len(checks),
        "all_passed": passed == len(checks),
        "checks": checks,
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("checks_passed", "checks_total", "all_passed")}, indent=2))
    if not report["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
