# Civ 6 Lua Coach — Project Handoff — **v0.7**

Read this fully before responding. It contains everything about what we are
building, what already works, and what to do next.

---

## 1. What this project is

The user plays **Civilization VI on Steam, base game only** — no Rise & Fall,
no Gathering Storm. They are a **first-time 4X player**.

They want an AI coach that sees their real game state without screenshots.
The mechanism: Civ 6 ships a debug interface called **FireTuner**. The user
runs a local Lua console that connects to the running game, types a command,
and the game prints a status report. The user copies that text into the chat.

**There is no live connection, no MCP, no connector, no tool access to the
game.** Everything the assistant knows arrives as pasted text. Do not attempt
to connect to, fetch from, or call the game. Do not ask for screenshots — the
whole point is to replace them.

## 2. Hard rules

- **Read-only.** Never suggest Lua that changes game state — no ending turns,
  no setting production or research, no moving units, no save/load,
  no `RequestPlayerOperation`. Reads only. Describe the click; the user
  presses it.
- **Base game only.** Never mention governors, loyalty, era score, Golden or
  Dark Ages, climate, disasters, power, resource consumption, World Congress,
  diplomatic favor, or Diplomatic Victory. None of those exist in this game.
- **Coach, don't play.** The user makes every decision.
- **Teach.** Define Civ jargon inline, once, briefly. Say *why*, not just
  *what*. When a decision is close, say so and name the tradeoff rather than
  faking confidence.
- **Never invent data.** If a number isn't in the pasted report, ask for it or
  write a query to fetch it. Do not estimate and present it as fact.

## 3. Current state — what works

Fully working, confirmed against the user's live game and the game's own UI
source:

- Launcher `civ6.bat` opens the Lua REPL against the running game.
- `use 5` selects the `GameCore_Tuner` Lua state — the one that can read game
  data.
- The `S()` function is defined by pasting the single long line from
  `civ6-query.lua`. Typing `S()` prints a full status report.
- The whole report body is wrapped in `pcall`, so a single unexpected
  nil / missing field prints an error line at the end rather than killing
  the entire report.

**v0.7 report includes:**

- Header: turn number + year string + era name
- Civ / leader / total score
- Global yields: gold (balance + net + yield + maintenance), science with
  current tech (progress/cost/turns) and **eureka trigger description**,
  culture with current civic (progress/cost/turns) and **inspiration trigger
  description**, faith balance + rate, tourism per turn
- Government name + open policy slot count
- **Slotted policy cards** listed by slot type + card name
- Aggregate military strength, techs done, civics done
- **Envoys**: envoys in hand, influence points earned / threshold, points
  per turn, envoys awarded per threshold
- **Religion**: pantheon (if picked) + founded religion + all belief names
- **Trade routes**: active / capacity, plus one line per active route
  with origin city, destination city, and per-yield breakdown
- **Strategic resources** with counts, **luxury resources** with counts
- **Great-people points** per class (total + per turn) for classes with any
  progress
- **Wonders built** empire-wide with which city holds each
- **Per city**: name, capital flag, map coords, population, growth turns
  (or STARVE countdown), food surplus, housing, amenities (have / needed),
  border-expansion turns, all six yields (F/P/G/S/C/Fa), current
  production + turns
  - Per built district: plot coords, adjacency yield totals, buildings
    inside (with `PILLAGED` flag)
  - Owned tile count + worked count
  - Terrain census + feature census
  - Improvement census
  - One line per tile with a resource: coords, bonus/lux/strat class,
    resource name + count, improvement (if any), worker flag
- **Units**: type, HP, moves, coords, XP, build charges, fortify turns,
  IDLE flag
- **Barbarian camps**: every camp improvement on the map with coords
- **Barb units alive**: every barbarian unit with type + coords
- **Diplomacy split**: majors met (score, military, techs, war, met-turn)
  vs city-states met (envoys sent by us, current suzerain — `ME` if it's
  us — war, met-turn). Barbarians (playerID 63) filtered from these.

Example shape (numbers illustrative):

