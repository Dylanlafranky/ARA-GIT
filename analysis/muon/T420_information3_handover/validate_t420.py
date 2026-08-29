from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
PROTOCOL = ROOT / "T420_FROZEN_PROTOCOL.md"
ANALYSIS = ROOT / "t420_information3_handover.py"
STAGES = ("DEVELOPMENT", "VALIDATION", "HOLDOUT")
TOL = 2e-9


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def close(a: float, b: float, tol: float = TOL) -> bool:
    return bool(np.isfinite(a) and np.isfinite(b) and abs(a - b) <= tol)


def main() -> None:
    checks: dict[str, dict[str, object]] = {}
    stage_results: dict[str, object] = {}

    for stage in STAGES:
        tag = stage.upper()
        result_path = RESULTS / f"T420_{tag}_RESULTS.json"
        timeline_path = RESULTS / f"T420_{tag}_TIMELINE.csv"
        event_path = RESULTS / f"T420_{tag}_CROSSING_EVENTS.csv"
        prediction_path = RESULTS / f"T420_{tag}_PREDICTION_ROWS.csv"
        sequence_path = RESULTS / f"T420_{tag}_SEQUENCE_METRICS.csv"

        result = json.loads(result_path.read_text(encoding="utf-8"))
        timeline = read_csv(timeline_path)
        events = read_csv(event_path)
        predictions = read_csv(prediction_path)
        sequence_metrics = read_csv(sequence_path)

        protocol_ok = result["protocol_sha256"] == sha256(PROTOCOL)
        analysis_ok = result["analysis_sha256"] == sha256(ANALYSIS)
        checks[f"{tag}_hashes"] = {
            "pass": protocol_ok and analysis_ok,
            "protocol_match": protocol_ok,
            "analysis_match": analysis_ok,
        }

        shared = np.asarray([float(r["shared_native_bins"]) for r in predictions])
        horizon = np.asarray([float(r["horizon_native_bins"]) for r in predictions])
        checks[f"{tag}_causality"] = {
            "pass": bool(np.all(shared == 0) and np.all(horizon == 128)),
            "max_shared_native_bins": float(np.max(shared)),
            "unique_horizon_native_bins": sorted(set(horizon.tolist())),
        }

        sums = np.asarray([
            float(r["openness_U"]) + float(r["closure_R"]) + float(r["handover_H"])
            for r in timeline
        ])
        std_sum = float(np.std(sums))
        med_sum = float(np.median(sums))
        coord = result["coordinate_independence"]
        coord_ok = close(std_sum, float(coord["std_U_plus_R_plus_H"])) and close(
            med_sum, float(coord["median_U_plus_R_plus_H"])
        )
        checks[f"{tag}_coordinate_recompute"] = {
            "pass": coord_ok and std_sum > 0.05,
            "std_recomputed": std_sum,
            "median_recomputed": med_sum,
        }

        event_formula_ok = True
        crossing_ok = True
        e2: list[float] = []
        e3: list[float] = []
        exposure: list[float] = []
        for row in events:
            u = float(row["crossing_U"])
            r = float(row["crossing_R"])
            h = float(row["crossing_H"])
            hm = float(row["history_median_H"])
            e2_calc = abs(2.0 - u - r)
            e3_calc = abs(2.0 - u - r - h)
            event_formula_ok &= close(e2_calc, float(row["E2"]))
            event_formula_ok &= close(e3_calc, float(row["E3_correct"]))
            event_formula_ok &= close(h - hm, float(row["H_exposure"]))
            crossing_ok &= close(u, r, 5e-8)
            e2.append(e2_calc)
            e3.append(e3_calc)
            exposure.append(h - hm)

        reported = result["crossings"]
        field_exposure = []
        for field in sorted({float(r["field_G"]) for r in events}):
            field_exposure.append(float(np.median([
                float(r["H_exposure"]) for r in events if float(r["field_G"]) == field
            ])))
        balanced_exposure = float(np.median(field_exposure))
        aggregate_ok = (
            len(events) == int(reported["event_count"])
            and close(float(np.median(e2)), float(reported["median_E2"]))
            and close(float(np.median(e3)), float(reported["median_E3_correct"]))
            and close(
                balanced_exposure,
                float(reported["effects"]["H_cross_minus_history"]["median"]),
            )
        )
        checks[f"{tag}_crossings"] = {
            "pass": event_formula_ok and crossing_ok and aggregate_ok,
            "event_count": len(events),
            "field_balanced_median_H_exposure": balanced_exposure,
            "median_E2": float(np.median(e2)),
            "median_E3": float(np.median(e3)),
        }

        prediction_ok = True
        pred_recomputed: dict[str, dict[str, float]] = {}
        for target in ("future_U", "future_R"):
            rows = [r for r in sequence_metrics if r["target"] == target]
            values = {}
            for output_key, source_key in (
                ("baseline_mse", "baseline_mse"),
                ("transfer_mse", "transfer_mse"),
                ("wrong_frequency_mse", "wrong_mse"),
            ):
                field_medians = []
                for field in sorted({float(r["field_G"]) for r in rows}):
                    field_medians.append(float(np.median([
                        float(r[source_key]) for r in rows if float(r["field_G"]) == field
                    ])))
                values[output_key] = float(np.median(field_medians))
            reported_errors = result["predictions"][target]["errors"]
            prediction_ok &= all(close(value, float(reported_errors[key])) for key, value in values.items())
            pred_recomputed[target] = values
        checks[f"{tag}_predictions"] = {
            "pass": prediction_ok,
            "recomputed": pred_recomputed,
        }

        stage_results[tag.lower()] = {
            "crossing_exposure_replicated": balanced_exposure > 0,
            "additive_closure_improved": float(np.median(np.asarray(e2) - np.asarray(e3))) > 0,
            "future_U_improved": (
                pred_recomputed["future_U"]["baseline_mse"]
                > pred_recomputed["future_U"]["transfer_mse"]
            ),
        }

    overall = all(bool(value["pass"]) for value in checks.values())
    conclusion = {
        "all_recomputations_pass": overall,
        "checks": checks,
        "stage_claims": stage_results,
        "auditor_interpretation": {
            "supported": "The independently derived lag-angle H is consistently elevated at exact U=R crossings.",
            "falsified_for_this_construction": "H is not a positive missing TE-ARA share under U+R+H=2 and does not add causal information for future openness.",
            "boundary": "The test concerns a detector-population spin relation, not an individual muon or neutrino event.",
        },
    }
    output = RESULTS / "T420_INDEPENDENT_VALIDATION.json"
    output.write_text(json.dumps(conclusion, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(conclusion, indent=2, sort_keys=True))
    if not overall:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
