"""Inspect only HDF5 paths, shapes and dtypes for the frozen Q27 adapter."""

from __future__ import annotations

import json
import pathlib
import sys


HERE = pathlib.Path(__file__).resolve().parent
DEPS = HERE / ".q27_deps"
sys.path.insert(0, str(DEPS))

import h5py  # noqa: E402


SOURCE = (
    HERE
    / "public_data"
    / "q27_network_reconstruction"
    / "unnati_submit_12_pure_random.hdf5"
)
OUTPUT = HERE / "Q27_ARA9_NETWORK_RECONSTRUCTION_SCHEMA.json"


def main() -> None:
    branches: list[dict[str, object]] = []
    with h5py.File(SOURCE, "r") as handle:
        root = handle["12 qubits"]
        for connectivity_name in sorted(root):
            seed_root = root[connectivity_name]["unitary energy subspace 1"]
            seed_names = sorted(
                seed_root,
                key=lambda value: int(value.rsplit(" ", 1)[-1]),
            )
            sample = seed_root[seed_names[0]]["ordering seed random"]
            dm_root = sample["two_qubit_dms"]
            time_names = sorted(dm_root, key=int)
            pair_names = sorted(
                dm_root[time_names[0]],
                key=lambda value: tuple(
                    int(part.strip())
                    for part in value.strip("()").split(",")
                ),
            )
            matrix = dm_root[time_names[0]][pair_names[0]]
            connectivity = sample["previous_order"]["orders_list"]["data"]
            branches.append(
                {
                    "connectivity": connectivity_name,
                    "seed_count": len(seed_names),
                    "seed_names": seed_names,
                    "time_count": len(time_names),
                    "time_min": int(time_names[0]),
                    "time_max": int(time_names[-1]),
                    "pair_count": len(pair_names),
                    "pair_names": pair_names,
                    "density_matrix": {
                        "shape": list(matrix.shape),
                        "dtype": str(matrix.dtype),
                        "chunks": (
                            list(matrix.chunks) if matrix.chunks else None
                        ),
                        "compression": matrix.compression,
                    },
                    "connectivity_array": {
                        "path_suffix": "previous_order/orders_list/data",
                        "shape": list(connectivity.shape),
                        "dtype": str(connectivity.dtype),
                    },
                }
            )

    payload = {
        "test_id": "Q27-ARA9-NETWORK-RECONSTRUCTION-v1",
        "source": SOURCE.name,
        "source_sha256": (
            "0e10afb6e5c7bcc3b469a9bb18a9bcae9469bfae165d5da5add93eeeb1972eeb"
        ),
        "inspection_boundary": "paths, shapes, dtypes, chunks and compression only; no values read",
        "root_groups": list(handle.keys()) if False else ["12 qubits"],
        "branches": branches,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"wrote {OUTPUT.name}: {len(branches)} connectivity branches")
    for branch in branches:
        print(
            branch["connectivity"],
            "seeds=", branch["seed_count"],
            "times=", branch["time_count"],
            "pairs=", branch["pair_count"],
            "dm=", branch["density_matrix"],
            "connectivity=", branch["connectivity_array"],
        )


if __name__ == "__main__":
    main()
