"""Frozen ARA test of Phi-ordered recurrence and resonance death."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
from dataclasses import asdict, dataclass

import numpy as np
import scipy.io as sio
from scipy.stats import spearmanr


HERE = os.path.dirname(os.path.abspath(__file__))
LOCAL_DATA = os.path.join(HERE, "data")
EXTERNAL_DATA = os.environ.get(
    "ARA_PENDULUM_EXTERNAL",
    r"F:\SystemFormulaFolder\external_data\MultiArm-Pendulum\DoublePendulum",
)
FILES = {
    "run1": os.path.join(LOCAL_DATA, "pend_double.mat"),
    "run2": os.path.join(EXTERNAL_DATA, "DoubleDataFreeSwing_2_Dt_0_001.mat"),
    "run3": os.path.join(EXTERNAL_DATA, "DoubleDataFreeSwing_3_Dt_0_001.mat"),
    "run4": os.path.join(EXTERNAL_DATA, "DoubleDataFreeSwing_4_Dt_0_001.mat"),
}
EXPECTED_SHA256 = {
    "run1": "2AF828048DEBC0EC33DCD9F46538B747A72A7BFAA3B333852CC474DB5ADA7633",
    "run2": "B0F94AFDC6F1BB20285CA9FD416DDB249521AC678AC84F45C0881F4D9DCB8FF2",
    "run3": "8E8369479E135B8BBD3FC292B051B314EEC61E1AC98DC56CB871CEB8299978EB",
    "run4": "2876A0D76708725723BF382DCE3E42A1C37327D88775671ABB6C9EBD448C77C6",
}

MIN_CYCLE_S = 0.4 * 1.333
MIN_CHILD_SAMPLES = 3
N_PERM = 5000
SEED = 20260730
PHI = (1.0 + math.sqrt(5.0)) / 2.0

CANDIDATES = {
    "phi": PHI**-2,
    "three_eighths": 3.0 / 8.0,
    "two_fifths": 2.0 / 5.0,
    "sqrt2_conjugate": math.sqrt(2.0) - 1.0,
    "third": 1.0 / 3.0,
    "quarter": 1.0 / 4.0,
    "e_conjugate": 3.0 - math.e,
    "pi_conjugate": math.pi - 3.0,
}


@dataclass
class Row:
    run: str
    cycle: int
    start_time_s: float
    stop_time_s: float
    period_s: float
    p_AA: float
    p_AB: float
    p_BB: float
    p_BA: float
    te_AA: float
    te_AB: float
    te_BB: float
    te_BA: float
    inequality: float
    diagonal_share: float
    amplitude: float
    next_retention: float
    mu_AA: float
    mu_AB: float
    mu_BB: float
    mu_BA: float
    rotation_signed: float
    rotation_folded: float
    rotation_coherence: float
    recurrence_residual: float
    stratum: str
    gap_phi: float
    drift_phi: float
    score_phi: float


def file_sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def wrap(a: np.ndarray) -> np.ndarray:
    return (a + np.pi) % (2.0 * np.pi) - np.pi


def circular_center(a: np.ndarray) -> float:
    return float(np.arctan2(np.mean(np.sin(a)), np.mean(np.cos(a))))


def circular_signed(value: np.ndarray | float) -> np.ndarray | float:
    return (np.asarray(value) + 0.5) % 1.0 - 0.5


def circular_mean(values: np.ndarray) -> tuple[float, float]:
    z = np.mean(np.exp(2j * np.pi * values))
    return float((np.angle(z) / (2.0 * np.pi)) % 1.0), float(abs(z))


def fold_step(alpha: float) -> float:
    alpha = alpha % 1.0
    return float(min(alpha, 1.0 - alpha))


def orbit_gaps(alpha: float) -> np.ndarray:
    points = np.sort((np.arange(4, dtype=float) * alpha) % 1.0)
    return np.diff(np.r_[points, points[0] + 1.0])


def orientations(template: np.ndarray) -> list[np.ndarray]:
    out: list[np.ndarray] = []
    for base in (template, template[::-1]):
        for shift in range(4):
            candidate = np.roll(base, shift)
            if not any(np.allclose(candidate, seen) for seen in out):
                out.append(candidate)
    return out


TEMPLATES = {
    name: orientations(orbit_gaps(alpha)) for name, alpha in CANDIDATES.items()
}


def gap_distance(gaps: np.ndarray, candidate: str) -> float:
    return float(
        min(
            0.5 * np.sum(np.abs(gaps - template))
            for template in TEMPLATES[candidate]
        )
    )


def entropy_inequality(p: np.ndarray) -> float:
    positive = p[p > 0.0]
    entropy = -float(np.sum(positive * np.log(positive)))
    return float(1.0 - entropy / math.log(4.0))


def retain(a: float, b: float) -> float:
    return float(min(a, b) / max(a, b)) if max(a, b) > 1e-15 else float("nan")


def child_labels(q1: np.ndarray, q2: np.ndarray) -> np.ndarray:
    a = q1 >= 0.0
    b = q2 >= 0.0
    return np.where(a & b, 0, np.where(a & ~b, 1, np.where(~a & ~b, 2, 3)))


def spaced_crossings(q1: np.ndarray, v1: np.ndarray, t: np.ndarray) -> np.ndarray:
    candidates = np.where(
        (q1[:-1] < 0.0) & (q1[1:] >= 0.0) & (v1[1:] > 0.0)
    )[0] + 1
    if not len(candidates):
        return candidates
    kept = [int(candidates[0])]
    for index in candidates[1:]:
        if t[int(index)] - t[kept[-1]] >= MIN_CYCLE_S:
            kept.append(int(index))
    return np.asarray(kept, dtype=int)


def load_run(path: str) -> tuple[np.ndarray, dict[int, np.ndarray], dict[int, np.ndarray]]:
    matrix = sio.loadmat(path)
    t = matrix["Time"].ravel()
    theta = {i: matrix[f"Theta{i}"].ravel() for i in (1, 2)}
    velocity = {i: matrix[f"dTheta{i}"].ravel() for i in (1, 2)}
    return t, theta, velocity


def raw_cycles(run: str, path: str) -> tuple[list[dict], dict]:
    t, theta, velocity = load_run(path)
    q1 = wrap(theta[1] - circular_center(theta[1]))
    q2 = wrap(theta[2] - circular_center(theta[2]))
    crossings = spaced_crossings(q1, velocity[1], t)
    rows: list[dict] = []

    for cycle, (start, stop) in enumerate(zip(crossings[:-1], crossings[1:])):
        start, stop = int(start), int(stop)
        n = stop - start
        if n < 8:
            continue
        labels = child_labels(q1[start:stop], q2[start:stop])
        counts = np.bincount(labels, minlength=4).astype(float)
        if np.any(counts < MIN_CHILD_SAMPLES):
            continue
        p = counts / counts.sum()
        u = np.arange(n, dtype=float) / n
        mu = np.empty(4)
        centroid_coherence = np.empty(4)
        for label in range(4):
            mu[label], centroid_coherence[label] = circular_mean(u[labels == label])
        sorted_mu = np.sort(mu)
        gaps = np.diff(np.r_[sorted_mu, sorted_mu[0] + 1.0])
        amplitude = float(np.max(q1[start:stop]) - np.min(q1[start:stop]))
        rows.append(
            {
                "run": run,
                "cycle": cycle,
                "start_time": float(t[start]),
                "stop_time": float(t[stop]),
                "period": float(t[stop] - t[start]),
                "p": p,
                "inequality": entropy_inequality(p),
                "diagonal": float(p[0] + p[2]),
                "amplitude": amplitude,
                "mu": mu,
                "centroid_coherence": centroid_coherence,
                "gaps": gaps,
                "gap_distance": {
                    name: gap_distance(gaps, name) for name in CANDIDATES
                },
            }
        )

    for index, row in enumerate(rows):
        if index + 1 >= len(rows):
            row["retention"] = float("nan")
            row["rotation_signed"] = float("nan")
            row["rotation_folded"] = float("nan")
            row["rotation_coherence"] = float("nan")
            row["recurrence_residual"] = float("nan")
            row["drift_distance"] = {
                name: float("nan") for name in CANDIDATES
            }
            row["score"] = {name: float("nan") for name in CANDIDATES}
            continue
        nxt = rows[index + 1]
        row["retention"] = retain(row["amplitude"], nxt["amplitude"])
        deltas = np.asarray(circular_signed(nxt["mu"] - row["mu"]), dtype=float)
        rotation_u, coherence = circular_mean(deltas % 1.0)
        rotation_signed = float(circular_signed(rotation_u))
        folded = abs(rotation_signed)
        aligned = np.asarray(circular_signed(deltas - rotation_signed), dtype=float)
        recurrence_residual = float(np.mean(np.abs(aligned)))
        row["rotation_signed"] = rotation_signed
        row["rotation_folded"] = folded
        row["rotation_coherence"] = coherence
        row["recurrence_residual"] = recurrence_residual
        row["drift_distance"] = {
            name: abs(folded - fold_step(alpha))
            for name, alpha in CANDIDATES.items()
        }
        row["score"] = {
            name: float(
                np.clip(
                    1.0
                    - 0.5
                    * (
                        row["gap_distance"][name]
                        + 2.0 * row["drift_distance"][name]
                    ),
                    0.0,
                    1.0,
                )
            )
            for name in CANDIDATES
        }

    median_amplitude = float(np.median([row["amplitude"] for row in rows]))
    for row in rows:
        inequality_bin = int(math.floor(row["inequality"] / 0.10))
        diagonal_bin = int(math.floor(row["diagonal"] / 0.20))
        amplitude_rung = int(
            round(math.log2(max(row["amplitude"], 1e-15) / median_amplitude) / 0.50)
        )
        row["stratum"] = f"{run}|I{inequality_bin}|D{diagonal_bin}|A{amplitude_rung}"

    return rows, {
        "path": path,
        "sha256": file_sha256(path),
        "sha256_matches_frozen": file_sha256(path) == EXPECTED_SHA256[run],
        "n_samples": int(len(t)),
        "duration_s": float(t[-1] - t[0]),
        "n_crossings": int(len(crossings)),
        "n_eligible_cycles": int(len(rows)),
    }


def usable_strata(rows: list[dict]) -> dict[str, list[int]]:
    strata: dict[str, list[int]] = {}
    for index, row in enumerate(rows):
        if np.isfinite(row["retention"]):
            strata.setdefault(row["stratum"], []).append(index)
    return {key: value for key, value in strata.items() if len(value) >= 3}


def conditional_association(
    rows: list[dict], candidate: str, rng: np.random.Generator
) -> dict:
    strata = usable_strata(rows)
    x_all: list[float] = []
    y_all: list[float] = []
    groups: list[list[int]] = []
    for indices in strata.values():
        x = np.array([rows[i]["score"][candidate] for i in indices])
        y = np.array([rows[i]["retention"] for i in indices])
        positions = list(range(len(x_all), len(x_all) + len(indices)))
        groups.append(positions)
        x_all.extend((x - np.mean(x)).tolist())
        y_all.extend((y - np.mean(y)).tolist())
    x_arr, y_arr = np.asarray(x_all), np.asarray(y_all)
    if len(x_arr) < 12 or np.std(x_arr) == 0.0 or np.std(y_arr) == 0.0:
        return {
            "n": int(len(x_arr)),
            "n_strata": int(len(groups)),
            "spearman_r": float("nan"),
            "p": float("nan"),
        }
    observed = float(spearmanr(x_arr, y_arr).statistic)
    null = np.empty(N_PERM)
    for permutation in range(N_PERM):
        shuffled = y_arr.copy()
        for positions in groups:
            shuffled[positions] = rng.permutation(shuffled[positions])
        null[permutation] = float(spearmanr(x_arr, shuffled).statistic)
    return {
        "n": int(len(x_arr)),
        "n_strata": int(len(groups)),
        "spearman_r": observed,
        "p_one_sided_within_stratum": float(
            (1 + np.sum(null >= observed)) / (N_PERM + 1)
        ),
        "null_median": float(np.median(null)),
        "null_q95": float(np.quantile(null, 0.95)),
    }


def resonance_death_test(rows: list[dict], rng: np.random.Generator) -> dict:
    strata = usable_strata(rows)
    residual: list[float] = []
    group: list[int] = []
    strata_positions: list[list[int]] = []
    for indices in strata.values():
        y = np.array([rows[i]["retention"] for i in indices])
        y = y - np.mean(y)
        local_values: list[float] = []
        local_labels: list[int] = []
        for position, index in enumerate(indices):
            drift = rows[index]["rotation_folded"]
            label = 0 if drift < 0.05 else (1 if 0.10 <= drift <= 0.45 else -1)
            if label >= 0:
                local_values.append(float(y[position]))
                local_labels.append(label)
        # A matched stratum is informative only when its labels can actually
        # exchange between both frozen groups under permutation.
        if len(local_values) >= 2 and set(local_labels) == {0, 1}:
            start = len(residual)
            residual.extend(local_values)
            group.extend(local_labels)
            strata_positions.append(list(range(start, start + len(local_values))))
    residual_arr = np.asarray(residual)
    group_arr = np.asarray(group)
    repeat = residual_arr[group_arr == 0]
    nonclosing = residual_arr[group_arr == 1]
    if not len(repeat) or not len(nonclosing):
        return {
            "n_repeat": int(len(repeat)),
            "n_nonclosing": int(len(nonclosing)),
            "difference": float("nan"),
            "p": float("nan"),
        }
    observed = float(np.median(nonclosing) - np.median(repeat))
    null = np.empty(N_PERM)
    for permutation in range(N_PERM):
        shuffled = group_arr.copy()
        for positions in strata_positions:
            shuffled[positions] = rng.permutation(shuffled[positions])
        null[permutation] = float(
            np.median(residual_arr[shuffled == 1])
            - np.median(residual_arr[shuffled == 0])
        )
    return {
        "n_repeat": int(len(repeat)),
        "n_nonclosing": int(len(nonclosing)),
        "repeat_median_stratum_residual": float(np.median(repeat)),
        "nonclosing_median_stratum_residual": float(np.median(nonclosing)),
        "difference_nonclosing_minus_repeat": observed,
        "p_one_sided_within_stratum": float(
            (1 + np.sum(null >= observed)) / (N_PERM + 1)
        ),
    }


def summarize(rows: list[dict], rng: np.random.Generator) -> dict:
    finite = [row for row in rows if np.isfinite(row["retention"])]
    gap = {
        name: float(np.median([row["gap_distance"][name] for row in finite]))
        for name in CANDIDATES
    }
    drift = {
        name: float(np.median([row["drift_distance"][name] for row in finite]))
        for name in CANDIDATES
    }
    association = {
        name: conditional_association(rows, name, rng) for name in CANDIDATES
    }
    return {
        "n_cycles": int(len(rows)),
        "n_scored_transitions": int(len(finite)),
        "median_te_ara": {
            label: float(2.0 * np.median([row["p"][index] for row in rows]))
            for index, label in enumerate(("AA", "AB", "BB", "BA"))
        },
        "median_inequality": float(np.median([row["inequality"] for row in rows])),
        "median_rotation_folded": float(
            np.median([row["rotation_folded"] for row in finite])
        ),
        "median_rotation_coherence": float(
            np.median([row["rotation_coherence"] for row in finite])
        ),
        "median_recurrence_residual": float(
            np.median([row["recurrence_residual"] for row in finite])
        ),
        "gap_candidate_median_distance": gap,
        "drift_candidate_median_distance": drift,
        "conditional_retention": association,
        "resonance_death": resonance_death_test(rows, rng),
    }


def combine(run_rows: dict[str, list[dict]], names: tuple[str, ...]) -> list[dict]:
    return [row for name in names for row in run_rows[name]]


def best_candidate(metric: dict[str, float]) -> str:
    return min(metric, key=metric.get)


def main() -> None:
    run_rows: dict[str, list[dict]] = {}
    metadata = {}
    for run, path in FILES.items():
        rows, meta = raw_cycles(run, path)
        run_rows[run] = rows
        metadata[run] = meta

    rng = np.random.default_rng(SEED)
    summaries = {
        run: summarize(rows, rng) for run, rows in run_rows.items()
    }
    pooled_rows = combine(run_rows, ("run2", "run3"))
    pooled = summarize(pooled_rows, rng)
    confirmation = summaries["run4"]

    phi_assoc = pooled["conditional_retention"]["phi"]
    competitor_r = [
        value["spearman_r"]
        for name, value in pooled["conditional_retention"].items()
        if name != "phi" and np.isfinite(value["spearman_r"])
    ]
    checks = {
        "pooled_phi_gap_best": best_candidate(
            pooled["gap_candidate_median_distance"]
        )
        == "phi",
        "pooled_phi_drift_best": best_candidate(
            pooled["drift_candidate_median_distance"]
        )
        == "phi",
        "pooled_phi_retention_specific": (
            phi_assoc["spearman_r"] > 0.0
            and phi_assoc["p_one_sided_within_stratum"] < 0.05
            and phi_assoc["spearman_r"] > max(competitor_r, default=-np.inf)
        ),
        "pooled_resonance_death_direction": (
            pooled["resonance_death"]["difference_nonclosing_minus_repeat"] > 0.0
            and pooled["resonance_death"]["p_one_sided_within_stratum"] < 0.05
        ),
    }

    run4_phi_assoc = confirmation["conditional_retention"]["phi"]
    run4_gap_best = best_candidate(confirmation["gap_candidate_median_distance"])
    run4_drift_best = best_candidate(
        confirmation["drift_candidate_median_distance"]
    )
    checks["run4_confirmation"] = (
        (run4_gap_best == "phi" or run4_drift_best == "phi")
        and confirmation["gap_candidate_median_distance"]["phi"]
        <= sorted(confirmation["gap_candidate_median_distance"].values())[1]
        and confirmation["drift_candidate_median_distance"]["phi"]
        <= sorted(confirmation["drift_candidate_median_distance"].values())[1]
        and run4_phi_assoc["spearman_r"] > 0.0
        and confirmation["resonance_death"]["difference_nonclosing_minus_repeat"]
        > 0.0
    )

    passed = int(sum(checks.values()))
    verdict = (
        "SUPPORTED" if passed == 5 else ("MIXED" if passed >= 3 else "NOT SUPPORTED")
    )
    result = {
        "protocol": "PHI_ORDERED_RECURRENCE_PROTOCOL_2026-07-30.md",
        "source": {
            "repository": "https://github.com/dynamicslab/MultiArm-Pendulum",
            "doi": "10.5281/zenodo.6633719",
        },
        "constants": {
            "candidates": CANDIDATES,
            "min_cycle_s": MIN_CYCLE_S,
            "min_child_samples": MIN_CHILD_SAMPLES,
            "permutations": N_PERM,
            "seed": SEED,
        },
        "data_quality": metadata,
        "runs": summaries,
        "pooled_frozen_run2_run3": pooled,
        "run4_confirmation": {
            "gap_best": run4_gap_best,
            "drift_best": run4_drift_best,
            "checks_applied_to": "runs.run4",
        },
        "verdict": {
            "label": verdict,
            "checks_passed": passed,
            "checks": checks,
        },
    }

    json_path = os.path.join(HERE, "phi_ordered_recurrence_results.json")
    csv_path = os.path.join(HERE, "phi_ordered_recurrence_cycles.csv")
    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, allow_nan=True)

    csv_rows = []
    for rows in run_rows.values():
        for row in rows:
            record = Row(
                run=row["run"],
                cycle=int(row["cycle"]),
                start_time_s=float(row["start_time"]),
                stop_time_s=float(row["stop_time"]),
                period_s=float(row["period"]),
                p_AA=float(row["p"][0]),
                p_AB=float(row["p"][1]),
                p_BB=float(row["p"][2]),
                p_BA=float(row["p"][3]),
                te_AA=float(2.0 * row["p"][0]),
                te_AB=float(2.0 * row["p"][1]),
                te_BB=float(2.0 * row["p"][2]),
                te_BA=float(2.0 * row["p"][3]),
                inequality=float(row["inequality"]),
                diagonal_share=float(row["diagonal"]),
                amplitude=float(row["amplitude"]),
                next_retention=float(row["retention"]),
                mu_AA=float(row["mu"][0]),
                mu_AB=float(row["mu"][1]),
                mu_BB=float(row["mu"][2]),
                mu_BA=float(row["mu"][3]),
                rotation_signed=float(row["rotation_signed"]),
                rotation_folded=float(row["rotation_folded"]),
                rotation_coherence=float(row["rotation_coherence"]),
                recurrence_residual=float(row["recurrence_residual"]),
                stratum=row["stratum"],
                gap_phi=float(row["gap_distance"]["phi"]),
                drift_phi=float(row["drift_distance"]["phi"]),
                score_phi=float(row["score"]["phi"]),
            )
            csv_rows.append(asdict(record))
    with open(csv_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(csv_rows[0]))
        writer.writeheader()
        writer.writerows(csv_rows)

    print(json.dumps(result, indent=2, allow_nan=True))


if __name__ == "__main__":
    main()
