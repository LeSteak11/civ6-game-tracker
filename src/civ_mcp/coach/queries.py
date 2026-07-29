"""Base-game-only Lua query builders for the coach snapshot.

Design rules (learned the hard way from the first live smoke test):

1.  **Never wrap a whole query in one outer pcall.**  If one field in the
    middle of the chunk errors, the outer pcall bails and we lose
    everything after it.  Instead, use a tiny ``safe(section, fn)`` helper
    that emits a ``TRACE|`` line, runs one narrow block inside pcall, and
    emits ``DIAG|section|err`` if it fails — then continues.
2.  **Emit TRACE|<section>|<field> before every risky group.**  If Lua
    crashes mid-section the next trace line names the field, so the next
    live failure never comes back as just "line 29 of an unknown chunk".
3.  **Iterate collections defensively.**  Each city, each district, each
    unit runs inside its own pcall.  A single missing building or plot
    yield cannot produce ``CITIES (0)``.
4.  **pcall every global** whose availability is not documented for the
    state we're running in.  Especially ``Calendar``,
    ``MapConfiguration``, ``GameConfiguration``, ``PlayerManager``,
    ``NotificationManager``, ``EndTurnBlockingTypes``.
5.  **Never guess a method name.**  If the exact API name isn't confirmed
    in the shipped base-game UI Lua or the v0.7 ``civ6-query.lua``, wrap
    the call in ``safeCall`` and treat a nil result as "unavailable".
"""

from __future__ import annotations

from civ_mcp.coach import SENTINEL


def _sentinel_line() -> str:
    return f'print("{SENTINEL}")'


# Common prelude used by every query.  Provides:
#   L           = Locale.Lookup
#   esc(s)      = pipe-safe string
#   sf(fn, ...) = pcall wrapper, returns nil on failure
#   safe(name, fn) = pcall block with TRACE+DIAG side effects
#   safeCall(name, obj, method, ...) = call obj:method(...) safely
#   me, p, cfg  = local player conveniences (nil if no player)
def _prelude(section: str) -> str:
    return f"""\
local L = Locale.Lookup
local function esc(s) if s == nil then return "" end return tostring(s):gsub("|", "/") end
local function sf(fn, ...)
  local ok, v = pcall(fn, ...)
  if ok then return v end
  return nil
end
local function safe(field, fn)
  print("TRACE|{section}|" .. field)
  local ok, err = pcall(fn)
  if not ok then print("DIAG|{section}." .. field .. "|" .. tostring(err)) end
end
local function safeCall(field, obj, method, ...)
  if obj == nil then return nil end
  local m = obj[method]
  if type(m) ~= "function" then
    print("DIAG|{section}." .. field .. "|method '" .. method .. "' not on object")
    return nil
  end
  local ok, v = pcall(m, obj, ...)
  if not ok then
    print("DIAG|{section}." .. field .. "|" .. tostring(v))
    return nil
  end
  return v
end
local me = -1
pcall(function() me = Game.GetLocalPlayer() end)
if me == nil or me == -1 then
  print("DIAG|{section}|no local player (main menu?)")
  {_sentinel_line()}
  return
end
local p = Players and Players[me] or nil
if not p then
  print("DIAG|{section}|Players[" .. me .. "] nil")
  {_sentinel_line()}
  return
end
local cfg = PlayerConfigurations and PlayerConfigurations[me] or nil
"""


# ---------------------------------------------------------------------------
# Q1 — metadata + global empire state
# ---------------------------------------------------------------------------

