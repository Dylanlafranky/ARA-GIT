from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "Q42_ARA_DUAL_STRAND_FLOW_STRANDS.csv.gz"
PROTOCOL = ROOT / "Q57_QUANTUM_SAME_PHASE_GOLDEN_SECTION_PROTOCOL_v1_FROZEN.md"
SEEDS_CSV = ROOT / "Q57_QUANTUM_SAME_PHASE_GOLDEN_SECTION_SEEDS.csv"
SUMMARY_CSV = ROOT / "Q57_QUANTUM_SAME_PHASE_GOLDEN_SECTION_SUMMARY.csv"
RESULTS_JSON = ROOT / "Q57_QUANTUM_SAME_PHASE_GOLDEN_SECTION_RESULTS.json"
FIGURE_PNG = ROOT / "Q57_QUANTUM_SAME_PHASE_GOLDEN_SECTION.png"
FIGURE_SVG = ROOT / "Q57_QUANTUM_SAME_PHASE_GOLDEN_SECTION.svg"

CHILD = "two_turn_7_5"
PARENT = "one_turn_15"
PHI = (1.0 + math.sqrt(5.0)) / 2.0
TOL = 0.08
BOOTSTRAPS = 10_000
PERMUTATIONS = 9_999
RNG_SEED = 570031
LANDMARKS = {
    "1": 1.0,
    "sqrt2": math.sqrt(2.0),
    "1.5": 1.5,
    "phi": PHI,
    "sqrt3": math.sqrt(3.0),
    "2": 2.0,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_seed_balanced() -> tuple[list[dict], dict]:
    grouped: dict[tuple[str, int, str, str], dict[str, list[float]]] = defaultdict(
        lambda: {"forward": [], "return": []}
    )
    row_counts: dict[tuple[str, str], int] = defaultdict(int)
    with gzip.open(SOURCE, "rt", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            family = row["family"]
            if family not in {CHILD, PARENT}:
                continue
            archive = row["archive"]
            seed = int(row["seed"])
            pair = row["pair"]
            key = (archive, seed, pair, family)
            grouped[key]["forward"].append(float(row["forward_duration"]))
            grouped[key]["return"].append(float(row["return_duration"]))
            row_counts[(archive, family)] += 1

    pair_medians: dict[tuple[str, int, str], dict[str, list[float]]] = defaultdict(
        lambda: {"forward": [], "return": []}
    )
    for (archive, seed, _pair, family), values in grouped.items():
        key = (archive, seed, family)
        pair_medians[key]["forward"].append(float(np.median(values["forward"])))
        pair_medians[key]["return"].append(float(np.median(values["return"])))

    seed_family: dict[tuple[str, int, str], dict[str, float]] = {}
    for key, values in pair_medians.items():
        seed_family[key] = {
            "forward": float(np.median(values["forward"])),
            "return": float(np.median(values["return"])),
            "pair_count": len(values["forward"]),
        }

    archive_seeds: dict[str, set[int]] = defaultdict(set)
    for archive, seed, _family in seed_family:
        archive_seeds[archive].add(seed)

    rows: list[dict] = []
    omitted: dict[str, list[int]] = defaultdict(list)
    for archive in sorted(archive_seeds):
        for seed in sorted(archive_seeds[archive]):
            p_key = (archive, seed, PARENT)
            c_key = (archive, seed, CHILD)
            if p_key not in seed_family or c_key not in seed_family:
                omitted[archive].append(seed)
                continue
            p = seed_family[p_key]
            c = seed_family[c_key]
            pf, pr = p["forward"], p["return"]
            cf, cr = c["forward"], c["return"]
            r_a = pf / cf
            r_b = pr / cr
            s_a = 1.0 + 1.0 / r_a
            s_b = 1.0 + 1.0 / r_b
            p_a = 2.0 * pf / (pf + pr)
            p_b = 2.0 - p_a
            c_a = 2.0 * cf / (cf + cr)
            c_b = 2.0 - c_a
            h_a = 2.0 - p_a + 0.5 * c_a
            h_b = 2.0 - p_b + 0.5 * c_b
            h_a_local = 2.0 - p_a + c_a
            h_b_local = 2.0 - p_b + c_b
            rows.append(
                {
                    "archive": archive,
                    "seed": seed,
                    "parent_pair_count": int(p["pair_count"]),
                    "child_pair_count": int(c["pair_count"]),
                    "parent_forward_duration": pf,
                    "parent_return_duration": pr,
                    "child_forward_duration": cf,
                    "child_return_duration": cr,
                    "r_A": r_a,
                    "s_A": s_a,
                    "r_B": r_b,
                    "s_B": s_b,
                    "P_A": p_a,
                    "P_B": p_b,
                    "C_A": c_a,
                    "C_B": c_b,
                    "h_A": h_a,
                    "h_B": h_b,
                    "h_A_local_control": h_a_local,
                    "h_B_local_control": h_b_local,
                    "ratio_phi_error_A": max(abs(r_a - PHI), abs(s_a - PHI)),
                    "ratio_phi_error_B": max(abs(r_b - PHI), abs(s_b - PHI)),
                    "additive_phi_error_A": abs(h_a - PHI),
                    "additive_phi_error_B": abs(h_b - PHI),
                    "ratio_within_phi_band_A": int(
                        max(abs(r_a - PHI), abs(s_a - PHI)) <= TOL
                    ),
                    "ratio_within_phi_band_B": int(
                        max(abs(r_b - PHI), abs(s_b - PHI)) <= TOL
                    ),
                    "additive_within_phi_band_A": int(abs(h_a - PHI) <= TOL),
                    "additive_within_phi_band_B": int(abs(h_b - PHI) <= TOL),
                }
            )
    counts = {
        "source_rows": {
            f"{archive}:{family}": count
            for (archive, family), count in sorted(row_counts.items())
        },
        "eligible_seeds": {
            archive: sum(1 for row in rows if row["archive"] == archive)
            for archive in sorted(archive_seeds)
        },
        "omitted_seeds_without_both_families": {
            archive: seeds for archive, seeds in sorted(omitted.items())
        },
    }
    return rows, counts


def ci_median(values: np.ndarray, rng: np.random.Generator) -> list[float]:
    n = len(values)
    draws = rng.integers(0, n, size=(BOOTSTRAPS, n))
    medians = np.median(values[draws], axis=1)
    return [float(np.quantile(medians, 0.025)), float(np.quantile(medians, 0.975))]


def nearest(value: float) -> tuple[str, float]:
    name = min(LANDMARKS, key=lambda label: abs(value - LANDMARKS[label]))
    return name, abs(value - LANDMARKS[name])


def summarize(rows: list[dict]) -> dict:
    rng = np.random.default_rng(RNG_SEED)
    metrics = [
        "r_A",
        "s_A",
        "r_B",
        "s_B",
        "P_A",
        "P_B",
        "C_A",
        "C_B",
        "h_A",
        "h_B",
        "h_A_local_control",
        "h_B_local_control",
        "ratio_phi_error_A",
        "ratio_phi_error_B",
        "additive_phi_error_A",
        "additive_phi_error_B",
    ]
    archives = sorted({row["archive"] for row in rows})
    summary: dict[str, dict] = {}
    for archive in archives:
        selected = [row for row in rows if row["archive"] == archive]
        entry: dict[str, object] = {"n_seeds": len(selected), "metrics": {}}
        for metric in metrics:
            values = np.array([float(row[metric]) for row in selected])
            med = float(np.median(values))
            landmark, distance = nearest(med)
            entry["metrics"][metric] = {
                "median": med,
                "mean": float(np.mean(values)),
                "q25": float(np.quantile(values, 0.25)),
                "q75": float(np.quantile(values, 0.75)),
                "bootstrap_95_ci_median": ci_median(values, rng),
                "nearest_landmark": landmark,
                "nearest_landmark_distance": distance,
                "distance_to_phi": abs(med - PHI),
            }
        for formulation in ("ratio", "additive"):
            a_field = f"{formulation}_within_phi_band_A"
            b_field = f"{formulation}_within_phi_band_B"
            both = [int(row[a_field] and row[b_field]) for row in selected]
            entry[f"{formulation}_seed_fraction_both_phases_within_band"] = float(
                np.mean(both)
            )
        entry["phase_mirror"] = {
            "ratio_abs_median_difference": abs(
                entry["metrics"]["r_A"]["median"]
                - entry["metrics"]["r_B"]["median"]
            ),
            "additive_abs_median_difference": abs(
                entry["metrics"]["h_A"]["median"]
                - entry["metrics"]["h_B"]["median"]
            ),
        }
        summary[archive] = entry
    return summary


def permutation_controls(rows: list[dict]) -> dict:
    rng = np.random.default_rng(RNG_SEED + 1)
    controls: dict[str, dict] = {}
    for archive in sorted({row["archive"] for row in rows}):
        selected = [row for row in rows if row["archive"] == archive]
        pf = np.array([row["parent_forward_duration"] for row in selected])
        pr = np.array([row["parent_return_duration"] for row in selected])
        cf = np.array([row["child_forward_duration"] for row in selected])
        cr = np.array([row["child_return_duration"] for row in selected])

        def scores(child_forward: np.ndarray, child_return: np.ndarray) -> tuple[float, float]:
            r_a = pf / child_forward
            r_b = pr / child_return
            s_a = 1.0 + 1.0 / r_a
            s_b = 1.0 + 1.0 / r_b
            ratio = np.median(
                (np.abs(r_a - PHI) + np.abs(s_a - PHI) + np.abs(r_b - PHI) + np.abs(s_b - PHI))
                / 4.0
            )
            p_a = 2.0 * pf / (pf + pr)
            p_b = 2.0 - p_a
            c_a = 2.0 * child_forward / (child_forward + child_return)
            c_b = 2.0 - c_a
            h_a = 2.0 - p_a + 0.5 * c_a
            h_b = 2.0 - p_b + 0.5 * c_b
            additive = np.median((np.abs(h_a - PHI) + np.abs(h_b - PHI)) / 2.0)
            return float(ratio), float(additive)

        observed_ratio, observed_additive = scores(cf, cr)
        null_ratio = np.empty(PERMUTATIONS)
        null_additive = np.empty(PERMUTATIONS)
        for i in range(PERMUTATIONS):
            order = rng.permutation(len(cf))
            null_ratio[i], null_additive[i] = scores(cf[order], cr[order])

        wrong_r_a = pf / cr
        wrong_r_b = pr / cf
        wrong_s_a = 1.0 + 1.0 / wrong_r_a
        wrong_s_b = 1.0 + 1.0 / wrong_r_b
        wrong_ratio_error = float(
            np.median(
                (
                    np.abs(wrong_r_a - PHI)
                    + np.abs(wrong_s_a - PHI)
                    + np.abs(wrong_r_b - PHI)
                    + np.abs(wrong_s_b - PHI)
                )
                / 4.0
            )
        )
        controls[archive] = {
            "same_seed_ratio_median_phi_error": observed_ratio,
            "same_seed_additive_median_phi_error": observed_additive,
            "ratio_permutation_p_lower_is_better": float(
                (1 + np.sum(null_ratio <= observed_ratio)) / (PERMUTATIONS + 1)
            ),
            "additive_permutation_p_lower_is_better": float(
                (1 + np.sum(null_additive <= observed_additive)) / (PERMUTATIONS + 1)
            ),
            "ratio_null_median": float(np.median(null_ratio)),
            "additive_null_median": float(np.median(null_additive)),
            "wrong_phase_ratio_median_phi_error": wrong_ratio_error,
            "correct_minus_wrong_ratio_error": observed_ratio - wrong_ratio_error,
        }
    return controls


def evaluate_gates(summary: dict) -> dict:
    archives = sorted(summary)
    ratio_archive: dict[str, dict] = {}
    additive_archive: dict[str, dict] = {}
    for archive in archives:
        metrics = summary[archive]["metrics"]
        ratio_archive[archive] = {
            "phase_A_fixed_point_within_0_08": all(
                abs(metrics[name]["median"] - PHI) <= TOL for name in ("r_A", "s_A")
            ),
            "phase_B_fixed_point_within_0_08": all(
                abs(metrics[name]["median"] - PHI) <= TOL for name in ("r_B", "s_B")
            ),
            "phi_nearest_to_both_ratios": all(
                metrics[name]["nearest_landmark"] == "phi" for name in ("r_A", "r_B")
            ),
            "phase_mirror_within_0_08": summary[archive]["phase_mirror"][
                "ratio_abs_median_difference"
            ]
            <= TOL,
        }
        additive_archive[archive] = {
            "both_phases_within_0_08": all(
                abs(metrics[name]["median"] - PHI) <= TOL for name in ("h_A", "h_B")
            ),
            "phi_nearest_to_both": all(
                metrics[name]["nearest_landmark"] == "phi" for name in ("h_A", "h_B")
            ),
            "phase_mirror_within_0_08": summary[archive]["phase_mirror"][
                "additive_abs_median_difference"
            ]
            <= TOL,
        }
    ratio_replication = all(
        abs(summary[archives[0]]["metrics"][name]["median"] - summary[archives[1]]["metrics"][name]["median"])
        <= TOL
        for name in ("r_A", "r_B")
    )
    additive_replication = all(
        abs(summary[archives[0]]["metrics"][name]["median"] - summary[archives[1]]["metrics"][name]["median"])
        <= TOL
        for name in ("h_A", "h_B")
    )
    ratio_supported = (
        all(all(values.values()) for values in ratio_archive.values()) and ratio_replication
    )
    additive_supported = (
        all(all(values.values()) for values in additive_archive.values())
        and additive_replication
    )
    return {
        "ratio": {
            "by_archive": ratio_archive,
            "cross_archive_replication_within_0_08": ratio_replication,
            "status": "SUPPORTED" if ratio_supported else "NOT SUPPORTED",
        },
        "additive": {
            "by_archive": additive_archive,
            "cross_archive_replication_within_0_08": additive_replication,
            "status": "SUPPORTED" if additive_supported else "NOT SUPPORTED",
        },
    }


def write_csvs(rows: list[dict], summary: dict) -> None:
    with SEEDS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    fields = [
        "archive",
        "metric",
        "median",
        "mean",
        "q25",
        "q75",
        "ci_low",
        "ci_high",
        "nearest_landmark",
        "nearest_landmark_distance",
        "distance_to_phi",
    ]
    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for archive, archive_summary in summary.items():
            for metric, values in archive_summary["metrics"].items():
                writer.writerow(
                    {
                        "archive": archive,
                        "metric": metric,
                        "median": values["median"],
                        "mean": values["mean"],
                        "q25": values["q25"],
                        "q75": values["q75"],
                        "ci_low": values["bootstrap_95_ci_median"][0],
                        "ci_high": values["bootstrap_95_ci_median"][1],
                        "nearest_landmark": values["nearest_landmark"],
                        "nearest_landmark_distance": values["nearest_landmark_distance"],
                        "distance_to_phi": values["distance_to_phi"],
                    }
                )


def make_figure(rows: list[dict], summary: dict, gates: dict) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(15.5, 11.8))
    fig.subplots_adjust(left=0.07, right=0.985, bottom=0.07, top=0.88, hspace=0.30, wspace=0.18)
    colors = {"greedy": "#3b74b9", "landmax": "#d78c29"}
    markers = {"greedy": "o", "landmax": "^"}

    ax = axes[0, 0]
    for archive in sorted(colors):
        selected = [row for row in rows if row["archive"] == archive]
        ax.scatter(
            [row["r_A"] for row in selected],
            [row["r_B"] for row in selected],
            s=30,
            alpha=0.58,
            color=colors[archive],
            marker=markers[archive],
            label=f"{archive} seeds",
        )
    ax.axvline(PHI, color="#8e44ad", lw=2, ls="--", label="phi")
    ax.axhline(PHI, color="#8e44ad", lw=2, ls="--")
    ax.axvline(2, color="#555", lw=1.5, ls=":", label="octave 2")
    ax.axhline(2, color="#555", lw=1.5, ls=":")
    ax.set(xlabel="Phase A parent/child duration ratio", ylabel="Phase B parent/child duration ratio")
    ax.set_title("Ratio formulation: seed-balanced same-phase tiers")
    ax.legend(frameon=True, fontsize=9)

    ax = axes[0, 1]
    for archive in sorted(colors):
        selected = [row for row in rows if row["archive"] == archive]
        ax.scatter(
            [row["h_A"] for row in selected],
            [row["h_B"] for row in selected],
            s=30,
            alpha=0.58,
            color=colors[archive],
            marker=markers[archive],
            label=archive,
        )
    ax.axvline(PHI, color="#8e44ad", lw=2, ls="--", label="phi")
    ax.axhline(PHI, color="#8e44ad", lw=2, ls="--")
    ax.axvline(1.5, color="#26734d", lw=1.5, ls=":", label="1.5")
    ax.axhline(1.5, color="#26734d", lw=1.5, ls=":")
    ax.plot([1.25, 1.75], [1.75, 1.25], color="#777", lw=1, alpha=0.6, label="forced hA+hB=3")
    ax.set(xlabel="Projected TE-ARA handover hA", ylabel="Projected TE-ARA handover hB")
    ax.set_title("Additive formulation: parent 2 − parent + half-child")
    ax.legend(frameon=True, fontsize=9)

    ax = axes[1, 0]
    names = ["r_A", "s_A", "r_B", "s_B", "h_A", "h_B"]
    x = np.arange(len(names))
    width = 0.36
    for offset, archive in zip((-width / 2, width / 2), sorted(colors)):
        medians = [summary[archive]["metrics"][name]["median"] for name in names]
        lows = [summary[archive]["metrics"][name]["bootstrap_95_ci_median"][0] for name in names]
        highs = [summary[archive]["metrics"][name]["bootstrap_95_ci_median"][1] for name in names]
        yerr = np.array([[m - lo for m, lo in zip(medians, lows)], [hi - m for m, hi in zip(medians, highs)]])
        ax.bar(x + offset, medians, width, color=colors[archive], alpha=0.85, label=archive, yerr=yerr, capsize=3)
    ax.axhline(PHI, color="#8e44ad", lw=2, ls="--", label="phi")
    ax.axhline(1.5, color="#26734d", lw=1.5, ls=":", label="1.5")
    ax.axhline(2, color="#555", lw=1.5, ls="-.", label="2")
    ax.set_xticks(x, names)
    ax.set_ylabel("Archive median (95% seed-bootstrap CI)")
    ax.set_title("Frozen coordinates against named landmarks")
    ax.legend(ncol=3, fontsize=8, frameon=True)

    ax = axes[1, 1]
    labels = []
    values = []
    bar_colors = []
    for archive in sorted(colors):
        for formulation, fields in (
            ("ratio", ("ratio_phi_error_A", "ratio_phi_error_B")),
            ("additive", ("additive_phi_error_A", "additive_phi_error_B")),
        ):
            labels.append(f"{archive}\n{formulation}")
            values.append(float(np.median([(row[fields[0]] + row[fields[1]]) / 2 for row in rows if row["archive"] == archive])))
            bar_colors.append(colors[archive])
    bars = ax.bar(np.arange(len(values)), values, color=bar_colors, alpha=0.88)
    ax.axhline(TOL, color="#b23a2e", lw=2, ls="--", label="frozen 0.08 band")
    ax.set_xticks(np.arange(len(labels)), labels)
    ax.set_ylabel("Median seed-level combined phi error")
    ax.set_title(
        f"Frozen verdicts: ratio {gates['ratio']['status']} · additive {gates['additive']['status']}"
    )
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.008, f"{value:.3f}", ha="center", va="bottom", fontsize=9)
    ax.legend(frameon=True)

    fig.suptitle(
        "Q57 — quantum same-phase cross-tier golden-section test",
        fontsize=18,
        fontweight="bold",
        y=0.975,
    )
    fig.text(
        0.5,
        0.942,
        "Q42 one-turn-15 parent vs two-turn-7.5 child · forward and return tested independently",
        ha="center",
        fontsize=11,
        color="#444",
    )
    fig.savefig(FIGURE_PNG, dpi=180)
    fig.savefig(FIGURE_SVG)
    plt.close(fig)


