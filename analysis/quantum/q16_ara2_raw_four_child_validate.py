#!/usr/bin/env python3
"""Independent validation for Q16 raw ARA×2 four-child geometry."""

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
CONTROLS_CSV = HERE / "Q16_ARA2_RAW_FOUR_CHILD_CONTROLS.csv"
RESULTS_JSON = HERE / "Q16_ARA2_RAW_FOUR_CHILD_RESULTS.json"
VALIDATION_JSON = HERE / "Q16_ARA2_RAW_FOUR_CHILD_VALIDATION.json"

STATE_ORDER = ("C00", "C01", "C10", "C11")
BITS = {"C00": (0, 0), "C01": (0, 1), "C10": (1, 0), "C11": (1, 1)}
OFFSET = 32766.0
SCALE = 3.0519e-5
SEGMENTS = 5
REPEATS = 40
SHUFFLES = 9999
CONTROLS = 1000
SEED = 2026072516

CONFIGS = {
    "C00": {
        "archive": "UPDOWN-DOWNUP.zip", "root": "UPDOWN-DOWNUP",
        "md5": "1724b4484ffb88e41dbac5f50981e91a",
        "measurements": 60, "buckets": 10, "timestamp0": "190250",
    },
    "C01": {
        "archive": "UPDOWN+DOWNUP.zip", "root": "UPDOWN+DOWNUP",
        "md5": "43f782ed4404b01393fb57a2da5d1534",
        "measurements": 60, "buckets": 10, "timestamp0": "171731",
    },
    "C10": {
        "archive": "UPUP-DOWNDOWN.zip", "root": "UPUP-DOWNDOWN",
        "md5": "8cd8a5f2b3b9a2ccd090e47312bcc390",
        "measurements": 40, "buckets": 2, "timestamp0": "115025",
    },
    "C11": {
        "archive": "UPUP+DOWNDOWN.zip", "root": "UPUP+DOWNDOWN",
        "md5": "3275210b912d51e5f10ba99d93ad6ca5",
        "measurements": 60, "buckets": 5, "timestamp0": "183730",
    },
}


