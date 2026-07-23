#!/usr/bin/env python3
"""Frozen ARA child-to-parent composition test across three continuity laws."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
PROTOCOL_PATH = HERE / "CHILD_PARENT_COMPOSITION_PROTOCOL_2026-07-23.md"
SUMMARY_CSV = HERE / "ARA_CHILD_PARENT_COMPOSITION_SUMMARY.csv"
SAMPLE_CSV = HERE / "ARA_CHILD_PARENT_COMPOSITION_BOUNDED_SAMPLE.csv"
RESULTS_JSON = HERE / "ARA_CHILD_PARENT_COMPOSITION_RESULTS.json"
ARTIFACT_JSON = HERE / "ARA_CHILD_PARENT_COMPOSITION_REPORT_ARTIFACT.json"

PLANNED_SAMPLES = 4097
ACTIVITY_EPS = 1e-12
PRIMARY_TOL = 5e-12
QUANTUM_CONTINUITY_TOL = 1e-6


def positive(x: np.ndarray) -> np.ndarray:
    return np.maximum(x, 0.0)


def interval_accounts(
    flux_left: np.ndarray, flux_right: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Return non-negative accumulation and release at an oriented interval."""
    accumulation = positive(flux_left) + positive(-flux_right)
    release = positive(-flux_left) + positive(flux_right)
    return accumulation, release


def safe_coordinate(release: np.ndarray, total: np.ndarray) -> np.ndarray:
    output = np.full_like(total, np.nan, dtype=float)
    valid = total > ACTIVITY_EPS
    output[valid] = 2.0 * release[valid] / total[valid]
    return output


def classical_string_flux(x: float | np.ndarray, t: np.ndarray) -> np.ndarray:
    """Energy flux of an analytic left/right wave superposition, rho=T=c=1."""
    right = (
        0.90 * 1.30 * np.cos(1.30 * (x - t) + 0.20)
        + 0.35 * 2.10 * np.cos(2.10 * (x - t) - 0.70)
    )
    left = (
        0.72 * 0.85 * np.cos(0.85 * (x + t) + 0.50)
        + 0.28 * 1.70 * np.cos(1.70 * (x + t) + 1.10)
    )
    return right**2 - left**2


def classical_continuity_residual(x: float, t: np.ndarray) -> np.ndarray:
    right = (
        0.90 * 1.30 * np.cos(1.30 * (x - t) + 0.20)
        + 0.35 * 2.10 * np.cos(2.10 * (x - t) - 0.70)
    )
    right_u = (
        -0.90 * 1.30**2 * np.sin(1.30 * (x - t) + 0.20)
        - 0.35 * 2.10**2 * np.sin(2.10 * (x - t) - 0.70)
    )
    left = (
        0.72 * 0.85 * np.cos(0.85 * (x + t) + 0.50)
        + 0.28 * 1.70 * np.cos(1.70 * (x + t) + 1.10)
    )
    left_v = (
        -0.72 * 0.85**2 * np.sin(0.85 * (x + t) + 0.50)
        - 0.28 * 1.70**2 * np.sin(1.70 * (x + t) + 1.10)
    )
    energy_t = -2.0 * right * right_u + 2.0 * left * left_v
    flux_x = 2.0 * right * right_u - 2.0 * left * left_v
    return energy_t + flux_x


