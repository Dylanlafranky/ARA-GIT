#!/usr/bin/env python3
"""T355: frozen relational parent-ridge test under non-mirrored child histories."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import matplotlib

HERE = Path(__file__).resolve().parent
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from t354_irrationality_parent_ridge_centre import estimate_ridge


PREFIX = "T355_IRRATIONALITY_RELATIONAL_PARENT_RIDGE"
PROTOCOL = HERE / f"{PREFIX}_PROTOCOL_v1_FROZEN.md"
LENGTH = 4096
WINDOWS = (128, 256, 384, 512)
Q_VALUES = (19, 29, 31)
D_VALUES = (59, 61, 67)
DURATIONS = (288, 480, 672)
REPLICATES = 8
BOOTSTRAPS = 5000
SEED = 35520260811


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest().upper()


def stable_seed(*parts: object) -> int:
    payload = "|".join(map(str, (SEED,) + parts)).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "little")


def coprime_numerator(q: int, replicate: int) -> int:
    values = [p for p in range(1, q) if math.gcd(p, q) == 1]
    return values[(replicate * 3 + 2) % len(values)]


def centre_values() -> np.ndarray:
    count = len(Q_VALUES) * len(DURATIONS) * REPLICATES
    return np.rint(np.linspace(1376, 2720, count)).astype(int)


def identity_centre(pair_index: int, duration_index: int, replicate: int) -> int:
    index = (pair_index * len(DURATIONS) + duration_index) * REPLICATES + replicate
    return int(centre_values()[index])


def transition_mix(
    centre: int,
    duration: int,
    condition: str,
    direction: str,
) -> np.ndarray:
    time = np.arange(LENGTH - 1, dtype=float)
    if condition == "clean":
        left = duration // 2
        right = duration - left
        gamma_left = 1.0
        gamma_right = 1.0
    elif direction == "irrational_to_rational":
        left = int(round(0.35 * duration))
        right = duration - left
        gamma_left = 0.68
        gamma_right = 1.62
    else:
        left = int(round(0.62 * duration))
        right = duration - left
        gamma_left = 1.48
        gamma_right = 0.74

    start = centre - left
    end = centre + right
    mix = np.zeros(LENGTH - 1, dtype=float)
    mix[time >= end] = 1.0
    before = (time >= start) & (time < centre)
    after = (time >= centre) & (time < end)
    if left > 0:
        u = (time[before] - start) / left
        mix[before] = 0.5 * np.power(np.clip(u, 0.0, 1.0), gamma_left)
    if right > 0:
        v = (time[after] - centre) / right
        mix[after] = 0.5 + 0.5 * (1.0 - np.power(1.0 - np.clip(v, 0.0, 1.0), gamma_right))
    return mix


def make_child(
    q: int,
    d: int,
    duration: int,
    replicate: int,
    centre: int,
    condition: str,
    direction: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, float]:
    rational = coprime_numerator(q, replicate) / q
    irrational = math.sqrt(d) - math.floor(math.sqrt(d))
    source, target = (
        (irrational, rational)
        if direction == "irrational_to_rational"
        else (rational, irrational)
    )
    mix = transition_mix(centre, duration, condition, direction)
    advances = source + mix * (target - source)

    if condition == "asymmetric":
        direction_index = 0 if direction == "irrational_to_rational" else 1
        amplitude_fraction = (0.040, 0.065)[direction_index]
        period = (37 + 2 * replicate, 53 + 3 * replicate)[direction_index]
        rng = np.random.default_rng(
            stable_seed("child-wave", q, d, duration, replicate, direction)
        )
        child_phase = float(rng.uniform(0.0, 2.0 * np.pi))
        time = np.arange(LENGTH - 1, dtype=float)
        envelope = 4.0 * mix * (1.0 - mix)
        child = np.sin(2.0 * np.pi * time / period + child_phase)
        child += 0.35 * np.sin(4.0 * np.pi * time / period + 0.7 * child_phase)
        advances = advances + amplitude_fraction * abs(target - source) * envelope * child

    rng = np.random.default_rng(
        stable_seed("initial-phase", q, d, duration, replicate, condition, direction)
    )
    phase = float(rng.random())
    path = np.empty(LENGTH, dtype=float)
    path[0] = phase
    path[1:] = (phase + np.cumsum(advances)) % 1.0
    return path, mix, advances, rational, irrational


def bootstrap_median(values: np.ndarray, offset: int) -> dict[str, float | int]:
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(SEED + offset)
    draws = rng.integers(0, len(values), size=(BOOTSTRAPS, len(values)))
    sampled = np.median(values[draws], axis=1)
    return {
        "estimate": float(np.median(values)),
        "ci_low": float(np.quantile(sampled, 0.025)),
        "ci_high": float(np.quantile(sampled, 0.975)),
        "n": int(len(values)),
    }


def make_wrong_pairs(pairs: pd.DataFrame) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    for (_, _), group in pairs.groupby(["condition", "window"], sort=True):
        part = group.sort_values(["true_center", "pair_id"]).copy()
        shift = max(1, len(part) // 2)
        part["wrong_reverse_ridge"] = np.roll(part["rational_to_irrational"].to_numpy(float), shift)
        part["wrong_pair_parent"] = (part["irrational_to_rational"] + part["wrong_reverse_ridge"]) / 2.0
        part["wrong_pair_abs_error"] = np.abs(part.wrong_pair_parent - part.true_center)
        rows.append(part)
    return pd.concat(rows, ignore_index=True)


def make_figure(
    audit: pd.DataFrame,
    pairs: pd.DataFrame,
    identities: pd.DataFrame,
    gates: pd.DataFrame,
    output: Path,
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=True)

    ax = axes[0, 0]
    x = np.arange(2)
    mix_values = [float(audit[audit.condition == c].mix_rms.median()) for c in ("clean", "asymmetric")]
    advance_values = [float(audit[audit.condition == c].advance_complement_rms.median()) for c in ("clean", "asymmetric")]
    ax.bar(x - 0.18, mix_values, width=0.36, color="#2F6FB0", label="mix-profile mismatch")
    ax.bar(x + 0.18, advance_values, width=0.36, color="#D49A2E", label="advance-complement residual")
    ax.set_xticks(x, ["clean", "asymmetric"])
    ax.set(ylabel="normalized RMS", title="The primary condition is deliberately non-mirrored")
    ax.legend(frameon=False, fontsize=8)

    ax = axes[0, 1]
    example = pairs[(pairs.condition == "asymmetric") & (pairs.window == 512)]
    ax.scatter(example.true_center, example.irrational_to_rational, s=20, alpha=0.50, label="irrational to rational")
    ax.scatter(example.true_center, example.rational_to_irrational, s=20, alpha=0.50, label="rational to irrational")
    ax.scatter(example.true_center, example.parent_ridge, s=22, color="#222222", label="paired parent")
    limits = (1300, 2800)
    ax.plot(limits, limits, color="#7A8490", lw=1, linestyle=":")
    ax.set(
        xlim=limits,
        ylim=limits,
        xlabel="hidden parent seam (states)",
        ylabel="predicted centre (states)",
        title="Non-mirrored children and their relational midpoint",
    )
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 0]
    colors = {"clean": "#2F6FB0", "asymmetric": "#C45A86"}
    for condition, color in colors.items():
        part = pairs[pairs.condition == condition]
        curve = part.groupby("window", as_index=False).agg(
            forward=("forward_error", "median"),
            reverse=("reverse_error", "median"),
            parent=("parent_error", "median"),
        )
        ax.plot(curve.window, curve.forward, "--", marker="o", color=color, alpha=0.65, label=f"{condition}: forward")
        ax.plot(curve.window, curve.reverse, ":", marker="s", color=color, alpha=0.65, label=f"{condition}: reverse")
        ax.plot(curve.window, curve.parent, "-", marker="D", color=color, lw=2, label=f"{condition}: paired")
    ax.axhline(0, color="#7A8490", lw=1)
    ax.set(
        xlabel="observation window W (states)",
        ylabel="median centre error (states)",
        title="Observer-width response of children versus parent relation",
    )
    ax.legend(frameon=False, fontsize=8, ncol=2)

    ax = axes[1, 1]
    labels = ["clean", "asymmetric"]
    paired_error = [float(identities[identities.condition == c].paired_abs_error_median.median()) for c in labels]
    single_error = [float(identities[identities.condition == c].better_single_error_median.median()) for c in labels]
    wrong_error = [float(identities[identities.condition == c].wrong_pair_abs_error_median.median()) for c in labels]
    x = np.arange(2)
    ax.bar(x - 0.25, paired_error, width=0.25, color="#2F6FB0", label="true pair")
    ax.bar(x, single_error, width=0.25, color="#D49A2E", label="better child")
    ax.bar(x + 0.25, wrong_error, width=0.25, color="#AAB2BC", label="wrong pair")
    ax.set_xticks(x, labels)
    ax.set(ylabel="median absolute error (states)", title="Relational specificity controls")
    ax.legend(frameon=False, fontsize=8)

    verdict = str(gates.attrs.get("verdict", ""))
    passed = int(gates.passed.sum())
    short_verdict = "SUPPORTED (synthetic)" if verdict.startswith("SUPPORTED") else verdict
    fig.suptitle(
        f"T355 - Relational parent-ridge test | {passed}/6 gates | {short_verdict}",
        fontsize=16,
        fontweight="bold",
    )
    fig.savefig(output, dpi=170)
    plt.close(fig)


def main() -> None:
    child_rows: list[dict] = []
    audit_rows: list[dict] = []
    for pair_index, (q, d) in enumerate(zip(Q_VALUES, D_VALUES)):
        for duration_index, duration in enumerate(DURATIONS):
            for replicate in range(REPLICATES):
                true_center = identity_centre(pair_index, duration_index, replicate)
                pair_id = f"q{q}:d{d}:t{duration}:r{replicate}"
                for condition in ("clean", "asymmetric"):
                    generated = {}
                    for direction in ("irrational_to_rational", "rational_to_irrational"):
                        generated[direction] = make_child(
                            q, d, duration, replicate, true_center, condition, direction
                        )
                    forward_path, forward_mix, forward_advances, rational, irrational = generated["irrational_to_rational"]
                    reverse_path, reverse_mix, reverse_advances, _, _ = generated["rational_to_irrational"]
                    union = ((forward_mix > 0) & (forward_mix < 1)) | ((reverse_mix > 0) & (reverse_mix < 1))
                    gap = max(abs(irrational - rational), 1e-12)
                    mix_rms = float(np.sqrt(np.mean((forward_mix[union] - reverse_mix[union]) ** 2)))
                    complement = (forward_advances + reverse_advances) - (irrational + rational)
                    advance_rms = float(np.sqrt(np.mean((complement[union] / gap) ** 2)))
                    audit_rows.append(
                        {
                            "pair_id": pair_id,
                            "q": q,
                            "d": d,
                            "duration": duration,
                            "replicate": replicate,
                            "condition": condition,
                            "true_center": true_center,
                            "mix_rms": mix_rms,
                            "advance_complement_rms": advance_rms,
                        }
                    )
                    for direction, generated_tuple in generated.items():
                        path = generated_tuple[0]
                        for window in WINDOWS:
                            summary, _ = estimate_ridge(path, window)
                            predicted = float(summary["predicted_ridge"])
                            child_rows.append(
                                {
                                    "pair_id": pair_id,
                                    "q": q,
                                    "d": d,
                                    "duration": duration,
                                    "replicate": replicate,
                                    "condition": condition,
                                    "direction": direction,
                                    "window": window,
                                    "true_center": true_center,
                                    **summary,
                                    "signed_error": predicted - true_center,
                                    "abs_error": abs(predicted - true_center),
                                }
                            )

    children = pd.DataFrame(child_rows)
    audit = pd.DataFrame(audit_rows)
    pair_keys = ["pair_id", "q", "d", "duration", "replicate", "condition", "window", "true_center"]
    pairs = children.pivot(index=pair_keys, columns="direction", values="predicted_ridge").reset_index()
    pairs["parent_ridge"] = (pairs.irrational_to_rational + pairs.rational_to_irrational) / 2.0
    pairs["forward_error"] = pairs.irrational_to_rational - pairs.true_center
    pairs["reverse_error"] = pairs.rational_to_irrational - pairs.true_center
    pairs["parent_error"] = pairs.parent_ridge - pairs.true_center
    pairs["parent_abs_error"] = np.abs(pairs.parent_error)
    pairs["better_single_error"] = np.minimum(np.abs(pairs.forward_error), np.abs(pairs.reverse_error))
    wrong = make_wrong_pairs(pairs)
    wrong_key = ["pair_id", "condition", "window"]
    pairs = pairs.merge(
        wrong[wrong_key + ["wrong_reverse_ridge", "wrong_pair_parent", "wrong_pair_abs_error"]],
        on=wrong_key,
        how="left",
        validate="one_to_one",
    )

    identity_rows: list[dict] = []
    for (pair_id, condition), group in pairs.groupby(["pair_id", "condition"]):
        identity_rows.append(
            {
                "pair_id": pair_id,
                "condition": condition,
                "true_center": float(group.true_center.iloc[0]),
                "paired_abs_error_median": float(group.parent_abs_error.median()),
                "paired_parent_range": float(group.parent_ridge.max() - group.parent_ridge.min()),
                "better_single_error_median": float(group.better_single_error.median()),
                "wrong_pair_abs_error_median": float(group.wrong_pair_abs_error.median()),
                "paired_error_median": float(group.parent_error.median()),
            }
        )
    identities = pd.DataFrame(identity_rows)

    gate_rows: list[dict] = []
    clean_mix = float(audit[audit.condition == "clean"].mix_rms.median())
    asym_mix = float(audit[audit.condition == "asymmetric"].mix_rms.median())
    asym_advance = float(audit[audit.condition == "asymmetric"].advance_complement_rms.median())
    p1 = clean_mix <= 1e-12 and asym_mix >= 0.05 and asym_advance >= 0.01
    gate_rows.append({"gate": "P1 asymmetry audit", "passed": bool(p1), "value": json.dumps({"clean_mix_rms": clean_mix, "asymmetric_mix_rms": asym_mix, "asymmetric_advance_rms": asym_advance})})

    grouped_separation = children.groupby(["condition", "direction", "window"]).endpoint_separation.median()
    prediction_rate = float(children.predicted.mean())
    p2 = grouped_separation.min() >= 0.75 and prediction_rate >= 0.95
    gate_rows.append({"gate": "P2 endpoint recovery", "passed": bool(p2), "value": f"minimum grouped median={grouped_separation.min():.6f}; prediction rate={prediction_rate:.4f}"})

    p3_details = {}
    p4_details = {}
    p5_details = {}
    p6_details = {}
    p3 = p4 = p5 = p6 = True
    for index, condition in enumerate(("clean", "asymmetric")):
        identity_part = identities[identities.condition == condition]
        loc = bootstrap_median(identity_part.paired_abs_error_median.to_numpy(float), 100 + index)
        window_medians = pairs[pairs.condition == condition].groupby("window").parent_abs_error.median().to_dict()
        p3_details[condition] = {"identity": loc, "window_medians": {str(k): float(v) for k, v in window_medians.items()}}
        p3 = p3 and loc["estimate"] <= 32 and loc["ci_high"] <= 64 and all(value <= 32 for value in window_medians.values())

        inv = bootstrap_median(identity_part.paired_parent_range.to_numpy(float), 200 + index)
        p4_details[condition] = inv
        p4 = p4 and inv["estimate"] <= 32 and inv["ci_high"] <= 64

        paired_error = identity_part.paired_abs_error_median.to_numpy(float)
        single_error = identity_part.better_single_error_median.to_numpy(float)
        gain = bootstrap_median(single_error - paired_error, 300 + index)
        paired_median = float(np.median(paired_error))
        single_median = float(np.median(single_error))
        p5_details[condition] = {"paired_median": paired_median, "better_single_median": single_median, "gain": gain}
        p5 = p5 and paired_median <= 0.25 * single_median and gain["ci_low"] > 0

        wrong_error = identity_part.wrong_pair_abs_error_median.to_numpy(float)
        wrong_gain = bootstrap_median(wrong_error - paired_error, 400 + index)
        wrong_median = float(np.median(wrong_error))
        p6_details[condition] = {"paired_median": paired_median, "wrong_pair_median": wrong_median, "gain": wrong_gain}
        p6 = p6 and paired_median <= 0.25 * wrong_median and wrong_gain["ci_low"] > 0

    gate_rows.append({"gate": "P3 relational localization", "passed": bool(p3), "value": json.dumps(p3_details)})
    gate_rows.append({"gate": "P4 relational window invariance", "passed": bool(p4), "value": json.dumps(p4_details)})
    gate_rows.append({"gate": "P5 pair beats either child", "passed": bool(p5), "value": json.dumps(p5_details)})
    gate_rows.append({"gate": "P6 wrong-pair specificity", "passed": bool(p6), "value": json.dumps(p6_details)})

    gates = pd.DataFrame(gate_rows)
    passed = int(gates.passed.sum())
    if passed == 6:
        verdict = "SUPPORTED [SYNTHETIC RELATIONAL PARENT-RIDGE INSTRUMENT ONLY]"
    elif p1 and p2 and (not p3 or not p4):
        verdict = "RELATIONAL RIDGE NOT RESOLVED"
    elif all(gates.iloc[:5].passed) and not p6:
        verdict = "PAIRING NOT SPECIFIC"
    else:
        verdict = "NOT SUPPORTED"
    gates.attrs["verdict"] = verdict

    audit.to_csv(HERE / f"{PREFIX}_ASYMMETRY_AUDIT.csv", index=False)
    children.to_csv(HERE / f"{PREFIX}_CHILDREN.csv", index=False)
    pairs.to_csv(HERE / f"{PREFIX}_PAIRS.csv", index=False)
    identities.to_csv(HERE / f"{PREFIX}_IDENTITIES.csv", index=False)
    gates.to_csv(HERE / f"{PREFIX}_FROZEN_GATES.csv", index=False)

    results = {
        "test": "T355",
        "run_date": "2026-08-11",
        "protocol_sha256": digest(PROTOCOL),
        "verdict": verdict,
        "passed_gates": passed,
        "total_gates": 6,
        "audit_rows": int(len(audit)),
        "child_rows": int(len(children)),
        "pair_rows": int(len(pairs)),
        "identity_rows": int(len(identities)),
        "P1_asymmetry": json.loads(gate_rows[0]["value"]),
        "P3_localization": p3_details,
        "P4_invariance": p4_details,
        "P5_single_control": p5_details,
        "P6_wrong_pair": p6_details,
    }
    (HERE / f"{PREFIX}_RESULTS.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    make_figure(audit, pairs, identities, gates, HERE / f"{PREFIX}_FIGURE.png")

    report = [
        "# T355 - Irrationality relational parent ridge",
        "",
        "**Run date:** 11 August 2026  ",
        "**Evidence boundary:** synthetic known-referee relational-instrument calibration  ",
        f"**Verdict:** **{verdict}**  ",
        f"**Frozen gates:** **{passed}/6 passed**",
        "",
        "## Answer first",
        "",
        "T355 froze the parent estimate as the unweighted midpoint of two independently measured directional child ridges. The primary condition used unequal timing, nonlinear shapes, independent phases and different tapered child perturbations while retaining one hidden parent seam.",
        "",
        "## Relational recovery",
        "",
        "| condition | paired median error | paired window range | better single child | wrong pair |",
        "|---|---:|---:|---:|---:|",
    ]
    for condition in ("clean", "asymmetric"):
        report.append(
            f"| {condition} | {p3_details[condition]['identity']['estimate']:.3f} [{p3_details[condition]['identity']['ci_low']:.3f}, {p3_details[condition]['identity']['ci_high']:.3f}] | {p4_details[condition]['estimate']:.3f} [{p4_details[condition]['ci_low']:.3f}, {p4_details[condition]['ci_high']:.3f}] | {p5_details[condition]['better_single_median']:.3f} | {p6_details[condition]['wrong_pair_median']:.3f} |"
        )
    report.extend(["", "## Frozen gates", "", "| gate | result | headline |", "|---|---|---|"])
    for row in gates.itertuples():
        report.append(f"| {row.gate} | {'PASS' if row.passed else 'FAIL'} | `{str(row.value)[:180]}` |")
    report.extend(
        [
            "",
            f"![T355 relational parent ridge]({PREFIX}_FIGURE.png)",
            "",
            "## Interpretation boundary",
            "",
            "A pass is synthetic evidence for this paired instrument, not proof of a universal physical ridge. Both children were generated around a supplied common seam; physical transfer still requires an independently justified pairing and an unseen event time.",
            "",
            "## Artifacts",
            "",
            f"- `{PREFIX}_ASYMMETRY_AUDIT.csv`",
            f"- `{PREFIX}_CHILDREN.csv`",
            f"- `{PREFIX}_PAIRS.csv`",
            f"- `{PREFIX}_IDENTITIES.csv`",
            f"- `{PREFIX}_FROZEN_GATES.csv`",
            f"- `{PREFIX}_RESULTS.json`",
            f"- `{PREFIX}_FIGURE.png`",
            "- `t355_irrationality_relational_parent_ridge.py`",
        ]
    )
    (HERE / f"{PREFIX}_REPORT_2026-08-11.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": verdict, "gates": f"{passed}/6", "audit": len(audit), "children": len(children), "pairs": len(pairs)}, indent=2))


if __name__ == "__main__":
    main()
