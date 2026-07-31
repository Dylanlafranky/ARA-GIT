#!/usr/bin/env python3
"""T318: repeat T309 with Jupiter-system-barycentre relative to the Sun."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data" / "t317"
SUN_PATH = DATA_DIR / "sun_vectors.csv"
JUPITER_PATH = DATA_DIR / "jupiter_vectors.csv"
PROTOCOL_PATH = (
    HERE / "T318_JUPITER_GALACTIC_ORBIT_7_5_15_PROTOCOL_v1_REGISTERED.md"
)
RESULTS_PATH = HERE / "T318_JUPITER_GALACTIC_ORBIT_7_5_15_RESULTS.json"
CYCLE_PATH = HERE / "T318_JUPITER_GALACTIC_ORBIT_7_5_15_CYCLES.csv"
SERIES_PATH = HERE / "T318_JUPITER_GALACTIC_ORBIT_7_5_15_SERIES.csv"
FIGURE_PATH = HERE / "T318_JUPITER_GALACTIC_ORBIT_7_5_15.png"
REPORT_PATH = HERE / "T318_JUPITER_GALACTIC_ORBIT_7_5_15_REPORT_2026-07-31.md"

SPLIT_YEAR = 1950
STEP_DAYS = 5.0
ALPHA_TARGET_DEG = 7.5
BETA_TARGET_DEG = 15.0
ALPHA_TOL_DEG = 0.25
BETA_TOL_DEG = 0.5

ROUNDED_PARENT_SPEED = 230.27777777777777
ROUNDED_PARENT_UNIT = np.array(
    [0.4941094278755837, -0.11099073341911324, 0.8622858750898978],
    dtype=float,
)
MODERN_PARENT_SPEED = 248.93142028923324
MODERN_PARENT_UNIT = np.array(
    [0.46129050783760756, -0.1551427763070162, 0.8735798683226815],
    dtype=float,
)

FRAMES = {
    "rounded_t309": {
        "label": "T309 rounded Galactic tangent",
        "speed_km_s": ROUNDED_PARENT_SPEED,
        "unit": ROUNDED_PARENT_UNIT,
    },
    "modern_measured": {
        "label": "Modern measured Galactocentric vector",
        "speed_km_s": MODERN_PARENT_SPEED,
        "unit": MODERN_PARENT_UNIT,
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_child() -> pd.DataFrame:
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
    sun = pd.read_csv(SUN_PATH)
    jupiter = pd.read_csv(JUPITER_PATH)
    for label, frame in (("Sun", sun), ("Jupiter", jupiter)):
        missing = required.difference(frame.columns)
        if missing:
            raise ValueError(f"{label} source missing columns: {sorted(missing)}")
    if len(sun) != len(jupiter) or len(sun) < 14000:
        raise ValueError("Unexpected source row count or Sun/Jupiter mismatch")
    if not np.array_equal(
        sun["jd_tdb"].to_numpy(), jupiter["jd_tdb"].to_numpy()
    ):
        raise ValueError("Sun and Jupiter timestamps are not exactly aligned")

    out = pd.DataFrame(
        {
            "jd_tdb": sun["jd_tdb"].to_numpy(dtype=float),
            "calendar_tdb": sun["calendar_tdb"].astype(str),
        }
    )
    for column in ("x_km", "y_km", "z_km", "vx_km_s", "vy_km_s", "vz_km_s"):
        out[column] = (
            jupiter[column].to_numpy(dtype=float)
            - sun[column].to_numpy(dtype=float)
        )
    out["year"] = (
        out["calendar_tdb"].str.extract(r"(\d{4})-")[0].astype(int)
    )
    return out


def estimate_period_days(frame: pd.DataFrame) -> float:
    calibration = frame.loc[frame["year"] < SPLIT_YEAR]
    jd = calibration["jd_tdb"].to_numpy(dtype=float)
    theta = np.unwrap(
        np.arctan2(
            calibration["y_km"].to_numpy(dtype=float),
            calibration["x_km"].to_numpy(dtype=float),
        )
    )
    slope = float(np.polyfit(jd - jd[0], theta, 1)[0])
    return float(2.0 * np.pi / abs(slope))


def interpolate_vectors(
    jd: np.ndarray, vectors: np.ndarray, query_jd: np.ndarray
) -> np.ndarray:
    return np.column_stack(
        [np.interp(query_jd, jd, vectors[:, axis]) for axis in range(3)]
    )


def vector_angle_to_axis_deg(vectors: np.ndarray, unit_axis: np.ndarray) -> np.ndarray:
    numerator = vectors @ unit_axis
    denominator = np.linalg.norm(vectors, axis=1)
    return np.degrees(np.arccos(np.clip(numerator / denominator, -1.0, 1.0)))


def angle_deg(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    numerator = np.sum(a * b, axis=1)
    denominator = np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1)
    return np.degrees(np.arccos(np.clip(numerator / denominator, -1.0, 1.0)))


def describe(values: np.ndarray) -> dict[str, float]:
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


def evaluate_frame(
    frame: pd.DataFrame,
    period_days: float,
    frame_key: str,
    parent_speed: float,
    parent_unit: np.ndarray,
) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    jd = frame["jd_tdb"].to_numpy(dtype=float)
    child_velocity = frame[["vx_km_s", "vy_km_s", "vz_km_s"]].to_numpy(
        dtype=float
    )
    split_jd = float(frame.loc[frame["year"] >= SPLIT_YEAR, "jd_tdb"].iloc[0])
    opposite_jd = jd + period_days / 2.0
    eligible = (jd >= split_jd) & (opposite_jd <= jd[-1])
    jd1 = jd[eligible]
    v1 = child_velocity[eligible]
    v2 = interpolate_vectors(jd, child_velocity, opposite_jd[eligible])
    speed = np.linalg.norm(v1, axis=1)

    parent = parent_speed * parent_unit
    total1 = parent + v1
    total2 = parent + v2
    alpha1 = vector_angle_to_axis_deg(total1, parent_unit)
    alpha2 = vector_angle_to_axis_deg(total2, parent_unit)
    beta = angle_deg(total1, total2)
    alpha_sum = alpha1 + alpha2
    closure_residual = beta - alpha_sum
    ara_a = 2.0 * alpha1 / alpha_sum
    cycle_index = np.floor((jd1 - split_jd) / period_days).astype(int)
    years_since_split = (jd1 - split_jd) / 365.25

    series = pd.DataFrame(
        {
            "frame": frame_key,
            "jd_tdb": jd1,
            "years_since_1950": years_since_split,
            "cycle_index": cycle_index,
            "jupiter_speed_km_s": speed,
            "alpha_deg": alpha1,
            "alpha_opposite_deg": alpha2,
            "beta_deg": beta,
            "beta_half_deg": beta / 2.0,
            "closure_residual_deg": closure_residual,
            "ara_a": ara_a,
            "ara_b": 2.0 - ara_a,
        }
    )

    expected_rows = period_days / STEP_DAYS
    cycle_rows: list[dict[str, object]] = []
    for index, group in series.groupby("cycle_index"):
        complete = len(group) >= 0.8 * expected_rows
        if not complete:
            continue
        alpha_max = float(group["alpha_deg"].max())
        beta_max = float(group["beta_deg"].max())
        cycle_rows.append(
            {
                "frame": frame_key,
                "cycle_index": int(index),
                "n_samples": int(len(group)),
                "start_jd_tdb": float(group["jd_tdb"].min()),
                "stop_jd_tdb": float(group["jd_tdb"].max()),
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
    cycles = pd.DataFrame(cycle_rows)

    alpha_stats = describe(alpha1)
    beta_stats = describe(beta)
    central_pass = bool(
        abs(alpha_stats["median"] - ALPHA_TARGET_DEG) <= ALPHA_TOL_DEG
        and abs(beta_stats["median"] - BETA_TARGET_DEG) <= BETA_TOL_DEG
    )
    cycle_passes = int(
        (cycles["alpha_max_pass"] & cycles["beta_max_pass"]).sum()
    )
    envelope_pass = bool(
        not central_pass and len(cycles) >= 12 and cycle_passes >= 9
    )
    if central_pass:
        verdict = "CENTRAL CADENCE SUPPORTED"
    elif envelope_pass:
        verdict = "STABLE CREST/ENVELOPE RECURRENCE"
    else:
        verdict = "NOT SUPPORTED"

    scalar_angle = math.degrees(
        math.atan(float(np.median(speed)) / parent_speed)
    )
    result = {
        "label": FRAMES[frame_key]["label"],
        "parent_speed_km_s": float(parent_speed),
        "parent_unit_ecliptic_j2000": [float(x) for x in parent_unit],
        "n_pairs": int(len(series)),
        "median_jupiter_speed_km_s": float(np.median(speed)),
        "scalar_speed_ratio_alpha_deg": float(scalar_angle),
        "scalar_speed_ratio_beta_deg": float(2.0 * scalar_angle),
        "alpha_deg": alpha_stats,
        "alpha_opposite_deg": describe(alpha2),
        "beta_deg": beta_stats,
        "closure_residual_deg": describe(closure_residual),
        "ara_a": describe(ara_a),
        "fraction_alpha_within_target_tolerance": float(
            np.mean(np.abs(alpha1 - ALPHA_TARGET_DEG) <= ALPHA_TOL_DEG)
        ),
        "fraction_beta_within_target_tolerance": float(
            np.mean(np.abs(beta - BETA_TARGET_DEG) <= BETA_TOL_DEG)
        ),
        "central_pass": central_pass,
        "complete_cycle_count": int(len(cycles)),
        "envelope_cycle_pass_count": cycle_passes,
        "envelope_pass": envelope_pass,
        "verdict": verdict,
        "cycles": cycle_rows,
    }
    return result, series, cycles


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def draw_line_chart(
    draw: ImageDraw.ImageDraw,
    rect: tuple[int, int, int, int],
    x: np.ndarray,
    series: list[tuple[str, np.ndarray, str]],
    y_min: float,
    y_max: float,
    title: str,
    subtitle: str,
    references: list[tuple[float, str]],
) -> None:
    left, top, right, bottom = rect
    title_font = font(24, True)
    label_font = font(17)
    small_font = font(14)
    draw.text((left, top), title, fill="#172033", font=title_font)
    draw.text((left, top + 34), subtitle, fill="#657087", font=small_font)
    plot = (left + 70, top + 78, right - 24, bottom - 55)
    pl, pt, pr, pb = plot
    for tick in np.linspace(y_min, y_max, 5):
        py = pb - (tick - y_min) / (y_max - y_min) * (pb - pt)
        draw.line((pl, py, pr, py), fill="#dde2ea", width=1)
        draw.text((left, py - 9), f"{tick:.1f}°", fill="#657087", font=small_font)
    for value, colour in references:
        py = pb - (value - y_min) / (y_max - y_min) * (pb - pt)
        draw.line((pl, py, pr, py), fill=colour, width=2)
    x_min = float(np.min(x))
    x_max = float(np.max(x))
    for name, values, colour in series:
        points = []
        for xv, yv in zip(x, values):
            px = pl + (float(xv) - x_min) / (x_max - x_min) * (pr - pl)
            py = pb - (float(yv) - y_min) / (y_max - y_min) * (pb - pt)
            points.append((px, py))
        if len(points) > 1:
            draw.line(points, fill=colour, width=3)
    legend_x = pl
    for name, _, colour in series:
        draw.line((legend_x, bottom - 24, legend_x + 30, bottom - 24), fill=colour, width=4)
        draw.text((legend_x + 38, bottom - 34), name, fill="#172033", font=label_font)
        legend_x += 225
    draw.text((pl, pb + 16), f"{x_min:.0f}", fill="#657087", font=small_font)
    draw.text((pr - 45, pb + 16), f"{x_max:.0f}", fill="#657087", font=small_font)
    draw.text(((pl + pr) / 2 - 70, pb + 16), "years after 1950", fill="#657087", font=small_font)


def render_figure(
    results: dict,
    rounded_series: pd.DataFrame,
    modern_series: pd.DataFrame,
) -> None:
    width, height = 1800, 1120
    image = Image.new("RGB", (width, height), "#f7f8fb")
    draw = ImageDraw.Draw(image)
    draw.text((70, 38), "T318 — Jupiter–Sun Galactic-orbit 7.5/15 test", fill="#172033", font=font(38, True))
    draw.text(
        (70, 88),
        "Same T309 construction, Jupiter-system-barycentre relative to Sun; held-out evaluation from 1950",
        fill="#657087",
        font=font(19),
    )
    draw_line_chart(
        draw,
        (70, 145, 1730, 560),
        rounded_series["years_since_1950"].to_numpy(),
        [
            ("rounded α", rounded_series["alpha_deg"].to_numpy(), "#356fc4"),
            ("rounded β/2", rounded_series["beta_half_deg"].to_numpy(), "#d89b2b"),
        ],
        0.0,
        8.2,
        "Rounded T309 parent",
        "Branch α and directly measured opposite aperture β/2; dark line is the frozen 7.5° target",
        [(ALPHA_TARGET_DEG, "#222936")],
    )
    draw_line_chart(
        draw,
        (70, 590, 1730, 1005),
        modern_series["years_since_1950"].to_numpy(),
        [
            ("modern α", modern_series["alpha_deg"].to_numpy(), "#356fc4"),
            ("modern β/2", modern_series["beta_half_deg"].to_numpy(), "#d89b2b"),
        ],
        0.0,
        8.2,
        "Modern measured Galactocentric parent",
        "The scientific robustness control uses the same fixed target and scale",
        [(ALPHA_TARGET_DEG, "#222936")],
    )
    footer = (
        f"Rounded max α {results['frames']['rounded_t309']['alpha_deg']['max']:.3f}°, "
        f"max β {results['frames']['rounded_t309']['beta_deg']['max']:.3f}°  |  "
        f"Modern max α {results['frames']['modern_measured']['alpha_deg']['max']:.3f}°, "
        f"max β {results['frames']['modern_measured']['beta_deg']['max']:.3f}°"
    )
    draw.text((70, 1060), footer, fill="#172033", font=font(18, True))
    image.save(FIGURE_PATH)


def write_report(results: dict) -> None:
    rounded = results["frames"]["rounded_t309"]
    modern = results["frames"]["modern_measured"]
    verdict = results["robust_verdict"]
    text = f"""# T318 — Jupiter–Sun Galactic-Orbit 7.5/15 ARA Test

