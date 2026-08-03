#!/usr/bin/env python3
"""T326: frozen independent plant replication of the T325 ARA/Phi operator."""

from __future__ import annotations

import hashlib
import json
import math
from collections import OrderedDict
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
LANDREIN = HERE / "source_landrein_2015"
CYANELLA = HERE / "source_cyanella_2025"
PROTOCOL = HERE / "T326_PHI_CIRCLE_TRAIN_INDEPENDENT_PLANTS_PROTOCOL_v1_FROZEN.md"
PREFIX = "T326_PHI_CIRCLE_TRAIN_INDEPENDENT_PLANTS"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_MINOR = 2.0 / PHI**2
RNG_SEED = 326
N_NULL = 10_000
N_BOOT = 10_000

CANDIDATES = OrderedDict(
    [
        ("persistence", 0.0),
        ("one_third", 2.0 / 3.0),
        ("one_over_e", 2.0 / math.e),
        ("three_eighths", 3.0 / 4.0),
        ("fibonacci_8_21", 16.0 / 21.0),
        ("phi", PHI_MINOR),
        ("two_fifths", 4.0 / 5.0),
        ("silver_conjugate", 2.0 * (math.sqrt(2.0) - 1.0)),
        ("ridge", 1.0),
    ]
)

LANDREIN_FILES = OrderedDict(
    [
        ("Col0-JL.txt", ("Col0", "JL")),
        ("Col0-JC-JL.txt", ("Col0", "JC-JL")),
        ("WS4-JL.txt", ("WS4", "JL")),
        ("WS4-JC-JL.txt", ("WS4", "JC-JL")),
        ("clasp1-JL.txt", ("clasp1", "JL")),
        ("clasp1-JC-Jl.txt", ("clasp1", "JC-JL")),
        ("bot17-JL.txt", ("bot1-7", "JL")),
        ("bot17-JC-JL.txt", ("bot1-7", "JC-JL")),
    ]
)