```
=== CIV6 STATUS | TURN 87 (725 BC, Classical Era) ===
CIV: CIVILIZATION_EGYPT / LEADER_CLEOPATRA | SCORE: 79
GOLD: 330 (net +10.4 | yield 12.4, maint 2.0)
SCIENCE: 17.1/turn | Construction 92/200 (7 turns) | eureka:false [need: Build a Water Mill]
CULTURE: 11.3/turn | Military Tradition 0/50 (4 turns) | inspiration:false [need: Clear a Barbarian Outpost]
FAITH: 184 (+7.3/turn)
TOURISM: 8.0/turn
GOVERNMENT: Classical Republic | open policy slots: 0
POLICY CARDS SLOTTED:
    MILITARY: Discipline
    ECONOMIC: Ilkum
    DIPLOMATIC: Diplomatic League
MILITARY: 119 | techs done 13 | civics done 8
ENVOYS: 0 in hand | 8/100 pts (+3.0/turn, 1 envoys per threshold)
RELIGION:
  Pantheon: Religious Settlements | Founded: none
TRADE ROUTES: 1/1
  Râ-Kedet -> Kabul: +2G +1F
STRATEGIC: none
LUXURIES: 1 Ivory
GREAT PEOPLE: GENERAL 49(+1.1) | PROPHET 25(+2.3)
WONDERS BUILT: none
CITIES:
=== Râ-Kedet [CAP] === pos(66,32) | pop 3 | grow 24t (food+1.0) | hous 10 | am 3/1 | border+5t
  YIELDS: F7.0 P14.7 G10.5 S8.5 C5.1 Fa6.3
  PRODUCING: BUILDING_STONEHENGE (1t)
  DIST CITY_CENTER pos(66,32): Palace, Granary
  DIST ENCAMPMENT pos(65,33) [adj: +1P]: Barracks
  TILES: 24 owned, 8 worked | terrain: 10 grass, 6 plains, 4 desert, 3 hills, 1 coast | features: 3 forest, 2 floodplains
  IMPROVEMENTS: 4 farm, 1 pasture, 1 quarry
  RESOURCE TILES:
    (67,32) bon Wheat farm W
    (68,30) lux Ivory camp
    (66,29) str Iron(2)
...
BARBARIAN CAMPS (1): (63,28)
BARB UNITS ALIVE (12): Warrior (63,29), Scout (58,22), ...
MAJORS MET (2):
  CIVILIZATION_SUMERIA | war=false | score=96 mil=169 techs=14 | metT27
CITY-STATES MET (4):
  HATTUSA | envoys sent 2 | suz: none | war=false | metT19
```

## 4. What's still missing (wishlist, not blockers)

The report already beats a screenshot for most decisions. These are the
remaining gaps worth chasing:

- **Trade route destinations** and per-route yields. UI source in
  `TradeSupport.lua` — `city:GetTrade():GetOutgoingRoutes()` returns a list
  containing `TraderUnitID` and destination info.
- **Per-district adjacency bonuses.** Confirmed in `CitySupport.lua`:
  `district:GetAdjacencyYield(yieldIndex)` per yield.
- **Buildings inside each district**, and pillaged status. Confirmed:
  `city:GetBuildings():GetBuildingsAtLocation(plotID)` and
  `:IsPillaged(buildingType)`.
- **Active city-state quests** and the specific tier-1/3/6 bonus text per
  city-state. Confirmed: `Game.GetQuestsManager()` in
  `PartialScreens\CityStates.lua`.
- **Slotted policy cards** (only slot count is shown right now).
- **Map / terrain** around cities and improvements on tiles. Confirmed:
  `Map.GetCityPlots():GetPurchasedPlots(pCity)` returns plot IDs;
  `Map.GetPlotByIndex(plotID)` returns a plot object.
- **Available techs/civics** the user could switch to (only current shown).
- **Other civs' attitude** toward the local player.

None of these are blockers. Add them when the user asks for one, not
speculatively.

## 5. How to extend the query — critical methodology

