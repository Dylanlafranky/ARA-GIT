from __future__ import annotations

import csv
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path


def load_file(path: Path):
    frames = defaultdict(list)
    ids = defaultdict(list)
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            rec = {
                "frame": int(row["frame_number"]),
                "id": int(row["ID"]),
                "x": float(row["cx_pos [m]"]),
                "y": float(row["cy_pos [m]"]),
                "area": float(row["size [m^2]"]),
                "perimeter": float(row["perimeter [m]"]),
            }
            frames[rec["frame"]].append(rec)
            ids[rec["id"]].append(rec)
    return frames, ids


def summarize(path: Path):
    frames, ids = load_file(path)
    frame_numbers = sorted(frames)
    counts = Counter(len(frames[f]) for f in frame_numbers)
    track_lengths = [len(rows) for rows in ids.values()]
    track_spans = [max(r["frame"] for r in rows) - min(r["frame"] for r in rows) + 1 for rows in ids.values()]

    adjacent = 0
    decreases = Counter()
    increases = Counter()
    consecutive_overlap = []
    for f in frame_numbers:
        if f + 1 not in frames:
            continue
        adjacent += 1
        here = {r["id"] for r in frames[f]}
        nxt = {r["id"] for r in frames[f + 1]}
        delta = len(nxt) - len(here)
        if delta < 0:
            decreases[-delta] += 1
        elif delta > 0:
            increases[delta] += 1
        consecutive_overlap.append(len(here & nxt) / max(1, len(here | nxt)))

    def quantiles(values):
        if not values:
            return None
        values = sorted(values)
        def q(p):
            i = (len(values) - 1) * p
            lo, hi = math.floor(i), math.ceil(i)
            return values[lo] if lo == hi else values[lo] * (hi - i) + values[hi] * (i - lo)
        return {"min": values[0], "q25": q(0.25), "median": q(0.5), "q75": q(0.75), "max": values[-1]}

    return {
        "file": path.name,
        "rows": sum(len(v) for v in frames.values()),
        "observed_frames": len(frame_numbers),
        "frame_min": min(frame_numbers) if frame_numbers else None,
        "frame_max": max(frame_numbers) if frame_numbers else None,
        "unique_ids": len(ids),
        "contours_per_frame": dict(sorted(counts.items())),
        "track_length": quantiles(track_lengths),
        "track_span": quantiles(track_spans),
        "adjacent_frame_pairs": adjacent,
        "contour_decreases": dict(decreases),
        "contour_increases": dict(increases),
        "median_id_jaccard": quantiles(consecutive_overlap)["median"] if consecutive_overlap else None,
    }


def main(root: str):
    paths = sorted(Path(root).glob("*.csv"))
    summaries = [summarize(p) for p in paths]
    compact = []
    for s in summaries:
        compact.append({
            "file": s["file"],
            "rows": s["rows"],
            "frames": s["observed_frames"],
            "ids": s["unique_ids"],
            "max_contours": max((int(k) for k in s["contours_per_frame"]), default=0),
            "frames_multi": sum(int(v) for k, v in s["contours_per_frame"].items() if int(k) >= 2),
            "track_med": s["track_length"]["median"] if s["track_length"] else None,
            "track_q75": s["track_length"]["q75"] if s["track_length"] else None,
            "down1": int(s["contour_decreases"].get(1, 0)),
            "id_jaccard": s["median_id_jaccard"],
        })
    print(json.dumps(compact, indent=2))


if __name__ == "__main__":
    main(sys.argv[1])
