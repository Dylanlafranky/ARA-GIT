"""Independent validation for Q40; does not import the main Q40 module."""

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


DATA = HERE / "public_data" / "q40_return_flow_inhomo_v1_greedy"
SOURCE = DATA / "unnati_submit_12_inhomo_v1_greedy.hdf5"
ARCHIVE = DATA / "unnati_submit_12_inhomo_v1_greedy.hdf5.zip"
DERIVED = DATA / "q40_derived_cache.npz"
CONNECTED = DATA / "q40_connected_cache.npy"
PREDICTIONS = DATA / "q40_frozen_predictions.npz"
RESULTS = HERE / "Q40_RETURN_FLOW_RELATION_REVERSAL_RESULTS.json"
EVENTS = HERE / "Q40_RETURN_FLOW_RELATION_REVERSAL_CYCLES.csv.gz"
VALIDATION = HERE / "Q40_RETURN_FLOW_RELATION_REVERSAL_VALIDATION.json"

EXPECTED_ARCHIVE_MD5 = "c04eb02b1766d9f83fb0240689d209a5"
EXPECTED_PROTOCOL_SHA256 = "256c13c251bed401efebff8351696d22ab9a0a1d991ca8c4aa142fab620f1c0f"
EXPECTED_FIDELITY_SHA256 = "ede891b99a6311ed10e864814389017b70d366f8e95449590e23337a1c821915"
EXPECTED_TARGET_LOCK_SHA256 = "e6f8e58d16bfb601a877f646c875b34bfbf59de264954bff0852ce41eef8b74c"
PROTOCOL = HERE / "Q40_RETURN_FLOW_RELATION_REVERSAL_PROTOCOL_v1_PRETARGET_FROZEN.md"
FIDELITY = HERE / "Q40_RETURN_FLOW_RELATION_REVERSAL_FIDELITY_v1.md"
TARGET_LOCK = HERE / "Q40_TARGET_LOCK_v1_FROZEN.md"
BRANCH = "c2_2local connectivity"
PAIRS = tuple(itertools.combinations(range(12), 2))
PAIR_NAMES = tuple(str(pair) for pair in PAIRS)
METHODS = (
    "q40",
    "forward",
    "persistence",
    "old_identity",
    "linear",
    "mean",
    "wrong_order",
    "whole_sign",
    "persistence_guard",
    "inverted_flag",
    "affine",
)
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
    ),
    axis=0,
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

    def visitor(_name: str, obj) -> None:
        if (
            isinstance(obj, h5py.Group)
            and "two_qubit_dms" in obj
            and "previous_order" in obj
        ):
            found.append(obj.name)

    root.visititems(visitor)
    if len(found) != 1:
        raise RuntimeError(f"Unexpected seed schema {seed}: {found}")
    return found[0]


def connected_from_rho(rho: np.ndarray) -> np.ndarray:
    expectation = np.einsum("ij,kji->k", rho, OPS, optimize=True).real
    a, b = expectation[:3], expectation[3:6]
    tensor = expectation[6:15].reshape(3, 3)
    return tensor - a[:, None] * b[None, :]


def predictors(c1, c2, c3, flag: bool, affine: np.ndarray):
    delta = c1 - c2
    forward = c3 + delta
    return np.stack(
        (
            c3 - delta if flag else forward,
            forward,
            c3,
            c1,
            2 * c3 - c2,
            (c1 + c2 + c3) / 3,
            c3 - delta,
            -forward if flag else forward,
            c3 if flag else forward,
            forward if flag else c3 - delta,
            affine[0] * c1 + affine[1] * c2 + affine[2] * c3,
        )
    )


def metrics(predicted, actual, scale):
    error = float(np.linalg.norm(predicted - actual))
    actual_norm = float(np.linalg.norm(actual))
    cosine = float(
        np.sum(predicted * actual)
        / (np.linalg.norm(predicted) * actual_norm + EPS)
    )
    return {
        "scaled_error": error / (scale + EPS),
        "absolute_error": error,
        "nrmse": error / (actual_norm + EPS),
        "cosine": cosine,
        "closure_error": abs(
            float(np.cbrt(abs(np.linalg.det(predicted))))
            - float(np.cbrt(abs(np.linalg.det(actual))))
        )
        / (float(np.cbrt(abs(np.linalg.det(actual)))) + EPS),
    }


