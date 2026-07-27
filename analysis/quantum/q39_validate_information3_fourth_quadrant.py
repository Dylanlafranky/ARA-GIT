"""Independent Q39 raw-record and result validation."""

from __future__ import annotations

import csv
import gzip
import hashlib
import itertools
import json
import pathlib
import sys


HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / "public_data" / "_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))

import h5py
import numpy as np


DATA = HERE / "public_data" / "q39_information3_strongmax"
SOURCE = DATA / "unnati_submit_12_pure_strongmax.hdf5"
ARCHIVE = DATA / "unnati_submit_12_pure_strongmax.hdf5.zip"
DERIVED = DATA / "q39_derived_cache.npz"
CONNECTED = DATA / "q39_connected_cache.npy"
RESULTS = HERE / "Q39_ARA9_INFORMATION3_FOURTH_QUADRANT_RESULTS.json"
EVENTS = HERE / "Q39_ARA9_INFORMATION3_FOURTH_QUADRANT_CYCLES.csv.gz"
OUTPUT = HERE / "Q39_ARA9_INFORMATION3_FOURTH_QUADRANT_VALIDATION.json"
PROTOCOL = HERE / "Q39_ARA9_INFORMATION3_FOURTH_QUADRANT_PROTOCOL_v1_FROZEN.md"
FIDELITY = HERE / "Q39_ARA9_INFORMATION3_FOURTH_QUADRANT_FIDELITY_v1.md"

EXPECTED_ARCHIVE_MD5 = "11b5f14ba185a9901f6a85bd31497d71"
EXPECTED_PROTOCOL_SHA256 = (
    "db74e4f69c4a263d317b5b1ae53dfb042d94585e2f2eb8404048e5fcad3f7ccb"
)
EXPECTED_FIDELITY_SHA256 = (
    "6ac71c0904a6295391261fca67cde7e7cc71d02a9d91f50c27d45f0b27a8d779"
)
BRANCH = "c2_2local connectivity"
PAIRS = tuple(itertools.combinations(range(12), 2))
PAIR_NAMES = tuple(str(pair) for pair in PAIRS)
METHODS = ("ara", "persistence", "no_flip", "linear", "mean", "wrong_order")
EPS = 1e-12

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


def digest(path: pathlib.Path, algorithm: str) -> str:
    value = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def locate_trial(handle: h5py.File, seed: int) -> str:
    root = handle[
        f"/12 qubits/{BRANCH}/unitary energy subspace 1/unitary seed {seed}"
    ]
    found = []

    def visitor(_name, obj):
        if (
            isinstance(obj, h5py.Group)
            and "two_qubit_dms" in obj
            and "previous_order" in obj
        ):
            found.append(obj.name)

    root.visititems(visitor)
    if len(found) != 1:
        raise RuntimeError(f"Unexpected seed schema for {seed}: {found}")
    return found[0]


def raw_quantities(rho: np.ndarray):
    expectation = np.einsum("ij,kji->k", rho, OPS, optimize=True).real
    a, b = expectation[:3], expectation[3:6]
    tensor = expectation[6:15].reshape(3, 3)
    connected = tensor - np.outer(a, b)
    closure = float(np.cbrt(abs(np.linalg.det(connected))))
    purity = float(np.trace(rho @ rho).real)
    l1 = float(np.sum(np.abs(rho)) - np.sum(np.abs(np.diag(rho))))
    return connected, closure, purity, l1


def matrix_metrics(predicted: np.ndarray, actual: np.ndarray):
    nrmse = float(
        np.linalg.norm(predicted - actual) / (np.linalg.norm(actual) + EPS)
    )
    cosine = float(
        np.sum(predicted * actual)
        / (np.linalg.norm(predicted) * np.linalg.norm(actual) + EPS)
    )
    predicted_h = float(np.cbrt(abs(np.linalg.det(predicted))))
    actual_h = float(np.cbrt(abs(np.linalg.det(actual))))
    closure_error = float(abs(predicted_h - actual_h) / (actual_h + EPS))
    return nrmse, cosine, closure_error


