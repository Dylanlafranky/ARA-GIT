"""Post-result diagnostic for Q35.

This does not alter Q35's frozen gates or verdict. It checks whether the
phase-opposition result seen in the 84 seam-eligible lineages also appears
across every development-eligible fixed loop.
"""

from __future__ import annotations

import json

import numpy as np

import q35_whole_phase_external_counterpart_test as q35


OUTPUT = q35.HERE / "Q35_POST_RESULT_ALL_LOOP_DIAGNOSTIC.json"


def main() -> None:
    derived = np.load(q35.CACHE)
    h = np.asarray(derived["closure"], dtype=np.float64)
    _, phase, cal = q35.calibration_and_phase(h)
    eligible, _, _ = q35.complete_loop_mask(phase, cal["w"])
    candidates = q35.choose_candidates(phase, eligible)

    metrics = {variant: [] for variant in q35.VARIANTS}
    lag_counts = {str(lag): 0 for lag in q35.LAGS}
    for candidate in candidates:
        seed = int(candidate["seed"])
        source_pair = int(candidate["source_pair"])
        counterpart_pair = int(candidate["counterpart_pair"])
        pair_control = int(candidate["pair_control"])
        lag = int(candidate["lag"])
        lag_counts[str(lag)] += 1
        times = np.arange(q35.EVAL_START, q35.EVAL_STOP - lag, dtype=np.int16)
        a = phase[0, seed, times, source_pair]
        for variant in q35.VARIANTS:
            branch, bseed, bpair, btimes = q35.b_indices(
                variant,
                seed,
                source_pair,
                counterpart_pair,
                pair_control,
                lag,
                times,
            )
            b = phase[branch, bseed, btimes, bpair]
            opposition, residual, half_turn = q35.phase_metrics(a, b)
            metrics[variant].append(
                (seed, opposition, residual, half_turn)
            )

    summary = {}
    for variant, values in metrics.items():
        array = np.asarray(
            [[row[1], row[2], row[3]] for row in values],
            dtype=np.float64,
        )
        summary[variant] = {
            "lineages": int(array.shape[0]),
            "median_opposition": float(np.nanmedian(array[:, 0])),
            "positive_opposition_fraction": float(
                np.nanmean(array[:, 0] > 0)
            ),
            "median_parent_residual": float(np.nanmedian(array[:, 1])),
            "median_half_turn_occupancy": float(
                np.nanmedian(array[:, 2])
            ),
        }

    result = {
        "status": "POST-RESULT DESCRIPTIVE ONLY — DOES NOT ALTER Q35",
        "complete_c2_loops": int(np.sum(eligible)),
        "candidate_lineages": int(len(candidates)),
        "lag_counts": lag_counts,
        "summary": summary,
        "reading_boundary": (
            "This removes Q35's seam-frequency eligibility restriction only "
            "to diagnose whether its phase result was confined to 84 rare "
            "lineages. It is not a new preregistered claim test."
        ),
    }
    OUTPUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

