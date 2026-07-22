"""Rerun the unchanged PN26 recording audit after clarifying one report phrase."""

from pathlib import Path

import validate_pn26_recording as frozen_v1


frozen_v1.OUTPUT = Path(__file__).resolve().parent / "PN26_RECORDING_VALIDATION_V1_1.json"


if __name__ == "__main__":
    frozen_v1.main()
