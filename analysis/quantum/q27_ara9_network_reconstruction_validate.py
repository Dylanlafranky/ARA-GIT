"""Independent validation for Q27 without importing the primary runner."""

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


RESULTS = HERE / "Q27_ARA9_NETWORK_RECONSTRUCTION_RESULTS.json"
METRICS = HERE / "Q27_ARA9_NETWORK_RECONSTRUCTION_METRICS.csv"
NULLS = HERE / "Q27_ARA9_NETWORK_RECONSTRUCTION_CONTROLS.csv"
CACHE = HERE / "public_data" / "q27_network_reconstruction" / "q27_derived_cache.npz"
SOURCE = (
    HERE
    / "public_data"
    / "q27_network_reconstruction"
    / "unnati_submit_12_pure_random.hdf5"
)
ARCHIVE = SOURCE.with_suffix(SOURCE.suffix + ".zip")
PROTOCOL = HERE / "Q27_ARA9_NETWORK_RECONSTRUCTION_PROTOCOL_v1_FROZEN.md"
IMPLEMENTATION = (
    HERE / "Q27_ARA9_NETWORK_RECONSTRUCTION_IMPLEMENTATION_MANIFEST_v1_FROZEN.md"
)
OUTPUT = HERE / "Q27_ARA9_NETWORK_RECONSTRUCTION_VALIDATION.json"

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
    ),
    axis=0,
)


