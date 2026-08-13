#!/usr/bin/env python3
"""T350 synthetic discrimination: tick-parent memory versus pure closure-front."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
SEED = 350_20260811
V_REF = 0.05
K_NEIGHBOURS = 5
CHECKPOINTS = np.array((1 / 8, 1 / 4, 3 / 8, 1 / 2, 5 / 8, 3 / 4, 7 / 8, 31 / 32, 1.0))
LAG_FRACTIONS = np.array((1 / 64, 1 / 32, 1 / 16, 1 / 8, 1 / 4, 1 / 2))
RESOLUTIONS = np.array((16, 32, 64, 128, 256), dtype=int)

PROTOCOL = HERE / "T350_TICK_PARENT_CLOSURE_FRONT_PROTOCOL_v1_FROZEN.md"
CLAIM = HERE / "T350_TICK_PARENT_CLOSURE_FRONT_CLAIM_PACKET_v1.md"

VARIANTS = (
    "gradual reference",
    "front-loaded",
    "back-loaded",
    "early burst",
    "positive detour",
    "negative detour",
    "oscillatory detour",
    "pseudo-stochastic bridge",
)

SPLITS = {
    "calibration": {
        "durations": (513, 1025),
        "turns": (2, 4, 6),
        "amplitudes": (0.18, 0.30),
        "seeds": tuple(range(3)),
    },
    "holdout": {
        "durations": (769, 1537),
        "turns": (3, 5, 7),
        "amplitudes": (0.24, 0.36),
        "seeds": tuple(range(10, 14)),
    },
}

COLORS = {
    "gradual reference": "#2F6FB0",
    "front-loaded": "#D49A2E",
    "back-loaded": "#8A929C",
    "early burst": "#D86D32",
    "positive detour": "#738C3A",
    "negative detour": "#C45A86",
    "oscillatory detour": "#6A5AA8",
    "pseudo-stochastic bridge": "#3A8C8C",
}


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


def bridge_shape(q: np.ndarray, seed: int) -> np.ndarray:
    """Continuous deterministic bridge reusable at any sampling cadence."""
    rng = np.random.default_rng(seed)
    coeff = rng.normal(size=9) / np.arange(1, 10) ** 1.15
    raw = sum(c * np.sin(np.pi * k * q) for k, c in enumerate(coeff, start=1))
    scale = float(np.max(np.abs(raw)))
    return raw / max(scale, 1e-12)


def early_profile(q: np.ndarray, variant: str, amplitude: float, seed: int) -> np.ndarray:
    if variant == "gradual reference":
        return q
    if variant == "front-loaded":
        return q + 0.12 * np.sin(2 * np.pi * q)
    if variant == "back-loaded":
        return q - 0.12 * np.sin(2 * np.pi * q)
    if variant == "early burst":
        raw = sigmoid(10.0 * (q - 0.28))
        lo = float(sigmoid(np.array([-2.8]))[0])
        hi = float(sigmoid(np.array([7.2]))[0])
        return (raw - lo) / (hi - lo)
    if variant == "positive detour":
        return q + amplitude * np.sin(np.pi * q) ** 2
    if variant == "negative detour":
        return q - amplitude * np.sin(np.pi * q) ** 2
    if variant == "oscillatory detour":
        return q + 0.70 * amplitude * np.sin(4 * np.pi * q) * np.sin(np.pi * q) ** 2
    if variant == "pseudo-stochastic bridge":
        return q + amplitude * bridge_shape(q, seed)
    raise ValueError(variant)


def generate_path(duration: int, turns: int, amplitude: float, seed: int, variant: str) -> np.ndarray:
    s = np.linspace(0.0, 1.0, duration)
    u = np.empty(duration, dtype=float)
    early = s <= 0.5
    q = 2.0 * s[early]
    u[early] = 0.5 * turns * early_profile(q, variant, amplitude, seed)
    # Exact common suffix for every matched family.
    u[~early] = turns * s[~early]
    u[0] = 0.0
    u[-1] = float(turns)
    return u


def address_openness(phase: np.ndarray) -> float:
    occupied = []
    for bins in RESOLUTIONS:
        idx = np.minimum((phase * bins).astype(int), bins - 1)
        occupied.append(max(1, int(np.unique(idx).size)))
    beta = float(np.polyfit(np.log(RESOLUTIONS), np.log(occupied), 1)[0])
    return 2.0 * float(np.clip(beta, 0.0, 1.0))


def circular_mean(values: np.ndarray) -> float:
    vector = np.mean(np.exp(2j * np.pi * values))
    return 0.0 if abs(vector) < 1e-15 else float((np.angle(vector) / (2 * np.pi)) % 1.0)


def circular_loss(actual: np.ndarray, predicted: np.ndarray) -> np.ndarray:
    return 1.0 - np.cos(2.0 * np.pi * (actual - predicted))


def knn_predict(train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray) -> np.ndarray:
    order = np.argsort(train_x)
    sx, sy = train_x[order], train_y[order]
    insertion = np.searchsorted(sx, test_x)
    radius = max(K_NEIGHBOURS + 2, 7)
    offsets = np.arange(-radius, radius + 1)
    candidates = (insertion[:, None] + offsets[None, :]) % len(sx)
    candidate_x = sx[candidates]
    distance = np.abs(candidate_x - test_x[:, None])
    distance = np.minimum(distance, 1.0 - distance)
    nearest_positions = np.argpartition(distance, K_NEIGHBOURS - 1, axis=1)[:, :K_NEIGHBOURS]
    nearest = np.take_along_axis(candidates, nearest_positions, axis=1)
    neighbour_y = sy[nearest]
    vectors = np.mean(np.exp(2j * np.pi * neighbour_y), axis=1)
    predicted = (np.angle(vectors) / (2 * np.pi)) % 1.0
    predicted[np.abs(vectors) < 1e-12] = circular_mean(train_y)
    return predicted


def stochastic_residual(phase: np.ndarray) -> float:
    split = len(phase) // 2
    train_x, train_y = phase[: split - 1], phase[1:split]
    test_x, test_y = phase[split:-1], phase[split + 1 :]
    local = float(np.mean(circular_loss(test_y, knn_predict(train_x, train_y, test_x))))
    null = float(np.mean(circular_loss(test_y, np.full_like(test_y, circular_mean(train_y)))))
    return 2.0 * min(1.0, local / max(null, 1e-12))


def closure_signature(phase: np.ndarray) -> np.ndarray:
    vector = np.exp(2j * np.pi * phase)
    values = []
    for fraction in LAG_FRACTIONS:
        lag = int(np.clip(round(fraction * (len(phase) - 1)), 1, len(phase) - 2))
        relation = vector[lag:] * np.conj(vector[:-lag])
        values.append(float(abs(np.mean(relation))))
    return np.asarray(values)


def history_vector(unwrapped: np.ndarray) -> np.ndarray:
    phase = np.mod(unwrapped, 1.0)
    x_p = address_openness(phase)
    x_r = stochastic_residual(phase)
    return np.r_[x_p / 2.0, x_r / 2.0, closure_signature(phase)]


def history_distance(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.sqrt(np.mean((a - b) ** 2)))


def tick_coordinates(unwrapped: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    x_position = 2.0 * np.mod(unwrapped, 1.0)
    delta = np.diff(unwrapped, prepend=unwrapped[0])
    x_motion = 1.0 + np.tanh(delta / V_REF)
    return x_position, x_motion


def reconstruct_from_ticks(initial: float, x_motion: np.ndarray) -> np.ndarray:
    clipped = np.clip(x_motion[1:] - 1.0, -1 + 1e-14, 1 - 1e-14)
    delta = V_REF * np.arctanh(clipped)
    return np.r_[initial, initial + np.cumsum(delta)]


def prefix_index(duration: int, progress: float) -> int:
    return max(96, min(duration, int(round(progress * (duration - 1))) + 1))


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def draw_panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, subtitle: str = "") -> tuple[int, int, int, int]:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=18, fill="#FFFFFF", outline="#D5DCE5", width=2)
    draw.text((x0 + 26, y0 + 20), title, fill="#172233", font=font(25, True))
    if subtitle:
        draw.text((x0 + 26, y0 + 55), subtitle, fill="#5D6878", font=font(16))
    return x0 + 70, y0 + 92, x1 - 28, y1 - 48


def map_xy(area: tuple[int, int, int, int], x: float, y: float, xlim=(0.0, 1.0), ylim=(0.0, 2.0)) -> tuple[int, int]:
    x0, y0, x1, y1 = area
    px = x0 + (x - xlim[0]) / (xlim[1] - xlim[0]) * (x1 - x0)
    py = y1 - (y - ylim[0]) / (ylim[1] - ylim[0]) * (y1 - y0)
    return int(px), int(py)


def axes(draw: ImageDraw.ImageDraw, area: tuple[int, int, int, int], x_ticks, y_ticks, xlim, ylim, xlabel="", ylabel="") -> None:
    x0, y0, x1, y1 = area
    for value in y_ticks:
        _, py = map_xy(area, xlim[0], value, xlim, ylim)
        draw.line((x0, py, x1, py), fill="#E5E9EF", width=1)
        draw.text((x0 - 50, py - 9), f"{value:g}", fill="#657184", font=font(14))
    for value in x_ticks:
        px, _ = map_xy(area, value, ylim[0], xlim, ylim)
        draw.line((px, y0, px, y1), fill="#EEF1F5", width=1)
        draw.text((px - 12, y1 + 8), f"{value:g}", fill="#657184", font=font(14))
    draw.line((x0, y1, x1, y1), fill="#344052", width=2)
    draw.line((x0, y0, x0, y1), fill="#344052", width=2)
    if xlabel:
        draw.text(((x0 + x1) // 2 - 70, y1 + 27), xlabel, fill="#4C5868", font=font(15))
    if ylabel:
        draw.text((x0, y0 - 24), ylabel, fill="#4C5868", font=font(15))


def make_figure(prefix_df: pd.DataFrame, pair_df: pd.DataFrame, cadence_df: pd.DataFrame,
                closure_df: pd.DataFrame, gate_df: pd.DataFrame, result: dict,
                example_paths: dict[str, np.ndarray]) -> None:
    width, height = 2400, 1500
    image = Image.new("RGB", (width, height), "#F5F7FA")
    draw = ImageDraw.Draw(image)
    draw.text((70, 38), "T350 — tick parent versus pure closure front", fill="#172233", font=font(42, True))
    draw.text((72, 94), "Causal prefixes · exact common suffix · untouched cadence and scale holdout", fill="#657184", font=font(20))

    boxes = [
        (70, 145, 775, 690), (815, 145, 1585, 690), (1625, 145, 2330, 690),
        (70, 730, 775, 1370), (815, 730, 1585, 1370), (1625, 730, 2330, 1370),
    ]

    # 1. Representative paths on the 0-2 position cut.
    area = draw_panel(draw, boxes[0], "ARA position at each tick", "Different early paths become the same path after the merge")
    axes(draw, area, (0, 0.5, 1), (0, 1, 2), (0, 1), (0, 2), "normalised tick", "ARA position")
    for variant in ("gradual reference", "front-loaded", "early burst", "positive detour"):
        u = example_paths[variant]
        xp, _ = tick_coordinates(u)
        s = np.linspace(0, 1, len(u))
        points = [map_xy(area, float(a), float(b), (0, 1), (0, 2)) for a, b in zip(s[::3], xp[::3])]
        draw.line(points, fill=COLORS[variant], width=3)
    mx, _ = map_xy(area, 0.5, 0, (0, 1), (0, 2))
    draw.line((mx, area[1], mx, area[3]), fill="#222A36", width=2)
    draw.text((mx + 7, area[1] + 5), "merge", fill="#222A36", font=font(14, True))
    legend_items = ("gradual reference", "front-loaded", "early burst", "positive detour")
    lx, ly = area[0] + 10, area[1] + 13
    draw.rounded_rectangle((lx - 7, ly - 7, lx + 260, ly + 76), radius=8, fill="#FFFFFF", outline="#D5DCE5")
    for i, variant in enumerate(legend_items):
        yy = ly + i * 19
        draw.line((lx, yy + 7, lx + 25, yy + 7), fill=COLORS[variant], width=4)
        draw.text((lx + 34, yy), variant, fill="#4C5868", font=font(13))

    # 2. Matched history distance.
    area = draw_panel(draw, boxes[1], "History difference through time", "Distance from the gradual reference; closure is at 1.0")
    max_y = max(0.12, float(pair_df.history_distance.max()) * 1.08)
    axes(draw, area, (0.125, 0.5, 0.75, 1.0), (0, round(max_y / 2, 2), round(max_y, 2)), (0.1, 1), (0, max_y), "event progress", "history distance")
    selected = pair_df[(pair_df.split == "holdout") & (pair_df.duration == 769) & (pair_df.turns == 5) & (pair_df.amplitude == 0.24) & (pair_df.seed == 10)]
    for variant in ("front-loaded", "early burst", "positive detour", "pseudo-stochastic bridge"):
        part = selected[selected.variant == variant].sort_values("progress")
        points = [map_xy(area, float(r.progress), float(r.history_distance), (0.1, 1), (0, max_y)) for r in part.itertuples()]
        draw.line(points, fill=COLORS[variant], width=4)
    mx, _ = map_xy(area, 0.5, 0, (0.1, 1), (0, max_y))
    draw.line((mx, area[1], mx, area[3]), fill="#8A929C", width=2)
    legend_items = ("front-loaded", "early burst", "positive detour", "pseudo-stochastic bridge")
    lx, ly = area[2] - 255, area[1] + 13
    draw.rounded_rectangle((lx - 7, ly - 7, lx + 245, ly + 76), radius=8, fill="#FFFFFF", outline="#D5DCE5")
    for i, variant in enumerate(legend_items):
        yy = ly + i * 19
        draw.line((lx, yy + 7, lx + 25, yy + 7), fill=COLORS[variant], width=4)
        label = variant.replace("pseudo-stochastic", "p-stochastic")
        draw.text((lx + 34, yy), label, fill="#4C5868", font=font(13))

    # 3. Final identical state, retained history.
    area = draw_panel(draw, boxes[2], "Same present, different retained path", "All listed pairs have zero final-suffix state difference")
    summary = pair_df[(pair_df.split == "holdout") & (pair_df.progress == 1.0)].groupby("variant").history_distance.median().sort_values()
    max_bar = max(0.05, float(summary.max()) * 1.15)
    x0, y0, x1, y1 = area
    row_h = (y1 - y0) / max(len(summary), 1)
    for i, (variant, value) in enumerate(summary.items()):
        y = int(y0 + i * row_h + 7)
        label = variant.replace("pseudo-stochastic", "p-stochastic")
        draw.text((x0, y), label, fill="#4C5868", font=font(14))
        bx0 = x0 + 175
        bx1 = int(bx0 + (x1 - bx0 - 70) * value / max_bar)
        draw.rectangle((bx0, y + 2, bx1, y + 20), fill=COLORS[variant], outline="#344052")
        draw.text((bx1 + 7, y), f"{value:.3f}", fill="#344052", font=font(14, True))
    draw.text((x0, y1 + 9), "history-vector distance (current suffix delta = 0)", fill="#657184", font=font(14))

    # 4. Emergence and retention distributions.
    area = draw_panel(draw, boxes[3], "Parent-memory diagnostics", "Holdout matched pairs; frozen thresholds shown")
    metrics = [
        ("retained ≥0.02", result["parent_checks"]["retained_share"], 0.70),
        ("median final/peak", result["parent_checks"]["median_retention"], 0.30),
        ("early emergence score", 1 - result["parent_checks"]["median_emergence"], 0.25),
        ("low closure-jump score", 1 - result["parent_checks"]["median_closure_jump"], 0.75),
        ("cadence ≤0.12", result["parent_checks"]["cadence_share"], 0.80),
    ]
    x0, y0, x1, y1 = area
    row_h = 90
    for i, (label, value, threshold) in enumerate(metrics):
        y = y0 + i * row_h
        draw.text((x0, y), label, fill="#344052", font=font(17))
        bx0, bx1 = x0 + 245, x1 - 25
        draw.rectangle((bx0, y + 3, bx1, y + 28), fill="#EDF0F4", outline="#C8CFD8")
        draw.rectangle((bx0, y + 3, int(bx0 + (bx1 - bx0) * np.clip(value, 0, 1)), y + 28), fill="#2F6FB0")
        tx = int(bx0 + (bx1 - bx0) * threshold)
        draw.line((tx, y - 2, tx, y + 34), fill="#D49A2E", width=3)
        draw.text((bx1 + 7, y + 1), f"{value:.3f}", fill="#172233", font=font(15, True))

    # 5. Gate scorecard.
    area = draw_panel(draw, boxes[4], "Frozen hypothesis scorecard", "Blue = parent; gold = pure front; grey = local-front utility")
    x0, y0, x1, y1 = area
    for i, row in enumerate(gate_df.itertuples()):
        y = y0 + i * 62
        root = "#2F6FB0" if row.hypothesis == "parent" else ("#D49A2E" if row.hypothesis == "pure front" else "#8A929C")
        draw.ellipse((x0, y + 2, x0 + 24, y + 26), fill=root if row.passed else "#FFFFFF", outline=root, width=3)
        draw.text((x0 + 36, y), row.gate, fill="#273343", font=font(17, True))
        draw.text((x0 + 330, y), "PASS" if row.passed else "FAIL", fill=root, font=font(17, True))
        draw.text((x0 + 420, y), str(row.detail)[:34], fill="#657184", font=font(14))
    draw.text((x0, y1 - 52), f"Dominant instrument verdict: {result['dominant_verdict']}", fill="#172233", font=font(18, True))

    # 6. Local closure estimate.
    area = draw_panel(draw, boxes[5], "Tick as a local handover locator", "Current remaining distance / current step in the shared suffix")
    sample = closure_df[(closure_df.split == "holdout") & (closure_df.duration == 769) & (closure_df.turns == 5)].iloc[::20]
    max_ticks = float(max(sample.actual_ticks.max(), sample.predicted_ticks.max()))
    axes(draw, area, (0, max_ticks / 2, max_ticks), (0, max_ticks / 2, max_ticks), (0, max_ticks), (0, max_ticks), "actual ticks to closure", "predicted ticks")
    p0 = map_xy(area, 0, 0, (0, max_ticks), (0, max_ticks)); p1 = map_xy(area, max_ticks, max_ticks, (0, max_ticks), (0, max_ticks))
    draw.line((p0, p1), fill="#8A929C", width=3)
    for row in sample.itertuples():
        px, py = map_xy(area, float(row.actual_ticks), float(row.predicted_ticks), (0, max_ticks), (0, max_ticks))
        draw.ellipse((px - 4, py - 4, px + 4, py + 4), fill="#D49A2E", outline="#344052")

    draw.text((72, 1415), "Source: frozen T350 synthetic known-referee protocol · no universal e/Phi landmark used", fill="#657184", font=font(16))
    image.save(HERE / "T350_TICK_PARENT_CLOSURE_FRONT_FIGURE.png")


def main() -> None:
    expected_claim = "C4C5CE519F1F596172D1209AF033C88915004E6B04002EFF16F3B606B15241A5"
    expected_protocol = "C68DD4A2EB60A18034CF8A7B504F5FAE8D3ADBE7AC7ABC2E14BD32E3132EB35E"
    if sha256(CLAIM) != expected_claim or sha256(PROTOCOL) != expected_protocol:
        raise RuntimeError("Frozen T350 claim/protocol hash mismatch")

    path_rows: list[dict] = []
    prefix_rows: list[dict] = []
    raw_examples: list[dict] = []
    trajectories: dict[tuple, np.ndarray] = {}

    for split, spec in SPLITS.items():
        for duration in spec["durations"]:
            for turns in spec["turns"]:
                for amplitude in spec["amplitudes"]:
                    for seed_index in spec["seeds"]:
                        continuous_seed = stable_seed(split, turns, amplitude, seed_index)
                        config = (split, duration, turns, amplitude, seed_index)
                        for variant in VARIANTS:
                            u = generate_path(duration, turns, amplitude, continuous_seed, variant)
                            trajectories[config + (variant,)] = u
                            x_position, x_motion = tick_coordinates(u)
                            reconstructed = reconstruct_from_ticks(u[0], x_motion)
                            reconstruction_error = float(np.max(np.abs(reconstructed - u)))
                            path_rows.append({
                                "split": split, "duration": duration, "turns": turns,
                                "amplitude": amplitude, "seed": seed_index, "variant": variant,
                                "reconstruction_error": reconstruction_error,
                                "final_position": float(x_position[-1]),
                                "final_motion": float(x_motion[-1]),
                            })
                            for progress in CHECKPOINTS:
                                n = prefix_index(duration, float(progress))
                                hv = history_vector(u[:n])
                                row = {
                                    "split": split, "duration": duration, "turns": turns,
                                    "amplitude": amplitude, "seed": seed_index, "variant": variant,
                                    "progress": float(progress), "prefix_n": n,
                                    "x_p": float(2 * hv[0]), "x_r": float(2 * hv[1]),
                                }
                                row.update({f"rho_{i}": float(value) for i, value in enumerate(hv[2:], start=1)})
                                prefix_rows.append(row)
                            if split == "holdout" and duration == 769 and turns == 5 and amplitude == 0.24 and seed_index == 10:
                                for i in range(duration):
                                    raw_examples.append({
                                        "variant": variant, "tick": i, "progress": i / (duration - 1),
                                        "unwrapped": float(u[i]), "x_position": float(x_position[i]),
                                        "x_motion": float(x_motion[i]),
                                    })

    paths = pd.DataFrame(path_rows)
    prefixes = pd.DataFrame(prefix_rows)
    examples = pd.DataFrame(raw_examples)

    vector_columns = ["x_p", "x_r"] + [f"rho_{i}" for i in range(1, 7)]
    scaled = prefixes.copy()
    scaled[["x_p", "x_r"]] = scaled[["x_p", "x_r"]] / 2.0
    key = ["split", "duration", "turns", "amplitude", "seed", "progress"]
    reference = scaled[scaled.variant == "gradual reference"][key + vector_columns].rename(columns={c: f"ref_{c}" for c in vector_columns})
    paired = scaled[scaled.variant != "gradual reference"].merge(reference, on=key, validate="many_to_one")
    paired["history_distance"] = np.sqrt(np.mean(np.column_stack([(paired[c] - paired[f"ref_{c}"]) ** 2 for c in vector_columns]), axis=1))

    # Current/suffix equality is calculated directly from raw trajectories.
    pair_meta = []
    config_keys = ["split", "duration", "turns", "amplitude", "seed"]
    for config_values, group in paired.groupby(config_keys + ["variant"]):
        split, duration, turns, amplitude, seed_index, variant = config_values
        config = (split, duration, turns, amplitude, seed_index)
        u = trajectories[config + (variant,)]
        ref_u = trajectories[config + ("gradual reference",)]
        suffix_start = duration // 2
        suffix_error = float(np.max(np.abs(u[suffix_start:] - ref_u[suffix_start:])))
        _, xm = tick_coordinates(u); _, ref_xm = tick_coordinates(ref_u)
        recent_error = float(np.max(np.abs(xm[-32:] - ref_xm[-32:])))
        ordered = group.sort_values("progress")
        distances = ordered.history_distance.to_numpy()
        progress = ordered.progress.to_numpy()
        final_distance = float(distances[-1])
        peak_distance = float(np.max(distances))
        retention = final_distance / max(peak_distance, 1e-12)
        target = 0.5 * final_distance
        eligible = np.flatnonzero(distances >= target)
        emergence = float(progress[eligible[0]]) if len(eligible) and final_distance >= 0.02 else float("nan")
        closure_jump = float(abs(distances[-1] - distances[-2]) / max(peak_distance, 1e-12))
        pair_meta.append({
            "split": split, "duration": duration, "turns": turns, "amplitude": amplitude,
            "seed": seed_index, "variant": variant, "suffix_error": suffix_error,
            "recent_tick_error": recent_error, "final_history_distance": final_distance,
            "peak_history_distance": peak_distance, "retention_ratio": retention,
            "emergence_progress": emergence, "closure_jump_share": closure_jump,
        })
    pair_summary = pd.DataFrame(pair_meta)
    paired = paired.merge(pair_summary[config_keys + ["variant", "suffix_error", "recent_tick_error"]], on=config_keys + ["variant"], validate="many_to_one")

    # Same continuous path at two untouched cadences.
    cadence_rows = []
    hold_prefix = scaled[(scaled.split == "holdout") & (scaled.progress == 1.0)]
    for group_key, group in hold_prefix.groupby(["turns", "amplitude", "seed", "variant"]):
        if set(group.duration) != set(SPLITS["holdout"]["durations"]):
            continue
        low = group[group.duration == SPLITS["holdout"]["durations"][0]].iloc[0]
        high = group[group.duration == SPLITS["holdout"]["durations"][1]].iloc[0]
        distance = math.sqrt(float(np.mean([(low[c] - high[c]) ** 2 for c in vector_columns])))
        cadence_rows.append({"turns": group_key[0], "amplitude": group_key[1], "seed": group_key[2], "variant": group_key[3], "history_distance": distance})
    cadence = pd.DataFrame(cadence_rows)

    # The local closure locator is evaluated only in the exact common suffix.
    closure_rows = []
    for split, spec in SPLITS.items():
        for duration in spec["durations"]:
            for turns in spec["turns"]:
                u = trajectories[(split, duration, turns, spec["amplitudes"][0], spec["seeds"][0], "gradual reference")]
                for i in range(duration // 2 + 1, duration - 1):
                    step = u[i] - u[i - 1]
                    predicted = (u[-1] - u[i]) / max(step, 1e-15)
                    actual = duration - 1 - i
                    closure_rows.append({
                        "split": split, "duration": duration, "turns": turns, "tick": i,
                        "actual_ticks": float(actual), "predicted_ticks": float(predicted),
                        "absolute_error": float(abs(predicted - actual)),
                    })
    closure = pd.DataFrame(closure_rows)

    hold_paths = paths[paths.split == "holdout"]
    hold_pairs = pair_summary[pair_summary.split == "holdout"]
    hold_cadence = cadence
    hold_closure = closure[closure.split == "holdout"]

    parent_checks = {
        "max_reconstruction_error": float(hold_paths.reconstruction_error.max()),
        "retained_share": float((hold_pairs.final_history_distance >= 0.02).mean()),
        "median_retention": float(hold_pairs.retention_ratio.median()),
        "median_emergence": float(hold_pairs.emergence_progress.dropna().median()),
        "median_closure_jump": float(hold_pairs.closure_jump_share.median()),
        "cadence_median": float(hold_cadence.history_distance.median()),
        "cadence_share": float((hold_cadence.history_distance <= 0.12).mean()),
    }
    front_checks = {
        "final_small_share": float((hold_pairs.final_history_distance <= 0.02).mean()),
        "median_final_distance": float(hold_pairs.final_history_distance.median()),
        "median_emergence": parent_checks["median_emergence"],
        "median_closure_jump": parent_checks["median_closure_jump"],
        "local_median_error": float(hold_closure.absolute_error.median()),
        "local_p95_error": float(hold_closure.absolute_error.quantile(0.95)),
    }

    p1 = parent_checks["max_reconstruction_error"] < 1e-9
    p2 = parent_checks["retained_share"] >= 0.70 and parent_checks["median_retention"] >= 0.30
    p3 = parent_checks["median_emergence"] <= 0.75 and parent_checks["median_closure_jump"] < 0.25
    p4 = parent_checks["cadence_median"] <= 0.08 and parent_checks["cadence_share"] >= 0.80
    f1 = front_checks["final_small_share"] >= 0.90 and front_checks["median_final_distance"] <= 0.01
    f2 = front_checks["median_emergence"] >= 0.90 and front_checks["median_closure_jump"] >= 0.50
    f3 = front_checks["local_median_error"] < 1.0 and front_checks["local_p95_error"] < 2.0

    gates = pd.DataFrame([
        {"hypothesis": "parent", "gate": "P1 tick reconstruction", "passed": p1, "detail": f"max {parent_checks['max_reconstruction_error']:.2e}"},
        {"hypothesis": "parent", "gate": "P2 retained history", "passed": p2, "detail": f"share {parent_checks['retained_share']:.3f}; retention {parent_checks['median_retention']:.3f}"},
        {"hypothesis": "parent", "gate": "P3 pre-closure emergence", "passed": p3, "detail": f"t {parent_checks['median_emergence']:.3f}; jump {parent_checks['median_closure_jump']:.3f}"},
        {"hypothesis": "parent", "gate": "P4 cadence stability", "passed": p4, "detail": f"median {parent_checks['cadence_median']:.3f}; share {parent_checks['cadence_share']:.3f}"},
        {"hypothesis": "pure front", "gate": "F1 current sufficiency", "passed": f1, "detail": f"small {front_checks['final_small_share']:.3f}; median {front_checks['median_final_distance']:.3f}"},
        {"hypothesis": "pure front", "gate": "F2 boundary emergence", "passed": f2, "detail": f"t {front_checks['median_emergence']:.3f}; jump {front_checks['median_closure_jump']:.3f}"},
        {"hypothesis": "local front", "gate": "F3 handover locator", "passed": f3, "detail": f"median {front_checks['local_median_error']:.3g}; p95 {front_checks['local_p95_error']:.3g}"},
    ])

    parent_supported = bool(p1 and p2 and p3 and p4)
    pure_front_supported = bool(f1 and f2)
    local_front_supported = bool(f3)
    if parent_supported and not pure_front_supported:
        dominant = "parent memory; local tick remains a closure locator" if local_front_supported else "parent memory"
    elif pure_front_supported and not parent_supported:
        dominant = "pure closure front"
    elif parent_supported and pure_front_supported:
        dominant = "both strong readings supported; hierarchy unresolved"
    else:
        dominant = "neither strong reading fully supported"

    result = {
        "test": "T350 tick-parent versus closure-front",
        "run_date": "2026-08-11",
        "evidence_class": "synthetic known-referee causal instrument calibration",
        "claim_hash": sha256(CLAIM),
        "protocol_hash": sha256(PROTOCOL),
        "counts": {
            "trajectories": int(len(paths)), "holdout_trajectories": int(len(hold_paths)),
            "matched_pairs": int(len(pair_summary)), "holdout_pairs": int(len(hold_pairs)),
            "prefix_measurements": int(len(prefixes)), "cadence_pairs": int(len(cadence)),
        },
        "parent_supported": parent_supported,
        "pure_closure_front_supported": pure_front_supported,
        "local_closure_locator_supported": local_front_supported,
        "dominant_verdict": dominant,
        "parent_checks": parent_checks,
        "front_checks": front_checks,
        "gates": gates.to_dict(orient="records"),
        "boundaries": [
            "Synthetic instrument relation only; not a universal physical causal result.",
            "Tick reconstruction and local closure estimation are partly algebraic.",
            "Retained history, causal emergence and cadence stability are the load-bearing comparisons.",
        ],
    }

    paths.to_csv(HERE / "T350_TICK_PARENT_CLOSURE_FRONT_PATHS.csv", index=False)
    prefixes.to_csv(HERE / "T350_TICK_PARENT_CLOSURE_FRONT_PREFIXES.csv", index=False)
    paired.to_csv(HERE / "T350_TICK_PARENT_CLOSURE_FRONT_PAIR_CURVES.csv", index=False)
    pair_summary.to_csv(HERE / "T350_TICK_PARENT_CLOSURE_FRONT_PAIR_SUMMARY.csv", index=False)
    cadence.to_csv(HERE / "T350_TICK_PARENT_CLOSURE_FRONT_CADENCE.csv", index=False)
    closure.to_csv(HERE / "T350_TICK_PARENT_CLOSURE_FRONT_LOCAL_CLOSURE.csv", index=False)
    gates.to_csv(HERE / "T350_TICK_PARENT_CLOSURE_FRONT_FROZEN_GATES.csv", index=False)
    examples.to_csv(HERE / "T350_TICK_PARENT_CLOSURE_FRONT_EXAMPLES.csv", index=False)
    (HERE / "T350_TICK_PARENT_CLOSURE_FRONT_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    example_paths = {v: trajectories[("holdout", 769, 5, 0.24, 10, v)] for v in VARIANTS}
    make_figure(prefixes, paired, cadence, closure, gates, result, example_paths)

    report = f"""# T350 — Tick-parent versus pure closure-front