def build_meta_query() -> str:
    return _prelude("META") + r"""

-- ---- Header (turn, year, era) ------------------------------------------
safe("header", function()
  local turn = Game.GetCurrentGameTurn() or 0
  local year = ""
  pcall(function() if Calendar and Calendar.MakeYearStr then year = Calendar.MakeYearStr(turn) or "" end end)
  local eraName = "?"
  pcall(function()
    local eraIdx = p:GetEra()
    if eraIdx and eraIdx >= 0 then
      local er = GameInfo.Eras[eraIdx]
      if er then eraName = L(er.Name) end
    end
  end)
  local civType   = ""; pcall(function() civType   = cfg:GetCivilizationTypeName() or "" end)
  local civShort  = ""; pcall(function() civShort  = L(cfg:GetCivilizationShortDescription()) or "" end)
  local leaderType = ""; pcall(function() leaderType = cfg:GetLeaderTypeName() or "" end)
  local leaderName = ""; pcall(function() leaderName = L(cfg:GetLeaderName()) or "" end)
  local diffName = "?"
  pcall(function()
    local diffHash = cfg:GetHandicapTypeID()
    for d in GameInfo.Difficulties() do
      if GameConfiguration.MakeHash(d.DifficultyType) == diffHash then
        diffName = L(d.Name); break
      end
    end
  end)
  -- Game speed.  Game.GetGameSpeedType() returns a HASH, not a row index, so
  -- GameInfo.GameSpeeds[hash] silently misses.  Use the same MakeHash
  -- comparison loop that makes the difficulty lookup above work correctly.
  local speedName = "?"
  pcall(function()
    local gsHash = nil
    if GameConfiguration and GameConfiguration.GetGameSpeedType then
      gsHash = GameConfiguration.GetGameSpeedType()
    end
    if gsHash == nil and Game.GetGameSpeedType then
      gsHash = Game.GetGameSpeedType()
    end
    if gsHash == nil then return end
    -- Direct index first (cheap, works if it really was an index).
    local direct = GameInfo.GameSpeeds[gsHash]
    if direct and direct.Name then speedName = L(direct.Name); return end
    for row in GameInfo.GameSpeeds() do
      if GameConfiguration.MakeHash(row.GameSpeedType) == gsHash then
        speedName = L(row.Name); return
      end
    end
    print("WARN|META.speed|unresolved game speed hash " .. tostring(gsHash))
  end)

  -- Map size.  MapConfiguration.GetMapSize() returns a hash.  In the Civ 6
  -- base game the sizes live in GameInfo.Maps (Maps.xml) — GameInfo.MapSizes
  -- is Civ 5 legacy and does not exist, which is why v1.01 rendered "?".
  local mapSize = "?"
  pcall(function()
    if not (MapConfiguration and MapConfiguration.GetMapSize) then return end
    local msHash = MapConfiguration.GetMapSize()
    if msHash == nil then return end
    -- Primary: GameInfo.Maps rows keyed by MapSizeType (e.g. MAPSIZE_STANDARD)
    if GameInfo.Maps then
      local direct = GameInfo.Maps[msHash]
      if direct and (direct.Name or direct.MapSizeType) then
        mapSize = direct.Name and L(direct.Name) or direct.MapSizeType
      else
        for row in GameInfo.Maps() do
          if GameConfiguration.MakeHash(row.MapSizeType) == msHash then
            mapSize = row.Name and L(row.Name) or row.MapSizeType
            break
          end
        end
      end
    end
    -- Secondary: some builds do carry a MapSizes table — harmless to probe.
    if mapSize == "?" and GameInfo.MapSizes then
      for row in GameInfo.MapSizes() do
        if GameConfiguration.MakeHash(row.MapSizeType) == msHash then
          mapSize = row.Name and L(row.Name) or row.MapSizeType
          break
        end
      end
    end
    if mapSize ~= "?" and mapSize:find("MAPSIZE_") then
      mapSize = mapSize:gsub("MAPSIZE_", ""):lower():gsub("^%l", string.upper)
    end
    if mapSize == "?" then
      print("WARN|META.map_size|unresolved map size hash " .. tostring(msHash))
    end
  end)

  -- Map script.  GetScript() returns a filename like "Continents.lua" (and may
  -- carry a directory prefix).  Present a readable name.
  local mapType = "?"
  pcall(function()
    if not (MapConfiguration and MapConfiguration.GetScript) then return end
    local raw = tostring(MapConfiguration.GetScript() or "")
    if raw == "" then return end
    local base = raw:match("([^/\\]+)$") or raw   -- strip any path
    base = base:gsub("%.lua$", "")                -- strip extension
    base = base:gsub("_", " ")
    mapType = base
  end)
  local maxPlayers = 0
  pcall(function() if MapConfiguration and MapConfiguration.GetMaxMajorPlayers then maxPlayers = MapConfiguration.GetMaxMajorPlayers() or 0 end end)
  local maxTurns = 0
  pcall(function() if GameConfiguration and GameConfiguration.GetValue then maxTurns = GameConfiguration.GetValue("GAME_MAX_TURNS") or 0 end end)
  print("META|" .. turn .. "|" .. esc(year) .. "|" .. esc(eraName)
    .. "|" .. esc(civType) .. "|" .. esc(civShort)
    .. "|" .. esc(leaderType) .. "|" .. esc(leaderName)
    .. "|" .. esc(diffName) .. "|" .. esc(speedName)
    .. "|" .. esc(mapSize) .. "|" .. esc(mapType)
    .. "|" .. maxPlayers .. "|" .. maxTurns)
end)

-- ---- Game identity seeds (persistent-archive fingerprint) ---------------
-- GameConfiguration.GetValue / MapConfiguration methods are already
-- confirmed working calls in this file ("GAME_MAX_TURNS", map script).
-- The keys below are config data, not method names: an absent key returns
-- nil, which we report as the -1 unknown sentinel plus a WARN compat note.
-- Never rendered as a real value downstream.
safe("seeds", function()
  local gameSeed, mapSeed = nil, nil
  pcall(function()
    if GameConfiguration and GameConfiguration.GetValue then
      gameSeed = GameConfiguration.GetValue("GAME_SYNC_RANDOM_SEED")
    end
  end)
  pcall(function()
    if MapConfiguration and MapConfiguration.GetValue then
      mapSeed = MapConfiguration.GetValue("RANDOM_SEED")
    end
  end)
  if gameSeed == nil then
    print("WARN|META.seeds|game seed unavailable (GAME_SYNC_RANDOM_SEED nil)")
    gameSeed = -1
  end
  if mapSeed == nil then
    print("WARN|META.seeds|map seed unavailable (RANDOM_SEED nil)")
    mapSeed = -1
  end
  print("SEEDS|" .. tostring(gameSeed) .. "|" .. tostring(mapSeed))
end)

-- ---- Enabled victories --------------------------------------------------
safe("victories", function()
  local vlist = {}
  local vtypes = {"VICTORY_TECHNOLOGY","VICTORY_CULTURE","VICTORY_RELIGIOUS","VICTORY_CONQUEST","VICTORY_SCORE"}
  for _, vt in ipairs(vtypes) do
    local row = GameInfo.Victories[vt]
    if row then
      local okv, en = pcall(function() return Game.IsVictoryEnabled(row.Index) end)
      if okv and en then vlist[#vlist+1] = vt end
    end
  end
  print("VICT|" .. table.concat(vlist, ","))
end)

-- ---- EMPIRE totals -----------------------------------------------------
safe("empire", function()
  local t   = p:GetTreasury()
  local tec = p:GetTechs()
  local cul = p:GetCulture()
  local rel = p:GetReligion()
  local st  = p:GetStats()
  local trd = p:GetTrade()

  local score = sf(function() return p:GetScore() end) or 0
  local gold  = sf(function() return t:GetGoldBalance() end) or 0
  local goldY = sf(function() return t:GetGoldYield() end) or 0
  local goldM = sf(function() return t:GetTotalMaintenance() end) or 0
  local sci   = sf(function() return tec:GetScienceYield() end) or 0
  local cult  = sf(function() return cul:GetCultureYield() end) or 0
  local faith = sf(function() return rel:GetFaithBalance() end) or 0
  local faithY = sf(function() return rel:GetFaithYield() end) or 0
  local tour  = sf(function() return st:GetTourism() end) or 0
  local mil   = sf(function() return st:GetMilitaryStrength() end) or 0
  local techsN = sf(function() return st:GetNumTechsResearched() end) or 0
  local civicsN = sf(function() return st:GetNumCivicsCompleted() end) or 0

  local nCities, totalPop, nUnits = 0, 0, 0
  pcall(function()
    for _, c in p:GetCities():Members() do
      nCities = nCities + 1
      totalPop = totalPop + (sf(function() return c:GetPopulation() end) or 0)
    end
  end)
  pcall(function() for _, u in p:GetUnits():Members() do nUnits = nUnits + 1 end end)

  local tradeUsed = sf(function() return trd:GetNumOutgoingRoutes() end) or 0
  local tradeCap  = sf(function() return trd:GetOutgoingRouteCapacity() end) or 0

  local revLand, totalLand = 0, 0
  pcall(function()
    local pVis = PlayersVisibility and PlayersVisibility[me] or nil
    local totalPlots = Map.GetPlotCount() or 0
    for i = 0, totalPlots - 1 do
      local plot = Map.GetPlotByIndex(i)
      if plot and not plot:IsWater() then
        totalLand = totalLand + 1
        if pVis and pVis:IsRevealed(plot:GetX(), plot:GetY()) then revLand = revLand + 1 end
      end
    end
  end)

  print(string.format("EMPIRE|%d|%.1f|%.1f|%.1f|%.1f|%.1f|%.1f|%.1f|%.1f|%.1f|%d|%d|%d|%d|%d|%d|%d|%d|%d|%d",
    score, gold, goldY, goldM, goldY - goldM,
    sci, cult, faith, faithY, tour,
    mil, techsN, civicsN,
    nCities, nUnits, totalPop,
    tradeUsed, tradeCap, revLand, totalLand))
end)

-- ---- Current tech + civic ----------------------------------------------
safe("current_tech", function()
  local tec = p:GetTechs()
  local ti = sf(function() return tec:GetResearchingTech() end)
  if not ti or ti < 0 then
    print("CURR|TECH||none|0|0|-1|false|")
    return
  end
  local trow = GameInfo.Technologies[ti]
  local typekey = trow and trow.TechnologyType or ""
  local trigger = ""
  pcall(function()
    for row in GameInfo.Boosts() do
      if row.TechnologyType == typekey then trigger = L(row.TriggerDescription or ""); break end
    end
  end)
  print(string.format("CURR|TECH|%s|%s|%.0f|%.0f|%d|%s|%s",
    typekey, esc(L(trow.Name)),
    sf(function() return tec:GetResearchProgress(ti) end) or 0,
    sf(function() return tec:GetResearchCost(ti) end) or 0,
    sf(function() return tec:GetTurnsToResearch(ti) end) or -1,
    tostring(sf(function() return tec:HasBoostBeenTriggered(ti) end)),
    esc(trigger)))
end)

safe("current_civic", function()
  local cul = p:GetCulture()
  local ci = sf(function() return cul:GetProgressingCivic() end)
  if not ci or ci < 0 then
    print("CURR|CIVIC||none|0|0|-1|false|")
    return
  end
  local crow = GameInfo.Civics[ci]
  local typekey = crow and crow.CivicType or ""
  local trigger = ""
  pcall(function()
    for row in GameInfo.Boosts() do
      if row.CivicType == typekey then trigger = L(row.TriggerDescription or ""); break end
    end
  end)
  print(string.format("CURR|CIVIC|%s|%s|%.0f|%.0f|%d|%s|%s",
    typekey, esc(L(crow.Name)),
    sf(function() return cul:GetCulturalProgress(ci) end) or 0,
    sf(function() return cul:GetCultureCost(ci) end) or 0,
    sf(function() return cul:GetTurnsToProgressCivic(ci) end) or -1,
    tostring(sf(function() return cul:HasBoostBeenTriggered(ci) end)),
    esc(trigger)))
end)

-- ---- Resources ---------------------------------------------------------
safe("resources", function()
  local pr = p:GetResources()
  for row in GameInfo.Resources() do
    local cls = row.ResourceClassType or ""
    if cls == "RESOURCECLASS_STRATEGIC" or cls == "RESOURCECLASS_LUXURY" or cls == "RESOURCECLASS_BONUS" then
      local amt = sf(function() return pr:GetResourceAmount(row.Index) end) or 0
      local acc = sf(function() return pr:HasResource(row.Index) end) or false
      if amt > 0 or (cls == "RESOURCECLASS_LUXURY" and acc) then
        local short = cls:gsub("RESOURCECLASS_", "")
        print(string.format("RES|%s|%s|%s|%d|%s",
          short, row.ResourceType, esc(L(row.Name)), amt, tostring(acc)))
      end
    end
  end
end)

-- ---- Government + Policy slots ----------------------------------------
safe("government", function()
  local cul = p:GetCulture()
  local govIdx = sf(function() return cul:GetCurrentGovernment() end) or -1
  local govType, govName = "NONE", "None"
  if govIdx >= 0 then
    local gr = GameInfo.Governments[govIdx]
    if gr then govType = gr.GovernmentType; govName = L(gr.Name) end
  end
  local slotsOpen = sf(function() return cul:GetNumPolicySlotsOpen() end) or 0
  -- PolicyChangeMade() returns true if a change was made THIS turn (no free
  -- change available).  When it errors, assume we don't know and report "?".
  local changed = sf(function() return cul:PolicyChangeMade() end)
  local freeChange = "?"
  if changed ~= nil then freeChange = tostring(not changed) end
  print(string.format("GOVT|%s|%s|%d|%s", govType, esc(govName), slotsOpen, freeChange))
end)

safe("policy_slots", function()
  local cul = p:GetCulture()
  for i = 0, 30 do
    local st_ = sf(function() return cul:GetSlotType(i) end)
    if not st_ or st_ < 0 then break end
    local slotRow = GameInfo.GovernmentSlots and GameInfo.GovernmentSlots[st_]
    local slotType = slotRow and slotRow.GovernmentSlotType or ("SLOT_" .. st_)
    local slotName = slotType:gsub("SLOT_", "")
    local pi = sf(function() return cul:GetSlotPolicy(i) end) or -1
    local pType, pName, pEff = "", "empty", ""
    if pi >= 0 then
      local pol = GameInfo.Policies[pi]
      if pol then
        pType = pol.PolicyType
        pName = L(pol.Name)
        if pol.Description then pEff = L(pol.Description) end
      end
    end
    print(string.format("POLICYSLOT|%d|%s|%s|%s|%s|%s",
      i, slotType, slotName, pType, esc(pName), esc(pEff)))
  end
end)

safe("policy_available", function()
  local cul = p:GetCulture()
  local slottedSet = {}
  for i = 0, 30 do
    local st_ = sf(function() return cul:GetSlotType(i) end)
    if not st_ or st_ < 0 then break end
    local pi = sf(function() return cul:GetSlotPolicy(i) end) or -1
    if pi >= 0 then slottedSet[pi] = true end
  end
  for pol in GameInfo.Policies() do
    local unlocked = sf(function() return cul:IsPolicyUnlocked(pol.Index) end)
    local obsolete = sf(function() return cul:IsPolicyObsolete(pol.Index) end)
    if unlocked and not slottedSet[pol.Index] and not obsolete then
      local slotName = (pol.GovernmentSlotType or ""):gsub("SLOT_", "")
      local eff = pol.Description and L(pol.Description) or ""
      print(string.format("POLICYAVAIL|%s|%s|%s|%s",
        pol.PolicyType, slotName, esc(L(pol.Name)), esc(eff)))
    end
  end
end)

-- ---- Great People ------------------------------------------------------
safe("great_people", function()
  local gpp = sf(function() return p:GetGreatPeoplePoints() end)
  if not gpp or not GameInfo.GreatPersonClasses then return end
  local gpm = sf(function() return Game.GetGreatPeople() end)

  -- ---- Tier 1: GetTimeline() -----------------------------------------
  -- This is what the shipped GreatPeoplePopup.lua reads.  Entries carry
  -- Class / Individual / Cost for every recruitable Great Person.  Build a
  -- per-class lookup keyed by the class hash.
  local timelineByClass = {}
  local timelineOK = false
  if gpm then
    pcall(function()
      local tl = gpm:GetTimeline()
      if type(tl) ~= "table" then return end
      for _, entry in ipairs(tl) do
        local cls = entry.Class or entry.ClassHash
        if cls ~= nil and timelineByClass[cls] == nil then
          timelineByClass[cls] = entry
          timelineOK = true
        end
      end
    end)
  end
  if gpm and not timelineOK then
    print("WARN|META.great_people|GetTimeline() unavailable or empty — falling back")
  end

  -- ---- Tier 3 prep: if everything fails, dump the real method names ---
  -- so the next live run tells us the correct API instead of guessing again.
  local dumpedMethods = false
  local function dumpMethods()
    if dumpedMethods or not gpm then return end
    dumpedMethods = true
    pcall(function()
      local names = {}
      local mt = getmetatable(gpm)
      local idx = mt and mt.__index
      if type(idx) == "table" then
        for k, v in pairs(idx) do
          if type(v) == "function" then names[#names+1] = tostring(k) end
        end
      end
      table.sort(names)
      if #names > 0 then
        print("DIAG|META.great_people.api|Game.GetGreatPeople() methods: " .. table.concat(names, ","))
      else
        print("DIAG|META.great_people.api|could not enumerate methods on GetGreatPeople()")
      end
    end)
  end

  for row in GameInfo.GreatPersonClasses() do
    local pts = sf(function() return gpp:GetPointsTotal(row.Index) end) or 0
    local rate = sf(function() return gpp:GetPointsPerTurn(row.Index) end) or 0
    -- -1 is the "unknown" sentinel.  Never report 0, which reads as free.
    local cand, patCost, nextCost = "", -1, -1

    local entry = timelineByClass[row.Hash] or timelineByClass[row.Index]
    if entry then
      -- Tier 1 values
      if entry.Cost and entry.Cost > 0 then nextCost = entry.Cost end
      local indiv = entry.Individual
      if indiv and indiv >= 0 then
        local irow = GameInfo.GreatPersonIndividuals[indiv]
        if irow then cand = L(irow.Name or irow.GreatPersonIndividualType) end
      end
    end

    if gpm then
      -- ---- Tier 2: per-class accessors (may not exist in base game) ----
      if cand == "" then
        local indiv = sf(function() return gpm:GetActiveIndividual(row.Hash) end)
        if indiv and indiv >= 0 then
          local irow = GameInfo.GreatPersonIndividuals[indiv]
          if irow then cand = L(irow.Name or irow.GreatPersonIndividualType) end
        end
      end
      if nextCost < 0 then
        local c = sf(function() return gpm:GetNextRecruitCost(row.Hash) end)
        if c and c > 0 then nextCost = c end
      end
      if nextCost < 0 then
        -- Some builds expose the cost per-player instead.
        local c = sf(function() return gpm:GetRecruitCost(me, row.Hash) end)
        if c and c > 0 then nextCost = c end
      end
      local pc = sf(function() return gpm:GetPatronizationCostFaith(me, row.Hash) end)
      if pc and pc > 0 then patCost = pc end
    end

    if pts > 0 or rate > 0 or (cand ~= "") then
      if nextCost < 0 then dumpMethods() end
      local shortName = row.GreatPersonClassType:gsub("GREAT_PERSON_CLASS_", "")
      print(string.format("GPPT|%s|%s|%.0f|%.1f|%d|%s|%d",
        row.GreatPersonClassType, esc(shortName), pts, rate, nextCost, esc(cand), patCost))
    end
  end
end)

""" + _sentinel_line()


# ---------------------------------------------------------------------------
# Q2 — tech + civic choices (per-item pcall so one bad row can't kill the loop)
# ---------------------------------------------------------------------------

