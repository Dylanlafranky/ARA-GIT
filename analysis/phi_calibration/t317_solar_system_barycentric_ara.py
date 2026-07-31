#!/usr/bin/env python3
"""T317 Solar-System barycentric ARA crosswalk.

Downloads checksum-retained public JPL Horizons vectors for the Sun and the
planetary-system barycentres, constructs the frozen Sun/planets ARA pair, and
separates forced conservation structure from descriptive composition/cadence.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data" / "t317"
RESULTS_PATH = HERE / "T317_SOLAR_SYSTEM_BARYCENTRIC_ARA_RESULTS.json"
SERIES_PATH = HERE / "T317_SOLAR_SYSTEM_BARYCENTRIC_ARA_SERIES.csv"
COMPOSITION_PATH = HERE / "T317_SOLAR_SYSTEM_BARYCENTRIC_ARA_COMPOSITION.csv"
FIGURE_PATH = HERE / "T317_SOLAR_SYSTEM_BARYCENTRIC_ARA.png"
REPORT_PATH = HERE / "T317_SOLAR_SYSTEM_BARYCENTRIC_ARA_REPORT_2026-07-31.md"

START = "1900-01-01"
STOP = "2101-01-01"
STEP = "5d"

GM = {
    "sun": 132_712_440_041.279419,
    "mercury": 22_031.868551,
    "venus": 324_858.592000,
    "emb": 398_600.435507 + 4_902.800118,
    "mars": 42_828.375816,
    "jupiter": 126_712_764.100000,
    "saturn": 37_940_584.841800,
    "uranus": 5_794_556.400000,
    "neptune": 6_836_527.100580,
    "pluto": 975.500000,
}

GALACTIC_TO_ICRS = np.array(
    [
        [-0.0548755604, 0.4941094279, -0.8676661490],
        [-0.8734370902, -0.4448296300, -0.1980763734],
        [-0.4838350155, 0.7469822445, 0.4559837762],
    ],
    dtype=float,
)
OBLIQUITY_DEG = 23.439291111


@dataclass(frozen=True)
class Body:
    key: str
    label: str
    command: str
    gm: float
    primary: bool


BODIES = [
    Body("sun", "Sun", "10", GM["sun"], False),
    Body("mercury", "Mercury", "1", GM["mercury"], True),
    Body("venus", "Venus", "2", GM["venus"], True),
    Body("emb", "Earth–Moon barycentre", "3", GM["emb"], True),
    Body("mars", "Mars system", "4", GM["mars"], True),
    Body("jupiter", "Jupiter system", "5", GM["jupiter"], True),
    Body("saturn", "Saturn system", "6", GM["saturn"], True),
    Body("uranus", "Uranus system", "7", GM["uranus"], True),
    Body("neptune", "Neptune system", "8", GM["neptune"], True),
    Body("pluto", "Pluto system", "9", GM["pluto"], False),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def horizons_url(body: Body) -> str:
    params = {
        "format": "text",
        "COMMAND": f"'{body.command}'",
        "OBJ_DATA": "'NO'",
        "MAKE_EPHEM": "'YES'",
        "EPHEM_TYPE": "'VECTORS'",
        "CENTER": "'500@0'",
        "START_TIME": f"'{START}'",
        "STOP_TIME": f"'{STOP}'",
        "STEP_SIZE": f"'{STEP}'",
        "TIME_TYPE": "'TDB'",
        "REF_PLANE": "'ECLIPTIC'",
        "REF_SYSTEM": "'ICRF'",
        "OUT_UNITS": "'KM-S'",
        "VEC_TABLE": "'2'",
        "VEC_CORR": "'NONE'",
        "CSV_FORMAT": "'YES'",
        "VEC_LABELS": "'YES'",
    }
    return "https://ssd.jpl.nasa.gov/api/horizons.api?" + urllib.parse.urlencode(
        params, safe="'@"
    )


def fetch_body(body: Body, force: bool = False) -> tuple[Path, Path]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = DATA_DIR / f"{body.key}_horizons_raw.txt"
    csv_path = DATA_DIR / f"{body.key}_vectors.csv"
    if raw_path.exists() and csv_path.exists() and not force:
        return raw_path, csv_path

    request = urllib.request.Request(
        horizons_url(body),
        headers={"User-Agent": "ARA-T317-public-barycentric-crosswalk/1.0"},
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        raw = response.read().decode("utf-8")
    if "$$SOE" not in raw or "$$EOE" not in raw:
        raise RuntimeError(f"Horizons response for {body.key} has no ephemeris block")
    raw_path.write_text(raw, encoding="utf-8")

    block = raw.split("$$SOE", 1)[1].split("$$EOE", 1)[0]
    parsed: list[dict[str, float | str]] = []
    for row in csv.reader(io.StringIO(block.strip())):
        if not row or len(row) < 8:
            continue
        parsed.append(
            {
                "jd_tdb": float(row[0]),
                "calendar_tdb": row[1].strip(),
                "x_km": float(row[2]),
                "y_km": float(row[3]),
                "z_km": float(row[4]),
                "vx_km_s": float(row[5]),
                "vy_km_s": float(row[6]),
                "vz_km_s": float(row[7]),
            }
        )
    if len(parsed) < 14_000:
        raise RuntimeError(f"Unexpectedly short Horizons table: {body.key} {len(parsed)}")
    pd.DataFrame(parsed).to_csv(csv_path, index=False)
    return raw_path, csv_path


def load_frames() -> dict[str, pd.DataFrame]:
    frames: dict[str, pd.DataFrame] = {}
    reference_jd: np.ndarray | None = None
    for body in BODIES:
        path = DATA_DIR / f"{body.key}_vectors.csv"
        if not path.exists():
            raise FileNotFoundError(f"Missing {path}; rerun with --fetch")
        frame = pd.read_csv(path)
        jd = frame["jd_tdb"].to_numpy(dtype=float)
        if reference_jd is None:
            reference_jd = jd
        elif len(jd) != len(reference_jd) or not np.allclose(jd, reference_jd):
            raise RuntimeError(f"Time grid mismatch for {body.key}")
        frames[body.key] = frame
    return frames


def vectors(frame: pd.DataFrame, kind: str) -> np.ndarray:
    prefix = "" if kind == "position" else "v"
    suffix = "_km" if kind == "position" else "_km_s"
    return frame[
        [f"{prefix}x{suffix}", f"{prefix}y{suffix}", f"{prefix}z{suffix}"]
    ].to_numpy(dtype=float)


def norm(v: np.ndarray) -> np.ndarray:
    return np.linalg.norm(v, axis=1)


def safe_angle_deg(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    denominator = norm(a) * norm(b)
    cosine = np.divide(
        np.sum(a * b, axis=1),
        denominator,
        out=np.full(len(a), np.nan),
        where=denominator > 0,
    )
    return np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))


def pair_metrics(a: np.ndarray, b: np.ndarray) -> dict[str, np.ndarray]:
    na = norm(a)
    nb = norm(b)
    total = na + nb
    x_a = np.divide(2.0 * na, total, out=np.full(len(a), np.nan), where=total > 0)
    x_b = np.divide(2.0 * nb, total, out=np.full(len(a), np.nan), where=total > 0)
    other = np.divide(
        2.0 * norm(a + b),
        total,
        out=np.full(len(a), np.nan),
        where=total > 0,
    )
    return {
        "x_a": x_a,
        "x_b": x_b,
        "opposition_deg": safe_angle_deg(a, -b),
        "other": other,
        "a_norm": na,
        "b_norm": nb,
    }


def galactic_to_ecliptic(vector_galactic: np.ndarray) -> np.ndarray:
    vector_icrs = GALACTIC_TO_ICRS @ vector_galactic
    epsilon = math.radians(OBLIQUITY_DEG)
    rotation = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, math.cos(epsilon), math.sin(epsilon)],
            [0.0, -math.sin(epsilon), math.cos(epsilon)],
        ]
    )
    return rotation @ vector_icrs


def modern_galactic_parent() -> dict[str, object]:
    k = 4.74047
    r0_kpc = 8.178
    mu_l_mas_yr = 6.411
    mu_b_mas_yr = 0.219
    u_radial = 11.1
    tangential = k * mu_l_mas_yr * r0_kpc
    vertical = k * mu_b_mas_yr * r0_kpc
    galactic = np.array([u_radial, tangential, vertical], dtype=float)
    ecliptic = galactic_to_ecliptic(galactic)
    return {
        "galactic_components_km_s": galactic.tolist(),
        "ecliptic_components_km_s": ecliptic.tolist(),
        "speed_km_s": float(np.linalg.norm(ecliptic)),
    }


def summarize(values: np.ndarray) -> dict[str, float]:
    finite = values[np.isfinite(values)]
    return {
        "minimum": float(np.min(finite)),
        "p05": float(np.quantile(finite, 0.05)),
        "median": float(np.median(finite)),
        "p95": float(np.quantile(finite, 0.95)),
        "maximum": float(np.max(finite)),
    }


def strongest_periods(
    vector: np.ndarray, step_days: float, count: int = 8
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    centered = vector - np.mean(vector, axis=0, keepdims=True)
    window = np.hanning(len(centered))[:, None]
    transform = np.fft.rfft(centered * window, axis=0)
    power = np.sum(np.abs(transform) ** 2, axis=1)
    frequencies = np.fft.rfftfreq(len(centered), d=step_days)
    period_years = np.divide(
        1.0,
        frequencies * 365.25,
        out=np.full_like(frequencies, np.inf),
        where=frequencies > 0,
    )
    eligible = (period_years >= 1.5) & (period_years <= 100.0)
    idx = np.flatnonzero(eligible)
    local = idx[
        (power[idx] >= power[np.maximum(idx - 1, 0)])
        & (power[idx] >= power[np.minimum(idx + 1, len(power) - 1)])
    ]
    ordered = local[np.argsort(power[local])[::-1]]
    selected: list[int] = []
    for candidate in ordered:
        p = period_years[candidate]
        if all(abs(math.log(p / period_years[prior])) > 0.035 for prior in selected):
            selected.append(int(candidate))
        if len(selected) >= count:
            break
    peak_power = max(float(np.max(power[eligible])), 1.0)
    rows = pd.DataFrame(
        {
            "rank": np.arange(1, len(selected) + 1),
            "period_years": [float(period_years[i]) for i in selected],
            "relative_power": [float(power[i] / peak_power) for i in selected],
        }
    )
    return rows, period_years[eligible], power[eligible] / peak_power


def gate_result(value: float, operator: str, threshold: float, threshold2=None) -> bool:
    if operator == "between":
        assert threshold2 is not None
        return threshold <= value <= threshold2
    if operator == "lt":
        return value < threshold
    raise ValueError(operator)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/segoeuib.ttf"]
        if bold
        else ["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/segoeui.ttf"]
    )
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    subtitle: str,
) -> tuple[int, int, int, int]:
    left, top, right, bottom = box
    draw.rounded_rectangle(box, radius=16, fill="#f8fafc", outline="#cbd5e1", width=2)
    draw.text((left + 22, top + 16), title, fill="#172033", font=font(24, True))
    draw.text((left + 22, top + 50), subtitle, fill="#64748b", font=font(15))
    return left + 78, top + 92, right - 30, bottom - 58


def line_chart(
    draw: ImageDraw.ImageDraw,
    plot: tuple[int, int, int, int],
    x: np.ndarray,
    named: list[tuple[str, np.ndarray, str]],
    y_min: float,
    y_max: float,
    *,
    y_transform=lambda z: z,
    y_labels: list[tuple[float, str]] | None = None,
    reference: float | None = None,
    x_labels: tuple[str, str] | None = None,
) -> None:
    x0, y0, x1, y1 = plot
    for fraction in np.linspace(0, 1, 5):
        yp = y1 - fraction * (y1 - y0)
        draw.line((x0, yp, x1, yp), fill="#e2e8f0", width=1)
    transformed_min = y_transform(y_min)
    transformed_max = y_transform(y_max)
    if y_labels is None:
        y_labels = [
            (y_min + i * (y_max - y_min) / 4.0, f"{y_min + i * (y_max - y_min) / 4.0:.4g}")
            for i in range(5)
        ]
    for value, label in y_labels:
        fraction = (y_transform(value) - transformed_min) / (transformed_max - transformed_min)
        yp = y1 - fraction * (y1 - y0)
        draw.text((x0 - 66, yp - 9), label, fill="#64748b", font=font(14))
    if reference is not None:
        fraction = (y_transform(reference) - transformed_min) / (transformed_max - transformed_min)
        yp = y1 - fraction * (y1 - y0)
        draw.line((x0, yp, x1, yp), fill="#111827", width=2)
    x_min = float(np.nanmin(x))
    x_max = float(np.nanmax(x))
    for name, values, colour in named:
        finite = np.isfinite(x) & np.isfinite(values) & (values > 0 if y_transform is np.log10 else True)
        points = []
        for xv, yv in zip(x[finite], values[finite]):
            xp = x0 + (float(xv) - x_min) / (x_max - x_min) * (x1 - x0)
            fraction = (y_transform(float(yv)) - transformed_min) / (transformed_max - transformed_min)
            yp = y1 - fraction * (y1 - y0)
            points.append((xp, yp))
        if len(points) >= 2:
            if name.startswith("−"):
                for start in range(0, len(points) - 1, 20):
                    segment = points[start : min(start + 12, len(points))]
                    if len(segment) >= 2:
                        draw.line(segment, fill=colour, width=3)
            else:
                draw.line(points, fill=colour, width=3)
    legend_x = x0
    for name, _values, colour in named:
        draw.line((legend_x, y1 + 29, legend_x + 28, y1 + 29), fill=colour, width=4)
        draw.text((legend_x + 35, y1 + 18), name, fill="#334155", font=font(15))
        legend_x += max(190, 14 * len(name))
    if x_labels is None:
        x_labels = (f"{x_min:.0f}", f"{x_max:.0f}")
    draw.text((x0, y1 + 2), x_labels[0], fill="#64748b", font=font(13))
    right_label = x_labels[1]
    width = draw.textbbox((0, 0), right_label, font=font(13))[2]
    draw.text((x1 - width, y1 + 2), right_label, fill="#64748b", font=font(13))


def build_figure(
    series: pd.DataFrame,
    annual: pd.DataFrame,
    spectrum_period: np.ndarray,
    spectrum_sun: np.ndarray,
    spectrum_planets: np.ndarray,
    results: dict[str, object],
) -> None:
    blue = "#3676c8"
    gold = "#d99a2b"
    grey = "#8a96a8"
    image = Image.new("RGB", (1900, 1250), "#ffffff")
    draw = ImageDraw.Draw(image)
    draw.text(
        (52, 28),
        "T317 — Sun Phase A and planetary Phase B",
        fill="#111827",
        font=font(42, True),
    )
    draw.text(
        (55, 80),
        "Solar-System barycentric ARA crosswalk · JPL Horizons 1900–2101 · five-day cadence",
        fill="#475569",
        font=font(20),
    )

    subset = series[(series["year"] >= 2000) & (series["year"] <= 2035)]
    plot = panel(
        draw,
        (42, 125, 935, 595),
        "Sun and combined-planet velocity coordinates",
        "Independent magnitudes normalized to one shared 0–2 ARA diameter",
    )
    pair_values = np.concatenate(
        [subset["velocity_x_a_9"].to_numpy(), subset["velocity_x_b_9"].to_numpy()]
    )
    padding = max(5e-7, 0.12 * float(np.ptp(pair_values)))
    line_chart(
        draw,
        plot,
        subset["year_fraction"].to_numpy(),
        [
            ("Sun Phase A", subset["velocity_x_a_9"].to_numpy(), blue),
            ("Planets Phase B", subset["velocity_x_b_9"].to_numpy(), gold),
        ],
        float(np.min(pair_values) - padding),
        float(np.max(pair_values) + padding),
        reference=1.0,
        y_labels=[
            (
                float(np.min(pair_values) - padding)
                + i
                * (
                    float(np.max(pair_values) + padding)
                    - float(np.min(pair_values) - padding)
                )
                / 4.0,
                f"{float(np.min(pair_values) - padding) + i * (float(np.max(pair_values) + padding) - float(np.min(pair_values) - padding)) / 4.0:.7f}",
            )
            for i in range(5)
        ],
        x_labels=("2000", "2035"),
    )

    plot = panel(
        draw,
        (965, 125, 1858, 595),
        "Unresolved velocity Other",
        "Eight-planet definition versus Pluto-system sensitivity · logarithmic scale",
    )
    other_values = np.concatenate(
        [series["velocity_other_8"].to_numpy(), series["velocity_other_9"].to_numpy()]
    )
    positive = other_values[np.isfinite(other_values) & (other_values > 0)]
    log_min = 10 ** math.floor(math.log10(float(np.quantile(positive, 0.001))))
    log_max = 10 ** math.ceil(math.log10(float(np.quantile(positive, 0.999))))
    log_ticks = np.geomspace(log_min, log_max, 5)
    line_chart(
        draw,
        plot,
        series["year_fraction"].to_numpy(),
        [
            ("8 planets", series["velocity_other_8"].to_numpy(), grey),
            ("8 + Pluto", series["velocity_other_9"].to_numpy(), blue),
        ],
        log_min,
        log_max,
        y_transform=np.log10,
        y_labels=[(v, f"{v:.0e}") for v in log_ticks],
        x_labels=("1900", "2100"),
    )

    plot = panel(
        draw,
        (42, 625, 935, 1105),
        "Absolute planetary movement composition",
        "Annual mean share of summed |GM × velocity| before vector cancellation",
    )
    x0, y0, x1, y1 = plot
    pivot = annual.pivot(index="year", columns="body", values="mean_absolute_share")
    order = ["jupiter", "saturn", "uranus", "neptune", "emb", "venus", "mars", "mercury", "pluto"]
    colours = ["#3676c8", "#d99a2b", "#7893b8", "#d7b878", "#aeb9c9", "#c8a66a", "#c8d1dd", "#e0cda8", "#edf0f5"]
    pivot = pivot.reindex(columns=order).fillna(0.0)
    years = pivot.index.to_numpy(dtype=float)
    lower = np.zeros(len(years))
    for key, colour in zip(order, colours):
        upper = lower + pivot[key].to_numpy()
        upper_points = [
            (
                x0 + (yr - years.min()) / (years.max() - years.min()) * (x1 - x0),
                y1 - value * (y1 - y0),
            )
            for yr, value in zip(years, upper)
        ]
        lower_points = [
            (
                x0 + (yr - years.min()) / (years.max() - years.min()) * (x1 - x0),
                y1 - value * (y1 - y0),
            )
            for yr, value in zip(years[::-1], lower[::-1])
        ]
        draw.polygon(upper_points + lower_points, fill=colour)
        lower = upper
    for fraction in np.linspace(0, 1, 5):
        yp = y1 - fraction * (y1 - y0)
        draw.line((x0, yp, x1, yp), fill="#ffffff", width=1)
        draw.text((x0 - 55, yp - 9), f"{fraction:.2f}", fill="#64748b", font=font(13))
    legend_x, legend_y = x0, y1 + 18
    for key, colour in zip(order, colours):
        draw.rectangle((legend_x, legend_y, legend_x + 14, legend_y + 14), fill=colour, outline="#64748b")
        draw.text((legend_x + 20, legend_y - 3), key.title(), fill="#334155", font=font(13))
        legend_x += 18 * len(key) + 52
        if legend_x > x1 - 110:
            legend_x = x0
            legend_y += 24

    plot = panel(
        draw,
        (965, 625, 1858, 1105),
        "Vector-component period spectrum",
        "Sun and negative combined-planets spectra; relative power, log-period axis",
    )
    log_period = np.log10(spectrum_period)
    line_chart(
        draw,
        plot,
        log_period,
        [
            ("Sun", spectrum_sun, blue),
            ("−combined planets", spectrum_planets, gold),
        ],
        0.0,
        1.05,
        x_labels=("1.5 y", "100 y"),
    )

    gate_count = results["gates"]["passed"]
    gate_total = results["gates"]["total"]
    med_other = results["extended_nine"]["velocity"]["other"]["median"]
    med_angle = results["extended_nine"]["velocity"]["opposition_deg"]["median"]
    draw.text(
        (55, 1150),
        f"Crosswalk gates {gate_count}/{gate_total} · median opposition error {med_angle:.6g}° · median Other {med_other:.3g}.",
        fill="#475569",
        font=font(18, True),
    )
    draw.text(
        (55, 1185),
        "The sum xA+xB=2 and near opposition are conservation structure. Composition, residual and cadence are the informative measurements.",
        fill="#64748b",
        font=font(17),
    )
    image.save(FIGURE_PATH)


def main() -> None:
    frames = load_frames()
    jd = frames["sun"]["jd_tdb"].to_numpy(dtype=float)
    calendar = frames["sun"]["calendar_tdb"].astype(str)
    dates = pd.to_datetime(calendar.str.extract(r"(\d{4}-[A-Za-z]{3}-\d{2})")[0], format="%Y-%b-%d")
    year = dates.dt.year.to_numpy()
    year_fraction = year + (dates.dt.dayofyear.to_numpy() - 1) / 365.25

    positions = {b.key: vectors(frames[b.key], "position") for b in BODIES}
    velocities = {b.key: vectors(frames[b.key], "velocity") for b in BODIES}
    q_weighted = {b.key: b.gm * positions[b.key] for b in BODIES}
    p_weighted = {b.key: b.gm * velocities[b.key] for b in BODIES}

    primary_keys = [b.key for b in BODIES if b.primary]
    extended_keys = primary_keys + ["pluto"]
    q_a = q_weighted["sun"]
    p_a = p_weighted["sun"]
    q_b8 = np.sum([q_weighted[k] for k in primary_keys], axis=0)
    p_b8 = np.sum([p_weighted[k] for k in primary_keys], axis=0)
    q_b9 = np.sum([q_weighted[k] for k in extended_keys], axis=0)
    p_b9 = np.sum([p_weighted[k] for k in extended_keys], axis=0)

    q8 = pair_metrics(q_a, q_b8)
    p8 = pair_metrics(p_a, p_b8)
    q9 = pair_metrics(q_a, q_b9)
    p9 = pair_metrics(p_a, p_b9)

    combined_norm = norm(p_b9)
    u_b = np.divide(
        p_b9,
        combined_norm[:, None],
        out=np.zeros_like(p_b9),
        where=combined_norm[:, None] > 0,
    )
    absolute_denominator = np.sum([norm(p_weighted[k]) for k in extended_keys], axis=0)
    composition_rows: list[dict[str, object]] = []
    projection_matrix = []
    absolute_matrix = []
    for key in extended_keys:
        projection = np.divide(
            np.sum(p_weighted[key] * u_b, axis=1),
            combined_norm,
            out=np.full(len(jd), np.nan),
            where=combined_norm > 0,
        )
        absolute_share = np.divide(
            norm(p_weighted[key]),
            absolute_denominator,
            out=np.full(len(jd), np.nan),
            where=absolute_denominator > 0,
        )
        projection_matrix.append(projection)
        absolute_matrix.append(absolute_share)
        temp = pd.DataFrame(
            {
                "year": year,
                "projection_share": projection,
                "absolute_share": absolute_share,
            }
        )
        grouped = temp.groupby("year", as_index=False).agg(
            mean_projection_share=("projection_share", "mean"),
            median_projection_share=("projection_share", "median"),
            mean_absolute_share=("absolute_share", "mean"),
            median_absolute_share=("absolute_share", "median"),
        )
        for row in grouped.itertuples(index=False):
            composition_rows.append(
                {
                    "year": int(row.year),
                    "body": key,
                    "mean_projection_share": float(row.mean_projection_share),
                    "median_projection_share": float(row.median_projection_share),
                    "mean_absolute_share": float(row.mean_absolute_share),
                    "median_absolute_share": float(row.median_absolute_share),
                }
            )
    projection_matrix_np = np.column_stack(projection_matrix)
    absolute_matrix_np = np.column_stack(absolute_matrix)
    top_projection_idx = np.argmax(np.abs(projection_matrix_np), axis=1)
    top_absolute_idx = np.argmax(absolute_matrix_np, axis=1)
    top_projection = np.array(extended_keys, dtype=object)[top_projection_idx]
    top_absolute = np.array(extended_keys, dtype=object)[top_absolute_idx]

    gm_total9 = GM["sun"] + sum(GM[k] for k in extended_keys)
    external = modern_galactic_parent()
    parent = np.asarray(external["ecliptic_components_km_s"], dtype=float)
    internal_whole_velocity = (p_a + p_b9) / gm_total9
    whole_velocity = internal_whole_velocity + parent[None, :]
    external_deviation_m_s = norm(whole_velocity - parent[None, :]) * 1000.0
    internal_barycentre_offset_km = norm((q_a + q_b9) / gm_total9)

    step_days = float(np.median(np.diff(jd)))
    sun_peaks, spectrum_period, spectrum_sun = strongest_periods(p_a, step_days)
    planet_peaks, spectrum_period_b, spectrum_planets = strongest_periods(-p_b9, step_days)
    if not np.allclose(spectrum_period, spectrum_period_b):
        raise RuntimeError("Spectrum grids do not match")
    spectrum_cosine = float(
        np.dot(spectrum_sun, spectrum_planets)
        / (np.linalg.norm(spectrum_sun) * np.linalg.norm(spectrum_planets))
    )

    series = pd.DataFrame(
        {
            "jd_tdb": jd,
            "calendar_tdb": calendar,
            "year": year,
            "year_fraction": year_fraction,
            "velocity_x_a_8": p8["x_a"],
            "velocity_x_b_8": p8["x_b"],
            "velocity_opposition_deg_8": p8["opposition_deg"],
            "velocity_other_8": p8["other"],
            "velocity_x_a_9": p9["x_a"],
            "velocity_x_b_9": p9["x_b"],
            "velocity_opposition_deg_9": p9["opposition_deg"],
            "velocity_other_9": p9["other"],
            "position_x_a_8": q8["x_a"],
            "position_x_b_8": q8["x_b"],
            "position_opposition_deg_8": q8["opposition_deg"],
            "position_other_8": q8["other"],
            "position_x_a_9": q9["x_a"],
            "position_x_b_9": q9["x_b"],
            "position_opposition_deg_9": q9["opposition_deg"],
            "position_other_9": q9["other"],
            "external_parent_deviation_m_s": external_deviation_m_s,
            "internal_barycentre_offset_km": internal_barycentre_offset_km,
            "top_projection_body": top_projection,
            "top_absolute_body": top_absolute,
        }
    )
    annual = pd.DataFrame(composition_rows)
    series.to_csv(SERIES_PATH, index=False)
    annual.to_csv(COMPOSITION_PATH, index=False)

    body_summary: dict[str, object] = {}
    for i, key in enumerate(extended_keys):
        body_summary[key] = {
            "gm_km3_s2": GM[key],
            "projection_share": summarize(projection_matrix_np[:, i]),
            "absolute_movement_share": summarize(absolute_matrix_np[:, i]),
            "top_projection_frequency": float(np.mean(top_projection == key)),
            "top_absolute_frequency": float(np.mean(top_absolute == key)),
        }

    extended_velocity = {
        "x_a": summarize(p9["x_a"]),
        "x_b": summarize(p9["x_b"]),
        "opposition_deg": summarize(p9["opposition_deg"]),
        "other": summarize(p9["other"]),
    }
    extended_position = {
        "x_a": summarize(q9["x_a"]),
        "x_b": summarize(q9["x_b"]),
        "opposition_deg": summarize(q9["opposition_deg"]),
        "other": summarize(q9["other"]),
    }
    gates = [
        {
            "name": "velocity_x_a_median",
            "value": extended_velocity["x_a"]["median"],
            "rule": "[0.995, 1.005]",
            "passed": gate_result(extended_velocity["x_a"]["median"], "between", 0.995, 1.005),
        },
        {
            "name": "velocity_x_b_median",
            "value": extended_velocity["x_b"]["median"],
            "rule": "[0.995, 1.005]",
            "passed": gate_result(extended_velocity["x_b"]["median"], "between", 0.995, 1.005),
        },
        {
            "name": "velocity_opposition_median_deg",
            "value": extended_velocity["opposition_deg"]["median"],
            "rule": "<0.05°",
            "passed": gate_result(extended_velocity["opposition_deg"]["median"], "lt", 0.05),
        },
        {
            "name": "velocity_other_median",
            "value": extended_velocity["other"]["median"],
            "rule": "<0.005",
            "passed": gate_result(extended_velocity["other"]["median"], "lt", 0.005),
        },
        {
            "name": "position_opposition_median_deg",
            "value": extended_position["opposition_deg"]["median"],
            "rule": "<0.05°",
            "passed": gate_result(extended_position["opposition_deg"]["median"], "lt", 0.05),
        },
        {
            "name": "position_other_median",
            "value": extended_position["other"]["median"],
            "rule": "<0.005",
            "passed": gate_result(extended_position["other"]["median"], "lt", 0.005),
        },
    ]
    pass_count = sum(int(g["passed"]) for g in gates)

    source_files = {}
    for body in BODIES:
        raw = DATA_DIR / f"{body.key}_horizons_raw.txt"
        parsed = DATA_DIR / f"{body.key}_vectors.csv"
        source_files[body.key] = {
            "label": body.label,
            "command": body.command,
            "raw_sha256": sha256(raw),
            "parsed_sha256": sha256(parsed),
            "rows": int(len(frames[body.key])),
        }

    results: dict[str, object] = {
        "test_id": "T317",
        "date": "2026-07-31",
        "status": "CROSSWALK / CALIBRATION",
        "source": {
            "provider": "NASA/JPL Horizons",
            "center": "500@0 Solar-System barycentre",
            "start": START,
            "stop": STOP,
            "step": STEP,
            "time_type": "TDB",
            "reference_plane": "ECLIPTIC",
            "reference_system": "ICRF",
            "units": "KM-S",
            "files": source_files,
        },
        "gm_source": "JPL Astrodynamic Parameters, DE440",
        "rows": int(len(jd)),
        "step_days": step_days,
        "primary_eight": {
            "velocity": {
                "x_a": summarize(p8["x_a"]),
                "x_b": summarize(p8["x_b"]),
                "opposition_deg": summarize(p8["opposition_deg"]),
                "other": summarize(p8["other"]),
            },
            "position": {
                "x_a": summarize(q8["x_a"]),
                "x_b": summarize(q8["x_b"]),
                "opposition_deg": summarize(q8["opposition_deg"]),
                "other": summarize(q8["other"]),
            },
        },
        "extended_nine": {
            "velocity": extended_velocity,
            "position": extended_position,
        },
        "gates": {
            "passed": pass_count,
            "total": len(gates),
            "all_passed": pass_count == len(gates),
            "items": gates,
        },
        "planetary_composition": body_summary,
        "cadence": {
            "sun_peaks": sun_peaks.to_dict(orient="records"),
            "combined_planet_peaks": planet_peaks.to_dict(orient="records"),
            "spectrum_cosine_similarity": spectrum_cosine,
        },
        "external_parent": {
            **external,
            "completed_whole_deviation_m_s": summarize(external_deviation_m_s),
            "internal_barycentre_offset_km": summarize(internal_barycentre_offset_km),
        },
        "forced_boundaries": [
            "x_A + x_B = 2 is forced by normalization",
            "near opposition is expected from barycentric momentum conservation",
            "the external parent translation is a change of frame, not a new Galactic model",
        ],
    }
    RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    build_figure(
        series,
        annual,
        spectrum_period,
        spectrum_sun,
        spectrum_planets,
        results,
    )
    write_report(results)


def write_report(results: dict[str, object]) -> None:
    v8 = results["primary_eight"]["velocity"]
    v9 = results["extended_nine"]["velocity"]
    q9 = results["extended_nine"]["position"]
    composition = results["planetary_composition"]
    cadence = results["cadence"]
    external = results["external_parent"]
    gates = results["gates"]
    top_periods = ", ".join(
        f"{row['period_years']:.3f} y"
        for row in cadence["sun_peaks"][:5]
    )
    top_absolute_share = sorted(
        composition.items(),
        key=lambda item: item[1]["absolute_movement_share"]["median"],
        reverse=True,
    )[:4]
    top_absolute_share_text = ", ".join(
        f"{name} {values['absolute_movement_share']['median']:.1%}"
        for name, values in top_absolute_share
    )
    jupiter_top_projection_frequency = composition["jupiter"][
        "top_projection_frequency"
    ]
    improvement_v = 1.0 - v9["other"]["median"] / v8["other"]["median"]

    report = rf"""# Sun and Planets as One Solar-System ARA Pair

