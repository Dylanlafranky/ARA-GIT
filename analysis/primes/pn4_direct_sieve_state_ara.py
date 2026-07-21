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
SOURCE_PATH = HERE / "PN3A_ADULT_SIEVE_DIAGNOSTIC_DATA.npz"
PROTOCOL_PATH = HERE / "PN4_DIRECT_SIEVE_STATE_ARA_PROTOCOL.md"
RESULTS_PATH = HERE / "PN4_DIRECT_SIEVE_STATE_RESULTS.json"
PATHS_PATH = HERE / "PN4_DIRECT_SIEVE_STATE_PATHS.csv"
FIGURE_PATH = HERE / "PN4_DIRECT_SIEVE_STATE_TRANSFER.png"
ARTIFACT_PATH = HERE / "PN4_DIRECT_SIEVE_STATE_ARTIFACT.json"

WINDOWS = {
    "r6": (1_000_000, 1_010_000),
    "r7": (10_000_000, 10_100_000),
    "r8": (100_000_000, 101_000_000),
    "r9": (1_000_000_000, 1_010_000_000),
}
CELLS = 24
EPS = 1e-12
EULER_GAMMA = 0.5772156649015329


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def simple_primes(limit: int) -> np.ndarray:
    sieve = np.ones(limit + 1, dtype=bool)
    sieve[:2] = False
    for prime in range(2, math.isqrt(limit) + 1):
        if sieve[prime]:
            sieve[prime * prime :: prime] = False
    return np.flatnonzero(sieve).astype(np.int64)


def make_path(name: str, death: np.ndarray, edge_death: np.ndarray) -> dict[str, Any]:
    _, high = WINDOWS[name]
    primes = simple_primes(math.isqrt(high - 1))
    primes = primes[primes > 29]
    qmax = int(primes[-1])
    progress = np.log(primes.astype(float) / 31.0) / math.log(qmax / 31.0)
    gate_cell = np.minimum((progress * CELLS).astype(int), CELLS - 1)

    out: dict[str, Any] = {
        "rung": name,
        "qmax": qmax,
        "progress": (np.arange(CELLS, dtype=float) + 1.0) / CELLS,
    }
    cell_products = np.ones(CELLS, dtype=float)
    q_end = np.zeros(CELLS, dtype=np.int64)
    q_count = np.zeros(CELLS, dtype=np.int64)
    for cell in range(CELLS):
        q = primes[gate_cell == cell]
        if len(q):
            cell_products[cell] = float(np.prod(1.0 - 1.0 / q.astype(float)))
            q_end[cell] = int(q[-1])
            q_count[cell] = len(q)
        elif cell:
            q_end[cell] = q_end[cell - 1]
        else:
            q_end[cell] = 29
    out["q_end"] = q_end
    out["q_count"] = q_count
    out["cell_product"] = cell_products

    for entity, values in (("candidate", death), ("edge", edge_death)):
        before = np.empty(CELLS, dtype=np.int64)
        deaths = np.empty(CELLS, dtype=np.int64)
        survival = np.empty(CELLS, dtype=float)
        alive = len(values)
        for cell in range(CELLS):
            before[cell] = alive
            cell_q = primes[gate_cell == cell]
            count = int(np.isin(values, cell_q, assume_unique=False).sum()) if len(cell_q) else 0
            deaths[cell] = count
            alive -= count
            survival[cell] = alive / len(values)
        out[f"{entity}_n0"] = int(len(values))
        out[f"{entity}_before"] = before
        out[f"{entity}_deaths"] = deaths
        out[f"{entity}_survival"] = survival
        out[f"{entity}_hazard"] = deaths / before
        out[f"{entity}_x"] = 2.0 * (1.0 - survival)

    out["candidate_independent"] = np.cumprod(cell_products)
    out["edge_independent"] = out["candidate_independent"] ** 2
    out["coupling_j"] = np.log(out["edge_survival"] / (out["candidate_survival"] ** 2))
    return out


def valid_path(raw: np.ndarray) -> tuple[np.ndarray, int]:
    clipped = np.clip(np.asarray(raw, dtype=float), EPS, 1.0)
    monotone = np.minimum.accumulate(clipped)
    changes = int(np.count_nonzero(np.abs(monotone - raw) > 1e-12))
    return monotone, changes


