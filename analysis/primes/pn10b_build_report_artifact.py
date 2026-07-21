"""Build the bounded Data Analytics report payload for PN10B."""

from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "PN10B_REPORT_ARTIFACT.json"

result = json.loads((HERE / "PN10B_CHILD_PHASE_RESULTS.json").read_text(encoding="utf-8"))
geometry = json.loads((HERE / "PN10B_EVENT_GEOMETRY_RESULTS.json").read_text(encoding="utf-8"))
metric_seed = list(csv.DictReader((HERE / "PN10B_MODEL_METRICS.csv").open(encoding="utf-8")))
comparison_seed = list(csv.DictReader((HERE / "PN10B_FRESH_COMPARISONS.csv").open(encoding="utf-8")))
event_seed = list(csv.DictReader((HERE / "PN10B_EVENT_CENTERED_TRACES.csv").open(encoding="utf-8")))
example_seed = list(csv.DictReader((HERE / "PN10B_PRIME_CHILD_EXAMPLES.csv").open(encoding="utf-8")))
feature_count = {
    "parent_empirical": 0,
    "buchstab_parent": 0,
    "ara_compact": 4,
    "raw_compact": 4,
    "ara_full": 17,
    "raw_full": 17,
    "ara_order_scrambled": 17,
}
metric_seed = [
    {
        "stage": row["stage"],
        "model": row["model"],
        "feature_count": feature_count[row["model"]],
        "events": int(row["events"]),
        "primes": int(row["primes"]),
        "prevalence": float(row["prevalence"]),
        "log_loss_bits": float(row["log_loss_bits"]),
        "brier": float(row["brier"]),
        "auc": float(row["auc"]),
        "top_decile_lift": float(row["top_decile_lift"]),
        "calibration_error": float(row["calibration_error"]),
    }
    for row in metric_seed
]
comparison_seed = [
    {
        "comparison": row["comparison"],
        "first_model": row["first_model"],
        "second_model": row["second_model"],
        "gain_bits_per_event": float(row["gain_bits_per_event"]),
        "ci95_low": float(row["ci95_low"]),
        "ci95_high": float(row["ci95_high"]),
        "positive_blocks": int(row["positive_blocks"]),
        "blocks": int(row["blocks"]),
        "draws": int(row["draws"]),
    }
    for row in comparison_seed
]
event_rows = [
    {
        "event": "Prime-centred" if row["event"] == "prime_center" else "Late-composite-centred",
        "offset": int(row["offset"]),
        "center_count": int(row["center_count"]),
        "prime_rate": float(row["prime_rate"]),
        "survivor_rate": float(row["survivor_rate"]),
        "parent_progress_mean": float(row["parent_progress_mean"]),
        "parent_progress_median": float(row["parent_progress_median"]),
        "child_centroid_mean": float(row["child_centroid_mean"]),
        "child_centroid_median": float(row["child_centroid_median"]),
        "child_dispersion_mean": float(row["child_dispersion_mean"]),
        "child_coupling_mean": float(row["child_coupling_mean"]),
        "child_flip_count_mean": float(row["child_flip_count_mean"]),
    }
    for row in event_seed
]
rank_rows = []
first_prime_rows = [row for row in example_seed if row["example"] == "first_prime"]
for row, first in zip(geometry["prime_gate_rank_summary"], first_prime_rows):
    rank_rows.extend(
        [
            {
                "gate_rank": int(row["gate_rank"]),
                "series": "Mean across primes",
                "phase_a": float(row["prime_mean_a"]),
                "median_a": float(row["prime_median_a"]),
                "p10_a": float(row["prime_p10_a"]),
                "p90_a": float(row["prime_p90_a"]),
                "population": "45,166 primes",
            },
            {
                "gate_rank": int(row["gate_rank"]),
                "series": "Prime 4,000,000,007",
                "phase_a": float(first["phase_a"]),
                "median_a": None,
                "p10_a": None,
                "p90_a": None,
                "population": "one worked prime",
            },
        ]
    )
