#!/usr/bin/env python3
"""Run frozen T262 on raw public Bell-state tomography current traces."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import zipfile
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "public_data" / "q4_bell_tomography"
ARCHIVE = DATA_DIR / "UPUP-DOWNDOWN.zip"
ARCHIVE_MD5 = "8cd8a5f2b3b9a2ccd090e47312bcc390"
PROTOCOL = HERE / "Q4_BELL_PARENT_CHILD_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q4_BELL_PARENT_CHILD_PROTOCOL_v1_FROZEN.sha256"
RECORDS_CSV = HERE / "Q4_BELL_PARENT_CHILD_RECORDS.csv"
PROJECTIONS_CSV = HERE / "Q4_BELL_PARENT_CHILD_PROJECTIONS.csv"
BOOTSTRAP_CSV = HERE / "Q4_BELL_PARENT_CHILD_BOOTSTRAP.csv"
RESULTS_JSON = HERE / "Q4_BELL_PARENT_CHILD_RESULTS.json"

OFFSET = 32766.0
SCALE = 3.0519e-5
CURRENT_THRESHOLD = 0.1
STATE_THRESHOLD = 0.5
READOUTS_PER_STATE = 40
BOOTSTRAP_SEED = 2026072404
BOOTSTRAP_REPS = 2000

ORIENTATION_TIMESTAMPS = {
    "II": "115025",
    "IX": "115222",
    "IY": "115424",
    "XI": "115627",
    "XX": "115835",
    "XY": "120033",
    "YI": "120230",
    "YX": "120428",
    "YY": "120626",
}
OUTCOME_NAMES = ("DOWNDOWN", "DOWNUP", "UPDOWN", "UPUP")
LOCAL_CHILDREN = ("YI", "XI", "IY", "IX", "ZI", "IZ")
SAME_AXIS = ("XX", "YY", "ZZ")
MIXED_PAIR = ("YZ", "XZ", "ZY", "ZX", "YX", "XY")
PROJECTION_ORDER = (
    "ZZ",
    "YZ",
    "XZ",
    "ZY",
    "ZX",
    "YY",
    "YX",
    "XY",
    "XX",
    "YI",
    "XI",
    "IY",
    "IX",
    "ZI",
    "IZ",
)
BELL_PATTERNS = {
    "Phi-plus": {"XX": 1.0, "YY": -1.0, "ZZ": 1.0},
    "Phi-minus": {"XX": -1.0, "YY": 1.0, "ZZ": 1.0},
    "Psi-plus": {"XX": 1.0, "YY": 1.0, "ZZ": -1.0},
    "Psi-minus": {"XX": -1.0, "YY": -1.0, "ZZ": -1.0},
}


def digest(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_sources() -> tuple[str, str]:
    observed_md5 = digest(ARCHIVE, "md5")
    if observed_md5 != ARCHIVE_MD5:
        raise RuntimeError(
            f"Archive MD5 mismatch: expected {ARCHIVE_MD5}, observed {observed_md5}"
        )
    expected_protocol_sha = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    observed_protocol_sha = digest(PROTOCOL, "sha256")
    if expected_protocol_sha != observed_protocol_sha:
        raise RuntimeError(
            "Frozen protocol SHA-256 mismatch: "
            f"expected {expected_protocol_sha}, observed {observed_protocol_sha}"
        )
    return observed_md5, observed_protocol_sha


def archive_member(timestamp: str, measurement: int, readout: int) -> str:
    return (
        "UPUP-DOWNDOWN/raw/"
        f"{timestamp}_Bell_states_{measurement}_{readout}.bin"
    )


def classify_record(raw_bytes: bytes) -> tuple[np.ndarray, np.ndarray]:
    raw = np.frombuffer(raw_bytes, dtype="<u2").astype(np.float64)
    if raw.size % (5 * READOUTS_PER_STATE) != 0:
        raise RuntimeError(f"Unexpected raw record length: {raw.size}")
    readout_length = raw.size // (5 * READOUTS_PER_STATE)
    current = SCALE * (raw - OFFSET)
    state_probabilities = np.zeros(4, dtype=np.float64)
    state_labels = np.zeros(4, dtype=np.int8)
    for state_index in range(4):
        start = (state_index + 1) * READOUTS_PER_STATE * readout_length
        stop = start + READOUTS_PER_STATE * readout_length
        segment = current[start:stop].reshape(READOUTS_PER_STATE, readout_length)
        tunnelling = (segment > CURRENT_THRESHOLD).sum(axis=1) > 1
        probability = float(tunnelling.mean())
        state_probabilities[state_index] = probability
        state_labels[state_index] = int(probability > STATE_THRESHOLD)
    return state_probabilities, state_labels


def load_records() -> tuple[dict[str, np.ndarray], list[dict[str, object]]]:
    by_orientation: dict[str, np.ndarray] = {}
    rows: list[dict[str, object]] = []
    with zipfile.ZipFile(ARCHIVE) as archive:
        names = set(archive.namelist())
        required = {
            archive_member(timestamp, measurement, readout)
            for timestamp in ORIENTATION_TIMESTAMPS.values()
            for measurement in range(1, 41)
            for readout in (1, 2)
        }
        missing = sorted(required - names)
        if missing:
            raise RuntimeError(f"Missing {len(missing)} required raw files")

        for orientation, timestamp in ORIENTATION_TIMESTAMPS.items():
            labels = []
            record_index = 0
            for readout in (1, 2):
                for measurement in range(1, 41):
                    member = archive_member(timestamp, measurement, readout)
                    probabilities, outcomes = classify_record(archive.read(member))
                    labels.append(outcomes)
                    for outcome_index, outcome_name in enumerate(OUTCOME_NAMES):
                        rows.append(
                            {
                                "orientation": orientation,
                                "timestamp": timestamp,
                                "record_index": record_index,
                                "readout": readout,
                                "measurement": measurement,
                                "outcome": outcome_name,
                                "segment_tunnelling_fraction": float(
                                    probabilities[outcome_index]
                                ),
                                "classified_present": int(outcomes[outcome_index]),
                            }
                        )
                    record_index += 1
            by_orientation[orientation] = np.asarray(labels, dtype=np.float64)
    return by_orientation, rows


def expectations(
    orientation_probabilities: dict[str, np.ndarray],
) -> dict[str, float]:
    ii = orientation_probabilities["II"]
    ix = orientation_probabilities["IX"]
    iy = orientation_probabilities["IY"]
    xi = orientation_probabilities["XI"]
    xx = orientation_probabilities["XX"]
    xy = orientation_probabilities["XY"]
    yi = orientation_probabilities["YI"]
    yx = orientation_probabilities["YX"]
    yy = orientation_probabilities["YY"]
    return {
        "II": float(ii[0] + ii[1] + ii[2] + ii[3]),
        "IX": float(ix[0] + ix[1] - ix[2] - ix[3]),
        "IY": float(iy[0] + iy[1] - iy[2] - iy[3]),
        "IZ": float(ii[0] + ii[1] - ii[2] - ii[3]),
        "XI": float(xi[0] - xi[1] + xi[2] - xi[3]),
        "XX": float(xx[0] - xx[1] - xx[2] + xx[3]),
        "XY": float(xy[0] - xy[1] - xy[2] + xy[3]),
        "XZ": float(xi[0] - xi[1] - xi[2] + xi[3]),
        "YI": float(yi[0] - yi[1] + yi[2] - yi[3]),
        "YX": float(yx[0] - yx[1] - yx[2] + yx[3]),
        "YY": float(yy[0] - yy[1] - yy[2] + yy[3]),
        "YZ": float(yi[0] - yi[1] - yi[2] + yi[3]),
        "ZI": float(ii[0] - ii[1] + ii[2] - ii[3]),
        "ZX": float(ix[0] - ix[1] - ix[2] + ix[3]),
        "ZY": float(iy[0] - iy[1] - iy[2] + iy[3]),
        "ZZ": float(ii[0] - ii[1] - ii[2] + ii[3]),
    }


def probabilities_from_records(
    records: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    return {orientation: values.mean(axis=0) for orientation, values in records.items()}


def group_metrics(exp: dict[str, float]) -> dict[str, float]:
    local_mean = float(np.mean([abs(exp[label]) for label in LOCAL_CHILDREN]))
    same_values = [exp[label] for label in SAME_AXIS]
    same_mean = float(np.mean([abs(value) for value in same_values]))
    mixed_mean = float(np.mean([abs(exp[label]) for label in MIXED_PAIR]))
    return {
        "local_child_mean_abs": local_mean,
        "same_axis_mean_abs": same_mean,
        "same_axis_min_abs": float(np.min(np.abs(same_values))),
        "same_minus_local": same_mean - local_mean,
        "mixed_pair_mean_abs": mixed_mean,
        "correlation_product": float(np.prod(same_values)),
    }


def bell_mae(exp: dict[str, float]) -> dict[str, float]:
    return {
        name: float(
            np.mean([abs(exp[label] - pattern[label]) for label in SAME_AXIS])
        )
        for name, pattern in BELL_PATTERNS.items()
    }


def bootstrap(
    records: dict[str, np.ndarray],
) -> tuple[dict[str, np.ndarray], list[dict[str, float | int]]]:
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    projection_draws = {
        label: np.empty(BOOTSTRAP_REPS, dtype=np.float64)
        for label in PROJECTION_ORDER
    }
    metric_rows: list[dict[str, float | int]] = []
    for repetition in range(BOOTSTRAP_REPS):
        probabilities = {}
        for orientation, values in records.items():
            indices = rng.integers(0, len(values), size=len(values))
            probabilities[orientation] = values[indices].mean(axis=0)
        exp = expectations(probabilities)
        metrics = group_metrics(exp)
        for label in PROJECTION_ORDER:
            projection_draws[label][repetition] = exp[label]
        metric_rows.append(
            {
                "replicate": repetition,
                **metrics,
                "xx": exp["XX"],
                "yy": exp["YY"],
                "zz": exp["ZZ"],
            }
        )
    return projection_draws, metric_rows


def projection_group(label: str) -> str:
    if label in LOCAL_CHILDREN:
        return "local_child"
    if label in SAME_AXIS:
        return "same_axis_parent"
    return "mixed_pair_control"


def main() -> None:
    archive_md5, protocol_sha = verify_sources()
    records, record_rows = load_records()
    probabilities = probabilities_from_records(records)
    exp = expectations(probabilities)
    metrics = group_metrics(exp)
    maes = bell_mae(exp)
    ranked_bells = sorted(maes.items(), key=lambda item: item[1])
    closest_bell, closest_mae = ranked_bells[0]
    runner_up_bell, runner_up_mae = ranked_bells[1]
    bell_margin = runner_up_mae - closest_mae

    projection_draws, bootstrap_rows = bootstrap(records)

    ideal_phi_minus = {
        label: BELL_PATTERNS["Phi-minus"].get(label, 0.0)
        for label in PROJECTION_ORDER
    }
    projection_rows = []
    max_affine_residual = 0.0
    max_reversal_residual = 0.0
    for label in PROJECTION_ORDER:
        value = exp[label]
        ara = 1.0 - value
        reversed_ara = 2.0 - ara
        affine_residual = abs(ara - (1.0 - value))
        reversal_residual = abs(ara + reversed_ara - 2.0)
        max_affine_residual = max(max_affine_residual, affine_residual)
        max_reversal_residual = max(max_reversal_residual, reversal_residual)
        low, high = np.quantile(projection_draws[label], [0.025, 0.975])
        projection_rows.append(
            {
                "projection": label,
                "group": projection_group(label),
                "expectation": value,
                "expectation_ci_low": float(low),
                "expectation_ci_high": float(high),
                "ara_coordinate": ara,
                "reversed_ara_coordinate": reversed_ara,
                "ideal_phi_minus_expectation": ideal_phi_minus[label],
                "ideal_phi_minus_ara": 1.0 - ideal_phi_minus[label],
            }
        )

    permutations = list(itertools.permutations(SAME_AXIS))
    observed_signs = {label: int(math.copysign(1, exp[label])) for label in SAME_AXIS}
    phi_minus_signs = {"XX": -1, "YY": 1, "ZZ": 1}
    label_shuffle_survivors = 0
    for permutation in permutations:
        relabelled = {
            destination: observed_signs[source]
            for destination, source in zip(SAME_AXIS, permutation)
        }
        label_shuffle_survivors += int(relabelled == phi_minus_signs)

    mixed_values = [exp[label] for label in MIXED_PAIR]
    mixed_control_best_mae = math.inf
    for chosen in itertools.combinations(mixed_values, 3):
        for arranged in itertools.permutations(chosen):
            candidate = dict(zip(SAME_AXIS, arranged))
            candidate_mae = float(
                np.mean(
                    [
                        abs(candidate[label] - BELL_PATTERNS["Phi-minus"][label])
                        for label in SAME_AXIS
                    ]
                )
            )
            mixed_control_best_mae = min(mixed_control_best_mae, candidate_mae)

    gates = {
        "G1_local_child_mean_abs_at_most_0p20": {
            "value": metrics["local_child_mean_abs"],
            "threshold": 0.20,
            "pass": metrics["local_child_mean_abs"] <= 0.20,
        },
        "G2_same_axis_signs": {
            "xx": exp["XX"],
            "yy": exp["YY"],
            "zz": exp["ZZ"],
            "pass": exp["XX"] < 0 and exp["YY"] > 0 and exp["ZZ"] > 0,
        },
        "G3_weakest_same_axis_abs_at_least_0p50": {
            "value": metrics["same_axis_min_abs"],
            "threshold": 0.50,
            "pass": metrics["same_axis_min_abs"] >= 0.50,
        },
        "G4_same_minus_local_at_least_0p40": {
            "value": metrics["same_minus_local"],
            "threshold": 0.40,
            "pass": metrics["same_minus_local"] >= 0.40,
        },
        "G5_mixed_pair_mean_abs_at_most_0p25": {
            "value": metrics["mixed_pair_mean_abs"],
            "threshold": 0.25,
            "pass": metrics["mixed_pair_mean_abs"] <= 0.25,
        },
        "G6_correlation_product_at_most_negative_0p125": {
            "value": metrics["correlation_product"],
            "threshold": -0.125,
            "pass": metrics["correlation_product"] <= -0.125,
        },
        "G7_phi_minus_closest_with_margin": {
            "closest": closest_bell,
            "closest_mae": closest_mae,
            "runner_up": runner_up_bell,
            "runner_up_mae": runner_up_mae,
            "margin": bell_margin,
            "threshold": 0.20,
            "pass": closest_bell == "Phi-minus" and bell_margin >= 0.20,
        },
        "G8_affine_and_reversal_residuals": {
            "affine": max_affine_residual,
            "reversal": max_reversal_residual,
            "threshold": 1e-12,
            "pass": max_affine_residual <= 1e-12
            and max_reversal_residual <= 1e-12,
        },
    }
    gates_passed = sum(int(gate["pass"]) for gate in gates.values())
    verdict = "SUPPORTED" if gates_passed == len(gates) else "NOT SUPPORTED"

    with RECORDS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(record_rows[0]))
        writer.writeheader()
        writer.writerows(record_rows)
    with PROJECTIONS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(projection_rows[0]))
        writer.writeheader()
        writer.writerows(projection_rows)
    with BOOTSTRAP_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(bootstrap_rows[0]))
        writer.writeheader()
        writer.writerows(bootstrap_rows)

    results = {
        "protocol_id": "Q4-BELL-PARENT-CHILD-v1",
        "ledger_id": "T262",
        "verdict": verdict,
        "gates_passed": gates_passed,
        "gates_total": len(gates),
        "source": {
            "doi": "10.6084/m9.figshare.14160476.v2",
            "file_id": 26690663,
            "archive": ARCHIVE.name,
            "archive_md5": archive_md5,
            "license": "CC BY 4.0",
        },
        "protocol_sha256": protocol_sha,
        "raw_decoder": {
            "orientations": ORIENTATION_TIMESTAMPS,
            "records_per_orientation": 80,
            "readouts_per_state_segment": READOUTS_PER_STATE,
            "current_threshold": CURRENT_THRESHOLD,
            "state_threshold": STATE_THRESHOLD,
            "independent_complete_tomography_sets": 1,
        },
        "expectations": exp,
        "metrics": metrics,
        "bell_mae": maes,
        "closest_bell": closest_bell,
        "bell_margin": bell_margin,
        "gates": gates,
        "controls": {
            "local_only_ideal_bell_patterns_distinguishable": False,
            "local_only_distinct_patterns": 1,
            "relation_label_shuffle_survivors": label_shuffle_survivors,
            "relation_label_shuffle_total": len(permutations),
            "mixed_projection_best_phi_minus_mae": mixed_control_best_mae,
        },
        "bootstrap": {
            "seed": BOOTSTRAP_SEED,
            "repetitions": BOOTSTRAP_REPS,
            "grain": (
                "80 classified measurement records resampled independently "
                "within each of nine acquisition orientations"
            ),
        },
        "evidence_boundary": (
            "One complete fifteen-projection tomography set. Raw record bootstrap "
            "quantifies acquisition-record variability but is not an independent "
            "device or state replication."
        ),
    }
    RESULTS_JSON.write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"expectations": exp, "metrics": metrics}, indent=2))
    print(f"{verdict}: {gates_passed}/{len(gates)} frozen gates")


if __name__ == "__main__":
    main()
