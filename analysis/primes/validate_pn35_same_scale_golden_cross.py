#!/usr/bin/env python3
"""PN35 independent validator: reconstruct the seal, then open prime labels and score gates."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from collections import defaultdict
from decimal import Decimal, getcontext
from pathlib import Path

import numpy as np


TEST_ID = "PN35/SAME-SCALE-GOLDEN-CROSS/v1"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MANIFEST = HERE / "PN35_PROTOCOL_FREEZE_MANIFEST.json"
PRIMARY_RECEIPT = HERE / "PN35_SAME_SCALE_GOLDEN_CROSS_PRIMARY.json"
PREDICTIONS = HERE / "PN35_SAME_SCALE_GOLDEN_CROSS_PREDICTIONS.csv"
SCORED = HERE / "PN35_SAME_SCALE_GOLDEN_CROSS_SCORED.csv"
RESULTS = HERE / "PN35_SAME_SCALE_GOLDEN_CROSS_RESULTS.json"
VALIDATION = HERE / "PN35_SAME_SCALE_GOLDEN_CROSS_VALIDATION.json"

RESIDUES = (1, 7, 11, 13, 17, 19, 23, 29)
CELLS_PER_RUNG = 4096
BOOTSTRAPS = 1000
SHIFTS = 256
BOOT_SEED = 35351

getcontext().prec = 60
D1 = Decimal(1)
D2 = Decimal(2)
PHI = (D1 + Decimal(5).sqrt()) / D2
ALPHAS = {
    "golden": D1 / (PHI * PHI),
    "exponential": D1 / D1.exp(),
    "rational_3_8": Decimal(3) / Decimal(8),
    "rational_2_5": Decimal(2) / Decimal(5),
    "shear_36deg": D1 / Decimal(10),
    "pentagon": D1 / Decimal(5),
    "hexagon": D1 / Decimal(6),
    "quadrant": D1 / Decimal(4),
    "triangle": D1 / Decimal(3),
    "anti_phase": D1 / Decimal(2),
    "silver_conjugate": Decimal(2).sqrt() - D1,
}
RIVALS = tuple(name for name in ALPHAS if name != "golden")
MR_BASES_64 = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def verify_freeze_and_primary() -> tuple[dict, dict]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for rel, expected in manifest["sha256"].items():
        actual = sha256(ROOT / rel)
        if actual != expected:
            raise RuntimeError(f"Frozen file changed: {rel}")
    receipt = json.loads(PRIMARY_RECEIPT.read_text(encoding="utf-8"))
    if receipt["test_id"] != TEST_ID or receipt["primality_opened"]:
        raise RuntimeError("Invalid primary receipt")
    if sha256(PREDICTIONS) != receipt["candidate_sha256"]:
        raise RuntimeError("Label-free candidate hash mismatch")
    return manifest, receipt


def mod2(value: Decimal) -> Decimal:
    return (value % D2 + D2) % D2


def distance_for(residue: int, t: Decimal, orientation: int, alpha: Decimal) -> float:
    g = mod2(D2 * Decimal(orientation) * alpha * t)
    x = Decimal(residue) / Decimal(15)
    best = D2
    for h in (g, mod2(g + D1)):
        delta = abs(x - h)
        best = min(best, delta, D2 - delta)
    return float(best)


def is_prime_64(n: int) -> bool:
    if n < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in small:
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
            a = auc_unweighted(scores[mask], y)
            numerator += a * p * n
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
                u = float(np.sum(gp * (neg_below + 0.5 * gn)))
                numerator += u
                denominator += ptotal * ntotal
        return numerator / denominator


def ci(values: np.ndarray) -> list[float]:
    return [float(np.quantile(values, 0.025)), float(np.quantile(values, 0.975))]


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
    manifest, primary = verify_freeze_and_primary()
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
    model_scores = {name: np.empty(nrows, dtype=np.float64) for name in ALPHAS}
    noflip_scores = np.empty(nrows, dtype=np.float64)

    scored_fields = list(raw[0].keys()) + ["is_prime"]
    for name in ALPHAS:
        if name != "golden":
            scored_fields += [f"{name}_distance", f"{name}_score"]

    with SCORED.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=scored_fields)
        writer.writeheader()
        for i, row in enumerate(raw):
            candidate = int(row["candidate"])
            label = int(is_prime_64(candidate))
            residue = int(row["residue"])
            t = Decimal(row["t_from_singularity"])
            orientation = int(row["orientation"])
            labels[i] = label
            residues[i] = residue
            cell_ids[i] = int(row["cell_index"])
            rung_k[i] = int(row["k"])
            pair_id[i] = int(row["pair_id"])
            sample_half[i] = 0 if row["sample_half"] == "first" else 1

            reconstructed = distance_for(residue, t, orientation, ALPHAS["golden"])
            sealed = float(row["golden_distance"])
            if abs(reconstructed - sealed) > 2e-23:
                raise RuntimeError(f"Golden reconstruction failed at row {i}")
            model_scores["golden"][i] = -sealed
            noflip_scores[i] = -float(row["noflip_distance"])
            out = dict(row)
            out["is_prime"] = label
            for name, alpha in ALPHAS.items():
                if name == "golden":
                    continue
                d = distance_for(residue, t, orientation, alpha)
                model_scores[name][i] = -d
                out[f"{name}_distance"] = f"{d:.24f}"
                out[f"{name}_score"] = f"{-d:.24f}"
            writer.writerow(out)

    aucs = {name: stratified_auc(score, labels, residues) for name, score in model_scores.items()}
    aucs["golden_no_flip"] = stratified_auc(noflip_scores, labels, residues)
    best_rival = max(RIVALS, key=lambda name: aucs[name])
    pooled_auc = aucs["golden"]
    noflip_auc = aucs["golden_no_flip"]

    by_rung = {}
    for k in sorted(set(rung_k.tolist())):
        mask = rung_k == k
        by_rung[str(k)] = {
            "rows": int(mask.sum()),
            "primes": int(labels[mask].sum()),
            "prime_rate": float(labels[mask].mean()),
            "golden_auc": stratified_auc(model_scores["golden"][mask], labels[mask], residues[mask]),
            "noflip_auc": stratified_auc(noflip_scores[mask], labels[mask], residues[mask]),
            "top2_capture": float(labels[mask & (np.array([int(r["golden_top2"]) for r in raw], dtype=bool))].sum() / labels[mask].sum()),
        }
    by_pair = {}
    for p in sorted(set(pair_id.tolist())):
        mask = pair_id == p
        by_pair[str(p)] = {
            "golden_auc": stratified_auc(model_scores["golden"][mask], labels[mask], residues[mask]),
            "noflip_auc": stratified_auc(noflip_scores[mask], labels[mask], residues[mask]),
        }
    by_half = {}
    for h, name in ((0, "first"), (1, "second")):
        mask = sample_half == h
        by_half[name] = stratified_auc(model_scores["golden"][mask], labels[mask], residues[mask])

    top2 = np.array([int(row["golden_top2"]) for row in raw], dtype=np.int8)
    total_primes = int(labels.sum())
    top2_capture = float(labels[top2 == 1].sum() / total_primes)
    for p in by_pair:
        mask = pair_id == int(p)
        by_pair[p]["top2_capture"] = float(labels[mask & (top2 == 1)].sum() / labels[mask].sum())

    full_weights = np.ones(primary["cells"], dtype=np.int32)
    weighted = {
        "golden": WeightedAUC(model_scores["golden"], labels, cell_ids, residues),
        "best_rival": WeightedAUC(model_scores[best_rival], labels, cell_ids, residues),
        "noflip": WeightedAUC(noflip_scores, labels, cell_ids, residues),
    }
    rng = np.random.default_rng(BOOT_SEED)
    boot_golden = np.empty(BOOTSTRAPS)
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
        boot_golden[b] = weighted["golden"](weights)
        boot_best[b] = weighted["best_rival"](weights)
        boot_noflip[b] = weighted["noflip"](weights)
        boot_capture[b] = float(np.dot(weights, top2_prime_by_cell) / np.dot(weights, prime_by_cell))

    # Fixed circular shifts: move every eight-lane crossing profile together within each rung.
    score_cube = model_scores["golden"].reshape(primary["cells"], 8)
    top2_cube = top2.reshape(primary["cells"], 8)
    label_cube = labels.reshape(primary["cells"], 8)
    residue_cube = residues.reshape(primary["cells"], 8)
    shift_aucs = []
    shift_captures = []
    for j in range(1, SHIFTS + 1):
        shift = (149 * j) % CELLS_PER_RUNG
        shifted_scores = np.empty_like(score_cube)
        shifted_top2 = np.empty_like(top2_cube)
        for r in range(6):
            sl = slice(r * CELLS_PER_RUNG, (r + 1) * CELLS_PER_RUNG)
            shifted_scores[sl] = np.roll(score_cube[sl], shift, axis=0)
            shifted_top2[sl] = np.roll(top2_cube[sl], shift, axis=0)
        shift_aucs.append(stratified_auc(shifted_scores.ravel(), label_cube.ravel(), residue_cube.ravel()))
        shift_captures.append(float(label_cube[shifted_top2 == 1].sum() / total_primes))
    shift_aucs_arr = np.array(shift_aucs)
    shift_captures_arr = np.array(shift_captures)
    shift_auc_p = float((1 + np.sum(shift_aucs_arr >= pooled_auc)) / (SHIFTS + 1))
    shift_capture_p = float((1 + np.sum(shift_captures_arr >= top2_capture)) / (SHIFTS + 1))

    # Distance octiles are declared on the sealed pooled distance, not fitted cut points.
    distance = -model_scores["golden"]
    edges = np.quantile(distance, np.linspace(0, 1, 9))
    octiles = []
    for q in range(8):
        mask = (distance >= edges[q]) & (distance <= edges[q + 1] if q == 7 else distance < edges[q + 1])
        octiles.append({
            "octile": q + 1,
            "distance_low": float(edges[q]),
            "distance_high": float(edges[q + 1]),
            "rows": int(mask.sum()),
            "primes": int(labels[mask].sum()),
            "prime_rate": float(labels[mask].mean()),
        })

    # Independent trial-division spots, including both labels and every scale.
    spot_rng = random.Random(35531)
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

    # Minimal synthetic instrument checks: registered score must detect a planted top-two signal and not create one
    # when labels are generated independently of the crossing.
    synthetic_signal = top2.copy()
    synthetic_signal_auc = stratified_auc(model_scores["golden"], synthetic_signal, residues)
    synthetic_rng = np.random.default_rng(35713)
    synthetic_null = synthetic_rng.binomial(1, 0.25, size=nrows).astype(np.int8)
    synthetic_null_auc = stratified_auc(model_scores["golden"], synthetic_null, residues)

    g1 = pooled_auc > 0.5 and ci(boot_golden)[0] > 0.5 and shift_auc_p <= 0.01
    g2 = (
        all(v["golden_auc"] > 0.5 for v in by_pair.values())
        and sum(v["golden_auc"] > 0.5 for v in by_rung.values()) >= 5
        and all(v > 0.5 for v in by_half.values())
    )
    golden_best_diff = boot_golden - boot_best
    flip_diff = boot_golden - boot_noflip
    g3 = aucs["golden"] > max(aucs[r] for r in RIVALS) and ci(golden_best_diff)[0] > 0
    g4 = (
        pooled_auc > noflip_auc
        and ci(flip_diff)[0] > 0
        and sum(v["golden_auc"] > v["noflip_auc"] for v in by_pair.values()) >= 2
    )
    g5 = (
        top2_capture > 0.25
        and ci(boot_capture)[0] > 0.25
        and shift_capture_p <= 0.01
        and all(v["top2_capture"] > 0.25 for v in by_pair.values())
    )
    gates = {"G1_pooled_preference": g1, "G2_scale_stability": g2, "G3_phi_specificity": g3,
             "G4_singularity_flip": g4, "G5_crossing_capture": g5}
    verdict = "SUPPORTED" if all(gates.values()) else ("SUGGESTIVE" if g1 and g2 else "NOT SUPPORTED")

    result = {
        "test_id": TEST_ID,
        "verdict": verdict,
        "rows": nrows,
        "cells": primary["cells"],
        "primes": total_primes,
        "prime_rate": float(labels.mean()),
        "golden_auc": pooled_auc,
        "golden_auc_ci95": ci(boot_golden),
        "best_rival": best_rival,
        "best_rival_auc": aucs[best_rival],
        "golden_minus_best_rival_ci95": ci(golden_best_diff),
        "golden_no_flip_auc": noflip_auc,
        "golden_minus_no_flip_ci95": ci(flip_diff),
        "top2_capture": top2_capture,
        "top2_capture_ci95": ci(boot_capture),
        "shift_auc_p": shift_auc_p,
        "shift_capture_p": shift_capture_p,
        "all_model_aucs": aucs,
        "by_rung": by_rung,
        "by_pair": by_pair,
        "by_half": by_half,
        "distance_octiles": octiles,
        "gates": gates,
        "synthetic_checks": {"planted_top2_auc": synthetic_signal_auc, "independent_null_auc": synthetic_null_auc},
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
