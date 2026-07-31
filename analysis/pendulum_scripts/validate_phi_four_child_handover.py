"""Independent row-level validation of the four-child Phi handover result."""
from __future__ import annotations

import csv
import json
import math
import os

import numpy as np
from scipy.stats import spearmanr, wilcoxon


HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "phi_four_child_handover_cycles.csv")
JSON_PATH = os.path.join(HERE, "phi_four_child_handover_results.json")
PHI = (1.0 + math.sqrt(5.0)) / 2.0
U = 2.0 - PHI


def close(a: float, b: float, tol: float = 1e-12) -> bool:
    return bool(abs(float(a) - float(b)) <= tol)


def circular_distance(values: np.ndarray, points: list[float]) -> np.ndarray:
    p = np.asarray(points)
    delta = np.abs(values[:, None] - p[None, :])
    return np.min(np.minimum(delta, 1.0 - delta), axis=1)


with open(CSV_PATH, encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
with open(JSON_PATH, encoding="utf-8") as handle:
    saved = json.load(handle)

checks: list[dict] = []
recomputed: dict = {}

for split in ("development", "frozen"):
    rr = [row for row in rows if row["split"] == split]
    summary = saved[split]
    completions = np.array(
        [
            float(row["completion_u"])
            for row in rr
            if row["all_four_seen"] == "True"
        ]
    )
    valid_retention = rr[:-1]
    retention = np.array([float(row["parent_retention"]) for row in valid_retention])

    values = {
        "n_cycles": len(rr),
        "all_four_seen_n": sum(row["all_four_seen"] == "True" for row in rr),
        "median_AA": float(np.median([float(row["p_AA"]) for row in rr])),
        "median_AB": float(np.median([float(row["p_AB"]) for row in rr])),
        "median_BB": float(np.median([float(row["p_BB"]) for row in rr])),
        "median_BA": float(np.median([float(row["p_BA"]) for row in rr])),
        "phi_template": float(
            np.median([float(row["phi_template_distance"]) for row in rr])
        ),
        "equal_template": float(
            np.median([float(row["equal_template_distance"]) for row in rr])
        ),
        "paired_template": float(
            np.median([float(row["paired_template_distance"]) for row in rr])
        ),
        "linear_template": float(
            np.median([float(row["linear_template_distance"]) for row in rr])
        ),
        "completion_phi": float(
            np.median(circular_distance(completions, [U, 1.0 - U]))
        ),
        "completion_poles": float(
            np.median(circular_distance(completions, [0.0]))
        ),
        "completion_ridge": float(
            np.median(circular_distance(completions, [0.5]))
        ),
        "completion_quarters": float(
            np.median(circular_distance(completions, [0.25, 0.75]))
        ),
        "completion_thirds": float(
            np.median(circular_distance(completions, [1.0 / 3.0, 2.0 / 3.0]))
        ),
        "inequality_median": float(
            np.median([float(row["inequality"]) for row in rr])
        ),
        "retention_median": float(np.nanmedian(retention)),
        "inequality_r": float(
            spearmanr(
                [float(row["inequality"]) for row in valid_retention], retention
            ).statistic
        ),
        "phi_retention_r": float(
            spearmanr(
                [
                    1.0 - float(row["phi_template_distance"])
                    for row in valid_retention
                ],
                retention,
            ).statistic
        ),
    }
    recomputed[split] = values

    targets = {
        "n_cycles": summary["n_cycles"],
        "all_four_seen_n": summary["all_four_seen_n"],
        "median_AA": summary["median_child_shares"]["AA"],
        "median_AB": summary["median_child_shares"]["AB"],
        "median_BB": summary["median_child_shares"]["BB"],
        "median_BA": summary["median_child_shares"]["BA"],
        "phi_template": summary["template_median_total_variation_distance"][
            "phi_quartet"
        ],
        "equal_template": summary["template_median_total_variation_distance"][
            "equal_quarters"
        ],
        "paired_template": summary["template_median_total_variation_distance"][
            "paired_dyadic"
        ],
        "linear_template": summary["template_median_total_variation_distance"][
            "linear_irregular"
        ],
        "completion_phi": summary[
            "completion_landmark_median_circular_distance"
        ]["phi"],
        "completion_poles": summary[
            "completion_landmark_median_circular_distance"
        ]["poles"],
        "completion_ridge": summary[
            "completion_landmark_median_circular_distance"
        ]["ridge_opposition"],
        "completion_quarters": summary[
            "completion_landmark_median_circular_distance"
        ]["quarters"],
        "completion_thirds": summary[
            "completion_landmark_median_circular_distance"
        ]["thirds"],
        "inequality_median": summary["inequality_median"],
        "retention_median": summary["parent_retention_median"],
        "inequality_r": summary["inequality_to_parent_retention"]["spearman_r"],
        "phi_retention_r": summary["phi_proximity_to_parent_retention"][
            "spearman_r"
        ],
    }
    for name, target in targets.items():
        actual = values[name]
        passed = actual == target if isinstance(target, int) else close(actual, target)
        checks.append(
            {
                "check": f"{split}:{name}",
                "passed": passed,
                "actual": actual,
                "saved": target,
            }
        )

# Post-verdict specificity diagnostics on the frozen rows.
frozen = [row for row in rows if row["split"] == "frozen"]
scored = frozen[:-1]
retention = np.array([float(row["parent_retention"]) for row in scored])
template_correlations = {}
for label, column in {
    "phi": "phi_template_distance",
    "equal": "equal_template_distance",
    "paired": "paired_template_distance",
    "linear": "linear_template_distance",
}.items():
    proximity = np.array([1.0 - float(row[column]) for row in scored])
    template_correlations[label] = float(
        spearmanr(proximity, retention).statistic
    )

completion = np.array(
    [
        float(row["completion_u"])
        for row in frozen
        if row["all_four_seen"] == "True"
    ]
)
d_phi = circular_distance(completion, [U, 1.0 - U])
d_thirds = circular_distance(completion, [1.0 / 3.0, 2.0 / 3.0])
paired_test = wilcoxon(d_phi, d_thirds, alternative="less")
rng = np.random.default_rng(20260730)
bootstrap = np.empty(20000)
for i in range(len(bootstrap)):
    indices = rng.integers(0, len(completion), len(completion))
    bootstrap[i] = np.median(d_phi[indices]) - np.median(d_thirds[indices])

output = {
    "validator": "validate_phi_four_child_handover.py",
    "row_count": len(rows),
    "checks": len(checks),
    "failures": sum(not check["passed"] for check in checks),
    "recomputed": recomputed,
    "post_verdict_specificity": {
        "template_proximity_to_parent_retention_spearman": template_correlations,
        "completion_phi_vs_thirds": {
            "n": len(completion),
            "phi_better_count": int(np.sum(d_phi < d_thirds)),
            "thirds_better_count": int(np.sum(d_thirds < d_phi)),
            "paired_wilcoxon_one_sided_p": float(paired_test.pvalue),
            "bootstrap_median_difference_phi_minus_thirds_q025_q50_q975": [
                float(value)
                for value in np.quantile(bootstrap, [0.025, 0.5, 0.975])
            ],
        },
    },
    "saved_verdict": saved["verdict"],
}
with open(
    os.path.join(HERE, "phi_four_child_handover_validation.json"),
    "w",
    encoding="utf-8",
) as handle:
    json.dump(output, handle, indent=2)
print(json.dumps(output, indent=2))
if output["failures"]:
    raise SystemExit(1)
