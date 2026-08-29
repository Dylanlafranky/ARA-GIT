from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
IRR = HERE.parent
OUT = HERE / "results"
OUT.mkdir(parents=True, exist_ok=True)

EVENTS = ["GW170104", "GW170608", "GW170809", "GW170814", "GW170818"]
PRIMARY = ["T427 direct", "T428 paired", "T429 separated", "T432 dynamic"]
ALL_METHODS = PRIMARY + ["T430 budget (secondary)"]
GRID = np.arange(-0.495267578125, -0.031267578125 + 1e-10, 0.004)
LAGS = np.arange(-16, 17, dtype=int)
SEED = 43320260826
N_NULL = 2000

SOURCES = {
    "T427": IRR / "T427_spacetime_strain_handover/results/T427_CONSENSUS_COORDINATES.csv",
    "T428": IRR / "T428_paired_phase_spacetime/results/T428_CONSENSUS_COORDINATES.csv",
    "T429": IRR / "T429_separated_space_time_strength/results/T429_HOLDOUT_MODEL_FREE_HISTORIES.csv",
    "T430": IRR / "T430_remaining_traversal_connection/results/T430_DEVELOPMENT_HISTORIES.csv",
    "T432": IRR / "T432_lagged_pushpull_settlement/results/T432_DEVELOPMENT_HISTORIES.csv",
}


def rolling_median(a: np.ndarray, width: int = 7) -> np.ndarray:
    return pd.Series(a).rolling(width, center=True, min_periods=1).median().to_numpy(float)


def interp_event(df: pd.DataFrame, event: str, mcol: str, ccol: str, invert_m: bool = False):
    d = df[df["event"] == event].sort_values("time_s")
    t = d["time_s"].to_numpy(float)
    m = d[mcol].to_numpy(float)
    c = d[ccol].to_numpy(float)
    if invert_m:
        m = 2.0 - m
    keep = np.isfinite(t) & np.isfinite(m) & np.isfinite(c)
    t, m, c = t[keep], m[keep], c[keep]
    if len(t) < 5 or GRID[0] < t.min() - 0.005 or GRID[-1] > t.max() + 0.005:
        raise ValueError(f"Insufficient common coverage for {event}: {t.min()}..{t.max()}")
    return np.interp(GRID, t, m), np.interp(GRID, t, c)


def load_histories():
    d427 = pd.read_csv(SOURCES["T427"])
    d428 = pd.read_csv(SOURCES["T428"])
    d429 = pd.read_csv(SOURCES["T429"])
    d430 = pd.read_csv(SOURCES["T430"])
    d432 = pd.read_csv(SOURCES["T432"])
    histories = {m: {} for m in ALL_METHODS}
    for ev in EVENTS:
        histories["T427 direct"][ev] = interp_event(d427, ev, "c1", "c2")

        x = d428[d428.event == ev].copy()
        x["M_macro"] = (x["T_A"] + x["T_B"]) / 2.0
        x["C_macro"] = (x["K_A"] + x["K_B"]) / 2.0
        histories["T428 paired"][ev] = interp_event(x, ev, "M_macro", "C_macro")

        histories["T429 separated"][ev] = interp_event(d429, ev, "T_A", "S_B")
        histories["T430 budget (secondary)"][ev] = interp_event(
            d430, ev, "M_rem", "C_acc", invert_m=True
        )
        histories["T432 dynamic"][ev] = interp_event(
            d432, ev, "movement_M", "connection_C"
        )
    return histories


def derive(m: np.ndarray, c: np.ndarray):
    ms = rolling_median(m)
    cs = rolling_median(c)
    dm = np.gradient(ms)
    dc = np.gradient(cs)
    speed = np.sqrt(dm * dm + dc * dc)
    speed_rank = pd.Series(speed).rank(method="average").to_numpy(float) / len(speed)
    madm = np.median(np.abs(dm - np.median(dm))) * 1.4826 + 1e-12
    madc = np.median(np.abs(dc - np.median(dc))) * 1.4826 + 1e-12
    vec = np.column_stack([dm / madm, dc / madc])
    ridge_dist = np.sqrt((ms - 1.0) ** 2 + (cs - 1.0) ** 2)
    bursts = speed_rank >= 0.8
    return {"m": ms, "c": cs, "speed": speed_rank, "vec": vec,
            "ridge_dist": ridge_dist, "bursts": bursts}


def aligned(a: np.ndarray, b: np.ndarray, lag: int):
    if lag > 0:
        return a[:-lag], b[lag:]
    if lag < 0:
        return a[-lag:], b[:lag]
    return a, b


