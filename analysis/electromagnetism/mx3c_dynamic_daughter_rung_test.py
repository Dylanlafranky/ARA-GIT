"""MX3c development test of a dynamic pressure-derived daughter-rung angle.

The pressure/velocity-spread moment at frozen mode k0=5 supplies the primary
angle independently of the trapping target. Current and third central moment
are disclosed comparators. This archive is already inspected and contains only
one particle-noise realisation, so all results remain development evidence.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from mx3a_existing_data_identity_analysis import (
    DATA,
    FIELD_SHA256,
    OUT,
    PHASE_SHA256,
    fit_predict,
    regression_metrics,
    safe_load,
    sha256,
)
from mx3b_angled_ridge_test import candidate_metrics, paired_summary, projection


K0 = 5
MAX_LEAD_SLICES = 8
RNG_SEED = 20260712


def circular_resultant(angle_a, angle_b, weights=None):
    difference = np.asarray(angle_a) - np.asarray(angle_b)
    if weights is None:
        weights = np.ones_like(difference)
    weights = np.asarray(weights, float)
    vector = np.sum(weights * np.exp(1j * difference)) / np.sum(weights)
    return float(np.abs(vector)), float(np.angle(vector))


def circular_mae(angle_a, angle_b):
    difference = np.angle(np.exp(1j * (np.asarray(angle_a) - np.asarray(angle_b))))
    return float(np.mean(np.abs(difference)))


def phase_randomised_angles(angles, rng):
    unit = np.exp(1j * np.asarray(angles))
    spectrum = np.fft.fft(unit)
    phases = rng.uniform(0.0, 2.0 * np.pi, size=len(spectrum))
    surrogate = np.fft.ifft(np.abs(spectrum) * np.exp(1j * phases))
    return np.angle(surrogate)


def one_to_one_pairs(selected, e_rms):
    peak = selected[np.argmax(e_rms[selected])]
    rising = selected[selected < peak]
    falling = selected[selected > peak]
    candidates = []
    for pre in rising:
        for post in falling:
            mismatch = abs(e_rms[pre] - e_rms[post]) / e_rms[post]
            if mismatch <= 0.01:
                candidates.append((float(mismatch), int(pre), int(post)))
    used_pre = set()
    used_post = set()
    pairs = []
    for mismatch, pre, post in sorted(candidates):
        if pre not in used_pre and post not in used_post:
            used_pre.add(pre)
            used_post.add(post)
            pairs.append((pre, post, mismatch))
    return pairs


def moment_waves(distribution, velocities, du):
    density = du * np.sum(distribution, axis=1)
    first = du * np.sum(distribution * velocities[None, :, None], axis=1)
    mean_velocity = np.divide(first, density, out=np.zeros_like(first), where=density > 0)
    centred = velocities[None, :, None] - mean_velocity[:, None, :]
    pressure = du * np.sum(distribution * centred**2, axis=1)
    third = du * np.sum(distribution * centred**3, axis=1)
    return density, first, pressure, third


def mode_angle_and_fraction(values, parent_hat, mode):
    fluctuation = values - np.mean(values, axis=1, keepdims=True)
    coefficient = np.fft.rfft(fluctuation, axis=1)
    cross = coefficient[:, mode] * np.conj(parent_hat[:, mode])
    angle = np.angle(cross)
    power = np.abs(coefficient[:, 1:]) ** 2
    fraction = np.divide(
        np.abs(coefficient[:, mode]) ** 2,
        np.sum(power, axis=1),
        out=np.zeros(len(values)),
        where=np.sum(power, axis=1) > 0,
    )
    return angle, fraction, coefficient[:, mode]


def main():
    field_path = DATA / "fld_data.pkl"
    phase_path = DATA / "phase_space_data.pkl"
    if sha256(field_path) != FIELD_SHA256 or sha256(phase_path) != PHASE_SHA256:
        raise RuntimeError("Development data hash mismatch")

    field = safe_load(field_path)
    phase = safe_load(phase_path)
    distribution = np.asarray(phase["F"], float)
    velocities = np.asarray(phase["v"], float)
    du = float(phase["du"])
    times = np.asarray(field["t"], float)

    rows = list(csv.DictReader((OUT / "MX1_DEVELOPMENT_TIMESERIES.csv").open(encoding="utf-8")))
    eligible = np.asarray([row["eligible"] == "1" for row in rows])
    selected = np.flatnonzero(eligible)
    e_rms = np.asarray([float(row["e_rms"]) for row in rows])
    fundamental = np.asarray([float(row["fundamental_fraction"]) for row in rows])
    te_g = np.asarray([float(row["te_ara_rho_g_analogue"]) for row in rows])
    te_f = np.asarray([float(row["te_ara_rho_f_analogue"]) for row in rows])
    g = te_g - 1.0
    f = te_f - 1.0
    q = (g + f) / np.sqrt(2.0)
    d = (g - f) / np.sqrt(2.0)
    z25 = projection(q, d, 25.0)

    mx3a = json.loads((OUT / "MX3A_EXISTING_DATA_RESULTS.json").read_text(encoding="utf-8"))
    trapped = np.asarray(mx3a["series"]["trapped_fraction"], float)
    nmi = np.asarray(mx3a["series"]["nmi"], float)

    density, current_moment, pressure, third_moment = moment_waves(
        distribution, velocities, du
    )
    rho_f = 1.0 - density
    rho_f_hat = np.fft.rfft(rho_f, axis=1)
    pressure_angle, pressure_fraction, _ = mode_angle_and_fraction(
        pressure, rho_f_hat, K0
    )
    current_angle, current_fraction, _ = mode_angle_and_fraction(
        current_moment, rho_f_hat, K0
    )
    third_angle, third_fraction, _ = mode_angle_and_fraction(
        third_moment, rho_f_hat, K0
    )

    dq = np.gradient(q, times)
    dd = np.gradient(d, times)
    tangent_angle = np.arctan2(dd, dq)
    tangent_speed = np.hypot(dq, dd)

    split = int(0.7 * len(selected))
    train = selected[:split]
    test = selected[split:]
    base_train = np.column_stack([e_rms[train], fundamental[train]])
    base_test = np.column_stack([e_rms[test], fundamental[test]])
    base_prediction, _ = fit_predict(base_train, trapped[train], base_test)
    baseline_metrics = regression_metrics(trapped[test], base_prediction)

    # A constant orientation offset may exist between the daughter-wave phase
    # and the q,d tangent. Estimate it on training direction only, never from
    # trapping, then freeze it for held-late use.
    pressure_resultant_train, pressure_offset_raw = circular_resultant(
        tangent_angle[train], pressure_angle[train], tangent_speed[train]
    )
    pressure_aligned = pressure_angle + pressure_offset_raw
    current_resultant_train, current_offset = circular_resultant(
        tangent_angle[train], current_angle[train], tangent_speed[train]
    )
    current_aligned = current_angle + current_offset
    third_resultant_train, third_offset = circular_resultant(
        tangent_angle[train], third_angle[train], tangent_speed[train]
    )
    third_aligned = third_angle + third_offset

    z_pressure_raw = q * np.cos(pressure_angle) + d * np.sin(pressure_angle)
    z_pressure_aligned = q * np.cos(pressure_aligned) + d * np.sin(pressure_aligned)
    z_pressure_weighted = np.sqrt(pressure_fraction) * z_pressure_aligned
    z_current = q * np.cos(current_aligned) + d * np.sin(current_aligned)
    z_third = q * np.cos(third_aligned) + d * np.sin(third_aligned)

    candidate_models = {
        "fixed_25deg": z25,
        "q_d_full": np.column_stack([q, d]),
        "pressure_magnitude": pressure_fraction,
        "pressure_angle_raw": z_pressure_raw,
        "pressure_angle_train_aligned": z_pressure_aligned,
        "pressure_angle_weighted": z_pressure_weighted,
        "pressure_magnitude_plus_dynamic": np.column_stack(
            [pressure_fraction, z_pressure_aligned]
        ),
        "q_d_plus_pressure_magnitude": np.column_stack([q, d, pressure_fraction]),
        "q_d_plus_pressure_dynamic": np.column_stack([q, d, z_pressure_aligned]),
        "current_dynamic_control": z_current,
        "third_moment_dynamic_control": z_third,
    }
    held_late = {"baseline": baseline_metrics}
    for name, values in candidate_models.items():
        held_late[name] = candidate_metrics(
            train, test, base_train, base_test, trapped, values
        )

    direction = {}
    for name, angle, aligned, train_resultant in (
        ("pressure", pressure_angle, pressure_aligned, pressure_resultant_train),
        ("current", current_angle, current_aligned, current_resultant_train),
        ("third_moment", third_angle, third_aligned, third_resultant_train),
    ):
        test_resultant, test_offset = circular_resultant(
            tangent_angle[test], aligned[test], tangent_speed[test]
        )
        direction[name] = {
            "training_resultant": train_resultant,
            "held_late_resultant": test_resultant,
            "held_late_mean_offset_radians": test_offset,
            "held_late_circular_mae_radians": circular_mae(
                tangent_angle[test], aligned[test]
            ),
        }

    lags = np.arange(-MAX_LEAD_SLICES, MAX_LEAD_SLICES + 1)
    lag_resultants = []
    for lag in lags:
        if lag >= 0:
            daughter_indices = selected[: len(selected) - lag or None]
            parent_indices = selected[lag:]
        else:
            daughter_indices = selected[-lag:]
            parent_indices = selected[: len(selected) + lag]
        resultant, _ = circular_resultant(
            tangent_angle[parent_indices],
            pressure_angle[daughter_indices],
            tangent_speed[parent_indices],
        )
        lag_resultants.append(resultant)
    lag_resultants = np.asarray(lag_resultants)
    best_lag_index = int(np.argmax(lag_resultants))

    # Shift and phase-randomised nulls for the zero-lag daughter/parent
    # directional association. Constant angular offset is irrelevant to the
    # resultant magnitude.
    observed_resultant, _ = circular_resultant(
        tangent_angle[selected], pressure_angle[selected], tangent_speed[selected]
    )
    shift_null = []
    for shift in range(10, len(selected) - 9):
        shifted = np.roll(pressure_angle[selected], shift)
        value, _ = circular_resultant(
            tangent_angle[selected], shifted, tangent_speed[selected]
        )
        shift_null.append(value)
    shift_null = np.asarray(shift_null)
    shift_p = float((1 + np.sum(shift_null >= observed_resultant)) / (1 + len(shift_null)))

    rng = np.random.default_rng(RNG_SEED)
    phase_null = []
    for _ in range(500):
        surrogate = phase_randomised_angles(pressure_angle[selected], rng)
        value, _ = circular_resultant(
            tangent_angle[selected], surrogate, tangent_speed[selected]
        )
        phase_null.append(value)
    phase_null = np.asarray(phase_null)
    phase_p = float((1 + np.sum(phase_null >= observed_resultant)) / (1 + len(phase_null)))

    pairs = one_to_one_pairs(selected, e_rms)
    matched = {
        "n_pairs": len(pairs),
        "pressure_magnitude": paired_summary(pressure_fraction, pairs),
        "pressure_dynamic_raw": paired_summary(z_pressure_raw, pairs),
        "pressure_dynamic_aligned": paired_summary(z_pressure_aligned, pairs),
        "fixed_25deg": paired_summary(z25, pairs),
        "q": paired_summary(q, pairs),
        "d": paired_summary(d, pairs),
        "trapped_fraction": paired_summary(trapped, pairs),
        "mutual_information": paired_summary(nmi, pairs),
    }

    rolling = {}
    for fraction in (0.5, 0.6, 0.7, 0.8):
        split_at = int(fraction * len(selected))
        rtrain = selected[:split_at]
        rtest = selected[split_at:]
        rbtrain = np.column_stack([e_rms[rtrain], fundamental[rtrain]])
        rbtest = np.column_stack([e_rms[rtest], fundamental[rtest]])
        rbase_prediction, _ = fit_predict(rbtrain, trapped[rtrain], rbtest)
        rolling[str(fraction)] = {
            "baseline": regression_metrics(trapped[rtest], rbase_prediction)["r2"],
            "fixed_25deg": candidate_metrics(
                rtrain, rtest, rbtrain, rbtest, trapped, z25
            )["r2"],
            "q_d_full": candidate_metrics(
                rtrain, rtest, rbtrain, rbtest, trapped, np.column_stack([q, d])
            )["r2"],
            "pressure_magnitude": candidate_metrics(
                rtrain, rtest, rbtrain, rbtest, trapped, pressure_fraction
            )["r2"],
            "pressure_dynamic_raw": candidate_metrics(
                rtrain, rtest, rbtrain, rbtest, trapped, z_pressure_raw
            )["r2"],
        }

    result = {
        "claim_id": "MX3c",
        "tier": "DEVELOPMENT / ALREADY-INSPECTED SINGLE REALISATION / NOT CONFIRMATORY",
        "primary_daughter": "pressure/velocity-spread moment at k0=5",
        "eligible_n": int(len(selected)),
        "held_late_trapping_models": held_late,
        "direction_association": direction,
        "lead_lag": {
            "lag_convention": "positive means daughter pressure angle leads parent tangent",
            "lags_slices": lags.tolist(),
            "lags_time": np.round(lags * float(np.median(np.diff(times))), 6).tolist(),
            "resultants": np.round(lag_resultants, 8).tolist(),
            "best_lag_slices": int(lags[best_lag_index]),
            "best_lag_time": float(lags[best_lag_index] * np.median(np.diff(times))),
            "best_resultant": float(lag_resultants[best_lag_index]),
        },
        "nulls": {
            "observed_zero_lag_resultant": observed_resultant,
            "circular_shift_null_n": int(len(shift_null)),
            "circular_shift_p": shift_p,
            "circular_shift_95th_percentile": float(np.quantile(shift_null, 0.95)),
            "phase_randomised_null_n": int(len(phase_null)),
            "phase_randomised_p": phase_p,
            "phase_randomised_95th_percentile": float(np.quantile(phase_null, 0.95)),
        },
        "matched_amplitude_one_to_one": matched,
        "rolling_chronological_splits": rolling,
    }
    (OUT / "MX3C_DYNAMIC_DAUGHTER_RESULTS.json").write_text(
        json.dumps(result, indent=2, allow_nan=False), encoding="utf-8"
    )

    base_r2 = held_late["baseline"]["r2"]
    report = f"""# MX3c dynamic daughter-rung result

