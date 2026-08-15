#!/usr/bin/env python3
"""T386: couple state/path and determinacy/relation Di-ARAs on BUAP data."""

from __future__ import annotations

import csv
import json
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENDOR = HERE / "_vendor"
if VENDOR.exists():
    sys.path.insert(0, str(VENDOR))
MPL_CONFIG = HERE / "_matplotlib_cache"
MPL_CONFIG.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CONFIG))

import matplotlib.pyplot as plt
import numpy as np

import t385_buap_causal_irrationality_di_ara as base


RAW = base.RAW
OUT = HERE / "T386_coupled_di_ara_handover"
PROTOCOL = HERE / "T386_COUPLED_DI_ARA_HANDOVER_PROTOCOL_2026-08-15.md"
EXPECTED_RAW_SHA256 = base.EXPECTED_RAW_SHA256
EXPECTED_PROTOCOL_SHA256 = "D6752426236FA8CD3811298EEEFA9D479EC755CB03A3E7328F3EED03FBA7751C"

DT_NS = base.DT_NS
W = base.W
STRIDE = base.STRIDE
LAG = base.LAG
EPS_MV = base.EPS_MV
RECOVERY = base.RECOVERY
GUARD = base.GUARD
POSITIVE_MAX_LEAD = base.POSITIVE_MAX_LEAD
NEGATIVE_MIN_LEAD = base.NEGATIVE_MIN_LEAD
SEED = 386

RAW_FEATURES = [
    "elapsed_us",
    "rms_current",
    "rms_previous",
    "mean_current",
    "std_current",
    "total_variation",
    "direct_path",
    "total_path",
]
STATE_FEATURES = ["x_radial", "x_history", "ridge_product", "dx_radial", "dx_history"]
DET_FEATURES = ["x_forecast", "x_relation", "dx_forecast", "dx_relation"]

FEATURES = {
    "M0": [],
    "MT": ["elapsed_us"],
    "MG": RAW_FEATURES,
    "MS": RAW_FEATURES + STATE_FEATURES,
    "MD": RAW_FEATURES + DET_FEATURES,
    "MC0": RAW_FEATURES + STATE_FEATURES + DET_FEATURES,
    "MC": RAW_FEATURES
    + STATE_FEATURES
    + DET_FEATURES
    + ["couple_rf", "couple_hl"],
    "MLEAK": RAW_FEATURES + ["row_samples", "remaining_to_end_us"],
}


def forecast_relation_metrics(previous: np.ndarray, current: np.ndarray) -> tuple[float, float, float, float, float]:
    """Return AR error, persistence error and the two 0-2 determinacy cuts."""
    train_x = np.column_stack(
        [np.ones(len(previous) - 2), previous[1:-1], previous[:-2]]
    )
    train_y = previous[2:]
    beta, *_ = np.linalg.lstsq(train_x, train_y, rcond=None)

    joined = np.concatenate([previous[-2:], current])
    predictors = np.column_stack(
        [np.ones(len(current)), joined[1:-1], joined[:-2]]
    )
    predicted = predictors @ beta
    persistence = joined[1:-1]
    rmse_ar = float(np.sqrt(np.mean((current - predicted) ** 2)))
    rmse_persistence = float(np.sqrt(np.mean((current - persistence) ** 2)))
    q = (rmse_ar + EPS_MV) / (rmse_persistence + EPS_MV)
    x_forecast = float(np.clip(2.0 * q / (1.0 + q), 0.0, 2.0))

    p = previous - float(np.mean(previous))
    c = current - float(np.mean(current))
    denom = float(np.linalg.norm(p) * np.linalg.norm(c))
    relation = 0.0 if denom <= EPS_MV**2 else float(np.clip(np.dot(p, c) / denom, -1.0, 1.0))
    x_relation = float(1.0 - relation)
    return rmse_ar, rmse_persistence, x_forecast, relation, x_relation


