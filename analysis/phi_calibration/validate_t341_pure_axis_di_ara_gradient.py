"""Independent validation for T341; does not import the primary runner."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
STEM = "T341_PURE_AXIS_DI_ARA_GRADIENT"
PROTOCOL = HERE / f"{STEM}_PROTOCOL_v1_FROZEN.md"
QUTRIT = REPO / "analysis" / "quantum" / "Q53_RECORDED_QUTRIT_EXTERNAL_RETURN_EVENTS.npz"
BUBBLES = REPO / "analysis" / "vertical_ara_bubbles" / "results" / "T334_BUBBLE_OCTAVE_RELATIVE_IRRATIONALITY_QUADRANT_EVENTS.csv"
RIVER = REPO / "analysis" / "hydraulics" / "results" / "T335_RIVER_IRRATIONALITY_DI_ARA_EVENTS.csv"
RESULTS = HERE / f"{STEM}_RESULTS.json"
EVENTS = HERE / f"{STEM}_EVENTS.csv"
SUMMARY = HERE / f"{STEM}_SUMMARY.csv"
PAIRS = HERE / f"{STEM}_FIXED_PAIRS.csv"
NULLS = HERE / f"{STEM}_NULLS.csv"
SENS = HERE / f"{STEM}_CONE_SENSITIVITY.csv"
FIGURE = HERE / f"{STEM}_FIGURE.png"
REPORT = HERE / f"{STEM}_REPORT_2026-08-05.md"
OUT = HERE / f"{STEM}_VALIDATION.json"

PHI = (1 + math.sqrt(5)) / 2
TAU = 1 / PHI**2
RADIAL = {"plastic": 1.324717957244746, "sqrt2": math.sqrt(2), "three_halves": 1.5, "phi": PHI, "octave": 2.0, "e": math.e}
ANGULAR = {"quarter": .25, "third": 1/3, "one_over_e": 1/math.e, "three_eighths": 3/8, "phi_inverse_squared": TAU, "two_fifths": .4, "sqrt2_minus_1": math.sqrt(2)-1}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8*1024*1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def loss(r, c, alpha, tau, euclid=False):
    rr, cc = r/math.log(alpha), c/tau
    b = np.sqrt(rr*rr+cc*cc) if euclid else rr+cc
    return float(np.median(np.abs(b-1)))


def source_counts() -> dict[tuple[str, str], int]:
    out = {}
    q = np.load(QUTRIT)
    for split in ("calibration", "holdout"):
        total = 0
        for plane in ("psi0_psi1", "psi1_psi2", "psi2_psi0"):
            time = q[f"{plane}_time"].astype(np.int64)
            residual = q[f"{plane}_residual"].astype(float)
            amp = q[f"{plane}_circle_strength"].astype(float)
            heading = q[f"{plane}_circle_heading"].astype(float)
            eligible = np.isfinite(amp)&np.isfinite(heading)&np.isfinite(residual)&(amp>=.01)&(residual<=.25)
            mid = len(time)//2
            start, stop = (0, mid) if split == "calibration" else (mid, len(time))
            idx = np.arange(start, stop-1)
            total += int((eligible[idx]&eligible[idx+1]&(np.diff(time)[idx]<=2200)).sum())
        out[("recorded_qutrit", split)] = total
    b = pd.read_csv(BUBBLES, usecols=["source_kind", "split"])
    b = b[b.source_kind == "observed"]
    for split, part in b.groupby("split"): out[("recorded_bubbles", split)] = len(part)
    rv = pd.read_csv(RIVER, usecols=["source_kind", "split"])
    rv = rv[rv.source_kind == "observed"]
    for split, part in rv.groupby("split"): out[("recorded_river", split)] = len(part)
    return out


def main():
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    e = pd.read_csv(EVENTS, low_memory=False)
    s = pd.read_csv(SUMMARY)
    p = pd.read_csv(PAIRS)
    n = pd.read_csv(NULLS)
    sens = pd.read_csv(SENS)
    checks = {}
    checks["protocol_hash"] = sha(PROTOCOL) == result["protocol_sha256"]
    checks["source_hashes"] = all(sha(REPO/path) == meta["sha256"] for path, meta in result["source_audit"].items())
    checks["output_existence"] = all(x.exists() and x.stat().st_size > 0 for x in (EVENTS, SUMMARY, PAIRS, NULLS, SENS, FIGURE, REPORT))
    checks["row_counts"] = (len(e)==result["event_rows"] and len(s)==result["summary_rows"] and len(p)==result["pair_rows"] and len(n)==result["null_rows"] and len(sens)==result["sensitivity_rows"])
    expected_counts = source_counts()
    actual_counts = {(d, sp): len(part) for (d, sp), part in e.groupby(["domain", "split"])}
    checks["source_event_counts"] = expected_counts == actual_counts

    radial = e.radial.to_numpy(float); delta = e.delta.to_numpy(float)
    x = 2*radial/(1+radial); y = 1+delta/math.pi
    dr = np.abs(x-1); dc = np.abs(y-1)
    gamma = np.degrees(np.arctan2(dc, dr)); R = np.abs(np.log(radial)); C = np.abs(delta)/(2*math.pi)
    checks["ara_coordinates"] = bool(np.allclose(e.x_radial_ara, x) and np.allclose(e.y_angular_ara, y) and np.allclose(e.gamma_deg, gamma) and np.allclose(e.R_abs_log_radial, R) and np.allclose(e.C_abs_turns, C))

    controls = {}
    for domain, cal in e[e.split=="calibration"].groupby("domain"):
        lcal=cal[cal.gamma_deg<=15]; ccal=cal[cal.gamma_deg>=75]
        controls[domain]=(float(lcal.R_abs_log_radial.median()),float(ccal.C_abs_turns.median()))
    summary_ok = True; pair_ok = True; null_ok = True; rebuilt_joint = 0
    offsets = {"recorded_qutrit":0, "recorded_bubbles":10000, "recorded_river":20000}
    for (domain, split), part in e.groupby(["domain", "split"], sort=True):
        row = s[(s.domain==domain)&(s.split==split)].iloc[0]
        line = part[part.gamma_deg<=15]; circle = part[part.gamma_deg>=75]
        rmed = float(line.R_abs_log_radial.median()); cmed = float(circle.C_abs_turns.median())
        rw = min(RADIAL, key=lambda k: abs(rmed-math.log(RADIAL[k])))
        cw = min(ANGULAR, key=lambda k: abs(cmed-ANGULAR[k]))
        line_eligible=len(line)>=30 and int((line.radial<1-1e-12).sum())>=10 and int((line.radial>1+1e-12).sum())>=10
        circle_eligible=len(circle)>=30 and int((circle.delta<-1e-12).sum())>=10 and int((circle.delta>1e-12).sum())>=10
        line_fixed=bool(line_eligible and rw=="e" and abs(rmed-1)<=.10)
        circle_fixed=bool(circle_eligible and cw=="phi_inverse_squared" and abs(cmed-TAU)<=.05)
        line_strong=bool(line_fixed and abs(rmed-1)<=abs(rmed-controls[domain][0]))
        circle_strong=bool(circle_fixed and abs(cmed-TAU)<=abs(cmed-controls[domain][1]))
        rr = part.R_abs_log_radial.to_numpy(float); cc = part.C_abs_turns.to_numpy(float)
        candidates = []
        for rn,a in RADIAL.items():
            for cn,t in ANGULAR.items(): candidates.append((rn,cn,loss(rr,cc,a,t),loss(rr,cc,a,t,True)))
        best = min(candidates, key=lambda z:z[2]); target = next(z for z in candidates if z[0]=="e" and z[1]=="phi_inverse_squared")
        summary_ok &= bool(int(row.line_n)==len(line) and int(row.circle_n)==len(circle) and np.isclose(row.line_R_median,rmed) and np.isclose(row.circle_C_median_turns,cmed) and row.line_fixed_winner==rw and row.circle_fixed_winner==cw and bool(row.line_fixed_pass)==line_fixed and bool(row.circle_fixed_pass)==circle_fixed and bool(row.line_pass)==line_strong and bool(row.circle_pass)==circle_strong and np.isclose(row.target_linear_budget_loss,target[2]) and row.best_pair_radial==best[0] and row.best_pair_angular==best[1])
        saved_pairs = p[(p.domain==domain)&(p.split==split)].sort_values(["radial_candidate","angular_candidate"])
        calc_pairs = sorted(candidates, key=lambda z:(z[0],z[1]))
        pair_ok &= len(saved_pairs)==42 and np.allclose(saved_pairs.linear_budget_loss, [z[2] for z in calc_pairs]) and np.allclose(saved_pairs.euclidean_budget_loss, [z[3] for z in calc_pairs])
        if split != "calibration":
            saved_null = n[(n.domain==domain)&(n.split==split)].sort_values("replicate").linear_budget_loss.to_numpy(float)
            rng = np.random.default_rng(3412026+offsets[domain]+(0 if split=="evaluation" else 1))
            calc_null = np.array([loss(rr, rng.permutation(cc), math.e, TAU) for _ in range(1000)])
            null_ok &= len(saved_null)==1000 and np.allclose(saved_null,calc_null)
            pval=(1+np.count_nonzero(calc_null<=target[2]))/1001
            summary_ok &= np.isclose(row.shuffle_p,pval)
        if split=="holdout" and bool(row.joint_pass): rebuilt_joint += 1
    checks["summary_recomputed"] = bool(summary_ok)
    checks["fixed_pairs_recomputed"] = bool(pair_ok)
    checks["nulls_recomputed"] = bool(null_ok)
    checks["verdict_recomputed"] = rebuilt_joint==result["joint_holdout_domains"] and result["verdict"] == ("SUPPORTED" if rebuilt_joint>=2 else ("PARTIAL / IDENTITY-SPECIFIC" if rebuilt_joint==1 else "NOT SUPPORTED"))
    checks["finite_primary_metrics"] = bool(np.isfinite(s[["line_R_median","circle_C_median_turns","target_linear_budget_loss"]].to_numpy()).all())
    payload = {
        "test":"T341 independent validation",
        "all_pass":bool(all(checks.values())),
        "checks":checks,
        "hashes":{path.name:sha(path) for path in (EVENTS,SUMMARY,PAIRS,NULLS,SENS,FIGURE,REPORT)},
    }
    OUT.write_text(json.dumps(payload,indent=2),encoding="utf-8")
    print(json.dumps(payload,indent=2))
    if not payload["all_pass"]: raise SystemExit(1)


if __name__ == "__main__": main()
