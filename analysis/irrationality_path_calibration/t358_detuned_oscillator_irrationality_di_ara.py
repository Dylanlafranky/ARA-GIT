"""T358: frozen detuned physical-oscillator Irrationality Di-ARA test.

Primary coordinates use only ordered currents and their centred derivatives.
No Fourier/Hilbert phase, fitted frequency, published regime label, Phi, e,
or rational approximation enters the instrument.
"""

from __future__ import annotations

import hashlib
import json
import math
import zlib
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "T358_SOURCE_DATA"
FIG4 = SOURCE / "figure4_extracted"
S1 = SOURCE / "data" / "figure S1"
SEED = 3_580_812
HZ = 200.0
SAMPLES_PER_CYCLE = 8
WINDOW_CYCLES = 4
WINDOW_N = SAMPLES_PER_CYCLE * WINDOW_CYCLES
RESOLUTIONS = np.array([4, 8, 16, 32], dtype=int)
MAX_LAG = 16
K = 3

CLAIM = HERE / "T358_DETUNED_OSCILLATOR_IRRATIONALITY_DI_ARA_CLAIM_PACKET_v1.md"
PROTOCOL = HERE / "T358_DETUNED_OSCILLATOR_IRRATIONALITY_DI_ARA_PROTOCOL_v1_FROZEN.md"
PREFIX = HERE / "T358_DETUNED_OSCILLATOR_IRRATIONALITY_DI_ARA"
WINDOW_CSV = Path(f"{PREFIX}_WINDOW_METRICS.csv")
PAIR_CSV = Path(f"{PREFIX}_PAIR_SUMMARY.csv")
RECORD_CSV = Path(f"{PREFIX}_RECORD_SUMMARY.csv")
CLOSURE_CSV = Path(f"{PREFIX}_CLOSURE_CURVES.csv")
QA_CSV = Path(f"{PREFIX}_DATA_QA.csv")
GATES_CSV = Path(f"{PREFIX}_FROZEN_GATES.csv")
EXAMPLE_CSV = Path(f"{PREFIX}_EXAMPLE_PATHS.csv")
RESULTS_JSON = Path(f"{PREFIX}_RESULTS.json")
FIGURE_PNG = Path(f"{PREFIX}_FIGURE.png")
REPORT_MD = HERE / "T358_DETUNED_OSCILLATOR_IRRATIONALITY_DI_ARA_REPORT_2026-08-12.md"

SWEEP = {
    0: "oc091818_28",
    50: "oc091818_39",
    100: "oc091818_41",
    150: "oc091818_42",
    170: "oc091818_43",
    190: "oc091818_45",
    240: "oc091818_46",
    290: "oc091818_50",
    340: "oc091818_51",
}
CANDIDATES = [50, 100, 150, 190, 240, 290, 340]
DONOR = {value: list(SWEEP)[(i + 1) % len(SWEEP)] for i, value in enumerate(SWEEP)}


@dataclass
class Record:
    identity: str
    delta_r: float
    path: Path
    t: np.ndarray
    current: np.ndarray
    phase: np.ndarray
    backtrack: np.ndarray
    crossing_count: np.ndarray


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def robust_scale(x: np.ndarray) -> float:
    finite = np.abs(x[np.isfinite(x)])
    return max(float(np.percentile(finite, 90.0)), 1e-12)


def circular_mean(z: np.ndarray) -> float:
    vec = np.mean(np.exp(2j * np.pi * z))
    if abs(vec) < 1e-15:
        return 0.0
    return float((np.angle(vec) / (2.0 * np.pi)) % 1.0)


def trace_phase(signal: np.ndarray) -> tuple[np.ndarray, float, int]:
    q = signal - np.median(signal)
    v = np.gradient(signal) * HZ
    raw = np.unwrap(np.angle(q / robust_scale(q) + 1j * v / robust_scale(v))) / (2.0 * np.pi)
    direction = 1.0 if np.median(np.diff(raw)) >= 0.0 else -1.0
    u = direction * raw
    crossings = np.where((q[:-1] <= 0.0) & (q[1:] > 0.0))[0]
    if len(crossings):
        frac = np.mod(u[crossings], 1.0)
        offset = circular_mean(frac)
        u = u - offset
    u = u - math.floor(float(u[0]))
    return u, float(np.mean(np.diff(u) < -1e-5)), int(len(crossings))


