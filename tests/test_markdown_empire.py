"""Regression tests for the EMPIRE renderer in coach/markdown.py.

Bug history: render_markdown() bound the empire dict to a variable named
``e`` and later reused ``e`` as the loop variable while rendering WORLD
NEWS events.  Any snapshot whose delta carried world_events therefore
rendered EMPIRE from the last world-event dict — score None, gold 0,
science 0, military None — while the JSON (and section_status.empire=ok)
were perfectly fine.  Turns without world events rendered correctly,
which made the corruption look intermittent.
"""

from civ_mcp.coach.markdown import render_markdown


def _empire() -> dict:
    # Values mirror the real turn-313 capture that exposed the bug.
    return {
        "score": 1250,
        "gold": 1075.5,
        "gold_net": 42.3,
        "gold_yield": 60.1,
        "gold_maint": 17.8,
        "science": 283.3,
        "culture": 155.2,
        "faith": 890.0,
        "faith_yield": 31.5,
        "tourism": 48.0,
        "military": 602,
        "techs_done": 55,
        "civics_done": 42,
        "num_cities": 11,
        "num_units": 30,
        "total_pop": 97,
        "trade_used": 8,
        "trade_cap": 9,
        "explored_land": 800,
        "total_land": 1200,
    }


def _snapshot() -> dict:
    return {
        "schema": "coach-snapshot/1.3",
        "coach_version": "1.7.1",
        "section_status": {"header": "ok", "empire": "ok"},
        "meta": {
            "turn": 313,
            "civ_name": "Egypt",
            "leader_name": "Cleopatra",
            "year": "1500 AD",
            "era": "Renaissance Era",
            "difficulty": "Chieftain",
            "speed": "Standard",
            "map_size": "Standard",
            "map_type": "Continents",
        },
        "empire": _empire(),
    }


def _delta_with_world_events() -> dict:
    return {
        "world_events": [
            {"event": "military_swing", "civ": "Sumeria", "from": 400, "to": 640},
            {"event": "suzerain_changed", "city_state": "Kabul", "from": "none", "to": "Sumeria"},
        ]
    }


def _empire_section(md: str) -> str:
    body = md.split("## EMPIRE", 1)[1]
    return body.split("\n## ", 1)[0]


def test_empire_survives_world_events():
    """WORLD NEWS rendering must not shadow the empire dict."""
    md = render_markdown(_snapshot(), _delta_with_world_events())

    # World news actually rendered (the trigger condition for the bug).
    assert "## WORLD NEWS" in md
    assert "Sumeria military 400 → 640" in md
    assert "Kabul suzerain: none → Sumeria" in md

    emp = _empire_section(md)
    assert "**score:** 1250" in emp
    assert "**gold:** 1076 (net +42.3" in emp  # 1075.5 rounds to 1076 with :.0f
    assert "**science:** 283.3/turn" in emp
    assert "**military:** 602" in emp
    assert "11 / 30 / 97" in emp  # cities / units / pop
    assert "**trade routes:** 8/9" in emp

    # The exact corruption signature of the bug:
    assert "None" not in emp
    assert "score:** None" not in md


def test_empire_unchanged_with_and_without_world_events():
    """The EMPIRE section must be byte-identical whether or not the delta
    carries world events."""
    quiet = render_markdown(_snapshot(), {})
    noisy = render_markdown(_snapshot(), _delta_with_world_events())
    assert _empire_section(quiet) == _empire_section(noisy)


def test_malformed_empire_dict_renders_query_failed_not_zeros():
    """A nonempty dict that isn't empire data (e.g. a world-event dict)
    must render as a failure, never as plausible zeros."""
    snap = _snapshot()
    snap["empire"] = {"event": "military_swing", "civ": "Sumeria", "from": 400, "to": 640}
    md = render_markdown(snap, {})
    emp = _empire_section(md)
    assert "QUERY FAILED — empire (malformed payload" in emp
    assert "score" in emp.lower() and "missing" in emp  # names the missing keys
    assert "**gold:** 0" not in emp
    assert "**science:** 0.0/turn" not in emp
