"""Independent reproducibility checks for T365."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
STEM = "T365_FAULT_TENSION_SCALE_LADDER_FORECAST"
RUNGS = [(-2, 3, 13), (-1, 5, 25), (0, 10, 50), (1, 20, 100), (2, 40, 200)]


def trailing(values: np.ndarray, width: int, summed: bool = False) -> np.ndarray:
    total = np.cumsum(np.insert(values, 0, 0.0))
    index = np.arange(len(values))
    start = np.maximum(0, index - width + 1)
    result = total[index + 1] - total[start]
    return result if summed else result / (index - start + 1)


def coordinates(stress: np.ndarray, smooth_width: int, transfer_width: int, q05: float, q95: float):
    smooth = trailing(stress, smooth_width)
    delta = np.diff(smooth, prepend=smooth[0])
    a = trailing(np.maximum(delta, 0), transfer_width, True)
    r = trailing(np.maximum(-delta, 0), transfer_width, True)
    xf = np.divide(2 * r, a + r, out=np.ones_like(r), where=(a + r) > 1e-15)
    xs = np.clip(2 * (smooth - q05) / (q95 - q05), 0, 2)
    active = (xs >= 1) & (xf >= 1)
    u, v = 2 * (xs - 1), 2 * (xf - 1)
    h = np.divide(2 * v, u + v, out=np.full_like(v, np.nan), where=active & ((u + v) > 1e-15))
    return xs, xf, active, h


def alarms(ladder: dict[int, tuple[np.ndarray, ...]]) -> np.ndarray:
    xsg, xfg, ag, hg = ladder[-2]
    xsc, xfc, ac, hc = ladder[-1]
    _, _, a0, h0 = ladder[0]
    child_cross = np.zeros(len(hc), bool)
    child_cross[1:] = ac[1:] & ac[:-1] & (hc[:-1] < 0.5) & (hc[1:] >= 0.5)
    gg, gc = np.abs(xsg - xfg), np.abs(xsc - xfc)
    close_g, close_c = np.zeros(len(hc), bool), np.zeros(len(hc), bool)
    close_g[3:] = gg[3:] < gg[:-3]
    close_c[5:] = gc[5:] < gc[:-5]
    return np.flatnonzero(ag & ac & (hg >= 0.5) & child_cross & ((~a0) | (~np.isfinite(h0)) | (h0 < 1)) & close_g & close_c)


def upward(active: np.ndarray, h: np.ndarray, level: float) -> np.ndarray:
    valid = active[1:] & active[:-1] & np.isfinite(h[1:]) & np.isfinite(h[:-1])
    return np.flatnonzero(valid & (h[:-1] < level) & (h[1:] >= level)) + 1


def main() -> None:
    result = json.loads((HERE / f"{STEM}_RESULTS.json").read_text(encoding="utf-8"))
    checks = []

    raw = np.load(HERE / "T362_SOURCE_EVENT101_QA_2MS.npz")
    stress, time, disp = raw["stress_mean"].astype(float), raw["time"].astype(float), raw["disp_mean"].astype(float)
    split = int(0.8 * len(stress))
    marker = int(np.argmax(np.diff(disp, append=disp[-1]))) + 1
    ladder = {}
    for rung, smooth_width, transfer_width in RUNGS:
        smooth = trailing(stress, smooth_width)
        q05, q95 = np.quantile(smooth[:split], [0.05, 0.95])
        ladder[rung] = coordinates(stress, smooth_width, transfer_width, q05, q95)
    dense_alarm = alarms(ladder)
    holdout = dense_alarm[dense_alarm >= split]
    checks.append(("dense independent slip index", marker == result["dense"]["slip_index"], f"{marker}"))
    checks.append(("dense independent alarm", len(holdout) == 1 and int(holdout[0]) == result["dense"]["alarm_index"], str(holdout.tolist())))
    lead_ms = float((time[marker] - time[holdout[0]]) * 1000)
    checks.append(("dense independent lead", abs(lead_ms - 14.0) < 1e-6, f"{lead_ms:.9f} ms"))

    expected_leads = {(-2, .5): 16, (-1, .5): 14, (0, 1.0): -2, (1, 1.0): -10, (2, 1.0): -24}
    observed_leads = []
    for (rung, level), expected in expected_leads.items():
        _, _, active, h = ladder[rung]
        cross = upward(active, h, level)
        local = cross[np.abs(cross - marker) <= 250]
        chosen = int(local[np.argmin(np.abs(local - marker))])
        lead = float((time[marker] - time[chosen]) * 1000)
        observed_leads.append(lead)
        checks.append((f"independent landmark r{rung} h{level}", abs(lead - expected) < 1e-6, f"{lead:.6f} ms"))

    protocol_hash = hashlib.sha256((HERE / "T365_FAULT_TENSION_SCALE_LADDER_FORECAST_PROTOCOL_v1_FROZEN.md").read_bytes()).hexdigest().upper()
    checks.append(("frozen protocol hash", protocol_hash == result["dense"]["protocol_sha256"], protocol_hash))

    events = pd.read_csv(HERE / f"{STEM}_REPLICATION_EVENTS.csv")
    checks.append(("replication rows", len(events) == 15, str(len(events))))
    checks.append(("replication order count", int(events.grandchild_no_later_than_current.sum()) == 5, str(int(events.grandchild_no_later_than_current.sum()))))
    checks.append(("replication alarm count", int(events.forecast_contains_drop.sum()) == 3, str(int(events.forecast_contains_drop.sum()))))
    checks.append(("fluid/dry split", int(events.query("medium == 'fluid'").forecast_contains_drop.sum()) == 3 and int(events.query("medium == 'dry'").forecast_contains_drop.sum()) == 0, "fluid=3/5; dry=0/10"))

    gates = pd.read_csv(HERE / f"{STEM}_FROZEN_GATES.csv")
    checks.append(("frozen gate verdict retained", int(gates.passed.sum()) == 6 and not result["all_gates_passed"], f"{int(gates.passed.sum())}/7 pass; overall={result['all_gates_passed']}"))
    address = pd.read_csv(HERE / f"{STEM}_IRRATIONALITY_ADDRESS.csv")
    checks.append(("five finite Irrationality addresses", len(address) == 5 and np.isfinite(address[["x_P", "x_R", "history_coherence_mean"]].to_numpy()).all(), str(len(address))))
    required = [HERE / f"{STEM}_FIGURE.png", HERE / f"{STEM}_REPORT_2026-08-12.md", HERE / f"{STEM}_DENSE_TIMESERIES.csv"]
    checks.append(("required artifacts", all(path.exists() and path.stat().st_size > 0 for path in required), "; ".join(path.name for path in required)))

    frame = pd.DataFrame(checks, columns=["check", "passed", "observed"])
    frame.to_csv(HERE / f"{STEM}_VALIDATION.csv", index=False)
    verdict = bool(frame.passed.all())
    (HERE / f"{STEM}_VALIDATION.md").write_text(
        "# T365 independent validation\n\n" +
        f"**Result:** {'PASS' if verdict else 'FAIL'} ({int(frame.passed.sum())}/{len(frame)})\n\n" +
        "| check | passed | observed |\n|---|---:|---|\n" +
        "\n".join(f"| {row.check} | {row.passed} | {row.observed} |" for row in frame.itertuples(index=False)) + "\n",
        encoding="utf-8",
    )
    print(frame.to_string(index=False))
    print(f"VALIDATION={'PASS' if verdict else 'FAIL'} ({int(frame.passed.sum())}/{len(frame)})")


if __name__ == "__main__":
    main()
