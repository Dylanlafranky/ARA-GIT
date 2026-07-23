#!/usr/bin/env python3
"""Frozen ARA parent/Other memory, compression and security experiment."""

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
SUMMARY = ROOT / "ARA_MEMORY_OTHER_SUMMARY.csv"

DATASET_SIZE = 65_536
PRIMARY_BLOCK_SIZE = 1_024
BLOCK_SIZES = (64, 256, PRIMARY_BLOCK_SIZE, 4_096)
MAGIC = b"ARAO1"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def zigzag_encode(value: int) -> int:
    return value * 2 if value >= 0 else -value * 2 - 1


def zigzag_decode(value: int) -> int:
    return value // 2 if value % 2 == 0 else -(value // 2) - 1


def encode_varint(value: int) -> bytes:
    encoded = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            encoded.append(byte | 0x80)
        else:
            encoded.append(byte)
            return bytes(encoded)


def decode_varint(data: bytes, offset: int) -> tuple[int, int]:
    value = 0
    shift = 0
    while True:
        if offset >= len(data) or shift > 35:
            raise ValueError("invalid variable integer")
        byte = data[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, offset
        shift += 7


def pair_forward(a: int, b: int) -> tuple[int, int]:
    difference = a - b
    parent = b + difference // 2
    return parent, difference


def pair_inverse(parent: int, difference: int) -> tuple[int, int]:
    b = parent - difference // 2
    a = b + difference
    return a, b


def block_forward(values: list[int]) -> tuple[int, list[list[int]]]:
    levels: list[list[int]] = []
    current = values
    while len(current) > 1:
        parents: list[int] = []
        differences: list[int] = []
        for index in range(0, len(current), 2):
            parent, difference = pair_forward(current[index], current[index + 1])
            parents.append(parent)
            differences.append(difference)
        levels.append(differences)
        current = parents
    return current[0], list(reversed(levels))


def block_inverse(root: int, coarse_to_fine: list[list[int]]) -> list[int]:
    current = [root]
    for differences in coarse_to_fine:
        if len(differences) != len(current):
            raise ValueError("invalid residual-tree shape")
        children: list[int] = []
        for parent, difference in zip(current, differences):
            children.extend(pair_inverse(parent, difference))
        current = children
    return current


def ara_encode(data: bytes, block_size: int) -> bytes:
    if block_size < 2 or block_size & (block_size - 1):
        raise ValueError("block size must be a power of two")
    output = bytearray(MAGIC)
    output.extend(struct.pack(">QII", len(data), block_size, math.ceil(len(data) / block_size)))
    for start in range(0, len(data), block_size):
        block = list(data[start : start + block_size])
        if len(block) < block_size:
            block.extend([block[-1] if block else 0] * (block_size - len(block)))
        root, levels = block_forward(block)
        output.extend(encode_varint(zigzag_encode(root)))
        for level in levels:
            for difference in level:
                output.extend(encode_varint(zigzag_encode(difference)))
    return bytes(output)


def ara_decode(encoded: bytes) -> bytes:
    if encoded[:5] != MAGIC:
        raise ValueError("invalid ARA memory stream")
    original_length, block_size, block_count = struct.unpack(">QII", encoded[5:21])
    offset = 21
    output: list[int] = []
    depth = int(math.log2(block_size))
    level_lengths = [1 << level for level in range(depth)]
    for _ in range(block_count):
        root_encoded, offset = decode_varint(encoded, offset)
        root = zigzag_decode(root_encoded)
        levels: list[list[int]] = []
        for length in level_lengths:
            differences: list[int] = []
            for _ in range(length):
                value, offset = decode_varint(encoded, offset)
                differences.append(zigzag_decode(value))
            levels.append(differences)
        output.extend(block_inverse(root, levels))
    if offset != len(encoded):
        raise ValueError("unexpected trailing bytes")
    if any(value < 0 or value > 255 for value in output[:original_length]):
        raise ValueError("decoded byte outside range")
    return bytes(output[:original_length])


def delta_encode(data: bytes) -> bytes:
    output = bytearray(b"DELT1")
    output.extend(struct.pack(">Q", len(data)))
    previous = 0
    for byte in data:
        difference = byte - previous
        output.extend(encode_varint(zigzag_encode(difference)))
        previous = byte
    return bytes(output)


def smooth_telemetry() -> bytes:
    rng = random.Random(2026072301)
    values = []
    for index in range(DATASET_SIZE):
        value = (
            128
            + 58 * math.sin(2 * math.pi * index / 4_096)
            + 19 * math.sin(2 * math.pi * index / 257)
            + 5 * math.sin(2 * math.pi * index / 31)
            + rng.choice((-1, 0, 0, 0, 1))
        )
        values.append(max(0, min(255, round(value))))
    return bytes(values)


def piecewise_memory() -> bytes:
    output = bytearray()
    rng = random.Random(2026072302)
    record = 0
    while len(output) < DATASET_SIZE:
        slow = (record // 32) % 256
        fast = record % 256
        status = 0xA5 if (record // 128) % 2 == 0 else 0x5A
        payload = bytes(
            [
                0x41,
                0x52,
                0x41,
                status,
                slow,
                fast,
                (slow + fast) % 256,
                (slow - fast) % 256,
            ]
        )
        payload += bytes([slow] * 24)
        payload += bytes([(fast + offset) % 256 for offset in range(16)])
        payload += bytes(rng.choice((0, 0, 0, 1, 255)) for _ in range(16))
        output.extend(payload)
        record += 1
    return bytes(output[:DATASET_SIZE])


def bytes_from_files(paths: list[Path]) -> bytes:
    output = bytearray()
    for path in paths:
        if path.exists():
            output.extend(path.read_bytes())
            output.extend(b"\n\n")
        if len(output) >= DATASET_SIZE:
            break
    if len(output) < DATASET_SIZE:
        raise RuntimeError("not enough source bytes for frozen dataset")
    return bytes(output[:DATASET_SIZE])


def make_datasets() -> dict[str, bytes]:
    markdown_paths = [
        REPO / "WHAT_IS_ARA.md",
        REPO / "GLOSSARY.md",
        REPO / "ARA_SCALE.md",
        REPO / "ARA_FOUNDATIONS_FROM_ESTABLISHED_MECHANICS.md",
    ]
    python_paths = sorted((REPO / "analysis").rglob("*.py"))
    return {
        "smooth_telemetry": smooth_telemetry(),
        "piecewise_memory": piecewise_memory(),
        "ara_text": bytes_from_files(markdown_paths),
        "python_source": bytes_from_files(python_paths),
        "uniform_random": random.Random(2026072303).randbytes(DATASET_SIZE),
    }


def run_compression(datasets: dict[str, bytes]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for name, data in datasets.items():
        raw_zlib = zlib.compress(data, level=9)
        delta = delta_encode(data)
        delta_zlib = zlib.compress(delta, level=9)
        for block_size in BLOCK_SIZES:
            encoded = ara_encode(data, block_size)
            restored = ara_decode(encoded)
            compressed = zlib.compress(encoded, level=9)
            rows.append(
                {
                    "dataset": name,
                    "dataset_class": (
                        "structured_numeric"
                        if name in {"smooth_telemetry", "piecewise_memory"}
                        else "random_control"
                        if name == "uniform_random"
                        else "generalization"
                    ),
                    "block_size": block_size,
                    "is_primary_block": block_size == PRIMARY_BLOCK_SIZE,
                    "original_bytes": len(data),
                    "ara_serialized_bytes": len(encoded),
                    "raw_zlib_bytes": len(raw_zlib),
                    "delta_zlib_bytes": len(delta_zlib),
                    "ara_zlib_bytes": len(compressed),
                    "ara_vs_raw_improvement": (len(raw_zlib) - len(compressed))
                    / len(raw_zlib),
                    "ara_vs_delta_improvement": (len(delta_zlib) - len(compressed))
                    / len(delta_zlib),
                    "restored_exactly": restored == data,
                    "original_sha256": sha256(data),
                    "restored_sha256": sha256(restored),
                    "ara_stream_sha256": sha256(encoded),
                }
            )
    return rows


def run_security(datasets: dict[str, bytes]) -> dict[str, object]:
    data = datasets["smooth_telemetry"]
    ara_stream = ara_encode(data, PRIMARY_BLOCK_SIZE)

    attacker_recovered = ara_decode(ara_stream)

    compressed = zlib.compress(ara_stream, level=9)
    key = hashlib.sha256(b"ARA public deterministic AES-GCM test key 2026-07-23").digest()
    nonce = hashlib.sha256(b"smooth_telemetry unique test nonce").digest()[:12]
    associated_data = b"ARA-memory-test-v1"
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, compressed, associated_data)
    decrypted = aesgcm.decrypt(nonce, ciphertext, associated_data)
    encrypted_restored = ara_decode(zlib.decompress(decrypted))

    tampered = bytearray(ciphertext)
    tampered[len(tampered) // 2] ^= 0x01
    tamper_rejected = False
    try:
        aesgcm.decrypt(nonce, bytes(tampered), associated_data)
    except InvalidTag:
        tamper_rejected = True

    ciphertext_with_nonce = nonce + ciphertext
    ciphertext_zlib = zlib.compress(ciphertext_with_nonce, level=9)
    return {
        "dataset": "smooth_telemetry",
        "naive_attacker_exact_recovery": attacker_recovered == data,
        "naive_attacker_sha256": sha256(attacker_recovered),
        "authenticated_roundtrip_exact": encrypted_restored == data,
        "tampered_ciphertext_rejected": tamper_rejected,
        "compressed_plaintext_bytes": len(compressed),
        "ciphertext_plus_nonce_bytes": len(ciphertext_with_nonce),
        "authenticated_overhead_bytes": len(ciphertext_with_nonce) - len(compressed),
        "ciphertext_then_zlib_bytes": len(ciphertext_zlib),
        "ciphertext_compression_improvement": (
            len(ciphertext_with_nonce) - len(ciphertext_zlib)
        )
        / len(ciphertext_with_nonce),
        "test_vector_key_sha256": sha256(key),
        "nonce_hex": nonce.hex(),
        "ciphertext_sha256": sha256(ciphertext_with_nonce),
    }


def write_summary(rows: list[dict[str, object]]) -> None:
    import csv

    with SUMMARY.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    datasets = make_datasets()
    rows = run_compression(datasets)
    security = run_security(datasets)
    primary = [row for row in rows if row["is_primary_block"]]
    structured = [
        row for row in primary if row["dataset_class"] == "structured_numeric"
    ]
    random_control = next(
        row for row in primary if row["dataset_class"] == "random_control"
    )

    restoration_pass = all(bool(row["restored_exactly"]) for row in rows)
    compression_pass = (
        restoration_pass
        and all(float(row["ara_vs_raw_improvement"]) >= 0.05 for row in structured)
        and float(random_control["ara_vs_raw_improvement"]) <= 0.01
    )
    naive_confidentiality_pass = not bool(
        security["naive_attacker_exact_recovery"]
    )
    authenticated_wrapper_pass = bool(
        security["authenticated_roundtrip_exact"]
        and security["tampered_ciphertext_rejected"]
    )

    result = {
        "status": "completed",
        "protocol_sha256": sha256(PROTOCOL.read_bytes()),
        "dataset_size_bytes_each": DATASET_SIZE,
        "datasets": list(datasets),
        "block_sizes": list(BLOCK_SIZES),
        "primary_block_size": PRIMARY_BLOCK_SIZE,
        "restoration_pass": restoration_pass,
        "compression_hypothesis_pass": compression_pass,
        "naive_other_confidentiality_pass": naive_confidentiality_pass,
        "authenticated_wrapper_pass": authenticated_wrapper_pass,
        "prime_replacement_status": "NOT ESTABLISHED",
        "primary_rows": primary,
        "all_rows": rows,
        "security": security,
        "interpretation": {
            "restoration": (
                "Parent roots plus all signed Other coefficients form an exactly reversible "
                "memory representation in the tested implementation."
            ),
            "compression": (
                "Compression is earned only when the residual coefficients are lower entropy "
                "than the raw bytes; random data is the required failure control."
            ),
            "security": (
                "The unkeyed transform is public and reversible, so it provides no "
                "confidentiality. AES-GCM can protect it, but the security is AES-GCM's."
            ),
            "public_key": (
                "No trapdoor or key-establishment hardness assumption was defined; the test "
                "does not support replacing prime-based public-key cryptography."
            ),
        },
    }
    RESULTS.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    write_summary(rows)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
