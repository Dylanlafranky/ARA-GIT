"""T373: frozen transfer of the T372 child-half handover to COHERENT argon.

The released CEvNS model makes the branch-mixture prediction.  The released
3D event cube then estimates prompt and delayed branch amplitudes independently
in a Poisson likelihood with the collaboration's background constraints.
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
from scipy.optimize import brentq, minimize, nnls
from scipy.signal import fftconvolve


HERE = Path(__file__).resolve().parent
DATA = Path(r"F:\SystemFormulaFolder\external_data\coherent_argon_3903810")
SEED = 373
N_BOOT = 2000

TAU_PI_US = 0.026033
TAU_MU_US = 2.1969811
PULSE_MEAN_US = 0.440
PULSE_SIGMA_US = 0.150

BRN_PRIOR = (497.0, 160.0)
DBRN_PRIOR = (33.0, 33.0)
SS_PRIOR = (3154.0, 25.0)


def load_cube(filename: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    a = np.loadtxt(DATA / filename)
    energies = np.unique(a[:, 0])
    f90s = np.unique(a[:, 1])
    times = np.unique(a[:, 2])
    cube = np.zeros((len(energies), len(f90s), len(times)), dtype=float)
    ei = {v: i for i, v in enumerate(energies)}
    fi = {v: i for i, v in enumerate(f90s)}
    ti = {v: i for i, v in enumerate(times)}
    for e, f, t, v in a:
        cube[ei[e], fi[f], ti[t]] = v
    return energies, f90s, times, cube


def timing_bases(times: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Bin-integrated SNS prompt-pion and delayed-muon timing bases."""
    dt = 0.0005  # 0.5 ns numerical grid
    grid = np.arange(-2.0, 20.0 + dt, dt)
    gaussian = np.exp(-0.5 * ((grid - PULSE_MEAN_US) / PULSE_SIGMA_US) ** 2)
    gaussian /= np.trapezoid(gaussian, grid)

    positive = np.arange(0.0, 20.0 + dt, dt)
    k_pi = np.exp(-positive / TAU_PI_US) / TAU_PI_US
    k_mu = np.exp(-positive / TAU_MU_US) / TAU_MU_US
    prompt = fftconvolve(gaussian, k_pi, mode="full")[: len(grid)] * dt
    delayed = fftconvolve(prompt, k_mu, mode="full")[: len(grid)] * dt

    edges = np.r_[times[0] - 0.25, times + 0.25]

    def integrate_bins(curve: np.ndarray) -> np.ndarray:
        out = np.zeros(len(times))
        for i in range(len(times)):
            m = (grid >= edges[i]) & (grid < edges[i + 1])
            out[i] = np.trapezoid(curve[m], grid[m]) if np.count_nonzero(m) > 1 else 0.0
        return out / out.sum()

    return integrate_bins(prompt), integrate_bins(delayed)


def decompose_signal(signal: np.ndarray, p_time: np.ndarray, d_time: np.ndarray) -> dict:
    """NNLS prompt/delayed split in every energy x pulse-shape cell."""
    design = np.column_stack([p_time, d_time])
    p = np.zeros_like(signal)
    d = np.zeros_like(signal)
    coeff = np.zeros(signal.shape[:2] + (2,))
    for i in range(signal.shape[0]):
        for j in range(signal.shape[1]):
            c, _ = nnls(design, signal[i, j, :])
            coeff[i, j] = c
            p[i, j, :] = c[0] * p_time
            d[i, j, :] = c[1] * d_time
    recon = p + d
    nrmse = float(np.linalg.norm(recon - signal) / max(np.linalg.norm(signal), 1e-12))
    return {"prompt": p, "delayed": d, "coeff": coeff, "nrmse": nrmse}


def normalize(a: np.ndarray) -> np.ndarray:
    return a / a.sum()


