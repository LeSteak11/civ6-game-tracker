# Civ 6 AI Coach — QUICKSTART — v0.5

The whole thing on one page. Stick to this order.

---

## Opening Civ 6 for a session

**1. Start Civ 6. Load your save.** Do this FIRST. The console attaches to a
running game — open it before the game and it finds nothing.

**2. Double-click `civ6.bat`.** A black terminal window opens and connects.
You'll see a long list of Lua states. Ignore it.

**3. Type this and press Enter:**

```
use 5
```

It should say `Switched to state 5`. That's `GameCore_Tuner`, the only state
that can read game data.

**4. Open `civ6-query.lua` in Notepad.** Select all (Ctrl+A), copy (Ctrl+C).

**5. Paste into the terminal, press Enter.**
**Nothing will print. That is correct** — it only defines the report.

**6. Type this and press Enter:**

```
S()
```

The report prints.

**7. Copy the whole report** and paste it into your AI chat, along with
`AI-COACH-INSTRUCTIONS.md` if it's a brand new chat.

---

## Every turn after that

Type `S()`. Copy. Paste to chat. That's it — steps 1–5 are once per session,
not once per turn.

---

## Starting a brand new game

**Nothing changes.** No extra setup. FireTuner stays enabled in options
permanently, the launcher still works, the query still works. Same seven
steps.

---

## When something breaks

| Symptom | Fix |
|---|---|
| `S()` → "attempt to call a nil value" | Re-paste the long line from `civ6-query.lua`. Always safe to re-paste. |
| Everything errors after `use 5` | Wrong state. Type `states`, find `GameCore_Tuner`, use the number printed just before that name. Verify with `print(Game.GetCurrentGameTurn())`. |
| Terminal closes instantly | Civ 6 isn't running, or no save is loaded. |
| Lua looks mangled, weird quote characters | It got saved through Word. Plain text only — `.txt` or `.lua`, never `.docx`. |

---

## Files in this folder

| File | What it's for |
|---|---|
| `civ6.bat` | Launcher. Double-click to open the console. |
| `civ6-query.lua` | The long line you paste each session. |
| `QUICKSTART-v0.5.md` | This page. |
| `SETUP-new-game.md` | Longer setup notes and troubleshooting. |
| `AI-COACH-INSTRUCTIONS.md` | Upload to any new AI chat so it knows how to read the report and how to coach. |
| `HANDOFF.md` | Full technical handoff — upload if continuing development in a new chat. |

---

## Two things worth knowing

**Achievements are off.** FireTuner disables Steam achievements while
enabled. Known, accepted, reversible in options.

**Nothing here can hurt your save.** Every command is read-only. The coach
never presses a button; it tells you which button to press.

---

## What v0.5 still can't see

Housing, amenities, food surplus, districts and buildings per city, envoys at
city-states, luxury/strategic resources, trade routes, great people progress,
map and terrain, other civs' actual standing.

Being worked on. Until then, if the coach needs one of those, it should ask
you to look it up in-game rather than guess.
