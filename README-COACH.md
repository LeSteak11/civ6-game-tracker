# Civ 6 AI Coach — README

**One launcher. One hotkey. Full game state on your clipboard.**

## What it is

A read-only Civilization VI *coach*: while you play, press
**`Ctrl+Shift+C`** anywhere on your desktop and the program collects your
current game state and copies a compact Markdown packet to your clipboard.
Paste that into ChatGPT, Claude, or Gemini and ask for coaching.  A full
JSON snapshot is also written to `output/` so you (or the AI) can diff
turn-to-turn or re-open past turns.

This replaces the old v0.7 flow (open FireTuner terminal → `use 5` →
paste `civ6-query.lua` → type `S()` → select the printed text → paste to
chat).  You never touch the terminal during normal play.

## What it is NOT

- Not an autoplayer.  It reads state; it never issues game commands, never
  ends your turn, never moves units, never sets production.
- Not an omniscient tool.  It respects fog of war and diplomatic
  visibility — no cheating for hidden tiles, hidden enemy units, or
  AI-private info.
- Not compatible with the expansions.  Base-game only: no Rise & Fall, no
  Gathering Storm.  Expansion-only fields (loyalty, governors, era score,
  alliances, diplomatic favor, World Congress) are intentionally omitted
  and listed in the JSON `diagnostics.unsupported` block.

## Setup (one-time)

1. Enable FireTuner in Civ 6.  Edit
   `Documents\My Games\Sid Meier's Civilization VI\AppOptions.txt` and set
   `EnableTuner 1`.  This persists across sessions.  Note: Steam
   achievements are disabled while the tuner is on — this is a known,
   accepted trade-off.
2. Make sure `uv` is installed and the repo is at
   `C:\Users\jakeb\civ6-mcp`.

## Everyday use

1. Launch Civ 6 and load your save.
2. Double-click **`Start Civ6 Coach.bat`** in the repo root.  A terminal
   window opens, connects to the game, and prints
   `[coach] hotkey ready: press Ctrl+Shift+C anywhere to grab a snapshot.`
3. Play.  Whenever you want coaching, hit **`Ctrl+Shift+C`**.  The window
   prints one confirmation line per snapshot (turn number, timing, tile
   counts, clipboard status).
4. Paste into an AI chat.

The launcher can stay open across turns and even across save-loads — the
bridge reconnects on its own if the game or tuner drops the socket.

If `Ctrl+Shift+C` is already claimed by another app, the coach falls back
to a manual trigger: press **Enter** in the coach terminal window.

## What's in a snapshot

The Markdown starts with a delta vs the previous snapshot (turns elapsed,
new units, new cities, tile reveals, resource changes, newly met civs,
new wars), then the full state:

- Metadata (turn, era, civ, leader, difficulty, speed, map, enabled
  victories).
- Empire totals (score, gold + net income, science/culture/faith/tourism
  per turn, military strength, techs/civics done, populations, trade
  routes used/cap, land explored).
- Current tech + civic with progress, cost, turns, boost status and
  boost-trigger description.
- **Available** techs and civics (top 10 by turns) with unlocks and boost
  descriptions — for making switching decisions.
- Owned resources (strategic, luxuries).
- Government, all slotted policy cards with effect text, and every
  currently unlocked but unslotted policy.
- Great person points/turn by class, current candidate, patronize cost.
- Religion: pantheon, founded religion, all beliefs.
- Every city: population, growth, housing, amenities, happiness,
  yields, current production (with progress and turns), defense (strength
  + garrison HP + wall HP), border-expansion timer, every district with
  coordinates + adjacency yields + pillaged flag, every building inside
  each district with pillaged flag, owned/worked tile rollup, top 10
  production options currently legal, active outgoing trade routes.
- Every unit: position, HP, moves, combat/ranged, XP, promotions held +
  available, fortify turns, build charges, upgrade availability + cost,
  IDLE flag.
- Visible barbarians and barbarian camps (respecting fog).
- Diplomacy: met majors (relationship, visibility, war/peace, score,
  military, open borders, known agendas) and city-states (envoys sent,
  suzerain, active quest, war/peace).
- **Full revealed map** — one dense line per revealed tile: coords,
  visible-vs-revealed, terrain, feature, resource, improvement, road,
  owner, district, city flag, visible units on tile, extras (river / lake
  / fresh water / appeal).  Natural wonders listed separately.
- Notifications and end-turn blockers.
- Diagnostics: per-query timing, any Lua errors, sections deliberately
  skipped because they're expansion-only.

## Files it writes

Every hotkey press produces (under `output/` — override with
`CIV6_COACH_OUTPUT` or `--output`):

    output\latest-full.json       # canonical JSON, versioned schema
    output\latest-coach.md        # what's on your clipboard
    output\turn-XXXX-full.json    # per-turn history
    output\turn-XXXX-coach.md

The JSON schema is documented in `docs/coach-snapshot-schema.md`.

## Testing without a hotkey

    uv run python -m civ_mcp.coach --test-once --verbose

Takes one snapshot then exits.  Requires the game to be running with a
save loaded.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `[coach] cannot reach Civ 6` | Civ 6 isn't running, or `EnableTuner=1` isn't set, or the firewall is blocking loopback:4318. |
| Terminal shows "hotkey ready" but Ctrl+Shift+C does nothing | Another app owns that key.  Press Enter in the coach terminal instead — same result. |
| Snapshot shows all cities/units empty | You're on the main menu.  Load a save; the bridge will reconnect on next press. |
| Markdown pasted into chat looks garbled | The Markdown uses backtick fences for the map block — some chat UIs collapse whitespace.  Use "raw" or "paste as text" mode if the tile map wraps. |
| Snapshot files stop appearing | Check the terminal window for `[coach] snapshot failed` — it lists which query broke.  Restart the launcher; the reconnect logic will pick things up. |

## Design notes for future work

- The bridge reuses `civ_mcp.tuner_client` (wire protocol) and
  `civ_mcp.connection.GameConnection` (name-based state discovery,
  auto-reconnect).  No `use 5` anywhere.
- Every Lua query is base-game-only and pcall-wrapped section by section:
  a single missing field prints one `DIAG|section|message` line rather
  than killing the whole snapshot.
- The coach package is fully separate from the existing MCP server
  (`civ_mcp.server`) — starting the coach does not start the MCP server.
- Snapshot writes are atomic per file, but not per pair — if the bridge
  is killed mid-write you can end up with a fresh `latest-coach.md` and a
  stale `latest-full.json`.  Simple; not worth Windows-atomic-rename
  gymnastics.

Read-only.  No `RequestPlayerOperation`, no `UI.RequestAction`, no
`EndTurn`, no save writes.  You make every decision and press every
button.  The coach describes; you play.
