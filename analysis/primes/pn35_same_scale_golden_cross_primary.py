#!/usr/bin/env python3
"""PN35 primary builder: seal same-scale ARA/Phi scores before primality is opened."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from decimal import Decimal, getcontext
from pathlib import Path


TEST_ID = "PN35/SAME-SCALE-GOLDEN-CROSS/v1"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MANIFEST = HERE / "PN35_PROTOCOL_FREEZE_MANIFEST.json"
OUTPUT = HERE / "PN35_SAME_SCALE_GOLDEN_CROSS_PREDICTIONS.csv"
RECEIPT = HERE / "PN35_SAME_SCALE_GOLDEN_CROSS_PRIMARY.json"

RESIDUES = (1, 7, 11, 13, 17, 19, 23, 29)
PAIR_SPECS = (
    (1, 26, 27, 35001),
    (2, 36, 37, 35002),
    (3, 46, 47, 35003),
)
CELLS_PER_RUNG = 4096

getcontext().prec = 60
D0 = Decimal(0)
D1 = Decimal(1)
D2 = Decimal(2)
D30 = Decimal(30)
PHI = (D1 + Decimal(5).sqrt()) / D2
ALPHA_GOLDEN = D1 / (PHI * PHI)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def verify_freeze() -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["test_id"] != TEST_ID:
        raise RuntimeError("Freeze manifest test ID mismatch")
    for rel, expected in manifest["sha256"].items():
        path = ROOT / rel
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(f"Frozen file changed: {rel}: {actual} != {expected}")
    return manifest


def complete_cell_starts(k: int, seed: int) -> list[int]:
    lower = 1 << k
    upper = 1 << (k + 1)
    first = ((lower + 29) // 30) * 30
    last = ((upper - 30) // 30) * 30
    count = ((last - first) // 30) + 1
    if count < CELLS_PER_RUNG:
        raise RuntimeError(f"Rung {k} has only {count} complete cells")
    indices = random.Random(seed + k).sample(range(count), CELLS_PER_RUNG)
    return sorted(first + 30 * i for i in indices)


def mod2(value: Decimal) -> Decimal:
    return (value % D2 + D2) % D2


def crossing(alpha: Decimal, t: Decimal, orientation: int) -> Decimal:
    return mod2(D2 * Decimal(orientation) * alpha * t)


def circular_distance(x: Decimal, crossing_1: Decimal) -> Decimal:
    crossing_2 = mod2(crossing_1 + D1)
    best = D2
    for h in (crossing_1, crossing_2):
        delta = abs(x - h)
        best = min(best, delta, D2 - delta)
    return best


def decimal_string(value: Decimal) -> str:
    return format(value, ".24f")


def build() -> dict:
    manifest = verify_freeze()
    fields = [
        "test_id", "pair_id", "k", "rung_side", "lower", "upper", "seed",
        "sample_order", "sample_half", "cell_index", "cell_start", "residue", "candidate",
        "structural_x", "t_from_singularity", "orientation", "golden_cross_1", "golden_cross_2",
        "golden_distance", "golden_score", "golden_rank_in_cell", "golden_top2", "noflip_distance",
    ]
    row_count = 0
    cell_count = 0
    rung_counts: dict[str, int] = {}
    with OUTPUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        global_cell = 0
        for pair_id, lower_k, upper_k, seed in PAIR_SPECS:
            for side, k in (("lower", lower_k), ("upper", upper_k)):
                lower = 1 << k
                upper = 1 << (k + 1)
                orientation = -1 if k % 2 else 1
                starts = complete_cell_starts(k, seed)
                rung_counts[str(k)] = len(starts)
                for order, cell_start in enumerate(starts):
                    t = Decimal(cell_start - lower) / D30
                    g = crossing(ALPHA_GOLDEN, t, orientation)
                    g_noflip = crossing(ALPHA_GOLDEN, t, 1)
                    cell_rows = []
                    for residue in RESIDUES:
                        x = Decimal(residue) / Decimal(15)
                        distance = circular_distance(x, g)
                        noflip_distance = circular_distance(x, g_noflip)
                        cell_rows.append((residue, x, distance, noflip_distance))
                    ranks = {
                        residue: rank + 1
                        for rank, (residue, _x, _d, _nf) in enumerate(
                            sorted(cell_rows, key=lambda item: (item[2], item[0]))
                        )
                    }
                    for residue, x, distance, noflip_distance in cell_rows:
                        rank = ranks[residue]
                        writer.writerow({
                            "test_id": TEST_ID,
                            "pair_id": pair_id,
                            "k": k,
                            "rung_side": side,
                            "lower": lower,
                            "upper": upper,
                            "seed": seed,
                            "sample_order": order,
                            "sample_half": "first" if order < CELLS_PER_RUNG // 2 else "second",
                            "cell_index": global_cell,
                            "cell_start": cell_start,
                            "residue": residue,
                            "candidate": cell_start + residue,
                            "structural_x": decimal_string(x),
                            "t_from_singularity": decimal_string(t),
                            "orientation": orientation,
                            "golden_cross_1": decimal_string(g),
                            "golden_cross_2": decimal_string(mod2(g + D1)),
                            "golden_distance": decimal_string(distance),
                            "golden_score": decimal_string(-distance),
                            "golden_rank_in_cell": rank,
                            "golden_top2": int(rank <= 2),
                            "noflip_distance": decimal_string(noflip_distance),
                        })
                        row_count += 1
                    global_cell += 1
                    cell_count += 1

    receipt = {
        "test_id": TEST_ID,
        "stage": "PRIMARY_LABEL_FREE",
        "primality_opened": False,
        "manifest_sha256": sha256(MANIFEST),
        "freeze_files_verified": manifest["sha256"],
        "rows": row_count,
        "cells": cell_count,
        "rungs": rung_counts,
        "golden_alpha": decimal_string(ALPHA_GOLDEN),
        "candidate_file": OUTPUT.name,
        "candidate_sha256": sha256(OUTPUT),
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    result = build()
    print(json.dumps(result, indent=2))
