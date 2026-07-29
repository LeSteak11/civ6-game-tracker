# EVERY TIME I OPEN CIV 6

Six steps. About 20 seconds. Then `S()` for the rest of the session.

---

### 1. Open Civ 6 and load your save
Game first, always. The console attaches to a running game.

### 2. Double-click `civ6.bat`
Terminal opens, connects, dumps a big list of Lua states. Ignore the list.

### 3. Type `use 5`
Should say `Switched to state 5`.

### 4. Open `civ6-query.lua` in Notepad → Ctrl+A → Ctrl+C

### 5. Paste into the terminal → Enter
**Nothing prints. That's correct.**

### 6. Type `S()`
The report prints. Copy it, paste it to the AI chat.

---

# THEN, EVERY TURN

```
S()
```

Copy. Paste to chat. That's the whole loop.

---

**New game?** Nothing changes. Same six steps. There is no per-game setup.

**Broke?** See `QUICKSTART-v0.5.md`.
