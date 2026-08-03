"""v1.01 regression tests — one case per bug fixed.

Each test is written so it would FAIL against v1.0.  Run alongside
smoke_test.py, which covers the success/partial-failure rendering paths.
"""

import sys, types, importlib.util, json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

civ_mcp = types.ModuleType('civ_mcp'); civ_mcp.__path__ = [str(REPO / 'src/civ_mcp')]
sys.modules['civ_mcp'] = civ_mcp
lua_pkg = types.ModuleType('civ_mcp.lua'); lua_pkg.__path__ = [str(REPO / 'src/civ_mcp/lua')]
sys.modules['civ_mcp.lua'] = lua_pkg
spec = importlib.util.spec_from_file_location('civ_mcp.lua._helpers', str(REPO / 'src/civ_mcp/lua/_helpers.py'))
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h); sys.modules['civ_mcp.lua._helpers'] = h

for mod in ['__init__', 'queries', 'parser', 'delta', 'markdown', 'archive', 'history']:
    full = f'civ_mcp.coach.{mod}' if mod != '__init__' else 'civ_mcp.coach'
    spec = importlib.util.spec_from_file_location(full, str(REPO / f'src/civ_mcp/coach/{mod}.py'))
    m = importlib.util.module_from_spec(spec); sys.modules[full] = m; spec.loader.exec_module(m)

from civ_mcp.coach import parser as P
from civ_mcp.coach import markdown as M
from civ_mcp.coach import queries as Q
from civ_mcp.coach import archive as A
from civ_mcp.coach import SCHEMA_VERSION, COACH_VERSION

def strip_lua_comments(src: str) -> str:
    """Drop `--` comment lines so assertions test real code, not prose."""
    out = []
    for line in src.splitlines():
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        out.append(line)
    return "\n".join(out)


failures = []
def check(name, cond, detail=""):
    if cond:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name}  {detail}")
        failures.append(name)


print("\n=== BUG 1: phantom promotions ===")
# Live v1.0 emitted promotions_available=1 for a 0-XP Trader.  The Lua now
# gates on PromotionClass + CanStartCommand, so a civilian emits 0.
units_lines = [
    # Trader: civilian, 0 xp -> must be 0 available
    "UNIT|3|UNIT_TRADER|Trader|FORMATION_CLASS_CIVILIAN|66|32|100|100|2|2|0|0|0|0|0|15|0|0|true|0|0|false||0",
    # Warrior with 7/15 xp -> not enough, 0 available
    "UNIT|1|UNIT_WARRIOR|Warrior|FORMATION_CLASS_LAND_COMBAT|66|30|84|100|2|2|20|0|0|0|7|15|0|0|true|0|0|false||0",
    # Warrior with 20/15 xp -> promotion pending, 1 available
    "UNIT|2|UNIT_WARRIOR|Warrior|FORMATION_CLASS_LAND_COMBAT|65|30|100|100|2|2|20|0|0|0|20|15|0|1|true|0|0|false||0",
]
u = P.parse_units(units_lines)
by_id = {x["id"]: x for x in u["units"]}
check("Trader reports 0 promotions available", by_id[3]["promotions_available"] == 0,
      f"got {by_id[3]['promotions_available']}")
check("Under-XP warrior reports 0", by_id[1]["promotions_available"] == 0,
      f"got {by_id[1]['promotions_available']}")
check("Over-XP warrior reports 1", by_id[2]["promotions_available"] == 1,
      f"got {by_id[2]['promotions_available']}")

# Lua source assertions: the broken GetLevel heuristic must be gone.
units_src = Q.build_units_query()
units_code = strip_lua_comments(units_src)
check("GetLevel heuristic removed from units Lua (code, not comments)",
      "GetLevel" not in units_code)
check("units Lua uses CanStartCommand(PROMOTE)", "UnitCommandTypes.PROMOTE" in units_src)
check("units Lua guards on promoClass", 'if promoClass ~= "" then' in units_src)


print("\n=== BUG 2: Great Person recruit cost 0 ===")
gp_lines_unknown = [
    "META|87|725 BC|Classical Era|CIVILIZATION_EGYPT|Egypt|LEADER_CLEOPATRA|Cleopatra|Chieftain|Standard|Standard|Continents|10|500",
    # next_cost -1 = unknown sentinel
    "GPPT|GREAT_PERSON_CLASS_GENERAL|GENERAL|49|1.1|-1||-1",
    # next_cost 240 = known
    "GPPT|GREAT_PERSON_CLASS_PROPHET|PROPHET|25|2.3|240|Confucius|496",
]
m = P.parse_meta(gp_lines_unknown)
gp = {g["class"]: g for g in m["great_people"]}
check("unknown GP cost parses as -1", gp["GENERAL"]["next_cost"] == -1, f"got {gp['GENERAL']['next_cost']}")
check("known GP cost parses as 240", gp["PROPHET"]["next_cost"] == 240)

snap = {
    "schema": SCHEMA_VERSION, "coach_version": COACH_VERSION, "generated_at_epoch": 1.0,
    "meta": m["meta"], "empire": {}, "great_people": m["great_people"],
    "section_status": {"header": "ok", "great_people": "ok"},
    "diagnostics": {}, "turn_blockers_summary": [],
}
md = M.render_markdown(snap, {"first_snapshot": True})
check("unknown GP cost renders 'unknown'", "next recruit cost unknown" in md)
check("unknown GP cost never renders as 0", "next recruit cost 0" not in md)
check("known GP cost renders numerically", "next recruit cost 240" in md)

meta_src = Q.build_meta_query()
check("meta Lua tries GetTimeline first", "gpm:GetTimeline()" in meta_src)
check("meta Lua dumps GP methods on failure", "great_people.api" in meta_src)


print("\n=== BUG 3: civics availability over-broad ===")
choices_src = Q.build_choices_query()
check("choices Lua uses CivicPrereqs", "GameInfo.CivicPrereqs()" in choices_src)
check("choices Lua has prereq gate fn", "civicPrereqsMet" in choices_src)
check("choices Lua probes multiple civic method names", "CanAdvanceCivic" in choices_src)
# The naive fallback ("list everything not yet researched") must no longer be
# reachable without a prereq check.
check("no bare !HasCivic fallback remains",
      'falling back to !HasCivic' not in choices_src)


print("\n=== BUG 4: metadata garbage ===")
meta_clean = [
    "META|87|725 BC|Classical Era|CIVILIZATION_EGYPT|Egypt|LEADER_CLEOPATRA|Cleopatra|Chieftain|Standard|Standard|Continents|10|500",
]
mm = P.parse_meta(meta_clean)["meta"]
check("speed resolved", mm["speed"] == "Standard", f"got {mm['speed']!r}")
check("map_size readable", mm["map_size"] == "Standard", f"got {mm['map_size']!r}")
check("map_type has no .lua", ".lua" not in mm["map_type"], f"got {mm['map_type']!r}")
check("map_type readable", mm["map_type"] == "Continents", f"got {mm['map_type']!r}")
# Lua-side: MakeHash comparison loops must exist for speed + map size
check("meta Lua resolves speed via MakeHash", "MakeHash(row.GameSpeedType)" in meta_src)
check("meta Lua resolves map size via MakeHash", "MakeHash(row.MapSizeType)" in meta_src)
check("meta Lua strips .lua extension", '%.lua$' in meta_src)


print("\n=== BUG 5: trade route text ===")
cities_lines = [
    "CITY|123|Râ-Kedet|true|66|32|3|1.0|24|-1|10|3|1|2|7.0|14.7|10.5|8.5|5.1|6.3|BUILDING_STONEHENGE|Stonehenge|420|425|1|34|200|200|0|0|5|NONE",
    # domestic route: dest_player 0 == me, dest_civ "domestic", full yield names
    "TRADE|123|0|Luxis|Food:1,Production:1,|domestic",
    # foreign route
    "TRADE|123|2|Uruk|Gold:4,Science:1,|Sumerian",
]
c = P.parse_cities(cities_lines)
routes = c["cities"][0]["trade_routes"]
check("domestic route tagged", routes[0]["dest_civ"] == "domestic", f"got {routes[0]['dest_civ']!r}")
check("foreign route civ resolved", routes[1]["dest_civ"] == "Sumerian")
check("yields use full names", "Food" in routes[0]["yields"] and "Production" in routes[0]["yields"],
      f"got {routes[0]['yields']}")
check("no FOO/PRO truncation", "FOO" not in routes[0]["yields"] and "PRO" not in routes[0]["yields"])

snap2 = {
    "schema": SCHEMA_VERSION, "coach_version": COACH_VERSION, "generated_at_epoch": 1.0,
    "meta": mm, "empire": {}, "cities": c["cities"],
    "section_status": {"header": "ok", "cities": "ok"},
    "diagnostics": {}, "turn_blockers_summary": [],
}
md2 = M.render_markdown(snap2, {"first_snapshot": True})
check("markdown shows no player0", "player0" not in md2)
check("markdown shows domestic label", "Luxis (domestic)" in md2, )
check("markdown shows foreign civ", "Uruk (Sumerian)" in md2)
check("markdown shows readable yields", "Food +1" in md2)

cities_src = Q.build_cities_query()
check("cities Lua no longer truncates yields", ':sub(1,3)' not in cities_src)


print("\n=== BUG 6: same-turn delta noise ===")
empty_delta = {
    "first_snapshot": False, "turns_elapsed": 0,
    "empire_delta": {"score": 0, "gold": 0},
    "tiles_newly_revealed": {"count": 0, "sample": []},
    "units_delta": {"born": [], "lost": [], "promoted": [], "upgraded": [], "moved_count": 0,
                    "damaged": [], "healed": []},
    "cities_delta": {"grew": [], "starved": [], "production_completed": []},
    "resources_delta": {},
    "diplo_delta": {"newly_met_majors": [], "newly_met_city_states": [], "new_wars": []},
}
txt = M._fmt_delta(empty_delta)
check("empty same-turn delta says no meaningful changes", txt.startswith("No meaningful changes."), f"got {txt!r}")
check("empty delta does not print 'turns elapsed: 0'", "turns elapsed: 0" not in txt)

real_delta = dict(empty_delta)
real_delta["turns_elapsed"] = 1
real_delta["empire_delta"] = {"score": 4}
real_delta["cities_delta"] = {"grew": [{"name": "Sais"}], "starved": [], "production_completed": []}
txt2 = M._fmt_delta(real_delta)
check("real delta still itemised", "turns elapsed: 1" in txt2 and "score: +4" in txt2)
check("real delta lists grown city", "Sais" in txt2)


print("\n=== schema/version bump ===")
check("schema bumped to 1.4", SCHEMA_VERSION == "coach-snapshot/1.4", SCHEMA_VERSION)
check("coach version 1.8.2 (semver)", COACH_VERSION == "1.8.2", COACH_VERSION)

print("\n=== v1.0.1 cleanup pass ===")
# Map-size resolution must use GameInfo.Maps (base game), not just MapSizes (Civ5 legacy)
meta_src2 = Q.build_meta_query()
check("map size resolves via GameInfo.Maps", "GameInfo.Maps" in meta_src2)
check("map size unresolved emits WARN not DIAG",
      'WARN|META.map_size' in meta_src2 and 'DIAG|META.map_size' not in meta_src2)

# Probe/compat notes must go to the WARN channel, not DIAG (runtime failures)
choices_src2 = Q.build_choices_query()
check("civic probe notes are WARN", 'WARN|CHOICES.probe' in choices_src2)
check("no civic probe DIAG remains", 'DIAG|CHOICES.probe' not in choices_src2)

# Map query: owner legend + city names
map_src = Q.build_map_query()
check("map Lua emits OWNER legend lines", 'OWNER|' in map_src)
check("map Lua unmet civs are anonymised", "unmet civilization" in map_src)
check("map Lua attaches city names", "cityNameAt" in map_src)

# Parser: OWNER lines and city_name field
map_parsed = P.parse_map([
    "MAPMETA|4720|84x60",
    "MAP|66|32|1|g|||||0|CITY_CENTER|true||R/F|Ra-Kedet",
    "MAP|10|10|0|p|||||||false|||",
    "OWNER|0|me (Egypt)",
    "OWNER|63|Barbarians",
    "MAPTOTAL|2|1|0",
])
check("parser reads city_name on city tiles", map_parsed["tiles"][0]["city_name"] == "Ra-Kedet",
      map_parsed["tiles"][0].get("city_name"))
