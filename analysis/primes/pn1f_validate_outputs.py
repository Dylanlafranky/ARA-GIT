"""Independent artifact-level checks for PN1F/DEV/v1.

This validator does not import the primary implementation. It recomputes the
saved probability, deformation, score-summary, and protected-target checks.
"""

from __future__ import annotations

import ast
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN1F_BIDIRECTIONAL_LANDSCAPE_DEVELOPMENT_PROTOCOL.md"
SCRIPT = HERE / "pn1f_bidirectional_landscape.py"
RESULTS = HERE / "PN1F_RESULTS.json"
MATRICES = HERE / "PN1F_BIDIRECTIONAL_MATRICES.npz"
RUNG = HERE / "PN1F_RUNG_METRICS.csv"
TRANSITION = HERE / "PN1F_TRANSITION_METRICS.csv"
MODES = HERE / "PN1F_DEFORMATION_MODE_SCORES.csv"
FOLDS = HERE / "PN1F_DOWNWARD_FOLD_SCORES.csv"
SUMMARY = HERE / "PN1F_DOWNWARD_MODEL_SUMMARY.csv"
UP_FIGURE = HERE / "PN1F_UPWARD_LANDSCAPE.png"
DOWN_FIGURE = HERE / "PN1F_DOWNWARD_DECOMPOSITION.png"
OUTPUT = HERE / "PN1F_VALIDATION.json"
PROTOCOL_SHA256 = "4ABCCB50E62780E41D9FF48455C1DC413926B9E5E527654E2B4F7108CAF004D7"
TOLERANCE = 1e-12


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def normalize(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    return values / values.sum()


def jsd_bits(first: np.ndarray, second: np.ndarray) -> float:
    p = normalize(first.ravel())
    q = normalize(second.ravel())
    midpoint = 0.5 * (p + q)
    active_p = p > 0
    active_q = q > 0
    return float(
        0.5 * np.sum(p[active_p] * np.log2(p[active_p] / midpoint[active_p]))
        + 0.5 * np.sum(q[active_q] * np.log2(q[active_q] / midpoint[active_q]))
    )


def cosine(first: np.ndarray, second: np.ndarray) -> float:
    return float(np.sum(first * second) / (np.linalg.norm(first) * np.linalg.norm(second)))


def parsed_open_primes() -> tuple[int, ...]:
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "ALL_OPEN_PRIMES":
                    value = ast.literal_eval(node.value)
                    return tuple(int(item) for item in value)
    raise AssertionError("ALL_OPEN_PRIMES not found")


def main() -> dict[str, object]:
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    rung = pd.read_csv(RUNG)
    transition = pd.read_csv(TRANSITION)
    modes = pd.read_csv(MODES)
    folds = pd.read_csv(FOLDS)
    summary = pd.read_csv(SUMMARY)
    arrays = np.load(MATRICES)
    open_primes = parsed_open_primes()

    checks: dict[str, bool] = {}
    checks["protocol_hash_matches"] = file_hash(PROTOCOL) == PROTOCOL_SHA256
    checks["result_protocol_hash_matches"] = results["protocol_sha256"] == PROTOCOL_SHA256
    checks["source_maximum_prime_is_23"] = max(open_primes) == 23
    checks["source_does_not_open_29"] = 29 not in open_primes
    checks["result_maximum_prime_is_23"] = results["maximum_generated_prime"] == 23
    checks["result_prime29_false"] = results["prime29_opened"] is False
    checks["core_primes_exact"] = np.array_equal(
        arrays["core_primes"], np.array([11, 13, 17, 19, 23])
    )

    for key in ("ordered_12", "gap_iid_12", "gap_markov1_12"):
        checks[f"{key}_normalizes"] = bool(
            np.allclose(arrays[key].sum(axis=(1, 2)), 1.0, atol=TOLERANCE)
        )
        checks[f"{key}_nonnegative"] = bool(np.all(arrays[key] >= 0))
    checks["residual_sums_zero"] = bool(
        np.allclose(arrays["markov_residual_12"].sum(axis=(1, 2)), 0.0, atol=TOLERANCE)
    )
    checks["residual_definition_exact"] = bool(
        np.allclose(
            arrays["markov_residual_12"],
            arrays["ordered_12"] - arrays["gap_markov1_12"],
            atol=TOLERANCE,
        )
    )
    checks["deformation_definition_exact"] = bool(
        np.allclose(
            arrays["deformation_12"],
            np.diff(arrays["markov_residual_12"], axis=0),
            atol=TOLERANCE,
        )
    )
    reconstructed = (
        arrays["deformation_mode_scores"] @ arrays["deformation_modes_12"].reshape(4, -1)
    ).reshape(arrays["deformation_12"].shape)
    checks["deformation_svd_reconstructs"] = bool(
        np.allclose(reconstructed, arrays["deformation_12"], atol=TOLERANCE)
    )
    checks["deformation_energy_sums_one"] = bool(
        math.isclose(float(arrays["deformation_energy_fractions"].sum()), 1.0, abs_tol=TOLERANCE)
    )

    core_rung = rung[rung["rung_prime"].isin([11, 13, 17, 19, 23])].reset_index(drop=True)
    jsd_recomputed = np.array(
        [
            jsd_bits(arrays["ordered_12"][index], arrays["gap_markov1_12"][index])
            for index in range(5)
        ]
    )
    checks["rung_markov_jsd_recomputes"] = bool(
        np.allclose(
            jsd_recomputed,
            core_rung["ordered_vs_gap_markov1_jsd_bits"].to_numpy(),
            atol=TOLERANCE,
        )
    )
    deformation = arrays["deformation_12"]
    adjacent_cosines = np.array(
        [cosine(deformation[index], deformation[index + 1]) for index in range(3)]
    )
    checks["transition_cosines_recompute"] = bool(
        np.allclose(
            adjacent_cosines,
            transition["cosine_with_previous_deformation"].dropna().to_numpy(),
            atol=TOLERANCE,
        )
    )
    checks["mode_scores_table_matches"] = bool(
        np.allclose(
            modes.pivot(index="transition", columns="mode", values="score")
            .loc[["11->13", "13->17", "17->19", "19->23"]]
            .to_numpy(),
            arrays["deformation_mode_scores"],
            atol=TOLERANCE,
        )
    )

    fold_means = folds.groupby("model", sort=False)["cross_entropy_bits"].mean()
    saved_means = summary.set_index("model")["mean_cross_entropy_bits"]
    checks["downward_fold_means_recompute"] = bool(
        np.allclose(fold_means.loc[saved_means.index], saved_means, atol=TOLERANCE)
    )
    base = float(saved_means.loc["current_B"])
    gains = base - saved_means
    checks["downward_gains_recompute"] = bool(
        np.allclose(
            gains.loc[summary["model"]].to_numpy(),
            summary["gain_vs_current_B_bits"].to_numpy(),
            atol=TOLERANCE,
        )
    )
    checks["all_decompressed_models_win_every_fold"] = bool(
        np.all(summary["min_fold_gain_vs_current_B_bits"] >= -TOLERANCE)
    )
    checks["full_pair_reconciles_pn1e"] = abs(
        float(saved_means.loc["full_A_B"]) - 2.0823
    ) < 0.001
    checks["p23_base_reconciles_pn1e"] = abs(base - 2.5565) < 0.001

    with Image.open(UP_FIGURE) as upward:
        checks["upward_figure_dimensions"] = upward.size == (2400, 1500)
    with Image.open(DOWN_FIGURE) as downward:
        checks["downward_figure_dimensions"] = downward.size == (1950, 900)

    high_residual = arrays["markov_residual_24"]
    high_deformation = np.diff(high_residual, axis=0)
    high_residual_cosines = [
        cosine(high_residual[index], high_residual[index + 1]) for index in range(3)
    ]
    high_deformation_cosines = [
        cosine(high_deformation[index], high_deformation[index + 1]) for index in range(2)
    ]
    singular_values = np.linalg.svd(high_deformation.reshape(3, -1), compute_uv=False)
    high_energy = singular_values**2 / np.sum(singular_values**2)
    checks["high_resolution_shape_persists"] = min(high_residual_cosines) > 0.99
    checks["high_resolution_deformation_direction_persists"] = min(high_deformation_cosines) > 0.98
    checks["high_resolution_first_mode_dominates"] = float(high_energy[0]) > 0.95

    validation = {
        "validation_id": "PN1F/DEV/v1-independent-artifact-validation",
        "all_checks_pass": all(checks.values()),
        "checks": checks,
        "recomputed": {
            "core_markov_jsd_bits": jsd_recomputed.tolist(),
            "adjacent_deformation_cosines_12": adjacent_cosines.tolist(),
            "adjacent_residual_cosines_24": high_residual_cosines,
            "adjacent_deformation_cosines_24": high_deformation_cosines,
            "deformation_energy_fractions_24": high_energy.tolist(),
            "downward_cross_entropy_bits": {
                key: float(value) for key, value in saved_means.items()
            },
        },
        "artifact_hashes": {
            path.name: file_hash(path)
            for path in (
                PROTOCOL,
                SCRIPT,
                RESULTS,
                MATRICES,
                RUNG,
                TRANSITION,
                MODES,
                FOLDS,
                SUMMARY,
                UP_FIGURE,
                DOWN_FIGURE,
            )
        },
    }
    OUTPUT.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, indent=2))
    if not validation["all_checks_pass"]:
        failed = [name for name, passed in checks.items() if not passed]
        raise SystemExit(f"PN1F validation failed: {failed}")
    return validation


if __name__ == "__main__":
    main()
