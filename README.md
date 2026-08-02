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
4. Paste into an AI chat.  (Set the chat up once by uploading
   `AI-COACH-INSTRUCTIONS.md` + `CIV6-REFERENCE.md` +
   `AI-GAME-HANDOFF-INSTRUCTIONS.md`.  When a chat gets long, say
   "handoff" — the AI writes a `=== GAME HANDOFF ===` report you paste
   into a fresh chat to continue the same game seamlessly.  For
   postgame deep dives, upload the game folder with
   `AI-GAME-ANALYSIS-INSTRUCTIONS.md` instead.)

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
- **Full tech + civic tree state** — every entry tagged
  done/current/available/blocked, with banked partial progress, cost,
  turns, era and prerequisites; the Markdown shows a compact rollup
  (completed list, banked progress, and only the ~8 blocked items nearest
  the frontier with their missing prereqs), the JSON has every item.
- Policy cards render with their full effect text, slotted and unslotted.
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

Every capture is filed into a **persistent per-game archive** (under
`output/` — override with `CIV6_COACH_OUTPUT` or `--output`):

    output\latest-full.json                          # newest capture, any game (delta seed)
    output\latest-coach.md                           # what's on your clipboard
    output\games\game-001_egypt\
        game.json                                    # leader/civ/difficulty/map/speed,
                                                     #   dates, last turn, schema, fingerprint
        latest.md                                    # newest capture of THIS game
        latest.json
        snapshots\turn-0087_r01.md / .json           # first capture on turn 87
        snapshots\turn-0087_r02.md / .json           # second capture, same turn
        snapshots\turn-0088_r01.md / .json
        GAME-PACK.md                                 # written by Make Game Pack.bat,
        GAME-PACK-LEAN.md                            #   never by a capture

Archive behaviour:

- A new match creates the next `game-NNN_<civ>` folder; relaunching the
  same match (even from an older save) reopens its existing folder.  Game
  identity comes from the read-only game + map seeds exported in
  `meta.game_seed` / `meta.map_seed`; if the seeds are unavailable the
  bridge falls back to matching the full static setup (civ, leader,
  difficulty, map script/size, speed, player count, max turns) plus a
  turn-must-not-go-backwards guard.
- Recapturing the same turn adds a revision (`_r02`, `_r03`, …); a capture
  whose content is byte-for-byte identical to the previous one (ignoring
  timestamps/diagnostics) writes **no** new file.
- `latest.md` / `latest.json` inside the game folder always mirror the
  newest capture, so there's one stable path to paste from.
- A capture with no trusted turn number (meta query failed / main menu)
  is never guessed into a game folder — it keeps the flat legacy naming
  `snapshot-partial-<epoch>-*` / `snapshot-noturn-<epoch>-*` directly
  under `output/`.

The JSON schema is documented in the appendix at the bottom of this file.

## Making a game pack (whole game -> one uploadable file)

Double-click **`Make Game Pack.bat`** with the game closed.  It lists every
archived game with its civ, turn span and capture count, you type a number,
and it writes `GAME-PACK.md` into that game's folder — one file containing
the entire game, sized for a single AI-chat upload.

    Make Game Pack.bat                         # numbered menu
    python scripts\make_game_pack.py --newest  # skip the menu
    python scripts\make_game_pack.py --game game-001_egypt

Pack contents, in order:

1. **Coverage header** — identity, real turn span, every gap, how far back
   gossip back-fills, and a loud warning if the archive spans coach
   versions (field derivations changed between them, so cross-version
   comparisons can mislead).
2. **Your timeline** — one row per captured turn, mined from the snapshot
   JSONs, highest revision per turn.  This is the only place the player's
   own arc exists: `rivals.json` tracks opponents, nothing tracks you.
3. **Rival timelines** — every met major plus city-state suzerain history.
4. **Master chronology** — `gossip.json` + `events.json` merged, turn-sorted
   and deduped.
5. **Turn-by-turn narrative** — the CHANGES / WORLD NEWS blocks from every
   turn's `.md`.
6. **Final state** — `latest.md` verbatim.

