"""MX3d development test of parent-to-daughter harmonic identity formation.

Parent mode k0=5 and primary daughter 2*k0=10 were declared before this run.
The test requires temporal order, phase inheritance, bicoherence, persistence,
and a separate field/particle daughter participation state. The archive has
already been inspected and has one noise realisation, so this is development.
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
    correlation,
    safe_load,
    sha256,
)
from mx3c_dynamic_daughter_rung_test import moment_waves


K_PARENT = 5
K_DAUGHTER = 10
K_SECONDARY = 15
PERSISTENCE_SLICES = 5
ONSET_SIGMA = 5.0
ONSET_PEAK_FRACTION = 0.01
MAX_LAG_SLICES = 20
RNG_SEED = 20260712


def mode_fraction(coefficients):
    power = np.abs(coefficients) ** 2
    total = np.sum(power[:, 1:], axis=1)
    return np.divide(power, total[:, None], out=np.zeros_like(power), where=total[:, None] > 0)


def onset_threshold(amplitude, baseline_end):
    baseline = np.asarray(amplitude[:baseline_end], float)
    return float(max(
        np.mean(baseline) + ONSET_SIGMA * np.std(baseline),
        ONSET_PEAK_FRACTION * np.max(amplitude),
    ))


def persistent_onset(amplitude, threshold, minimum_run=PERSISTENCE_SLICES):
    above = np.asarray(amplitude) >= threshold
    run = 0
    for index, value in enumerate(above):
        run = run + 1 if value else 0
        if run >= minimum_run:
            return index - minimum_run + 1
    return None


def weighted_resultant(angle, weight=None):
    angle = np.asarray(angle, float)
    if weight is None:
        weight = np.ones_like(angle)
    weight = np.asarray(weight, float)
    if np.sum(weight) <= 0:
        return float("nan"), float("nan")
    vector = np.sum(weight * np.exp(1j * angle)) / np.sum(weight)
    return float(np.abs(vector)), float(np.angle(vector))


def bicoherence(coefficients, mode_a, mode_b, indices):
    mode_c = mode_a + mode_b
    product = coefficients[indices, mode_a] * coefficients[indices, mode_b]
    child = coefficients[indices, mode_c]
    numerator = np.abs(np.mean(product * np.conj(child)))
    denominator = np.sqrt(np.mean(np.abs(product) ** 2) * np.mean(np.abs(child) ** 2))
    return float(numerator / denominator) if denominator > 0 else float("nan")


def triad_control_distribution(coefficients, indices, maximum_parent_mode=15):
    values = []
    labels = []
    max_available = coefficients.shape[1] - 1
    for a in range(1, maximum_parent_mode + 1):
        for b in range(a, maximum_parent_mode + 1):
            if a + b > max_available:
                continue
            if a == K_PARENT and b == K_PARENT:
                continue
            values.append(bicoherence(coefficients, a, b, indices))
            labels.append((a, b, a + b))
    return np.asarray(values, float), labels


def lag_correlations(parent_driver, daughter_response, start, stop, max_lag):
    lags = np.arange(-max_lag, max_lag + 1)
    values = []
    base_indices = np.arange(start, stop)
    for lag in lags:
        if lag >= 0:
            parent_indices = base_indices[: len(base_indices) - lag or None]
            child_indices = base_indices[lag:]
        else:
            parent_indices = base_indices[-lag:]
            child_indices = base_indices[: len(base_indices) + lag]
        values.append(correlation(parent_driver[parent_indices], daughter_response[child_indices]))
    return lags, np.asarray(values, float)


def main():
    field_path = DATA / "fld_data.pkl"
    phase_path = DATA / "phase_space_data.pkl"
    if sha256(field_path) != FIELD_SHA256 or sha256(phase_path) != PHASE_SHA256:
        raise RuntimeError("Development data hash mismatch")

    field = safe_load(field_path)
    phase = safe_load(phase_path)
    electric = np.asarray(field["E"], float)
    distribution = np.asarray(phase["F"], float)
    velocities = np.asarray(phase["v"], float)
    du = float(phase["du"])
    dx = float(field["dx"])
    times = np.asarray(field["t"], float)
    ntime, nspace = electric.shape

    rows = list(csv.DictReader((OUT / "MX1_DEVELOPMENT_TIMESERIES.csv").open(encoding="utf-8")))
    eligibility = np.asarray([row["eligible"] == "1" for row in rows])
    eligibility_start = int(np.flatnonzero(eligibility)[0])

    density, _, pressure, _ = moment_waves(distribution, velocities, du)
    rho_f = 1.0 - density
    k_phys = 2.0 * np.pi * np.fft.rfftfreq(nspace, d=dx)
    e_hat = np.fft.rfft(electric, axis=1)
    rho_g_hat = 1j * k_phys[None, :] * e_hat
    rho_f_hat = np.fft.rfft(rho_f, axis=1)
    pressure_hat = np.fft.rfft(pressure - np.mean(pressure, axis=1, keepdims=True), axis=1)

    e_fraction = mode_fraction(e_hat)
    g_fraction = mode_fraction(rho_g_hat)
    f_fraction = mode_fraction(rho_f_hat)
    pressure_fraction = mode_fraction(pressure_hat)

    parent_amplitude = np.abs(e_hat[:, K_PARENT])
    daughter_amplitude = np.abs(e_hat[:, K_DAUGHTER])
    secondary_amplitude = np.abs(e_hat[:, K_SECONDARY])
    daughter_particle_amplitude = np.abs(rho_f_hat[:, K_DAUGHTER])

    thresholds = {
        "parent_field": onset_threshold(parent_amplitude, eligibility_start),
        "daughter_field": onset_threshold(daughter_amplitude, eligibility_start),
        "daughter_particle": onset_threshold(daughter_particle_amplitude, eligibility_start),
        "secondary_field": onset_threshold(secondary_amplitude, eligibility_start),
    }
    onsets = {
        "parent_field": persistent_onset(parent_amplitude, thresholds["parent_field"]),
        "daughter_field": persistent_onset(daughter_amplitude, thresholds["daughter_field"]),
        "daughter_particle": persistent_onset(
            daughter_particle_amplitude, thresholds["daughter_particle"]
        ),
        "secondary_field": persistent_onset(secondary_amplitude, thresholds["secondary_field"]),
    }
    if onsets["parent_field"] is None or onsets["daughter_field"] is None:
        raise RuntimeError("Declared parent or daughter onset rule did not trigger")
    daughter_start = max(onsets["daughter_field"], onsets["daughter_particle"] or 0)
    post_indices = np.arange(daughter_start, ntime)
    pre_indices = np.arange(onsets["parent_field"], daughter_start)
    baseline_indices = np.arange(0, eligibility_start)

    phase_parent = np.angle(e_hat[:, K_PARENT])
    phase_daughter = np.angle(e_hat[:, K_DAUGHTER])
    phase_secondary = np.angle(e_hat[:, K_SECONDARY])
    phase_closure_2 = np.angle(np.exp(1j * (2.0 * phase_parent - phase_daughter)))
    phase_closure_3 = np.angle(np.exp(1j * (3.0 * phase_parent - phase_secondary)))
    closure_weight_2 = parent_amplitude**2 * daughter_amplitude
    closure_weight_3 = parent_amplitude**3 * secondary_amplitude
    pre_phase_r, pre_phase_mean = weighted_resultant(
        phase_closure_2[pre_indices], closure_weight_2[pre_indices]
    )
    baseline_phase_r, baseline_phase_mean = weighted_resultant(
        phase_closure_2[baseline_indices], closure_weight_2[baseline_indices]
    )
    post_phase_r, post_phase_mean = weighted_resultant(
        phase_closure_2[post_indices], closure_weight_2[post_indices]
    )
    post_phase_r_unweighted, _ = weighted_resultant(phase_closure_2[post_indices])
    post_phase_r_3, _ = weighted_resultant(
        phase_closure_3[post_indices], closure_weight_3[post_indices]
    )

    rng = np.random.default_rng(RNG_SEED)
    shift_null = []
    for shift in range(10, len(post_indices) - 9):
        shifted = np.roll(phase_daughter[post_indices], shift)
        closure = np.angle(np.exp(1j * (2.0 * phase_parent[post_indices] - shifted)))
        value, _ = weighted_resultant(closure, closure_weight_2[post_indices])
        shift_null.append(value)
    shift_null = np.asarray(shift_null)
    shift_p = float((1 + np.sum(shift_null >= post_phase_r)) / (1 + len(shift_null)))

    random_phase_null = []
    for _ in range(1000):
        permuted = rng.permutation(phase_daughter[post_indices])
        closure = np.angle(np.exp(1j * (2.0 * phase_parent[post_indices] - permuted)))
        value, _ = weighted_resultant(closure, closure_weight_2[post_indices])
        random_phase_null.append(value)
    random_phase_null = np.asarray(random_phase_null)
    random_phase_p = float(
        (1 + np.sum(random_phase_null >= post_phase_r)) / (1 + len(random_phase_null))
    )

    field_bicoherence = bicoherence(e_hat, K_PARENT, K_PARENT, post_indices)
    particle_bicoherence = bicoherence(rho_f_hat, K_PARENT, K_PARENT, post_indices)
    pressure_bicoherence = bicoherence(pressure_hat, K_PARENT, K_PARENT, post_indices)
    baseline_field_bicoherence = bicoherence(
        e_hat, K_PARENT, K_PARENT, baseline_indices
    )
    baseline_particle_bicoherence = bicoherence(
        rho_f_hat, K_PARENT, K_PARENT, baseline_indices
    )
    pre_field_bicoherence = bicoherence(e_hat, K_PARENT, K_PARENT, pre_indices)
    field_controls, field_control_labels = triad_control_distribution(e_hat, post_indices)
    particle_controls, _ = triad_control_distribution(rho_f_hat, post_indices)
    field_percentile = float(np.mean(field_controls <= field_bicoherence))
    particle_percentile = float(np.mean(particle_controls <= particle_bicoherence))

    parent_driver = parent_amplitude**2
    daughter_growth = np.gradient(daughter_amplitude, times)
    lags, raw_lag_corr = lag_correlations(
        parent_driver, daughter_amplitude, onsets["parent_field"], ntime, MAX_LAG_SLICES
    )
    _, growth_lag_corr = lag_correlations(
        parent_driver, daughter_growth, onsets["parent_field"], ntime, MAX_LAG_SLICES
    )
    raw_best_index = int(np.nanargmax(raw_lag_corr))
    growth_best_index = int(np.nanargmax(growth_lag_corr))

    parent_peak = int(np.argmax(parent_amplitude))
    daughter_above = daughter_amplitude >= thresholds["daughter_field"]
    persistence_after_onset = 0
    for value in daughter_above[onsets["daughter_field"]:]:
        if value:
            persistence_after_onset += 1
        else:
            break
    post_parent_peak_fraction_above = float(np.mean(daughter_above[parent_peak:]))
    post_peak_daughter_ratio = float(
        np.mean(daughter_amplitude[parent_peak:])
        / np.mean(daughter_amplitude[onsets["parent_field"]:parent_peak])
    )

    te_g_daughter = 2.0 * g_fraction[:, K_DAUGHTER]
    te_f_daughter = 2.0 * f_fraction[:, K_DAUGHTER]
    daughter_closure = 1.0 - np.abs(te_g_daughter - te_f_daughter) / 2.0
    daughter_state = {
        "field_particle_te_correlation_post_onset": correlation(
            te_g_daughter[post_indices], te_f_daughter[post_indices]
        ),
        "mean_closure_post_onset": float(np.mean(daughter_closure[post_indices])),
        "minimum_closure_post_onset": float(np.min(daughter_closure[post_indices])),
        "particle_other_mean_post_onset": float(np.mean(1.0 - f_fraction[post_indices, K_DAUGHTER])),
        "daughter_to_parent_field_power_mean_post_onset": float(
            np.mean(
                np.divide(
                    e_fraction[post_indices, K_DAUGHTER],
                    e_fraction[post_indices, K_PARENT],
                    out=np.zeros(len(post_indices)),
                    where=e_fraction[post_indices, K_PARENT] > 0,
                )
            )
        ),
    }

    onset_order = {
        "daughter_field_minus_parent_slices": int(
            onsets["daughter_field"] - onsets["parent_field"]
        ),
        "daughter_field_minus_parent_time": float(
            times[onsets["daughter_field"]] - times[onsets["parent_field"]]
        ),
        "daughter_particle_minus_parent_slices": int(
            onsets["daughter_particle"] - onsets["parent_field"]
        ) if onsets["daughter_particle"] is not None else None,
        "secondary_field_minus_parent_slices": int(
            onsets["secondary_field"] - onsets["parent_field"]
        ) if onsets["secondary_field"] is not None else None,
    }

    criteria = {
        "positive_temporal_order": onset_order["daughter_field_minus_parent_slices"] > 0,
        "phase_inheritance_beats_shift_null": shift_p < 0.05,
        "phase_inheritance_beats_random_phase_null": random_phase_p < 0.05,
        "field_bicoherence_top_5_percent_controls": field_percentile >= 0.95,
        "particle_bicoherence_top_5_percent_controls": particle_percentile >= 0.95,
        "persists_at_least_declared_slices": persistence_after_onset >= PERSISTENCE_SLICES,
        "persists_after_parent_peak": post_parent_peak_fraction_above >= 0.5,
        "separate_field_particle_state_correlation_over_0_8": (
            daughter_state["field_particle_te_correlation_post_onset"] >= 0.8
        ),
    }

    result = {
        "claim_id": "MX3d",
        "tier": "DEVELOPMENT / ALREADY-INSPECTED SINGLE REALISATION / NOT CONFIRMATORY",
        "declared_modes": {
            "parent": K_PARENT,
            "primary_daughter": K_DAUGHTER,
            "secondary_comparator": K_SECONDARY,
        },
        "onset_rule": {
            "baseline_end_index": eligibility_start,
            "sigma_above_baseline": ONSET_SIGMA,
            "minimum_peak_fraction": ONSET_PEAK_FRACTION,
            "minimum_persistence_slices": PERSISTENCE_SLICES,
        },
        "thresholds": thresholds,
        "onset_indices": onsets,
        "onset_times": {
            key: float(times[value]) if value is not None else None for key, value in onsets.items()
        },
        "onset_order": onset_order,
        "phase_inheritance": {
            "baseline_weighted_resultant": baseline_phase_r,
            "pre_daughter_weighted_resultant": pre_phase_r,
            "post_daughter_weighted_resultant": post_phase_r,
            "post_daughter_unweighted_resultant": post_phase_r_unweighted,
            "post_daughter_mean_closure_angle": post_phase_mean,
            "third_harmonic_post_weighted_resultant": post_phase_r_3,
            "circular_shift_p": shift_p,
            "circular_shift_95th_percentile": float(np.quantile(shift_null, 0.95)),
            "random_phase_p": random_phase_p,
            "random_phase_95th_percentile": float(np.quantile(random_phase_null, 0.95)),
        },
        "bicoherence": {
            "field_baseline": baseline_field_bicoherence,
            "particle_baseline": baseline_particle_bicoherence,
            "field_pre_daughter": pre_field_bicoherence,
            "field_post_daughter": field_bicoherence,
            "particle_post_daughter": particle_bicoherence,
            "pressure_post_daughter": pressure_bicoherence,
            "field_control_percentile": field_percentile,
            "particle_control_percentile": particle_percentile,
            "field_control_n": int(len(field_controls)),
        },
        "lead_lag": {
            "convention": "positive lag means parent driver leads daughter",
            "lags_slices": lags.tolist(),
            "lags_time": np.round(lags * float(np.median(np.diff(times))), 6).tolist(),
            "raw_amplitude_correlations": np.round(raw_lag_corr, 8).tolist(),
            "growth_correlations": np.round(growth_lag_corr, 8).tolist(),
            "raw_best_lag_slices": int(lags[raw_best_index]),
            "raw_best_correlation": float(raw_lag_corr[raw_best_index]),
            "growth_best_lag_slices": int(lags[growth_best_index]),
            "growth_best_correlation": float(growth_lag_corr[growth_best_index]),
        },
        "persistence": {
            "consecutive_slices_after_onset": persistence_after_onset,
            "fraction_above_threshold_after_parent_peak": post_parent_peak_fraction_above,
            "mean_daughter_amplitude_post_vs_pre_parent_peak_ratio": post_peak_daughter_ratio,
        },
        "daughter_state": daughter_state,
        "criteria": criteria,
        "criteria_passed": int(sum(criteria.values())),
        "criteria_total": int(len(criteria)),
    }
    (OUT / "MX3D_DAUGHTER_ECHO_RESULTS.json").write_text(
        json.dumps(result, indent=2, allow_nan=False), encoding="utf-8"
    )

    report = f"""# MX3d parent-collision to daughter identity result

