"""MX9: scale/axis ARA state map and analytic Maxwell calibration."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "MX9_SCALE_AXIS_ARA_MAXWELL_RESULTS.json"
SEED = 20_260_723
TOLERANCE = 1e-12


def outer_states(z: np.ndarray) -> np.ndarray:
    """Return z z^dagger, preserving any leading batch dimensions."""
    return np.einsum("...i,...j->...ij", z, z.conj())


def state_ball(g: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return dimensional activity T and ARA state-ball coordinate s."""
    total = np.real(g[..., 0, 0] + g[..., 1, 1])
    if np.any(total <= 0):
        raise ValueError("coherency activity must be positive")
    cross = g[..., 0, 1]
    s = np.stack(
        [
            2.0 * np.real(cross) / total,
            2.0 * np.imag(cross) / total,
            np.real(g[..., 1, 1] - g[..., 0, 0]) / total,
        ],
        axis=-1,
    )
    return total, s


def ara_projection(s: np.ndarray, axis: np.ndarray) -> np.ndarray:
    return 1.0 + np.sum(s * axis, axis=-1)


def unit_vectors(raw: np.ndarray) -> np.ndarray:
    return raw / np.linalg.norm(raw, axis=-1, keepdims=True)


def max_abs(values: np.ndarray) -> float:
    return float(np.max(np.abs(values)))


def relative_l2(delta: np.ndarray, reference: np.ndarray) -> float:
    denominator = float(np.linalg.norm(reference.ravel()))
    numerator = float(np.linalg.norm(delta.ravel()))
    return numerator / denominator if denominator else numerator


def mixed_state_audit(rng: np.random.Generator) -> dict[str, object]:
    samples = 20_000
    components = 3
    z = rng.normal(size=(samples, components, 2)) + 1j * rng.normal(
        size=(samples, components, 2)
    )
    g = np.einsum("nci,ncj->nij", z, z.conj())
    total, s = state_ball(g)
    axes = unit_vectors(rng.normal(size=(samples, 3)))
    x = ara_projection(s, axes)
    x_reverse = ara_projection(s, -axes)
    t_b = total * x / 2.0
    t_a = total * (2.0 - x) / 2.0
    x_population = ara_projection(s, np.broadcast_to([0.0, 0.0, 1.0], s.shape))
    expected_population = 2.0 * np.real(g[:, 1, 1]) / total

    errors = {
        "maximum_state_norm_excess": float(max(0.0, np.max(np.linalg.norm(s, axis=1)) - 1.0)),
        "minimum_projection": float(np.min(x)),
        "maximum_projection": float(np.max(x)),
        "axis_reversal_max_abs_error": max_abs(x_reverse - (2.0 - x)),
        "allocation_sum_relative_l2_error": relative_l2(t_a + t_b - total, total),
        "allocation_difference_relative_l2_error": relative_l2(
            (t_b - t_a) - total * (x - 1.0), total
        ),
        "population_axis_max_abs_error": max_abs(x_population - expected_population),
    }
    gates = {
        "state_inside_ball": errors["maximum_state_norm_excess"] <= TOLERANCE,
        "projection_in_0_2": errors["minimum_projection"] >= -TOLERANCE
        and errors["maximum_projection"] <= 2.0 + TOLERANCE,
        "axis_reversal": errors["axis_reversal_max_abs_error"] <= TOLERANCE,
        "allocation_sum": errors["allocation_sum_relative_l2_error"] <= TOLERANCE,
        "allocation_difference": errors["allocation_difference_relative_l2_error"] <= TOLERANCE,
        "population_axis": errors["population_axis_max_abs_error"] <= TOLERANCE,
    }
    return {"samples": samples, "metrics": errors, "gates": gates, "all_pass": all(gates.values())}


def pure_state_audit(rng: np.random.Generator) -> dict[str, object]:
    samples = 20_000
    z = rng.normal(size=(samples, 2)) + 1j * rng.normal(size=(samples, 2))
    g = outer_states(z)
    _, s = state_ball(g)
    norm_error = max_abs(np.linalg.norm(s, axis=1) - 1.0)
    return {
        "samples": samples,
        "state_norm_max_abs_error_from_one": norm_error,
        "pass": norm_error <= TOLERANCE,
    }


