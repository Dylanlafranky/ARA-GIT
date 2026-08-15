#!/usr/bin/env python3
"""T379: frozen individual-muon child handover test.

The script logs into the documented QuarkNet guest account, streams four raw
DAQ-6845 files without retaining the multi-hundred-megabyte sources, reduces
them to clean event-linked prompt/daughter records, and evaluates the frozen
chronological holdout protocol.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import http.cookiejar
import json
import math
import ssl
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict, deque
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "T379_individual_muon_child"
PROTOCOL = ROOT / "T379_INDIVIDUAL_MUON_CHILD_HANDOVER_PROTOCOL_2026-08-14.md"
EXPECTED_PROTOCOL_SHA256 = "b9219da0db0dae6b4b1e2b2b203378bcebee1fa5e0450d92b45acaded541b669"

FILES = [
    {"name": "6845.2020.0211.0", "split": "calibration", "freq": 25_000_000.0},
    {"name": "6845.2020.0212.0", "split": "calibration", "freq": 25_000_002.0},
    {"name": "6845.2020.0317.0", "split": "holdout", "freq": 24_999_998.0},
    {"name": "6845.2020.0318.0", "split": "holdout", "freq": 24_999_998.0},
]

VARIANTS = {
    "main": (100.0, 300.0),
    "w50": (50.0, 300.0),
    "w150": (150.0, 300.0),
    "d200": (100.0, 200.0),
    "d500": (100.0, 500.0),
}

MAX_DELAY_NS = 10_000.0
MAX_PULSE_NS = 500.0
BASE = "https://www.i2u2.org/elab/cosmic"


def protocol_hash() -> str:
    return hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()


def opener() -> urllib.request.OpenerDirector:
    jar = http.cookiejar.CookieJar()
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    op = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(jar),
        urllib.request.HTTPSHandler(context=context),
    )
    login = (
        BASE
        + "/login/login.jsp?"
        + urllib.parse.urlencode(
            {
                "prevPage": BASE + "/data/search.jsp",
                "login": "Login",
                "user": "guest",
                "pass": "guest",
                "project": "cosmic",
            }
        )
    )
    with op.open(login, timeout=60) as response:
        response.read(1024)
    return op


def counter_median(hist: Counter[int]) -> float:
    total = sum(hist.values())
    if not total:
        return float("nan")
    target = (total - 1) / 2
    acc = 0
    for key in sorted(hist):
        acc += hist[key]
        if acc > target:
            return float(key)
    raise RuntimeError("median failure")


def group_pulses(pulses: list[tuple[int, int, int]], gap_sub: int) -> list[list[tuple[int, int, int]]]:
    """Group (rise_sub, width_sub, channel) pulses into time clusters."""
    if not pulses:
        return []
    ordered = sorted(pulses)
    groups = [[ordered[0]]]
    for pulse in ordered[1:]:
        if pulse[0] - groups[-1][-1][0] <= gap_sub:
            groups[-1].append(pulse)
        else:
            groups.append([pulse])
    return groups


def event_candidate(
    pulses: list[tuple[int, int, int]],
    sub_ns: float,
    initial_window_ns: float,
    min_delay_ns: float,
) -> dict | None:
    valid = [p for p in pulses if 0 < p[1] * sub_ns <= MAX_PULSE_NS]
    if not valid:
        return None
    t0 = min(p[0] for p in valid)
    initial_window_sub = int(round(initial_window_ns / sub_ns))
    prompt = [p for p in valid if p[0] - t0 <= initial_window_sub]
    prompt_channels = {p[2] for p in prompt}
    if len(prompt_channels) < 2:
        return None
    tots = [0.0] * 4
    for _, width, ch in prompt:
        tots[ch] += width * sub_ns

    delayed = [
        p
        for p in valid
        if min_delay_ns <= (p[0] - t0) * sub_ns <= MAX_DELAY_NS
        and p[2] in prompt_channels
    ]
    groups = group_pulses(delayed, max(1, int(round(100.0 / sub_ns))))
    if len(groups) != 1:
        return None
    daughter = groups[0]
    delay_ns = (min(p[0] for p in daughter) - t0) * sub_ns
    return {
        "delay_us": delay_ns / 1000.0,
        "tot": tots,
        "multiplicity": len(prompt_channels),
        "prompt_channels": sorted(ch + 1 for ch in prompt_channels),
        "daughter_channels": sorted({p[2] + 1 for p in daughter}),
        "trace": [
            {"t_us": (rise - t0) * sub_ns / 1000.0, "width_ns": width * sub_ns, "channel": ch + 1}
            for rise, width, ch in valid
            if -0.05 <= (rise - t0) * sub_ns / 1000.0 <= 10.05
        ],
    }


def prompt_fourfold(pulses: list[tuple[int, int, int]], sub_ns: float) -> list[int] | None:
    valid = [p for p in pulses if 0 < p[1] * sub_ns <= MAX_PULSE_NS]
    if not valid:
        return None
    t0 = min(p[0] for p in valid)
    window = int(round(100.0 / sub_ns))
    prompt = [p for p in valid if p[0] - t0 <= window]
    channels = {p[2] for p in prompt}
    if channels != {0, 1, 2, 3}:
        return None
    widths = [0] * 4
    for _, width, ch in prompt:
        widths[ch] += width
    return widths if all(w > 0 for w in widths) else None


def prompt_summary(
    pulses: list[tuple[int, int, int]],
    sub_ns: float,
    initial_window_ns: float,
) -> dict | None:
    """Reduce one hardware trigger to its prompt pulse cluster.

    QuarkNet's long lifetime gate is implemented as a second hardware trigger,
    not as a second pulse inside the first trigger record.  The earlier parser
    incorrectly reset at the new-event bit and therefore could never link the
    stopped-muon trigger to its later electron trigger.  This summary preserves
    the absolute trigger-counter time so those two records can be linked while
    streaming.
    """
    valid = [p for p in pulses if 0 < p[1] * sub_ns <= MAX_PULSE_NS]
    if not valid:
        return None
    t0 = min(p[0] for p in valid)
    window_sub = int(round(initial_window_ns / sub_ns))
    prompt = [p for p in valid if p[0] - t0 <= window_sub]
    channels = {p[2] for p in prompt}
    tots = [0.0] * 4
    for _, width, ch in prompt:
        tots[ch] += width * sub_ns
    return {
        "t0_sub": t0,
        "tot": tots,
        "channels0": channels,
        "multiplicity": len(channels),
        "prompt": prompt,
        "daughters": [],
    }


def linked_candidate(initial: dict, daughter: dict, sub_ns: float) -> dict:
    delay_us = (daughter["t0_sub"] - initial["t0_sub"]) * sub_ns / 1000.0
    trace = []
    for pulse, offset in ((p, 0) for p in initial["prompt"]):
        rise, width, ch = pulse
        trace.append(
            {"t_us": (rise - initial["t0_sub"]) * sub_ns / 1000.0,
             "width_ns": width * sub_ns, "channel": ch + 1}
        )
    for rise, width, ch in daughter["prompt"]:
        trace.append(
            {"t_us": (rise - initial["t0_sub"]) * sub_ns / 1000.0,
             "width_ns": width * sub_ns, "channel": ch + 1}
        )
    return {
        "delay_us": delay_us,
        "tot": initial["tot"],
        "multiplicity": initial["multiplicity"],
        "prompt_channels": sorted(ch + 1 for ch in initial["channels0"]),
        "daughter_channels": sorted(ch + 1 for ch in daughter["channels0"]),
        "trace": sorted(trace, key=lambda z: (z["t_us"], z["channel"])),
    }


def process_stream(
    op: urllib.request.OpenerDirector,
    spec: dict,
    max_lines: int | None,
) -> tuple[dict[str, list[dict]], list[Counter[int]], dict]:
    name = spec["name"]
    freq = float(spec["freq"])
    tick_ns = 1e9 / freq
    sub_ns = tick_ns / 32.0
    url = BASE + "/data/download?" + urllib.parse.urlencode(
        {"filename": name, "elab": "cosmic", "type": "split"}
    )
    variants: dict[str, list[dict]] = {key: [] for key in VARIANTS}
    hists = [Counter() for _ in range(4)]
    quality = Counter()
    event_index = -1
    current_pulses: list[tuple[int, int, int]] = []
    pending = [deque() for _ in range(4)]
    start_counter: int | None = None
    start_counter_abs: int | None = None
    last_event_counter: int | None = None
    counter_epoch = 0
    active: dict[str, deque] = {key: deque() for key in VARIANTS}

    def emit(key: str, initial: dict) -> None:
        if len(initial["daughters"]) != 1:
            if len(initial["daughters"]) > 1:
                quality[f"rejected_multiple_daughters_{key}"] += 1
            return
        item = linked_candidate(initial, initial["daughters"][0], sub_ns)
        item.update({"file": name, "split": spec["split"], "event_index": initial["event_index"]})
        variants[key].append(item)
        quality[f"candidate_{key}"] += 1

    def register_summary(key: str, summary: dict) -> None:
        _, min_delay_ns = VARIANTS[key]
        min_delay_sub = int(round(min_delay_ns / sub_ns))
        max_delay_sub = int(round(MAX_DELAY_NS / sub_ns))
        queue = active[key]
        while queue and summary["t0_sub"] - queue[0]["t0_sub"] > max_delay_sub:
            emit(key, queue.popleft())
        for initial in queue:
            dt = summary["t0_sub"] - initial["t0_sub"]
            if min_delay_sub <= dt <= max_delay_sub and initial["channels0"] & summary["channels0"]:
                initial["daughters"].append(summary)
        if summary["multiplicity"] >= 2:
            summary["event_index"] = event_index
            queue.append(summary)

    def finish_event() -> None:
        nonlocal current_pulses, pending, event_index
        if event_index < 0:
            return
        quality["events"] += 1
        ff = prompt_fourfold(current_pulses, sub_ns)
        if ff is not None and spec["split"] == "calibration":
            quality["calibration_fourfold"] += 1
            for ch, width_sub in enumerate(ff):
                hists[ch][width_sub] += 1
        for key, (window_ns, _) in VARIANTS.items():
            summary = prompt_summary(current_pulses, sub_ns, window_ns)
            if summary is not None:
                register_summary(key, summary)

    request = urllib.request.Request(url, headers={"User-Agent": "ARA-T379-reproduction/1.0"})
    started = time.time()
    print(f"STREAM {name} ({spec['split']})", flush=True)
    with op.open(request, timeout=120) as response:
        for line_no, raw in enumerate(response, start=1):
            if max_lines and line_no > max_lines:
                break
            try:
                parts = raw.decode("ascii", "ignore").strip().split()
                if len(parts) < 9:
                    quality["short_lines"] += 1
                    continue
                counter = int(parts[0], 16)
                words = [int(x, 16) for x in parts[1:9]]
            except ValueError:
                quality["parse_errors"] += 1
                continue

            is_new = bool(words[0] & 0x80)
            if is_new:
                finish_event()
                event_index += 1
                current_pulses = []
                pending = [deque() for _ in range(4)]
                start_counter = counter
                if last_event_counter is not None and counter < last_event_counter and last_event_counter - counter > 0x80000000:
                    counter_epoch += 1 << 32
                last_event_counter = counter
                start_counter_abs = counter_epoch + counter
            if start_counter is None:
                continue
            rel_counter = (counter - start_counter) & 0xFFFFFFFF
            if rel_counter > 1_000_000:
                quality["counter_wrap_errors"] += 1
                continue
            base_sub = (start_counter_abs + rel_counter) * 32

            for ch in range(4):
                re_word = words[2 * ch]
                fe_word = words[2 * ch + 1]
                edges = []
                if re_word & 0x20:
                    edges.append((base_sub + (re_word & 0x1F), "rise"))
                if fe_word & 0x20:
                    edges.append((base_sub + (fe_word & 0x1F), "fall"))
                for edge_time, kind in sorted(edges):
                    if kind == "rise":
                        pending[ch].append(edge_time)
                    elif pending[ch]:
                        rise = pending[ch].popleft()
                        width = edge_time - rise
                        if width > 0:
                            current_pulses.append((rise, width, ch))
                        else:
                            quality["nonpositive_width"] += 1
                    else:
                        quality["unmatched_falls"] += 1

            if line_no % 250_000 == 0:
                elapsed = time.time() - started
                print(
                    f"  {name}: {line_no:,} lines, {quality['events']:,} events, "
                    f"{quality['candidate_main']:,} clean linked candidates, {elapsed:.1f}s",
                    flush=True,
                )
    finish_event()
    for key, queue in active.items():
        while queue:
            emit(key, queue.popleft())
    quality["lines"] = line_no if "line_no" in locals() else 0
    quality["seconds"] = round(time.time() - started, 3)
    print(
        f"DONE {name}: {quality['lines']:,} lines, {quality['events']:,} events, "
        f"{quality['candidate_main']:,} main candidates",
        flush=True,
    )
    return variants, hists, dict(quality)


def add_features(rows: list[dict], medians_ns: np.ndarray) -> list[dict]:
    output = []
    for row in rows:
        q = np.asarray(row["tot"], float) / medians_ns
        total = float(q.sum())
        if not np.isfinite(total) or total <= 0:
            continue
        upper = float(q[0] + q[1])
        lower = float(q[2] + q[3])
        x = 2.0 * lower / total
        depth = 2.0 * float(np.dot(np.arange(4), q)) / (3.0 * total)
        wrong_a = float(q[0] + q[2])
        wrong_b = float(q[1] + q[3])
        x_wrong = 2.0 * wrong_b / max(wrong_a + wrong_b, 1e-12)
        item = dict(row)
        item.update(
            {
                "q1": float(q[0]), "q2": float(q[1]), "q3": float(q[2]), "q4": float(q[3]),
                "Q": total, "x_mu": x, "s": x - 1.0, "a": abs(x - 1.0),
                "depth": depth, "x_wrong": x_wrong,
            }
        )
        output.append(item)
    return output


class Model:
    def __init__(self, kind: str, lower: float = 0.3, upper: float = 10.0):
        self.kind = kind
        self.lower = lower
        self.upper = upper
        self.mean = None
        self.std = None
        self.theta = None

    def raw(self, rows: list[dict]) -> np.ndarray:
        n = len(rows)
        if self.kind == "M0":
            return np.empty((n, 0))
        base = np.column_stack(
            [
                np.log(np.maximum([r["Q"] for r in rows], 1e-12)),
                [r["multiplicity"] for r in rows],
                [r["depth"] for r in rows],
            ]
        )
        if self.kind == "MG":
            return base
        if self.kind == "MA":
            return np.column_stack(
                [base, [r["s"] for r in rows], [r["a"] for r in rows], [r["s"] * r["depth"] for r in rows]]
            )
        if self.kind == "ML50":
            return np.column_stack([base, [abs(r["x_mu"] - 0.50) <= 0.05 for r in rows]])
        if self.kind == "MW":
            return np.column_stack(
                [
                    base,
                    [r["x_wrong"] - 1.0 for r in rows],
                    [abs(r["x_wrong"] - 1.0) for r in rows],
                    [(r["x_wrong"] - 1.0) * r["depth"] for r in rows],
                ]
            )
        raise ValueError(self.kind)

    def design(self, rows: list[dict], fit: bool = False) -> np.ndarray:
        raw = self.raw(rows)
        if raw.shape[1] == 0:
            return np.ones((len(rows), 1))
        if fit:
            self.mean = raw.mean(axis=0)
            self.std = raw.std(axis=0)
            self.std[self.std < 1e-9] = 1.0
        z = (raw - self.mean) / self.std
        return np.column_stack([np.ones(len(rows)), z])

    def losses_for(self, theta: np.ndarray, X: np.ndarray, delay: np.ndarray) -> np.ndarray:
        lower, upper = self.lower, self.upper
        width = upper - lower
        beta, gamma = theta[:-1], theta[-1]
        eta = np.clip(X @ beta, -5.0, 3.5)
        lam = np.exp(eta)
        u = np.clip(delay - lower, 0, width)
        log_norm = np.log(-np.expm1(-lam * width))
        log_exp = eta - lam * u - log_norm
        bg = 1.0 / (1.0 + np.exp(-gamma))
        return -logsumexp(
            np.vstack([np.log1p(-bg) + log_exp, np.log(bg) - math.log(width) + np.zeros_like(log_exp)]),
            axis=0,
        )

    def fit(self, rows: list[dict]) -> "Model":
        X = self.design(rows, fit=True)
        delay = np.asarray([r["delay_us"] for r in rows], float)
        x0 = np.zeros(X.shape[1] + 1)
        x0[0] = math.log(1 / 2.1)
        x0[-1] = -3.0

        def objective(theta: np.ndarray) -> float:
            losses = self.losses_for(theta, X, delay)
            penalty = 1e-3 * float(np.sum(theta[1:-1] ** 2))
            return float(losses.sum() + penalty)

        res = minimize(objective, x0, method="L-BFGS-B", options={"maxiter": 700, "ftol": 1e-11})
        if not res.success:
            print(f"WARNING {self.kind} fit: {res.message}", flush=True)
        self.theta = np.asarray(res.x)
        return self

    def losses(self, rows: list[dict], delay_override: np.ndarray | None = None) -> np.ndarray:
        X = self.design(rows, fit=False)
        delay = np.asarray([r["delay_us"] for r in rows], float) if delay_override is None else delay_override
        return self.losses_for(self.theta, X, delay)

    def rate(self, rows: list[dict]) -> np.ndarray:
        X = self.design(rows, fit=False)
        return np.exp(np.clip(X @ self.theta[:-1], -5.0, 3.5))


def block_bootstrap_delta(rows: list[dict], delta: np.ndarray, nboot: int = 10_000) -> dict:
    blocks = []
    for filename in sorted({r["file"] for r in rows}):
        idx = np.array([i for i, r in enumerate(rows) if r["file"] == filename], int)
        for block in np.array_split(idx, 6):
            if len(block):
                blocks.append(float(delta[block].mean()))
    rng = np.random.default_rng(379)
    arr = np.asarray(blocks)
    boot = arr[rng.integers(0, len(arr), size=(nboot, len(arr)))].mean(axis=1)
    return {
        "blocks": blocks,
        "mean": float(delta.mean()),
        "ci95": [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))],
    }


def evaluate(rows: list[dict], lower: float = 0.3) -> tuple[dict, dict[str, Model]]:
    cal = [r for r in rows if r["split"] == "calibration"]
    hold = [r for r in rows if r["split"] == "holdout"]
    if min(len(cal), len(hold)) < 50:
        raise RuntimeError(f"Too few candidates: calibration={len(cal)}, holdout={len(hold)}")
    models = {kind: Model(kind, lower=lower).fit(cal) for kind in ("M0", "MG", "MA", "MW", "ML50")}
    losses = {kind: models[kind].losses(hold) for kind in models}
    delta = losses["MG"] - losses["MA"]
    boot = block_bootstrap_delta(hold, delta)
    landmark_delta = losses["MG"] - losses["ML50"]
    landmark_boot = block_bootstrap_delta(hold, landmark_delta)

    by_run = {}
    for filename in sorted({r["file"] for r in hold}):
        idx = np.array([i for i, r in enumerate(hold) if r["file"] == filename], int)
        by_run[filename] = {
            "n": int(len(idx)),
            "mean_nll": {kind: float(losses[kind][idx].mean()) for kind in models},
            "delta_MG_minus_MA": float(delta[idx].mean()),
            "delta_MG_minus_ML50": float(landmark_delta[idx].mean()),
        }

    rng = np.random.default_rng(379)
    perm_deltas = []
    perm_landmark_deltas = []
    original_delay = np.asarray([r["delay_us"] for r in hold])
    run_indices = {
        filename: np.array([i for i, r in enumerate(hold) if r["file"] == filename], int)
        for filename in sorted({r["file"] for r in hold})
    }
    for _ in range(500):
        perm = original_delay.copy()
        for idx in run_indices.values():
            perm[idx] = rng.permutation(perm[idx])
        perm_deltas.append(float((models["MG"].losses(hold, perm) - models["MA"].losses(hold, perm)).mean()))
        perm_landmark_deltas.append(float((models["MG"].losses(hold, perm) - models["ML50"].losses(hold, perm)).mean()))

    landmarks = []
    mg_rate = models["MG"].rate(hold)
    ma_rate = models["MA"].rate(hold)
    for center in (0.50, 0.75, 1.00, 1.25, 1.50):
        mask = np.array([abs(r["x_mu"] - center) <= 0.05 for r in hold])
        landmarks.append(
            {
                "center": center,
                "n": int(mask.sum()),
                "fraction": float(mask.mean()),
                "mean_delay_us": float(np.mean(original_delay[mask])) if mask.any() else None,
                "median_delay_us": float(np.median(original_delay[mask])) if mask.any() else None,
                "mean_MG_rate_per_us": float(np.mean(mg_rate[mask])) if mask.any() else None,
                "mean_MA_rate_per_us": float(np.mean(ma_rate[mask])) if mask.any() else None,
            }
        )

    supported = (
        all(v["delta_MG_minus_MA"] > 0 for v in by_run.values())
        and boot["ci95"][0] > 0
        and float(np.mean(perm_deltas)) < boot["mean"]
    )
    # The last standardised coefficient belongs to the frozen x=0.50 window;
    # positive means a higher decay hazard / earlier linked daughter.
    landmark_higher_hazard = bool(models["ML50"].theta[-2] > 0)
    landmark_supported = (
        landmark_higher_hazard
        and all(v["delta_MG_minus_ML50"] > 0 for v in by_run.values())
        and landmark_boot["ci95"][0] > 0
    )
    result = {
        "n_calibration": len(cal),
        "n_holdout": len(hold),
        "mean_nll": {kind: float(losses[kind].mean()) for kind in models},
        "by_run": by_run,
        "bootstrap": boot,
        "landmark_0_50_test": {
            "calibration_direction_higher_hazard": landmark_higher_hazard,
            "calibration_standardised_log_rate_coefficient": float(models["ML50"].theta[-2]),
            "bootstrap": landmark_boot,
            "verdict": "SUPPORTED" if landmark_supported else "NOT SUPPORTED",
        },
        "permutation": {
            "replicates": len(perm_deltas),
            "mean_delta": float(np.mean(perm_deltas)),
            "ci95": [float(np.quantile(perm_deltas, 0.025)), float(np.quantile(perm_deltas, 0.975))],
            "landmark_mean_delta": float(np.mean(perm_landmark_deltas)),
            "landmark_ci95": [float(np.quantile(perm_landmark_deltas, 0.025)), float(np.quantile(perm_landmark_deltas, 0.975))],
        },
        "landmarks": landmarks,
        "individual_advance_information": "SUPPORTED" if supported else "NOT SUPPORTED",
        "fitted_uniform_background_fraction": {
            kind: float(1.0 / (1.0 + np.exp(-model.theta[-1]))) for kind, model in models.items()
        },
    }
    return result, models


def save_event_csv(rows: list[dict], path: Path) -> None:
    fields = [
        "split", "file", "event_index", "delay_us", "multiplicity", "prompt_channels", "daughter_channels",
        "q1", "q2", "q3", "q4", "Q", "x_mu", "s", "a", "depth", "x_wrong",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row[k] for k in fields})


def make_figure(rows: list[dict], result: dict, path_png: Path, path_svg: Path) -> list[dict]:
    hold = [r for r in rows if r["split"] == "holdout"]
    rng = np.random.default_rng(379)
    sampled = hold if len(hold) <= 4000 else [hold[i] for i in rng.choice(len(hold), 4000, replace=False)]

    fig = plt.figure(figsize=(17, 13), constrained_layout=True)
    gs = fig.add_gridspec(3, 2)

    ax = fig.add_subplot(gs[0, 0])
    ax.scatter([r["x_mu"] for r in sampled], [r["delay_us"] for r in sampled], s=7, alpha=0.24, color="#4c83c3")
    for x, color in [(0.5, "#d79a2b"), (0.75, "#ad7bcb"), (1.0, "#3aa66f"), (1.25, "#ad7bcb"), (1.5, "#d79a2b")]:
        ax.axvline(x, color=color, linestyle="--", linewidth=1.3)
    ax.set(xlim=(0, 2), ylim=(0.3, 10), xlabel="incoming child ARA x_mu = 2B/(A+B)", ylabel="linked daughter delay (microseconds)", title="Individual held-out muons")

    ax = fig.add_subplot(gs[0, 1])
    bins = np.linspace(0, 2, 41)
    ax.hist([r["x_mu"] for r in hold], bins=bins, color="#5d8fc7", alpha=0.82)
    ax.set(xlim=(0, 2), xlabel="incoming child ARA x_mu", ylabel="held-out individual muons per 0.05 bin", title="Where individual events occupy the ARA line")
    ax.axvline(1.0, color="#3aa66f", linewidth=1.5)

    ax = fig.add_subplot(gs[1, 0])
    labels = ["memoryless M0", "ordinary MG", "ARA MA", "wrong-pair MW", "landmark ML50"]
    vals = [result["mean_nll"][k] for k in ("M0", "MG", "MA", "MW", "ML50")]
    ax.bar(labels, vals, color=["#9aa5b1", "#6d99c7", "#44b481", "#c78383", "#d7a23f"])
    ax.set_ylabel("held-out mean negative log likelihood (lower is better)")
    ax.set_title("Prospective individual-event score")
    ax.tick_params(axis="x", rotation=15)
    for i, value in enumerate(vals):
        ax.text(i, value, f"{value:.5f}", ha="center", va="bottom", fontsize=9)

    ax = fig.add_subplot(gs[1, 1])
    centers = [x["center"] for x in result["landmarks"]]
    medians = [x["median_delay_us"] if x["median_delay_us"] is not None else np.nan for x in result["landmarks"]]
    counts = [x["n"] for x in result["landmarks"]]
    ax.plot(centers, medians, marker="o", color="#d79a2b", linewidth=2)
    ax.set(xlim=(0.4, 1.6), xlabel="frozen ARA landmark center", ylabel="held-out median daughter delay (microseconds)", title="Frozen landmark windows (±0.05)")
    for x, y, n in zip(centers, medians, counts):
        if np.isfinite(y):
            ax.annotate(f"n={n}", (x, y), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=8)

    ax = fig.add_subplot(gs[2, 0])
    ax.scatter([r["depth"] for r in sampled], [r["x_mu"] for r in sampled], s=7, alpha=0.22, color="#8467b0")
    ax.set(xlim=(0, 2), ylim=(0, 2), xlabel="ordinary prompt depth centroid (0=top, 2=bottom)", ylabel="ARA child relation x_mu", title="ARA relation versus ordinary stack geometry")
    ax.plot([0, 2], [0, 2], linestyle="--", color="#7c8793", linewidth=1)

    # Fixed visual examples: earliest four and latest four qualifying holdout events.
    ordered = sorted(hold, key=lambda r: (r["file"], r["event_index"]))
    examples = (ordered[:4] + ordered[-4:]) if len(ordered) >= 8 else ordered
    ax = fig.add_subplot(gs[2, 1])
    y = np.arange(len(examples))
    for i, row in enumerate(examples):
        for pulse in row["trace"]:
            color = ["#4c83c3", "#3aa66f", "#d79a2b", "#b05c96"][pulse["channel"] - 1]
            ax.scatter(pulse["t_us"], i, s=18 + 1.4 * pulse["width_ns"], color=color, alpha=0.72, edgecolors="none")
        ax.text(10.15, i, f"x={row['x_mu']:.3f}, t={row['delay_us']:.3f} us", va="center", fontsize=8)
    ax.set(xlim=(-0.1, 12.2), xlabel="time since incoming pulse (microseconds)", ylabel="fixed-rule individual event", title="Eight individual linked pulse histories (marker size = ToT)")
    ax.set_yticks(y, [f"{r['file'][-6:]} #{r['event_index']}" for r in examples])
    ax.axvline(0, color="#222", linewidth=1)

    fig.suptitle("T379 — individual-muon ARA child handover", fontsize=20, fontweight="bold")
    fig.savefig(path_png, dpi=180)
    fig.savefig(path_svg)
    plt.close(fig)
    return examples


def fmt(value, digits=6):
    if value is None:
        return "—"
    return f"{value:.{digits}f}" if isinstance(value, float) else str(value)


def write_html(result: dict, quality: dict, medians: list[float], examples: list[dict]) -> None:
    rows = "".join(
        f"<tr><td>{x['center']:.2f}</td><td>{x['n']:,}</td><td>{x['fraction']:.3%}</td>"
        f"<td>{fmt(x['median_delay_us'],3)}</td><td>{fmt(x['mean_delay_us'],3)}</td>"
        f"<td>{fmt(x['mean_MG_rate_per_us'],4)}</td><td>{fmt(x['mean_MA_rate_per_us'],4)}</td></tr>"
        for x in result["landmarks"]
    )
    runs = "".join(
        f"<tr><td>{html.escape(name)}</td><td>{r['n']:,}</td><td>{r['mean_nll']['MG']:.6f}</td>"
        f"<td>{r['mean_nll']['MA']:.6f}</td><td>{r['delta_MG_minus_MA']:+.6f}</td></tr>"
        for name, r in result["by_run"].items()
    )
    qrows = "".join(
        f"<tr><td>{html.escape(name)}</td><td>{q.get('lines',0):,}</td><td>{q.get('events',0):,}</td>"
        f"<td>{q.get('candidate_main',0):,}</td><td>{q.get('parse_errors',0):,}</td></tr>"
        for name, q in quality.items()
    )
    verdict = result["individual_advance_information"]
    color = "#61d69b" if verdict == "SUPPORTED" else "#f1b15b"
    page = f"""<!doctype html><html><head><meta charset='utf-8'><title>T379 individual muon child handover</title>
