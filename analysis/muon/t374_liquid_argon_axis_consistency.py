"""T374: frozen axis-consistency audit of the T373 liquid-argon 1.25 lead."""

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
PROFILE_GATE = 1.920729410347062

CUTS = {
    "full_3d": (0, 1, 2),
    "energy_time": (0, 2),
    "f90_time": (1, 2),
    "energy_f90": (0, 1),
    "time_only": (2,),
    "energy_only": (0,),
    "f90_only": (1,),
}
TIME_BEARING = {"full_3d", "energy_time", "f90_time", "time_only"}


def project(a: np.ndarray, keep_axes: tuple[int, ...]) -> np.ndarray:
    drop = tuple(i for i in range(a.ndim) if i not in keep_axes)
    out = a.sum(axis=drop) if drop else a.copy()
    # np.sum retains the original order of the axes that remain.
    return np.asarray(out, dtype=float)


def x_from_share(
    share: float,
    times: np.ndarray,
    prompt_time_shape: np.ndarray,
    delayed_time_shape: np.ndarray,
) -> tuple[float, float]:
    return handover(
        times,
        share * prompt_time_shape,
        (1.0 - share) * delayed_time_shape,
    )


def profile_cut(
    y_cube: np.ndarray,
    component_cubes: list[np.ndarray],
    keep_axes: tuple[int, ...],
    times: np.ndarray,
    prompt_time_shape: np.ndarray,
    delayed_time_shape: np.ndarray,
    target_share: float,
) -> dict:
    y = project(y_cube, keep_axes).ravel()
    templates = [normalize(project(c, keep_axes)).ravel() for c in component_cubes]
    shares = np.linspace(0.001, 0.999, 301)
    nll = np.asarray([fit_fixed(y, templates, float(s))["nll"] for s in shares])
    i_min = int(np.nanargmin(nll))
    left = float(shares[max(0, i_min - 1)])
    right = float(shares[min(len(shares) - 1, i_min + 1)])
    if right > left:
        refined = minimize_scalar(
            lambda s: fit_fixed(y, templates, float(s))["nll"],
            bounds=(left, right), method="bounded", options={"xatol": 1e-8},
        )
        refined_share = float(refined.x)
        refined_fit = fit_fixed(y, templates, refined_share)
    else:
        refined_share = float(shares[i_min])
        refined_fit = fit_fixed(y, templates, refined_share)
    grid_fit = fit_fixed(y, templates, float(shares[i_min]))
    if grid_fit["nll"] < refined_fit["nll"]:
        share, best = float(shares[i_min]), grid_fit
    else:
        share, best = refined_share, refined_fit

    total_signal = float(best["params"][0])
    p, d = share * total_signal, (1.0 - share) * total_signal
    t_h, x_h = x_from_share(share, times, prompt_time_shape, delayed_time_shape)

    target = fit_fixed(y, templates, target_share)
    target_delta = float(max(0.0, target["nll"] - best["nll"]))

    delta = nll - float(best["nll"])
    xs = np.asarray([
        x_from_share(float(s), times, prompt_time_shape, delayed_time_shape)[1]
        for s in shares
    ])
    ok = np.isfinite(xs) & (delta <= PROFILE_GATE)
    x_interval = [float(np.min(xs[ok])), float(np.max(xs[ok]))] if np.any(ok) else [None, None]
    share_ok = delta <= PROFILE_GATE
    share_interval = (
        [float(np.min(shares[share_ok])), float(np.max(shares[share_ok]))]
        if np.any(share_ok) else [None, None]
    )
    return {
        "fit_success": bool(best["success"]),
        "nll": float(best["nll"]),
        "fitted_prompt_events": p,
        "fitted_delayed_events": d,
        "fitted_total_signal_events": total_signal,
        "prompt_share": share,
        "handover_time_us": t_h,
        "handover_x": x_h,
        "profile_delta_nll_at_1_25": target_delta,
        "target_1_25_compatible": bool(target_delta <= PROFILE_GATE),
        "central_movement_side": bool(np.isfinite(x_h) and 1.0 <= x_h <= 1.5),
        "profile_95_prompt_share": share_interval,
        "profile_95_handover_x_finite_part": x_interval,
        "profile_grid": {
            "prompt_share": shares.tolist(),
            "handover_x": [None if not np.isfinite(v) else float(v) for v in xs],
            "delta_nll": delta.tolist(),
        },
    }


