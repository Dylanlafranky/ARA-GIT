from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

from bubble_lineage import load_run


ROOT_STEPS = (16, 32, 64)
MIN_STEP_M = 0.0005


def split_for_video(video: str) -> str:
    number = int(video[1:])
    if number <= 7:
        return "calibration"
    if number <= 28:
        return "evaluation"
    return "holdout"


def contiguous_lengths(track: dict) -> list[int]:
    frames = sorted(track)
    if not frames:
        return []
    lengths: list[int] = []
    length = 1
    for previous, current in zip(frames, frames[1:]):
        if current == previous + 1:
            length += 1
        else:
            lengths.append(length)
            length = 1
    lengths.append(length)
    return lengths


def contiguous_segments(track: dict) -> list[list]:
    frames = sorted(track)
    if not frames:
        return []
    segments: list[list] = []
    current = [track[frames[0]]]
    for previous, frame in zip(frames, frames[1:]):
        if frame == previous + 1:
            current.append(track[frame])
        else:
            segments.append(current)
            current = [track[frame]]
    segments.append(current)
    return segments


def root_passes_resolution(block: list) -> bool:
    steps = len(block) - 1
    child_steps = 1
    while child_steps * 2 <= steps:
        total_nodes = steps // (2 * child_steps)
        valid_nodes = 0
        for start in range(0, steps, 2 * child_steps):
            mid = start + child_steps
            end = start + 2 * child_steps
            left = math.hypot(block[mid].x - block[start].x, block[mid].y - block[start].y)
            right = math.hypot(block[end].x - block[mid].x, block[end].y - block[mid].y)
            valid_nodes += left >= MIN_STEP_M and right >= MIN_STEP_M
        if valid_nodes < math.ceil(total_nodes / 2):
            return False
        child_steps *= 2
    return True


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    source = base / "source_data"
    summary: dict[str, dict] = {}
    per_video: list[dict] = []

    totals = defaultdict(lambda: defaultdict(int))
    for path in sorted(source.glob("*.csv")):
        run = load_run(path)
        split = split_for_video(run.video)
        lengths = [
            length
            for track in run.tracks.values()
            for length in contiguous_lengths(track)
        ]
        segments = [
            segment
            for track in run.tracks.values()
            for segment in contiguous_segments(track)
        ]
        record = {
            "video": run.video,
            "split": split,
            "tracks": len(run.tracks),
            "segments": len(lengths),
            "max_positions": max(lengths, default=0),
        }
        totals[split]["videos"] += 1
        totals[split]["tracks"] += len(run.tracks)
        totals[split]["segments"] += len(lengths)
        for steps in ROOT_STEPS:
            positions = steps + 1
            eligible_segments = sum(length >= positions for length in lengths)
            sliding_blocks = sum(max(0, length - steps) for length in lengths)
            nonoverlap_blocks = sum((length - 1) // steps for length in lengths)
            analysis_eligible = 0
            for segment in segments:
                for start in range(0, len(segment) - steps, steps):
                    block = segment[start:start + steps + 1]
                    analysis_eligible += root_passes_resolution(block)
            record[f"segments_ge_{positions}_positions"] = eligible_segments
            record[f"sliding_{steps}_step_blocks"] = sliding_blocks
            record[f"nonoverlap_{steps}_step_blocks"] = nonoverlap_blocks
            record[f"resolution_eligible_{steps}_step_blocks"] = analysis_eligible
            totals[split][f"segments_ge_{positions}_positions"] += eligible_segments
            totals[split][f"sliding_{steps}_step_blocks"] += sliding_blocks
            totals[split][f"nonoverlap_{steps}_step_blocks"] += nonoverlap_blocks
            totals[split][f"resolution_eligible_{steps}_step_blocks"] += analysis_eligible
        per_video.append(record)

    for split in ("calibration", "evaluation", "holdout"):
        summary[split] = dict(totals[split])
    payload = {"root_steps": list(ROOT_STEPS), "splits": summary, "videos": per_video}
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
