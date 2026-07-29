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

for mod in ['__init__', 'queries', 'parser', 'delta', 'markdown', 'archive']:
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
check("schema bumped to 1.2", SCHEMA_VERSION == "coach-snapshot/1.2", SCHEMA_VERSION)
check("coach version 1.1.0 (semver)", COACH_VERSION == "1.1.0", COACH_VERSION)

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
