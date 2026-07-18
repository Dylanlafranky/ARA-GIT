"""Build compact, post-test aggregate data for the PN3 geometry explorer."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
PACKET = HERE / "PN3_STANDALONE_ARA_TARGET_PACKET.npz"
DEV = HERE / "PN3_STANDALONE_ARA_DEVELOPMENT_SUMMARY.json"
RESULTS = HERE / "PN3_STANDALONE_ARA_RESULTS.json"
SCORES = HERE / "PN3_STANDALONE_ARA_MODEL_SCORES.csv"
BLOCKS = HERE / "PN3_STANDALONE_ARA_BLOCK_CALIBRATION.csv"
GAPS = HERE / "PN3_STANDALONE_ARA_GAP_CLASSES.csv"
SIEVE_PRIMES = np.array([2, 3, 5, 7, 11, 13, 17, 19, 23, 29], dtype=float)
W29 = float(np.prod(1.0 - 1.0 / SIEVE_PRIMES))
HL_MULTIPLIER = 39.784544672686
BINS = 12


def finite(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): finite(item) for key, item in value.items()}
    if isinstance(value, list):
        return [finite(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return float(value) if math.isfinite(float(value)) else None
    return value


def ara_bin(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    coordinate = 2.0 * right.astype(float) / (left.astype(float) + right.astype(float))
    return np.minimum((coordinate * BINS / 2.0).astype(np.int16), BINS - 1)


def aggregate_plane(
    xbin: np.ndarray,
    ybin: np.ndarray,
    labels: np.ndarray,
    parent: np.ndarray,
    ara: np.ndarray,
    raw: np.ndarray,
    established: np.ndarray,
) -> list[dict[str, Any]]:
    index = ybin.astype(np.int64) * BINS + xbin.astype(np.int64)
    count = np.bincount(index, minlength=BINS * BINS).astype(float)

    def mean(values: np.ndarray) -> np.ndarray:
        total = np.bincount(index, weights=values.astype(float), minlength=BINS * BINS)
        return np.divide(total, count, out=np.full_like(total, np.nan), where=count > 0)

    actual_mean = mean(labels)
    parent_mean = mean(parent)
    ara_mean = mean(ara)
    raw_mean = mean(raw)
    established_mean = mean(established)
    cells: list[dict[str, Any]] = []
    for y in range(BINS):
        for x in range(BINS):
            position = y * BINS + x
            cells.append(
                {
                    "x": x,
                    "y": y,
                    "x0": 2.0 * x / BINS,
                    "x1": 2.0 * (x + 1) / BINS,
                    "y0": 2.0 * y / BINS,
                    "y1": 2.0 * (y + 1) / BINS,
                    "count": int(count[position]),
                    "actual": actual_mean[position],
                    "parent": parent_mean[position],
                    "ara": ara_mean[position],
                    "raw": raw_mean[position],
                    "established": established_mean[position],
                    "observed_from_parent": actual_mean[position] - parent_mean[position],
                    "ara_from_parent": ara_mean[position] - parent_mean[position],
                    "remaining_after_ara": actual_mean[position] - ara_mean[position],
                    "remaining_after_established": actual_mean[position] - established_mean[position],
                    "raw_from_parent": raw_mean[position] - parent_mean[position],
                }
            )
    return finite(cells)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    development = json.loads(DEV.read_text(encoding="utf-8"))
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    scores = pd.read_csv(SCORES)
    blocks = pd.read_csv(BLOCKS)
    gap_classes = pd.read_csv(GAPS)
    archive = np.load(PACKET, allow_pickle=False)

    parent = {
        "candidate": {
            "actual": [
                development["rung_rates"][name]["candidate_rate"] for name in ("r6", "r7", "r8")
            ] + [results["candidate_actual_rate"]],
            "predictions": results["parent_recovery"]["candidate"],
            "established": float(
                scores[(scores.task == "candidate") & (scores.model == "pnt29_reference")]["mean_prediction"].iloc[0]
            ),
        },
        "edge": {
            "actual": [development["rung_rates"][name]["edge_rate"] for name in ("r6", "r7", "r8")]
            + [results["edge_actual_rate"]],
            "predictions": results["parent_recovery"]["edge"],
            "established": float(
                scores[(scores.task == "edge") & (scores.model == "hl29_reference")]["mean_prediction"].iloc[0]
            ),
        },
    }

    block_rows: dict[str, list[dict[str, Any]]] = {"candidate": [], "edge": []}
    for row in blocks.to_dict(orient="records"):
        task = row["task"]
        if task == "candidate":
            prepared = {
                "block": int(row["block"]),
                "low": int(row["low"]),
                "high": int(row["high"]),
                "events": int(row["events"]),
                "actual": row["actual_rate"],
                "parent": row["mean__ara_parent_only"],
                "ara": row["mean__ara_parent_ara_i3_child"],
                "raw": row["mean__ara_parent_raw_stencil_child"],
                "established": row["mean__pnt29_reference"],
                "loss_parent": row["loss__ara_parent_only"],
                "loss_ara": row["loss__ara_parent_ara_i3_child"],
                "loss_raw": row["loss__ara_parent_raw_stencil_child"],
                "loss_established": row["loss__pnt29_reference"],
            }
        else:
            prepared = {
                "block": int(row["block"]),
                "low": int(row["low"]),
                "high": int(row["high"]),
                "events": int(row["events"]),
                "actual": row["actual_rate"],
                "parent": row["mean__ara_parent_only"],
                "ara": row["mean__ara_parent_ara_endpoints_child"],
                "raw": row["mean__ara_parent_raw_edge_child"],
                "established": row["mean__hl29_reference"],
                "loss_parent": row["loss__ara_parent_only"],
                "loss_ara": row["loss__ara_parent_ara_endpoints_child"],
                "loss_raw": row["loss__ara_parent_raw_edge_child"],
                "loss_established": row["loss__hl29_reference"],
            }
        block_rows[task].append(finite(prepared))

    gap_rows = []
    for row in gap_classes.to_dict(orient="records"):
        gap_rows.append(
            finite(
                {
                    "gap": int(row["gap"]),
                    "events": int(row["events"]),
                    "positives": int(row["positives"]),
                    "actual": row["actual_rate"],
                    "parent": row["mean__ara_parent_only"],
                    "ara": row["mean__ara_parent_ara_endpoints_child"],
                    "raw": row["mean__ara_parent_raw_edge_child"],
                    "established": row["mean__hl29_reference"],
                }
            )
        )

    numbers = archive["candidate_numbers"].astype(np.int64)
    labels = archive["candidate_labels"].astype(float)
    gm2 = archive["candidate_gm2"].astype(np.int16)
    gm1 = archive["candidate_gm1"].astype(np.int16)
    g0 = archive["candidate_g0"].astype(np.int16)
    gp1 = archive["candidate_gp1"].astype(np.int16)
    bprev = ara_bin(gm2, gm1)
    bcurrent = ara_bin(gm1, g0)
    bnext = ara_bin(g0, gp1)

    candidate_parent = archive["candidate_prediction__ara_parent_only"].astype(float)
    candidate_ara = archive["candidate_prediction__ara_parent_ara_i3_child"].astype(float)
    candidate_raw = archive["candidate_prediction__ara_parent_raw_stencil_child"].astype(float)
    candidate_established = 1.0 / (np.log(numbers.astype(float)) * W29)

    edge_count = len(archive["edge_labels"])
    edge_numbers = archive["edge_numbers"].astype(np.int64)
    edge_gaps = archive["edge_gaps"].astype(np.int64)
    edge_labels = archive["edge_labels"].astype(float)
    edge_parent = archive["edge_prediction__ara_parent_only"].astype(float)
    edge_ara = archive["edge_prediction__ara_parent_ara_endpoints_child"].astype(float)
    edge_raw = archive["edge_prediction__ara_parent_raw_edge_child"].astype(float)
    edge_established = HL_MULTIPLIER / (
        np.log(edge_numbers.astype(float)) * np.log((edge_numbers + edge_gaps).astype(float))
    )

    planes = {
        "candidate": {
            "prev_current": aggregate_plane(
                bprev,
                bcurrent,
                labels,
                candidate_parent,
                candidate_ara,
                candidate_raw,
                candidate_established,
            ),
            "current_next": aggregate_plane(
                bcurrent,
                bnext,
                labels,
                candidate_parent,
                candidate_ara,
                candidate_raw,
                candidate_established,
            ),
        },
        "edge": {
            "current_next": aggregate_plane(
                bcurrent[:edge_count],
                bnext[:edge_count],
                edge_labels,
                edge_parent,
                edge_ara,
                edge_raw,
                edge_established,
            )
        },
    }

    selected_scores = scores[
        scores.model.isin(
            [
                "ara_parent_only",
                "ara_parent_ara_i3_child",
                "ara_parent_raw_stencil_child",
                "pnt29_reference",
                "ara_parent_ara_endpoints_child",
                "ara_parent_raw_edge_child",
                "hl29_reference",
            ]
        )
    ][
        [
            "task",
            "model",
            "actual_rate",
            "mean_prediction",
            "log_loss_bits",
            "gain_vs_established_reference_bits",
        ]
    ].to_dict(orient="records")

    payload = {
        "meta": {
            "test_id": results["test_id"],
            "target": results["target_interval"],
            "candidate_events": results["candidate_events"],
            "edge_events": results["edge_events"],
            "bins": BINS,
            "packet_sha256": results["packet_sha256_before"],
        },
        "parent": finite(parent),
        "blocks": finite(block_rows),
        "gaps": finite(gap_rows),
        "planes": finite(planes),
        "scores": finite(selected_scores),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "bytes": args.output.stat().st_size}, indent=2))


if __name__ == "__main__":
    main()
