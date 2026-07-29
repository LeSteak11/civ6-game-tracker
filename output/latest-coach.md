# CIV6 COACH SNAPSHOT — turn 87
_Egypt (Cleopatra) — 725 BC / Classical Era — Chieftain / Standard / Small Continents — schema coach-snapshot/1.1 coach 1.0.1_

## CHANGES SINCE LAST SNAPSHOT
No meaningful changes. (Same turn as the previous snapshot.)

## TURN BLOCKERS
- blocker:ENDTURN_BLOCKING_UNITS (Command Units)
- 1 idle unit(s)

## EMPIRE
- **score:** 79
- **gold:** 330 (net +10.4 = yield 12.4 − maint 2.0)
- **science:** 17.1/turn
- **culture:** 11.3/turn
- **faith:** 184 (+7.3/turn)
- **tourism:** 8.0/turn
- **military:** 119
- **techs / civics done:** 13 / 8
- **cities / units / pop:** 4 / 6 / 14
- **trade routes:** 1/1
- **explored land:** 422/1153 tiles
- **enabled victories:** VICTORY_TECHNOLOGY, VICTORY_CULTURE, VICTORY_RELIGIOUS, VICTORY_CONQUEST, VICTORY_SCORE

## RESEARCH / CIVIC
- **tech:** Construction 92/200 (7t) — eureka:False [need: Build a Water Mill.]
- **civic:** Military Tradition 0/50 (4t) — inspiration:False [need: Clear a Barbarian Outpost.]

### TECHS AVAILABLE (up to 10, sorted by turns)
- Construction  — 200sci (7t) — unlocks: Siege Tower, Terracotta Army — boost: Build a Water Mill.
- Celestial Navigation  — 120sci (8t) — unlocks: Lighthouse, Great Lighthouse, Harbor, Royal Navy Dockyard — boost: Improve 2 sea resources.
- Iron Working  — 120sci (8t) — unlocks: Swordsman, Legion, Ngao Mbeba — boost: Build an Iron Mine.
- Shipbuilding  — 200sci (12t) — unlocks: Quadrireme, Colossus — boost: Own 2 Galleys.
- Mathematics  — 200sci (12t) — unlocks: Petra — boost: Build 3 different specialty districts.
- Engineering  — 200sci (12t) — unlocks: Catapult, Aqueduct, Bath — boost: Build Ancient Walls.
- Apprenticeship  — 300sci (18t) — unlocks: Man-At-Arms, Workshop, Industrial Zone, Hansa — boost: Build 3 Mines.
- Stirrups  — 390sci (23t) — unlocks: Knight, Mamluk — boost: Have the Feudalism civic.

### CIVICS AVAILABLE (up to 10, sorted by turns)
- Military Tradition  — 50cul (4t) — unlocks: Maneuver, Strategos — inspiration: Clear a Barbarian Outpost.
- Drama and Poetry  — 110cul (10t) — unlocks: Literary Tradition — inspiration: Build a wonder.
- Defensive Tactics  — 175cul (15t) — unlocks: Bastions, Limes — inspiration: Be the target of a Declaration of War.

## RESOURCES
- strategic: none
- **luxuries:** Ivory

## GOVERNMENT & POLICIES
- **government:** Classical Republic — 0 open slot(s) — free change avail: True
- **slotted:**
    - `ECONOMIC` Urban Planning
    - `ECONOMIC` God King
    - `DIPLOMATIC` Diplomatic League
    - `WILDCARD` Revelation
- **available (unslotted):** 13 card(s)
    - `MILITARY` Discipline
    - `MILITARY` Survey
    - `ECONOMIC` Ilkum
    - `MILITARY` Agoge
    - `ECONOMIC` Caravansaries
    - `MILITARY` Maritime Industries
    - `ECONOMIC` Corvée
    - `MILITARY` Conscription
    - `ECONOMIC` Land Surveyors
    - `ECONOMIC` Colonization
    - `GREAT_PERSON` Inspiration
    - `ECONOMIC` Insulae
    - `DIPLOMATIC` Charismatic Leader

## GREAT PEOPLE
- **GENERAL** 49pts (+1.1/turn) — next recruit cost 60 — candidate: Sun Tzu
- **ADMIRAL** 0pts (+0.0/turn) — next recruit cost 60 — candidate: Gaius Duilius
- **ENGINEER** 0pts (+0.0/turn) — next recruit cost 120 — candidate: Bi Sheng
- **MERCHANT** 0pts (+0.0/turn) — next recruit cost 60 — candidate: Zhang Qian
- **PROPHET** 25pts (+2.3/turn) — next recruit cost 60 — candidate: Simon Peter
- **SCIENTIST** 0pts (+0.0/turn) — next recruit cost 120 — candidate: Abu al-Qasim al-Zahrawi
- **WRITER** 0pts (+0.0/turn) — next recruit cost 60 — candidate: Homer
- **ARTIST** 0pts (+0.0/turn) — next recruit cost 240 — candidate: Hieronymus Bosch
- **MUSICIAN** 0pts (+0.0/turn) — next recruit cost 420 — candidate: Yatsuhashi Kengyo

