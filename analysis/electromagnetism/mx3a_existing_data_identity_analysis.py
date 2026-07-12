"""MX3a development-only identity-closure analysis on the existing OSIRIS archive.

This cannot test particle-count/noise convergence because only one PIC
realisation is available. It tests whether the proposed closure index carries
structure beyond field amplitude inside this already-inspected dataset.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "_data_cache" / "ara_em1"
OUT = Path(__file__).resolve().parent
FIELD_SHA256 = "0b368655fe61b33a3193d7d01180623d4f1df4be068b68fb4d453cd8e6d62907"
PHASE_SHA256 = "1cef8ab44720f60ab6559d04333fa60e8a9415963ff26356a177128181b8770f"


class RestrictedNumpyUnpickler(pickle.Unpickler):
    def find_class(self, module: str, name: str):
        allowed = {
            ("numpy.core.multiarray", "_reconstruct"): np._core.multiarray._reconstruct,
            ("numpy.core.multiarray", "scalar"): np._core.multiarray.scalar,
            ("numpy", "ndarray"): np.ndarray,
            ("numpy", "dtype"): np.dtype,
            ("numpy.core.numeric", "_frombuffer"): np._core.numeric._frombuffer,
        }
        if (module, name) not in allowed:
            raise pickle.UnpicklingError(f"Blocked {module}.{name}")
        return allowed[(module, name)]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def safe_load(path: Path):
    with path.open("rb") as handle:
        return RestrictedNumpyUnpickler(handle).load()


def correlation(a, b) -> float:
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    good = np.isfinite(a) & np.isfinite(b)
    if good.sum() < 3 or np.std(a[good]) == 0 or np.std(b[good]) == 0:
        return float("nan")
    return float(np.corrcoef(a[good], b[good])[0, 1])


def regression_metrics(actual, predicted) -> dict:
    actual = np.asarray(actual, float)
    predicted = np.asarray(predicted, float)
    error = predicted - actual
    denom = np.sum((actual - np.mean(actual)) ** 2)
    return {
        "n": int(len(actual)),
        "correlation": correlation(actual, predicted),
        "mae": float(np.mean(np.abs(error))),
        "nrmse": float(np.sqrt(np.mean(error**2)) / np.std(actual)),
        "r2": float(1 - np.sum(error**2) / denom) if denom > 0 else None,
    }


def fit_predict(train_x, train_y, test_x):
    mean = np.mean(train_x, axis=0)
    scale = np.std(train_x, axis=0)
    scale[scale == 0] = 1
    a = np.column_stack([np.ones(len(train_x)), (train_x - mean) / scale])
    b = np.column_stack([np.ones(len(test_x)), (test_x - mean) / scale])
    beta = np.linalg.lstsq(a, train_y, rcond=None)[0]
    return b @ beta, beta


def downsample_mean(array: np.ndarray, factor: int = 4) -> np.ndarray:
    nu, nx = array.shape
    return array.reshape(nu // factor, factor, nx // factor, factor).mean(axis=(1, 3))


def mutual_information(distribution: np.ndarray) -> tuple[float, float]:
    p = np.maximum(distribution, 0.0)
    total = np.sum(p)
    if total <= 0:
        return float("nan"), float("nan")
    p = p / total
    pu = np.sum(p, axis=1, keepdims=True)
    px = np.sum(p, axis=0, keepdims=True)
    expected = pu @ px
    good = (p > 0) & (expected > 0)
    mi = float(np.sum(p[good] * np.log(p[good] / expected[good])))
    hu = float(-np.sum(pu[pu > 0] * np.log(pu[pu > 0])))
    hx = float(-np.sum(px[px > 0] * np.log(px[px > 0])))
    return mi, mi / min(hu, hx) if min(hu, hx) > 0 else float("nan")


def phase_space_metrics(distribution: np.ndarray, k0: int) -> tuple[float, float, float]:
    fluct = distribution - np.mean(distribution, axis=1, keepdims=True)
    coeff = np.fft.rfft(fluct, axis=1)
    mode = coeff[:, k0]
    phase_coherence = float(np.abs(np.sum(mode)) / np.sum(np.abs(mode))) if np.sum(np.abs(mode)) > 0 else 0.0
    spatial_power = np.sum(np.abs(coeff[:, 1:]) ** 2)
    mode_fraction = float(np.sum(np.abs(mode) ** 2) / spatial_power) if spatial_power > 0 else 0.0
    reduced = downsample_mean(fluct, 4)
    singular = np.linalg.svd(reduced, compute_uv=False)
    rank2_fraction = float(np.sum(singular[:2] ** 2) / np.sum(singular**2)) if np.sum(singular**2) > 0 else 0.0
    return phase_coherence, mode_fraction, rank2_fraction


def residual_correlation(target, candidate, controls) -> float:
    controls = np.asarray(controls, float)
    design = np.column_stack([np.ones(len(controls)), controls])
    target_res = target - design @ np.linalg.lstsq(design, target, rcond=None)[0]
    candidate_res = candidate - design @ np.linalg.lstsq(design, candidate, rcond=None)[0]
    return correlation(target_res, candidate_res)


def main() -> None:
    field_path = DATA / "fld_data.pkl"
    phase_path = DATA / "phase_space_data.pkl"
    if sha256(field_path) != FIELD_SHA256 or sha256(phase_path) != PHASE_SHA256:
        raise RuntimeError("Development data hash mismatch")

    field = safe_load(field_path)
    phase = safe_load(phase_path)
    e = np.asarray(field["E"], float)
    f = np.asarray(phase["F"], float)
    u = np.asarray(phase["u"], float)
    v = np.asarray(phase["v"], float)
    t = np.asarray(field["t"], float)
    dx = float(field["dx"])
    du = float(phase["du"])
    ntime, nspace = e.shape
    k0 = 5
    kphys = 2 * np.pi * np.fft.rfftfreq(nspace, d=dx)

    mx1_rows = list(csv.DictReader((OUT / "MX1_DEVELOPMENT_TIMESERIES.csv").open(encoding="utf-8")))
    eligible = np.asarray([row["eligible"] == "1" for row in mx1_rows])
    te_g = np.asarray([float(row["te_ara_rho_g_analogue"]) for row in mx1_rows])
    te_f = np.asarray([float(row["te_ara_rho_f_analogue"]) for row in mx1_rows])
    e_rms = np.asarray([float(row["e_rms"]) for row in mx1_rows])
    fundamental = np.asarray([float(row["fundamental_fraction"]) for row in mx1_rows])
    particle_other = np.asarray([float(row["other_rho_f_fraction"]) for row in mx1_rows])
    gap = te_g - te_f
    closure_raw = 1.0 - np.abs(gap) / 2.0
    # Identity closure is conditional. Before the coherent mode is eligible,
    # two near-zero summaries can agree trivially and imitate high closure.
    closure = np.where(eligible, closure_raw, np.nan)

    ehat = np.fft.rfft(e, axis=1)
    phase_angle = np.unwrap(np.angle(ehat[:, k0]))
    wave_velocity = -np.gradient(phase_angle, t) / kphys[k0]
    wave_velocity = np.clip(wave_velocity, float(v.min()), float(v.max()))

    mi = np.empty(ntime)
    nmi = np.empty(ntime)
    velocity_phase_coherence = np.empty(ntime)
    distribution_mode_fraction = np.empty(ntime)
    rank2_fraction = np.empty(ntime)
    trapped_fraction = np.empty(ntime)
    perturbation_rms = np.empty(ntime)

    for index in range(ntime):
        mi[index], nmi[index] = mutual_information(f[index])
        (
            velocity_phase_coherence[index],
            distribution_mode_fraction[index],
            rank2_fraction[index],
        ) = phase_space_metrics(f[index], k0)
        perturbation = f[index] - np.mean(f[index], axis=1, keepdims=True)
        perturbation_rms[index] = float(np.sqrt(np.mean(perturbation**2)))

        potential_hat = np.zeros_like(ehat[index])
        potential_hat[k0] = 1j * ehat[index, k0] / kphys[k0]
        potential = np.fft.irfft(potential_hat, n=nspace)
        well_depth = np.maximum(potential - np.min(potential), 0.0)
        kinetic_wave = 0.5 * (v[:, None] - wave_velocity[index]) ** 2
        trapped = kinetic_wave <= well_depth[None, :]
        positive_f = np.maximum(f[index], 0.0)
        trapped_fraction[index] = float(np.sum(positive_f * trapped) / np.sum(positive_f))

    selected = np.flatnonzero(eligible)
    controls = np.column_stack([e_rms[selected], fundamental[selected]])
    correlations = {
        "closure_vs_e_rms": correlation(closure[selected], e_rms[selected]),
        "closure_vs_particle_other": correlation(closure[selected], particle_other[selected]),
        "closure_vs_mutual_information": correlation(closure[selected], nmi[selected]),
        "closure_vs_velocity_phase_coherence": correlation(closure[selected], velocity_phase_coherence[selected]),
        "closure_vs_distribution_mode_fraction": correlation(closure[selected], distribution_mode_fraction[selected]),
        "closure_vs_rank2_fraction": correlation(closure[selected], rank2_fraction[selected]),
        "closure_vs_trapped_fraction": correlation(closure[selected], trapped_fraction[selected]),
        "closure_vs_perturbation_rms": correlation(closure[selected], perturbation_rms[selected]),
        "partial_closure_vs_mutual_information_given_amplitude_mode": residual_correlation(
            nmi[selected], closure[selected], controls
        ),
        "partial_closure_vs_trapped_fraction_given_amplitude_mode": residual_correlation(
            trapped_fraction[selected], closure[selected], controls
        ),
        "partial_closure_vs_rank2_given_amplitude_mode": residual_correlation(
            rank2_fraction[selected], closure[selected], controls
        ),
    }

    split = int(0.7 * len(selected))
    train = selected[:split]
    test = selected[split:]
    baseline_train = np.column_stack([e_rms[train], fundamental[train]])
    baseline_test = np.column_stack([e_rms[test], fundamental[test]])
    added_train = np.column_stack([e_rms[train], fundamental[train], closure[train]])
    added_test = np.column_stack([e_rms[test], fundamental[test], closure[test]])
    held_late = {}
    for target_name, target in {
        "normalised_mutual_information": nmi,
        "trapped_fraction": trapped_fraction,
        "rank2_fraction": rank2_fraction,
    }.items():
        pred_base, _ = fit_predict(baseline_train, target[train], baseline_test)
        pred_added, _ = fit_predict(added_train, target[train], added_test)
        held_late[target_name] = {
            "baseline": regression_metrics(target[test], pred_base),
            "plus_closure": regression_metrics(target[test], pred_added),
        }

    peak = selected[np.argmax(e_rms[selected])]
    rising = selected[selected < peak]
    falling = selected[selected > peak]
    pairs = []
    for post in falling:
        pre = rising[np.argmin(np.abs(e_rms[rising] - e_rms[post]))]
        rel = abs(e_rms[pre] - e_rms[post]) / e_rms[post]
        if rel <= 0.01:
            pairs.append((int(pre), int(post), float(rel)))
    matched = {
        "n_pairs": len(pairs),
        "mean_post_minus_pre_closure": float(np.mean([closure[j] - closure[i] for i, j, _ in pairs])) if pairs else None,
        "mean_post_minus_pre_nmi": float(np.mean([nmi[j] - nmi[i] for i, j, _ in pairs])) if pairs else None,
        "mean_post_minus_pre_trapped_fraction": float(
            np.mean([trapped_fraction[j] - trapped_fraction[i] for i, j, _ in pairs])
        ) if pairs else None,
        "mean_amplitude_relative_mismatch": float(np.mean([r for _, _, r in pairs])) if pairs else None,
    }

    snapshot_indices = [0, int(selected[0]), int(peak), ntime - 1]
    snapshots = []
    for index in snapshot_indices:
        perturbation = f[index] - np.mean(f[index], axis=1, keepdims=True)
        reduced = downsample_mean(perturbation, 4)
        scale = float(np.max(np.abs(reduced)))
        normalised = reduced / scale if scale > 0 else reduced
        snapshots.append({
            "index": index,
            "time": float(t[index]),
            "closure": float(closure[index]) if eligible[index] else None,
            "raw_closure": float(closure_raw[index]),
            "eligible": bool(eligible[index]),
            "nmi": float(nmi[index]),
            "trapped_fraction": float(trapped_fraction[index]),
            "wave_velocity": float(wave_velocity[index]),
            "scale": scale,
            "values": np.round(normalised, 4).tolist(),
        })

    result = {
        "claim_id": "MX3a",
        "tier": "DEVELOPMENT / EXISTING SINGLE-NOISE REALISATION / NOT CONFIRMATORY",
        "noise_convergence_tested": False,
        "data_hashes": {"field": FIELD_SHA256, "phase_space": PHASE_SHA256},
        "definition": "C_id = 1 - abs(TE_rho_G - TE_rho_F)/2, defined only after identity eligibility",
        "eligible_n": int(len(selected)),
        "correlations": correlations,
        "held_late_models": held_late,
        "matched_amplitude": matched,
        "snapshot_indices": snapshot_indices,
        "series": {
            "time": np.round(t, 6).tolist(),
            "eligible": eligible.astype(int).tolist(),
            "closure_raw": np.round(closure_raw, 8).tolist(),
            "closure": [
                round(float(value), 8) if np.isfinite(value) else None
                for value in closure
            ],
            "e_rms": np.round(e_rms, 8).tolist(),
            "nmi": np.round(nmi, 8).tolist(),
            "velocity_phase_coherence": np.round(velocity_phase_coherence, 8).tolist(),
            "distribution_mode_fraction": np.round(distribution_mode_fraction, 8).tolist(),
            "rank2_fraction": np.round(rank2_fraction, 8).tolist(),
            "trapped_fraction": np.round(trapped_fraction, 8).tolist(),
            "particle_other": np.round(particle_other, 8).tolist(),
        },
        "snapshots": snapshots,
    }
    (OUT / "MX3A_EXISTING_DATA_RESULTS.json").write_text(
        json.dumps(result, indent=2, allow_nan=False), encoding="utf-8"
    )

    with (OUT / "MX3A_EXISTING_DATA_TIMESERIES.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "time", "eligible", "closure", "closure_raw", "e_rms", "nmi", "velocity_phase_coherence",
            "distribution_mode_fraction", "rank2_fraction", "trapped_fraction",
            "particle_other", "wave_velocity",
        ])
        for index in range(ntime):
            writer.writerow([
                t[index], int(eligible[index]), closure[index], closure_raw[index], e_rms[index], nmi[index],
                velocity_phase_coherence[index], distribution_mode_fraction[index],
                rank2_fraction[index], trapped_fraction[index], particle_other[index],
                wave_velocity[index],
            ])

    report = f"""# MX3a existing-data identity-formation result