population_rows = []
for metric in ("child_centroid", "child_dispersion", "child_coupling", "child_flip_count", "pooled_child_phase_a"):
    prime = geometry["node_distributions"]["prime"][metric]
    composite = geometry["node_distributions"]["survivor_composite"][metric]
    contrast = geometry["population_contrasts"].get(metric)
    population_rows.append(
        {
            "metric": metric.replace("_", " ").title(),
            "prime_n": int(prime["n"]),
            "prime_mean": float(prime["mean"]),
            "prime_median": float(prime["median"]),
            "prime_min": float(prime["min"]),
            "prime_max": float(prime["max"]),
            "composite_n": int(composite["n"]),
            "composite_mean": float(composite["mean"]),
            "composite_median": float(composite["median"]),
            "standardized_difference": None if contrast is None else float(contrast["standardized_mean_difference"]),
        }
    )
first_prime_table = [
    {
        "gate_rank": int(row["gate_rank"]),
        "gate_q": int(row["gate_q"]),
        "remainder": int(row["remainder"]),
        "phase_a": float(row["phase_a"]),
        "phase_b": float(row["phase_b"]),
        "signed_orientation": float(row["signed_orientation"]),
        "coupling_to_next_rank": None if row["coupling_to_next_rank"] == "" else float(row["coupling_to_next_rank"]),
    }
    for row in first_prime_rows
]

metrics_sql = (HERE / "pn10b_report_metrics.sql").read_text(encoding="utf-8")
comparisons_sql = (HERE / "pn10b_report_comparisons.sql").read_text(encoding="utf-8")
event_trace_sql = (HERE / "pn10b_report_event_trace.sql").read_text(encoding="utf-8")
child_rank_sql = (HERE / "pn10b_report_child_rank.sql").read_text(encoding="utf-8")
geometry_population_sql = (HERE / "pn10b_report_geometry_population.sql").read_text(encoding="utf-8")
worked_prime_sql = (HERE / "pn10b_report_worked_prime.sql").read_text(encoding="utf-8")
connection = sqlite3.connect(":memory:")
connection.row_factory = sqlite3.Row
connection.execute(
    "CREATE TABLE pn10b_metrics (stage TEXT, model TEXT, feature_count INTEGER, events INTEGER, primes INTEGER, prevalence REAL, log_loss_bits REAL, brier REAL, auc REAL, top_decile_lift REAL, calibration_error REAL)"
)
connection.executemany(
    "INSERT INTO pn10b_metrics VALUES (:stage,:model,:feature_count,:events,:primes,:prevalence,:log_loss_bits,:brier,:auc,:top_decile_lift,:calibration_error)",
    metric_seed,
)
connection.execute(
    "CREATE TABLE pn10b_comparisons (comparison TEXT, first_model TEXT, second_model TEXT, gain_bits_per_event REAL, ci95_low REAL, ci95_high REAL, positive_blocks INTEGER, blocks INTEGER, draws INTEGER)"
)
connection.executemany(
    "INSERT INTO pn10b_comparisons VALUES (:comparison,:first_model,:second_model,:gain_bits_per_event,:ci95_low,:ci95_high,:positive_blocks,:blocks,:draws)",
    comparison_seed,
)
connection.execute(
    "CREATE TABLE pn10b_event_trace (event TEXT, offset INTEGER, center_count INTEGER, prime_rate REAL, survivor_rate REAL, parent_progress_mean REAL, parent_progress_median REAL, child_centroid_mean REAL, child_centroid_median REAL, child_dispersion_mean REAL, child_coupling_mean REAL, child_flip_count_mean REAL)"
)
connection.executemany(
    "INSERT INTO pn10b_event_trace VALUES (:event,:offset,:center_count,:prime_rate,:survivor_rate,:parent_progress_mean,:parent_progress_median,:child_centroid_mean,:child_centroid_median,:child_dispersion_mean,:child_coupling_mean,:child_flip_count_mean)",
    event_rows,
)
connection.execute(
    "CREATE TABLE pn10b_child_rank_profile (gate_rank INTEGER, series TEXT, phase_a REAL, median_a REAL, p10_a REAL, p90_a REAL, population TEXT)"
)
connection.executemany(
    "INSERT INTO pn10b_child_rank_profile VALUES (:gate_rank,:series,:phase_a,:median_a,:p10_a,:p90_a,:population)",
    rank_rows,
)
connection.execute(
    "CREATE TABLE pn10b_geometry_population (metric TEXT, prime_n INTEGER, prime_mean REAL, prime_median REAL, prime_min REAL, prime_max REAL, composite_n INTEGER, composite_mean REAL, composite_median REAL, standardized_difference REAL)"
)
connection.executemany(
    "INSERT INTO pn10b_geometry_population VALUES (:metric,:prime_n,:prime_mean,:prime_median,:prime_min,:prime_max,:composite_n,:composite_mean,:composite_median,:standardized_difference)",
    population_rows,
)
connection.execute(
    "CREATE TABLE pn10b_worked_prime_children (gate_rank INTEGER, gate_q INTEGER, remainder INTEGER, phase_a REAL, phase_b REAL, signed_orientation REAL, coupling_to_next_rank REAL)"
)
connection.executemany(
    "INSERT INTO pn10b_worked_prime_children VALUES (:gate_rank,:gate_q,:remainder,:phase_a,:phase_b,:signed_orientation,:coupling_to_next_rank)",
    first_prime_table,
)
metric_rows = [dict(row) for row in connection.execute(metrics_sql).fetchall()]
comparison_rows = [dict(row) for row in connection.execute(comparisons_sql).fetchall()]
event_rows = [dict(row) for row in connection.execute(event_trace_sql).fetchall()]
rank_rows = [dict(row) for row in connection.execute(child_rank_sql).fetchall()]
population_rows = [dict(row) for row in connection.execute(geometry_population_sql).fetchall()]
first_prime_table = [dict(row) for row in connection.execute(worked_prime_sql).fetchall()]
connection.close()

