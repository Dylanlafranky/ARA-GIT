from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
PREDICTIONS = HERE / "PN6_NATIVE_ARA_FROZEN_PREDICTIONS.json"
FREEZE_MANIFEST = HERE / "PN6_NATIVE_ARA_FREEZE_MANIFEST.json"
TARGET = HERE / "PN6_R11_TARGET_AGGREGATES.json"
RESULTS = HERE / "PN6_NATIVE_ARA_RESULTS.json"
PATHS = HERE / "PN6_NATIVE_ARA_PATHS.csv"
FIGURE = HERE / "PN6_NATIVE_ARA_CIRCUMFERENCE.png"
PRIMARY = HERE / "PN6_NATIVE_ARA_PRIMARY_ARTIFACT.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def phase(survival: np.ndarray) -> np.ndarray:
    return np.arccos(np.clip(2.0 * survival - 1.0, -1.0, 1.0))


def rmse(prediction: np.ndarray, observed: np.ndarray) -> float:
    return float(np.sqrt(np.mean((prediction - observed) ** 2)))


def validity(path: np.ndarray) -> dict[str, Any]:
    return {
        "finite": bool(np.all(np.isfinite(path))),
        "within_unit_interval": bool(np.all((path >= 0.0) & (path <= 1.0))),
        "nonincreasing": bool(np.all(np.diff(path) <= 0.0)),
        "minimum": float(path.min()),
        "maximum": float(path.max()),
    }


def score_path(prediction: np.ndarray, observed: np.ndarray, before: np.ndarray, deaths: np.ndarray) -> dict[str, float]:
    prior = np.concatenate(([1.0], prediction[:-1]))
    hazard = 1.0 - prediction / prior
    if np.any((hazard <= 0.0) | (hazard >= 1.0)):
        raise AssertionError("Frozen path produces an invalid conditional hazard")
    survivors = before - deaths
    log_loss_bits = -np.sum(deaths * np.log2(hazard) + survivors * np.log2(1.0 - hazard)) / np.sum(before)
    return {
        "log_loss_bits_per_at_risk_event": float(log_loss_bits),
        "survival_rmse": rmse(prediction, observed),
        "phase_rmse_radians": rmse(phase(prediction), phase(observed)),
        "terminal_prediction": float(prediction[-1]),
        "terminal_observed": float(observed[-1]),
        "terminal_absolute_relative_error": float(abs(prediction[-1] - observed[-1]) / observed[-1]),
    }


def json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    return value