def bridge_metrics(a, b):
    best = None
    for lag in LAGS:
        sa, sb = aligned(a["speed"], b["speed"], lag)
        # The input histories are already converted to within-event ranks.
        # Pearson correlation of those ranks is the Spearman association.
        xa = sa - sa.mean()
        xb = sb - sb.mean()
        den = np.sqrt(np.dot(xa, xa) * np.dot(xb, xb))
        rho = float(np.dot(xa, xb) / den) if den > 1e-15 else -1.0
        if not np.isfinite(rho):
            rho = -1.0
        if best is None or rho > best[0]:
            best = (float(rho), int(lag))
    rho, lag = best
    ba, bb = aligned(a["bursts"], b["bursts"], lag)
    denom = ba.sum() + bb.sum()
    dice = float(2 * np.logical_and(ba, bb).sum() / denom) if denom else 0.0
    va, vb = aligned(a["vec"], b["vec"], lag)
    den = np.linalg.norm(va, axis=1) * np.linalg.norm(vb, axis=1)
    valid = den > 1e-10
    cos = np.sum(va[valid] * vb[valid], axis=1) / den[valid]
    orientation = float(np.median(cos)) if len(cos) else np.nan
    ridge_gap_ms = float(abs(GRID[np.argmin(a["ridge_dist"])] - GRID[np.argmin(b["ridge_dist"])]) * 1000)
    return {"speed_rho": rho, "lag_frames": lag, "lag_ms": lag * 4,
            "burst_dice": dice, "orientation_cosine": orientation,
            "ridge_time_gap_ms": ridge_gap_ms}


def shifted_derived(d, shift):
    out = dict(d)
    out["speed"] = np.roll(d["speed"], shift)
    out["bursts"] = np.roll(d["bursts"], shift)
    out["vec"] = np.roll(d["vec"], shift, axis=0)
    out["ridge_dist"] = np.roll(d["ridge_dist"], shift)
    return out


