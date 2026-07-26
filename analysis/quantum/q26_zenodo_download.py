"""Stage the public Q26 temperature-trajectory source files.

The high-temperature targets must not be downloaded until the final Q26
protocol has been frozen.  This downloader verifies the immutable Zenodo
checksums but does not parse or display any numerical values.
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import urllib.request


HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "public_data" / "q26_temperature_ara9"
BASE = "https://zenodo.org/records/14880901/files"

FILES = {
    "development": {
        "SuppFigure9.csv": "d4d5b1bbf74a82be3077e8aa0166da92",
        "SuppFigure3a.csv": "8c6e99f38fc3b01e914836babbb67b2c",
        "SuppFigure3b.csv": "2eee4bfb54b3a367a8c282ac94314822",
        "SuppFigure3c.csv": "b36b34600e322813f18da621d4c2989a",
    },
    "target": {
        "SuppFigure10.csv": "9a9e3abac0ee8f80535e17ec72313919",
    },
}


def md5(path: pathlib.Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(stage: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, expected in FILES[stage].items():
        destination = OUT / name
        if not destination.exists():
            request = urllib.request.Request(
                f"{BASE}/{name}?download=1",
                headers={"User-Agent": "ARA-Q26-reproduction/1.0"},
            )
            with urllib.request.urlopen(request, timeout=120) as response:
                destination.write_bytes(response.read())
        actual = md5(destination)
        if actual != expected:
            raise RuntimeError(
                f"{name}: checksum mismatch; expected {expected}, got {actual}"
            )
        print(f"{stage}: {name}: checksum verified ({actual})")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stage",
        choices=tuple(FILES),
        required=True,
        help="Download only the declared development or target partition.",
    )
    args = parser.parse_args()
    download(args.stage)


if __name__ == "__main__":
    main()
