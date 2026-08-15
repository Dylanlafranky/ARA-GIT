from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "T394_native_pair_and_release"
RESULTS_PATH = OUT / "T394_RESULTS.json"
VALIDATION_PATH = OUT / "T394_VALIDATION.json"
SAMPLE_PATH = OUT / "T394_TEST1_EVENT_SAMPLE.csv"
QUINTILE_PATH = OUT / "T394_TEST1_QUINTILES.csv"
CDF_PATH = OUT / "T394_TEST2_HOLDOUT_CDF.csv"
SENSITIVITY_PATH = OUT / "T394_TEST2_SENSITIVITY.csv"
ARTIFACT_PATH = OUT / "T394_REPORT_ARTIFACT.json"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build_histogram(values: list[float], bins: int = 24) -> list[dict[str, float | int]]:
    counts = [0 for _ in range(bins)]
    for value in values:
        index = min(bins - 1, max(0, int(value / 2.0 * bins)))
        counts[index] += 1
    width = 2.0 / bins
    total = len(values)
    return [
        {
            "bin": i + 1,
            "ara_coordinate": round((i + 0.5) * width, 6),
            "bin_low": round(i * width, 6),
            "bin_high": round((i + 1) * width, 6),
            "event_count": count,
            "event_share": count / total,
            "sample_n": total,
        }
        for i, count in enumerate(counts)
    ]


