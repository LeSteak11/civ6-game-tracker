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


def _world_events(prev: dict[str, Any], curr: dict[str, Any]) -> list[dict[str, Any]]:
    """Observed world events between two snapshots.

    Everything here is a comparison of two legitimate observations — no
    guessing.  When a source section is None (query failed) on either
    side, that event class is skipped entirely: a failed read must never
    manufacture a "city lost" or "war ended" story.
    """
    ev: list[dict[str, Any]] = []
    p_riv, c_riv = prev.get("rivals"), curr.get("rivals")
    pr = {r.get("player_id"): r for r in p_riv} if isinstance(p_riv, list) else None
    cr = {r.get("player_id"): r for r in c_riv} if isinstance(c_riv, list) else None

    def name_of(pid: Any) -> str:
        for src in (cr or {}), (pr or {}):
            if pid in src and src[pid].get("civ_name"):
                return src[pid]["civ_name"]
        return "me" if pid == 0 else f"player {pid}"

    if pr is not None and cr is not None:
        # Eliminations
        for pid, r in cr.items():
            if not r.get("alive", True) and pr.get(pid, {}).get("alive", True):
                ev.append({"event": "eliminated", "player_id": pid, "civ": name_of(pid)})
        # Wars declared / peace made anywhere among met civs
        def _war_pairs(rmap: dict) -> set:
            pairs = set()
            for pid, r in rmap.items():
                for o in r.get("wars_with") or []:
                    pairs.add(tuple(sorted((pid, o))))
            return pairs
        pw, cw = _war_pairs(pr), _war_pairs(cr)
        for a, b in sorted(cw - pw):
            ev.append({"event": "war_declared", "between": [a, b],
                       "civs": [name_of(a), name_of(b)]})
        for a, b in sorted(pw - cw):
            # Peace only if both parties still alive — a war "ending" via
            # elimination is the elimination event, not a peace deal.
            if cr.get(a, {}).get("alive", True) and cr.get(b, {}).get("alive", True):
                ev.append({"event": "peace", "between": [a, b],
                           "civs": [name_of(a), name_of(b)]})
        # Government changes (only when read at valid visibility both times)
        for pid, r in cr.items():
            g, gp = r.get("government"), pr.get(pid, {}).get("government")
            if g and gp and g.get("type") != gp.get("type"):
                ev.append({"event": "government_changed", "player_id": pid,
                           "civ": name_of(pid), "from": gp.get("name"), "to": g.get("name")})
        # Sharp military swings (>=20% and >=30 points, both observed)
        for pid, r in cr.items():
            p = pr.get(pid)
            if not p or not r.get("alive", True):
                continue
            m0, m1 = p.get("military") or 0, r.get("military") or 0
            if m0 >= 30 and abs(m1 - m0) >= max(30, 0.2 * m0):
                ev.append({"event": "military_swing", "player_id": pid,
                           "civ": name_of(pid), "from": m0, "to": m1})

    # Religions founded (public list on both sides)
    p_wrel, c_wrel = prev.get("world_religions"), curr.get("world_religions")
    if isinstance(p_wrel, list) and isinstance(c_wrel, list):
        known = {w.get("type") for w in p_wrel}
        for w in c_wrel:
            if w.get("type") not in known:
                ev.append({"event": "religion_founded", "civ": name_of(w.get("founder")),
                           "religion": w.get("name")})

    # City ownership changes among revealed rival cities (matched by coords)
    p_rc, c_rc = prev.get("rival_cities"), curr.get("rival_cities")
    if isinstance(p_rc, list) and isinstance(c_rc, list):
        p_at = {(c.get("x"), c.get("y")): c for c in p_rc}
        c_at = {(c.get("x"), c.get("y")): c for c in c_rc}
        for k, c in c_at.items():
            pc = p_at.get(k)
            if pc and pc.get("owner") != c.get("owner"):
                liberated = (
                    c.get("original_owner", -1) >= 0
                    and c.get("owner") == c.get("original_owner")
                )
                ev.append({
                    "event": "city_liberated" if liberated else "city_captured",
                    "city": c.get("name"), "at": [c.get("x"), c.get("y")],
                    "from": pc.get("owner"), "to": c.get("owner"),
                    "civs": [name_of(pc.get("owner")), name_of(c.get("owner"))],
                })
        # My cities lost / captured by me (own list vs rival list)
        p_mine, c_mine = prev.get("cities"), curr.get("cities")
        if isinstance(p_mine, list) and isinstance(c_mine, list):
            mine_now = {mc.get("id") for mc in c_mine}
            for mc in p_mine:
                if mc.get("id") not in mine_now:
                    k = (mc.get("x"), mc.get("y"))
                    taker = c_at.get(k, {}).get("owner")
                    ev.append({"event": "city_lost_by_me", "city": mc.get("name"),
                               "at": [mc.get("x"), mc.get("y")],
                               "to": taker, "to_civ": name_of(taker) if taker is not None else "unknown"})
            mine_before = {mc.get("id") for mc in p_mine}
            for mc in c_mine:
                if mc.get("id") not in mine_before and (mc.get("x"), mc.get("y")) in p_at:
                    prev_owner = p_at[(mc.get("x"), mc.get("y"))].get("owner")
                    ev.append({"event": "city_captured_by_me", "city": mc.get("name"),
                               "at": [mc.get("x"), mc.get("y")],
                               "from": prev_owner, "from_civ": name_of(prev_owner)})

    # Suzerain changes on met city-states
    p_cs, c_cs = prev.get("city_states_met"), curr.get("city_states_met")
    if isinstance(p_cs, list) and isinstance(c_cs, list):
        p_by = {c.get("player_id"): c for c in p_cs}
        for c in c_cs:
            pc = p_by.get(c.get("player_id"))
            if pc and pc.get("suzerain") != c.get("suzerain"):
                ev.append({"event": "suzerain_changed", "city_state": c.get("civ_name"),
                           "from": pc.get("suzerain"), "to": c.get("suzerain")})
    return ev


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
        # Full lists — any display trimming happens at render time, with a
        # label; the JSON delta is never silently truncated.
        "damaged": damaged,
        "healed": healed,
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

    # World events — observed changes in rival/city-state state.  Strictly
    # prev-vs-curr comparison of fog-legitimate data; a failed section on
    # either side suppresses that event class rather than fabricating one.
    d["world_events"] = _world_events(prev, curr)

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
