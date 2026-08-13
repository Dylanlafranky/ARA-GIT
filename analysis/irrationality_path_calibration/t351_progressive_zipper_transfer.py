#!/usr/bin/env python3
"""T351: causal calibration of a progressive ARA zipper signature."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
SEED = 351_20260811
PROTOCOL = HERE / "T351_PROGRESSIVE_ZIPPER_TRANSFER_PROTOCOL_v1_FROZEN.md"
CLAIM = HERE / "T351_PROGRESSIVE_ZIPPER_TRANSFER_CLAIM_PACKET_v1.md"
EXPECTED_PROTOCOL_HASH = "8BF4382F69BB278F22E9848C346A36FBA001F60A7CB36AEFC2DD2CD90234DBBB"
EXPECTED_CLAIM_HASH = "2353B43F143969F565CFB10A4666508602A822786B49E7755CD59971DBC3ABC0"

BLUE = "#2F6FB0"
GOLD = "#D49A2E"
ORANGE = "#D86D32"
OLIVE = "#738C3A"
PINK = "#C45A86"
INK = "#1C2736"
GREY = "#8A929C"
LIGHT = "#E5E9EF"


@dataclass(frozen=True)
class Config:
    split: str
    case_id: int
    seed: int
    duration: int
    teeth: int
    width: float
    rate_on: float
    noise: float


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def stable_seed(*parts: object) -> int:
    payload = "|".join(map(str, (SEED,) + parts)).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "little")


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def circular_distance(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    d = np.abs(a - b)
    return np.minimum(d, 1.0 - d)


def rankdata(values: np.ndarray) -> np.ndarray:
    return pd.Series(values).rank(method="average").to_numpy(float)


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    mask = np.isfinite(a) & np.isfinite(b)
    if int(mask.sum()) < 4:
        return float("nan")
    ra, rb = rankdata(a[mask]), rankdata(b[mask])
    if np.std(ra) < 1e-12 or np.std(rb) < 1e-12:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def auc(scores_positive: np.ndarray, scores_negative: np.ndarray) -> float:
    """Tie-aware Mann-Whitney AUROC."""
    pos = np.asarray(scores_positive, float)
    neg = np.asarray(scores_negative, float)
    combined = np.r_[pos, neg]
    ranks = rankdata(combined)
    rank_sum = float(ranks[: len(pos)].sum())
    u = rank_sum - len(pos) * (len(pos) + 1) / 2.0
    return u / (len(pos) * len(neg))


def build_configs(split: str) -> list[Config]:
    if split == "calibration":
        cases = 24
        durations = (641, 897)
        teeth = (28, 36, 44)
        widths = (0.055, 0.075, 0.095)
        rates = (0.050, 0.075, 0.100)
        noises = (0.24, 0.32, 0.40)
        offset = 0
    else:
        cases = 40
        durations = (769, 1025, 1281)
        teeth = (32, 40, 48, 52)
        widths = (0.045, 0.065, 0.085)
        rates = (0.045, 0.070, 0.095)
        noises = (0.28, 0.36, 0.44)
        offset = 100
    out = []
    for i in range(cases):
        out.append(
            Config(
                split=split,
                case_id=i,
                seed=offset + i,
                duration=durations[i % len(durations)],
                teeth=teeth[(i * 3 + 1) % len(teeth)],
                width=widths[(i * 5 + 2) % len(widths)],
                rate_on=rates[(i * 7 + 1) % len(rates)],
                noise=noises[(i * 11) % len(noises)],
            )
        )
    return out


def front_path(s: np.ndarray, mode: str) -> tuple[np.ndarray, int | None]:
    if mode == "forward":
        return s.copy(), None
    if mode == "pause":
        front = np.empty_like(s)
        first = s < 0.35
        hold = (s >= 0.35) & (s <= 0.65)
        last = s > 0.65
        front[first] = 0.5 * s[first] / 0.35
        front[hold] = 0.5
        front[last] = 0.5 + 0.5 * (s[last] - 0.65) / 0.35
        return front, None
    if mode == "reverse":
        pivot_fraction = 0.62
        pivot = int(round(pivot_fraction * (len(s) - 1)))
        front = np.empty_like(s)
        early = np.arange(len(s)) <= pivot
        front[early] = s[early] / pivot_fraction
        front[~early] = 1.0 - (s[~early] - pivot_fraction) / (1.0 - pivot_fraction)
        return np.clip(front, 0.0, 1.0), pivot
    raise ValueError(mode)


def ar_process(rng: np.random.Generator, rows: int, cols: int, scale: float) -> np.ndarray:
    innovations = rng.normal(scale=scale, size=(rows, cols))
    values = np.zeros((rows, cols), dtype=float)
    for t in range(1, rows):
        values[t] = 0.58 * values[t - 1] + innovations[t]
    std = np.std(values, axis=0, keepdims=True)
    return values / np.maximum(std, 1e-12)


def rolling_corr(x: np.ndarray, y: np.ndarray, window: int) -> np.ndarray:
    """Past-only rolling column correlation."""
    rows, cols = x.shape
    out = np.zeros((rows, cols), dtype=float)
    cx = np.vstack([np.zeros((1, cols)), np.cumsum(x, axis=0)])
    cy = np.vstack([np.zeros((1, cols)), np.cumsum(y, axis=0)])
    cxx = np.vstack([np.zeros((1, cols)), np.cumsum(x * x, axis=0)])
    cyy = np.vstack([np.zeros((1, cols)), np.cumsum(y * y, axis=0)])
    cxy = np.vstack([np.zeros((1, cols)), np.cumsum(x * y, axis=0)])
    for t in range(window - 1, rows):
        lo, hi = t + 1 - window, t + 1
        n = float(window)
        sx, sy = cx[hi] - cx[lo], cy[hi] - cy[lo]
        sxx, syy = cxx[hi] - cxx[lo], cyy[hi] - cyy[lo]
        sxy = cxy[hi] - cxy[lo]
        cov = sxy - sx * sy / n
        vx = np.maximum(sxx - sx * sx / n, 1e-12)
        vy = np.maximum(syy - sy * sy / n, 1e-12)
        out[t] = cov / np.sqrt(vx * vy)
    return np.clip(out, -1.0, 1.0)


def sustained_first(mask: np.ndarray, run: int = 3, start: int = 0) -> float:
    count = 0
    for idx in range(start, len(mask)):
        count = count + 1 if bool(mask[idx]) else 0
        if count >= run:
            return float(idx - run + 1)
    return float("nan")


def base_geometry(cfg: Config, mode: str) -> dict[str, np.ndarray | int | None]:
    rng = np.random.default_rng(stable_seed(cfg.split, cfg.seed, "geometry", mode))
    s = np.linspace(0.0, 1.0, cfg.duration)
    front, pivot = front_path(s, mode)
    pos = (np.arange(cfg.teeth) + 0.5) / cfg.teeth
    base = (np.arange(cfg.teeth) * ((math.sqrt(5.0) - 1.0) / 2.0)) % 1.0
    base = (base + rng.uniform(-0.015, 0.015, cfg.teeth)) % 1.0
    initial_sep = rng.uniform(0.31, 0.45, cfg.teeth)
    contact = sigmoid((front[:, None] - pos[None, :]) / cfg.width)
    if mode == "reverse":
        # Reversing the seam reopens the same child pairs in reverse order.
        contact = sigmoid((front[:, None] - pos[None, :]) / cfg.width)
    tremor = 0.010 * np.sin(2 * np.pi * (3.0 * s[:, None] + base[None, :]))
    separation = np.clip(initial_sep[None, :] * (1.0 - contact) + tremor * (1.0 - contact), 0.0, 0.49)
    common_drift = 0.025 * np.sin(2 * np.pi * (s[:, None] + base[None, :]))
    phase_a = (base[None, :] + common_drift) % 1.0
    phase_b = (phase_a + separation) % 1.0
    distance = circular_distance(phase_a, phase_b)
    geometry = np.exp(-((distance / 0.115) ** 2))
    return {
        "s": s,
        "front": front,
        "pivot": pivot,
        "pos": pos,
        "phase_a": phase_a,
        "phase_b": phase_b,
        "distance": distance,
        "geometry": geometry,
    }


def hidden_edges(cfg: Config, geometry: dict, regime: str, mode: str) -> np.ndarray:
    distance = np.asarray(geometry["distance"])
    front = np.asarray(geometry["front"])
    pos = np.asarray(geometry["pos"])
    pivot = geometry["pivot"]
    rows, cols = distance.shape
    edge = np.zeros((rows, cols), dtype=float)
    if regime == "memory-only":
        return edge
    if regime == "late-snap":
        start = int(round(0.94 * (rows - 1)))
        ramp = np.linspace(0.0, 1.0, rows - start)[:, None]
        edge[start:] = np.repeat(ramp, cols, axis=1)
        return edge
    q = np.exp(-((distance / 0.090) ** 2))
    for t in range(1, rows):
        if mode == "reverse" and pivot is not None and t > int(pivot):
            release = sigmoid((pos - front[t]) / max(cfg.width * 0.55, 1e-6))
            edge[t] = edge[t - 1] * (1.0 - 0.16 * release)
        else:
            edge[t] = edge[t - 1] + cfg.rate_on * q[t] * (1.0 - edge[t - 1])
    return np.clip(edge, 0.0, 1.0)


def response_channels(cfg: Config, edge: np.ndarray, regime: str, mode: str) -> tuple[np.ndarray, np.ndarray]:
    rows, cols = edge.shape
    rng = np.random.default_rng(stable_seed(cfg.split, cfg.seed, "response", mode))
    a = ar_process(rng, rows, cols, cfg.noise)
    independent = ar_process(rng, rows, cols, cfg.noise)
    driver = np.vstack([np.zeros((1, cols)), a[:-1]])
    if regime == "false-seam":
        perm_rng = np.random.default_rng(stable_seed(cfg.split, cfg.seed, "permutation"))
        perm = np.roll(perm_rng.permutation(cols), 1)
        driver_for_b = driver[:, perm]
    else:
        driver_for_b = driver
    b = edge * driver_for_b + np.sqrt(np.maximum(1.0 - edge * edge, 0.0)) * independent
    window = max(17, int(round(rows / 32)))
    corr = rolling_corr(driver, b, window)
    return a, np.clip(corr, 0.0, 1.0)


def simulate(cfg: Config, regime: str, mode: str) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    geo = base_geometry(cfg, mode)
    edge_regime = "progressive" if regime == "false-seam" else regime
    edge = hidden_edges(cfg, geo, edge_regime, mode)
    _, response = response_channels(cfg, edge, regime, mode)
    s = np.asarray(geo["s"])
    front = np.asarray(geo["front"])
    pos = np.asarray(geo["pos"])
    geometry = np.asarray(geo["geometry"])
    distance = np.asarray(geo["distance"])
    window = max(17, int(round(cfg.duration / 32)))

    geometry_global = np.mean(geometry, axis=1)
    connection_global = np.mean(response, axis=1)
    open_global = np.mean(distance / 0.5, axis=1)
    velocity = np.diff(front, prepend=front[0])

    lock_on = np.full(cfg.teeth, np.nan)
    unlock_on = np.full(cfg.teeth, np.nan)
    geometry_on = np.full(cfg.teeth, np.nan)
    pivot = geo["pivot"]
    for j in range(cfg.teeth):
        geometry_on[j] = sustained_first(geometry[:, j] >= 0.68, run=3, start=0)
        stop = cfg.duration if pivot is None else int(pivot) + 1
        lock_on[j] = sustained_first(response[:stop, j] >= 0.55, run=4, start=window)
        if pivot is not None:
            start = int(pivot) + window
            unlock_on[j] = sustained_first(response[:, j] <= 0.42, run=4, start=start)

    idx80 = int(round(0.80 * (cfg.duration - 1)))
    final_k = float(np.mean(connection_global[-max(window, 8) :]))
    k80 = float(np.mean(connection_global[max(0, idx80 - 3) : idx80 + 4]))
    share80 = k80 / max(final_k, 1e-12)
    onset_lag = float(np.nanmedian((lock_on - geometry_on) / max(cfg.duration - 1, 1)))
    lock_order_rho = spearman(pos, lock_on)
    reverse_rho = spearman(lock_on, unlock_on)
    post_mask = pos <= max(0.0, float(front[-1]) - 2.0 * cfg.width)
    post_response = float(np.nanmedian(response[-1, post_mask])) if np.any(post_mask) else float("nan")
    response_score = float(np.mean(connection_global[-max(window, 8) :]))
    geometry_score = float(np.mean(geometry_global))

    pause_delta = float("nan")
    pause_velocity = float("nan")
    if mode == "pause":
        p0 = int(round(0.40 * (cfg.duration - 1)))
        p1 = int(round(0.60 * (cfg.duration - 1)))
        pause_delta = float(connection_global[p1] - connection_global[p0])
        pause_velocity = float(np.median(np.abs(velocity[p0 + 2 : p1 - 1])))

    summary = {
        "split": cfg.split,
        "case_id": cfg.case_id,
        "seed": cfg.seed,
        "duration": cfg.duration,
        "teeth": cfg.teeth,
        "width": cfg.width,
        "rate_on": cfg.rate_on,
        "noise": cfg.noise,
        "regime": regime,
        "mode": mode,
        "connection_share_at_80": share80,
        "final_connection_response": final_k,
        "post_front_response": post_response,
        "geometry_score": geometry_score,
        "response_score": response_score,
        "lock_order_spearman": lock_order_rho,
        "median_k_minus_g_onset_lag": onset_lag,
        "pause_connection_gain": pause_delta,
        "pause_front_velocity": pause_velocity,
        "reverse_unlock_spearman": reverse_rho,
    }
    timeseries = pd.DataFrame(
        {
            "split": cfg.split,
            "case_id": cfg.case_id,
            "regime": regime,
            "mode": mode,
            "progress": s,
            "front": front,
            "front_velocity": velocity,
            "candidate_geometry": geometry_global,
            "open_mismatch": open_global,
            "connection_response": connection_global,
            "hidden_edge_mean": np.mean(edge, axis=1),
        }
    )
    teeth = pd.DataFrame(
        {
            "split": cfg.split,
            "case_id": cfg.case_id,
            "regime": regime,
            "mode": mode,
            "tooth": np.arange(cfg.teeth),
            "tooth_position": pos,
            "geometry_onset_tick": geometry_on,
            "lock_onset_tick": lock_on,
            "unlock_onset_tick": unlock_on,
        }
    )
    return summary, timeseries, teeth


def gate_row(name: str, value: float, operator: str, threshold: str, passed: bool, family: str) -> dict:
    return {
        "family": family,
        "gate": name,
        "value": value,
        "operator": operator,
        "threshold": threshold,
        "passed": bool(passed),
    }


def evaluate(summary: pd.DataFrame, geometry_max_diff: float) -> tuple[pd.DataFrame, dict]:
    h = summary[summary["split"] == "holdout"].copy()
    forward = h[h["mode"] == "forward"]
    prog = forward[forward["regime"] == "progressive"]
    memory = forward[forward["regime"] == "memory-only"]
    late = forward[forward["regime"] == "late-snap"]
    false = forward[forward["regime"] == "false-seam"]
    pause = h[(h["regime"] == "progressive") & (h["mode"] == "pause")]
    reverse = h[(h["regime"] == "progressive") & (h["mode"] == "reverse")]

    z1 = float(prog["connection_share_at_80"].median())
    z2 = float(prog["lock_order_spearman"].median())
    z3 = float(prog["median_k_minus_g_onset_lag"].median())
    z4_gain = float(pause["pause_connection_gain"].median())
    z4_velocity = float(pause["pause_front_velocity"].median())
    z5 = float(reverse["reverse_unlock_spearman"].median())
    z6_prog = float(prog["post_front_response"].median())
    z6_memory = float(memory["post_front_response"].median())
    z7 = auc(prog["response_score"].to_numpy(), memory["response_score"].to_numpy())
    geometry_auc = auc(prog["geometry_score"].to_numpy(), memory["geometry_score"].to_numpy())
    late_share = float(late["connection_share_at_80"].median())
    false_gap = float(prog["post_front_response"].median() - false["post_front_response"].median())

    gates = [
        gate_row("Z1 pre-closure construction", z1, ">=", "0.55", z1 >= 0.55, "primary"),
        gate_row("Z2 ordered local locks", z2, ">=", "0.80", z2 >= 0.80, "primary"),
        gate_row("Z3 causal handover lower", z3, ">=", "0.00", z3 >= 0.0, "primary"),
        gate_row("Z3 causal handover upper", z3, "<=", "0.15", z3 <= 0.15, "primary"),
        gate_row("Z4 pause construction", z4_gain, ">=", "0.05", z4_gain >= 0.05, "primary"),
        gate_row("Z4 stationary front", z4_velocity, "<", "1e-10", z4_velocity < 1e-10, "primary"),
        gate_row("Z5 reverse release", z5, "<=", "-0.75", z5 <= -0.75, "primary"),
        gate_row("Z6 progressive retained response", z6_prog, ">=", "0.65", z6_prog >= 0.65, "primary"),
        gate_row("Z6 memory response ceiling", z6_memory, "<=", "0.25", z6_memory <= 0.25, "primary"),
        gate_row("Z7 independent discrimination", z7, ">=", "0.90", z7 >= 0.90, "primary"),
        gate_row("B1 geometry-only lower", geometry_auc, ">=", "0.49", geometry_auc >= 0.49, "boundary"),
        gate_row("B1 geometry-only upper", geometry_auc, "<=", "0.51", geometry_auc <= 0.51, "boundary"),
        gate_row("B2 phase geometry identity", geometry_max_diff, "<=", "1e-12", geometry_max_diff <= 1e-12, "boundary"),
        gate_row("C1 late-snap at 80%", late_share, "<", "0.15", late_share < 0.15, "control"),
        gate_row("C2 false-seam response gap", false_gap, ">=", "0.25", false_gap >= 0.25, "control"),
    ]
    gate_df = pd.DataFrame(gates)
    primary_pass = bool(gate_df[gate_df["family"] == "primary"]["passed"].all())
    boundary_pass = bool(gate_df[gate_df["family"] == "boundary"]["passed"].all())
    control_pass = bool(gate_df[gate_df["family"] == "control"]["passed"].all())
    values = {
        "z1_connection_share_at_80": z1,
        "z2_lock_order_spearman": z2,
        "z3_median_k_minus_g_onset_lag": z3,
        "z4_pause_connection_gain": z4_gain,
        "z4_pause_front_velocity": z4_velocity,
        "z5_reverse_unlock_spearman": z5,
        "z6_progressive_post_front_response": z6_prog,
        "z6_memory_post_front_response": z6_memory,
        "z7_response_auroc": z7,
        "geometry_only_auroc": geometry_auc,
        "geometry_max_difference": geometry_max_diff,
        "late_snap_share_at_80": late_share,
        "false_seam_response_gap": false_gap,
        "primary_pass": primary_pass,
        "boundary_pass": boundary_pass,
        "control_pass": control_pass,
    }
    return gate_df, values


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, subtitle: str = "") -> tuple[int, int, int, int]:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=18, fill="#FFFFFF", outline="#D5DCE5", width=2)
    draw.text((x0 + 24, y0 + 18), title, fill=INK, font=font(24, True))
    if subtitle:
        draw.text((x0 + 24, y0 + 50), subtitle, fill="#5D6878", font=font(15))
    return x0 + 68, y0 + 84, x1 - 28, y1 - 52


def map_xy(area: tuple[int, int, int, int], x: float, y: float, ylim: tuple[float, float]) -> tuple[int, int]:
    x0, y0, x1, y1 = area
    px = x0 + float(x) * (x1 - x0)
    py = y1 - (float(y) - ylim[0]) / (ylim[1] - ylim[0]) * (y1 - y0)
    return int(px), int(py)


def draw_axes(draw: ImageDraw.ImageDraw, area: tuple[int, int, int, int], ylim: tuple[float, float], ylabel: str) -> None:
    x0, y0, x1, y1 = area
    for frac in (0.0, 0.5, 1.0):
        px, _ = map_xy(area, frac, ylim[0], ylim)
        draw.line((px, y0, px, y1), fill="#EEF1F5", width=1)
        draw.text((px - 10, y1 + 8), f"{frac:g}", fill="#657184", font=font(13))
    for value in np.linspace(ylim[0], ylim[1], 3):
        _, py = map_xy(area, 0.0, float(value), ylim)
        draw.line((x0, py, x1, py), fill=LIGHT, width=1)
        draw.text((x0 - 46, py - 8), f"{value:.1f}", fill="#657184", font=font(12))
    draw.line((x0, y1, x1, y1), fill="#344052", width=2)
    draw.line((x0, y0, x0, y1), fill="#344052", width=2)
    draw.text(((x0 + x1) // 2 - 45, y1 + 26), "event progress", fill="#4C5868", font=font(14))
    draw.text((x0, y0 - 22), ylabel, fill="#4C5868", font=font(13))


def draw_line(draw: ImageDraw.ImageDraw, area: tuple[int, int, int, int], x: np.ndarray, y: np.ndarray,
              color: str, ylim: tuple[float, float], width: int = 3) -> None:
    stride = max(1, len(x) // 500)
    points = [map_xy(area, float(a), float(b), ylim) for a, b in zip(x[::stride], y[::stride])]
    if len(points) > 1:
        draw.line(points, fill=color, width=width, joint="curve")


def legend(draw: ImageDraw.ImageDraw, area: tuple[int, int, int, int], entries: list[tuple[str, str]]) -> None:
    x0, y0, _, _ = area
    x, y = x0 + 8, y0 + 7
    for label, color in entries:
        draw.line((x, y + 7, x + 24, y + 7), fill=color, width=4)
        draw.text((x + 31, y), label, fill="#4C5868", font=font(13))
        y += 22


def make_figure(example: pd.DataFrame, teeth: pd.DataFrame, gates: pd.DataFrame, values: dict) -> Path:
    width, height = 2400, 1450
    image = Image.new("RGB", (width, height), "#F5F7FA")
    draw = ImageDraw.Draw(image)
    draw.text((60, 32), "T351 — progressive zipper transfer calibration", fill=INK, font=font(38, True))
    draw.text((60, 82), "Candidate proximity is not called Connection until an independent lower-rung response appears", fill="#5D6878", font=font(20))

    margin, gap = 48, 30
    top = 132
    panel_w = (width - 2 * margin - 2 * gap) // 3
    panel_h = 590
    boxes = []
    for row in range(2):
        for col in range(3):
            x0 = margin + col * (panel_w + gap)
            y0 = top + row * (panel_h + gap)
            boxes.append((x0, y0, x0 + panel_w, y0 + panel_h))

    prog = example[(example.regime == "progressive") & (example["mode"] == "forward")]
    memory = example[(example.regime == "memory-only") & (example["mode"] == "forward")]
    late = example[(example.regime == "late-snap") & (example["mode"] == "forward")]
    false = example[(example.regime == "false-seam") & (example["mode"] == "forward")]
    pause = example[(example.regime == "progressive") & (example["mode"] == "pause")]

    area = panel(draw, boxes[0], "ARA seam and lower-rung response", "Same event shown on the complete 0–2 ARA diameter")
    draw_axes(draw, area, (0, 2), "ARA")
    draw_line(draw, area, prog.progress.to_numpy(), 2 * prog.front.to_numpy(), INK, (0, 2), 4)
    draw_line(draw, area, prog.progress.to_numpy(), 2 * prog.candidate_geometry.to_numpy(), BLUE, (0, 2), 4)
    draw_line(draw, area, prog.progress.to_numpy(), 2 * prog.connection_response.to_numpy(), GOLD, (0, 2), 4)
    _, ridge = map_xy(area, 0, 1.0, (0, 2))
    draw.line((area[0], ridge, area[2], ridge), fill=GREY, width=2)
    legend(draw, area, [("parent seam", INK), ("candidate child geometry", BLUE), ("independent child Connection", GOLD)])

    area = panel(draw, boxes[1], "Approach precedes Connection", "Both readings are causal and use different formulas")
    draw_axes(draw, area, (0, 1), "reading")
    draw_line(draw, area, prog.progress.to_numpy(), prog.candidate_geometry.to_numpy(), BLUE, (0, 1), 4)
    draw_line(draw, area, prog.progress.to_numpy(), prog.connection_response.to_numpy(), GOLD, (0, 1), 4)
    legend(draw, area, [("candidate geometry", BLUE), ("Connection response", GOLD)])

    area = panel(draw, boxes[2], "Independent response separates controls", "Progressive and memory-only have identical visible phase paths")
    draw_axes(draw, area, (0, 1), "same-pair response")
    for df, color in ((prog, GOLD), (memory, GREY), (late, ORANGE), (false, PINK)):
        draw_line(draw, area, df.progress.to_numpy(), df.connection_response.to_numpy(), color, (0, 1), 4)
    px, _ = map_xy(area, 0.8, 0, (0, 1))
    draw.line((px, area[1], px, area[3]), fill=INK, width=2)
    legend(draw, area, [("progressive zip", GOLD), ("memory-only", GREY), ("late snap", ORANGE), ("false seam", PINK)])

    area = panel(draw, boxes[3], "Construction continues during a parent pause", "Blue band: stationary seam; gold still rises")
    draw_axes(draw, area, (0, 1), "reading")
    p0, _ = map_xy(area, 0.35, 0, (0, 1))
    p1, _ = map_xy(area, 0.65, 0, (0, 1))
    draw.rectangle((p0, area[1], p1, area[3]), fill="#E8F0F8")
    draw_line(draw, area, pause.progress.to_numpy(), pause.front.to_numpy(), INK, (0, 1), 4)
    draw_line(draw, area, pause.progress.to_numpy(), pause.connection_response.to_numpy(), GOLD, (0, 1), 4)
    legend(draw, area, [("parent seam", INK), ("Connection response", GOLD)])

    area = panel(draw, boxes[4], "Reverse seam releases in reverse order", "Forward lock rank versus chronological unlock rank")
    draw_axes(draw, area, (0, 1), "unlock rank")
    draw.line((map_xy(area, 0, 1, (0, 1)), map_xy(area, 1, 0, (0, 1))), fill=INK, width=2)
    rev = teeth[(teeth.regime == "progressive") & (teeth["mode"] == "reverse")].dropna(subset=["lock_onset_tick", "unlock_onset_tick"]).copy()
    if not rev.empty:
        rev["lock_rank"] = rev.lock_onset_tick.rank(pct=True)
        rev["unlock_rank"] = rev.unlock_onset_tick.rank(pct=True)
        for x, y in zip(rev.lock_rank, rev.unlock_rank):
            px, py = map_xy(area, float(x), float(y), (0, 1))
            draw.ellipse((px - 4, py - 4, px + 4, py + 4), fill=BLUE, outline="#FFFFFF")
    draw.text((area[0] + 12, area[1] + 10), f"holdout median rho = {values['z5_reverse_unlock_spearman']:.3f}", fill="#4C5868", font=font(14))

    area = panel(draw, boxes[5], "Frozen scorecard", "Primary blue · boundary gold · controls grey")
    plot_gates = gates.reset_index(drop=True)
    y = area[1] + 5
    row_h = max(24, (area[3] - area[1] - 10) // len(plot_gates))
    for _, row in plot_gates.iterrows():
        color = BLUE if row.family == "primary" else GOLD if row.family == "boundary" else GREY
        draw.rectangle((area[0], y + 3, area[0] + 18, y + 19), fill=color)
        label = str(row.gate)
        if len(label) > 34:
            label = label[:32] + "…"
        draw.text((area[0] + 27, y), label, fill=INK, font=font(13))
        status = "PASS" if bool(row.passed) else "FAIL"
        draw.text((area[2] - 55, y), status, fill=OLIVE if row.passed else ORANGE, font=font(13, True))
        y += row_h

    draw.text((60, height - 42), "Synthetic known-referee calibration · candidate geometry and Connection response are independent observables", fill="#657184", font=font(15))
    path = HERE / "T351_PROGRESSIVE_ZIPPER_TRANSFER_FIGURE.png"
    image.save(path)
    return path


def write_report(values: dict, gates: pd.DataFrame, counts: dict) -> Path:
    verdict = "SUPPORTED" if values["primary_pass"] else "NOT SUPPORTED"
    report = f"""# T351 — Progressive zipper transfer

