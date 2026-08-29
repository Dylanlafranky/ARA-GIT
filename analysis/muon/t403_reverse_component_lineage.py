from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "T403_reverse_component_lineage"
OUT.mkdir(exist_ok=True)

P402 = ROOT / "T402_whole_shape_child_relation"
P400 = ROOT / "T400_nested_child_window_population_to_event"
P398 = ROOT / "T398_population_neutrino_wave_overlap"
P397 = ROOT / "T397_spin_phase_maturity_vs_orientation"
PROTOCOL = ROOT / "T403_REVERSE_COMPONENT_LINEAGE_PROTOCOL_2026-08-18.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unit_center(v: np.ndarray) -> np.ndarray:
    z = np.asarray(v, dtype=float) - np.mean(v)
    n = np.linalg.norm(z)
    if not np.isfinite(n) or n <= 0:
        return np.full_like(z, np.nan)
    return z / n


def maxabs_center(v: np.ndarray) -> np.ndarray:
    z = np.asarray(v, dtype=float) - np.mean(v)
    m = np.max(np.abs(z))
    return z / m if np.isfinite(m) and m > 0 else np.full_like(z, np.nan)


def circular_rank(reference: np.ndarray, candidate: np.ndarray) -> tuple[int, list[float]]:
    r = unit_center(reference)
    scores = [float(np.dot(r, unit_center(np.roll(candidate, k)))) for k in range(len(candidate))]
    target = abs(scores[0])
    rank = 1 + sum(abs(s) > target + 1e-12 for s in scores[1:])
    return rank, scores


def sign_transitions(v: np.ndarray) -> int:
    z = unit_center(v)
    signs = np.sign(z)
    # Replace exact zeros by the previous non-zero sign for a stable circular count.
    for i in range(len(signs)):
        if signs[i] == 0:
            signs[i] = signs[i - 1] if i else 1
    return int(sum(signs[i] != signs[(i + 1) % len(signs)] for i in range(len(signs))))


with (P402 / "T402_RESULTS.json").open(encoding="utf-8") as f:
    r402 = json.load(f)
with (P400 / "T400_RESULTS.json").open(encoding="utf-8") as f:
    r400 = json.load(f)
with (P398 / "T398_RESULTS.json").open(encoding="utf-8") as f:
    r398 = json.load(f)
with (P397 / "T397_RESULTS.json").open(encoding="utf-8") as f:
    r397 = json.load(f)

b402 = pd.read_csv(P402 / "T402_BIN_SUMMARY.csv")
c402 = b402[b402["source"] == "C"].sort_values("bin_center").reset_index(drop=True)
x = c402["bin_center"].to_numpy(float)
detector = c402["mean_C_minus_AC"].to_numpy(float)

left = float(r400["primary_population"]["left_time_us"])
right = float(r400["primary_population"]["right_time_us"])
t = left + x * (right - left) / 2.0

native = pd.read_csv(P398 / "T398_NATIVE_WAVE_OVERLAP.csv")
tn = native["time_us"].to_numpy(float)

def interp(column: str) -> np.ndarray:
    return np.interp(t, tn, native[column].to_numpy(float))


total_native = native["delayed_total_release_peak_normalized"].to_numpy(float)
remaining_native = native["inferred_muon_remaining_fraction"].to_numpy(float)
d_total_native = np.gradient(total_native, tn)
dd_remaining_native = np.gradient(np.gradient(remaining_native, tn), tn)
nue_rate = interp("nu_e_release_over_delayed_peak")
anti_rate = interp("anti_nu_mu_release_over_delayed_peak")

candidates = {
    "delayed total release": interp("delayed_total_release_peak_normalized"),
    "nu_e release": nue_rate,
    "anti_nu_mu release": anti_rate,
    "flavor contrast (anti_nu_mu - nu_e)": anti_rate - nue_rate,
    "remaining muon": interp("inferred_muon_remaining_fraction"),
    "released muon": 1.0 - interp("inferred_muon_remaining_fraction"),
    "release gradient": np.interp(t, tn, d_total_native),
    "remaining-muon curvature": np.interp(t, tn, dd_remaining_native),
}

score_rows: list[dict] = []
profile_rows: list[dict] = []
for i, (xx, tt, dd) in enumerate(zip(x, t, detector)):
    profile_rows.append(
        {
            "ara_x": xx,
            "time_us": tt,
            "series": "T402 detector C-AC",
            "raw_value": dd,
            "centered_unit": unit_center(detector)[i],
            "centered_maxabs": maxabs_center(detector)[i],
            "evidence_class": "measured detector source-difference diagnostic",
        }
    )

