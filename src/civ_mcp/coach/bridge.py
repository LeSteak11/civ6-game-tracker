"""Coach bridge — the persistent process the launcher starts.

Responsibilities:
    1. Open a persistent GameConnection (auto-reconnects; discovers Lua
       states by name — no fixed index 5).
    2. Register the Ctrl+Shift+C global hotkey.
    3. When triggered: run every coach query, merge into a versioned
       snapshot, archive JSON + Markdown under the per-game folder in
       ``output/games/`` (see ``archive.py``), and copy the Markdown to
       the Windows clipboard.
    4. Keep the previous snapshot in memory (and on disk as
       ``latest-full.json``) so the next hotkey press produces a delta.

The Enter key in the terminal is a manual trigger fallback for when the
global hotkey can't register (e.g. another app owns Ctrl+Shift+C).
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import signal
import sys
import time  # noqa: F401 — used below for archive prefix fallback
from pathlib import Path
from typing import Any

from civ_mcp.connection import GameConnection
from civ_mcp.coach import COACH_VERSION, SCHEMA_VERSION
from civ_mcp.coach.archive import write_snapshot as archive_snapshot
from civ_mcp.coach.clipboard_win import ClipboardError, copy_text
from civ_mcp.coach.collector import collect_snapshot
from civ_mcp.coach.delta import compute_delta
from civ_mcp.coach.markdown import render_markdown

if sys.platform == "win32":
    from civ_mcp.coach.hotkey_win import HotkeyThread, start_hotkey
else:  # pragma: no cover
    HotkeyThread = None  # type: ignore[assignment]
    start_hotkey = None  # type: ignore[assignment]

log = logging.getLogger(__name__)


DEFAULT_OUTPUT_DIR = Path(os.environ.get("CIV6_COACH_OUTPUT", "output"))


class CoachBridge:
    def __init__(
        self,
        output_dir: Path = DEFAULT_OUTPUT_DIR,
        host: str = "127.0.0.1",
        port: int = 4318,
    ) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.conn = GameConnection(host=host, port=port)
        self._last_snapshot: dict[str, Any] | None = self._load_last_snapshot()
        self._in_flight = asyncio.Lock()  # one snapshot at a time
        self._snapshot_count = 0

    # ---- Persistence -----------------------------------------------------

    def _load_last_snapshot(self) -> dict[str, Any] | None:
        p = self.output_dir / "latest-full.json"
        if not p.exists():
            return None
        try:
            with p.open("r", encoding="utf-8") as f:
                snap = json.load(f)
            log.info("Loaded previous snapshot from %s (turn %s)", p, snap.get("meta", {}).get("turn"))
            return snap
        except Exception:  # noqa: BLE001
            log.warning("Could not parse existing latest-full.json — ignoring", exc_info=True)
            return None

    def _write_outputs(self, snap: dict[str, Any], md: str) -> str:
        """Write the capture and return a human-readable description.

        Snapshots with a trusted turn number go to the persistent per-game
        archive (``output/games/game-NNN_<civ>/``, see ``archive.py``):
        revisioned ``turn-XXXX_rNN`` files, per-game ``latest.*`` mirrors,
        content-hash dedup, and a ``game.json`` identity record keyed on
        the game/map seeds.

        Snapshots without one keep the legacy flat naming — we never guess
        which game a turnless capture belongs to:

        - meta failed but some other query worked (game IS loaded, we just
          couldn't read the turn number):    snapshot-partial-<epoch>-
        - no queries returned anything
          (probably at main menu):           snapshot-noturn-<epoch>-
        """
        # Root-level latest mirrors: kept for backward compatibility and as
        # the cross-restart delta seed (_load_last_snapshot reads it).
        with (self.output_dir / "latest-full.json").open("w", encoding="utf-8") as f:
            json.dump(snap, f, indent=2)
        (self.output_dir / "latest-coach.md").write_text(md, encoding="utf-8")

        res = archive_snapshot(self.output_dir, snap, md)
        if res is not None:
            rel = res.game_dir.name
            if res.deduplicated:
                return (
                    f"unchanged since {res.capture_name} — no new archive file "
                    f"(games/{rel}, latest.* refreshed)"
                )
            new_game = " [new game folder]" if res.created_game else ""
            return f"wrote games/{rel}/snapshots/{res.capture_name}.md + .json{new_game}"

        # Legacy fallback: no trusted turn number.
        status = snap.get("section_status") or {}
        any_ok = any(v == "ok" for v in status.values())
        ts = int(snap.get("generated_at_epoch") or time.time())
        prefix = f"snapshot-partial-{ts}" if any_ok else f"snapshot-noturn-{ts}"
        with (self.output_dir / f"{prefix}-full.json").open("w", encoding="utf-8") as f:
            json.dump(snap, f, indent=2)
        (self.output_dir / f"{prefix}-coach.md").write_text(md, encoding="utf-8")
        return f"wrote {prefix}-coach.md + -full.json (no trusted turn — not archived)"

    # ---- Hotkey callback --------------------------------------------------

    async def trigger_snapshot(self) -> None:
        if self._in_flight.locked():
            log.info("Snapshot already running — ignoring extra hotkey press")
            return
        async with self._in_flight:
            self._snapshot_count += 1
            n = self._snapshot_count
            print(f"\n[coach] snapshot #{n} starting...", flush=True)
            t0 = time.perf_counter()
            try:
                await self.conn.ensure_connected()
                snap = await collect_snapshot(self.conn)
            except ConnectionError as e:
                print(f"[coach] cannot reach Civ 6: {e}", flush=True)
                print(
                    "[coach] make sure Civ 6 is running with EnableTuner=1 "
                    "AND a save is loaded (not the main menu).",
                    flush=True,
                )
                return
            except Exception:  # noqa: BLE001
                log.exception("Snapshot failed")
                print("[coach] snapshot failed — see log for details.", flush=True)
                return

            delta = compute_delta(self._last_snapshot, snap)
            md = render_markdown(snap, delta)
            write_desc = self._write_outputs(snap, md)

            # Clipboard
            clip_status = "ok"
            try:
                copy_text(md)
            except ClipboardError as e:
                clip_status = f"failed ({e})"
            except NotImplementedError as e:
                clip_status = f"skipped ({e})"

            self._last_snapshot = snap
            dt = time.perf_counter() - t0
            m = snap.get("meta", {}) or {}
            e = snap.get("empire", {}) or {}
            mtot = snap.get("map_totals", {}) or {}
            print(
                f"[coach] snapshot #{n} OK — turn {m.get('turn')} "
                f"({m.get('civ_name')}/{m.get('leader_name')}) — {dt:.2f}s | "
                f"{len(md):,} md chars | "
                f"tiles: {mtot.get('revealed', 0)}rev/{mtot.get('visible', 0)}vis | "
                f"cities: {e.get('num_cities')} | units: {e.get('num_units')} | "
                f"clipboard: {clip_status}",
                flush=True,
            )
            print(f"[coach]   {write_desc}", flush=True)

    # ---- Main loop --------------------------------------------------------

    async def run(self) -> None:
        print("=" * 60, flush=True)
        print(f"  Civ 6 AI Coach — v{COACH_VERSION} (schema {SCHEMA_VERSION})", flush=True)
        print(f"  Output dir: {self.output_dir.resolve()}", flush=True)
        print("=" * 60, flush=True)
        # Try to connect immediately so we can print a friendly diagnostic if
        # the game isn't running yet.
        try:
            await self.conn.connect()
            print("[coach] connected to Civ 6.", flush=True)
            print(
                f"[coach] Lua states discovered by name — "
                f"GameCore_Tuner={self.conn.gamecore_index}, InGame={self.conn.ingame_index}",
                flush=True,
            )
        except ConnectionError as e:
            print(f"[coach] not connected yet: {e}", flush=True)
            print(
                "[coach] you can still press Ctrl+Shift+C once the game is loaded; "
                "the bridge will reconnect automatically.",
                flush=True,
            )

        loop = asyncio.get_running_loop()

        def _factory() -> Any:
            return self.trigger_snapshot()

        hk_thread: HotkeyThread | None = None
        if sys.platform == "win32" and start_hotkey is not None:
            hk_thread = start_hotkey(loop, _factory)
            hk_thread.wait_ready(timeout=3.0)
            if hk_thread.registered:
                print("[coach] hotkey ready: press Ctrl+Shift+C anywhere to grab a snapshot.", flush=True)
            else:
                print(
                    "[coach] could not register global hotkey. "
                    "Fallback: press Enter in this window to trigger manually.",
                    flush=True,
                )
        else:
            print(
                "[coach] non-Windows environment — global hotkey unavailable. "
                "Press Enter in this window to trigger manually.",
                flush=True,
            )

        # Manual Enter-key fallback loop.  Also handy for testing.
        stop = asyncio.Event()

        def _sigint(*_: Any) -> None:
            print("\n[coach] shutting down...", flush=True)
            stop.set()

        # Windows: signal handlers via SIGINT only; SIGBREAK not exposed by asyncio.
        try:
            loop.add_signal_handler(signal.SIGINT, _sigint)
        except (NotImplementedError, RuntimeError):
            signal.signal(signal.SIGINT, lambda *_: _sigint())

        async def _stdin_loop() -> None:
            # Windows Proactor event loop does NOT support connect_read_pipe on
            # console stdin — it fails asynchronously inside the transport
            # (WinError 6 "handle is invalid" in _loop_reading), which a
            # try/except at the call site cannot catch.  Always use the
            # blocking-thread reader on Windows.
            if sys.platform == "win32":
                await self._blocking_stdin(stop)
                return
            reader = asyncio.StreamReader(loop=loop)
            protocol = asyncio.StreamReaderProtocol(reader)
            try:
                await loop.connect_read_pipe(lambda: protocol, sys.stdin)
            except Exception:
                await self._blocking_stdin(stop)
                return
            while not stop.is_set():
                try:
                    await asyncio.wait_for(reader.readline(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                except Exception:
                    break
                if stop.is_set():
                    break
                asyncio.create_task(self.trigger_snapshot())

        try:
            await _stdin_loop()
        finally:
            if hk_thread is not None:
                hk_thread.stop()
            await self.conn.disconnect()
            print("[coach] disconnected. Goodbye.", flush=True)

    async def _blocking_stdin(self, stop: asyncio.Event) -> None:
        loop = asyncio.get_running_loop()
        while not stop.is_set():
            try:
                line = await loop.run_in_executor(None, sys.stdin.readline)
            except Exception:
                await asyncio.sleep(1.0)
                continue
            if not line:
                break
            if stop.is_set():
                break
            asyncio.create_task(self.trigger_snapshot())