For reference, `game-001_egypt` (208 captures, T87-T396) produces a ~327k
character pack, about 81k tokens.  `--lean` additionally writes
`GAME-PACK-LEAN.md` (~96k chars) with the revealed-map tile dump removed —
same timelines, same chronology, for smaller context windows.

The builder is read-only, stdlib-only and never needs the game running.  A
character budget (`--budget`, default 600,000) acts purely as a safety net
for archives far larger than any seen so far; when it fires it drops the map
dump first, then the narrative oldest-first, and **never** the timelines or
chronology.  Every drop is named in the coverage header.

Upload the pack alongside `AI-GAME-ANALYSIS-INSTRUCTIONS.md`.

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

---

# Appendix — snapshot JSON schema (`coach-snapshot/1.4`)

Every hotkey press writes a JSON file whose top-level `schema` field is
`coach-snapshot/1.4`.  Bump `SCHEMA_VERSION` in
`src/civ_mcp/coach/__init__.py` whenever a field is renamed or removed;
add-only changes stay backwards-compatible.

## Top-level shape

```jsonc
{
  "schema": "coach-snapshot/1.4",
  "coach_version": "1.7.1",
  "generated_at_epoch": 1753728000.123,

  "meta": {
    "turn": 87, "year": "725 BC", "era": "Classical Era",
    "civ_type": "CIVILIZATION_EGYPT", "civ_name": "Egypt",
    "leader_type": "LEADER_CLEOPATRA", "leader_name": "Cleopatra",
    "difficulty": "Chieftain", "speed": "Standard",
    "map_size": "Standard", "map_type": "Continents",
    "max_players": 10, "max_turns": 500,
    "game_seed": 1520978701, "map_seed": 316702041   // -1 = unknown (schema 1.2)
  },
  "victories_enabled": ["VICTORY_TECHNOLOGY", "..."],
  "empire": {
    "score": 79, "gold": 330, "gold_yield": 12.4, "gold_maint": 2.0, "gold_net": 10.4,
    "science": 17.1, "culture": 11.3, "faith": 184, "faith_yield": 7.3, "tourism": 8.0,
    "military": 119, "techs_done": 13, "civics_done": 8,
    "num_cities": 4, "num_units": 6, "total_pop": 14,
    "trade_used": 1, "trade_cap": 1,
    "explored_land": 422, "total_land": 1153
  },
  "current_research": {"type":"TECH_CONSTRUCTION","name":"Construction","progress":92,"cost":200,"turns":7,"boosted":false,"boost_desc":"Build a Water Mill."},
  "current_civic":    {"type":"CIVIC_MILITARY_TRADITION", "...": "same shape"},
  "resources": [{"class":"LUXURY","type":"RESOURCE_IVORY","name":"Ivory","amount":1,"accessible":true}],
  "government": {"type":"GOVERNMENT_CLASSICAL_REPUBLIC","name":"Classical Republic","slots_open":0,"free_change_available":true},
  "policy_slots":    [{"index":0,"slot_type":"SLOT_ECONOMIC","slot_name":"ECONOMIC","policy_type":"POLICY_URBAN_PLANNING","policy_name":"Urban Planning","effect":"..."}],
  "policy_available":[{"type":"POLICY_...","slot":"MILITARY","name":"Discipline","effect":"..."}],
  "great_people": [{"class_type":"GREAT_PERSON_CLASS_GENERAL","class":"GENERAL","points":49,"per_turn":1.1,"next_cost":-1,"candidate":"","patronize_cost":-1}],

  "techs_available":  [{"type":"...","name":"...","progress":0,"cost":120,"turns":8,"boosted":false,"boost_desc":"...","unlocks":"..."}],
  "civics_available": [ "... same shape ..." ],

  "cities": [{
    "id":123,"name":"Râ-Kedet","is_capital":true,"x":66,"y":32,
    "population":3,"food_surplus":1.0,"turns_to_growth":24,"turns_to_starvation":-1,
    "housing":10,"amenities":3,"amenities_needed":1,"happiness":2,
    "yields":{"food":7.0,"production":14.7,"gold":10.5,"science":8.5,"culture":5.1,"faith":6.3},
    "production":{"type":"BUILDING_STONEHENGE","name":"Stonehenge","progress":420,"cost":425,"turns":1},
    "defense":{"strength":34,"garrison_hp":200,"garrison_max":200,"wall_hp":0,"wall_max":0},
    "border_expansion_turns":5,
    "majority_religion":"NONE",
    "districts":[{"type":"DISTRICT_ENCAMPMENT","name":"Encampment","x":65,"y":33,"pillaged":false,"adjacency":{"PRODUCTION":1}}],
    "buildings":[{"district":"DISTRICT_CITY_CENTER","type":"BUILDING_PALACE","name":"Palace","is_wonder":false,"pillaged":false}],
    "tiles_rollup":{"owned":24,"worked":8,"terrain":{"grass":10},"features":{"forest":3},"improvements":{"farm":4}},
    "production_options":[{"kind":"UNIT","type":"UNIT_WARRIOR","name":"Warrior","progress":0,"cost":40,"turns":3}],
    "trade_routes":[{"dest_player":0,"dest_city":"Luxis","yields":{"Food":1,"Production":1},"dest_civ":"domestic"}]
  }],

  "units": [{
    "id":42,"type":"UNIT_WARRIOR","name":"Warrior","class":"FORMATION_CLASS_LAND_COMBAT",
    "x":66,"y":30,"hp":84,"hp_max":100,"moves":2,"moves_max":2,
    "combat":20,"ranged":0,"bombard":0,"range":0,
    "xp":7,"xp_needed":15,"promotions_held":0,"promotions_available":0,
    "idle":true,"fortify_turns":2,"charges":0,
    "can_upgrade":false,"upgrade_to":"","upgrade_cost":0
  }],
  "barbarians_visible": [], "camps_visible": [], "camps_revealed_only": [],

  "map_meta": {"total_plots":4720,"grid":"..."},
  "map_totals": {"revealed":422,"visible":96,"natural_wonders":2},
  "map_owners": {"0":"me (Egypt)","2":"Sumerian","40":"Kabul (city-state)","63":"Barbarians"},
  "tiles": [{"x":66,"y":32,"visible":true,"terrain":"g","feature":"","resource":"","improvement":"","road":"","owner":"0","district":"CITY_CENTER","is_city":true,"units":"0:WARRIOR:100","extra":"R","city_name":"Râ-Kedet"}],
  "natural_wonders": [{"name":"...","x":50,"y":40,"type":"FEATURE_..."}],

  "envoys": {"in_hand":0,"points":8,"threshold":100,"per_turn":3.0,"envoys_per_threshold":1},
  "majors_met":      [{"player_id":2,"civ_type":"CIVILIZATION_SUMERIA","known_agendas":[]}],
  "city_states_met": [{"player_id":40,"envoys_sent":1,"suzerain":"none","active_quests":[]}],

  "religion": {
    "pantheon":{"type":"BELIEF_...","name":"Religious Settlements","description":"..."},
    "religion":null, "beliefs":[], "can_found_pantheon":false,
    "city_religion":{"123":"NONE"}
  },

  "notifications":     [{"type":"NOTIFICATION_...","blocker_type":"","message":"..."}],
  "end_turn_blockers": [{"blocker_type":"ENDTURN_BLOCKING_UNITS","message":"Command Units"}],
  "turn_blockers_summary": ["1 idle unit(s)", "..."],

  "section_status": {"header":"ok","empire":"ok","cities":"ok","...":"ok|failed|missing"},

  "diagnostics": {
    "per_query_seconds": {"meta":0.36,"cities":0.36},
    "total_seconds": 2.77,
    "failures": [{"section":"meta.META","message":"..."}],
    "compat_notes": [{"section":"CHOICES.probe","message":"using cul:CanProgress() for civic availability"}],
    "traces": {"meta":["TRACE|META|great_people"]},
    "unsupported": ["governors (Rise & Fall)", "..."]
  }
}
```

