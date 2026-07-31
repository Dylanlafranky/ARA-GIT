"""Independent high-level validation for Q51.

The validator does not import the Q51 or Q50 implementation. It re-extracts
Q49 complete-cycle centres, then independently reconstructs Q51 summaries.
"""

from __future__ import annotations

import hashlib
import json
import math
import pathlib
from collections import defaultdict

import numpy as np

from q49_external_time_vector import build_events, extract_centres


HERE = pathlib.Path(__file__).resolve().parent
PUBLIC = HERE / "public_data"
RESULTS_PATH = HERE / "Q51_CROSS_ARCHIVE_EXTERNAL_REVERSAL_RESULTS.json"
OUTPUT_PATH = HERE / "Q51_CROSS_ARCHIVE_EXTERNAL_REVERSAL_VALIDATION.json"
ARCHIVES = {
    "random": PUBLIC / "q27_network_reconstruction" / "q27_derived_cache.npz",
    "greedy": PUBLIC / "q34_cross_archive_greedy" / "q34_derived_cache.npz",
    "landmax": PUBLIC / "q37_signed_crossing_landmax" / "q37_derived_cache.npz",
    "mimic": PUBLIC / "q38_fixed_anchor_mimic" / "q38_derived_cache.npz",
}
BRANCH_SHORT = {
    "c2_2local connectivity": "c2",
    "c4_2local connectivity": "c4",
}
PHI = (1.0 + math.sqrt(5.0)) / 2.0
LEFT = 1.0 / math.e
RIGHT = PHI - 1.0
CENTRE = LEFT + (RIGHT - LEFT) / 2.0
AXIS = np.asarray(
    [math.cos(2 * math.pi * CENTRE), math.sin(2 * math.pi * CENTRE)]
)
BOOTSTRAP_DRAWS = 5_000
BOOTSTRAP_SEED = 500030
EPS = 1e-15


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def vec(row: dict[str, object]) -> np.ndarray:
    return np.asarray([float(row["circle_du"]), float(row["circle_dv"])]) / float(
        row["radius_mean"]
    )


def aggregate(rows: list[dict[str, object]]) -> dict[str, float | int]:
    if not rows:
        return {"events": 0, "movement": math.nan, "x": math.nan, "heading": math.nan}
    vectors = np.asarray([vec(row) for row in rows])
    movement = float(np.linalg.norm(vectors, axis=1).sum())
    total = vectors.sum(axis=0)
    x = 1.0 - float(total @ AXIS) / movement
    heading = float((math.atan2(total[1], total[0]) / (2 * math.pi)) % 1.0)
    return {"events": len(rows), "movement": movement, "x": x, "heading": heading}


def distance(a: float, b: float) -> float:
    delta = abs(a - b)
    return min(delta, 1 - delta)


def analyse(events: list[dict[str, object]]) -> dict[str, object]:
    grouped: dict[tuple[int, int], list[dict[str, object]]] = defaultdict(list)
    for row in events:
        grouped[(int(row["seed"]), int(row["pair_index"]))].append(row)
    fixed = {
        key
        for key, rows in grouped.items()
        if sum(int(row["current_end"]) < 250 for row in rows) >= 3
        and sum(int(row["current_start"]) >= 250 for row in rows) >= 3
    }
    if not fixed:
        return {"eligible": False, "fixed_lineages": 0}
    development = [
        row
        for key in fixed
        for row in grouped[key]
        if int(row["current_end"]) < 250
    ]
    evaluation = [
        row
        for key in fixed
        for row in grouped[key]
        if int(row["current_start"]) >= 250
    ]
    dev = aggregate(development)
    eva = aggregate(evaluation)
    separation = distance(float(dev["heading"]), float(eva["heading"]))

    lineages: list[tuple[int, float, float, float]] = []
    d_to_o = o_to_d = 0
    for key in fixed:
        d = aggregate(
            [
                row
                for row in grouped[key]
                if int(row["current_end"]) < 250
            ]
        )
        e = aggregate(
            [
                row
                for row in grouped[key]
                if int(row["current_start"]) >= 250
            ]
        )
        dx = float(e["x"]) - float(d["x"])
        lineages.append((key[0], float(d["x"]), float(e["x"]), dx))
        d_to_o += float(d["x"]) < 1 < float(e["x"])
        o_to_d += float(d["x"]) > 1 > float(e["x"])

    by_seed: dict[int, list[float]] = defaultdict(list)
    for seed, _, _, delta in lineages:
        by_seed[seed].append(delta)
    seed_means = np.asarray(
        [np.mean(by_seed[seed]) for seed in sorted(by_seed)], dtype=np.float64
    )
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    chosen = rng.integers(
        0, seed_means.size, size=(BOOTSTRAP_DRAWS, seed_means.size)
    )
    bootstrap = np.mean(seed_means[chosen], axis=1)
    ci = np.quantile(bootstrap, [0.025, 0.975])

    bins: list[dict[str, float | int]] = []
    for left in range(0, 500, 25):
        rows = [
            row
            for key in fixed
            for row in grouped[key]
            if left <= int(row["current_start"]) < left + 25
        ]
        value = aggregate(rows)
        bins.append(
            {
                "left": left,
                "x": float(value["x"]),
                "mean_movement": float(value["movement"]) / int(value["events"]),
            }
        )
    values = np.asarray([item["x"] for item in bins])
    low = np.flatnonzero(values <= 0.5)
    high = np.flatnonzero(values >= 1.5)
    complete = any(
        any(later_low > high_index for later_low in low)
        for first_low in low
        for high_index in high
        if high_index > first_low
    )
    crossings = [
        index
        for index in range(1, len(values))
        if values[index - 1] < 1 <= values[index]
    ]
    recovers = False
    recovery_ratio = math.nan
    if crossings:
        index = crossings[0]
        movement = np.asarray([item["mean_movement"] for item in bins])
        pre = float(np.mean(movement[max(0, index - 2) : index]))
        later = movement[index + 1 :]
        peak = float(np.nanmax(later)) if later.size else math.nan
        recovery_ratio = peak / pre
        recovers = recovery_ratio >= 0.25
    dev_mean = float(dev["movement"]) / int(dev["events"])
    eval_mean = float(eva["movement"]) / int(eva["events"])
    movement_ratio = eval_mean / dev_mean
    gates = {
        "R1_opposing_strata": bool(float(dev["x"]) < 1 < float(eva["x"])),
        "R2_half_turn": bool(abs(separation - 0.5) <= 0.10),
        "R3_same_lineage": bool(d_to_o > o_to_d and ci[0] > 0),
        "R4_active_movement": bool(movement_ratio >= 0.10 or recovers),
        "R5_complete_return": bool(complete),
    }
    return {
        "eligible": True,
        "fixed_lineages": len(fixed),
        "fixed_seeds": len({key[0] for key in fixed}),
        "dev_x": float(dev["x"]),
        "eval_x": float(eva["x"]),
        "separation": separation,
        "movement_ratio": movement_ratio,
        "recovery_ratio": recovery_ratio,
        "d_to_o": int(d_to_o),
        "o_to_d": int(o_to_d),
        "bootstrap_ci": [float(value) for value in ci],
        "complete": bool(complete),
        "gates": gates,
    }


