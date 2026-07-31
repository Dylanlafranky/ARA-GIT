"""
Frozen test: Phi as one child->parent handover geometry across dimensions.

Protocol:
  PHI_DIMENSIONAL_HANDOVER_PROTOCOL_2026-07-30.md

Public data:
  dynamicslab MultiArm-Pendulum, Zenodo 10.5281/zenodo.6633719

The script uses only raw angles and timestamps. It does not use FFT, Hilbert
phase, SVD/POD, a normal-mode model, or equations of motion.
"""
from __future__ import annotations

import csv
import json
import math
import os
from dataclasses import dataclass, asdict

import numpy as np
from scipy.signal import find_peaks
from scipy.stats import spearmanr

from pendulum_common import (
    DRIVEN,
    OUT_DIR,
    RUNS,
    load_triple,
    load_triple_driven,
    rest_centered,
)


PDOM_S = 1.333
PROM_ARA = 0.02
DECIMATE = 20
N_PERM = 2000
SEED = 20260730

PHI = (1.0 + math.sqrt(5.0)) / 2.0
U_PHI = 2.0 - PHI
DIAM_PHI = np.array([U_PHI, 2.0 - U_PHI])
CIRC_PHI = np.array([U_PHI, 1.0 - U_PHI])
DIAM_MAX_DIST = PHI - 1.0
CIRC_MAX_DIST = U_PHI

DIAM_CONTROLS = {
    "phi": DIAM_PHI,
    "ridge": np.array([1.0]),
    "quarters": np.array([0.5, 1.5]),
    "thirds": np.array([2.0 / 3.0, 4.0 / 3.0]),
}
CIRC_CONTROLS = {
    "phi": CIRC_PHI,
    "quarters": np.array([0.25, 0.75]),
    "thirds": np.array([1.0 / 3.0, 2.0 / 3.0]),
    "ridge_opposition": np.array([0.0, 0.5]),
}


@dataclass
class Event:
    run: str
    regime: str
    child: int
    parent: int
    sample: int
    time_s: float
    diameter_x: float
    cycle_u: float
    diameter_phi_distance: float
    circular_phi_distance: float
    diameter_phi_proximity: float
    circular_phi_proximity: float
    joint_phi_proximity: float
    parent_retention: float
    current_parent_excursion: float
    next_parent_excursion: float


def extrema(x: np.ndarray, fs: float) -> np.ndarray:
    """Audited prominence-filtered genuine turns."""
    distance = max(1, int(0.4 * PDOM_S * fs))
    prom_rad = PROM_ARA * np.pi
    hi, _ = find_peaks(x, prominence=prom_rad, distance=distance)
    lo, _ = find_peaks(-x, prominence=prom_rad, distance=distance)
    return np.sort(np.concatenate([hi, lo]))


def nearest_linear_distance(values: np.ndarray, landmarks: np.ndarray) -> np.ndarray:
    return np.min(np.abs(values[:, None] - landmarks[None, :]), axis=1)


