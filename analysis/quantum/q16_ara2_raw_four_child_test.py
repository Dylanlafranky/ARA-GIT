#!/usr/bin/env python3
"""Run Q16: ARA-native two-parent/four-child geometry on raw current records.

Source
------
Figshare 10.6084/m9.figshare.14160476.v2 (CC BY 4.0).

The ARA stage deliberately does not reconstruct Pauli expectations, Bell labels,
density matrices, Ramsey/Hahn curves, or CHSH values. Archive names are used only
to locate bytes; immutable file-ID order supplies C00/C01/C10/C11.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import zipfile
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "public_data" / "q4_bell_tomography"
PROTOCOL = HERE / "Q16_ARA2_RAW_FOUR_CHILD_PROTOCOL_v2_FROZEN.md"
PROTOCOL_SHA = HERE / "Q16_ARA2_RAW_FOUR_CHILD_PROTOCOL_v2_FROZEN.sha256"
RECORDS_CSV = HERE / "Q16_ARA2_RAW_FOUR_CHILD_RECORDS.csv"
CUTS_CSV = HERE / "Q16_ARA2_RAW_FOUR_CHILD_CUTS.csv"
CONTRASTS_CSV = HERE / "Q16_ARA2_RAW_FOUR_CHILD_CONTRASTS.csv"
CONTROLS_CSV = HERE / "Q16_ARA2_RAW_FOUR_CHILD_CONTROLS.csv"
RESULTS_JSON = HERE / "Q16_ARA2_RAW_FOUR_CHILD_RESULTS.json"
QUALITY_JSON = HERE / "Q16_ARA2_RAW_FOUR_CHILD_DATA_QUALITY.json"

SEED = 20260725
BOOTSTRAPS = 2000
SHUFFLES = 9999
PSEUDO_CONTROLS = 1000
OFFSET = 32766.0
SCALE = 3.0519e-5
SEGMENTS = 5
REPEATS_PER_SEGMENT = 40
DEV_RECORDS = 40
HOLD_RECORDS = 40
SETTINGS = 9


CONFIGS = {
    "C00": {
        "archive": "UPDOWN-DOWNUP.zip",
        "root": "UPDOWN-DOWNUP",
        "file_id": 26690657,
        "size": 307629500,
        "md5": "1724b4484ffb88e41dbac5f50981e91a",
        "measurements": 60,
        "buckets": 10,
        "timestamps": (
            "190250", "191433", "192618", "193759", "194951",
            "200149", "201324", "202517", "203722",
        ),
    },
    "C01": {
        "archive": "UPDOWN+DOWNUP.zip",
        "root": "UPDOWN+DOWNUP",
        "file_id": 26690660,
        "size": 305874138,
        "md5": "43f782ed4404b01393fb57a2da5d1534",
        "measurements": 60,
        "buckets": 10,
        "timestamps": (
            "171731", "172913", "174052", "175222", "180412",
            "181547", "182710", "183831", "184958",
        ),
    },
    "C10": {
        "archive": "UPUP-DOWNDOWN.zip",
        "root": "UPUP-DOWNDOWN",
        "file_id": 26690663,
        "size": 41182988,
        "md5": "8cd8a5f2b3b9a2ccd090e47312bcc390",
        "measurements": 40,
        "buckets": 2,
        "timestamps": (
            "115025", "115222", "115424", "115627", "115835",
            "120033", "120230", "120428", "120626",
        ),
    },
    "C11": {
        "archive": "UPUP+DOWNDOWN.zip",
        "root": "UPUP+DOWNDOWN",
        "file_id": 26690666,
        "size": 151973378,
        "md5": "3275210b912d51e5f10ba99d93ad6ca5",
        "measurements": 60,
        "buckets": 5,
        "timestamps": (
            "183730", "185433", "190045", "190657", "191311",
            "191932", "192544", "193149", "193748",
        ),
    },
}

STATE_ORDER = ("C00", "C01", "C10", "C11")
BITS = {
    "C00": (0, 0),
    "C01": (0, 1),
    "C10": (1, 0),
    "C11": (1, 1),
}


def digest(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_inputs() -> tuple[dict[str, str], str]:
    observed = {}
    for state, config in CONFIGS.items():
        path = DATA_DIR / str(config["archive"])
        if not path.exists():
            raise RuntimeError(f"Missing source archive: {path}")
        if path.stat().st_size != int(config["size"]):
            raise RuntimeError(f"{state}: source size mismatch")
        md5 = digest(path, "md5")
        if md5 != config["md5"]:
            raise RuntimeError(
                f"{state}: MD5 mismatch; expected {config['md5']}, got {md5}"
            )
        observed[state] = md5
    expected_sha = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    observed_sha = digest(PROTOCOL, "sha256")
    if observed_sha != expected_sha:
        raise RuntimeError(
            f"Protocol SHA mismatch; expected {expected_sha}, got {observed_sha}"
        )
    return observed, observed_sha


def member_name(
    config: dict[str, object], timestamp: str, measurement: int, bucket: int
) -> str:
    return (
        f"{config['root']}/raw/"
        f"{timestamp}_Bell_states_{measurement}_{bucket}.bin"
    )


def record_pairs(config: dict[str, object]) -> list[tuple[int, int]]:
    return [
        (bucket, measurement)
        for bucket in range(1, int(config["buckets"]) + 1)
        for measurement in range(1, int(config["measurements"]) + 1)
    ]


def decode_member(raw_bytes: bytes) -> np.ndarray:
    raw = np.frombuffer(raw_bytes, dtype="<u2")
    denominator = SEGMENTS * REPEATS_PER_SEGMENT
    if raw.size % denominator:
        raise RuntimeError(f"Unexpected raw member length: {raw.size}")
    readout_length = raw.size // denominator
    return raw.reshape(SEGMENTS, REPEATS_PER_SEGMENT, readout_length)


def currents(raw_segment: np.ndarray) -> np.ndarray:
    return SCALE * (raw_segment.astype(np.float64) - OFFSET)


def cosine(left: np.ndarray, right: np.ndarray) -> float:
    denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
    if denominator == 0:
        return 0.0
    return float(np.dot(left, right) / denominator)


def state_centroids(
    vectors: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    return {state: vectors[state].mean(axis=0) for state in STATE_ORDER}


def contrasts(
    centroids: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    c00, c01, c10, c11 = (centroids[state] for state in STATE_ORDER)
    return {
        "M": (c00 + c01 + c10 + c11) / 4.0,
        "U": (c00 + c01 - c10 - c11) / 2.0,
        "V": (c00 - c01 + c10 - c11) / 2.0,
        "J": (c00 - c01 - c10 + c11) / 2.0,
    }


def sign_retention(dev: np.ndarray, hold: np.ndarray) -> tuple[float, int]:
    informative = np.abs(dev) > 1e-12
    count = int(informative.sum())
    if count == 0:
        return 0.0, 0
    retained = np.sign(dev[informative]) == np.sign(hold[informative])
    return float(retained.mean()), count


def decode_with_parent_axes(
    rows: np.ndarray,
    dev_contrasts: dict[str, np.ndarray],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    centered = rows - dev_contrasts["M"]
    score_u = centered @ dev_contrasts["U"]
    score_v = centered @ dev_contrasts["V"]
    bit_u = (score_u < 0).astype(np.int8)
    bit_v = (score_v < 0).astype(np.int8)
    child = 2 * bit_u + bit_v
    return bit_u, bit_v, child


def decode_metrics(
    vectors: dict[str, np.ndarray],
    dev_contrasts: dict[str, np.ndarray],
) -> dict[str, float]:
    rows = np.vstack([vectors[state] for state in STATE_ORDER])
    true_u = np.concatenate(
        [np.full(len(vectors[state]), BITS[state][0]) for state in STATE_ORDER]
    )
    true_v = np.concatenate(
        [np.full(len(vectors[state]), BITS[state][1]) for state in STATE_ORDER]
    )
    true_child = 2 * true_u + true_v
    pred_u, pred_v, pred_child = decode_with_parent_axes(rows, dev_contrasts)
    return {
        "bit_u_balanced_accuracy": float(np.mean(pred_u == true_u)),
        "bit_v_balanced_accuracy": float(np.mean(pred_v == true_v)),
        "four_child_balanced_accuracy": float(
            np.mean(pred_child == true_child)
        ),
    }


def nearest_centroid_accuracy(
    hold_vectors: dict[str, np.ndarray],
    dev_centroids: dict[str, np.ndarray],
) -> float:
    correct = 0
    total = 0
    centroid_matrix = np.vstack([dev_centroids[state] for state in STATE_ORDER])
    for state_index, state in enumerate(STATE_ORDER):
        distances = np.linalg.norm(
            hold_vectors[state][:, None, :] - centroid_matrix[None, :, :],
            axis=2,
        )
        correct += int(np.sum(np.argmin(distances, axis=1) == state_index))
        total += len(hold_vectors[state])
    return correct / total


def geometry_metrics(
    centroids: dict[str, np.ndarray],
) -> dict[str, object]:
    points = np.vstack([centroids[state] for state in STATE_ORDER])
    pairwise = {}
    distances = []
    for left_index in range(4):
        for right_index in range(left_index + 1, 4):
            label = f"{STATE_ORDER[left_index]}__{STATE_ORDER[right_index]}"
            value = float(np.linalg.norm(points[left_index] - points[right_index]))
            pairwise[label] = value
            distances.append(value)
    scale = float(np.mean(distances)) if distances else 1.0
    pairings = {
        "C00+C11_vs_C01+C10": (0, 3, 1, 2),
        "C00+C10_vs_C01+C11": (0, 2, 1, 3),
        "C00+C01_vs_C10+C11": (0, 1, 2, 3),
    }
    closure = {}
    for label, (a, b, c, d) in pairings.items():
        raw = float(np.linalg.norm(points[a] + points[b] - points[c] - points[d]))
        closure[label] = {
            "raw": raw,
            "normalized_by_mean_pair_distance": raw / scale if scale else 0.0,
        }
    edge_matrix = np.vstack(
        [points[1] - points[0], points[2] - points[0], points[3] - points[0]]
    )
    gram = edge_matrix @ edge_matrix.T
    determinant = max(float(np.linalg.det(gram)), 0.0)
    volume = math.sqrt(determinant) / 6.0
    return {
        "pairwise_distances": pairwise,
        "mean_pairwise_distance": scale,
        "parallelogram_residuals": closure,
        "tetrahedral_volume": volume,
        "normalized_tetrahedral_volume": (
            volume / (scale**3) if scale > 0 else 0.0
        ),
        "centered_rank": int(
            np.linalg.matrix_rank(points - points.mean(axis=0), tol=1e-10)
        ),
    }


def control_pass(
    dev_vectors: dict[str, np.ndarray],
    hold_vectors: dict[str, np.ndarray],
    four_threshold: float,
) -> tuple[bool, dict[str, float]]:
    dev_c = contrasts(state_centroids(dev_vectors))
    hold_c = contrasts(state_centroids(hold_vectors))
    u_cos = abs(cosine(dev_c["U"], hold_c["U"]))
    v_cos = abs(cosine(dev_c["V"], hold_c["V"]))
    u_sign, _ = sign_retention(dev_c["U"], hold_c["U"])
    v_sign, _ = sign_retention(dev_c["V"], hold_c["V"])
    decoded = decode_metrics(hold_vectors, dev_c)
    passed = (
        u_cos >= 0.80
        and v_cos >= 0.80
        and u_sign >= 0.75
        and v_sign >= 0.75
        and decoded["bit_u_balanced_accuracy"] >= 0.80
        and decoded["bit_v_balanced_accuracy"] >= 0.80
        and decoded["four_child_balanced_accuracy"] >= four_threshold
    )
    return passed, {
        "u_cosine": u_cos,
        "v_cosine": v_cos,
        "u_sign_retention": u_sign,
        "v_sign_retention": v_sign,
        **decoded,
    }


def main() -> None:
    archive_hashes, protocol_sha = verify_inputs()
    rng = np.random.default_rng(SEED)
    dimensions = SETTINGS * SEGMENTS
    vectors = {
        state: {
            "development": np.empty((DEV_RECORDS, dimensions), dtype=np.float64),
            "holdout": np.empty((HOLD_RECORDS, dimensions), dtype=np.float64),
        }
        for state in STATE_ORDER
    }
    record_rows: list[dict[str, object]] = []
    cut_ridges: dict[str, float] = {}
    readout_lengths: dict[str, list[int]] = {state: [] for state in STATE_ORDER}
    selected_member_counts = {state: 0 for state in STATE_ORDER}
    member_counts = {}

    archives = {
        state: zipfile.ZipFile(DATA_DIR / str(CONFIGS[state]["archive"]))
        for state in STATE_ORDER
    }
    try:
        for state in STATE_ORDER:
            config = CONFIGS[state]
            names = set(archives[state].namelist())
            pairs = record_pairs(config)
            member_counts[state] = len(
                [name for name in names if name.startswith(f"{config['root']}/raw/")]
            )
            required = {
                member_name(config, timestamp, measurement, bucket)
                for timestamp in config["timestamps"]
                for bucket, measurement in pairs
            }
            missing = required - names
            if missing:
                raise RuntimeError(f"{state}: {len(missing)} required members missing")

        for setting_index in range(SETTINGS):
            cache: dict[str, dict[str, list[np.ndarray]]] = {}
            for state in STATE_ORDER:
                config = CONFIGS[state]
                pairs = record_pairs(config)
                dev_pairs = pairs[:DEV_RECORDS]
                hold_pairs = pairs[-HOLD_RECORDS:]
                if set(dev_pairs) & set(hold_pairs):
                    raise RuntimeError(f"{state}: development/holdout overlap")
                timestamp = config["timestamps"][setting_index]
                cache[state] = {"development": [], "holdout": []}
                for split, selected_pairs in (
                    ("development", dev_pairs),
                    ("holdout", hold_pairs),
                ):
                    for bucket, measurement in selected_pairs:
                        name = member_name(
                            config, timestamp, measurement, bucket
                        )
                        decoded = decode_member(archives[state].read(name))
                        cache[state][split].append(decoded)
                        readout_lengths[state].append(int(decoded.shape[-1]))
                        selected_member_counts[state] += 1

            for segment_index in range(SEGMENTS):
                cut_index = setting_index * SEGMENTS + segment_index
                cut_name = f"K{setting_index}G{segment_index}"
                per_record_medians = []
                for state in STATE_ORDER:
                    for raw_member in cache[state]["development"]:
                        values = currents(raw_member[segment_index]).ravel()
                        per_record_medians.append(float(np.median(values)))
                ridge = float(np.median(per_record_medians))
                cut_ridges[cut_name] = ridge

                for state in STATE_ORDER:
                    for split, expected_count in (
                        ("development", DEV_RECORDS),
                        ("holdout", HOLD_RECORDS),
                    ):
                        members = cache[state][split]
                        if len(members) != expected_count:
                            raise RuntimeError("Unexpected selected record count")
                        for record_index, raw_member in enumerate(members):
                            values = currents(
                                raw_member[segment_index]
                            ).ravel()
                            above = int(np.sum(values > ridge))
                            below = int(np.sum(values < ridge))
                            ties = int(values.size - above - below)
                            denominator = above + below
                            x = (
                                2.0 * above / denominator
                                if denominator
                                else 1.0
                            )
                            vectors[state][split][record_index, cut_index] = x
                            q1, median, q3 = np.quantile(
                                values, [0.25, 0.5, 0.75]
                            )
                            mad = float(
                                np.median(np.abs(values - median))
                            )
                            activity = float(np.mean(np.abs(values - ridge)))
                            record_rows.append(
                                {
                                    "child": state,
                                    "split": split,
                                    "record_index": record_index,
                                    "setting": f"K{setting_index}",
                                    "segment": f"G{segment_index}",
                                    "cut": cut_name,
                                    "ara_x": x,
                                    "ridge_current": ridge,
                                    "samples": int(values.size),
                                    "above": above,
                                    "below": below,
                                    "ties": ties,
                                    "current_q1": float(q1),
                                    "current_median": float(median),
                                    "current_q3": float(q3),
                                    "current_mad": mad,
                                    "current_min": float(np.min(values)),
                                    "current_max": float(np.max(values)),
                                    "mean_abs_from_ridge": activity,
                                }
                            )
            print(f"decoded raw setting K{setting_index}")
    finally:
        for archive in archives.values():
            archive.close()

    dev_vectors = {state: vectors[state]["development"] for state in STATE_ORDER}
    hold_vectors = {state: vectors[state]["holdout"] for state in STATE_ORDER}
    dev_centroids = state_centroids(dev_vectors)
    hold_centroids = state_centroids(hold_vectors)
    dev_c = contrasts(dev_centroids)
    hold_c = contrasts(hold_centroids)

    u_cos = abs(cosine(dev_c["U"], hold_c["U"]))
    v_cos = abs(cosine(dev_c["V"], hold_c["V"]))
    j_cos = abs(cosine(dev_c["J"], hold_c["J"]))
    u_sign, u_informative = sign_retention(dev_c["U"], hold_c["U"])
    v_sign, v_informative = sign_retention(dev_c["V"], hold_c["V"])
    j_sign, j_informative = sign_retention(dev_c["J"], hold_c["J"])
    decoded = decode_metrics(hold_vectors, dev_c)
    nearest_accuracy = nearest_centroid_accuracy(hold_vectors, dev_centroids)

    # Held-out bootstrap of the frozen decoder.
    bootstrap_rows = []
    for _ in range(BOOTSTRAPS):
        sampled = {
            state: hold_vectors[state][
                rng.integers(0, HOLD_RECORDS, size=HOLD_RECORDS)
            ]
            for state in STATE_ORDER
        }
        bootstrap_rows.append(decode_metrics(sampled, dev_c))
    bootstrap_summary = {
        key: {
            "mean": float(np.mean([row[key] for row in bootstrap_rows])),
            "ci_low": float(np.quantile([row[key] for row in bootstrap_rows], 0.025)),
            "ci_high": float(np.quantile([row[key] for row in bootstrap_rows], 0.975)),
        }
        for key in bootstrap_rows[0]
    }

    # Label-shuffle null: shuffle only development child labels.
    dev_all = np.vstack([dev_vectors[state] for state in STATE_ORDER])
    dev_labels = np.repeat(np.arange(4), DEV_RECORDS)
    null_child_accuracy = np.empty(SHUFFLES, dtype=np.float64)
    null_j_energy = np.empty(SHUFFLES, dtype=np.float64)
    for repetition in range(SHUFFLES):
        shuffled = rng.permutation(dev_labels)
        shuffled_vectors = {
            state: dev_all[shuffled == state_index]
            for state_index, state in enumerate(STATE_ORDER)
        }
        shuffled_c = contrasts(state_centroids(shuffled_vectors))
        null_child_accuracy[repetition] = decode_metrics(
            hold_vectors, shuffled_c
        )["four_child_balanced_accuracy"]
        null_j_energy[repetition] = float(np.dot(shuffled_c["J"], shuffled_c["J"]))

    null_child_99 = float(np.quantile(null_child_accuracy, 0.99))
    observed_child_p = float(
        (1 + np.sum(null_child_accuracy >= decoded["four_child_balanced_accuracy"]))
        / (SHUFFLES + 1)
    )
    energy_u = float(np.dot(dev_c["U"], dev_c["U"]))
    energy_v = float(np.dot(dev_c["V"], dev_c["V"]))
    energy_j = float(np.dot(dev_c["J"], dev_c["J"]))
    energy_total = energy_u + energy_v + energy_j
    relation_share = energy_j / energy_total if energy_total else 0.0
    relation_null_99 = float(np.quantile(null_j_energy, 0.99))
    relation_p = float(
        (1 + np.sum(null_j_energy >= energy_j)) / (SHUFFLES + 1)
    )

    four_threshold = max(0.70, null_child_99)
    control_rows = []
    pseudo_passes = 0
    combined = {
        state: np.vstack(
            [vectors[state]["development"], vectors[state]["holdout"]]
        )
        for state in STATE_ORDER
    }
    for repetition in range(PSEUDO_CONTROLS):
        source_index = int(rng.integers(0, 4))
        source_state = STATE_ORDER[source_index]
        start = int(rng.integers(0, 80))
        reverse = bool(rng.integers(0, 2))
        order = np.arange(80)
        if reverse:
            order = order[::-1]
        order = np.roll(order, -start)
        arranged = combined[source_state][order]
        pseudo_dev = {}
        pseudo_hold = {}
        for child_index, child in enumerate(STATE_ORDER):
            block = arranged[child_index * 20:(child_index + 1) * 20]
            pseudo_dev[child] = block[:10]
            pseudo_hold[child] = block[10:]
        passed, metrics = control_pass(
            pseudo_dev, pseudo_hold, four_threshold
        )
        pseudo_passes += int(passed)
        control_rows.append(
            {
                "repetition": repetition,
                "source_child": source_state,
                "start": start,
                "reverse": int(reverse),
                "passed_all": int(passed),
                **metrics,
            }
        )
    pseudo_false_positive_rate = pseudo_passes / PSEUDO_CONTROLS

    stateful_relation = (
        j_cos >= 0.80
        and relation_share >= 0.05
        and energy_j > relation_null_99
    )
    gates = {
        "G1_parent_U_holdout_cosine": {
            "value": u_cos, "threshold": 0.80, "pass": u_cos >= 0.80
        },
        "G2_parent_V_holdout_cosine": {
            "value": v_cos, "threshold": 0.80, "pass": v_cos >= 0.80
        },
        "G3_parent_U_cut_sign_retention": {
            "value": u_sign, "threshold": 0.75, "pass": u_sign >= 0.75,
            "informative_cuts": u_informative,
        },
        "G4_parent_V_cut_sign_retention": {
            "value": v_sign, "threshold": 0.75, "pass": v_sign >= 0.75,
            "informative_cuts": v_informative,
        },
        "G5_parent_U_bit_accuracy": {
            "value": decoded["bit_u_balanced_accuracy"],
            "threshold": 0.80,
            "pass": decoded["bit_u_balanced_accuracy"] >= 0.80,
        },
        "G6_parent_V_bit_accuracy": {
            "value": decoded["bit_v_balanced_accuracy"],
            "threshold": 0.80,
            "pass": decoded["bit_v_balanced_accuracy"] >= 0.80,
        },
        "G7_four_child_accuracy": {
            "value": decoded["four_child_balanced_accuracy"],
            "threshold": four_threshold,
            "registered_floor": 0.70,
            "shuffle_99": null_child_99,
            "shuffle_p": observed_child_p,
            "pass": (
                decoded["four_child_balanced_accuracy"] >= four_threshold
                and observed_child_p <= 0.01
            ),
        },
        "G8_pseudo_child_false_positive_rate": {
            "value": pseudo_false_positive_rate,
            "threshold": 0.05,
            "passes": pseudo_passes,
            "total": PSEUDO_CONTROLS,
            "pass": pseudo_false_positive_rate <= 0.05,
        },
    }
    gates_passed = sum(int(gate["pass"]) for gate in gates.values())
    verdict = "SUPPORTED" if gates_passed == len(gates) else "NOT SUPPORTED"
    relation_class = (
        "STATEFUL RETAINED RELATION"
        if stateful_relation
        else "PLANAR/TWO-PARENT CLOSURE"
        if all(gates[name]["pass"] for name in ("G1_parent_U_holdout_cosine", "G2_parent_V_holdout_cosine"))
        else "UNRESOLVED GEOMETRY"
    )

    cut_rows = []
    for split, split_vectors in (
        ("development", dev_vectors),
        ("holdout", hold_vectors),
    ):
        for state in STATE_ORDER:
            for cut_index in range(dimensions):
                setting_index, segment_index = divmod(cut_index, SEGMENTS)
                values = split_vectors[state][:, cut_index]
                cut_rows.append(
                    {
                        "split": split,
                        "child": state,
                        "cut": f"K{setting_index}G{segment_index}",
                        "setting": f"K{setting_index}",
                        "segment": f"G{segment_index}",
                        "ridge_current": cut_ridges[
                            f"K{setting_index}G{segment_index}"
                        ],
                        "ara_mean": float(np.mean(values)),
                        "ara_std": float(np.std(values, ddof=1)),
                        "ara_q05": float(np.quantile(values, 0.05)),
                        "ara_median": float(np.median(values)),
                        "ara_q95": float(np.quantile(values, 0.95)),
                        "n_records": len(values),
                    }
                )

    contrast_rows = []
    for cut_index in range(dimensions):
        setting_index, segment_index = divmod(cut_index, SEGMENTS)
        row = {
            "cut": f"K{setting_index}G{segment_index}",
            "setting": f"K{setting_index}",
            "segment": f"G{segment_index}",
        }
        for name in ("M", "U", "V", "J"):
            row[f"{name}_development"] = float(dev_c[name][cut_index])
            row[f"{name}_holdout"] = float(hold_c[name][cut_index])
        contrast_rows.append(row)

    for path, rows in (
        (RECORDS_CSV, record_rows),
        (CUTS_CSV, cut_rows),
        (CONTRASTS_CSV, contrast_rows),
        (CONTROLS_CSV, control_rows),
    ):
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    data_quality = {
        "source_archive_md5s": archive_hashes,
        "source_member_counts": member_counts,
        "selected_member_reads": selected_member_counts,
        "readout_length_by_child": {
            state: {
                "min": min(readout_lengths[state]),
                "max": max(readout_lengths[state]),
                "distinct": sorted(set(readout_lengths[state])),
            }
            for state in STATE_ORDER
        },
        "records_csv_rows": len(record_rows),
        "cuts": dimensions,
        "development_records_per_child": DEV_RECORDS,
        "holdout_records_per_child": HOLD_RECORDS,
        "segment_zero_retained": True,
        "conventional_projection_labels_used": False,
        "density_matrix_used": False,
        "ramsey_hahn_used": False,
    }
    QUALITY_JSON.write_text(
        json.dumps(data_quality, indent=2) + "\n", encoding="utf-8"
    )

    diagnostic_energy_by_setting = {}
    for setting_index in range(SETTINGS):
        selection = slice(
            setting_index * SEGMENTS,
            (setting_index + 1) * SEGMENTS,
        )
        diagnostic_energy_by_setting[f"K{setting_index}"] = {
            name: float(np.sum(dev_c[name][selection] ** 2))
            for name in ("U", "V", "J")
        }

    diagnostic_energy_by_segment = {}
    for segment_index in range(SEGMENTS):
        selection = np.arange(segment_index, dimensions, SEGMENTS)
        diagnostic_energy_by_segment[f"G{segment_index}"] = {
            name: float(np.sum(dev_c[name][selection] ** 2))
            for name in ("U", "V", "J")
        }

    results = {
        "protocol_id": "Q16-ARA2-RAW-v2",
        "ledger_id": "T275",
        "verdict": verdict,
        "gates_passed": gates_passed,
        "gates_total": len(gates),
        "protocol_sha256": protocol_sha,
        "ara_stage": {
            "children": list(STATE_ORDER),
            "dimensions": dimensions,
            "coordinate": "2*n(current>development_ridge)/n(non-tie)",
            "development_ridge": "median of equally weighted per-record medians",
            "segments_retained": [f"G{i}" for i in range(SEGMENTS)],
            "settings_retained": [f"K{i}" for i in range(SETTINGS)],
        },
        "parent_geometry": {
            "U_holdout_cosine_abs": u_cos,
            "V_holdout_cosine_abs": v_cos,
            "J_holdout_cosine_abs": j_cos,
            "U_cut_sign_retention": u_sign,
            "V_cut_sign_retention": v_sign,
            "J_cut_sign_retention": j_sign,
            "U_informative_cuts": u_informative,
            "V_informative_cuts": v_informative,
            "J_informative_cuts": j_informative,
            "U_energy": energy_u,
            "V_energy": energy_v,
            "J_energy": energy_j,
            "J_energy_share": relation_share,
            "J_shuffle_99": relation_null_99,
            "J_shuffle_p": relation_p,
            "relation_class": relation_class,
        },
        "decoding": {
            **decoded,
            "nearest_four_centroid_accuracy": nearest_accuracy,
            "label_shuffle_99": null_child_99,
            "label_shuffle_p": observed_child_p,
            "bootstrap": bootstrap_summary,
        },
        "negative_control": {
            "pseudo_child_passes": pseudo_passes,
            "pseudo_child_total": PSEUDO_CONTROLS,
            "false_positive_rate": pseudo_false_positive_rate,
        },
        "development_geometry": geometry_metrics(dev_centroids),
        "holdout_geometry": geometry_metrics(hold_centroids),
        "post_result_diagnostics": {
            "energy_by_unnamed_setting": diagnostic_energy_by_setting,
            "energy_by_raw_segment": diagnostic_energy_by_segment,
            "boundary": (
                "Descriptive only; not used in frozen gates. Conventional "
                "setting names may be restored only after this result is saved."
            ),
        },
        "gates": gates,
        "data_quality_path": QUALITY_JSON.name,
        "artifacts": [
            RECORDS_CSV.name,
            CUTS_CSV.name,
            CONTRASTS_CSV.name,
            CONTROLS_CSV.name,
        ],
        "evidence_boundary": (
            "Corrected ARA-native reanalysis of four already-open archives from "
            "one device/deposit. Requires unchanged independent-source replication."
        ),
    }
    RESULTS_JSON.write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "verdict": verdict,
                "gates": f"{gates_passed}/{len(gates)}",
                "U_cos": u_cos,
                "V_cos": v_cos,
                "J_cos": j_cos,
                "bit_U": decoded["bit_u_balanced_accuracy"],
                "bit_V": decoded["bit_v_balanced_accuracy"],
                "four_child": decoded["four_child_balanced_accuracy"],
                "four_child_shuffle_p": observed_child_p,
                "relation": relation_class,
                "J_share": relation_share,
                "pseudo_false_positive_rate": pseudo_false_positive_rate,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
