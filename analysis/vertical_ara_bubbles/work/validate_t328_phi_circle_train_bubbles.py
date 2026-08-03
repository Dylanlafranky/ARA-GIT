#!/usr/bin/env python3
"""Independent QA for the frozen T328 bubble circle-train result."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

import run_t328_phi_circle_train_bubbles as t328


HERE = Path(__file__).resolve().parents[1]
PREFIX = t328.PREFIX
TOL = 1e-12


def close(left: float, right: float, tolerance: float = TOL) -> bool:
    return math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=tolerance)


def main() -> None:
    saved = json.loads((HERE / f"{PREFIX}_RESULTS.json").read_text(encoding="utf-8"))
    roots, diagnostics = t328.extract_roots()
    scores, _ = t328.score_roots(roots)
    candidate_summary, _ = t328.candidate_summary(scores)
    resolution = t328.resolution_audit(roots)

    checks: list[dict] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        checks.append({"name": name, "passed": bool(condition), "detail": detail})

    check("operator_exact", close(t328.PHI_DELTA, 2.0 / t328.PHI))
    check("protocol_hash", saved["protocol_sha256"] == t328.sha256(t328.PROTOCOL))
    check(
        "source_hash",
        saved["source_aggregate_sha256"] == t328.source_sha256(list(t328.SOURCE.glob("*.csv"))),
    )
    check("diagnostics_exact", saved["diagnostics"] == diagnostics)
    check("heading_range", all(np.all((root.headings >= 0.0) & (root.headings < 2.0)) for root in roots))
    check("all_steps_above_threshold", all(np.all(np.linalg.norm(root.steps, axis=1) >= t328.MIN_STEP_M) for root in roots))

    for split in ("calibration", "evaluation", "holdout"):
        for winner_field in (
            "winner_local_directed_mean",
            "winner_parent_directed_mean",
            "winner_return_mae_mean",
        ):
            check(
                f"{split}_{winner_field}",
                saved["candidate_summary"][split][winner_field] == candidate_summary[split][winner_field],
            )
        for candidate in t328.CANDIDATES:
            for field in ("local_directed_mean", "parent_directed_mean", "return_mae_mean"):
                check(
                    f"{split}_{candidate}_{field}",
                    close(
                        saved["candidate_summary"][split][candidate][field],
                        candidate_summary[split][candidate][field],
                    ),
                )

    with (HERE / "results" / f"{PREFIX}_ROOT_SCORES.csv").open("r", newline="", encoding="utf-8") as handle:
        stored_rows = list(csv.DictReader(handle))
    stored_index = {
        (row["split"], row["video"], int(row["track_id"]), int(row["start_frame"]), row["candidate"]): row
        for row in stored_rows
    }
    root_samples = roots[:: max(1, len(roots) // 12)][:12]
    maximum_spot_error = 0.0
    for root in root_samples:
        for candidate in ("persistence", "phi", "fibonacci_8_21"):
            calculated = t328.score_heading_path(root.headings, t328.CANDIDATES[candidate])
            calculated["return_mae"] = t328.return_loss(root.headings, t328.CANDIDATES[candidate])[0]
            stored = stored_index[(root.split, root.video, root.track_id, root.start_frame, candidate)]
            for field in ("local_directed", "parent_directed", "local_reversible", "parent_reversible", "return_mae"):
                maximum_spot_error = max(maximum_spot_error, abs(float(stored[field]) - float(calculated[field])))
    check("raw_root_spot_checks", maximum_spot_error <= TOL, f"maximum error {maximum_spot_error}")

    nulls = np.load(HERE / "results" / f"{PREFIX}_SHUFFLE_NULLS.npz")
    for split in ("evaluation", "holdout"):
        values = np.asarray(nulls[split], dtype=float)
        observed = float(saved["shuffle"][split]["observed_mean"])
        recomputed_p = float((1 + np.sum(values <= observed)) / (len(values) + 1))
        check(f"{split}_shuffle_draw_count", len(values) == t328.N_NULL)
        check(f"{split}_shuffle_p", close(recomputed_p, saved["shuffle"][split]["p_lower"]))
        check(f"{split}_shuffle_median", close(float(np.median(values)), saved["shuffle"][split]["null_median"]))

    check("resolution_exact", all(
        close(saved["resolution"][field], resolution[field])
        for field in ("pixel_scale_m", "median_heading_grain_ara", "one_step_separation_ara")
    ))
    check("nearest_candidate", saved["resolution"]["nearest_fixed_candidate"] == resolution["nearest_fixed_candidate"])
    check("first_resolved_horizon", saved["resolution"]["first_resolved_horizon"] == resolution["first_resolved_horizon"])

    image = Image.open(HERE / f"{PREFIX}_FIGURE.png")
    check("figure_dimensions", image.size == (1900, 1250), str(image.size))

    # Post-result sensitivity audit: the frozen gate only required a return
    # winner. These intervals show whether that winner is distinct from each
    # rival under the same video-cluster grain. They do not alter the verdict.
    score_index = {
        (row["split"], row["video"], row["track_id"], row["start_frame"], row["candidate"]): row
        for row in scores
    }
    return_sensitivity: dict[str, dict] = {}
    for split_index, split in enumerate(("evaluation", "holdout")):
        phi_rows = [row for row in scores if row["split"] == split and row["candidate"] == "phi"]
        return_sensitivity[split] = {}
        for candidate_index, candidate in enumerate(t328.CANDIDATES):
            if candidate == "phi":
                continue
            records = []
            for row in phi_rows:
                rival = score_index[(split, row["video"], row["track_id"], row["start_frame"], candidate)]
                records.append((row["video"], float(row["return_mae"]) - float(rival["return_mae"])))
            return_sensitivity[split][candidate] = t328.cluster_bootstrap_difference(
                records, 800 + split_index * 20 + candidate_index
            )

    observed_return_shape: dict[str, list[dict]] = {}
    for split in ("evaluation", "holdout"):
        split_roots = [root for root in roots if root.split == split]
        observed_return_shape[split] = []
        for lag in range(1, 22):
            mean_return = float(np.mean([
                np.median(t328.d2(root.headings[lag:], root.headings[:-lag]))
                for root in split_roots
            ]))
            observed_return_shape[split].append({"lag": lag, "mean_return_ara": mean_return})

    validation = {
        "test_id": saved["test_id"],
        "status": "PASS" if all(item["passed"] for item in checks) else "FAIL",
        "checks_passed": sum(item["passed"] for item in checks),
        "checks_total": len(checks),
        "maximum_raw_root_spot_error": maximum_spot_error,
        "checks": checks,
        "post_result_return_sensitivity_not_a_frozen_gate": return_sensitivity,
        "post_result_observed_return_shape_not_a_frozen_gate": observed_return_shape,
    }
    output = HERE / f"{PREFIX}_VALIDATION.json"
    output.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    eval_fib = return_sensitivity["evaluation"]["fibonacci_8_21"]
    hold_fib = return_sensitivity["holdout"]["fibonacci_8_21"]
    eval_persist = return_sensitivity["evaluation"]["persistence"]
    hold_persist = return_sensitivity["holdout"]["persistence"]
    eval_shape = {row["lag"]: row["mean_return_ara"] for row in observed_return_shape["evaluation"]}
    hold_shape = {row["lag"]: row["mean_return_ara"] for row in observed_return_shape["holdout"]}
    audit = f"""# T328 post-result return sensitivity audit