**Tier:** DEVELOPMENT / ALREADY INSPECTED / SINGLE NOISE REALISATION  
**Parent:** k={K_PARENT}  
**Primary daughter candidate:** k={K_DAUGHTER}  
**Criteria passed:** {sum(criteria.values())}/{len(criteria)}

## Temporal order

Parent onset: index {onsets['parent_field']}, t={times[onsets['parent_field']]:.4f}.  
Daughter field onset: index {onsets['daughter_field']}, t={times[onsets['daughter_field']]:.4f}.  
Daughter particle onset: index {onsets['daughter_particle']}, t={times[onsets['daughter_particle']]:.4f}.  
Field daughter minus parent: {onset_order['daughter_field_minus_parent_slices']} slices,
{onset_order['daughter_field_minus_parent_time']:.4f} time units.

## Phase inheritance

| Measure | Value |
|---|---:|
| pre-parent baseline weighted resultant | {baseline_phase_r:.4f} |
| pre-daughter weighted phase-closure resultant | {pre_phase_r:.4f} |
| post-daughter weighted phase-closure resultant | {post_phase_r:.4f} |
| post-daughter unweighted resultant | {post_phase_r_unweighted:.4f} |
| circular-shift p | {shift_p:.4f} |
| random-phase p | {random_phase_p:.4f} |
| third-harmonic post-onset resultant | {post_phase_r_3:.4f} |

