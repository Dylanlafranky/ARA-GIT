"""Q36: test closed-but-deforming versus relation-loss at determinant troughs."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import os
import pathlib
import sys
from collections import defaultdict


HERE = pathlib.Path(__file__).resolve().parent
LOCAL_DEPS = HERE / ".q27_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))
os.environ.setdefault("MPLCONFIGDIR", str(HERE / ".mplconfig"))
os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt
import numpy as np


DATA = HERE / "public_data" / "q34_cross_archive_greedy"
CONNECTED_CACHE = DATA / "q34_connected_cache.npy"
DERIVED_CACHE = DATA / "q34_derived_cache.npz"
ARCHIVE = DATA / "unnati_submit_12_pure_greedy.hdf5.zip"
PROTOCOL = HERE / "Q36_CLOSED_DEFORMING_SPHERE_PROTOCOL_v1_FROZEN.md"
FIDELITY = HERE / "Q36_CLOSED_DEFORMING_SPHERE_FIDELITY_v1.md"

RESULTS = HERE / "Q36_CLOSED_DEFORMING_SPHERE_RESULTS.json"
EVENTS = HERE / "Q36_CLOSED_DEFORMING_SPHERE_EVENTS.csv.gz"
FIGURE_PNG = HERE / "Q36_CLOSED_DEFORMING_SPHERE_GEOMETRY.png"
FIGURE_SVG = HERE / "Q36_CLOSED_DEFORMING_SPHERE_GEOMETRY.svg"
METRIC_CACHE = DATA / "q36_tensor_metric_cache.npz"

PROTOCOL_SHA256 = "7ca57a9a8fcf54ae186f8f6af14597445fa1dc38b944026ab4efd832eef454e4"
FIDELITY_SHA256 = "01f4f7619f10a87bd8bf80d3a8b957dc0a1a026b39d69a3cb0e5f07b8949311d"
CONNECTED_SHA256 = "8b02fa7d186e9e6debb60b501297cf39f2d55de11511fe116775d0eb6b4abde7"
DERIVED_SHA256 = "ab32ad22e207b9913eb69352f52ba9422e18ffb9bf8304d46412d80374428e3c"
ARCHIVE_MD5 = "c1cf77ccff486e3786d73ba47f8674f1"

EPS = 1e-12
VARIANTS = ("exact", "time", "pair", "network")
CONTROLS = VARIANTS[1:]
EVAL_FIRST = 258
EVAL_LAST = 491
TIME_SHIFT = 37
BOOTSTRAP_SEED = 361027
BOOTSTRAP_DRAWS = 20_000
WINDOW_OFFSETS = np.asarray(
    list(range(-7, 0)) + list(range(1, 8)), dtype=np.int16
)


def digest(path: pathlib.Path, algorithm: str = "sha256") -> str:
    value = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def circulation(phase: np.ndarray) -> float:
    left, right = phase[:-1], phase[1:]
    valid = (
        np.isfinite(left.real)
        & np.isfinite(left.imag)
        & np.isfinite(right.real)
        & np.isfinite(right.imag)
    )
    if not np.any(valid):
        return float("nan")
    turns = np.angle(np.conj(left[valid]) * right[valid])
    turns = turns[np.abs(turns) > 1e-10]
    return float(abs(np.mean(np.sign(turns)))) if turns.size else 0.0


def complete_loop_mask(h: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Exact Q35 development-only complete-loop eligibility for c2."""
    g = np.diff(h[0], axis=1)
    dev_h = np.asarray(h[0, :, :250, :], dtype=np.float64)
    dev_g = np.asarray(g[:, :249, :], dtype=np.float64)
    q05 = np.quantile(dev_h, 0.05, axis=1)
    q95 = np.quantile(dev_h, 0.95, axis=1)
    centre = (q05 + q95) / 2
    radius = (q95 - q05) / 2
    flow = np.quantile(np.abs(dev_g), 0.95, axis=1)
    u = np.divide(
        dev_h[:, :249, :] - centre[:, None, :],
        radius[:, None, :],
        out=np.full((100, 249, 66), np.nan),
        where=radius[:, None, :] > EPS,
    )
    v = np.divide(
        dev_g,
        flow[:, None, :],
        out=np.full((100, 249, 66), np.nan),
        where=flow[:, None, :] > EPS,
    )
    w = u + 1j * v
    length = np.abs(w)
    phase = np.divide(
        w,
        length,
        out=np.full(w.shape, np.nan + 1j * np.nan),
        where=length > EPS,
    )
    eligible = np.zeros((100, 66), dtype=bool)
    coherence = np.full((100, 66), np.nan)
    for seed in range(100):
        for pair in range(66):
            p = phase[seed, :, pair]
            z = w[seed, :, pair]
            valid = (
                np.isfinite(p.real)
                & np.isfinite(p.imag)
                & np.isfinite(z.real)
                & np.isfinite(z.imag)
            )
            if np.mean(valid) < 0.95:
                continue
            quadrant = (
                2 * (z.real[valid] >= 0).astype(np.int8)
                + (z.imag[valid] >= 0).astype(np.int8)
            )
            minimum_share = min(
                float(np.mean(quadrant == q)) for q in range(4)
            )
            coherence[seed, pair] = circulation(p)
            eligible[seed, pair] = bool(
                minimum_share >= 0.05 and coherence[seed, pair] >= 0.80
            )
    return eligible, coherence


