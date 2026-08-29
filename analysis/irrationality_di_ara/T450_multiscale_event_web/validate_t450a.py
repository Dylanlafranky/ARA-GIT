"""Reproducibility, data-quality and artifact validation for T450A."""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"


def check(name: str, condition: bool, detail: object) -> dict:
    return {"check": name, "passed": bool(condition), "detail": detail}


def main() -> None:
    dev_cache = sorted((HERE / "cache" / "development").glob("*.npz"))
    hold_cache = sorted((HERE / "cache" / "holdout").glob("*.npz"))
    config_path = RESULTS / "T450A_FROZEN_CONFIG.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    dev_metrics = pd.read_csv(RESULTS / "T450A_development_scale_metrics.csv")
    hold_metrics = pd.read_csv(RESULTS / "T450A_holdout_scale_metrics.csv")
    dev_quality = pd.read_csv(RESULTS / "T450A_development_quality.csv")
    hold_quality = pd.read_csv(RESULTS / "T450A_holdout_quality.csv")
    dev_ara = pd.read_csv(RESULTS / "T450A_development_ara_coordinates.csv")
    hold_ara = pd.read_csv(RESULTS / "T450A_holdout_ara_coordinates.csv")
    controls = pd.read_csv(RESULTS / "T450A_development_controls.csv")
    transfer = pd.read_csv(RESULTS / "T450A_holdout_transfer.csv")
    checks = []
    checks.append(check("six development caches", len(dev_cache) == 6, len(dev_cache)))
    checks.append(check("two untouched holdout caches", len(hold_cache) == 2, len(hold_cache)))
    checks.append(check("no source identity crosses split", not ({p.name for p in dev_cache} & {p.name for p in hold_cache}), "disjoint"))
    checks.append(check("four envelopes per development fly", len(dev_quality) == 24 and dev_quality.groupby("source_file").size().eq(4).all(), len(dev_quality)))
    checks.append(check("four envelopes per holdout fly", len(hold_quality) == 8 and hold_quality.groupby("source_file").size().eq(4).all(), len(hold_quality)))
    checks.append(check("development metric row count", len(dev_metrics) == 24 * 6 * 11, len(dev_metrics)))
    checks.append(check("holdout metric row count", len(hold_metrics) == 8 * 6 * 11, len(hold_metrics)))
    checks.append(check("all scale metrics retain at least five blocks", dev_metrics.valid_blocks.min() >= 5 and hold_metrics.valid_blocks.min() >= 5, {"development_min": int(dev_metrics.valid_blocks.min()), "holdout_min": int(hold_metrics.valid_blocks.min())}))
    checks.append(check("core pose visibility at least 99%", min(dev_quality.core_valid_fraction.min(), hold_quality.core_valid_fraction.min()) >= 0.99, float(min(dev_quality.core_valid_fraction.min(), hold_quality.core_valid_fraction.min()))))
    checks.append(check("ARA displays bounded strictly inside 0–2", dev_ara.ARA_coordinate.between(0, 2, inclusive="neither").all() and hold_ara.ARA_coordinate.between(0, 2, inclusive="neither").all(), {"min": float(min(dev_ara.ARA_coordinate.min(), hold_ara.ARA_coordinate.min())), "max": float(max(dev_ara.ARA_coordinate.max(), hold_ara.ARA_coordinate.max()))}))
    checks.append(check("all frozen rungs meet four-fly support", all(row["support_flies"] >= 4 for row in config["rungs"]), [row["support_flies"] for row in config["rungs"]]))
    checks.append(check("chronology controls present for every dev envelope and rung", len(controls) == 24 * len(config["rungs"]), len(controls)))
    checks.append(check("holdout transfer has both flies per rung", len(transfer) == 2 * len(config["rungs"]), len(transfer)))
    checks.append(check("frozen configuration predates all holdout caches", bool(hold_cache) and config_path.stat().st_mtime <= min(path.stat().st_mtime for path in hold_cache), {"config_mtime": config_path.stat().st_mtime, "first_holdout_mtime": min(path.stat().st_mtime for path in hold_cache) if hold_cache else None}))
    forbidden = re.compile(r"collapse|death", re.I)
    metadata_forbidden = []
    for path in dev_cache + hold_cache:
        loaded = np.load(path, allow_pickle=False)
        metadata = json.loads(str(loaded["metadata_json"]))
        found = [key for key in metadata if forbidden.search(key)]
        if found:
            metadata_forbidden.append({"file": path.name, "keys": found})
    checks.append(check("pose caches contain no collapse/death fields", not metadata_forbidden, metadata_forbidden or "none"))

    report = RESULTS / "T450A_POSE_SCALE_DISCOVERY_REPORT.html"
    report_text = report.read_text(encoding="utf-8") if report.exists() else ""
    images = sorted((RESULTS / "figures").glob("T450A_*.png"))
    image_sizes = {}
    for path in images:
        with Image.open(path) as image:
            image_sizes[path.name] = image.size
    checks.append(check("eight required visual figures exist", len(images) == 8, len(images)))
    checks.append(check("figures are readable and at least 1200px wide", bool(images) and all(width >= 1200 and height >= 600 for width, height in image_sizes.values()), image_sizes))
    checks.append(check("self-contained HTML report embeds all images", report.exists() and report_text.count("data:image/png;base64,") == 8, report_text.count("data:image/png;base64,")))
    checks.append(check("report preserves Who/What/When/Where/Why/How", all(term in report_text for term in ("Who:", "What:", "When:", "Where:", "Why:", "How:")), "all six labels"))
    status = "PASS" if all(row["passed"] for row in checks) else "FAIL"
    output = {
        "status": status,
        "checks_passed": sum(row["passed"] for row in checks),
        "checks_total": len(checks),
        "checks": checks,
    }
    (RESULTS / "T450A_VALIDATION.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