## Encoding rules

- All numeric fields are numbers, not strings.
- `-1` is the **unknown** sentinel for values we could not read
  (`great_people[].next_cost`, `patronize_cost`).  It must never be
  rendered as `0`, which would read as "free".
- A section whose `section_status` is `"failed"` is serialized as `null`,
  never as an empty list/dict — so consumers can tell "query broke" apart
  from "genuinely empty".
- Coordinates are the game's own plot (X, Y).
- Map `terrain`/`feature` codes use the compact legend printed in the
  Markdown map header; treat them as opaque strings and derive meaning
  from `queries.py:build_map_query`.
- `promotions_available` is `0` or `1` — a unit can have at most one
  pending promotion. Civilians are always `0`.

## Changes in 1.5 (v1.8.0 — GAME PACK builder)

Archive-side tooling only; no Lua changes, no new engine API, no change to
what a capture writes.

- **`Make Game Pack.bat` + `scripts/make_game_pack.py`** compile one game
  folder into a single `GAME-PACK.md` an AI chat can read without any other
  upload.  See "Making a game pack" above.
- The pack mines a **per-turn player timeline** out of the snapshot archive.
  Until now no file carried the local player's own arc over time —
  `rivals.json` recorded every opponent per turn while the player existed
  only in whichever single snapshot you happened to open.
