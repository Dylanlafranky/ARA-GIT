"""Conservative probability audit for the historical ARA pre-test record.

This script does not estimate P(ARA is true). It asks a narrower question:
given the provisional clean-hit/miss tally in the provenance ledger, how
sensitive is the binomial tail probability to the unknown background rate at
which a flexible structural statement could be judged a match?

It also calculates operating characteristics for the proposed decisive test:
one real target hidden among nine matched decoys, with one primary result per
independent domain.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PROVENANCE_LEDGER = ROOT / "FableConvo" / "PROVENANCE_LEDGER.md"
MASTER_LEDGER = ROOT / "MASTER_PREDICTION_LEDGER.md"
ANALYSIS_ROOT = ROOT / "analysis"
EARLY_GEOMETRY_RECORD = ROOT / "ARA_CONVERSATION_RECORD_2026-06-25.md"
AXIOMATIC_RECORD = ROOT / "ARA_AXIOMATIC_PROOFS_AND_DOMAIN_SUBSETS.md"
MAXWELL_AUDIT = ANALYSIS_ROOT / "electromagnetism" / "MAXWELL_ARA_COMPLETENESS_AUDIT_2026-07-12.md"
PRIME_CAPSTONE = ANALYSIS_ROOT / "primes" / "PRIME_THREAD_CAPSTONE_AND_CLOSURE_2026-07-21.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def binomial_upper_tail(n: int, k: int, probability: float) -> float:
    """Return P[X >= k] for X ~ Binomial(n, probability)."""
    return sum(
        math.comb(n, successes)
        * probability**successes
        * (1.0 - probability) ** (n - successes)
        for successes in range(k, n + 1)
    )


def critical_null_rate(n: int, k: int, alpha: float = 0.05) -> float:
    """Largest null success rate rejected by the observed k-of-n result."""
    lower = 0.0
    upper = k / n
    for _ in range(120):
        midpoint = (lower + upper) / 2.0
        if binomial_upper_tail(n, k, midpoint) < alpha:
            lower = midpoint
        else:
            upper = midpoint
    return (lower + upper) / 2.0


def first_critical_count(n: int, null_rate: float, alpha: float) -> int:
    for successes in range(n + 1):
        if binomial_upper_tail(n, successes, null_rate) <= alpha:
            return successes
    raise RuntimeError("No critical count exists for the supplied design.")


def extract_integer(pattern: str, text: str, label: str) -> int:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        raise RuntimeError(f"Could not extract {label} from {PROVENANCE_LEDGER.name}.")
    return int(match.group(1))


def formal_protocol_profile() -> dict[str, object]:
    protocols = sorted(
        path
        for path in ANALYSIS_ROOT.rglob("*.md")
        if "PROTOCOL" in path.name.upper() and "FROZEN" in path.name.upper()
    )
    by_domain: dict[str, int] = {}
    for path in protocols:
        relative = path.relative_to(ANALYSIS_ROOT)
        domain = relative.parts[0] if len(relative.parts) > 1 else "_analysis_root"
        by_domain[domain] = by_domain.get(domain, 0) + 1
    return {
        "count": len(protocols),
        "by_domain": by_domain,
        "paths": [str(path.relative_to(ROOT)).replace("\\", "/") for path in protocols],
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=HERE,
        help="Directory for JSON and CSV results.",
    )
    arguments = parser.parse_args()
    output_dir = arguments.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    provenance_text = PROVENANCE_LEDGER.read_text(encoding="utf-8")
    master_text = MASTER_LEDGER.read_text(encoding="utf-8")

    clean_hits = extract_integer(r"A-tier clean hits:\s*(\d+)", provenance_text, "clean hits")
    partial = extract_integer(r"Partial/C-tier:\s*~?(\d+)", provenance_text, "partial/C-tier")
    misses = extract_integer(r"Misses/refuted:\s*(\d+)", provenance_text, "misses")
    contaminated = extract_integer(
        r"Excluded as contaminated:\s*(\d+)", provenance_text, "contaminated exclusions"
    )

    strict_total = clean_hits + misses
    observed_rate = clean_hits / strict_total
    candidate_null_rates = [0.05, 0.10, 0.15, 0.20, 0.21, 0.22, 0.23, 0.25, 0.30, 1 / 3, 0.50]
    sensitivity_rows = []
    for null_rate in candidate_null_rates:
        probability = binomial_upper_tail(strict_total, clean_hits, null_rate)
        sensitivity_rows.append(
            {
                "null_match_rate": round(null_rate, 9),
                "tail_probability": probability,
                "reject_at_0_05": probability <= 0.05,
            }
        )

    critical_rate = critical_null_rate(strict_total, clean_hits)

    decoy_rows = []
    for domain_count in (10, 12, 15, 20):
        critical_count = first_critical_count(domain_count, null_rate=0.10, alpha=0.05)
        decoy_rows.append(
            {
                "independent_domains": domain_count,
                "matched_decoys_per_domain": 9,
                "null_top_rank_rate": 0.10,
                "critical_top_rank_wins": critical_count,
                "actual_alpha": binomial_upper_tail(domain_count, critical_count, 0.10),
                "power_if_true_rate_0_30": binomial_upper_tail(
                    domain_count, critical_count, 0.30
                ),
                "power_if_true_rate_0_40": binomial_upper_tail(
                    domain_count, critical_count, 0.40
                ),
                "power_if_true_rate_0_50": binomial_upper_tail(
                    domain_count, critical_count, 0.50
                ),
            }
        )

    protocol_profile = formal_protocol_profile()
    recent_t_headings = re.findall(r"(?m)^### T(\d+)\b", master_text)

    payload = {
        "study_id": "ARA-PRETEST-CONSTRAINT-PROBABILITY/PILOT/2026-07-21/v1",
        "question": (
            "How surprising is the provisional clean-hit count under assumed background "
            "match rates, and what prospective design would identify that background rate?"
        ),
        "not_an_estimate_of": "P(ARA is true | repository)",
        "sources": {
            "provenance_ledger": {
                "path": str(PROVENANCE_LEDGER.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(PROVENANCE_LEDGER),
                "ledger_as_of": "2026-07-05",
            },
            "master_prediction_ledger": {
                "path": str(MASTER_LEDGER.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(MASTER_LEDGER),
                "recent_numbered_T_entries": len(recent_t_headings),
                "recent_T_range": (
                    [min(map(int, recent_t_headings)), max(map(int, recent_t_headings))]
                    if recent_t_headings
                    else None
                ),
            },
            "pre_domain_geometry_record": {
                "path": str(EARLY_GEOMETRY_RECORD.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(EARLY_GEOMETRY_RECORD),
                "record_date": "2026-06-25",
            },
            "axiomatic_record": {
                "path": str(AXIOMATIC_RECORD.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(AXIOMATIC_RECORD),
                "initial_date": "2026-07-11",
                "centered_revision": "2026-07-19",
            },
            "maxwell_recovery_audit": {
                "path": str(MAXWELL_AUDIT.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(MAXWELL_AUDIT),
                "audit_date": "2026-07-12",
            },
            "prime_thread_capstone": {
                "path": str(PRIME_CAPSTONE.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(PRIME_CAPSTONE),
                "capstone_date": "2026-07-21",
            },
        },
        "ledger_profile": {
            "clean_hits": clean_hits,
            "partial_or_consistency_tier": partial,
            "misses_or_refutations": misses,
            "excluded_as_contaminated": contaminated,
            "strict_binary_total": strict_total,
            "strict_observed_hit_rate": observed_rate,
            "formal_frozen_protocols": protocol_profile,
        },
        "historical_sensitivity": {
            "model": "X ~ Binomial(n=clean_hits+misses, p0=assumed background match rate)",
            "tail": "P(X >= observed clean hits)",
            "rows": sensitivity_rows,
            "critical_null_rate_at_alpha_0_05": critical_rate,
            "interpretation": (
                "The historical count rejects only null match rates below the critical value. "
                "Because the ledger does not empirically estimate p0 and is self-scored, these "
                "tail probabilities are sensitivity calculations rather than valid global evidence."
            ),
        },
        "declared_geometry_domain_recoveries": {
            "why_included": (
                "The reversible 0-2 pair, ridge, recursive child/parent structure and orientation "
                "were recorded before the Maxwell and prime walks. These later families therefore "
                "matter as generative, pre-domain constraint evidence."
            ),
            "independence_rule": (
                "Physics and primes are treated as two dependent domain families, not as one "
                "independent vote per equation, protocol, algebraic identity or related subtest."
            ),
            "families": [
                {
                    "domain": "electromagnetism/plasma",
                    "predeclared_core_carried_forward": (
                        "opposing oriented waves, a 1.0 balance ridge, orthogonal coupling, "
                        "child-to-parent recursion and retained total activity"
                    ),
                    "supported_results": [
                        "faithful ARA translations of all four Maxwell field equations",
                        "exact E/B/Poynting orthogonal triad for vacuum plane waves",
                        "MX3D nonlinear daughter identity: 6 of 8 strict development criteria",
                        "MX3E granddaughter harmonic: 8 of 8 development criteria",
                    ],
                    "failures_or_open_fences": [
                        "most field-law recoveries are exact reparameterisations, not novel predictions",
                        "the frozen particle-to-grid Lorentz bridge failed",
                        "the compact Lorentz closure remained partial",
                        "Maxwell stress and an independent held-out compression remain open",
                    ],
                    "meta_evidence_class": "pre-domain structural recovery with mixed empirical development",
                },
                {
                    "domain": "prime arithmetic",
                    "predeclared_core_carried_forward": (
                        "reversible 0-2 geometry, ridge closure, recursive rungs, ordered AB/BA "
                        "paths and two-child-to-one-parent coarse-graining"
                    ),
                    "supported_results": [
                        "held-out wheel transition relation with all four permutation tests at 1/201",
                        "PN1G passed 6 of 6 frozen prime-29 transfer checks",
                        "PN17-PN19 sealed exact next primes from fresh large anchors",
                        "PN14 and PN15 transferred near-1.0 paired/full-square-root ridge templates",
                        "exact 2:1 reversible anti-pair state compression",
                    ],
                    "failures_or_open_fences": [
                        "ARA endpoints were worse than conditioned PNT/Hardy-Littlewood in PN2",
                        "standalone ARA parent/child forecasting failed in PN3",
                        "PN10B later-survival ranking was chance-like",
                        "fixed Phi/36-degree/leak carriers failed",
                        "the largest-two-child three-operation prime shortcut failed",
                    ],
                    "meta_evidence_class": "pre-domain exact arithmetic crosswalk with real transfer and failed novelty tests",
                },
            ],
            "statistical_use": (
                "These families strengthen the case that one declared vocabulary can organize "
                "multiple domains, but they do not identify a chance probability because the "
                "space of admissible mappings and alternative frameworks was not sampled."
            ),
        },
        "prospective_decoy_design": {
            "primary_endpoint": (
                "The real target receives the highest preregistered ARA fit score among one real "
                "target and nine matched decoys."
            ),
            "unit": "one locked primary outcome per independent domain",
            "rows": decoy_rows,
            "recommended_initial_battery": {
                "independent_domains": 12,
                "decoys_per_domain": 9,
                "critical_top_rank_wins": 4,
                "actual_alpha": binomial_upper_tail(12, 4, 0.10),
                "power_if_true_top_rank_rate_0_40": binomial_upper_tail(12, 4, 0.40),
            },
        },
        "data_quality_findings": [
            {
                "severity": "critical",
                "finding": "The background match rate is unmeasured.",
                "impact": "No model-free historical probability can be calculated.",
            },
            {
                "severity": "high",
                "finding": "The provenance tally is self-scored and awaits independent rescoring.",
                "impact": "Verdict uncertainty and evaluator dependence are not represented.",
            },
            {
                "severity": "high",
                "finding": "The ledgers mix exact identities, rediscoveries, exploratory probes, and predictions.",
                "impact": "Pooling all positive labels would double-count non-surprising results.",
            },
            {
                "severity": "high",
                "finding": "Tests within primes, ENSO, and plasma are dependent families.",
                "impact": "Rows cannot be treated as independent replications.",
            },
            {
                "severity": "medium",
                "finding": "Formal frozen protocols are concentrated in only a few domains.",
                "impact": "Current seal strength is better than current cross-domain independence.",
            },
        ],
        "decision": {
            "historical_global_probability_identified": False,
            "historical_result": "SENSITIVITY ONLY",
            "prospective_test_feasible": True,
            "recommended_status": "DRAFT DECOY-CONTROLLED PROTOCOL BEFORE NEW MAPPINGS",
        },
    }

    json_path = output_dir / "ARA_PRETEST_CONSTRAINT_PROBABILITY_RESULTS.json"
    sensitivity_path = output_dir / "ARA_PRETEST_NULL_RATE_SENSITIVITY.csv"
    decoy_path = output_dir / "ARA_PRETEST_DECOY_POWER.csv"

    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_csv(sensitivity_path, sensitivity_rows)
    write_csv(decoy_path, decoy_rows)

    print(
        json.dumps(
            {
                "status": "PASS",
                "clean_hits": clean_hits,
                "misses": misses,
                "observed_rate": observed_rate,
                "critical_null_rate": critical_rate,
                "recommended_battery": payload["prospective_decoy_design"][
                    "recommended_initial_battery"
                ],
                "outputs": [str(json_path), str(sensitivity_path), str(decoy_path)],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
