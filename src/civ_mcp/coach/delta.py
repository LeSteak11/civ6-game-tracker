"""Compute a compact delta between the previous and current snapshot.

Delta is a top-of-report summary — not a replacement for the full state.  We
only surface changes that matter for one-turn coaching:

    - newly revealed tiles (count + first few coords)
    - new metropolises seen (majors newly met, city-states newly met)
    - visible enemies that appeared / disappeared
    - units born / lost / promoted / upgraded
    - cities that grew, starved, or completed production
    - research / civic progress changes
    - resource stockpile deltas
    - score / military delta
"""

from __future__ import annotations

from typing import Any


def _by_id(items: list[dict[str, Any]], key: str = "id") -> dict[int, dict[str, Any]]:
    return {int(x.get(key)): x for x in items if key in x}


def _tile_key(t: dict[str, Any]) -> tuple[int, int]:
    return int(t.get("x", -1)), int(t.get("y", -1))


def compute_delta(prev: dict[str, Any] | None, curr: dict[str, Any]) -> dict[str, Any]:
    if not prev:
        return {"first_snapshot": True}
    d: dict[str, Any] = {"first_snapshot": False}
    # Turn advance
    prev_turn = prev.get("meta", {}).get("turn", 0)
    curr_turn = curr.get("meta", {}).get("turn", 0)
    d["turns_elapsed"] = curr_turn - prev_turn

    # Empire deltas
    pe, ce = prev.get("empire", {}) or {}, curr.get("empire", {}) or {}
    for key in (
        "score",
        "gold",
        "gold_net",
        "science",
        "culture",
        "faith",
        "tourism",
        "military",
        "techs_done",
        "civics_done",
        "num_cities",
        "num_units",
        "total_pop",
        "explored_land",
    ):
        if key in pe or key in ce:
            d.setdefault("empire_delta", {})[key] = (ce.get(key, 0) or 0) - (pe.get(key, 0) or 0)

    # Newly revealed tiles
    prev_tiles = {_tile_key(t) for t in prev.get("tiles", [])}
    curr_tiles = {_tile_key(t): t for t in curr.get("tiles", [])}
    new_keys = [k for k in curr_tiles if k not in prev_tiles]
    d["tiles_newly_revealed"] = {
        "count": len(new_keys),
        "sample": [{"x": k[0], "y": k[1], "terrain": curr_tiles[k].get("terrain")} for k in new_keys[:15]],
    }

    # Units — matched by ID
    prev_units = _by_id(prev.get("units", []))
    curr_units = _by_id(curr.get("units", []))
    born = [u for uid, u in curr_units.items() if uid not in prev_units]
    lost = [u for uid, u in prev_units.items() if uid not in curr_units]
    promoted, upgraded, moved, damaged, healed = [], [], [], [], []
    for uid, u in curr_units.items():
        pu = prev_units.get(uid)
        if not pu:
            continue
        if u.get("promotions_held", 0) > pu.get("promotions_held", 0):
            promoted.append(u)
        if u.get("type") != pu.get("type"):
            upgraded.append({"from": pu.get("type"), "to": u.get("type"), "id": uid})
        if (u.get("x"), u.get("y")) != (pu.get("x"), pu.get("y")):
            moved.append({"id": uid, "type": u.get("type"), "from": (pu.get("x"), pu.get("y")), "to": (u.get("x"), u.get("y"))})
        if u.get("hp", 0) < pu.get("hp", 0):
            damaged.append({"id": uid, "type": u.get("type"), "hp": u.get("hp"), "prev_hp": pu.get("hp")})
        if u.get("hp", 0) > pu.get("hp", 0):
            healed.append({"id": uid, "type": u.get("type"), "hp": u.get("hp"), "prev_hp": pu.get("hp")})
    d["units_delta"] = {
        "born": [{"id": u.get("id"), "type": u.get("type"), "at": (u.get("x"), u.get("y"))} for u in born],
        "lost": [{"id": u.get("id"), "type": u.get("type"), "at": (u.get("x"), u.get("y"))} for u in lost],
        "promoted": [{"id": u.get("id"), "type": u.get("type")} for u in promoted],
        "upgraded": upgraded,
        "moved_count": len(moved),
        "damaged": damaged[:10],
        "healed": healed[:10],
    }

    # Cities
    prev_cities = _by_id(prev.get("cities", []))
    curr_cities = _by_id(curr.get("cities", []))
    grew, starved, completed = [], [], []
    for cid, c in curr_cities.items():
        pc = prev_cities.get(cid)
        if not pc:
            continue
        if c.get("population", 0) > pc.get("population", 0):
            grew.append({"id": cid, "name": c.get("name"), "pop": c.get("population")})
        if c.get("population", 0) < pc.get("population", 0):
            starved.append({"id": cid, "name": c.get("name"), "pop": c.get("population")})
        p_prod = pc.get("production", {}) or {}
        c_prod = c.get("production", {}) or {}
        if p_prod.get("type") != c_prod.get("type") and p_prod.get("type") not in ("", "nothing"):
            completed.append(
                {"id": cid, "name": c.get("name"), "completed": p_prod.get("type"), "now_making": c_prod.get("type")}
            )
    d["cities_delta"] = {"grew": grew, "starved": starved, "production_completed": completed}

    # Resources
    prev_res = {r["type"]: r.get("amount", 0) for r in prev.get("resources", [])}
    curr_res = {r["type"]: r.get("amount", 0) for r in curr.get("resources", [])}
    res_delta = {}
    for k in set(prev_res) | set(curr_res):
        delta = curr_res.get(k, 0) - prev_res.get(k, 0)
        if delta != 0:
            res_delta[k] = delta
    d["resources_delta"] = res_delta

    # Diplomacy — newly met
    prev_maj = {m["player_id"] for m in prev.get("majors_met", [])}
    curr_maj = {m["player_id"] for m in curr.get("majors_met", [])}
    prev_cs = {c["player_id"] for c in prev.get("city_states_met", [])}
    curr_cs = {c["player_id"] for c in curr.get("city_states_met", [])}
    d["diplo_delta"] = {
        "newly_met_majors": [m for m in curr.get("majors_met", []) if m["player_id"] not in prev_maj],
        "newly_met_city_states": [
            c for c in curr.get("city_states_met", []) if c["player_id"] not in prev_cs
        ],
        "new_wars": [
            m["civ_type"]
            for m in curr.get("majors_met", [])
            if m.get("at_war")
            and not next((p for p in prev.get("majors_met", []) if p["player_id"] == m["player_id"] and p.get("at_war")), None)
        ],
    }
    return d