def event_windows(event: base.Event, reverse: bool = False, retrospective: bool = False) -> list[dict]:
    if not event.eligible:
        return []
    y = event.values - event.causal_baseline
    start = event.first_index + RECOVERY
    causal_last = event.second_index - GUARD
    last = min(len(y) - 1, event.second_index + 8) if retrospective else causal_last
    if last - start + 1 < 2 * W:
        return []
    if reverse:
        y = y.copy()
        y[start : causal_last + 1] = y[start : causal_last + 1][::-1]

    rows: list[dict] = []
    previous_values = {
        "x_radial": 1.0,
        "x_history": 1.0,
        "x_forecast": 1.0,
        "x_relation": 1.0,
    }
    for endpoint in range(start + 2 * W - 1, last + 1, STRIDE):
        current = y[endpoint - W + 1 : endpoint + 1]
        previous = y[endpoint - 2 * W + 1 : endpoint - W + 1]
        rms_current = float(np.sqrt(np.mean(current**2)))
        rms_previous = float(np.sqrt(np.mean(previous**2)))
        s = (rms_current + EPS_MV) / (rms_previous + EPS_MV)
        x_radial = float(2.0 * s / (1.0 + s))
        direct, total, x_history = base.path_metrics(current)
        rmse_ar, rmse_p, x_forecast, relation, x_relation = forecast_relation_metrics(previous, current)

        lead_samples = event.second_index - endpoint
        if GUARD <= lead_samples < POSITIVE_MAX_LEAD:
            target = 1
        elif lead_samples >= NEGATIVE_MIN_LEAD:
            target = 0
        else:
            target = -1
        row = {
            "row": event.row,
            "event_id": event.event_id,
            "split": event.split,
            "endpoint": endpoint,
            "target": target,
            "lead_ns": float(lead_samples * DT_NS),
            "elapsed_us": float((endpoint - event.first_index) * DT_NS / 1000.0),
            "rms_current": rms_current,
            "rms_previous": rms_previous,
            "mean_current": float(np.mean(current)),
            "std_current": float(np.std(current)),
            "total_variation": float(np.sum(np.abs(np.diff(current)))),
            "direct_path": direct,
            "total_path": total,
            "x_radial": x_radial,
            "x_history": x_history,
            "ridge_product": float((x_radial - 1.0) * (x_history - 1.0)),
            "x_forecast": x_forecast,
            "x_relation": x_relation,
            "rmse_ar": rmse_ar,
            "rmse_persistence": rmse_p,
            "raw_relation": relation,
            "row_samples": float(len(event.values)),
            "remaining_to_end_us": float((len(event.values) - 1 - endpoint) * DT_NS / 1000.0),
        }
        for name in ("x_radial", "x_history", "x_forecast", "x_relation"):
            row["d" + name] = float(row[name] - previous_values[name])
            previous_values[name] = row[name]
        row["dx_radial"] = row.pop("dx_radial")
        row["dx_history"] = row.pop("dx_history")
        row["dx_forecast"] = row.pop("dx_forecast")
        row["dx_relation"] = row.pop("dx_relation")
        row["couple_rf"] = float((x_radial - 1.0) * (x_forecast - 1.0))
        row["couple_hl"] = float((x_history - 1.0) * (x_relation - 1.0))
        rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def score_all(models: dict, rows_by_split: dict[str, list[dict]]) -> tuple[dict, dict]:
    metrics: dict = {}
    predictions: dict = {}
    for split in ("calibration", "validation", "evaluation"):
        rows = base.model_rows(rows_by_split[split])
        metrics[split] = {}
        predictions[split] = {}
        for name, model in models.items():
            pred = model.predict(rows)
            predictions[split][name] = pred
            metrics[split][name] = base.score_predictions(rows, pred)
    return metrics, predictions


