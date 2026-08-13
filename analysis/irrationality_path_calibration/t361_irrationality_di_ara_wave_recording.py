"""T361: frozen Irrationality Di-ARA wave recording and recovery test.

The recorder retains raw 0-2 amplitudes, the paired Di-ARA path, four causal
direction states, and local chronological movements.  It then reconstructs an
untouched child waveform from the visible parent and two entry readings.
"""

from __future__ import annotations

import hashlib
import json
import math
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree


HERE = Path(__file__).resolve().parent
SOURCE_ZIP = HERE / "T358_SOURCE_DATA.zip"
SOURCE = HERE / "T358_SOURCE_DATA" / "figure4_extracted"
HZ = 200.0
DROP_SECONDS = 10.0
M = 64
K_LOOKUP = 9
K_IRR = 3
FLAT = 0.01
RESOLUTIONS = np.array([8, 16, 32, 64], dtype=int)
MAX_LAG = 128

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

PREFIX = HERE / "T361_IRRATIONALITY_DI_ARA_WAVE_RECORDING"
CYCLE_CSV = Path(f"{PREFIX}_CYCLE_METRICS.csv")
PAIR_CSV = Path(f"{PREFIX}_PAIR_SUMMARY.csv")
RECORD_CSV = Path(f"{PREFIX}_RECORD_SUMMARY.csv")
IRR_CSV = Path(f"{PREFIX}_IRRATIONALITY_READINGS.csv")
PARENT_CSV = Path(f"{PREFIX}_PARENT_WAVES.csv")
EXAMPLE_CSV = Path(f"{PREFIX}_EXAMPLE_PATH.csv")
QA_CSV = Path(f"{PREFIX}_SOURCE_QA.csv")
GATES_CSV = Path(f"{PREFIX}_FROZEN_GATES.csv")
RESULTS_JSON = Path(f"{PREFIX}_RESULTS.json")
FIGURE_PNG = Path(f"{PREFIX}_FIGURE.png")
REPORT_MD = HERE / "T361_IRRATIONALITY_DI_ARA_WAVE_RECORDING_REPORT_2026-08-12.md"

CLAIM = HERE / "T361_IRRATIONALITY_DI_ARA_WAVE_RECORDING_CLAIM_PACKET_v1.md"
PROTOCOLS = [
    HERE / "T361_IRRATIONALITY_DI_ARA_WAVE_RECORDING_PROTOCOL_v1_FROZEN.md",
    HERE / "T361_IRRATIONALITY_DI_ARA_WAVE_RECORDING_PROTOCOL_v2_FROZEN.md",
    HERE / "T361_IRRATIONALITY_DI_ARA_WAVE_RECORDING_PROTOCOL_v3_FROZEN.md",
]


def digest(path: Path, kind: str = "sha256") -> str:
    h = hashlib.new(kind)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_lvm(path: Path) -> np.ndarray:
    frame = pd.read_csv(path, sep="\t", header=None, engine="c")
    frame = frame.dropna(axis=1, how="all")
    if frame.shape[1] != 80 or frame.isna().any().any():
        raise RuntimeError(f"{path}: expected complete 80-column matrix, got {frame.shape}")
    values = frame.to_numpy(dtype=np.float64)
    if not np.isfinite(values).all():
        raise RuntimeError(f"{path}: non-finite raw values")
    return values


def detect_events(signal: np.ndarray) -> np.ndarray:
    low, high = np.quantile(signal, [0.35, 0.65])
    events: list[float] = []
    armed = False
    for i in range(1, len(signal)):
        if signal[i] <= low:
            armed = True
        if armed and signal[i - 1] < high <= signal[i]:
            denom = signal[i] - signal[i - 1]
            frac = 0.0 if abs(denom) < 1e-12 else (high - signal[i - 1]) / denom
            events.append(float(i - 1 + np.clip(frac, 0.0, 1.0)))
            armed = False
    return np.asarray(events, dtype=float)


def sample_cycle(signal: np.ndarray, start: float, stop: float) -> np.ndarray:
    grid = np.linspace(start, stop, M)
    return np.interp(grid, np.arange(len(signal), dtype=float), signal)


def ara_map(values: np.ndarray, low: float, high: float) -> np.ndarray:
    return 2.0 * np.clip((values - low) / max(high - low, 1e-12), 0.0, 1.0)