**Run date:** 11 August 2026  
**Evidence boundary:** synthetic known-referee causal instrument calibration  
**Parent-memory verdict:** **{'SUPPORTED' if parent_supported else 'NOT SUPPORTED'} — {int(p1)+int(p2)+int(p3)+int(p4)}/4 frozen gates passed**  
**Pure closure-front verdict:** **{'SUPPORTED' if pure_front_supported else 'NOT SUPPORTED'} — {int(f1)+int(f2)}/2 frozen gates passed**  
**Local tick/front verdict:** **{'SUPPORTED' if local_front_supported else 'NOT SUPPORTED'}**

## Outcome first

The dominant instrument result is **{dominant}**.

The test gave every matched path the same endpoint and an exactly identical
final half-path. Therefore the final current state, final motion and all recent
ticks were identical. The only remaining difference was the ordered early
history.

## Parent-memory checks

| Check | Holdout result | Frozen gate |
|---|---:|---:|
| maximum tick reconstruction error | `{parent_checks['max_reconstruction_error']:.3e}` | `<1e-9` |
| pairs retaining final history distance >=0.02 | `{parent_checks['retained_share']:.4f}` | `>=0.70` |
| median final/peak history retention | `{parent_checks['median_retention']:.4f}` | `>=0.30` |
| median half-final emergence time | `{parent_checks['median_emergence']:.4f}` | `<=0.75` |
| median closure-jump share | `{parent_checks['median_closure_jump']:.4f}` | `<0.25` |
| median cadence distance | `{parent_checks['cadence_median']:.4f}` | `<=0.08` |
| cadence pairs within 0.12 | `{parent_checks['cadence_share']:.4f}` | `>=0.80` |

