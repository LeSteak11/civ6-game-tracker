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

SCHEMA_VERSION = "coach-snapshot/1.4"  # 1.3 + reports-screen data (additive)
COACH_VERSION = "1.7.0"

# Terminator every coach Lua chunk prints as its last line.
#
# ``GameConnection._locked_execute`` stops collecting output when it sees
# this, so the value MUST stay identical to ``civ_mcp.lua._helpers.SENTINEL``.
# It is redefined here rather than imported so the coach package has no
# import-time dependency on the upstream ``civ_mcp.lua`` package (whose
# ``__init__`` pulls in the entire agent toolchain).  ``scripts/regress.py``
# asserts the two values still match.
SENTINEL = "---END---"