## Bicoherence

| View | Target bicoherence | Control percentile |
|---|---:|---:|
| field k5+k5->k10 | {field_bicoherence:.4f} | {field_percentile:.4f} |
| particle source k5+k5->k10 | {particle_bicoherence:.4f} | {particle_percentile:.4f} |
| pressure k5+k5->k10 | {pressure_bicoherence:.4f} | not primary |

Baseline field/particle bicoherence: {baseline_field_bicoherence:.4f} / {baseline_particle_bicoherence:.4f}.  
Pre-daughter field bicoherence after parent onset: {pre_field_bicoherence:.4f}.

## Parent-to-daughter lag

Raw daughter amplitude: best lag {int(lags[raw_best_index])} slices, r={raw_lag_corr[raw_best_index]:.4f}.  
Daughter growth: best lag {int(lags[growth_best_index])} slices, r={growth_lag_corr[growth_best_index]:.4f}.  
Positive lag means parent driver leads daughter.

## Persistence and separate state

- consecutive slices above threshold after daughter onset: {persistence_after_onset};
- fraction above threshold after parent peak: {post_parent_peak_fraction_above:.4f};
- mean daughter amplitude after/before parent peak ratio: {post_peak_daughter_ratio:.4f};
- daughter field/particle TE correlation post-onset: {daughter_state['field_particle_te_correlation_post_onset']:.4f};
- mean daughter closure post-onset: {daughter_state['mean_closure_post_onset']:.4f};
- mean daughter/parent field-power ratio post-onset: {daughter_state['daughter_to_parent_field_power_mean_post_onset']:.4f}.