**Test:** T317  
**Date:** 31 July 2026  
**Evidence class:** public-data crosswalk/calibration; established conservation is not a discovery  
**Primary result:** **{gates['passed']}/{gates['total']} registered crosswalk gates passed**

## Technical summary

The corrected Solar-System assignment works numerically:

\[
\underbrace{{\mathbf A(t)}}_{{\text{{Sun / Phase A}}}}
+
\underbrace{{\mathbf B(t)}}_{{\text{{planetary systems / Phase B}}}}
\longrightarrow
\underbrace{{\text{{Solar-System barycentric parent}}}}_{{\text{{completed whole}}}}.
\]

Across `{results['rows']:,}` public five-day JPL Horizons states from 1900
through 2100, the extended Sun-versus-planets velocity pair sat at
`x_A={v9['x_a']['median']:.9f}` and `x_B={v9['x_b']['median']:.9f}`. Its
median opposition error was `{v9['opposition_deg']['median']:.9g}°` and its
unresolved velocity Other was `{v9['other']['median']:.9g}` TE-ARA units.
The GM-weighted position pair also closed, with median opposition error
`{q9['opposition_deg']['median']:.9g}°` and Other
`{q9['other']['median']:.9g}`.

That is a faithful ARA crosswalk, but its central closure is established
barycentric mechanics. The useful extra description is the changing planetary
composition, the residual left by omitted small bodies and the cadence carried
through both sides of the pair.

