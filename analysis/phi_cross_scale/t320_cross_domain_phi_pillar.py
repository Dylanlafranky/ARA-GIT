"""T320: frozen cross-domain transfer test for the A-B-A Phi pillar."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import pathlib
import sys

import numpy as np


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PENDULUM = ROOT / "analysis" / "pendulum_scripts"
sys.path.insert(0, str(PENDULUM))
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(HERE / ".mplconfig"))

import matplotlib.pyplot as plt

from pendulum_common import load_triple, load_triple_driven, rest_centered


TEST_ID = "T320-CROSS-DOMAIN-PHI-PILLAR-v1"
PROTOCOL = HERE / "T320_CROSS_DOMAIN_PHI_PILLAR_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA256 = "ab3324af52a84175c20afb0afc6a95d94404475abd48210e2ee4f39c2e9bf2c1"
T319 = HERE / "T319_PENTAGON_PHI_PILLAR_GEOMETRY_RESULTS.json"
LINEAGE = HERE / "phase_lineage_results.json"
RESULTS = HERE / "T320_CROSS_DOMAIN_PHI_PILLAR_RESULTS.json"
WINDOWS = HERE / "T320_CROSS_DOMAIN_PHI_PILLAR_WINDOWS.csv"
FIGURE = HERE / "T320_CROSS_DOMAIN_PHI_PILLAR.png"
FIGURE_SVG = HERE / "T320_CROSS_DOMAIN_PHI_PILLAR.svg"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
ANGLE_TARGET = 108.0
EPS = 1e-12
WINDOW_SECONDS = 0.10
SHIFT_FRACTIONS = (0.17, 0.31, 0.47)
Q_CANDIDATES = {
    "1": 1.0,
    "sqrt2": math.sqrt(2.0),
    "1.5": 1.5,
    "phi": PHI,
    "sqrt3": math.sqrt(3.0),
    "2": 2.0,
}
ANGLE_CANDIDATES = {
    "90": 90.0,
    "108": 108.0,
    "120": 120.0,
    "135": 135.0,
    "144": 144.0,
    "180": 180.0,
}


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def robust_scale(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=np.float64)
    median = float(np.median(values))
    scale = 1.4826 * float(np.median(np.abs(values - median)))
    if not np.isfinite(scale) or scale <= EPS:
        scale = float(np.std(values))
    if not np.isfinite(scale) or scale <= EPS:
        raise RuntimeError("Degenerate development scale")
    return scale


def development_scales() -> dict[str, float]:
    angle_parts: list[np.ndarray] = []
    velocity_parts: list[np.ndarray] = []
    for run in ("run1", "run2"):
        _, theta, velocity, _ = load_triple(run, decimate=10)
        centered = rest_centered(theta)
        for arm in (1, 2, 3):
            angle_parts.append(np.asarray(centered[arm], dtype=np.float64))
            velocity_parts.append(np.asarray(velocity[arm], dtype=np.float64))
    return {
        "angle": robust_scale(np.concatenate(angle_parts)),
        "velocity": robust_scale(np.concatenate(velocity_parts)),
    }


def raw_states(run: str, scales: dict[str, float], driven: bool = False):
    loader = load_triple_driven if driven else load_triple
    time, theta, velocity, fs = loader(run, decimate=10)
    centered = rest_centered(theta)
    states = {
        arm: np.column_stack(
            [
                np.asarray(centered[arm], dtype=np.float64) / scales["angle"],
                np.asarray(velocity[arm], dtype=np.float64) / scales["velocity"],
            ]
        )
        for arm in (1, 2, 3)
    }
    return np.asarray(time, dtype=np.float64), centered, states, float(fs)


def route_rows(
    label: str,
    time: np.ndarray,
    centered: dict[int, np.ndarray],
    states: dict[int, np.ndarray],
    fs: float,
    middle_shift: int = 0,
) -> list[dict]:
    a0 = states[3]
    a1 = states[1]
    b = np.roll(states[2], middle_shift, axis=0) if middle_shift else states[2]

    dot_aa = np.einsum("ij,ij->i", a0, a1)
    dot_a0b = np.einsum("ij,ij->i", a0, b)
    dot_a1b = np.einsum("ij,ij->i", a1, b)

    u = a0 - b
    v = a1 - b
    direct = a0 - a1
    d0 = np.linalg.norm(u, axis=1)
    d1 = np.linalg.norm(v, axis=1)
    chord = np.linalg.norm(direct, axis=1)
    norm0 = np.linalg.norm(a0, axis=1)
    norm1 = np.linalg.norm(a1, axis=1)
    normb = np.linalg.norm(b, axis=1)

    eligible = (
        (dot_aa > 0.0)
        & (dot_a0b < 0.0)
        & (dot_a1b < 0.0)
        & (d0 > EPS)
        & (d1 > EPS)
        & (norm0 > EPS)
        & (norm1 > EPS)
        & (normb > EPS)
    )
    idx = np.flatnonzero(eligible)
    if idx.size == 0:
        return []

    q = 2.0 * chord[idx] / (d0[idx] + d1[idx])
    cos_angle = np.einsum("ij,ij->i", u[idx], v[idx]) / (d0[idx] * d1[idx])
    angle = np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))
    leg_ratio = np.minimum(d0[idx], d1[idx]) / np.maximum(d0[idx], d1[idx])
    branch = np.where(np.asarray(centered[1])[idx] >= 0.0, "A-positive", "B-negative")

    window_samples = max(1, int(round(WINDOW_SECONDS * fs)))
    window_id = idx // window_samples
    rows: list[dict] = []
    for wid in np.unique(window_id):
        take = window_id == wid
        rows.append(
            {
                "dataset": label,
                "middle_shift_fraction": float(middle_shift / len(time)),
                "window": int(wid),
                "time_mid_s": float(np.median(time[idx[take]])),
                "eligible_samples": int(np.sum(take)),
                "q_median": float(np.median(q[take])),
                "angle_median_degrees": float(np.median(angle[take])),
                "leg_balance_median": float(np.median(leg_ratio[take])),
                "branch": (
                    "A-positive"
                    if np.sum(branch[take] == "A-positive") >= np.sum(branch[take] == "B-negative")
                    else "B-negative"
                ),
            }
        )
    return rows


def candidate_errors(values: np.ndarray, candidates: dict[str, float]) -> dict[str, float]:
    return {
        name: float(np.median(np.abs(values - target)))
        for name, target in candidates.items()
    }


def summarize(rows: list[dict]) -> dict:
    if not rows:
        return {
            "windows": 0,
            "eligible_samples": 0,
            "median_q": None,
            "q_candidate_errors": {},
            "q_winner": None,
            "median_angle_degrees": None,
            "angle_candidate_errors": {},
            "angle_winner": None,
            "median_leg_balance": None,
            "branches": {
                "A-positive": {"windows": 0, "median_q": None, "candidate_errors": {}, "winner": None},
                "B-negative": {"windows": 0, "median_q": None, "candidate_errors": {}, "winner": None},
            },
        }
    q = np.asarray([row["q_median"] for row in rows], dtype=np.float64)
    angle = np.asarray([row["angle_median_degrees"] for row in rows], dtype=np.float64)
    legs = np.asarray([row["leg_balance_median"] for row in rows], dtype=np.float64)
    q_errors = candidate_errors(q, Q_CANDIDATES)
    angle_errors = candidate_errors(angle, ANGLE_CANDIDATES)
    branch = {}
    for branch_name in ("A-positive", "B-negative"):
        bq = np.asarray(
            [row["q_median"] for row in rows if row["branch"] == branch_name],
            dtype=np.float64,
        )
        branch[branch_name] = {
            "windows": int(bq.size),
            "median_q": float(np.median(bq)) if bq.size else None,
            "candidate_errors": candidate_errors(bq, Q_CANDIDATES) if bq.size else {},
            "winner": min(candidate_errors(bq, Q_CANDIDATES), key=candidate_errors(bq, Q_CANDIDATES).get)
            if bq.size
            else None,
        }
    return {
        "windows": int(len(rows)),
        "eligible_samples": int(sum(row["eligible_samples"] for row in rows)),
        "median_q": float(np.median(q)),
        "q_candidate_errors": q_errors,
        "q_winner": min(q_errors, key=q_errors.get),
        "median_angle_degrees": float(np.median(angle)),
        "angle_candidate_errors": angle_errors,
        "angle_winner": min(angle_errors, key=angle_errors.get),
        "median_leg_balance": float(np.median(legs)),
        "branches": branch,
    }


def load_prior_evidence() -> dict:
    t319 = json.loads(T319.read_text(encoding="utf-8"))
    lineage = json.loads(LINEAGE.read_text(encoding="utf-8"))
    return {
        "exact_geometry": {
            "class": "deductive benchmark",
            "eligible_for_route_statistic": True,
            "q": 2.0 * t319["pentagon"]["diagonal"] / t319["pentagon"]["two_side_path"],
            "direct_route_on_octave_scale": t319["pentagon"]["diagonal"],
            "checks": f"{t319['checks_passed']}/{t319['checks_total']}",
            "result": "exact phi by regular-pentagon construction",
        },
        "sunflower_scale_lineage": {
            "class": "ordered-scale calibration",
            "eligible_for_complete_route_statistic": False,
            "adjacent_ratio_phi_median_error": lineage["direct_landmark_metrics"]["phi"][
                "median_absolute_error"
            ],
            "same_phase_phi_squared_median_error": lineage["two_rung_landmark_metrics"][
                "phi^2"
            ]["median_absolute_error"],
            "reason": "observes ordered scale ratios but not both physical paths between common endpoints",
        },
        "quantum_Q46_Q47": {
            "class": "existing public/simulator analyses",
            "eligible_for_complete_route_statistic": False,
            "reason": "tiers are not three independently labelled commensurate A-B-A endpoint states; Q47 tests recurrence, not the cross-scale pillar",
        },
        "solar_system_T317": {
            "class": "public orbital crosswalk",
            "eligible_for_complete_route_statistic": False,
            "reason": "supplies a Sun/planet A-B pair and a parent frame, not two same-phase endpoints with one commensurate middle state",
        },
        "T302_T305_carriers": {
            "class": "biological and schedule-carrier tests",
            "eligible_for_complete_route_statistic": False,
            "reason": "test cumulative placement/coverage rather than the direct-versus-around route",
        },
    }


def write_rows(rows: list[dict]) -> None:
    fields = [
        "dataset",
        "middle_shift_fraction",
        "window",
        "time_mid_s",
        "eligible_samples",
        "q_median",
        "angle_median_degrees",
        "leg_balance_median",
        "branch",
    ]
    with WINDOWS.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def make_figure(real_rows: list[dict], shifted: dict[str, list[dict]], result: dict) -> None:
    q = np.asarray([row["q_median"] for row in real_rows])
    angle = np.asarray([row["angle_median_degrees"] for row in real_rows])
    legs = np.asarray([row["leg_balance_median"] for row in real_rows])
    branches = np.asarray([row["branch"] for row in real_rows])

    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
    fig.suptitle("T320 — direct same-phase pillar vs full A–B–A octave route", fontsize=16, weight="bold")

    bins = np.linspace(0, 2, 51)
    axes[0, 0].hist(q[branches == "A-positive"], bins=bins, alpha=0.65, label="A-positive mirror")
    axes[0, 0].hist(q[branches == "B-negative"], bins=bins, alpha=0.65, label="B-negative mirror")
    for name, value in Q_CANDIDATES.items():
        if name in ("1", "phi", "2"):
            axes[0, 0].axvline(value, linestyle="--", linewidth=1.4, label=name)
    axes[0, 0].set(xlabel="q = 2 × direct / two-leg route", ylabel="0.10 s windows", xlim=(0, 2))
    axes[0, 0].legend(fontsize=8)

    axes[0, 1].scatter(angle, q, c=legs, cmap="viridis", s=9, alpha=0.6)
    axes[0, 1].axhline(PHI, color="#D97706", linestyle="--", label="Phi")
    axes[0, 1].axvline(ANGLE_TARGET, color="#7C3AED", linestyle="--", label="108°")
    axes[0, 1].set(xlabel="included angle at B (degrees)", ylabel="q", ylim=(0, 2))
    axes[0, 1].legend()

    names = ["real", "shift 17%", "shift 31%", "shift 47%"]
    errors = [result["pendulum"]["evaluation"]["q_candidate_errors"]["phi"]]
    errors.extend(shifted[key][0]["phi_error"] for key in sorted(shifted))
    axes[1, 0].bar(names, errors, color=["#2563EB", "#A3A3A3", "#A3A3A3", "#A3A3A3"])
    axes[1, 0].set(ylabel="median absolute q error from Phi", title="Middle-state alignment control")
    axes[1, 0].tick_params(axis="x", rotation=20)

    q_errors = result["pendulum"]["evaluation"]["q_candidate_errors"]
    axes[1, 1].bar(list(q_errors), list(q_errors.values()), color="#D4A017")
    axes[1, 1].set(ylabel="median absolute error", title="Frozen q landmarks")
    axes[1, 1].tick_params(axis="x", rotation=25)

    subtitle = (
        f"run 3: q={result['pendulum']['evaluation']['median_q']:.4f}; "
        f"angle={result['pendulum']['evaluation']['median_angle_degrees']:.2f}°; "
        f"leg balance={result['pendulum']['evaluation']['median_leg_balance']:.3f}; "
        f"verdict={result['pendulum']['verdict']}"
    )
    fig.text(0.5, 0.005, subtitle, ha="center", fontsize=10)
    fig.savefig(FIGURE, dpi=180)
    fig.savefig(FIGURE_SVG)
    plt.close(fig)


def main() -> None:
    if sha256(PROTOCOL) != PROTOCOL_SHA256:
        raise RuntimeError("Frozen T320 protocol hash mismatch")
    scales = development_scales()

    time, centered, states, fs = raw_states("run3", scales)
    real_rows = route_rows("free_run3", time, centered, states, fs)
    if not real_rows:
        raise RuntimeError("No eligible run-3 A-B-A samples")
    evaluation = summarize(real_rows)

    shifted_rows: dict[str, list[dict]] = {}
    shifted_summary: dict[str, dict] = {}
    for fraction in SHIFT_FRACTIONS:
        shift = int(round(fraction * len(time)))
        rows = route_rows(f"free_run3_shift_{fraction:.2f}", time, centered, states, fs, shift)
        summary = summarize(rows)
        shifted_rows[f"{fraction:.2f}"] = [
            {"phi_error": summary["q_candidate_errors"]["phi"]}
        ]
        shifted_summary[f"{fraction:.2f}"] = summary

    dtime, dcentered, dstates, dfs = raw_states("triple1", scales, driven=True)
    driven_rows = route_rows("driven_triple1", dtime, dcentered, dstates, dfs)
    driven_summary = summarize(driven_rows)

    gate1 = evaluation["q_winner"] == "phi"
    gate2 = evaluation["angle_winner"] == "108"
    gate3 = evaluation["median_leg_balance"] >= 0.90
    gate4 = all(
        evaluation["branches"][branch]["winner"] == "phi"
        for branch in ("A-positive", "B-negative")
    )
    real_phi_error = evaluation["q_candidate_errors"]["phi"]
    gate5 = all(
        real_phi_error < summary["q_candidate_errors"]["phi"]
        for summary in shifted_summary.values()
    )
    gates = {
        "G1_phi_unique_q_winner": gate1,
        "G2_108_unique_angle_winner": gate2,
        "G3_equal_leg_ratio_at_least_0_90": gate3,
        "G4_both_mirror_branches_choose_phi": gate4,
        "G5_real_alignment_beats_all_middle_shifts": gate5,
    }
    passed = sum(bool(value) for value in gates.values())
    verdict = "SUPPORTED" if passed == 5 else "MIXED" if passed >= 3 else "NOT SUPPORTED"

    prior = load_prior_evidence()
    physical_eligible_domains = 1
    physical_passes = 1 if verdict == "SUPPORTED" else 0
    cross_domain_verdict = (
        "PHYSICALLY CROSS-DOMAIN CONFIRMED"
        if physical_eligible_domains >= 2 and physical_passes >= 2
        else "INSUFFICIENT ELIGIBLE PHYSICAL DOMAINS"
    )

    result = {
        "test_id": TEST_ID,
        "protocol_sha256": PROTOCOL_SHA256,
        "claim": {
            "around_route": "A_k -> B -> A_(k+1), normalized to 2",
            "direct_route": "A_k -> A_(k+1)",
            "predicted_direct_coordinate": PHI,
            "route_statistic": "q = 2*d(A0,A1)/(d(A0,B)+d(B,A1))",
        },
        "development_metric_scales": scales,
        "pendulum": {
            "source": "dynamicslab MultiArm-Pendulum, Zenodo 10.5281/zenodo.6633719",
            "mapping": "arm3 A0/child -> arm2 B/intermediate -> arm1 A1/larger",
            "evaluation": evaluation,
            "middle_shift_controls": shifted_summary,
            "driven_transfer": driven_summary,
            "gates": gates,
            "gates_passed": passed,
            "gates_total": 5,
            "verdict": verdict,
        },
        "existing_domain_eligibility": prior,
        "eligible_raw_physical_domains": physical_eligible_domains,
        "passing_raw_physical_domains": physical_passes,
        "cross_domain_verdict": cross_domain_verdict,
        "boundary": (
            "The exact pentagon identity is deductive. Sunflower scale lineage is calibration. "
            "The pendulum is the only existing raw physical archive eligible under the frozen common-route rule; "
            "therefore this run cannot establish physical cross-domain universality even if it passes."
        ),
    }

    write_rows(real_rows + driven_rows)
    RESULTS.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    make_figure(real_rows, shifted_rows, result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
