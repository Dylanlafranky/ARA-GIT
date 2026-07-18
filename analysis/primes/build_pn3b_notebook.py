"""Build the reproducible PN3B notebook using only the Python standard library.

The scientific runtime in this workspace does not bundle nbformat/nbclient.
The analysis and validator are executed separately before this builder; their
verified JSON results are embedded as cell outputs.
"""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "PN3B_RAW_DUAL_PHASE_DIAGNOSTIC.ipynb"
RESULTS = json.loads((HERE / "PN3B_RAW_DUAL_PHASE_RESULTS.json").read_text(encoding="utf-8"))
VALIDATION = json.loads((HERE / "PN3B_INDEPENDENT_VALIDATION.json").read_text(encoding="utf-8"))


def markdown(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(True)}


def code(source: str, count: int, output: object) -> dict:
    return {
        "cell_type": "code",
        "execution_count": count,
        "metadata": {},
        "outputs": [{"name": "stdout", "output_type": "stream", "text": json.dumps(output, indent=2) + "\n"}],
        "source": source.splitlines(True),
    }


compact = {
    rung: {
        "raw_primes": summary["raw_prime_events"],
        "q29_low_mode_fwer_p": summary["block_phase"]["29"]["global_familywise_p"],
        "q997_low_mode_fwer_p": summary["block_phase"]["997"]["global_familywise_p"],
        "q29_top_full_frequency": summary["post_result_connection_line_crosswalk"]["q29_residual_top_frequency"],
        "period_62_harmonic": summary["post_result_connection_line_crosswalk"]["period_62_harmonic"],
        "within_one_fourier_bin": summary["post_result_connection_line_crosswalk"]["within_one_fourier_bin"],
        "joint_leading_energy_p": summary["joint_gate"]["leading_energy_p"],
    }
    for rung, summary in RESULTS["rung_summaries"].items()
}

notebook = {
    "cells": [
        markdown(
            """# PN3B raw dual-phase diagnostic

This opened-data diagnostic asks whether the complete raw integer/prime record contains a second, scale-persistent phase coordinate after known sieve connections are controlled. It is not a blind prime prediction, does not access p31 test data, and does not identify a mathematical coordinate with physical time merely because it changes along the number line.

The frozen protocol is `PN3B_RAW_DUAL_PHASE_DIAGNOSTIC_PROTOCOL.md`."""
        ),
        markdown("## Rebuild the raw windows, controls, nulls and figures"),
        code(
            """from pn3b_raw_dual_phase import run
results = run()
print({
    'test_id': results['test_id'],
    'candidate_time_like_phase_coordinate_supported': results['candidate_time_like_phase_coordinate_supported'],
    'p31_accessed': results['p31_accessed'],
})""",
            1,
            {
                "test_id": RESULTS["test_id"],
                "candidate_time_like_phase_coordinate_supported": RESULTS["candidate_time_like_phase_coordinate_supported"],
                "p31_accessed": RESULTS["p31_accessed"],
            },
        ),
        markdown("## Compact result table"),
        code(
            """compact = {
    rung: {
        'raw_primes': summary['raw_prime_events'],
        'q29_low_mode_fwer_p': summary['block_phase']['29']['global_familywise_p'],
        'q997_low_mode_fwer_p': summary['block_phase']['997']['global_familywise_p'],
        'q29_top_full_frequency': summary['post_result_connection_line_crosswalk']['q29_residual_top_frequency'],
        'period_62_harmonic': summary['post_result_connection_line_crosswalk']['period_62_harmonic'],
        'within_one_fourier_bin': summary['post_result_connection_line_crosswalk']['within_one_fourier_bin'],
        'joint_leading_energy_p': summary['joint_gate']['leading_energy_p'],
    }
    for rung, summary in results['rung_summaries'].items()
}
print(compact)""",
            2,
            compact,
        ),
        markdown("## Cross-rung recurrence test"),
        code(
            """cross = {
    'q29_block_phase': results['cross_rung']['r8_to_r9__q29__global'],
    'position_x_future_gate': results['cross_rung']['r8_to_r9__joint_gate'],
}
print(cross)""",
            3,
            {
                "q29_block_phase": RESULTS["cross_rung"]["r8_to_r9__q29__global"],
                "position_x_future_gate": RESULTS["cross_rung"]["r8_to_r9__joint_gate"],
            },
        ),
        markdown("## Independent deterministic audit"),
        code(
            """from pn3b_independent_validation import main as validate
validation = validate()
print({'all_checks_pass': validation['all_checks_pass'],
       'validator_imports_primary_module': validation['validator_imports_primary_module']})""",
            4,
            {
                "all_checks_pass": VALIDATION["all_checks_pass"],
                "validator_imports_primary_module": VALIDATION["validator_imports_primary_module"],
            },
        ),
        markdown(
            """## Interpretation boundary

The raw dual view finds within-rung position-by-future-gate organization, but its leading orientation does not recur from R8 to R9. The strongest R8/R9 Q29 residual line is the third harmonic of period 62, matching the next omitted `2 × 31` connection gate. The registered criteria therefore do not support a distinct scale-persistent candidate “Time-like” coordinate.

This result rules out only the tested representation: a stationary Fourier/phase coordinate in these opened raw prime-indicator windows under these controls. It does **not** prove that no dual process exists, nor that prime structure exhausts ARA's proposed second pole.

![Raw dual spectrum](PN3B_RAW_DUAL_SPECTRUM.png)

![Phase by future-gate map](PN3B_PHASE_GATE_MAP.png)"""
        ),
    ],
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3"},
        "pn3b_note": "Outputs embedded after successful standalone execution and independent deterministic validation.",
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

NOTEBOOK.write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")
print(NOTEBOOK)
