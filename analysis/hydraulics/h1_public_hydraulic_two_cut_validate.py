from __future__ import annotations

import csv
import hashlib
import json
import pathlib

import numpy as np


ROOT = pathlib.Path(__file__).resolve().parent
PUBLIC = ROOT / "public_data"
RESULTS = ROOT / "H1_PUBLIC_HYDRAULIC_RESULTS.json"
PREDICTIONS = ROOT / "H1_PUBLIC_HYDRAULIC_PREDICTIONS.csv"
FOLDS = ROOT / "H1_PUBLIC_HYDRAULIC_FOLDS.csv"
CANDIDATES = ROOT / "H1_PUBLIC_HYDRAULIC_CANDIDATES.csv"
PERMUTATIONS = ROOT / "H1_PUBLIC_HYDRAULIC_PERMUTATIONS.csv"
CONFUSION = ROOT / "H1_PUBLIC_HYDRAULIC_CONFUSION.csv"
SUMMARY = ROOT / "H1_PUBLIC_HYDRAULIC_SUMMARY.csv"
VALIDATION = ROOT / "H1_PUBLIC_HYDRAULIC_VALIDATION.json"
ARCHIVE = PUBLIC / "condition_monitoring_of_hydraulic_systems.zip"
PROTOCOL = ROOT / "H1_PUBLIC_HYDRAULIC_TWO_CUT_PROTOCOL_v1_FROZEN.md"
FIDELITY = ROOT / "H1_PUBLIC_HYDRAULIC_TWO_CUT_FIDELITY_v1.md"

