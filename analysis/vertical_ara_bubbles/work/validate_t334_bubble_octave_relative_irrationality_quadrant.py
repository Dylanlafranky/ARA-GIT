from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

from run_vertical_ara_dyadic_chain import Root, extract_roots
from run_vertical_ara_spiral_scale import complex_parent_vectors, eligible_vectors


BASE = Path(__file__).resolve().parents[1]
SOURCE = BASE / "source_data"
RESULTS_DIR = BASE / "results"
STEM = "T334_BUBBLE_OCTAVE_RELATIVE_IRRATIONALITY_QUADRANT"
PROTOCOL = BASE / f"{STEM}_PROTOCOL_v1_FROZEN.md"
RESULTS = BASE / f"{STEM}_RESULTS.json"
EVENTS = RESULTS_DIR / f"{STEM}_EVENTS.csv"
CELLS = RESULTS_DIR / f"{STEM}_CELLS.csv"
QUADRANTS = RESULTS_DIR / f"{STEM}_QUADRANTS.csv"
NULLS = RESULTS_DIR / f"{STEM}_NULLS.csv"
FIGURE = BASE / f"{STEM}_FIGURE.png"
OUT = BASE / f"{STEM}_VALIDATION.json"

PROTOCOL_HASH = "E827F7907FBE7B12699EA035453A60A3AC7DF5F4BA7A350B5686051D87C0023C"
DATA_ZIP_HASH = "11F050285C740CCA7B4248E64F24304317E0563E61D39DC5A9F2A7F39BA86BC0"
SOURCE_MANIFEST_HASH = "D712AA9BB5935C400AE76DA50B93DB97F5FEFD1E1E8814E5DC8322BD66076C7F"
PRIMARY_CARRIER = 2.0
SHUFFLES = 500
BOOTSTRAPS = 5000
SEED = 20260803
EPS = 1e-12
LEVELS = (0, 1, 2, 3)
SPLITS = ("calibration", "evaluation", "holdout")