def incoherent_parent_audit(rng: np.random.Generator) -> dict[str, object]:
    samples = 5_000
    children = 4
    z = rng.normal(size=(samples, children, 2)) + 1j * rng.normal(
        size=(samples, children, 2)
    )
    child_g = outer_states(z)
    child_t, child_s = state_ball(child_g)
    parent_g = np.sum(child_g, axis=1)
    parent_t, parent_s = state_ball(parent_g)
    expected_s = np.sum(child_t[..., None] * child_s, axis=1) / np.sum(child_t, axis=1)[:, None]
    axes = unit_vectors(rng.normal(size=(samples, 3)))
    child_x = 1.0 + np.sum(child_s * axes[:, None, :], axis=-1)
    parent_x = ara_projection(parent_s, axes)
    expected_x = np.sum(child_t * child_x, axis=1) / np.sum(child_t, axis=1)

    parent_s_error = max_abs(parent_s - expected_s)
    parent_x_error = max_abs(parent_x - expected_x)

    # Construct an exact parent ridge from two asymmetric antipodal pure children.
    plus = np.asarray([1.0, 1.0], dtype=np.complex128)
    minus = np.asarray([1.0, -1.0], dtype=np.complex128)
    ridge_g = outer_states(plus) + outer_states(minus)
    _, ridge_s = state_ball(ridge_g)
    child_states = state_ball(np.stack([outer_states(plus), outer_states(minus)]))[1]
    coherence_axis = np.asarray([1.0, 0.0, 0.0])
    child_positions = 1.0 + child_states @ coherence_axis
    ridge_position = float(ara_projection(ridge_s, coherence_axis))

    gates = {
        "parent_state_weighted_average": parent_s_error <= TOLERANCE,
        "parent_projection_weighted_average": parent_x_error <= TOLERANCE,
        "asymmetric_children_make_parent_ridge": max_abs(child_positions - [2.0, 0.0]) <= TOLERANCE
        and abs(ridge_position - 1.0) <= TOLERANCE,
    }
    return {
        "samples": samples,
        "children_per_parent": children,
        "parent_state_max_abs_error": parent_s_error,
        "parent_projection_max_abs_error": parent_x_error,
        "ridge_example": {
            "child_positions": child_positions.tolist(),
            "parent_position": ridge_position,
        },
        "gates": gates,
        "all_pass": all(gates.values()),
    }


def coherent_parent_audit(rng: np.random.Generator) -> dict[str, object]:
    samples = 5_000
    children = 4
    z = rng.normal(size=(samples, children, 2)) + 1j * rng.normal(
        size=(samples, children, 2)
    )
    summed = np.sum(z, axis=1)
    parent_g = outer_states(summed)
    separate = np.sum(outer_states(z), axis=1)
    cross = np.zeros_like(parent_g)
    for left in range(children):
        for right in range(children):
            if left != right:
                cross += np.einsum(
                    "ni,nj->nij", z[:, left], z[:, right].conj()
                )
    reconstructed = separate + cross
    identity_error = relative_l2(reconstructed - parent_g, parent_g)
    omitted_error = np.linalg.norm((separate - parent_g).reshape(samples, -1), axis=1) / np.maximum(
        np.linalg.norm(parent_g.reshape(samples, -1), axis=1), np.finfo(float).tiny
    )

    # Same population allocation, opposite retained relation.
    z_plus = np.asarray([1.0, 1.0], dtype=np.complex128)
    z_minus = np.asarray([1.0, -1.0], dtype=np.complex128)
    example_g = np.stack([outer_states(z_plus), outer_states(z_minus)])
    _, example_s = state_ball(example_g)
    population_axis = np.asarray([0.0, 0.0, 1.0])
    coherence_axis = np.asarray([1.0, 0.0, 0.0])
    population_x = 1.0 + example_s @ population_axis
    coherence_x = 1.0 + example_s @ coherence_axis

    gates = {
        "coherent_cross_term_identity": identity_error <= TOLERANCE,
        "scalar_population_flattening_example": max_abs(population_x - [1.0, 1.0]) <= TOLERANCE
        and max_abs(coherence_x - [2.0, 0.0]) <= TOLERANCE,
    }
    return {
        "samples": samples,
        "children_per_parent": children,
        "cross_term_reconstruction_relative_l2_error": identity_error,
        "omitting_cross_terms_relative_error": {
            "median": float(np.median(omitted_error)),
            "p95": float(np.quantile(omitted_error, 0.95)),
            "maximum": float(np.max(omitted_error)),
        },
        "flattening_example": {
            "population_axis_positions": population_x.tolist(),
            "coherence_axis_positions": coherence_x.tolist(),
        },
        "gates": gates,
        "all_pass": all(gates.values()),
    }


