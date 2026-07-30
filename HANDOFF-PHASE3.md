# Phase 3 Handoff — Civ 6 AI Coach

For the AI session continuing this project. **Read `AGENTS.md` first** (hard
rules: read-only, base-game-only, fog-of-war, never guess Lua method names,
never let a failed query render as a real value). This file assumes you know
nothing else: it is the complete project state after Phase 2.

## What this project is

A read-only Civilization VI (base game, Steam, Windows) coaching exporter.
A persistent Python bridge connects to the running game via the FireTuner
TCP protocol. The user presses **Ctrl+Shift+C** any time; the bridge runs 8
read-only Lua queries in the game's InGame Lua state, merges them into a
versioned JSON snapshot + an AI-readable Markdown packet, archives both
per-game, and copies the Markdown to the clipboard. The user pastes it into
an AI chat (with `AI-COACH-INSTRUCTIONS.md` + `CIV6-REFERENCE.md` uploaded
once per chat) and gets coached. A separate doc,
`AI-GAME-ANALYSIS-INSTRUCTIONS.md`, is uploaded with a whole game folder
for postgame deep-dive analysis.

The user plays; the tool describes. Nothing here ever mutates game state.

## Current state: v1.6.0, schema coach-snapshot/1.4

All shipped through the full verification gauntlet (below). Regression
suite: 235 checks, all passing. Lua lint: 8/8 builders parse.

**Live-verification status:** v1.0.1 through v1.4.0 are live-verified
against the user's running game (Egypt/Cleopatra save). The v1.4.0 live
run also confirmed the G0 probes: gossip manager exists with exactly one
method (`GetRecentVisibleGossipStrings`), `plot:GetYield` is available,
war-weariness accessors are NOT available (accepted, WARNs honestly).
**v1.5.0 and v1.6.0 are regression-verified but await their first live
capture.** Specifically unconfirmed live: the gossip call *arity* (the
export tries 3 known call shapes under pcall and WARNs which worked), and
whether `CityManager.GetOperationTargets` + `CityOperationResults.
FAILURE_REASONS` exist on this build (engine production-block reasons;
falls back to labeled reconstruction + WARN if not). Ask the user for the
compat-notes block of their next capture before building on either.

## Version history (each shipped with regression cases)

- **v1.0 → v1.0.1 (schema 1.1)** — pipeline + six confidently-wrong-data
  fixes (phantom promotions, GP cost 0, over-broad civics, hash metadata,
  trade text, delta noise), WARN/compat channel, owner legend, map city
  names.
- **v1.1.0 (schema 1.2) — persistent game archives.** Every capture files
  under `output/games/game-NNN_<civ>/` with `turn-XXXX_rNN` revisions,
  content-hash dedup of identical captures, per-game `latest.md/.json`
  mirrors, `game.json` identity record. Game identity = read-only game +
  map seeds (`GAME_SYNC_RANDOM_SEED` / `RANDOM_SEED` via GetValue, -1
  sentinel + WARN when absent) with a static-config + turn-forward
  fallback. Turnless captures keep flat legacy naming, never guessed into
  a game folder.
- **v1.2.0/v1.2.1** — full tech/civic tree state (TTREE/CTREE lines:
  done/current/available/blocked, banked partial progress, prereqs via
  `GameInfo.TechnologyPrereqs`), policy card effect text rendered
  (slotted + available), blocked-tree Markdown capped to the ~8
  frontier items (fewest missing prereqs, then cheapest) with the rest
  JSON-only.
- **v1.3.0 (schema 1.3) — opponent state expansion.** `rivals` list
  (fog-gated known cities w/ pop+defense only while visible, public
  World-Rankings stats, full inter-civ war matrix, rival-rival stances,
  visibility-gated governments, founded religions, elimination
  tombstones — dead met civs no longer vanish), `units_by_civ` rollup,
  CS `envoys_by_civ`, `delta.world_events` (captures/liberations/wars/
  peace/eliminations/religions/government changes/military swings/
  suzerain flips — strictly prev-vs-curr observation, failed sections
  suppress their event class), WORLD NEWS Markdown section, per-game
  `rivals.json` + `events.json` history files. Four data-trust tiers:
  visible / revealed / diplo_vis / public.
- **v1.4.0 (schema 1.4) — Reports-screen data.** Per-city owned-resource
  plots incl. bonus resources → `resources_inventory`; localized city
  status labels via `GameInfo.Happinesses`; CS 1/3/6-envoy bonus texts
  (Loc keys, raw keys never ship) + leader trait texts + envoy-race math
  (`reconstructed:threshold`); G0 probes.