for name, values in candidates.items():
    for orientation, oriented in (("direct", values), ("reversed", values[::-1])):
        cosine = float(np.dot(unit_center(detector), unit_center(oriented)))
        rank, shifts = circular_rank(detector, oriented)
        score_rows.append(
            {
                "candidate": name,
                "orientation": orientation,
                "cosine": cosine,
                "absolute_cosine": abs(cosine),
                "registered_shift_rank_of_8": rank,
                "best_shift": int(np.argmax(np.abs(shifts))),
                "best_shift_absolute_cosine": float(np.max(np.abs(shifts))),
                "sign_transitions": sign_transitions(oriented),
                "same_archive": True,
            }
        )
    for i, (xx, tt, vv) in enumerate(zip(x, t, values)):
        profile_rows.append(
            {
                "ara_x": xx,
                "time_us": tt,
                "series": name,
                "raw_value": vv,
                "centered_unit": unit_center(values)[i],
                "centered_maxabs": maxabs_center(values)[i],
                "evidence_class": (
                    "fitted source template"
                    if name not in {"remaining muon", "released muon", "release gradient", "remaining-muon curvature"}
                    else "derived from fitted delayed template"
                ),
            }
        )

scores = pd.DataFrame(score_rows).sort_values(
    ["absolute_cosine", "registered_shift_rank_of_8"], ascending=[False, True]
).reset_index(drop=True)
profiles = pd.DataFrame(profile_rows)

# T397 remains a separate phase-space comparison. It is never inserted into the
# COHERENT event lineage or used for the primary gates.
p397 = pd.read_csv(P397 / "T397_PHASE_PROFILES.csv")
t397_rows: list[dict] = []
t397_score_rows: list[dict] = []
for (run, field), group in p397.groupby(["run", "field_g"], sort=True):
    g = group.sort_values("phase_turn").copy()
    phase_bin = np.minimum((g["phase_turn"].to_numpy(float) * 8).astype(int), 7)
    for value_col, label in (
        ("observed_fractional_residual", "observed W residual"),
        ("predicted_fractional_residual", "fitted W phase"),
    ):
        values = np.array(
            [g.loc[phase_bin == j, value_col].mean() for j in range(8)], dtype=float
        )
        for orientation, oriented in (("direct", values), ("reversed", values[::-1])):
            cosine = float(np.dot(unit_center(detector), unit_center(oriented)))
            rank, shifts = circular_rank(detector, oriented)
            t397_score_rows.append(
                {
                    "run": run,
                    "field_g": field,
                    "series": label,
                    "orientation": orientation,
                    "cosine": cosine,
                    "absolute_cosine": abs(cosine),
                    "registered_shift_rank_of_8": rank,
                    "best_shift": int(np.argmax(np.abs(shifts))),
                    "best_shift_absolute_cosine": float(np.max(np.abs(shifts))),
                    "sign_transitions": sign_transitions(oriented),
                    "same_archive": False,
                }
            )
        for j, value in enumerate(values):
            t397_rows.append(
                {
                    "run": run,
                    "field_g": field,
                    "series": label,
                    "ara_x": (j + 0.5) / 4.0,
                    "raw_value": value,
                    "centered_unit": unit_center(values)[j],
                    "centered_maxabs": maxabs_center(values)[j],
                    "evidence_class": "separate RAL Silver experiment",
                }
            )

t397_profiles = pd.DataFrame(t397_rows)
t397_scores = pd.DataFrame(t397_score_rows).sort_values(
    ["absolute_cosine", "registered_shift_rank_of_8"], ascending=[False, True]
).reset_index(drop=True)