## RELIGION
- pantheon: River Goddess (+1 [ICON_Amenities] Amenity to cities if they have a Holy Site district adjacent to a River.)
- founded religion: none

## CITIES (4)
### Râ-Kedet [CAP] @ (66,29)
- pop 3 | grow 24t (food+1.0) | hous 10 | amen 3/1 | happ 5 | border+15t
- yields: F7.0 P14.7 G10.5 S8.5 C5.1 Fa6.3
- **producing:** Stonehenge (164/180, 1t)
- defense: str 23 | garrison 200/200 | walls 0/0
    - district `CITY_CENTER` @ (66,29)
    - district `ENCAMPMENT` @ (65,26)
    - district `WONDER` @ (66,27)
    - buildings in `CITY_CENTER`: Monument, Palace, Granary
    - tiles: 13 owned, 4 worked | terrain: 7 plains, 5 plains_hills, 1 grass_hills | features: 1 forest | improvements: 3 farm, 2 mine, 2 sphinx, 1 camp
    - top production options: Stonehenge (1t), Scout (2t), Warrior (3t), Trader (4t), Archer (4t), Spearman (4t), Battering Ram (4t), Builder (5t), Horseman (5t), Ancient Walls (6t)
    - ...13 more options in JSON
    - trade → Luxis (domestic): Food +1, Production +1
### Sais @ (62,26)
- pop 6 | grow 7t (food+8.0) | hous 7 | amen 1/2 | happ 3 | border+6t
- yields: F20.0 P6.7 G1.9 S4.0 C3.6 Fa0.0
- **producing:** Holy Site (82/131, 8t)
- defense: str 20 | garrison 200/200 | walls 0/0
    - district `CITY_CENTER` @ (62,26)
    - district `HOLY_SITE` @ (63,24)
    - buildings in `CITY_CENTER`: Monument
    - tiles: 11 owned, 7 worked | terrain: 7 grass, 2 plains, 1 grass_hills, 1 plains_hills | features: 2 jungle, 1 marsh | improvements: 2 pasture, 1 farm, 1 plantation
    - top production options: Scout (5t), Warrior (7t), Holy Site (8t), Trader (10t), Archer (10t), Spearman (10t), Battering Ram (10t), Granary (10t), Builder (12t), Horseman (13t)
    - ...11 more options in JSON
### SHEDET @ (66,25)
- pop 4 | grow 5t (food+5.0) | hous 5 | amen 1/1 | happ 4 | border+14t
- yields: F13.0 P6.0 G0.0 S2.8 C2.2 Fa1.0
- **producing:** Granary (18/65, 8t)
- defense: str 20 | garrison 200/200 | walls 0/0
    - district `CITY_CENTER` @ (66,25)
    - tiles: 9 owned, 5 worked | terrain: 6 grass, 1 grass_hills, 1 coast, 1 plains | features: 1 marsh, 1 forest | improvements: 2 quarry, 1 farm, 1 sphinx
    - top production options: Scout (5t), Builder (6t), Warrior (7t), Granary (8t), Archer (10t), Monument (10t), Trader (11t), Spearman (11t), Battering Ram (11t), Horseman (14t)
    - ...12 more options in JSON
### Luxis @ (64,22)
- pop 1 | grow 2t (food+2.0) | hous 5 | amen 1/0 | happ 5 | border+28t
- yields: F4.0 P3.1 G0.0 S1.8 C0.3 Fa0.0
- **producing:** Monument (15/60, 15t)
- defense: str 10 | garrison 200/200 | walls 0/0
    - district `CITY_CENTER` @ (64,22)
    - tiles: 7 owned, 2 worked | terrain: 4 grass, 1 grass_hills, 1 grass_mountain, 1 plains | features: 1 jungle
    - top production options: Scout (10t), Warrior (13t), Monument (15t), Trader (20t), Archer (20t), Spearman (21t), Battering Ram (21t), Granary (21t), Builder (25t), Horseman (26t)
    - ...12 more options in JSON

## UNITS (6)
- **Scout** #196608 @(49,19) | hp100/100 | mv0/3 | cs10 rs0 xp15/45
- **Warrior** #131073 @(66,29) | hp84/100 | mv1/2 | cs20 rs0 xp7/15 <IDLE>
- **Trader** #786434 @(65,24) | hp100/100 | mv0/2 | cs0 rs0 xp0/15
- **Warrior** #655363 @(62,26) | hp100/100 | mv2/2 | cs20 rs0 xp0/15 fort:2
- **Archer** #1048582 @(67,29) | hp100/100 | mv0/2 | cs15 rs25 xp22/45
- **Warrior** #983047 @(66,25) | hp100/100 | mv2/2 | cs20 rs0 xp0/15 fort:2

