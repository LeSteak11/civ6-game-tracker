"""Windows clipboard writer — no external dependencies.

Uses ``ctypes`` against ``user32``/``kernel32`` directly so the coach package
runs on a clean base-game Windows install without ``pywin32``, ``pyperclip``,
or any pip package.

The API is intentionally tiny: ``copy_text(s)``.  On non-Windows systems the
function raises ``NotImplementedError`` with a helpful message — the coach is
Windows-only anyway.
"""

from __future__ import annotations

import ctypes
import logging
import platform
import sys
import time
from ctypes import wintypes

log = logging.getLogger(__name__)


class ClipboardError(RuntimeError):
    pass


if sys.platform == "win32":  # pragma: no cover — Windows-only

    _CF_UNICODETEXT = 13
    _GMEM_MOVEABLE = 0x0002

    _user32 = ctypes.WinDLL("user32", use_last_error=True)
    _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    _user32.OpenClipboard.argtypes = [wintypes.HWND]
    _user32.OpenClipboard.restype = wintypes.BOOL
    _user32.EmptyClipboard.argtypes = []
    _user32.EmptyClipboard.restype = wintypes.BOOL
    _user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
    _user32.SetClipboardData.restype = wintypes.HANDLE
    _user32.CloseClipboard.argtypes = []
    _user32.CloseClipboard.restype = wintypes.BOOL

    _kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
    _kernel32.GlobalAlloc.restype = wintypes.HANDLE
    _kernel32.GlobalLock.argtypes = [wintypes.HANDLE]
    _kernel32.GlobalLock.restype = wintypes.LPVOID
    _kernel32.GlobalUnlock.argtypes = [wintypes.HANDLE]
    _kernel32.GlobalUnlock.restype = wintypes.BOOL
    _kernel32.GlobalFree.argtypes = [wintypes.HANDLE]
    _kernel32.GlobalFree.restype = wintypes.HANDLE

    def _open_clipboard(attempts: int = 20, delay: float = 0.05) -> None:
        """Retry ``OpenClipboard`` — another process may briefly hold it."""
        for _ in range(attempts):
            if _user32.OpenClipboard(None):
                return
            time.sleep(delay)
        raise ClipboardError(
            f"OpenClipboard failed after {attempts} attempts "
            f"(GetLastError={ctypes.get_last_error()})"
        )

    def copy_text(text: str) -> int:
        """Copy a Unicode string to the Windows clipboard.  Returns bytes written."""
        # Two bytes per UTF-16 code unit + terminating NUL.
        buf = text.encode("utf-16-le") + b"\x00\x00"
        h = _kernel32.GlobalAlloc(_GMEM_MOVEABLE, len(buf))
        if not h:
            raise ClipboardError(
                f"GlobalAlloc failed (GetLastError={ctypes.get_last_error()})"
            )
        try:
            p = _kernel32.GlobalLock(h)
            if not p:
                raise ClipboardError(
                    f"GlobalLock failed (GetLastError={ctypes.get_last_error()})"
                )
            ctypes.memmove(p, buf, len(buf))
            _kernel32.GlobalUnlock(h)
            _open_clipboard()
            try:
                _user32.EmptyClipboard()
                if not _user32.SetClipboardData(_CF_UNICODETEXT, h):
                    raise ClipboardError(
                        f"SetClipboardData failed (GetLastError={ctypes.get_last_error()})"
                    )
                # Ownership transferred to the clipboard — do not GlobalFree.
                h = None
            finally:
                _user32.CloseClipboard()
        finally:
            if h:
                _kernel32.GlobalFree(h)
        return len(buf)

else:

    def copy_text(text: str) -> int:  # pragma: no cover
        raise NotImplementedError(
            f"Coach clipboard is Windows-only (running on {platform.system()}). "
            "Snapshot files are still written to output/; copy manually if needed."
        )
