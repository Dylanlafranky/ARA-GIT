from __future__ import annotations

import csv
import hashlib
import json
import math
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astropy.cosmology import FlatLambdaCDM
from lenstronomy.LensModel.lens_model import LensModel
from lenstronomy.Util import param_util
from scipy.optimize import least_squares
from scipy.stats import chi2


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)
T444_DATA = ROOT.parent / "T444_gravitational_lens_distance_time" / "data"

SYSTEM_NAME = "GraLJ203802-400815"
Z_LENS = 0.230
Z_SOURCE = 0.777
H0 = 70.0
OMEGA_M = 0.3
ARCSEC_PER_RADIAN = 206264.80624709636
C_KM_S = 299792.458
MPC_KM = 3.0856775814913673e19
C_MPC_DAY = C_KM_S * 86400.0 / MPC_KM

PAIR_NAMES = ["AB", "AC", "AD"]
PAIR_COMPONENTS = [("A", "B"), ("A", "C"), ("A", "D")]
# Gaia GraL X and TDCOSMO use different image letters for this system.
# The permutation is recovered independently from the pre-delay model's
# Fermat ordering: TDCOSMO A/B/C/D = Gaia C/B/A/D.  Without this explicit
# crosswalk AB and AC acquire the wrong identity even though the source lock
# remains excellent.
TDCOSMO_TO_GAIA = {"A": "C", "B": "B", "C": "A", "D": "D"}
DELAY_MEAN_DAYS = np.array([-12.4, -5.3, -33.3], dtype=float)
DELAY_COV_DAYS2 = np.array(
    [
        [14.2, 6.1, 14.8],
        [6.1, 7.5, 7.1],
        [14.8, 7.1, 39.9],
    ],
    dtype=float,
)

# Published TDCOSMO-IX lenstronomy power-law marginal summaries.
PUBLISHED = {
    "theta_E": (1.380, 0.001),
    "q": (0.643, 0.005),
    "phi_mass_deg": (90.0 - 37.1, 0.2),
    "gamma": (2.22, 0.025),
    "shear": (0.065, 0.0035),
    # The paper angle is converted using the relation in the public notebook.
    "phi_shear_deg": (-90.0 - (-58.1), 0.35),
}

# Paper-level model predictions used only as a validation comparison, never as inputs.
PUBLISHED_PREDICTED_DELAYS = {"AB": -5.0, "AC": -10.0, "AD": -24.2}


@dataclass
class FitResult:
    x_sign: int
    vector: np.ndarray
    source_xy: np.ndarray
    source_points: np.ndarray
    source_rms_arcsec: float
    cost: float
    jacobian: np.ndarray


def json_ready(value):
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, np.ndarray):
        return [json_ready(v) for v in value.tolist()]
    if isinstance(value, dict):
        return {str(k): json_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(v) for v in value]
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_vizier_tsv(path: Path) -> pd.DataFrame:
    lines = path.read_text(encoding="utf-8").splitlines()
    usable = [line for line in lines if not line.startswith("#")]
    header_index = next(i for i, line in enumerate(usable) if line.startswith("recno\t"))
    header = usable[header_index]
    data_lines = [
        line
        for line in usable[header_index + 1 :]
        if line.split("\t", 1)[0].strip().isdigit()
    ]
    rows = list(csv.DictReader([header] + data_lines, delimiter="\t"))
    frame = pd.DataFrame(rows)
    for column in frame.columns:
        if pd.api.types.is_string_dtype(frame[column]):
            frame[column] = frame[column].str.strip()
    return frame


def parse_ra_deg(value: str) -> float:
    hours, minutes, seconds = (float(part) for part in value.split())
    return 15.0 * (hours + minutes / 60.0 + seconds / 3600.0)


def parse_dec_deg(value: str) -> float:
    parts = value.split()
    sign = -1.0 if parts[0].startswith("-") else 1.0
    degrees = abs(float(parts[0]))
    minutes = float(parts[1])
    seconds = float(parts[2])
    return sign * (degrees + minutes / 60.0 + seconds / 3600.0)


def image_positions() -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    a1 = load_vizier_tsv(T444_DATA / "tablea1.tsv")
    selected = a1[(a1["Name"] == SYSTEM_NAME) & a1["Comp"].isin(["A", "B", "C", "D", "G"])].copy()
    if set(selected["Comp"]) != {"A", "B", "C", "D", "G"}:
        raise RuntimeError("WGD2038 A/B/C/D/G astrometry is incomplete")
    coordinates = {}
    for row in selected.to_dict(orient="records"):
        coordinates[row["Comp"]] = np.array(
            [parse_ra_deg(row["RAJ2000"]), parse_dec_deg(row["DEJ2000"])], dtype=float
        )
    lens = coordinates["G"]
    cos_dec = math.cos(math.radians(lens[1]))
    offsets = {
        comp: np.array(
            [
                (coordinates[comp][0] - lens[0]) * cos_dec * 3600.0,
                (coordinates[comp][1] - lens[1]) * 3600.0,
            ]
        )
        for comp in ["A", "B", "C", "D"]
    }
    rows = []
    for comp in ["A", "B", "C", "D", "G"]:
        xy = offsets.get(comp, np.zeros(2))
        rows.append(
            {
                "gaia_component": comp,
                "tdcosmo_component": (
                    next((key for key, value in TDCOSMO_TO_GAIA.items() if value == comp), "G")
                    if comp != "G"
                    else "G"
                ),
                "ra_deg": coordinates[comp][0],
                "dec_deg": coordinates[comp][1],
                "east_arcsec": xy[0],
                "north_arcsec": xy[1],
            }
        )
    return pd.DataFrame(rows), offsets


