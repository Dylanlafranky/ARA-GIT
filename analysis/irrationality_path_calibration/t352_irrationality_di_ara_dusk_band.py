#!/usr/bin/env python3
"""T352: known-referee Irrationality Di-ARA dusk-band calibration."""

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


PREFIX = "T352_IRRATIONALITY_DI_ARA_DUSK_BAND"
PROTOCOL = HERE / f"{PREFIX}_PROTOCOL_v1_FROZEN.md"
LENGTH = 3072
CENTER = LENGTH // 2
WINDOW = 512
STRIDE = 64
RESOLUTIONS = np.asarray([16, 32, 64, 128, 256], dtype=float)
K_NEIGHBOURS = 8
MAX_LAG = 128
BOOTSTRAPS = 5000
SEED = 35220260811

SPECS = {
    "calibration": {
        "q": (5, 7, 9),
        "d": (2, 3, 5),
        "duration": (256, 512),
        "replicates": 12,
    },
    "holdout": {
        "q": (6, 10, 14),
        "d": (13, 17, 23),
        "duration": (384, 640),
        "replicates": 16,
    },
}


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
    candidates = [p for p in range(1, q) if math.gcd(p, q) == 1]
    return candidates[replicate % len(candidates)]


def make_path(
    split: str,
    q: int,
    d: int,
    duration: int,
    replicate: int,
    direction: str,
    mode: str,
) -> tuple[np.ndarray, int, int, float, float]:
    rational = coprime_numerator(q, replicate) / q
    irrational = math.sqrt(d) - math.floor(math.sqrt(d))
    if direction == "irrational_to_rational":
        source, target = irrational, rational
    else:
        source, target = rational, irrational

    ramp_start = CENTER - duration // 2
    ramp_end = ramp_start + duration
    advances = np.full(LENGTH - 1, source, dtype=float)
    advances[ramp_end:] = target

    if mode in ("ordered", "shuffled"):
        transition = np.linspace(source, target, duration, endpoint=False, dtype=float)
        if mode == "shuffled":
            rng = np.random.default_rng(
                stable_seed("shuffle", split, q, d, duration, replicate, direction)
            )
            transition = transition[rng.permutation(duration)]
        advances[ramp_start:ramp_end] = transition
    elif mode == "abrupt":
        advances[CENTER:] = target
    else:
        raise ValueError(mode)

    rng = np.random.default_rng(stable_seed("phase", split, q, d, duration, replicate, direction))
    phase = float(rng.random())
    path = np.empty(LENGTH, dtype=float)
    path[0] = phase
    path[1:] = (phase + np.cumsum(advances)) % 1.0
    return path, ramp_start, ramp_end, source, target


def address_openness(z: np.ndarray) -> tuple[float, list[int]]:
    occupied: list[int] = []
    for bins_float in RESOLUTIONS:
        bins = int(bins_float)
        idx = np.minimum((z * bins).astype(int), bins - 1)
        occupied.append(int(np.unique(idx).size))
    beta = float(np.polyfit(np.log(RESOLUTIONS), np.log(occupied), 1)[0])
    return 2.0 * float(np.clip(beta, 0.0, 1.0)), occupied


def circular_mean(values: np.ndarray) -> float:
    vector = np.mean(np.exp(2j * np.pi * values))
    if abs(vector) < 1e-15:
        return 0.0
    return float((np.angle(vector) / (2.0 * np.pi)) % 1.0)


def circular_loss(actual: np.ndarray, predicted: np.ndarray) -> np.ndarray:
    return 1.0 - np.cos(2.0 * np.pi * (actual - predicted))