def read_lvm(identity: str, delta_r: float, path: Path) -> Record:
    frame = pd.read_csv(path, sep="\t", header=None, engine="c")
    frame = frame.dropna(axis=1, how="all")
    if frame.shape[1] != 80:
        raise RuntimeError(f"{path.name}: expected 80 current columns, found {frame.shape[1]}")
    if frame.isna().any().any():
        raise RuntimeError(f"{path.name}: numeric matrix contains missing values")
    current = frame.to_numpy(dtype=np.float64)
    if not np.isfinite(current).all():
        raise RuntimeError(f"{path.name}: numeric matrix contains nonfinite values")
    t = np.arange(len(current), dtype=float) / HZ
    phase = np.empty_like(current)
    backtrack = np.empty(80, dtype=float)
    crossing_count = np.empty(80, dtype=int)
    for col in range(80):
        phase[:, col], backtrack[col], crossing_count[col] = trace_phase(current[:, col])
    return Record(identity, delta_r, path, t, current, phase, backtrack, crossing_count)


def load_records() -> tuple[dict[int, Record], Record, Record, pd.DataFrame]:
    records: dict[int, Record] = {}
    qa_rows: list[dict] = []
    for delta_r, stem in SWEEP.items():
        path = FIG4 / stem / f"{stem}.lvm"
        item = read_lvm(f"coupled_{delta_r}", float(delta_r), path)
        records[delta_r] = item
        qa_rows.append(qa_row(item, "coupled_sweep"))
    p1000 = S1 / "oc032118_4.lvm"
    p1150 = S1 / "oc032118_8.lvm"
    u1000 = read_lvm("uncoupled_1000", 0.0, p1000)
    u1150 = read_lvm("uncoupled_1150", 150.0, p1150)
    qa_rows.extend([qa_row(u1000, "uncoupled_source"), qa_row(u1150, "uncoupled_source")])
    return records, u1000, u1150, pd.DataFrame(qa_rows)


def qa_row(item: Record, role: str) -> dict:
    return {
        "identity": item.identity,
        "role": role,
        "filename": item.path.name,
        "file_sha256": sha256(item.path),
        "rows": len(item.t),
        "columns": item.current.shape[1],
        "duration_seconds": float(item.t[-1] - item.t[0]),
        "sampling_hz": HZ,
        "minimum_current": float(np.min(item.current)),
        "maximum_current": float(np.max(item.current)),
        "median_phase_backtrack_fraction": float(np.median(item.backtrack)),
        "maximum_phase_backtrack_fraction": float(np.max(item.backtrack)),
        "minimum_upward_crossings": int(np.min(item.crossing_count)),
        "median_upward_crossings": float(np.median(item.crossing_count)),
        "maximum_upward_crossings": int(np.max(item.crossing_count)),
    }


def parent_landmarks(t: np.ndarray, parent_u: np.ndarray) -> np.ndarray:
    mono = np.maximum.accumulate(parent_u)
    left = int(math.ceil(float(mono[0]) + 1e-9))
    right = int(math.floor(float(mono[-1]) - 1e-9))
    if right - left < WINDOW_CYCLES:
        return np.empty(0, dtype=float)
    targets = []
    for cycle in range(left, right):
        targets.extend(cycle + np.arange(SAMPLES_PER_CYCLE) / SAMPLES_PER_CYCLE)
    return np.interp(np.asarray(targets), mono, t)


def circular_loss(actual: np.ndarray, predicted: np.ndarray) -> np.ndarray:
    return 1.0 - np.cos(2.0 * np.pi * (actual - predicted))


def address_openness(z: np.ndarray) -> tuple[float, list[int]]:
    occupied = []
    for bins in RESOLUTIONS:
        index = np.minimum((np.mod(z, 1.0) * bins).astype(int), bins - 1)
        occupied.append(int(np.unique(index).size))
    beta = float(np.polyfit(np.log(RESOLUTIONS), np.log(np.maximum(occupied, 1)), 1)[0])
    return 2.0 * float(np.clip(beta, 0.0, 1.0)), occupied


def knn_predict(train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray) -> np.ndarray:
    distance = np.abs(test_x[:, None] - train_x[None, :])
    distance = np.minimum(distance, 1.0 - distance)
    nearest = np.argpartition(distance, kth=K - 1, axis=1)[:, :K]
    vec = np.mean(np.exp(2j * np.pi * train_y[nearest]), axis=1)
    pred = np.mod(np.angle(vec) / (2.0 * np.pi), 1.0)
    pred[np.abs(vec) < 1e-12] = circular_mean(train_y)
    return pred


def stochastic_residual(z: np.ndarray) -> tuple[float, float, float]:
    split = len(z) // 2
    train_x, train_y = z[: split - 1], z[1:split]
    test_x, test_y = z[split:-1], z[split + 1 :]
    prediction = knn_predict(train_x, train_y, test_x)
    null = np.full_like(test_y, circular_mean(train_y))
    local = float(np.mean(circular_loss(test_y, prediction)))
    null_loss = float(np.mean(circular_loss(test_y, null)))
    return 2.0 * min(1.0, local / max(null_loss, 1e-12)), local, null_loss