def build_choices_query() -> str:
    return _prelude("CHOICES") + r"""

local tec = p:GetTechs()
local cul = p:GetCulture()

-- Boost lookup
local boostsByTech, boostsByCivic = {}, {}
pcall(function()
  for b in GameInfo.Boosts() do
    if b.TechnologyType then boostsByTech[b.TechnologyType] = b end
    if b.CivicType then boostsByCivic[b.CivicType] = b end
  end
end)

-- Probe which availability methods actually exist in this build.
-- `tec:CanResearch` is confirmed present on the live base game.  The civic
-- equivalent is NOT (`CanProgressCivic` is missing), so we probe several
-- known spellings and otherwise fall back to real prerequisite gating via
-- GameInfo.CivicPrereqs — never to "every unresearched civic", which listed
-- 43 entries including Guilds/Exploration/Divine Right in the v1.0 output.
local hasCanResearch  = type(tec.CanResearch) == "function"
local civicCanFn = nil
local civicCanName = ""
for _, nm in ipairs({"CanProgressCivic", "CanProgress", "CanAdvanceCivic"}) do
  if type(cul[nm]) == "function" then civicCanFn = cul[nm]; civicCanName = nm; break end
end
-- Probe outcomes are compatibility notes, not failures — WARN channel.
if not hasCanResearch then
  print("WARN|CHOICES.probe|tec:CanResearch missing — falling back to !HasTech")
end
if civicCanFn then
  print("WARN|CHOICES.probe|using cul:" .. civicCanName .. "() for civic availability")
else
  print("WARN|CHOICES.probe|no civic availability method found — using GameInfo.CivicPrereqs gating")
end

-- Build civic -> {prereq civic type, ...}.  Table name confirmed in this
-- repo at src/civ_mcp/lua/tech.py:95.
local civicPrereqs = {}
local prereqTableOK = false
pcall(function()
  for row in GameInfo.CivicPrereqs() do
    if not civicPrereqs[row.Civic] then civicPrereqs[row.Civic] = {} end
    table.insert(civicPrereqs[row.Civic], row.PrereqCivic)
    prereqTableOK = true
  end
end)
if not prereqTableOK then
  print("WARN|CHOICES.probe|GameInfo.CivicPrereqs unavailable — civic list may be over-broad")
end

-- Completed-civic set, by CivicType string, for prereq resolution.
local completedCivics = {}
pcall(function()
  for civic in GameInfo.Civics() do
    if sf(function() return cul:HasCivic(civic.Index) end) then
      completedCivics[civic.CivicType] = true
    end
  end
end)

-- A civic is selectable when every one of its prereqs is already completed.
-- Civics with no prereq rows are era-openers and are treated as available.
local function civicPrereqsMet(civicType)
  local reqs = civicPrereqs[civicType]
  if not reqs then return true end
  for _, req in ipairs(reqs) do
    if not completedCivics[req] then return false end
  end
  return true
end

-- Tech prereq map.  Table name TechnologyPrereqs confirmed in this repo at
-- src/civ_mcp/lua/tech.py:45 (row.Technology / row.PrereqTech).
local techPrereqs = {}
local techPrereqTableOK = false
pcall(function()
  for row in GameInfo.TechnologyPrereqs() do
    if not techPrereqs[row.Technology] then techPrereqs[row.Technology] = {} end
    table.insert(techPrereqs[row.Technology], row.PrereqTech)
    techPrereqTableOK = true
  end
end)
if not techPrereqTableOK then
  print("WARN|CHOICES.probe|GameInfo.TechnologyPrereqs unavailable — tech tree prereqs empty")
end

-- Current research/civic indexes, for tree status tagging.
local curTechIdx = sf(function() return tec:GetResearchingTech() end) or -1
local curCivicIdx = sf(function() return cul:GetProgressingCivic() end) or -1

local function short(s, prefix) return (s or ""):gsub(prefix, "") end

-- ---- Full tech tree -----------------------------------------------------
-- One TTREE line per technology: status is done/current/available/blocked.
-- Partial research (progress > 0 on a non-done tech) is derivable from the
-- prog field — Civ 6 keeps partial progress when you switch research.
safe("tech_tree", function()
  for tech in GameInfo.Technologies() do
    pcall(function()
      local has = sf(function() return tec:HasTech(tech.Index) end)
      local status
      local prog, cost, turns = 0, 0, -1
      if has then
        status = "done"
      else
        cost = sf(function() return tec:GetResearchCost(tech.Index) end) or 0
        prog = sf(function() return tec:GetResearchProgress(tech.Index) end) or 0
        if tech.Index == curTechIdx then
          status = "current"
        elseif hasCanResearch then
          local can = sf(function() return tec:CanResearch(tech.Index) end)
          status = can and "available" or "blocked"
        else
          -- CanResearch missing (probed above, WARN already emitted):
          -- fall back to prereq gating so we never mark everything blocked.
          local reqs = techPrereqs[tech.TechnologyType]
          local met = true
          if reqs then
            for _, req in ipairs(reqs) do
              local rrow = GameInfo.Technologies[req]
              if rrow and not sf(function() return tec:HasTech(rrow.Index) end) then met = false; break end
            end
          end
          status = met and "available" or "blocked"
        end
        if status == "current" or status == "available" then
          turns = sf(function() return tec:GetTurnsToResearch(tech.Index) end) or -1
        end
      end
      local prereqStr = ""
      if techPrereqs[tech.TechnologyType] then
        local pp = {}
        for _, req in ipairs(techPrereqs[tech.TechnologyType]) do pp[#pp+1] = short(req, "TECH_") end
        prereqStr = table.concat(pp, ",")
      end
      print(string.format("TTREE|%s|%s|%s|%s|%.0f|%.0f|%d|%s",
        tech.TechnologyType, esc(L(tech.Name)), short(tech.EraType, "ERA_"),
        status, prog, cost, turns, esc(prereqStr)))
    end)
  end
end)

-- ---- Full civic tree ----------------------------------------------------
safe("civic_tree", function()
  for civic in GameInfo.Civics() do
    pcall(function()
      local has = sf(function() return cul:HasCivic(civic.Index) end)
      local status
      local prog, cost, turns = 0, 0, -1
      if has then
        status = "done"
      else
        cost = sf(function() return cul:GetCultureCost(civic.Index) end) or 0
        prog = sf(function() return cul:GetCulturalProgress(civic.Index) end) or 0
        if civic.Index == curCivicIdx then
          status = "current"
        elseif civicCanFn then
          local ok_c, can = pcall(civicCanFn, cul, civic.Index)
          status = (ok_c and can) and "available" or "blocked"
        else
          status = civicPrereqsMet(civic.CivicType) and "available" or "blocked"
        end
        if status == "current" or status == "available" then
          turns = sf(function() return cul:GetTurnsToProgressCivic(civic.Index) end) or -1
        end
      end
      local prereqStr = ""
      if civicPrereqs[civic.CivicType] then
        local pp = {}
        for _, req in ipairs(civicPrereqs[civic.CivicType]) do pp[#pp+1] = short(req, "CIVIC_") end
        prereqStr = table.concat(pp, ",")
      end
      print(string.format("CTREE|%s|%s|%s|%s|%.0f|%.0f|%d|%s",
        civic.CivicType, esc(L(civic.Name)), short(civic.EraType, "ERA_"),
        status, prog, cost, turns, esc(prereqStr)))
    end)
  end
end)

safe("techs_available", function()
  for tech in GameInfo.Technologies() do
    pcall(function()
      local has = sf(function() return tec:HasTech(tech.Index) end)
      if has then return end
      if hasCanResearch then
        local can = sf(function() return tec:CanResearch(tech.Index) end)
        if not can then return end
      end
      local cost = sf(function() return tec:GetResearchCost(tech.Index) end) or 0
      local prog = sf(function() return tec:GetResearchProgress(tech.Index) end) or 0
      local turns = sf(function() return tec:GetTurnsToResearch(tech.Index) end) or -1
      local boosted = sf(function() return tec:HasBoostBeenTriggered(tech.Index) end)
      local trig = ""
      local b = boostsByTech[tech.TechnologyType]
      if b and b.TriggerDescription then trig = L(b.TriggerDescription) end
      local unlocks = {}
      for u in GameInfo.Units() do if u.PrereqTech == tech.TechnologyType then unlocks[#unlocks+1] = L(u.Name) end end
      for bl in GameInfo.Buildings() do if bl.PrereqTech == tech.TechnologyType then unlocks[#unlocks+1] = L(bl.Name) end end
      for d in GameInfo.Districts() do if d.PrereqTech == tech.TechnologyType then unlocks[#unlocks+1] = L(d.Name) end end
      for imp in GameInfo.Improvements() do if imp.PrereqTech == tech.TechnologyType then unlocks[#unlocks+1] = L(imp.Name) end end
      for r in GameInfo.Resources() do if r.PrereqTech == tech.TechnologyType then unlocks[#unlocks+1] = "Reveals " .. L(r.Name) end end
      print(string.format("TAV|%s|%s|%.0f|%.0f|%d|%s|%s|%s",
        tech.TechnologyType, esc(L(tech.Name)),
        prog, cost, turns, tostring(boosted),
        esc(trig), esc(table.concat(unlocks, ", "))))
    end)
  end
end)

safe("civics_available", function()
  for civic in GameInfo.Civics() do
    pcall(function()
      local has = sf(function() return cul:HasCivic(civic.Index) end)
      if has then return end
      if civicCanFn then
        local ok_c, can = pcall(civicCanFn, cul, civic.Index)
        if not ok_c or not can then return end
      elseif not civicPrereqsMet(civic.CivicType) then
        -- Prereq civics not yet completed — this is not selectable now.
        return
      end
      local cost = sf(function() return cul:GetCultureCost(civic.Index) end) or 0
      local prog = sf(function() return cul:GetCulturalProgress(civic.Index) end) or 0
      local turns = sf(function() return cul:GetTurnsToProgressCivic(civic.Index) end) or -1
      local boosted = sf(function() return cul:HasBoostBeenTriggered(civic.Index) end)
      local trig = ""
      local b = boostsByCivic[civic.CivicType]
      if b and b.TriggerDescription then trig = L(b.TriggerDescription) end
      local unlocks = {}
      for pol in GameInfo.Policies() do
        if pol.PrereqCivic == civic.CivicType then unlocks[#unlocks+1] = L(pol.Name) end
      end
      for gov in GameInfo.Governments() do
        if gov.PrereqCivic == civic.CivicType then unlocks[#unlocks+1] = "Government: " .. L(gov.Name) end
      end
      print(string.format("CAV|%s|%s|%.0f|%.0f|%d|%s|%s|%s",
        civic.CivicType, esc(L(civic.Name)),
        prog, cost, turns, tostring(boosted),
        esc(trig), esc(table.concat(unlocks, ", "))))
    end)
  end
end)

""" + _sentinel_line()


# ---------------------------------------------------------------------------
# Q3 — cities (per-city, per-subsection pcall isolation)
# ---------------------------------------------------------------------------