def knn_predict(train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray) -> np.ndarray:
    order = np.argsort(train_x)
    sx = train_x[order]
    sy = train_y[order]
    n = len(sx)
    insertion = np.searchsorted(sx, test_x)
    radius = max(K_NEIGHBOURS + 2, 7)
    offsets = np.arange(-radius, radius + 1)
    candidate_idx = (insertion[:, None] + offsets[None, :]) % n
    candidate_x = sx[candidate_idx]
    distance = np.abs(candidate_x - test_x[:, None])
    distance = np.minimum(distance, 1.0 - distance)
    nearest_pos = np.argpartition(distance, kth=K_NEIGHBOURS - 1, axis=1)[:, :K_NEIGHBOURS]
    nearest_idx = np.take_along_axis(candidate_idx, nearest_pos, axis=1)
    neighbour_y = sy[nearest_idx]
    mean_vector = np.mean(np.exp(2j * np.pi * neighbour_y), axis=1)
    prediction = (np.angle(mean_vector) / (2.0 * np.pi)) % 1.0
    prediction[np.abs(mean_vector) < 1e-12] = circular_mean(train_y)
    return prediction


def stochastic_residual(z: np.ndarray) -> tuple[float, float, float]:
    split = len(z) // 2
    train_x = z[: split - 1]
    train_y = z[1:split]
    test_x = z[split:-1]
    test_y = z[split + 1 :]
    prediction = knn_predict(train_x, train_y, test_x)
    null_prediction = np.full_like(test_y, circular_mean(train_y))
    local = float(np.mean(circular_loss(test_y, prediction)))
    null = float(np.mean(circular_loss(test_y, null_prediction)))
    return 2.0 * min(1.0, local / max(null, 1e-12)), local, null


