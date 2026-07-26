#!/usr/bin/env python3
"""Independent raw-data validator for frozen Q21.

This validator does not import either Q21 analysis script. It re-parses the
source members, reconstructs all registered coordinates, refits every model,
reruns the 1,998 label permutations and compares with the saved result.
"""

from __future__ import annotations

import hashlib
import json
import pathlib

import numpy as np


ROOT = pathlib.Path(__file__).parent
DEV = ROOT / "public_data" / "q20_willow_105q" / "d5_at_q4_7"
FRESH = ROOT / "public_data" / "q21_willow_105q" / "d5_at_q6_5"
TARGETS = (
    ROOT
    / "public_data"
    / "q21_willow_105q_outcomes"
    / "d5_at_q6_5"
)
PREFREEZE_MANIFEST = (
    ROOT / "public_data" / "q21_willow_105q" / "SOURCE_MANIFEST.json"
)
PROTOCOL = (
    ROOT / "Q21_WILLOW_RECURSIVE_CHILD_TOPOLOGY_PROTOCOL_v1_FROZEN.md"
)
CALIBRATION = ROOT / "Q21_WILLOW_CHILD_TOPOLOGY_CALIBRATION.json"
EXPECTED = ROOT / "Q21_WILLOW_RECURSIVE_CHILD_TOPOLOGY_RESULTS.json"
OUTPUT = ROOT / "Q21_WILLOW_RECURSIVE_CHILD_TOPOLOGY_VALIDATION.json"
PROTOCOL_HASH = (
    "bd26fa2e70c1e4ddbb4e5d768b6099cb6caaea3c96ab1ce3cac545d6575cd24d"
)
CALIBRATION_HASH = (
    "dcc0e609011e7fb725918cd9222828b0375352d2589eb42a6e477d5d255ad7fd"
)
SEED = 20260726
PERMUTATIONS = 999
NAMES = (
    "child_topology",
    "grandchildren_only",
    "parent_xy",
    "q20_global_xt",
    "count_only",
    "topology_plus_count",
    "spatial_shuffle_topology",
)
METRIC_NAMES = (
    "prevalence",
    "accuracy",
    "balanced_accuracy",
    "auroc",
    "average_precision",
    "error_rate",
)


def digest(path: pathlib.Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1 << 20):
            value.update(chunk)
    return value.hexdigest()


def coordinates(path: pathlib.Path) -> np.ndarray:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line[:9] == "DETECTOR(":
            body = line.partition("(")[2].partition(")")[0]
            rows.append(tuple(float(x) for x in body.split(",")[:3]))
    return np.array(rows, dtype=np.float64)


def axis(raw: np.ndarray, column: int) -> np.ndarray:
    value = raw[:, column]
    return 2.0 * (value - value.min()) / (value.max() - value.min()) - 1.0


def event_bits(
    path: pathlib.Path, shots: int, detector_count: int
) -> np.ndarray:
    width = (detector_count + 7) // 8
    raw = np.fromfile(path, dtype=np.uint8)
    if raw.size != shots * width:
        raise ValueError("Detector source length mismatch.")
    return np.unpackbits(
        raw.reshape(shots, width), axis=1, bitorder="little"
    )[:, :detector_count]


def target_bits(path: pathlib.Path, shots: int) -> np.ndarray:
    raw = np.fromfile(path, dtype=np.uint8)
    if raw.size != shots or np.any(raw > 1):
        raise ValueError("Target source is not one byte-aligned bit per shot.")
    return raw.astype(np.uint8)


def xy_weights(raw: np.ndarray) -> np.ndarray:
    x, y = axis(raw, 0), axis(raw, 1)
    xa, xb = (1 - x) / 2, (1 + x) / 2
    ya, yb = (1 - y) / 2, (1 + y) / 2
    return np.stack((xa * ya, xa * yb, xb * yb, xb * ya), axis=1)


