"""Descriptive ENSO rare-leaf refinement: cycle spacing and temporal shape loss.

Hypothesis:

    routine shedding happens frequently
    larger drops may occur after one full cycle or a three-cycle recurrence
    a larger drop may be visible when the current cycle loses temporal shape

This is a raw descriptive diagnostic, not a predictor. The visible leaf marker
still uses the existing strict-causal brown/green harmonic reader. To avoid
testing that marker only against its own assumptions, temporal shape loss is
measured separately from raw NINO:

    loss(period, width, t)
        = 1 - corr(raw recent segment, raw segment period months earlier)

No smoothing, FFT, Hilbert phase, synthetic packet, or formula modification is
used. The sample is small, so all correlations are exploratory.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import ara_enso_causal_leaf_fall_ablation as leaf
import ara_enso_leaf_to_wwv_abnormality_test as soil
import ara_enso_two_flow_window_test as two_flow
import ara_joint_enso_topology_direction_test as joint
import ara_unified_layered_framework_test as base


HERE = Path(__file__).resolve().parent
OUT = HERE / "ara_enso_large_leaf_shape_loss_result.json"

BROWN_PERIOD = 48
THREE_CYCLE_PERIOD = 3 * BROWN_PERIOD
SHAPE_WIDTHS = (6, 12, 18, 24)
SOIL_WINDOW = tuple(range(30, 35))


def raw_shape_loss(values: np.ndarray, month: int, period: int, width: int) -> float:
    if month - period - width < 0:
        return float("nan")
    current = values[month - width : month]
    previous = values[month - period - width : month - period]
    corr = soil.correlation(current, previous)
    return float(1.0 - corr)


def leaf_peaks(marker: np.ndarray) -> list[int]:
    return [
        month
        for month in range(leaf.MIN_HISTORY + 1, len(marker) - 1)
        if marker[month] > 0.0
        and marker[month] >= marker[month - 1]
        and marker[month] > marker[month + 1]
    ]


def future_soil_mean(values: np.ndarray, month: int) -> float:
    indices = [month + delay for delay in SOIL_WINDOW if month + delay < len(values)]
    return float(np.mean(values[indices])) if indices else float("nan")


def safe_corr(left: list[float], right: list[float]) -> float:
    return soil.correlation(np.asarray(left, dtype=float), np.asarray(right, dtype=float))


def correlation_panel(events: list[dict], period: int) -> dict:
    completed = [
        event for event in events if np.isfinite(event["future_soil_battery_abnormality"])
    ]
    rows = {}
    for width in SHAPE_WIDTHS:
        key = f"{period}m_width_{width}m"
        usable = [
            event
            for event in completed
            if np.isfinite(event["raw_shape_loss"][str(period)][str(width)])
        ]
        losses = [event["raw_shape_loss"][str(period)][str(width)] for event in usable]
        rows[key] = {
            "n": int(len(usable)),
            "shape_loss_to_visible_leaf_size_corr": safe_corr(
                losses, [event["leaf_marker_size"] for event in usable]
            ),
            "shape_loss_to_future_soil_dump_corr": safe_corr(
                losses,
                [event["future_soil_battery_abnormality"] for event in usable],
            ),
        }
    return rows


def main() -> None:
    nodes = joint.build_nodes()
    keys = two_flow.aligned_keys()
    n = len(keys)
    cutoff = int(n * 0.60)
    nino = base.standardize_from_training(nodes[0].values, cutoff)
    marker = np.asarray(leaf.causal_leaf_state(nino)["leaf"], dtype=float)
    battery_abnormality = soil.build_abnormalities(nodes, cutoff)[0][
        "battery_abnormality"
    ]

    peaks = leaf_peaks(marker)
    events = []
    for index, month in enumerate(peaks):
        events.append(
            {
                "month_index": month,
                "month": keys[month],
                "split": "train" if month < cutoff else "heldout",
                "leaf_marker_size": float(marker[month]),
                "months_since_previous_leaf_peak": None
                if index == 0
                else int(month - peaks[index - 1]),
                "future_soil_battery_abnormality": future_soil_mean(
                    battery_abnormality, month
                ),
                "raw_shape_loss": {
                    str(period): {
                        str(width): raw_shape_loss(nino, month, period, width)
                        for width in SHAPE_WIDTHS
                    }
                    for period in (BROWN_PERIOD, THREE_CYCLE_PERIOD)
                },
            }
        )

    gaps = np.diff(peaks)
    completed = [
        event for event in events if np.isfinite(event["future_soil_battery_abnormality"])
    ]
    result = {
        "test": "descriptive ENSO leaf-peak spacing and raw temporal-shape-loss diagnostic",
        "status": "exploratory; too few leaf peaks for a validated rare-event law",
        "strict_causal_checklist": {
            "leaf_marker": "existing causal brown/green reader using NINO at or before each month",
            "shape_loss": "raw recent NINO segment compared with an earlier raw segment only",
            "soil_outcome": "future measured WWV abnormality used only as scored outcome",
            "smoothing": False,
            "fft_or_hilbert": False,
            "synthetic_energy_injection": False,
            "formula_modified": False,
        },
        "interpretation_limits": {
            "one_cycle_spacing_independent_proof": False,
            "reason": "the causal marker contains a declared 48-month brown geometry",
            "three_cycle_law_testable_with_current_event_count": False,
            "completed_soil_outcome_event_n": int(len(completed)),
        },
        "constants": {
            "declared_brown_period_months": BROWN_PERIOD,
            "three_cycle_period_months": THREE_CYCLE_PERIOD,
            "shape_widths_months": list(SHAPE_WIDTHS),
            "future_soil_window_months": list(SOIL_WINDOW),
        },
        "leaf_peak_spacing": {
            "event_n": int(len(events)),
            "train_event_n": int(sum(event["split"] == "train" for event in events)),
            "heldout_event_n": int(sum(event["split"] == "heldout" for event in events)),
            "gaps_months": [int(value) for value in gaps],
            "mean_gap_months": float(np.mean(gaps)),
            "std_gap_months": float(np.std(gaps)),
        },
        "one_cycle_raw_shape_loss_panel": correlation_panel(events, BROWN_PERIOD),
        "three_cycle_raw_shape_loss_panel": correlation_panel(
            events, THREE_CYCLE_PERIOD
        ),
        "leaf_size_to_future_soil_dump_corr": safe_corr(
            [event["leaf_marker_size"] for event in completed],
            [event["future_soil_battery_abnormality"] for event in completed],
        ),
        "events": events,
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("strict causal checklist")
    print(json.dumps(result["strict_causal_checklist"], indent=2))
    print()
    spacing = result["leaf_peak_spacing"]
    print(
        "leaf peak spacing",
        f"n={spacing['event_n']}",
        f"gaps={spacing['gaps_months']}",
        f"mean={spacing['mean_gap_months']:.1f}",
        f"std={spacing['std_gap_months']:.1f}",
    )
    print()
    print("events")
    for event in events:
        loss_one = event["raw_shape_loss"][str(BROWN_PERIOD)]["18"]
        loss_three = event["raw_shape_loss"][str(THREE_CYCLE_PERIOD)]["18"]
        print(
            " ",
            event["month"],
            f"leaf={event['leaf_marker_size']:.4f}",
            f"gap={event['months_since_previous_leaf_peak']}",
            f"soil={event['future_soil_battery_abnormality']:.3f}"
            if np.isfinite(event["future_soil_battery_abnormality"])
            else "soil=not-yet-observed",
            f"loss1={loss_one:.3f}",
            f"loss3={loss_three:.3f}",
        )
    print()
    print("one-cycle shape-loss panel")
    for name, row in result["one_cycle_raw_shape_loss_panel"].items():
        print(
            " ",
            name,
            f"n={row['n']}",
            f"loss->leaf={row['shape_loss_to_visible_leaf_size_corr']:+.3f}",
            f"loss->soil={row['shape_loss_to_future_soil_dump_corr']:+.3f}",
        )
    print("three-cycle shape-loss panel")
    for name, row in result["three_cycle_raw_shape_loss_panel"].items():
        print(
            " ",
            name,
            f"n={row['n']}",
            f"loss->leaf={row['shape_loss_to_visible_leaf_size_corr']:+.3f}",
            f"loss->soil={row['shape_loss_to_future_soil_dump_corr']:+.3f}",
        )


if __name__ == "__main__":
    main()
