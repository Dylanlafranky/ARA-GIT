#!/usr/bin/env python3
"""T309 registered Galactic-orbit 7.5/15 ARA geometry test."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
SOURCE_PATH = HERE / "data" / "t308" / "earth_sun_vectors.csv"
RESULTS_PATH = HERE / "T309_GALACTIC_ORBIT_7_5_15_RESULTS.json"
YEAR_PATH = HERE / "T309_GALACTIC_ORBIT_7_5_15_YEARLY.csv"
SENSITIVITY_PATH = HERE / "T309_GALACTIC_ORBIT_7_5_15_SENSITIVITY.csv"
FIGURE_PATH = HERE / "T309_GALACTIC_ORBIT_7_5_15.png"
REPORT_PATH = HERE / "T309_GALACTIC_ORBIT_7_5_15_REPORT_2026-07-31.md"

SPLIT_JD = 2456293.5  # 2013-01-01 00:00 TDB
GALACTIC_SPEED_KM_S = 829000.0 / 3600.0
SPEED_CONTROLS = [200.0, 220.0, GALACTIC_SPEED_KM_S, 240.0, 250.0, 300.0, 369.0]
ALPHA_TARGET_DEG = 7.5
BETA_TARGET_DEG = 15.0
ALPHA_TOL_DEG = 0.25
BETA_TOL_DEG = 0.5
MEASURED_R0_KPC = 8.178
MEASURED_MU_L_MAS_YR = 6.411
MEASURED_MU_B_MAS_YR = 0.219
MEASURED_U_KM_S = 11.1
MAS_YR_KPC_TO_KM_S = 4.74047

# IAU/J2000 ICRS -> Galactic rotation matrix. Galactic -> ICRS is transpose.
ICRS_TO_GAL = np.array(
    [
        [-0.0548755604162154, -0.8734370902348850, -0.4838350155487132],
        [+0.4941094278755837, -0.4448296299600112, +0.7469822444972189],
        [-0.8676661490190047, -0.1980763734312015, +0.4559837761750669],
    ],
    dtype=float,
)
OBLIQUITY_J2000_DEG = 23.439291111


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def galactic_lb_to_ecliptic(l_deg: float, b_deg: float) -> np.ndarray:
    """Return a unit vector in J2000 ecliptic Cartesian coordinates."""
    l_rad = math.radians(l_deg)
    b_rad = math.radians(b_deg)
    gal = np.array(
        [
            math.cos(b_rad) * math.cos(l_rad),
            math.cos(b_rad) * math.sin(l_rad),
            math.sin(b_rad),
        ]
    )
    icrs = ICRS_TO_GAL.T @ gal
    eps = math.radians(OBLIQUITY_J2000_DEG)
    eq_to_ecl = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, math.cos(eps), math.sin(eps)],
            [0.0, -math.sin(eps), math.cos(eps)],
        ]
    )
    ecliptic = eq_to_ecl @ icrs
    return ecliptic / np.linalg.norm(ecliptic)


def galactic_components_to_ecliptic(components: np.ndarray) -> np.ndarray:
    """Transform local Galactic U/V/W direction components to J2000 ecliptic."""
    galactic = components / np.linalg.norm(components)
    icrs = ICRS_TO_GAL.T @ galactic
    eps = math.radians(OBLIQUITY_J2000_DEG)
    eq_to_ecl = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, math.cos(eps), math.sin(eps)],
            [0.0, -math.sin(eps), math.cos(eps)],
        ]
    )
    ecliptic = eq_to_ecl @ icrs
    return ecliptic / np.linalg.norm(ecliptic)


def load_source() -> pd.DataFrame:
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(
            f"Missing {SOURCE_PATH}. Run t308_phi_temporal_ruler_orbital_probe.py "
            "--fetch first."
        )
    frame = pd.read_csv(SOURCE_PATH)
    required = {
        "jd_tdb",
        "calendar_tdb",
        "x_km",
        "y_km",
        "z_km",
        "vx_km_s",
        "vy_km_s",
        "vz_km_s",
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing source columns: {sorted(missing)}")
    if len(frame) < 9000:
        raise ValueError(f"Unexpectedly short source: {len(frame)} rows")
    years = frame["calendar_tdb"].astype(str).str.extract(r"(\d{4})-")[0]
    frame["year"] = years.astype(int)
    return frame


def estimate_period_days(frame: pd.DataFrame) -> float:
    calibration = frame.loc[frame["jd_tdb"] < SPLIT_JD]
    jd = calibration["jd_tdb"].to_numpy()
    theta = np.unwrap(
        np.arctan2(
            calibration["y_km"].to_numpy(),
            calibration["x_km"].to_numpy(),
        )
    )
    # Fit the long-run phase slope. A median instantaneous speed is biased by
    # the unequal time Earth spends near perihelion and aphelion.
    slope = float(np.polyfit(jd - jd[0], theta, 1)[0])
    return float(2.0 * np.pi / abs(slope))


def angle_deg(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    numerator = np.sum(a * b, axis=1)
    denominator = np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1)
    return np.degrees(np.arccos(np.clip(numerator / denominator, -1.0, 1.0)))


def vector_angle_to_axis_deg(vectors: np.ndarray, unit_axis: np.ndarray) -> np.ndarray:
    numerator = vectors @ unit_axis
    denominator = np.linalg.norm(vectors, axis=1)
    return np.degrees(np.arccos(np.clip(numerator / denominator, -1.0, 1.0)))


def interpolate_vectors(
    jd: np.ndarray, vectors: np.ndarray, query_jd: np.ndarray
) -> np.ndarray:
    return np.column_stack(
        [np.interp(query_jd, jd, vectors[:, column]) for column in range(3)]
    )


def summary(values: np.ndarray) -> dict[str, float]:
    q = np.quantile(values, [0.025, 0.25, 0.5, 0.75, 0.975])
    return {
        "min": float(np.min(values)),
        "q025": float(q[0]),
        "q25": float(q[1]),
        "median": float(q[2]),
        "mean": float(np.mean(values)),
        "q75": float(q[3]),
        "q975": float(q[4]),
        "max": float(np.max(values)),
        "std": float(np.std(values)),
    }


def evaluate_parent(
    frame: pd.DataFrame,
    period_days: float,
    parent_unit: np.ndarray,
    parent_speed_km_s: float,
) -> dict:
    jd = frame["jd_tdb"].to_numpy()
    child_velocity = frame[["vx_km_s", "vy_km_s", "vz_km_s"]].to_numpy()
    opposite_jd = jd + period_days / 2.0
    eligible = (jd >= SPLIT_JD) & (opposite_jd <= jd[-1])
    jd1 = jd[eligible]
    v1 = child_velocity[eligible]
    v2 = interpolate_vectors(jd, child_velocity, opposite_jd[eligible])
    year = frame.loc[eligible, "year"].to_numpy()

    parent = parent_speed_km_s * parent_unit
    total1 = v1 + parent
    total2 = v2 + parent
    alpha1 = vector_angle_to_axis_deg(total1, parent_unit)
    alpha2 = vector_angle_to_axis_deg(total2, parent_unit)
    beta = angle_deg(total1, total2)
    alpha_sum = alpha1 + alpha2
    closure_residual = beta - alpha_sum
    ara_a = 2.0 * alpha1 / alpha_sum

    pair_frame = pd.DataFrame(
        {
            "jd_tdb": jd1,
            "year": year,
            "alpha_deg": alpha1,
            "alpha_opposite_deg": alpha2,
            "beta_deg": beta,
            "closure_residual_deg": closure_residual,
            "ara_a": ara_a,
        }
    )

    yearly_rows: list[dict] = []
    for current_year, group in pair_frame.groupby("year"):
        if len(group) < 350:
            continue
        alpha_max = float(group["alpha_deg"].max())
        beta_max = float(group["beta_deg"].max())
        yearly_rows.append(
            {
                "year": int(current_year),
                "n_pairs": int(len(group)),
                "alpha_median_deg": float(group["alpha_deg"].median()),
                "alpha_max_deg": alpha_max,
                "beta_median_deg": float(group["beta_deg"].median()),
                "beta_max_deg": beta_max,
                "beta_half_max_deg": beta_max / 2.0,
                "ara_a_median": float(group["ara_a"].median()),
                "alpha_max_pass": bool(
                    abs(alpha_max - ALPHA_TARGET_DEG) <= ALPHA_TOL_DEG
                ),
                "beta_max_pass": bool(
                    abs(beta_max - BETA_TARGET_DEG) <= BETA_TOL_DEG
                ),
            }
        )

    alpha_stats = summary(alpha1)
    beta_stats = summary(beta)
    central_pass = bool(
        abs(alpha_stats["median"] - ALPHA_TARGET_DEG) <= ALPHA_TOL_DEG
        and abs(beta_stats["median"] - BETA_TARGET_DEG) <= BETA_TOL_DEG
    )
    yearly_passes = sum(
        row["alpha_max_pass"] and row["beta_max_pass"] for row in yearly_rows
    )
    envelope_pass = bool(
        not central_pass
        and len(yearly_rows) >= 12
        and yearly_passes >= 9
    )

    if central_pass:
        verdict = "CENTRAL CADENCE SUPPORTED"
    elif envelope_pass:
        verdict = "STABLE CREST/ENVELOPE RECURRENCE"
    else:
        verdict = "NOT SUPPORTED"

    return {
        "parent_speed_km_s": float(parent_speed_km_s),
        "parent_unit_ecliptic_j2000": [float(x) for x in parent_unit],
        "n_pairs": int(len(pair_frame)),
        "alpha_deg": alpha_stats,
        "alpha_opposite_deg": summary(alpha2),
        "beta_deg": beta_stats,
        "closure_residual_deg": summary(closure_residual),
        "ara_a": summary(ara_a),
        "fraction_alpha_within_target_tolerance": float(
            np.mean(np.abs(alpha1 - ALPHA_TARGET_DEG) <= ALPHA_TOL_DEG)
        ),
        "fraction_beta_within_target_tolerance": float(
            np.mean(np.abs(beta - BETA_TARGET_DEG) <= BETA_TOL_DEG)
        ),
        "central_pass": central_pass,
        "complete_year_count": int(len(yearly_rows)),
        "envelope_year_pass_count": int(yearly_passes),
        "envelope_pass": envelope_pass,
        "verdict": verdict,
        "yearly": yearly_rows,
        "_pair_frame": pair_frame,
    }


def scalar_angle(frame: pd.DataFrame, speed_km_s: float) -> float:
    evaluation = frame.loc[frame["jd_tdb"] >= SPLIT_JD]
    v = evaluation[["vx_km_s", "vy_km_s", "vz_km_s"]].to_numpy()
    median_speed = float(np.median(np.linalg.norm(v, axis=1)))
    return math.degrees(math.atan(median_speed / speed_km_s))


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


def plot_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    x: np.ndarray,
    series: list[tuple[str, np.ndarray, str]],
    y_min: float,
    y_max: float,
    target: float | None = None,
    x_labels: tuple[str, str] | None = None,
) -> None:
    left, top, right, bottom = box
    draw.rounded_rectangle(box, radius=14, fill="#f8fafc", outline="#cbd5e1", width=2)
    draw.text((left + 22, top + 16), title, fill="#172033", font=font(25, True))
    plot = (left + 76, top + 65, right - 28, bottom - 58)
    px0, py0, px1, py1 = plot
    for fraction in np.linspace(0.0, 1.0, 5):
        yy = py1 - fraction * (py1 - py0)
        value = y_min + fraction * (y_max - y_min)
        draw.line((px0, yy, px1, yy), fill="#e2e8f0", width=1)
        draw.text((left + 12, yy - 10), f"{value:.1f}", fill="#64748b", font=font(16))
    if target is not None:
        yy = py1 - (target - y_min) / (y_max - y_min) * (py1 - py0)
        draw.line((px0, yy, px1, yy), fill="#111827", width=2)
        draw.text((px1 - 105, yy - 24), f"target {target:g}°", fill="#111827", font=font(15))
    x_min = float(np.min(x))
    x_max = float(np.max(x))
    for name, values, colour in series:
        points = []
        for xx, yy_value in zip(x, values):
            x_pixel = px0 + (float(xx) - x_min) / (x_max - x_min) * (px1 - px0)
            y_pixel = py1 - (float(yy_value) - y_min) / (y_max - y_min) * (py1 - py0)
            points.append((x_pixel, y_pixel))
        if len(points) >= 2:
            draw.line(points, fill=colour, width=3)
    legend_x = px0
    for name, _values, colour in series:
        draw.line((legend_x, bottom - 28, legend_x + 28, bottom - 28), fill=colour, width=4)
        draw.text((legend_x + 35, bottom - 39), name, fill="#334155", font=font(16))
        legend_x += 210
    if x_labels:
        draw.text((px0, py1 + 12), x_labels[0], fill="#64748b", font=font(15))
        width = draw.textbbox((0, 0), x_labels[1], font=font(15))[2]
        draw.text((px1 - width, py1 + 12), x_labels[1], fill="#64748b", font=font(15))


def make_figure(primary: dict, sensitivity_rows: list[dict]) -> None:
    image = Image.new("RGB", (1800, 1300), "#ffffff")
    draw = ImageDraw.Draw(image)
    draw.text(
        (55, 30),
        "T309 — Earth orbit extruded along Galactic parent travel",
        fill="#111827",
        font=font(42, True),
    )
    draw.text(
        (58, 84),
        "Full 3D velocity geometry; 7.5° branch target and independently measured 15° opposite-branch aperture",
        fill="#475569",
        font=font(21),
    )

    pairs = primary["_pair_frame"]
    first_year = int(pairs["year"].min())
    first = pairs.loc[pairs["year"] == first_year].head(365)
    plot_panel(
        draw,
        (45, 135, 875, 600),
        f"Evaluation trajectory through {first_year}",
        first["jd_tdb"].to_numpy(),
        [
            ("branch α", first["alpha_deg"].to_numpy(), "#356fc4"),
            ("aperture β / 2", first["beta_deg"].to_numpy() / 2.0, "#d89b2b"),
        ],
        5.5,
        8.0,
        target=7.5,
        x_labels=("start of year", "end of year"),
    )

    yearly = primary["yearly"]
    years = np.array([row["year"] for row in yearly], dtype=float)
    plot_panel(
        draw,
        (925, 135, 1755, 600),
        "Complete-year crest stability",
        years,
        [
            ("max α", np.array([row["alpha_max_deg"] for row in yearly]), "#356fc4"),
            (
                "max β / 2",
                np.array([row["beta_half_max_deg"] for row in yearly]),
                "#d89b2b",
            ),
        ],
        7.2,
        7.7,
        target=7.5,
        x_labels=(str(int(years.min())), str(int(years.max()))),
    )

    speed_rows = [row for row in sensitivity_rows if row["frame"] == "galactic_tangent"]
    speeds = np.array([row["speed_km_s"] for row in speed_rows])
    plot_panel(
        draw,
        (45, 645, 1125, 1165),
        "Dependence on declared parent speed",
        speeds,
        [
            (
                "scalar perpendicular",
                np.array([row["scalar_alpha_deg"] for row in speed_rows]),
                "#6b7280",
            ),
            (
                "3D median α",
                np.array([row["alpha_median_deg"] for row in speed_rows]),
                "#356fc4",
            ),
            (
                "3D crest α",
                np.array([row["alpha_max_deg"] for row in speed_rows]),
                "#d89b2b",
            ),
        ],
        4.0,
        9.0,
        target=7.5,
        x_labels=("200 km/s", "369 km/s"),
    )

    box = (1175, 645, 1755, 1165)
    draw.rounded_rectangle(box, radius=14, fill="#f8fafc", outline="#cbd5e1", width=2)
    draw.text((1202, 672), "Registered outcome", fill="#172033", font=font(28, True))
    verdict = primary["verdict"]
    verdict_colour = "#8a5a08" if "ENVELOPE" in verdict else "#1e5f4a"
    draw.text((1202, 722), verdict, fill=verdict_colour, font=font(25, True))
    measured = primary["measured_control"]
    lines = [
        f"median α      {primary['alpha_deg']['median']:.3f}°",
        f"maximum α     {primary['alpha_deg']['max']:.3f}°",
        f"median β      {primary['beta_deg']['median']:.3f}°",
        f"maximum β     {primary['beta_deg']['max']:.3f}°",
        "",
        f"yearly crest gate  {primary['envelope_year_pass_count']}/{primary['complete_year_count']}",
        "",
        f"modern vector max α  {measured['alpha_deg']['max']:.3f}°",
        f"modern vector max β  {measured['beta_deg']['max']:.3f}°",
        "robustness: NOT SUPPORTED",
    ]
    y = 782
    for line in lines:
        colour = "#9b2c2c" if "NOT SUPPORTED" in line else "#334155"
        draw.text((1205, y), line, fill=colour, font=font(19))
        y += 36
    draw.text(
        (55, 1210),
        "Source: NASA/JPL Horizons Earth–Sun vectors, 2000–2026. Parent model: NASA 829,000 km/h local Galactic tangent.",
        fill="#64748b",
        font=font(17),
    )
    draw.text(
        (55, 1240),
        "The 3D result is frame-specific and registered after the approximate scalar speed-ratio clue.",
        fill="#64748b",
        font=font(17),
    )
    image.save(FIGURE_PATH)


def write_report(results: dict) -> None:
    primary = results["primary_galactic_frame"]
    alpha = primary["alpha_deg"]
    beta = primary["beta_deg"]
    cmb = results["cmb_control"]
    measured = results["modern_measured_galactocentric_control"]
    years = primary["complete_year_count"]
    passes = primary["envelope_year_pass_count"]

    if primary["verdict"] == "CENTRAL CADENCE SUPPORTED":
        plain = (
            "The full three-dimensional orbit retained the 7.5° branch and "
            "15° opposite-branch aperture as central values."
        )
    elif primary["verdict"] == "STABLE CREST/ENVELOPE RECURRENCE":
        plain = (
            "The exact 3D orbit does reproduce the 7.5°/15° neighbourhood, "
            "but as the stable outer crest of the yearly motion—not as its "
            "typical or median angle."
        )
    else:
        plain = (
            "The exact 3D orbit did not retain 7.5°/15° either centrally or "
            "as a stable yearly crest."
        )

    report = f"""# T309 — Galactic-Orbit 7.5/15 ARA Geometry