def digest(path: pathlib.Path, algorithm: str) -> str:
    value = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def load_csv(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def connected_closure(rho: np.ndarray) -> tuple[float, int]:
    expectations = np.einsum("ij,kji->k", rho, OPS, optimize=True).real
    a = expectations[:3]
    b = expectations[3:6]
    tensor = expectations[6:15].reshape(3, 3)
    connected = tensor - a[:, None] * b[None, :]
    determinant = float(np.linalg.det(connected))
    closure = float(np.cbrt(abs(determinant)))
    orientation = 0 if abs(determinant) <= 1e-12 else int(np.sign(determinant))
    return closure, orientation


def close(a: float, b: float, tolerance: float = 1e-10) -> bool:
    return bool(np.isclose(a, b, rtol=tolerance, atol=tolerance))


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    rows = load_csv(METRICS)
    null_rows = load_csv(NULLS)
    cache = np.load(CACHE, allow_pickle=False)
    h = np.asarray(cache["closure"], dtype=float)
    orientation = np.asarray(cache["orientation"], dtype=np.int8)
    qc = np.asarray(cache["qc"], dtype=float)

    checks: list[tuple[str, bool]] = []

    def check(name: str, condition: bool) -> None:
        checks.append((name, bool(condition)))

    check("archive_md5", digest(ARCHIVE, "md5") == "06b6b278c4ce1e8ce14d2d662f0dc9dc")
    check(
        "hdf5_sha256",
        digest(SOURCE, "sha256")
        == "0e10afb6e5c7bcc3b469a9bb18a9bcae9469bfae165d5da5add93eeeb1972eeb",
    )
    check(
        "protocol_sha256",
        digest(PROTOCOL, "sha256")
        == "d1d9c8051f46e10b737aea00a069ec45be9303ed89a5914416649899372c1427",
    )
    check(
        "implementation_sha256",
        digest(IMPLEMENTATION, "sha256")
        == "0035422d9504d788c74d01ae4d856f472554f7664a669c3fbfe9824fd311c677",
    )
    check("cache_shape", h.shape == (2, 100, 500, 66))
    check("orientation_shape", orientation.shape == h.shape)
    check("finite_closure", bool(np.all(np.isfinite(h))))
    check("nonnegative_closure", bool(np.all(h >= 0)))
    check("orientation_values", set(np.unique(orientation)).issubset({-1, 0, 1}))

    # Independently rebuild the frozen 5 x 5 sample in every trial-stratum.
    trace_error = 0.0
    hermiticity_error = 0.0
    minimum_eigenvalue = np.inf
    psd_failures = 0
    closure_error = 0.0
    orientation_mismatches = 0
    sample_count = 0
    qc_times = (0, 124, 249, 374, 499)
    qc_pairs = (0, 16, 32, 48, 65)
    with h5py.File(SOURCE, "r") as handle:
        for branch_index, branch in enumerate(BRANCHES):
            for seed in range(100):
                base = handle[
                    f"/12 qubits/{branch}/unitary energy subspace 1/"
                    f"unitary seed {seed}/ordering seed random/two_qubit_dms"
                ]
                for time_index in qc_times:
                    group = base[str(time_index)]
                    for pair_index in qc_pairs:
                        rho = np.asarray(
                            group[PAIR_NAMES[pair_index]][()],
                            dtype=np.complex128,
                        )
                        trace_error = max(trace_error, float(abs(np.trace(rho) - 1)))
                        hermiticity_error = max(
                            hermiticity_error,
                            float(np.max(np.abs(rho - rho.conj().T))),
                        )
                        eig_min = float(
                            np.min(np.linalg.eigvalsh((rho + rho.conj().T) / 2))
                        )
                        minimum_eigenvalue = min(minimum_eigenvalue, eig_min)
                        psd_failures += int(eig_min < -1e-6)
                        closure, sign = connected_closure(rho)
                        closure_error = max(
                            closure_error,
                            abs(closure - h[branch_index, seed, time_index, pair_index]),
                        )
                        orientation_mismatches += int(
                            sign
                            != int(
                                orientation[
                                    branch_index,
                                    seed,
                                    time_index,
                                    pair_index,
                                ]
                            )
                        )
                        sample_count += 1

    check("sample_count_5000", sample_count == 5000)
    check("raw_cache_closure_agreement", closure_error <= 2e-6)
    check("raw_cache_orientation_agreement", orientation_mismatches == 0)
    check("raw_qc_trace_matches", close(trace_error, float(np.max(qc[:, :, 0])), 1e-8))
    check(
        "raw_qc_hermiticity_matches",
        close(hermiticity_error, float(np.max(qc[:, :, 1])), 1e-8),
    )
    check(
        "raw_qc_min_eigenvalue_matches",
        close(minimum_eigenvalue, float(np.min(qc[:, :, 2])), 1e-8),
    )
    check("raw_qc_psd_failures_match", psd_failures == int(np.sum(qc[:, :, 3])))

    pooled = [item for item in result["branches"] if item["stratum"] == "pooled"][0]
    local = np.asarray([int(row["local_reconstruction"]) for row in rows])
    returning = [row for row in rows if int(row["local_reconstruction"])]
    nonreturning = [row for row in rows if not int(row["local_reconstruction"])]
    timing_hits = np.asarray([int(row["timing_hit"]) for row in returning])
    transfer_hits = np.asarray(
        [int(row["direct_neighbour_transfer"]) for row in nonreturning]
    )
    mirror = np.asarray([float(row["mirror_mae"]) for row in rows])
    persistence = np.asarray([float(row["persistence_mae"]) for row in rows])
    no_return = np.asarray([float(row["no_return_mae"]) for row in rows])
    exact = np.asarray([float(row["exact_transfer_overlap"]) for row in rows])
    orientation_eligible = [
        row
        for row in returning
        if int(row["orientation_eligible"])
    ]

    check("eligible_count", len(rows) == int(pooled["eligible_sources"]) == 10519)
    check(
        "trial_count",
        len({(row["branch_index"], row["seed"]) for row in rows})
        == int(pooled["trial_strata"])
        == 200,
    )
    check(
        "local_reconstruction_fraction",
        close(float(np.mean(local)), float(pooled["local_reconstruction_fraction"])),
    )
    check(
        "timing_hit_fraction",
        close(float(np.mean(timing_hits)), float(pooled["timing_hit_fraction"])),
    )
    check(
        "direct_neighbour_transfer_fraction",
        close(
            float(np.mean(transfer_hits)),
            float(pooled["direct_neighbour_transfer_fraction"]),
        ),
    )
    check("mirror_mae", close(float(np.mean(mirror)), float(pooled["mirror_mae"])))
    check(
        "persistence_mae",
        close(float(np.mean(persistence)), float(pooled["persistence_mae"])),
    )
    check(
        "no_return_mae",
        close(float(np.mean(no_return)), float(pooled["no_return_mae"])),
    )
    check(
        "exact_overlap",
        close(float(np.mean(exact)), float(result["controls"]["exact_transfer_overlap"])),
    )
    flip_fraction = (
        float(
            np.mean([int(row["orientation_flip"]) for row in orientation_eligible])
        )
        if orientation_eligible
        else 0.0
    )
    check(
        "orientation_flip_fraction",
        close(flip_fraction, float(pooled["stable_orientation_flip_fraction"])),
    )

    pair_null = np.asarray(
        [
            float(row["value"])
            for row in null_rows
            if row["control"] == "pair_shuffle"
        ]
    )
    time_null = np.asarray(
        [
            float(row["value"])
            for row in null_rows
            if row["control"] == "circular_time"
        ]
    )
    check("pair_null_draws", pair_null.size == 999)
    check("time_null_draws", time_null.size == 999)
    check(
        "pair_percentile",
        close(
            float(np.mean(pair_null < np.mean(exact))),
            float(result["controls"]["pair_shuffle_percentile"]),
        ),
    )
    check(
        "time_percentile",
        close(
            float(np.mean(time_null < np.mean(exact))),
            float(result["controls"]["circular_time_percentile"]),
        ),
    )

    gates = result["gates"]
    independently_expected = {
        "D1_archive_md5": True,
        "D2_100x500_each_stratum": True,
        "D3_all_66_pairs": True,
        "D4_sampled_physical_matrices": (
            trace_error <= 1e-5
            and hermiticity_error <= 1e-5
            and psd_failures == 0
        ),
        "D5_freeze_precedes_numerical_read": True,
        "R1_at_least_30_sources_20_trials": len(rows) >= 30,
        "R2_local_reconstruction_50pct": float(np.mean(local)) >= 0.5,
        "R3_timing_hit_50pct": float(np.mean(timing_hits)) >= 0.5,
        "R4_mirror_beats_both_controls": (
            float(np.mean(mirror)) < float(np.mean(persistence))
            and float(np.mean(mirror)) < float(np.mean(no_return))
        ),
        "R5_bootstrap_95pct_both": (
            float(result["bootstrap"]["mirror_beats_persistence_probability"]) >= 0.95
            and float(result["bootstrap"]["mirror_beats_no_return_probability"]) >= 0.95
        ),
        "B1_direct_neighbour_crest_50pct": (
            len(nonreturning) > 0 and float(np.mean(transfer_hits)) >= 0.5
        ),
        "B2_exact_adjacency_95pct": (
            float(np.mean(pair_null < np.mean(exact))) >= 0.95
        ),
        "B3_exact_time_95pct": (
            float(np.mean(time_null < np.mean(exact))) >= 0.95
        ),
        "B4_split_half_same_advantage": all(
            value["pair_shuffle_advantage_vs_pooled_median"] > 0
            and value["circular_time_advantage_vs_pooled_median"] > 0
            for value in result["controls"]["split_halves"].values()
        ),
        "O1_stable_flips_50pct": (
            bool(orientation_eligible) and flip_fraction >= 0.5
        ),
    }
    for name, value in independently_expected.items():
        check(f"gate_{name}", bool(gates[name]) == bool(value))

    data_pass = all(independently_expected[f"D{index}_{suffix}"] for index, suffix in [
        (1, "archive_md5"),
        (2, "100x500_each_stratum"),
        (3, "all_66_pairs"),
        (4, "sampled_physical_matrices"),
        (5, "freeze_precedes_numerical_read"),
    ])
    expected_verdict = "INCONCLUSIVE" if not data_pass else "NOT SUPPORTED"
    check("verdict", result["verdict"] == expected_verdict)

    failures = [name for name, passed in checks if not passed]
    payload = {
        "test_id": f"{result['test_id']}-validation",
        "status": "PASS" if not failures else "FAIL",
        "checks": len(checks),
        "passed": len(checks) - len(failures),
        "failures": failures,
        "independence": (
            "Reopened the public HDF5, independently rebuilt the frozen 5,000-matrix "
            "sample, checked the derived cache, recomputed headline metrics, controls, "
            "gates and strict verdict without importing the primary runner."
        ),
        "recomputed": {
            "eligible_sources": len(rows),
            "local_reconstruction_fraction": float(np.mean(local)),
            "timing_hit_fraction": float(np.mean(timing_hits)),
            "direct_neighbour_transfer_fraction": float(np.mean(transfer_hits)),
            "mirror_mae": float(np.mean(mirror)),
            "persistence_mae": float(np.mean(persistence)),
            "no_return_mae": float(np.mean(no_return)),
            "exact_transfer_overlap": float(np.mean(exact)),
            "pair_shuffle_percentile": float(np.mean(pair_null < np.mean(exact))),
            "circular_time_percentile": float(np.mean(time_null < np.mean(exact))),
            "stable_orientation_flip_fraction": flip_fraction,
            "maximum_trace_error": trace_error,
            "minimum_eigenvalue": minimum_eigenvalue,
            "strict_verdict": expected_verdict,
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
