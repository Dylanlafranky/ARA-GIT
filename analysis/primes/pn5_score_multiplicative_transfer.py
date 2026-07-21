from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN5_MULTIPLICATIVE_RUNG_TRANSFER_PROTOCOL.md"
FROZEN = HERE / "PN5_FROZEN_PREDICTIONS.json"
FREEZE_MANIFEST = HERE / "PN5_FROZEN_PREDICTION_MANIFEST.json"
TARGET = HERE / "PN5_R10_TARGET_AGGREGATES.json"
RESULTS = HERE / "PN5_MULTIPLICATIVE_RUNG_RESULTS.json"
PATHS = HERE / "PN5_MULTIPLICATIVE_RUNG_PATHS.csv"
FIGURE = HERE / "PN5_MULTIPLICATIVE_RUNG_TRANSFER.png"
ARTIFACT = HERE / "PN5_PRIMARY_ARTIFACT.json"
EPS = 1e-12


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def path_score(predicted: np.ndarray, before: np.ndarray, deaths: np.ndarray, actual: np.ndarray) -> dict[str, float]:
    previous = np.concatenate(([1.0], predicted[:-1]))
    probability = np.clip(1.0 - predicted / previous, EPS, 1.0 - EPS)
    n = before.astype(float)
    d = deaths.astype(float)
    loss = -(d * np.log2(probability) + (n - d) * np.log2(1.0 - probability))
    return {
        "log_loss_bits_per_at_risk_event": float(loss.sum() / n.sum()),
        "total_log_loss_bits": float(loss.sum()),
        "survival_rmse": float(np.sqrt(np.mean((predicted - actual) ** 2))),
        "terminal_prediction": float(predicted[-1]),
        "terminal_actual": float(actual[-1]),
        "terminal_absolute_relative_error": float(abs(predicted[-1] - actual[-1]) / actual[-1]),
    }


def ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): ready(item) for key, item in value.items()}
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    return value