## DIPLOMACY
- **envoys:** 0 in hand | 8/100 pts (+3.0/turn — 1 envoys/threshold)
### MAJORS MET
- **Sumeria (Gilgamesh)** — DIPLO_STATE_DECLARED_FRIEND | vis 1 | score 96 mil 169 | met T27 | OB from them
- **Brazil (Pedro II)** — DIPLO_STATE_FRIENDLY | vis 0 | score 34 mil 30 | met T84
### CITY-STATES MET
- **Kabul** (KABUL) — envoys sent 1 | suz: none | @(61,18) | met T20
- **Hattusa** (HATTUSA) — envoys sent 2 | suz: none | @(56,24) | met T19
- **Stockholm** (STOCKHOLM) — envoys sent 1 | suz: none | @(64,13) | met T32
- **Amsterdam** (AMSTERDAM) — envoys sent 1 | suz: none | @(67,19) | met T54

## BARBARIANS (only what we can currently see)
- **units visible (1):** Galley @(68,27) hp72/100

## NOTIFICATIONS
- `NOTIFICATION_WONDER_COMPLETED`: Wonder Completed
- `NOTIFICATION_BARBARIANS_SIGHTED`: Barbarians Approach
- `NOTIFICATION_CIVIC_DISCOVERED`: Discovered Games and Recreation
- `NOTIFICATION_COMMAND_UNITS` [BLOCKS: ENDTURN_BLOCKING_UNITS]: Command Units

