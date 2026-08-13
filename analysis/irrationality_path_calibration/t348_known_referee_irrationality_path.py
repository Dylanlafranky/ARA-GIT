#!/usr/bin/env python3
"""T348 known-referee Irrationality path calibration.

Orientation
-----------
x_P: 0 = finite/reused addresses; 2 = open/densely resolving potential.
x_R: 0 = relation-determined; 2 = stochastic residual.

Evidence boundary
-----------------
This is a fixed-seed, self-contained synthetic instrument calibration. Generator
labels and parameters are referee truth only and never enter the coordinate
calculations. A pass is not evidence that nature instantiates the coordinate.

Frozen protocol
---------------
T348_IRRATIONALITY_PATH_KNOWN_REFEREE_PROTOCOL_v1_FROZEN.md
SHA-256 4EB33854992EF4B30B70142814804C276B95C8794871D55F679B68A5ABB23547
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
SEED = 348_20260811
N_PER_PARAMETER = 48
LENGTH = 4096
HORIZONS = (256, 512, 1024, 2048, 4096)
RESOLUTIONS = np.array((16, 32, 64, 128, 256), dtype=int)
MAX_LAG = 512
K_NEIGHBOURS = 5
BOOTSTRAPS = 2000
MERSENNE_61 = (1 << 61) - 1

FAMILIES = (
    "periodic rational",
    "irrational rotation",
    "deterministic chaos",
    "finite stochastic",
    "continuous stochastic",
)

EXPECTED_SECTOR = {
    "periodic rational": (0, 0),
    "irrational rotation": (1, 0),
    "deterministic chaos": (1, 0),
    "finite stochastic": (0, 1),
    "continuous stochastic": (1, 1),
}

COLORS = {
    "periodic rational": "#2F6FB0",
    "irrational rotation": "#D49A2E",
    "deterministic chaos": "#D86D32",
    "finite stochastic": "#738C3A",
    "continuous stochastic": "#C45A86",
}

MARKERS = {
    "periodic rational": "circle",
    "irrational rotation": "square",
    "deterministic chaos": "triangle",
    "finite stochastic": "diamond",
    "continuous stochastic": "cross",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def stable_seed(*parts: object) -> int:
    payload = "|".join(map(str, (SEED,) + parts)).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "little")


def coprime_numerator(q: int, index: int) -> int:
    candidates = [p for p in range(1, q) if math.gcd(p, q) == 1]
    return candidates[index % len(candidates)]


def periodic_rotation(q: int, index: int, length: int) -> np.ndarray:
    p = coprime_numerator(q, index)
    phase = index % q
    return ((phase + p * np.arange(length, dtype=np.int64)) % q) / float(q)


def irrational_rotation(d: int, index: int, length: int) -> np.ndarray:
    advance = math.sqrt(d) - math.floor(math.sqrt(d))
    rng = np.random.default_rng(stable_seed("irr", d, index))
    phase = rng.random()
    return (phase + advance * np.arange(length, dtype=float)) % 1.0


def chaotic_circle(m: int, offset_d: int, index: int, length: int) -> np.ndarray:
    """Exact fine-grid implementation of z -> (m z + c) mod 1.

    Integer recurrence on the 61-bit prime grid prevents the floating-point
    dyadic collapse that an ordinary double implementation of the expanding
    circle map would introduce after only tens of iterations.
    """
    frac = math.sqrt(offset_d) - math.floor(math.sqrt(offset_d))
    c_num = max(1, min(MERSENNE_61 - 1, int(frac * MERSENNE_61)))
    rng = np.random.default_rng(stable_seed("chaos", m, offset_d, index))
    x = int(rng.integers(1, 1 << 61, dtype=np.int64)) % MERSENNE_61
    out = np.empty(length, dtype=float)
    for t in range(length):
        out[t] = x / MERSENNE_61
        x = (m * x + c_num) % MERSENNE_61
    return out


def finite_stochastic(q: int, index: int, length: int) -> np.ndarray:
    rng = np.random.default_rng(stable_seed("finite-stoch", q, index))
    return rng.integers(0, q, size=length) / float(q)


def continuous_stochastic(a: float, b: float, index: int, length: int) -> np.ndarray:
    rng = np.random.default_rng(stable_seed("continuous-stoch", a, b, index))
    return rng.beta(a, b, size=length)


def generate_paths() -> list[dict]:
    paths: list[dict] = []
    specs = {
        "calibration": {
            "periodic rational": [("q", q) for q in (5, 7, 9, 11, 13)],
            "irrational rotation": [("d", d) for d in (2, 3, 5, 7, 11)],
            "deterministic chaos": [("m/d", (2, 2)), ("m/d", (3, 3))],
            "finite stochastic": [("q", q) for q in (5, 7, 9, 11, 13)],
            "continuous stochastic": [("a/b", (1.0, 1.0)), ("a/b", (2.0, 2.0))],
        },
        "holdout": {
            "periodic rational": [("q", q) for q in (6, 8, 10, 12, 14, 15, 17)],
            "irrational rotation": [("d", d) for d in (13, 17, 19, 23, 29)],
            "deterministic chaos": [("m/d", (4, 5)), ("m/d", (5, 7))],
            "finite stochastic": [("q", q) for q in (6, 8, 10, 12, 14, 15, 17)],
            "continuous stochastic": [("a/b", (0.8, 0.8)), ("a/b", (3.0, 3.0))],
        },
    }
    for split, families in specs.items():
        for family, parameters in families.items():
            for param_index, (param_name, param) in enumerate(parameters):
                for rep in range(N_PER_PARAMETER):
                    identity = f"{split}:{family}:{param_index}:{rep}"
                    if family == "periodic rational":
                        z = periodic_rotation(int(param), rep, LENGTH)
                    elif family == "irrational rotation":
                        z = irrational_rotation(int(param), rep, LENGTH)
                    elif family == "deterministic chaos":
                        m, offset_d = param
                        z = chaotic_circle(int(m), int(offset_d), rep, LENGTH)
                    elif family == "finite stochastic":
                        z = finite_stochastic(int(param), rep, LENGTH)
                    else:
                        a, b = param
                        z = continuous_stochastic(float(a), float(b), rep, LENGTH)
                    paths.append(
                        {
                            "path_id": identity,
                            "split": split,
                            "family": family,
                            "parameter": repr(param),
                            "parameter_index": param_index,
                            "replicate": rep,
                            "z": z,
                        }
                    )
    return paths


def address_openness(z: np.ndarray) -> tuple[float, list[int]]:
    occupied = []
    for bins in RESOLUTIONS:
        idx = np.minimum((z * bins).astype(int), bins - 1)
        occupied.append(int(np.unique(idx).size))
    beta = float(np.polyfit(np.log(RESOLUTIONS), np.log(occupied), 1)[0])
    return 2.0 * float(np.clip(beta, 0.0, 1.0)), occupied


def circular_loss(actual: np.ndarray, predicted: np.ndarray) -> np.ndarray:
    return 1.0 - np.cos(2.0 * np.pi * (actual - predicted))


def circular_mean(values: np.ndarray) -> float:
    v = np.mean(np.exp(2j * np.pi * values))
    if abs(v) < 1e-15:
        return 0.0
    return float((np.angle(v) / (2.0 * np.pi)) % 1.0)


def knn_circle_predict(train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray, k: int) -> np.ndarray:
    order = np.argsort(train_x)
    sx = train_x[order]
    sy = train_y[order]
    n = len(sx)
    insertion = np.searchsorted(sx, test_x)
    radius = max(k + 2, 7)
    offsets = np.arange(-radius, radius + 1)
    candidate_idx = (insertion[:, None] + offsets[None, :]) % n
    candidate_x = sx[candidate_idx]
    distance = np.abs(candidate_x - test_x[:, None])
    distance = np.minimum(distance, 1.0 - distance)
    nearest_pos = np.argpartition(distance, kth=k - 1, axis=1)[:, :k]
    nearest_idx = np.take_along_axis(candidate_idx, nearest_pos, axis=1)
    neighbour_y = sy[nearest_idx]
    mean_vector = np.mean(np.exp(2j * np.pi * neighbour_y), axis=1)
    fallback = circular_mean(train_y)
    prediction = (np.angle(mean_vector) / (2.0 * np.pi)) % 1.0
    prediction[np.abs(mean_vector) < 1e-12] = fallback
    return prediction


def stochastic_residual(z: np.ndarray) -> tuple[float, float, float]:
    split = len(z) // 2
    train_x = z[: split - 1]
    train_y = z[1:split]
    test_x = z[split:-1]
    test_y = z[split + 1 :]
    prediction = knn_circle_predict(train_x, train_y, test_x, K_NEIGHBOURS)
    null_prediction = np.full_like(test_y, circular_mean(train_y))
    local_loss = float(np.mean(circular_loss(test_y, prediction)))
    null_loss = float(np.mean(circular_loss(test_y, null_prediction)))
    ratio = local_loss / max(null_loss, 1e-12)
    return 2.0 * min(1.0, ratio), local_loss, null_loss


def closure_history(z: np.ndarray, max_lag: int = MAX_LAG) -> tuple[np.ndarray, np.ndarray]:
    n = len(z)
    max_lag = min(max_lag, n // 4)
    u = np.exp(2j * np.pi * z)
    nfft = 1 << (2 * n - 1).bit_length()
    f = np.fft.fft(u, nfft)
    raw = np.fft.ifft(f * np.conj(f))[: max_lag + 1]
    raw = raw / np.arange(n, n - max_lag - 1, -1)
    r = raw[1:]
    rho = np.abs(r)
    distance = np.abs(np.angle(r)) / np.pi
    return rho.astype(float), distance.astype(float)


def best_coherent_miss(rho: np.ndarray, distance: np.ndarray, limit: int) -> float:
    limit = min(limit, len(rho))
    mask = rho[:limit] > 0.90
    if not np.any(mask):
        return float("nan")
    values = distance[:limit][mask]
    nonzero = values[values > 1e-12]
    if nonzero.size == 0:
        return 0.0
    return float(np.min(nonzero))


def exact_closure(rho: np.ndarray, distance: np.ndarray, limit: int = 64) -> bool:
    limit = min(limit, len(rho))
    return bool(np.any((rho[:limit] > 1.0 - 1e-10) & (distance[:limit] < 1e-12)))


def measure_path(z: np.ndarray) -> dict:
    x_p, occupied = address_openness(z)
    x_r, local_loss, null_loss = stochastic_residual(z)
    return {
        "x_p": x_p,
        "x_r": x_r,
        "local_loss": local_loss,
        "null_loss": null_loss,
        **{f"occupied_{b}": n for b, n in zip(RESOLUTIONS, occupied)},
    }


def shuffled(z: np.ndarray, path_id: str) -> np.ndarray:
    rng = np.random.default_rng(stable_seed("shuffle", path_id))
    return z[rng.permutation(len(z))]


def bootstrap_median_ci(values: np.ndarray, rng: np.random.Generator) -> tuple[float, float, float]:
    values = np.asarray(values, dtype=float)
    med = float(np.median(values))
    indices = rng.integers(0, len(values), size=(BOOTSTRAPS, len(values)))
    samples = np.median(values[indices], axis=1)
    lo, hi = np.quantile(samples, (0.025, 0.975))
    return med, float(lo), float(hi)


def write_csv(path: Path, rows: list[dict]) -> None:
    pd.DataFrame(rows).to_csv(path, index=False)


def font(size: int, bold: bool = False):
    names = ["arialbd.ttf" if bold else "arial.ttf", "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_marker(draw: ImageDraw.ImageDraw, x: float, y: float, family: str, r: int = 5) -> None:
    color = COLORS[family]
    marker = MARKERS[family]
    if marker == "circle":
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color, outline="#23313F")
    elif marker == "square":
        draw.rectangle((x - r, y - r, x + r, y + r), fill=color, outline="#23313F")
    elif marker == "triangle":
        draw.polygon(((x, y - r - 1), (x - r, y + r), (x + r, y + r)), fill=color, outline="#23313F")
    elif marker == "diamond":
        draw.polygon(((x, y - r), (x - r, y), (x, y + r), (x + r, y)), fill=color, outline="#23313F")
    else:
        draw.line((x - r, y - r, x + r, y + r), fill=color, width=3)
        draw.line((x - r, y + r, x + r, y - r), fill=color, width=3)


def axes(draw, box, title, xlabel, ylabel):
    x0, y0, x1, y1 = box
    draw.text((x0, y0 - 32), title, font=font(22, True), fill="#18212B")
    draw.line((x0, y1, x1, y1), fill="#263442", width=2)
    draw.line((x0, y0, x0, y1), fill="#263442", width=2)
    draw.text(((x0 + x1) / 2 - 70, y1 + 12), xlabel, font=font(16), fill="#263442")
    draw.text((x0 + 10, y0 + 8), f"↑ {ylabel}", font=font(15), fill="#52606D")


def make_figure(path_rows: pd.DataFrame, closure_curve: pd.DataFrame, gate_rows: list[dict], output: Path) -> None:
    img = Image.new("RGB", (1900, 1380), "#F7F9FB")
    draw = ImageDraw.Draw(img)
    draw.text((70, 34), "T348 — known-referee Irrationality path calibration", font=font(34, True), fill="#18212B")
    draw.text((70, 80), "Holdout geometry · raw ordered states · poles are reference identities", font=font(19), fill="#52606D")

    # Panel 1: ARA plane.
    box = (110, 180, 870, 760)
    axes(draw, box, "Holdout ARA path/history plane", "address openness 0 → 2", "stochastic residual 0 → 2")
    x0, y0, x1, y1 = box
    for v in (0, 0.5, 1, 1.5, 2):
        px = x0 + (x1 - x0) * v / 2
        py = y1 - (y1 - y0) * v / 2
        draw.line((px, y0, px, y1), fill="#DDE3E8" if v != 1 else "#6B7280", width=1 if v != 1 else 2)
        draw.line((x0, py, x1, py), fill="#DDE3E8" if v != 1 else "#6B7280", width=1 if v != 1 else 2)
        draw.text((px - 8, y1 + 34), f"{v:g}", font=font(14), fill="#52606D")
        draw.text((x0 - 32, py - 8), f"{v:g}", font=font(14), fill="#52606D")
    draw.text((x0 + 18, y0 + 42), "finite / stochastic", font=font(13), fill="#8A949E")
    draw.text((x1 - 145, y0 + 42), "open / stochastic", font=font(13), fill="#8A949E")
    draw.text((x0 + 18, y1 - 30), "finite / determinate", font=font(13), fill="#8A949E")
    draw.text((x1 - 152, y1 - 30), "open / determinate", font=font(13), fill="#8A949E")
    final = path_rows[(path_rows["split"] == "holdout") & (path_rows["horizon"] == LENGTH) & (path_rows["control"] == "chronological")]
    for family in FAMILIES:
        part = final[final["family"] == family].iloc[:: max(1, len(final[final["family"] == family]) // 80)]
        for row in part.itertuples():
            px = x0 + (x1 - x0) * row.x_p / 2
            py = y1 - (y1 - y0) * row.x_r / 2
            draw_marker(draw, px, py, family, 4)

    # Legend.
    ly = 835
    for i, family in enumerate(FAMILIES):
        lx = 110 + (i % 3) * 260
        yy = ly + (i // 3) * 30
        draw_marker(draw, lx, yy + 7, family, 5)
        draw.text((lx + 14, yy), family, font=font(15), fill="#263442")

    # Panel 2: medians.
    box2 = (1030, 180, 1800, 760)
    axes(draw, box2, "Family median coordinates", "ARA coordinate", "holdout family")
    x0, y0, x1, y1 = box2
    draw.line((x0 + (x1 - x0) / 2, y0, x0 + (x1 - x0) / 2, y1), fill="#6B7280", width=2)
    for v in (0, 1, 2):
        px = x0 + (x1 - x0) * v / 2
        draw.text((px - 8, y1 + 34), f"{v:g}", font=font(14), fill="#52606D")
    for i, family in enumerate(FAMILIES):
        part = final[final["family"] == family]
        xp = float(part["x_p"].median())
        xr = float(part["x_r"].median())
        yy = y0 + 65 + i * 95
        draw.text((x0 + 8, yy - 25), family, font=font(16, True), fill="#263442")
        for value, label, offset, fill in ((xp, "P", 0, COLORS[family]), (xr, "R", 24, "#FFFFFF")):
            px = x0 + (x1 - x0) * value / 2
            draw.line((x0, yy + offset, px, yy + offset), fill=COLORS[family], width=8)
            draw.ellipse((px - 7, yy + offset - 7, px + 7, yy + offset + 7), fill=fill, outline=COLORS[family], width=2)
            draw.text((px + 12, yy + offset - 10), f"{label} {value:.3f}", font=font(14), fill="#263442")

    # Panel 3: closure coherence.
    box3 = (110, 930, 1060, 1280)
    axes(draw, box3, "Closure-history coherence", "lag h (1–128 shown)", "median ρ")
    x0, y0, x1, y1 = box3
    for v in (0, 0.5, 1):
        py = y1 - (y1 - y0) * v
        draw.line((x0, py, x1, py), fill="#DDE3E8", width=1)
        draw.text((x0 - 40, py - 8), f"{v:g}", font=font(14), fill="#52606D")
    for family in FAMILIES:
        part = closure_curve[(closure_curve["split"] == "holdout") & (closure_curve["control"] == "chronological") & (closure_curve["family"] == family) & (closure_curve["lag"] <= 128)]
        points = []
        for row in part.itertuples():
            px = x0 + (x1 - x0) * (row.lag - 1) / 127
            py = y1 - (y1 - y0) * row.median_rho
            points.append((px, py))
        if len(points) > 1:
            draw.line(points, fill=COLORS[family], width=3)

    # Panel 4: control changes.
    box4 = (1220, 930, 1800, 1280)
    axes(draw, box4, "Chronology-destruction change", "median shuffled − chronological", "family")
    x0, y0, x1, y1 = box4
    zero = x0 + (x1 - x0) * 0.10 / 2.20
    draw.line((zero, y0, zero, y1), fill="#6B7280", width=2)
    controls = path_rows[(path_rows["split"] == "holdout") & (path_rows["horizon"] == LENGTH)]
    for i, family in enumerate(FAMILIES):
        c = controls[(controls["family"] == family) & (controls["control"] == "chronological")].set_index("path_id")
        s = controls[(controls["family"] == family) & (controls["control"] == "shuffled")].set_index("path_id")
        ids = c.index.intersection(s.index)
        dxr = float(np.median(s.loc[ids, "x_r"] - c.loc[ids, "x_r"]))
        dxp = float(np.median(s.loc[ids, "x_p"] - c.loc[ids, "x_p"]))
        yy = y0 + 55 + i * 58
        draw.text((x0 + 4, yy - 20), family, font=font(14, True), fill="#263442")
        for value, offset, label in ((dxr, 0, "ΔR"), (dxp, 18, "ΔP")):
            px = x0 + (x1 - x0) * (value + 0.10) / 2.20
            draw.line((zero, yy + offset, px, yy + offset), fill=COLORS[family], width=6)
            draw.text((px + 7, yy + offset - 8), f"{label} {value:+.3f}", font=font(12), fill="#263442")

    passed = sum(bool(row["passed"]) for row in gate_rows)
    draw.text((70, 1335), f"Frozen gates passed: {passed}/{len(gate_rows)} · synthetic instrument calibration only", font=font(17, True), fill="#263442")
    img.save(output)


def make_circle_examples(examples: dict[str, np.ndarray], output: Path) -> None:
    img = Image.new("RGB", (1900, 470), "#F7F9FB")
    draw = ImageDraw.Draw(img)
    draw.text((55, 25), "T348 holdout circle traces — first 160 ordered states", font=font(28, True), fill="#18212B")
    for i, family in enumerate(FAMILIES):
        cx = 190 + i * 375
        cy = 245
        radius = 135
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline="#AAB4BE", width=2)
        z = examples[family][:160]
        pts = [(cx + radius * math.cos(2 * math.pi * v), cy - radius * math.sin(2 * math.pi * v)) for v in z]
        draw.line(pts, fill=COLORS[family], width=2)
        for p in pts[::20]:
            draw_marker(draw, p[0], p[1], family, 4)
        draw.text((cx - 125, 405), family, font=font(16, True), fill="#263442")
    draw.text((55, 445), "Descriptive projection only; circle traces are not used by any frozen scoring gate.", font=font(14), fill="#52606D")
    img.save(output)


def main() -> None:
    protocol = HERE / "T348_IRRATIONALITY_PATH_KNOWN_REFEREE_PROTOCOL_v1_FROZEN.md"
    claim = HERE / "T348_IRRATIONALITY_PATH_KNOWN_REFEREE_CLAIM_PACKET_v1.md"
    print("T348 provenance")
    print(f"  seed={SEED} length={LENGTH} n_per_parameter={N_PER_PARAMETER}")
    print(f"  protocol_sha256={sha256(protocol)}")
    print(f"  claim_sha256={sha256(claim)}")

    paths = generate_paths()
    print(f"  generated_paths={len(paths)}")
    path_rows: list[dict] = []
    closure_rows: list[dict] = []
    closure_arrays: dict[tuple[str, str, str], list[np.ndarray]] = defaultdict(list)
    example_paths: dict[str, np.ndarray] = {}

    # Pair paths within split/family across parameter blocks for broken-lineage control.
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for item in paths:
        grouped[(item["split"], item["family"])].append(item)
    broken_partner: dict[str, np.ndarray] = {}
    for group in grouped.values():
        shift = N_PER_PARAMETER
        for i, item in enumerate(group):
            broken_partner[item["path_id"]] = group[(i + shift) % len(group)]["z"]

    for path_number, item in enumerate(paths, start=1):
        z = item["z"]
        if item["split"] == "holdout" and item["family"] not in example_paths:
            example_paths[item["family"]] = z.copy()
        base = {k: item[k] for k in ("path_id", "split", "family", "parameter", "parameter_index", "replicate")}

        for horizon in HORIZONS:
            measured = measure_path(z[:horizon])
            path_rows.append({**base, "horizon": horizon, "control": "chronological", **measured})

        # Frozen controls are required only at the final horizon.
        z_shuffle = shuffled(z, item["path_id"])
        z_reverse = z[::-1].copy()
        partner = broken_partner[item["path_id"]]
        half = LENGTH // 2
        z_broken = np.concatenate((z[:half], partner[half:]))
        for control, control_z in (("shuffled", z_shuffle), ("reversed", z_reverse), ("broken_lineage", z_broken)):
            measured = measure_path(control_z)
            path_rows.append({**base, "horizon": LENGTH, "control": control, **measured})

        for control, control_z in (("chronological", z), ("shuffled", z_shuffle)):
            rho, distance = closure_history(control_z)
            closure_arrays[(item["split"], item["family"], control)].append(rho)
            closure_rows.append(
                {
                    **base,
                    "control": control,
                    "mean_rho": float(np.median(rho)),
                    "best_miss_64": best_coherent_miss(rho, distance, 64),
                    "best_miss_512": best_coherent_miss(rho, distance, 512),
                    "exact_closure_64": exact_closure(rho, distance, 64),
                }
            )
        if path_number % 200 == 0:
            print(f"  measured {path_number}/{len(paths)} paths")

    path_df = pd.DataFrame(path_rows)
    closure_df = pd.DataFrame(closure_rows)
    write_csv(HERE / "T348_IRRATIONALITY_PATH_METRICS.csv", path_rows)
    write_csv(HERE / "T348_IRRATIONALITY_CLOSURE_SUMMARY.csv", closure_rows)

    curve_rows: list[dict] = []
    for (split, family, control), arrays in closure_arrays.items():
        matrix = np.vstack(arrays)
        med = np.median(matrix, axis=0)
        q25 = np.quantile(matrix, 0.25, axis=0)
        q75 = np.quantile(matrix, 0.75, axis=0)
        for lag, values in enumerate(zip(med, q25, q75), start=1):
            curve_rows.append(
                {
                    "split": split,
                    "family": family,
                    "control": control,
                    "lag": lag,
                    "median_rho": float(values[0]),
                    "q25_rho": float(values[1]),
                    "q75_rho": float(values[2]),
                    "n_paths": int(matrix.shape[0]),
                }
            )
    curve_df = pd.DataFrame(curve_rows)
    curve_df.to_csv(HERE / "T348_IRRATIONALITY_CLOSURE_CURVES.csv", index=False)

    # Family summaries with whole-path bootstrap intervals.
    rng_boot = np.random.default_rng(stable_seed("bootstrap"))
    summary_rows: list[dict] = []
    final = path_df[(path_df["horizon"] == LENGTH) & (path_df["control"] == "chronological")]
    chrono_closure = closure_df[closure_df["control"] == "chronological"]
    for split in ("calibration", "holdout"):
        for family in FAMILIES:
            part = final[(final["split"] == split) & (final["family"] == family)]
            cpart = chrono_closure[(chrono_closure["split"] == split) & (chrono_closure["family"] == family)]
            xp = bootstrap_median_ci(part["x_p"].to_numpy(), rng_boot)
            xr = bootstrap_median_ci(part["x_r"].to_numpy(), rng_boot)
            rho = bootstrap_median_ci(cpart["mean_rho"].to_numpy(), rng_boot)
            expected = EXPECTED_SECTOR[family]
            observed = ((part["x_p"] >= 1).astype(int), (part["x_r"] >= 1).astype(int))
            sector_correct = float(np.mean((observed[0] == expected[0]) & (observed[1] == expected[1])))
            summary_rows.append(
                {
                    "split": split,
                    "family": family,
                    "n_paths": len(part),
                    "median_x_p": xp[0], "x_p_ci_low": xp[1], "x_p_ci_high": xp[2],
                    "median_x_r": xr[0], "x_r_ci_low": xr[1], "x_r_ci_high": xr[2],
                    "median_mean_rho": rho[0], "rho_ci_low": rho[1], "rho_ci_high": rho[2],
                    "sector_accuracy": sector_correct,
                }
            )
    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(HERE / "T348_IRRATIONALITY_FAMILY_SUMMARY.csv", index=False)

    # Gate calculations.
    hsum = summary_df[summary_df["split"] == "holdout"].set_index("family")
    gate_rows: list[dict] = []
    gate1_checks = {
        "periodic rational x_P < 0.75": hsum.loc["periodic rational", "median_x_p"] < 0.75,
        "finite stochastic x_P < 0.75": hsum.loc["finite stochastic", "median_x_p"] < 0.75,
        "irrational rotation x_P > 1.25": hsum.loc["irrational rotation", "median_x_p"] > 1.25,
        "deterministic chaos x_P > 1.25": hsum.loc["deterministic chaos", "median_x_p"] > 1.25,
        "continuous stochastic x_P > 1.25": hsum.loc["continuous stochastic", "median_x_p"] > 1.25,
    }
    gate1_checks = {key: bool(value) for key, value in gate1_checks.items()}
    gate_rows.append({"gate": "G1 potential orientation", "passed": bool(all(gate1_checks.values())), "detail": json.dumps(gate1_checks)})

    gate2_checks = {
        "periodic rational x_R < 0.75": hsum.loc["periodic rational", "median_x_r"] < 0.75,
        "irrational rotation x_R < 0.75": hsum.loc["irrational rotation", "median_x_r"] < 0.75,
        "deterministic chaos x_R < 1.25": hsum.loc["deterministic chaos", "median_x_r"] < 1.25,
        "finite stochastic x_R > 1.25": hsum.loc["finite stochastic", "median_x_r"] > 1.25,
        "continuous stochastic x_R > 1.25": hsum.loc["continuous stochastic", "median_x_r"] > 1.25,
    }
    gate2_checks = {key: bool(value) for key, value in gate2_checks.items()}
    gate_rows.append({"gate": "G2 residual orientation", "passed": bool(all(gate2_checks.values())), "detail": json.dumps(gate2_checks)})

    holdout_final = final[final["split"] == "holdout"].copy()
    correct = []
    for row in holdout_final.itertuples():
        expected = EXPECTED_SECTOR[row.family]
        correct.append(int((row.x_p >= 1) == expected[0] and (row.x_r >= 1) == expected[1]))
    sector_accuracy = float(np.mean(correct))
    sector_accuracy_by_family = {
        family: float(hsum.loc[family, "sector_accuracy"]) for family in FAMILIES
    }
    macro_sector_accuracy = float(np.mean(list(sector_accuracy_by_family.values())))
    gate_rows.append({"gate": "G3 broad-sector recovery", "passed": bool(sector_accuracy >= 0.85), "value": sector_accuracy, "threshold": 0.85})

    hold_c = chrono_closure[chrono_closure["split"] == "holdout"]
    closure_checks = {
        "periodic median rho > 0.90": hsum.loc["periodic rational", "median_mean_rho"] > 0.90,
        "irrational median rho > 0.90": hsum.loc["irrational rotation", "median_mean_rho"] > 0.90,
        "chaos median rho < 0.25": hsum.loc["deterministic chaos", "median_mean_rho"] < 0.25,
        "finite stochastic median rho < 0.25": hsum.loc["finite stochastic", "median_mean_rho"] < 0.25,
        "continuous stochastic median rho < 0.25": hsum.loc["continuous stochastic", "median_mean_rho"] < 0.25,
        "periodic exact closure share >= 0.95": float(hold_c[hold_c["family"] == "periodic rational"]["exact_closure_64"].mean()) >= 0.95,
    }
    irr = hold_c[hold_c["family"] == "irrational rotation"]
    irr_no_exact = float(1.0 - irr["exact_closure_64"].mean())
    valid_miss = irr[["best_miss_64", "best_miss_512"]].dropna()
    improve_share = float(np.mean(valid_miss["best_miss_512"] < valid_miss["best_miss_64"]))
    closure_checks["irrational no exact closure share >= 0.95"] = irr_no_exact >= 0.95
    closure_checks["irrational miss improvement share >= 0.80"] = improve_share >= 0.80
    closure_checks = {key: bool(value) for key, value in closure_checks.items()}
    gate_rows.append({"gate": "G4 closure independence", "passed": bool(all(closure_checks.values())), "value": improve_share, "detail": json.dumps(closure_checks)})

    hold_controls = path_df[(path_df["split"] == "holdout") & (path_df["horizon"] == LENGTH)]
    shuffle_closure = closure_df[(closure_df["split"] == "holdout") & (closure_df["control"] == "shuffled")]
    order_checks = {}
    for family in ("periodic rational", "irrational rotation", "deterministic chaos"):
        c = hold_controls[(hold_controls["family"] == family) & (hold_controls["control"] == "chronological")].set_index("path_id")
        s = hold_controls[(hold_controls["family"] == family) & (hold_controls["control"] == "shuffled")].set_index("path_id")
        ids = c.index.intersection(s.index)
        order_checks[f"{family} delta x_R >= 0.50"] = float(np.median(s.loc[ids, "x_r"] - c.loc[ids, "x_r"])) >= 0.50
        order_checks[f"{family} abs delta x_P < 0.10"] = abs(float(np.median(s.loc[ids, "x_p"] - c.loc[ids, "x_p"]))) < 0.10
    for family in ("periodic rational", "irrational rotation"):
        c = hold_c[hold_c["family"] == family].set_index("path_id")
        s = shuffle_closure[shuffle_closure["family"] == family].set_index("path_id")
        ids = c.index.intersection(s.index)
        order_checks[f"{family} rho drop >= 0.50"] = float(np.median(c.loc[ids, "mean_rho"] - s.loc[ids, "mean_rho"])) >= 0.50
    order_checks = {key: bool(value) for key, value in order_checks.items()}
    gate_rows.append({"gate": "G5 order-destruction control", "passed": bool(all(order_checks.values())), "detail": json.dumps(order_checks)})

    pd.DataFrame(gate_rows).to_csv(HERE / "T348_IRRATIONALITY_FROZEN_GATES.csv", index=False)
    all_pass = all(bool(row["passed"]) for row in gate_rows)
    result = {
        "test": "T348 known-referee Irrationality path calibration",
        "orientation": {"x_p": "0 finite/reused -> 2 open potential", "x_r": "0 determinate -> 2 stochastic residual"},
        "evidence_boundary": "synthetic known-referee instrument calibration only",
        "n_paths": len(paths),
        "n_calibration_paths": int(sum(p["split"] == "calibration" for p in paths)),
        "n_holdout_paths": int(sum(p["split"] == "holdout" for p in paths)),
        "sector_accuracy_holdout": sector_accuracy,
        "sector_accuracy_holdout_macro_family": macro_sector_accuracy,
        "sector_accuracy_holdout_by_family": sector_accuracy_by_family,
        "irrational_best_miss_improvement_share": improve_share,
        "gates": gate_rows,
        "benchmark_verdict": "SUPPORTED [synthetic known-referee instrument only]" if all_pass else "NOT SUPPORTED [one or more frozen instrument gates failed]",
        "geometry_verdict": (
            "SUPPORTED AS A FOUR-SECTOR SYNTHETIC CALIBRATION WITH LIMITATION: "
            "ordered paths separate finite/open and determinate/stochastic reference families, "
            "but one lower-dimensional deterministic-chaos parameter group falls on the finite "
            "side of the fixed x_P ridge; closure history remains independently informative."
        ),
        "protocol_sha256": sha256(protocol),
        "claim_sha256": sha256(claim),
    }
    with (HERE / "T348_IRRATIONALITY_PATH_RESULTS.json").open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    # Small reviewed examples table, not the complete raw synthetic archive.
    example_rows = []
    for family, z in example_paths.items():
        for t, value in enumerate(z[:256]):
            example_rows.append({"family": family, "t": t, "z": float(value)})
    write_csv(HERE / "T348_IRRATIONALITY_EXAMPLE_PATHS.csv", example_rows)

    make_figure(path_df, curve_df, gate_rows, HERE / "T348_IRRATIONALITY_PATH_FIGURE.png")
    make_circle_examples(example_paths, HERE / "T348_IRRATIONALITY_CIRCLE_EXAMPLES.png")

    print(json.dumps({"benchmark_verdict": result["benchmark_verdict"], "sector_accuracy": sector_accuracy, "gates": gate_rows}, indent=2))


if __name__ == "__main__":
    main()
