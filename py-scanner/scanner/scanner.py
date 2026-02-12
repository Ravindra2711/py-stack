"""
Core scan loop – orchestrates repo preparation, analysis, and reporting
across multiple repositories with controlled concurrency.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from .repo_manager import prepare_repo, cleanup_repo
from .analyser import analyse
from .reporter import build_success_report, build_error_report

logger = logging.getLogger("scanner")


def _scan_one(name: str, url: str, cleanup: bool) -> dict:
    """Scan a single repository."""
    logger.info(f"[{name}] Preparing…")
    try:
        local_path, is_temporary = prepare_repo(name, url)
        logger.info(f"[{name}] Analysing {local_path}…")

        matched = analyse(local_path)

        report = build_success_report(name, matched)
        results = report.get("results", {})
        counts = ", ".join(f"{len(v)} {k}" for k, v in results.items())
        logger.info(f"[{name}] Done – {counts}")

        if cleanup and is_temporary:
            cleanup_repo(local_path)

        return report
    except Exception as err:
        logger.error(f"[{name}] Failed: {err}")
        return build_error_report(name, err)


def scan(repos: list[dict[str, str]], concurrency: int = 1, cleanup: bool = False) -> list[dict]:
    """
    Scan a list of repositories and return an array of per-repo reports.
    Each repo dict must have 'name' and 'url' keys.
    """
    logger.info(f"Starting scan of {len(repos)} repo(s) (concurrency={concurrency})")

    if concurrency <= 1:
        return [_scan_one(r["name"], r["url"], cleanup) for r in repos]

    reports: list[dict] = [{}] * len(repos)
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        future_to_idx = {
            executor.submit(_scan_one, r["name"], r["url"], cleanup): i
            for i, r in enumerate(repos)
        }
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                reports[idx] = future.result()
            except Exception as err:
                reports[idx] = build_error_report(repos[idx]["name"], err)

    return reports
