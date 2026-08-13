"""T344: frozen Irrationality Di-ARA test on BAW weir particle tracks.

The source is DOI 10.48437/99f329-73aee6.  This implementation reads the
wide x/y trajectory workbooks directly from their XML containers so the native
0.01 s samples are not converted, smoothed or interpolated.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import minimize


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source_baw_weir"
CONDITIONS = ("low", "medium", "high")
REPRESENTATION = os.environ.get("T344_REPRESENTATION", "lab").strip().lower()
if REPRESENTATION not in {"lab", "num"}:
    raise ValueError("T344_REPRESENTATION must be 'lab' or 'num'")
OUTPUT_PREFIX = (
    "T344_BAW_WEIR_IRRATIONALITY_DI_ARA"
    if REPRESENTATION == "lab"
    else "T344_BAW_WEIR_IRRATIONALITY_DI_ARA_NUMERICAL_REPLICATION"
)
VERTICAL_SIGN = -1.0 if REPRESENTATION == "lab" else 1.0
POSITION_UNIT = "px" if REPRESENTATION == "lab" else "m"
FILES = {c: SOURCE / f"Spheres_{REPRESENTATION}_{c}.xlsx" for c in CONDITIONS}
EXPECTED_HASHES = (
    {
        "low": "bf6bf4536bccabb6cb1991db52b2b630bed65de25475482d229bf1552cfbf549",
        "medium": "d42724a1f136a3b3b4d1e37a90cfb9e9bc2c4319d86392a89ff34e1ab62a70a7",
        "high": "2dfd229ac0561a5fc6601ddf9052f13d391b8e54862ea5e09d099a40af91064e",
    }
    if REPRESENTATION == "lab"
    else {
        "low": "6b4b30f532cfca965da92d73f92c100ed429cd5a2078a7c7dfc18d1eaf7bdfdd",
        "medium": "feb38f39468a64df5ef50d292b8edbe716f9a4bdd1d76782147d11c0b43a6632",
        "high": "4a3e737bfdb66ad913d08fe182d563e573648820e105da73726b88af6eb07eab",
    }
)
SECTOR_NAMES = np.array(["Ba", "Ab", "bA", "aB"], dtype=object)
SECTOR_COLORS = {"Ba": "#5B8FF9", "Ab": "#61DDAA", "bA": "#F6BD16", "aB": "#E8684A"}
CLASS_NAMES = {0: "low-order closure", 1: "structured non-closing", 2: "random-like", 3: "unclassified"}
RNG_SEED = 344
RIDGE_TOL = 1e-12
BOOTSTRAPS = 2000

NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def column_number(cell_ref: str) -> int:
    match = re.match(r"([A-Z]+)", cell_ref)
    if not match:
        raise ValueError(f"Bad cell reference: {cell_ref}")
    value = 0
    for char in match.group(1):
        value = value * 26 + ord(char) - 64
    return value


def numeric_cell(cell: ET.Element) -> float | None:
    value = cell.find(f"{{{NS_MAIN}}}v")
    if value is None or value.text is None:
        return None
    try:
        return float(value.text)
    except ValueError:
        return None


def workbook_sheet_paths(archive: zipfile.ZipFile) -> dict[str, str]:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    targets = {
        relation.attrib["Id"]: relation.attrib["Target"]
        for relation in relationships.findall(f"{{{NS_PKG_REL}}}Relationship")
    }
    paths = {}
    for sheet in workbook.findall(f".//{{{NS_MAIN}}}sheet"):
        name = sheet.attrib["name"]
        relation_id = sheet.attrib[f"{{{NS_REL}}}id"]
        target = targets[relation_id].replace("\\", "/")
        if target.startswith("/"):
            target = target[1:]
        elif not target.startswith("xl/"):
            target = "xl/" + target
        paths[name] = target
    return paths


def parse_coordinate_sheet(archive: zipfile.ZipFile, member: str) -> tuple[dict[int, dict[int, float]], dict]:
    """Return particle -> frame -> coordinate and a structural audit."""
    headers: dict[int, int] = {}
    tracks: dict[int, dict[int, float]] = defaultdict(dict)
    duplicates = 0
    invalid_times = 0
    data_cells = 0
    min_time = math.inf
    max_time = -math.inf

    with archive.open(member) as stream:
        for _, row in ET.iterparse(stream, events=("end",)):
            if row.tag != f"{{{NS_MAIN}}}row":
                continue
            row_number = int(row.attrib.get("r", "0"))
            cells = row.findall(f"{{{NS_MAIN}}}c")
            if row_number == 3:
                for cell in cells:
                    col = column_number(cell.attrib["r"])
                    if col == 1:
                        continue
                    value = numeric_cell(cell)
                    if value is not None and math.isfinite(value):
                        headers[col] = int(round(value))
            elif row_number >= 5:
                time_value = None
                for cell in cells:
                    if column_number(cell.attrib["r"]) == 1:
                        time_value = numeric_cell(cell)
                        break
                if time_value is None or not math.isfinite(time_value):
                    row.clear()
                    continue
                frame = int(round(time_value * 100.0))
                if abs(time_value - frame / 100.0) > 1e-8:
                    invalid_times += 1
                    row.clear()
                    continue
                min_time = min(min_time, time_value)
                max_time = max(max_time, time_value)
                for cell in cells:
                    col = column_number(cell.attrib["r"])
                    if col == 1 or col not in headers:
                        continue
                    value = numeric_cell(cell)
                    if value is None or not math.isfinite(value):
                        continue
                    particle = headers[col]
                    if frame in tracks[particle]:
                        duplicates += 1
                    else:
                        tracks[particle][frame] = value
                        data_cells += 1
            row.clear()

    audit = {
        "header_particles": len(set(headers.values())),
        "header_columns": len(headers),
        "duplicate_particle_headers": len(headers) - len(set(headers.values())),
        "data_cells": data_cells,
        "duplicate_particle_frames": duplicates,
        "invalid_time_rows": invalid_times,
        "min_time_s": None if min_time == math.inf else min_time,
        "max_time_s": None if max_time == -math.inf else max_time,
    }
    return dict(tracks), audit


def load_condition(condition: str) -> tuple[list[dict], dict]:
    path = FILES[condition]
    with zipfile.ZipFile(path) as archive:
        sheet_paths = workbook_sheet_paths(archive)
        x_raw, x_audit = parse_coordinate_sheet(archive, sheet_paths["x"])
        y_raw, y_audit = parse_coordinate_sheet(archive, sheet_paths["y"])

    x_ids, y_ids = set(x_raw), set(y_raw)
    tracks = []
    no_overlap = 0
    duplicate_join_frames = 0
    for particle in sorted(x_ids & y_ids):
        frames = np.array(sorted(set(x_raw[particle]) & set(y_raw[particle])), dtype=np.int32)
        if frames.size == 0:
            no_overlap += 1
            continue
        x = np.array([x_raw[particle][int(frame)] for frame in frames], dtype=np.float64)
        y = np.array([y_raw[particle][int(frame)] for frame in frames], dtype=np.float64)
        if len(np.unique(frames)) != len(frames):
            duplicate_join_frames += len(frames) - len(np.unique(frames))
        tracks.append(
            {
                "condition": condition,
                "particle_id": int(particle),
                "track_id": f"{condition}:{int(particle)}",
                "frames": frames,
                "time": frames.astype(np.float64) / 100.0,
                "x": x,
                "z": VERTICAL_SIGN * y,
            }
        )
    audit = {
        "condition": condition,
        "file": path.name,
        "file_bytes": path.stat().st_size,
        "sha256": sha256(path),
        "sha256_matches_official": sha256(path) == EXPECTED_HASHES[condition],
        "x_header_particles": x_audit["header_particles"],
        "y_header_particles": y_audit["header_particles"],
        "common_particle_ids": len(x_ids & y_ids),
        "x_only_particle_ids": len(x_ids - y_ids),
        "y_only_particle_ids": len(y_ids - x_ids),
        "joined_tracks": len(tracks),
        "tracks_without_overlap": no_overlap,
        "duplicate_join_frames": duplicate_join_frames,
        "joined_positions": int(sum(len(track["frames"]) for track in tracks)),
        "x_data_cells": x_audit["data_cells"],
        "y_data_cells": y_audit["data_cells"],
        "x_duplicate_particle_frames": x_audit["duplicate_particle_frames"],
        "y_duplicate_particle_frames": y_audit["duplicate_particle_frames"],
        "x_invalid_time_rows": x_audit["invalid_time_rows"],
        "y_invalid_time_rows": y_audit["invalid_time_rows"],
        "min_time_s": min((track["time"][0] for track in tracks), default=np.nan),
        "max_time_s": max((track["time"][-1] for track in tracks), default=np.nan),
    }
    return tracks, audit


def contiguous_runs(frames: np.ndarray) -> list[np.ndarray]:
    if frames.size == 0:
        return []
    cuts = np.flatnonzero(np.diff(frames) != 1) + 1
    return [part for part in np.split(np.arange(frames.size), cuts) if part.size]


def sector_code(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    sector = np.full(x.shape, -1, dtype=np.int8)
    away = (np.abs(x - 1.0) > RIDGE_TOL) & (np.abs(y - 1.0) > RIDGE_TOL)
    contraction = x < 1.0
    forward = y > 1.0
    sector[away & contraction & forward] = 0
    sector[away & ~contraction & forward] = 1
    sector[away & contraction & ~forward] = 2
    sector[away & ~contraction & ~forward] = 3
    return sector


def derive_track_events(track: dict, epsilon_multiplier: float = 1e-9) -> dict:
    chunks = []
    excluded_near_zero = 0
    for indexes in contiguous_runs(track["frames"]):
        if indexes.size < 3:
            continue
        frames = track["frames"][indexes]
        times = track["time"][indexes]
        x = track["x"][indexes]
        z = track["z"][indexes]
        w = np.diff(x) + 1j * np.diff(z)
        speed = np.abs(w)
        positive = speed[speed > 0]
        if positive.size == 0:
            continue
        epsilon = epsilon_multiplier * float(np.median(positive))
        valid = (speed[:-1] > epsilon) & (speed[1:] > epsilon)
        excluded_near_zero += int((~valid).sum())
        if not np.any(valid):
            continue
        ratio = np.empty(speed.size - 1, dtype=np.complex128)
        ratio[:] = np.nan + 1j * np.nan
        ratio[valid] = w[1:][valid] / w[:-1][valid]
        s = np.abs(ratio)
        delta = np.angle(ratio)
        ara_x = 2.0 * s / (1.0 + s)
        ara_y = 1.0 + delta / np.pi
        sectors = sector_code(ara_x, ara_y)
        chunks.append(
            {
                "frame": frames[2:],
                "time": times[2:],
                "x_pos": x[2:],
                "z_pos": z[2:],
                "dx": w[1:].real,
                "dz": w[1:].imag,
                "speed": speed[1:] / 0.01,
                "s": s,
                "delta": delta,
                "ara_x": ara_x,
                "ara_y": ara_y,
                "sector": sectors,
            }
        )
    if not chunks:
        arrays = {key: np.array([], dtype=float) for key in ("frame", "time", "x_pos", "z_pos", "dx", "dz", "speed", "s", "delta", "ara_x", "ara_y")}
        arrays["sector"] = np.array([], dtype=np.int8)
    else:
        arrays = {key: np.concatenate([chunk[key] for chunk in chunks]) for key in chunks[0]}
    order = np.argsort(arrays["frame"], kind="stable")
    for key in arrays:
        arrays[key] = arrays[key][order]
    arrays.update(
        {
            "condition": track["condition"],
            "particle_id": track["particle_id"],
            "track_id": track["track_id"],
            "source_frames": track["frames"],
            "source_x": track["x"],
            "source_z": track["z"],
            "excluded_near_zero": excluded_near_zero,
        }
    )
    return arrays


def build_transition_frame(events: list[dict]) -> pd.DataFrame:
    parts = []
    for event in events:
        n = len(event["frame"])
        if n < 2:
            continue
        valid = (
            (np.diff(event["frame"]) == 1)
            & (event["sector"][:-1] >= 0)
            & (event["sector"][1:] >= 0)
        )
        idx = np.flatnonzero(valid)
        if idx.size == 0:
            continue
        tmin, tmax = float(event["time"].min()), float(event["time"].max())
        span = max(tmax - tmin, 1e-12)
        progress = (event["time"][idx] - tmin) / span
        x_centered = event["ara_x"][idx] - 1.0
        y_centered = event["ara_y"][idx] - 1.0
        parts.append(
            pd.DataFrame(
                {
                    "condition": event["condition"],
                    "particle_id": event["particle_id"],
                    "track_id": event["track_id"],
                    "frame": event["frame"][idx],
                    "time_s": event["time"][idx],
                    "x_px": event["x_pos"][idx],
                    "z_px": event["z_pos"][idx],
                    "s": event["s"][idx],
                    "delta": event["delta"][idx],
                    "ara_x": event["ara_x"][idx],
                    "ara_y": event["ara_y"][idx],
                    "interaction": x_centered * y_centered,
                    "dominance": np.abs(x_centered) - np.abs(y_centered),
                    "radial_side": (event["ara_x"][idx] > 1.0).astype(np.int8),
                    "turn_side": (event["ara_y"][idx] > 1.0).astype(np.int8),
                    "sector": event["sector"][idx],
                    "target_sector": event["sector"][idx + 1],
                    "progress": progress,
                    "progress_decile": np.minimum((progress * 10).astype(int), 9),
                    "speed_px_s": event["speed"][idx],
                }
            )
        )
    if not parts:
        raise RuntimeError("No valid transitions were recovered")
    result = pd.concat(parts, ignore_index=True)
    result["condition"] = pd.Categorical(result["condition"], categories=CONDITIONS)
    return result


class SoftmaxL2:
    def __init__(self, c: float = 1.0):
        self.c = c

    def fit(self, x: np.ndarray, y: np.ndarray) -> "SoftmaxL2":
        x = np.asarray(x, dtype=np.float64)
        y = np.asarray(y, dtype=np.int64)
        self.mean_ = x.mean(axis=0)
        self.std_ = x.std(axis=0)
        self.std_[self.std_ == 0] = 1.0
        xs = (x - self.mean_) / self.std_
        n, d = xs.shape
        k_minus_one = 3
        x_aug = np.column_stack([xs, np.ones(n)])

        def objective(flat: np.ndarray):
            beta = flat.reshape(d + 1, k_minus_one)
            logits = np.column_stack([x_aug @ beta, np.zeros(n)])
            logits -= logits.max(axis=1, keepdims=True)
            exp_logits = np.exp(logits)
            prob = exp_logits / exp_logits.sum(axis=1, keepdims=True)
            loss = -np.log(np.clip(prob[np.arange(n), y], 1e-15, 1.0)).mean()
            loss += 0.5 * np.square(beta[:-1]).sum() / (self.c * n)
            residual = prob[:, :k_minus_one]
            residual[np.arange(n), np.minimum(y, k_minus_one - 1)] -= (y < k_minus_one)
            grad = x_aug.T @ residual / n
            grad[:-1] += beta[:-1] / (self.c * n)
            return float(loss), grad.ravel()

        initial = np.zeros((d + 1) * k_minus_one, dtype=np.float64)
        result = minimize(
            objective,
            initial,
            method="L-BFGS-B",
            jac=True,
            options={"maxiter": 1000, "ftol": 1e-12, "gtol": 1e-9},
        )
        self.beta_ = result.x.reshape(d + 1, k_minus_one)
        self.optimisation_ = {
            "success": bool(result.success),
            "status": int(result.status),
            "message": str(result.message),
            "iterations": int(result.nit),
            "objective": float(result.fun),
            "gradient_max_abs": float(np.max(np.abs(result.jac))),
        }
        return self

    def predict_proba(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=np.float64)
        xs = (x - self.mean_) / self.std_
        x_aug = np.column_stack([xs, np.ones(len(xs))])
        logits = np.column_stack([x_aug @ self.beta_, np.zeros(len(xs))])
        logits -= logits.max(axis=1, keepdims=True)
        values = np.exp(logits)
        return values / values.sum(axis=1, keepdims=True)


def laplace_table(keys: np.ndarray, target: np.ndarray, possible_keys: list[int]) -> dict[int, np.ndarray]:
    output = {}
    for key in possible_keys:
        counts = np.ones(4, dtype=np.float64)
        mask = keys == key
        if np.any(mask):
            counts += np.bincount(target[mask], minlength=4)
        output[key] = counts / counts.sum()
    return output


def table_predict(table: dict[int, np.ndarray], keys: np.ndarray) -> np.ndarray:
    return np.vstack([table[int(key)] for key in keys])


def log_losses(prob: np.ndarray, target: np.ndarray) -> np.ndarray:
    return -np.log(np.clip(prob[np.arange(len(target)), target], 1e-15, 1.0))


def classification_scores(prob: np.ndarray, target: np.ndarray) -> dict:
    prediction = prob.argmax(axis=1)
    recalls, f1s = [], []
    for cls in range(4):
        tp = np.sum((prediction == cls) & (target == cls))
        fn = np.sum((prediction != cls) & (target == cls))
        fp = np.sum((prediction == cls) & (target != cls))
        recall = tp / (tp + fn) if tp + fn else np.nan
        precision = tp / (tp + fp) if tp + fp else np.nan
        f1 = 2 * precision * recall / (precision + recall) if np.isfinite(precision) and np.isfinite(recall) and precision + recall else np.nan
        recalls.append(recall)
        f1s.append(f1)
    return {
        "log_loss": float(log_losses(prob, target).mean()),
        "accuracy": float((prediction == target).mean()),
        "balanced_accuracy": float(np.nanmean(recalls)),
        "macro_f1": float(np.nanmean(f1s)),
    }


def deterministic_donor_map(frame: pd.DataFrame) -> np.ndarray:
    result = np.full(len(frame), np.nan, dtype=np.float64)
    by_condition = frame.groupby("condition", observed=True, sort=False)
    for condition, condition_frame in by_condition:
        track_ids = sorted(
            condition_frame["track_id"].unique(),
            key=lambda value: hashlib.sha256(value.encode("utf-8")).hexdigest(),
        )
        if len(track_ids) < 2:
            continue
        groups = {
            track_id: group.sort_values("progress")
            for track_id, group in condition_frame.groupby("track_id", sort=False)
        }
        for index, track_id in enumerate(track_ids):
            recipient = groups[track_id]
            donor_id = track_ids[(index + 1) % len(track_ids)]
            donor = groups[donor_id]
            for decile, recipient_bin in recipient.groupby("progress_decile", sort=False):
                donor_bin = donor[donor["progress_decile"] == decile]
                if donor_bin.empty:
                    continue
                donor_progress = donor_bin["progress"].to_numpy()
                donor_y = donor_bin["ara_y"].to_numpy()
                order = np.argsort(donor_progress)
                donor_progress, donor_y = donor_progress[order], donor_y[order]
                values = recipient_bin["progress"].to_numpy()
                positions = np.searchsorted(donor_progress, values)
                positions = np.clip(positions, 0, len(donor_progress) - 1)
                left = np.maximum(positions - 1, 0)
                choose_left = np.abs(donor_progress[left] - values) <= np.abs(donor_progress[positions] - values)
                nearest = np.where(choose_left, left, positions)
                result[recipient_bin.index.to_numpy()] = donor_y[nearest]
    return result


def fit_and_score_folds(transitions: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[dict]]:
    transitions = transitions.copy()
    transitions["broken_y"] = deterministic_donor_map(transitions)
    model_rows, track_rows, prediction_parts, optimiser_rows = [], [], [], []
    for test_condition in CONDITIONS:
        train = transitions[transitions["condition"] != test_condition]
        test = transitions[transitions["condition"] == test_condition].copy()
        y_train = train["target_sector"].to_numpy(dtype=np.int64)
        y_test = test["target_sector"].to_numpy(dtype=np.int64)

        global_counts = np.ones(4) + np.bincount(y_train, minlength=4)
        global_prob = global_counts / global_counts.sum()
        probabilities = {
            "global": np.tile(global_prob, (len(test), 1)),
            "persistence": np.full((len(test), 4), 0.01),
        }
        probabilities["persistence"][np.arange(len(test)), test["sector"].to_numpy(dtype=int)] = 0.97
        radial_table = laplace_table(train["radial_side"].to_numpy(), y_train, [0, 1])
        turn_table = laplace_table(train["turn_side"].to_numpy(), y_train, [0, 1])
        probabilities["radial_child"] = table_predict(radial_table, test["radial_side"].to_numpy())
        probabilities["turn_child"] = table_predict(turn_table, test["turn_side"].to_numpy())

        additive_columns = ["ara_x", "ara_y"]
        intact_columns = ["ara_x", "ara_y", "interaction", "dominance"]
        additive_train = train[additive_columns].to_numpy() - np.array([1.0, 1.0])
        additive_test = test[additive_columns].to_numpy() - np.array([1.0, 1.0])
        intact_train = train[intact_columns].to_numpy().copy()
        intact_test = test[intact_columns].to_numpy().copy()
        intact_train[:, :2] -= 1.0
        intact_test[:, :2] -= 1.0

        additive = SoftmaxL2().fit(additive_train, y_train)
        intact = SoftmaxL2().fit(intact_train, y_train)
        probabilities["additive_children"] = additive.predict_proba(additive_test)
        probabilities["intact_parent"] = intact.predict_proba(intact_test)
        optimiser_rows.extend(
            [
                {"test_condition": test_condition, "model": "additive_children", **additive.optimisation_},
                {"test_condition": test_condition, "model": "intact_parent", **intact.optimisation_},
            ]
        )

        broken_train_mask = np.isfinite(train["broken_y"].to_numpy())
        broken_test_mask = np.isfinite(test["broken_y"].to_numpy())
        broken_train = train.loc[broken_train_mask]
        broken_y_train = broken_train["broken_y"].to_numpy()
        bx = broken_train["ara_x"].to_numpy() - 1.0
        by = broken_y_train - 1.0
        broken_train_features = np.column_stack([bx, by, bx * by, np.abs(bx) - np.abs(by)])
        broken_model = SoftmaxL2().fit(broken_train_features, broken_train["target_sector"].to_numpy(dtype=np.int64))
        broken_probability = np.full((len(test), 4), np.nan)
        bx_test = test.loc[broken_test_mask, "ara_x"].to_numpy() - 1.0
        by_test = test.loc[broken_test_mask, "broken_y"].to_numpy() - 1.0
        broken_test_features = np.column_stack([bx_test, by_test, bx_test * by_test, np.abs(bx_test) - np.abs(by_test)])
        broken_probability[broken_test_mask] = broken_model.predict_proba(broken_test_features)
        probabilities["broken_parent"] = broken_probability
        optimiser_rows.append({"test_condition": test_condition, "model": "broken_parent", **broken_model.optimisation_})

        pred_part = test[["condition", "particle_id", "track_id", "frame", "sector", "target_sector"]].copy()
        for model_name, prob in probabilities.items():
            valid = np.isfinite(prob).all(axis=1)
            scores = classification_scores(prob[valid], y_test[valid])
            model_rows.append(
                {
                    "test_condition": test_condition,
                    "model": model_name,
                    "events": int(valid.sum()),
                    "excluded": int((~valid).sum()),
                    **scores,
                }
            )
            loss = np.full(len(test), np.nan)
            loss[valid] = log_losses(prob[valid], y_test[valid])
            pred_part[f"loss_{model_name}"] = loss
            pred_part[f"prediction_{model_name}"] = np.where(valid, np.nanargmax(np.where(np.isfinite(prob), prob, -1), axis=1), -1)
        prediction_parts.append(pred_part)

        loss_columns = [column for column in pred_part if column.startswith("loss_")]
        for track_id, group in pred_part.groupby("track_id", sort=False):
            row = {
                "test_condition": test_condition,
                "track_id": track_id,
                "particle_id": int(group["particle_id"].iloc[0]),
                "events": len(group),
            }
            for column in loss_columns:
                row[column] = float(group[column].mean())
            track_rows.append(row)

    return (
        pd.DataFrame(model_rows),
        pd.DataFrame(track_rows),
        pd.concat(prediction_parts, ignore_index=True),
        optimiser_rows,
    )


def bootstrap_mean_difference(values: np.ndarray, replicates: int = BOOTSTRAPS) -> dict:
    values = np.asarray(values, dtype=np.float64)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return {"estimate": np.nan, "ci_low": np.nan, "ci_high": np.nan, "n_tracks": 0}
    rng = np.random.default_rng(RNG_SEED)
    estimates = np.empty(replicates)
    for index in range(replicates):
        estimates[index] = rng.choice(values, size=len(values), replace=True).mean()
    return {
        "estimate": float(values.mean()),
        "ci_low": float(np.quantile(estimates, 0.025)),
        "ci_high": float(np.quantile(estimates, 0.975)),
        "n_tracks": int(values.size),
    }


def model_bootstraps(track_scores: pd.DataFrame) -> pd.DataFrame:
    comparisons = {
        "intact_vs_radial_child": "loss_radial_child",
        "intact_vs_turn_child": "loss_turn_child",
        "intact_vs_broken_parent": "loss_broken_parent",
        "intact_vs_additive_children": "loss_additive_children",
        "intact_vs_persistence": "loss_persistence",
        "intact_vs_global": "loss_global",
    }
    rows = []
    for name, baseline_column in comparisons.items():
        improvement = track_scores[baseline_column] - track_scores["loss_intact_parent"]
        result = bootstrap_mean_difference(improvement.to_numpy())
        fold_wins = 0
        fold_effects = {}
        for condition in CONDITIONS:
            fold = track_scores[track_scores["test_condition"] == condition]
            effect = float((fold[baseline_column] - fold["loss_intact_parent"]).mean())
            fold_effects[condition] = effect
            fold_wins += int(effect > 0)
        rows.append({"comparison": name, "fold_wins": fold_wins, **fold_effects, **result})
    return pd.DataFrame(rows)


def rational_set(max_denominator: int = 8) -> np.ndarray:
    values = set()
    for denominator in range(1, max_denominator + 1):
        for numerator in range(denominator):
            values.add(numerator / denominator)
    return np.array(sorted(values), dtype=np.float64)


RATIONALS_8 = rational_set(8)


def wrapped_unit_distance(value: float, candidates: np.ndarray) -> float:
    raw = np.abs(candidates - (value % 1.0))
    return float(np.minimum(raw, 1.0 - raw).min())


def build_windows(events: list[dict], window: int) -> pd.DataFrame:
    parts = []
    threshold = 1.0 / (2.0 * window)
    for event in events:
        if len(event["frame"]) < window + 1:
            continue
        tmin, tmax = float(event["time"].min()), float(event["time"].max())
        span = max(tmax - tmin, 1e-12)
        for run in contiguous_runs(event["frame"]):
            if run.size < window + 1:
                continue
            for offset in range(run.size - window):
                indexes = run[offset : offset + window]
                target_index = run[offset + window]
                current_index = indexes[0]
                if event["sector"][current_index] < 0 or event["sector"][target_index] < 0:
                    continue
                angles = event["delta"][indexes]
                if not np.isfinite(angles).all():
                    continue
                resultant = np.mean(np.exp(1j * angles))
                coherence = abs(resultant)
                rho = (np.angle(resultant) / (2.0 * np.pi)) % 1.0
                distance = wrapped_unit_distance(rho, RATIONALS_8)
                if coherence >= 0.75 and distance <= threshold:
                    closure_class = 0
                elif coherence >= 0.75 and distance > threshold:
                    closure_class = 1
                elif coherence <= 0.25:
                    closure_class = 2
                else:
                    closure_class = 3
                positions = np.column_stack([event["x_pos"][run[offset : offset + window + 1]], event["z_pos"][run[offset : offset + window + 1]]])
                steps = np.linalg.norm(np.diff(positions, axis=0), axis=1)
                path_length = float(steps.sum())
                traversal = float(np.linalg.norm(positions[-1] - positions[0]) / path_length) if path_length > 0 else np.nan
                sectors = event["sector"][indexes]
                valid_pairs = (sectors[:-1] >= 0) & (sectors[1:] >= 0)
                handover = float(np.mean(sectors[:-1][valid_pairs] != sectors[1:][valid_pairs])) if valid_pairs.any() else np.nan
                reverse = float(np.mean(event["dx"][indexes] < 0))
                xc = event["ara_x"][current_index] - 1.0
                yc = event["ara_y"][current_index] - 1.0
                progress = (event["time"][current_index] - tmin) / span
                parts.append(
                    {
                        "condition": event["condition"],
                        "particle_id": event["particle_id"],
                        "track_id": event["track_id"],
                        "window": window,
                        "frame": int(event["frame"][current_index]),
                        "time_s": float(event["time"][current_index]),
                        "ara_x": float(event["ara_x"][current_index]),
                        "ara_y": float(event["ara_y"][current_index]),
                        "interaction": float(xc * yc),
                        "dominance": float(abs(xc) - abs(yc)),
                        "sector": int(event["sector"][current_index]),
                        "target_sector": int(event["sector"][target_index]),
                        "coherence": float(coherence),
                        "rotation_number": float(rho),
                        "rational_distance_q8": float(distance),
                        "closure_class": closure_class,
                        "traversal": traversal,
                        "path_length_px": path_length,
                        "handover_rate": handover,
                        "reverse_flow_rate": reverse,
                        "progress": float(progress),
                        "progress_decile": min(int(progress * 10), 9),
                        "speed_px_s": float(event["speed"][current_index]),
                        "x_px": float(event["x_pos"][current_index]),
                        "z_px": float(event["z_pos"][current_index]),
                    }
                )
    return pd.DataFrame(parts)


def score_window_information(windows: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    windows = windows.copy()
    windows["information_nats"] = np.nan
    windows["speed_quintile"] = -1
    optimiser = []
    for test_condition in CONDITIONS:
        train = windows[windows["condition"] != test_condition]
        test_index = windows.index[windows["condition"] == test_condition]
        test = windows.loc[test_index]
        columns = ["ara_x", "ara_y", "interaction", "dominance"]
        train_x = train[columns].to_numpy().copy()
        test_x = test[columns].to_numpy().copy()
        train_x[:, :2] -= 1.0
        test_x[:, :2] -= 1.0
        model = SoftmaxL2().fit(train_x, train["target_sector"].to_numpy(dtype=np.int64))
        probability = model.predict_proba(test_x)
        counts = np.ones(4) + np.bincount(train["target_sector"].to_numpy(dtype=np.int64), minlength=4)
        base = counts / counts.sum()
        target = test["target_sector"].to_numpy(dtype=np.int64)
        information = np.log(np.clip(probability[np.arange(len(test)), target], 1e-15, 1.0)) - np.log(base[target])
        windows.loc[test_index, "information_nats"] = information
        edges = np.quantile(train["speed_px_s"], [0.2, 0.4, 0.6, 0.8])
        windows.loc[test_index, "speed_quintile"] = np.searchsorted(edges, test["speed_px_s"].to_numpy(), side="right")
        optimiser.append({"test_condition": test_condition, "model": f"window_{int(windows['window'].iloc[0])}_intact", **model.optimisation_})
    return windows, optimiser


def stratified_point_difference(frame: pd.DataFrame, class_a: int, class_b: int, metric: str) -> tuple[float, int]:
    track_means = (
        frame[frame["closure_class"].isin([class_a, class_b])]
        .groupby(["condition", "progress_decile", "speed_quintile", "closure_class", "track_id"], observed=True)[metric]
        .mean()
        .reset_index()
    )
    differences = []
    for _, group in track_means.groupby(["condition", "progress_decile", "speed_quintile"], observed=True):
        a = group[group["closure_class"] == class_a][metric]
        b = group[group["closure_class"] == class_b][metric]
        if len(a) and len(b):
            differences.append(float(a.mean() - b.mean()))
    return (float(np.mean(differences)) if differences else np.nan, len(differences))


def stratified_cluster_bootstrap(frame: pd.DataFrame, class_a: int, class_b: int, metric: str) -> dict:
    selected = frame[frame["closure_class"].isin([class_a, class_b])].copy()
    aggregate = (
        selected.groupby(["condition", "progress_decile", "speed_quintile", "closure_class", "track_id"], observed=True)[metric]
        .mean()
        .reset_index()
    )
    track_ids = sorted(aggregate["track_id"].unique())
    track_index = {track: index for index, track in enumerate(track_ids)}
    condition_tracks = {
        condition: [track_index[value] for value in aggregate.loc[aggregate["condition"] == condition, "track_id"].unique()]
        for condition in CONDITIONS
    }
    groups = {}
    for key, group in aggregate.groupby(["condition", "progress_decile", "speed_quintile", "closure_class"], observed=True):
        groups[key] = (
            np.array([track_index[value] for value in group["track_id"]], dtype=np.int32),
            group[metric].to_numpy(dtype=np.float64),
        )
    strata = sorted(set(key[:3] for key in groups))

    def calculate(counts: np.ndarray) -> tuple[float, int]:
        differences = []
        for stratum in strata:
            key_a, key_b = (*stratum, class_a), (*stratum, class_b)
            if key_a not in groups or key_b not in groups:
                continue
            idx_a, val_a = groups[key_a]
            idx_b, val_b = groups[key_b]
            weight_a, weight_b = counts[idx_a], counts[idx_b]
            if weight_a.sum() == 0 or weight_b.sum() == 0:
                continue
            mean_a = float(np.dot(weight_a, val_a) / weight_a.sum())
            mean_b = float(np.dot(weight_b, val_b) / weight_b.sum())
            differences.append(mean_a - mean_b)
        return (float(np.mean(differences)) if differences else np.nan, len(differences))

    base_counts = np.ones(len(track_ids), dtype=np.int32)
    estimate, strata_count = calculate(base_counts)
    rng = np.random.default_rng(RNG_SEED)
    samples = []
    for _ in range(BOOTSTRAPS):
        counts = np.zeros(len(track_ids), dtype=np.int32)
        for indices in condition_tracks.values():
            if not indices:
                continue
            draw = rng.choice(indices, size=len(indices), replace=True)
            counts += np.bincount(draw, minlength=len(track_ids)).astype(np.int32)
        value, _ = calculate(counts)
        if np.isfinite(value):
            samples.append(value)
    return {
        "estimate": estimate,
        "ci_low": float(np.quantile(samples, 0.025)) if samples else np.nan,
        "ci_high": float(np.quantile(samples, 0.975)) if samples else np.nan,
        "n_tracks": len(track_ids),
        "n_strata": strata_count,
        "bootstrap_valid": len(samples),
    }


def window_summaries(windows: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary = (
        windows.assign(class_name=windows["closure_class"].map(CLASS_NAMES))
        .groupby(["window", "condition", "closure_class", "class_name"], observed=True)
        .agg(
            windows=("track_id", "size"),
            tracks=("track_id", "nunique"),
            information_nats=("information_nats", "mean"),
            traversal=("traversal", "mean"),
            path_length_px=("path_length_px", "mean"),
            handover_rate=("handover_rate", "mean"),
            reverse_flow_rate=("reverse_flow_rate", "mean"),
            coherence=("coherence", "mean"),
            rational_distance_q8=("rational_distance_q8", "mean"),
        )
        .reset_index()
    )
    gate_rows = []
    primary = windows[windows["window"] == 15]
    for condition in (*CONDITIONS, "pooled"):
        subset = primary if condition == "pooled" else primary[primary["condition"] == condition]
        information, info_strata = stratified_point_difference(subset, 1, 2, "information_nats")
        traversal, traversal_strata = stratified_point_difference(subset, 1, 0, "traversal")
        gate_rows.extend(
            [
                {"condition": condition, "comparison": "structured_minus_random_information", "estimate": information, "matched_strata": info_strata},
                {"condition": condition, "comparison": "structured_minus_closure_traversal", "estimate": traversal, "matched_strata": traversal_strata},
            ]
        )
    pooled_info = stratified_cluster_bootstrap(primary, 1, 2, "information_nats")
    pooled_traversal = stratified_cluster_bootstrap(primary, 1, 0, "traversal")
    for row in gate_rows:
        if row["condition"] == "pooled":
            extra = pooled_info if row["comparison"].endswith("information") else pooled_traversal
            row.update({key: value for key, value in extra.items() if key not in ("estimate", "n_strata")})
    return summary, pd.DataFrame(gate_rows)


def event_and_sector_summaries(events: list[dict]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    sector_rows, transition_rows, sample_parts = [], [], []
    for condition in CONDITIONS:
        condition_events = [event for event in events if event["condition"] == condition]
        all_sectors = np.concatenate([event["sector"] for event in condition_events if len(event["sector"])])
        boundary = int(np.sum(all_sectors < 0))
        counts = np.bincount(all_sectors[all_sectors >= 0], minlength=4)
        for code, count in enumerate(counts):
            sector_rows.append({"condition": condition, "sector": SECTOR_NAMES[code], "events": int(count), "share_nonboundary": float(count / counts.sum())})
        sector_rows.append({"condition": condition, "sector": "boundary", "events": boundary, "share_nonboundary": np.nan})
        matrix = np.zeros((4, 4), dtype=np.int64)
        for event in condition_events:
            valid = (np.diff(event["frame"]) == 1) & (event["sector"][:-1] >= 0) & (event["sector"][1:] >= 0)
            for current, target in zip(event["sector"][:-1][valid], event["sector"][1:][valid]):
                matrix[current, target] += 1
        for current in range(4):
            for target in range(4):
                transition_rows.append({"condition": condition, "current": SECTOR_NAMES[current], "next": SECTOR_NAMES[target], "count": int(matrix[current, target])})

        candidates = sorted(condition_events, key=lambda event: hashlib.sha256(event["track_id"].encode()).hexdigest())[:40]
        for event in candidates:
            if len(event["frame"]) == 0:
                continue
            take = np.linspace(0, len(event["frame"]) - 1, min(100, len(event["frame"]))).astype(int)
            sample_parts.append(
                pd.DataFrame(
                    {
                        "condition": condition,
                        "track_id": event["track_id"],
                        "particle_id": event["particle_id"],
                        "frame": event["frame"][take],
                        "time_s": event["time"][take],
                        "x_px": event["x_pos"][take],
                        "z_px": event["z_pos"][take],
                        "ara_x": event["ara_x"][take],
                        "ara_y": event["ara_y"][take],
                        "dominance": np.abs(event["ara_x"][take] - 1) - np.abs(event["ara_y"][take] - 1),
                        "sector": np.where(event["sector"][take] >= 0, SECTOR_NAMES[np.maximum(event["sector"][take], 0)], "boundary"),
                    }
                )
            )
    return pd.DataFrame(sector_rows), pd.DataFrame(transition_rows), pd.concat(sample_parts, ignore_index=True)


def landmark_summary(events: list[dict]) -> pd.DataFrame:
    phi = (1 + math.sqrt(5)) / 2
    rows = []
    for condition in CONDITIONS:
        selected = [event for event in events if event["condition"] == condition]
        s = np.concatenate([event["s"][np.isfinite(event["s"])] for event in selected])
        delta = np.concatenate([event["delta"][np.isfinite(event["delta"])] for event in selected])
        below, above = s[s < 1], s[s > 1]
        s_minus = float(np.median(below)) if len(below) else np.nan
        s_plus = float(np.median(above)) if len(above) else np.nan
        turn = float(np.median(np.abs(delta) / (2 * np.pi)))
        rational_distances = np.array([wrapped_unit_distance(turn, RATIONALS_8)])
        rows.append(
            {
                "condition": condition,
                "events": len(s),
                "median_contraction_s": s_minus,
                "median_expansion_s": s_plus,
                "reciprocal_product": s_minus * s_plus,
                "identity_alpha": math.sqrt(s_plus / s_minus) if s_minus > 0 else np.nan,
                "distance_contraction_to_1_over_e": abs(s_minus - 1 / math.e),
                "distance_contraction_to_1_over_phi": abs(s_minus - 1 / phi),
                "distance_expansion_to_e": abs(s_plus - math.e),
                "distance_expansion_to_phi": abs(s_plus - phi),
                "median_abs_turns": turn,
                "distance_turn_to_phi_minus_2": abs(turn - 1 / phi**2),
                "distance_turn_to_nearest_q_le_8": float(rational_distances[0]),
            }
        )
    return pd.DataFrame(rows)


def make_figure(
    event_sample: pd.DataFrame,
    transition_events: pd.DataFrame,
    model_scores: pd.DataFrame,
    model_bootstrap: pd.DataFrame,
    gate_d: pd.DataFrame,
    sector_transitions: pd.DataFrame,
    path: Path,
):
    plt.style.use("seaborn-v0_8-whitegrid")
    fig = plt.figure(figsize=(17, 15), constrained_layout=True)
    grid = fig.add_gridspec(4, 3)
    for column, condition in enumerate(CONDITIONS):
        ax = fig.add_subplot(grid[0, column])
        subset = event_sample[event_sample["condition"] == condition]
        for _, group in subset.groupby("track_id", sort=False):
            ax.plot(group["x_px"], group["z_px"], alpha=0.35, lw=0.7)
        ax.axvline(0, color="#333333", lw=0.5, alpha=0.4)
        ax.set_title(f"Native particle movement — {condition}")
        ax.set_xlabel(f"downstream x [{POSITION_UNIT}]")
        ax.set_ylabel(f"physical up z [{POSITION_UNIT}]")

    ax = fig.add_subplot(grid[1, 0])
    sample = transition_events.iloc[:: max(1, len(transition_events) // 180000)]
    h = ax.hexbin(sample["ara_x"], sample["ara_y"], gridsize=80, extent=(0, 2, 0, 2), bins="log", cmap="Blues", mincnt=1)
    ax.axvline(1, color="#222222", lw=1.2)
    ax.axhline(1, color="#222222", lw=1.2)
    ax.set(xlim=(0, 2), ylim=(0, 2), xlabel="radial ARA X: contraction → expansion", ylabel="turn ARA Y: reverse → forward", title="Intact Irrationality Di-ARA parent")
    for text, xy in [("Ba", (0.15, 1.85)), ("Ab", (1.75, 1.85)), ("bA", (0.15, 0.12)), ("aB", (1.75, 0.12))]:
        ax.text(*xy, text, fontsize=12, weight="bold")
    fig.colorbar(h, ax=ax, label="log event density")

    ax = fig.add_subplot(grid[1, 1])
    pooled = sector_transitions.groupby(["current", "next"], observed=True)["count"].sum().unstack(fill_value=0).reindex(index=SECTOR_NAMES, columns=SECTOR_NAMES)
    row_sum = pooled.to_numpy().sum(axis=1, keepdims=True)
    matrix = np.divide(pooled.to_numpy(), row_sum, out=np.zeros_like(pooled.to_numpy(), dtype=float), where=row_sum > 0)
    image = ax.imshow(matrix, vmin=0, vmax=max(0.01, matrix.max()), cmap="magma")
    ax.set_xticks(range(4), SECTOR_NAMES)
    ax.set_yticks(range(4), SECTOR_NAMES)
    ax.set_xlabel("next sector")
    ax.set_ylabel("current sector")
    ax.set_title("Ordered parent movement")
    for i in range(4):
        for j in range(4):
            ax.text(j, i, f"{matrix[i,j]:.2f}", ha="center", va="center", color="white" if matrix[i,j] > matrix.max()/2 else "black")
    fig.colorbar(image, ax=ax, label="transition probability")

    ax = fig.add_subplot(grid[1, 2])
    dominance_sample = sample.iloc[:: max(1, len(sample) // 50000)]
    scatter = ax.scatter(dominance_sample["x_px"], dominance_sample["z_px"], c=dominance_sample["dominance"], s=2, alpha=0.35, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set(xlabel=f"downstream x [{POSITION_UNIT}]", ylabel=f"physical up z [{POSITION_UNIT}]", title="Which child leads across the weir")
    fig.colorbar(scatter, ax=ax, label="D: radial-led (+) / turn-led (−)")

    ax = fig.add_subplot(grid[2, :2])
    order = ["intact_vs_radial_child", "intact_vs_turn_child", "intact_vs_additive_children", "intact_vs_broken_parent", "intact_vs_persistence"]
    plot = model_bootstrap.set_index("comparison").reindex(order)
    values = plot["estimate"].to_numpy()
    errors = np.vstack([values - plot["ci_low"].to_numpy(), plot["ci_high"].to_numpy() - values])
    ax.bar(range(len(order)), values, yerr=errors, color=["#5B8FF9", "#61DDAA", "#9270CA", "#E8684A", "#F6BD16"], capsize=4)
    ax.axhline(0, color="#222222", lw=1)
    ax.set_xticks(range(len(order)), [value.replace("intact_vs_", "") for value in order], rotation=20, ha="right")
    ax.set_ylabel("log-loss improvement (positive = intact better)")
    ax.set_title("Unseen-condition prediction: intact parent versus controls")

    ax = fig.add_subplot(grid[2, 2])
    fold_models = ["radial_child", "turn_child", "additive_children", "intact_parent", "broken_parent"]
    pivot = model_scores.pivot(index="test_condition", columns="model", values="log_loss").reindex(index=CONDITIONS, columns=fold_models)
    for model in fold_models:
        ax.plot(CONDITIONS, pivot[model], marker="o", label=model)
    ax.set_ylabel("held-out log loss (lower is better)")
    ax.set_title("Transfer by tailwater condition")
    ax.legend(fontsize=8)

    pooled_gate = gate_d[gate_d["condition"] == "pooled"].set_index("comparison")
    ax = fig.add_subplot(grid[3, 0])
    info = pooled_gate.loc["structured_minus_random_information"]
    ax.bar([0], [info["estimate"]], yerr=[[info["estimate"] - info.get("ci_low", np.nan)], [info.get("ci_high", np.nan) - info["estimate"]]], color="#9270CA", capsize=5)
    ax.axhline(0, color="#222222", lw=1)
    ax.set_xticks([0], ["structured − random"])
    ax.set_ylabel("predictive information [nats]")
    ax.set_title("Information-retention half")

    ax = fig.add_subplot(grid[3, 1])
    traversal = pooled_gate.loc["structured_minus_closure_traversal"]
    ax.bar([0], [traversal["estimate"]], yerr=[[traversal["estimate"] - traversal.get("ci_low", np.nan)], [traversal.get("ci_high", np.nan) - traversal["estimate"]]], color="#61DDAA", capsize=5)
    ax.axhline(0, color="#222222", lw=1)
    ax.set_xticks([0], ["structured − closure"])
    ax.set_ylabel("active-traversal difference")
    ax.set_title("Ongoing-movement half")

    ax = fig.add_subplot(grid[3, 2])
    primary = gate_d[gate_d["condition"].isin(CONDITIONS)].pivot(index="condition", columns="comparison", values="estimate").reindex(CONDITIONS)
    xloc = np.arange(3)
    ax.bar(xloc - 0.18, primary["structured_minus_random_information"], width=0.36, label="information", color="#9270CA")
    ax.bar(xloc + 0.18, primary["structured_minus_closure_traversal"], width=0.36, label="traversal", color="#61DDAA")
    ax.axhline(0, color="#222222", lw=1)
    ax.set_xticks(xloc, CONDITIONS)
    ax.set_title("Irrationality sandwich by condition")
    ax.legend(fontsize=8)

    fig.suptitle(f"T344 — controlled weir Irrationality Di-ARA ({REPRESENTATION})", fontsize=20, weight="bold")
    fig.savefig(path, dpi=220)
    plt.close(fig)


def make_explorer(event_sample: pd.DataFrame, model_scores: pd.DataFrame, window_summary: pd.DataFrame, path: Path):
    sample = event_sample.iloc[:: max(1, len(event_sample) // 16000)].copy()
    payload = {
        "events": sample.to_dict(orient="records"),
        "models": model_scores.to_dict(orient="records"),
        "windows": window_summary[window_summary["window"] == 15].replace({np.nan: None}).to_dict(orient="records"),
    }
    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>T344 BAW weir Irrationality Di-ARA explorer</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>body{{margin:0;background:#0b1020;color:#e8edf7;font-family:Inter,Segoe UI,sans-serif}}header{{padding:22px 28px;background:#111a31}}h1{{margin:0;font-size:24px}}p{{color:#aebbd3;max-width:1000px}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:14px;padding:14px}}.card{{background:#111a31;border:1px solid #253354;border-radius:12px;padding:8px}}.plot{{height:520px}}@media(max-width:1000px){{.grid{{grid-template-columns:1fr}}}}</style></head>
<body><header><h1>T344 — controlled weir Irrationality Di-ARA</h1><p>Native particle movement beside its radial×turn ARA parent. Use the legend to isolate low, medium and high tailwater conditions. The 3D view uses time as the third axis; it does not manufacture another ARA coordinate.</p></header><div class="grid"><div class="card"><div id="physical" class="plot"></div></div><div class="card"><div id="ara" class="plot"></div></div><div class="card"><div id="models" class="plot"></div></div><div class="card"><div id="classes" class="plot"></div></div></div>
<script>const D={json.dumps(payload, separators=(',', ':'))}; const colors={{low:'#5B8FF9',medium:'#61DDAA',high:'#E8684A'}};
const physical=[]; for(const c of ['low','medium','high']){{const e=D.events.filter(r=>r.condition===c); physical.push({{type:'scatter3d',mode:'markers',name:c,x:e.map(r=>r.x_px),y:e.map(r=>r.z_px),z:e.map(r=>r.time_s),marker:{{size:2,color:colors[c],opacity:.55}}}})}} Plotly.newPlot('physical',physical,{{title:'Particle paths: x × z × time',paper_bgcolor:'#111a31',plot_bgcolor:'#111a31',font:{{color:'#e8edf7'}},scene:{{xaxis:{{title:'downstream x [{POSITION_UNIT}]'}},yaxis:{{title:'physical up z [{POSITION_UNIT}]'}},zaxis:{{title:'time from crest [s]'}}}}}},{{responsive:true}});
const ara=[]; for(const c of ['low','medium','high']){{const e=D.events.filter(r=>r.condition===c && r.sector!=='boundary'); ara.push({{type:'scattergl',mode:'markers',name:c,x:e.map(r=>r.ara_x),y:e.map(r=>r.ara_y),text:e.map(r=>r.sector),marker:{{size:4,color:colors[c],opacity:.35}}}})}} Plotly.newPlot('ara',ara,{{title:'Intact Di-ARA parent',xaxis:{{title:'radial ARA X',range:[0,2],zeroline:false}},yaxis:{{title:'turn ARA Y',range:[0,2],zeroline:false}},shapes:[{{type:'line',x0:1,x1:1,y0:0,y1:2,line:{{color:'#fff'}}}},{{type:'line',x0:0,x1:2,y0:1,y1:1,line:{{color:'#fff'}}}}],paper_bgcolor:'#111a31',plot_bgcolor:'#111a31',font:{{color:'#e8edf7'}}}},{{responsive:true}});
const modelOrder=['radial_child','turn_child','additive_children','intact_parent','broken_parent']; const mt=[]; for(const c of ['low','medium','high']){{const rows=modelOrder.map(m=>D.models.find(r=>r.test_condition===c&&r.model===m)); mt.push({{type:'bar',name:c,x:modelOrder,y:rows.map(r=>r.log_loss),marker:{{color:colors[c]}}}})}} Plotly.newPlot('models',mt,{{title:'Unseen-condition next-state log loss',barmode:'group',yaxis:{{title:'lower is better'}},paper_bgcolor:'#111a31',plot_bgcolor:'#111a31',font:{{color:'#e8edf7'}}}},{{responsive:true}});
const classes=['low-order closure','structured non-closing','random-like']; const ct=[]; for(const c of ['low','medium','high']){{const rows=classes.map(n=>D.windows.find(r=>r.condition===c&&r.class_name===n)); ct.push({{type:'bar',name:c,x:classes,y:rows.map(r=>r? r.windows:0),marker:{{color:colors[c]}}}})}} Plotly.newPlot('classes',ct,{{title:'Frozen W=15 closure classes',barmode:'group',yaxis:{{title:'windows'}},paper_bgcolor:'#111a31',plot_bgcolor:'#111a31',font:{{color:'#e8edf7'}}}},{{responsive:true}});
</script></body></html>"""
    path.write_text(html, encoding="utf-8")


