"""Inventory public lifetime-fly HDF5 channels and sampled pose continuity."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import sys
from pathlib import Path

import h5py
import numpy as np
import pandas as pd


ROOT = Path(r"F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\irrationality_di_ara\T450_multiscale_event_web")
RESULTS = ROOT / "results"
T448 = Path(r"F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\irrationality_di_ara\T448_fruitfly_lifecycle_tomography")
sys.path.insert(0, str(T448))
from remote_behavior_aggregate import HTTPRangeReader  # noqa: E402


EXPECTED_DATASETS = {
    "behavior_names",
    "behaviors",
    "node_names",
    "on_edge",
    "relative_humidity",
    "seconds_elapsed",
    "temperature",
    "tracks",
}
CORE_BLOCK_FRACTIONS = (0.125, 0.375, 0.625, 0.875)
BLOCK_SECONDS = 5
CORE_NODES = ("head", "thorax", "abdomen")


def decode(values: np.ndarray) -> list[str]:
    result = []
    for value in values.ravel():
        if isinstance(value, bytes):
            result.append(value.decode("utf-8"))
        else:
            result.append(str(value))
    return result


def longest_true_run(values: np.ndarray) -> int:
    if not values.any():
        return 0
    padded = np.r_[False, values, False]
    edges = np.flatnonzero(padded[1:] != padded[:-1])
    return int(np.max(edges[1::2] - edges[::2]))


def inventory_one(item: dict) -> tuple[dict, list[dict]]:
    reader = HTTPRangeReader(item["download_url"], int(item["size"]))
    with h5py.File(reader, "r") as handle:
        fps = float(np.asarray(handle.attrs["frames_per_second"]).ravel()[0])
        names = decode(np.asarray(handle["node_names"]))
        behaviors = decode(np.asarray(handle["behavior_names"]))
        lengths = {}
        objects = {}
        for name in handle.keys():
            obj = handle[name]
            objects[name] = {
                "shape": list(obj.shape),
                "dtype": str(obj.dtype),
                "chunks": list(obj.chunks) if obj.chunks else None,
                "compression": obj.compression,
            }
            if name in {"behaviors", "on_edge", "relative_humidity", "seconds_elapsed", "temperature", "tracks"}:
                lengths[name] = int(obj.shape[-1])
        n_frames = int(handle["tracks"].shape[-1])
        duration_hours = n_frames / fps / 3600
        block_frames = int(round(BLOCK_SECONDS * fps))
        max_start = max(0, n_frames - block_frames)
        starts = np.array(
            [round(max_start * fraction) for fraction in CORE_BLOCK_FRACTIONS],
            dtype=np.int64,
        )
        core_indices = [names.index(name) for name in CORE_NODES]
        all_node_block_index = int(item["_inventory_index"] % len(CORE_BLOCK_FRACTIONS))
        validate_xy = bool(item["_validate_xy"])
        blocks = []
        for block_index, start in enumerate(starts):
            stop = min(n_frames, int(start) + block_frames)
            # Source orientation is coordinate × node × time. Core nodes are
            # checked in both coordinates at all four lifecycle positions.
            core_tracks = np.asarray(
                handle["tracks"][:, core_indices, int(start):stop], dtype=float
            )
            core_finite = np.isfinite(core_tracks).all(axis=0)
            edge = np.asarray(handle["on_edge"][0, int(start):stop], dtype=np.uint8)
            row = {
                "source_file": item["name"],
                "block_index": block_index,
                "all_node_sample": block_index == all_node_block_index,
                "recording_fraction": float((start + (stop - start) / 2) / n_frames),
                "lifecycle_quartile": min(4, int(4 * (start + 0.5 * (stop - start)) / n_frames) + 1),
                "start_frame": int(start),
                "frames": int(stop - start),
                "seconds": float((stop - start) / fps),
                "core_all_finite_fraction": float(core_finite.all(axis=0).mean()),
                "all_14_finite_fraction": np.nan,
                "at_least_10_finite_fraction": np.nan,
                "median_nodes_finite": np.nan,
                "x_y_mask_agreement": np.nan,
                "edge_fraction": float(edge.mean()),
            }
            for node in names:
                row[f"finite_{node}"] = np.nan
                row[f"longest_run_seconds_{node}"] = np.nan

            if block_index == all_node_block_index:
                x_tracks = np.asarray(
                    handle["tracks"][0, :, int(start):stop], dtype=float
                )
                node_finite = np.isfinite(x_tracks)
                finite_counts = node_finite.sum(axis=0)
                row["all_14_finite_fraction"] = float(node_finite.all(axis=0).mean())
                row["at_least_10_finite_fraction"] = float((finite_counts >= 10).mean())
                row["median_nodes_finite"] = float(np.median(finite_counts))
                for node_index, node in enumerate(names):
                    row[f"finite_{node}"] = float(node_finite[node_index].mean())
                    row[f"longest_run_seconds_{node}"] = float(
                        longest_true_run(node_finite[node_index]) / fps
                    )
                if validate_xy:
                    y_tracks = np.asarray(
                        handle["tracks"][1, :, int(start):stop], dtype=float
                    )
                    row["x_y_mask_agreement"] = float(
                        (np.isfinite(x_tracks) == np.isfinite(y_tracks)).mean()
                    )
            blocks.append(row)

        meta = {
            "source_file": item["name"],
            "file_bytes": int(item["size"]),
            "fps": fps,
            "frames": n_frames,
            "duration_hours": duration_hours,
            "datasets": sorted(handle.keys()),
            "missing_expected_datasets": sorted(EXPECTED_DATASETS - set(handle.keys())),
            "time_axis_lengths": lengths,
            "time_axes_agree": len(set(lengths.values())) == 1,
            "node_names": names,
            "behavior_names": behaviors,
            "objects": objects,
            "start_date_time_UTC": str(handle.attrs.get("start_date_time_UTC", "")),
            "lights_on_UTC": str(handle.attrs.get("lights_on_UTC", "")),
            "lights_off_UTC": str(handle.attrs.get("lights_off_UTC", "")),
            "camera": float(np.asarray(handle.attrs["camera"]).ravel()[0]),
            "video_quadrant": str(handle.attrs.get("video_quadrant", "")),
            "arena_center": np.asarray(handle.attrs["arena_center"]).astype(float).tolist(),
            "range_requests": int(reader.requests),
            "range_bytes": int(reader.bytes_fetched),
        }
    return meta, blocks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--representative-by-date", action="store_true")
    args = parser.parse_args()
    catalog = json.loads((T448 / "source" / "princeton_catalog.json").read_text(encoding="utf-8"))
    files = sorted(
        [item for item in catalog["files"] if item.get("extension") == "h5" and item.get("full_path", "").startswith("final_data/")],
        key=lambda item: item["name"],
    )
    if args.representative_by_date:
        by_date = {}
        for item in files:
            by_date.setdefault(item["name"][:8], []).append(item)
        files = []
        for date in sorted(by_date):
            group = by_date[date]
            files.extend([group[0], group[-1]] if len(group) > 1 else group)
    if args.limit:
        files = files[: args.limit]

    validation_dates = set()
    for index, item in enumerate(files):
        item["_inventory_index"] = index
        date = item["name"][:8]
        item["_validate_xy"] = date not in validation_dates
        validation_dates.add(date)
    meta_rows = []
    block_rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(inventory_one, item): item["name"] for item in files}
        for future in concurrent.futures.as_completed(futures):
            name = futures[future]
            meta, blocks = future.result()
            meta_rows.append(meta)
            block_rows.extend(blocks)
            print(f"inventoried {name}: {meta['duration_hours']:.1f} h, {meta['range_bytes']/2**20:.1f} MiB fetched", flush=True)

    RESULTS.mkdir(parents=True, exist_ok=True)
    meta_rows.sort(key=lambda row: row["source_file"])
    blocks = pd.DataFrame(block_rows).sort_values(["source_file", "block_index"])
    blocks.to_csv(RESULTS / "T450_sampled_pose_continuity.csv", index=False)
    compact = pd.DataFrame(
        [
            {
                "source_file": row["source_file"],
                "file_bytes": row["file_bytes"],
                "fps": row["fps"],
                "frames": row["frames"],
                "duration_hours": row["duration_hours"],
                "time_axes_agree": row["time_axes_agree"],
                "missing_expected_datasets": ";".join(row["missing_expected_datasets"]),
                "range_requests": row["range_requests"],
                "range_bytes": row["range_bytes"],
            }
            for row in meta_rows
        ]
    )
    compact.to_csv(RESULTS / "T450_file_inventory.csv", index=False)

    node_names = meta_rows[0]["node_names"] if meta_rows else []
    behavior_names = meta_rows[0]["behavior_names"] if meta_rows else []
    node_summary = []
    for node in node_names:
        node_summary.append(
            {
                "node": node,
                "sampled_finite_fraction": float(blocks[f"finite_{node}"].mean()),
                "median_block_finite_fraction": float(blocks[f"finite_{node}"].median()),
                "sampled_longest_run_seconds_median": float(blocks[f"longest_run_seconds_{node}"].median()),
                "sampled_longest_run_seconds_q10": float(blocks[f"longest_run_seconds_{node}"].quantile(0.10)),
            }
        )
    pd.DataFrame(node_summary).to_csv(RESULTS / "T450_node_continuity_summary.csv", index=False)

    quartiles = (
        blocks.groupby("lifecycle_quartile")
        .agg(
            blocks=("source_file", "size"),
            flies=("source_file", "nunique"),
            all_node_blocks=("all_node_sample", "sum"),
            core_all_finite_fraction=("core_all_finite_fraction", "mean"),
            all_14_finite_fraction=("all_14_finite_fraction", "mean"),
            at_least_10_finite_fraction=("at_least_10_finite_fraction", "mean"),
            median_nodes_finite=("median_nodes_finite", "median"),
            edge_fraction=("edge_fraction", "mean"),
        )
        .reset_index()
    )
    quartiles.to_csv(RESULTS / "T450_continuity_by_lifecycle_quartile.csv", index=False)

    fps_values = np.array([row["fps"] for row in meta_rows], dtype=float)
    vocabularies_agree = len({tuple(row["node_names"]) for row in meta_rows}) == 1 and len({tuple(row["behavior_names"]) for row in meta_rows}) == 1
    prior_qa_path = T448 / "results" / "extraction_qa.json"
    prior_qa = json.loads(prior_qa_path.read_text(encoding="utf-8")) if prior_qa_path.exists() else []
    summary = {
        "status": "pre-freeze inventory, not an ARA result",
        "pose_audited_files": len(meta_rows),
        "pose_audit_selection": "first and last HDF5 filename per experimental date" if args.representative_by_date else "requested file sequence",
        "cohort_files_previously_extracted_in_T448": len(prior_qa),
        "cohort_complete_precollapse_hours_in_T448": int(sum(row["hours"] for row in prior_qa)) if prior_qa else None,
        "total_hdf5_gib": float(sum(row["file_bytes"] for row in meta_rows) / 2**30),
        "total_recorded_hours": float(sum(row["duration_hours"] for row in meta_rows)),
        "fps_min": float(fps_values.min()) if len(fps_values) else None,
        "fps_max": float(fps_values.max()) if len(fps_values) else None,
        "fps_unique": sorted(np.unique(fps_values).tolist()),
        "all_time_axes_agree": bool(all(row["time_axes_agree"] for row in meta_rows)),
        "all_expected_datasets_present": bool(all(not row["missing_expected_datasets"] for row in meta_rows)),
        "vocabularies_agree": vocabularies_agree,
        "node_names": node_names,
        "behavior_names": behavior_names,
        "tracks_layout": "coordinate × node × frame",
        "coordinate_units": "camera pixels; no physical-length calibration present in HDF5 metadata",
        "sample_design": {
            "core_blocks_per_fly": len(CORE_BLOCK_FRACTIONS),
            "core_block_recording_fractions": list(CORE_BLOCK_FRACTIONS),
            "all_node_blocks_per_fly": 1,
            "seconds_per_block": BLOCK_SECONDS,
            "total_core_blocks": int(len(blocks)),
            "total_all_node_blocks": int(blocks.all_node_sample.sum()),
            "all_node_coordinate_basis": "x-coordinate mask, with x/y mask agreement checked on one file per experimental date",
        },
        "sampled_pose": {
            "core_all_finite_fraction": float(blocks.core_all_finite_fraction.mean()),
            "all_14_finite_fraction": float(blocks.all_14_finite_fraction.mean()),
            "at_least_10_finite_fraction": float(blocks.at_least_10_finite_fraction.mean()),
            "median_nodes_finite": float(blocks.median_nodes_finite.median()),
            "x_y_mask_agreement_min": float(blocks.x_y_mask_agreement.min()),
            "x_y_mask_agreement_mean": float(blocks.x_y_mask_agreement.mean()),
        },
        "node_continuity": node_summary,
        "lifecycle_quartiles": quartiles.to_dict(orient="records"),
        "network_range_requests": int(sum(row["range_requests"] for row in meta_rows)),
        "network_mebibytes_fetched": float(sum(row["range_bytes"] for row in meta_rows) / 2**20),
    }
    (RESULTS / "T450_SOURCE_INVENTORY.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (RESULTS / "T450_SCHEMA_DETAILS.json").write_text(json.dumps(meta_rows, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
