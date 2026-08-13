"""Extract T365 fixed rung scales from the complete Acosta medium records."""

from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "T362_SOURCE_AcOSTA_2019_Figure1Data.xlsx"
if not SOURCE.exists():
    SOURCE = HERE / "T362_SOURCE_Acosta_2019_Figure1Data.xlsx"
OUTPUT = HERE / "T365_SOURCE_ACOSTA_TENSION_SCALE_LADDER.csv"
RUNGS = [(-2, 3, 13), (-1, 5, 25), (0, 10, 50), (1, 20, 100), (2, 40, 200)]


def trailing_mean(values: np.ndarray, width: int) -> np.ndarray:
    total = np.cumsum(np.insert(values, 0, 0.0))
    index = np.arange(len(values))
    start = np.maximum(0, index - width + 1)
    return (total[index + 1] - total[start]) / (index - start + 1)


def main() -> None:
    rows = []
    for medium, sheet in [("dry", "Fig1a"), ("fluid", "Fig1d")]:
        raw = pd.read_excel(SOURCE, sheet_name=sheet, header=None)
        stress = pd.to_numeric(raw.iloc[:, 1], errors="coerce").dropna().to_numpy(float)
        for rung, smooth_width, transfer_width in RUNGS:
            smooth = trailing_mean(stress, smooth_width)
            q05, q95 = np.quantile(smooth, [0.05, 0.95])
            rows.append(
                {
                    "medium": medium,
                    "rung": rung,
                    "source_rows": len(stress),
                    "smooth_width": smooth_width,
                    "transfer_width": transfer_width,
                    "smoothed_stress_q05_mpa": float(q05),
                    "smoothed_stress_q95_mpa": float(q95),
                }
            )
    pd.DataFrame(rows).to_csv(OUTPUT, index=False)
    print(f"wrote {OUTPUT.name}")


if __name__ == "__main__":
    main()

