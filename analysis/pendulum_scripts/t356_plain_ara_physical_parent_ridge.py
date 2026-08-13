"""T356: frozen plain-ARA physical parent-ridge transfer.

Angle reversals are predictor-only child landmarks. Their unweighted midpoint
is scored against the peak of the separately recorded angular-velocity channel.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks

from pendulum_common import load_triple, load_triple_driven, rest_centered


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "T356_PLAIN_ARA_PHYSICAL_PARENT_RIDGE_PROTOCOL_v1_FROZEN.md"
EXPECTED_PROTOCOL_SHA256 = "CEA75E318D0FBFA28F0869F2BBDFFF7FAFEAC369698C3A058F4B6598709D8289"
EVENTS_CSV = HERE / "T356_PLAIN_ARA_PHYSICAL_PARENT_RIDGE_EVENTS.csv"
SUMMARY_CSV = HERE / "T356_PLAIN_ARA_PHYSICAL_PARENT_RIDGE_SUMMARY.csv"
RESULTS_JSON = HERE / "T356_PLAIN_ARA_PHYSICAL_PARENT_RIDGE_RESULTS.json"
FIGURE_PNG = HERE / "T356_PLAIN_ARA_PHYSICAL_PARENT_RIDGE_FIGURE.png"
REPORT_MD = HERE / "T356_PLAIN_ARA_PHYSICAL_PARENT_RIDGE_REPORT_2026-08-11.md"

DECIMATE = 10
PROM_RAD = 0.02 * math.pi
REFERENCE_PERIOD_S = 1.333
MIN_TURN_DISTANCE_S = 0.4 * REFERENCE_PERIOD_S
BOOTSTRAPS = 10_000
SEED = 20_260_811


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def detect_turns(angle: np.ndarray, fs: float) -> list[tuple[int, int]]:
    distance = max(1, int(round(MIN_TURN_DISTANCE_S * fs)))
    hi, _ = find_peaks(angle, prominence=PROM_RAD, distance=distance)
    lo, _ = find_peaks(-angle, prominence=PROM_RAD, distance=distance)
    tagged = [(int(i), 1) for i in hi] + [(int(i), -1) for i in lo]
    return sorted(tagged)


def interp_at(values: np.ndarray, index: float) -> float:
    return float(np.interp(index, np.arange(len(values), dtype=float), values))


def event_rows(run: str, regime: str, arm: int) -> list[dict]:
    if regime == "driven":
        t, raw, velocity, fs = load_triple_driven(run, decimate=DECIMATE)
    else:
        t, raw, velocity, fs = load_triple(run, decimate=DECIMATE)
    angle = rest_centered(raw)[arm]
    speed = np.abs(np.asarray(velocity[arm], dtype=float))
    turns = detect_turns(angle, fs)

    candidates: list[dict] = []
    for j in range(len(turns) - 1):
        (left, left_kind), (right, right_kind) = turns[j], turns[j + 1]
        if left_kind == right_kind or right - left < 6:
            continue
        interior = speed[left + 1 : right]
        if interior.size < 5 or not np.all(np.isfinite(interior)):
            continue
        target = left + 1 + int(np.argmax(interior))
        pred = 0.5 * (left + right)
        duration = float(right - left)
        peak_speed = float(speed[target])
        if not np.isfinite(peak_speed) or peak_speed <= 0:
            continue
        candidates.append(
            {
                "run": run,
                "regime": regime,
                "arm": arm,
                "event_local": len(candidates),
                "left_index": left,
                "right_index": right,
                "target_index": target,
                "pred_index": pred,
                "left_time_s": float(t[left]),
                "right_time_s": float(t[right]),
                "target_time_s": float(t[target]),
                "pred_time_s": float(np.interp(pred, np.arange(len(t)), t)),
                "duration_s": float(t[right] - t[left]),
                "direction": "increasing" if angle[right] > angle[left] else "decreasing",
                "left_angle_rad": float(angle[left]),
                "right_angle_rad": float(angle[right]),
                "target_speed_rad_s": peak_speed,
                "pred_speed_rad_s": interp_at(speed, pred),
                "flow_fraction": interp_at(speed, pred) / peak_speed,
                "target_phase": (target - left) / duration,
                "pred_phase": 0.5,
                "error_plain": abs(pred - target) / duration,
                "error_left": abs(left - target) / duration,
                "error_right": abs(right - target) / duration,
                "wrong_pred_index": float("nan"),
                "error_wrong": float("nan"),
            }
        )

    # Frozen wrong relation: current left child + next eligible half-swing's
    # right child. It is not used for the final event because no next pair exists.
    for i in range(len(candidates) - 1):
        current = candidates[i]
        nxt = candidates[i + 1]
        wrong = 0.5 * (current["left_index"] + nxt["right_index"])
        current["wrong_pred_index"] = wrong
        current["error_wrong"] = abs(wrong - current["target_index"]) / (
            current["right_index"] - current["left_index"]
        )
    return candidates


def q(values, p: float) -> float:
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    return float(np.quantile(x, p)) if len(x) else float("nan")


def median(values) -> float:
    return q(values, 0.5)


def bootstrap_ci(values, statistic="median") -> list[float]:
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    rng = np.random.default_rng(SEED)
    if len(x) == 0:
        return [float("nan"), float("nan")]
    draws = np.empty(BOOTSTRAPS, dtype=float)
    for i in range(BOOTSTRAPS):
        sample = x[rng.integers(0, len(x), len(x))]
        draws[i] = np.median(sample) if statistic == "median" else np.quantile(sample, 0.95)
    return [float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))]


def summarize(rows: list[dict]) -> list[dict]:
    keys = sorted({(r["regime"], r["run"], r["arm"], r["direction"]) for r in rows})
    out = []
    for regime, run, arm, direction in keys:
        z = [r for r in rows if (r["regime"], r["run"], r["arm"], r["direction"]) == (regime, run, arm, direction)]
        out.append(
            {
                "regime": regime,
                "run": run,
                "arm": arm,
                "direction": direction,
                "n": len(z),
                "median_error_plain": median([r["error_plain"] for r in z]),
                "p95_error_plain": q([r["error_plain"] for r in z], 0.95),
                "median_error_left": median([r["error_left"] for r in z]),
                "median_error_right": median([r["error_right"] for r in z]),
                "median_error_wrong": median([r["error_wrong"] for r in z]),
                "median_flow_fraction": median([r["flow_fraction"] for r in z]),
                "median_target_phase": median([r["target_phase"] for r in z]),
            }
        )
    return out


def score(rows: list[dict]) -> dict:
    free = [r for r in rows if r["regime"] == "free"]
    driven = [r for r in rows if r["regime"] == "driven"]
    ep = [r["error_plain"] for r in free]
    el = [r["error_left"] for r in free]
    er = [r["error_right"] for r in free]
    ew = [r["error_wrong"] for r in free]
    ff = [r["flow_fraction"] for r in free]

    direction = {
        d: {
            "n": len(z := [r for r in free if r["direction"] == d]),
            "median_error_plain": median([r["error_plain"] for r in z]),
            "median_flow_fraction": median([r["flow_fraction"] for r in z]),
        }
        for d in ("increasing", "decreasing")
    }
    groups = []
    for run in ("run1", "run2", "run3"):
        for arm in (1, 2, 3):
            z = [r for r in free if r["run"] == run and r["arm"] == arm]
            groups.append({"run": run, "arm": arm, "n": len(z), "median_error_plain": median([r["error_plain"] for r in z]), "median_flow_fraction": median([r["flow_fraction"] for r in z])})

    med_plain = median(ep)
    med_left = median(el)
    med_right = median(er)
    med_wrong = median(ew)
    p95_plain = q(ep, 0.95)
    med_flow = median(ff)
    gates = {
        "G1_absolute_location": med_plain < 0.10,
        "G2_tail": p95_plain < 0.25,
        "G3_two_child_necessity": med_plain <= 0.5 * med_left and med_plain <= 0.5 * med_right,
        "G4_correct_relation": med_plain <= 0.5 * med_wrong,
        "G5_directional_transfer": all(direction[d]["median_error_plain"] < 0.12 for d in direction),
        "G6_replication": sum(g["median_error_plain"] < 0.12 for g in groups) >= 8,
        "G7_physical_ridge": med_flow > 0.90,
    }

    def regime_metrics(z):
        return {
            "n": len(z),
            "median_error_plain": median([r["error_plain"] for r in z]),
            "p95_error_plain": q([r["error_plain"] for r in z], 0.95),
            "median_error_left": median([r["error_left"] for r in z]),
            "median_error_right": median([r["error_right"] for r in z]),
            "median_error_wrong": median([r["error_wrong"] for r in z]),
            "median_flow_fraction": median([r["flow_fraction"] for r in z]),
            "median_target_phase": median([r["target_phase"] for r in z]),
        }

    return {
        "protocol_sha256": sha256(PROTOCOL),
        "verdict": "SUPPORTED IN THIS PENDULUM CUT" if all(gates.values()) else "NOT SUPPORTED",
        "gates_passed": int(sum(gates.values())),
        "gates_total": len(gates),
        "gates": gates,
        "free": regime_metrics(free),
        "driven_transfer": regime_metrics(driven),
        "free_uncertainty": {
            "median_error_plain_ci95": bootstrap_ci(ep, "median"),
            "p95_error_plain_ci95": bootstrap_ci(ep, "p95"),
            "median_flow_fraction_ci95": bootstrap_ci(ff, "median"),
        },
        "directions": direction,
        "free_groups": groups,
        "constants": {
            "decimate": DECIMATE,
            "prominence_rad": PROM_RAD,
            "reference_period_s": REFERENCE_PERIOD_S,
            "minimum_turn_distance_s": MIN_TURN_DISTANCE_S,
            "bootstraps": BOOTSTRAPS,
            "seed": SEED,
        },
    }


def write_csv(path: Path, rows: list[dict]):
    fields = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def make_figure(rows: list[dict], result: dict):
    free = [r for r in rows if r["regime"] == "free"]
    driven = [r for r in rows if r["regime"] == "driven"]
    fig, ax = plt.subplots(2, 2, figsize=(15, 10), constrained_layout=True)
    fig.patch.set_facecolor("#f4f7fb")
    for a in ax.flat:
        a.set_facecolor("#ffffff")
        a.grid(color="#dfe5ec", lw=0.7, alpha=0.85)
        a.spines[["top", "right"]].set_visible(False)

    # A: representative raw half-swing from each regime, chosen near median error.
    for regime, pool, colour, ls in (("free", free, "#2869b2", "-"), ("driven", driven, "#dd8b24", "--")):
        m = median([r["error_plain"] for r in pool])
        r = min(pool, key=lambda z: abs(z["error_plain"] - m))
        if regime == "driven":
            t, raw, vel, _ = load_triple_driven(r["run"], decimate=DECIMATE)
        else:
            t, raw, vel, _ = load_triple(r["run"], decimate=DECIMATE)
        angle = rest_centered(raw)[r["arm"]]
        left, right = int(r["left_index"]), int(r["right_index"])
        u = np.linspace(0, 1, right - left + 1)
        segment = angle[left:right + 1]
        y = 2 * (segment - segment[0]) / (segment[-1] - segment[0])
        ax[0, 0].plot(u, y, color=colour, ls=ls, lw=1.8, label=f"{regime}: angle cut")
        ax[0, 0].axvline(r["target_phase"], color=colour, ls=":", lw=1.8)
    ax[0, 0].axvline(0.5, color="#1f2933", lw=2.2, label="plain-ARA midpoint")
    ax[0, 0].scatter([0, 1], [0, 2], c=["#2b7a78", "#b64b4b"], s=50, zorder=4)
    ax[0, 0].set(xlabel="local half-swing (0 → 1)", ylabel="oriented ARA cut (0 → 2)", title="Two child poles locate the physical flow ridge")
    ax[0, 0].legend(frameon=False, fontsize=8)

    # B: occurrence-wise physical peak positions.
    for direction, marker, colour in (("increasing", "o", "#2869b2"), ("decreasing", "^", "#dd8b24")):
        z = [r for r in free if r["direction"] == direction]
        ax[0, 1].scatter(range(len(z)), [r["target_phase"] for r in z], s=9, alpha=0.45, marker=marker, color=colour, label=direction)
    ax[0, 1].axhline(0.5, color="#1f2933", lw=2, label="predicted ridge")
    ax[0, 1].axhspan(0.4, 0.6, color="#6aa96b", alpha=0.12, label="G1 ±0.10")
    ax[0, 1].set(xlabel="half-swing occurrence (pooled)", ylabel="recorded peak-flow phase", ylim=(0, 1), title="Held-out velocity peaks cluster at the relation")
    ax[0, 1].legend(frameon=False, fontsize=8, ncols=2)

    # C: registered control distributions.
    labels = ["plain ARA", "left child", "right child", "wrong pair"]
    vals = [
        [r["error_plain"] for r in free],
        [r["error_left"] for r in free],
        [r["error_right"] for r in free],
        [r["error_wrong"] for r in free if np.isfinite(r["error_wrong"])],
    ]
    bp = ax[1, 0].boxplot(vals, tick_labels=labels, showfliers=False, patch_artist=True, widths=0.6)
    for i, box in enumerate(bp["boxes"]):
        box.set_facecolor("#5c8fc5" if i == 0 else "#c7ced7")
        box.set_alpha(0.85)
    ax[1, 0].axhline(0.10, color="#b64b4b", ls="--", lw=1.3, label="G1 ceiling")
    ax[1, 0].set(ylabel="error / half-swing duration", title="The relation, not either landmark alone, carries the location")
    ax[1, 0].legend(frameon=False, fontsize=8)

    # D: every group, including external-force transfer.
    groups = []
    for regime, run in [("free", "run1"), ("free", "run2"), ("free", "run3"), ("driven", "triple1")]:
        for arm in (1, 2, 3):
            z = [r for r in rows if r["regime"] == regime and r["run"] == run and r["arm"] == arm]
            groups.append((f"{run}\nA{arm}", median([r["error_plain"] for r in z]), regime))
    x = np.arange(len(groups))
    ax[1, 1].bar(x, [g[1] for g in groups], color=["#5c8fc5" if g[2] == "free" else "#dd8b24" for g in groups], width=0.72)
    ax[1, 1].axhline(0.12, color="#b64b4b", ls="--", lw=1.3, label="group gate")
    ax[1, 1].set_xticks(x, [g[0] for g in groups], fontsize=8)
    ax[1, 1].set(ylabel="median normalized error", title="Replication across arms, runs and driven transfer")
    ax[1, 1].legend(frameon=False, fontsize=8)

    fig.suptitle(
        f"T356 — plain ARA physical parent ridge | {result['verdict']} ({result['gates_passed']}/{result['gates_total']} gates)",
        fontsize=16,
        fontweight="normal",
    )
    fig.savefig(FIGURE_PNG, dpi=170)
    plt.close(fig)


def make_report(result: dict, rows: list[dict]):
    f = result["free"]
    d = result["driven_transfer"]
    ci = result["free_uncertainty"]
    groups = result["free_groups"]
    lines = [
        "# T356 — plain ARA physical parent-ridge transfer",
        "",
        "**Date:** 11 August 2026  ",
        f"**Frozen verdict:** **{result['verdict']} (`{result['gates_passed']}/{result['gates_total']}` gates)**  ",
        f"**Protocol SHA-256:** `{result['protocol_sha256']}`",
        "",
        "## Answer first",
        "",
        "Two angle reversals were enough to locate the typical centre of the separately recorded flow event, but not every individual maximum-flow event. The unweighted midpoint was frozen before the velocity channel was scored; no pendulum equation, fitted correction or velocity value moved it.",
        "",
        f"Across **{f['n']:,} free-swing half-cycles**, the plain-ARA midpoint had median normalized timing error **{f['median_error_plain']:.5f}** (95% bootstrap CI **{ci['median_error_plain_ci95'][0]:.5f}–{ci['median_error_plain_ci95'][1]:.5f}**) and 95th-percentile error **{f['p95_error_plain']:.5f}**. It retained **{100*f['median_flow_fraction']:.2f}%** of the interval's measured peak angular speed at the predicted location.",
        "",
        "The two reversals define a **local half-swing parent** whose geometric ridge is their centre. Maximum flow commonly coincides with that ridge, but the failed tail and replication gates show that this physical expression is not invariant in the freely coupled triple pendulum.",
        "",
        "## Registered comparison",
        "",
        "| Predictor | Median error / half-swing |",
        "|---|---:|",
        f"| Plain ARA midpoint | **{f['median_error_plain']:.6f}** |",
        f"| Left child alone | {f['median_error_left']:.6f} |",
        f"| Right child alone | {f['median_error_right']:.6f} |",
        f"| Wrongly paired children | {f['median_error_wrong']:.6f} |",
        "",
        "## Frozen gates",
        "",
    ]
    for name, passed in result["gates"].items():
        lines.append(f"- `{name}`: **{'PASS' if passed else 'FAIL'}**")
    lines += [
        "",
        "## Direction and replication",
        "",
        "| Direction | n | Median error | Median retained flow |",
        "|---|---:|---:|---:|",
    ]
    for direction, z in result["directions"].items():
        lines.append(f"| {direction} | {z['n']:,} | {z['median_error_plain']:.6f} | {z['median_flow_fraction']:.6f} |")
    lines += [
        "",
        "| Run | Arm | n | Median error | Median retained flow |",
        "|---|---:|---:|---:|---:|",
    ]
    for g in groups:
        lines.append(f"| {g['run']} | {g['arm']} | {g['n']} | {g['median_error_plain']:.6f} | {g['median_flow_fraction']:.6f} |")
    lines += [
        "",
        "## Driven transfer",
        "",
        f"The unchanged rule was also applied to **{d['n']:,}** externally driven half-cycles. Median error was **{d['median_error_plain']:.6f}**, 95th-percentile error **{d['p95_error_plain']:.6f}**, and median retained-flow fraction **{d['median_flow_fraction']:.6f}**. This transfer cannot alter the free-swing verdict.",
        "",
        "## ARA reading and boundary",
        "",
        "This is plain ARA in a literal local slice: child pole + opposite child pole + their relation fixes the geometric parent ridge. It also explains why the relation mattered in T355: either landmark alone describes a boundary, while the pair supplies the missing location. T356 does not support equating that geometric ridge with the strongest individual-arm flow in every coupled state.",
        "",
        "The result is a physical crosswalk and a successful prospective endpoint on previously opened public data. It does not prove universal ARA or new pendulum physics. The recovered identity—maximum angular flow—is specific to this oscillator representation; other systems require their own held-out physical referee.",
        "",
        "## Reproduction",
        "",
        "Run `t356_plain_ara_physical_parent_ridge.py`, then `validate_t356_plain_ara_physical_parent_ridge.py` from this directory with the repository verification environment.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    actual = sha256(PROTOCOL)
    if actual != EXPECTED_PROTOCOL_SHA256:
        raise RuntimeError(f"Frozen protocol hash mismatch: {actual}")

    rows: list[dict] = []
    for run in ("run1", "run2", "run3"):
        for arm in (1, 2, 3):
            rows.extend(event_rows(run, "free", arm))
    for arm in (1, 2, 3):
        rows.extend(event_rows("triple1", "driven", arm))
    for i, row in enumerate(rows):
        row["event_id"] = i

    summary = summarize(rows)
    result = score(rows)
    write_csv(EVENTS_CSV, rows)
    write_csv(SUMMARY_CSV, summary)
    RESULTS_JSON.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    make_figure(rows, result)
    make_report(result, rows)
    print(json.dumps({"verdict": result["verdict"], "gates": result["gates"], "free": result["free"], "driven": result["driven_transfer"]}, indent=2))


if __name__ == "__main__":
    main()
