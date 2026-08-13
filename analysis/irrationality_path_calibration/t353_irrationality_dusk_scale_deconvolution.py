#!/usr/bin/env python3
"""T353: separate finite Irrationality dusk duration from window smear."""

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

from t352_irrationality_di_ara_dusk_band import stochastic_residual


PREFIX = "T353_IRRATIONALITY_DUSK_SCALE_DECONVOLUTION"
PROTOCOL = HERE / f"{PREFIX}_PROTOCOL_v1_FROZEN.md"
LENGTH = 4096
CENTER = LENGTH // 2
WINDOWS = (128, 256, 384, 512)
STRIDE = 32
Q_VALUES = (11, 18, 22)
D_VALUES = (31, 37, 41)
DURATIONS = (320, 448, 576, 704)
REPLICATES = 12
BOOTSTRAPS = 5000
SEED = 35320260811


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
    return values[replicate % len(values)]


def make_path(q: int, d: int, duration: int, replicate: int, direction: str, mode: str) -> tuple[np.ndarray, int, int]:
    rational = coprime_numerator(q, replicate) / q
    irrational = math.sqrt(d) - math.floor(math.sqrt(d))
    source, target = (irrational, rational) if direction == "irrational_to_rational" else (rational, irrational)
    start = CENTER - duration // 2
    end = start + duration
    advances = np.full(LENGTH - 1, source, dtype=float)
    advances[end:] = target
    if mode == "ordered":
        advances[start:end] = np.linspace(source, target, duration, endpoint=False)
    elif mode == "abrupt":
        advances[CENTER:] = target
    else:
        raise ValueError(mode)
    rng = np.random.default_rng(stable_seed("phase", q, d, duration, replicate, direction))
    phase = float(rng.random())
    path = np.empty(LENGTH)
    path[0] = phase
    path[1:] = (phase + np.cumsum(advances)) % 1.0
    return path, start, end


def longest_band(centres: np.ndarray, values: np.ndarray, threshold: float) -> int:
    selected = centres[values >= threshold]
    if not len(selected):
        return 0
    best = 1
    current = 1
    for left, right in zip(selected[:-1], selected[1:]):
        if right - left == STRIDE:
            current += 1
            best = max(best, current)
        else:
            current = 1
    return int(best * STRIDE)


def spearman(left: np.ndarray, right: np.ndarray) -> float:
    left_rank = pd.Series(left).rank(method="average").to_numpy()
    right_rank = pd.Series(right).rank(method="average").to_numpy()
    if np.std(left_rank) == 0 or np.std(right_rank) == 0:
        return 0.0
    return float(np.corrcoef(left_rank, right_rank)[0, 1])


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


def bootstrap_spearman(frame: pd.DataFrame, offset: int) -> dict[str, float]:
    rng = np.random.default_rng(SEED + offset)
    duration = frame["duration"].to_numpy(float)
    estimate = frame["duration_hat"].to_numpy(float)
    draws = rng.integers(0, len(frame), size=(BOOTSTRAPS, len(frame)))
    samples = np.asarray([spearman(duration[idx], estimate[idx]) for idx in draws])
    return {
        "estimate": spearman(duration, estimate),
        "ci_low": float(np.quantile(samples, 0.025)),
        "ci_high": float(np.quantile(samples, 0.975)),
        "n": int(len(frame)),
    }


def r_squared(x: np.ndarray, y: np.ndarray, fit: np.ndarray) -> float:
    residual = float(np.sum((y - fit) ** 2))
    total = float(np.sum((y - np.mean(y)) ** 2))
    return 1.0 if total <= 1e-12 and residual <= 1e-12 else (0.0 if total <= 1e-12 else 1.0 - residual / total)


