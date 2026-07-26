"""Extract the already-checksummed Q27 archive outside short command windows."""

from __future__ import annotations

import pathlib
import zipfile


HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / "public_data" / "q27_network_reconstruction"
ARCHIVE = DATA / "unnati_submit_12_pure_random.hdf5.zip"
EXPECTED_SIZE = 3_452_716_320


def main() -> None:
    with zipfile.ZipFile(ARCHIVE) as zipped:
        info = zipped.getinfo("unnati_submit_12_pure_random.hdf5")
        if info.file_size != EXPECTED_SIZE:
            raise RuntimeError(
                f"Unexpected extracted size: {info.file_size} != {EXPECTED_SIZE}"
            )
        zipped.extract(info, DATA)

    target = DATA / info.filename
    if target.stat().st_size != EXPECTED_SIZE:
        raise RuntimeError(
            f"Truncated extraction: {target.stat().st_size} != {EXPECTED_SIZE}"
        )


if __name__ == "__main__":
    main()
