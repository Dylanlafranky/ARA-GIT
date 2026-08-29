from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
RESULTS = HERE / "results"
RESULTS.mkdir(parents=True, exist_ok=True)
MPL_CACHE = HERE / ".mplcache"
MPL_CACHE.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE))
SHARED_PYDEPS = [
    HERE.parents[1] / "pulsar" / "T443_delayed_connection_timeslices" / ".pydeps",
    HERE.parents[1] / "pulsar" / "T442_ng15_optimal_geometry" / ".pydeps",
]
for dependency_path in SHARED_PYDEPS:
    if dependency_path.exists():
        sys.path.insert(0, str(dependency_path))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.integrate import quad
from scipy.stats import spearmanr


H0 = 70.0  # km s^-1 Mpc^-1, frozen conversion landmark
OMEGA_M = 0.3
C_KM_S = 299792.458
MPC_KM = 3.0856775814913673e19
SECONDS_PER_DAY = 86400.0
OPENING_MIN_DEG = 150.0
RNG = np.random.default_rng(444)
N_PERMUTATIONS = 10_000


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean_number(value):
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def json_ready(value):
    if isinstance(value, dict):
        return {str(k): json_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(v) for v in value]
    return clean_number(value)


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


def first_positive(values: pd.Series) -> float | None:
    for value in values:
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if np.isfinite(number) and number > 0:
            return number
    return None


def parse_float(value: str) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if np.isfinite(number) else None


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


def sky_vector_arcsec(ra_deg: float, dec_deg: float, ra0_deg: float, dec0_deg: float) -> np.ndarray:
    dx = (ra_deg - ra0_deg) * math.cos(math.radians(dec0_deg)) * 3600.0
    dy = (dec_deg - dec0_deg) * 3600.0
    return np.array([dx, dy], dtype=float)


def angle_deg(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    denominator = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)
    if denominator <= 0:
        return float("nan")
    cosine = float(np.clip(np.dot(vector_a, vector_b) / denominator, -1.0, 1.0))
    return float(np.degrees(np.arccos(cosine)))


def comoving_distance_mpc(z: float) -> float:
    integral, _ = quad(
        lambda zz: 1.0 / math.sqrt(OMEGA_M * (1.0 + zz) ** 3 + (1.0 - OMEGA_M)),
        0.0,
        z,
        epsabs=1e-10,
        epsrel=1e-10,
    )
    return (C_KM_S / H0) * integral


def time_delay_distance_mpc(z_lens: float, z_source: float) -> float:
    chi_l = comoving_distance_mpc(z_lens)
    chi_s = comoving_distance_mpc(z_source)
    if chi_s <= chi_l:
        raise ValueError("source must be behind lens")
    d_l = chi_l / (1.0 + z_lens)
    d_s = chi_s / (1.0 + z_source)
    d_ls = (chi_s - chi_l) / (1.0 + z_source)
    return (1.0 + z_lens) * d_l * d_s / d_ls


def angular_term_to_days(term_arcsec2: float, ddt_mpc: float) -> float:
    radians2 = term_arcsec2 * (math.pi / (180.0 * 3600.0)) ** 2
    return ddt_mpc * MPC_KM / C_KM_S / SECONDS_PER_DAY * radians2


def pair_model_terms(r_a: float, r_b: float, ddt_mpc: float) -> dict[str, float]:
    r_outer = max(r_a, r_b)
    r_inner = min(r_a, r_b)

    # Point mass: theta_E^2 = r_outer*r_inner and beta = r_outer-r_inner.
    theta_e2_pm = r_outer * r_inner
    pm_geo_arcsec2 = 0.5 * (r_outer**2 - r_inner**2)
    pm_potential_arcsec2 = theta_e2_pm * math.log(r_outer / r_inner)
    pm_geo_days = angular_term_to_days(pm_geo_arcsec2, ddt_mpc)
    pm_potential_days = angular_term_to_days(pm_potential_arcsec2, ddt_mpc)

    # SIS: equal geometric terms cancel; the differential potential carries the delay.
    theta_e_sis = 0.5 * (r_outer + r_inner)
    sis_geo_arcsec2 = 0.0
    sis_potential_arcsec2 = theta_e_sis * (r_outer - r_inner)
    sis_geo_days = 0.0
    sis_potential_days = angular_term_to_days(sis_potential_arcsec2, ddt_mpc)

    return {
        "r_outer_arcsec": r_outer,
        "r_inner_arcsec": r_inner,
        "radius_ratio_inner_outer": r_inner / r_outer,
        "pm_geo_days": pm_geo_days,
        "pm_potential_days": pm_potential_days,
        "pm_total_days": pm_geo_days + pm_potential_days,
        "sis_geo_days": sis_geo_days,
        "sis_potential_days": sis_potential_days,
        "sis_total_days": sis_geo_days + sis_potential_days,
    }


