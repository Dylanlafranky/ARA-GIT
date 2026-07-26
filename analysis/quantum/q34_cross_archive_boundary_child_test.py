"""Q34: untouched cross-archive replication of the Q33B ARA route.

The geometry, selection, controls, partitions and gates are inherited without
change from Q33B.  Only the public simulator archive changes from
12_pure_random to the preregistered 12_pure_greedy target.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import pathlib
import sys
import urllib.request
import zipfile
from concurrent.futures import ProcessPoolExecutor, as_completed


HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / ".q27_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))
os.environ.setdefault("MPLBACKEND", "Agg")

import h5py
import numpy as np

import q33b_ara_first_boundary_child_test as core


TEST_ID = "Q34-CROSS-ARCHIVE-BOUNDARY-CHILD-v1"
DOI = "10.5281/zenodo.16753415"
ARCHIVE_NAME = "unnati_submit_12_pure_greedy.hdf5.zip"
HDF_NAME = "unnati_submit_12_pure_greedy.hdf5"
ARCHIVE_MD5 = "c1cf77ccff486e3786d73ba47f8674f1"
DOWNLOAD_URL = (
    "https://zenodo.org/records/16753415/files/"
    + ARCHIVE_NAME
    + "?download=1"
)

PROTOCOL = HERE / "Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_PROTOCOL_v1_FROZEN.md"
FIDELITY = HERE / "Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_FIDELITY_v1.md"
PROTOCOL_SHA256 = "56963274392d0c1f4b1c9c0cfe2ece700d25f20b43c9136b881bbde39baeae1e"
FIDELITY_SHA256 = "f480e7fc7bcdbc7a69ad0a3b921552c9c8fad84e9e2e96c438f714f2373bda98"

SOURCE_DIR = HERE / "public_data" / "q34_cross_archive_greedy"
ARCHIVE = SOURCE_DIR / ARCHIVE_NAME
SOURCE = SOURCE_DIR / HDF_NAME
DERIVED_CACHE = SOURCE_DIR / "q34_derived_cache.npz"
CONNECTED_CACHE = SOURCE_DIR / "q34_connected_cache.npy"

RESULTS = HERE / "Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_RESULTS.json"
EVENTS = HERE / "Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_EVENTS.csv.gz"
TRIALS = HERE / "Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_TRIALS.csv"
FIGURE_PNG = HERE / "Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_GEOMETRY.png"
FIGURE_SVG = HERE / "Q34_CROSS_ARCHIVE_BOUNDARY_CHILD_GEOMETRY.svg"

BRANCHES = ("c2_2local connectivity", "c4_2local connectivity")
PAIRS = tuple(itertools.combinations(range(12), 2))
PAIR_NAMES = tuple(str(pair) for pair in PAIRS)
EPS = 1e-12

I2 = np.eye(2, dtype=np.complex128)
X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
PAULI = (X, Y, Z)
A_OPS = np.stack([np.kron(p, I2) for p in PAULI])
B_OPS = np.stack([np.kron(I2, p) for p in PAULI])
T_OPS = np.stack([np.kron(p, q) for p in PAULI for q in PAULI])
OPS = np.concatenate((A_OPS, B_OPS, T_OPS), axis=0)


def digest(path: pathlib.Path, algorithm: str) -> str:
    value = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def ensure_archive() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    if ARCHIVE.exists() and digest(ARCHIVE, "md5") == ARCHIVE_MD5:
        print(f"verified existing {ARCHIVE_NAME}", flush=True)
        return
    if ARCHIVE.exists():
        raise RuntimeError("Existing Q34 archive does not match the frozen MD5")
    partial = ARCHIVE.with_suffix(ARCHIVE.suffix + ".part")
    request = urllib.request.Request(
        DOWNLOAD_URL,
        headers={"User-Agent": "ARA-Q34-replication/1.0"},
    )
    print(f"downloading frozen target {DOWNLOAD_URL}", flush=True)
    with urllib.request.urlopen(request, timeout=120) as response, partial.open(
        "wb"
    ) as output:
        while True:
            chunk = response.read(8 * 1024 * 1024)
            if not chunk:
                break
            output.write(chunk)
            print(f"downloaded {output.tell() / 1e6:.1f} MB", flush=True)
    if digest(partial, "md5") != ARCHIVE_MD5:
        raise RuntimeError("Downloaded Q34 archive does not match frozen MD5")
    partial.replace(ARCHIVE)


def ensure_source() -> None:
    ensure_archive()
    if SOURCE.exists():
        print(f"using extracted {HDF_NAME}", flush=True)
        return
    with zipfile.ZipFile(ARCHIVE) as zipped:
        members = [item for item in zipped.infolist() if not item.is_dir()]
        matching = [item for item in members if pathlib.Path(item.filename).name == HDF_NAME]
        if len(matching) != 1:
            raise RuntimeError(f"Expected one {HDF_NAME}, found {len(matching)}")
        member = matching[0]
        with zipped.open(member) as source, SOURCE.open("wb") as output:
            while True:
                chunk = source.read(8 * 1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)
    print(f"extracted {SOURCE} ({SOURCE.stat().st_size} bytes)", flush=True)


def locate_trial_path(
    handle: h5py.File,
    branch: str,
    seed: int,
) -> str:
    seed_path = (
        f"/12 qubits/{branch}/unitary energy subspace 1/unitary seed {seed}"
    )
    seed_group = handle[seed_path]
    candidates: list[str] = []

    def visitor(name: str, obj) -> None:
        if not isinstance(obj, h5py.Group):
            return
        if "two_qubit_dms" in obj and "previous_order" in obj:
            candidates.append(obj.name)

    seed_group.visititems(visitor)
    if len(candidates) != 1:
        raise RuntimeError(
            f"Expected one trial payload at {seed_path}; found {candidates}"
        )
    return candidates[0]


def inspect_schema() -> dict[str, object]:
    with h5py.File(SOURCE, "r") as handle:
        root_keys = sorted(handle["/12 qubits"].keys())
        paths = {
            f"{branch}/seed0": locate_trial_path(handle, branch, 0)
            for branch in BRANCHES
        }
        for path in paths.values():
            group = handle[path]
            if len(group["two_qubit_dms"].keys()) != 500:
                raise RuntimeError(f"Q34 target does not contain 500 times at {path}")
            first = group["two_qubit_dms"]["0"]
            if sorted(first.keys()) != sorted(PAIR_NAMES):
                raise RuntimeError(f"Q34 pair schema mismatch at {path}")
    return {"root_keys": root_keys, "sample_paths": paths}


def density_batch(
    rhos: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    expectations = np.einsum("nij,kji->nk", rhos, OPS, optimize=True).real
    a = expectations[:, 0:3]
    b = expectations[:, 3:6]
    tensor = expectations[:, 6:15].reshape(-1, 3, 3)
    connected = tensor - a[:, :, None] * b[:, None, :]
    determinants = np.linalg.det(connected)
    closure = np.cbrt(np.abs(determinants))
    orientation = np.where(
        np.abs(determinants) <= EPS,
        0,
        np.sign(determinants),
    ).astype(np.int8)
    return (
        closure.astype(np.float32),
        orientation,
        connected.astype(np.float32),
    )


def process_trial(
    branch_index: int,
    seed: int,
) -> tuple[int, int, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    closure = np.empty((500, 66), dtype=np.float32)
    orientation = np.empty((500, 66), dtype=np.int8)
    connected = np.empty((500, 66, 3, 3), dtype=np.float32)
    quality = np.zeros(5, dtype=np.float64)
    quality[2] = np.inf
    qc_times = {0, 124, 249, 374, 499}
    qc_pairs = {0, 16, 32, 48, 65}
    with h5py.File(SOURCE, "r") as handle:
        path = locate_trial_path(handle, BRANCHES[branch_index], seed)
        base = handle[path]
        dm_root = base["two_qubit_dms"]
        for time in range(500):
            group = dm_root[str(time)]
            rhos = np.stack([group[name][()] for name in PAIR_NAMES])
            (
                closure[time],
                orientation[time],
                connected[time],
            ) = density_batch(rhos)
            if time in qc_times:
                for pair_index in qc_pairs:
                    rho = np.asarray(rhos[pair_index], dtype=np.complex128)
                    quality[0] = max(quality[0], float(abs(np.trace(rho) - 1)))
                    quality[1] = max(
                        quality[1],
                        float(np.max(np.abs(rho - rho.conj().T))),
                    )
                    eig_min = float(
                        np.min(np.linalg.eigvalsh((rho + rho.conj().T) / 2))
                    )
                    quality[2] = min(quality[2], eig_min)
                    quality[3] += int(eig_min < -1e-6)
                    quality[4] += 1
        edges = np.asarray(
            base["previous_order"]["orders_list"]["data"][()],
            dtype=np.int8,
        )
    return (
        branch_index,
        seed,
        closure,
        orientation,
        edges,
        connected,
        quality,
    )


def build_caches(workers: int) -> dict[str, object]:
    ensure_source()
    schema = inspect_schema()
    if DERIVED_CACHE.exists() and CONNECTED_CACHE.exists():
        print("using existing Q34 derived caches", flush=True)
        return schema

    closure = np.empty((2, 100, 500, 66), dtype=np.float32)
    orientation = np.empty((2, 100, 500, 66), dtype=np.int8)
    edges = np.empty((2, 100, 499, 6, 2), dtype=np.int8)
    quality = np.empty((2, 100, 5), dtype=np.float64)
    connected_cache = np.lib.format.open_memmap(
        CONNECTED_CACHE,
        mode="w+",
        dtype=np.float32,
        shape=(2, 100, 500, 66, 3, 3),
    )
    jobs = [(branch, seed) for branch in range(2) for seed in range(100)]
    completed = 0
    with ProcessPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = {
            executor.submit(process_trial, branch, seed): (branch, seed)
            for branch, seed in jobs
        }
        for future in as_completed(futures):
            (
                branch,
                seed,
                trial_closure,
                trial_orientation,
                trial_edges,
                trial_connected,
                trial_quality,
            ) = future.result()
            closure[branch, seed] = trial_closure
            orientation[branch, seed] = trial_orientation
            edges[branch, seed] = trial_edges
            connected_cache[branch, seed] = trial_connected
            quality[branch, seed] = trial_quality
            completed += 1
            if completed % 10 == 0 or completed == len(jobs):
                print(f"Q34 derived {completed}/{len(jobs)} strata", flush=True)
    connected_cache.flush()
    np.savez(
        DERIVED_CACHE,
        closure=closure,
        orientation=orientation,
        edges=edges,
        qc=quality,
        branch_names=np.asarray(BRANCHES),
        pairs=np.asarray(PAIRS, dtype=np.int8),
    )
    print(f"wrote {DERIVED_CACHE}", flush=True)
    print(f"wrote {CONNECTED_CACHE}", flush=True)
    return schema


def replication_verdict(
    base: dict[str, object],
) -> dict[str, object]:
    if not bool(base["eligibility_pass"]):
        label = "INCONCLUSIVE — CROSS-ARCHIVE ELIGIBILITY GATE"
    elif bool(base["routing_pass"]):
        label = (
            "CROSS-ARCHIVE BOUNDARY-CHILD FLOW REPLICATED "
            "INSIDE THIS SIMULATOR FAMILY"
        )
    else:
        label = "CROSS-ARCHIVE BOUNDARY-CHILD FLOW NOT REPLICATED"
    return {**base, "label": label}


def run_test(schema: dict[str, object]) -> None:
    if digest(PROTOCOL, "sha256") != PROTOCOL_SHA256:
        raise RuntimeError("Q34 protocol hash mismatch")
    if digest(FIDELITY, "sha256") != FIDELITY_SHA256:
        raise RuntimeError("Q34 fidelity hash mismatch")
    if digest(ARCHIVE, "md5") != ARCHIVE_MD5:
        raise RuntimeError("Q34 archive hash mismatch")

    derived = np.load(DERIVED_CACHE)
    h_all = np.asarray(derived["closure"], dtype=np.float32)
    edges_all = np.asarray(derived["edges"], dtype=np.int8)
    connected = np.load(CONNECTED_CACHE, mmap_mode="r")
    expected_shapes = {
        "closure": (2, 100, 500, 66),
        "edges": (2, 100, 499, 6, 2),
        "connected": (2, 100, 500, 66, 3, 3),
    }
    observed_shapes = {
        "closure": tuple(h_all.shape),
        "edges": tuple(edges_all.shape),
        "connected": tuple(connected.shape),
    }
    if observed_shapes != expected_shapes:
        raise RuntimeError(
            f"Q34 cache-shape mismatch: {observed_shapes} != {expected_shapes}"
        )

    h_scale = np.quantile(
        np.asarray(h_all[:, :, :250, :], dtype=np.float64),
        0.95,
        axis=2,
    )
    z_all = np.divide(
        h_all,
        h_scale[:, :, None, :],
        out=np.full(h_all.shape, np.nan, dtype=np.float32),
        where=h_scale[:, :, None, :] > core.EPS,
    )
    energy_all = np.sum(
        np.asarray(connected, dtype=np.float32) ** 2,
        axis=(-2, -1),
        dtype=np.float32,
    )
    energy_scale = np.quantile(
        np.asarray(energy_all[:, :, :250, :], dtype=np.float64),
        0.95,
        axis=2,
    )

    all_rows: list[dict[str, object]] = []
    summaries: dict[str, object] = {}
    for split in core.SPLITS:
        rows = core.enumerate_split(
            split,
            h_all,
            z_all,
            h_scale,
            edges_all,
            energy_all,
            energy_scale,
        )
        all_rows.extend(rows)
        summaries[split] = core.summarize(rows)
    evaluation_rows = [
        row for row in all_rows if str(row["split"]) == "evaluation"
    ]
    bootstraps = {
        comparator: core.cluster_bootstrap(evaluation_rows, comparator)
        for comparator in core.COMPARATORS
    }
    base_verdict = core.frozen_verdict(
        summaries["evaluation"],
        bootstraps,
    )
    verdict = replication_verdict(base_verdict)

    q33b_comparison: dict[str, object] = {}
    q33b_path = HERE / "Q33B_ARA_FIRST_BOUNDARY_CHILD_RESULTS.json"
    if q33b_path.exists():
        q33b = json.loads(q33b_path.read_text(encoding="utf-8"))
        prior = q33b["splits"]["evaluation"]["routes"]["exact"]
        current = summaries["evaluation"]["routes"]["exact"]
        q33b_comparison = {
            "q33b_positive_fraction": prior["positive_fraction"],
            "q34_positive_fraction": current["positive_fraction"],
            "positive_fraction_delta": (
                float(current["positive_fraction"])
                - float(prior["positive_fraction"])
            ),
            "q33b_median_flow": prior["flow"]["median"],
            "q34_median_flow": current["flow"]["median"],
            "median_flow_delta": (
                float(current["flow"]["median"])
                - float(prior["flow"]["median"])
            ),
        }

    hashes = {
        "protocol_sha256": digest(PROTOCOL, "sha256"),
        "fidelity_sha256": digest(FIDELITY, "sha256"),
        "archive_md5": digest(ARCHIVE, "md5"),
        "source_hdf_sha256": digest(SOURCE, "sha256"),
        "derived_cache_sha256": digest(DERIVED_CACHE, "sha256"),
        "connected_cache_sha256": digest(CONNECTED_CACHE, "sha256"),
    }
    quality = np.asarray(derived["qc"], dtype=np.float64)
    output = {
        "test_id": TEST_ID,
        "date": "2026-07-26",
        "status": "complete",
        "source_status": (
            "archive selected and protocol frozen before target numerical "
            "inspection"
        ),
        "source": {
            "doi": DOI,
            "archive": ARCHIVE_NAME,
            "connectivity_identity": "pure_greedy",
            "schema": schema,
            "shapes": observed_shapes,
        },
        "hashes": hashes,
        "data_quality": {
            "maximum_trace_error": float(np.max(quality[:, :, 0])),
            "maximum_hermiticity_error": float(np.max(quality[:, :, 1])),
            "minimum_sampled_eigenvalue": float(np.min(quality[:, :, 2])),
            "sampled_psd_failures": int(np.sum(quality[:, :, 3])),
            "sampled_density_matrices": int(np.sum(quality[:, :, 4])),
            "maximum_sampled_off_diagonal_connected": float(
                np.max(
                    np.abs(
                        np.asarray(connected[:, :, ::124, :, :, :])
                        * (
                            1.0
                            - np.eye(3, dtype=np.float32)[
                                None, None, None, None, :, :
                            ]
                        )
                    )
                )
            ),
        },
        "geometry": {
            "generator": "ARA fixed structural route inherited from Q33B",
            "child_local_identity": 1.0,
            "octave_projection": 0.5,
            "vertical_leg": 1.5,
            "complete_path": 3.5,
            "scored_as_outcome": False,
        },
        "splits": summaries,
        "evaluation_bootstrap": bootstraps,
        "q33b_comparison": q33b_comparison,
        "frozen_verdict": verdict,
        "evidence_fence": (
            "The fixed Q33B route is tested on a preregistered untouched "
            "simulator archive. Only subsequent closure flow is scored."
        ),
    }
    RESULTS.write_text(
        json.dumps(core.json_safe(output), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    core.write_rows(EVENTS, all_rows)
    core.write_rows(TRIALS, core.trial_rows(evaluation_rows))
    core.FIGURE_PNG = FIGURE_PNG
    core.FIGURE_SVG = FIGURE_SVG
    core.FIGURE_TITLE = (
        "Q34 — fixed ARA boundary route on untouched pure-greedy archive"
    )
    core.plot_results(
        evaluation_rows,
        summaries["evaluation"],
        verdict["label"],
    )
    print(
        json.dumps(
            core.json_safe(
                {
                    "verdict": verdict["label"],
                    "events": summaries["evaluation"]["source_events"],
                    "strata": summaries["evaluation"]["branch_seed_strata"],
                    "routes": summaries["evaluation"]["routes"],
                    "paired_differences": summaries["evaluation"][
                        "paired_differences"
                    ],
                    "bootstraps": bootstraps,
                    "gates": verdict,
                    "q33b_comparison": q33b_comparison,
                    "hashes": hashes,
                }
            ),
            indent=2,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=("prepare", "run", "all"),
        nargs="?",
        default="all",
    )
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    if args.command == "prepare":
        schema = build_caches(args.workers)
        print(json.dumps(schema, indent=2))
        return
    if args.command == "run":
        if not DERIVED_CACHE.exists() or not CONNECTED_CACHE.exists():
            raise RuntimeError("Run Q34 prepare before Q34 run")
        schema = inspect_schema()
        run_test(schema)
        return
    schema = build_caches(args.workers)
    run_test(schema)


if __name__ == "__main__":
    main()