metrics_query = {
    "sql": metrics_sql,
    "language": "SQL",
    "engine": "SQLite",
    "tables_used": ["pn10b_metrics"],
    "description": "Select the reviewed fresh-target model scores in ascending log-loss order.",
    "filters": ["stage = pooled_D_E_to_fresh_F", "parent cutoff c = 0.90"],
    "metric_definitions": [
        "log_loss_bits = mean binary logarithmic scoring loss per surviving integer",
        "auc = probability that a randomly chosen prime receives a higher model score than a randomly chosen remaining composite, with ties averaged",
        "top_decile_lift = prime rate in the highest predicted-probability decile divided by overall survivor prime rate",
    ],
}
comparisons_query = {
    "sql": comparisons_sql,
    "language": "SQL",
    "engine": "SQLite",
    "tables_used": ["pn10b_comparisons"],
    "description": "Select paired fresh-target log-loss gains and registered contiguous-block bootstrap intervals.",
    "filters": ["fresh interval = [4000000000,4001000000)", "100 contiguous blocks", "2000 bootstrap draws", "seed = 20260720"],
    "metric_definitions": [
        "gain_bits_per_event = second-model log loss minus first-model log loss; positive values favor the first named model",
        "ci95_low and ci95_high = percentile 95% interval from resampling 100 contiguous target blocks",
    ],
}
event_trace_query = {
    "sql": event_trace_sql,
    "language": "SQL",
    "engine": "SQLite",
    "tables_used": ["pn10b_event_trace"],
    "description": "Select the complete post-hoc parent and child lead/at/lag traces around prime and late-composite events.",
    "filters": ["fresh interval = [4000000000,4001000000)", "event offsets = -32 through +32", "post-hoc descriptive only"],
    "metric_definitions": [
        "parent_progress_mean = mean of 1 for primes or 2*log(least_prime_factor)/log(n) for composites at each aligned offset",
        "child_centroid_mean = mean over event centres of the within-node mean of nine paid-gate Phase A readings",
    ],
}
child_rank_query = {
    "sql": child_rank_sql,
    "language": "SQL",
    "engine": "SQLite",
    "tables_used": ["pn10b_child_rank_profile"],
    "description": "Select the mean prime child-phase profile and the exact worked-prime profile by paid-gate rank.",
    "filters": ["nine largest already-paid gates q <= n^0.45", "worked prime n = 4000000007", "post-hoc descriptive only"],
    "metric_definitions": ["phase_a = 2*(n mod q)/q", "mean-across-primes phase_a uses 45166 prime nodes"],
}
geometry_population_query = {
    "sql": geometry_population_sql,
    "language": "SQL",
    "engine": "SQLite",
    "tables_used": ["pn10b_geometry_population"],
    "description": "Select reviewed prime and late-composite child-geometry summaries and standardized contrasts.",
    "filters": ["c = 0.90 survivors", "45166 primes", "9109 survivor composites", "post-hoc descriptive only"],
    "metric_definitions": ["standardized_difference = prime-minus-composite mean divided by the square root of the average population variance"],
}
worked_prime_query = {
    "sql": worked_prime_sql,
    "language": "SQL",
    "engine": "SQLite",
    "tables_used": ["pn10b_worked_prime_children"],
    "description": "Select all nine exact paid-gate child coordinates for prime 4000000007.",
    "filters": ["n = 4000000007", "nine largest already-paid gates q <= n^0.45"],
    "metric_definitions": ["phase_a = 2*remainder/q", "phase_b = 2-phase_a", "signed_orientation = phase_a-1"],
}

