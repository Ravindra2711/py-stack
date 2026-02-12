#!/usr/bin/env python3
"""
CLI entry point – the `scanner` command.

Usage:
  python -m scanner scan -i repos.json -o report.json --concurrency 4 --cleanup
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys

from .input_parser import parse_input_file
from .scanner import scan


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-7s  %(message)s",
        datefmt="%H:%M:%S",
    )
    logger = logging.getLogger("scanner")

    parser = argparse.ArgumentParser(
        prog="scanner",
        description="Tech Stack Bulk Scanner – analyse git repositories and report their tech stack",
    )
    sub = parser.add_subparsers(dest="command")

    scan_cmd = sub.add_parser("scan", help="Scan a list of repositories")
    scan_cmd.add_argument("-i", "--input", required=True, help="Path to input file (JSON or TXT)")
    scan_cmd.add_argument("-o", "--output", default="report.json", help="Path to output JSON file (default: report.json)")
    scan_cmd.add_argument("--concurrency", type=int, default=1, help="Number of parallel scans (default: 1)")
    scan_cmd.add_argument("--cleanup", action="store_true", help="Remove temp folders after scan")

    args = parser.parse_args()

    if args.command != "scan":
        parser.print_help()
        sys.exit(1)

    input_path = os.path.abspath(args.input)
    output_path = os.path.abspath(args.output)

    logger.info(f"Input:       {input_path}")
    logger.info(f"Output:      {output_path}")
    logger.info(f"Concurrency: {args.concurrency}")
    logger.info(f"Cleanup:     {args.cleanup}")

    # 1. Parse input
    repos = parse_input_file(args.input)
    if not repos:
        logger.warning("No repositories found in input file.")
        return

    # 2. Run scan
    reports = scan(repos, concurrency=args.concurrency, cleanup=args.cleanup)

    # 3. Write output
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(reports, f, indent=2, ensure_ascii=False)

    successful = sum(1 for r in reports if r.get("status") == "success")
    failed = sum(1 for r in reports if r.get("status") == "error")
    logger.info(f"Report written to {output_path}")
    logger.info(f"Results: {successful} succeeded, {failed} failed out of {len(reports)}")


if __name__ == "__main__":
    main()