**Tier:** DEVELOPMENT / SINGLE NOISE LEVEL / NOT CONFIRMATORY  
**Noise convergence tested:** No  
**Eligible slices:** {len(selected)}

## Outcome

The existing archive can test whether the proposed closure index co-moves with independently calculated phase-space
organisation, but it cannot distinguish physical closure from the single simulation's finite-particle noise.

The closure index is defined only after the predeclared coherent-mode eligibility gate. Before that gate, a high raw
agreement can arise trivially because both summaries are near zero; it is not evidence that an identity already exists.

On eligible slices:

- closure vs field RMS: {correlations['closure_vs_e_rms']:.4f};
- closure vs particle Other: {correlations['closure_vs_particle_other']:.4f};
- closure vs normalised position–momentum mutual information: {correlations['closure_vs_mutual_information']:.4f};
- closure vs velocity-bin phase coherence: {correlations['closure_vs_velocity_phase_coherence']:.4f};
- closure vs phase-space rank-2 fraction: {correlations['closure_vs_rank2_fraction']:.4f};
- closure vs approximate fundamental-wave trapped fraction: {correlations['closure_vs_trapped_fraction']:.4f}.

After linearly controlling field RMS and fundamental-mode fraction:

- residual closure–mutual-information correlation:
  {correlations['partial_closure_vs_mutual_information_given_amplitude_mode']:.4f};