## Pure closure-front checks

| Check | Holdout result | Frozen gate |
|---|---:|---:|
| final history distances <=0.02 | `{front_checks['final_small_share']:.4f}` | `>=0.90` |
| median final history distance | `{front_checks['median_final_distance']:.4f}` | `<=0.01` |
| median half-final emergence time | `{front_checks['median_emergence']:.4f}` | `>=0.90` |
| median closure-jump share | `{front_checks['median_closure_jump']:.4f}` | `>=0.50` |

## Local closure-front utility

Inside the shared linear suffix, current remaining distance divided by current
motion predicted the final handover with median error
`{front_checks['local_median_error']:.6g}` ticks and 95th-percentile error
`{front_checks['local_p95_error']:.6g}` ticks. This is a local geometric locator,
not evidence that the front creates the stored history.

## Interpretation boundary

Exact tick reconstruction and exact closure timing in the common suffix are
partly algebraic sanity checks. The load-bearing result is whether the frozen
history vector retains early ordered information after half an event of
identical present-state ticks, whether that distinction appears before final
closure, and whether it survives cadence changes.

Passing the parent gates means the current ARA implementation behaves as:

`ordered tick-state children -> compressed path/history parent`.

It does not exclude a simultaneous top-down parent constraint or prove that
every physical system preserves the same amount of history.

