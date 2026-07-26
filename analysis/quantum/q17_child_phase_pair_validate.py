from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "Q16_ARA2_RAW_FOUR_CHILD_RECORDS.csv"
PROTOCOL = ROOT / "Q17_CHILD_PHASE_PAIR_PROTOCOL_v1_FROZEN.md"
PRIMARY_CODE = ROOT / "q17_child_phase_pair_test.py"
RESULTS = ROOT / "Q17_CHILD_PHASE_PAIR_RESULTS.json"
CONTROLS = ROOT / "Q17_CHILD_PHASE_PAIR_CONTROLS.csv"
VALIDATION = ROOT / "Q17_CHILD_PHASE_PAIR_VALIDATION.json"

CHILDREN = ("C00", "C01", "C10", "C11")
ARCHITECTURES = (
    ("P1", ((0, 1), (2, 3))),
    ("P2", ((0, 2), (1, 3))),
    ("P3", ((0, 3), (1, 2))),
)
EXPECTED_SOURCE_HASH = "0f7e58b349e5bf3cdda0110a99627134c7a76c69bb0443be8ba1576c4f01e48b"
EXPECTED_PROTOCOL_HASH = "58f7520b9521e80620d2a232974b96fec3d4ac43bb7b5063d5f1f1dbc8228bb3"


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def cos(a: np.ndarray, b: np.ndarray) -> float:
    denominator = np.linalg.norm(a) * np.linalg.norm(b)
    return 0.0 if denominator == 0 else float(np.dot(a, b) / denominator)


def arrays_from_csv() -> tuple[dict[str, np.ndarray], list[str], pd.DataFrame]:
    frame = pd.read_csv(SOURCE, usecols=["child", "split", "record_index", "cut", "ara_x"])
    cuts = sorted(
        frame["cut"].unique(),
        key=lambda value: (int(value.split("G")[0][1:]), int(value.split("G")[1])),
    )
    arrays = {}
    for split in ("development", "holdout"):
        split_frame = frame[frame["split"] == split]
        record_ids = sorted(split_frame["record_index"].unique())
        child_arrays = []
        for child in CHILDREN:
            matrix = (
                split_frame[split_frame["child"] == child]
                .pivot(index="record_index", columns="cut", values="ara_x")
                .reindex(index=record_ids, columns=cuts)
                .to_numpy()
            )
            child_arrays.append(matrix)
        arrays[split] = np.stack(child_arrays)
    return arrays, cuts, frame


def geometry(data: np.ndarray) -> dict:
    means = data.mean(axis=1)
    centre = means.mean(axis=0)
    radial = means - centre
    lengths = np.linalg.norm(radial, axis=1)
    radius = float(np.sqrt(np.mean(lengths**2)))
    pairs = {}
    for i in range(4):
        for j in range(i + 1, 4):
            pair = f"{CHILDREN[i]}-{CHILDREN[j]}"
            norm_sum = lengths[i] + lengths[j]
            pairs[pair] = {
                "opposition": -cos(radial[i], radial[j]),
                "balance": float(2 * min(lengths[i], lengths[j]) / norm_sum),
                "closure_error": float(np.linalg.norm((means[i] + means[j]) / 2 - centre) / radius),
            }
    architectures = {}
    for name, pair_indices in ARCHITECTURES:
        names = [f"{CHILDREN[i]}-{CHILDREN[j]}" for i, j in pair_indices]
        values = [pairs[pair] for pair in names]
        error = max(value["closure_error"] for value in values)
        anti = min((value["opposition"] + 1) / 2 for value in values)
        balance = min(value["balance"] for value in values)
        architectures[name] = {
            "max_closure_error": error,
            "min_opposition": min(value["opposition"] for value in values),
            "min_balance": balance,
            "quality_q": float((1 / (1 + error)) * anti * balance),
        }
    ranking = sorted(architectures, key=lambda name: (-architectures[name]["quality_q"], name))
    return {
        "means": means,
        "pairs": pairs,
        "architectures": architectures,
        "winner": ranking[0],
        "ranking": ranking,
    }


def pair_check(dev: np.ndarray, hold: np.ndarray, i: int, j: int) -> dict:
    dev_a, dev_b = dev[i].mean(axis=0), dev[j].mean(axis=0)
    hold_a, hold_b = hold[i].mean(axis=0), hold[j].mean(axis=0)
    diameter_dev = (dev_a - dev_b) / 2
    diameter_hold = (hold_a - hold_b) / 2
    unit = diameter_dev / np.linalg.norm(diameter_dev)
    threshold = float(np.dot((dev_a + dev_b) / 2, unit))
    score_a, score_b = hold[i] @ unit, hold[j] @ unit
    accuracy = float((np.mean(score_a >= threshold) + np.mean(score_b < threshold)) / 2)
    pooled_sd = float(np.sqrt((np.var(score_a, ddof=1) + np.var(score_b, ddof=1)) / 2))
    return {
        "persistence": abs(cos(diameter_dev, diameter_hold)),
        "balanced_accuracy": accuracy,
        "dprime": float(abs(score_a.mean() - score_b.mean()) / pooled_sd),
    }