def score_path(predicted: np.ndarray, actual_path: dict[str, Any], entity: str) -> dict[str, float]:
    predicted, _ = valid_path(predicted)
    previous = np.concatenate(([1.0], predicted[:-1]))
    hazard = np.clip(1.0 - predicted / previous, EPS, 1.0 - EPS)
    deaths = actual_path[f"{entity}_deaths"].astype(float)
    before = actual_path[f"{entity}_before"].astype(float)
    nll = -(deaths * np.log2(hazard) + (before - deaths) * np.log2(1.0 - hazard))
    actual = actual_path[f"{entity}_survival"]
    return {
        "log_loss_bits_per_at_risk_event": float(nll.sum() / before.sum()),
        "survival_rmse": float(np.sqrt(np.mean((predicted - actual) ** 2))),
        "terminal_prediction": float(predicted[-1]),
        "terminal_actual": float(actual[-1]),
        "terminal_absolute_relative_error": float(abs(predicted[-1] - actual[-1]) / actual[-1]),
    }


def transfer_models(target: dict[str, Any], source: dict[str, Any], prior: dict[str, Any] | None) -> dict[str, Any]:
    ci_t = target["candidate_independent"]
    ci_s = source["candidate_independent"]
    cs = source["candidate_survival"]
    candidate: dict[str, np.ndarray] = {
        "independent_sieve": ci_t,
        "ara_same_form_residual": ci_t + (cs - ci_s),
        "raw_multiplicative_ratio": ci_t * (cs / ci_s),
    }
    if prior is not None:
        c_error_s = 2.0 * (1.0 - cs) - 2.0 * (1.0 - ci_s)
        c_error_p = 2.0 * (1.0 - prior["candidate_survival"]) - 2.0 * (1.0 - prior["candidate_independent"])
        candidate["ara_two_rung_residual"] = 1.0 - (2.0 * (1.0 - ci_t) + 2.0 * c_error_s - c_error_p) / 2.0
        log_ratio = 2.0 * np.log(cs / ci_s) - np.log(prior["candidate_survival"] / prior["candidate_independent"])
        candidate["raw_two_rung_ratio"] = ci_t * np.exp(log_ratio)

    candidate_valid: dict[str, np.ndarray] = {}
    adjustments: dict[str, int] = {}
    for key, values in candidate.items():
        candidate_valid[key], adjustments[f"candidate__{key}"] = valid_path(values)

    ei_t = target["edge_independent"]
    ei_s = source["edge_independent"]
    es = source["edge_survival"]
    j_s = source["coupling_j"]
    edge: dict[str, np.ndarray] = {
        "independent_pair": ei_t,
        "ara_direct_edge_residual": ei_t + (es - ei_s),
        "ara_coupled_relation": candidate_valid["ara_same_form_residual"] ** 2 * np.exp(j_s),
        "raw_multiplicative_edge_ratio": ei_t * (es / ei_s),
    }
    if prior is not None:
        e_error_s = 2.0 * (1.0 - es) - 2.0 * (1.0 - ei_s)
        e_error_p = 2.0 * (1.0 - prior["edge_survival"]) - 2.0 * (1.0 - prior["edge_independent"])
        edge["ara_two_rung_edge_residual"] = 1.0 - (2.0 * (1.0 - ei_t) + 2.0 * e_error_s - e_error_p) / 2.0
        j_gradient = 2.0 * j_s - prior["coupling_j"]
        edge["ara_coupled_relation_gradient"] = candidate_valid["ara_two_rung_residual"] ** 2 * np.exp(j_gradient)
        log_ratio = 2.0 * np.log(es / ei_s) - np.log(prior["edge_survival"] / prior["edge_independent"])
        edge["raw_two_rung_edge_ratio"] = ei_t * np.exp(log_ratio)

    edge_valid: dict[str, np.ndarray] = {}
    for key, values in edge.items():
        edge_valid[key], adjustments[f"edge__{key}"] = valid_path(values)
    return {"candidate": candidate_valid, "edge": edge_valid, "clipping_adjustments": adjustments}


def causal_probe(path: dict[str, Any], entity: str) -> dict[str, dict[str, float]]:
    actual_s = path[f"{entity}_survival"]
    actual_h = path[f"{entity}_hazard"]
    start = 2
    before = path[f"{entity}_before"][start:].astype(float)
    deaths = path[f"{entity}_deaths"][start:].astype(float)
    if entity == "candidate":
        independent = 1.0 - path["cell_product"][start:]
    else:
        independent = 1.0 - path["cell_product"][start:] ** 2
    home = actual_h[start - 1 : -1]
    secant_s = 2.0 * actual_s[start - 1 : -1] - actual_s[start - 2 : -2]
    secant_s = np.minimum(secant_s, actual_s[start - 1 : -1])
    secant_s = np.clip(secant_s, EPS, actual_s[start - 1 : -1])
    ara = 1.0 - secant_s / actual_s[start - 1 : -1]

    def score(probability: np.ndarray) -> dict[str, float]:
        p = np.clip(probability, EPS, 1.0 - EPS)
        nll = -(deaths * np.log2(p) + (before - deaths) * np.log2(1.0 - p))
        return {
            "log_loss_bits_per_at_risk_event": float(nll.sum() / before.sum()),
            "hazard_mae": float(np.mean(np.abs(p - actual_h[start:]))),
        }

    return {
        "independent_next_cell": score(independent),
        "home_last_hazard": score(home),
        "ara_three_point_secant": score(ara),
    }