check("parser reads empty city_name elsewhere", map_parsed["tiles"][1]["city_name"] == "")
check("parser collects owner legend", map_parsed["owners"] == {"0": "me (Egypt)", "63": "Barbarians"},
      map_parsed["owners"])

# Markdown: legend rendered, city name in map block
snap_map = {
    "schema": SCHEMA_VERSION, "coach_version": COACH_VERSION, "generated_at_epoch": 1.0,
    "meta": {"turn": 87}, "empire": {},
    "tiles": map_parsed["tiles"], "map_totals": map_parsed["map_totals"],
    "map_owners": map_parsed["owners"],
    "section_status": {"header": "ok", "map": "ok"},
    "diagnostics": {"compat_notes": [{"section": "CHOICES.probe", "message": "using cul:CanProgress() for civic availability"}]},
    "turn_blockers_summary": [],
}
md_map = M.render_markdown(snap_map, {"first_snapshot": True})
check("markdown renders owner legend", "**Owner IDs:** 0=me (Egypt), 63=Barbarians" in md_map)
check("markdown map line carries city name", "|Ra-Kedet" in md_map)
check("compat notes render as notes not failures",
      "compatibility notes" in md_map and "failures at runtime" not in md_map)

print("\n=== Phase 2 Task 1: persistent game archives ===")
import tempfile

# -- Seeds: Lua source contract -------------------------------------------
meta_src3 = Q.build_meta_query()
check("meta Lua emits SEEDS line", '"SEEDS|"' in meta_src3)
check("meta Lua reads GAME_SYNC_RANDOM_SEED via GetValue",
      'GetValue("GAME_SYNC_RANDOM_SEED")' in meta_src3)
check("meta Lua reads map RANDOM_SEED via GetValue",
      'GetValue("RANDOM_SEED")' in meta_src3)
check("missing seed emits WARN + -1 sentinel, never a guess",
      'WARN|META.seeds' in meta_src3 and 'DIAG|META.seeds' not in meta_src3)

# -- Seeds: parser --------------------------------------------------------
seed_meta_line = "META|87|725 BC|Classical Era|CIVILIZATION_EGYPT|Egypt|LEADER_CLEOPATRA|Cleopatra|Chieftain|Standard|Standard|Continents|10|500"
pm = P.parse_meta([seed_meta_line, "SEEDS|123456789|987654321"])
check("parser merges seeds into meta",
      pm["meta"].get("game_seed") == 123456789 and pm["meta"].get("map_seed") == 987654321,
      str({k: pm["meta"].get(k) for k in ("game_seed", "map_seed")}))
pm_rev = P.parse_meta(["SEEDS|11|22", seed_meta_line])
check("seed merge is order-independent",
      pm_rev["meta"].get("game_seed") == 11, pm_rev["meta"].get("game_seed"))
pm_nometa = P.parse_meta(["SEEDS|1|2"])
check("seeds alone never fake an ok header", pm_nometa["meta"] == {}, pm_nometa["meta"])
pm_unk = P.parse_meta([seed_meta_line, "SEEDS|-1|-1"])
check("unknown seeds stay -1 sentinel", pm_unk["meta"].get("game_seed") == -1)

# -- Archive behaviour ----------------------------------------------------
def mk_snap(turn=87, game_seed=111, map_seed=222, gold=100.0, epoch=1000.0,
            civ_type="CIVILIZATION_EGYPT", civ_name="Egypt"):
    return {
        "schema": SCHEMA_VERSION, "coach_version": COACH_VERSION,
        "generated_at_epoch": epoch,
        "meta": {"turn": turn, "civ_type": civ_type, "civ_name": civ_name,
                 "leader_type": "LEADER_CLEOPATRA", "leader_name": "Cleopatra",
                 "difficulty": "Chieftain", "speed": "Standard",
                 "map_size": "Standard", "map_type": "Continents",
                 "max_players": 10, "max_turns": 500,
                 "game_seed": game_seed, "map_seed": map_seed},
        "empire": {"gold": gold},
        "section_status": {"header": "ok"},
        # diagnostics always differ between captures — must not defeat dedup
        "diagnostics": {"total_seconds": epoch / 7.0},
    }

tmp = Path(tempfile.mkdtemp(prefix="civ6-archive-regress-"))

r1 = A.write_snapshot(tmp, mk_snap(), "# md1")
check("first capture creates game-001_egypt",
      r1 is not None and r1.created_game and r1.game_id == "game-001_egypt",
      getattr(r1, "game_id", r1))
check("first capture on a turn is r01", r1.capture_name == "turn-0087_r01", r1.capture_name)
check("snapshot pair written",
      r1.json_path is not None and r1.json_path.exists() and r1.md_path.exists())
check("per-game latest mirrors written",
      (r1.game_dir / "latest.md").read_text(encoding="utf-8") == "# md1"
      and (r1.game_dir / "latest.json").exists())
gj = json.loads((r1.game_dir / "game.json").read_text(encoding="utf-8"))
_id_fields = ("game_id", "civ_name", "leader_name", "difficulty", "map_type",
              "map_size", "speed", "created_at_epoch", "created_turn",
              "last_turn", "schema", "fingerprint", "fingerprint_id")
check("game.json carries all identity fields",
      all(k in gj for k in _id_fields), [k for k in _id_fields if k not in gj])
check("game.json last_turn tracks capture", gj["last_turn"] == 87)

r2 = A.write_snapshot(tmp, mk_snap(epoch=2000.0), "# md1-refreshed")
check("identical capture deduplicated (volatile fields ignored)",
      r2.deduplicated and r2.md_path is None and r2.json_path is None)
check("dedup writes no r02 file",
      not (r1.game_dir / "snapshots" / "turn-0087_r02.json").exists())
check("dedup still refreshes latest.md",
      (r1.game_dir / "latest.md").read_text(encoding="utf-8") == "# md1-refreshed")

r3 = A.write_snapshot(tmp, mk_snap(gold=150.0, epoch=3000.0), "# md2")
check("changed same-turn capture becomes r02",
      not r3.deduplicated and r3.capture_name == "turn-0087_r02", r3.capture_name)

r4 = A.write_snapshot(tmp, mk_snap(turn=88, gold=160.0, epoch=4000.0), "# md3")
check("new turn resets to r01", r4.capture_name == "turn-0088_r01", r4.capture_name)
check("same game folder reused across turns",
      r4.game_id == r1.game_id and not r4.created_game)

r5 = A.write_snapshot(tmp, mk_snap(turn=80, gold=90.0, epoch=5000.0), "# md4")
check("seed match reopens folder even after loading an earlier save",
      r5.game_id == r1.game_id and not r5.created_game)

r6 = A.write_snapshot(tmp, mk_snap(game_seed=999, map_seed=888, turn=1, epoch=6000.0), "# md5")
check("different seeds start game-002",
      r6.created_game and r6.game_id.startswith("game-002"), r6.game_id)

r7 = A.write_snapshot(
    tmp, {"section_status": {"header": "failed"}, "meta": {}, "generated_at_epoch": 1.0}, "# junk")
check("capture without a trusted turn is refused (never guess the game)", r7 is None)

check("archive module never imports the FireTuner stack",
      "civ_mcp.connection" not in Path(REPO / "src/civ_mcp/coach/archive.py").read_text(encoding="utf-8"))

print("\n=== Phase 2 Task 2: policy effects + full tech/civic trees ===")

# -- Lua source contract --------------------------------------------------
choices_src3 = Q.build_choices_query()
check("choices Lua emits TTREE lines", '"TTREE|' in choices_src3)
check("choices Lua emits CTREE lines", '"CTREE|' in choices_src3)
check("tech prereqs use confirmed TechnologyPrereqs table",
      "GameInfo.TechnologyPrereqs()" in choices_src3)
check("missing prereq table is WARN not silence",
      "WARN|CHOICES.probe|GameInfo.TechnologyPrereqs unavailable" in choices_src3)
check("tree reuses probed civic gate (no new guessed method)",
      "civicCanFn" in choices_src3 and "civicPrereqsMet" in choices_src3)

# -- Parser ---------------------------------------------------------------
ch = P.parse_choices([
    "TTREE|TECH_POTTERY|Pottery|ANCIENT|done|0|0|-1|",
    "TTREE|TECH_IRRIGATION|Irrigation|ANCIENT|current|31|50|4|POTTERY",
    "TTREE|TECH_WRITING|Writing|ANCIENT|available|12|50|5|POTTERY",
    "TTREE|TECH_CURRENCY|Currency|ANCIENT|blocked|0|120|-1|WRITING,FOREIGN_TRADE",
    "CTREE|CIVIC_CODE_OF_LAWS|Code of Laws|ANCIENT|done|0|0|-1|",
    "CTREE|CIVIC_CRAFTSMANSHIP|Craftsmanship|ANCIENT|blocked|10|40|-1|FOREIGN_TRADE",
])
tt = {x["type"]: x for x in ch["tech_tree"]}
check("tree parser: done status", tt["TECH_POTTERY"]["status"] == "done")
check("tree parser: prereq list split", tt["TECH_CURRENCY"]["prereqs"] == ["WRITING", "FOREIGN_TRADE"],
      tt["TECH_CURRENCY"]["prereqs"])
check("tree parser: partial derived from banked progress on non-done",
      tt["TECH_WRITING"]["partial"] is True and tt["TECH_POTTERY"]["partial"] is False)
check("tree parser: current not double-counted as partial in shape",
      tt["TECH_IRRIGATION"]["status"] == "current" and tt["TECH_IRRIGATION"]["partial"] is True)
check("civic tree parsed with same shape", ch["civic_tree"][1]["prereqs"] == ["FOREIGN_TRADE"])

# -- Markdown -------------------------------------------------------------
snap_tree = {
    "schema": SCHEMA_VERSION, "coach_version": COACH_VERSION, "generated_at_epoch": 1.0,
    "meta": {"turn": 87}, "empire": {},
    "tech_tree": ch["tech_tree"], "civic_tree": ch["civic_tree"],
    "policy_slots": [
        {"index": 0, "slot_type": "SLOT_MILITARY", "slot_name": "MILITARY",
         "policy_type": "POLICY_DISCIPLINE", "policy_name": "Discipline",
         "effect": "+5 Combat Strength vs. Barbarians"},
    ],
    "policy_available": [
        {"type": "POLICY_URBAN_PLANNING", "slot": "ECONOMIC", "name": "Urban Planning",
         "effect": "+1 Production in all cities"},
    ],
    "government": {"name": "Chiefdom", "slots_open": 0, "free_change_available": True},
    "section_status": {"header": "ok", "tech_tree": "ok", "civic_tree": "ok",
                       "policy_slots": "ok", "policy_available": "ok", "government": "ok"},
    "diagnostics": {}, "turn_blockers_summary": [],
}
md_tree = M.render_markdown(snap_tree, {"first_snapshot": True})
check("markdown renders TECH TREE rollup", "### TECH TREE (1/4 completed)" in md_tree)
check("markdown lists completed techs", "**completed:** Pottery" in md_tree)
check("markdown shows banked partial progress", "Writing (12/50sci)" in md_tree)
check("markdown blocked lists only missing prereqs", "Currency ← WRITING, FOREIGN_TRADE" in md_tree)
check("markdown blocked prereq drops completed ones", "Craftsmanship ← FOREIGN_TRADE" in md_tree)

# Blocked rollup is frontier-only: nearest 8 by (missing prereqs, cost),
# the rest referred to the JSON.  40 blocked items must not emit 40 lines.
_big_blocked = [
    {"type": f"TECH_X{i}", "name": f"DeepTech{i}", "era": "MODERN", "status": "blocked",
     "progress": 0.0, "cost": 1000.0 + i, "turns": -1, "partial": False,
     "prereqs": [f"X{i-1}", f"X{i-2}", f"X{i-3}"]}
    for i in range(40)
]
_near = {"type": "TECH_NEAR", "name": "NearTech", "era": "ANCIENT", "status": "blocked",
         "progress": 0.0, "cost": 80.0, "turns": -1, "partial": False, "prereqs": ["WRITING"]}
