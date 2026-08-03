"""T320A: fidelity-corrected pendulum transfer of the A-B-A Phi pillar."""

from __future__ import annotations

import csv
import json
import math
import pathlib

import matplotlib.pyplot as plt
import numpy as np

import t320_cross_domain_phi_pillar as base


HERE = pathlib.Path(__file__).resolve().parent
PROTOCOL = HERE / "T320A_CROSS_DOMAIN_PHI_PILLAR_FIDELITY_CORRECTION_v1.md"
PROTOCOL_SHA256 = "dc6faec59f3809cc180f28fa08660278ddd4a404508fed7608116c51e96992fc"
RESULTS = HERE / "T320A_CROSS_DOMAIN_PHI_PILLAR_FIDELITY_RESULTS.json"
WINDOWS = HERE / "T320A_CROSS_DOMAIN_PHI_PILLAR_FIDELITY_WINDOWS.csv"
FIGURE = HERE / "T320A_CROSS_DOMAIN_PHI_PILLAR_FIDELITY.png"
FIGURE_SVG = HERE / "T320A_CROSS_DOMAIN_PHI_PILLAR_FIDELITY.svg"


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

    u = a0 - b
    v = a1 - b
    d0 = np.linalg.norm(u, axis=1)
    d1 = np.linalg.norm(v, axis=1)
    chord = np.linalg.norm(a0 - a1, axis=1)
    norms = np.column_stack(
        [np.linalg.norm(a0, axis=1), np.linalg.norm(b, axis=1), np.linalg.norm(a1, axis=1)]
    )
    eligible = (
        np.all(norms > base.EPS, axis=1)
        & (d0 > base.EPS)
        & (d1 > base.EPS)
    )
    idx = np.flatnonzero(eligible)
    q = 2.0 * chord[idx] / (d0[idx] + d1[idx])
    cos_angle = np.einsum("ij,ij->i", u[idx], v[idx]) / (d0[idx] * d1[idx])
    angle = np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))
    leg_ratio = np.minimum(d0[idx], d1[idx]) / np.maximum(d0[idx], d1[idx])
    branch = np.where(np.asarray(centered[1])[idx] >= 0.0, "A-positive", "B-negative")

    window_samples = max(1, int(round(base.WINDOW_SECONDS * fs)))
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


def write_rows(rows: list[dict]) -> None:
    with WINDOWS.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def figure(real: list[dict], controls: dict[str, dict], result: dict) -> None:
    q = np.asarray([row["q_median"] for row in real])
    angle = np.asarray([row["angle_median_degrees"] for row in real])
    leg = np.asarray([row["leg_balance_median"] for row in real])
    branch = np.asarray([row["branch"] for row in real])

    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
    fig.suptitle("T320A — corrected cross-rung A–B–A pillar test", fontsize=16, weight="bold")

    bins = np.linspace(0, 2, 61)
    axes[0, 0].hist(q[branch == "A-positive"], bins=bins, alpha=0.65, label="A-positive mirror")
    axes[0, 0].hist(q[branch == "B-negative"], bins=bins, alpha=0.65, label="B-negative mirror")
    axes[0, 0].axvline(base.PHI, color="#D97706", linestyle="--", linewidth=2, label="Phi")
    axes[0, 0].set(xlabel="q = 2 × direct / A–B–A route", ylabel="0.10 s windows", xlim=(0, 2))
    axes[0, 0].legend(fontsize=8)

    scatter = axes[0, 1].scatter(angle, q, c=leg, cmap="viridis", s=11, alpha=0.55)
    axes[0, 1].axhline(base.PHI, color="#D97706", linestyle="--")
    axes[0, 1].axvline(base.ANGLE_TARGET, color="#7C3AED", linestyle="--")
    axes[0, 1].set(xlabel="included angle at B (degrees)", ylabel="q", ylim=(0, 2))
    fig.colorbar(scatter, ax=axes[0, 1], label="equal-leg ratio")

    names = ["real", "shift 17%", "shift 31%", "shift 47%"]
    errors = [result["evaluation"]["q_candidate_errors"]["phi"]]
    errors += [controls[key]["q_candidate_errors"]["phi"] for key in ("0.17", "0.31", "0.47")]
    axes[1, 0].bar(names, errors, color=["#2563EB", "#A3A3A3", "#A3A3A3", "#A3A3A3"])
    axes[1, 0].set(ylabel="median |q − Phi|", title="Real versus shifted middle arm")
    axes[1, 0].tick_params(axis="x", rotation=20)

    candidate_errors = result["evaluation"]["q_candidate_errors"]
    axes[1, 1].bar(list(candidate_errors), list(candidate_errors.values()), color="#D4A017")
    axes[1, 1].set(ylabel="median absolute error", title="Frozen q landmarks")
    axes[1, 1].tick_params(axis="x", rotation=25)

    fig.text(
        0.5,
        0.005,
        f"q={result['evaluation']['median_q']:.4f}; angle={result['evaluation']['median_angle_degrees']:.2f}°; "
        f"leg balance={result['evaluation']['median_leg_balance']:.3f}; "
        f"cross-arm triangle: {result['cross_arm_triangle_verdict']} ({result['gates_passed']}/5); "
        "intended same-arm temporal handover NOT TESTED",
        ha="center",
    )
    fig.savefig(FIGURE, dpi=180)
    fig.savefig(FIGURE_SVG)
    plt.close(fig)