def build_cities_query() -> str:
    return _prelude("CITIES") + r"""

-- Build hash → type-key lookup for production items.
local hashName = {}
pcall(function()
  for u in GameInfo.Units() do hashName[u.Hash] = u.UnitType end
  for b in GameInfo.Buildings() do hashName[b.Hash] = b.BuildingType end
  for d in GameInfo.Districts() do hashName[d.Hash] = d.DistrictType end
  for pr in GameInfo.Projects() do hashName[pr.Hash] = pr.ProjectType end
end)

local ccCenterIdx = GameInfo.Districts["DISTRICT_CITY_CENTER"] and GameInfo.Districts["DISTRICT_CITY_CENTER"].Index

-- Resource visibility honours PrereqTech, same rule as the map query.
local cpTech = sf(function() return p:GetTechs() end)
local function resVisible(rr)
  if not rr.PrereqTech then return true end
  if not cpTech then return false end
  local t = GameInfo.Technologies[rr.PrereqTech]
  return t and sf(function() return cpTech:HasTech(t.Index) end) or false
end

-- One-shot WARN flags for the probed city-status accessors (G0).
local statusGrowthWarned = false
local statusWWWarned = false
local plotYieldWarned = false

-- Static building yield table (GameInfo.Building_YieldChanges — standard
-- base-game DB).  These are BASE values, tagged static_db downstream:
-- they don't include percentage modifiers.
local bldgYieldDB = {}
pcall(function()
  for row in GameInfo.Building_YieldChanges() do
    if not bldgYieldDB[row.BuildingType] then bldgYieldDB[row.BuildingType] = {} end
    bldgYieldDB[row.BuildingType][row.YieldType] =
      (bldgYieldDB[row.BuildingType][row.YieldType] or 0) + (row.YieldChange or 0)
  end
end)

local function ysrcLine(cid, src, t)
  return string.format("YSRC|%d|%s|%.1f|%.1f|%.1f|%.1f|%.1f|%.1f",
    cid, src,
    t["YIELD_FOOD"] or 0, t["YIELD_PRODUCTION"] or 0, t["YIELD_GOLD"] or 0,
    t["YIELD_SCIENCE"] or 0, t["YIELD_CULTURE"] or 0, t["YIELD_FAITH"] or 0)
end

for _, c in p:GetCities():Members() do
  local cID = -1
  pcall(function() cID = c:GetID() end)
  print("TRACE|CITY|" .. cID .. "|start")

  -- --- Header --------------------------------------------------------
  pcall(function()
    local cName = "?"; pcall(function() cName = L(c:GetName()) end)
    local cx, cy = -1, -1
    pcall(function() cx = c:GetX(); cy = c:GetY() end)
    local pop = sf(function() return c:GetPopulation() end) or 0
    local isCap = sf(function() return c:IsCapital() end) or false

    -- Growth subsection
    local food, grow, starve, hous, am, amN, happ = 0, -1, -1, 0, 0, 0, 0
    pcall(function()
      local g = c:GetGrowth()
      if g then
        food = sf(function() return g:GetFoodSurplus() end) or 0
        grow = sf(function() return g:GetTurnsUntilGrowth() end) or -1
        starve = sf(function() return g:GetTurnsUntilStarvation() end) or -1
        hous = sf(function() return g:GetHousing() end) or 0
        am   = sf(function() return g:GetAmenities() end) or 0
        amN  = sf(function() return g:GetAmenitiesNeeded() end) or 0
        happ = sf(function() return g:GetHappiness() end) or 0
      end
    end)

    -- Border expansion timer.  City culture object name varies by state;
    -- try GetCulture first, then GetCulturalIdentity fallback.
    local expT = -1
    pcall(function()
      local ccul = sf(function() return c:GetCulture() end)
      if ccul then expT = sf(function() return ccul:GetTurnsUntilExpansion() end) or -1 end
    end)

    -- Yields
    local F, Pr, G, S, Cy, Fa = 0, 0, 0, 0, 0, 0
    pcall(function()
      F  = sf(function() return c:GetYield(YieldTypes.FOOD) end) or 0
      Pr = sf(function() return c:GetYield(YieldTypes.PRODUCTION) end) or 0
      G  = sf(function() return c:GetYield(YieldTypes.GOLD) end) or 0
      S  = sf(function() return c:GetYield(YieldTypes.SCIENCE) end) or 0
      Cy = sf(function() return c:GetYield(YieldTypes.CULTURE) end) or 0
      Fa = sf(function() return c:GetYield(YieldTypes.FAITH) end) or 0
    end)

    -- Production
    local prodType, prodName, prodProg, prodCost, prodTurns = "nothing", "nothing", 0, 0, 0
    pcall(function()
      local bq = c:GetBuildQueue()
      local prodHash = sf(function() return bq:GetCurrentProductionTypeHash() end) or 0
      if prodHash ~= 0 then
        prodType = hashName[prodHash] or ("HASH_" .. prodHash)
        local row = GameInfo.Types[prodHash]
        if row then
          local kind = row.Kind
          if kind == "KIND_UNIT" then
            local r = GameInfo.Units[prodType]
            if r then
              prodName = L(r.Name)
              prodProg = sf(function() return bq:GetUnitProgress(r.Index) end) or 0
              prodCost = sf(function() return bq:GetUnitCost(r.Index) end) or 0
            end
          elseif kind == "KIND_BUILDING" then
            local r = GameInfo.Buildings[prodType]
            if r then
              prodName = L(r.Name)
              prodProg = sf(function() return bq:GetBuildingProgress(r.Index) end) or 0
              prodCost = sf(function() return bq:GetBuildingCost(r.Index) end) or 0
            end
          elseif kind == "KIND_DISTRICT" then
            local r = GameInfo.Districts[prodType]
            if r then
              prodName = L(r.Name)
              prodProg = sf(function() return bq:GetDistrictProgress(r.Index) end) or 0
              prodCost = sf(function() return bq:GetDistrictCost(r.Index) end) or 0
            end
          elseif kind == "KIND_PROJECT" then
            local r = GameInfo.Projects[prodType]
            if r then
              prodName = L(r.Name)
              prodProg = sf(function() return bq:GetProjectProgress(r.Index) end) or 0
              prodCost = sf(function() return bq:GetProjectCost(r.Index) end) or 0
            end
          end
        end
      end
      prodTurns = sf(function() return bq:GetTurnsLeft() end) or 0
    end)

    -- Defense
    local defStr, garHP, garMax, wallHP, wallMax = 0, 0, 0, 0, 0
    pcall(function()
      if ccCenterIdx then
        for _, d in c:GetDistricts():Members() do
          if d:GetType() == ccCenterIdx then
            defStr = sf(function() return d:GetDefenseStrength() end) or 0
            garMax = sf(function() return d:GetMaxDamage(DefenseTypes.DISTRICT_GARRISON) end) or 0
            garHP  = garMax - (sf(function() return d:GetDamage(DefenseTypes.DISTRICT_GARRISON) end) or 0)
            wallMax = sf(function() return d:GetMaxDamage(DefenseTypes.DISTRICT_OUTER) end) or 0
            wallHP  = wallMax - (sf(function() return d:GetDamage(DefenseTypes.DISTRICT_OUTER) end) or 0)
            break
          end
        end
      end
    end)

    -- City-level religion majority
    local relMajType = "NONE"
    pcall(function()
      local cr = c:GetReligion()
      if cr then
        local relIdx = sf(function() return cr:GetMajorityReligion() end) or -1
        if relIdx >= 0 then
          local r = GameInfo.Religions[relIdx]
          if r then relMajType = r.ReligionType end
        end
      end
    end)

    print(string.format("CITY|%d|%s|%s|%d|%d|%d|%.1f|%d|%d|%d|%d|%d|%d|%.1f|%.1f|%.1f|%.1f|%.1f|%.1f|%s|%s|%.0f|%.0f|%d|%d|%d|%d|%d|%d|%d|%s",
      cID, esc(cName), tostring(isCap),
      cx, cy, pop, food, grow, starve,
      hous, am, amN, happ,
      F, Pr, G, S, Cy, Fa,
      prodType, esc(prodName), prodProg, prodCost, prodTurns,
      defStr, garHP, garMax, wallHP, wallMax,
      expT, relMajType))
  end)

  -- --- City status labels (Reports → City Status) -----------------------
  -- Happiness label + growth modifier come straight from the
  -- GameInfo.Happinesses row for the city's happiness index (direct DB,
  -- localized — the same data the report renders).  The live growth
  -- modifier and war weariness are probed accessors: -999/-1 unknown
  -- sentinels + one WARN per snapshot when absent, never a guess.
  pcall(function()
    print("TRACE|CITY|" .. cID .. "|status")
    local g2 = sf(function() return c:GetGrowth() end)
    if not g2 then return end
    local happIdx = sf(function() return g2:GetHappiness() end) or -1
    local happLabel, dbGrowthMod = "?", -999
    if happIdx >= 0 then
      local hr = GameInfo.Happinesses[happIdx]
      if hr then
        if hr.Name then happLabel = L(hr.Name) end
        if hr.GrowthModifier ~= nil then dbGrowthMod = hr.GrowthModifier end
      end
    end
    local liveGrowthMod = -999
    if type(g2.GetHappinessGrowthModifier) == "function" then
      liveGrowthMod = sf(function() return g2:GetHappinessGrowthModifier() end) or -999
    elseif not statusGrowthWarned then
      statusGrowthWarned = true
      print("WARN|CITIES.status|GetHappinessGrowthModifier unavailable — live growth modifier unknown")
    end
    local warWeary = -1
    local wwName = nil
    for _, nm in ipairs({"GetWarWeariness", "GetWarWearinessBreakdown"}) do
      if type(g2[nm]) == "function" then wwName = nm; break end
    end
    if wwName then
      local v = sf(function() return g2[wwName](g2) end)
      if type(v) == "number" then warWeary = v end
    elseif not statusWWWarned then
      statusWWWarned = true
      print("WARN|CITIES.status|war weariness accessor unavailable (tried GetWarWeariness, GetWarWearinessBreakdown)")
    end
    print(string.format("CITYSTATUS|%d|%s|%d|%d|%d",
      cID, esc(happLabel), dbGrowthMod, liveGrowthMod, warWeary))
  end)

  -- --- Districts + buildings in each ------------------------------------
  local cityBldgY = {}
  pcall(function()
    print("TRACE|CITY|" .. cID .. "|districts")
    for _, d in c:GetDistricts():Members() do
      pcall(function()
        local dr = GameInfo.Districts[d:GetType()]
        if not dr then return end
        local adjParts = {}
        pcall(function()
          for yrow in GameInfo.Yields() do
            local av = sf(function() return d:GetAdjacencyYield(yrow.Index) end) or 0
            if av > 0 then
              adjParts[#adjParts+1] = string.format("%s:%d", yrow.YieldType:gsub("YIELD_", ""), av)
            end
          end
        end)
        local dx = sf(function() return d:GetX() end) or -1
        local dy = sf(function() return d:GetY() end) or -1
        local pill = sf(function() return d:IsPillaged() end) or false
        print(string.format("DIST|%d|%s|%s|%d|%d|%s|%s",
          cID, dr.DistrictType, esc(L(dr.Name)),
          dx, dy, tostring(pill), table.concat(adjParts, ",")))
        -- Buildings at this district's plot
        pcall(function()
          local blds = c:GetBuildings()
          if not blds then return end
          local plot = Map.GetPlot(dx, dy)
          if not plot then return end
          local plotID = plot:GetIndex()
          local btypes = sf(function() return blds:GetBuildingsAtLocation(plotID) end) or {}
          for _, bt in ipairs(btypes) do
            local br = GameInfo.Buildings[bt]
            if br then
              local pillB = sf(function() return blds:IsPillaged(bt) end) or false
              print(string.format("BLDG|%d|%s|%s|%s|%s|%s",
                cID, dr.DistrictType, br.BuildingType, esc(L(br.Name)),
                tostring(br.IsWonder), tostring(pillB)))
              -- Static DB base yields of intact buildings (yield-source
              -- breakdown; pillaged buildings yield nothing).
              if not pillB and bldgYieldDB[br.BuildingType] then
                for yt, yv in pairs(bldgYieldDB[br.BuildingType]) do
                  cityBldgY[yt] = (cityBldgY[yt] or 0) + yv
                end
              end
            end
          end
        end)
      end)
    end
  end)

  -- Buildings yield-source line (emitted even when empty so "no
  -- buildings" and "districts query broke" stay distinguishable via
  -- section status, not via a missing line).
  pcall(function() print(ysrcLine(cID, "buildings_db", cityBldgY)) end)

  -- --- Owned tiles rollup ------------------------------------------------
  pcall(function()
    print("TRACE|CITY|" .. cID .. "|tiles")
    local plotList = sf(function() return Map.GetCityPlots():GetPurchasedPlots(c) end) or {}
    local terr, feat, imp = {}, {}, {}
    local workedY = {}
    local workedCount = 0
    for _, pid in ipairs(plotList) do
      local pl = Map.GetPlotByIndex(pid)
      if pl then
        pcall(function()
          local tt = pl:GetTerrainType()
          if tt and tt >= 0 then
            local ti = GameInfo.Terrains[tt]
            if ti then
              local tk = ti.TerrainType:gsub("TERRAIN_", ""):lower()
              terr[tk] = (terr[tk] or 0) + 1
            end
          end
        end)
        pcall(function()
          local ft = pl:GetFeatureType()
          if ft and ft >= 0 then
            local fi = GameInfo.Features[ft]
            if fi then
              local fk = fi.FeatureType:gsub("FEATURE_", ""):lower()
              feat[fk] = (feat[fk] or 0) + 1
            end
          end
        end)
        pcall(function()
          local it = pl:GetImprovementType()
          if it and it >= 0 then
            local ii = GameInfo.Improvements[it]
            if ii then
              local ik = ii.ImprovementType:gsub("IMPROVEMENT_", ""):lower()
              imp[ik] = (imp[ik] or 0) + 1
            end
          end
        end)
        pcall(function()
          local wc = pl:GetWorkerCount() or 0
          if wc > 0 then
            workedCount = workedCount + 1
            -- Worked-tile yield sums (plot:GetYield confirmed available by
            -- the v1.4.0 live probe; guarded anyway, WARN once if absent).
            if type(pl.GetYield) == "function" then
              for yrow in GameInfo.Yields() do
                local yv = sf(function() return pl:GetYield(yrow.Index) end) or 0
                workedY[yrow.YieldType] = (workedY[yrow.YieldType] or 0) + yv
              end
            elseif not plotYieldWarned then
              plotYieldWarned = true
              print("WARN|CITIES.yield_sources|plot:GetYield unavailable — worked-tile yields unknown")
            end
          end
        end)
        -- Owned-resource inventory (Reports → Resources): one line per
        -- resource plot this city owns.  Includes bonus resources (which
        -- never appear in p:GetResources() stockpiles).  "improved" is
        -- the direct observation that an improvement sits on the tile.
        pcall(function()
          local rt = pl:GetResourceType()
          if rt and rt >= 0 then
            local rr = GameInfo.Resources[rt]
            if rr and resVisible(rr) then
              local cls = (rr.ResourceClassType or ""):gsub("RESOURCECLASS_", "")
              local improved = (sf(function() return pl:GetImprovementType() end) or -1) >= 0
              local worked = (sf(function() return pl:GetWorkerCount() end) or 0) > 0
              print(string.format("CITYRES|%d|%s|%s|%s|%s|%s",
                cID, rr.ResourceType, cls, esc(L(rr.Name)),
                tostring(improved), tostring(worked)))
            end
          end
        end)
      end
    end
    local function fmt(tbl)
      local r = {}
      for k, v in pairs(tbl) do r[#r+1] = v .. ":" .. k end
      table.sort(r, function(a, b)
        local an = tonumber(a:match("^(%d+)")) or 0
        local bn = tonumber(b:match("^(%d+)")) or 0
        return an > bn
      end)
      return table.concat(r, ",")
    end
    print(string.format("TILES|%d|%d|%d|%s|%s|%s",
      cID, #plotList, workedCount, fmt(terr), fmt(feat), fmt(imp)))
    if not plotYieldWarned then
      print(ysrcLine(cID, "worked_tiles", workedY))
    end
  end)

  -- --- Production options ------------------------------------------------
  pcall(function()
    print("TRACE|CITY|" .. cID .. "|prod_options")
    local bq = sf(function() return c:GetBuildQueue() end)
    if not bq then return end
    for u in GameInfo.Units() do
      pcall(function()
        local can = sf(function() return bq:CanProduce(u.Hash, true) end)
        if not can then return end
        local prog = sf(function() return bq:GetUnitProgress(u.Index) end) or 0
        local cost = sf(function() return bq:GetUnitCost(u.Index) end) or 0
        local turns = -1
        if cost > 0 and prog < cost then
          turns = sf(function() return bq:GetTurnsLeft(u.Hash) end) or -1
        end
        print(string.format("PROD|%d|UNIT|%s|%s|%.0f|%.0f|%d",
          cID, u.UnitType, esc(L(u.Name)), prog, cost, turns))
      end)
    end
    for b in GameInfo.Buildings() do
      pcall(function()
        local can = sf(function() return bq:CanProduce(b.Hash, true) end)
        if not can then return end
        local prog = sf(function() return bq:GetBuildingProgress(b.Index) end) or 0
        local cost = sf(function() return bq:GetBuildingCost(b.Index) end) or 0
        local turns = -1
        if cost > 0 and prog < cost then
          turns = sf(function() return bq:GetTurnsLeft(b.Hash) end) or -1
        end
        print(string.format("PROD|%d|%s|%s|%s|%.0f|%.0f|%d",
          cID, b.IsWonder and "WONDER" or "BLDG", b.BuildingType, esc(L(b.Name)), prog, cost, turns))
      end)
    end
    for d in GameInfo.Districts() do
      if d.DistrictType ~= "DISTRICT_CITY_CENTER" and d.DistrictType ~= "DISTRICT_WONDER" then
        pcall(function()
          local can = sf(function() return bq:CanProduce(d.Hash, true) end)
          if not can then return end
          local prog = sf(function() return bq:GetDistrictProgress(d.Index) end) or 0
          local cost = sf(function() return bq:GetDistrictCost(d.Index) end) or 0
          local turns = -1
          if cost > 0 and prog < cost then
            turns = sf(function() return bq:GetTurnsLeft(d.Hash) end) or -1
          end
          print(string.format("PROD|%d|DIST|%s|%s|%.0f|%.0f|%d",
            cID, d.DistrictType, esc(L(d.Name)), prog, cost, turns))
        end)
      end
    end
    for pr in GameInfo.Projects() do
      pcall(function()
        local can = sf(function() return bq:CanProduce(pr.Hash, true) end)
        if not can then return end
        local prog = sf(function() return bq:GetProjectProgress(pr.Index) end) or 0
        local cost = sf(function() return bq:GetProjectCost(pr.Index) end) or 0
        print(string.format("PROD|%d|PROJ|%s|%s|%.0f|%.0f|%d",
          cID, pr.ProjectType, esc(L(pr.Name)), prog, cost, -1))
      end)
    end
  end)

  -- --- Outgoing trade routes ------------------------------------------
  pcall(function()
    print("TRACE|CITY|" .. cID .. "|trade")
    local ctrade = sf(function() return c:GetTrade() end)
    local routes = ctrade and sf(function() return ctrade:GetOutgoingRoutes() end) or {}
    for _, r in ipairs(routes) do
      pcall(function()
        local destPlayer = r.DestinationCityPlayer
        local dp = Players[destPlayer]
        local dc = dp and sf(function() return dp:GetCities():FindID(r.DestinationCityID) end) or nil
        local destName = dc and esc(L(dc:GetName())) or "(unknown city)"
        -- Resolve the owning civ so the report never shows a raw "player0".
        -- A route to ourselves is a domestic route.
        local destCiv = "?"
        if destPlayer == me then
          destCiv = "domestic"
        else
          pcall(function()
            local dcfg = PlayerConfigurations[destPlayer]
            if dcfg then
              destCiv = L(dcfg:GetCivilizationShortDescription()) or "?"
            end
          end)
        end
        -- Emit full yield names (Food/Production/Gold/Science/Culture/Faith)
        -- rather than a 3-character truncation like FOO/PRO.
        local ys = ""
        for _, y in ipairs(r.OriginYields or {}) do
          if y.Amount and y.Amount ~= 0 then
            local yi = GameInfo.Yields[y.YieldIndex]
            local yname = "?"
            if yi then
              local okY, loc = pcall(function() return L(yi.Name) end)
              if okY and loc and loc ~= "" then
                yname = loc
              else
                yname = yi.YieldType:gsub("YIELD_", "")
                yname = yname:sub(1, 1) .. yname:sub(2):lower()
              end
            end
            ys = ys .. string.format("%s:%d,", esc(yname), y.Amount)
          end
        end
        print(string.format("TRADE|%d|%d|%s|%s|%s",
          cID, destPlayer, destName, ys, esc(destCiv)))
      end)
    end
  end)

  print("TRACE|CITY|" .. cID .. "|end")
end

""" + _sentinel_line()


