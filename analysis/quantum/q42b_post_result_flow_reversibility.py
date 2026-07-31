"""Post-result Q42 audit of forward/return flow-shape reversibility."""

from __future__ import annotations

import csv
import gzip
import json
import pathlib

import numpy as np


HERE = pathlib.Path(__file__).resolve().parent
STRANDS = HERE / "Q42_ARA_DUAL_STRAND_FLOW_STRANDS.csv.gz"
PROFILES = HERE / "Q42_ARA_DUAL_STRAND_FLOW_PROFILES.npz"
RESULTS = HERE / "Q42B_POST_RESULT_FLOW_REVERSIBILITY.json"
EPS = 1e-12


def summary(values) -> dict:
    values = np.asarray(values, dtype=np.float64)
    values = values[np.isfinite(values)]
    return {
        "count": int(len(values)),
        "mean": float(np.mean(values)),
        "p05": float(np.quantile(values, 0.05)),
        "p25": float(np.quantile(values, 0.25)),
        "median": float(np.median(values)),
        "p75": float(np.quantile(values, 0.75)),
        "p95": float(np.quantile(values, 0.95)),
    }


def row_correlation(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    first = first - np.mean(first, axis=1, keepdims=True)
    second = second - np.mean(second, axis=1, keepdims=True)
    return np.sum(first * second, axis=1) / (
        np.sqrt(
            np.sum(first * first, axis=1)
            * np.sum(second * second, axis=1)
        )
        + EPS
    )


def main() -> None:
    with gzip.open(STRANDS, "rt", newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    profiles = np.load(PROFILES)
    progress = np.asarray(profiles["progress"], dtype=np.float64)
    forward = np.asarray(profiles["forward"], dtype=np.float64)
    returning = np.asarray(profiles["returning"], dtype=np.float64)
    residual = np.asarray(profiles["residual"], dtype=np.float64)
    forward_flow = np.gradient(forward, progress, axis=1)
    return_flow = -np.gradient(returning, progress, axis=1)
    same = row_correlation(forward_flow, return_flow)
    mirrored = row_correlation(forward_flow, return_flow[:, ::-1])

    median_forward_flow = np.median(forward_flow, axis=0)
    median_return_flow = np.median(return_flow, axis=0)
    aggregate_mirror_correlation = float(
        np.corrcoef(median_forward_flow, median_return_flow[::-1])[0, 1]
    )
    median_residual = np.median(residual, axis=0)
    peak_index = int(np.argmax(median_residual))

    output = {
        "status": "POST-RESULT FLOW-SHAPE AUDIT",
        "pairs": len(rows),
        "aggregate_median_flow_mirror_correlation": aggregate_mirror_correlation,
        "pairwise_same_progress_flow_correlation": summary(same),
        "pairwise_time_reversed_flow_correlation": summary(mirrored),
        "median_residual_peak": {
            "progress": float(progress[peak_index]),
            "forward_coordinate": float(np.median(forward[:, peak_index])),
            "return_coordinate": float(np.median(returning[:, peak_index])),
            "forward_plus_return_minus_2": float(median_residual[peak_index]),
        },
        "groups": {},
    }
    for archive in ("greedy", "landmax"):
        output["groups"][archive] = {}
        for family in ("two_turn_7_5", "one_turn_15", "other"):
            indices = np.asarray(
                [
                    index
                    for index, row in enumerate(rows)
                    if row["archive"] == archive and row["family"] == family
                ],
                dtype=np.int64,
            )
            output["groups"][archive][family] = {
                "pairs": int(len(indices)),
                "same_progress_flow_correlation": summary(same[indices]),
                "time_reversed_flow_correlation": summary(mirrored[indices]),
            }

    RESULTS.write_text(
        json.dumps(output, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(output, indent=2), flush=True)


if __name__ == "__main__":
    main()
