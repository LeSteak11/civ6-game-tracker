#!/usr/bin/env python3
"""Syntax-check every coach Lua query without needing the game running.

Loads each builder in ``civ_mcp.coach.queries`` and parses the emitted
chunk with an embedded Lua 5.3 runtime.  Catches the class of bug that
otherwise only shows up as a cryptic runtime error mid-snapshot.

    python scripts/lint_lua.py

Requires ``lupa`` (pip install lupa).  Exits non-zero on any parse error.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

try:
    import lupa
except ImportError:
    print("lupa not installed — run: pip install lupa", file=sys.stderr)
    raise SystemExit(2)

from civ_mcp.coach import queries as Q  # noqa: E402


def main() -> int:
    lua = lupa.LuaRuntime(unpack_returned_tuples=True)
    load = lua.eval('function(s) local f, e = load(s, "chunk"); return (f ~= nil), e end')

    failed = 0
    for name, build in Q.ALL_QUERIES.items():
        src = build()
        ok, err = load(src)
        if ok:
            print(f"  {name:9s} OK    ({len(src):,} chars)")
        else:
            failed += 1
            print(f"  {name:9s} FAIL  ({len(src):,} chars)")
            print(f"      {err}")

    print()
    if failed:
        print(f"{failed} query builder(s) failed Lua syntax check.")
        return 1
    print(f"All {len(Q.ALL_QUERIES)} query builders parse as valid Lua 5.3.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