def bh_qvalues(pvals):
    p = np.asarray(pvals, float)
    n = len(p)
    order = np.argsort(p)
    q = np.empty(n, float)
    ranked = p[order] * n / np.arange(1, n + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    q[order] = np.minimum(ranked, 1.0)
    return q


def main():
    histories = load_histories()
    derived = {m: {e: derive(*histories[m][e]) for e in EVENTS} for m in ALL_METHODS}

    from itertools import combinations
    primary_pairs = list(combinations(PRIMARY, 2))
    secondary_pairs = [(m, "T430 budget (secondary)") for m in PRIMARY]
    all_pairs = primary_pairs + secondary_pairs

    event_rows = []
    pair_rows = []
    rng = np.random.default_rng(SEED)

    for ma, mb in all_pairs:
        observed = []
        for ev in EVENTS:
            met = bridge_metrics(derived[ma][ev], derived[mb][ev])
            observed.append(met)
            event_rows.append({"method_a": ma, "method_b": mb, "event": ev, **met})

        obs_rho = float(np.median([x["speed_rho"] for x in observed]))
        obs_dice = float(np.median([x["burst_dice"] for x in observed]))
        null_rho = np.empty(N_NULL)
        null_dice = np.empty(N_NULL)
        # Precompute every wrong-event/large-shift combination. Null replicates
        # then sample from this frozen lookup without changing the statistic.
        allowed_shifts = np.arange(32, len(GRID) - 31, dtype=int)
        lookup = {}
        for i, ev in enumerate(EVENTS):
            for j, bev in enumerate(EVENTS):
                if i == j:
                    continue
                for shift in allowed_shifts:
                    lookup[(i, j, int(shift))] = bridge_metrics(
                        derived[ma][ev], shifted_derived(derived[mb][bev], int(shift))
                    )
        for k in range(N_NULL):
            perm = rng.permutation(len(EVENTS))
            while np.any(perm == np.arange(len(EVENTS))):
                perm = rng.permutation(len(EVENTS))
            rs, ds = [], []
            for i, ev in enumerate(EVENTS):
                bev = EVENTS[int(perm[i])]
                shift = int(rng.choice(allowed_shifts))
                met = lookup[(i, int(perm[i]), shift)]
                rs.append(met["speed_rho"])
                ds.append(met["burst_dice"])
            null_rho[k] = np.median(rs)
            null_dice[k] = np.median(ds)
        p_rho = float((1 + np.sum(null_rho >= obs_rho)) / (N_NULL + 1))
        p_dice = float((1 + np.sum(null_dice >= obs_dice)) / (N_NULL + 1))
        pair_rows.append({
            "method_a": ma, "method_b": mb,
            "tier": "primary" if (ma, mb) in primary_pairs else "secondary",
            "median_speed_rho": obs_rho,
            "median_burst_dice": obs_dice,
            "p_speed": p_rho, "p_burst": p_dice,
            "null_speed_p95": float(np.quantile(null_rho, .95)),
            "null_burst_p95": float(np.quantile(null_dice, .95)),
            "median_abs_lag_ms": float(np.median([abs(x["lag_ms"]) for x in observed])),
            "median_orientation_cosine": float(np.nanmedian([x["orientation_cosine"] for x in observed])),
            "median_ridge_gap_ms": float(np.median([x["ridge_time_gap_ms"] for x in observed])),
        })

    event_df = pd.DataFrame(event_rows)
    pair_df = pd.DataFrame(pair_rows)
    mask = pair_df.tier == "primary"
    pair_df.loc[mask, "q_speed"] = bh_qvalues(pair_df.loc[mask, "p_speed"])
    pair_df.loc[mask, "q_burst"] = bh_qvalues(pair_df.loc[mask, "p_burst"])
    pair_df.loc[~mask, "q_speed"] = np.nan
    pair_df.loc[~mask, "q_burst"] = np.nan
    pair_df["bridge_pass"] = mask & (pair_df.q_speed <= .05) & (pair_df.q_burst <= .05)

    pass_count = int(pair_df.loc[mask, "bridge_pass"].sum())
    verdict = "BROAD BRIDGE SUPPORTED" if pass_count >= 3 else (
        "PARTIAL BRIDGE" if pass_count else "NO PRIMARY BRIDGE"
    )

    event_df.to_csv(OUT / "T433_EVENT_BRIDGES.csv", index=False)
    pair_df.to_csv(OUT / "T433_METHOD_PAIR_SUMMARY.csv", index=False)

    # Long common histories for reproducibility and visual inspection.
    hist_rows = []
    for method in ALL_METHODS:
        for ev in EVENTS:
            d = derived[method][ev]
            for i, t in enumerate(GRID):
                hist_rows.append({"method": method, "event": ev, "time_s": t,
                                  "M": d["m"][i], "C": d["c"][i],
                                  "speed_rank": d["speed"][i],
                                  "ridge_distance": d["ridge_dist"][i],
                                  "burst": int(d["bursts"][i])})
    hist_df = pd.DataFrame(hist_rows)
    hist_df.to_csv(OUT / "T433_COMMON_HISTORIES.csv", index=False)

    summary = {
        "verdict": verdict,
        "primary_pairs_passed": pass_count,
        "primary_pairs_total": len(primary_pairs),
        "common_events": EVENTS,
        "common_time_window_s": [float(GRID[0]), float(GRID[-1])],
        "grid_step_s": .004,
        "null_replicates_per_pair": N_NULL,
        "t431_excluded_as_non_independent_of_t432": True,
        "t430_secondary_only": True,
        "pairs": pair_df.to_dict(orient="records"),
    }
    (OUT / "T433_RESULTS.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # Save the strongest event/pair as a compact chart-ready table. Rendering
    # is handled by the native Data Analytics surface rather than a second
    # local chart runtime.
    primary_event = event_df.merge(pair_df[["method_a","method_b","tier"]], on=["method_a","method_b"])
    strongest = primary_event[primary_event.tier == "primary"].sort_values(
        ["speed_rho", "burst_dice"], ascending=False).iloc[0]
    ma, mb, ev = strongest.method_a, strongest.method_b, strongest.event
    a, b = derived[ma][ev], derived[mb][ev]
    lag = int(strongest.lag_frames)
    strongest_rows = []
    for method, d, display_shift in [(ma, a, 0), (mb, b, -lag)]:
        for i, t in enumerate(GRID):
            strongest_rows.append({
                "event": ev, "method": method, "time_s": float(t + display_shift*.004),
                "M": float(d["m"][i]), "C": float(d["c"][i]),
                "speed_rank": float(d["speed"][i]), "display_shift_ms": display_shift*4,
                "selected_pair_lag_ms": lag*4,
            })
    pd.DataFrame(strongest_rows).to_csv(OUT / "T433_STRONGEST_BRIDGE_HISTORY.csv", index=False)

    print(json.dumps({"verdict": verdict, "pass_count": pass_count,
                      "strongest": strongest.to_dict(),
                      "results": str(OUT / "T433_RESULTS.json")}, indent=2, default=str))


if __name__ == "__main__":
    main()
