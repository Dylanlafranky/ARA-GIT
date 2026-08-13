"""Independent artifact validation for T361B."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PREFIX = HERE / "T361B_LOCAL_RECORD_VS_FREE_RESTORATION"
ROWS = Path(f"{PREFIX}_PAIR_ROWS.csv")
SUMMARY = Path(f"{PREFIX}_RECORD_SUMMARY.csv")
RESULTS = Path(f"{PREFIX}_RESULTS.json")
FIGURE = Path(f"{PREFIX}_FIGURE.png")
PROTOCOL = HERE / "T361B_LOCAL_RECORD_VS_FREE_RESTORATION_PROTOCOL_v1_FROZEN.md"
OUT = Path(f"{PREFIX}_VALIDATION.json")


def main() -> None:
    rows = pd.read_csv(ROWS)
    summary = pd.read_csv(SUMMARY)
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    checks = []
    def add(name, value, detail): checks.append({"check": name, "passed": bool(value), "detail": detail})
    actual_hash = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    add("protocol hash", actual_hash == "0518524db13524a597886b77ac34d7235878e3deb5d19567f3cceb5e6e9e9802", actual_hash)
    add("nine records", rows.delta_r.nunique() == 9, str(sorted(rows.delta_r.unique())))
    add("40 pairs", bool((rows.groupby("delta_r").pair.nunique() == 40).all()), str(rows.groupby("delta_r").pair.nunique().to_dict()))
    add("three methods", bool((rows.groupby(["delta_r", "pair"]).method.nunique() == 3).all()), "all pair groups")
    calc = rows.groupby(["delta_r", "method"], as_index=False)[["delta_RMSE_ARA", "next_position_RMSE_ARA", "direction_agreement"]].median()
    merged = calc.merge(summary, on=["delta_r", "method"], suffixes=("_calc", "_stored"))
    cols = ["delta_RMSE_ARA", "next_position_RMSE_ARA", "direction_agreement"]
    add("record medians", all(np.allclose(merged[f"{c}_calc"], merged[f"{c}_stored"], atol=1e-12) for c in cols), "recomputed from pair rows")
    p = calc[calc.method == "primary"]
    precise = p[(p.next_position_RMSE_ARA <= .10) & (p.direction_agreement >= .75)]
    add("locally precise count", len(precise) == int(result["locally_precise_records"]), f"recomputed={len(precise)}")
    add("all nine locally precise", len(precise) == 9, str(precise.delta_r.astype(int).tolist()))
    add("figure", FIGURE.exists() and FIGURE.stat().st_size > 100_000, f"bytes={FIGURE.stat().st_size if FIGURE.exists() else 0}")
    output = {"validation_passed": all(x["passed"] for x in checks), "checks": checks}
    OUT.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__": main()

