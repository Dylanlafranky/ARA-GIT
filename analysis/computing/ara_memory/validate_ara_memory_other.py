#!/usr/bin/env python3
"""Independent reference audit for the ARA memory/Other experiment."""

from __future__ import annotations

import hashlib
import json
import math
import random
import struct
import zlib
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
PROTOCOL = ROOT / "ARA_MEMORY_OTHER_PROTOCOL_2026-07-23.md"
RESULTS = ROOT / "ARA_MEMORY_OTHER_RESULTS.json"
OUTPUT = ROOT / "ARA_MEMORY_OTHER_VALIDATION.json"
MAGIC = b"ARAO1"
SIZE = 65_536


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def get_uint(stream: bytes, cursor: int) -> tuple[int, int]:
    total = 0
    bit = 0
    while True:
        octet = stream[cursor]
        cursor += 1
        total |= (octet & 127) << bit
        if octet < 128:
            return total, cursor
        bit += 7


def signed(unsigned: int) -> int:
    return unsigned // 2 if unsigned % 2 == 0 else -(unsigned // 2) - 1


def reference_decode(stream: bytes) -> bytes:
    if stream[:5] != MAGIC:
        raise AssertionError("bad stream marker")
    length, width, blocks = struct.unpack(">QII", stream[5:21])
    cursor = 21
    reconstructed: list[int] = []
    for _ in range(blocks):
        root, cursor = get_uint(stream, cursor)
        layer = [signed(root)]
        for depth in range(int(math.log2(width))):
            residuals = []
            for _ in range(1 << depth):
                value, cursor = get_uint(stream, cursor)
                residuals.append(signed(value))
            next_layer = []
            for parent, residual in zip(layer, residuals):
                right = parent - residual // 2
                left = right + residual
                next_layer.extend((left, right))
            layer = next_layer
        reconstructed.extend(layer)
    if cursor != len(stream):
        raise AssertionError("unexpected bytes after final block")
    return bytes(reconstructed[:length])


def uint(value: int) -> bytes:
    payload = bytearray()
    while True:
        current = value & 127
        value >>= 7
        payload.append(current | (128 if value else 0))
        if not value:
            return bytes(payload)


def unsigned(value: int) -> int:
    return 2 * value if value >= 0 else -2 * value - 1


