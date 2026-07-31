"""T307 embedded octave-closure crosswalk.

Retrospective, source-locked comparison of:
  1. the exact embedded 1/e <-> phi geometric closure identity; and
  2. the continuous Q40C 7.5/15 cadence modes.

The script deliberately preserves the distinction between an algebraic
identity, a population-level cadence ratio, and seed-specific pairing.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
Q40C = ROOT / "analysis" / "quantum" / "Q40C_POST_RESULT_DOUBLE_HELIX_RESULTS.json"
T306 = ROOT / "analysis" / "muon" / "T306_EMBEDDED_E_PHI_THREAD_RESULTS.json"
PROTOCOL = HERE / "T307_EMBEDDED_OCTAVE_CLOSURE_CROSSWALK_PROTOCOL_v1_FROZEN.md"

EXPECTED_Q40C_SHA256 = "5BFDEA834CD3E9F40ECD0FEF75DEE8A848D00902C62F342FA1DB96F21128B242"
EXPECTED_T306_SHA256 = "F1D524DD32B7A6B1DFF5537FE0313164A318B0710BBFDCEE0A74FDFB1A483484"

OUT_JSON = HERE / "T307_EMBEDDED_OCTAVE_CLOSURE_CROSSWALK_RESULTS.json"
OUT_CSV = HERE / "T307_EMBEDDED_OCTAVE_CLOSURE_SEED_RATIOS.csv"
OUT_PNG = HERE / "T307_EMBEDDED_OCTAVE_CLOSURE_CROSSWALK.png"

RNG_SEED = 20260730
N_RESAMPLES = 10_000
FACTOR_CANDIDATES = {
    "1": 1.0,
    "3/2": 1.5,
    "phi": (1.0 + math.sqrt(5.0)) / 2.0,
    "2": 2.0,
    "e": math.e,
    "3": 3.0,
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def percentile_dict(values: np.ndarray) -> dict[str, float]:
    qs = np.quantile(values, [0.025, 0.25, 0.5, 0.75, 0.975])
    return {
        "q025": float(qs[0]),
        "q25": float(qs[1]),
        "median": float(qs[2]),
        "q75": float(qs[3]),
        "q975": float(qs[4]),
    }


def bootstrap_median(values: np.ndarray, rng: np.random.Generator) -> tuple[np.ndarray, list[float]]:
    n = len(values)
    boot = np.empty(N_RESAMPLES, dtype=float)
    for index in range(N_RESAMPLES):
        sample = values[rng.integers(0, n, size=n)]
        boot[index] = np.median(sample)
    interval = np.quantile(boot, [0.025, 0.975])
    return boot, [float(interval[0]), float(interval[1])]


def draw_report(
    geometry: dict,
    ratios: np.ndarray,
    candidate_errors: dict[str, float],
    shuffled_errors: np.ndarray,
    paired_error: float,
    gates: dict[str, bool],
) -> None:
    width, height = 1700, 1120
    bg = "#0c1118"
    panel = "#151d28"
    grid = "#354151"
    text = "#edf3f8"
    muted = "#9babbc"
    blue = "#73a7ff"
    gold = "#efb64e"
    green = "#68d3a3"
    red = "#ee7c83"

    image = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(image)
    f_title = font(42, True)
    f_sub = font(22)
    f_head = font(27, True)
    f_body = font(20)
    f_small = font(17)

    draw.text((55, 40), "T307 — embedded octave-closure crosswalk", fill=text, font=f_title)
    draw.text(
        (57, 96),
        "Exact constant geometry beside continuous Q40C child/parent cadence",
        fill=muted,
        font=f_sub,
    )

    boxes = [(45, 145, 825, 510), (850, 145, 1655, 510), (45, 535, 825, 1065), (850, 535, 1655, 1065)]
    for box in boxes:
        draw.rounded_rectangle(box, radius=18, fill=panel, outline=grid, width=2)

    # Panel 1: geometry.
    draw.text((75, 172), "Exact 1/e ↔ Phi geometry", fill=text, font=f_head)
    draw.text((75, 220), "Parent interval", fill=muted, font=f_small)
    x0, x1, y = 105, 755, 280
    draw.line((x0, y, x1, y), fill=grid, width=8)
    lo = geometry["lower_1_over_e"]
    hi = geometry["upper_phi"]
    anti = geometry["anti_phi"]
    def gx(value: float) -> float:
        return x0 + (value / 2.0) * (x1 - x0)
    for value, label, color in [(lo, "1/e", blue), (1.0, "ridge 1", text), (hi, "Phi", gold)]:
        xx = gx(value)
        draw.line((xx, y - 20, xx, y + 20), fill=color, width=4)
        draw.text((xx - 25, y + 30), label, fill=color, font=f_small)
    draw.line((gx(lo), y + 100, gx(anti), y + 100), fill=green, width=10)
    draw.ellipse((gx(lo) - 7, y + 93, gx(lo) + 7, y + 107), fill=green)
    draw.ellipse((gx(anti) - 7, y + 93, gx(anti) + 7, y + 107), fill=green)
    draw.text((75, y + 76), "embedded child diameter", fill=muted, font=f_small)
    draw.text(
        (75, 442),
        f"child radius = parent ridge displacement = {geometry['child_radius']:.9f}",
        fill=green,
        font=f_body,
    )
    draw.text((75, 474), "This equality is algebraically forced.", fill=muted, font=f_small)
    draw.text(
        (410, 474),
        f"Raw child/parent width = {geometry['raw_child_to_parent_width_ratio']:.4%}, not 1:2.",
        fill=muted,
        font=f_small,
    )

    # Panel 2: cadence ratio.
    draw.text((880, 172), "Q40C continuous cadence closure", fill=text, font=f_head)
    med = float(np.median(ratios))
    q025, q975 = np.quantile(ratios, [0.025, 0.975])
    draw.text((880, 218), f"94 seed pairs · median 2Tc/Tp = {med:.9f}", fill=green, font=f_body)
    draw.text((880, 251), f"seed 95% range: {q025:.9f} — {q975:.9f}", fill=muted, font=f_small)
    hx0, hx1, hy0, hy1 = 905, 1605, 320, 465
    draw.rectangle((hx0, hy0, hx1, hy1), outline=grid, width=2)
    lo_r, hi_r = 0.9996, 1.0004
    bins = np.linspace(lo_r, hi_r, 35)
    hist, _ = np.histogram(ratios, bins=bins)
    max_h = max(1, int(hist.max()))
    for i, count in enumerate(hist):
        bx0 = hx0 + (bins[i] - lo_r) / (hi_r - lo_r) * (hx1 - hx0)
        bx1 = hx0 + (bins[i + 1] - lo_r) / (hi_r - lo_r) * (hx1 - hx0)
        by = hy1 - count / max_h * (hy1 - hy0 - 10)
        draw.rectangle((bx0 + 1, by, bx1 - 1, hy1), fill=blue)
    ridge_x = hx0 + (1.0 - lo_r) / (hi_r - lo_r) * (hx1 - hx0)
    draw.line((ridge_x, hy0, ridge_x, hy1), fill=gold, width=4)
    draw.text((ridge_x - 34, hy0 - 27), "1.0", fill=gold, font=f_small)

    # Panel 3: candidates.
    draw.text((75, 565), "Candidate multiplier control", fill=text, font=f_head)
    labels = list(candidate_errors)
    vals = np.array([candidate_errors[label] for label in labels])
    max_v = float(vals.max())
    by0, bar_h, gap = 630, 48, 20
    for i, (label, value) in enumerate(zip(labels, vals)):
        yy = by0 + i * (bar_h + gap)
        draw.text((85, yy + 11), label, fill=text, font=f_body)
        length = 600 * float(value / max_v)
        color = green if label == "2" else blue
        draw.rounded_rectangle((155, yy, 155 + length, yy + bar_h), radius=8, fill=color)
        draw.text((170 + length, yy + 11), f"{value:.6f}", fill=muted, font=f_small)
    draw.text((75, 1010), "Lower median |log(Tp / kTc)| is better.", fill=muted, font=f_small)

    # Panel 4: pairing control and verdict.
    draw.text((880, 565), "Seed-specific pairing control", fill=text, font=f_head)
    p_pair = float(np.mean(shuffled_errors <= paired_error))
    draw.text((880, 618), f"paired mean |2Tc/Tp − 1|: {paired_error:.9f}", fill=text, font=f_body)
    draw.text(
        (880, 653),
        f"shuffle median: {np.median(shuffled_errors):.9f} · p = {p_pair:.3f}",
        fill=muted,
        font=f_body,
    )
    sx0, sx1, sy0, sy1 = 905, 1605, 725, 875
    sh_lo, sh_hi = np.quantile(shuffled_errors, [0.005, 0.995])
    bins2 = np.linspace(sh_lo, sh_hi, 36)
    hist2, _ = np.histogram(shuffled_errors, bins=bins2)
    max_h2 = max(1, int(hist2.max()))
    for i, count in enumerate(hist2):
        bx0 = sx0 + (bins2[i] - sh_lo) / (sh_hi - sh_lo) * (sx1 - sx0)
        bx1 = sx0 + (bins2[i + 1] - sh_lo) / (sh_hi - sh_lo) * (sx1 - sx0)
        by = sy1 - count / max_h2 * (sy1 - sy0 - 8)
        draw.rectangle((bx0 + 1, by, bx1 - 1, sy1), fill="#647386")
    paired_x = sx0 + (paired_error - sh_lo) / (sh_hi - sh_lo) * (sx1 - sx0)
    draw.line((paired_x, sy0, paired_x, sy1), fill=gold, width=4)
    draw.text((max(sx0, paired_x - 70), sy0 - 27), "paired", fill=gold, font=f_small)

    verdict = "Q40C FACTOR-TWO CADENCE: SUPPORTED" if gates["G1_cadence_closure"] and gates["G2_factor_specificity"] else "Q40C FACTOR-TWO CADENCE: NOT SUPPORTED"
    pair_text = "SPECIFIC PAIRING: SUPPORTED" if gates["G3_seed_specific_pairing"] else "SPECIFIC PAIRING: NOT SUPPORTED"
    draw.text((880, 925), verdict, fill=green if "SUPPORTED" in verdict else red, font=f_head)
    draw.text((880, 968), pair_text, fill=green if gates["G3_seed_specific_pairing"] else red, font=f_head)
    draw.text((880, 1015), "Retrospective simulator crosswalk; not new Phi evidence.", fill=muted, font=f_small)

    image.save(OUT_PNG, optimize=True)


def main() -> None:
    q40c_hash = sha256(Q40C)
    t306_hash = sha256(T306)
    if q40c_hash != EXPECTED_Q40C_SHA256:
        raise RuntimeError(f"Q40C hash mismatch: {q40c_hash}")
    if t306_hash != EXPECTED_T306_SHA256:
        raise RuntimeError(f"T306 hash mismatch: {t306_hash}")

    with Q40C.open("r", encoding="utf-8") as handle:
        q40c = json.load(handle)
    with T306.open("r", encoding="utf-8") as handle:
        t306 = json.load(handle)

    phi = (1.0 + math.sqrt(5.0)) / 2.0
    lower = math.exp(-1.0)
    anti_phi = 2.0 - phi
    parent_midpoint = (lower + phi) / 2.0
    parent_displacement = 1.0 - parent_midpoint
    child_radius = (anti_phi - lower) / 2.0
    geometry_ratio = child_radius / parent_displacement
    parent_diameter = phi - lower
    child_diameter = 2.0 * child_radius
    raw_width_ratio = child_diameter / parent_diameter

    # Check the values already saved in T306 without using them as inputs.
    saved_geometry = t306["geometry"]
    t306_checks = {
        "parent_midpoint_abs_difference": abs(
            parent_midpoint - saved_geometry["embedded_centre_parent_coordinate"]
        ),
        "child_diameter_abs_difference": abs(
            2.0 * child_radius - saved_geometry["child_carrier_separation"]
        ),
        "closure_deficit_abs_difference": abs(
            2.0 * parent_displacement - saved_geometry["closure_deficit"]
        ),
    }

    by_seed: dict[int, dict[str, list[float]]] = defaultdict(
        lambda: {"child": [], "parent": []}
    )
    for row in q40c["population_rows"]:
        period = float(row["angular_period_samples"])
        seed = int(row["seed"])
        if row["posthoc_two_turn_7_5_family"]:
            by_seed[seed]["child"].append(period)
        if row["posthoc_one_turn_15_family"]:
            by_seed[seed]["parent"].append(period)

    seed_rows = []
    for seed in sorted(by_seed):
        child = by_seed[seed]["child"]
        parent = by_seed[seed]["parent"]
        if not child or not parent:
            continue
        tc = float(np.median(child))
        tp = float(np.median(parent))
        q = 2.0 * tc / tp
        seed_rows.append(
            {
                "seed": seed,
                "child_lineages": len(child),
                "parent_lineages": len(parent),
                "T_child_median": tc,
                "T_parent_median": tp,
                "Q_2Tc_over_Tp": q,
                "absolute_closure_error": abs(q - 1.0),
            }
        )

    if len(seed_rows) < 2:
        raise RuntimeError("Too few seeds contain both Q40C cadence families.")

    child_periods = np.array([row["T_child_median"] for row in seed_rows])
    parent_periods = np.array([row["T_parent_median"] for row in seed_rows])
    ratios = np.array([row["Q_2Tc_over_Tp"] for row in seed_rows])

    rng = np.random.default_rng(RNG_SEED)
    _, median_bootstrap_ci = bootstrap_median(ratios, rng)

    candidate_errors = {
        label: float(np.median(np.abs(np.log(parent_periods / (factor * child_periods)))))
        for label, factor in FACTOR_CANDIDATES.items()
    }
    ranked_candidates = sorted(candidate_errors, key=candidate_errors.get)

    paired_error = float(np.mean(np.abs(ratios - 1.0)))
    shuffled_errors = np.empty(N_RESAMPLES, dtype=float)
    for index in range(N_RESAMPLES):
        shuffled_parent = parent_periods[rng.permutation(len(parent_periods))]
        shuffled_q = 2.0 * child_periods / shuffled_parent
        shuffled_errors[index] = np.mean(np.abs(shuffled_q - 1.0))
    p_pair = float(np.mean(shuffled_errors <= paired_error))

    gates = {
        "G1_cadence_closure": bool(
            median_bootstrap_ci[0] >= 0.995 and median_bootstrap_ci[1] <= 1.005
        ),
        "G2_factor_specificity": bool(
            ranked_candidates[0] == "2"
            and candidate_errors["2"] < candidate_errors[ranked_candidates[1]]
        ),
        "G3_seed_specific_pairing": bool(p_pair <= 0.05),
    }

    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(seed_rows[0]))
        writer.writeheader()
        writer.writerows(seed_rows)

    geometry = {
        "lower_1_over_e": lower,
        "upper_phi": phi,
        "anti_phi": anti_phi,
        "parent_midpoint": parent_midpoint,
        "parent_ridge_displacement": parent_displacement,
        "parent_diameter": parent_diameter,
        "child_radius": child_radius,
        "child_diameter": child_diameter,
        "raw_child_to_parent_width_ratio": raw_width_ratio,
        "geometry_closure_ratio_rC_over_dP": geometry_ratio,
        "exact_identity_note": (
            "rC = dP is algebraically forced by anti_phi = 2 - phi. "
            "The raw child and parent interval widths are not in a 1:2 ratio."
        ),
    }
    results = {
        "test": "T307 embedded octave-closure crosswalk",
        "status": "RETROSPECTIVE",
        "protocol": PROTOCOL.name,
        "source_hashes": {
            "Q40C_POST_RESULT_DOUBLE_HELIX_RESULTS.json": q40c_hash,
            "T306_EMBEDDED_E_PHI_THREAD_RESULTS.json": t306_hash,
        },
        "geometry": geometry,
        "t306_recalculation_checks": t306_checks,
        "quantum_cadence": {
            "eligible_seeds": len(seed_rows),
            "child_lineages": int(sum(row["child_lineages"] for row in seed_rows)),
            "parent_lineages": int(sum(row["parent_lineages"] for row in seed_rows)),
            "pooled_child_period_median": float(
                np.median(
                    [
                        float(row["angular_period_samples"])
                        for row in q40c["population_rows"]
                        if row["posthoc_two_turn_7_5_family"]
                    ]
                )
            ),
            "pooled_parent_period_median": float(
                np.median(
                    [
                        float(row["angular_period_samples"])
                        for row in q40c["population_rows"]
                        if row["posthoc_one_turn_15_family"]
                    ]
                )
            ),
            "seed_ratio_Q_2Tc_over_Tp": {
                **percentile_dict(ratios),
                "mean": float(np.mean(ratios)),
                "mean_absolute_distance_from_1": paired_error,
                "median_absolute_distance_from_1": float(
                    np.median(np.abs(ratios - 1.0))
                ),
                "bootstrap_median_95_ci": median_bootstrap_ci,
            },
        },
        "candidate_factor_control": {
            "metric": "median absolute log(T_parent / (k*T_child))",
            "errors": candidate_errors,
            "ranking": ranked_candidates,
        },
        "seed_pairing_control": {
            "paired_mean_absolute_closure_error": paired_error,
            "shuffled_mean_absolute_closure_error": {
                **percentile_dict(shuffled_errors),
                "mean": float(np.mean(shuffled_errors)),
            },
            "p_shuffled_no_worse_than_paired": p_pair,
        },
        "gates": gates,
        "verdict": {
            "q40c_population_factor_two_cadence": (
                "SUPPORTED IN THIS ARCHIVE"
                if gates["G1_cadence_closure"] and gates["G2_factor_specificity"]
                else "NOT SUPPORTED"
            ),
            "cross_domain_equivalence": (
                "FORMAL CLOSURE MOTIF ONLY — RAW INTERVAL WIDTHS ARE NOT AN OCTAVE PAIR"
            ),
            "seed_specific_child_parent_pairing": (
                "SUPPORTED" if gates["G3_seed_specific_pairing"] else "NOT SUPPORTED"
            ),
            "overall": (
                "PARTIAL — matching factor-two closure motif, not literal scale equivalence"
                if gates["G1_cadence_closure"]
                and gates["G2_factor_specificity"]
                and not gates["G3_seed_specific_pairing"]
                else "SEE GATES"
            ),
        },
        "boundaries": [
            "The geometry equality is exact algebra, not empirical evidence.",
            "The raw embedded-child/parent interval-width ratio is about 0.01127, not 0.5.",
            "Q40C cadence families were previously identified near 7.5 and 15.",
            "The result is a retrospective structural crosswalk in a deterministic simulator.",
            "It does not show that Phi causes the quantum cadence.",
        ],
        "artifacts": {
            "seed_csv": OUT_CSV.name,
            "figure": OUT_PNG.name,
        },
    }

    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)
        handle.write("\n")

    draw_report(
        geometry,
        ratios,
        candidate_errors,
        shuffled_errors,
        paired_error,
        gates,
    )

    print(json.dumps(results["verdict"], indent=2))
    print(f"eligible seeds: {len(seed_rows)}")
    print(f"median Q=2Tc/Tp: {np.median(ratios):.12f}")
    print(f"bootstrap 95% CI: {median_bootstrap_ci}")
    print(f"pairing p: {p_pair:.6f}")


if __name__ == "__main__":
    main()