def make_figure(
    progress: np.ndarray,
    actual_c: np.ndarray,
    actual_e: np.ndarray,
    predictions: dict[str, dict[str, np.ndarray]],
    k8: np.ndarray,
    k9: np.ndarray,
    k10: np.ndarray,
    j8: np.ndarray,
    j9: np.ndarray,
    j10: np.ndarray,
) -> None:
    image = Image.new("RGB", (1680, 650), (250, 250, 248))
    draw = ImageDraw.Draw(image)
    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 24)
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 14)
        small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 12)
    except OSError:
        title_font = font = small = ImageFont.load_default()
    draw.text((45, 20), "PN5 fresh R10 multiplicative rung transfer", fill=(28, 34, 40), font=title_font)
    draw.text((45, 50), "Predictions frozen before the 100-million-integer target was constructed", fill=(92, 99, 105), font=font)
    boxes = [(45, 90, 555, 580), (585, 90, 1095, 580), (1125, 90, 1635, 580)]

    def panel(box: tuple[int, int, int, int], title: str, series: list[tuple[str, np.ndarray, tuple[int, int, int], int]], yrange: tuple[float, float]) -> None:
        x0, y0, x1, y1 = box
        draw.rectangle(box, outline=(205, 210, 214), width=1)
        draw.text((x0 + 15, y0 + 12), title, fill=(37, 42, 46), font=font)
        px0, py0, px1, py1 = x0 + 60, y0 + 55, x1 - 20, y1 - 75
        draw.line((px0, py1, px1, py1), fill=(125, 131, 137), width=1)
        draw.line((px0, py0, px0, py1), fill=(125, 131, 137), width=1)
        ymin, ymax = yrange
        for tick in np.linspace(ymin, ymax, 5):
            y = py1 - (float(tick) - ymin) / (ymax - ymin) * (py1 - py0)
            draw.line((px0, y, px1, y), fill=(231, 233, 235), width=1)
            draw.text((x0 + 8, y - 7), f"{tick:.3f}", fill=(95, 101, 107), font=small)
        for label, values, color, width in series:
            points = [
                (
                    px0 + float(tx) * (px1 - px0),
                    py1 - (float(value) - ymin) / (ymax - ymin) * (py1 - py0),
                )
                for tx, value in zip(progress, values)
            ]
            draw.line(points, fill=color, width=width)
        legend_x, legend_y = x0 + 15, y1 - 55
        for label, _, color, _ in series:
            draw.line((legend_x, legend_y + 7, legend_x + 18, legend_y + 7), fill=color, width=3)
            draw.text((legend_x + 23, legend_y), label, fill=(70, 76, 82), font=small)
            legend_x += max(92, 32 + 6 * len(label))
        draw.text((px0 + 105, y1 - 24), "normalized log-gate progress", fill=(90, 96, 102), font=small)

    panel(
        boxes[0], "Candidate survivor path",
        [
            ("Observed", actual_c, (20, 29, 38), 4),
            ("Independent", predictions["candidate"]["independent_sieve"], (145, 145, 145), 2),
            ("Additive ARA", predictions["candidate"]["ara_additive_previous_rule"], (49, 107, 166), 2),
            ("Multiplicative", predictions["candidate"]["ara_multiplicative_primary"], (107, 76, 165), 3),
            ("Buchstab", predictions["candidate"]["buchstab_established"], (209, 122, 52), 3),
        ], (0.24, 1.0),
    )
    panel(
        boxes[1], "Adjacent-pair survivor path",
        [
            ("Observed", actual_e, (20, 29, 38), 4),
            ("Independent²", predictions["edge"]["independent_pair"], (145, 145, 145), 2),
            ("Additive ARA", predictions["edge"]["ara_additive_edge_previous_rule"], (49, 107, 166), 2),
            ("Multiplicative", predictions["edge"]["ara_multiplicative_primary"], (107, 76, 165), 3),
            ("Buchstab+J", predictions["edge"]["buchstab_plus_source_relation"], (209, 122, 52), 3),
        ], (0.04, 1.0),
    )
    combined = np.concatenate([k8, k9, k10, j8, j9, j10])
    margin = max(0.005, 0.08 * float(combined.max() - combined.min()))
    panel(
        boxes[2], "Vertical log-ratio k (solid) and pair relation J (light)",
        [
            ("k R8", k8, (158, 189, 218), 2),
            ("k R9", k9, (61, 119, 174), 3),
            ("k R10", k10, (22, 66, 105), 4),
            ("J R8", j8, (235, 183, 136), 2),
            ("J R9", j9, (208, 126, 60), 3),
            ("J R10", j10, (145, 73, 25), 4),
        ], (float(combined.min() - margin), float(combined.max() + margin)),
    )
    image.save(FIGURE)


