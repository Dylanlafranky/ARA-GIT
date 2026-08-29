from __future__ import annotations

import hashlib
import json
import pathlib
import urllib.request


ROOT = pathlib.Path(__file__).resolve().parent
MANIFEST = ROOT / "T427_SOURCE_MANIFEST_PRE_DOWNLOAD.json"
CACHE = pathlib.Path(r"F:\SystemFormulaFolder\_data_cache\GWOSC\T427")
OUTPUT = ROOT / "results" / "T427_SOURCE_AUDIT.json"


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    spec = json.loads(MANIFEST.read_text(encoding="utf-8"))
    CACHE.mkdir(parents=True, exist_ok=True)
    audit: list[dict[str, object]] = []

    for event in spec["events"]:
        event_dir = CACHE / event["event"]
        event_dir.mkdir(parents=True, exist_ok=True)
        for detector, url in event["files"].items():
            filename = pathlib.PurePosixPath(url.split("?", 1)[0]).name
            target = event_dir / filename
            if not target.exists() or target.stat().st_size == 0:
                print(f"Downloading {event['event']} {detector}: {url}", flush=True)
                request = urllib.request.Request(
                    url,
                    headers={"User-Agent": "ARA-T427-public-data-validation/1.0"},
                )
                with urllib.request.urlopen(request, timeout=120) as response:
                    target.write_bytes(response.read())
            audit.append(
                {
                    "event": event["event"],
                    "role": event["role"],
                    "release": event["release"],
                    "gps": event["gps"],
                    "detector": detector,
                    "url": url,
                    "local_path": target.as_posix(),
                    "bytes": target.stat().st_size,
                    "sha256": sha256(target),
                }
            )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
