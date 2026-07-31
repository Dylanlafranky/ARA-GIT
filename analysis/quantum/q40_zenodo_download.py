"""Download, verify and extract the frozen Q40 public target archive."""

from __future__ import annotations

import hashlib
import pathlib
import re
import shutil
import urllib.request
import zipfile


HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "public_data" / "q40_return_flow_inhomo_v1_greedy"
NAME = "unnati_submit_12_inhomo_v1_greedy.hdf5.zip"
HDF_NAME = "unnati_submit_12_inhomo_v1_greedy.hdf5"
URL = f"https://zenodo.org/records/16753415/files/{NAME}?download=1"
EXPECTED_MD5 = "c04eb02b1766d9f83fb0240689d209a5"
CHUNK_BYTES = 16 * 1024 * 1024


def md5(path: pathlib.Path) -> str:
    value = hashlib.md5()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def download() -> pathlib.Path | None:
    OUT.mkdir(parents=True, exist_ok=True)
    destination = OUT / NAME
    partial = destination.with_suffix(destination.suffix + ".part")
    if not destination.exists():
        existing = partial.stat().st_size if partial.exists() else 0
        end = existing + CHUNK_BYTES - 1
        request = urllib.request.Request(
            URL,
            headers={
                "User-Agent": "ARA-Q40-reproduction/1.0",
                "Range": f"bytes={existing}-{end}",
            },
        )
        with urllib.request.urlopen(request, timeout=180) as response:
            status = getattr(response, "status", None)
            content_range = response.headers.get("Content-Range", "")
            match = re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)", content_range)
            if status != 206 or match is None:
                raise RuntimeError(
                    f"Server did not honor frozen range request: "
                    f"status={status}, Content-Range={content_range!r}"
                )
            start_returned, end_returned, total = map(int, match.groups())
            if start_returned != existing:
                raise RuntimeError(
                    f"Unexpected returned range start {start_returned}; "
                    f"expected {existing}"
                )
            expected_length = end_returned - start_returned + 1
            with partial.open("ab") as target:
                copied = 0
                while chunk := response.read(8 * 1024 * 1024):
                    target.write(chunk)
                    copied += len(chunk)
            if copied != expected_length:
                raise RuntimeError(
                    f"Short range response: expected {expected_length}, got {copied}"
                )
        current = partial.stat().st_size
        print(f"downloaded {current}/{total} bytes", flush=True)
        if current < total:
            return None
        if current != total:
            raise RuntimeError(f"Partial size {current} exceeds expected {total}")
        partial.replace(destination)
    actual = md5(destination)
    if actual != EXPECTED_MD5:
        raise RuntimeError(
            f"{NAME}: checksum mismatch; expected {EXPECTED_MD5}, got {actual}"
        )
    print(f"{NAME}: checksum verified ({actual})", flush=True)
    return destination


def extract(archive: pathlib.Path) -> pathlib.Path:
    destination = OUT / HDF_NAME
    with zipfile.ZipFile(archive) as zipped:
        matches = [
            item
            for item in zipped.infolist()
            if not item.is_dir() and pathlib.Path(item.filename).name == HDF_NAME
        ]
        if len(matches) != 1:
            raise RuntimeError(f"Expected one {HDF_NAME}, found {len(matches)}")
        member = matches[0]
        if destination.exists() and destination.stat().st_size == member.file_size:
            print(f"{HDF_NAME}: already extracted", flush=True)
            return destination
        if destination.exists():
            destination.unlink()
        member_path = pathlib.Path(member.filename)
        if member_path.is_absolute() or ".." in member_path.parts:
            raise RuntimeError(f"Unsafe archive member: {member.filename}")
        with zipped.open(member) as source, destination.open("wb") as target:
            shutil.copyfileobj(source, target, length=8 * 1024 * 1024)
    print(f"{HDF_NAME}: extracted ({destination.stat().st_size} bytes)", flush=True)
    return destination


def main() -> None:
    archive = download()
    if archive is not None:
        extract(archive)


if __name__ == "__main__":
    main()