![T317 Solar-System barycentric ARA](T317_SOLAR_SYSTEM_BARYCENTRIC_ARA.png)

## The Solar-System identity is Sun versus the planetary collective

The previous orbital T309 cut used Earth relative to the Sun as one child and
projected it directly against Galactic parent travel. T317 restores the missing
Solar-System level. Earth is one contribution inside Phase B; it is not the
Sun's complete opposite pole.

The primary eight-planet pair had median velocity Other
`{v8['other']['median']:.9g}`. Adding Pluto's system reduced that median by
`{improvement_v:.2%}` to `{v9['other']['median']:.9g}`. The remaining Other is
kept visible rather than assigned to either pole; it can include integrated
asteroids and differences between the retained mass model and the full JPL
ephemeris.

## Phase B is a changing web, not one planet

Jupiter supplied the largest absolute signed projection onto the combined
planetary vector in `{jupiter_top_projection_frequency:.1%}` of time slices.
The median shares of total absolute planetary movement were:
{top_absolute_share_text}. These are kinematic composition shares, not mass
shares.

The stacked composition in the figure uses each system's absolute
\(|GM\,\mathbf v|\) divided by the sum across retained planetary systems. It
therefore shows how much movement each child carries before vector
cancellation. Signed projection shares are retained separately in
`T317_SOLAR_SYSTEM_BARYCENTRIC_ARA_COMPOSITION.csv`.

