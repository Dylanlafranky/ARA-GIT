from __future__ import annotations

import hashlib
import json
import pathlib
import urllib.request


ROOT = pathlib.Path(__file__).resolve().parent
MANIFEST = ROOT / "T430_SOURCE_MANIFEST_PRE_DOWNLOAD.json"
RESULTS = ROOT / "results"
AUDIT = RESULTS / "T430_SOURCE_AUDIT.json"


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch_json(url: str) -> dict[str, object]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "ARA-T430-public-data-validation/1.0"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def download(url: str, target: pathlib.Path) -> None:
    if target.exists() and target.stat().st_size > 0:
        return
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "ARA-T430-public-data-validation/1.0"},
    )
    with urllib.request.urlopen(request, timeout=180) as response, target.open("wb") as handle:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)


def preferred_parameter_block(event_record: dict[str, object]) -> dict[str, object]:
    parameters = event_record.get("parameters", {})
    if not isinstance(parameters, dict):
        return {}
    preferred = [
        value for value in parameters.values()
        if isinstance(value, dict) and value.get("is_preferred") is True
    ]
    if preferred:
        return preferred[0]
    pe = [
        value for value in parameters.values()
        if isinstance(value, dict) and value.get("pipeline_type") == "pe"
    ]
    return pe[0] if pe else {}


def main() -> None:
    spec = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cache = pathlib.Path(spec["raw_cache"])
    cache.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    audit: list[dict[str, object]] = []

    for frozen in spec["confirmation_events"]:
        payload = fetch_json(str(frozen["event_json"]))
        records = payload.get("events", {})
        if not isinstance(records, dict) or len(records) != 1:
            raise ValueError(f"Unexpected event payload for {frozen['event']}")
        uid, event_record = next(iter(records.items()))
        if not isinstance(event_record, dict):
            raise TypeError(f"Invalid event record for {frozen['event']}")
        if str(event_record.get("commonName")) != str(frozen["event"]):
            raise ValueError(f"Event identity mismatch for {frozen['event']}: {uid}")
        if abs(float(event_record.get("GPS")) - float(frozen["gps"])) > 1e-6:
            raise ValueError(f"GPS mismatch for {frozen['event']}")

        event_dir = cache / str(frozen["event"])
        event_dir.mkdir(parents=True, exist_ok=True)
        raw_json = event_dir / f"{frozen['event']}_eventapi.json"
        raw_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        strains = event_record.get("strain", [])
        chosen: dict[str, dict[str, object]] = {}
        for item in strains if isinstance(strains, list) else []:
            if not isinstance(item, dict):
                continue
            if (
                item.get("detector") in {"H1", "L1"}
                and int(item.get("sampling_rate", 0)) == 4096
                and int(item.get("duration", 0)) == 32
                and str(item.get("format", "")).lower() == "hdf5"
            ):
                chosen[str(item["detector"])] = item
        if set(chosen) != {"H1", "L1"}:
            raise ValueError(f"Missing 32 s, 4 kHz H1/L1 HDF5 files for {frozen['event']}")

        parameter = preferred_parameter_block(event_record)
        parameter_out = {
            key: parameter.get(key)
            for key in (
                "mass_1_source", "mass_2_source", "chirp_mass_source",
                "redshift", "luminosity_distance", "network_matched_filter_snr",
                "final_mass_source", "E_rad",
            )
        }
        parameter_path = event_dir / f"{frozen['event']}_preferred_parameters.json"
        parameter_path.write_text(json.dumps(parameter_out, indent=2), encoding="utf-8")

        for detector in ("H1", "L1"):
            url = str(chosen[detector]["url"])
            filename = pathlib.PurePosixPath(url.split("?", 1)[0]).name
            target = event_dir / filename
            print(f"Downloading {frozen['event']} {detector}: {url}", flush=True)
            download(url, target)
            audit.append(
                {
                    "event": frozen["event"],
                    "uid": uid,
                    "role": frozen["role"],
                    "gps": frozen["gps"],
                    "detector": detector,
                    "url": url,
                    "local_path": target.as_posix(),
                    "bytes": target.stat().st_size,
                    "sha256": sha256(target),
                    "event_json_path": raw_json.as_posix(),
                    "event_json_sha256": sha256(raw_json),
                    "parameters_path": parameter_path.as_posix(),
                    "parameters_sha256": sha256(parameter_path),
                }
            )

    AUDIT.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(f"Wrote {AUDIT}")


if __name__ == "__main__":
    main()