# ---------------------------------------------------------------------------
# Q4 — units (per-unit pcall isolation)
# ---------------------------------------------------------------------------

def build_units_query() -> str:
    return _prelude("UNITS") + r"""

safe("units", function()
  for _, u in p:GetUnits():Members() do
    pcall(function()
      local uid = sf(function() return u:GetID() end) or -1
      local ut = sf(function() return u:GetType() end)
      local ur = ut and GameInfo.Units[ut] or nil
      local uname = ur and L(ur.Name) or "?"
      local utype = ur and ur.UnitType or "?"
      local uclass = ur and (ur.FormationClass or ur.PromotionClass or "") or ""
      local x = sf(function() return u:GetX() end) or -1
      local y = sf(function() return u:GetY() end) or -1
      local hpMax = sf(function() return u:GetMaxDamage() end) or 0
      local hp = hpMax - (sf(function() return u:GetDamage() end) or 0)
      local mv = sf(function() return u:GetMovesRemaining() end) or 0
      local mvMax = sf(function() return u:GetMaxMoves() end) or 0
      local combat = sf(function() return u:GetCombat() end) or 0
      local ranged = sf(function() return u:GetRangedCombat() end) or 0
      local bombard = sf(function() return u:GetBombardCombat() end) or 0
      local rng = ur and ur.Range or 0
      local xp = sf(function()
        local e = u:GetExperience()
        return e and e:GetExperiencePoints() or 0
      end) or 0
      local xpNeed = sf(function()
        local e = u:GetExperience()
        return e and e:GetExperienceForNextLevel() or 0
      end) or 0
      local promoClass = ur and ur.PromotionClass or ""
      local promoCount = 0
      if promoClass ~= "" then
        pcall(function()
          for pr in GameInfo.UnitPromotions() do
            if pr.PromotionClass == promoClass then
              local has = sf(function() return u:GetExperience():HasPromotion(pr.Index) end)
              if has then promoCount = promoCount + 1 end
            end
          end
        end)
      end
      local charges = sf(function() return u:GetBuildCharges() end) or 0
      if charges == 0 then charges = sf(function() return u:GetSpreadCharges() end) or 0 end
      local fort = sf(function() return u:GetFortifyTurns() end) or 0
      local idle = sf(function() return u:IsReadyToMove() end) or false
      -- Unspent promotion available?
      --
      -- v1.0 derived this from exp:GetLevel() - promotionsHeld, which is
      -- WRONG: a brand-new unit is level 1 with 0 promotions, so every unit
      -- (including Traders and other civilians) falsely reported "+1 avail".
      --
      -- Authoritative source is the same command the UI enables the promote
      -- button from.  Civilians have no PromotionClass and can never promote,
      -- so that guard alone removes the Trader/Builder false positives.
      local promoAvail = 0
      if promoClass ~= "" then
        local decided = false
        pcall(function()
          if UnitManager and UnitManager.CanStartCommand
             and UnitCommandTypes and UnitCommandTypes.PROMOTE then
            local can = UnitManager.CanStartCommand(u, UnitCommandTypes.PROMOTE)
            promoAvail = can and 1 or 0
            decided = true
          end
        end)
        if not decided then
          -- Fallback: a promotion is pending when banked XP has reached the
          -- threshold for the next level.
          if xpNeeded and xpNeeded > 0 and xp >= xpNeeded then
            promoAvail = 1
          end
          print("WARN|UNITS.promotions|UnitManager.CanStartCommand(PROMOTE) unavailable — using XP threshold fallback")
        end
      end
      local canUpgrade, upType, upCost = false, "", 0
      pcall(function()
        if ur and ur.UpgradeUnit then
          local target = GameInfo.Units[ur.UpgradeUnit]
          if target then
            upType = target.UnitType
            upCost = target.Cost or 0
            if UnitManager and UnitManager.CanStartCommand and UnitCommandTypes and UnitCommandTypes.UPGRADE then
              canUpgrade = UnitManager.CanStartCommand(u, UnitCommandTypes.UPGRADE) or false
            end
          end
        end
      end)
      print(string.format("UNIT|%d|%s|%s|%s|%d|%d|%d|%d|%.0f|%.0f|%d|%d|%d|%d|%d|%d|%d|%d|%s|%d|%d|%s|%s|%d",
        uid, utype, esc(uname), esc(uclass),
        x, y, hp, hpMax, mv, mvMax,
        combat, ranged, bombard, rng,
        xp, xpNeed, promoCount, promoAvail,
        tostring(idle), fort, charges, tostring(canUpgrade), upType, upCost))
    end)
  end
end)

safe("barbarian_visibility", function()
  local pVis = PlayersVisibility and PlayersVisibility[me] or nil
  local pBarb = Players and Players[63] or nil
  if not pBarb or not pVis then return end
  for _, bu in pBarb:GetUnits():Members() do
    pcall(function()
      local bx, by = bu:GetX(), bu:GetY()
      if pVis:IsVisible(bx, by) then
        local br = GameInfo.Units[bu:GetType()]
        local nm = br and L(br.Name) or "Barbarian"
        print(string.format("BARB|%s|%d|%d|%d|%d",
          esc(nm), bx, by,
          bu:GetMaxDamage() - bu:GetDamage(), bu:GetMaxDamage()))
      end
    end)
  end
end)

safe("barbarian_camps", function()
  local pVis = PlayersVisibility and PlayersVisibility[me] or nil
  if not pVis then return end
  local plotCount = Map.GetPlotCount() or 0
  for i = 0, plotCount - 1 do
    local pl = Map.GetPlotByIndex(i)
    if pl then
      pcall(function()
        local it = pl:GetImprovementType()
        if it and it >= 0 then
          local ii = GameInfo.Improvements[it]
          if ii and ii.ImprovementType == "IMPROVEMENT_BARBARIAN_CAMP" then
            local px, py = pl:GetX(), pl:GetY()
            if pVis:IsVisible(px, py) then
              print(string.format("CAMPV|%d|%d", px, py))
            elseif pVis:IsRevealed(px, py) then
              print(string.format("CAMPR|%d|%d", px, py))
            end
          end
        end
      end)
    end
  end
end)

""" + _sentinel_line()


