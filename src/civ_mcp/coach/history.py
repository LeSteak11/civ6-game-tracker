"""Per-game rival history — the archive's memory of the known world.

Maintained alongside each game folder (see ``archive.py``):

    games/game-NNN_<civ>/
        rivals.json    — per-player observation timeline, one entry per
                         turn a snapshot was taken (last capture on a turn
                         wins).  Values are what was legitimately observed
                         at that moment; a civ under fog simply keeps its
                         last-known entries.
        events.json    — append-only observed world events (city captures,
                         eliminations, wars, suzerain flips, ...), each
                         stamped with the turn it was noticed on.

Everything recorded here is copied from snapshots or from the delta
layer's prev-vs-curr comparisons — this module derives nothing new.
Stdlib only, like ``archive.py``, so the regression suite can exercise it
without the FireTuner stack.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)


def _load(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:  # noqa: BLE001 — corrupt history must not kill capture
        log.warning("Could not parse %s — starting fresh", path, exc_info=True)
        return default


def _timeline_entry(rival: dict[str, Any], turn: int) -> dict[str, Any]:
    ps = rival.get("public_stats") or {}
    kc = rival.get("known_cities")
    return {
        "turn": turn,
        "alive": rival.get("alive", True),
        "score": rival.get("score"),
        "military": rival.get("military"),
        "techs": ps.get("techs"),
        "civics": ps.get("civics"),
        "tourism": ps.get("tourism"),
        "cities_known": len(kc) if isinstance(kc, list) else None,
        "wars_with": rival.get("wars_with"),
        "government": (rival.get("government") or {}).get("type"),
        "suzerain_of": None,  # majors only; reserved
    }


def _cs_timeline_entry(cs: dict[str, Any], turn: int) -> dict[str, Any]:
    return {
        "turn": turn,
        "suzerain": cs.get("suzerain"),
        "envoys_by_civ": cs.get("envoys_by_civ"),
        "at_war_with_me": cs.get("at_war"),
    }


def update_history(
    game_dir: Path, snap: dict[str, Any], world_events: list[dict[str, Any]] | None
) -> None:
    """Append this capture's observations to the game's history files.

    Safe to call on every capture: the last capture on a given turn
    replaces that turn's timeline entries (so same-turn revisions don't
    duplicate), and an empty event list appends nothing.
    """
    meta = snap.get("meta") or {}
    turn = meta.get("turn")
    if not isinstance(turn, int) or turn <= 0:
        return  # no trusted turn — same rule as the archive itself

    game_dir = Path(game_dir)
    rivals_path = game_dir / "rivals.json"
    events_path = game_dir / "events.json"

    # ---- rivals.json timeline -------------------------------------------
    hist = _load(rivals_path, {"majors": {}, "city_states": {}})
    majors = hist.setdefault("majors", {})
    for r in snap.get("rivals") or []:
        pid = str(r.get("player_id"))
        rec = majors.setdefault(
            pid,
            {
                "civ_type": r.get("civ_type"),
                "civ_name": r.get("civ_name"),
                "leader_name": r.get("leader_name"),
                "timeline": [],
            },
        )
        # Keep identity fresh (e.g. name resolved later than first met)
        for k in ("civ_type", "civ_name", "leader_name"):
            if r.get(k):
                rec[k] = r.get(k)
        tl = rec.setdefault("timeline", [])
        entry = _timeline_entry(r, turn)
        if tl and tl[-1].get("turn") == turn:
            tl[-1] = entry
        else:
            tl.append(entry)
    city_states = hist.setdefault("city_states", {})
    for c in snap.get("city_states_met") or []:
        pid = str(c.get("player_id"))
        rec = city_states.setdefault(
            pid,
            {"civ_name": c.get("civ_name"), "cs_type": c.get("cs_type"), "timeline": []},
        )
        tl = rec.setdefault("timeline", [])
        entry = _cs_timeline_entry(c, turn)
        if tl and tl[-1].get("turn") == turn:
            tl[-1] = entry
        else:
            tl.append(entry)
    with rivals_path.open("w", encoding="utf-8") as f:
        json.dump(hist, f, indent=2)

    # ---- events.json ----------------------------------------------------
    if world_events:
        events = _load(events_path, [])
        for e in world_events:
            events.append({"turn": turn, **e})
        with events_path.open("w", encoding="utf-8") as f:
            json.dump(events, f, indent=2)

    # ---- gossip.json -----------------------------------------------------
    # Append-only, deduped on (about, turn, text): the in-game report
    # scrolls, this file doesn't.  first_seen = the capture turn on which
    # the entry first appeared.
    snap_gossip = snap.get("gossip")
    if isinstance(snap_gossip, list) and snap_gossip:
        gossip_path = game_dir / "gossip.json"
        stored = _load(gossip_path, [])
        seen = {(g.get("about"), g.get("turn"), g.get("text")) for g in stored}
        added = 0
        for g in snap_gossip:
            key = (g.get("about"), g.get("turn"), g.get("text"))
            if key not in seen:
                seen.add(key)
                stored.append({**g, "first_seen": turn})
                added += 1
        if added:
            with gossip_path.open("w", encoding="utf-8") as f:
                json.dump(stored, f, indent=2)
