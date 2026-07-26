from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "Q16_ARA2_RAW_FOUR_CHILD_RECORDS.csv"
PROTOCOL = ROOT / "Q17_CHILD_PHASE_PAIR_PROTOCOL_v1_FROZEN.md"
RESULTS = ROOT / "Q17_CHILD_PHASE_PAIR_RESULTS.json"
PAIR_CSV = ROOT / "Q17_CHILD_PHASE_PAIR_METRICS.csv"
ARCH_CSV = ROOT / "Q17_CHILD_PHASE_PAIR_ARCHITECTURES.csv"
CONTROL_CSV = ROOT / "Q17_CHILD_PHASE_PAIR_CONTROLS.csv"
LEAVEOUT_CSV = ROOT / "Q17_CHILD_PHASE_PAIR_LEAVE_SETTING_OUT.csv"

EXPECTED_SOURCE_SHA256 = "0f7e58b349e5bf3cdda0110a99627134c7a76c69bb0443be8ba1576c4f01e48b"
EXPECTED_PROTOCOL_SHA256 = "58f7520b9521e80620d2a232974b96fec3d4ac43bb7b5063d5f1f1dbc8228bb3"
SEED = 20260725
N_SHUFFLES = 9_999
N_PSEUDO = 1_000

CHILDREN = ("C00", "C01", "C10", "C11")
ARCHITECTURES = (
    ("P1", (("C00", "C01"), ("C10", "C11"))),
    ("P2", (("C00", "C10"), ("C01", "C11"))),
    ("P3", (("C00", "C11"), ("C01", "C10"))),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denominator == 0:
        return 0.0
    return float(np.dot(a, b) / denominator)


def load_arrays() -> tuple[dict[str, np.ndarray], list[str]]:
    frame = pd.read_csv(SOURCE, usecols=["child", "split", "record_index", "cut", "ara_x"])
    if set(frame["child"]) != set(CHILDREN):
        raise RuntimeError("unexpected child labels")
    if frame.duplicated(["child", "split", "record_index", "cut"]).any():
        raise RuntimeError("duplicate child/split/record/cut rows")

    cuts = sorted(
        frame["cut"].unique(),
        key=lambda value: (int(value.split("G")[0][1:]), int(value.split("G")[1])),
    )
    if len(cuts) != 45:
        raise RuntimeError(f"expected 45 cuts, found {len(cuts)}")

    arrays: dict[str, np.ndarray] = {}
    for split in ("development", "holdout"):
        part = frame[frame["split"] == split]
        records = sorted(part["record_index"].unique())
        if len(records) != 40:
            raise RuntimeError(f"expected 40 {split} records, found {len(records)}")
        data = np.empty((4, len(records), len(cuts)), dtype=float)
        for child_index, child in enumerate(CHILDREN):
            pivot = (
                part[part["child"] == child]
                .pivot(index="record_index", columns="cut", values="ara_x")
                .reindex(index=records, columns=cuts)
            )
            if pivot.isna().any().any():
                raise RuntimeError(f"incomplete matrix for {split}/{child}")
            data[child_index] = pivot.to_numpy()
        arrays[split] = data
    return arrays, cuts


def split_geometry(data: np.ndarray) -> dict:
    centroids = data.mean(axis=1)
    centre = centroids.mean(axis=0)
    radial = centroids - centre
    norms = np.linalg.norm(radial, axis=1)
    radius = float(np.sqrt(np.mean(norms**2)))
    if radius == 0:
        radius = np.finfo(float).eps

    pair_metrics: dict[str, dict] = {}
    for i in range(4):
        for j in range(i + 1, 4):
            name = f"{CHILDREN[i]}-{CHILDREN[j]}"
            opposition = -cosine(radial[i], radial[j])
            norm_sum = float(norms[i] + norms[j])
            balance = 0.0 if norm_sum == 0 else float(2 * min(norms[i], norms[j]) / norm_sum)
            midpoint = (centroids[i] + centroids[j]) / 2
            closure_error = float(np.linalg.norm(midpoint - centre) / radius)
            pair_metrics[name] = {
                "children": [CHILDREN[i], CHILDREN[j]],
                "opposition": opposition,
                "balance": balance,
                "closure_error": closure_error,
                "radial_norm_a": float(norms[i]),
                "radial_norm_b": float(norms[j]),
            }

    architecture_metrics: dict[str, dict] = {}
    for architecture, pairs in ARCHITECTURES:
        metrics = [pair_metrics[f"{a}-{b}"] for a, b in pairs]
        max_error = max(item["closure_error"] for item in metrics)
        min_opposition_unit = min((item["opposition"] + 1) / 2 for item in metrics)
        min_balance = min(item["balance"] for item in metrics)
        quality = float((1 / (1 + max_error)) * min_opposition_unit * min_balance)
        architecture_metrics[architecture] = {
            "pairs": [f"{a}-{b}" for a, b in pairs],
            "max_closure_error": float(max_error),
            "min_opposition": float(min(item["opposition"] for item in metrics)),
            "min_balance": float(min_balance),
            "quality_q": quality,
        }

    ranked = sorted(
        architecture_metrics,
        key=lambda name: (-architecture_metrics[name]["quality_q"], name),
    )
    return {
        "centroids": centroids,
        "centre": centre,
        "radius": radius,
        "pairs": pair_metrics,
        "architectures": architecture_metrics,
        "ranking": ranked,
        "winner": ranked[0],
    }


def pair_holdout_metrics(
    development: np.ndarray,
    holdout: np.ndarray,
    child_a: str,
    child_b: str,
) -> dict:
    i = CHILDREN.index(child_a)
    j = CHILDREN.index(child_b)
    mu_dev_a = development[i].mean(axis=0)
    mu_dev_b = development[j].mean(axis=0)
    mu_hold_a = holdout[i].mean(axis=0)
    mu_hold_b = holdout[j].mean(axis=0)

    diameter_dev = (mu_dev_a - mu_dev_b) / 2
    diameter_hold = (mu_hold_a - mu_hold_b) / 2
    diameter_norm = float(np.linalg.norm(diameter_dev))
    if diameter_norm == 0:
        return {
            "persistence": 0.0,
            "balanced_accuracy": 0.5,
            "dprime": 0.0,
            "holdout_mean_a": 0.0,
            "holdout_mean_b": 0.0,
        }

    unit = diameter_dev / diameter_norm
    threshold = float(np.dot((mu_dev_a + mu_dev_b) / 2, unit))
    score_a = holdout[i] @ unit
    score_b = holdout[j] @ unit
    correct_a = float(np.mean(score_a >= threshold))
    correct_b = float(np.mean(score_b < threshold))
    balanced_accuracy = (correct_a + correct_b) / 2
    pooled_sd = float(np.sqrt((np.var(score_a, ddof=1) + np.var(score_b, ddof=1)) / 2))
    dprime = 0.0 if pooled_sd == 0 else float(abs(score_a.mean() - score_b.mean()) / pooled_sd)

    return {
        "persistence": abs(cosine(diameter_dev, diameter_hold)),
        "balanced_accuracy": balanced_accuracy,
        "dprime": dprime,
        "holdout_mean_a": float(score_a.mean()),
        "holdout_mean_b": float(score_b.mean()),
        "frozen_threshold": threshold,
    }


def evaluate(development: np.ndarray, holdout: np.ndarray) -> dict:
    dev_geometry = split_geometry(development)
    hold_geometry = split_geometry(holdout)
    selected = dev_geometry["winner"]
    selected_pairs = next(pairs for name, pairs in ARCHITECTURES if name == selected)

    hold_scores = hold_geometry["architectures"]
    hold_selected = hold_scores[selected]
    hold_runner = max(
        item["quality_q"] for name, item in hold_scores.items() if name != selected
    )
    selected_pair_metrics = {
        f"{a}-{b}": pair_holdout_metrics(development, holdout, a, b)
        for a, b in selected_pairs
    }

    gate_values = {
        "G1_same_winner": hold_geometry["winner"] == selected,
        "G2_holdout_q_at_least_0_70": hold_selected["quality_q"] >= 0.70,
        "G3_both_oppositions_at_least_0_80": hold_selected["min_opposition"] >= 0.80,
        "G4_both_balances_at_least_0_80": hold_selected["min_balance"] >= 0.80,
        "G5_both_persistences_at_least_0_80": min(
            item["persistence"] for item in selected_pair_metrics.values()
        )
        >= 0.80,
        "G6_both_balanced_accuracies_at_least_0_80": min(
            item["balanced_accuracy"] for item in selected_pair_metrics.values()
        )
        >= 0.80,
        "G7_holdout_margin_at_least_10_percent": hold_selected["quality_q"]
        >= 1.10 * hold_runner,
    }

    return {
        "development": dev_geometry,
        "holdout": hold_geometry,
        "selected_architecture": selected,
        "selected_pairs": [f"{a}-{b}" for a, b in selected_pairs],
        "selected_pair_holdout": selected_pair_metrics,
        "holdout_runner_up_q": float(hold_runner),
        "gates_1_to_7": gate_values,
        "passes_gates_1_to_7": all(gate_values.values()),
    }


def strip_arrays(value):
    if isinstance(value, dict):
        return {key: strip_arrays(item) for key, item in value.items() if key not in {"centroids", "centre"}}
    if isinstance(value, list):
        return [strip_arrays(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    return value


def balanced_shuffle(data: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    child_count, records, cuts = data.shape
    pooled = data.reshape(child_count * records, cuts)
    return pooled[rng.permutation(len(pooled))].reshape(child_count, records, cuts)


def pseudo_children(data: np.ndarray, source_index: int, rng: np.random.Generator) -> np.ndarray:
    records = data[source_index]
    if records.shape[0] % 4:
        raise RuntimeError("pseudo-child record count must divide by four")
    return records[rng.permutation(len(records))].reshape(4, records.shape[0] // 4, records.shape[1])


def leave_setting_out(
    development: np.ndarray,
    holdout: np.ndarray,
    cuts: list[str],
    selected_architecture: str,
) -> list[dict]:
    rows = []
    for setting in range(9):
        mask = np.array([not cut.startswith(f"K{setting}G") for cut in cuts])
        result = evaluate(development[:, :, mask], holdout[:, :, mask])
        rows.append(
            {
                "left_out": f"K{setting}",
                "development_winner": result["development"]["winner"],
                "holdout_winner": result["holdout"]["winner"],
                "same_as_full_selected": result["selected_architecture"] == selected_architecture,
                "selected_architecture": result["selected_architecture"],
                "holdout_q": result["holdout"]["architectures"][result["selected_architecture"]]["quality_q"],
                "passes_gates_1_to_7": result["passes_gates_1_to_7"],
            }
        )
    return rows


def write_pair_csv(result: dict) -> None:
    rows = []
    for split in ("development", "holdout"):
        geometry = result[split]
        for pair, metrics in geometry["pairs"].items():
            holdout_metrics = pair_holdout_metrics(
                ARRAYS["development"],
                ARRAYS["holdout"],
                *metrics["children"],
            )
            rows.append(
                {
                    "split": split,
                    "pair": pair,
                    **{key: value for key, value in metrics.items() if key != "children"},
                    **holdout_metrics,
                    "selected_pair": pair in result["selected_pairs"],
                }
            )
    pd.DataFrame(rows).to_csv(PAIR_CSV, index=False)


def write_architecture_csv(result: dict) -> None:
    rows = []
    for split in ("development", "holdout"):
        for name, metrics in result[split]["architectures"].items():
            rows.append(
                {
                    "split": split,
                    "architecture": name,
                    **{key: value for key, value in metrics.items() if key != "pairs"},
                    "pairs": " + ".join(metrics["pairs"]),
                    "rank": result[split]["ranking"].index(name) + 1,
                    "selected_on_development": name == result["selected_architecture"],
                }
            )
    pd.DataFrame(rows).to_csv(ARCH_CSV, index=False)


if __name__ == "__main__":
    source_hash = sha256(SOURCE)
    protocol_hash = sha256(PROTOCOL)
    if source_hash != EXPECTED_SOURCE_SHA256:
        raise RuntimeError(f"source hash mismatch: {source_hash}")
    if protocol_hash != EXPECTED_PROTOCOL_SHA256:
        raise RuntimeError(f"protocol hash mismatch: {protocol_hash}")

    ARRAYS, CUTS = load_arrays()
    observed = evaluate(ARRAYS["development"], ARRAYS["holdout"])

    rng = np.random.default_rng(SEED)
    controls = []
    shuffle_passes = 0
    for iteration in range(N_SHUFFLES):
        dev = balanced_shuffle(ARRAYS["development"], rng)
        hold = balanced_shuffle(ARRAYS["holdout"], rng)
        result = evaluate(dev, hold)
        passed = result["passes_gates_1_to_7"]
        shuffle_passes += int(passed)
        controls.append(
            {
                "control_type": "balanced_label_shuffle",
                "iteration": iteration,
                "source_child": "",
                "development_winner": result["development"]["winner"],
                "holdout_winner": result["holdout"]["winner"],
                "selected_holdout_q": result["holdout"]["architectures"][
                    result["selected_architecture"]
                ]["quality_q"],
                "passes_gates_1_to_7": passed,
            }
        )

    pseudo_passes = 0
    for iteration in range(N_PSEUDO):
        source_index = iteration % 4
        dev = pseudo_children(ARRAYS["development"], source_index, rng)
        hold = pseudo_children(ARRAYS["holdout"], source_index, rng)
        result = evaluate(dev, hold)
        passed = result["passes_gates_1_to_7"]
        pseudo_passes += int(passed)
        controls.append(
            {
                "control_type": "within_archive_pseudo_child",
                "iteration": iteration,
                "source_child": CHILDREN[source_index],
                "development_winner": result["development"]["winner"],
                "holdout_winner": result["holdout"]["winner"],
                "selected_holdout_q": result["holdout"]["architectures"][
                    result["selected_architecture"]
                ]["quality_q"],
                "passes_gates_1_to_7": passed,
            }
        )

    shuffle_rate = shuffle_passes / N_SHUFFLES
    pseudo_rate = pseudo_passes / N_PSEUDO
    gate_8 = shuffle_rate <= 0.01 and pseudo_rate <= 0.05
    verdict = (
        "SUPPORTED"
        if observed["passes_gates_1_to_7"] and gate_8
        else "NOT SUPPORTED"
    )

    leaveout = leave_setting_out(
        ARRAYS["development"],
        ARRAYS["holdout"],
        CUTS,
        observed["selected_architecture"],
    )

    write_pair_csv(observed)
    write_architecture_csv(observed)
    pd.DataFrame(controls).to_csv(CONTROL_CSV, index=False)
    pd.DataFrame(leaveout).to_csv(LEAVEOUT_CSV, index=False)

    output = {
        "claim_id": "Q17-CHILD-PAIR-v1",
        "seed": SEED,
        "source": SOURCE.name,
        "source_sha256": source_hash,
        "protocol": PROTOCOL.name,
        "protocol_sha256": protocol_hash,
        "children": list(CHILDREN),
        "cuts": CUTS,
        "observed": strip_arrays(observed),
        "controls": {
            "balanced_label_shuffles": N_SHUFFLES,
            "balanced_label_shuffle_passes": shuffle_passes,
            "balanced_label_shuffle_rate": shuffle_rate,
            "within_archive_pseudo_children": N_PSEUDO,
            "within_archive_pseudo_child_passes": pseudo_passes,
            "within_archive_pseudo_child_rate": pseudo_rate,
        },
        "gate_8_controls": gate_8,
        "all_gates": {
            **observed["gates_1_to_7"],
            "G8_control_rates": gate_8,
        },
        "verdict": verdict,
        "leave_setting_out": leaveout,
        "evidence_class": "exploratory same-deposit follow-up; independent replication required",
    }
    RESULTS.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print(json.dumps({
        "verdict": verdict,
        "selected_architecture": observed["selected_architecture"],
        "development_ranking": observed["development"]["ranking"],
        "holdout_ranking": observed["holdout"]["ranking"],
        "selected_holdout_q": observed["holdout"]["architectures"][
            observed["selected_architecture"]
        ]["quality_q"],
        "gates": output["all_gates"],
        "shuffle_rate": shuffle_rate,
        "pseudo_rate": pseudo_rate,
    }, indent=2))
