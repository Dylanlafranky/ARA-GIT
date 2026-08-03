#!/usr/bin/env python3
"""Independent checks for the frozen T338 ENSO transport result."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "T338_ENSO_THREE_TIER_TRANSPORT_RESULTS.json"
COORDINATES = HERE / "T338_ENSO_THREE_TIER_TRANSPORT_COORDINATES.csv"
PROTOCOL = HERE / "T338_ENSO_THREE_TIER_TRANSPORT_PROTOCOL_v1_FROZEN.md"
OUTPUT = HERE / "T338_ENSO_THREE_TIER_TRANSPORT_VALIDATION.json"
HOLD_START = pd.Timestamp("2005-01-01")
HOLD_END = pd.Timestamp("2025-12-01")
TOL = 1e-10


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bacc(driver: np.ndarray, target: np.ndarray) -> tuple[float, float, float, int]:
    valid = np.isfinite(driver) & np.isfinite(target) & (driver != 0) & (target != 0)
    d = np.sign(driver[valid])
    y = np.sign(target[valid])
    positive = y > 0
    negative = y < 0
    recall_positive = float(np.mean(d[positive] > 0))
    recall_negative = float(np.mean(d[negative] < 0))
    return (
        float((recall_positive + recall_negative) / 2),
        recall_positive,
        recall_negative,
        int(valid.sum()),
    )


def spearman(driver: np.ndarray, target: np.ndarray) -> float:
    valid = np.isfinite(driver) & np.isfinite(target)
    x = pd.Series(driver[valid]).rank(method="average").to_numpy()
    y = pd.Series(target[valid]).rank(method="average").to_numpy()
    return float(np.corrcoef(x, y)[0, 1])


def recompute(df: pd.DataFrame, driver: str, state: str, lead: int) -> dict:
    target = df[state].shift(-lead) - df[state]
    mask = (
        (df.index >= HOLD_START)
        & (df.index <= HOLD_END)
        & (df.index + pd.offsets.MonthBegin(lead) <= HOLD_END)
        & df[driver].notna()
        & target.notna()
    )
    d = df.loc[mask, driver].to_numpy(dtype=float)
    y = target.loc[mask].to_numpy(dtype=float)
    score, recall_el, recall_la, n = bacc(d, y)
    return {
        "bacc": score,
        "recall_el_nino_direction": recall_el,
        "recall_la_nina_direction": recall_la,
        "spearman": spearman(d, y),
        "n": n,
    }


def close(a: float, b: float) -> bool:
    return math.isfinite(a) and math.isfinite(b) and abs(a - b) <= TOL


def main() -> None:
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    df = pd.read_csv(
        COORDINATES, parse_dates=["date"], float_precision="round_trip"
    ).set_index("date")
    exported_parent_ara = df["ara_parent"].copy()

    scales = results["development_scales"]
    # Rebuild every tested coordinate from exported raw observations. This
    # avoids rank-tie changes caused by subtracting already-normalized CSV
    # values, while remaining independent of the scoring runner.
    df["ocean_state"] = df["nino34_raw"] / scales["nino34"]
    df["atmos_state"] = -df["soi_raw"] / scales["soi"]
    df["atmos_state_olr"] = -df["olr_raw"] / scales["olr"]
    redistribution = df["wwv_east_raw"] - df["wwv_west_raw"]
    df["ocean_flow"] = redistribution.diff() / scales["wwv_redistribution_change"]
    for region in ["w", "c", "e"]:
        df[f"atmos_flow_{region}"] = -df[f"wind_{region}_raw"] / scales[f"wind_{region}"]
    df["heat_flow"] = df["heat_raw"].diff() / results["development_scales"]["heat_change"]

    df["la_ocean"] = (-df["ocean_state"]).clip(lower=0)
    df["la_atmos"] = (-df["atmos_state"]).clip(lower=0)
    df["el_ocean"] = df["ocean_state"].clip(lower=0)
    df["el_atmos"] = df["atmos_state"].clip(lower=0)
    la_rebuilt = df["la_ocean"] + df["la_atmos"]
    el_rebuilt = df["el_ocean"] + df["el_atmos"]
    parent_total = la_rebuilt + el_rebuilt
    df["ara_parent"] = np.where(parent_total > 0, 2 * el_rebuilt / parent_total, 1.0)
    df["parent_signed"] = df["ara_parent"] - 1.0
    atmos_median = df[["atmos_flow_w", "atmos_flow_c", "atmos_flow_e"]].median(axis=1)
    flow_total = df["ocean_flow"].abs() + atmos_median.abs()
    el_flow = df["ocean_flow"].clip(lower=0) + atmos_median.clip(lower=0)
    df["ara_parent_flow"] = np.where(flow_total > 0, 2 * el_flow / flow_total, 1.0)
    df["parent_flow_signed"] = df["ara_parent_flow"] - 1.0

    checks: dict[str, object] = {}
    checks["protocol_hash_matches_result"] = sha256(PROTOCOL) == results["protocol_sha256"]
    checks["all_input_hashes_match"] = all(
        sha256(HERE / "data" / name) == expected
        for name, expected in results["input_sha256"].items()
    )
    checks["wwv_full_monthly_record"] = (
        results["coverage"]["wwv_east_raw"]["n"] == 556
        and results["coverage"]["wwv_west_raw"]["n"] == 556
    )
    checks["wwv_scientific_notation_preserved"] = (
        float(df["wwv_east_raw"].abs().max()) > 1e13
        and float(df["wwv_west_raw"].abs().max()) > 1e13
    )

    child_columns = ["la_ocean", "la_atmos", "el_ocean", "el_atmos"]
    checks["four_grandchild_strengths_nonnegative"] = bool(
        (df[child_columns].dropna() >= 0).all().all()
    )
    la_sum = df["la_ocean"] + df["la_atmos"]
    el_sum = df["el_ocean"] + df["el_atmos"]
    parent_expected = np.where(la_sum + el_sum > 0, 2 * el_sum / (la_sum + el_sum), 1.0)
    checks["parent_ara_reconstructs_from_four_grandchildren"] = bool(
        np.nanmax(np.abs(exported_parent_ara.to_numpy() - parent_expected)) < 1e-12
    )

    mapping = {
        "ocean WWV redistribution → Niño3.4": ("ocean_flow", "ocean_state"),
        "west trade wind → SOI": ("atmos_flow_w", "atmos_state"),
        "central trade wind → SOI": ("atmos_flow_c", "atmos_state"),
        "east trade wind → SOI": ("atmos_flow_e", "atmos_state"),
        "nested inflow relation → ENSO parent": ("parent_flow_signed", "parent_signed"),
        "west trade wind → OLR replication": ("atmos_flow_w", "atmos_state_olr"),
        "central trade wind → OLR replication": ("atmos_flow_c", "atmos_state_olr"),
        "east trade wind → OLR replication": ("atmos_flow_e", "atmos_state_olr"),
        "heat-content change → Niño3.4 replication": ("heat_flow", "ocean_state"),
    }

    replays: dict[str, dict] = {}
    replay_ok = True
    for recorded in results["holdout_results"]:
        driver, state = mapping[recorded["path"]]
        replay = recompute(df, driver, state, int(recorded["lead"]))
        fields_ok = {
            key: (replay[key] == recorded[key] if key == "n" else close(replay[key], recorded[key]))
            for key in [
                "bacc",
                "recall_el_nino_direction",
                "recall_la_nina_direction",
                "spearman",
                "n",
            ]
        }
        replays[recorded["path"]] = {"checks": fields_ok, "recomputed": replay}
        replay_ok = replay_ok and all(fields_ok.values())
    checks["all_holdout_scores_recompute"] = replay_ok

    passed = all(bool(value) for value in checks.values())
    payload = {
        "test": "T338 independent validation",
        "verdict": "PASS" if passed else "FAIL",
        "checks": checks,
        "holdout_replays": replays,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"verdict": payload["verdict"], "checks": checks}, indent=2))


if __name__ == "__main__":
    main()
