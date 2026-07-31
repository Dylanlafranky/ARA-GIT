"""Run the independent Q44 validator against the Q44A amendment outputs."""

from __future__ import annotations

import pathlib

import q44_validate_ara_mixing_prediction as validator


HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / "public_data" / "q44_mixing_inhomo_v1_mimic"

validator.PREDICTIONS = DATA / "q44a_frozen_predictions.npz"
validator.RESULTS = HERE / "Q44A_SPARSE_GROUP_ARA_MIXING_RESULTS.json"
validator.VALIDATION = HERE / "Q44A_SPARSE_GROUP_ARA_MIXING_VALIDATION.json"


if __name__ == "__main__":
    validator.main()