def build_metric_cache(
    h: np.ndarray,
) -> dict[str, np.ndarray]:
    if METRIC_CACHE.exists():
        cached = np.load(METRIC_CACHE)
        expected = (2, 100, 500, 66)
        if tuple(cached["amplitude"].shape) == expected:
            return {name: np.asarray(cached[name]) for name in cached.files}

    connected = np.load(CONNECTED_CACHE, mmap_mode="r")
    shape = (2, 100, 500, 66)
    amplitude = np.full(shape, np.nan, dtype=np.float32)
    lattice = np.full(shape, np.nan, dtype=np.float32)
    deform = np.full(shape, np.nan, dtype=np.float32)
    effective_rank = np.full(shape, np.nan, dtype=np.float32)
    sigma3 = np.full(shape, np.nan, dtype=np.float32)
    wobble = np.full(shape, np.nan, dtype=np.float32)

    for branch in range(2):
        for seed in range(100):
            c = np.asarray(connected[branch, seed], dtype=np.float64)
            energy = np.sum(c * c, axis=(-2, -1))
            a = np.sqrt(energy)
            singular = np.linalg.svd(c, compute_uv=False)
            probability = np.divide(
                singular * singular,
                energy[..., None],
                out=np.full(singular.shape, np.nan),
                where=energy[..., None] > EPS,
            )
            rank = np.divide(
                1.0,
                np.sum(probability * probability, axis=-1),
                out=np.full(energy.shape, np.nan),
                where=np.sum(probability * probability, axis=-1) > EPS,
            )
            lshare = np.divide(
                3.0 * np.asarray(h[branch, seed], dtype=np.float64) ** 2,
                energy,
                out=np.full(energy.shape, np.nan),
                where=energy > EPS,
            )
            lshare = np.clip(lshare, 0.0, 1.0)
            q = np.einsum("tpik,tpjk->tpij", c, c, optimize=True)
            q = np.divide(
                q,
                energy[..., None, None],
                out=np.full(q.shape, np.nan),
                where=energy[..., None, None] > EPS,
            )
            delta = q[2:] - q[:-2]
            w = np.linalg.norm(delta, axis=(-2, -1))

            amplitude[branch, seed] = a.astype(np.float32)
            lattice[branch, seed] = lshare.astype(np.float32)
            deform[branch, seed] = (1.0 - lshare).astype(np.float32)
            effective_rank[branch, seed] = rank.astype(np.float32)
            sigma3[branch, seed] = singular[..., -1].astype(np.float32)
            wobble[branch, seed, 1:499] = w.astype(np.float32)
        print(f"derived tensor metrics for branch {branch + 1}/2", flush=True)

    np.savez_compressed(
        METRIC_CACHE,
        amplitude=amplitude,
        lattice=lattice,
        deform=deform,
        effective_rank=effective_rank,
        sigma3=sigma3,
        wobble=wobble,
    )
    return {
        "amplitude": amplitude,
        "lattice": lattice,
        "deform": deform,
        "effective_rank": effective_rank,
        "sigma3": sigma3,
        "wobble": wobble,
    }


