from __future__ import annotations

import hashlib
import json
import pathlib

import numpy as np
import pandas as pd


ROOT = pathlib.Path(__file__).resolve().parent
RESULTS = ROOT / "results"


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def close(a: float, b: float, tolerance: float = 1e-9) -> bool:
    return bool(np.isfinite(a) and np.isfinite(b) and abs(a - b) <= tolerance)


def main() -> None:
    events = pd.read_csv(RESULTS / "T431_CONFIRMATION_EVENTS.csv")
    controls = pd.read_csv(RESULTS / "T431_CONFIRMATION_CONTROLS.csv")
    histories = pd.read_csv(RESULTS / "T431_CONFIRMATION_HISTORIES.csv")
    summary = json.loads((RESULTS / "T431_CONFIRMATION_SUMMARY.json").read_text(encoding="utf-8"))
    audit = json.loads((RESULTS / "T431_SOURCE_AUDIT.json").read_text(encoding="utf-8"))
    development = set(pd.read_csv(RESULTS / "T431_DEVELOPMENT_LEDGER_EVENTS.csv")["event"])

    checks: dict[str, object] = {}
    checks["four_unique_confirmation_events"] = len(events) == 4 and events["event"].nunique() == 4
    checks["confirmation_absent_from_development"] = not bool(set(events["event"]) & development)
    checks["two_source_files_per_event"] = all(sum(row["event"] == event for row in audit) == 2 for event in events["event"])
    checks["all_source_hashes_match"] = all(
        pathlib.Path(str(row["local_path"])).exists()
        and sha256(pathlib.Path(str(row["local_path"]))) == row["sha256"]
        for row in audit
    )
    checks["all_api_gps_match"] = all(bool(row["gps_matches_api"]) for row in audit)
    checks["controls_per_event_equal"] = controls.groupby("event").size().nunique() == 1
    checks["no_nonfinite_primary_metrics"] = bool(np.isfinite(events[[
        "C_old", "C_mobile", "C_new", "M_old", "M_mobile", "M_new",
        "connection_break_depth", "movement_excursion", "ledger_strength",
        "ledger_empirical_p", "phase_coherence_offsource_percentile",
    ]].to_numpy(dtype=float)).all())

    arithmetic_ok = True
    history_ok = True
    pvalue_ok = True
    for _, row in events.iterrows():
        connection_break = (float(row["C_old"]) + float(row["C_new"])) / 2.0 - float(row["C_mobile"])
        movement_excursion = float(row["M_mobile"]) - (float(row["M_old"]) + float(row["M_new"])) / 2.0
        arithmetic_ok &= close(connection_break, float(row["connection_break_depth"]))
        arithmetic_ok &= close(movement_excursion, float(row["movement_excursion"]))
        arithmetic_ok &= close(connection_break + movement_excursion, float(row["ledger_strength"]))
        event_controls = controls[controls["event"] == row["event"]]
        expected_p = (1 + np.sum(event_controls["ledger_strength"] >= float(row["ledger_strength"]))) / (len(event_controls) + 1)
        pvalue_ok &= close(float(expected_p), float(row["ledger_empirical_p"]))
        h = histories[histories["event"] == row["event"]]
        for time_key, c_key, m_key in (
            ("pre_time_s", "C_old", "M_old"),
            ("mobile_time_s", "C_mobile", "M_mobile"),
            ("post_time_s", "C_new", "M_new"),
        ):
            index = (h["time_s"] - float(row[time_key])).abs().idxmin()
            history_ok &= close(float(h.loc[index, "connection_C"]), float(row[c_key]), 1e-8)
            history_ok &= close(float(h.loc[index, "movement_M"]), float(row[m_key]), 1e-8)
    checks["ledger_arithmetic_recomputed"] = arithmetic_ok
    checks["event_pvalues_recomputed"] = pvalue_ok
    checks["landmarks_match_saved_histories"] = history_ok

    recomputed_counts = {
        "network_shape": int(events["network_shape_pass"].sum()),
        "source_specific_p_le_0_05": int((events["ledger_empirical_p"] <= 0.05).sum()),
        "detector_replication": int(events["detector_replication_pass"].sum()),
        "unresolved_mobile": int((events["unresolved_mobile_excess"] > 0).sum()),
        "phase_coherence_ge_p90": int((events["phase_coherence_offsource_percentile"] >= 0.90).sum()),
    }
    checks["summary_counts_recomputed"] = recomputed_counts == summary["counts"]
    gates = {
        "gate_1_network_shape_3_of_4": recomputed_counts["network_shape"] >= 3,
        "gate_2_source_specific_3_of_4": recomputed_counts["source_specific_p_le_0_05"] >= 3,
        "gate_3_detector_replication_2_of_4": recomputed_counts["detector_replication"] >= 2,
        "gate_4_unresolved_mobile_3_of_4": recomputed_counts["unresolved_mobile"] >= 3,
        "gate_5_phase_coherence_3_of_4": recomputed_counts["phase_coherence_ge_p90"] >= 3,
    }
    checks["summary_gates_recomputed"] = gates == summary["gates"]
    checks["verdict_recomputed"] = summary["verdict"] == ("SUPPORTED" if all(gates.values()) else "NOT SUPPORTED")
    checks["all_checks_pass"] = all(bool(value) for value in checks.values())
    output = {
        "checks": checks,
        "recomputed_counts": recomputed_counts,
        "recomputed_gates": gates,
        "validated_files": {
            "events": sha256(RESULTS / "T431_CONFIRMATION_EVENTS.csv"),
            "controls": sha256(RESULTS / "T431_CONFIRMATION_CONTROLS.csv"),
            "histories": sha256(RESULTS / "T431_CONFIRMATION_HISTORIES.csv"),
            "summary": sha256(RESULTS / "T431_CONFIRMATION_SUMMARY.json"),
        },
    }
    (RESULTS / "T431_INDEPENDENT_VALIDATION.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))
    if not checks["all_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
