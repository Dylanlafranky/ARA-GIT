"""Independent validator for Q38's fixed-anchor phase-cycle test."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
DATA = HERE / "public_data" / "q38_fixed_anchor_mimic"
ARCHIVE = DATA / "unnati_submit_12_pure_mimic.hdf5.zip"
HDF = DATA / "unnati_submit_12_pure_mimic.hdf5"
DERIVED = DATA / "q38_derived_cache.npz"
CONNECTED = DATA / "q38_connected_cache.npy"
EVENTS = HERE / "Q38_FIXED_ANCHOR_PHASE_CYCLE_EVENTS.csv.gz"
RESULTS = HERE / "Q38_FIXED_ANCHOR_PHASE_CYCLE_RESULTS.json"
PROTOCOL = HERE / "Q38_FIXED_ANCHOR_PHASE_CYCLE_PROTOCOL_v1_FROZEN.md"
FIDELITY = HERE / "Q38_FIXED_ANCHOR_PHASE_CYCLE_FIDELITY_v1.md"
OUTPUT = HERE / "Q38_FIXED_ANCHOR_PHASE_CYCLE_VALIDATION.json"

EXPECTED = {
    "archive_md5": "04477abdac1849dd034576c0dbb685cb",
    "protocol_sha256": "166551802e124688acc898033435a964534c02dc2f15ded75ce4dabcba56eda6",
    "fidelity_sha256": "ff97db53aa769964c6178657f98c5fed356966577723b40bef05e342c259f70e",
    "archive_size": 224_548_658,
    "hdf_size": 3_452_716_648,
}

PRE = np.arange(-7, -2, dtype=np.int16)
POST = np.arange(1, 15, dtype=np.int16)
EVAL_FIRST, EVAL_LAST = 258, 485
TIME_SHIFT = 37
BOOTSTRAP_SEED = 381027
BOOTSTRAP_DRAWS = 20_000
EPS = 1e-12
VARIANTS = ("exact", "time", "pair", "network")


def digest(path: Path, algorithm: str) -> str:
    value = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def circulation(phase: np.ndarray) -> float:
    turn = np.angle(np.conj(phase[:-1]) * phase[1:])
    turn = turn[np.isfinite(turn) & (np.abs(turn) > 1e-10)]
    return float(abs(np.mean(np.sign(turn)))) if turn.size else 0.0


def eligibility(closure: np.ndarray) -> np.ndarray:
    development = np.asarray(closure[0, :, :250], dtype=np.float64)
    flow = np.diff(development, axis=1)
    lo, hi = np.quantile(development, [0.05, 0.95], axis=1)
    centre, radius = (lo + hi) / 2, (hi - lo) / 2
    scale = np.quantile(np.abs(flow), 0.95, axis=1)
    plane = (
        (development[:, :249] - centre[:, None]) / radius[:, None]
        + 1j * flow / scale[:, None]
    )
    phase = plane / np.abs(plane)
    eligible = np.zeros((100, 66), dtype=bool)
    for seed in range(100):
        for pair in range(66):
            line = plane[seed, :, pair]
            valid = np.isfinite(line.real) & np.isfinite(line.imag)
            if np.mean(valid) < 0.95:
                continue
            quadrant = 2 * (line.real[valid] >= 0) + (line.imag[valid] >= 0)
            minimum = min(np.mean(quadrant == q) for q in range(4))
            eligible[seed, pair] = (
                minimum >= 0.05
                and circulation(phase[seed, valid, pair]) >= 0.80
            )
    return eligible


def event_times(line: np.ndarray, threshold: float) -> list[int]:
    kept: list[int] = []
    for time in range(EVAL_FIRST, EVAL_LAST + 1):
        event = (
            line[time - 1] > line[time]
            and line[time] <= line[time + 1]
            and line[time] <= threshold
        )
        if event and (not kept or time - kept[-1] >= 14):
            kept.append(time)
    return kept


def shift(time: int) -> int:
    width = EVAL_LAST - EVAL_FIRST + 1
    return EVAL_FIRST + ((time - EVAL_FIRST + TIME_SHIFT) % width)


def raw_metrics(
    branch: int,
    seed: int,
    pair: int,
    time: int,
    closure: np.ndarray,
    connected: np.ndarray,
) -> dict[str, float]:
    before = np.asarray(
        connected[branch, seed, time + PRE, pair], dtype=np.float64
    )
    before_amp = np.linalg.norm(before, axis=(-2, -1))
    anchor_index = int(np.argmax(before_amp))
    anchor = before[anchor_index]
    anchor_amp = float(before_amp[anchor_index])
    anchor_offset = int(PRE[anchor_index])
    anchor_h = float(closure[branch, seed, time + anchor_offset, pair])
    after = np.asarray(
        connected[branch, seed, time + POST, pair], dtype=np.float64
    )
    after_amp = np.linalg.norm(after, axis=(-2, -1))
    denom = anchor_amp * after_amp
    relation = np.divide(
        np.sum(anchor * after, axis=(-2, -1)),
        denom,
        out=np.full(14, np.nan),
        where=denom > EPS,
    )
    amp_ratio = after_amp / anchor_amp
    h_ratio = (
        np.asarray(closure[branch, seed, time + POST, pair], dtype=np.float64)
        / anchor_h
    )
    reliable = np.isfinite(relation) & (amp_ratio >= 0.10)
    early = np.flatnonzero(reliable[:7])
    if early.size:
        b_index = int(early[np.argmin(relation[early])])
        r_b = float(relation[b_index])
        j_b = b_index + 1
        amp_b = float(amp_ratio[b_index])
        h_b = float(h_ratio[b_index])
    else:
        b_index, j_b, r_b, amp_b, h_b = -1, -1, np.nan, np.nan, np.nan
    later = (
        np.flatnonzero(
            reliable & (np.arange(14) > b_index) & (amp_ratio >= 0.50)
        )
        if b_index >= 0
        else np.empty(0, dtype=int)
    )
    if later.size:
        best = np.max(relation[later])
        return_index = int(later[np.flatnonzero(relation[later] == best)[0]])
        r_return = float(relation[return_index])
        j_return = return_index + 1
        amp_return = float(amp_ratio[return_index])
        h_return = float(h_ratio[return_index])
    else:
        r_return, j_return, amp_return, h_return = np.nan, -1, np.nan, np.nan
    b_entry = bool(np.isfinite(r_b) and r_b <= -0.25)
    strong_b = bool(np.isfinite(r_b) and r_b <= -0.50)
    a_return = bool(np.isfinite(r_return) and r_return >= 0.25)
    cycle = bool(b_entry and a_return)
    score = (
        float(min(-r_b, r_return))
        if np.isfinite(r_b) and np.isfinite(r_return)
        else -1.0
    )
    result = {
        "anchor_offset": float(anchor_offset),
        "anchor_amplitude": anchor_amp,
        "anchor_closure": anchor_h,
        "r_b": r_b,
        "j_b": float(j_b),
        "amplitude_b": amp_b,
        "closure_b": h_b,
        "phase_b_entry": float(b_entry),
        "strong_phase_b": float(strong_b),
        "r_return": r_return,
        "j_return": float(j_return),
        "amplitude_return": amp_return,
        "closure_return": h_return,
        "phase_a_return": float(a_return),
        "cycle": float(cycle),
        "cycle_score": score,
    }
    result.update({f"r_{j}": float(relation[j - 1]) for j in POST})
    result.update({f"a_{j}": float(amp_ratio[j - 1]) for j in POST})
    return result


def summarize(frame: pd.DataFrame, variant: str) -> dict[str, object]:
    def array(metric: str) -> np.ndarray:
        return frame[f"{variant}_{metric}"].to_numpy(float)

    cycle, score, strong = array("cycle"), array("cycle_score"), array(
        "strong_phase_b"
    )
    r_b, r_return = array("r_b"), array("r_return")
    j_b, j_return = array("j_b"), array("j_return")
    amp_b, amp_return = array("amplitude_b"), array("amplitude_return")
    grouped = frame.groupby(["seed", "source_pair"], sort=True)
    lineage_cycle = grouped[f"{variant}_cycle"].mean().to_numpy(float)
    lineage_score = grouped[f"{variant}_cycle_score"].mean().to_numpy(float)
    complete = cycle > 0.5
    return {
        "events": int(len(frame)),
        "cycle_fraction": float(np.mean(cycle)),
        "strong_phase_b_fraction": float(np.mean(strong)),
        "cycle_score_mean": float(np.mean(score)),
        "cycle_score_median": float(np.median(score)),
        "lineages_cycle_ge_half_fraction": float(np.mean(lineage_cycle >= 0.50)),
        "lineage_cycle_mean": float(np.mean(lineage_cycle)),
        "lineage_score_mean": float(np.mean(lineage_score)),
        "r_b_mean": float(np.nanmean(r_b)),
        "r_b_median": float(np.nanmedian(r_b)),
        "r_return_mean": float(np.nanmean(r_return)),
        "r_return_median": float(np.nanmedian(r_return)),
        "j_b_median": float(np.nanmedian(j_b[j_b > 0])),
        "j_return_completed_median": float(np.median(j_return[complete]))
        if np.any(complete)
        else np.nan,
        "amplitude_b_median": float(np.nanmedian(amp_b)),
        "amplitude_return_completed_median": float(np.median(amp_return[complete]))
        if np.any(complete)
        else np.nan,
        **{
            f"offset_{label}": [
                float(function(array(f"r_{offset}"), value))
                if value is not None
                else float(function(array(f"r_{offset}")))
                for offset in POST
            ]
            for label, function, value in (
                ("median", np.nanmedian, None),
                ("q25", np.nanquantile, 0.25),
                ("q75", np.nanquantile, 0.75),
                ("q05", np.nanquantile, 0.05),
                ("q95", np.nanquantile, 0.95),
            )
        },
    }


def bootstrap(
    frame: pd.DataFrame,
    exact_key: str,
    control_key: str | None = None,
    null: float = 0.0,
) -> float:
    difference = (
        frame[exact_key].to_numpy(float) - null
        if control_key is None
        else frame[exact_key].to_numpy(float)
        - frame[control_key].to_numpy(float)
    )
    clusters = (
        pd.DataFrame({"seed": frame["seed"], "difference": difference})
        .groupby("seed", sort=True)["difference"]
        .mean()
        .to_numpy(float)
    )
    rng = np.random.default_rng(
        BOOTSTRAP_SEED
        + sum(map(ord, exact_key))
        + (sum(map(ord, control_key)) if control_key else 0)
    )
    draws = rng.choice(
        clusters, size=(BOOTSTRAP_DRAWS, clusters.size), replace=True
    ).mean(axis=1)
    return float(np.mean(draws > 0))


def floats_match(left: object, right: object, tolerance: float = 1e-11) -> bool:
    a, b = float(left), float(right)
    return (np.isnan(a) and np.isnan(b)) or bool(
        np.isclose(a, b, atol=tolerance, rtol=tolerance)
    )


def main() -> None:
    stored = json.loads(RESULTS.read_text(encoding="utf-8"))
    derived = np.load(DERIVED)
    closure = derived["closure"]
    connected = np.load(CONNECTED, mmap_mode="r")
    frame = pd.read_csv(EVENTS, compression="gzip")
    provenance = {
        "archive_md5": digest(ARCHIVE, "md5"),
        "protocol_sha256": digest(PROTOCOL, "sha256"),
        "fidelity_sha256": digest(FIDELITY, "sha256"),
        "archive_size": ARCHIVE.stat().st_size,
        "hdf_size": HDF.stat().st_size,
    }
    checks: dict[str, bool] = {
        "provenance_and_sizes": provenance == EXPECTED,
        "cache_shapes": (
            closure.shape == (2, 100, 500, 66)
            and connected.shape == (2, 100, 500, 66, 3, 3)
        ),
    }

    eligible = eligibility(closure)
    expected_events: list[tuple[int, int, int]] = []
    seeds: set[int] = set()
    lineages: set[tuple[int, int]] = set()
    for seed in range(100):
        for pair in np.flatnonzero(eligible[seed]):
            pair = int(pair)
            controls = [
                int(q) for q in np.flatnonzero(eligible[seed]) if int(q) != pair
            ]
            if not controls:
                continue
            threshold = float(np.quantile(closure[0, seed, :250, pair], 0.20))
            for time in event_times(closure[0, seed, :, pair], threshold):
                expected_events.append((seed, pair, time))
                seeds.add(seed)
                lineages.add((seed, pair))
    exported_events = list(
        frame[["seed", "source_pair", "time"]].itertuples(index=False, name=None)
    )
    eligibility_counts = {
        "complete_c2_lineages": int(np.sum(eligible)),
        "events": len(expected_events),
        "represented_seeds": len(seeds),
        "represented_lineages": len(lineages),
    }
    checks["eligibility_counts"] = eligibility_counts == stored["eligibility"]
    checks["complete_event_list"] = expected_events == exported_events

    sample_indices = np.unique(np.linspace(0, len(frame) - 1, 24, dtype=int))
    max_error = 0.0
    raw_checks = 0
    for index in sample_indices:
        row = frame.iloc[index]
        seed, pair, time = int(row.seed), int(row.source_pair), int(row.time)
        specifications = {
            "exact": (0, seed, pair, time),
            "time": (0, seed, pair, shift(time)),
            "pair": (0, seed, int(row.pair_control), time),
            "network": (1, seed, pair, time),
        }
        for variant, specification in specifications.items():
            calculated = raw_metrics(*specification, closure, connected)
            for metric, value in calculated.items():
                recorded = float(row[f"{variant}_{metric}"])
                error = (
                    0.0
                    if np.isnan(value) and np.isnan(recorded)
                    else abs(value - recorded)
                )
                max_error = max(max_error, error)
                raw_checks += 1
    checks["sampled_raw_metrics"] = max_error <= 1e-11

    summaries = {variant: summarize(frame, variant) for variant in VARIANTS}
    summary_matches: list[bool] = []
    for variant in VARIANTS:
        for key, value in summaries[variant].items():
            recorded = stored["summary"][variant][key]
            if isinstance(value, list):
                summary_matches.extend(
                    floats_match(a, b) for a, b in zip(value, recorded)
                )
            else:
                summary_matches.append(floats_match(value, recorded))
    checks["all_summaries"] = all(summary_matches)

    boot = {
        "cycle_above_half": bootstrap(frame, "exact_cycle", null=0.50),
        "cycle_vs_controls": {
            variant: bootstrap(frame, "exact_cycle", f"{variant}_cycle")
            for variant in ("time", "pair", "network")
        },
        "score_vs_controls": {
            variant: bootstrap(
                frame, "exact_cycle_score", f"{variant}_cycle_score"
            )
            for variant in ("time", "pair", "network")
        },
    }
    checks["all_bootstraps"] = (
        floats_match(boot["cycle_above_half"], stored["bootstrap"]["cycle_above_half"])
        and all(
            floats_match(
                boot[family][variant], stored["bootstrap"][family][variant]
            )
            for family in ("cycle_vs_controls", "score_vs_controls")
            for variant in ("time", "pair", "network")
        )
    )

    exact = summaries["exact"]
    eligibility_pass = (
        eligibility_counts["events"] >= 2000
        and eligibility_counts["represented_seeds"] >= 80
        and eligibility_counts["represented_lineages"] >= 500
    )
    gates = {
        "events_cycle_ge_0_55": exact["cycle_fraction"] >= 0.55,
        "lineages_cycle_ge_half_ge_0_55": exact[
            "lineages_cycle_ge_half_fraction"
        ]
        >= 0.55,
        "bootstrap_cycle_above_half_ge_0_99": boot["cycle_above_half"] >= 0.99,
        "median_score_ge_0_25": exact["cycle_score_median"] >= 0.25,
        "cycle_beats_controls_by_0_10": all(
            exact["cycle_fraction"] >= summaries[v]["cycle_fraction"] + 0.10
            for v in ("time", "pair", "network")
        ),
        "score_beats_controls_by_0_10": all(
            exact["cycle_score_mean"] >= summaries[v]["cycle_score_mean"] + 0.10
            for v in ("time", "pair", "network")
        ),
        "bootstrap_cycle_controls_ge_0_95": all(
            boot["cycle_vs_controls"][v] >= 0.95
            for v in ("time", "pair", "network")
        ),
        "bootstrap_score_controls_ge_0_95": all(
            boot["score_vs_controls"][v] >= 0.95
            for v in ("time", "pair", "network")
        ),
    }
    checks["gates_and_verdict_inputs"] = (
        gates == stored["gates"]
        and eligibility_pass == stored["eligibility_pass"]
    )
    result = {
        "test_id": "Q38-INDEPENDENT-VALIDATION-v1",
        "date": "2026-07-27",
        "pass": all(checks.values()),
        "checks": checks,
        "provenance": provenance,
        "eligibility": eligibility_counts,
        "sampled_rows": int(len(sample_indices)),
        "sampled_metric_checks": raw_checks,
        "sampled_max_absolute_error": max_error,
        "bootstrap": boot,
        "verdict": stored["verdict"],
    }
    OUTPUT.write_text(
        json.dumps(result, indent=2, allow_nan=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, allow_nan=True))
    if not result["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