- **v1.5.0 — gossip + yield breakdown.** `gossip` export (direct
  localized entries `{about, turn, text}`), GOSSIP md section (last 10),
  per-game deduped `gossip.json` with `first_seen` stamps. Per-city
  `yield_breakdown`: worked_tiles (direct, plot:GetYield), buildings_db
  (static_db, pillaged excluded), district_adjacency (direct),
  trade_routes (direct), unattributed (reconstructed remainder — the
  base game has no per-source API for modifiers). **Also fixed: DIST
  adjacency was parsed from the pillaged column and silently empty since
  v1.0** (regression-pinned).
- **v1.6.0 — unavailable production + truncation integrity.** PRODX
  lines: panel-visible-but-blocked items with ALL exposed reasons, in
  strict source order: `engine` (localized FAILURE_REASONS via the
  read-only `CityManager.GetOperationTargets` — the query the production
  panel itself uses; probed), `reconstructed` (confirmed DB facts only,
  each reason self-labels: BuildingPrereqs / Units.StrategicResource /
  pop÷3+1 district cap), `unknown` (never invented). Other civs' uniques
  excluded via trait sets. Integrity: every query prints an `EOQ` marker
  before the sentinel and the collector FAILS (never partial-parses) a
  stream without it — this fixed a real bug where a mid-stream timeout
  silently returned fewer cities/tiles; delta damaged/healed lists
  unsliced; all intentional Markdown limits labeled "showing X of Y";
  Markdown footer comment carries JSON-mirrored per-section counts +
  `md_chars` as an external-truncation detector.

## Architecture (all coach code in `src/civ_mcp/coach/`)

```
queries.py    8 Lua builders (~2600 lines). _prelude() gives safe()/TRACE/
              WARN/DIAG helpers + esc()/sf(). Per-item pcall isolation.
              Every chunk ends: print("EOQ"); print("---END---").
parser.py     Pipe-delimited line parsers, defensive, one per query. Also
              the pure merge/compose helpers (build_rivals, units_by_civ,
              resources_inventory, cs_envoy_status, build_yield_breakdown)
              so the regression suite can reach them without FireTuner.
collector.py  Runs queries (InGame state, read-only), splits TRACE/WARN,
              enforces the EOQ completeness gate, merges fragments, builds
              section_status (ok/failed/missing). Failed sections become
              None, never empty-list lies.
delta.py      Turn-over-turn diff (CHANGES block) + _world_events().
markdown.py   Renderer. QUERY FAILED markers, WORLD NEWS, GOSSIP, tree
              rollups, rival blocks, unavailable production, integrity
              footer. Never renders a failed read as 0/none.
archive.py    Per-game folders, revisions, dedup, latest mirrors,
              game.json fingerprint. Stdlib-only (regress-testable).
history.py    rivals.json / events.json / gossip.json per game folder.
              Stdlib-only. Same-turn recapture replaces, never dupes.
bridge.py     Persistent loop: connection, Ctrl+Shift+C hotkey
              (hotkey_win.py), clipboard (clipboard_win.py), archive +
              history writes, Enter-key fallback.
```

Reused upstream (don't rewrite): `tuner_client.py` (wire protocol, length-
framed — no message-size caps), `connection.py` (name-based Lua state
discovery — never `use 5` —, auto-reconnect, sentinel-based collection;
NOTE: it returns partial lines silently on timeout, which is exactly why
the coach-side EOQ gate exists — do not remove either half). The rest of
`src/civ_mcp/` is an upstream agent project — not read-only, not
base-game-safe; only `coach/` ships. `scripts/` and `tests/` also contain
upstream files (analyze.py, orchestrator, test_*.py) — leave them alone;
the coach only owns `scripts/lint_lua.py` and `scripts/regress.py`.

Key invariants:
- Coach package has NO import dependency on `civ_mcp.lua` (SENTINEL
  redefined in `coach/__init__.py`, regress-guarded).
- `SCHEMA_VERSION = "coach-snapshot/1.4"`, `COACH_VERSION = "1.6.0"`,
  both in `coach/__init__.py`. Add-only schema changes don't bump the
  schema number; renames/removals do. Bump COACH_VERSION every ship and
  update the regress pins.
- `-1` = unknown sentinel everywhere (also `-999` for growth modifiers).
  A value the user could act on wrongly is worse than a visible gap.
- All queries run via `execute_write` (misnomer — it just targets the
  InGame Lua state; usage is read-only).
- Every parsed None-vs-empty distinction is deliberate: None = query
  failed (renders QUERY FAILED), [] = genuinely empty.

## Verification workflow (run before shipping anything)

```
python scripts/lint_lua.py    # 8/8 builders must parse (pip lupa)
python scripts/regress.py     # 235 checks — add yours, one per bug/feature
uv run python -m civ_mcp.coach --test-once --verbose   # live, game running
```

