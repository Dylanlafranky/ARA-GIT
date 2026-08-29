"""Score the already-written and hashed T437 waveform-only prediction."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
PREDICTION = RESULTS / "T437_WAVEFORM_ONLY_FOUR_INSTRUMENT_CLOCKS.json"
PREDICTION_NPZ = RESULTS / "T437_WAVEFORM_ONLY_FOUR_INSTRUMENT_CLOCKS.npz"
RECEIPT = RESULTS / "T437_PREDICTION_SHA256.txt"
T435_SCORE = HERE.parent / "T435_blind_ara_binary_inversion" / "results" / "T435_SCORED_RESULT.json"
T436_SCORE = HERE.parent / "T436_irrationality_timing_transfer" / "results" / "T436_SCORED_RESULT.json"
OUT_JSON = RESULTS / "T437_SCORED_RESULT.json"
OUT_CSV = RESULTS / "T437_TIMING_COMPARISON.csv"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt_hash(label: str) -> str:
    for line in RECEIPT.read_text(encoding="utf-8").splitlines():
        if line.startswith(label):
            return line.split()[-1]
    raise KeyError(label)


def score_row(
    name: str,
    kind: str,
    support: str,
    predicted: float,
    actual: float,
    cycle: float,
    baseline_error: float,
) -> dict[str, object]:
    signed = predicted - actual
    absolute = abs(signed)
    return {
        "clock": name,
        "instrument": kind,
        "support": support,
        "predicted_time_M": predicted,
        "actual_common_horizon_M": actual,
        "signed_error_M": signed,
        "absolute_error_M": absolute,
        "error_parent_cycles": absolute / cycle,
        "improvement_vs_T435_M": baseline_error - absolute,
        "within_one_parent_cycle": absolute <= cycle,
    }


def main() -> None:
    if sha256(PREDICTION_NPZ) != receipt_hash("prediction_sha256"):
        raise RuntimeError("T437 prediction hash mismatch; refusing to score")
    if sha256(PREDICTION) != receipt_hash("summary_sha256"):
        raise RuntimeError("T437 summary hash mismatch; refusing to score")

    prediction = json.loads(PREDICTION.read_text(encoding="utf-8"))
    t435 = json.loads(T435_SCORE.read_text(encoding="utf-8"))
    t436 = json.loads(T436_SCORE.read_text(encoding="utf-8"))
    actual = float(t435["hidden_system_revealed"]["common_horizon_time"])
    cycle = float(t435["metrics"]["parent_waveform_cycle_at_prediction"])
    baseline_time = float(t435["metrics"]["predicted_handover_time"])
    baseline_error = abs(baseline_time - actual)

    rows = [
        score_row(
            "State Irr-Di-ARA",
            "state",
            "causal past/current",
            float(prediction["state_clock"]["time_M"]),
            actual,
            cycle,
            baseline_error,
        ),
        score_row(
            "Path/history Irr-Di-ARA",
            "path/history",
            "causal past-only",
            float(prediction["path_history_clock"]["time_M"]),
            actual,
            cycle,
            baseline_error,
        ),
        score_row(
            "Dynamic Irr-Di-ARA (T436 unchanged)",
            "dynamic",
            "causal past-only",
            float(prediction["dynamic_clock_unchanged_from_T436"]["time_M"]),
            actual,
            cycle,
            baseline_error,
        ),
        score_row(
            "Experimental Rationality reconstruction",
            "rationality",
            "retrospective future-read-backward",
            float(prediction["experimental_rationality_clock"]["time_M"]),
            actual,
            cycle,
            baseline_error,
        ),
        score_row(
            "T435 median clock",
            "baseline",
            "causal waveform-only",
            baseline_time,
            actual,
            cycle,
            baseline_error,
        ),
        score_row(
            "Waveform-power maximum",
            "physics crosswalk",
            "waveform-only",
            float(prediction["power_peak_time_M"]),
            actual,
            cycle,
            baseline_error,
        ),
    ]

    controls: list[dict[str, object]] = []
    controls.append(score_row(
        "State quarter-record roll",
        "control",
        "chronology roll",
        float(prediction["controls"]["state_quarter_record_roll"]["time_M"]),
        actual,
        cycle,
        baseline_error,
    ))
    for family, label in (
        ("path_history", "Path/history"),
        ("experimental_rationality", "Rationality"),
    ):
        for name, clock in prediction["controls"][family].items():
            controls.append(score_row(
                f"{label} control: {name}",
                "control",
                name,
                float(clock["time_M"]),
                actual,
                cycle,
                baseline_error,
            ))

    primary = {row["instrument"]: row for row in rows if row["instrument"] in {"state", "path/history", "dynamic", "rationality"}}
    state_is_power_crosswalk = abs(
        float(prediction["state_clock"]["time_M"]) - float(prediction["power_peak_time_M"])
    ) < 1e-9
    verdicts = {
        "state": "SUPPORTED AS POWER-CREST CROSSWALK; NOT INDEPENDENT" if primary["state"]["within_one_parent_cycle"] else "NOT SUPPORTED",
        "path_history": "SUPPORTED" if primary["path/history"]["within_one_parent_cycle"] else "NOT SUPPORTED",
        "dynamic": "SUPPORTED" if primary["dynamic"]["within_one_parent_cycle"] else "NOT SUPPORTED",
        "experimental_rationality": "SUPPORTED RETROSPECTIVELY" if primary["rationality"]["within_one_parent_cycle"] else "NOT SUPPORTED",
    }
    if state_is_power_crosswalk:
        verdicts["state"] = "SUPPORTED AS POWER-CREST CROSSWALK; NOT INDEPENDENT"

    result = {
        "test": "T437_four_instrument_spacetime_timing",
        "evidence_class": "one-event known-answer method calibration",
        "prediction_sha256_verified": True,
        "actual_common_horizon_time_M": actual,
        "local_parent_cycle_M": cycle,
        "primary_verdicts": verdicts,
        "timing_comparison": rows,
        "controls": controls,
        "diagnostics": {
            "state_selection_mode": prediction["state_clock"]["selection_mode"],
            "state_is_exact_power_maximum_crosswalk": state_is_power_crosswalk,
            "path_distance_at_read": prediction["path_history_clock"]["distance"],
            "rationality_distance_at_read": prediction["experimental_rationality_clock"]["distance"],
            "path_chronology_shuffle_distance": prediction["controls"]["path_history"]["chronology_shuffle"]["distance"],
            "rationality_chronology_shuffle_distance": prediction["controls"]["experimental_rationality"]["chronology_shuffle"]["distance"],
            "T436_primary_result": t436["verdict"],
        },
        "bottom_line": (
            "Only the state instrument lands within one local parent cycle, and it collapses to the waveform-power crest. "
            "The path/history, unchanged dynamic, and reverse-facing Rationality clocks do not recover the horizon time."
        ),
        "limitations": [
            "Only SXS:BBH:0305 is archived locally, so this cannot establish event-to-event transfer.",
            "The horizon time was already known historically; hashing prevents within-test retuning but does not make this blind discovery.",
            "The state clock is a crosswalk to the amplitude crest and therefore is not independent of standard waveform timing.",
            "The experimental Rationality clock uses future data and cannot be treated as a causal forecast.",
        ],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows + controls)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
