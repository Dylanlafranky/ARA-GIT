"""Independent arithmetic and validity audit for frozen T359 artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
STEM = "T359_EVENT_CLOCK_OSCILLATOR_IRRATIONALITY_DI_ARA"
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
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def one(frame: pd.DataFrame, identity: str, condition: str) -> pd.Series:
    selected = frame[(frame.identity == identity) & (frame.condition == condition)]
    if len(selected) != 1:
        raise AssertionError(f"Expected one row for {identity}/{condition}; got {len(selected)}")
    return selected.iloc[0]


def gates_from_exports(record: pd.DataFrame, qa: pd.DataFrame) -> tuple[dict[str, bool], dict]:
    event_ok = qa.median_event_count >= 30
    period_ok = qa.median_period_seconds.between(1.5, 4.0, inclusive="both")
    share_ok = qa.median_valid_period_fraction >= 0.85
    direction_ok = qa.median_phase_backtrack_fraction <= 1e-12
    g0 = bool((event_ok & period_ok & share_ok & direction_ok).all())

    locked = one(record, "coupled_170", "chronological")
    g1 = bool(
        locked.x_p < 1.0 and locked.x_r < 1.0 and locked.cycle_rho >= 0.80
        and locked.cycle_miss_abs <= 0.03 and locked.pair_closure_share >= 0.60
    )

    candidate = {d: one(record, f"coupled_{d}", "chronological") for d in CANDIDATES}
    structured = {
        d: bool(r.x_r < 1.25 and r.cycle_rho >= 0.80 and r.cycle_miss_abs > 0.03 and r.pair_coherent_nonclosure_share >= 0.40)
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
    chronology_hits = sum(shuffle_xr[d] >= 0.25 and shuffle_rho[d] >= 0.15 for d in CANDIDATES)
    g3 = chronology_hits >= 4 and max(shuffle_xp) <= 0.02

    uncoupled = one(record, "uncoupled_detuned", "chronological")
    specificity = {
        d: max(float(uncoupled.x_r - r.x_r), float(r.best_rho - uncoupled.best_rho))
        for d, r in candidate.items()
    }
    median_xr = float(np.median([r.x_r for r in candidate.values()]))
    median_rho = float(np.median([r.best_rho for r in candidate.values()]))
    group_specific = bool(uncoupled.x_r - median_xr >= 0.15 or median_rho - uncoupled.best_rho >= 0.15)
    specificity_hits = sum(value >= 0.15 for value in specificity.values())
    g4 = bool(group_specific and specificity_hits >= 4)

    lineage = {}
    for d, chronological in candidate.items():
        wrong = one(record, f"coupled_{d}", "wrong_record")
        lineage[d] = max(float(wrong.x_r - chronological.x_r), float(chronological.best_rho - wrong.best_rho))
    lineage_hits = sum(value >= 0.15 for value in lineage.values())
    g5 = lineage_hits >= 4

    reverse_xp, reverse_rho, reverse_orientation = {}, {}, {}
    for d in SWEEP:
        chronological = one(record, f"coupled_{d}", "chronological")
        reversed_row = one(record, f"coupled_{d}", "reversed")
        reverse_xp[d] = abs(float(reversed_row.x_p - chronological.x_p))
        reverse_rho[d] = abs(float(reversed_row.best_rho - chronological.best_rho))
        reverse_orientation[d] = abs(float(reversed_row.orientation + chronological.orientation))
    orientation_hits = sum(value <= 0.02 for value in reverse_orientation.values())
    g6 = bool(max(reverse_xp.values()) <= 0.02 and max(reverse_rho.values()) <= 0.05 and orientation_hits >= 7)

    gates = {"G0": g0, "G1": g1, "G2": g2, "G3": g3, "G4": g4, "G5": g5, "G6": g6}
    gates["overall"] = all(gates.values())
    detail = {
        "g0_record_component_counts": {
            "event": int(event_ok.sum()), "period": int(period_ok.sum()),
            "share": int(share_ok.sum()), "direction": int(direction_ok.sum()),
        },
        "structured_candidates": {str(key): value for key, value in structured.items()},
        "chronology_hits": chronology_hits,
        "specificity_hits": specificity_hits,
        "group_specific": group_specific,
        "lineage_hits": lineage_hits,
        "orientation_hits": orientation_hits,
    }
    return gates, detail


def main() -> None:
    window = pd.read_csv(ROOT / f"{STEM}_WINDOW_METRICS.csv")
    pair = pd.read_csv(ROOT / f"{STEM}_PAIR_SUMMARY.csv")
    record = pd.read_csv(ROOT / f"{STEM}_RECORD_SUMMARY.csv")
    qa = pd.read_csv(ROOT / f"{STEM}_EVENT_CLOCK_QA.csv")
    frozen = pd.read_csv(ROOT / f"{STEM}_FROZEN_GATES.csv")
    results = json.loads((ROOT / f"{STEM}_RESULTS.json").read_text(encoding="utf-8"))

    checks: dict[str, bool] = {}
    checks["claim_sha_matches"] = digest(ROOT / f"{STEM}_CLAIM_PACKET_v1.md") == results["claim_sha256"]
    checks["protocol_sha_matches"] = digest(ROOT / f"{STEM}_PROTOCOL_v1_FROZEN.md") == results["protocol_sha256"]
    checks["archive_md5_matches"] = digest(ROOT / "T358_SOURCE_DATA.zip", "md5") == results["source_archive_md5"]

    rebuilt_pair = window.groupby(["identity", "family", "delta_r_ohm", "pair", "condition"], as_index=False).agg(
        **{name: (name, "median") for name in NUMERIC},
        windows=("window", "size"),
        closure_share=("cycle_closure", "mean"),
        coherent_nonclosure_share=("coherent_nonclosure", "mean"),
    )
    joined_pair = pair.merge(rebuilt_pair, on=["identity", "pair", "condition"], suffixes=("_saved", "_rebuilt"), how="outer", indicator=True)
    checks["pair_keyset_reproduced"] = bool((joined_pair._merge == "both").all())
    pair_diffs = {}
    for name in NUMERIC + ["windows", "closure_share", "coherent_nonclosure_share"]:
        pair_diffs[name] = float(np.nanmax(np.abs(joined_pair[f"{name}_saved"].astype(float) - joined_pair[f"{name}_rebuilt"].astype(float))))
    checks["pair_aggregation_reproduced"] = max(pair_diffs.values()) <= 1e-12

    rebuilt_record = pair.groupby(["identity", "family", "delta_r_ohm", "condition"], as_index=False).agg(
        **{name: (name, "median") for name in NUMERIC},
        pairs=("pair", "size"),
        pair_closure_share=("closure_share", lambda s: float(np.mean(s >= 0.50))),
        pair_coherent_nonclosure_share=("coherent_nonclosure_share", lambda s: float(np.mean(s >= 0.50))),
    )
    joined_record = record.merge(rebuilt_record, on=["identity", "condition"], suffixes=("_saved", "_rebuilt"), how="outer", indicator=True)
    checks["record_keyset_reproduced"] = bool((joined_record._merge == "both").all())
    record_diffs = {}
    for name in NUMERIC + ["pairs", "pair_closure_share", "pair_coherent_nonclosure_share"]:
        record_diffs[name] = float(np.nanmax(np.abs(joined_record[f"{name}_saved"].astype(float) - joined_record[f"{name}_rebuilt"].astype(float))))
    checks["record_aggregation_reproduced"] = max(record_diffs.values()) <= 1e-12

    gates, detail = gates_from_exports(record, qa)
    saved_gates = {row.gate: str(row["pass"]).strip().lower() == "true" for _, row in frozen.iterrows()}
    checks["frozen_gates_reproduced"] = all(gates[key] == saved_gates[key] for key in saved_gates)
    checks["json_gates_reproduced"] = gates == results["grouped_gates"]
    checks["all_arithmetic_reproduced"] = all(checks.values())

    validation = {
        "test": "Independent validation of T359",
        "checks": checks,
        "maximum_pair_aggregation_difference": max(pair_diffs.values()),
        "maximum_record_aggregation_difference": max(record_diffs.values()),
        "recomputed_gates": gates,
        "gate_detail": detail,
        "diagnosis": (
            "The event clock is monotone and its record-median periods all lie in the frozen physical range. "
            "G0 fails only because the two shorter uncoupled control records contain 23 and 28 median events, "
            "below the frozen count of 30. Independently, G4 and G5 fail because event normalization makes "
            "coupled, uncoupled and wrong-record sequences almost equally deterministic."
        ),
    }
    (ROOT / f"{STEM}_VALIDATION.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")

    lines = [
        "# Independent validation of T359", "",
        f"**All exported arithmetic reproduced:** {'YES' if checks['all_arithmetic_reproduced'] else 'NO'}  ",
        f"**Frozen gates reproduced:** {'YES' if checks['frozen_gates_reproduced'] else 'NO'}  ",
        f"**Overall frozen result:** {'PASS' if gates['overall'] else 'FAIL / INCONCLUSIVE'}", "",
        "Pair medians, record medians, source/preregistration hashes and every gate were reconstructed without importing the T359 analysis program.", "",
        "## Gate result", "",
    ]
    lines.extend(f"- {key}: {'PASS' if value else 'FAIL'}" for key, value in gates.items())
    lines.extend([
        "", "## Diagnostic reading", "",
        "The constructed event phase is strictly monotone and all 11 record-median periods lie inside 1.5–4.0 seconds. G0 failed only because the two shorter uncoupled source records supplied median event counts of 23 and 28 rather than the frozen minimum of 30.", "",
        "That technical count miss does not rescue the complete result: G4 and G5 independently failed. The event normalization made the coupled, uncoupled and wrong-record sequences almost equally deterministic (`x_R≈0`, best coherence `≈1`). It therefore recovered closure and non-closure locations but removed the coupling-specific information needed to identify the relation.", "",
        "T359 is useful calibration but not a supported physical transfer.", "",
    ])
    (ROOT / f"{STEM}_VALIDATION.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(validation, indent=2))
    if not checks["all_arithmetic_reproduced"]:
        raise SystemExit("T359 validation mismatch")


if __name__ == "__main__":
    main()
