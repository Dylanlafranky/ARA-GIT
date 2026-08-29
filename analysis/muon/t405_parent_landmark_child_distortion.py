from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys

EXTRA = Path(r"F:\SystemFormulaFolder\.codex_python_packages")
if EXTRA.exists() and str(EXTRA) not in sys.path:
    sys.path.insert(0, str(EXTRA))

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "_mplconfig"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr


OUT = ROOT / "T405_parent_landmark_child_distortion"
OUT.mkdir(exist_ok=True)
PROTOCOL = ROOT / "T405_PARENT_LANDMARK_CHILD_DISTORTION_PROTOCOL_2026-08-18.md"
INPUT = ROOT / "T400_nested_child_window_population_to_event" / "T400_REPEATED_SPLITS.csv"
SEED = 40520260818
N_PERM = 50_000


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def partial_rank_correlation(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> float:
    rx = rankdata(x)
    ry = rankdata(y)
    rz = rankdata(z)
    design = np.column_stack([np.ones(len(rz)), rz])
    ex = rx - design @ np.linalg.lstsq(design, rx, rcond=None)[0]
    ey = ry - design @ np.linalg.lstsq(design, ry, rcond=None)[0]
    if float(np.linalg.norm(ex)) < 1e-10 or float(np.linalg.norm(ey)) < 1e-10:
        return float("nan")
    return float(np.corrcoef(ex, ey)[0, 1])


data = pd.read_csv(INPUT)
valid = data[data["valid"].astype(str).str.lower() == "true"].copy()
valid["prompt_participation"] = valid["n_prompt"] / (valid["n_prompt"] + valid["n_delayed"])
valid["delayed_participation"] = 1.0 - valid["prompt_participation"]
valid["child_displacement_from_0p5"] = valid["population_local_mode"] - 0.5
valid["window_width_us"] = valid["right_time_us"] - valid["left_time_us"]
valid["crest_fraction_linear_time"] = (
    (valid["mode_time_us"] - valid["left_time_us"]) / valid["window_width_us"]
)

x = valid["prompt_participation"].to_numpy(float)
y = valid["child_displacement_from_0p5"].to_numpy(float)
rho = float(spearmanr(x, y).statistic)

rng = np.random.default_rng(SEED)
as_large = 0
permutation_rows: list[dict] = []
rank_x = rankdata(x)
rank_y = rankdata(y)
rank_x = (rank_x - rank_x.mean()) / np.linalg.norm(rank_x - rank_x.mean())
rank_y = (rank_y - rank_y.mean()) / np.linalg.norm(rank_y - rank_y.mean())
for replicate in range(N_PERM):
    score = float(np.dot(rank_x, rng.permutation(rank_y)))
    as_large += int(score >= rho - 1e-12)
    if replicate < 5000:
        permutation_rows.append({"replicate": replicate, "rho": score})
permutation_p = float((as_large + 1) / (N_PERM + 1))

loo_rows: list[dict] = []
for index, row in valid.reset_index(drop=True).iterrows():
    keep = np.ones(len(valid), dtype=bool)
    keep[index] = False
    loo_rho = float(spearmanr(x[keep], y[keep]).statistic)
    loo_rows.append({"removed_salt": int(row["salt"]), "rho": loo_rho})
loo = pd.DataFrame(loo_rows)

left = valid["left_time_us"].to_numpy(float)
rho_q_left = float(spearmanr(x, left).statistic)
rho_left_delta = float(spearmanr(left, y).statistic)
partial_rho = partial_rank_correlation(x, y, left)

diagnostic_rows = []
for field, label in (
    ("left_time_us", "left equality boundary"),
    ("window_width_us", "child-window width"),
    ("effective_delayed_holdout", "holdout effective delayed weight"),
    ("mean_delayed_weight_C", "mean delayed membership weight"),
    ("population_skewness", "population child skewness"),
):
    values = valid[field].to_numpy(float)
    diagnostic_rows.append(
        {
            "variable": label,
            "field": field,
            "rho_with_prompt_participation": float(spearmanr(x, values).statistic),
            "rho_with_child_displacement": float(spearmanr(values, y).statistic),
        }
    )
diagnostics = pd.DataFrame(diagnostic_rows)

gates = {
    "G1_at_least_15_valid_splits": bool(len(valid) >= 15),
    "G2_primary_rho_at_least_0p70": bool(rho >= 0.70),
    "G3_permutation_p_at_most_0p05": bool(permutation_p <= 0.05),
    "G4_all_LOO_positive_and_min_at_least_0p60": bool((loo["rho"] > 0).all() and loo["rho"].min() >= 0.60),
    "G5_median_child_crest_above_parent_0p5": bool(valid["population_local_mode"].median() > 0.5),
}

verdict = (
    "PARTICIPATION-DEPENDENT CHILD DISPLACEMENT REPRODUCED; STRUCTURALLY ENCODED BY THE CUT"
    if all(gates.values())
    else "PARTICIPATION-DEPENDENT CHILD DISPLACEMENT NOT FULLY SUPPORTED"
)

results = {
    "test": "T405 parent landmark versus child distortion",
    "date": "2026-08-18",
    "protocol_sha256": sha256(PROTOCOL),
    "verdict": verdict,
    "primary": {
        "valid_splits": int(len(valid)),
        "parent_reference": 0.5,
        "median_child_crest": float(valid["population_local_mode"].median()),
        "child_crest_range": valid["population_local_mode"].agg(["min", "max"]).tolist(),
        "median_displacement": float(valid["child_displacement_from_0p5"].median()),
        "prompt_participation_range": valid["prompt_participation"].agg(["min", "max"]).tolist(),
        "spearman_rho": rho,
        "permutation_draws": N_PERM,
        "permutation_as_large": int(as_large),
        "permutation_p_add_one": permutation_p,
        "loo_rho_range": loo["rho"].agg(["min", "max"]).tolist(),
    },
    "boundary_mediation_diagnostic": {
        "rho_prompt_participation_vs_left_boundary": rho_q_left,
        "rho_left_boundary_vs_displacement": rho_left_delta,
        "partial_rank_rho_prompt_vs_displacement_given_left_boundary": None if not np.isfinite(partial_rho) else partial_rho,
        "interpretation": "Prompt participation, equality-boundary position and child displacement have identical ranks here. Conditioning is non-identifiable: the boundary carries the measured participation effect and cannot supply independent evidence.",
    },
    "gates": gates,
    "boundaries": [
        "The deterministic splits overlap heavily and are not external replications.",
        "Prompt and delayed fractions are complements, not independent variables.",
        "The equality boundary is part of the coordinate construction and is a mechanism diagnostic, not a second predictor.",
        "The perfect rank relation is structurally encoded by the fitted cut and validates the coordinate response; it is not external physical confirmation.",
        "This test supports displacement tracking inside T400; it does not name a physical energy carrier or predict an individual decay.",
    ],
}

valid.to_csv(OUT / "T405_SPLIT_PARTICIPATION.csv", index=False)
loo.to_csv(OUT / "T405_LEAVE_ONE_OUT.csv", index=False)
pd.DataFrame(permutation_rows).to_csv(OUT / "T405_PERMUTATION_SAMPLE.csv", index=False)
diagnostics.to_csv(OUT / "T405_DIAGNOSTICS.csv", index=False)
(OUT / "T405_RESULTS.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

fig, axes = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=True)
ax = axes[0, 0]
ax.scatter(x, valid["population_local_mode"], color="#2563eb", s=55)
coef = np.polyfit(x, valid["population_local_mode"], 1)
grid = np.linspace(x.min(), x.max(), 100)
ax.plot(grid, np.polyval(coef, grid), color="#f59e0b", linewidth=2)
ax.axhline(0.5, color="black", linestyle="--", label="parent landmark 0.5")
ax.set(title=f"Child crest tracks branch participation (rho={rho:.3f})", xlabel="prompt participation q", ylabel="child release crest on local ARA")
ax.legend(frameon=False)

ax = axes[0, 1]
ax.scatter(x, left, color="#16a34a", s=55)
ax.set(title=f"Participation moves the equality boundary (rho={rho_q_left:.3f})", xlabel="prompt participation q", ylabel="left equality-boundary time (us)")

ax = axes[1, 0]
ax.scatter(left, y, color="#9333ea", s=55)
ax.set(title=f"Boundary position carries the displacement (rho={rho_left_delta:.3f})", xlabel="left equality-boundary time (us)", ylabel="child crest minus parent 0.5")

ax = axes[1, 1]
ax.hist(loo["rho"], bins=10, color="#4f86c6", edgecolor="white")
ax.axvline(0.60, color="black", linestyle="--", label="frozen minimum")
ax.set(title="Leave-one-split-out stability", xlabel="Spearman rho", ylabel="removed-split count")
ax.legend(frameon=False)

fig.suptitle("T405 — Parent landmark versus child distortion", fontsize=16, fontweight="bold")
fig.savefig(OUT / "T405_PARENT_LANDMARK_CHILD_DISTORTION.png", dpi=180)
plt.close(fig)

print(json.dumps(results, indent=2))
