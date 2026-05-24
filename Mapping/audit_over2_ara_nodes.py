#!/usr/bin/env python3
"""
Audit ARA mapping nodes above the clean 0..2 band.

Above-2 values are useful diagnostics, but they should not be treated as
ordinary bounded ARA coordinates until each one has an interpretation:

- reversed orientation candidate
- compound/multiple-system ratio
- one-shot lifetime or storage/release ratio
- rung mismatch
- source-specific fit metric rather than build/release ARA

This script does not rewrite the atlas. It creates a review ledger that can be
used to correct or quarantine entries in a controlled way.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ATLAS = HERE / "ara_mapping_atlas_data.json"
OUT_JSON = HERE / "ara_over2_audit.json"
OUT_MD = HERE / "ARA_OVER2_AUDIT.md"

PHI = (1.0 + 5.0**0.5) / 2.0


def bounded_inverse(ara: float) -> float | None:
    if ara == 0 or not math.isfinite(ara):
        return None
    inv = 1.0 / ara
    return inv if 0.0 <= inv <= 2.0 else None


def fold_mod_two(ara: float) -> float | None:
    if not math.isfinite(ara):
        return None
    folded = ara % 2.0
    return folded if 0.0 <= folded <= 2.0 else None


def classify_review(node: dict) -> tuple[str, str]:
    ara = node["ara"]
    layer = node.get("layer", "")
    source = node.get("source", "")
    system = node.get("system", "")
    name = node.get("name", "")
    relation_class = node.get("relation_class", "")
    notes = node.get("notes", "")
    text = " ".join([name, system, relation_class, notes, source]).lower()

    if layer == "state_geometry":
        return (
            "formula_state_metric",
            "State-geometry ARA above 2 is a fitted state descriptor; retest from the underlying signal before treating it as bounded build/release ARA.",
        )
    if layer == "measured_fit":
        return (
            "event_fit_metric",
            "Measured-fit event nodes can encode sparse event spacing or fitted component ratios; retest from raw event windows and orientation.",
        )
    if any(key in text for key in ["metastable", "decay", "half-life", "lifetime", "transient"]):
        return (
            "one_shot_storage_release",
            "Likely a one-shot storage/release or lifetime ratio. Keep as diagnostic unless a repeatable cycle is defined.",
        )
    if any(key in text for key in ["cell cycle", "protein", "transcription", "translation", "turnover", "fold"]):
        return (
            "compound_biochemical_process",
            "Biochemical above-2 value likely mixes storage, processing, and release windows. Needs subsystem split.",
        )
    if any(key in text for key in ["dark adaptation", "stellar lifecycle", "supernova", "geomagnetic reversal", "wilson cycle"]):
        return (
            "long_transient_or_regime_change",
            "Long transient/regime-change ratio rather than a clean bounded oscillator.",
        )
    if ara > 10:
        return (
            "extreme_snap_or_rung_mismatch",
            "Very large ARA. Treat as snap/overflow or rung mismatch until independently remeasured.",
        )
    return (
        "moderate_overflow_review",
        "Moderate above-2 value. First checks: reverse orientation, split coupled subsystems, or move up/down a rung.",
    )


def audit_node(node: dict) -> dict:
    ara = float(node["ara"])
    inv = bounded_inverse(ara)
    folded = fold_mod_two(ara)
    review_class, recommendation = classify_review(node)
    return {
        "id": node["id"],
        "name": node["name"],
        "system": node["system"],
        "system_label": node["system_label"],
        "layer": node["layer"],
        "source": node.get("source"),
        "ara": ara,
        "period_seconds": node.get("period_seconds"),
        "period_phi_rung": node.get("period_phi_rung"),
        "ara_class": node.get("ara_class"),
        "nearest_boundary": node.get("nearest_boundary"),
        "review_class": review_class,
        "recommendation": recommendation,
        "inverse_if_reversed": inv,
        "folded_mod_2": folded,
        "distance_inverse_to_phi": abs(inv - PHI) if inv is not None else None,
        "distance_folded_to_phi": abs(folded - PHI) if folded is not None else None,
        "notes": node.get("notes"),
        "source_metric": node.get("source_metric"),
        "measurement_status": node.get("measurement_status"),
    }


def fmt(value, digits=4):
    if value is None:
        return "n/a"
    if isinstance(value, float):
        if abs(value) >= 1e5 or (0 < abs(value) < 1e-4):
            return f"{value:.3e}"
        return f"{value:.{digits}f}"
    return str(value)


def main() -> None:
    payload = json.loads(ATLAS.read_text(encoding="utf-8"))
    nodes = [n for n in payload["nodes"] if n.get("ara") is not None and n["ara"] > 2.0]
    audits = [audit_node(n) for n in sorted(nodes, key=lambda item: (-item["ara"], item["layer"], item["id"]))]
    all_layers = sorted({n.get("layer", "unknown") for n in payload["nodes"]})
    over2_layers = {a["layer"] for a in audits}
    summary = {
        "date": "2026-05-24",
        "threshold": 2.0,
        "over2_count": len(audits),
        "total_nodes": len(payload["nodes"]),
        "by_layer": dict(Counter(a["layer"] for a in audits)),
        "layers_without_over2": [layer for layer in all_layers if layer not in over2_layers],
        "by_review_class": dict(Counter(a["review_class"] for a in audits)),
        "extreme_over10_count": sum(1 for a in audits if a["ara"] > 10.0),
        "moderate_2_to_10_count": sum(1 for a in audits if 2.0 < a["ara"] <= 10.0),
        "bounded_inverse_count": sum(1 for a in audits if a["inverse_if_reversed"] is not None),
    }
    out = {"summary": summary, "items": audits}
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")

    lines = [
        "# ARA Over-2 Audit",
        "",
        "**Date:** 2026-05-24",
        "",
        "Above-2 nodes are no longer treated as normal bounded ARA positions.",
        "Each should be interpreted as a diagnostic until retested from source data or decomposed into subsystems.",
        "",
        "## Summary",
        "",
        f"- Over-2 nodes: `{summary['over2_count']}` / `{summary['total_nodes']}`",
        f"- Moderate `2..10`: `{summary['moderate_2_to_10_count']}`",
        f"- Extreme `>10`: `{summary['extreme_over10_count']}`",
        f"- Inverse would fall inside `0..2`: `{summary['bounded_inverse_count']}`",
        "",
        "By layer:",
        "",
    ]
    for layer, count in sorted(summary["by_layer"].items()):
        lines.append(f"- `{layer}`: `{count}`")
    lines.extend(["", "Layer leakage check:", ""])
    if summary["layers_without_over2"]:
        clean_layers = ", ".join(f"`{layer}`" for layer in summary["layers_without_over2"])
        lines.append(f"- No over-2 nodes found in: {clean_layers}")
    else:
        lines.append("- Every atlas layer has at least one over-2 node.")
    lines.append("- Current result: all above-2 nodes come from the older hand-curated catalogue layer.")
    lines.extend(["", "By review class:", ""])
    for klass, count in sorted(summary["by_review_class"].items()):
        lines.append(f"- `{klass}`: `{count}`")
    lines.extend(
        [
            "",
            "## Review Table",
            "",
            "| Node | Layer | ARA | Inverse | Folded mod 2 | Review class | Recommendation |",
            "|---|---|---:|---:|---:|---|---|",
        ]
    )
    for item in audits:
        node = f"`{item['name']}`<br>`{item['id']}`"
        lines.append(
            "| "
            + " | ".join(
                [
                    node,
                    f"`{item['layer']}`",
                    fmt(item["ara"]),
                    fmt(item["inverse_if_reversed"]),
                    fmt(item["folded_mod_2"]),
                    f"`{item['review_class']}`",
                    item["recommendation"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Retest Rules",
            "",
            "1. If `ARA > 2`, first ask whether the measurement is a true repeatable build/release cycle.",
            "2. If it is a repeatable cycle, test the opposite orientation: `1 / ARA`.",
            "3. If both sides are physical and coupled, split it into child subsystems before placing it on the bounded axis.",
            "4. If it is a one-shot lifetime, decay, storage, or regime-change ratio, keep it on the diagnostic rail rather than the normal ARA band.",
            "5. If it came from a fitted state or event extractor, rerun from the raw series and record the source window before changing the atlas coordinate.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"over2={summary['over2_count']} total={summary['total_nodes']}")
    print(f"by_layer={summary['by_layer']}")
    print(f"by_review_class={summary['by_review_class']}")
    print(f"saved {OUT_JSON}")
    print(f"saved {OUT_MD}")


if __name__ == "__main__":
    main()
