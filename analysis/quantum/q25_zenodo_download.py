"""Download the checksum-locked Q25 source files without printing their values."""

from __future__ import annotations

import hashlib
from pathlib import Path
from urllib.request import Request, urlopen


HERE = Path(__file__).resolve().parent
SOURCE_DIR = HERE / "public_data" / "q25_atomic_bell"
PROTOCOL = HERE / "Q25_ARA9_BLIND_MISSING_CUT_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q25_ARA9_BLIND_MISSING_CUT_PROTOCOL_v1_FROZEN.sha256"
BASE_URL = "https://zenodo.org/records/4604775/files"

FILES = {
    "Fig3a_dm.csv": "6d9c796a2fe5a1e28bf421ddf3854794",
    "Fig3b_dm_AA.csv": "fabd72f98052a53cddd230f5f43dcbb7",
    "Fig3b_dm_AD.csv": "098362b0cc4ea2a20c952f0f644ed3b2",
    "Fig3b_dm_DA.csv": "9b6f161cc046b92e614e7962c47904ff",
    "Fig3b_dm_DD.csv": "98b2c5070cee080eb10dc4ab413acb67",
    "figure4_dm_AA.csv": "a760fd823f7ca7413013e1edaf2a2537",
    "figure4_dm_AD.csv": "231ee28c4b140bfd12cdd85239160608",
    "figure4_dm_DA.csv": "c37febe660af215d25d5e64a68849619",
    "figure4_dm_DD.csv": "77266fe4df3be1c2792cfaa75881772c",
    "figure3_info.txt": "eef5910c2f36544704f0d987ae4dad7e",
    "figure4_info.txt": "8c8125a9e778da74bb7cbf12ee3b05c1",
}


def digest(path: Path, algorithm: str) -> str:
    hasher = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_protocol() -> str:
    expected = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    actual = digest(PROTOCOL, "sha256")
    if actual != expected:
        raise RuntimeError(f"Frozen protocol hash mismatch: {actual} != {expected}")
    return actual


def download_file(filename: str, expected_md5: str) -> str:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    destination = SOURCE_DIR / filename
    if destination.exists() and digest(destination, "md5") == expected_md5:
        return "verified-existing"

    request = Request(
        f"{BASE_URL}/{filename}?download=1",
        headers={"User-Agent": "ARA-Q25-reproduction/1.0"},
    )
    with urlopen(request, timeout=60) as response:
        payload = response.read()
    actual_md5 = hashlib.md5(payload).hexdigest()
    if actual_md5 != expected_md5:
        raise RuntimeError(
            f"Checksum mismatch for {filename}: {actual_md5} != {expected_md5}"
        )
    destination.write_bytes(payload)
    return "downloaded"


def main() -> None:
    protocol_hash = verify_protocol()
    print(f"Protocol verified: {protocol_hash}")
    for filename, expected_md5 in FILES.items():
        status = download_file(filename, expected_md5)
        print(f"{filename}: {status}; md5={expected_md5}")
    print(f"Source directory: {SOURCE_DIR}")
    print("No matrix values were displayed.")


if __name__ == "__main__":
    main()
