"""Validate Q41B by reusing the independent Q41 validator on Q41B paths."""

from __future__ import annotations

import pathlib

import q41_validate_cadence_strand_reversal as validation


HERE = pathlib.Path(__file__).resolve().parent
validation.DATA = (
    HERE / "public_data" / "q41b_cadence_strand_inhomo_v1_landmax"
)
validation.CONNECTED = validation.DATA / "q41b_connected_cache.npy"
validation.PREDICTIONS = validation.DATA / "q41b_frozen_predictions.npz"
validation.EVENTS = HERE / "Q41B_CADENCE_STRAND_REVERSAL_CYCLES.csv.gz"
validation.RESULTS = HERE / "Q41B_CADENCE_STRAND_REVERSAL_RESULTS.json"
validation.OUTPUT = HERE / "Q41B_CADENCE_STRAND_REVERSAL_VALIDATION.json"


if __name__ == "__main__":
    validation.main()

