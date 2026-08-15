#!/usr/bin/env python3
"""Download and verify the public source used by T385.

The BUAP `Last` endpoint is mutable.  This script refuses to describe changed
content as the frozen T385 source: it reports the new hash and exits non-zero.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import urllib.request
from pathlib import Path


URL = "https://ciiec.buap.mx/Muon-Decay/Datos/MD10000Last.csv"
EXPECTED_SHA256 = "C2DC1E012FBDF0F3C5EC305E2D8E4DD1D87B05DF5CBA39B492189C0F7D5454CD"
DEFAULT_OUT = Path(
    r"F:\SystemFormulaFolder\DataTEsted(TOBEDELETEDBEFOREGIT)\muon_buap\MD10000Last.csv"
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--keep-mismatch", action="store_true")
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.out.with_suffix(args.out.suffix + ".download")
    with urllib.request.urlopen(URL, timeout=180) as response, temporary.open("wb") as handle:
        shutil.copyfileobj(response, handle)
    actual = sha256(temporary)
    if actual != EXPECTED_SHA256:
        if args.keep_mismatch:
            temporary.replace(args.out)
        else:
            temporary.unlink(missing_ok=True)
        print(f"HASH MISMATCH\nexpected {EXPECTED_SHA256}\nactual   {actual}")
        print("The mutable BUAP Last endpoint has changed; do not call it the frozen T385 source.")
        return 2
    temporary.replace(args.out)
    print(f"verified {actual}  {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