def event_times(
    h_line: np.ndarray,
    development_q20: float,
) -> list[int]:
    kept: list[int] = []
    for time in range(EVAL_FIRST, EVAL_LAST + 1):
        if not (
            h_line[time - 1] > h_line[time]
            and h_line[time] <= h_line[time + 1]
            and h_line[time] <= development_q20
        ):
            continue
        if kept and time - kept[-1] < 7:
            continue
        kept.append(time)
    return kept


def displaced_time(time: int) -> int:
    span = EVAL_LAST - EVAL_FIRST + 1
    return int(EVAL_FIRST + ((time - EVAL_FIRST + TIME_SHIFT) % span))


def local_metrics(
    branch: int,
    seed: int,
    pair: int,
    time: int,
    h: np.ndarray,
    metrics: dict[str, np.ndarray],
) -> dict[str, float]:
    local_times = time + WINDOW_OFFSETS
    local_a = np.asarray(
        metrics["amplitude"][branch, seed, local_times, pair],
        dtype=np.float64,
    )
    local_h = np.asarray(
        h[branch, seed, local_times, pair], dtype=np.float64
    )
    local_w = np.asarray(
        metrics["wobble"][branch, seed, local_times, pair],
        dtype=np.float64,
    )
    local_s3 = np.asarray(
        metrics["sigma3"][branch, seed, local_times, pair],
        dtype=np.float64,
    )
    a_base = float(np.nanmedian(local_a))
    h_base = float(np.nanmedian(local_h))
    w_base = float(np.nanmedian(local_w))
    s3_base = float(np.nanmedian(local_s3))
    a_event = float(metrics["amplitude"][branch, seed, time, pair])
    h_event = float(h[branch, seed, time, pair])
    w_event = float(metrics["wobble"][branch, seed, time, pair])
    s3_event = float(metrics["sigma3"][branch, seed, time, pair])
    r_a = a_event / a_base if a_base > EPS else float("nan")
    r_h = h_event / h_base if h_base > EPS else float("nan")
    r_w = w_event / w_base if w_base > EPS else float("nan")
    r_s3 = s3_event / s3_base if s3_base > EPS else float("nan")
    post = np.asarray(
        h[branch, seed, time + 1 : time + 8, pair],
        dtype=np.float64,
    )
    reclosure = (
        float(np.nanmax(post) / h_base) if h_base > EPS else float("nan")
    )
    return {
        "amplitude_retention": r_a,
        "closure_retention": r_h,
        "selective_gap": r_a - r_h,
        "lattice_share": float(metrics["lattice"][branch, seed, time, pair]),
        "deforming_share": float(metrics["deform"][branch, seed, time, pair]),
        "effective_rank": float(
            metrics["effective_rank"][branch, seed, time, pair]
        ),
        "weakest_axis_retention": r_s3,
        "wobble_ratio": r_w,
        "reclosure_ratio": reclosure,
        "reclosed_0_75": float(reclosure >= 0.75),
    }


def choose_pair_control(
    eligible: np.ndarray,
    seed: int,
    source_pair: int,
) -> int | None:
    choices = [
        int(pair)
        for pair in np.flatnonzero(eligible[seed])
        if int(pair) != source_pair
    ]
    if not choices:
        return None
    choices.sort(key=lambda pair: ((pair - source_pair) % 66, pair))
    return choices[0]