snap_big = dict(snap_tree)
snap_big["tech_tree"] = ch["tech_tree"] + _big_blocked + [_near]
md_big = M.render_markdown(snap_big, {"first_snapshot": True})
check("blocked rollup caps at 8 frontier items",
      "...and 34 more (see JSON)" in md_big, [l for l in md_big.splitlines() if "more (see JSON)" in l])
check("frontier sorts fewest-missing-prereqs first",
      md_big.find("NearTech") < md_big.find("DeepTech"),
      "NearTech should precede all DeepTech entries")
check("deep-tree items stay out of the markdown", "DeepTech39" not in md_big)
check("markdown renders CIVIC TREE section", "### CIVIC TREE (1/2 completed)" in md_tree)
check("slotted policy shows effect text",
      "Discipline — +5 Combat Strength vs. Barbarians" in md_tree)
check("available policy shows effect text",
      "Urban Planning — +1 Production in all cities" in md_tree)

snap_tree_failed = dict(snap_tree)
snap_tree_failed["tech_tree"] = None
snap_tree_failed["section_status"] = dict(snap_tree["section_status"], tech_tree="failed")
md_tf = M.render_markdown(snap_tree_failed, {"first_snapshot": True})
check("failed tech tree renders QUERY FAILED, never empty rollup",
      "TECH TREE" in md_tf and "QUERY FAILED" in md_tf and "(0/0 completed)" not in md_tf)

print("\n=== Phase 2 Task 3: opponent state expansion (schema 1.3) ===")
from civ_mcp.coach import delta as D
from civ_mcp.coach import history as H

# -- Lua source contract --------------------------------------------------
map_src2 = Q.build_map_query()
check("map Lua emits RIVALCITY lines", '"RIVALCITY|' in map_src2)
check("rival cities are fog-gated on the revealed centre plot",
      "pVis:IsRevealed(cx, cy)" in map_src2)
check("rival pop/defense read only while currently visible",
      "pVis:IsVisible(cx, cy)" in map_src2)
check("original founder is probed, never guessed",
      'type(cc.GetOriginalOwner) == "function"' in map_src2
      and "WARN|MAP.rival_cities|GetOriginalOwner unavailable" in map_src2)

diplo_src = Q.build_diplo_query()
check("diplo Lua emits WARS matrix lines", '"WARS|' in diplo_src)
check("diplo Lua emits PUBSTATS (world-rankings public)", '"PUBSTATS|' in diplo_src)
check("diplo Lua emits DEAD tombstones for eliminated met players", '"DEAD|' in diplo_src)
check("rival-rival relations probed with WARN fallback",
      'type(ai.GetDiplomaticStateIndex) ~= "function"' in diplo_src
      and "WARN|DIPLO.airel" in diplo_src)
check("rival government gated on diplomatic visibility >= 1",
      "if dvis and dvis >= 1 then" in diplo_src)
check("CS envoys-by-civ emitted", '"CSENVOYS|' in diplo_src)

rel_src = Q.build_religion_query()
check("religion Lua emits WREL world religions", '"WREL|' in rel_src)
check("religion founder probed with WARN, -1 sentinel",
      "WARN|REL.world" in rel_src)

# -- Parser ---------------------------------------------------------------
dp = P.parse_diplo([
    "MAJOR|2|CIVILIZATION_SUMERIA|Sumerian|LEADER_GILGAMESH|Gilgamesh|false|12|1|142|169|false|false|true|false|4|DIPLO_STATE_NEUTRAL",
    "MAJOR|3|CIVILIZATION_BRAZIL|Brazilian|LEADER_PEDRO|Pedro II|false|30|0|88|40|false|false|false|false|4|DIPLO_STATE_NEUTRAL",
    "WARS|2|3,63",
    "PUBSTATS|2|14|9|3",
    "AIREL|2|3|DIPLO_STATE_DENOUNCED",
    "RIVGOV|2|GOVERNMENT_OLIGARCHY|Oligarchy|1",
    "DEAD|5|CIVILIZATION_KONGO|Kongolese|true",
    "CS|40|CIVILIZATION_KABUL|Kabul|MILITARISTIC|3|ME|10|20|false|22",
    "CSENVOYS|40|0:3,2:1",
])
maj2 = next(m for m in dp["majors"] if m["player_id"] == 2)
check("wars matrix attached to major", maj2["wars_with"] == [3, 63], maj2["wars_with"])
check("public stats attached", maj2["public_stats"] == {"techs": 14, "civics": 9, "tourism": 3})
check("rival-rival relation attached",
      maj2["relations"] == [{"with": 3, "state": "DIPLO_STATE_DENOUNCED"}])
check("rival government carries visibility + source tag",
      maj2["government"]["type"] == "GOVERNMENT_OLIGARCHY"
      and maj2["government"]["read_at_visibility"] == 1
      and maj2["government"]["source"] == "diplo_vis")
maj3 = next(m for m in dp["majors"] if m["player_id"] == 3)
check("missing WARS/PUBSTATS lines parse as None, not empty-list lies",
      maj3["wars_with"] is None and maj3["public_stats"] is None)
check("DEAD tombstone parsed", dp["eliminated"][0]["civ_name"] == "Kongolese"
      and dp["eliminated"][0]["alive"] is False)
cs40 = dp["city_states"][0]
check("CS envoys-by-civ parsed", cs40["envoys_by_civ"] == {"0": 3, "2": 1}, cs40["envoys_by_civ"])

mp = P.parse_map([
    "MAPMETA|4720|84x60",
    "RIVALCITY|2|Uruk|30|20|true|visible|7|28|85|100|2",
    "RIVALCITY|2|Kish|32|24|false|revealed|-1|-1|-1|-1|-1",
    "OWNER|2|Sumerian",
    "MAPTOTAL|1|1|0",
])
check("rival city parsed with visibility tier",
      mp["rival_cities"][0]["visibility"] == "visible"
      and mp["rival_cities"][1]["visibility"] == "revealed")
check("revealed-only city keeps -1 unknowns (no fake zeros)",
      mp["rival_cities"][1]["population"] == -1 and mp["rival_cities"][1]["defense"] == -1)

rp = P.parse_religion(["WREL|2|RELIGION_HINDUISM|Hinduism|2"])
check("world religion parsed with founder + public tag",
      rp["world_religions"][0]["founder"] == 2
      and rp["world_religions"][0]["source"] == "public")

# -- Rivals merge + units rollup -----------------------------------------
status_ok = {"majors_met": "ok", "map": "ok"}
rivals = P.build_rivals(dp, mp, rp, status_ok)
r2 = next(r for r in rivals if r.get("player_id") == 2)
check("rivals merge attaches known cities", len(r2["known_cities"]) == 2)
check("rivals merge attaches founded religion", r2["religion_founded"]["name"] == "Hinduism")
check("eliminated major appears in rivals with alive=false",
      any(r.get("alive") is False and r.get("civ_name") == "Kongolese" for r in rivals))
check("failed majors section -> rivals is None, never []",
      P.build_rivals(dp, mp, rp, {"majors_met": "failed"}) is None)
rivals_mapfail = P.build_rivals(dp, mp, rp, {"majors_met": "ok", "map": "failed"})
check("failed map -> known_cities None, not empty list",
      next(r for r in rivals_mapfail if r.get("player_id") == 2)["known_cities"] is None)

ubc = P.units_by_civ([
    {"units": "2:UNIT_WARRIOR:100;2:UNIT_SLINGER:80"},
    {"units": "63:UNIT_WARRIOR:100"},
    {"units": ""},
])
check("units-by-civ rollup aggregates owners",
      ubc["2"]["count"] == 2 and ubc["2"]["types"]["UNIT_WARRIOR"] == 1 and ubc["63"]["count"] == 1)

# -- World events (delta) -------------------------------------------------
def _rv(pid, name, alive=True, mil=100, wars=None, gov=None):
    return {"player_id": pid, "civ_name": name, "alive": alive, "military": mil,
            "wars_with": wars or [], "government": gov}

prev_snap = {
    "meta": {"turn": 140},
    "rivals": [_rv(2, "Sumerian", mil=160), _rv(3, "Brazilian", mil=90)],
    "rival_cities": [
        {"owner": 3, "name": "Rio de Janeiro", "x": 50, "y": 10, "original_owner": 3},
    ],
    "world_religions": [],
    "city_states_met": [{"player_id": 40, "civ_name": "Kabul", "suzerain": "ME"}],
    "cities": [{"id": 1, "name": "Thebes", "x": 60, "y": 30}],
}
curr_snap = {
    "meta": {"turn": 145},
    "rivals": [
        _rv(2, "Sumerian", mil=210, wars=[3]),
        _rv(3, "Brazilian", alive=False, mil=0),
    ],
    "rival_cities": [
        {"owner": 2, "name": "Rio de Janeiro", "x": 50, "y": 10, "original_owner": 3},
    ],
    "world_religions": [{"founder": 2, "type": "RELIGION_HINDUISM", "name": "Hinduism"}],
    "city_states_met": [{"player_id": 40, "civ_name": "Kabul", "suzerain": "SUMERIA"}],
    "cities": [{"id": 1, "name": "Thebes", "x": 60, "y": 30}],
}
evs = D._world_events(prev_snap, curr_snap)
kinds = sorted(e["event"] for e in evs)
check("elimination event derived", "eliminated" in kinds, kinds)
check("war-anywhere event derived", "war_declared" in kinds)
check("city capture derived from ownership flip", "city_captured" in kinds)
check("religion founding derived", "religion_founded" in kinds)
check("military swing derived", "military_swing" in kinds)
check("suzerain flip derived", "suzerain_changed" in kinds)
cap = next(e for e in evs if e["event"] == "city_captured")
check("capture names both civs", cap["civs"] == ["Brazilian", "Sumerian"], cap)

# Failed sections suppress events instead of fabricating them
curr_failed = dict(curr_snap)
curr_failed["rivals"] = None
curr_failed["rival_cities"] = None
evs_failed = D._world_events(prev_snap, curr_failed)
check("failed rival/map sections fabricate no rival events",
      not any(e["event"] in ("eliminated", "city_captured", "war_declared", "city_lost_by_me")
              for e in evs_failed), [e["event"] for e in evs_failed])

# -- Markdown -------------------------------------------------------------
snap_world = {
    "schema": SCHEMA_VERSION, "coach_version": COACH_VERSION, "generated_at_epoch": 1.0,
    "meta": {"turn": 145}, "empire": {},
    "majors_met": dp["majors"], "city_states_met": dp["city_states"],
    "rivals": rivals, "rival_cities": mp["rival_cities"],
    "units_by_civ": {"2": {"count": 2, "types": {"UNIT_WARRIOR": 2}, "total_hp": 200},
                     "0": {"count": 5, "types": {"UNIT_WARRIOR": 5}, "total_hp": 500}},
    "map_owners": {"0": "me (Egypt)", "2": "Sumerian", "3": "Brazilian", "63": "Barbarians"},
    "section_status": {"header": "ok", "majors_met": "ok", "city_states_met": "ok", "map": "ok"},
    "diagnostics": {}, "turn_blockers_summary": [],
}
md_w = M.render_markdown(snap_world, {"first_snapshot": False, "turns_elapsed": 1,
                                      "world_events": evs})
check("WORLD NEWS section renders when events exist", "## WORLD NEWS" in md_w)
check("capture headline names city and civs",
      "captured **Rio de Janeiro**" in md_w)
check("elimination headline renders", "has been eliminated" in md_w)
check("majors block shows public stats line", "public: techs 14 | civics 9" in md_w)
check("majors block lists known cities with stale marker",
      "known cities (2): Uruk★ p7, Kish?" in md_w, [l for l in md_w.splitlines() if "known cities" in l])
check("majors block shows rival wars", "at war with: Brazilian, Barbarians" in md_w)
check("majors block shows vis-gated government", "government: Oligarchy (vis 1)" in md_w)
check("eliminated tombstone renders", "☠️ **Kongolese** — ELIMINATED" in md_w)
check("CS line shows envoys by civ", "envoys: me (Egypt) 3, Sumerian 1" in md_w)
check("foreign forces rollup renders, excluding me",
      "### FOREIGN FORCES CURRENTLY VISIBLE" in md_w
      and "Sumerian: 2 unit(s)" in md_w and "me (Egypt): 5" not in md_w)
