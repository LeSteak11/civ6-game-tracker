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
    # Game/map seeds arrive on their own SEEDS line.  Collected separately
    # and merged into ``meta`` only if the META header actually parsed —
    # merging into an empty meta dict would make a failed header section
    # look "ok" to the collector's section classifier.
    seeds: dict[str, Any] = {}
    for line in lines:
        p = line.split("|")
        tag = p[0] if p else ""
        if tag == "SEEDS":
            seeds = {
                "game_seed": _i(p, 1, -1),
                "map_seed": _i(p, 2, -1),
            }
        elif tag == "META":
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
    out["seeds"] = seeds
    if out["meta"] and seeds:
        out["meta"].update(seeds)
    return out


def _tree_item(p: list[str]) -> dict[str, Any]:
    """Shared shape for TTREE/CTREE lines.

    ``partial`` is derived: progress banked on a not-yet-completed item
    (Civ 6 keeps partial research/culture when you switch away).
    """
    status = _s(p, 4)
    prog = _f(p, 5)
    return {
        "type": _s(p, 1),
        "name": _s(p, 2),
        "era": _s(p, 3),
        "status": status,          # done | current | available | blocked
        "progress": prog,
        "cost": _f(p, 6),
        "turns": _i(p, 7, -1),
        "partial": status != "done" and prog > 0,
        "prereqs": [x for x in _s(p, 8).split(",") if x],
    }


def parse_choices(lines: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {
        "techs_available": [],
        "civics_available": [],
        "tech_tree": [],
        "civic_tree": [],
        "diagnostics": [],
    }
    for line in lines:
        p = line.split("|")
        tag = p[0] if p else ""
        if tag == "TTREE":
            out["tech_tree"].append(_tree_item(p))
        elif tag == "CTREE":
            out["civic_tree"].append(_tree_item(p))
        elif tag == "TAV":
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
                "resources": [],
                "production_unavailable": [],
                # None until a CITYSTATUS line arrives — a missing status
                # read must stay distinct from any real value.
                "status_labels": None,
            }
        elif tag == "DIST":
            cid = _i(p, 1)
            city = cities.get(cid)
            if city:
                # DIST|cid|type|name|x|y|pillaged|adjacency — column 6 is
                # the pillaged flag, column 7 the adjacency pairs.  (v1.5.0
                # fix: adjacency was previously read from column 6 and so
                # always parsed empty.)
                adj: dict[str, int] = {}
                for pair in _s(p, 7).split(","):
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
                        "pillaged": _s(p, 6).strip().lower() == "true",
                        "adjacency": adj,
                    }
                )
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
        elif tag == "YSRC":
            cid = _i(p, 1)
            city = cities.get(cid)
            if city:
                city.setdefault("yield_sources", {})[_s(p, 2)] = {
                    "food": _f(p, 3),
                    "production": _f(p, 4),
                    "gold": _f(p, 5),
                    "science": _f(p, 6),
                    "culture": _f(p, 7),
                    "faith": _f(p, 8),
                }
        elif tag == "PRODX":
            cid = _i(p, 1)
            city = cities.get(cid)
            if city:
                city["production_unavailable"].append(
                    {
                        "category": _s(p, 2),   # UNIT | BLDG | WONDER | DIST
                        "type": _s(p, 3),
                        "name": _s(p, 4),
                        "cost": _f(p, 5),
                        # engine = localized FAILURE_REASONS from the same
                        # query the production panel uses; reconstructed =
                        # confirmed DB facts (each reason says which);
                        # unknown = blocked but nothing exposed.
                        "reason_source": _s(p, 6),
                        "reasons": [r for r in _s(p, 7).split(";;") if r],
                    }
                )
        elif tag == "CITYRES":
            cid = _i(p, 1)
            city = cities.get(cid)
            if city:
                city["resources"].append(
                    {
                        "type": _s(p, 2),
                        "class": _s(p, 3),
                        "name": _s(p, 4),
                        "improved": _b(p, 5),
                        "worked": _b(p, 6),
                        "source": "direct",  # observed on an owned tile
                    }
                )
        elif tag == "CITYSTATUS":
            cid = _i(p, 1)
            city = cities.get(cid)
            if city:
                city["status_labels"] = {
                    "happiness_label": _s(p, 2),
                    # -999 / -1 = unknown sentinels from probed accessors
                    "db_growth_modifier": _i(p, 3, -999),
                    "live_growth_modifier": _i(p, 4, -999),
                    "war_weariness": _i(p, 5, -1),
                    "source": "direct",
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
    rival_cities: list[dict[str, Any]] = []
    natural_wonders: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    meta = {"total_plots": 0, "grid": ""}
    totals = {"revealed": 0, "visible": 0, "natural_wonders": 0}
    # Owner-ID legend: str(player_id) -> readable name (str keys survive JSON)
    owners: dict[str, str] = {}
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
                    # Schema 1.1: city name on city-centre tiles ("" otherwise)
                    "city_name": _s(p, 14),
                }
            )
        elif tag == "RIVALCITY":
            rival_cities.append(
                {
                    "owner": _i(p, 1),
                    "name": _s(p, 2),
                    "x": _i(p, 3),
                    "y": _i(p, 4),
                    "capital": _s(p, 5).lower() == "true",
                    # "visible" = banner on screen now (pop/defense readable);
                    # "revealed" = seen before, name/position only, may be stale
                    "visibility": _s(p, 6),
                    "population": _i(p, 7, -1),
                    "defense": _i(p, 8, -1),
                    "wall_hp": _i(p, 9, -1),
                    "wall_max": _i(p, 10, -1),
                    "original_owner": _i(p, 11, -1),
                }
            )
        elif tag == "OWNER":
            owners[_s(p, 1)] = _s(p, 2)
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
        "rival_cities": rival_cities,
        "owners": owners,
        "natural_wonders": natural_wonders,
        "diagnostics": diagnostics,
    }