sources = [
    {"id": "pn10b_results", "label": "PN10B machine-readable results", "path": "analysis/primes/PN10B_CHILD_PHASE_RESULTS.json"},
    {"id": "pn10b_protocol", "label": "PN10B frozen protocol", "path": "analysis/primes/PN10B_CHILD_PHASE_PRIME_RANKING_PROTOCOL.md"},
    {"id": "pn10b_validation", "label": "PN10B independent validation", "path": "analysis/primes/PN10B_CHILD_PHASE_VALIDATION.json"},
    {"id": "pn10b_metrics_sql", "label": "PN10B fresh model-score query", "path": "analysis/primes/pn10b_report_metrics.sql", "query": metrics_query},
    {"id": "pn10b_comparisons_sql", "label": "PN10B paired-comparison query", "path": "analysis/primes/pn10b_report_comparisons.sql", "query": comparisons_query},
    {"id": "pn10b_geometry_results", "label": "PN10B post-hoc geometry results", "path": "analysis/primes/PN10B_EVENT_GEOMETRY_RESULTS.json"},
    {"id": "pn10b_geometry_trace", "label": "PN10B event-centred trace", "path": "analysis/primes/PN10B_EVENT_CENTERED_TRACES.csv"},
    {"id": "pn10b_geometry_examples", "label": "PN10B worked prime child vectors", "path": "analysis/primes/PN10B_PRIME_CHILD_EXAMPLES.csv"},
    {"id": "pn10b_geometry_validation", "label": "PN10B geometry validation", "path": "analysis/primes/PN10B_EVENT_GEOMETRY_VALIDATION.json"},
    {"id": "pn10b_geometry_trace_query", "label": "PN10B event-trace query", "path": "analysis/primes/pn10b_report_event_trace.sql", "query": event_trace_query},
    {"id": "pn10b_child_rank_query", "label": "PN10B child-rank query", "path": "analysis/primes/pn10b_report_child_rank.sql", "query": child_rank_query},
    {"id": "pn10b_geometry_population_query", "label": "PN10B population-geometry query", "path": "analysis/primes/pn10b_report_geometry_population.sql", "query": geometry_population_query},
    {"id": "pn10b_worked_prime_query", "label": "PN10B worked-prime query", "path": "analysis/primes/pn10b_report_worked_prime.sql", "query": worked_prime_query},
]

