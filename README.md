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

The JSON schema is documented in the appendix at the bottom of this file.

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

# Appendix — snapshot JSON schema (`coach-snapshot/1.1`)

Every hotkey press writes a JSON file whose top-level `schema` field is
`coach-snapshot/1.1`.  Bump `SCHEMA_VERSION` in
`src/civ_mcp/coach/__init__.py` whenever a field is renamed or removed;
add-only changes stay backwards-compatible.

## Top-level shape

```jsonc
{
  "schema": "coach-snapshot/1.1",
  "coach_version": "1.01",
  "generated_at_epoch": 1753728000.123,

  "meta": {
    "turn": 87, "year": "725 BC", "era": "Classical Era",
    "civ_type": "CIVILIZATION_EGYPT", "civ_name": "Egypt",
    "leader_type": "LEADER_CLEOPATRA", "leader_name": "Cleopatra",
    "difficulty": "Chieftain", "speed": "Standard",
    "map_size": "Standard", "map_type": "Continents",
    "max_players": 10, "max_turns": 500
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
  "tiles": [{"x":66,"y":32,"visible":true,"terrain":"g","feature":"","resource":"","improvement":"","road":"","owner":"0","district":"CITY_CENTER","is_city":true,"units":"0:WARRIOR:100","extra":"R"}],
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