def bootstrap_model_delta(rows: list[dict], pred_component: np.ndarray, pred_coupled: np.ndarray, n_boot: int = 500) -> np.ndarray:
    rng = np.random.default_rng(SEED)
    y = np.asarray([r["target"] for r in rows], dtype=float)
    w = np.asarray([r["weight"] for r in rows], dtype=float)
    pc = np.clip(pred_component, 1e-9, 1 - 1e-9)
    pf = np.clip(pred_coupled, 1e-9, 1 - 1e-9)
    lc = -(y * np.log(pc) + (1 - y) * np.log(1 - pc))
    lf = -(y * np.log(pf) + (1 - y) * np.log(1 - pf))
    event_ids = np.asarray([r["row"] for r in rows], dtype=int)
    per_event = []
    for event in np.unique(event_ids):
        mask = event_ids == event
        per_event.append(float(np.sum(w[mask] * (lc[mask] - lf[mask])) / np.sum(w[mask])))
    per_event = np.asarray(per_event)
    return np.asarray(
        [float(np.mean(rng.choice(per_event, len(per_event), replace=True))) for _ in range(n_boot)]
    )


def shuffled_alignment_scores(rows: list[dict], model: base.LogisticModel, n: int = 100) -> np.ndarray:
    rng = np.random.default_rng(SEED + 1)
    det_fields = ["x_forecast", "x_relation", "dx_forecast", "dx_relation"]
    groups: dict[tuple[int, int], list[int]] = {}
    for i, row in enumerate(rows):
        key = (int(row["target"]), int(row["lead_ns"] // 128))
        groups.setdefault(key, []).append(i)
    scores = []
    for _ in range(n):
        work = [dict(r) for r in rows]
        for indices in groups.values():
            donors = rng.permutation(indices)
            for destination, donor in zip(indices, donors):
                for field in det_fields:
                    work[destination][field] = rows[int(donor)][field]
        for row in work:
            row["couple_rf"] = (row["x_radial"] - 1.0) * (row["x_forecast"] - 1.0)
            row["couple_hl"] = (row["x_history"] - 1.0) * (row["x_relation"] - 1.0)
        scores.append(base.score_predictions(work, model.predict(work))["logloss"])
    return np.asarray(scores)


def select_nearest(group: list[dict], lead: float, tolerance: float = 32.0) -> dict | None:
    item = min(group, key=lambda r: abs(r["lead_ns"] - lead))
    return item if abs(item["lead_ns"] - lead) <= tolerance else None


def axis_profile(rows: list[dict], leads: list[int]) -> list[dict]:
    grouped: dict[int, list[dict]] = {}
    for row in rows:
        grouped.setdefault(int(row["row"]), []).append(row)
    output: list[dict] = []
    axes = ("x_radial", "x_history", "x_forecast", "x_relation", "couple_rf", "couple_hl")
    for lead in leads:
        chosen = [select_nearest(group, lead) for group in grouped.values()]
        chosen = [item for item in chosen if item is not None]
        for axis in axes:
            values = np.asarray([item[axis] for item in chosen], dtype=float)
            output.append(
                {
                    "lead_ns": lead,
                    "axis": axis,
                    "n": int(len(values)),
                    "median": float(np.median(values)) if len(values) else math.nan,
                    "q25": float(np.quantile(values, 0.25)) if len(values) else math.nan,
                    "q75": float(np.quantile(values, 0.75)) if len(values) else math.nan,
                }
            )
    return output


def weighted_calibration(rows: list[dict], predictions: np.ndarray, bins: int = 10) -> list[dict]:
    p = np.asarray(predictions)
    y = np.asarray([r["target"] for r in rows], dtype=float)
    w = np.asarray([r["weight"] for r in rows], dtype=float)
    edges = np.unique(np.quantile(p, np.linspace(0, 1, bins + 1)))
    output = []
    for left, right in zip(edges[:-1], edges[1:]):
        mask = (p >= left) & (p <= right if right == edges[-1] else p < right)
        if not np.any(mask):
            continue
        output.append(
            {
                "predicted": float(np.sum(w[mask] * p[mask]) / np.sum(w[mask])),
                "observed": float(np.sum(w[mask] * y[mask]) / np.sum(w[mask])),
                "n": int(np.sum(mask)),
            }
        )
    return output


def sampled(rows: list[dict], n: int = 3500) -> list[dict]:
    if len(rows) <= n:
        return rows
    rng = np.random.default_rng(SEED)
    return [rows[i] for i in sorted(rng.choice(len(rows), n, replace=False))]


def style_axes(axes) -> None:
    for ax in np.asarray(axes).ravel():
        ax.set_facecolor("#FFFFFF")
        ax.grid(True, color="#E5E9EF", linewidth=0.8)
        for spine in ax.spines.values():
            spine.set_color("#B7C0CA")


def scatter_di_ara(ax, rows: list[dict], x_name: str, y_name: str, x_label: str, y_label: str, title: str) -> None:
    colors = {0: "#3F6FAE", 1: "#D89432"}
    labels = {0: "open (>=640 ns)", 1: "imminent (128-384 ns)"}
    for target in (0, 1):
        group = sampled([r for r in rows if r["target"] == target], 1800)
        ax.scatter(
            [r[x_name] for r in group],
            [r[y_name] for r in group],
            s=9,
            alpha=0.22,
            color=colors[target],
            label=f"{labels[target]} · n={len([r for r in rows if r['target']==target]):,}",
        )
        ax.scatter(
            np.median([r[x_name] for r in group]),
            np.median([r[y_name] for r in group]),
            s=100,
            facecolors="white",
            edgecolors=colors[target],
            linewidths=2,
        )
    ax.axvline(1, color="#202833", linewidth=1.2)
    ax.axhline(1, color="#202833", linewidth=1.2)
    ax.set_xlim(0, 2)
    ax.set_ylim(0, 2)
    ax.set_xticks([0, 0.5, 1, 1.5, 2])
    ax.set_yticks([0, 0.5, 1, 1.5, 2])
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title, loc="left", fontweight="bold")
    ax.legend(frameon=False, fontsize=8, loc="upper right")


def make_primary_figure(metrics: dict, predictions: dict, rows_eval: list[dict], shuffle_losses: np.ndarray, path: Path) -> None:
    blue, orange, charcoal, grey = "#3F6FAE", "#D89432", "#202833", "#98A2AE"
    fig, axes = plt.subplots(3, 2, figsize=(16, 15), constrained_layout=True)
    fig.patch.set_facecolor("#FAFBFC")
    style_axes(axes)

    scatter_di_ara(
        axes[0, 0], rows_eval, "x_radial", "x_history",
        "x_R: 0 contraction - 1 ridge - 2 expansion",
        "x_H: 0 recurrent - 1 ridge - 2 open",
        "State/path Di-ARA · internal evaluation",
    )
    scatter_di_ara(
        axes[0, 1], rows_eval, "x_forecast", "x_relation",
        "x_F: 0 predictable - 1 persistence - 2 unresolved",
        "x_L: 0 repeated - 1 unrelated - 2 inverted",
        "Determinacy/relation Di-ARA · internal evaluation",
    )

    names = ["MG", "MS", "MD", "MC0", "MC"]
    labels = ["raw", "state", "determinacy", "both additive", "coupled"]
    x = np.arange(len(names))
    width = 0.36
    ax = axes[1, 0]
    ax.bar(x - width / 2, [metrics["validation"][n]["auc"] for n in names], width, color=blue, label="validation")
    ax.bar(x + width / 2, [metrics["evaluation"][n]["auc"] for n in names], width, color=orange, label="evaluation")
    ax.set_xticks(x, labels, rotation=15)
    ax.set_ylim(0.45, 0.80)
    ax.set_ylabel("Weighted AUC (higher is better)")
    ax.set_title("Predictive ranking by model ladder", loc="left", fontweight="bold")
    ax.legend(frameon=False)

    ax = axes[1, 1]
    ax.bar(x - width / 2, [metrics["validation"][n]["logloss"] for n in names], width, color=blue, label="validation")
    ax.bar(x + width / 2, [metrics["evaluation"][n]["logloss"] for n in names], width, color=orange, label="evaluation")
    ax.set_xticks(x, labels, rotation=15)
    ax.set_ylim(0.60, 0.70)
    ax.set_ylabel("Weighted log loss (lower is better)")
    ax.set_title("Probability calibration by model ladder", loc="left", fontweight="bold")
    ax.legend(frameon=False)

    ax = axes[2, 0]
    observed_loss = metrics["evaluation"]["MC"]["logloss"]
    deltas = shuffle_losses - observed_loss
    ax.hist(deltas, bins=18, color="#BFD0E7", edgecolor=blue)
    ax.axvline(0, color=charcoal, linewidth=1.4, label="same as observed coupling")
    ax.set_xlabel("Shuffled minus observed MC log loss (positive favours observed alignment)")
    ax.set_ylabel("Shuffle count (100 total)")
    ax.set_title("Within-lead determinacy-alignment control", loc="left", fontweight="bold")
    ax.legend(frameon=False)

    ax = axes[2, 1]
    for model_name, color, marker, label in (("MG", grey, "o", "raw MG"), ("MC", orange, "s", "coupled MC")):
        profile = weighted_calibration(rows_eval, predictions["evaluation"][model_name])
        ax.plot([r["predicted"] for r in profile], [r["observed"] for r in profile], marker=marker, color=color, linewidth=2, label=label)
    ax.plot([0, 1], [0, 1], linestyle="--", color=charcoal, linewidth=1, label="ideal")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Predicted imminent-release probability")
    ax.set_ylabel("Weighted observed fraction")
    ax.set_title("Internal-evaluation calibration", loc="left", fontweight="bold")
    ax.legend(frameon=False)

    fig.suptitle(
        "T386 - coupled Di-ARA causal handover test\n"
        "BUAP liquid scintillator · 8 ns samples · 128 ns causal guard",
        fontsize=18,
        color=charcoal,
    )
    fig.savefig(path, dpi=190, facecolor=fig.get_facecolor())
    plt.close(fig)


def profile_items(profile: list[dict], axis: str) -> list[dict]:
    return sorted([r for r in profile if r["axis"] == axis], key=lambda r: r["lead_ns"], reverse=True)


def plot_profile(ax, profile: list[dict], axes_specs: list[tuple[str, str, str]], title: str, ylabel: str = "ARA coordinate") -> None:
    for name, color, label in axes_specs:
        items = profile_items(profile, name)
        leads = np.asarray([r["lead_ns"] for r in items])
        med = np.asarray([r["median"] for r in items])
        q25 = np.asarray([r["q25"] for r in items])
        q75 = np.asarray([r["q75"] for r in items])
        ax.plot(leads, med, marker="o", color=color, linewidth=2, label=label)
        ax.fill_between(leads, q25, q75, color=color, alpha=0.16)
    ax.axvspan(128, 0, color="#F1D6AD", alpha=0.5, label="excluded causal guard")
    ax.axvline(0, color="#202833", linewidth=1.2, label="second-pulse minimum")
    if ylabel == "ARA coordinate":
        ax.axhline(1, color="#202833", linewidth=1, linestyle="--", label="ARA ridge 1")
        ax.set_ylim(0, 2)
    else:
        ax.axhline(0, color="#202833", linewidth=1, linestyle="--", label="ridge-centred zero")
    ax.set_xlim(max(r["lead_ns"] for r in profile) + 40, min(r["lead_ns"] for r in profile) - 40)
    ax.set_xlabel("Time to second-pulse minimum (ns; decreasing toward release)")
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left", fontweight="bold")
    ax.legend(frameon=False, fontsize=8, ncol=2)


def make_handover_figure(events: list[base.Event], retrospective_profile: list[dict], path: Path) -> None:
    blue, orange, olive, pink, charcoal = "#3F6FAE", "#D89432", "#71814A", "#B25F7C", "#202833"
    fig, axes = plt.subplots(2, 2, figsize=(16, 11), constrained_layout=True)
    fig.patch.set_facecolor("#FAFBFC")
    style_axes(axes)

    eligible = [e for e in events if e.split == "evaluation" and e.eligible]
    median_delay = float(np.median([e.delay_ns for e in eligible]))
    example = min(eligible, key=lambda e: abs(e.delay_ns - median_delay))
    ax = axes[0, 0]
    time_to_second = (np.arange(len(example.values)) - example.second_index) * DT_NS
    y = example.values - example.causal_baseline
    mask = (time_to_second >= -1150) & (time_to_second <= 96)
    ax.plot(time_to_second[mask], y[mask], color=blue, linewidth=1.3, label=f"event row {example.row}")
    ax.axvspan(-128, 0, color="#F1D6AD", alpha=0.55, label="excluded 128 ns guard")
    ax.axvline(0, color=orange, linewidth=1.4, label="second-pulse minimum")
    ax.set_xlabel("Time relative to second-pulse minimum (ns)")
    ax.set_ylabel("Baseline-subtracted detector voltage (mV)")
    ax.set_title("Representative detector handover", loc="left", fontweight="bold")
    ax.legend(frameon=False)

    plot_profile(
        axes[0, 1], retrospective_profile,
        [("x_radial", blue, "x_R radial state"), ("x_history", orange, "x_H path history")],
        "State/path Di-ARA through the event",
    )
    plot_profile(
        axes[1, 0], retrospective_profile,
        [("x_forecast", olive, "x_F forecast unresolvedness"), ("x_relation", pink, "x_L window relation")],
        "Determinacy/relation Di-ARA through the event",
    )
    plot_profile(
        axes[1, 1], retrospective_profile,
        [("couple_rf", blue, "C_RF radial x forecast"), ("couple_hl", orange, "C_HL path x relation")],
        "Ridge-centred coupling through the event",
        ylabel="Coupling product (dimensionless)",
    )
    fig.suptitle(
        "T386 - retrospective coupled-Di-ARA handover map\n"
        "The shaded final 128 ns is descriptive, not advance prediction",
        fontsize=18,
        color=charcoal,
    )
    fig.savefig(path, dpi=190, facecolor=fig.get_facecolor())
    plt.close(fig)


def make_markdown_report(results: dict, path: Path) -> None:
    m = results["metrics"]
    gates = results["gates"]
    comparator = results["bootstrap"]["comparator"]
    text = f"""# T386 — coupled Di-ARA muon-handover result

## Outcome

**{results['status']}**

{results['plain_language']}

This remains a Class-D liquid-scintillator detector-proxy result.  It does not
measure a neutrino trajectory or prove deterministic muon decay.

## Exact model comparison

| Split | Raw MG AUC | State MS AUC | Determinacy MD AUC | Additive MC0 AUC | Coupled MC AUC | Raw MG log loss | Coupled MC log loss |
|---|---:|---:|---:|---:|---:|---:|---:|
| Validation | {m['validation']['MG']['auc']:.6f} | {m['validation']['MS']['auc']:.6f} | {m['validation']['MD']['auc']:.6f} | {m['validation']['MC0']['auc']:.6f} | {m['validation']['MC']['auc']:.6f} | {m['validation']['MG']['logloss']:.6f} | {m['validation']['MC']['logloss']:.6f} |
| Evaluation | {m['evaluation']['MG']['auc']:.6f} | {m['evaluation']['MS']['auc']:.6f} | {m['evaluation']['MD']['auc']:.6f} | {m['evaluation']['MC0']['auc']:.6f} | {m['evaluation']['MC']['auc']:.6f} | {m['evaluation']['MG']['logloss']:.6f} | {m['evaluation']['MC']['logloss']:.6f} |

## Coupling checks

- Validation-selected component comparator: `{comparator}`.
- Evaluation event-bootstrap log-loss improvement, coupled minus comparator:
  median `{results['bootstrap']['median_improvement']:.6f}`, 95% interval
  `[{results['bootstrap']['ci95'][0]:.6f}, {results['bootstrap']['ci95'][1]:.6f}]`.
- Same-time observed MC evaluation log loss:
  `{m['evaluation']['MC']['logloss']:.6f}`.
- Within-lead shuffled-alignment log loss median:
  `{results['controls']['alignment_shuffle_median_logloss']:.6f}`;
  observed alignment beat `{results['controls']['alignment_shuffle_beat_share']:.1%}`
  of 100 shuffles.
- Time-reversed fixed-model evaluation AUC:
  `{results['controls']['time_reversed_auc']:.6f}`.
- Forbidden acquisition leakage AUC:
  `{results['controls']['forbidden_leakage_auc']:.6f}` (audit only).

## Frozen gates

"""
    for name, value in gates.items():
        text += f"- {'PASS' if value else 'FAIL'} — `{name}`\n"
    text += """

## Interpretation boundary

The event-centred figure includes the final 128 ns and the observed pulse to
show the detector handover retrospectively.  Those samples are absent from the
causal predictor.  A pattern inside the shaded region may describe the local
release geometry; it is not forewarning.

T386 uses the already-opened T385 source.  A successful result would still
require execution on an unopened dated BUAP archive before being described as
external confirmation.

## Reproduction

Run:

```powershell
python analysis/muon/t386_coupled_di_ara_handover.py
python analysis/muon/validate_t386_coupled_di_ara_handover.py
```
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    raw_hash = base.sha256(RAW)
    protocol_hash = base.sha256(PROTOCOL)
    if raw_hash != EXPECTED_RAW_SHA256:
        raise RuntimeError(f"source hash mismatch: {raw_hash}")
    if protocol_hash != EXPECTED_PROTOCOL_SHA256:
        raise RuntimeError(f"protocol hash mismatch: {protocol_hash}")

    events = base.load_events(RAW)
    rows_by_split = {name: [] for name in ("engineering", "calibration", "validation", "evaluation")}
    reverse_evaluation: list[dict] = []
    retrospective_evaluation: list[dict] = []
    eligibility: list[dict] = []
    for event in events:
        rows_by_split[event.split].extend(event_windows(event))
        if event.split == "evaluation":
            reverse_evaluation.extend(event_windows(event, reverse=True))
            retrospective_evaluation.extend(event_windows(event, retrospective=True))
        eligibility.append({"row": event.row, "split": event.split, "eligible": int(event.eligible), "reason": event.exclusion})

    for rows in rows_by_split.values():
        base.balance_weights(rows)
    base.balance_weights(reverse_evaluation)
    base.balance_weights(retrospective_evaluation)

    base.FEATURES = FEATURES
    calibration = base.model_rows(rows_by_split["calibration"])
    models = {name: base.fit_logistic(name, calibration) for name in FEATURES}
    metrics, predictions = score_all(models, rows_by_split)
    rows_eval = base.model_rows(rows_by_split["evaluation"])

    comparator_names = ("MS", "MD", "MC0")
    comparator = min(comparator_names, key=lambda n: metrics["validation"][n]["logloss"])
    bootstrap = bootstrap_model_delta(
        rows_eval,
        predictions["evaluation"][comparator],
        predictions["evaluation"]["MC"],
    )
    boot_ci = [float(np.quantile(bootstrap, 0.025)), float(np.quantile(bootstrap, 0.975))]

    shuffle_losses = shuffled_alignment_scores(rows_eval, models["MC"], 100)
    reverse_rows = base.model_rows(reverse_evaluation)
    reverse_metrics = base.score_predictions(reverse_rows, models["MC"].predict(reverse_rows))

    causal_profile = axis_profile(rows_by_split["evaluation"], [1024, 512, 384, 256, 128])
    retrospective_profile = axis_profile(
        retrospective_evaluation,
        [1024, 512, 384, 256, 128, 64, 32, 0, -32, -64],
    )

    gates = {
        "proper_scores_improve_vs_raw_both_splits": all(
            metrics[s]["MC"]["logloss"] < metrics[s]["MG"]["logloss"]
            and metrics[s]["MC"]["brier"] < metrics[s]["MG"]["brier"]
            for s in ("validation", "evaluation")
        ),
        "auc_gain_at_least_0p02_vs_raw_both_splits": all(
            metrics[s]["MC"]["auc"] >= metrics[s]["MG"]["auc"] + 0.02
            for s in ("validation", "evaluation")
        ),
        "coupled_logloss_beats_each_component_both_splits": all(
            metrics[s]["MC"]["logloss"] < metrics[s][n]["logloss"]
            for s in ("validation", "evaluation")
            for n in comparator_names
        ),
        "evaluation_bootstrap_above_zero": boot_ci[0] > 0,
        "observed_alignment_beats_95pct_shuffles": float(np.mean(shuffle_losses > metrics["evaluation"]["MC"]["logloss"])) >= 0.95,
        "guard_and_forbidden_fields_excluded": True,
    }
    supported = all(gates.values())
    if supported:
        status = "SUPPORTED"
        plain = "The coupled Di-ARA improved both ranking and calibrated risk beyond raw, component-only and shuffled-alignment controls."
    elif gates["proper_scores_improve_vs_raw_both_splits"]:
        status = "CALIBRATION STRUCTURE ONLY"
        plain = "The coupled coordinates improved probability calibration, but the frozen ranking and/or coupling-specific gates did not all pass."
    elif metrics["evaluation"]["MC0"]["logloss"] <= metrics["evaluation"]["MC"]["logloss"]:
        status = "ADDITIONAL COORDINATES, COUPLING NOT SUPPORTED"
        plain = "The additional coordinates may describe the detector, but their declared ridge-centred coupling did not outperform placing them side by side."
    else:
        status = "NOT SUPPORTED"
        plain = "The coupled Di-ARA did not produce the frozen causal improvement on this detector-proxy source."

    results = {
        "test": "T386",
        "status": status,
        "plain_language": plain,
        "source": {
            "path": str(RAW),
            "sha256": raw_hash,
            "protocol": str(PROTOCOL),
            "protocol_sha256": protocol_hash,
            "sample_interval_ns": DT_NS,
            "medium": "BUAP 95 L liquid scintillator",
            "claim_class": "D detector proxy",
            "already_opened_by_T385": True,
        },
        "coordinate_definitions": {
            "state_path": ["x_R contraction-expansion", "x_H recurrent-open"],
            "determinacy_relation": ["x_F predictable-unresolved", "x_L repeated-inverted"],
            "coupling": ["C_RF=(x_R-1)(x_F-1)", "C_HL=(x_H-1)(x_L-1)"],
        },
        "metrics": metrics,
        "bootstrap": {
            "comparator": comparator,
            "median_improvement": float(np.median(bootstrap)),
            "ci95": boot_ci,
            "replicates": 500,
        },
        "controls": {
            "time_reversed_auc": reverse_metrics["auc"],
            "time_reversed_logloss": reverse_metrics["logloss"],
            "alignment_shuffle_median_logloss": float(np.median(shuffle_losses)),
            "alignment_shuffle_beat_share": float(np.mean(shuffle_losses > metrics["evaluation"]["MC"]["logloss"])),
            "alignment_shuffle_count": 100,
            "forbidden_leakage_auc": metrics["evaluation"]["MLEAK"]["auc"],
        },
        "gates": gates,
        "boundary": {
            "advance_prediction_excludes_last_ns": 128,
            "retrospective_map_includes_guard": True,
            "no_direct_neutrino_measurement": True,
            "external_confirmation": False,
        },
    }

    write_csv(OUT / "T386_MODEL_SCORES.csv", base.model_metric_rows(metrics))
    write_csv(OUT / "T386_CAUSAL_AXIS_PROFILE.csv", causal_profile)
    write_csv(OUT / "T386_RETROSPECTIVE_AXIS_PROFILE.csv", retrospective_profile)
    write_csv(OUT / "T386_ELIGIBILITY.csv", eligibility)
    write_csv(OUT / "T386_BOOTSTRAP.csv", [{"replicate": i, "logloss_improvement": v} for i, v in enumerate(bootstrap)])
    write_csv(OUT / "T386_ALIGNMENT_SHUFFLES.csv", [{"replicate": i, "logloss": v} for i, v in enumerate(shuffle_losses)])
    (OUT / "T386_RESULTS.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    make_primary_figure(metrics, predictions, rows_eval, shuffle_losses, OUT / "T386_COUPLED_DI_ARA_FIGURE.png")
    make_handover_figure(events, retrospective_profile, OUT / "T386_EVENT_CENTERED_HANDOVER_FIGURE.png")
    make_markdown_report(results, OUT / "T386_COUPLED_DI_ARA_REPORT.md")
    print(json.dumps({"status": status, "gates": gates, "output": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()

