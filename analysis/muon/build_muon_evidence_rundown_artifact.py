from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "muon_evidence_rundown_2026-08-18"


def rows(name: str):
    with (OUT / name).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


landmarks = rows("MUON_POPULATION_LANDMARKS.csv")
for row in landmarks:
    row["order"] = int(row["order"])
    row["time_us"] = float(row["time_us"])
    row["cumulative_ara"] = float(row["cumulative_ara"])

ladder = rows("MUON_EVIDENCE_LADDER.csv")

sources = [
    {
        "id": "t399_landmarks",
        "label": "T399 native population landmarks",
        "path": "analysis/muon/T399_child_half_precrest_sequence/T399_NATIVE_LANDMARKS.csv",
        "query": {
            "engine": "python",
            "language": "python",
            "description": "Frozen T399 fitted-population landmark order and cumulative ARA placement.",
            "tables_used": ["T399_NATIVE_LANDMARKS.csv"],
            "filters": ["Best-fit COHERENT population identity; not an individual muon trajectory."],
            "metric_definitions": ["Cumulative ARA is the integrated prompt-plus-delayed fitted release compressed to 0-2."],
        },
    },
    {
        "id": "muon_ladder",
        "label": "T371-T409 evidence-grain review",
        "path": "analysis/muon/muon_evidence_rundown_2026-08-18/MUON_EVIDENCE_LADDER.csv",
        "query": {
            "engine": "document-review",
            "language": "text",
            "description": "Evidence-graded synthesis of the saved T371-T409 findings and session record.",
            "tables_used": ["MUON_EVIDENCE_LADDER.csv"],
            "filters": ["Preserves population, event-linked, detector-template and truth-model boundaries."],
        },
    },
    {
        "id": "t408_individual",
        "label": "T408 nested individual windows",
        "path": "analysis/muon/T408_NESTED_WINDOWS_INDIVIDUAL_MUON_FINDINGS_2026-08-18.md",
        "query": {
            "description": "Latest directional individual-event result after parent conditioning and child decompression.",
            "tables_used": ["T408_NESTED_WINDOWS_INDIVIDUAL_MUON_FINDINGS_2026-08-18.md"],
        },
    },
    {
        "id": "rundown_record",
        "label": "Muon evidence rundown",
        "path": "analysis/muon/MUON_TEST_RUNDOWN_2026-08-18.md",
        "query": {
            "description": "Reader-facing audit distinguishing population lead-up, decay-product split and individual prediction.",
            "tables_used": ["MUON_TEST_RUNDOWN_2026-08-18.md"],
        },
    },
]

title = "Muon tests: a population lead-up was recovered, not an individual emission movie"

