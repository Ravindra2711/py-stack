"""
Reporter – transforms the raw matched list into a rich categorised report.
"""

from __future__ import annotations

from typing import Any

# ── Category mapping ───────────────────────────────────────

CATEGORY_MAP: dict[str, str] = {
    "language":         "languages",
    "framework":        "frameworks",
    "ui_framework":     "ui",
    "ui":               "ui",
    "db":               "databases",
    "orm":              "orm",
    "ai":               "ai",
    "monitoring":       "monitoring",
    "analytics":        "analytics",
    "cloud":            "cloud",
    "hosting":          "hosting",
    "ci":               "ci",
    "test":             "testing",
    "auth":             "auth",
    "payment":          "payment",
    "notification":     "notification",
    "cms":              "cms",
    "queue":            "queue",
    "storage":          "storage",
    "iac":              "iac",
    "security":         "security",
    "automation":       "automation",
    "builder":          "builders",
    "linter":           "linters",
    "package_manager":  "packageManagers",
    "ssg":              "ssg",
    "validation":       "validation",
    "tool":             "tools",
    "saas":             "tools",
    "runtime":          "tools",
    "app":              "tools",
    "network":          "tools",
    "unknown":          "tools",
}

ALL_BUCKETS = [
    "languages", "frameworks", "ui", "databases", "orm",
    "ai", "monitoring", "analytics", "cloud", "hosting",
    "ci", "testing", "auth", "payment", "notification",
    "cms", "queue", "storage", "iac", "security",
    "automation", "builders", "linters", "packageManagers",
    "ssg", "validation", "tools",
]


def categorise(matched: list[dict]) -> dict[str, list[str]]:
    """Group matched techs into named buckets. Empty buckets are stripped."""
    results: dict[str, list[str]] = {b: [] for b in ALL_BUCKETS}

    for node in matched:
        bucket = CATEGORY_MAP.get(node["type"], "tools")
        results[bucket].append(node["name"])

    # Deduplicate each bucket
    for key in list(results.keys()):
        results[key] = list(dict.fromkeys(results[key]))

    # Remove empty arrays
    return {k: v for k, v in results.items() if v}


def build_success_report(repo_name: str, matched: list[dict]) -> dict[str, Any]:
    return {
        "repo": repo_name,
        "status": "success",
        "results": categorise(matched),
    }


def build_error_report(repo_name: str, error: Exception | str) -> dict[str, Any]:
    return {
        "repo": repo_name,
        "status": "error",
        "error": str(error),
    }