**Date:** 31 July 2026  
**Frozen protocol:** `T318_JUPITER_GALACTIC_ORBIT_7_5_15_PROTOCOL_v1_REGISTERED.md`  
**Robust verdict:** `{verdict}`

## Technical summary

Repeating T309 with Jupiter instead of Earth did **not** reproduce the
predeclared `7.5° : 15°` geometry. In the rounded T309 parent frame the
largest branch angle was `{rounded['alpha_deg']['max']:.4f}°` and the largest
opposite-branch aperture was `{rounded['beta_deg']['max']:.4f}°`. In the
modern measured Galactocentric frame they were
`{modern['alpha_deg']['max']:.4f}°` and
`{modern['beta_deg']['max']:.4f}°`.

The outcome is close to the speed-ratio expectation recorded before the
calculation: Jupiter’s smaller orbital speed produces a smaller angular
opening against the same Galactic translation. This makes the earlier
Earth `7.5 : 15` recurrence planet- and frame-dependent rather than a
universal Solar-System cadence.

## What was measured

JPL Horizons Sun and Jupiter-system-barycentre vectors share the same
five-day timestamps. Subtracting the Sun vector produced Jupiter’s
Sun-relative position and velocity. Data before 1950 estimated the orbital
period; data from 1950 onward were held out for the angle test.