manifest = {
    "version": 1,
    "surface": "report",
    "title": title,
    "description": "Evidence-graded rundown of the T371-T409 muon and neutrino-handover tests.",
    "generatedAt": datetime.now(timezone.utc).isoformat(),
    "sources": sources,
    "blocks": [
        {"id": "title", "type": "markdown", "body": f"# {title}"},
        {
            "id": "summary",
            "type": "markdown",
            "sourceId": "rundown_record",
            "body": "## Technical summary\n\n**Yes, the tests recovered a split and a lead-up, but not as two neutrinos appearing at separately measured times.** The strongest lead-up is a fitted population sequence. The strongest split is charged daughter versus a joint neutral branch, followed by an asymmetric two-neutrino decomposition in templates and Standard-Model truth models. Population spin anti-phase and daughter orientation are also recovered. What remains unconfirmed is an individual pre-decay countdown that predicts one named muon's release.",
        },
        {
            "id": "population_text",
            "type": "markdown",
            "sourceId": "t399_landmarks",
            "body": "## The lead-up we actually recovered\n\nThe fitted COHERENT population moves through four ordered landmarks: prompt crest, equality of prompt and delayed rates, cumulative child-half, and the delayed muon-decay-neutrino crest. Read this as an ensemble release history, not one muon's internal movie. T399 recovered the order in the best-fit identity but missed two predeclared high-stringency robustness gates, so the sequence is directional rather than universal.",
        },
        {"id": "population_chart", "type": "chart", "chartId": "landmark_chart"},
        {
            "id": "ladder_text",
            "type": "markdown",
            "sourceId": "muon_ladder",
            "body": "## The evidence changes as we move down the rung\n\nPopulation handovers, spin anti-phase and daughter-allocation relations are the strongest results. Event-linked tests are stricter: the incoming detector coordinates usually failed to improve individual daughter-time prediction, while T408 supplied a small, directionally positive nested-child signal that did not clear its full frozen confirmation rule. This is why population lead-up and individual birth prediction must remain separate claims.",
        },
        {"id": "ladder_table", "type": "table", "tableId": "evidence_table"},
        {
            "id": "dots",
            "type": "markdown",
            "sourceId": "t408_individual",
            "body": "## What the individual dots contain\n\nEach T408/T409 dot links an incoming stopped-muon detector record to a later charged-daughter candidate. A genuine decay implies that the decay products existed, but neither neutrino is plotted or directly measured. The dots can test whether incoming relations change the probability of later timing windows; they cannot show the neutrino waveform or distinguish the two neutral children.",
        },
        {
            "id": "limits",
            "type": "markdown",
            "sourceId": "rundown_record",
            "body": "## The corrected conclusion\n\nThe project has evidence for a structured population approach to the muon-decay handover and for multiple nested daughter relations. It has not shown that the two neutrinos are born in temporally separated stages, nor that one living muon's decay instant is predictable. The decisive dataset must join repeated pre-decay spin or another dynamic state, charged-daughter energy/direction, neutral-sensitive timing or missing momentum, and the held-out decay time under one event key.",
        },
        {
            "id": "questions",
            "type": "markdown",
            "body": "## Further questions\n\n- Does T408's nested-child improvement replicate on untouched dates or another detector?\n- Can an event-level spin/polarisation axis supply the missing same-scale anti-phase?\n- Can a neutral-sensitive or missing-momentum record turn the current distribution lock into a true individual Information-cubed lock?",
        },
    ],
    "charts": [
        {
            "id": "landmark_chart",
            "title": "Fitted population landmarks before the delayed-release crest",
            "subtitle": "COHERENT best-fit population identity; cumulative ARA versus time after the source pulse.",
            "type": "line",
            "dataset": "landmarks",
            "sourceId": "t399_landmarks",
            "source": {
                "query": {
                    "sql": "SELECT \"order\", landmark, time_us, cumulative_ara, evidence_grain FROM \"MUON_POPULATION_LANDMARKS.csv\" ORDER BY \"order\" ASC",
                    "description": "Read the four frozen T399 population landmarks in chronological order from the reviewed CSV extract.",
                },
                "tables": ["MUON_POPULATION_LANDMARKS.csv"],
            },
            "palette": {"kind": "categorical", "name": "blue-gold"},
            "encodings": {
                "x": {"field": "time_us", "type": "quantitative", "label": "Time after source pulse (microseconds)"},
                "y": {"field": "cumulative_ara", "type": "quantitative", "label": "Cumulative population ARA (0-2)"},
                "tooltip": [
                    {"field": "landmark", "type": "nominal", "label": "Landmark"},
                    {"field": "cumulative_ara", "type": "quantitative", "label": "Cumulative ARA"},
                    {"field": "evidence_grain", "type": "nominal", "label": "Evidence grain"},
                ],
            },
        }
    ],
    "tables": [
        {
            "id": "evidence_table",
            "title": "Evidence ladder across the muon programme",
            "subtitle": "Saved T371-T409 results grouped by measurement grain and claim ceiling.",
            "dataset": "ladder",
            "sourceId": "muon_ladder",
            "source": {
                "query": {
                    "sql": "SELECT test_group, grain, measured_or_modelled, result, status, claim_boundary FROM \"MUON_EVIDENCE_LADDER.csv\" ORDER BY test_group ASC",
                    "description": "Read the evidence-graded T371-T409 audit rows from the reviewed CSV synthesis.",
                },
                "tables": ["MUON_EVIDENCE_LADDER.csv"],
            },
            "defaultSort": {"field": "test_group", "direction": "asc"},
            "columns": [
                {"field": "test_group", "label": "Tests", "type": "text"},
                {"field": "grain", "label": "Evidence grain", "type": "text"},
                {"field": "measured_or_modelled", "label": "What was measured/modelled", "type": "text"},
                {"field": "result", "label": "Result", "type": "text"},
                {"field": "status", "label": "Status", "type": "text"},
                {"field": "claim_boundary", "label": "Claim boundary", "type": "text"},
            ],
        }
    ],
}

artifact = {
    "surface": "report",
    "manifest": manifest,
    "snapshot": {
        "version": 1,
        "status": "ready",
        "generatedAt": manifest["generatedAt"],
        "datasets": {"landmarks": landmarks, "ladder": ladder},
        "accessIssues": [],
    },
    "sources": sources,
    "package_info": {
        "artifact_name": "Muon evidence rundown",
        "artifact_version": "1.0.0",
        "delivery": "mcp-app",
    },
}

(OUT / "artifact.json").write_text(json.dumps(artifact, indent=2), encoding="utf-8")
print(json.dumps({"artifact": str(OUT / "artifact.json"), "landmarks": len(landmarks), "ladder": len(ladder)}))