**Tier:** DEVELOPMENT / ALREADY INSPECTED / SINGLE NOISE REALISATION  
**Primary daughter:** pressure/velocity-spread wave at frozen mode k0=5  
**Eligible slices:** {len(selected)}

## Direction test

The pressure-derived angle has whole-eligible weighted resultant {observed_resultant:.4f} with the parent q,d tangent.
Circular-shift null p={shift_p:.4f}; phase-randomised null p={phase_p:.4f}. On the held-late block, after a constant
orientation offset was learned from parent direction in the training block, pressure resultant is
{direction['pressure']['held_late_resultant']:.4f} and circular MAE is
{direction['pressure']['held_late_circular_mae_radians']:.4f} radians.

Best disclosed lag: {int(lags[best_lag_index])} slices ({lags[best_lag_index] * float(np.median(np.diff(times))):.4f}
time units), where positive means the daughter leads. Resultant: {lag_resultants[best_lag_index]:.4f}.

## Held-late approximate-trapping models

All additions are compared with the same amplitude + fundamental-mode baseline.

| Added information | R-squared | Change |
|---|---:|---:|
| none | {base_r2:.4f} | 0.0000 |
| fixed 25-degree projection | {held_late['fixed_25deg']['r2']:.4f} | {held_late['fixed_25deg']['r2']-base_r2:+.4f} |
| full q,d parent coordinates | {held_late['q_d_full']['r2']:.4f} | {held_late['q_d_full']['r2']-base_r2:+.4f} |
| pressure magnitude only | {held_late['pressure_magnitude']['r2']:.4f} | {held_late['pressure_magnitude']['r2']-base_r2:+.4f} |
| raw pressure-directed reading | {held_late['pressure_angle_raw']['r2']:.4f} | {held_late['pressure_angle_raw']['r2']-base_r2:+.4f} |
| train-aligned pressure reading | {held_late['pressure_angle_train_aligned']['r2']:.4f} | {held_late['pressure_angle_train_aligned']['r2']-base_r2:+.4f} |
| pressure magnitude + dynamic reading | {held_late['pressure_magnitude_plus_dynamic']['r2']:.4f} | {held_late['pressure_magnitude_plus_dynamic']['r2']-base_r2:+.4f} |
| q,d + pressure magnitude | {held_late['q_d_plus_pressure_magnitude']['r2']:.4f} | {held_late['q_d_plus_pressure_magnitude']['r2']-base_r2:+.4f} |
| q,d + pressure dynamic | {held_late['q_d_plus_pressure_dynamic']['r2']:.4f} | {held_late['q_d_plus_pressure_dynamic']['r2']-base_r2:+.4f} |