def directions(delta: np.ndarray) -> np.ndarray:
    out = np.zeros(len(delta), dtype=int)
    out[delta > FLAT] = 1
    out[delta < -FLAT] = -1
    if not np.any(out):
        return np.ones(len(delta), dtype=int)
    first = int(np.flatnonzero(out)[0])
    out[:first] = out[first]
    for i in range(first + 1, len(out)):
        if out[i] == 0:
            out[i] = out[i - 1]
    return out


def quadrant(parent_out: int, child_in: int) -> str:
    return ("+" if parent_out >= 0 else "-") + ("+" if child_in >= 0 else "-")


def di_coordinates(xa: np.ndarray, xb: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    z = np.mod(np.arctan2(xb - 1.0, xa - 1.0) / (2.0 * np.pi), 1.0)
    radius = np.sqrt((xa - 1.0) ** 2 + (xb - 1.0) ** 2) / math.sqrt(2.0)
    return z, radius


@dataclass
class Recorder:
    scale_da: float
    features: np.ndarray
    target: np.ndarray
    state: np.ndarray
    all_tree: cKDTree
    state_trees: dict[str, tuple[cKDTree, np.ndarray]]

    @classmethod
    def build(cls, train_a: list[np.ndarray], train_b: list[np.ndarray]) -> "Recorder":
        raw_da = np.concatenate([np.diff(x) for x in train_a])
        nonzero = np.abs(raw_da[np.abs(raw_da) > 1e-12])
        scale_da = max(float(np.percentile(nonzero, 90.0)) if len(nonzero) else 1.0, 1e-6)
        features: list[list[float]] = []
        target: list[float] = []
        states: list[str] = []
        for xa, xb in zip(train_a, train_b):
            da, db = np.diff(xa), np.diff(xb)
            dir_a, dir_b = directions(da), directions(db)
            for t in range(1, M - 1):
                q = quadrant(int(dir_a[t]), int(dir_b[t - 1]))
                features.append([xa[t] / 2.0, xb[t] / 2.0, da[t] / scale_da])
                target.append(float(db[t]))
                states.append(q)
        x = np.asarray(features, dtype=float)
        y = np.asarray(target, dtype=float)
        qv = np.asarray(states, dtype="U2")
        if not len(x):
            raise RuntimeError("empty relation recorder")
        state_trees: dict[str, tuple[cKDTree, np.ndarray]] = {}
        for q in ("++", "+-", "--", "-+"):
            index = np.flatnonzero(qv == q)
            if len(index):
                state_trees[q] = (cKDTree(x[index]), index)
        return cls(scale_da, x, y, qv, cKDTree(x), state_trees)

    def step(self, xa: float, xb: float, da: float, q: str, direction_blind: bool = False) -> tuple[float, bool]:
        point = np.asarray([xa / 2.0, xb / 2.0, da / self.scale_da], dtype=float)
        fallback = False
        if not direction_blind and q in self.state_trees:
            tree, source_index = self.state_trees[q]
            k = min(K_LOOKUP, len(source_index))
            _, local_index = tree.query(point, k=k)
            local_index = np.atleast_1d(local_index)
            index = source_index[local_index]
        else:
            fallback = not direction_blind
            k = min(K_LOOKUP, len(self.features))
            _, index = self.all_tree.query(point, k=k)
            index = np.atleast_1d(index)
        return float(np.median(self.target[index])), fallback


def recover(xa: np.ndarray, xb: np.ndarray, model: Recorder, *, blind: bool = False) -> tuple[np.ndarray, int]:
    pred = np.empty_like(xb)
    pred[:2] = xb[:2]
    fallback = 0
    da_all = np.diff(xa)
    dir_a = directions(da_all)
    child_in = int(directions(np.diff(pred[:2]))[0])
    for t in range(1, M - 1):
        q = quadrant(int(dir_a[t]), child_in)
        db, used_fallback = model.step(float(xa[t]), float(pred[t]), float(da_all[t]), q, blind)
        pred[t + 1] = np.clip(pred[t] + db, 0.0, 2.0)
        if abs(pred[t + 1] - pred[t]) >= FLAT:
            child_in = 1 if pred[t + 1] > pred[t] else -1
        fallback += int(used_fallback)
    return pred, fallback


def pearson(a: np.ndarray, b: np.ndarray) -> float:
    if np.std(a) < 1e-9 or np.std(b) < 1e-9:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def turn_indices(x: np.ndarray) -> np.ndarray:
    d = directions(np.diff(x))
    return np.flatnonzero(d[1:] != d[:-1]) + 1


def turning_error(actual: np.ndarray, pred: np.ndarray) -> float:
    a, p = turn_indices(actual), turn_indices(pred)
    if not len(a) and not len(p):
        return 0.0
    if not len(a) or not len(p):
        return 1.0
    return float(np.median(np.min(np.abs(a[:, None] - p[None, :]), axis=1)) / (M - 1))


def path_metrics(xa: np.ndarray, actual: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    err = pred - actual
    actual_dir = directions(np.diff(actual))
    pred_dir = directions(np.diff(pred))
    parent_dir = directions(np.diff(xa))
    actual_q = np.asarray([quadrant(int(a), int(b)) for a, b in zip(parent_dir[1:], actual_dir[:-1])])
    pred_q = np.asarray([quadrant(int(a), int(b)) for a, b in zip(parent_dir[1:], pred_dir[:-1])])
    za, ra = di_coordinates(xa, actual)
    zp, rp = di_coordinates(xa, pred)
    angular = np.abs(np.angle(np.exp(2j * np.pi * (zp - za)))) / (2.0 * np.pi)
    return {
        "RMSE_ARA": float(np.sqrt(np.mean(err**2))),
        "MAE_ARA": float(np.mean(np.abs(err))),
        "waveform_r": pearson(actual, pred),
        "direction_agreement": float(np.mean(actual_dir == pred_dir)),
        "quadrant_agreement": float(np.mean(actual_q == pred_q)),
        "turn_error": turning_error(actual, pred),
        "endpoint_error": float(abs(err[-1])),
        "angular_path_error": float(np.mean(angular)),
        "radial_path_error": float(np.mean(np.abs(rp - ra))),
    }


def circular_mean(z: np.ndarray) -> float:
    vec = np.mean(np.exp(2j * np.pi * z))
    return float(np.mod(np.angle(vec) / (2.0 * np.pi), 1.0)) if abs(vec) > 1e-12 else 0.0


def address_openness(z: np.ndarray) -> tuple[float, list[int]]:
    counts = []
    for bins in RESOLUTIONS:
        index = np.minimum((np.mod(z, 1.0) * bins).astype(int), bins - 1)
        counts.append(int(np.unique(index).size))
    slope = float(np.polyfit(np.log(RESOLUTIONS), np.log(np.maximum(counts, 1)), 1)[0])
    return 2.0 * float(np.clip(slope, 0.0, 1.0)), counts


def circular_loss(actual: np.ndarray, pred: np.ndarray) -> np.ndarray:
    return 1.0 - np.cos(2.0 * np.pi * (actual - pred))


def history_residual(train_z: np.ndarray, test_z: np.ndarray) -> tuple[float, float, float]:
    train_x, train_y = train_z[:-1], train_z[1:]
    test_x, test_y = test_z[:-1], test_z[1:]
    tree_points = np.column_stack([np.cos(2 * np.pi * train_x), np.sin(2 * np.pi * train_x)])
    test_points = np.column_stack([np.cos(2 * np.pi * test_x), np.sin(2 * np.pi * test_x)])
    tree = cKDTree(tree_points)
    _, near = tree.query(test_points, k=min(K_IRR, len(train_x)))
    near = np.atleast_2d(near)
    if near.shape[0] != len(test_x):
        near = near.T
    vec = np.mean(np.exp(2j * np.pi * train_y[near]), axis=1)
    pred = np.mod(np.angle(vec) / (2 * np.pi), 1.0)
    null = np.full_like(test_y, circular_mean(train_y))
    local = float(np.mean(circular_loss(test_y, pred)))
    null_loss = float(np.mean(circular_loss(test_y, null)))
    return 2.0 * min(1.0, local / max(null_loss, 1e-12)), local, null_loss


def closure_history(z: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    rho, miss = [], []
    for lag in range(1, min(MAX_LAG, len(z) - 1) + 1):
        delta = z[lag:] - z[:-lag]
        vec = np.mean(np.exp(2j * np.pi * delta))
        rho.append(float(abs(vec)))
        miss.append(float(np.angle(vec) / (2.0 * np.pi)))
    return np.asarray(rho), np.asarray(miss)


def prepare_pair(signal_a: np.ndarray, signal_b: np.ndarray) -> tuple[list[np.ndarray], list[np.ndarray], int, dict]:
    events = detect_events(signal_a)
    cycles = list(zip(events[:-1], events[1:]))
    n_train = int(math.floor(0.60 * len(cycles)))
    if len(cycles) < 8 or n_train < 4 or len(cycles) - n_train < 3:
        raise RuntimeError(f"insufficient cycles: events={len(events)}, cycles={len(cycles)}")
    prefix_start = int(max(0, math.floor(events[0])))
    prefix_stop = int(min(len(signal_a), math.ceil(events[n_train])))
    a_low, a_high = np.quantile(signal_a[prefix_start:prefix_stop], [0.05, 0.95])
    b_low, b_high = np.quantile(signal_b[prefix_start:prefix_stop], [0.05, 0.95])
    all_a, all_b = [], []
    for start, stop in cycles:
        all_a.append(ara_map(sample_cycle(signal_a, start, stop), a_low, a_high))
        all_b.append(ara_map(sample_cycle(signal_b, start, stop), b_low, b_high))
    qa = {
        "events": len(events),
        "cycles": len(cycles),
        "train_cycles": n_train,
        "test_cycles": len(cycles) - n_train,
        "a_q05": float(a_low),
        "a_q95": float(a_high),
        "b_q05": float(b_low),
        "b_q95": float(b_high),
    }
    return all_a, all_b, n_train, qa


def summarise(df: pd.DataFrame, group: list[str]) -> pd.DataFrame:
    metrics = [
        "RMSE_ARA", "MAE_ARA", "waveform_r", "direction_agreement",
        "quadrant_agreement", "turn_error", "endpoint_error",
        "angular_path_error", "radial_path_error", "fallback_steps",
    ]
    return df.groupby(group, as_index=False)[metrics].median()


def gate_row(gate: str, requirement: str, hits: int, passed: bool, observed: str) -> dict:
    return {"gate": gate, "requirement": requirement, "record_hits": hits, "records_total": 9, "passed": passed, "observed": observed}


def render_figure(cycle_df: pd.DataFrame, record_df: pd.DataFrame, parent_df: pd.DataFrame,
                  example_df: pd.DataFrame, gate_df: pd.DataFrame, irr_df: pd.DataFrame) -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    ink, blue, gold, orange, grey = "#222A33", "#3B6FB6", "#D99B2B", "#C76A2A", "#AAB3BE"
    fig = plt.figure(figsize=(18, 17), facecolor="#F7F8FA")
    gs = fig.add_gridspec(3, 2, hspace=0.34, wspace=0.25)

    ax = fig.add_subplot(gs[0, 0])
    ex = example_df
    ax.plot(ex["fraction"], ex["parent_actual"], color=ink, lw=2.0, label="visible parent A")
    ax.plot(ex["fraction"], ex["child_actual"], color=blue, lw=2.2, label="hidden child B — actual")
    ax.plot(ex["fraction"], ex["child_primary"], color=gold, lw=2.0, ls="--", label="child recovered from Di-ARA")
    ax.axhline(1, color=grey, lw=1)
    ax.set(xlabel="within-cycle time fraction", ylabel="ARA diameter position (0–2)", ylim=(-0.05, 2.05), title="Raw physical waves and recovered child")
    ax.legend(frameon=False, ncol=2, loc="upper center")
    ax.grid(alpha=0.18)

    ax = fig.add_subplot(gs[0, 1])
    ax.plot(ex["parent_actual"], ex["child_actual"], color=blue, lw=2.3, label="actual Di-ARA path")
    ax.plot(ex["parent_actual"], ex["child_primary"], color=gold, lw=1.8, ls="--", label="recovered path")
    ax.scatter(ex.iloc[0]["parent_actual"], ex.iloc[0]["child_actual"], s=70, facecolors="white", edgecolors=ink, zorder=5, label="cycle entry")
    ax.axvline(1, color=ink, lw=1); ax.axhline(1, color=ink, lw=1)
    ax.set(xlim=(-0.05, 2.05), ylim=(-0.05, 2.05), xlabel="visible parent A (0–2)", ylabel="child B (0–2)", title="Two-wave Di-ARA traversal and four direction regions")
    ax.set_aspect("equal", adjustable="box"); ax.legend(frameon=False, loc="upper left"); ax.grid(alpha=0.15)

    ax = fig.add_subplot(gs[1, 0])
    methods = ["primary", "direction_blind", "wrong_lineage", "previous_cycle"]
    labels = ["four-state Di-ARA", "direction-blind", "wrong lineage", "previous cycle"]
    colors = [gold, grey, orange, blue]
    x = np.arange(len(SWEEP))
    width = 0.19
    for i, (method, label, color) in enumerate(zip(methods, labels, colors)):
        sub = record_df[record_df.method == method].set_index("delta_r").reindex(SWEEP)
        ax.bar(x + (i - 1.5) * width, sub["RMSE_ARA"], width, color=color, edgecolor=ink, linewidth=0.5, label=label)
    ax.axhline(0.30, color=ink, ls=":", lw=1.5, label="frozen absolute gate")
    ax.set(xticks=x, xticklabels=list(SWEEP), xlabel="physical detuning ΔR (ohm)", ylabel="median child RMSE (ARA units)", title="Untouched child-wave reconstruction")
    ax.legend(frameon=False, fontsize=9, ncol=2); ax.grid(axis="y", alpha=0.18)

    ax = fig.add_subplot(gs[1, 1])
    prim = record_df[record_df.method == "primary"].set_index("delta_r").reindex(SWEEP)
    ax.plot(list(SWEEP), prim["waveform_r"], "o-", color=blue, lw=2, label="child waveform correlation")
    ax.plot(list(SWEEP), prim["direction_agreement"], "s-", color=gold, lw=2, label="child direction agreement")
    ax.plot(list(SWEEP), prim["quadrant_agreement"], "^-", color=orange, lw=2, label="Di-ARA quadrant agreement")
    parent_summary = parent_df.groupby("delta_r", as_index=False).first().set_index("delta_r").reindex(SWEEP)
    ax.plot(list(SWEEP), parent_summary["parent_waveform_r"], "D--", color=ink, lw=1.8, label="coarse parent correlation")
    ax.axhline(0.75, color=grey, ls=":", lw=1); ax.axhline(0.90, color=ink, ls=":", lw=1)
    ax.set(xlabel="physical detuning ΔR (ohm)", ylabel="agreement / correlation", ylim=(-0.05, 1.05), title="What the recorder retained")
    ax.legend(frameon=False, fontsize=9); ax.grid(alpha=0.18)

    ax = fig.add_subplot(gs[2, 0])
    irr = irr_df.groupby("delta_r", as_index=False)[["x_P", "x_R", "rho_cycle", "abs_miss_cycle"]].median()
    scatter = ax.scatter(irr["x_P"], irr["x_R"], c=irr["delta_r"], cmap="cividis", s=95, edgecolor=ink)
    for _, row in irr.iterrows():
        ax.annotate(f"{int(row.delta_r)}", (row.x_P, row.x_R), xytext=(5, 4), textcoords="offset points", fontsize=8)
    ax.axvline(1, color=ink, lw=1); ax.axhline(1, color=ink, lw=1)
    ax.set(xlim=(-0.05, 2.05), ylim=(-0.05, 2.05), xlabel="x_P: reused → opening addresses", ylabel="x_R: relation-determined → residual", title="Irrationality Di-ARA parent readings of the raw path")
    fig.colorbar(scatter, ax=ax, label="ΔR (ohm)"); ax.grid(alpha=0.15)

    ax = fig.add_subplot(gs[2, 1])
    ax.axis("off")
    lines = ["FROZEN MECHANISM GATES", ""]
    for _, row in gate_df.iterrows():
        mark = "PASS" if bool(row.passed) else "FAIL"
        lines.append(f"{row.gate}  {mark}  —  {row.observed}")
    lines.extend(["", "Primary question:", "Did the 0–2 two-wave record rebuild the physical child and its parent?", "No chance/classification score is used as the verdict."])
    ax.text(0.02, 0.98, "\n".join(lines), va="top", ha="left", color=ink, fontsize=11, family="DejaVu Sans Mono", linespacing=1.55)

    overall = bool(gate_df.passed.all())
    fig.suptitle(
        f"T361 — Irrationality Di-ARA wave recording and recovery\nControlled raw physical waves · verdict: {'SUPPORTED' if overall else 'NOT SUPPORTED AS A COMPLETE RECORDER'}",
        fontsize=18, color=ink, y=0.985,
    )
    fig.text(0.01, 0.008, "Source: Ocampo-Espindola et al., Zenodo 10.5281/zenodo.15122129 · first 60% records relation; final 40% reconstructed", color="#58616D", fontsize=9)
    fig.savefig(FIGURE_PNG, dpi=190, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def process_pair(delta_r: int, pair: int, prepared: list[tuple]) -> dict:
    all_a, all_b, n_train, model, _qa = prepared[pair]
    wrong_model = prepared[(pair + 1) % 40][3]
    train_z = np.concatenate([di_coordinates(a, b)[0] for a, b in zip(all_a[:n_train], all_b[:n_train])])
    test_z = np.concatenate([di_coordinates(a, b)[0] for a, b in zip(all_a[n_train:], all_b[n_train:])])
    x_p, occupied = address_openness(test_z)
    x_r, local_loss, null_loss = history_residual(train_z, test_z)
    rho, miss = closure_history(test_z)
    cycle_lag = M - 1
    irr_row = {
        "delta_r": delta_r, "pair": pair + 1, "x_P": x_p, "x_R": x_r,
        "occupied_8": occupied[0], "occupied_16": occupied[1],
        "occupied_32": occupied[2], "occupied_64": occupied[3],
        "successor_loss": local_loss, "null_loss": null_loss,
        "rho_cycle": float(rho[cycle_lag - 1]) if len(rho) >= cycle_lag else np.nan,
        "miss_cycle": float(miss[cycle_lag - 1]) if len(miss) >= cycle_lag else np.nan,
        "abs_miss_cycle": abs(float(miss[cycle_lag - 1])) if len(miss) >= cycle_lag else np.nan,
        "best_rho": float(np.max(rho)) if len(rho) else np.nan,
    }
    rows: list[dict] = []
    actuals: list[np.ndarray] = []
    predictions_primary: list[np.ndarray] = []
    examples: list[tuple[float, pd.DataFrame]] = []
    previous = all_b[n_train - 1]
    for local_cycle, (xa, xb) in enumerate(zip(all_a[n_train:], all_b[n_train:])):
        predictions = {}
        predictions["primary"], fallback = recover(xa, xb, model, blind=False)
        predictions["direction_blind"], _ = recover(xa, xb, model, blind=True)
        predictions["wrong_lineage"], _ = recover(xa, xb, wrong_model, blind=False)
        replay = previous.copy()
        replay[:2] = xb[:2]
        predictions["previous_cycle"] = replay
        actuals.append(xb)
        predictions_primary.append(predictions["primary"])
        primary_metric = None
        for method, pred in predictions.items():
            metric = path_metrics(xa, xb, pred)
            if method == "primary":
                primary_metric = metric
            rows.append({
                "delta_r": delta_r, "pair": pair + 1, "test_cycle": local_cycle + 1,
                "method": method, **metric,
                "fallback_steps": fallback if method == "primary" else 0,
            })
        ex = pd.DataFrame({
            "delta_r": delta_r, "pair": pair + 1, "test_cycle": local_cycle + 1,
            "fraction": np.linspace(0, 1, M), "parent_actual": xa,
            "child_actual": xb, "child_primary": predictions["primary"],
            "child_direction_blind": predictions["direction_blind"],
            "child_wrong_lineage": predictions["wrong_lineage"],
            "child_previous_cycle": predictions["previous_cycle"],
        })
        examples.append((float(primary_metric["RMSE_ARA"]), ex))
    return {"cycle_rows": rows, "irr_row": irr_row, "actuals": actuals,
            "predictions": predictions_primary, "examples": examples}


def main() -> None:
    if digest(SOURCE_ZIP, "md5") != "abe81a3631481b58977925daf453ede5":
        raise RuntimeError("source archive MD5 mismatch")
    cycle_rows: list[dict] = []
    irr_rows: list[dict] = []
    qa_rows: list[dict] = []
    parent_rows: list[dict] = []
    example_candidates: list[tuple[float, pd.DataFrame]] = []

    for delta_r, stem in SWEEP.items():
        path = SOURCE / stem / f"{stem}.lvm"
        raw = read_lvm(path)[int(DROP_SECONDS * HZ):]
        qa_rows.append({
            "delta_r": delta_r, "filename": path.name, "sha256": digest(path),
            "rows_after_10s": len(raw), "columns": raw.shape[1], "sampling_hz": HZ,
            "raw_min": float(raw.min()), "raw_max": float(raw.max()),
        })
        prepared = []
        for pair in range(40):
            all_a, all_b, n_train, qa = prepare_pair(raw[:, pair], raw[:, pair + 40])
            model = Recorder.build(all_a[:n_train], all_b[:n_train])
            prepared.append((all_a, all_b, n_train, model, qa))
            qa_rows.append({"delta_r": delta_r, "pair": pair + 1, **qa})

        population_actual: list[np.ndarray] = []
        population_primary: list[np.ndarray] = []
        with ThreadPoolExecutor(max_workers=16) as pool:
            outputs = list(pool.map(lambda p: process_pair(delta_r, p, prepared), range(40)))
        for output in outputs:
            cycle_rows.extend(output["cycle_rows"])
            irr_rows.append(output["irr_row"])
            population_actual.extend(output["actuals"])
            population_primary.extend(output["predictions"])
            example_candidates.extend(output["examples"])

        actual_parent = np.median(np.vstack(population_actual), axis=0)
        pred_parent = np.median(np.vstack(population_primary), axis=0)
        parent_metric = path_metrics(np.median(np.vstack([x[0][x[2]] for x in prepared if len(x[0]) > x[2]]), axis=0), actual_parent, pred_parent)
        for i, (actual, pred) in enumerate(zip(actual_parent, pred_parent)):
            parent_rows.append({
                "delta_r": delta_r, "fraction_index": i, "fraction": i / (M - 1),
                "actual_parent_child": float(actual), "recovered_parent_child": float(pred),
                "parent_RMSE_ARA": parent_metric["RMSE_ARA"],
                "parent_waveform_r": parent_metric["waveform_r"],
            })

    cycle_df = pd.DataFrame(cycle_rows)
    pair_df = summarise(cycle_df, ["delta_r", "pair", "method"])
    record_df = summarise(cycle_df, ["delta_r", "method"])
    irr_df = pd.DataFrame(irr_rows)
    qa_df = pd.DataFrame(qa_rows)
    parent_df = pd.DataFrame(parent_rows)

    primary = record_df[record_df.method == "primary"].set_index("delta_r")
    blind = record_df[record_df.method == "direction_blind"].set_index("delta_r")
    wrong = record_df[record_df.method == "wrong_lineage"].set_index("delta_r")
    parent_summary = parent_df.groupby("delta_r", as_index=True).first()
    gate1_mask = (primary.waveform_r >= 0.80) & (primary.RMSE_ARA <= 0.30)
    gate2_mask = (primary.direction_agreement >= 0.75) & (primary.quadrant_agreement >= 0.75) & (primary.turn_error <= 0.10)
    gate3_mask = (primary.endpoint_error <= 0.20) & (primary.angular_path_error <= 0.15)
    gate4_mask = ((blind.RMSE_ARA - primary.RMSE_ARA) >= 0.05) | ((primary.direction_agreement - blind.direction_agreement) >= 0.05)
    gate5_mask = ((wrong.RMSE_ARA - primary.RMSE_ARA) >= 0.05) | ((primary.waveform_r - wrong.waveform_r) >= 0.05)
    gate6_mask = (parent_summary.parent_waveform_r >= 0.90) & (parent_summary.parent_RMSE_ARA <= 0.20)
    masks = [gate1_mask, gate2_mask, gate3_mask, gate4_mask, gate5_mask, gate6_mask]
    needed = [7, 7, 7, 5, 5, 7]
    requirements = [
        "waveform_r>=0.80 and RMSE<=0.30 in >=7/9 records",
        "direction/quadrant>=0.75 and turn_error<=0.10 in >=7/9",
        "endpoint<=0.20 and angular error<=0.15 in >=7/9",
        "four-state improves RMSE or direction by >=0.05 in >=5/9",
        "correct lineage improves RMSE or waveform_r by >=0.05 in >=5/9",
        "coarse parent r>=0.90 and RMSE<=0.20 in >=7/9",
    ]
    labels = ["G1 waveform", "G2 movement", "G3 closure", "G4 four-state", "G5 lineage", "G6 parent"]
    gate_rows = []
    for label, requirement, mask, threshold in zip(labels, requirements, masks, needed):
        hits = int(mask.sum())
        gate_rows.append(gate_row(label, requirement, hits, hits >= threshold, f"{hits}/9 records"))
    gate_df = pd.DataFrame(gate_rows)

    median_rmse = float(cycle_df[cycle_df.method == "primary"].RMSE_ARA.median())
    example_candidates.sort(key=lambda item: abs(item[0] - median_rmse))
    example_df = example_candidates[0][1]

    cycle_df.to_csv(CYCLE_CSV, index=False)
    pair_df.to_csv(PAIR_CSV, index=False)
    record_df.to_csv(RECORD_CSV, index=False)
    irr_df.to_csv(IRR_CSV, index=False)
    qa_df.to_csv(QA_CSV, index=False)
    parent_df.to_csv(PARENT_CSV, index=False)
    example_df.to_csv(EXAMPLE_CSV, index=False)
    gate_df.to_csv(GATES_CSV, index=False)
    render_figure(cycle_df, record_df, parent_df, example_df, gate_df, irr_df)

    overall = bool(gate_df.passed.all())
    result = {
        "test": "T361 Irrationality Di-ARA wave recording and recovery",
        "run_date": "2026-08-12",
        "source_doi": "10.5281/zenodo.15122129",
        "source_zip_md5": digest(SOURCE_ZIP, "md5"),
        "claim_sha256": digest(CLAIM),
        "protocol_sha256": {p.name: digest(p) for p in PROTOCOLS},
        "records": 9,
        "pairs_per_record": 40,
        "cycle_rows": int(len(cycle_df)),
        "verdict": "SUPPORTED [controlled physical wave recorder]" if overall else "NOT SUPPORTED AS A COMPLETE PHYSICAL WAVE RECORDER",
        "overall": overall,
        "gates": gate_df.to_dict(orient="records"),
        "primary_record_medians": record_df[record_df.method == "primary"].to_dict(orient="records"),
        "parent_record_metrics": parent_summary.reset_index().to_dict(orient="records"),
    }
    RESULTS_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    record_table = record_df[record_df.method == "primary"][
        ["delta_r", "RMSE_ARA", "waveform_r", "direction_agreement", "quadrant_agreement", "turn_error", "endpoint_error", "angular_path_error"]
    ].to_markdown(index=False, floatfmt=".4f")
    gate_table = gate_df.to_markdown(index=False)
    parent_table = parent_summary.reset_index()[["delta_r", "parent_RMSE_ARA", "parent_waveform_r"]].to_markdown(index=False, floatfmt=".4f")
    report = f"""# T361 — Irrationality Di-ARA wave recording and recovery

**Run date:** 12 August 2026  
**Source:** Ocampo-Espindola et al., Zenodo 10.5281/zenodo.15122129  
**Frozen verdict:** **{result['verdict']}**

## Question actually tested

This is an instrument-recovery test, not a chance or regime-classification test. The first 60% of complete raw physical cycles recorded the two-wave Di-ARA relation. On the final 40%, the visible parent waveform and only two child entry readings were supplied; the recorder had to rebuild the remaining child waveform.

The retained record was the raw 0–2 parent/child path, its four causal direction states, local movement vectors, circumference angle, radial amplitude, address opening, ordered-relation residual and closure history.

## Primary untouched recovery

{record_table}

## Frozen mechanism gates

{gate_table}

## Child-to-parent coarse-graining

{parent_table}

## Interpretation boundary

The absolute waveform, movement and closure gates answer whether the record reconstructed what it measured. The direction-blind and wrong-lineage gates answer whether the four-state Di-ARA and the specific physical relation contributed, rather than a generic repeated waveform. A partial pass is retained as a layer-specific result and is not replaced by chance accuracy.

## Reproduction

```powershell
& 'F:\\SystemFormulaFolder\\.venv_ara_verify\\Scripts\\python.exe' 'analysis\\irrationality_path_calibration\\t361_irrationality_di_ara_wave_recording.py'
```
"""
    REPORT_MD.write_text(report, encoding="utf-8")
    print(json.dumps({"verdict": result["verdict"], "gates": gate_df.to_dict(orient="records")}, indent=2))


if __name__ == "__main__":
    main()
