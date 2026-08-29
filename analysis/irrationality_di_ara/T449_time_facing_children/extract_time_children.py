"""Extract frozen T449 same-rung temporal children from public fly histories."""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import json
import math
import re
import sys
from pathlib import Path

import h5py
import numpy as np


T448 = Path(
    r"F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\irrationality_di_ara"
    r"\T448_fruitfly_lifecycle_tomography"
)
sys.path.insert(0, str(T448))
from remote_behavior_aggregate import (  # noqa: E402
    DATE_EXPERIMENT,
    HTTPRangeReader,
    QUADRANT,
    load_index,
    parse_float,
    zt_hour,
)


WINDOW_SECONDS = 600
RETENTION_LAGS = (1, 10, 60)
RESOLVED_STATES = tuple(range(1, 8))
STATE_NAMES = (
    "unstereotyped",
    "idle",
    "proboscis",
    "fore_groom",
    "hind_groom",
    "wing_groom",
    "altered_locomotion",
    "locomotion",
    "on_edge",
)


def stable_seed(*parts: object) -> int:
    digest = hashlib.sha256("|".join(map(str, parts)).encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "little")


def modal_second_sequence(labels: np.ndarray, fps: float) -> np.ndarray:
    """Exact modal label across every available frame in each second."""
    second_index = np.floor(np.arange(len(labels), dtype=float) / fps).astype(np.int64)
    valid = second_index < WINDOW_SECONDS
    flat_index = second_index[valid] * 9 + labels[valid].astype(np.int64)
    counts = np.bincount(flat_index, minlength=WINDOW_SECONDS * 9).reshape(WINDOW_SECONDS, 9)
    return counts.argmax(axis=1).astype(np.uint8)


def child_metrics(sequence: np.ndarray) -> dict[str, float | int]:
    resolved = np.isin(sequence, RESOLVED_STATES)
    resolved_values = sequence[resolved]
    counts = np.bincount(resolved_values, minlength=9).astype(float)
    resolved_n = int(resolved.sum())
    state_prob = counts[1:8] / max(resolved_n, 1)
    chance_same = float(np.square(state_prob).sum())

    retention = {}
    for lag in RETENTION_LAGS:
        valid = resolved[:-lag] & resolved[lag:]
        if valid.sum() < 30 or chance_same >= 1 - 1e-12:
            value = math.nan
        else:
            same = float((sequence[:-lag][valid] == sequence[lag:][valid]).mean())
            value = (same - chance_same) / (1 - chance_same)
        retention[f"retention_{lag}s"] = value

    valid_retention = np.asarray([retention[f"retention_{lag}s"] for lag in RETENTION_LAGS], dtype=float)
    c_a = float(np.nanmean(valid_retention)) if np.isfinite(valid_retention).sum() >= 2 else math.nan

    valid_adjacent = resolved[:-1] & resolved[1:]
    origins = sequence[:-1][valid_adjacent] - 1
    destinations = sequence[1:][valid_adjacent] - 1
    transition_counts = np.zeros((7, 7), dtype=float)
    if len(origins):
        np.add.at(transition_counts, (origins, destinations), 1)
    row_totals = transition_counts.sum(axis=1)
    total = float(row_totals.sum())
    conditional_entropy = 0.0
    if total > 0:
        for row, row_total in zip(transition_counts, row_totals):
            if row_total <= 0:
                continue
            probabilities = row[row > 0] / row_total
            conditional_entropy += (row_total / total) * float(-(probabilities * np.log(probabilities)).sum())
    present_states = int(np.count_nonzero(counts[1:8]))
    c_b = conditional_entropy / math.log(present_states) if present_states >= 2 else math.nan

    change_rate = float((origins != destinations).mean()) if len(origins) else math.nan
    if present_states >= 2:
        positive = state_prob[state_prob > 0]
        occupancy_entropy = float(-(positive * np.log(positive)).sum() / math.log(present_states))
    else:
        occupancy_entropy = math.nan

    if total > 0:
        transition_asymmetry = float(np.abs(transition_counts - transition_counts.T).sum() / (2 * total))
    else:
        transition_asymmetry = math.nan

    result: dict[str, float | int] = {
        "resolved_seconds": resolved_n,
        "valid_adjacent_transitions": int(valid_adjacent.sum()),
        "present_resolved_states": present_states,
        "resolved_fraction": float(resolved.mean()),
        "chance_same_from_occupancy": chance_same,
        "C_A_retention": c_a,
        "C_B_traversal": c_b,
        "change_rate_1s": change_rate,
        "occupancy_entropy": occupancy_entropy,
        "transition_asymmetry": transition_asymmetry,
        **retention,
    }
    all_counts = np.bincount(sequence, minlength=9).astype(float) / len(sequence)
    for state, name in enumerate(STATE_NAMES):
        result[f"share_{name}"] = float(all_counts[state])
    return result


