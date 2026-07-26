"""Download and verify the frozen Q27 public quantum-network target.

Source:
    Akhouri, Shandera and Henry (2025)
    Dataset for 6-14 qubits evolving on network with varying connectivity
    DOI: 10.5281/zenodo.16753415

The protocol and checksum were frozen before this downloader was executed.
The archive is intentionally excluded from git; rerunning this script restores
the exact source byte-for-byte.
"""

from __future__ import annotations

import hashlib
import pathlib
import shutil
import urllib.request
import zipfile


HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "public_data" / "q27_network_reconstruction"
NAME = "unnati_submit_12_pure_random.hdf5.zip"
URL = f"https://zenodo.org/records/16753415/files/{NAME}?download=1"
EXPECTED_MD5 = "06b6b278c4ce1e8ce14d2d662f0dc9dc"


def md5(path: pathlib.Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download() -> pathlib.Path:
    OUT.mkdir(parents=True, exist_ok=True)
    destination = OUT / NAME
    if not destination.exists():
        partial = destination.with_suffix(destination.suffix + ".part")
        existing = partial.stat().st_size if partial.exists() else 0
        headers = {"User-Agent": "ARA-Q27-reproduction/1.0"}
        if existing:
            headers["Range"] = f"bytes={existing}-"
        request = urllib.request.Request(
            URL,
            headers=headers,
        )
        with urllib.request.urlopen(request, timeout=180) as response:
            status = getattr(response, "status", None)
            append = existing > 0 and status == 206
            if existing and not append:
                existing = 0
            mode = "ab" if append else "wb"
            print(
                f"downloading from byte {existing}"
                if append
                else "downloading from byte 0"
            )
            target = partial.open(mode)
            try:
                shutil.copyfileobj(response, target, length=8 * 1024 * 1024)
            finally:
                target.close()
        partial.replace(destination)

    actual = md5(destination)
    if actual != EXPECTED_MD5:
        raise RuntimeError(
            f"{NAME}: checksum mismatch; expected {EXPECTED_MD5}, got {actual}"
        )
    print(f"{NAME}: checksum verified ({actual})")
    return destination


def extract(archive: pathlib.Path) -> list[pathlib.Path]:
    with zipfile.ZipFile(archive) as zipped:
        unsafe = [
            name
            for name in zipped.namelist()
            if pathlib.Path(name).is_absolute() or ".." in pathlib.Path(name).parts
        ]
        if unsafe:
            raise RuntimeError(f"Unsafe archive members: {unsafe}")
        zipped.extractall(OUT)

    extracted = sorted(
        path for path in OUT.rglob("*") if path.is_file() and path != archive
    )
    if not extracted:
        raise RuntimeError("Archive contained no files")
    for path in extracted:
        print(f"extracted: {path.relative_to(HERE)} ({path.stat().st_size} bytes)")
    return extracted


def main() -> None:
    archive = download()
    extract(archive)


if __name__ == "__main__":
    main()
