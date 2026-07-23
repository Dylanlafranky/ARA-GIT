"""Run the invalidated, uncollocated MX10 v1 test (audit trail only)."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import h5py
import numpy as np


DEVELOPMENT = tuple(range(255, 321, 5))
QUARANTINE = tuple(range(325, 351, 5))
TEST = tuple(range(355, 401, 5))
PAIRS = (("x", "y"), ("y", "z"), ("z", "x"))
RUNGS = (1, 2, 4, 8, 16)
BOOTSTRAP_SEED = 20260723
BOOTSTRAP_REPLICATES = 5_000


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_components(path: Path, iteration: int) -> dict[str, np.ndarray]:
    with h5py.File(path, "r") as handle:
        group = handle[f"data/{iteration}/fields/E"]
        output = {}
        for component in ("x", "y", "z"):
            dataset = group[component]
            output[component] = (
                dataset[...].astype(np.float64)
                * float(dataset.attrs.get("unitSI", 1.0))
            )
    if len({array.shape for array in output.values()}) != 1:
        raise ValueError(f"Component shape mismatch in {path}")
    return output


def centered_crop(array: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    starts = tuple((old - new) // 2 for old, new in zip(array.shape, shape))
    if any(start < 0 for start in starts):
        raise ValueError(f"Cannot crop {array.shape} to {shape}")
    return array[
        starts[0] : starts[0] + shape[0],
        starts[1] : starts[1] + shape[1],
    ]


def block_state_radius(a: np.ndarray, b: np.ndarray, width: int) -> float:
    """Activity-weighted mean MX9 state radius across square blocks."""
    if a.shape != b.shape or a.ndim != 2:
        raise ValueError("Expected two equally shaped 2-D component planes")
    ny = (a.shape[0] // width) * width
    nx = (a.shape[1] // width) * width
    if ny == 0 or nx == 0:
        raise ValueError(f"Rung {width} does not fit shape {a.shape}")
    a = a[:ny, :nx]
    b = b[:ny, :nx]
    shape = (ny // width, width, nx // width, width)
    aa = np.mean(a.reshape(shape) ** 2, axis=(1, 3))
    bb = np.mean(b.reshape(shape) ** 2, axis=(1, 3))
    ab = np.mean((a * b).reshape(shape), axis=(1, 3))
    activity = aa + bb
    numerator = np.sqrt((2.0 * ab) ** 2 + (bb - aa) ** 2)
    total_activity = float(np.sum(activity))
    if not np.isfinite(total_activity) or total_activity <= 0.0:
        raise ValueError("Plane has no finite positive two-channel activity")
    value = float(np.sum(numerator) / total_activity)
    if value < -1e-12 or value > 1.0 + 1e-10:
        raise AssertionError(f"State radius outside [0,1]: {value}")
    return float(np.clip(value, 0.0, 1.0))


def warp_observations(source_dir: Path, iterations: tuple[int, ...], split: str) -> list[dict]:
    observations = []
    for iteration in iterations:
        path = source_dir / f"data{iteration:08d}.h5"
        fields = load_components(path, iteration)
        fields = {
            name: centered_crop(array, (48, 192))
            for name, array in fields.items()
        }
        for first, second in PAIRS:
            pair = f"{first}{second}"
            for width in RUNGS:
                observations.append(
                    {
                        "dataset": "warp",
                        "split": split,
                        "unit": str(iteration),
                        "pair": pair,
                        "rung": width,
                        "D": block_state_radius(fields[first], fields[second], width),
                    }
                )
    return observations


def picongpu_observations(path: Path) -> list[dict]:
    fields = load_components(path, 200)
    observations = []
    for normal_axis in range(3):
        for index in range(fields["x"].shape[normal_axis]):
            planes = {
                name: np.take(array, index, axis=normal_axis)
                for name, array in fields.items()
            }
            unit = f"axis{normal_axis}:{index:02d}"
            for first, second in PAIRS:
                pair = f"{first}{second}"
                for width in RUNGS:
                    observations.append(
                        {
                            "dataset": "picongpu",
                            "split": "external",
                            "unit": unit,
                            "pair": pair,
                            "rung": width,
                            "D": block_state_radius(
                                planes[first], planes[second], width
                            ),
                        }
                    )
    return observations


def fit_beta(rows: list[dict], pair: str | None = None) -> float:
    selected = [
        row["D"]
        for row in rows
        if row["rung"] == 2 and (pair is None or row["pair"] == pair)
    ]
    if not selected:
        raise ValueError("No rung-2 observations for beta fit")
    return float(-np.mean(np.log(selected)) / math.log(2.0))


def predictions(rows: list[dict], beta: float, beta_by_pair: dict[str, float]) -> list[dict]:
    d2 = {
        (row["dataset"], row["unit"], row["pair"]): row["D"]
        for row in rows
        if row["rung"] == 2
    }
    output = []
    for row in rows:
        width = row["rung"]
        if width == 1:
            continue
        record = dict(row)
        record["prediction"] = {
            "common": width ** (-beta),
            "flat": 1.0,
            "independent_2d": width ** (-1.0),
            "pair_specific": width ** (-beta_by_pair[row["pair"]]),
        }
        if width >= 4:
            local_d2 = d2[(row["dataset"], row["unit"], row["pair"])]
            local_beta = -math.log(local_d2) / math.log(2.0)
            record["prediction"]["local_one_step"] = width ** (-local_beta)
        output.append(record)
    return output


def model_metrics(rows: list[dict], model: str, minimum_rung: int = 2) -> dict:
    selected = [
        row
        for row in rows
        if row["rung"] >= minimum_rung and model in row["prediction"]
    ]
    errors = np.asarray(
        [
            abs(math.log(row["prediction"][model]) - math.log(row["D"]))
            for row in selected
        ],
        dtype=float,
    )
    apes = np.asarray(
        [
            abs(row["prediction"][model] - row["D"]) / row["D"]
            for row in selected
        ],
        dtype=float,
    )
    signed = np.asarray(
        [
            math.log(row["prediction"][model]) - math.log(row["D"])
            for row in selected
        ],
        dtype=float,
    )
    return {
        "n": int(len(selected)),
        "mean_absolute_log_error": float(np.mean(errors)),
        "median_absolute_percentage_error": float(np.median(apes)),
        "mean_signed_log_error": float(np.mean(signed)),
    }


def metrics_bundle(rows: list[dict]) -> dict:
    models = ("common", "flat", "independent_2d", "pair_specific")
    return {
        "rungs_2_to_16": {
            model: model_metrics(rows, model, 2)
            for model in models
        },
        "rungs_4_to_16": {
            model: model_metrics(rows, model, 4)
            for model in models + ("local_one_step",)
        },
        "by_rung_common": {
            str(width): model_metrics(
                [row for row in rows if row["rung"] == width], "common", width
            )
            for width in (2, 4, 8, 16)
        },
        "by_pair_common": {
            pair: model_metrics(
                [row for row in rows if row["pair"] == pair], "common", 2
            )
            for pair in ("xy", "yz", "zx")
        },
    }


def bootstrap_beta(development: list[dict], rng: np.random.Generator) -> dict:
    units = sorted({row["unit"] for row in development})
    grouped = defaultdict(list)
    for row in development:
        if row["rung"] == 2:
            grouped[row["unit"]].append(row)
    values = []
    for _ in range(BOOTSTRAP_REPLICATES):
        sample_units = rng.choice(units, size=len(units), replace=True)
        sample = [row for unit in sample_units for row in grouped[unit]]
        values.append(fit_beta(sample))
    low, high = np.quantile(values, [0.025, 0.975])
    return {
        "replicates": BOOTSTRAP_REPLICATES,
        "unit": "Warp iteration",
        "ci95": [float(low), float(high)],
    }


def bootstrap_common_male(rows: list[dict], rng: np.random.Generator) -> dict:
    units = sorted({row["unit"] for row in rows})
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["unit"]].append(row)
    values = []
    for _ in range(BOOTSTRAP_REPLICATES):
        sample_units = rng.choice(units, size=len(units), replace=True)
        sample = [row for unit in sample_units for row in grouped[unit]]
        values.append(
            model_metrics(sample, "common", 2)["mean_absolute_log_error"]
        )
    low, high = np.quantile(values, [0.025, 0.975])
    return {
        "replicates": BOOTSTRAP_REPLICATES,
        "resampling_unit": "iteration" if rows[0]["dataset"] == "warp" else "plane",
        "ci95": [float(low), float(high)],
    }


def evaluate_decision(metrics: dict, external: bool) -> dict:
    all_rungs = metrics["rungs_2_to_16"]
    large_rungs = metrics["rungs_4_to_16"]
    common = all_rungs["common"]["mean_absolute_log_error"]
    fixed_pass = (
        common < all_rungs["flat"]["mean_absolute_log_error"]
        and common < all_rungs["independent_2d"]["mean_absolute_log_error"]
    )
    local_ratio = (
        large_rungs["common"]["mean_absolute_log_error"]
        / large_rungs["local_one_step"]["mean_absolute_log_error"]
    )
    threshold = 1.25 if external else 1.20
    result = {
        "beats_both_fixed_comparators": bool(fixed_pass),
        "common_to_local_error_ratio": float(local_ratio),
        "local_ratio_threshold": threshold,
        "local_condition": bool(local_ratio <= threshold),
    }
    if not external:
        pair_ratio = (
            common
            / all_rungs["pair_specific"]["mean_absolute_log_error"]
        )
        result["common_to_pair_specific_error_ratio"] = float(pair_ratio)
        result["pair_specific_ratio_threshold"] = 1.10
        result["pair_condition"] = bool(pair_ratio <= 1.10)
        result["pass"] = bool(
            fixed_pass and local_ratio <= threshold and pair_ratio <= 1.10
        )
    else:
        result["pass"] = bool(fixed_pass and local_ratio <= threshold)
    return result


def rung_summary(rows: list[dict]) -> dict:
    output = {}
    for width in RUNGS:
        values = np.asarray([row["D"] for row in rows if row["rung"] == width])
        output[str(width)] = {
            "n": int(len(values)),
            "mean": float(np.mean(values)),
            "median": float(np.median(values)),
            "minimum": float(np.min(values)),
            "maximum": float(np.max(values)),
        }
    return output


def run(warp_dir: Path, picongpu_path: Path) -> dict:
    expected = DEVELOPMENT + QUARANTINE + TEST
    missing = [
        str(warp_dir / f"data{iteration:08d}.h5")
        for iteration in expected
        if not (warp_dir / f"data{iteration:08d}.h5").exists()
    ]
    if not picongpu_path.exists():
        missing.append(str(picongpu_path))
    if missing:
        raise FileNotFoundError("Missing source files: " + ", ".join(missing))

    development = warp_observations(warp_dir, DEVELOPMENT, "development")
    heldout_raw = warp_observations(warp_dir, TEST, "heldout")
    external_raw = picongpu_observations(picongpu_path)

    beta = fit_beta(development)
    beta_by_pair = {pair: fit_beta(development, pair) for pair in ("xy", "yz", "zx")}
    heldout = predictions(heldout_raw, beta, beta_by_pair)
    external = predictions(external_raw, beta, beta_by_pair)
    development_pred = predictions(development, beta, beta_by_pair)

    development_metrics = metrics_bundle(development_pred)
    heldout_metrics = metrics_bundle(heldout)
    external_metrics = metrics_bundle(external)
    internal_decision = evaluate_decision(heldout_metrics, external=False)
    external_decision = evaluate_decision(external_metrics, external=True)
    if internal_decision["pass"] and external_decision["pass"]:
        verdict = "strong_cross_rung_support"
    elif internal_decision["pass"]:
        verdict = "partial_support_internal_only"
    else:
        verdict = "not_supported_as_one_transferable_law"

    rng = np.random.default_rng(BOOTSTRAP_SEED)
    warp_hashes = {
        str(iteration): sha256(warp_dir / f"data{iteration:08d}.h5")
        for iteration in expected
    }
    return {
        "protocol": {
            "name": "MX10_CROSS_RUNG_STATE_CONTRACTION",
            "version": "1.0",
            "freeze_date": "2026-07-23",
            "rungs": list(RUNGS),
            "pairs": ["xy", "yz", "zx"],
            "bootstrap_seed": BOOTSTRAP_SEED,
        },
        "sources": {
            "warp": {
                "directory": str(warp_dir.resolve()),
                "development_iterations": list(DEVELOPMENT),
                "quarantine_iterations_not_scored": list(QUARANTINE),
                "heldout_iterations": list(TEST),
                "raw_shape": [51, 201],
                "crop_shape": [48, 192],
                "sha256": warp_hashes,
            },
            "picongpu": {
                "path": str(picongpu_path.resolve()),
                "iteration": 200,
                "raw_shape": [32, 32, 32],
                "planes": 96,
                "sha256": sha256(picongpu_path),
            },
        },
        "fit": {
            "common_beta_from_development_rung_2_only": beta,
            "pair_specific_beta_from_development_rung_2_only": beta_by_pair,
            "common_beta_bootstrap": bootstrap_beta(development, rng),
        },
        "summaries": {
            "development": rung_summary(development),
            "heldout_warp": rung_summary(heldout_raw),
            "external_picongpu": rung_summary(external_raw),
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
            "internal": internal_decision,
            "external": external_decision,
            "verdict": verdict,
        },
        "observations": {
            "development": development,
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
