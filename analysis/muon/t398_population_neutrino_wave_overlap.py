#!/usr/bin/env python3
"""T398: evidence-graded population neutrino wave overlap.

This is deliberately not an individual-event birth-time claim.  It rebuilds
the official COHERENT flavor timing templates at native 1 ns resolution,
displays every fifth sample, preserves the frozen T372 handover, and keeps the
separate RAL Silver spin-phase result on its own coordinate.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENDOR = HERE / ".t398_vendor"
if VENDOR.exists():
    sys.path.insert(0, str(VENDOR))

import numpy as np
import uproot
from scipy.special import spherical_jn
from scipy.stats import gamma

DATA = Path(r"F:\SystemFormulaFolder\external_data\coherent_csi_2110_07730\anc")
OUT = HERE / "T398_population_neutrino_wave_overlap"
T371_COMPONENTS = HERE / "T371_COHERENT_PION_MUON_DIARA_COMPONENTS.csv"
T371_RESULTS = HERE / "T371_COHERENT_PION_MUON_DIARA_RESULTS.json"
T372_NATIVE = HERE / "T372_CHILD_HALF_HANDOVER_NATIVE_SERIES.csv"
T372_RESULTS = HERE / "T372_CHILD_HALF_HANDOVER_GRADIENT_RESULTS.json"
T378_COMPONENTS = HERE / "T378_coherent_2017_holdout" / "T378_timing_components.csv"
T378_RESULTS = HERE / "T378_coherent_2017_holdout" / "T378_results.json"
T397_PROFILES = HERE / "T397_spin_phase_maturity_vs_orientation" / "T397_PHASE_PROFILES.csv"
PROTOCOL = HERE / "T398_POPULATION_NEUTRINO_WAVE_OVERLAP_PROTOCOL_2026-08-17.md"


def energy_efficiency(pe: np.ndarray) -> np.ndarray:
    a, b, c, d = 1.32045, 0.285979, 10.8646, -0.333322
    return np.clip(a / (1.0 + np.exp(-b * (pe - c))) + d, 0.0, 1.0)


def time_efficiency(t_us: np.ndarray) -> np.ndarray:
    return np.where(t_us < 0.52, 1.0, np.exp(-0.0494 * (t_us - 0.52)))


def helm_form_factor(q_mev: np.ndarray, mass_number: float) -> np.ndarray:
    q = q_mev / 197.3269804
    skin = 0.9
    radius = 1.2 * mass_number ** (1.0 / 3.0)
    r0 = math.sqrt(max(radius * radius - 5.0 * skin * skin, 1e-12))
    z = q * r0
    out = np.ones_like(z)
    nonzero = np.abs(z) > 1e-12
    out[nonzero] = 3.0 * spherical_jn(1, z[nonzero]) / z[nonzero]
    return out * np.exp(-0.5 * (q * skin) ** 2)


def pe_response(t_mev: np.ndarray) -> np.ndarray:
    a, b, c, d = 0.0554628, 4.30681, -111.707, 840.384
    electron_equivalent_kev = 1000.0 * (
        a * t_mev + b * t_mev**2 + c * t_mev**3 + d * t_mev**4
    )
    electron_equivalent_kev = np.maximum(electron_equivalent_kev, 1e-12)
    shape = 1.0 + 9.56 * electron_equivalent_kev
    rate = (0.0749 / electron_equivalent_kev) * shape
    scale = 1.0 / rate
    one_pe_edges = np.arange(0.0, 61.0, 1.0)
    probabilities = np.diff(
        gamma.cdf(one_pe_edges[None, :], a=shape[:, None], scale=scale[:, None]), axis=1
    )
    probabilities *= energy_efficiency((one_pe_edges[:-1] + one_pe_edges[1:]) / 2)[None, :]
    return probabilities.reshape(len(t_mev), 6, 10).sum(axis=2)


def recoil_response() -> np.ndarray:
    """Reproduce T371's flavor-independent CEvNS detector response."""
    neutrino_energy = np.arange(0.5, 600.0, 1.0)
    recoil_edges = np.linspace(0.0, 0.08, 801)
    recoil = (recoil_edges[:-1] + recoil_edges[1:]) / 2
    delta_recoil = np.diff(recoil_edges)
    response_pe = pe_response(recoil)
    result = np.zeros((len(neutrino_energy), 6))
    sin2 = 0.23857
    for mass_number, proton_number in ((132.90545196, 55), (126.9044719, 53)):
        neutron_number = round(mass_number) - proton_number
        nucleus_mass = mass_number * 931.49410242
        weak_charge = neutron_number - (1.0 - 4.0 * sin2) * proton_number
        tmax = 2.0 * neutrino_energy**2 / (nucleus_mass + 2.0 * neutrino_energy)
        kinematic = 1.0 - nucleus_mass * recoil[None, :] / (2.0 * neutrino_energy[:, None] ** 2)
        valid = recoil[None, :] <= tmax[:, None]
        q = np.sqrt(2.0 * nucleus_mass * recoil)
        form_factor_sq = helm_form_factor(q, mass_number) ** 2
        differential = (
            weak_charge**2
            * nucleus_mass
            * np.clip(kinematic, 0.0, None)
            * valid
            * form_factor_sq[None, :]
        )
        result += (differential * delta_recoil[None, :]) @ response_pe
    return result


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"No rows for {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def native_detector_weighted_profile(
    root_file: uproot.ReadOnlyDirectory,
    key: str,
    response: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return 1 ns time centres and detector-weighted, efficiency-folded shape."""
    hist = root_file[key]
    values = np.asarray(hist.values(flow=False), dtype=float)
    time_edges_ns = np.asarray(hist.axes[0].edges(), dtype=float)
    time_ns = (time_edges_ns[:-1] + time_edges_ns[1:]) / 2.0
    energy_edges = np.asarray(hist.axes[1].edges(), dtype=float)
    energy_mev = (energy_edges[:-1] + energy_edges[1:]) / 2.0
    expected = np.arange(0.5, 600.0, 1.0)
    if values.shape[1] != response.shape[0] or not np.allclose(energy_mev, expected):
        raise ValueError(f"Unexpected source schema for {key}")
    keep = (time_ns >= 0.0) & (time_ns < 6000.0)
    weighted = values[keep] * time_efficiency(time_ns[keep] / 1000.0)[:, None]
    detector_weight_by_energy = response.sum(axis=1)
    profile = weighted @ detector_weight_by_energy
    return time_ns[keep] / 1000.0, np.asarray(profile, dtype=float)


def first_crossing(time_us: np.ndarray, a: np.ndarray, b: np.ndarray) -> float:
    diff = a - b
    # Ignore numerical near-zero source tails and select the first proper sign
    # change after the prompt branch has become established.
    peak = int(np.argmax(a))
    for index in range(peak, len(diff) - 1):
        if diff[index] >= 0.0 and diff[index + 1] <= 0.0:
            x0, x1 = time_us[index], time_us[index + 1]
            y0, y1 = diff[index], diff[index + 1]
            if y1 == y0:
                return float(x0)
            return float(x0 - y0 * (x1 - x0) / (y1 - y0))
    return float("nan")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    t371 = json.loads(T371_RESULTS.read_text(encoding="utf-8"))
    t372 = json.loads(T372_RESULTS.read_text(encoding="utf-8"))
    t378 = json.loads(T378_RESULTS.read_text(encoding="utf-8"))

    response = recoil_response()
    root_file = uproot.open(DATA / "snsFlux2D.root")
    native_time, prompt_shape = native_detector_weighted_profile(
        root_file, "convolved_energy_time_of_nu_mu", response
    )
    time_e, nue_shape = native_detector_weighted_profile(
        root_file, "convolved_energy_time_of_nu_e", response
    )
    time_m, antinumu_shape = native_detector_weighted_profile(
        root_file, "convolved_energy_time_of_anti_nu_mu", response
    )
    if not (np.array_equal(native_time, time_e) and np.array_equal(native_time, time_m)):
        raise ValueError("Flavor timing axes differ")

    n_prompt = float(t371["fit"]["prompt_nu_mu"])
    n_delayed = float(t371["fit"]["delayed_nu_e_plus_anti_nu_mu"])
    prompt_rate = n_prompt * prompt_shape / prompt_shape.sum()
    delayed_denominator = float(nue_shape.sum() + antinumu_shape.sum())
    nue_rate = n_delayed * nue_shape / delayed_denominator
    antinumu_rate = n_delayed * antinumu_shape / delayed_denominator
    delayed_rate = nue_rate + antinumu_rate

    cumulative_release = np.cumsum(delayed_rate) / delayed_rate.sum()
    remaining_muon = 1.0 - cumulative_release
    sample = np.arange(0, len(native_time), 5)
    display_time = native_time[sample]
    prompt_display = prompt_rate[sample]
    nue_display = nue_rate[sample]
    antinumu_display = antinumu_rate[sample]
    delayed_display = delayed_rate[sample]
    remaining_display = remaining_muon[sample]
    release_display = cumulative_release[sample]

    saved_native = read_csv(T372_NATIVE)
    saved_time = np.array([float(row["time_us"]) for row in saved_native])
    saved_prompt = np.array([float(row["prompt_rate"]) for row in saved_native])
    saved_delayed = np.array([float(row["delayed_rate"]) for row in saved_native])
    saved_ara = np.array([float(row["cumulative_ara"]) for row in saved_native])
    if len(saved_time) != len(display_time) or not np.allclose(saved_time, display_time, atol=1e-15):
        raise ValueError("T372 display axis does not match reconstructed native axis")

    delayed_peak = float(np.max(delayed_display))
    prompt_peak = float(np.max(prompt_display))
    overlap_rows: list[dict[str, object]] = []
    for i in range(len(display_time)):
        overlap_rows.append(
            {
                "time_us": float(display_time[i]),
                "prompt_nu_mu_peak_normalized": float(prompt_display[i] / prompt_peak),
                "inferred_muon_remaining_fraction": float(remaining_display[i]),
                "nu_e_release_over_delayed_peak": float(nue_display[i] / delayed_peak),
                "anti_nu_mu_release_over_delayed_peak": float(antinumu_display[i] / delayed_peak),
                "delayed_total_release_peak_normalized": float(delayed_display[i] / delayed_peak),
                "cumulative_delayed_release_fraction": float(release_display[i]),
                "cumulative_ara_0_to_2": float(saved_ara[i]),
                "prompt_fitted_events_per_native_ns": float(prompt_display[i]),
                "nu_e_fitted_events_per_native_ns": float(nue_display[i]),
                "anti_nu_mu_fitted_events_per_native_ns": float(antinumu_display[i]),
                "delayed_total_fitted_events_per_native_ns": float(delayed_display[i]),
            }
        )
    write_csv(OUT / "T398_NATIVE_WAVE_OVERLAP.csv", overlap_rows)

    binned_rows: list[dict[str, object]] = []
    for row in read_csv(T371_COMPONENTS):
        observed_c = float(row["observed_C"])
        observed_ac = float(row["observed_AC"])
        background = float(row["steady"]) + float(row["BRN"]) + float(row["NIN"])
        prompt = float(row["prompt_nu_mu"])
        delayed = float(row["delayed_nu_e_plus_anti_nu_mu"])
        binned_rows.append(
            {
                "time_us": float(row["time_us"]),
                "observed_beam_coincident": observed_c,
                "observed_anti_coincident": observed_ac,
                "observed_excess_C_minus_AC": observed_c - observed_ac,
                "fitted_background": background,
                "fitted_prompt_nu_mu": prompt,
                "fitted_delayed_nu_e_plus_anti_nu_mu": delayed,
                "fitted_total": background + prompt + delayed,
            }
        )
    write_csv(OUT / "T398_T371_MEASURED_AND_FITTED.csv", binned_rows)

    holdout_rows: list[dict[str, object]] = []
    for row in read_csv(T378_COMPONENTS):
        c = float(row["beam_on_C"])
        ac = float(row["beam_on_AC"])
        holdout_rows.append(
            {
                "time_us": float(row["time_us"]),
                "observed_beam_on_C": c,
                "observed_beam_on_AC": ac,
                "observed_excess_C_minus_AC": c - ac,
                "fitted_background": float(row["steady_fit"]) + float(row["prompt_neutron_fit"]),
                "fitted_prompt_nu_mu": float(row["prompt_neutrino_fit"]),
                "fitted_delayed_nu_e_plus_anti_nu_mu": float(row["delayed_neutrino_fit"]),
                "fitted_total": float(row["total_fit"]),
            }
        )
    write_csv(OUT / "T398_T378_INDEPENDENT_HOLDOUT.csv", holdout_rows)

    phase_rows: list[dict[str, object]] = []
    for row in read_csv(T397_PROFILES):
        if float(row["field_g"]) != 160.0 or row["channel"] != "W":
            continue
        phase_rows.extend(
            [
                {
                    "phase_turn": float(row["phase_turn"]),
                    "residual_pct": 100.0 * float(row["observed_fractional_residual"]),
                    "series": "160 G observed common mode",
                    "source_identity": "RAL Silver T397 (separate experiment)",
                },
                {
                    "phase_turn": float(row["phase_turn"]),
                    "residual_pct": 100.0 * float(row["predicted_fractional_residual"]),
                    "series": "160 G fitted spin phase",
                    "source_identity": "RAL Silver T397 (separate experiment)",
                },
            ]
        )
    write_csv(OUT / "T398_T397_SEPARATE_PHASE_COMPARISON.csv", phase_rows)

    reconstructed_handover = first_crossing(native_time, prompt_rate, delayed_rate)
    t372_handover = float(t372["native_fit"]["handover_time_us"])
    t372_ci = [float(value) for value in t372["native_fit"]["bootstrap_95pct"]["handover_time_us"]]
    prompt_error = float(np.max(np.abs(prompt_display - saved_prompt)))
    delayed_error = float(np.max(np.abs(delayed_display - saved_delayed)))
    flavor_closure_error = float(np.max(np.abs((nue_display + antinumu_display) - delayed_display)))
    t378_prompt = float(t378["fit"]["params"][2])
    t378_delayed = float(t378["fit"]["params"][3])

    gates = {
        "G1_native_profiles_reproduce_T372": bool(prompt_error < 1e-10 and delayed_error < 1e-10),
        "G2_T371_delayed_yield_interval_positive": bool(float(t371["fit"]["delayed_ci95"][0]) > 0.0),
        "G3_T371_delayed_branch_required_delta_AIC_at_least_10": bool(float(t371["fit"]["delta_aic_vs_prompt_only"]) >= 10.0),
        "G4_T371_delayed_crest_after_prompt": bool(float(t371["timing"]["delayed_peak_us"]) > float(t371["timing"]["prompt_peak_us"])),
        "G5_native_handover_inside_T372_bootstrap_interval": bool(t372_ci[0] <= reconstructed_handover <= t372_ci[1]),
        "G6_flavor_children_close_to_combined_delayed_branch": bool(flavor_closure_error < 1e-12),
        "G7_T378_positive_populations_and_correct_order": bool(t378_prompt > 0.0 and t378_delayed > 0.0 and float(t378["timing"]["delayed_peak_us"]) > float(t378["timing"]["prompt_peak_us"])),
        "G8_claim_boundary_is_population_not_individual": True,
    }
    verdict = (
        "POPULATION NEUTRINO RELEASE WAVEFORM OBSERVED; INDIVIDUAL BIRTH UNOBSERVED"
        if all(gates.values())
        else "DELAYED POPULATION PRESENT; OVERLAP INCOMPLETE"
    )

    result = {
        "test": "T398",
        "date": datetime.now(timezone.utc).date().isoformat(),
        "protocol_sha256": sha256(PROTOCOL),
        "verdict": verdict,
        "primary_identity": "COHERENT CsI stopped-pion -> stopped-muon -> delayed neutrino population",
        "time_window_us": [0.0, 6.0],
        "handover": {
            "reconstructed_native_equality_us": reconstructed_handover,
            "saved_T372_equality_us": t372_handover,
            "T372_bootstrap_95pct_us": t372_ci,
            "cumulative_ara_at_handover": float(t372["native_fit"]["cumulative_ara_at_handover"]),
            "interpretation": "instantaneous equality of fitted prompt and combined delayed population rates",
        },
        "T371_population_fit": {
            "prompt_nu_mu": n_prompt,
            "prompt_ci95": [float(value) for value in t371["fit"]["prompt_ci95"]],
            "delayed_nu_e_plus_anti_nu_mu": n_delayed,
            "delayed_ci95": [float(value) for value in t371["fit"]["delayed_ci95"]],
            "delta_aic_vs_prompt_only": float(t371["fit"]["delta_aic_vs_prompt_only"]),
            "prompt_peak_us_binned": float(t371["timing"]["prompt_peak_us"]),
            "delayed_peak_us_binned": float(t371["timing"]["delayed_peak_us"]),
            "nu_e_template_share_of_delayed": float(nue_shape.sum() / delayed_denominator),
            "anti_nu_mu_template_share_of_delayed": float(antinumu_shape.sum() / delayed_denominator),
        },
        "T378_independent_holdout": {
            "verdict": t378["verdict"],
            "prompt_nu_mu": t378_prompt,
            "prompt_ci95": [float(value) for value in t378["fit"]["prompt_ci95"]],
            "delayed_nu_e_plus_anti_nu_mu": t378_delayed,
            "delayed_ci95": [float(value) for value in t378["fit"]["delayed_ci95"]],
            "prompt_peak_us": float(t378["timing"]["prompt_peak_us"]),
            "delayed_peak_us": float(t378["timing"]["delayed_peak_us"]),
            "handover_us": float(t378["timing"]["t_h_us"]),
            "strict_frozen_handover_gates_all_pass": False,
        },
        "reconstruction_checks": {
            "max_abs_prompt_error_vs_T372": prompt_error,
            "max_abs_delayed_error_vs_T372": delayed_error,
            "max_abs_flavor_closure_error": flavor_closure_error,
            "remaining_plus_released_max_abs_error": float(np.max(np.abs(remaining_muon + cumulative_release - 1.0))),
        },
        "gates": gates,
        "evidence_boundaries": [
            "COHERENT measures population timing distributions, not a named muon and its named daughter neutrinos.",
            "The delayed CsI branch combines nu_e and anti-nu_mu; the separate curves are released source-template components.",
            "The remaining-muon curve is derived from the tail integral of the delayed template and is not independent evidence.",
            "T397 RAL Silver is a separate medium and detector and is not event-linked to T371 or T378.",
            "The T378 holdout resolves the two populations in the correct order but retains its partial high-stringency verdict.",
        ],
        "input_hashes_sha256": {
            path.name: sha256(path)
            for path in (
                T371_COMPONENTS,
                T371_RESULTS,
                T372_NATIVE,
                T372_RESULTS,
                T378_COMPONENTS,
                T378_RESULTS,
                T397_PROFILES,
                DATA / "snsFlux2D.root",
            )
        },
    }
    (OUT / "T398_RESULTS.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({"output": str(OUT), "verdict": verdict, "gates": gates}, indent=2))


if __name__ == "__main__":
    main()
