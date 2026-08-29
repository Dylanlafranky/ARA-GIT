from __future__ import annotations

import json
import math
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"


def check(name: str, condition: bool, detail: str, checks: list[dict]) -> None:
    checks.append({"check": name, "pass": bool(condition), "detail": detail})


def main() -> None:
    summary = json.loads((RESULTS / "T445_SUMMARY.json").read_text(encoding="utf-8"))
    paths = pd.read_csv(RESULTS / "T445_CONTROLLED_PATH.csv")
    result = pd.read_csv(RESULTS / "T445_DECOMPOSITION.csv")
    lock = pd.read_csv(RESULTS / "T445_SOURCE_LOCK.csv")
    samples = pd.read_csv(RESULTS / "T445_UNCERTAINTY_SAMPLES.csv")
    global_fit = pd.read_csv(RESULTS / "T445_GLOBAL_CLEAN_FIT.csv")
    checks: list[dict] = []

    check("controlled_path_row_count", len(paths) == 126, f"rows={len(paths)}; expected 41×3 path + 3 outcome", checks)
    path_only = paths[paths["point_type"] == "path"]
    check(
        "fermat_components_sum",
        np.allclose(path_only["geometric_a_arcsec2"] + path_only["potential_b_arcsec2"], path_only["total_dphi_arcsec2"], atol=1e-12),
        "A+B equals the model differential Fermat potential for every controlled point",
        checks,
    )
    check(
        "ara_pair_sums_to_two",
        np.allclose(paths["traversal_ara"] + paths["connection_ara"], 2.0, atol=1e-12),
        "native terms are retained; the secondary contribution-share display sums to 2 by definition",
        checks,
    )
    rms = math.sqrt(np.mean((lock["source_offset_mas"] / 1000.0) ** 2))
    check("source_lock", rms < 0.02, f"independently recomputed RMS={rms:.6f} arcsec", checks)
    check(
        "component_crosswalk",
        summary["quality"]["component_crosswalk"] == {"A": "C", "B": "B", "C": "A", "D": "D"},
        "TDCOSMO A/B/C/D = Gaia C/B/A/D",
        checks,
    )
    published = np.array([-5.0, -10.0, -24.2])
    check(
        "pre_delay_prediction_reproduction",
        np.all(np.abs(result["model_delay_days"].to_numpy() - published) < 1.0),
        f"reconstructed={result['model_delay_days'].round(3).tolist()} days",
        checks,
    )
    check(
        "te_ara_solve",
        np.allclose(result["observed_required_b_arcsec2"], result["observed_dphi_arcsec2"] - result["geometric_a_arcsec2"], atol=1e-12),
        "B_eff = observed total − delay-blind A",
        checks,
    )
    for row in result.itertuples(index=False):
        group = path_only[path_only["pair"] == row.pair].sort_values("lambda")
        start = float(group.iloc[0]["total_dphi_arcsec2"])
        end = float(group.iloc[-1]["total_dphi_arcsec2"])
        recovered = (row.observed_dphi_arcsec2 - start) / (end - start)
        check(
            f"total_match_lambda_{row.pair}",
            math.isclose(recovered, row.total_match_lambda, rel_tol=0, abs_tol=1e-10),
            f"lambda={recovered:.6f}",
            checks,
        )
    check(
        "clean_pairs_outside_controlled_path",
        bool((~result[result["pair"].isin(["AB", "AD"])]["within_fitted_shear_path"]).all()),
        "both independently clean delay pairs lie beyond λ∈[0,1]",
        checks,
    )
    check("uncertainty_draw_count", len(samples) == 6000, f"rows={len(samples)} = 2000 draws × 3 pairs", checks)
    check(
        "uncertainty_pair_balance",
        samples.groupby("pair").size().to_dict() == {"AB": 2000, "AC": 2000, "AD": 2000},
        str(samples.groupby("pair").size().to_dict()),
        checks,
    )
    cov = np.array([[14.2, 6.1, 14.8], [6.1, 7.5, 7.1], [14.8, 7.1, 39.9]])
    check("delay_covariance_positive_definite", bool(np.all(np.linalg.eigvalsh(cov) > 0)), f"eigenvalues={np.linalg.eigvalsh(cov).round(4).tolist()}", checks)

    metric = dict(zip(global_fit["measurement"], global_fit["value"]))
    check(
        "global_p_value_consistency",
        math.isclose(metric["shared_lambda_p_value"], float(chi2.sf(metric["shared_lambda_chi2"], 1)), rel_tol=0, abs_tol=1e-12),
        f"p={metric['shared_lambda_p_value']:.6f}",
        checks,
    )
    with sqlite3.connect(RESULTS / "T445_ANALYSIS.sqlite") as conn:
        sqlite_counts = {
            table: int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
            for table in ["decomposition", "controlled_path", "uncertainty_samples", "source_lock", "model_parameters", "global_clean_fit"]
        }
    check(
        "sqlite_extract_counts",
        sqlite_counts == {"decomposition": 3, "controlled_path": 126, "uncertainty_samples": 6000, "source_lock": 4, "model_parameters": 8, "global_clean_fit": 5},
        str(sqlite_counts),
        checks,
    )

    source = (ROOT / "t445_lens_te_ara_other_recovery.py").read_text(encoding="utf-8")
    fit_slice = source[source.index("def fit_published_summary") : source.index("def contribution_arrays")]
    check(
        "no_delay_leakage_into_fit",
        "DELAY_MEAN_DAYS" not in fit_slice and "observed_dphi" not in fit_slice,
        "astrometric lens fit contains no measured-delay variable",
        checks,
    )

    passed = all(item["pass"] for item in checks)
    payload = {
        "test": "T445",
        "status": "PASS" if passed else "FAIL",
        "checks_passed": sum(item["pass"] for item in checks),
        "checks_total": len(checks),
        "checks": checks,
    }
    (RESULTS / "T445_VALIDATION.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