def digest(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_records() -> tuple[list[dict[str, str]], dict[tuple[str, str, int, str], dict[str, str]]]:
    with RECORDS_CSV.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    lookup = {
        (row["child"], row["split"], int(row["record_index"]), row["cut"]): row
        for row in rows
    }
    return rows, lookup


def arrays(rows: list[dict[str, str]]) -> dict[str, dict[str, np.ndarray]]:
    result = {
        state: {
            split: np.empty((40, 45), dtype=np.float64)
            for split in ("development", "holdout")
        }
        for state in STATE_ORDER
    }
    for row in rows:
        state = row["child"]
        split = row["split"]
        record = int(row["record_index"])
        setting = int(row["setting"][1:])
        segment = int(row["segment"][1:])
        result[state][split][record, setting * 5 + segment] = float(row["ara_x"])
    return result


def centroids(vectors: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    return {state: vectors[state].mean(axis=0) for state in STATE_ORDER}


def contrast(c: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    a, b, d, e = (c[state] for state in STATE_ORDER)
    return {
        "M": (a + b + d + e) / 4,
        "U": (a + b - d - e) / 2,
        "V": (a - b + d - e) / 2,
        "J": (a - b - d + e) / 2,
    }


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.dot(a, b) / denominator) if denominator else 0.0


def decode(
    hold: dict[str, np.ndarray], dev_c: dict[str, np.ndarray]
) -> dict[str, float]:
    rows = np.vstack([hold[state] for state in STATE_ORDER])
    true_u = np.concatenate(
        [np.full(len(hold[state]), BITS[state][0]) for state in STATE_ORDER]
    )
    true_v = np.concatenate(
        [np.full(len(hold[state]), BITS[state][1]) for state in STATE_ORDER]
    )
    centered = rows - dev_c["M"]
    pred_u = (centered @ dev_c["U"] < 0).astype(int)
    pred_v = (centered @ dev_c["V"] < 0).astype(int)
    return {
        "u": float(np.mean(pred_u == true_u)),
        "v": float(np.mean(pred_v == true_v)),
        "four": float(np.mean((2 * pred_u + pred_v) == (2 * true_u + true_v))),
    }


def raw_spot_checks(
    lookup: dict[tuple[str, str, int, str], dict[str, str]]
) -> list[dict[str, object]]:
    checks = []
    for state in STATE_ORDER:
        config = CONFIGS[state]
        member = (
            f"{config['root']}/raw/{config['timestamp0']}_Bell_states_1_1.bin"
        )
        with zipfile.ZipFile(DATA_DIR / config["archive"]) as archive:
            raw = np.frombuffer(archive.read(member), dtype="<u2")
        length = raw.size // (SEGMENTS * REPEATS)
        shaped = raw.reshape(SEGMENTS, REPEATS, length)
        for segment in range(SEGMENTS):
            row = lookup[(state, "development", 0, f"K0G{segment}")]
            ridge = float(row["ridge_current"])
            values = SCALE * (shaped[segment].astype(np.float64) - OFFSET)
            values = values.ravel()
            above = int(np.sum(values > ridge))
            below = int(np.sum(values < ridge))
            x = 2 * above / (above + below)
            observed = float(row["ara_x"])
            checks.append(
                {
                    "child": state,
                    "cut": f"K0G{segment}",
                    "expected_x": observed,
                    "redecoded_x": x,
                    "absolute_error": abs(x - observed),
                    "pass": abs(x - observed) <= 1e-12,
                }
            )
    return checks


def main() -> None:
    results = json.loads(RESULTS_JSON.read_text(encoding="utf-8"))
    expected_sha = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    observed_sha = digest(PROTOCOL, "sha256")
    rows, lookup = load_records()
    data = arrays(rows)
    dev = {state: data[state]["development"] for state in STATE_ORDER}
    hold = {state: data[state]["holdout"] for state in STATE_ORDER}
    dev_c = contrast(centroids(dev))
    hold_c = contrast(centroids(hold))
    metrics = decode(hold, dev_c)

    recomputed = {
        "U_cos": abs(cosine(dev_c["U"], hold_c["U"])),
        "V_cos": abs(cosine(dev_c["V"], hold_c["V"])),
        "J_cos": abs(cosine(dev_c["J"], hold_c["J"])),
        "U_energy": float(np.dot(dev_c["U"], dev_c["U"])),
        "V_energy": float(np.dot(dev_c["V"], dev_c["V"])),
        "J_energy": float(np.dot(dev_c["J"], dev_c["J"])),
        "bit_U": metrics["u"],
        "bit_V": metrics["v"],
        "four_child": metrics["four"],
    }
    total_energy = (
        recomputed["U_energy"] + recomputed["V_energy"] + recomputed["J_energy"]
    )
    recomputed["J_share"] = recomputed["J_energy"] / total_energy

    expected = {
        "U_cos": results["parent_geometry"]["U_holdout_cosine_abs"],
        "V_cos": results["parent_geometry"]["V_holdout_cosine_abs"],
        "J_cos": results["parent_geometry"]["J_holdout_cosine_abs"],
        "U_energy": results["parent_geometry"]["U_energy"],
        "V_energy": results["parent_geometry"]["V_energy"],
        "J_energy": results["parent_geometry"]["J_energy"],
        "J_share": results["parent_geometry"]["J_energy_share"],
        "bit_U": results["decoding"]["bit_u_balanced_accuracy"],
        "bit_V": results["decoding"]["bit_v_balanced_accuracy"],
        "four_child": results["decoding"]["four_child_balanced_accuracy"],
    }
    metric_checks = {
        key: {
            "expected": expected[key],
            "recomputed": recomputed[key],
            "absolute_error": abs(expected[key] - recomputed[key]),
            "pass": abs(expected[key] - recomputed[key]) <= 1e-12,
        }
        for key in expected
    }

    rng = np.random.default_rng(SEED)
    dev_all = np.vstack([dev[state] for state in STATE_ORDER])
    labels = np.repeat(np.arange(4), 40)
    null_accuracy = np.empty(SHUFFLES)
    null_j = np.empty(SHUFFLES)
    for index in range(SHUFFLES):
        shuffled = rng.permutation(labels)
        shuffled_dev = {
            state: dev_all[shuffled == state_index]
            for state_index, state in enumerate(STATE_ORDER)
        }
        shuffled_c = contrast(centroids(shuffled_dev))
        null_accuracy[index] = decode(hold, shuffled_c)["four"]
        null_j[index] = float(np.dot(shuffled_c["J"], shuffled_c["J"]))
    independent_null = {
        "four_child_p": float(
            (1 + np.sum(null_accuracy >= recomputed["four_child"]))
            / (SHUFFLES + 1)
        ),
        "four_child_99": float(np.quantile(null_accuracy, 0.99)),
        "J_p": float(
            (1 + np.sum(null_j >= recomputed["J_energy"])) / (SHUFFLES + 1)
        ),
        "J_99": float(np.quantile(null_j, 0.99)),
    }

    combined = {state: np.vstack([dev[state], hold[state]]) for state in STATE_ORDER}
    pseudo_passes = 0
    for _ in range(CONTROLS):
        state = STATE_ORDER[int(rng.integers(0, 4))]
        order = np.arange(80)
        if rng.integers(0, 2):
            order = order[::-1]
        order = np.roll(order, -int(rng.integers(0, 80)))
        arranged = combined[state][order]
        pseudo_dev = {}
        pseudo_hold = {}
        for child_index, child in enumerate(STATE_ORDER):
            block = arranged[20 * child_index:20 * (child_index + 1)]
            pseudo_dev[child] = block[:10]
            pseudo_hold[child] = block[10:]
        pdev = contrast(centroids(pseudo_dev))
        phold = contrast(centroids(pseudo_hold))
        u_cos = abs(cosine(pdev["U"], phold["U"]))
        v_cos = abs(cosine(pdev["V"], phold["V"]))
        u_sign = float(np.mean(np.sign(pdev["U"]) == np.sign(phold["U"])))
        v_sign = float(np.mean(np.sign(pdev["V"]) == np.sign(phold["V"])))
        dm = decode(pseudo_hold, pdev)
        passed = (
            u_cos >= 0.80 and v_cos >= 0.80
            and u_sign >= 0.75 and v_sign >= 0.75
            and dm["u"] >= 0.80 and dm["v"] >= 0.80
            and dm["four"] >= max(0.70, independent_null["four_child_99"])
        )
        pseudo_passes += int(passed)
    independent_control_rate = pseudo_passes / CONTROLS

    source_hashes = {
        state: digest(DATA_DIR / config["archive"], "md5")
        for state, config in CONFIGS.items()
    }
    spot_checks = raw_spot_checks(lookup)
    failures = []
    if observed_sha != expected_sha:
        failures.append("protocol hash")
    if len(rows) != 14400:
        failures.append("record row count")
    if any(not check["pass"] for check in metric_checks.values()):
        failures.append("metric recomputation")
    if any(source_hashes[state] != CONFIGS[state]["md5"] for state in STATE_ORDER):
        failures.append("source hash")
    if any(not check["pass"] for check in spot_checks):
        failures.append("raw spot decode")
    if independent_null["four_child_p"] > 0.01:
        failures.append("independent label-shuffle control")
    if independent_null["J_p"] > 0.01:
        failures.append("independent relation null")
    if independent_control_rate > 0.05:
        failures.append("independent pseudo-child control")

    validation = {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "protocol_sha256": {
            "expected": expected_sha,
            "observed": observed_sha,
            "pass": expected_sha == observed_sha,
        },
        "source_md5": source_hashes,
        "records_rows": len(rows),
        "metric_checks": metric_checks,
        "raw_spot_checks": spot_checks,
        "independent_null": independent_null,
        "independent_pseudo_child": {
            "passes": pseudo_passes,
            "total": CONTROLS,
            "false_positive_rate": independent_control_rate,
        },
        "methodology_caveat": (
            "The four-state Walsh transform always exists algebraically. Validation "
            "supports raw separability, held-out stability, and a stable relation "
            "contrast; it does not make the transform itself independent evidence."
        ),
    }
    VALIDATION_JSON.write_text(
        json.dumps(validation, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": validation["status"],
                "failures": failures,
                "four_child_p": independent_null["four_child_p"],
                "J_p": independent_null["J_p"],
                "pseudo_false_positive_rate": independent_control_rate,
                "raw_spot_checks_passed": sum(
                    int(check["pass"]) for check in spot_checks
                ),
                "raw_spot_checks_total": len(spot_checks),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
