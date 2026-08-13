"""Extract the frozen T363 stress-drop event windows without scoring them."""

from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "T362_SOURCE_Acosta_2019_Figure1Data.xlsx"
OUTPUT = HERE / "T363_SOURCE_ACOSTA_STRESS_EVENTS_15.csv"
META = HERE / "T363_SOURCE_ACOSTA_STRESS_EVENTS_META.csv"
SCALES = HERE / "T363_SOURCE_ACOSTA_STRESS_MEDIUM_SCALES.csv"


def trailing_mean(values: np.ndarray, width: int) -> np.ndarray:
    total = np.cumsum(np.insert(values, 0, 0.0))
    starts = np.maximum(0, np.arange(len(values)) - width + 1)
    counts = np.arange(len(values)) - starts + 1
    return (total[np.arange(1, len(values) + 1)] - total[starts]) / counts


def extract(sheet: str, medium: str) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    raw = pd.read_excel(SOURCE, sheet_name=sheet, header=None)
    position = pd.to_numeric(raw.iloc[:, 0], errors="coerce").to_numpy(float)
    stress = pd.to_numeric(raw.iloc[:, 1], errors="coerce").to_numpy(float)
    valid = np.isfinite(position) & np.isfinite(stress)
    position, stress = position[valid], stress[valid]
    instantaneous_fall = -np.diff(stress)
    candidates = np.flatnonzero(instantaneous_fall >= 5.0)
    events: list[int] = []
    for candidate in candidates:
        if not events or candidate - events[-1] >= 1000:
            events.append(int(candidate))
        elif instantaneous_fall[candidate] > instantaneous_fall[events[-1]]:
            events[-1] = int(candidate)

    event_rows = []
    meta_rows = []
    for number, drop_before in enumerate(events, start=1):
        drop_after = drop_before + 1
        start, stop = drop_after - 2048, drop_after + 513
        if start < 0 or stop > len(stress):
            raise ValueError(f"event {medium} {number} lacks frozen window")
        frame = pd.DataFrame(
            {
                "medium": medium,
                "event": number,
                "relative_row": np.arange(-2048, 513),
                "source_row": np.arange(start, stop),
                "source_position": position[start:stop],
                "stress_mpa": stress[start:stop],
            }
        )
        event_rows.append(frame)
        meta_rows.append(
            {
                "medium": medium,
                "event": number,
                "drop_source_row": drop_after,
                "drop_position_before": position[drop_before],
                "drop_position_after": position[drop_after],
                "stress_before_mpa": stress[drop_before],
                "stress_after_mpa": stress[drop_after],
                "instantaneous_fall_mpa": instantaneous_fall[drop_before],
            }
        )
    smoothed = trailing_mean(stress, 31)
    q05, q95 = np.quantile(smoothed, [0.05, 0.95])
    scale = {
        "medium": medium,
        "source_rows": len(stress),
        "smoothing_rows": 31,
        "smoothed_stress_q05_mpa": float(q05),
        "smoothed_stress_q95_mpa": float(q95),
    }
    return pd.concat(event_rows, ignore_index=True), pd.DataFrame(meta_rows), scale


def main() -> None:
    dry, dry_meta, dry_scale = extract("Fig1a", "dry")
    fluid, fluid_meta, fluid_scale = extract("Fig1d", "fluid")
    events = pd.concat([dry, fluid], ignore_index=True)
    meta = pd.concat([dry_meta, fluid_meta], ignore_index=True)
    events.to_csv(OUTPUT, index=False)
    meta.to_csv(META, index=False)
    pd.DataFrame([dry_scale, fluid_scale]).to_csv(SCALES, index=False)
    print(f"wrote {len(events):,} rows for {len(meta)} events")
    print(meta.to_string(index=False))


if __name__ == "__main__":
    main()
