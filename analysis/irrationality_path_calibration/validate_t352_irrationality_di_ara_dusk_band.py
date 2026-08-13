#!/usr/bin/env python3
"""Independent artifact-level validation for T352."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image


HERE = Path(__file__).resolve().parent
PREFIX = "T352_IRRATIONALITY_DI_ARA_DUSK_BAND"
PROTOCOL = HERE / f"{PREFIX}_PROTOCOL_v1_FROZEN.md"
WINDOWS = HERE / f"{PREFIX}_WINDOWS.csv"
EVENTS = HERE / f"{PREFIX}_EVENTS.csv"
GATES = HERE / f"{PREFIX}_FROZEN_GATES.csv"
RESULTS = HERE / f"{PREFIX}_RESULTS.json"
FIGURE = HERE / f"{PREFIX}_FIGURE.png"
BOOTSTRAPS = 5000
SEED = 35220260811
STRIDE = 64


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest().upper()


def bootstrap_median(values: np.ndarray, offset: int) -> tuple[float, float, float]:
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(SEED + offset)
    draws = rng.integers(0, len(values), size=(BOOTSTRAPS, len(values)))
    samples = np.median(values[draws], axis=1)
    return float(np.median(values)), float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))


def close(left: float, right: float, tolerance: float = 1e-11) -> bool:
    return bool(abs(float(left) - float(right)) <= tolerance)


def main() -> None:
    windows = pd.read_csv(WINDOWS)
    events = pd.read_csv(EVENTS)
    gates = pd.read_csv(GATES)
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    checks: list[dict] = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    add("protocol hash", digest(PROTOCOL) == result["protocol_sha256"], digest(PROTOCOL))
    add("window row count", len(windows) == result["window_rows"] == 41328, str(len(windows)))
    add("event row count", len(events) == result["event_rows"] == 1008, str(len(events)))
    add("three modes per identity", bool((events.groupby("path_id")["mode"].nunique() == 3).all()), "abrupt/ordered/shuffled")
    add("fixed window width", bool(((windows["window_end"] - windows["window_start"]) == 512).all()), "512 states")
    add("fixed centre stride", bool(windows.groupby(["path_id", "mode"])["center"].apply(lambda x: np.all(np.diff(np.sort(x)) == STRIDE)).all()), "64 states")
    add("coordinate range x_P", bool(windows["x_p"].between(0, 2).all()), f"[{windows.x_p.min()}, {windows.x_p.max()}]")
    add("coordinate range x_R", bool(windows["x_r"].between(0, 2).all()), f"[{windows.x_r.min()}, {windows.x_r.max()}]")
    add("all regions present", set(windows["region"]) == {"pre", "handover", "post"}, str(sorted(windows.region.unique())))

    # Independently rebuild every event summary from the saved local coordinates.
    rebuilt: list[dict] = []
    keys = ["path_id", "mode"]
    for (identity, mode), group in windows.groupby(keys, sort=False):
        group = group.sort_values("center")
        pre = group[group.region == "pre"]
        post = group[group.region == "post"]
        hand = group[group.region == "handover"]
        pre_xr = float(pre.x_r.median())
        post_xr = float(post.x_r.median())
        baseline = max(pre_xr, post_xr)
        coords = hand[["x_p", "x_r"]].to_numpy(float)
        rebuilt.append(
            {
                "path_id": identity,
                "mode": mode,
                "pre_x_p": float(pre.x_p.median()),
                "post_x_p": float(post.x_p.median()),
                "pre_x_r": pre_xr,
                "post_x_r": post_xr,
                "excursion_x_r": float(hand.x_r.max() - baseline),
                "excess_area_x_r": float(np.maximum(hand.x_r.to_numpy() - baseline, 0).mean()),
                "band_width_states": int(np.sum(hand.x_r.to_numpy() >= baseline + 0.25) * STRIDE),
                "coordinate_roughness": float(np.linalg.norm(np.diff(coords, axis=0), axis=1).mean()),
                "final_post_error_x_r": abs(float(post.iloc[-1].x_r) - post_xr),
            }
        )
    rebuilt_df = pd.DataFrame(rebuilt).set_index(keys).sort_index()
    stored_df = events.set_index(keys).sort_index()
    summary_fields = [
        "pre_x_p", "post_x_p", "pre_x_r", "post_x_r", "excursion_x_r",
        "excess_area_x_r", "coordinate_roughness", "final_post_error_x_r",
    ]
    maximum_error = max(float(np.max(np.abs(rebuilt_df[field] - stored_df[field]))) for field in summary_fields)
    add("event summary numerical reconstruction", maximum_error < 1e-11, f"max error {maximum_error:.3e}")
    add("band width reconstruction", bool((rebuilt_df.band_width_states == stored_df.band_width_states).all()), "exact")

    hold = events[events["split"] == "holdout"]
    direction_values: dict[str, dict] = {}
    for index, direction in enumerate(("irrational_to_rational", "rational_to_irrational")):
        group = hold[hold["direction"] == direction]
        ordered = group[group["mode"] == "ordered"]
        pivot_area = group.pivot(index="path_id", columns="mode", values="excess_area_x_r")
        pivot_rough = group.pivot(index="path_id", columns="mode", values="coordinate_roughness")
        direction_values[direction] = {
            "excursion": bootstrap_median(ordered.excursion_x_r.to_numpy(), 100 + index),
            "reclosure": bootstrap_median(ordered.final_post_error_x_r.to_numpy(), 200 + index),
            "area": bootstrap_median((pivot_area["ordered"] - pivot_area["abrupt"]).to_numpy(), 300 + index),
            "rough": bootstrap_median((pivot_rough["shuffled"] - pivot_rough["ordered"]).to_numpy(), 400 + index),
        }
        saved = result["direction_results"][direction]
        for label, source in (("excursion", saved["excursion"]), ("reclosure", saved["reclosure_error"]), ("area", saved["ordered_minus_abrupt_area"]), ("rough", saved["shuffled_minus_ordered_roughness"])):
            values = direction_values[direction][label]
            add(f"{direction} {label} estimate", close(values[0], source["estimate"]), f"{values[0]:.12g}")
            add(f"{direction} {label} interval", close(values[1], source["ci_low"]) and close(values[2], source["ci_high"]), f"[{values[1]:.12g}, {values[2]:.12g}]")

    passed_count = int(gates.passed.astype(str).str.lower().eq("true").sum())
    add("gate count", passed_count == result["gates_passed"] == 4, f"{passed_count}/6")
    add("verdict logic", result["verdict"] == "MEASUREMENT DUSK ONLY", result["verdict"])
    with Image.open(FIGURE) as image:
        add("figure readable", image.width >= 1200 and image.height >= 800, f"{image.width}x{image.height}")

    passed = sum(item["passed"] for item in checks)
    status = "PASS" if passed == len(checks) else "FAIL"
    payload = {"status": status, "passed": passed, "total": len(checks), "checks": checks}
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = [
        "# T352 independent validation",
        "",
        f"**Status:** **{status} — {passed}/{len(checks)} checks passed**",
        "",
        "This validator does not import the T352 run script. It independently rebuilds every event summary from the saved local-window coordinates, repeats the matched bootstrap calculations, checks the frozen protocol hash and verifies the rendered figure.",
        "",
        "| check | result | detail |",
        "|---|---|---|",
    ]
    lines.extend(f"| {item['check']} | {'PASS' if item['passed'] else 'FAIL'} | {item['detail']} |" for item in checks)
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is artifact-level numerical validation. It does not independently regenerate every raw synthetic path, and it does not change the synthetic-only evidence class.",
        ]
    )
    (HERE / f"{PREFIX}_VALIDATION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "passed": passed, "total": len(checks)}, indent=2))


if __name__ == "__main__":
    main()
