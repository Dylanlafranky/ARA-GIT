"""Q35: ARA-first test for a fixed external counterpart to a complete loop.

The visible c2 relation-flow loop is treated as one complete local identity.
Candidate parent counterparts are selected on development only, remain fixed
in evaluation, and are compared with relation-broken controls.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import os
import pathlib
import sys
from collections import defaultdict

HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / ".q27_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))
os.environ.setdefault("MPLCONFIGDIR", str(HERE / ".mplconfig"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


DATA = HERE / "public_data" / "q34_cross_archive_greedy"
CACHE = DATA / "q34_derived_cache.npz"
ARCHIVE = DATA / "unnati_submit_12_pure_greedy.hdf5.zip"
PROTOCOL = HERE / "Q35_WHOLE_PHASE_EXTERNAL_COUNTERPART_PROTOCOL_v1_FROZEN.md"
FIDELITY = HERE / "Q35_WHOLE_PHASE_EXTERNAL_COUNTERPART_FIDELITY_v1.md"

RESULTS = HERE / "Q35_WHOLE_PHASE_EXTERNAL_COUNTERPART_RESULTS.json"
TRACKS = HERE / "Q35_WHOLE_PHASE_EXTERNAL_COUNTERPART_TRACKS.csv.gz"
CANDIDATES = HERE / "Q35_WHOLE_PHASE_EXTERNAL_COUNTERPART_CANDIDATES.csv"
FIGURE_PNG = HERE / "Q35_WHOLE_PHASE_EXTERNAL_COUNTERPART_GEOMETRY.png"
FIGURE_SVG = HERE / "Q35_WHOLE_PHASE_EXTERNAL_COUNTERPART_GEOMETRY.svg"

PROTOCOL_SHA256 = "3f8f872b5a32e6ec7ea61e8e61e9f452a55e361122ba2c5e1178f847043ddbbc"
FIDELITY_SHA256 = "c7cbc1c6860fb33cb47c985cd7eb7c05bdbffde8e231f2cec8eca0337b01d36e"
CACHE_SHA256 = "ab32ad22e207b9913eb69352f52ba9422e18ffb9bf8304d46412d80374428e3c"
ARCHIVE_MD5 = "c1cf77ccff486e3786d73ba47f8674f1"

TEST_ID = "Q35-WHOLE-PHASE-EXTERNAL-COUNTERPART-v1"
EPS = 1e-12
DEV_H = slice(0, 250)
DEV_P = slice(0, 249)
EVAL_START = 250
EVAL_STOP = 499  # phase points are 250..498
LAGS = tuple(range(8))
TIME_SHIFT = 37
PAIR_SHIFT = 17
BOOTSTRAP_SEED = 350927
BOOTSTRAP_DRAWS = 20_000
CONTROLS = ("time", "seed", "pair", "network")
VARIANTS = ("exact",) + CONTROLS


def digest(path: pathlib.Path, algorithm: str = "sha256") -> str:
    value = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def circulation(phase: np.ndarray) -> float:
    valid = np.isfinite(phase.real) & np.isfinite(phase.imag)
    if np.sum(valid) < 3:
        return float("nan")
    left = phase[:-1]
    right = phase[1:]
    good = (
        np.isfinite(left.real)
        & np.isfinite(left.imag)
        & np.isfinite(right.real)
        & np.isfinite(right.imag)
    )
    if np.sum(good) == 0:
        return float("nan")
    turns = np.angle(np.conj(left[good]) * right[good])
    turns = turns[np.abs(turns) > 1e-10]
    if turns.size == 0:
        return 0.0
    return float(abs(np.mean(np.sign(turns))))


def calibration_and_phase(
    h: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, dict[str, np.ndarray]]:
    """Return movement, unit phase and development-only calibration arrays."""
    g = np.diff(h, axis=2)
    dev_h = np.asarray(h[:, :, DEV_H, :], dtype=np.float64)
    dev_g = np.asarray(g[:, :, DEV_P, :], dtype=np.float64)
    q05 = np.quantile(dev_h, 0.05, axis=2)
    q95 = np.quantile(dev_h, 0.95, axis=2)
    center = (q05 + q95) / 2.0
    radius = (q95 - q05) / 2.0
    flow = np.quantile(np.abs(dev_g), 0.95, axis=2)

    level_cut = np.divide(
        h[:, :, :499, :] - center[:, :, None, :],
        radius[:, :, None, :],
        out=np.full((2, 100, 499, 66), np.nan, dtype=np.float64),
        where=radius[:, :, None, :] > EPS,
    )
    flow_cut = np.divide(
        g,
        flow[:, :, None, :],
        out=np.full((2, 100, 499, 66), np.nan, dtype=np.float64),
        where=flow[:, :, None, :] > EPS,
    )
    w = level_cut + 1j * flow_cut
    magnitude = np.abs(w)
    phase = np.divide(
        w,
        magnitude,
        out=np.full(w.shape, np.nan + 1j * np.nan, dtype=np.complex128),
        where=magnitude > EPS,
    )
    return g, phase, {
        "q05": q05,
        "q95": q95,
        "center": center,
        "radius": radius,
        "flow": flow,
        "w": w,
    }


def complete_loop_mask(
    phase: np.ndarray,
    w: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    eligible = np.zeros((100, 66), dtype=bool)
    coherence = np.full((100, 66), np.nan, dtype=np.float64)
    quadrant_min = np.zeros((100, 66), dtype=np.float64)
    for seed in range(100):
        for pair in range(66):
            p = phase[0, seed, DEV_P, pair]
            z = w[0, seed, DEV_P, pair]
            valid = (
                np.isfinite(p.real)
                & np.isfinite(p.imag)
                & np.isfinite(z.real)
                & np.isfinite(z.imag)
            )
            valid_fraction = float(np.mean(valid))
            if np.sum(valid) == 0:
                continue
            quadrant = (
                (z.real[valid] >= 0).astype(np.int8) * 2
                + (z.imag[valid] >= 0).astype(np.int8)
            )
            shares = np.asarray(
                [np.mean(quadrant == q) for q in range(4)],
                dtype=np.float64,
            )
            quadrant_min[seed, pair] = float(np.min(shares))
            coherence[seed, pair] = circulation(p)
            eligible[seed, pair] = bool(
                valid_fraction >= 0.95
                and quadrant_min[seed, pair] >= 0.05
                and coherence[seed, pair] >= 0.80
            )
    return eligible, coherence, quadrant_min


def pairwise_opposition(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    lvalid = np.isfinite(left.real) & np.isfinite(left.imag)
    rvalid = np.isfinite(right.real) & np.isfinite(right.imag)
    lzero = np.where(lvalid, left, 0.0 + 0.0j)
    rzero = np.where(rvalid, right, 0.0 + 0.0j)
    numerator = -np.real(np.conj(lzero).T @ rzero)
    counts = lvalid.astype(np.float64).T @ rvalid.astype(np.float64)
    return np.divide(
        numerator,
        counts,
        out=np.full(numerator.shape, -np.inf, dtype=np.float64),
        where=counts > 0,
    )


def choose_candidates(
    phase: np.ndarray,
    eligible: np.ndarray,
) -> list[dict[str, int | float]]:
    rows: list[dict[str, int | float]] = []
    for seed in range(100):
        ids = np.flatnonzero(eligible[seed])
        if ids.size < 3:
            continue
        dev = phase[0, seed, DEV_P, :][:, ids]
        best_score = np.full(ids.size, -np.inf, dtype=np.float64)
        best_pair = np.full(ids.size, -1, dtype=np.int16)
        best_lag = np.full(ids.size, -1, dtype=np.int8)
        for lag in LAGS:
            if lag == 0:
                score = pairwise_opposition(dev, dev)
            else:
                score = pairwise_opposition(dev[:-lag], dev[lag:])
            np.fill_diagonal(score, -np.inf)
            for a_pos in range(ids.size):
                b_pos = int(np.argmax(score[a_pos]))
                value = float(score[a_pos, b_pos])
                pair = int(ids[b_pos])
                # Lags are visited ascending. Strict improvement preserves the
                # frozen smaller-lag tie break; np.argmax preserves pair order.
                if value > best_score[a_pos] + 1e-15:
                    best_score[a_pos] = value
                    best_pair[a_pos] = pair
                    best_lag[a_pos] = lag
        for a_pos, source_pair in enumerate(ids):
            exact_pair = int(best_pair[a_pos])
            if exact_pair < 0:
                continue
            cyclic = [
                int(pair)
                for pair in ids
                if int(pair) not in (int(source_pair), exact_pair)
            ]
            cyclic.sort(
                key=lambda pair: ((pair - exact_pair) % 66, pair)
            )
            if not cyclic:
                continue
            rows.append(
                {
                    "seed": seed,
                    "source_pair": int(source_pair),
                    "counterpart_pair": exact_pair,
                    "lag": int(best_lag[a_pos]),
                    "development_opposition": float(best_score[a_pos]),
                    "pair_control": int(cyclic[0]),
                }
            )
    return rows


def phase_metrics(a: np.ndarray, b: np.ndarray) -> tuple[float, float, float]:
    valid = (
        np.isfinite(a.real)
        & np.isfinite(a.imag)
        & np.isfinite(b.real)
        & np.isfinite(b.imag)
    )
    if np.sum(valid) == 0:
        return float("nan"), float("nan"), float("nan")
    av = a[valid]
    bv = b[valid]
    opposition = float(-np.mean(np.real(np.conj(av) * bv)))
    residual = float(np.mean(np.abs(av + bv) / 2.0))
    delta = np.angle(bv) - np.angle(av) - np.pi
    wrapped = (delta + np.pi) % (2 * np.pi) - np.pi
    half_turn = float(np.mean(np.abs(wrapped) <= np.pi / 4))
    return opposition, residual, half_turn


def empirical_rank_ara(value: float, development: np.ndarray) -> float:
    finite = np.sort(development[np.isfinite(development)])
    if finite.size == 0 or not np.isfinite(value):
        return float("nan")
    return float(2.0 * np.searchsorted(finite, value, side="right") / finite.size)


def b_indices(
    variant: str,
    source_seed: int,
    source_pair: int,
    counterpart_pair: int,
    pair_control: int,
    lag: int,
    base_t: np.ndarray,
) -> tuple[int, int, int, np.ndarray]:
    branch = 0
    seed = source_seed
    pair = counterpart_pair
    times = base_t + lag
    if variant == "time":
        times = EVAL_START + (
            (times - EVAL_START + TIME_SHIFT) % (EVAL_STOP - EVAL_START)
        )
    elif variant == "seed":
        seed = (source_seed + 1) % 100
    elif variant == "pair":
        pair = pair_control
    elif variant == "network":
        branch = 1
    return branch, seed, pair, times.astype(np.int16)


def bootstrap_probability(
    rows: list[dict[str, object]],
    control: str,
    metric: str,
    direction: str,
) -> float:
    by_seed: dict[int, list[float]] = defaultdict(list)
    control_key = f"{control}_{metric}"
    exact_key = f"exact_{metric}"
    for row in rows:
        exact = float(row[exact_key])
        comparison = float(row[control_key])
        if np.isfinite(exact) and np.isfinite(comparison):
            by_seed[int(row["seed"])].append(exact - comparison)
    clusters = np.asarray(
        [np.mean(by_seed[seed]) for seed in sorted(by_seed) if by_seed[seed]],
        dtype=np.float64,
    )
    if clusters.size == 0:
        return float("nan")
    rng = np.random.default_rng(BOOTSTRAP_SEED + sum(map(ord, control + metric)))
    samples = rng.choice(
        clusters,
        size=(BOOTSTRAP_DRAWS, clusters.size),
        replace=True,
    ).mean(axis=1)
    if direction == "positive":
        return float(np.mean(samples > 0))
    return float(np.mean(samples < 0))


def summarize_variant(
    rows: list[dict[str, object]],
    seam_values: dict[str, list[float]],
    seam_turns: dict[str, list[float]],
    variant: str,
) -> dict[str, float | int]:
    opposition = np.asarray(
        [float(row[f"{variant}_opposition"]) for row in rows],
        dtype=np.float64,
    )
    residual = np.asarray(
        [float(row[f"{variant}_residual"]) for row in rows],
        dtype=np.float64,
    )
    half_turn = np.asarray(
        [float(row[f"{variant}_half_turn"]) for row in rows],
        dtype=np.float64,
    )
    seam = np.asarray(seam_values[variant], dtype=np.float64)
    turns = np.asarray(seam_turns[variant], dtype=np.float64)
    return {
        "lineages": int(len(rows)),
        "median_opposition": float(np.nanmedian(opposition)),
        "positive_opposition_fraction": float(np.nanmean(opposition > 0)),
        "median_parent_residual": float(np.nanmedian(residual)),
        "median_half_turn_occupancy": float(np.nanmedian(half_turn)),
        "seam_events": int(np.sum(np.isfinite(seam))),
        "seam_median_counterpart_x": float(np.nanmedian(seam)),
        "seam_far_pole_fraction": float(np.nanmean(seam > 1)),
        "seam_high_turn_fraction": float(np.nanmean(turns > 0.5)),
    }


def write_csvs(
    candidates: list[dict[str, int | float]],
    rows: list[dict[str, object]],
) -> None:
    candidate_fields = list(candidates[0].keys()) if candidates else []
    with CANDIDATES.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=candidate_fields)
        writer.writeheader()
        writer.writerows(candidates)
    track_fields = list(rows[0].keys()) if rows else []
    with gzip.open(TRACKS, "wt", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=track_fields)
        writer.writeheader()
        writer.writerows(rows)


def make_figure(
    h: np.ndarray,
    g: np.ndarray,
    phase: np.ndarray,
    cal: dict[str, np.ndarray],
    rows: list[dict[str, object]],
    summary: dict[str, dict[str, float | int]],
) -> None:
    exact_o = np.asarray(
        [float(row["exact_opposition"]) for row in rows], dtype=np.float64
    )
    target = float(np.nanmedian(exact_o))
    representative = rows[int(np.nanargmin(np.abs(exact_o - target)))]
    seed = int(representative["seed"])
    a_pair = int(representative["source_pair"])
    b_pair = int(representative["counterpart_pair"])
    lag = int(representative["lag"])

    fig, axes = plt.subplots(2, 2, figsize=(15, 11), constrained_layout=True)
    fig.suptitle(
        "Q35 — complete visible A loop and frozen external-counterpart test",
        fontsize=16,
        fontweight="bold",
    )

    ax = axes[0, 0]
    w_a = cal["w"][0, seed, :, a_pair]
    w_b = cal["w"][0, seed, :, b_pair]
    idx = np.arange(EVAL_START, EVAL_STOP - lag)
    ax.plot(
        w_a.real[idx],
        w_a.imag[idx],
        color="#2878b5",
        lw=1.1,
        alpha=0.78,
        label=f"visible A: seed {seed}, pair {a_pair}",
    )
    ax.plot(
        w_b.real[idx + lag],
        w_b.imag[idx + lag],
        color="#d45500",
        lw=1.1,
        alpha=0.78,
        label=f"frozen counterpart: pair {b_pair}, lag {lag}",
    )
    marker_times = idx[:: max(1, len(idx) // 12)]
    ax.scatter(
        w_a.real[marker_times],
        w_a.imag[marker_times],
        s=25,
        color="#2878b5",
        zorder=4,
    )
    ax.scatter(
        w_b.real[marker_times + lag],
        w_b.imag[marker_times + lag],
        s=30,
        marker="^",
        color="#d45500",
        zorder=4,
    )
    for time in marker_times:
        ax.plot(
            [w_a.real[time], w_b.real[time + lag]],
            [w_a.imag[time], w_b.imag[time + lag]],
            color="#3f3f3f",
            lw=0.65,
            alpha=0.38,
            linestyle="--",
        )
    ax.axhline(0, color="#8a8a8a", lw=0.8)
    ax.axvline(0, color="#8a8a8a", lw=0.8)
    ax.set_xlabel("ARA cut 1: centred relation closure")
    ax.set_ylabel("ARA cut 2: directed next-slice movement")
    ax.set_title("Two complete local loop identities (representative lineage)")
    ax.legend(frameon=False, fontsize=9)

    labels = list(VARIANTS)
    colors = ["#2b8cbe", "#9e9e9e", "#bdbdbd", "#969696", "#737373"]
    ax = axes[0, 1]
    opposition = [float(summary[v]["median_opposition"]) for v in labels]
    ax.bar(labels, opposition, color=colors)
    ax.axhline(0, color="#222222", lw=0.9)
    ax.set_ylabel("median half-turn opposition  (higher is better)")
    ax.set_title("Frozen evaluation opposition")
    ax.tick_params(axis="x", rotation=25)

    ax = axes[1, 0]
    residual = [float(summary[v]["median_parent_residual"]) for v in labels]
    ax.bar(labels, residual, color=colors)
    ax.set_ylabel("median |A + B| / 2  (lower is better)")
    ax.set_title("Parent-ridge cancellation residual")
    ax.tick_params(axis="x", rotation=25)

    ax = axes[1, 1]
    seam_x = [float(summary[v]["seam_median_counterpart_x"]) for v in labels]
    far = [100 * float(summary[v]["seam_far_pole_fraction"]) for v in labels]
    xpos = np.arange(len(labels))
    bars = ax.bar(xpos, seam_x, color=colors, alpha=0.85)
    ax.axhline(1, color="#101010", lw=1.0, label="ARA ridge display = 1")
    ax.set_ylim(0, 2)
    ax.set_ylabel("counterpart empirical ARA display coordinate")
    ax.set_xticks(xpos, labels, rotation=25)
    ax.set_title("Counterpart location when visible A touches its seam")
    for bar, value in zip(bars, far):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.04,
            f"{value:.1f}% > ridge",
            ha="center",
            va="bottom",
            fontsize=8,
        )
    ax.legend(frameon=False, fontsize=9)

    for path in (FIGURE_PNG, FIGURE_SVG):
        fig.savefig(path, dpi=180 if path.suffix == ".png" else None)
    plt.close(fig)


def main() -> None:
    required = {
        "protocol": (PROTOCOL, PROTOCOL_SHA256, "sha256"),
        "fidelity": (FIDELITY, FIDELITY_SHA256, "sha256"),
        "cache": (CACHE, CACHE_SHA256, "sha256"),
        "archive": (ARCHIVE, ARCHIVE_MD5, "md5"),
    }
    observed_hashes: dict[str, str] = {}
    for label, (path, expected, algorithm) in required.items():
        observed = digest(path, algorithm)
        observed_hashes[label] = observed
        if observed != expected:
            raise RuntimeError(f"{label} hash mismatch: {observed} != {expected}")

    derived = np.load(CACHE)
    h = np.asarray(derived["closure"], dtype=np.float64)
    if h.shape != (2, 100, 500, 66):
        raise RuntimeError(f"Unexpected closure shape {h.shape}")
    pairs = np.asarray(derived["pairs"], dtype=np.int16)

    g, phase, cal = calibration_and_phase(h)
    eligible, dev_circulation, quadrant_min = complete_loop_mask(
        phase, cal["w"]
    )
    candidates = choose_candidates(phase, eligible)

    rows: list[dict[str, object]] = []
    seam_values: dict[str, list[float]] = {name: [] for name in VARIANTS}
    seam_turns: dict[str, list[float]] = {name: [] for name in VARIANTS}

    for candidate in candidates:
        seed = int(candidate["seed"])
        source_pair = int(candidate["source_pair"])
        counterpart_pair = int(candidate["counterpart_pair"])
        pair_control = int(candidate["pair_control"])
        lag = int(candidate["lag"])
        eval_t = np.arange(EVAL_START, EVAL_STOP - lag, dtype=np.int16)

        seam_t = np.arange(EVAL_START + 1, EVAL_STOP - lag, dtype=np.int16)
        seam_mask = (
            h[0, seed, seam_t, source_pair]
            <= cal["q05"][0, seed, source_pair]
        ) & (g[0, seed, seam_t - 1, source_pair] < 0)
        seam_t = seam_t[seam_mask]
        if seam_t.size < 5:
            continue

        row: dict[str, object] = {
            **candidate,
            "source_q05": float(cal["q05"][0, seed, source_pair]),
            "source_dev_circulation": float(
                dev_circulation[seed, source_pair]
            ),
            "counterpart_dev_circulation": float(
                dev_circulation[seed, counterpart_pair]
            ),
            "source_quadrant_min_share": float(
                quadrant_min[seed, source_pair]
            ),
            "seam_events": int(seam_t.size),
        }
        a_eval = phase[0, seed, eval_t, source_pair]

        for variant in VARIANTS:
            branch, bseed, bpair, btime = b_indices(
                variant,
                seed,
                source_pair,
                counterpart_pair,
                pair_control,
                lag,
                eval_t,
            )
            b_eval = phase[branch, bseed, btime, bpair]
            opposition, residual, half_turn = phase_metrics(a_eval, b_eval)
            row[f"{variant}_opposition"] = opposition
            row[f"{variant}_residual"] = residual
            row[f"{variant}_half_turn"] = half_turn

            _, _, _, seam_btime = b_indices(
                variant,
                seed,
                source_pair,
                counterpart_pair,
                pair_control,
                lag,
                seam_t,
            )
            development = h[branch, bseed, DEV_H, bpair]
            local_x: list[float] = []
            local_turn: list[float] = []
            for time in seam_btime:
                time_i = int(time)
                local_x.append(
                    empirical_rank_ara(
                        float(h[branch, bseed, time_i, bpair]),
                        development,
                    )
                )
                local_turn.append(
                    float(
                        g[branch, bseed, time_i - 1, bpair] > 0
                        and g[branch, bseed, time_i, bpair] <= 0
                    )
                )
            seam_values[variant].extend(local_x)
            seam_turns[variant].extend(local_turn)
            row[f"{variant}_seam_median_x"] = float(np.nanmedian(local_x))
            row[f"{variant}_seam_far_fraction"] = float(
                np.nanmean(np.asarray(local_x) > 1)
            )
            row[f"{variant}_seam_turn_fraction"] = float(np.mean(local_turn))

        exact_eval_phase = phase[
            0, seed, EVAL_START:EVAL_STOP, counterpart_pair
        ]
        row["counterpart_eval_circulation"] = circulation(exact_eval_phase)
        rows.append(row)

    if not rows:
        raise RuntimeError("No Q35 lineages survived the frozen eligibility")

    summary = {
        variant: summarize_variant(
            rows, seam_values, seam_turns, variant
        )
        for variant in VARIANTS
    }
    exact_circulation = np.asarray(
        [float(row["counterpart_eval_circulation"]) for row in rows],
        dtype=np.float64,
    )
    summary["exact"]["median_evaluation_circulation"] = float(
        np.nanmedian(exact_circulation)
    )
    summary["exact"]["evaluation_circulation_ge_0_8_fraction"] = float(
        np.nanmean(exact_circulation >= 0.8)
    )

    bootstrap: dict[str, dict[str, float]] = {}
    for control in CONTROLS:
        bootstrap[control] = {
            "p_opposition_exact_gt_control": bootstrap_probability(
                rows, control, "opposition", "positive"
            ),
            "p_residual_exact_lt_control": bootstrap_probability(
                rows, control, "residual", "negative"
            ),
        }

    eligibility = {
        "development_complete_c2_loops": int(np.sum(eligible)),
        "candidate_lineages_before_seam_gate": int(len(candidates)),
        "scored_lineages_with_ge_5_seams": int(len(rows)),
        "all_scored_have_counterpart": bool(
            all(int(row["counterpart_pair"]) >= 0 for row in rows)
        ),
        "all_scored_have_ge_5_seams": bool(
            all(int(row["seam_events"]) >= 5 for row in rows)
        ),
    }
    eligibility_pass = bool(
        len(rows) >= 500
        and eligibility["all_scored_have_counterpart"]
        and eligibility["all_scored_have_ge_5_seams"]
    )

    gates: dict[str, bool] = {
        "eligibility": eligibility_pass,
        "exact_median_opposition_positive": bool(
            float(summary["exact"]["median_opposition"]) > 0
        ),
        "exact_positive_opposition_fraction_gt_0_55": bool(
            float(summary["exact"]["positive_opposition_fraction"]) > 0.55
        ),
        "exact_opposition_beats_all_controls": bool(
            all(
                float(summary["exact"]["median_opposition"])
                > float(summary[control]["median_opposition"])
                and bootstrap[control]["p_opposition_exact_gt_control"] >= 0.95
                for control in CONTROLS
            )
        ),
        "exact_residual_beats_all_controls": bool(
            all(
                float(summary["exact"]["median_parent_residual"])
                < float(summary[control]["median_parent_residual"])
                and bootstrap[control]["p_residual_exact_lt_control"] >= 0.95
                for control in CONTROLS
            )
        ),
        "exact_seam_far_pole": bool(
            float(summary["exact"]["seam_median_counterpart_x"]) > 1
            and float(summary["exact"]["seam_far_pole_fraction"]) > 0.55
            and all(
                float(summary["exact"]["seam_median_counterpart_x"])
                > float(summary[control]["seam_median_counterpart_x"])
                and float(summary["exact"]["seam_far_pole_fraction"])
                > float(summary[control]["seam_far_pole_fraction"])
                for control in CONTROLS
            )
        ),
        "counterpart_remains_complete": bool(
            float(summary["exact"]["median_evaluation_circulation"]) >= 0.8
            and float(
                summary["exact"][
                    "evaluation_circulation_ge_0_8_fraction"
                ]
            )
            >= 0.5
        ),
    }
    support_pass = bool(
        eligibility_pass
        and all(value for key, value in gates.items() if key != "eligibility")
    )
    if not eligibility_pass:
        claim_verdict = (
            "INCONCLUSIVE — INSUFFICIENT COMPLETE LOOPS OR SEAM EVENTS"
        )
    elif support_pass:
        claim_verdict = (
            "FIXED EXTERNAL PHASE-OPPOSED COUNTERPART RELATION SUPPORTED "
            "INSIDE Q34 C2"
        )
    else:
        claim_verdict = (
            "FIXED EXTERNAL COUNTERPART RELATION NOT SUPPORTED BY THIS "
            "REPRESENTATION"
        )

    exact_beats = [
        control
        for control in CONTROLS
        if float(summary["exact"]["median_opposition"])
        > float(summary[control]["median_opposition"])
    ]
    if support_pass:
        geometry_verdict = (
            "The complete-loop, external-opposite and parent-cancellation "
            "geometry all survive the frozen evaluation."
        )
    elif (
        float(summary["exact"]["median_opposition"]) > 0
        and len(exact_beats) >= 2
    ):
        geometry_verdict = (
            "A partial external-opposition geometry survives, but it does "
            "not close every frozen parent-counterpart control."
        )
    else:
        geometry_verdict = (
            "Complete local loops are present, but no uniquely preserved "
            "external parent-opposite is recovered by the frozen rule."
        )

    result = {
        "test_id": TEST_ID,
        "date": "2026-07-27",
        "design": (
            "post-hoc retrospective development/evaluation; Q34 archive and "
            "broad c2 loop already inspected"
        ),
        "source": {
            "doi": "10.5281/zenodo.16753415",
            "archive": ARCHIVE.name,
            "archive_md5": ARCHIVE_MD5,
            "cache": CACHE.name,
            "shape": list(h.shape),
            "primary_branch": "c2",
            "control_branch": "c4",
        },
        "hashes": observed_hashes,
        "frozen_parameters": {
            "development_times": [0, 249],
            "evaluation_phase_times": [250, 498],
            "lags": list(LAGS),
            "time_control_shift": TIME_SHIFT,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "bootstrap_draws": BOOTSTRAP_DRAWS,
            "loop_coherence_floor": 0.8,
            "quadrant_min_share": 0.05,
        },
        "eligibility": eligibility,
        "summary": summary,
        "bootstrap": bootstrap,
        "gates": gates,
        "support_pass": support_pass,
        "claim_verdict": claim_verdict,
        "geometry_verdict": geometry_verdict,
        "boundaries": [
            "Raw determinant closure is not the literal structural 0-2 coordinate.",
            "The empirical seam rank is a display/crosswalk coordinate only.",
            "The archive and broad c2 loop were already seen before Q35.",
            "A simulator counterpart is not a universal or hidden quantum Phase B.",
        ],
    }

    write_csvs(candidates, rows)
    make_figure(h, g, phase, cal, rows, summary)
    RESULTS.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