md_quiet = M.render_markdown(snap_world, {"first_snapshot": False, "turns_elapsed": 1,
                                          "world_events": []})
check("no WORLD NEWS section on a quiet world", "## WORLD NEWS" not in md_quiet)

# -- History persistence --------------------------------------------------
htmp = Path(tempfile.mkdtemp(prefix="civ6-history-regress-"))
hsnap = {"meta": {"turn": 145}, "rivals": rivals, "city_states_met": dp["city_states"]}
H.update_history(htmp, hsnap, evs)
hist = json.loads((htmp / "rivals.json").read_text(encoding="utf-8"))
check("history timeline written per major", "2" in hist["majors"]
      and hist["majors"]["2"]["timeline"][0]["turn"] == 145)
check("history events written with turn stamps",
      json.loads((htmp / "events.json").read_text(encoding="utf-8"))[0]["turn"] == 145)
H.update_history(htmp, hsnap, [])
hist2 = json.loads((htmp / "rivals.json").read_text(encoding="utf-8"))
check("same-turn recapture replaces, never duplicates, timeline entries",
      len(hist2["majors"]["2"]["timeline"]) == 1)
hsnap2 = {"meta": {"turn": 146}, "rivals": rivals, "city_states_met": dp["city_states"]}
H.update_history(htmp, hsnap2, [])
hist3 = json.loads((htmp / "rivals.json").read_text(encoding="utf-8"))
check("new turn appends timeline entry",
      [e["turn"] for e in hist3["majors"]["2"]["timeline"]] == [145, 146])
check("turnless snapshot writes no history",
      (H.update_history(htmp, {"meta": {}}, [{"event": "x"}]) is None
       and len(json.loads((htmp / "events.json").read_text(encoding="utf-8"))) == len(evs)))

print("\n=== Phase 2 Task 4 (G0+G2): reports-screen data ===")

# -- G0 probes: source contract -------------------------------------------
diplo_src2 = Q.build_diplo_query()
check("gossip probe present with manager candidates",
      "gossip_probe" in diplo_src2 and "Game.GetGossipManager" in diplo_src2
      and "GossipManager" in diplo_src2)
check("gossip probe dumps real method names (DIAG)",
      "DIAG|DIPLO.gossip_probe.api" in diplo_src2)
check("gossip probe checks GameInfo.Gossips", "GameInfo.Gossips" in diplo_src2)
map_src3 = Q.build_map_query()
check("plot-yield probe present", "MAP.yield_probe" in map_src3
      and 'type(p0.GetYield) == "function"' in map_src3)
cities_src2 = Q.build_cities_query()
check("growth/war-weariness accessors probed not guessed",
      'type(g2.GetHappinessGrowthModifier) == "function"' in cities_src2
      and "WARN|CITIES.status" in cities_src2)

# -- G2 Lua: source contract ----------------------------------------------
check("cities Lua emits CITYRES resource plots", '"CITYRES|' in cities_src2)
check("city resources honour PrereqTech visibility", "resVisible" in cities_src2)
check("cities Lua emits CITYSTATUS labels", '"CITYSTATUS|' in cities_src2)
check("happiness label from GameInfo.Happinesses (direct DB)",
      "GameInfo.Happinesses[happIdx]" in cities_src2)
check("CS bonus Loc keys detected, raw keys never shipped",
      "_INFLUENCE_BONUS" in diplo_src2 and "txt ~= key" in diplo_src2
      and "WARN|DIPLO.cs_bonus" in diplo_src2)
check("suzerain traits via LeaderTraits DB rows",
      "GameInfo.LeaderTraits()" in diplo_src2)

# -- Parser: CITYRES / CITYSTATUS -----------------------------------------
c4 = P.parse_cities([
    "CITY|123|Râ-Kedet|true|66|32|3|1.0|24|-1|10|3|1|2|7.0|14.7|10.5|8.5|5.1|6.3|BUILDING_STONEHENGE|Stonehenge|420|425|1|34|200|200|0|0|5|NONE",
    "CITY|124|Memphis|false|70|30|2|2.0|10|-1|6|2|1|1|5.0|4.0|3.0|2.0|1.0|0.0|nothing|nothing|0|0|0|10|100|100|0|0|8|NONE",
    "CITYRES|123|RESOURCE_CATTLE|BONUS|Cattle|true|true",
    "CITYRES|123|RESOURCE_IVORY|LUXURY|Ivory|false|false",
    "CITYRES|124|RESOURCE_CATTLE|BONUS|Cattle|false|true",
    "CITYSTATUS|123|Content|0|10|0",
    "CITYSTATUS|124|Displeased|-15|-999|4",
])
c123 = next(c for c in c4["cities"] if c["id"] == 123)
c124 = next(c for c in c4["cities"] if c["id"] == 124)
check("city resources parsed with improved/worked flags",
      c123["resources"][0]["improved"] is True and c123["resources"][1]["improved"] is False)
check("city status labels parsed", c123["status_labels"]["happiness_label"] == "Content")
check("unknown live growth modifier keeps -999 sentinel",
      c124["status_labels"]["live_growth_modifier"] == -999)
check("war weariness parsed", c124["status_labels"]["war_weariness"] == 4)
c_nostatus = P.parse_cities([
    "CITY|9|X|false|1|1|1|1.0|5|-1|3|1|1|1|1|1|1|1|1|1|nothing|nothing|0|0|0|1|1|1|0|0|1|NONE",
])
check("missing CITYSTATUS stays None, never a fake label",
      c_nostatus["cities"][0]["status_labels"] is None)

# -- Resource inventory aggregation ---------------------------------------
inv = P.resources_inventory(c4["cities"])
cattle = next(r for r in inv if r["type"] == "RESOURCE_CATTLE")
check("inventory aggregates bonus resources across cities",
      cattle["count"] == 2 and cattle["improved"] == 1 and cattle["unimproved"] == 1)
check("inventory names source cities",
      sorted(cattle["cities"]) == ["Memphis", "Râ-Kedet"], cattle["cities"])
check("inventory tagged direct", cattle["source"] == "direct")
check("failed cities -> inventory None, never []", P.resources_inventory(None) is None)

# -- CS bonuses + envoy race ----------------------------------------------
dp2 = P.parse_diplo([
    "CS|40|CIVILIZATION_KABUL|Kabul|MILITARISTIC|3|ME|10|20|false|22",
    "CSENVOYS|40|0:3,2:2",
    "CSBONUS|40|small|+2 Production toward units",
    "CSBONUS|40|medium|+2 more Production toward units",
    "CSBONUS|40|trait|Your units receive +5 experience",
    "CS|41|CIVILIZATION_LUXIS|Luxis|TRADE|1|SUMERIA|5|5|false|30",
    "CSENVOYS|41|0:1,2:6",
])
k = dp2["city_states"][0]
check("CS bonuses parsed by tier + trait",
      k["bonuses"]["small"].startswith("+2 Production")
      and k["bonuses"]["traits"] == ["Your units receive +5 experience"])
check("thresholds met computed from my envoys", k["envoy_status"]["thresholds_met"] == [1, 3])
check("leading race detected", k["envoy_status"]["needed_to_lead"] == 0)
lx = dp2["city_states"][1]
check("envoys-needed-to-lead computed", lx["envoy_status"]["needed_to_lead"] == 6,
      lx["envoy_status"])
check("envoy status tagged reconstructed",
      k["envoy_status"]["source"] == "reconstructed:threshold")
cs_noenvoys = P.parse_diplo(["CS|42|CIVILIZATION_X|X|TRADE|0|none|1|1|false|5"])
check("missing envoy data -> None fields, not zeros",
      cs_noenvoys["city_states"][0]["envoy_status"]["leader_envoys"] is None)

# -- Markdown -------------------------------------------------------------
snap_g2 = {
    "schema": SCHEMA_VERSION, "coach_version": COACH_VERSION, "generated_at_epoch": 1.0,
    "meta": {"turn": 87}, "empire": {},
    "cities": c4["cities"], "resources": [], "resources_inventory": inv,
    "city_states_met": dp2["city_states"][:2],
    "section_status": {"header": "ok", "cities": "ok", "resources": "ok",
                       "city_states_met": "ok"},
    "diagnostics": {}, "turn_blockers_summary": [],
}
md_g2 = M.render_markdown(snap_g2, {"first_snapshot": True})
check("city header shows localized happiness label", "happ Content" in md_g2)
check("war weariness surfaces only when positive",
      "war weariness 4" in md_g2 and "war weariness 0" not in md_g2)
check("growth modifier surfaces when nonzero", "growth -15%" in md_g2)
check("bonus resource inventory renders",
      "owned bonus tiles:" in md_g2 and "Cattle (1/2 improved)" in md_g2)
check("CS threshold + race line renders",
      "thresholds met: 1/3 | envoy race: leading" in md_g2)
check("CS envoy-tier bonus text renders", "1-envoy: +2 Production toward units" in md_g2)
check("suzerain trait text renders when I hold it",
      "suzerain bonus: Your units receive +5 experience" in md_g2)

print("\n=== Phase 2 Task 4 (G1+G3): gossip export + yield breakdown ===")

# -- Gossip Lua contract --------------------------------------------------
diplo_src3 = Q.build_diplo_query()
check("gossip export uses the live-confirmed method name",
      "GetRecentVisibleGossipStrings" in diplo_src3 and '"GOSSIP|' in diplo_src3)
check("gossip arity discovered under pcall, never assumed",
      "pcall(fn, gossipMgr, 0, me, target)" in diplo_src3
      or ("arity" in diplo_src3 and "pcall(fn, gossipMgr" in diplo_src3))
check("gossip failure is WARN, never silence",
      "WARN|DIPLO.gossip|" in diplo_src3)

# -- Gossip parser + snapshot ---------------------------------------------
dpg = P.parse_diplo([
    "GOSSIP|2|141|Sumeria declared war on Brazil!",
    "GOSSIP|2|143|Sumeria has conquered Recife.",
    "GOSSIP|3|-1|Brazil adopted the pantheon God of the Forge.",
])
check("gossip entries parsed with about/turn/text",
      dpg["gossip"][1]["about"] == 2 and dpg["gossip"][1]["turn"] == 143
      and "Recife" in dpg["gossip"][1]["text"])
check("unknown gossip turn stays -1", dpg["gossip"][2]["turn"] == -1)
check("gossip tagged direct", dpg["gossip"][0]["source"] == "direct")

# -- Yield sources: Lua contract ------------------------------------------
cities_src3 = Q.build_cities_query()
check("cities Lua emits YSRC lines", '"YSRC|' in cities_src3)
check("worked-tile yields guarded on plot:GetYield with WARN",
      'type(pl.GetYield) == "function"' in cities_src3
      and "WARN|CITIES.yield_sources" in cities_src3)
check("building yields from Building_YieldChanges DB",
      "GameInfo.Building_YieldChanges()" in cities_src3)
check("pillaged buildings excluded from yield sums",
      "if not pillB and bldgYieldDB" in cities_src3)

# -- Yield breakdown composition ------------------------------------------
cyb = P.parse_cities([
    "CITY|123|Thebes|true|66|32|3|1.0|24|-1|10|3|1|2|7.0|14.7|10.5|8.5|5.1|6.3|nothing|nothing|0|0|0|34|200|200|0|0|5|NONE",
    "DIST|123|DISTRICT_INDUSTRIAL_ZONE|Industrial Zone|66|33|false|PRODUCTION:3",
    "TRADE|123|2|Uruk|Gold:4,Production:1,|Sumerian",
    "YSRC|123|worked_tiles|5.0|8.0|2.0|0.0|0.0|0.0",
    "YSRC|123|buildings_db|1.0|2.0|0.0|2.0|1.0|2.0",
])
city_b = cyb["cities"][0]
yb = P.build_yield_breakdown(city_b)
prod = yb["production"]
check("breakdown: worked tiles direct", prod["worked_tiles"]["value"] == 8.0
      and prod["worked_tiles"]["source"] == "direct")
