#!/usr/bin/env python3
"""T422 independent detector-bank parent test.

The frozen protocol in T422_FROZEN_PROTOCOL.md is authoritative.  This script
keeps the ISIS EMU forward and backward detector banks disjoint, detects a
U=R child crossing in one bank, and reads candidate-parent H from the other.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
MUON = HERE.parent
T416_DIR = MUON / "T416_dual_irrationality_time_tracking"
T421_DIR = MUON / "T421_child_singularity_parent_ridge"
PROTOCOL = HERE / "T422_FROZEN_PROTOCOL.md"
RESULTS = HERE / "results"
FREEZE = HERE / "T422_DEVELOPMENT_FREEZE.json"

sys.path.insert(0, str(T416_DIR))
sys.path.insert(0, str(T421_DIR))
import t416_dual_irrationality_time_tracking as t416  # noqa: E402
import t421_child_singularity_parent_ridge as t421  # noqa: E402


SEED = 422
SHIFT_DRAWS = 1000
BOOTSTRAPS = 10000
EVENT_HALF_WIDTH = 8
MIN_PRIMARY_ELIGIBILITY = 0.90
EPS = 1e-12

PARTITIONS: dict[str, np.ndarray] = {
    "F": np.arange(0, 48, dtype=int),
    "B": np.arange(48, 96, dtype=int),
    "F_inner": np.arange(0, 48, 3, dtype=int),
    "F_middle": np.arange(1, 48, 3, dtype=int),
    "F_outer": np.arange(2, 48, 3, dtype=int),
    "B_inner": np.arange(48, 96, 3, dtype=int),
    "B_middle": np.arange(49, 96, 3, dtype=int),
    "B_outer": np.arange(50, 96, 3, dtype=int),
}

PRIMARY_DIRECTIONS = (("F", "B"), ("B", "F"))
RINGS = ("inner", "middle", "outer")
WRONG_RING = {"inner": "middle", "middle": "outer", "outer": "inner"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_clean(value):
    if isinstance(value, dict):
        return {str(key): json_clean(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_clean(item) for item in value]
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(json_clean(value), indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict], header: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=header, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def wrong_frequencies(frequency: float) -> list[float]:
    values = []
    for k in t416.WRONG_K:
        for sign in (-1.0, 1.0):
            candidate = frequency + sign * float(k) / t416.LENGTH_US
            if candidate > 0.05:
                values.append(candidate)
    return values


def partition_paths(time: np.ndarray, counts: np.ndarray, frequency: float) -> tuple[dict, list[dict]]:
    correct = t416.extract_spin_path(time, counts, frequency)
    wrong = [t416.extract_spin_path(time, counts, value) for value in wrong_frequencies(frequency)]
    return correct, wrong


def analyse_run_period(row: dict, period: str) -> tuple[list[dict], list[dict]]:
    data = t416.t414.load_run(row)
    period_index = 0 if period == "RF on" else 1
    all_counts = data["counts"][period_index]
    time = data["time"]
    field = float(row["field_G"])
    frequency = t416.GAMMA_MHZ_PER_G * field
    dt = float(np.median(np.diff(time)))
    cycle_bins = max(4, int(round(1.0 / max(frequency * dt, EPS))))
    start = max(t416.PATH_WINDOW - 1, cycle_bins)

    timelines: list[dict] = []
    calibration: list[dict] = []
    for name, indices in PARTITIONS.items():
        correct, wrong = partition_paths(time, all_counts[indices], frequency)
        wrong_improvements = np.asarray([float(item["calibration_improvement"]) for item in wrong], dtype=float)
        finite_path = bool(
            np.all(np.isfinite(correct["phase"]))
            and np.isfinite(float(correct["basis_condition"]))
            and np.isfinite(float(correct["calibration_improvement"]))
        )
        basic_ok = bool(finite_path and float(correct["calibration_improvement"]) > 0.0)
        ring_specific_ok = bool(
            basic_ok
            and len(wrong_improvements) > 0
            and float(correct["calibration_improvement"]) > float(np.median(wrong_improvements))
        )
        calibration.append({
            "split": row["split"], "run": row["run"], "period": period,
            "field_G": field, "partition": name, "detector_count": len(indices),
            "detector_first_one_based": int(indices[0] + 1),
            "detector_last_one_based": int(indices[-1] + 1),
            "basis_condition": float(correct["basis_condition"]),
            "calibration_improvement": float(correct["calibration_improvement"]),
            "wrong_frequency_improvement_median": float(np.median(wrong_improvements)),
            "basic_eligible": int(basic_ok),
            "ring_frequency_specific_eligible": int(ring_specific_ok),
        })

        for end in range(start, len(correct["time"]), t416.PATH_STEP):
            time_us = float(correct["time"][end])
            if time_us < t416.CALIBRATION_END_US:
                continue
            history = correct["phase"][end - t416.PATH_WINDOW + 1 : end + 1]
            measured = t421.relation_metrics(history)
            wrong_metrics = [
                t421.relation_metrics(path["phase"][end - t416.PATH_WINDOW + 1 : end + 1])
                for path in wrong
            ]
            timelines.append({
                "split": row["split"], "run": row["run"], "period": period,
                "rf_flag": int(period == "RF on"), "temperature_K": float(row["temperature_K"]),
                "field_G": field, "frequency_MHz": frequency, "partition": name,
                "time_us": time_us, "openness_U": measured["U"], "closure_R": measured["R"],
                "parent_H": measured["H"], "signed_parent_Q": measured["Q"],
                "Q_concentration": measured["Q_concentration"],
                "wrong_parent_H": float(np.median([item["H"] for item in wrong_metrics])),
                "cycle_bins": cycle_bins, "history_native_bins": t416.PATH_WINDOW,
                "basis_condition": float(correct["basis_condition"]),
                "calibration_improvement": float(correct["calibration_improvement"]),
            })
    return timelines, calibration


def partition_groups(timeline: list[dict], partition: str) -> dict[tuple[str, str], list[dict]]:
    output: dict[tuple[str, str], list[dict]] = {}
    for row in timeline:
        if row["partition"] != partition:
            continue
        output.setdefault((str(row["run"]), str(row["period"])), []).append(row)
    for key in output:
        output[key].sort(key=lambda item: float(item["time_us"]))
    return output


def calibration_map(rows: list[dict]) -> dict[tuple[str, str, str], dict]:
    return {(str(row["run"]), str(row["period"]), str(row["partition"])): row for row in rows}


def mismatch_map(groups: dict[tuple[str, str], list[dict]]) -> dict[tuple[str, str], tuple[str, str]]:
    by_period: dict[str, list[tuple[float, tuple[str, str]]]] = {}
    for key, rows in groups.items():
        by_period.setdefault(key[1], []).append((float(rows[0]["field_G"]), key))
    output = {}
    for items in by_period.values():
        ordered = [key for _, key in sorted(items)]
        for index, key in enumerate(ordered):
            output[key] = ordered[(index + 1) % len(ordered)]
    return output


def event_rows(
    timeline: list[dict],
    calibration: list[dict],
    child_partition: str,
    parent_partition: str,
    wrong_ring_partition: str | None = None,
    require_ring_specific: bool = False,
) -> tuple[list[dict], list[dict], dict]:
    child_groups = partition_groups(timeline, child_partition)
    parent_groups = partition_groups(timeline, parent_partition)
    wrong_ring_groups = partition_groups(timeline, wrong_ring_partition) if wrong_ring_partition else {}
    parent_mismatch = mismatch_map(parent_groups)
    cal = calibration_map(calibration)
    events: list[dict] = []
    centered: list[dict] = []
    attempted = len(child_groups)
    eligible_sequences = 0

    for key, child in sorted(child_groups.items()):
        parent = parent_groups.get(key)
        if not parent or len(parent) != len(child):
            continue
        c_cal = cal.get((key[0], key[1], child_partition), {})
        p_cal = cal.get((key[0], key[1], parent_partition), {})
        field_ok = bool(c_cal.get("basic_eligible", 0) and p_cal.get("basic_eligible", 0))
        if require_ring_specific:
            field_ok = bool(
                field_ok
                and c_cal.get("ring_frequency_specific_eligible", 0)
                and p_cal.get("ring_frequency_specific_eligible", 0)
            )
        if not field_ok:
            continue

        crossings = t421.crossing_positions(child)
        if not crossings:
            continue
        eligible_sequences += 1

        parent_h = np.asarray([float(row["parent_H"]) for row in parent])
        parent_wrong_h = np.asarray([float(row["wrong_parent_H"]) for row in parent])
        same_h = np.asarray([float(row["parent_H"]) for row in child])
        child_u = np.asarray([float(row["openness_U"]) for row in child])
        child_r = np.asarray([float(row["closure_R"]) for row in child])
        child_t = np.asarray([float(row["time_us"]) for row in child])
        mismatch_rows = parent_groups[parent_mismatch[key]]
        mismatch_h = np.asarray([float(row["parent_H"]) for row in mismatch_rows])
        wrong_ring_rows = wrong_ring_groups.get(key) if wrong_ring_partition else None
        wrong_ring_h = (
            np.asarray([float(row["parent_H"]) for row in wrong_ring_rows])
            if wrong_ring_rows and len(wrong_ring_rows) == len(child) else None
        )
        history_distance = float(np.median(np.abs(parent_h - 1.0)))
        same_history_distance = float(np.median(np.abs(same_h - 1.0)))
        wrong_ring_history_distance = (
            float(np.median(np.abs(wrong_ring_h - 1.0))) if wrong_ring_h is not None else float("nan")
        )

        for event_index, crossing in enumerate(crossings):
            position = float(crossing["child_position"])
            progress = position / max(len(child) - 1, 1)
            parent_value = t421.at(parent_h, position)
            wrong_value = t421.at(parent_wrong_h, position)
            same_value = t421.at(same_h, position)
            mismatch_value = t421.at(mismatch_h, progress * (len(mismatch_h) - 1))
            wrong_ring_value = t421.at(wrong_ring_h, position) if wrong_ring_h is not None else float("nan")
            exposure = history_distance - abs(parent_value - 1.0)
            same_exposure = same_history_distance - abs(same_value - 1.0)
            wrong_ring_exposure = (
                wrong_ring_history_distance - abs(wrong_ring_value - 1.0)
                if np.isfinite(wrong_ring_value) else float("nan")
            )
            event_id = f"{key[0]}|{key[1]}|{child_partition}_to_{parent_partition}|{event_index}"
            record = {
                "split": child[0]["split"], "event_id": event_id,
                "run": key[0], "period": key[1], "rf_flag": child[0]["rf_flag"],
                "temperature_K": child[0]["temperature_K"], "field_G": child[0]["field_G"],
                "direction": f"{child_partition}_to_{parent_partition}",
                "child_partition": child_partition, "parent_partition": parent_partition,
                "wrong_ring_partition": wrong_ring_partition or "",
                "crossing_position": position, "crossing_time_us": t421.at(child_t, position),
                "crossing_U": crossing["crossing_U"], "crossing_R": crossing["crossing_R"],
                "crossing_direction": crossing["direction"],
                "parent_H": parent_value, "parent_ridge_distance": abs(parent_value - 1.0),
                "history_parent_distance": history_distance, "ridge_exposure": exposure,
                "same_bank_H": same_value, "same_bank_ridge_distance": abs(same_value - 1.0),
                "same_bank_history_distance": same_history_distance,
                "same_bank_exposure": same_exposure,
                "wrong_parent_H": wrong_value,
                "wrong_frequency_minus_correct_distance": abs(wrong_value - 1.0) - abs(parent_value - 1.0),
                "mismatch_parent_H": mismatch_value,
                "mismatch_lineage_minus_correct_distance": abs(mismatch_value - 1.0) - abs(parent_value - 1.0),
                "wrong_ring_H": wrong_ring_value,
                "wrong_ring_exposure": wrong_ring_exposure,
                "ring_correspondence_advantage": exposure - wrong_ring_exposure if np.isfinite(wrong_ring_exposure) else float("nan"),
            }
            events.append(record)
            for offset in range(-EVENT_HALF_WIDTH, EVENT_HALF_WIDTH + 1):
                point = position + offset
                if point < 0 or point > len(child) - 1:
                    continue
                centered.append({
                    "split": child[0]["split"], "event_id": event_id, "run": key[0],
                    "period": key[1], "field_G": child[0]["field_G"],
                    "direction": record["direction"], "offset_reads": offset,
                    "offset_us": t421.at(child_t, point) - record["crossing_time_us"],
                    "child_U": t421.at(child_u, point), "child_R": t421.at(child_r, point),
                    "other_bank_H": t421.at(parent_h, point), "same_bank_H": t421.at(same_h, point),
                })
    return events, centered, {
        "attempted_sequences": attempted,
        "eligible_sequences": eligible_sequences,
        "eligibility_rate": eligible_sequences / attempted if attempted else 0.0,
    }


def field_values(rows: list[dict], key: str, period: str | None = None) -> dict[float, float]:
    output = {}
    fields = sorted({float(row["field_G"]) for row in rows if period is None or row["period"] == period})
    for field in fields:
        values = [
            float(row[key]) for row in rows
            if float(row["field_G"]) == field
            and (period is None or row["period"] == period)
            and np.isfinite(float(row[key]))
        ]
        if values:
            output[field] = float(np.median(values))
    return output


def aggregate(rows: list[dict], key: str, period: str | None = None) -> float:
    values = list(field_values(rows, key, period).values())
    return float(np.median(values)) if values else float("nan")


def bootstrap(rows: list[dict], key: str, seed: int) -> dict:
    field = field_values(rows, key)
    values = np.asarray([field[name] for name in sorted(field)], dtype=float)
    if len(values) == 0:
        return {"median": float("nan"), "ci95": [float("nan"), float("nan")], "field_count": 0}
    rng = np.random.default_rng(seed)
    draws = rng.choice(values, size=(BOOTSTRAPS, len(values)), replace=True)
    medians = np.median(draws, axis=1)
    return {
        "median": float(np.median(values)),
        "ci95": [float(np.percentile(medians, 2.5)), float(np.percentile(medians, 97.5))],
        "field_count": len(values),
    }


def shift_null(
    timeline: list[dict], child_partition: str, parent_partition: str, seed: int
) -> np.ndarray:
    child_groups = partition_groups(timeline, child_partition)
    parent_groups = partition_groups(timeline, parent_partition)
    positions = {key: t421.crossing_positions(rows) for key, rows in child_groups.items()}
    rng = np.random.default_rng(seed)
    draws = np.empty(SHIFT_DRAWS, dtype=float)
    for draw in range(SHIFT_DRAWS):
        pseudo = []
        for key, crossings in sorted(positions.items()):
            parent = parent_groups.get(key)
            if not parent or not crossings:
                continue
            h = np.asarray([float(row["parent_H"]) for row in parent])
            shift = int(rng.choice(np.arange(1, len(h), dtype=int)))
            for crossing in crossings:
                value = t421.at(h, float(crossing["child_position"]) + shift, circular=True)
                pseudo.append({"field_G": parent[0]["field_G"], "distance": abs(value - 1.0)})
        draws[draw] = aggregate(pseudo, "distance")
    return draws


def direction_summary(
    stage: str,
    timeline: list[dict],
    events: list[dict],
    eligibility: dict,
    child_partition: str,
    parent_partition: str,
    seed_offset: int,
) -> tuple[dict, list[dict]]:
    exposure = bootstrap(events, "ridge_exposure", SEED + seed_offset + 1)
    same = bootstrap(events, "same_bank_exposure", SEED + seed_offset + 2)
    wrong = bootstrap(events, "wrong_frequency_minus_correct_distance", SEED + seed_offset + 3)
    mismatch = bootstrap(events, "mismatch_lineage_minus_correct_distance", SEED + seed_offset + 4)
    real_distance = aggregate(events, "parent_ridge_distance")
    shifts = shift_null(timeline, child_partition, parent_partition, SEED + seed_offset + 5)
    finite_shift = np.all(np.isfinite(shifts)) and np.isfinite(real_distance)
    shift_p = (
        float((1 + np.count_nonzero(shifts <= real_distance)) / (1 + len(shifts)))
        if finite_shift else float("nan")
    )
    period_effects = {
        period: aggregate(events, "ridge_exposure", period)
        for period in ("RF on", "RF off")
    }
    result = {
        "direction": f"{child_partition}_to_{parent_partition}",
        "event_count": len(events),
        "field_count": len(field_values(events, "ridge_exposure")),
        **eligibility,
        "median_crossing_coordinate": float(np.median([row["crossing_U"] for row in events])) if events else float("nan"),
        "median_other_bank_H": float(np.median([row["parent_H"] for row in events])) if events else float("nan"),
        "field_balanced_parent_ridge_distance": real_distance,
        "ridge_exposure": exposure,
        "same_bank_exposure": same,
        "wrong_frequency_effect": wrong,
        "mismatch_lineage_effect": mismatch,
        "shift": {
            "empirical_p": shift_p,
            "real_distance": real_distance,
            "null_median": float(np.median(shifts)) if finite_shift else float("nan"),
        },
        "rf_exposure": period_effects,
    }
    shift_rows = [
        {"split": stage, "direction": result["direction"], "draw": index, "parent_ridge_distance": value}
        for index, value in enumerate(shifts)
    ]
    return result, shift_rows


def summarize_stage(
    stage: str,
    timeline: list[dict],
    calibration: list[dict],
) -> tuple[dict, list[dict], list[dict], list[dict], list[dict]]:
    all_events: list[dict] = []
    all_centered: list[dict] = []
    shift_rows: list[dict] = []
    summaries: dict[str, dict] = {}
    for index, (child_partition, parent_partition) in enumerate(PRIMARY_DIRECTIONS):
        events, centered, eligibility = event_rows(
            timeline, calibration, child_partition, parent_partition
        )
        summary, shifts = direction_summary(
            stage, timeline, events, eligibility, child_partition, parent_partition, index * 20
        )
        summaries[summary["direction"]] = summary
        all_events.extend(events)
        all_centered.extend(centered)
        shift_rows.extend(shifts)

    ring_events: list[dict] = []
    ring_eligibility: list[dict] = []
    for child_bank, parent_bank in PRIMARY_DIRECTIONS:
        for ring in RINGS:
            child_partition = f"{child_bank}_{ring}"
            parent_partition = f"{parent_bank}_{ring}"
            wrong_partition = f"{parent_bank}_{WRONG_RING[ring]}"
            events, _, eligibility = event_rows(
                timeline, calibration, child_partition, parent_partition,
                wrong_ring_partition=wrong_partition, require_ring_specific=True,
            )
            ring_events.extend(events)
            ring_eligibility.append({
                "split": stage, "direction": f"{child_bank}_to_{parent_bank}",
                "ring": ring, "wrong_ring": WRONG_RING[ring], **eligibility,
            })

    directions = list(summaries.values())
    g1 = all(item["eligibility_rate"] >= MIN_PRIMARY_ELIGIBILITY for item in directions)
    g2 = all(item["ridge_exposure"]["ci95"][0] > 0.0 for item in directions)
    g3 = all(item["shift"]["empirical_p"] < 0.05 for item in directions)
    g4 = all(item["wrong_frequency_effect"]["ci95"][0] > 0.0 for item in directions)
    g5 = all(item["mismatch_lineage_effect"]["ci95"][0] > 0.0 for item in directions)
    g6 = all(
        item["rf_exposure"][period] > 0.0
        for item in directions for period in ("RF on", "RF off")
    )

    all_three_rings = all(item["eligibility_rate"] > 0.0 for item in ring_eligibility)
    ring_advantage = bootstrap(ring_events, "ring_correspondence_advantage", SEED + 90)
    g7 = bool(all_three_rings and ring_advantage["ci95"][0] > 0.0)
    gates = {
        "G1_availability": {"pass": g1, "minimum_rate": MIN_PRIMARY_ELIGIBILITY,
                            "direction_rates": {item["direction"]: item["eligibility_rate"] for item in directions}},
        "G2_bidirectional_independent_ridge": {"pass": g2,
                                                "effects": {item["direction"]: item["ridge_exposure"] for item in directions}},
        "G3_timing_specificity": {"pass": g3,
                                   "empirical_p": {item["direction"]: item["shift"]["empirical_p"] for item in directions}},
        "G4_frequency_specificity": {"pass": g4,
                                      "effects": {item["direction"]: item["wrong_frequency_effect"] for item in directions}},
        "G5_lineage_specificity": {"pass": g5,
                                    "effects": {item["direction"]: item["mismatch_lineage_effect"] for item in directions}},
        "G6_RF_robustness": {"pass": g6,
                              "effects": {item["direction"]: item["rf_exposure"] for item in directions}},
        "G7_ring_correspondence_secondary": {"pass": g7, "available": all_three_rings,
                                               "effect": ring_advantage},
    }
    result = {
        "test": "T422 independent detector-bank parent test",
        "stage": stage,
        "identity": "muoniated-acetone detector-population spin relation",
        "raw_population": "ISIS EMU 96 detector spectra split into disjoint forward/backward banks",
        "coordinates": {
            "child": "U/R crossing from one bank",
            "candidate_parent": "other-bank lag-angle H with ridge at 1",
            "orientation": "all coordinates 0-2; U=R child crossover; H=1 candidate-parent ridge",
        },
        "causal_boundary_us": t416.CALIBRATION_END_US,
        "timeline_rows": len(timeline),
        "calibration_rows": len(calibration),
        "directions": summaries,
        "ring_eligibility": ring_eligibility,
        "ring_correspondence_effect": ring_advantage,
        "gates": gates,
        "primary_supported": bool(all(gates[name]["pass"] for name in (
            "G1_availability", "G2_bidirectional_independent_ridge", "G3_timing_specificity",
            "G4_frequency_specificity", "G5_lineage_specificity", "G6_RF_robustness",
        ))),
        "secondary_ring_supported": g7,
        "boundaries": [
            "Population-level detector relation, not an individual muon or neutrino event.",
            "Opposing banks are disjoint measurements of one source but can share source and instrument systematics.",
            "A pass does not identify H as a unique physical parent.",
        ],
        "protocol_sha256": sha256(PROTOCOL),
        "analysis_sha256": sha256(Path(__file__).resolve()),
    }
    return result, all_events, all_centered, shift_rows, ring_events


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True, choices=("development", "validation", "holdout"))
    args = parser.parse_args()
    stage = args.stage

    manifest = [row for row in t416.t414.read_manifest() if row["split"] == stage]
    timeline: list[dict] = []
    calibration: list[dict] = []
    for index, row in enumerate(manifest, start=1):
        print(f"{stage}: {index}/{len(manifest)} {row['run']} {row['field_G']:.0f} G", flush=True)
        for period in ("RF on", "RF off"):
            rows, checks = analyse_run_period(row, period)
            timeline.extend(rows)
            calibration.extend(checks)

    if stage == "development":
        freeze = {
            "protocol_sha256": sha256(PROTOCOL),
            "analysis_sha256": sha256(Path(__file__).resolve()),
            "constants": {
                "seed": SEED, "shift_draws": SHIFT_DRAWS, "bootstraps": BOOTSTRAPS,
                "event_half_width": EVENT_HALF_WIDTH,
                "minimum_primary_eligibility": MIN_PRIMARY_ELIGIBILITY,
                "causal_boundary_us": t416.CALIBRATION_END_US,
                "path_window": t416.PATH_WINDOW, "path_step": t416.PATH_STEP,
            },
            "partitions_zero_based": {name: values.tolist() for name, values in PARTITIONS.items()},
        }
        write_json(FREEZE, freeze)
    else:
        freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
        if freeze["protocol_sha256"] != sha256(PROTOCOL) or freeze["analysis_sha256"] != sha256(Path(__file__).resolve()):
            raise RuntimeError("T422 protocol or analysis changed after development freeze")

    result, events, centered, shifts, ring_events = summarize_stage(stage, timeline, calibration)
    result["source_hashes"] = {
        row["run"]: sha256(t416.t414.RAW / f"{row['run']}.nxs") for row in manifest
    }
    tag = stage.upper()
    RESULTS.mkdir(parents=True, exist_ok=True)
    write_json(RESULTS / f"T422_{tag}_RESULTS.json", result)
    write_csv(RESULTS / f"T422_{tag}_TIMELINE.csv", timeline, list(timeline[0]) if timeline else [])
    write_csv(RESULTS / f"T422_{tag}_CALIBRATION.csv", calibration, list(calibration[0]) if calibration else [])
    event_header = list(events[0]) if events else [
        "split", "event_id", "run", "period", "field_G", "direction", "crossing_time_us",
        "crossing_U", "crossing_R", "parent_H", "parent_ridge_distance", "ridge_exposure",
    ]
    write_csv(RESULTS / f"T422_{tag}_EVENTS.csv", events, event_header)
    centered_header = list(centered[0]) if centered else [
        "split", "event_id", "run", "period", "field_G", "direction", "offset_reads",
        "offset_us", "child_U", "child_R", "other_bank_H", "same_bank_H",
    ]
    write_csv(RESULTS / f"T422_{tag}_EVENT_CENTERED.csv", centered, centered_header)
    write_csv(RESULTS / f"T422_{tag}_SHIFT_NULL.csv", shifts, list(shifts[0]) if shifts else [])
    ring_header = list(ring_events[0]) if ring_events else event_header
    write_csv(RESULTS / f"T422_{tag}_RING_EVENTS.csv", ring_events, ring_header)
    print(json.dumps(json_clean(result), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