def tdcosmo_positions(offsets: dict[str, np.ndarray], x_sign: int) -> dict[str, np.ndarray]:
    return {
        tdcosmo_label: offsets[gaia_label] * np.array([x_sign, 1.0])
        for tdcosmo_label, gaia_label in TDCOSMO_TO_GAIA.items()
    }


LENS_MODEL = LensModel(lens_model_list=["EPL", "SHEAR"])


def kwargs_from_vector(vector: np.ndarray, shear_fraction: float = 1.0):
    theta_e, q, phi_mass_deg, gamma, shear, phi_shear_deg, center_x, center_y = vector
    e1, e2 = param_util.phi_q2_ellipticity(math.radians(phi_mass_deg), q)
    gamma1, gamma2 = param_util.shear_polar2cartesian(
        math.radians(phi_shear_deg), shear * shear_fraction
    )
    return [
        {
            "theta_E": theta_e,
            "gamma": gamma,
            "e1": e1,
            "e2": e2,
            "center_x": center_x,
            "center_y": center_y,
        },
        {"gamma1": gamma1, "gamma2": gamma2, "ra_0": 0.0, "dec_0": 0.0},
    ]


def source_points_for(vector: np.ndarray, positions_xy: np.ndarray, shear_fraction: float = 1.0):
    kwargs_lens = kwargs_from_vector(vector, shear_fraction)
    alpha_x, alpha_y = LENS_MODEL.alpha(positions_xy[:, 0], positions_xy[:, 1], kwargs_lens)
    return positions_xy - np.column_stack([alpha_x, alpha_y])


def initial_vector() -> np.ndarray:
    return np.array(
        [
            PUBLISHED["theta_E"][0],
            PUBLISHED["q"][0],
            PUBLISHED["phi_mass_deg"][0],
            PUBLISHED["gamma"][0],
            PUBLISHED["shear"][0],
            PUBLISHED["phi_shear_deg"][0],
            0.0,
            0.0,
        ],
        dtype=float,
    )


def fit_published_summary(offsets: dict[str, np.ndarray], x_sign: int) -> FitResult:
    positions = np.vstack([offsets[c] * np.array([x_sign, 1.0]) for c in ["A", "B", "C", "D"]])
    means = initial_vector()
    sigmas = np.array(
        [
            PUBLISHED["theta_E"][1],
            PUBLISHED["q"][1],
            PUBLISHED["phi_mass_deg"][1],
            PUBLISHED["gamma"][1],
            PUBLISHED["shear"][1],
            PUBLISHED["phi_shear_deg"][1],
        ]
    )

    def residuals(vector):
        source_points = source_points_for(vector, positions)
        source_mean = source_points.mean(axis=0)
        source_residual = ((source_points - source_mean) / 0.004).ravel()
        prior_residual = (vector[:6] - means[:6]) / sigmas
        return np.concatenate([source_residual, prior_residual])

    lower = np.array([1.36, 0.60, 48.0, 2.08, 0.045, -36.0, -0.20, -0.20])
    upper = np.array([1.40, 0.69, 58.0, 2.36, 0.085, -27.0, 0.20, 0.20])
    fit = least_squares(
        residuals,
        means,
        bounds=(lower, upper),
        xtol=1e-13,
        ftol=1e-13,
        gtol=1e-13,
        max_nfev=3000,
    )
    source_points = source_points_for(fit.x, positions)
    source_mean = source_points.mean(axis=0)
    source_rms = float(np.sqrt(np.mean(np.sum((source_points - source_mean) ** 2, axis=1))))
    return FitResult(
        x_sign=x_sign,
        vector=fit.x,
        source_xy=source_mean,
        source_points=source_points,
        source_rms_arcsec=source_rms,
        cost=float(fit.cost),
        jacobian=fit.jac,
    )


