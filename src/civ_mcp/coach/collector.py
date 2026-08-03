"""Snapshot orchestrator — runs every query and merges the fragments.

Uses ``civ_mcp.connection.GameConnection`` (which already discovers the
GameCore_Tuner and InGame Lua-state indexes by name — no ``use 5``).  All
coach queries are read-only.  We route every query to the **InGame** state
because it's a superset of GameCore for reads and exposes the UI helpers
(``Calendar``, ``NotificationManager``, ``EndTurnBlockingTypes``,
``UnitCommandTypes``) that some sections need.  This is a read-only use
of InGame — no ``UI.RequestAction`` / ``RequestPlayerOperation`` /
``EndTurn`` anywhere.

The returned snapshot dict follows the schema in
``docs/coach-snapshot-schema.md`` and adds a ``section_status`` field so
downstream renderers can tell "query failed" apart from "nothing to show".
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from civ_mcp.connection import GameConnection, LuaError
from civ_mcp.coach import COACH_VERSION, SCHEMA_VERSION
from civ_mcp.coach import parser as P
from civ_mcp.coach import queries as Q

log = logging.getLogger(__name__)


# Per-query timeout — cities and map are the heaviest.
QUERY_TIMEOUT = {
    "meta": 10.0,
    "choices": 20.0,
    "cities": 30.0,
    "units": 15.0,
    "map": 45.0,
    "diplo": 12.0,
    "religion": 10.0,
    "notif": 8.0,
    "xpac": 12.0,  # Q9 expansion mechanics (R&F batch)
    "ruleset": 15.0,  # Q10 declared ruleset — live DB tables
    "probe": 15.0,  # Q11 capability probe — diagnostics only, runs last
}


PARSERS = {
    "meta": P.parse_meta,
    "choices": P.parse_choices,
    "cities": P.parse_cities,
    "units": P.parse_units,
    "map": P.parse_map,
    "diplo": P.parse_diplo,
    "religion": P.parse_religion,
    "notif": P.parse_notifications,
    "xpac": P.parse_xpac,
    "ruleset": P.parse_ruleset,
    "probe": P.parse_probe,
}


# Every coach query runs read-only in the InGame state.  See module docstring.
def _exec(conn: GameConnection, name: str, code: str, timeout: float):
    # ``execute_write`` is a misnomer inherited from the base repo — it just
    # means "run in the InGame Lua state".  We never emit mutating APIs.
    return conn.execute_write(code, timeout=timeout)


# Sections the snapshot exposes, mapped to the fragment key + subkey we
# expect to see populated when the query succeeds.  Used to build
# section_status without every parser having to declare its own contract.
SECTION_EXPECTATIONS = {
    "header":            ("meta",     "meta"),
    "victories":         ("meta",     "victories_enabled"),
    "empire":            ("meta",     "empire"),
    "current_research":  ("meta",     "current.tech"),
    "current_civic":     ("meta",     "current.civic"),
    "resources":         ("meta",     "resources"),
    "government":        ("meta",     "government"),
    "policy_slots":      ("meta",     "policy_slots"),
    "policy_available":  ("meta",     "policy_available"),
    "great_people":      ("meta",     "great_people"),
    "techs_available":   ("choices",  "techs_available"),
    "civics_available":  ("choices",  "civics_available"),
    "tech_tree":         ("choices",  "tech_tree"),
    "civic_tree":        ("choices",  "civic_tree"),
    "cities":            ("cities",   "cities"),
    "units":             ("units",    "units"),
    "map":               ("map",      "tiles"),
    "envoys":            ("diplo",    "envoys"),
    "majors_met":        ("diplo",    "majors"),
    "city_states_met":   ("diplo",    "city_states"),
    "religion":          ("religion", "pantheon"),
    "notifications":     ("notif",    "notifications"),
    "ruleset":           ("ruleset",  "ruleset"),
    "probe":             ("probe",    "probe"),
    "era":               ("xpac",     "era"),
    "governors":         ("xpac",     "governors"),
    "emergencies":       ("xpac",     "emergencies"),
}


def _dig(d: dict, path: str):
    cur = d
    for part in path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
        if cur is None:
            return None
    return cur


async def _run_one(
    conn: GameConnection, name: str
) -> tuple[str, dict[str, Any] | None, list[str], list[str], str | None]:
    """Run one query.

    Returns (name, parsed-or-None, trace-lines, warn-lines, exec-error-or-None).
    """
    build = Q.ALL_QUERIES[name]
    timeout = QUERY_TIMEOUT.get(name, 15.0)
    code = build()
    try:
        raw_lines = await _exec(conn, name, code, timeout)
    except LuaError as e:
        return name, None, [], [], f"LuaError [ingame]: {e}"
    except (ConnectionError, asyncio.TimeoutError, OSError) as e:
        return name, None, [], [], f"{type(e).__name__} [ingame]: {e}"

    # Split TRACE and WARN lines out before parsing — parsers only see data.
    # WARN = compatibility notes (fallback paths taken, cosmetic lookups
    # unresolved); they must NOT appear as runtime failures.
    trace_lines: list[str] = []
    warn_lines: list[str] = []
    data_lines: list[str] = []
    for line in raw_lines:
        if line.startswith("TRACE|"):
            trace_lines.append(line)
        elif line.startswith("WARN|"):
            warn_lines.append(line)
        else:
            data_lines.append(line)

    # Completeness gate: every coach query prints EOQ immediately before
    # the sentinel.  The connection layer returns partial output silently
    # when a query times out mid-stream — without this check a truncated
    # CITIES stream would parse as "fewer cities", which is a lie.
    if data_lines and data_lines[-1].strip() == "EOQ":
        data_lines = data_lines[:-1]
    else:
        return (
            name, None, trace_lines, warn_lines,
            "TruncatedOutput: EOQ end-marker missing — output cut off "
            "(likely a mid-stream timeout); section marked failed, not partial",
        )

    # Wire-format arity guard: an inserted/reordered column in a known tag
    # would otherwise mis-parse silently (indexed reads).  Surfaced via the
    # WARN channel so it lands in compat_notes, loudly.
    for w in P.arity_warnings(data_lines):
        warn_lines.append(f"WARN|{name}.arity|{w}")

    parser = PARSERS[name]
    try:
        parsed = parser(data_lines)
    except Exception as e:  # noqa: BLE001 — parsers must never take down the bridge
        log.exception("Parser failed for %s", name)
        return name, None, trace_lines, warn_lines, f"ParserError: {e}"
    return name, parsed, trace_lines, warn_lines, None


def _classify_sections(fragments: dict[str, dict[str, Any]], exec_errors: dict[str, str]) -> dict[str, str]:
    """Build ``section_status[section] = ok|failed|missing``.

    - ``failed``  — query threw at execute time OR a DIAG entry names the section.
    - ``missing`` — query ran but the expected data key is empty.
    - ``ok``      — data is present.
    """
    # Collect all DIAG-reported subsections keyed by their prefix.
    diag_prefixes: dict[str, list[str]] = {}
    for qname, frag in fragments.items():
        for d in (frag or {}).get("diagnostics", []) or []:
            sec = d.get("section", "")
            diag_prefixes.setdefault(sec, []).append(d.get("message", ""))

    status: dict[str, str] = {}
    for section, (qname, keypath) in SECTION_EXPECTATIONS.items():
        if qname in exec_errors:
            status[section] = "failed"
            continue
        frag = fragments.get(qname) or {}
        val = _dig(frag, keypath)
        has_data = bool(val) if not isinstance(val, dict) else bool(val)
        # If a DIAG matched this section name (e.g. "META.header" or "CITIES"
        # or "REL.pantheon"), and there's no data, mark failed.  Otherwise
        # missing.
        expected_diag = section.upper().replace("_", "")
        matched = any(
            d.upper().replace("_", "").startswith(expected_diag)
            or expected_diag in d.upper().replace("_", "")
            for d in diag_prefixes.keys()
        )
        if has_data:
            status[section] = "ok"
        elif matched or qname in exec_errors:
            status[section] = "failed"
        else:
            status[section] = "missing"
    return status


# Expansion mechanics the coach knows about: (label, probe API key that
# proves existence, extracted-yet flag).  diagnostics.unsupported is
# DERIVED from the capture's own probe results — never asserted statically.
# Flip a mechanic's flag to True in the same commit that ships its
# extraction, or the capability report contradicts the snapshot.
_MECHANIC_PROBES: list[tuple[str, str, bool]] = [
    # R&F batch — extracted since v1.10.0 (Q9 xpac query)
    ("governors (Rise & Fall)", "Player.GetGovernors", True),
    ("loyalty (Rise & Fall)", "City.GetCulturalIdentity", True),
    ("era score, Golden/Dark Ages (Rise & Fall)", "Eras.GetPlayerCurrentScore", True),
    ("alliance levels (Rise & Fall)", "Diplomacy.GetAllianceLevel", True),
    ("emergencies (Rise & Fall)", "EmergencyManager.GetEmergencyInfoTable", True),
    # GS batch — planned (Phase D2)
    ("diplomatic favor (Gathering Storm)", "Player.GetFavor", False),
    ("Diplomatic Victory points (Gathering Storm)", "PlayerStats.GetDiplomaticVictoryPoints", False),
    ("World Congress (Gathering Storm)", "WorldCongress.IsInSession", False),
    ("climate / CO2 (Gathering Storm)", "GameClimate.GetTotalCO2Footprint", False),
    ("city power (Gathering Storm)", "CityPower.IsFullyPowered", False),
    ("strategic resource stockpiles (Gathering Storm)", "Resources.GetResourceStockpileCap", False),
]


def _derive_unsupported(probe: dict[str, Any] | None) -> list[str]:
    """Capability status per known expansion mechanic, from live probe data.

    States: extracted (present + section live), present-but-not-yet-
    extracted, confirmed-absent, and undetermined (probe didn't reach the
    accessor — e.g. city probes skipped with no capital).  A failed probe
    yields one loud line, never a guessed list."""
    if not probe:
        return [
            "capability probe failed this capture — expansion-mechanic "
            "availability UNKNOWN (nothing extracted beyond base sections)"
        ]
    api = probe.get("api") or {}
    out: list[str] = []
    for label, key, extracted in _MECHANIC_PROBES:
        t = api.get(key)
        if t == "function":
            if extracted:
                out.append(f"{label} — extracted (see snapshot sections)")
            else:
                out.append(f"{label} — PRESENT in this game, not yet extracted")
        elif t is None:
            out.append(f"{label} — undetermined this capture (probe did not reach {key})")
        else:
            out.append(f"{label} — unavailable in this game ({key} = {t})")
    return out


# Ruleset id → human label for the snapshot header.
_RULESET_LABELS = {
    "RULESET_STANDARD": "base game",
    "RULESET_EXPANSION_1": "Rise & Fall",
    "RULESET_EXPANSION_2": "Gathering Storm (includes Rise & Fall)",
}


async def collect_snapshot(conn: GameConnection) -> dict[str, Any]:
    t0 = time.perf_counter()
    diagnostics: list[dict[str, Any]] = []
    fragments: dict[str, dict[str, Any]] = {}
    per_query_timing: dict[str, float] = {}
    traces: dict[str, list[str]] = {}
    compat_notes: list[dict[str, str]] = []
    exec_errors: dict[str, str] = {}

    for name in Q.ALL_QUERIES:
        qt = time.perf_counter()
        _, parsed, trace_lines, warn_lines, err = await _run_one(conn, name)
        per_query_timing[name] = round(time.perf_counter() - qt, 3)
        traces[name] = trace_lines
        for w in warn_lines:
            # WARN|<section>|<message>
            parts = w.split("|", 2)
            compat_notes.append(
                {
                    "section": parts[1] if len(parts) > 1 else name,
                    "message": parts[2] if len(parts) > 2 else w,
                }
            )
        if err:
            exec_errors[name] = err
            diagnostics.append({"section": name, "message": err})
            fragments[name] = {}
            continue
        # Merge query-level diagnostics into the shared list.
        if parsed and "diagnostics" in parsed:
            for d in parsed["diagnostics"]:
                d = {**d, "section": f"{name}.{d.get('section', '')}"}
                diagnostics.append(d)
            # Keep the raw fragment's diagnostics too so _classify_sections
            # can inspect them.
        fragments[name] = parsed or {}

    section_status = _classify_sections(fragments, exec_errors)

    # -- Build the merged snapshot -------------------------------------------
    meta_frag = fragments.get("meta", {}) or {}
    choices_frag = fragments.get("choices", {}) or {}
    cities_frag = fragments.get("cities", {}) or {}
    units_frag = fragments.get("units", {}) or {}
    map_frag = fragments.get("map", {}) or {}
    diplo_frag = fragments.get("diplo", {}) or {}
    rel_frag = fragments.get("religion", {}) or {}
    notif_frag = fragments.get("notif", {}) or {}
    ruleset_frag = fragments.get("ruleset", {}) or {}
    probe_frag = fragments.get("probe", {}) or {}
    xpac_frag = fragments.get("xpac", {}) or {}

    # Live DB tables from the ruleset query — the static module tables are
    # only fallbacks now.  Empty set/dict => derivations fall back and label
    # their source accordingly.
    rs = ruleset_frag.get("ruleset") or {}
    live_specialty: set[str] = set(rs.get("specialty_districts") or [])
    live_housing: dict[str, int] = rs.get("housing_buildings") or {}
    _resclass: dict[str, str] = rs.get("resource_classes") or {}
    live_lux: set[str] = {k for k, v in _resclass.items() if v == "LUXURY"}
    live_strat: set[str] = {k for k, v in _resclass.items() if v == "STRATEGIC"}

    def _or_none(status_key: str, value):
        """Return None (=> "QUERY FAILED" in markdown) if the section failed,
        else return the value even if empty."""
        return value if section_status.get(status_key) != "failed" else None

    # Per-city yield decomposition (worked tiles / buildings / adjacency /
    # trade / unattributed remainder), composed from already-parsed parts.
    for c in cities_frag.get("cities") or []:
        c["yield_breakdown"] = P.build_yield_breakdown(c)

    # v1.7.0 Part A derivations — pure reorganization of already-collected
    # data (no new engine reads).  Each helper returns None on missing
    # inputs; None renders as absent, never as a fake value.
    map_ok = section_status.get("map") != "failed"
    tiles_by_xy = (
        {(t["x"], t["y"]): t for t in map_frag.get("tiles") or []} if map_ok else None
    )
    # Attach per-city loyalty (xpac query) to my cities by id.  Absent key
    # = unknown, never "no loyalty pressure".
    _loy_by_cid = {l.get("city_id"): l for l in xpac_frag.get("loyalty") or []}
    for c in cities_frag.get("cities") or []:
        l = _loy_by_cid.get(c.get("id"))
        if l:
            c["loyalty"] = {
                "loyalty": l.get("loyalty"),
                "per_turn": l.get("per_turn"),
                "max": l.get("max"),
            }

    # Attach my alliance state (xpac query) to the matching met major.
    # A failed/empty xpac read attaches nothing — the `alliance` key is
    # simply ABSENT, which is "unknown", never "no alliance".
    _ally_by_pid = {a.get("player_id"): a for a in xpac_frag.get("alliances") or []}
    for m in diplo_frag.get("majors") or []:
        a = _ally_by_pid.get(m.get("player_id"))
        if a:
            m["alliance"] = {
                "name": a.get("alliance_name"),
                "level": a.get("level"),
                "turns_until_expiration": a.get("turns_until_expiration"),
            }

    for c in cities_frag.get("cities") or []:
        c["district_capacity"] = P.district_capacity(c, live_specialty or None)
        c["housing_breakdown"] = P.build_housing_breakdown(
            c, tiles_by_xy, live_housing or None
        )
        c["amenity_status"] = P.amenity_status(c)

    snapshot: dict[str, Any] = {
        "schema": SCHEMA_VERSION,
        "coach_version": COACH_VERSION,
        "generated_at_epoch": time.time(),
        "meta":               _or_none("header",           meta_frag.get("meta", {}) or {}),
        "victories_enabled":  _or_none("victories",       meta_frag.get("victories_enabled", []) or []),
        "empire":             _or_none("empire",           meta_frag.get("empire", {}) or {}),
        "current_research":   _or_none("current_research", meta_frag.get("current", {}).get("tech")),
        "current_civic":      _or_none("current_civic",    meta_frag.get("current", {}).get("civic")),
        "resources":          _or_none("resources",        meta_frag.get("resources", []) or []),
        "government":         _or_none("government",       meta_frag.get("government", {}) or {}),
        "policy_slots":       _or_none("policy_slots",     meta_frag.get("policy_slots", []) or []),
        "policy_available":   _or_none("policy_available", meta_frag.get("policy_available", []) or []),
        "great_people":       _or_none("great_people",     meta_frag.get("great_people", []) or []),
        "techs_available":    _or_none("techs_available",  choices_frag.get("techs_available", []) or []),
        "civics_available":   _or_none("civics_available", choices_frag.get("civics_available", []) or []),
        "tech_tree":          _or_none("tech_tree",        choices_frag.get("tech_tree", []) or []),
        "civic_tree":         _or_none("civic_tree",       choices_frag.get("civic_tree", []) or []),
        "cities":             _or_none("cities",           cities_frag.get("cities", []) or []),
        "units":              _or_none("units",            units_frag.get("units", []) or []),
        "barbarians_visible": units_frag.get("barbarians_visible", []) or [],
        "camps_visible":      units_frag.get("camps_visible", []) or [],
        "camps_revealed_only": units_frag.get("camps_revealed_only", []) or [],
        "map_meta":           map_frag.get("map_meta", {}) or {},
        "map_totals":         map_frag.get("map_totals", {}) or {},
        "tiles":              _or_none("map",              map_frag.get("tiles", []) or []),
        "map_owners":         map_frag.get("owners", {}) or {},
        "natural_wonders":    map_frag.get("natural_wonders", []) or [],
        "envoys":             _or_none("envoys",           diplo_frag.get("envoys", {}) or {}),
        "majors_met":         _or_none("majors_met",       diplo_frag.get("majors", []) or []),
        "city_states_met":    _or_none("city_states_met",  diplo_frag.get("city_states", []) or []),
        "eliminated":         diplo_frag.get("eliminated", []) or [],
        "gossip":             _or_none("majors_met",       diplo_frag.get("gossip", []) or []),
        "resources_inventory": P.resources_inventory(
            (cities_frag.get("cities") or []) if section_status.get("cities") != "failed" else None
        ),
        "rivals":             P.build_rivals(diplo_frag, map_frag, rel_frag, section_status),
        "rival_cities":       _or_none("map",              map_frag.get("rival_cities", []) or []),
        "units_by_civ":       P.units_by_civ(map_frag.get("tiles") if section_status.get("map") != "failed" else None),
        "world_religions":    rel_frag.get("world_religions", []) or [],
        "religion": _or_none(
            "religion",
            {
                "pantheon": rel_frag.get("pantheon", {}),
                "religion": rel_frag.get("religion"),
                "beliefs":  rel_frag.get("beliefs", []),
                "can_found_pantheon": rel_frag.get("can_found_pantheon", False),
                "city_religion": rel_frag.get("city_religion", {}),
            },
        ),
        "luxury_duplicates": P.luxury_duplicates(
            meta_frag.get("resources") if section_status.get("resources") != "failed" else None
        ),
        "settler_advisor": P.settler_advisor(
            units_frag.get("units") if section_status.get("units") != "failed" else None,
            map_frag.get("tiles") if map_ok else None,
            cities_frag.get("cities") if section_status.get("cities") != "failed" else None,
            map_frag.get("rival_cities") if map_ok else None,
            diplo_frag.get("city_states") if section_status.get("city_states_met") != "failed" else None,
            owned_luxury_types={
                (r.get("type") or "").replace("RESOURCE_", "")
                for r in meta_frag.get("resources") or []
                if r.get("class") == "LUXURY"
            },
            luxury_set=live_lux or None,
            strategic_set=live_strat or None,
        ),
        "civ_accounting": P.civ_accounting(
            diplo_frag.get("majors") if section_status.get("majors_met") != "failed" else None,
            P.build_rivals(diplo_frag, map_frag, rel_frag, section_status),
            rel_frag.get("world_religions"),
            meta_frag.get("meta"),
        ),
        "notifications":     _or_none("notifications", notif_frag.get("notifications", []) or []),
        "end_turn_blockers": notif_frag.get("end_turn_blockers", []) or [],
        # -- Expansion mechanics, R&F batch (Phase D1).  None = query
        # failed; {} = query ran but the mechanic returned nothing.
        "era":               _or_none("era",         xpac_frag.get("era", {}) or {}),
        "governors":         _or_none("governors",   xpac_frag.get("governors", {}) or {}),
        "emergencies":       _or_none("emergencies", xpac_frag.get("emergencies", {}) or {}),
        # Declared ruleset — stamped into every snapshot so a modded or
        # expansion game is never silently compared against a vanilla one.
        # None = the ruleset query itself failed (renders as QUERY FAILED).
        "ruleset": _or_none(
            "ruleset",
            {
                "ruleset": rs.get("ruleset", ""),
                "ruleset_label": _RULESET_LABELS.get(
                    rs.get("ruleset", ""), rs.get("ruleset") or "unknown"
                ),
                "mod_count": rs.get("mod_count", -1),
                "mods": rs.get("mods", []),
                "specialty_districts": rs.get("specialty_districts", []),
                "resource_classes": _resclass,
                "housing_buildings": live_housing,
            },
        ),
        "section_status":    section_status,
        "diagnostics": {
            "per_query_seconds": per_query_timing,
            "failures": diagnostics,
            "compat_notes": compat_notes,  # WARN channel — fallbacks taken, not failures
            # Derived at runtime from this capture's own probe — three
            # honest states per mechanic (present-not-extracted / absent /
            # undetermined).  Never a static assertion.
            "unsupported": _derive_unsupported(
                probe_frag.get("probe")
                if section_status.get("probe") != "failed"
                else None
            ),
            # Q9 capability probe: live ruleset, enabled mods, GameInfo
            # census, expansion-accessor discovery.  Diagnostics-only —
            # no coaching section reads from this (yet).  None = probe
            # query itself failed, never silently {}.
            "probe": _or_none("probe", probe_frag.get("probe", {}) or {}),
            "traces": traces,  # populated for every query, useful for the next post-mortem
            "total_seconds": round(time.perf_counter() - t0, 3),
        },
    }
    snapshot["turn_blockers_summary"] = _build_turn_blockers(snapshot)
    return snapshot


def _build_turn_blockers(snap: dict[str, Any]) -> list[str]:
    """Compact list of what needs attention.  If a source query failed we
    surface that instead of pretending the field is empty."""
    out: list[str] = []
    st = snap.get("section_status", {}) or {}
    for b in snap.get("end_turn_blockers", []) or []:
        out.append(f"blocker:{b.get('blocker_type', '')} ({b.get('message', '')})")
    if st.get("units") == "ok":
        idle = [u for u in (snap.get("units") or []) if u.get("idle")]
        if idle:
            out.append(f"{len(idle)} idle unit(s)")
        promo = [u for u in (snap.get("units") or []) if u.get("promotions_available", 0) > 0]
        if promo:
            out.append(f"{len(promo)} unit(s) with unspent promotion")
    elif st.get("units") == "failed":
        out.append("units: QUERY FAILED — cannot list idle/promo units")

    if st.get("cities") == "ok":
        idle_cities = [c for c in (snap.get("cities") or []) if (c.get("production") or {}).get("type") == "nothing"]
        if idle_cities:
            out.append(f"{len(idle_cities)} city/cities with no production")
    elif st.get("cities") == "failed":
        out.append("cities: QUERY FAILED — cannot check idle city production")

    if st.get("current_research") == "ok":
        cr = snap.get("current_research") or {}
        if not cr.get("type"):
            out.append("no research selected")
    elif st.get("current_research") == "failed":
        out.append("current research: QUERY FAILED — cannot confirm selection")

    if st.get("current_civic") == "ok":
        cc = snap.get("current_civic") or {}
        if not cc.get("type"):
            out.append("no civic selected")
    elif st.get("current_civic") == "failed":
        out.append("current civic: QUERY FAILED — cannot confirm selection")

    if st.get("government") == "ok":
        g = snap.get("government") or {}
        if g.get("slots_open", 0) > 0:
            out.append(f"{g['slots_open']} open policy slot(s)")
    if st.get("religion") == "ok":
        if (snap.get("religion") or {}).get("can_found_pantheon"):
            out.append("pantheon available to found")
    return out