- residual closure–trapped-fraction correlation:
  {correlations['partial_closure_vs_trapped_fraction_given_amplitude_mode']:.4f};
- residual closure–rank-2 correlation:
  {correlations['partial_closure_vs_rank2_given_amplitude_mode']:.4f}.

Matched-amplitude rising-versus-post-peak pairs (within 1% field RMS): {matched['n_pairs']}.
Mean post-minus-pre closure: {matched['mean_post_minus_pre_closure'] if matched['mean_post_minus_pre_closure'] is not None else 'undefined'}.
Mean post-minus-pre mutual information: {matched['mean_post_minus_pre_nmi'] if matched['mean_post_minus_pre_nmi'] is not None else 'undefined'}.
Mean post-minus-pre trapped fraction: {matched['mean_post_minus_pre_trapped_fraction'] if matched['mean_post_minus_pre_trapped_fraction'] is not None else 'undefined'}.

The matched-amplitude result is the main narrowing: closure does not separate rising from post-peak structural history
when field amplitude is nearly fixed, although the approximate trapped fraction increases. The large negative partial
trapping correlation is not treated as a physical inverse law because late-time collinearity and the approximate
single-wave separatrix can reverse a residual relation.

## Held-late development comparison

The baseline uses field RMS plus fundamental-mode fraction. The added model includes the closure index. Both are fitted
on the first 70% of eligible development slices and scored on the same final 30%; this remains calibration evidence.

