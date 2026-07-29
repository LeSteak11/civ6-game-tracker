# Coach snapshot schema — `coach-snapshot/1`

Every hotkey press writes a JSON file whose top-level `schema` field is
`coach-snapshot/1`.  Bump the version if you break field shapes.

## Top-level shape

```jsonc
{
  "schema": "coach-snapshot/1",
  "coach_version": "0.1.0",
  "generated_at_epoch": 1753728000.123,

  "meta": {
    "turn": 87, "year": "725 BC", "era": "Classical Era",
    "civ_type": "CIVILIZATION_EGYPT", "civ_name": "Egyptian",
    "leader_type": "LEADER_CLEOPATRA", "leader_name": "Cleopatra",
    "difficulty": "Prince", "speed": "Standard",
    "map_size": "MAPSIZE_STANDARD", "map_type": "Continents",
    "max_players": 8, "max_turns": 500
  },
  "victories_enabled": ["VICTORY_TECHNOLOGY","VICTORY_CULTURE","VICTORY_RELIGIOUS","VICTORY_CONQUEST","VICTORY_SCORE"],
  "empire": {
    "score": 79, "gold": 330, "gold_yield": 12.4, "gold_maint": 2.0, "gold_net": 10.4,
    "science": 17.1, "culture": 11.3, "faith": 184, "faith_yield": 7.3, "tourism": 8.0,
    "military": 119, "techs_done": 13, "civics_done": 8,
    "num_cities": 2, "num_units": 6, "total_pop": 9,
    "trade_used": 1, "trade_cap": 1,
    "explored_land": 340, "total_land": 1_200
  },
  "current_research": {"type":"TECH_CONSTRUCTION","name":"Construction","progress":92,"cost":200,"turns":7,"boosted":false,"boost_desc":"Build a Water Mill."},
  "current_civic":    {"type":"CIVIC_MILITARY_TRADITION","name":"Military Tradition","progress":0,"cost":50,"turns":4,"boosted":false,"boost_desc":"Clear a Barbarian Outpost."},
  "resources": [{"class":"LUXURY","type":"RESOURCE_IVORY","name":"Ivory","amount":1,"accessible":true}, ...],
  "government": {"type":"GOVERNMENT_CLASSICAL_REPUBLIC","name":"Classical Republic","slots_open":0,"free_change_available":true},
  "policy_slots":    [{"index":0,"slot_type":"SLOT_MILITARY","slot_name":"MILITARY","policy_type":"POLICY_DISCIPLINE","policy_name":"Discipline","effect":"+5 combat vs barbarians."}, ...],
  "policy_available":[{"type":"POLICY_...","slot":"MILITARY","name":"...","effect":"..."}, ...],
  "great_people": [{"class_type":"GREAT_PERSON_CLASS_GENERAL","class":"GENERAL","points":49,"per_turn":1.1,"next_cost":60,"candidate":"Sun Tzu","patronize_cost":150}],

  "techs_available":  [{"type":"...","name":"...","progress":0,"cost":50,"turns":3,"boosted":false,"boost_desc":"...","unlocks":"Warrior, Barracks"}, ...],
  "civics_available": [ ... same shape ... ],

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
    "tiles_rollup":{"owned":24,"worked":8,"terrain":{"grass":10,"plains":6,"desert":4,"hills":3,"coast":1},"features":{"forest":3,"floodplains":2},"improvements":{"farm":4,"pasture":1,"quarry":1}},
    "production_options":[{"kind":"UNIT","type":"UNIT_WARRIOR","name":"Warrior","progress":0,"cost":40,"turns":3}, ...],
    "trade_routes":[{"dest_player":2,"dest_city":"Kabul","yields":{"GOL":2,"FOO":1}}]
  }, ...],

  "units": [{
    "id":42,"type":"UNIT_WARRIOR","name":"Warrior","class":"FORMATION_CLASS_LAND_COMBAT",
    "x":66,"y":30,"hp":84,"hp_max":100,"moves":2,"moves_max":2,
    "combat":20,"ranged":0,"bombard":0,"range":0,
    "xp":15,"xp_needed":30,"promotions_held":0,"promotions_available":0,
    "idle":true,"fortify_turns":2,"charges":0,
    "can_upgrade":false,"upgrade_to":"","upgrade_cost":0
  }, ...],
  "barbarians_visible": [...],
  "camps_visible": [...],
  "camps_revealed_only": [...],

  "map_meta": {"total_plots":4720,"grid":"..."},
  "map_totals": {"revealed":340,"visible":120,"natural_wonders":2},
  "tiles": [{"x":66,"y":32,"visible":true,"terrain":"g","feature":"","resource":"","improvement":"","road":"","owner":"0","district":"CITY_CENTER","is_city":true,"units":"0:WARRIOR:100","extra":"R"}, ...],
  "natural_wonders": [{"name":"...","x":50,"y":40,"type":"FEATURE_..."}],

  "envoys": {"in_hand":0,"points":8,"threshold":100,"per_turn":3.0,"envoys_per_threshold":1},
  "majors_met":     [{"player_id":2,"civ_type":"CIVILIZATION_SUMERIA", ...,"known_agendas":[...]}],
  "city_states_met":[{"player_id":40,"civ_type":"...","cs_type":"...","envoys_sent":1,"suzerain":"none","x":..,"y":..,"at_war":false,"met_turn":20,"active_quests":[...]}],

  "religion": {
    "pantheon":{"type":"BELIEF_...","name":"Religious Settlements","description":"..."},
    "religion":null,
    "beliefs":[],
    "can_found_pantheon":false,
    "city_religion":{"123":"NONE"}
  },

  "notifications":     [{"type":"NOTIFICATION_...","blocker_type":"","message":"..."}],
  "end_turn_blockers": [{"blocker_type":"NEEDS_ORDERS","message":"..."}],

  "turn_blockers_summary": ["3 idle unit(s)", "1 city with no production", "no research selected"],

  "diagnostics": {
    "per_query_seconds": {"meta":0.31,"choices":1.02, ...},
    "total_seconds": 3.42,
    "failures": [{"section":"meta.CITIES","message":"..."}],
    "unsupported": ["governors (Rise & Fall)", "loyalty (Rise & Fall)", ...]
  }
}
```

## Encoding rules

- All numeric fields are numbers, not strings.
- Missing / not-yet-known fields are `null`, `""`, `0`, or `-1` — never a
  string like `"?"` (the Markdown renderer does the `"?"` styling).
- IDs are stable across turns for units and cities (verified against
  Civ 6 engine behaviour — unit IDs recycle on death, so a re-used ID
  paired with a different `type` is a legitimate different unit).
- Coordinates are the game's own plot (X, Y).
- The `map` `terrain` codes use the compact legend printed in the
  Markdown header.  If you consume the JSON directly, treat them as
  opaque strings and derive from `queries.py:build_map_query`.

## Versioning

The Markdown renderer always writes a trailing HTML comment with the
schema version.  Increment `SCHEMA_VERSION` in
`src/civ_mcp/coach/__init__.py` whenever a field is renamed or removed;
add-only changes are backwards-compatible.