## The same cadence appears on both sides because they are a conserved pair

The strongest Sun-vector periods were {top_periods}. The normalized
component-spectrum cosine similarity between the Sun and the negative
combined-planet vector was `{cadence['spectrum_cosine_similarity']:.9f}`.

This shared spectrum is expected: the planetary collective generates the
Sun's barycentric counter-motion. It is still useful for the ARA architecture
because it shows that the Phase-A and Phase-B labels refer to two measurable
sides of one dynamical identity rather than two unrelated curves.

## The completed parent follows the external Galactic translation

After internal A/B cancellation, adding the modern Galactocentric parent
vector gave a median completed-whole deviation of
`{external['completed_whole_deviation_m_s']['median']:.9g} m/s` from that
parent. The retained bodies' median internal barycentre offset was
`{external['internal_barycentre_offset_km']['median']:.9g} km`.

This is the correct rung order:

\[
\text{{Sun + planets}}
\longrightarrow
\text{{Solar-System parent}}
\longrightarrow
\text{{that parent translated through the Galaxy}}.
\]

It is a frame reconstruction, not a new model of Galactic gravity.

## What passed, what is forced and what remains informative

All `{gates['total']}` registered numerical crosswalk gates
{'passed' if gates['all_passed'] else 'did not pass'}. Three boundaries must
remain attached to that statement:

