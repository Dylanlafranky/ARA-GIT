"""Inspect a public HDF5 file through HTTP byte-range requests.

This avoids downloading multi-gigabyte lifetime records merely to discover their
schema. The reader is intentionally read-only and caches fixed-size byte blocks.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
import urllib.request
from collections import OrderedDict

import h5py


class HTTPRangeReader(io.RawIOBase):
    def __init__(self, url: str, size: int, block_size: int = 1024 * 1024, max_blocks: int = 64):
        self.url = url
        self.size = size
        self.block_size = block_size
        self.max_blocks = max_blocks
        self.pos = 0
        self.cache: OrderedDict[int, bytes] = OrderedDict()

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return True

    def tell(self) -> int:
        return self.pos

    def seek(self, offset: int, whence: int = io.SEEK_SET) -> int:
        if whence == io.SEEK_SET:
            new_pos = offset
        elif whence == io.SEEK_CUR:
            new_pos = self.pos + offset
        elif whence == io.SEEK_END:
            new_pos = self.size + offset
        else:
            raise ValueError(f"Unsupported whence: {whence}")
        if new_pos < 0:
            raise ValueError("Negative seek position")
        self.pos = min(new_pos, self.size)
        return self.pos

    def _block(self, block_index: int) -> bytes:
        if block_index in self.cache:
            data = self.cache.pop(block_index)
            self.cache[block_index] = data
            return data

        start = block_index * self.block_size
        end = min(start + self.block_size, self.size) - 1
        req = urllib.request.Request(self.url, headers={"Range": f"bytes={start}-{end}"})
        with urllib.request.urlopen(req, timeout=120) as response:
            data = response.read()
        expected = end - start + 1
        if len(data) != expected:
            raise IOError(f"Range {start}-{end} returned {len(data)} bytes; expected {expected}")
        print(f"fetched block {block_index}: {start}-{end}", file=sys.stderr, flush=True)
        self.cache[block_index] = data
        while len(self.cache) > self.max_blocks:
            self.cache.popitem(last=False)
        return data

    def readinto(self, buffer) -> int:
        view = memoryview(buffer).cast("B")
        if self.pos >= self.size or len(view) == 0:
            return 0
        remaining = min(len(view), self.size - self.pos)
        copied = 0
        while copied < remaining:
            block_index = self.pos // self.block_size
            block_offset = self.pos % self.block_size
            block = self._block(block_index)
            take = min(remaining - copied, len(block) - block_offset)
            view[copied : copied + take] = block[block_offset : block_offset + take]
            self.pos += take
            copied += take
        return copied


def serializable(value):
    if hasattr(value, "tolist"):
        value = value.tolist()
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, list):
        return [serializable(item) for item in value]
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("size", type=int)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    reader = HTTPRangeReader(args.url, args.size)
    report = {"url": args.url, "size": args.size, "root_attributes": {}, "objects": []}
    with h5py.File(reader, "r") as handle:
        report["root_attributes"] = {key: serializable(value) for key, value in handle.attrs.items()}
        for name in handle.keys():
            obj = handle[name]
            item = {
                "path": name,
                "kind": "dataset" if isinstance(obj, h5py.Dataset) else "group",
            }
            if isinstance(obj, h5py.Dataset):
                item.update(
                    {
                        "shape": list(obj.shape),
                        "dtype": str(obj.dtype),
                        "chunks": list(obj.chunks) if obj.chunks else None,
                        "compression": obj.compression,
                    }
                )
                if name in {"behavior_names", "node_names"}:
                    item["values"] = serializable(obj[...])
            report["objects"].append(item)

    with open(args.output, "w", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