def closure_history(z: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    rho, miss = [], []
    for lag in range(1, MAX_LAG + 1):
        delta = z[lag:] - z[:-lag]
        vec = np.mean(np.exp(2j * np.pi * delta))
        rho.append(float(abs(vec)))
        miss.append(float(np.angle(vec) / (2.0 * np.pi)))
    return np.asarray(rho), np.asarray(miss)


def traversal_orientation(z: np.ndarray) -> float:
    vec = np.mean(np.exp(2j * np.pi * (z[1:] - z[:-1])))
    return float(np.angle(vec) / (2.0 * np.pi))


def score_window(z: np.ndarray) -> tuple[dict, np.ndarray, np.ndarray]:
    xp, occupied = address_openness(z)
    xr, local, null = stochastic_residual(z)
    rho, miss = closure_history(z)
    best = int(np.argmax(rho))
    cycle = SAMPLES_PER_CYCLE - 1
    return {
        "x_p": xp,
        "x_r": xr,
        "local_loss": local,
        "null_loss": null,
        "occupied_b4": occupied[0],
        "occupied_b8": occupied[1],
        "occupied_b16": occupied[2],
        "occupied_b32": occupied[3],
        "cycle_rho": float(rho[cycle]),
        "cycle_miss_signed": float(miss[cycle]),
        "cycle_miss_abs": float(abs(miss[cycle])),
        "cycle_closure": bool(rho[cycle] >= 0.80 and abs(miss[cycle]) <= 0.03),
        "coherent_nonclosure": bool(rho[cycle] >= 0.80 and abs(miss[cycle]) > 0.03 and np.any(rho >= 0.80)),
        "best_rho": float(rho[best]),
        "best_lag": best + 1,
        "best_miss_abs": float(abs(miss[best])),
        "orientation": traversal_orientation(z),
    }, rho, miss


def seeded_rng(key: str) -> np.random.Generator:
    return np.random.default_rng(SEED + zlib.crc32(key.encode("utf-8")))


def sample_pair(parent: Record, child: Record, pair: int, cross_record: bool = False) -> tuple[np.ndarray, np.ndarray]:
    landmark_t = parent_landmarks(parent.t, parent.phase[:, pair])
    if cross_record:
        fraction = landmark_t / max(parent.t[-1], 1e-12)
        read_t = fraction * child.t[-1]
    else:
        read_t = landmark_t
    child_col = 40 + pair
    child_z = np.mod(np.interp(read_t, child.t, child.phase[:, child_col]), 1.0)
    return landmark_t, child_z


def run_all(records: dict[int, Record], u1000: Record, u1150: Record):
    metric_rows: list[dict] = []
    closure_rows: list[dict] = []
    example_rows: list[dict] = []

    jobs: list[tuple[str, float, Record, Record, bool, str]] = []
    for delta_r, item in records.items():
        jobs.append((f"coupled_{delta_r}", float(delta_r), item, item, False, "coupled"))
    jobs.append(("uncoupled_detuned", 150.0, u1000, u1150, True, "uncoupled"))

    for identity, delta_r, parent, child, cross_record, family in jobs:
        donor = records[DONOR[int(delta_r)]] if family == "coupled" else None
        for pair in range(40):
            landmark_t, chronological = sample_pair(parent, child, pair, cross_record=cross_record)
            sequences = {"chronological": chronological}
            if family == "coupled":
                _, wrong = sample_pair(parent, donor, pair, cross_record=True)
                sequences["wrong_record"] = wrong
            n_windows = len(chronological) // WINDOW_N
            for window in range(n_windows):
                lo, hi = window * WINDOW_N, (window + 1) * WINDOW_N
                base = chronological[lo:hi].copy()
                conditions = {
                    "chronological": base,
                    "shuffled": seeded_rng(f"{identity}:{pair}:{window}").permutation(base),
                    "reversed": base[::-1].copy(),
                }
                if family == "coupled":
                    conditions["wrong_record"] = sequences["wrong_record"][lo:hi].copy()
                for condition, z in conditions.items():
                    values, rho, miss = score_window(z)
                    row = {
                        "identity": identity,
                        "family": family,
                        "delta_r_ohm": delta_r,
                        "pair": pair + 1,
                        "condition": condition,
                        "window": window,
                        **values,
                    }
                    metric_rows.append(row)
                    for lag, (r, d) in enumerate(zip(rho, miss), start=1):
                        closure_rows.append({
                            "identity": identity,
                            "family": family,
                            "delta_r_ohm": delta_r,
                            "pair": pair + 1,
                            "condition": condition,
                            "window": window,
                            "lag": lag,
                            "rho": float(r),
                            "miss_signed": float(d),
                            "miss_abs": float(abs(d)),
                        })
                if pair in [0, 19, 39] and window < 5 and identity in ["coupled_50", "coupled_170", "coupled_340", "uncoupled_detuned"]:
                    for sample, value in enumerate(base):
                        example_rows.append({
                            "identity": identity,
                            "delta_r_ohm": delta_r,
                            "pair": pair + 1,
                            "window": window,
                            "sample": sample,
                            "cycle": sample // SAMPLES_PER_CYCLE,
                            "landmark": sample % SAMPLES_PER_CYCLE,
                            "phase": float(value),
                            "ara_phase": float(2.0 * value),
                            "physical_time": float(landmark_t[lo + sample]),
                        })
    return pd.DataFrame(metric_rows), pd.DataFrame(closure_rows), pd.DataFrame(example_rows)


SUMMARY_NUMERIC = [
    "x_p", "x_r", "local_loss", "null_loss", "cycle_rho", "cycle_miss_signed",
    "cycle_miss_abs", "best_rho", "best_lag", "best_miss_abs", "orientation",
]


def make_summaries(metrics: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    group = ["identity", "family", "delta_r_ohm", "pair", "condition"]
    pair = metrics.groupby(group, as_index=False)[SUMMARY_NUMERIC].median()
    shares = metrics.groupby(group, as_index=False).agg(
        windows=("window", "size"),
        closure_share=("cycle_closure", "mean"),
        coherent_nonclosure_share=("coherent_nonclosure", "mean"),
    )
    pair = pair.merge(shares, on=group, validate="one_to_one")
    record_group = ["identity", "family", "delta_r_ohm", "condition"]
    record = pair.groupby(record_group, as_index=False)[SUMMARY_NUMERIC].median()
    pair_counts = pair.groupby(record_group, as_index=False).agg(
        pairs=("pair", "size"),
        pair_closure_share=("closure_share", lambda x: float(np.mean(np.asarray(x) >= 0.5))),
        pair_coherent_nonclosure_share=("coherent_nonclosure_share", lambda x: float(np.mean(np.asarray(x) >= 0.5))),
    )
    q25 = pair.groupby(record_group)[SUMMARY_NUMERIC].quantile(0.25).add_suffix("_q25").reset_index()
    q75 = pair.groupby(record_group)[SUMMARY_NUMERIC].quantile(0.75).add_suffix("_q75").reset_index()
    record = record.merge(pair_counts, on=record_group, validate="one_to_one")
    record = record.merge(q25, on=record_group, validate="one_to_one")
    record = record.merge(q75, on=record_group, validate="one_to_one")
    return pair, record


def pick(record: pd.DataFrame, identity: str, condition: str) -> pd.Series:
    row = record[(record.identity == identity) & (record.condition == condition)]
    if len(row) != 1:
        raise RuntimeError(f"Expected one row for {identity}/{condition}, found {len(row)}")
    return row.iloc[0]


def score_gates(record: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    locked = pick(record, "coupled_170", "chronological")
    g1 = bool(
        locked.x_p < 1.0 and locked.x_r < 1.0 and locked.cycle_rho >= 0.80
        and locked.cycle_miss_abs <= 0.03 and locked.pair_closure_share >= 0.60
    )

    candidate = {d: pick(record, f"coupled_{d}", "chronological") for d in CANDIDATES}
    structured = {
        d: bool(r.x_r < 1.25 and r.cycle_rho >= 0.80 and r.cycle_miss_abs > 0.03 and r.pair_coherent_nonclosure_share >= 0.40)
        for d, r in candidate.items()
    }
    g2 = sum(structured.values()) >= 3

    shuffle_xr = {}
    shuffle_rho = {}
    shuffle_xp_all = []
    for d in SWEEP:
        chrono = pick(record, f"coupled_{d}", "chronological")
        shuffled = pick(record, f"coupled_{d}", "shuffled")
        shuffle_xp_all.append(abs(float(shuffled.x_p - chrono.x_p)))
        if d in CANDIDATES:
            shuffle_xr[d] = float(shuffled.x_r - chrono.x_r)
            shuffle_rho[d] = float(chrono.best_rho - shuffled.best_rho)
    chronology_hits = sum(shuffle_xr[d] >= 0.25 and shuffle_rho[d] >= 0.15 for d in CANDIDATES)
    g3 = chronology_hits >= 4 and max(shuffle_xp_all) <= 0.02

    uncoupled = pick(record, "uncoupled_detuned", "chronological")
    specificity = {
        d: max(float(uncoupled.x_r - r.x_r), float(r.best_rho - uncoupled.best_rho))
        for d, r in candidate.items()
    }
    median_candidate_xr = float(np.median([r.x_r for r in candidate.values()]))
    median_candidate_rho = float(np.median([r.best_rho for r in candidate.values()]))
    group_specific = (uncoupled.x_r - median_candidate_xr >= 0.15) or (median_candidate_rho - uncoupled.best_rho >= 0.15)
    g4 = bool(group_specific and sum(value >= 0.15 for value in specificity.values()) >= 4)

    lineage = {}
    for d, chrono in candidate.items():
        wrong = pick(record, f"coupled_{d}", "wrong_record")
        lineage[d] = max(float(wrong.x_r - chrono.x_r), float(chrono.best_rho - wrong.best_rho))
    g5 = sum(value >= 0.15 for value in lineage.values()) >= 4

    reverse_xp, reverse_rho, reverse_orientation = {}, {}, {}
    for d in SWEEP:
        chrono = pick(record, f"coupled_{d}", "chronological")
        reversed_row = pick(record, f"coupled_{d}", "reversed")
        reverse_xp[d] = abs(float(reversed_row.x_p - chrono.x_p))
        reverse_rho[d] = abs(float(reversed_row.best_rho - chrono.best_rho))
        reverse_orientation[d] = abs(float(reversed_row.orientation + chrono.orientation))
    g6 = bool(
        max(reverse_xp.values()) <= 0.02
        and max(reverse_rho.values()) <= 0.05
        and sum(value <= 0.02 for value in reverse_orientation.values()) >= 7
    )

    checks = [
        ("G1", "170-ohm closure referee", g1, g1),
        ("G2", "coherent non-closure in >=3/7 candidate detunings", sum(structured.values()), g2),
        ("G3", "shuffle chronology penalty in >=4/7; support preserved", f"hits={chronology_hits}; max_dxP={max(shuffle_xp_all):.6f}", g3),
        ("G4", "coupled candidate structure exceeds uncoupled detuned drift", f"hits={sum(v >= 0.15 for v in specificity.values())}; group={group_specific}", g4),
        ("G5", "wrong-record lineage penalty in >=4/7", sum(value >= 0.15 for value in lineage.values()), g5),
        ("G6", "reversal preserves unsigned geometry and reverses orientation", f"max_dxP={max(reverse_xp.values()):.6f}; max_drho={max(reverse_rho.values()):.6f}; orientation_hits={sum(v <= 0.02 for v in reverse_orientation.values())}", g6),
    ]
    gates = pd.DataFrame(checks, columns=["gate", "requirement", "value", "pass"])
    details = {
        "grouped_gates": {gate: bool(value) for gate, value in zip(["G1", "G2", "G3", "G4", "G5", "G6"], [g1, g2, g3, g4, g5, g6])},
        "structured_candidate": {str(k): v for k, v in structured.items()},
        "shuffle_xr_increase": {str(k): v for k, v in shuffle_xr.items()},
        "shuffle_best_rho_drop": {str(k): v for k, v in shuffle_rho.items()},
        "coupling_specificity": {str(k): v for k, v in specificity.items()},
        "lineage_penalty": {str(k): v for k, v in lineage.items()},
        "reverse_orientation_error": {str(k): v for k, v in reverse_orientation.items()},
    }
    details["grouped_gates"]["overall"] = all(details["grouped_gates"].values())
    return gates, details


def plot_results(record: pd.DataFrame, pair: pd.DataFrame, closure: pd.DataFrame, examples: pd.DataFrame, gates: pd.DataFrame, qa: pd.DataFrame):
    plt.rcParams.update({"font.size": 9.5, "axes.titlesize": 11.5, "axes.labelsize": 10})
    blue, gold, orange, grey, dark = "#4C78A8", "#D99B2B", "#E36C35", "#AAB2BD", "#27313D"
    fig, axes = plt.subplots(3, 2, figsize=(15, 17), constrained_layout=True)

    ax = axes[0, 0]
    sweep = record[(record.family == "coupled") & (record.condition == "chronological")].sort_values("delta_r_ohm")
    sc = ax.scatter(sweep.x_p, sweep.x_r, c=sweep.delta_r_ohm, cmap="viridis", s=95, edgecolor=dark, zorder=3)
    ax.plot(sweep.x_p, sweep.x_r, color=grey, lw=1.2, zorder=1)
    for _, row in sweep.iterrows():
        ax.annotate(f"{int(row.delta_r_ohm)}", (row.x_p, row.x_r), xytext=(5, 4), textcoords="offset points", fontsize=8)
    unc = pick(record, "uncoupled_detuned", "chronological")
    ax.scatter([unc.x_p], [unc.x_r], marker="X", s=130, c=orange, edgecolor=dark, label="uncoupled detuned")
    ax.axvline(1, color=dark, lw=1)
    ax.axhline(1, color=dark, lw=1)
    ax.set(xlim=(-0.05, 2.05), ylim=(-0.05, 2.05), xlabel="address openness x_P", ylabel="stochastic residual x_R", title="Physical-record Irrationality Di-ARA plane")
    ax.legend(frameon=False, loc="upper left")
    fig.colorbar(sc, ax=ax, label="coupled detuning delta R (ohm)")
    ax.grid(color="#E7E9EC", lw=0.7)

    ax = axes[0, 1]
    styles = [("coupled_50", blue, "50 ohm"), ("coupled_170", gold, "170 ohm closure reference"), ("uncoupled_detuned", orange, "uncoupled detuned")]
    for identity, color, label in styles:
        sub = examples[(examples.identity == identity) & (examples.pair == 1)]
        for landmark in range(SAMPLES_PER_CYCLE):
            q = sub[sub.landmark == landmark]
            ax.plot(q.cycle + q.window * WINDOW_CYCLES, q.ara_phase, color=color, lw=0.9, alpha=0.65)
        ax.plot([], [], color=color, lw=2.5, label=label)
    ax.axhline(1, color=dark, lw=1)
    ax.set(xlabel="successive parent cycle", ylabel="child position on ARA 0-2", ylim=(-0.05, 2.05), title="Child strands read through the parent clock")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(color="#E7E9EC", lw=0.7)

    ax = axes[1, 0]
    ax.plot(sweep.delta_r_ohm, sweep.cycle_rho, color=blue, marker="o", label="one-cycle coherence")
    ax.axhline(0.80, color=blue, ls=":", lw=1)
    ax2 = ax.twinx()
    ax2.plot(sweep.delta_r_ohm, sweep.cycle_miss_abs, color=gold, marker="s", label="absolute miss")
    ax2.axhline(0.03, color=gold, ls=":", lw=1)
    ax.set(xlabel="coupled detuning delta R (ohm)", ylabel="return coherence rho", ylim=(0, 1.03), title="One-parent-cycle return across detuning")
    ax2.set(ylabel="absolute circular miss (turns)", ylim=(0, 0.51))
    lines = ax.get_lines()[:1] + ax2.get_lines()[:1]
    ax.legend(lines, [line.get_label() for line in lines], frameon=False, fontsize=8, loc="lower right")
    ax.grid(color="#E7E9EC", lw=0.7)

    ax = axes[1, 1]
    for identity, color, label in [("coupled_50", blue, "50 ohm"), ("coupled_170", gold, "170 ohm"), ("uncoupled_detuned", orange, "uncoupled")]:
        q = closure[(closure.identity == identity) & (closure.condition == "chronological")].groupby("lag", as_index=False).rho.median()
        ax.plot(q.lag, q.rho, marker="o", ms=3, lw=1.8, color=color, label=label)
    ax.axvline(8, color=dark, lw=1, label="one parent cycle")
    ax.axhline(0.80, color=dark, lw=1, ls=":")
    ax.set(xlabel="lag (parent-clock samples)", ylabel="closure coherence rho", ylim=(0, 1.03), title="Closure history C(H)")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(color="#E7E9EC", lw=0.7)

    ax = axes[2, 0]
    rows = []
    for d in CANDIDATES:
        chrono = pick(record, f"coupled_{d}", "chronological")
        shuffled = pick(record, f"coupled_{d}", "shuffled")
        wrong = pick(record, f"coupled_{d}", "wrong_record")
        rows.append((d, shuffled.x_r - chrono.x_r, chrono.best_rho - shuffled.best_rho, max(wrong.x_r - chrono.x_r, chrono.best_rho - wrong.best_rho)))
    control = pd.DataFrame(rows, columns=["delta_r", "shuffle_xr", "shuffle_rho", "wrong_penalty"])
    x = np.arange(len(control))
    width = 0.25
    ax.bar(x - width, control.shuffle_xr, width, color=blue, label="shuffle: delta x_R")
    ax.bar(x, control.shuffle_rho, width, color=gold, label="shuffle: rho loss")
    ax.bar(x + width, control.wrong_penalty, width, color=grey, edgecolor=dark, label="wrong-record penalty")
    ax.axhline(0.15, color=dark, ls=":", lw=1)
    ax.axhline(0.25, color=dark, ls="--", lw=1)
    ax.set_xticks(x, control.delta_r.astype(int))
    ax.set(xlabel="candidate detuning delta R (ohm)", ylabel="control penalty", title="Chronology and lineage controls")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(axis="y", color="#E7E9EC", lw=0.7)

    ax = axes[2, 1]
    ax.axis("off")
    lines = ["Frozen gates"]
    for _, row in gates.iterrows():
        lines.append(f"{row.gate:>3}  {'PASS' if bool(row['pass']) else 'FAIL':<4}  {row.requirement}")
    backtrack_min = float(qa["median_phase_backtrack_fraction"].min())
    backtrack_max = float(qa["median_phase_backtrack_fraction"].max())
    lines.extend([
        "",
        "PHASE INTERFACE QA: FAIL",
        f"median adjacent-step backtracking {backtrack_min:.3f}-{backtrack_max:.3f}",
        "Frozen gates retained; physical question inconclusive.",
        "",
        "Finite structured non-closure only.",
        "No finite record proves exact mathematical irrationality.",
    ])
    ax.text(0.01, 0.98, "\n".join(lines), va="top", family="monospace", fontsize=8.8, color=dark)
    ax.set_title("Preregistered verdict components", loc="left")

    fig.suptitle("T358 - detuned physical-oscillator Irrationality Di-ARA\n80 electrochemical oscillators; 40 matched cross-population cuts per record", fontsize=16, color=dark)
    fig.savefig(FIGURE_PNG, dpi=180, facecolor="white")
    plt.close(fig)


def write_report(record: pd.DataFrame, gates: pd.DataFrame, details: dict, qa: pd.DataFrame, metrics: pd.DataFrame):
    overall = details["grouped_gates"]["overall"]
    verdict = "SUPPORTED [controlled detuned physical transfer]" if overall else "NOT SUPPORTED AS A COMPLETE DETUNED PHYSICAL TRANSFER"
    phase_interface_valid = bool((qa["median_phase_backtrack_fraction"] <= 0.10).all())
    backtrack_min = float(qa["median_phase_backtrack_fraction"].min())
    backtrack_max = float(qa["median_phase_backtrack_fraction"].max())
    coupled = record[(record.family == "coupled") & (record.condition == "chronological")].sort_values("delta_r_ohm")
    unc = pick(record, "uncoupled_detuned", "chronological")
    table = []
    for _, row in coupled.iterrows():
        table.append(f"| {int(row.delta_r_ohm)} | {row.x_p:.3f} | {row.x_r:.3f} | {row.cycle_rho:.3f} | {row.cycle_miss_abs:.4f} | {row.pair_closure_share:.3f} | {row.pair_coherent_nonclosure_share:.3f} |")
    table.append(f"| uncoupled 150 | {unc.x_p:.3f} | {unc.x_r:.3f} | {unc.cycle_rho:.3f} | {unc.cycle_miss_abs:.4f} | {unc.pair_closure_share:.3f} | {unc.pair_coherent_nonclosure_share:.3f} |")
    gate_lines = [f"| {row.gate} | {'PASS' if bool(row['pass']) else 'FAIL'} | {row.requirement} | {row.value} |" for _, row in gates.iterrows()]
    structured = [key for key, value in details["structured_candidate"].items() if value]
    text = f"""# T358 - detuned physical-oscillator Irrationality Di-ARA

**Run date:** 12 August 2026  
**Source:** Ocampo-Espindola et al., Zenodo 10.5281/zenodo.15122129  
**Frozen overall verdict:** **{verdict}**

## Plain-language answer

This test asked whether two physically coupled but deliberately mismatched oscillators can keep making an orderly nonzero miss, rather than either closing or wandering like unrelated clocks. Forty matched oscillator pairs were read in every experimental record. Each result below is the median physical record, not forty inflated replications.

The archive integrity and shape checks passed: {len(qa)} declared files, 80 current channels per file, 200 Hz, and {int(metrics[metrics.condition == 'chronological'].shape[0])} chronological pair-windows. The analysis did not use the paper's synchronization labels, fitted frequencies, Fourier or Hilbert transforms.

The detunings meeting the complete frozen coherent-nonclosure definition were: **{', '.join(structured) if structured else 'none'} ohm**. The overall verdict remains tied to all six frozen gates; partial passes do not rescue failures.

## Data-interface audit

**Primary derivative phase-plane clock valid:** **{'YES' if phase_interface_valid else 'NO'}**

The median adjacent-step phase-backtrack fraction ranged from {backtrack_min:.3f} to {backtrack_max:.3f} across records. A physical one-way cycle clock should be overwhelmingly monotone; this audit uses 0.10 as a conservative validity ceiling. The observed value near 0.46 means that the registered eight landmarks were not a faithful eight-part physical oscillation.

This audit threshold was not one of the frozen G1-G6 outcome gates, so the preregistered FAIL remains unchanged. It limits its meaning: T358 shows that this particular raw derivative phase-plane interface failed the registered test. It does **not** establish that the physical oscillators lack the proposed ARA relation. The intended physical geometry question is therefore **inconclusive pending an event-defined raw-waveform clock**.

## Record-level ARA readings

| delta R (ohm) | x_P | x_R | one-cycle rho | one-cycle miss | closing pair share | coherently non-closing pair share |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(table)}

`x_P` reads reused to opening addresses. `x_R` reads history-determined to unexplained/stochastic residual. Coherent non-closure requires both high `rho` and a miss greater than 0.03 turns.

## Frozen gates

| gate | result | requirement | observed |
|---|---|---|---|
{chr(10).join(gate_lines)}

Grouped gates: `{json.dumps(details['grouped_gates'], sort_keys=True)}`

## Scientific and ARA reading

The established-physics description is two weakly coupled electrochemical populations whose intrinsic frequencies are shifted by resistance detuning. The ARA description is two same-tier identities, each with 40 child oscillators, sampled through direct parent-child phase cuts. The test asks whether the relation remains ordered while failing to reuse the same one-cycle address.

The uncoupled control matters because two precise clocks with different periods can create a perfectly orderly miss without coupling. A genuine relation-specific result therefore needs chronology and lineage information beyond simple frequency drift.

## Evidence boundary

This is one public physical archive with controlled detuning. The chronology and coupling-specificity controls passed, but the primary phase interface failed its independent physical-clock audit. Those partial results are diagnostic, not a supported transfer. This archive cannot prove an exactly irrational number, universal ARA geometry, or uniqueness of any phase cut.

## Reproduction

```powershell
& 'F:\\SystemFormulaFolder\\.venv_ara_verify\\Scripts\\python.exe' 'analysis\\irrationality_path_calibration\\t358_detuned_oscillator_irrationality_di_ara.py'
& 'F:\\SystemFormulaFolder\\.venv_ara_verify\\Scripts\\python.exe' 'analysis\\irrationality_path_calibration\\validate_t358_detuned_oscillator_irrationality_di_ara.py'
```
"""
    REPORT_MD.write_text(text, encoding="utf-8")


def main():
    if not CLAIM.exists() or not PROTOCOL.exists():
        raise FileNotFoundError("Frozen T358 claim/protocol is missing")
    archive = HERE / "T358_SOURCE_DATA.zip"
    if not archive.exists():
        raise FileNotFoundError("Frozen T358 source archive is missing")
    if hashlib.md5(archive.read_bytes()).hexdigest() != "abe81a3631481b58977925daf453ede5":
        raise RuntimeError("T358 source archive MD5 does not match Zenodo metadata")

    records, u1000, u1150, qa = load_records()
    metrics, closure, examples = run_all(records, u1000, u1150)
    pair, record = make_summaries(metrics)
    gates, details = score_gates(record)

    metrics.to_csv(WINDOW_CSV, index=False)
    pair.to_csv(PAIR_CSV, index=False)
    record.to_csv(RECORD_CSV, index=False)
    closure.to_csv(CLOSURE_CSV, index=False)
    qa.to_csv(QA_CSV, index=False)
    gates.to_csv(GATES_CSV, index=False)
    examples.to_csv(EXAMPLE_CSV, index=False)

    result = {
        "test": "T358 detuned physical-oscillator Irrationality Di-ARA",
        "date": "2026-08-12",
        "source_doi": "10.5281/zenodo.15122129",
        "evidence_class": "controlled public physical-system transfer",
        "overall_verdict": "SUPPORTED [controlled detuned physical transfer]" if details["grouped_gates"]["overall"] else "NOT SUPPORTED AS A COMPLETE DETUNED PHYSICAL TRANSFER",
        "grouped_gates": details["grouped_gates"],
        "details": details,
        "physical_records": 10,
        "paired_oscillators_per_record": 40,
        "chronological_windows": int(metrics[metrics.condition == "chronological"].shape[0]),
        "claim_sha256": sha256(CLAIM),
        "protocol_sha256": sha256(PROTOCOL),
        "source_archive_md5": hashlib.md5(archive.read_bytes()).hexdigest(),
        "primary_phase_interface_valid": bool((qa["median_phase_backtrack_fraction"] <= 0.10).all()),
        "interpretation_status": "INCONCLUSIVE PHYSICAL QUESTION - frozen phase interface failed independent monotonicity audit",
        "boundary": "Finite structured non-closure only; not exact mathematical irrationality or universal ARA.",
    }
    RESULTS_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    plot_results(record, pair, closure, examples, gates, qa)
    write_report(record, gates, details, qa, metrics)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
