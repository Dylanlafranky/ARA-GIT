"""MX3b development test of angled and phase-sensitive ARA ridge readings.

The 25-degree projection is a heuristic fixed probe named before this run,
not a proposed universal constant. A 0--90 degree sweep is explicitly exploratory and selects its angle on an
internal chronological validation block before scoring the held-late block.
The source archive has already been inspected, so no result is confirmatory.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from mx3a_existing_data_identity_analysis import (
    DATA,
    FIELD_SHA256,
    OUT,
    PHASE_SHA256,
    correlation,
    fit_predict,
    regression_metrics,
    safe_load,
    sha256,
)


ANGLE_PREDECLARED_DEG = 25.0


def candidate_metrics(train, test, baseline_train, baseline_test, target, candidate):
    candidate = np.asarray(candidate, float)
    if candidate.ndim == 1:
        candidate = candidate[:, None]
    added_train = np.column_stack([baseline_train, candidate[train]])
    added_test = np.column_stack([baseline_test, candidate[test]])
    prediction, _ = fit_predict(added_train, target[train], added_test)
    return regression_metrics(target[test], prediction)


def paired_summary(values, pairs):
    differences = np.asarray([values[j] - values[i] for i, j, _ in pairs], float)
    sd = float(np.std(differences, ddof=1)) if len(differences) > 1 else float("nan")
    mean = float(np.mean(differences)) if len(differences) else float("nan")
    return {
        "n": int(len(differences)),
        "mean_post_minus_pre": mean,
        "median_post_minus_pre": float(np.median(differences)),
        "cohen_dz": mean / sd if sd > 0 else None,
        "fraction_positive": float(np.mean(differences > 0)),
    }


def projection(q, d, angle_deg):
    theta = np.deg2rad(angle_deg)
    return q * np.cos(theta) + d * np.sin(theta)


def main() -> None:
    field_path = DATA / "fld_data.pkl"
    phase_path = DATA / "phase_space_data.pkl"
    if sha256(field_path) != FIELD_SHA256 or sha256(phase_path) != PHASE_SHA256:
        raise RuntimeError("Development data hash mismatch")

    field = safe_load(field_path)
    phase = safe_load(phase_path)
    e = np.asarray(field["E"], float)
    distribution = np.asarray(phase["F"], float)
    du = float(phase["du"])
    dx = float(field["dx"])
    ntime, nspace = e.shape
    k0 = 5

    rows = list(csv.DictReader((OUT / "MX1_DEVELOPMENT_TIMESERIES.csv").open(encoding="utf-8")))
    eligible = np.asarray([row["eligible"] == "1" for row in rows])
    selected = np.flatnonzero(eligible)
    e_rms = np.asarray([float(row["e_rms"]) for row in rows])
    fundamental = np.asarray([float(row["fundamental_fraction"]) for row in rows])
    te_g = np.asarray([float(row["te_ara_rho_g_analogue"]) for row in rows])
    te_f = np.asarray([float(row["te_ara_rho_f_analogue"]) for row in rows])

    mx3a = json.loads((OUT / "MX3A_EXISTING_DATA_RESULTS.json").read_text(encoding="utf-8"))
    trapped = np.asarray(mx3a["series"]["trapped_fraction"], float)
    nmi = np.asarray(mx3a["series"]["nmi"], float)
    closure = 1.0 - np.abs(te_g - te_f) / 2.0

    # Coordinates centred on the TE-ARA ridge G=F. q moves along the ridge;
    # d crosses it. The named angle is measured away from the ridge tangent.
    g = te_g - 1.0
    f = te_f - 1.0
    q = (g + f) / math.sqrt(2.0)
    d = (g - f) / math.sqrt(2.0)
    z25 = projection(q, d, ANGLE_PREDECLARED_DEG)

    # Phase-sensitive field/particle comparison at the frozen identity mode.
    k_phys = 2.0 * np.pi * np.fft.rfftfreq(nspace, d=dx)
    e_hat = np.fft.rfft(e, axis=1)
    rho_g_hat = 1j * k_phys[None, :] * e_hat
    electron_density = du * np.sum(distribution, axis=1)
    rho_f = 1.0 - electron_density
    rho_f_hat = np.fft.rfft(rho_f, axis=1)
    cross = rho_g_hat[:, k0] * np.conj(rho_f_hat[:, k0])
    relative_phase = np.angle(cross)
    phase_alignment = np.cos(relative_phase)
    phase_quadrature = np.sin(relative_phase)

    # Same chronological development split as MX3a.
    split = int(0.7 * len(selected))
    train = selected[:split]
    test = selected[split:]
    baseline_train = np.column_stack([e_rms[train], fundamental[train]])
    baseline_test = np.column_stack([e_rms[test], fundamental[test]])
    baseline_prediction, _ = fit_predict(baseline_train, trapped[train], baseline_test)
    held_late = {
        "baseline_amplitude_mode": regression_metrics(trapped[test], baseline_prediction),
        "closure_distance": candidate_metrics(
            train, test, baseline_train, baseline_test, trapped, closure
        ),
        "ridge_parallel_q": candidate_metrics(
            train, test, baseline_train, baseline_test, trapped, q
        ),
        "ridge_normal_d": candidate_metrics(
            train, test, baseline_train, baseline_test, trapped, d
        ),
        "predeclared_25deg": candidate_metrics(
            train, test, baseline_train, baseline_test, trapped, z25
        ),
        "phase_alignment_quadrature": candidate_metrics(
            train,
            test,
            baseline_train,
            baseline_test,
            trapped,
            np.column_stack([phase_alignment, phase_quadrature]),
        ),
        "predeclared_25deg_plus_phase": candidate_metrics(
            train,
            test,
            baseline_train,
            baseline_test,
            trapped,
            np.column_stack([z25, phase_alignment, phase_quadrature]),
        ),
        "ridge_q_d_plus_phase": candidate_metrics(
            train,
            test,
            baseline_train,
            baseline_test,
            trapped,
            np.column_stack([q, d, phase_alignment, phase_quadrature]),
        ),
    }

    # Internal chronological angle selection: fit block, validation block,
    # then refit at the selected angle before the held-late score.
    inner_split = int(0.7 * len(train))
    inner_fit = train[:inner_split]
    inner_valid = train[inner_split:]
    inner_base_fit = np.column_stack([e_rms[inner_fit], fundamental[inner_fit]])
    inner_base_valid = np.column_stack([e_rms[inner_valid], fundamental[inner_valid]])
    angles = np.arange(0.0, 91.0, 1.0)
    validation_r2 = []
    held_late_r2 = []
    for angle in angles:
        z = projection(q, d, angle)
        validation_r2.append(
            candidate_metrics(
                inner_fit,
                inner_valid,
                inner_base_fit,
                inner_base_valid,
                trapped,
                z,
            )["r2"]
        )
        held_late_r2.append(
            candidate_metrics(train, test, baseline_train, baseline_test, trapped, z)["r2"]
        )
    validation_r2 = np.asarray(validation_r2, float)
    held_late_r2 = np.asarray(held_late_r2, float)
    selected_angle = float(angles[np.nanargmax(validation_r2)])
    selected_z = projection(q, d, selected_angle)
    held_late["validation_selected_angle"] = candidate_metrics(
        train, test, baseline_train, baseline_test, trapped, selected_z
    )

    peak = selected[np.argmax(e_rms[selected])]
    rising = selected[selected < peak]
    falling = selected[selected > peak]
    pairs = []
    for post in falling:
        pre = rising[np.argmin(np.abs(e_rms[rising] - e_rms[post]))]
        relative_mismatch = abs(e_rms[pre] - e_rms[post]) / e_rms[post]
        if relative_mismatch <= 0.01:
            pairs.append((int(pre), int(post), float(relative_mismatch)))

    # The nearest-neighbour reproduction reuses some rising slices. Use a
    # greedy one-to-one amplitude match as the primary robustness result.
    candidates = []
    for pre in rising:
        for post in falling:
            relative_mismatch = abs(e_rms[pre] - e_rms[post]) / e_rms[post]
            if relative_mismatch <= 0.01:
                candidates.append((float(relative_mismatch), int(pre), int(post)))
    used_pre = set()
    used_post = set()
    unique_pairs = []
    for relative_mismatch, pre, post in sorted(candidates):
        if pre not in used_pre and post not in used_post:
            used_pre.add(pre)
            used_post.add(post)
            unique_pairs.append((pre, post, relative_mismatch))

    phase_differences = np.asarray([
        np.angle(np.exp(1j * (relative_phase[j] - relative_phase[i])))
        for i, j, _ in unique_pairs
    ])
    matched_primary = {
        "amplitude_pair_count": len(unique_pairs),
        "mean_relative_amplitude_mismatch": float(np.mean([r for _, _, r in unique_pairs])),
        "closure_distance": paired_summary(closure, unique_pairs),
        "ridge_parallel_q": paired_summary(q, unique_pairs),
        "ridge_normal_d": paired_summary(d, unique_pairs),
        "predeclared_25deg": paired_summary(z25, unique_pairs),
        "trapped_fraction": paired_summary(trapped, unique_pairs),
        "mutual_information": paired_summary(nmi, unique_pairs),
        "relative_phase_circular": {
            "mean_post_minus_pre_radians": float(np.angle(np.mean(np.exp(1j * phase_differences)))),
            "resultant_length": float(np.abs(np.mean(np.exp(1j * phase_differences)))),
        },
    }
    matched_reuse = {
        "amplitude_pair_count": len(pairs),
        "unique_rising_slices": len({i for i, _, _ in pairs}),
        "closure_distance": paired_summary(closure, pairs),
        "ridge_parallel_q": paired_summary(q, pairs),
        "ridge_normal_d": paired_summary(d, pairs),
        "predeclared_25deg": paired_summary(z25, pairs),
        "trapped_fraction": paired_summary(trapped, pairs),
    }

    rolling_splits = {}
    for fraction in (0.5, 0.6, 0.7, 0.8):
        rolling_index = int(fraction * len(selected))
        rolling_train = selected[:rolling_index]
        rolling_test = selected[rolling_index:]
        rolling_base_train = np.column_stack([e_rms[rolling_train], fundamental[rolling_train]])
        rolling_base_test = np.column_stack([e_rms[rolling_test], fundamental[rolling_test]])
        rolling_prediction, _ = fit_predict(
            rolling_base_train, trapped[rolling_train], rolling_base_test
        )
        rolling_splits[str(fraction)] = {
            "baseline": regression_metrics(trapped[rolling_test], rolling_prediction)["r2"],
            "ridge_parallel_q": candidate_metrics(
                rolling_train, rolling_test, rolling_base_train, rolling_base_test, trapped, q
            )["r2"],
            "ridge_normal_d": candidate_metrics(
                rolling_train, rolling_test, rolling_base_train, rolling_base_test, trapped, d
            )["r2"],
            "predeclared_25deg": candidate_metrics(
                rolling_train, rolling_test, rolling_base_train, rolling_base_test, trapped, z25
            )["r2"],
        }

    correlations = {}
    for name, values in {
        "closure_distance": closure,
        "ridge_parallel_q": q,
        "ridge_normal_d": d,
        "predeclared_25deg": z25,
        "phase_alignment": phase_alignment,
        "phase_quadrature": phase_quadrature,
    }.items():
        correlations[name] = {
            "trapped_fraction": correlation(values[selected], trapped[selected]),
            "mutual_information": correlation(values[selected], nmi[selected]),
            "field_rms": correlation(values[selected], e_rms[selected]),
        }

    results = {
        "claim_id": "MX3b",
        "tier": "DEVELOPMENT / ALREADY-INSPECTED SINGLE REALISATION / NOT CONFIRMATORY",
        "predeclared_angle_degrees_from_ridge": ANGLE_PREDECLARED_DEG,
        "angle_claim": "heuristic fixed probe; the proposed next-rung angle is dynamic",
        "coordinate_definition": {
            "g": "TE_rho_G - 1",
            "f": "TE_rho_F - 1",
            "q_parallel": "(g + f)/sqrt(2)",
            "d_normal": "(g - f)/sqrt(2)",
            "z_theta": "q*cos(theta) + d*sin(theta)",
        },
        "eligible_n": int(len(selected)),
        "held_late": held_late,
        "matched_amplitude": {
            "primary_one_to_one": matched_primary,
            "sensitivity_nearest_with_reused_pre_slices": matched_reuse,
        },
        "rolling_chronological_splits": rolling_splits,
        "correlations": correlations,
        "exploratory_angle_sweep": {
            "angles_degrees": angles.tolist(),
            "internal_validation_r2": np.round(validation_r2, 8).tolist(),
            "held_late_r2": np.round(held_late_r2, 8).tolist(),
            "validation_selected_angle_degrees": selected_angle,
            "selected_angle_internal_validation_r2": float(np.nanmax(validation_r2)),
            "selected_angle_held_late_r2": held_late["validation_selected_angle"]["r2"],
            "any_internal_validation_r2_positive": bool(np.nanmax(validation_r2) > 0),
            "predeclared_25deg_internal_validation_r2": float(validation_r2[25]),
        },
        "phase": {
            "definition": "arg(rho_G_hat[k0] * conjugate(rho_F_hat[k0]))",
            "eligible_circular_mean_radians": float(
                np.angle(np.mean(np.exp(1j * relative_phase[selected])))
            ),
            "eligible_resultant_length": float(
                np.abs(np.mean(np.exp(1j * relative_phase[selected])))
            ),
        },
    }
    (OUT / "MX3B_ANGLED_RIDGE_RESULTS.json").write_text(
        json.dumps(results, indent=2, allow_nan=False), encoding="utf-8"
    )

    baseline_r2 = held_late["baseline_amplitude_mode"]["r2"]
    report = rf"""# MX3b angled-ridge and phase-sensitive development result