The calibration-only period was
`{results['period_days_from_calibration']:.4f} days`
(`{results['period_years_from_calibration']:.6f} years`). The median held-out
Jupiter speed was `{modern['median_jupiter_speed_km_s']:.4f} km/s`.

## Frozen-target results

| Parent frame | median α | maximum α | median β | maximum β | scalar α | verdict |
|---|---:|---:|---:|---:|---:|---|
| Rounded T309 | {rounded['alpha_deg']['median']:.4f}° | {rounded['alpha_deg']['max']:.4f}° | {rounded['beta_deg']['median']:.4f}° | {rounded['beta_deg']['max']:.4f}° | {rounded['scalar_speed_ratio_alpha_deg']:.4f}° | {rounded['verdict']} |
| Modern measured | {modern['alpha_deg']['median']:.4f}° | {modern['alpha_deg']['max']:.4f}° | {modern['beta_deg']['median']:.4f}° | {modern['beta_deg']['max']:.4f}° | {modern['scalar_speed_ratio_alpha_deg']:.4f}° | {modern['verdict']} |

Neither the median gate nor the repeated cycle-envelope gate passed in
either frame. The rounded frame had
`{rounded['envelope_cycle_pass_count']}/{rounded['complete_cycle_count']}`
complete cycles passing both crest targets; the modern frame had
`{modern['envelope_cycle_pass_count']}/{modern['complete_cycle_count']}`.