def write_report(results: dict, path: Path):
    gates = results["gates"]
    b = gates["B_intact_parent"]
    c = gates["C_coupling_asymmetry"]
    d = gates["D_structured_nonclosure"]
    verdict = "SUPPORTED" if b["pass"] and c["pass"] and d["pass"] else "PARTIALLY SUPPORTED" if b["pass"] or c["pass"] or d["pass"] else "NOT SUPPORTED"
    text = f"""# T344 — controlled weir Irrationality Di-ARA report

**Date:** 6 August 2026  
**Overall frozen result:** **{verdict}**  
**Source:** BAW DOI [10.48437/99f329-73aee6](https://doi.org/10.48437/99f329-73aee6)

## Answer first

This archive supplied the test we were missing: thousands of objects physically moving
through a controlled weir at 0.01-second resolution. The result must be separated into
three claims:

1. **Complete local geometry:** Gate A = **{'PASS' if gates['A_four_sectors']['pass'] else 'FAIL'}**.
2. **The intact two-child parent matters out of sample:** Gate B = **{'PASS' if b['pass'] else 'FAIL'}**.
3. **The typed irrationality mechanism occupies the proposed middle regime:** Gate D =
   **{'PASS' if d['pass'] else 'FAIL'}**.

The coupling-asymmetry interaction gate is **{'PASS' if c['pass'] else 'FAIL'}**. These
statuses are not averaged into a stronger claim.

## Plain-language reading

The particle movement was split into two native children at every time step: whether the
next movement grew or shrank, and whether it turned forward or back. Their intact pairing
was then asked to predict the next movement in a completely unseen water-level setting.
The comparison included each child alone, both children without an interaction, and a
false parent made by pairing children from different particles.

The irrationality test then asked for the specific ARA “middle”: coherent motion that
does not settle into a low-order closure should retain more future information than
random-like motion while continuing to traverse more effectively than closing motion.

## Frozen gate details

```json
{json.dumps(gates, indent=2)}
```

## Boundaries

- A finite trajectory cannot establish mathematical irrationality. The tested label is
  **structured non-closing**.
- The exact constants `Phi`, `1/Phi`, `e`, and `1/e` were secondary probes and could not
  rescue a failed primary gate.
- The numerical OpenFOAM trajectories remain a separate replication tier; they are not
  counted as extra laboratory observations.
- Approximately one quarter of laboratory tracks reportedly required some manual
  reconstruction. If the archive does not expose a per-track flag, that limitation
  cannot be removed retrospectively.
"""
    path.write_text(text, encoding="utf-8")


