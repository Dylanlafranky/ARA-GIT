"""Independent headline validation for T360.

This script reads saved artifacts and does not import the analysis module.
"""

from __future__ import annotations

from itertools import product
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, wilcoxon


HERE = Path(__file__).resolve().parent
PREFIX = "T360_MAGNETIC_PLINKO_IRRATIONALITY_DI_ARA"


def exact_label_p(matrix: np.ndarray) -> tuple[float, float]:
    observed = float(np.mean(matrix[:, 0] - matrix[:, 1:].mean(axis=1)))
    null = []
    for choices in product(range(matrix.shape[1]), repeat=matrix.shape[0]):
        values = []
        for row, choice in zip(matrix, choices):
            values.append(float(row[choice] - np.delete(row, choice).mean()))
        null.append(float(np.mean(values)))
    p_value = float(np.mean(np.asarray(null) >= observed - 1e-12))
    return observed, p_value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def close(left: float, right: float, tolerance: float = 1e-10) -> bool:
    return bool(abs(left - right) <= tolerance)


def main() -> None:
    points = pd.read_csv(HERE / f"{PREFIX}_POINTS.csv")
    events = pd.read_csv(HERE / f"{PREFIX}_EVENTS.csv")
    controls = pd.read_csv(HERE / f"{PREFIX}_CONTROLS.csv")
    anchors = pd.read_csv(HERE / "T360_MAGNETIC_PLINKO_MARKER_ANCHORS.csv")
    magnets = pd.read_csv(HERE / "T360_MAGNETIC_PLINKO_REGISTERED_MAGNETS.csv")
    gates_saved = pd.read_csv(HERE / f"{PREFIX}_FROZEN_GATES.csv")
    results = json.loads((HERE / f"{PREFIX}_RESULTS.json").read_text(encoding="utf-8"))

    # G0
    spans = points.groupby("run_id").v.agg(lambda values: float(values.max() - values.min()))
    tangent_counts = events.groupby("run_id").size().reindex(range(1, 6), fill_value=0)
    anchor_counts = anchors.groupby("run_id").size().reindex(range(1, 6), fill_value=0)
    anchor_medians = anchors.groupby("run_id").lateral_discrepancy_px.median().reindex(range(1, 6))
    g0 = bool(
        len(points.run_id.unique()) == 5
        and (spans >= 0.8).all()
        and (tangent_counts >= 4).all()
        and (anchor_counts >= 6).all()
        and (anchor_medians <= 8).all()
        and len(magnets) == 28
    )

    # G1
    wrong = ["A_mirror", "A_half_column_shift", "A_cyclic_row_shift", "A_stagger_inversion"]
    real_median = float(events.A_real.median())
    positive_rate = float((events.A_real > 0).mean())
    beats_each = all(real_median > float(events[column].median()) for column in wrong)
    wrong_mean = events[wrong].mean(axis=1)
    g1_p = float(wilcoxon(events.A_real, wrong_mean, alternative="greater", method="exact").pvalue)
    g1 = bool(real_median > 0 and positive_rate >= 0.70 and beats_each and g1_p <= 0.05)

    # G2
    parent = controls[controls.control_family == "parent_channel"]
    parent_matrix = parent.pivot(index="run_id", columns="condition", values="value")[["real", "mirror", "shift_minus", "shift_plus"]].to_numpy()
    run_wins = int(sum(row[0] > np.max(row[1:]) for row in parent_matrix))
    g2_effect, g2_p = exact_label_p(parent_matrix)
    g2 = bool(run_wins >= 4 and g2_effect > 0 and g2_p <= 0.05)

    # G3
    chronology = controls[controls.control_family == "chronology"]
    chronology_matrix = chronology.pivot(index="run_id", columns="condition", values="value")[["real", "row_reversal", "cyclic_row_shift", "wrong_lineage"]].to_numpy()
    real_joint = float(events.joint_positive.astype(bool).mean())
    rates = chronology.groupby("condition").value.mean()
    beats_controls = all(real_joint > float(rates[name]) for name in ["row_reversal", "cyclic_row_shift", "wrong_lineage"])
    g3_effect, g3_p = exact_label_p(chronology_matrix)
    g3 = bool(real_joint >= 0.65 and beats_controls and g3_p <= 0.05)

    # G4
    block = points[(points.v >= 0) & (points.v <= 1)]
    rho = float(spearmanr(block.x_C, block.x_P).statistic)
    iqr_c = float(block.x_C.quantile(0.75) - block.x_C.quantile(0.25))
    iqr_p = float(block.x_P.quantile(0.75) - block.x_P.quantile(0.25))
    g4 = bool(abs(rho) < 0.90 and iqr_c > 0 and iqr_p > 0)

    recomputed = [g0, g1, g2, g3, g4]
    saved = gates_saved["pass"].astype(str).str.lower().map({"true": True, "false": False}).tolist()
    numerical_checks = {
        "G1_median": close(real_median, float(results["G1"]["real_median_alignment"])),
        "G1_positive_rate": close(positive_rate, float(results["G1"]["positive_rate"])),
        "G1_p": close(g1_p, float(results["G1"]["exact_wilcoxon_p"])),
        "G2_effect": close(g2_effect, float(results["G2"]["effect"])),
        "G2_p": close(g2_p, float(results["G2"]["exact_label_randomization_p"])),
        "G3_rate": close(real_joint, float(results["G3"]["joint_positive_rate"])),
        "G3_p": close(g3_p, float(results["G3"]["exact_label_randomization_p"])),
        # CSV serialization can alter tie handling at the fifth decimal place.
        "G4_rho": close(rho, float(results["G4"]["spearman_rho"]), tolerance=1e-4),
    }
    protocol_hash = sha256(HERE / "T360_MAGNETIC_PLINKO_IRRATIONALITY_DI_ARA_PROTOCOL_v5_FROZEN.md")
    figure = cv2.imread(str(HERE / f"{PREFIX}_FIGURE.png"))
    validation = {
        "validation_status": "PASS" if recomputed == saved and all(numerical_checks.values()) else "FAIL",
        "recomputed_gates": recomputed,
        "saved_gates": saved,
        "numerical_checks": numerical_checks,
        "headline": {
            "G1_real_median": real_median,
            "G1_positive_rate": positive_rate,
            "G1_p": g1_p,
            "G2_run_wins": run_wins,
            "G2_effect": g2_effect,
            "G2_p": g2_p,
            "G3_joint_rate": real_joint,
            "G3_effect": g3_effect,
            "G3_p": g3_p,
            "G4_rho": rho,
        },
        "protocol_v5_sha256": protocol_hash,
        "protocol_hash_matches_sidecar": protocol_hash == "ADCB323D976D1EB0ABAB06A5D344373113B433C4C92DF1FCF2FF386C80368EA8",
        "figure_shape": list(figure.shape) if figure is not None else None,
        "figure_exists": figure is not None,
    }
    (HERE / f"{PREFIX}_VALIDATION.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