def shifted_order_controls(
    y_cube: np.ndarray,
    component_cubes: list[np.ndarray],
    keep_axes: tuple[int, ...],
    native_nll: float,
) -> dict:
    def robust_free(y: np.ndarray, templates: list[np.ndarray]) -> dict:
        fits = []
        for share in (0.01, 0.10, 0.25, 0.50, 0.75, 0.90, 0.99):
            total = 160.0
            start = np.asarray([share * total, (1.0 - share) * total, 497.0, 33.0, 3154.0])
            fits.append(fit_free(y, templates, start=start))
        return min(fits, key=lambda item: item["nll"])

    values = []
    for shift in range(1, 10):
        shifted = [
            np.roll(component_cubes[0], shift=shift, axis=2),
            np.roll(component_cubes[1], shift=shift, axis=2),
            component_cubes[2], component_cubes[3], component_cubes[4],
        ]
        y = project(y_cube, keep_axes).ravel()
        templates = [normalize(project(c, keep_axes)).ravel() for c in shifted]
        fit = robust_free(y, templates)
        values.append({
            "shift_bins": shift,
            "shift_us": 0.5 * shift,
            "nll": float(fit["nll"]),
            "native_minus_shifted_nll": float(native_nll - fit["nll"]),
            "shifted_minus_native_nll": float(fit["nll"] - native_nll),
            "fit_success": bool(fit["success"]),
        })
    shifted_nll = np.asarray([v["nll"] for v in values])
    all_nll = np.r_[native_nll, shifted_nll]
    rank = int(np.sum(all_nll < native_nll) + 1)
    return {
        "native_nll": native_nll,
        "median_shifted_nll": float(np.median(shifted_nll)),
        "native_better_than_shifted_median": bool(native_nll < np.median(shifted_nll)),
        "native_rank_of_10_lower_is_better": rank,
        "controls": values,
    }