## REVEALED MAP
_508 revealed, 96 currently visible, 1 natural wonders_
**Owner IDs:** 0=me (Egypt), 3=Sumeria, 4=Brazil, 7=Kabul (city-state), 8=Hattusa (city-state), 10=Stockholm (city-state), 11=Amsterdam (city-state)
**Line schema:** `MAP x,y v|terr|feat|res|imp|road|owner|dist|city|units|extra|cityname`  (`v`=1 currently visible; `terr` = g/p/d/t/s (+h for hills, +m for mountain); `feat` = for/jun/mar/fld/oas/reef/nw:NAME; `imp` may end `:P` if pillaged; `extra` R=river L=lake F=freshwater A±N=appeal; `cityname` set on city-centre tiles)
```
59,5 0|co|||||||0|||
60,5 0|co|||||||0|||
61,5 0|co|||||||0|||
62,5 0|co|||||||0|||
55,6 0|sh|||||||0||A4|
56,6 0|sh|||||||0||A3|
59,6 0|co|||||||0|||
60,6 0|th||COPPER|||||0||A5|
61,6 0|t|for||||||0||A3|
62,6 0|t|||||||0||A4|
63,6 0|co||CRABS|||||0|||
54,7 0|th|for||||||0||A3|
55,7 0|th||IRON|||||0||A3|
56,7 0|tm|||||||0||R/A4|
57,7 0|th|||||||0||R/A3/F|
58,7 0|th||DEER|||||0||A2|
59,7 0|th|||||||0||A2|
60,7 0|th|for||||||0||A2|
61,7 0|t|||||||0||A3|
62,7 0|t|||||||0||A2|
63,7 0|co|||||||0|||
64,7 0|co||FISH|||||0|||
65,7 0|co|||||||0|||
68,7 0|co|||||||0|||
69,7 0|co|||||||0|||
54,8 0|th|for||||||0||A1|
55,8 0|tm|||||||0||A4|
56,8 0|th|||||3|HOLY_SITE|0||A3|
57,8 0|t|||||||0||A2|
58,8 0|th|||||3||0|||
59,8 0|th|||||||0||A1|
60,8 0|th|||||||0||A3|
61,8 0|t|for|IVORY|||||0||A1|
62,8 0|t|||||||0||A1|
63,8 0|th|||||||0||R/A2/F|
64,8 0|t|||||||0||R/A3/F|
65,8 0|t|||||||0||A4|
66,8 0|gh|for|SILK|||||0||A2|
67,8 0|gh|||||||0||A2|
68,8 0|gh|||||||0||A2|
69,8 0|g|mar||||||0||A3|
70,8 0|gh||COPPER|||||0|||
71,8 0|th|||||||0|||
72,8 0|t|for||||||0||A4/F|
53,9 0|ph|||||||0|||
54,9 0|p||IVORY|||||0||A3|
55,9 0|th|||||3||0||A3|
56,9 0|tm|||||3||0||A4|
57,9 0|ph|||||3||0||A2|
58,9 0|ph|||||3||0||A2|
59,9 0|gh|for||||||0|||
60,9 0|g|||||||0||A2|
61,9 0|gh|||||||0||A2|
62,9 0|g|||||||0||A1|
63,9 0|g||MARBLE|||||0||R/A1/F|
64,9 0|gh|||||||0||R/A2/F|
65,9 0|g|for||||||0||R/A3/F|
66,9 0|gh|||||||0||A3|
67,9 0|gh|||||||0||A2|
68,9 0|gm|||||||0||A4|
69,9 0|g|||||||0||A1|
70,9 0|g|||||||0||A-1|
71,9 0|g|mar||||||0||A2|
72,9 0|g|for||||||0||A3/F|
53,10 0|ph||IRON|MINE||3||0||R/A1/F|
54,10 0|p|||||||0||R/A1/F|
55,10 0|pm|||||||0||R/A4|
56,10 0|p||||1|3|CAMPUS|0||A2|
57,10 0|ph||||1|3|CITY_CENTER|1||R/A3/F|Uruk
58,10 0|gh||||1|3|WONDER|0||R/A1/F|
59,10 0|gh|||||3||0||A2|
60,10 0|g|||||||0||A1|
61,10 0|gh|||||||0||R/A2/F|
62,10 0|g|for||||||0||R/A1/F|
63,10 0|g|||||||0||R/A2/F|
64,10 0|g|||||||0||R/A2/F|
65,10 0|g||RICE|||||0||R/A4/F|
66,10 0|gm|||||||0||R/A4|
67,10 0|g|||||||0||R/A3/F|
68,10 0|gh|for|DEER|||||0||A2|
69,10 0|gm|||||||0||A4|
70,10 0|g||HORSES|||||0||A2|
71,10 0|g|||||||0||A-1|
72,10 0|g|||||||0|||
73,10 0|g|||||||0||A1|
52,11 0|g|mar||||3||0||R/F|
53,11 0|g|||ZIGGURAT||3||0||R/F|
54,11 0|p||WHEAT|||3||0||R/A3/F|
55,11 0|ph|||||3||0||R/A1/F|
56,11 0|p|||ZIGGURAT||3||0||R/F|
57,11 0|g|||ZIGGURAT||3||0||R/A3/F|
58,11 0|g|||ZIGGURAT||3||0||R/A3/F|
59,11 0|g||RICE|||3||0||R/A1/F|
60,11 0|g||HORSES|||3||0||R/A1/F|
61,11 0|g|||||||0||R/A2/F|
62,11 0|g|||||||0||R/A2/F|
63,11 0|g|||||||0||R/A2/F|
64,11 0|g|for|DYES|||||0||A-1|
65,11 0|g|||||||0||R/A2/F|
66,11 0|g||STONE|||||0||R/A2/F|
67,11 0|gh|||||||0||R/A2/F|
68,11 0|gh|||||||0||A4|
69,11 0|gh|for||||||0||A2|
70,11 0|g|||||||0||A1|
71,11 0|g|||||||0|||
72,11 0|g||CATTLE|||||0|||
73,11 0|g|||||||0|||
0,12 0|g|||||||0||A1|
48,12 0|g|||||4||0||R/A3/F|
49,12 0|gh||||0|4||0|||
52,12 0|g||TEA|||3||0|||
53,12 0|g||||1|3|CITY_CENTER|1||R/A1/F|Lagash
54,12 0|gh|for||||3||0||R/A2/F|
55,12 0|ph|||||||0||R/A2/F|
56,12 0|ph||MARBLE|QUARRY||3||0||R/A1/F|
57,12 0|g|||||||0||R/A2/F|
58,12 0|g|for||||3||0||R/A3/F|
59,12 0|g|||||3||0||R/A3/F|
60,12 0|g||||1|3|CITY_CENTER|1||R/A1/F|Adab
61,12 0|g|||||3||0||R/A1/F|
62,12 0|g|||||||0|||
63,12 0|g||STONE|||||0||R/A1/F|
64,12 0|g|||FARM||10||0||R/F|
65,12 0|gh|||MINE||10||0||R/F|
66,12 0|g||STONE|||||0||R/A-1/F|
67,12 0|g|||||||0||R/A1/F|
68,12 0|g|||||||0||A1|
69,12 0|g|for||||||0||A2|
70,12 0|gh|||||||0||A3|
71,12 0|gh||STONE|||||0|||
72,12 0|g|||||||0|||
73,12 0|g|||||||0|||
0,13 0|d|||||||0||A3|
47,13 0|g||TEA|||4||0||R/A2/F|
48,13 0|g||||0|4|CITY_CENTER|1||R/A2/F|Recife
49,13 0|g|||FARM||4||0|||
50,13 0|g|mar|RICE|||4||0||A1|
51,13 0|gh|for||||3||0|||
52,13 0|gh|||||3||0||R/A3/F|
53,13 0|g||||1|3|CAMPUS|0||R/A3/F|
54,13 0|gm|||||||0||A4|
55,13 0|gh|||||||0|||
56,13 0|gh|||||||0|||
57,13 0|gm|||||||0||A4|
58,13 0|g|for||||||0||R/A4/F|
59,13 0|g|||||3||0||R/A2/F|
60,13 0|g|||||3||0||R/A1/F|
61,13 0|g|||||||0|||
63,13 0|g|||FARM||10||0||R/A1/F|
64,13 0|d|fld|||1|10|CITY_CENTER|1||R/A-1/F|Stockholm
65,13 0|d|fld||FARM||10||0||R/A-1/F|
66,13 0|g|||||||0||R/A-1/F|
67,13 0|g||TOBACCO|||||0||R/A1/F|
68,13 0|g|||||||0||R/A4/F|
69,13 0|g|for|DEER|||||0||A2|
70,13 0|g|||||||0||A3|
71,13 0|gh|||||||0||R/A1/F|
72,13 0|gh|||||||0||A-1|
73,13 0|d|||||||0|||
0,14 0|dh|||||||0||A1|
48,14 0|g|||FARM||4||0||A1|
49,14 0|gm|||||4||0||A4|
50,14 0|g|||||||0||A1|
51,14 0|g||RICE|||||0||A2|
52,14 0|gh|for||||||0||R/A2/F|
53,14 0|g||CATTLE|||3||0||R/A3/F|
54,14 0|gh|||||||0||A2|
55,14 0|gh|||||||0||A1|
56,14 0|g||MARBLE|||||0||A1|
57,14 0|g||MARBLE|||||0||A3|
58,14 0|gh|for||||||0||R/A3/F|
59,14 0|g|||||||0||R/A3/F|
60,14 0|g|||||||0|||
64,14 0|d||||1|10|CAMPUS|0|||
65,14 0|d||||1|10||0||A-2|
66,14 0|d|||||||0||A-2|
67,14 0|d|fld||||||0||R/A2/F|
68,14 0|g|for||||||0||R/A-1/F|
69,14 0|g|||||||0||R/A4/F|
70,14 0|gm|||||||0||R/A4|
71,14 0|g|for||||||0||R/A2/F|
72,14 0|d|fld||||||0||R/A2/F|
73,14 0|d|||||||0||A-1|
48,15 0|g|||||||0||A4|
49,15 0|g|||||4|HOLY_SITE|0||A4|
50,15 0|g|for||||||0|||
51,15 0|g|||||||0||R/A3/F|
52,15 0|g|||||||0||R/A3/F|
53,15 0|gm|||||||0||R/A4|
54,15 0|gh|||||||0||A3|
55,15 0|gh|||||||0||A3|
56,15 0|gh|for||||||0||R/A2/F|
57,15 0|g|||||||0||R/A3/F|
58,15 0|g|||||||0||R/A3/F|
63,15 0|d||||1|||0||A1|
64,15 0|d|||||||0|||
65,15 0|dh||||0|||0|||
66,15 0|dh||SHEEP|||||0||A-1|
67,15 0|d|||||||0||A-1|
68,15 0|d|fld|SUGAR|||||0||R/A3/F|
69,15 0|p|for||||||0||R/A3/F|
70,15 0|p|for||||||0||R/A6/F|
71,15 0|g|||||||0||R/A3/F|
72,15 0|dh|||||||0||A-1|
73,15 0|d|||||||0||A1|
0,16 0|gh|for||||||0|||
1,16 0|co|||||||0|||
48,16 0|g|for||||||0|||
49,16 0|g|nw:TSINGY||||||0||A5|
50,16 0|g|||||||0||A1|
51,16 0|g|||||||0||R/F|
52,16 0|g||HORSES|PASTURE||3||0||R/A-1/F|
53,16 0|g|||||||0||R/A1/F|
54,16 0|gh|for||||||0||A1|
55,16 0|gm|||||||0||A4|
56,16 0|dm|||||||0||A4|
57,16 0|g|||||||0||R/A3/F|
58,16 0|g||RICE|||||0||R/A2/F|
59,16 0|gm|||||||0||A4|
64,16 0|d|||||||0||A-1|
65,16 0|dh|||||||0||A-2|
66,16 0|d||||0|||0||A-1|
67,16 0|d|||||||0|||
68,16 0|dh|||||||0||F|
69,16 0|d|||||||0||A2/F|
70,16 0|p|for||||||0||R/A4/F|
71,16 0|g|for||||||0||R/A3/F|
72,16 0|dh|||||||0||A1|
73,16 0|d|||||||0|||
0,17 0|dh|||||||0||A3|
1,17 0|co|||||||0|||
47,17 0|g|mar||||||0|||
48,17 0|p|jun|DYES|||||0||A2|
49,17 1|ph|jun||||||0|||
50,17 0|p|jun|BANANAS|||3||0||R/A-2/F|
51,17 0|ph|jun||||3||0||R/F|
52,17 0|p|jun||||3||0||A-1|
53,17 0|p|jun||||||0||A1|
55,17 0|dm|||||||0||A4|
56,17 0|dh||SHEEP|||||0||A3|
57,17 0|d|||||||0|||
58,17 0|d|||||||0||A1|
59,17 0|p|jun|BANANAS|||||0||A1|
60,17 0|p|||FARM||7||0||A-3|
61,17 0|ph|||MINE||7||0||A-2|
64,17 0|p|jun||||||0|||
65,17 0|p|jun||||||0||A-1|
66,17 0|d||||0|||0||A-1|
67,17 0|d||SALT|||||0||A1/F|
68,17 0|d|oas||||||0||F|
69,17 0|dh|||||||0||A1/F|
70,17 0|d|||||||0||A2|
71,17 0|d|||||||0||A2|
72,17 0|d|||||||0||A-2|
73,17 0|p|jun||||||0|||
0,18 0|dh|||||||0||A1|
1,18 0|co|||||||0|||
2,18 0|oc|||||||0|||
48,18 1|gh||||1|||0||A-1|
49,18 1|gh|for||||||0||A-3|
50,18 1|p|jun||||3||0||R/A1/F|
51,18 0|g|||||3||0||R/F|
52,18 0|g|for||||3||0||R/A-1/F|
55,18 0|dh|||||||0||A4|
56,18 0|dm|||||||0||A4|
57,18 0|dh|||||||0||A1|
58,18 0|d|||||||0|||
59,18 0|p|for||||||0||A-4|
60,18 0|ph|||MINE||7||0||A-1|
61,18 0|ph||||1|7|CITY_CENTER|1||A-2|Kabul
62,18 0|g|||FARM|1|7||0||A-1|
66,18 0|g||STONE|||||0||A-1|
67,18 0|g|||FARM|1|11||0|||
68,18 0|d|||||11||0||A2/F|
69,18 0|d|||||||0||A1/F|
70,18 0|p|jun||||||0||A1|
71,18 0|p|for||||||0|||
72,18 0|d|||||||0||A1|
73,18 0|g|mar||||||0|||
0,19 0|co|||||||0|||
1,19 0|oc|||||||0|||
47,19 1|p|jun||||||0|||
48,19 1|p||||0|||0|||
49,19 1|g||STONE|||3||0|0:SCOUT:100|A3|
50,19 1|g|for||||3||0||R/F|
51,19 0|g||||1|3|CITY_CENTER|1||R/A1/F|Rio de Janeiro
52,19 0|gh||STONE|||3||0||R/A3/F|
54,19 0|gm|||||||0||A4|
55,19 0|gh||TEA|||||0||A3/F|
56,19 0|gh|||||||0||R/A3/F|
57,19 0|gh|||||||0||R/A1/F|
58,19 0|g|mar||||||0||A1|
59,19 0|p|jun||||||0|||
60,19 0|p|||FARM||7||0||A-3|
61,19 0|p|||FARM||7||0||A-1|
62,19 0|g||HORSES|||||0||A2|
63,19 0|gm|||||||0||A4|
66,19 0|g|||FARM||11||0|||
67,19 0|p||||1|11|CITY_CENTER|1||R/A2/F|Amsterdam
68,19 0|gm|||||11||0||R/A4|
69,19 0|ph|||||||0||A-1|
70,19 0|p||WHEAT|||||0||A1|
71,19 0|p|for||||||0||A3|
72,19 0|p||WHEAT|||||0||A3|
73,19 0|co|||||||0|||
0,20 0|co|||||||0|||
1,20 0|co|||||||0|||
48,20 1|p|jun||||||0|||
49,20 1|p|for||||||0|||
50,20 1|pm|||||||0||A4|
51,20 0|g|mar||||3||0||R/A3/F|
52,20 0|g||STONE|QUARRY||3||0||R/A2/F|
55,20 0|co|||||||0||L|
56,20 0|gh|||||||0||A1/F|
57,20 0|pm|||||||0||R/A4|
58,20 0|g|||||||0||R/A2/F|
59,20 0|gh|for||||||0||A-1|
60,20 0|gh||COPPER|||||0|||
61,20 0|p|jun||||||0|||
62,20 0|gh|||||||0||A-1|
63,20 1|g|||||||0||R/A3/F|
64,20 1|g|for|DYES|||||0||R/A2/F|
65,20 1|g|||||||0||A2|
67,20 0|g|||FARM||11||0|||
68,20 0|g|||FARM||11||0||R/A2/F|
69,20 0|ph||IRON|||||0||R/A1/F|
70,20 0|p|jun||||||0||A2|
71,20 0|co|||||||0|||
72,20 0|co|||||||0|||
73,20 0|co|||||||0|||
50,21 0|g|for||||||0||R/A1/F|
51,21 0|g|||||||0||R/F|
55,21 0|g||STONE|||||0||A1/F|
56,21 0|p|jun||||||0||R/A2/F|
57,21 0|g|||||||0||R/A2/F|
58,21 0|gh||SHEEP|||||0||A3|
59,21 0|gh|for||||||0||A2|
60,21 0|g|||||||0||A1|
61,21 0|g|||||||0||A-2|
62,21 1|g||RICE|||||0||A-1|
63,21 1|g|||||0||0||R/A1/F|
64,21 1|p|jun||||0||0||R/A4/F|
65,21 1|g|for||||||0||A1|
68,21 0|g||RICE|||||0||R/A2/F|
69,21 0|gh|||||||0||R/A3/F|
70,21 0|co|||||||0|||
71,21 0|co|||||||0|||
72,21 0|oc|||||||0|||
73,21 0|co|||||||0|||
58,22 0|g|for||||||0||A1|
59,22 0|g|||||||0||R/A4/F|
60,22 0|gm|||||||0||A4|
61,22 0|gh|||||||0|||
62,22 1|ph|jun||||||0||A2|
63,22 1|g|||||0||0|||
64,22 1|g||||1|0|CITY_CENTER|1||R/A1/F|Luxis
65,22 1|gm|||||0||0||R/A4|
66,22 1|g|for||||||0||A4|
67,22 0|g|||||||0||A2|
68,22 0|g|||||||0||A2|
70,22 0|co||FISH|||||0|||
71,22 0|co|||||||0|||
55,23 0|g|||FARM||8||0||R/A1/F|
56,23 0|g|||FARM||8||0||R/A2/F|
57,23 0|gm|||||||0||A4|
58,23 0|g||STONE|||||0||R/A2/F|
59,23 0|g|||||||0||R/A1/F|
60,23 0|p|jun||||||0||A3|
61,23 0|gm|||||||0||A4|
62,23 1|gm|||||||0||A4|
63,23 1|gh||IRON|||0||0||A1|
64,23 1|g|||||0||0||R/A3/F|
65,23 1|g|for||||||0||R/A5/F|
66,23 1|gm|||||||0||R/A4|
67,23 1|g|||||||0||A2|
68,23 0|co|||||||0|||
55,24 0|g|||FARM||8||0||A-1|
56,24 0|g||||1|8|CITY_CENTER|1||R/F|Hattusa
57,24 0|g||||1|8|CAMPUS|0||R/A1/F|
58,24 0|p|jun||||||0||R/A3/F|
59,24 0|g|||||||0||R/A1/F|
60,24 0|g||MARBLE|||||0|||
61,24 1|gm|||||||0||A4|
62,24 1|gm|||||||0||A4|
63,24 1|gh|||||0|HOLY_SITE|0||A3|
64,24 1|g|||||||0||A2|
65,24 1|g||RICE||1|0||0||R/A3/F|
66,24 1|g|||SPHINX||0||0||R/A1/F|
67,24 1|g||STONE|QUARRY||0||0||R/A5/F|
68,24 1|co|||||||0|||
69,24 1|oc|||||||0|||
55,25 0|p|jun||||8||0||A1|
56,25 0|g|||FARM||8||0||R/A2/F|
58,25 0|g|for||||||0||R/A2/F|
59,25 0|g|||||||0||A2|
60,25 1|g|||||||0||A1|
61,25 1|g|||FARM||0||0||A2|
62,25 1|g||CATTLE|PASTURE||0||0||R/A2/F|
63,25 1|gm|||||||0||R/A4|
64,25 1|gm|||||||0||A4|
65,25 1|g|mar|RICE|FARM|1|0||0||R/A1/F|
66,25 1|p||||1|0|CITY_CENTER|1|0:WARRIOR:100|R/F|SHEDET
67,25 1|g|for||||0||0||A2|
68,25 1|co||FISH|||0||0|||
69,25 1|co||FISH|||||0|||
59,26 0|co|||||||0|||
60,26 1|g|||||||0||A3|
61,26 1|g||CATTLE|PASTURE||0||0||A1|
62,26 1|g||||1|0|CITY_CENTER|1|0:WARRIOR:100|R/F|Sais
63,26 1|g|mar||||0||0||R/A1/F|
64,26 1|ph|jun|BANANAS|PLANTATION||0||0|||
65,26 1|gh||||1|0|ENCAMPMENT|0||A-1|
66,26 1|g||STONE|QUARRY|1|0||0||R/F|
67,26 1|gh||STONE|||0||0||R/A1/F|
68,26 1|co|||||||0|||
69,26 1|oc|||||||0|||
59,27 0|co|||||||0|||
60,27 1|co|||||||0|||
61,27 1|g|||||0||0||A1|
62,27 1|g||||1|0||0||R/A-1/F|
63,27 1|g||||1|||0||R/A-1/F|
64,27 1|g|||||||0|||
65,27 1|ph|||SPHINX||0||0||A-1|
66,27 1|p||||1|0|WONDER|0||R/A1/F|
67,27 1|g|mar||||||0||R/A5/F|
68,27 1|co|||||||0|63:GALLEY:72||
69,27 0|oc|||||||0|||
60,28 0|co|||||||0|||
61,28 1|co|||||||0|||
62,28 1|p|jun|BANANAS|||0||0||R/A4/F|
63,28 1|p|||||0||0||R/A1/F|
64,28 1|p||WHEAT||1|||0||A1|
65,28 1|ph|for||||0||0||A1|
66,28 1|p|||FARM|1|0||0||R/A4/F|
67,28 1|p|||SPHINX||0||0||R/F|
68,28 1|co|||||||0|||
69,28 1|oc|||||||0|||
60,29 0|oc|||||||0|||
61,29 1|co|||||||0|||
62,29 1|co|||||||0|||
63,29 1|p||WHEAT|||||0||A3|
64,29 1|p||||1|0||0||A2|
65,29 1|p|||FARM|1|0||0||R/A2/F|
66,29 1|ph||||1|0|CITY_CENTER|1|0:WARRIOR:84|R/F|Râ-Kedet
67,29 1|ph|||MINE||0||0|0:ARCHER:100|A3|
68,29 1|co|||||||0|||
69,29 1|co||PEARLS|||||0|||
61,30 0|oc|||||||0|||
62,30 0|oc|||||||0|||
63,30 0|co|||||||0|||
64,30 1|co|||||||0|||
65,30 1|p||IVORY|CAMP||0||0||R/A4/F|
66,30 1|p|||FARM||0||0||R/A1/F|
67,30 1|ph|||MINE||0||0|||
68,30 1|co|||||||0|||
69,30 1|co|||||||0|||
70,30 0|co|||||||0|||
61,31 0|oc|||||||0|||
62,31 0|co|||||||0|||
63,31 0|oc|||||||0|||
64,31 1|co|||||||0|||
65,31 1|co|||||||0|||
66,31 1|p|||||||0|||
67,31 1|p|||||||0||A1|
68,31 1|p|||||||0||A5|
69,31 0|co|||||||0|||
70,31 0|co||FISH|||||0|||
63,32 0|co||CRABS|||||0|||
64,32 0|co|||||||0|||
65,32 0|co|||||||0|||
66,32 0|p||WHEAT|||||0||A2|
67,32 0|p|||||||0||A1|
68,32 0|co|||||||0|||
69,32 0|co|||||||0|||
70,32 0|oc|||||||0|||
64,33 0|oc|||||||0|||
65,33 0|co|||||||0|||
66,33 0|g|mar||||||0||A1|
67,33 0|g|for|DEER|||||0||A2|
68,33 0|co|||||||0|||
69,33 0|oc|||||||0|||
65,34 0|co|||||||0|||
66,34 0|g|mar|RICE|||||0||A2|
67,34 0|g|||||||0||A1|
68,34 0|co|||||||0|||
69,34 0|co|||||||0|||
64,35 0|oc|||||||0|||
65,35 0|co|||||||0|||
66,35 0|g|||||||0||A1|
67,35 0|gh|for||||||0||A2|
68,35 0|gh||IRON|||||0||A6|
65,36 0|co||FISH|||||0|||
66,36 0|g|||||||0||A3|
67,36 0|gh||SHEEP|||||0||A2|
68,36 0|gm|||||||0||A4|
69,36 0|co|||||||0|||
65,37 0|co|||||||0|||
66,37 0|gh|||||||0||A1|
67,37 0|gh||SHEEP|||||0|||
68,37 0|g|||||||0||A3|
69,37 0|co||FISH|||||0|||
66,38 0|g||RICE|||||0||A4|
67,38 0|g|||||||0|||
68,38 0|g|mar||||||0||A1|
69,38 0|co|||||||0|||
66,39 0|co|||||||0|||
67,39 0|t|||||||0||A1|
68,39 0|th|||||||0||A2|
```