1. \(x_A+x_B=2\) is imposed by normalization.
2. Near opposition and low Other are expected from established barycentric
   conservation.
3. The informative non-forced results are the time-varying child composition,
   the size and identity of the residual, and the cadence decomposition.

Therefore T317 supports the corrected **placement** of the ARA cut. It does
not independently validate universal ARA dynamics or recover new Solar-System
physics.

## Scope and method

- Source: NASA/JPL Horizons vector tables, targets `10` and `1`–`9`, all
  relative to `500@0`.
- Interval: 1900-01-01 through 2101-01-01 TDB at five-day cadence.
- Frame: ecliptic ICRF/J2000, geometric vectors, no aberration correction.
- Weighting: JPL DE440 gravitational parameters.
- Phase A: \(GM_\odot\mathbf v_\odot\).
- Phase B: the vector sum of planetary-system \(GM_i\mathbf v_i\).
- Other: normalized magnitude of the unresolved vector sum.
- Cadence: Hann-windowed FFT power summed across all three vector components.

## Limitations and next test

This test uses planetary-system barycentres and does not individually unpack
moons, asteroids or other small bodies. Its central balance is a known
conservation identity and should be treated as a calibration of ARA language.

The next non-trivial test should freeze a prediction from the child
composition—such as when Jupiter/Saturn directional dominance changes or how
much a named omitted-body group reduces Other—and score that prediction on a
held-out interval or a higher-completeness ephemeris.

## Reproduction

```powershell
python t317_solar_system_barycentric_ara.py --fetch
python validate_t317_solar_system_barycentric_ara.py
```

Primary sources:

- JPL Horizons: https://ssd.jpl.nasa.gov/horizons/
- JPL Horizons manual: https://ssd.jpl.nasa.gov/horizons/manual.html
- JPL DE440 astrodynamic parameters: https://ssd.jpl.nasa.gov/astro_par.html
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--force-fetch", action="store_true")
    args = parser.parse_args()
    if args.fetch or args.force_fetch:
        for body in BODIES:
            print(f"Fetching {body.label}…", flush=True)
            fetch_body(body, force=args.force_fetch)
    main()
