from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

import t433_cross_method_bridge as base


HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
OUT.mkdir(parents=True, exist_ok=True)

base.GRID = np.arange(-0.495267578125, 0.244732421875 + 1e-10, 0.004)
GRID = base.GRID
EVENTS = base.EVENTS
METHODS = base.PRIMARY
N_NULL = 2000
SEED = 43320260826


def load_primary():
    d427 = pd.read_csv(base.SOURCES["T427"])
    d428 = pd.read_csv(base.SOURCES["T428"])
    d429 = pd.read_csv(base.SOURCES["T429"])
    d432 = pd.read_csv(base.SOURCES["T432"])
    histories = {m: {} for m in METHODS}
    for ev in EVENTS:
        histories["T427 direct"][ev] = base.interp_event(d427, ev, "c1", "c2")
        x = d428[d428.event == ev].copy()
        x["M_macro"] = (x["T_A"] + x["T_B"]) / 2.0
        x["C_macro"] = (x["K_A"] + x["K_B"]) / 2.0
        histories["T428 paired"][ev] = base.interp_event(x, ev, "M_macro", "C_macro")
        histories["T429 separated"][ev] = base.interp_event(d429, ev, "T_A", "S_B")
        histories["T432 dynamic"][ev] = base.interp_event(d432, ev, "movement_M", "connection_C")
    return histories


def main():
    histories = load_primary()
    derived = {m: {e: base.derive(*histories[m][e]) for e in EVENTS} for m in METHODS}
    pairs = list(combinations(METHODS, 2))
    rng = np.random.default_rng(SEED)
    event_rows, pair_rows = [], []

    for ma, mb in pairs:
        observed = []
        for ev in EVENTS:
            met = base.bridge_metrics(derived[ma][ev], derived[mb][ev])
            observed.append(met)
            event_rows.append({"method_a": ma, "method_b": mb, "event": ev, **met})

        obs_rho = float(np.median([x["speed_rho"] for x in observed]))
        obs_dice = float(np.median([x["burst_dice"] for x in observed]))
        allowed_shifts = np.arange(32, len(GRID) - 31, dtype=int)
        lookup = {}
        for i, ev in enumerate(EVENTS):
            for j, bev in enumerate(EVENTS):
                if i == j:
                    continue
                for shift in allowed_shifts:
                    lookup[(i, j, int(shift))] = base.bridge_metrics(
                        derived[ma][ev], base.shifted_derived(derived[mb][bev], int(shift))
                    )

        null_rho, null_dice = np.empty(N_NULL), np.empty(N_NULL)
        for k in range(N_NULL):
            perm = rng.permutation(len(EVENTS))
            while np.any(perm == np.arange(len(EVENTS))):
                perm = rng.permutation(len(EVENTS))
            rs, ds = [], []
            for i in range(len(EVENTS)):
                shift = int(rng.choice(allowed_shifts))
                met = lookup[(i, int(perm[i]), shift)]
                rs.append(met["speed_rho"])
                ds.append(met["burst_dice"])
            null_rho[k] = np.median(rs)
            null_dice[k] = np.median(ds)

        pair_rows.append({
            "method_a": ma, "method_b": mb,
            "median_speed_rho": obs_rho,
            "median_burst_dice": obs_dice,
            "p_speed": float((1 + np.sum(null_rho >= obs_rho)) / (N_NULL + 1)),
            "p_burst": float((1 + np.sum(null_dice >= obs_dice)) / (N_NULL + 1)),
            "null_speed_p95": float(np.quantile(null_rho, .95)),
            "null_burst_p95": float(np.quantile(null_dice, .95)),
            "median_abs_lag_ms": float(np.median([abs(x["lag_ms"]) for x in observed])),
            "median_orientation_cosine": float(np.nanmedian([x["orientation_cosine"] for x in observed])),
            "median_ridge_gap_ms": float(np.median([x["ridge_time_gap_ms"] for x in observed])),
        })

    event_df = pd.DataFrame(event_rows)
    pair_df = pd.DataFrame(pair_rows)
    pair_df["q_speed"] = base.bh_qvalues(pair_df.p_speed)
    pair_df["q_burst"] = base.bh_qvalues(pair_df.p_burst)
    pair_df["bridge_pass"] = (pair_df.q_speed <= .05) & (pair_df.q_burst <= .05)
    pass_count = int(pair_df.bridge_pass.sum())
    verdict = "BROAD BRIDGE SUPPORTED" if pass_count >= 3 else (
        "PARTIAL BRIDGE" if pass_count else "NO PRIMARY BRIDGE"
    )

    event_df.to_csv(OUT / "T433B_EVENT_BRIDGES.csv", index=False)
    pair_df.to_csv(OUT / "T433B_METHOD_PAIR_SUMMARY.csv", index=False)

    hist_rows = []
    for method in METHODS:
        for ev in EVENTS:
            d = derived[method][ev]
            for i, t in enumerate(GRID):
                hist_rows.append({"method": method, "event": ev, "time_s": t,
                                  "M": d["m"][i], "C": d["c"][i],
                                  "speed_rank": d["speed"][i],
                                  "ridge_distance": d["ridge_dist"][i],
                                  "burst": int(d["bursts"][i])})
    pd.DataFrame(hist_rows).to_csv(OUT / "T433B_COMMON_HISTORIES.csv", index=False)

    strongest = event_df.sort_values(["speed_rho", "burst_dice"], ascending=False).iloc[0]
    ma, mb, ev = strongest.method_a, strongest.method_b, strongest.event
    lag = int(strongest.lag_frames)
    rows = []
    for method, d, display_shift in [
        (ma, derived[ma][ev], 0), (mb, derived[mb][ev], -lag)
    ]:
        for i, t in enumerate(GRID):
            rows.append({"event": ev, "method": method,
                         "time_s": float(t + display_shift*.004),
                         "M": float(d["m"][i]), "C": float(d["c"][i]),
                         "speed_rank": float(d["speed"][i]),
                         "display_shift_ms": display_shift*4,
                         "selected_pair_lag_ms": lag*4})
    pd.DataFrame(rows).to_csv(OUT / "T433B_STRONGEST_BRIDGE_HISTORY.csv", index=False)

    summary = {
        "verdict": verdict,
        "primary_pairs_passed": pass_count,
        "primary_pairs_total": len(pairs),
        "common_events": EVENTS,
        "common_time_window_s": [float(GRID[0]), float(GRID[-1])],
        "grid_step_s": .004,
        "null_replicates_per_pair": N_NULL,
        "pairs": pair_df.to_dict(orient="records"),
        "strongest_event_bridge": strongest.to_dict(),
    }
    (OUT / "T433B_RESULTS.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({"verdict": verdict, "pass_count": pass_count,
                      "strongest": strongest.to_dict()}, indent=2, default=str))


if __name__ == "__main__":
    main()