- The coverage header reports **capture gaps, the uncaptured pre-archive
  turns, and coach-version drift** across the snapshots it read, so an
  analyst is told what the pack cannot support before it is asked to
  conclude anything.
- Honesty rules carry over: an unreadable section renders `?`, never `0`;
  every budget trim is labelled "showing X of Y"; the timelines and
  chronology are never trimmed.

## Changes in 1.4 (v1.4.0–v1.7.1 — Reports-screen data + Part A derivations)

All additive.

v1.7.1 (Markdown rendering only — JSON unchanged):

- Unit truncation removed: `can build now` renders the COMPLETE unit
  list, and blocked trainable units render in full with reasons
  (`unavailable units (all N trainables)`).  Guarantee: a trainable
  unit absent from both lists does not exist for this civ (other civs'
  uniques stay trait-excluded by design and never appear).
- Great People and faith-purchased religious units in the blocked list
  roll up into one explanatory `not city-trainable by design` line
  instead of ~14 "reason not exposed" noise lines per city; full
  detail remains in the JSON.
- The non-unit unavailable block is relabeled
  `unavailable buildings/districts/wonders` (still capped at 6 with an
  explicit shown-of-total label).

v1.7.0 additions (Part A — derivations over already-collected data; NO
new engine API surface, every field self-labels its trust tier and is
absent — never guessed — when its inputs were unreadable):

- `cities[].district_capacity` — `{built, cap, slots_open,
  next_slot_at_pop}` from the pop/3+1 rule + the static base-game
  RequiresPopulation district set (`reconstructed:pop/3+1`).  Markdown:
  `districts: 2/2 built — FULL, next slot at pop 6`.
- `cities[].housing_breakdown` — per-source housing reconstruction
  (base + fresh water/coastal, buildings, Aqueduct/Neighborhood, +0.5
  improvements) from static DB values, cross-checked against the
  directly-read total; any gap renders as an explicit `unattributed`
  bucket (`reconstructed:static_db`).  None without map tiles.
- `cities[].amenity_status` — surplus, tier, and amenities-to-next-tier
  from the static happiness tier table (`reconstructed:static_db`).
  The live happiness label stays the authority for the current tier.
- `luxury_duplicates` — luxuries with >1 copies and their spare
  (tradable) counts.
- `settler_advisor` — present only when a Settler exists: top-5 settle
  candidates ranked from the REVEALED map (fresh water/coastal, ring-1
  base-terrain yields, resources within 2 tiles, min-distance-3
  legality vs known cities, distance/direction from the settler,
  own-territory overlap).  Entirely `reconstructed`; its `note` states
  the fog/approximation caveats and the direction convention
  (+y = north).
- `civ_accounting` — fog-safe met/eliminated arithmetic plus hard
  unmet-civ evidence (world religions founded by unmet player ids).
  `map_max_majors` is labeled a map capacity, never a start count.