def handover(times: np.ndarray, prompt_counts: np.ndarray, delayed_counts: np.ndarray) -> tuple[float, float]:
    """Rate equality at bin centres; cumulative ARA integrated within native bins."""
    width = 0.5
    p_rate = prompt_counts / width
    d_rate = delayed_counts / width
    diff = p_rate - d_rate
    candidates = np.where((diff[:-1] >= 0.0) & (diff[1:] < 0.0))[0]
    if not len(candidates):
        return float("nan"), float("nan")
    i = int(candidates[0])
    frac = float(diff[i] / (diff[i] - diff[i + 1]))
    t_h = float(times[i] + frac * (times[i + 1] - times[i]))

    total = prompt_counts + delayed_counts
    edges = np.r_[times[0] - width / 2.0, times + width / 2.0]
    k = int(np.searchsorted(edges, t_h, side="right") - 1)
    k = max(0, min(k, len(total) - 1))
    before = float(total[:k].sum())
    within = float((t_h - edges[k]) / width)
    within = min(1.0, max(0.0, within))
    cum = before + within * float(total[k])
    x_h = 2.0 * cum / float(total.sum())
    return t_h, x_h


def nll_free(theta: np.ndarray, y: np.ndarray, templates: list[np.ndarray]) -> float:
    mu = sum(v * t for v, t in zip(theta, templates))
    if np.any(mu <= 0):
        return 1e100
    val = float(np.sum(mu - y * np.log(mu)))
    for value, (mean, sigma) in zip(theta[2:], [BRN_PRIOR, DBRN_PRIOR, SS_PRIOR]):
        val += 0.5 * ((value - mean) / sigma) ** 2
    return val


def fit_free(y: np.ndarray, templates: list[np.ndarray], start: np.ndarray | None = None) -> dict:
    if start is None:
        start = np.asarray([30.0, 130.0, 550.0, 10.0, 3130.0])
    res = minimize(
        nll_free, start, args=(y, templates), method="L-BFGS-B",
        bounds=[(1e-8, None)] * 5, options={"maxiter": 3000, "ftol": 1e-11},
    )
    return {"params": res.x, "nll": float(res.fun), "success": bool(res.success), "message": str(res.message)}


def fit_fixed(y: np.ndarray, templates: list[np.ndarray], prompt_share: float) -> dict:
    p, d, brn, dbrn, ss = templates
    signal = prompt_share * p + (1.0 - prompt_share) * d
    fixed_templates = [signal, brn, dbrn, ss]

    def objective(theta: np.ndarray) -> float:
        mu = sum(v * t for v, t in zip(theta, fixed_templates))
        if np.any(mu <= 0):
            return 1e100
        val = float(np.sum(mu - y * np.log(mu)))
        for value, (mean, sigma) in zip(theta[1:], [BRN_PRIOR, DBRN_PRIOR, SS_PRIOR]):
            val += 0.5 * ((value - mean) / sigma) ** 2
        return val

    res = minimize(
        objective, np.asarray([159.0, 550.0, 10.0, 3130.0]), method="L-BFGS-B",
        bounds=[(1e-8, None)] * 4, options={"maxiter": 3000, "ftol": 1e-11},
    )
    return {"params": res.x, "nll": float(res.fun), "success": bool(res.success), "message": str(res.message)}


