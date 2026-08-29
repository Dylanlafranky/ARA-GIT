"""Post-frozen exploratory map of event-specific T433B bridges.

This does not change or rescue the frozen T433B global verdict. It answers the
narrower question of whether any individual event/method pair is unusual
relative to wrong-event, large-time-shift controls.
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


def main():
    base.GRID = full.GRID
    histories = full.load_primary()
    derived = {m: {e: base.derive(*histories[m][e]) for e in full.EVENTS}
               for m in full.METHODS}
    shifts = np.arange(32, len(full.GRID) - 31, dtype=int)
    rows = []
    for ma, mb in combinations(full.METHODS, 2):
        for ev in full.EVENTS:
            obs = base.bridge_metrics(derived[ma][ev], derived[mb][ev])
            null_rho, null_dice = [], []
            for bev in full.EVENTS:
                if bev == ev:
                    continue
                for shift in shifts:
                    met = base.bridge_metrics(
                        derived[ma][ev],
                        base.shifted_derived(derived[mb][bev], int(shift)),
                    )
                    null_rho.append(met["speed_rho"])
                    null_dice.append(met["burst_dice"])
            null_rho = np.asarray(null_rho)
            null_dice = np.asarray(null_dice)
            rows.append({
                "method_a": ma, "method_b": mb, "event": ev,
                **obs,
                "p_speed_event": (1 + np.sum(null_rho >= obs["speed_rho"])) / (len(null_rho) + 1),
                "p_burst_event": (1 + np.sum(null_dice >= obs["burst_dice"])) / (len(null_dice) + 1),
                "null_count": len(null_rho),
            })
    out = pd.DataFrame(rows)
    out["q_speed_event"] = base.bh_qvalues(out.p_speed_event)
    out["q_burst_event"] = base.bh_qvalues(out.p_burst_event)
    out["event_bridge_pass"] = (out.q_speed_event <= .05) & (out.q_burst_event <= .05)
    out.to_csv(OUT / "T433C_EVENT_SPECIFIC_BRIDGE_MAP.csv", index=False)
    print(out.sort_values(["p_speed_event", "p_burst_event"])[[
        "method_a", "method_b", "event", "speed_rho", "burst_dice",
        "lag_ms", "p_speed_event", "p_burst_event", "q_speed_event",
        "q_burst_event", "event_bridge_pass"
    ]].head(15).to_string(index=False))
    print(f"\nEvent-specific FDR bridges: {int(out.event_bridge_pass.sum())}/{len(out)}")


if __name__ == "__main__":
    main()