def json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): json_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    return value


def write_paths(paths: dict[str, dict[str, Any]], transfers: dict[str, Any]) -> None:
    fieldnames = [
        "rung", "cell", "progress", "q_end", "q_count", "candidate_before", "candidate_deaths",
        "candidate_survival", "candidate_x", "candidate_independent", "edge_before", "edge_deaths",
        "edge_survival", "edge_x", "edge_independent", "coupling_j",
    ]
    model_fields: list[str] = []
    r9_models = transfers["r8_to_r9"]["predictions"]
    for entity in ("candidate", "edge"):
        for model in r9_models[entity]:
            model_fields.append(f"r9_prediction__{entity}__{model}")
    with PATHS_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames + model_fields)
        writer.writeheader()
        for rung, path in paths.items():
            for i in range(CELLS):
                row = {
                    "rung": rung,
                    "cell": i + 1,
                    "progress": path["progress"][i],
                    "q_end": path["q_end"][i],
                    "q_count": path["q_count"][i],
                    "candidate_before": path["candidate_before"][i],
                    "candidate_deaths": path["candidate_deaths"][i],
                    "candidate_survival": path["candidate_survival"][i],
                    "candidate_x": path["candidate_x"][i],
                    "candidate_independent": path["candidate_independent"][i],
                    "edge_before": path["edge_before"][i],
                    "edge_deaths": path["edge_deaths"][i],
                    "edge_survival": path["edge_survival"][i],
                    "edge_x": path["edge_x"][i],
                    "edge_independent": path["edge_independent"][i],
                    "coupling_j": path["coupling_j"][i],
                }
                if rung == "r9":
                    for entity in ("candidate", "edge"):
                        for model, values in r9_models[entity].items():
                            row[f"r9_prediction__{entity}__{model}"] = values[i]
                writer.writerow(json_ready(row))


def make_figure(paths: dict[str, dict[str, Any]], transfers: dict[str, Any]) -> None:
    r9 = paths["r9"]
    pred = transfers["r8_to_r9"]["predictions"]
    t = r9["progress"]
    image = Image.new("RGB", (1680, 620), (250, 250, 248))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((45, 24), "PN4 direct sieve-state ARA — opened-data scale transfer", fill=(25, 31, 37), font=font)
    boxes = [(45, 75, 555, 545), (585, 75, 1095, 545), (1125, 75, 1635, 545)]

    def panel(box: tuple[int, int, int, int], title: str, series: list[tuple[str, np.ndarray, tuple[int, int, int], int]], yrange: tuple[float, float]) -> None:
        x0, y0, x1, y1 = box
        draw.rectangle(box, outline=(205, 210, 214), width=1)
        draw.text((x0 + 12, y0 + 10), title, fill=(37, 42, 46), font=font)
        px0, py0, px1, py1 = x0 + 50, y0 + 45, x1 - 18, y1 - 55
        draw.line((px0, py1, px1, py1), fill=(130, 136, 141), width=1)
        draw.line((px0, py0, px0, py1), fill=(130, 136, 141), width=1)
        ymin, ymax = yrange
        for label, values, color, width in series:
            points = []
            for tx, value in zip(t, values):
                x = px0 + float(tx) * (px1 - px0)
                y = py1 - (float(value) - ymin) / (ymax - ymin) * (py1 - py0)
                points.append((x, y))
            draw.line(points, fill=color, width=width)
        legend_y = y1 - 42
        legend_x = x0 + 15
        for label, _, color, _ in series:
            draw.line((legend_x, legend_y + 5, legend_x + 18, legend_y + 5), fill=color, width=3)
            draw.text((legend_x + 23, legend_y), label, fill=(70, 76, 82), font=font)
            legend_x += max(92, 28 + 7 * len(label))
        draw.text((px0 + 115, y1 - 18), "normalized log-gate progress", fill=(90, 96, 102), font=font)

    panel(
        boxes[0],
        "Candidate survivor path",
        [
            ("Observed", r9["candidate_survival"], (22, 32, 42), 4),
            ("Independent", pred["candidate"]["independent_sieve"], (136, 136, 136), 2),
            ("ARA same-form", pred["candidate"]["ara_same_form_residual"], (49, 107, 166), 3),
            ("Raw ratio", pred["candidate"]["raw_multiplicative_ratio"], (209, 122, 52), 2),
        ],
        (0.25, 1.0),
    )
    panel(
        boxes[1],
        "Adjacent-pair survivor path",
        [
            ("Observed", r9["edge_survival"], (22, 32, 42), 4),
            ("Independent²", pred["edge"]["independent_pair"], (136, 136, 136), 2),
            ("Direct edge", pred["edge"]["ara_direct_edge_residual"], (49, 107, 166), 2),
            ("Coupled ARA", pred["edge"]["ara_coupled_relation"], (107, 76, 165), 3),
            ("Raw ratio", pred["edge"]["raw_multiplicative_edge_ratio"], (209, 122, 52), 2),
        ],
        (0.05, 1.0),
    )
    j_all = np.concatenate([paths[r]["coupling_j"] for r in paths])
    margin = max(0.01, 0.08 * float(j_all.max() - j_all.min()))
    panel(
        boxes[2],
        "Coupling J = log(pair / candidate²)",
        [
            ("R6", paths["r6"]["coupling_j"], (174, 201, 225), 2),
            ("R7", paths["r7"]["coupling_j"], (113, 161, 202), 2),
            ("R8", paths["r8"]["coupling_j"], (61, 119, 174), 3),
            ("R9", paths["r9"]["coupling_j"], (30, 75, 120), 4),
        ],
        (float(j_all.min() - margin), float(j_all.max() + margin)),
    )
    image.save(FIGURE_PATH)


