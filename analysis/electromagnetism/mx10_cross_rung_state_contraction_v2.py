"""Run the frozen, collocation-corrected MX10 v2 test."""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import h5py
import numpy as np

import mx10_cross_rung_state_contraction_v1_invalid as base


WARP_RUNGS = (1, 2, 4, 8, 16)
EXTERNAL_RUNGS = (1, 2, 4, 8)


def collocate_half_cell(
    fields: dict[str, np.ndarray],
    positions: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    """Linearly collocate staggered components to offset 0.5 on every axis."""
    ndim = next(iter(fields.values())).ndim
    target_shape = tuple(size - 1 for size in next(iter(fields.values())).shape)
    output = {}
    for name, original in fields.items():
        array = np.asarray(original, dtype=np.float64)
        position = np.asarray(positions[name], dtype=float)
        if len(position) != ndim:
            raise ValueError(f"Position dimensionality mismatch for {name}")
        for axis, offset in enumerate(position):
            if np.isclose(offset, 0.0):
                lower = [slice(None)] * ndim
                upper = [slice(None)] * ndim
                lower[axis] = slice(0, -1)
                upper[axis] = slice(1, None)
                array = 0.5 * (array[tuple(lower)] + array[tuple(upper)])
            elif not np.isclose(offset, 0.5):
                raise ValueError(f"Unsupported stagger offset {offset} for {name}")
        slices = tuple(slice(0, size) for size in target_shape)
        output[name] = array[slices]
    if len({array.shape for array in output.values()}) != 1:
        raise AssertionError("Collocated components do not share one shape")
    return output


def load_collocated(path: Path, iteration: int) -> dict[str, np.ndarray]:
    with h5py.File(path, "r") as handle:
        group = handle[f"data/{iteration}/fields/E"]
        fields = {}
        positions = {}
        for component in ("x", "y", "z"):
            dataset = group[component]
            fields[component] = (
                dataset[...].astype(np.float64)
                * float(dataset.attrs.get("unitSI", 1.0))
            )
            positions[component] = np.asarray(dataset.attrs["position"], dtype=float)
    return collocate_half_cell(fields, positions)


def warp_observations(
    source_dir: Path,
    iterations: tuple[int, ...],
    split: str,
) -> list[dict]:
    observations = []
    for iteration in iterations:
        path = source_dir / f"data{iteration:08d}.h5"
        fields = {
            name: base.centered_crop(array, (48, 192))
            for name, array in load_collocated(path, iteration).items()
        }
        for first, second in base.PAIRS:
            pair = f"{first}{second}"
            for width in WARP_RUNGS:
                observations.append(
                    {
                        "dataset": "warp",
                        "split": split,
                        "unit": str(iteration),
                        "pair": pair,
                        "rung": width,
                        "D": base.block_state_radius(
                            fields[first], fields[second], width
                        ),
                    }
                )
    return observations


def picongpu_observations(path: Path) -> list[dict]:
    fields_3d = load_collocated(path, 200)
    observations = []
    for normal_axis in range(3):
        for index in range(fields_3d["x"].shape[normal_axis]):
            planes = {
                name: base.centered_crop(
                    np.take(array, index, axis=normal_axis), (24, 24)
                )
                for name, array in fields_3d.items()
            }
            unit = f"axis{normal_axis}:{index:02d}"
            for first, second in base.PAIRS:
                pair = f"{first}{second}"
                for width in EXTERNAL_RUNGS:
                    observations.append(
                        {
                            "dataset": "picongpu",
                            "split": "external",
                            "unit": unit,
                            "pair": pair,
                            "rung": width,
                            "D": base.block_state_radius(
                                planes[first], planes[second], width
                            ),
                        }
                    )
    return observations


def metrics_bundle(rows: list[dict], rungs: tuple[int, ...]) -> dict:
    models = ("common", "flat", "independent_2d", "pair_specific")
    larger = tuple(width for width in rungs if width >= 4)
    return {
        "all_scored_rungs": {
            model: base.model_metrics(rows, model, 2)
            for model in models
        },
        "larger_rungs": {
            model: base.model_metrics(rows, model, 4)
            for model in models + ("local_one_step",)
        },
        "by_rung_common": {
            str(width): base.model_metrics(
                [row for row in rows if row["rung"] == width], "common", width
            )
            for width in rungs
            if width >= 2
        },
        "by_pair_common": {
            pair: base.model_metrics(
                [row for row in rows if row["pair"] == pair], "common", 2
            )
            for pair in ("xy", "yz", "zx")
        },
        "larger_rungs_included": list(larger),
    }


def evaluate_decision(metrics: dict, external: bool) -> dict:
    all_rungs = metrics["all_scored_rungs"]
    larger = metrics["larger_rungs"]
    common = all_rungs["common"]["mean_absolute_log_error"]
    fixed_pass = (
        common < all_rungs["flat"]["mean_absolute_log_error"]
        and common < all_rungs["independent_2d"]["mean_absolute_log_error"]
    )
    local_ratio = (
        larger["common"]["mean_absolute_log_error"]
        / larger["local_one_step"]["mean_absolute_log_error"]
    )
    threshold = 1.25 if external else 1.20
    result = {
        "beats_both_fixed_comparators": bool(fixed_pass),
        "common_to_local_error_ratio": float(local_ratio),
        "local_ratio_threshold": threshold,
        "local_condition": bool(local_ratio <= threshold),
    }
    if external:
        result["pass"] = bool(fixed_pass and local_ratio <= threshold)
    else:
        pair_ratio = (
            common / all_rungs["pair_specific"]["mean_absolute_log_error"]
        )
        result.update(
            {
                "common_to_pair_specific_error_ratio": float(pair_ratio),
                "pair_specific_ratio_threshold": 1.10,
                "pair_condition": bool(pair_ratio <= 1.10),
                "pass": bool(
                    fixed_pass
                    and local_ratio <= threshold
                    and pair_ratio <= 1.10
                ),
            }
        )
    return result


def rung_summary(rows: list[dict], rungs: tuple[int, ...]) -> dict:
    output = {}
    for width in rungs:
        values = np.asarray([row["D"] for row in rows if row["rung"] == width])
        output[str(width)] = {
            "n": int(len(values)),
            "mean": float(np.mean(values)),
            "median": float(np.median(values)),
            "minimum": float(np.min(values)),
            "maximum": float(np.max(values)),
        }
    return output


def bootstrap_common_male(
    rows: list[dict], rng: np.random.Generator
) -> dict:
    units = sorted({row["unit"] for row in rows})
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["unit"]].append(row)
    values = []
    for _ in range(base.BOOTSTRAP_REPLICATES):
        sample_units = rng.choice(units, size=len(units), replace=True)
        sample = [row for unit in sample_units for row in grouped[unit]]
        values.append(
            base.model_metrics(sample, "common", 2)[
                "mean_absolute_log_error"
            ]
        )
    low, high = np.quantile(values, [0.025, 0.975])
    return {
        "replicates": base.BOOTSTRAP_REPLICATES,
        "resampling_unit": "iteration" if rows[0]["dataset"] == "warp" else "plane",
        "ci95": [float(low), float(high)],
    }


