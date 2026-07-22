#!/usr/bin/env python3
"""PN36 validator: reconstruct the frozen conversion, then open prime labels."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from decimal import Decimal, ROUND_FLOOR, getcontext
from pathlib import Path

import numpy as np


TEST_ID = "PN36/PHI-TO-PENTAGON-CONVERSION/v1"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MANIFEST = HERE / "PN36_PROTOCOL_FREEZE_MANIFEST.json"
PRIMARY_RECEIPT = HERE / "PN36_PHI_TO_PENTAGON_CONVERSION_PRIMARY.json"
PREDICTIONS = HERE / "PN36_PHI_TO_PENTAGON_CONVERSION_PREDICTIONS.csv"
SCORED = HERE / "PN36_PHI_TO_PENTAGON_CONVERSION_SCORED.csv"
RESULTS = HERE / "PN36_PHI_TO_PENTAGON_CONVERSION_RESULTS.json"
VALIDATION = HERE / "PN36_PHI_TO_PENTAGON_CONVERSION_VALIDATION.json"

RESIDUES = (1, 7, 11, 13, 17, 19, 23, 29)
CELLS_PER_RUNG = 4096
BOOTSTRAPS = 1000
SHIFTS = 256
BOOT_SEED = 36361
MR_BASES_64 = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)

getcontext().prec = 60
D1 = Decimal(1)
D2 = Decimal(2)
D30 = Decimal(30)
PHI = (D1 + Decimal(5).sqrt()) / D2
ALPHA_PHI = D1 / (PHI * PHI)
CONVERTED_SECTORS = (3, 4, 5, 6, 7, 8)
RIVALS = (
    "raw_phi", "direct_pentagon", "direct_36deg",
    "converted_3", "converted_4", "converted_6", "converted_7", "converted_8",
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def verify_freeze_and_primary() -> tuple[dict, dict]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["test_id"] != TEST_ID:
        raise RuntimeError("Freeze manifest test ID mismatch")
    for rel, expected in manifest["sha256"].items():
        if sha256(ROOT / rel) != expected:
            raise RuntimeError(f"Frozen file changed: {rel}")
    receipt = json.loads(PRIMARY_RECEIPT.read_text(encoding="utf-8"))
    if receipt["test_id"] != TEST_ID or receipt["primality_opened"]:
        raise RuntimeError("Invalid primary receipt")
    if sha256(PREDICTIONS) != receipt["candidate_sha256"]:
        raise RuntimeError("Label-free candidate hash mismatch")
    return manifest, receipt


def mod1(value: Decimal) -> Decimal:
    return (value % D1 + D1) % D1


def quantize(theta: Decimal, sectors: int) -> Decimal:
    m = Decimal(sectors)
    vertex = int((m * theta + Decimal("0.5")).to_integral_value(rounding=ROUND_FLOOR)) % sectors
    return Decimal(vertex) / m


def circular_point_distance(a: Decimal, b: Decimal) -> Decimal:
    delta = abs(a - b)
    return min(delta, D1 - delta)


def antipodal_distance(x: Decimal, crossing: Decimal) -> float:
    return float(min(
        circular_point_distance(x, crossing),
        circular_point_distance(x, mod1(crossing + Decimal("0.5"))),
    ))


def model_distance(model: str, residue: int, t: Decimal, orientation: int) -> float:
    x = Decimal(residue) / D30
    theta_phi = mod1(Decimal(orientation) * ALPHA_PHI * t)
    if model == "raw_phi":
        crossing = theta_phi
    elif model == "direct_pentagon":
        crossing = mod1(Decimal(orientation) * Decimal(1) / Decimal(5) * t)
    elif model == "direct_36deg":
        crossing = mod1(Decimal(orientation) * Decimal(1) / Decimal(10) * t)
    elif model.startswith("converted_"):
        crossing = quantize(theta_phi, int(model.split("_")[1]))
    else:
        raise ValueError(model)
    return antipodal_distance(x, crossing)


def is_prime_64(n: int) -> bool:
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    for a in MR_BASES_64:
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


def auc_unweighted(scores: np.ndarray, labels: np.ndarray) -> float:
    positives = int(labels.sum())
    negatives = len(labels) - positives
    if positives == 0 or negatives == 0:
        return float("nan")
    order = np.argsort(scores, kind="mergesort")
    s = scores[order]
    y = labels[order]
    total = 0.0
    neg_below = 0.0
    i = 0
    while i < len(s):
        j = i + 1
        while j < len(s) and s[j] == s[i]:
            j += 1
        p = float(y[i:j].sum())
        n = float((j - i) - p)
        total += p * (neg_below + 0.5 * n)
        neg_below += n
        i = j
    return total / (positives * negatives)


def stratified_auc(scores: np.ndarray, labels: np.ndarray, residues: np.ndarray) -> float:
    numerator = 0.0
    denominator = 0.0
    for residue in RESIDUES:
        mask = residues == residue
        y = labels[mask]
        p = int(y.sum())
        n = len(y) - p
        if p and n:
            numerator += auc_unweighted(scores[mask], y) * p * n
            denominator += p * n
    return numerator / denominator


class WeightedAUC:
    def __init__(self, scores: np.ndarray, labels: np.ndarray, cell_ids: np.ndarray, residues: np.ndarray):
        self.parts = []
        for residue in RESIDUES:
            mask = residues == residue
            s = scores[mask]
            y = labels[mask]
            c = cell_ids[mask]
            order = np.argsort(s, kind="mergesort")
            s = s[order]
            y = y[order]
            c = c[order]
            starts = np.r_[0, np.flatnonzero(s[1:] != s[:-1]) + 1]
            self.parts.append((y, c, starts))

    def __call__(self, cell_weights: np.ndarray) -> float:
        numerator = 0.0
        denominator = 0.0
        for y, c, starts in self.parts:
            w = cell_weights[c]
            pos = w * y
            neg = w * (1 - y)
            gp = np.add.reduceat(pos, starts)
            gn = np.add.reduceat(neg, starts)
            ptotal = float(gp.sum())
            ntotal = float(gn.sum())
            if ptotal and ntotal:
                neg_below = np.cumsum(gn) - gn
                numerator += float(np.sum(gp * (neg_below + 0.5 * gn)))
                denominator += ptotal * ntotal
        return numerator / denominator


def ci(values: np.ndarray) -> list[float]:
    return [float(np.quantile(values, 0.025)), float(np.quantile(values, 0.975))]


def rank_average(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    sorted_values = values[order]
    ranks = np.empty(len(values), dtype=np.float64)
    i = 0
    while i < len(values):
        j = i + 1
        while j < len(values) and sorted_values[j] == sorted_values[i]:
            j += 1
        ranks[order[i:j]] = (i + j - 1) / 2.0
        i = j
    return ranks


def standardized_within_groups(values: np.ndarray, groups: np.ndarray) -> np.ndarray:
    out = np.zeros(len(values), dtype=np.float64)
    for group in np.unique(groups):
        mask = groups == group
        v = values[mask]
        sd = float(v.std())
        out[mask] = 0.0 if sd == 0 else (v - float(v.mean())) / sd
    return out


def trial_prime(n: int, primes: list[int]) -> bool:
    for p in primes:
        if p * p > n:
            return True
        if n % p == 0:
            return n == p
    return True


def sieve_primes(limit: int) -> list[int]:
    flags = bytearray(b"\x01") * (limit + 1)
    flags[0:2] = b"\x00\x00"
    for p in range(2, math.isqrt(limit) + 1):
        if flags[p]:
            start = p * p
            flags[start:limit + 1:p] = b"\x00" * (((limit - start) // p) + 1)
    return [i for i, flag in enumerate(flags) if flag]


def main() -> dict:
    _manifest, primary = verify_freeze_and_primary()
    raw = list(csv.DictReader(PREDICTIONS.open("r", encoding="utf-8", newline="")))
    if len(raw) != primary["rows"]:
        raise RuntimeError("Primary row count mismatch")

    nrows = len(raw)
    labels = np.empty(nrows, dtype=np.int8)
    residues = np.empty(nrows, dtype=np.int16)
    cell_ids = np.empty(nrows, dtype=np.int32)
    rung_k = np.empty(nrows, dtype=np.int16)
    pair_id = np.empty(nrows, dtype=np.int8)
    sample_half = np.empty(nrows, dtype=np.int8)
    model_names = ("converted_5",) + RIVALS
    model_scores = {name: np.empty(nrows, dtype=np.float64) for name in model_names}
    noflip_scores = np.empty(nrows, dtype=np.float64)

    scored_fields = list(raw[0].keys()) + ["is_prime"]
    for name in RIVALS:
        scored_fields += [f"{name}_distance", f"{name}_score"]

    with SCORED.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=scored_fields)
        writer.writeheader()
        for i, row in enumerate(raw):
            candidate = int(row["candidate"])
            residue = int(row["residue"])
            t = Decimal(row["t_from_singularity"])
            orientation = int(row["orientation"])
            label = int(is_prime_64(candidate))
            labels[i] = label
            residues[i] = residue
            cell_ids[i] = int(row["cell_index"])
            rung_k[i] = int(row["k"])
            pair_id[i] = int(row["pair_id"])
            sample_half[i] = 0 if row["sample_half"] == "first" else 1

            reconstructed = model_distance("converted_5", residue, t, orientation)
            sealed = float(row["converted_distance"])
            if abs(reconstructed - sealed) > 2e-23:
                raise RuntimeError(f"Converted reconstruction failed at row {i}")
            model_scores["converted_5"][i] = -sealed
            noflip_scores[i] = -float(row["noflip_converted_distance"])
            out = dict(row)
            out["is_prime"] = label
            for name in RIVALS:
                distance = model_distance(name, residue, t, orientation)
                model_scores[name][i] = -distance
                out[f"{name}_distance"] = f"{distance:.24f}"
                out[f"{name}_score"] = f"{-distance:.24f}"
            writer.writerow(out)

    aucs = {name: stratified_auc(score, labels, residues) for name, score in model_scores.items()}
    aucs["converted_5_no_flip"] = stratified_auc(noflip_scores, labels, residues)
    best_rival = max(RIVALS, key=lambda name: aucs[name])
    primary_auc = aucs["converted_5"]
    noflip_auc = aucs["converted_5_no_flip"]
    top2 = np.array([int(row["converted_top2"]) for row in raw], dtype=np.int8)
    total_primes = int(labels.sum())
    top2_capture = float(labels[top2 == 1].sum() / total_primes)

    by_rung = {}
    for k in sorted(set(rung_k.tolist())):
        mask = rung_k == k
        by_rung[str(k)] = {
            "rows": int(mask.sum()),
            "primes": int(labels[mask].sum()),
            "prime_rate": float(labels[mask].mean()),
            "converted_5_auc": stratified_auc(model_scores["converted_5"][mask], labels[mask], residues[mask]),
            "no_flip_auc": stratified_auc(noflip_scores[mask], labels[mask], residues[mask]),
            "top2_capture": float(labels[mask & (top2 == 1)].sum() / labels[mask].sum()),
        }
    by_pair = {}
    for pair in sorted(set(pair_id.tolist())):
        mask = pair_id == pair
        by_pair[str(pair)] = {
            "converted_5_auc": stratified_auc(model_scores["converted_5"][mask], labels[mask], residues[mask]),
            "no_flip_auc": stratified_auc(noflip_scores[mask], labels[mask], residues[mask]),
            "top2_capture": float(labels[mask & (top2 == 1)].sum() / labels[mask].sum()),
        }
    by_half = {}
    for half, name in ((0, "first"), (1, "second")):
        mask = sample_half == half
        by_half[name] = stratified_auc(model_scores["converted_5"][mask], labels[mask], residues[mask])
    by_lane = {}
    for residue in RESIDUES:
        mask = residues == residue
        by_lane[str(residue)] = {
            "rows": int(mask.sum()), "primes": int(labels[mask].sum()),
            "prime_rate": float(labels[mask].mean()),
            "converted_5_auc": auc_unweighted(model_scores["converted_5"][mask], labels[mask]),
        }

    weighted = {
        "primary": WeightedAUC(model_scores["converted_5"], labels, cell_ids, residues),
        "best_rival": WeightedAUC(model_scores[best_rival], labels, cell_ids, residues),
        "noflip": WeightedAUC(noflip_scores, labels, cell_ids, residues),
    }
    rng = np.random.default_rng(BOOT_SEED)
    boot_primary = np.empty(BOOTSTRAPS)
    boot_best = np.empty(BOOTSTRAPS)
    boot_noflip = np.empty(BOOTSTRAPS)
    boot_capture = np.empty(BOOTSTRAPS)
    rung_cell_ids = [np.arange(j * CELLS_PER_RUNG, (j + 1) * CELLS_PER_RUNG) for j in range(6)]
    prime_by_cell = np.bincount(cell_ids, weights=labels, minlength=primary["cells"])
    top2_prime_by_cell = np.bincount(cell_ids, weights=labels * top2, minlength=primary["cells"])
    for b in range(BOOTSTRAPS):
        weights = np.zeros(primary["cells"], dtype=np.int32)
        for ids in rung_cell_ids:
            chosen = rng.choice(ids, size=CELLS_PER_RUNG, replace=True)
            weights += np.bincount(chosen, minlength=primary["cells"]).astype(np.int32)
        boot_primary[b] = weighted["primary"](weights)
        boot_best[b] = weighted["best_rival"](weights)
        boot_noflip[b] = weighted["noflip"](weights)
        boot_capture[b] = float(np.dot(weights, top2_prime_by_cell) / np.dot(weights, prime_by_cell))

    score_cube = model_scores["converted_5"].reshape(primary["cells"], 8)
    top2_cube = top2.reshape(primary["cells"], 8)
    label_cube = labels.reshape(primary["cells"], 8)
    residue_cube = residues.reshape(primary["cells"], 8)
    shift_aucs = []
    shift_captures = []
    for j in range(1, SHIFTS + 1):
        shift = (149 * j) % CELLS_PER_RUNG
        shifted_scores = np.empty_like(score_cube)
        shifted_top2 = np.empty_like(top2_cube)
        for rung in range(6):
            sl = slice(rung * CELLS_PER_RUNG, (rung + 1) * CELLS_PER_RUNG)
            shifted_scores[sl] = np.roll(score_cube[sl], shift, axis=0)
            shifted_top2[sl] = np.roll(top2_cube[sl], shift, axis=0)
        shift_aucs.append(stratified_auc(shifted_scores.ravel(), label_cube.ravel(), residue_cube.ravel()))
        shift_captures.append(float(label_cube[shifted_top2 == 1].sum() / total_primes))
    shift_aucs_arr = np.array(shift_aucs)
    shift_captures_arr = np.array(shift_captures)
    shift_auc_p = float((1 + np.sum(shift_aucs_arr >= primary_auc)) / (SHIFTS + 1))
    shift_capture_p = float((1 + np.sum(shift_captures_arr >= top2_capture)) / (SHIFTS + 1))

    distance = -model_scores["converted_5"]
    edges = np.quantile(distance, np.linspace(0, 1, 9))
    distance_octiles = []
    for q in range(8):
        mask = (distance >= edges[q]) & (distance <= edges[q + 1] if q == 7 else distance < edges[q + 1])
        distance_octiles.append({
            "octile": q + 1, "distance_low": float(edges[q]), "distance_high": float(edges[q + 1]),
            "rows": int(mask.sum()), "primes": int(labels[mask].sum()),
            "prime_rate": None if not mask.any() else float(labels[mask].mean()),
        })

    # Descriptive only: does prime count change near the Phi carrier's fivefold handover boundaries?
    boundary_closeness = np.array([-float(raw[i * 8]["sector_boundary_distance"]) for i in range(primary["cells"])])
    cell_rung = rung_k.reshape(primary["cells"], 8)[:, 0]
    boundary_rank = rank_average(boundary_closeness)
    prime_count_rank = rank_average(prime_by_cell)
    z_boundary = standardized_within_groups(boundary_rank, cell_rung)
    z_count = standardized_within_groups(prime_count_rank, cell_rung)
    boundary_corr = float(np.corrcoef(z_boundary, z_count)[0, 1])
    boundary_by_rung = {}
    for k in sorted(set(cell_rung.tolist())):
        mask = cell_rung == k
        boundary_by_rung[str(k)] = float(np.corrcoef(
            rank_average(boundary_closeness[mask]), rank_average(prime_by_cell[mask])
        )[0, 1])

    spot_rng = random.Random(36531)
    spot_indices = []
    for k in sorted(set(rung_k.tolist())):
        pool = np.flatnonzero(rung_k == k).tolist()
        spot_indices.extend(spot_rng.sample(pool, 3))
    max_spot = max(int(raw[i]["candidate"]) for i in spot_indices)
    trial_primes = sieve_primes(math.isqrt(max_spot) + 1)
    spots = []
    for i in spot_indices:
        n = int(raw[i]["candidate"])
        trial = trial_prime(n, trial_primes)
        spots.append({"row": i, "candidate": n, "miller_rabin": bool(labels[i]), "trial_division": trial})
        if trial != bool(labels[i]):
            raise RuntimeError(f"Independent primality disagreement for {n}")

    synthetic_signal = top2.copy()
    synthetic_signal_auc = stratified_auc(model_scores["converted_5"], synthetic_signal, residues)
    synthetic_rng = np.random.default_rng(36713)
    synthetic_null = synthetic_rng.binomial(1, 0.25, size=nrows).astype(np.int8)
    synthetic_null_auc = stratified_auc(model_scores["converted_5"], synthetic_null, residues)

    primary_ci = ci(boot_primary)
    primary_minus_best_ci = ci(boot_primary - boot_best)
    primary_minus_noflip_ci = ci(boot_primary - boot_noflip)
    capture_ci = ci(boot_capture)
    g1 = primary_auc > 0.5 and primary_ci[0] > 0.5 and shift_auc_p <= 0.01
    g2 = (
        all(v["converted_5_auc"] > 0.5 for v in by_pair.values())
        and sum(v["converted_5_auc"] > 0.5 for v in by_rung.values()) >= 5
        and all(v > 0.5 for v in by_half.values())
    )
    g3 = primary_auc > max(aucs[name] for name in RIVALS) and primary_minus_best_ci[0] > 0
    g4 = (
        primary_auc > noflip_auc and primary_minus_noflip_ci[0] > 0
        and sum(v["converted_5_auc"] > v["no_flip_auc"] for v in by_pair.values()) >= 2
    )
    g5 = (
        top2_capture > 0.25 and capture_ci[0] > 0.25 and shift_capture_p <= 0.01
        and all(v["top2_capture"] > 0.25 for v in by_pair.values())
    )
    gates = {
        "G1_converted_preference": g1, "G2_scale_transfer": g2,
        "G3_conversion_specificity": g3, "G4_singularity_flip": g4,
        "G5_crossing_capture": g5,
    }
    verdict = "SUPPORTED" if all(gates.values()) else ("SUGGESTIVE" if g1 and g2 else "NOT SUPPORTED")

    result = {
        "test_id": TEST_ID,
        "verdict": verdict,
        "rows": nrows,
        "cells": primary["cells"],
        "primes": total_primes,
        "prime_rate": float(labels.mean()),
        "converted_5_auc": primary_auc,
        "converted_5_auc_ci95": primary_ci,
        "best_rival": best_rival,
        "best_rival_auc": aucs[best_rival],
        "converted_5_minus_best_rival_ci95": primary_minus_best_ci,
        "converted_5_no_flip_auc": noflip_auc,
        "converted_5_minus_no_flip_ci95": primary_minus_noflip_ci,
        "top2_capture": top2_capture,
        "top2_capture_ci95": capture_ci,
        "shift_auc_p": shift_auc_p,
        "shift_capture_p": shift_capture_p,
        "all_model_aucs": aucs,
        "by_rung": by_rung,
        "by_pair": by_pair,
        "by_half": by_half,
        "by_lane": by_lane,
        "distance_octiles": distance_octiles,
        "descriptive_boundary_association": {
            "pooled_within_rung_spearman_like": boundary_corr,
            "by_rung_spearman": boundary_by_rung,
            "registered_support_gate": False,
        },
        "gates": gates,
        "synthetic_checks": {
            "planted_top2_auc": synthetic_signal_auc,
            "independent_null_auc": synthetic_null_auc,
        },
        "shift_null": {
            "auc_mean": float(shift_aucs_arr.mean()), "auc_min": float(shift_aucs_arr.min()),
            "auc_max": float(shift_aucs_arr.max()), "capture_mean": float(shift_captures_arr.mean()),
            "capture_min": float(shift_captures_arr.min()), "capture_max": float(shift_captures_arr.max()),
        },
    }
    RESULTS.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    validation = {
        "test_id": TEST_ID,
        "status": "PASS",
        "freeze_manifest_sha256": sha256(MANIFEST),
        "primary_receipt_sha256": sha256(PRIMARY_RECEIPT),
        "prediction_sha256": sha256(PREDICTIONS),
        "scored_sha256": sha256(SCORED),
        "results_sha256": sha256(RESULTS),
        "reconstructed_rows": nrows,
        "independent_trial_division_spots": spots,
        "synthetic_checks": result["synthetic_checks"],
    }
    VALIDATION.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))

