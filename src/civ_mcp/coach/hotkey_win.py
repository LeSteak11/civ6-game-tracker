"""Windows global hotkey — Ctrl+Shift+C by default.

Registers a WM_HOTKEY hook on a dedicated background thread using
``RegisterHotKey``/``GetMessageW``.  When the hotkey fires we schedule a
callback on the main asyncio loop via ``loop.call_soon_threadsafe``.

No external dependencies — pure ``ctypes``.

Fallback: if ``RegisterHotKey`` fails (another app already owns Ctrl+Shift+C,
or we're not on Windows), the coach still works — the user can press Enter
in the terminal to trigger a snapshot manually.  See ``bridge.py``.
"""

from __future__ import annotations

import asyncio
import ctypes
import logging
import sys
import threading
from ctypes import wintypes
from typing import Callable

log = logging.getLogger(__name__)


# Modifier flags for RegisterHotKey.
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000

# Virtual key for 'C'.
VK_C = 0x43

WM_HOTKEY = 0x0312
WM_QUIT = 0x0012


class HotkeyThread(threading.Thread):
    """Background thread that owns the hotkey message pump.

    ``on_press`` is invoked on THIS thread (not on the asyncio loop).  Wire it
    up via ``loop.call_soon_threadsafe`` in the caller.
    """

    def __init__(
        self,
        on_press: Callable[[], None],
        *,
        modifiers: int = MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT,
        vkey: int = VK_C,
        hotkey_id: int = 1,
        name: str = "Ctrl+Shift+C",
    ) -> None:
        super().__init__(daemon=True, name="civ6-coach-hotkey")
        self.on_press = on_press
        self.modifiers = modifiers
        self.vkey = vkey
        self.hotkey_id = hotkey_id
        self.hotkey_name = name
        self._thread_id: int | None = None
        self._registered = threading.Event()
        self._register_ok = False
        self._register_err: str | None = None

    @property
    def registered(self) -> bool:
        return self._registered.is_set() and self._register_ok

    def wait_ready(self, timeout: float = 3.0) -> bool:
        self._registered.wait(timeout)
        return self._register_ok

    def stop(self) -> None:
        if self._thread_id is not None and sys.platform == "win32":
            user32 = ctypes.WinDLL("user32", use_last_error=True)
            user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)

    def run(self) -> None:  # pragma: no cover — background thread
        if sys.platform != "win32":
            self._register_err = "not on windows"
            self._registered.set()
            return
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self._thread_id = kernel32.GetCurrentThreadId()

        user32.RegisterHotKey.argtypes = [
            wintypes.HWND,
            ctypes.c_int,
            wintypes.UINT,
            wintypes.UINT,
        ]
        user32.RegisterHotKey.restype = wintypes.BOOL
        user32.UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]
        user32.UnregisterHotKey.restype = wintypes.BOOL

        if not user32.RegisterHotKey(None, self.hotkey_id, self.modifiers, self.vkey):
            self._register_err = (
                f"RegisterHotKey failed (GetLastError={ctypes.get_last_error()}). "
                "Another application may already own this key combination."
            )
            log.warning(self._register_err)
            self._registered.set()
            return
        self._register_ok = True
        self._registered.set()
        log.info("Hotkey %s registered (id=%d)", self.hotkey_name, self.hotkey_id)

        msg = wintypes.MSG()
        try:
            while True:
                r = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                if r == 0 or r == -1:  # WM_QUIT or error
                    break
                if msg.message == WM_HOTKEY and msg.wParam == self.hotkey_id:
                    try:
                        self.on_press()
                    except Exception:  # noqa: BLE001
                        log.exception("Hotkey callback raised")
        finally:
            user32.UnregisterHotKey(None, self.hotkey_id)
            log.info("Hotkey unregistered")


def start_hotkey(loop: asyncio.AbstractEventLoop, coro_factory: Callable[[], "asyncio.coroutines"]) -> HotkeyThread:
    """Register Ctrl+Shift+C globally; on press, schedule ``coro_factory()`` on ``loop``."""

    def _on_press() -> None:
        # Called on the hotkey thread.  Bounce onto the asyncio loop.
        asyncio.run_coroutine_threadsafe(coro_factory(), loop)

    t = HotkeyThread(on_press=_on_press)
    t.start()
    return t