def main() -> None:
    summary = json.loads(RESULTS.read_text(encoding="utf-8"))
    frozen = np.load(PREDICTIONS, allow_pickle=False)
    connected = np.load(CONNECTED, mmap_mode="r")
    derived = np.load(DERIVED, allow_pickle=False)
    methods = tuple(str(value) for value in frozen["methods"])
    if methods != METHODS:
        raise RuntimeError(f"Method mismatch: {methods}")
    forbidden_keys = {
        key
        for key in frozen.files
        if "target" in key.lower() or "actual" in key.lower() or key == "c4"
    }
    if forbidden_keys:
        raise RuntimeError(f"Target leaked into prediction artifact: {forbidden_keys}")

    checks = {
        "archive_md5": digest(ARCHIVE, "md5") == EXPECTED_ARCHIVE_MD5,
        "protocol_sha256": digest(PROTOCOL, "sha256")
        == EXPECTED_PROTOCOL_SHA256,
        "fidelity_sha256": digest(FIDELITY, "sha256")
        == EXPECTED_FIDELITY_SHA256,
        "target_lock_sha256": digest(TARGET_LOCK, "sha256")
        == EXPECTED_TARGET_LOCK_SHA256,
        "prediction_sha256": digest(PREDICTIONS, "sha256")
        == summary["frozen_files"]["prediction_sha256"],
        "prediction_artifact_has_no_target_matrix": not forbidden_keys,
        "connected_shape": list(connected.shape) == [100, 500, 66, 3, 3],
        "closure_shape": list(derived["closure"].shape) == [100, 500, 66],
    }

    rng = np.random.default_rng(400127)
    raw_indices = np.column_stack(
        (
            rng.integers(0, 100, size=4000),
            rng.integers(0, 500, size=4000),
            rng.integers(0, 66, size=4000),
        )
    )
    max_connected_difference = 0.0
    max_trace_error = 0.0
    max_hermiticity_error = 0.0
    min_eigenvalue = np.inf
    grouped: dict[int, list[tuple[int, int]]] = {}
    for seed, time_index, pair in raw_indices:
        grouped.setdefault(int(seed), []).append((int(time_index), int(pair)))
    with h5py.File(SOURCE, "r") as handle:
        for seed, samples in grouped.items():
            root = handle[locate_trial(handle, seed)]["two_qubit_dms"]
            for time_index, pair in samples:
                rho = np.asarray(
                    root[str(time_index)][PAIR_NAMES[pair]][()],
                    dtype=np.complex128,
                )
                recomputed = connected_from_rho(rho)
                max_connected_difference = max(
                    max_connected_difference,
                    float(np.max(abs(recomputed - connected[seed, time_index, pair]))),
                )
                max_trace_error = max(
                    max_trace_error, float(abs(np.trace(rho) - 1))
                )
                max_hermiticity_error = max(
                    max_hermiticity_error,
                    float(np.max(abs(rho - rho.conj().T))),
                )
                min_eigenvalue = min(
                    min_eigenvalue,
                    float(np.min(np.linalg.eigvalsh((rho + rho.conj().T) / 2))),
                )

    n = len(frozen["seed"])
    sample_indices = np.sort(rng.choice(n, size=min(401, n), replace=False))
    prediction_max_difference = 0.0
    visible_max_difference = 0.0
    metric_max_difference = 0.0
    flag_disagreements = 0
    event_lookup = {}
    with gzip.open(EVENTS, "rt", newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            event_lookup[int(row["cycle_id"])] = row

    affine = np.asarray(frozen["affine_coefficients"], dtype=np.float64)
    for index in sample_indices:
        seed, pair = int(frozen["seed"][index]), int(frozen["pair"][index])
        identities = []
        for visit in (1, 2, 3):
            start = int(frozen[f"q{visit}_start"][index])
            end = int(frozen[f"q{visit}_end"][index])
            identities.append(
                np.mean(
                    connected[seed, start : end + 1, pair],
                    axis=0,
                    dtype=np.float64,
                )
            )
        c1, c2, c3 = identities
        visible_max_difference = max(
            visible_max_difference,
            float(np.max(abs(np.stack(identities) - frozen["c_visible"][index]))),
        )
        forward = c1 - c2 + c3
        flag = (
            float(
                np.sum(forward * c3)
                / (np.linalg.norm(forward) * np.linalg.norm(c3) + EPS)
            )
            < 0
        )
        if flag != bool(frozen["flag"][index]):
            flag_disagreements += 1
        reconstructed = predictors(c1, c2, c3, flag, affine)
        prediction_max_difference = max(
            prediction_max_difference,
            float(np.max(abs(reconstructed - frozen["predictions"][index]))),
        )
        start = int(frozen["q4_start"][index])
        end = int(frozen["q4_end"][index])
        actual = np.mean(
            connected[seed, start : end + 1, pair],
            axis=0,
            dtype=np.float64,
        )
        saved = event_lookup[int(index)]
        for method_index, method in enumerate(METHODS):
            recalculated = metrics(
                reconstructed[method_index],
                actual,
                float(frozen["lineage_scale"][index]),
            )
            for name, value in recalculated.items():
                metric_max_difference = max(
                    metric_max_difference,
                    abs(value - float(saved[f"{method}_{name}"])),
                )

    overlap_failures = 0
    grouped_rows: dict[tuple[int, int], list[dict]] = {}
    for row in event_lookup.values():
        grouped_rows.setdefault(
            (int(row["seed"]), int(row["pair_index"])), []
        ).append(row)
    for rows in grouped_rows.values():
        rows.sort(key=lambda row: int(row["q1_start"]))
        for left, right in zip(rows, rows[1:]):
            if int(right["q1_start"]) <= int(left["q4_end"]):
                overlap_failures += 1

    flag = np.asarray([int(row["flag"]) == 1 for row in event_lookup.values()])
    target = np.asarray(
        [
            int(row["target_negative_orientation"]) == 1
            for row in event_lookup.values()
        ]
    )
    confusion = {
        "true_positive": int(np.sum(flag & target)),
        "false_positive": int(np.sum(flag & ~target)),
        "false_negative": int(np.sum(~flag & target)),
        "true_negative": int(np.sum(~flag & ~target)),
    }
    checks.update(
        {
            "raw_connected_tolerance": max_connected_difference <= 5e-6,
            # The deposited simulator stores traces with approximately
            # float32-scale serialization error; this checks the observed
            # matrices against a conservative 5e-5 normalization tolerance.
            "raw_trace_tolerance": max_trace_error <= 5e-5,
            "raw_hermiticity_tolerance": max_hermiticity_error <= 5e-8,
            "raw_eigenvalue_tolerance": min_eigenvalue >= -5e-8,
            "visible_matrix_tolerance": visible_max_difference <= 5e-7,
            "prediction_matrix_tolerance": prediction_max_difference <= 5e-7,
            # Predictions are deliberately frozen as float32 matrices. The
            # independent path reconstructs in float64, so derived nonlinear
            # metrics are checked at a conservative 5e-6 tolerance.
            "metric_tolerance": metric_max_difference <= 5e-6,
            "flag_exact": flag_disagreements == 0,
            "cycle_nonoverlap": overlap_failures == 0,
            "cycle_count": len(event_lookup)
            == summary["population"]["complete_cycles"],
            "confusion_exact": confusion
            == {
                key: int(summary["visible_flag"][key])
                for key in confusion
            },
        }
    )
    output = {
        "test_id": "Q40-INDEPENDENT-VALIDATION-v1",
        "passed": all(checks.values()),
        "checks": checks,
        "raw_density_matrices_recomputed": 4000,
        "prediction_cycles_recomputed": int(len(sample_indices)),
        "max_connected_difference": max_connected_difference,
        "max_trace_error": max_trace_error,
        "max_hermiticity_error": max_hermiticity_error,
        "min_density_matrix_eigenvalue": min_eigenvalue,
        "max_visible_matrix_difference": visible_max_difference,
        "max_prediction_matrix_difference": prediction_max_difference,
        "max_metric_difference": metric_max_difference,
        "flag_disagreements": flag_disagreements,
        "cycle_overlap_failures": overlap_failures,
        "confusion": confusion,
    }
    VALIDATION.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))
    if not output["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
