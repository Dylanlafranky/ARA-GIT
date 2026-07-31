"""Post-result control for Q42's coarse-cadence sampling asymmetry.

For each eligible lineage, fit a single symmetric sinusoid at its measured
orbit period, sample it at the identical integer times, and send it through
the unchanged Q42 half-wave extraction.  The difference between observed and
synthetic closure residual estimates what coarse cadence alone cannot explain.
"""

from __future__ import annotations

import csv
import gzip
import json
import pathlib
from collections import defaultdict

import numpy as np

import q40_return_flow_relation_reversal_test as base
import q42_ara_dual_strand_flow_test as q42


HERE = pathlib.Path(__file__).resolve().parent
STRANDS = HERE / "Q42_ARA_DUAL_STRAND_FLOW_STRANDS.csv.gz"
RESULTS = HERE / "Q42A_POST_RESULT_SYMMETRIC_SAMPLING_CONTROL.json"
BOOTSTRAP_SEED = 420029
BOOTSTRAP_DRAWS = 20_000


def summary(values) -> dict:
    data = np.asarray(list(values), dtype=np.float64)
    data = data[np.isfinite(data)]
    if not len(data):
        return {"count": 0}
    return {
        "count": int(len(data)),
        "mean": float(np.mean(data)),
        "p25": float(np.quantile(data, 0.25)),
        "median": float(np.median(data)),
        "p75": float(np.quantile(data, 0.75)),
    }


def read_observed():
    grouped = defaultdict(list)
    with gzip.open(STRANDS, "rt", newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            grouped[
                (row["archive"], int(row["seed"]), int(row["pair"]))
            ].append(float(row["closure_mae"]))
    return {
        key: float(np.median(values))
        for key, values in grouped.items()
    }


def bootstrap_seed_difference(rows: list[dict]) -> dict:
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["archive"], row["seed"])].append(
            row["observed_median_mae"] - row["symmetric_median_mae"]
        )
    values = np.asarray(
        [np.mean(group) for group in grouped.values()],
        dtype=np.float64,
    )
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    estimates = np.empty(BOOTSTRAP_DRAWS, dtype=np.float64)
    for index in range(BOOTSTRAP_DRAWS):
        estimates[index] = float(
            np.mean(rng.choice(values, size=len(values), replace=True))
        )
    return {
        "seed_clusters": int(len(values)),
        "mean_observed_minus_symmetric": float(np.mean(values)),
        "ci95": [
            float(np.quantile(estimates, 0.025)),
            float(np.quantile(estimates, 0.975)),
        ],
        "bootstrap_fraction_above_zero": float(np.mean(estimates > 0)),
    }


def main() -> None:
    observed = read_observed()
    rows = []
    sample = np.arange(500, dtype=np.float64)
    development_sample = sample[:250]

    for archive, paths in q42.DATASETS.items():
        closure = np.asarray(np.load(paths["derived"])["closure"], dtype=np.float32)
        for seed in range(closure.shape[0]):
            for pair in range(closure.shape[2]):
                coordinate = base.coordinates(closure[seed, :, pair])
                if coordinate is None:
                    continue
                u, v, _labels, _direction, coherence, occupancy = coordinate
                if coherence < 0.80 or occupancy < 0.05:
                    continue
                family, fit = q42.cadence_family(u, v)
                period = float(fit["angular_period_samples"])
                if not np.isfinite(period) or period <= 0:
                    continue
                omega = 2 * np.pi / period
                design = np.column_stack(
                    (
                        np.ones(250),
                        np.cos(omega * development_sample),
                        np.sin(omega * development_sample),
                    )
                )
                coefficients = np.linalg.lstsq(
                    design,
                    np.asarray(closure[seed, :250, pair], dtype=np.float64),
                    rcond=None,
                )[0]
                synthetic = (
                    coefficients[0]
                    + coefficients[1] * np.cos(omega * sample)
                    + coefficients[2] * np.sin(omega * sample)
                )
                synthetic_rows, *_profiles = q42.extract_strand_pairs(
                    archive,
                    seed,
                    pair,
                    synthetic,
                    family,
                )
                key = (archive, seed, pair)
                if not synthetic_rows or key not in observed:
                    continue
                rows.append(
                    {
                        "archive": archive,
                        "seed": seed,
                        "pair": pair,
                        "family": family,
                        "period": period,
                        "observed_median_mae": observed[key],
                        "symmetric_median_mae": float(
                            np.median(
                                [
                                    row["closure_mae"]
                                    for row in synthetic_rows
                                ]
                            )
                        ),
                    }
                )

    output = {
        "status": "POST-RESULT SAMPLING CONTROL",
        "question": (
            "How much Q42 strand-closure mismatch is reproduced by a fitted "
            "perfectly symmetric single sinusoid at the same sample cadence?"
        ),
        "lineages": len(rows),
        "combined_bootstrap": bootstrap_seed_difference(rows),
        "archives": {},
    }
    for archive in q42.DATASETS:
        selected_archive = [row for row in rows if row["archive"] == archive]
        item = {
            "lineages": len(selected_archive),
            "observed_median_mae": summary(
                row["observed_median_mae"] for row in selected_archive
            ),
            "symmetric_median_mae": summary(
                row["symmetric_median_mae"] for row in selected_archive
            ),
            "observed_minus_symmetric": summary(
                row["observed_median_mae"] - row["symmetric_median_mae"]
                for row in selected_archive
            ),
            "families": {},
        }
        for family in ("two_turn_7_5", "one_turn_15", "other"):
            selected = [
                row for row in selected_archive if row["family"] == family
            ]
            item["families"][family] = {
                "lineages": len(selected),
                "observed_median_mae": summary(
                    row["observed_median_mae"] for row in selected
                ),
                "symmetric_median_mae": summary(
                    row["symmetric_median_mae"] for row in selected
                ),
                "observed_minus_symmetric": summary(
                    row["observed_median_mae"] - row["symmetric_median_mae"]
                    for row in selected
                ),
            }
        output["archives"][archive] = item

    RESULTS.write_text(
        json.dumps(output, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(output, indent=2), flush=True)


if __name__ == "__main__":
    main()
