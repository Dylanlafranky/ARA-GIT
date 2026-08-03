"""Independent validator for T333.

The validator deliberately does not import the primary runner.  It rebuilds
the registered ratios, endpoints, candidates, quadrants, nulls and gates from
the checksum-locked Q53 event archive.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ROOT = REPO.parents[1]
QUANTUM = REPO / "analysis" / "quantum"
SOURCE = ROOT / "external_data" / "quantum" / "eth_single_ion_contextuality_2017" / "ExpDataYuOh.csv"
EVENTS = QUANTUM / "Q53_RECORDED_QUTRIT_EXTERNAL_RETURN_EVENTS.npz"
PROTOCOL = HERE / "T333_RECORDED_QUTRIT_RECIPROCAL_RADIAL_BREATHING_PROTOCOL_v1_FROZEN.md"
RESULTS = HERE / "T333_RECORDED_QUTRIT_RECIPROCAL_RADIAL_BREATHING_RESULTS.json"
CELLS = HERE / "T333_RECORDED_QUTRIT_RECIPROCAL_RADIAL_BREATHING_CELLS.csv"
QUADRANTS = HERE / "T333_RECORDED_QUTRIT_RECIPROCAL_RADIAL_BREATHING_QUADRANTS.csv"
NULLS = HERE / "T333_RECORDED_QUTRIT_RECIPROCAL_RADIAL_BREATHING_NULLS.csv"
FIGURE = HERE / "T333_RECORDED_QUTRIT_RECIPROCAL_RADIAL_BREATHING.png"
OUT = HERE / "T333_RECORDED_QUTRIT_RECIPROCAL_RADIAL_BREATHING_VALIDATION.json"

SOURCE_HASH = "5410775c307edea9f68e95133cf0a733b6cd34e7d9d774b6509472face74d55d"
PROTOCOL_HASH = "81a05e47746d6cc2829f658af7376b78e2c0f90e12001fecbea420c8c0e03f93"
PLANES = ("psi0_psi1", "psi1_psi2", "psi2_psi0")
EXPECTED = (168_399, 169_035, 168_456)
ESTIMATORS = ("circle", "centroid", "extrema")
LAGS = (1, 2, 4, 8, 16, 32, 64)
MAX_GAP = 2200
SHUFFLES = 500
BLOCK = 10_000
SEED = 3_332_026
PHI = (1.0 + math.sqrt(5.0)) / 2.0
CANDIDATES = {
    "plastic": 1.324717957244746,
    "sqrt2": math.sqrt(2.0),
    "three_halves": 1.5,
    "phi": PHI,
    "octave": 2.0,
    "e": math.e,
}


def hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def close(left: float, right: float, atol: float = 2e-12) -> bool:
    return math.isclose(float(left), float(right), rel_tol=1e-10, abs_tol=atol)


def read_planes() -> dict[str, dict[str, np.ndarray]]:
    z = np.load(EVENTS)
    out = {}
    for plane in PLANES:
        part = {
            "time": np.asarray(z[f"{plane}_time"], dtype=np.int64),
            "residual": np.asarray(z[f"{plane}_residual"], dtype=float),
        }
        for estimator in ESTIMATORS:
            part[f"{estimator}_heading"] = np.asarray(z[f"{plane}_{estimator}_heading"], dtype=float)
            part[f"{estimator}_strength"] = np.asarray(z[f"{plane}_{estimator}_strength"], dtype=float)
        out[plane] = part
    return out


def valid(part: dict[str, np.ndarray], estimator: str) -> np.ndarray:
    return (
        np.isfinite(part[f"{estimator}_heading"])
        & np.isfinite(part[f"{estimator}_strength"])
        & np.isfinite(part["residual"])
        & (part[f"{estimator}_strength"] >= 0.01)
        & (part["residual"] <= 0.25)
    )


def pair_indices(part, estimator, start, stop, lag):
    base = np.arange(start, stop - lag, dtype=np.int64)
    broken = np.diff(part["time"]) > MAX_GAP
    cumulative = np.r_[0, np.cumsum(broken)]
    keep = (
        valid(part, estimator)[base]
        & valid(part, estimator)[base + lag]
        & ((cumulative[base + lag] - cumulative[base]) == 0)
    )
    left = base[keep]
    return left, left + lag


def ratios(part, estimator, start, stop, lag, amplitude=None):
    if amplitude is None:
        amplitude = part[f"{estimator}_strength"]
    left, right = pair_indices(part, estimator, start, stop, lag)
    return amplitude[right] / amplitude[left]


def summary(values):
    contracting = values[values < 1.0]
    expanding = values[values > 1.0]
    mc = float(np.median(contracting))
    me = float(np.median(expanding))
    scores = {
        name: abs(math.log(mc) + math.log(alpha)) + abs(math.log(me) - math.log(alpha))
        for name, alpha in CANDIDATES.items()
    }
    return {
        "n": int(values.size),
        "mc": mc,
        "me": me,
        "product": mc * me,
        "scores": scores,
        "winner": min(scores, key=scores.get),
    }


def pooled(part, estimator, start, stop, amplitude=None):
    return np.concatenate([ratios(part, estimator, start, stop, lag, amplitude) for lag in LAGS])


def permute_amplitudes(amplitude, mask, start, stop, rng):
    copy = amplitude.copy()
    for left in range(start, stop, BLOCK):
        right = min(stop, left + BLOCK)
        positions = np.flatnonzero(mask[left:right]) + left
        if positions.size > 1:
            copy[positions] = rng.permutation(copy[positions])
    return copy


def main() -> None:
    registered = json.loads(RESULTS.read_text(encoding="utf-8"))
    planes = read_planes()
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"name": name, "pass": bool(passed), "detail": detail})

    check("source_sha256", hash_file(SOURCE) == SOURCE_HASH, hash_file(SOURCE))
    check("protocol_sha256", hash_file(PROTOCOL) == PROTOCOL_HASH, hash_file(PROTOCOL))
    observed_counts = tuple(len(planes[p]["time"]) for p in PLANES)
    check("registered_event_counts", observed_counts == EXPECTED, observed_counts)

    reconstructed_cells = []
    pool_store = {}
    for estimator in ESTIMATORS:
        for plane in PLANES:
            part = planes[plane]
            mid = len(part["time"]) // 2
            for split, start, stop in (("calibration", 0, mid), ("holdout", mid, len(part["time"]))):
                pieces = []
                for lag in LAGS:
                    values = ratios(part, estimator, start, stop, lag)
                    item = summary(values)
                    reconstructed_cells.append((plane, estimator, split, lag, item))
                    pieces.append(values)
                pool_store[(plane, estimator, split)] = np.concatenate(pieces)

    train = np.concatenate([pool_store[(p, "circle", "calibration")] for p in PLANES])
    holdout = np.concatenate([pool_store[(p, "circle", "holdout")] for p in PLANES])
    train_sum = summary(train)
    holdout_sum = summary(holdout)
    fit_alpha = math.exp(0.5 * (math.log(train_sum["me"]) - math.log(train_sum["mc"])))
    fit_score = abs(math.log(holdout_sum["mc"]) + math.log(fit_alpha)) + abs(math.log(holdout_sum["me"]) - math.log(fit_alpha))
    reg_train = registered["calibration"]["pooled_primary"]
    reg_hold = registered["holdout"]["pooled_primary"]
    check(
        "pooled_train_endpoints",
        close(train_sum["mc"], reg_train["median_contracting"]) and close(train_sum["me"], reg_train["median_expanding"]),
        {"contracting": train_sum["mc"], "expanding": train_sum["me"]},
    )
    check(
        "fitted_alpha",
        close(fit_alpha, registered["calibration"]["fitted_reciprocal_alpha"]),
        fit_alpha,
    )
    check(
        "pooled_holdout_endpoints",
        close(holdout_sum["mc"], reg_hold["median_contracting"]) and close(holdout_sum["me"], reg_hold["median_expanding"]),
        {"contracting": holdout_sum["mc"], "expanding": holdout_sum["me"]},
    )
    check("fitted_holdout_score", close(fit_score, registered["holdout"]["fitted_alpha_score"]), fit_score)

    with CELLS.open("r", encoding="utf-8", newline="") as handle:
        saved_cells = list(csv.DictReader(handle))
    cells_match = len(saved_cells) == len(reconstructed_cells)
    phi_wins = 0
    if cells_match:
        for saved, reconstructed in zip(saved_cells, reconstructed_cells):
            plane, estimator, split, lag, item = reconstructed
            cells_match &= saved["plane"] == plane and saved["estimator"] == estimator and saved["split"] == split and int(saved["lag"]) == lag
            cells_match &= close(float(saved["median_contracting"]), item["mc"])
            cells_match &= close(float(saved["median_expanding"]), item["me"])
            cells_match &= saved["winner"] == item["winner"]
            if estimator == "circle" and split == "holdout" and item["winner"] == "phi":
                phi_wins += 1
    check("all_cell_scores", cells_match, {"rows": len(saved_cells), "phi_wins": phi_wins})
    check("registered_phi_win_count", phi_wins == registered["gates"]["g2_phi_wins_of_21"], phi_wins)

    reconstructed_quadrants = []
    for plane in PLANES:
        part = planes[plane]
        mid = len(part["time"]) // 2
        left, right = pair_indices(part, "circle", mid, len(part["time"]), 1)
        amplitude = part["circle_strength"]
        log_s = np.log(amplitude[right] / amplitude[left])
        phase = 2 * math.pi * (part["circle_heading"][right] - part["circle_heading"][left])
        delta = np.arctan2(np.sin(phase), np.cos(phase))
        usable = (log_s != 0.0) & (delta != 0.0)
        reconstructed_quadrants.append({
            "plane": plane,
            "valid_steps": int(np.sum(usable)),
            "shares": [
                float(np.mean((log_s < 0) & (delta < 0))),
                float(np.mean((log_s < 0) & (delta > 0))),
                float(np.mean((log_s > 0) & (delta < 0))),
                float(np.mean((log_s > 0) & (delta > 0))),
            ],
        })
    quadrant_match = True
    for rebuilt, saved in zip(reconstructed_quadrants, registered["quadrants"]):
        quadrant_match &= rebuilt["plane"] == saved["plane"] and rebuilt["valid_steps"] == saved["valid_steps"]
        registered_shares = [saved[f"{name}_share"] for name in ("contracting_reverse", "contracting_forward", "expanding_reverse", "expanding_forward")]
        quadrant_match &= all(close(a, b) for a, b in zip(rebuilt["shares"], registered_shares))
    check("quadrant_reconstruction", quadrant_match, reconstructed_quadrants)

    precomputed = {
        plane: [pair_indices(planes[plane], "circle", len(planes[plane]["time"]) // 2, len(planes[plane]["time"]), lag) for lag in LAGS]
        for plane in PLANES
    }
    rng = np.random.default_rng(SEED)
    rebuilt_nulls = []
    null_summaries = {name: [] for name in (*PLANES, "pooled")}
    for rep in range(SHUFFLES):
        rep_values = []
        for plane in PLANES:
            part = planes[plane]
            mid = len(part["time"]) // 2
            amplitude = permute_amplitudes(part["circle_strength"], valid(part, "circle"), mid, len(part["time"]), rng)
            values = np.concatenate([amplitude[right] / amplitude[left] for left, right in precomputed[plane]])
            item = summary(values)
            null_summaries[plane].append(item["scores"]["phi"])
            rebuilt_nulls.append((rep, plane, item["scores"]["phi"], item["mc"], item["me"]))
            rep_values.append(values)
        item = summary(np.concatenate(rep_values))
        null_summaries["pooled"].append(item["scores"]["phi"])
        rebuilt_nulls.append((rep, "pooled", item["scores"]["phi"], item["mc"], item["me"]))

    with NULLS.open("r", encoding="utf-8", newline="") as handle:
        saved_nulls = list(csv.DictReader(handle))
    null_match = len(saved_nulls) == len(rebuilt_nulls)
    if null_match:
        for saved, rebuilt in zip(saved_nulls, rebuilt_nulls):
            rep, plane, score, mc, me = rebuilt
            null_match &= int(saved["replicate"]) == rep and saved["plane"] == plane
            null_match &= close(float(saved["phi_score"]), score) and close(float(saved["median_contracting"]), mc) and close(float(saved["median_expanding"]), me)
    check("all_500_temporal_nulls", null_match, {"rows": len(saved_nulls)})

    null_summary_match = True
    observed_scores = {p: summary(pool_store[(p, "circle", "holdout")])["scores"]["phi"] for p in PLANES}
    observed_scores["pooled"] = holdout_sum["scores"]["phi"]
    rebuilt_null_summary = {}
    for name, scores in null_summaries.items():
        values = np.asarray(scores)
        observed = observed_scores[name]
        item = {
            "p05": float(np.percentile(values, 5)),
            "median": float(np.median(values)),
            "p95": float(np.percentile(values, 95)),
            "empirical_p": float((1 + np.sum(values <= observed)) / 501),
        }
        rebuilt_null_summary[name] = item
        saved = registered["temporal_null"][name]
        null_summary_match &= all(close(item[key], saved[key]) for key in item)
    check("temporal_null_summaries", null_summary_match, rebuilt_null_summary)

    expected_gates = {
        "g1_four_quadrants": all(min(row["shares"]) >= 0.05 for row in reconstructed_quadrants),
        "g2_phi_wins": phi_wins >= 15,
        "g3_absolute_endpoints": sum(
            abs(summary(pool_store[(p, "circle", "holdout")])["mc"] / (1 / PHI) - 1) <= 0.10
            and abs(summary(pool_store[(p, "circle", "holdout")])["me"] / PHI - 1) <= 0.10
            and abs(summary(pool_store[(p, "circle", "holdout")])["product"] - 1) <= 0.05
            for p in PLANES
        ) >= 2,
        "g4_temporal_order": sum(observed_scores[p] < np.percentile(null_summaries[p], 5) for p in PLANES) >= 2
        and rebuilt_null_summary["pooled"]["empirical_p"] < 0.05,
        "g5_beats_train_fitted": holdout_sum["scores"]["phi"] <= fit_score,
    }
    gate_match = all(bool(registered["gates"][key]) == value for key, value in expected_gates.items())
    check("gate_reconstruction", gate_match, expected_gates)

    with Image.open(FIGURE) as image:
        dimensions = image.size
        image_ok = dimensions == (2400, 1700)
    check("figure_integrity", image_ok, dimensions)

    passed = sum(bool(item["pass"]) for item in checks)
    output = {
        "test": "T333 independent validation",
        "date": "2026-08-03",
        "passed": passed,
        "total": len(checks),
        "all_pass": passed == len(checks),
        "checks": checks,
    }
    OUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": passed, "total": len(checks), "all_pass": output["all_pass"]}, indent=2))


if __name__ == "__main__":
    main()