**Date:** 31 July 2026  
**Registered verdict:** **{primary['verdict']}**  
**Evidence class:** exact-3D confirmation after a known scalar clue; not blind

## Plain-language result

{plain}

That registered result does **not** survive the stronger post-result
robustness audit. The `230.28 km/s` value is a rounded NASA public-facts
description. A modern astrometric construction using Sgr A*'s measured reflex
proper motion and the GRAVITY Galactic-centre distance gives a Solar velocity
of `{results['modern_measured_parent']['speed_km_s']:.3f} km/s` in a slightly
different three-dimensional direction. Under that vector:

- maximum alpha = `{measured['alpha_deg']['max']:.4f}°`;
- maximum beta = `{measured['beta_deg']['max']:.4f}°`;
- verdict = `{measured['verdict']}`.

The scientifically controlling conclusion is therefore:
**simplified-frame envelope recurrence; not robust as the best available
Galactocentric orbit estimate**.

The simple calculation
`atan(Earth orbital speed / Galactic parent speed)` gives
`{results['scalar_primary_alpha_deg']:.4f}°`, whose doubled value is
`{2 * results['scalar_primary_alpha_deg']:.4f}°`. Once the real orbital-plane
orientation and the changing three-dimensional Earth velocity are restored,
the evaluation median moves inward:

- branch inclination alpha: median `{alpha['median']:.4f}°`, range
  `{alpha['min']:.4f}°` to `{alpha['max']:.4f}°`;
- independently measured opposite-branch aperture beta: median
  `{beta['median']:.4f}°`, range `{beta['min']:.4f}°` to
  `{beta['max']:.4f}°`.

The central registered gate therefore
`{'passed' if primary['central_pass'] else 'did not pass'}`. The yearly crest
gate passed in `{passes}/{years}` complete evaluation years.

## What the geometry actually says

The 7.5° value is not the orbit's constant pitch. The branch breathes across
the year because the ecliptic is tilted relative to the declared Galactic
travel direction and because Earth's orbital speed varies. In the primary
frame, the outer branch reaches `{alpha['max']:.4f}°`; the full Phase A/Phase B
aperture reaches `{beta['max']:.4f}°`.

The directly measured aperture is almost exactly the sum of the two
parent-relative branch angles:

```text
median beta - (alpha_A + alpha_B)
= {primary['closure_residual_deg']['median']:.7f} degrees
```

That is a clean geometric decomposition of two opposite child branches around
one parent traversal axis. It is established vector geometry; calling it an
ARA parent/child crosswalk is the framework interpretation.

The normalized pair coordinate had median
`{primary['ara_a']['median']:.6f}` and range
`{primary['ara_a']['min']:.6f}` to `{primary['ara_a']['max']:.6f}`. Its
TE-ARA sum of two is imposed by normalization, so that sum is bookkeeping,
not independent evidence. The observed branch variation is the informative
part.