<style>body{{margin:0;background:#0b1017;color:#e8eef7;font:16px system-ui}}main{{max-width:1320px;margin:auto;padding:28px}}.hero,.card{{background:#131b27;border:1px solid #2a394e;border-radius:16px;padding:22px;margin:16px 0}}h1,h2{{margin-top:0}}.verdict{{font-size:32px;font-weight:850;color:{color}}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:14px}}table{{width:100%;border-collapse:collapse}}th,td{{text-align:left;padding:8px;border-bottom:1px solid #2b394d}}code{{color:#8ec5ff}}img{{width:100%;height:auto;border-radius:12px;background:white}}.note{{color:#b8c5d5}}a{{color:#8ec5ff}}</style></head>
<body><main><section class='hero'><h1>T379 — individual-muon child handover</h1><div class='verdict'>Individual advance information: {verdict}</div>
<p>{result['n_calibration']:,} calibration and {result['n_holdout']:,} untouched held-out linked events.</p>
<p>Frozen protocol SHA-256: <code>{EXPECTED_PROTOCOL_SHA256}</code></p></section>
<section class='card'><h2>How to read the test</h2><div class='grid'><p><b>Phase A</b><br>Gain-normalised prompt pulse strength in upper counters 1+2.</p><p><b>Phase B</b><br>Gain-normalised prompt pulse strength in lower counters 3+4.</p><p><b>ARA x_mu</b><br><code>2B/(A+B)</code>. 0 = purely upper, 1 = equal, 2 = purely lower.</p><p><b>Outcome</b><br>Microseconds until the one later electron-candidate cluster in the same detector event.</p></div>
<p class='note'>The detector sees the charged electron in a later linked hardware trigger. The neutrinos are created in the same decay but are not directly timed here.</p></section>
<section class='card'><img src='T379_INDIVIDUAL_MUON_CHILD_HANDOVER_FIGURE.png' alt='Six fully labelled T379 result panels'></section>
<section class='card'><h2>Prospective scores</h2><table><tr><th>model</th><th>held-out mean NLL (lower better)</th></tr>
{''.join(f'<tr><td>{k}</td><td>{v:.7f}</td></tr>' for k,v in result['mean_nll'].items())}</table>
<p>ARA improvement over ordinary geometry: <b>{result['bootstrap']['mean']:+.7f}</b>; chronological-block 95% interval <b>{result['bootstrap']['ci95'][0]:+.7f} to {result['bootstrap']['ci95'][1]:+.7f}</b>.</p>
<p>Within-run outcome-permutation delta: mean {result['permutation']['mean_delta']:+.7f}, 95% range {result['permutation']['ci95'][0]:+.7f} to {result['permutation']['ci95'][1]:+.7f}.</p></section>
<section class='card'><h2>Separate frozen x=0.50 landmark gate</h2><p class='verdict'>{result['landmark_0_50_test']['verdict']}</p><p>Calibration direction higher hazard: <b>{result['landmark_0_50_test']['calibration_direction_higher_hazard']}</b>; ordinary-minus-landmark held-out delta <b>{result['landmark_0_50_test']['bootstrap']['mean']:+.7f}</b>, chronological-block 95% interval <b>{result['landmark_0_50_test']['bootstrap']['ci95'][0]:+.7f} to {result['landmark_0_50_test']['bootstrap']['ci95'][1]:+.7f}</b>.</p></section>
<section class='card'><h2>Each untouched run</h2><table><tr><th>run</th><th>n</th><th>ordinary MG</th><th>ARA MA</th><th>MG−MA</th></tr>{runs}</table></section>
<section class='card'><h2>Frozen landmarks</h2><table><tr><th>x</th><th>n</th><th>share</th><th>median delay us</th><th>mean delay us</th><th>ordinary rate/us</th><th>ARA rate/us</th></tr>{rows}</table></section>
<section class='card'><h2>Data quality</h2><p>Calibration-only fourfold ToT medians (ns): {', '.join(f'ch{i+1}={v:.3f}' for i,v in enumerate(medians))}.</p><table><tr><th>file</th><th>raw lines</th><th>events</th><th>clean linked candidates</th><th>parse errors</th></tr>{qrows}</table></section>
<section class='card'><h2>Boundary</h2><p>This test asks whether one incoming muon's prompt child relation improves the prospective timing distribution of its own later visible daughter. It does not directly observe either neutrino and cannot turn an intrinsically stochastic decay into an exact timestamp unless the data contain reproducible advance information.</p></section>
</main></body></html>"""
    (OUT / "T379_INDIVIDUAL_MUON_CHILD_HANDOVER.html").write_text(page, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-lines", type=int, default=None, help="Schema/debug limit per source file")
    args = parser.parse_args()
    digest = protocol_hash()
    if digest != EXPECTED_PROTOCOL_SHA256:
        raise RuntimeError(f"Protocol hash changed: {digest}")
    OUT.mkdir(parents=True, exist_ok=True)
    op = opener()
    all_variants = {key: [] for key in VARIANTS}
    all_hists = [Counter() for _ in range(4)]
    quality = {}
    for spec in FILES:
        variants, hists, q = process_stream(op, spec, args.max_lines)
        quality[spec["name"]] = q
        for key in VARIANTS:
            all_variants[key].extend(variants[key])
        for ch in range(4):
            all_hists[ch].update(hists[ch])

    # Histograms are in 1/32-clock subcounts. Calibration frequencies differ by
    # less than 0.1 ppm, so the shared 1.25 ns conversion is adequate for gain
    # normalisation while exact per-run conversions were used for event times.
    median_sub = np.array([counter_median(h) for h in all_hists])
    median_ns = median_sub * (1e9 / (25_000_001.0 * 32.0))
    if not np.all(np.isfinite(median_ns)):
        raise RuntimeError(f"Missing calibration medians: {median_ns}")

    featured = {key: add_features(rows, median_ns) for key, rows in all_variants.items()}
    result, _ = evaluate(featured["main"])
    sensitivities = {}
    for key, rows in featured.items():
        variant_result, _ = evaluate(rows, lower=VARIANTS[key][1] / 1000.0)
        sensitivities[key] = {
            "n_calibration": variant_result["n_calibration"],
            "n_holdout": variant_result["n_holdout"],
            "delta_MG_minus_MA": variant_result["bootstrap"]["mean"],
            "ci95": variant_result["bootstrap"]["ci95"],
            "verdict": variant_result["individual_advance_information"],
        }
    result["cut_sensitivity"] = sensitivities
    result["protocol_sha256"] = digest
    result["source"] = "QuarkNet Cosmic Ray e-Lab detector 6845"
    result["channel_medians_ns"] = median_ns.tolist()

    save_event_csv(featured["main"], OUT / "T379_INDIVIDUAL_MUON_CHILD_HANDOVER_EVENTS.csv")
    examples = make_figure(
        featured["main"], result,
        OUT / "T379_INDIVIDUAL_MUON_CHILD_HANDOVER_FIGURE.png",
        OUT / "T379_INDIVIDUAL_MUON_CHILD_HANDOVER_FIGURE.svg",
    )
    write_html(result, quality, median_ns.tolist(), examples)
    (OUT / "T379_INDIVIDUAL_MUON_CHILD_HANDOVER_RESULTS.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    validation = {
        "protocol_sha256": digest,
        "quality": quality,
        "variant_counts": {key: len(rows) for key, rows in featured.items()},
        "source_files": FILES,
    }
    (OUT / "T379_INDIVIDUAL_MUON_CHILD_HANDOVER_VALIDATION.json").write_text(
        json.dumps(validation, indent=2), encoding="utf-8"
    )
    print(json.dumps({
        "verdict": result["individual_advance_information"],
        "n_calibration": result["n_calibration"],
        "n_holdout": result["n_holdout"],
        "delta": result["bootstrap"],
        "html": str(OUT / "T379_INDIVIDUAL_MUON_CHILD_HANDOVER.html"),
    }, indent=2), flush=True)


if __name__ == "__main__":
    main()