def main() -> None:
    results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    validation = json.loads(VALIDATION_PATH.read_text(encoding="utf-8"))
    test1 = results["test1_native_neutral_pair"]
    va = test1["v_minus_a"]
    phase_space = test1["phase_space_control"]
    shuffled = test1["identity_shuffled_control"]
    test2 = results["test2_causal_release"]
    scores = test2["models"]["scores"]
    ci = test2["bootstrap_M0_minus_MP_nll"]["ci95"]

    sample = read_csv(SAMPLE_PATH)
    pair_hist = build_histogram([float(row["y_nu_e_native"]) for row in sample])
    quintiles = [
        {
            "charged_energy_quintile": int(row["quintile"]),
            "x_low": float(row["x_low"]),
            "x_high": float(row["x_high"]),
            "events": int(row["n"]),
            "mean_pair_asymmetry": float(row["mean_pair_asymmetry"]),
            "median_y_nu_e": float(row["median_y_nu_e"]),
        }
        for row in read_csv(QUINTILE_PATH)
    ]

    cdf_rows = read_csv(CDF_PATH)[::2]
    cdf_long: list[dict[str, float | str]] = []
    for row in cdf_rows:
        t = float(row["time_us"])
        cdf_long.extend(
            [
                {
                    "time_us": t,
                    "series": "Observed holdout",
                    "cdf": float(row["holdout_empirical_cdf"]),
                    "cohort": "374,340 tagged holdout decays",
                    "role": "untouched outcome",
                },
                {
                    "time_us": t,
                    "series": "ARA anti-phase reconstruction",
                    "cdf": float(row["MP_antiphase_cdf"]),
                    "cohort": "calibration-derived",
                    "role": "prospective population prediction",
                },
                {
                    "time_us": t,
                    "series": "One exponential",
                    "cdf": float(row["M0_exponential_cdf"]),
                    "cohort": "calibration-fitted",
                    "role": "baseline",
                },
            ]
        )

    sensitivity = [
        {
            "bins": int(row["bins"]),
            "M0_mean_nll": float(row["M0_mean_nll"]),
            "MP_mean_nll": float(row["MP_mean_nll"]),
            "M0_minus_MP_nll": float(row["M0_minus_MP_nll"]),
            "ci95_low": float(row["ci95_low"]),
            "ci95_high": float(row["ci95_high"]),
            "M0_ks": float(row["M0_ks"]),
            "MP_ks": float(row["MP_ks"]),
            "passes": row["passes"].lower() == "true",
        }
        for row in read_csv(SENSITIVITY_PATH)
    ]

    summary = [
        {
            "native_y_nue_mean": va["mean_y_nu_e"],
            "native_y_antinu_mean": va["mean_y_anti_nu_mu"],
            "native_ordering": va["probability_anti_nu_mu_heavier"],
            "shuffled_ordering": shuffled["probability_anti_nu_mu_heavier"],
            "native_coarse_pair": va["fraction_coarse_pair_l1_le_0p20"],
            "phase_space_coarse_pair": phase_space["fraction_coarse_pair_l1_le_0p20"],
            "nll_gain": test2["bootstrap_M0_minus_MP_nll"]["mean"],
            "nll_ci_low": ci[0],
            "nll_ci_high": ci[1],
            "M0_ks": scores["M0_truncated_exponential"]["ks"],
            "MP_ks": scores["MP_reconstructed_antiphase"]["ks"],
            "holdout_tagged": test2["splits"]["holdout_tagged"],
            "calibration_tagged": test2["splits"]["calibration_tagged"],
        }
    ]

    controls = [
        {
            "measure": "Near coarse 0.5/1.5 pair",
            "native": va["fraction_coarse_pair_l1_le_0p20"],
            "control": phase_space["fraction_coarse_pair_l1_le_0p20"],
            "control_name": "uniform phase space",
            "interpretation": "not enriched",
        },
        {
            "measure": "Anti-nu_mu is heavier",
            "native": va["probability_anti_nu_mu_heavier"],
            "control": shuffled["probability_anti_nu_mu_heavier"],
            "control_name": "identity-label shuffle",
            "interpretation": "direction survives only with native labels",
        },
    ]

    gates = [
        {
            "gate": "T1 native pair closes at 2",
            "status": "PASS",
            "meaning": "Each truth-level neutral pair satisfies y_nu_e + y_anti_nu_mu = 2.",
        },
        {
            "gate": "T1 fixed 0.5/1.5 landmark",
            "status": "NOT SUPPORTED",
            "meaning": "14.6% are near the pair, below the 17.2% uniform phase-space control.",
        },
        {
            "gate": "T2 population handover forecast",
            "status": "PASS",
            "meaning": "Calibration reconstruction beats one-exponential and reversed controls on untouched tagged decays.",
        },
        {
            "gate": "T2 next individual muon",
            "status": "NOT TESTABLE",
            "meaning": "The source has no varying pre-decay measurement for individual surviving muons.",
        },
    ]

    sources = [
        {
            "id": "t394_results",
            "label": "T394 frozen results",
            "path": "analysis/muon/T394_native_pair_and_release/T394_RESULTS.json",
            "query": {
                "engine": "duckdb",
                "language": "sql",
                "sql": "SELECT * FROM read_json_auto('analysis/muon/T394_native_pair_and_release/T394_RESULTS.json')",
                "description": "Read the frozen Test 1 and Test 2 results, cohorts, scores and gates.",
                "tables_used": [
                    "analysis/muon/T394_native_pair_and_release/T394_RESULTS.json"
                ],
                "metric_definitions": [
                    "Native pair coordinate y_nu_e = 2 E_nu_e/(E_nu_e + E_anti_nu_mu); y_anti_nu_mu = 2 - y_nu_e.",
                    "NLL gain = mean held-out NLL(one exponential) - mean held-out NLL(calibration anti-phase reconstruction).",
                ],
            },
        },
        {
            "id": "t394_validation",
            "label": "T394 independent validation and bin sensitivity",
            "path": "analysis/muon/T394_native_pair_and_release/T394_VALIDATION.json",
            "query": {
                "engine": "duckdb",
                "language": "sql",
                "sql": "SELECT * FROM read_json_auto('analysis/muon/T394_native_pair_and_release/T394_VALIDATION.json')",
                "description": "Read independent closure, source-hash, optimizer-reproduction and bin-sensitivity checks.",
                "tables_used": [
                    "analysis/muon/T394_native_pair_and_release/T394_VALIDATION.json"
                ],
                "metric_definitions": [
                    "A bin setting passes when the reconstruction improves mean NLL, its block-bootstrap 95% interval is above zero, and KS is below the exponential baseline."
                ],
            },
        },
        {
            "id": "t394_test1_sample",
            "label": "T394 deterministic native-pair event sample",
            "path": "analysis/muon/T394_native_pair_and_release/T394_TEST1_EVENT_SAMPLE.csv",
            "query": {
                "engine": "duckdb",
                "language": "sql",
                "sql": "SELECT *, 2*x_nu_e/(x_nu_e+x_anti_nu_mu) AS y_nu_e FROM read_csv_auto('analysis/muon/T394_native_pair_and_release/T394_TEST1_EVENT_SAMPLE.csv')",
                "description": "Read the deterministic 20,000-event truth-level sample used to display the native neutral-pair coordinate.",
                "tables_used": [
                    "analysis/muon/T394_native_pair_and_release/T394_TEST1_EVENT_SAMPLE.csv"
                ],
                "filters": ["deterministic evenly spaced sample from 1,000,000 frozen events"],
            },
        },
        {
            "id": "superk_2025",
            "label": "Super-Kamiokande stopped cosmic-muon decay-electron and neutron archive",
            "href": "https://zenodo.org/records/15081911",
            "query": {
                "engine": "python",
                "language": "python",
                "description": "Parse decay-electron momentum/time and neutron-time rows; create deterministic calibration, validation and holdout row-hash splits.",
                "tables_used": ["decayes_and_neutrons.csv"],
                "filters": [
                    "decay-electron time 0.45 to 30 microseconds",
                    "positive decay-electron momentum",
                    "outcome columns forbidden from pre-outcome prediction",
                ],
            },
        },
        {
            "id": "t394_test2_cdf",
            "label": "T394 tagged-muon holdout CDF reduction",
            "path": "analysis/muon/T394_native_pair_and_release/T394_TEST2_HOLDOUT_CDF.csv",
            "query": {
                "engine": "duckdb",
                "language": "sql",
                "sql": "SELECT * FROM read_csv_auto('analysis/muon/T394_native_pair_and_release/T394_TEST2_HOLDOUT_CDF.csv')",
                "description": "Read observed untouched holdout CDF and the two calibration-fitted prediction curves.",
                "tables_used": [
                    "analysis/muon/T394_native_pair_and_release/T394_TEST2_HOLDOUT_CDF.csv"
                ],
                "filters": [
                    "tagged decay-electron time 0.45 to 30 microseconds",
                    "deterministic holdout row-hash buckets 7 to 9",
                ],
                "metric_definitions": [
                    "holdout_empirical_cdf = cumulative fraction of 374,340 untouched tagged decay-electron times",
                    "MP_antiphase_cdf = calibration-only 128-bin empirical release complement with Jeffreys 0.5 smoothing",
                ],
            },
        },
        {
            "id": "pdg_muon_decay",
            "label": "Particle Data Group review of muon decay parameters",
            "href": "https://pdg.lbl.gov/2025/reviews/rpp2025-rev-muon-decay-params.pdf",
            "query": {
                "description": "Standard Model V-A muon-decay crosswalk used to generate the truth-level neutral-pair distribution."
            },
        },
    ]

    manifest = {
        "version": 1,
        "surface": "report",
        "title": "T394 — Native neutrino pair and causal muon handover",
        "description": "Two frozen ARA tests: native neutral-pair geometry and leakage-safe population handover prediction.",
        "generatedAt": "2026-08-15T21:35:00+10:00",
        "blocks": [
            {"id": "title", "type": "markdown", "body": "# T394 — Native neutrino pair and causal muon handover"},
            {
                "id": "summary",
                "type": "markdown",
                "body": "## Technical summary\n\n**Both tests completed, but they answer different rungs.** Test 1 recovers a broad truth-level neutrino-pair ARA gradient: the pair always closes at 2, but a fixed 0.5/1.5 split is not supported. Test 2 reconstructs the untouched population distribution of tagged muon-decay handovers substantially better than one fitted exponential, and the gain survives four histogram resolutions. It still cannot identify which individual living muon releases next because this archive contains no changing pre-decay field for an individual muon."
            },
            {"id": "metrics", "type": "metric-strip", "cardIds": ["pair_card", "direction_card", "forecast_card", "ks_card"]},
            {
                "id": "test1_intro",
                "type": "markdown",
                "sourceId": "t394_results",
                "body": "## The neutral pair is a gradient, not a fixed 0.5/1.5 split\n\nThe native pair coordinate spans almost the whole 0–2 line. Its mean is **0.924 / 1.076**, while **14.6%** of events lie within L1 distance 0.20 of either 0.5/1.5 orientation. A uniform phase-space control places **17.2%** there, so the coarse pair is allowed but not preferentially selected by this model."
            },
            {"id": "pair_chart", "type": "chart", "chartId": "pair_distribution"},
            {
                "id": "test1_gradient_intro",
                "type": "markdown",
                "sourceId": "t394_results",
                "body": "## Charged-daughter energy changes the pair asymmetry monotonically\n\nMean neutral-pair asymmetry rises from **0.225** in the lowest charged-energy quintile to **0.710** in the highest. The native labels also retain a directional ordering—anti-neutrino muon is heavier in **62.5%** of events—while a label shuffle returns that probability to **50.0%**. This is the informative Test 1 structure."
            },
            {"id": "quintile_chart", "type": "chart", "chartId": "quintile_asymmetry"},
            {
                "id": "controls_intro",
                "type": "markdown",
                "sourceId": "t394_results",
                "body": "## The controls separate shape from identity\n\nThe phase-space control tests whether a visually interesting pair is merely geometrically common. The label shuffle preserves the amount of asymmetry but destroys which neutrino owns which side. Together they reject a privileged fixed split while preserving a real identity-dependent direction."
            },
            {"id": "controls_table", "type": "table", "tableId": "control_audit"},
            {
                "id": "test2_intro",
                "type": "markdown",
                "sourceId": "t394_results",
                "body": "## The reconstructed anti-phase forecasts the untouched population handover\n\nOn **374,340** tagged holdout decays, the calibration-derived reconstruction lowers mean negative log likelihood from **1.8494** to **1.8058** and reduces KS error from **0.0720** to **0.0178**. The plotted prediction was frozen before reading the holdout outcomes. It forecasts the population distribution conditional on a detected decay electron; it is not yet an individual countdown."
            },
            {"id": "cdf_chart", "type": "chart", "chartId": "holdout_cdf"},
            {
                "id": "robust_intro",
                "type": "markdown",
                "sourceId": "t394_validation",
                "body": "## The population result is not a 128-bin accident\n\nIndependent recomputation reproduced the fitted rate within **4.1×10⁻⁹** and found positive held-out improvement at 32, 64, 128 and 256 bins. Every block-bootstrap interval remained above zero and every reconstructed KS score beat the exponential baseline."
            },
            {"id": "sensitivity_chart", "type": "chart", "chartId": "bin_sensitivity"},
            {"id": "sensitivity_table", "type": "table", "tableId": "sensitivity_audit"},
            {
                "id": "scope",
                "type": "markdown",
                "body": "## Scope, data and metric definitions\n\n**Test 1** uses a frozen one-million-event Standard-Model V-A truth crosswalk. For each event, the two neutrino energies are normalized to their own TE-ARA pair: `y_nu_e = 2E_nu_e/(E_nu_e+E_anti_nu_mu)` and `y_anti_nu_mu = 2-y_nu_e`. **Test 2** uses 1,986,465 stopped-cosmic-muon rows from Super-Kamiokande; 622,746 tagged decays form calibration and 374,340 form untouched holdout. Lower NLL and lower KS are better."
            },
            {
                "id": "methods",
                "type": "markdown",
                "body": "## Frozen methodology\n\nTest 1 compares the native V-A pair with a uniform phase-space control and an identity-label shuffle. Test 2 deterministically splits rows by a frozen 64-bit row hash. The null is one truncated exponential over 0.45–30 microseconds. The ARA anti-phase candidate is a calibration-only empirical release complement with Jeffreys smoothing. A time-reversed distribution is the wrong-direction control. Outcome columns—decay-electron time, momentum and neutron observations—are forbidden as pre-outcome predictors."
            },
            {
                "id": "limits",
                "type": "markdown",
                "body": "## Limitations and claim ceiling\n\nTest 1 is a truth-model crosswalk, not direct simultaneous observation of both neutrinos. Test 2 is flexible population density estimation, so its success is not unique proof of ARA. The archive is also outcome-conditioned: it describes when detected tagged decays occur, not whether a stopped muon decays rather than captures or escapes detection. Most importantly, it contains no varying pre-decay individual field, so the individual handover gate is structurally untestable here."
            },
            {"id": "gates_intro", "type": "markdown", "body": "## Frozen gate audit\n\nThe completed tests support native pair closure and population handover reconstruction. They do not support a privileged fixed 0.5/1.5 neutral split, and they cannot yet establish advance prediction for a named individual muon."},
            {"id": "gates_table", "type": "table", "tableId": "gate_audit"},
            {
                "id": "next",
                "type": "markdown",
                "body": "## Recommended next step\n\nAcquire or locate an event-linked archive that observes the **same individual muon before decay** with at least one changing traversal-sensitive field—spin/polarisation phase, trajectory, stopping-site field or another same-scale child cut—and then records the charged-daughter timestamp. Freeze the anti-phase reconstruction on calibration muons and score it on untouched individuals. That is the test that can turn the present population result into genuine advance handover prediction."
            },
            {
                "id": "questions",
                "type": "markdown",
                "body": "## Further questions\n\nDoes the native pair gradient shift with muon polarisation? Which pre-decay child coordinate best carries the missing anti-phase? Does the population reconstruction replicate in a second detector medium after explicitly modelling capture and detector response?"
            },
        ],
        "cards": [
            {
                "id": "pair_card",
                "dataset": "summary",
                "sourceId": "t394_results",
                "description": "Truth-level native neutral-pair mean on its own 0–2 ARA scale.",
                "metrics": [
                    {"label": "Mean y_nu_e", "field": "native_y_nue_mean", "format": "number"},
                    {"label": "Mean y_anti_nu_mu", "field": "native_y_antinu_mean", "format": "number"},
                ],
            },
            {
                "id": "direction_card",
                "dataset": "summary",
                "sourceId": "t394_results",
                "description": "Fraction of events where the anti-neutrino muon owns the heavier side.",
                "metrics": [
                    {"label": "Native ordering", "field": "native_ordering", "format": "percent"},
                    {"label": "After label shuffle", "field": "shuffled_ordering", "format": "percent"},
                ],
            },
            {
                "id": "forecast_card",
                "dataset": "summary",
                "sourceId": "t394_results",
                "description": "Positive NLL gain favors the calibration-derived anti-phase reconstruction.",
                "metrics": [
                    {"label": "M0 − MP NLL", "field": "nll_gain", "format": "number", "signed": True},
                    {"label": "95% CI low", "field": "nll_ci_low", "format": "number", "signed": True},
                    {"label": "95% CI high", "field": "nll_ci_high", "format": "number", "signed": True},
                ],
            },
            {
                "id": "ks_card",
                "dataset": "summary",
                "sourceId": "t394_results",
                "description": "Maximum CDF error on untouched tagged decays; lower is better.",
                "metrics": [
                    {"label": "Reconstructed KS", "field": "MP_ks", "format": "number"},
                    {"label": "One-exponential KS", "field": "M0_ks", "format": "number"},
                ],
            },
        ],
        "charts": [
            {
                "id": "pair_distribution",
                "title": "Native neutrino-pair ARA distribution",
                "subtitle": "Deterministic 20,000-event display sample; full frozen model n=1,000,000",
                "type": "bar",
                "intent": "distribution",
                "question": "Does the native neutral pair occupy one fixed split or a broad 0–2 gradient?",
                "rationale": "A binned distribution shows occupancy over the complete pair coordinate without hiding event spread in a mean.",
                "dataset": "pair_hist",
                "sourceId": "t394_test1_sample",
                "layout": "full",
                "encodings": {
                    "x": {"field": "ara_coordinate", "type": "quantitative", "label": "nu_e share of neutral pair", "unit": "ARA 0–2"},
                    "y": {"field": "event_share", "type": "quantitative", "label": "Share of events"},
                    "tooltip": [
                        {"field": "bin_low", "label": "Bin low"},
                        {"field": "bin_high", "label": "Bin high"},
                        {"field": "event_count", "label": "Events"},
                    ],
                },
                "referenceLines": [
                    {"axis": "x", "value": 0.5, "label": "coarse child", "lineStyle": "dashed", "color": "neutral"},
                    {"axis": "x", "value": 1.0, "label": "pair ridge", "lineStyle": "solid", "color": "neutral"},
                    {"axis": "x", "value": 1.5, "label": "coarse child", "lineStyle": "dashed", "color": "neutral"},
                ],
                "valueFormat": "percent",
            },
            {
                "id": "quintile_asymmetry",
                "title": "Neutral-pair asymmetry across charged-energy quintiles",
                "subtitle": "Five equal groups of 200,000 frozen truth events",
                "type": "line",
                "intent": "trend",
                "question": "Does the neutral-pair split change systematically with the charged daughter?",
                "rationale": "A connected ordered line makes the monotonic change across energy quintiles explicit.",
                "dataset": "quintiles",
                "sourceId": "t394_results",
                "layout": "full",
                "encodings": {
                    "x": {"field": "charged_energy_quintile", "type": "quantitative", "label": "Charged-energy quintile"},
                    "y": {"field": "mean_pair_asymmetry", "type": "quantitative", "label": "Mean |y_nu_e − y_anti_nu_mu|", "unit": "ARA"},
                    "tooltip": [
                        {"field": "x_low", "label": "Charged coordinate low"},
                        {"field": "x_high", "label": "Charged coordinate high"},
                        {"field": "median_y_nu_e", "label": "Median y_nu_e"},
                    ],
                },
                "valueFormat": "number",
            },
            {
                "id": "holdout_cdf",
                "title": "Tagged muon-decay handover timing",
                "subtitle": "Untouched holdout n=374,340; calibration-derived prediction compared with one exponential",
                "type": "line",
                "intent": "trend",
                "question": "Does the calibration anti-phase reconstruct the unseen release-time distribution?",
                "rationale": "CDF curves expose both overall agreement and where timing departures accumulate.",
                "dataset": "cdf_long",
                "sourceId": "t394_test2_cdf",
                "layout": "full",
                "encodings": {
                    "x": {"field": "time_us", "type": "quantitative", "label": "Tagged daughter time", "unit": "microseconds"},
                    "y": {"field": "cdf", "type": "quantitative", "label": "Cumulative share"},
                    "color": {"field": "series", "type": "nominal", "label": "Curve"},
                    "tooltip": [
                        {"field": "cohort", "label": "Cohort"},
                        {"field": "role", "label": "Role"},
                    ],
                },
                "valueFormat": "percent",
            },
            {
                "id": "bin_sensitivity",
                "title": "Held-out NLL gain across reconstruction resolutions",
                "subtitle": "Positive values favor the ARA anti-phase reconstruction; all 95% intervals remain above zero",
                "type": "bar",
                "intent": "comparison",
                "question": "Does Test 2 depend on one arbitrary bin count?",
                "rationale": "Bars compare the same held-out score at four predeclared resolutions on a common scale.",
                "dataset": "sensitivity",
                "sourceId": "t394_validation",
                "layout": "full",
                "encodings": {
                    "x": {"field": "bins", "type": "nominal", "label": "Empirical reconstruction bins"},
                    "y": {"field": "M0_minus_MP_nll", "type": "quantitative", "label": "M0 − MP mean NLL"},
                    "tooltip": [
                        {"field": "ci95_low", "label": "95% CI low"},
                        {"field": "ci95_high", "label": "95% CI high"},
                        {"field": "MP_ks", "label": "MP KS"},
                    ],
                },
                "referenceLines": [
                    {"axis": "y", "value": 0, "label": "no improvement", "lineStyle": "solid", "color": "neutral"}
                ],
                "valueFormat": "number",
            },
        ],
        "tables": [
            {
                "id": "control_audit",
                "title": "Test 1 control comparison",
                "subtitle": "Native V-A pair versus geometry-only and identity-shuffled controls",
                "dataset": "controls",
                "sourceId": "t394_results",
                "defaultSort": {"field": "measure", "direction": "asc"},
                "density": "spacious",
                "layout": "full",
                "columns": [
                    {"field": "measure", "label": "Measure", "type": "text"},
                    {"field": "native", "label": "Native", "type": "percent"},
                    {"field": "control", "label": "Control", "type": "percent"},
                    {"field": "control_name", "label": "Control", "type": "text"},
                    {"field": "interpretation", "label": "Reading", "type": "text"},
                ],
            },
            {
                "id": "sensitivity_audit",
                "title": "Test 2 resolution sensitivity",
                "subtitle": "Independent holdout scoring across 32–256 empirical bins",
                "dataset": "sensitivity",
                "sourceId": "t394_validation",
                "defaultSort": {"field": "bins", "direction": "asc"},
                "density": "spacious",
                "layout": "full",
                "columns": [
                    {"field": "bins", "label": "Bins", "type": "number"},
                    {"field": "M0_minus_MP_nll", "label": "NLL gain", "type": "number"},
                    {"field": "ci95_low", "label": "95% low", "type": "number"},
                    {"field": "ci95_high", "label": "95% high", "type": "number"},
                    {"field": "MP_ks", "label": "MP KS", "type": "number"},
                    {"field": "passes", "label": "Pass", "type": "text"},
                ],
            },
            {
                "id": "gate_audit",
                "title": "Frozen T394 claims and gates",
                "subtitle": "What the two tests establish and what remains outside this source",
                "dataset": "gates",
                "sourceId": "t394_results",
                "defaultSort": {"field": "gate", "direction": "asc"},
                "density": "spacious",
                "layout": "full",
                "columns": [
                    {"field": "gate", "label": "Gate", "type": "text"},
                    {"field": "status", "label": "Status", "type": "text"},
                    {"field": "meaning", "label": "Meaning", "type": "text"},
                ],
            },
        ],
        "sources": sources,
    }

    artifact = {
        "surface": "report",
        "manifest": manifest,
        "snapshot": {
            "version": 1,
            "generatedAt": "2026-08-15T21:35:00+10:00",
            "status": "ready",
            "datasets": {
                "summary": summary,
                "pair_hist": pair_hist,
                "quintiles": quintiles,
                "controls": controls,
                "cdf_long": cdf_long,
                "sensitivity": sensitivity,
                "gates": gates,
            },
        },
        "sources": sources,
        "package_info": {
            "report_audience": "technical",
            "chart_map": [
                "Test 1 distribution: native neutral-pair occupancy over ARA 0–2.",
                "Test 1 relationship: asymmetry across charged-energy quintiles.",
                "Test 2 prediction: observed versus reconstructed holdout CDF.",
                "Robustness: NLL gain across bin resolutions.",
            ],
            "validation_status": validation["overall"],
        },
    }
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    print(ARTIFACT_PATH)


if __name__ == "__main__":
    main()
