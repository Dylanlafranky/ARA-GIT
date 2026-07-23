#!/usr/bin/env python3
"""Build the bounded Data Analytics report artifact for the ARA memory test."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "ARA_MEMORY_OTHER_RESULTS.json"
OUTPUT = ROOT / "ARA_MEMORY_OTHER_REPORT_ARTIFACT.json"


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    primary = result["primary_rows"]
    smooth = next(row for row in primary if row["dataset"] == "smooth_telemetry")

    headline = [
        {
            "restoration_checks_passed": 20,
            "restoration_checks_total": 20,
            "smooth_improvement": smooth["ara_vs_raw_improvement"],
            "attacker_recovery_rate": 1.0,
            "authenticated_roundtrip": 1.0,
        }
    ]

    comparison = []
    for row in primary:
        comparison.append(
            {
                "dataset": row["dataset"],
                "dataset_class": row["dataset_class"],
                "block_size": row["block_size"],
                "ara_vs_raw_improvement": row["ara_vs_raw_improvement"],
                "improvement_percent": 100 * row["ara_vs_raw_improvement"],
                "raw_zlib_bytes": row["raw_zlib_bytes"],
                "delta_zlib_bytes": row["delta_zlib_bytes"],
                "ara_zlib_bytes": row["ara_zlib_bytes"],
                "restored_exactly": row["restored_exactly"],
            }
        )

    method_sizes = []
    for row in primary:
        for method, field in (
            ("Raw zlib", "raw_zlib_bytes"),
            ("Delta + zlib", "delta_zlib_bytes"),
            ("ARA + zlib", "ara_zlib_bytes"),
        ):
            method_sizes.append(
                {
                    "dataset": row["dataset"],
                    "dataset_class": row["dataset_class"],
                    "method": method,
                    "compressed_bytes": row[field],
                    "original_bytes": row["original_bytes"],
                    "block_size": row["block_size"],
                    "restored_exactly": row["restored_exactly"],
                }
            )

    security = [
        {
            "test": "Public-transform attacker",
            "outcome": "Plaintext recovered",
            "passed_as_security": False,
            "exact_restoration": result["security"]["naive_attacker_exact_recovery"],
            "overhead_bytes": 0,
        },
        {
            "test": "AES-256-GCM wrapper",
            "outcome": "Roundtrip and tamper rejection",
            "passed_as_security": True,
            "exact_restoration": result["security"]["authenticated_roundtrip_exact"],
            "overhead_bytes": result["security"]["authenticated_overhead_bytes"],
        },
    ]

    source = {
        "id": "ara-memory-test",
        "label": "Frozen ARA memory test outputs",
        "path": str(RESULTS),
        "query": {
            "id": "ara-memory-primary-v1",
            "language": "sql",
            "engine": "duckdb",
            "description": (
                "Reads primary 1,024-byte-block compression and restoration results "
                "from the frozen deterministic experiment."
            ),
            "sql": (
                "SELECT * FROM read_json_auto("
                "'analysis/computing/ara_memory/ARA_MEMORY_OTHER_RESULTS.json');"
            ),
            "tables_used": [
                "analysis/computing/ara_memory/ARA_MEMORY_OTHER_RESULTS.json",
                "analysis/computing/ara_memory/ARA_MEMORY_OTHER_VALIDATION.json",
            ],
            "filters": [
                "Primary block size = 1,024 bytes for headline compression comparison",
                "Every frozen dataset contains 65,536 bytes",
            ],
            "metric_definitions": [
                "improvement_percent = 100 * (raw_zlib_bytes - ara_zlib_bytes) / raw_zlib_bytes",
                "Positive improvement means ARA + zlib is smaller; negative means it is larger",
                "All restoration outcomes require byte equality and matching SHA-256",
                "Attacker recovery rate is exact public-transform plaintext recovery",
            ],
        },
    }

    manifest = {
        "version": 1,
        "surface": "report",
        "title": "ARA Other Memory, Compression and Security Test",
        "description": (
            "Frozen test separating reversible restoration, compression efficiency, "
            "confidentiality and authenticated-encryption compatibility."
        ),
        "generatedAt": "2026-07-23T22:00:00+10:00",
        "sources": [source],
        "cards": [
            {
                "id": "restoration-card",
                "description": "Dataset/block combinations reconstructed byte-for-byte.",
                "dataset": "headline",
                "sourceId": "ara-memory-test",
                "metrics": [
                    {
                        "label": "Exact restorations",
                        "field": "restoration_checks_passed",
                        "format": "number",
                    },
                    {
                        "label": "Frozen checks",
                        "field": "restoration_checks_total",
                        "format": "number",
                    },
                ],
            },
            {
                "id": "smooth-card",
                "description": "ARA + zlib size reduction versus raw zlib on smooth telemetry.",
                "dataset": "headline",
                "sourceId": "ara-memory-test",
                "metrics": [
                    {
                        "label": "Smooth-data gain",
                        "field": "smooth_improvement",
                        "format": "percent",
                    }
                ],
            },
            {
                "id": "attack-card",
                "description": "Exact plaintext recovery by an attacker knowing the public transform.",
                "dataset": "headline",
                "sourceId": "ara-memory-test",
                "metrics": [
                    {
                        "label": "Attacker recovery",
                        "field": "attacker_recovery_rate",
                        "format": "percent",
                    }
                ],
            },
        ],
        "charts": [
            {
                "id": "compression-change-chart",
                "title": "ARA compression change versus raw zlib",
                "description": (
                    "Positive values are smaller; negative values are expansion. "
                    "Each dataset contains 65,536 bytes."
                ),
                "type": "bar",
                "dataset": "comparison",
                "sourceId": "ara-memory-test",
                "encodings": {
                    "x": {"field": "dataset", "type": "nominal"},
                    "y": {"field": "improvement_percent", "type": "quantitative"},
                },
                "options": {"orientation": "vertical", "grouping": "single"},
            },
            {
                "id": "method-size-chart",
                "title": "Compressed size by representation",
                "description": (
                    "Lower is better; the fixed ARA transform helps only the smooth signal."
                ),
                "type": "bar",
                "dataset": "method_sizes",
                "sourceId": "ara-memory-test",
                "encodings": {
                    "x": {"field": "dataset", "type": "nominal"},
                    "y": {"field": "compressed_bytes", "type": "quantitative"},
                    "color": {"field": "method", "type": "nominal"},
                },
                "options": {"orientation": "vertical", "grouping": "grouped"},
            },
        ],
        "tables": [
            {
                "id": "primary-results-table",
                "title": "Primary 1,024-byte-block results",
                "description": "Exact byte counts and restoration status by dataset.",
                "dataset": "comparison",
                "sourceId": "ara-memory-test",
                "columns": [
                    {"field": "dataset", "label": "Dataset", "type": "text"},
                    {"field": "dataset_class", "label": "Class", "type": "text"},
                    {"field": "raw_zlib_bytes", "label": "Raw zlib", "type": "number"},
                    {"field": "delta_zlib_bytes", "label": "Delta + zlib", "type": "number"},
                    {"field": "ara_zlib_bytes", "label": "ARA + zlib", "type": "number"},
                    {
                        "field": "improvement_percent",
                        "label": "ARA change, %",
                        "type": "number",
                    },
                    {
                        "field": "restored_exactly",
                        "label": "Exact restore",
                        "type": "text",
                    },
                ],
                "defaultSort": {
                    "field": "improvement_percent",
                    "direction": "desc",
                },
            },
            {
                "id": "security-table",
                "title": "Security outcomes",
                "description": (
                    "Reversible representation and authenticated encryption are separate."
                ),
                "dataset": "security",
                "sourceId": "ara-memory-test",
                "columns": [
                    {"field": "test", "label": "Test", "type": "text"},
                    {"field": "outcome", "label": "Outcome", "type": "text"},
                    {
                        "field": "passed_as_security",
                        "label": "Security passed",
                        "type": "text",
                    },
                    {
                        "field": "exact_restoration",
                        "label": "Exact restore",
                        "type": "text",
                    },
                    {"field": "overhead_bytes", "label": "Overhead", "type": "number"},
                ],
                "defaultSort": {"field": "overhead_bytes", "direction": "asc"},
            },
        ],
        "blocks": [
            {
                "id": "title",
                "type": "markdown",
                "body": "# ARA Other Memory, Compression and Security Test",
            },
            {
                "id": "executive-summary",
                "type": "markdown",
                "sourceId": "ara-memory-test",
                "body": (
                    "## Executive Summary\n\n"
                    "Parent plus retained signed `Other` is an exact reversible memory "
                    "representation: all 20 frozen dataset/block combinations restored "
                    "byte-for-byte. Compression was conditional rather than universal. "
                    "The fixed transform improved smooth telemetry by 19.23% versus raw "
                    "zlib, but simple delta was better and the other four datasets expanded. "
                    "The public residual stream was inverted exactly, so it is not encryption. "
                    "AES-GCM protected it successfully, but the security belongs to AES-GCM."
                ),
            },
            {
                "id": "metrics",
                "type": "metric-strip",
                "cardIds": ["restoration-card", "smooth-card", "attack-card"],
            },
            {
                "id": "compression-heading",
                "type": "markdown",
                "body": (
                    "## Compression Boundary\n\n"
                    "A residual is useful only when its parent predicts the children more "
                    "cheaply than the transform disrupts existing repetition. The random "
                    "control correctly produced no win."
                ),
            },
            {
                "id": "compression-change",
                "type": "chart",
                "chartId": "compression-change-chart",
            },
            {
                "id": "method-heading",
                "type": "markdown",
                "body": (
                    "## Method Comparison\n\n"
                    "The smooth-data gain is real but not superior to the ordinary delta "
                    "control. Raw zlib remains best for record memory, text and source code."
                ),
            },
            {"id": "method-size", "type": "chart", "chartId": "method-size-chart"},
            {
                "id": "results-heading",
                "type": "markdown",
                "body": (
                    "## Exact Results\n\n"
                    "Every representation was scored with container overhead included."
                ),
            },
            {
                "id": "primary-results",
                "type": "table",
                "tableId": "primary-results-table",
            },
            {
                "id": "security-heading",
                "type": "markdown",
                "body": (
                    "## Security Boundary\n\n"
                    "Moving `Other` into a hidden coordinate is obscurity when the transform "
                    "is public. A keyed authenticated cipher can wrap the residual stream, "
                    "but ARA has not supplied a public-key hardness assumption or trapdoor."
                ),
            },
            {"id": "security-results", "type": "table", "tableId": "security-table"},
            {
                "id": "conclusion",
                "type": "markdown",
                "body": (
                    "## Conclusion\n\n"
                    "Exact hierarchical restoration is confirmed. Universal compression is "
                    "not supported. Naive ARA confidentiality failed. Compatibility with "
                    "authenticated encryption is confirmed, while prime/public-key replacement "
                    "remains unestablished.\n\n"
                    "### Next test\n\n"
                    "Freeze an adaptive block selector that chooses raw, delta, pair-lifting "
                    "or record-aware prediction after paying selector overhead, then evaluate "
                    "unseen sensor, media, memory, text and random inputs."
                ),
            },
        ],
    }

    artifact = {
        "surface": "report",
        "manifest": manifest,
        "snapshot": {
            "version": 1,
            "status": "ready",
            "generatedAt": "2026-07-23T22:00:00+10:00",
            "datasets": {
                "headline": headline,
                "comparison": comparison,
                "method_sizes": method_sizes,
                "security": security,
            },
        },
        "sources": [source],
    }
    OUTPUT.write_text(
        json.dumps(artifact, ensure_ascii=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(OUTPUT)


if __name__ == "__main__":
    main()