manifest = {
    "version": 1,
    "surface": "report",
    "title": "PN10B Child-Phase Prime Ranking",
    "description": "Registered test of whether already-paid factor-sphere child phases rank unresolved prime survivors.",
    "generatedAt": "2026-07-20T15:30:00+10:00",
    "sources": sources,
    "charts": [
        {
            "id": "fresh_gains",
            "title": "Fresh paired log-loss gain by registered comparison",
            "subtitle": "Positive values favor the first named model; 54,275 survivors at c=0.90",
            "type": "bar",
            "dataset": "fresh_comparisons",
            "sourceId": "pn10b_comparisons_sql",
            "source": {"label": "PN10B paired-comparison query", "path": "analysis/primes/pn10b_report_comparisons.sql", "query": comparisons_query},
            "encodings": {
                "x": {"field": "comparison", "type": "nominal", "label": "Registered comparison"},
                "y": {"field": "gain_bits_per_event", "type": "quantitative", "label": "Log-loss gain (bits/event)"},
                "tooltip": [
                    {"field": "ci95_low", "type": "quantitative", "label": "95% CI low"},
                    {"field": "ci95_high", "type": "quantitative", "label": "95% CI high"},
                    {"field": "positive_blocks", "type": "quantitative", "label": "Positive blocks"},
                ],
            },
            "layout": "full",
        },
        {
            "id": "parent_event_trace",
            "title": "Parent factor progress around prime and late-composite events",
            "subtitle": "Raw-integer offsets -32 to +32; the prime-centred trace reaches the exact 1.0 ridge at zero",
            "type": "line",
            "dataset": "event_trace",
            "sourceId": "pn10b_geometry_trace_query",
            "source": {"label": "PN10B event-trace query", "path": "analysis/primes/pn10b_report_event_trace.sql", "query": event_trace_query},
            "encodings": {
                "x": {"field": "offset", "type": "quantitative", "label": "Raw-integer offset"},
                "y": {"field": "parent_progress_mean", "type": "quantitative", "label": "Mean parent factor progress"},
                "color": {"field": "event", "type": "nominal", "label": "Centred event"},
                "tooltip": [
                    {"field": "prime_rate", "type": "quantitative", "label": "Prime rate"},
                    {"field": "center_count", "type": "quantitative", "label": "Centres"},
                    {"field": "child_centroid_mean", "type": "quantitative", "label": "Mean child centroid"},
                ],
            },
            "layout": "full",
        },
        {
            "id": "child_rank_trace",
            "title": "Nine paid-gate child phases at prime nodes",
            "subtitle": "Population means cancel near 1.0 while the worked prime carries strong local asymmetry",
            "type": "line",
            "dataset": "child_rank_profile",
            "sourceId": "pn10b_child_rank_query",
            "source": {"label": "PN10B child-rank query", "path": "analysis/primes/pn10b_report_child_rank.sql", "query": child_rank_query},
            "encodings": {
                "x": {"field": "gate_rank", "type": "quantitative", "label": "Paid-gate child rank"},
                "y": {"field": "phase_a", "type": "quantitative", "label": "Phase A on the 0-2 line"},
                "color": {"field": "series", "type": "nominal", "label": "Reading"},
                "tooltip": [
                    {"field": "population", "type": "nominal", "label": "Population"},
                    {"field": "p10_a", "type": "quantitative", "label": "Prime p10"},
                    {"field": "p90_a", "type": "quantitative", "label": "Prime p90"},
                ],
            },
            "layout": "full",
        },
    ],
    "tables": [
        {
            "id": "fresh_metrics",
            "title": "Fresh-target model scores",
            "subtitle": "Untouched interval [4,000,000,000, 4,001,000,000); lower log loss and Brier are better",
            "dataset": "fresh_metrics",
            "sourceId": "pn10b_metrics_sql",
            "source": {"label": "PN10B fresh model-score query", "path": "analysis/primes/pn10b_report_metrics.sql", "query": metrics_query},
            "defaultSort": {"field": "log_loss_bits", "direction": "asc"},
            "density": "spacious",
            "layout": "full",
            "columns": [
                {"field": "model", "label": "Model", "type": "text"},
                {"field": "feature_count", "label": "Features", "type": "number"},
                {"field": "log_loss_bits", "label": "Log loss (bits)", "type": "number"},
                {"field": "brier", "label": "Brier", "type": "number"},
                {"field": "auc", "label": "AUC", "type": "number"},
                {"field": "top_decile_lift", "label": "Top-decile lift", "type": "number"},
            ],
        },
        {
            "id": "fresh_comparison_table",
            "title": "Paired fresh-target comparisons",
            "subtitle": "Positive gain favors the first named model; intervals use 100 contiguous blocks and 2,000 resamples",
            "dataset": "fresh_comparisons",
            "sourceId": "pn10b_comparisons_sql",
            "source": {"label": "PN10B paired-comparison query", "path": "analysis/primes/pn10b_report_comparisons.sql", "query": comparisons_query},
            "defaultSort": {"field": "gain_bits_per_event", "direction": "desc"},
            "density": "spacious",
            "layout": "full",
            "columns": [
                {"field": "comparison", "label": "Comparison", "type": "text"},
                {"field": "gain_bits_per_event", "label": "Gain (bits/event)", "type": "number", "movement": True},
                {"field": "ci95_low", "label": "95% CI low", "type": "number"},
                {"field": "ci95_high", "label": "95% CI high", "type": "number"},
                {"field": "positive_blocks", "label": "Positive blocks", "type": "number"},
            ],
        },
        {
            "id": "geometry_population_table",
            "title": "Prime and late-composite child geometry",
            "subtitle": "Post-hoc descriptive summaries; standardized differences near zero mean the paid-gate geometry is shared",
            "dataset": "geometry_population",
            "sourceId": "pn10b_geometry_population_query",
            "source": {"label": "PN10B population-geometry query", "path": "analysis/primes/pn10b_report_geometry_population.sql", "query": geometry_population_query},
            "defaultSort": {"field": "metric", "direction": "asc"},
            "density": "spacious",
            "layout": "full",
            "columns": [
                {"field": "metric", "label": "Child summary", "type": "text"},
                {"field": "prime_mean", "label": "Prime mean", "type": "number"},
                {"field": "prime_median", "label": "Prime median", "type": "number"},
                {"field": "prime_min", "label": "Prime minimum", "type": "number"},
                {"field": "prime_max", "label": "Prime maximum", "type": "number"},
                {"field": "composite_mean", "label": "Late-composite mean", "type": "number"},
                {"field": "standardized_difference", "label": "Standardized difference", "type": "number", "movement": True},
            ],
        },
        {
            "id": "worked_prime_children",
            "title": "Exact children of prime 4,000,000,007",
            "subtitle": "Nine already-paid gate readings; every Phase A plus Phase B closes to 2",
            "dataset": "worked_prime_children",
            "sourceId": "pn10b_worked_prime_query",
            "source": {"label": "PN10B worked-prime query", "path": "analysis/primes/pn10b_report_worked_prime.sql", "query": worked_prime_query},
            "defaultSort": {"field": "gate_rank", "direction": "asc"},
            "density": "spacious",
            "layout": "full",
            "columns": [
                {"field": "gate_rank", "label": "Rank", "type": "number"},
                {"field": "gate_q", "label": "Paid gate q", "type": "number"},
                {"field": "remainder", "label": "Remainder", "type": "number"},
                {"field": "phase_a", "label": "Phase A", "type": "number"},
                {"field": "phase_b", "label": "Phase B", "type": "number"},
                {"field": "signed_orientation", "label": "A - 1", "type": "number", "movement": True},
                {"field": "coupling_to_next_rank", "label": "Coupling to next", "type": "number", "movement": True},
            ],
        },
    ],
    "blocks": [
        {"id": "title", "type": "markdown", "body": "# PN10B Child-Phase Prime Ranking"},
        {
            "id": "technical_summary",
            "type": "markdown",
            "sourceId": "pn10b_results",
            "body": "## The child geometry closed exactly, but prime ranking was null\n\nThe frozen 17-feature ARA child model scored **0.652923909 bits per survivor** on the untouched interval versus **0.652816910** for the empirical parent. Its paired gain was `-0.000106999` bits/event with a 95% interval of `[-0.000241111,+0.000034314]`, and AUC was `0.500307`. Only the closure/leakage criterion passed; the registered verdict is **NULL**.",
        },
        {
            "id": "geometry_reporting_correction",
            "type": "markdown",
            "sourceId": "pn10b_geometry_results",
            "body": "## The benchmark verdict hid a separate event-geometry result\n\nThe NULL remains frozen, but it is not the whole result. At a prime, the parent factor-survival coordinate reaches an exact **1.0 crest**. Every odd raw offset falls to the parity trough near **0.062701**. Inside those prime nodes, paid-gate child A readings span almost the full 0-2 line and average **4.1286 side flips**, yet late composites carry nearly the same child distribution. The event crest is therefore real at the parent coordinate while the tested child coordinate is rich but non-discriminating.",
        },
        {
            "id": "parent_event_interpretation",
            "type": "markdown",
            "sourceId": "pn10b_geometry_trace",
            "body": "## Prime events form a sharp parent crest inside a sieve sawtooth\n\nThe prime-centred trace reaches `1.0` only at offset zero. Odd offsets are even composites with least factor 2; even offsets form smaller shoulders according to their factor and prime-pair structure. This is an exact retrospective geometry map, not an advance prediction, because assigning the central `1.0` requires completing the factor search.",
        },
        {"id": "parent_event_trace_block", "type": "chart", "chartId": "parent_event_trace", "layout": "full"},
        {
            "id": "child_geometry_interpretation",
            "type": "markdown",
            "sourceId": "pn10b_geometry_results",
            "body": "## Population cancellation hides the children inside each prime\n\nAcross **406,494 prime-child readings**, pooled Phase A is `0.9998605`, but individual readings span `0.0000955-1.9999044` and prime-node centroids span `0.4997889-1.4266385`. The worked prime at 4,000,000,007 has centroid `0.5913851` and four side flips. The population ridge is cancellation across locally asymmetric children, not nine quiet children.",
        },
        {"id": "child_rank_trace_block", "type": "chart", "chartId": "child_rank_trace", "layout": "full"},
        {
            "id": "population_control_interpretation",
            "type": "markdown",
            "sourceId": "pn10b_geometry_results",
            "body": "## Late composites share the same paid-gate child geometry\n\nPrime and surviving-composite centroids, spreads, couplings and flip counts differ by less than `0.015` pooled standard deviations. That shared geometry explains the fresh AUC of `0.500307`: the child waves exist, but this proxy does not identify which survivor contains an unseen factor.",
        },
        {"id": "geometry_population_table_block", "type": "table", "tableId": "geometry_population_table", "layout": "full"},
        {
            "id": "worked_prime_interpretation",
            "type": "markdown",
            "sourceId": "pn10b_geometry_examples",
            "body": "## One prime contains strong child asymmetry\n\nPrime 4,000,000,007 has six paid-gate children below the ridge, two above it, and four adjacent orientation changes. The exact row-level values below are the local geometry that a population mean near 1.0 conceals.",
        },
        {"id": "worked_prime_children_block", "type": "table", "tableId": "worked_prime_children", "layout": "full"},
        {
            "id": "key_finding",
            "type": "markdown",
            "sourceId": "pn10b_results",
            "body": "## None of the registered child comparisons produced fresh prime information\n\nThe full ARA representation did not beat the parent, equal-budget raw residues, or the order-scrambled ARA control. The chart shows paired score differences around zero; intervals crossing zero mean the observed differences are not stable across contiguous parts of the fresh number line.",
        },
        {"id": "fresh_gain_chart", "type": "chart", "chartId": "fresh_gains", "layout": "full"},
        {
            "id": "model_table_reading",
            "type": "markdown",
            "sourceId": "pn10b_results",
            "body": "## Established rough-number calibration remained the strongest parent description\n\nBuchstab's constant probability had the lowest fresh log loss (`0.652720245`) because it closely matched overall survivor purity. It is still a constant with AUC `0.5`, so it does not locate individual primes. Every learned model also remained effectively at chance ranking.",
        },
        {"id": "fresh_metrics_block", "type": "table", "tableId": "fresh_metrics", "layout": "full"},
        {
            "id": "scope_definitions",
            "type": "markdown",
            "sourceId": "pn10b_protocol",
            "body": "## Scope, data and metric definitions\n\nPN10B retained only numbers surviving all prime gates `q<=n^0.45`. The fresh target contained 54,275 survivors: 45,166 primes and 9,109 composites. For the nine largest paid gates, `A=2(n mod q)/q`, `B=2-A`, signed orientation `s=A-1`, and adjacent coupling `h=s_j s_(j+1)`. Log loss in bits was primary; Brier, AUC, top-decile lift and calibration error were supporting metrics.",
        },
        {
            "id": "methodology",
            "type": "markdown",
            "sourceId": "pn10b_protocol",
            "body": "## Frozen model and validation design\n\nThe protocol, source, intervals, nine-gate identity, features, `lambda=0.01` logistic model, controls and criteria were SHA-256 frozen before opening the fresh interval. Stage A trained on `[10^6,2x10^6)` and transferred to the PN10 interval near `2x10^9`; Stage B pooled both and scored the untouched interval near `4x10^9`. Paired uncertainty used 100 contiguous blocks and 2,000 fixed-seed bootstrap draws.",
        },
        {"id": "fresh_comparison_table_block", "type": "table", "tableId": "fresh_comparison_table", "layout": "full"},
        {
            "id": "limitations",
            "type": "markdown",
            "sourceId": "pn10b_validation",
            "body": "## The null is specific to this child identity\n\nThe result does not say that ARA cannot be decomposed or that the broader fractal claim is false. It says that exact positions between nine already-tested divisor multiples do not expose a later unseen divisor at this grain. All features are deterministic functions of existing residues and cannot create Shannon information. Independent direct-multiple reconstruction passed **79/79 checks** with zero metric disagreement.",
        },
        {
            "id": "geometry_validation",
            "type": "markdown",
            "sourceId": "pn10b_geometry_validation",
            "body": "## Geometry disclosure validation and boundary\n\nAn independent structural and arithmetic validator passed **12/12 checks**, including event-centre ridge identity, odd-offset parity, A+B closure, modular formulas, landmark totals, example boundaries and figure integrity. These diagnostics were selected after opening the PN10B target, so they cannot promote the registered NULL. They restore descriptive information only.",
        },
        {
            "id": "next_steps",
            "type": "markdown",
            "body": "## Recommended next step\n\nClose this coordinate as a valid geometric decomposition but null prime-ranking instrument. A future registered prime test should change the arithmetic identity rather than tune gate count or model complexity on this target. The strongest options are to predict a rung-level population property, or to define a child relation whose information is not conditionally washed out by sieve survival.",
        },
        {
            "id": "further_questions",
            "type": "markdown",
            "body": "## Further questions\n\nWhy did ARA compact beat raw compact while neither beat the parent? Is there a population-level child statistic that transfers without claiming individual-prime information? Can a theorem show that the paid nonzero residue positions are conditionally uniform enough to explain the null? Which alternative child identity can be frozen without inspecting new gates?",
        },
    ],
}

snapshot = {
    "version": 1,
    "generatedAt": "2026-07-20T15:30:00+10:00",
    "status": "ready",
    "datasets": {
        "fresh_metrics": metric_rows,
        "fresh_comparisons": comparison_rows,
        "event_trace": event_rows,
        "child_rank_profile": rank_rows,
        "geometry_population": population_rows,
        "worked_prime_children": first_prime_table,
    },
}

payload = {"surface": "report", "manifest": manifest, "snapshot": snapshot, "sources": sources}
OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(OUT)