def main() -> None:
    if base.sha256(PROTOCOL) != PROTOCOL_SHA256:
        raise RuntimeError("Frozen T320A correction hash mismatch")
    scales = base.development_scales()
    time, centered, states, fs = base.raw_states("run3", scales)
    real = route_rows("free_run3", time, centered, states, fs)
    evaluation = base.summarize(real)

    controls: dict[str, dict] = {}
    control_rows: list[dict] = []
    for fraction in base.SHIFT_FRACTIONS:
        shift = int(round(fraction * len(time)))
        rows = route_rows(f"free_run3_shift_{fraction:.2f}", time, centered, states, fs, shift)
        controls[f"{fraction:.2f}"] = base.summarize(rows)
        control_rows.extend(rows)

    dtime, dcentered, dstates, dfs = base.raw_states("triple1", scales, driven=True)
    driven = route_rows("driven_triple1", dtime, dcentered, dstates, dfs)
    driven_summary = base.summarize(driven)

    gates = {
        "G1_phi_unique_q_winner": evaluation["q_winner"] == "phi",
        "G2_108_unique_angle_winner": evaluation["angle_winner"] == "108",
        "G3_equal_leg_ratio_at_least_0_90": evaluation["median_leg_balance"] >= 0.90,
        "G4_both_mirror_branches_choose_phi": all(
            evaluation["branches"][name]["winner"] == "phi"
            for name in ("A-positive", "B-negative")
        ),
        "G5_real_alignment_beats_all_middle_shifts": all(
            evaluation["q_candidate_errors"]["phi"]
            < controls[key]["q_candidate_errors"]["phi"]
            for key in controls
        ),
    }
    passed = sum(gates.values())
    verdict = "SUPPORTED" if passed == 5 else "MIXED" if passed >= 3 else "NOT SUPPORTED"
    result = {
        "test_id": "T320A-CROSS-DOMAIN-PHI-PILLAR-FIDELITY-v1",
        "protocol_sha256": PROTOCOL_SHA256,
        "status": "post-result fidelity correction; retrospective",
        "correction": "cross-rung A/B labels no longer require instantaneous phase-plane sign alignment",
        "source": "dynamicslab MultiArm-Pendulum, Zenodo 10.5281/zenodo.6633719",
        "development_metric_scales": scales,
        "evaluation": evaluation,
        "middle_shift_controls": controls,
        "driven_transfer": driven_summary,
        "endpoint_swap_invariance": "exact by symmetry of q and included angle",
        "gates": gates,
        "gates_passed": passed,
        "gates_total": 5,
        "cross_arm_triangle_verdict": verdict,
        "intended_same_identity_temporal_handover_status": "NOT TESTED — WRONG IDENTITY BOUNDARY",
        "physical_cross_domain_status": "NO ELIGIBLE PHYSICAL TEST OF THE INTENDED HANDOVER",
        "superseded_interpretation": (
            "Arm 3 -> arm 2 -> arm 1 compares three distinct identities. It is not the intended "
            "same-identity temporal handover A[j,k] -> B[j,k] -> A[j,k+1]."
        ),
        "boundary": (
            "This retains a descriptive cross-arm coupling cut only. It neither supports nor rejects "
            "the intended same-arm temporal Phi-handover claim."
        ),
    }
    write_rows(real + control_rows + driven)
    RESULTS.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    figure(real, controls, result)
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
