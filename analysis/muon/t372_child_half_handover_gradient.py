"""T372: native-resolution child-half handover and asymmetry gradient audit.

This is a post-result calibration on the opened T371 COHERENT record.  It
corrects the coarse cumulative plotting convention, maps the full native
gradient, bootstraps uncertainty and exports reader-facing artifacts.
"""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".mplcache"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import uproot
from scipy.optimize import brentq

import t371_coherent_pion_muon_diara as t371


HERE = Path(__file__).resolve().parent
SEED = 372
N_BOOT = 2000


def native_branch(root_file: uproot.ReadOnlyDirectory, key: str, response: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return native-time observed response without normalizing the branch."""
    h = root_file[key]
    values = h.values(flow=False)
    edges_ns = h.axes[0].edges()
    times_us = (edges_ns[:-1] + edges_ns[1:]) / 2000.0
    keep = (times_us >= 0.0) & (times_us < 6.0)
    weighted = values[keep] * t371.time_efficiency(times_us[keep])[:, None]
    return times_us[keep], weighted @ response


def equality_and_coordinate(times: np.ndarray, prompt_rate: np.ndarray, delayed_rate: np.ndarray) -> tuple[float, float]:
    """Linear rate crossing plus cumulative ARA coordinate at that crossing."""
    diff = prompt_rate - delayed_rate
    candidates = np.where((diff[:-1] >= 0) & (diff[1:] < 0))[0]
    if not len(candidates):
        return float("nan"), float("nan")
    i = int(candidates[0])
    frac = float(diff[i] / (diff[i] - diff[i + 1]))
    handover_t = float(times[i] + frac * (times[i + 1] - times[i]))
    total = prompt_rate + delayed_rate
    cumulative = 2.0 * np.cumsum(total) / np.sum(total)
    handover_x = float(cumulative[i] + frac * (cumulative[i + 1] - cumulative[i]))
    return handover_t, handover_x


def build_inputs() -> dict:
    c_events = np.loadtxt(t371.DATA / "dataBeamOnC.txt")
    ac_events = np.loadtxt(t371.DATA / "dataBeamOnAC.txt")
    y_c = t371.hist2(c_events)
    y_ac = t371.hist2(ac_events)
    ss = t371.steady_template(ac_events[(ac_events[:, 0] < 60) & (ac_events[:, 1] < 12)])
    brn = t371.released_background("brnPE.txt", "brnTrec.txt")
    nin = t371.released_background("ninPE.txt", "ninTrec.txt")
    response = t371.recoil_response()
    root_file = uproot.open(t371.DATA / "snsFlux2D.root")
    times, prompt_raw_native = native_branch(root_file, "convolved_energy_time_of_nu_mu", response)
    _, delayed_mu_raw_native = native_branch(root_file, "convolved_energy_time_of_anti_nu_mu", response)
    _, delayed_e_raw_native = native_branch(root_file, "convolved_energy_time_of_nu_e", response)
    delayed_raw_native = delayed_mu_raw_native + delayed_e_raw_native

    prompt_native = prompt_raw_native / prompt_raw_native.sum()
    delayed_native = delayed_raw_native / delayed_raw_native.sum()
    prompt_binned = t371.normalize(prompt_native.reshape(12, 500, 6).sum(axis=1).T)
    delayed_binned = t371.normalize(delayed_native.reshape(12, 500, 6).sum(axis=1).T)
    templates = [ss, brn, nin, prompt_binned, delayed_binned]
    fit = t371.fit_model(y_c, y_ac, templates)
    return {
        "times": times,
        "prompt_raw_native": prompt_raw_native,
        "delayed_raw_native": delayed_raw_native,
        "prompt_native": prompt_native,
        "delayed_native": delayed_native,
        "templates": templates,
        "fit": fit,
        "y_c": y_c,
        "y_ac": y_ac,
    }


def main() -> None:
    data = build_inputs()
    times = data["times"]
    p2 = data["prompt_native"]
    d2 = data["delayed_native"]
    p_shape = p2.sum(axis=1)
    d_shape = d2.sum(axis=1)
    params = data["fit"]["params"]
    n_ss, n_brn, n_nin, n_prompt, n_delayed = params
    observed_share = float(n_prompt / (n_prompt + n_delayed))

    prompt_rate = n_prompt * p_shape
    delayed_rate = n_delayed * d_shape
    native_t, native_x = equality_and_coordinate(times, prompt_rate, delayed_rate)

    prompt_raw = data["prompt_raw_native"]
    delayed_raw = data["delayed_raw_native"]
    model_share = float(prompt_raw.sum() / (prompt_raw.sum() + delayed_raw.sum()))
    model_t, model_x = equality_and_coordinate(times, model_share * p_shape, (1.0 - model_share) * d_shape)

    # Reproduce the opened T371 plot convention for an explicit audit trail.
    old = json.loads((HERE / "T371_COHERENT_PION_MUON_DIARA_RESULTS.json").read_text(encoding="utf-8"))
    coarse_t = float(old["timing"]["instantaneous_branch_equality_us"])
    coarse_p = n_prompt * data["templates"][3].sum(axis=0)
    coarse_d = n_delayed * data["templates"][4].sum(axis=0)
    coarse_cumulative = 2.0 * np.cumsum(coarse_p + coarse_d) / np.sum(coarse_p + coarse_d)
    i = int(np.searchsorted(t371.T_CENTERS, coarse_t) - 1)
    i = max(0, min(i, len(t371.T_CENTERS) - 2))
    frac = (coarse_t - t371.T_CENTERS[i]) / (t371.T_CENTERS[i + 1] - t371.T_CENTERS[i])
    coarse_x = float(coarse_cumulative[i] + frac * (coarse_cumulative[i + 1] - coarse_cumulative[i]))

    # Parametric uncertainty from the full registered T371 likelihood.
    ss, brn, nin, prompt_binned, delayed_binned = data["templates"]
    mu_c = n_ss * ss + n_brn * brn + n_nin * nin + n_prompt * prompt_binned + n_delayed * delayed_binned
    mu_ac = n_ss * ss
    rng = np.random.default_rng(SEED)
    boot = np.full((N_BOOT, 4), np.nan)
    for b in range(N_BOOT):
        fit_b = t371.fit_model(
            rng.poisson(mu_c), rng.poisson(mu_ac), data["templates"], start=params
        )
        pb, db = fit_b["params"][3], fit_b["params"][4]
        if pb + db > 0:
            tb, xb = equality_and_coordinate(times, pb * p_shape, db * d_shape)
            boot[b] = [pb / (pb + db), tb, xb, xb - 0.5]
    valid_boot = boot[np.isfinite(boot).all(axis=1)]
    ci = np.percentile(valid_boot, [2.5, 50, 97.5], axis=0)

    # Exact identity-specific map once the two native branch shapes are fixed.
    shares = np.linspace(0.02, 0.98, 193)
    gradient_rows = []
    for share in shares:
        th, xh = equality_and_coordinate(times, share * p_shape, (1.0 - share) * d_shape)
        gradient_rows.append((share, 1.0 - 2.0 * share, th, xh, xh - 0.5))
    gradient = np.asarray(gradient_rows, dtype=float)
    finite = np.isfinite(gradient[:, 3])

    def coordinate_for_share(share: float) -> float:
        return equality_and_coordinate(times, share * p_shape, (1.0 - share) * d_shape)[1]

    share_at_half = float(brentq(lambda s: coordinate_for_share(s) - 0.5, 0.02, 0.98))

    # Energy cuts are sensitivity views of one experiment, not replications.
    energy_rows = []
    for e in range(6):
        p_rate_e = n_prompt * p2[:, e]
        d_rate_e = n_delayed * d2[:, e]
        total_e = p_rate_e.sum() + d_rate_e.sum()
        share_e = float(p_rate_e.sum() / total_e)
        th, xh = equality_and_coordinate(times, p_rate_e, d_rate_e)
        energy_rows.append((e * 10, (e + 1) * 10, share_e, th, xh, xh - 0.5))

    total_rate = prompt_rate + delayed_rate
    cumulative = 2.0 * np.cumsum(total_rate) / np.sum(total_rate)
    gradient_sample = np.column_stack([
        times[::5], prompt_rate[::5], delayed_rate[::5], cumulative[::5]
    ])

    exact_half_in_ci = bool(ci[0, 2] <= 0.5 <= ci[2, 2])
    model_in_ci = bool(ci[0, 2] <= model_x <= ci[2, 2])
    results = {
        "test": "T372",
        "date": "2026-08-13",
        "evidence_class": "post-result native-resolution calibration on opened T371 data",
        "verdict": "HANDOVER GRADIENT MAPPED; EXACT CHILD-HALF REMAINS UNCONFIRMED",
        "theory_status": "strong ARA theory; requires frozen external replication",
        "coarse_plot_audit": {
            "handover_time_us": coarse_t,
            "cumulative_ara_at_handover": coarse_x,
            "warning": "Completed 0.5-us bins were plotted at bin centres; this is not the native integral.",
        },
        "native_fit": {
            "prompt_share": observed_share,
            "parent_asymmetry_delayed_minus_prompt": 1.0 - 2.0 * observed_share,
            "handover_time_us": native_t,
            "cumulative_ara_at_handover": native_x,
            "displacement_from_child_half": native_x - 0.5,
            "bootstrap_95pct": {
                "prompt_share": ci[[0, 2], 0].tolist(),
                "handover_time_us": ci[[0, 2], 1].tolist(),
                "cumulative_ara_at_handover": ci[[0, 2], 2].tolist(),
                "displacement": ci[[0, 2], 3].tolist(),
                "valid_replicates": int(len(valid_boot)),
            },
        },
        "collaboration_source_crosscheck": {
            "prompt_share": model_share,
            "handover_time_us": model_t,
            "cumulative_ara_at_handover": model_x,
            "inside_fit_bootstrap_interval": model_in_ci,
        },
        "identity_specific_gradient": {
            "share_that_places_handover_at_exact_half": share_at_half,
            "observed_share_minus_exact_half_share": observed_share - share_at_half,
            "monotone_over_finite_sweep": bool(np.all(np.diff(gradient[finite, 3]) > 0)),
            "interpretation": "Exact mathematical dependency after fixing branch shapes; not independent physical evidence.",
        },
        "tests": {
            "native_handover_resolved": bool(np.isfinite(native_t) and np.isfinite(native_x)),
            "collaboration_model_inside_fit_interval": model_in_ci,
            "exact_half_inside_fit_interval": exact_half_in_ci,
            "all_energy_cuts_resolve_handover": bool(np.isfinite(np.asarray(energy_rows)[:, 4]).all()),
        },
        "boundaries": [
            "T372 is post-result and cannot independently confirm the theory.",
            "Counterfactual parent-weight sweeps use fixed extracted shapes.",
            "Energy bands are cuts of one experiment, not independent replications.",
            "The pure x=0.5 landmark and identity-specific physical coordinate must remain distinct.",
            "No universal Phi law is claimed.",
        ],
    }

    (HERE / "T372_CHILD_HALF_HANDOVER_GRADIENT_RESULTS.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    with (HERE / "T372_CHILD_HALF_HANDOVER_GRADIENT.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["prompt_share", "parent_asymmetry_delayed_minus_prompt", "handover_time_us", "cumulative_ara_at_handover", "displacement_from_0_5"])
        w.writerows(gradient_rows)
    with (HERE / "T372_CHILD_HALF_HANDOVER_ENERGY_CUTS.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pe_low", "pe_high", "prompt_share", "handover_time_us", "cumulative_ara_at_handover", "displacement_from_0_5"])
        w.writerows(energy_rows)
    np.savetxt(
        HERE / "T372_CHILD_HALF_HANDOVER_NATIVE_SERIES.csv", gradient_sample,
        delimiter=",", header="time_us,prompt_rate,delayed_rate,cumulative_ara", comments=""
    )

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=True)
    blue, orange, red, green = "#2f7ed8", "#ed9b33", "#c33c54", "#1b9e77"

    view = times <= 2.5
    axes[0, 0].plot(times[view], prompt_rate[view] * 1000, color=blue, label="prompt pion branch")
    axes[0, 0].plot(times[view], delayed_rate[view] * 1000, color=orange, label="delayed muon branch")
    axes[0, 0].axvline(native_t, color=red, ls="--", label=f"native equality {native_t:.3f} us")
    axes[0, 0].set(title="Native release-flow handover", xlabel="time after beam pulse (us)", ylabel="fitted events per microsecond")
    axes[0, 0].legend(fontsize=9)

    axes[0, 1].plot(times[view], cumulative[view], color=green, lw=2)
    axes[0, 1].axhline(0.5, color="#666666", ls=":", label="proposed pure child landmark 0.5")
    axes[0, 1].axhline(1.0, color="black", label="parent ridge 1.0")
    axes[0, 1].scatter([native_t], [native_x], s=70, color=red, zorder=4, label=f"measured handover {native_x:.3f}")
    axes[0, 1].scatter([model_t], [model_x], s=65, facecolor="white", edgecolor="#7b3294", lw=2, zorder=4, label=f"source-model handover {model_x:.3f}")
    axes[0, 1].set(title="Cumulative ARA coordinate at handover", xlabel="time after beam pulse (us)", ylabel="cumulative ARA release", ylim=(0, 2.03))
    axes[0, 1].legend(fontsize=9)

    axes[1, 0].plot(gradient[finite, 0], gradient[finite, 3], color="#5e3c99", lw=2, label="fixed-shape asymmetry gradient")
    axes[1, 0].axhline(0.5, color="#666666", ls=":")
    axes[1, 0].axvline(share_at_half, color="#666666", ls=":", label=f"share for exact 0.5 = {share_at_half:.3f}")
    axes[1, 0].scatter([observed_share], [native_x], color=red, s=70, zorder=4, label="T371 fitted balance")
    axes[1, 0].scatter([model_share], [model_x], facecolor="white", edgecolor="#7b3294", lw=2, s=70, zorder=4, label="collaboration-source balance")
    axes[1, 0].set(title="Parent balance displaces the handover", xlabel="prompt share of detected two-branch release", ylabel="ARA coordinate at branch equality", xlim=(0, 1), ylim=(0, 2))
    axes[1, 0].legend(fontsize=8)

    er = np.asarray(energy_rows)
    axes[1, 1].scatter(er[:, 2], er[:, 4], c=np.arange(6), cmap="viridis", s=85, edgecolor="black")
    for row in energy_rows:
        axes[1, 1].annotate(f"{int(row[0])}-{int(row[1])} PE", (row[2], row[4]), xytext=(5, 3), textcoords="offset points", fontsize=8)
    axes[1, 1].axhline(0.5, color="#666666", ls=":")
    axes[1, 1].set(title="Energy cuts retain an oriented but identity-specific gradient", xlabel="prompt share within energy cut", ylabel="ARA coordinate at branch equality", xlim=(0, 0.45), ylim=(0, 1.0))

    fig.suptitle("T372 — child-half handover and parent-asymmetry gradient\nPost-result native-resolution audit; not an independent confirmation", fontsize=16, fontweight="bold")
    fig.savefig(HERE / "T372_CHILD_HALF_HANDOVER_GRADIENT_FIGURE.png", dpi=180)
    fig.savefig(HERE / "T372_CHILD_HALF_HANDOVER_GRADIENT_FIGURE.svg")
    plt.close(fig)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()

