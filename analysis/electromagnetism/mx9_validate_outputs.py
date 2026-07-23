"""Independent validation of MX9 using projector traces and fresh parameters."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "MX9_SCALE_AXIS_ARA_MAXWELL_RESULTS.json"
OUTPUT = HERE / "MX9_SCALE_AXIS_ARA_MAXWELL_VALIDATION.json"
TOL = 1e-12

SIGMA_X = np.asarray([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
SIGMA_Y = np.asarray([[0.0, 1.0j], [-1.0j, 0.0]], dtype=np.complex128)
SIGMA_Z = np.asarray([[-1.0, 0.0], [0.0, 1.0]], dtype=np.complex128)
IDENTITY = np.eye(2, dtype=np.complex128)


def outer(z: np.ndarray) -> np.ndarray:
    return np.einsum("...i,...j->...ij", z, z.conj())


def state_from_traces(g: np.ndarray) -> tuple[float, np.ndarray]:
    total = float(np.real(np.trace(g)))
    rho = g / total
    s = np.asarray(
        [
            np.real(np.trace(rho @ SIGMA_X)),
            np.real(np.trace(rho @ SIGMA_Y)),
            np.real(np.trace(rho @ SIGMA_Z)),
        ]
    )
    return total, s


def projection_from_projector(g: np.ndarray, axis: np.ndarray) -> float:
    total = float(np.real(np.trace(g)))
    operator = axis[0] * SIGMA_X + axis[1] * SIGMA_Y + axis[2] * SIGMA_Z
    projector = 0.5 * (IDENTITY + operator)
    return float(2.0 * np.real(np.trace((g / total) @ projector)))


def randomized_projector_check() -> dict[str, object]:
    rng = np.random.default_rng(20_260_724)
    samples = 4_096
    max_projection_error = 0.0
    max_reversal_error = 0.0
    max_norm_excess = 0.0
    for _ in range(samples):
        z = rng.normal(size=(5, 2)) + 1j * rng.normal(size=(5, 2))
        g = np.sum(outer(z), axis=0)
        _, s = state_from_traces(g)
        axis = rng.normal(size=3)
        axis /= np.linalg.norm(axis)
        direct = projection_from_projector(g, axis)
        vector = 1.0 + float(axis @ s)
        reverse = projection_from_projector(g, -axis)
        max_projection_error = max(max_projection_error, abs(direct - vector))
        max_reversal_error = max(max_reversal_error, abs(reverse - (2.0 - direct)))
        max_norm_excess = max(max_norm_excess, max(0.0, float(np.linalg.norm(s)) - 1.0))
    passed = max(max_projection_error, max_reversal_error, max_norm_excess) <= TOL
    return {
        "samples": samples,
        "projector_vs_vector_max_abs_error": max_projection_error,
        "axis_reversal_max_abs_error": max_reversal_error,
        "state_norm_maximum_excess": max_norm_excess,
        "pass": passed,
    }


def aggregation_check() -> dict[str, object]:
    rng = np.random.default_rng(90_900_009)
    samples = 2_048
    max_incoherent_state_error = 0.0
    max_coherent_matrix_error = 0.0
    for _ in range(samples):
        children = rng.normal(size=(3, 2)) + 1j * rng.normal(size=(3, 2))
        child_g = outer(children)
        totals_and_states = [state_from_traces(g) for g in child_g]
        totals = np.asarray([item[0] for item in totals_and_states])
        states = np.asarray([item[1] for item in totals_and_states])
        mixed_g = np.sum(child_g, axis=0)
        _, mixed_s = state_from_traces(mixed_g)
        expected_s = np.sum(totals[:, None] * states, axis=0) / np.sum(totals)
        max_incoherent_state_error = max(
            max_incoherent_state_error, float(np.max(np.abs(mixed_s - expected_s)))
        )

        coherent_g = outer(np.sum(children, axis=0))
        cross = np.zeros((2, 2), dtype=np.complex128)
        for left in range(3):
            for right in range(3):
                if left != right:
                    cross += np.outer(children[left], children[right].conj())
        reconstructed = mixed_g + cross
        scale = max(float(np.linalg.norm(coherent_g)), np.finfo(float).tiny)
        max_coherent_matrix_error = max(
            max_coherent_matrix_error,
            float(np.linalg.norm(reconstructed - coherent_g)) / scale,
        )
    passed = max(max_incoherent_state_error, max_coherent_matrix_error) <= TOL
    return {
        "samples": samples,
        "incoherent_parent_state_max_abs_error": max_incoherent_state_error,
        "coherent_cross_term_max_relative_error": max_coherent_matrix_error,
        "pass": passed,
    }


def exact_axis_examples() -> dict[str, object]:
    plus = outer(np.asarray([1.0, 1.0], dtype=np.complex128))
    minus = outer(np.asarray([1.0, -1.0], dtype=np.complex128))
    population = np.asarray([0.0, 0.0, 1.0])
    coherence = np.asarray([1.0, 0.0, 0.0])
    population_positions = [
        projection_from_projector(plus, population),
        projection_from_projector(minus, population),
    ]
    coherence_positions = [
        projection_from_projector(plus, coherence),
        projection_from_projector(minus, coherence),
    ]
    parent_position = projection_from_projector(plus + minus, coherence)
    passed = (
        np.allclose(population_positions, [1.0, 1.0], atol=TOL, rtol=0.0)
        and np.allclose(coherence_positions, [2.0, 0.0], atol=TOL, rtol=0.0)
        and abs(parent_position - 1.0) <= TOL
    )
    return {
        "population_positions": population_positions,
        "coherence_positions": coherence_positions,
        "incoherent_parent_coherence_position": parent_position,
        "pass": bool(passed),
    }


def independent_maxwell_check() -> dict[str, object]:
    epsilon = 1.3
    c = 2.1
    mu = 1.0 / (epsilon * c * c)
    k = 0.9
    omega = c * k
    theta = np.linspace(0.0, 2.0 * math.pi, 1_024, endpoint=False)
    e = np.cos(theta)
    b = e / c
    sine = np.sin(theta)
    faraday = omega * sine / c - k * sine
    ampere = omega * sine - c * c * (k * sine / c)
    u_e = epsilon * e * e / 2.0
    u_b = b * b / (2.0 * mu)
    flux = e * b / mu
    total_u = u_e + u_b
    active = np.abs(e) > 1e-10
    pair = np.stack([np.sqrt(epsilon) * e[active], b[active] / np.sqrt(mu)], axis=1)
    pop = []
    coh = []
    reverse = []
    for row in pair:
        g = outer(row.astype(np.complex128))
        pop.append(projection_from_projector(g, np.asarray([0.0, 0.0, 1.0])))
        coh.append(projection_from_projector(g, np.asarray([1.0, 0.0, 0.0])))
        flipped = row.astype(np.complex128).copy()
        flipped[1] *= -1.0
        reverse.append(projection_from_projector(outer(flipped), np.asarray([1.0, 0.0, 0.0])))
    errors = {
        "faraday_max_abs": float(np.max(np.abs(faraday))),
        "ampere_max_abs": float(np.max(np.abs(ampere))),
        "energy_balance_max_abs": float(np.max(np.abs(u_e - u_b))),
        "flux_relation_max_abs": float(np.max(np.abs(flux - c * total_u))),
        "population_ridge_max_abs": float(np.max(np.abs(np.asarray(pop) - 1.0))),
        "forward_coherence_max_abs": float(np.max(np.abs(np.asarray(coh) - 2.0))),
        "reverse_coherence_max_abs": float(np.max(np.abs(np.asarray(reverse)))),
    }
    return {"parameters": {"epsilon": epsilon, "mu": mu, "c": c, "k": k},
            "errors": errors, "pass": max(errors.values()) <= TOL}


def result_record_check(results: dict) -> dict[str, object]:
    sections = results["sections"]
    checks = {
        "top_status_pass": results["status"] == "PASS" and bool(results["all_gates_pass"]),
        "mixed_section_pass": bool(sections["mixed_state_ball"]["all_pass"]),
        "pure_section_pass": bool(sections["pure_state_surface"]["pass"]),
        "incoherent_section_pass": bool(sections["incoherent_parent"]["all_pass"]),
        "coherent_section_pass": bool(sections["coherent_parent"]["all_pass"]),
        "maxwell_section_pass": bool(sections["maxwell_plane_wave"]["all_pass"]),
        "registered_counts": (
            sections["mixed_state_ball"]["samples"] == 20_000
            and sections["pure_state_surface"]["samples"] == 20_000
            and sections["incoherent_parent"]["samples"] == 5_000
            and sections["coherent_parent"]["samples"] == 5_000
            and sections["maxwell_plane_wave"]["samples"] == 4_096
        ),
    }
    return {"checks": checks, "pass": all(checks.values())}


def main() -> None:
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    checks = {
        "saved_result_record": result_record_check(results),
        "fresh_projector_trace_path": randomized_projector_check(),
        "fresh_aggregation_path": aggregation_check(),
        "exact_axis_examples": exact_axis_examples(),
        "fresh_maxwell_parameters": independent_maxwell_check(),
    }
    all_pass = all(bool(item["pass"]) for item in checks.values())
    payload = {
        "validation_id": "MX9/SCALE-AXIS-ARA-MAXWELL/independent-validation/v1",
        "source": RESULTS.name,
        "method": (
            "Independent Pauli-projector trace calculation, fresh random states, direct child-matrix "
            "aggregation, and a plane wave with different constants and sampling."
        ),
        "checks": checks,
        "all_checks_pass": all_pass,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
