# Civ VI Base-Game Reference — Coach Companion

**Upload this alongside `AI-COACH-INSTRUCTIONS.md` in a new coaching chat.**
Purpose: give the coach exact base-game numbers and mechanics so it doesn't
hallucinate values or accidentally coach with expansion rules. This doc is
**strategy-neutral by design** — see §7. It describes how the game works and
what the options are; it never declares one strategy "best."

Everything here is **vanilla Civ VI** (2016 base game with official patches).
No Rise & Fall. No Gathering Storm. No game modes.

---

## 1. The base-game boundary (what does NOT exist in my game)

The internet's Civ 6 advice overwhelmingly assumes both expansions. These
systems **do not exist** here — never reference them, never coach around them:

| Doesn't exist | Came with | Common mistake it causes |
|---|---|---|
| Governors, governor titles | R&F | "Assign Pingala" advice |
| Loyalty, free cities | R&F | Fear of forward-settling flips |
| Era score, Golden/Dark/Heroic Ages, dedications | R&F | "Save that for era score" |
| Alliances with levels/types | R&F | Vanilla has only basic declared friendship + open borders + defensive pact style deals |
| Emergencies | R&F | — |
| Diplomatic favor, World Congress, Diplomatic Victory | GS | Suggesting a 6th victory path |
| Climate, floods, volcanoes, sea rise, storms | GS | "Don't settle floodplains" fear |
| Power, consumable strategic stockpiles | GS | See §6 — vanilla resources work differently |
| Dams, Canals, Railroads, Mountain Tunnels | GS | Suggesting unbuildable things |
| Rock bands, Naturalist parks still EXIST in vanilla? | — | Naturalists + National Parks **DO exist** in vanilla (Conservation civic). Rock Bands are GS-only. |

Also vanilla-specific: **boosts give 50%** of a tech/civic (expansions reduced
this to 40%) — eurekas are stronger here than most guides assume.

## 2. Cities: growth, housing, amenities

**Housing at founding:** fresh water (river/lake/oasis) = 5, coastal without
fresh water = 3, neither = 2. Aqueduct raises a no-fresh-water city to 6 (or
+2 if it already had fresh water). Granary +2, Sewer +2, most tile
improvements +0.5 each (farms, pastures, camps, plantations).

**Housing growth throttle:** at 1 pop below the housing cap, growth −50%.
At or above the cap, growth −75%. At 5 pop over, growth stops entirely.
A no-water city is throttled almost immediately — that's the real cost of a
dry settle, and an Aqueduct largely repairs it.

**Amenities:** a city needs 1 amenity per 2 population, starting at pop 3
(pop 1–2 needs none). Each unique luxury supplies 1 amenity to up to 4 cities
(duplicate copies of the same luxury do nothing except as trade bait).
Approximate happiness tiers (exact labels from the city panel are
authoritative):

| State | Surplus | Effect |
|---|---|---|
| Ecstatic | +3 or more | +20% growth, +10% non-food yields |
| Happy | +1 to +2 | +10% growth, +5% non-food yields |
| Content | 0 | baseline |
| Displeased | −1 to −2 | −15% growth, −5% non-food yields |
| Unhappy | −3 to −4 | −30% growth, −10% non-food yields |
| Unrest/Revolt | −5 and below | growth stops, heavy yield penalties, rebel (barbarian) units can spawn |

**Border growth:** tiles are claimed by culture at roughly
`10 + 6 × n^1.3` culture per tile (n = tiles already claimed by culture), out
to a 5-tile radius. Gold purchase reaches only 3 tiles out; price starts
around 50g (ring 2) / 75g (ring 3) and scales up with tech/civic progress —
buying early is cheaper.

## 3. Districts

**Slots:** 1 specialty district at pop 1, +1 more for every 3 additional pop
(2nd at pop 4, 3rd at pop 7, 4th at pop 10...). City Center, and in vanilla
the Aqueduct, don't count against the limit.

**Cost scaling:** district cost = base × (1 + 9 × max(techs%, civics%)) —
where the percentage is of the whole tree completed. Base 54 production for
most; Aqueduct 36; Spaceport 1800 (does not scale). Unique civ districts cost
half. Practical consequence: a district *placed* (locking its cost) early is
much cheaper than the same district started late, and rushing one tree ahead
of the other inflates district costs.

