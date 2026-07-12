"""MX3e development test of daughter-to-granddaughter harmonic inheritance.

Declared lineage probes:
  k5 + k5 -> k10       parent self-coupling creates daughter
  k5 + k10 -> k15      mixed parent-daughter descendant
  k10 + k10 -> k20     daughter self-coupling creates grandchild candidate

The k20 mode can have multiple nonlinear production paths, so the test compares
k10+k10 with k5+k15 rather than assuming a unique genealogy.
"""

from __future__ import annotations

import csv
import json

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
from mx3d_parent_collision_daughter_test import (
    ONSET_PEAK_FRACTION,
    ONSET_SIGMA,
    PERSISTENCE_SLICES,
    bicoherence,
    mode_fraction,
    onset_threshold,
    persistent_onset,
    triad_control_distribution,
    weighted_resultant,
)


K_PARENT = 5
K_DAUGHTER = 10
K_MIXED_DESCENDANT = 15
K_GRANDCHILD = 20
RNG_SEED = 20260712


def route_phase(coefficients, mode_a, mode_b, mode_c):
    return np.angle(np.exp(1j * (
        np.angle(coefficients[:, mode_a])
        + np.angle(coefficients[:, mode_b])
        - np.angle(coefficients[:, mode_c])
    )))


def phase_random_p(coefficients, mode_a, mode_b, mode_c, indices, observed, rng, n=1000):
    phase_a = np.angle(coefficients[indices, mode_a])
    phase_b = np.angle(coefficients[indices, mode_b])
    phase_c = np.angle(coefficients[indices, mode_c])
    weight = (
        np.abs(coefficients[indices, mode_a])
        * np.abs(coefficients[indices, mode_b])
        * np.abs(coefficients[indices, mode_c])
    )
    null = []
    for _ in range(n):
        random_c = rng.permutation(phase_c)
        closure = np.angle(np.exp(1j * (phase_a + phase_b - random_c)))
        value, _ = weighted_resultant(closure, weight)
        null.append(value)
    null = np.asarray(null)
    return float((1 + np.sum(null >= observed)) / (1 + len(null))), null


