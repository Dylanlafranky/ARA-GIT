#!/usr/bin/env python3
"""PN36 label-free primary: convert a Phi carrier into a frozen fivefold state."""

from __future__ import annotations

import csv
import hashlib
import json
import random
from decimal import Decimal, ROUND_FLOOR, getcontext
from pathlib import Path


TEST_ID = "PN36/PHI-TO-PENTAGON-CONVERSION/v1"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MANIFEST = HERE / "PN36_PROTOCOL_FREEZE_MANIFEST.json"
OUTPUT = HERE / "PN36_PHI_TO_PENTAGON_CONVERSION_PREDICTIONS.csv"
RECEIPT = HERE / "PN36_PHI_TO_PENTAGON_CONVERSION_PRIMARY.json"

RESIDUES = (1, 7, 11, 13, 17, 19, 23, 29)
PAIR_SPECS = (
    (1, 28, 29, 36001),
    (2, 38, 39, 36002),
    (3, 48, 49, 36003),
)
CELLS_PER_RUNG = 4096

getcontext().prec = 60
D0 = Decimal(0)
D1 = Decimal(1)
D2 = Decimal(2)
D5 = Decimal(5)
D30 = Decimal(30)
PHI = (D1 + Decimal(5).sqrt()) / D2
ALPHA_PHI = D1 / (PHI * PHI)


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
        actual = sha256(ROOT / rel)
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


def mod1(value: Decimal) -> Decimal:
    return (value % D1 + D1) % D1


def phi_phase(t: Decimal, orientation: int) -> Decimal:
    return mod1(Decimal(orientation) * ALPHA_PHI * t)


def quantize(theta: Decimal, sectors: int) -> Decimal:
    m = Decimal(sectors)
    vertex = int((m * theta + Decimal("0.5")).to_integral_value(rounding=ROUND_FLOOR)) % sectors
    return Decimal(vertex) / m


def circular_point_distance(a: Decimal, b: Decimal) -> Decimal:
    delta = abs(a - b)
    return min(delta, D1 - delta)


def antipodal_distance(x: Decimal, crossing: Decimal) -> Decimal:
    return min(circular_point_distance(x, crossing), circular_point_distance(x, mod1(crossing + Decimal("0.5"))))


def boundary_distance(theta: Decimal, sectors: int) -> Decimal:
    m = Decimal(sectors)
    return min(
        circular_point_distance(theta, (Decimal(j) + Decimal("0.5")) / m)
        for j in range(sectors)
    )


def decimal_string(value: Decimal) -> str:
    return format(value, ".24f")


def build() -> dict:
    manifest = verify_freeze()
    fields = [
        "test_id", "pair_id", "k", "rung_side", "lower", "upper", "seed",
        "sample_order", "sample_half", "cell_index", "cell_start", "residue", "candidate",
        "structural_x", "t_from_singularity", "orientation", "phi_phase", "converted_vertex",
        "converted_antiphase", "conversion_residual", "sector_boundary_distance",
        "converted_distance", "converted_score", "converted_rank_in_cell", "converted_top2",
        "noflip_converted_distance",
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
                    theta = phi_phase(t, orientation)
                    theta_noflip = phi_phase(t, 1)
                    converted = quantize(theta, 5)
                    converted_noflip = quantize(theta_noflip, 5)
                    cell_rows = []
                    for residue in RESIDUES:
                        x = Decimal(residue) / D30
                        distance = antipodal_distance(x, converted)
                        noflip_distance = antipodal_distance(x, converted_noflip)
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
                            "phi_phase": decimal_string(theta),
                            "converted_vertex": decimal_string(converted),
                            "converted_antiphase": decimal_string(mod1(converted + Decimal("0.5"))),
                            "conversion_residual": decimal_string(circular_point_distance(theta, converted)),
                            "sector_boundary_distance": decimal_string(boundary_distance(theta, 5)),
                            "converted_distance": decimal_string(distance),
                            "converted_score": decimal_string(-distance),
                            "converted_rank_in_cell": rank,
                            "converted_top2": int(rank <= 2),
                            "noflip_converted_distance": decimal_string(noflip_distance),
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
        "phi_alpha": decimal_string(ALPHA_PHI),
        "conversion": "nearest fivefold vertex",
        "candidate_file": OUTPUT.name,
        "candidate_sha256": sha256(OUTPUT),
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))