def profile_prompt_share(y: np.ndarray, templates: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """Post-result diagnostic: constrained profile over the signal prompt share."""
    shares = np.linspace(0.001, 0.999, 400)
    nll = np.asarray([fit_fixed(y, templates, float(s))["nll"] for s in shares])
    return shares, nll


def percentile_interval(a: np.ndarray) -> list[float]:
    return np.percentile(a[np.isfinite(a)], [2.5, 50.0, 97.5]).tolist()


def main() -> None:
    energies, f90s, times, y_cube = load_cube("datanobkgsub.txt")
    _, _, _, signal_cube = load_cube("cevnspdf.txt")
    _, _, _, brn_cube = load_cube("brnpdf.txt")
    _, _, _, dbrn_cube = load_cube("delbrnpdf.txt")
    _, _, _, ss_cube = load_cube("bkgpdf.txt")

    p_time, d_time = timing_bases(times)
    split = decompose_signal(signal_cube, p_time, d_time)
    p_model = split["prompt"]
    d_model = split["delayed"]
    model_prompt_total = float(p_model.sum())
    model_delayed_total = float(d_model.sum())
    model_share = model_prompt_total / (model_prompt_total + model_delayed_total)
    pred_t, pred_x = handover(times, p_model.sum(axis=(0, 1)), d_model.sum(axis=(0, 1)))

    p_template = normalize(p_model).ravel()
    d_template = normalize(d_model).ravel()
    templates = [p_template, d_template, normalize(brn_cube).ravel(), normalize(dbrn_cube).ravel(), normalize(ss_cube).ravel()]
    y = y_cube.ravel()
    fit = fit_free(y, templates)
    fixed = fit_fixed(y, templates, model_share)
    n_prompt, n_delayed, n_brn, n_dbrn, n_ss = fit["params"]
    measured_share = float(n_prompt / (n_prompt + n_delayed))
    fitted_p_t = n_prompt * p_model.sum(axis=(0, 1)) / model_prompt_total
    fitted_d_t = n_delayed * d_model.sum(axis=(0, 1)) / model_delayed_total
    meas_t, meas_x = handover(times, fitted_p_t, fitted_d_t)

    rng = np.random.default_rng(SEED)
    mu = sum(v * t for v, t in zip(fit["params"], templates))
    boot = np.full((N_BOOT, 5), np.nan)
    success_count = 0
    start = fit["params"]
    for b in range(N_BOOT):
        fb = fit_free(rng.poisson(mu), templates, start=start)
        if fb["success"]:
            success_count += 1
        bp, bd = fb["params"][:2]
        if bp > 1e-6 and bd > 1e-6 and bp + bd > 0:
            bt, bx = handover(
                times,
                bp * p_model.sum(axis=(0, 1)) / model_prompt_total,
                bd * d_model.sum(axis=(0, 1)) / model_delayed_total,
            )
            if np.isfinite(bt) and np.isfinite(bx):
                boot[b] = [bp / (bp + bd), bt, bx, bx - 0.5, bp + bd]
    valid = boot[np.isfinite(boot).all(axis=1)]
    valid_fraction = float(len(valid) / N_BOOT)
    ci_share = percentile_interval(valid[:, 0])
    ci_t = percentile_interval(valid[:, 1])
    ci_x = percentile_interval(valid[:, 2])
    ci_delta = percentile_interval(valid[:, 3])
    ci_signal = percentile_interval(valid[:, 4])

    transfer_pass = bool(ci_x[0] <= pred_x <= ci_x[2])
    exact_half_supported = bool(ci_x[0] <= 0.5 <= ci_x[2])
    identifiability_pass = bool(valid_fraction >= 0.80)
    lr = float(max(0.0, 2.0 * (fixed["nll"] - fit["nll"])))
    direction_pass = bool(np.sign(meas_x - 0.5) == np.sign(pred_x - 0.5))
    reconstruction_ok = bool(split["nrmse"] < 0.10)

    # Post-result audit of the conditional-bootstrap boundary.  The native
    # equality does not exist for sufficiently prompt-poor mixtures, so a
    # crossing-conditioned percentile interval cannot by itself exclude 0.5.
    model_p_shape = p_model.sum(axis=(0, 1)) / p_model.sum()
    model_d_shape = d_model.sum(axis=(0, 1)) / d_model.sum()

    def x_for_share(share: float) -> float:
        return handover(times, share * model_p_shape, (1.0 - share) * model_d_shape)[1]

    half_grid = np.linspace(0.001, 0.999, 999)
    half_x = np.asarray([x_for_share(float(s)) for s in half_grid])
    half_ok = np.isfinite(half_x)
    half_share = float(brentq(lambda s: x_for_share(s) - 0.5, half_grid[half_ok][0], half_grid[half_ok][-1]))
    half_fit = fit_fixed(y, templates, half_share)
    liquid_quarter_share = float(brentq(lambda s: x_for_share(s) - 1.25, half_grid[half_ok][0], half_grid[half_ok][-1]))
    liquid_quarter_fit = fit_fixed(y, templates, liquid_quarter_share)
    profile_share, profile_nll = profile_prompt_share(y, templates)
    profile_delta = profile_nll - np.min(profile_nll)
    profile_95_mask = profile_delta <= 1.920729410347062  # conventional 1-dof 95% diagnostic
    profile_95 = [float(profile_share[profile_95_mask][0]), float(profile_share[profile_95_mask][-1])]
    model_profile_delta = float(fixed["nll"] - np.min(profile_nll))
    half_profile_delta = float(half_fit["nll"] - np.min(profile_nll))

    if transfer_pass and identifiability_pass:
        verdict = "ASYMMETRY-SHIFTED HANDOVER TRANSFERS TO ARGON"
    elif not identifiability_pass:
        verdict = "INCONCLUSIVE — ARGON BRANCH MIXTURE NOT IDENTIFIABLE"
    else:
        verdict = "TRANSFER NOT SUPPORTED ON ARGON"

    results = {
        "test": "T373",
        "date": "2026-08-13",
        "evidence_class": "prospective coordinate transfer to previously inspected independent public detector data",
        "frozen_gate_verdict": verdict,
        "scientific_interpretation": "ORIGINAL SAME-COORDINATE TRANSFER INTERPRETATION INVALIDATED; NESTED LIQUID CHILD-TO-PARENT 1.25 LANDMARK IS A POST-RESULT LEAD",
        "source": "COHERENT CENNS-10 liquid-argon public 3D release",
        "released_cube": {
            "shape_energy_f90_time": list(y_cube.shape),
            "observed_events": float(y.sum()),
            "native_time_centers_us": times.tolist(),
        },
        "model_prediction": {
            "prompt_share": model_share,
            "prompt_events_in_released_128_event_template": model_prompt_total,
            "delayed_events_in_released_128_event_template": model_delayed_total,
            "handover_time_us": pred_t,
            "cumulative_ara_at_handover": pred_x,
            "displacement_from_child_half": pred_x - 0.5,
            "signal_template_decomposition_nrmse": split["nrmse"],
        },
        "event_measurement": {
            "fit_success": fit["success"],
            "fit_message": fit["message"],
            "fitted_events": {
                "prompt_cevns": float(n_prompt),
                "delayed_cevns": float(n_delayed),
                "total_cevns": float(n_prompt + n_delayed),
                "prompt_brn": float(n_brn),
                "delayed_brn": float(n_dbrn),
                "steady_state": float(n_ss),
            },
            "prompt_share": measured_share,
            "handover_time_us": meas_t,
            "cumulative_ara_at_handover": meas_x,
            "displacement_from_child_half": meas_x - 0.5,
            "bootstrap_95pct": {
                "prompt_share": [ci_share[0], ci_share[2]],
                "handover_time_us": [ci_t[0], ci_t[2]],
                "cumulative_ara_at_handover": [ci_x[0], ci_x[2]],
                "displacement": [ci_delta[0], ci_delta[2]],
                "total_cevns": [ci_signal[0], ci_signal[2]],
                "valid_replicates": int(len(valid)),
                "total_replicates": N_BOOT,
                "valid_fraction": valid_fraction,
                "optimizer_success_fraction": float(success_count / N_BOOT),
            },
        },
        "fixed_vs_free_mixture": {
            "fixed_model_signal_events": float(fixed["params"][0]),
            "fixed_nll": fixed["nll"],
            "free_nll": fit["nll"],
            "likelihood_ratio_2delta_nll": lr,
            "note": "No naive chi-square p-value is claimed because non-negative branch amplitudes create boundary issues.",
        },
        "post_result_boundary_audit": {
            "reason": "A crossing-conditioned bootstrap truncates mixtures whose prompt branch is already below the delayed branch at the first released bin.",
            "prompt_share_that_places_handover_at_x_0_5": half_share,
            "profile_delta_nll_at_model_prediction": model_profile_delta,
            "profile_delta_nll_at_pure_x_0_5": half_profile_delta,
            "conventional_profile_95pct_prompt_share_diagnostic": profile_95,
            "pure_half_interpretation": "Compatible in the likelihood profile even though absent from the crossing-conditioned bootstrap interval; not an exclusion.",
            "status": "post-result diagnostic; not a replacement for the frozen gate",
        },
        "originator_identity_correction": {
            "status": "material methodology correction after result review",
            "error": "The analysis compared the released source-model child cut with the fitted liquid-detector parent response as though they were the same ARA coordinate and rung.",
            "corrected_working_reading": "The argon record retains the stopped-pion/muon source relation as a child inside a provisionally movement-heavy liquid parent. A cross-rung Phase-A-to-Phase-B projection sends the pure 0.5 child contribution to 0.25 beyond the parent ridge: 1 + 0.25 = 1.25.",
            "candidate_liquid_handover_landmark": 1.25,
            "observed_minus_candidate": meas_x - 1.25,
            "absolute_relative_error_percent": 100.0 * abs(meas_x - 1.25) / 1.25,
            "prompt_share_that_places_handover_at_1_25": liquid_quarter_share,
            "profile_delta_nll_at_1_25": float(liquid_quarter_fit["nll"] - np.min(profile_nll)),
            "evidence_boundary": "The 1.25 reading was identified after viewing the argon result and is not a T373 prediction or confirmation. It requires a newly frozen same-identity test.",
        },
        "gates": {
            "transfer_prediction_inside_event_95pct": transfer_pass,
            "identifiability_valid_bootstrap_at_least_80pct": identifiability_pass,
            "free_mixture_matches_or_improves_fixed": bool(fit["nll"] <= fixed["nll"] + 1e-7),
            "pure_child_half_inside_event_95pct": exact_half_supported,
            "prediction_and_measurement_displacement_same_sign": direction_pass,
            "signal_template_decomposition_nrmse_below_0_10": reconstruction_ok,
            "same_coordinate_transfer_premise_valid_after_originator_review": False,
            "nested_child_parent_relation_retained_after_originator_review": True,
            "post_result_liquid_1_25_landmark_likelihood_compatible": bool(liquid_quarter_fit["nll"] - np.min(profile_nll) < 1.920729410347062),
        },
        "boundaries": [
            "The argon source files were inspected during T371; only this handover score and 3D branch fit were prospectively frozen.",
            "The prediction uses the collaboration's released argon CEvNS signal template and therefore tests transfer/calibration, not a universal ARA correction law.",
            "Prompt CEvNS competes with a large prompt-neutron background; the bootstrap interval is the relevant uncertainty statement.",
            "The native release has only ten 0.5-us bins, so the equality time is linearly interpolated and the cumulative coordinate is integrated inside the containing native bin.",
            "Passing does not identify individual neutrino events or establish particle-by-particle release times.",
        ],
    }
    (HERE / "T373_ARGON_CHILD_HALF_TRANSFER_RESULTS.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    with (HERE / "T373_ARGON_CHILD_HALF_TRANSFER_BOOTSTRAP.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["prompt_share", "handover_time_us", "cumulative_ara_at_handover", "displacement_from_0_5", "total_cevns"])
        w.writerows(valid)

    timeline = np.column_stack([times, p_model.sum(axis=(0, 1)), d_model.sum(axis=(0, 1)), fitted_p_t, fitted_d_t])
    np.savetxt(
        HERE / "T373_ARGON_CHILD_HALF_TRANSFER_TIMELINE.csv", timeline, delimiter=",",
        header="time_us,model_prompt,model_delayed,fitted_prompt,fitted_delayed", comments="",
    )

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=True)
    blue, orange, green, red = "#2f7ed8", "#ed9b33", "#1b9e77", "#c33c54"

    model_p_t = p_model.sum(axis=(0, 1))
    model_d_t = d_model.sum(axis=(0, 1))
    axes[0, 0].step(times, model_p_t / 0.5, where="mid", color=blue, lw=2, label="prompt pion branch")
    axes[0, 0].step(times, model_d_t / 0.5, where="mid", color=orange, lw=2, label="delayed muon branch")
    axes[0, 0].axvline(pred_t, color=red, ls="--", label=f"predicted equality {pred_t:.3f} us")
    axes[0, 0].set(title="Frozen model-side prediction", xlabel="time after beam pulse (us)", ylabel="events per microsecond in released 128-event model")
    axes[0, 0].legend(fontsize=9)

    axes[0, 1].step(times, fitted_p_t / 0.5, where="mid", color=blue, lw=2, label="event-fitted prompt")
    axes[0, 1].step(times, fitted_d_t / 0.5, where="mid", color=orange, lw=2, label="event-fitted delayed")
    axes[0, 1].axvline(meas_t, color=red, ls="--", label=f"measured equality {meas_t:.3f} us")
    axes[0, 1].set(title="Independent event-cube measurement", xlabel="time after beam pulse (us)", ylabel="fitted events per microsecond")
    axes[0, 1].legend(fontsize=9)

    # Display the cumulative coordinates at native bin edges, with handover points.
    edges = np.r_[times[0] - 0.25, times + 0.25]
    model_cum = np.r_[0.0, 2.0 * np.cumsum(model_p_t + model_d_t) / np.sum(model_p_t + model_d_t)]
    fit_cum = np.r_[0.0, 2.0 * np.cumsum(fitted_p_t + fitted_d_t) / np.sum(fitted_p_t + fitted_d_t)]
    axes[1, 0].step(edges, model_cum, where="post", color="#7b3294", lw=2, label="model prediction")
    axes[1, 0].step(edges, fit_cum, where="post", color=green, lw=2, label="event measurement")
    axes[1, 0].axhline(0.5, color="#666666", ls=":", label="pure child-half 0.5")
    axes[1, 0].axhline(1.0, color="black", lw=1.2, label="parent ridge 1.0")
    axes[1, 0].axhline(1.25, color="#b2182b", ls="--", lw=1.5, label="post-result liquid lead 1.25")
    axes[1, 0].scatter([pred_t], [pred_x], facecolor="white", edgecolor="#7b3294", s=90, lw=2, zorder=5)
    axes[1, 0].scatter([meas_t], [meas_x], color=green, s=75, zorder=5)
    axes[1, 0].set(title="ARA release position at branch equality", xlabel="time after beam pulse (us)", ylabel="cumulative ARA release", ylim=(0, 2.03))
    axes[1, 0].legend(fontsize=8)

    axes[1, 1].hist(valid[:, 2], bins=45, color="#89b6e3", edgecolor="white", alpha=0.9, label="event bootstrap")
    axes[1, 1].axvline(pred_x, color="#7b3294", lw=2, label=f"frozen prediction {pred_x:.3f}")
    axes[1, 1].axvline(meas_x, color=green, lw=2, label=f"event estimate {meas_x:.3f}")
    axes[1, 1].axvline(0.5, color="#666666", ls=":", lw=2, label="pure 0.5")
    axes[1, 1].axvline(1.25, color="#b2182b", ls="--", lw=2, label="post-result liquid lead 1.25")
    axes[1, 1].set(title=f"Transfer interval (valid bootstrap {len(valid)}/{N_BOOT})", xlabel="ARA coordinate at handover", ylabel="bootstrap replicates")
    axes[1, 1].legend(fontsize=8)

    fig.suptitle("T373 — liquid-argon identity audit\nSame source child, movement-heavy liquid parent: post-result lead at ridge + 0.25", fontsize=16, fontweight="bold")
    fig.savefig(HERE / "T373_ARGON_CHILD_HALF_TRANSFER_FIGURE.png", dpi=180)
    fig.savefig(HERE / "T373_ARGON_CHILD_HALF_TRANSFER_FIGURE.svg")
    plt.close(fig)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