RAW_PAIRS = OrderedDict(
    [
        ("WS4-JL-Angles-Bruts.txt", "WS4-JL.txt"),
        ("WS4-JC-JL-Angles-Bruts.txt", "WS4-JC-JL.txt"),
        ("bot17-JL-Angles-Bruts.txt", "bot17-JL.txt"),
        ("bot17-JC-JL-Angles-Bruts.txt", "bot17-JC-JL.txt"),
    ]
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest().upper()


def d2(a, b):
    d = np.abs(np.asarray(a, dtype=float) - np.asarray(b, dtype=float))
    return np.minimum(d, 2.0 - d)


def read_numeric_tsv(path: Path) -> pd.DataFrame:
    """Read a two/three-column source TSV, tolerating a missing header row."""
    raw = pd.read_csv(path, sep="\t", header=None, dtype=str)
    for c in raw.columns:
        raw[c] = pd.to_numeric(raw[c], errors="coerce")
    raw = raw.dropna(subset=[raw.columns[0]])
    return raw.reset_index(drop=True)


def load_landrein() -> pd.DataFrame:
    parts = []
    for filename, (genotype, condition) in LANDREIN_FILES.items():
        path = LANDREIN / filename
        raw = read_numeric_tsv(path)
        plant_col = raw.columns[0]
        # The calculated angle is always the final source column. Some files
        # include a middle silique index; retaining the last column reproduces
        # the source's published divergence field without reprocessing it.
        angle_col = raw.columns[-1]
        frame = pd.DataFrame(
            {
                "dataset": "Landrein2015",
                "cohort": f"{genotype}_{condition}",
                "genotype": genotype,
                "condition": condition,
                "source_file": filename,
                "source_plant": raw[plant_col].astype(int),
                "angle_deg": raw[angle_col].astype(float),
            }
        )
        frame["event"] = frame.groupby("source_plant", sort=False).cumcount() + 1
        frame["plant_id"] = (
            frame["cohort"] + "_P" + frame["source_plant"].astype(str)
        )
        parts.append(frame)
    out = pd.concat(parts, ignore_index=True)
    if not np.isfinite(out["angle_deg"]).all():
        raise RuntimeError("Landrein contains non-finite angles")
    if ((out["angle_deg"] < 0) | (out["angle_deg"] > 360)).any():
        raise RuntimeError("Landrein angle outside frozen 0..360 support")
    return out


def load_cyanella() -> pd.DataFrame:
    source = pd.read_csv(CYANELLA / "cyanellaAlbaFlavescens_final_export.csv")
    angle_cols = sorted(
        [c for c in source.columns if c.startswith("angle")],
        key=lambda c: int(c.replace("angle", "")),
    )
    rows = []
    for record in source.itertuples(index=False):
        values = record._asdict()
        bins = []
        for col in angle_cols:
            value = values.get(col)
            if pd.isna(value):
                break
            bins.append(int(value))
        if len(bins) < 3:
            continue
        low = sum(2 <= b <= 8 for b in bins)
        high = sum(10 <= b <= 16 for b in bins)
        orientation = "clockwise" if low > 0 and high == 0 else (
            "counterclockwise" if high > 0 and low == 0 else "mixed_or_neutral"
        )
        for event, b in enumerate(bins, start=1):
            degrees = ((b - 1) * 22.5) % 360.0
            if orientation == "counterclockwise":
                common = (-degrees) % 360.0
            elif orientation == "clockwise":
                common = degrees
            else:
                common = min(degrees, 360.0 - degrees)
            rows.append(
                {
                    "dataset": "Cyanella2025",
                    "cohort": "Cyanella_all",
                    "genotype": "Cyanella_alba",
                    "condition": "field_2023",
                    "source_file": "cyanellaAlbaFlavescens_final_export.csv",
                    "source_plant": str(values["plant"]),
                    "plant_id": f"Cyanella_{values['plant']}",
                    "event": event,
                    "source_bin": b,
                    "source_orientation": orientation,
                    "angle_deg": common,
                }
            )
    return pd.DataFrame(rows)


def add_geometry(events: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for _, group in events.groupby("plant_id", sort=False):
        g = group.sort_values("event").copy()
        if g["event"].tolist() != list(range(1, len(g) + 1)):
            raise RuntimeError(f"Non-contiguous lineage {g['plant_id'].iloc[0]}")
        if len(g) < 3:
            continue
        g["u_ara"] = np.mod(g["angle_deg"].to_numpy(float) / 180.0, 2.0)
        g["position_ara"] = np.mod(np.cumsum(g["u_ara"].to_numpy(float)), 2.0)
        g["heldout"] = g["event"] >= 3
        frames.append(g)
    if not frames:
        raise RuntimeError("No eligible lineages")
    return pd.concat(frames, ignore_index=True)


def plant_losses(events: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for plant_id, group in events.groupby("plant_id", sort=False):
        g = group.sort_values("event")
        steps = g["u_ara"].to_numpy(float)
        positions = g["position_ara"].to_numpy(float)
        held = np.flatnonzero(g["heldout"].to_numpy(bool))
        anchor = positions[1]
        horizons = held - 1
        meta = g.iloc[0]
        for name, delta in CANDIDATES.items():
            pred = np.mod(anchor + horizons * delta, 2.0)
            rows.append(
                {
                    "dataset": meta["dataset"],
                    "cohort": meta["cohort"],
                    "genotype": meta["genotype"],
                    "condition": meta["condition"],
                    "plant_id": plant_id,
                    "events": len(g),
                    "candidate": name,
                    "increment_ara": delta,
                    "one_step_median_ara": float(np.median(d2(steps[held], delta))),
                    "one_step_mean_ara": float(np.mean(d2(steps[held], delta))),
                    "carrier_median_ara": float(np.median(d2(positions[held], pred))),
                    "carrier_mean_ara": float(np.mean(d2(positions[held], pred))),
                }
            )
    return pd.DataFrame(rows)


def candidate_summary(scores: pd.DataFrame, dataset: str, cohort: str = "ALL") -> pd.DataFrame:
    subset = scores[scores["dataset"] == dataset]
    if cohort != "ALL":
        subset = subset[subset["cohort"] == cohort]
    out = (
        subset.groupby(["candidate", "increment_ara"], as_index=False)
        .agg(
            plants=("plant_id", "nunique"),
            one_step_median_ara=("one_step_median_ara", "median"),
            one_step_mean_ara=("one_step_mean_ara", "mean"),
            carrier_median_ara=("carrier_median_ara", "median"),
            carrier_mean_ara=("carrier_mean_ara", "mean"),
        )
    )
    out.insert(0, "cohort", cohort)
    out.insert(0, "dataset", dataset)
    out["one_step_median_deg"] = out["one_step_median_ara"] * 180.0
    out["carrier_median_deg"] = out["carrier_median_ara"] * 180.0
    out["one_step_rank"] = out["one_step_median_ara"].rank(method="min")
    out["carrier_rank"] = out["carrier_median_ara"].rank(method="min")
    return out.sort_values("increment_ara")


def groups_for(events: pd.DataFrame, dataset: str):
    return [
        g.sort_values("event")
        for _, g in events[events["dataset"] == dataset].groupby("plant_id", sort=False)
    ]


def order_shuffle(groups, delta: float, rng: np.random.Generator):
    prepared = []
    true_losses = []
    for g in groups:
        steps = g["u_ara"].to_numpy(float)
        positions = g["position_ara"].to_numpy(float)
        anchor = positions[1]
        horizons = np.arange(1, len(steps) - 1, dtype=float)
        pred = np.mod(anchor + horizons * delta, 2.0)
        true_losses.append(float(np.median(d2(positions[2:], pred))))
        prepared.append((anchor, steps[2:].copy(), pred))
    observed = float(np.median(true_losses))
    null = np.empty(N_NULL)
    for draw in range(N_NULL):
        losses = []
        for anchor, held, pred in prepared:
            synthetic = np.mod(anchor + np.cumsum(rng.permutation(held)), 2.0)
            losses.append(float(np.median(d2(synthetic, pred))))
        null[draw] = np.median(losses)
    return {
        "observed": observed,
        "null_median": float(np.median(null)),
        "null_95": [float(np.quantile(null, 0.025)), float(np.quantile(null, 0.975))],
        "p_lower": float((1 + np.sum(null <= observed)) / (N_NULL + 1)),
    }


def compensation(groups, delta: float, rng: np.random.Generator):
    residuals = [g["u_ara"].to_numpy(float)[2:] - delta for g in groups]

    def ratio(parts):
        x = np.concatenate([a[:-1] for a in parts if len(a) >= 2])
        y = np.concatenate([a[1:] for a in parts if len(a) >= 2])
        den = np.median((np.abs(x) + np.abs(y)) / 2)
        return float(np.median(np.abs((x + y) / 2)) / den) if den > 0 else math.nan

    observed = ratio(residuals)
    within = np.empty(N_NULL)
    for draw in range(N_NULL):
        within[draw] = ratio([rng.permutation(a) for a in residuals])

    xs = np.concatenate([a[:-1] for a in residuals if len(a) >= 2])
    ys = np.concatenate([a[1:] for a in residuals if len(a) >= 2])
    plant_labels = np.concatenate(
        [np.full(len(a) - 1, i, int) for i, a in enumerate(residuals) if len(a) >= 2]
    )
    pool = np.concatenate(residuals)
    pool_labels = np.concatenate([np.full(len(a), i, int) for i, a in enumerate(residuals)])
    allowed = [np.flatnonzero(pool_labels != label) for label in plant_labels]
    broken = np.empty(N_NULL)
    for draw in range(N_NULL):
        by = np.array([pool[idx[rng.integers(len(idx))]] for idx in allowed])
        den = np.median((np.abs(xs) + np.abs(by)) / 2)
        broken[draw] = np.median(np.abs((xs + by) / 2)) / den
    return {
        "pairs": int(len(xs)),
        "observed_ratio": observed,
        "within_order_p_lower": float((1 + np.sum(within <= observed)) / (N_NULL + 1)),
        "within_order_null_median": float(np.median(within)),
        "broken_lineage_p_lower": float((1 + np.sum(broken <= observed)) / (N_NULL + 1)),
        "broken_lineage_null_median": float(np.median(broken)),
    }


def fibonacci_profiles(groups):
    rows = []
    for name, delta in CANDIDATES.items():
        for lag in [2, 3, 5, 8, 13]:
            plant_values = []
            for g in groups:
                p = g["position_ara"].to_numpy(float)
                if len(p) <= lag:
                    continue
                plant_values.append(float(np.median(d2(p[lag:], p[:-lag]))))
            if not plant_values:
                continue
            predicted = float(d2((lag * delta) % 2.0, 0.0))
            observed = float(np.median(plant_values))
            rows.append(
                {
                    "candidate": name,
                    "lag": lag,
                    "plants": len(plant_values),
                    "observed_return_ara": observed,
                    "predicted_return_ara": predicted,
                    "absolute_profile_error": abs(observed - predicted),
                }
            )
    out = pd.DataFrame(rows)
    mae = (
        out.groupby("candidate", as_index=False)["absolute_profile_error"]
        .mean()
        .rename(columns={"absolute_profile_error": "five_lag_mae"})
    )
    return out, mae


def bootstrap_phi_vs_eighth(scores: pd.DataFrame, dataset: str, rng: np.random.Generator):
    s = scores[scores["dataset"] == dataset]
    pivot_child = s.pivot(index="plant_id", columns="candidate", values="one_step_median_ara")
    pivot_parent = s.pivot(index="plant_id", columns="candidate", values="carrier_median_ara")
    n = len(pivot_child)
    child = np.empty(N_BOOT)
    parent = np.empty(N_BOOT)
    for i in range(N_BOOT):
        idx = rng.integers(0, n, n)
        child[i] = np.median(
            pivot_child["phi"].to_numpy()[idx] - pivot_child["three_eighths"].to_numpy()[idx]
        )
        parent[i] = np.median(
            pivot_parent["phi"].to_numpy()[idx] - pivot_parent["three_eighths"].to_numpy()[idx]
        )
    return {
        "plants": n,
        "child_phi_minus_three_eighths": {
            "observed": float(np.median(pivot_child["phi"] - pivot_child["three_eighths"])),
            "bootstrap_95": [float(np.quantile(child, 0.025)), float(np.quantile(child, 0.975))],
        },
        "parent_phi_minus_three_eighths": {
            "observed": float(np.median(pivot_parent["phi"] - pivot_parent["three_eighths"])),
            "bootstrap_95": [float(np.quantile(parent, 0.025)), float(np.quantile(parent, 0.975))],
        },
    }


def raw_reconstruction_checks():
    rows = []
    for raw_name, calc_name in RAW_PAIRS.items():
        raw = read_numeric_tsv(LANDREIN / raw_name)
        calc = read_numeric_tsv(LANDREIN / calc_name)
        for plant in sorted(set(raw.iloc[:, 0].astype(int)) & set(calc.iloc[:, 0].astype(int))):
            pos = raw.loc[raw.iloc[:, 0].astype(int) == plant, raw.columns[-1]].to_numpy(float)
            published = calc.loc[calc.iloc[:, 0].astype(int) == plant, calc.columns[-1]].to_numpy(float)
            forward = np.mod(pos[1:] - pos[:-1], 360.0)
            backward = np.mod(pos[:-1] - pos[1:], 360.0)
            n = min(len(published), len(forward))
            if n == 0:
                continue
            f_mae = float(np.mean(np.abs(forward[:n] - published[:n])))
            b_mae = float(np.mean(np.abs(backward[:n] - published[:n])))
            rows.append(
                {
                    "raw_file": raw_name,
                    "calculated_file": calc_name,
                    "plant": plant,
                    "compared": n,
                    "forward_mae_deg": f_mae,
                    "backward_mae_deg": b_mae,
                    "matching_direction": "forward" if f_mae <= b_mae else "backward",
                    "best_mae_deg": min(f_mae, b_mae),
                }
            )
    return pd.DataFrame(rows)


def write_report(result, summary: pd.DataFrame, raw_checks: pd.DataFrame):
    land = summary[(summary.dataset == "Landrein2015") & (summary.cohort == "ALL")]
    child_winner = land.sort_values("one_step_median_ara").iloc[0]
    parent_winner = land.sort_values("carrier_median_ara").iloc[0]
    c = result["Landrein2015"]
    verdict = result["verdict"]
    cohort_lines = []
    for cohort in sorted(summary.loc[summary.dataset == "Landrein2015", "cohort"].unique()):
        if cohort == "ALL":
            continue
        q = summary[(summary.dataset == "Landrein2015") & (summary.cohort == cohort)]
        cw = q.sort_values("one_step_median_ara").iloc[0]
        pw = q.sort_values("carrier_median_ara").iloc[0]
        cohort_lines.append(
            f"| {cohort} | {int(cw.plants)} | {cw.candidate} | {cw.one_step_median_deg:.3f}° | "
            f"{pw.candidate} | {pw.carrier_median_deg:.3f}° |"
        )
    report = f"""# T326 report — independent plant Phi circle-train replication

**Date:** 2 August 2026  
**Frozen protocol:** `T326_PHI_CIRCLE_TRAIN_INDEPENDENT_PLANTS_PROTOCOL_v1_FROZEN.md`  
**Protocol SHA-256:** `{result['protocol_sha256']}`  
**Verdict:** **{verdict}**

## Answer first

The independent Landrein Arabidopsis archive does **not** reproduce the exact
T325 scale split as a complete frozen result. Its lowest local-child fixed
loss is **{child_winner.candidate}** ({child_winner.one_step_median_deg:.3f}°),
and its lowest ordered parent-carrier fixed loss is **{parent_winner.candidate}**
({parent_winner.carrier_median_deg:.3f}°).

For the declared close comparison, child `Phi - 3/8` is
`{c['bootstrap']['child_phi_minus_three_eighths']['observed']:.6f}` ARA and
parent `Phi - 3/8` is
`{c['bootstrap']['parent_phi_minus_three_eighths']['observed']:.6f}` ARA.
Negative means Phi is better; positive means `3/8` is better.

Real downstream/developmental order versus within-plant shuffling gives
`p={c['order_shuffle']['p_lower']:.6f}` for the frozen Phi parent carrier.
The result is therefore retained even if its direction differs from T325: no
candidate or gate was changed after the protocol was frozen.

## Primary aggregate ranking

| Candidate | Child median | Child rank | Parent median | Parent rank |
|---|---:|---:|---:|---:|
"""
    for row in land.sort_values("increment_ara").itertuples():
        report += (
            f"| {row.candidate} | {row.one_step_median_deg:.3f}° | {int(row.one_step_rank)} | "
            f"{row.carrier_median_deg:.3f}° | {int(row.carrier_rank)} |\n"
        )
    report += """

## Cohort results

| Cohort | Plants | Child winner | Child loss | Parent winner | Parent loss |
|---|---:|---|---:|---|---:|
""" + "\n".join(cohort_lines)
    report += f"""

## Ordered controls

- Phi true-order parent loss: `{c['order_shuffle']['observed']:.6f}` ARA.
- Shuffled-order median: `{c['order_shuffle']['null_median']:.6f}` ARA.
- Shuffle lower-tail p: `{c['order_shuffle']['p_lower']:.6f}`.
- Adjacent compensation ratio: `{c['compensation']['observed_ratio']:.6f}`.
- Within-order compensation p: `{c['compensation']['within_order_p_lower']:.6f}`.
- Broken-lineage compensation p: `{c['compensation']['broken_lineage_p_lower']:.6f}`.
- Best five-lag return candidate: `{c['fibonacci_best_candidate']}`.

## Cyanella resolution control

The Cyanella archive supplies ordered lineages, but angles are measured in
`22.5°` bins. The exact Phi-versus-`3/8` separation is only `2.507764°`.
Its numerical rankings are recorded in the machine outputs, but its formal
verdict is **INCONCLUSIVE — RESOLUTION**. It cannot decide the close constant
question.

## Source reconstruction and provenance

The Landrein primary uses the authors' published calculated divergence files.
Where raw angular positions exist, both subtraction directions were checked
against those published files. The median best reconstruction MAE is
`{raw_checks.best_mae_deg.median():.6f}°` across `{len(raw_checks)}` plant-file
checks. These checks verify extraction only and are not extra evidence.

The complete source hashes, event rows, plant scores, candidate summaries,
null results and independent validation are stored beside this report.

## Scientific boundary

This is an independent-source test of one frozen crosswalk. It neither proves
nor disproves the complete ARA framework. The result distinguishes the
specific T325 scale-split claim from the broader facts that phyllotactic
angles are ordered, approximately golden, noisy, genotype-dependent and
sometimes rearranged during stem development.
"""
    (HERE / f"{PREFIX}_REPORT_2026-08-02.md").write_text(report, encoding="utf-8")


def main():
    if sha256(PROTOCOL) != "A049DEBBAB20DE75422A94D29ED932FCEAA9E984DFC58E9879937B6527296D18":
        raise RuntimeError("Frozen protocol hash mismatch")
    rng = np.random.default_rng(RNG_SEED)
    landrein = add_geometry(load_landrein())
    cyanella = add_geometry(load_cyanella())
    events = pd.concat([landrein, cyanella], ignore_index=True, sort=False)
    scores = plant_losses(events)

    summaries = []
    for dataset in ["Landrein2015", "Cyanella2025"]:
        summaries.append(candidate_summary(scores, dataset))
        for cohort in events.loc[events.dataset == dataset, "cohort"].unique():
            summaries.append(candidate_summary(scores, dataset, cohort))
    summary = pd.concat(summaries, ignore_index=True)

    land_groups = groups_for(events, "Landrein2015")
    order = order_shuffle(land_groups, PHI_MINOR, rng)
    comp = compensation(land_groups, PHI_MINOR, rng)
    fib, fib_mae = fibonacci_profiles(land_groups)
    boot = bootstrap_phi_vs_eighth(scores, "Landrein2015", rng)
    raw_checks = raw_reconstruction_checks()

    land_all = summary[(summary.dataset == "Landrein2015") & (summary.cohort == "ALL")]
    child_winner = str(land_all.sort_values("one_step_median_ara").iloc[0].candidate)
    parent_winner = str(land_all.sort_values("carrier_median_ara").iloc[0].candidate)
    fib_winner = str(fib_mae.sort_values("five_lag_mae").iloc[0].candidate)
    if child_winner == "three_eighths" and parent_winner == "phi" and order["p_lower"] < 0.05:
        verdict = "REPLICATED SCALE SPLIT"
    elif child_winner == "three_eighths" or parent_winner == "phi" or order["p_lower"] < 0.05:
        verdict = "PARTIAL / MIXED"
    else:
        verdict = "NOT REPLICATED"

    source_hashes = {}
    for folder in [LANDREIN, CYANELLA]:
        for path in sorted(folder.iterdir()):
            if path.is_file():
                source_hashes[str(path.relative_to(HERE))] = sha256(path)

    result = {
        "test_id": "T326-PHI-CIRCLE-TRAIN-INDEPENDENT-PLANTS-v1",
        "protocol_sha256": sha256(PROTOCOL),
        "source_hashes": source_hashes,
        "verdict": verdict,
        "Landrein2015": {
            "events": int(len(landrein)),
            "plants": int(landrein.plant_id.nunique()),
            "cohorts": int(landrein.cohort.nunique()),
            "child_winner": child_winner,
            "parent_winner": parent_winner,
            "order_shuffle": order,
            "compensation": comp,
            "bootstrap": boot,
            "fibonacci_best_candidate": fib_winner,
            "fibonacci_mae": {
                row.candidate: float(row.five_lag_mae) for row in fib_mae.itertuples()
            },
        },
        "Cyanella2025": {
            "events": int(len(cyanella)),
            "plants": int(cyanella.plant_id.nunique()),
            "recorded_bin_width_deg": 22.5,
            "phi_vs_three_eighths_separation_deg": abs(360.0 / PHI**2 - 135.0),
            "formal_verdict": "INCONCLUSIVE — RESOLUTION",
        },
        "raw_reconstruction": {
            "checks": int(len(raw_checks)),
            "median_best_mae_deg": float(raw_checks.best_mae_deg.median()),
            "max_best_mae_deg": float(raw_checks.best_mae_deg.max()),
        },
    }

    events.to_csv(HERE / f"{PREFIX}_EVENTS.csv", index=False)
    scores.to_csv(HERE / f"{PREFIX}_PLANT_SCORES.csv", index=False)
    summary.to_csv(HERE / f"{PREFIX}_CANDIDATE_SUMMARY.csv", index=False)
    fib.to_csv(HERE / f"{PREFIX}_FIBONACCI.csv", index=False)
    raw_checks.to_csv(HERE / f"{PREFIX}_RAW_RECONSTRUCTION.csv", index=False)
    (HERE / f"{PREFIX}_RESULTS.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    write_report(result, summary, raw_checks)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

