#!/usr/bin/env python3
"""Rebuild and verify the large, intentionally untracked PN35/PN36 CSVs.

The original frozen primary builders and independent validators remain the
methodological source of truth. This script only orchestrates them, redirects
their bulky products to a safe temporary directory, verifies the recorded
SHA-256 hashes, and then promotes the completed CSVs to the requested output
directory.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path
from types import ModuleType


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MANIFEST = HERE / "PN35_PN36_CSV_REPRODUCTION_MANIFEST.json"


class ReproductionError(RuntimeError):
    """Raised when regenerated output differs from the recorded experiment."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ReproductionError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_hash(path: Path, expected: str, label: str) -> None:
    if not path.is_file():
        raise ReproductionError(f"Missing {label}: {path}")
    actual = sha256(path)
    if actual != expected:
        raise ReproductionError(
            f"{label} hash mismatch\n"
            f"  file:     {path}\n"
            f"  expected: {expected}\n"
            f"  actual:   {actual}"
        )


def verify_bytes(path: Path, expected: int, label: str) -> None:
    actual = path.stat().st_size
    if actual != expected:
        raise ReproductionError(
            f"{label} byte-count mismatch: expected {expected}, got {actual}"
        )


def canonical_metadata_is_intact(spec: dict) -> None:
    for key in ("primary_receipt", "results", "validation"):
        item = spec[key]
        verify_hash(HERE / item["name"], item["sha256"], f"canonical {key}")


def existing_output_matches(path: Path, item: dict) -> bool:
    return (
        path.is_file()
        and path.stat().st_size == item["bytes"]
        and sha256(path) == item["sha256"]
    )


def run_one(
    key: str,
    spec: dict,
    output_dir: Path,
    stage: str,
    force: bool,
    check_only: bool,
) -> None:
    label = key.upper()
    prediction_path = output_dir / spec["prediction"]["name"]
    scored_path = output_dir / spec["scored"]["name"]

    canonical_metadata_is_intact(spec)
    primary = load_module(HERE / spec["primary_script"], f"_{key}_primary_reproduction")
    primary.verify_freeze()

    prediction_ok = existing_output_matches(prediction_path, spec["prediction"])
    scored_ok = existing_output_matches(scored_path, spec["scored"])

    if check_only:
        verify_hash(prediction_path, spec["prediction"]["sha256"], f"{label} predictions")
        verify_bytes(prediction_path, spec["prediction"]["bytes"], f"{label} predictions")
        if stage == "full":
            verify_hash(scored_path, spec["scored"]["sha256"], f"{label} scored data")
            verify_bytes(scored_path, spec["scored"]["bytes"], f"{label} scored data")
        print(f"[{label}] existing {stage} products match the recorded hashes")
        return

    if prediction_ok and (stage == "predictions" or scored_ok) and not force:
        print(f"[{label}] matching products already exist; use --force to rebuild them")
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".reproduction_tmp_", dir=output_dir) as temp_name:
        temp_dir = Path(temp_name)
        generated_prediction = temp_dir / spec["prediction"]["name"]
        generated_receipt = temp_dir / spec["primary_receipt"]["name"]

        if force or not prediction_ok:
            print(f"[{label}] rebuilding label-free predictions")
            primary.OUTPUT = generated_prediction
            primary.RECEIPT = generated_receipt
            receipt = primary.build()
            if receipt["test_id"] != spec["test_id"]:
                raise ReproductionError(f"{label} primary test ID changed")
            if receipt["rows"] != spec["prediction"]["rows"]:
                raise ReproductionError(f"{label} primary row count changed")
            verify_hash(
                generated_prediction,
                spec["prediction"]["sha256"],
                f"regenerated {label} predictions",
            )
            verify_bytes(
                generated_prediction,
                spec["prediction"]["bytes"],
                f"regenerated {label} predictions",
            )
            verify_hash(
                generated_receipt,
                spec["primary_receipt"]["sha256"],
                f"regenerated {label} primary receipt",
            )
            prediction_for_validation = generated_prediction
            receipt_for_validation = generated_receipt
        else:
            print(f"[{label}] reusing hash-verified predictions")
            prediction_for_validation = prediction_path
            receipt_for_validation = HERE / spec["primary_receipt"]["name"]

        generated_scored: Path | None = None
        if stage == "full":
            try:
                validator = load_module(
                    HERE / spec["validator_script"], f"_{key}_validator_reproduction"
                )
            except ModuleNotFoundError as exc:
                if exc.name == "numpy":
                    raise ReproductionError(
                        "Full reproduction requires NumPy. Install "
                        "analysis/primes/requirements_pn35_pn36_reproduction.txt"
                    ) from exc
                raise

            print(f"[{label}] opening primality labels and rebuilding scored data")
            generated_scored = temp_dir / spec["scored"]["name"]
            generated_results = temp_dir / spec["results"]["name"]
            generated_validation = temp_dir / spec["validation"]["name"]
            validator.PRIMARY_RECEIPT = receipt_for_validation
            validator.PREDICTIONS = prediction_for_validation
            validator.SCORED = generated_scored
            validator.RESULTS = generated_results
            validator.VALIDATION = generated_validation
            result = validator.main()
            if result["test_id"] != spec["test_id"]:
                raise ReproductionError(f"{label} validator test ID changed")
            if result["rows"] != spec["scored"]["rows"]:
                raise ReproductionError(f"{label} scored row count changed")
            verify_hash(
                generated_scored,
                spec["scored"]["sha256"],
                f"regenerated {label} scored data",
            )
            verify_bytes(
                generated_scored,
                spec["scored"]["bytes"],
                f"regenerated {label} scored data",
            )
            verify_hash(
                generated_results,
                spec["results"]["sha256"],
                f"regenerated {label} results",
            )
            verify_hash(
                generated_validation,
                spec["validation"]["sha256"],
                f"regenerated {label} validation receipt",
            )

        if generated_prediction.is_file():
            os.replace(generated_prediction, prediction_path)
        if generated_scored is not None:
            os.replace(generated_scored, scored_path)

    print(f"[{label}] reproduction passed; verified CSVs are in {output_dir}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rebuild and hash-verify the large PN35/PN36 CSV products."
    )
    parser.add_argument(
        "--test",
        choices=("all", "pn35", "pn36"),
        default="all",
        help="test to reproduce (default: all)",
    )
    parser.add_argument(
        "--stage",
        choices=("predictions", "full"),
        default="full",
        help="stop after the label-free predictions or also rebuild scored CSVs",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=HERE,
        help="directory for the regenerated CSVs (default: analysis/primes)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="rebuild even when existing CSVs already match",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify existing CSVs without regenerating them",
    )
    args = parser.parse_args()
    if args.check and args.force:
        parser.error("--check and --force cannot be used together")
    return args


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.expanduser().resolve()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    selected = manifest["tests"].keys() if args.test == "all" else (args.test,)

    print(f"Python {sys.version.split()[0]}")
    try:
        for key in selected:
            run_one(
                key,
                manifest["tests"][key],
                output_dir,
                args.stage,
                args.force,
                args.check,
            )
    except (OSError, ReproductionError) as exc:
        print(f"REPRODUCTION FAILED: {exc}", file=sys.stderr)
        return 1

    print("All requested hash checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
