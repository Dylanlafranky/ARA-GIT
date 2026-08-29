from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source" / "MH_01_easy_state_groundtruth.csv"
RESULTS = ROOT / "results"


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    source = pd.read_csv(SOURCE)
    source.columns = [column.strip() for column in source.columns]
    sample = pd.read_csv(RESULTS / "T447_HOLDOUT_RECONSTRUCTION_SAMPLE.csv")
    metrics = pd.read_csv(RESULTS / "T447_METHOD_METRICS.csv")
    shuffle = pd.read_csv(RESULTS / "T447_SHUFFLED_THIRD_CONTROLS.csv")
    axes = pd.read_csv(RESULTS / "T447_AXIS_SCAN.csv")
    with (RESULTS / "T447_RESULT.json").open(encoding="utf-8") as handle:
        result = json.load(handle)

    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": detail})

    q_columns = ["q_RS_w []", "q_RS_x []", "q_RS_y []", "q_RS_z []"]
    check("source_columns", all(column in source.columns for column in ["#timestamp", *q_columns]), str(source.columns.tolist()))
    check("source_rows", len(source) == 36382, f"rows={len(source)}")
    check("source_hash", hash_file(SOURCE) == result["quality"]["source_sha256"], hash_file(SOURCE))
    timestamps = source["#timestamp"].to_numpy(np.int64)
    check("timestamps_strictly_increase", bool(np.all(np.diff(timestamps) > 0)), f"minimum_delta_ns={int(np.min(np.diff(timestamps)))}")

    q_raw = source[q_columns].to_numpy(float)
    raw_norm = np.linalg.norm(q_raw, axis=1)
    q = q_raw / raw_norm[:, None]
    check("normalization_identity", bool(np.allclose(np.sum(q**2, axis=1), 1, atol=2e-15)), f"max_norm_error={float(np.max(np.abs(np.linalg.norm(q, axis=1)-1))):.3e}")
    check("raw_norm_range", float(raw_norm.min()) > 0.9999 and float(raw_norm.max()) < 1.0001, f"range=({raw_norm.min():.9f},{raw_norm.max():.9f})")
    check("no_quaternion_sign_jump", int(np.sum(np.sum(q[1:] * q[:-1], axis=1) < 0)) == 0, "adjacent quaternion dot products remain non-negative")

    split_index = int(np.floor(0.7 * len(q)))
    holdout = q[split_index:]
    actual = np.abs(holdout[:, 0])
    pred_three = np.sqrt(np.maximum(0, 1 - np.sum(holdout[:, 1:] ** 2, axis=1)))
    pred_two = np.sqrt(np.maximum(0, (1 - holdout[:, 1] ** 2 - holdout[:, 2] ** 2) / 2))
    mae_three = float(np.mean(np.abs(pred_three - actual)))
    mae_two = float(np.mean(np.abs(pred_two - actual)))
    saved_three = float(metrics.loc[metrics["method"] == "three independent cuts (x,y,z)", "mae"].iloc[0])
    saved_two = float(metrics.loc[metrics["method"] == "two cuts (x,y), equal hidden split", "mae"].iloc[0])
    check("manual_three_cut_mae", np.isclose(mae_three, saved_three, rtol=0, atol=2e-17), f"manual={mae_three:.12g}, saved={saved_three:.12g}; difference is below one tenth of float64 epsilon")
    check("manual_two_cut_mae", np.isclose(mae_two, saved_two, rtol=1e-10, atol=1e-14), f"manual={mae_two:.12g}, saved={saved_two:.12g}")
    check("three_cut_exact_after_normalization", saved_three < 1e-12, f"MAE={saved_three:.3e}")
    check("two_cut_not_identifiable", saved_two > 0.1, f"MAE={saved_two:.6f}")

    rank_two = int(np.linalg.matrix_rank(q[:split_index, 1:3]))
    redundant = np.column_stack([q[:split_index, 1], q[:split_index, 2], q[:split_index, 1] - q[:split_index, 2]])
    rank_redundant = int(np.linalg.matrix_rank(redundant))
    rank_three = int(np.linalg.matrix_rank(q[:split_index, 1:]))
    check("rank_two", rank_two == 2 == result["primary"]["rank_two"], f"rank={rank_two}")
    check("redundant_axis_adds_no_rank", rank_redundant == 2 == result["primary"]["rank_redundant"], f"rank={rank_redundant}")
    check("independent_third_adds_rank", rank_three == 3 == result["primary"]["rank_three"], f"rank={rank_three}")
    redundant_mae = float(metrics.loc[metrics["method"] == "two cuts + redundant x−y", "mae"].iloc[0])
    check("redundant_prediction_equals_two_cut", np.isclose(redundant_mae, saved_two, atol=1e-15), f"two={saved_two:.12g}, redundant={redundant_mae:.12g}")

    shuffle_median = float(shuffle["mae"].median())
    check("shuffle_count", len(shuffle) == 200 and shuffle["draw"].nunique() == 200, f"rows={len(shuffle)}")
    check("event_linked_beats_shuffled", saved_three < shuffle["mae"].min(), f"linked={saved_three:.3e}, shuffle_min={shuffle['mae'].min():.6f}")
    check("shuffle_summary", np.isclose(shuffle_median, result["primary"]["shuffled_third_mae_median"], atol=1e-14), f"median={shuffle_median:.12g}")

    raw_radius = float(np.median(raw_norm[:split_index]))
    raw_pred = np.sqrt(np.maximum(0, raw_radius**2 - np.sum(q_raw[split_index:, 1:] ** 2, axis=1)))
    raw_mae = float(np.mean(np.abs(raw_pred - np.abs(q_raw[split_index:, 0]))))
    check("raw_recorded_sensitivity", np.isclose(raw_mae, result["primary"]["raw_three_cut"]["mae"], rtol=1e-9), f"MAE={raw_mae:.12g}")
    check("raw_result_still_precise", raw_mae < 1e-5, f"MAE={raw_mae:.3e}")

    sign_changes = [int(np.sum(np.signbit(q[1:, i]) != np.signbit(q[:-1, i]))) for i in range(4)]
    saved_changes = axes.set_index("hidden_component").loc[["w", "x", "y", "z"], "source_sign_changes"].astype(int).tolist()
    check("axis_scan_sign_changes", sign_changes == saved_changes, f"manual={sign_changes}, saved={saved_changes}")
    check("primary_w_no_crossing", sign_changes[0] == 0 and not result["branch"]["identifiable"], f"w_crossings={sign_changes[0]}")
    check("exploratory_axes_expose_boundary", sign_changes[1] > 0 and sign_changes[3] > 0, f"x={sign_changes[1]}, z={sign_changes[3]}")

    first = sample.iloc[0]
    manual = float(np.sqrt(max(0, 1 - first["x"] ** 2 - first["y"] ** 2 - first["z"] ** 2)))
    check("sample_record_trace", np.isclose(manual, first["pred_three_independent"], atol=1e-14), f"row_id={int(first['row_id'])}, manual={manual:.12g}")
    check("holdout_sample_bounded", len(sample) == 1200 and sample["split"].eq("holdout").all(), f"rows={len(sample)}")

    visual_paths = [RESULTS / "T447_GEOMETRY_FIRST.png", RESULTS / "T447_PAIR_PLANES_AND_BOUNDARY.png"]
    check("visual_outputs", all(path.exists() and path.stat().st_size > 100_000 for path in visual_paths), str({path.name: path.stat().st_size if path.exists() else 0 for path in visual_paths}))
    required_outputs = [
        RESULTS / "T447_RESULT.json",
        RESULTS / "T447_ANALYSIS.sqlite",
        RESULTS / "T447_METHOD_METRICS.csv",
        RESULTS / "T447_AXIS_SCAN.csv",
        RESULTS / "T447_SHUFFLED_THIRD_CONTROLS.csv",
    ]
    check("required_outputs", all(path.exists() and path.stat().st_size > 0 for path in required_outputs), str([path.name for path in required_outputs]))

    passed = sum(bool(item["pass"]) for item in checks)
    validation = {
        "test": "T447",
        "checks_passed": passed,
        "checks_total": len(checks),
        "all_passed": passed == len(checks),
        "checks": checks,
    }
    (RESULTS / "T447_VALIDATION.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    (RESULTS / "T447_VALIDATION_LOG.txt").write_text(
        "\n".join([f"[{ 'PASS' if item['pass'] else 'FAIL' }] {item['check']}: {item['detail']}" for item in checks]) + f"\n{passed}/{len(checks)} checks passed\n",
        encoding="utf-8",
    )
    print(json.dumps(validation, indent=2))
    if passed != len(checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