def reference_encode(payload: bytes, width: int) -> bytes:
    encoded = bytearray(MAGIC)
    encoded.extend(struct.pack(">QII", len(payload), width, math.ceil(len(payload) / width)))
    for start in range(0, len(payload), width):
        block = list(payload[start : start + width])
        block += [block[-1]] * (width - len(block))
        detail_layers: list[list[int]] = []
        while len(block) > 1:
            next_block = []
            details = []
            for index in range(0, len(block), 2):
                left, right = block[index : index + 2]
                difference = left - right
                next_block.append(right + difference // 2)
                details.append(difference)
            detail_layers.append(details)
            block = next_block
        encoded.extend(uint(unsigned(block[0])))
        for details in reversed(detail_layers):
            for difference in details:
                encoded.extend(uint(unsigned(difference)))
    return bytes(encoded)


def smooth() -> bytes:
    rng = random.Random(2026072301)
    values = []
    for index in range(SIZE):
        value = (
            128
            + 58 * math.sin(2 * math.pi * index / 4096)
            + 19 * math.sin(2 * math.pi * index / 257)
            + 5 * math.sin(2 * math.pi * index / 31)
            + rng.choice((-1, 0, 0, 0, 1))
        )
        values.append(max(0, min(255, round(value))))
    return bytes(values)


def piecewise() -> bytes:
    data = bytearray()
    rng = random.Random(2026072302)
    record = 0
    while len(data) < SIZE:
        slow = (record // 32) % 256
        fast = record % 256
        status = 165 if (record // 128) % 2 == 0 else 90
        data.extend((65, 82, 65, status, slow, fast, (slow + fast) % 256, (slow - fast) % 256))
        data.extend([slow] * 24)
        data.extend((fast + offset) % 256 for offset in range(16))
        data.extend(rng.choice((0, 0, 0, 1, 255)) for _ in range(16))
        record += 1
    return bytes(data[:SIZE])


def source_bytes(paths: list[Path]) -> bytes:
    output = bytearray()
    for path in paths:
        if path.exists():
            output.extend(path.read_bytes())
            output.extend(b"\n\n")
        if len(output) >= SIZE:
            return bytes(output[:SIZE])
    raise AssertionError("frozen source set too short")


def datasets() -> dict[str, bytes]:
    return {
        "smooth_telemetry": smooth(),
        "piecewise_memory": piecewise(),
        "ara_text": source_bytes(
            [
                REPO / "WHAT_IS_ARA.md",
                REPO / "GLOSSARY.md",
                REPO / "ARA_SCALE.md",
                REPO / "ARA_FOUNDATIONS_FROM_ESTABLISHED_MECHANICS.md",
            ]
        ),
        "python_source": source_bytes(sorted((REPO / "analysis").rglob("*.py"))),
        "uniform_random": random.Random(2026072303).randbytes(SIZE),
    }


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    errors: list[str] = []
    if result["protocol_sha256"] != digest(PROTOCOL.read_bytes()):
        errors.append("protocol hash mismatch")

    local_data = datasets()
    row_lookup = {
        (row["dataset"], int(row["block_size"])): row for row in result["all_rows"]
    }
    checks = []
    for name, data in local_data.items():
        for width in result["block_sizes"]:
            encoded = reference_encode(data, int(width))
            restored = reference_decode(encoded)
            compressed = zlib.compress(encoded, 9)
            primary = row_lookup[(name, int(width))]
            passed = (
                restored == data
                and digest(data) == primary["original_sha256"]
                and digest(restored) == primary["restored_sha256"]
                and digest(encoded) == primary["ara_stream_sha256"]
                and len(encoded) == primary["ara_serialized_bytes"]
                and len(compressed) == primary["ara_zlib_bytes"]
            )
            if not passed:
                errors.append(f"reference mismatch: {name}, block {width}")
            checks.append({"dataset": name, "block_size": width, "passed": passed})

    # Exhaust the elementary byte-pair inverse independently.
    pair_failures = 0
    for left in range(256):
        for right in range(256):
            difference = left - right
            parent = right + difference // 2
            restored_right = parent - difference // 2
            restored_left = restored_right + difference
            pair_failures += (restored_left, restored_right) != (left, right)
    if pair_failures:
        errors.append(f"{pair_failures} elementary byte pairs did not invert")

    # Reproduce the public-transform attack and authenticated wrapper.
    data = local_data["smooth_telemetry"]
    public_stream = reference_encode(data, 1024)
    public_attack_exact = reference_decode(public_stream) == data
    compressed = zlib.compress(public_stream, 9)
    key = hashlib.sha256(b"ARA public deterministic AES-GCM test key 2026-07-23").digest()
    nonce = hashlib.sha256(b"smooth_telemetry unique test nonce").digest()[:12]
    aad = b"ARA-memory-test-v1"
    aes = AESGCM(key)
    ciphertext = aes.encrypt(nonce, compressed, aad)
    authenticated_exact = (
        reference_decode(zlib.decompress(aes.decrypt(nonce, ciphertext, aad))) == data
    )
    corrupt = bytearray(ciphertext)
    corrupt[len(corrupt) // 2] ^= 1
    tamper_rejected = False
    try:
        aes.decrypt(nonce, bytes(corrupt), aad)
    except InvalidTag:
        tamper_rejected = True

    security_matches = (
        public_attack_exact == result["security"]["naive_attacker_exact_recovery"]
        and authenticated_exact == result["security"]["authenticated_roundtrip_exact"]
        and tamper_rejected == result["security"]["tampered_ciphertext_rejected"]
        and digest(nonce + ciphertext) == result["security"]["ciphertext_sha256"]
    )
    if not security_matches:
        errors.append("independent security-vector result mismatch")

    validation = {
        "status": "passed" if not errors else "failed",
        "scope": (
            "Independent reference transform/inverse, exhaustive 65,536 byte-pair "
            "identity check, regenerated compression sizes and reproduced AES-GCM vectors."
        ),
        "protocol_sha256": digest(PROTOCOL.read_bytes()),
        "results_sha256": digest(RESULTS.read_bytes()),
        "dataset_block_checks_passed": sum(check["passed"] for check in checks),
        "dataset_block_checks_total": len(checks),
        "elementary_byte_pairs_checked": 65_536,
        "elementary_pair_failures": pair_failures,
        "public_attack_exact": public_attack_exact,
        "authenticated_roundtrip_exact": authenticated_exact,
        "tamper_rejected": tamper_rejected,
        "security_matches_primary": security_matches,
        "errors": errors,
    }
    OUTPUT.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
