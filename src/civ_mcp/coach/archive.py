"""Persistent per-game snapshot archive.

Every capture that carries a valid turn number is filed under a stable
per-game folder::

    <output>/games/game-001_egypt/
        game.json          — leader/civ/difficulty/map/speed, dates,
                             last turn, schema version, fingerprint
        latest.md          — mirror of the newest capture (paste-ready)
        latest.json        — mirror of the newest capture (full snapshot)
        snapshots/
            turn-0087_r01.md / .json
            turn-0087_r02.md / .json   — second capture on the same turn
            turn-0088_r01.md / .json

Behaviour contract (Phase 2, Task 1):

* New match           -> create the next ``game-NNN_<civ>`` folder.
* Relaunched match    -> reopen its existing folder (fingerprint match).
* New turn            -> ``turn-XXXX_r01``.
* Same-turn recapture -> next revision, ``turn-XXXX_r02`` etc.
* Identical capture   -> no new files (dedup on content hash); the latest
                         mirrors are still refreshed.
* ``latest.md`` / ``latest.json`` always mirror the newest capture.

Game identity ("the fingerprint"): primarily the read-only game + map
seeds exported by the meta query (``SEEDS`` line, schema 1.2).  When the
seeds are unavailable (``-1`` unknown sentinel) we fall back to matching
the full static config (civ, leader, difficulty, map script/size, speed,
player count, max turns) **and** require the game to have moved forward
(current turn >= the folder's last recorded turn).  That heuristic can in
principle confuse two games started with identical settings where the
newer game is replayed past the older one's last turn — with seeds
available this cannot happen.

This module is intentionally dependency-free (stdlib only) so the
regression suite can exercise it without the FireTuner stack.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Top-level snapshot keys that legitimately differ between two captures of
# an unchanged game state and therefore must not defeat deduplication.
_VOLATILE_TOP_KEYS = ("generated_at_epoch", "diagnostics")

_GAME_DIR_RE = re.compile(r"^game-(\d+)")
_REV_RE = re.compile(r"^turn-(\d{4})_r(\d{2})\.json$")

_UNKNOWN_SEED = -1


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------

def content_hash(snap: dict[str, Any]) -> str:
    """Stable hash of the *meaningful* snapshot content (volatile keys
    stripped), so back-to-back captures of an unchanged state dedup."""
    slim = {k: v for k, v in snap.items() if k not in _VOLATILE_TOP_KEYS}
    blob = json.dumps(slim, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def fingerprint(snap: dict[str, Any]) -> dict[str, Any]:
    meta = snap.get("meta") or {}
    return {
        "game_seed": meta.get("game_seed", _UNKNOWN_SEED),
        "map_seed": meta.get("map_seed", _UNKNOWN_SEED),
        "civ_type": meta.get("civ_type", ""),
        "leader_type": meta.get("leader_type", ""),
        "difficulty": meta.get("difficulty", ""),
        "map_type": meta.get("map_type", ""),
        "map_size": meta.get("map_size", ""),
        "speed": meta.get("speed", ""),
        "max_players": meta.get("max_players", 0),
        "max_turns": meta.get("max_turns", 0),
    }


def fingerprint_id(fp: dict[str, Any]) -> str:
    blob = json.dumps(fp, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


def _seeds_known(fp: dict[str, Any]) -> bool:
    return (
        fp.get("game_seed", _UNKNOWN_SEED) != _UNKNOWN_SEED
        or fp.get("map_seed", _UNKNOWN_SEED) != _UNKNOWN_SEED
    )


def _same_game(fp: dict[str, Any], stored_fp: dict[str, Any],
               snap_turn: int, stored_last_turn: int) -> bool:
    if _seeds_known(fp) and _seeds_known(stored_fp):
        return (
            fp.get("game_seed") == stored_fp.get("game_seed")
            and fp.get("map_seed") == stored_fp.get("map_seed")
            and fp.get("civ_type") == stored_fp.get("civ_type")
            and fp.get("leader_type") == stored_fp.get("leader_type")
        )
    # Seedless fallback: full static config must match AND time must not
    # have gone backwards for this folder.
    static_keys = ("civ_type", "leader_type", "difficulty", "map_type",
                   "map_size", "speed", "max_players", "max_turns")
    if any(fp.get(k) != stored_fp.get(k) for k in static_keys):
        return False
    return snap_turn >= int(stored_last_turn or 0)


def _slug(meta: dict[str, Any]) -> str:
    base = str(meta.get("civ_name") or meta.get("civ_type") or "game")
    base = base.lower().replace("civilization_", "")
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-") or "game"
    return base[:24]


# ---------------------------------------------------------------------------
# Folder resolution
# ---------------------------------------------------------------------------

def _load_game_meta(game_dir: Path) -> dict[str, Any] | None:
    p = game_dir / "game.json"
    if not p.exists():
        return None
    try:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:  # noqa: BLE001 — a corrupt game.json must not kill capture
        return None


def resolve_game_dir(
    games_root: Path, snap: dict[str, Any]
) -> tuple[Path, dict[str, Any] | None, bool]:
    """Return ``(game_dir, existing_game_meta_or_None, created)``."""
    fp = fingerprint(snap)
    turn = int((snap.get("meta") or {}).get("turn") or 0)
    games_root.mkdir(parents=True, exist_ok=True)

    candidates: list[tuple[int, Path, dict[str, Any]]] = []
    for d in sorted(games_root.iterdir()):
        if not d.is_dir():
            continue
        m = _GAME_DIR_RE.match(d.name)
        if not m:
            continue
        gm = _load_game_meta(d)
        if gm is None:
            continue
        candidates.append((int(m.group(1)), d, gm))

    for _, d, gm in candidates:
        if _same_game(fp, gm.get("fingerprint") or {}, turn, gm.get("last_turn", 0)):
            return d, gm, False

    next_n = max((n for n, _, _ in candidates), default=0) + 1
    name = f"game-{next_n:03d}_{_slug(snap.get('meta') or {})}"
    d = games_root / name
    d.mkdir(parents=True, exist_ok=True)
    return d, None, True


# ---------------------------------------------------------------------------
# Writing
# ---------------------------------------------------------------------------

@dataclass
class ArchiveResult:
    game_dir: Path
    game_id: str
    created_game: bool
    deduplicated: bool
    capture_name: str          # e.g. "turn-0087_r02" (existing name on dedup)
    md_path: Path | None       # None on dedup (no new file written)
    json_path: Path | None
    latest_md: Path
    latest_json: Path


def _next_revision(snapshots_dir: Path, turn: int) -> int:
    rev = 0
    if snapshots_dir.exists():
        for f in snapshots_dir.iterdir():
            m = _REV_RE.match(f.name)
            if m and int(m.group(1)) == turn:
                rev = max(rev, int(m.group(2)))
    return rev + 1


def write_snapshot(
    output_dir: Path, snap: dict[str, Any], md: str
) -> ArchiveResult | None:
    """Archive one capture.  Returns None when the snapshot has no trusted
    turn number (meta failed / main menu) — the caller falls back to the
    legacy flat naming; we never guess which game a turnless capture
    belongs to."""
    status = snap.get("section_status") or {}
    meta = snap.get("meta") or {}
    turn = meta.get("turn") if isinstance(meta, dict) else None
    if not (status.get("header") == "ok" and isinstance(turn, int) and turn > 0):
        return None

    games_root = Path(output_dir) / "games"
    game_dir, game_meta, created = resolve_game_dir(games_root, snap)
    snapshots_dir = game_dir / "snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    h = content_hash(snap)
    latest_md = game_dir / "latest.md"
    latest_json = game_dir / "latest.json"

    dedup = bool(game_meta) and game_meta.get("last_capture_hash") == h
    if dedup:
        capture_name = game_meta.get("last_capture_file") or f"turn-{turn:04d}_r01"
        md_path = json_path = None
    else:
        rev = _next_revision(snapshots_dir, turn)
        capture_name = f"turn-{turn:04d}_r{rev:02d}"
        json_path = snapshots_dir / f"{capture_name}.json"
        md_path = snapshots_dir / f"{capture_name}.md"
        with json_path.open("w", encoding="utf-8") as f:
            json.dump(snap, f, indent=2)
        md_path.write_text(md, encoding="utf-8")

    # Latest mirrors always track the newest capture (even on dedup the md
    # can carry a fresher CHANGES block, and refreshing is cheap).
    latest_md.write_text(md, encoding="utf-8")
    with latest_json.open("w", encoding="utf-8") as f:
        json.dump(snap, f, indent=2)

    fp = fingerprint(snap)
    now_epoch = snap.get("generated_at_epoch")
    gm = dict(game_meta or {})
    gm.update(
        {
            "game_id": game_dir.name,
            "civ_type": meta.get("civ_type", ""),
            "civ_name": meta.get("civ_name", ""),
            "leader_type": meta.get("leader_type", ""),
            "leader_name": meta.get("leader_name", ""),
            "difficulty": meta.get("difficulty", ""),
            "map_type": meta.get("map_type", ""),
            "map_size": meta.get("map_size", ""),
            "speed": meta.get("speed", ""),
            "last_turn": turn,
            "last_capture_at_epoch": now_epoch,
            "last_capture_file": capture_name,
            "last_capture_hash": h,
            "schema": snap.get("schema", ""),
            "coach_version": snap.get("coach_version", ""),
            "fingerprint": fp,
            "fingerprint_id": fingerprint_id(fp),
        }
    )
    gm.setdefault("created_at_epoch", now_epoch)
    gm.setdefault("created_turn", turn)
    with (game_dir / "game.json").open("w", encoding="utf-8") as f:
        json.dump(gm, f, indent=2)

    return ArchiveResult(
        game_dir=game_dir,
        game_id=game_dir.name,
        created_game=created,
        deduplicated=dedup,
        capture_name=capture_name,
        md_path=md_path,
        json_path=json_path,
        latest_md=latest_md,
        latest_json=latest_json,
    )
