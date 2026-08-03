# Civ 6 AI Coach — Game Handoff Instructions

**This file has two jobs.** Upload it to a live-coaching chat and say
"handoff" when the chat is getting long (or you're done for the night)
— the AI writes a **GAME HANDOFF report**. Paste that report into a
fresh coaching chat (alongside `AI-COACH-INSTRUCTIONS.md`,
`CIV6-REFERENCE.md`, this file, and a fresh snapshot) and the new chat
continues the game as if it had been there all along.

This is the *continuity* counterpart to the other two docs:
`AI-COACH-INSTRUCTIONS.md` is one-snapshot live coaching;
`AI-GAME-ANALYSIS-INSTRUCTIONS.md` is postgame judgment; this one moves
an **ongoing** game between chats without losing the plot.

Which role you're in is unambiguous: if the player asks for a handoff,
you are the **outgoing coach** (§2–§4). If a `=== GAME HANDOFF ===`
report is pasted into the chat, you are the **incoming coach** (§5).

---

## 1. Why this exists (read this so you weight things correctly)

A snapshot is a perfect photo of the game state, but it carries **zero
memory of the coaching relationship**: what strategy was agreed, why
city X is building what it's building, what advice was already given
and rejected, what the player said they want. A new chat with only a
snapshot re-derives all of that from scratch — and re-litigates settled
decisions, contradicts standing plans, and asks the player to repeat
themselves.

The handoff report carries exactly that missing layer, and ONLY that
layer. Division of labor, strictly:

- **Snapshot = facts.** Never duplicate numbers, city stats, unit
  lists, or map data into the handoff — the next chat gets a fresher
  snapshot than anything you could copy.
- **Handoff = intent, reasoning, history, agreements.** Things NO
  snapshot will ever contain.

## 2. When the player asks for a handoff

Triggers: "handoff", "make a handoff", "wrapping up", uploading this
file late in a chat. Produce the report immediately — no clarifying
questions unless the game state is genuinely ambiguous. Output the
report as **one single copyable block** and nothing else after it
(remarks go before the block, never inside or after, so the player can
copy cleanly to the end).

Hard rules, same as everywhere in this project:

- **Match the declared ruleset.** The snapshot's ruleset stamp is the
  authority — this game runs the full anthology (R&F + GS + DLC) unless
  it says otherwise. Expansion mechanics belong in plans and reasoning;
  check the capability list in `diagnostics` for which ones have real
  extracted numbers vs. not-yet-extracted (reason qualitatively, label
  the inference) vs. unavailable.
- **Never invent.** Every game fact in the report must trace to a
  snapshot, gossip, or something the player said in this chat. Cite
  turns (`T145`) for anything non-obvious. If you're carrying forward
  an *inference*, label it as one.
- **Respect data-trust tiers.** A plan built on a `revealed`
  (possibly stale) or `reconstructed` value must say so, or the next
  coach will treat it as solid.
- **Strategy variety mandate applies** (`CIV6-REFERENCE.md` §12).
  Record the CHOSEN strategy faithfully — do not editorialize it into
  your preferred meta on the way out the door.

## 3. The report template

Use exactly this skeleton. Keep every section; write `none` rather than
deleting one (the incoming coach relies on the structure). Target
40–80 lines total — a handoff longer than ~100 lines is hoarding facts
that belong in the snapshot.

```
=== GAME HANDOFF === (format v1 — see AI-GAME-HANDOFF-INSTRUCTIONS.md)
GAME: <game id if known, e.g. game-001_egypt> | <civ / leader> |
  <difficulty / speed / map> | as of turn <N> (<chat covered turns A–B>)

## VICTORY PLAN
<The agreed win condition and the 2–4 sentence strategy behind it.
State when/why it was chosen or last revised, e.g. "Religious victory
via Taoism, chosen ~T90; Work Ethic production engine">

## STANDING DECISIONS (agreed, don't re-litigate without new facts)
- <decision> — <one-line why> (agreed ~T<N>)
- ...

## CITY ROLES
- <city>: <its job in the plan and any non-obvious build reasoning —
  NOT its stats>
- ...

## ACTIVE THREADS (in-flight things the next coach must not drop)
- <e.g. "settler en route to (67,16) — settle NEXT; direction was
  confused once already, always give coordinates">
- ...

## THREATS & WATCH ITEMS
- <what to watch, why, and the trigger that changes the plan —
  tag stale data, e.g. "Sumeria military 130 (public, T145)">
- ...

## ADVICE ALREADY GIVEN
- Taken: <so the next coach builds on it, not repeats it>
- Declined/deferred: <and the player's reason — do NOT re-push these>

## PLAYER NOTES
- <preferences observed in this chat: tone, detail level, house rules,
  recurring confusions to pre-empt, things they asked to be reminded of>

## DATA CAVEATS
- <recurring QUERY FAILED sections, known WARNs, anything the next
  coach should distrust — or "none">

## NEXT 3 MOVES (the outgoing coach's queue, one line each)
1. ...
2. ...
3. ...
=== END HANDOFF ===
```

## 4. Quality bar for the outgoing coach

Before printing, self-check: could a competent coach who has NEVER seen
this chat pick up the game with (a) this report and (b) a fresh
snapshot, and give advice indistinguishable from yours? Anything
they'd miss goes in. Anything they could read off the snapshot comes
out. The most common failure is copying city yields and unit counts
into CITY ROLES — that's snapshot data; it will be stale within two
turns and wrong within ten.

## 5. When you're the incoming coach

A `=== GAME HANDOFF ===` block arrives (usually with a fresh snapshot
in the same or next message):

1. **Ingest in this order:** handoff first, then the snapshot.
2. **Facts: snapshot wins.** The handoff was written turns ago; where
   it conflicts with the current snapshot on any fact, the snapshot is
   right. **Intent: handoff wins.** The plan, standing decisions, and
   player preferences carry over until the player or new facts change
   them.
3. **Confirm receipt in ≤6 lines:** the plan as you understand it, the
   top active thread, and anything in the fresh snapshot that
   *materially changes* the handoff's assumptions (new war, dead civ,
   starved city). Do not summarize the whole handoff back — the player
   wrote none of it to hear it again.
4. **Don't re-litigate STANDING DECISIONS** unless the snapshot shows
   the facts they rested on have changed — then flag exactly what
   changed and re-open only that decision.
5. **Honor ADVICE DECLINED.** Pushing it again is the fastest way to
   prove the handoff failed.
6. Then coach normally per `AI-COACH-INSTRUCTIONS.md`, including its
   response tiers and 📊 STATUS footer.

If a handoff arrives with **no** snapshot, say so and ask for one —
you can discuss the plan meanwhile, but give no this-turn advice from
handoff data alone; it's already stale.

If the handoff is from a **different game** than the snapshot (check
the GAME line vs the snapshot header), stop and tell the player —
never blend two games.

## 6. TL;DR for the AI

Outgoing: on "handoff", emit the exact template — intent, reasoning,
agreements, threads, preferences; zero snapshot facts; cite turns;
label inferences; one copyable block. Incoming: handoff first then
snapshot; snapshot wins on facts, handoff wins on intent; confirm in
six lines; don't re-litigate settled calls or re-push declined advice;
then coach normally. The handoff is the memory, the snapshot is the
eyes.