def cluster_probability(
    rows: list[dict[str, object]],
    exact_key: str,
    control_key: str | None = None,
) -> float:
    by_seed: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        exact = float(row[exact_key])
        comparison = float(row[control_key]) if control_key else 0.0
        if np.isfinite(exact) and np.isfinite(comparison):
            by_seed[int(row["seed"])].append(exact - comparison)
    clusters = np.asarray(
        [np.mean(by_seed[seed]) for seed in sorted(by_seed) if by_seed[seed]],
        dtype=np.float64,
    )
    rng = np.random.default_rng(
        BOOTSTRAP_SEED
        + sum(map(ord, exact_key))
        + (sum(map(ord, control_key)) if control_key else 0)
    )
    draws = rng.choice(
        clusters,
        size=(BOOTSTRAP_DRAWS, clusters.size),
        replace=True,
    ).mean(axis=1)
    return float(np.mean(draws > 0))


def variant_summary(
    rows: list[dict[str, object]],
    variant: str,
) -> dict[str, float | int]:
    def values(metric: str) -> np.ndarray:
        return np.asarray(
            [float(row[f"{variant}_{metric}"]) for row in rows],
            dtype=np.float64,
        )

    a = values("amplitude_retention")
    h = values("closure_retention")
    gap = values("selective_gap")
    d = values("deforming_share")
    w = values("wobble_ratio")
    reclose = values("reclosure_ratio")
    rank = values("effective_rank")
    s3 = values("weakest_axis_retention")
    return {
        "events": int(len(rows)),
        "median_amplitude_retention": float(np.nanmedian(a)),
        "amplitude_retention_ge_0_5_fraction": float(np.nanmean(a >= 0.5)),
        "median_closure_retention": float(np.nanmedian(h)),
        "median_selective_gap": float(np.nanmedian(gap)),
        "median_deforming_share": float(np.nanmedian(d)),
        "median_wobble_ratio": float(np.nanmedian(w)),
        "median_reclosure_ratio": float(np.nanmedian(reclose)),
        "reclosed_0_75_fraction": float(np.nanmean(reclose >= 0.75)),
        "median_effective_rank": float(np.nanmedian(rank)),
        "median_weakest_axis_retention": float(np.nanmedian(s3)),
    }


def median_path(
    rows: list[dict[str, object]],
    h: np.ndarray,
    metrics: dict[str, np.ndarray],
) -> dict[str, list[float]]:
    offsets = np.arange(-7, 8, dtype=np.int16)
    h_paths, a_paths, l_paths, d_paths = [], [], [], []
    for row in rows:
        seed = int(row["seed"])
        pair = int(row["source_pair"])
        time = int(row["time"])
        times = time + offsets
        local = time + WINDOW_OFFSETS
        h_base = np.nanmedian(h[0, seed, local, pair])
        a_base = np.nanmedian(metrics["amplitude"][0, seed, local, pair])
        h_paths.append(h[0, seed, times, pair] / h_base)
        a_paths.append(metrics["amplitude"][0, seed, times, pair] / a_base)
        l_paths.append(2.0 * metrics["lattice"][0, seed, times, pair])
        d_paths.append(2.0 * metrics["deform"][0, seed, times, pair])
    return {
        "offsets": offsets.astype(int).tolist(),
        "closure": np.nanmedian(np.asarray(h_paths), axis=0).tolist(),
        "amplitude": np.nanmedian(np.asarray(a_paths), axis=0).tolist(),
        "lattice_x": np.nanmedian(np.asarray(l_paths), axis=0).tolist(),
        "deforming_x": np.nanmedian(np.asarray(d_paths), axis=0).tolist(),
    }


