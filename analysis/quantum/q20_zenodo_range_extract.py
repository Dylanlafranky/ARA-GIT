#!/usr/bin/env python3
"""Selectively extract Q20 members from the immutable Willow Zenodo ZIP.

The source archive is 5.7 GB. This script reads its ZIP central directory with
an HTTP range request, downloads only explicitly requested members, verifies
their CRC-32 values, and writes a source manifest. It uses only Python's
standard library.
"""

from __future__ import annotations

import argparse
import binascii
import json
import pathlib
import struct
import urllib.request
import zlib
from dataclasses import dataclass
from datetime import datetime, timezone


RECORD_ID = 13273331
RECORD_API = f"https://zenodo.org/api/records/{RECORD_ID}"
ARCHIVE_KEY = "google_105Q_surface_code_d3_d5_d7.zip"
EXPECTED_ARCHIVE_SIZE = 5_716_907_033
EXPECTED_ARCHIVE_MD5 = "21fa6ad35b395d838ebcdbc92e364a12"
TAIL_BYTES = 10 * 1024 * 1024

DEFAULT_MEMBERS = (
    "google_105Q_surface_code_d3_d5_d7/d5_at_q4_7/X/r13/metadata.json",
    "google_105Q_surface_code_d3_d5_d7/d5_at_q4_7/X/r13/circuit_ideal.stim",
    "google_105Q_surface_code_d3_d5_d7/d5_at_q4_7/X/r13/detection_events.b8",
    "google_105Q_surface_code_d3_d5_d7/d5_at_q4_7/X/r13/obs_flips_actual.b8",
    "google_105Q_surface_code_d3_d5_d7/d5_at_q4_7/X/r30/metadata.json",
    "google_105Q_surface_code_d3_d5_d7/d5_at_q4_7/X/r30/circuit_ideal.stim",
    "google_105Q_surface_code_d3_d5_d7/d5_at_q4_7/X/r30/detection_events.b8",
    "google_105Q_surface_code_d3_d5_d7/d5_at_q4_7/X/r30/obs_flips_actual.b8",
    "google_105Q_surface_code_d3_d5_d7/d5_at_q4_7/Z/r13/metadata.json",
    "google_105Q_surface_code_d3_d5_d7/d5_at_q4_7/Z/r13/circuit_ideal.stim",
    "google_105Q_surface_code_d3_d5_d7/d5_at_q4_7/Z/r13/detection_events.b8",
    "google_105Q_surface_code_d3_d5_d7/d5_at_q4_7/Z/r13/obs_flips_actual.b8",
    "google_105Q_surface_code_d3_d5_d7/d5_at_q4_7/Z/r30/metadata.json",
    "google_105Q_surface_code_d3_d5_d7/d5_at_q4_7/Z/r30/circuit_ideal.stim",
    "google_105Q_surface_code_d3_d5_d7/d5_at_q4_7/Z/r30/detection_events.b8",
    "google_105Q_surface_code_d3_d5_d7/d5_at_q4_7/Z/r30/obs_flips_actual.b8",
)


@dataclass(frozen=True)
class ZipMember:
    name: str
    compression: int
    crc32: int
    compressed_size: int
    uncompressed_size: int
    local_offset: int


def http_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "ARA-Q20/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def http_range(url: str, start: int, end: int) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "Range": f"bytes={start}-{end}",
            "User-Agent": "ARA-Q20/1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        data = response.read()
        expected = end - start + 1
        if len(data) != expected:
            raise RuntimeError(
                f"Range {start}-{end} returned {len(data)} bytes; expected {expected}."
            )
        return data


def archive_metadata() -> tuple[str, int, str]:
    record = http_json(RECORD_API)
    for item in record["files"]:
        if item["key"] == ARCHIVE_KEY:
            size = int(item["size"])
            checksum = item["checksum"]
            if size != EXPECTED_ARCHIVE_SIZE:
                raise RuntimeError(f"Unexpected archive size: {size}")
            if checksum != f"md5:{EXPECTED_ARCHIVE_MD5}":
                raise RuntimeError(f"Unexpected archive checksum: {checksum}")
            return item["links"]["self"], size, checksum
    raise RuntimeError(f"Archive not found in Zenodo record: {ARCHIVE_KEY}")


def zip64_value(
    extra: bytes,
    uncompressed_size: int,
    compressed_size: int,
    local_offset: int,
) -> tuple[int, int, int]:
    position = 0
    while position + 4 <= len(extra):
        tag, size = struct.unpack_from("<HH", extra, position)
        payload = extra[position + 4 : position + 4 + size]
        position += 4 + size
        if tag != 1:
            continue
        cursor = 0
        if uncompressed_size == 0xFFFFFFFF:
            uncompressed_size = struct.unpack_from("<Q", payload, cursor)[0]
            cursor += 8
        if compressed_size == 0xFFFFFFFF:
            compressed_size = struct.unpack_from("<Q", payload, cursor)[0]
            cursor += 8
        if local_offset == 0xFFFFFFFF:
            local_offset = struct.unpack_from("<Q", payload, cursor)[0]
        break
    return uncompressed_size, compressed_size, local_offset


