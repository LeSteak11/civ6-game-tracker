# Phase 2 Handoff — Civ 6 AI Coach

For the AI session continuing this project. Read `AGENTS.md` first (hard
rules: read-only, base-game-only, fog-of-war, never guess Lua method names,
never let a failed query render as a real value). This file is the current
state + the Phase 2 mission.

## What this project is

A read-only Civ VI (base game, Steam, Windows) coaching exporter. A
persistent Python bridge connects to the running game via FireTuner. The user
presses **Ctrl+Shift+C** any time; the bridge runs 8 read-only Lua queries,
merges them into a versioned JSON snapshot + AI-readable Markdown, writes
both to `output/`, and copies the Markdown to the clipboard. The user pastes
it into an AI chat (with `AI-COACH-INSTRUCTIONS.md` + `CIV6-REFERENCE.md`
uploaded once per chat) and gets coached.

## Current state: v1.0.1 — everything works live

Verified against the user's live game (Egypt/Cleopatra, turn 87, 4 cities):
all 8 query groups succeed, snapshot takes ~3s, ~500 tiles, clipboard OK,
global hotkey OK, Enter-key fallback OK (Windows Proactor stdin bug fixed).

History: v1.0 shipped the pipeline; v1.01 fixed six confidently-wrong data
bugs (phantom promotions, GP cost 0, over-broad civics, hash metadata,
player0/FOO trade text, turns-elapsed-0 noise); v1.0.1 cleanup added
GameInfo.Maps map-size resolution, a WARN/compat-notes channel distinct from
failures, owner-ID legend + city names on map tiles, semver version.

## Architecture (all coach code in `src/civ_mcp/coach/`)

```
queries.py    8 Lua builders. _prelude() gives safe()/TRACE/WARN/DIAG helpers.
              Per-item pcall isolation. Sentinel-terminated.
parser.py     Pipe-delimited line parsers, defensive, one per query.
collector.py  Runs queries (InGame state, read-only), splits TRACE/WARN,
              merges fragments, builds section_status (ok/failed/missing).
              Failed sections become None, never empty-list lies.
delta.py      Turn-over-turn diff for the CHANGES block.
markdown.py   Renderer. QUERY FAILED markers, owner legend, map block,
              compat notes. Never renders a failed read as 0/none.
bridge.py     Persistent loop: connection, hotkey (hotkey_win.py), clipboard
              (clipboard_win.py), file writing w/ turn-XXXX naming.
```

Reused upstream (don't rewrite): `tuner_client.py` (wire protocol),
`connection.py` (name-based Lua state discovery, auto-reconnect). The rest of
`src/civ_mcp/` is the upstream agent project — not read-only, not
base-game-safe; only `coach/` ships.

Key invariants: coach package has NO import dependency on `civ_mcp.lua`
(SENTINEL redefined in `coach/__init__.py`, regress-guarded). Schema is
`coach-snapshot/1.1`, documented in README.md appendix. `-1` = unknown
sentinel. All queries route to the InGame Lua state via `execute_write`
(misnomer; it's read-only use).

## Verification workflow (run before shipping anything)

```
python scripts/lint_lua.py    # 8/8 builders must parse (needs pip lupa)
python scripts/regress.py     # 50+ checks, one per past bug — add yours
uv run python -m civ_mcp.coach --test-once --verbose   # live, game running
```

Add a regression case for every bug fixed, written to fail against the buggy
version. Use lupa Lua-lint before ever shipping Lua. TRACE lines mean a live
failure names the exact field, not a line number.

## Phase 2 mission: output improvements + detail additions

Phase 1 = correctness (done). Phase 2 = richer, more useful output. The user
will direct priorities; known candidate items from past discussion:

- Per-tile yields in the map export (biggest known gap for district siting)
- City-state suzerain bonus text + quest details
- Great Work slots and contents (wonders/buildings)
- Other civs' visible cities (owner legend exists; city list per rival doesn't)
- Trade route turns remaining; deal expiration timing
- Machine-readable "pending decisions" tags in the delta block (supports the
  tiered coaching format in AI-COACH-INSTRUCTIONS.md)
- Snapshot size management if Markdown grows past comfortable paste size
  (deterministic sections; keep one-paste default)

Constraints unchanged: read-only, base game only, fog-of-war respected,
feature-detect + WARN/DIAG rather than assume, schema bump if field shapes
change (1.1 → 1.2 additive).

## User preferences (matter for how you work)

- Technically capable, hates ceremony. Move fast, state assumptions, don't
  ask what the repo can answer.
- Wants commit messages written for them (conventional-commit style titles).
- Wants docs consolidated — README.md + AI-COACH-INSTRUCTIONS.md +
  CIV6-REFERENCE.md only. Don't add new docs without asking.
- Coaching output should be flexible: tiered depth + the 📊 STATUS footer
  (see AI-COACH-INSTRUCTIONS.md §4). Strategy variety is a hard requirement
  (CIV6-REFERENCE.md §12) — never coach one meta lane.
```

## File map

```
README.md                  user-facing: setup/usage/troubleshooting + schema appendix
AI-COACH-INSTRUCTIONS.md   uploaded to coaching chats (tiers, STATUS footer)
CIV6-REFERENCE.md          uploaded to coaching chats (mechanics, variety mandate)
AGENTS.md                  rules for AI sessions in this repo (read first)
HANDOFF-PHASE2.md          this file
Start Civ6 Coach.bat       launcher
scripts/lint_lua.py        Lua syntax gate
scripts/regress.py         regression suite
src/civ_mcp/coach/         all coach code
docs/civ6-query*.lua       legacy S() fallback, keep as-is
output/                    snapshots (gitignore-worthy, user's call)
```