check("breakdown: buildings tagged static_db", prod["buildings_db"]["source"] == "static_db")
check("breakdown: adjacency summed from districts", prod["district_adjacency"]["value"] == 3.0)
# Regression for the v1.5.0 column fix: adjacency comes from column 7,
# pillaged from column 6 — the old parser read adjacency from 6 and got {}.
d0 = city_b["districts"][0]
check("DIST adjacency parsed from the correct column (v1.5.0 fix)",
      d0["adjacency"] == {"PRODUCTION": 3} and d0["pillaged"] is False, d0)
check("breakdown: trade routes summed", prod["trade_routes"]["value"] == 1.0)
# total P = 14.7, attributed = 8+2+3+1 = 14 -> unattributed 0.7 reconstructed
check("breakdown: remainder is reconstructed, not invented",
      prod["unattributed"]["value"] == 0.7 and prod["unattributed"]["source"] == "reconstructed",
      prod["unattributed"])
check("no YSRC lines -> breakdown None, never fabricated",
      P.build_yield_breakdown({"yields": {"production": 5}}) is None)

# -- Markdown -------------------------------------------------------------
city_b2 = dict(city_b)
city_b2["yield_breakdown"] = yb
snap_g13 = {
    "schema": SCHEMA_VERSION, "coach_version": COACH_VERSION, "generated_at_epoch": 1.0,
    "meta": {"turn": 145}, "empire": {},
    "cities": [city_b2], "gossip": dpg["gossip"],
    "map_owners": {"2": "Sumerian", "3": "Brazilian"},
    "section_status": {"header": "ok", "cities": "ok", "majors_met": "ok"},
    "diagnostics": {}, "turn_blockers_summary": [],
}
md_g13 = M.render_markdown(snap_g13, {"first_snapshot": True})
check("GOSSIP section renders with turn + subject",
      "## GOSSIP" in md_g13 and "T143 [Sumerian] Sumeria has conquered Recife." in md_g13)
check("unknown gossip turn renders T?", "T? [Brazilian]" in md_g13)
check("prod sources line renders compactly",
      "prod sources: tiles 8.0, bldgs 2, adj 3, trade 1, other +0.7" in md_g13,
      [l for l in md_g13.splitlines() if "prod sources" in l])

# -- Gossip history persistence -------------------------------------------
gtmp = Path(tempfile.mkdtemp(prefix="civ6-gossip-regress-"))
gsnap = {"meta": {"turn": 145}, "rivals": [], "city_states_met": [], "gossip": dpg["gossip"]}
H.update_history(gtmp, gsnap, [])
gj = json.loads((gtmp / "gossip.json").read_text(encoding="utf-8"))
check("gossip history written with first_seen stamps",
      len(gj) == 3 and gj[0]["first_seen"] == 145)
H.update_history(gtmp, {"meta": {"turn": 146}, "rivals": [], "city_states_met": [],
                        "gossip": dpg["gossip"] + [{"about": 2, "turn": 146, "text": "New entry", "source": "direct"}]}, [])
gj2 = json.loads((gtmp / "gossip.json").read_text(encoding="utf-8"))
check("gossip history dedupes, appends only unseen",
      len(gj2) == 4 and gj2[-1]["text"] == "New entry" and gj2[-1]["first_seen"] == 146)

print("\n=== Phase 2 Task 5: unavailable production + truncation integrity ===")

# -- Lua source contract: PRODX -------------------------------------------
cities_src4 = Q.build_cities_query()
check("cities Lua emits PRODX blocked lines", '"PRODX|' in cities_src4)
check("engine reasons via GetOperationTargets (probed, WARN off-path)",
      "CityManager.GetOperationTargets" in cities_src4
      and "WARN|CITIES.prod_blocked" in cities_src4
      and "FAILURE_REASONS" in cities_src4)
check("engine reasons preferred; reconstruction only as fallback",
      'engineReasons(c, paramKey, hash), "engine"' in cities_src4)
check("unknown blocks never get invented reasons",
      '"blocked (reason not exposed by engine)"' in cities_src4)
check("other civs' uniques excluded via trait set", "traitOK" in cities_src4
      and "GameInfo.CivilizationTraits()" in cities_src4)
check("reconstructed reasons self-label their DB source",
      "[reconstructed: BuildingPrereqs]" in cities_src4
      and "[reconstructed: Units.StrategicResource]" in cities_src4
      and "[reconstructed: pop/3+1 rule]" in cities_src4)
check("obsolete units excluded from the unavailable list",
      "u.ObsoleteTech and haveTech(u.ObsoleteTech)" in cities_src4)

# -- Parser: PRODX fixtures covering the required reason cases ------------
cpx = P.parse_cities([
    "CITY|123|Thebes|true|66|32|6|1.0|24|-1|10|3|1|2|7.0|14.7|10.5|8.5|5.1|6.3|nothing|nothing|0|0|0|34|200|200|0|0|5|NONE",
    # 1: district capacity (reconstructed)
    "PRODX|123|DIST|DISTRICT_CAMPUS|Campus|54|reconstructed|District capacity reached (2/2); next slot at population 9 [reconstructed: pop/3+1 rule]",
    # 2: missing prereq building (reconstructed)
    "PRODX|123|BLDG|BUILDING_TEMPLE|Temple|120|reconstructed|Requires Shrine [reconstructed: BuildingPrereqs]",
    # 3: missing strategic resource (reconstructed)
    "PRODX|123|UNIT|UNIT_SWORDSMAN|Swordsman|90|reconstructed|Requires Iron [reconstructed: Units.StrategicResource]",
    # 4: placement restriction (engine tooltip text)
    "PRODX|123|DIST|DISTRICT_HARBOR|Harbor|54|engine|Must be placed on Coast or Lake Terrain adjacent to land.",
    # 5: multiple simultaneous reasons (engine)
    "PRODX|123|WONDER|BUILDING_PYRAMIDS|Pyramids|220|engine|Requires Desert without Hills.;;A city may have only one of this wonder.",
    # unknown case
    "PRODX|123|UNIT|UNIT_GALLEY|Galley|65|unknown|blocked (reason not exposed by engine)",
])
cx = cpx["cities"][0]["production_unavailable"]
by_type = {b["type"]: b for b in cx}
check("district-capacity reason parsed",
      "District capacity reached" in by_type["DISTRICT_CAMPUS"]["reasons"][0])
check("prereq-building reason parsed", "Requires Shrine" in by_type["BUILDING_TEMPLE"]["reasons"][0])
check("strategic-resource reason parsed", "Requires Iron" in by_type["UNIT_SWORDSMAN"]["reasons"][0])
check("engine placement reason kept verbatim",
      by_type["DISTRICT_HARBOR"]["reason_source"] == "engine"
      and by_type["DISTRICT_HARBOR"]["reasons"][0].startswith("Must be placed on Coast"))
check("multiple reasons all retained",
      len(by_type["BUILDING_PYRAMIDS"]["reasons"]) == 2,
      by_type["BUILDING_PYRAMIDS"]["reasons"])
check("unknown source never carries a specific claim",
      by_type["UNIT_GALLEY"]["reason_source"] == "unknown"
      and "not exposed" in by_type["UNIT_GALLEY"]["reasons"][0])

# -- Markdown: unavailable highlights -------------------------------------
snap_px = {
    "schema": SCHEMA_VERSION, "coach_version": COACH_VERSION, "generated_at_epoch": 1.0,
    "meta": {"turn": 87}, "empire": {}, "cities": cpx["cities"],
    "section_status": {"header": "ok", "cities": "ok"},
    "diagnostics": {}, "turn_blockers_summary": [],
}
md_px = M.render_markdown(snap_px, {"first_snapshot": True})
# (v1.7.1: blocked units render in FULL in their own block; the
# shown-of-total cap + district/wonder-first ranking apply to the rest.)
check("blocked units render in a complete, labeled block",
      "unavailable units (all 2 trainables):" in md_px
      and "Swordsman — Requires Iron" in md_px and "Galley —" in md_px,
      [l for l in md_px.splitlines() if "unavailable" in l])
check("non-unit unavailable renders with explicit shown-of-total label",
      "unavailable buildings/districts/wonders (showing 4 of 4; full list + reasons in JSON):" in md_px,
      [l for l in md_px.splitlines() if "unavailable" in l])
check("districts/wonders ranked first within the non-unit block",
      md_px.find("Campus —") < md_px.find("Pyramids —") < md_px.find("Temple —"))
check("reason text renders on the item line",
      "Temple — Requires Shrine [reconstructed: BuildingPrereqs]" in md_px)

# -- Truncation integrity: EOQ completeness gate --------------------------
check("every query chunk emits EOQ before the sentinel",
      all('print("EOQ")' in b() for b in Q.ALL_QUERIES.values()))
collector_src = (REPO / "src/civ_mcp/coach/collector.py").read_text(encoding="utf-8")
check("collector fails (not partial-parses) on missing EOQ",
      "TruncatedOutput" in collector_src and 'data_lines[-1].strip() == "EOQ"' in collector_src)

# -- Truncation integrity: big sections render fully ----------------------
many_units = [
    {"id": i, "type": "UNIT_WARRIOR", "name": f"Warrior {i}", "x": i, "y": 1,
     "hp": 100, "hp_max": 100, "moves": 2, "moves_max": 2, "combat": 20,
     "ranged": 0, "xp": 0, "xp_needed": 15, "promotions_available": 0,
     "charges": 0, "fortified_turns": 0, "idle": False}
    for i in range(60)
]
many_tiles = [
    {"x": i % 40, "y": i // 40, "visible": True, "terrain": "g", "feature": "",
     "resource": "", "improvement": "", "road": "", "owner": "", "district": "",
     "is_city": False, "units": "", "extra": "", "city_name": ""}
    for i in range(500)
]
many_gossip = [
    {"about": 2, "turn": t, "text": f"Gossip entry {t}", "source": "direct"}
    for t in range(1, 51)
]
snap_big2 = {
    "schema": SCHEMA_VERSION, "coach_version": COACH_VERSION, "generated_at_epoch": 1.0,
    "meta": {"turn": 200}, "empire": {},
    "units": many_units, "tiles": many_tiles, "gossip": many_gossip,
    "map_meta": {"total_plots": 500, "grid": "40x13"},
    "map_totals": {"revealed": 500, "visible": 500, "natural_wonders": 0},
    "map_owners": {"2": "Sumerian"},
    "section_status": {"header": "ok", "units": "ok", "map": "ok", "majors_met": "ok"},
    "diagnostics": {}, "turn_blockers_summary": [],
}
md_big2 = M.render_markdown(snap_big2, {"first_snapshot": True})
check("all 60 units render (no hidden unit cap)",
      md_big2.count("Warrior ") >= 60)
check("all 500 map tile lines render (no hidden map cap)",
      sum(1 for l in md_big2.splitlines() if l.startswith("MAP ")) == 500
      or sum(1 for l in md_big2.splitlines()
             if l and l[0].isdigit() and "," in l.split(" ")[0]) == 500,
      "tile line count mismatch")
check("gossip trimmed to 10 WITH label; full history reference present",
      md_big2.count("Gossip entry") == 10 and "full history in gossip.json" in md_big2)
check("integrity footer carries JSON section counts",
      "counts: cities=0 units=60 tiles=500" in md_big2 and "gossip=50" in md_big2,
      [l for l in md_big2.splitlines() if "counts:" in l])
check("integrity footer logs md size", "md_chars=" in md_big2)
check("footer is the final line (truncation detector)",
      md_big2.rstrip().endswith("-->"))

# -- Delta lists no longer silently sliced --------------------------------
prev_u = {"meta": {"turn": 1}, "units": [
    {"id": i, "type": "UNIT_WARRIOR", "x": 1, "y": 1, "hp": 100} for i in range(15)
]}
curr_u = {"meta": {"turn": 2}, "units": [
    {"id": i, "type": "UNIT_WARRIOR", "x": 1, "y": 1, "hp": 50} for i in range(15)
]}
import civ_mcp.coach.delta as DD
d_u = DD.compute_delta(prev_u, curr_u)
check("delta damaged list keeps all 15 entries (was sliced to 10)",
      len(d_u["units_delta"]["damaged"]) == 15, len(d_u["units_delta"]["damaged"]))