- Markdown: city production options are now grouped by category
  (districts / wonders / buildings / projects in full, units capped at
  8 by turns with an explicit shown-of-total label) with cost⚙/turns
  and banked progress; the amenity line carries surplus + next-tier
  math inline.

v1.6.0 additions:

- `cities[].production_unavailable` — panel-visible-but-blocked items
  (prereq tech/civic researched, own civ's items only, not obsolete, not
  already built) with cost and ALL exposed blocking reasons.  Reason
  sourcing in strict preference order: `engine` (localized
  FAILURE_REASONS from `CityManager.GetOperationTargets` — the exact
  query the production panel uses for its red tooltips; a read-only
  inspection, probed with WARN fallback), `reconstructed` (confirmed DB
  facts only — building prereq chains, `Units.StrategicResource`,
  the district pop/3+1 capacity rule — each reason labels its source),
  `unknown` ("blocked, reason not exposed" — absence from the legal list
  is never turned into a specific claim).  Markdown shows up to 6 per
  city, districts/wonders first, with an explicit shown-of-total label.
- Truncation integrity: every query now prints an `EOQ` end-marker
  before the sentinel; the collector marks a stream that lacks it as
  FAILED instead of parsing partial output (previously a mid-stream
  timeout could silently yield e.g. fewer cities).  Delta damaged/healed
  lists are no longer sliced to 10 in the JSON.  The Markdown footer
  comment now carries per-section item counts mirrored from the JSON,
  plus `md_chars`, so external truncation of the document is detectable
  (footer missing = document cut).  All intentional Markdown limits are
  labeled "showing X of Y".

v1.5.0 additions (probe-confirmed):

- `gossip` — the player-visible gossip record, fetched via the
  live-confirmed `GetRecentVisibleGossipStrings` (call arity discovered
  under pcall and reported as a compat note).  Entries: `{about, turn
  (-1 unknown), text, source: "direct"}` — localized, engine-filtered
  strings, exactly what the Gossip report shows.  Markdown gets a
  `## GOSSIP (recent)` section (last 10); the full deduped history
  persists per game in `gossip.json` with `first_seen` stamps.
- `cities[].yield_sources` + `cities[].yield_breakdown` — per-source
  decomposition per yield: `worked_tiles` (direct, plot:GetYield sums),
  `buildings_db` (static_db base values, pillaged excluded),
  `district_adjacency` (direct), `trade_routes` (direct), and
  `unattributed` (reconstructed: city total minus the parts — population
  /amenity/policy modifiers land here; the base game exposes no
  per-source API for them).  Markdown shows one compact production-source
  line per city; `None`, never fabricated, when plot yields are absent.
- Fix: district `adjacency` was parsed from the wrong column and always
  came back empty; corrected (regression-pinned), so yield math and the
  district lines now carry real adjacency numbers.
- War weariness stays a WARN on this build (both known accessors absent)
  — accepted limitation.

- `cities[].resources` — one entry per owned resource plot (type, class
  incl. BONUS, localized name, improved = improvement observed on the
  tile, worked), PrereqTech-gated like the map.  `resources_inventory` —
  the per-resource aggregation across cities (count, improved/unimproved,
  worked, source cities), tagged `direct`; `None` when cities failed.
- `cities[].status_labels` — localized happiness label + DB growth
  modifier from the `GameInfo.Happinesses` row (direct), plus probed
  live growth modifier and war weariness (`-999`/`-1` unknown sentinels,
  WARN when the accessor is absent).  `None` when the status line never
  arrived.
- `city_states_met[].bonuses` — 1/3/6-envoy bonus texts (Loc keys,
  skipped with WARN when unresolved — a raw LOC_ key never ships) and
  leader trait texts (the suzerain bonus is among them).
  `city_states_met[].envoy_status` — thresholds met, leading civ +
  count, envoys needed to take the lead, tie flag; arithmetic over
  exported counts, tagged `reconstructed:threshold`.
- G0 probes (compat notes in `diagnostics`): gossip manager discovery +
  method dump (`DIPLO.gossip_probe`), `plot:GetYield` availability
  (`MAP.yield_probe`), growth/war-weariness accessors (`CITIES.status`).
  Gossip export and yield breakdowns ship after these confirm real API
  names on a live run.

