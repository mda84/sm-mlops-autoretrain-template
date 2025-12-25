from __future__ import annotations

import hashlib
import json
import pathlib
from typing import Dict


def compute_file_sha256(path: str | pathlib.Path) -> str:
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha.update(chunk)
    return sha.hexdigest()


def compute_dataset_fingerprint(directory: str | pathlib.Path) -> str:
    base = pathlib.Path(directory)
    hashes: Dict[str, str] = {}
    for file in sorted(p for p in base.rglob("*") if p.is_file()):
        hashes[str(file.relative_to(base))] = compute_file_sha256(file)
    payload = json.dumps(hashes, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