def make_figure(
    summary: dict[str, dict[str, float | int]],
    path: dict[str, list[float]],
    event_count: int,
) -> None:
    colors = {
        "blue": "#2b8cbe",
        "orange": "#e07a2d",
        "gold": "#d5a62e",
        "grey": "#9b9b9b",
        "dark": "#313131",
    }
    fig, axes = plt.subplots(2, 2, figsize=(15, 10), constrained_layout=True)
    fig.suptitle(
        "Q36 — tensor magnitude, closure balance and shape motion at c2 troughs",
        fontsize=16,
        fontweight="bold",
    )
    offsets = np.asarray(path["offsets"])

    ax = axes[0, 0]
    ax.plot(
        offsets,
        path["amplitude"],
        color=colors["blue"],
        lw=2.4,
        marker="o",
        ms=4,
        label="total relation amplitude",
    )
    ax.plot(
        offsets,
        path["closure"],
        color=colors["orange"],
        lw=2.4,
        marker="s",
        ms=4,
        label="balanced determinant closure",
    )
    ax.axvline(0, color=colors["dark"], lw=1.0, linestyle="--")
    ax.axhline(1, color=colors["grey"], lw=0.8)
    ax.set_title("Median event path")
    ax.set_xlabel("slices from determinant trough")
    ax.set_ylabel("ratio to local baseline")
    ax.legend(frameon=False)

    ax = axes[0, 1]
    ax.plot(
        offsets,
        path["lattice_x"],
        color=colors["blue"],
        lw=2.4,
        label="lattice-facing share xL",
    )
    ax.plot(
        offsets,
        path["deforming_x"],
        color=colors["gold"],
        lw=2.4,
        label="deforming/mobile share xD",
    )
    ax.axvline(0, color=colors["dark"], lw=1.0, linestyle="--")
    ax.axhline(1, color=colors["grey"], lw=0.8, label="ARA ridge = 1")
    ax.set_ylim(0, 2)
    ax.set_title("TE-ARA display shares")
    ax.set_xlabel("slices from determinant trough")
    ax.set_ylabel("0–2 display coordinate")
    ax.legend(frameon=False)

    labels = list(VARIANTS)
    palette = [
        colors["blue"],
        "#b3b3b3",
        "#929292",
        "#707070",
    ]
    ax = axes[1, 0]
    gaps = [summary[name]["median_selective_gap"] for name in labels]
    ax.bar(labels, gaps, color=palette)
    ax.axhline(0, color=colors["dark"], lw=0.9)
    ax.set_title("Selective determinant loss versus total magnitude")
    ax.set_ylabel("median amplitude retention − closure retention")

    ax = axes[1, 1]
    xpos = np.arange(len(labels))
    width = 0.36
    wobble = [summary[name]["median_wobble_ratio"] for name in labels]
    reclosure = [summary[name]["median_reclosure_ratio"] for name in labels]
    ax.bar(
        xpos - width / 2,
        wobble,
        width,
        color=colors["blue"],
        label="shape wobble / local baseline",
    )
    ax.bar(
        xpos + width / 2,
        reclosure,
        width,
        color=colors["gold"],
        label="7-slice reclosure / baseline",
    )
    ax.axhline(1, color=colors["dark"], lw=0.9)
    ax.set_xticks(xpos, labels)
    ax.set_title("Shape motion and subsequent reclosure")
    ax.set_ylabel("median ratio")
    ax.legend(frameon=False)

    fig.text(
        0.5,
        0.005,
        (
            f"{event_count:,} trough events; public pure-greedy simulator. "
            "The 0–2 shares are an exact display decomposition, not independent evidence."
        ),
        ha="center",
        fontsize=9,
        color="#4a4a4a",
    )
    fig.savefig(FIGURE_PNG, dpi=180)
    fig.savefig(FIGURE_SVG)
    plt.close(fig)


