#!/usr/bin/env python3
"""Independent recomputation for Q20; does not import the primary runner."""

from __future__ import annotations

import hashlib
import json
import pathlib

import numpy as np


HERE = pathlib.Path(__file__).parent
DATA = HERE / "public_data" / "q20_willow_105q" / "d5_at_q4_7"
RESULTS = HERE / "Q20_WILLOW_ARA_RELATION_DECODER_RESULTS.json"
OUTPUT = HERE / "Q20_WILLOW_ARA_RELATION_DECODER_VALIDATION.json"
PROTOCOL = HERE / "Q20_WILLOW_ARA_RELATION_DECODER_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = "3a55824116968450d43f64770933059c4ce00b0a873a7302b417111986118d6f"
SEED = 20260726
REPETITIONS = 999


def digest(path: pathlib.Path) -> str:
    value = hashlib.sha256()
    value.update(path.read_bytes())
    return value.hexdigest()


def detector_coordinates(path: pathlib.Path) -> np.ndarray:
    values = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("DETECTOR("):
            text = line.split("(", 1)[1].split(")", 1)[0]
            values.append([float(x) for x in text.split(",")[:3]])
    return np.asarray(values, dtype=np.float32)


def read_split(basis: str, rounds_name: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    folder = DATA / basis / rounds_name
    meta = json.loads((folder / "metadata.json").read_text(encoding="utf-8"))
    shots = int(meta["shots"])
    coords = detector_coordinates(folder / "circuit_ideal.stim")
    detectors_n = coords.shape[0]
    packed = np.fromfile(folder / "detection_events.b8", dtype=np.uint8)
    packed = packed.reshape(shots, (detectors_n + 7) // 8)
    detectors = np.unpackbits(packed, axis=1, bitorder="little")[:, :detectors_n]
    labels_raw = np.fromfile(folder / "obs_flips_actual.b8", dtype=np.uint8)
    labels = (labels_raw & 1).astype(np.uint8)

    x = coords[:, 0]
    t = coords[:, 2]
    x = 2 * (x - x.min()) / (x.max() - x.min()) - 1
    t = 2 * (t - t.min()) / (t.max() - t.min()) - 1
    x_a, x_b = (1 - x) / 2, (1 + x) / 2
    t_a, t_b = (1 - t) / 2, (1 + t) / 2
    children = np.column_stack(
        (
            detectors @ (x_a * t_a),
            detectors @ (x_a * t_b),
            detectors @ (x_b * t_a),
            detectors @ (x_b * t_b),
        )
    ).astype(np.float64)
    total = children.sum(axis=1, keepdims=True)
    empty = total[:, 0] == 0
    total[empty] = 1
    children = children / total
    children[empty] = 0.25
    ara = np.column_stack(
        (
            2 * (children[:, 2] + children[:, 3]),
            2 * (children[:, 1] + children[:, 3]),
            2 * (children[:, 1] + children[:, 2]),
        )
    )
    fill = detectors.sum(axis=1).astype(float) / detectors_n
    return ara, fill, labels


def train(features: np.ndarray, labels: np.ndarray) -> tuple:
    mean = features.mean(axis=0)
    sd = features.std(axis=0)
    z = (features - mean) / sd
    zero = z[labels == 0].mean(axis=0)
    one = z[labels == 1].mean(axis=0)
    return mean, sd, zero, one, one - zero


def score(model: tuple, features: np.ndarray) -> np.ndarray:
    mean, sd, zero, one, direction = model
    return ((features - mean) / sd - (zero + one) / 2) @ direction


def ranks(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    sorted_values = values[order]
    starts = np.flatnonzero(
        np.concatenate(([True], sorted_values[1:] != sorted_values[:-1]))
    )
    ends = np.concatenate((starts[1:], [values.size]))
    out = np.empty(values.size, dtype=float)
    out[order] = np.repeat((starts + 1 + ends) / 2, ends - starts)
    return out


def auc(labels: np.ndarray, scores: np.ndarray) -> float:
    pos = labels == 1
    p = int(pos.sum())
    n = labels.size - p
    return float((ranks(scores)[pos].sum() - p * (p + 1) / 2) / (p * n))


def balanced_accuracy(labels: np.ndarray, scores: np.ndarray) -> float:
    predicted = scores > 0
    return float(
        (
            np.mean(predicted[labels == 1])
            + np.mean(~predicted[labels == 0])
        )
        / 2
    )


def main() -> None:
    saved = json.loads(RESULTS.read_text(encoding="utf-8"))
    checks = {
        "protocol_checksum": digest(PROTOCOL) == PROTOCOL_SHA,
        "saved_protocol_checksum": saved["protocol_sha256"] == PROTOCOL_SHA,
        "saved_verdict": saved["verdict"] == "NOT SUPPORTED",
    }
    rng = np.random.default_rng(SEED)
    recomputed = {}
    for basis in ("X", "Z"):
        dev_ara, dev_fill, dev_y = read_split(basis, "r13")
        hold_ara, hold_fill, hold_y = read_split(basis, "r30")
        feature_sets = {
            "ARA_relation": (dev_ara, hold_ara),
            "count_only": (dev_fill[:, None], hold_fill[:, None]),
            "ARA_plus_count": (
                np.column_stack((dev_ara, dev_fill)),
                np.column_stack((hold_ara, hold_fill)),
            ),
        }
        recomputed[basis] = {}
        for name, (dev_x, hold_x) in feature_sets.items():
            model = train(dev_x, dev_y)
            hold_score = score(model, hold_x)
            observed = {
                "auroc": auc(hold_y, hold_score),
                "balanced_accuracy": balanced_accuracy(hold_y, hold_score),
            }
            recomputed[basis][name] = observed
            expected = saved["bases"][basis]["models"][name]["holdout_metrics"]
            checks[f"{basis}_{name}_auroc"] = (
                abs(observed["auroc"] - expected["auroc"]) <= 1e-12
            )
            checks[f"{basis}_{name}_balanced_accuracy"] = (
                abs(
                    observed["balanced_accuracy"]
                    - expected["balanced_accuracy"]
                )
                <= 1e-12
            )

        null_auc = np.empty(REPETITIONS)
        for index in range(REPETITIONS):
            permuted = rng.permutation(dev_y)
            model = train(dev_ara, permuted)
            null_auc[index] = auc(hold_y, score(model, hold_ara))
        observed_auc = recomputed[basis]["ARA_relation"]["auroc"]
        p_value = float((1 + np.sum(null_auc >= observed_auc)) / 1000)
        expected_control = saved["bases"][basis]["models"]["ARA_relation"][
            "permutation_control"
        ]
        checks[f"{basis}_permutation_p"] = (
            abs(p_value - expected_control["p_value_one_sided"]) <= 1e-12
        )
        recomputed[basis]["permutation_p_value"] = p_value

    validation = {
        "claim": "Q20-WILLOW-ARA-RELATION-v1",
        "created": "2026-07-26",
        "independent_recomputation": True,
        "imports_primary_runner": False,
        "checks": checks,
        "recomputed": recomputed,
        "passed": bool(all(checks.values())),
    }
    OUTPUT.write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, indent=2, sort_keys=True))
    if not validation["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
