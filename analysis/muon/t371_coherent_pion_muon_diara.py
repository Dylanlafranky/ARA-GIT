"""T371: stopped-pion -> muon two-stage Di-ARA handover on COHERENT CsI data.

The script consumes only the official arXiv:2110.07730v2 ancillary files. It
keeps beam-coincident and anti-coincident events separate, constructs the
released background templates, reconstructs flavor-resolved CEvNS templates,
fits all components jointly, then applies the frozen ARA compression.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import uproot
from scipy.optimize import minimize
from scipy.special import spherical_jn
from scipy.stats import gamma


HERE = Path(__file__).resolve().parent
DATA = Path(r"F:\SystemFormulaFolder\external_data\coherent_csi_2110_07730\anc")
SEED = 371
N_BOOT = 1000
N_PERM = 1000

E_EDGES = np.arange(0.0, 60.0 + 10.0, 10.0)
T_EDGES = np.arange(0.0, 6.0 + 0.5, 0.5)
E_CENTERS = (E_EDGES[:-1] + E_EDGES[1:]) / 2
T_CENTERS = (T_EDGES[:-1] + T_EDGES[1:]) / 2


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def hist2(events: np.ndarray) -> np.ndarray:
    # np.histogram includes the final right edge; the frozen/released region is
    # half-open, PE < 60 and t_rec < 6 us.
    keep = (
        (events[:, 0] >= E_EDGES[0])
        & (events[:, 0] < E_EDGES[-1])
        & (events[:, 1] >= T_EDGES[0])
        & (events[:, 1] < T_EDGES[-1])
    )
    return np.histogram2d(events[keep, 0], events[keep, 1], bins=(E_EDGES, T_EDGES))[0]


def normalize(a: np.ndarray) -> np.ndarray:
    s = float(np.sum(a))
    if not np.isfinite(s) or s <= 0:
        raise ValueError("Template has non-positive normalization")
    return a / s


def energy_efficiency(pe: np.ndarray) -> np.ndarray:
    a, b, c, d = 1.32045, 0.285979, 10.8646, -0.333322
    return np.clip(a / (1.0 + np.exp(-b * (pe - c))) + d, 0.0, 1.0)


def time_efficiency(t_us: np.ndarray) -> np.ndarray:
    return np.where(t_us < 0.52, 1.0, np.exp(-0.0494 * (t_us - 0.52)))


def released_background(name_pe: str, name_t: str) -> np.ndarray:
    pe = np.loadtxt(DATA / name_pe)
    tt = np.loadtxt(DATA / name_t)
    e_weights = np.histogram(pe[:, 0], E_EDGES, weights=pe[:, 1])[0]
    t_weights = np.histogram(
        tt[:, 0], T_EDGES, weights=tt[:, 1] * time_efficiency(tt[:, 0])
    )[0]
    return normalize(np.outer(normalize(e_weights), normalize(t_weights)))


def steady_template(ac_events: np.ndarray) -> np.ndarray:
    # The release declares E_rec and t_rec independent for selected SSB events.
    e = np.histogram(ac_events[:, 0], E_EDGES)[0].astype(float)
    t = np.exp(-0.0494 * T_CENTERS)
    return normalize(np.outer(normalize(e), normalize(t)))


def helm_form_factor(q_mev: np.ndarray, A: float) -> np.ndarray:
    q = q_mev / 197.3269804  # fm^-1
    s = 0.9
    R = 1.2 * A ** (1.0 / 3.0)
    r0 = math.sqrt(max(R * R - 5.0 * s * s, 1e-12))
    z = q * r0
    out = np.ones_like(z)
    nz = np.abs(z) > 1e-12
    out[nz] = 3.0 * spherical_jn(1, z[nz]) / z[nz]
    return out * np.exp(-0.5 * (q * s) ** 2)


def pe_response(t_mev: np.ndarray) -> np.ndarray:
    """Probability for a true nuclear recoil to land in each 10-PE bin."""
    a, b, c, d = 0.0554628, 4.30681, -111.707, 840.384
    eee_kev = 1000.0 * (a * t_mev + b * t_mev**2 + c * t_mev**3 + d * t_mev**4)
    eee_kev = np.maximum(eee_kev, 1e-12)
    shape = 1.0 + 9.56 * eee_kev
    rate = (0.0749 / eee_kev) * shape
    scale = 1.0 / rate

    one_pe_edges = np.arange(0.0, 61.0, 1.0)
    probs = np.diff(gamma.cdf(one_pe_edges[None, :], a=shape[:, None], scale=scale[:, None]), axis=1)
    probs *= energy_efficiency((one_pe_edges[:-1] + one_pe_edges[1:]) / 2)[None, :]
    return probs.reshape(len(t_mev), 6, 10).sum(axis=2)


def recoil_response() -> np.ndarray:
    """Flavor-independent CEvNS response: neutrino energy -> observed PE bin."""
    enu = np.arange(0.5, 600.0, 1.0)
    t_edges = np.linspace(0.0, 0.08, 801)  # MeVnr, 0.1 keV bins
    t = (t_edges[:-1] + t_edges[1:]) / 2
    dt = np.diff(t_edges)
    response_pe = pe_response(t)
    result = np.zeros((len(enu), len(E_CENTERS)))
    sin2 = 0.23857

    for A, Z in ((132.90545196, 55), (126.9044719, 53)):
        N = round(A) - Z
        m = A * 931.49410242
        qw = N - (1.0 - 4.0 * sin2) * Z
        tmax = 2.0 * enu**2 / (m + 2.0 * enu)
        kin = 1.0 - m * t[None, :] / (2.0 * enu[:, None] ** 2)
        valid = t[None, :] <= tmax[:, None]
        q = np.sqrt(2.0 * m * t)
        ff2 = helm_form_factor(q, A) ** 2
        ds = qw**2 * m * np.clip(kin, 0.0, None) * valid * ff2[None, :]
        result += (ds * dt[None, :]) @ response_pe
    return result


def flavor_template(root_file: uproot.ReadOnlyDirectory, key: str, response: np.ndarray, *, do_normalize: bool = True) -> np.ndarray:
    h = root_file[key]
    values = h.values(flow=False)
    t_edges_ns = h.axes[0].edges()
    t_ns = (t_edges_ns[:-1] + t_edges_ns[1:]) / 2
    e_edges = h.axes[1].edges()
    e_mev = (e_edges[:-1] + e_edges[1:]) / 2

    # The released histograms use 1-MeV source bins matching the response grid.
    if values.shape[1] != response.shape[0] or not np.allclose(e_mev, np.arange(0.5, 600.0, 1.0)):
        raise ValueError("Unexpected source-energy schema")
    keep = (t_ns >= 0.0) & (t_ns < 6000.0)
    weighted = values[keep] * time_efficiency(t_ns[keep] / 1000.0)[:, None]
    # 1 ns native timing -> twelve fixed 0.5-us bins.
    flux_te = weighted.reshape(12, 500, values.shape[1]).sum(axis=1)
    pe_t = flux_te @ response
    out = pe_t.T
    return normalize(out) if do_normalize else out


def nll_and_grad(x: np.ndarray, y_c: np.ndarray, y_ac: np.ndarray, templates: list[np.ndarray], active: np.ndarray) -> tuple[float, np.ndarray]:
    full = np.zeros(5)
    full[active] = x
    n_ss, n_brn, n_nin, n_p, n_d = full
    ss, brn, nin, prompt, delayed = templates
    mu_c = n_ss * ss + n_brn * brn + n_nin * nin + n_p * prompt + n_d * delayed
    mu_a = n_ss * ss
    mu_c = np.maximum(mu_c, 1e-12)
    mu_a = np.maximum(mu_a, 1e-12)
    val = float(np.sum(mu_c - y_c * np.log(mu_c)) + np.sum(mu_a - y_ac * np.log(mu_a)))
    val += 0.5 * ((n_brn - 18.4) / 4.6) ** 2 + 0.5 * ((n_nin - 5.6) / 2.0) ** 2

    bases_c = [ss, brn, nin, prompt, delayed]
    grad = np.zeros(5)
    r_c = 1.0 - y_c / mu_c
    r_a = 1.0 - y_ac / mu_a
    grad[0] = np.sum(ss * r_c) + np.sum(ss * r_a)
    for i in range(1, 5):
        grad[i] = np.sum(bases_c[i] * r_c)
    grad[1] += (n_brn - 18.4) / 4.6**2
    grad[2] += (n_nin - 5.6) / 2.0**2
    return val, grad[active]


def fit_model(y_c: np.ndarray, y_ac: np.ndarray, templates: list[np.ndarray], use_prompt: bool = True, use_delayed: bool = True, start: np.ndarray | None = None) -> dict:
    active = np.array([True, True, True, use_prompt, use_delayed])
    default = np.array([1286.0, 18.4, 5.6, 100.0, 200.0])
    x0 = (default if start is None else np.asarray(start))[active]

    def fun(x: np.ndarray) -> float:
        return nll_and_grad(x, y_c, y_ac, templates, active)[0]

    def jac(x: np.ndarray) -> np.ndarray:
        return nll_and_grad(x, y_c, y_ac, templates, active)[1]

    res = minimize(fun, x0, jac=jac, bounds=[(0.0, None)] * len(x0), method="L-BFGS-B", options={"maxiter": 5000, "ftol": 1e-12, "gtol": 1e-8})
    full = np.zeros(5)
    full[active] = res.x
    return {
        "success": bool(res.success),
        "message": str(res.message),
        "nll": float(res.fun),
        "aic": float(2 * active.sum() + 2 * res.fun),
        "params": full,
    }


def branch_crossing(prompt: np.ndarray, delayed: np.ndarray, p: float, d: float) -> float:
    a = p * prompt.sum(axis=0)
    b = d * delayed.sum(axis=0)
    diff = a - b
    for i in range(len(diff) - 1):
        if diff[i] >= 0 and diff[i + 1] < 0:
            frac = diff[i] / (diff[i] - diff[i + 1])
            return float(T_CENTERS[i] + frac * (T_CENTERS[i + 1] - T_CENTERS[i]))
    return float("nan")


def cumulative_crossing(time_weights: np.ndarray, level: float = 1.0) -> float:
    cumulative = 2 * np.cumsum(time_weights) / np.sum(time_weights)
    if cumulative[0] >= level:
        # Interpolate from the left boundary, where cumulative release is zero.
        return float(T_EDGES[0] + (level / cumulative[0]) * (T_CENTERS[0] - T_EDGES[0]))
    for i in range(len(cumulative) - 1):
        if cumulative[i] < level <= cumulative[i + 1]:
            frac = (level - cumulative[i]) / (cumulative[i + 1] - cumulative[i])
            return float(T_CENTERS[i] + frac * (T_CENTERS[i + 1] - T_CENTERS[i]))
    return float("nan")


def main() -> None:
    required = [
        "dataBeamOnC.txt", "dataBeamOnAC.txt", "brnPE.txt", "brnTrec.txt",
        "ninPE.txt", "ninTrec.txt", "snsFlux2D.root", "effCoefficients.txt",
        "scintRespCoefficients.txt", "Paper_CEvNSCsI_FullDataset_SupMaterials.pdf",
    ]
    hashes = {name: sha256(DATA / name) for name in required}
    c_events = np.loadtxt(DATA / "dataBeamOnC.txt")
    ac_events = np.loadtxt(DATA / "dataBeamOnAC.txt")
    y_c = hist2(c_events)
    y_ac = hist2(ac_events)

    ss = steady_template(ac_events[(ac_events[:, 0] < 60) & (ac_events[:, 1] < 12)])
    brn = released_background("brnPE.txt", "brnTrec.txt")
    nin = released_background("ninPE.txt", "ninTrec.txt")
    response = recoil_response()
    root_file = uproot.open(DATA / "snsFlux2D.root")
    prompt_raw = flavor_template(root_file, "convolved_energy_time_of_nu_mu", response, do_normalize=False)
    delayed_mu_raw = flavor_template(root_file, "convolved_energy_time_of_anti_nu_mu", response, do_normalize=False)
    delayed_e_raw = flavor_template(root_file, "convolved_energy_time_of_nu_e", response, do_normalize=False)
    prompt = normalize(prompt_raw)
    delayed = normalize(delayed_mu_raw + delayed_e_raw)
    templates = [ss, brn, nin, prompt, delayed]

    full = fit_model(y_c, y_ac, templates)
    prompt_only = fit_model(y_c, y_ac, templates, use_delayed=False, start=full["params"])
    delayed_only = fit_model(y_c, y_ac, templates, use_prompt=False, start=full["params"])
    params = full["params"]
    n_ss, n_brn, n_nin, n_p, n_d = params

    # Swapped-order control: keep each branch's energy shape but exchange timing.
    p_e, p_t = prompt.sum(axis=1), prompt.sum(axis=0)
    d_e, d_t = delayed.sum(axis=1), delayed.sum(axis=0)
    swapped_templates = [ss, brn, nin, normalize(np.outer(p_e, d_t)), normalize(np.outer(d_e, p_t))]
    swapped = fit_model(y_c, y_ac, swapped_templates, start=params)

    expected_prompt_share = float(prompt_raw.sum() / (prompt_raw.sum() + delayed_mu_raw.sum() + delayed_e_raw.sum()))
    fixed_combined = normalize(prompt_raw + delayed_mu_raw + delayed_e_raw)
    fixed_combined_templates = [ss, brn, nin, fixed_combined, delayed]
    combined_single = fit_model(y_c, y_ac, fixed_combined_templates, use_delayed=False, start=params)

    rng = np.random.default_rng(SEED)
    perm_nll = np.empty(N_PERM)
    for i in range(N_PERM):
        order = rng.permutation(len(T_CENTERS))
        perm_templates = [ss, brn, nin, prompt[:, order], delayed[:, order]]
        perm_nll[i] = fit_model(y_c, y_ac, perm_templates, start=params)["nll"]
    perm_as_good = int(np.sum(perm_nll <= full["nll"] + 1e-9))

    # Parametric bootstrap from the complete registered fit.
    mu_c = n_ss * ss + n_brn * brn + n_nin * nin + n_p * prompt + n_d * delayed
    mu_ac = n_ss * ss
    boot = np.empty((N_BOOT, 5))
    boot_cross = np.empty(N_BOOT)
    for i in range(N_BOOT):
        yc_b = rng.poisson(mu_c)
        ya_b = rng.poisson(mu_ac)
        f = fit_model(yc_b, ya_b, templates, start=params)
        boot[i] = f["params"]
        boot_cross[i] = branch_crossing(prompt, delayed, f["params"][3], f["params"][4])

    ci = np.percentile(boot, [2.5, 50, 97.5], axis=0)
    denom = n_p + n_d
    x_p = 2 * n_p / denom
    x_d = 2 * n_d / denom
    boot_denom = boot[:, 3] + boot[:, 4]
    boot_xp = np.divide(2 * boot[:, 3], boot_denom, out=np.full(N_BOOT, np.nan), where=boot_denom > 0)
    xp_ci = np.nanpercentile(boot_xp, [2.5, 50, 97.5])
    xd_ci = 2 - xp_ci[::-1]

    loo = []
    for axis, count in (("energy", len(E_CENTERS)), ("time", len(T_CENTERS))):
        for j in range(count):
            mask = np.ones_like(y_c, dtype=bool)
            if axis == "energy":
                mask[j, :] = False
            else:
                mask[:, j] = False
            tmp = [z[mask] for z in templates]
            f = fit_model(y_c[mask], y_ac[mask], tmp, start=params)
            loo.append({"axis": axis, "removed_bin": j, "prompt": float(f["params"][3]), "delayed": float(f["params"][4])})

    p_peak = float(T_CENTERS[np.argmax(n_p * prompt.sum(axis=0))])
    d_peak = float(T_CENTERS[np.argmax(n_d * delayed.sum(axis=0))])
    crossing = branch_crossing(prompt, delayed, n_p, n_d)
    release_t = n_p * prompt.sum(axis=0) + n_d * delayed.sum(axis=0)
    cumulative_ridge = cumulative_crossing(release_t)

    gates = {
        "G1_source_and_boundaries": bool(y_c.sum() == 1578 and y_ac.sum() == 1295),
        "G2_both_95pct_above_zero": bool(ci[0, 3] > 0 and ci[0, 4] > 0),
        "G3_aic_at_least_10_vs_each_single": bool(prompt_only["aic"] - full["aic"] >= 10 and delayed_only["aic"] - full["aic"] >= 10),
        "G4_no_more_than_10_permutations_as_good": bool(perm_as_good <= 10),
        "G5_delayed_crest_after_prompt": bool(d_peak > p_peak),
        "G6_leave_one_out_both_positive": bool(all(z["prompt"] > 0 and z["delayed"] > 0 for z in loo)),
    }
    supported = all(gates.values())
    verdict = "TWO-STAGE DI-ARA HANDOVER RECOVERED" if supported else (
        "TWO POPULATIONS WITHOUT ORDERED-HANDOVER SUPPORT" if gates["G2_both_95pct_above_zero"] else "PUBLIC RECORD DOES NOT RESOLVE BOTH HANDOVERS"
    )

    results = {
        "test": "T371",
        "date": "2026-08-13",
        "verdict": verdict,
        "evidence_class": "known-decay recovery/crosswalk on public unbinned data",
        "source": "arXiv:2110.07730v2 ancillary release",
        "hashes_sha256": hashes,
        "analysis_bounds": {"pe": [0, 60], "time_us": [0, 6], "energy_bins": E_EDGES.tolist(), "time_bins_us": T_EDGES.tolist()},
        "event_counts": {"beam_coincident": int(y_c.sum()), "anti_coincident": int(y_ac.sum())},
        "fit": {
            "steady_state": float(n_ss), "brn": float(n_brn), "nin": float(n_nin),
            "prompt_nu_mu": float(n_p), "delayed_nu_e_plus_anti_nu_mu": float(n_d),
            "prompt_ci95": [float(ci[0, 3]), float(ci[2, 3])],
            "delayed_ci95": [float(ci[0, 4]), float(ci[2, 4])],
            "full_nll": full["nll"], "full_aic": full["aic"],
            "delta_aic_vs_prompt_only": float(prompt_only["aic"] - full["aic"]),
            "delta_aic_vs_delayed_only": float(delayed_only["aic"] - full["aic"]),
            "delta_aic_vs_fixed_expected_combined_single": float(combined_single["aic"] - full["aic"]),
            "delta_aic_vs_swapped_order": float(swapped["aic"] - full["aic"]),
        },
        "timing": {"prompt_peak_us": p_peak, "delayed_peak_us": d_peak, "instantaneous_branch_equality_us": crossing, "bootstrap_branch_equality_ci95_us": np.nanpercentile(boot_cross, [2.5, 97.5]).tolist(), "cumulative_release_ridge_us": cumulative_ridge},
        "ara_compression": {"x_prompt": float(x_p), "x_delayed": float(x_d), "x_prompt_ci95": xp_ci[[0, 2]].tolist(), "x_delayed_ci95": xd_ci[[0, 2]].tolist(), "sum_forced_by_definition": float(x_p + x_d), "standard_model_detector_weighted_x_prompt": float(2 * expected_prompt_share), "standard_model_detector_weighted_x_delayed": float(2 * (1 - expected_prompt_share)), "phi_pair_is_not_a_registered_gate": True},
        "permutation": {"n": N_PERM, "as_good_as_chronological": perm_as_good, "p_upper": float((perm_as_good + 1) / (N_PERM + 1)), "nll_percentiles": np.percentile(perm_nll, [2.5, 50, 97.5]).tolist()},
        "leave_one_out": loo,
        "gates": gates,
        "boundaries": [
            "Ensemble populations are not individually linked pion-muon-neutrino events.",
            "The detector does not distinguish nu_e from anti-nu_mu in the delayed branch.",
            "x_prompt+x_delayed=2 is normalization bookkeeping, not evidence.",
            "This recovers a known decay lineage and does not prove universal fractal geometry.",
        ],
    }

    with (HERE / "T371_COHERENT_PION_MUON_DIARA_RESULTS.json").open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    with (HERE / "T371_COHERENT_PION_MUON_DIARA_COMPONENTS.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["time_us", "observed_C", "observed_AC", "steady", "BRN", "NIN", "prompt_nu_mu", "delayed_nu_e_plus_anti_nu_mu"])
        for j, t in enumerate(T_CENTERS):
            w.writerow([t, y_c[:, j].sum(), y_ac[:, j].sum(), n_ss * ss[:, j].sum(), n_brn * brn[:, j].sum(), n_nin * nin[:, j].sum(), n_p * prompt[:, j].sum(), n_d * delayed[:, j].sum()])

    # Reader-facing figure.
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(2, 3, figsize=(17, 10), constrained_layout=True)
    colors = {"p": "#2f7ed8", "d": "#ed9b33", "ss": "#aab2bd", "b": "#8c6bb1", "n": "#5aae61"}

    obs_t, ac_t = y_c.sum(axis=0), y_ac.sum(axis=0)
    ax[0, 0].errorbar(T_CENTERS, obs_t - ac_t, yerr=np.sqrt(obs_t + ac_t), fmt="o", color="black", label="C − AC data")
    ax[0, 0].plot(T_CENTERS, n_p * prompt.sum(axis=0), "-o", color=colors["p"], label="prompt pion release")
    ax[0, 0].plot(T_CENTERS, n_d * delayed.sum(axis=0), "-o", color=colors["d"], label="delayed muon release")
    ax[0, 0].plot(T_CENTERS, n_brn * brn.sum(axis=0), color=colors["b"], label="prompt neutrons")
    ax[0, 0].plot(T_CENTERS, n_nin * nin.sum(axis=0), color=colors["n"], label="neutrino-induced neutrons")
    ax[0, 0].axvline(crossing, color="#d62728", ls="--", label=f"instantaneous equality {crossing:.2f} μs")
    ax[0, 0].set(title="Observed handover in arrival time", xlabel="recoil time (μs)", ylabel="events per 0.5 μs")
    ax[0, 0].legend(fontsize=8)

    obs_e, ac_e = y_c.sum(axis=1), y_ac.sum(axis=1)
    ax[0, 1].errorbar(E_CENTERS, obs_e - ac_e, yerr=np.sqrt(obs_e + ac_e), fmt="o", color="black", label="C − AC data")
    ax[0, 1].step(E_CENTERS, n_p * prompt.sum(axis=1), where="mid", color=colors["p"], label="prompt")
    ax[0, 1].step(E_CENTERS, n_d * delayed.sum(axis=1), where="mid", color=colors["d"], label="delayed")
    ax[0, 1].step(E_CENTERS, n_brn * brn.sum(axis=1), where="mid", color=colors["b"], label="BRN")
    ax[0, 1].step(E_CENTERS, n_nin * nin.sum(axis=1), where="mid", color=colors["n"], label="NIN")
    ax[0, 1].set(title="Energy cut separates look-alike timing tails", xlabel="reconstructed energy (PE)", ylabel="events per 10 PE")
    ax[0, 1].legend(fontsize=8)

    residual = y_c - y_ac
    im = ax[0, 2].imshow(residual, origin="lower", aspect="auto", extent=[0, 6, 0, 60], cmap="coolwarm")
    ax[0, 2].set(title="Raw beam excess before model assignment", xlabel="recoil time (μs)", ylabel="reconstructed energy (PE)")
    fig.colorbar(im, ax=ax[0, 2], label="C − AC counts")

    total_t = release_t
    cumulative = 2 * np.cumsum(total_t) / total_t.sum()
    ax[1, 0].plot(T_CENTERS, cumulative, "-o", color="#1b9e77", lw=2)
    ax[1, 0].axhline(1, color="black", lw=1, label="ARA ridge")
    ax[1, 0].axhline(2, color="black", lw=1, ls=":", label="completed observed release")
    ax[1, 0].axvline(crossing, color="#d62728", ls="--", label="instantaneous branch equality")
    ax[1, 0].axvline(cumulative_ridge, color="#006d2c", ls="-.", label="cumulative release ridge")
    ax[1, 0].set(title="Cumulative observed release on the ARA 0–2 cut", xlabel="recoil time (μs)", ylabel="released coordinate")
    ax[1, 0].set_ylim(0, 2.08)
    ax[1, 0].legend(fontsize=8)

    vals = [x_p, x_d]
    lo = [x_p - xp_ci[0], x_d - xd_ci[0]]
    hi = [xp_ci[2] - x_p, xd_ci[2] - x_d]
    ax[1, 1].bar(["prompt\npion branch", "delayed\nmuon branch"], vals, color=[colors["p"], colors["d"]], yerr=np.array([lo, hi]), capsize=5)
    ax[1, 1].axhline(1, color="black", lw=1, label="equal detected share")
    ax[1, 1].set(title="Post-extraction ARA pair (sum = 2 by definition)", ylabel="ARA coordinate", ylim=(0, 2))
    ax[1, 1].legend(fontsize=8)

    ax[1, 2].hist(2 * (perm_nll - full["nll"]), bins=35, color="#bdbdbd", edgecolor="white", label="time-permuted controls")
    ax[1, 2].axvline(0, color="#d62728", lw=2, label="registered chronology")
    ax[1, 2].axvline(swapped["aic"] - full["aic"], color="#7b3294", ls="--", lw=2, label="swapped branch order")
    ax[1, 2].set(title=f"Chronology control: {perm_as_good}/{N_PERM} as good", xlabel="2ΔNLL relative to chronological fit", ylabel="control count")
    ax[1, 2].legend(fontsize=8)

    fig.suptitle(f"T371 — COHERENT stopped-pion → muon Di-ARA handover\n{verdict}", fontsize=17, fontweight="bold")
    fig.savefig(HERE / "T371_COHERENT_PION_MUON_DIARA_FIGURE.png", dpi=180)
    fig.savefig(HERE / "T371_COHERENT_PION_MUON_DIARA_FIGURE.svg")
    plt.close(fig)

    print(json.dumps({"verdict": verdict, "fit": results["fit"], "timing": results["timing"], "ara": results["ara_compression"], "permutation": results["permutation"], "gates": gates}, indent=2))


if __name__ == "__main__":
    main()