# ---------------------------------------------------------------------------
# Q5 — revealed map (unchanged behaviour, per-tile pcall)
# ---------------------------------------------------------------------------

def build_map_query() -> str:
    return _prelude("MAP") + r"""

local pTech = sf(function() return p:GetTechs() end)
local pVis = PlayersVisibility and PlayersVisibility[me] or nil
if not pVis then print("DIAG|MAP|PlayersVisibility unavailable"); print("---END---"); return end

local terrShort = {
  TERRAIN_GRASS = "g", TERRAIN_PLAINS = "p", TERRAIN_DESERT = "d",
  TERRAIN_TUNDRA = "t", TERRAIN_SNOW = "s",
  TERRAIN_GRASS_HILLS = "gh", TERRAIN_PLAINS_HILLS = "ph",
  TERRAIN_DESERT_HILLS = "dh", TERRAIN_TUNDRA_HILLS = "th",
  TERRAIN_SNOW_HILLS = "sh",
  TERRAIN_GRASS_MOUNTAIN = "gm", TERRAIN_PLAINS_MOUNTAIN = "pm",
  TERRAIN_DESERT_MOUNTAIN = "dm", TERRAIN_TUNDRA_MOUNTAIN = "tm",
  TERRAIN_SNOW_MOUNTAIN = "sm",
  TERRAIN_COAST = "co", TERRAIN_OCEAN = "oc"
}
local featShort = {
  FEATURE_FOREST = "for", FEATURE_JUNGLE = "jun", FEATURE_MARSH = "mar",
  FEATURE_FLOODPLAINS = "fld", FEATURE_OASIS = "oas", FEATURE_ICE = "ice",
  FEATURE_REEF = "reef", FEATURE_GEOTHERMAL_FISSURE = "geo",
}

local totalPlots = Map.GetPlotCount() or 0
local mapW = sf(function() return Map.GetGridSize() end) or 0
print("MAPMETA|" .. totalPlots .. "|" .. tostring(mapW))

-- City-name lookup by plot index so city-centre MAP records carry the
-- city's name.  Revealed city banners are visible in the normal UI, so
-- this respects fog: names are only attached to tiles we emit (revealed).
--
-- The same walk emits one RIVALCITY line per non-local city whose centre
-- plot is revealed.  Detail is visibility-tiered: a merely-revealed city
-- gives name/position/capital only (its banner is what the UI shows);
-- population/defense/walls are read only while the plot is currently
-- visible (the banner shows them then).  Defense reads reuse the exact
-- DISTRICT_CITY_CENTER calls the own-cities query ships.  -1 = unknown.
local cityNameAt = {}
local ccIdx = GameInfo.Districts["DISTRICT_CITY_CENTER"]
      and GameInfo.Districts["DISTRICT_CITY_CENTER"].Index or -1
local origOwnerProbed = nil
pcall(function()
  for pid = 0, 63 do
    local pp = Players[pid]
    if pp and pp:IsAlive() then
      local cities = sf(function() return pp:GetCities() end)
      if cities then
        for _, cc in cities:Members() do
          pcall(function()
            local cx, cy = cc:GetX(), cc:GetY()
            local cplot = Map.GetPlot(cx, cy)
            if not cplot then return end
            cityNameAt[cplot:GetIndex()] = L(cc:GetName())
            if pid == me or not pVis:IsRevealed(cx, cy) then return end
            local isVis = pVis:IsVisible(cx, cy)
            local pop, defStr, wallHP, wallMax = -1, -1, -1, -1
            if isVis then
              pop = sf(function() return cc:GetPopulation() end) or -1
              pcall(function()
                for _, d in cc:GetDistricts():Members() do
                  if d:GetType() == ccIdx then
                    defStr = sf(function() return d:GetDefenseStrength() end) or -1
                    wallMax = sf(function() return d:GetMaxDamage(DefenseTypes.DISTRICT_OUTER) end) or -1
                    if wallMax and wallMax > 0 then
                      wallHP = wallMax - (sf(function() return d:GetDamage(DefenseTypes.DISTRICT_OUTER) end) or 0)
                    end
                    break
                  end
                end
              end)
            end
            -- Original founder: probe once (rule 4 — never guess a method).
            if origOwnerProbed == nil then
              origOwnerProbed = (type(cc.GetOriginalOwner) == "function")
              if not origOwnerProbed then
                print("WARN|MAP.rival_cities|GetOriginalOwner unavailable — city founder unknown")
              end
            end
            local orig = -1
            if origOwnerProbed then
              orig = sf(function() return cc:GetOriginalOwner() end)
              if orig == nil then orig = -1 end
            end
            local isCap = sf(function() return cc:IsCapital() end) or false
            print(string.format("RIVALCITY|%d|%s|%d|%d|%s|%s|%d|%d|%d|%d|%d",
              pid, esc(L(cc:GetName())), cx, cy, tostring(isCap),
              isVis and "visible" or "revealed",
              pop, defStr, wallHP, wallMax, orig))
          end)
        end
      end
    end
  end
end)

-- Owner legend: map player id -> readable name, for every id that appears
-- as a tile owner.  Unmet civs are labelled "unmet" — the UI shows their
-- borders but not their identity, so we must not leak names.
local metSet = {}
metSet[me] = true
pcall(function()
  local d = Players[me]:GetDiplomacy()
  for _, q in ipairs(d:GetPlayersMetIDs() or {}) do metSet[q] = true end
end)
local ownerName = {}
local function legendFor(pid)
  if ownerName[pid] ~= nil then return end
  if pid == 63 then
    ownerName[pid] = "Barbarians"
  elseif pid == me then
    local nm = "me"
    pcall(function() nm = "me (" .. L(PlayerConfigurations[pid]:GetCivilizationShortDescription()) .. ")" end)
    ownerName[pid] = nm
  elseif metSet[pid] then
    local nm = "player " .. pid
    pcall(function()
      local pc = PlayerConfigurations[pid]
      if pc then
        nm = L(pc:GetCivilizationShortDescription()) or nm
        local pp = Players[pid]
        if pp and not pp:IsMajor() then nm = nm .. " (city-state)" end
      end
    end)
    ownerName[pid] = nm
  else
    ownerName[pid] = "unmet civilization"
  end
end

-- G0 probe: per-tile yield availability (gates the future yield-breakdown
-- and per-tile-yield features).  One compat note per snapshot.
pcall(function()
  local p0 = Map.GetPlotByIndex(0)
  if p0 then
    if type(p0.GetYield) == "function" then
      print("WARN|MAP.yield_probe|plot:GetYield available — per-tile yields exportable")
    else
      print("WARN|MAP.yield_probe|plot:GetYield NOT available on this build")
    end
  end
end)

local revealed, visible, nwCount = 0, 0, 0

local function res_visible(resRow)
  if not resRow.PrereqTech then return true end
  if not pTech then return false end
  local t = GameInfo.Technologies[resRow.PrereqTech]
  return t and sf(function() return pTech:HasTech(t.Index) end) or false
end

for i = 0, totalPlots - 1 do
  pcall(function()
    local pl = Map.GetPlotByIndex(i)
    if not pl then return end
    local x, y = pl:GetX(), pl:GetY()
    if not pVis:IsRevealed(x, y) then return end
    revealed = revealed + 1
    local isVis = pVis:IsVisible(x, y)
    if isVis then visible = visible + 1 end
    local tCode = "?"
    local tt = sf(function() return pl:GetTerrainType() end)
    if tt and tt >= 0 then
      local tr = GameInfo.Terrains[tt]
      if tr then tCode = terrShort[tr.TerrainType] or tr.TerrainType:gsub("TERRAIN_",""):lower() end
    end
    local fCode = ""
    local ft = sf(function() return pl:GetFeatureType() end)
    if ft and ft >= 0 then
      local fr = GameInfo.Features[ft]
      if fr then
        if fr.NaturalWonder then
          fCode = "nw:" .. fr.FeatureType:gsub("FEATURE_","")
          nwCount = nwCount + 1
          print(string.format("NW|%s|%d|%d|%s", esc(L(fr.Name)), x, y, fr.FeatureType))
        else
          fCode = featShort[fr.FeatureType] or fr.FeatureType:gsub("FEATURE_",""):lower():sub(1,4)
        end
      end
    end
    local rCode = ""
    local rt = sf(function() return pl:GetResourceType() end)
    if rt and rt >= 0 then
      local rr = GameInfo.Resources[rt]
      if rr and res_visible(rr) then
        rCode = rr.ResourceType:gsub("RESOURCE_", "")
        local rcount = sf(function() return pl:GetResourceCount() end) or 0
        if rcount > 1 then rCode = rCode .. "x" .. rcount end
      end
    end
    local iCode = ""
    local it = sf(function() return pl:GetImprovementType() end)
    if it and it >= 0 then
      local ir = GameInfo.Improvements[it]
      if ir then
        iCode = ir.ImprovementType:gsub("IMPROVEMENT_", "")
        local pill = sf(function() return pl:IsImprovementPillaged() end)
        if pill then iCode = iCode .. ":P" end
      end
    end
    local roadCode = ""
    local rte = sf(function() return pl:GetRouteType() end)
    if rte and rte >= 0 then
      local rr = GameInfo.Routes[rte]
      if rr then roadCode = tostring(rr.Level or rte) end
    end
    local owner = sf(function() return pl:GetOwner() end)
    local ownerStr = ""
    if owner and owner >= 0 then
      ownerStr = tostring(owner)
      legendFor(owner)
    end
    local dCode = ""
    local dt = sf(function() return pl:GetDistrictType() end)
    if dt and dt >= 0 then
      local dr = GameInfo.Districts[dt]
      if dr then dCode = dr.DistrictType:gsub("DISTRICT_", "") end
    end
    local isCity = sf(function() return pl:IsCity() end)
    local cityName = ""
    if isCity then
      cityName = cityNameAt[pl:GetIndex()] or ""
    end
    local unitStr = ""
    if isVis then
      pcall(function()
        local pu = Map.GetUnitsAt(x, y)
        if pu then
          local parts = {}
          for un in pu:Units() do
            local o = un:GetOwner()
            local et = GameInfo.Units[un:GetType()]
            local etype = et and et.UnitType or "?"
            local uhp = un:GetMaxDamage() - un:GetDamage()
            parts[#parts+1] = string.format("%d:%s:%d", o, etype:gsub("UNIT_",""), uhp)
          end
          unitStr = table.concat(parts, ";")
        end
      end)
    end
    local extras = {}
    if sf(function() return pl:IsRiver() end) then extras[#extras+1] = "R" end
    if sf(function() return pl:IsLake() end) then extras[#extras+1] = "L" end
    local appeal = sf(function() return pl:GetAppeal() end)
    if appeal and appeal ~= 0 then extras[#extras+1] = "A" .. appeal end
    if sf(function() return pl:IsFreshWater() end) then extras[#extras+1] = "F" end
    local extraStr = table.concat(extras, "/")
    print(string.format("MAP|%d|%d|%d|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s",
      x, y, isVis and 1 or 0,
      tCode, fCode, rCode, iCode, roadCode, ownerStr,
      dCode, tostring(isCity or false), unitStr, extraStr, esc(cityName)))
  end)
end
-- Owner legend — one line per player id that owns at least one revealed tile.
for pid, nm in pairs(ownerName) do
  print(string.format("OWNER|%d|%s", pid, esc(nm)))
end
print(string.format("MAPTOTAL|%d|%d|%d", revealed, visible, nwCount))

""" + _sentinel_line()


