# AGENTS.md — working rules for this repo

This repo is a **read-only Civilization VI coaching exporter**. A Python
bridge talks to a running Civ 6 over the FireTuner protocol, collects the
full legitimately-visible game state on a hotkey press, and writes a JSON
snapshot plus an AI-readable Markdown packet to the clipboard.

If you are an AI tool working in this repo, these rules override defaults.

## Hard constraints

1. **Read-only. No exceptions.** Never add, suggest, or call anything that
   mutates game state: no `RequestPlayerOperation`, no `UI.RequestAction`,
   no `EndTurn`, no `CityManager.RequestCommand`, no unit orders, no save
   or load. The tool describes; the human plays. If you find a mutating
   API in `src/civ_mcp/lua/` (inherited from the upstream MCP-agent
   project), do not expose or call it from `src/civ_mcp/coach/`.

2. **Base game only.** No Rise & Fall, no Gathering Storm. Never emit or
   depend on: governors, loyalty, era score, Golden/Dark Ages, era
   dedications, formal alliance levels, diplomatic favor, World Congress,
   Diplomatic Victory, climate, disasters, power, resource consumption,
   dams, canals, railroads. Feature-detect rather than assume, and record
   anything unavailable in `diagnostics.unsupported`.

3. **Respect fog of war.** Only export what the player has legitimately
   revealed or what the normal UI exposes. Barbarian units and camps are
   split into `visible` vs `revealed_only`. Resources honour `PrereqTech`.
   Never surface hidden tiles, hidden enemy units, or AI-private state.

4. **Never guess a Lua method name.** This project has been broken twice
   by guessed API names. Confirm against the shipped base-game UI Lua at
   `…/Sid Meier's Civilization VI/Base/Assets/UI/`, or against a call that
   already works elsewhere in this repo. If you cannot confirm it, probe
   for it at runtime with `type(obj.Method) == "function"` and emit a
   `DIAG` line on failure rather than shipping a guess.

5. **Never let a query lie.** A failed read must render as `QUERY FAILED`
   or `unknown` — never as `0`, `none`, `empty`, or "not selected". A
   value the user could act on wrongly is worse than a visible gap. See
   `section_status` in the collector and the `-1` unknown sentinel.

## Architecture

```
Civ 6  →  FireTuner TCP (civ_mcp/tuner_client.py)
       →  GameConnection (civ_mcp/connection.py) — discovers Lua states BY NAME
       →  8 read-only Lua queries (coach/queries.py)
       →  parsers (coach/parser.py) → collector merge (coach/collector.py)
       →  delta (coach/delta.py) + Markdown (coach/markdown.py)
       →  JSON + Markdown files, and the Windows clipboard
```

Everything the coach owns lives in `src/civ_mcp/coach/`. The surrounding
`src/civ_mcp/` tree is inherited from the upstream `civ6-mcp` agent
project — reuse `tuner_client` and `connection` from it, but do not
assume the rest is base-game-safe or read-only.

Lua state indexes are **discovered by name** (`GameCore_Tuner`, `InGame`).
Never hardcode `use 5` or any fixed index.

## Lua query conventions

- No outer `pcall` around a whole query — one bad field would discard
  every line after it. Use the `safe(field, fn)` helper from `_prelude`.
- Emit `TRACE|<SECTION>|<field>` before each risky block so a live crash
  names the exact field instead of a line number.
- Wrap every collection item (each city, unit, district, tile) in its own
  `pcall`. One bad building must not produce `CITIES (0)`.
- Terminate every chunk with the shared sentinel.

## Verification before shipping

Run both, from the repo root:

```
python scripts/lint_lua.py      # all 8 builders must parse as Lua 5.3
python scripts/regress.py       # regression suite
```

Then a live check with the game running and a save loaded:

```
uv run python -m civ_mcp.coach --test-once --verbose
```

Add a regression case for every bug you fix — each of the six bugs fixed
in v1.01 has one, written so it fails against the buggy version.

## Style

The user is technically capable and does not want setup ceremony. Explain
trade-offs plainly, state assumptions, and don't ask questions the repo
can answer. When a field can't be obtained, show what you inspected and
why it's unavailable.