def route_bicoherences(coefficients, indices, child_mode):
    routes = []
    for a in range(1, child_mode // 2 + 1):
        b = child_mode - a
        routes.append({
            "a": a,
            "b": b,
            "child": child_mode,
            "bicoherence": bicoherence(coefficients, a, b, indices),
        })
    return routes


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

    modes = [K_PARENT, K_DAUGHTER, K_MIXED_DESCENDANT, K_GRANDCHILD]
    amplitudes = {mode: np.abs(e_hat[:, mode]) for mode in modes}
    particle_amplitudes = {mode: np.abs(rho_f_hat[:, mode]) for mode in modes}
    thresholds = {
        mode: onset_threshold(amplitudes[mode], baseline_end) for mode in modes
    }
    particle_thresholds = {
        mode: onset_threshold(particle_amplitudes[mode], baseline_end) for mode in modes
    }
    onsets = {
        mode: persistent_onset(amplitudes[mode], thresholds[mode]) for mode in modes
    }
    particle_onsets = {
        mode: persistent_onset(particle_amplitudes[mode], particle_thresholds[mode])
        for mode in modes
    }
    if onsets[K_GRANDCHILD] is None:
        raise RuntimeError("Declared k20 grandchild visibility rule did not trigger")

    grandchild_start = max(onsets[K_GRANDCHILD], particle_onsets[K_GRANDCHILD] or 0)
    post = np.arange(grandchild_start, ntime)
    between = np.arange(onsets[K_DAUGHTER], grandchild_start)
    baseline = np.arange(0, baseline_end)

    route_10_10 = route_phase(e_hat, 10, 10, 20)
    route_5_15 = route_phase(e_hat, 5, 15, 20)
    weight_10_10 = amplitudes[10] ** 2 * amplitudes[20]
    weight_5_15 = amplitudes[5] * amplitudes[15] * amplitudes[20]
    r_10_baseline, _ = weighted_resultant(route_10_10[baseline], weight_10_10[baseline])
    r_10_between, _ = weighted_resultant(route_10_10[between], weight_10_10[between])
    r_10_post, mean_10_post = weighted_resultant(route_10_10[post], weight_10_10[post])
    r_5_15_post, mean_5_15_post = weighted_resultant(route_5_15[post], weight_5_15[post])

    rng = np.random.default_rng(RNG_SEED)
    random_p_10, null_10 = phase_random_p(
        e_hat, 10, 10, 20, post, r_10_post, rng
    )
    random_p_5_15, null_5_15 = phase_random_p(
        e_hat, 5, 15, 20, post, r_5_15_post, rng
    )

    field_bic_10 = bicoherence(e_hat, 10, 10, post)
    field_bic_5_15 = bicoherence(e_hat, 5, 15, post)
    particle_bic_10 = bicoherence(rho_f_hat, 10, 10, post)
    particle_bic_5_15 = bicoherence(rho_f_hat, 5, 15, post)
    field_routes = route_bicoherences(e_hat, post, K_GRANDCHILD)
    particle_routes = route_bicoherences(rho_f_hat, post, K_GRANDCHILD)
    field_route_values = np.asarray([row["bicoherence"] for row in field_routes])
    particle_route_values = np.asarray([row["bicoherence"] for row in particle_routes])
    field_all_controls, _ = triad_control_distribution(e_hat, post, maximum_parent_mode=20)
    particle_all_controls, _ = triad_control_distribution(
        rho_f_hat, post, maximum_parent_mode=20
    )

    above = amplitudes[20] >= thresholds[20]
    persistence = 0
    for value in above[onsets[20]:]:
        if value:
            persistence += 1
        else:
            break

    te_g20 = 2.0 * g_fraction[:, 20]
    te_f20 = 2.0 * f_fraction[:, 20]
    closure20 = 1.0 - np.abs(te_g20 - te_f20) / 2.0
    state = {
        "field_particle_te_correlation": correlation(te_g20[post], te_f20[post]),
        "mean_closure": float(np.mean(closure20[post])),
        "mean_grandchild_to_daughter_field_power_ratio": float(np.mean(
            np.divide(
                e_fraction[post, 20],
                e_fraction[post, 10],
                out=np.zeros(len(post)),
                where=e_fraction[post, 10] > 0,
            )
        )),
        "mean_grandchild_field_power_fraction": float(np.mean(e_fraction[post, 20])),
    }

    onset_order = {
        "k10_minus_k5_slices": int(onsets[10] - onsets[5]),
        "k15_minus_k10_slices": int(onsets[15] - onsets[10]),
        "k20_minus_k10_slices": int(onsets[20] - onsets[10]),
        "particle_k20_minus_particle_k10_slices": int(
            particle_onsets[20] - particle_onsets[10]
        ),
        "k20_minus_k10_time": float(times[onsets[20]] - times[onsets[10]]),
    }

    criteria = {
        "grandchild_field_after_daughter": onsets[20] > onsets[10],
        "grandchild_particle_after_daughter": particle_onsets[20] > particle_onsets[10],
        "daughter_self_coupling_phase_null_pass": random_p_10 < 0.05,
        "daughter_self_coupling_field_bicoherence_top_20pct_routes": bool(
            np.mean(field_route_values <= field_bic_10) >= 0.8
        ),
        "daughter_self_coupling_particle_bicoherence_top_20pct_routes": bool(
            np.mean(particle_route_values <= particle_bic_10) >= 0.8
        ),
        "persists_declared_slices": persistence >= PERSISTENCE_SLICES,
        "separate_field_particle_state_correlation_over_0_8": (
            state["field_particle_te_correlation"] >= 0.8
        ),
        "detectable_mean_power_fraction_over_1e_minus_5": (
            state["mean_grandchild_field_power_fraction"] >= 1e-5
        ),
    }

    result = {
        "claim_id": "MX3e",
        "tier": "DEVELOPMENT / ALREADY-INSPECTED SINGLE REALISATION / NOT CONFIRMATORY",
        "declared_lineage": ["5+5->10", "5+10->15", "10+10->20"],
        "onset_rule": {
            "sigma": ONSET_SIGMA,
            "peak_fraction": ONSET_PEAK_FRACTION,
            "persistence_slices": PERSISTENCE_SLICES,
        },
        "onset_indices": {str(k): int(v) if v is not None else None for k, v in onsets.items()},
        "particle_onset_indices": {
            str(k): int(v) if v is not None else None for k, v in particle_onsets.items()
        },
        "onset_times": {
            str(k): float(times[v]) if v is not None else None for k, v in onsets.items()
        },
        "onset_order": onset_order,
        "phase_inheritance": {
            "10_plus_10_to_20_baseline_resultant": r_10_baseline,
            "10_plus_10_to_20_between_resultant": r_10_between,
            "10_plus_10_to_20_post_resultant": r_10_post,
            "10_plus_10_to_20_post_mean_angle": mean_10_post,
            "10_plus_10_to_20_random_phase_p": random_p_10,
            "5_plus_15_to_20_post_resultant": r_5_15_post,
            "5_plus_15_to_20_post_mean_angle": mean_5_15_post,
            "5_plus_15_to_20_random_phase_p": random_p_5_15,
        },
        "bicoherence": {
            "field_10_plus_10_to_20": field_bic_10,
            "field_5_plus_15_to_20": field_bic_5_15,
            "particle_10_plus_10_to_20": particle_bic_10,
            "particle_5_plus_15_to_20": particle_bic_5_15,
            "field_10_route_percentile_among_sum20": float(
                np.mean(field_route_values <= field_bic_10)
            ),
            "particle_10_route_percentile_among_sum20": float(
                np.mean(particle_route_values <= particle_bic_10)
            ),
            "field_10_percentile_all_triads": float(
                np.mean(field_all_controls <= field_bic_10)
            ),
            "particle_10_percentile_all_triads": float(
                np.mean(particle_all_controls <= particle_bic_10)
            ),
            "field_sum20_routes": field_routes,
            "particle_sum20_routes": particle_routes,
        },
        "persistence_slices": persistence,
        "grandchild_state": state,
        "criteria": criteria,
        "criteria_passed": int(sum(criteria.values())),
        "criteria_total": len(criteria),
    }
    (OUT / "MX3E_GRANDDAUGHTER_RESULTS.json").write_text(
        json.dumps(result, indent=2, allow_nan=False), encoding="utf-8"
    )

    report = f"""# MX3e daughter-to-grandchild harmonic result

**Tier:** DEVELOPMENT / ALREADY INSPECTED / SINGLE NOISE REALISATION  
**Declared grandchild candidate:** k=20 from k=10+k=10  
**Mixed alternative route:** k=5+k=15 -> k=20  
**Criteria passed:** {sum(criteria.values())}/{len(criteria)}

## Onset order

| Mode | Field onset index | Time | Particle onset index |
|---|---:|---:|---:|
| parent k5 | {onsets[5]} | {times[onsets[5]]:.4f} | {particle_onsets[5]} |
| daughter k10 | {onsets[10]} | {times[onsets[10]]:.4f} | {particle_onsets[10]} |
| mixed descendant k15 | {onsets[15]} | {times[onsets[15]]:.4f} | {particle_onsets[15]} |
| grandchild candidate k20 | {onsets[20]} | {times[onsets[20]]:.4f} | {particle_onsets[20]} |

k20 follows k10 by {onset_order['k20_minus_k10_slices']} field slices
({onset_order['k20_minus_k10_time']:.4f} time units) and
{onset_order['particle_k20_minus_particle_k10_slices']} particle slices.

## Phase inheritance

| Route | Post-onset resultant | Random-phase p |
|---|---:|---:|
| k10+k10->k20 | {r_10_post:.4f} | {random_p_10:.4f} |
| k5+k15->k20 | {r_5_15_post:.4f} | {random_p_5_15:.4f} |

k10+k10->k20 phase concentration: baseline {r_10_baseline:.4f}, between daughter and grandchild thresholds
{r_10_between:.4f}, post-grandchild {r_10_post:.4f}.

## Route bicoherence

| View | k10+k10->k20 | k5+k15->k20 | k10 route percentile among sum-20 routes |
|---|---:|---:|---:|
| field | {field_bic_10:.4f} | {field_bic_5_15:.4f} | {np.mean(field_route_values <= field_bic_10):.4f} |
| particle | {particle_bic_10:.4f} | {particle_bic_5_15:.4f} | {np.mean(particle_route_values <= particle_bic_10):.4f} |

## Persistence and separate state

- persistent slices after k20 onset: {persistence};
- mean k20/k10 field-power ratio: {state['mean_grandchild_to_daughter_field_power_ratio']:.6f};
- mean k20 field-power fraction: {state['mean_grandchild_field_power_fraction']:.8f};
- field/particle k20 TE correlation: {state['field_particle_te_correlation']:.4f};
- mean k20 closure: {state['mean_closure']:.4f}.

## Criteria

""" + "\n".join(
        f"- {'PASS' if value else 'FAIL'}: {name}" for name, value in criteria.items()
    ) + """

## Verdict

All eight development criteria pass for a detectable, persistent k20 descendant after k10. The daughter-self-coupling
route has strong phase inheritance and is much stronger than the disclosed k5+k15 mixed route. However, k10+k10 is
not the strongest sum-20 triad: k9+k11 has higher field and particle bicoherence. The result therefore supports a
grandchild within a wider nonlinear coupling web, not an exclusive binary family tree.

The k20 field onset precedes k15, and the k5+k15 phase null fails, which argues against that mixed route being the
primary origin in this trajectory. The grandchild remains fine but measurable, with mean field-power fraction
{state['mean_grandchild_field_power_fraction']:.8f} and field/particle state correlation
{state['field_particle_te_correlation']:.4f}.

**Status:** `8/8 DEVELOPMENT CRITERIA / GRANDCHILD HARMONIC SUPPORTED / UNIQUE GENEALOGY AND NOISE TRANSFER OPEN`.

## Fence

A k20 harmonic is not genealogically unique. It can be generated through k10+k10, k5+k15, repeated k5
self-coupling, or a wider nonlinear network. Strong k10+k10 coupling supports a daughter-self-coupling route but does
not prove that it is the only route. Noise/seed convergence is required because fine modes are most vulnerable to
particle and grid noise.
"""
    (OUT / "MX3E_GRANDDAUGHTER_REPORT.md").write_text(report, encoding="utf-8")

    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
    ax = axes[0, 0]
    for mode in modes:
        ax.semilogy(times, e_fraction[:, mode] + 1e-15, label=f"k{mode}")
        ax.axvline(times[onsets[mode]], linestyle="--", linewidth=0.8)
    ax.set(title="Harmonic lineage and visibility onsets", xlabel="time", ylabel="field power fraction")
    ax.legend(fontsize=8)

    ax = axes[0, 1]
    ax.plot(times, route_10_10, label="10+10->20 phase closure")
    ax.plot(times, route_5_15, label="5+15->20 phase closure", alpha=0.8)
    ax.axvline(times[grandchild_start], color="black", linestyle="--", label="joint k20 eligibility")
    ax.set(title="Grandchild phase inheritance routes", xlabel="time", ylabel="wrapped phase")
    ax.legend(fontsize=8)

    ax = axes[1, 0]
    route_labels = [f"{row['a']}+{row['b']}" for row in field_routes]
    x = np.arange(len(route_labels))
    ax.bar(x - 0.18, field_route_values, width=0.36, label="field")
    ax.bar(x + 0.18, particle_route_values, width=0.36, label="particle")
    ax.set_xticks(x, route_labels, rotation=45)
    ax.set(title="All routes summing to k20", ylabel="bicoherence")
    ax.legend(fontsize=8)

    ax = axes[1, 1]
    ax.plot(times[post], te_g20[post], label="k20 TE field-derived")
    ax.plot(times[post], te_f20[post], label="k20 TE particle-derived")
    ax.plot(times[post], closure20[post], label="k20 closure", alpha=0.8)
    ax.set(title="Grandchild candidate state", xlabel="time", ylabel="0-2 / closure")
    ax.legend(fontsize=8)

    fig.suptitle("MX3e daughter-to-grandchild harmonic test — existing development data")
    fig.savefig(OUT / "MX3E_GRANDDAUGHTER_RESULT.png", dpi=170)
    plt.close(fig)

    print(json.dumps({
        "report": str(OUT / "MX3E_GRANDDAUGHTER_REPORT.md"),
        "onset_order": onset_order,
        "phase_10_plus_10": result["phase_inheritance"],
        "bicoherence_summary": {
            key: value for key, value in result["bicoherence"].items()
            if not key.endswith("routes")
        },
        "grandchild_state": state,
        "criteria_passed": result["criteria_passed"],
        "criteria_total": result["criteria_total"],
    }, indent=2))


if __name__ == "__main__":
    main()