## Frame and speed controls

The result is relational, not absolute. In the CMB control frame:

- median alpha = `{cmb['alpha_deg']['median']:.4f}°`;
- maximum alpha = `{cmb['alpha_deg']['max']:.4f}°`;
- median beta = `{cmb['beta_deg']['median']:.4f}°`;
- maximum beta = `{cmb['beta_deg']['max']:.4f}°`.

The CMB control verdict is `{cmb['verdict']}`. Therefore the Galactic result
must not be described as a universal angle of Earth's motion. It belongs to
the declared child-orbit/parent-Galactic-travel relation.

The sensitivity table records the same Galactic direction from `200` through
`369 km/s`. This matters because the published `829,000 km/h` parent speed is
rounded and a different Galactic velocity convention changes the angle.

The modern measured-vector audit is not part of the originally registered
primary frame; it was added because the fixed speed sensitivity showed that
the result depended materially on the rounded parent speed. It is a required
post-result correction, not a second frozen prediction.

## ARA reading

The strongest faithful ARA statement is:

\\[
\\underbrace{{\\mathbf V_{{\\rm parent}}}}_{{\\text{{larger traversal}}}}
+
\\underbrace{{\\mathbf v_{{\\rm child}}(t)}}_{{\\text{{0→2→0 orbit}}}}
\\longrightarrow
\\underbrace{{\\mathbf v_\\oplus(t)}}_{{\\text{{extruded child path}}}}.
\\]

