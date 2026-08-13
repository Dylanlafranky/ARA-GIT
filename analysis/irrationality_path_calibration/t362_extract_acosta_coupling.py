"""Extract the 15 published Acosta et al. coupling histories from the source XLSX.

This is deliberately a source-conversion step only.  It performs no scoring and
does not know the T362 gates.
"""

from pathlib import Path

import pandas as pd


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "T362_SOURCE_Acosta_2019_Figure1Data.xlsx"
OUTPUT = HERE / "T362_SOURCE_ACOSTA_COUPLING_15.csv"


def extract(sheet: str, medium: str) -> pd.DataFrame:
    raw = pd.read_excel(SOURCE, sheet_name=sheet, header=None)
    time = pd.to_numeric(raw.iloc[:, 0], errors="coerce")
    frames = []
    for column in range(1, raw.shape[1]):
        frame = pd.DataFrame(
            {
                "time_to_mainshock_s": time,
                "medium": medium,
                "event": column,
                "coupling": pd.to_numeric(raw.iloc[:, column], errors="coerce"),
            }
        ).dropna()
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def main() -> None:
    output = pd.concat(
        [extract("Fig1c", "dry"), extract("Fig1f", "fluid")],
        ignore_index=True,
    )
    output.to_csv(OUTPUT, index=False)
    print(f"wrote {OUTPUT.name}: {len(output):,} rows, "
          f"{output[['medium', 'event']].drop_duplicates().shape[0]} histories")


if __name__ == "__main__":
    main()
