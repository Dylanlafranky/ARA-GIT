"""Independent validation of Q46 saved outputs and raw parent decomposition."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import os
import pathlib
import sys
from collections import defaultdict


HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / "public_data" / "_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))

import h5py
import numpy as np

import q40_return_flow_relation_reversal_test as base
import q44_ara_mixing_prediction_test as q44


PROTOCOL = HERE / "Q46_DOUBLE_PARENT_INTERNAL_ARA_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA256 = (
    "0f7b271c5c4df9614dc553b71e3d08004c1dfdf986835f6c8c2ba83928f7ee86"
)
RESULTS = HERE / "Q46_DOUBLE_PARENT_INTERNAL_ARA_RESULTS.json"
WINDOWS = HERE / "Q46_DOUBLE_PARENT_INTERNAL_ARA_WINDOWS.csv.gz"
VALIDATION = HERE / "Q46_DOUBLE_PARENT_INTERNAL_ARA_VALIDATION.json"
FIGURE_PNG = HERE / "Q46_DOUBLE_PARENT_INTERNAL_ARA_DIAGNOSTICS.png"
FIGURE_SVG = HERE / "Q46_DOUBLE_PARENT_INTERNAL_ARA_DIAGNOSTICS.svg"
EPS = 1e-12


def digest(path: pathlib.Path, algorithm: str) -> str:
    value = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def load_rows() -> list[dict]:
    numeric = {
        "seed",
        "pair",
        "start",
        "parent_phase_radians",
        "parent_phase_quadrant",
        "native_path_p1",
        "native_path_p2",
        "native_share_p1",
        "native_share_p2",
        "native_ara_x1",
        "native_ara_x2",
        "native_ridge_distance",
        "lifted_share_p1",
        "lifted_share_p2",
        "lifted_share_other",
        "local_product_path",
        "connected_child_path",
        "double_parent_share_local",
        "double_parent_share_connected",
        "product_rule_max_error",
    }
    with gzip.open(WINDOWS, "rt", newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    for row in rows:
        for field in numeric:
            row[field] = float(row[field])
    return rows


def seed_median(rows: list[dict], field: str) -> float:
    grouped: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        grouped[int(row["seed"])].append(float(row[field]))
    values = [float(np.mean(items)) for items in grouped.values()]
    return float(np.median(values))


def raw_spot_check(rows: list[dict]) -> dict:
    selected = [rows[0], rows[len(rows) // 2], rows[-1]]
    connected = np.load(q44.CONNECTED, mmap_mode="r")
    max_difference = 0.0
    checked = 0
    with h5py.File(q44.SOURCE, "r") as handle:
        for row in selected:
            seed = int(row["seed"])
            pair = int(row["pair"])
            start = int(row["start"])
            name = base.PAIR_NAMES[pair]
            root = handle[q44.locate_trial(handle, seed)]["two_qubit_dms"]
            rhos = np.stack(
                [root[str(t)][name][()] for t in range(start, start + 16)]
            ).astype(np.complex128)
            expectation = np.einsum(
                "nij,kji->nk", rhos, base.OPS, optimize=True
            ).real
            a = expectation[:, :3]
            b = expectation[:, 3:6]
            da = np.diff(a, axis=0)
            db = np.diff(b, axis=0)
            d1 = da[:, :, None] * b[:-1, None, :]
            d2 = a[:-1, :, None] * db[:, None, :]
            dx = da[:, :, None] * db[:, None, :]
            local = a[:, :, None] * b[:, None, :]
            dl = np.diff(local, axis=0)
            max_difference = max(
                max_difference,
                float(np.max(np.abs(dl - (d1 + d2 + dx)))),
            )

            pa = float(np.sum(np.linalg.norm(da, axis=1)))
            pb = float(np.sum(np.linalg.norm(db, axis=1)))
            share = pa / (pa + pb)
            max_difference = max(
                max_difference,
                abs(share - float(row["native_share_p1"])),
            )

            dc = np.diff(
                np.asarray(
                    connected[seed, start : start + 16, pair],
                    dtype=np.float64,
                ),
                axis=0,
            )
            path_l = float(
                np.sum(np.linalg.norm(dl.reshape(15, -1), axis=1))
            )
            path_c = float(
                np.sum(np.linalg.norm(dc.reshape(15, -1), axis=1))
            )
            connected_share = path_c / (path_l + path_c)
            max_difference = max(
                max_difference,
                abs(
                    connected_share
                    - float(row["double_parent_share_connected"])
                ),
            )
            checked += 1
    return {"windows": checked, "maximum_difference": max_difference}


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    rows = load_rows()
    numeric_values = [
        float(value)
        for row in rows
        for field, value in row.items()
        if field not in {"pair_name", "family"} and isinstance(value, float)
    ]

    native_share = seed_median(rows, "native_share_p1")
    ridge_distance = seed_median(rows, "native_ridge_distance")
    lifted_one = seed_median(rows, "lifted_share_p1")
    lifted_two = seed_median(rows, "lifted_share_p2")
    lifted_other = seed_median(rows, "lifted_share_other")
    local_share = seed_median(rows, "double_parent_share_local")
    connected_share = seed_median(rows, "double_parent_share_connected")
    saved = result["metrics"]

    point_differences = {
        "native_parent1_share": abs(
            native_share - saved["native_parent1_share"]["estimate"]
        ),
        "native_ridge_distance": abs(
            ridge_distance - saved["native_ridge_distance"]["estimate"]
        ),
        "lifted_parent1_share": abs(
            lifted_one - saved["lifted_parent1_share"]["estimate"]
        ),
        "lifted_parent2_share": abs(
            lifted_two - saved["lifted_parent2_share"]["estimate"]
        ),
        "lifted_other_share": abs(
            lifted_other - saved["lifted_other_share"]["estimate"]
        ),
        "double_parent_local_share": abs(
            local_share - saved["double_parent_local_share"]["estimate"]
        ),
        "double_parent_connected_share": abs(
            connected_share
            - saved["double_parent_connected_share"]["estimate"]
        ),
    }

    share_sum_error = max(
        abs(float(row["native_share_p1"]) + float(row["native_share_p2"]) - 1)
        for row in rows
    )
    lifted_sum_error = max(
        abs(
            float(row["lifted_share_p1"])
            + float(row["lifted_share_p2"])
            + float(row["lifted_share_other"])
            - 1
        )
        for row in rows
    )
    swap_error = max(
        abs(
            abs(2 * float(row["native_share_p1"]) - 1)
            - abs(2 * float(row["native_share_p2"]) - 1)
        )
        for row in rows
    )
    raw = raw_spot_check(rows)

    checks = {
        "protocol_hash_matches": digest(PROTOCOL, "sha256")
        == PROTOCOL_SHA256,
        "archive_hash_matches": digest(q44.ARCHIVE, "md5")
        == q44.ARCHIVE_MD5,
        "window_count_matches": len(rows) == result["scope"]["windows"] == 1264,
        "lineage_count_matches": len(
            {(int(row["seed"]), int(row["pair"])) for row in rows}
        )
        == result["scope"]["lineages"]
        == 79,
        "seed_count_matches": len({int(row["seed"]) for row in rows})
        == result["scope"]["seeds"]
        == 17,
        "no_nonfinite_values": bool(np.all(np.isfinite(numeric_values))),
        "point_summaries_recompute": max(point_differences.values()) <= 1e-12,
        "native_shares_close": share_sum_error <= 1e-12,
        "lifted_shares_close": lifted_sum_error <= 1e-12,
        "swap_invariance_holds": swap_error <= 1e-12,
        "product_rule_holds": result["maximum_product_rule_error"] <= 1e-12,
        "raw_spot_check_matches": raw["maximum_difference"] <= 1e-12,
        "forty_two_is_accounting_complement": abs(
            result["q45_recomputed_connected_child_share"]["estimate"]
            - (1 - result["metrics"]["double_parent_local_share"]["estimate"])
        )
        <= 1e-8,
        "figure_png_exists": FIGURE_PNG.exists(),
        "figure_svg_exists": FIGURE_SVG.exists(),
    }
    validation = {
        "test_id": result["test_id"],
        "passed": all(checks.values()),
        "checks": checks,
        "maximum_point_summary_difference": max(point_differences.values()),
        "maximum_native_share_sum_error": share_sum_error,
        "maximum_lifted_share_sum_error": lifted_sum_error,
        "maximum_swap_invariance_error": swap_error,
        "raw_spot_check": raw,
        "interpretive_warning": (
            "The pooled P1 share is near 0.5, but the orientation-free "
            "within-window ridge distance is substantial. The result is a "
            "coarse parent ridge with unresolved internal asymmetry, not "
            "universal pointwise equality."
        ),
    }
    VALIDATION.write_text(
        json.dumps(validation, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, indent=2))
    if not validation["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