# Post-frozen diagnostic: remove the unequal 38.7/61.3 child weights before
# asking whether T402 contains flavor-specific *shape* information. This does
# not alter the registered candidate selection or any gate.
nue_shape = nue_rate / np.trapezoid(nue_rate, t)
anti_shape = anti_rate / np.trapezoid(anti_rate, t)
flavor_shape_contrast = anti_shape - nue_shape
flavor_shape_rows: list[dict] = []
for orientation, oriented in (
    ("direct", flavor_shape_contrast),
    ("reversed", flavor_shape_contrast[::-1]),
):
    cosine = float(np.dot(unit_center(detector), unit_center(oriented)))
    rank, shifts = circular_rank(detector, oriented)
    flavor_shape_rows.append(
        {
            "candidate": "area-normalized flavor-shape contrast (post-frozen)",
            "orientation": orientation,
            "cosine": cosine,
            "absolute_cosine": abs(cosine),
            "registered_shift_rank_of_8": rank,
            "best_shift": int(np.argmax(np.abs(shifts))),
            "best_shift_absolute_cosine": float(np.max(np.abs(shifts))),
            "same_archive": True,
        }
    )
flavor_shape_scores = pd.DataFrame(flavor_shape_rows)
flavor_rate_collinearity = float(np.dot(unit_center(nue_rate), unit_center(anti_rate)))

# Robustness of the selected primary profile over the already-saved T402 splits.
best = scores.iloc[0]
best_values = candidates[str(best["candidate"])]
if best["orientation"] == "reversed":
    best_values = best_values[::-1]

dist = pd.read_csv(P402 / "T402_PRIMARY_BIN_DISTRIBUTIONS.csv")
pivot = dist.pivot_table(
    index=["salt", "bin_center"],
    columns="source",
    values="proportion_of_split_weight",
).reset_index()
split_rows: list[dict] = []
for salt, group in pivot.groupby("salt", sort=True):
    g = group.sort_values("bin_center")
    if len(g) != 8 or g[["C", "AC"]].isna().any().any():
        continue
    d_split = (g["C"] - g["AC"]).to_numpy(float)
    score = float(np.dot(unit_center(d_split), unit_center(best_values)))
    split_rows.append(
        {
            "salt": int(salt),
            "cosine": score,
            "absolute_cosine": abs(score),
            "same_sign_as_primary": bool(np.sign(score) == np.sign(best["cosine"])),
        }
    )
split_scores = pd.DataFrame(split_rows)

kde = pd.read_csv(P402 / "T402_KDE_TOPOLOGY.csv")
saved_vector = np.asarray(r402["source_difference"]["mean_C_minus_AC_by_bin"], dtype=float)
g1 = bool(np.allclose(detector, saved_vector, atol=1e-15, rtol=0) and kde["passes_registered_windows"].all())
g2 = bool(best["absolute_cosine"] >= 0.65)
g3 = bool(best["registered_shift_rank_of_8"] == 1)
whole_names = {"delayed total release", "nu_e release", "anti_nu_mu release"}
component_names = {
    "flavor contrast (anti_nu_mu - nu_e)",
    "release gradient",
    "remaining-muon curvature",
}
max_whole = float(scores[scores["candidate"].isin(whole_names)]["absolute_cosine"].max())
g4 = bool(
    best["candidate"] in component_names
    and best["absolute_cosine"] >= max_whole + 0.10
)
g5 = True

if all([g1, g2, g3, g4, g5]):
    verdict = "COMPONENT LOCATED"
elif g1 and g2 and g5:
    verdict = "PARTIAL COMPONENT RELATION"
elif g1 and g5:
    verdict = "COMPONENT NOT LOCATED"
else:
    verdict = "INVALID"

split_summary = {
    "n": int(len(split_scores)),
    "median_cosine": float(split_scores["cosine"].median()),
    "resampling_interval_95": [
        float(split_scores["cosine"].quantile(0.025)),
        float(split_scores["cosine"].quantile(0.975)),
    ],
    "fraction_absolute_cosine_at_least_0p65": float(
        (split_scores["absolute_cosine"] >= 0.65).mean()
    ),
    "fraction_same_sign_as_primary": float(split_scores["same_sign_as_primary"].mean()),
    "note": "Overlapping deterministic T402 resampling probes, not independent experiments.",
}

