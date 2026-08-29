from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys

EXTRA = Path(r"F:\SystemFormulaFolder\.codex_python_packages")
if EXTRA.exists() and str(EXTRA) not in sys.path:
    sys.path.insert(0, str(EXTRA))
os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / "_mplconfig"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "T404_corrected_child_release_diara"
OUT.mkdir(exist_ok=True)

P398 = ROOT / "T398_population_neutrino_wave_overlap"
P400 = ROOT / "T400_nested_child_window_population_to_event"
P402 = ROOT / "T402_whole_shape_child_relation"
P378 = ROOT / "T378_coherent_2017_holdout"
P397 = ROOT / "T397_spin_phase_maturity_vs_orientation"
PROTOCOL = ROOT / "T404_CORRECTED_CHILD_RELEASE_DIARA_PROTOCOL_2026-08-18.md"

SEED = 40420260818
N_BOOT = 5000
BIN_X = np.arange(0.125, 2.0, 0.25)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unit_center(values: np.ndarray) -> np.ndarray:
    z = np.asarray(values, dtype=float) - np.mean(values)
    norm = float(np.linalg.norm(z))
    return z / norm if norm > 0 else np.full_like(z, np.nan)


def centered_maxabs(values: np.ndarray) -> np.ndarray:
    z = np.asarray(values, dtype=float) - np.mean(values)
    scale = float(np.max(np.abs(z)))
    return z / scale if scale > 0 else np.full_like(z, np.nan)


def quadratic_crest(x: np.ndarray, y: np.ndarray) -> float:
    """Fixed binned crest estimator used only for saved split histograms."""
    early = np.where(x <= 1.0)[0]
    idx = int(early[np.argmax(y[early])])
    if idx == 0 or idx == len(x) - 1:
        return float(x[idx])
    xx = x[idx - 1 : idx + 2]
    yy = y[idx - 1 : idx + 2]
    a, b, _ = np.polyfit(xx, yy, 2)
    if not np.isfinite(a) or a >= 0:
        return float(x[idx])
    vertex = float(-b / (2 * a))
    return float(np.clip(vertex, xx[0], xx[-1]))


def ridge_crossing(x: np.ndarray, y: np.ndarray) -> float:
    crossings: list[float] = []
    for i in range(len(x) - 1):
        if y[i] == 0:
            crossings.append(float(x[i]))
        elif y[i] * y[i + 1] < 0:
            crossings.append(
                float(x[i] - y[i] * (x[i + 1] - x[i]) / (y[i + 1] - y[i]))
            )
    return min(crossings, key=lambda value: abs(value - 1.0)) if crossings else float("nan")


def binned_landmarks(y: np.ndarray) -> tuple[float, float]:
    return quadratic_crest(BIN_X, y), ridge_crossing(BIN_X, y)


