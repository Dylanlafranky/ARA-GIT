"""Q44A prospective sparse-group repair, frozen before evaluation C4 access."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import defaultdict


HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / "public_data" / "_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))

import numpy as np

import q44_ara_mixing_prediction_test as q44


TEST_ID = "Q44A-SPARSE-GROUP-ARA-MIXING-v1"
PROTOCOL = HERE / "Q44A_SPARSE_GROUP_FALLBACK_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA256 = "2dc63a86865f52fad62e8edf3a130c8d02ac92b2064c4dd3578b7c35dde200a6"
PREDICTIONS = q44.DATA / "q44a_frozen_predictions.npz"
RESULTS = HERE / "Q44A_SPARSE_GROUP_ARA_MIXING_RESULTS.json"
EVENTS = HERE / "Q44A_SPARSE_GROUP_ARA_MIXING_CYCLES.csv.gz"
MIN_GROUP_CYCLES = 25


def verify() -> None:
    q44.verify_frozen_files()
    actual = q44.digest(PROTOCOL, "sha256")
    if actual != PROTOCOL_SHA256:
        raise RuntimeError(
            f"Q44A frozen protocol changed; expected {PROTOCOL_SHA256}, got {actual}"
        )


def fit_mixing(records: list[dict], grouping):
    normal = defaultdict(lambda: np.zeros((2, 2), dtype=np.float64))
    rhs = defaultdict(lambda: np.zeros(2, dtype=np.float64))
    counts = defaultdict(int)
    for row in records:
        key = grouping(row)
        d, o, y = row["diameter"], row["other"], row["target_step"]
        normal[key][0, 0] += np.sum(d * d)
        normal[key][0, 1] += np.sum(d * o)
        normal[key][1, 0] += np.sum(d * o)
        normal[key][1, 1] += np.sum(o * o)
        rhs[key][0] += np.sum(d * y)
        rhs[key][1] += np.sum(o * y)
        counts[key] += 1
    coefficients = {
        key: np.linalg.pinv(value, rcond=1e-12) @ rhs[key]
        for key, value in normal.items()
    }
    return coefficients, dict(counts)


def fit_affine(records: list[dict], grouping):
    normal = defaultdict(lambda: np.zeros((3, 3), dtype=np.float64))
    rhs = defaultdict(lambda: np.zeros(3, dtype=np.float64))
    counts = defaultdict(int)
    for row in records:
        key = grouping(row)
        states = (row["c1"], row["c2"], row["c3"])
        for left in range(3):
            for right in range(3):
                normal[key][left, right] += np.sum(
                    states[left] * states[right]
                )
            rhs[key][left] += np.sum(states[left] * row["c4"])
        counts[key] += 1
    coefficients = {
        key: np.linalg.pinv(value, rcond=1e-12) @ rhs[key]
        for key, value in normal.items()
    }
    return coefficients, dict(counts)


def coefficient_json(values: dict) -> str:
    return json.dumps(
        {
            repr(key): [float(item) for item in value]
            for key, value in sorted(values.items(), key=lambda item: repr(item[0]))
        },
        sort_keys=True,
    )


def prepare() -> str:
    verify()
    closure = np.asarray(np.load(q44.DERIVED)["closure"], dtype=np.float32)
    connected = np.load(q44.CONNECTED, mmap_mode="r")
    development, coordinate_cache = q44.gather_development(closure, connected)

    by_family, family_counts = fit_mixing(
        development,
        lambda row: q44.group_key(row["family"], row["q4"]),
    )
    by_quadrant, quadrant_counts = fit_mixing(
        development,
        lambda row: (int(row["q4"]),),
    )
    pooled_affine, pooled_counts = fit_affine(
        development,
        lambda _row: ("pooled",),
    )
    family_affine, family_affine_counts = fit_affine(
        development,
        lambda row: q44.group_key(row["family"], row["q4"]),
    )
    quadrant_affine, quadrant_affine_counts = fit_affine(
        development,
        lambda row: (int(row["q4"]),),
    )

    metadata: dict[str, list] = defaultdict(list)
    visible_blocks: list[np.ndarray] = []
    prediction_blocks: list[np.ndarray] = []
    selected_coefficients: dict[tuple[str, int], np.ndarray] = {}
    selected_affine: dict[tuple[str, int], np.ndarray] = {}
    selected_counts: dict[tuple[str, int], int] = {}
    selected_affine_counts: dict[tuple[str, int], int] = {}
    evaluation_counts = defaultdict(int)
    fallback_groups: dict[tuple[str, int], dict] = {}

    for (seed, pair), (coordinate, family, fit) in coordinate_cache.items():
        u, v, labels, direction, coherence, occupancy = coordinate
        scale = float(
            np.median(
                np.linalg.norm(connected[seed, :250, pair], axis=(1, 2))
            )
        )
        for window in q44.base.complete_windows(labels, direction, 250, 498):
            q4 = int(window[3][0])
            family_key = q44.group_key(family, q4)
            quadrant_key = (q4,)
            if family_counts.get(family_key, 0) >= MIN_GROUP_CYCLES:
                mixing = by_family[family_key]
                affine = family_affine[family_key]
                selected_count = family_counts[family_key]
                selected_affine_count = family_affine_counts[family_key]
                level = "family_quadrant"
            else:
                if quadrant_counts.get(quadrant_key, 0) < MIN_GROUP_CYCLES:
                    raise RuntimeError(
                        f"Quadrant fallback remains sparse: {quadrant_key}"
                    )
                mixing = by_quadrant[quadrant_key]
                affine = quadrant_affine[quadrant_key]
                selected_count = quadrant_counts[quadrant_key]
                selected_affine_count = quadrant_affine_counts[quadrant_key]
                level = "quadrant_fallback"
                fallback_groups[family_key] = {
                    "family_development_cycles": family_counts.get(family_key, 0),
                    "quadrant_development_cycles": selected_count,
                }
            selected_coefficients[family_key] = mixing
            selected_affine[family_key] = affine
            selected_counts[family_key] = selected_count
            selected_affine_counts[family_key] = selected_affine_count
            evaluation_counts[family_key] += 1

            c1, c2, c3 = q44.base.identities_for_window(
                connected,
                seed,
                pair,
                window,
                count=3,
            )
            visible_blocks.append(np.stack((c1, c2, c3)))
            prediction_blocks.append(
                q44.predictor_stack(
                    c1,
                    c2,
                    c3,
                    mixing,
                    pooled_affine[("pooled",)],
                    affine,
                )
            )
            metadata["seed"].append(seed)
            metadata["pair"].append(pair)
            metadata["family"].append(family)
            metadata["model_level"].append(level)
            metadata["q4"].append(q4)
            metadata["direction"].append(direction)
            metadata["coherence"].append(coherence)
            metadata["occupancy"].append(occupancy)
            metadata["lineage_scale"].append(scale)
            metadata["angular_period"].append(
                float(fit["angular_period_samples"])
            )
            for index, (quadrant, start, end) in enumerate(window, start=1):
                metadata[f"q{index}"].append(quadrant)
                metadata[f"q{index}_start"].append(start)
                metadata[f"q{index}_end"].append(end)

    payload = {key: np.asarray(value) for key, value in metadata.items()}
    payload.update(
        {
            "c_visible": np.asarray(visible_blocks, dtype=np.float32),
            "predictions": np.asarray(prediction_blocks, dtype=np.float32),
            "methods": np.asarray(q44.METHODS),
            "mixing_coefficients_json": np.asarray(
                coefficient_json(selected_coefficients)
            ),
            "mixing_development_counts_json": np.asarray(
                json.dumps(
                    {repr(k): int(v) for k, v in selected_counts.items()},
                    sort_keys=True,
                )
            ),
            "affine_pooled_json": np.asarray(
                coefficient_json(pooled_affine)
            ),
            "affine_grouped_json": np.asarray(
                coefficient_json(selected_affine)
            ),
            "affine_pooled_counts_json": np.asarray(
                json.dumps(
                    {repr(k): int(v) for k, v in pooled_counts.items()},
                    sort_keys=True,
                )
            ),
            "affine_grouped_counts_json": np.asarray(
                json.dumps(
                    {
                        repr(k): int(v)
                        for k, v in selected_affine_counts.items()
                    },
                    sort_keys=True,
                )
            ),
            "evaluation_group_counts_json": np.asarray(
                json.dumps(
                    {repr(k): int(v) for k, v in evaluation_counts.items()},
                    sort_keys=True,
                )
            ),
            "fallback_groups_json": np.asarray(
                json.dumps(
                    {repr(k): value for k, value in fallback_groups.items()},
                    sort_keys=True,
                )
            ),
            "development_cycles": np.asarray(len(development)),
            "eligible_lineages": np.asarray(len(coordinate_cache)),
            "protocol_sha256": np.asarray(PROTOCOL_SHA256),
            "target_lock_sha256": np.asarray(q44.TARGET_LOCK_SHA256),
            "archive_md5": np.asarray(q44.ARCHIVE_MD5),
        }
    )
    np.savez_compressed(PREDICTIONS, **payload)
    prediction_hash = q44.digest(PREDICTIONS, "sha256")
    print(
        json.dumps(
            {
                "status": (
                    "Q44A PREDICTIONS SEALED — EVALUATION C4 NOT READ"
                ),
                "prediction_sha256": prediction_hash,
                "development_cycles": len(development),
                "eligible_lineages": len(coordinate_cache),
                "evaluation_cycles": len(prediction_blocks),
                "fallback_groups": {
                    repr(key): value
                    for key, value in sorted(fallback_groups.items(), key=lambda x: repr(x[0]))
                },
                "fallback_evaluation_cycles": int(
                    sum(
                        evaluation_counts[key]
                        for key in fallback_groups
                    )
                ),
            },
            indent=2,
        ),
        flush=True,
    )
    return prediction_hash


def configure_base() -> None:
    q44.TEST_ID = TEST_ID
    q44.PROTOCOL = PROTOCOL
    q44.PROTOCOL_SHA256 = PROTOCOL_SHA256
    q44.PREDICTIONS = PREDICTIONS
    q44.RESULTS = RESULTS
    q44.EVENTS = EVENTS


def score() -> None:
    configure_base()
    result = q44.score_and_report()
    frozen = np.load(PREDICTIONS, allow_pickle=False)
    result["prospective_status"] = "prospective after eligibility amendment"
    result["sparse_group_fallback"] = json.loads(
        str(frozen["fallback_groups_json"])
    )
    RESULTS.write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("prepare", "score"))
    args = parser.parse_args()
    if args.stage == "prepare":
        prepare()
    else:
        score()


if __name__ == "__main__":
    main()
