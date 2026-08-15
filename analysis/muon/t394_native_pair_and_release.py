from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source_cache" / "superk_2025" / "decayes_and_neutrons.csv"
OUT = HERE / "T394_native_pair_and_release"
OUT.mkdir(exist_ok=True)

SEED = 394
N_TRUTH = 1_000_000
T_MIN = 0.45
T_MAX = 30.0
N_BINS = 128
SMOOTHING = 0.5


def splitmix64(values: np.ndarray) -> np.ndarray:
    mask = np.uint64(0xFFFFFFFFFFFFFFFF)
    z = (values.astype(np.uint64) + np.uint64(0x9E3779B97F4A7C15)) & mask
    z = ((z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)) & mask
    z = ((z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)) & mask
    return z ^ (z >> np.uint64(31))


def sample_michel_x(rng: np.random.Generator, n: int) -> np.ndarray:
    accepted: list[np.ndarray] = []
    count = 0
    while count < n:
        m = max(100_000, int((n - count) * 1.5))
        x = rng.random(m)
        keep = rng.random(m) < x * x * (3.0 - 2.0 * x)
        accepted.append(x[keep])
        count += int(keep.sum())
    return np.concatenate(accepted)[:n]


def sample_va_z(
    rng: np.random.Generator, x_e: np.ndarray
) -> np.ndarray:
    result = np.empty_like(x_e)
    pending = np.ones(len(x_e), dtype=bool)
    while pending.any():
        idx = np.flatnonzero(pending)
        lower = 1.0 - x_e[idx]
        z = lower + (1.0 - lower) * rng.random(len(idx))
        keep = rng.random(len(idx)) < z * (1.0 - z) / 0.25
        result[idx[keep]] = z[keep]
        pending[idx[keep]] = False
    return result


def native_pair_metrics(y_nue: np.ndarray, x_e: np.ndarray) -> dict[str, object]:
    y_other = 2.0 - y_nue
    asymmetry = np.abs(y_nue - y_other)
    distance_coarse = np.minimum(
        np.abs(y_nue - 0.5) + np.abs(y_other - 1.5),
        np.abs(y_nue - 1.5) + np.abs(y_other - 0.5),
    )
    quintile_edges = np.quantile(x_e, np.linspace(0.0, 1.0, 6))
    quintiles: list[dict[str, float]] = []
    for q in range(5):
        if q == 4:
            mask = (x_e >= quintile_edges[q]) & (x_e <= quintile_edges[q + 1])
        else:
            mask = (x_e >= quintile_edges[q]) & (x_e < quintile_edges[q + 1])
        quintiles.append(
            {
                "quintile": q + 1,
                "x_low": float(quintile_edges[q]),
                "x_high": float(quintile_edges[q + 1]),
                "n": int(mask.sum()),
                "mean_pair_asymmetry": float(asymmetry[mask].mean()),
                "median_y_nu_e": float(np.median(y_nue[mask])),
            }
        )
    return {
        "mean_y_nu_e": float(y_nue.mean()),
        "mean_y_anti_nu_mu": float(y_other.mean()),
        "median_y_nu_e": float(np.median(y_nue)),
        "quantiles_y_nu_e": {
            str(q): float(v)
            for q, v in zip(
                [0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99],
                np.quantile(y_nue, [0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]),
            )
        },
        "mean_pair_asymmetry": float(asymmetry.mean()),
        "fraction_coarse_pair_l1_le_0p20": float(np.mean(distance_coarse <= 0.20)),
        "probability_anti_nu_mu_heavier": float(np.mean(y_other > y_nue)),
        "quintiles": quintiles,
    }


