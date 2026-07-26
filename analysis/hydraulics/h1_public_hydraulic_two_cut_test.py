from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import pathlib
import urllib.request
import zipfile

import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import balanced_accuracy_score, confusion_matrix
from sklearn.model_selection import StratifiedGroupKFold


ROOT = pathlib.Path(__file__).resolve().parent
PUBLIC = ROOT / "public_data"
ARCHIVE = PUBLIC / "condition_monitoring_of_hydraulic_systems.zip"
EXTRACTED = PUBLIC / "extracted"
FEATURE_CACHE = PUBLIC / "h1_pressure_features.npz"
URL = (
    "https://archive.ics.uci.edu/static/public/447/"
    "condition+monitoring+of+hydraulic+systems.zip"
)
ARCHIVE_SHA256 = "24128aad2ee45eea7e6b63ebbd9992cdf25d0483a2cebefbfc13bc69079af1f2"
SENSORS = tuple(f"PS{i}" for i in range(1, 7))
CLASSES = np.array([90, 100, 115, 130], dtype=int)
OUTER_SEED = 260
BOOTSTRAP_SEED = 2600
N_BOOTSTRAP = 2000
N_PERMUTATIONS = 100

FOLDS_CSV = ROOT / "H1_PUBLIC_HYDRAULIC_FOLDS.csv"
PREDICTIONS_CSV = ROOT / "H1_PUBLIC_HYDRAULIC_PREDICTIONS.csv"
CANDIDATES_CSV = ROOT / "H1_PUBLIC_HYDRAULIC_CANDIDATES.csv"
PERMUTATIONS_CSV = ROOT / "H1_PUBLIC_HYDRAULIC_PERMUTATIONS.csv"
CONFUSION_CSV = ROOT / "H1_PUBLIC_HYDRAULIC_CONFUSION.csv"
SUMMARY_CSV = ROOT / "H1_PUBLIC_HYDRAULIC_SUMMARY.csv"
RESULTS_JSON = ROOT / "H1_PUBLIC_HYDRAULIC_RESULTS.json"


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_and_extract() -> None:
    PUBLIC.mkdir(parents=True, exist_ok=True)
    if not ARCHIVE.exists():
        urllib.request.urlretrieve(URL, ARCHIVE)
    observed = sha256(ARCHIVE)
    if observed.lower() != ARCHIVE_SHA256:
        raise RuntimeError(f"Archive SHA-256 mismatch: {observed}")
    EXTRACTED.mkdir(parents=True, exist_ok=True)
    required = ["profile.txt", *(f"{sensor}.txt" for sensor in SENSORS)]
    with zipfile.ZipFile(ARCHIVE) as archive:
        for name in required:
            target = EXTRACTED / name
            if not target.exists():
                archive.extract(name, EXTRACTED)


def require_source() -> None:
    required = [EXTRACTED / "profile.txt", *(EXTRACTED / f"{s}.txt" for s in SENSORS)]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing extracted source files. Run with --download. Missing: " + ", ".join(missing)
        )
    if sha256(ARCHIVE).lower() != ARCHIVE_SHA256:
        raise RuntimeError("The local UCI archive does not match the frozen SHA-256.")


def fixed_features(trace: np.ndarray) -> np.ndarray:
    if trace.ndim != 2 or trace.shape[1] != 6000:
        raise ValueError(f"Expected n x 6000 pressure trace, got {trace.shape}")
    windows = trace.reshape(trace.shape[0], 12, 500)
    means = windows.mean(axis=2, dtype=np.float64)
    stds = windows.std(axis=2, dtype=np.float64)
    return np.concatenate([means, stds], axis=1)


