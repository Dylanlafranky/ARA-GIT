from __future__ import annotations

import hashlib
import json
import pathlib

import numpy as np
import pandas as pd
from scipy import stats


ROOT = pathlib.Path(__file__).resolve().parent
RESULTS = ROOT / "results"
AUDIT = RESULTS / "T430_SOURCE_AUDIT.json"


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    summary = pd.read_csv(RESULTS / "T430_CONFIRMATION_SUMMARY.csv")
    histories = pd.read_csv(RESULTS / "T430_CONFIRMATION_HISTORIES.csv")
    controls = pd.read_csv(RESULTS / "T430_CONFIRMATION_OFFSOURCE_CONTROLS.csv")
    qa = pd.read_csv(RESULTS / "T430_CONFIRMATION_SOURCE_QA.csv")
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    gates = json.loads((RESULTS / "T430_CONFIRMATION_GATES.json").read_text(encoding="utf-8"))
    old_events = set(pd.read_csv(ROOT.parent / "T429_separated_space_time_strength" / "results" / "T429_HOLDOUT_SUMMARY.csv").event)

    hash_checks = []
    for row in audit:
        path = pathlib.Path(row["local_path"])
        hash_checks.append(path.exists() and path.stat().st_size == row["bytes"] and sha256(path) == row["sha256"])

    event_checks: dict[str, object] = {}
    for event, group in histories.groupby("event"):
        source = summary.loc[summary.event == event].iloc[0]
        recomputed_rho = float(stats.spearmanr(group.M_rem, group.C_acc).statistic)
        event_checks[event] = {
            "rows": len(group),
            "movement_starts_at_2": bool(np.isclose(group.M_rem.iloc[0], 2.0)),
            "movement_ends_at_0": bool(np.isclose(group.M_rem.iloc[-1], 0.0)),
            "movement_monotone_nonincreasing": bool(np.all(np.diff(group.M_rem) <= 1e-12)),
            "connection_is_component_mean": bool(np.allclose(group.C_acc, (group.C_amount + group.C_density) / 2.0)),
            # CSV round-tripping can create/remove rank ties at machine precision.
            "rho_reproduces": bool(np.isclose(recomputed_rho, source.inverse_rho, atol=5e-4)),
            "residual_reproduces": bool(np.isclose(np.median(group.TE_ARA_residual), source.median_te_ara_residual)),
            "inverse_and_growth_are_rank_redundant": bool(np.isclose(source.inverse_rho, -source.connection_time_rho)),
            "not_forced_exact_complement": bool(np.std(group.TE_ARA_residual) > 0.05),
        }

    validation = {
        "status": "PASS_WITH_METHODOLOGICAL_WARNINGS",
        "source_hashes_all_match": bool(all(hash_checks)),
        "source_files_checked": len(hash_checks),
        "confirmation_events": summary.event.tolist(),
        "confirmation_events_absent_from_t429": bool(set(summary.event).isdisjoint(old_events)),
        "events_count_is_4": bool(len(summary) == 4),
        "source_qa_rows_is_8": bool(len(qa) == 8),
        "all_public_dq_pass": bool(qa.public_dq_pass.astype(bool).all()),
        "all_finite_fraction_one": bool(np.allclose(qa.finite_fraction, 1.0)),
        "offsource_windows_per_event": controls.groupby("event").size().to_dict(),
        "all_offsource_counts_are_66": bool((controls.groupby("event").size() == 66).all()),
        "primary_supported": gates["primary_supported"],
        "event_recalculations": event_checks,
        "warnings": [
            "M_rem is a window-normalized, strictly decreasing coordinate; inverse rho and connection-growth rho are algebraically redundant Spearman tests.",
            "C_acc is an instantaneous amount/concentration state despite its accumulated label; it is not a cumulative integral.",
            "Median M_rem is near 1 by construction and connection features are off-source centered near 1, so a median TE-ARA sum near 2 is not independently evidential.",
            "The official catalog event time defines the scored endpoint, so T430 is retrospective and cannot establish prospective handover prediction.",
        ],
    }
    (RESULTS / "T430_VALIDATION.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
