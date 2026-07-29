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
check("coach version 1.4.0 (semver)", COACH_VERSION == "1.4.0", COACH_VERSION)

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


print()
if failures:
    print(f"{len(failures)} FAILED: {failures}")
    sys.exit(1)
print("All v1.01 regression tests passed.")
