#!/usr/bin/env python3
"""T421 child-singularity / parent-ridge hierarchy test."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
MUON = HERE.parent
T416_DIR = MUON / "T416_dual_irrationality_time_tracking"
T419_DIR = MUON / "T419_dynamic_irrationality_handover"
T420_DIR = MUON / "T420_information3_handover"
PROTOCOL = HERE / "T421_FROZEN_PROTOCOL.md"
RESULTS = HERE / "results"
FREEZE = HERE / "T421_DEVELOPMENT_FREEZE.json"

sys.path.insert(0, str(T416_DIR))
sys.path.insert(0, str(T419_DIR))
sys.path.insert(0, str(T420_DIR))
import t416_dual_irrationality_time_tracking as t416  # noqa: E402
import t420_information3_handover as t420  # noqa: E402


SEED = 421
LAGS = tuple(range(-8, 9))
BRANCH_HALF_WIDTH = 4
EVENT_HALF_WIDTH = 8
SHIFT_DRAWS = 1000
BOOTSTRAPS = 10000
EPS = 1e-12


def write_csv_or_header(path: Path, rows: list[dict], header: list[str]) -> None:
    if rows:
        t420.write_csv(path, rows)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(",".join(header) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relation_metrics(phase_history: np.ndarray) -> dict:
    _, local_loss, null_loss = t416.stochastic_residual(phase_history)
    vector = np.exp(2j * np.pi * phase_history)
    relations = np.asarray([
        np.mean(vector[lag:] * np.conj(vector[:-lag]))
        for lag in range(1, t416.MAX_LAG + 1)
    ])
    magnitude = np.abs(relations)
    angle = np.angle(relations)
    denominator = local_loss + null_loss
    unit = relations / np.maximum(magnitude, EPS)
    branch = np.mean(unit)
    return {
        "U": float(1.0 if denominator <= EPS else 2.0 * local_loss / denominator),
        "R": float(2.0 * np.median(magnitude)),
        "H": float(2.0 * np.median(np.abs(angle) / np.pi)),
        "Q": float(1.0 + np.imag(branch)),
        "Q_concentration": float(abs(branch)),
        "local_loss": float(local_loss),
        "null_loss": float(null_loss),
    }


def analyse_run_period(row: dict, period: str) -> list[dict]:
    data = t416.t414.load_run(row)
    period_index = 0 if period == "RF on" else 1
    counts = data["counts"][period_index]
    time = data["time"]
    field = float(row["field_G"])
    frequency = t416.GAMMA_MHZ_PER_G * field
    correct = t416.extract_spin_path(time, counts, frequency)
    dt = float(np.median(np.diff(correct["time"])))
    cycle_bins = max(4, int(round(1.0 / max(frequency * dt, EPS))))
    wrong_frequencies = []
    for k in t416.WRONG_K:
        for sign in (-1.0, 1.0):
            candidate = frequency + sign * float(k) / t416.LENGTH_US
            if candidate > 0.05:
                wrong_frequencies.append(candidate)
    wrong_paths = [t416.extract_spin_path(time, counts, candidate) for candidate in wrong_frequencies]
    turns_per_lifetime = max(frequency * t416.TAU_US, EPS)
    start = max(t416.PATH_WINDOW - 1, cycle_bins)
    output = []
    for end in range(start, len(correct["time"]), t416.PATH_STEP):
        history = correct["phase"][end - t416.PATH_WINDOW + 1 : end + 1]
        measured = relation_metrics(history)
        wrong = [
            relation_metrics(path["phase"][end - t416.PATH_WINDOW + 1 : end + 1])
            for path in wrong_paths
        ]
        time_us = float(correct["time"][end])
        output.append({
            "split": row["split"], "run": row["run"], "period": period,
            "rf_flag": int(period == "RF on"), "temperature_K": float(row["temperature_K"]),
            "field_G": field, "frequency_MHz": frequency,
            "turns_per_lifetime": turns_per_lifetime,
            "field_turn_log2": math.log2(turns_per_lifetime),
            "time_us": time_us,
            "parent_lifespan_ARA": 2.0 * (1.0 - math.exp(-time_us / t416.TAU_US)),
            "openness_U": measured["U"], "closure_R": measured["R"],
            "parent_H": measured["H"], "signed_parent_Q": measured["Q"],
            "Q_concentration": measured["Q_concentration"],
            "child_distance": abs(measured["U"] - measured["R"]),
            "parent_ridge_distance": abs(measured["H"] - 1.0),
            "wrong_parent_H": float(np.median([item["H"] for item in wrong])),
            "wrong_signed_Q": float(np.median([item["Q"] for item in wrong])),
            "cycle_bins": cycle_bins, "history_native_bins": t416.PATH_WINDOW,
        })
    return output


def groups(rows: list[dict]) -> dict[tuple[str, str], list[dict]]:
    output: dict[tuple[str, str], list[dict]] = {}
    for row in rows:
        output.setdefault((str(row["run"]), str(row["period"])), []).append(row)
    for key in output:
        output[key].sort(key=lambda item: float(item["time_us"]))
    return output


def at(series: np.ndarray, position: float, circular: bool = False) -> float:
    n = len(series)
    if circular:
        position %= n
        lo = int(math.floor(position)) % n
        hi = (lo + 1) % n
    else:
        if position < 0 or position > n - 1:
            return float("nan")
        lo = int(math.floor(position))
        hi = min(lo + 1, n - 1)
    fraction = position - math.floor(position)
    return float(series[lo] + fraction * (series[hi] - series[lo]))


def crossing_positions(rows: list[dict]) -> list[dict]:
    u = np.asarray([float(row["openness_U"]) for row in rows])
    r = np.asarray([float(row["closure_R"]) for row in rows])
    output = []
    for index in range(1, len(rows)):
        da, db = u[index - 1] - r[index - 1], u[index] - r[index]
        if da == 0.0:
            fraction = 0.0
        elif db == 0.0:
            fraction = 1.0
        elif da * db > 0.0:
            continue
        else:
            fraction = float(-da / (db - da))
        if not 0.0 <= fraction <= 1.0:
            continue
        position = index - 1 + fraction
        output.append({
            "child_position": position,
            "crossing_U": at(u, position),
            "crossing_R": at(r, position),
            "direction": "R_to_U" if da < 0.0 and db > 0.0 else "U_to_R",
        })
    return output


def mismatch_map(timeline: list[dict]) -> dict[tuple[str, str], tuple[str, str]]:
    by_period: dict[str, list[tuple[float, tuple[str, str]]]] = {}
    for key, rows in groups(timeline).items():
        by_period.setdefault(key[1], []).append((float(rows[0]["field_G"]), key))
    output = {}
    for period, items in by_period.items():
        ordered = [key for _, key in sorted(items)]
        for index, key in enumerate(ordered):
            output[key] = ordered[(index + 1) % len(ordered)]
    return output


def circular_branch_delta(series: np.ndarray, center: float) -> float:
    before = [at(series, center - offset, circular=True) for offset in range(BRANCH_HALF_WIDTH, 0, -1)]
    after = [at(series, center + offset, circular=True) for offset in range(1, BRANCH_HALF_WIDTH + 1)]
    return float(np.median(after) - np.median(before))


def all_shift_branch_delta(series: np.ndarray, center: float) -> float:
    deltas = [circular_branch_delta(series, center + shift) for shift in range(1, len(series))]
    return float(np.median(deltas))


def build_events(timeline: list[dict], lag: int, orientation: int = 1) -> tuple[list[dict], list[dict]]:
    grouped = groups(timeline)
    mismatch = mismatch_map(timeline)
    events, centered = [], []
    for key, rows in sorted(grouped.items()):
        h = np.asarray([float(row["parent_H"]) for row in rows])
        q = np.asarray([float(row["signed_parent_Q"]) for row in rows])
        wh = np.asarray([float(row["wrong_parent_H"]) for row in rows])
        wq = np.asarray([float(row["wrong_signed_Q"]) for row in rows])
        mismatch_rows = grouped[mismatch[key]]
        mh = np.asarray([float(row["parent_H"]) for row in mismatch_rows])
        history_dp = float(np.median(np.abs(h - 1.0)))
        for event_index, base in enumerate(crossing_positions(rows)):
            child_position = float(base["child_position"])
            parent_position = child_position + lag
            cross_h = at(h, parent_position)
            cross_q = at(q, parent_position)
            wrong_h = at(wh, parent_position)
            if not np.isfinite(cross_h):
                continue
            progress = child_position / max(len(rows) - 1, 1)
            mismatch_h = at(mh, progress * (len(mh) - 1))
            time_us = at(np.asarray([float(row["time_us"]) for row in rows]), child_position)
            parent_time = at(np.asarray([float(row["time_us"]) for row in rows]), parent_position)
            direction_code = 1 if base["direction"] == "R_to_U" else -1
            eligible = parent_position - BRANCH_HALF_WIDTH >= 0 and parent_position + BRANCH_HALF_WIDTH <= len(rows) - 1
            delta_q = circular_branch_delta(q, parent_position) if eligible else float("nan")
            wrong_delta_q = circular_branch_delta(wq, parent_position) if eligible else float("nan")
            shifted_delta_q = all_shift_branch_delta(q, parent_position) if eligible else float("nan")
            raw_branch = direction_code * delta_q if eligible else float("nan")
            branch = orientation * raw_branch if eligible else float("nan")
            event_id = f"{key[0]}|{key[1]}|{event_index}|lag{lag:+d}"
            event = {
                "split": rows[0]["split"], "event_id": event_id, "run": key[0], "period": key[1],
                "rf_flag": rows[0]["rf_flag"], "temperature_K": rows[0]["temperature_K"],
                "field_G": rows[0]["field_G"], "direction": base["direction"],
                "lag_reads": lag, "child_position": child_position, "parent_position": parent_position,
                "crossing_time_us": time_us, "parent_time_us": parent_time,
                "crossing_U": base["crossing_U"], "crossing_R": base["crossing_R"],
                "parent_H": cross_h, "signed_parent_Q": cross_q,
                "parent_ridge_distance": abs(cross_h - 1.0),
                "history_parent_distance": history_dp,
                "ridge_exposure": history_dp - abs(cross_h - 1.0),
                "wrong_parent_H": wrong_h, "wrong_parent_distance": abs(wrong_h - 1.0),
                "wrong_minus_correct_distance": abs(wrong_h - 1.0) - abs(cross_h - 1.0),
                "mismatch_parent_H": mismatch_h, "mismatch_parent_distance": abs(mismatch_h - 1.0),
                "mismatch_minus_correct_distance": abs(mismatch_h - 1.0) - abs(cross_h - 1.0),
                "branch_eligible": int(eligible), "delta_Q": delta_q,
                "raw_oriented_branch": raw_branch, "oriented_branch": branch,
                "wrong_oriented_branch": orientation * direction_code * wrong_delta_q if eligible else float("nan"),
                "shifted_oriented_branch": orientation * direction_code * shifted_delta_q if eligible else float("nan"),
            }
            if eligible:
                event["correct_minus_wrong_branch"] = event["oriented_branch"] - event["wrong_oriented_branch"]
                event["correct_minus_shifted_branch"] = event["oriented_branch"] - event["shifted_oriented_branch"]
            else:
                event["correct_minus_wrong_branch"] = float("nan")
                event["correct_minus_shifted_branch"] = float("nan")
            events.append(event)
            for offset in range(-EVENT_HALF_WIDTH, EVENT_HALF_WIDTH + 1):
                child_at = child_position + offset
                parent_at = parent_position + offset
                if child_at < 0 or child_at > len(rows) - 1 or parent_at < 0 or parent_at > len(rows) - 1:
                    continue
                centered.append({
                    "split": rows[0]["split"], "event_id": event_id, "run": key[0], "period": key[1],
                    "field_G": rows[0]["field_G"], "direction": base["direction"], "lag_reads": lag,
                    "offset_reads": offset,
                    "offset_us": at(np.asarray([float(row["time_us"]) for row in rows]), child_at) - time_us,
                    "child_U": at(np.asarray([float(row["openness_U"]) for row in rows]), child_at),
                    "child_R": at(np.asarray([float(row["closure_R"]) for row in rows]), child_at),
                    "parent_H": at(h, parent_at), "signed_parent_Q": at(q, parent_at),
                })
    return events, centered


def field_values(rows: list[dict], key: str) -> dict[float, float]:
    output = {}
    for field in sorted({float(row["field_G"]) for row in rows}):
        values = [float(row[key]) for row in rows if float(row["field_G"]) == field and np.isfinite(float(row[key]))]
        if values:
            output[field] = float(np.median(values))
    return output


def aggregate(rows: list[dict], key: str) -> float:
    values = list(field_values(rows, key).values())
    return float(np.median(values)) if values else float("nan")


def bootstrap(rows: list[dict], key: str, seed: int) -> dict:
    field = field_values(rows, key)
    values = np.asarray([field[k] for k in sorted(field)], dtype=float)
    if len(values) == 0:
        return {"median": float("nan"), "ci95": [float("nan"), float("nan")], "field_count": 0}
    rng = np.random.default_rng(seed)
    draws = rng.choice(values, size=(BOOTSTRAPS, len(values)), replace=True)
    medians = np.median(draws, axis=1)
    return {"median": float(np.median(values)), "ci95": [float(np.percentile(medians, 2.5)), float(np.percentile(medians, 97.5))], "field_count": len(values)}


def lag_profile(timeline: list[dict]) -> list[dict]:
    output = []
    for lag in LAGS:
        events, _ = build_events(timeline, lag)
        output.append({
            "split": timeline[0]["split"], "lag_reads": lag,
            "lag_us_median": float(lag * np.median(np.diff([float(row["time_us"]) for row in next(iter(groups(timeline).values()))]))),
            "event_count": len(events), "field_count": len(field_values(events, "parent_ridge_distance")),
            "parent_ridge_distance": aggregate(events, "parent_ridge_distance"),
            "ridge_exposure": aggregate(events, "ridge_exposure"),
        })
    return output


def choose_lag(profile: list[dict]) -> int:
    ordered = sorted(profile, key=lambda row: (float(row["parent_ridge_distance"]), abs(int(row["lag_reads"])), int(row["lag_reads"])))
    return int(ordered[0]["lag_reads"])


def choose_orientation(events: list[dict]) -> int:
    value = aggregate(events, "raw_oriented_branch")
    return 1 if not np.isfinite(value) or value >= 0 else -1


def shift_null(timeline: list[dict], lag: int) -> np.ndarray:
    grouped = groups(timeline)
    positions = {key: crossing_positions(rows) for key, rows in grouped.items()}
    rng = np.random.default_rng(SEED + 100)
    draws = np.empty(SHIFT_DRAWS, dtype=float)
    for draw in range(SHIFT_DRAWS):
        pseudo = []
        for key, rows in sorted(grouped.items()):
            h = np.asarray([float(row["parent_H"]) for row in rows])
            choices = np.arange(1, len(h), dtype=int)
            shift = int(rng.choice(choices))
            for event_index, base in enumerate(positions[key]):
                position = float(base["child_position"]) + lag + shift
                value = at(h, position, circular=True)
                pseudo.append({"field_G": rows[0]["field_G"], "distance": abs(value - 1.0)})
        draws[draw] = aggregate(pseudo, "distance")
    return draws


def summarize(stage: str, timeline: list[dict], lag: int, orientation: int) -> tuple[dict, list[dict], list[dict], list[dict], np.ndarray]:
    profile = lag_profile(timeline)
    events, centered = build_events(timeline, lag, orientation)
    zero_events, _ = build_events(timeline, 0, orientation)
    eligible = [row for row in events if int(row["branch_eligible"]) == 1]
    shifts = shift_null(timeline, lag)
    real_distance = aggregate(events, "parent_ridge_distance")
    timing_available = bool(bool(events) and np.isfinite(real_distance) and np.all(np.isfinite(shifts)))
    shift_p = (
        float((1 + np.count_nonzero(shifts <= real_distance)) / (1 + len(shifts)))
        if timing_available else float("nan")
    )
    zero_exposure = bootstrap(zero_events, "ridge_exposure", SEED + 1)
    exposure = bootstrap(events, "ridge_exposure", SEED + 2)
    wrong = bootstrap(events, "wrong_minus_correct_distance", SEED + 3)
    mismatch = bootstrap(events, "mismatch_minus_correct_distance", SEED + 4)
    branch = bootstrap(eligible, "oriented_branch", SEED + 5)
    branch_wrong = bootstrap(eligible, "correct_minus_wrong_branch", SEED + 6)
    branch_shift = bootstrap(eligible, "correct_minus_shifted_branch", SEED + 7)
    availability = float(np.mean([
        np.isfinite(float(row[key]))
        for row in timeline
        for key in ("openness_U", "closure_R", "parent_H", "signed_parent_Q", "wrong_parent_H", "wrong_signed_Q")
    ]))
    gates = {
        "G1_availability": {"pass": availability == 1.0, "value": availability},
        "G2_literal_hierarchy": {"pass": zero_exposure["ci95"][0] > 0.0, "effect": zero_exposure},
        "G3_frozen_offset_hierarchy": {"pass": exposure["ci95"][0] > 0.0, "effect": exposure},
        "G4_timing_specificity": {"pass": bool(timing_available and shift_p < 0.05), "available": timing_available, "empirical_p": shift_p, "real_distance": real_distance, "null_median": float(np.median(shifts))},
        "G5_frequency_specificity": {"pass": wrong["ci95"][0] > 0.0, "effect": wrong},
        "G6_lineage_specificity": {"pass": mismatch["ci95"][0] > 0.0, "effect": mismatch},
        "G7_signed_reversal": {"pass": branch["ci95"][0] > 0.0, "effect": branch},
        "G8_signed_controls": {"pass": branch_wrong["ci95"][0] > 0.0 and branch_shift["ci95"][0] > 0.0, "wrong_effect": branch_wrong, "shift_effect": branch_shift},
    }
    parent_values = np.asarray([float(row["parent_H"]) for row in events])
    median_child = float(np.median([float(row["crossing_U"]) for row in events])) if events else float("nan")
    median_parent = float(np.median(parent_values)) if events else float("nan")
    median_parent_distance = float(np.median(np.abs(parent_values - 1.0))) if events else float("nan")
    result = {
        "test": "T421 child singularity / parent ridge hierarchy", "stage": stage,
        "identity": "muoniated-acetone detector-population spin relation",
        "hierarchy": {"child": "U/R crossover", "parent": "lag-angle H", "signed_parent_branch": "Q"},
        "selected_lag_reads": lag,
        "selected_lag_us_median": float(next(row["lag_us_median"] for row in profile if int(row["lag_reads"]) == lag)),
        "orientation_sign": orientation, "timeline_rows": len(timeline),
        "sequence_count": len(groups(timeline)), "event_count": len(events),
        "zero_lag_event_count": len(zero_events), "branch_eligible_events": len(eligible),
        "field_count": len(field_values(events, "parent_ridge_distance")),
        "crossing": {
            "median_child_coordinate": median_child,
            "median_parent_H": median_parent,
            "median_parent_ridge_distance": median_parent_distance,
            "field_balanced_parent_ridge_distance": real_distance,
            "zero_lag_exposure": zero_exposure, "frozen_lag_exposure": exposure,
            "wrong_frequency_effect": wrong, "mismatch_lineage_effect": mismatch,
            "shift": {"empirical_p": shift_p, "null_median": float(np.median(shifts)), "real_distance": real_distance},
        },
        "signed_branch": {"oriented_effect": branch, "correct_minus_wrong": branch_wrong, "correct_minus_shifted": branch_shift},
        "gates": gates,
        "narrow_hierarchy_supported": bool(all(gates[key]["pass"] for key in ("G1_availability", "G2_literal_hierarchy", "G3_frozen_offset_hierarchy", "G4_timing_specificity", "G5_frequency_specificity", "G6_lineage_specificity"))),
        "full_hierarchy_supported": bool(all(item["pass"] for item in gates.values())),
        "protocol_sha256": sha256(PROTOCOL), "analysis_sha256": sha256(Path(__file__).resolve()),
    }
    return result, events, centered, profile, shifts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True, choices=("development", "validation", "holdout"))
    args = parser.parse_args()
    stage = args.stage
    manifest = [row for row in t416.t414.read_manifest() if row["split"] == stage]
    timeline = []
    for index, row in enumerate(manifest, start=1):
        print(f"{stage}: {index}/{len(manifest)} {row['run']} {row['field_G']:.0f} G", flush=True)
        for period in ("RF on", "RF off"):
            timeline.extend(analyse_run_period(row, period))
    profile = lag_profile(timeline)
    if stage == "development":
        lag = choose_lag(profile)
        preliminary, _ = build_events(timeline, lag, 1)
        orientation = choose_orientation(preliminary)
        freeze = {
            "selected_lag_reads": lag, "orientation_sign": orientation,
            "protocol_sha256": sha256(PROTOCOL), "analysis_sha256": sha256(Path(__file__).resolve()),
            "constants": {"lags": list(LAGS), "branch_half_width": BRANCH_HALF_WIDTH, "event_half_width": EVENT_HALF_WIDTH, "shift_draws": SHIFT_DRAWS, "bootstraps": BOOTSTRAPS, "seed": SEED},
        }
        t420.write_json(FREEZE, freeze)
    else:
        freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
        if freeze["protocol_sha256"] != sha256(PROTOCOL) or freeze["analysis_sha256"] != sha256(Path(__file__).resolve()):
            raise RuntimeError("T421 protocol or analysis changed after development freeze")
        lag = int(freeze["selected_lag_reads"])
        orientation = int(freeze["orientation_sign"])
    result, events, centered, profile, shifts = summarize(stage, timeline, lag, orientation)
    result["source_hashes"] = {row["run"]: sha256(t416.t414.RAW / f"{row['run']}.nxs") for row in manifest}
    tag = stage.upper()
    RESULTS.mkdir(parents=True, exist_ok=True)
    t420.write_csv(RESULTS / f"T421_{tag}_TIMELINE.csv", timeline)
    write_csv_or_header(
        RESULTS / f"T421_{tag}_EVENTS.csv", events,
        ["split", "event_id", "run", "period", "field_G", "direction", "lag_reads", "child_position", "parent_position", "crossing_time_us", "parent_time_us", "crossing_U", "crossing_R", "parent_H", "signed_parent_Q", "parent_ridge_distance", "history_parent_distance", "ridge_exposure", "wrong_parent_H", "wrong_parent_distance", "wrong_minus_correct_distance", "mismatch_parent_H", "mismatch_parent_distance", "mismatch_minus_correct_distance", "branch_eligible", "delta_Q", "raw_oriented_branch", "oriented_branch", "wrong_oriented_branch", "shifted_oriented_branch", "correct_minus_wrong_branch", "correct_minus_shifted_branch"],
    )
    write_csv_or_header(
        RESULTS / f"T421_{tag}_EVENT_CENTERED.csv", centered,
        ["split", "event_id", "run", "period", "field_G", "direction", "lag_reads", "offset_reads", "offset_us", "child_U", "child_R", "parent_H", "signed_parent_Q"],
    )
    t420.write_csv(RESULTS / f"T421_{tag}_LAG_PROFILE.csv", profile)
    t420.write_csv(RESULTS / f"T421_{tag}_SHIFT_NULL.csv", [{"split": stage, "draw": i, "parent_ridge_distance": value} for i, value in enumerate(shifts)])
    t420.write_json(RESULTS / f"T421_{tag}_RESULTS.json", result)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
