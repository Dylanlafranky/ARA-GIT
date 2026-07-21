"""Independent arithmetic and artifact validation for PN10C."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np

from pn10b_child_phase_prime_ranking import segmented_least_prime_factor


ROOT = Path(__file__).resolve().parent
LOW, HIGH, WINDOW = 4_000_000_000, 4_001_000_000, 150
OUT = ROOT / "PN10C_MOD6_THREE_LANE_VALIDATION.json"


def load_csv(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def close(a: float, b: float, tolerance: float = 1e-10) -> bool:
    return abs(a - b) <= tolerance


def main() -> None:
    result = json.loads((ROOT / "PN10C_MOD6_THREE_LANE_RESULTS.json").read_text(encoding="utf-8"))
    offsets = load_csv("PN10C_MOD6_OFFSET_PROFILE.csv")
    lanes = load_csv("PN10C_MOD6_LANE_SUMMARY.csv")
    matrix = load_csv("PN10C_MOD30_BLACK_CHILD_MATRIX.csv")
    examples = load_csv("PN10C_MOD6_WORKED_EXAMPLES.csv")

    numbers, lpf = segmented_least_prime_factor(LOW, HIGH)
    is_prime = lpf == 0
    parent = np.empty(len(numbers), dtype=float)
    parent[is_prime] = 1.0
    composite = ~is_prime
    parent[composite] = 2*np.log(lpf[composite].astype(float))/np.log(numbers[composite].astype(float))
    interior = np.arange(WINDOW, len(numbers)-WINDOW)
    prime_idx = interior[is_prime[interior]]

    checks: list[dict] = []
    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"check":name,"passed":bool(passed),"detail":detail})

    check("status_is_post_hoc", result["status"] == "post_hoc_structural_diagnostic", result["status"])
    check("pn10b_verdict_unchanged", result["registered_pn10b_verdict_unchanged"] == "NULL", str(result["registered_pn10b_verdict_unchanged"]))
    check("interior_prime_count", int(result["scope"]["interior_prime_count"]) == len(prime_idx), f"saved={result['scope']['interior_prime_count']}; recomputed={len(prime_idx)}")

    # Recompute every prime offset profile directly.
    max_error = 0.0
    for row in offsets:
        if row["center_group"] != "prime":
            continue
        residue, offset = int(row["center_mod6"]), int(row["offset"])
        centers = prime_idx[numbers[prime_idx] % 6 == residue]
        observed = float(np.mean(parent[centers + offset]))
        max_error = max(max_error, abs(observed-float(row["parent_progress_mean"])))
    check("offset_profiles_recomputed", max_error < 1e-12, f"maximum absolute error={max_error:.3g}")

    lane_lookup={(int(r["center_mod6"]),int(r["offset_lane_mod6"])):float(r["parent_progress_mean"])
                 for r in lanes if r["center_group"]=="prime" and r["direction"]=="all"}
    swap=.5*((lane_lookup[(1,4)]-lane_lookup[(1,2)])+(lane_lookup[(5,2)]-lane_lookup[(5,4)]))
    saved_swap=float(result["headline_contrasts"]["red_blue_swap"]["estimate"])
    check("red_blue_swap_recomputed", close(swap,saved_swap),f"saved={saved_swap:.12f}; recomputed={swap:.12f}")
    check("red_blue_swap_ci_excludes_zero", float(result["headline_contrasts"]["red_blue_swap"]["ci95_low"])>0, str(result["headline_contrasts"]["red_blue_swap"]))

    black_diff=lane_lookup[(1,0)]-lane_lookup[(5,0)]
    saved_black=float(result["headline_contrasts"]["black_orientation_difference"]["estimate"])
    check("black_difference_recomputed",close(black_diff,saved_black),f"saved={saved_black:.12f}; recomputed={black_diff:.12f}")
    bci=result["headline_contrasts"]["black_orientation_difference"]
    check("black_invariance_ci_contains_zero",float(bci["ci95_low"])<=0<=float(bci["ci95_high"]),str(bci))

    third=.5*((lane_lookup[(1,0)]-lane_lookup[(1,4)])+(lane_lookup[(5,0)]-lane_lookup[(5,2)]))
    saved_third=float(result["headline_contrasts"]["black_minus_admissible_colour"]["estimate"])
    check("third_lane_discriminator_recomputed",close(third,saved_third),f"saved={saved_third:.12f}; recomputed={third:.12f}")
    check("black_not_above_admissible_colour",float(result["headline_contrasts"]["black_minus_admissible_colour"]["ci95_high"])<0,str(result["headline_contrasts"]["black_minus_admissible_colour"]))

    prof={(int(r["center_mod6"]),int(r["offset"])):float(r["parent_progress_mean"]) for r in offsets if r["center_group"]=="prime"}
    reflected=np.mean([abs(prof[(1,k)]-prof[(5,-k)]) for k in range(-WINDOW,WINDOW+1)])
    direct=np.mean([abs(prof[(1,k)]-prof[(5,k)]) for k in range(-WINDOW,WINDOW+1)])
    check("reflection_recomputed",close(reflected,float(result["reflection_test"]["mean_absolute_error_reflected"])) and close(direct,float(result["reflection_test"]["mean_absolute_error_direct"])),f"reflected={reflected:.12f}; direct={direct:.12f}")
    check("reflection_improves_alignment",reflected<direct/100,f"reflected/direct={reflected/direct:.6f}")

    matrix_prime=[r for r in matrix if r["center_group"]=="prime"]
    rotating=True
    q5_values=[]
    eligible_values=[]
    for row in matrix_prime:
        p5,m=int(row["center_mod5"]),int(row["black_child_m_mod5"])
        predicted=int(row["predicted_factor5_collision"])==1
        exact=((p5+m)%5==0)
        rate=float(row["divisible_by_5_rate"])
        rotating &= predicted==exact and close(rate,1.0 if exact else 0.0)
        (q5_values if exact else eligible_values).append(float(row["parent_progress_mean"]))
    check("mod30_rotating_factor5_identity",rotating,"each centre-mod5 row has the predicted rotating factor-5 collision")
    expected=float(np.mean(2*math.log(5)/np.log(numbers[prime_idx].astype(float))))
    observed=float(result["mechanism_checks"]["observed_suppressed_parent_progress"])
    check("factor5_trough_value",abs(expected-observed)<1e-9,f"expected={expected:.12f}; observed={observed:.12f}")
    check("mod30_contrast_ci_excludes_zero",float(result["headline_contrasts"]["mod30_eligible_minus_suppressed"]["ci95_low"])>0,str(result["headline_contrasts"]["mod30_eligible_minus_suppressed"]))

    example_ok=True
    for row in examples:
        n=int(row["n"]); idx=n-LOW
        example_ok &= int(row["least_prime_factor"])==int(lpf[idx])
        example_ok &= int(row["is_prime"])==int(is_prime[idx])
        example_ok &= close(float(row["parent_progress"]),float(parent[idx]))
    check("worked_examples_trace_raw_values",example_ok,f"rows={len(examples)}")

    fig=ROOT/"PN10C_MOD6_THREE_LANE_FIGURE.png"
    check("figure_present",fig.exists() and fig.stat().st_size>50_000,f"bytes={fig.stat().st_size if fig.exists() else 0}")

    passed=sum(int(c["passed"]) for c in checks)
    payload={
        "status":"PASS" if passed==len(checks) else "FAIL",
        "checks_passed":passed,"checks_total":len(checks),"checks":checks,
        "validation_boundary":"Arithmetic and artifact consistency only; it does not promote the post-hoc result to prospective evidence.",
    }
    OUT.write_text(json.dumps(payload,indent=2),encoding="utf-8")
    print(json.dumps(payload,indent=2))
    if payload["status"]!="PASS": raise SystemExit(1)


if __name__=="__main__":
    main()