def build_systems(a1: pd.DataFrame, b1: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    delay_names = set(b1["Name"])
    rows: list[dict] = []
    exclusions: dict[str, int] = {
        "not_in_delay_table": 0,
        "not_double": 0,
        "ambiguous_components": 0,
        "missing_redshift": 0,
        "missing_tAB": 0,
        "invalid_coordinates": 0,
        "opening_below_150_deg": 0,
    }

    for name, group in a1.groupby("Name", sort=True):
        if name not in delay_names:
            exclusions["not_in_delay_table"] += 1
            continue
        system_type = next((v for v in group["Type"] if v), "")
        if system_type != "Double":
            exclusions["not_double"] += 1
            continue
        counts = group["Comp"].value_counts()
        if any(counts.get(component, 0) != 1 for component in ["A", "B", "G"]):
            exclusions["ambiguous_components"] += 1
            continue
        z_source = first_positive(group["zsource"])
        z_lens = first_positive(group["zdef"])
        if z_source is None or z_lens is None or z_source <= z_lens:
            exclusions["missing_redshift"] += 1
            continue
        delay_matches = b1.loc[b1["Name"] == name]
        if len(delay_matches) != 1:
            exclusions["missing_tAB"] += 1
            continue
        delay_row = delay_matches.iloc[0]
        observed_signed = parse_float(delay_row["tAB"])
        delay_error = parse_float(delay_row["e_tAB"])
        if observed_signed is None or observed_signed == 0:
            exclusions["missing_tAB"] += 1
            continue

        components = {component: group.loc[group["Comp"] == component].iloc[0] for component in ["A", "B", "G"]}
        try:
            ra_g = parse_ra_deg(components["G"]["RAJ2000"])
            dec_g = parse_dec_deg(components["G"]["DEJ2000"])
            positions = {}
            for component in ["A", "B"]:
                positions[component] = sky_vector_arcsec(
                    parse_ra_deg(components[component]["RAJ2000"]),
                    parse_dec_deg(components[component]["DEJ2000"]),
                    ra_g,
                    dec_g,
                )
        except (KeyError, TypeError, ValueError):
            exclusions["invalid_coordinates"] += 1
            continue
        r_a = float(np.linalg.norm(positions["A"]))
        r_b = float(np.linalg.norm(positions["B"]))
        opening = angle_deg(positions["A"], positions["B"])
        if not np.isfinite(r_a + r_b + opening) or min(r_a, r_b) <= 0:
            exclusions["invalid_coordinates"] += 1
            continue
        if opening < OPENING_MIN_DEG:
            exclusions["opening_below_150_deg"] += 1
            continue

        ddt = time_delay_distance_mpc(z_lens, z_source)
        terms = pair_model_terms(r_a, r_b, ddt)
        observed_days = abs(observed_signed)
        row = {
            "name": name,
            "observed_signed_days": observed_signed,
            "observed_days": observed_days,
            "observed_error_days": delay_error,
            "z_lens": z_lens,
            "z_source": z_source,
            "time_delay_distance_mpc": ddt,
            "r_A_arcsec": r_a,
            "r_B_arcsec": r_b,
            "A_dx_arcsec": positions["A"][0],
            "A_dy_arcsec": positions["A"][1],
            "B_dx_arcsec": positions["B"][0],
            "B_dy_arcsec": positions["B"][1],
            "opening_angle_deg": opening,
            "axisymmetry_error_deg": 180.0 - opening,
            "max_separation_arcsec": parse_float(group["MaxSep"].iloc[0]),
            "delay_bibcode": delay_row["BibCode"],
            "astrometry_A": components["A"]["rpos"],
            "astrometry_B": components["B"]["rpos"],
            "astrometry_G": components["G"]["rpos"],
            **terms,
        }
        for model in ["pm", "sis"]:
            total = row[f"{model}_total_days"]
            geo = row[f"{model}_geo_days"]
            potential = row[f"{model}_potential_days"]
            denominator = abs(geo) + abs(potential)
            row[f"{model}_path_ara"] = 2.0 * abs(geo) / denominator if denominator else np.nan
            row[f"{model}_connection_ara"] = 2.0 * abs(potential) / denominator if denominator else np.nan
            row[f"{model}_residual_days"] = observed_days - total
            row[f"{model}_absolute_error_days"] = abs(observed_days - total)
            row[f"{model}_log10_ratio"] = math.log10(total / observed_days)
            row[f"{model}_factor_error"] = 10 ** abs(row[f"{model}_log10_ratio"])
        rows.append(row)

    frame = pd.DataFrame(rows).sort_values("observed_days").reset_index(drop=True)
    quality = {
        "a1_rows": int(len(a1)),
        "a1_systems": int(a1["Name"].nunique()),
        "b1_rows": int(len(b1)),
        "eligible_systems": int(len(frame)),
        "exclusions": exclusions,
        "source_hashes": {
            "tablea1.tsv": sha256(DATA / "tablea1.tsv"),
            "tableb1.tsv": sha256(DATA / "tableb1.tsv"),
            "ReadMe.txt": sha256(DATA / "ReadMe.txt"),
        },
        "null_cells_eligible": int(frame.isna().sum().sum()) if len(frame) else 0,
        "duplicate_eligible_names": int(frame["name"].duplicated().sum()) if len(frame) else 0,
    }
    return frame, quality


def model_metrics(frame: pd.DataFrame, model: str) -> dict:
    observed = frame["observed_days"].to_numpy(float)
    predicted = frame[f"{model}_total_days"].to_numpy(float)
    rho = float(spearmanr(observed, predicted).statistic)
    log_error = np.abs(np.log10(predicted / observed))
    return {
        "spearman_rho": rho,
        "median_absolute_error_days": float(np.median(np.abs(predicted - observed))),
        "median_factor_error": float(10 ** np.median(log_error)),
        "within_factor_2_count": int(np.sum(log_error <= math.log10(2.0))),
        "within_factor_2_share": float(np.mean(log_error <= math.log10(2.0))),
        "median_predicted_observed_ratio": float(np.median(predicted / observed)),
    }


def permutation_controls(frame: pd.DataFrame, model: str) -> tuple[pd.DataFrame, dict]:
    observed = frame["observed_days"].to_numpy(float)
    predicted = frame[f"{model}_total_days"].to_numpy(float)
    real_rho = float(spearmanr(observed, predicted).statistic)
    real_factor = float(10 ** np.median(np.abs(np.log10(predicted / observed))))
    rows = []
    for index in range(N_PERMUTATIONS):
        shuffled = RNG.permutation(observed)
        rho = float(spearmanr(shuffled, predicted).statistic)
        factor = float(10 ** np.median(np.abs(np.log10(predicted / shuffled))))
        rows.append({"permutation": index, "model": model, "rho": rho, "median_factor_error": factor})
    controls = pd.DataFrame(rows)
    summary = {
        "real_rho": real_rho,
        "rho_two_sided_p": float((1 + np.sum(np.abs(controls["rho"]) >= abs(real_rho))) / (N_PERMUTATIONS + 1)),
        "real_median_factor_error": real_factor,
        "factor_error_p": float((1 + np.sum(controls["median_factor_error"] <= real_factor)) / (N_PERMUTATIONS + 1)),
    }
    return controls, summary


def residual_relations(frame: pd.DataFrame, model: str) -> dict:
    residual_log_abs = np.abs(frame[f"{model}_log10_ratio"].to_numpy(float))
    relations = {}
    for field in ["axisymmetry_error_deg", "radius_ratio_inner_outer", "max_separation_arcsec", "z_lens"]:
        values = frame[field].to_numpy(float)
        mask = np.isfinite(values) & np.isfinite(residual_log_abs)
        if mask.sum() >= 3:
            statistic = spearmanr(values[mask], residual_log_abs[mask])
            relations[field] = {
                "n": int(mask.sum()),
                "spearman_rho": float(statistic.statistic),
                "p_value": float(statistic.pvalue),
            }
    return relations


def leave_one_out(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for model in ["pm", "sis"]:
        for held_out in frame["name"]:
            subset = frame.loc[frame["name"] != held_out]
            metrics = model_metrics(subset, model)
            rows.append({"model": model, "held_out": held_out, **metrics})
    return pd.DataFrame(rows)


def plot_sky_geometries(frame: pd.DataFrame) -> None:
    count = len(frame)
    columns = 4
    rows = max(1, math.ceil(count / columns))
    fig, axes = plt.subplots(rows, columns, figsize=(14, 3.4 * rows), squeeze=False)
    for axis, (_, row) in zip(axes.flat, frame.sort_values("observed_days", ascending=False).iterrows()):
        a = np.array([row["A_dx_arcsec"], row["A_dy_arcsec"]])
        b = np.array([row["B_dx_arcsec"], row["B_dy_arcsec"]])
        axis.plot([a[0], 0, b[0]], [a[1], 0, b[1]], color="#b6c2d9", linewidth=1.4)
        axis.scatter(a[0], a[1], s=70, color="#3984ff", label="image A")
        axis.scatter(b[0], b[1], s=70, color="#ff8c42", label="image B")
        axis.scatter(0, 0, s=100, marker="X", color="#6b2d84", label="deflector G")
        extent = max(np.linalg.norm(a), np.linalg.norm(b)) * 1.25
        axis.set_xlim(-extent, extent)
        axis.set_ylim(-extent, extent)
        axis.set_aspect("equal", adjustable="box")
        axis.axhline(0, color="#dfe4ea", linewidth=0.6)
        axis.axvline(0, color="#dfe4ea", linewidth=0.6)
        axis.set_title(f"{row['name']}\nΔt={row['observed_days']:.1f} d; opening={row['opening_angle_deg']:.1f}°", fontsize=9)
        axis.set_xlabel("east offset (arcsec)", fontsize=8)
        axis.set_ylabel("north offset (arcsec)", fontsize=8)
        axis.tick_params(labelsize=7)
    for axis in axes.flat[count:]:
        axis.axis("off")
    handles, labels = axes.flat[0].get_legend_handles_labels() if count else ([], [])
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.965), ncol=3, frameon=False)
    fig.suptitle("T444 — actual sky-plane child/parent geometry used by the frozen cut", fontsize=16, y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.925))
    fig.savefig(RESULTS / "T444_SKY_GEOMETRIES.png", dpi=190, bbox_inches="tight")
    plt.close(fig)


