from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


SOURCE = Path(__file__).with_name("T362_SOURCE_Acosta_2019_Figure1Data.xlsx")


def describe_sheet(name: str) -> None:
    df = pd.read_excel(SOURCE, sheet_name=name, header=None)
    print(f"\n=== {name}: shape={df.shape} ===")
    for column in df.columns:
        values = pd.to_numeric(df[column], errors="coerce").dropna().to_numpy(dtype=float)
        if len(values) == 0:
            print(f"col {column}: empty")
            continue
        delta = np.diff(values)
        print(
            f"col {column}: n={len(values)} min={np.min(values):.9g} "
            f"q01={np.quantile(values, .01):.9g} median={np.median(values):.9g} "
            f"q99={np.quantile(values, .99):.9g} max={np.max(values):.9g} "
            f"first={values[:5].tolist()} last={values[-5:].tolist()}"
        )
        if len(delta):
            print(
                f"  delta: min={np.min(delta):.9g} q01={np.quantile(delta, .01):.9g} "
                f"median={np.median(delta):.9g} q99={np.quantile(delta, .99):.9g} "
                f"max={np.max(delta):.9g} negative_share={np.mean(delta < 0):.6f}"
            )


for sheet in ("Fig1a", "Fig1b", "Fig1c", "Fig1d", "Fig1e", "Fig1f"):
    describe_sheet(sheet)