## Matched-amplitude one-to-one comparison

| Coordinate | Paired Cohen dz | Mean post-minus-pre |
|---|---:|---:|
| pressure magnitude | {matched['pressure_magnitude']['cohen_dz']:.4f} | {matched['pressure_magnitude']['mean_post_minus_pre']:.6f} |
| raw pressure-directed reading | {matched['pressure_dynamic_raw']['cohen_dz']:.4f} | {matched['pressure_dynamic_raw']['mean_post_minus_pre']:.6f} |
| train-aligned pressure reading | {matched['pressure_dynamic_aligned']['cohen_dz']:.4f} | {matched['pressure_dynamic_aligned']['mean_post_minus_pre']:.6f} |
| fixed 25 degrees | {matched['fixed_25deg']['cohen_dz']:.4f} | {matched['fixed_25deg']['mean_post_minus_pre']:.6f} |
| approximate trapping | {matched['trapped_fraction']['cohen_dz']:.4f} | {matched['trapped_fraction']['mean_post_minus_pre']:.6f} |

## Verdict

The primary directional claim is not supported. The observed daughter/parent directional resultant is lower than
almost all circular-shift and phase-randomised nulls. The best disclosed lag is negative and lies at the tested
boundary, so the pressure angle lags rather than leads the parent turn. Its train-aligned orientation also rotates by
nearly pi in the held-late regime.

