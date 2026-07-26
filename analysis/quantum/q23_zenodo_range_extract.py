#!/usr/bin/env python3
"""Staged extraction for Q23 connection-web to logical-bit ARA closure."""

from __future__ import annotations

import argparse
import json
import pathlib
from datetime import datetime, timezone

from q20_zenodo_range_extract import (
    ARCHIVE_KEY,
    EXPECTED_ARCHIVE_MD5,
    RECORD_ID,
    archive_metadata,
    central_directory,
    extract_member,
    safe_output_path,
)


ROOT = pathlib.Path(__file__).parent
PREFIX = "google_105Q_surface_code_d3_d5_d7/d7_at_q6_7"
ROUNDS = ("r13", "r30")
GEOMETRY_MEMBERS = tuple(
    f"{PREFIX}/{basis}/{rounds}/{name}"
    for basis in ("X", "Z")
    for rounds in ROUNDS
    for name in ("metadata.json", "circuit_ideal.stim", "detection_events.b8")
)
OUTCOME_MEMBERS = tuple(
    f"{PREFIX}/{basis}/{rounds}/obs_flips_actual.b8"
    for basis in ("X", "Z")
    for rounds in ROUNDS
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stage", required=True, choices=("geometry", "outcomes")
    )
    stage = parser.parse_args().stage
    selected = GEOMETRY_MEMBERS if stage == "geometry" else OUTCOME_MEMBERS
    output_root = (
        ROOT
        / "public_data"
        / (
            "q23_willow_d7_geometry"
            if stage == "geometry"
            else "q23_willow_d7_outcomes"
        )
    )
    url, archive_size, archive_checksum = archive_metadata()
    members = central_directory(url, archive_size)
    missing = [name for name in selected if name not in members]
    if missing:
        raise RuntimeError(f"Members absent from archive: {missing}")

    extracted = []
    for name in selected:
        member = members[name]
        output = safe_output_path(output_root, name)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(extract_member(url, member))
        extracted.append(
            {
                "name": name,
                "output": str(output.relative_to(output_root)),
                "compression": member.compression,
                "crc32": f"{member.crc32:08x}",
                "compressed_size": member.compressed_size,
                "uncompressed_size": member.uncompressed_size,
                "local_offset": member.local_offset,
            }
        )
        print(f"verified {name} -> {output}")
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "SOURCE_MANIFEST.json").write_text(
        json.dumps(
            {
                "stage": stage,
                "source_doi": "10.5281/zenodo.13273331",
                "record_id": RECORD_ID,
                "archive_key": ARCHIVE_KEY,
                "archive_size": archive_size,
                "archive_checksum": archive_checksum,
                "expected_archive_md5": EXPECTED_ARCHIVE_MD5,
                "extracted_utc": datetime.now(timezone.utc).isoformat(),
                "members": extracted,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