**Date:** 2 August 2026  
**Status:** validation-only; not a frozen verdict gate

The frozen test asked which candidate had the lowest mean Fibonacci-return
error. After that result was known, this audit applied the existing
whole-video cluster bootstrap to the paired return differences.

| Comparison (Phi minus rival) | Evaluation mean | Evaluation 95% | Holdout mean | Holdout 95% |
|---|---:|---:|---:|---:|
| `8/21` | {eval_fib['mean']:.6f} | {eval_fib['ci_low']:.6f} to {eval_fib['ci_high']:.6f} | {hold_fib['mean']:.6f} | {hold_fib['ci_low']:.6f} to {hold_fib['ci_high']:.6f} |
| persistence | {eval_persist['mean']:.6f} | {eval_persist['ci_low']:.6f} to {eval_persist['ci_high']:.6f} | {hold_persist['mean']:.6f} | {hold_persist['ci_low']:.6f} to {hold_persist['ci_high']:.6f} |

Negative values favour Phi. Phi is a stable numerical return winner over
`8/21`, but its intervals against persistence cross zero. Combined with the
failed directional-resolution gate, this audit does not establish exact-Phi
recovery and does not change the frozen `PARTIAL / MIXED` verdict.

## Shape check across every lag 1-21

The ideal Phi carrier predicts return distances `{float(t328.d2(0, 2*t328.PHI_DELTA)):.6f}`,
`{float(t328.d2(0, 3*t328.PHI_DELTA)):.6f}`, `{float(t328.d2(0, 5*t328.PHI_DELTA)):.6f}`,
`{float(t328.d2(0, 8*t328.PHI_DELTA)):.6f}`, `{float(t328.d2(0, 13*t328.PHI_DELTA)):.6f}` and
`{float(t328.d2(0, 21*t328.PHI_DELTA)):.6f}` at the registered Fibonacci lags.
Those values shrink toward zero.

The observed evaluation means at those lags were
`{eval_shape[2]:.6f}, {eval_shape[3]:.6f}, {eval_shape[5]:.6f}, {eval_shape[8]:.6f},
{eval_shape[13]:.6f}, {eval_shape[21]:.6f}`; holdout was
`{hold_shape[2]:.6f}, {hold_shape[3]:.6f}, {hold_shape[5]:.6f}, {hold_shape[8]:.6f},
{hold_shape[13]:.6f}, {hold_shape[21]:.6f}`. Evaluation's smallest nontrivial
return over all lags `2..21` occurred at lag `2`; holdout's occurred at lag
`3`. There is no observed concentration of near-returns at the larger
Fibonacci lags. Thus "Phi won the frozen return MAE" is a template-ranking
fact, not evidence that the bubbles visibly executed Fibonacci near-closures.
"""
    (HERE / f"{PREFIX}_POST_RESULT_RETURN_AUDIT_2026-08-02.md").write_text(audit, encoding="utf-8")
    print(json.dumps(validation, indent=2))
    if validation["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
