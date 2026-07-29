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


async def collect_snapshot(conn: GameConnection) -> dict[str, Any]:
    t0 = time.perf_counter()
    diagnostics: list[dict[str, Any]] = []
    unsupported: list[str] = [
        "governors (Rise & Fall)",
        "loyalty (Rise & Fall)",
        "era score, Golden/Dark Ages, dedications (Rise & Fall)",
        "formal alliances with level (Rise & Fall)",
        "diplomatic favor, World Congress, Diplomatic Victory (Gathering Storm)",
        "climate, disasters, floods, volcanoes (Gathering Storm)",
        "power, resource consumption, canals, dams (Gathering Storm)",
        "railroads (Gathering Storm)",
    ]
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

    def _or_none(status_key: str, value):
        """Return None (=> "QUERY FAILED" in markdown) if the section failed,
        else return the value even if empty."""
        return value if section_status.get(status_key) != "failed" else None

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
        "notifications":     _or_none("notifications", notif_frag.get("notifications", []) or []),
        "end_turn_blockers": notif_frag.get("end_turn_blockers", []) or [],
        "section_status":    section_status,
        "diagnostics": {
            "per_query_seconds": per_query_timing,
            "failures": diagnostics,
            "compat_notes": compat_notes,  # WARN channel — fallbacks taken, not failures
            "unsupported": unsupported,
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
