"""Post-verdict descriptive Q38 replay on the already-open Q37 landmax archive."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import q38_fixed_anchor_phase_cycle_test as q38


HERE = Path(__file__).resolve().parent
DATA = HERE / "public_data" / "q37_signed_crossing_landmax"
DERIVED = DATA / "q37_derived_cache.npz"
CONNECTED = DATA / "q37_connected_cache.npy"
OUTPUT = HERE / "Q38_Q37_LANDMAX_DESCRIPTIVE_REPLAY.json"


def main() -> None:
    derived = np.load(DERIVED)
    closure = derived["closure"]
    connected = np.load(CONNECTED, mmap_mode="r")
    eligible, coherence = q38.complete_loops(closure)
    rows: list[dict[str, object]] = []
    seeds: set[int] = set()
    lineages: set[tuple[int, int]] = set()
    for seed in range(100):
        for pair in np.flatnonzero(eligible[seed]):
            pair = int(pair)
            control_pair = q38.pair_control(eligible, seed, pair)
            if control_pair is None:
                continue
            threshold = float(np.quantile(closure[0, seed, :250, pair], 0.20))
            for time in q38.event_times(closure[0, seed, :, pair], threshold):
                specifications = {
                    "exact": (0, seed, pair, time),
                    "time": (0, seed, pair, q38.shifted_time(time)),
                    "pair": (0, seed, control_pair, time),
                    "network": (1, seed, pair, time),
                }
                row: dict[str, object] = {
                    "seed": seed,
                    "source_pair": pair,
                    "time": time,
                    "pair_control": control_pair,
                    "development_circulation": float(coherence[seed, pair]),
                    "development_q20": threshold,
                }
                for variant, specification in specifications.items():
                    metrics = q38.cycle_metrics(
                        *specification, closure=closure, connected=connected
                    )
                    row.update(
                        {f"{variant}_{key}": value for key, value in metrics.items()}
                    )
                rows.append(row)
                seeds.add(seed)
                lineages.add((seed, pair))
    variants = ("exact", "time", "pair", "network")
    summary = {variant: q38.summarize(rows, variant) for variant in variants}
    bootstrap = {
        "cycle_above_half": q38.cluster_probability(
            rows, "exact_cycle", null_value=0.50
        ),
        "cycle_vs_controls": {
            variant: q38.cluster_probability(
                rows, "exact_cycle", f"{variant}_cycle"
            )
            for variant in ("time", "pair", "network")
        },
        "score_vs_controls": {
            variant: q38.cluster_probability(
                rows, "exact_cycle_score", f"{variant}_cycle_score"
            )
            for variant in ("time", "pair", "network")
        },
    }
    result = {
        "test_id": "Q38-LANDMAX-DESCRIPTIVE-REPLAY-v1",
        "date": "2026-07-27",
        "status": "POST-VERDICT DESCRIPTIVE ONLY",
        "source": "Q37 untouched target after Q38 prospective verdict sealed",
        "eligibility": {
            "complete_c2_lineages": int(np.sum(eligible)),
            "events": len(rows),
            "represented_seeds": len(seeds),
            "represented_lineages": len(lineages),
        },
        "summary": summary,
        "bootstrap": bootstrap,
        "boundary": (
            "This replay was calculated after the Q38 target verdict and "
            "cannot alter or rescue that verdict."
        ),
    }
    OUTPUT.write_text(
        json.dumps(result, indent=2, allow_nan=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, allow_nan=True))


if __name__ == "__main__":
    main()
