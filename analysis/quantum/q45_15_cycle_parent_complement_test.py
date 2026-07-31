"""Q45 frozen shaping test for the missing 15-cycle parent complement.

The candidate is the local-product Pauli relation L = a b^T.  Cadence,
eligibility and phase are defined from the connected relation C only.  The
identity T = C + L is checked as algebraic bookkeeping and is never scored as
evidence by itself.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import gzip
import hashlib
import json
import math
import os
import pathlib
import sys
import time
from collections import defaultdict


HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / "public_data" / "_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(HERE / ".mplconfig"))

import h5py
import matplotlib.pyplot as plt
import numpy as np

import q40_return_flow_relation_reversal_test as base
import q44_ara_mixing_prediction_test as q44
from q40c_post_result_double_helix_projection_audit import fit_orbit


TEST_ID = "Q45-15-CYCLE-PARENT-COMPLEMENT-v1"
PROTOCOL = HERE / "Q45_15_CYCLE_PARENT_COMPLEMENT_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA256 = (
    "43e83f4be441d3e29645cca888d35284287fc62c44bcc90e24e395143bbec9ca"
)
SOURCE = q44.SOURCE
ARCHIVE = q44.ARCHIVE
ARCHIVE_MD5 = q44.ARCHIVE_MD5
DERIVED = q44.DERIVED
CONNECTED = q44.CONNECTED
LOCAL_PRODUCT = q44.DATA / "q45_local_product_cache.npy"
LOCAL_QC = q44.DATA / "q45_local_product_qc.npz"

RESULTS = HERE / "Q45_15_CYCLE_PARENT_COMPLEMENT_RESULTS.json"
LINEAGES = HERE / "Q45_15_CYCLE_PARENT_COMPLEMENT_LINEAGES.csv.gz"
FLOW_SEEDS = HERE / "Q45_15_CYCLE_PARENT_COMPLEMENT_FLOW_SEEDS.csv"
PROFILES = HERE / "Q45_15_CYCLE_PARENT_COMPLEMENT_PROFILES.npz"
FIGURE_PNG = HERE / "Q45_15_CYCLE_PARENT_COMPLEMENT_DIAGNOSTICS.png"
FIGURE_SVG = HERE / "Q45_15_CYCLE_PARENT_COMPLEMENT_DIAGNOSTICS.svg"

PHASE_BINS = 16
BOOTSTRAP_DRAWS = 20_000
BOOTSTRAP_SEED = 450028
EPS = 1e-12

BLUE = "#537DB8"
GOLD = "#D99B31"
ORANGE = "#D85C4A"
PINK = "#B65D83"
INK = "#17212B"
MID = "#647180"
GRID = "#D9E0E7"
BG = "#FAFBFC"


def digest(path: pathlib.Path, algorithm: str) -> str:
    value = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def verify_frozen_inputs() -> None:
    actual_protocol = digest(PROTOCOL, "sha256")
    if actual_protocol != PROTOCOL_SHA256:
        raise RuntimeError(
            "Frozen Q45 protocol changed: "
            f"expected {PROTOCOL_SHA256}, got {actual_protocol}"
        )
    actual_archive = digest(ARCHIVE, "md5")
    if actual_archive != ARCHIVE_MD5:
        raise RuntimeError(
            "Q44 archive changed: "
            f"expected {ARCHIVE_MD5}, got {actual_archive}"
        )
    for path in (SOURCE, DERIVED, CONNECTED):
        if not path.exists():
            raise RuntimeError(f"Required Q44 source/cache missing: {path}")


def local_product_batch(rhos: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    expectation = np.einsum("nij,kji->nk", rhos, base.OPS, optimize=True).real
    a = expectation[:, :3]
    b = expectation[:, 3:6]
    local = a[:, :, None] * b[:, None, :]
    norms = np.column_stack(
        (
            np.linalg.norm(a, axis=1),
            np.linalg.norm(b, axis=1),
        )
    )
    return local.astype(np.float32), norms


def process_seed(seed: int):
    local = np.empty((500, 66, 3, 3), dtype=np.float32)
    max_a = 0.0
    max_b = 0.0
    nonfinite = 0
    with h5py.File(SOURCE, "r") as handle:
        group = handle[q44.locate_trial(handle, seed)]
        root = group["two_qubit_dms"]
        for time_index in range(500):
            rhos = np.stack(
                [
                    root[str(time_index)][name][()]
                    for name in base.PAIR_NAMES
                ]
            ).astype(np.complex128)
            local[time_index], norms = local_product_batch(rhos)
            max_a = max(max_a, float(np.max(norms[:, 0])))
            max_b = max(max_b, float(np.max(norms[:, 1])))
            nonfinite += int(np.size(local[time_index]) - np.isfinite(local[time_index]).sum())
    return seed, local, np.asarray((max_a, max_b, nonfinite), dtype=np.float64)


def build_local_cache(workers: int) -> None:
    verify_frozen_inputs()
    if LOCAL_PRODUCT.exists() and LOCAL_QC.exists():
        print("using existing Q45 local-product cache", flush=True)
        return
    local = np.lib.format.open_memmap(
        LOCAL_PRODUCT,
        mode="w+",
        dtype=np.float32,
        shape=(100, 500, 66, 3, 3),
    )
    qc = np.empty((100, 3), dtype=np.float64)
    started = time.time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(process_seed, seed) for seed in range(100)]
        for completed, future in enumerate(
            concurrent.futures.as_completed(futures), start=1
        ):
            seed, seed_local, seed_qc = future.result()
            local[seed] = seed_local
            qc[seed] = seed_qc
            if completed % 5 == 0 or completed == 100:
                print(
                    f"cached Q45 local relation {completed}/100 seeds "
                    f"({time.time() - started:.1f}s)",
                    flush=True,
                )
    local.flush()
    np.savez_compressed(
        LOCAL_QC,
        qc=qc,
        protocol_sha256=np.asarray(PROTOCOL_SHA256),
        archive_md5=np.asarray(ARCHIVE_MD5),
    )


def classify_development(u: np.ndarray, v: np.ndarray):
    fit = fit_orbit(u[:249], v[:249])
    period = fit["angular_period_samples"]
    lag15 = fit["fixed_lag_15"]["coordinate_correlation"]
    if 7.35 <= period <= 7.65 and lag15 >= 0.95:
        return "two_turn_7_5", fit
    if 14.8 <= period <= 15.2 and lag15 >= 0.95:
        return "one_turn_15", fit
    return "other", fit


def phase_definition(u: np.ndarray, v: np.ndarray, family: str):
    theta = np.unwrap(np.arctan2(v[:249], u[:249]))
    sample = np.arange(len(theta), dtype=np.float64)
    slope, intercept = np.polyfit(sample, theta, 1)
    full_sample = np.arange(499, dtype=np.float64)
    fitted = intercept + slope * full_sample
    parent_multiplier = 0.5 if family == "two_turn_7_5" else 1.0
    wrong_multiplier = 1.0 if family == "two_turn_7_5" else 2.0
    parent = np.mod(parent_multiplier * fitted, 2 * np.pi)
    wrong = np.mod(wrong_multiplier * fitted, 2 * np.pi)
    lagged = np.mod(parent_multiplier * (fitted - 4 * slope), 2 * np.pi)
    return parent, wrong, lagged, float(slope), float(intercept)


def phase_bins(phase: np.ndarray) -> np.ndarray:
    return np.floor(np.mod(phase, 2 * np.pi) / (2 * np.pi) * PHASE_BINS).astype(
        np.int16
    )


def fit_template(values: np.ndarray, bins: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    mean = np.mean(values, axis=0)
    output = np.empty((PHASE_BINS, 3, 3), dtype=np.float64)
    for index in range(PHASE_BINS):
        selected = values[bins == index]
        output[index] = np.mean(selected, axis=0) if len(selected) else mean
    return output


def template_metrics(
    local_line: np.ndarray,
    parent_phase: np.ndarray,
    wrong_phase: np.ndarray,
    lagged_phase: np.ndarray,
):
    dev = slice(0, 249)
    evaluation = slice(250, 499)
    dev_values = np.asarray(local_line[dev], dtype=np.float64)
    actual = np.asarray(local_line[evaluation], dtype=np.float64)
    dev_mean = np.mean(dev_values, axis=0)
    denominator = float(np.sum((actual - dev_mean) ** 2))
    if denominator <= EPS:
        return None

    parent_template = fit_template(dev_values, phase_bins(parent_phase[dev]))
    wrong_template = fit_template(dev_values, phase_bins(wrong_phase[dev]))
    parent_pred = parent_template[phase_bins(parent_phase[evaluation])]
    wrong_pred = wrong_template[phase_bins(wrong_phase[evaluation])]
    lagged_pred = parent_template[phase_bins(lagged_phase[evaluation])]

    sse_parent = float(np.sum((actual - parent_pred) ** 2))
    sse_wrong = float(np.sum((actual - wrong_pred) ** 2))
    sse_lagged = float(np.sum((actual - lagged_pred) ** 2))
    return {
        "constant_sse": denominator,
        "parent_sse": sse_parent,
        "wrong_sse": sse_wrong,
        "lagged_sse": sse_lagged,
        "parent_skill": 1.0 - sse_parent / denominator,
        "parent_over_wrong": (sse_wrong - sse_parent) / denominator,
        "parent_over_lagged": (sse_lagged - sse_parent) / denominator,
    }


def movement_metrics(c_line: np.ndarray, l_line: np.ndarray):
    shares = []
    state_shares = []
    relations = []
    for start in range(250, 485, 15):
        if start + 15 >= len(c_line):
            continue
        dc = np.diff(np.asarray(c_line[start : start + 16], dtype=np.float64), axis=0)
        dl = np.diff(np.asarray(l_line[start : start + 16], dtype=np.float64), axis=0)
        nc = np.linalg.norm(dc.reshape(15, -1), axis=1)
        nl = np.linalg.norm(dl.reshape(15, -1), axis=1)
        pc, pl = float(np.sum(nc)), float(np.sum(nl))
        if pc + pl > EPS:
            shares.append(pl / (pc + pl))

        c_state = np.linalg.norm(
            np.asarray(c_line[start : start + 15], dtype=np.float64).reshape(15, -1),
            axis=1,
        )
        l_state = np.linalg.norm(
            np.asarray(l_line[start : start + 15], dtype=np.float64).reshape(15, -1),
            axis=1,
        )
        if float(np.sum(c_state + l_state)) > EPS:
            state_shares.append(
                float(np.sum(l_state)) / float(np.sum(c_state + l_state))
            )

        valid = (nc > EPS) & (nl > EPS)
        if np.any(valid):
            cosine = np.sum(dc[valid] * dl[valid], axis=(1, 2)) / (
                nc[valid] * nl[valid]
            )
            relations.extend(cosine.tolist())
    if not shares:
        return None
    return {
        "path_share_l": float(np.mean(shares)),
        "path_share_c": float(1.0 - np.mean(shares)),
        "ara_x_l": float(2 * np.mean(shares)),
        "ara_x_c": float(2 * (1.0 - np.mean(shares))),
        "state_share_l": float(np.mean(state_shares)),
        "movement_relation": float(np.mean(relations)) if relations else float("nan"),
        "windows": int(len(shares)),
    }


def normalize_profile(values: np.ndarray) -> np.ndarray | None:
    values = np.asarray(values, dtype=np.float64)
    development = values[:249]
    lo, hi = np.quantile(development, [0.05, 0.95])
    if not np.isfinite(hi - lo) or hi - lo <= EPS:
        return None
    return 2 * (values - lo) / (hi - lo)


def binned_profile(values: np.ndarray, phase: np.ndarray) -> np.ndarray:
    bins = phase_bins(phase[250:499])
    selected = np.asarray(values[250:499], dtype=np.float64)
    output = np.full(PHASE_BINS, np.nan, dtype=np.float64)
    for index in range(PHASE_BINS):
        if np.any(bins == index):
            output[index] = float(np.mean(selected[bins == index]))
    return output


def gather_lineages(closure: np.ndarray, connected, local):
    rows: list[dict] = []
    profile_c = []
    profile_l = []
    profile_t = []
    eligible: list[tuple[int, int, str]] = []
    for seed in range(100):
        for pair in range(66):
            coordinate = base.coordinates(closure[seed, :, pair])
            if coordinate is None:
                continue
            u, v, _labels, _direction, coherence, occupancy = coordinate
            family, fit = classify_development(u, v)
            if family == "other":
                continue
            parent, wrong, lagged, slope, intercept = phase_definition(u, v, family)
            l_line = np.asarray(local[seed, :, pair], dtype=np.float64)
            c_line = np.asarray(connected[seed, :, pair], dtype=np.float64)
            phase = template_metrics(l_line, parent, wrong, lagged)
            movement = movement_metrics(c_line, l_line)
            if phase is None or movement is None:
                continue
            row = {
                "seed": seed,
                "pair": pair,
                "pair_name": base.PAIR_NAMES[pair],
                "family": family,
                "development_period": float(fit["angular_period_samples"]),
                "development_lag15_correlation": float(
                    fit["fixed_lag_15"]["coordinate_correlation"]
                ),
                "development_phase_slope": slope,
                "development_phase_intercept": intercept,
                "development_coordinate_coherence": float(coherence),
                "development_quadrant_occupancy": float(occupancy),
                **phase,
                **movement,
            }
            rows.append(row)
            eligible.append((seed, pair, family))

            c_norm = np.linalg.norm(c_line.reshape(500, -1), axis=1)
            l_norm = np.linalg.norm(l_line.reshape(500, -1), axis=1)
            t_norm = np.linalg.norm((c_line + l_line).reshape(500, -1), axis=1)
            c_scaled = normalize_profile(c_norm)
            l_scaled = normalize_profile(l_norm)
            t_scaled = normalize_profile(t_norm)
            if c_scaled is not None and l_scaled is not None and t_scaled is not None:
                profile_c.append(binned_profile(c_scaled, parent))
                profile_l.append(binned_profile(l_scaled, parent))
                profile_t.append(binned_profile(t_scaled, parent))
        if (seed + 1) % 10 == 0:
            print(f"analysed Q45 lineages for {seed + 1}/100 seeds", flush=True)
    return rows, eligible, np.asarray(profile_c), np.asarray(profile_l), np.asarray(profile_t)


def fit_scalar_model(blocks, target_name: str, augmented: bool, lagged: bool = False):
    xx = np.zeros((2, 2), dtype=np.float64)
    xy = np.zeros(2, dtype=np.float64)
    for c_line, l_line in blocks:
        dc = np.diff(c_line, axis=0)
        dl = np.diff(l_line, axis=0)
        dt = dc + dl
        # A 250-sample development block has 249 differences (0..248).
        # The target uses t+1, so the final admissible predictor index is 247.
        t = np.arange(5, 248)
        x1 = dc[t]
        x2 = dl[t - 4] if lagged else dl[t]
        y = dt[t + 1] if target_name == "parent" else dc[t + 1]
        xx[0, 0] += float(np.sum(x1 * x1))
        xy[0] += float(np.sum(x1 * y))
        if augmented:
            xx[0, 1] += float(np.sum(x1 * x2))
            xx[1, 0] = xx[0, 1]
            xx[1, 1] += float(np.sum(x2 * x2))
            xy[1] += float(np.sum(x2 * y))
    if augmented:
        return np.linalg.solve(xx + EPS * np.eye(2), xy)
    return np.asarray((xy[0] / (xx[0, 0] + EPS), 0.0))


def flow_models(connected, local, eligible):
    development_blocks = [
        (
            np.asarray(connected[seed, :250, pair], dtype=np.float64),
            np.asarray(local[seed, :250, pair], dtype=np.float64),
        )
        for seed, pair, _family in eligible
    ]
    coefficients = {}
    for target in ("parent", "child"):
        coefficients[f"{target}_baseline"] = fit_scalar_model(
            development_blocks, target, augmented=False
        )
        coefficients[f"{target}_augmented"] = fit_scalar_model(
            development_blocks, target, augmented=True
        )
        coefficients[f"{target}_lagged"] = fit_scalar_model(
            development_blocks, target, augmented=True, lagged=True
        )

    accum = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0]))
    for seed, pair, _family in eligible:
        c_line = np.asarray(connected[seed, :, pair], dtype=np.float64)
        l_line = np.asarray(local[seed, :, pair], dtype=np.float64)
        dc = np.diff(c_line, axis=0)
        dl = np.diff(l_line, axis=0)
        dt = dc + dl
        t = np.arange(254, 498)
        x1 = dc[t]
        x2 = dl[t]
        x2_lag = dl[t - 4]
        for target in ("parent", "child"):
            y = dt[t + 1] if target == "parent" else dc[t + 1]
            target_power = float(np.sum(y * y))
            models = {
                "baseline": (
                    coefficients[f"{target}_baseline"][0] * x1
                ),
                "augmented": (
                    coefficients[f"{target}_augmented"][0] * x1
                    + coefficients[f"{target}_augmented"][1] * x2
                ),
                "lagged": (
                    coefficients[f"{target}_lagged"][0] * x1
                    + coefficients[f"{target}_lagged"][1] * x2_lag
                ),
            }
            for method, predicted in models.items():
                error = float(np.sum((y - predicted) ** 2))
                accum[seed][f"{target}_{method}"][0] += error
                accum[seed][f"{target}_{method}"][1] += target_power

    seed_rows = []
    for seed in sorted(accum):
        row = {"seed": seed}
        for key, (error, target_power) in accum[seed].items():
            row[key] = math.sqrt(error / (target_power + EPS))
        seed_rows.append(row)
    return coefficients, seed_rows


def seed_balanced(rows: list[dict], field: str):
    grouped = defaultdict(list)
    for row in rows:
        value = float(row[field])
        if np.isfinite(value):
            grouped[int(row["seed"])].append(value)
    return {
        seed: float(np.mean(values))
        for seed, values in grouped.items()
        if values
    }


def bootstrap(values, statistic: str = "mean", seed_offset: int = 0):
    values = np.asarray(list(values), dtype=np.float64)
    values = values[np.isfinite(values)]
    if not len(values):
        return {"count": 0}
    rng = np.random.default_rng(BOOTSTRAP_SEED + seed_offset)
    samples = values[rng.integers(0, len(values), size=(BOOTSTRAP_DRAWS, len(values)))]
    draws = np.median(samples, axis=1) if statistic == "median" else np.mean(samples, axis=1)
    observed = float(np.median(values)) if statistic == "median" else float(np.mean(values))
    return {
        "count": int(len(values)),
        "statistic": statistic,
        "estimate": observed,
        "ci95": [
            float(np.quantile(draws, 0.025)),
            float(np.quantile(draws, 0.975)),
        ],
    }


def summarize_lineages(rows: list[dict]):
    parent_skill = seed_balanced(rows, "parent_skill")
    wrong_advantage = seed_balanced(rows, "parent_over_wrong")
    lagged_advantage = seed_balanced(rows, "parent_over_lagged")
    path_share = seed_balanced(rows, "path_share_l")
    state_share = seed_balanced(rows, "state_share_l")
    relation = seed_balanced(rows, "movement_relation")
    family = {}
    for name in ("two_turn_7_5", "one_turn_15"):
        selected = [row for row in rows if row["family"] == name]
        family[name] = {
            "lineages": len(selected),
            "seeds": len({row["seed"] for row in selected}),
            "parent_skill": bootstrap(
                seed_balanced(selected, "parent_skill").values(),
                seed_offset=10 if name == "two_turn_7_5" else 11,
            ),
            "path_share_l": bootstrap(
                seed_balanced(selected, "path_share_l").values(),
                statistic="median",
                seed_offset=12 if name == "two_turn_7_5" else 13,
            ),
        }
    return {
        "parent_phase_skill": bootstrap(parent_skill.values(), seed_offset=1),
        "parent_over_wrong_rung": bootstrap(
            wrong_advantage.values(), seed_offset=2
        ),
        "parent_over_four_sample_lag": bootstrap(
            lagged_advantage.values(), seed_offset=3
        ),
        "path_share_l": bootstrap(
            path_share.values(), statistic="median", seed_offset=4
        ),
        "state_share_l": bootstrap(
            state_share.values(), statistic="median", seed_offset=5
        ),
        "movement_relation": bootstrap(relation.values(), seed_offset=6),
        "families": family,
    }


def summarize_flow(seed_rows: list[dict]):
    output = {}
    for target in ("parent", "child"):
        baseline = np.asarray(
            [row[f"{target}_baseline"] for row in seed_rows], dtype=np.float64
        )
        augmented = np.asarray(
            [row[f"{target}_augmented"] for row in seed_rows], dtype=np.float64
        )
        lagged = np.asarray(
            [row[f"{target}_lagged"] for row in seed_rows], dtype=np.float64
        )
        output[target] = {
            "baseline_error": float(np.mean(baseline)),
            "augmented_error": float(np.mean(augmented)),
            "lagged_control_error": float(np.mean(lagged)),
            "augmented_advantage": bootstrap(
                baseline - augmented,
                seed_offset=20 if target == "parent" else 21,
            ),
            "real_l_over_lagged_advantage": bootstrap(
                lagged - augmented,
                seed_offset=22 if target == "parent" else 23,
            ),
        }
    return output


def write_lineages(rows: list[dict]) -> None:
    with gzip.open(LINEAGES, "wt", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_flow_seeds(rows: list[dict]) -> None:
    with FLOW_SEEDS.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def style_axis(axis) -> None:
    axis.set_facecolor(BG)
    axis.grid(True, color=GRID, linewidth=0.8, alpha=0.75)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.tick_params(colors=INK, labelsize=9)
    axis.xaxis.label.set_color(INK)
    axis.yaxis.label.set_color(INK)
    axis.title.set_color(INK)


def make_figure(
    rows: list[dict],
    profile_c: np.ndarray,
    profile_l: np.ndarray,
    profile_t: np.ndarray,
    flow: dict,
    verdict: str,
) -> None:
    centres = (np.arange(PHASE_BINS) + 0.5) * 360 / PHASE_BINS
    c_median = np.nanmedian(profile_c, axis=0)
    l_median = np.nanmedian(profile_l, axis=0)
    t_median = np.nanmedian(profile_t, axis=0)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.patch.set_facecolor(BG)
    ax = axes[0, 0]
    ax.plot(centres, c_median, color=BLUE, marker="o", label="connected child C")
    ax.plot(centres, l_median, color=GOLD, marker="s", label="candidate complement L")
    ax.plot(centres, t_median, color=INK, linestyle="--", label="full parent relation T")
    ax.axhline(1.0, color=MID, linewidth=1.2, label="ARA ridge")
    ax.set(
        title="Parent-phase ARA cuts",
        xlabel="extrapolated 15-cycle parent phase (degrees)",
        ylabel="development-normalised 0–2 ARA coordinate",
        xlim=(0, 360),
    )
    ax.legend(frameon=False, fontsize=8, ncol=2)
    style_axis(ax)

    ax = axes[0, 1]
    colors = {
        "two_turn_7_5": BLUE,
        "one_turn_15": GOLD,
    }
    for family, color in colors.items():
        selected = [row for row in rows if row["family"] == family]
        ax.scatter(
            [row["path_share_l"] for row in selected],
            [row["parent_skill"] for row in selected],
            s=9,
            alpha=0.25,
            color=color,
            label=family.replace("_", " "),
        )
    ax.axvline(0.5, color=INK, linestyle="--", linewidth=1.2)
    ax.axvspan(0.4, 0.6, color=GOLD, alpha=0.10)
    ax.axhline(0.0, color=MID, linewidth=1.0)
    ax.set(
        title="Candidate share and held-out parent-phase skill",
        xlabel="L movement share of C + L path",
        ylabel="phase-template skill versus static L",
    )
    ax.legend(frameon=False, fontsize=8)
    style_axis(ax)

    ax = axes[1, 0]
    labels = ["child→parent", "parent→child"]
    baseline = [flow["parent"]["baseline_error"], flow["child"]["baseline_error"]]
    augmented = [flow["parent"]["augmented_error"], flow["child"]["augmented_error"]]
    lagged = [
        flow["parent"]["lagged_control_error"],
        flow["child"]["lagged_control_error"],
    ]
    position = np.arange(2)
    width = 0.24
    ax.bar(position - width, baseline, width, color=MID, label="C only")
    ax.bar(position, augmented, width, color=GOLD, label="C + real L")
    ax.bar(position + width, lagged, width, color=BLUE, label="C + L lagged 4")
    ax.set_xticks(position, labels)
    ax.set(
        title="Held-out one-step matrix-flow error",
        ylabel="seed-balanced scaled Frobenius error (lower is better)",
    )
    ax.legend(frameon=False, fontsize=8)
    style_axis(ax)

    ax = axes[1, 1]
    gate_names = [
        "phase > static",
        "phase > wrong rung",
        "half-share band",
        "child→parent",
        "parent→child",
    ]
    gates = [
        float(flow["_gates"]["phase_skill"]),
        float(flow["_gates"]["wrong_rung"]),
        float(flow["_gates"]["half_share"]),
        float(flow["_gates"]["forward"]),
        float(flow["_gates"]["reverse"]),
    ]
    ax.barh(
        np.arange(len(gates)),
        gates,
        color=[GOLD if value else MID for value in gates],
    )
    ax.set_yticks(np.arange(len(gates)), gate_names)
    ax.set_xticks((0, 1), ("fail", "pass"))
    ax.set_xlim(-0.05, 1.05)
    ax.set(
        title="Frozen complement gates",
        xlabel=f"shaping verdict: {verdict}",
    )
    style_axis(ax)

    fig.suptitle(
        "Q45 — 15-cycle parent-complement shaping test",
        fontsize=18,
        color=INK,
        fontweight="bold",
    )
    fig.text(
        0.5,
        0.94,
        f"{len(rows):,} eligible lineages · {len({row['seed'] for row in rows})} seeds · "
        "phase defined from development C only",
        ha="center",
        color=MID,
        fontsize=10,
    )
    fig.text(
        0.02,
        0.01,
        "Source: Zenodo 10.5281/zenodo.16753415 · Q44 mimic archive · "
        "T=C+L is bookkeeping, not a scored result.",
        color=MID,
        fontsize=8,
    )
    fig.tight_layout(rect=(0.02, 0.035, 0.98, 0.92))
    fig.savefig(FIGURE_PNG, dpi=180, bbox_inches="tight")
    fig.savefig(FIGURE_SVG, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--build-only", action="store_true")
    args = parser.parse_args()

    build_local_cache(args.workers)
    if args.build_only:
        return

    derived = np.load(DERIVED, allow_pickle=False)
    closure = np.asarray(derived["closure"], dtype=np.float32)
    connected = np.load(CONNECTED, mmap_mode="r")
    local = np.load(LOCAL_PRODUCT, mmap_mode="r")

    rows, eligible, profile_c, profile_l, profile_t = gather_lineages(
        closure, connected, local
    )
    if not rows:
        raise RuntimeError("No Q45 eligible lineages")
    write_lineages(rows)
    np.savez_compressed(
        PROFILES,
        connected=profile_c.astype(np.float32),
        local=profile_l.astype(np.float32),
        parent=profile_t.astype(np.float32),
        phase_centres_degrees=(
            (np.arange(PHASE_BINS) + 0.5) * 360 / PHASE_BINS
        ).astype(np.float32),
    )

    lineage_summary = summarize_lineages(rows)
    coefficients, seed_flow_rows = flow_models(connected, local, eligible)
    write_flow_seeds(seed_flow_rows)
    flow_summary = summarize_flow(seed_flow_rows)

    seeds = len({row["seed"] for row in rows})
    phase_observations = len(rows) * 249
    adequacy = seeds >= 80 and len(rows) >= 1_000 and phase_observations >= 10_000
    phase_gate = (
        lineage_summary["parent_phase_skill"]["ci95"][0] > 0
    )
    wrong_gate = (
        lineage_summary["parent_over_wrong_rung"]["ci95"][0] > 0
    )
    share = lineage_summary["path_share_l"]
    half_gate = (
        0.40 <= share["estimate"] <= 0.60
        and share["ci95"][0] <= 0.50 <= share["ci95"][1]
    )
    forward_gate = (
        flow_summary["parent"]["augmented_advantage"]["ci95"][0] > 0
    )
    reverse_gate = (
        flow_summary["child"]["augmented_advantage"]["ci95"][0] > 0
    )
    gates = {
        "adequacy": adequacy,
        "phase_skill": phase_gate,
        "wrong_rung": wrong_gate,
        "half_share": half_gate,
        "forward": forward_gate,
        "reverse": reverse_gate,
    }
    scored = sum(
        gates[key]
        for key in ("phase_skill", "wrong_rung", "half_share", "forward", "reverse")
    )
    if adequacy and scored == 5:
        verdict = "SUPPORTED IN SHAPING ARCHIVE"
    elif adequacy and scored >= 3:
        verdict = "PARTIAL"
    else:
        verdict = "NOT SUPPORTED"

    flow_for_plot = dict(flow_summary)
    flow_for_plot["_gates"] = gates
    make_figure(
        rows,
        profile_c,
        profile_l,
        profile_t,
        flow_for_plot,
        verdict,
    )

    qc = np.load(LOCAL_QC, allow_pickle=False)["qc"]
    results = {
        "test_id": TEST_ID,
        "date": "2026-07-28",
        "status": "descriptive shaping on previously opened Q44 archive",
        "verdict": verdict,
        "gates": gates,
        "source": {
            "archive": ARCHIVE.name,
            "archive_md5": digest(ARCHIVE, "md5"),
            "hdf5": SOURCE.name,
            "branch": q44.BRANCH,
            "seeds": 100,
            "time_samples": 500,
            "pairs": 66,
            "development": "0..249",
            "evaluation": "250..499",
        },
        "frozen": {
            "protocol": PROTOCOL.name,
            "protocol_sha256": digest(PROTOCOL, "sha256"),
            "phase_bins": PHASE_BINS,
            "bootstrap_draws": BOOTSTRAP_DRAWS,
            "bootstrap_seed": BOOTSTRAP_SEED,
        },
        "eligibility": {
            "lineages": len(rows),
            "seeds": seeds,
            "evaluation_phase_observations": phase_observations,
            "family_counts": {
                name: sum(row["family"] == name for row in rows)
                for name in ("two_turn_7_5", "one_turn_15")
            },
        },
        "lineage_summary": lineage_summary,
        "flow_summary": flow_summary,
        "flow_coefficients": {
            key: [float(value) for value in coefficients[key]]
            for key in coefficients
        },
        "quality": {
            "max_local_bloch_a_norm": float(np.max(qc[:, 0])),
            "max_local_bloch_b_norm": float(np.max(qc[:, 1])),
            "nonfinite_local_product_values": int(np.sum(qc[:, 2])),
        },
        "bookkeeping_boundary": (
            "T=C+L is an exact Pauli-tensor decomposition and is not counted "
            "as evidence. Phase, path share and held-out lagged prediction are "
            "the scored quantities."
        ),
        "artifacts": {
            "lineages": LINEAGES.name,
            "flow_seeds": FLOW_SEEDS.name,
            "profiles": PROFILES.name,
            "figure_png": FIGURE_PNG.name,
            "figure_svg": FIGURE_SVG.name,
        },
    }
    RESULTS.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps({
        "verdict": verdict,
        "gates": gates,
        "lineages": len(rows),
        "seeds": seeds,
        "path_share_l": share,
        "phase_skill": lineage_summary["parent_phase_skill"],
        "flow": flow_summary,
    }, indent=2))


if __name__ == "__main__":
    main()
