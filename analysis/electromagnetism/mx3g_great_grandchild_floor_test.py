"""MX3g development test of k20->k40->k80 recursive harmonics and floor.

k40 and k80 were declared before inspection. k80 has only 3.2 grid samples per
wavelength in this 256-cell archive; k160 is beyond Nyquist. Any phase-flip
reading is exploratory because a physical flip observable was not yet fixed.
"""

from __future__ import annotations

import csv
import json

import matplotlib.pyplot as plt
import numpy as np

from mx3a_existing_data_identity_analysis import (
    DATA, FIELD_SHA256, OUT, PHASE_SHA256, correlation, safe_load, sha256,
)
from mx3c_dynamic_daughter_rung_test import moment_waves
from mx3d_parent_collision_daughter_test import (
    ONSET_PEAK_FRACTION, ONSET_SIGMA, PERSISTENCE_SLICES,
    bicoherence, mode_fraction, onset_threshold, persistent_onset,
    weighted_resultant,
)
from mx3e_granddaughter_harmonic_test import phase_random_p, route_bicoherences


MODES = [5, 10, 20, 40, 80]
TEST_GENERATIONS = [(20, 40), (40, 80)]
RNG_SEED = 20260712


def wrapped_difference(a, b):
    return float(np.angle(np.exp(1j * (a - b))))


