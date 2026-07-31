"""Frozen ARA test: Phi as a collective four-child handover.

Protocol:
    PHI_FOUR_CHILD_HANDOVER_PROTOCOL_2026-07-30.md

The endpoint uses raw angles, angular velocities and timestamps only.
"""
from __future__ import annotations

import csv
import json
import math
import os
from dataclasses import asdict, dataclass

import numpy as np
import scipy.io as sio
from scipy.stats import spearmanr


HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
DEVELOPMENT_FILE = "DoubleDataWithControl_1_Dt_0_0001.mat"
FROZEN_FILE = "DoubleDataWithControl_2_Dt_0_0001.mat"
DECIMATE = 20
MIN_CYCLE_S = 0.4 * 1.333
N_PERM = 5000
SEED = 20260730

PHI = (1.0 + math.sqrt(5.0)) / 2.0
U_PHI = 2.0 - PHI

GOLDEN = np.array([PHI**-4, PHI**-3, PHI**-2, PHI**-3], dtype=float)
TEMPLATES = {
    "phi_quartet": GOLDEN,
    "equal_quarters": np.array([0.25, 0.25, 0.25, 0.25]),
    "paired_dyadic": np.array([0.5, 0.0, 0.5, 0.0]),
    "linear_irregular": np.array([0.1, 0.2, 0.3, 0.4]),
}
LANDMARKS = {
    "phi": np.array([U_PHI, 1.0 - U_PHI]),
    "poles": np.array([0.0]),
    "ridge_opposition": np.array([0.5]),
    "quarters": np.array([0.25, 0.75]),
    "thirds": np.array([1.0 / 3.0, 2.0 / 3.0]),
}


@dataclass
class Cycle:
    split: str
    cycle: int
    start_sample: int
    stop_sample: int
    start_time_s: float
    stop_time_s: float
    period_s: float
    p_AA: float
    p_AB: float
    p_BB: float
    p_BA: float
    all_four_seen: bool
    completion_u: float
    transition_count: int
    inequality: float
    phi_template_distance: float
    equal_template_distance: float
    paired_template_distance: float
    linear_template_distance: float
    parent_amplitude: float
    parent_retention: float
    period_retention: float
    child_allocation_retention: float
    one_wave_phi_distance: float
    one_wave_equal_distance: float


def wrap(a: np.ndarray) -> np.ndarray:
    return (a + np.pi) % (2.0 * np.pi) - np.pi


def circular_center(a: np.ndarray) -> float:
    return float(np.arctan2(np.mean(np.sin(a)), np.mean(np.cos(a))))


def oriented_templates(template: np.ndarray) -> list[np.ndarray]:
    out: list[np.ndarray] = []
    for base in (template, template[::-1]):
        for shift in range(4):
            candidate = np.roll(base, shift)
            if not any(np.allclose(candidate, prior) for prior in out):
                out.append(candidate)
    return out


ORIENTED = {name: oriented_templates(value) for name, value in TEMPLATES.items()}


def template_distance(p: np.ndarray, name: str) -> float:
    return float(
        min(0.5 * np.sum(np.abs(p - candidate)) for candidate in ORIENTED[name])
    )


def circular_distance(values: np.ndarray, points: np.ndarray) -> np.ndarray:
    delta = np.abs(values[:, None] - points[None, :])
    return np.min(np.minimum(delta, 1.0 - delta), axis=1)


def entropy_inequality(p: np.ndarray) -> float:
    positive = p[p > 0.0]
    entropy = -float(np.sum(positive * np.log(positive)))
    return float(1.0 - entropy / math.log(4.0))


def retain(a: float, b: float) -> float:
    maximum = max(abs(a), abs(b))
    if maximum <= 1e-15:
        return float("nan")
    return float(min(abs(a), abs(b)) / maximum)