**Tier:** DEVELOPMENT / ALREADY INSPECTED / NOT CONFIRMATORY  
**Fixed test angle:** {ANGLE_PREDECLARED_DEG:.0f} degrees from the ridge; heuristic, not universal  
**Eligible slices:** {len(selected)}

## Question

Does the earlier matched-amplitude null occur because the scalar closure index measures only absolute distance from
the ridge \(G=F\), discarding motion along the ridge, crossing direction and field-particle phase?

## Coordinates

With \(g=G-1\) and \(f=F-1\):

\[
q=(g+f)/\sqrt{{2}},\qquad d=(g-f)/\sqrt{{2}},\qquad
Z_{{\theta}}=q\cos\theta+d\sin\theta.
\]

Here \(q\) is position along the ridge, \(d\) is signed distance across it, and \(Z_{{25^\circ}}\) is the fixed
oblique probe named before the run. Relative phase is measured independently at the frozen identity mode \(k_0=5\).

## Matched-amplitude result

The primary comparison uses {len(unique_pairs)} one-to-one pre/post pairs matched within 1% field RMS, so no rising
slice is counted repeatedly:

| Coordinate | Mean post-minus-pre | Paired Cohen dz |
|---|---:|---:|
| closure distance | {matched_primary['closure_distance']['mean_post_minus_pre']:.6f} | {matched_primary['closure_distance']['cohen_dz']:.4f} |
| ridge-parallel q | {matched_primary['ridge_parallel_q']['mean_post_minus_pre']:.6f} | {matched_primary['ridge_parallel_q']['cohen_dz']:.4f} |
| ridge-normal d | {matched_primary['ridge_normal_d']['mean_post_minus_pre']:.6f} | {matched_primary['ridge_normal_d']['cohen_dz']:.4f} |
| predeclared 25-degree projection | {matched_primary['predeclared_25deg']['mean_post_minus_pre']:.6f} | {matched_primary['predeclared_25deg']['cohen_dz']:.4f} |
| approximate trapped fraction | {matched_primary['trapped_fraction']['mean_post_minus_pre']:.6f} | {matched_primary['trapped_fraction']['cohen_dz']:.4f} |