**Run date:** 11 August 2026  
**Evidence boundary:** synthetic known-referee causal instrument calibration  
**Primary verdict:** **{verdict}**  
**Necessary non-identifiability boundary:** **{'PASSED' if values['boundary_pass'] else 'FAILED'}**  
**Late-snap / false-seam controls:** **{'PASSED' if values['control_pass'] else 'FAILED'}**

## Technical summary

The instrument {'recovered' if values['primary_pass'] else 'did not fully recover'} the frozen progressive-zip signature. Candidate child geometry and independently measured lower-rung Connection were deliberately kept separate. The same visible phase path could not distinguish a true zip from a memory-only mimic, while the independent response channel could.

## What was tested

Two ordered lower-rung ARA strands approached pairwise contact behind a moving parent seam. The detector saw causal ARA phase geometry and rolling same-pair response coherence, but not the hidden edge strengths or regime labels. Progressive, memory-only, late-snap, false-seam, interrupted and reverse events were scored on untouched parameter combinations.

## Main results

- By 80% parent progress, progressive events carried a median **{values['z1_connection_share_at_80']:.3f}** of their final independently measured Connection.
- Child order versus detected lock order had median Spearman **{values['z2_lock_order_spearman']:.3f}**.
- Connection response followed candidate geometry by median **{values['z3_median_k_minus_g_onset_lag']:.4f}** event durations.
- During a stationary parent-front interval, lower-rung Connection increased by median **{values['z4_pause_connection_gain']:.3f}** while median front velocity was **{values['z4_pause_front_velocity']:.3e}**.
- Forward lock order versus chronological unlock order had median Spearman **{values['z5_reverse_unlock_spearman']:.3f}**.
- Post-front response coherence was **{values['z6_progressive_post_front_response']:.3f}** for progressive zips and **{values['z6_memory_post_front_response']:.3f}** for the memory-only mimic.
- Independent-response AUROC was **{values['z7_response_auroc']:.3f}**.

