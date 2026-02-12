"""
Repo Manager – handles git clone / pull / validation and
provides a local path ready for analysis.
"""

from __future__ import annotations

import hashlib
import logging
import os
import re
import shutil
import subprocess
import tempfile

logger = logging.getLogger("scanner")

WORKSPACE_ROOT = os.path.join(tempfile.gettempdir(), "scanner-workspace")


def _safe_folder_name(name: str, url: str) -> str:
    """Slugify + hash to produce a unique, filesystem-safe folder name."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    h = hashlib.sha256(url.encode()).hexdigest()[:8]
    return f"{slug}-{h}"


def _validate_url(url: str) -> None:
    """Very basic URL validation – only allow known-safe protocols."""
    allowed = ("http:", "https:", "ssh:", "file:", "git@")
    lower = url.lower()
    if not any(lower.startswith(p) for p in allowed):
        raise ValueError(f'Unsupported URL protocol in "{url}". Allowed: {", ".join(allowed)}')
    if re.search(r"[;&|`$]", url):
        raise ValueError(f'URL contains suspicious characters: "{url}"')


def _is_local_path(url: str) -> bool:
    return (
        url.startswith("/")
        or url.startswith(".")
        or bool(re.match(r"^[a-zA-Z]:\\", url))
        or url.startswith("~")
    )


def prepare_repo(name: str, url: str) -> tuple[str, bool]:
    """
    Prepare the local directory for a repo entry.

    Returns (local_path, is_temporary).
    """
    if _is_local_path(url):
        return _prepare_local(url), False

    _validate_url(url)
    return _prepare_remote(name, url), True


def _prepare_local(local_url: str) -> str:
    resolved = os.path.abspath(os.path.expanduser(local_url))
    if not os.path.exists(resolved):
        raise FileNotFoundError(f"Local path does not exist: {resolved}")

    sensitive = ["/etc", "/usr", "/bin", "/sbin", "C:\\Windows", "C:\\Program Files"]
    for s in sensitive:
        if resolved.lower().startswith(s.lower()):
            raise ValueError(f'Path "{resolved}" is inside a sensitive directory.')
    return resolved


def _prepare_remote(name: str, url: str) -> str:
    folder = _safe_folder_name(name, url)
    target_dir = os.path.join(WORKSPACE_ROOT, folder)
    os.makedirs(WORKSPACE_ROOT, exist_ok=True)

    if os.path.isdir(target_dir):
        # Check origin matches
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=target_dir, capture_output=True, text=True, timeout=30,
            )
            current_origin = result.stdout.strip()
            if current_origin and current_origin != url.strip():
                raise RuntimeError(
                    f'Directory "{target_dir}" already exists with a different origin.\n'
                    f"  Expected: {url}\n  Found:    {current_origin}"
                )
            logger.info(f'Pulling latest for "{name}"…')
            subprocess.run(["git", "pull"], cwd=target_dir, capture_output=True, timeout=120)
        except RuntimeError:
            raise
        except Exception as err:
            logger.warning(f'Pull failed for "{name}", re-cloning: {err}')
            shutil.rmtree(target_dir, ignore_errors=True)
            _clone_fresh(url, target_dir, name)
    else:
        _clone_fresh(url, target_dir, name)

    return target_dir


def _clone_fresh(url: str, target_dir: str, name: str) -> None:
    logger.info(f'Cloning "{name}" from {url}…')
    subprocess.run(
        ["git", "clone", "--depth", "1", url, target_dir],
        capture_output=True, text=True, timeout=300, check=True,
    )


def cleanup_repo(local_path: str) -> None:
    """Remove a previously cloned directory."""
    logger.info(f"Cleaning up {local_path}")
    shutil.rmtree(local_path, ignore_errors=True)