def main() -> None:
    rows, counts = read_seed_balanced()
    summary = summarize(rows)
    controls = permutation_controls(rows)
    gates = evaluate_gates(summary)
    max_invariant_error = max(
        max(
            abs(row["P_A"] + row["P_B"] - 2.0),
            abs(row["C_A"] + row["C_B"] - 2.0),
            abs(row["h_A"] + row["h_B"] - 3.0),
        )
        for row in rows
    )
    write_csvs(rows, summary)
    make_figure(rows, summary, gates)
    results = {
        "test_id": "Q57",
        "title": "Quantum same-phase cross-tier golden-section test",
        "frozen_protocol_sha256": sha256(PROTOCOL),
        "source_sha256": sha256(SOURCE),
        "constants": {
            "phi": PHI,
            "tolerance": TOL,
            "bootstraps": BOOTSTRAPS,
            "permutations": PERMUTATIONS,
            "rng_seed": RNG_SEED,
            "landmarks": LANDMARKS,
            "child_projection_into_parent_units": 0.5,
        },
        "counts": counts,
        "summary": summary,
        "controls": controls,
        "gates": gates,
        "arithmetic": {"max_forced_identity_error": max_invariant_error},
        "files": {
            "source": str(SOURCE),
            "protocol": str(PROTOCOL),
            "seed_csv": str(SEEDS_CSV),
            "summary_csv": str(SUMMARY_CSV),
            "figure_png": str(FIGURE_PNG),
            "figure_svg": str(FIGURE_SVG),
        },
    }
    RESULTS_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps({"gates": gates, "counts": counts, "summary": summary, "controls": controls}, indent=2))


if __name__ == "__main__":
    main()
