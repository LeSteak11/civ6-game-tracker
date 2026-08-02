"""GAME PACK builder — the whole game as one uploadable Markdown file.

Reads one game folder under ``output/games/`` and writes ``GAME-PACK.md``
into that same folder: a single file an AI chat can digest without any
other upload.

Pack contents, in order:

1. Coverage header  — identity, turn span, capture density, gaps, and a
   loud schema-drift warning when the archive spans coach versions.
2. Your timeline    — one row per captured turn, mined from the snapshot
                      JSONs (highest revision per turn wins).
3. Rival timelines  — every met major + city-state suzerain history.
4. Master chronology— gossip.json + events.json merged and turn-sorted.
5. Your narrative   — the CHANGES / WORLD NEWS blocks of every turn .md.
6. Final state      — latest.md verbatim.

Design rules (AGENTS.md applies):

* **Read-only.**  Nothing here mutates the archive; snapshots are opened
  and closed, never rewritten.
* **Never let the pack lie.**  A section that was not read renders ``?``
  — never ``0``, never blank.  The ``-1`` / ``-999`` unknown sentinels
  from the collector are translated to ``?`` on the way in.
* **Every trim is labelled.**  If the budget forces a cut, the coverage
  header says exactly what was dropped and how much.
* **Stdlib only**, like ``archive.py`` and ``history.py``, so
  ``scripts/regress.py`` can exercise it with no FireTuner, no game
  running, and no third-party packages.

Usage::

    python scripts/make_game_pack.py                  # numbered menu
    python scripts/make_game_pack.py --game game-001_egypt
    python scripts/make_game_pack.py --newest
    python scripts/make_game_pack.py --lean           # also GAME-PACK-LEAN.md
    python scripts/make_game_pack.py --budget 600000
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

PACK_FORMAT = "game-pack/1.0"

#: Default character budget.  Deliberately generous — a 396-turn archive
#: lands around 475k, so nothing trims in practice.  The budget exists as a
#: safety net for archives far larger than anything seen so far, not as a
#: shaping constraint.
DEFAULT_BUDGET = 600_000

#: Lean variant: drops the revealed-map dump and the verbatim final state.
LEAN_BUDGET = 150_000

#: Values the collector uses to mean "not readable".  Rendered as ``?``.
UNKNOWN_SENTINELS = (-1, -999)

#: H2 headers lifted out of each turn .md for the narrative digest.
NARRATIVE_HEADERS = ("CHANGES SINCE LAST SNAPSHOT", "WORLD NEWS")

#: Dropped from latest.md in the lean pack (thousands of tile lines).
BULK_HEADERS = ("REVEALED MAP",)

SNAPSHOT_RE = re.compile(r"^turn-(\d+)_r(\d+)\.(json|md)$")


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------


def _load_json(path: Path, default: Any = None) -> Any:
    """Read JSON, returning ``default`` on any failure.

    A corrupt snapshot must never abort a pack build — the coverage header
    reports it instead.
    """
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:  # noqa: BLE001 — corrupt file is data, not a crash
        return default


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001
        return ""


def _num(value: Any, digits: int = 0) -> str:
    """Render a number, or ``?`` when it is missing or an unknown sentinel."""
    if value is None:
        return "?"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (int, float)):
        if value in UNKNOWN_SENTINELS:
            return "?"
        if digits == 0:
            return str(int(round(value)))
        return f"{value:.{digits}f}"
    text = str(value).strip()
    return text or "?"


def _plural(n: int, singular: str, plural: str | None = None) -> str:
    """``3 captures`` / ``1 capture`` — the pack is read by humans too."""
    return f"{n} {singular if n == 1 else (plural or singular + 's')}"


def _dig(obj: Any, *path: str) -> Any:
    for key in path:
        if not isinstance(obj, dict):
            return None
        obj = obj.get(key)
    return obj


def _section_ok(snap: dict[str, Any], section: str) -> bool:
    """True when the collector marked this section readable.

    Absent status is treated as OK — old schemas (coach-snapshot/1.2) did
    not always carry a full ``section_status`` map, and refusing to read
    them would silently blank the early game.
    """
    status = snap.get("section_status")
    if not isinstance(status, dict):
        return True
    return status.get(section, "ok") == "ok"


def _fmt_ranges(numbers: Iterable[int]) -> str:
    """Collapse a sorted int sequence into ``1-3, 7, 11-14`` form."""
    nums = sorted(set(numbers))
    if not nums:
        return ""
    parts: list[str] = []
    start = prev = nums[0]
    for n in nums[1:]:
        if n == prev + 1:
            prev = n
            continue
        parts.append(str(start) if start == prev else f"{start}-{prev}")
        start = prev = n
    parts.append(str(start) if start == prev else f"{start}-{prev}")
    return ", ".join(parts)


def _split_md_sections(text: str) -> dict[str, str]:
    """Split a snapshot .md into ``{H2 title: body}``.

    Header text is matched verbatim against ``## `` lines so a renamed
    section shows up as missing rather than as silently empty content.
    """
    sections: dict[str, str] = {}
    current: str | None = None
    buf: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            if current is not None:
                sections[current] = "\n".join(buf).strip()
            current = line[3:].strip()
            buf = []
        elif current is not None:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf).strip()
    return sections


def _strip_md_sections(text: str, drop: Iterable[str]) -> tuple[str, int]:
    """Remove named H2 sections from a .md, returning (text, chars_dropped)."""
    drop_set = {d.strip().upper() for d in drop}
    out: list[str] = []
    skipping = False
    dropped = 0
    for line in text.splitlines(keepends=True):
        if line.startswith("## "):
            skipping = line[3:].strip().upper() in drop_set
            if skipping:
                dropped += len(line)
                out.append(f"## {line[3:].strip()}\n\n*[omitted from lean pack]*\n\n")
                continue
        if skipping:
            dropped += len(line)
            continue
        out.append(line)
    return "".join(out), dropped


# --------------------------------------------------------------------------
# Archive discovery
# --------------------------------------------------------------------------


class GameFolder:
    """One ``output/games/game-NNN_<civ>/`` directory."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.meta: dict[str, Any] = _load_json(path / "game.json", {}) or {}
        self.snapshots: dict[int, tuple[Path, Path | None]] = {}
        self._scan_snapshots()

    def _scan_snapshots(self) -> None:
        """Map turn -> (json, md) keeping only the highest revision.

        Same-turn recaptures are ``_r02``, ``_r03``…; the last one is the
        one the player actually meant, so it wins.
        """
        snap_dir = self.path / "snapshots"
        if not snap_dir.is_dir():
            return
        best: dict[int, int] = {}
        for entry in snap_dir.iterdir():
            match = SNAPSHOT_RE.match(entry.name)
            if not match:
                continue
            turn, rev = int(match.group(1)), int(match.group(2))
            if rev >= best.get(turn, -1):
                best[turn] = rev
        for turn, rev in best.items():
            stem = f"turn-{turn:04d}_r{rev:02d}"
            js = snap_dir / f"{stem}.json"
            md = snap_dir / f"{stem}.md"
            if js.exists():
                self.snapshots[turn] = (js, md if md.exists() else None)

    @property
    def turns(self) -> list[int]:
        return sorted(self.snapshots)

    @property
    def label(self) -> str:
        civ = self.meta.get("civ_name") or "?"
        leader = self.meta.get("leader_name") or "?"
        turns = self.turns
        span = f"T{turns[0]}-T{turns[-1]}" if turns else "no captures"
        return f"{self.path.name}  ({civ} / {leader}, {span}, {len(turns)} captures)"


