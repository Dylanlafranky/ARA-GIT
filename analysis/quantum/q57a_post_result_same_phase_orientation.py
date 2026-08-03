from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "Q57_QUANTUM_SAME_PHASE_GOLDEN_SECTION_SEEDS.csv"
OUTPUT_CSV = ROOT / "Q57A_POST_RESULT_SAME_PHASE_ORIENTATION_SEEDS.csv"
OUTPUT_JSON = ROOT / "Q57A_POST_RESULT_SAME_PHASE_ORIENTATION_RESULTS.json"
OUTPUT_PNG = ROOT / "Q57A_POST_RESULT_SAME_PHASE_ORIENTATION.png"
PHI = (1 + math.sqrt(5)) / 2
LANDMARKS = {
    "sqrt2": math.sqrt(2),
    "1.5": 1.5,
    "phi": PHI,
    "sqrt3": math.sqrt(3),
    "2": 2.0,
}
BOOTSTRAPS = 10_000
RNG_SEED = 570032


def nearest(value: float) -> tuple[str, float]:
    name = min(LANDMARKS, key=lambda key: abs(value - LANDMARKS[key]))
    return name, abs(value - LANDMARKS[name])


def main() -> None:
    rows = []
    with SOURCE.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            g_a = float(row["P_A"]) + 0.5 * float(row["C_A"])
            g_b = float(row["P_B"]) + 0.5 * float(row["C_B"])
            rows.append(
                {
                    "archive": row["archive"],
                    "seed": int(row["seed"]),
                    "g_A_same_phase": g_a,
                    "g_B_same_phase": g_b,
                    "sum_forced": g_a + g_b,
                    "distance_A_to_phi": abs(g_a - PHI),
                    "distance_B_to_phi": abs(g_b - PHI),
                }
            )

    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    rng = np.random.default_rng(RNG_SEED)
    summary = {}
    for archive in sorted({row["archive"] for row in rows}):
        selected = [row for row in rows if row["archive"] == archive]
        summary[archive] = {"n_seeds": len(selected), "metrics": {}}
        for field in ("g_A_same_phase", "g_B_same_phase"):
            values = np.array([row[field] for row in selected])
            draws = rng.integers(0, len(values), size=(BOOTSTRAPS, len(values)))
            boot = np.median(values[draws], axis=1)
            median = float(np.median(values))
            landmark, distance = nearest(median)
            summary[archive]["metrics"][field] = {
                "median": median,
                "bootstrap_95_ci_median": [
                    float(np.quantile(boot, 0.025)),
                    float(np.quantile(boot, 0.975)),
                ],
                "nearest_landmark": landmark,
                "nearest_landmark_distance": distance,
                "distance_to_phi": abs(median - PHI),
            }

    max_sum_error = max(abs(row["sum_forced"] - 3) for row in rows)
    results = {
        "test_id": "Q57A",
        "status": "POST-RESULT ORIENTATION CORRECTION",
        "formula": {
            "AA": "P_A + 0.5*C_A",
            "BB": "P_B + 0.5*C_B",
            "forced_sum": "g_A + g_B = 3",
        },
        "phi": PHI,
        "summary": summary,
        "max_forced_sum_error": max_sum_error,
        "files": {"seed_csv": str(OUTPUT_CSV), "figure_png": str(OUTPUT_PNG)},
    }
    OUTPUT_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(9.5, 7.2))
    colors = {"greedy": "#3b74b9", "landmax": "#d78c29"}
    for archive in sorted(colors):
        selected = [row for row in rows if row["archive"] == archive]
        ax.scatter(
            [row["g_A_same_phase"] for row in selected],
            [row["g_B_same_phase"] for row in selected],
            s=34,
            alpha=0.6,
            label=archive,
            color=colors[archive],
        )
    ax.plot([1.2, 1.8], [1.8, 1.2], color="#666", lw=1.5, label="forced gA+gB=3")
    ax.axvline(PHI, color="#8e44ad", lw=2, ls="--", label="phi")
    ax.axhline(PHI, color="#8e44ad", lw=2, ls="--")
    ax.axvline(1.5, color="#26734d", lw=1.5, ls=":", label="1.5")
    ax.axhline(1.5, color="#26734d", lw=1.5, ls=":")
    ax.set(
        xlabel="AA = parent Phase A + half-weight child Phase A",
        ylabel="BB = parent Phase B + half-weight child Phase B",
        title="Q57A — corrected additive same-phase orientation",
    )
    ax.legend(frameon=True)
    fig.tight_layout()
    fig.savefig(OUTPUT_PNG, dpi=180)
    plt.close(fig)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
