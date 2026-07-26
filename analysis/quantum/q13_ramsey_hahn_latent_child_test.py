#!/usr/bin/env python3
"""Run the frozen Q13 Ramsey/Hahn latent-child test."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
INPUT = HERE / "Q11_VISIBLE_UNRESOLVED_INFORMATION3_RECORDS.csv"
PROTOCOL = HERE / "Q13_RAMSEY_HAHN_LATENT_CHILD_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q13_RAMSEY_HAHN_LATENT_CHILD_PROTOCOL_v1_FROZEN.sha256"
CHILDREN_CSV = HERE / "Q13_RAMSEY_HAHN_FOUR_CHILDREN.csv"
FOLDS_CSV = HERE / "Q13_RAMSEY_HAHN_LATENT_FOLDS.csv"
CANDIDATES_CSV = HERE / "Q13_RAMSEY_HAHN_LATENT_CANDIDATES.csv"
GATES_CSV = HERE / "Q13_RAMSEY_HAHN_LATENT_GATES.csv"
RESULTS_JSON = HERE / "Q13_RAMSEY_HAHN_LATENT_RESULTS.json"
VALIDATION_INPUT_JSON = HERE / "Q13_RAMSEY_HAHN_NULL_SUMMARY.json"
FIGURE_SVG = HERE / "Q13_RAMSEY_HAHN_LATENT_GEOMETRY.svg"

STATES = ("Phi-plus", "Phi-minus", "Psi-plus", "Psi-minus")
CANDIDATES = ("R_A", "R_B", "H_A", "H_B")
AXES = ("amplitude", "direction")
COLORS = {
    "R_A": "#2F6B9A",
    "R_B": "#7EA6C6",
    "H_A": "#D17A22",
    "H_B": "#E8A45A",
}
PERMUTATIONS = 999
SEED = 27013


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_protocol() -> str:
    expected = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    observed = digest(PROTOCOL)
    if expected != observed:
        raise RuntimeError(f"Q13 protocol mismatch: {observed} != {expected}")
    return observed


def offdiag_energy(matrix: np.ndarray) -> float:
    return float(sum(matrix[i, j] ** 2 for i in range(3) for j in range(i + 1, 3)))


def sign_agreement(observed: np.ndarray, predicted: np.ndarray) -> float:
    matches = []
    for i in range(3):
        for j in range(i + 1, 3):
            left, right = float(observed[i, j]), float(predicted[i, j])
            if abs(left) <= 1e-15 or abs(right) <= 1e-15:
                matches.append(False)
            else:
                matches.append(math.copysign(1.0, left) == math.copysign(1.0, right))
    return float(np.mean(matches))


def evaluate_candidate(
    matrix: np.ndarray,
    state_labels: np.ndarray,
    candidate_index: int,
    hidden_override: np.ndarray | None = None,
) -> list[dict[str, object]]:
    hidden = matrix[:, candidate_index] if hidden_override is None else hidden_override
    visible_indices = [index for index in range(4) if index != candidate_index]
    folds: list[dict[str, object]] = []
    for heldout in STATES:
        train = state_labels != heldout
        test = state_labels == heldout
        train_design = np.column_stack([np.ones(int(np.sum(train))), hidden[train]])
        test_design = np.column_stack([np.ones(int(np.sum(test))), hidden[test]])
        beta_columns = []
        residual_columns = []
        for visible_index in visible_indices:
            coefficients, *_ = np.linalg.lstsq(
                train_design, matrix[train, visible_index], rcond=None
            )
            beta_columns.append(float(coefficients[1]))
            predicted = test_design @ coefficients
            residual_columns.append(matrix[test, visible_index] - predicted)
        visible_test = matrix[test][:, visible_indices]
        residual_test = np.column_stack(residual_columns)
        before = np.cov(visible_test, rowvar=False, ddof=1)
        after = np.cov(residual_test, rowvar=False, ddof=1)
        before_energy = offdiag_energy(before)
        after_energy = offdiag_energy(after)
        reduction = (
            1.0 - after_energy / before_energy if before_energy > 1e-18 else float("nan")
        )
        removed = before - after
        singular = np.linalg.svd(removed, compute_uv=False)
        singular_energy = singular**2
        rank_one_share = float(
            singular_energy[0] / np.sum(singular_energy)
            if np.sum(singular_energy) > 0
            else 0.0
        )
        slopes = np.array(beta_columns)
        induced = np.outer(slopes, slopes) * float(np.var(hidden[test], ddof=1))
        folds.append(
            {
                "heldout_state": heldout,
                "train_rows": int(np.sum(train)),
                "test_rows": int(np.sum(test)),
                "before_offdiag_energy": before_energy,
                "after_offdiag_energy": after_energy,
                "reduction": reduction,
                "rank_one_share": rank_one_share,
                "sign_agreement": sign_agreement(removed, induced),
                "visible_children": "/".join(CANDIDATES[index] for index in visible_indices),
            }
        )
    return folds


def summarize_folds(folds: list[dict[str, object]]) -> dict[str, float]:
    return {
        "median_reduction": float(np.median([float(row["reduction"]) for row in folds])),
        "mean_reduction": float(np.mean([float(row["reduction"]) for row in folds])),
        "median_rank_one_share": float(
            np.median([float(row["rank_one_share"]) for row in folds])
        ),
        "median_sign_agreement": float(
            np.median([float(row["sign_agreement"]) for row in folds])
        ),
    }


def choose_candidate(candidate_summaries: dict[str, dict[str, dict[str, float]]]) -> str:
    scores = {
        candidate: 0.5
        * (
            candidate_summaries[candidate]["amplitude"]["median_reduction"]
            + candidate_summaries[candidate]["direction"]["median_reduction"]
        )
        for candidate in CANDIDATES
    }
    return sorted(CANDIDATES, key=lambda candidate: (-scores[candidate], candidate))[0]


def p_value(observed: float, null_values: list[float]) -> float:
    return (1 + sum(value >= observed for value in null_values)) / (
        len(null_values) + 1
    )


def add_gate(
    gates: list[dict[str, object]],
    gate_id: str,
    description: str,
    passed: bool,
    value: object,
) -> None:
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, dict):
        value = {
            key: item.item() if isinstance(item, np.generic) else item
            for key, item in value.items()
        }
    gates.append(
        {
            "gate_id": gate_id,
            "description": description,
            "passed": bool(passed),
            "value": value,
        }
    )


def txt(parts: list[str], x: float, y: float, text: str, css: str = "label") -> None:
    parts.append(f'<text x="{x:.1f}" y="{y:.1f}" class="{css}">{text}</text>')


def build_svg(
    candidate_summaries: dict[str, dict[str, dict[str, float]]],
    selected: str,
    fold_rows: list[dict[str, object]],
    null_summary: dict[str, object],
) -> None:
    width, height = 1500, 1060
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        "text{font-family:Arial,sans-serif;fill:#17212B}.title{font-size:27px;font-weight:700}.subtitle{font-size:13px;fill:#405164}.paneltitle{font-size:19px;font-weight:700}.axis{font-size:12px;fill:#405164}.tick{font-size:11px;fill:#566573}.label{font-size:12px}.small{font-size:10px;fill:#566573}",
        "</style>",
        '<rect width="1500" height="1060" fill="#FFFFFF"/>',
    ]
    txt(parts, 52, 44, "One latent child projected into three visible relations", "title")
    txt(
        parts,
        52,
        69,
        "Q13: leave-one-Bell-identity-out covariance removal; matched ordinal Ramsey/Hahn stages",
        "subtitle",
    )

    left_x, top_y, panel_w, panel_h = 50, 95, 680, 500
    parts.append(
        f'<rect x="{left_x}" y="{top_y}" width="{panel_w}" height="{panel_h}" rx="14" fill="#FAFBFC" stroke="#D6DEE6"/>'
    )
    txt(parts, left_x + 22, top_y + 33, "Median visible covariance reduction", "paneltitle")
    txt(parts, left_x + 22, top_y + 55, "Higher is better; negative values mean conditioning added relation energy", "subtitle")
    plot_left, plot_top = left_x + 190, top_y + 90
    plot_w, plot_h = panel_w - 235, panel_h - 140
    values = [
        candidate_summaries[candidate][axis]["median_reduction"]
        for candidate in CANDIDATES
        for axis in AXES
    ]
    minimum = min(-0.25, min(values) * 1.1)
    maximum = max(0.25, max(values) * 1.1)
    zero_x = plot_left + (0 - minimum) / (maximum - minimum) * plot_w
    parts.append(
        f'<line x1="{zero_x}" y1="{plot_top-12}" x2="{zero_x}" y2="{plot_top+plot_h}" stroke="#273746"/>'
    )
    for candidate_index, candidate in enumerate(CANDIDATES):
        base_y = plot_top + candidate_index * 82
        txt(parts, left_x + 24, base_y + 27, candidate, "label")
        if candidate == selected:
            txt(parts, left_x + 76, base_y + 27, "selected", "small")
        for axis_index, axis in enumerate(AXES):
            value = candidate_summaries[candidate][axis]["median_reduction"]
            xx = plot_left + (value - minimum) / (maximum - minimum) * plot_w
            y = base_y + axis_index * 28
            start = min(zero_x, xx)
            width_bar = max(1.2, abs(xx - zero_x))
            opacity = 0.95 if axis == "amplitude" else 0.55
            parts.append(
                f'<rect x="{start:.2f}" y="{y}" width="{width_bar:.2f}" height="19" rx="2" fill="{COLORS[candidate]}" opacity="{opacity}"/>'
            )
            label_x = xx + 6 if value >= 0 else xx - 48
            txt(parts, label_x, y + 14, f"{value:+.3f}", "small")
    txt(parts, plot_left, top_y + panel_h - 24, f"axis range {minimum:.2f} to {maximum:.2f}", "axis")
    txt(parts, plot_left + 175, top_y + panel_h - 24, "solid = amplitude / light = direction", "axis")

    right_x = 770
    parts.append(
        f'<rect x="{right_x}" y="{top_y}" width="{panel_w}" height="{panel_h}" rx="14" fill="#FAFBFC" stroke="#D6DEE6"/>'
    )
    txt(parts, right_x + 22, top_y + 33, f"Selected candidate: {selected}", "paneltitle")
    txt(parts, right_x + 22, top_y + 55, "Held-out Bell-state diagnostics by axis", "subtitle")
    selected_rows = [
        row for row in fold_rows if row["candidate"] == selected
    ]
    headers = ("axis", "held out", "reduction", "rank-one", "sign")
    x_positions = (right_x + 25, right_x + 140, right_x + 285, right_x + 410, right_x + 535)
    for x, header in zip(x_positions, headers):
        txt(parts, x, top_y + 95, header, "axis")
    row_index = 0
    for axis in AXES:
        for state in STATES:
            row = next(
                item
                for item in selected_rows
                if item["axis"] == axis and item["heldout_state"] == state
            )
            yy = top_y + 125 + row_index * 39
            if row_index % 2 == 0:
                parts.append(
                    f'<rect x="{right_x+18}" y="{yy-19}" width="{panel_w-36}" height="32" fill="#F0F4F7"/>'
                )
            txt(parts, x_positions[0], yy, axis, "label")
            txt(parts, x_positions[1], yy, state, "label")
            txt(parts, x_positions[2], yy, f"{float(row['reduction']):+.3f}", "label")
            txt(parts, x_positions[3], yy, f"{float(row['rank_one_share']):.3f}", "label")
            txt(parts, x_positions[4], yy, f"{float(row['sign_agreement']):.3f}", "label")
            row_index += 1

    bottom_y = 625
    parts.append(
        f'<rect x="50" y="{bottom_y}" width="1400" height="375" rx="14" fill="#FAFBFC" stroke="#D6DEE6"/>'
    )
    txt(parts, 72, bottom_y + 34, "Selection-corrected permutation comparison", "paneltitle")
    txt(
        parts,
        72,
        bottom_y + 57,
        "Null shuffles each candidate within Bell identity, preserving its values but breaking aligned child relations",
        "subtitle",
    )
    selected_summary = candidate_summaries[selected]
    rows = [
        ("amplitude reduction", selected_summary["amplitude"]["median_reduction"], float(null_summary["p_amplitude"]), float(null_summary["null_amplitude_q99"])),
        ("direction reduction", selected_summary["direction"]["median_reduction"], float(null_summary["p_direction"]), float(null_summary["null_direction_q95"])),
        ("composite score", float(null_summary["observed_composite"]), float(null_summary["p_composite"]), float(null_summary["null_composite_q95"])),
    ]
    for index, (label, observed, pval, threshold) in enumerate(rows):
        yy = bottom_y + 105 + index * 70
        txt(parts, 90, yy, label, "label")
        txt(parts, 360, yy, f"observed {observed:+.3f}", "label")
        txt(parts, 610, yy, f"null reference {threshold:+.3f}", "label")
        txt(parts, 890, yy, f"p = {pval:.4f}", "label")
    txt(
        parts,
        90,
        bottom_y + 325,
        "This is a structural matched-stage test; it does not observe a pulse-resolved Ramsey-to-Hahn time handoff.",
        "subtitle",
    )
    parts.append("</svg>")
    FIGURE_SVG.write_text("\n".join(parts), encoding="utf-8")


def run() -> dict[str, object]:
    protocol_hash = verify_protocol()
    with INPUT.open(newline="", encoding="utf-8") as handle:
        source = list(csv.DictReader(handle))
    source_by = {
        (row["condition"], row["state"], int(row["wait_index"])): row
        for row in source
    }
    data_ok = len(source) == 88 and len(source_by) == 88
    child_rows: list[dict[str, object]] = []
    for state in STATES:
        for wait_index in range(11):
            ramsey = source_by[("Ramsey", state, wait_index)]
            hahn = source_by[("Hahn", state, wait_index)]
            row = {
                "state": state,
                "wait_index": wait_index,
                "ramsey_wait_us": float(ramsey["wait_us"]),
                "hahn_wait_us": float(hahn["wait_us"]),
                "R_A_amplitude": float(ramsey["visible_x"]) - 1.0,
                "R_A_direction": float(ramsey["visible_y"]) - 1.0,
                "R_B_amplitude": float(ramsey["target_x"]) - 1.0,
                "R_B_direction": float(ramsey["target_y"]) - 1.0,
                "H_A_amplitude": float(hahn["visible_x"]) - 1.0,
                "H_A_direction": float(hahn["visible_y"]) - 1.0,
                "H_B_amplitude": float(hahn["target_x"]) - 1.0,
                "H_B_direction": float(hahn["target_y"]) - 1.0,
            }
            data_ok = bool(
                data_ok
                and all(math.isfinite(float(value)) for key, value in row.items() if key not in ("state",))
            )
            child_rows.append(row)
    state_labels = np.array([str(row["state"]) for row in child_rows])
    matrices = {
        axis: np.array(
            [
                [float(row[f"{candidate}_{axis}"]) for candidate in CANDIDATES]
                for row in child_rows
            ]
        )
        for axis in AXES
    }

    all_folds: list[dict[str, object]] = []
    summaries: dict[str, dict[str, dict[str, float]]] = {
        candidate: {} for candidate in CANDIDATES
    }
    for candidate_index, candidate in enumerate(CANDIDATES):
        for axis in AXES:
            folds = evaluate_candidate(
                matrices[axis], state_labels, candidate_index
            )
            summaries[candidate][axis] = summarize_folds(folds)
            for row in folds:
                all_folds.append(
                    {"candidate": candidate, "axis": axis, **row}
                )
    selected = choose_candidate(summaries)
    selected_index = CANDIDATES.index(selected)
    observed_amp = summaries[selected]["amplitude"]["median_reduction"]
    observed_dir = summaries[selected]["direction"]["median_reduction"]
    observed_composite = 0.5 * (observed_amp + observed_dir)

    fold_winners = {}
    for heldout in STATES:
        scores = {}
        for candidate in CANDIDATES:
            amp = next(
                float(row["reduction"])
                for row in all_folds
                if row["candidate"] == candidate
                and row["axis"] == "amplitude"
                and row["heldout_state"] == heldout
            )
            direction = next(
                float(row["reduction"])
                for row in all_folds
                if row["candidate"] == candidate
                and row["axis"] == "direction"
                and row["heldout_state"] == heldout
            )
            scores[candidate] = 0.5 * (amp + direction)
        fold_winners[heldout] = sorted(
            CANDIDATES, key=lambda candidate: (-scores[candidate], candidate)
        )[0]
    selected_wins = sum(winner == selected for winner in fold_winners.values())

    rng = np.random.default_rng(SEED)
    null_amp_max: list[float] = []
    null_dir_max: list[float] = []
    null_composite_max: list[float] = []
    state_indices = {
        state: np.where(state_labels == state)[0] for state in STATES
    }
    for _ in range(PERMUTATIONS):
        candidate_scores: dict[str, dict[str, float]] = {}
        for candidate_index, candidate in enumerate(CANDIDATES):
            permutations = {
                state: rng.permutation(indices)
                for state, indices in state_indices.items()
            }
            candidate_scores[candidate] = {}
            for axis in AXES:
                hidden = matrices[axis][:, candidate_index].copy()
                permuted = hidden.copy()
                for state, indices in state_indices.items():
                    permuted[indices] = hidden[permutations[state]]
                folds = evaluate_candidate(
                    matrices[axis],
                    state_labels,
                    candidate_index,
                    hidden_override=permuted,
                )
                candidate_scores[candidate][axis] = summarize_folds(folds)[
                    "median_reduction"
                ]
        null_amp_max.append(
            max(candidate_scores[candidate]["amplitude"] for candidate in CANDIDATES)
        )
        null_dir_max.append(
            max(candidate_scores[candidate]["direction"] for candidate in CANDIDATES)
        )
        null_composite_max.append(
            max(
                0.5
                * (
                    candidate_scores[candidate]["amplitude"]
                    + candidate_scores[candidate]["direction"]
                )
                for candidate in CANDIDATES
            )
        )
    null_summary = {
        "permutations": PERMUTATIONS,
        "seed": SEED,
        "selected_candidate": selected,
        "observed_amplitude": observed_amp,
        "observed_direction": observed_dir,
        "observed_composite": observed_composite,
        "p_amplitude": p_value(observed_amp, null_amp_max),
        "p_direction": p_value(observed_dir, null_dir_max),
        "p_composite": p_value(observed_composite, null_composite_max),
        "null_amplitude_q99": float(np.quantile(null_amp_max, 0.99)),
        "null_direction_q95": float(np.quantile(null_dir_max, 0.95)),
        "null_composite_q95": float(np.quantile(null_composite_max, 0.95)),
    }
    VALIDATION_INPUT_JSON.write_text(
        json.dumps(null_summary, indent=2), encoding="utf-8"
    )

    selected_rows = [
        row for row in all_folds if row["candidate"] == selected
    ]
    rank_one = {
        axis: float(
            np.median(
                [
                    float(row["rank_one_share"])
                    for row in selected_rows
                    if row["axis"] == axis
                ]
            )
        )
        for axis in AXES
    }
    sign_scores = {
        axis: float(
            np.median(
                [
                    float(row["sign_agreement"])
                    for row in selected_rows
                    if row["axis"] == axis
                ]
            )
        )
        for axis in AXES
    }
    fold_shapes_ok = all(
        int(row["train_rows"]) == 33 and int(row["test_rows"]) == 11
        for row in all_folds
    )

    gates: list[dict[str, object]] = []
    add_gate(gates, "L1", "44 complete cells contain four finite children", data_ok and len(child_rows) == 44, {"cells": len(child_rows), "finite": data_ok})
    add_gate(gates, "L2", "every fold uses 33 training and 11 held-out rows", fold_shapes_ok, fold_shapes_ok)
    add_gate(gates, "L3", "selected candidate is unresolved Phase B", selected in ("R_B", "H_B"), selected)
    add_gate(gates, "L4", "selected amplitude covariance reduction >= 0.60", observed_amp >= 0.60, observed_amp)
    add_gate(gates, "L5", "selected direction covariance reduction >= 0.25", observed_dir >= 0.25, observed_dir)
    add_gate(gates, "L6", "selection-corrected amplitude p <= 0.01", float(null_summary["p_amplitude"]) <= 0.01, null_summary["p_amplitude"])
    add_gate(gates, "L7", "selection-corrected direction p <= 0.05", float(null_summary["p_direction"]) <= 0.05, null_summary["p_direction"])
    add_gate(gates, "L8", "median rank-one share >= 0.70 on both axes", all(value >= 0.70 for value in rank_one.values()), rank_one)
    add_gate(gates, "L9", "median induced-relation sign agreement >= 2/3 on both axes", all(value >= 2 / 3 for value in sign_scores.values()), sign_scores)
    add_gate(gates, "L10", "same candidate wins at least 3/4 held-out states", selected_wins >= 3, {"selected_wins": selected_wins, "fold_winners": fold_winners})

    candidate_rows = []
    for candidate in CANDIDATES:
        score = 0.5 * (
            summaries[candidate]["amplitude"]["median_reduction"]
            + summaries[candidate]["direction"]["median_reduction"]
        )
        candidate_rows.append(
            {
                "candidate": candidate,
                "phase_assignment": "B_unresolved" if candidate.endswith("_B") else "A_visible",
                "amplitude_median_reduction": summaries[candidate]["amplitude"]["median_reduction"],
                "direction_median_reduction": summaries[candidate]["direction"]["median_reduction"],
                "composite_score": score,
                "amplitude_rank_one_share": summaries[candidate]["amplitude"]["median_rank_one_share"],
                "direction_rank_one_share": summaries[candidate]["direction"]["median_rank_one_share"],
                "amplitude_sign_agreement": summaries[candidate]["amplitude"]["median_sign_agreement"],
                "direction_sign_agreement": summaries[candidate]["direction"]["median_sign_agreement"],
                "selected": candidate == selected,
            }
        )

    result = {
        "test_id": "Q13-RAMSEY-HAHN-LATENT-CHILD-v1",
        "ledger_id": "T272",
        "test_class": "post-outcome held-out latent-coordinate test",
        "protocol_sha256": protocol_hash,
        "verdict": "CALIBRATED" if all(gate["passed"] for gate in gates) else "PARTIAL / NOT CALIBRATED",
        "summary": {
            "selected_candidate": selected,
            "selected_phase_assignment": "B_unresolved" if selected.endswith("_B") else "A_visible",
            "candidate_summaries": summaries,
            "rank_one_shares": rank_one,
            "sign_agreement": sign_scores,
            "fold_winners": fold_winners,
            "selected_fold_wins": selected_wins,
            "null": null_summary,
            "gates_passed": sum(bool(gate["passed"]) for gate in gates),
            "gates_total": len(gates),
        },
        "gates": gates,
        "boundary": (
            "This matched-ordinal-stage test conditions on the deliberately revealed hidden candidate. "
            "It tests structural mediation across Bell identities, not recovery of an unmeasured variable "
            "or a pulse-resolved Ramsey-to-Hahn temporal handoff."
        ),
    }

    with CHILDREN_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(child_rows[0]))
        writer.writeheader()
        writer.writerows(child_rows)
    with FOLDS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(all_folds[0]))
        writer.writeheader()
        writer.writerows(all_folds)
    with CANDIDATES_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(candidate_rows[0]))
        writer.writeheader()
        writer.writerows(candidate_rows)
    with GATES_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("gate_id", "description", "passed", "value"))
        writer.writeheader()
        for gate in gates:
            writer.writerow({**gate, "value": json.dumps(gate["value"], sort_keys=True)})
    RESULTS_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    build_svg(summaries, selected, all_folds, null_summary)
    print(json.dumps(result["summary"], indent=2))
    print(f"Verdict: {result['verdict']}")
    return result


if __name__ == "__main__":
    run()