## The important negative result

Progressive and memory-only phase geometry was identical to maximum difference **{values['geometry_max_difference']:.3e}**. Geometry-only AUROC was therefore **{values['geometry_only_auroc']:.3f}**: chance, as frozen.

This answers the user's uncertainty directly. Approaching geometry can identify where a lock *could* form, but it cannot establish that a hidden Connection actually formed when an exact non-locking path mimic is possible. A connection-bearing consequence at a lower rung is required.

## ARA interpretation

The synthetic progressive case is consistent with:

`open parent traversal -> candidate child meeting -> local lock -> ordered retained Connection`.

The pause result isolates the proposed rung distinction: local children continued constructing Connection while the parent seam did not move. The reverse result recovered the zipper prediction that a reversed seam releases the accumulated locks in reverse order.

The result does **not** show that every physical system implements this zipper. It calibrates the signature and tells us what must be measured in real data: candidate proximity plus an independent lower-rung coupling response.

## Frozen controls

- Late-snap Connection share at 80% progress: **{values['late_snap_share_at_80']:.3f}**.
- Progressive minus false-seam same-pair response: **{values['false_seam_response_gap']:.3f}**.
- Primary gates passed: **{int(gates[gates.family == 'primary'].passed.sum())}/{int((gates.family == 'primary').sum())}**.
- Boundary gates passed: **{int(gates[gates.family == 'boundary'].passed.sum())}/{int((gates.family == 'boundary').sum())}**.
- Control gates passed: **{int(gates[gates.family == 'control'].passed.sum())}/{int((gates.family == 'control').sum())}**.

