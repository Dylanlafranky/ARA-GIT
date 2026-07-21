"""Build the bounded Data Analytics report artifact for PN10C."""

from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path


HERE=Path(__file__).resolve().parent
OUT=HERE/"PN10C_REPORT_ARTIFACT.json"
result=json.loads((HERE/"PN10C_MOD6_THREE_LANE_RESULTS.json").read_text(encoding="utf-8"))


def read_csv(name: str) -> list[dict[str,str]]:
    with (HERE/name).open(newline="",encoding="utf-8") as handle: return list(csv.DictReader(handle))


offset_seed=read_csv("PN10C_MOD6_OFFSET_PROFILE.csv")
lane_seed=read_csv("PN10C_MOD6_LANE_SUMMARY.csv")
matrix_seed=read_csv("PN10C_MOD30_BLACK_CHILD_MATRIX.csv")

conn=sqlite3.connect(":memory:"); conn.row_factory=sqlite3.Row
conn.execute("CREATE TABLE pn10c_offset_profile (center_group TEXT, center_mod6 INTEGER, offset INTEGER, offset_lane_mod6 TEXT, center_count INTEGER, parent_progress_mean REAL, parent_progress_median REAL, prime_rate REAL, survivor_rate REAL, divisible_by_3_rate REAL, divisible_by_5_rate REAL)")
conn.executemany("INSERT INTO pn10c_offset_profile VALUES (:center_group,:center_mod6,:offset,:offset_lane_mod6,:center_count,:parent_progress_mean,:parent_progress_median,:prime_rate,:survivor_rate,:divisible_by_3_rate,:divisible_by_5_rate)",offset_seed)
conn.execute("CREATE TABLE pn10c_lane_summary (center_group TEXT, center_mod6 INTEGER, offset_lane_mod6 INTEGER, direction TEXT, center_count INTEGER, offset_count_per_center INTEGER, observation_count INTEGER, parent_progress_mean REAL, parent_progress_sd REAL, parent_progress_median REAL, prime_rate REAL, survivor_rate REAL, divisible_by_3_rate REAL, divisible_by_5_rate REAL)")
conn.executemany("INSERT INTO pn10c_lane_summary VALUES (:center_group,:center_mod6,:offset_lane_mod6,:direction,:center_count,:offset_count_per_center,:observation_count,:parent_progress_mean,:parent_progress_sd,:parent_progress_median,:prime_rate,:survivor_rate,:divisible_by_3_rate,:divisible_by_5_rate)",lane_seed)
conn.execute("CREATE TABLE pn10c_mod30_matrix (center_group TEXT, center_mod5 INTEGER, black_child_m_mod5 INTEGER, offset_mod30 INTEGER, predicted_factor5_collision INTEGER, center_count INTEGER, offset_count_per_center INTEGER, observation_count INTEGER, parent_progress_mean REAL, parent_progress_median REAL, prime_rate REAL, survivor_rate REAL, divisible_by_5_rate REAL)")
conn.executemany("INSERT INTO pn10c_mod30_matrix VALUES (:center_group,:center_mod5,:black_child_m_mod5,:offset_mod30,:predicted_factor5_collision,:center_count,:offset_count_per_center,:observation_count,:parent_progress_mean,:parent_progress_median,:prime_rate,:survivor_rate,:divisible_by_5_rate)",matrix_seed)

contrast_rows=[]
interpretations={
    "red_blue_swap":"Positive means the two coloured lanes exchange high/low roles as frozen.",
    "black_orientation_difference":"Near zero means black is invariant across the two centre orientations.",
    "black_minus_admissible_colour":"Positive would support a stronger independent black lane; the observed value is negative.",
    "black_minus_pooled_red_blue":"Positive explains why black appears higher before orientation conditioning.",
    "mod30_eligible_minus_suppressed":"Positive measures the rotating factor-5 child trough inside black.",
}
for order,(name,row) in enumerate(result["headline_contrasts"].items(),1):
    contrast_rows.append({"display_order":order,"contrast":name.replace("_"," ").title(),"estimate":row["estimate"],"ci95_low":row["ci95_low"],"ci95_high":row["ci95_high"],"standardized_difference":row.get("standardized_difference"),"interpretation":interpretations[name]})