**Key adjacencies (vanilla):**
- **Campus:** +1 science per adjacent mountain; +1 per 2 rainforest; +1 per 2 adjacent districts.
- **Holy Site:** +2 per adjacent natural wonder; +1 per mountain; +1 per 2 woods; +1 per 2 districts.
- **Commercial Hub:** +2 per adjacent river; +2 per harbor; +1 per 2 districts.
- **Harbor:** +2 for adjacent city center; +1 per adjacent sea resource.
- **Industrial Zone:** +1 per adjacent mine or quarry; +1 per 2 districts.
- **Theater Square:** +1 per adjacent wonder; +1 per 2 districts.
- Factories/Power-free vanilla: Industrial Zone building bonuses (Factory,
  Power Plant) radiate to city centers within 6 tiles — regional overlap
  planning matters.

## 4. Combat math

**Damage formula (confirmed):**
`damage = 30 × e^(0.04 × strength_difference) × random(0.8 … 1.2)`

Practical readings:
- Equal strength: both take ~30 HP (24–36 range) per exchange.
- Each +1 CS ≈ +4% damage dealt and −4% taken. **+10 CS ≈ 1.5× damage.**
- Rule of thumb for small gaps: HP-difference per exchange ≈ 2.5 × CS gap.
- A wounded unit loses CS: penalty ≈ `10 − HP/10` (a 50 HP unit fights at −5).

**Common modifiers (all flat CS, they stack):**
- Fortified: +3 (1 turn) / +6 (2+ turns). Forts grant +6 immediately.
- Ideal terrain (hills, woods, rainforest): +3 defending (stacks: wooded hill +6).
- Marsh/floodplains: −2 defending.
- River crossing: +5 to defender vs melee attack.
- Embarked amphibious attack: −10.
- Melee vs anti-cavalry: +5. Anti-cavalry vs any cavalry: +10.
- Ranged attacks vs city defenses or naval: −17. Bombard vs land units: −17
  (siege units are for walls, not field battles).
- Diplomatic visibility edge: +3 CS per level of advantage over that civ.
- Great General: +5 CS and +1 movement within 2 tiles (era-matched units).

**Cities:** a city only gets a ranged strike after building Ancient Walls.
Walls give the city an outer-defense HP pool that ranged attacks can't
finish off — you need melee, siege, or battering-ram-supported units to take
a walled city. Garrisoned units add their strength to city defense.

**XP:** promotions come at set XP thresholds (15 for the first, rising after).
Barbarian fights only award XP up to your first promotion level, then 1 XP
per fight — you can't farm barbs forever.

## 5. Diplomacy, war, city-states

**War types (vanilla casus belli):** Surprise War (worst penalties — except
in the Ancient Era where warmonger penalties are zero), Formal War, Holy War,
Liberation War, Reconquest, Protectorate, Colonial War, War of Territorial
Expansion. Penalties for everything scale up with era. Denounce first (5
turns) to unlock Formal War. Taking cities carries a much bigger warmonger
hit than winning field battles; razing is the biggest.

**War weariness** builds with combat (more on foreign soil), drains slowly in
peace, and shows up as amenity penalties in your cities. Long grinding wars
strangle your economy even when you're winning.

**City-states:** 6 types in vanilla (Trade, Militaristic, Scientific,
Cultural, Religious, Industrial). Envoy bonuses at 1 / 3 / 6 envoys (type-
specific yields in capital, then in relevant district buildings; 6 doubles
it). **Suzerain** = 6+ envoys AND strictly more than every other civ: grants
the unique suzerain bonus, their resources, and the ability to levy their
military with gold. Envoys accrue from influence points (bonus per turn is
driven mostly by your government tier) and from completing city-state quests.
The first civ to meet a city-state gets a free envoy.

**Vanilla relationship states:** you'll see neutral, friendly/declared
friends, denounced, at war — no alliance levels or favor economy.

## 6. Strategic resources (vanilla rules — very different from GS)

No stockpiles, no per-turn consumption. You either **have access to N copies
or you don't**:
- **1 copy** of a resource: cities with the matching military district can
  build the units (Encampment for land, Harbor for naval).
- **2+ copies:** every city can build them.
- Trading away your only copy removes your ability to train those units.

Iron → Swordsman/Knight; Horses → Horseman/Knight; Niter → Musketman/Bombard;
Coal/Oil/Aluminum/Uranium → industrial-era-and-later lines. Resource
visibility requires the tech (Bronze Working reveals Iron, etc.) — decisions
about settling spots can change retroactively as resources appear.

## 7. Religion

- **Pantheon:** at 25 faith. One belief, permanent, first-come-first-served
  from a shared pool.
- **Founding:** requires a Great Prophet (earned via GPP from Holy Sites and
  their buildings — or Stonehenge which grants one outright). Number of
  religions is capped at roughly half the number of major civs plus one; when
  the last prophet is claimed, the door closes permanently.
