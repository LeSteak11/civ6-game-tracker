"""Civ VI AI Coach — one-hotkey full-state copier.

Reuses ``civ_mcp.tuner_client`` and ``civ_mcp.connection.GameConnection`` for
the FireTuner wire protocol and name-based Lua-state discovery.

Public entry point:  ``python -m civ_mcp.coach``  (launched by
``Start Civ6 Coach.bat``).

Read-only.  Never sends commands that mutate game state.  Base-game only
(no Rise & Fall, no Gathering Storm) — expansion-only API surfaces are
feature-detected and reported under ``diagnostics.unsupported`` instead of
being silently omitted.
"""

from __future__ import annotations

SCHEMA_VERSION = "coach-snapshot/1"
COACH_VERSION = "0.1.0"