def main() -> None:
    frozen = {
        "protocol": (PROTOCOL, "sha256", PROTOCOL_SHA256),
        "fidelity": (FIDELITY, "sha256", FIDELITY_SHA256),
        "connected_cache": (CONNECTED_CACHE, "sha256", CONNECTED_SHA256),
        "derived_cache": (DERIVED_CACHE, "sha256", DERIVED_SHA256),
        "archive": (ARCHIVE, "md5", ARCHIVE_MD5),
    }
    observed_hashes = {}
    for label, (path, algorithm, expected) in frozen.items():
        observed = digest(path, algorithm)
        observed_hashes[label] = observed
        if observed != expected:
            raise RuntimeError(f"{label} hash mismatch: {observed} != {expected}")

    derived = np.load(DERIVED_CACHE)
    h = np.asarray(derived["closure"], dtype=np.float64)
    if h.shape != (2, 100, 500, 66):
        raise RuntimeError(f"Unexpected closure shape {h.shape}")
    eligible, coherence = complete_loop_mask(h)
    q20 = np.quantile(h[0, :, :250, :], 0.20, axis=1)
    metrics = build_metric_cache(h)

    rows: list[dict[str, object]] = []
    for seed in range(100):
        for pair in np.flatnonzero(eligible[seed]):
            pair = int(pair)
            pair_control = choose_pair_control(eligible, seed, pair)
            if pair_control is None:
                continue
            times = event_times(h[0, seed, :, pair], float(q20[seed, pair]))
            for time in times:
                row: dict[str, object] = {
                    "seed": seed,
                    "source_pair": pair,
                    "time": time,
                    "pair_control": pair_control,
                    "development_circulation": float(coherence[seed, pair]),
                    "development_q20": float(q20[seed, pair]),
                }
                locations = {
                    "exact": (0, seed, pair, time),
                    "time": (0, seed, pair, displaced_time(time)),
                    "pair": (0, seed, pair_control, time),
                    "network": (1, seed, pair, time),
                }
                for variant, (branch, v_seed, v_pair, v_time) in locations.items():
                    measured = local_metrics(
                        branch,
                        v_seed,
                        v_pair,
                        v_time,
                        h,
                        metrics,
                    )
                    for name, value in measured.items():
                        row[f"{variant}_{name}"] = value
                rows.append(row)

    if not rows:
        raise RuntimeError("No Q36 events passed the frozen definition")

    with gzip.open(EVENTS, "wt", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        variant: variant_summary(rows, variant) for variant in VARIANTS
    }
    bootstrap = {
        "p_exact_selective_gap_gt_zero": cluster_probability(
            rows, "exact_selective_gap"
        ),
        "deforming_share": {
            control: cluster_probability(
                rows,
                "exact_deforming_share",
                f"{control}_deforming_share",
            )
            for control in CONTROLS
        },
        "wobble_ratio": {
            control: cluster_probability(
                rows,
                "exact_wobble_ratio",
                f"{control}_wobble_ratio",
            )
            for control in CONTROLS
        },
    }

    seeds = {int(row["seed"]) for row in rows}
    lineages = {
        (int(row["seed"]), int(row["source_pair"])) for row in rows
    }
    eligibility = {
        "q35_complete_c2_lineages": int(np.sum(eligible)),
        "retained_trough_events": int(len(rows)),
        "represented_seeds": int(len(seeds)),
        "represented_lineages": int(len(lineages)),
    }
    eligibility_pass = bool(
        len(rows) >= 2000 and len(seeds) >= 80 and len(lineages) >= 500
    )
    gates = {
        "eligibility": eligibility_pass,
        "median_amplitude_retention_ge_0_75": bool(
            summary["exact"]["median_amplitude_retention"] >= 0.75
        ),
        "amplitude_half_retained_in_ge_80_percent": bool(
            summary["exact"]["amplitude_retention_ge_0_5_fraction"] >= 0.80
        ),
        "selective_gap_gt_0_25_and_bootstrap": bool(
            summary["exact"]["median_selective_gap"] > 0.25
            and bootstrap["p_exact_selective_gap_gt_zero"] >= 0.99
        ),
        "deforming_share_beats_controls": bool(
            all(
                summary["exact"]["median_deforming_share"]
                > summary[control]["median_deforming_share"]
                and bootstrap["deforming_share"][control] >= 0.95
                for control in CONTROLS
            )
        ),
        "wobble_beats_controls": bool(
            summary["exact"]["median_wobble_ratio"] > 1
            and all(
                summary["exact"]["median_wobble_ratio"]
                > summary[control]["median_wobble_ratio"]
                and bootstrap["wobble_ratio"][control] >= 0.95
                for control in CONTROLS
            )
        ),
        "reclosure": bool(
            summary["exact"]["median_reclosure_ratio"] >= 0.75
            and summary["exact"]["reclosed_0_75_fraction"] >= 0.60
        ),
    }
    support_pass = bool(all(gates.values()))
    relation_loss = bool(
        eligibility_pass
        and summary["exact"]["median_amplitude_retention"] < 0.50
        and summary["exact"]["median_selective_gap"] <= 0
    )
    if not eligibility_pass:
        claim_verdict = "INCONCLUSIVE — FROZEN ELIGIBILITY GATE"
    elif support_pass:
        claim_verdict = (
            "CLOSED-BUT-DEFORMING TENSOR SIGNATURE SUPPORTED "
            "INSIDE THIS SIMULATOR"
        )
    elif relation_loss:
        claim_verdict = (
            "TROUGHS ARE MORE CONSISTENT WITH MEASURED RELATION LOSS"
        )
    else:
        claim_verdict = (
            "MIXED/INCONCLUSIVE CLOSED-DEFORMING SIGNATURE"
        )

    if support_pass:
        geometry_verdict = (
            "Balanced lattice closure falls selectively while total relation "
            "persists, normalized shape motion rises, and the same lineage "
            "re-closes."
        )
    elif relation_loss:
        geometry_verdict = (
            "Total measured relation falls with determinant closure; the "
            "wibbly-sphere account is not supported here."
        )
    else:
        geometry_verdict = (
            "Some deformation coordinates move as proposed, but the complete "
            "registered geometry does not close."
        )

    path = median_path(rows, h, metrics)
    result = {
        "test_id": "Q36-CLOSED-DEFORMING-SPHERE-v1",
        "date": "2026-07-27",
        "design": "retrospective frozen within already-open Q34/Q35 simulator",
        "source": {
            "doi": "10.5281/zenodo.16753415",
            "archive": ARCHIVE.name,
            "primary_branch": "c2",
            "network_control": "c4",
            "shape": list(h.shape),
        },
        "hashes": observed_hashes,
        "frozen_parameters": {
            "development_times": [0, 249],
            "evaluation_candidate_times": [EVAL_FIRST, EVAL_LAST],
            "trough_quantile": 0.20,
            "event_separation": 7,
            "local_window": [-7, 7],
            "time_shift": TIME_SHIFT,
            "bootstrap_seed": BOOTSTRAP_SEED,
            "bootstrap_draws": BOOTSTRAP_DRAWS,
        },
        "eligibility": eligibility,
        "summary": summary,
        "bootstrap": bootstrap,
        "gates": gates,
        "support_pass": support_pass,
        "relation_loss_pass": relation_loss,
        "claim_verdict": claim_verdict,
        "geometry_verdict": geometry_verdict,
        "median_event_path": path,
        "boundaries": [
            "xL + xD = 2 is exact bookkeeping and is not a result.",
            "The connected tensor does not directly prove topological sphere closure.",
            "Tensor magnitude is relation magnitude, not physical energy.",
            "The archive and loop geometry were already inspected before Q36.",
        ],
    }
    RESULTS.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    make_figure(summary, path, len(rows))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