def circular_delta(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    d = np.abs(a[:, None] - b[None, :])
    return np.minimum(d, 1.0 - d)


def nearest_circular_distance(values: np.ndarray, landmarks: np.ndarray) -> np.ndarray:
    return np.min(circular_delta(values, landmarks), axis=1)


def event_at(
    c_idx: int,
    parent_turns: np.ndarray,
    parent_angle: np.ndarray,
    t: np.ndarray,
    run: str,
    regime: str,
    child: int,
    parent: int,
) -> Event | None:
    j = int(np.searchsorted(parent_turns, c_idx) - 1)
    if j < 0 or j + 2 >= len(parent_turns):
        return None
    p0, p1, p2 = map(int, parent_turns[j : j + 3])
    if not (p0 < c_idx < p1):
        return None

    denom = parent_angle[p1] - parent_angle[p0]
    if abs(denom) < 1e-12:
        return None

    # Local parent half-cycle, oriented from 0 to 2 by its actual traversal.
    x_d = 2.0 * (parent_angle[c_idx] - parent_angle[p0]) / denom
    x_d = float(np.clip(x_d, 0.0, 2.0))

    frac_half = (t[c_idx] - t[p0]) / (t[p1] - t[p0])
    cycle_u = float((0.5 * j + 0.5 * frac_half) % 1.0)

    dd = float(nearest_linear_distance(np.array([x_d]), DIAM_PHI)[0])
    dc = float(nearest_circular_distance(np.array([cycle_u]), CIRC_PHI)[0])
    pd = float(np.clip(1.0 - dd / DIAM_MAX_DIST, 0.0, 1.0))
    pc = float(np.clip(1.0 - dc / CIRC_MAX_DIST, 0.0, 1.0))
    joint = 0.5 * (pd + pc)

    a0 = float(abs(parent_angle[p1] - parent_angle[p0]))
    a1 = float(abs(parent_angle[p2] - parent_angle[p1]))
    if max(a0, a1) < 1e-12:
        return None
    retention = min(a0, a1) / max(a0, a1)

    return Event(
        run=run,
        regime=regime,
        child=child,
        parent=parent,
        sample=int(c_idx),
        time_s=float(t[c_idx]),
        diameter_x=x_d,
        cycle_u=cycle_u,
        diameter_phi_distance=dd,
        circular_phi_distance=dc,
        diameter_phi_proximity=pd,
        circular_phi_proximity=pc,
        joint_phi_proximity=joint,
        parent_retention=retention,
        current_parent_excursion=a0,
        next_parent_excursion=a1,
    )


def load_run(run: str, regime: str):
    if regime == "driven":
        return load_triple_driven(run, decimate=DECIMATE)
    return load_triple(run, decimate=DECIMATE)


def extract_events(run: str, regime: str) -> tuple[list[Event], dict]:
    t, th, _, fs = load_run(run, regime)
    rc = rest_centered(th)
    turns = {i: extrema(rc[i], fs) for i in (1, 2, 3)}
    events: list[Event] = []
    pair_meta = {}
    for child, parent in ((3, 2), (2, 1)):
        pair = f"{child}->{parent}"
        pair_events = []
        for c_idx in turns[child]:
            ev = event_at(
                int(c_idx), turns[parent], rc[parent], t, run, regime, child, parent
            )
            if ev is not None:
                events.append(ev)
                pair_events.append(ev)
        pair_meta[pair] = {
            "n_child_turns": int(len(turns[child])),
            "n_parent_turns": int(len(turns[parent])),
            "n_eligible": int(len(pair_events)),
            "valid_min": int(turns[parent][0] + 1),
            "valid_max": int(turns[parent][-2] - 1),
        }
    return events, {
        "fs": float(fs),
        "n_samples": int(len(t)),
        "duration_s": float(t[-1] - t[0]),
        "pairs": pair_meta,
        "t": t,
        "rc": rc,
        "turns": turns,
    }


def rank_lock(events: list[Event]) -> dict:
    rows = []
    z_num = 0.0
    z_den = 0.0
    for child, parent in ((3, 2), (2, 1)):
        e = [x for x in events if x.child == child and x.parent == parent]
        if len(e) < 4:
            r = float("nan")
            p = float("nan")
        else:
            r, p = spearmanr(
                [x.diameter_phi_proximity for x in e],
                [x.circular_phi_proximity for x in e],
            )
            r, p = float(r), float(p)
            if np.isfinite(r):
                rc = float(np.clip(r, -0.999999, 0.999999))
                weight = max(len(e) - 3, 1)
                z_num += weight * np.arctanh(rc)
                z_den += weight
        rows.append({"pair": f"{child}->{parent}", "n": len(e), "spearman_r": r, "p": p})
    pooled = float(np.tanh(z_num / z_den)) if z_den else float("nan")
    return {"by_pair": rows, "pooled_weighted_fisher_r": pooled}


def retention_difference(events: list[Event]) -> dict:
    if len(events) < 8:
        return {
            "n": len(events),
            "q25": float("nan"),
            "q75": float("nan"),
            "bottom_median": float("nan"),
            "top_median": float("nan"),
            "difference": float("nan"),
        }
    prox = np.array([e.joint_phi_proximity for e in events])
    retain = np.array([e.parent_retention for e in events])
    q25, q75 = np.quantile(prox, [0.25, 0.75])
    bottom = retain[prox <= q25]
    top = retain[prox >= q75]
    bm = float(np.median(bottom))
    tm = float(np.median(top))
    return {
        "n": len(events),
        "q25": float(q25),
        "q75": float(q75),
        "bottom_n": int(len(bottom)),
        "top_n": int(len(top)),
        "bottom_median": bm,
        "top_median": tm,
        "difference": tm - bm,
    }


def summarize_run(events: list[Event]) -> dict:
    x = np.array([e.diameter_x for e in events])
    u = np.array([e.cycle_u for e in events])
    landmark_d = {
        name: float(np.median(nearest_linear_distance(x, pts)))
        for name, pts in DIAM_CONTROLS.items()
    }
    landmark_c = {
        name: float(np.median(nearest_circular_distance(u, pts)))
        for name, pts in CIRC_CONTROLS.items()
    }
    ret_by_pair = {}
    for child, parent in ((3, 2), (2, 1)):
        e = [z for z in events if z.child == child and z.parent == parent]
        ret_by_pair[f"{child}->{parent}"] = retention_difference(e)
    return {
        "n_events": len(events),
        "median_joint_phi_proximity": float(
            np.median([e.joint_phi_proximity for e in events])
        ),
        "median_identity_retention": float(
            np.median([e.parent_retention for e in events])
        ),
        "diameter_landmark_median_distance": landmark_d,
        "circular_landmark_median_distance": landmark_c,
        "dimensional_locking": rank_lock(events),
        "retention": {
            "pooled": retention_difference(events),
            "by_pair": ret_by_pair,
        },
    }


def shifted_events_for_pair(
    base_events: list[Event],
    meta: dict,
    run: str,
    regime: str,
    child: int,
    parent: int,
    rng: np.random.Generator,
) -> list[Event]:
    pair = f"{child}->{parent}"
    lo = int(meta["pairs"][pair]["valid_min"])
    hi = int(meta["pairs"][pair]["valid_max"])
    width = hi - lo + 1
    if width <= 10:
        return []
    min_shift = max(1, int(1.5 * PDOM_S * meta["fs"]))
    possible = np.arange(min_shift, max(min_shift + 1, width - min_shift), dtype=int)
    if len(possible) == 0:
        possible = np.arange(1, width, dtype=int)
    shift = int(rng.choice(possible))
    out = []
    for old in base_events:
        shifted = lo + ((old.sample - lo + shift) % width)
        ev = event_at(
            shifted,
            meta["turns"][parent],
            meta["rc"][parent],
            meta["t"],
            run,
            regime,
            child,
            parent,
        )
        if ev is not None:
            out.append(ev)
    return out


def permutation_test(
    events: list[Event], meta: dict, run: str, regime: str, seed: int
) -> dict:
    rng = np.random.default_rng(seed)
    obs_prox = float(np.median([e.joint_phi_proximity for e in events]))
    obs_ret = retention_difference(events)["difference"]
    perm_prox = []
    perm_ret = []
    by_pair = {
        (child, parent): [
            e for e in events if e.child == child and e.parent == parent
        ]
        for child, parent in ((3, 2), (2, 1))
    }
    for _ in range(N_PERM):
        shifted_all = []
        for (child, parent), pair_events in by_pair.items():
            shifted_all.extend(
                shifted_events_for_pair(
                    pair_events, meta, run, regime, child, parent, rng
                )
            )
        if len(shifted_all) < 8:
            continue
        perm_prox.append(
            float(np.median([e.joint_phi_proximity for e in shifted_all]))
        )
        perm_ret.append(retention_difference(shifted_all)["difference"])

    pp = np.asarray(perm_prox)
    pr = np.asarray(perm_ret)
    p_prox = float((1 + np.sum(pp >= obs_prox)) / (1 + len(pp)))
    p_ret = float((1 + np.sum(pr >= obs_ret)) / (1 + len(pr)))
    return {
        "n_permutations": int(len(pp)),
        "observed_median_joint_proximity": obs_prox,
        "permutation_median_joint_proximity": float(np.median(pp)),
        "joint_proximity_p_one_sided": p_prox,
        "observed_retention_difference": float(obs_ret),
        "permutation_median_retention_difference": float(np.median(pr)),
        "retention_p_one_sided": p_ret,
    }


def specificity_pass(summary: dict) -> bool:
    d = summary["diameter_landmark_median_distance"]
    c = summary["circular_landmark_median_distance"]
    return all(d["phi"] < d[k] for k in d if k != "phi") and all(
        c["phi"] < c[k] for k in c if k != "phi"
    )


def verdict(summary: dict, perm: dict) -> dict:
    checks = {
        "landmark_specificity": specificity_pass(summary),
        "dimensional_locking_positive": (
            summary["dimensional_locking"]["pooled_weighted_fisher_r"] > 0
        ),
        "retention_difference_positive": (
            summary["retention"]["pooled"]["difference"] > 0
        ),
        "both_permutation_p_below_0_05": (
            perm["joint_proximity_p_one_sided"] < 0.05
            and perm["retention_p_one_sided"] < 0.05
        ),
    }
    n = sum(checks.values())
    label = "SUPPORTED" if n == 4 else ("MIXED" if n >= 2 else "NOT SUPPORTED")
    return {"label": label, "checks_passed": n, "checks": checks}


def main():
    all_events: list[Event] = []
    output = {
        "protocol": "PHI_DIMENSIONAL_HANDOVER_PROTOCOL_2026-07-30.md",
        "phi": PHI,
        "u_phi": U_PHI,
        "runs": {},
    }

    run_specs = [
        ("run1", "development"),
        ("run2", "development"),
        ("run3", "evaluation"),
        ("triple1", "driven"),
    ]
    for i, (run, regime) in enumerate(run_specs):
        events, meta = extract_events(run, regime)
        summary = summarize_run(events)
        perm = permutation_test(events, meta, run, regime, SEED + i)
        output["runs"][run] = {
            "regime": regime,
            "data": {
                "fs": meta["fs"],
                "duration_s": meta["duration_s"],
                "n_samples": meta["n_samples"],
                "pairs": meta["pairs"],
            },
            "summary": summary,
            "permutation": perm,
        }
        all_events.extend(events)

    evaluation = output["runs"]["run3"]
    output["frozen_evaluation_verdict"] = verdict(
        evaluation["summary"], evaluation["permutation"]
    )

    json_path = os.path.join(OUT_DIR, "phi_dimensional_handover_results.json")
    csv_path = os.path.join(OUT_DIR, "phi_dimensional_handover_events.csv")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, allow_nan=True)
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(all_events[0]).keys()))
        writer.writeheader()
        writer.writerows(asdict(e) for e in all_events)

    print(json.dumps(output, indent=2, allow_nan=True))
    print("saved", json_path)
    print("saved", csv_path)


if __name__ == "__main__":
    main()