def extract_file(item: dict, index_lookup: dict) -> tuple[list[dict], dict]:
    match = re.match(r"(\d{8})_cam(\d+)_flid(\d+)\.h5", item["name"])
    if match is None:
        raise ValueError(item["name"])
    date, camera, file_fly_id = match.group(1), int(match.group(2)), int(match.group(3))
    reader = HTTPRangeReader(item["download_url"], int(item["size"]))
    rows: list[dict] = []
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
        full_windows = int(math.floor(analysis_end * 3600 / WINDOW_SECONDS))
        frames_per_window = int(round(WINDOW_SECONDS * fps))

        for window in range(full_windows):
            start = int(round(window * WINDOW_SECONDS * fps))
            end = min(start + frames_per_window, n_frames)
            labels = np.asarray(handle["behaviors"][0, start:end], dtype=np.uint8)
            if len(labels) < int(0.99 * frames_per_window):
                continue
            sequence = modal_second_sequence(labels, fps)
            metrics = child_metrics(sequence)
            shuffled = sequence.copy()
            np.random.default_rng(stable_seed(item["name"], window, "timestamp-shuffle")).shuffle(shuffled)
            shuffled_metrics = child_metrics(shuffled)
            midpoint = (window + 0.5) * WINDOW_SECONDS / 3600.0
            eligible = (
                metrics["resolved_fraction"] >= 0.80
                and metrics["valid_adjacent_transitions"] >= 300
                and metrics["present_resolved_states"] >= 2
                and math.isfinite(float(metrics["C_A_retention"]))
                and math.isfinite(float(metrics["C_B_traversal"]))
            )
            rows.append(
                {
                    "date": date,
                    "experiment": metadata["Experiment"],
                    "camera": camera,
                    "well": well,
                    "fly_id_index": metadata["Fly id"],
                    "fly_id_file": file_fly_id,
                    "source_file": item["name"],
                    "child_window_index": window,
                    "child_midpoint_hours": midpoint,
                    "parent_hour_index": window // 6,
                    "hours_to_collapse": collapse - midpoint,
                    "hours_to_death": death - midpoint,
                    "collapse_hour": collapse,
                    "death_hour": death,
                    "recording_duration_hours": duration_hours,
                    "zt_hour": zt_hour(handle.attrs["start_date_time_UTC"], handle.attrs["lights_on_UTC"], midpoint),
                    "lights_on": int(zt_hour(handle.attrs["start_date_time_UTC"], handle.attrs["lights_on_UTC"], midpoint) < 12),
                    "eligible": int(eligible),
                    **metrics,
                    "shuffle_C_A_retention": shuffled_metrics["C_A_retention"],
                    "shuffle_C_B_traversal": shuffled_metrics["C_B_traversal"],
                }
            )
    return rows, {
        "source_file": item["name"],
        "windows": len(rows),
        "eligible_windows": int(sum(row["eligible"] for row in rows)),
        "requests": reader.requests,
        "bytes_fetched": reader.bytes_fetched,
    }


def write_progress(output: Path, qa_output: Path, rows: list[dict], qa: list[dict]) -> None:
    rows.sort(key=lambda row: (row["source_file"], int(row["child_window_index"])))
    qa.sort(key=lambda row: row["source_file"])
    output.parent.mkdir(parents=True, exist_ok=True)
    if rows:
        with output.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    qa_output.write_text(json.dumps(qa, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--index", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--qa-output", required=True)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--names", nargs="*")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    catalog = json.load(open(args.catalog, encoding="utf-8"))
    files = sorted(
        [item for item in catalog["files"] if item.get("extension") == "h5"],
        key=lambda item: item["name"],
    )
    if args.names:
        wanted = set(args.names)
        files = [item for item in files if item["name"] in wanted]
    if args.limit:
        files = files[: args.limit]
    index_lookup = load_index(args.index)
    output = Path(args.output)
    qa_output = Path(args.qa_output)
    rows: list[dict] = []
    qa: list[dict] = []
    if args.resume and output.exists() and qa_output.exists():
        rows = list(csv.DictReader(output.open(newline="", encoding="utf-8")))
        qa = json.loads(qa_output.read_text(encoding="utf-8"))
        complete = {row["source_file"] for row in qa}
        files = [item for item in files if item["name"] not in complete]
        print(f"resuming after {len(complete)} files; {len(files)} remain", file=sys.stderr, flush=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {executor.submit(extract_file, item, index_lookup): item for item in files}
        for number, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            item = futures[future]
            file_rows, file_qa = future.result()
            rows.extend(file_rows)
            qa.append(file_qa)
            write_progress(output, qa_output, rows, qa)
            print(
                f"[{number}/{len(files)}] {item['name']}: {file_qa['eligible_windows']}/"
                f"{file_qa['windows']} eligible; {file_qa['bytes_fetched']/2**20:.1f} MiB",
                file=sys.stderr,
                flush=True,
            )


if __name__ == "__main__":
    main()
