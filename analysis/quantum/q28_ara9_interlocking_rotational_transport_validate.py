"""Independent validation for Q28 without importing the primary runner."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import pathlib
import sys


HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / ".q27_deps"))

import h5py  # noqa: E402
import numpy as np  # noqa: E402


RESULTS = HERE / "Q28_ARA9_INTERLOCKING_ROTATIONAL_TRANSPORT_RESULTS.json"
TRIALS = HERE / "Q28_ARA9_INTERLOCKING_ROTATIONAL_TRANSPORT_TRIALS.csv"
LAG_CURVE = HERE / "Q28_ARA9_INTERLOCKING_ROTATIONAL_TRANSPORT_LAG_CURVE.csv"
EVENTS = HERE / "Q28_ARA9_INTERLOCKING_ROTATIONAL_TRANSPORT_EVENT_SAMPLE.csv"
WORKED = HERE / "Q28_ARA9_INTERLOCKING_ROTATIONAL_TRANSPORT_WORKED_TRAJECTORY.csv"
FIGURE = HERE / "Q28_ARA9_INTERLOCKING_ROTATIONAL_TRANSPORT_GEOMETRY.png"
FIGURE_SVG = HERE / "Q28_ARA9_INTERLOCKING_ROTATIONAL_TRANSPORT_GEOMETRY.svg"
PROTOCOL = HERE / "Q28_ARA9_INTERLOCKING_ROTATIONAL_TRANSPORT_PROTOCOL_v1_FROZEN.md"
FIDELITY = HERE / "Q28_ARA9_INTERLOCKING_ROTATIONAL_TRANSPORT_FIDELITY_v1.md"
SOURCE_DIR = HERE / "public_data" / "q27_network_reconstruction"
SOURCE = SOURCE_DIR / "unnati_submit_12_pure_random.hdf5"
Q27_CACHE = SOURCE_DIR / "q27_derived_cache.npz"
CONNECTED_CACHE = SOURCE_DIR / "q28_connected_cache.npy"
OUTPUT = HERE / "Q28_ARA9_INTERLOCKING_ROTATIONAL_TRANSPORT_VALIDATION.json"

EXPECTED_SOURCE = "0e10afb6e5c7bcc3b469a9bb18a9bcae9469bfae165d5da5add93eeeb1972eeb"
EXPECTED_PROTOCOL = "400789b6ccfa22962d6860b23c379fada7ca00684346bab19daa8fbd88481d14"
EXPECTED_FIDELITY = "62bbf38f26cc0433655516652e3e45fd674b89b8a4052686b3eeb898fad07e07"
BRANCHES = ("c2_2local connectivity", "c4_2local connectivity")
PAIRS = tuple(itertools.combinations(range(12), 2))
PAIR_NAMES = tuple(str(pair) for pair in PAIRS)

I2 = np.eye(2, dtype=np.complex128)
X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
PAULI = (X, Y, Z)
OPS = np.concatenate(
    (
        np.stack([np.kron(p, I2) for p in PAULI]),
        np.stack([np.kron(I2, p) for p in PAULI]),
        np.stack([np.kron(p, q) for p in PAULI for q in PAULI]),
    )
)


def digest(path: pathlib.Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def connected_relation(rho: np.ndarray) -> np.ndarray:
    expectations = np.einsum("ij,kji->k", rho, OPS, optimize=True).real
    a = expectations[:3]
    b = expectations[3:6]
    tensor = expectations[6:15].reshape(3, 3)
    return tensor - a[:, None] * b[None, :]


def close(left: float, right: float, tolerance: float = 1e-10) -> bool:
    return bool(np.isclose(left, right, rtol=tolerance, atol=tolerance))


def pooled_sum_from_trials(
    selected: list[dict[str, str]], field: str
) -> float:
    weight = sum(float(row["weight"]) for row in selected)
    return sum(float(row[field]) for row in selected) / weight


def weighted_metric_from_trials(
    selected: list[dict[str, str]], field: str
) -> float:
    weight = sum(float(row["weight"]) for row in selected)
    return (
        sum(float(row["weight"]) * float(row[field]) for row in selected)
        / weight
    )


def bootstrap(
    hidden: list[dict[str, str]], draws: int = 2000
) -> dict[str, float]:
    rng = np.random.default_rng(28028)
    count = len(hidden)
    comparisons = {
        "rotation_beats_no_rotation": "sum_no_rotation",
        "shared_beats_wrong_endpoint": "sum_wrong",
        "exact_beats_seed_displacement": "sum_seed",
        "exact_beats_time_displacement": "sum_time",
        "positive_lag_beats_lag_zero": "sum_lag_zero",
    }
    successes = {name: 0 for name in comparisons}
    weights = np.asarray([float(row["weight"]) for row in hidden])
    exact_sums = np.asarray([float(row["sum_rotation"]) for row in hidden])
    control_sums = {
        name: np.asarray([float(row[field]) for row in hidden])
        for name, field in comparisons.items()
    }
    for _ in range(draws):
        indices = rng.integers(0, count, size=count)
        denominator = float(np.sum(weights[indices]))
        exact = float(np.sum(exact_sums[indices]) / denominator)
        for name, values in control_sums.items():
            control = float(np.sum(values[indices]) / denominator)
            successes[name] += int(exact < control)
    return {name: value / draws for name, value in successes.items()}


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    trial_rows = rows(TRIALS)
    lag_rows = rows(LAG_CURVE)
    event_rows = rows(EVENTS)
    worked_rows = rows(WORKED)
    connected = np.load(CONNECTED_CACHE, mmap_mode="r")
    q27 = np.load(Q27_CACHE, allow_pickle=False)
    qc = np.asarray(q27["qc"], dtype=float)

    checks: list[tuple[str, bool]] = []

    def check(name: str, condition: bool) -> None:
        checks.append((name, bool(condition)))

    check("source_sha256", digest(SOURCE) == EXPECTED_SOURCE)
    check("protocol_sha256", digest(PROTOCOL) == EXPECTED_PROTOCOL)
    check("fidelity_sha256", digest(FIDELITY) == EXPECTED_FIDELITY)
    check("connected_cache_shape", connected.shape == (2, 100, 500, 66, 3, 3))
    check("connected_cache_dtype", connected.dtype == np.float32)
    check("all_expected_outputs_exist", all(
        path.exists() and path.stat().st_size > 0
        for path in (RESULTS, TRIALS, LAG_CURVE, EVENTS, WORKED, FIGURE, FIGURE_SVG)
    ))
    check("trial_rows_400", len(trial_rows) == 400)
    check("lag_rows_16", len(lag_rows) == 16)
    check("event_sample_nonempty", len(event_rows) > 0)
    check("worked_trajectory_nonempty", len(worked_rows) > 0)

    # Independently reconstruct a value-independent 200-state raw sample.
    max_cache_error = 0.0
    max_off_diagonal = 0.0
    max_asymmetry = 0.0
    sample_count = 0
    with h5py.File(SOURCE, "r") as handle:
        for branch_index, branch in enumerate(BRANCHES):
            for seed in range(0, 100, 10):
                base = handle[
                    f"/12 qubits/{branch}/unitary energy subspace 1/"
                    f"unitary seed {seed}/ordering seed random/two_qubit_dms"
                ]
                for time_index, pair_index in (
                    (0, 0),
                    (57, 7),
                    (124, 16),
                    (249, 32),
                    (374, 48),
                    (499, 65),
                    (141, 23),
                    (281, 41),
                    (403, 55),
                    (487, 63),
                ):
                    rho = np.asarray(
                        base[str(time_index)][PAIR_NAMES[pair_index]][()],
                        dtype=np.complex128,
                    )
                    rebuilt = connected_relation(rho)
                    cached = np.asarray(
                        connected[branch_index, seed, time_index, pair_index],
                        dtype=float,
                    )
                    max_cache_error = max(
                        max_cache_error, float(np.max(np.abs(rebuilt - cached)))
                    )
                    off_diagonal = rebuilt.copy()
                    off_diagonal[np.diag_indices(3)] = 0
                    max_off_diagonal = max(
                        max_off_diagonal, float(np.max(np.abs(off_diagonal)))
                    )
                    max_asymmetry = max(
                        max_asymmetry,
                        float(np.max(np.abs(rebuilt - rebuilt.T))),
                    )
                    sample_count += 1

    check("raw_sample_200", sample_count == 200)
    check("raw_connected_cache_agreement", max_cache_error <= 2e-6)
    check("raw_sample_exactly_diagonal", max_off_diagonal <= 1e-12)
    check("raw_sample_exactly_symmetric", max_asymmetry <= 1e-12)

    development = [row for row in trial_rows if row["split"] == "development"]
    hidden = [row for row in trial_rows if row["split"] == "hidden"]
    pooled = result["hidden"]["pooled"]
    check("development_trials_200", len(development) == 200)
    check("hidden_trials_200", len(hidden) == 200)
    check(
        "hidden_event_count",
        sum(int(row["events"]) for row in hidden) == int(pooled["events"]) == 76393,
    )
    for field in (
        "spectrum_similarity",
        "seed_spectrum_similarity",
        "time_spectrum_similarity",
    ):
        check(
            f"hidden_{field}",
            close(
                weighted_metric_from_trials(hidden, field),
                float(pooled[field]),
            ),
        )

    # The named sum fields differ for two controls; check explicitly.
    explicit = {
        "rotation_error": "sum_rotation",
        "no_rotation_error": "sum_no_rotation",
        "wrong_endpoint_error": "sum_wrong",
        "seed_error": "sum_seed",
        "time_error": "sum_time",
        "lag_zero_error": "sum_lag_zero",
    }
    for metric, sum_field in explicit.items():
        check(
            f"hidden_{metric}_explicit",
            close(pooled_sum_from_trials(hidden, sum_field), float(pooled[metric])),
        )

    development_lags = [
        row for row in lag_rows if row["split"] == "development"
    ]
    selected = min(
        development_lags,
        key=lambda row: (float(row["rotation_error"]), int(row["lag"])),
    )
    check("selected_lag_2", int(selected["lag"]) == result["selected_lag"] == 2)

    independent_bootstrap = bootstrap(hidden)
    for name, value in independent_bootstrap.items():
        check(
            f"bootstrap_{name}",
            close(value, float(result["bootstrap"][name])),
        )

    check(
        "wrong_endpoint_exact_degeneracy",
        all(
            close(float(row["rotation_error"]), float(row["wrong_endpoint_error"]))
            for row in trial_rows
        ),
    )
    check(
        "angles_binary_in_sample",
        {
            round(float(row["angle_deg"]), 9) for row in event_rows
        }.issubset({0.0, 180.0}),
    )
    check(
        "source_quality_gate",
        float(np.max(qc[:, :, 0])) <= 5e-5
        and float(np.max(qc[:, :, 1])) <= 1e-6
        and float(np.min(qc[:, :, 2])) >= -1e-6,
    )
    check("eligibility_fails_event_floor", int(pooled["events"]) < 100_000)
    check("reported_verdict_inconclusive", result["verdict"] == "INCONCLUSIVE")
    check("reported_I3_false", result["gates"]["I3_shared_endpoint_5pct_and_bootstrap"] is False)

    passed = sum(condition for _, condition in checks)
    validation = {
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "checks": {name: condition for name, condition in checks},
        "independent_measurements": {
            "raw_sample_count": sample_count,
            "maximum_connected_cache_error": max_cache_error,
            "maximum_off_diagonal_magnitude": max_off_diagonal,
            "maximum_matrix_asymmetry": max_asymmetry,
            "independent_bootstrap": independent_bootstrap,
        },
        "interpretive_boundary": (
            "The exact diagonal source makes endpoint reversal unidentifiable "
            "and restricts fitted rotations to 0 or 180 degrees. The hidden "
            "two-step advantage is reproducible, but this dataset cannot test "
            "a continuous angled rotational pivot."
        ),
    }
    OUTPUT.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))
    if validation["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