## Artifact index

- frozen claim: `T350_TICK_PARENT_CLOSURE_FRONT_CLAIM_PACKET_v1.md`
- frozen protocol: `T350_TICK_PARENT_CLOSURE_FRONT_PROTOCOL_v1_FROZEN.md`
- path/prefix data: `T350_TICK_PARENT_CLOSURE_FRONT_PATHS.csv`, `T350_TICK_PARENT_CLOSURE_FRONT_PREFIXES.csv`
- matched curves and summary: `T350_TICK_PARENT_CLOSURE_FRONT_PAIR_CURVES.csv`, `T350_TICK_PARENT_CLOSURE_FRONT_PAIR_SUMMARY.csv`
- cadence and local closure: `T350_TICK_PARENT_CLOSURE_FRONT_CADENCE.csv`, `T350_TICK_PARENT_CLOSURE_FRONT_LOCAL_CLOSURE.csv`
- frozen gates: `T350_TICK_PARENT_CLOSURE_FRONT_FROZEN_GATES.csv`
- machine result: `T350_TICK_PARENT_CLOSURE_FRONT_RESULTS.json`
- main figure: `T350_TICK_PARENT_CLOSURE_FRONT_FIGURE.png`
"""
    (HERE / "T350_TICK_PARENT_CLOSURE_FRONT_REPORT_2026-08-11.md").write_text(report, encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