The high standalone pressure-directed R-squared does not rescue the directional claim. The pressure angle is nearly
constant through much of the eligible interval, making the dynamic reading another approximately fixed projection of
the already-informative q,d coordinates. It does not add to the full parent coordinate: q,d plus pressure direction
scores {held_late['q_d_plus_pressure_dynamic']['r2']:.4f}, below q,d alone at
{held_late['q_d_full']['r2']:.4f}.

Pressure-mode magnitude is nevertheless a strong matched-amplitude state marker
(paired dz={matched['pressure_magnitude']['cohen_dz']:.4f}), but its held-late continuous-state R-squared is only
{held_late['pressure_magnitude']['r2']:.4f}. That is evidence for pressure as an adjacent nonlinear-state observable,
not evidence that its spatial phase supplies the missing ARA viewing direction.

**Status:** `PRESSURE STATE MARKER POSITIVE / PRESSURE-DERIVED DYNAMIC ANGLE NULL / NEXT-RUNG HYPOTHESIS REMAINS OPEN WITH THIS OBSERVABLE REJECTED`.

## Fences

- Pressure is derived from the same particle distribution but is independent of the trapping diagnostic definition.
- The constant orientation offset uses parent tangent direction on training data; it never uses trapping.
- The archive and target were already inspected, so held-late scores remain development evidence.
- A fixed spatial-mode phase may not be the correct mathematical representation of an ARA rung angle.
- Full support still requires unchanged noise/seed/beam transfer.
"""
    (OUT / "MX3C_DYNAMIC_DAUGHTER_REPORT.md").write_text(report, encoding="utf-8")

    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
    ax = axes[0, 0]
    ax.plot(times[selected], tangent_angle[selected], label="parent tangent", linewidth=1.2)
    ax.plot(times[selected], pressure_aligned[selected], label="pressure angle, train-aligned", linewidth=1.0)
    ax.axvline(times[test[0]], color="black", linestyle="--", linewidth=1, label="held-late start")
    ax.set(title="Parent direction and pressure daughter angle", xlabel="time", ylabel="angle (radians)")
    ax.legend(fontsize=8)

    ax = axes[0, 1]
    ax.plot(lags, lag_resultants, marker="o", markersize=3)
    ax.axvline(0, color="black", linewidth=1)
    ax.axvline(lags[best_lag_index], color="tab:red", linestyle="--", label="best disclosed lag")
    ax.set(title="Pressure-angle lead/lag association", xlabel="lag slices; positive = daughter leads", ylabel="circular resultant")
    ax.legend(fontsize=8)

    ax = axes[1, 0]
    labels = ["base", "25 deg", "q,d", "P mag", "P dynamic", "q,d + P mag", "q,d + P dyn"]
    scores = [
        base_r2,
        held_late["fixed_25deg"]["r2"],
        held_late["q_d_full"]["r2"],
        held_late["pressure_magnitude"]["r2"],
        held_late["pressure_angle_train_aligned"]["r2"],
        held_late["q_d_plus_pressure_magnitude"]["r2"],
        held_late["q_d_plus_pressure_dynamic"]["r2"],
    ]
    ax.bar(labels, scores, color=["0.5", "tab:red", "tab:blue", "tab:purple", "tab:orange", "tab:green", "tab:brown"])
    ax.axhline(0, color="black", linewidth=0.8)
    ax.tick_params(axis="x", rotation=25)
    ax.set(title="Held-late trapping description", ylabel="R-squared")

    ax = axes[1, 1]
    ax.hist(shift_null, bins=24, alpha=0.65, label="circular-shift null")
    ax.hist(phase_null, bins=24, alpha=0.55, label="phase-randomised null")
    ax.axvline(observed_resultant, color="black", linewidth=2, label="observed")
    ax.set(title="Daughter/parent direction nulls", xlabel="circular resultant", ylabel="count")
    ax.legend(fontsize=8)

    fig.suptitle("MX3c dynamic pressure-rung test — existing development data")
    fig.savefig(OUT / "MX3C_DYNAMIC_DAUGHTER_RESULT.png", dpi=170)
    plt.close(fig)

    print(json.dumps({
        "report": str(OUT / "MX3C_DYNAMIC_DAUGHTER_REPORT.md"),
        "observed_direction_resultant": observed_resultant,
        "shift_p": shift_p,
        "phase_randomised_p": phase_p,
        "best_lag_slices": int(lags[best_lag_index]),
        "baseline_r2": base_r2,
        "pressure_magnitude_r2": held_late["pressure_magnitude"]["r2"],
        "pressure_dynamic_r2": held_late["pressure_angle_train_aligned"]["r2"],
        "q_d_r2": held_late["q_d_full"]["r2"],
        "q_d_plus_pressure_dynamic_r2": held_late["q_d_plus_pressure_dynamic"]["r2"],
        "matched_pressure_dynamic": matched["pressure_dynamic_aligned"],
    }, indent=2))


if __name__ == "__main__":
    main()