results = {
    "test": "T403",
    "date": "2026-08-18",
    "protocol_sha256": sha256(PROTOCOL),
    "verdict": verdict,
    "question": "Can the detector-side delayed-neutrino footprint be reverse-traced to a component already present upstream?",
    "coordinate": {
        "local_ara": "T402/T400 frozen local child ARA 0-2",
        "left_time_us": left,
        "right_time_us": right,
        "sample_x": x.tolist(),
        "sample_time_us": t.tolist(),
    },
    "selected_same_archive_candidate": {
        "candidate": str(best["candidate"]),
        "orientation": str(best["orientation"]),
        "cosine": float(best["cosine"]),
        "absolute_cosine": float(best["absolute_cosine"]),
        "registered_shift_rank_of_8": int(best["registered_shift_rank_of_8"]),
        "best_shift": int(best["best_shift"]),
        "best_shift_absolute_cosine": float(best["best_shift_absolute_cosine"]),
        "max_whole_positive_rate_absolute_cosine": max_whole,
        "margin_over_whole_positive_rates": float(best["absolute_cosine"] - max_whole),
    },
    "detector_landmarks_from_T402": {
        "positive_crest_x_range": [float(kde["positive_crest_x"].min()), float(kde["positive_crest_x"].max())],
        "ridge_crossing_x_range": [float(kde["crossing_nearest_ridge_x"].min()), float(kde["crossing_nearest_ridge_x"].max())],
        "negative_trough_x_range": [float(kde["negative_trough_x"].min()), float(kde["negative_trough_x"].max())],
    },
    "split_robustness": split_summary,
    "t397_exploratory_best": t397_scores.iloc[0].to_dict(),
    "post_frozen_flavor_identifiability": {
        "nu_e_vs_anti_nu_mu_centered_cosine": flavor_rate_collinearity,
        "area_normalized_flavor_shape_contrast_direct_cosine": float(
            flavor_shape_scores.loc[
                flavor_shape_scores["orientation"] == "direct", "cosine"
            ].iloc[0]
        ),
        "area_normalized_flavor_shape_contrast_direct_rank_of_8": int(
            flavor_shape_scores.loc[
                flavor_shape_scores["orientation"] == "direct",
                "registered_shift_rank_of_8",
            ].iloc[0]
        ),
        "classification": "diagnostic only; does not alter the frozen gates",
    },
    "gates": {
        "G1_detector_integrity": g1,
        "G2_component_selection": g2,
        "G3_alignment_control": g3,
        "G4_derivative_specificity": g4,
        "G5_evidence_boundary": g5,
    },
    "evidence_classes": {
        "T402": "measured detector source-difference diagnostic; not a flavor tag",
        "T398_T400": "fitted source templates and a derived remaining-parent complement",
        "T397": "independent silver muon phase trace; separate medium and experiment",
        "T395_T396": "truth-model statistical locks; not temporal waveform observations and therefore excluded from waveform scoring",
    },
    "boundaries": [
        "The detector footprint is a C-minus-AC response contrast, not a pristine neutrino field waveform.",
        "The remaining-muon curve, release gradient and remaining-parent curvature are derived from the same delayed source template and are not independent confirmations.",
        "T397 has no shared event key or time origin with COHERENT and cannot establish a causal precursor match.",
        "T395 and T396 recover event-level statistical relations in a frozen V-A truth model but do not contain observed time waveforms.",
        "No individual neutrino birth time is measured.",
    ],
    "input_hashes_sha256": {
        "T402_BIN_SUMMARY.csv": sha256(P402 / "T402_BIN_SUMMARY.csv"),
        "T402_RESULTS.json": sha256(P402 / "T402_RESULTS.json"),
        "T400_RESULTS.json": sha256(P400 / "T400_RESULTS.json"),
        "T398_NATIVE_WAVE_OVERLAP.csv": sha256(P398 / "T398_NATIVE_WAVE_OVERLAP.csv"),
        "T398_RESULTS.json": sha256(P398 / "T398_RESULTS.json"),
        "T397_PHASE_PROFILES.csv": sha256(P397 / "T397_PHASE_PROFILES.csv"),
        "T397_RESULTS.json": sha256(P397 / "T397_RESULTS.json"),
    },
}

profiles.to_csv(OUT / "T403_COMPONENT_PROFILES.csv", index=False)
scores.to_csv(OUT / "T403_COMPONENT_SCORES.csv", index=False)
t397_profiles.to_csv(OUT / "T403_T397_PHASE_PROFILES.csv", index=False)
t397_scores.to_csv(OUT / "T403_T397_COMPONENT_SCORES.csv", index=False)
flavor_shape_scores.to_csv(OUT / "T403_FLAVOR_SHAPE_DIAGNOSTIC.csv", index=False)
split_scores.to_csv(OUT / "T403_SPLIT_ROBUSTNESS.csv", index=False)
with (OUT / "T403_RESULTS.json").open("w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(json.dumps(results, indent=2, ensure_ascii=False))
