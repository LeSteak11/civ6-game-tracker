"""Render a snapshot dict into a compact AI-readable Markdown packet.

Structure is stable across turns so the AI can diff.  A short delta block
appears at the top, followed by turn blockers, then the full state.

When a section's ``section_status`` is ``"failed"``, we render
``**QUERY FAILED — see diagnostics**`` in place of that section's content.
We never render zeros / "none selected" / empty lists that would let the
coach lie about actual live state.
"""

from __future__ import annotations

from typing import Any


def _status(snap: dict[str, Any], key: str) -> str:
    return (snap.get("section_status") or {}).get(key, "ok")


def _fail_marker(key: str, snap: dict[str, Any]) -> str:
    fails = [
        f
        for f in ((snap.get("diagnostics") or {}).get("failures") or [])
        if key.lower() in (f.get("section", "").lower())
    ]
    hint = f" ({fails[0]['message'][:120]})" if fails else ""
    return f"**QUERY FAILED — {key}{hint}**"


def _kv(label: str, value: Any) -> str:
    return f"- **{label}:** {value}"


def _delta_is_empty(d: dict[str, Any]) -> bool:
    """True when nothing materially changed since the previous snapshot.

    Covers the common case of pressing the hotkey twice on the same turn:
    reporting "turns elapsed: 0" and nothing else is noise.
    """
    if any((d.get("empire_delta") or {}).values()):
        return False
    if (d.get("tiles_newly_revealed") or {}).get("count"):
        return False
    ud = d.get("units_delta") or {}
    if any(ud.get(k) for k in ("born", "lost", "promoted", "upgraded")):
        return False
    if ud.get("moved_count"):
        return False
    cd = d.get("cities_delta") or {}
    if any(cd.get(k) for k in ("grew", "starved", "production_completed")):
        return False
    if any((d.get("resources_delta") or {}).values()):
        return False
    dd = d.get("diplo_delta") or {}
    if any(dd.get(k) for k in ("newly_met_majors", "newly_met_city_states", "new_wars")):
        return False
    return True


def _fmt_delta(d: dict[str, Any]) -> str:
    if not d:
        return "_no delta available_"
    if d.get("first_snapshot"):
        return "_first snapshot this session — no delta to show_"

    turns = d.get("turns_elapsed", 0)
    if _delta_is_empty(d):
        if turns == 0:
            return "No meaningful changes. (Same turn as the previous snapshot.)"
        return f"No meaningful changes. ({turns} turn(s) elapsed.)"

    lines: list[str] = []
    lines.append(f"- turns elapsed: {turns}")
    ed = d.get("empire_delta", {}) or {}
    if ed:
        parts = [f"{k}: {v:+}" for k, v in ed.items() if v]
        if parts:
            lines.append("- empire: " + ", ".join(parts))
    tnr = d.get("tiles_newly_revealed", {}) or {}
    if tnr.get("count"):
        sample = ", ".join(f"({t['x']},{t['y']}) {t['terrain']}" for t in tnr.get("sample", []))
        lines.append(f"- newly revealed tiles: {tnr['count']} (sample: {sample})")
    ud = d.get("units_delta", {}) or {}
    for k in ("born", "lost", "promoted", "upgraded"):
        v = ud.get(k, [])
        if v:
            lines.append(f"- units {k}: {len(v)}")
    if ud.get("moved_count"):
        lines.append(f"- units moved: {ud['moved_count']}")
    cd = d.get("cities_delta", {}) or {}
    for k in ("grew", "starved", "production_completed"):
        v = cd.get(k, [])
        if v:
            names = ", ".join(x.get("name", "?") for x in v)
            lines.append(f"- cities {k}: {names}")
    rd = d.get("resources_delta", {}) or {}
    if rd:
        parts = [f"{k}{v:+}" for k, v in rd.items() if v]
        if parts:
            lines.append("- resources: " + ", ".join(parts))
    dd = d.get("diplo_delta", {}) or {}
    if dd.get("newly_met_majors"):
        lines.append(
            "- newly met civs: "
            + ", ".join(m.get("civ_name", m.get("civ_type", "?")) for m in dd["newly_met_majors"])
        )
    if dd.get("newly_met_city_states"):
        lines.append(
            "- newly met city-states: "
            + ", ".join(c.get("civ_name", c.get("civ_type", "?")) for c in dd["newly_met_city_states"])
        )
    if dd.get("new_wars"):
        lines.append("- **new wars: " + ", ".join(dd["new_wars"]) + "**")
    return "\n".join(lines) if lines else "_no material changes_"


