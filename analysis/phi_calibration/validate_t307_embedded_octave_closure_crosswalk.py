"""Independent structural validator for T307."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RESULTS = HERE / "T307_EMBEDDED_OCTAVE_CLOSURE_CROSSWALK_RESULTS.json"
SEEDS = HERE / "T307_EMBEDDED_OCTAVE_CLOSURE_SEED_RATIOS.csv"
FIGURE = HERE / "T307_EMBEDDED_OCTAVE_CLOSURE_CROSSWALK.png"
Q40C = ROOT / "analysis" / "quantum" / "Q40C_POST_RESULT_DOUBLE_HELIX_RESULTS.json"
T306 = ROOT / "analysis" / "muon" / "T306_EMBEDDED_E_PHI_THREAD_RESULTS.json"
OUT = HERE / "T307_EMBEDDED_OCTAVE_CLOSURE_CROSSWALK_VALIDATION.json"

EXPECTED_Q40C_SHA256 = "5BFDEA834CD3E9F40ECD0FEF75DEE8A848D00902C62F342FA1DB96F21128B242"
EXPECTED_T306_SHA256 = "F1D524DD32B7A6B1DFF5537FE0313164A318B0710BBFDCEE0A74FDFB1A483484"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()


def close(a: float, b: float, tolerance: float = 1e-12) -> bool:
    return bool(abs(float(a) - float(b)) <= tolerance)


def main() -> None:
    checks: list[dict[str, object]] = []

    qhash = digest(Q40C)
    thash = digest(T306)
    checks.append(
        {
            "name": "source hashes",
            "pass": qhash == EXPECTED_Q40C_SHA256 and thash == EXPECTED_T306_SHA256,
        }
    )

    with RESULTS.open("r", encoding="utf-8") as handle:
        saved = json.load(handle)
    with Q40C.open("r", encoding="utf-8") as handle:
        q40c = json.load(handle)
    with T306.open("r", encoding="utf-8") as handle:
        t306 = json.load(handle)

    phi = (1.0 + math.sqrt(5.0)) / 2.0
    lower = math.exp(-1.0)
    anti = 2.0 - phi
    midpoint = (lower + phi) / 2.0
    displacement = 1.0 - midpoint
    radius = (anti - lower) / 2.0
    parent_diameter = phi - lower
    child_diameter = 2.0 * radius
    raw_width_ratio = child_diameter / parent_diameter
    geometry = saved["geometry"]
    checks.append(
        {
            "name": "exact geometry recalculation",
            "pass": all(
                [
                    close(geometry["parent_midpoint"], midpoint),
                    close(geometry["parent_ridge_displacement"], displacement),
                    close(geometry["child_radius"], radius),
                    close(geometry["parent_diameter"], parent_diameter),
                    close(geometry["child_diameter"], child_diameter),
                    close(geometry["raw_child_to_parent_width_ratio"], raw_width_ratio),
                    close(radius, displacement),
                    close(geometry["geometry_closure_ratio_rC_over_dP"], 1.0),
                ]
            ),
            "max_abs_error": float(
                max(
                    abs(geometry["parent_midpoint"] - midpoint),
                    abs(geometry["parent_ridge_displacement"] - displacement),
                    abs(geometry["child_radius"] - radius),
                    abs(radius - displacement),
                )
            ),
        }
    )
    checks.append(
        {
            "name": "T306 saved geometry agreement",
            "pass": all(
                [
                    close(midpoint, t306["geometry"]["embedded_centre_parent_coordinate"]),
                    close(2.0 * radius, t306["geometry"]["child_carrier_separation"]),
                    close(2.0 * displacement, t306["geometry"]["closure_deficit"]),
                ]
            ),
        }
    )

    groups: dict[int, dict[str, list[float]]] = defaultdict(
        lambda: {"child": [], "parent": []}
    )
    for row in q40c["population_rows"]:
        seed = int(row["seed"])
        value = float(row["angular_period_samples"])
        if row["posthoc_two_turn_7_5_family"]:
            groups[seed]["child"].append(value)
        if row["posthoc_one_turn_15_family"]:
            groups[seed]["parent"].append(value)

    recalculated = []
    for seed in sorted(groups):
        child = groups[seed]["child"]
        parent = groups[seed]["parent"]
        if child and parent:
            tc = float(np.median(child))
            tp = float(np.median(parent))
            recalculated.append((seed, len(child), len(parent), tc, tp, 2.0 * tc / tp))

    with SEEDS.open("r", encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    csv_ok = len(csv_rows) == len(recalculated)
    max_row_error = 0.0
    if csv_ok:
        for csv_row, expected in zip(csv_rows, recalculated):
            seed, nc, np_, tc, tp, ratio = expected
            csv_ok &= int(csv_row["seed"]) == seed
            csv_ok &= int(csv_row["child_lineages"]) == nc
            csv_ok &= int(csv_row["parent_lineages"]) == np_
            local_error = max(
                abs(float(csv_row["T_child_median"]) - tc),
                abs(float(csv_row["T_parent_median"]) - tp),
                abs(float(csv_row["Q_2Tc_over_Tp"]) - ratio),
                abs(float(csv_row["absolute_closure_error"]) - abs(ratio - 1.0)),
            )
            max_row_error = max(max_row_error, local_error)
        csv_ok &= max_row_error <= 1e-12
    checks.append(
        {
            "name": "seed CSV independent reconstruction",
            "pass": bool(csv_ok),
            "rows": len(recalculated),
            "max_abs_error": max_row_error,
        }
    )

    ratios = np.array([row[-1] for row in recalculated])
    qsummary = saved["quantum_cadence"]["seed_ratio_Q_2Tc_over_Tp"]
    summary_ok = all(
        [
            saved["quantum_cadence"]["eligible_seeds"] == len(recalculated),
            close(qsummary["median"], np.median(ratios)),
            close(qsummary["mean"], np.mean(ratios)),
            close(
                qsummary["mean_absolute_distance_from_1"],
                np.mean(np.abs(ratios - 1.0)),
            ),
            close(
                qsummary["median_absolute_distance_from_1"],
                np.median(np.abs(ratios - 1.0)),
            ),
        ]
    )
    checks.append(
        {
            "name": "quantum cadence summary",
            "pass": bool(summary_ok),
            "recalculated_median": float(np.median(ratios)),
        }
    )

    factors = {
        "1": 1.0,
        "3/2": 1.5,
        "phi": phi,
        "2": 2.0,
        "e": math.e,
        "3": 3.0,
    }
    children = np.array([row[3] for row in recalculated])
    parents = np.array([row[4] for row in recalculated])
    errors = {
        label: float(np.median(np.abs(np.log(parents / (factor * children)))))
        for label, factor in factors.items()
    }
    saved_errors = saved["candidate_factor_control"]["errors"]
    candidate_ok = all(close(errors[label], saved_errors[label]) for label in factors)
    candidate_ok &= min(errors, key=errors.get) == "2"
    checks.append(
        {
            "name": "candidate factor control",
            "pass": bool(candidate_ok),
            "winner": min(errors, key=errors.get),
        }
    )

    # Reproduce the deterministic bootstrap and shuffle in the saved order.
    rng = np.random.default_rng(20260730)
    boot = np.empty(10_000)
    for index in range(10_000):
        boot[index] = np.median(ratios[rng.integers(0, len(ratios), size=len(ratios))])
    boot_ci = np.quantile(boot, [0.025, 0.975])
    saved_ci = np.array(qsummary["bootstrap_median_95_ci"])
    checks.append(
        {
            "name": "bootstrap interval",
            "pass": bool(np.max(np.abs(boot_ci - saved_ci)) <= 1e-12),
            "max_abs_error": float(np.max(np.abs(boot_ci - saved_ci))),
        }
    )

    paired_error = float(np.mean(np.abs(ratios - 1.0)))
    shuffles = np.empty(10_000)
    for index in range(10_000):
        shuffled = parents[rng.permutation(len(parents))]
        shuffles[index] = np.mean(np.abs(2.0 * children / shuffled - 1.0))
    pair_p = float(np.mean(shuffles <= paired_error))
    saved_pair = saved["seed_pairing_control"]
    pairing_ok = all(
        [
            close(saved_pair["paired_mean_absolute_closure_error"], paired_error),
            close(saved_pair["p_shuffled_no_worse_than_paired"], pair_p),
            pair_p > 0.05,
        ]
    )
    checks.append(
        {
            "name": "seed pairing shuffle",
            "pass": bool(pairing_ok),
            "recalculated_p": pair_p,
        }
    )

    image_ok = False
    image_size = None
    if FIGURE.exists() and FIGURE.stat().st_size > 10_000:
        with Image.open(FIGURE) as image:
            image.verify()
        with Image.open(FIGURE) as image:
            image_size = list(image.size)
            image_ok = image.size == (1700, 1120)
    checks.append(
        {
            "name": "figure integrity",
            "pass": image_ok,
            "size": image_size,
            "bytes": FIGURE.stat().st_size if FIGURE.exists() else 0,
        }
    )

    validation = {
        "test": "T307 independent validation",
        "status": "PASS" if all(check["pass"] for check in checks) else "FAIL",
        "checks_passed": int(sum(bool(check["pass"]) for check in checks)),
        "checks_total": len(checks),
        "checks": checks,
        "scope": (
            "Structural and numerical validation of a retrospective crosswalk. "
            "Not independent quantum replication and not empirical validation of Phi causation."
        ),
    }
    with OUT.open("w", encoding="utf-8") as handle:
        json.dump(validation, handle, indent=2)
        handle.write("\n")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
