"""Exploratory ridge-time bridge test following frozen T433B.

The frozen protocol declared ridge timing descriptive. This post-frozen test
therefore cannot alter T433B's verdict; it tests a newly noticed bridge lead.
"""

from __future__ import annotations

from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

import t433_cross_method_bridge as base
import t433b_full_handover_bridge as full


HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
SEED = 433420260826
N_NULL = 5000


def ridge_index(d):
    return int(np.argmin(d["ridge_dist"]))


def main():
    base.GRID = full.GRID
    histories = full.load_primary()
    derived = {m: {e: base.derive(*histories[m][e]) for e in full.EVENTS}
               for m in full.METHODS}
    rng = np.random.default_rng(SEED)
    shifts = np.arange(32, len(full.GRID) - 31, dtype=int)
    rows = []
    event_rows = []

    for ma, mb in combinations(full.METHODS, 2):
        event_gaps = []
        for ev in full.EVENTS:
            ia = ridge_index(derived[ma][ev])
            ib = ridge_index(derived[mb][ev])
            gap = abs(ia - ib) * 4.0
            event_gaps.append(gap)
            event_rows.append({
                "method_a": ma, "method_b": mb, "event": ev,
                "ridge_time_a_s": float(full.GRID[ia]),
                "ridge_time_b_s": float(full.GRID[ib]),
                "ridge_gap_ms": float(gap),
            })
        observed = float(np.median(event_gaps))

        null = np.empty(N_NULL)
        for k in range(N_NULL):
            perm = rng.permutation(len(full.EVENTS))
            while np.any(perm == np.arange(len(full.EVENTS))):
                perm = rng.permutation(len(full.EVENTS))
            gaps = []
            for i, ev in enumerate(full.EVENTS):
                bev = full.EVENTS[int(perm[i])]
                shift = int(rng.choice(shifts))
                ia = ridge_index(derived[ma][ev])
                ib = (ridge_index(derived[mb][bev]) + shift) % len(full.GRID)
                # Linear event-time separation, not circular distance.
                gaps.append(abs(ia - ib) * 4.0)
            null[k] = np.median(gaps)

        rows.append({
            "method_a": ma, "method_b": mb,
            "median_same_event_ridge_gap_ms": observed,
            "event_gaps_ms": ";".join(str(int(x)) for x in event_gaps),
            "null_median_ms": float(np.median(null)),
            "null_p05_ms": float(np.quantile(null, .05)),
            "p_small_gap": float((1 + np.sum(null <= observed)) / (N_NULL + 1)),
        })

    out = pd.DataFrame(rows)
    out["q_small_gap"] = base.bh_qvalues(out.p_small_gap)
    out["exploratory_ridge_bridge"] = out.q_small_gap <= .05
    out.to_csv(OUT / "T433D_RIDGE_BRIDGE.csv", index=False)
    pd.DataFrame(event_rows).to_csv(OUT / "T433D_RIDGE_EVENT_ROWS.csv", index=False)
    print(out.sort_values("p_small_gap").to_string(index=False))


if __name__ == "__main__":
    main()
