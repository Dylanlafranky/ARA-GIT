"""Post-seal evaluation of the PN3 standalone ARA target packet.

This script owns all established analytic prime references. It cannot create or
modify the standalone predictions; it first verifies the immutable packet hash,
then reads target outcomes and compares the frozen predictions.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN3_STANDALONE_ARA_PARENT_CHILD_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA256 = "DB6BE581908BA336A02F2481CEAB21FAACEF137F8773E9FC74CCF605E5E5A2EB"
TARGET_CONFIG = HERE / "PN3_TARGET_RUN_CONFIG_v1_FROZEN.json"
COMPARATOR_CONFIG = HERE / "PN3_COMPARATOR_RUN_CONFIG_v1_FROZEN.json"
PACKET_PATH = HERE / "PN3_STANDALONE_ARA_TARGET_PACKET.npz"
TARGET_SUMMARY_PATH = HERE / "PN3_STANDALONE_ARA_TARGET_SUMMARY.json"

RESULTS_PATH = HERE / "PN3_STANDALONE_ARA_RESULTS.json"
SCORES_PATH = HERE / "PN3_STANDALONE_ARA_MODEL_SCORES.csv"
BOOTSTRAP_PATH = HERE / "PN3_STANDALONE_ARA_BOOTSTRAP.csv"
BLOCK_PATH = HERE / "PN3_STANDALONE_ARA_BLOCK_CALIBRATION.csv"
GAP_PATH = HERE / "PN3_STANDALONE_ARA_GAP_CLASSES.csv"
MODEL_FIGURE = HERE / "PN3_STANDALONE_ARA_MODEL_COMPARISON.png"
PARENT_FIGURE = HERE / "PN3_STANDALONE_ARA_PARENT_RECOVERY.png"
BLOCK_FIGURE = HERE / "PN3_STANDALONE_ARA_BLOCK_CALIBRATION.png"

SIEVE_PRIMES = np.array([2, 3, 5, 7, 11, 13, 17, 19, 23, 29], dtype=np.int64)
W29 = float(np.prod(1.0 - 1.0 / SIEVE_PRIMES.astype(float)))
TWIN_PRIME_CONSTANT = 0.6601618158468696
EPS = 1e-9
BLOCKS = 40
BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_SEED = 20_260_717


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


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
    if isinstance(value, Path):
        return str(value)
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(json_ready(payload), indent=2) + "\n", encoding="utf-8")


def clip_probability(values: np.ndarray | float) -> np.ndarray:
    return np.clip(np.asarray(values, dtype=float), EPS, 1.0 - EPS)


def per_event_loss(labels: np.ndarray, probabilities: np.ndarray) -> np.ndarray:
    p = clip_probability(probabilities)
    return -(labels * np.log2(p) + (1 - labels) * np.log2(1.0 - p))


def simple_primes(limit: int) -> np.ndarray:
    sieve = np.ones(limit + 1, dtype=bool)
    sieve[:2] = False
    for p in range(2, int(math.isqrt(limit)) + 1):
        if sieve[p]:
            sieve[p * p :: p] = False
    return np.flatnonzero(sieve).astype(np.int64)


def prime_factors(number: int) -> list[int]:
    factors: list[int] = []
    remaining = int(number)
    for p in simple_primes(math.isqrt(remaining) + 1):
        p_int = int(p)
        if remaining % p_int == 0:
            factors.append(p_int)
            while remaining % p_int == 0:
                remaining //= p_int
        if p_int * p_int > remaining:
            break
    if remaining > 1:
        factors.append(remaining)
    return factors


def pnt29_probability(numbers: np.ndarray) -> np.ndarray:
    return clip_probability(1.0 / (np.log(numbers.astype(float)) * W29))


def hl29_multiplier(gap: int) -> float:
    singular = 2.0 * TWIN_PRIME_CONSTANT
    for factor in prime_factors(gap):
        if factor > 2:
            singular *= (factor - 1.0) / (factor - 2.0)
    pass_probability = 1.0
    for prime in SIEVE_PRIMES:
        q = int(prime)
        forbidden = 1 if gap % q == 0 else 2
        pass_probability *= 1.0 - forbidden / q
    return singular / pass_probability


def hl29_probability(numbers: np.ndarray, gaps: np.ndarray) -> np.ndarray:
    multipliers = {int(gap): hl29_multiplier(int(gap)) for gap in np.unique(gaps)}
    factors = np.array([multipliers[int(gap)] for gap in gaps], dtype=float)
    return clip_probability(
        factors / (np.log(numbers.astype(float)) * np.log((numbers + gaps).astype(float)))
    )


def validate_configs() -> tuple[dict[str, Any], dict[str, Any]]:
    if sha256_file(PROTOCOL) != PROTOCOL_SHA256:
        raise AssertionError("frozen protocol hash mismatch")
    target = json.loads(TARGET_CONFIG.read_text(encoding="utf-8"))
    comparator = json.loads(COMPARATOR_CONFIG.read_text(encoding="utf-8"))
    expected = {
        "test_id": "PN3/STANDALONE-ARA-PARENT-CHILD/v1",
        "protocol_sha256": PROTOCOL_SHA256,
        "packet_sha256": sha256_file(PACKET_PATH),
        "target_summary_sha256": sha256_file(TARGET_SUMMARY_PATH),
        "target_config_sha256": sha256_file(TARGET_CONFIG),
        "comparison_script_sha256": sha256_file(Path(__file__)),
    }
    for key, value in expected.items():
        if comparator.get(key) != value:
            raise AssertionError(f"comparator config mismatch for {key}: {comparator.get(key)!r} != {value!r}")
    return target, comparator


def score(task: str, model: str, labels: np.ndarray, predictions: np.ndarray) -> dict[str, Any]:
    losses = per_event_loss(labels, predictions)
    return {
        "task": task,
        "model": model,
        "events": int(len(labels)),
        "positives": int(np.sum(labels)),
        "actual_rate": float(np.mean(labels)),
        "mean_prediction": float(np.mean(predictions)),
        "calibration_error": float(np.mean(predictions) - np.mean(labels)),
        "log_loss_bits": float(np.mean(losses)),
        "brier_score": float(np.mean((predictions - labels) ** 2)),
    }


def block_indices(numbers: np.ndarray, low: int, high: int) -> np.ndarray:
    width = (high - low) / BLOCKS
    return np.minimum(((numbers - low) / width).astype(int), BLOCKS - 1)


def block_summary(
    task: str,
    numbers: np.ndarray,
    labels: np.ndarray,
    predictions: dict[str, np.ndarray],
    low: int,
    high: int,
) -> pd.DataFrame:
    blocks = block_indices(numbers, low, high)
    rows: list[dict[str, Any]] = []
    for block in range(BLOCKS):
        mask = blocks == block
        row: dict[str, Any] = {
            "task": task,
            "block": block,
            "low": int(low + block * (high - low) / BLOCKS),
            "high": int(low + (block + 1) * (high - low) / BLOCKS),
            "events": int(np.sum(mask)),
            "positives": int(np.sum(labels[mask])),
            "actual_rate": float(np.mean(labels[mask])),
        }
        for name, prediction in predictions.items():
            row[f"mean__{name}"] = float(np.mean(prediction[mask]))
            row[f"loss__{name}"] = float(np.mean(per_event_loss(labels[mask], prediction[mask])))
        rows.append(row)
    return pd.DataFrame(rows)


def block_bootstrap(
    blocks: pd.DataFrame,
    task: str,
    model: str,
    comparator: str,
    rng: np.random.Generator,
) -> dict[str, Any]:
    task_blocks = blocks[blocks["task"] == task].sort_values("block")
    model_losses = task_blocks[f"loss__{model}"].to_numpy(float)
    comparator_losses = task_blocks[f"loss__{comparator}"].to_numpy(float)
    weights = task_blocks["events"].to_numpy(float)
    observed = float(np.average(comparator_losses - model_losses, weights=weights))
    samples = rng.integers(0, len(task_blocks), size=(BOOTSTRAP_REPLICATES, len(task_blocks)))
    sampled_weights = weights[samples]
    sampled_delta = comparator_losses[samples] - model_losses[samples]
    distribution = np.sum(sampled_delta * sampled_weights, axis=1) / np.sum(sampled_weights, axis=1)
    return {
        "task": task,
        "model": model,
        "comparator": comparator,
        "observed_gain_bits": observed,
        "bootstrap_mean_gain_bits": float(np.mean(distribution)),
        "ci95_low_bits": float(np.quantile(distribution, 0.025)),
        "ci95_high_bits": float(np.quantile(distribution, 0.975)),
        "probability_gain_positive": float(np.mean(distribution > 0.0)),
        "replicates": BOOTSTRAP_REPLICATES,
        "blocks": BLOCKS,
        "seed": BOOTSTRAP_SEED,
    }


def gap_table(numbers: np.ndarray, labels: np.ndarray, gaps: np.ndarray, predictions: dict[str, np.ndarray]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for gap in np.unique(gaps):
        mask = gaps == gap
        row: dict[str, Any] = {
            "gap": int(gap),
            "events": int(np.sum(mask)),
            "positives": int(np.sum(labels[mask])),
            "actual_rate": float(np.mean(labels[mask])),
            "mean_number": float(np.mean(numbers[mask])),
        }
        for name, prediction in predictions.items():
            row[f"mean__{name}"] = float(np.mean(prediction[mask]))
        rows.append(row)
    return pd.DataFrame(rows)


def make_figures(
    scores: pd.DataFrame,
    blocks: pd.DataFrame,
    gaps: pd.DataFrame,
    results: dict[str, Any],
) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    colors = {"candidate": "#276FBF", "edge": "#D95D39"}

    selected = [
        ("candidate", "ara_parent_only"),
        ("candidate", "ara_parent_ara_i3_child"),
        ("candidate", "ara_parent_raw_stencil_child"),
        ("candidate", "pnt29_reference"),
        ("edge", "ara_parent_only"),
        ("edge", "ara_parent_ara_endpoints_child"),
        ("edge", "ara_parent_raw_edge_child"),
        ("edge", "hl29_reference"),
    ]
    selected_scores = pd.concat(
        [scores[(scores["task"] == task) & (scores["model"] == model)] for task, model in selected],
        ignore_index=True,
    )
    selected_scores["reference_loss"] = selected_scores["task"].map(
        scores[scores["model"].isin(["pnt29_reference", "hl29_reference"])].set_index("task")["log_loss_bits"]
    )
    selected_scores["gain_vs_reference"] = selected_scores["reference_loss"] - selected_scores["log_loss_bits"]
    labels = [
        "ARA parent\n(candidate)", "ARA I3\n(candidate)", "Raw stencil\n(candidate)", "PNT29\n(candidate)",
        "ARA parent\n(edge)", "ARA endpoints\n(edge)", "Raw edge\n(edge)", "HL29\n(edge)",
    ]
    fig, ax = plt.subplots(figsize=(12, 6.5))
    bar_colors = [colors[task] for task, _ in selected]
    ax.bar(np.arange(len(selected_scores)), selected_scores["gain_vs_reference"], color=bar_colors, alpha=0.88)
    ax.axhline(0.0, color="#222222", linewidth=1)
    ax.set_xticks(np.arange(len(labels)), labels, rotation=0)
    ax.set_ylabel("Log-loss gain vs established reference (bits/event)")
    ax.set_title("PN3 standalone ARA: absolute prediction comparison")
    ax.text(0.01, -0.18, "Positive means lower out-of-sample log loss than the task's established reference.", transform=ax.transAxes, fontsize=9)
    fig.tight_layout()
    fig.savefig(MODEL_FIGURE, dpi=180, bbox_inches="tight")
    plt.close(fig)

    parent = results["parent_recovery"]
    names = ["Actual", "ARA", "Home", "Raw additive", "3-rung log OLS", "ARA curvature"]
    candidate_values = [
        parent["candidate"]["actual_rate"], parent["candidate"]["ara"], parent["candidate"]["home"],
        parent["candidate"]["raw_additive"], parent["candidate"]["log_ols_3rung"], parent["candidate"]["ara_curvature"],
    ]
    edge_values = [
        parent["edge"]["actual_rate"], parent["edge"]["ara"], parent["edge"]["home"],
        parent["edge"]["raw_additive"], parent["edge"]["log_ols_3rung"], parent["edge"]["ara_curvature"],
    ]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.8))
    for ax, values, task in zip(axes, [candidate_values, edge_values], ["candidate", "edge"]):
        ax.bar(np.arange(len(names)), values, color=colors[task], alpha=0.88)
        ax.set_xticks(np.arange(len(names)), names, rotation=28, ha="right")
        ax.set_ylabel("Observed or predicted survival rate")
        ax.set_title(f"{task.capitalize()} parent-rung recovery")
        ax.set_ylim(min(values) * 0.97, max(values) * 1.01)
    fig.suptitle("Parent forecast from development rungs to the sealed R9 target")
    fig.tight_layout()
    fig.savefig(PARENT_FIGURE, dpi=180, bbox_inches="tight")
    plt.close(fig)

    candidate_blocks = blocks[blocks["task"] == "candidate"].sort_values("block")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(candidate_blocks["block"], candidate_blocks["actual_rate"], color="#222222", linewidth=1.4, label="Actual")
    ax.plot(candidate_blocks["block"], candidate_blocks["mean__ara_parent_ara_i3_child"], color=colors["candidate"], linewidth=1.5, label="ARA I3")
    ax.plot(candidate_blocks["block"], candidate_blocks["mean__pnt29_reference"], color="#777777", linewidth=1.2, label="PNT29")
    ax.set_xlabel("Target block (40 equal number-axis blocks)")
    ax.set_ylabel("Candidate prime-survival rate")
    ax.set_title("Candidate calibration across the untouched target interval")
    ax.legend()
    fig.tight_layout()
    fig.savefig(BLOCK_FIGURE, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    if any(path.exists() for path in (RESULTS_PATH, SCORES_PATH, BOOTSTRAP_PATH, BLOCK_PATH, GAP_PATH)):
        raise AssertionError("comparison artifacts already exist; refusing to overwrite frozen results")
    target_config, comparator_config = validate_configs()
    packet_hash_before = sha256_file(PACKET_PATH)
    archive = np.load(PACKET_PATH, allow_pickle=False)
    metadata = json.loads(str(archive["metadata_json"]))
    low = int(metadata["target_low"])
    high = int(metadata["target_high"])

    candidate_numbers = archive["candidate_numbers"].astype(np.int64)
    candidate_labels = archive["candidate_labels"].astype(np.uint8)
    edge_numbers = archive["edge_numbers"].astype(np.int64)
    edge_labels = archive["edge_labels"].astype(np.uint8)
    edge_gaps = archive["edge_gaps"].astype(np.int64)

    candidate_predictions = {
        name: archive[f"candidate_prediction__{name}"].astype(float)
        for name in metadata["candidate_models"]
    }
    edge_predictions = {
        name: archive[f"edge_prediction__{name}"].astype(float)
        for name in metadata["edge_models"]
    }
    candidate_predictions["pnt29_reference"] = pnt29_probability(candidate_numbers)
    edge_predictions["hl29_reference"] = hl29_probability(edge_numbers, edge_gaps)

    rows = [score("candidate", name, candidate_labels, prediction) for name, prediction in candidate_predictions.items()]
    rows.extend(score("edge", name, edge_labels, prediction) for name, prediction in edge_predictions.items())
    scores = pd.DataFrame(rows)
    reference_loss = {
        "candidate": float(scores[(scores["task"] == "candidate") & (scores["model"] == "pnt29_reference")]["log_loss_bits"].iloc[0]),
        "edge": float(scores[(scores["task"] == "edge") & (scores["model"] == "hl29_reference")]["log_loss_bits"].iloc[0]),
    }
    scores["gain_vs_established_reference_bits"] = scores.apply(
        lambda row: reference_loss[row["task"]] - row["log_loss_bits"], axis=1
    )
    scores.to_csv(SCORES_PATH, index=False)

    candidate_block_models = {
        "ara_parent_only": candidate_predictions["ara_parent_only"],
        "ara_parent_ara_i3_child": candidate_predictions["ara_parent_ara_i3_child"],
        "ara_parent_raw_stencil_child": candidate_predictions["ara_parent_raw_stencil_child"],
        "pnt29_reference": candidate_predictions["pnt29_reference"],
    }
    edge_block_models = {
        "ara_parent_only": edge_predictions["ara_parent_only"],
        "ara_parent_ara_endpoints_child": edge_predictions["ara_parent_ara_endpoints_child"],
        "ara_parent_raw_edge_child": edge_predictions["ara_parent_raw_edge_child"],
        "hl29_reference": edge_predictions["hl29_reference"],
    }
    blocks = pd.concat(
        [
            block_summary("candidate", candidate_numbers, candidate_labels, candidate_block_models, low, high),
            block_summary("edge", edge_numbers, edge_labels, edge_block_models, low, high),
        ],
        ignore_index=True,
    )
    blocks.to_csv(BLOCK_PATH, index=False)

    rng = np.random.default_rng(BOOTSTRAP_SEED)
    comparisons = [
        ("candidate", "ara_parent_ara_i3_child", "ara_parent_only"),
        ("candidate", "ara_parent_ara_i3_child", "ara_parent_raw_stencil_child"),
        ("candidate", "ara_parent_ara_i3_child", "pnt29_reference"),
        ("edge", "ara_parent_ara_endpoints_child", "ara_parent_only"),
        ("edge", "ara_parent_ara_endpoints_child", "ara_parent_raw_edge_child"),
        ("edge", "ara_parent_ara_endpoints_child", "hl29_reference"),
    ]
    bootstrap_rows = [block_bootstrap(blocks, task, model, comparator, rng) for task, model, comparator in comparisons]
    bootstrap = pd.DataFrame(bootstrap_rows)
    bootstrap.to_csv(BOOTSTRAP_PATH, index=False)

    gaps = gap_table(edge_numbers, edge_labels, edge_gaps, edge_block_models)
    gaps.to_csv(GAP_PATH, index=False)

    target_summary = json.loads(TARGET_SUMMARY_PATH.read_text(encoding="utf-8"))
    parent_recovery: dict[str, Any] = {}
    for task, labels, predictions, rate_key in (
        ("candidate", candidate_labels, candidate_predictions, "candidate_parent_predictions"),
        ("edge", edge_labels, edge_predictions, "edge_parent_predictions"),
    ):
        actual_rate = float(np.mean(labels))
        frozen_rates = target_summary[rate_key]
        ara_rate = float(frozen_rates["ara"])
        ara_loss = float(np.mean(per_event_loss(labels, np.full(len(labels), ara_rate))))
        home_loss = float(np.mean(per_event_loss(labels, np.full(len(labels), frozen_rates["home"]))))
        additive_loss = float(np.mean(per_event_loss(labels, np.full(len(labels), frozen_rates["raw_additive"]))))
        parent_recovery[task] = {
            "actual_rate": actual_rate,
            **{key: float(value) for key, value in frozen_rates.items()},
            "ara_relative_rate_error": abs(ara_rate - actual_rate) / actual_rate,
            "ara_log_loss_bits": ara_loss,
            "home_log_loss_bits": home_loss,
            "raw_additive_log_loss_bits": additive_loss,
            "passes_one_percent_rate_error": abs(ara_rate - actual_rate) / actual_rate <= 0.01,
            "passes_parent_control_losses": ara_loss <= home_loss and ara_loss <= additive_loss,
        }

    boot_lookup = {
        (row["task"], row["model"], row["comparator"]): row
        for row in bootstrap_rows
    }
    candidate_child_parent = boot_lookup[("candidate", "ara_parent_ara_i3_child", "ara_parent_only")]
    candidate_child_raw = boot_lookup[("candidate", "ara_parent_ara_i3_child", "ara_parent_raw_stencil_child")]
    candidate_full_reference = boot_lookup[("candidate", "ara_parent_ara_i3_child", "pnt29_reference")]
    edge_child_parent = boot_lookup[("edge", "ara_parent_ara_endpoints_child", "ara_parent_only")]
    edge_child_raw = boot_lookup[("edge", "ara_parent_ara_endpoints_child", "ara_parent_raw_edge_child")]
    edge_full_reference = boot_lookup[("edge", "ara_parent_ara_endpoints_child", "hl29_reference")]

    criteria = {
        "candidate_P1_parent_recovery": bool(
            parent_recovery["candidate"]["passes_one_percent_rate_error"]
            and parent_recovery["candidate"]["passes_parent_control_losses"]
        ),
        "edge_P1_parent_recovery": bool(
            parent_recovery["edge"]["passes_one_percent_rate_error"]
            and parent_recovery["edge"]["passes_parent_control_losses"]
        ),
        "candidate_P2_child_redistribution": bool(
            candidate_child_parent["ci95_low_bits"] > 0
            and candidate_child_raw["observed_gain_bits"] > 0
        ),
        "edge_P2_child_redistribution": bool(
            edge_child_parent["ci95_low_bits"] > 0
            and edge_child_raw["observed_gain_bits"] > 0
        ),
        "candidate_P3_full_standalone": bool(
            parent_recovery["candidate"]["passes_one_percent_rate_error"]
            and parent_recovery["candidate"]["passes_parent_control_losses"]
            and candidate_full_reference["ci95_low_bits"] > 0
        ),
        "edge_P3_full_standalone": bool(
            parent_recovery["edge"]["passes_one_percent_rate_error"]
            and parent_recovery["edge"]["passes_parent_control_losses"]
            and edge_full_reference["ci95_low_bits"] > 0
        ),
    }

    unique_multipliers = sorted({round(hl29_multiplier(int(gap)), 12) for gap in np.unique(edge_gaps)})
    packet_hash_after = sha256_file(PACKET_PATH)
    if packet_hash_after != packet_hash_before:
        raise AssertionError("standalone target packet changed during comparison")
    results = {
        "test_id": "PN3/STANDALONE-ARA-PARENT-CHILD/v1",
        "protocol_sha256": PROTOCOL_SHA256,
        "target_config": target_config,
        "comparator_config": comparator_config,
        "packet_sha256_before": packet_hash_before,
        "packet_sha256_after": packet_hash_after,
        "packet_immutable_during_comparison": True,
        "target_interval": [low, high],
        "candidate_events": int(len(candidate_labels)),
        "candidate_positives": int(np.sum(candidate_labels)),
        "candidate_actual_rate": float(np.mean(candidate_labels)),
        "edge_events": int(len(edge_labels)),
        "edge_positives": int(np.sum(edge_labels)),
        "edge_actual_rate": float(np.mean(edge_labels)),
        "parent_recovery": parent_recovery,
        "criteria": criteria,
        "bootstrap_primary_comparisons": bootstrap_rows,
        "established_reference_notes": {
            "p29_wheel_factor": W29,
            "conditional_hl_unique_multipliers_on_target": unique_multipliers,
            "conditional_hl_multiplier_constant_across_target_gap_classes": len(unique_multipliers) == 1,
        },
        "scores_csv": str(SCORES_PATH),
        "bootstrap_csv": str(BOOTSTRAP_PATH),
        "blocks_csv": str(BLOCK_PATH),
        "gap_classes_csv": str(GAP_PATH),
    }
    write_json(RESULTS_PATH, results)
    make_figures(scores, blocks, gaps, results)
    print(json.dumps(json_ready(results), indent=2))


if __name__ == "__main__":
    main()
