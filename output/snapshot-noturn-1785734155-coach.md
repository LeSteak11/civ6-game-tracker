# CIV6 COACH SNAPSHOT — turn UNKNOWN (meta query failed)
_meta query failed — schema coach-snapshot/1.6 coach 1.10.0_
_ruleset: QUERY FAILED — static-table fallbacks in effect; treat derived numbers with suspicion_

> **PARTIAL SNAPSHOT** — one or more queries failed live:
> `cities, city_states_met, civic_tree, civics_available, current_civic, current_research, emergencies, empire, envoys, era, government, governors, great_people, header, majors_met, map, notifications, policy_available, policy_slots, probe, religion, resources, ruleset, tech_tree, techs_available, units, victories` — see the DIAGNOSTICS section at the bottom.
>
> Do not treat missing/zero values below as game state; they may be query failures.

## CHANGES SINCE LAST SNAPSHOT
No meaningful changes. (-23 turn(s) elapsed.)
- ⚠ delta incomplete — skipped (section failed on one side): empire, tiles, units, cities, resources, majors_met, city_states_met

## TURN BLOCKERS
- units: QUERY FAILED — cannot list idle/promo units
- cities: QUERY FAILED — cannot check idle city production
- current research: QUERY FAILED — cannot confirm selection
- current civic: QUERY FAILED — cannot confirm selection

## EMPIRE
- **QUERY FAILED — empire**
- **enabled victories:** **QUERY FAILED — victories**
- **era score:** **QUERY FAILED — era**

## RESEARCH / CIVIC
- **tech:** **QUERY FAILED — current_research**
- **civic:** **QUERY FAILED — current_civic**

### TECHS AVAILABLE
**QUERY FAILED — techs_available**

### CIVICS AVAILABLE
**QUERY FAILED — civics_available**

### TECH TREE
**QUERY FAILED — tech_tree**

### CIVIC TREE
**QUERY FAILED — civic_tree**

## RESOURCES
- **QUERY FAILED — resources**

## GOVERNMENT & POLICIES
- **QUERY FAILED — government**
- **slotted:** **QUERY FAILED — policy_slots**
- **available:** **QUERY FAILED — policy_available**

## GOVERNORS (R&F)
- **QUERY FAILED — governors**

## GREAT PEOPLE
**QUERY FAILED — great_people**

## RELIGION
- **QUERY FAILED — religion (TruncatedOutput: EOQ end-marker missing — output cut off (likely a mid-stream timeout); section marked failed, not parti)**

## CITIES
**QUERY FAILED — cities (TruncatedOutput: EOQ end-marker missing — output cut off (likely a mid-stream timeout); section marked failed, not parti)**

## UNITS
**QUERY FAILED — units (TruncatedOutput: EOQ end-marker missing — output cut off (likely a mid-stream timeout); section marked failed, not parti)**

## DIPLOMACY
- **envoys:** **QUERY FAILED — envoys**
### MAJORS MET
**QUERY FAILED — majors_met**
### CITY-STATES MET
**QUERY FAILED — city_states_met**
### EMERGENCIES (R&F)
- **QUERY FAILED — emergencies**

## NOTIFICATIONS
**QUERY FAILED — notifications**

## REVEALED MAP
**QUERY FAILED — map (TruncatedOutput: EOQ end-marker missing — output cut off (likely a mid-stream timeout); section marked failed, not parti)**

## DIAGNOSTICS
- section status: cities=failed, city_states_met=failed, civic_tree=failed, civics_available=failed, current_civic=failed, current_research=failed, emergencies=failed, empire=failed, envoys=failed, era=failed, government=failed, governors=failed, great_people=failed, header=failed, majors_met=failed, map=failed, notifications=failed, policy_available=failed, policy_slots=failed, probe=failed, religion=failed, resources=failed, ruleset=failed, tech_tree=failed, techs_available=failed, units=failed, victories=failed
- generation time: 25.55s
- per-query timing (s): meta=2.334, choices=2.322, cities=2.326, units=2.314, map=2.327, diplo=2.319, religion=2.32, notif=2.322, xpac=2.314, ruleset=2.323, probe=2.323
- **failures at runtime:**
    - `meta`: TruncatedOutput: EOQ end-marker missing — output cut off (likely a mid-stream timeout); section marked failed, not partial
    - `choices`: TruncatedOutput: EOQ end-marker missing — output cut off (likely a mid-stream timeout); section marked failed, not partial
    - `cities`: TruncatedOutput: EOQ end-marker missing — output cut off (likely a mid-stream timeout); section marked failed, not partial
    - `units`: TruncatedOutput: EOQ end-marker missing — output cut off (likely a mid-stream timeout); section marked failed, not partial
    - `map`: TruncatedOutput: EOQ end-marker missing — output cut off (likely a mid-stream timeout); section marked failed, not partial
    - `diplo`: TruncatedOutput: EOQ end-marker missing — output cut off (likely a mid-stream timeout); section marked failed, not partial
    - `religion`: TruncatedOutput: EOQ end-marker missing — output cut off (likely a mid-stream timeout); section marked failed, not partial
    - `notif`: TruncatedOutput: EOQ end-marker missing — output cut off (likely a mid-stream timeout); section marked failed, not partial
    - `xpac`: TruncatedOutput: EOQ end-marker missing — output cut off (likely a mid-stream timeout); section marked failed, not partial
    - `ruleset`: TruncatedOutput: EOQ end-marker missing — output cut off (likely a mid-stream timeout); section marked failed, not partial
    - `probe`: TruncatedOutput: EOQ end-marker missing — output cut off (likely a mid-stream timeout); section marked failed, not partial
- last trace per query (for post-mortem):
    - `meta`: (no traces)
    - `choices`: (no traces)
    - `cities`: (no traces)
    - `units`: (no traces)
    - `map`: (no traces)
    - `diplo`: (no traces)
    - `religion`: (no traces)
    - `notif`: (no traces)
    - `xpac`: (no traces)
    - `ruleset`: (no traces)
    - `probe`: (no traces)
- expansion-mechanic capability (derived from this capture's probe):
    - capability probe failed this capture — expansion-mechanic availability UNKNOWN (nothing extracted beyond base sections)

<!-- coach snapshot: schema=coach-snapshot/1.6 turn=None generated_at=1785734155.609353 failed_sections=cities,city_states_met,civic_tree,civics_available,current_civic,current_research,emergencies,empire,envoys,era,government,governors,great_people,header,majors_met,map,notifications,policy_available,policy_slots,probe,religion,resources,ruleset,tech_tree,techs_available,units,victories counts: cities=failed units=failed tiles=failed majors=failed city_states=failed gossip=failed rival_cities=failed tech_tree=failed civic_tree=failed md_chars=5656 -->