def render_markdown(snap: dict[str, Any], delta: dict[str, Any]) -> str:
    st = snap.get("section_status") or {}
    m = snap.get("meta") or {}
    e = snap.get("empire") or {}
    lines: list[str] = []

    # ---- Header ------------------------------------------------------------
    header_ok = st.get("header") == "ok"
    if header_ok and m:
        turn_display = m.get("turn", "?")
        header_desc = (
            f"_{m.get('civ_name', '?')} ({m.get('leader_name', '?')}) — "
            f"{m.get('year', '?')} / {m.get('era', '?')} — "
            f"{m.get('difficulty', '?')} / {m.get('speed', '?')} / "
            f"{m.get('map_size', '?')} {m.get('map_type', '?')} — "
            f"schema {snap.get('schema')} coach {snap.get('coach_version')}_"
        )
    else:
        turn_display = "UNKNOWN (meta query failed)"
        header_desc = f"_meta query failed — schema {snap.get('schema')} coach {snap.get('coach_version')}_"

    lines.append(f"# CIV6 COACH SNAPSHOT — turn {turn_display}")
    lines.append(header_desc)
    lines.append("")

    # Prominent partial-run warning if any section failed
    failed_sections = sorted(k for k, v in st.items() if v == "failed")
    if failed_sections:
        lines.append("> **PARTIAL SNAPSHOT** — one or more queries failed live:")
        lines.append(f"> `{', '.join(failed_sections)}` — see the DIAGNOSTICS section at the bottom.")
        lines.append(">")
        lines.append("> Do not treat missing/zero values below as game state; they may be query failures.")
        lines.append("")

    lines.append("## CHANGES SINCE LAST SNAPSHOT")
    lines.append(_fmt_delta(delta))
    lines.append("")

    # ---- Turn blockers ----------------------------------------------------
    blockers = snap.get("turn_blockers_summary", []) or []
    lines.append("## TURN BLOCKERS")
    if blockers:
        for b in blockers:
            lines.append(f"- {b}")
    else:
        lines.append("- (none)")
    lines.append("")

    # ---- Empire ------------------------------------------------------------
    lines.append("## EMPIRE")
    if st.get("empire") == "failed" or not e:
        lines.append("- " + _fail_marker("empire", snap))
    else:
        lines.append(_kv("score", e.get("score")))
        lines.append(
            _kv(
                "gold",
                f"{e.get('gold', 0):.0f} (net {e.get('gold_net', 0):+.1f} = "
                f"yield {e.get('gold_yield', 0):.1f} − maint {e.get('gold_maint', 0):.1f})",
            )
        )
        lines.append(_kv("science", f"{e.get('science', 0):.1f}/turn"))
        lines.append(_kv("culture", f"{e.get('culture', 0):.1f}/turn"))
        lines.append(_kv("faith", f"{e.get('faith', 0):.0f} (+{e.get('faith_yield', 0):.1f}/turn)"))
        lines.append(_kv("tourism", f"{e.get('tourism', 0):.1f}/turn"))
        lines.append(_kv("military", e.get("military")))
        lines.append(_kv("techs / civics done", f"{e.get('techs_done')} / {e.get('civics_done')}"))
        lines.append(
            _kv(
                "cities / units / pop",
                f"{e.get('num_cities')} / {e.get('num_units')} / {e.get('total_pop')}",
            )
        )
        lines.append(_kv("trade routes", f"{e.get('trade_used')}/{e.get('trade_cap')}"))
        lines.append(_kv("explored land", f"{e.get('explored_land')}/{e.get('total_land')} tiles"))
    if st.get("victories") == "failed":
        lines.append("- **enabled victories:** " + _fail_marker("victories", snap))
    else:
        vict = snap.get("victories_enabled") or []
        lines.append(_kv("enabled victories", ", ".join(vict) or "(none)"))
    lines.append("")

    # ---- Research / Civic --------------------------------------------------
    ct = snap.get("current_research")
    cc = snap.get("current_civic")
    lines.append("## RESEARCH / CIVIC")
    if st.get("current_research") == "failed" or ct is None:
        lines.append("- **tech:** " + _fail_marker("current_research", snap))
    else:
        lines.append(
            _kv(
                "tech",
                f"{ct.get('name', 'none')} {ct.get('progress', 0):.0f}/{ct.get('cost', 0):.0f} "
                f"({ct.get('turns', -1)}t) — eureka:{ct.get('boosted')}"
                + (f" [need: {ct.get('boost_desc')}]" if ct.get("boost_desc") and not ct.get("boosted") else ""),
            )
        )
    if st.get("current_civic") == "failed" or cc is None:
        lines.append("- **civic:** " + _fail_marker("current_civic", snap))
    else:
        lines.append(
            _kv(
                "civic",
                f"{cc.get('name', 'none')} {cc.get('progress', 0):.0f}/{cc.get('cost', 0):.0f} "
                f"({cc.get('turns', -1)}t) — inspiration:{cc.get('boosted')}"
                + (f" [need: {cc.get('boost_desc')}]" if cc.get("boost_desc") and not cc.get("boosted") else ""),
            )
        )
    lines.append("")

    # ---- Available techs / civics -----------------------------------------
    def _sort_avail(a):
        return sorted(a, key=lambda x: (x.get("turns") if x.get("turns", -1) >= 0 else 999, x.get("cost", 0)))

    if st.get("techs_available") == "failed":
        lines.append("### TECHS AVAILABLE")
        lines.append(_fail_marker("techs_available", snap))
        lines.append("")
    else:
        tavail = snap.get("techs_available") or []
        if tavail:
            lines.append("### TECHS AVAILABLE (up to 10, sorted by turns)")
            for t in _sort_avail(tavail)[:10]:
                flag = "★" if t.get("boosted") else ""
                lines.append(
                    f"- {t.get('name')} {flag} — {t.get('cost', 0):.0f}sci ({t.get('turns')}t) "
                    f"— unlocks: {t.get('unlocks') or '—'}"
                    + (f" — boost: {t.get('boost_desc')}" if t.get("boost_desc") and not t.get("boosted") else "")
                )
            lines.append("")
    if st.get("civics_available") == "failed":
        lines.append("### CIVICS AVAILABLE")
        lines.append(_fail_marker("civics_available", snap))
        lines.append("")
    else:
        cavail = snap.get("civics_available") or []
        if cavail:
            lines.append("### CIVICS AVAILABLE (up to 10, sorted by turns)")
            for c in _sort_avail(cavail)[:10]:
                flag = "★" if c.get("boosted") else ""
                lines.append(
                    f"- {c.get('name')} {flag} — {c.get('cost', 0):.0f}cul ({c.get('turns')}t) "
                    f"— unlocks: {c.get('unlocks') or '—'}"
                    + (f" — inspiration: {c.get('boost_desc')}" if c.get("boost_desc") and not c.get("boosted") else "")
                )
            lines.append("")

    # ---- Resources --------------------------------------------------------
    lines.append("## RESOURCES")
    if st.get("resources") == "failed":
        lines.append("- " + _fail_marker("resources", snap))
    else:
        res = snap.get("resources") or []
        strat = [r for r in res if r.get("class") == "STRATEGIC"]
        lux = [r for r in res if r.get("class") == "LUXURY"]
        if strat:
            lines.append("- **strategic:** " + ", ".join(f"{r.get('amount')} {r.get('name')}" for r in strat))
        else:
            lines.append("- strategic: none")
        if lux:
            lines.append(
                "- **luxuries:** "
                + ", ".join(
                    (f"{r.get('amount')}× " if r.get("amount", 0) > 1 else "") + r.get("name", "?") for r in lux
                )
            )
        else:
            lines.append("- luxuries: none")
    lines.append("")

    # ---- Government / policies -------------------------------------------
    lines.append("## GOVERNMENT & POLICIES")
    g = snap.get("government")
    if st.get("government") == "failed" or g is None:
        lines.append("- " + _fail_marker("government", snap))
    else:
        lines.append(
            _kv(
                "government",
                f"{g.get('name', 'none')} — {g.get('slots_open', 0)} open slot(s) — "
                f"free change avail: {g.get('free_change_available')}",
            )
        )
    if st.get("policy_slots") == "failed":
        lines.append("- **slotted:** " + _fail_marker("policy_slots", snap))
    else:
        slots = snap.get("policy_slots") or []
        if slots:
            lines.append("- **slotted:**")
            for s in slots:
                lines.append(f"    - `{s.get('slot_name'):8}` {s.get('policy_name')}")
    if st.get("policy_available") == "failed":
        lines.append("- **available:** " + _fail_marker("policy_available", snap))
    else:
        avail = snap.get("policy_available") or []
        if avail:
            lines.append(f"- **available (unslotted):** {len(avail)} card(s)")
            for a in avail[:20]:
                lines.append(f"    - `{a.get('slot'):8}` {a.get('name')}")
            if len(avail) > 20:
                lines.append(f"    - ...and {len(avail) - 20} more (see JSON)")
    lines.append("")

    # ---- Great people -----------------------------------------------------
    if st.get("great_people") == "failed":
        lines.append("## GREAT PEOPLE")
        lines.append(_fail_marker("great_people", snap))
        lines.append("")
    else:
        gp = snap.get("great_people") or []
        if gp:
            lines.append("## GREAT PEOPLE")
            for gpe in gp:
                cand = f" — candidate: {gpe.get('candidate')}" if gpe.get("candidate") else ""
                pat = f", patronize: {gpe.get('patronize_cost')}faith" if gpe.get("patronize_cost", -1) > 0 else ""
                # -1 is the "could not read" sentinel.  Never print 0, which
                # would read as "free to recruit".
                nc = gpe.get("next_cost", -1)
                cost_str = f"{nc}" if isinstance(nc, (int, float)) and nc > 0 else "unknown"
                lines.append(
                    f"- **{gpe.get('class')}** {gpe.get('points'):.0f}pts (+{gpe.get('per_turn'):.1f}/turn) "
                    f"— next recruit cost {cost_str}{cand}{pat}"
                )
            lines.append("")

    # ---- Religion ---------------------------------------------------------
    lines.append("## RELIGION")
    if st.get("religion") == "failed" or snap.get("religion") is None:
        lines.append("- " + _fail_marker("religion", snap))
    else:
        r = snap.get("religion") or {}
        pan = r.get("pantheon", {}) or {}
        rel = r.get("religion")
        lines.append(f"- pantheon: {pan.get('name', 'none')} ({pan.get('description') or '—'})")
        if rel:
            lines.append(f"- founded: {rel.get('name')} ({rel.get('type')})")
            for b in r.get("beliefs", []):
                lines.append(f"    - {b.get('class', '?')}: {b.get('name')} — {b.get('description') or '—'}")
        else:
            lines.append("- founded religion: none")
        if r.get("can_found_pantheon"):
            lines.append("- **pantheon available to found**")
    lines.append("")

    # ---- Cities -----------------------------------------------------------
    if st.get("cities") == "failed":
        lines.append("## CITIES")
        lines.append(_fail_marker("cities", snap))
        lines.append("")
    else:
        cities = snap.get("cities") or []
        lines.append(f"## CITIES ({len(cities)})")
        for c in cities:
            cap = " [CAP]" if c.get("is_capital") else ""
            y = c.get("yields", {}) or {}
            prod = c.get("production", {}) or {}
            defense = c.get("defense", {}) or {}
            grow_str = (
                f"{c.get('turns_to_growth')}t"
                if c.get("turns_to_growth", -1) >= 0
                else f"STARVE {c.get('turns_to_starvation')}t"
                if c.get("turns_to_starvation", -1) >= 0
                else "-"
            )
            lines.append(f"### {c.get('name')}{cap} @ ({c.get('x')},{c.get('y')})")
            lines.append(
                f"- pop {c.get('population')} | grow {grow_str} (food{c.get('food_surplus'):+.1f}) | "
                f"hous {c.get('housing')} | amen {c.get('amenities')}/{c.get('amenities_needed')} | "
                f"happ {c.get('happiness')} | border+{c.get('border_expansion_turns')}t"
            )
            lines.append(
                f"- yields: F{y.get('food', 0):.1f} P{y.get('production', 0):.1f} G{y.get('gold', 0):.1f} "
                f"S{y.get('science', 0):.1f} C{y.get('culture', 0):.1f} Fa{y.get('faith', 0):.1f}"
            )
            lines.append(
                f"- **producing:** {prod.get('name')} "
                f"({prod.get('progress', 0):.0f}/{prod.get('cost', 0):.0f}, {prod.get('turns')}t)"
            )
            lines.append(
                f"- defense: str {defense.get('strength', 0)} | "
                f"garrison {defense.get('garrison_hp', 0)}/{defense.get('garrison_max', 0)} | "
                f"walls {defense.get('wall_hp', 0)}/{defense.get('wall_max', 0)}"
            )
            rel_here = c.get("majority_religion", "NONE")
            if rel_here and rel_here != "NONE":
                lines.append(f"- majority religion: {rel_here}")
            for d in c.get("districts", []):
                adj = ", ".join(f"+{v}{k}" for k, v in (d.get("adjacency") or {}).items())
                pill = " (PILLAGED)" if d.get("pillaged") else ""
                lines.append(
                    f"    - district `{d.get('type', '').replace('DISTRICT_', '')}` "
                    f"@ ({d.get('x')},{d.get('y')}){pill}"
                    + (f" [{adj}]" if adj else "")
                )
            blds = c.get("buildings", []) or []
            if blds:
                by_dist: dict[str, list[str]] = {}
                for b in blds:
                    mark = " (PILLAGED)" if b.get("pillaged") else ""
                    by_dist.setdefault(b.get("district", "?"), []).append(b.get("name") + mark)
                for k, v in by_dist.items():
                    lines.append(f"    - buildings in `{k.replace('DISTRICT_', '')}`: " + ", ".join(v))
            tr = c.get("tiles_rollup", {}) or {}
            if tr:
                terr = ", ".join(f"{v} {k}" for k, v in (tr.get("terrain") or {}).items())
                feat = ", ".join(f"{v} {k}" for k, v in (tr.get("features") or {}).items())
                improv = ", ".join(f"{v} {k}" for k, v in (tr.get("improvements") or {}).items())
                lines.append(
                    f"    - tiles: {tr.get('owned')} owned, {tr.get('worked')} worked "
                    f"| terrain: {terr or '—'}"
                    + (f" | features: {feat}" if feat else "")
                    + (f" | improvements: {improv}" if improv else "")
                )
            prods = c.get("production_options", []) or []
            if prods:
                sortable = sorted(prods, key=lambda p: (p.get("turns") if p.get("turns", -1) >= 0 else 999))[:10]
                lines.append(
                    "    - top production options: "
                    + ", ".join(f"{p.get('name')} ({p.get('turns')}t)" for p in sortable)
                )
                if len(prods) > 10:
                    lines.append(f"    - ...{len(prods) - 10} more options in JSON")
            for tr_r in c.get("trade_routes", []) or []:
                y = ", ".join(f"{k} {v:+d}" for k, v in tr_r.get("yields", {}).items())
                civ = tr_r.get("dest_civ") or "?"
                # "domestic" reads better inline than a civ name we already know.
                where = (
                    f"{tr_r.get('dest_city')} (domestic)"
                    if civ == "domestic"
                    else f"{tr_r.get('dest_city')} ({civ})"
                )
                lines.append(f"    - trade → {where}: {y or 'no yields'}")
        lines.append("")

    # ---- Units ------------------------------------------------------------
    if st.get("units") == "failed":
        lines.append("## UNITS")
        lines.append(_fail_marker("units", snap))
        lines.append("")
    else:
        units = snap.get("units") or []
        lines.append(f"## UNITS ({len(units)})")
        for u in units:
            idle = " <IDLE>" if u.get("idle") else ""
            promo = (
                f" xp{u.get('xp')}/{u.get('xp_needed')} (+{u.get('promotions_available')} avail)"
                if u.get("promotions_available", 0) > 0
                else f" xp{u.get('xp')}/{u.get('xp_needed')}"
            )
            upg = f" | UPGRADE→{u.get('upgrade_to')}({u.get('upgrade_cost')})" if u.get("can_upgrade") else ""
            chrg = f" ch{u.get('charges')}" if u.get("charges") else ""
            fort = f" fort:{u.get('fortify_turns')}" if u.get("fortify_turns") else ""
            lines.append(
                f"- **{u.get('name')}** #{u.get('id')} @({u.get('x')},{u.get('y')}) "
                f"| hp{u.get('hp')}/{u.get('hp_max')} | mv{u.get('moves'):.0f}/{u.get('moves_max'):.0f} "
                f"| cs{u.get('combat')} rs{u.get('ranged')}{promo}{chrg}{fort}{upg}{idle}"
            )
        lines.append("")

    # ---- Diplomacy --------------------------------------------------------
    lines.append("## DIPLOMACY")
    if st.get("envoys") == "failed":
        lines.append("- **envoys:** " + _fail_marker("envoys", snap))
    else:
        envoys = snap.get("envoys") or {}
        if envoys:
            lines.append(
                _kv(
                    "envoys",
                    f"{envoys.get('in_hand')} in hand | {envoys.get('points')}/{envoys.get('threshold')} pts "
                    f"(+{envoys.get('per_turn'):.1f}/turn — {envoys.get('envoys_per_threshold')} envoys/threshold)",
                )
            )
    if st.get("majors_met") == "failed":
        lines.append("### MAJORS MET")
        lines.append(_fail_marker("majors_met", snap))
    else:
        majors = snap.get("majors_met") or []
        if majors:
            lines.append("### MAJORS MET")
            for majg in majors:
                war = " ⚔️AT WAR" if majg.get("at_war") else ""
                ob = []
                if majg.get("open_borders_from_them"):
                    ob.append("OB from them")
                if majg.get("open_borders_from_us"):
                    ob.append("OB to them")
                ob_str = f" | {', '.join(ob)}" if ob else ""
                agendas = ", ".join(a.get("name", a.get("type", "?")) for a in majg.get("known_agendas", []))
                lines.append(
                    f"- **{majg.get('civ_name')} ({majg.get('leader_name')})** — "
                    f"{majg.get('relation_state_name') or '?'}{war} | "
                    f"vis {majg.get('diplo_visibility')} | score {majg.get('score')} mil {majg.get('military')} | "
                    f"met T{majg.get('met_turn')}{ob_str}"
                    + (f" | agendas: {agendas}" if agendas else "")
                )
    if st.get("city_states_met") == "failed":
        lines.append("### CITY-STATES MET")
        lines.append(_fail_marker("city_states_met", snap))
    else:
        cs = snap.get("city_states_met") or []
        if cs:
            lines.append("### CITY-STATES MET")
            for c in cs:
                war = " ⚔️" if c.get("at_war") else ""
                quests = ", ".join(q.get("description", q.get("type", "?")) for q in c.get("active_quests", []))
                lines.append(
                    f"- **{c.get('civ_name')}** ({c.get('cs_type')}) — "
                    f"envoys sent {c.get('envoys_sent')} | suz: {c.get('suzerain')} | "
                    f"@({c.get('x')},{c.get('y')}) | met T{c.get('met_turn')}{war}"
                    + (f" | quest: {quests}" if quests else "")
                )
    lines.append("")

    # ---- Barbarians -------------------------------------------------------
    barbs = snap.get("barbarians_visible") or []
    camps_v = snap.get("camps_visible") or []
    camps_r = snap.get("camps_revealed_only") or []
    if barbs or camps_v or camps_r:
        lines.append("## BARBARIANS (only what we can currently see)")
        if barbs:
            lines.append(
                f"- **units visible ({len(barbs)}):** "
                + "; ".join(
                    f"{b.get('name')} @({b.get('x')},{b.get('y')}) hp{b.get('hp')}/{b.get('hp_max')}" for b in barbs
                )
            )
        if camps_v:
            lines.append(
                f"- **camps currently visible ({len(camps_v)}):** "
                + ", ".join(f"({c.get('x')},{c.get('y')})" for c in camps_v)
            )
        if camps_r:
            lines.append(
                f"- camps previously revealed but not currently visible ({len(camps_r)}): "
                + ", ".join(f"({c.get('x')},{c.get('y')})" for c in camps_r)
            )
        lines.append("")

    # ---- Notifications ---------------------------------------------------
    if st.get("notifications") == "failed":
        lines.append("## NOTIFICATIONS")
        lines.append(_fail_marker("notifications", snap))
        lines.append("")
    else:
        notifs = snap.get("notifications") or []
        if notifs:
            lines.append("## NOTIFICATIONS")
            for n in notifs:
                tag = f" [BLOCKS: {n.get('blocker_type')}]" if n.get("blocker_type") else ""
                lines.append(f"- `{n.get('type')}`{tag}: {n.get('message')}")
            lines.append("")

    # ---- Revealed map ----------------------------------------------------
    if st.get("map") == "failed":
        lines.append("## REVEALED MAP")
        lines.append(_fail_marker("map", snap))
        lines.append("")
    else:
        tiles = snap.get("tiles") or []
        mtot = snap.get("map_totals", {}) or {}
        if tiles:
            lines.append("## REVEALED MAP")
            lines.append(
                f"_{mtot.get('revealed', 0)} revealed, {mtot.get('visible', 0)} currently visible, "
                f"{mtot.get('natural_wonders', 0)} natural wonders_"
            )
            lines.append(
                "**Line schema:** `MAP x,y v|terr|feat|res|imp|road|owner|dist|city|units|extra`  "
                "(`v`=1 currently visible; `terr` = g/p/d/t/s (+h for hills, +m for mountain); "
                "`feat` = for/jun/mar/fld/oas/reef/nw:NAME; `imp` may end `:P` if pillaged; "
                "`extra` R=river L=lake F=freshwater A±N=appeal)"
            )
            lines.append("```")
            for t in tiles:
                lines.append(
                    f"{t.get('x')},{t.get('y')} {int(bool(t.get('visible')))}|"
                    f"{t.get('terrain')}|{t.get('feature')}|{t.get('resource')}|{t.get('improvement')}|"
                    f"{t.get('road')}|{t.get('owner')}|{t.get('district')}|{int(bool(t.get('is_city')))}|"
                    f"{t.get('units')}|{t.get('extra')}"
                )
            lines.append("```")
            lines.append("")

    # ---- Natural wonders --------------------------------------------------
    nws = snap.get("natural_wonders") or []
    if nws:
        lines.append("## NATURAL WONDERS SEEN")
        for nw in nws:
            lines.append(f"- {nw.get('name')} @({nw.get('x')},{nw.get('y')})")
        lines.append("")

    # ---- Diagnostics -----------------------------------------------------
    diag = snap.get("diagnostics", {}) or {}
    lines.append("## DIAGNOSTICS")
    lines.append(f"- section status: " + ", ".join(f"{k}={v}" for k, v in sorted(st.items())))
    tot = diag.get("total_seconds", 0)
    lines.append(f"- generation time: {tot:.2f}s")
    pq = diag.get("per_query_seconds", {}) or {}
    if pq:
        lines.append("- per-query timing (s): " + ", ".join(f"{k}={v}" for k, v in pq.items()))
    fails = diag.get("failures", []) or []
    if fails:
        lines.append("- **failures at runtime:**")
        for f in fails:
            msg = (f.get("message", "") or "").splitlines()[0][:200]
            lines.append(f"    - `{f.get('section')}`: {msg}")
    traces = diag.get("traces", {}) or {}
    if traces:
        # Only show the LAST trace per query — helpful for "where did we stop"
        lines.append("- last trace per query (for post-mortem):")
        for q, tl in traces.items():
            last = tl[-1] if tl else "(no traces)"
            lines.append(f"    - `{q}`: {last}")
    ua = diag.get("unsupported", []) or []
    if ua:
        lines.append("- categories intentionally omitted (base-game only):")
        for u in ua:
            lines.append(f"    - {u}")
    md = "\n".join(lines)
    meta_turn = (snap.get("meta") or {}).get("turn") if snap.get("meta") else None
    md += (
        f"\n\n<!-- coach snapshot: schema={snap.get('schema')} "
        f"turn={meta_turn} generated_at={snap.get('generated_at_epoch')} "
        f"failed_sections={','.join(failed_sections) if failed_sections else 'none'} -->\n"
    )
    return md