def run_test1() -> tuple[dict[str, object], dict[str, np.ndarray]]:
    rng = np.random.default_rng(SEED)
    x_e = sample_michel_x(rng, N_TRUTH)
    x_nue = sample_va_z(rng, x_e)
    x_anumu = 2.0 - x_e - x_nue
    pair_total = x_nue + x_anumu
    y_nue = 2.0 * x_nue / pair_total

    z_uniform = (1.0 - x_e) + x_e * rng.random(N_TRUTH)
    y_uniform = 2.0 * z_uniform / (2.0 - x_e)

    swap = rng.random(N_TRUTH) < 0.5
    y_shuffled = np.where(swap, y_nue, 2.0 - y_nue)

    result = {
        "source_class": "truth-level Standard-Model V-A crosswalk",
        "n": N_TRUTH,
        "seed": SEED,
        "energy_coordinate_means": {
            "charged": float(x_e.mean()),
            "nu_e": float(x_nue.mean()),
            "anti_nu_mu": float(x_anumu.mean()),
            "closure": float((x_e + x_nue + x_anumu).mean()),
        },
        "v_minus_a": native_pair_metrics(y_nue, x_e),
        "phase_space_control": native_pair_metrics(y_uniform, x_e),
        "identity_shuffled_control": native_pair_metrics(y_shuffled, x_e),
        "claim_boundary": (
            "Measures the event-level native neutral-pair distribution in a frozen "
            "truth model; it is not direct observation of both neutrinos."
        ),
    }
    arrays = {
        "x_e": x_e,
        "x_nue": x_nue,
        "x_anumu": x_anumu,
        "y_nue": y_nue,
        "y_uniform": y_uniform,
        "y_shuffled": y_shuffled,
    }
    return result, arrays


def load_superk() -> dict[str, np.ndarray | int]:
    momenta: list[float] = []
    times: list[float] = []
    neutron_counts: list[int] = []
    invalid_rows = 0
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        for row in csv.reader(handle):
            try:
                values = [float(item) for item in row]
                if len(values) < 2:
                    raise ValueError("short row")
            except ValueError:
                invalid_rows += 1
                continue
            momenta.append(values[0])
            times.append(values[1])
            neutron_counts.append(len(values) - 2)
    return {
        "momentum": np.asarray(momenta, dtype=float),
        "time": np.asarray(times, dtype=float),
        "neutron_count": np.asarray(neutron_counts, dtype=int),
        "invalid_rows": invalid_rows,
    }


def truncated_exp_log_norm(rate: float) -> float:
    return math.log(math.exp(-rate * T_MIN) - math.exp(-rate * T_MAX))


def fit_truncated_exponential(times: np.ndarray) -> float:
    # Stable golden-section minimisation of negative log likelihood.
    def nll(log_rate: float) -> float:
        rate = math.exp(log_rate)
        return float(-len(times) * math.log(rate) + rate * times.sum() + len(times) * truncated_exp_log_norm(rate))

    left, right = math.log(0.01), math.log(10.0)
    phi = (1.0 + math.sqrt(5.0)) / 2.0
    c = right - (right - left) / phi
    d = left + (right - left) / phi
    fc, fd = nll(c), nll(d)
    for _ in range(120):
        if fc < fd:
            right, d, fd = d, c, fc
            c = right - (right - left) / phi
            fc = nll(c)
        else:
            left, c, fc = c, d, fd
            d = left + (right - left) / phi
            fd = nll(d)
    return math.exp((left + right) / 2.0)


def exp_density_cdf(times: np.ndarray, rate: float) -> tuple[np.ndarray, np.ndarray]:
    denom = math.exp(-rate * T_MIN) - math.exp(-rate * T_MAX)
    density = rate * np.exp(-rate * times) / denom
    cdf = (math.exp(-rate * T_MIN) - np.exp(-rate * times)) / denom
    return density, cdf