def load_features() -> tuple[dict[str, np.ndarray], np.ndarray]:
    profile = np.loadtxt(EXTRACTED / "profile.txt", dtype=np.float64)
    if profile.shape != (2205, 5) or not np.isfinite(profile).all():
        raise ValueError(f"Invalid profile shape/values: {profile.shape}")
    if FEATURE_CACHE.exists():
        cached = np.load(FEATURE_CACHE)
        features = {sensor: cached[sensor].astype(np.float64) for sensor in SENSORS}
    else:
        features = {}
        for sensor in SENSORS:
            raw = np.loadtxt(EXTRACTED / f"{sensor}.txt", dtype=np.float32)
            if raw.shape != (2205, 6000) or not np.isfinite(raw).all():
                raise ValueError(f"Invalid {sensor} shape/values: {raw.shape}")
            features[sensor] = fixed_features(raw)
        np.savez_compressed(FEATURE_CACHE, **features)
    for sensor, values in features.items():
        if values.shape != (2205, 24) or not np.isfinite(values).all():
            raise ValueError(f"Invalid derived {sensor} features: {values.shape}")
    return features, profile


def candidate_matrix(features: dict[str, np.ndarray], candidate: tuple[str, ...]) -> np.ndarray:
    return np.concatenate([features[sensor] for sensor in candidate], axis=1)


