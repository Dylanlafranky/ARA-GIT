#!/usr/bin/env python3
"""Independent artifact-level validation for T353."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image


HERE = Path(__file__).resolve().parent
PREFIX = "T353_IRRATIONALITY_DUSK_SCALE_DECONVOLUTION"
PROTOCOL = HERE / f"{PREFIX}_PROTOCOL_v1_FROZEN.md"
BANDS = HERE / f"{PREFIX}_BANDS.csv"
PROFILES = HERE / f"{PREFIX}_PROFILES.csv"
IDENTITIES = HERE / f"{PREFIX}_IDENTITIES.csv"
GATES = HERE / f"{PREFIX}_FROZEN_GATES.csv"
RESULTS = HERE / f"{PREFIX}_RESULTS.json"
FIGURE = HERE / f"{PREFIX}_FIGURE.png"
STRIDE = 32


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest().upper()


def spearman(left: np.ndarray, right: np.ndarray) -> float:
    lr = pd.Series(left).rank(method="average").to_numpy()
    rr = pd.Series(right).rank(method="average").to_numpy()
    if np.std(lr) == 0 or np.std(rr) == 0:
        return 0.0
    return float(np.corrcoef(lr, rr)[0, 1])


def main() -> None:
    bands = pd.read_csv(BANDS)
    profiles = pd.read_csv(PROFILES)
    identities = pd.read_csv(IDENTITIES)
    gates = pd.read_csv(GATES)
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    checks: list[dict] = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    add("protocol hash", digest(PROTOCOL) == result["protocol_sha256"], digest(PROTOCOL))
    add("band count", len(bands) == result["band_rows"] == 2304, str(len(bands)))
    add("profile count", len(profiles) == result["profile_rows"] == 76032, str(len(profiles)))
    add("identity count", len(identities) == result["identity_rows"] == 288, str(len(identities)))
    add("two modes per window", bool((bands.groupby(["path_id", "window"])["mode"].nunique() == 2).all()), "ordered/abrupt")
    add("four windows per mode", bool((bands.groupby(["path_id", "mode"])["window"].nunique() == 4).all()), "128/256/384/512")
    add("x_R range", bool(profiles.x_r.between(0, 2).all()), f"[{profiles.x_r.min()}, {profiles.x_r.max()}]")
    add("band width stride", bool((bands.band_width % STRIDE == 0).all()), "32-state grain")

    # Rebuild each band from the saved profiles and its independently stored baseline.
    rebuilt = []
    for keys, group in profiles.groupby(["path_id", "mode", "window"], sort=False):
        identity, mode, window = keys
        stored = bands[(bands.path_id == identity) & (bands["mode"] == mode) & (bands.window == window)].iloc[0]
        threshold = float(stored.baseline_x_r + 0.25)
        selected = np.sort(group.loc[group.x_r >= threshold, "center"].unique())
        best = current = 0
        previous = None
        for center in selected:
            current = current + 1 if previous is not None and center - previous == STRIDE else 1
            best = max(best, current)
            previous = center
        rebuilt.append((identity, mode, window, best * STRIDE))
    rebuilt_df = pd.DataFrame(rebuilt, columns=["path_id", "mode", "window", "rebuilt_width"])
    compare = bands.merge(rebuilt_df, on=["path_id", "mode", "window"], validate="one_to_one")
    add("band-width reconstruction", bool((compare.band_width == compare.rebuilt_width).all()), "exact")

    # Independently rebuild identity deconvolution and smear fits.
    recreated = []
    for (identity, direction, duration), group in bands.groupby(["path_id", "direction", "duration"]):
        pivot = group.pivot(index="window", columns="mode", values="band_width").sort_index()
        added = pivot["ordered"] - pivot["abrupt"]
        x = pivot.index.to_numpy(float)
        y = pivot["abrupt"].to_numpy(float)
        slope, intercept = np.polyfit(x, y, 1)
        fit = slope * x + intercept
        total = float(np.sum((y - np.mean(y)) ** 2))
        residual = float(np.sum((y - fit) ** 2))
        r2 = 1.0 if total <= 1e-12 and residual <= 1e-12 else (0.0 if total <= 1e-12 else 1 - residual / total)
        duration_hat = float(np.median(added))
        recreated.append({"path_id": identity, "duration_hat": duration_hat, "absolute_error": abs(duration_hat - duration), "abrupt_intercept": intercept, "abrupt_slope": slope, "abrupt_r2": r2, "positive_window_count": int(np.sum(added > 0))})
    recreated = pd.DataFrame(recreated).set_index("path_id").sort_index()
    stored = identities.set_index("path_id").sort_index()
    numeric = ["duration_hat", "absolute_error", "abrupt_intercept", "abrupt_slope", "abrupt_r2"]
    max_error = max(float(np.max(np.abs(recreated[column] - stored[column]))) for column in numeric)
    add("identity numerical reconstruction", max_error < 1e-10, f"max error {max_error:.3e}")
    add("positive-window reconstruction", bool((recreated.positive_window_count == stored.positive_window_count).all()), "exact")

    for direction in ("irrational_to_rational", "rational_to_irrational"):
        part = identities[identities.direction == direction]
        rho = spearman(part.duration.to_numpy(float), part.duration_hat.to_numpy(float))
        saved = result["direction_results"][direction]
        add(f"{direction} duration median", abs(float(np.median(part.duration_hat)) - saved["duration_hat"]["estimate"]) < 1e-12, f"{np.median(part.duration_hat):.6f}")
        add(f"{direction} duration Spearman", abs(rho - saved["duration_spearman"]["estimate"]) < 1e-12, f"{rho:.12f}")
        add(f"{direction} absolute error median", abs(float(np.median(part.absolute_error)) - saved["absolute_error"]["estimate"]) < 1e-12, f"{np.median(part.absolute_error):.6f}")

    passed_count = int(gates.passed.astype(str).str.lower().eq("true").sum())
    add("gate count", passed_count == result["gates_passed"] == 2, f"{passed_count}/6")
    add("verdict", result["verdict"] == "WINDOW SMEAR ONLY", result["verdict"])
    with Image.open(FIGURE) as image:
        add("figure readable", image.width >= 1200 and image.height >= 800, f"{image.width}x{image.height}")

    passed = sum(record["passed"] for record in checks)
    status = "PASS" if passed == len(checks) else "FAIL"
    payload = {"status": status, "passed": passed, "total": len(checks), "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = [
        "# T353 independent validation", "",
        f"**Status:** **{status} — {passed}/{len(checks)} checks passed**", "",
        "The validator does not import the T353 run script. It rebuilds all band widths from saved profiles, independently reconstructs the matched deconvolution and smear fits, checks headline statistics, the protocol hash and the rendered figure.", "",
        "| check | result | detail |", "|---|---|---|",
    ]
    lines.extend(f"| {item['check']} | {'PASS' if item['passed'] else 'FAIL'} | {item['detail']} |" for item in checks)
    lines.extend(["", "## Boundary", "", "This is artifact-level numerical validation. It does not independently regenerate the raw synthetic paths and does not change the synthetic-only evidence class."])
    (HERE / f"{PREFIX}_VALIDATION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "passed": passed, "total": len(checks)}, indent=2))


if __name__ == "__main__":
    main()