## Population and reproducibility

- Calibration configurations: **{counts['calibration_configs']}**.
- Holdout configurations: **{counts['holdout_configs']}**.
- Regime/mode event records: **{counts['events']}**.
- Causal time-series rows: **{counts['timeseries_rows']}**.
- Protocol SHA-256: `{EXPECTED_PROTOCOL_HASH}`.
- Claim SHA-256: `{EXPECTED_CLAIM_HASH}`.

## Evidence boundary

This is generated calibration data with known referee states. Exact geometry identity in the mimic is constructed as a hard identifiability control. The independently observed response is noisy and causal, but still comes from a declared synthetic coupling process. Public-data testing must predeclare a domain-specific connection-bearing response before labels are opened.
"""
    path = HERE / "T351_PROGRESSIVE_ZIPPER_TRANSFER_REPORT_2026-08-11.md"
    path.write_text(report, encoding="utf-8")
    return path


def main() -> None:
    if sha256(PROTOCOL) != EXPECTED_PROTOCOL_HASH:
        raise RuntimeError("Frozen protocol hash mismatch")
    if sha256(CLAIM) != EXPECTED_CLAIM_HASH:
        raise RuntimeError("Frozen claim hash mismatch")

    summaries: list[dict] = []
    time_parts: list[pd.DataFrame] = []
    tooth_parts: list[pd.DataFrame] = []
    geometry_max_diff = 0.0
    example_time: list[pd.DataFrame] = []
    example_teeth: list[pd.DataFrame] = []

    all_configs = build_configs("calibration") + build_configs("holdout")
    for cfg in all_configs:
        per_case = {}
        for regime in ("progressive", "memory-only", "late-snap", "false-seam"):
            summary, times, teeth = simulate(cfg, regime, "forward")
            summaries.append(summary)
            time_parts.append(times)
            tooth_parts.append(teeth)
            per_case[regime] = times
            if cfg.split == "holdout" and cfg.case_id == 0:
                example_time.append(times)
                example_teeth.append(teeth)
        # Exact geometry-control check uses the complete causal geometry traces.
        for regime in ("memory-only", "late-snap"):
            geometry_max_diff = max(
                geometry_max_diff,
                float(np.max(np.abs(per_case["progressive"].candidate_geometry.to_numpy() - per_case[regime].candidate_geometry.to_numpy()))),
            )
        for mode in ("pause", "reverse"):
            summary, times, teeth = simulate(cfg, "progressive", mode)
            summaries.append(summary)
            time_parts.append(times)
            tooth_parts.append(teeth)
            if cfg.split == "holdout" and cfg.case_id == 0:
                example_time.append(times)
                example_teeth.append(teeth)

    summary_df = pd.DataFrame(summaries)
    times_df = pd.concat(time_parts, ignore_index=True)
    teeth_df = pd.concat(tooth_parts, ignore_index=True)
    gate_df, values = evaluate(summary_df, geometry_max_diff)

    summary_path = HERE / "T351_PROGRESSIVE_ZIPPER_TRANSFER_EVENT_SUMMARY.csv"
    time_path = HERE / "T351_PROGRESSIVE_ZIPPER_TRANSFER_TIMESERIES.csv"
    teeth_path = HERE / "T351_PROGRESSIVE_ZIPPER_TRANSFER_TEETH.csv"
    gate_path = HERE / "T351_PROGRESSIVE_ZIPPER_TRANSFER_FROZEN_GATES.csv"
    summary_df.to_csv(summary_path, index=False)
    times_df.to_csv(time_path, index=False)
    teeth_df.to_csv(teeth_path, index=False)
    gate_df.to_csv(gate_path, index=False)

    example_df = pd.concat(example_time, ignore_index=True)
    example_teeth_df = pd.concat(example_teeth, ignore_index=True)
    example_df.to_csv(HERE / "T351_PROGRESSIVE_ZIPPER_TRANSFER_EXAMPLE_TIMESERIES.csv", index=False)
    example_teeth_df.to_csv(HERE / "T351_PROGRESSIVE_ZIPPER_TRANSFER_EXAMPLE_TEETH.csv", index=False)

    counts = {
        "calibration_configs": len(build_configs("calibration")),
        "holdout_configs": len(build_configs("holdout")),
        "events": len(summary_df),
        "timeseries_rows": len(times_df),
    }
    result = {
        "test": "T351_PROGRESSIVE_ZIPPER_TRANSFER",
        "run_date": "2026-08-11",
        "evidence_boundary": "synthetic known-referee causal instrument calibration",
        "protocol_sha256": EXPECTED_PROTOCOL_HASH,
        "claim_sha256": EXPECTED_CLAIM_HASH,
        "counts": counts,
        "results": values,
        "verdict": "SUPPORTED" if values["primary_pass"] else "NOT SUPPORTED",
    }
    (HERE / "T351_PROGRESSIVE_ZIPPER_TRANSFER_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_report(values, gate_df, counts)
    make_figure(example_df, example_teeth_df, gate_df, values)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