def maxwell_plane_wave_audit() -> dict[str, object]:
    samples = 4_096
    epsilon = 0.7
    c = 3.2
    mu = 1.0 / (epsilon * c * c)
    k = 1.7
    omega = c * k
    theta = np.linspace(0.0, 2.0 * np.pi, samples, endpoint=False)
    cosine = np.cos(theta)
    sine = np.sin(theta)
    electric = cosine
    magnetic = cosine / c

    d_e_dt = omega * sine
    d_b_dt = omega * sine / c
    curl_e_y = -k * sine
    curl_b_x = k * sine / c
    faraday_residual = d_b_dt + curl_e_y
    ampere_residual = d_e_dt - c * c * curl_b_x

    u_e = 0.5 * epsilon * electric**2
    u_b = 0.5 * magnetic**2 / mu
    u_total = u_e + u_b
    poynting = electric * magnetic / mu

    active = np.abs(cosine) > 1e-10
    normalized_pair = np.stack(
        [np.sqrt(epsilon) * electric[active], magnetic[active] / np.sqrt(mu)], axis=1
    )
    _, pair_s = state_ball(outer_states(normalized_pair))
    population_axis = np.broadcast_to([0.0, 0.0, 1.0], pair_s.shape)
    coherence_axis = np.broadcast_to([1.0, 0.0, 0.0], pair_s.shape)
    population_x = ara_projection(pair_s, population_axis)
    coherence_x = ara_projection(pair_s, coherence_axis)

    one_flip = normalized_pair.copy()
    one_flip[:, 1] *= -1.0
    _, one_flip_s = state_ball(outer_states(one_flip))
    one_flip_coherence_x = ara_projection(one_flip_s, coherence_axis)

    joint_flip = -normalized_pair
    joint_flip_g = outer_states(joint_flip)
    original_g = outer_states(normalized_pair)

    field_change_dot = float(
        np.dot(cosine, sine) / (np.linalg.norm(cosine) * np.linalg.norm(sine))
    )
    e_b_correlation = float(np.corrcoef(electric, c * magnetic)[0, 1])
    quadrature_x = 2.0 * sine**2 / (cosine**2 + sine**2)

    metrics = {
        "faraday_max_abs_residual": max_abs(faraday_residual),
        "ampere_max_abs_residual": max_abs(ampere_residual),
        "electric_vs_cB_correlation": e_b_correlation,
        "field_vs_normalized_change_inner_product": field_change_dot,
        "electric_magnetic_energy_max_abs_error": max_abs(u_e - u_b),
        "poynting_equals_c_u_max_abs_error": max_abs(poynting - c * u_total),
        "population_axis_max_abs_error_from_ridge": max_abs(population_x - 1.0),
        "coherence_axis_max_abs_error_from_forward_pole": max_abs(coherence_x - 2.0),
        "one_flip_coherence_max_abs_error_from_reverse_pole": max_abs(one_flip_coherence_x),
        "paired_flip_coherency_relative_l2_error": relative_l2(joint_flip_g - original_g, original_g),
        "quadrature_ara_minimum": float(np.min(quadrature_x)),
        "quadrature_ara_maximum": float(np.max(quadrature_x)),
        "quadrature_ara_mean": float(np.mean(quadrature_x)),
    }
    gates = {
        "faraday": metrics["faraday_max_abs_residual"] <= TOLERANCE,
        "ampere_maxwell": metrics["ampere_max_abs_residual"] <= TOLERANCE,
        "raw_E_B_in_phase": abs(e_b_correlation - 1.0) <= TOLERANCE,
        "field_change_quadrature": abs(field_change_dot) <= TOLERANCE,
        "equal_field_energy": metrics["electric_magnetic_energy_max_abs_error"] <= TOLERANCE,
        "poynting_energy_relation": metrics["poynting_equals_c_u_max_abs_error"] <= TOLERANCE,
        "population_ridge": metrics["population_axis_max_abs_error_from_ridge"] <= TOLERANCE,
        "forward_coherence_pole": metrics["coherence_axis_max_abs_error_from_forward_pole"] <= TOLERANCE,
        "one_flip_reverses_coherence_pole": metrics[
            "one_flip_coherence_max_abs_error_from_reverse_pole"
        ]
        <= TOLERANCE,
        "paired_flip_preserves_parent": metrics["paired_flip_coherency_relative_l2_error"] <= TOLERANCE,
        "quadrature_covers_0_2": abs(metrics["quadrature_ara_minimum"]) <= TOLERANCE
        and abs(metrics["quadrature_ara_maximum"] - 2.0) <= TOLERANCE
        and abs(metrics["quadrature_ara_mean"] - 1.0) <= TOLERANCE,
    }
    return {
        "samples": samples,
        "parameters": {"epsilon": epsilon, "mu": mu, "c": c, "k": k, "omega": omega},
        "metrics": metrics,
        "gates": gates,
        "all_pass": all(gates.values()),
    }


def main() -> None:
    rng = np.random.default_rng(SEED)
    sections = {
        "mixed_state_ball": mixed_state_audit(rng),
        "pure_state_surface": pure_state_audit(rng),
        "incoherent_parent": incoherent_parent_audit(rng),
        "coherent_parent": coherent_parent_audit(rng),
        "maxwell_plane_wave": maxwell_plane_wave_audit(),
    }
    all_pass = all(bool(section["all_pass"] if "all_pass" in section else section["pass"])
                   for section in sections.values())
    result = {
        "test_id": "MX9/SCALE-AXIS-ARA-MAXWELL/v1",
        "protocol": "MX9_SCALE_AXIS_ARA_MAXWELL_PROTOCOL_v1_FROZEN.md",
        "seed": SEED,
        "tolerance": TOLERANCE,
        "status": "PASS" if all_pass else "FAIL",
        "sections": sections,
        "all_gates_pass": all_pass,
        "claim_boundary": {
            "exact": (
                "Two-channel coherency states admit a 0-2 projection on every declared axis; "
                "coarse mixtures average by activity and coherent sums require relation cross-terms; "
                "the construction matches an analytic source-free Maxwell plane wave."
            ),
            "not_established": (
                "No universal physical decomposition, privileged axis, cross-scale fractal law, "
                "new electromagnetic prediction, or raw E/B temporal phase offset is established."
            ),
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
