"""
Input Parser – reads the repo list from a JSON or plain-text file.
"""

from __future__ import annotations

import json
import os
import re


def _name_from_url(url: str) -> str:
    """Derive a repo name from a URL."""
    cleaned = url.rstrip("/").removesuffix(".git")
    last = cleaned.rsplit("/", 1)[-1]
    return last or "unknown"


def parse_input_file(file_path: str) -> list[dict[str, str]]:
    """
    Parse an input file (JSON array or one-URL-per-line text).
    Returns list of {"name": str, "url": str}.
    """
    abs_path = os.path.abspath(file_path)
    if not os.path.isfile(abs_path):
        raise FileNotFoundError(f"Input file not found: {abs_path}")

    with open(abs_path, "r", encoding="utf-8") as f:
        raw = f.read().strip()

    # Attempt JSON first
    if raw.startswith("["):
        arr = json.loads(raw)
        return [
            {"name": item.get("name", _name_from_url(item["url"])), "url": item["url"]}
            for item in arr
        ]

    # Otherwise treat as plain text (one URL per line)
    repos: list[dict[str, str]] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        repos.append({"name": _name_from_url(line), "url": line})
    return repos