def analyse_generation(parent, child, e_hat, rho_f_hat, e_fraction, g_fraction,
                       f_fraction, times, baseline_end, onsets, particle_onsets,
                       thresholds, particle_thresholds, rng, nspace):
    parent_onset = onsets.get(parent)
    child_onset = onsets.get(child)
    particle_child_onset = particle_onsets.get(child)
    result = {
        "parent": parent,
        "child": child,
        "samples_per_wavelength": float(nspace / child),
        "parent_onset": parent_onset,
        "child_onset": child_onset,
        "particle_child_onset": particle_child_onset,
        "detectable": child_onset is not None and particle_child_onset is not None,
    }
    if not result["detectable"]:
        result["criteria"] = {
            "field_onset_detected": child_onset is not None,
            "particle_onset_detected": particle_child_onset is not None,
        }
        result["criteria_passed"] = sum(result["criteria"].values())
        result["criteria_total"] = len(result["criteria"])
        return result

    start = max(child_onset, particle_child_onset)
    post = np.arange(start, len(times))
    between = np.arange(parent_onset, start)
    baseline = np.arange(0, baseline_end)

    phase_parent = np.angle(e_hat[:, parent])
    phase_child = np.angle(e_hat[:, child])
    closure = np.angle(np.exp(1j * (2.0 * phase_parent - phase_child)))
    weight = np.abs(e_hat[:, parent]) ** 2 * np.abs(e_hat[:, child])
    baseline_r, _ = weighted_resultant(closure[baseline], weight[baseline])
    between_r, _ = weighted_resultant(closure[between], weight[between])
    post_r, post_mean = weighted_resultant(closure[post], weight[post])
    random_p, random_null = phase_random_p(
        e_hat, parent, parent, child, post, post_r, rng
    )

    field_bic = bicoherence(e_hat, parent, parent, post)
    particle_bic = bicoherence(rho_f_hat, parent, parent, post)
    field_routes = route_bicoherences(e_hat, post, child)
    particle_routes = route_bicoherences(rho_f_hat, post, child)
    field_values = np.asarray([row["bicoherence"] for row in field_routes])
    particle_values = np.asarray([row["bicoherence"] for row in particle_routes])
    field_percentile = float(np.mean(field_values <= field_bic))
    particle_percentile = float(np.mean(particle_values <= particle_bic))

    above = np.abs(e_hat[:, child]) >= thresholds[child]
    persistence = 0
    for value in above[child_onset:]:
        if value:
            persistence += 1
        else:
            break

    te_g = 2.0 * g_fraction[:, child]
    te_f = 2.0 * f_fraction[:, child]
    state_corr = correlation(te_g[post], te_f[post])
    state_closure = 1.0 - np.abs(te_g - te_f) / 2.0
    baseline_amplitude = np.abs(e_hat[:baseline_end, child])
    post_amplitude = np.abs(e_hat[post, child])
    snr = float(np.median(post_amplitude) / np.mean(baseline_amplitude))

    criteria = {
        "child_field_after_parent": child_onset > parent_onset,
        "child_particle_after_parent": particle_child_onset > particle_onsets[parent],
        "phase_random_null_pass": random_p < 0.05,
        "field_route_top_20_percent": field_percentile >= 0.8,
        "particle_route_top_20_percent": particle_percentile >= 0.8,
        "persists_declared_slices": persistence >= PERSISTENCE_SLICES,
        "field_particle_state_correlation_over_0_8": state_corr >= 0.8,
        "post_to_baseline_amplitude_snr_over_5": snr >= 5.0,
    }
    result.update({
        "child_minus_parent_field_slices": int(child_onset - parent_onset),
        "child_minus_parent_particle_slices": int(
            particle_child_onset - particle_onsets[parent]
        ),
        "child_minus_parent_time": float(times[child_onset] - times[parent_onset]),
        "phase_baseline_resultant": baseline_r,
        "phase_between_resultant": between_r,
        "phase_post_resultant": post_r,
        "phase_post_mean_angle": post_mean,
        "phase_random_p": random_p,
        "field_bicoherence": field_bic,
        "particle_bicoherence": particle_bic,
        "field_route_percentile": field_percentile,
        "particle_route_percentile": particle_percentile,
        "persistence_slices": persistence,
        "field_particle_te_correlation": state_corr,
        "mean_state_closure": float(np.mean(state_closure[post])),
        "mean_field_power_fraction": float(np.mean(e_fraction[post, child])),
        "post_to_baseline_amplitude_snr": snr,
        "field_routes": field_routes,
        "particle_routes": particle_routes,
        "criteria": criteria,
        "criteria_passed": int(sum(criteria.values())),
        "criteria_total": len(criteria),
    })
    return result


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
    nyquist_mode = nspace // 2

    rows = list(csv.DictReader((OUT / "MX1_DEVELOPMENT_TIMESERIES.csv").open(encoding="utf-8")))
    eligible = np.asarray([row["eligible"] == "1" for row in rows])
    baseline_end = int(np.flatnonzero(eligible)[0])

    density, _, _, _ = moment_waves(distribution, velocities, du)
    rho_f = 1.0 - density
    k_phys = 2.0 * np.pi * np.fft.rfftfreq(nspace, d=dx)
    e_hat = np.fft.rfft(electric, axis=1)
    rho_g_hat = 1j * k_phys[None, :] * e_hat
    rho_f_hat = np.fft.rfft(rho_f, axis=1)
    e_fraction = mode_fraction(e_hat)
    g_fraction = mode_fraction(rho_g_hat)
    f_fraction = mode_fraction(rho_f_hat)

    amplitudes = {mode: np.abs(e_hat[:, mode]) for mode in MODES}
    particle_amplitudes = {mode: np.abs(rho_f_hat[:, mode]) for mode in MODES}
    thresholds = {mode: onset_threshold(amplitudes[mode], baseline_end) for mode in MODES}
    particle_thresholds = {
        mode: onset_threshold(particle_amplitudes[mode], baseline_end) for mode in MODES
    }
    onsets = {mode: persistent_onset(amplitudes[mode], thresholds[mode]) for mode in MODES}
    particle_onsets = {
        mode: persistent_onset(particle_amplitudes[mode], particle_thresholds[mode])
        for mode in MODES
    }

    rng = np.random.default_rng(RNG_SEED)
    generations = {
        f"{parent}_to_{child}": analyse_generation(
            parent, child, e_hat, rho_f_hat, e_fraction, g_fraction, f_fraction,
            times, baseline_end, onsets, particle_onsets, thresholds,
            particle_thresholds, rng, nspace
        )
        for parent, child in TEST_GENERATIONS
    }

    flip = {"testable": False}
    if generations["20_to_40"]["detectable"] and generations["40_to_80"]["detectable"]:
        angle_40 = generations["20_to_40"]["phase_post_mean_angle"]
        angle_80 = generations["40_to_80"]["phase_post_mean_angle"]
        difference = wrapped_difference(angle_80, angle_40)
        flip = {
            "testable": True,
            "phase_closure_angle_k40": angle_40,
            "phase_closure_angle_k80": angle_80,
            "wrapped_difference": difference,
            "distance_from_pi": float(abs(abs(difference) - np.pi)),
            "cosine_sign_flip": bool(np.sign(np.cos(angle_40)) != np.sign(np.cos(angle_80))),
            "tier": "EXPLORATORY / FLIP OBSERVABLE NOT PREDECLARED",
        }

    result = {
        "claim_id": "MX3g",
        "tier": "DEVELOPMENT / SAME INSPECTED ARCHIVE / K40 AND K80 PREDECLARED",
        "grid": {
            "nspace": nspace,
            "nyquist_mode": nyquist_mode,
            "samples_per_wavelength": {str(k): float(nspace / k) for k in MODES},
            "next_after_k80": 160,
            "next_after_k80_representable": 160 <= nyquist_mode,
        },
        "onset_indices": {str(k): onsets[k] for k in MODES},
        "particle_onset_indices": {str(k): particle_onsets[k] for k in MODES},
        "generations": generations,
        "exploratory_flip": flip,
    }
    (OUT / "MX3G_GREAT_GRANDCHILD_FLOOR_RESULTS.json").write_text(
        json.dumps(result, indent=2, allow_nan=False), encoding="utf-8"
    )

    lines = []
    for key, generation in generations.items():
        if not generation["detectable"]:
            lines.append(f"- {key}: not jointly detectable; {generation['criteria_passed']}/{generation['criteria_total']} gates.")
        else:
            lines.append(
                f"- {key}: {generation['criteria_passed']}/{generation['criteria_total']} gates; "
                f"field lag {generation['child_minus_parent_field_slices']} slices; "
                f"phase R={generation['phase_post_resultant']:.4f}, p={generation['phase_random_p']:.4f}; "
                f"field/particle bicoherence={generation['field_bicoherence']:.4f}/"
                f"{generation['particle_bicoherence']:.4f}; TE corr={generation['field_particle_te_correlation']:.4f}."
            )

    g40 = generations["20_to_40"]
    top_field_route = max(g40.get("field_routes", []), key=lambda row: row["bicoherence"], default=None)
    top_particle_route = max(g40.get("particle_routes", []), key=lambda row: row["bicoherence"], default=None)

    report = f"""# MX3g great-grandchild and resolution-floor result

**Tier:** DEVELOPMENT / SAME INSPECTED ARCHIVE  
**Predeclared sequence:** k20 -> k40 -> k80  
**Grid:** {nspace} cells; Nyquist mode k={nyquist_mode}

## Resolution geometry

- k40: {nspace/40:.2f} samples per wavelength;
- k80: {nspace/80:.2f} samples per wavelength;
- next doubling k160: {'representable' if 160 <= nyquist_mode else 'beyond Nyquist and not representable'}.

## Generation results

""" + "\n".join(lines) + f"""

## Exploratory flip

{json.dumps(flip, indent=2)}

The flip calculation is descriptive only. A phase-closure sign change was not fixed as the physical ARA singularity
observable before inspection, and k80 is marginally resolved. No flip claim may be promoted from this archive.

## Verdict

k40 is a detectable fine identity candidate but not a clean k20+k20 self-coupled descendant. It passes
{g40['criteria_passed']}/{g40['criteria_total']} gates: field and particle onsets are ordered after k20, amplitude SNR
is {g40['post_to_baseline_amplitude_snr']:.2f}, it persists {g40['persistence_slices']} slices, and field/particle TE
correlation is {g40['field_particle_te_correlation']:.4f}. But post-onset phase concentration is only
{g40['phase_post_resultant']:.4f}, and exact-ridge k20+k20 bicoherence ranks at only the
{g40['field_route_percentile']:.2f}/{g40['particle_route_percentile']:.2f} field/particle route percentiles.

The strongest k40 routes are
{top_field_route['a']}+{top_field_route['b']} in the field and
{top_particle_route['a']}+{top_particle_route['b']} in particles. The near-ridge 19+21 route is among the strongest,
while exact 20+20 is weak. The fine identity is therefore web-generated rather than a clean binary doubling.

k80 crosses the field threshold but never the particle threshold. At 3.2 samples per wavelength it does not qualify
as an independently recovered identity. The descent reaches the operational floor between k40 and k80. Since k80
never becomes jointly eligible, no physical phase flip is testable; k160 is also beyond the grid Nyquist limit.

**Status:** `K40 WEAK WEB-GENERATED IDENTITY 6/8 / K80 FIELD-ONLY FLOOR / FLIP NOT TESTABLE`.

## Fences

- k80 has only 3.2 samples per wavelength and is vulnerable to grid/deposition artifacts.
- k160 cannot exist as a resolved mode on this grid; this is a hard numerical floor, not automatically a physical
  singularity or universal rung flip.
- Fine-mode identity requires field/particle agreement, phase inheritance, route bicoherence and noise convergence;
  amplitude alone does not count.
"""
    (OUT / "MX3G_GREAT_GRANDCHILD_FLOOR_REPORT.md").write_text(report, encoding="utf-8")

    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
    ax = axes[0, 0]
    for mode in MODES:
        ax.semilogy(times, e_fraction[:, mode] + 1e-16, label=f"k{mode}")
        if onsets[mode] is not None:
            ax.axvline(times[onsets[mode]], linestyle="--", linewidth=0.7)
    ax.set(title="Recursive harmonic descent", xlabel="time", ylabel="field power fraction")
    ax.legend(fontsize=8)

    for ax, (parent, child) in zip(axes[0:1, 1:].flat, [(20, 40)]):
        closure = np.angle(np.exp(1j * (2*np.angle(e_hat[:, parent]) - np.angle(e_hat[:, child]))))
        ax.plot(times, closure)
        ax.set(title=f"{parent}+{parent}->{child} phase closure", xlabel="time", ylabel="wrapped phase")

    ax = axes[1, 0]
    for parent, child in TEST_GENERATIONS:
        closure = np.angle(np.exp(1j * (2*np.angle(e_hat[:, parent]) - np.angle(e_hat[:, child]))))
        ax.plot(times, closure, label=f"{parent}+{parent}->{child}")
    ax.set(title="Late-rung phase comparison", xlabel="time", ylabel="wrapped phase")
    ax.legend(fontsize=8)

    ax = axes[1, 1]
    labels = []
    field_bic = []
    particle_bic = []
    for key, generation in generations.items():
        labels.append(key)
        field_bic.append(generation.get("field_bicoherence", 0.0))
        particle_bic.append(generation.get("particle_bicoherence", 0.0))
    x = np.arange(len(labels))
    ax.bar(x - 0.18, field_bic, width=0.36, label="field")
    ax.bar(x + 0.18, particle_bic, width=0.36, label="particle")
    ax.set_xticks(x, labels)
    ax.set(title="Fine-generation bicoherence", ylabel="bicoherence")
    ax.legend(fontsize=8)

    fig.suptitle("MX3g k40/k80 recursion and resolution floor")
    fig.savefig(OUT / "MX3G_GREAT_GRANDCHILD_FLOOR_RESULT.png", dpi=170)
    plt.close(fig)

    print(json.dumps({
        "report": str(OUT / "MX3G_GREAT_GRANDCHILD_FLOOR_REPORT.md"),
        "grid": result["grid"],
        "onsets": result["onset_indices"],
        "generations": {
            key: {k: v for k, v in value.items() if k not in ("field_routes", "particle_routes")}
            for key, value in generations.items()
        },
        "flip": flip,
    }, indent=2))


if __name__ == "__main__":
    main()