- Found with 2 beliefs; Apostles (Theology civic, ~400 faith, needs Temple)
  can Evangelize to add up to 2 more.
- **Spread:** passive pressure from cities following a religion (trade routes
  add pressure), active spread via Missionaries (Shrine) and Apostles.
  Theological combat between religious units is a vanilla mechanic.
- **Religious victory:** your religion is the majority in every civilization
  still alive. Also note religion feeds other paths (faith-buying Great
  People via Patronage, Naturalists for culture).

## 8. Victory conditions (vanilla specifics)

- **Science:** research the tree to Spaceports, then three projects in order:
  Launch Earth Satellite → Launch Moon Landing → Launch Mars Colony (Mars has
  THREE components — Reactor, Habitation, Hydroponics — buildable in parallel
  at different Spaceports). No exoplanet expedition, no laser stations (those
  are GS).
- **Culture:** attract more **visiting tourists** than any other civ has
  **domestic tourists**. Domestic tourists ≈ lifetime culture / 100. Your
  visiting tourists from a civ ≈ lifetime tourism vs them / (number of civs ×
  200). Open borders (+25%), trade routes (+25%), and shared religion boost
  tourism against a specific civ. Wonders, Great Works, artifacts, relics,
  seaside resorts, and National Parks generate tourism.
- **Domination:** capture every other civ's **original capital**. You only
  need to hold them all simultaneously.
- **Religious:** majority religion in every living civ.
- **Score:** turn limit reached (turn 500 standard) — highest score wins.
  Enabled victories for the current game are listed in the snapshot header.

## 9. Great People

Each class accumulates points per turn from districts/buildings
(Encampment→General, Holy Site→Prophet, Campus→Scientist, etc.). Each Great
Person is a **named individual with a unique ability** — sometimes worth
passing (costs a small GPP payment) if the current one fits you poorly and
you want the next. Recruit costs rise each era. Faith or gold can Patronize
one outright. Once claimed by any civ, that individual is gone for everyone.

## 10. Barbarians

Outposts spawn in fog outside any civ's vision. A **Scout** that sees your
city will run home and trigger a raid wave (3–6 units). Killing the scout
before it reports prevents the raid. Camps near horses spawn cavalry raiders.
Clearing a camp pays gold (scales with era/difficulty) and can trigger boosts
("Clear a barbarian outpost" inspiration). Barbarians scale with the tech of
the most advanced civ — leaving camps alive late-game produces surprisingly
modern raiders.

## 11. Trade routes

Capacity comes from Trader units (1 route each); slots from Commercial Hubs /
Harbors (first building in each +1). **Domestic routes** pay food +
production based on districts at the destination — strong for growing new
cities. **International routes** pay gold (+ small yields per destination
district type) — strong for economy. Routes also build roads along their
path (era-appropriate), create trading posts, and carry religious pressure
both ways. Traders can be plundered on land or sea by units at war with you.

---

## 12. Coaching variety mandate (read carefully)

This section constrains HOW to use everything above.

**Never present one strategy as the correct lane.** I want variety across
games and flexibility within a game. Concretely:

- When I face an opening decision (2nd city spot, first districts, early
  wonder or not, early war or not), present the **live options with their
  trade-offs** and a recommendation *for this map*, not a doctrine. "Campus
  first is standard" is banned phrasing; "this start has 3 mountain tiles
  adjacent to the capital, which makes an early Campus unusually strong
  *here*" is good coaching.
- **Let the map and civ ability pull the strategy.** Egypt's rivers, a faith-
  heavy pantheon start, an aggressive neighbor, a wonder-friendly capital —
  read what THIS game is offering before defaulting to what's generically
  strong.
- **Respect my chosen direction.** If I commit to something offbeat (early
  religion on a science-ish map, a wonder-hoarding game, an early rush),
  coach me to do *that* well. Point out the cost once, then optimize my
  plan — don't relitigate it every turn.
- **Multiple victory doors open.** Until the mid-game makes it obvious,
  coach to keep 2–3 victory paths alive rather than tunneling on one from
  turn 20. Vanilla's five paths (Science, Culture, Domination, Religious,
  Score) are all winnable.
- It's fine to say a specific move is a mistake (settling with no water when
  a river is one tile away, attacking walls with ranged only). Mechanics
  have right answers; strategy has trade-offs. Keep those categories
  separate.

## 13. Trust order when sources disagree

1. The live snapshot (always wins — it's my actual game).
2. This document.
3. The model's general Civ 6 knowledge — **only after checking it isn't an
   expansion mechanic**, which is the most common failure mode.

If a number in this doc seems wrong in-game (patches changed some values over
the years), trust the game, tell me about the discrepancy, and move on.