def load_double(filename: str) -> tuple[np.ndarray, dict[int, np.ndarray], dict[int, np.ndarray], float]:
    matrix = sio.loadmat(os.path.join(DATA, filename))
    q = DECIMATE
    t = matrix["Time"].ravel()[::q]
    theta = {i: matrix[f"Theta{i}"].ravel()[::q] for i in (1, 2)}
    velocity = {i: matrix[f"dTheta{i}"].ravel()[::q] for i in (1, 2)}
    dt = float(np.asarray(matrix["dt"]).ravel()[0])
    return t, theta, velocity, 1.0 / (dt * q)


def spaced_parent_crossings(
    q1: np.ndarray, v1: np.ndarray, t: np.ndarray
) -> np.ndarray:
    candidates = np.where(
        (q1[:-1] < 0.0) & (q1[1:] >= 0.0) & (v1[1:] > 0.0)
    )[0] + 1
    if len(candidates) == 0:
        return candidates
    kept = [int(candidates[0])]
    for index in candidates[1:]:
        if t[int(index)] - t[kept[-1]] >= MIN_CYCLE_S:
            kept.append(int(index))
    return np.asarray(kept, dtype=int)


def coupled_labels(q1: np.ndarray, q2: np.ndarray) -> np.ndarray:
    # Circular square order: AA (++), AB (+-), BB (--), BA (-+).
    a = q1 >= 0.0
    b = q2 >= 0.0
    return np.where(a & b, 0, np.where(a & ~b, 1, np.where(~a & ~b, 2, 3)))


def one_wave_labels(q1: np.ndarray, v1: np.ndarray) -> np.ndarray:
    # Same circular square order for position side x movement direction.
    a = q1 >= 0.0
    b = v1 >= 0.0
    return np.where(a & b, 0, np.where(a & ~b, 1, np.where(~a & ~b, 2, 3)))


def completion_phase(labels: np.ndarray) -> tuple[bool, float]:
    seen: set[int] = set()
    for i, label in enumerate(labels):
        seen.add(int(label))
        if len(seen) == 4:
            return True, float(i / len(labels))
    return False, float("nan")


def transition_count(labels: np.ndarray) -> int:
    if len(labels) == 0:
        return 0
    return int(1 + np.sum(labels[1:] != labels[:-1]))


def extract_cycles(filename: str, split: str) -> tuple[list[Cycle], dict]:
    t, theta, velocity, fs = load_double(filename)
    q1 = wrap(theta[1] - circular_center(theta[1]))
    q2 = wrap(theta[2] - circular_center(theta[2]))
    crossings = spaced_parent_crossings(q1, velocity[1], t)

    raw: list[dict] = []
    for index, (start, stop) in enumerate(zip(crossings[:-1], crossings[1:])):
        start, stop = int(start), int(stop)
        if stop - start < 5:
            continue
        labels = coupled_labels(q1[start:stop], q2[start:stop])
        counts = np.bincount(labels, minlength=4).astype(float)
        p = counts / counts.sum()
        all_four, completion = completion_phase(labels)

        wave_labels = one_wave_labels(
            q1[start:stop], velocity[1][start:stop]
        )
        wave_counts = np.bincount(wave_labels, minlength=4).astype(float)
        wave_p = wave_counts / wave_counts.sum()

        raw.append(
            {
                "cycle": index,
                "start": start,
                "stop": stop,
                "period": float(t[stop] - t[start]),
                "p": p,
                "all_four": all_four,
                "completion": completion,
                "transitions": transition_count(labels),
                "inequality": entropy_inequality(p),
                "distances": {
                    name: template_distance(p, name) for name in TEMPLATES
                },
                "amplitude": float(np.max(q1[start:stop]) - np.min(q1[start:stop])),
                "wave_phi_distance": template_distance(wave_p, "phi_quartet"),
                "wave_equal_distance": template_distance(wave_p, "equal_quarters"),
            }
        )

    cycles: list[Cycle] = []
    for i, row in enumerate(raw):
        if i + 1 < len(raw):
            nxt = raw[i + 1]
            parent_retention = retain(row["amplitude"], nxt["amplitude"])
            period_retention = retain(row["period"], nxt["period"])
            child_retention = float(
                1.0 - 0.5 * np.sum(np.abs(row["p"] - nxt["p"]))
            )
        else:
            parent_retention = float("nan")
            period_retention = float("nan")
            child_retention = float("nan")
        p = row["p"]
        cycles.append(
            Cycle(
                split=split,
                cycle=int(row["cycle"]),
                start_sample=int(row["start"]),
                stop_sample=int(row["stop"]),
                start_time_s=float(t[row["start"]]),
                stop_time_s=float(t[row["stop"]]),
                period_s=float(row["period"]),
                p_AA=float(p[0]),
                p_AB=float(p[1]),
                p_BB=float(p[2]),
                p_BA=float(p[3]),
                all_four_seen=bool(row["all_four"]),
                completion_u=float(row["completion"]),
                transition_count=int(row["transitions"]),
                inequality=float(row["inequality"]),
                phi_template_distance=float(row["distances"]["phi_quartet"]),
                equal_template_distance=float(row["distances"]["equal_quarters"]),
                paired_template_distance=float(row["distances"]["paired_dyadic"]),
                linear_template_distance=float(row["distances"]["linear_irregular"]),
                parent_amplitude=float(row["amplitude"]),
                parent_retention=parent_retention,
                period_retention=period_retention,
                child_allocation_retention=child_retention,
                one_wave_phi_distance=float(row["wave_phi_distance"]),
                one_wave_equal_distance=float(row["wave_equal_distance"]),
            )
        )
    return cycles, {
        "filename": filename,
        "n_samples": int(len(t)),
        "duration_s": float(t[-1] - t[0]),
        "fs_hz": float(fs),
        "n_parent_crossings": int(len(crossings)),
        "n_cycles": int(len(cycles)),
    }