def measure_band(path: np.ndarray, ramp_start: int, ramp_end: int, window: int) -> tuple[dict, list[dict]]:
    all_starts = np.arange(0, LENGTH - window + 1, STRIDE, dtype=int)
    all_centres = all_starts + window // 2
    hand_mask = (all_centres >= ramp_start - window // 2) & (all_centres <= ramp_end + window // 2)
    pre_candidates = all_starts[all_starts + window <= ramp_start]
    post_candidates = all_starts[all_starts >= ramp_end]
    selected_pre = pre_candidates[-4:]
    selected_post = post_candidates[:4]
    selected = np.unique(np.concatenate((selected_pre, all_starts[hand_mask], selected_post)))
    rows = []
    for start in selected:
        end = int(start + window)
        center = int(start + window // 2)
        x_r, local, null = stochastic_residual(path[start:end])
        if end <= ramp_start:
            region = "pre"
        elif start >= ramp_end:
            region = "post"
        else:
            region = "handover"
        rows.append({"start": int(start), "end": end, "center": center, "region": region, "x_r": x_r, "local_loss": local, "null_loss": null})
    frame = pd.DataFrame(rows).sort_values("center")
    baseline = max(float(frame[frame.region == "pre"].x_r.median()), float(frame[frame.region == "post"].x_r.median()))
    hand = frame[(frame.center >= ramp_start - window // 2) & (frame.center <= ramp_end + window // 2)]
    width = longest_band(hand.center.to_numpy(int), hand.x_r.to_numpy(float), baseline + 0.25)
    return {
        "baseline_x_r": baseline,
        "band_width": width,
        "peak_excursion": float(hand.x_r.max() - baseline),
        "pre_x_r": float(frame[frame.region == "pre"].x_r.median()),
        "post_x_r": float(frame[frame.region == "post"].x_r.median()),
    }, rows


def make_figure(bands: pd.DataFrame, identities: pd.DataFrame, gates: pd.DataFrame, profiles: pd.DataFrame, output: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=True)
    colors = {"ordered": "#2F6FB0", "abrupt": "#D49A2E"}
    ax = axes[0, 0]
    for direction, marker in (("irrational_to_rational", "o"), ("rational_to_irrational", "s")):
        for mode, style in (("ordered", "-"), ("abrupt", "--")):
            part = bands[(bands.direction == direction) & (bands["mode"] == mode)]
            curve = part.groupby("window", as_index=False).band_width.median()
            ax.plot(curve.window, curve.band_width, style, marker=marker, color=colors[mode], alpha=0.9, label=f"{mode}, {direction.replace('_to_', '→')}")
    ax.set(xlabel="observation window W (states)", ylabel="observed band width B(W)", title="Window growth versus finite handover width")
    ax.legend(frameon=False, fontsize=8)

    ax = axes[0, 1]
    jitter = {"irrational_to_rational": -8, "rational_to_irrational": 8}
    for direction, color in (("irrational_to_rational", "#2F6FB0"), ("rational_to_irrational", "#D49A2E")):
        part = identities[identities.direction == direction]
        grouped = part.groupby("duration", as_index=False).duration_hat.median()
        ax.scatter(grouped.duration + jitter[direction], grouped.duration_hat, s=60, color=color, label=direction.replace("_to_", "→"))
    ax.plot([250, 750], [250, 750], color="#7A8490", lw=1, linestyle=":")
    ax.set(xlim=(250, 750), ylim=(-20, 780), xlabel="declared handover duration", ylabel="deconvolved duration T_hat", title="Can the instrument recover handover duration?")
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 0]
    example = profiles[(profiles.q == Q_VALUES[0]) & (profiles.duration == DURATIONS[1]) & (profiles.replicate == 0) & (profiles.direction == "irrational_to_rational")]
    for window, alpha in ((128, 0.75), (512, 1.0)):
        for mode, style in (("ordered", "-"), ("abrupt", "--")):
            part = example[(example.window == window) & (example["mode"] == mode)].sort_values("center")
            ax.plot(part.center - CENTER, part.x_r, style, color=colors[mode], alpha=alpha, label=f"{mode}, W={window}")
    ax.axvline(0, color="#7A8490", lw=1)
    ax.set(xlabel="states from declared centre", ylabel="x_R", title="One untouched matched transition")
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 1]
    ax.axis("off")
    table = ax.table(
        cellText=[[row.gate, "PASS" if row.passed else "FAIL", str(row.value)[:42]] for row in gates.itertuples()],
        colLabels=["Frozen gate", "Result", "headline"],
        colWidths=[0.50, 0.16, 0.34], loc="center", cellLoc="left"
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.45)
    ax.set_title("Frozen T353 scorecard", loc="left")
    fig.suptitle("T353 — Irrationality dusk scale deconvolution", fontsize=18, fontweight="bold")
    fig.savefig(output, dpi=170)
    plt.close(fig)


def main() -> None:
    band_rows: list[dict] = []
    profile_rows: list[dict] = []
    for q, d in zip(Q_VALUES, D_VALUES):
        for duration in DURATIONS:
            for replicate in range(REPLICATES):
                for direction in ("irrational_to_rational", "rational_to_irrational"):
                    identity = f"q{q}:d{d}:t{duration}:r{replicate}:{direction}"
                    for mode in ("ordered", "abrupt"):
                        path, ramp_start, ramp_end = make_path(q, d, duration, replicate, direction, mode)
                        for window in WINDOWS:
                            summary, rows = measure_band(path, ramp_start, ramp_end, window)
                            band_rows.append({"path_id": identity, "q": q, "d": d, "duration": duration, "replicate": replicate, "direction": direction, "mode": mode, "window": window, **summary})
                            for row in rows:
                                profile_rows.append({"path_id": identity, "q": q, "d": d, "duration": duration, "replicate": replicate, "direction": direction, "mode": mode, "window": window, **row})
    bands = pd.DataFrame(band_rows)
    profiles = pd.DataFrame(profile_rows)

    identity_rows: list[dict] = []
    for (identity, direction, duration), group in bands.groupby(["path_id", "direction", "duration"]):
        pivot = group.pivot(index="window", columns="mode", values="band_width").sort_index()
        added = pivot["ordered"] - pivot["abrupt"]
        abrupt = pivot["abrupt"].to_numpy(float)
        x = pivot.index.to_numpy(float)
        slope, intercept = np.polyfit(x, abrupt, 1)
        fit = slope * x + intercept
        identity_rows.append({
            "path_id": identity,
            "direction": direction,
            "duration": duration,
            "duration_hat": float(np.median(added)),
            "absolute_error": abs(float(np.median(added)) - duration),
            "abrupt_intercept": float(intercept),
            "abrupt_slope": float(slope),
            "abrupt_r2": r_squared(x, abrupt, fit),
            "positive_window_count": int(np.sum(added > 0)),
        })
    identities = pd.DataFrame(identity_rows)

    stable = bands.groupby(["direction", "mode", "window"])[["pre_x_r", "post_x_r"]].median().reset_index()
    m1 = bool((stable[["pre_x_r", "post_x_r"]].to_numpy() < 0.75).all())
    m2_parts = {}
    for direction in identities.direction.unique():
        part = identities[identities.direction == direction]
        m2_parts[direction] = {"median_abs_intercept": float(np.median(np.abs(part.abrupt_intercept))), "median_r2": float(np.median(part.abrupt_r2))}
    m2 = all(v["median_abs_intercept"] <= 64 and v["median_r2"] >= 0.75 for v in m2_parts.values())

    direction_results = {}
    for index, direction in enumerate(("irrational_to_rational", "rational_to_irrational")):
        part = identities[identities.direction == direction]
        direction_results[direction] = {
            "duration_hat": bootstrap_median(part.duration_hat.to_numpy(), 100 + index),
            "duration_spearman": bootstrap_spearman(part, 200 + index),
            "absolute_error": bootstrap_median(part.absolute_error.to_numpy(), 300 + index),
            "positive_window_median": float(np.median(part.positive_window_count)),
        }
    m3 = all(v["duration_hat"]["ci_low"] > 0 for v in direction_results.values())
    m4 = all(v["duration_spearman"]["estimate"] >= 0.75 and v["duration_spearman"]["ci_low"] > 0.50 for v in direction_results.values())
    m5 = all(v["absolute_error"]["estimate"] <= 128 for v in direction_results.values())
    hats = [v["duration_hat"]["estimate"] for v in direction_results.values()]
    width_wins = {}
    for direction in direction_results:
        group = bands[bands.direction == direction].groupby(["window", "mode"]).band_width.median().unstack("mode")
        width_wins[direction] = int(np.sum(group["ordered"] > group["abrupt"]))
    m6 = abs(hats[0] - hats[1]) <= 64 and all(value >= 3 for value in width_wins.values())

    gates = pd.DataFrame([
        {"gate": "M1 stable endpoints", "passed": m1, "value": f"maximum grouped median={stable[['pre_x_r','post_x_r']].to_numpy().max():.6f}"},
        {"gate": "M2 abrupt-smear calibration", "passed": m2, "value": json.dumps(m2_parts)},
        {"gate": "M3 positive deconvolved duration", "passed": m3, "value": json.dumps({k: v['duration_hat'] for k, v in direction_results.items()})},
        {"gate": "M4 duration ordering", "passed": m4, "value": json.dumps({k: v['duration_spearman'] for k, v in direction_results.items()})},
        {"gate": "M5 numerical recovery", "passed": m5, "value": json.dumps({k: v['absolute_error'] for k, v in direction_results.items()})},
        {"gate": "M6 directional symmetry", "passed": m6, "value": f"hat difference={abs(hats[0]-hats[1]):.3f}; width wins={width_wins}"},
    ])
    passed = int(gates.passed.sum())
    if passed == 6:
        verdict = "SUPPORTED [synthetic multiscale dusk-duration instrument only]"
    elif m1 and m2 and not m3:
        verdict = "WINDOW SMEAR ONLY"
    elif m3 and (not m4 or not m5):
        verdict = "FINITE BAND, DURATION UNRESOLVED"
    else:
        verdict = "NOT SUPPORTED"

    bands.to_csv(HERE / f"{PREFIX}_BANDS.csv", index=False)
    profiles.to_csv(HERE / f"{PREFIX}_PROFILES.csv", index=False)
    identities.to_csv(HERE / f"{PREFIX}_IDENTITIES.csv", index=False)
    gates.to_csv(HERE / f"{PREFIX}_FROZEN_GATES.csv", index=False)
    result = {
        "test": "T353 Irrationality dusk scale deconvolution",
        "run_date": "2026-08-11",
        "evidence_class": "synthetic known-referee multiscale follow-up",
        "protocol_sha256": digest(PROTOCOL),
        "verdict": verdict,
        "gates_passed": passed,
        "gates_total": 6,
        "band_rows": len(bands),
        "profile_rows": len(profiles),
        "identity_rows": len(identities),
        "direction_results": direction_results,
        "abrupt_smear": m2_parts,
        "width_wins": width_wins,
    }
    (HERE / f"{PREFIX}_RESULTS.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    figure = HERE / f"{PREFIX}_FIGURE.png"
    make_figure(bands, identities, gates, profiles, figure)

    lines = [
        "# T353 — Irrationality dusk scale deconvolution", "",
        "**Run date:** 11 August 2026  ",
        "**Evidence boundary:** synthetic known-referee multiscale follow-up  ",
        f"**Verdict:** **{verdict}**  ", f"**Frozen gates:** **{passed}/6 passed**", "",
        "## Answer first", "",
        "T353 changed the observer rather than the event. Four window sizes measured each new ordered handover and its matched abrupt switch. The abrupt width estimates measurement smear; subtracting it tests whether a finite transition duration remains.", "",
        "## Directional recovery", "",
        "| direction | median T_hat | Spearman with declared duration | median absolute error | positive window count |", "|---|---:|---:|---:|---:|",
    ]
    for direction, value in direction_results.items():
        lines.append(f"| {direction.replace('_',' ')} | {value['duration_hat']['estimate']:.3f} [{value['duration_hat']['ci_low']:.3f}, {value['duration_hat']['ci_high']:.3f}] | {value['duration_spearman']['estimate']:.4f} [{value['duration_spearman']['ci_low']:.4f}, {value['duration_spearman']['ci_high']:.4f}] | {value['absolute_error']['estimate']:.3f} | {value['positive_window_median']:.1f}/4 |")
    lines.extend(["", "## Frozen gates", "", "| gate | result | headline |", "|---|---|---|"])
    for row in gates.itertuples():
        lines.append(f"| {row.gate} | {'PASS' if row.passed else 'FAIL'} | `{row.value}` |")
    lines.extend(["", f"![T353 scale deconvolution]({figure.name})", "", "## Interpretation boundary", "", "The generator contains the transition duration by construction. Passing shows only that the frozen residual plus matched abrupt control can recover that duration across new parameters and scales. It is not physical-domain evidence.", "", "## Artifacts", "", f"- `{PREFIX}_BANDS.csv`", f"- `{PREFIX}_PROFILES.csv`", f"- `{PREFIX}_IDENTITIES.csv`", f"- `{PREFIX}_FROZEN_GATES.csv`", f"- `{PREFIX}_RESULTS.json`", f"- `{PREFIX}_FIGURE.png`", "- `t353_irrationality_dusk_scale_deconvolution.py`"])
    (HERE / f"{PREFIX}_REPORT_2026-08-11.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": verdict, "gates": f"{passed}/6", "identities": len(identities)}, indent=2))


if __name__ == "__main__":
    main()