def main() -> None:
    energies, f90s, times, y_cube = load_cube("datanobkgsub.txt")
    _, _, _, signal_cube = load_cube("cevnspdf.txt")
    _, _, _, brn_cube = load_cube("brnpdf.txt")
    _, _, _, dbrn_cube = load_cube("delbrnpdf.txt")
    _, _, _, ss_cube = load_cube("bkgpdf.txt")

    p_time, d_time = timing_bases(times)
    split = decompose_signal(signal_cube, p_time, d_time)
    p_cube = split["prompt"]
    d_cube = split["delayed"]
    component_cubes = [p_cube, d_cube, brn_cube, dbrn_cube, ss_cube]
    p_shape = p_cube.sum(axis=(0, 1)); p_shape /= p_shape.sum()
    d_shape = d_cube.sum(axis=(0, 1)); d_shape /= d_shape.sum()

    grid = np.linspace(0.001, 0.999, 999)
    finite = np.asarray([np.isfinite(x_from_share(float(s), times, p_shape, d_shape)[1]) for s in grid])
    lo, hi = float(grid[finite][0]), float(grid[finite][-1])
    target_share = float(brentq(
        lambda s: x_from_share(s, times, p_shape, d_shape)[1] - TARGET_X,
        lo, hi,
    ))

    cut_results = {}
    for name, axes in CUTS.items():
        cut_results[name] = profile_cut(
            y_cube, component_cubes, axes, times, p_shape, d_shape, target_share
        )

    controls = {}
    for name in TIME_BEARING:
        controls[name] = shifted_order_controls(
            y_cube, component_cubes, CUTS[name], cut_results[name]["nll"]
        )

    primary_names = ["energy_time", "f90_time"]
    main_geometry_pass = all(
        cut_results[n]["fit_success"]
        and np.isfinite(cut_results[n]["handover_x"])
        and cut_results[n]["target_1_25_compatible"]
        and cut_results[n]["central_movement_side"]
        for n in primary_names
    )
    order_pass = all(controls[n]["native_better_than_shifted_median"] for n in TIME_BEARING)

    if main_geometry_pass and order_pass:
        verdict = "SUPPORTED AS AN INTERNAL AXIS-CONSISTENT LIQUID-PARENT LEAD"
    elif main_geometry_pass:
        verdict = "GEOMETRY COMPATIBLE; SOURCE-ORDER CONTROL MIXED"
    else:
        verdict = "LIQUID-PARENT 1.25 LEAD NOT AXIS-CONSISTENT"

    results = {
        "test": "T374",
        "date": "2026-08-13",
        "source": "COHERENT CENNS-10 liquid-argon Analysis A public 3D release",
        "evidence_class": "predeclared internal axis-consistency test; same 3752 events as T373; not an independent replication",
        "medium_change": False,
        "identity_change": False,
        "target_handover_x": TARGET_X,
        "target_prompt_share": target_share,
        "signal_decomposition_nrmse": float(split["nrmse"]),
        "verdict": verdict,
        "main_axis_consistency_gate": main_geometry_pass,
        "arrival_order_control_gate": order_pass,
        "cuts": cut_results,
        "arrival_order_controls": controls,
        "boundaries": [
            "All projection fits reuse the same 3752 liquid-argon events and are correlated views, not independent replications.",
            "The 1.25 hypothesis was formulated after T373 but frozen before T374 projection fits.",
            "A broad projection can be compatible without locating the handover; central estimates and interval widths are therefore reported.",
            "Circular shifts test sensitivity to source timing order; they do not represent alternative physical media.",
            "A new same-identity event record remains necessary for prospective confirmation of the 1.25 law.",
        ],
    }
    out_json = HERE / "T374_LIQUID_ARGON_AXIS_CONSISTENCY_RESULTS.json"
    out_json.write_text(json.dumps(results, indent=2), encoding="utf-8")

    with (HERE / "T374_LIQUID_ARGON_AXIS_CONSISTENCY_CUTS.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "cut", "prompt_share", "handover_time_us", "handover_x",
            "profile_delta_nll_at_1_25", "target_compatible", "movement_side",
            "profile_x_low", "profile_x_high",
        ])
        for name in CUTS:
            c = cut_results[name]
            w.writerow([
                name, c["prompt_share"], c["handover_time_us"], c["handover_x"],
                c["profile_delta_nll_at_1_25"], c["target_1_25_compatible"],
                c["central_movement_side"], *c["profile_95_handover_x_finite_part"],
            ])

    with (HERE / "T374_LIQUID_ARGON_AXIS_CONSISTENCY_CONTROLS.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["cut", "shift_bins", "shift_us", "nll", "shifted_minus_native_nll"])
        for name in sorted(TIME_BEARING):
            for row in controls[name]["controls"]:
                w.writerow([name, row["shift_bins"], row["shift_us"], row["nll"], row["shifted_minus_native_nll"]])

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(15, 11), constrained_layout=True)
    blue, orange, green, red, purple = "#2f7ed8", "#ed9b33", "#1b9e77", "#c33c54", "#7b3294"

    names = list(CUTS)
    labels = [n.replace("_", " × ") for n in names]
    y_pos = np.arange(len(names))
    centres = np.asarray([cut_results[n]["handover_x"] for n in names], dtype=float)
    lows = np.asarray([
        np.nan if cut_results[n]["profile_95_handover_x_finite_part"][0] is None
        else cut_results[n]["profile_95_handover_x_finite_part"][0]
        for n in names
    ])
    highs = np.asarray([
        np.nan if cut_results[n]["profile_95_handover_x_finite_part"][1] is None
        else cut_results[n]["profile_95_handover_x_finite_part"][1]
        for n in names
    ])
    valid = np.isfinite(centres) & np.isfinite(lows) & np.isfinite(highs)
    # Some weak cuts have a free optimum outside the finite equality-crossing
    # portion of the profile grid.  Draw the finite profile support as a range
    # and the free optimum separately; do not imply a symmetric error bar.
    axes[0, 0].hlines(y_pos[valid], lows[valid], highs[valid], color="#8ab6e6", lw=5, alpha=0.85)
    finite_centres = np.isfinite(centres)
    axes[0, 0].scatter(centres[finite_centres], y_pos[finite_centres], color=blue, s=48, zorder=4, label="free-fit centre")
    axes[0, 0].axvline(1.0, color="black", lw=1.2, label="parent ridge 1.0")
    axes[0, 0].axvline(1.25, color=red, ls="--", lw=2, label="frozen liquid lead 1.25")
    axes[0, 0].axvspan(1.0, 1.5, color="#dff2e8", alpha=0.6, label="movement-side interval")
    axes[0, 0].set(yticks=y_pos, yticklabels=labels, xlabel="ARA coordinate at prompt/delayed equality", title="Same liquid parent, different measurement cuts", xlim=(0.35, 2.02))
    axes[0, 0].invert_yaxis(); axes[0, 0].legend(fontsize=8)

    penalties = [cut_results[n]["profile_delta_nll_at_1_25"] for n in names]
    colors = [green if v <= PROFILE_GATE else red for v in penalties]
    axes[0, 1].barh(y_pos, penalties, color=colors, alpha=0.88)
    axes[0, 1].axvline(PROFILE_GATE, color="black", ls="--", label="95% compatibility boundary")
    axes[0, 1].set(yticks=y_pos, yticklabels=labels, xlabel="profile ΔNLL at exact x = 1.25", title="Does each cut permit the frozen location?")
    axes[0, 1].invert_yaxis(); axes[0, 1].legend(fontsize=8)

    control_names = ["full_3d", "energy_time", "f90_time", "time_only"]
    control_labels = [n.replace("_", " × ") for n in control_names]
    control_gain = [
        controls[n]["median_shifted_nll"] - controls[n]["native_nll"]
        for n in control_names
    ]
    axes[1, 0].bar(control_labels, control_gain, color=[green if v > 0 else red for v in control_gain])
    axes[1, 0].axhline(0, color="black", lw=1)
    axes[1, 0].set(ylabel="median shifted-source NLL − native NLL\n(positive favours correct order)", title="Arrival-order negative control")
    axes[1, 0].tick_params(axis="x", rotation=18)

    profile_names = ["full_3d", "energy_time", "f90_time", "energy_f90"]
    profile_colors = [purple, blue, orange, green]
    for name, color in zip(profile_names, profile_colors):
        pg = cut_results[name]["profile_grid"]
        x = np.asarray([np.nan if v is None else v for v in pg["handover_x"]], dtype=float)
        d = np.asarray(pg["delta_nll"])
        order = np.argsort(x[np.isfinite(x)])
        xf = x[np.isfinite(x)][order]; df = d[np.isfinite(x)][order]
        axes[1, 1].plot(xf, df, color=color, lw=2, label=name.replace("_", " × "))
    axes[1, 1].axvline(1.25, color=red, ls="--", lw=2)
    axes[1, 1].axhline(PROFILE_GATE, color="black", ls=":", lw=1.5)
    axes[1, 1].set(xlabel="finite handover ARA coordinate", ylabel="profile ΔNLL", title="Likelihood profiles through the liquid parent", xlim=(0.45, 1.95), ylim=(0, 6))
    axes[1, 1].legend(fontsize=8)

    fig.suptitle(
        "T374 — liquid-argon 1.25 axis-consistency audit\n"
        "Same events and medium; different cuts through one parent identity",
        fontsize=16, fontweight="bold",
    )
    fig.savefig(HERE / "T374_LIQUID_ARGON_AXIS_CONSISTENCY_FIGURE.png", dpi=180)
    fig.savefig(HERE / "T374_LIQUID_ARGON_AXIS_CONSISTENCY_FIGURE.svg")
    plt.close(fig)

    print(json.dumps({
        "verdict": verdict,
        "target_prompt_share": target_share,
        "main_axis_consistency_gate": main_geometry_pass,
        "arrival_order_control_gate": order_pass,
        "cuts": {k: {
            "x": v["handover_x"],
            "delta_nll_1_25": v["profile_delta_nll_at_1_25"],
            "compatible": v["target_1_25_compatible"],
            "movement_side": v["central_movement_side"],
        } for k, v in cut_results.items()},
        "control_ranks": {k: v["native_rank_of_10_lower_is_better"] for k, v in controls.items()},
    }, indent=2))


if __name__ == "__main__":
    main()