def closure_history(z: np.ndarray) -> tuple[float, float, bool]:
    n = len(z)
    max_lag = min(MAX_LAG, n // 4)
    unit = np.exp(2j * np.pi * z)
    nfft = 1 << (2 * n - 1).bit_length()
    spectrum = np.fft.fft(unit, nfft)
    raw = np.fft.ifft(spectrum * np.conj(spectrum))[: max_lag + 1]
    raw = raw / np.arange(n, n - max_lag - 1, -1)
    relation = raw[1:]
    rho = np.abs(relation)
    distance = np.abs(np.angle(relation)) / np.pi
    coherent = rho > 0.90
    misses = distance[coherent & (distance > 1e-12)]
    best_miss = float(np.min(misses)) if len(misses) else 0.0
    exact = bool(np.any((rho > 1.0 - 1e-10) & (distance < 1e-12)))
    return float(np.mean(rho)), best_miss, exact


def measure(z: np.ndarray) -> dict[str, float | int | bool]:
    x_p, occupied = address_openness(z)
    x_r, local, null = stochastic_residual(z)
    mean_rho, best_miss, exact = closure_history(z)
    return {
        "x_p": x_p,
        "x_r": x_r,
        "local_loss": local,
        "null_loss": null,
        "mean_rho": mean_rho,
        "best_coherent_miss": best_miss,
        "exact_closure": exact,
        **{f"occupied_{int(b)}": n for b, n in zip(RESOLUTIONS, occupied)},
    }


def region(window_start: int, window_end: int, ramp_start: int, ramp_end: int) -> str:
    if window_end <= ramp_start:
        return "pre"
    if window_start >= ramp_end:
        return "post"
    return "handover"


def path_id(split: str, q: int, d: int, duration: int, replicate: int, direction: str) -> str:
    return f"{split}:q{q}:d{d}:w{duration}:r{replicate}:{direction}"


def summarize_path(rows: pd.DataFrame, metadata: dict) -> dict:
    pre = rows[rows["region"] == "pre"]
    post = rows[rows["region"] == "post"]
    hand = rows[rows["region"] == "handover"].sort_values("center")
    pre_xp = float(pre["x_p"].median())
    post_xp = float(post["x_p"].median())
    pre_xr = float(pre["x_r"].median())
    post_xr = float(post["x_r"].median())
    baseline = max(pre_xr, post_xr)
    excursion = float(hand["x_r"].max() - baseline)
    excess_area = float(np.maximum(hand["x_r"].to_numpy() - baseline, 0.0).mean())
    band_width = int(np.sum(hand["x_r"].to_numpy() >= baseline + 0.25) * STRIDE)
    coords = hand[["x_p", "x_r"]].to_numpy(dtype=float)
    roughness = float(np.linalg.norm(np.diff(coords, axis=0), axis=1).mean()) if len(coords) > 1 else 0.0
    final_post_error = abs(float(post.iloc[-1]["x_r"]) - post_xr)
    return {
        **metadata,
        "n_pre": len(pre),
        "n_handover": len(hand),
        "n_post": len(post),
        "pre_x_p": pre_xp,
        "post_x_p": post_xp,
        "pre_x_r": pre_xr,
        "post_x_r": post_xr,
        "baseline_x_r": baseline,
        "excursion_x_r": excursion,
        "excess_area_x_r": excess_area,
        "band_width_states": band_width,
        "coordinate_roughness": roughness,
        "final_post_error_x_r": final_post_error,
    }


def bootstrap_median(values: np.ndarray, offset: int) -> dict[str, float]:
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(SEED + offset)
    draws = rng.integers(0, len(values), size=(BOOTSTRAPS, len(values)))
    samples = np.median(values[draws], axis=1)
    return {
        "estimate": float(np.median(values)),
        "ci_low": float(np.quantile(samples, 0.025)),
        "ci_high": float(np.quantile(samples, 0.975)),
        "n": int(len(values)),
    }


def matched_difference(events: pd.DataFrame, left: str, right: str, field: str) -> np.ndarray:
    pivot = events.pivot(index="path_id", columns="mode", values=field)
    return (pivot[left] - pivot[right]).dropna().to_numpy(dtype=float)


def write_figure(windows: pd.DataFrame, events: pd.DataFrame, gates: pd.DataFrame, output: Path) -> None:
    hold_w = windows[(windows["split"] == "holdout") & (windows["mode"] == "ordered")]
    hold_e = events[events["split"] == "holdout"]
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=True)
    colors = {"irrational_to_rational": "#2F6FB0", "rational_to_irrational": "#D49A2E"}

    ax = axes[0, 0]
    for direction in colors:
        part = hold_w[hold_w["direction"] == direction].copy()
        part["rel"] = (part["center"] - CENTER) / part["duration"]
        part["rel_bin"] = (part["rel"] * 4).round() / 4
        curve = part.groupby("rel_bin", as_index=False)[["x_p", "x_r"]].median()
        ax.plot(curve["x_p"], curve["x_r"], marker="o", ms=3, lw=2, color=colors[direction], label=direction.replace("_", " "))
        if len(curve):
            ax.scatter(curve.iloc[0]["x_p"], curve.iloc[0]["x_r"], s=90, facecolors="none", edgecolors=colors[direction], lw=2)
            ax.scatter(curve.iloc[-1]["x_p"], curve.iloc[-1]["x_r"], s=70, marker="X", color=colors[direction])
    ax.axvline(1, color="#7A8490", lw=1)
    ax.axhline(1, color="#7A8490", lw=1)
    ax.set(xlim=(0, 2.05), ylim=(0, 2.05), xlabel="address openness x_P", ylabel="stochastic residual x_R", title="Ordered handover through the Irrationality Di-ARA")
    ax.legend(frameon=False, fontsize=9)

    ax = axes[0, 1]
    styles = {"ordered": ("#2F6FB0", "-"), "abrupt": ("#D49A2E", "--"), "shuffled": ("#C45A86", ":")}
    for mode, (color, style) in styles.items():
        part = windows[(windows["split"] == "holdout") & (windows["direction"] == "irrational_to_rational") & (windows["mode"] == mode)].copy()
        part["rel"] = (part["center"] - CENTER) / part["duration"]
        part["rel_bin"] = (part["rel"] * 4).round() / 4
        curve = part.groupby("rel_bin", as_index=False)["x_r"].median()
        ax.plot(curve["rel_bin"], curve["x_r"], style, lw=2, color=color, label=mode)
    ax.axhline(1, color="#7A8490", lw=1)
    ax.axvline(0, color="#7A8490", lw=1)
    ax.set(xlabel="transition-relative time (transition durations)", ylabel="x_R", title="Ordered band versus abrupt smear and destroyed order")
    ax.legend(frameon=False)

    ax = axes[1, 0]
    positions = np.arange(2)
    labels = []
    values = []
    lows = []
    highs = []
    for index, direction in enumerate(colors):
        group = hold_e[hold_e["direction"] == direction]
        diff = matched_difference(group, "ordered", "abrupt", "excess_area_x_r")
        record = bootstrap_median(diff, 700 + index)
        labels.append(direction.replace("_to_", " → ").replace("_", " "))
        values.append(record["estimate"])
        lows.append(record["estimate"] - record["ci_low"])
        highs.append(record["ci_high"] - record["estimate"])
    ax.bar(positions, values, color=[colors[x] for x in colors], alpha=0.85)
    ax.errorbar(positions, values, yerr=[lows, highs], fmt="none", ecolor="#263442", capsize=5)
    ax.axhline(0, color="#263442", lw=1)
    ax.set_xticks(positions, labels, rotation=12, ha="right")
    ax.set(ylabel="ordered − abrupt excess area", title="Does ordered handover exceed window smear?")

    ax = axes[1, 1]
    ax.axis("off")
    table_rows = [[row["gate"], "PASS" if row["passed"] else "FAIL", row["value"]] for _, row in gates.iterrows()]
    table = ax.table(cellText=table_rows, colLabels=["Frozen gate", "Result", "value"], loc="center", cellLoc="left", colWidths=[0.55, 0.18, 0.27])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.45)
    ax.set_title("Frozen T352 scorecard", loc="left", pad=12)

    fig.suptitle("T352 — Irrationality Di-ARA dusk-band calibration", fontsize=18, fontweight="bold")
    fig.savefig(output, dpi=170)
    plt.close(fig)