def find_games(games_root: Path) -> list[GameFolder]:
    if not games_root.is_dir():
        return []
    folders = [
        GameFolder(p)
        for p in sorted(games_root.iterdir())
        if p.is_dir() and (p / "game.json").exists()
    ]
    return folders


def choose_game(folders: list[GameFolder]) -> GameFolder | None:
    """Numbered console menu.  Returns None when the user backs out."""
    print()
    print("  Which game do you want to pack?")
    print()
    for i, folder in enumerate(folders, 1):
        print(f"    {i}. {folder.label}")
    print()
    print("    0. Cancel")
    print()
    while True:
        try:
            raw = input("  Number: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        if raw in ("0", "q", "Q", ""):
            return None
        if raw.isdigit() and 1 <= int(raw) <= len(folders):
            return folders[int(raw) - 1]
        print(f"  Enter 1-{len(folders)}, or 0 to cancel.")


# --------------------------------------------------------------------------
# Section builders
# --------------------------------------------------------------------------

#: (column header, snapshot keypath, decimal digits)
PLAYER_COLUMNS: tuple[tuple[str, tuple[str, ...], int], ...] = (
    ("Era", ("meta", "era"), 0),
    ("Score", ("empire", "score"), 0),
    ("Sci/t", ("empire", "science"), 1),
    ("Cul/t", ("empire", "culture"), 1),
    ("Gold", ("empire", "gold"), 0),
    ("Gold/t", ("empire", "gold_net"), 1),
    ("Faith", ("empire", "faith"), 0),
    ("Mil", ("empire", "military"), 0),
    ("Cities", ("empire", "num_cities"), 0),
    ("Pop", ("empire", "total_pop"), 0),
    ("Techs", ("empire", "techs_done"), 0),
    ("Civics", ("empire", "civics_done"), 0),
    ("Trade", ("empire", "trade_used"), 0),
    ("Units", ("empire", "num_units"), 0),
)


def build_player_timeline(game: GameFolder) -> tuple[str, dict[str, Any]]:
    """Mine one row per captured turn from the snapshot JSONs.

    This is the piece the on-disk history spine does not carry:
    ``rivals.json`` tracks every *rival* per turn, but nothing tracks the
    local player.  Without this the pack can chart five opponents across
    300 turns and show a single dot for the person who actually played.
    """
    rows: list[str] = []
    stats: dict[str, Any] = {"unreadable": 0, "corrupt": 0, "versions": {}}

    header = "| Turn | " + " | ".join(c[0] for c in PLAYER_COLUMNS) + " |"
    divider = "|---" * (len(PLAYER_COLUMNS) + 1) + "|"
    rows.append(header)
    rows.append(divider)

    for turn in game.turns:
        js_path, _ = game.snapshots[turn]
        snap = _load_json(js_path)
        if not isinstance(snap, dict):
            stats["corrupt"] += 1
            rows.append(f"| {turn} | " + " | ".join("?" for _ in PLAYER_COLUMNS) + " |")
            continue

        version = snap.get("coach_version") or "unknown"
        stats["versions"][version] = stats["versions"].get(version, 0) + 1

        cells: list[str] = []
        for _name, keypath, digits in PLAYER_COLUMNS:
            section = keypath[0]
            if not _section_ok(snap, section) and section != "meta":
                cells.append("?")
                stats["unreadable"] += 1
                continue
            cells.append(_num(_dig(snap, *keypath), digits))
        rows.append(f"| {turn} | " + " | ".join(cells) + " |")

    return "\n".join(rows), stats


def build_rival_timelines(rivals: dict[str, Any]) -> str:
    """Compress rivals.json into per-civ tables plus city-state history."""
    if not isinstance(rivals, dict):
        return "*rivals.json not present — no rival history in this pack.*"

    out: list[str] = []
    majors = rivals.get("majors") or {}
    if not majors:
        out.append("*No met majors recorded.*")

    for pid, rival in majors.items():
        if not isinstance(rival, dict):
            continue
        name = rival.get("civ_name") or f"player {pid}"
        leader = rival.get("leader_name") or "?"
        timeline = rival.get("timeline") or []
        out.append(f"### {name} — {leader} (player {pid})")
        out.append("")
        if not timeline:
            out.append("*No observations recorded.*")
            out.append("")
            continue

        first, last = timeline[0], timeline[-1]
        death = next((t for t in timeline if not t.get("alive", True)), None)
        summary = (
            f"First observed T{first.get('turn')}, "
            f"last observed T{last.get('turn')}, "
            f"{_plural(len(timeline), 'observation')}."
        )
        if death:
            summary += f" **Recorded as no longer alive from T{death.get('turn')}.**"
        out.append(summary)
        out.append("")

        alive_rows = [e for e in timeline if e.get("alive", True)]
        if not alive_rows:
            # Every observation is a tombstone — e.g. a civ already dead the
            # first time we met anyone who remembered them.  An empty table
            # would read as "no data"; this says what actually happened.
            out.append(
                "*No observations while alive — this civ was already gone by the "
                "time the archive starts. See the chronology for how they fell.*"
            )
            out.append("")
            continue

        out.append("| Turn | Score | Mil | Techs | Civics | Tourism | Cities | Govt | At war with |")
        out.append("|---|---|---|---|---|---|---|---|---|")
        for entry in alive_rows:
            wars = entry.get("wars_with")
            wars_txt = ", ".join(str(w) for w in wars) if isinstance(wars, list) and wars else "-"
            govt = (entry.get("government") or "").replace("GOVERNMENT_", "").replace("_", " ").title() or "?"
            out.append(
                "| {t} | {s} | {m} | {te} | {c} | {to} | {ci} | {g} | {w} |".format(
                    t=entry.get("turn"),
                    s=_num(entry.get("score")),
                    m=_num(entry.get("military")),
                    te=_num(entry.get("techs")),
                    c=_num(entry.get("civics")),
                    to=_num(entry.get("tourism")),
                    ci=_num(entry.get("cities_known")),
                    g=govt,
                    w=wars_txt,
                )
            )
        out.append("")

    city_states = rivals.get("city_states") or {}
    if city_states:
        out.append("### City-states")
        out.append("")
        out.append("| City-state | Observations | Suzerain history |")
        out.append("|---|---|---|")
        for csid, cs in city_states.items():
            if not isinstance(cs, dict):
                continue
            name = cs.get("name") or cs.get("civ_name") or f"city-state {csid}"
            timeline = cs.get("timeline") or []
            flips: list[str] = []
            prev = object()
            for entry in timeline:
                suz = entry.get("suzerain")
                if suz != prev:
                    flips.append(f"T{entry.get('turn')}:{suz or 'none'}")
                    prev = suz
            out.append(
                f"| {name} | {len(timeline)} | {' → '.join(flips) if flips else '-'} |"
            )
        out.append("")

    return "\n".join(out)


def build_chronology(gossip: Any, events: Any) -> tuple[str, dict[str, int]]:
    """Merge gossip + events into one turn-sorted, deduped record."""
    entries: list[tuple[int, str, str]] = []
    seen: set[tuple[int, str]] = set()
    stats = {"gossip": 0, "events": 0, "duplicates": 0}

    if isinstance(gossip, list):
        for item in gossip:
            if not isinstance(item, dict):
                continue
            turn = item.get("turn")
            text = (item.get("text") or "").strip()
            if turn is None or not text:
                continue
            key = (int(turn), text)
            if key in seen:
                stats["duplicates"] += 1
                continue
            seen.add(key)
            entries.append((int(turn), "gossip", text))
            stats["gossip"] += 1

    if isinstance(events, list):
        for item in events:
            if not isinstance(item, dict):
                continue
            turn = item.get("turn")
            kind = item.get("event")
            if turn is None or not kind:
                continue
            detail = {k: v for k, v in item.items() if k not in ("turn", "event")}
            if kind == "suzerain_changed":
                text = (
                    f"suzerain of {detail.get('city_state')}: "
                    f"{detail.get('from')} -> {detail.get('to')}"
                )
            elif kind == "military_swing":
                text = (
                    f"{detail.get('civ')} military {detail.get('from')} -> "
                    f"{detail.get('to')}"
                )
            elif kind == "government_changed":
                text = (
                    f"{detail.get('civ')} government {detail.get('from')} -> "
                    f"{detail.get('to')}"
                )
            elif kind == "religion_founded":
                text = f"{detail.get('civ')} founded {detail.get('religion')}"
            else:
                text = f"{kind} {json.dumps(detail, sort_keys=True)}"
            key = (int(turn), text)
            if key in seen:
                stats["duplicates"] += 1
                continue
            seen.add(key)
            entries.append((int(turn), "event", text))
            stats["events"] += 1

    entries.sort(key=lambda e: (e[0], e[1], e[2]))
    lines = [f"- **T{turn}** `{src}` {text}" for turn, src, text in entries]
    if not lines:
        lines = ["*No gossip or events recorded for this game.*"]
    return "\n".join(lines), stats


def build_narrative(game: GameFolder) -> tuple[list[tuple[int, str]], int]:
    """Pull the CHANGES / WORLD NEWS blocks out of every turn .md.

    Returns per-turn chunks (newest last) so the budget pass can drop
    oldest-first without re-reading anything.
    """
    chunks: list[tuple[int, str]] = []
    missing_md = 0
    for turn in game.turns:
        _, md_path = game.snapshots[turn]
        if md_path is None:
            missing_md += 1
            continue
        sections = _split_md_sections(_read_text(md_path))
        parts: list[str] = []
        for header in NARRATIVE_HEADERS:
            body = sections.get(header, "").strip()
            if body:
                parts.append(f"*{header.title()}*\n\n{body}")
        if not parts:
            continue
        chunks.append((turn, f"#### Turn {turn}\n\n" + "\n\n".join(parts) + "\n"))
    return chunks, missing_md


# --------------------------------------------------------------------------
# Pack assembly
# --------------------------------------------------------------------------


def build_pack(
    game: GameFolder,
    budget: int = DEFAULT_BUDGET,
    lean: bool = False,
) -> str:
    meta = game.meta
    turns = game.turns
    notes: list[str] = []  # every trim / anomaly, surfaced in the header

    rivals = _load_json(game.path / "rivals.json", {}) or {}
    gossip = _load_json(game.path / "gossip.json", []) or []
    events = _load_json(game.path / "events.json", []) or []
    latest_md = _read_text(game.path / "latest.md")

    player_table, player_stats = build_player_timeline(game)
    rival_block = build_rival_timelines(rivals)
    chronology, chrono_stats = build_chronology(gossip, events)
    narrative_chunks, missing_md = build_narrative(game)

    # ---- coverage facts -------------------------------------------------
    first_turn = turns[0] if turns else None
    last_turn = turns[-1] if turns else None
    gaps = (
        [t for t in range(first_turn, last_turn + 1) if t not in game.snapshots]
        if turns
        else []
    )

    gossip_turns = [g["turn"] for g in gossip if isinstance(g, dict) and g.get("turn") is not None]
    earliest_record = min(gossip_turns) if gossip_turns else None

    versions = player_stats["versions"]
    multi_version = len(versions) > 1

    header: list[str] = []
    header.append(f"# CIV 6 GAME PACK — {meta.get('civ_name', '?')} ({game.path.name})")
    header.append("")
    header.append(f"`{PACK_FORMAT}`  ·  built from the on-disk archive, no game required.")
    header.append("")
    header.append("## COVERAGE — read this before drawing conclusions")
    header.append("")
    header.append(f"- **Civ / leader:** {meta.get('civ_name', '?')} / {meta.get('leader_name', '?')}")
    header.append(
        f"- **Settings:** {meta.get('difficulty', '?')} difficulty, "
        f"{meta.get('map_type', '?')} map ({meta.get('map_size', '?')}), "
        f"{meta.get('speed', '?')} speed"
    )
    if turns:
        header.append(
            f"- **Captured turns:** T{first_turn}–T{last_turn} — "
            f"{_plural(len(turns), 'capture')} covering {len(turns)} of "
            f"{last_turn - first_turn + 1} turns in that span"
        )
    else:
        header.append("- **Captured turns:** none")

    if first_turn and first_turn > 1:
        line = (
            f"- **Turns 1–{first_turn - 1} were never captured.** Nothing about the "
            f"player's own early game is in this pack"
        )
        if earliest_record is not None and earliest_record < first_turn:
            line += (
                f"; world events are back-filled to T{earliest_record} via gossip, "
                f"but the player's own arc starts at T{first_turn}"
            )
        header.append(line + ".")

    if gaps:
        header.append(f"- **Gaps inside the captured span:** T{_fmt_ranges(gaps)}")

    if multi_version:
        version_list = ", ".join(
            f"{v} ({_plural(n, 'capture')})" for v, n in sorted(versions.items())
        )
        header.append("")
        header.append(
            "> **SCHEMA DRIFT WARNING.** This archive spans multiple coach "
            f"versions: {version_list}. Field availability and derivation "
            "changed across those versions, so a metric that appears to jump "
            "may reflect a tooling change rather than a game event. Treat "
            "cross-version comparisons with suspicion, and prefer the "
            "chronology (which is version-stable) when a curve and a record "
            "disagree."
        )
    elif versions:
        header.append(f"- **Coach version:** {', '.join(sorted(versions))}")

    if player_stats["corrupt"]:
        notes.append(
            f"{_plural(player_stats['corrupt'], 'snapshot JSON')} unreadable — rendered `?`"
        )
    if player_stats["unreadable"]:
        notes.append(
            f"{_plural(player_stats['unreadable'], 'individual metric')} came from a "
            "failed section and render `?`"
        )
    if missing_md:
        notes.append(
            f"{_plural(missing_md, 'turn')} had a .json but no .md — no narrative for those"
        )

    header.append("")
    header.append(
        f"- **Chronology:** {_plural(chrono_stats['gossip'], 'gossip entry', 'gossip entries')}"
        f" + {_plural(chrono_stats['events'], 'observed event')}"
        f" ({_plural(chrono_stats['duplicates'], 'duplicate')} removed)"
    )
    header.append(
        f"- **Narrative:** turn-by-turn blocks for {_plural(len(narrative_chunks), 'turn')}"
    )
    header.append("")
    header.append(
        "**Data trust.** `?` means the value was not readable at capture time — "
        "it never means zero. Rival figures are observations, not omniscience: "
        "a civ under fog keeps its last-known values. Judge decisions by what "
        "was visible on that turn, not by later information."
    )

    # ---- assemble -------------------------------------------------------
    def _compose(narrative: list[tuple[int, str]], final_state: str, extra: list[str]) -> str:
        body: list[str] = []
        body.append("\n".join(header + ([""] + [f"- **Note:** {n}" for n in extra] if extra else [])))
        body.append("\n---\n")
        body.append("## 1. YOUR TIMELINE\n")
        body.append(
            "One row per captured turn, mined from the snapshot archive "
            "(highest revision per turn).\n"
        )
        body.append(player_table)
        body.append("\n---\n")
        body.append("## 2. RIVAL TIMELINES\n")
        body.append(rival_block)
        body.append("\n---\n")
        body.append("## 3. MASTER CHRONOLOGY\n")
        body.append(
            "Gossip (the game's own dated record) merged with observed world "
            "events. This is the spine every conclusion should cite.\n"
        )
        body.append(chronology)
        body.append("\n---\n")
        body.append("## 4. TURN-BY-TURN NARRATIVE\n")
        if narrative:
            body.append("\n".join(chunk for _turn, chunk in narrative))
        else:
            body.append("*No narrative blocks available.*")
        body.append("\n---\n")
        body.append("## 5. FINAL STATE\n")
        body.append(final_state or "*latest.md not present.*")
        return "\n".join(body)

    if lean:
        stripped, dropped = _strip_md_sections(latest_md, BULK_HEADERS)
        notes.append(
            f"LEAN pack: revealed-map dump omitted from final state ({dropped // 1024} KB)"
        )
        pack = _compose(narrative_chunks, stripped, notes)
    else:
        pack = _compose(narrative_chunks, latest_md, notes)

    # ---- budget safety net ---------------------------------------------
    # Drop order: map dump -> narrative oldest-first -> rest of final state.
    # The timelines and chronology are never trimmed; they are the pack.
    if len(pack) > budget:
        stripped, dropped = _strip_md_sections(latest_md, BULK_HEADERS)
        notes.append(
            f"Budget {budget:,} chars exceeded — revealed-map dump dropped "
            f"from final state ({dropped // 1024} KB)"
        )
        pack = _compose(narrative_chunks, stripped, notes)
        latest_md = stripped

    if len(pack) > budget:
        kept = list(narrative_chunks)
        total = len(kept)
        while kept and len(pack) > budget:
            drop_n = max(1, len(kept) // 10)
            kept = kept[drop_n:]
            trimmed = list(notes) + [
                f"Budget {budget:,} chars exceeded — narrative trimmed "
                f"oldest-first, showing {len(kept)} of {total} turns "
                f"(from T{kept[0][0] if kept else '-'})"
            ]
            pack = _compose(kept, latest_md, trimmed)
        narrative_chunks = kept

    if len(pack) > budget:
        notes.append(
            f"Budget {budget:,} chars still exceeded — final state omitted entirely"
        )
        pack = _compose(narrative_chunks, "*Omitted to fit the budget.*", notes)

    return pack


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compile one game folder into a single uploadable GAME-PACK.md"
    )
    parser.add_argument("--game", help="game folder name, e.g. game-001_egypt")
    parser.add_argument("--newest", action="store_true", help="pick the most recent game")
    parser.add_argument("--lean", action="store_true", help="also write GAME-PACK-LEAN.md")
    parser.add_argument("--budget", type=int, default=DEFAULT_BUDGET)
    parser.add_argument("--games-root", type=Path, default=None)
    args = parser.parse_args(argv)

    games_root = args.games_root or (_repo_root() / "output" / "games")
    folders = find_games(games_root)

    if not folders:
        print(f"\n  No game folders found under {games_root}")
        print("  Capture at least one turn first, then run this again.\n")
        return 1

    if args.game:
        match = [f for f in folders if f.path.name == args.game]
        if not match:
            print(f"\n  No game folder named {args.game!r}. Available:")
            for f in folders:
                print(f"    {f.path.name}")
            print()
            return 1
        game = match[0]
    elif args.newest or len(folders) == 1:
        game = max(folders, key=lambda f: f.meta.get("last_capture_at_epoch") or 0)
        if len(folders) > 1:
            print(f"\n  Newest game: {game.path.name}")
    else:
        chosen = choose_game(folders)
        if chosen is None:
            print("\n  Cancelled.\n")
            return 0
        game = chosen

    if not game.turns:
        print(f"\n  {game.path.name} has no snapshots to pack.\n")
        return 1

    print(f"\n  Packing {game.path.name} ({len(game.turns)} captures)...")

    pack = build_pack(game, budget=args.budget, lean=False)
    out_path = game.path / "GAME-PACK.md"
    out_path.write_text(pack, encoding="utf-8")
    print(f"  Wrote {out_path}")
    print(f"        {len(pack):,} chars  (~{len(pack) // 4000}k tokens)")

    if args.lean:
        lean_pack = build_pack(game, budget=LEAN_BUDGET, lean=True)
        lean_path = game.path / "GAME-PACK-LEAN.md"
        lean_path.write_text(lean_pack, encoding="utf-8")
        print(f"  Wrote {lean_path}")
        print(f"        {len(lean_pack):,} chars  (~{len(lean_pack) // 4000}k tokens)")

    print()
    print("  Upload it to an AI chat alongside AI-GAME-ANALYSIS-INSTRUCTIONS.md.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
