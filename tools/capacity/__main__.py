"""CLI: ``python -m capacity [scenario ...]`` prints Markdown capacity tables."""

from __future__ import annotations

import argparse
import sys

from .model import estimate, to_markdown
from .scenarios import SCENARIOS


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="capacity", description=__doc__)
    parser.add_argument("scenarios", nargs="*", help="scenario keys (default: all)")
    parser.add_argument("--list", action="store_true", help="list scenario keys and exit")
    args = parser.parse_args(argv)

    if args.list:
        for key, w in SCENARIOS.items():
            print(f"{key:24} {w.name}")
        return 0

    keys = args.scenarios or list(SCENARIOS)
    unknown = [k for k in keys if k not in SCENARIOS]
    if unknown:
        print(f"unknown scenario(s): {', '.join(unknown)}", file=sys.stderr)
        return 2

    for key in keys:
        w = SCENARIOS[key]
        print(f"### {w.name}\n")
        print(to_markdown(estimate(w)))
        for note in w.notes:
            print(f"\n> Note: {note}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
