#!/usr/bin/env python3
"""Run frozen T259 on the public Arnold-Werner superconducting-qubit I/Q data."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
from scipy.io import loadmat


HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "public_data"
ARCHIVE = DATA_DIR / "AllopticalSCQreadout_data.zip"
EXTRACTED = DATA_DIR / "extracted"
SOURCE_ROOT = EXTRACTED / "AllopticalSCQreadout_data"
SOURCE_URL = (
    "https://zenodo.org/records/14033026/files/"
    "AllopticalSCQreadout_data.zip?download=1"
)
SOURCE_SHA256 = "73f3e2ca7b3658452b4c171532c751e96d7392dcb8741b87a18e28c7073d67fd"
PROTOCOL = HERE / "Q2_PUBLIC_HARDWARE_IQ_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q2_PUBLIC_HARDWARE_IQ_PROTOCOL_v1_FROZEN.sha256"
FIDELITY = HERE / "Q2_PUBLIC_HARDWARE_IQ_FIDELITY_v1.md"

FOLDS_CSV = HERE / "Q2_PUBLIC_HARDWARE_IQ_FOLDS.csv"
BLOCKS_CSV = HERE / "Q2_PUBLIC_HARDWARE_IQ_BLOCKS.csv"
SUMMARY_CSV = HERE / "Q2_PUBLIC_HARDWARE_IQ_SUMMARY.csv"
RESULTS_JSON = HERE / "Q2_PUBLIC_HARDWARE_IQ_RESULTS.json"

CONDITIONS = (0, 10, 50, 250, 500, 1000)
BLOCK_SIZE = 1000
PAIR_SHIFT = 10007
BOOTSTRAP_SEED = 2026072403
BOOTSTRAP_REPS = 2000
PINV_RCOND = 1e-12

RUNS = {
    "primary_first_readout": {"prep": False, "readout": 1},
    "replication_second_readout": {"prep": False, "readout": 2},
    "replication_prep_first": {"prep": True, "readout": 1},
    "replication_prep_second": {"prep": True, "readout": 2},
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_source(download: bool) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not ARCHIVE.exists():
        if not download:
            raise FileNotFoundError(
                f"{ARCHIVE} is absent. Re-run with --download or place the DOI archive there."
            )
        print(f"Downloading {SOURCE_URL}")
        urllib.request.urlretrieve(SOURCE_URL, ARCHIVE)
    observed = sha256(ARCHIVE)
    if observed != SOURCE_SHA256:
        raise RuntimeError(f"Source SHA-256 mismatch: {observed}")
    required = SOURCE_ROOT / "Fig_4a" / "IQblobs_0Hz.mat"
    if not required.exists():
        EXTRACTED.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(ARCHIVE) as zf:
            wanted = [
                n
                for n in zf.namelist()
                if n.startswith("AllopticalSCQreadout_data/Fig_4a/IQblobs_")
                and n.endswith(".mat")
            ]
            zf.extractall(EXTRACTED, members=wanted)


def verify_freeze() -> tuple[str, str]:
    expected = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0].lower()
    observed = sha256(PROTOCOL)
    if observed != expected:
        raise RuntimeError(
            f"Frozen protocol hash mismatch: expected {expected}, observed {observed}"
        )
    return expected, sha256(FIDELITY)


def source_file(condition: int, prep: bool) -> Path:
    suffix = "_prep" if prep else ""
    return SOURCE_ROOT / "Fig_4a" / f"IQblobs_{condition}Hz{suffix}.mat"


def load_run(prep: bool, readout: int) -> dict[int, dict[int, np.ndarray]]:
    tag = "" if readout == 1 else "2"
    out: dict[int, dict[int, np.ndarray]] = {}
    for condition in CONDITIONS:
        path = source_file(condition, prep)
        raw = loadmat(
            path,
            variable_names=[f"I_g{tag}", f"Q_g{tag}", f"I_e{tag}", f"Q_e{tag}"],
        )
        g = np.column_stack(
            [
                np.asarray(raw[f"I_g{tag}"], dtype=np.float64).reshape(-1),
                np.asarray(raw[f"Q_g{tag}"], dtype=np.float64).reshape(-1),
            ]
        )
        e = np.column_stack(
            [
                np.asarray(raw[f"I_e{tag}"], dtype=np.float64).reshape(-1),
                np.asarray(raw[f"Q_e{tag}"], dtype=np.float64).reshape(-1),
            ]
        )
        if g.shape != (50000, 2) or e.shape != (50000, 2):
            raise RuntimeError(f"Schema mismatch in {path}: {g.shape}, {e.shape}")
        if not np.isfinite(g).all() or not np.isfinite(e).all():
            raise RuntimeError(f"Non-finite primary values in {path}")
        out[condition] = {0: g, 1: e}
    return out


def stack_conditions(
    data: dict[int, dict[int, np.ndarray]], conditions: list[int], label: int
) -> np.ndarray:
    return np.vstack([data[c][label] for c in conditions])


def pooled_covariance(x0: np.ndarray, x1: np.ndarray) -> np.ndarray:
    m0 = x0.mean(axis=0)
    m1 = x1.mean(axis=0)
    c0 = x0 - m0
    c1 = x1 - m1
    return (c0.T @ c0 + c1.T @ c1) / (len(x0) + len(x1) - 2)


def fit_lda(x0: np.ndarray, x1: np.ndarray) -> dict[str, np.ndarray]:
    if x0.ndim == 1:
        x0 = x0[:, None]
        x1 = x1[:, None]
    m0 = x0.mean(axis=0)
    m1 = x1.mean(axis=0)
    cov = np.atleast_2d(pooled_covariance(x0, x1))
    inv = np.linalg.pinv(cov, rcond=PINV_RCOND)
    w = inv @ (m1 - m0)
    return {"m0": m0, "m1": m1, "mid": (m0 + m1) / 2, "w": w, "cov": cov}


def lda_score(model: dict[str, np.ndarray], x: np.ndarray) -> np.ndarray:
    if x.ndim == 1:
        x = x[:, None]
    return (x - model["mid"]) @ model["w"]


def lda_predict(model: dict[str, np.ndarray], x: np.ndarray) -> np.ndarray:
    return (lda_score(model, x) >= 0).astype(np.int8)


def fit_qda(x0: np.ndarray, x1: np.ndarray) -> dict[str, np.ndarray | float]:
    def class_parts(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
        mean = x.mean(axis=0)
        centered = x - mean
        cov = centered.T @ centered / (len(x) - 1)
        eigvals, eigvecs = np.linalg.eigh(cov)
        floor = max(float(eigvals.max()) * 1e-12, 1e-24)
        cov = eigvecs @ np.diag(np.maximum(eigvals, floor)) @ eigvecs.T
        inv = np.linalg.inv(cov)
        logdet = float(np.linalg.slogdet(cov)[1])
        return mean, inv, logdet

    m0, i0, d0 = class_parts(x0)
    m1, i1, d1 = class_parts(x1)
    return {"m0": m0, "i0": i0, "d0": d0, "m1": m1, "i1": i1, "d1": d1}


def qda_predict(model: dict[str, np.ndarray | float], x: np.ndarray) -> np.ndarray:
    d0 = x - model["m0"]
    d1 = x - model["m1"]
    s0 = np.einsum("ni,ij,nj->n", d0, model["i0"], d0) + float(model["d0"])
    s1 = np.einsum("ni,ij,nj->n", d1, model["i1"], d1) + float(model["d1"])
    return (s1 <= s0).astype(np.int8)


def fit_ara_calibration(x0: np.ndarray, x1: np.ndarray) -> dict[str, np.ndarray]:
    m0 = x0.mean(axis=0)
    m1 = x1.mean(axis=0)
    mid = (m0 + m1) / 2
    std = np.sqrt(np.diag(pooled_covariance(x0, x1)))
    if np.any(std <= 1e-15):
        raise RuntimeError("INCONCLUSIVE: DEGENERATE CUT")
    orientation = np.where((m1 - m0) >= 0, 1.0, -1.0)
    return {"mid": mid, "std": std, "orientation": orientation}


def ara_transform(cal: dict[str, np.ndarray], x: np.ndarray) -> np.ndarray:
    return 1.0 + cal["orientation"] * (x - cal["mid"]) / cal["std"]


def balanced_accuracy(y: np.ndarray, pred: np.ndarray) -> float:
    tnr = float((pred[y == 0] == 0).mean())
    tpr = float((pred[y == 1] == 1).mean())
    return (tnr + tpr) / 2


def confusion(y: np.ndarray, pred: np.ndarray) -> dict[str, int]:
    return {
        "tn": int(np.sum((y == 0) & (pred == 0))),
        "fp": int(np.sum((y == 0) & (pred == 1))),
        "fn": int(np.sum((y == 1) & (pred == 0))),
        "tp": int(np.sum((y == 1) & (pred == 1))),
    }


def mcc_from_conf(c: dict[str, int]) -> float:
    num = c["tp"] * c["tn"] - c["fp"] * c["fn"]
    den = math.sqrt(
        (c["tp"] + c["fp"])
        * (c["tp"] + c["fn"])
        * (c["tn"] + c["fp"])
        * (c["tn"] + c["fn"])
    )
    return float(num / den) if den else 0.0


def kappa_from_conf(c: dict[str, int]) -> float:
    n = sum(c.values())
    po = (c["tp"] + c["tn"]) / n
    actual_pos = (c["tp"] + c["fn"]) / n
    pred_pos = (c["tp"] + c["fp"]) / n
    pe = actual_pos * pred_pos + (1 - actual_pos) * (1 - pred_pos)
    return float((po - pe) / (1 - pe)) if pe < 1 else 0.0


def choose_axis_training_only(
    data: dict[int, dict[int, np.ndarray]], train_conditions: list[int]
) -> tuple[int, float, float]:
    scores = []
    for axis in (0, 1):
        fold_scores = []
        for validation in train_conditions:
            inner = [c for c in train_conditions if c != validation]
            x0 = stack_conditions(data, inner, 0)[:, axis]
            x1 = stack_conditions(data, inner, 1)[:, axis]
            model = fit_lda(x0, x1)
            y = np.concatenate(
                [
                    np.zeros(len(data[validation][0]), dtype=np.int8),
                    np.ones(len(data[validation][1]), dtype=np.int8),
                ]
            )
            x = np.concatenate(
                [data[validation][0][:, axis], data[validation][1][:, axis]]
            )
            fold_scores.append(balanced_accuracy(y, lda_predict(model, x)))
        scores.append(float(np.mean(fold_scores)))
    selected = 0 if scores[0] >= scores[1] else 1
    return selected, scores[0], scores[1]


def shuffled_training_classes(
    data: dict[int, dict[int, np.ndarray]],
    train_conditions: list[int],
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    new0 = []
    new1 = []
    for condition in train_conditions:
        x = np.vstack([data[condition][0], data[condition][1]])
        labels = np.concatenate(
            [
                np.zeros(len(data[condition][0]), dtype=np.int8),
                np.ones(len(data[condition][1]), dtype=np.int8),
            ]
        )
        labels = labels[rng.permutation(len(labels))]
        new0.append(x[labels == 0])
        new1.append(x[labels == 1])
    return np.vstack(new0), np.vstack(new1)


def evaluate_run(
    run_name: str,
    data: dict[int, dict[int, np.ndarray]],
    capture_blocks: bool,
) -> tuple[list[dict], list[dict]]:
    fold_rows: list[dict] = []
    block_rows: list[dict] = []
    for fold_index, target_condition in enumerate(CONDITIONS):
        train_conditions = [c for c in CONDITIONS if c != target_condition]
        train0 = stack_conditions(data, train_conditions, 0)
        train1 = stack_conditions(data, train_conditions, 1)
        target0 = data[target_condition][0]
        target1 = data[target_condition][1]
        target_x = np.vstack([target0, target1])
        y = np.concatenate(
            [
                np.zeros(len(target0), dtype=np.int8),
                np.ones(len(target1), dtype=np.int8),
            ]
        )

        selected_axis, train_i_ba, train_q_ba = choose_axis_training_only(
            data, train_conditions
        )
        i_model = fit_lda(train0[:, 0], train1[:, 0])
        q_model = fit_lda(train0[:, 1], train1[:, 1])
        selected_model = i_model if selected_axis == 0 else q_model

        pred_i = lda_predict(i_model, target_x[:, 0])
        pred_q = lda_predict(q_model, target_x[:, 1])
        pred_selected = pred_i if selected_axis == 0 else pred_q

        cal = fit_ara_calibration(train0, train1)
        ara_train0 = ara_transform(cal, train0)
        ara_train1 = ara_transform(cal, train1)
        ara_target = ara_transform(cal, target_x)
        ara_model = fit_lda(ara_train0, ara_train1)
        pred_ara = lda_predict(ara_model, ara_target)
        ara_scores = lda_score(ara_model, ara_target)

        raw_model = fit_lda(train0, train1)
        pred_raw = lda_predict(raw_model, target_x)
        raw_scores = lda_score(raw_model, target_x)

        qda_model = fit_qda(train0, train1)
        pred_qda = qda_predict(qda_model, target_x)

        reversed_train0 = 2.0 - ara_train0
        reversed_train1 = 2.0 - ara_train1
        reversed_target = 2.0 - ara_target
        reversed_model = fit_lda(reversed_train0, reversed_train1)
        pred_reversed = lda_predict(reversed_model, reversed_target)

        shuffled0, shuffled1 = shuffled_training_classes(
            data, train_conditions, 2026072402 + fold_index
        )
        shuffled_cal = fit_ara_calibration(shuffled0, shuffled1)
        shuffled_model = fit_lda(
            ara_transform(shuffled_cal, shuffled0),
            ara_transform(shuffled_cal, shuffled1),
        )
        pred_label_shuffle = lda_predict(
            shuffled_model, ara_transform(shuffled_cal, target_x)
        )

        pair0 = target0.copy()
        pair1 = target1.copy()
        pair0[:, 1] = np.roll(pair0[:, 1], PAIR_SHIFT)
        pair1[:, 1] = np.roll(pair1[:, 1], PAIR_SHIFT)
        pair_target = np.vstack([pair0, pair1])
        pred_pair_destroyed = lda_predict(ara_model, ara_transform(cal, pair_target))

        complement_residual = float(
            np.max(np.abs(ara_target + (2.0 - ara_target) - 2.0))
        )
        out_of_range = float(np.mean((ara_target < 0) | (ara_target > 2)))
        same_disagreement = int(np.sum(pred_ara != pred_raw))
        reversed_disagreement = int(np.sum(pred_ara != pred_reversed))

        predictions = {
            "i_only": pred_i,
            "q_only": pred_q,
            "selected_onecut": pred_selected,
            "ara_twocut": pred_ara,
            "raw_iq_lda": pred_raw,
            "raw_iq_qda": pred_qda,
            "label_shuffle": pred_label_shuffle,
            "pair_destroyed": pred_pair_destroyed,
        }
        for arm, pred in predictions.items():
            c = confusion(y, pred)
            fold_rows.append(
                {
                    "run": run_name,
                    "condition_hz": target_condition,
                    "fold_index": fold_index,
                    "arm": arm,
                    "selected_axis": "I" if selected_axis == 0 else "Q",
                    "training_cv_i_ba": train_i_ba,
                    "training_cv_q_ba": train_q_ba,
                    "balanced_accuracy": balanced_accuracy(y, pred),
                    "mcc": mcc_from_conf(c),
                    "kappa": kappa_from_conf(c),
                    **c,
                    "ara_raw_disagreements": same_disagreement
                    if arm == "ara_twocut"
                    else "",
                    "pole_reversal_disagreements": reversed_disagreement
                    if arm == "ara_twocut"
                    else "",
                    "complement_max_residual": complement_residual
                    if arm == "ara_twocut"
                    else "",
                    "ara_out_of_range_fraction": out_of_range
                    if arm == "ara_twocut"
                    else "",
                    "score_margin_median": float(np.median(np.abs(ara_scores)))
                    if arm == "ara_twocut"
                    else (
                        float(np.median(np.abs(raw_scores)))
                        if arm == "raw_iq_lda"
                        else ""
                    ),
                }
            )

        if capture_blocks:
            for label, offset in ((0, 0), (1, len(target0))):
                for block_index in range(50):
                    start = offset + block_index * BLOCK_SIZE
                    stop = start + BLOCK_SIZE
                    block_y = y[start:stop]
                    block_rows.append(
                        {
                            "condition_hz": target_condition,
                            "class": "g" if label == 0 else "e",
                            "block_index": block_index,
                            "n": BLOCK_SIZE,
                            "ara_correct": int(
                                np.sum(pred_ara[start:stop] == block_y)
                            ),
                            "selected_onecut_correct": int(
                                np.sum(pred_selected[start:stop] == block_y)
                            ),
                            "raw_iq_correct": int(
                                np.sum(pred_raw[start:stop] == block_y)
                            ),
                        }
                    )
    return fold_rows, block_rows


def summarize_folds(fold_rows: list[dict]) -> list[dict]:
    keys = sorted({(r["run"], r["arm"]) for r in fold_rows})
    out = []
    for run_name, arm in keys:
        rows = [r for r in fold_rows if r["run"] == run_name and r["arm"] == arm]
        total = {
            name: sum(int(r[name]) for r in rows) for name in ("tn", "fp", "fn", "tp")
        }
        out.append(
            {
                "run": run_name,
                "arm": arm,
                "condition_weighted_ba": float(
                    np.mean([r["balanced_accuracy"] for r in rows])
                ),
                "worst_condition_ba": float(
                    np.min([r["balanced_accuracy"] for r in rows])
                ),
                "mcc": mcc_from_conf(total),
                "kappa": kappa_from_conf(total),
                **total,
            }
        )
    return out


def paired_bootstrap(block_rows: list[dict]) -> dict[str, float]:
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    by_condition: dict[int, dict[str, list[dict]]] = {}
    for condition in CONDITIONS:
        by_condition[condition] = {
            "g": [
                r
                for r in block_rows
                if r["condition_hz"] == condition and r["class"] == "g"
            ],
            "e": [
                r
                for r in block_rows
                if r["condition_hz"] == condition and r["class"] == "e"
            ],
        }
    deltas = np.empty(BOOTSTRAP_REPS, dtype=float)
    ara_values = np.empty(BOOTSTRAP_REPS, dtype=float)
    one_values = np.empty(BOOTSTRAP_REPS, dtype=float)
    for b in range(BOOTSTRAP_REPS):
        sampled_conditions = rng.choice(CONDITIONS, size=len(CONDITIONS), replace=True)
        cond_ara = []
        cond_one = []
        for condition in sampled_conditions:
            class_ara = []
            class_one = []
            for label in ("g", "e"):
                rows = by_condition[int(condition)][label]
                sampled = rng.integers(0, len(rows), size=len(rows))
                class_ara.append(
                    np.mean([rows[i]["ara_correct"] / BLOCK_SIZE for i in sampled])
                )
                class_one.append(
                    np.mean(
                        [
                            rows[i]["selected_onecut_correct"] / BLOCK_SIZE
                            for i in sampled
                        ]
                    )
                )
            cond_ara.append(float(np.mean(class_ara)))
            cond_one.append(float(np.mean(class_one)))
        ara_values[b] = np.mean(cond_ara)
        one_values[b] = np.mean(cond_one)
        deltas[b] = ara_values[b] - one_values[b]
    return {
        "repetitions": BOOTSTRAP_REPS,
        "seed": BOOTSTRAP_SEED,
        "ara_ba_ci_low": float(np.quantile(ara_values, 0.025)),
        "ara_ba_ci_high": float(np.quantile(ara_values, 0.975)),
        "selected_onecut_ba_ci_low": float(np.quantile(one_values, 0.025)),
        "selected_onecut_ba_ci_high": float(np.quantile(one_values, 0.975)),
        "gain_ci_low": float(np.quantile(deltas, 0.025)),
        "gain_ci_high": float(np.quantile(deltas, 0.975)),
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summary_value(summary: list[dict], run: str, arm: str, field: str) -> float:
    row = next(r for r in summary if r["run"] == run and r["arm"] == arm)
    return float(row[field])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()

    protocol_hash, fidelity_hash = verify_freeze()
    ensure_source(args.download)

    all_folds: list[dict] = []
    primary_blocks: list[dict] = []
    for run_name, spec in RUNS.items():
        print(f"Running {run_name}")
        data = load_run(bool(spec["prep"]), int(spec["readout"]))
        folds, blocks = evaluate_run(
            run_name, data, capture_blocks=(run_name == "primary_first_readout")
        )
        all_folds.extend(folds)
        primary_blocks.extend(blocks)

    summary = summarize_folds(all_folds)
    bootstrap = paired_bootstrap(primary_blocks)
    primary = "primary_first_readout"
    ara_ba = summary_value(summary, primary, "ara_twocut", "condition_weighted_ba")
    one_ba = summary_value(
        summary, primary, "selected_onecut", "condition_weighted_ba"
    )
    raw_ba = summary_value(summary, primary, "raw_iq_lda", "condition_weighted_ba")
    shuffle_ba = summary_value(
        summary, primary, "label_shuffle", "condition_weighted_ba"
    )
    worst_ba = summary_value(summary, primary, "ara_twocut", "worst_condition_ba")
    ara_fold_rows = [
        r
        for r in all_folds
        if r["run"] == primary and r["arm"] == "ara_twocut"
    ]
    same_disagreements = sum(int(r["ara_raw_disagreements"]) for r in ara_fold_rows)
    reversed_disagreements = sum(
        int(r["pole_reversal_disagreements"]) for r in ara_fold_rows
    )
    complement_residual = max(
        float(r["complement_max_residual"]) for r in ara_fold_rows
    )
    gates = {
        "G1_ara_ba_at_least_0p80": {
            "value": ara_ba,
            "threshold": 0.80,
            "pass": ara_ba >= 0.80,
        },
        "G2_gain_at_least_0p005": {
            "value": ara_ba - one_ba,
            "threshold": 0.005,
            "pass": (ara_ba - one_ba) >= 0.005,
        },
        "G3_gain_ci_low_above_zero": {
            "value": bootstrap["gain_ci_low"],
            "threshold": 0.0,
            "pass": bootstrap["gain_ci_low"] > 0.0,
        },
        "G4_worst_condition_at_least_0p70": {
            "value": worst_ba,
            "threshold": 0.70,
            "pass": worst_ba >= 0.70,
        },
        "G5_equal_information_tie": {
            "accuracy_difference": abs(ara_ba - raw_ba),
            "disagreements": same_disagreements,
            "threshold": 1e-12,
            "pass": abs(ara_ba - raw_ba) <= 1e-12
            and same_disagreements == 0,
        },
        "G6_pole_reversal_and_complement": {
            "reversal_disagreements": reversed_disagreements,
            "complement_max_residual": complement_residual,
            "threshold": 1e-12,
            "pass": reversed_disagreements == 0 and complement_residual <= 1e-12,
        },
        "G7_label_shuffle_at_most_0p55": {
            "value": shuffle_ba,
            "threshold": 0.55,
            "pass": shuffle_ba <= 0.55,
        },
    }
    gate_count = sum(int(v["pass"]) for v in gates.values())
    verdict = "SUPPORTED" if gate_count == len(gates) else "NOT SUPPORTED"

    write_csv(FOLDS_CSV, all_folds)
    write_csv(BLOCKS_CSV, primary_blocks)
    write_csv(SUMMARY_CSV, summary)
    result = {
        "protocol_id": "Q2-PUBLIC-HARDWARE-IQ-v1",
        "ledger_id": "T259",
        "verdict": verdict,
        "gates_passed": gate_count,
        "gates_total": len(gates),
        "protocol_sha256": protocol_hash,
        "fidelity_sha256": fidelity_hash,
        "source": {
            "doi": "10.5281/zenodo.14033026",
            "url": SOURCE_URL,
            "archive": ARCHIVE.name,
            "sha256": sha256(ARCHIVE),
            "conditions_hz": list(CONDITIONS),
            "shots_per_class_condition": 50000,
        },
        "primary": {
            "ara_twocut_ba": ara_ba,
            "selected_onecut_ba": one_ba,
            "gain": ara_ba - one_ba,
            "raw_iq_lda_ba": raw_ba,
            "worst_condition_ba": worst_ba,
            "label_shuffle_ba": shuffle_ba,
            "ara_raw_disagreements": same_disagreements,
            "pole_reversal_disagreements": reversed_disagreements,
            "complement_max_residual": complement_residual,
        },
        "bootstrap": bootstrap,
        "gates": gates,
        "summary": summary,
        "artifacts": {
            "folds_csv": FOLDS_CSV.name,
            "blocks_csv": BLOCKS_CSV.name,
            "summary_csv": SUMMARY_CSV.name,
            "results_json": RESULTS_JSON.name,
        },
        "claim_boundary": (
            "Real I/Q readout measurement geometry only; not full Bloch tomography, "
            "a quantum derivation, or evidence for universal ARA ontology."
        ),
    }
    RESULTS_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"verdict": verdict, "gates": f"{gate_count}/{len(gates)}", **result["primary"]}, indent=2))


if __name__ == "__main__":
    main()
