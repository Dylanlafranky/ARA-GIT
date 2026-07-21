"""Build the bounded Data Analytics report payload for PN10."""

from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "PN10_REPORT_ARTIFACT.json"

path_rows = list(csv.DictReader((HERE / "PN10_FACTOR_SPHERE_PATHS.csv").open(encoding="utf-8")))
transfer_rows = list(csv.DictReader((HERE / "PN10_FACTOR_SPHERE_TRANSFER.csv").open(encoding="utf-8")))
result = json.loads((HERE / "PN10_FACTOR_SPHERE_RESULTS.json").read_text(encoding="utf-8"))

purity_seed = [
    {
        "cutoff": float(row["cutoff"]),
        "interval": row["interval"],
        "prime_purity": float(row["prime_purity"]),
        "survivors": int(row["survivors"]),
        "remaining_composites": int(row["remaining_composites"]),
    }
    for row in path_rows
]
transfer_seed = [
    {
        "cutoff": float(row["cutoff"]),
        "method": row["method"],
        "absolute_q": int(row["absolute_q"]) if row["absolute_q"] else None,
        "development_purity": float(row["development_purity"]),
        "evaluation_purity": float(row["evaluation_purity"]),
        "purity_transfer_error": float(row["purity_transfer_error"]),
        "evaluation_brier": float(row["evaluation_brier"]),
        "evaluation_remaining_composites": int(row["evaluation_remaining_composites"]),
    }
    for row in transfer_rows
]

purity_sql = (HERE / "pn10_report_purity_path.sql").read_text(encoding="utf-8")
transfer_sql = (HERE / "pn10_report_transfer.sql").read_text(encoding="utf-8")
connection = sqlite3.connect(":memory:")
connection.row_factory = sqlite3.Row
connection.execute("CREATE TABLE pn10_purity_path (cutoff REAL, interval TEXT, prime_purity REAL, survivors INTEGER, remaining_composites INTEGER)")
connection.executemany(
    "INSERT INTO pn10_purity_path VALUES (:cutoff, :interval, :prime_purity, :survivors, :remaining_composites)",
    purity_seed,
)
connection.execute("CREATE TABLE pn10_transfer (cutoff REAL, method TEXT, absolute_q INTEGER, development_purity REAL, evaluation_purity REAL, purity_transfer_error REAL, evaluation_brier REAL, evaluation_remaining_composites INTEGER)")
connection.executemany(
    "INSERT INTO pn10_transfer VALUES (:cutoff, :method, :absolute_q, :development_purity, :evaluation_purity, :purity_transfer_error, :evaluation_brier, :evaluation_remaining_composites)",
    transfer_seed,
)
purity_path = [dict(row) for row in connection.execute(purity_sql).fetchall()]
transfer = [dict(row) for row in connection.execute(transfer_sql).fetchall()]
connection.close()

purity_source = {
    "label": "PN10 purity-path artifact query",
    "path": "analysis/primes/pn10_report_purity_path.sql",
    "query": {
        "sql": purity_sql,
        "language": "SQL",
        "engine": "SQLite",
        "tables_used": ["pn10_purity_path"],
        "description": "Select the reviewed cutoff-by-interval prime-purity path used by the report chart.",
        "metric_definitions": ["prime_purity = exact prime count divided by surviving integer count at the registered ARA cutoff"],
    },
}
transfer_source = {
    "label": "PN10 transfer artifact query",
    "path": "analysis/primes/pn10_report_transfer.sql",
    "query": {
        "sql": transfer_sql,
        "language": "SQL",
        "engine": "SQLite",
        "tables_used": ["pn10_transfer"],
        "description": "Select the reviewed development-to-fresh transfer metrics used by the report chart and table.",
        "metric_definitions": [
            "purity_transfer_error = absolute difference between development and evaluation survivor prime purity",
            "evaluation_brier = mean squared error of prime probability across all one million fresh integers",
        ],
    },
}

