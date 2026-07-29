"""Parse the pipe-delimited output lines from ``queries.py`` into typed dicts.

Each ``parse_*`` function accepts the list of lines returned by
``GameConnection.execute_read`` and returns a normalized dict fragment.  The
collector merges the fragments into a single snapshot.

All parsers are defensive: an unrecognized line is ignored (recorded under
diagnostics), a malformed field falls back to a sane default rather than
raising.  Missing sections show up as empty lists/dicts, not exceptions.
"""

from __future__ import annotations

from typing import Any


def _s(parts: list[str], i: int, default: str = "") -> str:
    return parts[i] if i < len(parts) else default


def _i(parts: list[str], i: int, default: int = 0) -> int:
    try:
        return int(float(parts[i]))
    except (ValueError, IndexError):
        return default


def _f(parts: list[str], i: int, default: float = 0.0) -> float:
    try:
        return float(parts[i])
    except (ValueError, IndexError):
        return default


def _b(parts: list[str], i: int, default: bool = False) -> bool:
    v = _s(parts, i, "").strip().lower()
    if v in ("true", "1", "yes"):
        return True
    if v in ("false", "0", "no", ""):
        return False
    return default


def parse_meta(lines: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {
        "meta": {},
        "empire": {},
        "current": {},
        "resources": [],
        "government": {},
        "policy_slots": [],
        "policy_available": [],
        "great_people": [],
        "victories_enabled": [],
        "diagnostics": [],
    }
    for line in lines:
        p = line.split("|")
        tag = p[0] if p else ""
        if tag == "META":
            out["meta"] = {
                "turn": _i(p, 1),
                "year": _s(p, 2),
                "era": _s(p, 3),
                "civ_type": _s(p, 4),
                "civ_name": _s(p, 5),
                "leader_type": _s(p, 6),
                "leader_name": _s(p, 7),
                "difficulty": _s(p, 8),
                "speed": _s(p, 9),
                "map_size": _s(p, 10),
                "map_type": _s(p, 11),
                "max_players": _i(p, 12),
                "max_turns": _i(p, 13),
            }
        elif tag == "VICT":
            v = _s(p, 1)
            out["victories_enabled"] = [x for x in v.split(",") if x]
        elif tag == "EMPIRE":
            out["empire"] = {
                "score": _i(p, 1),
                "gold": _f(p, 2),
                "gold_yield": _f(p, 3),
                "gold_maint": _f(p, 4),
                "gold_net": _f(p, 5),
                "science": _f(p, 6),
                "culture": _f(p, 7),
                "faith": _f(p, 8),
                "faith_yield": _f(p, 9),
                "tourism": _f(p, 10),
                "military": _i(p, 11),
                "techs_done": _i(p, 12),
                "civics_done": _i(p, 13),
                "num_cities": _i(p, 14),
                "num_units": _i(p, 15),
                "total_pop": _i(p, 16),
                "trade_used": _i(p, 17),
                "trade_cap": _i(p, 18),
                "explored_land": _i(p, 19),
                "total_land": _i(p, 20),
            }
        elif tag == "CURR":
            kind = _s(p, 1).lower()
            out["current"][kind] = {
                "type": _s(p, 2),
                "name": _s(p, 3),
                "progress": _f(p, 4),
                "cost": _f(p, 5),
                "turns": _i(p, 6, -1),
                "boosted": _b(p, 7),
                "boost_desc": _s(p, 8),
            }
        elif tag == "RES":
            out["resources"].append(
                {
                    "class": _s(p, 1),
                    "type": _s(p, 2),
                    "name": _s(p, 3),
                    "amount": _i(p, 4),
                    "accessible": _b(p, 5),
                }
            )
        elif tag == "GOVT":
            out["government"] = {
                "type": _s(p, 1),
                "name": _s(p, 2),
                "slots_open": _i(p, 3),
                "free_change_available": _b(p, 4),
            }
        elif tag == "POLICYSLOT":
            out["policy_slots"].append(
                {
                    "index": _i(p, 1),
                    "slot_type": _s(p, 2),
                    "slot_name": _s(p, 3),
                    "policy_type": _s(p, 4),
                    "policy_name": _s(p, 5),
                    "effect": _s(p, 6),
                }
            )
        elif tag == "POLICYAVAIL":
            out["policy_available"].append(
                {
                    "type": _s(p, 1),
                    "slot": _s(p, 2),
                    "name": _s(p, 3),
                    "effect": _s(p, 4),
                }
            )
        elif tag == "GPPT":
            out["great_people"].append(
                {
                    "class_type": _s(p, 1),
                    "class": _s(p, 2),
                    "points": _f(p, 3),
                    "per_turn": _f(p, 4),
                    "next_cost": _i(p, 5),
                    "candidate": _s(p, 6),
                    "patronize_cost": _i(p, 7, -1),
                }
            )
        elif tag == "DIAG":
            out["diagnostics"].append({"section": _s(p, 1), "message": _s(p, 2)})
    return out


def parse_choices(lines: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {"techs_available": [], "civics_available": [], "diagnostics": []}
    for line in lines:
        p = line.split("|")
        tag = p[0] if p else ""
        if tag == "TAV":
            out["techs_available"].append(
                {
                    "type": _s(p, 1),
                    "name": _s(p, 2),
                    "progress": _f(p, 3),
                    "cost": _f(p, 4),
                    "turns": _i(p, 5, -1),
                    "boosted": _b(p, 6),
                    "boost_desc": _s(p, 7),
                    "unlocks": _s(p, 8),
                }
            )
        elif tag == "CAV":
            out["civics_available"].append(
                {
                    "type": _s(p, 1),
                    "name": _s(p, 2),
                    "progress": _f(p, 3),
                    "cost": _f(p, 4),
                    "turns": _i(p, 5, -1),
                    "boosted": _b(p, 6),
                    "boost_desc": _s(p, 7),
                    "unlocks": _s(p, 8),
                }
            )
        elif tag == "DIAG":
            out["diagnostics"].append({"section": _s(p, 1), "message": _s(p, 2)})
    return out


def parse_cities(lines: list[str]) -> dict[str, Any]:
    """Cities are complex — one CITY line per city, followed by DIST/BLDG/TILES/PROD/TRADE
    lines that reference the city by ID.
    """
    cities: dict[int, dict[str, Any]] = {}
    diagnostics: list[dict[str, Any]] = []
    for line in lines:
        p = line.split("|")
        tag = p[0] if p else ""
        if tag == "CITY":
            cid = _i(p, 1)
            cities[cid] = {
                "id": cid,
                "name": _s(p, 2),
                "is_capital": _b(p, 3),
                "x": _i(p, 4),
                "y": _i(p, 5),
                "population": _i(p, 6),
                "food_surplus": _f(p, 7),
                "turns_to_growth": _i(p, 8, -1),
                "turns_to_starvation": _i(p, 9, -1),
                "housing": _i(p, 10),
                "amenities": _i(p, 11),
                "amenities_needed": _i(p, 12),
                "happiness": _i(p, 13),
                "yields": {
                    "food": _f(p, 14),
                    "production": _f(p, 15),
                    "gold": _f(p, 16),
                    "science": _f(p, 17),
                    "culture": _f(p, 18),
                    "faith": _f(p, 19),
                },
                "production": {
                    "type": _s(p, 20),
                    "name": _s(p, 21),
                    "progress": _f(p, 22),
                    "cost": _f(p, 23),
                    "turns": _i(p, 24, -1),
                },
                "defense": {
                    "strength": _i(p, 25),
                    "garrison_hp": _i(p, 26),
                    "garrison_max": _i(p, 27),
                    "wall_hp": _i(p, 28),
                    "wall_max": _i(p, 29),
                },
                "border_expansion_turns": _i(p, 30, -1),
                "majority_religion": _s(p, 31),
                "districts": [],
                "buildings": [],
                "tiles_rollup": {},
                "production_options": [],
                "trade_routes": [],
            }
        elif tag == "DIST":
            cid = _i(p, 1)
            city = cities.get(cid)
            if city:
                adj: dict[str, int] = {}
                for pair in _s(p, 6).split(","):
                    if ":" in pair:
                        k, v = pair.split(":", 1)
                        try:
                            adj[k] = int(v)
                        except ValueError:
                            pass
                city["districts"].append(
                    {
                        "type": _s(p, 2),
                        "name": _s(p, 3),
                        "x": _i(p, 4),
                        "y": _i(p, 5),
                        "pillaged": _b(p, 6) if _s(p, 6) in ("true", "false") else False,
                        "adjacency": adj,
                    }
                )
                # The pillaged field is column index 6 in the query — but adjacency
                # is column 7.  Re-parse to disambiguate:
                city["districts"][-1]["pillaged"] = _s(p, 6).strip().lower() == "true"
        elif tag == "BLDG":
            cid = _i(p, 1)
            city = cities.get(cid)
            if city:
                city["buildings"].append(
                    {
                        "district": _s(p, 2),
                        "type": _s(p, 3),
                        "name": _s(p, 4),
                        "is_wonder": _b(p, 5),
                        "pillaged": _b(p, 6),
                    }
                )
        elif tag == "TILES":
            cid = _i(p, 1)
            city = cities.get(cid)
            if city:
                def _breakdown(s: str) -> dict[str, int]:
                    out: dict[str, int] = {}
                    for token in s.split(","):
                        if ":" in token:
                            n, k = token.split(":", 1)
                            try:
                                out[k] = int(n)
                            except ValueError:
                                pass
                    return out
                city["tiles_rollup"] = {
                    "owned": _i(p, 2),
                    "worked": _i(p, 3),
                    "terrain": _breakdown(_s(p, 4)),
                    "features": _breakdown(_s(p, 5)),
                    "improvements": _breakdown(_s(p, 6)),
                }
        elif tag == "PROD":
            cid = _i(p, 1)
            city = cities.get(cid)
            if city:
                city["production_options"].append(
                    {
                        "kind": _s(p, 2),
                        "type": _s(p, 3),
                        "name": _s(p, 4),
                        "progress": _f(p, 5),
                        "cost": _f(p, 6),
                        "turns": _i(p, 7, -1),
                    }
                )
        elif tag == "TRADE":
            cid = _i(p, 1)
            city = cities.get(cid)
            if city:
                yields: dict[str, int] = {}
                for tok in _s(p, 4).split(","):
                    if ":" in tok:
                        k, v = tok.split(":", 1)
                        try:
                            yields[k] = int(v)
                        except ValueError:
                            pass
                city["trade_routes"].append(
                    {
                        "dest_player": _i(p, 2),
                        "dest_city": _s(p, 3),
                        "yields": yields,
                        # Added in schema 1.1 — readable owner name, or
                        # "domestic" when the route stays inside our empire.
                        "dest_civ": _s(p, 5, "?"),
                    }
                )
        elif tag == "DIAG":
            diagnostics.append({"section": _s(p, 1), "message": _s(p, 2)})
    return {"cities": list(cities.values()), "diagnostics": diagnostics}


def parse_units(lines: list[str]) -> dict[str, Any]:
    units: list[dict[str, Any]] = []
    barbs_visible: list[dict[str, Any]] = []
    camps_visible: list[dict[str, Any]] = []
    camps_revealed: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    for line in lines:
        p = line.split("|")
        tag = p[0] if p else ""
        if tag == "UNIT":
            units.append(
                {
                    "id": _i(p, 1),
                    "type": _s(p, 2),
                    "name": _s(p, 3),
                    "class": _s(p, 4),
                    "x": _i(p, 5),
                    "y": _i(p, 6),
                    "hp": _i(p, 7),
                    "hp_max": _i(p, 8),
                    "moves": _f(p, 9),
                    "moves_max": _f(p, 10),
                    "combat": _i(p, 11),
                    "ranged": _i(p, 12),
                    "bombard": _i(p, 13),
                    "range": _i(p, 14),
                    "xp": _i(p, 15),
                    "xp_needed": _i(p, 16),
                    "promotions_held": _i(p, 17),
                    "promotions_available": _i(p, 18),
                    "idle": _b(p, 19),
                    "fortify_turns": _i(p, 20),
                    "charges": _i(p, 21),
                    "can_upgrade": _b(p, 22),
                    "upgrade_to": _s(p, 23),
                    "upgrade_cost": _i(p, 24),
                }
            )
        elif tag == "BARB":
            barbs_visible.append(
                {"name": _s(p, 1), "x": _i(p, 2), "y": _i(p, 3), "hp": _i(p, 4), "hp_max": _i(p, 5)}
            )
        elif tag == "CAMPV":
            camps_visible.append({"x": _i(p, 1), "y": _i(p, 2)})
        elif tag == "CAMPR":
            camps_revealed.append({"x": _i(p, 1), "y": _i(p, 2)})
        elif tag == "DIAG":
            diagnostics.append({"section": _s(p, 1), "message": _s(p, 2)})
    return {
        "units": units,
        "barbarians_visible": barbs_visible,
        "camps_visible": camps_visible,
        "camps_revealed_only": camps_revealed,
        "diagnostics": diagnostics,
    }


def parse_map(lines: list[str]) -> dict[str, Any]:
    tiles: list[dict[str, Any]] = []
    natural_wonders: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    meta = {"total_plots": 0, "grid": ""}
    totals = {"revealed": 0, "visible": 0, "natural_wonders": 0}
    for line in lines:
        p = line.split("|")
        tag = p[0] if p else ""
        if tag == "MAPMETA":
            meta = {"total_plots": _i(p, 1), "grid": _s(p, 2)}
        elif tag == "MAP":
            tiles.append(
                {
                    "x": _i(p, 1),
                    "y": _i(p, 2),
                    "visible": _i(p, 3) == 1,
                    "terrain": _s(p, 4),
                    "feature": _s(p, 5),
                    "resource": _s(p, 6),
                    "improvement": _s(p, 7),
                    "road": _s(p, 8),
                    "owner": _s(p, 9),
                    "district": _s(p, 10),
                    "is_city": _s(p, 11).lower() == "true",
                    "units": _s(p, 12),
                    "extra": _s(p, 13),
                }
            )
        elif tag == "NW":
            natural_wonders.append(
                {"name": _s(p, 1), "x": _i(p, 2), "y": _i(p, 3), "type": _s(p, 4)}
            )
        elif tag == "MAPTOTAL":
            totals = {"revealed": _i(p, 1), "visible": _i(p, 2), "natural_wonders": _i(p, 3)}
        elif tag == "DIAG":
            diagnostics.append({"section": _s(p, 1), "message": _s(p, 2)})
    return {
        "map_meta": meta,
        "map_totals": totals,
        "tiles": tiles,
        "natural_wonders": natural_wonders,
        "diagnostics": diagnostics,
    }


def parse_diplo(lines: list[str]) -> dict[str, Any]:
    envoys = {}
    majors: list[dict[str, Any]] = []
    city_states: list[dict[str, Any]] = []
    agendas: dict[int, list[dict[str, Any]]] = {}
    quests: dict[int, list[dict[str, Any]]] = {}
    diagnostics: list[dict[str, Any]] = []
    for line in lines:
        p = line.split("|")
        tag = p[0] if p else ""
        if tag == "ENVOY":
            envoys = {
                "in_hand": _i(p, 1),
                "points": _i(p, 2),
                "threshold": _i(p, 3),
                "per_turn": _f(p, 4),
                "envoys_per_threshold": _i(p, 5),
            }
        elif tag == "MAJOR":
            majors.append(
                {
                    "player_id": _i(p, 1),
                    "civ_type": _s(p, 2),
                    "civ_name": _s(p, 3),
                    "leader_type": _s(p, 4),
                    "leader_name": _s(p, 5),
                    "at_war": _b(p, 6),
                    "met_turn": _i(p, 7, -1),
                    "diplo_visibility": _i(p, 8),
                    "score": _i(p, 9),
                    "military": _i(p, 10),
                    "open_borders_from_them": _b(p, 11),
                    "open_borders_from_us": _b(p, 12),
                    "delegation_sent": _b(p, 13),
                    "embassy_sent": _b(p, 14),
                    "relation_state_idx": _i(p, 15, -1),
                    "relation_state_name": _s(p, 16),
                }
            )
        elif tag == "CS":
            city_states.append(
                {
                    "player_id": _i(p, 1),
                    "civ_type": _s(p, 2),
                    "civ_name": _s(p, 3),
                    "cs_type": _s(p, 4),
                    "envoys_sent": _i(p, 5),
                    "suzerain": _s(p, 6),
                    "x": _i(p, 7, -1),
                    "y": _i(p, 8, -1),
                    "at_war": _b(p, 9),
                    "met_turn": _i(p, 10, -1),
                }
            )
        elif tag == "AGENDA":
            pid = _i(p, 1)
            agendas.setdefault(pid, []).append({"type": _s(p, 2), "name": _s(p, 3)})
        elif tag == "QUEST":
            pid = _i(p, 1)
            quests.setdefault(pid, []).append({"type": _s(p, 2), "description": _s(p, 3)})
        elif tag == "DIAG":
            diagnostics.append({"section": _s(p, 1), "message": _s(p, 2)})
    # Attach agendas/quests to their respective players
    for m in majors:
        m["known_agendas"] = agendas.get(m["player_id"], [])
    for c in city_states:
        c["active_quests"] = quests.get(c["player_id"], [])
    return {
        "envoys": envoys,
        "majors": majors,
        "city_states": city_states,
        "diagnostics": diagnostics,
    }


def parse_religion(lines: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {
        "pantheon": {"type": "NONE", "name": "none", "description": ""},
        "religion": None,
        "beliefs": [],
        "can_found_pantheon": False,
        "city_religion": {},
        "diagnostics": [],
    }
    for line in lines:
        p = line.split("|")
        tag = p[0] if p else ""
        if tag == "PANTHEON":
            out["pantheon"] = {
                "type": _s(p, 1),
                "name": _s(p, 2),
                "description": _s(p, 3),
            }
        elif tag == "RELIGION":
            out["religion"] = {"type": _s(p, 1), "name": _s(p, 2)}
        elif tag == "BELIEF":
            out["beliefs"].append(
                {
                    "class": _s(p, 1),
                    "type": _s(p, 2),
                    "name": _s(p, 3),
                    "description": _s(p, 4),
                }
            )
        elif tag == "RELSTATE":
            v = _s(p, 1)
            if v.startswith("canFoundPantheon="):
                out["can_found_pantheon"] = v.endswith("true")
        elif tag == "CITYREL":
            # Keyed by stringified city ID so the snapshot survives a JSON
            # round-trip (int keys become strings when JSON is re-loaded).
            out["city_religion"][str(_i(p, 1))] = _s(p, 2)
        elif tag == "DIAG":
            out["diagnostics"].append({"section": _s(p, 1), "message": _s(p, 2)})
    return out


def parse_notifications(lines: list[str]) -> dict[str, Any]:
    notifs: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    seen_blockers: set[str] = set()
    for line in lines:
        p = line.split("|")
        tag = p[0] if p else ""
        if tag == "NOTIF":
            tn = _s(p, 1)
            bt = _s(p, 2)
            msg = _s(p, 3)
            notifs.append({"type": tn, "blocker_type": bt, "message": msg})
            if bt and bt not in seen_blockers:
                seen_blockers.add(bt)
                blockers.append({"blocker_type": bt, "message": msg})
        elif tag == "DIAG":
            diagnostics.append({"section": _s(p, 1), "message": _s(p, 2)})
    return {"notifications": notifs, "end_turn_blockers": blockers, "diagnostics": diagnostics}
