"""Independent computational validation for T455 outputs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
SOURCE = ROOT / "source" / "eopc04_20u24.1962-now.csv"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def add_check(checks: list[dict], name: str, passed: bool, detail: str) -> None:
    checks.append({"check": name, "passed": bool(passed), "detail": detail})


def metric(actual: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    error = pred - actual
    denom = np.sum((actual - actual.mean()) ** 2)
    return {
        "n": len(actual),
        "mae": float(np.mean(np.abs(error))),
        "rmse": float(np.sqrt(np.mean(error**2))),
        "bias": float(np.mean(error)),
        "r2": float(1 - np.sum(error**2) / denom) if denom > 0 else np.nan,
    }


def main() -> None:
    checks: list[dict] = []
    result = json.loads((RESULTS / "T455_RESULT.json").read_text(encoding="utf-8"))
    windows = pd.read_csv(RESULTS / "T455_SCALE_WINDOWS.csv", parse_dates=["start_date", "end_date"])
    daily = pd.read_csv(RESULTS / "T455_DAILY_IERS_1984_NOW.csv", parse_dates=["date"])
    ledger = pd.read_csv(RESULTS / "T455_FORECAST_LEDGER.csv", parse_dates=["end_date", "target_end_date"])
    metrics = pd.read_csv(RESULTS / "T455_FORECAST_METRICS.csv")
    gates = pd.read_csv(RESULTS / "T455_FROZEN_GATES.csv")
    seasonal = pd.read_csv(RESULTS / "T455_POSTHOC_SEASONAL_AUDIT.csv")

    observed_hash = sha256(SOURCE)
    add_check(
        checks,
        "official source checksum",
        observed_hash == result["source_sha256"],
        f"sha256={observed_hash}",
    )

    gaps = daily.date.diff().dropna().dt.days
    add_check(
        checks,
        "daily sequence is chronological and gap-free",
        bool((gaps == 1).all()),
        f"rows={len(daily)}; start={daily.date.min().date()}; end={daily.date.max().date()}",
    )

    scale_one = windows[windows.scale_days.eq(1)].copy()
    s_clock = (86400.0 + scale_one.lod.to_numpy(float)) / 86400.0
    expected_clock = 2 * s_clock / (1 + s_clock)
    clock_diff = float(np.max(np.abs(expected_clock - scale_one.clock_ara.to_numpy(float))))
    add_check(checks, "exact two-clock ARA formula", clock_diff < 1e-14, f"max diff={clock_diff:.3g}")

    finite_amount = windows.dropna(subset=["pole_log_ratio", "pole_amount_ara"])
    expected_amount = 1 + np.tanh(finite_amount.pole_log_ratio.to_numpy(float) / 2)
    amount_diff = float(np.max(np.abs(expected_amount - finite_amount.pole_amount_ara.to_numpy(float))))
    add_check(checks, "pole amount ARA formula", amount_diff < 1e-14, f"max diff={amount_diff:.3g}")

    finite_turn = windows.dropna(subset=["pole_turn_rad", "pole_traversal_ara"])
    expected_traversal = 1 + finite_turn.pole_turn_rad.to_numpy(float) / np.pi
    traversal_diff = float(
        np.max(np.abs(expected_traversal - finite_turn.pole_traversal_ara.to_numpy(float)))
    )
    bounded = finite_turn.pole_traversal_ara.between(0, 2).all()
    add_check(
        checks,
        "signed traversal ARA formula and bounds",
        traversal_diff < 1e-14 and bool(bounded),
        f"max diff={traversal_diff:.3g}; range={finite_turn.pole_traversal_ara.min():.6f}–{finite_turn.pole_traversal_ara.max():.6f}",
    )

    prospective = bool((ledger.target_end_date > ledger.end_date).all())
    split_dates = (
        (ledger.split.eq("development") & ledger.target_end_date.le("2008-12-31"))
        | (ledger.split.eq("validation") & ledger.target_end_date.between("2009-01-01", "2016-12-31"))
        | (ledger.split.eq("holdout") & ledger.target_end_date.ge("2017-01-01"))
    )
    add_check(
        checks,
        "all forecasts are prospective with frozen chronological splits",
        prospective and bool(split_dates.all()),
        f"rows={len(ledger)}; minimum lead={(ledger.target_end_date-ledger.end_date).dt.days.min()} day(s)",
    )

    maximum_metric_diff = 0.0
    row_count_match = True
    for row in metrics.itertuples(index=False):
        selected = ledger[
            ledger.scale_days.eq(row.scale_days)
            & ledger.horizon_windows.eq(row.horizon_windows)
            & ledger.split.eq(row.split)
        ]
        direct = metric(
            selected.target_lod.to_numpy(float),
            selected[f"pred_{row.model}"].to_numpy(float),
        )
        row_count_match &= int(row.n) == int(direct["n"])
        for field in ("mae", "rmse", "bias", "r2"):
            if np.isfinite(getattr(row, field)) and np.isfinite(direct[field]):
                maximum_metric_diff = max(maximum_metric_diff, abs(float(getattr(row, field)) - direct[field]))
    add_check(
        checks,
        "forecast metrics reproduce from the event ledger",
        row_count_match and maximum_metric_diff < 1e-12,
        f"max numeric diff={maximum_metric_diff:.3g}",
    )

    gate_passes = int(gates.passed.astype(str).str.lower().eq("true").sum())
    add_check(
        checks,
        "frozen gate accounting",
        gate_passes == result["gates_passed"] == 3 and len(gates) == result["gates_total"] == 6,
        f"{gate_passes}/{len(gates)} gates passed",
    )

    posthoc_labeled = seasonal.status.str.contains("post-result", case=False, regex=False).all()
    add_check(
        checks,
        "seasonal diagnostic cannot silently alter frozen result",
        bool(posthoc_labeled),
        f"{len(seasonal)} rows explicitly labelled post-result",
    )

    artifact_path = RESULTS / "artifact.json"
    artifact_ok = False
    artifact_detail = "artifact not yet built"
    if artifact_path.exists():
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        datasets = artifact.get("snapshot", {}).get("datasets", {})
        max_rows = max((len(rows) for rows in datasets.values()), default=0)
        artifact_ok = (
            artifact.get("surface") == "report"
            and artifact.get("manifest", {}).get("title")
            and artifact.get("manifest", {}).get("blocks")
            and len(datasets) <= 50
            and max_rows <= 2000
            and artifact_path.stat().st_size < 3_000_000
        )
        artifact_detail = (
            f"datasets={len(datasets)}; max rows={max_rows}; bytes={artifact_path.stat().st_size}"
        )
    add_check(checks, "bounded report artifact structure", artifact_ok, artifact_detail)

    payload = {
        "test": "T455",
        "checks_passed": int(sum(item["passed"] for item in checks)),
        "checks_total": len(checks),
        "all_passed": bool(all(item["passed"] for item in checks)),
        "assessment": "Share with caveats" if all(item["passed"] for item in checks) else "Do not share",
        "checks": checks,
    }
    (RESULTS / "T455_VALIDATION.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