EXPECTED_ARCHIVE = "24128aad2ee45eea7e6b63ebbd9992cdf25d0483a2cebefbfc13bc69079af1f2"
EXPECTED_PROTOCOL = "bd23be7b65468eec5ccee020f41294636bd714b40276896cf0b409d8541bd391"
EXPECTED_FIDELITY = "2e1a6c660fb591c822d322d6463dbef7972426e0dd0a05f0e27e745e684392ac"
CLASSES = [90, 100, 115, 130]


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rows(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def balanced_accuracy(truth: np.ndarray, prediction: np.ndarray) -> float:
    recalls = []
    for label in sorted(np.unique(truth)):
        mask = truth == label
        recalls.append(float(np.mean(prediction[mask] == label)))
    return float(np.mean(recalls))


def grouped_bootstrap(prediction_rows: list[dict[str, str]]) -> tuple[float, float]:
    rng = np.random.default_rng(2600)
    row_by_cycle = {int(row["cycle_index"]): row for row in prediction_rows}
    by_fold: dict[int, set[int]] = {}
    group_cycles: dict[int, list[int]] = {}
    for row in prediction_rows:
        fold = int(row["outer_fold"])
        group = int(row["group"])
        cycle = int(row["cycle_index"])
        by_fold.setdefault(fold, set()).add(group)
        group_cycles.setdefault(group, []).append(cycle)
    gains = np.empty(2000, dtype=np.float64)
    for b in range(2000):
        sampled: list[int] = []
        for fold in sorted(by_fold):
            available = np.array(sorted(by_fold[fold]), dtype=int)
            selected = rng.choice(available, size=available.size, replace=True)
            for group in selected:
                sampled.extend(group_cycles[int(group)])
        truth = np.array([int(row_by_cycle[c]["truth"]) for c in sampled], dtype=int)
        pair = np.array(
            [int(row_by_cycle[c]["pair_prediction"]) for c in sampled], dtype=int
        )
        single = np.array(
            [int(row_by_cycle[c]["single_prediction"]) for c in sampled], dtype=int
        )
        gains[b] = balanced_accuracy(truth, pair) - balanced_accuracy(truth, single)
    return float(np.quantile(gains, 0.025)), float(np.quantile(gains, 0.975))


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    prediction_rows = rows(PREDICTIONS)
    fold_rows = rows(FOLDS)
    candidate_rows = rows(CANDIDATES)
    permutation_rows = rows(PERMUTATIONS)
    confusion_rows = rows(CONFUSION)
    summary_rows = rows(SUMMARY)

    checks: list[dict] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"name": name, "pass": bool(passed), "detail": detail})

    check("archive_hash", sha256(ARCHIVE) == EXPECTED_ARCHIVE, sha256(ARCHIVE))
    check("protocol_hash", sha256(PROTOCOL) == EXPECTED_PROTOCOL, sha256(PROTOCOL))
    check("fidelity_hash", sha256(FIDELITY) == EXPECTED_FIDELITY, sha256(FIDELITY))

    cycle_index = np.array([int(row["cycle_index"]) for row in prediction_rows], dtype=int)
    truth = np.array([int(row["truth"]) for row in prediction_rows], dtype=int)
    pair = np.array([int(row["pair_prediction"]) for row in prediction_rows], dtype=int)
    single = np.array(
        [int(row["single_prediction"]) for row in prediction_rows], dtype=int
    )
    raw = np.array(
        [int(row["raw_pair_prediction"]) for row in prediction_rows], dtype=int
    )
    reversal = np.array(
        [int(row["reversal_prediction"]) for row in prediction_rows], dtype=int
    )
    destroyed = np.array(
        [int(row["phase_destroyed_prediction"]) for row in prediction_rows], dtype=int
    )
    forest = np.array(
        [int(row["forest_prediction"]) for row in prediction_rows], dtype=int
    )

    check("prediction_row_count", len(prediction_rows) == 2205, len(prediction_rows))
    check(
        "cycles_exactly_once",
        np.array_equal(np.sort(cycle_index), np.arange(2205)),
        len(np.unique(cycle_index)),
    )
    check("target_classes", sorted(np.unique(truth).tolist()) == CLASSES, sorted(np.unique(truth).tolist()))
    check("five_outer_folds", len(fold_rows) == 5, len(fold_rows))

    group_to_fold: dict[int, set[int]] = {}
    fold_classes: dict[int, set[int]] = {}
    for row in prediction_rows:
        group_to_fold.setdefault(int(row["group"]), set()).add(int(row["outer_fold"]))
        fold_classes.setdefault(int(row["outer_fold"]), set()).add(int(row["truth"]))
    check(
        "whole_group_holdout",
        all(len(folds) == 1 for folds in group_to_fold.values()),
        len(group_to_fold),
    )
    check(
        "complete_classes_each_fold",
        all(sorted(values) == CLASSES for values in fold_classes.values()),
        {str(key): sorted(value) for key, value in fold_classes.items()},
    )

    candidate_by_fold_kind: dict[tuple[int, str], list[tuple[str, float]]] = {}
    for row in candidate_rows:
        key = (int(row["outer_fold"]), row["kind"])
        candidate_by_fold_kind.setdefault(key, []).append(
            (row["candidate"], float(row["mean_inner_balanced_accuracy"]))
        )
    selection_ok = True
    selection_detail = []
    for row in fold_rows:
        fold = int(row["outer_fold"])
        for kind, field in [("single", "selected_single"), ("pair", "selected_pair")]:
            ranked = sorted(
                candidate_by_fold_kind[(fold, kind)], key=lambda item: (-item[1], item[0])
            )
            expected = ranked[0][0]
            observed = row[field]
            selection_ok &= expected == observed
            selection_detail.append(
                {"fold": fold, "kind": kind, "expected": expected, "observed": observed}
            )
    check("nested_selection_reproduced", selection_ok, selection_detail)

    pair_ba = balanced_accuracy(truth, pair)
    single_ba = balanced_accuracy(truth, single)
    gain = pair_ba - single_ba
    raw_ba = balanced_accuracy(truth, raw)
    reversal_ba = balanced_accuracy(truth, reversal)
    destroyed_ba = balanced_accuracy(truth, destroyed)
    forest_ba = balanced_accuracy(truth, forest)
    check(
        "pair_accuracy_recomputed",
        abs(pair_ba - result["primary"]["pair_balanced_accuracy"]) <= 1e-15,
        pair_ba,
    )
    check(
        "single_accuracy_recomputed",
        abs(single_ba - result["primary"]["single_balanced_accuracy"]) <= 1e-15,
        single_ba,
    )
    check(
        "gain_recomputed",
        abs(gain - result["primary"]["gain"]) <= 1e-15,
        gain,
    )

    recalls = {}
    for label in CLASSES:
        mask = truth == label
        recalls[str(label)] = float(np.mean(pair[mask] == label))
    check(
        "class_recalls_recomputed",
        all(
            abs(recalls[key] - result["primary"]["class_recalls"][key]) <= 1e-15
            for key in recalls
        ),
        recalls,
    )

    fold_gains = []
    fold_metric_ok = True
    for fold_row in fold_rows:
        fold = int(fold_row["outer_fold"])
        mask = np.array(
            [int(row["outer_fold"]) == fold for row in prediction_rows], dtype=bool
        )
        fold_pair = balanced_accuracy(truth[mask], pair[mask])
        fold_single = balanced_accuracy(truth[mask], single[mask])
        fold_gain = fold_pair - fold_single
        fold_gains.append(fold_gain)
        fold_metric_ok &= (
            abs(fold_pair - float(fold_row["pair_balanced_accuracy"])) <= 1e-15
            and abs(fold_single - float(fold_row["single_balanced_accuracy"])) <= 1e-15
            and abs(fold_gain - float(fold_row["gain"])) <= 1e-15
        )
    check("fold_metrics_recomputed", fold_metric_ok, fold_gains)
    check(
        "pair_wins_all_folds",
        sum(value > 0 for value in fold_gains) == result["primary"]["pair_fold_wins"],
        sum(value > 0 for value in fold_gains),
    )

    low, high = grouped_bootstrap(prediction_rows)
    expected_low, expected_high = result["primary"]["gain_ci_95"]
    check(
        "bootstrap_interval_recomputed",
        abs(low - expected_low) <= 1e-15 and abs(high - expected_high) <= 1e-15,
        [low, high],
    )

    check(
        "raw_ara_predictions_exact",
        np.array_equal(pair, raw)
        and abs(pair_ba - raw_ba) <= 1e-15
        and result["coordinate_controls"]["raw_ara_disagreements"] == 0,
        {"disagreements": int(np.sum(pair != raw)), "raw_ba": raw_ba},
    )
    check(
        "pole_reversal_exact",
        np.array_equal(pair, reversal)
        and abs(pair_ba - reversal_ba) <= 1e-15
        and result["coordinate_controls"]["reversal_disagreements"] == 0,
        {"disagreements": int(np.sum(pair != reversal)), "reversal_ba": reversal_ba},
    )

    permutation_scores = np.array(
        [float(row["balanced_accuracy"]) for row in permutation_rows], dtype=float
    )
    permutation_mean = float(np.mean(permutation_scores))
    permutation_p95 = float(np.quantile(permutation_scores, 0.95))
    check("permutation_count", permutation_scores.size == 500, permutation_scores.size)
    check(
        "permutation_summary_recomputed",
        abs(permutation_mean - result["negative_controls"]["label_permutation_mean"])
        <= 1e-15
        and abs(permutation_p95 - result["negative_controls"]["label_permutation_p95"])
        <= 1e-15,
        {"mean": permutation_mean, "p95": permutation_p95},
    )
    check(
        "diagnostic_accuracies_recomputed",
        abs(destroyed_ba - result["diagnostics"]["phase_destroyed_balanced_accuracy"])
        <= 1e-15
        and abs(forest_ba - result["diagnostics"]["random_forest_balanced_accuracy"])
        <= 1e-15,
        {"phase_destroyed": destroyed_ba, "random_forest": forest_ba},
    )

    confusion_total = sum(int(row["count"]) for row in confusion_rows)
    check("confusion_total", confusion_total == 2205, confusion_total)

    summary = {row["metric"]: float(row["value"]) for row in summary_rows}
    check(
        "summary_matches_primary",
        abs(summary["pair_balanced_accuracy"] - pair_ba) <= 1e-15
        and abs(summary["single_balanced_accuracy"] - single_ba) <= 1e-15
        and abs(summary["gain"] - gain) <= 1e-15,
        {
            "pair": summary["pair_balanced_accuracy"],
            "single": summary["single_balanced_accuracy"],
            "gain": summary["gain"],
        },
    )

    independent_gates = {
        "H1_G1_pair_ba": pair_ba >= 0.75,
        "H1_G2_gain": gain >= 0.03,
        "H1_G3_gain_ci_low": low > 0,
        "H1_G4_worst_class_recall": min(recalls.values()) >= 0.60,
        "H1_G5_fold_wins": sum(value > 0 for value in fold_gains) >= 4,
        "H1_G6_raw_ara_tie": np.array_equal(pair, raw),
        "H1_G7_reversal": np.array_equal(pair, reversal),
        "H1_G8_permutations": permutation_mean <= 0.30 and permutation_p95 <= 0.35,
    }
    independent_count = sum(independent_gates.values())
    independent_verdict = "SUPPORTED" if independent_count == 8 else "NOT SUPPORTED"
    check(
        "gates_recomputed",
        independent_gates
        == {key: bool(value["pass"]) for key, value in result["gates"].items()},
        independent_gates,
    )
    check(
        "verdict_recomputed",
        independent_verdict == result["verdict"]
        and independent_count == result["gates_passed"],
        {"verdict": independent_verdict, "gates": independent_count},
    )

    passed = sum(item["pass"] for item in checks)
    validation = {
        "validation_status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "independent_verdict": independent_verdict,
        "independent_gate_count": independent_count,
        "checks": checks,
    }
    VALIDATION.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))
    if passed != len(checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