PHI = (1 + math.sqrt(5)) / 2
FIXED = {
    "plastic": 1.324717957244746,
    "sqrt2": math.sqrt(2.0),
    "three_halves": 1.5,
    "phi": PHI,
    "t333_qutrit": 1.809114052291864,
    "two": 2.0,
    "e": math.e,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def manifest_hash() -> str:
    lines = [f"{path.name}:{sha256(path)}" for path in sorted(SOURCE.glob("*.csv"))]
    return hashlib.sha256("\n".join(lines).encode()).hexdigest().upper()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def close(a: float, b: float, tolerance: float = 2e-10) -> bool:
    return abs(a - b) <= tolerance * max(1.0, abs(a), abs(b))


def root_key(root: Root) -> str:
    return f"{root.video}:{root.track_id}:{root.start_frame}"


def wrap(value: float) -> float:
    return (value + math.pi) % (2 * math.pi) - math.pi


def make_event(root: Root, vectors: list[complex], level: int) -> dict:
    q = vectors[level + 1] / vectors[level]
    return {
        "split": root.split,
        "video": root.video,
        "root_key": root_key(root),
        "level": level,
        "raw_scale": abs(q),
        "delta_rad": wrap(math.atan2(q.imag, q.real)),
    }


def endpoints(rows: list[dict], carrier: float, alpha: float | None = None) -> dict:
    values = np.asarray([float(row["raw_scale"]) / carrier for row in rows], dtype=float)
    lower = values[values < 1 - EPS]
    upper = values[values > 1 + EPS]
    if not len(lower) or not len(upper):
        return {"u_minus": math.nan, "u_plus": math.nan, "product": math.nan, "implied_alpha": math.nan, "score": math.nan}
    lm = float(np.median(np.log(lower)))
    lp = float(np.median(np.log(upper)))
    record = {
        "u_minus": float(np.median(lower)),
        "u_plus": float(np.median(upper)),
        "product": float(np.median(lower) * np.median(upper)),
        "implied_alpha": math.exp((lp - lm) / 2),
        "midpoint_log": (lm + lp) / 2,
        "lower_count": int(len(lower)),
        "upper_count": int(len(upper)),
        "count": int(len(values)),
    }
    record["score"] = math.nan if alpha is None else 0.5 * (abs(lm + math.log(alpha)) + abs(lp - math.log(alpha)))
    return record


def score(record: dict, alpha: float) -> float:
    lm, lp = math.log(record["u_minus"]), math.log(record["u_plus"])
    return 0.5 * (abs(lm + math.log(alpha)) + abs(lp - math.log(alpha)))


def qlabel(row: dict, carrier: float) -> str:
    h = math.log(float(row["raw_scale"]) / carrier)
    delta = float(row["delta_rad"])
    if abs(h) <= EPS or abs(delta) <= EPS:
        return "boundary"
    return ("expanding" if h > 0 else "contracting") + "_" + ("forward" if delta > 0 else "reverse")


def shuffled_steps(steps, key, draw):
    digest = hashlib.sha256(f"{SEED}:{draw}:{key}".encode()).digest()
    rng = random.Random(int.from_bytes(digest[:8], "big"))
    indices = list(range(len(steps)))
    rng.shuffle(indices)
    return [steps[index] for index in indices]


def broken_events(retained):
    groups = defaultdict(list)
    for item in retained:
        groups[item[0].video].append(item)
    output = []
    for video, group in groups.items():
        group.sort(key=lambda item: (item[0].start_frame, item[0].track_id, item[0].segment_index))
        if len(group) < 2:
            continue
        for index, (root, vectors) in enumerate(group):
            partner = group[(index + 1) % len(group)][1]
            for level in LEVELS:
                q = partner[level + 1] / vectors[level]
                output.append({"split": root.split, "video": video, "root_key": root_key(root), "level": level, "raw_scale": abs(q), "delta_rad": wrap(math.atan2(q.imag, q.real))})
    return output


def bootstrap_comparison(observed, broken, split, alpha, offset):
    obs = defaultdict(list)
    bro = defaultdict(list)
    for row in observed:
        if row["split"] == split:
            obs[row["video"]].append(row)
    for row in broken:
        if row["split"] == split:
            bro[row["video"]].append(row)
    videos = sorted(set(obs) & set(bro))
    point_obs = endpoints([r for v in videos for r in obs[v]], 2, alpha)["score"]
    point_bro = endpoints([r for v in videos for r in bro[v]], 2, alpha)["score"]
    rng = np.random.default_rng(SEED + offset)
    values = []
    for _ in range(BOOTSTRAPS):
        chosen = rng.integers(0, len(videos), size=len(videos))
        left, right = [], []
        for position in chosen:
            video = videos[int(position)]
            left.extend(obs[video])
            right.extend(bro[video])
        values.append(endpoints(left, 2, alpha)["score"] - endpoints(right, 2, alpha)["score"])
    return point_obs, point_bro, float(np.quantile(values, 0.025)), float(np.quantile(values, 0.975))


def bootstrap_product(observed, split, offset):
    groups = defaultdict(list)
    for row in observed:
        if row["split"] == split:
            groups[row["video"]].append(row)
    videos = sorted(groups)
    rng = np.random.default_rng(SEED + offset)
    values = []
    for _ in range(BOOTSTRAPS):
        sampled = []
        for position in rng.integers(0, len(videos), size=len(videos)):
            sampled.extend(groups[videos[int(position)]])
        values.append(endpoints(sampled, 2)["product"])
    point = endpoints([row for v in videos for row in groups[v]], 2)["product"]
    return point, float(np.quantile(values, 0.025)), float(np.quantile(values, 0.975))


def main() -> None:
    saved = json.loads(RESULTS.read_text(encoding="utf-8"))
    saved_events = read_csv(EVENTS)
    saved_cells = read_csv(CELLS)
    saved_quadrants = read_csv(QUADRANTS)
    saved_nulls = read_csv(NULLS)
    checks = []

    def check(name: str, passed: bool, detail) -> None:
        checks.append({"name": name, "pass": bool(passed), "detail": detail})

    check("protocol_sha256", sha256(PROTOCOL) == PROTOCOL_HASH, sha256(PROTOCOL))
    check("data_zip_sha256", sha256(BASE / "data.zip") == DATA_ZIP_HASH, sha256(BASE / "data.zip"))
    check("source_manifest_sha256", manifest_hash() == SOURCE_MANIFEST_HASH, manifest_hash())

    roots, diagnostics = extract_roots(SOURCE)
    retained = []
    reconstructed = []
    for root in roots:
        vectors = complex_parent_vectors(root.steps)
        if eligible_vectors(vectors):
            retained.append((root, vectors))
            reconstructed.extend(make_event(root, vectors, level) for level in LEVELS)
    counts = {split: sum(root.split == split for root, _ in retained) for split in SPLITS}
    check("root_counts", counts == {"calibration": 125, "evaluation": 172, "holdout": 40}, counts)
    check("event_count", len(reconstructed) == len(saved_events) == 1348, [len(reconstructed), len(saved_events)])

    saved_lookup = {(row["root_key"], int(row["level"])): row for row in saved_events}
    max_scale_error = 0.0
    max_delta_error = 0.0
    for row in reconstructed:
        target = saved_lookup[(row["root_key"], row["level"])]
        max_scale_error = max(max_scale_error, abs(row["raw_scale"] - float(target["raw_scale"])))
        max_delta_error = max(max_delta_error, abs(wrap(row["delta_rad"] - float(target["delta_rad"]))))
    check("raw_event_reconstruction", max_scale_error < 1e-12 and max_delta_error < 1e-12, {"scale": max_scale_error, "delta": max_delta_error})

    calibration = [row for row in reconstructed if row["split"] == "calibration"]
    carrier_cal = math.exp(statistics.median(math.log(row["raw_scale"]) for row in calibration))
    alpha_cal = endpoints(calibration, 2)["implied_alpha"]
    check("calibration_carrier", close(carrier_cal, saved["calibration_sensitivity_carrier"]), carrier_cal)
    check("calibration_alpha", close(alpha_cal, saved["calibration_fitted_reciprocal_alpha"]), alpha_cal)

    pooled_ok = True
    pooled_detail = {}
    for split in SPLITS:
        record = endpoints([row for row in reconstructed if row["split"] == split], 2)
        target = saved["primary_pooled"][split]
        pooled_detail[split] = record
        for field in ("u_minus", "u_plus", "product", "implied_alpha", "midpoint_log"):
            pooled_ok = pooled_ok and close(record[field], target[field])
    check("pooled_endpoints", pooled_ok, pooled_detail)

    cells_ok = True
    max_cell_error = 0.0
    for saved_row in saved_cells:
        carrier = float(saved_row["carrier"])
        split = saved_row["split"]
        level = saved_row["level"]
        subset = [row for row in reconstructed if row["split"] == split and (level == "pooled" or row["level"] == int(level))]
        record = endpoints(subset, carrier)
        for field in ("u_minus", "u_plus", "product", "implied_alpha", "midpoint_log"):
            error = abs(record[field] - float(saved_row[field]))
            max_cell_error = max(max_cell_error, error)
            cells_ok = cells_ok and error < 2e-10
        candidates = dict(FIXED)
        candidates["fitted_calibration"] = alpha_cal
        winner = min(candidates, key=lambda name: score(record, candidates[name]))
        cells_ok = cells_ok and winner == saved_row["winner"]
    check("cell_recalculation", cells_ok, max_cell_error)

    quadrant_ok = True
    quadrant_detail = {}
    for split in SPLITS:
        subset = [row for row in reconstructed if row["split"] == split]
        labels = [qlabel(row, 2) for row in subset]
        nonboundary = sum(label != "boundary" for label in labels)
        quadrant_detail[split] = {}
        for name in ("contracting_reverse", "contracting_forward", "expanding_reverse", "expanding_forward"):
            share = labels.count(name) / nonboundary
            target = next(row for row in saved_quadrants if row["carrier_name"] == "primary_two" and row["split"] == split and row["quadrant"] == name)
            quadrant_ok = quadrant_ok and close(share, float(target["share_nonboundary"]))
            quadrant_detail[split][name] = share
    check("quadrant_recalculation", quadrant_ok, quadrant_detail)

    # Recompute every temporal null independently.
    null_lookup = {(int(row["draw"]), row["split"]): row for row in saved_nulls}
    null_ok = len(saved_nulls) == 1000
    max_null_error = 0.0
    as_close = {"evaluation": 0, "holdout": 0}
    observed_score = {
        split: endpoints([row for row in reconstructed if row["split"] == split], 2, alpha_cal)["score"]
        for split in ("evaluation", "holdout")
    }
    for draw in range(SHUFFLES):
        by_split = defaultdict(list)
        for root, _ in retained:
            if root.split not in ("evaluation", "holdout"):
                continue
            vectors = complex_parent_vectors(shuffled_steps(root.steps, root_key(root), draw))
            if not eligible_vectors(vectors):
                continue
            by_split[root.split].extend(make_event(root, vectors, level) for level in LEVELS)
        for split in ("evaluation", "holdout"):
            value = endpoints(by_split[split], 2, alpha_cal)["score"]
            saved_value = float(null_lookup[(draw, split)]["score"])
            max_null_error = max(max_null_error, abs(value - saved_value))
            null_ok = null_ok and close(value, saved_value)
            as_close[split] += value <= observed_score[split]
    check("all_500_temporal_nulls", null_ok, {"max_error": max_null_error, "as_close": as_close})
    p_values = {split: (1 + as_close[split]) / 501 for split in as_close}
    check("temporal_p_values", all(close(p_values[s], saved["temporal_null"][s]["empirical_p"]) for s in p_values), p_values)

    broken = broken_events(retained)
    identity_ok = True
    identity_detail = {}
    for index, split in enumerate(("evaluation", "holdout")):
        obs, bro, lo, hi = bootstrap_comparison(reconstructed, broken, split, alpha_cal, 100 + index)
        target = saved["identity_control"][split]
        identity_ok = identity_ok and all(close(value, target[field]) for value, field in ((obs, "observed_score"), (bro, "broken_score"), (lo, "ci_low"), (hi, "ci_high")))
        identity_detail[split] = {"observed": obs, "broken": bro, "ci_low": lo, "ci_high": hi}
    check("identity_control_bootstrap", identity_ok, identity_detail)

    product_ok = True
    product_detail = {}
    for index, split in enumerate(("evaluation", "holdout")):
        point, lo, hi = bootstrap_product(reconstructed, split, 200 + index)
        target = saved["reciprocal_product_bootstrap"][split]
        product_ok = product_ok and all(close(value, target[field]) for value, field in ((point, "product"), (lo, "ci_low"), (hi, "ci_high")))
        product_detail[split] = {"product": point, "ci_low": lo, "ci_high": hi}
    check("product_bootstrap", product_ok, product_detail)

    # Recompute gates without trusting saved booleans.
    g1 = all(value >= 0.05 for split in ("evaluation", "holdout") for value in quadrant_detail[split].values())
    g2 = True
    for split in ("evaluation", "holdout"):
        pooled = endpoints([r for r in reconstructed if r["split"] == split], 2)["product"]
        level_products = [endpoints([r for r in reconstructed if r["split"] == split and r["level"] == level], 2)["product"] for level in LEVELS]
        g2 = g2 and 0.9 <= pooled <= 1.1 and sum(0.85 <= value <= 1.15 for value in level_products) >= 3
    g3 = True
    for split in ("evaluation", "holdout"):
        record = endpoints([r for r in reconstructed if r["split"] == split], 2)
        fit_score = score(record, alpha_cal)
        g3 = g3 and all(fit_score < score(record, value) for value in FIXED.values())
        g3 = g3 and abs(math.log(record["implied_alpha"] / alpha_cal)) <= math.log(1.10)
    g4 = all(p_values[split] <= 0.05 for split in p_values)
    g5 = identity_detail["evaluation"]["ci_high"] < 0 and identity_detail["holdout"]["observed"] - identity_detail["holdout"]["broken"] < 0
    recomputed_gates = {"G1_four_quadrants": g1, "G2_reciprocal_closure": g2, "G3_calibration_transfer": g3, "G4_recorded_order": g4, "G5_intact_identity": g5}
    check("gate_recalculation", all(saved["gates"][name] == value for name, value in recomputed_gates.items()), recomputed_gates)

    with Image.open(FIGURE) as figure:
        figure_ok = figure.size == (2400, 1700)
        figure_detail = {"size": list(figure.size), "mode": figure.mode}
    check("figure_integrity", figure_ok, figure_detail)

    payload = {
        "test": "T334 independent validation",
        "date": "2026-08-03",
        "passed": sum(item["pass"] for item in checks),
        "total": len(checks),
        "all_pass": all(item["pass"] for item in checks),
        "checks": checks,
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("passed", "total", "all_pass")}, indent=2))


if __name__ == "__main__":
    main()
