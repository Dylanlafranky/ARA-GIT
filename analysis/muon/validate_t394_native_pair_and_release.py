from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
OUT = HERE / "T394_native_pair_and_release"
SOURCE = HERE / "source_cache" / "superk_2025" / "decayes_and_neutrons.csv"
RESULTS = OUT / "T394_RESULTS.json"
SAMPLE = OUT / "T394_TEST1_EVENT_SAMPLE.csv"
QUINTILES = OUT / "T394_TEST1_QUINTILES.csv"

T_MIN = 0.45
T_MAX = 30.0
EXPECTED_SOURCE_SHA256 = "B6BB10270E6C604935B47687293470CAEAFD01172288170D83349043566CD05A"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest().upper()


def splitmix64(values: np.ndarray) -> np.ndarray:
    mask = np.uint64(0xFFFFFFFFFFFFFFFF)
    z = (values.astype(np.uint64) + np.uint64(0x9E3779B97F4A7C15)) & mask
    z = ((z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)) & mask
    z = ((z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)) & mask
    return z ^ (z >> np.uint64(31))


def read_first_two_columns(path: Path) -> tuple[np.ndarray, np.ndarray, int]:
    momenta: list[float] = []
    times: list[float] = []
    invalid = 0
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.reader(handle):
            try:
                if len(row) < 2:
                    raise ValueError("short row")
                momenta.append(float(row[0]))
                times.append(float(row[1]))
            except ValueError:
                invalid += 1
    return np.asarray(momenta), np.asarray(times), invalid


def truncated_exp_nll(rate: float, times: np.ndarray) -> float:
    denom = math.exp(-rate * T_MIN) - math.exp(-rate * T_MAX)
    return float(-math.log(rate) + rate * times.mean() + math.log(denom))


def fit_rate(times: np.ndarray) -> float:
    # Independent bounded ternary minimisation in rate space.
    left, right = 0.01, 2.0
    for _ in range(160):
        third = (right - left) / 3.0
        c, d = left + third, right - third
        if truncated_exp_nll(c, times) < truncated_exp_nll(d, times):
            right = d
        else:
            left = c
    return (left + right) / 2.0


def exponential_score(rate: float, times: np.ndarray) -> tuple[float, float, np.ndarray]:
    denom = math.exp(-rate * T_MIN) - math.exp(-rate * T_MAX)
    density = rate * np.exp(-rate * times) / denom
    cdf = (math.exp(-rate * T_MIN) - np.exp(-rate * times)) / denom
    order = np.argsort(times)
    empirical = (np.arange(len(times)) + 0.5) / len(times)
    ks = float(np.max(np.abs(cdf[order] - empirical)))
    return float(-np.log(density).mean()), ks, cdf


def histogram_score(
    cal_times: np.ndarray,
    hold_times: np.ndarray,
    bins: int,
    smoothing: float = 0.5,
) -> tuple[float, float, np.ndarray, np.ndarray, np.ndarray]:
    edges = np.linspace(T_MIN, T_MAX, bins + 1)
    counts, _ = np.histogram(cal_times, bins=edges)
    probs = (counts + smoothing) / (counts.sum() + smoothing * bins)
    width = edges[1] - edges[0]
    idx = np.clip(np.searchsorted(edges, hold_times, side="right") - 1, 0, bins - 1)
    density = probs[idx] / width
    cumulative = np.concatenate([[0.0], np.cumsum(probs[:-1])])
    fraction = np.clip((hold_times - edges[idx]) / width, 0.0, 1.0)
    cdf = cumulative[idx] + probs[idx] * fraction
    order = np.argsort(hold_times)
    empirical = (np.arange(len(hold_times)) + 0.5) / len(hold_times)
    ks = float(np.max(np.abs(cdf[order] - empirical)))
    return float(-np.log(density).mean()), ks, density, cdf, probs


def bootstrap_delta(
    nll0_event: np.ndarray,
    nllp_event: np.ndarray,
    seed: int,
    reps: int = 1000,
) -> tuple[float, float, float]:
    delta = nll0_event - nllp_event
    block = np.arange(len(delta)) % 100
    means = np.asarray([delta[block == i].mean() for i in range(100)])
    rng = np.random.default_rng(seed)
    boot = means[rng.integers(0, 100, size=(reps, 100))].mean(axis=1)
    low, high = np.quantile(boot, [0.025, 0.975])
    return float(delta.mean()), float(low), float(high)


