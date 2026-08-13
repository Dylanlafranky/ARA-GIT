from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


SOURCE = Path(__file__).with_name("T362_SOURCE_Acosta_2019_Figure1Data.xlsx")

for sheet in ("Fig1a", "Fig1d"):
    df = pd.read_excel(SOURCE, sheet_name=sheet, header=None)
    displacement = pd.to_numeric(df.iloc[:, 0], errors="coerce").to_numpy(float)
    stress = pd.to_numeric(df.iloc[:, 1], errors="coerce").to_numpy(float)
    valid = np.isfinite(stress) & np.isfinite(displacement)
    stress = stress[valid]
    displacement = displacement[valid]
    drop = -np.diff(stress)
    for threshold in (1, 2, 5, 10):
        candidates = np.flatnonzero(drop >= threshold)
        peaks = []
        for candidate in candidates:
            if not peaks or candidate - peaks[-1] >= 1000:
                peaks.append(int(candidate))
            elif drop[candidate] > drop[peaks[-1]]:
                peaks[-1] = int(candidate)
        print(sheet, "threshold", threshold, "n", len(peaks))
        print([(int(p + 1), float(displacement[p]), float(displacement[p+1]), float(drop[p]), float(stress[p]), float(stress[p + 1])) for p in peaks])
