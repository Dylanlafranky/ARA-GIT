#!/usr/bin/env python3
"""T354: test whether an Irrationality handover retains a fixed parent ridge."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import matplotlib

HERE = Path(__file__).resolve().parent
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from t352_irrationality_di_ara_dusk_band import address_openness, stochastic_residual


PREFIX = "T354_IRRATIONALITY_PARENT_RIDGE_CENTRE"
PROTOCOL = HERE / f"{PREFIX}_PROTOCOL_v1_FROZEN.md"
LENGTH = 4096
WINDOWS = (128, 256, 384, 512)
STRIDE = 32
Q_VALUES = (13, 17, 23)
D_VALUES = (43, 47, 53)
DURATIONS = (256, 448, 640)
REPLICATES = 6
BOOTSTRAPS = 5000
SEED = 35420260811


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest().upper()


def stable_seed(*parts: object) -> int:
    payload = "|".join(map(str, (SEED,) + parts)).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "little")


def coprime_numerator(q: int, replicate: int) -> int:
    values = [p for p in range(1, q) if math.gcd(p, q) == 1]
    return values[(replicate * 2 + 1) % len(values)]


def centre_values() -> np.ndarray:
    count = len(Q_VALUES) * len(DURATIONS) * REPLICATES
    return np.rint(np.linspace(1408, 2688, count)).astype(int)


def identity_centre(pair_index: int, duration_index: int, replicate: int) -> int:
    index = (pair_index * len(DURATIONS) + duration_index) * REPLICATES + replicate
    return int(centre_values()[index])


def make_path(
    q: int,
    d: int,
    duration: int,
    replicate: int,
    direction: str,
    mode: str,
    centre: int,
) -> tuple[np.ndarray, int, int, float, float]:
    rational = coprime_numerator(q, replicate) / q
    irrational = math.sqrt(d) - math.floor(math.sqrt(d))
    source, target = (
        (irrational, rational)
        if direction == "irrational_to_rational"
        else (rational, irrational)
    )
    start = centre - duration // 2
    end = start + duration
    advances = np.full(LENGTH - 1, source, dtype=float)
    if mode == "ordered":
        advances[start:end] = np.linspace(source, target, duration, endpoint=False)
        advances[end:] = target
    elif mode == "abrupt":
        advances[centre:] = target
    else:
        raise ValueError(mode)
    rng = np.random.default_rng(
        stable_seed("phase", q, d, duration, replicate, direction)
    )
    phase = float(rng.random())
    path = np.empty(LENGTH, dtype=float)
    path[0] = phase
    path[1:] = (phase + np.cumsum(advances)) % 1.0
    return path, start, end, source, target


def contiguous_runs(mask: np.ndarray) -> list[tuple[int, int]]:
    indices = np.flatnonzero(mask)
    if not len(indices):
        return []
    breaks = np.flatnonzero(np.diff(indices) > 1)
    starts = np.r_[0, breaks + 1]
    ends = np.r_[breaks, len(indices) - 1]
    return [(int(indices[s]), int(indices[e])) for s, e in zip(starts, ends)]


def interpolate_crossing(centres: np.ndarray, r_p: np.ndarray, left: int, right: int) -> float:
    candidates: list[float] = []
    for index in range(left, right):
        y0 = float(r_p[index] - 1.0)
        y1 = float(r_p[index + 1] - 1.0)
        if y0 == 0:
            candidates.append(float(centres[index]))
        elif y0 * y1 <= 0 and y1 != y0:
            fraction = -y0 / (y1 - y0)
            candidates.append(float(centres[index] + fraction * (centres[index + 1] - centres[index])))
    if candidates:
        return float(candidates[0])
    local = np.arange(left, right + 1)
    nearest = int(local[np.argmin(np.abs(r_p[local] - 1.0))])
    return float(centres[nearest])


def estimate_ridge(path: np.ndarray, window: int) -> tuple[dict[str, float | bool], pd.DataFrame]:
    starts = np.arange(0, LENGTH - window + 1, STRIDE, dtype=int)
    centres = starts + window // 2
    x_p = np.asarray([address_openness(path[s : s + window])[0] for s in starts], dtype=float)
    first = float(np.median(x_p[centres <= LENGTH // 4]))
    last = float(np.median(x_p[centres >= 3 * LENGTH // 4]))
    separation = abs(last - first)
    if separation <= 1e-12:
        frame = pd.DataFrame({"start": starts, "center": centres, "x_p": x_p, "r_p": np.nan})
        return {
            "predicted": False,
            "first_x_p": first,
            "last_x_p": last,
            "endpoint_separation": separation,
            "ridge_level_x_p": (first + last) / 2.0,
            "predicted_ridge": np.nan,
            "transition_width": np.nan,
            "x_r_peak_center": np.nan,
            "x_r_peak": np.nan,
        }, frame

    r_p = 2.0 * (x_p - first) / (last - first)
    runs = contiguous_runs((r_p >= 0.5) & (r_p <= 1.5))
    if not runs:
        nearest = int(np.argmin(np.abs(r_p - 1.0)))
        run = (nearest, nearest)
    else:
        run = max(runs, key=lambda item: (item[1] - item[0] + 1, -item[0]))
    left, right = run
    predicted_ridge = interpolate_crossing(centres, r_p, left, right)
    transition_width = float(centres[right] - centres[left] + STRIDE)

    x_r = np.full(len(starts), np.nan, dtype=float)
    local_radius = max(window, 256)
    local_indices = np.flatnonzero(np.abs(centres - predicted_ridge) <= local_radius)
    for index in local_indices:
        x_r[index] = stochastic_residual(path[starts[index] : starts[index] + window])[0]
    if len(local_indices):
        peak_index = int(local_indices[np.nanargmax(x_r[local_indices])])
        x_r_peak_center = float(centres[peak_index])
        x_r_peak = float(x_r[peak_index])
    else:
        x_r_peak_center = np.nan
        x_r_peak = np.nan

    frame = pd.DataFrame(
        {"start": starts, "center": centres, "x_p": x_p, "r_p": r_p, "x_r": x_r}
    )
    return {
        "predicted": True,
        "first_x_p": first,
        "last_x_p": last,
        "endpoint_separation": separation,
        "ridge_level_x_p": (first + last) / 2.0,
        "predicted_ridge": predicted_ridge,
        "transition_width": transition_width,
        "x_r_peak_center": x_r_peak_center,
        "x_r_peak": x_r_peak,
    }, frame


def bootstrap_median(values: np.ndarray, offset: int) -> dict[str, float | int]:
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(SEED + offset)
    draws = rng.integers(0, len(values), size=(BOOTSTRAPS, len(values)))
    sampled = np.median(values[draws], axis=1)
    return {
        "estimate": float(np.median(values)),
        "ci_low": float(np.quantile(sampled, 0.025)),
        "ci_high": float(np.quantile(sampled, 0.975)),
        "n": int(len(values)),
    }


def bootstrap_matched_difference(wrong: np.ndarray, true: np.ndarray, offset: int) -> dict[str, float | int]:
    wrong = np.asarray(wrong, dtype=float)
    true = np.asarray(true, dtype=float)
    delta = wrong - true
    return bootstrap_median(delta, offset)


def build_wrong_time_control(identities: pd.DataFrame) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    for (_, _), group in identities.groupby(["direction", "mode"], sort=True):
        part = group.sort_values(["true_center", "path_id"]).copy()
        shift = max(1, len(part) // 2)
        part["wrong_center"] = np.roll(part["true_center"].to_numpy(float), shift)
        part["wrong_abs_error"] = np.abs(part["predicted_ridge_median"] - part["wrong_center"])
        rows.append(part)
    return pd.concat(rows, ignore_index=True)


def make_figure(series: pd.DataFrame, identities: pd.DataFrame, controls: pd.DataFrame, gates: pd.DataFrame, output: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=True)
    colors = {"ordered": "#2F6FB0", "abrupt": "#D49A2E"}
    markers = {"irrational_to_rational": "o", "rational_to_irrational": "s"}

    ax = axes[0, 0]
    for direction in markers:
        for mode in colors:
            part = series[(series.direction == direction) & (series["mode"] == mode)]
            curve = part.groupby("window", as_index=False).agg(
                width=("transition_width", "median"), error=("signed_error", "median")
            )
            ax.plot(
                curve.window,
                curve.width,
                marker=markers[direction],
                linestyle="-" if mode == "ordered" else "--",
                color=colors[mode],
                label=f"{mode}, {direction.replace('_to_', ' to ')}",
            )
    ax.set(
        xlabel="observation window W (states)",
        ylabel="visible 0.5 to 1.5 width (states)",
        title="The handover broadens as the observer widens",
    )
    ax.legend(frameon=False, fontsize=8)

    ax = axes[0, 1]
    plot = series[series.window.isin([128, 512])]
    for window, alpha in ((128, 0.55), (512, 0.9)):
        part = plot[plot.window == window]
        ax.scatter(part.true_center, part.predicted_ridge, s=20, alpha=alpha, label=f"W={window}")
    limits = (1320, 2780)
    ax.plot(limits, limits, color="#7A8490", lw=1, linestyle=":")
    ax.set(
        xlim=limits,
        ylim=limits,
        xlabel="hidden referee centre (states)",
        ylabel="predicted parent ridge (states)",
        title="Blind ridge predictions against the revealed centre",
    )
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 0]
    for direction, marker in markers.items():
        for mode, color in colors.items():
            part = series[(series.direction == direction) & (series["mode"] == mode)]
            curve = part.groupby("window", as_index=False).signed_error.median()
            ax.plot(
                curve.window,
                curve.signed_error,
                marker=marker,
                linestyle="-" if mode == "ordered" else "--",
                color=color,
                label=f"{mode}, {direction.replace('_to_', ' to ')}",
            )
    ax.axhline(0, color="#7A8490", lw=1)
    ax.set(
        xlabel="observation window W (states)",
        ylabel="median ridge-centre error (states)",
        title="Does the centre drift when the window changes?",
    )

    ax = axes[1, 1]
    labels = []
    true_values = []
    wrong_values = []
    for direction in markers:
        for mode in colors:
            part = controls[(controls.direction == direction) & (controls["mode"] == mode)]
            labels.append(f"{mode}\n{direction.split('_to_')[0][:3]} to {direction.split('_to_')[1][:3]}")
            true_values.append(float(part.abs_error_median.median()))
            wrong_values.append(float(part.wrong_abs_error.median()))
    x = np.arange(len(labels))
    ax.bar(x - 0.18, true_values, width=0.36, color="#2F6FB0", label="true time")
    ax.bar(x + 0.18, wrong_values, width=0.36, color="#AAB2BC", label="wrong time")
    ax.set_xticks(x, labels)
    ax.set(ylabel="median absolute error (states)", title="Specificity: true versus permuted event times")
    ax.legend(frameon=False, fontsize=8)

    passed = int(gates.passed.sum())
    verdict = str(gates.attrs.get("verdict", ""))
    fig.suptitle(f"T354 - Irrationality parent-ridge centre invariance | {passed}/6 gates | {verdict}", fontsize=16, fontweight="bold")
    fig.savefig(output, dpi=170)
    plt.close(fig)


def main() -> None:
    series_rows: list[dict] = []
    profile_rows: list[dict] = []
    for pair_index, (q, d) in enumerate(zip(Q_VALUES, D_VALUES)):
        for duration_index, duration in enumerate(DURATIONS):
            for replicate in range(REPLICATES):
                true_center = identity_centre(pair_index, duration_index, replicate)
                for direction in ("irrational_to_rational", "rational_to_irrational"):
                    path_id = f"q{q}:d{d}:t{duration}:r{replicate}:{direction}"
                    for mode in ("ordered", "abrupt"):
                        path, ramp_start, ramp_end, source, target = make_path(
                            q, d, duration, replicate, direction, mode, true_center
                        )
                        for window in WINDOWS:
                            summary, profile = estimate_ridge(path, window)
                            predicted = float(summary["predicted_ridge"])
                            row = {
                                "path_id": path_id,
                                "q": q,
                                "d": d,
                                "duration": duration,
                                "replicate": replicate,
                                "direction": direction,
                                "mode": mode,
                                "window": window,
                                "true_center": true_center,
                                "ramp_start": ramp_start,
                                "ramp_end": ramp_end,
                                "source_advance": source,
                                "target_advance": target,
                                **summary,
                                "signed_error": predicted - true_center if np.isfinite(predicted) else np.nan,
                                "abs_error": abs(predicted - true_center) if np.isfinite(predicted) else np.nan,
                            }
                            series_rows.append(row)
                            profile = profile.copy()
                            for key in (
                                "path_id",
                                "q",
                                "d",
                                "duration",
                                "replicate",
                                "direction",
                                "mode",
                                "window",
                                "true_center",
                            ):
                                profile[key] = row[key]
                            profile_rows.extend(profile.to_dict("records"))

    series = pd.DataFrame(series_rows)
    profiles = pd.DataFrame(profile_rows)
    identity_rows: list[dict] = []
    for (path_id, direction, mode), group in series.groupby(["path_id", "direction", "mode"]):
        predicted = group.predicted_ridge.dropna().to_numpy(float)
        true_center = float(group.true_center.iloc[0])
        identity_rows.append(
            {
                "path_id": path_id,
                "direction": direction,
                "mode": mode,
                "true_center": true_center,
                "prediction_rate": float(group.predicted.mean()),
                "predicted_ridge_median": float(np.median(predicted)) if len(predicted) else np.nan,
                "signed_error_median": float(np.median(predicted) - true_center) if len(predicted) else np.nan,
                "abs_error_median": abs(float(np.median(predicted) - true_center)) if len(predicted) else np.nan,
                "centre_range": float(np.max(predicted) - np.min(predicted)) if len(predicted) else np.nan,
                "endpoint_separation_median": float(group.endpoint_separation.median()),
                "x_r_peak_offset_median": float(np.nanmedian(group.x_r_peak_center - group.predicted_ridge)),
            }
        )
    identities = pd.DataFrame(identity_rows)
    controls = build_wrong_time_control(identities)

    gate_rows: list[dict] = []
    grouped_separation = series.groupby(["direction", "mode", "window"]).endpoint_separation.median()
    prediction_rate = float(series.predicted.mean())
    r1 = bool(grouped_separation.min() >= 0.75 and prediction_rate >= 0.95)
    gate_rows.append(
        {
            "gate": "R1 endpoint separation",
            "passed": r1,
            "value": f"minimum grouped median={grouped_separation.min():.6f}; prediction rate={prediction_rate:.4f}",
        }
    )

    r2_details = {}
    r2 = True
    r3_details = {}
    r3 = True
    offset = 0
    for direction in ("irrational_to_rational", "rational_to_irrational"):
        for mode in ("ordered", "abrupt"):
            part = identities[(identities.direction == direction) & (identities["mode"] == mode)]
            loc = bootstrap_median(part.abs_error_median.to_numpy(float), 100 + offset)
            inv = bootstrap_median(part.centre_range.to_numpy(float), 200 + offset)
            key = f"{direction}:{mode}"
            r2_details[key] = loc
            r3_details[key] = inv
            r2 = r2 and loc["estimate"] <= 64 and loc["ci_high"] <= 128
            r3 = r3 and inv["estimate"] <= 64 and inv["ci_high"] <= 128
            offset += 1
    gate_rows.append({"gate": "R2 known-centre localization", "passed": bool(r2), "value": json.dumps(r2_details)})
    gate_rows.append({"gate": "R3 window invariance", "passed": bool(r3), "value": json.dumps(r3_details)})

    signed = {}
    for direction in ("irrational_to_rational", "rational_to_irrational"):
        part = identities[(identities.direction == direction) & (identities["mode"] == "ordered")]
        signed[direction] = float(part.signed_error_median.median())
    r4 = abs(signed["irrational_to_rational"] - signed["rational_to_irrational"]) <= 32 and all(abs(v) <= 32 for v in signed.values())
    gate_rows.append({"gate": "R4 directional complement", "passed": bool(r4), "value": json.dumps(signed)})

    r5_details = {}
    r5 = True
    for direction in ("irrational_to_rational", "rational_to_irrational"):
        for mode in ("ordered", "abrupt"):
            part = series[(series.direction == direction) & (series["mode"] == mode)]
            curve = part.groupby("window", as_index=False).agg(
                width=("transition_width", "median"), error=("signed_error", "median")
            )
            nondecreasing = bool(np.all(np.diff(curve.width.to_numpy(float)) >= -1e-9))
            slope = float(np.polyfit(curve.window.to_numpy(float), curve.error.to_numpy(float), 1)[0])
            key = f"{direction}:{mode}"
            r5_details[key] = {"widths": curve.width.to_list(), "centre_error_slope": slope}
            r5 = r5 and nondecreasing and abs(slope) <= 0.10
    gate_rows.append({"gate": "R5 broadening without centre drift", "passed": bool(r5), "value": json.dumps(r5_details)})

    r6_details = {}
    r6 = True
    offset = 0
    for direction in ("irrational_to_rational", "rational_to_irrational"):
        for mode in ("ordered", "abrupt"):
            part = controls[(controls.direction == direction) & (controls["mode"] == mode)]
            true_error = part.abs_error_median.to_numpy(float)
            wrong_error = part.wrong_abs_error.to_numpy(float)
            diff = bootstrap_matched_difference(wrong_error, true_error, 400 + offset)
            true_median = float(np.median(true_error))
            wrong_median = float(np.median(wrong_error))
            key = f"{direction}:{mode}"
            r6_details[key] = {"true_median": true_median, "wrong_median": wrong_median, "difference": diff}
            r6 = r6 and true_median <= 0.25 * wrong_median and diff["ci_low"] > 0
            offset += 1
    gate_rows.append({"gate": "R6 wrong-time control", "passed": bool(r6), "value": json.dumps(r6_details)})

    gates = pd.DataFrame(gate_rows)
    passed = int(gates.passed.sum())
    if passed == 6:
        verdict = "SUPPORTED [SYNTHETIC PARENT-RIDGE INSTRUMENT ONLY]"
    elif r1 and (not r2 or not r3):
        verdict = "RIDGE NOT RESOLVED"
    elif all(gates.iloc[:5].passed) and not r6:
        verdict = "ALIGNMENT NOT SPECIFIC"
    else:
        verdict = "NOT SUPPORTED"
    gates.attrs["verdict"] = verdict

    series.to_csv(HERE / f"{PREFIX}_SERIES.csv", index=False)
    profiles.to_csv(HERE / f"{PREFIX}_PROFILES.csv", index=False)
    identities.to_csv(HERE / f"{PREFIX}_IDENTITIES.csv", index=False)
    controls.to_csv(HERE / f"{PREFIX}_WRONG_TIME_CONTROLS.csv", index=False)
    gates.to_csv(HERE / f"{PREFIX}_FROZEN_GATES.csv", index=False)

    results = {
        "test": "T354",
        "run_date": "2026-08-11",
        "protocol_sha256": digest(PROTOCOL),
        "verdict": verdict,
        "passed_gates": passed,
        "total_gates": 6,
        "series_rows": int(len(series)),
        "profile_rows": int(len(profiles)),
        "identity_rows": int(len(identities)),
        "r2_localization": r2_details,
        "r3_window_invariance": r3_details,
        "r4_directional_complement": signed,
        "r5_broadening": r5_details,
        "r6_wrong_time": r6_details,
    }
    (HERE / f"{PREFIX}_RESULTS.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    make_figure(series, identities, controls, gates, HERE / f"{PREFIX}_FIGURE.png")

    report = [
        "# T354 - Irrationality parent-ridge centre invariance",
        "",
        "**Run date:** 11 August 2026  ",
        "**Evidence boundary:** synthetic known-referee instrument calibration  ",
        f"**Verdict:** **{verdict}**  ",
        f"**Frozen gates:** **{passed}/6 passed**",
        "",
        "## Answer first",
        "",
        "T354 varied observer width while hiding identity-specific transition times from the estimator. The primary question was whether the midpoint between the two stable Irrationality endpoint coordinates stays fixed even when its visible transition run broadens.",
        "",
        "## Headline localization",
        "",
        "| direction | mode | median absolute error | median window range |",
        "|---|---|---:|---:|",
    ]
    for direction in ("irrational_to_rational", "rational_to_irrational"):
        for mode in ("ordered", "abrupt"):
            key = f"{direction}:{mode}"
            report.append(
                f"| {direction.replace('_to_', ' to ')} | {mode} | {r2_details[key]['estimate']:.3f} [{r2_details[key]['ci_low']:.3f}, {r2_details[key]['ci_high']:.3f}] | {r3_details[key]['estimate']:.3f} [{r3_details[key]['ci_low']:.3f}, {r3_details[key]['ci_high']:.3f}] |"
            )
    report.extend(
        [
            "",
            "## Frozen gates",
            "",
            "| gate | result | headline |",
            "|---|---|---|",
        ]
    )
    for row in gates.itertuples():
        report.append(f"| {row.gate} | {'PASS' if row.passed else 'FAIL'} | `{str(row.value)[:180]}` |")
    report.extend(
        [
            "",
            f"![T354 parent-ridge centre]({PREFIX}_FIGURE.png)",
            "",
            "## Interpretation boundary",
            "",
            "A pass supports only a stable parent midpoint in the existing synthetic Irrationality coordinate. It does not identify an Irrationality dusk/dawn child pair or prove that a physical transition uses this geometry.",
            "",
            "## Artifacts",
            "",
            f"- `{PREFIX}_SERIES.csv`",
            f"- `{PREFIX}_PROFILES.csv`",
            f"- `{PREFIX}_IDENTITIES.csv`",
            f"- `{PREFIX}_WRONG_TIME_CONTROLS.csv`",
            f"- `{PREFIX}_FROZEN_GATES.csv`",
            f"- `{PREFIX}_RESULTS.json`",
            f"- `{PREFIX}_FIGURE.png`",
            "- `t354_irrationality_parent_ridge_centre.py`",
        ]
    )
    (HERE / f"{PREFIX}_REPORT_2026-08-11.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": verdict, "gates": f"{passed}/6", "series": len(series), "profiles": len(profiles)}, indent=2))


if __name__ == "__main__":
    main()