def run() -> dict[str, Any]:
    archive = np.load(SOURCE_PATH, allow_pickle=False)
    paths = {
        rung: make_path(rung, archive[f"{rung}__candidate_death"], archive[f"{rung}__edge_death"])
        for rung in WINDOWS
    }

    transfer_specs = [
        ("r6_to_r7", "r7", "r6", None),
        ("r7_to_r8", "r8", "r7", "r6"),
        ("r8_to_r9", "r9", "r8", "r7"),
    ]
    transfers: dict[str, Any] = {}
    for label, target_name, source_name, prior_name in transfer_specs:
        target = paths[target_name]
        model_output = transfer_models(target, paths[source_name], None if prior_name is None else paths[prior_name])
        predictions = {entity: model_output[entity] for entity in ("candidate", "edge")}
        scores: dict[str, Any] = {}
        for entity in ("candidate", "edge"):
            scores[entity] = {}
            for model, predicted in predictions[entity].items():
                scores[entity][model] = score_path(predicted, target, entity)
        transfers[label] = {
            "target": target_name,
            "source": source_name,
            "prior": prior_name,
            "scores": scores,
            "clipping_adjustments": model_output["clipping_adjustments"],
            "predictions": predictions,
        }

    local = {
        rung: {entity: causal_probe(path, entity) for entity in ("candidate", "edge")}
        for rung, path in paths.items()
    }

    r9_scores = transfers["r8_to_r9"]["scores"]
    c = r9_scores["candidate"]
    e = r9_scores["edge"]
    c1 = c["ara_same_form_residual"]["log_loss_bits_per_at_risk_event"] < min(
        c["independent_sieve"]["log_loss_bits_per_at_risk_event"],
        c["raw_multiplicative_ratio"]["log_loss_bits_per_at_risk_event"],
    )
    c2 = e["ara_coupled_relation"]["log_loss_bits_per_at_risk_event"] < min(
        e["independent_pair"]["log_loss_bits_per_at_risk_event"],
        e["ara_direct_edge_residual"]["log_loss_bits_per_at_risk_event"],
        e["raw_multiplicative_edge_ratio"]["log_loss_bits_per_at_risk_event"],
    )
    repeat_candidate = all(
        transfers[label]["scores"]["candidate"]["ara_same_form_residual"]["log_loss_bits_per_at_risk_event"]
        < transfers[label]["scores"]["candidate"]["independent_sieve"]["log_loss_bits_per_at_risk_event"]
        for label in ("r7_to_r8", "r8_to_r9")
    )
    repeat_edge = all(
        transfers[label]["scores"]["edge"]["ara_coupled_relation"]["log_loss_bits_per_at_risk_event"]
        < transfers[label]["scores"]["edge"]["independent_pair"]["log_loss_bits_per_at_risk_event"]
        for label in ("r7_to_r8", "r8_to_r9")
    )
    c5_candidate = local["r9"]["candidate"]["ara_three_point_secant"]["log_loss_bits_per_at_risk_event"] < min(
        local["r9"]["candidate"]["home_last_hazard"]["log_loss_bits_per_at_risk_event"],
        local["r9"]["candidate"]["independent_next_cell"]["log_loss_bits_per_at_risk_event"],
    )
    c5_edge = local["r9"]["edge"]["ara_three_point_secant"]["log_loss_bits_per_at_risk_event"] < min(
        local["r9"]["edge"]["home_last_hazard"]["log_loss_bits_per_at_risk_event"],
        local["r9"]["edge"]["independent_next_cell"]["log_loss_bits_per_at_risk_event"],
    )

    factor = math.exp(EULER_GAMMA) / 2.0
    terminal = {
        "candidate": {
            "actual": float(paths["r9"]["candidate_survival"][-1]),
            "independent": float(paths["r9"]["candidate_independent"][-1]),
            "mertens_pnt_factor_prediction": float(paths["r9"]["candidate_independent"][-1] * factor),
        },
        "edge": {
            "actual": float(paths["r9"]["edge_survival"][-1]),
            "independent_squared": float(paths["r9"]["edge_independent"][-1]),
            "mertens_pnt_factor_squared_prediction": float(paths["r9"]["edge_independent"][-1] * factor * factor),
        },
    }
    for values in terminal.values():
        actual = values["actual"]
        values["absolute_relative_errors"] = {
            key: abs(value - actual) / actual
            for key, value in values.items()
            if key != "actual" and not key.startswith("absolute_")
        }

    results = {
        "test_id": "PN4/DIRECT-SIEVE-STATE/OPENED-DEVELOPMENT-v1",
        "status": "OPENED-DATA RETROSPECTIVE TRANSFER",
        "cells": CELLS,
        "source_sha256": sha256_file(SOURCE_PATH),
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "script_sha256": sha256_file(Path(__file__)),
        "rung_summaries": {
            rung: {
                "qmax": path["qmax"],
                "candidate_n0": path["candidate_n0"],
                "edge_n0": path["edge_n0"],
                "candidate_terminal_survival": float(path["candidate_survival"][-1]),
                "edge_terminal_survival": float(path["edge_survival"][-1]),
                "candidate_terminal_x": float(path["candidate_x"][-1]),
                "edge_terminal_x": float(path["edge_x"][-1]),
                "terminal_coupling_j": float(path["coupling_j"][-1]),
            }
            for rung, path in paths.items()
        },
        "transfers": {
            label: {key: value for key, value in transfer.items() if key != "predictions"}
            for label, transfer in transfers.items()
        },
        "local_causal_probe": local,
        "terminal_established_comparators": terminal,
        "criteria": {
            "C1_candidate_same_form_beats_independent_and_raw_ratio_r9": bool(c1),
            "C2_coupled_edge_beats_independent_direct_and_raw_ratio_r9": bool(c2),
            "C3_candidate_direction_repeats_r7_r8_and_r8_r9": bool(repeat_candidate),
            "C3_edge_direction_repeats_r7_r8_and_r8_r9": bool(repeat_edge),
            "C4_candidate_same_form_terminal_error_below_1pct": bool(c["ara_same_form_residual"]["terminal_absolute_relative_error"] < 0.01),
            "C4_edge_coupled_terminal_error_below_1pct": bool(e["ara_coupled_relation"]["terminal_absolute_relative_error"] < 0.01),
            "C5_candidate_local_stencil_beats_home_and_independence_r9": bool(c5_candidate),
            "C5_edge_local_stencil_beats_home_and_independence_r9": bool(c5_edge),
        },
        "calibration": {
            "ara_same_form_equals_additive_raw_survival_residual": True,
            "identity": "x=2(1-S), so additive x-residual transfer and additive S-residual transfer are affine-equivalent",
            "information_ceiling": "No prediction contains information unavailable from exact prior-rung survivor paths and known sieve gates.",
        },
    }

    RESULTS_PATH.write_text(json.dumps(json_ready(results), indent=2) + "\n", encoding="utf-8")
    write_paths(paths, transfers)
    make_figure(paths, transfers)
    artifact = {
        "test_id": results["test_id"],
        "files": {
            path.name: sha256_file(path)
            for path in (SOURCE_PATH, PROTOCOL_PATH, Path(__file__), RESULTS_PATH, PATHS_PATH, FIGURE_PATH)
        },
    }
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    return results


if __name__ == "__main__":
    outcome = run()
    print(json.dumps({"status": outcome["status"], "criteria": outcome["criteria"]}, indent=2))
