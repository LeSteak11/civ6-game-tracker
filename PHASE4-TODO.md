# Phase 4 — TODO

Running task list for Phase 4 dev sessions. Add tasks at the bottom,
check them off with the ship version that closed them. Each task that's
ready to build carries a **copy/paste prompt** — paste it verbatim into
the dev chat to kick the work off.

Conventions still apply to every task here: read `AGENTS.md` first,
verification gauntlet before shipping (`python scripts/lint_lua.py`,
`python scripts/regress.py`), regress case per bug/feature, bump
`COACH_VERSION` + regress pin per ship, conventional-commit message,
user runs all live checks.

---

## [ ] 1. GAME PACK builder — one-click "whole game in one file"

**Problem:** the archive now holds 60+ turn snapshots (~2.4MB of
Markdown for game-001). That's 3x over any chat context window — the
turns can't be uploaded raw, and 95% of each snapshot repeats the
previous one anyway. The user wants one clickable file that combines
the whole game into a single upload an AI can actually digest.

**Copy/paste prompt for the dev chat:**

> Build the GAME PACK builder: a double-clickable `Make Game Pack.bat`
> in the repo root plus `scripts/make_game_pack.py` (coach-owned,
> stdlib-only like archive.py so regress can run it without FireTuner).
> It reads one game folder under `output/games/` (default: the game
> with the newest `latest.json`; optional argument to pick another) and
> writes `GAME-PACK.md` into that same game folder — ONE file, budgeted
> to fit a single AI-chat upload (target ~250k chars, hard cap 300k,
> every trim labeled "showing X of Y" per project convention).
>
> Pack contents, in order:
> 1. **Coverage header** — from game.json: game id, civ/leader,
>    difficulty/map/speed, turn span captured, number of captures,
>    capture density gaps (e.g. "T113, T126–T127 missing"), coach
>    versions seen. State plainly what the pack does and doesn't cover.
> 2. **Trend table** — one row per captured turn, mined from every
>    `snapshots/turn-*_rNN.json` (highest revision per turn): turn,
>    score, science/t, culture/t, gold stock, gold net, faith stock,
>    military, cities, total pop, techs done, civics done, trade
>    routes used. Skip a column honestly (`?`) where that snapshot's
>    section failed — never a fake 0 (the `-1`/None sentinels rule
>    applies to the pack too).
> 3. **Chronology** — events.json + gossip.json merged and turn-sorted,
>    deduped, one line per entry. This is the game's dated story.
> 4. **Rival timelines** — compressed from rivals.json: per met civ,
>    first/last seen, score+military at ~every 10th observed turn,
>    wars, government changes, cities-known progression.
> 5. **Per-turn delta digest** — the CHANGES SINCE LAST SNAPSHOT and
>    WORLD NEWS blocks extracted from each turn's .md, in order —
>    the narrative of the whole game at ~1k chars/turn.
> 6. **Current state** — the full latest.md embedded verbatim.
> 7. **Checkpoint snapshots** — full .md of every Nth captured turn
>    (default N=15, auto-raised if the budget would blow), listed in
>    the coverage header so the reader knows which turns are full-res.
>
> If the budget still overflows: drop checkpoints first, then truncate
> the delta digest oldest-first — never the trend table, chronology, or
> latest.md. Every drop must be stated in the coverage header.
>
> Also: add a short section to AI-GAME-ANALYSIS-INSTRUCTIONS.md §2
> telling the analyst chat how to read a GAME-PACK.md (it substitutes
> for the multi-file upload; same evidence rules; checkpoint turns are
> full-res, everything else is digest). Add regress cases (build a pack
> from synthetic fixture snapshots: budget respected, failed sections
> render `?` not 0, dedup of gossip/events, highest-revision-wins,
> labeled trims). Bump COACH_VERSION, update the regress pin and README
> (Files it writes + changelog). No Lua changes, no new engine API —
> this is pure archive-side tooling. Ship files back to the repo and
> give me the commit message.

**Acceptance:** double-click the .bat with the game NOT running →
GAME-PACK.md appears in the game folder, under 300k chars, uploads to a
chat alongside AI-GAME-ANALYSIS-INSTRUCTIONS.md and produces a coherent
whole-game analysis without any other file.

---

## [ ] 2. Investigate the COACH_VERSION revert (found T148-era)

`src/civ_mcp/coach/__init__.py` on disk reads `COACH_VERSION = "1.6.0"`
with an mtime AFTER the v1.7.1 ship, while captures T146–T148 stamp
`coach 1.7.1` (the running bridge imported the pre-revert code). Run
`git diff`/`git status` on `src/civ_mcp/coach/` — if only `__init__.py`
regressed, restore `COACH_VERSION = "1.7.1"`; if more files reverted,
re-apply the v1.7.1 ship before building anything on top. The regress
suite pins the version and will catch it: `python scripts/regress.py`.

---

## Queued from Phase 3 (unchanged, see HANDOFFPHASE3/Phase 4 handoff)

- [ ] Part B probe pack (DIAG-only query: citizens worked-tiles, trade
      manager, adjacency yield, housing/amenity getters, map pins,
      diplo accessors, religion pressure, belief-taken, victory stats,
      participating-player count)
- [ ] Part C features on confirmed probes, priority: citizens → trade
      routes → housing engine → amenities → religion → victory →
      district placement (last; md-size risk)
- [ ] Md size management if the paste gets uncomfortable
- [ ] Postgame trend graphs / decision reviews on the archive spine
