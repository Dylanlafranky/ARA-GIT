"""Download, verify and extract the frozen Q38 public target archive."""

from __future__ import annotations

import hashlib
import pathlib
import shutil
import urllib.request
import zipfile


HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "public_data" / "q38_fixed_anchor_mimic"
NAME = "unnati_submit_12_pure_mimic.hdf5.zip"
HDF_NAME = "unnati_submit_12_pure_mimic.hdf5"
URL = f"https://zenodo.org/records/16753415/files/{NAME}?download=1"
EXPECTED_MD5 = "04477abdac1849dd034576c0dbb685cb"


def md5(path: pathlib.Path) -> str:
    value = hashlib.md5()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def download() -> pathlib.Path:
    OUT.mkdir(parents=True, exist_ok=True)
    destination = OUT / NAME
    if not destination.exists():
        partial = destination.with_suffix(destination.suffix + ".part")
        existing = partial.stat().st_size if partial.exists() else 0
        request = urllib.request.Request(
            URL,
            headers={
                "User-Agent": "ARA-Q38-reproduction/1.0",
                **({"Range": f"bytes={existing}-"} if existing else {}),
            },
        )
        with urllib.request.urlopen(request, timeout=180) as response:
            status = getattr(response, "status", None)
            append = bool(existing and status == 206)
            mode = "ab" if append else "wb"
            print(
                f"downloading from byte {existing}"
                if append
                else "downloading from byte 0",
                flush=True,
            )
            with partial.open(mode) as target:
                shutil.copyfileobj(response, target, length=8 * 1024 * 1024)
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
        member = zipped.getinfo(HDF_NAME)
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
    extract(download())


if __name__ == "__main__":
    main()
