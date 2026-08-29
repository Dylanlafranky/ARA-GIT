from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
EXPECTED_EVENTS = ["GW170104", "GW170608", "GW170809", "GW170814", "GW170818"]
EXPECTED_METHODS = ["T427 direct", "T428 paired", "T429 separated", "T432 dynamic"]
SEEDS = [433420260826, 433420260827, 433420260828, 433420260829, 433420260830]
N_NULL = 5000


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def bh(p):
    p = np.asarray(p, float)
    n = len(p)
    order = np.argsort(p)
    ranked = p[order] * n / np.arange(1, n + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    q = np.empty(n)
    q[order] = np.minimum(ranked, 1)
    return q


def lead_p(seed, indices_a, indices_b, n):
    rng = np.random.default_rng(seed)
    shifts = np.arange(32, n - 31, dtype=int)
    null = np.empty(N_NULL)
    for k in range(N_NULL):
        perm = rng.permutation(5)
        while np.any(perm == np.arange(5)):
            perm = rng.permutation(5)
        gaps = []
        for i in range(5):
            shift = int(rng.choice(shifts))
            ib = (indices_b[int(perm[i])] + shift) % n
            gaps.append(abs(indices_a[i] - ib) * 4.0)
        null[k] = np.median(gaps)
    return float((1 + np.sum(null <= 16.0)) / (N_NULL + 1))


def main():
    lock = json.loads((HERE / "T433B_FREEZE_LOCK.json").read_text())
    checks = {}
    checks["protocol_hash"] = sha(HERE / "T433B_FULL_HANDOVER_PROTOCOL.md") == lock["protocol_sha256"]
    checks["script_hash"] = sha(HERE / "t433b_full_handover_bridge.py") == lock["script_sha256"]

    hist = pd.read_csv(OUT / "T433B_COMMON_HISTORIES.csv")
    checks["history_rows"] = len(hist) == 5 * 4 * 186
    checks["events"] = sorted(hist.event.unique()) == sorted(EXPECTED_EVENTS)
    checks["methods"] = sorted(hist.method.unique()) == sorted(EXPECTED_METHODS)
    checks["finite"] = np.isfinite(hist[["time_s", "M", "C", "speed_rank", "ridge_distance"]]).all().all()
    checks["ara_range"] = bool(hist.M.between(0, 2).all() and hist.C.between(0, 2).all())

    derived_rows = []
    ridge_indices = {m: [] for m in ["T427 direct", "T429 separated"]}
    for ma, mb in [("T427 direct", "T429 separated")]:
        for ev in EXPECTED_EVENTS:
            da = hist[(hist.method == ma) & (hist.event == ev)].sort_values("time_s")
            db = hist[(hist.method == mb) & (hist.event == ev)].sort_values("time_s")
            ia = int(np.argmin(da.ridge_distance.to_numpy()))
            ib = int(np.argmin(db.ridge_distance.to_numpy()))
            ridge_indices[ma].append(ia)
            ridge_indices[mb].append(ib)
            derived_rows.append((ev, abs(ia-ib)*4.0))
    expected_gaps = dict(zip(EXPECTED_EVENTS, [16.0, 176.0, 0.0, 16.0, 164.0]))
    checks["lead_event_gaps"] = all(abs(g-expected_gaps[e]) < 1e-9 for e,g in derived_rows)
    checks["lead_median_gap"] = abs(np.median([g for _,g in derived_rows]) - 16.0) < 1e-9

    ps = [lead_p(s, ridge_indices["T427 direct"], ridge_indices["T429 separated"], 186) for s in SEEDS]
    checks["seed_stable_raw_p_below_0_01"] = max(ps) < .01
    checks["seed_stable_bonferroni_six_below_0_05"] = max(ps) * 6 < .05

    source_files = [
        HERE.parent / "T427_spacetime_strain_handover/results/T427_CONSENSUS_COORDINATES.csv",
        HERE.parent / "T428_paired_phase_spacetime/results/T428_CONSENSUS_COORDINATES.csv",
        HERE.parent / "T429_separated_space_time_strength/results/T429_HOLDOUT_MODEL_FREE_HISTORIES.csv",
        HERE.parent / "T432_lagged_pushpull_settlement/results/T432_DEVELOPMENT_HISTORIES.csv",
    ]
    checks = {k: bool(v) for k, v in checks.items()}
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "lead_seed_sensitivity_p": ps,
        "lead_seed_sensitivity_range": [min(ps), max(ps)],
        "source_hashes_sha256": {str(p.relative_to(HERE.parents[2])): sha(p) for p in source_files},
        "interpretation": "T427/T429 ridge-time bridge is exploratory and stable to five control seeds; it does not alter the frozen T433B no-universal-bridge verdict."
    }
    (OUT / "T433_INDEPENDENT_VALIDATION.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