def rescale_0_2(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    lo = float(np.min(values))
    hi = float(np.max(values))
    return 2.0 * (values - lo) / (hi - lo) if hi > lo else np.ones_like(values)


r400 = json.loads((P400 / "T400_RESULTS.json").read_text(encoding="utf-8"))
r402 = json.loads((P402 / "T402_RESULTS.json").read_text(encoding="utf-8"))
r378 = json.loads((P378 / "T378_results.json").read_text(encoding="utf-8"))

curve400 = pd.read_csv(P400 / "T400_LOCAL_CHILD_CURVE.csv").sort_values("local_child_ara")
native = pd.read_csv(P398 / "T398_NATIVE_WAVE_OVERLAP.csv").sort_values("time_us")
kde = pd.read_csv(P402 / "T402_KDE_TOPOLOGY.csv").sort_values("bandwidth")
bins = pd.read_csv(P402 / "T402_BIN_SUMMARY.csv")
dist = pd.read_csv(P402 / "T402_PRIMARY_BIN_DISTRIBUTIONS.csv")
holdout = pd.read_csv(P398 / "T398_T378_INDEPENDENT_HOLDOUT.csv")

cx = curve400["local_child_ara"].to_numpy(float)
ct = curve400["time_us"].to_numpy(float)
left = float(r400["primary_population"]["left_time_us"])
right = float(r400["primary_population"]["right_time_us"])
tn = native["time_us"].to_numpy(float)

# Rebuild the exact T400 parent coordinate from the saved primary fit and the
# native source templates. T400_LOCAL_CHILD_CURVE is deliberately thinned for
# plotting, so using it alone would add interpolation error at the crest.
n_prompt = float(r400["primary_event_transfer"]["n_prompt"])
n_delayed = float(r400["primary_event_transfer"]["n_delayed"])
prompt_shape = native["prompt_fitted_events_per_native_ns"].to_numpy(float)
delayed_shape = native["delayed_total_fitted_events_per_native_ns"].to_numpy(float)
p_rate = n_prompt * prompt_shape / prompt_shape.sum()
d_rate = n_delayed * delayed_shape / delayed_shape.sum()
parent_x_exact = 2.0 * np.cumsum(p_rate + d_rate) / np.sum(p_rate + d_rate)
x_left = float(r400["primary_population"]["left_parent_ara"])
x_right = float(r400["primary_population"]["right_parent_ara"])
local_x_exact = 2.0 * (parent_x_exact - x_left) / (x_right - x_left)
window_mask = (tn >= left) & (tn <= right)
bin_time_correct = np.interp(BIN_X, local_x_exact[window_mask], tn[window_mask])
bin_time_linear = left + BIN_X * (right - left) / 2.0

source_crest_x = float(r400["primary_population"]["local_crest_ara"])
source_crest_time = float(r400["primary_population"]["delayed_crest_time_us"])
mode_index = int(np.argmin(np.abs(tn - source_crest_time)))
source_crest_reconstructed = float(local_x_exact[mode_index])
linear_source_crest_x = float(2.0 * (source_crest_time - left) / (right - left))

mapping = pd.DataFrame(
    {
        "local_child_ara": BIN_X,
        "correct_time_us": bin_time_correct,
        "t403_linear_time_us": bin_time_linear,
        "time_error_us": bin_time_linear - bin_time_correct,
    }
)


def native_interp(column: str, times: np.ndarray) -> np.ndarray:
    return np.interp(times, tn, native[column].to_numpy(float))


detector = (
    bins[bins["source"] == "C"]
    .sort_values("bin_center")["mean_C_minus_AC"]
    .to_numpy(float)
)
corrected_candidates = {
    "detector C-AC": detector,
    "delayed total release": native_interp(
        "delayed_total_release_peak_normalized", bin_time_correct
    ),
    "nu_e release": native_interp("nu_e_release_over_delayed_peak", bin_time_correct),
    "anti_nu_mu release": native_interp(
        "anti_nu_mu_release_over_delayed_peak", bin_time_correct
    ),
    "remaining muon": native_interp("inferred_muon_remaining_fraction", bin_time_correct),
}

profile_rows: list[dict] = []
for series, values in corrected_candidates.items():
    for xx, tt, value, z in zip(BIN_X, bin_time_correct, values, centered_maxabs(values)):
        profile_rows.append(
            {
                "ara_x": float(xx),
                "time_us": float(tt),
                "series": series,
                "raw_value": float(value),
                "centered_maxabs": float(z),
                "evidence_class": (
                    "measured detector diagnostic"
                    if series == "detector C-AC"
                    else "fitted or derived source relation"
                ),
            }
        )

score_rows: list[dict] = []
for series, values in corrected_candidates.items():
    if series == "detector C-AC":
        continue
    for orientation, oriented in (("direct", values), ("reversed", values[::-1])):
        score_rows.append(
            {
                "candidate": series,
                "orientation": orientation,
                "cosine": float(np.dot(unit_center(detector), unit_center(oriented))),
            }
        )

landmark_rows: list[dict] = []
for row in kde.itertuples(index=False):
    detector_crest = float(row.positive_crest_x)
    ridge = float(row.crossing_nearest_ridge_x)
    landmark_rows.append(
        {
            "bandwidth": float(row.bandwidth),
            "detector_crest_x": detector_crest,
            "source_release_crest_x": source_crest_x,
            "detector_ridge_x": ridge,
            "ordered_three_stage": bool(detector_crest < source_crest_x < ridge),
            "detector_to_ridge_ratio": ridge / detector_crest,
            "source_to_ridge_ratio": ridge / source_crest_x,
            "detector_octave_residual": ridge - 2.0 * detector_crest,
            "source_octave_residual": ridge - 2.0 * source_crest_x,
        }
    )
landmarks = pd.DataFrame(landmark_rows)

# Saved split histograms are overlapping deterministic robustness probes. The
# bootstrap resamples split identities, not raw independent events.
pivot = dist.pivot_table(
    index=["salt", "bin_center"],
    columns="source",
    values="proportion_of_split_weight",
).reset_index()
split_vectors = []
for _, group in pivot.groupby("salt", sort=True):
    group = group.sort_values("bin_center")
    if len(group) == 8 and not group[["C", "AC"]].isna().any().any():
        split_vectors.append((group["C"] - group["AC"]).to_numpy(float))
split_vectors_np = np.vstack(split_vectors)

rng = np.random.default_rng(SEED)
boot_rows: list[dict] = []
shift_better = 0
shift_total = 0
for boot in range(N_BOOT):
    selected = rng.integers(0, len(split_vectors_np), len(split_vectors_np))
    mean_curve = np.mean(split_vectors_np[selected], axis=0)
    crest, ridge = binned_landmarks(mean_curve)
    valid = np.isfinite(crest) and np.isfinite(ridge)
    residual = ridge - 2.0 * crest if valid else float("nan")
    order = bool(valid and crest < source_crest_x < ridge)
    valid_shift_errors: list[float] = []
    for shift in range(1, 8):
        shifted = np.roll(mean_curve, shift)
        shift_crest, shift_ridge = binned_landmarks(shifted)
        if np.isfinite(shift_crest) and np.isfinite(shift_ridge):
            valid_shift_errors.append(abs(shift_ridge - 2.0 * shift_crest))
    if valid and valid_shift_errors:
        shift_better += sum(error <= abs(residual) for error in valid_shift_errors)
        shift_total += len(valid_shift_errors)
    boot_rows.append(
        {
            "bootstrap": boot,
            "detector_crest_x": crest,
            "detector_ridge_x": ridge,
            "detector_octave_residual": residual,
            "ordered_three_stage": order,
            "valid": valid,
        }
    )
bootstrap = pd.DataFrame(boot_rows)
valid_boot = bootstrap[bootstrap["valid"]].copy()

# Candidate storage-flow Di-ARA on the actual T400 curve, not the eight-bin
# detector approximation.
times = tn[window_mask]
local_x = local_x_exact[window_mask]
remaining = native_interp("inferred_muon_remaining_fraction", times)
release = native_interp("delayed_total_release_peak_normalized", times)
storage_ara = rescale_0_2(remaining)
flow_ara = rescale_0_2(release)
mean_detector_crest = float(landmarks["detector_crest_x"].mean())
mean_ridge = float(landmarks["detector_ridge_x"].mean())


def stage(xx: float) -> str:
    if xx < mean_detector_crest:
        return "pre-turn storage"
    if xx < source_crest_x:
        return "turn to release"
    if xx < mean_ridge:
        return "release to handover"
    return "post-handover"


diara = pd.DataFrame(
    {
        "local_child_ara": local_x,
        "time_us": times,
        "storage_ara": storage_ara,
        "release_flow_ara": flow_ara,
        "remaining_muon_fraction": remaining,
        "delayed_release_rate": release,
        "stage": [stage(xx) for xx in local_x],
        "quadrant": [
            ("storage-high" if s >= 1 else "storage-low")
            + " / "
            + ("flow-high" if f >= 1 else "flow-low")
            for s, f in zip(storage_ara, flow_ara)
        ],
    }
)

quadrants = (
    diara.groupby("quadrant", as_index=False)
    .agg(samples=("local_child_ara", "size"), x_min=("local_child_ara", "min"), x_max=("local_child_ara", "max"))
)
quadrants["fraction"] = quadrants["samples"] / len(diara)

# Coarse independent chronology only.
prompt_time = float(holdout.loc[holdout["fitted_prompt_nu_mu"].idxmax(), "time_us"])
delayed_time = float(
    holdout.loc[holdout["fitted_delayed_nu_e_plus_anti_nu_mu"].idxmax(), "time_us"]
)

boot_interval = valid_boot["detector_octave_residual"].quantile([0.025, 0.975]).tolist()
bootstrap_order_fraction = float(valid_boot["ordered_three_stage"].mean())
circular_p = float((1 + shift_better) / (1 + shift_total)) if shift_total else float("nan")

gates = {
    "G1_correct_inverse_map_reproduces_T400_crest": bool(
        np.isclose(source_crest_reconstructed, source_crest_x, atol=1e-12)
    ),
    "G2_three_stage_all_registered_bandwidths": bool(landmarks["ordered_three_stage"].all()),
    "G3_three_stage_bootstrap_at_least_90pct": bool(bootstrap_order_fraction >= 0.90),
    "G4_exact_detector_octave": bool(
        boot_interval[0] <= 0 <= boot_interval[1] and circular_p <= 0.05
    ),
    "G5_exact_source_octave_across_bandwidths": bool(
        landmarks["source_octave_residual"].min() <= 0 <= landmarks["source_octave_residual"].max()
    ),
    "G6_independent_prompt_before_delayed_chronology": bool(prompt_time < delayed_time),
    "G7_individual_spinning_muon_event_link_available": False,
}

if gates["G2_three_stage_all_registered_bandwidths"] and gates["G3_three_stage_bootstrap_at_least_90pct"]:
    verdict = "THREE-STAGE HANDOVER SUPPORTED DESCRIPTIVELY"
else:
    verdict = "THREE-STAGE HANDOVER NOT ROBUST"
verdict += (
    "; DETECTOR-TURN OCTAVE BOOTSTRAP-COMPATIBLE BUT POINT ESTIMATES SHORT"
    if gates["G4_exact_detector_octave"]
    else "; DETECTOR-TURN OCTAVE NOT SUPPORTED"
)
verdict += (
    "; SOURCE-RELEASE OCTAVE SUPPORTED"
    if gates["G5_exact_source_octave_across_bandwidths"]
    else "; SOURCE-RELEASE OCTAVE REJECTED"
)

results = {
    "test": "T404 corrected child-release and Di-ARA audit",
    "date": "2026-08-18",
    "protocol_sha256": sha256(PROTOCOL),
    "verdict": verdict,
    "coordinate_audit": {
        "saved_T400_local_crest": source_crest_x,
        "corrected_reconstructed_local_crest": source_crest_reconstructed,
        "T403_linear_map_apparent_local_crest": linear_source_crest_x,
        "T403_apparent_displacement": linear_source_crest_x - source_crest_x,
        "maximum_eight_bin_time_error_us": float(np.max(np.abs(bin_time_linear - bin_time_correct))),
    },
    "registered_bandwidth_summary": {
        "detector_crest_range": landmarks["detector_crest_x"].agg(["min", "max"]).tolist(),
        "source_release_crest": source_crest_x,
        "detector_ridge_range": landmarks["detector_ridge_x"].agg(["min", "max"]).tolist(),
        "detector_to_ridge_ratio_range": landmarks["detector_to_ridge_ratio"].agg(["min", "max"]).tolist(),
        "source_to_ridge_ratio_range": landmarks["source_to_ridge_ratio"].agg(["min", "max"]).tolist(),
        "detector_octave_residual_range": landmarks["detector_octave_residual"].agg(["min", "max"]).tolist(),
        "source_octave_residual_range": landmarks["source_octave_residual"].agg(["min", "max"]).tolist(),
    },
    "bootstrap": {
        "seed": SEED,
        "draws": N_BOOT,
        "valid_draws": int(len(valid_boot)),
        "three_stage_fraction": bootstrap_order_fraction,
        "detector_octave_residual_median": float(valid_boot["detector_octave_residual"].median()),
        "detector_octave_residual_95_interval": boot_interval,
        "circular_shift_errors_as_good_fraction": float(shift_better / shift_total) if shift_total else None,
        "circular_shift_p_add_one": circular_p,
        "warning": "Saved splits overlap; this is robustness, not an independent sampling interval.",
    },
    "diara": {
        "axes": "remaining-parent storage versus delayed-child release flow",
        "normalization": "Each fitted/derived within-window axis mapped separately to 0-2 for geometry display.",
        "mean_detector_turn": mean_detector_crest,
        "child_release_maximum": source_crest_x,
        "mean_detector_handover": mean_ridge,
        "dependency_boundary": "Storage is the cumulative complement of the same delayed template whose rate defines flow; the phase portrait is descriptive, not independent confirmation.",
    },
    "independent_holdout": {
        "archive": "T378 COHERENT 2017 coarse timing",
        "prompt_crest_time_us": prompt_time,
        "delayed_crest_time_us": delayed_time,
        "supports_only": "broad prompt-before-delayed chronology",
    },
    "individual_spin_audit": {
        "T397_identity": "aggregate muSR asymmetry/phase profiles in RAL Silver",
        "event_linked": False,
        "can_test": "population spin-phase geometry",
        "cannot_test": "one named spinning muon producing a charged daughter and two neutrinos",
        "required_data": [
            "event-linked muon spin or polarization",
            "individual decay time",
            "charged-daughter direction and energy",
            "neutral-sensitive timing or independently reconstructed missing momentum",
        ],
    },
    "gates": gates,
    "evidence_boundaries": [
        "T402 detector C-minus-AC is measured but is not a pristine neutrino waveform.",
        "T398/T400 source curves are fitted or derived from the same archive.",
        "T402 saved splits overlap and are not independent experiments.",
        "T378 is too coarse to reproduce the nested local coordinate.",
        "No input is an event-linked individual muon-neutrino record.",
    ],
}

mapping.to_csv(OUT / "T404_COORDINATE_MAPPING.csv", index=False)
pd.DataFrame(profile_rows).to_csv(OUT / "T404_CORRECTED_PROFILES.csv", index=False)
pd.DataFrame(score_rows).to_csv(OUT / "T404_CORRECTED_COMPONENT_SCORES.csv", index=False)
landmarks.to_csv(OUT / "T404_REGISTERED_LANDMARKS.csv", index=False)
bootstrap.to_csv(OUT / "T404_BOOTSTRAP.csv", index=False)
diara.to_csv(OUT / "T404_STORAGE_FLOW_DIARA.csv", index=False)
quadrants.to_csv(OUT / "T404_DIARA_QUADRANTS.csv", index=False)
(OUT / "T404_RESULTS.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

# Static QA companion. The portable HTML report is built separately.
fig, axes = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=True)
axes[0, 0].plot(cx, ct, color="#2563eb", linewidth=2.4, label="correct T400 inverse")
axes[0, 0].plot([0, 2], [left, right], color="#f59e0b", linestyle="--", linewidth=2, label="T403 linear assumption")
axes[0, 0].axvline(source_crest_x, color="#16a34a", linestyle=":", label=f"release crest {source_crest_x:.3f}")
axes[0, 0].set(title="Coordinate audit", xlabel="local child ARA", ylabel="source time (us)")
axes[0, 0].legend(frameon=False)

for row in landmarks.itertuples(index=False):
    axes[0, 1].plot(
        [row.detector_crest_x, row.source_release_crest_x, row.detector_ridge_x],
        [row.bandwidth] * 3,
        marker="o",
        linewidth=1.5,
        label=f"h={row.bandwidth:.2f}",
    )
axes[0, 1].axvline(1, color="black", linestyle="--", linewidth=1)
axes[0, 1].set(title="Three registered landmarks", xlabel="local child ARA", ylabel="KDE bandwidth")

for name, group in diara.groupby("stage", sort=False):
    axes[1, 0].plot(group["storage_ara"], group["release_flow_ara"], marker=".", label=name)
axes[1, 0].axvline(1, color="grey", linewidth=1)
axes[1, 0].axhline(1, color="grey", linewidth=1)
axes[1, 0].set(title="Candidate storage-flow Di-ARA", xlabel="remaining-parent storage (0-2)", ylabel="child release flow (0-2)")
axes[1, 0].legend(frameon=False, fontsize=8)

axes[1, 1].hist(valid_boot["detector_octave_residual"], bins=45, color="#4f86c6", alpha=0.85)
axes[1, 1].axvline(0, color="black", linestyle="--", label="exact octave")
axes[1, 1].set(title="Saved-split octave residual", xlabel="ridge - 2 x detector crest", ylabel="bootstrap count")
axes[1, 1].legend(frameon=False)

fig.suptitle("T404 corrected child-release and Di-ARA audit", fontsize=16, fontweight="bold")
fig.savefig(OUT / "T404_CORRECTED_CHILD_RELEASE_DIARA.png", dpi=180)
plt.close(fig)

print(json.dumps(results, indent=2))
