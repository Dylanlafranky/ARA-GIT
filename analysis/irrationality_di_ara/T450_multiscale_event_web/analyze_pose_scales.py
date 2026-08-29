"""Fit and evaluate the frozen T450A multiscale pose geometry."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import warnings
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
SCALES = np.asarray([1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024], dtype=int)
DESCRIPTORS = ("persistence", "retained_dispersion", "abs_reversal_asymmetry")
FEATURE_ORDER = (
    "traversal_speed",
    "rotation_speed",
    "core_bend",
    "core_span",
    "articulation_speed",
    "lr_articulation_balance",
)
FEATURE_META = {
    "traversal_speed": {"aggregation": "mean", "min_finite": 0.80, "units": "body lengths/s"},
    "rotation_speed": {"aggregation": "mean", "min_finite": 0.80, "units": "rad/s"},
    "core_bend": {"aggregation": "median", "min_finite": 0.80, "units": "body lengths"},
    "core_span": {"aggregation": "median", "min_finite": 0.80, "units": "body lengths"},
    "articulation_speed": {"aggregation": "mean", "min_finite": 0.50, "units": "body lengths/s"},
    "lr_articulation_balance": {"aggregation": "median", "min_finite": 0.50, "units": "signed share"},
}
APPENDAGES = ("forelegL", "forelegR", "midlegL", "midlegR", "hindlegL", "hindlegR", "wingL", "wingR")
LEFT = ("forelegL", "midlegL", "hindlegL", "wingL")
RIGHT = ("forelegR", "midlegR", "hindlegR", "wingR")


def stable_seed(*parts: object) -> int:
    digest = hashlib.sha256("|".join(map(str, parts)).encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "little")


def robust_mad(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if not len(values):
        return math.nan
    centre = float(np.median(values))
    return float(np.median(np.abs(values - centre)))


def safe_scale(values: np.ndarray) -> float:
    mad = robust_mad(values)
    if math.isfinite(mad) and mad > 1e-12:
        return mad
    values = np.asarray(values, dtype=float)
    sd = float(np.nanstd(values))
    return sd if math.isfinite(sd) and sd > 1e-12 else 1.0


def rankdata(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    sorted_values = values[order]
    start = 0
    while start < len(values):
        end = start + 1
        while end < len(values) and sorted_values[end] == sorted_values[start]:
            end += 1
        ranks[order[start:end]] = (start + end - 1) / 2.0
        start = end
    return ranks


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    valid = np.isfinite(x) & np.isfinite(y)
    if int(valid.sum()) < 4:
        return math.nan
    rx, ry = rankdata(x[valid]), rankdata(y[valid])
    if np.std(rx) < 1e-12 or np.std(ry) < 1e-12:
        return math.nan
    return float(np.corrcoef(rx, ry)[0, 1])


def interpolate_short_gaps(values: np.ndarray, max_gap: int = 2) -> np.ndarray:
    out = np.asarray(values, dtype=float).copy()
    finite = np.isfinite(out)
    if finite.all() or not finite.any():
        return out
    i = 0
    while i < len(out):
        if finite[i]:
            i += 1
            continue
        start = i
        while i < len(out) and not finite[i]:
            i += 1
        end = i
        if end - start <= max_gap and start > 0 and end < len(out) and finite[start - 1] and finite[end]:
            out[start:end] = np.linspace(out[start - 1], out[end], end - start + 2)[1:-1]
    return out


def wrapped_difference(angle: np.ndarray) -> np.ndarray:
    delta = np.diff(angle)
    return (delta + np.pi) % (2 * np.pi) - np.pi


def load_file_features(path: Path) -> tuple[list[dict], dict]:
    loaded = np.load(path, allow_pickle=False)
    meta = json.loads(str(loaded["metadata_json"]))
    names = meta["node_names"]
    node = {name: names.index(name) for name in names}
    lengths: list[np.ndarray] = []
    for burst in meta["bursts"]:
        tracks = np.asarray(loaded[f"{burst['key']}_tracks"], dtype=float)
        head, abdomen = tracks[:, node["head"], :], tracks[:, node["abdomen"], :]
        lengths.append(np.hypot(head[0] - abdomen[0], head[1] - abdomen[1]))
    reference_length = float(np.nanmedian(np.concatenate(lengths)))
    if not math.isfinite(reference_length) or reference_length <= 1e-6:
        raise ValueError(f"unstable body length in {path.name}: {reference_length}")

    bursts: list[dict] = []
    for burst in meta["bursts"]:
        key = burst["key"]
        tracks = np.asarray(loaded[f"{key}_tracks"], dtype=float)
        fps = float(meta["fps"])
        # Only two-frame core gaps may be filled; appendages remain observed/missing.
        for coord in range(2):
            for name in ("head", "thorax", "abdomen"):
                tracks[coord, node[name], :] = interpolate_short_gaps(tracks[coord, node[name], :], 2)
        head = tracks[:, node["head"], :]
        thorax = tracks[:, node["thorax"], :]
        abdomen = tracks[:, node["abdomen"], :]
        axis = head - abdomen
        axis_length = np.hypot(axis[0], axis[1])
        angle = np.arctan2(axis[1], axis[0])
        core_valid = np.isfinite(head).all(axis=0) & np.isfinite(thorax).all(axis=0) & np.isfinite(abdomen).all(axis=0)

        traversal = np.full(tracks.shape[-1], np.nan)
        traversal[1:] = np.hypot(np.diff(thorax[0]), np.diff(thorax[1])) * fps / reference_length
        rotation = np.full(tracks.shape[-1], np.nan)
        rotation[1:] = np.abs(wrapped_difference(angle)) * fps
        # Signed distance of thorax from the abdomen-to-head line.
        rel_thorax = thorax - abdomen
        core_bend = (axis[0] * rel_thorax[1] - axis[1] * rel_thorax[0]) / np.maximum(axis_length, 1e-12)
        core_bend /= reference_length
        core_span = axis_length / reference_length
        traversal[~core_valid] = np.nan
        rotation[~core_valid] = np.nan
        core_bend[~core_valid] = np.nan
        core_span[~core_valid] = np.nan

        cos_a, sin_a = np.cos(angle), np.sin(angle)
        body_x = np.full((len(names), tracks.shape[-1]), np.nan)
        body_y = np.full_like(body_x, np.nan)
        for name in names:
            rel_x = tracks[0, node[name], :] - thorax[0]
            rel_y = tracks[1, node[name], :] - thorax[1]
            body_x[node[name]] = (rel_x * cos_a + rel_y * sin_a) / reference_length
            body_y[node[name]] = (-rel_x * sin_a + rel_y * cos_a) / reference_length

        node_speed = np.full((len(names), tracks.shape[-1]), np.nan)
        for name in APPENDAGES:
            idx = node[name]
            node_speed[idx, 1:] = np.hypot(np.diff(body_x[idx]), np.diff(body_y[idx])) * fps

        def side_speed(side: tuple[str, ...], minimum: int) -> np.ndarray:
            values = node_speed[[node[name] for name in side]]
            finite_n = np.isfinite(values).sum(axis=0)
            with warnings.catch_warnings(), np.errstate(all="ignore"):
                warnings.simplefilter("ignore", category=RuntimeWarning)
                result = np.nanmedian(values, axis=0)
            result[finite_n < minimum] = np.nan
            return result

        appendage_values = node_speed[[node[name] for name in APPENDAGES]]
        appendage_n = np.isfinite(appendage_values).sum(axis=0)
        with warnings.catch_warnings(), np.errstate(all="ignore"):
            warnings.simplefilter("ignore", category=RuntimeWarning)
            articulation = np.nanmedian(appendage_values, axis=0)
        articulation[appendage_n < 4] = np.nan
        left, right = side_speed(LEFT, 2), side_speed(RIGHT, 2)
        lr_balance = (left - right) / (left + right + 1e-12)
        lr_balance[~(np.isfinite(left) & np.isfinite(right))] = np.nan

        signals = {
            "traversal_speed": traversal,
            "rotation_speed": rotation,
            "core_bend": core_bend,
            "core_span": core_span,
            "articulation_speed": articulation,
            "lr_articulation_balance": lr_balance,
        }
        behaviours = np.asarray(loaded[f"{key}_behaviors"], dtype=np.uint8)
        on_edge = np.asarray(loaded[f"{key}_on_edge"], dtype=np.uint8)
        bursts.append(
            {
                "source_file": meta["source_file"],
                "date": meta["date"],
                "split": meta["split"],
                "burst": key,
                "recording_fraction": float(burst["recording_fraction"]),
                "fps": fps,
                "reference_body_length_pixels": reference_length,
                "signals": signals,
                "behaviours": behaviours,
                "on_edge": on_edge,
                "body_x": body_x,
                "body_y": body_y,
                "core_valid_fraction": float(core_valid.mean()),
                "appendage_valid_fraction": float(np.isfinite(articulation).mean()),
                "lr_valid_fraction": float(np.isfinite(lr_balance).mean()),
                "idle_fraction": float((behaviours == 1).mean()),
                "locomotion_fraction": float(np.isin(behaviours, [6, 7]).mean()),
                "on_edge_fraction": float(on_edge.mean()),
                "temperature_median": float(np.nanmedian(loaded[f"{key}_temperature"])),
                "relative_humidity_median": float(np.nanmedian(loaded[f"{key}_relative_humidity"])),
            }
        )
    return bursts, meta


def load_split(cache_dir: Path) -> tuple[list[dict], list[dict]]:
    bursts: list[dict] = []
    files: list[dict] = []
    for path in sorted(cache_dir.glob("*_T450A_pose_bursts.npz")):
        file_bursts, meta = load_file_features(path)
        bursts.extend(file_bursts)
        files.append(meta)
    if not bursts:
        raise FileNotFoundError(f"no pose caches in {cache_dir}")
    return bursts, files


def fit_winsor(bursts: list[dict]) -> dict:
    config = {}
    for feature in FEATURE_ORDER:
        values = np.concatenate([burst["signals"][feature] for burst in bursts])
        values = values[np.isfinite(values)]
        config[feature] = {
            "q005": float(np.quantile(values, 0.005)),
            "q995": float(np.quantile(values, 0.995)),
            "raw_median": float(np.median(values)),
            "raw_mad": safe_scale(values),
        }
    return config


def block_values(signal: np.ndarray, scale: int, feature: str) -> np.ndarray:
    n_blocks = len(signal) // scale
    if n_blocks < 5:
        return np.asarray([], dtype=float)
    matrix = signal[: n_blocks * scale].reshape(n_blocks, scale)
    finite_fraction = np.isfinite(matrix).mean(axis=1)
    with warnings.catch_warnings(), np.errstate(all="ignore"):
        warnings.simplefilter("ignore", category=RuntimeWarning)
        if FEATURE_META[feature]["aggregation"] == "mean":
            values = np.nanmean(matrix, axis=1)
        else:
            values = np.nanmedian(matrix, axis=1)
    values[finite_fraction < FEATURE_META[feature]["min_finite"]] = np.nan
    return values


def descriptors(signal: np.ndarray, scale: int, feature: str) -> dict:
    values = block_values(signal, scale, feature)
    raw_dispersion = safe_scale(signal)
    persistence = spearman(values[:-1], values[1:]) if len(values) >= 5 else math.nan
    retained = robust_mad(values) / raw_dispersion if len(values) else math.nan
    valid_pair = np.isfinite(values[:-1]) & np.isfinite(values[1:]) if len(values) else np.asarray([], bool)
    difference = values[1:][valid_pair] - values[:-1][valid_pair] if len(values) else np.asarray([])
    if len(difference) >= 4:
        denom = float(np.mean(np.abs(difference) ** 3))
        asymmetry = float(np.mean(difference**3) / denom) if denom > 1e-15 else 0.0
    else:
        asymmetry = math.nan
    return {
        "amount": float(np.nanmedian(values)) if np.isfinite(values).any() else math.nan,
        "persistence": persistence,
        "retained_dispersion": retained,
        "reversal_asymmetry": asymmetry,
        "abs_reversal_asymmetry": abs(asymmetry) if math.isfinite(asymmetry) else math.nan,
        "valid_blocks": int(np.isfinite(values).sum()),
        "total_blocks": int(len(values)),
    }


def metric_table(bursts: list[dict], winsor: dict) -> pd.DataFrame:
    rows = []
    for burst in bursts:
        for feature in FEATURE_ORDER:
            raw = burst["signals"][feature]
            bounds = winsor[feature]
            signal = np.clip(raw, bounds["q005"], bounds["q995"])
            for scale in SCALES:
                result = descriptors(signal, int(scale), feature)
                rows.append(
                    {
                        "source_file": burst["source_file"],
                        "date": burst["date"],
                        "split": burst["split"],
                        "burst": burst["burst"],
                        "recording_fraction": burst["recording_fraction"],
                        "fps": burst["fps"],
                        "feature": feature,
                        "scale_frames": int(scale),
                        "scale_seconds": float(scale / burst["fps"]),
                        **result,
                    }
                )
    return pd.DataFrame(rows)


def fit_descriptor_scaling(metrics: pd.DataFrame) -> dict:
    config = {}
    for feature in FEATURE_ORDER:
        config[feature] = {}
        part = metrics[metrics.feature == feature]
        for descriptor in DESCRIPTORS:
            values = part[descriptor].to_numpy(float)
            config[feature][descriptor] = {
                "median": float(np.nanmedian(values)),
                "mad": safe_scale(values),
            }
    return config


def boundary_table(metrics: pd.DataFrame, scaling: dict) -> pd.DataFrame:
    rows = []
    group_cols = ["source_file", "date", "split", "burst", "recording_fraction", "feature"]
    for key, group in metrics.groupby(group_cols, sort=False):
        group = group.sort_values("scale_frames")
        feature = key[-1]
        records = group.to_dict("records")
        for previous, current in zip(records[:-1], records[1:]):
            deltas = {}
            score_parts = []
            for descriptor in DESCRIPTORS:
                delta = (current[descriptor] - previous[descriptor]) / scaling[feature][descriptor]["mad"]
                deltas[f"delta_{descriptor}"] = float(delta)
                score_parts.append(delta)
            score = float(np.sqrt(np.nansum(np.square(score_parts)))) if np.isfinite(score_parts).all() else math.nan
            rows.append(
                {
                    **dict(zip(group_cols, key)),
                    "boundary_scale_frames": int(current["scale_frames"]),
                    "boundary_scale_seconds": float(current["scale_seconds"]),
                    "geometry_change_score": score,
                    **deltas,
                }
            )
    return pd.DataFrame(rows)


def calibrate_boundary_nulls(
    bursts: list[dict],
    winsor: dict,
    scaling: dict,
    boundaries: pd.DataFrame,
    permutations: int = 32,
) -> pd.DataFrame:
    """Attach the identical-scale timestamp-permutation null to every boundary."""
    calibration_rows = []
    for burst in bursts:
        for feature in FEATURE_ORDER:
            bounds = winsor[feature]
            signal = np.clip(burst["signals"][feature], bounds["q005"], bounds["q995"])
            finite = np.flatnonzero(np.isfinite(signal))
            null_by_scale = {int(scale): [] for scale in SCALES[1:]}
            for iteration in range(permutations):
                shuffled = signal.copy()
                rng = np.random.default_rng(
                    stable_seed("boundary-null", burst["source_file"], burst["burst"], feature, iteration)
                )
                shuffled[finite] = shuffled[finite][rng.permutation(len(finite))]
                scale_metrics = {int(scale): descriptors(shuffled, int(scale), feature) for scale in SCALES}
                for previous_scale, current_scale in zip(SCALES[:-1], SCALES[1:]):
                    previous = scale_metrics[int(previous_scale)]
                    current = scale_metrics[int(current_scale)]
                    parts = [
                        (current[name] - previous[name]) / scaling[feature][name]["mad"]
                        for name in DESCRIPTORS
                    ]
                    value = float(np.sqrt(np.sum(np.square(parts)))) if np.isfinite(parts).all() else math.nan
                    null_by_scale[int(current_scale)].append(value)
            observed_group = boundaries[
                (boundaries.source_file == burst["source_file"])
                & (boundaries.burst == burst["burst"])
                & (boundaries.feature == feature)
            ]
            for record in observed_group.itertuples():
                values = np.asarray(null_by_scale[int(record.boundary_scale_frames)], dtype=float)
                median = float(np.nanmedian(values))
                q95 = float(np.nanquantile(values, 0.95))
                null_scale = safe_scale(values)
                calibration_rows.append(
                    {
                        "source_file": record.source_file,
                        "burst": record.burst,
                        "feature": record.feature,
                        "boundary_scale_frames": int(record.boundary_scale_frames),
                        "null_median": median,
                        "null_q95": q95,
                        "null_excess_q95": float(record.geometry_change_score - q95),
                        "null_z_score": float((record.geometry_change_score - median) / null_scale),
                    }
                )
    calibration = pd.DataFrame(calibration_rows)
    return boundaries.merge(
        calibration,
        on=["source_file", "burst", "feature", "boundary_scale_frames"],
        how="left",
        validate="one_to_one",
    )


def fly_boundary_summary(boundaries: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "geometry_change_score",
        "null_median",
        "null_q95",
        "null_excess_q95",
        "null_z_score",
        "delta_persistence",
        "delta_retained_dispersion",
        "delta_abs_reversal_asymmetry",
    ]
    return (
        boundaries.groupby(
            ["source_file", "date", "split", "feature", "boundary_scale_frames", "boundary_scale_seconds"],
            as_index=False,
        )[columns]
        .median()
    )


def nominate(summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (source, feature), group in summary.groupby(["source_file", "feature"], sort=False):
        chosen = []
        eligible = group[
            group.boundary_scale_frames.isin(SCALES[2:-1])
            & (group.null_excess_q95 > 0)
            & group.null_z_score.notna()
        ]
        for record in eligible.sort_values("null_z_score", ascending=False).to_dict("records"):
            scale = int(record["boundary_scale_frames"])
            if all(abs(math.log2(scale / existing)) >= 2 for existing in chosen):
                chosen.append(scale)
                rows.append({**record, "nomination_rank": len(chosen)})
            if len(chosen) == 2:
                break
    return pd.DataFrame(rows, columns=[*summary.columns, "nomination_rank"])


def select_rungs(nominations: pd.DataFrame, summary: pd.DataFrame) -> list[dict]:
    rungs: list[dict] = []
    n_flies = int(summary.source_file.nunique())
    for feature in FEATURE_ORDER:
        feature_nominations = nominations[nominations.feature == feature]
        candidates = []
        for scale in SCALES[1:-1]:
            supporters = []
            for source, group in feature_nominations.groupby("source_file"):
                if any(abs(math.log2(value / scale)) <= 1 for value in group.boundary_scale_frames):
                    supporters.append(source)
            local = summary[
                (summary.feature == feature)
                & (np.abs(np.log2(summary.boundary_scale_frames / scale)) <= 1)
            ]
            candidates.append(
                {
                    "feature": feature,
                    "scale_frames": int(scale),
                    "support_flies": len(supporters),
                    "support_fraction": len(supporters) / n_flies,
                    "supporting_sources": sorted(supporters),
                    "median_local_score": float(local.geometry_change_score.median()),
                    "median_local_null_z": float(local.null_z_score.median()),
                }
            )
        chosen = []
        for candidate in sorted(candidates, key=lambda row: (-row["support_flies"], -row["median_local_null_z"])):
            if candidate["support_flies"] < 4:
                continue
            scale = candidate["scale_frames"]
            if all(abs(math.log2(scale / existing)) >= 2 for existing in chosen):
                chosen.append(scale)
                local = summary[
                    (summary.feature == feature)
                    & (np.abs(np.log2(summary.boundary_scale_frames / scale)) <= 1)
                ]
                candidate["direction_vector"] = {
                    descriptor: float(local[f"delta_{descriptor}"].median()) for descriptor in DESCRIPTORS
                }
                candidate["scale_seconds_at_99_96fps"] = scale / 99.96
                rungs.append(candidate)
            if len(chosen) == 2:
                break
    for feature in FEATURE_ORDER:
        feature_rungs = sorted([row for row in rungs if row["feature"] == feature], key=lambda row: row["scale_frames"])
        for index, row in enumerate(feature_rungs):
            row["rung_label"] = "micro" if index == 0 else "bout"
    return rungs


def fit_amount_mappings(metrics: pd.DataFrame, rungs: list[dict]) -> dict:
    mappings = {}
    for rung in rungs:
        feature, scale = rung["feature"], rung["scale_frames"]
        values = metrics[(metrics.feature == feature) & (metrics.scale_frames == scale)].amount.to_numpy(float)
        mappings[f"{feature}|{scale}"] = {
            "median": float(np.nanmedian(values)),
            "mad": safe_scale(values),
            "units": FEATURE_META[feature]["units"],
        }
    return mappings


def quality_table(bursts: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                key: burst[key]
                for key in (
                    "source_file",
                    "date",
                    "split",
                    "burst",
                    "recording_fraction",
                    "fps",
                    "reference_body_length_pixels",
                    "core_valid_fraction",
                    "appendage_valid_fraction",
                    "lr_valid_fraction",
                    "idle_fraction",
                    "locomotion_fraction",
                    "on_edge_fraction",
                    "temperature_median",
                    "relative_humidity_median",
                )
            }
            for burst in bursts
        ]
    )


def ara_table(metrics: pd.DataFrame, mappings: dict) -> pd.DataFrame:
    rows = []
    for key, mapping in mappings.items():
        feature, scale_text = key.split("|")
        scale = int(scale_text)
        part = metrics[(metrics.feature == feature) & (metrics.scale_frames == scale)].copy()
        part["ARA_coordinate"] = 1 + np.tanh((part.amount - mapping["median"]) / (2 * mapping["mad"]))
        rows.append(part)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def development_nulls(bursts: list[dict], config: dict, permutations: int = 32) -> pd.DataFrame:
    rung_lookup = {(row["feature"], row["scale_frames"]): row for row in config["rungs"]}
    rows = []
    for burst in bursts:
        for feature, scale in rung_lookup:
            bounds = config["winsor"][feature]
            signal = np.clip(burst["signals"][feature], bounds["q005"], bounds["q995"])
            previous_scale = scale // 2
            observed_previous = descriptors(signal, previous_scale, feature)
            observed_current = descriptors(signal, scale, feature)

            def score(a: dict, b: dict) -> float:
                parts = [
                    (b[name] - a[name]) / config["descriptor_scaling"][feature][name]["mad"]
                    for name in DESCRIPTORS
                ]
                return float(np.sqrt(np.sum(np.square(parts)))) if np.isfinite(parts).all() else math.nan

            observed = score(observed_previous, observed_current)
            null_values = []
            valid = np.flatnonzero(np.isfinite(signal))
            for iteration in range(permutations):
                shuffled = signal.copy()
                rng = np.random.default_rng(stable_seed(burst["source_file"], burst["burst"], feature, iteration))
                shuffled[valid] = shuffled[valid][rng.permutation(len(valid))]
                null_values.append(score(descriptors(shuffled, previous_scale, feature), descriptors(shuffled, scale, feature)))
            reverse = signal[::-1]
            reverse_asymmetry = descriptors(reverse, scale, feature)["reversal_asymmetry"]
            rows.append(
                {
                    "source_file": burst["source_file"],
                    "burst": burst["burst"],
                    "recording_fraction": burst["recording_fraction"],
                    "feature": feature,
                    "scale_frames": scale,
                    "observed_score": observed,
                    "permuted_median": float(np.nanmedian(null_values)),
                    "permuted_q95": float(np.nanquantile(null_values, 0.95)),
                    "observed_reversal_asymmetry": observed_current["reversal_asymmetry"],
                    "reversed_reversal_asymmetry": reverse_asymmetry,
                }
            )
    return pd.DataFrame(rows)


def common_bands(rungs: list[dict]) -> list[dict]:
    bands = []
    for scale in sorted({int(row["scale_frames"]) for row in rungs}):
        members = [
            row for row in rungs if abs(math.log2(row["scale_frames"] / scale)) <= 1
        ]
        features = sorted({row["feature"] for row in members})
        if len(features) >= 3:
            centre = int(round(float(np.median([row["scale_frames"] for row in members]))))
            bands.append({"centre_scale_frames": centre, "features": features, "feature_count": len(features)})
    chosen = []
    for band in sorted(bands, key=lambda row: (-row["feature_count"], row["centre_scale_frames"])):
        if all(abs(math.log2(band["centre_scale_frames"] / prior["centre_scale_frames"])) >= 2 for prior in chosen):
            chosen.append(band)
    return chosen


def fit_development(cache_dir: Path) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    bursts, files = load_split(cache_dir)
    if {burst["split"] for burst in bursts} != {"development"}:
        raise RuntimeError("development fit received a non-development cache")
    winsor = fit_winsor(bursts)
    metrics = metric_table(bursts, winsor)
    scaling = fit_descriptor_scaling(metrics)
    boundaries = calibrate_boundary_nulls(bursts, winsor, scaling, boundary_table(metrics, scaling))
    summary = fly_boundary_summary(boundaries)
    nominations = nominate(summary)
    rungs = select_rungs(nominations, summary)
    mappings = fit_amount_mappings(metrics, rungs)
    config = {
        "status": "frozen from development before experiment-4 exposure",
        "protocol": "T450A_FROZEN_PROTOCOL.md",
        "development_sources": sorted({burst["source_file"] for burst in bursts}),
        "feature_order": list(FEATURE_ORDER),
        "feature_meta": FEATURE_META,
        "scales_frames": SCALES.tolist(),
        "winsor": winsor,
        "descriptor_scaling": scaling,
        "rungs": rungs,
        "common_parent_candidates": common_bands(rungs),
        "amount_ara_mappings": mappings,
    }
    nulls = development_nulls(bursts, config)
    quality_table(bursts).to_csv(RESULTS / "T450A_development_quality.csv", index=False)
    metrics.to_csv(RESULTS / "T450A_development_scale_metrics.csv", index=False)
    boundaries.to_csv(RESULTS / "T450A_development_boundaries.csv", index=False)
    summary.to_csv(RESULTS / "T450A_development_fly_boundaries.csv", index=False)
    nominations.to_csv(RESULTS / "T450A_development_nominations.csv", index=False)
    ara_table(metrics, mappings).to_csv(RESULTS / "T450A_development_ara_coordinates.csv", index=False)
    nulls.to_csv(RESULTS / "T450A_development_controls.csv", index=False)
    (RESULTS / "T450A_FROZEN_CONFIG.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    result = {
        "files": len(files),
        "bursts": len(bursts),
        "rungs": rungs,
        "common_parent_candidates": config["common_parent_candidates"],
        "quality": {
            "core_valid_min": min(burst["core_valid_fraction"] for burst in bursts),
            "appendage_valid_min": min(burst["appendage_valid_fraction"] for burst in bursts),
            "lr_valid_min": min(burst["lr_valid_fraction"] for burst in bursts),
        },
    }
    (RESULTS / "T450A_DEVELOPMENT_RESULT.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


def evaluate_holdout(cache_dir: Path) -> None:
    config_path = RESULTS / "T450A_FROZEN_CONFIG.json"
    if not config_path.exists():
        raise FileNotFoundError("fit development and freeze T450A_FROZEN_CONFIG.json first")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    bursts, files = load_split(cache_dir)
    if {burst["split"] for burst in bursts} != {"holdout"}:
        raise RuntimeError("holdout evaluation received a non-holdout cache")
    metrics = metric_table(bursts, config["winsor"])
    boundaries = calibrate_boundary_nulls(
        bursts,
        config["winsor"],
        config["descriptor_scaling"],
        boundary_table(metrics, config["descriptor_scaling"]),
    )
    summary = fly_boundary_summary(boundaries)
    nominations = nominate(summary)
    transfer_rows = []
    for rung in config["rungs"]:
        feature, scale = rung["feature"], int(rung["scale_frames"])
        dev_direction = rung["direction_vector"]
        for source in sorted(summary.source_file.unique()):
            candidates = nominations[(nominations.source_file == source) & (nominations.feature == feature)].copy()
            if candidates.empty:
                transfer_rows.append(
                    {
                        "feature": feature,
                        "frozen_scale_frames": scale,
                        "frozen_scale_seconds": scale / 99.96,
                        "source_file": source,
                        "matched_holdout_scale_frames": math.nan,
                        "matched_holdout_scale_seconds": math.nan,
                        "octave_distance": math.nan,
                        "within_one_octave": 0,
                        "direction_agreement_count": 0,
                        "direction_agreement_available": 0,
                        "direction_agrees_2_of_3": 0,
                        "fly_transfer": 0,
                    }
                )
                continue
            candidates["octave_distance"] = np.abs(np.log2(candidates.boundary_scale_frames / scale))
            matched = candidates.sort_values(["octave_distance", "geometry_change_score"], ascending=[True, False]).iloc[0]
            direction_agreements = []
            for descriptor in DESCRIPTORS:
                expected = float(dev_direction[descriptor])
                observed = float(matched[f"delta_{descriptor}"])
                if abs(expected) > 1e-12 and math.isfinite(observed):
                    direction_agreements.append(np.sign(expected) == np.sign(observed))
            transfer_rows.append(
                {
                    "feature": feature,
                    "frozen_scale_frames": scale,
                    "frozen_scale_seconds": scale / 99.96,
                    "source_file": source,
                    "matched_holdout_scale_frames": int(matched.boundary_scale_frames),
                    "matched_holdout_scale_seconds": float(matched.boundary_scale_seconds),
                    "octave_distance": float(matched.octave_distance),
                    "within_one_octave": int(matched.octave_distance <= 1),
                    "direction_agreement_count": int(sum(direction_agreements)),
                    "direction_agreement_available": len(direction_agreements),
                    "direction_agrees_2_of_3": int(sum(direction_agreements) >= 2),
                    "fly_transfer": int(matched.octave_distance <= 1 and sum(direction_agreements) >= 2),
                }
            )
    transfer = pd.DataFrame(transfer_rows)
    rung_transfer = []
    if not transfer.empty:
        for (feature, scale), group in transfer.groupby(["feature", "frozen_scale_frames"]):
            rung_transfer.append(
                {
                    "feature": feature,
                    "frozen_scale_frames": int(scale),
                    "holdout_flies": int(group.source_file.nunique()),
                    "flies_transferred": int(group.fly_transfer.sum()),
                    "both_flies_transfer": bool(group.source_file.nunique() == 2 and group.fly_transfer.sum() == 2),
                }
            )
    quality_table(bursts).to_csv(RESULTS / "T450A_holdout_quality.csv", index=False)
    metrics.to_csv(RESULTS / "T450A_holdout_scale_metrics.csv", index=False)
    boundaries.to_csv(RESULTS / "T450A_holdout_boundaries.csv", index=False)
    summary.to_csv(RESULTS / "T450A_holdout_fly_boundaries.csv", index=False)
    nominations.to_csv(RESULTS / "T450A_holdout_nominations.csv", index=False)
    ara_table(metrics, config["amount_ara_mappings"]).to_csv(RESULTS / "T450A_holdout_ara_coordinates.csv", index=False)
    transfer.to_csv(RESULTS / "T450A_holdout_transfer.csv", index=False)
    result = {
        "status": "untouched experiment-4 transfer evaluated with frozen development configuration",
        "files": len(files),
        "bursts": len(bursts),
        "rung_transfer": rung_transfer,
        "quality": {
            "core_valid_min": min(burst["core_valid_fraction"] for burst in bursts),
            "appendage_valid_min": min(burst["appendage_valid_fraction"] for burst in bursts),
            "lr_valid_min": min(burst["lr_valid_fraction"] for burst in bursts),
        },
    }
    (RESULTS / "T450A_HOLDOUT_RESULT.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=("fit-development", "evaluate-holdout"))
    parser.add_argument("--cache-root", default=str(HERE / "cache"))
    args = parser.parse_args()
    cache_root = Path(args.cache_root)
    if args.mode == "fit-development":
        fit_development(cache_root / "development")
    else:
        evaluate_holdout(cache_root / "holdout")


if __name__ == "__main__":
    main()