def contribution_arrays(vector: np.ndarray, positions: dict[str, np.ndarray], shear_fraction: float):
    ordered = ["A", "B", "C", "D"]
    xy = np.vstack([positions[c] for c in ordered])
    source_points = source_points_for(vector, xy, shear_fraction)
    source = source_points.mean(axis=0)
    kwargs_lens = kwargs_from_vector(vector, shear_fraction)
    potential = np.asarray(LENS_MODEL.potential(xy[:, 0], xy[:, 1], kwargs_lens), dtype=float)
    geometric = 0.5 * np.sum((xy - source) ** 2, axis=1)
    indices = {name: i for i, name in enumerate(ordered)}
    records = []
    for pair, (first, second) in zip(PAIR_NAMES, PAIR_COMPONENTS):
        i = indices[first]
        j = indices[second]
        a = float(geometric[i] - geometric[j])
        b = float(-potential[i] + potential[j])
        records.append((pair, a, b, a + b))
    return records, source, source_points


def time_delay_distance_mpc() -> float:
    cosmology = FlatLambdaCDM(H0=H0, Om0=OMEGA_M)
    d_l = cosmology.angular_diameter_distance(Z_LENS).value
    d_s = cosmology.angular_diameter_distance(Z_SOURCE).value
    d_ls = cosmology.angular_diameter_distance_z1z2(Z_LENS, Z_SOURCE).value
    return float((1.0 + Z_LENS) * d_l * d_s / d_ls)


def delay_to_dphi_arcsec2(delay_days: np.ndarray, ddt_mpc: float) -> np.ndarray:
    return delay_days * C_MPC_DAY / ddt_mpc * ARCSEC_PER_RADIAN**2


def dphi_to_delay_days(dphi_arcsec2: np.ndarray, ddt_mpc: float) -> np.ndarray:
    return dphi_arcsec2 / ARCSEC_PER_RADIAN**2 * ddt_mpc / C_MPC_DAY


def normalize_pair(a: float, b: float) -> tuple[float, float]:
    denominator = abs(a) + abs(b)
    if denominator <= 1e-15:
        return 1.0, 1.0
    return 2.0 * abs(a) / denominator, 2.0 * abs(b) / denominator


def split_residual(endpoint: np.ndarray, previous: np.ndarray, target: np.ndarray):
    tangent = endpoint - previous
    tangent_norm = np.linalg.norm(tangent)
    if tangent_norm <= 1e-15:
        tangent_hat = np.array([1.0, 0.0])
    else:
        tangent_hat = tangent / tangent_norm
    normal_hat = np.array([-tangent_hat[1], tangent_hat[0]])
    residual = target - endpoint
    parallel = float(residual @ tangent_hat)
    perpendicular = float(residual @ normal_hat)
    return parallel, perpendicular, tangent_hat, normal_hat


def controlled_paths(fit: FitResult, offsets: dict[str, np.ndarray], observed_dphi: np.ndarray):
    positions = tdcosmo_positions(offsets, fit.x_sign)
    lambdas = np.linspace(0.0, 1.0, 41)
    path_rows = []
    native_by_pair = {pair: [] for pair in PAIR_NAMES}
    for lam in lambdas:
        contributions, _, _ = contribution_arrays(fit.vector, positions, float(lam))
        for pair, a, b, total in contributions:
            x_ara, y_ara = normalize_pair(a, b)
            row = {
                "pair": pair,
                "lambda": float(lam),
                "geometric_a_arcsec2": a,
                "potential_b_arcsec2": b,
                "total_dphi_arcsec2": total,
                "traversal_ara": x_ara,
                "connection_ara": y_ara,
                "point_type": "path",
            }
            path_rows.append(row)
            native_by_pair[pair].append(np.array([a, b], dtype=float))

    result_rows = []
    for pair_index, pair in enumerate(PAIR_NAMES):
        curve = np.vstack(native_by_pair[pair])
        endpoint = curve[-1]
        previous = curve[-2]
        observed_required_b = float(observed_dphi[pair_index] - endpoint[0])
        target = np.array([endpoint[0], observed_required_b])
        parallel, perpendicular, tangent_hat, normal_hat = split_residual(endpoint, previous, target)
        distances = np.linalg.norm(curve - target, axis=1)
        nearest_index = int(np.argmin(distances))
        total_start = float(curve[0].sum())
        total_end = float(endpoint.sum())
        total_change = total_end - total_start
        total_match_lambda = (
            float((observed_dphi[pair_index] - total_start) / total_change)
            if abs(total_change) > 1e-15
            else float("nan")
        )
        segment_lengths = np.linalg.norm(np.diff(curve, axis=0), axis=1)
        arc_length = float(segment_lengths.sum())
        chord = float(np.linalg.norm(curve[-1] - curve[0]))
        straightness = chord / arc_length if arc_length > 0 else 1.0
        other_denominator = abs(parallel) + abs(perpendicular)
        if other_denominator > 1e-15:
            movement_ara = 2.0 * abs(parallel) / other_denominator
            connection_ara = 2.0 * abs(perpendicular) / other_denominator
        else:
            movement_ara = connection_ara = 1.0
        endpoint_ara = normalize_pair(endpoint[0], endpoint[1])
        target_ara = normalize_pair(target[0], target[1])
        result_rows.append(
            {
                "pair": pair,
                "blind_status": "clean" if pair in {"AB", "AD"} else "model-informed sign",
                "geometric_a_arcsec2": endpoint[0],
                "potential_b_arcsec2": endpoint[1],
                "model_total_dphi_arcsec2": endpoint.sum(),
                "observed_dphi_arcsec2": observed_dphi[pair_index],
                "observed_required_b_arcsec2": observed_required_b,
                "parallel_residual_arcsec2": parallel,
                "perpendicular_residual_arcsec2": perpendicular,
                "parallel_fraction": abs(parallel) / other_denominator if other_denominator else 0.5,
                "perpendicular_fraction": abs(perpendicular) / other_denominator if other_denominator else 0.5,
                "other_movement_ara": movement_ara,
                "other_connection_ara": connection_ara,
                "model_traversal_ara": endpoint_ara[0],
                "model_connection_ara": endpoint_ara[1],
                "observed_traversal_ara": target_ara[0],
                "observed_connection_ara": target_ara[1],
                "nearest_lambda": lambdas[nearest_index],
                "nearest_distance_arcsec2": distances[nearest_index],
                "total_match_lambda": total_match_lambda,
                "within_fitted_shear_path": bool(0.0 <= total_match_lambda <= 1.0),
                "lambda_beyond_fitted_endpoint": total_match_lambda - 1.0,
                "path_straightness": straightness,
                "path_curvature_fraction": max(0.0, 1.0 - straightness),
                "tangent_x": tangent_hat[0],
                "tangent_y": tangent_hat[1],
                "normal_x": normal_hat[0],
                "normal_y": normal_hat[1],
            }
        )
        path_rows.append(
            {
                "pair": pair,
                "lambda": 1.0,
                "geometric_a_arcsec2": endpoint[0],
                "potential_b_arcsec2": observed_required_b,
                "total_dphi_arcsec2": observed_dphi[pair_index],
                "traversal_ara": target_ara[0],
                "connection_ara": target_ara[1],
                "point_type": "observed-required",
            }
        )
    return pd.DataFrame(path_rows), pd.DataFrame(result_rows)


