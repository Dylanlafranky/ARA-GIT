"""Independent arithmetic validator for PN7A phase-referenced occurrence.

This file intentionally does not import the analysis implementation.  It uses
scalar loops and a hand-written interpolator to check the vectorised result.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
AGG = HERE / "PN7A_PHASE_REFERENCED_OCCURRENCE_AGGREGATES.npz"
RESULTS = HERE / "PN7A_PHASE_REFERENCED_OCCURRENCE_RESULTS.json"
CURVES = HERE / "PN7A_PHASE_REFERENCED_OCCURRENCE_CURVES.csv"
OUT = HERE / "PN7A_PHASE_REFERENCED_OCCURRENCE_VALIDATION.json"
RUNGS = (7, 8, 9, 10, 11)
ENTITIES = ("candidate", "edge")


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest().upper()


def pearson(x, y):
    pairs = [(float(a), float(b)) for a, b in zip(x, y) if math.isfinite(float(a)) and math.isfinite(float(b))]
    mx = sum(a for a, _ in pairs) / len(pairs)
    my = sum(b for _, b in pairs) / len(pairs)
    num = sum((a - mx) * (b - my) for a, b in pairs)
    dx = sum((a - mx) ** 2 for a, _ in pairs)
    dy = sum((b - my) ** 2 for _, b in pairs)
    return num / math.sqrt(dx * dy)


def interpolate(xs, ys, grid):
    out = []
    j = 0
    for g in grid:
        while j + 1 < len(xs) and xs[j + 1] < g:
            j += 1
        if g <= xs[0]:
            out.append(float(ys[0]))
        elif g >= xs[-1]:
            out.append(float(ys[-1]))
        else:
            x0, x1 = float(xs[j]), float(xs[j + 1])
            w = (float(g) - x0) / (x1 - x0)
            out.append(float(ys[j]) * (1.0 - w) + float(ys[j + 1]) * w)
    return out


def close(a, b, tol=2e-11):
    return abs(float(a) - float(b)) <= tol * max(1.0, abs(float(a)), abs(float(b)))


def main():
    z = np.load(AGG)
    official = json.loads(RESULTS.read_text(encoding="utf-8"))
    checks = []

    def check(name, passed, detail=""):
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    check("aggregate hash matches result", file_hash(AGG) == official["input"]["sha256"])
    rebuilt = {e: {} for e in ENTITIES}
    for entity in ENTITIES:
        for rung in RUNGS:
            exposure = z[f"r{rung}__{entity}_exposure"].astype(np.int64)
            matrix = z[f"r{rung}__{entity}_stage_position"].astype(np.int64)
            check(f"{entity} r{rung} matrix shape", matrix.shape == (25, 64))
            check(f"{entity} r{rung} exposure shape", exposure.shape == (64,))
            check(
                f"{entity} r{rung} complete partition",
                int(matrix.sum()) == int(exposure.sum()),
                f"matrix={int(matrix.sum())}, exposure={int(exposure.sum())}",
            )
            check(f"{entity} r{rung} nonnegative", bool((matrix >= 0).all() and (exposure >= 0).all()))

            alive_bins = [int(v) for v in exposure]
            total_initial = sum(alive_bins)
            theta_after, theta_event, root = [], [], []
            depth_coeffs = {0: [], 1: [], 2: []}
            previous_theta = 0.0
            for stage in range(24):
                death_bins = [int(v) for v in matrix[stage]]
                total_deaths = sum(death_bins)
                next_total = sum(alive_bins) - total_deaths
                current_theta = math.acos(max(-1.0, min(1.0, 2.0 * next_total / total_initial - 1.0)))
                theta_after.append(current_theta)
                theta_event.append((previous_theta + current_theta) / 2.0)
                previous_theta = current_theta
                for depth in (0, 1, 2):
                    width = 64 // (2**depth)
                    row = []
                    for node in range(2**depth):
                        lo = node * width
                        mid = lo + width // 2
                        hi = lo + width
                        dl, dr = sum(death_bins[lo:mid]), sum(death_bins[mid:hi])
                        nl, nr = sum(alive_bins[lo:mid]), sum(alive_bins[mid:hi])
                        hl = dl / nl if nl else 0.0
                        hr = dr / nr if nr else 0.0
                        row.append((hr - hl) / (hr + hl) if hr + hl else 0.0)
                    depth_coeffs[depth].append(row)
                root.append(depth_coeffs[0][-1][0])
                alive_bins = [n - d for n, d in zip(alive_bins, death_bins)]

            check(f"{entity} r{rung} terminal bins reconcile", alive_bins == [int(v) for v in matrix[24]])
            check(f"{entity} r{rung} theta monotone", all(b >= a for a, b in zip(theta_after, theta_after[1:])))
            check(f"{entity} r{rung} root bounded", all(-1.0 <= v <= 1.0 for v in root))

            term = [int(v) for v in matrix[24]]
            hl = sum(term[:32]) / sum(int(v) for v in exposure[:32])
            hr = sum(term[32:]) / sum(int(v) for v in exposure[32:])
            terminal_lean = (hr - hl) / (hr + hl)
            depth_energy = {
                d: sum(v * v for row in depth_coeffs[d] for v in row) / sum(len(row) for row in depth_coeffs[d])
                for d in (0, 1, 2)
            }
            rebuilt[entity][rung] = {
                "theta_after": theta_after,
                "theta_event": theta_event,
                "root": root,
                "terminal_lean": terminal_lean,
                "depth_energy": depth_energy,
            }
            check(
                f"{entity} r{rung} terminal lean agrees",
                close(terminal_lean, official["terminal_lean"][entity][f"r{rung}"]),
            )
            for depth in (0, 1, 2):
                check(
                    f"{entity} r{rung} depth {depth} energy agrees",
                    close(depth_energy[depth], official["depth_energy"][entity][f"r{rung}"][f"depth_{depth}"]),
                )

    low = max(min(rebuilt[e][r]["theta_event"]) for e in ENTITIES for r in (9, 10, 11))
    high = min(max(rebuilt[e][r]["theta_event"]) for e in ENTITIES for r in (9, 10, 11))
    grid = [low + i * (high - low) / 23.0 for i in range(24)]
    check("phase grid lower agrees", close(low, official["phase_grid"]["theta_low"]))
    check("phase grid upper agrees", close(high, official["phase_grid"]["theta_high"]))

    for entity in ENTITIES:
        for rung in (9, 10, 11):
            rebuilt[entity][rung]["aligned"] = interpolate(
                rebuilt[entity][rung]["theta_event"], rebuilt[entity][rung]["root"], grid
            )
        for a, b in ((9, 10), (10, 11), (9, 11)):
            raw = pearson(rebuilt[entity][a]["root"], rebuilt[entity][b]["root"])
            aligned = pearson(rebuilt[entity][a]["aligned"], rebuilt[entity][b]["aligned"])
            check(
                f"{entity} raw recurrence r{a}/r{b}",
                close(raw, official["lateral_recurrence"][entity]["raw"][f"r{a}_r{b}"]),
            )
            check(
                f"{entity} aligned recurrence r{a}/r{b}",
                close(aligned, official["lateral_recurrence"][entity]["phase_aligned"][f"r{a}_r{b}"]),
            )

    for rung in (9, 10, 11):
        value = pearson(rebuilt["candidate"][rung]["aligned"], rebuilt["edge"][rung]["aligned"])
        check(
            f"candidate/edge agreement r{rung}",
            close(value, official["candidate_edge_phase_agreement"][f"r{rung}"]),
        )

    for entity in ENTITIES:
        vertical = {}
        for rung in (10, 11):
            delta = [
                a - b
                for a, b in zip(rebuilt[entity][rung]["theta_after"], rebuilt[entity][rung - 1]["theta_after"])
            ]
            vertical[rung] = interpolate(rebuilt[entity][rung]["theta_after"], delta, grid)
            value = pearson(rebuilt[entity][rung]["aligned"], vertical[rung])
            check(
                f"vertical/lateral {entity} r{rung}",
                close(value, official["vertical_lateral_correlation"][f"{entity}_r{rung}"]),
            )
        value = pearson(vertical[10], vertical[11])
        check(f"vertical recurrence {entity}", close(value, official["vertical_recurrence"][entity]))

    with CURVES.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    check("curve CSV row count", len(rows) == 1 + len(ENTITIES) * len(RUNGS) * 24, f"rows={len(rows)}")
    check("curve CSV header width", len(rows[0]) == 11, f"columns={len(rows[0])}")

    passed = sum(1 for c in checks if c["passed"])
    report = {
        "validator": "independent scalar-loop reconstruction; no import from analysis implementation",
        "checks_passed": passed,
        "checks_total": len(checks),
        "all_passed": passed == len(checks),
        "checks": checks,
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("checks_passed", "checks_total", "all_passed")}, indent=2))
    if not report["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