The original attempt at this project failed by **guessing method names**.
`Players[id]:GetTreasury():GetGold()` failed with
`function expected instead of nil`, which does not say which link broke. The
real name was `GetGoldBalance`.

**Never guess. Confirm first**, using the game's own UI source:

- `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI\Base\Assets\UI\`
- The whole folder is Lua source that reads the same objects the tuner
  exposes. If the game's own UI can compute a number, so can `S()`.

Key files that gave us most of v0.6:
- `TopPanel.lua` — global yields, tourism, envoys, resources, trade slots
- `CitySupport.lua` — food surplus, housing, amenities (with per-source
  breakdowns), per-city yields, districts, buildings, trading posts
- `TechAndCivicSupport.lua` — tech/civic progress, boost detection,
  `GameInfo.Boosts()` iteration for `TriggerDescription`
- `TradeSupport.lua` — trade routes
- `PartialScreens\CityStates.lua` — `GetTokensReceived`, `GetSuzerain`,
  `GetTokensToGive`, city-state bonus/quest logic
- `PartialScreens\WorldRankings.lua` — score / military / tourism /
  culture / religion / tech scoring per civ
- `Popups\GreatPeoplePopup.lua` — `GetGreatPeoplePoints():GetPointsTotal /
  GetPointsPerTurn` by class ID

Secondary tool — reflection at the REPL when the UI source doesn't show it:

```lua
function M(o) local mt=getmetatable(o) local i=mt and mt.__index local t={} if type(i)=="table" then for k,v in pairs(i) do t[#t+1]=k end end table.sort(t) print(table.concat(t,"\n")) end
```

Usage: `M(city:GetGrowth())` prints every method on the growth object. Build
queries only from names that actually appeared in a dump or in UI source.

**Console constraints:**

- **Input must be a single line.** The REPL wraps input as `_cmdr = {...}`.
  Multi-line pastes break. The header comments in `civ6-query.lua` are
  separate lines but are fine because Lua parses them as comments; the
  actual `function S() … end` must stay on one line.
- Function definitions print no output. That is success, not failure.
- Wrap uncertain calls in `pcall` so one bad field returns nil instead of
  killing the whole report. The v0.6 `S()` also wraps its whole body in
  `pcall(function() … end)` for a final safety net.

## 6. Confirmed-working API surface (v0.6)

**Player-level entry points on `Players[0]`:**
`GetTreasury, GetTechs, GetCulture, GetReligion, GetCities, GetUnits,
 GetDiplomacy, GetStats, GetDistricts, GetResources, GetImprovements,
 GetInfluence, GetTrade, GetGrandStrategicAI, GetEra, GetScore,
 GetGreatPeoplePoints`

**Yields live on sub-objects, not the player:**
`player:GetTechs():GetScienceYield()`, `GetCulture():GetCultureYield()`,
`GetReligion():GetFaithYield()`, `GetTreasury():GetGoldYield()`.

**Treasury:** `GetGoldBalance, GetGoldYield, GetTotalMaintenance`.

**Techs:** `GetResearchingTech()` returns row index. Then
`GetResearchProgress(i), GetResearchCost(i), GetTurnsToResearch(i),
HasBoostBeenTriggered(i)`. Cost/progress getters require the index.

**Culture:** `GetProgressingCivic()` returns row index. Then
`GetCulturalProgress(i), GetCultureCost(i), GetTurnsToProgressCivic(i),
HasBoostBeenTriggered(i), GetCurrentGovernment(),
GetNumPolicySlotsOpen()`.

**Religion:** `GetFaithBalance, GetFaithYield`.

**Stats:** `GetMilitaryStrength, GetMilitaryStrengthWithoutTreasury,
GetNumTechsResearched, GetNumCivicsCompleted, GetTourism,
GetNumCitiesFollowingReligion`.

**Influence:** `GetTokensToGive, GetPointsEarned, GetPointsThreshold,
GetPointsPerTurn, GetTokensPerThreshold`. On another player's influence
object: `GetTokensReceived(otherPlayerID), GetSuzerain()`.

**Trade (player):** `GetNumOutgoingRoutes, GetOutgoingRouteCapacity`.
**Trade (city):** `city:GetTrade():GetOutgoingRoutes()` returns a list of
route tables with `TraderUnitID` etc.

**Resources:** `pr:GetResourceAmount(resourceType),
pr:HasResource(resourceType), pr:HasExportedResource(resourceType),
pr:GetExportedResourceAmount(resourceType)`.
Iterate `GameInfo.Resources()` and filter on `row.ResourceClassType` in
`RESOURCECLASS_STRATEGIC / RESOURCECLASS_LUXURY / RESOURCECLASS_BONUS /
RESOURCECLASS_ARTIFACT`.

**Great people:** `p:GetGreatPeoplePoints():GetPointsTotal(classID),
GetPointsPerTurn(classID)`. Iterate `GameInfo.GreatPersonClasses()`; each
row has `.Index` and `.GreatPersonClassType`.

**Cities:** iterate `p:GetCities():Members()`. Methods:
`GetName, GetPopulation, GetBuildQueue, GetGrowth, GetCitizens,
GetDistricts, GetBuildings, GetYield(yieldTypeEnum), GetGold, GetCulture,
GetReligion, GetTrade, GetX, GetY, IsCapital, IsOccupied,
GetAmenityAdvice, GetHousingAdvice, GetBuildingYield(bldg, yieldType)`.

**City growth object** (`city:GetGrowth()`):
`GetFood, GetGrowthThreshold, GetFoodSurplus, GetTurnsUntilGrowth,
GetTurnsUntilStarvation, GetOverallGrowthModifier, GetHousing,
GetHousingFromWater/Buildings/Improvements/Districts/Civics/GreatPeople/
StartingEra/GreatWorks, GetHousingGrowthModifier, GetAmenities,
GetAmenitiesNeeded, GetAmenitiesFromLuxuries/Entertainment/Civics/
GreatPeople/CityStates/Religion/NationalParks/StartingEra/Improvements/
Districts/NaturalWonders, GetAmenitiesLostFromWarWeariness/Bankruptcy,
GetHappiness, GetHappinessGrowthModifier,
GetHappinessNonFoodYieldModifier, GetOccupationGrowthModifier`.

**City build queue:** `GetCurrentProductionTypeHash(), GetTurnsLeft(),
GetBuildingProgress(idx), GetBuildingCost(idx), GetDistrictProgress(idx),
GetDistrictCost(idx), GetUnitProgress(idx), GetUnitCost(idx),
GetProjectProgress(idx), GetProjectCost(idx)`.

**City districts (`city:GetDistricts()`):** iterate with `:Members()`.
Each district has `GetType(), GetX(), GetY(), GetYield(yieldIndex),
GetAdjacencyYield(yieldIndex)`. Collection has
`GetNumZonedDistrictsRequiringPopulation(),
GetNumAllowedDistrictsRequiringPopulation(),
IsPillaged(type, plotID), HasDistrict(index, boolean),
FindID(districtID)`.

**City buildings:** `city:GetBuildings():GetBuildingsAtLocation(plotID),
IsPillaged(type), HasBuilding(index)`.

**Units:** iterate `p:GetUnits():Members()`. Methods:
`GetUnitType, GetDamage, GetMaxDamage, GetMovesRemaining, GetMaxMoves,
GetX, GetY, IsReadyToMove, GetExperience, GetCombat, GetRangedCombat,
GetBuildCharges, GetFortifyTurns, GetID`.

**Diplomacy:** `d:GetNumPlayersMet(), d:GetPlayersMetIDs() [array],
d:IsAtWarWith(id), d:GetMetTurn(id), d:HasMet(id)`.

**Player classification:** `PlayerManager.GetAliveMajorIDs(),
PlayerManager.GetAliveMinorIDs(), PlayerManager.GetAliveMajors()`.

**Player configuration:** `PlayerConfigurations[id]:GetCivilizationTypeName(),
GetLeaderTypeName(), GetCivilizationShortDescription(), GetTeam()`.

**Database lookups:**
- `GameInfo.Technologies[i]`, `GameInfo.Civics[i]`, `GameInfo.Units[i]`,
  `GameInfo.Governments[i]`, `GameInfo.Buildings[hash]`,
  `GameInfo.Districts[typeOrIndex]`, `GameInfo.Projects[hash]`.
- `GameInfo.Types[hash]` resolves a production hash to `.Type` and `.Kind`.
- Iterate: `GameInfo.Resources()`, `GameInfo.Yields()`, `GameInfo.Boosts()`,
  `GameInfo.GreatPersonClasses()`, `GameInfo.Governments()`,
  `GameInfo.LeaderTraits()`, `GameInfo.DiplomaticStates`,
  `GameInfo.Quests()`.
- `GameInfo.Boosts()` row has `TechnologyType` OR `CivicType`,
  `Boost` (percent), `TriggerDescription` (a LOC key).

**Globals:** `Game.GetLocalPlayer(), Game.GetCurrentGameTurn(),
Game.GetGameEndTurn(), Game.GetReligion(), Game.GetQuestsManager(),
Game.GetTradeManager(), Game.GetGameDiplomacy()`.
`GameConfiguration.GetStartTurn(), MapConfiguration.GetMaxMajorPlayers()`.
`Calendar.MakeYearStr(turn)`, `Locale.Lookup(loc_key)`.
`YieldTypes.FOOD / PRODUCTION / GOLD / SCIENCE / CULTURE / FAITH`.

**Player-ID gotchas:**
- `Players[0]` is the local player. `Players[63]` is Barbarians — always
  filter out.
- City-states appear in the met list alongside real civs. Split with
  `PlayerManager.GetAliveMajorIDs()`.

## 7. Immediate next step

Smoke-test the v0.6 `S()` output on the user's live game (Cleopatra,
Egypt). Confirm every line renders and no `!! mid-report error` appears at
the bottom.

If a specific line comes back malformed, `M(obj)` at the REPL against that
sub-object will show what actually exists. Then patch the corresponding
call in `civ6-query.readable.lua` and re-flatten to single-line.

After that, pick one wishlist item from Section 4 and extend. The most
useful next add is probably **trade route destinations** (bottlenecks
whether the user is squeezing gold/food/production out of their traders)
or **per-district adjacency yields** (huge for district siting decisions).

## 8. Files the user has

- `civ6.bat` — launcher, opens the REPL. Lives in the project root.
- `civ6-query.lua` — the single-line `S()` definition plus header comments.
- `civ6-query.readable.lua` — the same function formatted for editing.
  Regenerate the single-line file from this when you tweak it.
- `SETUP-new-game.md` — per-session startup steps.
- `EVERY-TIME.md` — condensed six-step recap.
- `QUICKSTART-v0.5.md` — original one-page how-to (filename kept for
  continuity; contents now reflect v0.6).
- `AI-COACH-INSTRUCTIONS.md` — the coaching brief to upload into a fresh
  chat.
- `HANDOFF.md` — this file.

## 9. Coaching output format

When the user pastes a status report, give a short scannable read of the
position, then close with:

**WHAT MATTERS NOW** — exactly three priorities, ranked, one sentence of
reasoning each.

Do not re-run full analysis every turn unless asked. For a mid-turn
question, just answer the question.

## 10. Known open issues

- Pasting the long line each session is clunky. Ideas discussed: auto-send
  from the launcher via a small Python wrapper around
  `civ_mcp.tuner_client`, an AutoHotkey hotkey, or a proper Civ 6 mod. Not
  yet built.
- `use 5` is currently hardcoded. It resolved correctly to
  `GameCore_Tuner`, but the state list ordering is not guaranteed stable
  across launches. A fallback exists in `SETUP-new-game.md`.
- Keep the Lua in plain text only. Word converts quotes to curly quotes
  and silently breaks the script. `.txt` or `.lua` only, never `.docx`.
- The v0.6 line is ~9 KB. Notepad handles it fine; some terminals may
  visually wrap it, but the parser sees one line. If a paste ever fails,
  regenerate from `civ6-query.readable.lua` to rule out edit corruption.