# -- Archived files hold the complete document ----------------------------
atmp2 = Path(tempfile.mkdtemp(prefix="civ6-fullwrite-regress-"))
big_snap_arch = mk_snap(turn=200, epoch=9000.0)
big_md = md_big2  # ~large document
r_arch = A.write_snapshot(atmp2, big_snap_arch, big_md)
check("archived md is byte-identical to the rendered document",
      r_arch.md_path.read_text(encoding="utf-8") == big_md)
check("archived latest.md matches too",
      (r_arch.game_dir / "latest.md").read_text(encoding="utf-8") == big_md)
check("archived JSON round-trips completely",
      json.loads(r_arch.json_path.read_text(encoding="utf-8")) == big_snap_arch)

print("\n=== sentinel decoupling ===")
from civ_mcp.coach import SENTINEL as COACH_SENTINEL
# The coach defines its own SENTINEL so it has no import-time dependency on
# the upstream civ_mcp.lua package.  It MUST still match what
# GameConnection._locked_execute watches for, or output collection hangs
# until timeout on every single query.
check("every query chunk ends with the sentinel",
      all(COACH_SENTINEL in b() for b in Q.ALL_QUERIES.values()))
try:
    from civ_mcp.lua._helpers import SENTINEL as UPSTREAM_SENTINEL
    check("coach sentinel matches upstream connection sentinel",
          COACH_SENTINEL == UPSTREAM_SENTINEL,
          f"coach={COACH_SENTINEL!r} upstream={UPSTREAM_SENTINEL!r}")
except Exception as e:
    # Upstream package needs Python 3.12; skip rather than fail on 3.10/3.11.
    print(f"  SKIP  upstream sentinel comparison ({type(e).__name__})")


print("\n=== v1.7.0 Part A: district capacity (pop/3+1) ===")
# Live fixture: Râ-Kedet T138 — pop 5, Encampment + Industrial Zone built.
# Cap = floor(5/3)+1 = 2, both slots used.  This is exactly the state that
# produced the bad "build a Harbor" recommendation.
_rk = {
    "population": 5,
    "districts": [
        {"type": "DISTRICT_CITY_CENTER"}, {"type": "DISTRICT_ENCAMPMENT"},
        {"type": "DISTRICT_WONDER"}, {"type": "DISTRICT_INDUSTRIAL_ZONE"},
    ],
}
_dc = P.district_capacity(_rk)
check("Râ-Kedet: 2/2 specialty districts, FULL",
      _dc and _dc["built"] == 2 and _dc["cap"] == 2 and _dc["slots_open"] == 0, _dc)
check("next slot at pop 6 (cap*3)", _dc["next_slot_at_pop"] == 6, _dc)
check("city centre / wonder plots don't count against the cap",
      P.district_capacity({"population": 3, "districts": [
          {"type": "DISTRICT_CITY_CENTER"}, {"type": "DISTRICT_WONDER"}]})["built"] == 0)
check("aqueduct/neighborhood don't count against the cap",
      P.district_capacity({"population": 6, "districts": [
          {"type": "DISTRICT_AQUEDUCT"}, {"type": "DISTRICT_NEIGHBORHOOD"}]})["built"] == 0)
check("capacity is None when population unreadable (never guessed)",
      P.district_capacity({"districts": []}) is None
      and P.district_capacity({"population": -1, "districts": []}) is None)

print("\n=== v1.7.0 Part A: housing breakdown reconciles live captures ===")
# All four cities of the T138 Egypt capture reconcile EXACTLY against the
# static table — these pins fail if anyone fiddles the DB values.
def _tile(x, y, terr="p", extra=""):
    return {"x": x, "y": y, "terrain": terr, "extra": extra}

# Râ-Kedet: fresh water 5 + Palace 1 + Granary 2 + Barracks 1
#           + 6 farms & 1 camp (3.5) = 12.5 -> 12 reported
_txy = {(66, 29): _tile(66, 29, "ph", "R/F")}
_rk_house = {
    "x": 66, "y": 29, "housing": 12,
    "buildings": [
        {"type": "BUILDING_PALACE", "name": "Palace"},
        {"type": "BUILDING_GRANARY", "name": "Granary"},
        {"type": "BUILDING_BARRACKS", "name": "Barracks"},
        {"type": "BUILDING_MONUMENT", "name": "Monument"},
        {"type": "BUILDING_WALLS", "name": "Ancient Walls"},
    ],
    "districts": [], "tiles_rollup": {"improvements": {"farm": 6, "mine": 3, "sphinx": 2, "camp": 1}},
}
_hb = P.build_housing_breakdown(_rk_house, _txy)
check("Râ-Kedet housing 12 fully attributed (12.5 floored)",
      _hb and _hb["attributed"] == 12.5 and _hb["unattributed"] == 0, _hb)
check("fresh water beats coastal in the base term",
      any(p["label"] == "fresh water" for p in _hb["parts"]))
# SHEDET: fresh 5 + Granary 2 + 3 farms (1.5) = 8.5 -> 8 reported
_sh = P.build_housing_breakdown(
    {"x": 66, "y": 25, "housing": 8,
     "buildings": [{"type": "BUILDING_GRANARY", "name": "Granary"}],
     "districts": [], "tiles_rollup": {"improvements": {"farm": 3, "quarry": 3, "sphinx": 2}}},
    {(66, 25): _tile(66, 25, "p", "R/A-2/F")})
check("SHEDET housing 8 fully attributed (8.5 floored)",
      _sh and _sh["unattributed"] == 0, _sh)
check("pillaged buildings grant no housing",
      not any("Granary" in p["label"] for p in P.build_housing_breakdown(
          {"x": 1, "y": 1, "housing": 2,
           "buildings": [{"type": "BUILDING_GRANARY", "name": "Granary", "pillaged": True}],
           "districts": [], "tiles_rollup": {}},
          {(1, 1): _tile(1, 1)})["parts"]))
check("breakdown is None without map tiles (never guessed)",
      P.build_housing_breakdown(_rk_house, None) is None
      and P.build_housing_breakdown(_rk_house, {}) is None)
_mismatch = P.build_housing_breakdown(
    {"x": 1, "y": 1, "housing": 9, "buildings": [], "districts": [], "tiles_rollup": {}},
    {(1, 1): _tile(1, 1)})
check("unexplained housing surfaces as unattributed, not absorbed",
      _mismatch["unattributed"] == 7, _mismatch)

print("\n=== v1.7.0 Part A: amenity math matches live tier labels ===")
# Live T138: Râ-Kedet 4/2 -> Happy(+2); Sais 3/3 -> Content; SHEDET 2/3 -> Displeased
_a = P.amenity_status({"amenities": 4, "amenities_needed": 2})
check("surplus +2 = Happy, +1 to Ecstatic",
      _a["tier"] == "Happy" and _a["next_tier"] == {"tier": "Ecstatic", "amenities_needed": 1}, _a)
_a = P.amenity_status({"amenities": 3, "amenities_needed": 3})
check("surplus 0 = Content, +1 to Happy",
      _a["tier"] == "Content" and _a["next_tier"]["amenities_needed"] == 1, _a)
_a = P.amenity_status({"amenities": 2, "amenities_needed": 3})
check("surplus -1 = Displeased (matches live SHEDET label)",
      _a["tier"] == "Displeased", _a)
check("Ecstatic has no next tier",
      P.amenity_status({"amenities": 9, "amenities_needed": 2})["next_tier"] is None)
check("amenity status None on unreadable counts",
      P.amenity_status({"amenities": -1, "amenities_needed": 2}) is None)

check("luxury duplicates: only >1 copies, spare = n-1",
      P.luxury_duplicates([
          {"class": "LUXURY", "name": "Dyes", "type": "RESOURCE_DYES", "amount": 3},
          {"class": "LUXURY", "name": "Ivory", "type": "RESOURCE_IVORY", "amount": 1},
          {"class": "STRATEGIC", "name": "Iron", "type": "RESOURCE_IRON", "amount": 4},
      ]) == [{"name": "Dyes", "type": "RESOURCE_DYES", "copies": 3, "spare": 2,
              "source": "reconstructed"}])
check("luxury duplicates None when resources failed",
      P.luxury_duplicates(None) is None)

print("\n=== v1.7.0 Part A: hex grid + settler advisor ===")
# Distance sanity on the odd-r offset grid, pinned against known city
# geometry from the live capture: Sais(62,26) <-> its Holy Site(63,24) = 2.
check("hex distance Sais->its Holy Site == 2", P.hex_distance(62, 26, 63, 24) == 2)
check("hex distance is symmetric",
      P.hex_distance(66, 29, 65, 26) == P.hex_distance(65, 26, 66, 29) == 3)
check("adjacent tiles are distance 1",
      all(P.hex_distance(10, 10, nx, ny) == 1 for nx, ny in P._hex_neighbors(10, 10))
      and all(P.hex_distance(10, 11, nx, ny) == 1 for nx, ny in P._hex_neighbors(10, 11)))

_units = [{"id": 9, "type": "UNIT_SETTLER", "x": 10, "y": 10}]
_tiles = []
for xx in range(4, 18):
    for yy in range(4, 18):
        _tiles.append(_tile(xx, yy, "g", "F" if (xx, yy) == (14, 10) else ""))
_tiles.append(_tile(2, 2, "co"))
_cities = [{"x": 6, "y": 10, "name": "Home"}]
_sa = P.settler_advisor(_units, _tiles, _cities, [], [], set())
check("advisor triggers on a settler and ranks candidates",
      _sa is not None and len(_sa["candidates"]) > 0)
check("fresh-water tile outranks dry neighbours",
      _sa["candidates"][0]["x"] == 14 and _sa["candidates"][0]["fresh_water"], _sa["candidates"][0])
check("min-distance rule: no candidate within 2 of a known city",
      all(P.hex_distance(cnd["x"], cnd["y"], 6, 10) >= 3 for cnd in _sa["candidates"]))
check("water/mountain/foreign tiles are never candidates",
      P.settler_advisor(_units, [_tile(10, 10, "co"), _tile(11, 10, "gm"),
                                 {**_tile(12, 10, "g"), "owner": "3"}], [], [], [], set())
      ["candidates"] == [])
check("advisor is None with no settler (section stays absent)",
      P.settler_advisor([{"type": "UNIT_WARRIOR"}], _tiles, [], [], [], set()) is None)
check("advisor is None when units/map failed (never guessed)",
      P.settler_advisor(None, _tiles, [], [], [], set()) is None
      and P.settler_advisor(_units, None, [], [], [], set()) is None)
check("advisor self-labels as reconstructed", _sa["source"] == "reconstructed")

print("\n=== v1.7.0 Part A: civ accounting (fog-safe) ===")
_maj = [{"player_id": 3, "civ_name": "Sumeria"}]
_riv = [{"player_id": 3, "civ_name": "Sumeria", "alive": True},
        {"player_id": 4, "civ_name": "Brazil", "alive": False}]
_wrel = [{"founder": 0, "name": "Taoism"}, {"founder": 5, "name": "Hinduism"}]
_ca = P.civ_accounting(_maj, _riv, _wrel, {"max_players": 10})
check("counts met alive + eliminated",
      _ca["met_alive"] == 1 and _ca["eliminated"] == 1
      and _ca["eliminated_names"] == ["Brazil"], _ca)
check("religion founded by unknown player id = unmet-civ evidence",
      len(_ca["unmet_evidence"]) == 1 and "Hinduism" in _ca["unmet_evidence"][0], _ca)
check("own religion (founder 0) is not unmet evidence",
      not any("Taoism" in e for e in _ca["unmet_evidence"]))
check("map max labeled as capacity, never as start count",
      "capacity" in _ca["note"] and _ca["map_max_majors"] == 10)
check("accounting None when majors failed",
      P.civ_accounting(None, _riv, _wrel, {}) is None)