## Changes in 1.3 (v1.3.0 — opponent state expansion)

All additive.  Rival data carries a source tier: `visible` (on screen
now), `revealed` (seen before — may be stale), `diplo_vis` (present only
at sufficient diplomatic visibility), `public` (World Rankings / religion
screen / war state / envoy counts — known to every player).

- `rivals` — one merged object per met major: everything from
  `majors_met` plus `alive`, `known_cities` (fog-gated; population and
  defense/walls only while currently visible, `original_owner` probed,
  `-1` unknown), `public_stats` {techs, civics, tourism}, `wars_with`
  (public war matrix incl. wars not involving me), `relations`
  (non-neutral rival-rival stances), `government` (visibility-gated, with
  `read_at_visibility`), `religion_founded`.  Eliminated met majors stay
  in the list with `alive: false`.
- `rival_cities`, `world_religions`, `units_by_civ` (per-owner rollup of
  currently visible units), `eliminated` — top-level additions.
- `city_states_met[].envoys_by_civ` — every civ's envoy count (public).
- `delta.world_events` + `## WORLD NEWS` Markdown section — observed
  events: war_declared / peace / city_captured / city_liberated /
  city_lost_by_me / city_captured_by_me / eliminated / religion_founded /
  government_changed / military_swing / suzerain_changed.  Derived
  strictly from prev-vs-curr comparison; failed sections suppress their
  event class instead of fabricating events.
- Per-game history files next to `game.json`: `rivals.json` (per-turn
  observation timelines per major and city-state) and `events.json`
  (append-only world events with turn stamps) — the postgame-analysis
  spine.

## Changes in 1.2 (v1.1.0 — persistent game archives)

- `meta.game_seed` / `meta.map_seed` added (additive) — read-only game
  identity from `GameConfiguration.GetValue("GAME_SYNC_RANDOM_SEED")` and
  `MapConfiguration.GetValue("RANDOM_SEED")`; `-1` = unknown sentinel with
  a WARN compat note, never a guessed value.
- Snapshots are archived per game under `output/games/game-NNN_<civ>/`
  with turn revisions (`turn-0087_r02`), content-hash dedup of identical
  captures, per-game `latest.*` mirrors, and a `game.json` identity
  record.  See "Files it writes".
- `tech_tree` / `civic_tree` added (additive, v1.2.0) — one entry per
  tech/civic: `{type, name, era, status, progress, cost, turns, partial,
  prereqs}`.  `status` is `done|current|available|blocked`; `partial` is
  true when progress is banked on a not-yet-completed item; `turns` is
  `-1` unless current/available; `prereqs` are short type names
  (`TECH_`/`CIVIC_` stripped).  Tech prereqs come from
  `GameInfo.TechnologyPrereqs`; a missing table emits a WARN, never an
  empty lie.
- Policy card effect text now renders in the Markdown for slotted and
  available cards (the JSON always carried it).

## Changes in 1.0.1 (cleanup pass)

- `map_owners` added — owner-ID legend for map tiles (unmet civs are
  anonymised as "unmet civilization").
- `tiles[].city_name` added — display name on city-centre tiles.
- `diagnostics.compat_notes` added — fallback-path notes (WARN channel),
  separated from `failures`.
- Map size resolves via `GameInfo.Maps` (base-game table; `MapSizes` is
  Civ 5 legacy and doesn't exist).
- Version string normalized to semver (`1.0.1`).

## Changes in 1.1 (v1.01)

- `promotions_available` semantics corrected — v1.0 reported `1` for every
  unit including civilians.
- `great_people[].next_cost` gains the `-1` unknown sentinel.
- `cities[].trade_routes[].dest_civ` added — readable civ name, or
  `"domestic"` for internal routes.
- Trade route `yields` keys are now full names (`Food`, `Production`)
  rather than 3-character truncations (`FOO`, `PRO`).
- `meta.speed` / `meta.map_size` / `meta.map_type` now resolve to readable
  names instead of raw hashes and `.lua` filenames.