# ---------------------------------------------------------------------------
# Q6 — diplomacy
# ---------------------------------------------------------------------------

def build_diplo_query() -> str:
    return _prelude("DIPLO") + r"""

local d = sf(function() return p:GetDiplomacy() end)
if not d then print("DIAG|DIPLO|no diplomacy object"); print("---END---"); return end

safe("envoys", function()
  local inf = sf(function() return p:GetInfluence() end)
  if not inf then return end
  print(string.format("ENVOY|%d|%d|%d|%.1f|%d",
    sf(function() return inf:GetTokensToGive() end) or 0,
    sf(function() return inf:GetPointsEarned() end) or 0,
    sf(function() return inf:GetPointsThreshold() end) or 0,
    sf(function() return inf:GetPointsPerTurn() end) or 0,
    sf(function() return inf:GetTokensPerThreshold() end) or 0))
end)

local majorSet = {}
pcall(function()
  local ids = PlayerManager and PlayerManager.GetAliveMajorIDs and PlayerManager.GetAliveMajorIDs() or {}
  for _, pid in ipairs(ids) do majorSet[pid] = true end
end)

-- Gossip manager discovery (G0 probe, kept as a permanent feature
-- detect) + the wired export below.  The live probe on the user's build
-- confirmed exactly one method: GetRecentVisibleGossipStrings.
local gossipMgr = nil
safe("gossip_probe", function()
  if GameInfo.Gossips then
    local n = 0
    pcall(function() for _ in GameInfo.Gossips() do n = n + 1 end end)
    print("WARN|DIPLO.gossip_probe|GameInfo.Gossips present (" .. n .. " gossip types)")
  else
    print("WARN|DIPLO.gossip_probe|GameInfo.Gossips missing")
  end
  local mgr, how = nil, ""
  pcall(function()
    if type(Game.GetGossipManager) == "function" then
      mgr = Game.GetGossipManager()
      how = "Game.GetGossipManager()"
    end
  end)
  if mgr == nil then
    pcall(function()
      local g = GossipManager
      if g ~= nil then mgr = g; how = "global GossipManager" end
    end)
  end
  if mgr == nil then
    print("WARN|DIPLO.gossip_probe|no gossip manager found (tried Game.GetGossipManager, global GossipManager)")
    return
  end
  print("WARN|DIPLO.gossip_probe|gossip manager found via " .. how)
  gossipMgr = mgr
  pcall(function()
    local names = {}
    local mt = getmetatable(mgr)
    local idx = mt and mt.__index
    if type(idx) == "table" then
      for k, v in pairs(idx) do
        if type(v) == "function" then names[#names+1] = tostring(k) end
      end
    elseif type(mgr) == "table" then
      for k, v in pairs(mgr) do
        if type(v) == "function" then names[#names+1] = tostring(k) end
      end
    end
    table.sort(names)
    if #names > 0 then
      print("DIAG|DIPLO.gossip_probe.api|methods: " .. table.concat(names, ","))
    else
      print("DIAG|DIPLO.gossip_probe.api|could not enumerate gossip manager methods")
    end
  end)
end)

local metIDs = sf(function() return d:GetPlayersMetIDs() end) or {}
local airelWarned = false
local csLocWarned = false

-- Gossip export.  The method NAME was confirmed by the v1.4.0 live probe
-- (the manager's only method: GetRecentVisibleGossipStrings).  Its arity
-- is not documented, so we discover it once by trying known base-game
-- call shapes under pcall and note which one worked.  Entry shapes are
-- handled defensively: strings pass through; tables yield their first
-- string (text) and first number (turn).  -1 = turn unknown.  Only what
-- the game returns is exported — these are the player-visible gossip
-- strings, already localized and visibility-filtered by the engine.
safe("gossip", function()
  if gossipMgr == nil then return end
  local fn = gossipMgr.GetRecentVisibleGossipStrings
  if type(fn) ~= "function" then
    print("WARN|DIPLO.gossip|GetRecentVisibleGossipStrings missing — gossip not exported")
    return
  end
  local arity = nil
  local function fetch(target)
    if arity == nil or arity == 3 then
      local ok, t = pcall(fn, gossipMgr, 0, me, target)
      if ok and type(t) == "table" then arity = 3; return t end
    end
    if arity == nil or arity == 2 then
      local ok, t = pcall(fn, gossipMgr, me, target)
      if ok and type(t) == "table" then arity = 2; return t end
    end
    if arity == nil or arity == 1 then
      local ok, t = pcall(fn, gossipMgr, target)
      if ok and type(t) == "table" then arity = 1; return t end
    end
    return nil
  end
  local emitted, anyFetched = 0, false
  for _, tq in ipairs(metIDs) do
    if tq ~= me and tq ~= 63 then
      local tbl = fetch(tq)
      if tbl then
        anyFetched = true
        for _, e in ipairs(tbl) do
          pcall(function()
            local text, turn = nil, -1
            if type(e) == "string" then
              text = e
            elseif type(e) == "table" then
              for _, v in ipairs(e) do
                if text == nil and type(v) == "string" and v ~= "" then text = v end
                if turn == -1 and type(v) == "number" then turn = v end
              end
              if text == nil then
                for _, k in ipairs({"Message", "Text", "GossipString"}) do
                  if type(e[k]) == "string" and e[k] ~= "" then text = e[k]; break end
                end
              end
              if turn == -1 and type(e.Turn) == "number" then turn = e.Turn end
            end
            if text and text ~= "" then
              print(string.format("GOSSIP|%d|%d|%s", tq, math.floor(turn), esc(text)))
              emitted = emitted + 1
            end
          end)
        end
      end
    end
  end
  if not anyFetched then
    print("WARN|DIPLO.gossip|no call shape of GetRecentVisibleGossipStrings returned a table — gossip not exported")
  elseif arity then
    print("WARN|DIPLO.gossip|gossip fetched via call arity " .. arity .. " (" .. emitted .. " entries)")
  end
end)
for _, q in ipairs(metIDs) do
  pcall(function()
    if q == 63 or q == me then return end
    local op = Players[q]
    local opc = PlayerConfigurations[q]
    if not (op and opc) then return end
    -- A met player who is no longer alive was eliminated — that's public
    -- (the game announces it).  Emit the tombstone instead of silently
    -- dropping them from the met list.
    if not sf(function() return op:IsAlive() end) then
      print(string.format("DEAD|%d|%s|%s|%s",
        q,
        esc(opc:GetCivilizationTypeName()),
        esc(L(opc:GetCivilizationShortDescription())),
        tostring(sf(function() return op:IsMajor() end) or false)))
      return
    end
    local warStr = tostring(sf(function() return d:IsAtWarWith(q) end) or false)
    local metT = sf(function() return d:GetMetTurn(q) end) or -1
    local dvis = sf(function() return d:GetVisibilityOn(q) end) or 0
    local ob = sf(function() return d:HasOpenBordersFrom(q) end) or false
    local obMe = sf(function() return d:HasOpenBordersWith(q) end) or false
    local hasDeleg = sf(function() return d:HasSentDelegationTo(q) end) or false
    local hasEmbassy = sf(function() return d:HasSentEmbassyTo(q) end) or false

    if majorSet[q] then
      local ost = sf(function() return op:GetStats() end)
      local mil = ost and (sf(function() return ost:GetMilitaryStrength() end) or 0) or 0
      local sc = sf(function() return op:GetScore() end) or 0
      local relStateName, relStateIdx = "?", -1
      pcall(function()
        local ai = op:GetDiplomaticAI()
        if ai then
          relStateIdx = ai:GetDiplomaticStateIndex(me) or -1
          if relStateIdx and relStateIdx >= 0 then
            local r = GameInfo.DiplomaticStates[relStateIdx]
            if r then relStateName = r.StateType end
          end
        end
      end)
      print(string.format("MAJOR|%d|%s|%s|%s|%s|%s|%d|%d|%d|%d|%s|%s|%s|%s|%d|%s",
        q,
        esc(opc:GetCivilizationTypeName()),
        esc(L(opc:GetCivilizationShortDescription())),
        esc(opc:GetLeaderTypeName()),
        esc(L(opc:GetLeaderName())),
        warStr, metT, dvis, sc, mil, tostring(ob), tostring(obMe),
        tostring(hasDeleg), tostring(hasEmbassy),
        relStateIdx, esc(relStateName)))
      pcall(function()
        local vals = sf(function() return d:GetLearnedAgendas(q) end) or {}
        for _, ah in ipairs(vals) do
          for a in GameInfo.Agendas() do
            if a.Hash == ah then
              print(string.format("AGENDA|%d|%s|%s", q, a.AgendaType, esc(L(a.Name))))
              break
            end
          end
        end
      end)

      -- Wars of this civ against every other met player (and me).  War
      -- state is public in the base UI, read from the rival's own
      -- diplomacy object with the already-confirmed IsAtWarWith.
      pcall(function()
        local od = op:GetDiplomacy()
        if not od then return end
        local wl = {}
        if sf(function() return od:IsAtWarWith(me) end) then wl[#wl+1] = tostring(me) end
        for _, r in ipairs(metIDs) do
          if r ~= q and r ~= 63 and r ~= me then
            if sf(function() return od:IsAtWarWith(r) end) then wl[#wl+1] = tostring(r) end
          end
        end
        print(string.format("WARS|%d|%s", q, table.concat(wl, ",")))
      end)

      -- Public victory-rankings stats (shown to every player on the base
      -- game's World Rankings screens): techs, civics, tourism.  -1 unknown.
      pcall(function()
        local techsN = ost and (sf(function() return ost:GetNumTechsResearched() end) or -1) or -1
        local civN = ost and (sf(function() return ost:GetNumCivicsCompleted() end) or -1) or -1
        local tourN = ost and (sf(function() return ost:GetTourism() end) or -1) or -1
        print(string.format("PUBSTATS|%d|%d|%d|%d", q, techsN, civN, tourN))
      end)

      -- Rival-to-rival diplomatic states (declared friends / denounced —
      -- announced publicly in game).  Probed per rule 4; non-neutral only
      -- to keep the packet small.
      pcall(function()
        local ai = op:GetDiplomaticAI()
        if not ai or type(ai.GetDiplomaticStateIndex) ~= "function" then
          if not airelWarned then
            airelWarned = true
            print("WARN|DIPLO.airel|GetDiplomaticStateIndex unavailable — rival-rival relations unknown")
          end
          return
        end
        for _, r in ipairs(metIDs) do
          if r ~= q and r ~= 63 and r ~= me and majorSet[r] then
            local idx = sf(function() return ai:GetDiplomaticStateIndex(r) end)
            if idx and idx >= 0 then
              local row = GameInfo.DiplomaticStates[idx]
              local stype = row and row.StateType or "?"
              if stype ~= "DIPLO_STATE_NEUTRAL" then
                print(string.format("AIREL|%d|%d|%s", q, r, esc(stype)))
              end
            end
          end
        end
      end)

      -- Rival government — emitted ONLY at diplomatic visibility >= 1
      -- (limited access shows it on the leader screen); the API would
      -- return the true value regardless, so the gate lives here, not in
      -- the renderer.  Tagged with the visibility level it was read at.
      if dvis and dvis >= 1 then
        pcall(function()
          local oc = op:GetCulture()
          local gi = oc and sf(function() return oc:GetCurrentGovernment() end)
          if gi and gi >= 0 then
            local gr = GameInfo.Governments[gi]
            if gr then
              print(string.format("RIVGOV|%d|%s|%s|%d", q, gr.GovernmentType, esc(L(gr.Name)), dvis))
            end
          end
        end)
      end
    else
      -- City-state
      local oinf = sf(function() return op:GetInfluence() end)
      local sent = oinf and (sf(function() return oinf:GetTokensReceived(me) end) or 0) or 0
      local suz = oinf and (sf(function() return oinf:GetSuzerain() end) or -1) or -1
      local suzStr = "none"
      if suz and suz >= 0 then
        if suz == me then suzStr = "ME"
        else
          local sc = PlayerConfigurations[suz]
          suzStr = sc and (sc:GetCivilizationTypeName() or "?"):gsub("CIVILIZATION_", "") or ("p" .. suz)
        end
      end
      local csType = "?"
      pcall(function()
        local lt = opc:GetLeaderTypeName() or ""
        csType = lt:gsub("LEADER_MINOR_CIV_", "")
      end)
      local csx, csy = -1, -1
      pcall(function()
        local cc = op:GetCities():GetCapitalCity()
        if cc then csx, csy = cc:GetX(), cc:GetY() end
      end)
      print(string.format("CS|%d|%s|%s|%s|%d|%s|%d|%d|%s|%d",
        q,
        esc(opc:GetCivilizationTypeName()),
        esc(L(opc:GetCivilizationShortDescription())),
        esc(csType),
        sent, suzStr,
        csx, csy, warStr, metT))
      pcall(function()
        local qm = Game.GetQuestsManager and Game.GetQuestsManager() or nil
        if qm then
          for qrow in GameInfo.Quests() do
            local qact = sf(function() return qm:HasActiveQuestFromPlayer(me, q, qrow.Hash) end)
            if qact then
              print(string.format("QUEST|%d|%s|%s", q, qrow.QuestType, esc(L(qrow.Description or qrow.QuestType))))
            end
          end
        end
      end)

      -- Envoys this city-state has received from EVERY met major (the CS
      -- panel shows all civs' envoy counts publicly).  pid:count pairs,
      -- zero counts omitted.
      pcall(function()
        if not oinf then return end
        local parts = {}
        if sent > 0 then parts[#parts+1] = me .. ":" .. sent end
        for _, r in ipairs(metIDs) do
          if r ~= q and r ~= 63 and r ~= me and majorSet[r] then
            local n = sf(function() return oinf:GetTokensReceived(r) end) or 0
            if n > 0 then parts[#parts+1] = r .. ":" .. n end
          end
        end
        print(string.format("CSENVOYS|%d|%s", q, table.concat(parts, ",")))
      end)

      -- Envoy-threshold bonus texts (shown on the base game's city-state
      -- panel).  The Loc keys are data, not method names: an unresolved
      -- key comes back as the key itself, which we detect and skip with a
      -- WARN — a raw LOC_ key must never render as a bonus.
      pcall(function()
        for _, kv in ipairs({{"small", "SMALL"}, {"medium", "MEDIUM"}, {"large", "LARGE"}}) do
          local key = "LOC_MINOR_CIV_" .. csType .. "_TRAIT_" .. kv[2] .. "_INFLUENCE_BONUS"
          local txt = L(key)
          if txt and txt ~= "" and txt ~= key then
            print(string.format("CSBONUS|%d|%s|%s", q, kv[1], esc(txt)))
          elseif not csLocWarned then
            csLocWarned = true
            print("WARN|DIPLO.cs_bonus|influence-bonus Loc key unresolved (" .. key .. ")")
          end
        end
      end)

      -- Leader trait descriptions — the unique suzerain bonus lives among
      -- these (standard DB rows: LeaderTraits -> Traits.Description).
      pcall(function()
        local lt = opc:GetLeaderTypeName() or ""
        if lt == "" then return end
        for row in GameInfo.LeaderTraits() do
          if row.LeaderType == lt then
            local tr = GameInfo.Traits[row.TraitType]
            if tr and tr.Description then
              local txt = L(tr.Description)
              if txt ~= "" and txt ~= tr.Description then
                print(string.format("CSBONUS|%d|trait|%s", q, esc(txt)))
              end
            end
          end
        end
      end)
    end
  end)
end

""" + _sentinel_line()


