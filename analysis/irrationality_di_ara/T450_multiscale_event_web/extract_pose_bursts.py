"""Extract the frozen T450A pose bursts through public HTTP byte ranges."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import sys
from pathlib import Path

import h5py
import numpy as np


HERE = Path(__file__).resolve().parent
T448 = HERE.parent / "T448_fruitfly_lifecycle_tomography"
sys.path.insert(0, str(T448))
from remote_behavior_aggregate import HTTPRangeReader  # noqa: E402


FRACTIONS = (0.125, 0.375, 0.625, 0.875)
SECONDS = 60.0
DEVELOPMENT_DATES = {"20220217", "20220313", "20220326"}
HOLDOUT_DATE = "20220418"


def selected_files(catalog: dict) -> list[dict]:
    by_date: dict[str, list[dict]] = {}
    for item in catalog["files"]:
        if item.get("extension") != "h5":
            continue
        match = re.match(r"(\d{8})_cam\d+_flid\d+\.h5$", item["name"])
        if match:
            by_date.setdefault(match.group(1), []).append(item)
    selected: list[dict] = []
    for date in sorted(by_date):
        ordered = sorted(by_date[date], key=lambda row: row["name"])
        for item in (ordered[0], ordered[-1]):
            item = dict(item)
            item["date"] = date
            item["split"] = "development" if date in DEVELOPMENT_DATES else "holdout"
            selected.append(item)
    return selected


def decode_strings(values: np.ndarray) -> list[str]:
    return [value.decode() if isinstance(value, bytes) else str(value) for value in values]


def extract_one(item: dict, output_dir: Path) -> dict:
    reader = HTTPRangeReader(item["download_url"], int(item["size"]), block_size=1024 * 1024, max_blocks=96)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{Path(item['name']).stem}_T450A_pose_bursts.npz"
    arrays: dict[str, np.ndarray] = {}
    burst_meta: list[dict] = []
    with h5py.File(reader, "r") as handle:
        fps = float(np.asarray(handle.attrs["frames_per_second"]).ravel()[0])
        n_frames = int(handle["tracks"].shape[-1])
        frames_per_burst = int(round(SECONDS * fps))
        node_names = decode_strings(np.asarray(handle["node_names"]))
        behavior_names = decode_strings(np.asarray(handle["behavior_names"]))
        for index, fraction in enumerate(FRACTIONS):
            center = int(round((n_frames - 1) * fraction))
            start = max(0, center - frames_per_burst // 2)
            end = min(n_frames, start + frames_per_burst)
            start = max(0, end - frames_per_burst)
            key = f"q{index + 1}"
            arrays[f"{key}_tracks"] = np.asarray(handle["tracks"][:, :, start:end], dtype=np.float32)
            arrays[f"{key}_behaviors"] = np.asarray(handle["behaviors"][0, start:end], dtype=np.uint8)
            arrays[f"{key}_on_edge"] = np.asarray(handle["on_edge"][0, start:end], dtype=np.uint8)
            arrays[f"{key}_seconds_elapsed"] = np.asarray(
                handle["seconds_elapsed"][0, start:end], dtype=np.float64
            )
            arrays[f"{key}_temperature"] = np.asarray(handle["temperature"][0, start:end], dtype=np.float32)
            arrays[f"{key}_relative_humidity"] = np.asarray(
                handle["relative_humidity"][0, start:end], dtype=np.float32
            )
            burst_meta.append(
                {
                    "key": key,
                    "recording_fraction": fraction,
                    "start_frame": start,
                    "end_frame_exclusive": end,
                    "frames": end - start,
                    "start_seconds": start / fps,
                    "end_seconds": end / fps,
                }
            )
        metadata = {
            "source_file": item["name"],
            "source_url": item["download_url"],
            "source_size": int(item["size"]),
            "date": item["date"],
            "split": item["split"],
            "fps": fps,
            "recording_frames": n_frames,
            "recording_hours": n_frames / fps / 3600.0,
            "node_names": node_names,
            "behavior_names": behavior_names,
            "bursts": burst_meta,
            "root_attributes": {
                name: (
                    value.decode()
                    if isinstance(value, bytes)
                    else np.asarray(value).tolist()
                    if isinstance(value, np.ndarray)
                    else value.item()
                    if isinstance(value, np.generic)
                    else value
                )
                for name, value in handle.attrs.items()
            },
        }
    arrays["metadata_json"] = np.asarray(json.dumps(metadata))
    np.savez_compressed(out_path, **arrays)
    return {
        **metadata,
        "cache_file": str(out_path),
        "range_requests": reader.requests,
        "mebibytes_fetched": reader.bytes_fetched / 2**20,
        "cache_mebibytes": out_path.stat().st_size / 2**20,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", default=str(T448 / "source" / "princeton_catalog.json"))
    parser.add_argument("--split", required=True, choices=("development", "holdout"))
    parser.add_argument("--output-dir", default=str(HERE / "cache"))
    parser.add_argument("--manifest", default=str(HERE / "results" / "T450A_EXTRACTION_MANIFEST.json"))
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    catalog = json.loads(Path(args.catalog).read_text(encoding="utf-8"))
    files = [item for item in selected_files(catalog) if item["split"] == args.split]
    output_dir = Path(args.output_dir) / args.split
    manifest_path = Path(args.manifest)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {"protocol": "T450A_FROZEN_PROTOCOL.md", "files": []}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    by_source = {row["source_file"]: row for row in manifest.get("files", [])}

    pending = []
    for number, item in enumerate(files, start=1):
        cache_file = output_dir / f"{Path(item['name']).stem}_T450A_pose_bursts.npz"
        if cache_file.exists() and not args.force:
            print(f"[{number}/{len(files)}] cached {item['name']}", flush=True)
            continue
        pending.append(item)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        future_to_item = {}
        for item in pending:
            print(f"extracting {item['name']}", flush=True)
            future_to_item[executor.submit(extract_one, item, output_dir)] = item
        for number, future in enumerate(concurrent.futures.as_completed(future_to_item), start=1):
            item = future_to_item[future]
            record = future.result()
            by_source[item["name"]] = record
            manifest["files"] = sorted(by_source.values(), key=lambda row: row["source_file"])
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            print(
                f"[{number}/{len(pending)} complete] {item['name']}: "
                f"{record['mebibytes_fetched']:.1f} MiB fetched; "
                f"{record['cache_mebibytes']:.1f} MiB cached",
                flush=True,
            )


if __name__ == "__main__":
    main()