def shift_test(x: np.ndarray, y: np.ndarray, rng: np.random.Generator) -> dict:
    valid = np.isfinite(x) & np.isfinite(y)
    x, y = x[valid], y[valid]
    if len(x) < 12:
        return {"n": int(len(x)), "spearman_r": float("nan"), "p": float("nan")}
    observed = float(spearmanr(x, y).statistic)
    min_shift = min(5, max(1, len(y) // 4))
    allowed = np.arange(min_shift, len(y) - min_shift + 1)
    null = np.empty(N_PERM, dtype=float)
    for i in range(N_PERM):
        shifted = np.roll(y, int(rng.choice(allowed)))
        null[i] = float(spearmanr(x, shifted).statistic)
    p = float((1 + np.sum(null >= observed)) / (N_PERM + 1))
    return {
        "n": int(len(x)),
        "spearman_r": observed,
        "p_one_sided_circular_shift": p,
        "null_median": float(np.nanmedian(null)),
        "null_q95": float(np.nanquantile(null, 0.95)),
    }


def summarize(cycles: list[Cycle], rng: np.random.Generator) -> dict:
    template = {
        "phi_quartet": float(np.median([c.phi_template_distance for c in cycles])),
        "equal_quarters": float(np.median([c.equal_template_distance for c in cycles])),
        "paired_dyadic": float(np.median([c.paired_template_distance for c in cycles])),
        "linear_irregular": float(np.median([c.linear_template_distance for c in cycles])),
    }
    completion = np.array(
        [c.completion_u for c in cycles if c.all_four_seen], dtype=float
    )
    landmark = {
        name: (
            float(np.median(circular_distance(completion, points)))
            if len(completion)
            else float("nan")
        )
        for name, points in LANDMARKS.items()
    }
    inequality = np.array([c.inequality for c in cycles[:-1]], dtype=float)
    phi_proximity = 1.0 - np.array(
        [c.phi_template_distance for c in cycles[:-1]], dtype=float
    )
    parent_retention = np.array(
        [c.parent_retention for c in cycles[:-1]], dtype=float
    )
    return {
        "n_cycles": int(len(cycles)),
        "all_four_seen_n": int(sum(c.all_four_seen for c in cycles)),
        "all_four_seen_fraction": float(np.mean([c.all_four_seen for c in cycles])),
        "median_transition_count": float(
            np.median([c.transition_count for c in cycles])
        ),
        "median_child_shares": {
            name: float(np.median([getattr(c, f"p_{name}") for c in cycles]))
            for name in ("AA", "AB", "BB", "BA")
        },
        "template_median_total_variation_distance": template,
        "completion_landmark_median_circular_distance": landmark,
        "inequality_median": float(np.median([c.inequality for c in cycles])),
        "parent_retention_median": float(
            np.nanmedian([c.parent_retention for c in cycles])
        ),
        "inequality_to_parent_retention": shift_test(
            inequality, parent_retention, rng
        ),
        "phi_proximity_to_parent_retention": shift_test(
            phi_proximity, parent_retention, rng
        ),
        "secondary": {
            "period_retention_median": float(
                np.nanmedian([c.period_retention for c in cycles])
            ),
            "child_allocation_retention_median": float(
                np.nanmedian([c.child_allocation_retention for c in cycles])
            ),
            "one_wave_phi_template_median_distance": float(
                np.median([c.one_wave_phi_distance for c in cycles])
            ),
            "one_wave_equal_quarters_median_distance": float(
                np.median([c.one_wave_equal_distance for c in cycles])
            ),
        },
    }


def verdict(frozen: dict) -> dict:
    template = frozen["template_median_total_variation_distance"]
    landmark = frozen["completion_landmark_median_circular_distance"]
    inequality = frozen["inequality_to_parent_retention"]
    phi_retention = frozen["phi_proximity_to_parent_retention"]
    checks = {
        "phi_quartet_best_template": template["phi_quartet"]
        < min(value for key, value in template.items() if key != "phi_quartet"),
        "completion_closest_to_phi": landmark["phi"]
        < min(value for key, value in landmark.items() if key != "phi"),
        "inequality_maintains_parent": (
            inequality["spearman_r"] > 0.0
            and inequality["p_one_sided_circular_shift"] < 0.05
        ),
        "phi_proximity_maintains_parent": (
            phi_retention["spearman_r"] > 0.0
            and phi_retention["p_one_sided_circular_shift"] < 0.05
        ),
    }
    passed = int(sum(checks.values()))
    label = "SUPPORTED" if passed == 4 else ("MIXED" if passed >= 2 else "NOT SUPPORTED")
    return {"label": label, "checks_passed": passed, "checks": checks}


def write_csv(path: str, cycles: list[Cycle]) -> None:
    rows = [asdict(cycle) for cycle in cycles]
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    development_cycles, development_meta = extract_cycles(
        DEVELOPMENT_FILE, "development"
    )
    frozen_cycles, frozen_meta = extract_cycles(FROZEN_FILE, "frozen")

    rng = np.random.default_rng(SEED)
    development = summarize(development_cycles, rng)
    frozen = summarize(frozen_cycles, rng)
    result = {
        "protocol": "PHI_FOUR_CHILD_HANDOVER_PROTOCOL_2026-07-30.md",
        "data": {
            "source": "dynamicslab MultiArm-Pendulum",
            "doi": "10.5281/zenodo.6633719",
            "development": development_meta,
            "frozen": frozen_meta,
        },
        "constants": {
            "phi": PHI,
            "u_phi": U_PHI,
            "golden_quartet": GOLDEN.tolist(),
            "decimate": DECIMATE,
            "min_cycle_s": MIN_CYCLE_S,
            "permutations": N_PERM,
            "seed": SEED,
        },
        "development": development,
        "frozen": frozen,
        "verdict": verdict(frozen),
    }

    json_path = os.path.join(HERE, "phi_four_child_handover_results.json")
    csv_path = os.path.join(HERE, "phi_four_child_handover_cycles.csv")
    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, allow_nan=True)
    write_csv(csv_path, development_cycles + frozen_cycles)
    print(json.dumps(result, indent=2, allow_nan=True))


if __name__ == "__main__":
    main()