| Target | Baseline R² | + closure R² | Change |
|---|---:|---:|---:|
| position–momentum mutual information | {held_late['normalised_mutual_information']['baseline']['r2']:.4f} | {held_late['normalised_mutual_information']['plus_closure']['r2']:.4f} | {(held_late['normalised_mutual_information']['plus_closure']['r2']-held_late['normalised_mutual_information']['baseline']['r2']):.4f} |
| approximate trapped fraction | {held_late['trapped_fraction']['baseline']['r2']:.4f} | {held_late['trapped_fraction']['plus_closure']['r2']:.4f} | {(held_late['trapped_fraction']['plus_closure']['r2']-held_late['trapped_fraction']['baseline']['r2']):.4f} |
| phase-space rank-2 fraction | {held_late['rank2_fraction']['baseline']['r2']:.4f} | {held_late['rank2_fraction']['plus_closure']['r2']:.4f} | {(held_late['rank2_fraction']['plus_closure']['r2']-held_late['rank2_fraction']['baseline']['r2']):.4f} |

## Fences

- The trapping fraction is an approximate fundamental-wave separatrix diagnostic, not particle-orbit tracking.
- Mutual information and SVD rank are generic structure measures, not uniquely plasma trapping.
- All 459 times and this archive have now been inspected; no result here is prospective.
- The missing particle-count/seed axis remains the decisive MX3 test.