def misassigned_weights(weight: np.ndarray, raw: np.ndarray) -> np.ndarray:
    output = weight.copy()
    for time in np.unique(raw[:, 2]):
        index = np.flatnonzero(raw[:, 2] == time)
        order = index[np.lexsort((raw[index, 1], raw[index, 0]))]
        amount = max(1, len(order) // 2 - 1)
        output[order] = weight[np.roll(order, amount)]
    return output


def ara_pack(
    events: np.ndarray, raw: np.ndarray, weight: np.ndarray
) -> dict[str, np.ndarray]:
    time = axis(raw, 2)
    phases = ((1 - time) / 2, (1 + time) / 2)
    unscaled = np.stack(
        [
            events @ (weight[:, child] * phase)
            for child in range(4)
            for phase in phases
        ],
        axis=1,
    ).astype(np.float64)
    total = unscaled.sum(axis=1, keepdims=True)
    empty = total[:, 0] == 0
    total[empty] = 1
    grand = 2 * unscaled / total
    grand[empty] = 0.25

    times = np.unique(raw[:, 2])
    shares = np.zeros((len(events), len(times), 4), np.float64)
    active = np.zeros((len(events), len(times)), bool)
    for position, time_value in enumerate(times):
        index = np.flatnonzero(raw[:, 2] == time_value)
        value = events[:, index] @ weight[index]
        value_total = value.sum(axis=1)
        good = value_total > 0
        shares[good, position] = value[good] / value_total[good, None]
        active[:, position] = good

    transition = np.zeros((len(events), 4, 4), np.float64)
    for position in range(len(times) - 1):
        good = active[:, position] & active[:, position + 1]
        transition[good] += (
            shares[good, position, :, None]
            * shares[good, position + 1, None, :]
        )
    transition_total = transition.sum(axis=(1, 2), keepdims=True)
    empty_transition = transition_total[:, 0, 0] == 0
    transition_total[empty_transition] = 1
    transition = 2 * transition / transition_total
    transition[empty_transition] = 0.125
    transition = transition.reshape(len(events), 16)

    child = grand.reshape(-1, 4, 2).sum(axis=2)
    x_parent = child[:, 2] + child[:, 3]
    y_parent = child[:, 1] + child[:, 2]
    j_xy = child[:, 1] + child[:, 3]
    t_parent = grand[:, 1::2].sum(axis=1)
    j_xt = grand[:, 1] + grand[:, 3] + grand[:, 4] + grand[:, 6]
    return {
        "grand": grand,
        "topology": np.concatenate((grand, transition), axis=1),
        "parent_xy": np.stack((x_parent, y_parent, j_xy), axis=1),
        "q20_global_xt": np.stack((x_parent, t_parent, j_xt), axis=1),
    }


def load(basis: str, split: str) -> tuple[dict[str, np.ndarray], np.ndarray, dict]:
    if split == "development":
        folder = DEV / basis / "r13"
        target = folder / "obs_flips_actual.b8"
    else:
        folder = FRESH / basis / "r30"
        target = TARGETS / basis / "r30" / "obs_flips_actual.b8"
    meta = json.loads((folder / "metadata.json").read_text(encoding="utf-8"))
    shots = int(meta["shots"])
    raw = coordinates(folder / "circuit_ideal.stim")
    events = event_bits(folder / "detection_events.b8", shots, len(raw))
    labels = target_bits(target, shots)
    weight = xy_weights(raw)
    ordinary = ara_pack(events, raw, weight)
    shuffled = ara_pack(events, raw, misassigned_weights(weight, raw))
    fill = events.sum(axis=1).astype(np.float64) / len(raw)
    features = {
        "child_topology": ordinary["topology"],
        "grandchildren_only": ordinary["grand"],
        "parent_xy": ordinary["parent_xy"],
        "q20_global_xt": ordinary["q20_global_xt"],
        "count_only": fill[:, None],
        "topology_plus_count": np.concatenate(
            (ordinary["topology"], fill[:, None]), axis=1
        ),
        "spatial_shuffle_topology": shuffled["topology"],
    }
    quality = {
        "shots": shots,
        "detectors": len(raw),
        "grand_sum_error": float(
            np.max(np.abs(ordinary["grand"].sum(axis=1) - 2))
        ),
        "topology_handover_sum_error": float(
            np.max(
                np.abs(ordinary["topology"][:, 8:].sum(axis=1) - 2)
            )
        ),
    }
    return features, labels, quality


def rank(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    sorted_value = values[order]
    result = np.empty(len(values), np.float64)
    left = 0
    while left < len(values):
        right = left + 1
        while right < len(values) and sorted_value[right] == sorted_value[left]:
            right += 1
        result[order[left:right]] = (left + 1 + right) / 2
        left = right
    return result


def roc_auc(y: np.ndarray, score: np.ndarray) -> float:
    positive = y == 1
    n1 = int(positive.sum())
    n0 = len(y) - n1
    ranks = rank(score)
    return float(
        (ranks[positive].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)
    )


def avg_precision(y: np.ndarray, score: np.ndarray) -> float:
    order = np.argsort(-score, kind="mergesort")
    ordered = y[order]
    cumulative = np.cumsum(ordered)
    precision = cumulative / np.arange(1, len(y) + 1)
    return float(precision[ordered == 1].sum() / ordered.sum())


def fit(
    value: np.ndarray, y: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    mean = value.mean(axis=0)
    sd = value.std(axis=0)
    z = (value - mean) / sd
    zero = z[y == 0].mean(axis=0)
    one = z[y == 1].mean(axis=0)
    return mean, sd, zero, one, one - zero


def score(
    value: np.ndarray,
    model: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray],
) -> np.ndarray:
    mean, sd, zero, one, direction = model
    return ((value - mean) / sd - (zero + one) / 2) @ direction


def measures(y: np.ndarray, value: np.ndarray) -> dict[str, float]:
    predicted = value > 0
    positive = y == 1
    accuracy = float((predicted == positive).mean())
    return {
        "prevalence": float(y.mean()),
        "accuracy": accuracy,
        "balanced_accuracy": float(
            (
                predicted[positive].mean()
                + (~predicted[~positive]).mean()
            )
            / 2
        ),
        "auroc": roc_auc(y, value),
        "average_precision": avg_precision(y, value),
        "error_rate": 1 - accuracy,
    }


def main() -> None:
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    checks = []

    def check(name: str, passed: bool, detail: str = "") -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    check("protocol_sha256", digest(PROTOCOL) == PROTOCOL_HASH)
    check("calibration_sha256", digest(CALIBRATION) == CALIBRATION_HASH)
    manifest = json.loads(PREFREEZE_MANIFEST.read_text(encoding="utf-8"))
    check(
        "prefreeze_manifest_has_no_outcome",
        len(manifest["members"]) == 6
        and not any(
            "obs_flips" in item["name"] for item in manifest["members"]
        ),
    )

    rng = np.random.default_rng(SEED)
    reproduced = {}
    qualities = {}
    for basis in ("X", "Z"):
        dev_x, dev_y, dev_quality = load(basis, "development")
        test_x, test_y, test_quality = load(basis, "holdout")
        qualities[basis] = {
            "development": dev_quality,
            "holdout": test_quality,
        }
        reproduced[basis] = {}
        for name in NAMES:
            model = fit(dev_x[name], dev_y)
            reproduced[basis][name] = measures(
                test_y, score(test_x[name], model)
            )
            for metric in METRIC_NAMES:
                actual = reproduced[basis][name][metric]
                saved = expected["bases"][basis]["models"][name][
                    "holdout_metrics"
                ][metric]
                check(
                    f"{basis}_{name}_{metric}",
                    abs(actual - saved) <= 1e-12,
                    f"{actual:.16g} vs {saved:.16g}",
                )

        model = fit(dev_x["child_topology"], dev_y)
        holdout_z = (
            test_x["child_topology"] - model[0]
        ) / model[1]
        null_auc = np.empty(PERMUTATIONS, np.float64)
        development_z = (
            dev_x["child_topology"] - model[0]
        ) / model[1]
        development_sum = development_z.sum(axis=0)
        for iteration in range(PERMUTATIONS):
            permuted = rng.permutation(dev_y)
            positive_count = int(permuted.sum())
            positive_sum = permuted.astype(np.float64) @ development_z
            one = positive_sum / positive_count
            zero = (
                development_sum - positive_sum
            ) / (len(permuted) - positive_count)
            null_auc[iteration] = roc_auc(
                test_y, holdout_z @ (one - zero)
            )
        observed = reproduced[basis]["child_topology"]["auroc"]
        p_value = float((1 + np.sum(null_auc >= observed)) / 1000)
        saved_p = expected["bases"][basis]["models"]["child_topology"][
            "permutation_control"
        ]["p_value_one_sided"]
        check(
            f"{basis}_permutation_p",
            p_value == saved_p,
            f"{p_value} vs {saved_p}",
        )
        reproduced[basis]["permutation_p"] = p_value

    for basis in ("X", "Z"):
        for split in ("development", "holdout"):
            item = qualities[basis][split]
            check(
                f"{basis}_{split}_construction",
                item["shots"] == 50000
                and item["detectors"]
                == (312 if split == "development" else 720)
                and item["grand_sum_error"] <= 1e-12
                and item["topology_handover_sum_error"] <= 1e-12,
            )

    mean_auc = {
        name: float(
            np.mean([reproduced[basis][name]["auroc"] for basis in ("X", "Z")])
        )
        for name in NAMES
    }
    gates = {
        "construction_and_source_integrity": all(
            item["passed"]
            for item in checks
            if item["check"].endswith("_construction")
        )
        and checks[0]["passed"]
        and checks[1]["passed"]
        and checks[2]["passed"],
        "child_topology_auroc_at_least_0_55_both_bases": all(
            reproduced[b]["child_topology"]["auroc"] >= 0.55
            for b in ("X", "Z")
        ),
        "mean_child_minus_parent_xy_at_least_0_01": (
            mean_auc["child_topology"] - mean_auc["parent_xy"] >= 0.01
        ),
        "mean_child_minus_q20_global_xt_at_least_0_01": (
            mean_auc["child_topology"] - mean_auc["q20_global_xt"] >= 0.01
        ),
        "permutation_p_at_most_0_01_both_bases": all(
            reproduced[b]["permutation_p"] <= 0.01 for b in ("X", "Z")
        ),
        "mean_topology_plus_count_minus_count_at_least_0_01": (
            mean_auc["topology_plus_count"] - mean_auc["count_only"] >= 0.01
        ),
        "mean_child_minus_spatial_shuffle_at_least_0_01": (
            mean_auc["child_topology"]
            - mean_auc["spatial_shuffle_topology"]
            >= 0.01
        ),
        "combined_not_over_0_01_worse_than_count_either_basis": all(
            reproduced[b]["topology_plus_count"]["auroc"]
            >= reproduced[b]["count_only"]["auroc"] - 0.01
            for b in ("X", "Z")
        ),
    }
    check("gates_exact", gates == expected["gates"])
    verdict = "SUPPORTED" if all(gates.values()) else "NOT SUPPORTED"
    check("verdict_exact", verdict == expected["verdict"])

    validation = {
        "claim": "Q21-WILLOW-RECURSIVE-CHILD-TOPOLOGY-v1",
        "created": "2026-07-26",
        "independent_raw_reparse": True,
        "imports_primary_runner": False,
        "permutations_recomputed": 2 * PERMUTATIONS,
        "checks": checks,
        "reproduced_holdout": reproduced,
        "reproduced_mean_auroc": mean_auc,
        "reproduced_gates": gates,
        "reproduced_verdict": verdict,
        "passed": all(item["passed"] for item in checks),
    }
    OUTPUT.write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "passed": validation["passed"],
                "check_count": len(checks),
                "failed": [
                    item for item in checks if not item["passed"]
                ],
                "verdict": verdict,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