Relative field-particle phase changes by a circular mean of
{matched_primary['relative_phase_circular']['mean_post_minus_pre_radians']:.4f} radians across those pairs, with resultant
length {matched_primary['relative_phase_circular']['resultant_length']:.4f}.

The earlier nearest-neighbour method produced 80 pairs but reused all rising information through only
{matched_reuse['unique_rising_slices']} unique rising slices. Its apparent 25-degree effect
\(d_z={matched_reuse['predeclared_25deg']['cohen_dz']:.4f}\) shrinks to
\(d_z={matched_primary['predeclared_25deg']['cohen_dz']:.4f}\) under one-to-one matching. The trapped-fraction
separation remains much larger \(\left(d_z={matched_primary['trapped_fraction']['cohen_dz']:.4f}\right)\).

## Held-late trapping comparison

All models include field RMS and fundamental-mode fraction. Added coordinates are fitted on the first 70% of eligible
slices and scored on the final 30%.

| Added coordinate | Held-late R-squared | Change from baseline |
|---|---:|---:|
| none | {baseline_r2:.4f} | 0.0000 |
| absolute closure distance | {held_late['closure_distance']['r2']:.4f} | {held_late['closure_distance']['r2']-baseline_r2:+.4f} |
| ridge-parallel q | {held_late['ridge_parallel_q']['r2']:.4f} | {held_late['ridge_parallel_q']['r2']-baseline_r2:+.4f} |
| ridge-normal d | {held_late['ridge_normal_d']['r2']:.4f} | {held_late['ridge_normal_d']['r2']-baseline_r2:+.4f} |
| predeclared 25-degree projection | {held_late['predeclared_25deg']['r2']:.4f} | {held_late['predeclared_25deg']['r2']-baseline_r2:+.4f} |
| phase alignment + quadrature | {held_late['phase_alignment_quadrature']['r2']:.4f} | {held_late['phase_alignment_quadrature']['r2']-baseline_r2:+.4f} |
| 25-degree projection + phase | {held_late['predeclared_25deg_plus_phase']['r2']:.4f} | {held_late['predeclared_25deg_plus_phase']['r2']-baseline_r2:+.4f} |
| q + d + phase | {held_late['ridge_q_d_plus_phase']['r2']:.4f} | {held_late['ridge_q_d_plus_phase']['r2']-baseline_r2:+.4f} |

