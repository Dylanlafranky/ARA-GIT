"""Extract the Q54 hardware-data subset from a remote ZIP using HTTP ranges.

The full Zenodo archive is about 297 MB.  Q54 needs the recorded time-domain
files in Fig. 6 and Fig. 8, not the simulated spectra or rendered figures.
This script reads the ZIP central directory, downloads only those members,
checks their ZIP CRCs, and writes a reproducible manifest.
"""

from __future__ import annotations

import argparse
import binascii
import hashlib
import json
import struct
import urllib.request
import zlib
from pathlib import Path


RECORD_ID = 8004359
ARCHIVE_URL = (
    "https://zenodo.org/api/records/8004359/files/"
    "Source%20Data%20_%20full_version.zip/content"
)
ARCHIVE_SIZE = 297_216_848
ARCHIVE_MD5 = "ced1ed4af893ad064045900903e19a17"
TOP = "Source Data _ full_version/"


def fetch_range(start: int, end: int) -> bytes:
    request = urllib.request.Request(
        ARCHIVE_URL,
        headers={
            "Range": f"bytes={start}-{end}",
            "User-Agent": "ARA-Q54-reproduction/1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = response.read()
        status = getattr(response, "status", None)
        if status not in (200, 206):
            raise RuntimeError(f"Unexpected HTTP status {status}")
        expected = end - start + 1
        if len(payload) != expected:
            raise RuntimeError(
                f"Range {start}-{end} returned {len(payload)} bytes, "
                f"expected {expected}"
            )
        return payload


def central_entries() -> list[dict]:
    tail_size = min(65_536, ARCHIVE_SIZE)
    tail_start = ARCHIVE_SIZE - tail_size
    tail = fetch_range(tail_start, ARCHIVE_SIZE - 1)
    eocd = tail.rfind(b"PK\x05\x06")
    if eocd < 0:
        raise RuntimeError("ZIP end-of-central-directory record not found")

    fields = struct.unpack_from("<4s4H2LH", tail, eocd)
    expected_entries = fields[4]
    cd_size = fields[5]
    cd_offset = fields[6]
    central = fetch_range(cd_offset, cd_offset + cd_size - 1)

    entries: list[dict] = []
    pos = 0
    while central[pos : pos + 4] == b"PK\x01\x02":
        header = struct.unpack_from("<4s6H3L5H2L", central, pos)
        method = header[4]
        crc32 = header[7]
        compressed_size = header[8]
        uncompressed_size = header[9]
        name_len = header[10]
        extra_len = header[11]
        comment_len = header[12]
        local_offset = header[16]
        name = central[pos + 46 : pos + 46 + name_len].decode(
            "utf-8", errors="replace"
        )
        entries.append(
            {
                "name": name,
                "method": method,
                "crc32": crc32,
                "compressed_size": compressed_size,
                "uncompressed_size": uncompressed_size,
                "local_offset": local_offset,
            }
        )
        pos += 46 + name_len + extra_len + comment_len

    if len(entries) != expected_entries:
        raise RuntimeError(
            f"Parsed {len(entries)} central entries, expected {expected_entries}"
        )
    return entries


def wanted(name: str) -> bool:
    lower = name.lower()
    if lower.endswith("/"):
        return False
    if lower.startswith((TOP + "Fig6/").lower()) and lower.endswith(
        (".txt", ".nb")
    ):
        return True
    if lower.startswith((TOP + "Fig8/Fig8c/").lower()) and lower.endswith(
        (".dat", ".nb")
    ):
        return True
    return False


def extract_entry(entry: dict, output_root: Path) -> dict:
    local_offset = entry["local_offset"]
    fixed = fetch_range(local_offset, local_offset + 29)
    if fixed[:4] != b"PK\x03\x04":
        raise RuntimeError(f"Bad local header for {entry['name']}")
    local = struct.unpack("<4s5H3L2H", fixed)
    name_len = local[9]
    extra_len = local[10]
    data_start = local_offset + 30 + name_len + extra_len
    compressed_size = entry["compressed_size"]
    compressed = fetch_range(data_start, data_start + compressed_size - 1)

    if entry["method"] == 0:
        payload = compressed
    elif entry["method"] == 8:
        payload = zlib.decompress(compressed, -15)
    else:
        raise RuntimeError(
            f"Unsupported ZIP method {entry['method']} for {entry['name']}"
        )

    if len(payload) != entry["uncompressed_size"]:
        raise RuntimeError(f"Size mismatch for {entry['name']}")
    crc32 = binascii.crc32(payload) & 0xFFFFFFFF
    if crc32 != entry["crc32"]:
        raise RuntimeError(f"CRC mismatch for {entry['name']}")

    relative = Path(entry["name"][len(TOP) :])
    destination = output_root / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    return {
        "archive_path": entry["name"],
        "local_path": str(destination),
        "size": len(payload),
        "crc32": f"{crc32:08x}",
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Directory that receives the selected Fig6/Fig8 files.",
    )
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    entries = central_entries()
    selected = [entry for entry in entries if wanted(entry["name"])]
    extracted = [extract_entry(entry, args.output) for entry in selected]

    manifest = {
        "record_id": RECORD_ID,
        "doi": "10.5281/zenodo.8004359",
        "archive_url": ARCHIVE_URL,
        "archive_size": ARCHIVE_SIZE,
        "archive_md5": ARCHIVE_MD5,
        "selection": [
            "Fig6/**/*.txt",
            "Fig6/**/*.nb",
            "Fig8/Fig8c/**/*.dat",
            "Fig8/Fig8c/**/*.nb",
        ],
        "central_entry_count": len(entries),
        "extracted_file_count": len(extracted),
        "extracted_bytes": sum(item["size"] for item in extracted),
        "files": extracted,
    }
    manifest_path = args.output / "Q54_ZENODO_SUBSET_MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps({k: v for k, v in manifest.items() if k != "files"}, indent=2))


if __name__ == "__main__":
    main()