def local_uncertainty_samples(
    fit: FitResult,
    offsets: dict[str, np.ndarray],
    ddt_mpc: float,
    n_draws: int = 2000,
):
    rng = np.random.default_rng(445)
    jtj = fit.jacobian.T @ fit.jacobian
    covariance = np.linalg.pinv(jtj)
    parameter_draws = rng.multivariate_normal(fit.vector, covariance, size=n_draws * 2)
    delay_draws = rng.multivariate_normal(DELAY_MEAN_DAYS, DELAY_COV_DAYS2, size=n_draws * 2)
    positions = tdcosmo_positions(offsets, fit.x_sign)
    rows = []
    accepted = 0
    lower = np.array([1.36, 0.60, 48.0, 2.08, 0.045, -36.0, -0.20, -0.20])
    upper = np.array([1.40, 0.69, 58.0, 2.36, 0.085, -27.0, 0.20, 0.20])
    for draw_index, (vector, delays) in enumerate(zip(parameter_draws, delay_draws)):
        if accepted >= n_draws:
            break
        if np.any(vector < lower) or np.any(vector > upper):
            continue
        xy = np.vstack([positions[c] for c in ["A", "B", "C", "D"]])
        source_points = source_points_for(vector, xy)
        source_rms = float(np.sqrt(np.mean(np.sum((source_points - source_points.mean(axis=0)) ** 2, axis=1))))
        if not np.isfinite(source_rms) or source_rms > 0.03:
            continue
        endpoint_records, _, _ = contribution_arrays(vector, positions, 1.0)
        previous_records, _, _ = contribution_arrays(vector, positions, 0.975)
        observed_dphi = delay_to_dphi_arcsec2(delays, ddt_mpc)
        endpoint_map = {row[0]: np.array(row[1:3], dtype=float) for row in endpoint_records}
        previous_map = {row[0]: np.array(row[1:3], dtype=float) for row in previous_records}
        for pair_index, pair in enumerate(PAIR_NAMES):
            endpoint = endpoint_map[pair]
            target = np.array([endpoint[0], observed_dphi[pair_index] - endpoint[0]])
            parallel, perpendicular, tangent_hat, normal_hat = split_residual(endpoint, previous_map[pair], target)
            rows.append(
                {
                    "draw": accepted,
                    "pair": pair,
                    "delay_days": delays[pair_index],
                    "source_rms_arcsec": source_rms,
                    "geometric_a_arcsec2": endpoint[0],
                    "potential_b_arcsec2": endpoint[1],
                    "observed_dphi_arcsec2": observed_dphi[pair_index],
                    "parallel_residual_arcsec2": parallel,
                    "perpendicular_residual_arcsec2": perpendicular,
                    "tangent_x": tangent_hat[0],
                    "tangent_y": tangent_hat[1],
                    "normal_x": normal_hat[0],
                    "normal_y": normal_hat[1],
                }
            )
        accepted += 1
    if accepted < n_draws // 2:
        raise RuntimeError(f"too few accepted local uncertainty draws: {accepted}")
    return pd.DataFrame(rows), covariance, accepted


