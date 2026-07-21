"""Primary PN18 recursive TE-ARA product-tree builder.

The target path contains no primality-test function and reads no nearby-prime
table. It recursively couples all lower prime children into one product root,
couples the p29-wheel candidates into a second tree, and seals the first leaf
whose GCD relation with the child root is one.
"""

from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "PN18_RECURSIVE_TEARA_PRODUCT_TREE_PROTOCOL_v1_FROZEN.md"
FREEZE = HERE / "PN18_TARGET_FREEZE_MANIFEST.json"
RESULT = HERE / "PN18_RECURSIVE_TEARA_PRODUCT_TREE_PREDICTION.json"
CHILD_ROOT_FILE = HERE / "PN18_TARGET_CHILD_PRODUCT_ROOT.bin"
EXPECTED_PROTOCOL_SHA256 = "5D989C96641C91676DFADD6277AE4DA06037ABAABA2018D3028DBD6EE3EA40FF"

WINDOW = 65_536
TARGET_ANCHOR = 700_000_000_000
P29_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29)
P29_PRIMORIAL = math.prod(P29_PRIMES)
DEVELOPMENT = {
    100_000_000: 100_000_007,
    1_000_000_000: 1_000_000_007,
    10_000_000_000: 10_000_000_019,
    100_000_000_000: 100_000_000_003,
    400_000_000_000: 400_000_000_019,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def eratosthenes(limit: int) -> list[int]:
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for prime in range(2, math.isqrt(limit) + 1):
        if sieve[prime]:
            start = prime * prime
            sieve[start : limit + 1 : prime] = b"\x00" * (((limit - start) // prime) + 1)
    return [value for value in range(2, limit + 1) if sieve[value]]


def recursive_product(values: list[int]) -> tuple[int, dict]:
    if not values:
        return 1, {
            "levels": 0,
            "level_node_counts": [],
            "nodes_created_including_leaves": 0,
            "peak_level_payload_bits": 0,
            "sum_level_payload_bits": 0,
        }
    current = list(values)
    level_counts: list[int] = []
    level_payload_bits: list[int] = []
    while True:
        level_counts.append(len(current))
        level_payload_bits.append(sum(value.bit_length() for value in current))
        if len(current) == 1:
            break
        next_level: list[int] = []
        for index in range(0, len(current), 2):
            if index + 1 < len(current):
                next_level.append(current[index] * current[index + 1])
            else:
                next_level.append(current[index])
        current = next_level
    return current[0], {
        "levels": len(level_counts),
        "level_node_counts": level_counts,
        "level_payload_bits": level_payload_bits,
        "nodes_created_including_leaves": sum(level_counts),
        "peak_level_payload_bits": max(level_payload_bits),
        "sum_level_payload_bits": sum(level_payload_bits),
    }


@dataclass(slots=True)
class CandidateNode:
    lo: int
    hi: int
    product: int
    left: "CandidateNode | None" = None
    right: "CandidateNode | None" = None


def build_candidate_tree(values: list[int], lo: int = 0, hi: int | None = None) -> CandidateNode:
    if hi is None:
        hi = len(values)
    if hi <= lo:
        raise ValueError("candidate tree cannot contain an empty branch")
    if hi - lo == 1:
        return CandidateNode(lo=lo, hi=hi, product=values[lo])
    mid = (lo + hi) // 2
    left = build_candidate_tree(values, lo, mid)
    right = build_candidate_tree(values, mid, hi)
    return CandidateNode(lo=lo, hi=hi, product=left.product * right.product, left=left, right=right)


def tree_payload(node: CandidateNode) -> tuple[int, int, int]:
    """Return node count, total payload bits, and peak single-node bits."""
    nodes = 1
    total_bits = node.product.bit_length()
    peak_bits = node.product.bit_length()
    if node.left is not None:
        child_nodes, child_bits, child_peak = tree_payload(node.left)
        nodes += child_nodes
        total_bits += child_bits
        peak_bits = max(peak_bits, child_peak)
    if node.right is not None:
        child_nodes, child_bits, child_peak = tree_payload(node.right)
        nodes += child_nodes
        total_bits += child_bits
        peak_bits = max(peak_bits, child_peak)
    return nodes, total_bits, peak_bits


def first_quiet_from_tree(
    root: CandidateNode,
    candidates: list[int],
    child_root: int,
    anchor: int,
) -> tuple[int, dict]:
    trace: list[dict] = []
    visited_nodes = 0
    explicit_leaf_queries = 0
    internal_all_quiet_shortcuts = 0

    def descend(node: CandidateNode) -> int | None:
        nonlocal visited_nodes, explicit_leaf_queries, internal_all_quiet_shortcuts
        relation = math.gcd(node.product, child_root)
        visited_nodes += 1
        is_leaf = node.hi - node.lo == 1
        if is_leaf:
            explicit_leaf_queries += 1
        if len(trace) < 128:
            trace.append({
                "candidate_index_start": node.lo,
                "candidate_index_end_exclusive": node.hi,
                "leaf_count": node.hi - node.lo,
                "first_offset": candidates[node.lo] - anchor if candidates else None,
                "last_offset": candidates[node.hi - 1] - anchor if candidates else None,
                "relation_is_one": relation == 1,
                "relation_bit_length": relation.bit_length(),
                "is_leaf": is_leaf,
            })
        if relation == 1:
            if not is_leaf:
                internal_all_quiet_shortcuts += 1
            return node.lo
        if is_leaf:
            return None
        found = descend(node.left)  # type: ignore[arg-type]
        if found is not None:
            return found
        return descend(node.right)  # type: ignore[arg-type]

    found_index = descend(root)
    if found_index is None:
        raise RuntimeError("No quiet p29-wheel candidate in the frozen window")
    return found_index, {
        "gcd_nodes_visited": visited_nodes,
        "explicit_candidate_leaves_queried": explicit_leaf_queries,
        "internal_all_quiet_shortcuts": internal_all_quiet_shortcuts,
        "visited_trace": trace,
    }


def p29_candidates(anchor: int) -> list[int]:
    return [
        anchor + offset
        for offset in range(1, WINDOW)
        if math.gcd(anchor + offset, P29_PRIMORIAL) == 1
    ]


def run_anchor(anchor: int) -> tuple[dict, int, bytes]:
    started = time.perf_counter()
    maximum = anchor + WINDOW - 1
    limit = math.isqrt(maximum)
    children = eratosthenes(limit)
    child_root, child_tree = recursive_product(children)
    child_root_bytes = child_root.to_bytes((child_root.bit_length() + 7) // 8, "big")

    candidates = p29_candidates(anchor)
    candidate_tree_started = time.perf_counter()
    candidate_root = build_candidate_tree(candidates)
    candidate_nodes, candidate_payload_bits, candidate_peak_bits = tree_payload(candidate_root)
    tree_build_seconds = time.perf_counter() - candidate_tree_started

    found_index, query = first_quiet_from_tree(candidate_root, candidates, child_root, anchor)
    predicted = candidates[found_index]
    correction = predicted - anchor
    odd_count = sum((anchor + offset) % 2 == 1 for offset in range(1, correction + 1))
    one_bit_odd_sieve_bytes = ((limit - 1) // 2 + 7) // 8
    row = {
        "anchor": anchor,
        "window": WINDOW,
        "block_end": maximum,
        "sqrt_block_end_floor": limit,
        "child_count": len(children),
        "child_ceiling": children[-1],
        "child_tree": child_tree,
        "child_root_bit_length": child_root.bit_length(),
        "child_root_byte_length": len(child_root_bytes),
        "child_list_uint32_bytes": len(children) * 4,
        "one_bit_odd_sieve_bytes": one_bit_odd_sieve_bytes,
        "pn17_collision_field_bytes": WINDOW * 2,
        "candidate_count_in_window_after_p29": len(candidates),
        "candidate_tree_nodes": candidate_nodes,
        "candidate_tree_total_payload_bits": candidate_payload_bits,
        "candidate_tree_peak_node_bits": candidate_peak_bits,
        "candidate_tree_transient_payload_bytes_ceil": (candidate_payload_bits + 7) // 8,
        "candidate_tree_build_seconds": tree_build_seconds,
        "correction": correction,
        "predicted_integer": predicted,
        "p29_candidate_rank_through_prediction": found_index + 1,
        "odd_scan_candidates_through_prediction": odd_count,
        "query": query,
        "total_primary_seconds": time.perf_counter() - started,
    }
    return row, child_root, child_root_bytes


def main() -> None:
    if sha256(PROTOCOL) != EXPECTED_PROTOCOL_SHA256:
        raise RuntimeError("Frozen PN18 protocol hash mismatch")
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    if freeze["protocol_sha256"] != EXPECTED_PROTOCOL_SHA256:
        raise RuntimeError("PN18 freeze manifest does not match the protocol")
    if freeze["target_anchor"] != TARGET_ANCHOR or freeze["window"] != WINDOW:
        raise RuntimeError("PN18 target configuration differs from the frozen manifest")
    if sha256(Path(__file__)) != freeze["primary_script_sha256"]:
        raise RuntimeError("PN18 primary script changed after target freeze")
    if RESULT.exists() or CHILD_ROOT_FILE.exists():
        raise RuntimeError("PN18 target artifacts already exist; refusing to overwrite")

    development: list[dict] = []
    for anchor, expected in DEVELOPMENT.items():
        row, _, _ = run_anchor(anchor)
        row["established_development_control"] = expected
        row["matches_development_control"] = row["predicted_integer"] == expected
        development.append(row)
    if not all(row["matches_development_control"] for row in development):
        raise RuntimeError("Development integrity failed; target remains unopened")

    target, _, root_bytes = run_anchor(TARGET_ANCHOR)
    CHILD_ROOT_FILE.write_bytes(root_bytes)
    target["child_root_file"] = CHILD_ROOT_FILE.name
    target["child_root_sha256"] = sha256(CHILD_ROOT_FILE)
    target["root_vs_uint32_list_byte_ratio"] = target["child_root_byte_length"] / target["child_list_uint32_bytes"]
    target["root_vs_one_bit_odd_sieve_byte_ratio"] = target["child_root_byte_length"] / target["one_bit_odd_sieve_bytes"]
    target["root_vs_pn17_collision_field_byte_ratio"] = target["child_root_byte_length"] / target["pn17_collision_field_bytes"]

    payload = {
        "test_id": "PN18/RECURSIVE-TEARA-PRODUCT-TREE/v1",
        "sealed_utc": datetime.now(timezone.utc).isoformat(),
        "protocol_sha256": sha256(PROTOCOL),
        "freeze_manifest_sha256": sha256(FREEZE),
        "separation": (
            "The target is the first p29-wheel leaf with GCD one against the complete lower-child product root. "
            "The primary builder contains no target primality-test function and reads no nearby-target prime label."
        ),
        "method_control": (
            "This is established primorial/product-tree/batch-GCD mathematics expressed as recursive ARA parents."
        ),
        "development": development,
        "target": target,
        "claims_not_yet_opened": {
            "predicted_integer_is_prime": None,
            "predicted_integer_is_first_prime_above_anchor": None,
        },
    }
    RESULT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "anchor": TARGET_ANCHOR,
        "correction": target["correction"],
        "sealed_prediction": target["predicted_integer"],
        "gcd_nodes_visited": target["query"]["gcd_nodes_visited"],
        "explicit_candidate_leaves_queried": target["query"]["explicit_candidate_leaves_queried"],
        "prediction_packet_sha256": sha256(RESULT),
        "target_primality_opened": False,
    }, indent=2))


if __name__ == "__main__":
    main()