## ARA interpretation

The ARA construction still gives a clean paired child around the parent
direction: the two half-orbit branches remain close to an ARA `1.0` balance
when normalized against each other, and the directly measured aperture is
close to their angular sum. What does **not** survive is the specific
`7.5° : 15°` size.

Plainly: Jupiter traces the same kind of child-on-parent geometry as Earth,
but its sphere opens by a smaller amount because its Sun-relative movement
is smaller beside the Galactic parent movement. The repeating relationship
is the branch/aperture construction; `7.5/15` is not a scale-free constant
of that construction.

## Limitations and robustness

- The Galactic vectors are treated as fixed over the 151-year evaluation
  interval, which is adequate for this local construction but is not a full
  Galactic orbit model.
- Linear interpolation is used at the calibration-derived half period.
- This test concerns the Jupiter-system barycentre, not the motion of
  Jupiter’s centre relative to its satellites.
- The ARA pair sum of two is forced by normalization and is not evidence.

## Recommended next step

Treat the result as a useful falsification of a planet-independent
`7.5 : 15` claim. If the broader ARA question is continued, the stronger
test is to predeclare the child/parent speed-ratio scaling law and evaluate
it across all planets, rather than continuing to search for the fixed
Earth-sized angle in each orbit.
"""
    REPORT_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    child = load_child()
    period_days = estimate_period_days(child)

    frame_results: dict[str, dict] = {}
    all_series: list[pd.DataFrame] = []
    all_cycles: list[pd.DataFrame] = []
    series_by_frame: dict[str, pd.DataFrame] = {}
    for key, spec in FRAMES.items():
        result, series, cycles = evaluate_frame(
            child,
            period_days,
            key,
            float(spec["speed_km_s"]),
            np.asarray(spec["unit"], dtype=float),
        )
        frame_results[key] = result
        all_series.append(series)
        all_cycles.append(cycles)
        series_by_frame[key] = series

    modern_support = (
        frame_results["modern_measured"]["central_pass"]
        or frame_results["modern_measured"]["envelope_pass"]
    )
    rounded_support = (
        frame_results["rounded_t309"]["central_pass"]
        or frame_results["rounded_t309"]["envelope_pass"]
    )
    if modern_support:
        robust_verdict = "ROBUST 7.5/15 SUPPORT"
    elif rounded_support:
        robust_verdict = "FRAME-SENSITIVE SUPPORT; NOT ROBUST"
    else:
        robust_verdict = "7.5/15 NOT SUPPORTED"

    results = {
        "test_id": "T318",
        "date": "2026-07-31",
        "status": "FROZEN HELD-OUT TEST",
        "question": (
            "Does the T309 7.5/15 geometry recur when Jupiter-system-"
            "barycentre relative to Sun replaces Earth relative to Sun?"
        ),
        "source": {
            "provider": "NASA/JPL Horizons",
            "center": "500@0 Solar-System barycentre",
            "sun_target": "10",
            "jupiter_system_target": "5",
            "step": "5d",
            "start": "1900-01-01",
            "stop": "2101-01-01",
            "sun_path": str(SUN_PATH.relative_to(HERE)),
            "jupiter_path": str(JUPITER_PATH.relative_to(HERE)),
            "sun_sha256": sha256(SUN_PATH),
            "jupiter_sha256": sha256(JUPITER_PATH),
            "protocol_sha256": sha256(PROTOCOL_PATH),
            "rows": int(len(child)),
        },
        "split": {
            "calibration": "1900-01-01 through 1949-12-31",
            "evaluation": "1950-01-01 onward",
        },
        "period_days_from_calibration": float(period_days),
        "period_years_from_calibration": float(period_days / 365.25),
        "targets": {
            "alpha_deg": ALPHA_TARGET_DEG,
            "alpha_tolerance_deg": ALPHA_TOL_DEG,
            "beta_deg": BETA_TARGET_DEG,
            "beta_tolerance_deg": BETA_TOL_DEG,
        },
        "frames": frame_results,
        "robust_verdict": robust_verdict,
        "forced_boundaries": [
            "x_A + x_B = 2 is forced by normalization",
            "the target 7.5/15 was inherited from T309 and was not blind",
            "the speed-ratio expectation was recorded before evaluation",
        ],
    }

    pd.concat(all_series, ignore_index=True).to_csv(SERIES_PATH, index=False)
    pd.concat(all_cycles, ignore_index=True).to_csv(CYCLE_PATH, index=False)
    RESULTS_PATH.write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    render_figure(
        results,
        series_by_frame["rounded_t309"],
        series_by_frame["modern_measured"],
    )
    write_report(results)
    print(json.dumps(
        {
            "test_id": "T318",
            "period_days": period_days,
            "robust_verdict": robust_verdict,
            "rounded": {
                "alpha_median": frame_results["rounded_t309"]["alpha_deg"]["median"],
                "alpha_max": frame_results["rounded_t309"]["alpha_deg"]["max"],
                "beta_median": frame_results["rounded_t309"]["beta_deg"]["median"],
                "beta_max": frame_results["rounded_t309"]["beta_deg"]["max"],
                "verdict": frame_results["rounded_t309"]["verdict"],
            },
            "modern": {
                "alpha_median": frame_results["modern_measured"]["alpha_deg"]["median"],
                "alpha_max": frame_results["modern_measured"]["alpha_deg"]["max"],
                "beta_median": frame_results["modern_measured"]["beta_deg"]["median"],
                "beta_max": frame_results["modern_measured"]["beta_deg"]["max"],
                "verdict": frame_results["modern_measured"]["verdict"],
            },
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()