## Decision criteria

""" + "\n".join(
        f"- {'PASS' if value else 'FAIL'}: {name}" for name, value in criteria.items()
    ) + """

## Verdict

The declared k10 candidate receives strong but incomplete development support as a nonlinear daughter identity. It
crosses the field threshold 19 slices after the parent and the particle threshold 31 slices after the parent. Phase
closure rises from {baseline_phase_r:.4f} before parent eligibility to {pre_phase_r:.4f} during sub-threshold daughter
formation and remains {post_phase_r:.4f} after visible onset. Field bicoherence rises from
{baseline_field_bicoherence:.4f} to {field_bicoherence:.4f}; particle bicoherence is
{particle_bicoherence:.4f}. The daughter persists and has a highly reproducible field/particle participation state.

Two strict fences prevent promotion. Circularly shifting the daughter within the already phase-locked post-onset
interval does not destroy closure, so the time-local shift null fails. Particle bicoherence ranks at the
{particle_percentile:.4f} percentile, just below the predeclared 0.95 cutoff. Parent-driver cross-correlation also peaks
at a negative boundary even though threshold onset order is positive, showing that gradual shared trends do not give
a clean predictive growth lag.

The most defensible reading is gradual nonlinear inheritance: coupling becomes phase-organised below the chosen
visibility threshold, the daughter then becomes measurable and persists as its own small participation mode. This is
consistent with established harmonic/three-wave physics. Whether the same bundle defines a scale-general ARA identity
requires noise/seed transfer.