## Verdict

`VISUAL ORGANISATION CONFIRMED / CLOSURE CO-MOVES / MATCHED-AMPLITUDE IDENTITY SEPARATION NULL / NOISE CONVERGENCE OPEN`
"""
    (OUT / "MX3A_EXISTING_DATA_REPORT.md").write_text(report, encoding="utf-8")

    fig, axes = plt.subplots(2, 2, figsize=(13, 9.5), constrained_layout=True)
    for ax, snap in zip(axes.flat, snapshots):
        values = np.asarray(snap["values"])
        image = ax.imshow(
            values,
            origin="lower",
            aspect="auto",
            extent=[float(field["x"][0]), float(field["x"][-1]), float(u[0]), float(u[-1])],
            cmap="RdBu_r",
            vmin=-1,
            vmax=1,
        )
        closure_label = f"{snap['closure']:.3f}" if snap["closure"] is not None else "undefined"
        ax.set_title(
            f"t={snap['time']:.2f}  Cid={closure_label}  "
            f"NMI={snap['nmi']:.4f}  trapped≈{snap['trapped_fraction']:.3f}"
        )
        ax.set_xlabel("x")
        ax.set_ylabel("normalised momentum u")
    fig.suptitle("MX3a phase-space perturbation snapshots — existing development data")
    fig.colorbar(
        image,
        ax=axes.ravel().tolist(),
        label="normalised F − spatial mean",
        shrink=0.84,
        pad=0.025,
    )
    fig.savefig(OUT / "MX3A_PHASE_SPACE_IDENTITY.png", dpi=170)
    plt.close(fig)

    print(json.dumps({
        "report": str(OUT / "MX3A_EXISTING_DATA_REPORT.md"),
        "correlations": correlations,
        "matched_amplitude": matched,
        "held_late_r2": {
            key: {
                "baseline": value["baseline"]["r2"],
                "plus_closure": value["plus_closure"]["r2"],
            }
            for key, value in held_late.items()
        },
        "noise_convergence_tested": False,
    }, indent=2))


if __name__ == "__main__":
    main()