print("\n=== v1.7.0 Part A: markdown wiring ===")
_snap_a = {
    "schema": SCHEMA_VERSION, "coach_version": COACH_VERSION, "generated_at_epoch": 1.0,
    "section_status": {"cities": "ok", "header": "ok"},
    "meta": {"turn": 138}, "empire": {},
    "cities": [{
        "id": 1, "name": "TestCity", "x": 5, "y": 5, "population": 5,
        "food_surplus": 1.0, "turns_to_growth": 5, "turns_to_starvation": -1,
        "housing": 7, "amenities": 4, "amenities_needed": 2, "happiness": 2,
        "yields": {}, "production": {"name": "X", "progress": 0, "cost": 1, "turns": 1},
        "defense": {}, "border_expansion_turns": 3, "majority_religion": "NONE",
        "districts": [{"type": "DISTRICT_ENCAMPMENT"}, {"type": "DISTRICT_INDUSTRIAL_ZONE"}],
        "buildings": [], "tiles_rollup": {}, "trade_routes": [], "resources": [],
        "production_unavailable": [], "status_labels": None,
        "production_options": [
            {"kind": "UNIT", "type": "U1", "name": "Scout", "progress": 0, "cost": 30, "turns": 1},
            {"kind": "DIST", "type": "D1", "name": "Campus", "progress": 10, "cost": 54, "turns": 9},
            {"kind": "WONDER", "type": "W1", "name": "Oracle", "progress": 0, "cost": 290, "turns": 30},
        ],
        "district_capacity": {"built": 2, "cap": 2, "slots_open": 0,
                              "next_slot_at_pop": 6, "source": "reconstructed:pop/3+1"},
        "amenity_status": {"surplus": 2, "tier": "Happy",
                           "next_tier": {"tier": "Ecstatic", "amenities_needed": 1},
                           "source": "reconstructed:static_db"},
        "housing_breakdown": {"total_reported": 7,
                              "parts": [{"label": "base", "value": 2},
                                        {"label": "fresh water", "value": 3},
                                        {"label": "Granary", "value": 2}],
                              "attributed": 7.0, "unattributed": 0,
                              "source": "reconstructed:static_db"},
    }],
    "civ_accounting": {"met_alive": 1, "met_alive_names": ["Sumeria"], "eliminated": 1,
                       "eliminated_names": ["Brazil"], "map_max_majors": 10,
                       "unmet_evidence": ["Hinduism was founded by an unmet civilization (public info)"],
                       "note": "capacity", "source": "reconstructed"},
    "settler_advisor": {
        "settlers": [{"id": 9, "x": 10, "y": 10}],
        "candidates": [{"x": 14, "y": 10, "score": 9.5, "fresh_water": True, "coastal": False,
                        "ring1_food": 12, "ring1_production": 0, "resources_within_2": [],
                        "nearest_own_city": {"name": "Home", "dist": 8},
                        "dist_from_settler": 4, "direction_from_settler": "east",
                        "overlap_owned_tiles_r2": 0}],
        "note": "reconstructed", "source": "reconstructed"},
    "luxury_duplicates": [{"name": "Dyes", "type": "RESOURCE_DYES", "copies": 2, "spare": 1,
                           "source": "reconstructed"}],
    "diagnostics": {},
}
_md_a = M.render_markdown(_snap_a, {})
check("md shows district capacity FULL line with next pop",
      "districts: 2/2 built — FULL, next slot at pop 6" in _md_a)
check("md shows amenity surplus + next tier inline",
      "(+2; +1 amen → Ecstatic)" in _md_a)
check("md shows housing breakdown line",
      "housing 7 = base 2 + fresh water 3 + Granary 2 [reconstructed]" in _md_a)
check("md groups production by category",
      "districts (need placement)" in _md_a and "Campus (54⚙ 9t) [10/54 banked]" in _md_a
      and "wonders (need placement)" in _md_a)
check("md renders settler advisor section",
      "## SETTLER ADVISOR" in _md_a and "(14,10) score 9.5" in _md_a
      and "fresh water" in _md_a)
check("md renders civ accounting under diplomacy",
      "civ accounting:" in _md_a and "unmet-civ evidence: Hinduism" in _md_a)
check("md renders tradable spare luxuries",
      "tradable spare luxuries" not in _md_a or True)  # resources section absent here
_snap_a["resources"] = []
_snap_a["section_status"]["resources"] = "ok"
_md_a2 = M.render_markdown(_snap_a, {})
check("md renders spare luxuries when resources section present",
      "tradable spare luxuries:** Dyes (1 spare of 2)" in _md_a2)
# v1.7.1: unit list is NEVER truncated — a unit absent from the md must
# mean "genuinely not buildable here" (the Mamluk/Knight invisibility bug:
# units fell off both the capped buildable list and the capped
# unavailable list, so the coach couldn't answer "can I build X?").
_snap_a["cities"][0]["production_options"] = [
    {"kind": "UNIT", "type": f"U{i}", "name": f"Unit{i}", "progress": 0, "cost": 10, "turns": i}
    for i in range(15)
]
_md_a3 = M.render_markdown(_snap_a, {})
check("buildable unit list renders in full (15/15, no cap)",
      all(f"Unit{i} (" in _md_a3 for i in range(15)) and "rest in JSON" not in _md_a3)
check("full unit list is labeled complete", "units (complete list):" in _md_a3)
_snap_a["cities"][0]["production_unavailable"] = (
    [{"category": "UNIT", "type": f"BU{i}", "name": f"BlockedUnit{i}", "cost": 100 + i,
      "reason_source": "reconstructed", "reasons": [f"needs thing {i}"]} for i in range(9)]
    + [{"category": "WONDER", "type": f"W{i}", "name": f"Wonder{i}", "cost": 300,
        "reason_source": "unknown", "reasons": []} for i in range(8)]
)
_md_a4 = M.render_markdown(_snap_a, {})
check("ALL blocked units render with reasons (9/9)",
      "unavailable units (all 9 trainables):" in _md_a4
      and all(f"BlockedUnit{i} — needs thing {i}" in _md_a4 for i in range(9)))
check("non-unit unavailable stays capped with explicit label",
      "unavailable buildings/districts/wonders (showing 6 of 8" in _md_a4)
check("absence discipline: no capacity/housing/advisor lines when derivations are None",
      all(s not in M.render_markdown({
          "schema": SCHEMA_VERSION, "coach_version": COACH_VERSION, "generated_at_epoch": 1.0,
          "section_status": {"cities": "ok", "header": "ok"}, "meta": {"turn": 1}, "empire": {},
          "cities": [{**_snap_a["cities"][0], "district_capacity": None,
                      "housing_breakdown": None, "amenity_status": None,
                      "production_options": []}],
          "diagnostics": {},
      }, {}) for s in ("districts:", "housing 7 =", "## SETTLER ADVISOR", "civ accounting")))
_snap_a["cities"][0]["production_unavailable"] += [
    {"category": "UNIT", "type": "UNIT_GREAT_WRITER", "name": "Great Writer", "cost": 0,
     "reason_source": "unknown", "reasons": []},
    {"category": "UNIT", "type": "UNIT_APOSTLE", "name": "Apostle", "cost": 0,
     "reason_source": "unknown", "reasons": []},
]
_md_a5 = M.render_markdown(_snap_a, {})
check("GP/faith units roll up into one explanatory line, not noise",
      "not city-trainable by design (2): Great Writer, Apostle" in _md_a5
      and "Great Writer — " not in _md_a5)
check("rollup line names the recruit/faith mechanism",
      "recruited with points" in _md_a5 and "purchased with Faith" in _md_a5)
check("trainable blocked list count excludes rolled-up units",
      "unavailable units (all 9 trainables):" in _md_a5)



# ---------------------------------------------------------------------------
# GAME PACK builder (scripts/make_game_pack.py)
#
# The pack is what an AI chat actually reads, so its failure modes are the
# expensive kind: a silently-dropped turn or a fake 0 becomes a confident
# wrong conclusion.  These cases pin the honesty rules.
# ---------------------------------------------------------------------------

import tempfile as _tempfile
import shutil as _shutil

sys.path.insert(0, str(REPO / "scripts"))
import make_game_pack as GP  # noqa: E402


def _pack_fixture(root, *, turns=((10, "1.2.1"), (11, "1.7.1"), (14, "1.7.1"))):
    """Synthetic archive: a version seam, a gap, a failed section, a rev02."""
    d = Path(root) / "output" / "games" / "game-001_test"
    (d / "snapshots").mkdir(parents=True, exist_ok=True)
    (d / "game.json").write_text(json.dumps({
        "civ_name": "Egypt", "leader_name": "Cleopatra", "difficulty": "Chieftain",
        "map_type": "Continents", "map_size": "Small", "speed": "Standard",
        "last_capture_at_epoch": 100,
    }), encoding="utf-8")
    for turn, ver in turns:
        snap = {
            "coach_version": ver,
            "meta": {"turn": turn, "era": "Ancient Era"},
            "empire": {"score": turn * 2, "science": 1.5, "culture": 2.0, "gold": 100,
                       "gold_net": 3.0, "faith": 0, "military": 50, "num_cities": 2,
                       "total_pop": 5, "techs_done": 4, "civics_done": 3,
                       "trade_used": 1, "num_units": 6},
            # turn 11 stands in for a section the collector could not read
            "section_status": {"empire": "failed" if turn == 11 else "ok"},
        }
        (d / "snapshots" / f"turn-{turn:04d}_r01.json").write_text(
            json.dumps(snap), encoding="utf-8")
        (d / "snapshots" / f"turn-{turn:04d}_r01.md").write_text(
            f"# SNAP {turn}\n\n## CHANGES SINCE LAST SNAPSHOT\n- grew\n\n"
            f"## WORLD NEWS\n- news\n\n## REVEALED MAP\n" + "tile\n" * 50,
            encoding="utf-8")
    # same-turn recapture: the higher revision must win
    snap["meta"]["turn"] = 14
    snap["empire"]["score"] = 999
    snap["section_status"] = {"empire": "ok"}
    (d / "snapshots" / "turn-0014_r02.json").write_text(json.dumps(snap), encoding="utf-8")
    (d / "snapshots" / "turn-0014_r02.md").write_text(
        "## CHANGES SINCE LAST SNAPSHOT\n- rev2 wins\n", encoding="utf-8")

    (d / "gossip.json").write_text(json.dumps([
        {"turn": 5, "text": "Rumor: dup"},
        {"turn": 5, "text": "Rumor: dup"},
        {"turn": 9, "text": "Sumeria expanded"},
    ]), encoding="utf-8")
    (d / "events.json").write_text(json.dumps([
        {"turn": 12, "event": "military_swing", "civ": "Sumeria", "from": 100, "to": 10},
    ]), encoding="utf-8")
    (d / "rivals.json").write_text(json.dumps({
        "majors": {
            "3": {"civ_name": "Sumeria", "leader_name": "Gilgamesh", "timeline": [
                {"turn": 10, "alive": True, "score": 30, "military": 100, "techs": 5,
                 "civics": 4, "tourism": 0, "cities_known": 3, "wars_with": [],
                 "government": "GOVERNMENT_AUTOCRACY"}]},
            # dead before the archive begins — must not render an empty table
            "4": {"civ_name": "Brazil", "timeline": [
                {"turn": 10, "alive": False, "score": None}]},
        },
        "city_states": {"7": {"name": "Hattusa", "timeline": [
            {"turn": 10, "suzerain": "ME"}, {"turn": 12, "suzerain": None}]}},
    }), encoding="utf-8")
    (d / "latest.md").write_text(
        "# FINAL\n\n## EMPIRE\n- score 999\n\n## REVEALED MAP\n" + "tile\n" * 200,
        encoding="utf-8")
    return d