def main():
    audits, raw_tracks = [], []
    for condition in CONDITIONS:
        print(f"[T344] loading {condition} source workbook", flush=True)
        tracks, audit = load_condition(condition)
        raw_tracks.extend(tracks)
        audits.append(audit)

    print(f"[T344] deriving native ARA events for {len(raw_tracks):,} tracks", flush=True)
    event_tracks = [derive_track_events(track) for track in raw_tracks]
    for audit in audits:
        condition_events = [event for event in event_tracks if event["condition"] == audit["condition"]]
        audit["ara_events"] = int(sum(len(event["frame"]) for event in condition_events))
        audit["near_zero_quotients_excluded"] = int(sum(event["excluded_near_zero"] for event in condition_events))
        audit["eligible_tracks_20_events"] = int(sum(len(event["frame"]) >= 20 for event in condition_events))
    audit_frame = pd.DataFrame(audits)

    print("[T344] building exact consecutive next-sector rows", flush=True)
    transitions = build_transition_frame(event_tracks)
    print(f"[T344] fitting frozen held-out models on {len(transitions):,} rows", flush=True)
    model_scores, track_scores, predictions, optimiser_rows = fit_and_score_folds(transitions)
    print("[T344] bootstrapping model comparisons by whole trajectory", flush=True)
    model_bootstrap = model_bootstraps(track_scores)
    sector_summary, sector_transitions, event_sample = event_and_sector_summaries(event_tracks)
    landmarks = landmark_summary(event_tracks)

    window_frames = []
    for window in (8, 15, 30):
        print(f"[T344] constructing and scoring W={window} closure windows", flush=True)
        frame = build_windows(event_tracks, window)
        frame, optimiser = score_window_information(frame)
        optimiser_rows.extend(optimiser)
        window_frames.append(frame)
    windows = pd.concat(window_frames, ignore_index=True)
    print(f"[T344] bootstrapping the Irrationality Di-ARA sandwich across {len(windows):,} windows", flush=True)
    window_summary, gate_d_summary = window_summaries(windows)

    four_sector_pass = bool(all((sector_summary[(sector_summary["condition"] == condition) & (sector_summary["sector"] != "boundary")]["events"] > 0).all() for condition in CONDITIONS))
    bootstrap_index = model_bootstrap.set_index("comparison")
    gate_b_components = {}
    gate_b_pass = True
    for comparison in ("intact_vs_radial_child", "intact_vs_turn_child", "intact_vs_broken_parent"):
        row = bootstrap_index.loc[comparison]
        passed = bool(row["fold_wins"] >= 2 and row["ci_low"] > 0)
        gate_b_components[comparison] = {"pass": passed, "estimate": float(row["estimate"]), "ci": [float(row["ci_low"]), float(row["ci_high"])], "fold_wins": int(row["fold_wins"])}
        gate_b_pass &= passed
    row_c = bootstrap_index.loc["intact_vs_additive_children"]
    gate_c_pass = bool(row_c["fold_wins"] >= 2 and row_c["ci_low"] > 0)

    gate_d_index = gate_d_summary.set_index(["condition", "comparison"])
    condition_info = [float(gate_d_index.loc[(condition, "structured_minus_random_information"), "estimate"]) for condition in CONDITIONS]
    condition_traversal = [float(gate_d_index.loc[(condition, "structured_minus_closure_traversal"), "estimate"]) for condition in CONDITIONS]
    pooled_info = gate_d_index.loc[("pooled", "structured_minus_random_information")]
    pooled_traversal = gate_d_index.loc[("pooled", "structured_minus_closure_traversal")]
    gate_d_pass = bool(
        sum(value > 0 for value in condition_info if np.isfinite(value)) >= 2
        and sum(value > 0 for value in condition_traversal if np.isfinite(value)) >= 2
        and float(pooled_info.get("ci_low", np.nan)) > 0
        and float(pooled_traversal.get("ci_low", np.nan)) > 0
    )

    gates = {
        "A_four_sectors": {"pass": four_sector_pass},
        "B_intact_parent": {"pass": gate_b_pass, "components": gate_b_components},
        "C_coupling_asymmetry": {"pass": gate_c_pass, "estimate": float(row_c["estimate"]), "ci": [float(row_c["ci_low"]), float(row_c["ci_high"])], "fold_wins": int(row_c["fold_wins"])},
        "D_structured_nonclosure": {
            "pass": gate_d_pass,
            "information_condition_effects": dict(zip(CONDITIONS, condition_info)),
            "traversal_condition_effects": dict(zip(CONDITIONS, condition_traversal)),
            "pooled_information": {"estimate": float(pooled_info["estimate"]), "ci": [float(pooled_info.get("ci_low", np.nan)), float(pooled_info.get("ci_high", np.nan))]},
            "pooled_traversal": {"estimate": float(pooled_traversal["estimate"]), "ci": [float(pooled_traversal.get("ci_low", np.nan)), float(pooled_traversal.get("ci_high", np.nan))]},
        },
        "E_numerical_replication": {
            "status": "not_run_in_primary_stage" if REPRESENTATION == "lab" else "replication_run_complete"
        },
    }

    results = {
        "test": "T344_BAW_WEIR_IRRATIONALITY_DI_ARA",
        "representation": REPRESENTATION,
        "source_doi": "10.48437/99f329-73aee6",
        "source_hashes_match": bool(audit_frame["sha256_matches_official"].all()),
        "trajectory_tracks": int(audit_frame["joined_tracks"].sum()),
        "ara_events": int(audit_frame["ara_events"].sum()),
        "next_state_events": int(len(transitions)),
        "window_counts": {str(window): int((windows["window"] == window).sum()) for window in (8, 15, 30)},
        "gates": gates,
        "optimisers": optimiser_rows,
    }

    prefix = OUTPUT_PREFIX
    audit_frame.to_csv(HERE / f"{prefix}_DATA_QUALITY.csv", index=False)
    sector_summary.to_csv(HERE / f"{prefix}_SECTORS.csv", index=False)
    sector_transitions.to_csv(HERE / f"{prefix}_TRANSITIONS.csv", index=False)
    model_scores.to_csv(HERE / f"{prefix}_MODEL_SCORES.csv", index=False)
    track_scores.to_csv(HERE / f"{prefix}_TRACK_SCORES.csv", index=False)
    model_bootstrap.to_csv(HERE / f"{prefix}_BOOTSTRAPS.csv", index=False)
    pd.DataFrame(optimiser_rows).to_csv(HERE / f"{prefix}_OPTIMISERS.csv", index=False)
    window_summary.to_csv(HERE / f"{prefix}_WINDOW_SUMMARY.csv", index=False)
    gate_d_summary.to_csv(HERE / f"{prefix}_IRRATIONALITY_GATE.csv", index=False)
    landmarks.to_csv(HERE / f"{prefix}_LANDMARKS_SECONDARY.csv", index=False)
    event_sample.to_csv(HERE / f"{prefix}_EVENT_SAMPLE.csv", index=False)
    predictions.iloc[:: max(1, len(predictions) // 100000)].to_csv(HERE / f"{prefix}_PREDICTION_SAMPLE.csv", index=False)
    (HERE / f"{prefix}_RESULTS.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    make_figure(
        event_sample,
        transitions,
        model_scores,
        model_bootstrap,
        gate_d_summary,
        sector_transitions,
        HERE / f"{prefix}_FIGURE.png",
    )
    make_explorer(event_sample, model_scores, window_summary, HERE / f"{prefix}_EXPLORER.html")
    write_report(results, HERE / f"{prefix}_REPORT_2026-08-06.md")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