def run(warp_dir: Path, picongpu_path: Path) -> dict:
    expected = base.DEVELOPMENT + base.QUARANTINE + base.TEST
    missing = [
        str(warp_dir / f"data{iteration:08d}.h5")
        for iteration in expected
        if not (warp_dir / f"data{iteration:08d}.h5").exists()
    ]
    if not picongpu_path.exists():
        missing.append(str(picongpu_path))
    if missing:
        raise FileNotFoundError("Missing source files: " + ", ".join(missing))

    development = warp_observations(warp_dir, base.DEVELOPMENT, "development")
    heldout_raw = warp_observations(warp_dir, base.TEST, "heldout")
    external_raw = picongpu_observations(picongpu_path)

    beta = base.fit_beta(development)
    beta_by_pair = {
        pair: base.fit_beta(development, pair) for pair in ("xy", "yz", "zx")
    }
    development_pred = base.predictions(development, beta, beta_by_pair)
    heldout = base.predictions(heldout_raw, beta, beta_by_pair)
    external = base.predictions(external_raw, beta, beta_by_pair)

    development_metrics = metrics_bundle(development_pred, WARP_RUNGS)
    heldout_metrics = metrics_bundle(heldout, WARP_RUNGS)
    external_metrics = metrics_bundle(external, EXTERNAL_RUNGS)
    internal = evaluate_decision(heldout_metrics, external=False)
    external_decision = evaluate_decision(external_metrics, external=True)
    if internal["pass"] and external_decision["pass"]:
        verdict = "strong_cross_rung_support"
    elif internal["pass"]:
        verdict = "partial_support_internal_only"
    else:
        verdict = "not_supported_as_one_transferable_law"

    rng = np.random.default_rng(base.BOOTSTRAP_SEED)
    return {
        "protocol": {
            "name": "MX10_CROSS_RUNG_STATE_CONTRACTION",
            "version": "2.0",
            "freeze_date": "2026-07-23",
            "warp_rungs": list(WARP_RUNGS),
            "external_rungs": list(EXTERNAL_RUNGS),
            "pairs": ["xy", "yz", "zx"],
            "collocation_target_offset": 0.5,
            "bootstrap_seed": base.BOOTSTRAP_SEED,
        },
        "sources": {
            "warp": {
                "directory": str(warp_dir.resolve()),
                "development_iterations": list(base.DEVELOPMENT),
                "quarantine_iterations_not_scored": list(base.QUARANTINE),
                "heldout_iterations": list(base.TEST),
                "raw_shape": [51, 201],
                "collocated_shape": [50, 200],
                "crop_shape": [48, 192],
                "sha256": {
                    str(iteration): base.sha256(
                        warp_dir / f"data{iteration:08d}.h5"
                    )
                    for iteration in expected
                },
            },
            "picongpu": {
                "path": str(picongpu_path.resolve()),
                "iteration": 200,
                "raw_shape": [32, 32, 32],
                "collocated_shape": [31, 31, 31],
                "plane_crop_shape": [24, 24],
                "planes": 93,
                "sha256": base.sha256(picongpu_path),
            },
        },
        "fit": {
            "common_beta_from_development_rung_2_only": beta,
            "pair_specific_beta_from_development_rung_2_only": beta_by_pair,
            "common_beta_bootstrap": base.bootstrap_beta(development, rng),
        },
        "summaries": {
            "development": rung_summary(development, WARP_RUNGS),
            "heldout_warp": rung_summary(heldout_raw, WARP_RUNGS),
            "external_picongpu": rung_summary(external_raw, EXTERNAL_RUNGS),
        },
        "metrics": {
            "development": development_metrics,
            "heldout_warp": heldout_metrics,
            "external_picongpu": external_metrics,
        },
        "bootstrap": {
            "heldout_common_male": bootstrap_common_male(heldout, rng),
            "external_common_male": bootstrap_common_male(external, rng),
        },
        "decision": {
            "internal": internal,
            "external": external_decision,
            "verdict": verdict,
        },
        "observations": {
            "development": development,
            "heldout_warp": heldout_raw,
            "external_picongpu": external_raw,
        },
        "scored_predictions": {
            "development": development_pred,
            "heldout_warp": heldout,
            "external_picongpu": external,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--warp-dir", type=Path, required=True)
    parser.add_argument("--picongpu", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.warp_dir, args.picongpu)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"fit": result["fit"], "decision": result["decision"]}, indent=2))


if __name__ == "__main__":
    main()