def transmission_components(
    x: float | np.ndarray, t: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    forward = (
        0.85 * np.sin(1.20 * (x - t) + 0.15)
        + 0.40 * np.sin(2.30 * (x - t) - 0.35)
    )
    backward = (
        0.70 * np.cos(0.80 * (x + t) - 0.40)
        + 0.35 * np.sin(1.90 * (x + t) + 0.25)
    )
    return forward, backward


def transmission_flux(x: float | np.ndarray, t: np.ndarray) -> np.ndarray:
    forward, backward = transmission_components(x, t)
    voltage = forward + backward
    current = forward - backward
    return voltage * current


def transmission_continuity_residual(x: float, t: np.ndarray) -> np.ndarray:
    forward, backward = transmission_components(x, t)
    forward_u = (
        0.85 * 1.20 * np.cos(1.20 * (x - t) + 0.15)
        + 0.40 * 2.30 * np.cos(2.30 * (x - t) - 0.35)
    )
    backward_v = (
        -0.70 * 0.80 * np.sin(0.80 * (x + t) - 0.40)
        + 0.35 * 1.90 * np.cos(1.90 * (x + t) + 0.25)
    )
    energy_t = -2.0 * forward * forward_u + 2.0 * backward * backward_v
    power_x = 2.0 * forward * forward_u - 2.0 * backward * backward_v
    return energy_t + power_x


def gaussian_density_current(
    x: float | np.ndarray, t: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Free Gaussian packet in units hbar=m=1."""
    sigma0 = 0.80
    x0 = -1.00
    k0 = 1.30
    sigma_sq = sigma0**2 + t**2 / (4.0 * sigma0**2)
    sigma = np.sqrt(sigma_sq)
    centre = x0 + k0 * t
    z = x - centre
    density = np.exp(-(z**2) / (2.0 * sigma_sq)) / (
        math.sqrt(2.0 * math.pi) * sigma
    )
    spread_velocity = t / (4.0 * sigma0**4 + t**2)
    velocity = k0 + z * spread_velocity
    current = density * velocity
    return density, current


def quantum_flux(x: float | np.ndarray, t: np.ndarray) -> np.ndarray:
    return gaussian_density_current(x, t)[1]


def quantum_fd_continuity_residual() -> float:
    """Independent central-difference check of d_t rho + d_x j."""
    x = np.linspace(-1.5, 2.4, 97)
    t = np.linspace(0.20, 2.40, 97)
    xx, tt = np.meshgrid(x, t, indexing="ij")
    h = 1e-5
    rho_plus, _ = gaussian_density_current(xx, tt + h)
    rho_minus, _ = gaussian_density_current(xx, tt - h)
    _, j_plus = gaussian_density_current(xx + h, tt)
    _, j_minus = gaussian_density_current(xx - h, tt)
    residual = (rho_plus - rho_minus) / (2.0 * h) + (
        j_plus - j_minus
    ) / (2.0 * h)
    return float(np.max(np.abs(residual)))


def evaluate_model(
    *,
    name: str,
    domain: str,
    role: str,
    time: np.ndarray,
    boundaries: tuple[float, float, float],
    flux_function,
    continuity_residual: float,
    holdout: bool,
) -> tuple[dict, list[dict]]:
    left, interface, right = boundaries
    flux_left = np.asarray(flux_function(left, time), dtype=float)
    flux_interface = np.asarray(flux_function(interface, time), dtype=float)
    flux_right = np.asarray(flux_function(right, time), dtype=float)

    a1, r1 = interval_accounts(flux_left, flux_interface)
    a2, r2 = interval_accounts(flux_interface, flux_right)
    t1 = a1 + r1
    t2 = a2 + r2
    x1 = safe_coordinate(r1, t1)
    x2 = safe_coordinate(r2, t2)

    parent_a, parent_r = interval_accounts(flux_left, flux_right)
    parent_total = parent_a + parent_r
    parent_direct = safe_coordinate(parent_r, parent_total)

    internal = np.abs(flux_interface)
    composed_a = a1 + a2 - internal
    composed_r = r1 + r2 - internal
    composed_total = t1 + t2 - 2.0 * internal
    parent_frozen = safe_coordinate(composed_r, composed_total)

    parent_naive = 0.5 * (x1 + x2)
    parent_no_internal = safe_coordinate(r1 + r2, t1 + t2)

    reversed_frozen = safe_coordinate(composed_a, composed_total)
    reversal_target = 2.0 - parent_frozen

    valid = (
        (parent_total > ACTIVITY_EPS)
        & (t1 > ACTIVITY_EPS)
        & (t2 > ACTIVITY_EPS)
        & np.isfinite(parent_direct)
        & np.isfinite(parent_frozen)
        & np.isfinite(parent_naive)
        & np.isfinite(parent_no_internal)
    )

    def metric(values: np.ndarray, kind: str) -> float:
        selected = np.abs(values[valid])
        if kind == "max":
            return float(np.max(selected))
        if kind == "mean":
            return float(np.mean(selected))
        if kind == "p95":
            return float(np.quantile(selected, 0.95))
        raise ValueError(kind)

    frozen_error = parent_frozen - parent_direct
    naive_error = parent_naive - parent_direct
    no_internal_error = parent_no_internal - parent_direct
    reversal_error = reversed_frozen - reversal_target

    valid_count = int(np.sum(valid))
    summary = {
        "model": name,
        "domain": domain,
        "test_role": role,
        "holdout": holdout,
        "planned_samples": int(time.size),
        "valid_samples": valid_count,
        "retention_fraction": valid_count / float(time.size),
        "max_abs_error_frozen": metric(frozen_error, "max"),
        "mean_abs_error_frozen": metric(frozen_error, "mean"),
        "p95_abs_error_frozen": metric(frozen_error, "p95"),
        "mean_abs_error_naive": metric(naive_error, "mean"),
        "mean_abs_error_no_internal": metric(no_internal_error, "mean"),
        "max_abs_orientation_error": metric(reversal_error, "max"),
        "continuity_residual_max": float(continuity_residual),
        "parent_coordinate_min": float(np.min(parent_direct[valid])),
        "parent_coordinate_max": float(np.max(parent_direct[valid])),
        "boundary_left": left,
        "boundary_interface": interface,
        "boundary_right": right,
    }
    summary["naive_to_frozen_mae_ratio"] = summary["mean_abs_error_naive"] / max(
        summary["mean_abs_error_frozen"], 1e-18
    )
    summary["no_internal_to_frozen_mae_ratio"] = summary[
        "mean_abs_error_no_internal"
    ] / max(summary["mean_abs_error_frozen"], 1e-18)

    indices = np.unique(np.linspace(0, time.size - 1, 161, dtype=int))
    rows: list[dict] = []
    for idx in indices:
        if not valid[idx]:
            continue
        rows.append(
            {
                "model": name,
                "domain": domain,
                "test_role": role,
                "sample_index": int(idx),
                "time": float(time[idx]),
                "flux_left": float(flux_left[idx]),
                "flux_interface": float(flux_interface[idx]),
                "flux_right": float(flux_right[idx]),
                "child_1_accumulation": float(a1[idx]),
                "child_1_release": float(r1[idx]),
                "child_1_total": float(t1[idx]),
                "child_1_ara": float(x1[idx]),
                "child_2_accumulation": float(a2[idx]),
                "child_2_release": float(r2[idx]),
                "child_2_total": float(t2[idx]),
                "child_2_ara": float(x2[idx]),
                "internal_handover": float(internal[idx]),
                "parent_accumulation_direct": float(parent_a[idx]),
                "parent_release_direct": float(parent_r[idx]),
                "parent_total_direct": float(parent_total[idx]),
                "parent_ara_direct": float(parent_direct[idx]),
                "parent_ara_frozen": float(parent_frozen[idx]),
                "parent_ara_naive": float(parent_naive[idx]),
                "parent_ara_no_internal": float(parent_no_internal[idx]),
                "abs_error_frozen": float(abs(frozen_error[idx])),
                "abs_error_naive": float(abs(naive_error[idx])),
                "abs_error_no_internal": float(abs(no_internal_error[idx])),
            }
        )
    return summary, rows


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"No rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_artifact(summaries: list[dict], samples: list[dict], results: dict) -> dict:
    summary_rows = []
    error_rows = []
    for row in summaries:
        summary_rows.append(
            {
                "model": row["model"],
                "domain": row["domain"],
                "test_role": row["test_role"],
                "valid_samples": row["valid_samples"],
                "retention_fraction": row["retention_fraction"],
                "max_abs_error_frozen": row["max_abs_error_frozen"],
                "mean_abs_error_frozen": row["mean_abs_error_frozen"],
                "mean_abs_error_naive": row["mean_abs_error_naive"],
                "mean_abs_error_no_internal": row["mean_abs_error_no_internal"],
                "max_abs_orientation_error": row["max_abs_orientation_error"],
                "continuity_residual_max": row["continuity_residual_max"],
                "parent_coordinate_min": row["parent_coordinate_min"],
                "parent_coordinate_max": row["parent_coordinate_max"],
            }
        )
        methods = [
            ("Frozen operator", row["mean_abs_error_frozen"]),
            ("Naive child mean", row["mean_abs_error_naive"]),
            ("Internal transfer retained", row["mean_abs_error_no_internal"]),
        ]
        for method, error in methods:
            error_rows.append(
                {
                    "model": row["model"],
                    "domain": row["domain"],
                    "method": method,
                    "mean_absolute_error": error,
                    "correct_decimal_orders": -math.log10(max(error, 1e-18)),
                    "valid_samples": row["valid_samples"],
                    "test_role": row["test_role"],
                }
            )

    quantum_samples = [r for r in samples if r["test_role"] == "Holdout"]
    trace_indices = np.unique(
        np.linspace(0, len(quantum_samples) - 1, min(121, len(quantum_samples)), dtype=int)
    )
    trace_rows = []
    for rank, idx in enumerate(trace_indices):
        row = quantum_samples[int(idx)]
        series_values = [
            ("Direct parent", row["parent_ara_direct"]),
            ("Frozen operator", row["parent_ara_frozen"]),
            ("Naive child mean", row["parent_ara_naive"]),
            ("Internal transfer retained", row["parent_ara_no_internal"]),
        ]
        for series, value in series_values:
            trace_rows.append(
                {
                    "trace_order": rank,
                    "time": row["time"],
                    "ara_coordinate": value,
                    "series": series,
                    "model": row["model"],
                    "internal_handover": row["internal_handover"],
                    "direct_parent_activity": row["parent_total_direct"],
                }
            )

    metrics = [
        {
            "models_passed": results["models_passed"],
            "models_total": results["models_total"],
            "models_passed_text": (
                f"{results['models_passed']} / {results['models_total']}"
            ),
            "max_frozen_error": results["max_frozen_error"],
            "max_frozen_error_text": f"{results['max_frozen_error']:.3e}",
            "smallest_control_mae": results["smallest_control_mae"],
            "smallest_control_mae_text": f"{results['smallest_control_mae']:.6f}",
            "quantum_holdout_max_error": results["quantum_holdout_max_error"],
            "quantum_holdout_max_error_text": (
                f"{results['quantum_holdout_max_error']:.3e}"
            ),
        }
    ]

    source = {
        "id": "src-child-parent-composition",
        "label": "Frozen ARA child-parent composition test",
        "path": "analysis/physics_ladder/ara_child_parent_composition_test.py",
        "query": {
            "engine": "portable-snapshot",
            "language": "sql",
            "description": (
                "Deterministic analytic classical-wave, transmission-line and "
                "free-Gaussian probability-current calculations produced by the "
                "named Python source, then selected from the bounded report snapshot."
            ),
            "sql": (
                "SELECT * FROM snapshot.headline_metrics; "
                "SELECT * FROM snapshot.model_summary ORDER BY model; "
                "SELECT * FROM snapshot.method_errors ORDER BY model, method; "
                "SELECT * FROM snapshot.quantum_trace ORDER BY time, series;"
            ),
            "tables_used": [
                "analysis/physics_ladder/ARA_CHILD_PARENT_COMPOSITION_SUMMARY.csv",
                "analysis/physics_ladder/ARA_CHILD_PARENT_COMPOSITION_BOUNDED_SAMPLE.csv",
            ],
            "filters": [
                "4,097 deterministic time samples per model",
                "exclude only parent or child activity at or below 1e-12",
                "no smoothing, fitting, Fourier decomposition or learned coefficients",
                "quantum Gaussian packet retained as holdout",
            ],
            "metric_definitions": [
                "x_i = 2 R_i / (A_i + R_i)",
                "I = absolute signed flux through the shared child interface",
                "x_parent = 2(sum R_i - I)/(sum T_i - 2I)",
                "errors compare predicted parent ARA with direct outer-boundary ARA",
            ],
        },
    }

    charts = [
        {
            "id": "method-error-orders",
            "title": "Correct decimal orders by model and composition method",
            "subtitle": (
                "Higher is better; values are -log10(mean absolute ARA error) "
                "over each model's valid samples"
            ),
            "intent": "comparison",
            "question": "Does internal-handover removal matter relative to plausible controls?",
            "rationale": (
                "A grouped bar comparison makes the machine-precision reconstruction "
                "and control gaps visible on one honest scale."
            ),
            "comparisonContext": {
                "grain": "one model-method result",
                "unit": "correct decimal orders",
                "semanticFamily": "reconstruction accuracy",
            },
            "type": "bar",
            "dataset": "method_errors",
            "sourceId": source["id"],
            "encodings": {
                "x": {
                    "field": "model",
                    "type": "nominal",
                    "label": "Physical model",
                },
                "y": {
                    "field": "correct_decimal_orders",
                    "type": "quantitative",
                    "label": "Correct decimal orders",
                },
                "color": {
                    "field": "method",
                    "type": "nominal",
                    "label": "Composition method",
                },
                "tooltip": [
                    {"field": "model", "type": "text", "label": "Model"},
                    {"field": "method", "type": "text", "label": "Method"},
                    {
                        "field": "mean_absolute_error",
                        "type": "quantitative",
                        "label": "Mean absolute error",
                    },
                    {
                        "field": "valid_samples",
                        "type": "quantitative",
                        "label": "Valid samples",
                    },
                ],
            },
            "options": {"orientation": "vertical", "grouping": "grouped"},
            "layout": "full",
            "maxRows": len(error_rows),
        },
        {
            "id": "quantum-holdout-trace",
            "title": "Quantum holdout parent ARA by time",
            "subtitle": (
                "Direct parent, frozen operator and two controls over the bounded "
                "free-Gaussian holdout sample"
            ),
            "intent": "trend",
            "question": "Does the frozen classical/EM operator transfer unchanged to probability current?",
            "rationale": (
                "The time trace reveals exact overlap and where controls distort the "
                "parent reading."
            ),
            "comparisonContext": {
                "grain": "one deterministic holdout time and method",
                "unit": "ARA coordinate on 0-2",
                "semanticFamily": "holdout reconstruction",
            },
            "type": "line",
            "dataset": "quantum_trace",
            "sourceId": source["id"],
            "encodings": {
                "x": {"field": "time", "type": "quantitative", "label": "Time"},
                "y": {
                    "field": "ara_coordinate",
                    "type": "quantitative",
                    "label": "Parent ARA",
                },
                "color": {
                    "field": "series",
                    "type": "nominal",
                    "label": "Reading",
                },
                "tooltip": [
                    {"field": "time", "type": "quantitative", "label": "Time"},
                    {
                        "field": "ara_coordinate",
                        "type": "quantitative",
                        "label": "ARA",
                    },
                    {"field": "series", "type": "text", "label": "Reading"},
                    {
                        "field": "internal_handover",
                        "type": "quantitative",
                        "label": "Internal handover",
                    },
                ],
            },
            "layout": "full",
            "maxRows": len(trace_rows),
        },
    ]

    cards = [
        {
            "id": "models-passed",
            "dataset": "headline_metrics",
            "sourceId": source["id"],
            "metrics": [
                {"label": "Passed", "field": "models_passed_text"},
            ],
        },
        {
            "id": "max-frozen-error",
            "dataset": "headline_metrics",
            "sourceId": source["id"],
            "metrics": [
                {"label": "Max |error|", "field": "max_frozen_error_text"},
            ],
        },
        {
            "id": "smallest-control-error",
            "dataset": "headline_metrics",
            "sourceId": source["id"],
            "metrics": [
                {"label": "Control MAE", "field": "smallest_control_mae_text"},
            ],
        },
        {
            "id": "quantum-holdout-error",
            "dataset": "headline_metrics",
            "sourceId": source["id"],
            "metrics": [
                {"label": "Holdout |error|", "field": "quantum_holdout_max_error_text"},
            ],
        },
    ]

    tables = [
        {
            "id": "model-summary",
            "title": "Model-level reconstruction and control results",
            "subtitle": "All planned systems; errors are dimensionless ARA-coordinate differences",
            "dataset": "model_summary",
            "defaultSort": {"field": "model", "direction": "asc"},
            "density": "spacious",
            "sourceId": source["id"],
            "layout": "full",
            "columns": [
                {"field": "model", "label": "Model", "type": "text"},
                {"field": "test_role", "label": "Role", "type": "text"},
                {
                    "field": "valid_samples",
                    "label": "Valid samples",
                    "type": "number",
                },
                {
                    "field": "max_abs_error_frozen",
                    "label": "Frozen max error",
                    "type": "number",
                },
                {
                    "field": "mean_abs_error_naive",
                    "label": "Naive MAE",
                    "type": "number",
                },
                {
                    "field": "mean_abs_error_no_internal",
                    "label": "No-closure MAE",
                    "type": "number",
                },
                {
                    "field": "continuity_residual_max",
                    "label": "Continuity residual",
                    "type": "number",
                },
            ],
        }
    ]

    title = "ARA child-to-parent composition across three continuity laws"
    blocks = [
        {
            "id": "title",
            "type": "markdown",
            "layout": "full",
            "body": f"# {title}",
        },
        {
            "id": "technical-summary",
            "type": "markdown",
            "layout": "full",
            "sourceId": source["id"],
            "body": (
                "## The frozen boundary operator reconstructed every parent to "
                "floating-point precision\n\nThe unchanged rule passed the classical "
                "mechanical wave, electromagnetic transmission-line verification and "
                "the quantum probability-current holdout. This establishes an exact "
                "shared boundary-accounting reparameterisation. It does not establish "
                "new dynamics or prove universal fractality."
            ),
        },
        {
            "id": "headline-metrics",
            "type": "metric-strip",
            "layout": "full",
            "cardIds": [
                "models-passed",
                "max-frozen-error",
                "smallest-control-error",
                "quantum-holdout-error",
            ],
            "dataset": "headline_metrics",
        },
        {
            "id": "control-finding",
            "type": "markdown",
            "layout": "full",
            "sourceId": source["id"],
            "body": (
                "## Removing the child interface is necessary at the parent boundary\n\n"
                "The naive mean and the activity-weighted version that retains the "
                "interface both produce finite errors. The frozen rule succeeds because "
                "the interface is a release for one child and an accumulation for the "
                "other, but neither enters nor leaves their enclosing parent."
            ),
        },
        {
            "id": "error-chart",
            "type": "chart",
            "layout": "full",
            "chartId": "method-error-orders",
        },
        {
            "id": "holdout-finding",
            "type": "markdown",
            "layout": "full",
            "sourceId": source["id"],
            "body": (
                "## The unchanged operator transferred to the quantum holdout\n\n"
                "The quantum calculation uses raw analytic probability current. The "
                "frozen prediction lies on the direct outer-boundary account while both "
                "controls wander away. This is expected from continuity and is therefore "
                "a cross-domain consistency result, not a derivation of quantum mechanics."
            ),
        },
        {
            "id": "holdout-chart",
            "type": "chart",
            "layout": "full",
            "chartId": "quantum-holdout-trace",
        },
        {
            "id": "definitions",
            "type": "markdown",
            "layout": "full",
            "body": (
                "## Scope and definitions\n\nEach child uses `x=2R/(A+R)`, where "
                "`A` is inward boundary activity and `R` is outward boundary activity. "
                "The shared interface magnitude `I` is counted once in each direction "
                "at child grain and removed from both channels at parent grain. Samples "
                "with zero total activity have no defined diameter position."
            ),
        },
        {
            "id": "summary-table",
            "type": "table",
            "layout": "full",
            "tableId": "model-summary",
        },
        {
            "id": "methodology",
            "type": "markdown",
            "layout": "full",
            "body": (
                "## Frozen design and validation\n\nThe protocol fixed 4,097 time "
                "samples per system, oriented interval accounting, one parent operator, "
                "two incorrect controls and machine-precision pass criteria before the "
                "comparison. The models are analytic and unfiltered. An independent "
                "validator recomputes the operator on randomized signed boundary fluxes "
                "and checks the saved results."
            ),
        },
        {
            "id": "limitations",
            "type": "markdown",
            "layout": "full",
            "body": (
                "## The pass formalizes scale accounting but does not yet predict an "
                "unknown term\n\nAll three systems were deliberately selected because "
                "they obey source-free local continuity. The frozen operator is the "
                "correct finite-volume boundary identity in ARA coordinates. Its exact "
                "success is meaningful for formal coherence, but it cannot by itself "
                "distinguish ARA from ordinary conservation accounting."
            ),
        },
        {
            "id": "next-step",
            "type": "markdown",
            "layout": "full",
            "body": (
                "## Next test: hide an `Other` term prospectively\n\nIntroduce a known "
                "damper, conductor or source in an otherwise matched system. Freeze the "
                "observed child accounts, hide the source label and require the residual "
                "to recover its sign, location and magnitude before revealing the native "
                "term."
            ),
        },
        {
            "id": "further-questions",
            "type": "markdown",
            "layout": "full",
            "body": (
                "## Further questions\n\nDoes the same operator remain sufficient when "
                "the relation stores energy or probability rather than transferring it "
                "instantaneously? Can the residual distinguish relation storage from a "
                "true external leak?"
            ),
        },
    ]

    return {
        "surface": "report",
        "manifest": {
            "version": 1,
            "surface": "report",
            "title": title,
            "description": (
                "Frozen cross-domain test of one ARA child-to-parent boundary operator."
            ),
            "generatedAt": "2026-07-23T00:00:00+10:00",
            "sources": [source],
            "cards": cards,
            "charts": charts,
            "tables": tables,
            "blocks": blocks,
        },
        "snapshot": {
            "version": 1,
            "generatedAt": "2026-07-23T00:00:00+10:00",
            "status": "ready",
            "datasets": {
                "headline_metrics": metrics,
                "model_summary": summary_rows,
                "method_errors": error_rows,
                "quantum_trace": trace_rows,
            },
        },
        "sources": [source],
    }


def main() -> None:
    classical_time = np.linspace(0.0, 30.0, PLANNED_SAMPLES)
    em_time = np.linspace(0.0, 25.0, PLANNED_SAMPLES)
    quantum_time = np.linspace(0.05, 2.50, PLANNED_SAMPLES)

    models = [
        {
            "name": "Classical string energy",
            "domain": "Newton/Hamilton continuum",
            "role": "Operator establishment",
            "time": classical_time,
            "boundaries": (-1.40, 0.20, 1.70),
            "flux_function": classical_string_flux,
            "continuity_residual": float(
                np.max(
                    np.abs(
                        classical_continuity_residual(
                            0.37, np.linspace(0.0, 30.0, 1025)
                        )
                    )
                )
            ),
            "holdout": False,
        },
        {
            "name": "Lossless transmission line",
            "domain": "Maxwell/Poynting analogue",
            "role": "Verification",
            "time": em_time,
            "boundaries": (-1.10, 0.35, 1.90),
            "flux_function": transmission_flux,
            "continuity_residual": float(
                np.max(
                    np.abs(
                        transmission_continuity_residual(
                            -0.23, np.linspace(0.0, 25.0, 1025)
                        )
                    )
                )
            ),
            "holdout": False,
        },
        {
            "name": "Free Gaussian probability",
            "domain": "Schrodinger probability continuity",
            "role": "Holdout",
            "time": quantum_time,
            "boundaries": (-1.80, 0.30, 2.20),
            "flux_function": quantum_flux,
            "continuity_residual": quantum_fd_continuity_residual(),
            "holdout": True,
        },
    ]

    summaries: list[dict] = []
    bounded_samples: list[dict] = []
    for model in models:
        summary, rows = evaluate_model(**model)
        summaries.append(summary)
        bounded_samples.extend(rows)

    models_passed = sum(
        int(
            row["retention_fraction"] >= 0.99
            and row["max_abs_error_frozen"] <= PRIMARY_TOL
            and row["max_abs_orientation_error"] <= PRIMARY_TOL
            and row["mean_abs_error_naive"] > row["mean_abs_error_frozen"]
            and row["mean_abs_error_no_internal"] > row["mean_abs_error_frozen"]
            and (
                row["continuity_residual_max"] <= QUANTUM_CONTINUITY_TOL
                if row["holdout"]
                else row["continuity_residual_max"] <= PRIMARY_TOL
            )
        )
        for row in summaries
    )
    quantum_summary = next(row for row in summaries if row["holdout"])
    results = {
        "status": "passed" if models_passed == len(summaries) else "failed",
        "protocol_sha256": hashlib.sha256(PROTOCOL_PATH.read_bytes()).hexdigest(),
        "models_passed": models_passed,
        "models_total": len(summaries),
        "planned_samples_per_model": PLANNED_SAMPLES,
        "valid_samples_total": sum(row["valid_samples"] for row in summaries),
        "max_frozen_error": max(
            row["max_abs_error_frozen"] for row in summaries
        ),
        "max_orientation_error": max(
            row["max_abs_orientation_error"] for row in summaries
        ),
        "smallest_control_mae": min(
            min(row["mean_abs_error_naive"], row["mean_abs_error_no_internal"])
            for row in summaries
        ),
        "quantum_holdout_max_error": quantum_summary["max_abs_error_frozen"],
        "primary_tolerance": PRIMARY_TOL,
        "quantum_continuity_tolerance": QUANTUM_CONTINUITY_TOL,
        "operator": (
            "x_parent = 2*(sum(release_i)-I)/(sum(activity_i)-2*I)"
        ),
        "interpretation": (
            "Exact common boundary-accounting reparameterisation of three "
            "source-free continuity systems; not new dynamics or proof of universality."
        ),
        "model_summaries": summaries,
    }

    write_csv(SUMMARY_CSV, summaries)
    write_csv(SAMPLE_CSV, bounded_samples)
    RESULTS_JSON.write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    artifact = build_artifact(summaries, bounded_samples, results)
    ARTIFACT_JSON.write_text(
        json.dumps(artifact, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