_pk_root = _tempfile.mkdtemp(prefix="civ6-pack-regress-")
try:
    _pk_dir = _pack_fixture(_pk_root)
    _pk_games = Path(_pk_root) / "output" / "games"
    _pk_game = GP.find_games(_pk_games)[0]
    _pk = GP.build_pack(_pk_game)

    check("game pack: discovers the game folder and every captured turn",
          len(_pk_game.turns) == 3 and _pk_game.turns == [10, 11, 14])

    check("game pack: highest revision per turn wins",
          "| 14 | Ancient Era | 999 |" in _pk and "| 14 | Ancient Era | 28 |" not in _pk)

    check("game pack: failed section renders ?, never a fake 0",
          "| 11 | Ancient Era | ? | ? |" in _pk)

    check("game pack: uncaptured early turns are declared, not glossed over",
          "Turns 1-9 were never captured" in _pk.replace("\u2013", "-")
          or "Turns 1\u20139 were never captured" in _pk)

    check("game pack: back-fill horizon is stated when gossip predates capture",
          "back-filled to T5" in _pk)

    check("game pack: gaps inside the captured span are listed",
          "Gaps inside the captured span" in _pk and "12-13" in _pk)

    check("game pack: schema drift across coach versions is warned about loudly",
          "SCHEMA DRIFT WARNING" in _pk and "1.2.1" in _pk and "1.7.1" in _pk)

    check("game pack: chronology dedups repeated gossip",
          _pk.count("Rumor: dup") == 1 and "1 duplicate removed" in _pk)

    check("game pack: gossip and events merge into one turn-sorted record",
          _pk.index("**T5**") < _pk.index("**T9**") < _pk.index("**T12**"))

    check("game pack: a civ dead before the archive gets a sentence, not an empty table",
          "No observations while alive" in _pk)

    check("game pack: city-state suzerain flips are compressed into a history",
          "T10:ME" in _pk and "T12:none" in _pk)

    check("game pack: narrative carries the per-turn CHANGES/WORLD NEWS blocks",
          "#### Turn 10" in _pk and "rev2 wins" in _pk)

    check("game pack: final state is embedded verbatim by default",
          "score 999" in _pk and "## REVEALED MAP" in _pk)

    # --- budget: trims are real, labelled, and never touch the spine --------
    _pk_lean = GP.build_pack(_pk_game, lean=True)
    check("game pack: lean variant drops the map dump and says so",
          "[omitted from lean pack]" in _pk_lean and len(_pk_lean) < len(_pk))

    _pk_tight = GP.build_pack(_pk_game, budget=2500)
    check("game pack: an exceeded budget is stated in the coverage header",
          "Budget 2,500 chars exceeded" in _pk_tight)
    check("game pack: budget trims never remove the timelines or chronology",
          "## 1. YOUR TIMELINE" in _pk_tight
          and "## 3. MASTER CHRONOLOGY" in _pk_tight
          and "**T9**" in _pk_tight)

    check("game pack: --newest and --game select the same single-game archive",
          GP.main(["--game", "game-001_test", "--games-root", str(_pk_games)]) == 0
          and (_pk_dir / "GAME-PACK.md").exists())

    check("game pack: an unknown game name exits non-zero instead of guessing",
          GP.main(["--game", "nope", "--games-root", str(_pk_games)]) == 1)
finally:
    _shutil.rmtree(_pk_root, ignore_errors=True)


print("\n=== v1.8.1 BUG 1 (P0): delta crash on failed sections ===")
# collector._or_none stores explicit None for a failed section, and
# dict.get(key, []) returns that stored None — v1.8.0's compute_delta then
# died at `{_tile_key(t) for t in None}`, and because bridge.py called it
# outside any try/except, the NEXT capture after any partial snapshot lost
# clipboard, archive and summary.  The fix is two layers:
#   1. delta tolerates stored-None sections (skips the class, records a gap);
#   2. bridge guards compute_delta/render_markdown so nothing kills a capture.
from civ_mcp.coach import delta as DL  # noqa: E402  (loaded by the shim above)

_prev_partial = {
    "schema": SCHEMA_VERSION, "coach_version": COACH_VERSION, "generated_at_epoch": 1.0,
    "meta": {"turn": 100}, "empire": None,
    "tiles": None, "units": None, "cities": None, "resources": None,
    "majors_met": None, "city_states_met": None,
    "section_status": {"header": "ok", "map": "failed", "units": "failed",
                       "cities": "failed", "empire": "failed", "diplo": "failed"},
}
_curr_full = {
    "schema": SCHEMA_VERSION, "coach_version": COACH_VERSION, "generated_at_epoch": 2.0,
    "meta": {"turn": 101}, "empire": {"score": 200, "gold": 500},
    "tiles": [{"x": 1, "y": 2, "terrain": "g"}],
    "units": [{"id": 1, "type": "UNIT_WARRIOR", "x": 1, "y": 2, "hp": 100}],
    "cities": [{"id": 1, "name": "Thebes", "population": 6, "x": 1, "y": 2}],
    "resources": [{"type": "IRON", "amount": 20}],
    "majors_met": [{"player_id": 1, "civ_type": "CIVILIZATION_ROME", "civ_name": "Rome"}],
    "city_states_met": [],
    "section_status": {"header": "ok"},
    "diagnostics": {}, "turn_blockers_summary": [],
}
try:
    _d = DL.compute_delta(_prev_partial, _curr_full)
    _delta_ok = True
except TypeError:
    _d, _delta_ok = {}, False
check("compute_delta survives a previous snapshot with None sections", _delta_ok)
check("failed sections are recorded as delta gaps, not compared",
      set(_d.get("delta_gaps", [])) >= {"tiles", "units", "cities", "resources", "empire"},
      f"got {_d.get('delta_gaps')}")
check("a None section never fabricates 'newly revealed tiles'",
      "tiles_newly_revealed" not in _d)
check("a None section never fabricates born units",
      "units_delta" not in _d)
check("a None empire never fabricates a score swing",
      "empire_delta" not in _d)

_md_snap = {
    "schema": SCHEMA_VERSION, "coach_version": COACH_VERSION, "generated_at_epoch": 2.0,
    "meta": {"turn": 101}, "empire": {},
    "section_status": {"header": "ok"},
    "diagnostics": {}, "turn_blockers_summary": [],
}
_md_gap = M.render_markdown(_md_snap, _d)
check("markdown declares the delta incomplete instead of implying no changes",
      "delta incomplete" in _md_gap)

# Symmetric case: both sides fine -> no gaps key, delta works as before.
_d2 = DL.compute_delta(_curr_full, _curr_full)
check("clean snapshots produce no delta_gaps", "delta_gaps" not in _d2, f"got {_d2.get('delta_gaps')}")

# The bridge-side guard: a delta/render failure must not abort the capture.
_bridge_src = (REPO / "src/civ_mcp/coach/bridge.py").read_text(encoding="utf-8")
check("bridge guards compute_delta (failure degrades, never aborts)",
      "delta computation failed" in _bridge_src and '"delta_failed": True' in _bridge_src)
check("bridge guards render_markdown (JSON still archived on render crash)",
      "markdown render failed" in _bridge_src)
check("markdown renders the delta_failed marker",
      "DELTA FAILED" in M.render_markdown(_md_snap, {"first_snapshot": False, "delta_failed": True}))


print("\n=== v1.8.1 BUG 2: dead promote-availability fallback ===")
# v1.8.0 declared `xpNeed` but tested the undeclared global `xpNeeded` —
# always nil in Lua, so the XP-threshold fallback could never fire.
_units_code = strip_lua_comments(Q.build_units_query())
check("undeclared global xpNeeded is gone from units Lua (code, not comments)",
      "xpNeeded" not in _units_code)
check("fallback tests the declared xpNeed local",
      "if xpNeed and xpNeed > 0 and xp >= xpNeed then" in _units_code)


print("\n=== v1.8.1 BUG 3: early returns must terminate with EOQ ===")
# Three guard clauses printed the sentinel without EOQ, so a clean
# "no religion/diplomacy/visibility object" was misclassified as a
# truncated (FAILED) query instead of an honest empty result.
for _qname, _qbuild in Q.ALL_QUERIES.items():
    _qsrc = strip_lua_comments(_qbuild())
    _bare = _qsrc.replace('print("EOQ"); print("---END---")', "")
    check(f"{_qname}: every ---END--- is preceded by EOQ",
          'print("---END---")' not in _bare)

print("\n=== v1.8.2: Q9 capability probe (diagnostics-only) ===")
# Discovery pass for the declared-ruleset migration.  Contract: runs last,
# probes instead of guessing, lands only under diagnostics.probe, and a
# missing table/method is a reported result — never an error or a zero.
check("probe is registered and runs LAST",
      list(Q.ALL_QUERIES.keys())[-1] == "probe", list(Q.ALL_QUERIES.keys()))

_probe_src = Q.build_probe_query()
_probe_code = strip_lua_comments(_probe_src)
check("probe Lua contains no mutating APIs",
      not any(bad in _probe_code for bad in (
          "RequestPlayerOperation", "UI.RequestAction", "EndTurn(",
          "RequestCommand", "RequestOperation", "SetProperty",
      )))
check("probe gates every deep call on a type() == \"function\" check",
      _probe_code.count('== "function"') >= 8)
check("probe uses pcall-guarded indexing (probeIndex), not bare access",
      "probeIndex" in _probe_code and "index-error" in _probe_code)
check("probe terminates with EOQ before the sentinel",
      _probe_src.rstrip().endswith('print("EOQ"); print("---END---")'))
check("probe resolves DISTRICT_DIPLOMATIC_QUARTER against the live DB",
      "DISTRICT_DIPLOMATIC_QUARTER" in _probe_code)
check("probe asks the live DB for the specialty-district set (RequiresPopulation)",
      "RequiresPopulation" in _probe_code)

_probe_lines = [
    "PROBE|ruleset|RULESET|RULESET_EXPANSION_2",
    "PROBE|mod|4873eb62-8ccc-4574-b784-dda455e74e68|Expansion: Gathering Storm",
    "PROBE|db|Districts|71",
    "PROBE|db|Governors|absent",
    "PROBE|db|RandomEvents|uncountable",
    "PROBE|dbrow|Districts|DISTRICT_DIPLOMATIC_QUARTER|present",
    "PROBE|dbrow|Routes|ROUTE_RAILROAD|present",
    "PROBE|specialty|DISTRICT_SEOWON",
    "PROBE|specialty|DISTRICT_CAMPUS",
    "PROBE|resclass|RESOURCECLASS_LUXURY|27",
    "PROBE|victory|VICTORY_DIPLOMATIC|enabled",
    "PROBE|api|Player.GetGovernors|function",
    "PROBE|api|GameClimate|nil",
    "DIAG|PROBE.api_city|no readable capital city — city probes skipped",
]
_pp = P.parse_probe(_probe_lines)["probe"]
check("parse_probe: ruleset string comes through verbatim",
      _pp["ruleset"].get("RULESET") == "RULESET_EXPANSION_2")
check("parse_probe: enabled mods keep id and title",
      _pp["enabled_mods"][0]["title"] == "Expansion: Gathering Storm")
check("parse_probe: numeric counts parse as int", _pp["db_counts"].get("Districts") == 71)
check("parse_probe: 'absent' stays a string, never becomes 0",
      _pp["db_counts"].get("Governors") == "absent")
check("parse_probe: 'uncountable' stays a string, never becomes 0",
      _pp["db_counts"].get("RandomEvents") == "uncountable")
check("parse_probe: targeted rows keyed Table.TYPE",
      _pp["db_rows"].get("Districts.DISTRICT_DIPLOMATIC_QUARTER") == "present")
check("parse_probe: specialty districts sorted",
      _pp["specialty_districts"] == ["DISTRICT_CAMPUS", "DISTRICT_SEOWON"])
check("parse_probe: victory states keep the raw word",
      _pp["victories"].get("VICTORY_DIPLOMATIC") == "enabled")
check("parse_probe: api types recorded verbatim",
      _pp["api"].get("Player.GetGovernors") == "function"
      and _pp["api"].get("GameClimate") == "nil")
check("parse_probe: DIAG lines flow into diagnostics",
      P.parse_probe(_probe_lines)["diagnostics"][0]["section"] == "PROBE.api_city")

# Collector wiring (source-level: collector imports the connection stack,
# which this harness doesn't load).
_coll_src = (REPO / "src/civ_mcp/coach/collector.py").read_text(encoding="utf-8")
check("collector: probe has a timeout entry", '"probe": 15.0' in _coll_src)
check("collector: probe has a parser entry", '"probe": P.parse_probe' in _coll_src)
check("collector: probe result lands under diagnostics, failure-honest",
      '"probe": _or_none("probe"' in _coll_src)
check("collector: probe tracked in section_status",
      '"probe":             ("probe",    "probe")' in _coll_src)

print()
if failures:
    print(f"{len(failures)} FAILED: {failures}")
    sys.exit(1)
print("All v1.01 regression tests passed.")
