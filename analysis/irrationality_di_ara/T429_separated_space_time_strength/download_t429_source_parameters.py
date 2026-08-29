from __future__ import annotations

import hashlib
import json
import pathlib
import urllib.request


ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "source_parameters"

EVENTS = {
    "GW150914": "https://gwosc.org/eventapi/json/GWTC-1-confident/GW150914/v3",
    "GW170104": "https://gwosc.org/eventapi/json/GWTC-1-confident/GW170104/v2",
    "GW170608": "https://gwosc.org/eventapi/json/GWTC-1-confident/GW170608/v3",
    "GW170809": "https://gwosc.org/eventapi/json/GWTC-1-confident/GW170809/v1",
    "GW170814": "https://gwosc.org/eventapi/json/GWTC-1-confident/GW170814/v3",
    "GW170818": "https://gwosc.org/eventapi/json/GWTC-1-confident/GW170818/v1",
}

FIELDS = (
    "GPS",
    "mass_1_source",
    "mass_1_source_lower",
    "mass_1_source_upper",
    "mass_2_source",
    "mass_2_source_lower",
    "mass_2_source_upper",
    "total_mass_source",
    "chirp_mass_source",
    "chirp_mass",
    "luminosity_distance",
    "redshift",
    "network_matched_filter_snr",
    "final_mass_source",
)


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for common_name, url in EVENTS.items():
        request = urllib.request.Request(url, headers={"User-Agent": "ARA-T429/1.0"})
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read()
        raw_path = OUT / f"{common_name}_GWOSC_GWTC1.json"
        raw_path.write_bytes(raw)
        payload = json.loads(raw)
        key, event = next(iter(payload["events"].items()))
        row = {"event": common_name, "catalog_key": key, "source_url": url}
        for field in FIELDS:
            row[field] = event.get(field)
        row["raw_sha256"] = sha256(raw_path)
        rows.append(row)
    manifest = {
        "source": "GWOSC GWTC-1-confident compact event JSON",
        "retrieved_by": pathlib.Path(__file__).name,
        "events": rows,
    }
    (ROOT / "T429_SOURCE_PARAMETERS_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