def calibration(
    x_train: np.ndarray, y_train: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    centre = np.median(x_train, axis=0)
    q25, q75 = np.quantile(x_train, [0.25, 0.75], axis=0)
    scale = (q75 - q25) / 1.349
    fallback = np.std(x_train, axis=0)
    scale = np.where(scale >= 1e-12, scale, fallback)
    keep = np.isfinite(scale) & (scale >= 1e-12)
    if not np.any(keep):
        raise ValueError("Candidate contains no non-constant features.")
    pole_delta = x_train[y_train == 90].mean(axis=0) - x_train[y_train == 130].mean(axis=0)
    orientation = np.where(pole_delta >= 0.0, 1.0, -1.0)
    return centre, scale, orientation, keep


def transform(
    values: np.ndarray,
    params: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
    ara: bool,
) -> np.ndarray:
    centre, scale, orientation, keep = params
    standardized = (values[:, keep] - centre[keep]) / scale[keep]
    if ara:
        return 1.0 + orientation[keep] * standardized
    return standardized


def lda() -> LinearDiscriminantAnalysis:
    return LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto")


def fit_predict(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_test: np.ndarray,
    ara: bool = True,
) -> tuple[np.ndarray, LinearDiscriminantAnalysis, tuple[np.ndarray, ...]]:
    params = calibration(x_train, y_train)
    train_t = transform(x_train, params, ara=ara)
    test_t = transform(x_test, params, ara=ara)
    model = lda().fit(train_t, y_train)
    return model.predict(test_t), model, params


def candidate_inner_score(
    features: dict[str, np.ndarray],
    candidate: tuple[str, ...],
    indices: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    outer_fold: int,
) -> tuple[float, list[float]]:
    matrix = candidate_matrix(features, candidate)
    splitter = StratifiedGroupKFold(
        n_splits=4, shuffle=True, random_state=1260 + outer_fold
    )
    scores: list[float] = []
    for train_local, test_local in splitter.split(
        np.zeros(indices.size), y[indices], groups[indices]
    ):
        train_idx = indices[train_local]
        test_idx = indices[test_local]
        if set(y[train_idx]) != set(CLASSES) or set(y[test_idx]) != set(CLASSES):
            raise RuntimeError(
                f"BLOCKED: inner fold lacks classes in outer fold {outer_fold}."
            )
        prediction, _, _ = fit_predict(
            matrix[train_idx], y[train_idx], matrix[test_idx], ara=True
        )
        scores.append(float(balanced_accuracy_score(y[test_idx], prediction)))
    return float(np.mean(scores)), scores


def select_candidates(
    features: dict[str, np.ndarray],
    train_idx: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    outer_fold: int,
) -> tuple[tuple[str, ...], tuple[str, ...], list[dict]]:
    singles = [(sensor,) for sensor in SENSORS]
    pairs = list(itertools.combinations(SENSORS, 2))
    rows: list[dict] = []
    scores: dict[tuple[str, ...], float] = {}
    for candidate in [*singles, *pairs]:
        mean_score, inner_scores = candidate_inner_score(
            features, candidate, train_idx, y, groups, outer_fold
        )
        scores[candidate] = mean_score
        rows.append(
            {
                "outer_fold": outer_fold,
                "kind": "single" if len(candidate) == 1 else "pair",
                "candidate": "+".join(candidate),
                "mean_inner_balanced_accuracy": mean_score,
                "inner_scores": json.dumps(inner_scores),
            }
        )
    best_single = sorted(singles, key=lambda c: (-scores[c], c))[0]
    best_pair = sorted(pairs, key=lambda c: (-scores[c], c))[0]
    return best_single, best_pair, rows


def phase_destroy_pair(matrix: np.ndarray, cycle_indices: np.ndarray) -> np.ndarray:
    destroyed = matrix.copy()
    second = destroyed[:, 24:48]
    means = second[:, :12].copy()
    stds = second[:, 12:24].copy()
    for row, cycle_index in enumerate(cycle_indices):
        shift = int(cycle_index % 11) + 1
        means[row] = np.roll(means[row], shift)
        stds[row] = np.roll(stds[row], shift)
    destroyed[:, 24:36] = means
    destroyed[:, 36:48] = stds
    return destroyed


def write_rows(path: pathlib.Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def macro_gain(
    truth: np.ndarray, pair_prediction: np.ndarray, single_prediction: np.ndarray
) -> float:
    return float(
        balanced_accuracy_score(truth, pair_prediction)
        - balanced_accuracy_score(truth, single_prediction)
    )


def bootstrap_gain(
    prediction_rows: list[dict], groups: np.ndarray
) -> tuple[float, float, np.ndarray]:
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    by_fold: dict[int, list[int]] = {}
    row_by_cycle = {int(row["cycle_index"]): row for row in prediction_rows}
    for row in prediction_rows:
        by_fold.setdefault(int(row["outer_fold"]), []).append(int(row["cycle_index"]))
    fold_groups: dict[int, list[int]] = {}
    for fold, cycles in by_fold.items():
        fold_groups[fold] = sorted({int(groups[cycle]) for cycle in cycles})
    group_cycles: dict[int, list[int]] = {}
    for cycle in row_by_cycle:
        group_cycles.setdefault(int(groups[cycle]), []).append(cycle)

    gains = np.empty(N_BOOTSTRAP, dtype=np.float64)
    for b in range(N_BOOTSTRAP):
        sampled_cycles: list[int] = []
        for fold in sorted(fold_groups):
            available = np.array(fold_groups[fold], dtype=int)
            selected = rng.choice(available, size=available.size, replace=True)
            for group in selected:
                sampled_cycles.extend(group_cycles[int(group)])
        truth = np.array([row_by_cycle[c]["truth"] for c in sampled_cycles], dtype=int)
        pair_pred = np.array(
            [row_by_cycle[c]["pair_prediction"] for c in sampled_cycles], dtype=int
        )
        single_pred = np.array(
            [row_by_cycle[c]["single_prediction"] for c in sampled_cycles], dtype=int
        )
        gains[b] = macro_gain(truth, pair_pred, single_pred)
    return (
        float(np.quantile(gains, 0.025)),
        float(np.quantile(gains, 0.975)),
        gains,
    )


def run() -> dict:
    features, profile = load_features()
    y = profile[:, 3].astype(int)
    groups = np.arange(y.size, dtype=int) // 15
    splitter = StratifiedGroupKFold(
        n_splits=5, shuffle=True, random_state=OUTER_SEED
    )

    fold_rows: list[dict] = []
    prediction_rows: list[dict] = []
    candidate_rows: list[dict] = []
    permutation_rows: list[dict] = []
    selected_pairs: list[tuple[str, ...]] = []
    selected_singles: list[tuple[str, ...]] = []

    for outer_fold, (train_idx, test_idx) in enumerate(
        splitter.split(np.zeros(y.size), y, groups)
    ):
        if set(y[train_idx]) != set(CLASSES) or set(y[test_idx]) != set(CLASSES):
            raise RuntimeError(f"BLOCKED: outer fold {outer_fold} lacks a class.")
        best_single, best_pair, candidate_part = select_candidates(
            features, train_idx, y, groups, outer_fold
        )
        candidate_rows.extend(candidate_part)
        selected_singles.append(best_single)
        selected_pairs.append(best_pair)

        x_single = candidate_matrix(features, best_single)
        x_pair = candidate_matrix(features, best_pair)

        single_pred, _, _ = fit_predict(
            x_single[train_idx], y[train_idx], x_single[test_idx], ara=True
        )
        pair_pred, pair_model, pair_params = fit_predict(
            x_pair[train_idx], y[train_idx], x_pair[test_idx], ara=True
        )
        raw_pred, _, _ = fit_predict(
            x_pair[train_idx], y[train_idx], x_pair[test_idx], ara=False
        )

        train_ara = transform(x_pair[train_idx], pair_params, ara=True)
        test_ara = transform(x_pair[test_idx], pair_params, ara=True)
        reversal_model = lda().fit(2.0 - train_ara, y[train_idx])
        reversal_pred = reversal_model.predict(2.0 - test_ara)

        destroyed_raw = phase_destroy_pair(x_pair[test_idx], test_idx)
        destroyed_pred = pair_model.predict(
            transform(destroyed_raw, pair_params, ara=True)
        )

        forest = RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced_subsample",
            max_features="sqrt",
            random_state=3260 + outer_fold,
            n_jobs=-1,
        )
        forest.fit(x_pair[train_idx], y[train_idx])
        forest_pred = forest.predict(x_pair[test_idx])

        pair_ba = float(balanced_accuracy_score(y[test_idx], pair_pred))
        single_ba = float(balanced_accuracy_score(y[test_idx], single_pred))
        raw_ba = float(balanced_accuracy_score(y[test_idx], raw_pred))
        destroyed_ba = float(balanced_accuracy_score(y[test_idx], destroyed_pred))
        forest_ba = float(balanced_accuracy_score(y[test_idx], forest_pred))
        raw_disagreements = int(np.sum(pair_pred != raw_pred))
        reversal_disagreements = int(np.sum(pair_pred != reversal_pred))

        fold_rows.append(
            {
                "outer_fold": outer_fold,
                "train_cycles": int(train_idx.size),
                "test_cycles": int(test_idx.size),
                "test_groups": int(np.unique(groups[test_idx]).size),
                "selected_single": "+".join(best_single),
                "selected_pair": "+".join(best_pair),
                "single_balanced_accuracy": single_ba,
                "pair_balanced_accuracy": pair_ba,
                "gain": pair_ba - single_ba,
                "raw_pair_balanced_accuracy": raw_ba,
                "raw_ara_disagreements": raw_disagreements,
                "reversal_disagreements": reversal_disagreements,
                "phase_destroyed_balanced_accuracy": destroyed_ba,
                "random_forest_balanced_accuracy": forest_ba,
            }
        )

        for local, cycle_index in enumerate(test_idx):
            prediction_rows.append(
                {
                    "cycle_index": int(cycle_index),
                    "outer_fold": outer_fold,
                    "group": int(groups[cycle_index]),
                    "truth": int(y[cycle_index]),
                    "single_prediction": int(single_pred[local]),
                    "pair_prediction": int(pair_pred[local]),
                    "raw_pair_prediction": int(raw_pred[local]),
                    "reversal_prediction": int(reversal_pred[local]),
                    "phase_destroyed_prediction": int(destroyed_pred[local]),
                    "forest_prediction": int(forest_pred[local]),
                    "cooler": int(profile[cycle_index, 0]),
                    "valve": int(profile[cycle_index, 1]),
                    "pump": int(profile[cycle_index, 2]),
                    "stable_flag": int(profile[cycle_index, 4]),
                    "selected_single": "+".join(best_single),
                    "selected_pair": "+".join(best_pair),
                }
            )

        rng = np.random.default_rng(4260 + outer_fold)
        for permutation in range(N_PERMUTATIONS):
            permuted_y = rng.permutation(y[train_idx])
            perm_pred, _, _ = fit_predict(
                x_pair[train_idx], permuted_y, x_pair[test_idx], ara=True
            )
            permutation_rows.append(
                {
                    "outer_fold": outer_fold,
                    "permutation": permutation,
                    "balanced_accuracy": float(
                        balanced_accuracy_score(y[test_idx], perm_pred)
                    ),
                }
            )

    write_rows(FOLDS_CSV, fold_rows)
    write_rows(PREDICTIONS_CSV, prediction_rows)
    write_rows(CANDIDATES_CSV, candidate_rows)
    write_rows(PERMUTATIONS_CSV, permutation_rows)

    truth = np.array([row["truth"] for row in prediction_rows], dtype=int)
    pair_pred = np.array([row["pair_prediction"] for row in prediction_rows], dtype=int)
    single_pred = np.array(
        [row["single_prediction"] for row in prediction_rows], dtype=int
    )
    raw_pred = np.array(
        [row["raw_pair_prediction"] for row in prediction_rows], dtype=int
    )
    reversal_pred = np.array(
        [row["reversal_prediction"] for row in prediction_rows], dtype=int
    )
    destroyed_pred = np.array(
        [row["phase_destroyed_prediction"] for row in prediction_rows], dtype=int
    )
    forest_pred = np.array(
        [row["forest_prediction"] for row in prediction_rows], dtype=int
    )

    pair_ba = float(balanced_accuracy_score(truth, pair_pred))
    single_ba = float(balanced_accuracy_score(truth, single_pred))
    gain = pair_ba - single_ba
    raw_ba = float(balanced_accuracy_score(truth, raw_pred))
    reversal_ba = float(balanced_accuracy_score(truth, reversal_pred))
    destroyed_ba = float(balanced_accuracy_score(truth, destroyed_pred))
    forest_ba = float(balanced_accuracy_score(truth, forest_pred))
    gain_low, gain_high, _ = bootstrap_gain(prediction_rows, groups)

    matrix = confusion_matrix(truth, pair_pred, labels=CLASSES)
    recalls = np.diag(matrix) / matrix.sum(axis=1)
    confusion_rows: list[dict] = []
    for i, true_class in enumerate(CLASSES):
        for j, predicted_class in enumerate(CLASSES):
            confusion_rows.append(
                {
                    "true_class": int(true_class),
                    "predicted_class": int(predicted_class),
                    "count": int(matrix[i, j]),
                    "row_rate": float(matrix[i, j] / matrix[i].sum()),
                }
            )
    write_rows(CONFUSION_CSV, confusion_rows)

    fold_gains = np.array([row["gain"] for row in fold_rows], dtype=np.float64)
    pair_wins = int(np.sum(fold_gains > 0.0))
    permutation_scores = np.array(
        [row["balanced_accuracy"] for row in permutation_rows], dtype=np.float64
    )
    permutation_mean = float(np.mean(permutation_scores))
    permutation_p95 = float(np.quantile(permutation_scores, 0.95))
    raw_disagreements = int(np.sum(pair_pred != raw_pred))
    reversal_disagreements = int(np.sum(pair_pred != reversal_pred))

    gates = {
        "H1_G1_pair_ba": {"pass": pair_ba >= 0.75, "value": pair_ba, "threshold": 0.75},
        "H1_G2_gain": {"pass": gain >= 0.03, "value": gain, "threshold": 0.03},
        "H1_G3_gain_ci_low": {
            "pass": gain_low > 0.0,
            "value": gain_low,
            "threshold": 0.0,
        },
        "H1_G4_worst_class_recall": {
            "pass": float(np.min(recalls)) >= 0.60,
            "value": float(np.min(recalls)),
            "threshold": 0.60,
        },
        "H1_G5_fold_wins": {
            "pass": pair_wins >= 4,
            "value": pair_wins,
            "threshold": 4,
        },
        "H1_G6_raw_ara_tie": {
            "pass": abs(pair_ba - raw_ba) <= 1e-12 and raw_disagreements == 0,
            "accuracy_difference": pair_ba - raw_ba,
            "disagreements": raw_disagreements,
            "threshold": 1e-12,
        },
        "H1_G7_reversal": {
            "pass": reversal_disagreements == 0,
            "accuracy_difference": pair_ba - reversal_ba,
            "disagreements": reversal_disagreements,
            "threshold": 0,
        },
        "H1_G8_permutations": {
            "pass": permutation_mean <= 0.30 and permutation_p95 <= 0.35,
            "mean": permutation_mean,
            "p95": permutation_p95,
            "mean_threshold": 0.30,
            "p95_threshold": 0.35,
        },
    }
    gates_passed = int(sum(bool(gate["pass"]) for gate in gates.values()))
    verdict = "SUPPORTED" if gates_passed == len(gates) else "NOT SUPPORTED"

    summary_rows = [
        {"metric": "pair_balanced_accuracy", "value": pair_ba},
        {"metric": "single_balanced_accuracy", "value": single_ba},
        {"metric": "gain", "value": gain},
        {"metric": "gain_ci_low", "value": gain_low},
        {"metric": "gain_ci_high", "value": gain_high},
        {"metric": "worst_class_recall", "value": float(np.min(recalls))},
        {"metric": "pair_fold_wins", "value": pair_wins},
        {"metric": "raw_pair_balanced_accuracy", "value": raw_ba},
        {"metric": "raw_ara_disagreements", "value": raw_disagreements},
        {"metric": "reversal_disagreements", "value": reversal_disagreements},
        {"metric": "permutation_mean", "value": permutation_mean},
        {"metric": "permutation_p95", "value": permutation_p95},
        {"metric": "phase_destroyed_balanced_accuracy", "value": destroyed_ba},
        {"metric": "random_forest_balanced_accuracy", "value": forest_ba},
        {"metric": "gates_passed", "value": gates_passed},
        {"metric": "gates_total", "value": len(gates)},
    ]
    write_rows(SUMMARY_CSV, summary_rows)

    results = {
        "test_id": "T260-H1",
        "status": verdict,
        "archive_sha256": sha256(ARCHIVE),
        "source_instances": int(y.size),
        "classes": CLASSES.tolist(),
        "outer_folds": len(fold_rows),
        "primary": {
            "pair_balanced_accuracy": pair_ba,
            "single_balanced_accuracy": single_ba,
            "gain": gain,
            "gain_ci_95": [gain_low, gain_high],
            "worst_class_recall": float(np.min(recalls)),
            "class_recalls": {
                str(int(label)): float(value) for label, value in zip(CLASSES, recalls)
            },
            "pair_fold_wins": pair_wins,
            "selected_singles": ["+".join(value) for value in selected_singles],
            "selected_pairs": ["+".join(value) for value in selected_pairs],
        },
        "coordinate_controls": {
            "raw_pair_balanced_accuracy": raw_ba,
            "raw_ara_accuracy_difference": pair_ba - raw_ba,
            "raw_ara_disagreements": raw_disagreements,
            "reversal_balanced_accuracy": reversal_ba,
            "reversal_disagreements": reversal_disagreements,
        },
        "negative_controls": {
            "label_permutation_mean": permutation_mean,
            "label_permutation_p95": permutation_p95,
        },
        "diagnostics": {
            "phase_destroyed_balanced_accuracy": destroyed_ba,
            "random_forest_balanced_accuracy": forest_ba,
        },
        "gates": gates,
        "gates_passed": gates_passed,
        "gates_total": len(gates),
        "verdict": verdict,
        "files": {
            "folds": FOLDS_CSV.name,
            "predictions": PREDICTIONS_CSV.name,
            "candidates": CANDIDATES_CSV.name,
            "permutations": PERMUTATIONS_CSV.name,
            "confusion": CONFUSION_CSV.name,
            "summary": SUMMARY_CSV.name,
        },
    }
    RESULTS_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    if args.download:
        download_and_extract()
    require_source()
    results = run()
    print(
        json.dumps(
            {
                "verdict": results["verdict"],
                "gates": f"{results['gates_passed']}/{results['gates_total']}",
                "pair_balanced_accuracy": results["primary"]["pair_balanced_accuracy"],
                "single_balanced_accuracy": results["primary"][
                    "single_balanced_accuracy"
                ],
                "gain": results["primary"]["gain"],
                "gain_ci_95": results["primary"]["gain_ci_95"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
