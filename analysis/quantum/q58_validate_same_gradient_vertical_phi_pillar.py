"""Independent validator for Q58 frozen same-gradient Phi-pillar test."""

from __future__ import annotations

import hashlib
import json
import math
import pathlib
import warnings

import numpy as np
import pandas as pd


HERE = pathlib.Path(__file__).resolve().parent
PROTOCOL = HERE / "Q58_SAME_GRADIENT_VERTICAL_PHI_PILLAR_PROTOCOL_v1_FROZEN.md"
RESULTS = HERE / "Q58_SAME_GRADIENT_VERTICAL_PHI_PILLAR_RESULTS.json"
CROSSINGS = HERE / "Q58_SAME_GRADIENT_VERTICAL_PHI_PILLAR_CROSSINGS.csv.gz"
PAIR_PROFILES = HERE / "Q58_SAME_GRADIENT_VERTICAL_PHI_PILLAR_PAIR_PROFILES.csv.gz"
SEED_RATIOS = HERE / "Q58_SAME_GRADIENT_VERTICAL_PHI_PILLAR_SEED_RATIOS.csv"
GRID_SUMMARY = HERE / "Q58_SAME_GRADIENT_VERTICAL_PHI_PILLAR_GRID_SUMMARY.csv"
OUTPUT = HERE / "Q58_SAME_GRADIENT_VERTICAL_PHI_PILLAR_VALIDATION.json"

DATASETS = {
    "greedy": {
        "derived": HERE / "public_data" / "q40_return_flow_inhomo_v1_greedy" / "q40_derived_cache.npz",
        "connected": HERE / "public_data" / "q40_return_flow_inhomo_v1_greedy" / "q40_connected_cache.npy",
    },
    "landmax": {
        "derived": HERE / "public_data" / "q41b_cadence_strand_inhomo_v1_landmax" / "q41b_derived_cache.npz",
        "connected": HERE / "public_data" / "q41b_cadence_strand_inhomo_v1_landmax" / "q41b_connected_cache.npy",
    },
}

GRID = np.round(np.arange(0.2, 2.0, 0.2), 10)
PHI = (1 + math.sqrt(5)) / 2
LANDMARKS = {"1": 1.0, "sqrt2": math.sqrt(2), "1.5": 1.5, "phi": PHI, "sqrt3": math.sqrt(3), "2": 2.0}
TOLERANCE = 0.08
EPS = 1e-12
BOOTSTRAP_DRAWS = 10_000
PERMUTATION_DRAWS = 9_999
RANDOM_SEED = 580031