def plot_geometry_first(frame: pd.DataFrame, summary: dict) -> None:
    fig = plt.figure(figsize=(18, 15), constrained_layout=True)
    grid = fig.add_gridspec(3, 2)
    blue, orange, purple, green, charcoal = "#3984ff", "#ff8c42", "#744fc6", "#20a464", "#24292f"

    ax = fig.add_subplot(grid[0, 0])
    minimum = min(frame[["observed_days", "pm_total_days", "sis_total_days"]].min()) * 0.65
    maximum = max(frame[["observed_days", "pm_total_days", "sis_total_days"]].max()) * 1.4
    ax.loglog([minimum, maximum], [minimum, maximum], linestyle="--", color=charcoal, label="perfect total-delay match")
    ax.scatter(frame["observed_days"], frame["pm_total_days"], s=75, color=blue, alpha=0.82, label="point-mass landmark")
    ax.scatter(frame["observed_days"], frame["sis_total_days"], s=75, marker="s", color=orange, alpha=0.82, label="SIS landmark")
    for _, row in frame.iterrows():
        if max(row["pm_factor_error"], row["sis_factor_error"]) > 3:
            ax.annotate(row["name"], (row["observed_days"], row["sis_total_days"]), fontsize=7, xytext=(3, 3), textcoords="offset points")
    ax.set_xlim(minimum, maximum)
    ax.set_ylim(minimum, maximum)
    ax.set_xlabel("published |A–B delay| (days)")
    ax.set_ylabel("geometry-only landmark prediction (days)")
    ax.set_title("A. Known lens equations recover scale, not every identity")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend()

    ax = fig.add_subplot(grid[0, 1])
    ordered = frame.sort_values("observed_days", ascending=False).reset_index(drop=True)
    y = np.arange(len(ordered))
    ax.barh(y, ordered["pm_geo_days"], color=blue, label="geometric / travelled-path term")
    ax.barh(y, ordered["pm_potential_days"], left=ordered["pm_geo_days"], color=purple, label="potential / Connection term")
    ax.scatter(ordered["observed_days"], y, marker="|", s=210, linewidths=2.2, color=charcoal, label="published total delay")
    ax.set_yticks(y, ordered["name"], fontsize=8)
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlabel("days (log scale)")
    ax.set_title("B. Point-mass landmark: path plus Connection")
    ax.grid(True, axis="x", which="both", alpha=0.25)
    ax.legend(fontsize=8)

    ax = fig.add_subplot(grid[1, 0])
    scatter = ax.scatter(
        frame["pm_path_ara"],
        frame["pm_connection_ara"],
        c=frame["radius_ratio_inner_outer"],
        cmap="viridis",
        s=85,
        edgecolor="white",
        linewidth=0.5,
    )
    ax.scatter(frame["sis_path_ara"], frame["sis_connection_ara"], marker="X", s=105, color=orange, label="SIS: all differential delay on Connection pole")
    ax.plot([0, 2], [2, 0], color=charcoal, linestyle="--", linewidth=1.2, label="two-term contribution ridge: x+y=2")
    for _, row in frame.iterrows():
        ax.annotate(row["name"], (row["pm_path_ara"], row["pm_connection_ara"]), fontsize=7, xytext=(3, 2), textcoords="offset points")
    ax.set_xlim(-0.05, 2.05)
    ax.set_ylim(-0.05, 2.05)
    ax.axvline(1, color="#8b949e", linestyle=":")
    ax.axhline(1, color="#8b949e", linestyle=":")
    ax.set_xlabel("travelled-path contribution ARA (0–2)")
    ax.set_ylabel("Connection-potential contribution ARA (0–2)")
    ax.set_title("C. ARA contribution cut—not promoted to a Di-ARA")
    ax.grid(True, alpha=0.25)
    ax.legend(fontsize=8, loc="lower left")
    fig.colorbar(scatter, ax=ax, label="inner/outer image radius ratio")

    ax = fig.add_subplot(grid[1, 1])
    for model, color, label in [("pm", blue, "point mass"), ("sis", orange, "SIS")]:
        ax.scatter(frame["axisymmetry_error_deg"], frame[f"{model}_factor_error"], s=75, alpha=0.82, color=color, label=label)
    ax.axhline(2, color=charcoal, linestyle="--", label="factor-of-two error")
    ax.set_yscale("log")
    ax.set_xlabel("departure from 180° A–G–B alignment (degrees)")
    ax.set_ylabel("prediction factor error (≥1; log scale)")
    ax.set_title("D. Independently visible geometry versus missing delay relation")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend()

    ax = fig.add_subplot(grid[2, 0])
    ratios = np.log10(frame["observed_days"] / frame["sis_total_days"])
    colors = np.where(ratios >= 0, green, purple)
    ax.bar(frame["name"], ratios, color=colors)
    ax.axhline(0, color=charcoal, linewidth=1)
    ax.axhline(math.log10(2), color="#8b949e", linestyle="--")
    ax.axhline(-math.log10(2), color="#8b949e", linestyle="--")
    ax.set_ylabel("log10(observed / SIS prediction)")
    ax.set_title("E. Residual direction: extra or over-predicted arrival relation")
    ax.tick_params(axis="x", rotation=70, labelsize=8)
    ax.grid(True, axis="y", alpha=0.25)

    ax = fig.add_subplot(grid[2, 1])
    ax.axis("off")
    pm = summary["models"]["pm"]
    sis = summary["models"]["sis"]
    text = (
        "WHAT THIS CUT ACTUALLY SHOWS\n\n"
        f"Eligible real doubles: {len(frame)}\n"
        f"Point-mass rank relation: ρ={pm['spearman_rho']:.2f}; median factor error={pm['median_factor_error']:.2f}×\n"
        f"SIS rank relation: ρ={sis['spearman_rho']:.2f}; median factor error={sis['median_factor_error']:.2f}×\n\n"
        "Blue/orange equations are conventional landmarks frozen before scoring.\n"
        "Their components show that arrival time is neither chord displacement nor\n"
        "isolated identity state: it is a travelled path evaluated inside a lens relation.\n\n"
        "The residual is not a discovered force. It bundles lens profile, ellipticity,\n"
        "external shear, line-of-sight mass, cosmology, and catalogue uncertainty.\n"
        "That bundle is exactly the information a future identity-only predictor lacks."
    )
    ax.text(0.02, 0.98, text, va="top", ha="left", fontsize=12, linespacing=1.42, bbox={"boxstyle": "round,pad=0.8", "facecolor": "#f4f6f8", "edgecolor": "#b6c2d9"})
    ax.set_title("F. Framework interpretation and scientific boundary", loc="left")

    fig.suptitle("T444 — real gravitational-lens distance/time decomposition", fontsize=20)
    fig.savefig(RESULTS / "T444_GEOMETRY_FIRST.png", dpi=190, bbox_inches="tight")
    plt.close(fig)