The earlier `7.5 : 15` cadence reappears in the simplified `230 km/s`
Galactocentric construction as a stable upper envelope. It does **not**
survive the best measured parent vector, and therefore cannot currently be
claimed as an orbital recovery. What does survive is the ARA-shaped
decomposition itself: one parent direction, two opposite child branches, an
almost exact branch-sum aperture and a periodically breathing asymmetry.

## Sources

- [NASA Solar System Facts](https://science.nasa.gov/solar-system/solar-system-facts/)
  — Solar System Galactic speed and period.
- [NASA Reference Systems](https://science.nasa.gov/learn/basics-of-space-flight/chapter2-1/)
  — Earth orbital-speed range.
- [NASA/JPL Horizons](https://ssd.jpl.nasa.gov/horizons/)
  — retained Earth-relative-to-Sun Cartesian vectors.
- [ESA Planck CMB velocity result](https://sci.esa.int/s/WLdyMrW)
  — CMB-frame control speed and direction.
- [Reid & Brunthaler (2020)](https://arxiv.org/abs/2001.04386)
  — measured Sgr A* reflex proper motion.
- [GRAVITY Collaboration (2019)](https://arxiv.org/abs/1904.05721)
  — geometric Galactic-centre distance used to convert proper motion to speed.
- [Schönrich, Binney & Dehnen (2010)](https://academic.oup.com/mnras/article/403/4/1829/1054839)
  — local Solar radial component and peculiar-motion reference.

## Reproduction

```powershell
python t308_phi_temporal_ruler_orbital_probe.py --fetch
python t309_galactic_orbit_7_5_15.py
python validate_t309_galactic_orbit_7_5_15.py
```

Source SHA-256:
`{results['source']['sha256']}`.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    frame = load_source()
    period_days = estimate_period_days(frame)
    galactic_unit = galactic_lb_to_ecliptic(90.0, 0.0)
    cmb_unit = galactic_lb_to_ecliptic(264.0, 48.0)
    measured_v = (
        MAS_YR_KPC_TO_KM_S * MEASURED_MU_L_MAS_YR * MEASURED_R0_KPC
    )
    measured_w = (
        MAS_YR_KPC_TO_KM_S * MEASURED_MU_B_MAS_YR * MEASURED_R0_KPC
    )
    measured_components = np.array([MEASURED_U_KM_S, measured_v, measured_w])
    measured_speed = float(np.linalg.norm(measured_components))
    measured_unit = galactic_components_to_ecliptic(measured_components)

    primary = evaluate_parent(
        frame, period_days, galactic_unit, GALACTIC_SPEED_KM_S
    )
    primary_pairs = primary.pop("_pair_frame")

    measured = evaluate_parent(
        frame, period_days, measured_unit, measured_speed
    )
    measured.pop("_pair_frame")
    primary["measured_control"] = measured

    sensitivity_rows: list[dict] = []
    for speed in SPEED_CONTROLS:
        evaluated = evaluate_parent(frame, period_days, galactic_unit, speed)
        evaluated.pop("_pair_frame")
        sensitivity_rows.append(
            {
                "frame": "galactic_tangent",
                "speed_km_s": float(speed),
                "scalar_alpha_deg": scalar_angle(frame, speed),
                "alpha_median_deg": evaluated["alpha_deg"]["median"],
                "alpha_max_deg": evaluated["alpha_deg"]["max"],
                "beta_median_deg": evaluated["beta_deg"]["median"],
                "beta_max_deg": evaluated["beta_deg"]["max"],
                "verdict": evaluated["verdict"],
            }
        )

    cmb = evaluate_parent(frame, period_days, cmb_unit, 369.0)
    cmb.pop("_pair_frame")
    sensitivity_rows.append(
        {
            "frame": "cmb",
            "speed_km_s": 369.0,
            "scalar_alpha_deg": scalar_angle(frame, 369.0),
            "alpha_median_deg": cmb["alpha_deg"]["median"],
            "alpha_max_deg": cmb["alpha_deg"]["max"],
            "beta_median_deg": cmb["beta_deg"]["median"],
            "beta_max_deg": cmb["beta_deg"]["max"],
            "verdict": cmb["verdict"],
        }
    )
    sensitivity_rows.append(
        {
            "frame": "modern_measured_galactocentric",
            "speed_km_s": measured_speed,
            "scalar_alpha_deg": scalar_angle(frame, measured_speed),
            "alpha_median_deg": measured["alpha_deg"]["median"],
            "alpha_max_deg": measured["alpha_deg"]["max"],
            "beta_median_deg": measured["beta_deg"]["median"],
            "beta_max_deg": measured["beta_deg"]["max"],
            "verdict": measured["verdict"],
        }
    )

    results = {
        "test_id": "T309",
        "registered_status": (
            "exact-3D confirmation after scalar 7.4/14.8 clue; not blind discovery"
        ),
        "source": {
            "path": str(SOURCE_PATH.relative_to(HERE)),
            "sha256": sha256(SOURCE_PATH),
            "rows": int(len(frame)),
            "start_jd_tdb": float(frame["jd_tdb"].min()),
            "stop_jd_tdb": float(frame["jd_tdb"].max()),
        },
        "period_days_from_calibration": float(period_days),
        "targets": {
            "alpha_deg": ALPHA_TARGET_DEG,
            "alpha_tolerance_deg": ALPHA_TOL_DEG,
            "beta_deg": BETA_TARGET_DEG,
            "beta_tolerance_deg": BETA_TOL_DEG,
        },
        "primary_parent": {
            "description": "local circular Galactic tangent",
            "galactic_l_deg": 90.0,
            "galactic_b_deg": 0.0,
            "speed_km_s": GALACTIC_SPEED_KM_S,
            "unit_ecliptic_j2000": [float(x) for x in galactic_unit],
        },
        "scalar_primary_alpha_deg": scalar_angle(frame, GALACTIC_SPEED_KM_S),
        "primary_galactic_frame": primary,
        "modern_measured_parent": {
            "construction": (
                "U from Schonrich et al. 2010; V and W reflex components "
                "from Reid & Brunthaler 2020 proper motions times R0=8.178 kpc"
            ),
            "r0_kpc": MEASURED_R0_KPC,
            "mu_l_mas_yr": MEASURED_MU_L_MAS_YR,
            "mu_b_mas_yr": MEASURED_MU_B_MAS_YR,
            "galactic_components_km_s": [
                float(value) for value in measured_components
            ],
            "speed_km_s": measured_speed,
            "unit_ecliptic_j2000": [float(value) for value in measured_unit],
        },
        "modern_measured_galactocentric_control": measured,
        "cmb_control": cmb,
        "sensitivity": sensitivity_rows,
        "robustness_verdict": (
            "NOT ROBUST TO MODERN MEASURED GALACTOCENTRIC VECTOR"
        ),
    }

    pd.DataFrame(primary["yearly"]).to_csv(YEAR_PATH, index=False)
    pd.DataFrame(sensitivity_rows).to_csv(SENSITIVITY_PATH, index=False)
    RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")

    primary_for_figure = dict(primary)
    primary_for_figure["_pair_frame"] = primary_pairs
    make_figure(primary_for_figure, sensitivity_rows)
    write_report(results)

    print(json.dumps(
        {
            "verdict": primary["verdict"],
            "period_days": period_days,
            "alpha_median_deg": primary["alpha_deg"]["median"],
            "alpha_max_deg": primary["alpha_deg"]["max"],
            "beta_median_deg": primary["beta_deg"]["median"],
            "beta_max_deg": primary["beta_deg"]["max"],
            "envelope_years": (
                f"{primary['envelope_year_pass_count']}/"
                f"{primary['complete_year_count']}"
            ),
            "figure": str(FIGURE_PATH),
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()
