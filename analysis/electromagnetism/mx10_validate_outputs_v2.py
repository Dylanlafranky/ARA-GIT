"""Independent direct-source validation of selected MX10 v2 outputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import h5py
import numpy as np


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(1_048_576)
            if not block:
                break
            value.update(block)
    return value.hexdigest()


def read_and_align(path: Path, iteration: int) -> dict[str, np.ndarray]:
    raw = {}
    offsets = {}
    with h5py.File(path, "r") as handle:
        electric = handle[f"data/{iteration}/fields/E"]
        for label in ("x", "y", "z"):
            item = electric[label]
            raw[label] = np.asarray(item, dtype=float) * float(
                item.attrs.get("unitSI", 1.0)
            )
            offsets[label] = np.asarray(item.attrs["position"], dtype=float)

    common_shape = tuple(length - 1 for length in raw["x"].shape)
    aligned = {}
    for label in ("x", "y", "z"):
        values = raw[label]
        for dimension, offset in enumerate(offsets[label]):
            if abs(offset) < 1e-12:
                before = np.take(
                    values, np.arange(values.shape[dimension] - 1), axis=dimension
                )
                after = np.take(
                    values, np.arange(1, values.shape[dimension]), axis=dimension
                )
                values = (before + after) / 2.0
            elif abs(offset - 0.5) >= 1e-12:
                raise AssertionError(f"Unexpected offset {offset}")
        aligned[label] = values[tuple(slice(0, n) for n in common_shape)]
    assert len({item.shape for item in aligned.values()}) == 1
    return aligned


def crop_center(values: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    y0 = (values.shape[0] - shape[0]) // 2
    x0 = (values.shape[1] - shape[1]) // 2
    return values[y0 : y0 + shape[0], x0 : x0 + shape[1]]


def direct_radius(first: np.ndarray, second: np.ndarray, width: int) -> float:
    """Deliberately loop over blocks instead of using the production reshape."""
    numerator_total = 0.0
    activity_total = 0.0
    for y0 in range(0, first.shape[0], width):
        for x0 in range(0, first.shape[1], width):
            a = first[y0 : y0 + width, x0 : x0 + width].ravel()
            b = second[y0 : y0 + width, x0 : x0 + width].ravel()
            aa = float(np.dot(a, a) / len(a))
            bb = float(np.dot(b, b) / len(b))
            ab = float(np.dot(a, b) / len(a))
            numerator_total += math.hypot(2.0 * ab, bb - aa)
            activity_total += aa + bb
    return numerator_total / activity_total


def result_lookup(rows: list[dict]) -> dict[tuple[str, str, int], float]:
    return {
        (row["unit"], row["pair"], int(row["rung"])): float(row["D"])
        for row in rows
    }


def validate(results_path: Path) -> dict:
    results = json.loads(results_path.read_text(encoding="utf-8"))
    warp_dir = Path(results["sources"]["warp"]["directory"])
    picongpu = Path(results["sources"]["picongpu"]["path"])
    checks = []

    def record(name: str, passed: bool, detail: dict) -> None:
        checks.append({"name": name, "pass": bool(passed), **detail})

    record(
        "picongpu_source_hash",
        digest(picongpu) == results["sources"]["picongpu"]["sha256"],
        {"path": str(picongpu)},
    )
    for iteration in (255, 320, 355, 400):
        path = warp_dir / f"data{iteration:08d}.h5"
        expected = results["sources"]["warp"]["sha256"][str(iteration)]
        record(
            f"warp_source_hash_{iteration}",
            digest(path) == expected,
            {"path": str(path)},
        )

    warp_lookup = result_lookup(results["observations"]["heldout_warp"])
    warp_fields = read_and_align(warp_dir / "data00000355.h5", 355)
    warp_fields = {
        key: crop_center(value, (48, 192))
        for key, value in warp_fields.items()
    }
    for pair, labels in {"xy": ("x", "y"), "zx": ("z", "x")}.items():
        for width in (1, 4, 16):
            actual = direct_radius(
                warp_fields[labels[0]], warp_fields[labels[1]], width
            )
            expected = warp_lookup[("355", pair, width)]
            record(
                f"warp_355_{pair}_rung_{width}",
                abs(actual - expected) <= 2e-12,
                {
                    "recomputed": actual,
                    "recorded": expected,
                    "absolute_difference": abs(actual - expected),
                },
            )

    external_lookup = result_lookup(results["observations"]["external_picongpu"])
    external_fields = read_and_align(picongpu, 200)
    selected = (
        (0, 7, "xy", ("x", "y")),
        (1, 15, "yz", ("y", "z")),
        (2, 23, "zx", ("z", "x")),
    )
    for axis, index, pair, labels in selected:
        first = crop_center(np.take(external_fields[labels[0]], index, axis=axis), (24, 24))
        second = crop_center(np.take(external_fields[labels[1]], index, axis=axis), (24, 24))
        unit = f"axis{axis}:{index:02d}"
        for width in (2, 8):
            actual = direct_radius(first, second, width)
            expected = external_lookup[(unit, pair, width)]
            record(
                f"picongpu_{unit}_{pair}_rung_{width}",
                abs(actual - expected) <= 2e-12,
                {
                    "recomputed": actual,
                    "recorded": expected,
                    "absolute_difference": abs(actual - expected),
                },
            )

    development_d2 = [
        float(row["D"])
        for row in results["observations"]["development"]
        if int(row["rung"]) == 2
    ]
    beta = -float(np.mean(np.log(development_d2))) / math.log(2.0)
    recorded_beta = float(
        results["fit"]["common_beta_from_development_rung_2_only"]
    )
    record(
        "common_beta_recomputed",
        abs(beta - recorded_beta) <= 2e-15,
        {
            "recomputed": beta,
            "recorded": recorded_beta,
            "absolute_difference": abs(beta - recorded_beta),
        },
    )

    all_observations = (
        results["observations"]["development"]
        + results["observations"]["heldout_warp"]
        + results["observations"]["external_picongpu"]
    )
    bounds_pass = all(
        -1e-12 <= float(row["D"]) <= 1.0 + 1e-12
        for row in all_observations
    )
    boundary_pass = all(
        abs(float(row["D"]) - 1.0) <= 2e-12
        for row in all_observations
        if int(row["rung"]) == 1
    )
    record("all_state_radii_in_unit_interval", bounds_pass, {})
    record("all_one_cell_states_on_boundary", boundary_pass, {})

    return {
        "results_path": str(results_path.resolve()),
        "checks": checks,
        "passed": int(sum(item["pass"] for item in checks)),
        "total": len(checks),
        "all_pass": bool(all(item["pass"] for item in checks)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    validation = validate(args.results)
    args.output.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
