"""Back the PN34 MCP report artifact with a real, local SQLite query source."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "PN34_FILL_RANK_BUDGET_RESULTS.json"
ARTIFACT = HERE / "PN34_FILL_RANK_BUDGET_REPORT_ARTIFACT.json"
DATABASE = HERE / "PN34_REPORT_SOURCE.sqlite"


def rows(cursor: sqlite3.Cursor, sql: str) -> list[dict]:
    cursor.execute(sql)
    names = [item[0] for item in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]


def main() -> None:
    if DATABASE.exists():
        raise RuntimeError(f"refusing to overwrite {DATABASE.name}")
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    fill_ll = results["benchmark_top1"]["fill_prior"]["log_loss"]
    flat_ll = results["benchmark_top1"]["flat_pn26_prior"]["log_loss"]

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE pn34_summary (calibration TEXT, budgets TEXT, direction TEXT, flat_gain_percent REAL)")
    cursor.execute("INSERT INTO pn34_summary VALUES (?, ?, ?, ?)", ("9 / 9", "6 / 6", "FAIL", 100 * (flat_ll - fill_ll) / flat_ll))
    cursor.execute("CREATE TABLE pn34_coverage (cohort TEXT, depth INTEGER, series TEXT, coverage_percent REAL, predicted REAL, observed REAL, sample_n INTEGER)")
    cursor.execute("CREATE TABLE pn34_benchmarks (method TEXT, brier REAL, log_loss REAL)")
    cursor.execute("CREATE TABLE pn34_cohorts (cohort TEXT, scale_anchor INTEGER, fill_x REAL, predicted_top1 REAL, observed_top1 REAL, phase_a_children INTEGER, phase_b_children INTEGER, rank1 INTEGER, rank2 INTEGER, rank3 INTEGER, over3 INTEGER, sample_n INTEGER)")

    for item in results["cohorts"]:
        for depth in (1, 2, 3):
            predicted = item[f"predicted_top{depth}"]
            observed = item[f"observed_top{depth}"]
            cursor.executemany(
                "INSERT INTO pn34_coverage VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    (item["cohort"].title(), depth, "Predicted", 100 * predicted, predicted, observed, item["rows"]),
                    (item["cohort"].title(), depth, "Observed", 100 * observed, predicted, observed, item["rows"]),
                ],
            )
        counts = item["rank_counts_1_2_3_over3"]
        cursor.execute(
            "INSERT INTO pn34_cohorts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (item["cohort"].title(), item["scale_anchor"], item["remaining_fill_x"], item["predicted_top1"], item["observed_top1"], item["phase_a_count"], item["phase_b_count"], counts[0], counts[1], counts[2], counts[3], item["rows"]),
        )
    for key, label in (("fill_prior", "Fill prior"), ("flat_pn26_prior", "Flat PN26 prior"), ("conditional_pnt_prior", "Conditional PNT")):
        item = results["benchmark_top1"][key]
        cursor.execute("INSERT INTO pn34_benchmarks VALUES (?, ?, ?)", (label, item["brier"], item["log_loss"]))
    connection.commit()

    queries = {
        "headline": "SELECT calibration, budgets, direction, flat_gain_percent FROM pn34_summary",
        "coverage": "SELECT cohort || ' / ' || depth AS cohort_depth, cohort, depth, series, coverage_percent, predicted, observed, sample_n FROM pn34_coverage ORDER BY CASE cohort WHEN 'Low' THEN 1 WHEN 'Middle' THEN 2 ELSE 3 END, depth, series DESC",
        "benchmarks": "SELECT method, brier, log_loss FROM pn34_benchmarks ORDER BY log_loss ASC",
        "cohorts": "SELECT cohort, scale_anchor, fill_x, predicted_top1, observed_top1, phase_a_children, phase_b_children, rank1, rank2, rank3, over3, sample_n FROM pn34_cohorts ORDER BY scale_anchor ASC",
    }
    artifact["snapshot"]["datasets"] = {name: rows(cursor, sql) for name, sql in queries.items()}
    connection.close()

    def query_source(source_id: str, label: str, sql: str, table: str, description: str, definitions: list[str]) -> dict:
        return {
            "id": source_id,
            "label": label,
            "path": "analysis/primes/PN34_REPORT_SOURCE.sqlite",
            "query": {
                "id": source_id,
                "engine": "sqlite",
                "language": "sql",
                "executed_at": "2026-07-22T20:13:00+10:00",
                "description": description,
                "sql": sql,
                "tables_used": [table],
                "filters": ["PN34 fresh cohorts only", "2,000 deterministic anchors per scale"],
                "metric_definitions": definitions,
            },
        }

    sources = [
        query_source("pn34_headline", "PN34 headline endpoint summary", queries["headline"], "pn34_summary", "Return the frozen endpoint pass counts and benchmark gain.", ["Calibration cells passed: count of scale-by-depth cells within frozen absolute-error tolerances.", "Flat gain: relative log-loss reduction versus the pooled PN26 development prior."]),
        query_source("pn34_coverage", "PN34 predicted and observed rank coverage", queries["coverage"], "pn34_coverage", "Return tidy predicted/observed rank coverage for all fresh cohorts and depths.", ["Coverage: share of 2,000 anchors whose exact next prime is contained by the retained Phase A rank depth.", "Predicted top-k: 1-(1-1/R_B)^k, with R_B the omitted Phase B inverse-density product."]),
        query_source("pn34_benchmarks", "PN34 top-one probability benchmarks", queries["benchmarks"], "pn34_benchmarks", "Return Brier score and log loss for the three registered/descriptive top-one priors.", ["Log loss and Brier use one binary row per anchor: actual next prime equals first Phase A quiet state."]),
        query_source("pn34_cohorts", "PN34 candidate-rank counts", queries["cohorts"], "pn34_cohorts", "Return exact rank counts and parent metadata for each fresh scale.", ["Beyond rank 3 counts anchors whose exact next prime was not in the three sealed Phase A quiet candidates."]),
        {"id": "pn34_results", "label": "PN34 independently scored result file", "path": "analysis/primes/PN34_FILL_RANK_BUDGET_RESULTS.json"},
        {"id": "pn34_protocol", "label": "PN34 frozen protocol", "path": "analysis/primes/PN34_FILL_RANK_BUDGET_PROTOCOL_v1_FROZEN.md"},
    ]
    artifact["manifest"]["sources"] = sources
    for card in artifact["manifest"]["cards"]:
        card["sourceId"] = "pn34_headline"
    artifact["manifest"]["charts"][0]["sourceId"] = "pn34_coverage"
    artifact["manifest"]["charts"][1]["sourceId"] = "pn34_benchmarks"
    artifact["manifest"]["tables"][0]["sourceId"] = "pn34_cohorts"
    ARTIFACT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(DATABASE)
    print(ARTIFACT)


if __name__ == "__main__":
    main()