def main() -> None:
    window_rows: list[dict] = []
    event_rows: list[dict] = []
    prefix_rows: list[dict] = []

    for split, spec in SPECS.items():
        for q, d in zip(spec["q"], spec["d"]):
            for duration in spec["duration"]:
                for replicate in range(spec["replicates"]):
                    for direction in ("irrational_to_rational", "rational_to_irrational"):
                        identity = path_id(split, q, d, duration, replicate, direction)
                        for mode in ("abrupt", "ordered", "shuffled"):
                            path, ramp_start, ramp_end, source, target = make_path(
                                split, q, d, duration, replicate, direction, mode
                            )
                            rows: list[dict] = []
                            for start in range(0, LENGTH - WINDOW + 1, STRIDE):
                                end = start + WINDOW
                                center = start + WINDOW // 2
                                record = {
                                    "path_id": identity,
                                    "split": split,
                                    "q": q,
                                    "d": d,
                                    "duration": duration,
                                    "replicate": replicate,
                                    "direction": direction,
                                    "mode": mode,
                                    "source_advance": source,
                                    "target_advance": target,
                                    "window_start": start,
                                    "window_end": end,
                                    "center": center,
                                    "region": region(start, end, ramp_start, ramp_end),
                                    **measure(path[start:end]),
                                }
                                rows.append(record)
                                window_rows.append(record)
                            event_rows.append(
                                summarize_path(
                                    pd.DataFrame(rows),
                                    {
                                        "path_id": identity,
                                        "split": split,
                                        "q": q,
                                        "d": d,
                                        "duration": duration,
                                        "replicate": replicate,
                                        "direction": direction,
                                        "mode": mode,
                                    },
                                )
                            )

                            if mode == "ordered":
                                for horizon in range(WINDOW, LENGTH + 1, 256):
                                    prefix_rows.append(
                                        {
                                            "path_id": identity,
                                            "split": split,
                                            "direction": direction,
                                            "duration": duration,
                                            "horizon": horizon,
                                            **measure(path[:horizon]),
                                        }
                                    )

    windows = pd.DataFrame(window_rows)
    events = pd.DataFrame(event_rows)
    prefixes = pd.DataFrame(prefix_rows)
    windows.to_csv(HERE / f"{PREFIX}_WINDOWS.csv", index=False)
    events.to_csv(HERE / f"{PREFIX}_EVENTS.csv", index=False)
    prefixes.to_csv(HERE / f"{PREFIX}_PREFIX_PARENT.csv", index=False)

    hold = events[events["split"] == "holdout"]
    gate_rows: list[dict] = []
    endpoint_checks = {}
    for direction in ("irrational_to_rational", "rational_to_irrational"):
        ordered = hold[(hold["direction"] == direction) & (hold["mode"] == "ordered")]
        if direction == "irrational_to_rational":
            irr_xp = float(ordered["pre_x_p"].median())
            rat_xp = float(ordered["post_x_p"].median())
        else:
            rat_xp = float(ordered["pre_x_p"].median())
            irr_xp = float(ordered["post_x_p"].median())
        endpoint_checks[direction] = {
            "irrational_x_p": irr_xp,
            "rational_x_p": rat_xp,
            "pre_x_r": float(ordered["pre_x_r"].median()),
            "post_x_r": float(ordered["post_x_r"].median()),
        }
    d1 = all(
        v["irrational_x_p"] > 1.25
        and v["rational_x_p"] < 0.75
        and v["pre_x_r"] < 0.75
        and v["post_x_r"] < 0.75
        for v in endpoint_checks.values()
    )
    gate_rows.append({"gate": "D1 endpoint recovery", "passed": d1, "value": json.dumps(endpoint_checks)})

    direction_results: dict[str, dict] = {}
    for index, direction in enumerate(("irrational_to_rational", "rational_to_irrational")):
        group = hold[hold["direction"] == direction]
        ordered = group[group["mode"] == "ordered"]
        excursion = bootstrap_median(ordered["excursion_x_r"].to_numpy(), 100 + index)
        reclose = bootstrap_median(ordered["final_post_error_x_r"].to_numpy(), 200 + index)
        area_diff = bootstrap_median(
            matched_difference(group, "ordered", "abrupt", "excess_area_x_r"), 300 + index
        )
        rough_diff = bootstrap_median(
            matched_difference(group, "shuffled", "ordered", "coordinate_roughness"), 400 + index
        )
        post_share = float(np.mean(ordered["n_post"] > 0))
        direction_results[direction] = {
            "excursion": excursion,
            "reclosure_error": reclose,
            "ordered_minus_abrupt_area": area_diff,
            "shuffled_minus_ordered_roughness": rough_diff,
            "stable_post_share": post_share,
        }

    d2 = all(v["excursion"]["estimate"] >= 0.25 and v["excursion"]["ci_low"] > 0 for v in direction_results.values())
    d3 = all(v["reclosure_error"]["estimate"] <= 0.10 and v["stable_post_share"] >= 0.90 for v in direction_results.values())
    d4 = all(v["ordered_minus_abrupt_area"]["ci_low"] > 0 for v in direction_results.values())
    d5 = all(v["shuffled_minus_ordered_roughness"]["ci_low"] > 0 for v in direction_results.values())
    peaks = [v["excursion"]["estimate"] for v in direction_results.values()]
    d6 = d2 and d3 and d4 and d5 and abs(peaks[0] - peaks[1]) <= 0.25
    gate_rows.extend(
        [
            {"gate": "D2 finite ordered excursion", "passed": d2, "value": json.dumps({k: v["excursion"] for k, v in direction_results.items()})},
            {"gate": "D3 reclosure", "passed": d3, "value": json.dumps({k: {"error": v["reclosure_error"], "post_share": v["stable_post_share"]} for k, v in direction_results.items()})},
            {"gate": "D4 beyond window smear", "passed": d4, "value": json.dumps({k: v["ordered_minus_abrupt_area"] for k, v in direction_results.items()})},
            {"gate": "D5 ordered vs destroyed chronology", "passed": d5, "value": json.dumps({k: v["shuffled_minus_ordered_roughness"] for k, v in direction_results.items()})},
            {"gate": "D6 directional symmetry", "passed": d6, "value": f"median excursion difference={abs(peaks[0]-peaks[1]):.6f}"},
        ]
    )
    gates = pd.DataFrame(gate_rows)
    gates.to_csv(HERE / f"{PREFIX}_FROZEN_GATES.csv", index=False)

    passed = int(gates["passed"].sum())
    if passed == 6:
        verdict = "SUPPORTED [synthetic Irrationality Di-ARA dusk instrument only]"
    elif d1 and d2 and d3 and not d4:
        verdict = "MEASUREMENT DUSK ONLY"
    else:
        verdict = "NOT SUPPORTED"

    result = {
        "test": "T352 Irrationality Di-ARA dusk band",
        "run_date": "2026-08-11",
        "evidence_class": "synthetic known-referee transition/instrument calibration",
        "protocol_sha256": digest(PROTOCOL),
        "verdict": verdict,
        "gates_passed": passed,
        "gates_total": 6,
        "window_rows": len(windows),
        "event_rows": len(events),
        "prefix_rows": len(prefixes),
        "endpoint_checks": endpoint_checks,
        "direction_results": direction_results,
    }
    (HERE / f"{PREFIX}_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    figure = HERE / f"{PREFIX}_FIGURE.png"
    write_figure(windows, events, gates, figure)

    report = [
        "# T352 — Irrationality Di-ARA dusk band",
        "",
        "**Run date:** 11 August 2026  ",
        "**Evidence boundary:** synthetic known-referee transition/instrument calibration  ",
        f"**Verdict:** **{verdict}**  ",
        f"**Frozen gates:** **{passed}/6 passed**",
        "",
        "## Answer first",
        "",
        "T352 tested whether the existing Irrationality Di-ARA resolves a finite ordered handover between structured non-closing and rationally closing movement, after subtracting the transition produced by passing an abrupt switch through the same sliding window.",
        "",
        "The result is an instrument calibration. The generator supplies the changing rule; the test asks whether the frozen coordinates distinguish ordered transition, abrupt measurement smear and destroyed chronology without using those labels in the measurements.",
        "",
        "## Directional results",
        "",
        "| direction | ordered excursion | ordered−abrupt excess area | shuffled−ordered roughness | final post error |",
        "|---|---:|---:|---:|---:|",
    ]
    for direction, values in direction_results.items():
        report.append(
            f"| {direction.replace('_', ' ')} | {values['excursion']['estimate']:.6f} "
            f"[{values['excursion']['ci_low']:.6f}, {values['excursion']['ci_high']:.6f}] | "
            f"{values['ordered_minus_abrupt_area']['estimate']:+.6f} "
            f"[{values['ordered_minus_abrupt_area']['ci_low']:+.6f}, {values['ordered_minus_abrupt_area']['ci_high']:+.6f}] | "
            f"{values['shuffled_minus_ordered_roughness']['estimate']:+.6f} "
            f"[{values['shuffled_minus_ordered_roughness']['ci_low']:+.6f}, {values['shuffled_minus_ordered_roughness']['ci_high']:+.6f}] | "
            f"{values['reclosure_error']['estimate']:.6f} |"
        )
    report.extend(["", "## Frozen gates", "", "| gate | verdict | value |", "|---|---|---|"])
    for _, row in gates.iterrows():
        report.append(f"| {row['gate']} | {'PASS' if row['passed'] else 'FAIL'} | `{row['value']}` |")
    report.extend(
        [
            "",
            f"![T352 dusk-band diagnostics]({figure.name})",
            "",
            "## Interpretation boundary",
            "",
            "Passing would show that the frozen instrument can distinguish an ordered finite handover from abrupt window mixing and destroyed order in controlled paths. It would not establish a physical dusk band in bubbles or another domain. Failure of D4 means the visible transition is adequately explained by measurement-window mixing; failure of D5 means the instrument does not preserve the difference between smooth and order-destroyed handover.",
            "",
            "## Reproduction artifacts",
            "",
            f"- `{PREFIX}_WINDOWS.csv`",
            f"- `{PREFIX}_EVENTS.csv`",
            f"- `{PREFIX}_PREFIX_PARENT.csv`",
            f"- `{PREFIX}_FROZEN_GATES.csv`",
            f"- `{PREFIX}_RESULTS.json`",
            f"- `{PREFIX}_FIGURE.png`",
            "- `t352_irrationality_di_ara_dusk_band.py`",
        ]
    )
    (HERE / f"{PREFIX}_REPORT_2026-08-11.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": verdict, "gates": f"{passed}/6", "events": len(events), "windows": len(windows)}, indent=2))


if __name__ == "__main__":
    main()
