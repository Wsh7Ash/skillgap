"""Command-line interface for skillgap."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .skillgap import evaluate, load_skills_json, render_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="skillgap",
        description="Replay example inputs against a skill corpus to find coverage gaps and ambiguity.",
    )
    parser.add_argument("corpus", help="JSON file: [{\"name\":...,\"triggers\":[...]}, ...]")
    parser.add_argument(
        "--examples", help="File with one example input per line (default: read stdin)"
    )
    parser.add_argument(
        "--fail-on-issues", action="store_true",
        help="Exit 1 if any gap or ambiguous example is found (for CI)",
    )
    args = parser.parse_args(argv)

    skills = load_skills_json(args.corpus)
    if args.examples:
        lines = Path(args.examples).read_text(encoding="utf-8").splitlines()
    else:
        lines = sys.stdin.read().splitlines()
    examples = [ln for ln in lines if ln.strip()]

    results = evaluate(examples, skills)
    print(render_report(results, skills))

    if args.fail_on_issues:
        bad = [r for r in results if r.status != "ok"]
        return 1 if bad else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