def records(frame: pd.DataFrame, columns: list[str]) -> list[dict]:
    return [
        {column: clean_number(row[column]) for column in columns}
        for _, row in frame[columns].iterrows()
    ]


def build_artifact(frame: pd.DataFrame, summary: dict, generated_at: str) -> dict:
    report_columns = [
        "name", "observed_days", "observed_error_days", "opening_angle_deg",
        "radius_ratio_inner_outer", "pm_geo_days", "pm_potential_days", "pm_total_days",
        "sis_total_days", "pm_factor_error", "sis_factor_error", "delay_bibcode",
    ]
    source_frame = frame[report_columns].copy()
    report_sql = "SELECT * FROM t444_system_results ORDER BY observed_days DESC;"
    with sqlite3.connect(":memory:") as connection:
        source_frame.to_sql("t444_system_results", connection, index=False, if_exists="replace")
        report_frame = pd.read_sql_query(report_sql, connection)

    comparison_rows = []
    contribution_rows = []
    ara_rows = []
    residual_rows = []
    for _, row in frame.iterrows():
        for model, label in [("pm", "Point mass"), ("sis", "SIS")]:
            comparison_rows.append({
                "name": row["name"], "model": label,
                "observed_log10_days": math.log10(row["observed_days"]),
                "predicted_log10_days": math.log10(row[f"{model}_total_days"]),
                "observed_days": row["observed_days"], "predicted_days": row[f"{model}_total_days"],
            })
            ara_rows.append({
                "name": row["name"], "model": label,
                "path_ara": row[f"{model}_path_ara"], "connection_ara": row[f"{model}_connection_ara"],
                "radius_ratio": row["radius_ratio_inner_outer"],
            })
            residual_rows.append({
                "name": row["name"], "model": label,
                "axisymmetry_error_deg": row["axisymmetry_error_deg"],
                "factor_error": row[f"{model}_factor_error"],
            })
        contribution_rows.extend([
            {"name": row["name"], "component": "geometric path", "days": row["pm_geo_days"], "observed_days": row["observed_days"]},
            {"name": row["name"], "component": "Connection potential", "days": row["pm_potential_days"], "observed_days": row["observed_days"]},
        ])

    source = {
        "id": "gaia_gral_x",
        "label": "Gaia GraL X catalogue and T444 derived lens rows",
        "href": "https://cdsarc.cds.unistra.fr/viz-bin/cat/J/A+A/707/A345",
        "query": {
            "language": "sql", "engine": "SQLite", "sql": report_sql,
            "description": "Actual report-input query over the reviewed T444 eligible-system table derived from VizieR tables A1 and B1.",
            "executed_at": generated_at, "tables_used": ["t444_system_results"],
            "filters": [
                "Type = Double", "exactly one A, B, and G component", "opening angle at G >= 150 degrees",
                "finite source/lens redshifts", "published non-zero tAB",
            ],
            "metric_definitions": [
                "Observed delay is the absolute published A-B delay in days; its original sign remains in the detailed CSV.",
                "Point-mass and SIS values are frozen conventional axisymmetric landmark predictions using H0=70 km/s/Mpc and Omega_m=0.3.",
                "Factor error is max(predicted/observed, observed/predicted), so 1 is exact and 2 is a factor-of-two miss.",
            ],
        },
    }
    theory_source = {
        "id": "fermat_delay_theory",
        "label": "Geometric and potential gravitational-lensing delay relation",
        "href": "https://arxiv.org/abs/2004.11845",
    }
    metrics = [
        {"id": "eligible", "description": "Real double-image lens systems meeting the frozen astrometric and redshift eligibility cut.", "dataset": "headline", "sourceId": source["id"], "metrics": [{"label": "Eligible systems", "field": "eligible_systems", "format": "number"}]},
        {"id": "pm_rho", "description": "Spearman rank relation between observed delay magnitude and point-mass landmark prediction.", "dataset": "headline", "sourceId": source["id"], "metrics": [{"label": "Point-mass rank ρ", "field": "pm_rho", "format": "number"}]},
        {"id": "sis_rho", "description": "Spearman rank relation between observed delay magnitude and SIS landmark prediction.", "dataset": "headline", "sourceId": source["id"], "metrics": [{"label": "SIS rank ρ", "field": "sis_rho", "format": "number"}]},
        {"id": "pm_factor", "description": "Median multiplicative miss of the point-mass landmark across eligible systems.", "dataset": "headline", "sourceId": source["id"], "metrics": [{"label": "Point-mass median miss", "field": "pm_factor", "format": "number", "unit": "×"}]},
        {"id": "sis_factor", "description": "Median multiplicative miss of the SIS landmark across eligible systems.", "dataset": "headline", "sourceId": source["id"], "metrics": [{"label": "SIS median miss", "field": "sis_factor", "format": "number", "unit": "×"}]},
    ]
    charts = [
        {
            "id": "observed_predicted", "title": "Observed and landmark-predicted A–B delays", "subtitle": "Both axes are log10(days); the models use image/deflector geometry and redshifts, not the observed delay.",
            "type": "scatter", "dataset": "comparison", "sourceId": source["id"], "layout": "full",
            "encodings": {
                "x": {"field": "observed_log10_days", "type": "quantitative", "label": "Observed log10(days)"},
                "y": {"field": "predicted_log10_days", "type": "quantitative", "label": "Predicted log10(days)"},
                "color": {"field": "model", "type": "nominal", "label": "Frozen lens landmark"},
                "tooltip": [
                    {"field": "name", "type": "nominal", "label": "Lens"},
                    {"field": "observed_days", "type": "quantitative", "label": "Observed days"},
                    {"field": "predicted_days", "type": "quantitative", "label": "Predicted days"},
                ],
            },
        },
        {
            "id": "contributions", "title": "Point-mass geometric and potential delay terms", "subtitle": "Native days are retained; the two components jointly produce the landmark total.",
            "type": "bar", "dataset": "contributions", "sourceId": source["id"], "layout": "full",
            "encodings": {
                "x": {"field": "name", "type": "nominal", "label": "Lens system"},
                "y": {"field": "days", "type": "quantitative", "label": "Component delay (days)"},
                "color": {"field": "component", "type": "nominal", "label": "Fermat component"},
                "tooltip": [{"field": "observed_days", "type": "quantitative", "label": "Observed total days"}],
            },
        },
        {
            "id": "ara_cut", "title": "Path/Connection contribution ARA", "subtitle": "A simple two-term cut with x+y=2; it is not asserted to be an independent Di-ARA.",
            "type": "scatter", "dataset": "ara", "sourceId": source["id"], "layout": "full",
            "encodings": {
                "x": {"field": "path_ara", "type": "quantitative", "label": "Travelled-path contribution (0–2)"},
                "y": {"field": "connection_ara", "type": "quantitative", "label": "Connection-potential contribution (0–2)"},
                "color": {"field": "model", "type": "nominal", "label": "Frozen lens landmark"},
                "tooltip": [
                    {"field": "name", "type": "nominal", "label": "Lens"},
                    {"field": "radius_ratio", "type": "quantitative", "label": "Inner/outer radius"},
                ],
            },
        },
        {
            "id": "residual_geometry", "title": "Prediction miss and independently visible non-axisymmetry", "subtitle": "A larger departure from 180° is one observable warning that the two limiting models omit relation structure.",
            "type": "scatter", "dataset": "residuals", "sourceId": source["id"], "layout": "full",
            "encodings": {
                "x": {"field": "axisymmetry_error_deg", "type": "quantitative", "label": "Departure from 180° alignment"},
                "y": {"field": "factor_error", "type": "quantitative", "label": "Prediction factor error"},
                "color": {"field": "model", "type": "nominal", "label": "Frozen lens landmark"},
                "tooltip": [{"field": "name", "type": "nominal", "label": "Lens"}],
            },
        },
    ]
    table = {
        "id": "system_detail", "title": "Eligible real lens systems", "subtitle": "Published delay and frozen model results in native units.",
        "dataset": "system_detail", "sourceId": source["id"], "defaultSort": {"field": "observed_days", "direction": "desc"}, "density": "dense", "layout": "full",
        "columns": [
            {"field": "name", "label": "Lens"}, {"field": "observed_days", "label": "Observed days", "format": "number"},
            {"field": "observed_error_days", "label": "Delay error (d)", "format": "number"}, {"field": "opening_angle_deg", "label": "A–G–B opening (°)", "format": "number"},
            {"field": "pm_geo_days", "label": "PM path (d)", "format": "number"}, {"field": "pm_potential_days", "label": "PM Connection (d)", "format": "number"},
            {"field": "pm_total_days", "label": "PM total (d)", "format": "number"}, {"field": "sis_total_days", "label": "SIS total (d)", "format": "number"},
            {"field": "pm_factor_error", "label": "PM miss (×)", "format": "number"}, {"field": "sis_factor_error", "label": "SIS miss (×)", "format": "number"},
        ],
    }
    pm, sis = summary["models"]["pm"], summary["models"]["sis"]
    blocks = [
        {"id": "title", "type": "markdown", "body": "# Real gravitational-lens distance/time decomposition"},
        {"id": "summary", "type": "markdown", "sourceId": source["id"], "body": (
            "## Known physics gives a real landmark, while residuals preserve the missing relations\n\n"
            f"Across **{len(frame)}** real double-image quasars, the point-mass and SIS landmarks achieved rank correlations of **{pm['spearman_rho']:.2f}** and **{sis['spearman_rho']:.2f}** with published delay magnitude. "
            f"Their median multiplicative misses were **{pm['median_factor_error']:.2f}×** and **{sis['median_factor_error']:.2f}×**. The cut therefore recovers genuine arrival-scale structure without predicting every system from identity geometry alone."
        )},
        {"id": "metrics", "type": "metric-strip", "cardIds": [m["id"] for m in metrics]},
        {"id": "comparison_text", "type": "markdown", "sourceId": source["id"], "body": (
            "## The same source arrives through two paths, but neither path is isolated\n\n"
            "The x-axis is a published delay measured by repeating quasar variability. The y-axis is computed from image/deflector astrometry and redshifts only. Closeness to the diagonal is recovery of established lensing structure; displacement from it retains lens-profile, ellipticity, environment, cosmology, and measurement effects."
        )},
        {"id": "comparison_chart", "type": "chart", "chartId": "observed_predicted", "layout": "full"},
        {"id": "decomposition_text", "type": "markdown", "sourceId": theory_source["id"], "body": (
            "## Travelled path and Connection potential are separable terms in the arrival relation\n\n"
            "The conventional Fermat delay contains a geometric path term and a lens-potential term. In the concentrated point-mass landmark both contribute. In the ideal extended SIS landmark the two geometric image terms cancel differentially, so the potential term carries the A–B delay. This is a physical model-family distinction, not a relabelling of the light identity."
        )},
        {"id": "contribution_chart", "type": "chart", "chartId": "contributions", "layout": "full"},
        {"id": "ara_text", "type": "markdown", "sourceId": source["id"], "body": (
            "## The 0–2 view is a contribution cut, not a newly assumed Di-ARA\n\n"
            "Each native component is divided by the total absolute component amount and mapped to 0–2. The ridge x+y=2 is therefore definitional for this cut. The informative shape is the model-dependent position along that ridge: concentrated mass shares delay between path and potential, while ideal SIS sits on the Connection pole."
        )},
        {"id": "ara_chart", "type": "chart", "chartId": "ara_cut", "layout": "full"},
        {"id": "residual_text", "type": "markdown", "sourceId": source["id"], "body": (
            "## An identity-only forecast leaves observable relation structure unresolved\n\n"
            "The opening-angle diagnostic is measured independently of the delay. It does not identify all missing couplings, but it makes the methodological point testable: even before timing, the sky geometry can warn that a one-parent axisymmetric relation is incomplete. A future predictor needs the path direction, the opposing lens field, and relevant external overlaps."
        )},
        {"id": "residual_chart", "type": "chart", "chartId": "residual_geometry", "layout": "full"},
        {"id": "table", "type": "table", "tableId": "system_detail", "layout": "full"},
        {"id": "scope", "type": "markdown", "sourceId": source["id"], "body": (
            "## Scope and data quality\n\n"
            "The parent is the foreground deflector; the children are the two observed light paths of one quasar signal. Eligibility required an exact A/B/G double, both redshifts, a published A–B delay, and an opening angle of at least 150°. Catalogue signs are preserved in CSV, while the cross-system comparison uses magnitudes because literature sign conventions differ."
        )},
        {"id": "method", "type": "markdown", "body": (
            "## Frozen methodology and controls\n\n"
            "The lens families, cosmology conversion, eligibility, and evaluation were frozen before scoring. Delays were not fitted. Controls permuted observed delays 10,000 times, and leave-one-system-out summaries test whether one lens drives the aggregate. Native days remain primary; ARA coordinates are secondary visualization."
        )},
        {"id": "limits", "type": "markdown", "body": (
            "## What this does not establish\n\n"
            "Neither axisymmetric landmark is a modern full lens model. The residual cannot be assigned to a new force or ARA identity: it combines mass profile, ellipticity, external shear, line-of-sight convergence, microlensing/time-delay systematics, cosmology, and astrometry. The catalogue contains completed handovers, so this is reconstruction rather than live pre-event prediction."
        )},
        {"id": "next", "type": "markdown", "body": (
            "## Recommended next step\n\n"
            "Choose one system with public posterior lens models and line-of-sight data. Freeze a full model, remove one independently measured coupling at a time, and test whether the resulting delay displacement follows the ARA relation predicted from that removed identity. That is the clean bridge from a landmark recovery to an external-overlap test."
        )},
        {"id": "questions", "type": "markdown", "body": (
            "## Further questions\n\n"
            "- Does independently published external shear reduce residuals in the predicted direction?\n"
            "- Does the path/potential share remain stable across posterior lens models?\n"
            "- Can a future monitored transient turn the completed-handover reconstruction into a genuinely chronological prediction?"
        )},
    ]
    return {
        "surface": "report",
        "manifest": {
            "version": 1, "surface": "report", "title": "Real gravitational-lens distance/time decomposition",
            "description": "A geometry-first ARA audit of travelled-path and Connection-potential contributions in real strong-lens time delays.",
            "generatedAt": generated_at, "cards": metrics, "charts": charts, "tables": [table],
            "sources": [source, theory_source], "blocks": blocks,
        },
        "snapshot": {
            "version": 1, "generatedAt": generated_at, "status": "ready",
            "datasets": {
                "headline": [{
                    "eligible_systems": len(frame), "pm_rho": pm["spearman_rho"], "sis_rho": sis["spearman_rho"],
                    "pm_factor": pm["median_factor_error"], "sis_factor": sis["median_factor_error"],
                }],
                "comparison": comparison_rows, "contributions": contribution_rows, "ara": ara_rows,
                "residuals": residual_rows, "system_detail": records(report_frame, report_columns),
            },
        },
        "sources": [source, theory_source],
    }


