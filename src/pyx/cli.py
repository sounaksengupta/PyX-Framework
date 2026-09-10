"""Command-line interface for PyTestX."""

from __future__ import annotations

import argparse
from pathlib import Path

from pyx.engine import TestDefinitionError, TestExecutionError, run_test_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pyx", description="Run PyTestX YAML tests.")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="run a YAML test file")
    run.add_argument("test_file", type=Path)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command != "run":
        return
    try:
        result = run_test_file(args.test_file)
    except (TestDefinitionError, TestExecutionError) as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(2) from exc

    print("PyTestX Test Runner")
    print(f"Test: {result.name}")
    for step in result.steps:
        state = "PASS" if step.passed else "FAIL"
        suffix = f" — {step.error}" if step.error else ""
        print(f"  {state} {step.keyword}{suffix}")
    print(f"\n{'PASSED' if result.passed else 'FAILED'} ({len(result.steps)} steps)")
    if not result.passed:
        raise SystemExit(1)
