"""Independent validation for PN1 output artifacts."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageStat


HERE = Path(__file__).resolve().parent
EXPECTED_PROTOCOL_HASH = "EE14829EEA0D2BAAE05C37FAE2AA558F015EFC649FBFA54F0A563A7CE277DF9D"
SEED = 20260717
N_SHUFFLES = 200


def hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def entropy_bits(values: np.ndarray) -> float:
    positive = values[values > 0]
    return float(-np.sum(positive * np.log2(positive)))


def js_entropy_form(left: np.ndarray, right: np.ndarray) -> float:
    left = left / left.sum()
    right = right / right.sum()
    midpoint = 0.5 * (left + right)
    return entropy_bits(midpoint) - 0.5 * entropy_bits(left) - 0.5 * entropy_bits(right)


def incremental_wheels() -> dict[int, tuple[int, np.ndarray, np.ndarray]]:
    wheels: dict[int, tuple[int, np.ndarray, np.ndarray]] = {}
    period = 1
    residues = np.array([0], dtype=np.int64)
    for prime in (2, 3, 5, 7, 11, 13, 17, 19):
        lifts = residues[:, None] + period * np.arange(prime, dtype=np.int64)[None, :]
        period *= prime
        residues = np.sort(lifts.ravel()[np.mod(lifts.ravel(), prime) != 0])
        if prime == 2:
            # The seed residue zero lifts to {0,1}; after excluding zero, residue 1 remains.
            assert np.array_equal(residues, np.array([1], dtype=np.int64))
        gaps = np.diff(np.concatenate((residues, residues[:1] + period))).astype(np.int32)
        wheels[prime] = (period, residues, gaps)
    return wheels


def coordinate(gaps: np.ndarray) -> np.ndarray:
    gaps_float = gaps.astype(np.float64)
    return 2.0 * np.roll(gaps_float, -1) / (gaps_float + np.roll(gaps_float, -1))


def histogram(gaps: np.ndarray, bins: int, triple: bool) -> np.ndarray:
    first = coordinate(gaps)
    edges = np.linspace(0.0, 2.0, bins + 1)
    if not triple:
        counts = np.histogram(first, bins=edges)[0].astype(np.float64)
    else:
        counts = np.histogram2d(first, np.roll(first, -1), bins=(edges, edges))[0].ravel()
    return counts / counts.sum()


def validate() -> dict[str, object]:
    results = json.loads((HERE / "PN1_SIEVE_RUNG_RESULTS.json").read_text(encoding="utf-8"))
    primary = pd.read_csv(HERE / "PN1_PRIMARY_DISTANCES.csv")
    calibration = pd.read_csv(HERE / "PN1_CALIBRATION_CHECKS.csv")
    sensitivity = pd.read_csv(HERE / "PN1_BIN_SENSITIVITY.csv")
    split_half = pd.read_csv(HERE / "PN1_SPLIT_HALF_CHECKS.csv")
    saved = np.load(HERE / "PN1_HISTOGRAMS_AND_NULLS.npz")
    wheels = incremental_wheels()

    checks: dict[str, bool] = {}
    checks["protocol_hash_matches"] = hash_file(
        HERE / "PN1_SIEVE_RUNG_PROTOCOL_v1_FROZEN.md"
    ) == EXPECTED_PROTOCOL_HASH
    checks["json_hash_matches"] = (
        results["protocol_sha256_observed"] == EXPECTED_PROTOCOL_HASH
    )
    checks["four_primary_rows"] = len(primary) == 4
    checks["primary_csv_all_pass"] = bool(primary["passes_frozen_primary"].all())
    checks["summary_matches_csv"] = (
        int(primary["passes_frozen_primary"].sum())
        == results["summary"]["primary_comparisons_passed"]
        == 4
    )
    checks["all_calibration_rows_pass"] = bool(calibration["all_exact_checks_pass"].all())
    checks["all_split_half_rows_pass"] = bool(split_half["passes_same_direction"].all())
    checks["sensitivity_all_directional"] = bool(
        (sensitivity["ordered_jsd_bits"] < sensitivity["shuffle_median_jsd_bits"]).all()
    )

    regenerated_matches: list[bool] = []
    shuffled_matches: list[bool] = []
    for transition_index, (parent_prime, child_prime) in enumerate(((13, 17), (17, 19))):
        parent_gaps = wheels[parent_prime][2]
        child_gaps = wheels[child_prime][2]
        for observable, bins, triple in (("pair_x", 64, False), ("triple_xx", 24, True)):
            parent_hist = histogram(parent_gaps, bins, triple)
            child_hist = histogram(child_gaps, bins, triple)
            observed = js_entropy_form(parent_hist, child_hist)
            row = primary[
                (primary["transition"] == f"{parent_prime}->{child_prime}")
                & (primary["observable"] == observable)
            ].iloc[0]
            regenerated_matches.append(
                math.isclose(observed, row["ordered_jsd_bits"], rel_tol=0.0, abs_tol=1e-13)
            )

        rng = np.random.default_rng(SEED + transition_index * 10000)
        pair_distances = np.empty(N_SHUFFLES)
        triple_distances = np.empty(N_SHUFFLES)
        child_pair = histogram(child_gaps, 64, False)
        child_triple = histogram(child_gaps, 24, True)
        for index in range(N_SHUFFLES):
            shuffled = rng.permutation(parent_gaps)
            pair_distances[index] = js_entropy_form(histogram(shuffled, 64, False), child_pair)
            triple_distances[index] = js_entropy_form(histogram(shuffled, 24, True), child_triple)
        shuffled_matches.append(
            np.allclose(
                pair_distances,
                saved[f"{parent_prime}_{child_prime}_pair_shuffle_distances"],
                atol=1e-13,
                rtol=0.0,
            )
        )
        shuffled_matches.append(
            np.allclose(
                triple_distances,
                saved[f"{parent_prime}_{child_prime}_triple_shuffle_distances"],
                atol=1e-13,
                rtol=0.0,
            )
        )

    checks["independent_incremental_wheels_match_ordered_jsd"] = all(regenerated_matches)
    checks["independent_shuffle_replay_matches_saved_nulls"] = all(shuffled_matches)
    checks["log_ratio_is_exact_coordinate_rival"] = bool(
        primary["coordinate_rival_abs_difference"].dropna().max() <= 1e-15
    )

    figure_path = HERE / "PN1_SIEVE_RUNG_FIGURE.png"
    with Image.open(figure_path) as figure:
        stats = ImageStat.Stat(figure.convert("L"))
        checks["figure_dimensions_expected"] = figure.size == (1800, 760)
        checks["figure_not_blank"] = stats.var[0] > 100.0

    ready = all(checks.values())
    validation = {
        "test_id": "T227 / PN1/v1",
        "assessment": "Ready to share" if ready else "Needs revision",
        "checks": checks,
        "all_checks_pass": ready,
        "primary_rating": results["summary"]["rating"],
        "required_caveats": [
            "The two held-out transitions are sequential and not independent replications.",
            "The exact sieve checks are reconstruction/calibration, not new evidence.",
            "The bounded x coordinate and matched log-gap-ratio are equivalent representations.",
            "No Riemann-Hypothesis or physical-universality inference is licensed.",
        ],
    }
    (HERE / "PN1_VALIDATION.json").write_text(
        json.dumps(validation, indent=2), encoding="utf-8"
    )
    print(json.dumps(validation, indent=2))
    return validation


if __name__ == "__main__":
    validate()

