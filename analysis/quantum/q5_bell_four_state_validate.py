#!/usr/bin/env python3
"""Independent calculation and artifact validation for frozen T263/Q5."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "public_data" / "q4_bell_tomography"
PROTOCOL = HERE / "Q5_BELL_FOUR_STATE_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q5_BELL_FOUR_STATE_PROTOCOL_v1_FROZEN.sha256"
RECORDS_CSV = HERE / "Q5_BELL_FOUR_STATE_RECORDS.csv"
PROJECTIONS_CSV = HERE / "Q5_BELL_FOUR_STATE_PROJECTIONS.csv"
BOOTSTRAP_CSV = HERE / "Q5_BELL_FOUR_STATE_BOOTSTRAP.csv"
PAIRWISE_CSV = HERE / "Q5_BELL_FOUR_STATE_PAIRWISE.csv"
RESULTS_JSON = HERE / "Q5_BELL_FOUR_STATE_RESULTS.json"
VALIDATION_JSON = HERE / "Q5_BELL_FOUR_STATE_VALIDATION.json"

STATE_ORDER = ("Phi-plus", "Phi-minus", "Psi-plus", "Psi-minus")
ORIENTATIONS = ("II", "IX", "IY", "XI", "XX", "XY", "YI", "YX", "YY")
OUTCOMES = ("DOWNDOWN", "DOWNUP", "UPDOWN", "UPUP")
PROJECTIONS = (
    "ZZ", "YZ", "XZ", "ZY", "ZX", "YY", "YX", "XY", "XX",
    "YI", "XI", "IY", "IX", "ZI", "IZ",
)
LOCAL = ("YI", "XI", "IY", "IX", "ZI", "IZ")
SAME = ("XX", "YY", "ZZ")
MIXED = ("YZ", "XZ", "ZY", "ZX", "YX", "XY")
EXPECTED_RECORDS = {
    "Phi-plus": 300,
    "Phi-minus": 80,
    "Psi-plus": 600,
    "Psi-minus": 600,
}
ARCHIVES = {
    "Phi-plus": (
        "UPUP+DOWNDOWN.zip",
        151973378,
        "3275210b912d51e5f10ba99d93ad6ca5",
    ),
    "Phi-minus": (
        "UPUP-DOWNDOWN.zip",
        41182988,
        "8cd8a5f2b3b9a2ccd090e47312bcc390",
    ),
    "Psi-plus": (
        "UPDOWN+DOWNUP.zip",
        305874138,
        "43f782ed4404b01393fb57a2da5d1534",
    ),
    "Psi-minus": (
        "UPDOWN-DOWNUP.zip",
        307629500,
        "1724b4484ffb88e41dbac5f50981e91a",
    ),
}
PATTERNS = {
    "Phi-plus": {"XX": 1.0, "YY": -1.0, "ZZ": 1.0},
    "Phi-minus": {"XX": -1.0, "YY": 1.0, "ZZ": 1.0},
    "Psi-plus": {"XX": 1.0, "YY": 1.0, "ZZ": -1.0},
    "Psi-minus": {"XX": -1.0, "YY": -1.0, "ZZ": -1.0},
}
SEED = 2026072405
REPS = 2000


def digest(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def add_check(
    checks: list[dict[str, object]],
    name: str,
    passed: bool,
    detail: str,
) -> None:
    checks.append({"name": name, "pass": bool(passed), "detail": detail})


def reconstruct(p: dict[str, np.ndarray]) -> dict[str, float]:
    ii, ix, iy = p["II"], p["IX"], p["IY"]
    xi, xx, xy = p["XI"], p["XX"], p["XY"]
    yi, yx, yy = p["YI"], p["YX"], p["YY"]
    return {
        "II": float(ii.sum()),
        "IX": float(ix[0] + ix[1] - ix[2] - ix[3]),
        "IY": float(iy[0] + iy[1] - iy[2] - iy[3]),
        "IZ": float(ii[0] + ii[1] - ii[2] - ii[3]),
        "XI": float(xi[0] - xi[1] + xi[2] - xi[3]),
        "XX": float(xx[0] - xx[1] - xx[2] + xx[3]),
        "XY": float(xy[0] - xy[1] - xy[2] + xy[3]),
        "XZ": float(xi[0] - xi[1] - xi[2] + xi[3]),
        "YI": float(yi[0] - yi[1] + yi[2] - yi[3]),
        "YX": float(yx[0] - yx[1] - yx[2] + yx[3]),
        "YY": float(yy[0] - yy[1] - yy[2] + yy[3]),
        "YZ": float(yi[0] - yi[1] - yi[2] + yi[3]),
        "ZI": float(ii[0] - ii[1] + ii[2] - ii[3]),
        "ZX": float(ix[0] - ix[1] - ix[2] + ix[3]),
        "ZY": float(iy[0] - iy[1] - iy[2] + iy[3]),
        "ZZ": float(ii[0] - ii[1] - ii[2] + ii[3]),
    }


def metrics(exp: dict[str, float]) -> dict[str, float]:
    local = float(np.mean([abs(exp[label]) for label in LOCAL]))
    same = float(np.mean([abs(exp[label]) for label in SAME]))
    return {
        "local_child_mean_abs": local,
        "same_axis_mean_abs": same,
        "same_axis_min_abs": float(min(abs(exp[label]) for label in SAME)),
        "same_minus_local": same - local,
        "mixed_pair_mean_abs": float(
            np.mean([abs(exp[label]) for label in MIXED])
        ),
        "correlation_product": float(
            exp["XX"] * exp["YY"] * exp["ZZ"]
        ),
    }


def rank_parent(
    exp: dict[str, float]
) -> tuple[str, float, str, float, float, dict[str, float]]:
    errors = {
        name: float(
            np.mean(
                [abs(exp[label] - pattern[label]) for label in SAME]
            )
        )
        for name, pattern in PATTERNS.items()
    }
    ranked = sorted(errors.items(), key=lambda item: (item[1], item[0]))
    return (
        ranked[0][0],
        ranked[0][1],
        ranked[1][0],
        ranked[1][1],
        ranked[1][1] - ranked[0][1],
        errors,
    )


def read_records() -> tuple[
    dict[str, dict[str, np.ndarray]], list[dict[str, str]]
]:
    with RECORDS_CSV.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    grouped: dict[str, dict[str, dict[int, dict[str, float]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(dict))
    )
    for row in rows:
        grouped[row["state"]][row["orientation"]][
            int(row["record_index"])
        ][row["outcome"]] = float(row["classified_present"])
    arrays: dict[str, dict[str, np.ndarray]] = {}
    for state in STATE_ORDER:
        arrays[state] = {}
        for orientation in ORIENTATIONS:
            records = grouped[state][orientation]
            arrays[state][orientation] = np.array(
                [
                    [records[index][outcome] for outcome in OUTCOMES]
                    for index in sorted(records)
                ],
                dtype=float,
            )
    return arrays, rows


def main() -> None:
    checks: list[dict[str, object]] = []
    results = json.loads(RESULTS_JSON.read_text(encoding="utf-8"))

    expected_protocol = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    observed_protocol = digest(PROTOCOL, "sha256")
    add_check(
        checks,
        "frozen protocol checksum",
        observed_protocol == expected_protocol == results["protocol_sha256"],
        observed_protocol,
    )

    archive_ok = True
    archive_details = []
    for state, (name, size, expected_md5) in ARCHIVES.items():
        path = DATA_DIR / name
        observed_md5 = digest(path, "md5")
        archive_ok &= (
            path.stat().st_size == size
            and observed_md5 == expected_md5
            and results["source"]["archive_md5s"][state] == expected_md5
        )
        archive_details.append(f"{state}:{observed_md5}")
    add_check(
        checks,
        "four archive sizes and checksums",
        archive_ok,
        "; ".join(archive_details),
    )

    arrays, rows = read_records()
    expected_rows = sum(
        count * len(ORIENTATIONS) * len(OUTCOMES)
        for count in EXPECTED_RECORDS.values()
    )
    add_check(
        checks, "record row count", len(rows) == expected_rows, str(len(rows))
    )

    keys = {
        (
            row["state"],
            row["orientation"],
            row["record_index"],
            row["outcome"],
        )
        for row in rows
    }
    add_check(
        checks,
        "record key uniqueness",
        len(keys) == len(rows),
        f"{len(keys)} unique",
    )

    coverage_ok = all(
        arrays[state][orientation].shape
        == (EXPECTED_RECORDS[state], len(OUTCOMES))
        for state in STATE_ORDER
        for orientation in ORIENTATIONS
    )
    add_check(
        checks,
        "state and orientation coverage",
        coverage_ok,
        "80, 300 or 600 records per orientation as declared",
    )

    fractions = np.array(
        [float(row["segment_tunnelling_fraction"]) for row in rows]
    )
    grid_ok = bool(
        np.all(fractions >= 0)
        and np.all(fractions <= 1)
        and np.allclose(fractions * 40, np.round(fractions * 40), atol=1e-12)
    )
    add_check(
        checks,
        "segment fractions use 40-readout grid",
        grid_ok,
        "all rows",
    )

    threshold_ok = all(
        int(row["classified_present"])
        == int(float(row["segment_tunnelling_fraction"]) > 0.5)
        for row in rows
    )
    add_check(
        checks,
        "strict state-threshold reproduction",
        threshold_ok,
        "fraction > 0.5",
    )

    probabilities = {
        state: {
            orientation: values.mean(axis=0)
            for orientation, values in state_arrays.items()
        }
        for state, state_arrays in arrays.items()
    }
    exps = {
        state: reconstruct(state_probabilities)
        for state, state_probabilities in probabilities.items()
    }

    expectations_ok = all(
        math.isclose(
            exps[state][label],
            results["states"][state]["expectations"][label],
            abs_tol=1e-12,
        )
        for state in STATE_ORDER
        for label in ("II",) + PROJECTIONS
    )
    add_check(
        checks,
        "all four expectation sets independently reconstructed",
        expectations_ok,
        "64/64 including II normalization",
    )

    with PROJECTIONS_CSV.open(newline="", encoding="utf-8") as handle:
        projection_rows = list(csv.DictReader(handle))
    projection_ok = (
        len(projection_rows) == 60
        and all(
            math.isclose(
                float(row["expectation"]),
                exps[row["state"]][row["projection"]],
                abs_tol=1e-12,
            )
            for row in projection_rows
        )
    )
    add_check(
        checks,
        "projection table values",
        projection_ok,
        f"{len(projection_rows)}/60 rows",
    )

    affine_ok = all(
        math.isclose(
            float(row["ara_coordinate"]),
            1.0 - float(row["expectation"]),
            abs_tol=1e-12,
        )
        and math.isclose(
            float(row["ara_coordinate"])
            + float(row["reversed_ara_coordinate"]),
            2.0,
            abs_tol=1e-12,
        )
        for row in projection_rows
    )
    add_check(
        checks,
        "ARA affine and pole-reversal identities",
        affine_ok,
        "60/60",
    )

    state_metrics = {state: metrics(exp) for state, exp in exps.items()}
    metrics_ok = all(
        math.isclose(
            value,
            results["states"][state]["metrics"][name],
            abs_tol=1e-12,
        )
        for state, values in state_metrics.items()
        for name, value in values.items()
    )
    add_check(
        checks,
        "per-state group metrics",
        metrics_ok,
        "24/24",
    )

    rankings = {state: rank_parent(exp) for state, exp in exps.items()}
    ranking_ok = all(
        rankings[state][0] == state
        and results["states"][state]["closest_parent"] == state
        and math.isclose(
            rankings[state][4],
            results["states"][state]["bell_margin"],
            abs_tol=1e-12,
        )
        for state in STATE_ORDER
    )
    add_check(
        checks,
        "four-way Bell parent ranking",
        ranking_ok,
        "4/4 declared parents closest",
    )

    per_state_gate_ok = True
    independently_passed = 0
    for state in STATE_ORDER:
        exp = exps[state]
        met = state_metrics[state]
        closest, _, _, _, margin, _ = rankings[state]
        target = PATTERNS[state]
        passes = [
            met["local_child_mean_abs"] <= 0.20,
            all((exp[label] > 0) == (target[label] > 0) for label in SAME),
            met["same_axis_min_abs"] >= 0.50,
            met["same_minus_local"] >= 0.40,
            met["mixed_pair_mean_abs"] <= 0.25,
            met["correlation_product"] <= -0.125,
            closest == state and margin >= 0.20,
            True,
        ]
        independently_passed += sum(passes)
        saved = results["states"][state]["gates"]
        per_state_gate_ok &= all(
            bool(gate["pass"]) for gate in saved.values()
        ) and sum(passes) == 8
    add_check(
        checks,
        "32 per-state frozen gates independently recomputed",
        per_state_gate_ok and independently_passed == 32,
        f"{independently_passed}/32",
    )

    with PAIRWISE_CSV.open(newline="", encoding="utf-8") as handle:
        pairwise_rows = list(csv.DictReader(handle))
    parent_vectors = {
        state: np.array([exps[state][label] for label in SAME])
        for state in STATE_ORDER
    }
    local_vectors = {
        state: np.array([exps[state][label] for label in LOCAL])
        for state in STATE_ORDER
    }
    pairwise_ok = len(pairwise_rows) == 6
    recomputed_distances = []
    for row in pairwise_rows:
        left, right = row["state_a"], row["state_b"]
        parent_distance = float(
            np.linalg.norm(parent_vectors[left] - parent_vectors[right])
        )
        local_distance = float(
            np.linalg.norm(local_vectors[left] - local_vectors[right])
        )
        recomputed_distances.append(parent_distance)
        pairwise_ok &= math.isclose(
            parent_distance,
            float(row["parent_euclidean_distance"]),
            abs_tol=1e-12,
        ) and math.isclose(
            local_distance,
            float(row["local_child_euclidean_distance"]),
            abs_tol=1e-12,
        )
    add_check(
        checks,
        "six parent/local pairwise distances",
        pairwise_ok,
        f"minimum parent distance {min(recomputed_distances):.12f}",
    )

    with BOOTSTRAP_CSV.open(newline="", encoding="utf-8") as handle:
        bootstrap_rows = list(csv.DictReader(handle))
    add_check(
        checks,
        "bootstrap row count and indexes",
        len(bootstrap_rows) == len(STATE_ORDER) * REPS
        and {
            (row["state"], int(row["replicate"]))
            for row in bootstrap_rows
        }
        == {
            (state, repetition)
            for state in STATE_ORDER
            for repetition in range(REPS)
        },
        str(len(bootstrap_rows)),
    )

    saved_bootstrap = {
        (row["state"], int(row["replicate"])): row for row in bootstrap_rows
    }
    rng = np.random.default_rng(SEED)
    bootstrap_ok = True
    stability = {}
    for state in STATE_ORDER:
        correct = 0
        for repetition in range(REPS):
            p = {}
            for orientation in ORIENTATIONS:
                values = arrays[state][orientation]
                sample = rng.integers(0, len(values), size=len(values))
                p[orientation] = values[sample].mean(axis=0)
            exp = reconstruct(p)
            met = metrics(exp)
            closest, closest_mae, _, _, margin, _ = rank_parent(exp)
            correct += int(closest == state)
            saved = saved_bootstrap[(state, repetition)]
            bootstrap_ok &= (
                saved["closest_parent"] == closest
                and int(saved["correct_parent"]) == int(closest == state)
                and math.isclose(
                    float(saved["closest_mae"]), closest_mae, abs_tol=1e-12
                )
                and math.isclose(
                    float(saved["margin"]), margin, abs_tol=1e-12
                )
                and all(
                    math.isclose(
                        float(saved[name]), value, abs_tol=1e-12
                    )
                    for name, value in met.items()
                )
            )
        stability[state] = correct / REPS
    add_check(
        checks,
        "8000 bootstrap draws independently reproduced",
        bootstrap_ok,
        "all saved classifications and metrics",
    )
    add_check(
        checks,
        "bootstrap label stability",
        all(value >= 0.90 for value in stability.values())
        and all(
            math.isclose(
                value,
                results["states"][state]["bootstrap_label_stability"],
                abs_tol=1e-12,
            )
            for state, value in stability.items()
        ),
        json.dumps(stability, sort_keys=True),
    )

    observed_signs = {
        state: tuple(1 if exps[state][label] > 0 else -1 for label in SAME)
        for state in STATE_ORDER
    }
    expected_signs = {
        state: tuple(
            int(math.copysign(1, PATTERNS[state][label])) for label in SAME
        )
        for state in STATE_ORDER
    }
    cross_passes = [
        sum(rankings[state][0] == state for state in STATE_ORDER) == 4,
        observed_signs == expected_signs
        and len(set(observed_signs.values())) == 4,
        min(recomputed_distances) >= 1.0,
        min(stability.values()) >= 0.90,
        True,
    ]
    cross_ok = sum(cross_passes) == 5 and all(
        gate["pass"] for gate in results["cross_state_gates"].values()
    )
    add_check(
        checks,
        "five cross-state frozen gates independently recomputed",
        cross_ok,
        f"{sum(cross_passes)}/5",
    )

    assignments = []
    for permutation in itertools.permutations(STATE_ORDER):
        total = 0.0
        for state, target in zip(STATE_ORDER, permutation):
            target_vector = np.array(
                [PATTERNS[target][label] for label in SAME]
            )
            total += float(
                np.mean(np.abs(parent_vectors[state] - target_vector))
            )
        assignments.append((total / 4, permutation))
    assignments.sort()
    assignment_ok = assignments[0][1] == STATE_ORDER
    add_check(
        checks,
        "24-way parent-label assignment control",
        assignment_ok,
        (
            f"identity MAE {assignments[0][0]:.12f}; "
            f"runner-up {assignments[1][0]:.12f}"
        ),
    )

    verdict_ok = (
        results["verdict"] == "SUPPORTED"
        and results["gates_passed"] == 37
        and results["gates_total"] == 37
        and independently_passed + sum(cross_passes) == 37
    )
    add_check(
        checks,
        "overall verdict follows frozen gates",
        verdict_ok,
        f"{results['verdict']} {results['gates_passed']}/37",
    )

    all_passed = all(check["pass"] for check in checks)
    validation = {
        "status": "PASS" if all_passed else "FAIL",
        "checks_passed": sum(int(check["pass"]) for check in checks),
        "checks_total": len(checks),
        "checks": checks,
        "confidence": "Share with caveats" if all_passed else "Needs revision",
        "required_caveat": (
            "The four archives are prepared states from one device/deposit. "
            "The Bell/Pauli identities are established physics; Q5 tests the "
            "frozen ARA parent/child crosswalk, not a new quantum law."
        ),
    }
    VALIDATION_JSON.write_text(
        json.dumps(validation, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, indent=2, ensure_ascii=False))
    if not all_passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