The first two run anywhere (the dev session runs them in its own sandbox
after staging the repo; pip needs `lupa`). The live check only the user
can run — hand them the exact things to look for (new sections, WARN
lines, timing) and wait for results before building on unconfirmed APIs.
Add a regression case for every bug fixed, written to fail against the
buggy version. Lua-lint before ever shipping Lua. Probe unknown APIs with
`type(obj.Method) == "function"` + WARN/DIAG method dumps — this workflow
found the gossip method name and killed the war-weariness guess.

## Data-trust discipline (load-bearing, don't dilute)

Every rival/derived field carries a source tier: `visible` (on screen at
capture), `revealed` (seen before, may be stale — `?`-marked in md),
`diplo_vis` (only at sufficient diplomatic visibility, gated in Lua, not
in the renderer), `public` (World Rankings / religion / wars / envoys),
`static_db` (base DB values), `direct` (engine records like gossip),
`reconstructed` (arithmetic/derivation over direct data — always
self-labeled with its rule or DB source). Never upgrade a lower tier into
a higher one, in code or in docs.

## The three coaching docs (repo root — the ONLY docs, plus this handoff)

- `README.md` — user-facing setup/usage/troubleshooting + the full JSON
  schema appendix with per-version changelogs. Update the appendix with
  every schema-visible change.
- `AI-COACH-INSTRUCTIONS.md` — uploaded to live-coaching chats. Documents
  every Markdown section, the tiered response format (quiet turn /
  decisions / position shift), the 📊 STATUS footer, QUERY FAILED
  handling, data-trust tiers, the integrity footer. Update it whenever
  the packet gains a section — this was forgotten once and had to be
  caught up later.
- `AI-GAME-ANALYSIS-INSTRUCTIONS.md` — uploaded with a game folder for
  postgame deep dives (chronology-first method, evidence citation rules).
- Do NOT create new docs without asking. Consolidate into these.

## User preferences (matter for how you work)

- Technically capable, hates ceremony. Move fast, state assumptions,
  don't ask what the repo can answer. Blunt > polite.
- Wants conventional-commit-style commit messages written for them at
  every ship (they commit manually).
- Ships are delivered by writing files straight back to the repo working
  tree; the user runs the live check and reports back (paste of terminal
  or compat notes). Wait for that before stacking dependent work.
- Markdown packet size is a standing concern: JSON is always the complete
  record; Markdown stays compact with labeled "showing X of Y" limits.
  Strategy variety is a hard requirement (CIV6-REFERENCE.md §12) — the
  coach must never push one meta lane.

## Known open threads (start of Phase 3)

1. **Live-verify v1.5.0/v1.6.0** — first hotkey press should show: GOSSIP
   section + `gossip fetched via call arity N` note; prod-sources lines;
   unavailable-production blocks with engine or reconstructed reasons;
   no `WARN|CITIES.prod_blocked` (if it appears, engine reasons are off
   and only reconstruction runs — report which). Also watch the cities
   query timing vs its 30s timeout — it has grown a lot.
2. **Gossip arity/shape** — if no call shape returns a table, the WARN
   says so; the fix is trying additional argument shapes.
3. **Deferred from the original Phase 2 list:** per-tile yields in the
   MAP export (plot:GetYield is confirmed available; blocked only on
   size concerns — pairs with a snapshot-size-management design), trade
   route turns remaining + deal expiration (deal APIs = the riskiest
   surface, probe-first), Great Work slots/contents, wonder ownership
   by civ.
4. **Size management** — the md packet has grown every version. If the
   user reports it past comfortable paste size: deterministic section
   trimming, keep one-paste default, measure before engineering.
5. **Phase 3 candidates the user has hinted at** (postgame tooling on top
   of the archive spine): campaign history / trend analysis, decision
   reviews, graphs from rivals.json timelines, "what changed over the
   last N turns" digests. The archive files were designed for exactly
   this — read them before inventing new storage.

## File map

```
README.md                        user-facing + schema appendix/changelog
AI-COACH-INSTRUCTIONS.md         live-coaching chat doc
AI-GAME-ANALYSIS-INSTRUCTIONS.md postgame deep-dive chat doc
CIV6-REFERENCE.md                base-game numbers + variety mandate
AGENTS.md                        rules for AI sessions (read first)
HANDOFF-PHASE3.md                this file
Start Civ6 Coach.bat             launcher
scripts/lint_lua.py              Lua syntax gate (coach-owned)
scripts/regress.py               235-check regression suite (coach-owned)
src/civ_mcp/coach/               all coach code (see architecture)
src/civ_mcp/                     upstream agent project — reuse
                                 tuner_client/connection only
docs/civ6-query*.lua             legacy v0.7 fallback, keep as-is
output/games/game-NNN_<civ>/     per-game archive: game.json, latest.*,
                                 snapshots/, rivals.json, events.json,
                                 gossip.json
```

Repo root: `C:\Users\jakeb\civ6-game-tracker`. Connect that folder in the
new Cowork session; stage files to read, write changed files straight
back to the same paths.