def main() -> None:
    manifest = json.loads(FREEZE_MANIFEST.read_text(encoding="utf-8"))
    if sha256(FROZEN) != manifest["files"][FROZEN.name]:
        raise AssertionError("Prediction packet changed after freeze")
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    target = json.loads(TARGET.read_text(encoding="utf-8"))
    if target["freeze_evidence"]["prediction_packet_sha256_observed_before_open"] != sha256(FROZEN):
        raise AssertionError("Target was not built against the current frozen packet")

    predictions = {
        entity: {model: np.asarray(values, dtype=float) for model, values in models.items()}
        for entity, models in frozen["predictions"].items()
    }
    actual = {
        entity: {
            field: np.asarray(target[entity][field], dtype=float if field in ("survival", "hazard") else np.int64)
            for field in ("before", "deaths", "survival", "hazard")
        }
        for entity in ("candidate", "edge")
    }
    scores: dict[str, dict[str, dict[str, float]]] = {"candidate": {}, "edge": {}}
    for entity in ("candidate", "edge"):
        for model, path in predictions[entity].items():
            scores[entity][model] = path_score(path, actual[entity]["before"], actual[entity]["deaths"], actual[entity]["survival"])

    independent = predictions["candidate"]["independent_sieve"]
    k10 = np.log(actual["candidate"]["survival"] / independent)
    j10 = np.log(actual["edge"]["survival"] / actual["candidate"]["survival"] ** 2)
    source = {key: np.asarray(value, dtype=float) for key, value in frozen["source_coordinates"].items()}
    k8, k9 = source["r8_k_candidate"], source["r9_k_candidate"]
    j8, j9 = source["r8_j_pair"], source["r9_j_pair"]
    relation_rmse = {
        "k_r9_to_r10": float(np.sqrt(np.mean((k9 - k10) ** 2))),
        "k_r8_to_r10": float(np.sqrt(np.mean((k8 - k10) ** 2))),
        "j_r9_to_r10": float(np.sqrt(np.mean((j9 - j10) ** 2))),
        "j_r8_to_r10": float(np.sqrt(np.mean((j8 - j10) ** 2))),
    }

    c = scores["candidate"]
    e = scores["edge"]
    p1 = (
        c["ara_multiplicative_primary"]["log_loss_bits_per_at_risk_event"]
        < min(c["independent_sieve"]["log_loss_bits_per_at_risk_event"], c["ara_additive_previous_rule"]["log_loss_bits_per_at_risk_event"])
        and c["ara_multiplicative_primary"]["terminal_absolute_relative_error"] < 0.01
    )
    p2 = (
        e["ara_multiplicative_primary"]["log_loss_bits_per_at_risk_event"]
        < min(e["independent_pair"]["log_loss_bits_per_at_risk_event"], e["ara_additive_edge_previous_rule"]["log_loss_bits_per_at_risk_event"])
        and e["ara_multiplicative_primary"]["terminal_absolute_relative_error"] < 0.01
    )
    p3 = relation_rmse["k_r9_to_r10"] < relation_rmse["k_r8_to_r10"] and relation_rmse["j_r9_to_r10"] < relation_rmse["j_r8_to_r10"]
    p4 = c["ara_multiplicative_primary"]["log_loss_bits_per_at_risk_event"] < c["buchstab_established"]["log_loss_bits_per_at_risk_event"]
    p5 = e["ara_multiplicative_primary"]["log_loss_bits_per_at_risk_event"] < e["buchstab_plus_source_relation"]["log_loss_bits_per_at_risk_event"]
    p6 = frozen["clipping_adjustments"]["candidate__ara_multiplicative_primary"] == 0 and frozen["clipping_adjustments"]["edge__ara_multiplicative_primary"] == 0

    terminal_actual = {
        "candidate": float(actual["candidate"]["survival"][-1]),
        "edge": float(actual["edge"]["survival"][-1]),
    }
    terminal_established = {
        "candidate_mertens_pnt_prediction": float(frozen["terminal_constants"]["candidate_mertens_pnt_prediction"]),
        "candidate_mertens_pnt_absolute_relative_error": abs(float(frozen["terminal_constants"]["candidate_mertens_pnt_prediction"]) - terminal_actual["candidate"]) / terminal_actual["candidate"],
        "edge_mertens_pnt_squared_prediction": float(frozen["terminal_constants"]["edge_mertens_pnt_squared_prediction"]),
        "edge_mertens_pnt_squared_absolute_relative_error": abs(float(frozen["terminal_constants"]["edge_mertens_pnt_squared_prediction"]) - terminal_actual["edge"]) / terminal_actual["edge"],
    }
    observed_ratios = {
        "candidate_terminal_k": float(k10[-1]),
        "candidate_terminal_survival_over_independent": float(np.exp(k10[-1])),
        "edge_terminal_j": float(j10[-1]),
        "edge_terminal_survival_over_independent": float(actual["edge"]["survival"][-1] / predictions["edge"]["independent_pair"][-1]),
    }

    progress = np.asarray(frozen["gate_path"]["progress"], dtype=float)
    with PATHS.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = ["cell", "progress", "q_end", "candidate_before", "candidate_deaths", "candidate_survival", "candidate_k", "edge_before", "edge_deaths", "edge_survival", "edge_j"]
        for entity in ("candidate", "edge"):
            fieldnames.extend(f"prediction__{entity}__{model}" for model in predictions[entity])
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(len(progress)):
            row: dict[str, Any] = {
                "cell": i + 1,
                "progress": progress[i],
                "q_end": frozen["gate_path"]["q_end"][i],
                "candidate_before": int(actual["candidate"]["before"][i]),
                "candidate_deaths": int(actual["candidate"]["deaths"][i]),
                "candidate_survival": actual["candidate"]["survival"][i],
                "candidate_k": k10[i],
                "edge_before": int(actual["edge"]["before"][i]),
                "edge_deaths": int(actual["edge"]["deaths"][i]),
                "edge_survival": actual["edge"]["survival"][i],
                "edge_j": j10[i],
            }
            for entity in ("candidate", "edge"):
                for model, path in predictions[entity].items():
                    row[f"prediction__{entity}__{model}"] = path[i]
            writer.writerow(ready(row))

    make_figure(progress, actual["candidate"]["survival"], actual["edge"]["survival"], predictions, k8, k9, k10, j8, j9, j10)
    results = {
        "test_id": frozen["test_id"],
        "status": "FRESH R10 TARGET SCORED AGAINST PRE-TARGET HASHED PREDICTIONS",
        "freeze_integrity": {
            "prediction_packet_sha256": sha256(FROZEN),
            "matches_freeze_manifest": sha256(FROZEN) == manifest["files"][FROZEN.name],
            "target_builder_verified_hash_before_open": target["freeze_evidence"]["matched"],
        },
        "target_summary": {
            "low": target["target"]["low"],
            "high": target["target"]["high"],
            "candidate_n0": target["candidate"]["n0"],
            "edge_n0": target["edge"]["n0"],
            "candidate_terminal_survivors": target["candidate"]["terminal_survivors"],
            "edge_terminal_survivors": target["edge"]["terminal_survivors"],
            "candidate_terminal_survival": terminal_actual["candidate"],
            "edge_terminal_survival": terminal_actual["edge"],
        },
        "scores": scores,
        "relation_path_rmse": relation_rmse,
        "observed_terminal_relations": observed_ratios,
        "terminal_established_comparators": terminal_established,
        "criteria": {
            "P1_candidate_primary_beats_independent_and_additive_with_sub1pct_terminal": bool(p1),
            "P2_edge_primary_beats_independent_and_additive_with_sub1pct_terminal": bool(p2),
            "P3_nearest_rung_k_and_j_recurrence": bool(p3),
            "P4_candidate_primary_beats_buchstab_path": bool(p4),
            "P5_edge_primary_beats_buchstab_plus_source_j": bool(p5),
            "P6_primary_paths_need_no_repair": bool(p6),
        },
        "calibration": frozen["equivalence_disclosure"],
        "hashes": {
            PROTOCOL.name: sha256(PROTOCOL),
            FROZEN.name: sha256(FROZEN),
            TARGET.name: sha256(TARGET),
            Path(__file__).name: sha256(Path(__file__)),
        },
    }
    RESULTS.write_text(json.dumps(ready(results), indent=2) + "\n", encoding="utf-8")
    artifact = {
        "test_id": results["test_id"],
        "files": {path.name: sha256(path) for path in (PROTOCOL, FROZEN, TARGET, Path(__file__), RESULTS, PATHS, FIGURE)},
    }
    ARTIFACT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": results["status"], "criteria": results["criteria"], "target_summary": results["target_summary"]}, indent=2))


if __name__ == "__main__":
    main()
