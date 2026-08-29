"""Aggregate individual lifetime behavior files through public HTTP ranges."""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import io
import json
import math
import re
import sys
import urllib.request
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path

import h5py
import numpy as np


class HTTPRangeReader(io.RawIOBase):
    def __init__(self, url: str, size: int, block_size: int = 1024 * 1024, max_blocks: int = 48):
        self.url = url
        self.size = size
        self.block_size = block_size
        self.max_blocks = max_blocks
        self.pos = 0
        self.cache: OrderedDict[int, bytes] = OrderedDict()
        self.bytes_fetched = 0
        self.requests = 0

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=io.SEEK_SET):
        if whence == io.SEEK_SET:
            new_pos = offset
        elif whence == io.SEEK_CUR:
            new_pos = self.pos + offset
        elif whence == io.SEEK_END:
            new_pos = self.size + offset
        else:
            raise ValueError(whence)
        if new_pos < 0:
            raise ValueError("negative seek")
        self.pos = min(new_pos, self.size)
        return self.pos

    def _block(self, index):
        if index in self.cache:
            data = self.cache.pop(index)
            self.cache[index] = data
            return data
        start = index * self.block_size
        end = min(start + self.block_size, self.size) - 1
        req = urllib.request.Request(self.url, headers={"Range": f"bytes={start}-{end}"})
        with urllib.request.urlopen(req, timeout=60) as response:
            data = response.read()
        expected = end - start + 1
        if len(data) != expected:
            raise IOError(f"range {start}-{end}: received {len(data)}, expected {expected}")
        self.requests += 1
        self.bytes_fetched += len(data)
        if self.requests % 25 == 0:
            print(
                f"  {self.requests} range requests; {self.bytes_fetched / 2**20:.1f} MiB fetched",
                file=sys.stderr,
                flush=True,
            )
        self.cache[index] = data
        while len(self.cache) > self.max_blocks:
            self.cache.popitem(last=False)
        return data

    def readinto(self, buffer):
        view = memoryview(buffer).cast("B")
        if self.pos >= self.size or not len(view):
            return 0
        remaining = min(len(view), self.size - self.pos)
        copied = 0
        while copied < remaining:
            index = self.pos // self.block_size
            offset = self.pos % self.block_size
            block = self._block(index)
            take = min(remaining - copied, len(block) - offset)
            view[copied : copied + take] = block[offset : offset + take]
            self.pos += take
            copied += take
        return copied


QUADRANT = {"upper left": "UL", "upper right": "UR", "lower left": "LL", "lower right": "LR"}
DATE_EXPERIMENT = {"20220217": "exp1", "20220313": "exp2", "20220326": "exp3", "20220418": "exp4"}


def date_key(raw):
    return datetime.strptime(raw, "%m/%d/%Y").strftime("%Y%m%d")


def load_index(path):
    rows = list(csv.DictReader(open(path, newline="", encoding="utf-8-sig")))
    lookup = {}
    for row in rows:
        if not row.get("Date") or not row.get("Camera"):
            continue
        camera = int(re.search(r"(\d+)", row["Camera"]).group(1))
        key = (row["Experiment"].strip(), camera, row["Well location"].strip().upper())
        lookup[key] = row
    return lookup


def parse_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return math.nan


def zt_hour(start_text, lights_on_text, midpoint_hours):
    start = datetime.strptime(start_text, "%Y%m%d_%H:%M:%S")
    light_clock = datetime.strptime(lights_on_text, "%H:%M:%S").time()
    lights_on = datetime.combine(start.date(), light_clock)
    while lights_on > start:
        lights_on -= timedelta(days=1)
    point = start + timedelta(hours=midpoint_hours)
    return ((point - lights_on).total_seconds() / 3600.0) % 24.0