def main() -> None:
    saved = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    checks: list[dict[str, object]] = []
    orientation_passes = active_passes = complete_passes = 0

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "pass": bool(passed), "detail": detail})

    for strategy, path in ARCHIVES.items():
        check(
            f"{strategy} source hash",
            sha256(path) == saved["archives"][strategy]["sha256"],
            sha256(path),
        )
        data = np.load(path, allow_pickle=False)
        for index, name in enumerate(data["branch_names"].tolist()):
            short = BRANCH_SHORT[str(name)]
            key = f"{strategy}:{short}"
            centres, _ = extract_centres(data["closure"][index], data["pairs"])
            events = build_events(centres)
            result = analyse(events)
            target = saved["branches"][key]["primary"]
            if not result["eligible"]:
                passed = (
                    target["eligible"] is False
                    and target["fixed_lineages"] == 0
                )
                check(key, passed, "NOT TESTABLE under fixed lineage rule")
                continue
            numeric = (
                result["fixed_lineages"] == target["fixed_lineages"]
                and result["fixed_seeds"] == target["fixed_seeds"]
                and abs(result["dev_x"] - target["development"]["x"]) < 1e-10
                and abs(result["eval_x"] - target["evaluation"]["x"]) < 1e-10
                and abs(result["separation"] - target["heading_separation_turns"])
                < 1e-10
                and abs(
                    result["movement_ratio"]
                    - target["evaluation_to_development_mean_movement_ratio"]
                )
                < 1e-10
                and result["d_to_o"] == target["paired"]["declared_to_opposite"]
                and result["o_to_d"] == target["paired"]["opposite_to_declared"]
                and np.allclose(
                    result["bootstrap_ci"], target["bootstrap"]["ci95"], atol=1e-10
                )
                and result["gates"] == target["gates"]
            )
            check(
                key,
                numeric,
                f"x {result['dev_x']:.6f}→{result['eval_x']:.6f}; "
                f"separation {result['separation']:.6f}; gates {result['gates']}",
            )
            if short == "c2":
                first_three = all(
                    result["gates"][gate]
                    for gate in (
                        "R1_opposing_strata",
                        "R2_half_turn",
                        "R3_same_lineage",
                    )
                )
                orientation_passes += first_three
                active_passes += first_three and result["gates"]["R4_active_movement"]
                complete_passes += all(result["gates"].values())

    cross = saved["primary_c2_summary"]
    check(
        "cross-archive summary",
        orientation_passes == cross["orientation_reversal_passes"]
        and active_passes == cross["active_traversal_passes"]
        and complete_passes == cross["complete_cycle_passes"],
        f"orientation={orientation_passes}; active={active_passes}; complete={complete_passes}",
    )
    payload = {
        "validation": "PASS" if all(item["pass"] for item in checks) else "FAIL",
        "checks_passed": sum(item["pass"] for item in checks),
        "checks_total": len(checks),
        "checks": checks,
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