conn.execute("CREATE TABLE pn10c_contrasts (display_order INTEGER, contrast TEXT, estimate REAL, ci95_low REAL, ci95_high REAL, standardized_difference REAL, interpretation TEXT)")
conn.executemany("INSERT INTO pn10c_contrasts VALUES (:display_order,:contrast,:estimate,:ci95_low,:ci95_high,:standardized_difference,:interpretation)",contrast_rows)

sqls={name:(HERE/name).read_text(encoding="utf-8") for name in ("pn10c_report_offset_trace.sql","pn10c_report_lane_summary.sql","pn10c_report_mod30_matrix.sql","pn10c_report_contrasts.sql")}
offset_rows=[dict(r) for r in conn.execute(sqls["pn10c_report_offset_trace.sql"]).fetchall()]
lane_rows=[dict(r) for r in conn.execute(sqls["pn10c_report_lane_summary.sql"]).fetchall()]
matrix_rows=[dict(r) for r in conn.execute(sqls["pn10c_report_mod30_matrix.sql"]).fetchall()]
contrast_rows=[dict(r) for r in conn.execute(sqls["pn10c_report_contrasts.sql"]).fetchall()]
conn.close()


def query(sql_name,tables,description,definitions):
    return {"sql":sqls[sql_name],"language":"SQL","engine":"SQLite","tables_used":tables,"description":description,"filters":["integer interval = [4000000000,4001000000)","post-hoc structural diagnostic","prime centres reserve +-150 boundary"],"metric_definitions":definitions}


q_offset=query("pn10c_report_offset_trace.sql",["pn10c_offset_profile"],"Select the orientation-conditioned prime event traces for the visible +-30 offset window.",["parent_progress_mean = mean of 1 for primes or 2*log(least_prime_factor)/log(n) for composites","centre orientation = centre prime modulo 6"])
q_lane=query("pn10c_report_lane_summary.sql",["pn10c_lane_summary"],"Select the six prime-centred mod-6 lane means after conditioning on centre orientation.",["lane = nonzero even offset modulo 6","prime_rate = share of all aligned centre-offset observations that are prime"])
q_matrix=query("pn10c_report_mod30_matrix.sql",["pn10c_mod30_matrix"],"Select the factor-5 child matrix inside nonzero offsets divisible by 6.",["black child m = (offset/6) modulo 5","predicted collision = 1 when (centre mod5 + m mod5) mod5 = 0"])
q_contrast=query("pn10c_report_contrasts.sql",["pn10c_contrasts"],"Select frozen PN10C contrasts and contiguous-block bootstrap intervals.",["red/blue swap = half the sum of the two orientation-conditioned high-minus-low differences","intervals = percentile 95% intervals from 2000 resamples of 100 contiguous centre blocks"])

sources=[
    {"id":"pn10c_protocol","label":"PN10C frozen diagnostic protocol","path":"analysis/primes/PN10C_MOD6_THREE_LANE_COUPLING_PROTOCOL.md"},
    {"id":"pn10c_results","label":"PN10C machine-readable results","path":"analysis/primes/PN10C_MOD6_THREE_LANE_RESULTS.json"},
    {"id":"pn10c_validation","label":"PN10C independent validation","path":"analysis/primes/PN10C_MOD6_THREE_LANE_VALIDATION.json"},
    {"id":"pn10c_offset_query","label":"PN10C orientation-conditioned trace query","path":"analysis/primes/pn10c_report_offset_trace.sql","query":q_offset},
    {"id":"pn10c_lane_query","label":"PN10C mod-6 lane summary query","path":"analysis/primes/pn10c_report_lane_summary.sql","query":q_lane},
    {"id":"pn10c_matrix_query","label":"PN10C mod-30 child matrix query","path":"analysis/primes/pn10c_report_mod30_matrix.sql","query":q_matrix},
    {"id":"pn10c_contrast_query","label":"PN10C frozen contrast query","path":"analysis/primes/pn10c_report_contrasts.sql","query":q_contrast},
]

