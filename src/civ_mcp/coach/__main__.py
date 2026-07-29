"""Entry point: ``python -m civ_mcp.coach``.

Launched by ``Start Civ6 Coach.bat``.  Prints a banner, wires logging, and
runs the persistent bridge until Ctrl+C.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from civ_mcp.coach.bridge import CoachBridge, DEFAULT_OUTPUT_DIR


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="python -m civ_mcp.coach",
        description="Civ VI AI Coach — one-hotkey full-state copier.",
    )
    p.add_argument("--host", default="127.0.0.1", help="Tuner host (default 127.0.0.1)")
    p.add_argument("--port", type=int, default=4318, help="Tuner port (default 4318)")
    p.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Snapshot output directory (default {DEFAULT_OUTPUT_DIR})",
    )
    p.add_argument("--verbose", "-v", action="count", default=0, help="Verbose logging")
    p.add_argument(
        "--test-once",
        action="store_true",
        help="Take one snapshot then exit — useful for debugging without a hotkey.",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    level = logging.WARNING - (10 * min(args.verbose, 2))
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    bridge = CoachBridge(output_dir=args.output, host=args.host, port=args.port)
    if args.test_once:
        async def _once() -> int:
            try:
                await bridge.conn.connect()
            except ConnectionError as e:
                print(f"cannot connect: {e}", file=sys.stderr)
                return 2
            await bridge.trigger_snapshot()
            await bridge.conn.disconnect()
            return 0

        return asyncio.run(_once())
    try:
        asyncio.run(bridge.run())
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