sources = [
    {"id": "pn10_results", "label": "PN10 machine-readable results", "path": "analysis/primes/PN10_FACTOR_SPHERE_RESULTS.json"},
    {"id": "pn10_protocol", "label": "PN10 frozen protocol", "path": "analysis/primes/PN10_FACTOR_SPHERE_PRIME_RECOVERY_PROTOCOL.md"},
    {"id": "pn10_validation", "label": "PN10 independent validation", "path": "analysis/primes/PN10_FACTOR_SPHERE_VALIDATION.json"},
    {"id": "pn10_purity_sql", "label": "PN10 purity-path artifact query", "path": "analysis/primes/pn10_report_purity_path.sql", "query": purity_source["query"]},
    {"id": "pn10_transfer_sql", "label": "PN10 transfer artifact query", "path": "analysis/primes/pn10_report_transfer.sql", "query": transfer_source["query"]},
]

manifest = {
    "version": 1,
    "surface": "report",
    "title": "PN10 Factor-Sphere Prime Recovery",
    "description": "Exact ARA factor-ridge prime recovery plus fresh cross-scale early-ridge transfer.",
    "generatedAt": "2026-07-20T12:00:00+10:00",
    "sources": sources,
    "charts": [
        {
            "id": "purity_path",
            "title": "Prime purity through the factor-ridge walk",
            "subtitle": "Both scales converge to exact prime purity at the 1.0 ridge",
            "type": "line",
            "dataset": "purity_path",
            "sourceId": "pn10_results",
            "source": purity_source,
            "encodings": {
                "x": {"field": "cutoff", "type": "quantitative", "label": "ARA cutoff"},
                "y": {"field": "prime_purity", "type": "quantitative", "label": "Prime purity"},
                "color": {"field": "interval", "type": "nominal", "label": "Interval"},
                "tooltip": [
                    {"field": "survivors", "type": "quantitative", "label": "Survivors"},
                    {"field": "remaining_composites", "type": "quantitative", "label": "Composites left"},
                ],
            },
            "layout": "full",
        },
        {
            "id": "brier_by_cutoff",
            "title": "Fresh-range Brier score by early-ridge cutoff",
            "subtitle": "The identity-scaled factor coordinate transfers better than a fixed absolute divisor cutoff",
            "type": "bar",
            "dataset": "transfer",
            "sourceId": "pn10_results",
            "source": transfer_source,
            "encodings": {
                "x": {"field": "cutoff", "type": "nominal", "label": "Early-ridge cutoff"},
                "y": {"field": "evaluation_brier", "type": "quantitative", "label": "Brier score"},
                "color": {"field": "method", "type": "nominal", "label": "Method"},
                "tooltip": [
                    {"field": "purity_transfer_error", "type": "quantitative", "label": "Purity transfer error"},
                    {"field": "evaluation_remaining_composites", "type": "quantitative", "label": "Composites left"},
                ],
            },
            "layout": "full",
        },
    ],
    "tables": [
        {
            "id": "transfer_table",
            "title": "Early-ridge transfer results",
            "subtitle": "Development calibration applied once to the fresh evaluation interval",
            "dataset": "transfer",
            "sourceId": "pn10_results",
            "source": transfer_source,
            "defaultSort": {"field": "cutoff", "direction": "asc"},
            "density": "spacious",
            "layout": "full",
            "columns": [
                {"field": "cutoff", "label": "Cutoff", "type": "number"},
                {"field": "method", "label": "Method", "type": "text"},
                {"field": "development_purity", "label": "Development purity", "type": "percent"},
                {"field": "evaluation_purity", "label": "Fresh purity", "type": "percent"},
                {"field": "purity_transfer_error", "label": "Transfer error", "type": "percent"},
                {"field": "evaluation_brier", "label": "Brier", "type": "number"},
                {"field": "evaluation_remaining_composites", "label": "Composites left", "type": "number"},
            ],
        }
    ],
    "blocks": [
        {
            "id": "title",
            "type": "markdown",
            "body": "# PN10 Factor-Sphere Prime Recovery\n\n**Result:** Exact at the 1.0 factor ridge; strongly calibrated but not exact before it. **Validation:** 64/64 checks passed.",
        },
        {
            "id": "technical_summary",
            "type": "markdown",
            "sourceId": "pn10_results",
            "body": "## The frozen rule recovered every prime in the fresh million-number interval\n\nThe ARA factor walk classified all **46,903 primes** in `[2,000,000,000, 2,001,000,000)` with zero false positives or negatives. Its factor-pair reflection closed to `4.44 x 10^-16`, and 1,229 prime squares landed exactly at the `1.0` ridge. The exact rule is classical trial division through `sqrt(n)` expressed in a reversible 0-2 coordinate, not a faster prime algorithm.",
        },
        {"id": "purity_chart", "type": "chart", "chartId": "purity_path", "layout": "full"},
        {
            "id": "transfer_finding",
            "type": "markdown",
            "sourceId": "pn10_results",
            "body": "## Partial factor depth transferred across a scale jump\n\nAt cutoff `0.90`, development survivor purity was **83.7346%** and fresh purity was **83.5286%**, only **0.206 percentage points** apart. The fixed absolute divisor control missed by **29.735 percentage points**. Across all four frozen cutoffs, ARA's mean Brier score was `0.021150` versus `0.034329` for fixed-Q.",
        },
        {"id": "brier_chart", "type": "chart", "chartId": "brier_by_cutoff", "layout": "full"},
        {"id": "transfer_table_block", "type": "table", "tableId": "transfer_table", "layout": "full"},
        {
            "id": "scope_method",
            "type": "markdown",
            "sourceId": "pn10_protocol",
            "body": "## Scope and method\n\nFor factor candidate `d`, PN10 used `x_n(d)=2 log(d)/log(n)`. The endpoints are `d=1` and `d=n`; `d=sqrt(n)` is the ridge. Factor partners satisfy `x_n(d)+x_n(n/d)=2`. The development and fresh intervals each contained one million consecutive raw integers. No Fourier transform, smoothing, SVD, NMF or learned feature extraction was used.",
        },
        {
            "id": "limitations",
            "type": "markdown",
            "sourceId": "pn10_validation",
            "body": "## The pre-ridge method remains probabilistic\n\nAt cutoff `0.90`, **9,249 composites** remained among 56,152 survivors. The one-coordinate walk therefore cannot yet identify each prime early. Standard number theory also uses the square-root boundary and relative logarithmic factor scale, so the exact recovery is a crosswalk and the transfer is compatible with established rough-number structure; neither uniquely establishes universal ARA geometry.",
        },
        {
            "id": "next_steps",
            "type": "markdown",
            "body": "## Next test: resolve the hidden pre-ridge composites\n\nFreeze a parent factor-depth coordinate plus two reversible child relations around neighbouring untested gates, then score individual survivors on a new interval against fixed-complexity number-theory controls. The target is not another exact ridge recovery; it is whether native child geometry can distinguish the 9,249 hidden composites without simply continuing trial division.",
        },
        {
            "id": "questions",
            "type": "markdown",
            "body": "## Further questions\n\nCan a second native relation rank pre-ridge survivors? Does calibration remain stable over additional scale jumps? Can the same coordinate reduce computation rather than only re-express factor progress? Which result, if any, differs from standard rough-number predictions under an equal-information comparison?",
        },
    ],
}

snapshot = {
    "version": 1,
    "generatedAt": "2026-07-20T12:00:00+10:00",
    "status": "ready",
    "datasets": {"purity_path": purity_path, "transfer": transfer},
}

payload = {"surface": "report", "manifest": manifest, "snapshot": snapshot, "sources": sources}
OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(OUT)