def main() -> None:
    freeze_manifest = json.loads(FREEZE_MANIFEST.read_text(encoding="utf-8"))
    expected_prediction_hash = freeze_manifest["files"][PREDICTIONS.name]
    observed_prediction_hash = sha256(PREDICTIONS)
    if expected_prediction_hash != observed_prediction_hash:
        raise AssertionError("Frozen native prediction packet changed after target opening")

    frozen = json.loads(PREDICTIONS.read_text(encoding="utf-8"))
    target = json.loads(TARGET.read_text(encoding="utf-8"))
    if not target["freeze_evidence"]["matched"]:
        raise AssertionError("Target was not opened against the frozen prediction packet")
    if target["test_id"] != frozen["test_id"]:
        raise AssertionError("Target and frozen prediction test IDs differ")

    observed = {
        entity: np.asarray(target[entity]["survival"], dtype=float)
        for entity in ("candidate", "edge")
    }
    before = {
        entity: np.asarray(target[entity]["before"], dtype=np.int64)
        for entity in ("candidate", "edge")
    }
    deaths = {
        entity: np.asarray(target[entity]["deaths"], dtype=np.int64)
        for entity in ("candidate", "edge")
    }

    scores: dict[str, dict[str, dict[str, float]]] = {}
    valid: dict[str, dict[str, dict[str, Any]]] = {}
    for entity in ("candidate", "edge"):
        scores[entity] = {}
        valid[entity] = {}
        for name, values in frozen["predictions"][entity].items():
            prediction = np.asarray(values, dtype=float)
            scores[entity][name] = score_path(prediction, observed[entity], before[entity], deaths[entity])
            valid[entity][name] = validity(prediction)

    theta9 = {
        entity: np.asarray(frozen["source_phase"]["r9"][entity], dtype=float)
        for entity in ("candidate", "edge")
    }
    theta10 = {
        entity: np.asarray(frozen["source_phase"]["r10"][entity], dtype=float)
        for entity in ("candidate", "edge")
    }
    theta11 = {entity: phase(observed[entity]) for entity in ("candidate", "edge")}
    rho_observed = {}
    for entity in ("candidate", "edge"):
        delta10 = theta10[entity] - theta9[entity]
        delta11 = theta11[entity] - theta10[entity]
        rho_observed[entity] = float(np.dot(delta10, delta11) / np.dot(delta10, delta10))

    rho_frozen = float(frozen["fitted_parameters"]["rho_shared"])
    candidate_primary = scores["candidate"]["circle_shared_rho_primary"]
    edge_primary = scores["edge"]["circle_shared_rho_primary"]
    edge_secondary = scores["edge"]["circle_candidate_plus_j_secondary"]
    candidate_home = scores["candidate"]["home_r10"]
    edge_home = scores["edge"]["home_r10"]
    candidate_direct_log = scores["candidate"]["direct_log_rung"]
    edge_direct_log = scores["edge"]["direct_log_rung"]

    criteria = {
        "P1_candidate_primary_beats_home_terminal_under_1pct_phase_under_0_015": bool(
            candidate_primary["log_loss_bits_per_at_risk_event"] < candidate_home["log_loss_bits_per_at_risk_event"]
            and candidate_primary["terminal_absolute_relative_error"] < 0.01
            and candidate_primary["phase_rmse_radians"] < 0.015
        ),
        "P2_edge_primary_beats_home_terminal_under_1pct_phase_under_0_015": bool(
            edge_primary["log_loss_bits_per_at_risk_event"] < edge_home["log_loss_bits_per_at_risk_event"]
            and edge_primary["terminal_absolute_relative_error"] < 0.01
            and edge_primary["phase_rmse_radians"] < 0.015
        ),
        "P3_candidate_primary_beats_direct_native_log": bool(
            candidate_primary["log_loss_bits_per_at_risk_event"] < candidate_direct_log["log_loss_bits_per_at_risk_event"]
        ),
        "P4_edge_primary_beats_direct_native_log": bool(
            edge_primary["log_loss_bits_per_at_risk_event"] < edge_direct_log["log_loss_bits_per_at_risk_event"]
        ),
        "P5_shared_withdrawal_recurs": bool(
            abs(rho_observed["candidate"] - rho_frozen) < 0.15
            and abs(rho_observed["edge"] - rho_frozen) < 0.15
            and abs(rho_observed["candidate"] - rho_observed["edge"]) < 0.10
        ),
        "P6_primary_paths_valid_monotone_unrepaired": bool(
            all(valid[entity]["circle_shared_rho_primary"][key]
                for entity in ("candidate", "edge")
                for key in ("finite", "within_unit_interval", "nonincreasing"))
        ),
        "P7_native_pair_routes_close": bool(
            frozen["fitted_parameters"]["pretarget_pair_route_rmse"] < 0.002
            and edge_primary["terminal_absolute_relative_error"] < 0.01
            and edge_secondary["terminal_absolute_relative_error"] < 0.01
        ),
    }
    recurrence_core = all(criteria[key] for key in (
        "P1_candidate_primary_beats_home_terminal_under_1pct_phase_under_0_015",
        "P2_edge_primary_beats_home_terminal_under_1pct_phase_under_0_015",
        "P5_shared_withdrawal_recurs",
        "P6_primary_paths_valid_monotone_unrepaired",
    ))
    circle_added_value = all(criteria[key] for key in (
        "P3_candidate_primary_beats_direct_native_log",
        "P4_edge_primary_beats_direct_native_log",
    ))

    results = {
        "test_id": frozen["test_id"],
        "verdict_boundary": "NATIVE ARA ONLY; NO ESTABLISHED PRIME-LAW AUDIT RUN",
        "freeze_integrity": {
            "prediction_packet_sha256_expected": expected_prediction_hash,
            "prediction_packet_sha256_after_target": observed_prediction_hash,
            "matched": expected_prediction_hash == observed_prediction_hash,
            "target_packet_sha256": sha256(TARGET),
        },
        "target": target["target"],
        "counts": {
            entity: {
                "initial": int(target[entity]["n0"]),
                "terminal_survivors": int(target[entity]["terminal_survivors"]),
            }
            for entity in ("candidate", "edge")
        },
        "frozen_rho_shared": rho_frozen,
        "observed_rho": rho_observed,
        "observed_rho_distance_from_frozen": {
            entity: abs(rho_observed[entity] - rho_frozen) for entity in ("candidate", "edge")
        },
        "observed_rho_candidate_edge_distance": abs(rho_observed["candidate"] - rho_observed["edge"]),
        "scores": scores,
        "path_validity": valid,
        "criteria": criteria,
        "summary_verdict": {
            "criteria_passed": sum(criteria.values()),
            "criteria_total": len(criteria),
            "native_shared_circumference_log_rung_recurrence_supported": recurrence_core,
            "canonical_circle_adds_value_beyond_direct_native_log": circle_added_value,
            "native_pair_route_closure_supported": criteria["P7_native_pair_routes_close"],
        },
        "target_accounting_checks": target["accounting_checks"],
        "native_model_quarantine": frozen["native_model_quarantine"],
    }
    RESULTS.write_text(json.dumps(json_ready(results), indent=2) + "\n", encoding="utf-8")

    with PATHS.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["cell", "progress", "q_end", "entity", "observed_survival", "observed_phase",
                         "model", "predicted_survival", "predicted_phase"])
        for cell, progress in enumerate(frozen["progress"]):
            for entity in ("candidate", "edge"):
                for name, values in frozen["predictions"][entity].items():
                    value = float(values[cell])
                    writer.writerow([
                        cell + 1,
                        progress,
                        target["q_end"][cell],
                        entity,
                        observed[entity][cell],
                        theta11[entity][cell],
                        name,
                        value,
                        math.acos(2.0 * value - 1.0),
                    ])

    primary = {
        "test_id": frozen["test_id"],
        "model": "canonical ARA circumference plus shared log-rung phase withdrawal",
        "prediction_packet_sha256": observed_prediction_hash,
        "frozen_rho_shared": rho_frozen,
        "candidate": candidate_primary,
        "edge": edge_primary,
        "criteria": criteria,
        "summary_verdict": results["summary_verdict"],
    }
    PRIMARY.write_text(json.dumps(primary, indent=2) + "\n", encoding="utf-8")

    progress = np.asarray(frozen["progress"], dtype=float)
    colors = {
        "home_r10": "#9ca3af",
        "direct_log_rung": "#f59e0b",
        "circle_secant_rho1": "#8b5cf6",
        "circle_shared_rho_primary": "#2563eb",
        "circle_candidate_plus_j_secondary": "#16a34a",
    }
    labels = {
        "home_r10": "Home R10",
        "direct_log_rung": "Direct native log",
        "circle_secant_rho1": "Circle secant (rho=1)",
        "circle_shared_rho_primary": "Circle + shared rho (primary)",
        "circle_candidate_plus_j_secondary": "Candidate + J route",
    }
    image = Image.new("RGB", (1800, 620), "white")
    draw = ImageDraw.Draw(image)
    font_path = Path("C:/Windows/Fonts/arial.ttf")
    bold_path = Path("C:/Windows/Fonts/arialbd.ttf")
    font = ImageFont.truetype(str(font_path), 20) if font_path.exists() else ImageFont.load_default()
    small = ImageFont.truetype(str(font_path), 16) if font_path.exists() else ImageFont.load_default()
    bold = ImageFont.truetype(str(bold_path), 27) if bold_path.exists() else font
    title_font = ImageFont.truetype(str(bold_path), 30) if bold_path.exists() else font
    draw.text((900, 20), "PN6: native ARA circumference prediction on untouched R11", fill="#111827",
              font=title_font, anchor="ma")

    panels = [(40, 90, 560, 550), (640, 90, 1160, 550), (1240, 90, 1760, 550)]

    def panel_axes(box: tuple[int, int, int, int], title: str, ymin: float, ymax: float, ylabel: str) -> tuple[int, int, int, int]:
        left, top, right, bottom = box
        plot = (left + 70, top + 45, right - 18, bottom - 60)
        x0, y0, x1, y1 = plot
        draw.text(((left + right) / 2, top + 5), title, fill="#111827", font=bold, anchor="ma")
        draw.line((x0, y0, x0, y1), fill="#111827", width=2)
        draw.line((x0, y1, x1, y1), fill="#111827", width=2)
        for tick in range(5):
            fraction = tick / 4
            y = y1 - fraction * (y1 - y0)
            value = ymin + fraction * (ymax - ymin)
            draw.line((x0, y, x1, y), fill="#e5e7eb", width=1)
            draw.text((x0 - 8, y), f"{value:.2f}", fill="#374151", font=small, anchor="rm")
        draw.text(((x0 + x1) / 2, bottom - 33), "Normalized log-gate progress", fill="#374151", font=small, anchor="ma")
        return plot

    def draw_series(plot: tuple[int, int, int, int], xs: np.ndarray, ys: np.ndarray,
                    ymin: float, ymax: float, color: str, width: int = 3) -> None:
        x0, y0, x1, y1 = plot
        points = []
        for x, y in zip(xs, ys):
            px = x0 + float(x) * (x1 - x0)
            py = y1 - (float(y) - ymin) / (ymax - ymin) * (y1 - y0)
            points.append((px, py))
        draw.line(points, fill=color, width=width, joint="curve")

    for panel, entity, panel_title in zip(panels[:2], ("candidate", "edge"), ("Candidate identity", "Adjacent-pair identity")):
        plot = panel_axes(panel, panel_title, 0.0, 1.0, "Survival")
        names = ["home_r10", "direct_log_rung", "circle_secant_rho1", "circle_shared_rho_primary"]
        if entity == "edge":
            names.append("circle_candidate_plus_j_secondary")
        for name in names:
            draw_series(plot, progress, np.asarray(frozen["predictions"][entity][name]), 0.0, 1.0, colors[name], 3)
        draw_series(plot, progress, observed[entity], 0.0, 1.0, "#111111", 5)
        legend_x, legend_y = plot[0] + 10, plot[1] + 8
        legend_items = [("Observed R11", "#111111")] + [(labels[name], colors[name]) for name in names]
        for index, (label, color) in enumerate(legend_items):
            y = legend_y + index * 22
            draw.line((legend_x, y + 8, legend_x + 25, y + 8), fill=color, width=4)
            draw.text((legend_x + 32, y), label, fill="#111827", font=small)

    phase_plot = panel_axes(panels[2], "Circumference phase increments", 0.0, 0.16, "Radians")
    phase_legend = []
    for entity, color in (("candidate", "#2563eb"), ("edge", "#dc2626")):
        delta10 = theta10[entity] - theta9[entity]
        delta11 = theta11[entity] - theta10[entity]
        draw_series(phase_plot, progress, delta10, 0.0, 0.16, color, 2)
        draw_series(phase_plot, progress, delta11, 0.0, 0.16, color, 5)
        draw_series(phase_plot, progress, rho_frozen * delta10, 0.0, 0.16, "#111111" if entity == "candidate" else "#6b7280", 2)
        phase_legend.extend([(f"{entity}: observed next", color),
                             (f"{entity}: frozen rho x prior", "#111111" if entity == "candidate" else "#6b7280")])
    legend_x, legend_y = phase_plot[0] + 10, phase_plot[1] + 8
    for index, (label, color) in enumerate(phase_legend):
        y = legend_y + index * 22
        draw.line((legend_x, y + 8, legend_x + 25, y + 8), fill=color, width=4)
        draw.text((legend_x + 32, y), label, fill="#111827", font=small)
    image.save(FIGURE)

    print(json.dumps({
        "criteria": criteria,
        "summary_verdict": results["summary_verdict"],
        "frozen_rho": rho_frozen,
        "observed_rho": rho_observed,
        "candidate_primary": candidate_primary,
        "edge_primary": edge_primary,
        "edge_secondary": edge_secondary,
        "results_sha256": sha256(RESULTS),
        "primary_sha256": sha256(PRIMARY),
    }, indent=2))


if __name__ == "__main__":
    main()
