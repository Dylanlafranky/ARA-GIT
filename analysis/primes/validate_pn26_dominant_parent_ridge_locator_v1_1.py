"""PN26 validator v1.1: frozen one-bound correction to the v1 validator."""

from __future__ import annotations

import math
from pathlib import Path

import validate_pn26_dominant_parent_ridge_locator as frozen_v1


HERE = Path(__file__).resolve().parent
ORIGINAL_PRIME_BUILDER = frozen_v1.independent_primes
REQUIRED_PARENT_LIMIT = math.isqrt(
    2 * max(scale_anchor for _, scale_anchor, _, _ in frozen_v1.TARGET_RANGES)
) + 2


def corrected_prime_builder(requested_limit: int) -> list[int]:
    """Supply both the truth bound and the larger declared parent-child bound."""
    return ORIGINAL_PRIME_BUILDER(max(requested_limit, REQUIRED_PARENT_LIMIT))


frozen_v1.independent_primes = corrected_prime_builder
frozen_v1.VALIDATED_ROWS = HERE / "PN26_DOMINANT_PARENT_RIDGE_VALIDATED_ROWS_V1_1.csv"
frozen_v1.VALIDATION = HERE / "PN26_DOMINANT_PARENT_RIDGE_VALIDATION_V1_1.json"


if __name__ == "__main__":
    frozen_v1.main()