def close(a: float, b: float, tolerance: float = 1e-12) -> bool:
    return bool(abs(float(a) - float(b)) <= tolerance)


if __name__ == "__main__":
    saved = json.loads(RESULTS.read_text(encoding="utf-8"))
    arrays, cuts, frame = arrays_from_csv()
    dev = geometry(arrays["development"])
    hold = geometry(arrays["holdout"])

    checks = {
        "source_hash": file_hash(SOURCE) == EXPECTED_SOURCE_HASH == saved["source_sha256"],
        "protocol_hash": file_hash(PROTOCOL) == EXPECTED_PROTOCOL_HASH == saved["protocol_sha256"],
        "row_count_14400": len(frame) == 14_400,
        "cut_count_45": len(cuts) == 45,
        "no_duplicate_rows": not frame.duplicated(["child", "split", "record_index", "cut"]).any(),
        "development_winner": dev["winner"] == saved["observed"]["development"]["winner"],
        "holdout_winner": hold["winner"] == saved["observed"]["holdout"]["winner"],
    }

    for split, computed in (("development", dev), ("holdout", hold)):
        for pair, metrics in computed["pairs"].items():
            expected = saved["observed"][split]["pairs"][pair]
            for field in ("opposition", "balance", "closure_error"):
                checks[f"{split}_{pair}_{field}"] = close(metrics[field], expected[field])
        for architecture, metrics in computed["architectures"].items():
            expected = saved["observed"][split]["architectures"][architecture]
            for field in ("max_closure_error", "min_opposition", "min_balance", "quality_q"):
                checks[f"{split}_{architecture}_{field}"] = close(metrics[field], expected[field])

    selected = saved["observed"]["selected_architecture"]
    selected_pairs = next(pairs for name, pairs in ARCHITECTURES if name == selected)
    recomputed_selected = {}
    for i, j in selected_pairs:
        pair_name = f"{CHILDREN[i]}-{CHILDREN[j]}"
        metrics = pair_check(arrays["development"], arrays["holdout"], i, j)
        recomputed_selected[pair_name] = metrics
        expected = saved["observed"]["selected_pair_holdout"][pair_name]
        for field in ("persistence", "balanced_accuracy", "dprime"):
            checks[f"selected_{pair_name}_{field}"] = close(metrics[field], expected[field])

    selected_hold = hold["architectures"][selected]
    runner_q = max(value["quality_q"] for name, value in hold["architectures"].items() if name != selected)
    gates = {
        "G1_same_winner": hold["winner"] == selected,
        "G2_holdout_q_at_least_0_70": selected_hold["quality_q"] >= 0.70,
        "G3_both_oppositions_at_least_0_80": selected_hold["min_opposition"] >= 0.80,
        "G4_both_balances_at_least_0_80": selected_hold["min_balance"] >= 0.80,
        "G5_both_persistences_at_least_0_80": min(
            value["persistence"] for value in recomputed_selected.values()
        )
        >= 0.80,
        "G6_both_balanced_accuracies_at_least_0_80": min(
            value["balanced_accuracy"] for value in recomputed_selected.values()
        )
        >= 0.80,
        "G7_holdout_margin_at_least_10_percent": selected_hold["quality_q"] >= 1.10 * runner_q,
    }
    checks["gate_vector"] = gates == saved["observed"]["gates_1_to_7"]

    controls = pd.read_csv(CONTROLS)
    shuffle = controls[controls["control_type"] == "balanced_label_shuffle"]
    pseudo = controls[controls["control_type"] == "within_archive_pseudo_child"]
    checks.update(
        {
            "shuffle_rows_9999": len(shuffle) == 9_999,
            "pseudo_rows_1000": len(pseudo) == 1_000,
            "shuffle_pass_count": int(shuffle["passes_gates_1_to_7"].sum())
            == saved["controls"]["balanced_label_shuffle_passes"],
            "pseudo_pass_count": int(pseudo["passes_gates_1_to_7"].sum())
            == saved["controls"]["within_archive_pseudo_child_passes"],
        }
    )

    code_text = PRIMARY_CODE.read_text(encoding="utf-8").lower()
    checks["primary_code_has_no_conventional_state_names"] = not any(
        token in code_text for token in ("psi-plus", "psi-minus", "phi-plus", "phi-minus", "pauli", "ramsey", "hahn")
    )
    checks["verdict_consistent"] = saved["verdict"] == (
        "SUPPORTED"
        if all(gates.values()) and saved["gate_8_controls"]
        else "NOT SUPPORTED"
    )

    failed = [name for name, passed in checks.items() if not passed]
    output = {
        "validator": Path(__file__).name,
        "primary_code_imported": False,
        "checks_run": len(checks),
        "checks_passed": len(checks) - len(failed),
        "failed_checks": failed,
        "all_checks_pass": not failed,
        "recomputed_development_winner": dev["winner"],
        "recomputed_holdout_winner": hold["winner"],
        "recomputed_gates_1_to_7": gates,
        "validated_verdict": saved["verdict"],
    }
    VALIDATION.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))
    if failed:
        raise SystemExit(1)
