"""T301: Phi as orientation advance of a breathing ARA state-sphere.

Protocol:
  PHI_SPHERE_BREATHING_PROTOCOL_2026-07-30.md

The endpoint uses only raw pendulum angles, circular-mean centring, radial
maxima, and spherical angles between successive maximum directions.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.io import loadmat
from scipy.signal import find_peaks
from scipy.stats import spearmanr


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
EXTERNAL_DOUBLE = Path(
    r"F:\SystemFormulaFolder\external_data\MultiArm-Pendulum\DoublePendulum"
)
OUT_JSON = HERE / "phi_sphere_breathing_results.json"
OUT_CSV = HERE / "phi_sphere_breathing_events.csv"
OUT_PNG = HERE / "PHI_SPHERE_BREATHING_DIAGNOSTICS.png"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
CANDIDATES = {
    "recurrence": 0.0,
    "pi_conjugate": math.pi - 3.0,
    "quarter": 0.25,
    "e_conjugate": 3.0 - math.e,
    "third": 1.0 / 3.0,
    "three_eighths": 3.0 / 8.0,
    "phi": PHI ** -2,
    "two_fifths": 2.0 / 5.0,
    "silver": math.sqrt(2.0) - 1.0,
    "opposition": 0.5,
}

DOUBLE_RUNS = {
    "double_run1": DATA / "pend_double.mat",
    "double_run2": EXTERNAL_DOUBLE / "DoubleDataFreeSwing_2_Dt_0_001.mat",
    "double_run3": EXTERNAL_DOUBLE / "DoubleDataFreeSwing_3_Dt_0_001.mat",
    "double_run4": EXTERNAL_DOUBLE / "DoubleDataFreeSwing_4_Dt_0_001.mat",
}
TRIPLE_RUNS = {
    "triple_run1": DATA / "pend_triple.mat",
    "triple_run2": DATA / "tri2.mat",
    "triple_run3": DATA / "tri3.mat",
}

PRIMARY_PROMINENCE = 0.05
PRIMARY_SPACING = 0.20
REFERENCE_PERIOD_S = 1.333
TARGET_FS = 1000.0
RNG_SEED = 20260730
N_PERM = 5000


def wrap(a: np.ndarray) -> np.ndarray:
    return (a + np.pi) % (2.0 * np.pi) - np.pi


def circular_center(x: np.ndarray) -> np.ndarray:
    rest = math.atan2(float(np.mean(np.sin(x))), float(np.mean(np.cos(x))))
    return wrap(x - rest)


def load_angles(path: Path, dimension: int) -> tuple[np.ndarray, np.ndarray, float]:
    if not path.exists():
        raise FileNotFoundError(path)
    m = loadmat(path)
    t = np.asarray(m["Time"]).ravel().astype(float)
    q = np.column_stack(
        [circular_center(np.asarray(m[f"Theta{i}"]).ravel().astype(float))
         for i in range(1, dimension + 1)]
    )
    dt = float(np.asarray(m["dt"]).ravel()[0])
    raw_fs = 1.0 / dt
    stride = max(1, int(round(raw_fs / TARGET_FS)))
    return t[::stride], q[::stride], raw_fs / stride


def detect_radial_maxima(
    q: np.ndarray,
    fs: float,
    prominence_fraction: float,
    spacing_fraction: float,
) -> tuple[np.ndarray, np.ndarray]:
    radius = np.linalg.norm(q, axis=1)
    q05, q95 = np.quantile(radius, [0.05, 0.95])
    scale = max(float(q95 - q05), np.finfo(float).eps)
    min_distance = max(
        1, int(round(spacing_fraction * REFERENCE_PERIOD_S * fs))
    )
    peaks, _ = find_peaks(
        radius,
        prominence=prominence_fraction * scale,
        distance=min_distance,
    )
    peaks = peaks[radius[peaks] > np.finfo(float).eps]
    return radius, peaks


def spherical_step(u: np.ndarray, v: np.ndarray) -> float:
    nu = float(np.linalg.norm(u))
    nv = float(np.linalg.norm(v))
    if nu <= 0.0 or nv <= 0.0:
        return float("nan")
    cosine = float(np.clip(np.dot(u, v) / (nu * nv), -1.0, 1.0))
    return float(math.acos(cosine) / (2.0 * math.pi))


def event_rows(
    run: str,
    dimension: int,
    t: np.ndarray,
    q: np.ndarray,
    radius: np.ndarray,
    peaks: np.ndarray,
) -> list[dict]:
    rows: list[dict] = []
    for lag in (1, 2):
        for i in range(0, len(peaks) - lag):
            p0 = int(peaks[i])
            p1 = int(peaks[i + lag])
            delta = spherical_step(q[p0], q[p1])
            retention = float(
                min(radius[p0], radius[p1]) / max(radius[p0], radius[p1])
            )
            row = {
                "run": run,
                "dimension": dimension,
                "lag": lag,
                "peak_index_0": p0,
                "peak_index_1": p1,
                "time_0_s": float(t[p0]),
                "time_1_s": float(t[p1]),
                "radius_0": float(radius[p0]),
                "radius_1": float(radius[p1]),
                "delta_turn": delta,
                "retention": retention,
            }
            for name, value in CANDIDATES.items():
                row[f"distance_{name}"] = abs(delta - value)
                row[f"proximity_{name}"] = 1.0 - abs(delta - value) / 0.5
            rows.append(row)
    return rows


def median_distances(rows: list[dict], names: list[str]) -> dict[str, float]:
    return {
        candidate: float(
            np.median([r[f"distance_{candidate}"] for r in rows])
        )
        for candidate in names
    }


def winner(distances: dict[str, float]) -> str:
    return min(distances, key=lambda k: (distances[k], k))


def pooled_spearman(
    rows: list[dict], candidate: str, run_names: list[str]
) -> tuple[float, dict[str, float], dict[str, int]]:
    correlations: dict[str, float] = {}
    counts: dict[str, int] = {}
    weighted_z = 0.0
    total_weight = 0.0
    for run in run_names:
        rr = [r for r in rows if r["run"] == run and r["lag"] == 2]
        if len(rr) < 4:
            continue
        x = np.asarray([r[f"proximity_{candidate}"] for r in rr])
        y = np.asarray([r["retention"] for r in rr])
        rho = float(spearmanr(x, y).statistic)
        if not np.isfinite(rho):
            continue
        correlations[run] = rho
        counts[run] = len(rr)
        weight = max(len(rr) - 3, 1)
        weighted_z += weight * np.arctanh(np.clip(rho, -0.999999, 0.999999))
        total_weight += weight
    pooled = float(np.tanh(weighted_z / total_weight)) if total_weight else float("nan")
    return pooled, correlations, counts


def shift_pvalue(
    rows: list[dict],
    candidate: str,
    run_names: list[str],
    observed: float,
    n_perm: int = N_PERM,
) -> float:
    rng = np.random.default_rng(RNG_SEED)
    by_run: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for run in run_names:
        rr = [r for r in rows if r["run"] == run and r["lag"] == 2]
        if len(rr) < 8:
            continue
        x = np.asarray([r[f"proximity_{candidate}"] for r in rr])
        y = np.asarray([r["retention"] for r in rr])
        by_run[run] = (x, y)

    null = np.empty(n_perm, dtype=float)
    for b in range(n_perm):
        weighted_z = 0.0
        total_weight = 0.0
        for x, y in by_run.values():
            # Circular shifts retain each series' serial structure.
            lo = min(5, len(y) - 1)
            allowed = np.arange(lo, len(y) - lo + 1)
            if len(allowed) == 0:
                shift = int(rng.integers(1, len(y)))
            else:
                shift = int(rng.choice(allowed))
            rho = float(spearmanr(x, np.roll(y, shift)).statistic)
            if not np.isfinite(rho):
                continue
            weight = max(len(y) - 3, 1)
            weighted_z += weight * np.arctanh(
                np.clip(rho, -0.999999, 0.999999)
            )
            total_weight += weight
        null[b] = (
            float(np.tanh(weighted_z / total_weight))
            if total_weight else float("nan")
        )
    valid = null[np.isfinite(null)]
    return float((1 + np.sum(valid >= observed)) / (1 + len(valid)))


def star_discrepancy(points: np.ndarray) -> float:
    x = np.sort(points % 1.0)
    n = len(x)
    upper = np.max(np.arange(1, n + 1) / n - x)
    lower = np.max(x - np.arange(0, n) / n)
    return float(max(upper, lower))


def geometry_benchmark() -> dict:
    names = [
        k for k in CANDIDATES
        if k not in {"recurrence", "opposition"}
    ]
    rows = []
    wins = {
        "recurrence_avoidance": {k: 0 for k in names},
        "largest_gap": {k: 0 for k in names},
        "discrepancy": {k: 0 for k in names},
    }
    for n in range(4, 201):
        metrics = {}
        for name in names:
            a = CANDIDATES[name]
            pts = (np.arange(n, dtype=float) * a) % 1.0
            ordered = np.sort(pts)
            gaps = np.diff(np.r_[ordered, ordered[0] + 1.0])
            recurrence = float(
                np.min(
                    np.minimum(
                        (np.arange(1, n + 1) * a) % 1.0,
                        1.0 - ((np.arange(1, n + 1) * a) % 1.0),
                    )
                )
            )
            metrics[name] = {
                "recurrence_avoidance": recurrence,
                "largest_gap": float(np.max(gaps)),
                "discrepancy": star_discrepancy(pts),
            }
            rows.append({"n": n, "candidate": name, **metrics[name]})
        best_rec = max(names, key=lambda k: metrics[k]["recurrence_avoidance"])
        best_gap = min(names, key=lambda k: metrics[k]["largest_gap"])
        best_disc = min(names, key=lambda k: metrics[k]["discrepancy"])
        wins["recurrence_avoidance"][best_rec] += 1
        wins["largest_gap"][best_gap] += 1
        wins["discrepancy"][best_disc] += 1
    return {"horizon_rows": rows, "win_counts": wins}


def sensitivity(path: Path, dimension: int) -> list[dict]:
    t, q, fs = load_angles(path, dimension)
    out = []
    for prom in (0.02, 0.05, 0.10):
        for spacing in (0.15, 0.20, 0.30):
            radius, peaks = detect_radial_maxima(q, fs, prom, spacing)
            rows = event_rows("sensitivity", dimension, t, q, radius, peaks)
            lag2 = [r for r in rows if r["lag"] == 2]
            distances = median_distances(lag2, list(CANDIDATES))
            out.append(
                {
                    "prominence_fraction": prom,
                    "spacing_fraction": spacing,
                    "n_peaks": int(len(peaks)),
                    "n_lag2": int(len(lag2)),
                    "winner": winner(distances),
                    "phi_distance": distances["phi"],
                    "three_eighths_distance": distances["three_eighths"],
                    "two_fifths_distance": distances["two_fifths"],
                    "recurrence_distance": distances["recurrence"],
                    "opposition_distance": distances["opposition"],
                }
            )
    return out


def plot_results(results: dict, rows: list[dict]) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))

    order = list(CANDIDATES)
    labels = [
        "0", "π−3", "1/4", "3−e", "1/3", "3/8",
        "φ⁻²", "2/5", "√2−1", "1/2"
    ]
    x = np.arange(len(order))

    for ax, key, title in (
        (axes[0, 0], "double_frozen", "2D complete-breath candidate distance"),
        (axes[0, 1], "triple_frozen", "3D complete-breath candidate distance"),
    ):
        vals = [results["candidate_distances"][key][k] for k in order]
        colors = ["#d99b2b" if k == "phi" else "#8da0b5" for k in order]
        ax.bar(x, vals, color=colors, edgecolor="#425466")
        ax.set_xticks(x, labels, rotation=45, ha="right")
        ax.set_ylabel("median |observed step − candidate|")
        ax.set_title(title)

    lag2_double = [
        r["delta_turn"] for r in rows
        if r["lag"] == 2 and r["run"] in {"double_run2", "double_run3"}
    ]
    lag2_triple = [
        r["delta_turn"] for r in rows
        if r["lag"] == 2 and r["run"] == "triple_run2"
    ]
    bins = np.linspace(0, 0.5, 41)
    axes[1, 0].hist(
        lag2_double, bins=bins, alpha=0.60, label="2D double", color="#4c78a8"
    )
    axes[1, 0].hist(
        lag2_triple, bins=bins, alpha=0.60, label="3D triple", color="#59a14f"
    )
    axes[1, 0].axvline(CANDIDATES["phi"], color="#e28e2c", lw=2, label="φ⁻²")
    axes[1, 0].axvline(3 / 8, color="#777", lw=1.5, ls="--", label="3/8")
    axes[1, 0].axvline(2 / 5, color="#222", lw=1.5, ls=":", label="2/5")
    axes[1, 0].set_xlabel("orientation advance (fraction of full turn)")
    axes[1, 0].set_ylabel("events")
    axes[1, 0].set_title("Observed complete-breath advances")
    axes[1, 0].legend()

    geom = results["geometry_benchmark"]["win_counts"]
    geom_names = [
        "pi_conjugate", "quarter", "e_conjugate", "third",
        "three_eighths", "phi", "two_fifths", "silver"
    ]
    gx = np.arange(len(geom_names))
    width = 0.26
    axes[1, 1].bar(
        gx - width,
        [geom["recurrence_avoidance"][k] for k in geom_names],
        width,
        label="avoid recurrence",
    )
    axes[1, 1].bar(
        gx,
        [geom["largest_gap"][k] for k in geom_names],
        width,
        label="small largest gap",
    )
    axes[1, 1].bar(
        gx + width,
        [geom["discrepancy"][k] for k in geom_names],
        width,
        label="low discrepancy",
    )
    axes[1, 1].set_xticks(
        gx,
        ["π−3", "1/4", "3−e", "1/3", "3/8", "φ⁻²", "2/5", "√2−1"],
        rotation=45,
        ha="right",
    )
    axes[1, 1].set_ylabel("horizons won, N=4…200")
    axes[1, 1].set_title("Controlled circle generator benchmark")
    axes[1, 1].legend(fontsize=8)

    fig.suptitle(
        f"T301 Phi sphere-breathing test — {results['verdict']}",
        fontsize=16,
        fontweight="bold",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(OUT_PNG, dpi=180)
    plt.close(fig)


def main() -> None:
    rows: list[dict] = []
    run_meta: dict[str, dict] = {}
    for run, path in {**DOUBLE_RUNS, **TRIPLE_RUNS}.items():
        dimension = 2 if run.startswith("double") else 3
        t, q, fs = load_angles(path, dimension)
        radius, peaks = detect_radial_maxima(
            q, fs, PRIMARY_PROMINENCE, PRIMARY_SPACING
        )
        rr = event_rows(run, dimension, t, q, radius, peaks)
        rows.extend(rr)
        run_meta[run] = {
            "path": str(path),
            "dimension": dimension,
            "n_samples": int(len(t)),
            "fs_hz": float(fs),
            "duration_s": float(t[-1] - t[0]),
            "n_radial_maxima": int(len(peaks)),
            "n_lag1": int(sum(r["lag"] == 1 for r in rr)),
            "n_lag2": int(sum(r["lag"] == 2 for r in rr)),
        }

    groups = {
        "double_development": ["double_run1"],
        "double_frozen": ["double_run2", "double_run3"],
        "double_confirmation": ["double_run4"],
        "triple_development": ["triple_run1"],
        "triple_frozen": ["triple_run2"],
        "triple_confirmation": ["triple_run3"],
    }
    candidate_distances: dict[str, dict] = {}
    candidate_winners: dict[str, str] = {}
    lag1_distances: dict[str, dict] = {}
    for group, names in groups.items():
        lag2 = [r for r in rows if r["run"] in names and r["lag"] == 2]
        lag1 = [r for r in rows if r["run"] in names and r["lag"] == 1]
        candidate_distances[group] = median_distances(
            lag2, list(CANDIDATES)
        )
        candidate_winners[group] = winner(candidate_distances[group])
        lag1_distances[group] = median_distances(lag1, list(CANDIDATES))

    maintenance_names = [
        "recurrence", "three_eighths", "phi", "two_fifths", "opposition"
    ]
    maintenance_runs = [
        "double_run2", "double_run3", "triple_run2"
    ]
    maintenance: dict[str, dict] = {}
    for name in maintenance_names:
        pooled, per_run, counts = pooled_spearman(rows, name, maintenance_runs)
        maintenance[name] = {
            "pooled_spearman": pooled,
            "per_run": per_run,
            "event_counts": counts,
        }
    maintenance["phi"]["shift_p_one_sided"] = shift_pvalue(
        rows,
        "phi",
        maintenance_runs,
        maintenance["phi"]["pooled_spearman"],
    )

    check1 = candidate_winners["double_frozen"] == "phi"
    check2 = candidate_winners["triple_frozen"] == "phi"
    check3 = (
        candidate_winners["double_confirmation"] == "phi"
        and candidate_winners["triple_confirmation"] == "phi"
    )
    phi_rho = maintenance["phi"]["pooled_spearman"]
    comparator_rhos = [
        maintenance[k]["pooled_spearman"]
        for k in ("recurrence", "three_eighths", "two_fifths", "opposition")
    ]
    check4 = (
        phi_rho > 0
        and maintenance["phi"]["shift_p_one_sided"] < 0.05
        and all(phi_rho > x for x in comparator_rhos)
    )
    passed = int(check1) + int(check2) + int(check3) + int(check4)
    verdict = (
        "SUPPORTED" if passed == 4
        else "MIXED" if passed >= 2
        else "NOT SUPPORTED"
    )

    geometry = geometry_benchmark()
    results = {
        "test_id": "T301-PHI-SPHERE-BREATHING-v1",
        "verdict": f"{verdict} ({passed}/4)",
        "phi": PHI,
        "phi_conjugate": PHI ** -2,
        "primary_detector": {
            "prominence_fraction": PRIMARY_PROMINENCE,
            "spacing_fraction_of_1_333s": PRIMARY_SPACING,
            "target_sampling_hz": TARGET_FS,
        },
        "run_metadata": run_meta,
        "candidate_distances": candidate_distances,
        "lag1_candidate_distances": lag1_distances,
        "candidate_winners": candidate_winners,
        "maintenance": maintenance,
        "checks": {
            "double_frozen_phi_best": check1,
            "triple_frozen_phi_best": check2,
            "both_confirmations_phi_best": check3,
            "phi_uniquely_predicts_retention": check4,
            "passed": passed,
            "total": 4,
        },
        "sensitivity": {
            "double_run3": sensitivity(DOUBLE_RUNS["double_run3"], 2),
            "triple_run3": sensitivity(TRIPLE_RUNS["triple_run3"], 3),
        },
        "geometry_benchmark": geometry,
        "boundaries": [
            "All empirical source records were used in earlier, different analyses.",
            "State-space radius is a declared ARA cut, not literal spatial radius.",
            "The controlled generator benchmark is not empirical evidence for Phi.",
            "The fixed pivot does not supply an external common-mode galactic-like carrier.",
        ],
    }

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        fieldnames = list(rows[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Horizon rows are numerous; keep them out of the main JSON after plotting.
    plot_results(results, rows)
    compact = dict(results)
    compact["geometry_benchmark"] = {
        "win_counts": geometry["win_counts"],
        "horizon_range": [4, 200],
    }
    OUT_JSON.write_text(
        json.dumps(compact, indent=2, allow_nan=False), encoding="utf-8"
    )
    print(json.dumps({
        "verdict": compact["verdict"],
        "candidate_winners": candidate_winners,
        "maintenance": maintenance,
        "checks": compact["checks"],
        "geometry_win_counts": compact["geometry_benchmark"]["win_counts"],
        "outputs": [str(OUT_JSON), str(OUT_CSV), str(OUT_PNG)],
    }, indent=2))


if __name__ == "__main__":
    main()
