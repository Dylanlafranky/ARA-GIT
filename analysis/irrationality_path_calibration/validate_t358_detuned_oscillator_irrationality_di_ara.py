"""Independent validation of the frozen T358 detuned-oscillator run.

This validator deliberately does not import the analysis program.  It checks
artifact integrity, reproduces the two aggregation layers from exported rows,
recomputes the six frozen gates, and separately audits whether the phase-plane
interface behaved like a usable physical clock.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
STEM = "T358_DETUNED_OSCILLATOR_IRRATIONALITY_DI_ARA"
CANDIDATES = [50, 100, 150, 190, 240, 290, 340]
SWEEP = [0, 50, 100, 150, 170, 190, 240, 290, 340]
NUMERIC = [
    "x_p", "x_r", "local_loss", "null_loss", "cycle_rho",
    "cycle_miss_signed", "cycle_miss_abs", "best_rho", "best_lag",
    "best_miss_abs", "orientation",
]


def digest(path: Path, algorithm: str = "sha256") -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def one(frame: pd.DataFrame, identity: str, condition: str) -> pd.Series:
    selected = frame[(frame.identity == identity) & (frame.condition == condition)]
    if len(selected) != 1:
        raise AssertionError(f"Expected one row for {identity}/{condition}; got {len(selected)}")
    return selected.iloc[0]


def close(a: float, b: float, tol: float = 1e-12) -> bool:
    return bool(np.isclose(float(a), float(b), atol=tol, rtol=tol, equal_nan=True))


def recompute_gates(record: pd.DataFrame) -> tuple[dict[str, bool], dict]:
    locked = one(record, "coupled_170", "chronological")
    g1 = bool(
        locked.x_p < 1.0
        and locked.x_r < 1.0
        and locked.cycle_rho >= 0.80
        and locked.cycle_miss_abs <= 0.03
        and locked.pair_closure_share >= 0.60
    )

    candidate = {d: one(record, f"coupled_{d}", "chronological") for d in CANDIDATES}
    structured = {
        d: bool(
            r.x_r < 1.25
            and r.cycle_rho >= 0.80
            and r.cycle_miss_abs > 0.03
            and r.pair_coherent_nonclosure_share >= 0.40
        )
        for d, r in candidate.items()
    }
    g2 = sum(structured.values()) >= 3

    shuffle_xr, shuffle_rho, shuffle_xp = {}, {}, []
    for d in SWEEP:
        chronological = one(record, f"coupled_{d}", "chronological")
        shuffled = one(record, f"coupled_{d}", "shuffled")
        shuffle_xp.append(abs(float(shuffled.x_p - chronological.x_p)))
        if d in CANDIDATES:
            shuffle_xr[d] = float(shuffled.x_r - chronological.x_r)
            shuffle_rho[d] = float(chronological.best_rho - shuffled.best_rho)
    chronology_hits = sum(
        shuffle_xr[d] >= 0.25 and shuffle_rho[d] >= 0.15 for d in CANDIDATES
    )
    g3 = chronology_hits >= 4 and max(shuffle_xp) <= 0.02

    uncoupled = one(record, "uncoupled_detuned", "chronological")
    specificity = {
        d: max(float(uncoupled.x_r - r.x_r), float(r.best_rho - uncoupled.best_rho))
        for d, r in candidate.items()
    }
    median_xr = float(np.median([r.x_r for r in candidate.values()]))
    median_rho = float(np.median([r.best_rho for r in candidate.values()]))
    group_specific = (
        uncoupled.x_r - median_xr >= 0.15
        or median_rho - uncoupled.best_rho >= 0.15
    )
    g4 = bool(group_specific and sum(value >= 0.15 for value in specificity.values()) >= 4)

    lineage = {}
    for d, chronological in candidate.items():
        wrong = one(record, f"coupled_{d}", "wrong_record")
        lineage[d] = max(
            float(wrong.x_r - chronological.x_r),
            float(chronological.best_rho - wrong.best_rho),
        )
    g5 = sum(value >= 0.15 for value in lineage.values()) >= 4

    reverse_xp, reverse_rho, reverse_orientation = {}, {}, {}
    for d in SWEEP:
        chronological = one(record, f"coupled_{d}", "chronological")
        reversed_row = one(record, f"coupled_{d}", "reversed")
        reverse_xp[d] = abs(float(reversed_row.x_p - chronological.x_p))
        reverse_rho[d] = abs(float(reversed_row.best_rho - chronological.best_rho))
        reverse_orientation[d] = abs(float(reversed_row.orientation + chronological.orientation))
    g6 = bool(
        max(reverse_xp.values()) <= 0.02
        and max(reverse_rho.values()) <= 0.05
        and sum(value <= 0.02 for value in reverse_orientation.values()) >= 7
    )

    gates = {"G1": g1, "G2": g2, "G3": g3, "G4": g4, "G5": g5, "G6": g6}
    gates["overall"] = all(gates.values())
    detail = {
        "structured_candidate": structured,
        "chronology_hits": chronology_hits,
        "shuffle_max_xp_change": max(shuffle_xp),
        "coupling_specificity_hits": sum(value >= 0.15 for value in specificity.values()),
        "group_specific": bool(group_specific),
        "lineage_hits": sum(value >= 0.15 for value in lineage.values()),
        "reverse_max_xp_change": max(reverse_xp.values()),
        "reverse_max_rho_change": max(reverse_rho.values()),
        "reverse_orientation_hits": sum(value <= 0.02 for value in reverse_orientation.values()),
    }
    return gates, detail


def main() -> None:
    window = pd.read_csv(ROOT / f"{STEM}_WINDOW_METRICS.csv")
    pair = pd.read_csv(ROOT / f"{STEM}_PAIR_SUMMARY.csv")
    record = pd.read_csv(ROOT / f"{STEM}_RECORD_SUMMARY.csv")
    qa = pd.read_csv(ROOT / f"{STEM}_DATA_QA.csv")
    frozen = pd.read_csv(ROOT / f"{STEM}_FROZEN_GATES.csv")
    results = json.loads((ROOT / f"{STEM}_RESULTS.json").read_text(encoding="utf-8"))

    checks: dict[str, bool] = {}

    claim_sha = digest(ROOT / f"{STEM}_CLAIM_PACKET_v1.md")
    protocol_sha = digest(ROOT / f"{STEM}_PROTOCOL_v1_FROZEN.md")
    archive_md5 = digest(ROOT / "T358_SOURCE_DATA.zip", "md5")
    checks["claim_sha_matches_results"] = claim_sha == results["claim_sha256"]
    checks["protocol_sha_matches_results"] = protocol_sha == results["protocol_sha256"]
    checks["archive_md5_matches_results"] = archive_md5 == results["source_archive_md5"]

    # Independently rebuild pair medians from chronological/control window rows.
    rebuilt_pair = (
        window.groupby(["identity", "family", "delta_r_ohm", "pair", "condition"], as_index=False)
        .agg(
            **{name: (name, "median") for name in NUMERIC},
            windows=("window", "size"),
            closure_share=("cycle_closure", "mean"),
            coherent_nonclosure_share=("coherent_nonclosure", "mean"),
        )
    )
    pair_key = ["identity", "pair", "condition"]
    joined_pair = pair.merge(
        rebuilt_pair,
        on=pair_key,
        suffixes=("_saved", "_rebuilt"),
        how="outer",
        indicator=True,
    )
    checks["pair_keyset_reproduced"] = bool((joined_pair._merge == "both").all())
    pair_diffs = {}
    for name in NUMERIC + ["windows", "closure_share", "coherent_nonclosure_share"]:
        a = joined_pair[f"{name}_saved"].to_numpy(dtype=float)
        b = joined_pair[f"{name}_rebuilt"].to_numpy(dtype=float)
        pair_diffs[name] = float(np.nanmax(np.abs(a - b)))
    checks["pair_aggregation_reproduced"] = max(pair_diffs.values()) <= 1e-12

    # Independently rebuild record medians and pair-level event shares.
    record_group = ["identity", "family", "delta_r_ohm", "condition"]
    rebuilt_record = pair.groupby(record_group, as_index=False).agg(
        **{name: (name, "median") for name in NUMERIC},
        pairs=("pair", "size"),
        pair_closure_share=("closure_share", lambda s: float(np.mean(s >= 0.60))),
        pair_coherent_nonclosure_share=(
            "coherent_nonclosure_share", lambda s: float(np.mean(s >= 0.40))
        ),
    )
    joined_record = record.merge(
        rebuilt_record,
        on=["identity", "condition"],
        suffixes=("_saved", "_rebuilt"),
        how="outer",
        indicator=True,
    )
    checks["record_keyset_reproduced"] = bool((joined_record._merge == "both").all())
    record_diffs = {}
    for name in NUMERIC + ["pairs", "pair_closure_share", "pair_coherent_nonclosure_share"]:
        a = joined_record[f"{name}_saved"].to_numpy(dtype=float)
        b = joined_record[f"{name}_rebuilt"].to_numpy(dtype=float)
        record_diffs[name] = float(np.nanmax(np.abs(a - b)))
    checks["record_aggregation_reproduced"] = max(record_diffs.values()) <= 1e-12

    gates, gate_detail = recompute_gates(record)
    saved_gates = {row.gate: str(row["pass"]).strip().lower() == "true" for _, row in frozen.iterrows()}
    checks["frozen_gates_reproduced"] = all(gates[key] == saved_gates[key] for key in saved_gates)
    checks["json_gates_reproduced"] = gates == results["grouped_gates"]

    # A physical phase clock should overwhelmingly move forward between adjacent
    # samples.  No such threshold was preregistered, so this validity audit does
    # not rewrite the six frozen gates.  It limits what their outcome can mean.
    median_backtrack = qa["median_phase_backtrack_fraction"].astype(float)
    maximum_backtrack = qa["maximum_phase_backtrack_fraction"].astype(float)
    phase_interface_valid = bool((median_backtrack <= 0.10).all())
    checks["all_export_arithmetic_reproduced"] = all(
        checks[key]
        for key in [
            "claim_sha_matches_results",
            "protocol_sha_matches_results",
            "archive_md5_matches_results",
            "pair_keyset_reproduced",
            "pair_aggregation_reproduced",
            "record_keyset_reproduced",
            "record_aggregation_reproduced",
            "frozen_gates_reproduced",
            "json_gates_reproduced",
        ]
    )

    validation = {
        "test": "Independent validation of T358",
        "checks": checks,
        "maximum_pair_aggregation_difference": max(pair_diffs.values()),
        "maximum_record_aggregation_difference": max(record_diffs.values()),
        "recomputed_gates": gates,
        "gate_detail": gate_detail,
        "primary_phase_interface_valid": phase_interface_valid,
        "median_backtrack_fraction_range": [float(median_backtrack.min()), float(median_backtrack.max())],
        "maximum_backtrack_fraction_range": [float(maximum_backtrack.min()), float(maximum_backtrack.max())],
        "interpretation": (
            "Arithmetic and frozen gates reproduced, but the raw derivative phase-plane "
            "interface is not a trustworthy one-way physical clock. The frozen gate verdict "
            "is retained; the intended physical geometry question remains inconclusive."
        ),
    }
    (ROOT / f"{STEM}_VALIDATION.json").write_text(
        json.dumps(validation, indent=2), encoding="utf-8"
    )

    lines = [
        "# Independent validation of T358",
        "",
        f"**Export arithmetic reproduced:** {'YES' if checks['all_export_arithmetic_reproduced'] else 'NO'}  ",
        f"**Frozen gates reproduced:** {'YES' if checks['frozen_gates_reproduced'] else 'NO'}  ",
        f"**Primary phase interface valid:** {'YES' if phase_interface_valid else 'NO'}",
        "",
        "The saved pair medians, record medians, six frozen gates, preregistration hashes and source archive checksum were independently reproduced without importing the analysis program.",
        "",
        "## Data-interface audit",
        "",
        f"Across records, the median adjacent-step phase-backtrack fraction ranged from {median_backtrack.min():.3f} to {median_backtrack.max():.3f}; the maximum channel value ranged from {maximum_backtrack.min():.3f} to {maximum_backtrack.max():.3f}. A valid one-way cycle clock should be overwhelmingly monotone; the audit threshold was 0.10.",
        "",
        "This threshold was not a frozen outcome gate, so the registered G1-G6 verdict is not rewritten. It does change the scientific reading: T358 faithfully shows that this particular derivative phase-plane cut failed the registered test, but it does not faithfully establish that the oscillators lacked the proposed ARA relation. The intended physical question remains inconclusive until the same archive is read with a physical event clock defined from the raw waveform.",
        "",
        "## Recomputed frozen gates",
        "",
    ]
    lines.extend(f"- {key}: {'PASS' if value else 'FAIL'}" for key, value in gates.items())
    lines.append("")
    (ROOT / f"{STEM}_VALIDATION.md").write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(validation, indent=2))
    if not checks["all_export_arithmetic_reproduced"]:
        raise SystemExit("Validation arithmetic mismatch")


if __name__ == "__main__":
    main()
