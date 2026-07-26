"""Independent validation for Q32 edge-child pole handover.

This script does not import the primary runner.  It reconstructs the selected
lag directly from the Q27 cache and checks the stored headline values and
verdict.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
from collections import defaultdict

import numpy as np


HERE = pathlib.Path(__file__).resolve().parent
PROTOCOL = HERE / "Q32_EDGE_CHILD_POLE_HANDOVER_PROTOCOL_v1_FROZEN.md"
EXPECTED_PROTOCOL_SHA = "2c06d9f39476947a6d71d63d1237b5faf43745842121a48725ebab7556c712ef"
CACHE = HERE / "public_data" / "q27_network_reconstruction" / "q27_derived_cache.npz"
RESULTS = HERE / "Q32_EDGE_CHILD_POLE_HANDOVER_RESULTS.json"
OUTPUT = HERE / "Q32_EDGE_CHILD_POLE_HANDOVER_VALIDATION.json"

PAIRS = tuple((i, j) for i in range(12) for j in range(i + 1, 12))
PAIR_TO_INDEX = {pair: index for index, pair in enumerate(PAIRS)}
CONTROLS = ("topology", "seed", "time")
EPS = 1e-12


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def active_indices(row: np.ndarray) -> tuple[int, ...]:
    return tuple(
        PAIR_TO_INDEX[tuple(sorted((int(left), int(right))))]
        for left, right in row
    )


def sample_ok(branch: int, seed: int, time: int, pair: int, endpoint: int) -> bool:
    return (
        97 * seed + 53 * time + 31 * pair + 17 * endpoint + 11 * branch
    ) % 16 == 0


def choose(candidates: list[int], x_row: np.ndarray) -> int | None:
    candidates = [p for p in candidates if np.isfinite(float(x_row[p]))]
    if not candidates:
        return None
    return min(candidates, key=lambda p: (float(x_row[p]), p))


def shift_time(time: int, lag: int) -> int:
    return 250 + ((time - 250 + 137) % (250 - lag))


def movements(path: np.ndarray) -> tuple[float, float, float]:
    delta = np.diff(path)
    release = float(np.maximum(0.0, -delta).sum())
    accumulation = float(np.maximum(0.0, delta).sum())
    gain = float(path[-1] - path[0])
    return release, accumulation, gain


def add_route(
    row: dict[str, float | int],
    route: str,
    source_path: np.ndarray,
    child_path: np.ndarray,
) -> None:
    source_release, _, _ = movements(source_path)
    _, accumulation, gain = movements(child_path)
    row[f"{route}_start_x"] = float(child_path[0])
    row[f"{route}_gain"] = gain
    row[f"{route}_overlap"] = source_release * accumulation
    denominator = source_release + accumulation
    row[f"{route}_flow_x"] = (
        2.0 * accumulation / denominator if denominator > EPS else np.nan
    )


def trial_difference(
    rows: list[dict[str, float | int]],
    exact_key: str,
    control_key: str,
) -> float:
    exact: dict[tuple[int, int], list[float]] = defaultdict(list)
    control: dict[tuple[int, int], list[float]] = defaultdict(list)
    for row in rows:
        if control_key not in row:
            continue
        group = (int(row["branch"]), int(row["seed"]))
        exact[group].append(float(row[exact_key]))
        control[group].append(float(row[control_key]))
    groups = sorted(set(exact).intersection(control))
    return float(
        np.mean(
            [
                np.mean(exact[group]) - np.mean(control[group])
                for group in groups
            ]
        )
    )


def close(name: str, observed: float, expected: float, tolerance: float = 1e-10) -> None:
    if not np.isclose(observed, expected, rtol=tolerance, atol=tolerance):
        raise AssertionError(f"{name}: observed={observed} expected={expected}")


def main() -> None:
    checks: list[str] = []
    if sha256(PROTOCOL) != EXPECTED_PROTOCOL_SHA:
        raise AssertionError("protocol SHA-256 mismatch")
    checks.append("protocol checksum")

    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    lag = int(result["selected_lag"])
    if lag != 1:
        raise AssertionError(f"expected stored selected lag 1, found {lag}")
    checks.append("selected lag")

    data = np.load(CACHE, allow_pickle=False)
    closure = np.asarray(data["closure"], dtype=np.float64)
    edges = np.asarray(data["edges"], dtype=np.int8)
    scales = np.quantile(closure[:, :, :250], 0.95, axis=2)
    x = np.divide(
        2.0 * closure,
        scales[:, :, None],
        out=np.full_like(closure, np.nan),
        where=scales[:, :, None] >= 1e-10,
    )

    rows: list[dict[str, float | int]] = []
    for branch in range(2):
        for seed in range(100):
            for time in range(250, 493):
                active = active_indices(edges[branch, seed, time])
                for source_pair, nodes in enumerate(PAIRS):
                    source_start = float(x[branch, seed, time, source_pair])
                    if not np.isfinite(source_start) or source_start < 1.5:
                        continue
                    one_release = (
                        source_start - float(x[branch, seed, time + 1, source_pair])
                    )
                    if not np.isfinite(one_release) or one_release <= 0:
                        continue
                    for endpoint in nodes:
                        if not sample_ok(
                            branch, seed, time, source_pair, endpoint
                        ):
                            continue
                        exact = choose(
                            [
                                p
                                for p in active
                                if p != source_pair and endpoint in PAIRS[p]
                            ],
                            x[branch, seed, time],
                        )
                        if exact is None:
                            continue
                        source_path = x[
                            branch, seed, time : time + lag + 1, source_pair
                        ]
                        exact_path = x[
                            branch, seed, time : time + lag + 1, exact
                        ]
                        row: dict[str, float | int] = {
                            "branch": branch,
                            "seed": seed,
                        }
                        add_route(row, "exact", source_path, exact_path)

                        topology = choose(
                            [
                                p
                                for p in active
                                if not set(nodes).intersection(PAIRS[p])
                            ],
                            x[branch, seed, time],
                        )
                        if topology is not None:
                            add_route(
                                row,
                                "topology",
                                source_path,
                                x[
                                    branch,
                                    seed,
                                    time : time + lag + 1,
                                    topology,
                                ],
                            )

                        shifted_seed = (seed + 37) % 100
                        seed_active = active_indices(
                            edges[branch, shifted_seed, time]
                        )
                        seed_child = choose(
                            [
                                p
                                for p in seed_active
                                if p != source_pair and endpoint in PAIRS[p]
                            ],
                            x[branch, shifted_seed, time],
                        )
                        if seed_child is not None:
                            add_route(
                                row,
                                "seed",
                                source_path,
                                x[
                                    branch,
                                    shifted_seed,
                                    time : time + lag + 1,
                                    seed_child,
                                ],
                            )

                        control_time = shift_time(time, lag)
                        time_active = active_indices(
                            edges[branch, seed, control_time]
                        )
                        time_child = choose(
                            [
                                p
                                for p in time_active
                                if p != source_pair and endpoint in PAIRS[p]
                            ],
                            x[branch, seed, control_time],
                        )
                        if time_child is not None:
                            add_route(
                                row,
                                "time",
                                source_path,
                                x[
                                    branch,
                                    seed,
                                    control_time : control_time + lag + 1,
                                    time_child,
                                ],
                            )
                        rows.append(row)

    expected_count = int(result["event_counts"]["evaluation_selected_lag"])
    if len(rows) != expected_count:
        raise AssertionError(f"event count {len(rows)} != {expected_count}")
    checks.append("full event reconstruction")

    stored = result["evaluation_selected_lag_summary"]
    exact_start = np.asarray([float(row["exact_start_x"]) for row in rows])
    exact_gain = np.asarray([float(row["exact_gain"]) for row in rows])
    exact_overlap = np.asarray([float(row["exact_overlap"]) for row in rows])
    exact_flow = np.asarray(
        [
            float(row["exact_flow_x"])
            for row in rows
            if np.isfinite(float(row["exact_flow_x"]))
        ]
    )
    close("exact start mean", float(exact_start.mean()), stored["exact_start_x_mean"])
    close(
        "exact start median",
        float(np.median(exact_start)),
        stored["exact_start_x_median"],
    )
    close(
        "start <=0.5",
        float(np.mean(exact_start <= 0.5)),
        stored["exact_start_le_05_fraction"],
    )
    close("exact gain", float(exact_gain.mean()), stored["exact_gain_mean"])
    close("exact overlap", float(exact_overlap.mean()), stored["exact_overlap_mean"])
    close("exact flow", float(exact_flow.mean()), stored["exact_flow_x_mean"])
    checks.extend(
        [
            "starting-position statistics",
            "signed child gain",
            "source-release child-accumulation overlap",
            "flow coordinate",
        ]
    )

    for control in CONTROLS:
        difference = trial_difference(
            rows,
            "exact_gain",
            f"{control}_gain",
        )
        close(
            f"exact minus {control} gain",
            difference,
            stored[f"exact_minus_{control}_gain"],
        )
    checks.append("trial-weighted control differences")

    expected_verdict = "ORDERED CHILD TRANSFER WITHOUT POLE-ORIGIN SUPPORT"
    if result["verdict"] != expected_verdict:
        raise AssertionError("stored verdict does not match gate outcome")
    checks.append("verdict boundary")

    payload = {
        "validation": "PASS",
        "checks_passed": len(checks),
        "checks": checks,
        "recomputed_events": len(rows),
        "selected_lag": lag,
        "verdict": expected_verdict,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Q32 VALIDATION: PASS ({len(checks)}/{len(checks)})")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