## NATURAL WONDERS SEEN
- Tsingy de Bemaraha @(49,16)

## DIAGNOSTICS
- section status: cities=ok, city_states_met=ok, civics_available=ok, current_civic=ok, current_research=ok, empire=ok, envoys=ok, government=ok, great_people=ok, header=ok, majors_met=ok, map=ok, notifications=ok, policy_available=ok, policy_slots=ok, religion=ok, resources=ok, techs_available=ok, units=ok, victories=ok
- generation time: 2.80s
- per-query timing (s): meta=0.368, choices=0.342, cities=0.359, units=0.343, map=0.357, diplo=0.345, religion=0.342, notif=0.343
- compatibility notes (fallback paths, not failures):
    - `CHOICES.probe`: using cul:CanProgress() for civic availability
- last trace per query (for post-mortem):
    - `meta`: TRACE|META|great_people
    - `choices`: TRACE|CHOICES|civics_available
    - `cities`: TRACE|CITY|262147|end
    - `units`: TRACE|UNITS|barbarian_camps
    - `map`: (no traces)
    - `diplo`: TRACE|DIPLO|envoys
    - `religion`: TRACE|REL|per_city_religion
    - `notif`: TRACE|NOTIF|notifications
- categories intentionally omitted (base-game only):
    - governors (Rise & Fall)
    - loyalty (Rise & Fall)
    - era score, Golden/Dark Ages, dedications (Rise & Fall)
    - formal alliances with level (Rise & Fall)
    - diplomatic favor, World Congress, Diplomatic Victory (Gathering Storm)
    - climate, disasters, floods, volcanoes (Gathering Storm)
    - power, resource consumption, canals, dams (Gathering Storm)
    - railroads (Gathering Storm)

<!-- coach snapshot: schema=coach-snapshot/1.1 turn=87 generated_at=1785305059.6712434 failed_sections=none -->