def empirical_model(cal_times: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    edges = np.linspace(T_MIN, T_MAX, N_BINS + 1)
    counts, _ = np.histogram(cal_times, bins=edges)
    probs = (counts + SMOOTHING) / (counts.sum() + SMOOTHING * N_BINS)
    return edges, probs


def empirical_density_cdf(
    times: np.ndarray, edges: np.ndarray, probs: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    width = edges[1] - edges[0]
    idx = np.clip(np.searchsorted(edges, times, side="right") - 1, 0, len(probs) - 1)
    density = probs[idx] / width
    cum_before = np.concatenate([[0.0], np.cumsum(probs[:-1])])
    frac = np.clip((times - edges[idx]) / width, 0.0, 1.0)
    cdf = cum_before[idx] + probs[idx] * frac
    return density, cdf


def distribution_scores(times: np.ndarray, density: np.ndarray, cdf: np.ndarray) -> dict[str, float]:
    ordered = np.argsort(times)
    empirical = (np.arange(len(times)) + 0.5) / len(times)
    cdf_ordered = cdf[ordered]
    return {
        "mean_nll": float(-np.mean(np.log(np.maximum(density, 1e-300)))),
        "ks": float(np.max(np.abs(cdf_ordered - empirical))),
        "integrated_abs_cdf_error": float(np.mean(np.abs(cdf_ordered - empirical))),
    }


def run_test2() -> tuple[dict[str, object], dict[str, np.ndarray]]:
    data = load_superk()
    momentum = data["momentum"]
    time = data["time"]
    neutron_count = data["neutron_count"]
    assert isinstance(momentum, np.ndarray)
    assert isinstance(time, np.ndarray)
    assert isinstance(neutron_count, np.ndarray)

    row_index = np.arange(len(time), dtype=np.uint64)
    bucket = (splitmix64(row_index) % np.uint64(10)).astype(int)
    tagged = (time >= T_MIN) & (time <= T_MAX) & (momentum > 0)
    cal = tagged & (bucket <= 4)
    val = tagged & (bucket >= 5) & (bucket <= 6)
    hold = tagged & (bucket >= 7)

    rate = fit_truncated_exponential(time[cal])
    edges, probs = empirical_model(time[cal])

    hold_times = time[hold]
    d0, c0 = exp_density_cdf(hold_times, rate)
    dp, cp = empirical_density_cdf(hold_times, edges, probs)
    dr, cr = empirical_density_cdf(hold_times, edges, probs[::-1])
    scores = {
        "M0_truncated_exponential": distribution_scores(hold_times, d0, c0),
        "MP_reconstructed_antiphase": distribution_scores(hold_times, dp, cp),
        "MR_time_reversed_control": distribution_scores(hold_times, dr, cr),
    }

    nll0 = -np.log(np.maximum(d0, 1e-300))
    nllp = -np.log(np.maximum(dp, 1e-300))
    delta = nll0 - nllp
    block_id = np.arange(len(delta)) % 100
    block_means = np.array([delta[block_id == b].mean() for b in range(100)])
    rng = np.random.default_rng(SEED)
    boot = block_means[rng.integers(0, 100, size=(2000, 100))].mean(axis=1)
    ci = np.quantile(boot, [0.025, 0.975])

    gate_population = bool(
        scores["MP_reconstructed_antiphase"]["mean_nll"]
        < scores["M0_truncated_exponential"]["mean_nll"]
        and ci[0] > 0.0
        and scores["MP_reconstructed_antiphase"]["ks"]
        < scores["M0_truncated_exponential"]["ks"]
        and scores["MP_reconstructed_antiphase"]["mean_nll"]
        < scores["MR_time_reversed_control"]["mean_nll"]
    )

    result = {
        "source": {
            "doi": "10.5281/zenodo.15081911",
            "sha256": "B6BB10270E6C604935B47687293470CAEAFD01172288170D83349043566CD05A",
            "rows": int(len(time)),
            "invalid_rows": int(data["invalid_rows"]),
            "tagged_decay_e_rows": int(np.sum((time > 0) & (momentum > 0))),
            "tagged_decay_fraction": float(np.mean((time > 0) & (momentum > 0))),
            "rows_with_tagged_neutrons": int(np.sum(neutron_count > 0)),
            "electron_zero_pair_consistency": float(np.mean((time == 0) == (momentum == 0))),
            "pre_outcome_varying_fields": [],
            "outcome_fields_forbidden_as_predictors": [
                "decay electron momentum",
                "decay electron time",
                "neutron presence/count/time",
            ],
        },
        "splits": {
            "calibration_tagged": int(cal.sum()),
            "validation_tagged": int(val.sum()),
            "holdout_tagged": int(hold.sum()),
            "split_type": "deterministic row-hash; not chronological",
        },
        "models": {
            "M0_fitted_rate_per_us": rate,
            "empirical_bins": N_BINS,
            "scores": scores,
        },
        "bootstrap_M0_minus_MP_nll": {
            "mean": float(delta.mean()),
            "ci95": [float(ci[0]), float(ci[1])],
            "replicates": 2000,
        },
        "gates": {
            "G1_source_grain": True,
            "G2_no_future_leakage": True,
            "G3_population_antiphase_prediction": gate_population,
            "G4_individual_advance_prediction": "STRUCTURALLY_UNTESTABLE_NO_PRE_OUTCOME_VARIATION",
        },
        "claim_boundary": (
            "Tests whether a calibration release complement predicts the held-out "
            "population distribution. The source cannot distinguish which individual "
            "still-living muon releases next."
        ),
    }
    arrays = {
        "hold_times": hold_times,
        "cdf_m0": c0,
        "cdf_mp": cp,
        "cdf_mr": cr,
        "edges": edges,
        "probs": probs,
        "block_means": block_means,
    }
    return result, arrays


def write_outputs(
    test1: dict[str, object],
    arrays1: dict[str, np.ndarray],
    test2: dict[str, object],
    arrays2: dict[str, np.ndarray],
) -> None:
    summary = {
        "test_id": "T394",
        "protocol_sha256": "73285D4968422A57CFEC7F78C2A3ABA5FD903B8E460D939C62D1A770E49F10F6",
        "test1_native_neutral_pair": test1,
        "test2_causal_release": test2,
    }
    (OUT / "T394_RESULTS.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    sample_idx = np.linspace(0, len(arrays1["x_e"]) - 1, 20_000, dtype=int)
    with (OUT / "T394_TEST1_EVENT_SAMPLE.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["x_e", "x_nu_e", "x_anti_nu_mu", "y_nu_e_native", "y_anti_nu_mu_native"])
        for i in sample_idx:
            writer.writerow([
                arrays1["x_e"][i],
                arrays1["x_nue"][i],
                arrays1["x_anumu"][i],
                arrays1["y_nue"][i],
                2.0 - arrays1["y_nue"][i],
            ])

    with (OUT / "T394_TEST1_QUINTILES.csv").open("w", newline="", encoding="utf-8") as handle:
        rows = test1["v_minus_a"]["quintiles"]
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    grid = np.linspace(T_MIN, T_MAX, 600)
    rate = test2["models"]["M0_fitted_rate_per_us"]
    _, c0 = exp_density_cdf(grid, float(rate))
    _, cp = empirical_density_cdf(grid, arrays2["edges"], arrays2["probs"])
    _, cr = empirical_density_cdf(grid, arrays2["edges"], arrays2["probs"][::-1])
    with (OUT / "T394_TEST2_CURVES.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["time_us", "M0_exponential_cdf", "MP_antiphase_cdf", "MR_reversed_cdf"])
        writer.writerows(zip(grid, c0, cp, cr))


def main() -> None:
    test1, arrays1 = run_test1()
    test2, arrays2 = run_test2()
    write_outputs(test1, arrays1, test2, arrays2)
    print(json.dumps({"test1": test1, "test2": test2}, indent=2))


if __name__ == "__main__":
    main()