def parse_diplo(lines: list[str]) -> dict[str, Any]:
    envoys = {}
    majors: list[dict[str, Any]] = []
    city_states: list[dict[str, Any]] = []
    agendas: dict[int, list[dict[str, Any]]] = {}
    quests: dict[int, list[dict[str, Any]]] = {}
    eliminated: list[dict[str, Any]] = []
    wars: dict[int, list[int]] = {}
    pubstats: dict[int, dict[str, int]] = {}
    airel: dict[int, list[dict[str, Any]]] = {}
    rivgov: dict[int, dict[str, Any]] = {}
    cs_envoys: dict[int, dict[str, int]] = {}
    cs_bonuses: dict[int, dict[str, Any]] = {}
    gossip: list[dict[str, Any]] = []
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
        elif tag == "DEAD":
            eliminated.append(
                {
                    "player_id": _i(p, 1),
                    "civ_type": _s(p, 2),
                    "civ_name": _s(p, 3),
                    "was_major": _b(p, 4),
                    "alive": False,
                }
            )
        elif tag == "GOSSIP":
            gossip.append(
                {
                    "about": _i(p, 1),
                    "turn": _i(p, 2, -1),
                    "text": _s(p, 3),
                    # Localized, engine-visibility-filtered gossip string —
                    # a direct record, not a reconstruction.
                    "source": "direct",
                }
            )
        elif tag == "WARS":
            wars[_i(p, 1)] = [int(x) for x in _s(p, 2).split(",") if x.strip().lstrip("-").isdigit()]
        elif tag == "PUBSTATS":
            pubstats[_i(p, 1)] = {
                "techs": _i(p, 2, -1),
                "civics": _i(p, 3, -1),
                "tourism": _i(p, 4, -1),
            }
        elif tag == "AIREL":
            airel.setdefault(_i(p, 1), []).append({"with": _i(p, 2), "state": _s(p, 3)})
        elif tag == "RIVGOV":
            rivgov[_i(p, 1)] = {
                "type": _s(p, 2),
                "name": _s(p, 3),
                # visibility level the value was read at — vis-gated in Lua
                "read_at_visibility": _i(p, 4, -1),
                "source": "diplo_vis",
            }
        elif tag == "CSBONUS":
            pid = _i(p, 1)
            kind = _s(p, 2)
            entry = cs_bonuses.setdefault(pid, {"traits": []})
            if kind == "trait":
                entry["traits"].append(_s(p, 3))
            else:
                entry[kind] = _s(p, 3)
        elif tag == "CSENVOYS":
            by_civ: dict[str, int] = {}
            for pair in _s(p, 2).split(","):
                if ":" in pair:
                    pid_s, n_s = pair.split(":", 1)
                    try:
                        by_civ[str(int(pid_s))] = int(n_s)
                    except ValueError:
                        continue
            cs_envoys[_i(p, 1)] = by_civ
        elif tag == "DIAG":
            diagnostics.append({"section": _s(p, 1), "message": _s(p, 2)})
    # Attach per-player fragments to their respective entries
    for m in majors:
        pid = m["player_id"]
        m["known_agendas"] = agendas.get(pid, [])
        # None (never rendered as a value) when the line didn't arrive.
        m["wars_with"] = wars.get(pid)
        m["public_stats"] = pubstats.get(pid)
        m["relations"] = airel.get(pid, [])
        m["government"] = rivgov.get(pid)
    for c in city_states:
        pid = c["player_id"]
        c["active_quests"] = quests.get(pid, [])
        c["envoys_by_civ"] = cs_envoys.get(pid)
        c["wars_with"] = wars.get(pid)
        c["bonuses"] = cs_bonuses.get(pid)
        c["envoy_status"] = cs_envoy_status(c)
    return {
        "envoys": envoys,
        "majors": majors,
        "city_states": city_states,
        "eliminated": eliminated,
        "gossip": gossip,
        "diagnostics": diagnostics,
    }


