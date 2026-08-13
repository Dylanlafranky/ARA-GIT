#!/usr/bin/env python3
"""T349 synthetic state/history Di-ARA interface calibration."""

from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
SEED = 349_20260811
N_PER_PARAMETER = 24
LENGTH = 4096
RESOLUTIONS = np.array((16, 32, 64, 128, 256), dtype=int)
MAX_LAG = 512
K_NEIGHBOURS = 5
G_REF = 0.75
MERSENNE_61 = (1 << 61) - 1

PROTOCOL = HERE / "T349_STATE_HISTORY_DI_ARA_INTERFACE_PROTOCOL_v1_FROZEN.md"
CLAIM = HERE / "T349_STATE_HISTORY_DI_ARA_INTERFACE_CLAIM_PACKET_v1.md"

FAMILIES = (
    "periodic rational",
    "irrational rotation",
    "deterministic chaos",
    "finite stochastic",
    "continuous stochastic",
)
RADIAL_MODES = ("contraction", "neutral", "expansion")
EXPECTED_SECTOR = {
    "periodic rational": (0, 0),
    "irrational rotation": (1, 0),
    "deterministic chaos": (1, 0),
    "finite stochastic": (0, 1),
    "continuous stochastic": (1, 1),
}
FAMILY_COLORS = {
    "periodic rational": "#2F6FB0",
    "irrational rotation": "#D49A2E",
    "deterministic chaos": "#D86D32",
    "finite stochastic": "#738C3A",
    "continuous stochastic": "#C45A86",
}
RADIAL_COLORS = {"contraction": "#2F6FB0", "neutral": "#8A929C", "expansion": "#D49A2E"}
RADIAL_MARKERS = {"contraction": "v", "neutral": "o", "expansion": "^"}
FAMILY_MARKERS = {
    "periodic rational": "o",
    "irrational rotation": "s",
    "deterministic chaos": "^",
    "finite stochastic": "D",
    "continuous stochastic": "P",
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


def coprime_numerator(q: int, index: int) -> int:
    values = [p for p in range(1, q) if math.gcd(p, q) == 1]
    return values[index % len(values)]


def periodic_rotation(q: int, index: int) -> np.ndarray:
    p = coprime_numerator(q, index)
    phase = index % q
    return ((phase + p * np.arange(LENGTH, dtype=np.int64)) % q) / float(q)


def irrational_rotation(d: int, index: int) -> np.ndarray:
    advance = math.sqrt(d) - math.floor(math.sqrt(d))
    rng = np.random.default_rng(stable_seed("irr", d, index))
    return (rng.random() + advance * np.arange(LENGTH)) % 1.0


def chaotic_circle(m: int, offset_d: int, index: int) -> np.ndarray:
    frac = math.sqrt(offset_d) - math.floor(math.sqrt(offset_d))
    c_num = max(1, min(MERSENNE_61 - 1, int(frac * MERSENNE_61)))
    rng = np.random.default_rng(stable_seed("chaos", m, offset_d, index))
    x = int(rng.integers(1, 1 << 61, dtype=np.int64)) % MERSENNE_61
    out = np.empty(LENGTH)
    for t in range(LENGTH):
        out[t] = x / MERSENNE_61
        x = (m * x + c_num) % MERSENNE_61
    return out


def finite_stochastic(q: int, index: int) -> np.ndarray:
    rng = np.random.default_rng(stable_seed("finite", q, index))
    return rng.integers(0, q, size=LENGTH) / float(q)


def continuous_stochastic(a: float, b: float, index: int) -> np.ndarray:
    rng = np.random.default_rng(stable_seed("continuous", a, b, index))
    return rng.beta(a, b, size=LENGTH)


def generate_phase_paths() -> list[dict]:
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
    rows = []
    for split, family_specs in specs.items():
        for family, parameters in family_specs.items():
            for parameter_index, (_, parameter) in enumerate(parameters):
                for replicate in range(N_PER_PARAMETER):
                    if family == "periodic rational":
                        u = periodic_rotation(int(parameter), replicate)
                    elif family == "irrational rotation":
                        u = irrational_rotation(int(parameter), replicate)
                    elif family == "deterministic chaos":
                        m, d = parameter
                        u = chaotic_circle(int(m), int(d), replicate)
                    elif family == "finite stochastic":
                        u = finite_stochastic(int(parameter), replicate)
                    else:
                        a, b = parameter
                        u = continuous_stochastic(float(a), float(b), replicate)
                    rows.append({
                        "phase_id": f"{split}:{family}:{parameter_index}:{replicate}",
                        "split": split,
                        "family": family,
                        "parameter": repr(parameter),
                        "parameter_index": parameter_index,
                        "replicate": replicate,
                        "u": u,
                    })
    return rows


def radial_profile(mode: str, span: float) -> np.ndarray:
    sign = {"contraction": -1.0, "neutral": 0.0, "expansion": 1.0}[mode]
    coordinate = np.linspace(-0.5, 0.5, LENGTH)
    return np.exp(sign * span * coordinate)


def address_openness(u: np.ndarray) -> float:
    occupied = []
    for bins in RESOLUTIONS:
        idx = np.minimum((u * bins).astype(int), bins - 1)
        occupied.append(int(np.unique(idx).size))
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


def stochastic_residual(u: np.ndarray) -> float:
    split = len(u) // 2
    train_x, train_y = u[:split - 1], u[1:split]
    test_x, test_y = u[split:-1], u[split + 1:]
    local = float(np.mean(circular_loss(test_y, knn_predict(train_x, train_y, test_x))))
    null = float(np.mean(circular_loss(test_y, np.full_like(test_y, circular_mean(train_y)))))
    return 2.0 * min(1.0, local / max(null, 1e-12))


def closure_history(u: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    n = len(u)
    vector = np.exp(2j * np.pi * u)
    nfft = 1 << (2 * n - 1).bit_length()
    spectrum = np.fft.fft(vector, nfft)
    raw = np.fft.ifft(spectrum * np.conj(spectrum))[:MAX_LAG + 1]
    raw = raw / np.arange(n, n - MAX_LAG - 1, -1)
    relation = raw[1:]
    return np.abs(relation), np.abs(np.angle(relation)) / np.pi


def closure_summary(u: np.ndarray) -> dict:
    rho, distance = closure_history(u)
    def best(limit: int) -> float:
        mask = rho[:limit] > 0.90
        if not np.any(mask):
            return float("nan")
        values = distance[:limit][mask]
        values = values[values > 1e-12]
        return 0.0 if not len(values) else float(np.min(values))
    exact = bool(np.any((rho[:64] > 1 - 1e-10) & (distance[:64] < 1e-12)))
    return {
        "mean_rho": float(np.median(rho)),
        "best_miss_64": best(64),
        "best_miss_512": best(512),
        "exact_closure_64": exact,
        "rho": rho,
    }


def state_coordinates(radius: np.ndarray, u: np.ndarray) -> tuple[float, float, float]:
    gain = float(np.log(radius[-1] / radius[0]))
    x_l = 1.0 + math.tanh(gain / G_REF)
    delta = np.angle(np.exp(2j * np.pi * (u[1:] - u[:-1])))
    denominator = float(np.sum(np.abs(np.sin(delta))))
    orientation = 0.0 if denominator < 1e-15 else float(np.sum(np.sin(delta)) / denominator)
    return x_l, 1.0 + orientation, gain


def phase_coordinates(u: np.ndarray) -> tuple[float, float]:
    return address_openness(u), stochastic_residual(u)


def shuffled_phase(u: np.ndarray, phase_id: str, endpoints: bool) -> np.ndarray:
    rng = np.random.default_rng(stable_seed("endpoint" if endpoints else "shuffle", phase_id))
    if endpoints:
        out = u.copy()
        out[1:-1] = out[1:-1][rng.permutation(len(out) - 2)]
        return out
    return u[rng.permutation(len(u))]


def measure(radius: np.ndarray, u: np.ndarray) -> dict:
    x_l, x_c, gain = state_coordinates(radius, u)
    x_p, x_r = phase_coordinates(u)
    closure = closure_summary(u)
    return {
        "x_l": x_l, "x_c": x_c, "radial_log_gain": gain,
        "x_p": x_p, "x_r": x_r,
        "mean_rho": closure["mean_rho"],
        "best_miss_64": closure["best_miss_64"],
        "best_miss_512": closure["best_miss_512"],
        "exact_closure_64": closure["exact_closure_64"],
    }


def paired(df: pd.DataFrame, control: str) -> pd.DataFrame:
    keys = ["trajectory_id", "split", "family", "radial_mode", "radial_span"]
    base = df[df.control == "chronological"].set_index(keys)
    other = df[df.control == control].set_index(keys)
    return base.join(other, lsuffix="_base", rsuffix="_control", how="inner").reset_index()


def make_figure(metrics: pd.DataFrame, summary: pd.DataFrame, interventions: pd.DataFrame,
                constants: pd.DataFrame, curves: pd.DataFrame, output: Path) -> None:
    width, height = 2400, 1500
    image = Image.new("RGB", (width, height), "#F8FAFC")
    draw = ImageDraw.Draw(image, "RGBA")

    def get_font(size: int, bold: bool = False):
        names = ["arialbd.ttf" if bold else "arial.ttf", "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"]
        for name in names:
            try:
                return ImageFont.truetype(name, size)
            except OSError:
                pass
        return ImageFont.load_default()

    title_font, panel_font, label_font, small_font = get_font(42, True), get_font(24, True), get_font(18), get_font(15)
    draw.text((70, 32), "T349 — state/history Di-ARA interface calibration", font=title_font, fill="#172033")
    draw.text((72, 88), "Untouched holdout · 15 core identities · independent radial and chronological interventions", font=label_font, fill="#596579")
    boxes = [
        (70, 145, 800, 745), (835, 145, 1565, 745), (1600, 145, 2330, 745),
        (70, 790, 800, 1410), (835, 790, 1565, 1410), (1600, 790, 2330, 1410),
    ]
    for box in boxes:
        draw.rounded_rectangle(box, radius=18, fill="#FFFFFF", outline="#D6DCE5", width=2)

    def plot_frame(box, title, xlabel, ylabel, xlim=(0, 2), ylim=(0, 2)):
        x0, y0, x1, y1 = box
        draw.text((x0 + 28, y0 + 20), title, font=panel_font, fill="#172033")
        area = (x0 + 90, y0 + 80, x1 - 30, y1 - 78)
        ax0, ay0, ax1, ay1 = area
        for frac in (0, 0.5, 1):
            xx = ax0 + frac * (ax1 - ax0); yy = ay1 - frac * (ay1 - ay0)
            draw.line((xx, ay0, xx, ay1), fill="#E4E8EE", width=1)
            draw.line((ax0, yy, ax1, yy), fill="#E4E8EE", width=1)
            draw.text((xx - 10, ay1 + 8), f"{xlim[0] + frac*(xlim[1]-xlim[0]):.1f}", font=small_font, fill="#667085")
            draw.text((ax0 - 38, yy - 9), f"{ylim[0] + frac*(ylim[1]-ylim[0]):.1f}", font=small_font, fill="#667085")
        draw.line((ax0, ay1, ax1, ay1), fill="#303846", width=2)
        draw.line((ax0, ay0, ax0, ay1), fill="#303846", width=2)
        draw.text(((ax0 + ax1)//2 - 130, y1 - 44), xlabel, font=small_font, fill="#465267")
        draw.text((ax0 + 4, y0 + 55), ylabel, font=small_font, fill="#465267")
        return area

    def xy(area, x, y, xlim=(0, 2), ylim=(0, 2)):
        ax0, ay0, ax1, ay1 = area
        px = ax0 + (x - xlim[0]) / (xlim[1] - xlim[0]) * (ax1 - ax0)
        py = ay1 - (y - ylim[0]) / (ylim[1] - ylim[0]) * (ay1 - ay0)
        return px, py

    def marker(px, py, color, kind="o", radius=6):
        if kind in ("^", "v"):
            sign = -1 if kind == "^" else 1
            pts = [(px, py + sign * -radius), (px - radius, py + sign * radius), (px + radius, py + sign * radius)]
            draw.polygon(pts, fill=color, outline="#20242C")
        elif kind == "s":
            draw.rectangle((px-radius, py-radius, px+radius, py+radius), fill=color, outline="#20242C")
        elif kind == "D":
            draw.polygon([(px,py-radius),(px+radius,py),(px,py+radius),(px-radius,py)], fill=color, outline="#20242C")
        else:
            draw.ellipse((px-radius,py-radius,px+radius,py+radius), fill=color, outline="#20242C")

    hold = metrics[(metrics.split == "holdout") & (metrics.control == "chronological")]
    area = plot_frame(boxes[0], "Older state cut", "xL: contraction ← ridge → expansion", "xC: reverse ↔ forward")
    rx, ry = xy(area, 1, 1); draw.line((rx, area[1], rx, area[3]), fill="#273142", width=2); draw.line((area[0], ry, area[2], ry), fill="#273142", width=2)
    sampled = hold.iloc[::max(1, len(hold)//900)]
    for row in sampled.itertuples():
        px, py = xy(area, row.x_l, row.x_c)
        draw.ellipse((px-2, py-2, px+2, py+2), fill=RADIAL_COLORS[row.radial_mode] + "66")
    med = hold.groupby(["radial_mode", "family"], as_index=False)[["x_l", "x_c"]].median()
    for row in med.itertuples():
        px, py = xy(area, row.x_l, row.x_c); marker(px, py, RADIAL_COLORS[row.radial_mode], FAMILY_MARKERS[row.family], 8)

    area = plot_frame(boxes[1], "Newer path/history cut", "xP: reused ← ridge → open", "xR: determinate ↔ stochastic")
    rx, ry = xy(area, 1, 1); draw.line((rx, area[1], rx, area[3]), fill="#273142", width=2); draw.line((area[0], ry, area[2], ry), fill="#273142", width=2)
    for row in sampled.itertuples():
        px, py = xy(area, row.x_p, row.x_r)
        draw.ellipse((px-2, py-2, px+2, py+2), fill=FAMILY_COLORS[row.family] + "66")
    med = hold.groupby(["family", "radial_mode"], as_index=False)[["x_p", "x_r"]].median()
    for row in med.itertuples():
        px, py = xy(area, row.x_p, row.x_r); marker(px, py, FAMILY_COLORS[row.family], RADIAL_MARKERS[row.radial_mode], 8)

    box = boxes[2]; x0,y0,x1,y1=box
    draw.text((x0+28,y0+20), "Intervention selectivity", font=panel_font, fill="#172033")
    display = interventions[interventions.metric.isin(["abs_delta_x_l","abs_delta_x_c","abs_delta_x_p","abs_delta_x_r"])]
    pivot = display.pivot(index="intervention", columns="metric", values="median").reindex(["radial_inverted","phase_reflected","shuffled","endpoint_shuffled"])
    chart=(x0+70,y0+95,x1-30,y1-100); cx0,cy0,cx1,cy1=chart
    metric_colors={"abs_delta_x_l":"#2F6FB0","abs_delta_x_c":"#D49A2E","abs_delta_x_p":"#738C3A","abs_delta_x_r":"#C45A86"}
    maxv=max(0.01,float(np.nanmax(pivot.to_numpy()))*1.08)
    groupw=(cx1-cx0)/4
    for gi,(name,row) in enumerate(pivot.iterrows()):
        for mi,metric in enumerate(metric_colors):
            value=float(row[metric]); bw=groupw/5; bx0=cx0+gi*groupw+(mi+0.5)*bw; by=cy1-(value/maxv)*(cy1-cy0)
            draw.rectangle((bx0,by,bx0+bw-3,cy1), fill=metric_colors[metric], outline="#394150")
        draw.text((cx0+gi*groupw+4,cy1+10), name.replace("_","\n"), font=small_font, fill="#4D596C")
    for i,(metric,color) in enumerate(metric_colors.items()):
        lx=x0+35+(i%2)*310; ly=y1-65+(i//2)*24
        draw.rectangle((lx,ly,lx+18,ly+12), fill=color); draw.text((lx+25,ly-4), metric.replace("abs_delta_","Δ "), font=small_font, fill="#4D596C")
    draw.line((cx0,cy1,cx1,cy1), fill="#303846", width=2)

    box=boxes[3]; x0,y0,x1,y1=box
    draw.text((x0+28,y0+20), "Path-sector recovery across radial states", font=panel_font, fill="#172033")
    matrix=summary.pivot(index="family",columns="radial_mode",values="path_sector_accuracy").reindex(index=FAMILIES,columns=RADIAL_MODES)
    left=x0+210; top=y0+95; cellw=(x1-left-35)/3; cellh=(y1-top-45)/5
    for j,radial in enumerate(RADIAL_MODES): draw.text((left+j*cellw+15,top-32),radial,font=small_font,fill="#4D596C")
    for i,family in enumerate(FAMILIES):
        draw.text((x0+30,top+i*cellh+cellh/2-8),family,font=small_font,fill="#4D596C")
        for j in range(3):
            value=float(matrix.iloc[i,j]); shade=int(245-120*value)
            fill=(shade,shade+8,min(255,shade+25),255)
            rect=(left+j*cellw,top+i*cellh,left+(j+1)*cellw-5,top+(i+1)*cellh-5)
            draw.rounded_rectangle(rect,radius=7,fill=fill,outline="#D1D7E0")
            draw.text((rect[0]+cellw/2-25,rect[1]+cellh/2-10),f"{100*value:.1f}%",font=label_font,fill="#172033")

    area=plot_frame(boxes[4],"Uncompressed closure history","lag H","median coherence ρ(H)",xlim=(1,512),ylim=(0,1))
    for family in FAMILIES:
        part=curves[(curves.split=="holdout")&(curves.family==family)&(curves.control=="chronological")]
        pts=[xy(area,float(r.lag),float(r.median_rho),xlim=(1,512),ylim=(0,1)) for r in part.itertuples()]
        if len(pts)>1: draw.line(pts,fill=FAMILY_COLORS[family],width=3)
    for i,family in enumerate(FAMILIES):
        ly=boxes[4][1]+78+i*22; draw.line((boxes[4][2]-245,ly,boxes[4][2]-220,ly),fill=FAMILY_COLORS[family],width=4); draw.text((boxes[4][2]-212,ly-9),family,font=small_font,fill="#4D596C")

    box=boxes[5]; x0,y0,x1,y1=box
    draw.text((x0+28,y0+20),"Fixed reciprocal-amplitude specificity",font=panel_font,fill="#172033")
    bars=constants.sort_values("mean_abs_log_error"); maxerr=max(0.4,float(bars.mean_abs_log_error.max())*1.08)
    bx0=x0+170; bx1=x1-35; top=y0+90; bh=(y1-top-60)/len(bars)
    gate_x=bx0+0.10/maxerr*(bx1-bx0); draw.line((gate_x,top-10,gate_x,y1-45),fill="#303846",width=2)
    draw.text((gate_x+5,top-28),"universal gate 0.10",font=small_font,fill="#303846")
    for i,row in enumerate(bars.itertuples()):
        yy=top+i*bh; color="#2F6FB0" if row.candidate=="calibration_fitted" else ("#D49A2E" if row.candidate=="e" else "#A8AFB8")
        draw.text((x0+35,yy+7),row.candidate,font=small_font,fill="#4D596C")
        length=row.mean_abs_log_error/maxerr*(bx1-bx0)
        draw.rounded_rectangle((bx0,yy+5,bx0+length,yy+bh-8),radius=5,fill=color,outline="#566170")
        draw.text((bx0+length+8,yy+7),f"{row.mean_abs_log_error:.3f}",font=small_font,fill="#303846")

    footer_y = 1450
    draw.text((72, footer_y-8), "Phase-history family:", font=small_font, fill="#465267")
    cursor = 245
    for family in FAMILIES:
        marker(cursor, footer_y, FAMILY_COLORS[family], FAMILY_MARKERS[family], 6)
        draw.text((cursor+12, footer_y-9), family, font=small_font, fill="#465267")
        cursor += 230 if family != "continuous stochastic" else 0
    draw.text((1550, footer_y-8), "Radial state:", font=small_font, fill="#465267")
    cursor = 1665
    for radial in RADIAL_MODES:
        marker(cursor, footer_y, RADIAL_COLORS[radial], RADIAL_MARKERS[radial], 6)
        draw.text((cursor+12, footer_y-9), radial, font=small_font, fill="#465267")
        cursor += 165
    image.save(output)


def main() -> None:
    print("T349 frozen provenance")
    print(f"  protocol_sha256={sha256(PROTOCOL)}")
    print(f"  claim_sha256={sha256(CLAIM)}")
    paths = generate_phase_paths()
    print(f"  base_phase_paths={len(paths)}")
    spans = {"calibration": (0.35, 0.75, 1.15), "holdout": (0.55, 0.95, 1.35)}
    metrics_rows, curve_buckets, example_rows = [], defaultdict(list), []

    for number, item in enumerate(paths, start=1):
        u = item["u"]
        controls = {
            "chronological": u,
            "phase_reflected": (-u) % 1.0,
            "shuffled": shuffled_phase(u, item["phase_id"], False),
            "endpoint_shuffled": shuffled_phase(u, item["phase_id"], True),
        }
        phase_measurements = {name: measure(np.ones(LENGTH), values) for name, values in controls.items()}
        for control, values in controls.items():
            rho, _ = closure_history(values)
            curve_buckets[(item["split"], item["family"], control)].append(rho)

        span = spans[item["split"]][item["replicate"] % 3]
        for radial_mode in RADIAL_MODES:
            radius = radial_profile(radial_mode, span)
            trajectory_id = f"{item['phase_id']}:{radial_mode}"
            base = {
                "trajectory_id": trajectory_id, "phase_id": item["phase_id"], "split": item["split"],
                "family": item["family"], "parameter": item["parameter"],
                "parameter_index": item["parameter_index"], "replicate": item["replicate"],
                "radial_mode": radial_mode, "radial_span": span,
            }
            for control, control_u in controls.items():
                measured = phase_measurements[control].copy()
                x_l, x_c, gain = state_coordinates(radius, control_u)
                measured.update({"x_l": x_l, "x_c": x_c, "radial_log_gain": gain})
                endpoint_error = 0.0
                if control == "endpoint_shuffled":
                    original = radius * np.exp(2j * np.pi * u)
                    changed = radius * np.exp(2j * np.pi * control_u)
                    endpoint_error = float(max(abs(original[0] - changed[0]), abs(original[-1] - changed[-1])))
                metrics_rows.append({**base, "control": control, "endpoint_error": endpoint_error, **measured})
            inverted = 1.0 / radius
            measured = measure(inverted, u)
            metrics_rows.append({**base, "control": "radial_inverted", "endpoint_error": 0.0, **measured})

            if item["split"] == "holdout" and item["replicate"] == 0 and item["parameter_index"] == 0:
                for t in range(LENGTH):
                    example_rows.append({**base, "t": t, "u": float(u[t]), "radius": float(radius[t])})
        if number % 100 == 0:
            print(f"  measured {number}/{len(paths)} base paths")

    metrics = pd.DataFrame(metrics_rows)
    metrics.to_csv(HERE / "T349_STATE_HISTORY_DI_ARA_METRICS.csv", index=False)
    pd.DataFrame(example_rows).to_csv(HERE / "T349_STATE_HISTORY_DI_ARA_EXAMPLES.csv", index=False)

    curve_rows = []
    for (split, family, control), arrays in curve_buckets.items():
        matrix = np.vstack(arrays)
        median = np.median(matrix, axis=0)
        for lag, value in enumerate(median, start=1):
            curve_rows.append({"split": split, "family": family, "control": control, "lag": lag, "median_rho": float(value), "n_phase_paths": len(matrix)})
    curves = pd.DataFrame(curve_rows)
    curves.to_csv(HERE / "T349_STATE_HISTORY_DI_ARA_CLOSURE_CURVES.csv", index=False)

    hold = metrics[(metrics.split == "holdout") & (metrics.control == "chronological")].copy()
    hold["radial_correct"] = np.select(
        [hold.x_l < 0.75, hold.x_l > 1.25],
        [hold.radial_mode == "contraction", hold.radial_mode == "expansion"],
        default=hold.radial_mode == "neutral",
    ).astype(bool)
    hold["path_correct"] = [
        ((row.x_p >= 1) == EXPECTED_SECTOR[row.family][0]) and ((row.x_r >= 1) == EXPECTED_SECTOR[row.family][1])
        for row in hold.itertuples()
    ]
    summary = hold.groupby(["family", "radial_mode"], as_index=False).agg(
        n=("trajectory_id", "size"), median_x_l=("x_l", "median"), median_x_c=("x_c", "median"),
        median_x_p=("x_p", "median"), median_x_r=("x_r", "median"), median_rho=("mean_rho", "median"),
        radial_accuracy=("radial_correct", "mean"), path_sector_accuracy=("path_correct", "mean"),
    )
    summary.to_csv(HERE / "T349_STATE_HISTORY_DI_ARA_FACTORIAL_SUMMARY.csv", index=False)

    intervention_rows = []
    for control in ("radial_inverted", "phase_reflected", "shuffled", "endpoint_shuffled"):
        joined = paired(metrics[metrics.split == "holdout"], control)
        for coordinate in ("x_l", "x_c", "x_p", "x_r", "mean_rho"):
            delta = joined[f"{coordinate}_control"] - joined[f"{coordinate}_base"]
            intervention_rows.append({"intervention": control, "metric": f"abs_delta_{coordinate}", "median": float(np.median(np.abs(delta))), "signed_median": float(np.median(delta)), "n": len(delta)})
    interventions = pd.DataFrame(intervention_rows)
    interventions.to_csv(HERE / "T349_STATE_HISTORY_DI_ARA_INTERVENTIONS.csv", index=False)

    nonneutral = hold[hold.radial_mode != "neutral"].copy()
    observed_log_alpha = np.abs(nonneutral.radial_log_gain.to_numpy())
    fixed = {
        "plastic": 1.324717957244746,
        "sqrt2": math.sqrt(2),
        "phi": (1 + math.sqrt(5)) / 2,
        "octave": 2.0,
        "e": math.e,
    }
    constant_rows = []
    for name, alpha in fixed.items():
        error = np.abs(observed_log_alpha - math.log(alpha))
        constant_rows.append({"candidate": name, "alpha": alpha, "candidate_type": "fixed", "mean_abs_log_error": float(np.mean(error)), "within_0_10_share": float(np.mean(error < 0.10)), "universal_gate": bool(np.mean(error) < 0.10 and np.mean(error < 0.10) >= 0.80)})
    calibration = metrics[(metrics.split == "calibration") & (metrics.control == "chronological") & (metrics.radial_mode != "neutral")]
    fitted_log = float(np.median(np.abs(calibration.radial_log_gain)))
    fitted_error = np.abs(observed_log_alpha - fitted_log)
    constant_rows.append({"candidate": "calibration_fitted", "alpha": float(np.exp(fitted_log)), "candidate_type": "calibration control", "mean_abs_log_error": float(np.mean(fitted_error)), "within_0_10_share": float(np.mean(fitted_error < 0.10)), "universal_gate": False})
    constants = pd.DataFrame(constant_rows)
    constants.to_csv(HERE / "T349_STATE_HISTORY_DI_ARA_CONSTANT_SPECIFICITY.csv", index=False)

    gate_rows = []
    radial_medians = hold.groupby("radial_mode").x_l.median()
    radial_family_acc = hold.groupby("family").radial_correct.mean()
    g1 = bool(radial_medians.contraction < 0.75 and 0.75 <= radial_medians.neutral <= 1.25 and radial_medians.expansion > 1.25 and hold.radial_correct.mean() >= 0.95 and radial_family_acc.min() >= 0.90)
    gate_rows.append({"gate": "G1 radial recovery", "passed": g1, "value": float(hold.radial_correct.mean()), "detail": json.dumps({"medians": radial_medians.to_dict(), "min_family_accuracy": float(radial_family_acc.min())})})

    radial_path_acc = hold.groupby("radial_mode").path_correct.mean()
    h_family = hold.groupby("family").mean_rho.median()
    irrational = hold[hold.family == "irrational rotation"]
    miss = irrational[["best_miss_64", "best_miss_512"]].dropna()
    improve = float(np.mean(miss.best_miss_512 < miss.best_miss_64))
    closure_ok = h_family["periodic rational"] > 0.90 and h_family["irrational rotation"] > 0.90 and all(h_family[f] < 0.25 for f in ("deterministic chaos", "finite stochastic", "continuous stochastic")) and improve >= 0.80
    g2 = bool(hold.path_correct.mean() >= 0.85 and radial_path_acc.min() >= 0.80 and closure_ok)
    gate_rows.append({"gate": "G2 history recovery across radius", "passed": g2, "value": float(hold.path_correct.mean()), "detail": json.dumps({"min_radial_accuracy": float(radial_path_acc.min()), "irrational_improve": improve, "family_rho": h_family.to_dict()})})

    inv = paired(metrics[metrics.split == "holdout"], "radial_inverted")
    reflection_error = np.median(np.abs(inv.x_l_control - (2 - inv.x_l_base)))
    inv_other = {c: float(np.median(np.abs(inv[f"{c}_control"] - inv[f"{c}_base"]))) for c in ("x_c", "x_p", "x_r", "mean_rho")}
    g3 = bool(reflection_error < 0.01 and max(inv_other.values()) < 0.02)
    gate_rows.append({"gate": "G3 radial inversion", "passed": g3, "value": float(reflection_error), "detail": json.dumps(inv_other)})

    ref = paired(metrics[metrics.split == "holdout"], "phase_reflected")
    orientation_error = np.median(np.abs(ref.x_c_control - (2 - ref.x_c_base)))
    ref_other = {c: float(np.median(np.abs(ref[f"{c}_control"] - ref[f"{c}_base"]))) for c in ("x_l", "x_p", "x_r", "mean_rho")}
    g4 = bool(orientation_error < 0.01 and max(ref_other.values()) < 0.02)
    gate_rows.append({"gate": "G4 phase reflection", "passed": g4, "value": float(orientation_error), "detail": json.dumps(ref_other)})

    shuffle = paired(metrics[metrics.split == "holdout"], "shuffled")
    g5_checks = {}
    for family in ("periodic rational", "irrational rotation", "deterministic chaos"):
        part = shuffle[shuffle.family == family]
        g5_checks[f"{family} delta_x_r"] = float(np.median(part.x_r_control - part.x_r_base))
        g5_checks[f"{family} abs_delta_x_l"] = float(np.median(np.abs(part.x_l_control - part.x_l_base)))
        g5_checks[f"{family} abs_delta_x_p"] = float(np.median(np.abs(part.x_p_control - part.x_p_base)))
    for family in ("periodic rational", "irrational rotation"):
        part = shuffle[shuffle.family == family]
        g5_checks[f"{family} rho_drop"] = float(np.median(part.mean_rho_base - part.mean_rho_control))
    g5 = all(value >= 0.50 for key, value in g5_checks.items() if "delta_x_r" in key or "rho_drop" in key) and all(value < 0.10 for key, value in g5_checks.items() if "abs_delta" in key)
    gate_rows.append({"gate": "G5 chronology specificity", "passed": bool(g5), "detail": json.dumps(g5_checks)})

    endpoint = paired(metrics[metrics.split == "holdout"], "endpoint_shuffled")
    g6_checks = {"max_endpoint_error": float(endpoint.endpoint_error_control.max())}
    for family in ("periodic rational", "irrational rotation", "deterministic chaos"):
        part = endpoint[endpoint.family == family]
        g6_checks[f"{family} delta_x_r"] = float(np.median(part.x_r_control - part.x_r_base))
        g6_checks[f"{family} abs_delta_x_l"] = float(np.median(np.abs(part.x_l_control - part.x_l_base)))
        g6_checks[f"{family} abs_delta_x_p"] = float(np.median(np.abs(part.x_p_control - part.x_p_base)))
    for family in ("periodic rational", "irrational rotation"):
        part = endpoint[endpoint.family == family]
        g6_checks[f"{family} rho_drop"] = float(np.median(part.mean_rho_base - part.mean_rho_control))
    g6 = g6_checks["max_endpoint_error"] < 1e-12 and all(value >= 0.50 for key, value in g6_checks.items() if "delta_x_r" in key or "rho_drop" in key) and all(value < 0.10 for key, value in g6_checks.items() if "abs_delta" in key)
    gate_rows.append({"gate": "G6 endpoint/history distinction", "passed": bool(g6), "detail": json.dumps(g6_checks)})

    xl_ranges = hold.groupby(["radial_mode", "family"]).x_l.median().groupby("radial_mode").agg(lambda s: float(s.max() - s.min()))
    xp_ranges = hold.groupby(["family", "radial_mode"]).x_p.median().groupby("family").agg(lambda s: float(s.max() - s.min()))
    xr_ranges = hold.groupby(["family", "radial_mode"]).x_r.median().groupby("family").agg(lambda s: float(s.max() - s.min()))
    g7 = bool(xl_ranges.max() < 0.02 and xp_ranges.max() < 0.02 and xr_ranges.max() < 0.02)
    gate_rows.append({"gate": "G7 factorial independence", "passed": g7, "detail": json.dumps({"max_x_l_range": float(xl_ranges.max()), "max_x_p_range": float(xp_ranges.max()), "max_x_r_range": float(xr_ranges.max())})})

    g8 = bool(constants[constants.candidate_type == "fixed"].universal_gate.any())
    gate_rows.append({"gate": "G8 fixed constant specificity (separate)", "passed": g8, "value": float(constants.mean_abs_log_error.min()), "detail": json.dumps(constants.set_index("candidate").mean_abs_log_error.to_dict())})
    gates = pd.DataFrame(gate_rows)
    gates.to_csv(HERE / "T349_STATE_HISTORY_DI_ARA_FROZEN_GATES.csv", index=False)

    primary_pass = bool(gates[gates.gate != "G8 fixed constant specificity (separate)"].passed.all())
    result = {
        "test": "T349 state/history Di-ARA interface calibration",
        "evidence_boundary": "synthetic known-referee instrument/interface calibration only",
        "n_base_phase_paths": len(paths),
        "n_core_trajectories": int(len(metrics[metrics.control == "chronological"])),
        "n_holdout_core_trajectories": int(len(hold)),
        "radial_accuracy_holdout": float(hold.radial_correct.mean()),
        "history_sector_accuracy_holdout": float(hold.path_correct.mean()),
        "primary_gates_passed": int(gates[gates.gate != "G8 fixed constant specificity (separate)"].passed.sum()),
        "primary_gates_total": 7,
        "interface_verdict": "SUPPORTED [synthetic state/history interface calibration only]" if primary_pass else "NOT SUPPORTED [one or more frozen interface gates failed]",
        "constant_verdict": "SUPPORTED [one frozen universal fixed amplitude passed]" if g8 else "NOT SUPPORTED [no frozen universal fixed amplitude passed]",
        "gates": gate_rows,
        "protocol_sha256": sha256(PROTOCOL),
        "claim_sha256": sha256(CLAIM),
    }
    with (HERE / "T349_STATE_HISTORY_DI_ARA_RESULTS.json").open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)

    make_figure(metrics, summary, interventions, constants, curves, HERE / "T349_STATE_HISTORY_DI_ARA_FIGURE.png")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
