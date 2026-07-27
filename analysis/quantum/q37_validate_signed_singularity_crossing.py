"""Independent validation of Q37's frozen signed-crossing test.

This deliberately does not import the primary analysis module. It rebuilds
eligibility, event selection, sampled raw metrics, summaries, bootstraps, gates,
and the final verdict from the sealed caches and exported event table.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
DATA = HERE / "public_data" / "q37_signed_crossing_landmax"
ARCHIVE = DATA / "unnati_submit_12_pure_landmax.hdf5.zip"
HDF = DATA / "unnati_submit_12_pure_landmax.hdf5"
DERIVED = DATA / "q37_derived_cache.npz"
CONNECTED = DATA / "q37_connected_cache.npy"
EVENTS = HERE / "Q37_SIGNED_SINGULARITY_CROSSING_EVENTS.csv.gz"
RESULTS = HERE / "Q37_SIGNED_SINGULARITY_CROSSING_RESULTS.json"
PROTOCOL = HERE / "Q37_SIGNED_SINGULARITY_CROSSING_PROTOCOL_v1_FROZEN.md"
FIDELITY = HERE / "Q37_SIGNED_SINGULARITY_CROSSING_FIDELITY_v1.md"
OUTPUT = HERE / "Q37_SIGNED_SINGULARITY_CROSSING_VALIDATION.json"

EXPECTED = {
    "archive_md5": "ace64ede12cfbc9e5413326f23c306ad",
    "protocol_sha256": "05d590b14751e289796a95e9d156210d51895a21ae11bd332182524a4c4ebe9a",
    "fidelity_sha256": "2d42c57dea506949c760b85893905be86280055338a071d8af7972eb8e63134a",
    "archive_size": 224_191_403,
    "hdf_size": 3_452_715_680,
}

K = np.arange(1, 8, dtype=np.int16)
EVAL_FIRST, EVAL_LAST = 258, 491
TIME_SHIFT = 37
BOOTSTRAP_DRAWS = 20_000
BOOTSTRAP_SEED = 371027
EPS = 1e-12
VARIANTS = ("exact", "time", "pair", "network")


def digest(path: Path, algorithm: str) -> str:
    value = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def circulation(phase: np.ndarray) -> float:
    turn = np.angle(np.conj(phase[:-1]) * phase[1:])
    turn = turn[np.isfinite(turn) & (np.abs(turn) > 1e-10)]
    return float(abs(np.mean(np.sign(turn)))) if turn.size else 0.0


def rebuild_eligibility(closure: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    development = np.asarray(closure[0, :, :250], dtype=np.float64)
    flow = np.diff(development, axis=1)
    lo, hi = np.quantile(development, [0.05, 0.95], axis=1)
    centre = (lo + hi) / 2
    radius = (hi - lo) / 2
    flow_scale = np.quantile(np.abs(flow), 0.95, axis=1)
    u = (development[:, :249] - centre[:, None]) / radius[:, None]
    v = flow / flow_scale[:, None]
    plane = u + 1j * v
    phase = plane / np.abs(plane)
    eligible = np.zeros((100, 66), dtype=bool)
    coherence = np.full((100, 66), np.nan)
    for seed in range(100):
        for pair in range(66):
            line = plane[seed, :, pair]
            valid = np.isfinite(line.real) & np.isfinite(line.imag)
            if np.mean(valid) < 0.95:
                continue
            quadrant = 2 * (line.real[valid] >= 0) + (line.imag[valid] >= 0)
            minimum = min(np.mean(quadrant == q) for q in range(4))
            coherence[seed, pair] = circulation(phase[seed, valid, pair])
            eligible[seed, pair] = minimum >= 0.05 and coherence[seed, pair] >= 0.80
    return eligible, coherence


def selected_times(line: np.ndarray, threshold: float) -> list[int]:
    result: list[int] = []
    for time in range(EVAL_FIRST, EVAL_LAST + 1):
        is_event = (
            line[time - 1] > line[time]
            and line[time] <= line[time + 1]
            and line[time] <= threshold
        )
        if not is_event or (result and time - result[-1] < 7):
            continue
        result.append(time)
    return result


def shifted(time: int) -> int:
    width = EVAL_LAST - EVAL_FIRST + 1
    return EVAL_FIRST + ((time - EVAL_FIRST + TIME_SHIFT) % width)


def raw_metrics(
    branch: int,
    seed: int,
    pair: int,
    time: int,
    closure: np.ndarray,
    orientation: np.ndarray,
    connected: np.ndarray,
) -> dict[str, float]:
    before = np.asarray(connected[branch, seed, time - K, pair], dtype=np.float64)
    after = np.asarray(connected[branch, seed, time + K, pair], dtype=np.float64)
    inner = np.sum(before * after, axis=(-2, -1))
    norms = np.linalg.norm(before, axis=(-2, -1)) * np.linalg.norm(
        after, axis=(-2, -1)
    )

    def coordinate(left: np.ndarray, right: np.ndarray) -> float:
        total = float(np.sum(left) + np.sum(right))
        return float(2 * np.sum(right) / total) if total > EPS else np.nan

    before_amp = np.linalg.norm(before, axis=(-2, -1))
    after_amp = np.linalg.norm(after, axis=(-2, -1))
    before_h = np.asarray(closure[branch, seed, time - K, pair], dtype=np.float64)
    after_h = np.asarray(closure[branch, seed, time + K, pair], dtype=np.float64)
    before_sign = np.asarray(
        orientation[branch, seed, time - K, pair], dtype=np.int8
    )
    after_sign = np.asarray(
        orientation[branch, seed, time + K, pair], dtype=np.int8
    )
    reliable = (before_sign != 0) & (after_sign != 0)
    parity = (
        float(np.mean(before_sign[reliable] != after_sign[reliable]))
        if np.any(reliable)
        else np.nan
    )
    result = {
        "signed_orientation": float(np.sum(inner) / np.sum(norms)),
        "amplitude_x": coordinate(before_amp, after_amp),
        "closure_x": coordinate(before_h, after_h),
        "determinant_parity_flip_fraction": parity,
    }
    for k, value in enumerate(
        np.divide(inner, norms, out=np.full(7, np.nan), where=norms > EPS), 1
    ):
        result[f"signed_k{k}"] = float(value)
    return result


def summarize(frame: pd.DataFrame, variant: str) -> dict[str, object]:
    signed = frame[f"{variant}_signed_orientation"].to_numpy(float)
    amplitude = frame[f"{variant}_amplitude_x"].to_numpy(float)
    closure = frame[f"{variant}_closure_x"].to_numpy(float)
    lineages = frame.groupby(["seed", "source_pair"], sort=True)
    lineage_amplitude = lineages[f"{variant}_amplitude_x"].mean().to_numpy(float)
    lineage_closure = lineages[f"{variant}_closure_x"].mean().to_numpy(float)
    parity = frame[
        f"{variant}_determinant_parity_flip_fraction"
    ].to_numpy(float)
    return {
        "events": int(len(frame)),
        "signed_orientation_median": float(np.median(signed)),
        "signed_orientation_mean": float(np.mean(signed)),
        "signed_negative_fraction": float(np.mean(signed < 0)),
        "amplitude_x_mean": float(np.mean(amplitude)),
        "amplitude_x_median": float(np.median(amplitude)),
        "amplitude_below_ridge_fraction": float(np.mean(amplitude < 1)),
        "amplitude_lineage_mean": float(np.mean(lineage_amplitude)),
        "amplitude_lineages_below_ridge_fraction": float(
            np.mean(lineage_amplitude < 1)
        ),
        "closure_x_mean": float(np.mean(closure)),
        "closure_x_median": float(np.median(closure)),
        "closure_below_ridge_fraction": float(np.mean(closure < 1)),
        "closure_lineage_mean": float(np.mean(lineage_closure)),
        "closure_lineages_below_ridge_fraction": float(
            np.mean(lineage_closure < 1)
        ),
        "determinant_parity_flip_fraction_mean": float(np.mean(parity)),
        "offset_signed_means": [
            float(frame[f"{variant}_signed_k{k}"].mean()) for k in range(1, 8)
        ],
    }


def bootstrap_probability(
    frame: pd.DataFrame,
    exact_key: str,
    control_key: str | None,
    null_value: float = 0.0,
) -> float:
    exact = frame[exact_key].to_numpy(float)
    if control_key is None:
        difference = null_value - exact
    else:
        difference = frame[control_key].to_numpy(float) - exact
    temp = pd.DataFrame({"seed": frame["seed"], "difference": difference})
    clusters = (
        temp[np.isfinite(temp["difference"])]
        .groupby("seed", sort=True)["difference"]
        .mean()
        .to_numpy(float)
    )
    rng = np.random.default_rng(
        BOOTSTRAP_SEED
        + sum(map(ord, exact_key))
        + (sum(map(ord, control_key)) if control_key else 0)
    )
    draws = rng.choice(
        clusters, size=(BOOTSTRAP_DRAWS, clusters.size), replace=True
    ).mean(axis=1)
    return float(np.mean(draws > 0))


def same_float(a: object, b: object, tolerance: float = 1e-11) -> bool:
    try:
        left, right = float(a), float(b)
    except (TypeError, ValueError):
        return a == b
    if np.isnan(left) and np.isnan(right):
        return True
    return bool(np.isclose(left, right, atol=tolerance, rtol=tolerance))


def main() -> None:
    stored = json.loads(RESULTS.read_text(encoding="utf-8"))
    derived = np.load(DERIVED)
    closure = derived["closure"]
    orientation = derived["orientation"]
    connected = np.load(CONNECTED, mmap_mode="r")
    frame = pd.read_csv(EVENTS, compression="gzip")

    provenance = {
        "archive_md5": digest(ARCHIVE, "md5"),
        "protocol_sha256": digest(PROTOCOL, "sha256"),
        "fidelity_sha256": digest(FIDELITY, "sha256"),
        "archive_size": ARCHIVE.stat().st_size,
        "hdf_size": HDF.stat().st_size,
    }
    provenance_pass = provenance == EXPECTED
    shape_pass = (
        closure.shape == (2, 100, 500, 66)
        and orientation.shape == (2, 100, 500, 66)
        and connected.shape == (2, 100, 500, 66, 3, 3)
    )

    eligible, coherence = rebuild_eligibility(closure)
    event_rows: list[tuple[int, int, int]] = []
    represented_seeds: set[int] = set()
    represented_lineages: set[tuple[int, int]] = set()
    for seed in range(100):
        for pair in np.flatnonzero(eligible[seed]):
            pair_controls = [
                int(candidate)
                for candidate in np.flatnonzero(eligible[seed])
                if int(candidate) != int(pair)
            ]
            if not pair_controls:
                continue
            threshold = float(np.quantile(closure[0, seed, :250, pair], 0.20))
            times = selected_times(closure[0, seed, :, pair], threshold)
            for time in times:
                event_rows.append((seed, int(pair), time))
                represented_seeds.add(seed)
                represented_lineages.add((seed, int(pair)))
    exported_rows = list(
        frame[["seed", "source_pair", "time"]].itertuples(index=False, name=None)
    )
    event_selection_pass = event_rows == exported_rows
    eligibility = {
        "complete_c2_lineages": int(np.sum(eligible)),
        "events": len(event_rows),
        "represented_seeds": len(represented_seeds),
        "represented_lineages": len(represented_lineages),
    }
    eligibility_match = eligibility == stored["eligibility"]

    sample_indices = np.unique(
        np.linspace(0, len(frame) - 1, 24, dtype=np.int64)
    )
    sampled_max_error = 0.0
    sampled_checks = 0
    for index in sample_indices:
        row = frame.iloc[int(index)]
        seed, source_pair, time = (
            int(row["seed"]),
            int(row["source_pair"]),
            int(row["time"]),
        )
        specifications = {
            "exact": (0, seed, source_pair, time),
            "time": (0, seed, source_pair, shifted(time)),
            "pair": (0, seed, int(row["pair_control"]), time),
            "network": (1, seed, source_pair, time),
        }
        for variant, spec in specifications.items():
            metrics = raw_metrics(*spec, closure, orientation, connected)
            for metric, value in metrics.items():
                recorded = float(row[f"{variant}_{metric}"])
                if np.isnan(value) and np.isnan(recorded):
                    error = 0.0
                else:
                    error = abs(value - recorded)
                sampled_max_error = max(sampled_max_error, error)
                sampled_checks += 1
    sampled_raw_pass = sampled_max_error <= 1e-11

    summary = {variant: summarize(frame, variant) for variant in VARIANTS}
    summary_checks: list[bool] = []
    for variant in VARIANTS:
        for key, value in summary[variant].items():
            recorded = stored["summary"][variant][key]
            if isinstance(value, list):
                summary_checks.extend(
                    same_float(a, b) for a, b in zip(value, recorded)
                )
            else:
                summary_checks.append(same_float(value, recorded))
    summary_pass = all(summary_checks)

    bootstrap: dict[str, object] = {
        "signed_below_zero": bootstrap_probability(
            frame, "exact_signed_orientation", None, 0.0
        ),
        "signed_vs_controls": {
            v: bootstrap_probability(
                frame, "exact_signed_orientation", f"{v}_signed_orientation"
            )
            for v in ("time", "pair", "network")
        },
        "amplitude_below_ridge": bootstrap_probability(
            frame, "exact_amplitude_x", None, 1.0
        ),
        "closure_below_ridge": bootstrap_probability(
            frame, "exact_closure_x", None, 1.0
        ),
        "amplitude_vs_controls": {
            v: bootstrap_probability(
                frame, "exact_amplitude_x", f"{v}_amplitude_x"
            )
            for v in ("time", "pair", "network")
        },
        "closure_vs_controls": {
            v: bootstrap_probability(
                frame, "exact_closure_x", f"{v}_closure_x"
            )
            for v in ("time", "pair", "network")
        },
    }
    bootstrap_pass = all(
        same_float(bootstrap[key], stored["bootstrap"][key])
        if not isinstance(bootstrap[key], dict)
        else all(
            same_float(value, stored["bootstrap"][key][control])
            for control, value in bootstrap[key].items()
        )
        for key in bootstrap
    )

    exact = summary["exact"]
    eligibility_pass = (
        eligibility["events"] >= 2000
        and eligibility["represented_seeds"] >= 80
        and eligibility["represented_lineages"] >= 500
    )
    signed_gates = {
        "median_le_minus_0_25": exact["signed_orientation_median"] <= -0.25,
        "negative_fraction_ge_0_60": exact["signed_negative_fraction"] >= 0.60,
        "bootstrap_below_zero_ge_0_99": bootstrap["signed_below_zero"] >= 0.99,
        "mean_beats_controls_by_0_10": all(
            exact["signed_orientation_mean"]
            <= summary[v]["signed_orientation_mean"] - 0.10
            for v in ("time", "pair", "network")
        ),
        "bootstrap_beats_controls_ge_0_95": all(
            bootstrap["signed_vs_controls"][v] >= 0.95
            for v in ("time", "pair", "network")
        ),
    }
    traversal_gates: dict[str, bool] = {}
    for metric in ("amplitude", "closure"):
        traversal_gates[f"{metric}_mean_in_band"] = (
            0.92 <= exact[f"{metric}_x_mean"] <= 0.98
        )
        traversal_gates[f"{metric}_events_below_ge_0_55"] = (
            exact[f"{metric}_below_ridge_fraction"] >= 0.55
        )
        traversal_gates[f"{metric}_lineages_below_ge_0_55"] = (
            exact[f"{metric}_lineages_below_ridge_fraction"] >= 0.55
        )
        traversal_gates[f"{metric}_bootstrap_below_ge_0_99"] = (
            bootstrap[f"{metric}_below_ridge"] >= 0.99
        )
        traversal_gates[f"{metric}_mean_beats_controls_by_0_02"] = all(
            exact[f"{metric}_x_mean"]
            <= summary[v][f"{metric}_x_mean"] - 0.02
            for v in ("time", "pair", "network")
        )
        traversal_gates[f"{metric}_bootstrap_controls_ge_0_95"] = all(
            bootstrap[f"{metric}_vs_controls"][v] >= 0.95
            for v in ("time", "pair", "network")
        )
    gates_pass = (
        signed_gates == stored["signed_gates"]
        and traversal_gates == stored["traversal_gates"]
        and eligibility_pass == stored["eligibility_pass"]
    )
    verdict = (
        "INCONCLUSIVE — ELIGIBILITY"
        if not eligibility_pass
        else "SIGNED CROSSING + TRAVERSAL REPLICATED"
        if all(signed_gates.values()) and all(traversal_gates.values())
        else "SIGNED CROSSING ONLY"
        if all(signed_gates.values())
        else "TRAVERSAL ASYMMETRY ONLY"
        if all(traversal_gates.values())
        else "WEAK ANTI-ORIENTATION"
        if (
            signed_gates["negative_fraction_ge_0_60"]
            and signed_gates["bootstrap_below_zero_ge_0_99"]
        )
        else "NOT REPLICATED"
    )
    verdict_pass = verdict == stored["verdict"]

    checks = {
        "provenance_and_sizes": provenance_pass,
        "cache_shapes": shape_pass,
        "complete_loop_eligibility": eligibility_match,
        "complete_event_list": event_selection_pass,
        "sampled_raw_metrics": sampled_raw_pass,
        "all_exported_summaries": summary_pass,
        "seed_cluster_bootstraps": bootstrap_pass,
        "gates": gates_pass,
        "verdict": verdict_pass,
    }
    result = {
        "test_id": "Q37-INDEPENDENT-VALIDATION-v1",
        "date": "2026-07-27",
        "pass": all(checks.values()),
        "checks": checks,
        "provenance": provenance,
        "eligibility": eligibility,
        "eligibility_pass": eligibility_pass,
        "sampled_rows": int(len(sample_indices)),
        "sampled_metric_checks": sampled_checks,
        "sampled_max_absolute_error": sampled_max_error,
        "bootstrap": bootstrap,
        "verdict": verdict,
        "note": (
            "The eligibility floor fails only because 71 represented seeds is "
            "below the frozen minimum of 80."
        ),
    }
    OUTPUT.write_text(
        json.dumps(result, indent=2, allow_nan=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, allow_nan=True))
    if not result["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