## Exploratory angle sweep

The angle was selected only on an internal chronological validation block, then refitted without changing the angle
and scored held-late. Selected angle: {selected_angle:.0f} degrees. Internal validation R-squared:
{float(np.nanmax(validation_r2)):.4f}. Held-late R-squared: {held_late['validation_selected_angle']['r2']:.4f}.

No angle achieved positive R-squared on the internal validation block. The named 25-degree angle scored
{validation_r2[25]:.4f} internally despite scoring {held_late['predeclared_25deg']['r2']:.4f} held-late. The angle
relation is therefore regime-dependent in this trajectory, not yet a stable transferred law. The held-late gain is
primarily carried by the ridge-parallel coordinate: \(q\) scores {held_late['ridge_parallel_q']['r2']:.4f}, slightly
above the 25-degree projection.

## Rolling split stability

| Training fraction | Baseline | q along ridge | d across ridge | 25 degrees |
|---:|---:|---:|---:|---:|
| 0.5 | {rolling_splits['0.5']['baseline']:.4f} | {rolling_splits['0.5']['ridge_parallel_q']:.4f} | {rolling_splits['0.5']['ridge_normal_d']:.4f} | {rolling_splits['0.5']['predeclared_25deg']:.4f} |
| 0.6 | {rolling_splits['0.6']['baseline']:.4f} | {rolling_splits['0.6']['ridge_parallel_q']:.4f} | {rolling_splits['0.6']['ridge_normal_d']:.4f} | {rolling_splits['0.6']['predeclared_25deg']:.4f} |
| 0.7 | {rolling_splits['0.7']['baseline']:.4f} | {rolling_splits['0.7']['ridge_parallel_q']:.4f} | {rolling_splits['0.7']['ridge_normal_d']:.4f} | {rolling_splits['0.7']['predeclared_25deg']:.4f} |
| 0.8 | {rolling_splits['0.8']['baseline']:.4f} | {rolling_splits['0.8']['ridge_parallel_q']:.4f} | {rolling_splits['0.8']['ridge_normal_d']:.4f} | {rolling_splits['0.8']['predeclared_25deg']:.4f} |

