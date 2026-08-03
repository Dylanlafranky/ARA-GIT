#!/usr/bin/env python3
"""Q60 frozen test: ordered Ramsey phase advance versus the ARA Phi step."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).parent / ".mplconfig"))

import matplotlib.pyplot as plt
import numpy as np
from scipy.io import loadmat
from scipy.optimize import curve_fit


HERE = Path(__file__).resolve().parent
SOURCE = (
    HERE
    / "public_data"
    / "extracted"
    / "AllopticalSCQreadout_data"
    / "Fig_4b"
    / "T2_errorbars"
)
PROTOCOL = HERE / "Q60_RAMSEY_VERTICAL_PHI_PHASE_ADVANCE_PROTOCOL_v1_FROZEN.md"
PHASES_OUT = HERE / "Q60_RAMSEY_VERTICAL_PHI_PHASE_ADVANCE_PHASES.csv.gz"
SCORES_OUT = HERE / "Q60_RAMSEY_VERTICAL_PHI_PHASE_ADVANCE_SCORES.csv"
LAGS_OUT = HERE / "Q60_RAMSEY_VERTICAL_PHI_PHASE_ADVANCE_LAGS.csv"
RESULT_OUT = HERE / "Q60_RAMSEY_VERTICAL_PHI_PHASE_ADVANCE_RESULTS.json"
FIG_OUT = HERE / "Q60_RAMSEY_VERTICAL_PHI_PHASE_ADVANCE.png"
SVG_OUT = HERE / "Q60_RAMSEY_VERTICAL_PHI_PHASE_ADVANCE.svg"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
CANDIDATES = {
    "phi_2_over_phi": 2.0 / PHI,
    "rational_26_over_21": 26.0 / 21.0,
    "rational_5_over_4": 5.0 / 4.0,
    "anti_phi_orientation": 2.0 - 2.0 / PHI,
    "two_over_e": 2.0 / math.e,
    "one_over_e": 1.0 / math.e,
    "sqrt_2": math.sqrt(2.0),
    "persistence": 0.0,
}
EXPECTED_PROTOCOL_SHA256 = "68701DE96A6539D2B4A9BB3DB59A7BF2D874B868C5134B8766741C37AEFCF598"
BOOT_DRAWS = 5000
SHUFFLE_DRAWS = 1999
BOOT_BLOCK = 50
SEED = 60032026
FIB_LAGS = (1, 2, 3, 5, 8, 13, 21)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def circular_signed(x: np.ndarray | float) -> np.ndarray:
    return (np.asarray(x) + 1.0) % 2.0 - 1.0


def circular_loss(x: np.ndarray, target: float) -> np.ndarray:
    return np.abs(circular_signed(x - target))


def circular_mean_ara(x: np.ndarray) -> tuple[float, float]:
    z = np.mean(np.exp(1j * np.pi * np.asarray(x)))
    return float((np.angle(z) / np.pi) % 2.0), float(abs(z))


def damped_cosine(t: np.ndarray, offset: float, amp: float, tau: float, omega: float, phase: float) -> np.ndarray:
    return offset + amp * np.exp(-t / tau) * np.cos(omega * t - phase)


def fit_file(path: Path, split: str) -> dict:
    source = loadmat(path)
    I = np.squeeze(np.asarray(source["I"], dtype=float))
    Q = np.squeeze(np.asarray(source["Q"], dtype=float))
    t = np.squeeze(np.asarray(source["t_ns"], dtype=float))
    if I.shape != Q.shape or I.ndim != 2 or I.shape[1] != len(t):
        raise RuntimeError(f"Unexpected schema in {path.name}: I={I.shape}, Q={Q.shape}, t={t.shape}")
    order = np.argsort(t)
    t = t[order]
    I = I[:, order]
    Q = Q[:, order]
    t = t - t.min()

    mean_iq = np.column_stack([I.mean(axis=0), Q.mean(axis=0)])
    centred = mean_iq - mean_iq.mean(axis=0, keepdims=True)
    _, _, vh = np.linalg.svd(centred, full_matrices=False)
    direction = vh[0]
    if direction[0] < 0:
        direction = -direction
    Y = I * direction[0] + Q * direction[1]
    mean_y = Y.mean(axis=0)

    dt = float(np.median(np.diff(t)))
    span = float(t.max() - t.min())
    centred_y = mean_y - mean_y.mean()
    freqs = np.fft.rfftfreq(len(t), d=dt)
    spectrum = np.abs(np.fft.rfft(centred_y))
    peak_idx = int(np.argmax(spectrum[1:]) + 1)
    omega0 = 2.0 * np.pi * freqs[peak_idx]
    amp0 = max(float(np.ptp(mean_y) / 2.0), np.finfo(float).eps)
    tau0 = max(span / 2.0, dt)
    p0 = [float(mean_y.mean()), amp0, tau0, omega0, 0.0]
    lower = [-np.inf, 0.0, dt / 10.0, max(omega0 * 0.5, 1e-12), -4.0 * np.pi]
    upper = [np.inf, amp0 * 20.0, span * 100.0, omega0 * 1.5, 4.0 * np.pi]
    popt, _ = curve_fit(
        damped_cosine,
        t,
        mean_y,
        p0=p0,
        bounds=(lower, upper),
        maxfev=100000,
    )
    fit_y = damped_cosine(t, *popt)
    sse = float(np.sum((mean_y - fit_y) ** 2))
    sst = float(np.sum((mean_y - mean_y.mean()) ** 2))
    r2 = 1.0 - sse / sst if sst > 0 else float("nan")
    _, _, tau, omega, _ = popt

    envelope = np.exp(-t / tau)
    design = np.column_stack([np.ones_like(t), envelope * np.cos(omega * t), envelope * np.sin(omega * t)])
    pinv_t = np.linalg.pinv(design).T
    beta = Y @ pinv_t
    fitted = beta @ design.T
    resid = Y - fitted
    sweep_sst = np.sum((Y - Y.mean(axis=1, keepdims=True)) ** 2, axis=1)
    sweep_sse = np.sum(resid**2, axis=1)
    sweep_r2 = np.where(sweep_sst > 0, 1.0 - sweep_sse / sweep_sst, np.nan)
    amp = np.hypot(beta[:, 1], beta[:, 2])
    phase = np.mod(np.arctan2(beta[:, 2], beta[:, 1]), 2.0 * np.pi)
    x = phase / np.pi
    steps = np.mod(np.diff(x), 2.0)

    return {
        "path": path,
        "file": path.name,
        "split": split,
        "t": t,
        "mean_y": mean_y,
        "fit_y": fit_y,
        "direction": direction,
        "tau": float(tau),
        "omega": float(omega),
        "r2": float(r2),
        "x": x,
        "steps": steps,
        "amplitude": amp,
        "sweep_r2": sweep_r2,
    }


def equal_file_score(files: list[dict], candidate: float, lag: int = 1) -> float:
    medians = []
    for item in files:
        d = np.mod(item["x"][lag:] - item["x"][:-lag], 2.0)
        medians.append(float(np.median(circular_loss(d, (lag * candidate) % 2.0))))
    return float(np.mean(medians))


def previous_velocity_score(files: list[dict]) -> float:
    medians = []
    for item in files:
        d = item["steps"]
        medians.append(float(np.median(circular_loss(d[1:], d[:-1]))))
    return float(np.mean(medians))


def split_circular_mean(files: list[dict]) -> tuple[float, float]:
    phasors = []
    for item in files:
        phasors.append(np.mean(np.exp(1j * np.pi * item["steps"])))
    z = np.mean(phasors)
    return float((np.angle(z) / np.pi) % 2.0), float(abs(z))


def resample_blocks(values: np.ndarray, rng: np.random.Generator, block: int = BOOT_BLOCK) -> np.ndarray:
    n = len(values)
    pieces = []
    while sum(len(piece) for piece in pieces) < n:
        start = int(rng.integers(0, max(1, n - block + 1)))
        pieces.append(values[start : start + block])
    return np.concatenate(pieces)[:n]


def bootstrap_split(files: list[dict]) -> dict:
    rng = np.random.default_rng(SEED)
    point, _ = split_circular_mean(files)
    means = np.empty(BOOT_DRAWS)
    diffs = np.empty(BOOT_DRAWS)
    c_phi = CANDIDATES["phi_2_over_phi"]
    c_rat = CANDIDATES["rational_26_over_21"]
    for b in range(BOOT_DRAWS):
        samples = [resample_blocks(item["steps"], rng) for item in files]
        z = np.mean([np.mean(np.exp(1j * np.pi * sample)) for sample in samples])
        means[b] = (np.angle(z) / np.pi) % 2.0
        phi_loss = np.mean([np.median(circular_loss(sample, c_phi)) for sample in samples])
        rat_loss = np.mean([np.median(circular_loss(sample, c_rat)) for sample in samples])
        diffs[b] = phi_loss - rat_loss
    delta = circular_signed(means - point)
    ci_delta = np.quantile(delta, [0.025, 0.975])
    ci_unwrapped = [float(point + ci_delta[0]), float(point + ci_delta[1])]
    return {
        "point": point,
        "mean_ci_unwrapped": ci_unwrapped,
        "mean_ci_width": float(ci_delta[1] - ci_delta[0]),
        "phi_minus_26_21_ci": [float(x) for x in np.quantile(diffs, [0.025, 0.975])],
        "phi_minus_26_21_point": float(
            equal_file_score(files, c_phi) - equal_file_score(files, c_rat)
        ),
    }


def shuffle_control(files: list[dict], fitted: float) -> dict:
    rng = np.random.default_rng(SEED + 1)
    observed = equal_file_score(files, fitted)
    scores = np.empty(SHUFFLE_DRAWS)
    for draw in range(SHUFFLE_DRAWS):
        medians = []
        for item in files:
            perm = rng.permutation(item["x"])
            d = np.mod(np.diff(perm), 2.0)
            medians.append(float(np.median(circular_loss(d, fitted))))
        scores[draw] = np.mean(medians)
    return {
        "observed": float(observed),
        "shuffle_median": float(np.median(scores)),
        "relative_improvement": float((np.median(scores) - observed) / np.median(scores)),
        "p_no_worse": float((1 + np.sum(scores <= observed)) / (SHUFFLE_DRAWS + 1)),
    }


def broken_lineage_score(files: list[dict], fitted: float) -> float:
    if len(files) != 2:
        raise ValueError("Frozen split requires exactly two files")
    medians = []
    for left, right in ((files[0], files[1]), (files[1], files[0])):
        n = min(len(left["x"]), len(right["x"]))
        target = np.roll(right["x"][:n], -317)
        d = np.mod(target - left["x"][:n], 2.0)
        medians.append(float(np.median(circular_loss(d, fitted))))
    return float(np.mean(medians))


def time_reverse_score(files: list[dict], target: float) -> float:
    return equal_file_score(
        [{**item, "x": item["x"][::-1]} for item in files],
        (2.0 - target) % 2.0,
    )


def amplitude_quartiles(files: list[dict], target: float) -> list[dict]:
    rows = []
    for item in files:
        step_amp = np.minimum(item["amplitude"][:-1], item["amplitude"][1:])
        edges = np.quantile(step_amp, [0.0, 0.25, 0.5, 0.75, 1.0])
        for q in range(4):
            if q == 3:
                mask = (step_amp >= edges[q]) & (step_amp <= edges[q + 1])
            else:
                mask = (step_amp >= edges[q]) & (step_amp < edges[q + 1])
            rows.append(
                {
                    "file": item["file"],
                    "split": item["split"],
                    "quartile": q + 1,
                    "n": int(mask.sum()),
                    "median_phi_loss": float(np.median(circular_loss(item["steps"][mask], target))),
                    "median_sweep_r2": float(np.nanmedian(item["sweep_r2"][:-1][mask])),
                }
            )
    return rows


def plot_result(files: list[dict], fitted: float, scores: list[dict], boot: dict) -> None:
    palette = {"calibration": "#6f82b8", "evaluation": "#d89b3c", "holdout": "#4e9a72"}
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=True)
    example = [item for item in files if item["split"] == "holdout"][-1]
    ax = axes[0, 0]
    ax.plot(example["t"], example["mean_y"], "o", ms=3, alpha=0.65, label="raw file mean")
    ax.plot(example["t"], example["fit_y"], lw=2.2, label="frozen damped-sine fit")
    ax.set_title(f"Mean of 2,000 complete Ramsey patterns · $R^2$={example['r2']:.3f}")
    ax.set_xlabel("native delay, ns")
    ax.set_ylabel("detector-axis response")
    ax.legend(frameon=False)

    ax = axes[0, 1]
    start = 0
    for item in files:
        n = len(item["x"])
        idx = np.arange(start, start + n)
        ax.plot(idx, item["x"], lw=0.45, alpha=0.75, color=palette[item["split"]])
        start += n
        ax.axvline(start, color="#d1d5db", lw=0.7)
    ax.axhline(1.0, color="#111827", lw=1.0, ls="--", label="ARA ridge")
    ax.set_ylim(0, 2)
    ax.set_title("Recovered phase states on the native ARA circle")
    ax.set_xlabel("ordered complete Ramsey sweep")
    ax.set_ylabel("phase coordinate $x_j$ (0–2)")

    ax = axes[1, 0]
    for split, color in palette.items():
        values = np.concatenate([item["steps"] for item in files if item["split"] == split])
        ax.hist(values, bins=80, range=(0, 2), histtype="step", density=True, lw=1.5, color=color, label=split)
    ax.axvline(CANDIDATES["phi_2_over_phi"], color="#c2410c", lw=2, label="$2/\\phi$")
    ax.axvline(fitted, color="#111827", lw=2, ls="--", label="calibration-fitted")
    ax.axvline(CANDIDATES["rational_26_over_21"], color="#7c3aed", lw=1.3, ls=":", label="26/21")
    ax.set_xlim(0, 2)
    ax.set_title("Ordered one-sweep phase advances")
    ax.set_xlabel("$d_{j,1}$ on 0–2")
    ax.set_ylabel("density")
    ax.legend(frameon=False, fontsize=9)

    ax = axes[1, 1]
    fixed_names = [name for name in CANDIDATES] + ["calibration_fitted", "previous_step_velocity"]
    xloc = np.arange(len(fixed_names))
    width = 0.36
    for offset, split in ((-width / 2, "evaluation"), (width / 2, "holdout")):
        lookup = {(row["split"], row["candidate"]): row["primary_loss"] for row in scores}
        vals = [lookup[(split, name)] for name in fixed_names]
        ax.bar(xloc + offset, vals, width=width, label=split, color=palette[split])
    ax.set_xticks(xloc, [name.replace("_", "\n") for name in fixed_names], rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("equal-file median circular loss")
    ax.set_title("Frozen candidates · lower is better")
    ax.legend(frameon=False)

    fig.suptitle("Q60 · Does repeated Ramsey phase transport select the ARA Phi step?", fontsize=16)
    fig.savefig(FIG_OUT, dpi=190)
    fig.savefig(SVG_OUT)
    plt.close(fig)


def main() -> None:
    if sha256(PROTOCOL) != EXPECTED_PROTOCOL_SHA256:
        raise RuntimeError("Frozen Q60 protocol hash mismatch")
    paths = sorted(SOURCE.glob("*.mat"))
    if len(paths) != 6:
        raise RuntimeError(f"Expected six raw T2 errorbar files, found {len(paths)}")
    split_names = ["calibration"] * 2 + ["evaluation"] * 2 + ["holdout"] * 2
    files = [fit_file(path, split) for path, split in zip(paths, split_names)]
    split_files = {split: [item for item in files if item["split"] == split] for split in set(split_names)}

    calibration_steps = np.concatenate([item["steps"] for item in split_files["calibration"]])
    fitted, fitted_resultant = circular_mean_ara(calibration_steps)
    all_candidates = {**CANDIDATES, "calibration_fitted": fitted}

    score_rows = []
    lag_rows = []
    for split in ("calibration", "evaluation", "holdout"):
        subset = split_files[split]
        for name, candidate in all_candidates.items():
            score_rows.append(
                {
                    "split": split,
                    "candidate": name,
                    "step": candidate,
                    "primary_loss": equal_file_score(subset, candidate),
                }
            )
            for lag in FIB_LAGS:
                lag_rows.append(
                    {
                        "split": split,
                        "candidate": name,
                        "lag": lag,
                        "predicted_step": (lag * candidate) % 2.0,
                        "loss": equal_file_score(subset, candidate, lag=lag),
                    }
                )
        score_rows.append(
            {
                "split": split,
                "candidate": "previous_step_velocity",
                "step": float("nan"),
                "primary_loss": previous_velocity_score(subset),
            }
        )

    boot = {split: bootstrap_split(split_files[split]) for split in ("evaluation", "holdout")}
    controls = {}
    for split in ("evaluation", "holdout"):
        subset = split_files[split]
        controls[split] = {
            "shuffle": shuffle_control(subset, fitted),
            "broken_lineage_loss": broken_lineage_score(subset, fitted),
            "time_reverse_phi_loss": time_reverse_score(subset, CANDIDATES["phi_2_over_phi"]),
            "forward_phi_loss": equal_file_score(subset, CANDIDATES["phi_2_over_phi"]),
        }

    score_lookup = {(row["split"], row["candidate"]): row["primary_loss"] for row in score_rows}
    g0 = all(item["r2"] >= 0.70 and np.isfinite(item["x"]).sum() >= 1900 for item in files)
    g1_parts = {}
    for split in ("evaluation", "holdout"):
        fitted_loss = score_lookup[(split, "calibration_fitted")]
        g1_parts[split] = {
            "shuffle_20pct": controls[split]["shuffle"]["relative_improvement"] >= 0.20,
            "beats_broken": fitted_loss < controls[split]["broken_lineage_loss"],
            "beats_persistence": fitted_loss < score_lookup[(split, "persistence")],
        }
    g1 = g0 and all(all(parts.values()) for parts in g1_parts.values())

    cphi = CANDIDATES["phi_2_over_phi"]
    g2_parts = {}
    for split in ("evaluation", "holdout"):
        phi_loss = score_lookup[(split, "phi_2_over_phi")]
        fitted_loss = score_lookup[(split, "calibration_fitted")]
        low, high = boot[split]["mean_ci_unwrapped"]
        # Compare Phi to the interval in the unwrapped neighbourhood of its point estimate.
        point = boot[split]["point"]
        phi_near = point + float(circular_signed(cphi - point))
        g2_parts[split] = {
            "within_5pct_fitted": phi_loss <= 1.05 * fitted_loss,
            "phi_in_step_ci": low <= phi_near <= high,
        }
    g2 = g0 and all(all(parts.values()) for parts in g2_parts.values())

    aggregate_lag = {}
    for split in ("evaluation", "holdout"):
        for name in all_candidates:
            vals = [row["loss"] for row in lag_rows if row["split"] == split and row["candidate"] == name]
            aggregate_lag[(split, name)] = float(np.mean(vals))
    g3_parts = {}
    for split in ("evaluation", "holdout"):
        ci = boot[split]["phi_minus_26_21_ci"]
        phi_lag = aggregate_lag[(split, "phi_2_over_phi")]
        best_other = min(
            value for (sp, name), value in aggregate_lag.items() if sp == split and name != "phi_2_over_phi"
        )
        g3_parts[split] = {"beats_26_21_ci": ci[1] < 0.0, "best_fibonacci_loss": phi_lag < best_other}
    g3 = g0 and all(all(parts.values()) for parts in g3_parts.values())

    quartiles = amplitude_quartiles(files, cphi)
    result = {
        "test": "Q60_RAMSEY_VERTICAL_PHI_PHASE_ADVANCE",
        "date": "2026-08-03",
        "source_doi": "10.5281/zenodo.14033026",
        "source_archive_sha256": "73F3E2CA7B3658452B4C171532C751E96D7392DCB8741B87A18E28C7073D67FD",
        "protocol_sha256": EXPECTED_PROTOCOL_SHA256,
        "retrospective_reanalysis": True,
        "calibration_fitted_step": fitted,
        "calibration_fitted_resultant": fitted_resultant,
        "candidate_steps": all_candidates,
        "file_quality": [
            {
                "file": item["file"],
                "split": item["split"],
                "sweeps": len(item["x"]),
                "mean_fit_r2": item["r2"],
                "tau_ns": item["tau"],
                "omega_rad_per_ns": item["omega"],
                "detector_direction": item["direction"].tolist(),
                "median_sweep_r2": float(np.nanmedian(item["sweep_r2"])),
                "step_circular_mean": circular_mean_ara(item["steps"])[0],
                "step_resultant": circular_mean_ara(item["steps"])[1],
            }
            for item in files
        ],
        "bootstrap": boot,
        "controls": controls,
        "amplitude_quartiles": quartiles,
        "gates": {
            "G0_usable_phase_reconstruction": g0,
            "G1_ordered_phase_transport": g1,
            "G1_parts": g1_parts,
            "G2_phi_compatibility": g2,
            "G2_parts": g2_parts,
            "G3_phi_identification": g3,
            "G3_parts": g3_parts,
        },
        "verdicts": {
            "data": "USABLE" if g0 else "DATA INADEQUATE",
            "ordered_transport": "SUPPORTED" if g1 else "NOT SUPPORTED",
            "phi_compatibility": "PHI-COMPATIBLE" if g2 else "NOT PHI-COMPATIBLE",
            "phi_identification": "PHI IDENTIFIED" if g3 else "PHI NOT IDENTIFIED AT THIS RESOLUTION",
        },
        "boundary": (
            "Q60 tests ordered phase drift between complete saved Ramsey sweeps. It does not directly test a "
            "double-slit trajectory or measurement-induced irrational-to-rational collapse. Saved row order is "
            "assumed to preserve acquisition order because per-sweep timestamps are absent."
        ),
    }

    with gzip.open(PHASES_OUT, "wt", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["file", "split", "sweep", "x", "step_to_next", "amplitude", "sweep_r2"],
        )
        writer.writeheader()
        for item in files:
            for j, x in enumerate(item["x"]):
                writer.writerow(
                    {
                        "file": item["file"],
                        "split": item["split"],
                        "sweep": j,
                        "x": x,
                        "step_to_next": item["steps"][j] if j < len(item["steps"]) else "",
                        "amplitude": item["amplitude"][j],
                        "sweep_r2": item["sweep_r2"][j],
                    }
                )
    with SCORES_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(score_rows[0]))
        writer.writeheader()
        writer.writerows(score_rows)
    with LAGS_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(lag_rows[0]))
        writer.writeheader()
        writer.writerows(lag_rows)
    RESULT_OUT.write_text(json.dumps(result, indent=2, allow_nan=False), encoding="utf-8")
    plot_result(files, fitted, score_rows, boot)
    print(json.dumps(result["verdicts"], indent=2))
    print(f"calibration fitted step: {fitted:.9f}; 2/phi: {cphi:.9f}")


if __name__ == "__main__":
    main()
