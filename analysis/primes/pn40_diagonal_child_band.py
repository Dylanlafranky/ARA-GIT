"""PN40: quantify the diagonal crest family marked in the PN39 raster."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "PN39_INDIVIDUAL_PRIME_CHILD_RASTER.json"
OUTPUT = HERE / "PN40_DIAGONAL_CHILD_BAND_RESULTS.json"

DISPLAY_BINS = 80
DEVELOPMENT_N = 256
MIN_SLOPE = 0.0200
MAX_SLOPE = 0.1000
SLOPE_STEP = 0.0005
MIN_SEPARATION = 12
SHUFFLES = 2000
SEED = 4_000_000_007


def standardize_rows(matrix: np.ndarray) -> np.ndarray:
    residual = matrix - matrix.mean(axis=1, keepdims=True)
    scale = np.sqrt(np.mean(residual * residual, axis=1, keepdims=True))
    return residual / scale


def circular_distance(a: float, b: float, period: int = DISPLAY_BINS) -> float:
    direct = abs(a - b)
    return min(direct, period - direct)


def interpolate(field: np.ndarray, phase: np.ndarray) -> np.ndarray:
    lower_float = np.floor(phase)
    lower = lower_float.astype(np.int64) % field.shape[1]
    upper = (lower + 1) % field.shape[1]
    fraction = phase - lower_float
    rows = np.arange(field.shape[0], dtype=np.int64)[:, None]
    return (1.0 - fraction) * field[rows, lower] + fraction * field[rows, upper]


def all_intercept_scores(field: np.ndarray, slope: float, global_start: int = 0) -> np.ndarray:
    x = (global_start + np.arange(field.shape[0], dtype=np.float64))[:, None]
    intercepts = np.arange(field.shape[1], dtype=np.float64)[None, :]
    phase = intercepts + slope * x
    samples = (
        0.25 * interpolate(field, phase - 1.0)
        + 0.50 * interpolate(field, phase)
        + 0.25 * interpolate(field, phase + 1.0)
    )
    return samples.mean(axis=0)


def choose_three(scores: np.ndarray) -> tuple[list[int], float]:
    chosen: list[int] = []
    for candidate in np.argsort(scores)[::-1]:
        value = int(candidate)
        if all(circular_distance(value, existing) >= MIN_SEPARATION for existing in chosen):
            chosen.append(value)
        if len(chosen) == 3:
            break
    if len(chosen) != 3:
        raise AssertionError("could not select three separated crests")
    return chosen, float(np.mean(scores[chosen]))


def score_template(
    field: np.ndarray,
    slope: float,
    intercepts: list[float] | np.ndarray,
    global_start: int,
) -> tuple[list[float], float]:
    x = (global_start + np.arange(field.shape[0], dtype=np.float64))[:, None]
    phase = np.asarray(intercepts, dtype=np.float64)[None, :] + slope * x
    samples = (
        0.25 * interpolate(field, phase - 1.0)
        + 0.50 * interpolate(field, phase)
        + 0.25 * interpolate(field, phase + 1.0)
    )
    scores = samples.mean(axis=0)
    return [float(value) for value in scores], float(np.mean(scores))


def percentile(value: float, null: np.ndarray) -> float:
    return float(100.0 * (np.count_nonzero(null <= value) + 0.5) / (null.size + 1.0))


def search(field: np.ndarray, global_start: int = 0) -> dict[str, object]:
    slopes = np.arange(MIN_SLOPE, MAX_SLOPE + SLOPE_STEP / 2.0, SLOPE_STEP)
    best: dict[str, object] | None = None
    for slope in slopes:
        scores = all_intercept_scores(field, float(slope), global_start)
        intercepts, joint_score = choose_three(scores)
        if best is None or joint_score > float(best["score"]):
            best = {
                "slope_bins_per_prime": float(slope),
                "intercepts_bins_at_global_zero": intercepts,
                "individual_scores": [float(scores[index]) for index in intercepts],
                "score": joint_score,
            }
    if best is None:
        raise AssertionError("empty slope search")
    return best


def main() -> None:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    original = np.asarray(payload["histogram_rows"], dtype=np.float64)
    if original.shape != (512, 160):
        raise AssertionError(f"unexpected PN39 shape: {original.shape}")

    displayed = original.reshape(original.shape[0], DISPLAY_BINS, 2).sum(axis=2)
    field = standardize_rows(displayed)
    development = field[:DEVELOPMENT_N]
    transfer = field[DEVELOPMENT_N:]
    primes = np.asarray(payload["prime_values"], dtype=np.int64)

    fitted = search(development, global_start=0)
    slope = float(fitted["slope_bins_per_prime"])
    intercepts = [float(value) for value in fitted["intercepts_bins_at_global_zero"]]

    transfer_individual, transfer_score = score_template(
        transfer, slope, intercepts, global_start=DEVELOPMENT_N
    )

    offset_grid = np.linspace(0.0, DISPLAY_BINS, 800, endpoint=False)
    offset_null = np.asarray([
        score_template(transfer, slope, np.asarray(intercepts) + offset, DEVELOPMENT_N)[1]
        for offset in offset_grid
    ])

    rng = np.random.default_rng(SEED)
    shuffled_null = np.empty(SHUFFLES, dtype=np.float64)
    for index in range(SHUFFLES):
        shuffled = transfer[rng.permutation(transfer.shape[0])]
        shuffled_null[index] = score_template(
            shuffled, slope, intercepts, global_start=DEVELOPMENT_N
        )[1]

    transfer_refit = search(transfer, global_start=DEVELOPMENT_N)

    # Secondary descriptive readout tied directly to Dylan's drawn ~5 degree line.
    # This is deliberately kept outside the frozen primary result.
    five_degree_slope = math.tan(math.radians(5.0)) * (684.0 / DEVELOPMENT_N) / (
        348.0 / DISPLAY_BINS
    )
    five_degree_scores = all_intercept_scores(development, five_degree_slope, 0)
    five_degree_intercepts, five_degree_development_score = choose_three(five_degree_scores)
    _, five_degree_transfer_score = score_template(
        transfer, five_degree_slope, five_degree_intercepts, DEVELOPMENT_N
    )
    quarter_refits = [
        {
            "prime_indices": [start, start + 127],
            **search(field[start : start + 128], global_start=start),
        }
        for start in (0, 128, 256, 384)
    ]

    intercept_ara = [2.0 * value / DISPLAY_BINS for value in intercepts]
    ordered = sorted(intercepts)
    separations_bins = [
        ordered[1] - ordered[0],
        ordered[2] - ordered[1],
        ordered[0] + DISPLAY_BINS - ordered[2],
    ]
    slope_ara = slope * 2.0 / DISPLAY_BINS
    screen_x_per_prime = 684.0 / DEVELOPMENT_N
    screen_y_per_bin = 348.0 / DISPLAY_BINS
    screen_angle = math.degrees(math.atan(slope * screen_y_per_bin / screen_x_per_prime))

    mean_gap_development = float(np.mean(np.diff(primes[:DEVELOPMENT_N])))
    mean_gap_transfer = float(np.mean(np.diff(primes[DEVELOPMENT_N:])))
    equivalent_q_development = float(2.0 * mean_gap_development / slope_ara)
    equivalent_q_transfer = float(2.0 * mean_gap_transfer / slope_ara)

    result = {
        "test": "PN40 diagonal child-band test",
        "status": "post-hoc development plus same-file fixed-continuation transfer",
        "source": SOURCE.name,
        "fixed_representation": {
            "display_bins": DISPLAY_BINS,
            "bin_width_ara": 2.0 / DISPLAY_BINS,
            "row_standardization": "subtract row mean; divide by row RMS residual",
            "circular_vertical_axis": True,
            "band_kernel": {"offset_bins": [-1, 0, 1], "weights": [0.25, 0.5, 0.25]},
        },
        "development": {
            "prime_indices": [0, 255],
            "first_prime": int(primes[0]),
            "last_prime": int(primes[255]),
            **fitted,
            "intercepts_ara_at_global_zero": intercept_ara,
            "circular_separations_bins": separations_bins,
            "circular_separations_ara": [2.0 * value / DISPLAY_BINS for value in separations_bins],
        },
        "native_slope": {
            "ara_per_prime_occurrence": slope_ara,
            "ara_change_across_256_occurrences": slope_ara * DEVELOPMENT_N,
            "approximate_existing_chart_angle_degrees": screen_angle,
            "angle_note": "chart angle depends on plot aspect ratio; native ARA slope does not",
        },
        "transfer": {
            "prime_indices": [256, 511],
            "first_prime": int(primes[256]),
            "last_prime": int(primes[511]),
            "fixed_individual_scores": transfer_individual,
            "fixed_joint_score": transfer_score,
            "common_circular_offset_null": {
                "count": int(offset_null.size),
                "mean": float(np.mean(offset_null)),
                "standard_deviation": float(np.std(offset_null)),
                "percentile": percentile(transfer_score, offset_null),
            },
            "prime_order_shuffle_null": {
                "count": SHUFFLES,
                "seed": SEED,
                "mean": float(np.mean(shuffled_null)),
                "standard_deviation": float(np.std(shuffled_null)),
                "percentile": percentile(transfer_score, shuffled_null),
            },
            "independent_refit": transfer_refit,
        },
        "post_hoc_exploratory_readouts": {
            "user_drawn_five_degree_template": {
                "slope_bins_per_prime": five_degree_slope,
                "slope_ara_per_prime": five_degree_slope * 2.0 / DISPLAY_BINS,
                "development_intercepts_bins": five_degree_intercepts,
                "development_score": five_degree_development_score,
                "fixed_transfer_score": five_degree_transfer_score,
            },
            "independent_128_prime_window_refits": quarter_refits,
            "warning": "These readouts were added after the frozen PN40 primary run and are descriptive only.",
        },
        "arithmetic_crosswalk": {
            "mean_prime_gap_development": mean_gap_development,
            "mean_prime_gap_transfer": mean_gap_transfer,
            "equivalent_gate_q_development": equivalent_q_development,
            "equivalent_gate_q_transfer": equivalent_q_transfer,
            "identity": "A_q(p_next) = A_q(p) + 2*(p_next-p)/q (mod 2)",
        },
        "interpretation_limits": [
            "The first half is opened post-hoc development data.",
            "The second half is a fixed continuation in the same pre-existing window, not a new blind interval.",
            "A stable band is a structural feature of the raw child ARA field, not by itself a prime predictor.",
            "The approximate five-degree screen angle is not invariant to chart dimensions.",
        ],
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