The oblique/along-ridge view becomes useful only after enough of the nonlinear trajectory is included in training.
This supports a state-dependent geometric reading but prevents a universal-angle claim from this run.

## Verdict

The ridge-only scalar was incomplete: retaining position along the ridge materially improves late-state description.
The predeclared 25-degree view is useful on the final block, but it is not uniquely favoured; the pure along-ridge
coordinate performs slightly better, the internal validation block rejects every angle, and one-to-one amplitude
matching leaves only a small 25-degree separation. Direct field-particle phase is almost fixed and adds no gain.

**Status:** `RIDGE-TANGENT INFORMATION POSITIVE / 25-DEGREE LATE-BLOCK POSITIVE / ANGLE-SPECIFIC AND TRANSFER CLAIMS NOT SUPPORTED`.

## Post-test clarification

The 25-degree value was a general geometric estimate, not a claim that identity has one fixed privileged angle. The
intended ARA hypothesis is that the viewing direction is itself a wave supplied by the next coupled rung down, much
as blood pressure supplied directional state missing from the aggregate heart series. MX3b therefore tested only a
fixed-angle proxy. The next test must obtain a changing angle from an independently declared daughter observable,
not optimise the angle against the trapping target.

The 25-degree result is the named geometric test. The sweep is diagnostic only and cannot retroactively replace it.
The whole archive was already inspected, so even the held-late block is development evidence.
"""
    (OUT / "MX3B_ANGLED_RIDGE_REPORT.md").write_text(report, encoding="utf-8")

    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
    ax = axes[0, 0]
    ax.scatter(te_g[selected], te_f[selected], c=np.arange(len(selected)), s=11, cmap="viridis")
    diagonal = np.linspace(0, 2, 100)
    ax.plot(diagonal, diagonal, color="black", linewidth=1, linestyle="--", label="G=F ridge")
    ax.set(xlabel="TE-ARA Gauss-source G", ylabel="TE-ARA particle-source F", title="Trajectory around the closure ridge")
    ax.legend()

    ax = axes[0, 1]
    held_line = ax.plot(angles, held_late_r2, color="tab:orange", label="held-late diagnostic", linewidth=1.7)
    ax.axvline(ANGLE_PREDECLARED_DEG, color="tab:red", linestyle="--", label="predeclared 25 degrees")
    ax.axvline(selected_angle, color="tab:green", linestyle=":", label=f"validation selected {selected_angle:.0f} degrees")
    ax.axhline(baseline_r2, color="black", linewidth=1, alpha=0.7, label="baseline")
    ax.set(xlabel="angle from ridge (degrees)", ylabel="held-late trapping R-squared", title="Angled projection comparison")
    ax.set_ylim(-0.45, 1.08)
    validation_axis = ax.twinx()
    validation_line = validation_axis.plot(
        angles, validation_r2, color="tab:blue", label="internal validation", linewidth=1.4, alpha=0.8
    )
    validation_axis.set_ylabel("internal-validation R-squared")
    lines = held_line + validation_line + ax.lines[1:]
    ax.legend(lines, [line.get_label() for line in lines], fontsize=8, loc="lower left")

    ax = axes[1, 0]
    names = ["closure", "q along", "d across", "25 deg", "trapped"]
    effects = [
        matched_primary["closure_distance"]["cohen_dz"],
        matched_primary["ridge_parallel_q"]["cohen_dz"],
        matched_primary["ridge_normal_d"]["cohen_dz"],
        matched_primary["predeclared_25deg"]["cohen_dz"],
        matched_primary["trapped_fraction"]["cohen_dz"],
    ]
    ax.bar(names, effects, color=["0.5", "tab:blue", "tab:orange", "tab:red", "tab:green"])
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set(ylabel="paired Cohen dz", title="Matched-amplitude pre/post separation")

    ax = axes[1, 1]
    ax.plot(np.asarray(field["t"])[selected], relative_phase[selected], linewidth=1.1, label="relative phase")
    ax2 = ax.twinx()
    ax2.plot(np.asarray(field["t"])[selected], trapped[selected], color="tab:green", alpha=0.7, label="trapped fraction")
    ax.set(xlabel="time", ylabel="phase difference (radians)", title="Phase-sensitive view")
    ax2.set_ylabel("approximate trapped fraction")
    lines = ax.lines + ax2.lines
    ax.legend(lines, [line.get_label() for line in lines], fontsize=8)

    fig.suptitle("MX3b angled ARA ridge test — existing development data")
    fig.savefig(OUT / "MX3B_ANGLED_RIDGE_RESULT.png", dpi=170)
    plt.close(fig)

    print(json.dumps({
        "report": str(OUT / "MX3B_ANGLED_RIDGE_REPORT.md"),
        "predeclared_25deg_held_late_r2": held_late["predeclared_25deg"]["r2"],
        "baseline_held_late_r2": baseline_r2,
        "matched_25deg": matched_primary["predeclared_25deg"],
        "matched_closure": matched_primary["closure_distance"],
        "matched_q": matched_primary["ridge_parallel_q"],
        "matched_d": matched_primary["ridge_normal_d"],
        "phase_plus_25deg_r2": held_late["predeclared_25deg_plus_phase"]["r2"],
        "validation_selected_angle": selected_angle,
        "selected_angle_held_late_r2": held_late["validation_selected_angle"]["r2"],
    }, indent=2))


if __name__ == "__main__":
    main()