def main() -> None:
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    a1 = load_vizier_tsv(DATA / "tablea1.tsv")
    b1 = load_vizier_tsv(DATA / "tableb1.tsv")
    frame, quality = build_systems(a1, b1)
    if len(frame) < 5:
        raise RuntimeError(f"too few eligible systems for the frozen test: {len(frame)}")

    controls = []
    control_summaries = {}
    for model in ["pm", "sis"]:
        control_frame, control_summary = permutation_controls(frame, model)
        controls.append(control_frame)
        control_summaries[model] = control_summary
    controls_frame = pd.concat(controls, ignore_index=True)

    summary = {
        "test": "T444",
        "generated_at": generated_at,
        "frozen_cosmology": {"H0_km_s_Mpc": H0, "Omega_m": OMEGA_M},
        "quality": quality,
        "models": {model: model_metrics(frame, model) for model in ["pm", "sis"]},
        "permutation_controls": control_summaries,
        "residual_relations": {model: residual_relations(frame, model) for model in ["pm", "sis"]},
        "interpretation": {
            "claim_type": "descriptive reconstruction with frozen conventional landmarks",
            "ara_result": "travelled-path and Connection-potential terms are separately recoverable, but exact prediction remains coupling/model dependent",
            "not_established": "a new physical force, unique ARA identity, or live future prediction",
        },
    }

    leave_one_out_frame = leave_one_out(frame)
    frame.to_csv(RESULTS / "T444_SYSTEM_RESULTS.csv", index=False)
    controls_frame.to_csv(RESULTS / "T444_PERMUTATION_CONTROLS.csv", index=False)
    leave_one_out_frame.to_csv(RESULTS / "T444_LEAVE_ONE_OUT.csv", index=False)
    (RESULTS / "T444_SUMMARY.json").write_text(json.dumps(json_ready(summary), indent=2), encoding="utf-8")

    plot_sky_geometries(frame)
    plot_geometry_first(frame, summary)
    artifact = build_artifact(frame, summary, generated_at)
    (RESULTS / "artifact.json").write_text(json.dumps(json_ready(artifact), indent=2), encoding="utf-8")
    print(json.dumps(json_ready(summary), indent=2))


if __name__ == "__main__":
    main()