manifest={
    "version":1,"surface":"report","title":"PN10C Three-Lane Prime Geometry","description":"Post-hoc diagnostic of the red, blue and black lane families marked in the PN10B parent trace.","generatedAt":"2026-07-20T20:00:00+10:00","sources":sources,
    "charts":[
        {"id":"orientation_trace","title":"Parent factor progress around prime centres","subtitle":"Prime centres split by mod-6 orientation; raw offsets -30 to +30","type":"line","dataset":"orientation_trace","sourceId":"pn10c_offset_query","source":{"label":"PN10C orientation-conditioned trace query","path":"analysis/primes/pn10c_report_offset_trace.sql","query":q_offset},"encodings":{"x":{"field":"offset","type":"quantitative","label":"Raw-integer offset"},"y":{"field":"parent_progress_mean","type":"quantitative","label":"Mean parent factor progress"},"color":{"field":"center_orientation","type":"nominal","label":"Centre orientation"},"tooltip":[{"field":"prime_rate","type":"quantitative","label":"Prime rate"},{"field":"survivor_rate","type":"quantitative","label":"c=.90 survivor rate"},{"field":"divisible_by_3_rate","type":"quantitative","label":"Divisible by 3"},{"field":"center_count","type":"quantitative","label":"Centres"}]},"layout":"full"},
        {"id":"lane_means","title":"Mod-6 lane means after centre-orientation conditioning","subtitle":"Black is compared with the coloured branch that remains admissible in each orientation","type":"bar","dataset":"lane_summary","sourceId":"pn10c_lane_query","source":{"label":"PN10C mod-6 lane summary query","path":"analysis/primes/pn10c_report_lane_summary.sql","query":q_lane},"encodings":{"x":{"field":"lane_label","type":"nominal","label":"Centre orientation and offset lane"},"y":{"field":"parent_progress_mean","type":"quantitative","label":"Mean parent factor progress"},"tooltip":[{"field":"prime_rate","type":"quantitative","label":"Prime rate"},{"field":"divisible_by_3_rate","type":"quantitative","label":"Divisible by 3"},{"field":"observation_count","type":"quantitative","label":"Aligned observations"}]},"layout":"full"},
        {"id":"contrast_chart","title":"Frozen three-lane and child-decomposition contrasts","subtitle":"Positive and negative estimates retain their signed diagnostic meaning","type":"bar","dataset":"contrasts","sourceId":"pn10c_contrast_query","source":{"label":"PN10C frozen contrast query","path":"analysis/primes/pn10c_report_contrasts.sql","query":q_contrast},"encodings":{"x":{"field":"contrast","type":"nominal","label":"Frozen contrast"},"y":{"field":"estimate","type":"quantitative","label":"Parent-progress contrast"},"tooltip":[{"field":"ci95_low","type":"quantitative","label":"95% CI low"},{"field":"ci95_high","type":"quantitative","label":"95% CI high"},{"field":"interpretation","type":"nominal","label":"Meaning"}]},"layout":"full"},
    ],
    "tables":[
        {"id":"lane_table","title":"Prime-centred mod-6 lane detail","subtitle":"All nonzero offsets from -150 to +150, pooled within each residue lane","dataset":"lane_summary","sourceId":"pn10c_lane_query","source":{"label":"PN10C mod-6 lane summary query","path":"analysis/primes/pn10c_report_lane_summary.sql","query":q_lane},"defaultSort":{"field":"lane_label","direction":"asc"},"density":"spacious","layout":"full","columns":[{"field":"lane_label","label":"Centre and lane","type":"text"},{"field":"parent_progress_mean","label":"Mean progress","type":"number"},{"field":"prime_rate","label":"Prime rate","type":"number"},{"field":"survivor_rate","label":"Survivor rate","type":"number"},{"field":"divisible_by_3_rate","label":"Divisible by 3","type":"number"},{"field":"divisible_by_5_rate","label":"Divisible by 5","type":"number"}]},
        {"id":"matrix_table","title":"Black-lane mod-30 child matrix","subtitle":"One factor-5 collision rotates across each centre-mod-5 row","dataset":"mod30_matrix","sourceId":"pn10c_matrix_query","source":{"label":"PN10C mod-30 child matrix query","path":"analysis/primes/pn10c_report_mod30_matrix.sql","query":q_matrix},"defaultSort":{"field":"center_mod5","direction":"asc"},"density":"spacious","layout":"full","columns":[{"field":"center_mod5","label":"Centre mod 5","type":"number"},{"field":"black_child_m_mod5","label":"Child m mod 5","type":"number"},{"field":"predicted_factor5_collision","label":"Factor-5 collision","type":"number"},{"field":"parent_progress_mean","label":"Mean progress","type":"number"},{"field":"prime_rate","label":"Prime rate","type":"number"},{"field":"divisible_by_5_rate","label":"Divisible by 5","type":"number"}]},
        {"id":"contrast_table","title":"Frozen diagnostic contrasts","subtitle":"95% intervals use 2,000 resamples of 100 contiguous centre blocks","dataset":"contrasts","sourceId":"pn10c_contrast_query","source":{"label":"PN10C frozen contrast query","path":"analysis/primes/pn10c_report_contrasts.sql","query":q_contrast},"defaultSort":{"field":"contrast","direction":"asc"},"density":"spacious","layout":"full","columns":[{"field":"contrast","label":"Contrast","type":"text"},{"field":"estimate","label":"Estimate","type":"number","movement":True},{"field":"ci95_low","label":"95% CI low","type":"number"},{"field":"ci95_high","label":"95% CI high","type":"number"},{"field":"standardized_difference","label":"Std. difference","type":"number"},{"field":"interpretation","label":"Diagnostic meaning","type":"text"}]},
    ],
    "blocks":[
        {"id":"title","type":"markdown","body":"# PN10C Three-Lane Prime Geometry"},
        {"id":"summary","type":"markdown","sourceId":"pn10c_results","body":"## The marked lanes are real, but black is the common route\n\nRed and blue exchange roles by **+0.323729** (95% CI **[+0.323298,+0.324171]**), and reflecting one centre orientation onto the other cuts mismatch by **99.52%**. Black is invariant across orientations, but after conditioning it is **0.004060 lower** than the admissible coloured branch. Black is therefore the shared mod-6 route at this grain, not a stronger independent third wave. It then decomposes into a rotating factor-5 child trough at mod 30. PN10B remains **NULL**."},
        {"id":"pair_result","type":"markdown","sourceId":"pn10c_results","body":"## Red and blue form a reversible conditional pair\n\nFor a centre `1 mod 6`, lane 2 lands entirely on multiples of 3 and falls to **0.099378**, while lane 4 remains admissible at **0.423268**. For a centre `5 mod 6`, the roles reverse: lane 2 is **0.422946** and lane 4 is **0.099378**. The reflected trace error is **0.000515** versus **0.107882** without reflection."},
        {"id":"trace","type":"chart","chartId":"orientation_trace","layout":"full"},
        {"id":"common_result","type":"markdown","sourceId":"pn10c_results","body":"## Black preserves either orientation instead of selecting one\n\nBlack offsets are multiples of 6, so they keep both prime-admissible centre classes clear of factors 2 and 3. Its orientation difference is **-0.000358**, with an interval containing zero. Its apparent aggregate height comes from remaining admissible in both orientations while each coloured lane is suppressed in one."},
        {"id":"lanes","type":"chart","chartId":"lane_means","layout":"full"},
        {"id":"lane_detail","type":"table","tableId":"lane_table","layout":"full"},
        {"id":"child_result","type":"markdown","sourceId":"pn10c_results","body":"## The common route opens into a rotating mod-5 child trough\n\nWriting a black offset as `k=6m`, the child satisfying `(centre mod 5 + m mod 5) mod 5 = 0` is always divisible by 5. Its measured progress is **0.145586686**, exactly the factor-5 value, versus **0.487412541** for eligible children. The eligible-minus-suppressed contrast is **+0.341826**."},
        {"id":"matrix","type":"table","tableId":"matrix_table","layout":"full"},
        {"id":"control","type":"markdown","sourceId":"pn10c_results","body":"## Matched composites show that the surrounding geometry is modular\n\nComposite centres coprime to 6 reproduce the red/blue swap at **+0.323995**. The surrounding lanes are therefore a general modular lattice, not a signal unique to primes. The exact central **1.0 ridge** remains prime-specific by the parent-coordinate definition."},
        {"id":"contrasts_reading","type":"markdown","sourceId":"pn10c_results","body":"## The frozen contrasts separate the supported and unsupported readings\n\nThe red/blue swap, reflection and mod-30 child split are strongly supported. Black-lane independence is not: its comparison with the admissible coloured branch has the opposite sign. The signed chart and exact table retain that distinction."},
        {"id":"contrasts_chart","type":"chart","chartId":"contrast_chart","layout":"full"},
        {"id":"contrasts_table","type":"table","tableId":"contrast_table","layout":"full"},
        {"id":"scope","type":"markdown","sourceId":"pn10c_protocol","body":"## Scope, data and metric definitions\n\nThe test used the already-open million-integer interval near four billion, **45,156** interior prime centres, a `+-150` window and **45,156** matched coprime-composite controls. Parent factor progress is `1` for primes and `2 log(LPF(n))/log(n)` for composites. The lane-conditioned predictions were frozen before their calculation; the interval itself was already open, so the evidence is post-hoc."},
        {"id":"method","type":"markdown","sourceId":"pn10c_protocol","body":"## Frozen diagnostic and uncertainty design\n\nThe protocol fixed five questions: coloured-lane exchange, phase reflection, black invariance, black-versus-admissible-colour independence, and `6 -> 30` child decomposition. Uncertainty used 2,000 deterministic resamples over 100 contiguous centre blocks. Positive and negative offsets, exact divisibility identities, worked events and matched composites were retained as controls."},
        {"id":"validation","type":"markdown","sourceId":"pn10c_validation","body":"## Independent validation passed 17 of 17 checks\n\nThe validator regenerated the interval, recomputed every prime-centred offset profile and headline contrast, traced all 222 worked-example rows, and found zero mod-3 or mod-5 identity violations. This verifies the arithmetic and artifacts, not a universal ARA ontology."},
        {"id":"limitations","type":"markdown","body":"## Established mechanism, bounded ARA inference\n\nThe result validates the decomposition of this plot, but the mechanism is established wheel-sieve arithmetic. It does not establish three independent waves, a new prime theorem, prospective predictive value, physical universality or the full fractal claim. Its value is that ARA led to the correct orientation, shared-route and child-hierarchy questions without flattening the aggregate trace."},
        {"id":"next","type":"markdown","body":"## Recommended next step\n\nFreeze a `6 -> 30 -> 210` wheel-hierarchy transformation on a new unopened interval. Add one ARA statistic among the still-eligible children whose value or ordering is not automatically fixed by divisibility. That is the point at which the method could move beyond a clean crosswalk into an independently informative calculation."},
        {"id":"questions","type":"markdown","body":"## Further questions\n\nDoes the mod-7 orientation produce the predicted rotating child while preserving the common parent relation? Can ARA predeclare a continuous ordering among eligible children? Does the reflection persist at new numerical scales? Which prospective quantity distinguishes ARA from a relabelled wheel sieve?"},
    ],
}

snapshot={"version":1,"generatedAt":"2026-07-20T20:00:00+10:00","status":"ready","datasets":{"orientation_trace":offset_rows,"lane_summary":lane_rows,"mod30_matrix":matrix_rows,"contrasts":contrast_rows}}
payload={"surface":"report","manifest":manifest,"snapshot":snapshot,"sources":sources}
OUT.write_text(json.dumps(payload,indent=2),encoding="utf-8")
print(OUT)