def percentile_summary(samples: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for pair, group in samples.groupby("pair", sort=False):
        for metric in [
            "geometric_a_arcsec2",
            "potential_b_arcsec2",
            "observed_dphi_arcsec2",
            "parallel_residual_arcsec2",
            "perpendicular_residual_arcsec2",
        ]:
            q16, q50, q84 = np.percentile(group[metric], [16, 50, 84])
            rows.append({"pair": pair, "metric": metric, "q16": q16, "median": q50, "q84": q84})
    return pd.DataFrame(rows)


def plot_results(
    astrometry: pd.DataFrame,
    fit: FitResult,
    offsets: dict[str, np.ndarray],
    paths: pd.DataFrame,
    decomposition: pd.DataFrame,
    samples: pd.DataFrame,
    ddt_mpc: float,
):
    plt.style.use("default")
    colors = {"blue": "#2F6BFF", "orange": "#F59E0B", "pink": "#D946EF", "ink": "#243244"}

    fig, axes = plt.subplots(2, 2, figsize=(14, 11), constrained_layout=True)
    ax = axes[0, 0]
    positions = tdcosmo_positions(offsets, fit.x_sign)
    for comp in ["A", "B", "C", "D"]:
        point = positions[comp]
        ax.scatter(point[0], point[1], s=80, color=colors["blue"])
        ax.text(point[0] + 0.04, point[1] + 0.04, comp, fontsize=10)
    ax.scatter(fit.vector[6], fit.vector[7], marker="x", s=100, color=colors["ink"], label="fitted mass centre")
    ax.scatter(fit.source_points[:, 0], fit.source_points[:, 1], marker="o", facecolors="none", edgecolors=colors["orange"], s=70, label="back-projected sources")
    ax.scatter(fit.source_xy[0], fit.source_xy[1], marker="*", s=150, color=colors["pink"], label="source lock")
    ax.set_title("Published-summary lens reconstructs one source")
    ax.set_xlabel("model x (arcsec)")
    ax.set_ylabel("model y / north (arcsec)")
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(alpha=0.2)
    ax.legend(fontsize=8)

    ax = axes[0, 1]
    width = 0.18
    x = np.arange(len(PAIR_NAMES))
    a = decomposition["geometric_a_arcsec2"].to_numpy()
    b = decomposition["potential_b_arcsec2"].to_numpy()
    total = decomposition["model_total_dphi_arcsec2"].to_numpy()
    observed = decomposition["observed_dphi_arcsec2"].to_numpy()
    ax.bar(x - 1.5 * width, a, width, label="geometric A", color=colors["blue"])
    ax.bar(x - 0.5 * width, b, width, label="potential B", color=colors["orange"])
    ax.bar(x + 0.5 * width, total, width, label="model total", color=colors["ink"])
    ax.bar(x + 1.5 * width, observed, width, label="observed-required total", color=colors["pink"])
    ax.axhline(0, color="#6B7280", linewidth=1)
    ax.set_xticks(x, PAIR_NAMES)
    ax.set_ylabel("differential Fermat potential (arcsec²)")
    ax.set_title("Native path + potential decomposition")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.2)

    ax = axes[1, 0]
    pair_colors = {"AB": "#2F6BFF", "AC": "#F59E0B", "AD": "#6B7280"}
    for pair in PAIR_NAMES:
        group = paths[(paths["pair"] == pair) & (paths["point_type"] == "path")]
        ax.plot(group["geometric_a_arcsec2"], group["potential_b_arcsec2"], color=pair_colors[pair], label=f"{pair} shear path")
        target = paths[(paths["pair"] == pair) & (paths["point_type"] == "observed-required")].iloc[0]
        ax.scatter(target["geometric_a_arcsec2"], target["potential_b_arcsec2"], marker="X", s=90, color=pair_colors[pair], edgecolor="black")
    ax.set_xlabel("geometric A / traversal (arcsec²)")
    ax.set_ylabel("potential B / connection (arcsec²)")
    ax.set_title("Controlled shear path and observed-required point")
    ax.grid(alpha=0.2)
    ax.legend(fontsize=8)

    ax = axes[1, 1]
    x = np.arange(len(PAIR_NAMES))
    ax.bar(x - 0.18, decomposition["parallel_residual_arcsec2"], 0.36, color=colors["blue"], label="along known pair path")
    ax.bar(x + 0.18, decomposition["perpendicular_residual_arcsec2"], 0.36, color=colors["orange"], label="away from known pair path")
    ax.axhline(0, color="#6B7280", linewidth=1)
    ax.set_xticks(x, PAIR_NAMES)
    ax.set_ylabel("signed residual (arcsec²)")
    ax.set_title("Circle/line tangent–normal split")
    ax.grid(axis="y", alpha=0.2)
    ax.legend(fontsize=8)
    fig.suptitle(
        f"T445 WGD2038 — Te-ARA and coarse Other recovery\n"
        f"fixed H₀={H0:g}, Ωm={OMEGA_M:g}; DΔt={ddt_mpc:.1f} Mpc; source RMS={fit.source_rms_arcsec*1000:.1f} mas",
        fontsize=14,
    )
    fig.savefig(RESULTS / "T445_GEOMETRY_FIRST.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), constrained_layout=True)
    for ax, pair in zip(axes, PAIR_NAMES):
        group = paths[(paths["pair"] == pair) & (paths["point_type"] == "path")]
        ax.plot(group["traversal_ara"], group["connection_ara"], color=colors["blue"], linewidth=2)
        ax.scatter(group.iloc[0]["traversal_ara"], group.iloc[0]["connection_ara"], marker="o", facecolors="none", edgecolors=colors["ink"], s=70, label="no shear")
        ax.scatter(group.iloc[-1]["traversal_ara"], group.iloc[-1]["connection_ara"], marker="o", color=colors["orange"], s=70, label="fitted shear")
        target = paths[(paths["pair"] == pair) & (paths["point_type"] == "observed-required")].iloc[0]
        ax.scatter(target["traversal_ara"], target["connection_ara"], marker="X", color=colors["pink"], edgecolor="black", s=90, label="observed-required")
        ax.axvline(1, color="#94A3B8", linestyle="--", linewidth=1)
        ax.axhline(1, color="#94A3B8", linestyle="--", linewidth=1)
        ax.set_xlim(0, 2)
        ax.set_ylim(0, 2)
        ax.set_aspect("equal")
        ax.set_title(f"{pair} — {decomposition.loc[decomposition.pair == pair, 'blind_status'].iloc[0]}")
        ax.set_xlabel("Traversal share ARA (0–2)")
        ax.set_ylabel("Connection share ARA (0–2)")
        ax.grid(alpha=0.2)
    axes[0].legend(fontsize=8, loc="best")
    fig.suptitle("Same controlled relation on the ARA 0–2 contribution-share plane")
    fig.savefig(RESULTS / "T445_ARA_PAIR_PLANES.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), constrained_layout=True)
    ax = axes[0]
    for pair, color in zip(PAIR_NAMES, [colors["blue"], colors["orange"], colors["pink"]]):
        group = samples[samples["pair"] == pair]
        ax.hist(group["parallel_residual_arcsec2"], bins=45, histtype="step", linewidth=1.8, color=color, label=f"{pair} parallel")
    ax.axvline(0, color="#6B7280", linewidth=1)
    ax.set_title("Local uncertainty: along-path residual")
    ax.set_xlabel("arcsec²")
    ax.set_ylabel("draw count")
    ax.legend(fontsize=8)
    ax = axes[1]
    for pair, color in zip(PAIR_NAMES, [colors["blue"], colors["orange"], colors["pink"]]):
        group = samples[samples["pair"] == pair]
        ax.hist(group["perpendicular_residual_arcsec2"], bins=45, histtype="step", linewidth=1.8, color=color, label=f"{pair} perpendicular")
    ax.axvline(0, color="#6B7280", linewidth=1)
    ax.set_title("Local uncertainty: away-from-path residual")
    ax.set_xlabel("arcsec²")
    ax.set_ylabel("draw count")
    ax.legend(fontsize=8)
    fig.savefig(RESULTS / "T445_UNCERTAINTY_RESIDUALS.png", dpi=180)
    plt.close(fig)


def write_sql_extracts(tables: dict[str, pd.DataFrame]):
    database = RESULTS / "T445_ANALYSIS.sqlite"
    with sqlite3.connect(database) as connection:
        for name, frame in tables.items():
            frame.to_sql(name, connection, if_exists="replace", index=False)
        queries = {
            "decomposition": "SELECT * FROM decomposition ORDER BY CASE pair WHEN 'AB' THEN 1 WHEN 'AC' THEN 2 ELSE 3 END",
            "paths": "SELECT * FROM controlled_path ORDER BY pair, lambda, point_type",
            "uncertainty": "SELECT pair, COUNT(*) AS n_draws, AVG(parallel_residual_arcsec2) AS mean_parallel, AVG(perpendicular_residual_arcsec2) AS mean_perpendicular FROM uncertainty_samples GROUP BY pair ORDER BY pair",
            "global_clean_fit": "SELECT * FROM global_clean_fit ORDER BY measurement",
        }
        for name, sql in queries.items():
            pd.read_sql_query(sql, connection).to_csv(RESULTS / f"T445_SQL_{name.upper()}.csv", index=False)
    (RESULTS / "T445_SOURCE_QUERIES.sql").write_text(
        "\n\n".join(f"-- {name}\n{sql};" for name, sql in queries.items()), encoding="utf-8"
    )


def main():
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    astrometry, offsets = image_positions()
    fits = [fit_published_summary(offsets, sign) for sign in (-1, 1)]
    fit = min(fits, key=lambda item: item.cost)
    if fit.source_rms_arcsec > 0.02:
        raise RuntimeError(
            f"published-summary model did not source-lock: RMS={fit.source_rms_arcsec:.5f} arcsec"
        )

    ddt_mpc = time_delay_distance_mpc()
    observed_dphi = delay_to_dphi_arcsec2(DELAY_MEAN_DAYS, ddt_mpc)
    paths, decomposition = controlled_paths(fit, offsets, observed_dphi)
    decomposition["model_delay_days"] = dphi_to_delay_days(
        decomposition["model_total_dphi_arcsec2"].to_numpy(), ddt_mpc
    )
    decomposition["observed_delay_days"] = DELAY_MEAN_DAYS
    decomposition["observed_delay_sigma_days"] = np.sqrt(np.diag(DELAY_COV_DAYS2))
    decomposition["published_prediction_days"] = decomposition["pair"].map(PUBLISHED_PREDICTED_DELAYS)
    decomposition["reconstruction_minus_published_days"] = (
        decomposition["model_delay_days"] - decomposition["published_prediction_days"]
    )

    clean_indices = [0, 2]
    clean_pairs = ["AB", "AD"]
    clean_covariance = DELAY_COV_DAYS2[np.ix_(clean_indices, clean_indices)]
    clean_precision = np.linalg.inv(clean_covariance)
    clean_observed = DELAY_MEAN_DAYS[clean_indices]
    clean_start_dphi = np.array(
        [
            float(
                paths[
                    (paths["pair"] == pair)
                    & (paths["point_type"] == "path")
                    & np.isclose(paths["lambda"], 0.0)
                ]["total_dphi_arcsec2"].iloc[0]
            )
            for pair in clean_pairs
        ]
    )
    clean_start_days = dphi_to_delay_days(clean_start_dphi, ddt_mpc)
    clean_end_days = decomposition.set_index("pair").loc[clean_pairs, "model_delay_days"].to_numpy()
    clean_slopes = clean_end_days - clean_start_days
    best_shared_lambda = float(
        (clean_slopes @ clean_precision @ (clean_observed - clean_start_days))
        / (clean_slopes @ clean_precision @ clean_slopes)
    )
    clean_shared_prediction = clean_start_days + best_shared_lambda * clean_slopes
    clean_shared_residual = clean_observed - clean_shared_prediction
    shared_chi2 = float(clean_shared_residual @ clean_precision @ clean_shared_residual)
    fitted_residual = clean_observed - clean_end_days
    fitted_chi2 = float(fitted_residual @ clean_precision @ fitted_residual)
    global_clean_fit = pd.DataFrame(
        [
            {
                "measurement": "shared_lambda_fit",
                "value": best_shared_lambda,
                "units": "fraction of fitted external-shear amplitude",
                "note": "fit jointly to clean AB and AD delay outcomes",
            },
            {
                "measurement": "shared_lambda_chi2",
                "value": shared_chi2,
                "units": "chi-square",
                "note": "1 degree of freedom after fitting one shared lambda",
            },
            {
                "measurement": "shared_lambda_p_value",
                "value": float(chi2.sf(shared_chi2, 1)),
                "units": "probability",
                "note": "tests whether one shared shear-scaling coordinate fits both clean pairs",
            },
            {
                "measurement": "fitted_endpoint_chi2",
                "value": fitted_chi2,
                "units": "chi-square",
                "note": "published-summary fitted endpoint versus clean observed delays",
            },
            {
                "measurement": "fitted_endpoint_p_value",
                "value": float(chi2.sf(fitted_chi2, 2)),
                "units": "probability",
                "note": "2 degrees of freedom; observational covariance only",
            },
        ]
    )

    samples, covariance, n_accepted = local_uncertainty_samples(fit, offsets, ddt_mpc)
    uncertainty_summary = percentile_summary(samples)

    positions_model = tdcosmo_positions(offsets, fit.x_sign)
    raw_source_points = dict(zip(["A", "B", "C", "D"], fit.source_points))
    astrometry_rows = []
    for index, comp in enumerate(["A", "B", "C", "D"]):
        point = positions_model[comp]
        source_point = raw_source_points[TDCOSMO_TO_GAIA[comp]]
        astrometry_rows.append(
            {
                "tdcosmo_component": comp,
                "gaia_component": TDCOSMO_TO_GAIA[comp],
                "image_x_arcsec": point[0],
                "image_y_arcsec": point[1],
                "source_x_arcsec": source_point[0],
                "source_y_arcsec": source_point[1],
                "source_offset_mas": 1000.0 * np.linalg.norm(source_point - fit.source_xy),
            }
        )
    astrometry_fit = pd.DataFrame(astrometry_rows)

    quality = {
        "source_rows": int(len(astrometry)),
        "required_components_present": True,
        "delay_covariance_positive_definite": bool(np.all(np.linalg.eigvalsh(DELAY_COV_DAYS2) > 0)),
        "source_rms_arcsec": fit.source_rms_arcsec,
        "source_lock_threshold_arcsec": 0.02,
        "source_lock_pass": fit.source_rms_arcsec <= 0.02,
        "coordinate_convention_candidates": [
            {"x_sign": item.x_sign, "cost": item.cost, "source_rms_arcsec": item.source_rms_arcsec}
            for item in fits
        ],
        "selected_x_sign": fit.x_sign,
        "component_crosswalk": TDCOSMO_TO_GAIA,
        "component_crosswalk_check": "recovered from the pre-delay Fermat ordering, not from observed delays",
        "full_posterior_available": False,
        "full_posterior_gap": "TDCOSMO repository's linked Google Drive folder returns 404 as of the test date",
        "uncertainty_mode": "local covariance approximation around an astrometry-locked reconstruction from published marginal summaries",
        "accepted_uncertainty_draws": n_accepted,
        "ac_blind_status": "model-informed sign; positive alternative was rejected using mass-model ordering in TDCOSMO-XVI",
    }

    parameter_names = [
        "theta_E_arcsec",
        "q",
        "phi_mass_model_deg",
        "gamma",
        "shear",
        "phi_shear_model_deg",
        "center_x_arcsec",
        "center_y_arcsec",
    ]
    parameters = pd.DataFrame(
        {
            "parameter": parameter_names,
            "fitted_value": fit.vector,
            "local_sigma": np.sqrt(np.maximum(np.diag(covariance), 0.0)),
        }
    )

    summary = {
        "test": "T445",
        "generated_at": generated_at,
        "identity": "WGD 2038-4008 (GraLJ203802-400815)",
        "method": "published-summary pre-delay lens reconstruction; Te-ARA solve; controlled external-shear path; tangent-normal residual split",
        "cosmology": {"H0_km_s_Mpc": H0, "Omega_m": OMEGA_M, "Ddt_Mpc": ddt_mpc},
        "quality": quality,
        "fit": {
            "parameters": dict(zip(parameter_names, fit.vector)),
            "source_xy_arcsec": fit.source_xy,
            "source_rms_arcsec": fit.source_rms_arcsec,
        },
        "results": decomposition.to_dict(orient="records"),
        "global_clean_fit": global_clean_fit.to_dict(orient="records"),
        "interpretation_boundary": {
            "established": "the observed-required Phase-B term can be solved and compared geometrically with a delay-blind controlled shear path",
            "not_established": "a unique physical Other, chronological motion through posterior samples, or a new law of time",
            "clean_blind_pairs": ["AB", "AD"],
            "model_informed_pair": "AC",
        },
    }

    astrometry.to_csv(RESULTS / "T445_INPUT_ASTROMETRY.csv", index=False)
    astrometry_fit.to_csv(RESULTS / "T445_SOURCE_LOCK.csv", index=False)
    parameters.to_csv(RESULTS / "T445_MODEL_PARAMETERS.csv", index=False)
    paths.to_csv(RESULTS / "T445_CONTROLLED_PATH.csv", index=False)
    decomposition.to_csv(RESULTS / "T445_DECOMPOSITION.csv", index=False)
    samples.to_csv(RESULTS / "T445_UNCERTAINTY_SAMPLES.csv", index=False)
    uncertainty_summary.to_csv(RESULTS / "T445_UNCERTAINTY_SUMMARY.csv", index=False)
    global_clean_fit.to_csv(RESULTS / "T445_GLOBAL_CLEAN_FIT.csv", index=False)
    (RESULTS / "T445_SUMMARY.json").write_text(
        json.dumps(json_ready(summary), indent=2), encoding="utf-8"
    )
    (RESULTS / "T445_DATA_QUALITY.json").write_text(
        json.dumps(json_ready(quality), indent=2), encoding="utf-8"
    )
    (RESULTS / "T445_SOURCE_HASHES.json").write_text(
        json.dumps(
            {
                "tablea1.tsv": sha256(T444_DATA / "tablea1.tsv"),
                "tableb1.tsv": sha256(T444_DATA / "tableb1.tsv"),
                "tdcosmo_ix_source.tar.gz": sha256(ROOT / "data" / "papers" / "tdcosmo_ix_source.tar.gz"),
                "public_notebook": sha256(
                    ROOT
                    / "data"
                    / "upstream"
                    / "WGD2038-4008"
                    / "lenstronomy_modeling"
                    / "notebooks"
                    / "Fermat potentials and lens model comparisons.ipynb"
                ),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    write_sql_extracts(
        {
            "decomposition": decomposition,
            "controlled_path": paths,
            "uncertainty_samples": samples,
            "source_lock": astrometry_fit,
            "model_parameters": parameters,
            "global_clean_fit": global_clean_fit,
        }
    )
    plot_results(astrometry, fit, offsets, paths, decomposition, samples, ddt_mpc)
    print(json.dumps(json_ready(summary), indent=2))


if __name__ == "__main__":
    main()
