from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
T445 = ROOT.parent / "T445_lens_te_ara_other_recovery" / "results"
PAIR_ORDER = ["AC", "AB", "AD"]


def signed_turn(p0: np.ndarray, p1: np.ndarray, p2: np.ndarray) -> float:
    v1 = p1 - p0
    v2 = p2 - p1
    return math.atan2(float(v1[0] * v2[1] - v1[1] * v2[0]), float(np.dot(v1, v2)))


def metrics(points: np.ndarray) -> tuple[float, float, float]:
    steps = np.diff(points, axis=0)
    directness = float(np.linalg.norm(points[-1] - points[0]) / np.linalg.norm(steps, axis=1).sum())
    turns = np.array(
        [signed_turn(points[i], points[i + 1], points[i + 2]) for i in range(len(points) - 2)]
    )
    consistency = float(abs(turns.sum()) / np.abs(turns).sum())
    return directness, consistency, (1.0 - directness) * consistency


def close(a: float, b: float, atol: float = 1e-10) -> bool:
    return bool(np.isclose(a, b, rtol=1e-9, atol=atol, equal_nan=True))


def main() -> None:
    samples = pd.read_csv(T445 / "T445_UNCERTAINTY_SAMPLES.csv")
    decomposition = pd.read_csv(T445 / "T445_DECOMPOSITION.csv")
    source_lock = pd.read_csv(T445 / "T445_SOURCE_LOCK.csv")
    with (T445 / "T445_SUMMARY.json").open(encoding="utf-8") as handle:
        t445_summary = json.load(handle)
    path_draws = pd.read_csv(RESULTS / "T446_PATH_DRAWS.csv")
    transfer = pd.read_csv(RESULTS / "T446_TRANSFER_DRAWS.csv")
    path_summary = pd.read_csv(RESULTS / "T446_PATH_SUMMARY.csv")
    transfer_summary = pd.read_csv(RESULTS / "T446_TRANSFER_SUMMARY.csv")
    central = pd.read_csv(RESULTS / "T446_CENTRAL_PATHS.csv")
    with (RESULTS / "T446_RESULT.json").open(encoding="utf-8") as handle:
        result = json.load(handle)

    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "pass": bool(passed), "detail": detail})

    required = {
        "draw",
        "pair",
        "geometric_a_arcsec2",
        "potential_b_arcsec2",
        "observed_dphi_arcsec2",
        "tangent_x",
        "tangent_y",
    }
    check("input_columns", required.issubset(samples.columns), f"required={sorted(required)}")
    check("input_rows", len(samples) == 6000 and samples["draw"].nunique() == 2000, f"rows={len(samples)}, draws={samples['draw'].nunique()}")
    check("input_pair_balance", (samples.groupby("draw")["pair"].nunique() == 3).all(), "each draw contains AB, AC and AD")
    tangent_norms = np.hypot(samples["tangent_x"], samples["tangent_y"])
    check("unit_tangents", np.allclose(tangent_norms, 1.0, atol=1e-10), f"max_abs_error={float(np.max(np.abs(tangent_norms - 1))):.3e}")

    center = np.array(
        [t445_summary["fit"]["parameters"]["center_x_arcsec"], t445_summary["fit"]["parameters"]["center_y_arcsec"]]
    )
    positions = source_lock.set_index("tdcosmo_component")[["image_x_arcsec", "image_y_arcsec"]]
    angles = {
        label: math.atan2(*(positions.loc[label].to_numpy() - center)[::-1]) for label in ["A", "B", "C", "D"]
    }
    a_angle = angles["A"]
    relative = {label: (angle - a_angle) % (2 * math.pi) for label, angle in angles.items()}
    recovered_order = [label for label, _ in sorted(relative.items(), key=lambda item: item[1])]
    check("spatial_order", recovered_order == ["A", "C", "B", "D"], f"recovered={recovered_order}")

    check("path_output_rows", len(path_draws) == 4000, f"rows={len(path_draws)}")
    check("transfer_output_rows", len(transfer) == 12000, f"rows={len(transfer)}")
    check("scenario_balance", path_draws.groupby("scenario")["draw"].nunique().eq(2000).all(), str(path_draws.groupby("scenario")["draw"].nunique().to_dict()))
    check("transfer_balance", transfer.groupby(["scenario", "holdout_pair"])["draw"].nunique().eq(2000).all(), "2,000 draws in each scenario × holdout")

    bounded = [column for column in path_draws.columns if any(token in column for token in ["directness_D", "turn_consistency_G", "historical_circularity_C"])]
    in_range = all(((path_draws[column] >= -1e-12) & (path_draws[column] <= 1 + 1e-12)).all() for column in bounded)
    check("path_metrics_bounded", in_range, f"columns={bounded}")

    draw0 = samples[samples["draw"] == samples["draw"].min()].set_index("pair")
    origin = np.zeros(2)
    known_points = np.vstack(
        [origin]
        + [
            np.array([draw0.loc[pair, "geometric_a_arcsec2"], draw0.loc[pair, "potential_b_arcsec2"]])
            for pair in PAIR_ORDER
        ]
    )
    d_manual, g_manual, c_manual = metrics(known_points)
    output0 = path_draws[
        (path_draws["draw"] == samples["draw"].min()) & (path_draws["scenario"] == "selected_AC_-5.3d")
    ].iloc[0]
    check("manual_D", close(d_manual, output0["known_directness_D"]), f"manual={d_manual:.12g}, saved={output0['known_directness_D']:.12g}")
    check("manual_G", close(g_manual, output0["known_turn_consistency_G"]), f"manual={g_manual:.12g}, saved={output0['known_turn_consistency_G']:.12g}")
    check("manual_C", close(c_manual, output0["known_historical_circularity_C"]), f"manual={c_manual:.12g}, saved={output0['known_historical_circularity_C']:.12g}")

    dphi_per_day = float(
        decomposition.loc[decomposition["pair"] == "AB", "observed_dphi_arcsec2"].iloc[0]
        / decomposition.loc[decomposition["pair"] == "AB", "observed_delay_days"].iloc[0]
    )
    selected_ac = central[(central["scenario"] == "selected_AC_-5.3d") & (central["relation"] == "AC")].iloc[0]
    alternate_ac = central[(central["scenario"] == "alternate_AC_+7.9d") & (central["relation"] == "AC")].iloc[0]
    actual_shift = float(alternate_ac["B_arcsec2"] - selected_ac["B_arcsec2"])
    expected_shift = 13.2 * dphi_per_day
    check("AC_sensitivity_shift", close(actual_shift, expected_shift), f"actual={actual_shift:.12g}, expected={expected_shift:.12g}")

    no_leakage = (
        (transfer["holdout_pair"] != transfer["calibration_pair_1"])
        & (transfer["holdout_pair"] != transfer["calibration_pair_2"])
        & (transfer["calibration_pair_1"] != transfer["calibration_pair_2"])
    ).all()
    check("holdout_excluded_from_angle", no_leakage, "both angle-calibration children differ from the holdout")
    unit_columns = [
        ("target_direction_x", "target_direction_y"),
        ("straight_direction_x", "straight_direction_y"),
        ("distorted_direction_x", "distorted_direction_y"),
        ("opposite_direction_x", "opposite_direction_y"),
    ]
    unit_ok = all(np.allclose(np.hypot(transfer[x], transfer[y]), 1.0, atol=1e-10) for x, y in unit_columns)
    check("saved_directions_unit_length", unit_ok, "target and three prediction directions have unit norm")

    first_transfer = transfer[
        (transfer["draw"] == samples["draw"].min())
        & (transfer["scenario"] == "selected_AC_-5.3d")
        & (transfer["holdout_pair"] == "AD")
    ].iloc[0]
    known = {
        pair: np.array([draw0.loc[pair, "geometric_a_arcsec2"], draw0.loc[pair, "potential_b_arcsec2"]])
        for pair in PAIR_ORDER
    }
    outcome = {
        pair: np.array(
            [
                draw0.loc[pair, "geometric_a_arcsec2"],
                draw0.loc[pair, "observed_dphi_arcsec2"] - draw0.loc[pair, "geometric_a_arcsec2"],
            ]
        )
        for pair in PAIR_ORDER
    }
    delta_manual = math.degrees(
        math.atan2(
            math.sin(signed_turn(origin, outcome["AC"], outcome["AB"]) - signed_turn(origin, known["AC"], known["AB"])),
            math.cos(signed_turn(origin, outcome["AC"], outcome["AB"]) - signed_turn(origin, known["AC"], known["AB"])),
        )
    )
    check("manual_terminal_delta", close(delta_manual, first_transfer["distortion_delta_deg"]), f"manual={delta_manual:.12g}, saved={first_transfer['distortion_delta_deg']:.12g}")

    path_med = path_draws.groupby("scenario")["outcome_directness_D"].median()
    summary_med = path_summary.set_index("scenario")["outcome_directness_D_median"]
    check("path_summary_matches_draws", np.allclose(path_med.sort_index(), summary_med.sort_index()), "median outcome D reconciles")
    transfer_med = transfer.groupby(["scenario", "holdout_pair"])["distorted_to_straight_error_ratio"].median()
    summary_transfer_med = transfer_summary.set_index(["scenario", "holdout_pair"])["distorted_to_straight_error_ratio_median"]
    check("transfer_summary_matches_draws", np.allclose(transfer_med.sort_index(), summary_transfer_med.sort_index()), "median error ratios reconcile")
    roles = transfer_summary.set_index("holdout_pair")["holdout_role"].to_dict()
    check("topology_roles", roles.get("AB") == "internal-child interpolation" and roles.get("AD") == "terminal forward continuation", str(roles))

    selected_ad = transfer_summary[(transfer_summary["scenario"] == "selected_AC_-5.3d") & (transfer_summary["holdout_pair"] == "AD")].iloc[0]
    alternate_ad = transfer_summary[(transfer_summary["scenario"] == "alternate_AC_+7.9d") & (transfer_summary["holdout_pair"] == "AD")].iloc[0]
    check("selected_terminal_improves", selected_ad["distorted_to_straight_error_ratio_median"] < 1 and selected_ad["fraction_improved"] > 0.5, f"ratio={selected_ad['distorted_to_straight_error_ratio_median']:.3f}, fraction={selected_ad['fraction_improved']:.3f}")
    check("alternate_terminal_reverses", alternate_ad["distorted_to_straight_error_ratio_median"] > 1 and alternate_ad["fraction_improved"] < 0.5, f"ratio={alternate_ad['distorted_to_straight_error_ratio_median']:.3f}, fraction={alternate_ad['fraction_improved']:.3f}")
    check("verdict_records_sensitivity", "AC_sign_sensitive" in result["verdict"]["geometry_first_terminal_status"], result["verdict"]["geometry_first_terminal_status"])

    visuals = [RESULTS / "T446_OTHER_PATH_GEOMETRY.png", RESULTS / "T446_DISTORTION_TRANSFER.png"]
    check("visuals_exist", all(path.exists() and path.stat().st_size > 50_000 for path in visuals), str({path.name: path.stat().st_size if path.exists() else 0 for path in visuals}))

    passed = sum(item["pass"] for item in checks)
    validation = {
        "test": "T446",
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "checks": checks,
    }
    (RESULTS / "T446_VALIDATION.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))
    if passed != len(checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
