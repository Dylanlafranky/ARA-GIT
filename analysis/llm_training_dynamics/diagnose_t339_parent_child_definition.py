#!/usr/bin/env python3
"""Post-result T339 diagnostic: total-child versus child-specific flow.

This does not alter the frozen T339 verdict. It tests the exact algebraic
reconciliation implied when a measured layer flow already contains its model
parent's common flow.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent


def main() -> None:
    pred = pd.read_csv(HERE / "T339_PREDICTIONS.csv.gz")
    base = pred[pred.predictor == "ara_corrected"].reset_index(drop=True)
    equal = pred[pred.predictor == "equal_average_t338"].reset_index(drop=True)

    parent = base.parent_flow_input.to_numpy()
    child_total = base.child_flow_input.to_numpy()
    child_specific = child_total - parent
    dt = base.delta_tau.to_numpy()

    # Dylan's stated 1 parent + 0.5 child rule, with child defined as the
    # lower-rung identity remaining after removing the inherited parent mode.
    residual_rule_delta = (parent + 0.5 * child_specific) * dt
    equal_average_delta = equal.pred_delta.to_numpy()

    by_split_stream: list[dict] = []
    for (split, stream), g in base.groupby(["split", "stream"]):
        p = g.parent_flow_input.to_numpy()
        c = g.child_flow_input.to_numpy()
        r = c - p
        by_split_stream.append({
            "split": split,
            "stream": stream,
            "n": int(len(g)),
            "parent_child_pearson": float(np.corrcoef(p, c)[0, 1]),
            "parent_child_same_sign_rate": float(np.mean(np.sign(p) == np.sign(c))),
            "mean_abs_parent_flow": float(np.mean(np.abs(p))),
            "mean_abs_total_child_flow": float(np.mean(np.abs(c))),
            "mean_abs_child_specific_residual": float(np.mean(np.abs(r))),
        })

    result = {
        "status": "POST-RESULT ALGEBRAIC RECONCILIATION; DOES NOT ALTER T339 VERDICT",
        "definitions": {
            "measured_layer_flow": "C_total",
            "parent_common_flow": "P",
            "child_specific_flow": "C_specific = C_total - P",
            "user_rule": "P + 0.5*C_specific",
            "expanded_rule": "0.5*P + 0.5*C_total",
        },
        "max_abs_delta_difference_vs_t338_equal_average": float(
            np.max(np.abs(residual_rule_delta - equal_average_delta))
        ),
        "mean_abs_delta_difference_vs_t338_equal_average": float(
            np.mean(np.abs(residual_rule_delta - equal_average_delta))
        ),
        "exact_within_1e_12": bool(
            np.allclose(residual_rule_delta, equal_average_delta, rtol=0, atol=1e-12)
        ),
        "by_split_stream": by_split_stream,
    }
    (HERE / "T339_PARENT_CHILD_DEFINITION_DIAGNOSTIC.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