def central_directory(url: str, archive_size: int) -> dict[str, ZipMember]:
    tail_start = archive_size - TAIL_BYTES
    tail = http_range(url, tail_start, archive_size - 1)
    zip64_index = tail.rfind(b"PK\x06\x06")
    if zip64_index < 0:
        raise RuntimeError("ZIP64 end-of-central-directory record was not found.")
    zip64 = struct.unpack_from("<4sQ2H2I4Q", tail, zip64_index)
    entry_count = int(zip64[7])
    central_size = int(zip64[8])
    central_offset = int(zip64[9])
    central_end = central_offset + central_size
    if central_offset >= tail_start and central_end <= archive_size:
        central = tail[central_offset - tail_start : central_end - tail_start]
    else:
        central = http_range(url, central_offset, central_end - 1)

    members: dict[str, ZipMember] = {}
    position = 0
    while position + 46 <= len(central):
        if central[position : position + 4] != b"PK\x01\x02":
            break
        header = struct.unpack_from("<4s6H3I5H2I", central, position)
        compression = int(header[4])
        crc32 = int(header[7])
        compressed_size = int(header[8])
        uncompressed_size = int(header[9])
        name_length = int(header[10])
        extra_length = int(header[11])
        comment_length = int(header[12])
        local_offset = int(header[16])
        name_start = position + 46
        name_end = name_start + name_length
        extra_end = name_end + extra_length
        name = central[name_start:name_end].decode("utf-8")
        extra = central[name_end:extra_end]
        uncompressed_size, compressed_size, local_offset = zip64_value(
            extra, uncompressed_size, compressed_size, local_offset
        )
        members[name] = ZipMember(
            name=name,
            compression=compression,
            crc32=crc32,
            compressed_size=compressed_size,
            uncompressed_size=uncompressed_size,
            local_offset=local_offset,
        )
        position += 46 + name_length + extra_length + comment_length

    if len(members) != entry_count:
        raise RuntimeError(
            f"Parsed {len(members)} ZIP members; central directory declares {entry_count}."
        )
    return members


def decompress(member: ZipMember, payload: bytes) -> bytes:
    if member.compression == 0:
        output = payload
    elif member.compression == 8:
        output = zlib.decompress(payload, -15)
    else:
        raise RuntimeError(
            f"Unsupported compression method {member.compression}: {member.name}"
        )
    if len(output) != member.uncompressed_size:
        raise RuntimeError(
            f"Size mismatch for {member.name}: "
            f"{len(output)} != {member.uncompressed_size}"
        )
    actual_crc = binascii.crc32(output) & 0xFFFFFFFF
    if actual_crc != member.crc32:
        raise RuntimeError(
            f"CRC mismatch for {member.name}: {actual_crc:08x} != {member.crc32:08x}"
        )
    return output


def extract_member(url: str, member: ZipMember) -> bytes:
    header = http_range(url, member.local_offset, member.local_offset + 65_535)
    local = struct.unpack_from("<4s5H3I2H", header, 0)
    if local[0] != b"PK\x03\x04":
        raise RuntimeError(f"Invalid local header: {member.name}")
    name_length = int(local[9])
    extra_length = int(local[10])
    payload_offset = member.local_offset + 30 + name_length + extra_length
    payload_end = payload_offset + member.compressed_size - 1
    available_start = 30 + name_length + extra_length
    available_end = available_start + member.compressed_size
    if available_end <= len(header):
        payload = header[available_start:available_end]
    else:
        payload = http_range(url, payload_offset, payload_end)
    return decompress(member, payload)


def safe_output_path(output_root: pathlib.Path, member_name: str) -> pathlib.Path:
    relative = pathlib.PurePosixPath(member_name)
    parts = relative.parts[1:] if len(relative.parts) > 1 else relative.parts
    if any(part in ("", ".", "..") for part in parts):
        raise RuntimeError(f"Unsafe ZIP path: {member_name}")
    return output_root.joinpath(*parts)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=pathlib.Path(__file__).parent / "public_data" / "q20_willow_105q",
    )
    parser.add_argument(
        "--member",
        action="append",
        default=[],
        help="Exact archive member to extract; repeat as needed.",
    )
    parser.add_argument(
        "--list",
        metavar="SUBSTRING",
        help="List matching archive members without extracting them.",
    )
    args = parser.parse_args()

    url, archive_size, archive_checksum = archive_metadata()
    members = central_directory(url, archive_size)
    if args.list is not None:
        for name, member in sorted(members.items()):
            if args.list in name:
                print(
                    f"{name}\t{member.compressed_size}\t{member.uncompressed_size}"
                )
        return

    selected = tuple(args.member) if args.member else DEFAULT_MEMBERS
    missing = [name for name in selected if name not in members]
    if missing:
        raise RuntimeError(f"Members absent from archive: {missing}")

    extracted = []
    for name in selected:
        member = members[name]
        output = safe_output_path(args.output, name)
        output.parent.mkdir(parents=True, exist_ok=True)
        data = extract_member(url, member)
        output.write_bytes(data)
        extracted.append(
            {
                "name": name,
                "output": str(output.relative_to(args.output)),
                "compression": member.compression,
                "crc32": f"{member.crc32:08x}",
                "compressed_size": member.compressed_size,
                "uncompressed_size": member.uncompressed_size,
                "local_offset": member.local_offset,
            }
        )
        print(f"verified {name} -> {output}")

    manifest = {
        "source_title": 'Data for "Quantum error correction below the surface code threshold"',
        "source_doi": "10.5281/zenodo.13273331",
        "record_id": RECORD_ID,
        "archive_key": ARCHIVE_KEY,
        "archive_size": archive_size,
        "archive_checksum": archive_checksum,
        "range_extraction_note": (
            "Archive-wide MD5 is locked from Zenodo metadata; each selectively "
            "extracted member is verified against its ZIP central-directory CRC-32."
        ),
        "extracted_utc": datetime.now(timezone.utc).isoformat(),
        "members": extracted,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    manifest_path = args.output / "SOURCE_MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {manifest_path}")


if __name__ == "__main__":
    main()
