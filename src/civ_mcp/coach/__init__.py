"""Civ VI AI Coach — one-hotkey full-state copier.

Reuses ``civ_mcp.tuner_client`` and ``civ_mcp.connection.GameConnection`` for
the FireTuner wire protocol and name-based Lua-state discovery.

Public entry point:  ``python -m civ_mcp.coach``  (launched by
``Start Civ6 Coach.bat``).

Read-only.  Never sends commands that mutate game state.  Ruleset-aware:
every snapshot stamps the active ruleset (expansions + mods + live DB
tables), derives its data tables from ``GameInfo`` at capture time, and
reports per-mechanic capability under ``diagnostics.unsupported`` —
derived from the capture's own probe, never asserted.
"""

from __future__ import annotations

SCHEMA_VERSION = "coach-snapshot/1.6"  # 1.5 + R&F sections: era, governors, emergencies, city loyalty, major alliances (additive)
COACH_VERSION = "1.10.0"  # Phase D1: Rise & Fall extraction (era score/ages, governors, loyalty, alliances, emergencies)

# Terminator every coach Lua chunk prints as its last line.
#
# ``GameConnection._locked_execute`` stops collecting output when it sees
# this, so the value MUST stay identical to ``civ_mcp.lua._helpers.SENTINEL``.
# It is redefined here rather than imported so the coach package has no
# import-time dependency on the upstream ``civ_mcp.lua`` package (whose
# ``__init__`` pulls in the entire agent toolchain).  ``scripts/regress.py``
# asserts the two values still match.
SENTINEL = "---END---"