def empirical_cdf_on_grid(times: np.ndarray, grid: np.ndarray) -> np.ndarray:
    ordered = np.sort(times)
    return np.searchsorted(ordered, grid, side="right") / len(ordered)


def main() -> None:
    frozen = json.loads(RESULTS.read_text(encoding="utf-8"))

    sample = np.genfromtxt(SAMPLE, delimiter=",", names=True)
    sample_energy_closure = sample["x_e"] + sample["x_nu_e"] + sample["x_anti_nu_mu"]
    sample_pair_closure = sample["y_nu_e_native"] + sample["y_anti_nu_mu_native"]
    sample_checks = {
        "n": int(len(sample)),
        "max_abs_energy_closure_error": float(np.max(np.abs(sample_energy_closure - 2.0))),
        "max_abs_pair_closure_error": float(np.max(np.abs(sample_pair_closure - 2.0))),
        "sample_mean_y_nu_e": float(sample["y_nu_e_native"].mean()),
        "reported_full_mean_y_nu_e": float(
            frozen["test1_native_neutral_pair"]["v_minus_a"]["mean_y_nu_e"]
        ),
    }

    quintiles = np.genfromtxt(QUINTILES, delimiter=",", names=True)
    asymmetry = np.asarray(quintiles["mean_pair_asymmetry"], dtype=float)
    v_minus_a = frozen["test1_native_neutral_pair"]["v_minus_a"]
    phase_space = frozen["test1_native_neutral_pair"]["phase_space_control"]
    shuffled = frozen["test1_native_neutral_pair"]["identity_shuffled_control"]
    test1_checks = {
        "closure_pass": sample_checks["max_abs_energy_closure_error"] < 1e-12
        and sample_checks["max_abs_pair_closure_error"] < 1e-12,
        "sample_matches_full_mean_pass": abs(
            sample_checks["sample_mean_y_nu_e"] - sample_checks["reported_full_mean_y_nu_e"]
        ) < 0.02,
        "asymmetry_increases_by_charged_quintile": bool(np.all(np.diff(asymmetry) > 0)),
        "native_coarse_pair_fraction": float(v_minus_a["fraction_coarse_pair_l1_le_0p20"]),
        "phase_space_coarse_pair_fraction": float(
            phase_space["fraction_coarse_pair_l1_le_0p20"]
        ),
        "coarse_pair_not_enriched_vs_phase_space": bool(
            v_minus_a["fraction_coarse_pair_l1_le_0p20"]
            < phase_space["fraction_coarse_pair_l1_le_0p20"]
        ),
        "native_ordering_probability": float(v_minus_a["probability_anti_nu_mu_heavier"]),
        "shuffled_ordering_probability": float(shuffled["probability_anti_nu_mu_heavier"]),
        "direction_erased_by_label_shuffle": bool(
            abs(shuffled["probability_anti_nu_mu_heavier"] - 0.5) < 0.005
            and v_minus_a["probability_anti_nu_mu_heavier"] > 0.60
        ),
    }

    source_hash = sha256(SOURCE)
    momentum, time, invalid = read_first_two_columns(SOURCE)
    row_index = np.arange(len(time), dtype=np.uint64)
    bucket = (splitmix64(row_index) % np.uint64(10)).astype(int)
    tagged = (time >= T_MIN) & (time <= T_MAX) & (momentum > 0)
    cal = tagged & (bucket <= 4)
    hold = tagged & (bucket >= 7)
    cal_times = time[cal]
    hold_times = time[hold]

    rate = fit_rate(cal_times)
    nll0, ks0, cdf0_events = exponential_score(rate, hold_times)
    denom = math.exp(-rate * T_MIN) - math.exp(-rate * T_MAX)
    density0 = rate * np.exp(-rate * hold_times) / denom

    sensitivity: list[dict[str, float | int | bool]] = []
    selected: dict[str, object] | None = None
    for bins in [32, 64, 128, 256]:
        nllp, ksp, densityp, cdfp_events, probs = histogram_score(cal_times, hold_times, bins)
        delta, low, high = bootstrap_delta(
            -np.log(density0), -np.log(densityp), seed=1394 + bins
        )
        row: dict[str, float | int | bool] = {
            "bins": bins,
            "M0_mean_nll": nll0,
            "MP_mean_nll": nllp,
            "M0_minus_MP_nll": delta,
            "ci95_low": low,
            "ci95_high": high,
            "M0_ks": ks0,
            "MP_ks": ksp,
            "passes": bool(delta > 0 and low > 0 and ksp < ks0),
        }
        sensitivity.append(row)
        if bins == 128:
            selected = {
                "cdf_events": cdfp_events,
                "probs": probs,
                "row": row,
            }

    assert selected is not None
    grid = np.linspace(T_MIN, T_MAX, 600)
    cdf_observed = empirical_cdf_on_grid(hold_times, grid)
    cdf_m0 = (
        math.exp(-rate * T_MIN) - np.exp(-rate * grid)
    ) / denom
    edges = np.linspace(T_MIN, T_MAX, 129)
    probs = np.asarray(selected["probs"])
    width = edges[1] - edges[0]
    idx = np.clip(np.searchsorted(edges, grid, side="right") - 1, 0, len(probs) - 1)
    before = np.concatenate([[0.0], np.cumsum(probs[:-1])])
    fraction = np.clip((grid - edges[idx]) / width, 0.0, 1.0)
    cdf_mp = before[idx] + probs[idx] * fraction

    with (OUT / "T394_TEST2_HOLDOUT_CDF.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["time_us", "holdout_empirical_cdf", "M0_exponential_cdf", "MP_antiphase_cdf"])
        writer.writerows(zip(grid, cdf_observed, cdf_m0, cdf_mp))

    with (OUT / "T394_TEST2_SENSITIVITY.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(sensitivity[0]))
        writer.writeheader()
        writer.writerows(sensitivity)

    reported_test2 = frozen["test2_causal_release"]
    reported_scores = reported_test2["models"]["scores"]
    test2_checks = {
        "source_sha256": source_hash,
        "source_hash_pass": source_hash == EXPECTED_SOURCE_SHA256,
        "rows": int(len(time)),
        "invalid_rows": int(invalid),
        "calibration_tagged": int(cal.sum()),
        "holdout_tagged": int(hold.sum()),
        "independent_rate_per_us": rate,
        "reported_rate_per_us": float(reported_test2["models"]["M0_fitted_rate_per_us"]),
        "rate_reproduction_abs_error": abs(
            rate - float(reported_test2["models"]["M0_fitted_rate_per_us"])
        ),
        "reported_M0_mean_nll": float(reported_scores["M0_truncated_exponential"]["mean_nll"]),
        "independent_M0_mean_nll": nll0,
        "reported_MP_128_mean_nll": float(reported_scores["MP_reconstructed_antiphase"]["mean_nll"]),
        "independent_MP_128_mean_nll": float(selected["row"]["MP_mean_nll"]),
        "all_bin_sensitivities_pass": bool(all(row["passes"] for row in sensitivity)),
        "individual_prediction_status": reported_test2["gates"]["G4_individual_advance_prediction"],
        "no_pre_outcome_variation_confirmed": len(
            reported_test2["source"]["pre_outcome_varying_fields"]
        ) == 0,
    }

    validation = {
        "test_id": "T394-independent-validation",
        "test1_sample_checks": sample_checks,
        "test1_validation": test1_checks,
        "test2_validation": test2_checks,
        "test2_bin_sensitivity": sensitivity,
        "overall": {
            "test1_validated": bool(
                test1_checks["closure_pass"]
                and test1_checks["sample_matches_full_mean_pass"]
                and test1_checks["asymmetry_increases_by_charged_quintile"]
                and test1_checks["direction_erased_by_label_shuffle"]
            ),
            "test2_population_validation": bool(
                test2_checks["source_hash_pass"]
                and test2_checks["rate_reproduction_abs_error"] < 1e-8
                and test2_checks["all_bin_sensitivities_pass"]
            ),
            "test2_individual_prediction": "NOT_TESTABLE_IN_THIS_SOURCE",
        },
    }
    (OUT / "T394_VALIDATION.json").write_text(
        json.dumps(validation, indent=2), encoding="utf-8"
    )
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