def sha256(path: pathlib.Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def independent_interp(x: np.ndarray, y: np.ndarray, target: float) -> float:
    order = np.argsort(x, kind="mergesort")
    x, y = np.asarray(x)[order], np.asarray(y)[order]
    unique = np.unique(x)
    collapsed = np.asarray([np.median(y[x == value]) for value in unique])
    if target < unique[0] - 1e-12 or target > unique[-1] + 1e-12:
        return float("nan")
    return float(np.interp(target, unique, collapsed))


def bootstrap_interval(values: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    values = np.asarray(values, dtype=np.float64)
    values = values[np.isfinite(values)]
    medians = np.empty(BOOTSTRAP_DRAWS)
    for start in range(0, BOOTSTRAP_DRAWS, 500):
        stop = min(start + 500, BOOTSTRAP_DRAWS)
        draw = rng.integers(0, len(values), size=(stop - start, len(values)))
        medians[start:stop] = np.median(values[draw], axis=1)
    return tuple(float(value) for value in np.quantile(medians, [0.025, 0.975]))


def validate_crossing_sample(crossings: pd.DataFrame) -> dict:
    indices = np.unique(np.linspace(0, len(crossings) - 1, 256, dtype=int))
    sampled = crossings.iloc[indices]
    max_fro_error = 0.0
    max_spec_error = 0.0
    outside = 0
    caches = {}
    for archive in sampled["archive"].unique():
        derived = np.load(DATASETS[archive]["derived"])
        caches[archive] = (
            np.asarray(derived["closure"], dtype=np.float64),
            np.load(DATASETS[archive]["connected"], mmap_mode="r"),
        )
    for row in sampled.itertuples(index=False):
        closure, connected = caches[row.archive]
        line = closure[int(row.seed), :, int(row.pair)]
        lo, hi = np.quantile(line[:250], [0.05, 0.95])
        x = 2 * (line - lo) / (hi - lo)
        start, end = int(row.run_start), int(row.run_end)
        x_run = x[start:end + 1]
        matrices = np.asarray(connected[int(row.seed), start:end + 1, int(row.pair)], dtype=np.float64)
        fro = np.linalg.norm(matrices, axis=(1, 2))
        spec = np.linalg.svd(matrices, compute_uv=False)[:, 0]
        if row.ara_x < np.min(x_run) - 1e-12 or row.ara_x > np.max(x_run) + 1e-12:
            outside += 1
            continue
        expected_fro = independent_interp(x_run, fro, float(row.ara_x))
        expected_spec = independent_interp(x_run, spec, float(row.ara_x))
        max_fro_error = max(max_fro_error, abs(expected_fro - float(row.frobenius)))
        max_spec_error = max(max_spec_error, abs(expected_spec - float(row.spectral)))
    return {
        "sampled_rows": int(len(sampled)),
        "outside_run_coordinate_range": outside,
        "max_frobenius_interpolation_error": max_fro_error,
        "max_spectral_interpolation_error": max_spec_error,
    }


def reproduce_permutation(pair_rows: pd.DataFrame, seed_ratios: pd.DataFrame) -> dict:
    rng = np.random.default_rng(RANDOM_SEED + 2)
    columns = [(phase, float(x)) for phase in ("A", "B") for x in GRID]
    output = {}
    for archive in sorted(pair_rows["archive"].unique()):
        observed = seed_ratios.loc[seed_ratios.archive == archive, "ratio_frobenius"].to_numpy()
        observed_error = float(np.mean(np.abs(observed - PHI)))
        sums = np.zeros(PERMUTATION_DRAWS)
        counts = np.zeros(PERMUTATION_DRAWS, dtype=np.int64)
        used = 0
        selected_archive = pair_rows[pair_rows.archive == archive]
        for seed, frame in selected_archive.groupby("seed", sort=True):
            pairs = np.sort(frame["pair"].unique())
            labels = frame.drop_duplicates("pair").set_index("pair").loc[pairs, "family"].to_numpy()
            n_parent = int(np.sum(labels == "one_turn_15"))
            n_child = int(np.sum(labels == "two_turn_7_5"))
            if n_parent == 0 or n_child == 0:
                continue
            pivot = frame.pivot_table(index="pair", columns=["phase", "ara_x"], values="frobenius", aggfunc="first")
            pivot = pivot.reindex(index=pairs, columns=pd.MultiIndex.from_tuples(columns))
            values = pivot.to_numpy(dtype=np.float64)
            used += 1
            for start in range(0, PERMUTATION_DRAWS, 128):
                stop = min(start + 128, PERMUTATION_DRAWS)
                order = np.argsort(rng.random((stop - start, len(pairs))), axis=1)
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", RuntimeWarning)
                    parent = np.nanmedian(values[order[:, :n_parent], :], axis=1)
                    child = np.nanmedian(values[order[:, n_parent:n_parent + n_child], :], axis=1)
                ratio = parent / child
                valid = np.isfinite(ratio) & (child > EPS)
                sums[start:stop] += np.sum(np.where(valid, np.abs(ratio - PHI), 0), axis=1)
                counts[start:stop] += np.sum(valid, axis=1)
        null = sums / np.maximum(counts, 1)
        output[archive] = {
            "used_seeds": used,
            "observed_mean_abs_phi_error": observed_error,
            "null_median_mean_abs_phi_error": float(np.median(null)),
            "null_ci95": [float(value) for value in np.quantile(null, [0.025, 0.975])],
            "p_observed_no_worse_than_null": float((1 + np.sum(null <= observed_error)) / (PERMUTATION_DRAWS + 1)),
        }
    return output


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    seed = pd.read_csv(SEED_RATIOS)
    published_grid = pd.read_csv(GRID_SUMMARY)
    crossings = pd.read_csv(CROSSINGS)
    pairs = pd.read_csv(PAIR_PROFILES)
    rng = np.random.default_rng(RANDOM_SEED)

    protocol_match = sha256(PROTOCOL) == result["protocol_sha256"]
    max_grid_error = 0.0
    max_ci_error = 0.0
    max_control_error = 0.0
    recomputed_rows = []
    for archive in sorted(seed.archive.unique()):
        for phase in ("A", "B"):
            for grid_x in GRID:
                values = seed[(seed.archive == archive) & (seed.phase == phase) & (np.isclose(seed.ara_x, grid_x))]
                ratios = values.ratio_frobenius.to_numpy()
                median = float(np.median(ratios))
                lo, hi = bootstrap_interval(ratios, rng)
                published = published_grid[(published_grid.archive == archive) & (published_grid.phase == phase) & (np.isclose(published_grid.ara_x, grid_x))].iloc[0]
                max_grid_error = max(max_grid_error, abs(median - published.median_ratio_frobenius))
                max_ci_error = max(max_ci_error, abs(lo - published.ci95_low), abs(hi - published.ci95_high))
                spectral = float(np.median(values.ratio_spectral))
                wrong = float(np.median(values.wrong_phase_frobenius))
                max_control_error = max(max_control_error, abs(spectral - published.median_ratio_spectral), abs(wrong - published.median_wrong_phase_frobenius))
                recomputed_rows.append((archive, phase, grid_x, len(values), median))

    fixed_grid = sorted(published_grid.ara_x.unique().tolist()) == GRID.tolist()
    cell_counts_pass = bool((published_grid.seeds >= 50).all())
    denominators_pass = bool((seed.child_frobenius > EPS).all())
    crossing_validation = validate_crossing_sample(crossings)
    permutation = reproduce_permutation(pairs, seed)
    max_permutation_error = 0.0
    for archive, values in permutation.items():
        published = result["family_label_permutation"][archive]
        max_permutation_error = max(
            max_permutation_error,
            abs(values["observed_mean_abs_phi_error"] - published["observed_mean_abs_phi_error"]),
            abs(values["null_median_mean_abs_phi_error"] - published["null_median_mean_abs_phi_error"]),
            abs(values["null_ci95"][0] - published["null_ci95"][0]),
            abs(values["null_ci95"][1] - published["null_ci95"][1]),
            abs(values["p_observed_no_worse_than_null"] - published["p_observed_no_worse_than_null"]),
        )

    checks = {
        "protocol_hash_matches": protocol_match,
        "fixed_grid_complete": fixed_grid,
        "data_gate_seed_counts_pass": cell_counts_pass,
        "data_gate_denominators_pass": denominators_pass,
        "crossing_row_count_matches": len(crossings) == result["counts"]["crossing_rows"],
        "pair_profile_count_matches": len(pairs) == result["counts"]["pair_profiles"],
        "seed_ratio_count_matches": len(seed) == result["counts"]["seed_ratios"],
        "grid_medians_exact": max_grid_error <= 1e-12,
        "bootstrap_intervals_exact": max_ci_error <= 1e-12,
        "control_medians_exact": max_control_error <= 1e-12,
        "sample_interpolation_exact": crossing_validation["outside_run_coordinate_range"] == 0 and crossing_validation["max_frobenius_interpolation_error"] <= 1e-12 and crossing_validation["max_spectral_interpolation_error"] <= 1e-12,
        "permutation_summary_exact": max_permutation_error <= 1e-12,
        "published_verdict_is_negative": result["status"] == "NOT SUPPORTED" and not result["evaluation"]["strict_support"],
    }
    checks = {key: bool(value) for key, value in checks.items()}
    output = {
        "test_id": "Q58-independent-validation-v1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "max_errors": {
            "grid_median": max_grid_error,
            "bootstrap_interval": max_ci_error,
            "control_median": max_control_error,
            "permutation_summary": max_permutation_error,
        },
        "crossing_sample": crossing_validation,
        "permutation_reproduction": permutation,
    }
    OUTPUT.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))
    if output["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
