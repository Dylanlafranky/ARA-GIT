"""T375: frozen nested energy-resolution test inside one liquid-argon parent."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".mplcache"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import brentq, minimize_scalar
from scipy.stats import spearmanr

from t373_argon_child_half_transfer import (
    decompose_signal,
    fit_fixed,
    fit_free,
    handover,
    load_cube,
    normalize,
    timing_bases,
)


HERE = Path(__file__).resolve().parent
TARGET_X = 1.25
TARGET_SHARE = 0.5032314472084726
PROFILE_GATE = 1.920729410347062
SEED = 375

GROUPS = {
    1: [list(range(12))],
    2: [[0], list(range(1, 12))],
    3: [[0], [1], list(range(2, 12))],
    5: [[0], [1], [2], [3], list(range(4, 12))],
    12: [[i] for i in range(12)],
}


def group_energy(cube: np.ndarray, groups: list[list[int]]) -> np.ndarray:
    return np.stack([cube[idx].sum(axis=0) for idx in groups], axis=0)


def x_from_share(
    share: float, times: np.ndarray, p_shape: np.ndarray, d_shape: np.ndarray
) -> tuple[float, float]:
    return handover(times, share * p_shape, (1.0 - share) * d_shape)


def profile_arrays(
    y: np.ndarray,
    templates: list[np.ndarray],
    times: np.ndarray,
    p_shape: np.ndarray,
    d_shape: np.ndarray,
) -> dict:
    shares = np.linspace(0.001, 0.999, 301)
    nll = np.asarray([fit_fixed(y, templates, float(s))["nll"] for s in shares])
    i_min = int(np.nanargmin(nll))
    left = float(shares[max(0, i_min - 1)])
    right = float(shares[min(len(shares) - 1, i_min + 1)])
    refined = minimize_scalar(
        lambda s: fit_fixed(y, templates, float(s))["nll"],
        bounds=(left, right), method="bounded", options={"xatol": 1e-8},
    )
    candidates = [
        (float(shares[i_min]), fit_fixed(y, templates, float(shares[i_min]))),
        (float(refined.x), fit_fixed(y, templates, float(refined.x))),
    ]
    share, best = min(candidates, key=lambda item: item[1]["nll"])
    t_h, x_h = x_from_share(share, times, p_shape, d_shape)
    target = fit_fixed(y, templates, TARGET_SHARE)
    delta = nll - float(best["nll"])
    xs = np.asarray([x_from_share(float(s), times, p_shape, d_shape)[1] for s in shares])
    ok = np.isfinite(xs) & (delta <= PROFILE_GATE)
    return {
        "fit_success": bool(best["success"]),
        "nll": float(best["nll"]),
        "prompt_share": share,
        "handover_time_us": t_h,
        "handover_x": x_h,
        "distance_to_1_25": abs(x_h - TARGET_X),
        "delta_nll_at_1_25": float(max(0.0, target["nll"] - best["nll"])),
        "target_compatible": bool(target["nll"] - best["nll"] <= PROFILE_GATE),
        "profile_95_x": [float(np.min(xs[ok])), float(np.max(xs[ok]))] if np.any(ok) else [None, None],
        "profile_grid": {
            "share": shares.tolist(),
            "x": [None if not np.isfinite(v) else float(v) for v in xs],
            "delta_nll": delta.tolist(),
        },
    }


def robust_fit_free(y: np.ndarray, templates: list[np.ndarray]) -> dict:
    fits = []
    for share in (0.01, 0.10, 0.25, 0.50, 0.75, 0.90, 0.99):
        total = 160.0
        start = np.asarray([share * total, (1.0 - share) * total, 497.0, 33.0, 3154.0])
        fits.append(fit_free(y, templates, start=start))
    return min(fits, key=lambda item: item["nll"])


def make_permutations(g: int, rng: np.random.Generator) -> list[tuple[str, np.ndarray]]:
    identity = np.arange(g)
    out = [("reversed", identity[::-1].copy())]
    for i in range(20):
        p = rng.permutation(g)
        while np.array_equal(p, identity):
            p = rng.permutation(g)
        out.append((f"random_{i + 1:02d}", p.copy()))
    return out


def main() -> None:
    energies, f90s, times, y_cube = load_cube("datanobkgsub.txt")
    _, _, _, signal_cube = load_cube("cevnspdf.txt")
    _, _, _, brn_cube = load_cube("brnpdf.txt")
    _, _, _, dbrn_cube = load_cube("delbrnpdf.txt")
    _, _, _, ss_cube = load_cube("bkgpdf.txt")

    p_time, d_time = timing_bases(times)
    split = decompose_signal(signal_cube, p_time, d_time)
    components = [split["prompt"], split["delayed"], brn_cube, dbrn_cube, ss_cube]
    p_shape = split["prompt"].sum(axis=(0, 1)); p_shape /= p_shape.sum()
    d_shape = split["delayed"].sum(axis=(0, 1)); d_shape /= d_shape.sum()

    ladder = {}
    grouped_cache = {}
    for g, groups in GROUPS.items():
        gy = group_energy(y_cube, groups)
        gc = [group_energy(c, groups) for c in components]
        templates = [normalize(c).ravel() for c in gc]
        ladder[str(g)] = profile_arrays(gy.ravel(), templates, times, p_shape, d_shape)
        grouped_cache[g] = (gy, gc)

    levels = np.asarray(list(GROUPS), dtype=float)
    distances = np.asarray([ladder[str(int(g))]["distance_to_1_25"] for g in levels])
    rho = float(spearmanr(levels, distances).statistic)
    successive_improvements = int(np.sum(np.diff(distances) < 0))
    intermediate_same_side = all(ladder[str(g)]["handover_x"] >= 1.0 for g in (2, 3, 5))
    finite_all = bool(np.all(np.isfinite([ladder[str(int(g))]["handover_x"] for g in levels])))
    primary_pass = bool(finite_all and rho <= -0.80 and successive_improvements >= 3 and intermediate_same_side)

    rng = np.random.default_rng(SEED)
    controls = {}
    for g in (3, 5, 12):
        gy, gc = grouped_cache[g]
        y = gy.ravel()
        native_nll = ladder[str(g)]["nll"]
        rows = []
        for label, perm in make_permutations(g, rng):
            pc = [gc[0][perm], gc[1][perm], gc[2], gc[3], gc[4]]
            fit = robust_fit_free(y, [normalize(c).ravel() for c in pc])
            rows.append({
                "label": label,
                "permutation": perm.tolist(),
                "nll": float(fit["nll"]),
                "permuted_minus_native_nll": float(fit["nll"] - native_nll),
                "fit_success": bool(fit["success"]),
            })
        perm_nll = np.asarray([row["nll"] for row in rows])
        rank = int(np.sum(np.r_[native_nll, perm_nll] < native_nll) + 1)
        controls[str(g)] = {
            "native_nll": native_nll,
            "median_permuted_nll": float(np.median(perm_nll)),
            "native_better_than_median": bool(native_nll < np.median(perm_nll)),
            "native_rank_of_22_lower_is_better": rank,
            "best_quarter": bool(rank <= 5),
            "unique_permutations": int(len({tuple(row["permutation"]) for row in rows})),
            "controls": rows,
        }
    control_pass = all(v["native_better_than_median"] and v["best_quarter"] for v in controls.values())

    if primary_pass and control_pass:
        verdict = "PROGRESSIVE ENERGY-PLACEMENT MECHANISM SUPPORTED"
    elif primary_pass:
        verdict = "PROGRESSIVE PLACEMENT PRESENT; PHYSICAL ENERGY ORDER NOT SUPPORTED"
    else:
        verdict = "PROGRESSIVE ENERGY-PLACEMENT MECHANISM NOT SUPPORTED"

    results = {
        "test": "T375",
        "date": "2026-08-13",
        "source": "COHERENT CENNS-10 liquid-argon Analysis A public 3D release",
        "evidence_class": "predeclared internal intermediate-resolution mechanism test; endpoints previously exposed by T374",
        "medium_change": False,
        "identity_change": False,
        "target_x": TARGET_X,
        "target_prompt_share": TARGET_SHARE,
        "energy_groups": {str(k): v for k, v in GROUPS.items()},
        "template_energy_fraction": (signal_cube.sum(axis=(1, 2)) / signal_cube.sum()).tolist(),
        "ladder": ladder,
        "primary_metrics": {
            "spearman_energy_groups_vs_distance_to_1_25": rho,
            "successive_refinements_reducing_distance": successive_improvements,
            "required_successive_refinements": 3,
            "all_centres_finite": finite_all,
            "intermediate_centres_same_side_of_ridge": intermediate_same_side,
            "primary_gate": primary_pass,
        },
        "energy_order_controls": controls,
        "energy_order_control_gate": control_pass,
        "verdict": verdict,
        "boundaries": [
            "The 1-group and 12-group endpoints were already exposed in T374; T375 tests only the frozen intermediate ladder and order controls.",
            "All levels reuse the same events and are not independent replications.",
            "Improved placement may reflect ordinary signal/background separation and does not alone establish a microscopic ARA mechanism.",
            "The exact liquid-parent 1.25 law still requires a new same-identity event record.",
        ],
    }
    (HERE / "T375_LIQUID_ARGON_ENERGY_PLACEMENT_RESULTS.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    with (HERE / "T375_LIQUID_ARGON_ENERGY_PLACEMENT_LADDER.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["energy_groups", "prompt_share", "handover_time_us", "handover_x", "distance_to_1_25", "delta_nll_at_1_25", "profile_x_low", "profile_x_high"])
        for g in GROUPS:
            row = ladder[str(g)]
            w.writerow([g, row["prompt_share"], row["handover_time_us"], row["handover_x"], row["distance_to_1_25"], row["delta_nll_at_1_25"], *row["profile_95_x"]])

    with (HERE / "T375_LIQUID_ARGON_ENERGY_PLACEMENT_CONTROLS.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["energy_groups", "label", "permutation", "nll", "permuted_minus_native_nll"])
        for g, block in controls.items():
            for row in block["controls"]:
                w.writerow([g, row["label"], " ".join(map(str, row["permutation"])), row["nll"], row["permuted_minus_native_nll"]])

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=True)
    blue, orange, green, red, purple = "#2f7ed8", "#ed9b33", "#1b9e77", "#c33c54", "#7b3294"

    xs = np.asarray([ladder[str(g)]["handover_x"] for g in GROUPS])
    axes[0, 0].plot(levels, xs, "o-", color=blue, lw=2.4, ms=7)
    for g, x in zip(levels, xs):
        axes[0, 0].annotate(f"{x:.3f}", (g, x), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=9)
    axes[0, 0].axhline(1.0, color="black", lw=1.2, label="parent ridge 1.0")
    axes[0, 0].axhline(1.25, color=red, ls="--", lw=2, label="frozen lead 1.25")
    axes[0, 0].axhspan(1.0, 1.5, color="#dff2e8", alpha=0.6)
    axes[0, 0].set(xscale="log", xticks=levels, xticklabels=[str(int(v)) for v in levels], xlabel="retained energy groups", ylabel="ARA coordinate at handover", title="Nested energy resolution inside the same liquid parent", ylim=(0.9, 2.04))
    axes[0, 0].legend(fontsize=8)

    axes[0, 1].plot(levels, distances, "o-", color=purple, lw=2.4, ms=7)
    axes[0, 1].set(xscale="log", xticks=levels, xticklabels=[str(int(v)) for v in levels], xlabel="retained energy groups", ylabel="|x − 1.25|", title=f"Placement error (Spearman ρ = {rho:+.3f})")

    control_levels = [3, 5, 12]
    penalties = [controls[str(g)]["median_permuted_nll"] - controls[str(g)]["native_nll"] for g in control_levels]
    axes[1, 0].bar([str(g) for g in control_levels], penalties, color=[green if v > 0 else red for v in penalties])
    for i, (g, val) in enumerate(zip(control_levels, penalties)):
        axes[1, 0].text(i, val, f"rank {controls[str(g)]['native_rank_of_22_lower_is_better']}/22", ha="center", va="bottom" if val >= 0 else "top", fontsize=9)
    axes[1, 0].axhline(0, color="black", lw=1)
    axes[1, 0].set(xlabel="energy groups", ylabel="median permuted NLL − native NLL", title="Does physical energy order matter?")

    colors = ["#a6cee3", blue, orange, green, purple]
    for g, color in zip(GROUPS, colors):
        pg = ladder[str(g)]["profile_grid"]
        x = np.asarray([np.nan if v is None else v for v in pg["x"]], dtype=float)
        d = np.asarray(pg["delta_nll"])
        ok = np.isfinite(x)
        order = np.argsort(x[ok])
        axes[1, 1].plot(x[ok][order], d[ok][order], color=color, lw=2, label=f"{g} groups")
    axes[1, 1].axvline(1.25, color=red, ls="--", lw=2)
    axes[1, 1].axhline(PROFILE_GATE, color="black", ls=":", lw=1.4)
    axes[1, 1].set(xlabel="finite handover ARA coordinate", ylabel="profile ΔNLL", title="Likelihood sharpens as energy relation is restored", xlim=(0.45, 2.01), ylim=(0, 6))
    axes[1, 1].legend(fontsize=8)

    fig.suptitle("T375 — liquid-argon nested energy-placement test\nSame medium and events; progressively restore the energy relation", fontsize=16, fontweight="bold")
    fig.savefig(HERE / "T375_LIQUID_ARGON_ENERGY_PLACEMENT_FIGURE.png", dpi=180)
    fig.savefig(HERE / "T375_LIQUID_ARGON_ENERGY_PLACEMENT_FIGURE.svg")
    plt.close(fig)

    print(json.dumps({
        "verdict": verdict,
        "ladder": {g: {"x": ladder[g]["handover_x"], "distance": ladder[g]["distance_to_1_25"]} for g in ladder},
        "rho": rho,
        "successive_improvements": successive_improvements,
        "primary_gate": primary_pass,
        "control_gate": control_pass,
        "control_ranks": {g: controls[g]["native_rank_of_22_lower_is_better"] for g in controls},
    }, indent=2))


if __name__ == "__main__":
    main()