def parse_religion(lines: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {
        "pantheon": {"type": "NONE", "name": "none", "description": ""},
        "religion": None,
        "beliefs": [],
        "can_found_pantheon": False,
        "city_religion": {},
        "world_religions": [],
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
        elif tag == "WREL":
            out["world_religions"].append(
                {
                    "founder": _i(p, 1, -1),
                    "type": _s(p, 2),
                    "name": _s(p, 3),
                    "num_beliefs": _i(p, 4, -1),
                    "source": "public",
                }
            )
        elif tag == "CITYREL":
            # Keyed by stringified city ID so the snapshot survives a JSON
            # round-trip (int keys become strings when JSON is re-loaded).
            out["city_religion"][str(_i(p, 1))] = _s(p, 2)
        elif tag == "DIAG":
            out["diagnostics"].append({"section": _s(p, 1), "message": _s(p, 2)})
    return out


_YIELD_KEYS = ("food", "production", "gold", "science", "culture", "faith")


def build_yield_breakdown(city: dict[str, Any]) -> dict[str, Any] | None:
    """Compose the per-source yield decomposition for one city.

    Sources and their trust tags:
      worked_tiles        direct       (plot:GetYield sums over worked plots)
      buildings_db        static_db    (base DB values, no pct modifiers)
      district_adjacency  direct       (exported per district)
      trade_routes        direct       (exported per route)
      unattributed        reconstructed (city total minus the above —
                          population/amenity/policy/wonder modifiers land
                          here; base game exposes no per-source API for them)

    Returns None when the Lua never sent yield_sources (query failed or
    plot:GetYield absent) — never a fabricated breakdown.
    """
    ys = city.get("yield_sources")
    if not ys:
        return None
    adj = {k: 0.0 for k in _YIELD_KEYS}
    for d in city.get("districts") or []:
        for yk, v in (d.get("adjacency") or {}).items():
            lk = str(yk).lower()
            if lk in adj:
                adj[lk] += v
    trade = {k: 0.0 for k in _YIELD_KEYS}
    for t in city.get("trade_routes") or []:
        for yk, v in (t.get("yields") or {}).items():
            lk = str(yk).lower()
            if lk in trade:
                trade[lk] += v
    totals = city.get("yields") or {}
    out: dict[str, Any] = {}
    for k in _YIELD_KEYS:
        parts = {
            "worked_tiles": {"value": (ys.get("worked_tiles") or {}).get(k, 0.0), "source": "direct"},
            "buildings_db": {"value": (ys.get("buildings_db") or {}).get(k, 0.0), "source": "static_db"},
            "district_adjacency": {"value": adj[k], "source": "direct"},
            "trade_routes": {"value": trade[k], "source": "direct"},
        }
        attributed = sum(p["value"] for p in parts.values())
        total = totals.get(k)
        parts["unattributed"] = {
            "value": round(total - attributed, 1) if isinstance(total, (int, float)) else None,
            "source": "reconstructed",
        }
        out[k] = parts
    return out


def cs_envoy_status(cs: dict[str, Any]) -> dict[str, Any]:
    """Threshold / lead arithmetic over directly-exported envoy counts.

    Presentation math on observed data (the CS panel shows exactly this),
    tagged ``reconstructed:threshold`` so consumers know it's derived.
    Returns None-bearing fields when envoys_by_civ wasn't readable.
    """
    mine = cs.get("envoys_sent")
    out: dict[str, Any] = {
        "thresholds_met": [t for t in (1, 3, 6) if isinstance(mine, int) and mine >= t],
        "source": "reconstructed:threshold",
    }
    ebc = cs.get("envoys_by_civ")
    if not isinstance(ebc, dict) or not ebc:
        out.update({"leader_id": None, "leader_envoys": None,
                    "needed_to_lead": None, "tied_for_lead": None})
        return out
    top = max(ebc.values())
    leaders = [pid for pid, n in ebc.items() if n == top]
    mine_n = mine if isinstance(mine, int) else 0
    out["leader_envoys"] = top
    out["leader_id"] = leaders[0] if len(leaders) == 1 else None  # None on tie
    out["tied_for_lead"] = mine_n == top and len(leaders) > 1
    out["needed_to_lead"] = 0 if (mine_n == top and len(leaders) == 1) else top - mine_n + 1
    return out


def resources_inventory(cities: list[dict[str, Any]] | None) -> list[dict[str, Any]] | None:
    """Aggregate per-city CITYRES observations into one owned-resource
    inventory (Reports → Resources).  Pure reorganization — every plot
    was directly observed as owned; None when cities weren't readable."""
    if cities is None:
        return None
    agg: dict[str, dict[str, Any]] = {}
    for c in cities:
        for r in c.get("resources") or []:
            a = agg.setdefault(
                r.get("type", "?"),
                {
                    "type": r.get("type"),
                    "class": r.get("class"),
                    "name": r.get("name"),
                    "count": 0,
                    "improved": 0,
                    "unimproved": 0,
                    "worked": 0,
                    "cities": [],
                    "source": "direct",
                },
            )
            a["count"] += 1
            a["improved" if r.get("improved") else "unimproved"] += 1
            if r.get("worked"):
                a["worked"] += 1
            cname = c.get("name")
            if cname and cname not in a["cities"]:
                a["cities"].append(cname)
    return sorted(agg.values(), key=lambda a: (a["class"], -a["count"], a["type"] or ""))


def units_by_civ(tiles: list[dict[str, Any]] | None) -> dict[str, dict[str, Any]]:
    """Aggregate the per-tile visible-unit strings (``owner:type:hp;...``)
    into a per-owner rollup.  Pure reorganization of already-fog-gated data
    — the tile strings only ever contain currently-visible units."""
    agg: dict[str, dict[str, Any]] = {}
    for t in tiles or []:
        for part in (t.get("units") or "").split(";"):
            bits = part.split(":")
            if len(bits) < 3:
                continue
            try:
                owner, hp = int(bits[0]), int(bits[2])
            except ValueError:
                continue
            a = agg.setdefault(str(owner), {"count": 0, "types": {}, "total_hp": 0})
            a["count"] += 1
            a["types"][bits[1]] = a["types"].get(bits[1], 0) + 1
            a["total_hp"] += hp
    return agg


def build_rivals(
    diplo_frag: dict[str, Any],
    map_frag: dict[str, Any],
    rel_frag: dict[str, Any],
    section_status: dict[str, str],
) -> list[dict[str, Any]] | None:
    """Merge the per-civ fragments into one ``rivals`` list (schema 1.3).

    Pure merge by player id — no inference.  Returns None when the diplo
    majors section failed (renders as QUERY FAILED, never an empty list)."""
    if section_status.get("majors_met") == "failed":
        return None
    rcities = (map_frag or {}).get("rival_cities") or []
    wrels = (rel_frag or {}).get("world_religions") or []
    out: list[dict[str, Any]] = []
    for m in diplo_frag.get("majors") or []:
        r = dict(m)
        pid = m.get("player_id")
        r["alive"] = True
        # Known cities only if the map query succeeded — otherwise None so
        # "no cities known" and "couldn't read the map" stay distinct.
        r["known_cities"] = (
            [c for c in rcities if c.get("owner") == pid]
            if section_status.get("map") != "failed"
            else None
        )
        r["religion_founded"] = next((w for w in wrels if w.get("founder") == pid), None)
        out.append(r)
    for dead in diplo_frag.get("eliminated") or []:
        if dead.get("was_major"):
            out.append(dict(dead))
    return out


# ---------------------------------------------------------------------------
# v1.7.0 Part A derivations — pure reorganization/arithmetic over data the
# snapshot already contains.  NO new engine API surface.  Every output is
# tagged with its trust tier; every static table below is base-game DB fact
# (tagged static_db) and every rule-of-thumb is tagged reconstructed with
# its rule named.  All helpers return None when their inputs are missing —
# a missing derivation must never render as a real value.
# ---------------------------------------------------------------------------

# Base-game districts that count against the population district cap
# (Districts.xml RequiresPopulation=true).  City Center, Wonder plots,
# Aqueduct and Neighborhood/Mbanza do not count.  [static_db]
SPECIALTY_DISTRICTS = {
    "DISTRICT_CAMPUS", "DISTRICT_THEATER", "DISTRICT_HOLY_SITE",
    "DISTRICT_ENCAMPMENT", "DISTRICT_COMMERCIAL_HUB", "DISTRICT_HARBOR",
    "DISTRICT_INDUSTRIAL_ZONE", "DISTRICT_ENTERTAINMENT_COMPLEX",
    # base-game unique replacements
    "DISTRICT_ACROPOLIS", "DISTRICT_HANSA", "DISTRICT_ROYAL_NAVY_DOCKYARD",
    "DISTRICT_STREET_CARNIVAL",
}


def district_capacity(city: dict[str, Any]) -> dict[str, Any] | None:
    """Districts built vs the pop/3+1 cap — the one line that prevents
    "build a Harbor" advice in a city with no free district slot.

    Reconstructed (pop/3+1 rule + static RequiresPopulation set); returns
    None when population or districts are unreadable."""
    pop = city.get("population")
    dists = city.get("districts")
    if not isinstance(pop, int) or pop < 0 or not isinstance(dists, list):
        return None
    built = sum(1 for d in dists if d.get("type") in SPECIALTY_DISTRICTS)
    cap = pop // 3 + 1
    return {
        "built": built,
        "cap": cap,
        "slots_open": max(0, cap - built),
        # pop that unlocks the next slot beyond the current cap
        "next_slot_at_pop": (cap) * 3,
        "source": "reconstructed:pop/3+1",
    }


# --- Housing (base-game static DB values) ----------------------------------
# Only entries confirmed against the base DB are listed; anything else
# (wonders, policies, beliefs) lands in the labeled `unattributed` bucket
# rather than being guessed.
HOUSING_BUILDINGS = {          # BuildingType -> housing  [static_db]
    "BUILDING_PALACE": 1,
    "BUILDING_GRANARY": 2,
    "BUILDING_SEWER": 2,
    "BUILDING_LIGHTHOUSE": 1,
    "BUILDING_BARRACKS": 1,
    "BUILDING_STABLE": 1,
    "BUILDING_UNIVERSITY": 1,
    "BUILDING_MADRASA": 1,     # Arabia's university replacement
}
HOUSING_IMPROVEMENTS_HALF = {  # +0.5 housing each  [static_db]
    "farm", "pasture", "plantation", "camp", "fishing_boats", "fishing boats",
}
# Neighborhood housing by tile appeal  [static_db]
_NEIGHBORHOOD_HOUSING = ((4, 6), (2, 5), (-1, 4), (-3, 3))  # (min appeal, housing)


def _hex_neighbors(x: int, y: int) -> list[tuple[int, int]]:
    """Civ 6 offset-hex neighbors (odd rows shifted east)."""
    if y % 2 == 0:
        d = ((1, 0), (-1, 0), (0, 1), (-1, 1), (0, -1), (-1, -1))
    else:
        d = ((1, 0), (-1, 0), (0, 1), (1, 1), (0, -1), (1, -1))
    return [(x + dx, y + dy) for dx, dy in d]


def hex_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    """Hex distance on Civ 6's odd-r offset grid (no wraparound)."""
    def _cube(x: int, y: int) -> tuple[int, int]:
        q = x - (y - (y & 1)) // 2
        return q, y
    q1, r1 = _cube(x1, y1)
    q2, r2 = _cube(x2, y2)
    dq, dr = q2 - q1, r2 - r1
    return (abs(dq) + abs(dr) + abs(dq + dr)) // 2


def _tile_appeal(tile: dict[str, Any]) -> int | None:
    extra = tile.get("extra") or ""
    for part in extra.split("/"):
        if part.startswith("A"):
            try:
                return int(part[1:])
            except ValueError:
                return None
    return None


def build_housing_breakdown(
    city: dict[str, Any], tiles_by_xy: dict[tuple[int, int], dict[str, Any]] | None
) -> dict[str, Any] | None:
    """Per-source housing reconstruction from static DB values + the city's
    observed buildings/districts/improvements/water situation.

    The sum is cross-checked against the directly-read housing total; any
    difference renders as an explicit `unattributed` bucket (wonder, policy
    and belief housing has no per-source API in the base game).  Returns
    None when the map tiles or the city rollup aren't readable — a wrong
    breakdown is worse than none."""
    total = city.get("housing")
    if not isinstance(total, int) or total < 0 or not tiles_by_xy:
        return None
    ctile = tiles_by_xy.get((city.get("x"), city.get("y")))
    if ctile is None:
        return None
    parts: list[dict[str, Any]] = []

    # Base + water (fresh water 5 / coastal 3 / neither 2) [static_db]
    fresh = "F" in (ctile.get("extra") or "").split("/")
    coastal = any(
        (tiles_by_xy.get(n) or {}).get("terrain") == "co"
        and "L" not in ((tiles_by_xy.get(n) or {}).get("extra") or "").split("/")
        for n in _hex_neighbors(city.get("x"), city.get("y"))
    )
    parts.append({"label": "base", "value": 2})
    water_base = 2
    if fresh:
        parts.append({"label": "fresh water", "value": 3})
        water_base = 5
    elif coastal:
        parts.append({"label": "coastal", "value": 1})
        water_base = 3

    # Buildings [static_db] — pillaged buildings grant nothing
    for b in city.get("buildings") or []:
        if b.get("pillaged"):
            continue
        v = HOUSING_BUILDINGS.get(b.get("type"))
        if v:
            parts.append({"label": b.get("name") or b.get("type"), "value": v})

    # Districts: Aqueduct raises water housing to 6; Neighborhood/Mbanza by appeal
    for d in city.get("districts") or []:
        if d.get("pillaged"):
            continue
        dt = d.get("type")
        if dt == "DISTRICT_AQUEDUCT":
            v = max(0, 6 - water_base)
            if v:
                parts.append({"label": "Aqueduct (water housing to 6)", "value": v})
        elif dt in ("DISTRICT_NEIGHBORHOOD", "DISTRICT_MBANZA"):
            if dt == "DISTRICT_MBANZA":
                parts.append({"label": "Mbanza", "value": 5})
            else:
                ap = _tile_appeal(tiles_by_xy.get((d.get("x"), d.get("y"))) or {})
                if ap is None:
                    continue  # appeal unreadable -> lands in unattributed
                v = next((h for mn, h in _NEIGHBORHOOD_HOUSING if ap >= mn), 2)
                parts.append({"label": f"Neighborhood (appeal {ap:+d})", "value": v})

    # Improvements: +0.5 each for farm/pasture/plantation/camp/fishing boats
    imp = (city.get("tiles_rollup") or {}).get("improvements") or {}
    half = sum(n for k, n in imp.items() if k in HOUSING_IMPROVEMENTS_HALF)
    if half:
        parts.append({"label": f"improvements ({half} x 0.5)", "value": half * 0.5})

    attributed = sum(p["value"] for p in parts)
    floored = int(attributed)  # the game floors fractional housing
    return {
        "total_reported": total,
        "parts": parts,
        "attributed": round(attributed, 1),
        "unattributed": total - floored,
        "source": "reconstructed:static_db",
    }


# --- Amenities (base-game tier table) ---------------------------------------
# Happiness tier by amenity surplus (amenities - needed)  [static_db]
def _amenity_tier(surplus: int) -> str:
    if surplus >= 3:
        return "Ecstatic"
    if surplus >= 1:
        return "Happy"
    if surplus == 0:
        return "Content"
    if surplus >= -2:
        return "Displeased"
    if surplus >= -4:
        return "Unhappy"
    if surplus >= -6:
        return "Unrest"
    return "Revolt"


def amenity_status(city: dict[str, Any]) -> dict[str, Any] | None:
    """Surplus arithmetic + next-tier distance over directly-read amenity
    counts.  The live tier label (status_labels.happiness_label) stays the
    authority when present; this adds the "how many more do I need" math."""
    have, need = city.get("amenities"), city.get("amenities_needed")
    if not isinstance(have, int) or not isinstance(need, int) or have < 0 or need < 0:
        return None
    surplus = have - need
    tier = _amenity_tier(surplus)
    to_next = None
    if tier != "Ecstatic":
        k = 1
        while k <= 12 and _amenity_tier(surplus + k) == tier:
            k += 1
        to_next = {"tier": _amenity_tier(surplus + k), "amenities_needed": k}
    return {
        "surplus": surplus,
        "tier": tier,
        "next_tier": to_next,
        "source": "reconstructed:static_db",
    }


def luxury_duplicates(resources: list[dict[str, Any]] | None) -> list[dict[str, Any]] | None:
    """Luxuries with spare (tradable) copies — one copy supplies the empire,
    the rest are trade bait.  Pure arithmetic over the directly-read
    resource amounts; None when resources weren't readable."""
    if resources is None:
        return None
    return [
        {"name": r.get("name"), "type": r.get("type"), "copies": r.get("amount"),
         "spare": r.get("amount") - 1, "source": "reconstructed"}
        for r in resources
        if r.get("class") == "LUXURY" and isinstance(r.get("amount"), int) and r.get("amount") > 1
    ]


# --- Settler advisor (reconstructed from the revealed map) ------------------
# Static base-terrain yields for a quick ring-1 read  [static_db, approx —
# resources/features add more; they're listed separately, not summed].
_TERRAIN_YIELDS = {
    "g": (2, 0), "gh": (2, 1), "gm": (0, 0),
    "p": (1, 1), "ph": (1, 2), "pm": (0, 0),
    "d": (0, 0), "dh": (0, 1), "dm": (0, 0),
    "t": (1, 0), "th": (1, 1), "tm": (0, 0),
    "s": (0, 0), "sh": (0, 1), "sm": (0, 0),
    "co": (1, 0), "oc": (1, 0),
}
_FEATURE_YIELD_BONUS = {"for": (0, 1), "jun": (1, 0), "mar": (1, 0), "fld": (2, 0), "oas": (3, 0)}

# Vanilla resource classes for map-resource strings  [static_db]
_LUXURY_RES = {
    "CITRUS", "COCOA", "COFFEE", "COTTON", "DIAMONDS", "DYES", "FURS",
    "GYPSUM", "INCENSE", "IVORY", "JADE", "MARBLE", "MERCURY", "PEARLS",
    "SALT", "SILK", "SILVER", "SPICES", "SUGAR", "TEA", "TOBACCO",
    "TRUFFLES", "WHALES", "WINE",
}
_STRATEGIC_RES = {"HORSES", "IRON", "NITER", "COAL", "OIL", "ALUMINUM", "URANIUM"}

_SETTLE_MIN_CITY_DIST = 3  # centers closer than this are illegal [static_db CITY_MIN_RANGE]


def _direction(from_x: int, from_y: int, to_x: int, to_y: int) -> str:
    dx, dy = to_x - from_x, to_y - from_y
    ns = "north" if dy > 0 else "south" if dy < 0 else ""
    ew = "east" if dx > 0 else "west" if dx < 0 else ""
    return (ns + ew) or "here"


def settler_advisor(
    units: list[dict[str, Any]] | None,
    tiles: list[dict[str, Any]] | None,
    cities: list[dict[str, Any]] | None,
    rival_cities: list[dict[str, Any]] | None,
    city_states: list[dict[str, Any]] | None,
    owned_luxury_types: set[str] | None = None,
    top_n: int = 5,
) -> dict[str, Any] | None:
    """Rank settle spots from the revealed map when a Settler exists.

    Entirely reconstructed: legality is the min-distance rule + terrain
    over *revealed* tiles (an unrevealed rival city can invalidate a spot);
    yields are base-terrain approximations.  The engine settle lens is NOT
    queried — this never claims engine truth, and says so in its note.
    Returns None when units or map weren't readable."""
    if units is None or tiles is None:
        return None
    settlers = [u for u in units if u.get("type") == "UNIT_SETTLER"]
    if not settlers:
        return None

    tiles_by_xy = {(t["x"], t["y"]): t for t in tiles}
    known_centers: list[tuple[int, int, str]] = []
    for c in cities or []:
        known_centers.append((c.get("x"), c.get("y"), c.get("name", "?")))
    for rc in rival_cities or []:
        known_centers.append((rc.get("x"), rc.get("y"), rc.get("name", "?")))
    for cs in city_states or []:
        if cs.get("x", -1) >= 0:
            known_centers.append((cs.get("x"), cs.get("y"), cs.get("civ_name", "?")))

    owned_lux = owned_luxury_types or set()
    s0 = settlers[0]
    candidates: list[dict[str, Any]] = []
    for (x, y), t in tiles_by_xy.items():
        terr = t.get("terrain") or ""
        feat = t.get("feature") or ""
        if terr in ("co", "oc") or terr.endswith("m"):
            continue
        if feat.startswith("nw:") or feat == "oas":
            continue
        if t.get("is_city") or t.get("district"):
            continue
        owner = t.get("owner") or ""
        if owner not in ("", "0"):
            continue  # foreign territory
        if any(hex_distance(x, y, cx, cy) < _SETTLE_MIN_CITY_DIST for cx, cy, _ in known_centers):
            continue

        fresh = "F" in (t.get("extra") or "").split("/")
        ring1 = [tiles_by_xy.get(n) for n in _hex_neighbors(x, y)]
        coastal = any(
            r is not None and r.get("terrain") == "co"
            and "L" not in (r.get("extra") or "").split("/")
            for r in ring1
        )
        f_sum, p_sum = 0, 0
        for r in ring1:
            if r is None:
                continue
            fy, py = _TERRAIN_YIELDS.get(r.get("terrain") or "", (0, 0))
            bf, bp = _FEATURE_YIELD_BONUS.get(r.get("feature") or "", (0, 0))
            f_sum += fy + bf
            p_sum += py + bp
        res_r2: list[dict[str, Any]] = []
        overlap = 0
        for (nx, ny), nt in tiles_by_xy.items():
            d = hex_distance(x, y, nx, ny)
            if d > 2:
                continue
            if d > 0 and (nt.get("owner") or "") == "0":
                overlap += 1
            rn = nt.get("resource") or ""
            if rn:
                cls = (
                    "luxury" if rn in _LUXURY_RES
                    else "strategic" if rn in _STRATEGIC_RES
                    else "bonus"
                )
                res_r2.append({
                    "name": rn, "class": cls, "dist": d,
                    "new_luxury": cls == "luxury" and rn not in owned_lux,
                })
        nearest = None
        my_cities = [(cx, cy, nm) for cx, cy, nm in known_centers[: len(cities or [])]]
        if my_cities:
            cx, cy, nm = min(my_cities, key=lambda c: hex_distance(x, y, c[0], c[1]))
            nearest = {"name": nm, "dist": hex_distance(x, y, cx, cy)}
        score = (
            (3 if fresh else 0) + (1 if coastal else 0)
            + 0.5 * (f_sum + p_sum)
            + sum(3 if r["new_luxury"] else 1 if r["class"] == "luxury" else 2 if r["class"] == "strategic" else 0.5 for r in res_r2)
            - 0.15 * hex_distance(x, y, s0.get("x", x), s0.get("y", y))
            - 0.1 * overlap
        )
        candidates.append({
            "x": x, "y": y, "score": round(score, 1),
            "fresh_water": fresh, "coastal": coastal,
            "ring1_food": f_sum, "ring1_production": p_sum,
            "resources_within_2": sorted(res_r2, key=lambda r: (r["dist"], r["name"])),
            "nearest_own_city": nearest,
            "dist_from_settler": hex_distance(x, y, s0.get("x", x), s0.get("y", y)),
            "direction_from_settler": _direction(s0.get("x", x), s0.get("y", y), x, y),
            "overlap_owned_tiles_r2": overlap,
        })
    candidates.sort(key=lambda c: -c["score"])
    return {
        "settlers": [{"id": s.get("id"), "x": s.get("x"), "y": s.get("y")} for s in settlers],
        "candidates": candidates[:top_n],
        "note": (
            "reconstructed from the REVEALED map only — legality is the "
            f"min-distance ({_SETTLE_MIN_CITY_DIST}) rule vs KNOWN cities; an unrevealed "
            "city can invalidate a spot; ring-1 yields are base terrain+feature "
            "approximations; directions use map coordinates (+y = north, +x = east)"
        ),
        "source": "reconstructed",
    }


def civ_accounting(
    majors_met: list[dict[str, Any]] | None,
    rivals: list[dict[str, Any]] | None,
    world_religions: list[dict[str, Any]] | None,
    meta: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Met / eliminated / possibly-unmet arithmetic (fog-safe).

    The base snapshot does not export the game's starting major count
    (map max is a capacity, not a participant count — labeled as such),
    so "unmet" stays a possibility statement plus hard evidence: a world
    religion founded by a player id we haven't met proves an unmet civ
    exists.  Never names or locates unmet civs."""
    if majors_met is None:
        return None
    met_ids = {m.get("player_id") for m in majors_met}
    dead = [r for r in (rivals or []) if not r.get("alive", True)]
    dead_ids = {r.get("player_id") for r in dead}
    evidence: list[str] = []
    for w in world_religions or []:
        fid = w.get("founder", -1)
        if fid >= 0 and fid not in met_ids and fid not in dead_ids and fid != 0:
            evidence.append(
                f"{w.get('name')} was founded by an unmet civilization (public info)"
            )
    return {
        "met_alive": len(majors_met),
        "met_alive_names": [m.get("civ_name") for m in majors_met],
        "eliminated": len(dead),
        "eliminated_names": [r.get("civ_name") for r in dead],
        "map_max_majors": (meta or {}).get("max_players") or None,
        "unmet_evidence": evidence,
        "note": (
            "starting major-civ count is not exported by the base snapshot; "
            "map_max_majors is the MAP's capacity, not the actual player count "
            "— unmet living civs may exist"
        ),
        "source": "reconstructed",
    }


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
