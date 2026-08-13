#!/usr/bin/env python3
"""Acquire the two fresh public-source families used by frozen test T342.

Previously cached ARA datasets are intentionally not duplicated here.  Their
exact local hashes are recorded in the T342 source manifest.
"""

from __future__ import annotations

import hashlib
import urllib.request
import zipfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source_data"
COLD = SOURCE / "cold_room"
ACOUSTICS = SOURCE / "acoustics"

COLD_FILES = {
    "Raw.zip": (
        "https://zenodo.org/records/15130001/files/Raw.zip?download=1",
        "9af88d88cd9aba6f893e5e76eff2d3dd",
    ),
    "experiment_actions.csv": (
        "https://zenodo.org/records/15130001/files/experiment_actions.csv?download=1",
        "63507fe89c3ff8047baba0d279735a93",
    ),
}


def md5(path: Path) -> str:
    h = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".partial")
    request = urllib.request.Request(url, headers={"User-Agent": "ARA-T342-reproduction/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response, tmp.open("wb") as handle:
        while chunk := response.read(1 << 20):
            handle.write(chunk)
    tmp.replace(path)


def main() -> None:
    for name, (url, expected_md5) in COLD_FILES.items():
        path = COLD / name
        if not path.exists() or md5(path) != expected_md5:
            print(f"downloading {name}")
            download(url, path)
        actual = md5(path)
        if actual != expected_md5:
            raise RuntimeError(f"MD5 mismatch for {name}: {actual} != {expected_md5}")

    raw_dir = COLD / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(COLD / "Raw.zip") as archive:
        archive.extractall(raw_dir)

    urls_file = SOURCE / "ACOUSTIC_URLS.txt"
    urls = [line.strip() for line in urls_file.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
    for url in urls:
        path = ACOUSTICS / url.rsplit("/", 1)[-1]
        if not path.exists() or path.stat().st_size == 0:
            print(f"downloading {path.name}")
            download(url, path)

    print(f"ready: {len(list(raw_dir.glob('SENSOR*.CSV')))} cold-room files, {len(list(ACOUSTICS.glob('*.wav')))} acoustic files")


if __name__ == "__main__":
    main()
