#!/usr/bin/env python3
"""T417 coupled Rationality/Irrationality Di-ARA handover test."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
T416 = HERE.parent / "T416_dual_irrationality_time_tracking"
PROTOCOL = HERE / "T417_FROZEN_PROTOCOL.md"
RESULTS = HERE / "results"
FREEZE = HERE / "T417_DEVELOPMENT_FREEZE.json"
SEED = 417
SHIFT_DRAWS = 1000
BOOTSTRAPS = 10000
EPS = 1e-12
SATURATION = 1.99


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def median_abs_deviation(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    if len(values) == 0:
        return float("nan")
    middle = float(np.median(values))
    return float(np.median(np.abs(values - middle)))


def first_balance_crossing(time: np.ndarray, r: np.ndarray, i: np.ndarray) -> float:
    difference = i - r
    for index in range(2, len(difference) - 2):
        if (
            np.all(difference[index - 2 : index] <= 0.0)
            and np.all(difference[index : index + 3] > 0.0)
        ):
            left, right = float(difference[index - 1]), float(difference[index])
            fraction = 0.0 if abs(right - left) < EPS else -left / (right - left)
            return float(time[index - 1] + fraction * (time[index] - time[index - 1]))
    return float("nan")


def first_saturation(time: np.ndarray, i: np.ndarray) -> float:
    for index in range(0, len(i) - 2):
        if np.all(i[index : index + 3] >= SATURATION):
            return float(time[index])
    return float("nan")


def interpolate_at(time: np.ndarray, values: np.ndarray, at: float) -> float:
    if not np.isfinite(at):
        return float("nan")
    return float(np.interp(at, time, values))


def roots(time: np.ndarray, values: np.ndarray) -> np.ndarray:
    found: list[float] = []
    for index in range(1, len(values)):
        left, right = float(values[index - 1]), float(values[index])
        if left == 0.0:
            found.append(float(time[index - 1]))
        if left * right < 0.0 or right == 0.0:
            fraction = 0.0 if abs(right - left) < EPS else -left / (right - left)
            found.append(float(time[index - 1] + fraction * (time[index] - time[index - 1])))
    if not found:
        return np.asarray([], dtype=float)
    return np.unique(np.round(np.asarray(found, dtype=float), 12))


def nearest_distance(points: np.ndarray, target: float) -> tuple[float, float]:
    if len(points) == 0 or not np.isfinite(target):
        return float("nan"), float("nan")
    index = int(np.argmin(np.abs(points - target)))
    return float(points[index]), float(abs(points[index] - target))


def grouped(rows: list[dict]) -> dict[tuple[str, str], list[dict]]:
    result: dict[tuple[str, str], list[dict]] = {}
    for row in rows:
        result.setdefault((row["run"], row["period"]), []).append(row)
    for key in result:
        result[key].sort(key=lambda item: float(item["time_us"]))
    return result


def sequence_arrays(rows: list[dict]) -> dict[str, np.ndarray]:
    time = np.asarray([float(row["time_us"]) for row in rows], dtype=float)
    parent = np.asarray([float(row["parent_ARA"]) for row in rows], dtype=float)
    x_l = np.asarray([float(row["state_x_L"]) for row in rows], dtype=float)
    x_c = np.asarray([float(row["state_x_C"]) for row in rows], dtype=float)
    i_wave = np.asarray([float(row["history_x_R"]) for row in rows], dtype=float)
    rho = np.asarray([float(row["median_closure_rho"]) for row in rows], dtype=float)
    r_wave = 2.0 * rho
    amount = 0.5 * (r_wave + i_wave)
    balance = 1.0 + (i_wave - r_wave) / (i_wave + r_wave + EPS)
    return {
        "time": time,
        "parent": parent,
        "x_L": x_l,
        "x_C": x_c,
        "I": i_wave,
        "R": r_wave,
        "A": amount,
        "B": balance,
    }


def summarise_sequence(rows: list[dict]) -> tuple[dict, list[dict]]:
    arrays = sequence_arrays(rows)
    time = arrays["time"]
    handover = first_balance_crossing(time, arrays["R"], arrays["I"])
    saturation = first_saturation(time, arrays["I"])
    same_roots = roots(time, arrays["x_L"] - arrays["x_C"])
    mirror_roots = roots(time, arrays["x_L"] + arrays["x_C"] - 2.0)
    same_time, same_distance = nearest_distance(same_roots, handover)
    mirror_time, mirror_distance = nearest_distance(mirror_roots, handover)
    eligible = bool(np.isfinite(handover) and np.isfinite(saturation))
    ordered = bool(eligible and handover < saturation)
    lead = float(saturation - handover) if eligible else float("nan")
    first = rows[0]
    summary = {
        "run": first["run"],
        "period": first["period"],
        "field_G": float(first["field_G"]),
        "windows": len(rows),
        "handover_time_us": handover,
        "handover_parent_ARA": interpolate_at(time, arrays["parent"], handover),
        "handover_amount_A": interpolate_at(time, arrays["A"], handover),
        "handover_balance_B": interpolate_at(time, arrays["B"], handover),
        "handover_R": interpolate_at(time, arrays["R"], handover),
        "handover_I": interpolate_at(time, arrays["I"], handover),
        "saturation_time_us": saturation,
        "saturation_parent_ARA": interpolate_at(time, arrays["parent"], saturation),
        "eligible": int(eligible),
        "ordered": int(ordered),
        "lead_us": lead,
        "nearest_same_time_us": same_time,
        "nearest_same_distance_us": same_distance,
        "nearest_mirror_time_us": mirror_time,
        "nearest_mirror_distance_us": mirror_distance,
        "same_meeting_count": len(same_roots),
        "mirror_meeting_count": len(mirror_roots),
    }
    timeline: list[dict] = []
    for index, source in enumerate(rows):
        timeline.append({
            "split": source["split"],
            "run": source["run"],
            "period": source["period"],
            "field_G": float(source["field_G"]),
            "time_us": float(source["time_us"]),
            "parent_ARA": float(source["parent_ARA"]),
            "state_x_L": arrays["x_L"][index],
            "state_x_C": arrays["x_C"][index],
            "rational_closure_R": arrays["R"][index],
            "irrational_unresolved_I": arrays["I"][index],
            "coupled_amount_A": arrays["A"][index],
            "coupled_balance_B": arrays["B"][index],
            "handover_time_us": handover,
            "saturation_time_us": saturation,
        })
    return summary, timeline


def field_bootstrap_interval(summaries: list[dict], rng: np.random.Generator) -> list[float]:
    by_field: dict[float, list[float]] = {}
    for row in summaries:
        if int(row["eligible"]) and np.isfinite(float(row["lead_us"])):
            by_field.setdefault(float(row["field_G"]), []).append(float(row["lead_us"]))
    field_values = np.asarray([np.median(values) for values in by_field.values()], dtype=float)
    if len(field_values) == 0:
        return [float("nan"), float("nan")]
    boot = np.asarray([
        np.median(rng.choice(field_values, size=len(field_values), replace=True))
        for _ in range(BOOTSTRAPS)
    ])
    return [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))]


def random_nontrivial_shift(rng: np.random.Generator, length: int) -> int:
    candidates = np.arange(5, max(6, length - 4), dtype=int)
    if len(candidates) == 0:
        return max(1, length // 2)
    return int(rng.choice(candidates))


def shifted_controls(groups: dict[tuple[str, str], list[dict]], rng: np.random.Generator) -> dict:
    keys = sorted(groups)
    ri_mads: list[float] = []
    state_same: list[float] = []
    state_mirror: list[float] = []
    for _ in range(SHIFT_DRAWS):
        shifted_parent_positions: list[float] = []
        shifted_same_distances: list[float] = []
        shifted_mirror_distances: list[float] = []
        for key in keys:
            arrays = sequence_arrays(groups[key])
            length = len(arrays["time"])
            r_shift = np.roll(arrays["R"], random_nontrivial_shift(rng, length))
            shifted_handover = first_balance_crossing(arrays["time"], r_shift, arrays["I"])
            if np.isfinite(shifted_handover):
                shifted_parent_positions.append(interpolate_at(arrays["time"], arrays["parent"], shifted_handover))
            x_c_shift = np.roll(arrays["x_C"], random_nontrivial_shift(rng, length))
            same_points = roots(arrays["time"], arrays["x_L"] - x_c_shift)
            mirror_points = roots(arrays["time"], arrays["x_L"] + x_c_shift - 2.0)
            _, same_distance = nearest_distance(same_points, first_balance_crossing(arrays["time"], arrays["R"], arrays["I"]))
            _, mirror_distance = nearest_distance(mirror_points, first_balance_crossing(arrays["time"], arrays["R"], arrays["I"]))
            if np.isfinite(same_distance):
                shifted_same_distances.append(same_distance)
            if np.isfinite(mirror_distance):
                shifted_mirror_distances.append(mirror_distance)
        ri_mads.append(median_abs_deviation(np.asarray(shifted_parent_positions)) if len(shifted_parent_positions) >= 20 else float("nan"))
        state_same.append(float(np.median(shifted_same_distances)) if shifted_same_distances else float("nan"))
        state_mirror.append(float(np.median(shifted_mirror_distances)) if shifted_mirror_distances else float("nan"))
    return {
        "ri_parent_mad": np.asarray(ri_mads, dtype=float),
        "state_same_distance": np.asarray(state_same, dtype=float),
        "state_mirror_distance": np.asarray(state_mirror, dtype=float),
    }


def empirical_lower_p(null: np.ndarray, observed: float) -> float:
    finite = null[np.isfinite(null)]
    if len(finite) == 0 or not np.isfinite(observed):
        return float("nan")
    return float((1 + np.count_nonzero(finite <= observed)) / (1 + len(finite)))


def analyse(stage: str) -> dict:
    source = T416 / "results" / f"T416_{'DEVELOPMENT' if stage == 'development' else 'VALIDATION'}_TIMELINE.csv"
    rows = load_csv(source)
    groups = grouped(rows)
    summaries: list[dict] = []
    timelines: list[dict] = []
    for key in sorted(groups):
        summary, timeline = summarise_sequence(groups[key])
        summaries.append(summary)
        timelines.extend(timeline)

    rng = np.random.default_rng(SEED + (0 if stage == "development" else 100000))
    controls = shifted_controls(groups, rng)
    eligible = [row for row in summaries if int(row["eligible"])]
    ordered = [row for row in eligible if int(row["ordered"])]
    leads = np.asarray([float(row["lead_us"]) for row in eligible], dtype=float)
    parent_positions = np.asarray([float(row["handover_parent_ARA"]) for row in summaries if np.isfinite(float(row["handover_parent_ARA"]))], dtype=float)
    observed_parent_mad = median_abs_deviation(parent_positions)
    null_parent_mad = controls["ri_parent_mad"]
    null_parent_median = float(np.nanmedian(null_parent_mad))
    dispersion_improvement = float((null_parent_median - observed_parent_mad) / max(null_parent_median, EPS))
    dispersion_p = empirical_lower_p(null_parent_mad, observed_parent_mad)
    observed_same = float(np.nanmedian([float(row["nearest_same_distance_us"]) for row in summaries]))
    observed_mirror = float(np.nanmedian([float(row["nearest_mirror_distance_us"]) for row in summaries]))
    same_p = empirical_lower_p(controls["state_same_distance"], observed_same)
    mirror_p = empirical_lower_p(controls["state_mirror_distance"], observed_mirror)
    state_winner = "same-coordinate xL=xC" if same_p <= mirror_p else "mirror xL+xC=2"
    state_winner_p = min(same_p, mirror_p)
    lead_ci = field_bootstrap_interval(summaries, rng)

    gates = {
        "G1_availability": {
            "pass": len(eligible) >= 20,
            "value": len(eligible),
            "threshold": ">=20 of 26 sequences",
        },
        "G2_ordering": {
            "pass": len(eligible) > 0 and len(ordered) / len(eligible) >= 0.80,
            "value": float(len(ordered) / len(eligible)) if eligible else float("nan"),
            "threshold": ">=0.80",
        },
        "G3_positive_lead": {
            "pass": np.isfinite(lead_ci[0]) and lead_ci[0] > 0.0,
            "value": float(np.median(leads)) if len(leads) else float("nan"),
            "ci95": lead_ci,
            "threshold": "field-bootstrap lower 95% bound >0 us",
        },
        "G4_coupling_specificity": {
            "pass": dispersion_improvement >= 0.25 and dispersion_p < 0.05,
            "observed_parent_ARA_mad": observed_parent_mad,
            "null_median_parent_ARA_mad": null_parent_median,
            "relative_improvement": dispersion_improvement,
            "empirical_p": dispersion_p,
            "threshold": ">=25% tighter and p<0.05",
        },
        "G5_state_alignment": {
            "pass": state_winner_p < 0.05,
            "winner": state_winner,
            "winner_p": state_winner_p,
            "same_observed_distance_us": observed_same,
            "same_null_median_distance_us": float(np.nanmedian(controls["state_same_distance"])),
            "same_p": same_p,
            "mirror_observed_distance_us": observed_mirror,
            "mirror_null_median_distance_us": float(np.nanmedian(controls["state_mirror_distance"])),
            "mirror_p": mirror_p,
            "threshold": "either relation p<0.05 against shifted xC",
        },
    }
    primary_supported = all(gates[name]["pass"] for name in (
        "G1_availability", "G2_ordering", "G3_positive_lead", "G4_coupling_specificity"
    ))
    complete_supported = primary_supported and gates["G5_state_alignment"]["pass"]

    timeline_path = RESULTS / f"T417_{stage.upper()}_TIMELINE.csv"
    summary_path = RESULTS / f"T417_{stage.upper()}_SEQUENCE_SUMMARY.csv"
    null_path = RESULTS / f"T417_{stage.upper()}_SHIFT_NULLS.csv"
    write_csv(timeline_path, timelines)
    write_csv(summary_path, summaries)
    null_rows = [{
        "draw": index,
        "ri_parent_ARA_mad": controls["ri_parent_mad"][index],
        "state_same_distance_us": controls["state_same_distance"][index],
        "state_mirror_distance_us": controls["state_mirror_distance"][index],
    } for index in range(SHIFT_DRAWS)]
    write_csv(null_path, null_rows)

    example_rows = [row for row in timelines if abs(float(row["field_G"]) - 284.0) < 1e-9]
    if example_rows:
        write_csv(RESULTS / f"T417_{stage.upper()}_284G_TIMELINE.csv", example_rows)

    result = {
        "test": "T417 coupled Rationality/Irrationality Di-ARA handover",
        "stage": stage,
        "status": "SUPPORTED" if complete_supported else "NOT SUPPORTED",
        "primary_coupled_handover": "SUPPORTED" if primary_supported else "NOT SUPPORTED",
        "state_alignment": "SUPPORTED" if gates["G5_state_alignment"]["pass"] else "NOT SUPPORTED",
        "boundary": "post-T416 locked evaluation; population ensemble only",
        "source": str(source.relative_to(HERE.parent.parent.parent)),
        "run_period_sequences": len(summaries),
        "eligible_sequences": len(eligible),
        "ordered_sequences": len(ordered),
        "median_lead_us": float(np.median(leads)) if len(leads) else float("nan"),
        "lead_ci95_us": lead_ci,
        "median_handover_parent_ARA": float(np.nanmedian(parent_positions)),
        "handover_parent_ARA_mad": observed_parent_mad,
        "gates": gates,
        "hashes": {
            "protocol_sha256": sha256(PROTOCOL),
            "script_sha256": sha256(Path(__file__).resolve()),
            "source_sha256": sha256(source),
        },
    }
    write_json(RESULTS / f"T417_{stage.upper()}_RESULTS.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("development", "evaluation"), required=True)
    arguments = parser.parse_args()
    RESULTS.mkdir(parents=True, exist_ok=True)
    script = Path(__file__).resolve()
    if arguments.stage == "development":
        if FREEZE.exists():
            raise SystemExit("development freeze already exists; refusing to overwrite")
        result = analyse("development")
        freeze = {
            "frozen_after_stage": "development",
            "protocol_sha256": sha256(PROTOCOL),
            "script_sha256": sha256(script),
            "development_results_sha256": sha256(RESULTS / "T417_DEVELOPMENT_RESULTS.json"),
            "development_status": result["status"],
        }
        write_json(FREEZE, freeze)
    else:
        if not FREEZE.exists():
            raise SystemExit("missing T417 development freeze")
        freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
        if freeze["protocol_sha256"] != sha256(PROTOCOL):
            raise SystemExit("protocol changed after development freeze")
        if freeze["script_sha256"] != sha256(script):
            raise SystemExit("analysis script changed after development freeze")
        result = analyse("evaluation")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