# ---------------------------------------------------------------------------
# Q7 — religion
# ---------------------------------------------------------------------------

def build_religion_query() -> str:
    return _prelude("REL") + r"""

local rel = sf(function() return p:GetReligion() end)
if not rel then print("DIAG|REL|no religion object"); print("---END---"); return end

safe("pantheon", function()
  local pantheonIdx = sf(function() return rel:GetPantheon() end) or -1
  local pantheonType, pantheonName, pantheonDesc = "NONE", "none", ""
  if pantheonIdx >= 0 then
    local pb = GameInfo.Beliefs[pantheonIdx]
    if pb then
      pantheonType = pb.BeliefType
      pantheonName = L(pb.Name)
      if pb.Description then pantheonDesc = L(pb.Description) end
    end
  end
  print(string.format("PANTHEON|%s|%s|%s", pantheonType, esc(pantheonName), esc(pantheonDesc)))
end)

safe("founded_religion", function()
  local myRel = sf(function() return rel:GetReligionTypeCreated() end) or -1
  if not (myRel and myRel > 0) then return end
  local rr = GameInfo.Religions[myRel]
  local rName = rr and L(rr.Name) or ("religion#" .. myRel)
  local rType = rr and rr.ReligionType or "?"
  print(string.format("RELIGION|%s|%s", rType, esc(rName)))
  local gameR = sf(function() return Game.GetReligion() end)
  local allRels = gameR and sf(function() return gameR:GetReligions() end) or {}
  for _, r in ipairs(allRels) do
    if r.Religion == myRel and r.Beliefs then
      for _, bi in ipairs(r.Beliefs) do
        local b = GameInfo.Beliefs[bi]
        if b then
          local desc = b.Description and L(b.Description) or ""
          print(string.format("BELIEF|%s|%s|%s|%s", b.BeliefClassType or "", b.BeliefType, esc(L(b.Name)), esc(desc)))
        end
      end
    end
  end
end)

-- All founded religions in the world with their founder — public via the
-- religion lens/screen.  Reuses the confirmed Game.GetReligion():
-- GetReligions() call from founded_religion above.  Founder field probed:
-- absent means -1 unknown + WARN, never a guess.
safe("world_religions", function()
  local gameR = sf(function() return Game.GetReligion() end)
  local allRels = gameR and sf(function() return gameR:GetReligions() end) or {}
  local founderWarned = false
  for _, r in ipairs(allRels) do
    pcall(function()
      if not (r.Religion and r.Religion > 0) then return end
      local rr = GameInfo.Religions[r.Religion]
      if not rr or rr.ReligionType == "RELIGION_PANTHEON" then return end
      local founder = -1
      if r.Founder ~= nil then
        founder = r.Founder
      elseif not founderWarned then
        founderWarned = true
        print("WARN|REL.world|religion entries carry no Founder field — founders unknown")
      end
      local nb = r.Beliefs and #r.Beliefs or -1
      print(string.format("WREL|%d|%s|%s|%d", founder, rr.ReligionType, esc(L(rr.Name)), nb))
    end)
  end
end)

safe("can_found_pantheon", function()
  local canFoundPantheon = sf(function() return rel:CanCreatePantheon() end) or false
  print(string.format("RELSTATE|canFoundPantheon=%s", tostring(canFoundPantheon)))
end)

safe("per_city_religion", function()
  for _, c in p:GetCities():Members() do
    pcall(function()
      local cr = sf(function() return c:GetReligion() end)
      if not cr then return end
      local majIdx = sf(function() return cr:GetMajorityReligion() end) or -1
      local majType = "NONE"
      if majIdx >= 0 then
        local rr = GameInfo.Religions[majIdx]
        if rr then majType = rr.ReligionType end
      end
      print(string.format("CITYREL|%d|%s", c:GetID(), majType))
    end)
  end
end)

""" + _sentinel_line()


# ---------------------------------------------------------------------------
# Q8 — notifications + end-turn blockers
# ---------------------------------------------------------------------------

def build_notifications_query() -> str:
    return _prelude("NOTIF") + r"""

safe("notifications", function()
  if not NotificationManager then print("DIAG|NOTIF|NotificationManager unavailable"); return end
  local list = sf(function() return NotificationManager.GetList(me) end)
  if not list then return end
  for _, nid in ipairs(list) do
    pcall(function()
      local entry = NotificationManager.Find(me, nid)
      if not entry then return end
      if sf(function() return entry:IsDismissed() end) then return end
      local tn = (sf(function() return entry:GetTypeName() end) or "UNKNOWN"):gsub("|", "/")
      local msg = (sf(function() return entry:GetMessage() end) or ""):gsub("|", "/")
      local bt = sf(function() return entry:GetEndTurnBlocking() end) or 0
      local btName = ""
      if bt ~= 0 and EndTurnBlockingTypes then
        for k, v in pairs(EndTurnBlockingTypes) do
          if v == bt then btName = k; break end
        end
      end
      print(string.format("NOTIF|%s|%s|%s", tn, btName, msg))
    end)
  end
end)

""" + _sentinel_line()


# ---------------------------------------------------------------------------
# Query registry — the collector runs these in order.
# ---------------------------------------------------------------------------

ALL_QUERIES = {
    "meta": build_meta_query,
    "choices": build_choices_query,
    "cities": build_cities_query,
    "units": build_units_query,
    "map": build_map_query,
    "diplo": build_diplo_query,
    "religion": build_religion_query,
    "notif": build_notifications_query,
}