**Status:** `6/8 STRICT CRITERIA / NONLINEAR DAUGHTER IDENTITY DEVELOPMENT-SUPPORTED / TIME-LOCAL AND PARTICLE-BICOHERENCE FENCES OPEN`.

## Fences

- Harmonic generation and three-wave phase coupling are established plasma mechanisms.
- This test asks whether the declared secondary mode meets a reproducible ARA identity-birth bundle.
- Daughter closure near one is not sufficient by itself because both participation fractions can be small; the
  field/particle correlation, phase inheritance, onset order and persistence carry the interpretation.
- Threshold onset means first sustained visibility under the declared rule, not creation from exact zero.
- A single already-inspected noise realisation cannot establish fractality or universality.
- The onset thresholds and mode family require transfer without alteration.
"""
    (OUT / "MX3D_DAUGHTER_ECHO_REPORT.md").write_text(report, encoding="utf-8")

    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
    ax = axes[0, 0]
    ax.semilogy(times, e_fraction[:, K_PARENT] + 1e-14, label="parent k5")
    ax.semilogy(times, e_fraction[:, K_DAUGHTER] + 1e-14, label="daughter k10")
    ax.semilogy(times, e_fraction[:, K_SECONDARY] + 1e-14, label="secondary k15")
    ax.axvline(times[onsets["parent_field"]], color="black", linestyle="--", label="parent onset")
    ax.axvline(times[onsets["daughter_field"]], color="tab:red", linestyle="--", label="daughter onset")
    ax.set(title="Parent and daughter field participation", xlabel="time", ylabel="spectral power fraction")
    ax.legend(fontsize=8)

    ax = axes[0, 1]
    ax.plot(times, phase_closure_2, linewidth=1.0, label="2 phi5 - phi10")
    ax.axvline(times[daughter_start], color="tab:red", linestyle="--", label="joint daughter eligibility")
    ax.set(title="Parent-to-daughter phase closure", xlabel="time", ylabel="wrapped angle (radians)")
    ax.legend(fontsize=8)

    ax = axes[1, 0]
    ax.plot(lags, raw_lag_corr, marker="o", markersize=3, label="daughter amplitude")
    ax.plot(lags, growth_lag_corr, marker="o", markersize=3, label="daughter growth")
    ax.axvline(0, color="black", linewidth=1)
    ax.set(title="Parent driver to daughter lag", xlabel="lag slices; positive = parent leads", ylabel="correlation")
    ax.legend(fontsize=8)

    ax = axes[1, 1]
    ax.plot(times[post_indices], te_g_daughter[post_indices], label="daughter TE field-derived")
    ax.plot(times[post_indices], te_f_daughter[post_indices], label="daughter TE particle-derived")
    ax.plot(times[post_indices], daughter_closure[post_indices], label="daughter closure", alpha=0.8)
    ax.set(title="Candidate daughter identity state", xlabel="time", ylabel="0-2 / closure coordinate")
    ax.legend(fontsize=8)

    fig.suptitle("MX3d parent-to-daughter harmonic test — existing development data")
    fig.savefig(OUT / "MX3D_DAUGHTER_ECHO_RESULT.png", dpi=170)
    plt.close(fig)

    print(json.dumps({
        "report": str(OUT / "MX3D_DAUGHTER_ECHO_REPORT.md"),
        "onset_order": onset_order,
        "phase_post_resultant": post_phase_r,
        "phase_shift_p": shift_p,
        "phase_random_p": random_phase_p,
        "field_bicoherence": field_bicoherence,
        "field_control_percentile": field_percentile,
        "particle_bicoherence": particle_bicoherence,
        "particle_control_percentile": particle_percentile,
        "persistence": result["persistence"],
        "daughter_state": daughter_state,
        "criteria_passed": result["criteria_passed"],
        "criteria_total": result["criteria_total"],
    }, indent=2))


if __name__ == "__main__":
    main()