def aggregate_file(item, index_lookup, hour_seconds=3600):
    match = re.match(r"(\d{8})_cam(\d+)_flid(\d+)\.h5", item["name"])
    date, camera, file_fly_id = match.group(1), int(match.group(2)), int(match.group(3))
    reader = HTTPRangeReader(item["download_url"], int(item["size"]))
    rows = []
    with h5py.File(reader, "r") as handle:
        fps = float(np.asarray(handle.attrs["frames_per_second"]).ravel()[0])
        quadrant_text = handle.attrs["video_quadrant"]
        if isinstance(quadrant_text, bytes):
            quadrant_text = quadrant_text.decode()
        well = QUADRANT[str(quadrant_text).lower()]
        experiment = DATE_EXPERIMENT[date]
        metadata = index_lookup.get((experiment, camera, well))
        if metadata is None:
            raise KeyError(f"No index match for {(experiment, camera, well)}")
        collapse = parse_float(metadata.get("Collapse (hours into video)"))
        death = parse_float(metadata.get("Time of death (hours into video)"))
        n_frames = int(handle["behaviors"].shape[-1])
        duration_hours = n_frames / fps / 3600.0
        analysis_end = min(duration_hours, collapse if math.isfinite(collapse) else duration_hours)
        frames_per_hour = int(round(hour_seconds * fps))
        full_windows = int(math.floor(analysis_end * 3600 / hour_seconds))
        for hour in range(full_windows):
            start = hour * frames_per_hour
            end = min(start + frames_per_hour, n_frames)
            labels = np.asarray(handle["behaviors"][0, start:end], dtype=np.uint8)
            counts = np.bincount(labels, minlength=9).astype(float)
            raw_total = counts.sum()
            parts = np.array(
                [counts[6] + counts[7], counts[3] + counts[4] + counts[5], counts[2], counts[1]],
                dtype=float,
            )
            # Jeffreys half-count prevents a zero hour from becoming an infinite log-ratio.
            closed = (parts + 0.5) / (parts.sum() + 2.0)
            t, g, p, idle = closed
            z1 = math.sqrt(0.5) * math.log(t / g)
            z2 = math.sqrt(2.0 / 3.0) * math.log(math.sqrt(t * g) / p)
            z3 = math.sqrt(3.0 / 4.0) * math.log((t * g * p) ** (1.0 / 3.0) / idle)
            midpoint = (hour + 0.5) * hour_seconds / 3600.0
            rows.append(
                {
                    "date": date,
                    "experiment": metadata["Experiment"],
                    "camera": camera,
                    "well": well,
                    "fly_id_index": metadata["Fly id"],
                    "fly_id_file": file_fly_id,
                    "source_file": item["name"],
                    "hour_index": hour,
                    "hour_midpoint": midpoint,
                    "hours_to_collapse": collapse - midpoint,
                    "hours_to_death": death - midpoint,
                    "collapse_hour": collapse,
                    "death_hour": death,
                    "recording_duration_hours": duration_hours,
                    "zt_hour": zt_hour(handle.attrs["start_date_time_UTC"], handle.attrs["lights_on_UTC"], midpoint),
                    "lights_on": int(zt_hour(handle.attrs["start_date_time_UTC"], handle.attrs["lights_on_UTC"], midpoint) < 12),
                    "traversal_share": parts[0] / max(parts.sum(), 1),
                    "grooming_share": parts[1] / max(parts.sum(), 1),
                    "proboscis_share": parts[2] / max(parts.sum(), 1),
                    "idle_share": parts[3] / max(parts.sum(), 1),
                    "excluded_unstereotyped_share": counts[0] / raw_total,
                    "excluded_edge_share": counts[8] / raw_total,
                    "z_traversal_maintenance": z1,
                    "z_action_intake": z2,
                    "z_participation_quiescence": z3,
                }
            )
    return rows, {"requests": reader.requests, "bytes_fetched": reader.bytes_fetched}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--index", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--qa-output", required=True)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--names", nargs="*")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    catalog = json.load(open(args.catalog, encoding="utf-8"))
    files = [item for item in catalog["files"] if item.get("extension") == "h5"]
    files.sort(key=lambda item: item["name"])
    if args.names:
        wanted = set(args.names)
        files = [item for item in files if item["name"] in wanted]
    if args.limit:
        files = files[: args.limit]
    index_lookup = load_index(args.index)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    all_rows = []
    qa = []
    if args.resume and output.exists() and Path(args.qa_output).exists():
        all_rows = list(csv.DictReader(open(output, newline="", encoding="utf-8")))
        qa = json.loads(Path(args.qa_output).read_text(encoding="utf-8"))
        completed = {row["source_file"] for row in qa}
        files = [item for item in files if item["name"] not in completed]
        print(f"resuming after {len(completed)} completed files; {len(files)} remain", file=sys.stderr, flush=True)
    def save_progress():
        all_rows.sort(key=lambda row: (row["source_file"], int(row["hour_index"])))
        qa.sort(key=lambda row: row["source_file"])
        with open(output, "w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(all_rows[0]))
            writer.writeheader()
            writer.writerows(all_rows)
        Path(args.qa_output).write_text(json.dumps(qa, indent=2), encoding="utf-8")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        future_to_item = {executor.submit(aggregate_file, item, index_lookup): item for item in files}
        for number, future in enumerate(concurrent.futures.as_completed(future_to_item), start=1):
            item = future_to_item[future]
            rows, network = future.result()
            all_rows.extend(rows)
            qa.append({"source_file": item["name"], "hours": len(rows), **network})
            save_progress()
            print(
                f"[{number}/{len(files)}] {item['name']}: {len(rows)} hours; "
                f"{network['bytes_fetched'] / 2**20:.1f} MiB fetched",
                file=sys.stderr,
                flush=True,
            )


if __name__ == "__main__":
    main()
