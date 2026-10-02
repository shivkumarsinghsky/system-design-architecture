#!/usr/bin/env python3
"""Keep the capacity tables in docs/designs/*.md in sync with tools/capacity.

Each design marks a generated region:

    <!-- capacity:url-shortener:start -->
    ...generated table...
    <!-- capacity:url-shortener:end -->

Usage:
    python scripts/sync_capacity_tables.py           # check, exit 1 on drift (CI)
    python scripts/sync_capacity_tables.py --write   # regenerate in place
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from capacity import SCENARIOS, estimate, to_markdown  # noqa: E402

PATTERN = re.compile(
    r"(<!-- capacity:(?P<key>[a-z0-9-]+):start -->\n)(?P<body>.*?)(<!-- capacity:(?P=key):end -->)",
    re.DOTALL,
)


def render(key: str) -> str:
    return to_markdown(estimate(SCENARIOS[key])) + "\n"


def main(write: bool) -> int:
    drift: list[str] = []
    seen: set[str] = set()
    for doc in sorted((ROOT / "docs" / "designs").glob("*.md")):
        text = doc.read_text(encoding="utf-8")

        def repl(m: re.Match[str], doc: Path = doc) -> str:
            key = m.group("key")
            if key not in SCENARIOS:
                raise SystemExit(f"{doc.name}: unknown capacity scenario '{key}'")
            seen.add(key)
            expected = render(key)
            if m.group("body") != expected:
                drift.append(f"{doc.relative_to(ROOT)} [{key}]")
            return m.group(1) + expected + m.group(4)

        new = PATTERN.sub(repl, text)
        if write and new != text:
            doc.write_text(new, encoding="utf-8")

    missing = sorted(set(SCENARIOS) - seen)
    if missing:
        print(f"scenarios not referenced by any design: {', '.join(missing)}")
        return 1
    if drift and not write:
        print("capacity tables out of date (run with --write):")
        for d in drift:
            print(f"  - {d}")
        return 1
    print(f"capacity tables OK ({len(seen)} scenarios)" if not write else "capacity tables written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(write="--write" in sys.argv))
