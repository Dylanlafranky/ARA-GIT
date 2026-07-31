"""Run the unchanged Q41 strand operator on the frozen Q41B landmax target."""

from __future__ import annotations

import pathlib

import q41_cadence_strand_reversal_test as test


HERE = pathlib.Path(__file__).resolve().parent
test.TEST_ID = "Q41B-CADENCE-STRAND-REVERSAL-LANDMAX-v1"
test.DATA = (
    HERE / "public_data" / "q41b_cadence_strand_inhomo_v1_landmax"
)
test.ARCHIVE_NAME = "unnati_submit_12_inhomo_v1_landmax.hdf5.zip"
test.HDF_NAME = "unnati_submit_12_inhomo_v1_landmax.hdf5"
test.ARCHIVE = test.DATA / test.ARCHIVE_NAME
test.SOURCE = test.DATA / test.HDF_NAME
test.ARCHIVE_MD5 = "f2e191d2f06643818c4ba64743e16238"
test.DERIVED = test.DATA / "q41b_derived_cache.npz"
test.CONNECTED = test.DATA / "q41b_connected_cache.npy"
test.PREDICTIONS = test.DATA / "q41b_frozen_predictions.npz"
test.RESULTS = HERE / "Q41B_CADENCE_STRAND_REVERSAL_RESULTS.json"
test.EVENTS = HERE / "Q41B_CADENCE_STRAND_REVERSAL_CYCLES.csv.gz"
test.FIGURE_PNG = HERE / "Q41B_CADENCE_STRAND_REVERSAL_DIAGNOSTICS.png"
test.FIGURE_SVG = HERE / "Q41B_CADENCE_STRAND_REVERSAL_DIAGNOSTICS.svg"
test.PROTOCOL = (
    HERE / "Q41B_CADENCE_STRAND_REVERSAL_PROTOCOL_v1_PRETARGET_FROZEN.md"
)
test.TARGET_LOCK = HERE / "Q41B_TARGET_LOCK_v1_FROZEN.md"
test.EXPECTED_PROTOCOL_SHA256 = (
    "78491f3c2a0d6df97f069acaa399d6bbca7172cf2d219bfa01e3948418c0631d"
)
test.EXPECTED_TARGET_LOCK_SHA256 = (
    "80d0df632223a2f21b6a30aab75d7fdbbffa142fdb36aebd0e0c99e963d06ccd"
)


if __name__ == "__main__":
    test.main()