def main() -> None:
    checksums = {
        "archive_md5": digest(ARCHIVE, "md5"),
        "protocol_sha256": digest(PROTOCOL, "sha256"),
        "fidelity_sha256": digest(FIDELITY, "sha256"),
    }
    checksum_pass = (
        checksums["archive_md5"] == EXPECTED_ARCHIVE_MD5
        and checksums["protocol_sha256"] == EXPECTED_PROTOCOL_SHA256
        and checksums["fidelity_sha256"] == EXPECTED_FIDELITY_SHA256
    )
    derived = np.load(DERIVED, allow_pickle=False)
    closure_cache = derived["closure"]
    purity_cache = derived["purity"]
    l1_cache = derived["l1"]
    connected_cache = np.load(CONNECTED, mmap_mode="r")

    max_errors = {
        "connected": 0.0,
        "closure": 0.0,
        "purity": 0.0,
        "l1_coherence": 0.0,
        "trace": 0.0,
        "hermiticity": 0.0,
    }
    min_eigenvalue = float("inf")
    raw_checks = 0
    with h5py.File(SOURCE, "r") as handle:
        for seed in range(32):
            root = handle[locate_trial(handle, seed)]["two_qubit_dms"]
            for time_index in (0, 124, 249, 374, 499):
                for pair in range(25):
                    rho = np.asarray(
                        root[str(time_index)][PAIR_NAMES[pair]][()],
                        dtype=np.complex128,
                    )
                    c, h, p, k = raw_quantities(rho)
                    max_errors["connected"] = max(
                        max_errors["connected"],
                        float(
                            np.max(abs(c - connected_cache[seed, time_index, pair]))
                        ),
                    )
                    max_errors["closure"] = max(
                        max_errors["closure"],
                        abs(h - float(closure_cache[seed, time_index, pair])),
                    )
                    max_errors["purity"] = max(
                        max_errors["purity"],
                        abs(p - float(purity_cache[seed, time_index, pair])),
                    )
                    max_errors["l1_coherence"] = max(
                        max_errors["l1_coherence"],
                        abs(k - float(l1_cache[seed, time_index, pair])),
                    )
                    max_errors["trace"] = max(
                        max_errors["trace"], float(abs(np.trace(rho) - 1))
                    )
                    max_errors["hermiticity"] = max(
                        max_errors["hermiticity"],
                        float(np.max(abs(rho - rho.conj().T))),
                    )
                    min_eigenvalue = min(
                        min_eigenvalue,
                        float(
                            np.min(
                                np.linalg.eigvalsh((rho + rho.conj().T) / 2)
                            )
                        ),
                    )
                    raw_checks += 1

    with gzip.open(EVENTS, "rt", newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    summary = json.loads(RESULTS.read_text(encoding="utf-8"))
    order_failures = 0
    interval_failures = 0
    metric_max_error = 0.0
    for row in rows:
        direction = int(row["direction"])
        labels = [int(row[f"q{i}"]) for i in range(1, 5)]
        expected = [
            (labels[0] + direction * step) % 4 for step in range(4)
        ]
        if labels != expected:
            order_failures += 1
        intervals = [
            (int(row[f"q{i}_start"]), int(row[f"q{i}_end"]))
            for i in range(1, 5)
        ]
        if any(end < start for start, end in intervals) or any(
            intervals[i][1] >= intervals[i + 1][0] for i in range(3)
        ):
            interval_failures += 1

    for row in rows[:: max(1, len(rows) // 250)]:
        seed, pair = int(row["seed"]), int(row["pair_index"])
        identities = []
        for index in range(1, 5):
            start, end = int(row[f"q{index}_start"]), int(row[f"q{index}_end"])
            identities.append(
                np.mean(
                    connected_cache[seed, start : end + 1, pair],
                    axis=0,
                    dtype=np.float64,
                )
            )
        c1, c2, c3, c4 = identities
        predicted = {
            "ara": c1 - c2 + c3,
            "persistence": c3,
            "no_flip": c1,
            "linear": 2 * c3 - c2,
            "mean": (c1 + c2 + c3) / 3,
            "wrong_order": c2 - c1 + c3,
        }
        for method in METHODS:
            actual_metrics = matrix_metrics(predicted[method], c4)
            saved_metrics = (
                float(row[f"{method}_nrmse"]),
                float(row[f"{method}_cosine"]),
                float(row[f"{method}_closure_error"]),
            )
            metric_max_error = max(
                metric_max_error,
                max(abs(a - b) for a, b in zip(actual_metrics, saved_metrics)),
            )

    count_match = len(rows) == int(summary["population"]["complete_cycles"])
    validation = {
        "test_id": "Q39-INDEPENDENT-VALIDATION-v1",
        "checksums": checksums,
        "checksum_pass": checksum_pass,
        "raw_density_matrix_checks": raw_checks,
        "raw_cache_max_absolute_errors": max_errors,
        "raw_min_eigenvalue": min_eigenvalue,
        "cycle_count_csv": len(rows),
        "cycle_count_matches_summary": count_match,
        "cycle_order_failures": order_failures,
        "cycle_interval_failures": interval_failures,
        "deterministic_metric_spot_checks": len(rows[:: max(1, len(rows) // 250)]),
        "metric_max_absolute_error": metric_max_error,
        "pass": bool(
            checksum_pass
            and count_match
            and raw_checks == 4000
            and max_errors["connected"] < 1e-6
            and max_errors["closure"] < 1e-6
            and max_errors["purity"] < 1e-6
            and max_errors["l1_coherence"] < 1e-6
            and order_failures == 0
            and interval_failures == 0
            and metric_max_error < 1e-10
        ),
    }
    OUTPUT.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()

