# CIV 6 GAME PACK — Egypt (game-001_egypt)

`game-pack/1.0`  ·  built from the on-disk archive, no game required.

## COVERAGE — read this before drawing conclusions

- **Civ / leader:** Egypt / Cleopatra
- **Settings:** Chieftain difficulty, Continents map (Small), Standard speed
- **Captured turns:** T87–T396 — 208 captures covering 208 of 310 turns in that span
- **Turns 1–86 were never captured.** Nothing about the player's own early game is in this pack; world events are back-filled to T52 via gossip, but the player's own arc starts at T87.
- **Gaps inside the captured span:** T113, 126-127, 183, 185, 187, 189, 196, 200, 202, 209-210, 217-219, 224-225, 227-228, 231-232, 234-235, 241, 245, 247, 249, 251-252, 255, 258, 264, 266-267, 272, 274-275, 281-283, 287, 289-291, 295-297, 306, 309, 315, 320-321, 330-334, 336-337, 340-341, 343-344, 346-348, 350, 353-356, 358-359, 361-366, 368-369, 371-373, 375-377, 381-395

> **SCHEMA DRIFT WARNING.** This archive spans multiple coach versions: 1.2.1 (12 captures), 1.3.0 (5 captures), 1.4.0 (4 captures), 1.5.0 (7 captures), 1.6.0 (24 captures), 1.7.0 (3 captures), 1.7.1 (153 captures). Field availability and derivation changed across those versions, so a metric that appears to jump may reflect a tooling change rather than a game event. Treat cross-version comparisons with suspicion, and prefer the chronology (which is version-stable) when a curve and a record disagree.

- **Chronology:** 344 gossip entries + 75 observed events (0 duplicates removed)
- **Narrative:** turn-by-turn blocks for 208 turns

**Data trust.** `?` means the value was not readable at capture time — it never means zero. Rival figures are observations, not omniscience: a civ under fog keeps its last-known values. Judge decisions by what was visible on that turn, not by later information.

- **Note:** LEAN pack: revealed-map dump omitted from final state (87 KB)
- **Note:** Budget 150,000 chars exceeded — revealed-map dump dropped from final state (87 KB)
- **Note:** Budget 150,000 chars still exceeded — final state omitted entirely

---

## 1. YOUR TIMELINE

One row per captured turn, mined from the snapshot archive (highest revision per turn).

| Turn | Era | Score | Sci/t | Cul/t | Gold | Gold/t | Faith | Mil | Cities | Pop | Techs | Civics | Trade | Units |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 87 | Classical Era | 79 | 17.1 | 11.3 | 330 | 10.4 | 184 | 119 | 4 | 14 | 13 | 8 | 1 | 6 |
| 88 | Classical Era | 79 | 17.1 | 12.3 | 340 | 10.4 | 191 | 120 | 4 | 14 | 13 | 8 | 1 | 7 |
| 89 | Classical Era | 91 | 17.8 | 12.6 | 354 | 13.6 | 206 | 120 | 4 | 15 | 13 | 8 | 1 | 6 |
| 90 | Classical Era | 92 | 17.8 | 12.6 | 368 | 13.6 | 220 | 121 | 4 | 15 | 13 | 8 | 1 | 6 |
| 91 | Classical Era | 92 | 17.8 | 12.6 | 381 | 13.6 | 235 | 123 | 4 | 15 | 13 | 9 | 1 | 6 |
| 92 | Classical Era | 94 | 18.3 | 12.8 | 395 | 13.6 | 249 | 125 | 4 | 16 | 13 | 9 | 1 | 6 |
| 93 | Classical Era | 95 | 18.3 | 12.8 | 408 | 13.6 | 264 | 127 | 4 | 16 | 13 | 9 | 1 | 6 |
| 94 | Classical Era | 95 | 19.0 | 13.1 | 422 | 13.6 | 279 | 129 | 4 | 17 | 14 | 9 | 1 | 6 |
| 95 | Classical Era | 98 | 19.0 | 13.1 | 435 | 12.6 | 293 | 131 | 4 | 17 | 14 | 10 | 1 | 6 |
| 96 | Classical Era | 103 | 19.0 | 13.1 | 448 | 12.6 | 311 | 128 | 4 | 17 | 14 | 10 | 1 | 6 |
| 97 | Classical Era | 103 | 19.0 | 13.1 | 460 | 12.6 | 328 | 129 | 4 | 17 | 14 | 10 | 1 | 6 |
| 98 | Classical Era | 106 | 19.0 | 13.1 | 476 | 15.4 | 346 | 134 | 4 | 17 | 14 | 10 | 1 | 7 |
| 99 | Classical Era | 106 | 19.0 | 15.2 | 491 | 15.4 | 363 | 135 | 4 | 17 | 14 | 10 | 1 | 8 |
| 100 | Classical Era | 106 | 19.6 | 15.4 | 507 | 14.2 | 380 | 137 | 4 | 18 | 14 | 11 | 1 | 9 |
| 101 | Classical Era | 109 | 19.6 | 15.4 | 521 | 14.2 | 401 | 138 | 4 | 18 | 14 | 11 | 1 | 9 |
| 102 | Classical Era | 109 | 19.6 | 15.4 | 535 | 14.2 | 421 | 139 | 4 | 18 | 15 | 11 | 1 | 9 |
| 103 | Classical Era | 111 | 20.3 | 15.7 | 549 | 14.2 | 441 | 140 | 4 | 19 | 15 | 11 | 1 | 9 |
| 104 | Classical Era | 112 | 20.3 | 15.7 | 564 | 14.2 | 462 | 141 | 4 | 19 | 15 | 12 | 1 | 9 |
| 105 | Classical Era | 114 | 21.0 | 16.0 | 578 | 13.2 | 482 | 143 | 4 | 20 | 15 | 12 | 1 | 7 |
| 106 | Classical Era | 115 | 21.0 | 16.0 | 591 | 13.2 | 504 | 144 | 4 | 20 | 15 | 12 | 1 | 7 |
| 107 | Classical Era | 115 | 21.0 | 16.0 | 604 | 12.2 | 526 | 145 | 4 | 20 | 15 | 12 | 1 | 7 |
| 108 | Classical Era | 115 | 21.0 | 16.0 | 616 | 12.2 | 548 | 141 | 4 | 20 | 16 | 12 | 1 | 7 |
| 109 | Classical Era | 117 | 21.0 | 16.0 | 546 | 10.2 | 570 | 147 | 4 | 20 | 16 | 12 | 1 | 7 |
| 110 | Classical Era | 117 | 21.0 | 17.9 | 557 | 10.2 | 592 | 148 | 4 | 20 | 16 | 12 | 1 | 7 |
| 111 | Classical Era | 117 | 21.0 | 17.9 | 567 | 10.2 | 615 | 156 | 4 | 20 | 16 | 12 | 0 | 8 |
| 112 | Classical Era | 117 | 21.0 | 17.9 | 577 | 10.2 | 637 | 158 | 4 | 20 | 16 | 12 | 1 | 8 |
| 114 | Classical Era | 117 | 21.0 | 17.9 | 598 | 10.2 | 681 | 159 | 4 | 20 | 16 | 13 | 1 | 8 |
| 115 | Medieval Era | 119 | 21.7 | 18.2 | 608 | 9.2 | 703 | 160 | 4 | 21 | 17 | 13 | 1 | 9 |
| 116 | Medieval Era | 122 | 22.3 | 18.4 | 617 | 9.2 | 725 | 186 | 4 | 22 | 17 | 13 | 1 | 9 |
| 117 | Medieval Era | 123 | 22.3 | 18.4 | 626 | 9.2 | 748 | 187 | 4 | 22 | 17 | 13 | 1 | 9 |
| 118 | Medieval Era | 123 | 22.3 | 18.4 | 567 | 6.2 | 770 | 187 | 4 | 22 | 17 | 13 | 1 | 9 |
| 119 | Medieval Era | 123 | 22.3 | 18.4 | 576 | 9.2 | 792 | 178 | 4 | 22 | 17 | 13 | 1 | 9 |
| 120 | Medieval Era | 123 | 22.3 | 18.4 | 586 | 9.2 | 814 | 173 | 4 | 22 | 17 | 13 | 1 | 9 |
| 121 | Medieval Era | 123 | 22.3 | 18.4 | 592 | 6.4 | 836 | 174 | 4 | 22 | 17 | 13 | 1 | 9 |
| 122 | Medieval Era | 124 | 23.1 | 18.8 | 490 | 8.2 | 858 | 175 | 4 | 23 | 17 | 14 | 1 | 9 |
| 123 | Medieval Era | 126 | 23.8 | 19.1 | 502 | 8.2 | 880 | 176 | 4 | 24 | 18 | 14 | 1 | 9 |
| 124 | Medieval Era | 132 | 23.8 | 19.1 | 510 | 8.2 | 906 | 187 | 4 | 24 | 18 | 14 | 1 | 9 |
| 125 | Medieval Era | 132 | 23.8 | 19.1 | 518 | 8.2 | 932 | 188 | 4 | 24 | 18 | 14 | 1 | 9 |
| 128 | Medieval Era | 132 | 23.8 | 20.0 | 542 | 8.2 | 1013 | 190 | 4 | 24 | 18 | 14 | 1 | 8 |
| 129 | Medieval Era | 132 | 24.3 | 20.2 | 551 | 7.9 | 1040 | 190 | 4 | 25 | 18 | 14 | 1 | 9 |
| 130 | Medieval Era | 133 | 24.3 | 20.2 | 559 | 6.9 | 1067 | 191 | 4 | 25 | 18 | 14 | 1 | 9 |
| 131 | Medieval Era | 133 | 24.8 | 20.5 | 460 | 9.3 | 1094 | 183 | 4 | 25 | 18 | 15 | 1 | 9 |
| 132 | Medieval Era | 135 | 24.8 | 20.5 | 470 | 9.3 | 1121 | 178 | 4 | 25 | 19 | 15 | 1 | 9 |
| 133 | Medieval Era | 137 | 24.8 | 20.5 | 479 | 9.3 | 1149 | 179 | 4 | 25 | 19 | 15 | 1 | 9 |
| 134 | Medieval Era | 137 | 25.5 | 20.8 | 488 | 9.3 | 1176 | 181 | 4 | 26 | 19 | 15 | 1 | 9 |
| 135 | Medieval Era | 138 | 25.5 | 20.8 | 498 | 9.3 | 1204 | 183 | 4 | 26 | 19 | 15 | 0 | 9 |
| 136 | Medieval Era | 138 | 24.7 | 20.5 | 520 | 24.0 | 1231 | 186 | 4 | 25 | 19 | 15 | 1 | 10 |
| 137 | Medieval Era | 137 | 25.4 | 20.8 | 544 | 24.0 | 1259 | 189 | 4 | 26 | 20 | 15 | 1 | 10 |
| 138 | Medieval Era | 140 | 25.4 | 20.8 | 568 | 23.0 | 1286 | 192 | 4 | 26 | 20 | 15 | 1 | 11 |
| 139 | Medieval Era | 140 | 25.4 | 20.8 | 591 | 22.0 | 1314 | 219 | 4 | 26 | 20 | 15 | 1 | 12 |
| 140 | Medieval Era | 140 | 26.1 | 21.1 | 610 | 19.9 | 1341 | 245 | 4 | 27 | 20 | 15 | 1 | 12 |
| 141 | Medieval Era | 141 | 26.1 | 21.1 | 630 | 17.9 | 1369 | 247 | 4 | 27 | 20 | 15 | 1 | 13 |
| 142 | Medieval Era | 141 | 26.1 | 21.1 | 578 | 17.9 | 1396 | 279 | 4 | 27 | 20 | 15 | 1 | 13 |
| 143 | Medieval Era | 147 | 27.9 | 21.4 | 596 | 17.9 | 1424 | 280 | 5 | 28 | 20 | 15 | 1 | 12 |
| 144 | Medieval Era | 147 | 27.9 | 21.4 | 734 | 17.9 | 1451 | 292 | 5 | 28 | 21 | 15 | 1 | 12 |
| 145 | Medieval Era | 149 | 27.9 | 21.4 | 749 | 15.0 | 1479 | 289 | 5 | 28 | 21 | 15 | 1 | 13 |
| 146 | Medieval Era | 149 | 27.9 | 21.4 | 767 | 17.9 | 1506 | 291 | 5 | 28 | 21 | 16 | 1 | 13 |
| 147 | Medieval Era | 151 | 27.9 | 21.4 | 785 | 17.9 | 1531 | 293 | 5 | 28 | 21 | 16 | 1 | 13 |
| 148 | Medieval Era | 151 | 27.9 | 21.4 | 800 | 14.9 | 1555 | 295 | 5 | 28 | 21 | 16 | 1 | 13 |
| 149 | Medieval Era | 151 | 29.0 | 21.8 | 820 | 20.5 | 1580 | 285 | 5 | 30 | 21 | 16 | 1 | 13 |
| 150 | Medieval Era | 153 | 29.0 | 21.8 | 840 | 20.5 | 1604 | 287 | 5 | 30 | 22 | 16 | 1 | 13 |
| 151 | Medieval Era | 155 | 28.3 | 20.5 | 861 | 20.5 | 1629 | 293 | 5 | 29 | 22 | 17 | 1 | 14 |
| 152 | Medieval Era | 156 | 29.5 | 24.4 | 880 | 18.1 | 1650 | 298 | 5 | 30 | 22 | 17 | 1 | 14 |
| 153 | Medieval Era | 157 | 29.5 | 24.4 | 901 | 21.1 | 1672 | 303 | 5 | 30 | 22 | 17 | 1 | 14 |
| 154 | Medieval Era | 160 | 29.5 | 24.4 | 922 | 21.1 | 1693 | 307 | 5 | 30 | 22 | 17 | 1 | 13 |
| 155 | Medieval Era | 160 | 30.3 | 25.7 | 943 | 21.1 | 1715 | 309 | 5 | 31 | 22 | 17 | 1 | 14 |
| 156 | Medieval Era | 161 | 30.3 | 25.7 | 964 | 24.7 | 1740 | 311 | 5 | 31 | 22 | 17 | 1 | 14 |
| 157 | Medieval Era | 161 | 30.3 | 25.7 | 989 | 24.7 | 1764 | 291 | 5 | 31 | 22 | 17 | 1 | 14 |
| 158 | Medieval Era | 161 | 30.3 | 25.7 | 1014 | 24.7 | 1789 | 308 | 5 | 31 | 22 | 17 | 1 | 14 |
| 159 | Medieval Era | 161 | 31.0 | 26.0 | 1038 | 24.7 | 1813 | 307 | 5 | 32 | 22 | 17 | 1 | 14 |
| 160 | Medieval Era | 168 | 37.9 | 28.2 | 1064 | 24.4 | 1840 | 309 | 6 | 33 | 22 | 17 | 1 | 13 |
| 161 | Medieval Era | 171 | 37.9 | 28.2 | 1088 | 24.4 | 1868 | 306 | 6 | 33 | 22 | 17 | 1 | 13 |
| 162 | Medieval Era | 171 | 37.9 | 28.2 | 1113 | 23.4 | 1895 | 282 | 6 | 33 | 23 | 18 | 1 | 13 |
| 163 | Medieval Era | 175 | 40.4 | 24.7 | 1164 | 38.8 | 1918 | 309 | 6 | 35 | 23 | 18 | 1 | 12 |
| 164 | Medieval Era | 180 | 41.1 | 25.0 | 912 | 33.8 | 1941 | 333 | 6 | 36 | 23 | 18 | 1 | 13 |
| 165 | Medieval Era | 181 | 41.1 | 25.0 | 946 | 33.8 | 1964 | 326 | 6 | 36 | 23 | 18 | 1 | 12 |
| 166 | Medieval Era | 181 | 41.7 | 29.4 | 980 | 34.8 | 1988 | 313 | 6 | 37 | 23 | 18 | 1 | 11 |
| 167 | Medieval Era | 182 | 41.9 | 29.5 | 1014 | 34.9 | 2011 | 326 | 6 | 37 | 24 | 18 | 1 | 11 |
| 168 | Medieval Era | 184 | 42.5 | 29.8 | 1049 | 34.9 | 2034 | 338 | 6 | 38 | 24 | 18 | 1 | 11 |
| 169 | Medieval Era | 185 | 55.2 | 35.1 | 871 | 29.7 | 2057 | 329 | 6 | 38 | 24 | 18 | 1 | 11 |
| 170 | Medieval Era | 188 | 55.2 | 34.0 | 905 | 33.9 | 2079 | 340 | 6 | 38 | 24 | 18 | 1 | 11 |
| 171 | Medieval Era | 188 | 55.2 | 34.0 | 939 | 33.9 | 2101 | 333 | 6 | 38 | 24 | 18 | 1 | 11 |
| 172 | Renaissance Era | 188 | 55.2 | 34.0 | 948 | 33.9 | 2123 | 334 | 6 | 38 | 25 | 18 | 1 | 11 |
| 173 | Renaissance Era | 190 | 55.4 | 36.1 | 982 | 33.8 | 2145 | 337 | 6 | 40 | 25 | 18 | 1 | 11 |
| 174 | Renaissance Era | 192 | 56.7 | 36.7 | 902 | 39.2 | 2170 | 330 | 6 | 40 | 25 | 18 | 1 | 10 |
| 175 | Renaissance Era | 192 | 57.4 | 37.0 | 928 | 40.2 | 2195 | 332 | 6 | 41 | 25 | 19 | 1 | 10 |
| 176 | Renaissance Era | 195 | 58.1 | 37.4 | 968 | 41.3 | 2220 | 346 | 6 | 42 | 25 | 19 | 1 | 10 |
| 177 | Renaissance Era | 196 | 64.4 | 38.4 | 1014 | 44.5 | 2246 | 350 | 6 | 42 | 26 | 19 | 1 | 10 |
| 178 | Renaissance Era | 201 | 64.4 | 38.4 | 1055 | 41.3 | 2271 | 353 | 6 | 42 | 26 | 19 | 1 | 10 |
| 179 | Renaissance Era | 201 | 72.8 | 39.5 | 1100 | 43.5 | 2296 | 350 | 6 | 42 | 26 | 19 | 1 | 10 |
| 180 | Renaissance Era | 204 | 72.8 | 39.5 | 1143 | 43.5 | 2321 | 357 | 6 | 42 | 27 | 19 | 1 | 10 |
| 181 | Renaissance Era | 206 | 77.0 | 39.5 | 1187 | 42.5 | 2346 | 364 | 6 | 42 | 27 | 19 | 1 | 10 |
| 182 | Renaissance Era | 206 | 81.2 | 39.5 | 1226 | 37.3 | 2372 | 368 | 6 | 42 | 27 | 20 | 1 | 10 |
| 184 | Renaissance Era | 209 | 85.6 | 40.4 | 1257 | 40.4 | 2422 | 370 | 6 | 45 | 28 | 20 | 1 | 10 |
| 186 | Renaissance Era | 214 | 90.5 | 40.7 | 1338 | 39.4 | 2472 | 377 | 6 | 46 | 28 | 20 | 1 | 10 |
| 188 | Renaissance Era | 214 | 90.5 | 42.8 | 1418 | 40.0 | 2523 | 384 | 6 | 46 | 28 | 20 | 1 | 10 |
| 190 | Renaissance Era | 214 | 90.5 | 42.8 | 1498 | 40.0 | 2573 | 390 | 6 | 46 | 29 | 20 | 1 | 10 |
| 191 | Renaissance Era | 216 | 91.2 | 43.1 | 1538 | 40.0 | 2598 | 394 | 6 | 47 | 29 | 21 | 1 | 10 |
| 192 | Renaissance Era | 219 | 89.5 | 42.0 | 1578 | 26.4 | 2622 | 397 | 6 | 48 | 29 | 21 | 1 | 11 |
| 193 | Renaissance Era | 220 | 93.5 | 42.0 | 1401 | 21.2 | 2646 | 382 | 6 | 48 | 29 | 21 | 1 | 11 |
| 194 | Renaissance Era | 220 | 93.5 | 42.0 | 1426 | 23.8 | 2670 | 384 | 6 | 48 | 29 | 21 | 1 | 11 |
| 195 | Renaissance Era | 220 | 93.5 | 42.0 | 1449 | 23.8 | 2695 | 386 | 6 | 48 | 29 | 21 | 1 | 11 |
| 197 | Renaissance Era | 220 | 101.7 | 42.0 | 1496 | 22.8 | 2743 | 390 | 6 | 48 | 30 | 21 | 1 | 11 |
| 198 | Renaissance Era | 222 | 101.7 | 42.0 | 1519 | 22.8 | 2767 | 371 | 6 | 48 | 30 | 21 | 1 | 11 |
| 199 | Renaissance Era | 225 | 101.7 | 42.0 | 1542 | 22.8 | 2791 | 368 | 6 | 48 | 30 | 21 | 1 | 10 |
| 201 | Renaissance Era | 225 | 101.7 | 42.0 | 1587 | 22.8 | 2839 | 377 | 6 | 48 | 30 | 22 | 1 | 10 |
| 203 | Renaissance Era | 228 | 101.3 | 42.0 | 1289 | 32.4 | 2887 | 355 | 6 | 49 | 30 | 22 | 1 | 11 |
| 204 | Renaissance Era | 228 | 101.3 | 42.0 | 1324 | 35.4 | 2911 | 358 | 6 | 49 | 30 | 22 | 1 | 11 |
| 205 | Industrial Era | 228 | 101.0 | 42.0 | 1362 | 37.0 | 2935 | 359 | 6 | 50 | 31 | 22 | 1 | 11 |
| 206 | Industrial Era | 231 | 101.0 | 43.0 | 1399 | 50.0 | 2959 | 371 | 6 | 50 | 31 | 22 | 2 | 12 |
| 207 | Industrial Era | 234 | 103.0 | 43.0 | 1449 | 50.0 | 2983 | 379 | 6 | 50 | 31 | 22 | 2 | 12 |
| 208 | Industrial Era | 234 | 103.0 | 43.0 | 1496 | 47.0 | 3007 | 387 | 6 | 50 | 31 | 22 | 2 | 12 |
| 211 | Industrial Era | 234 | 106.8 | 44.6 | 1650 | 53.6 | 3080 | 403 | 6 | 50 | 31 | 22 | 2 | 12 |
| 212 | Industrial Era | 234 | 106.8 | 44.6 | 1700 | 50.6 | 3106 | 407 | 6 | 50 | 32 | 22 | 2 | 12 |
| 213 | Industrial Era | 236 | 113.8 | 44.9 | 1754 | 50.6 | 3131 | 412 | 6 | 51 | 32 | 23 | 2 | 12 |
| 214 | Industrial Era | 239 | 115.9 | 47.0 | 1804 | 50.6 | 3156 | 416 | 6 | 51 | 32 | 23 | 2 | 12 |
| 215 | Industrial Era | 239 | 114.9 | 46.0 | 1841 | 39.9 | 3181 | 419 | 6 | 51 | 33 | 23 | 1 | 12 |
| 216 | Industrial Era | 241 | 135.9 | 47.6 | 1893 | 51.0 | 3206 | 423 | 6 | 52 | 33 | 23 | 2 | 12 |
| 220 | Industrial Era | 245 | 135.4 | 47.5 | 2093 | 50.7 | 3305 | 440 | 6 | 52 | 33 | 24 | 2 | 12 |
| 221 | Industrial Era | 247 | 157.1 | 45.5 | 2159 | 64.2 | 3330 | 445 | 6 | 52 | 33 | 24 | 3 | 12 |
| 222 | Industrial Era | 247 | 158.9 | 45.5 | 2223 | 63.2 | 3354 | 451 | 6 | 52 | 34 | 24 | 3 | 12 |
| 223 | Industrial Era | 249 | 158.9 | 46.6 | 2286 | 65.3 | 3379 | 456 | 6 | 52 | 34 | 24 | 3 | 12 |
| 226 | Modern Era | 253 | 161.7 | 46.9 | 2166 | 74.7 | 3453 | 438 | 6 | 53 | 35 | 24 | 4 | 13 |
| 229 | Modern Era | 255 | 162.4 | 47.2 | 2390 | 75.8 | 3527 | 458 | 6 | 54 | 35 | 24 | 4 | 13 |
| 230 | Modern Era | 261 | 162.4 | 47.2 | 2471 | 80.8 | 3552 | 471 | 6 | 54 | 35 | 25 | 4 | 13 |
| 233 | Modern Era | 262 | 162.3 | 47.5 | 2392 | 86.2 | 3626 | 465 | 6 | 55 | 36 | 25 | 5 | 14 |
| 236 | Modern Era | 264 | 162.3 | 47.5 | 2664 | 96.3 | 3700 | 488 | 6 | 55 | 36 | 25 | 5 | 14 |
| 237 | Modern Era | 264 | 170.3 | 47.5 | 2771 | 100.3 | 3725 | 496 | 6 | 55 | 36 | 26 | 5 | 14 |
| 238 | Modern Era | 269 | 178.8 | 47.5 | 2861 | 98.4 | 3750 | 504 | 6 | 55 | 36 | 26 | 5 | 14 |
| 239 | Modern Era | 272 | 180.8 | 47.5 | 2964 | 103.4 | 3774 | 513 | 6 | 55 | 37 | 26 | 5 | 15 |
| 240 | Modern Era | 274 | 180.2 | 47.4 | 3068 | 109.6 | 3799 | 521 | 6 | 56 | 37 | 26 | 5 | 14 |
| 242 | Modern Era | 280 | 181.0 | 47.5 | 2900 | 107.2 | 3848 | 507 | 6 | 56 | 37 | 26 | 5 | 15 |
| 243 | Modern Era | 280 | 181.0 | 47.5 | 3012 | 120.2 | 3873 | 516 | 6 | 56 | 37 | 26 | 6 | 16 |
| 244 | Modern Era | 279 | 180.6 | 47.6 | 2363 | 111.5 | 3895 | 462 | 6 | 55 | 37 | 26 | 5 | 17 |
| 246 | Modern Era | 279 | 181.4 | 49.2 | 2615 | 123.9 | 3938 | 470 | 6 | 56 | 38 | 26 | 6 | 17 |
| 248 | Modern Era | 282 | 187.1 | 51.2 | 2894 | 114.7 | 3989 | 483 | 6 | 56 | 38 | 26 | 6 | 17 |
| 250 | Modern Era | 283 | 186.9 | 51.1 | 2739 | 114.5 | 4039 | 452 | 6 | 57 | 38 | 26 | 6 | 17 |
| 253 | Modern Era | 284 | 196.4 | 50.0 | 3080 | 105.9 | 4104 | 507 | 6 | 58 | 38 | 26 | 6 | 18 |
| 254 | Atomic Era | 287 | 196.4 | 50.0 | 3186 | 105.9 | 4126 | 522 | 6 | 58 | 39 | 26 | 6 | 19 |
| 256 | Atomic Era | 289 | 208.0 | 50.0 | 3393 | 100.8 | 4170 | 548 | 6 | 58 | 39 | 27 | 6 | 19 |
| 257 | Atomic Era | 291 | 211.7 | 50.8 | 3497 | 103.4 | 4192 | 557 | 6 | 58 | 39 | 27 | 6 | 18 |
| 259 | Atomic Era | 291 | 222.2 | 52.9 | 3708 | 102.4 | 4236 | 568 | 6 | 58 | 39 | 27 | 6 | 18 |
| 260 | Atomic Era | 291 | 226.6 | 53.2 | 2827 | 99.2 | 4258 | 495 | 6 | 59 | 40 | 27 | 6 | 18 |
| 261 | Atomic Era | 294 | 226.4 | 53.2 | 2926 | 97.2 | 4280 | 509 | 6 | 59 | 40 | 27 | 6 | 18 |
| 262 | Atomic Era | 294 | 226.4 | 53.2 | 3023 | 97.2 | 4302 | 534 | 6 | 59 | 40 | 27 | 6 | 18 |
| 263 | Atomic Era | 300 | 227.1 | 53.5 | 3117 | 89.9 | 4324 | 510 | 7 | 60 | 40 | 27 | 6 | 17 |
| 265 | Atomic Era | 300 | 227.1 | 53.5 | 2512 | 93.1 | 4369 | 522 | 7 | 60 | 40 | 27 | 6 | 17 |
| 268 | Atomic Era | 301 | 224.1 | 53.9 | 1207 | 66.6 | 4435 | 558 | 7 | 62 | 40 | 27 | 5 | 18 |
| 269 | Information Era | 302 | 225.5 | 55.2 | 859 | 72.6 | 4458 | 517 | 7 | 62 | 41 | 27 | 5 | 19 |
| 270 | Information Era | 304 | 233.9 | 55.2 | 983 | 77.0 | 4481 | 525 | 7 | 62 | 42 | 27 | 5 | 19 |
| 271 | Information Era | 306 | 235.1 | 55.9 | 220 | 78.0 | 4504 | 546 | 7 | 61 | 43 | 27 | 5 | 20 |
| 273 | Information Era | 307 | 234.2 | 56.2 | 378 | 83.9 | 4550 | 489 | 7 | 62 | 43 | 28 | 5 | 20 |
| 276 | Information Era | 311 | 228.1 | 54.7 | 626 | 94.2 | 4619 | 510 | 7 | 63 | 43 | 28 | 5 | 19 |
| 277 | Information Era | 317 | 228.8 | 55.0 | 203 | 92.2 | 4642 | 509 | 8 | 64 | 44 | 29 | 5 | 18 |
| 278 | Information Era | 321 | 229.5 | 56.4 | 295 | 92.3 | 4664 | 517 | 8 | 65 | 44 | 29 | 5 | 18 |
| 279 | Information Era | 325 | 229.5 | 56.4 | 389 | 94.3 | 4687 | 525 | 8 | 65 | 44 | 29 | 5 | 18 |
| 280 | Information Era | 325 | 230.2 | 56.7 | 486 | 93.3 | 4710 | 533 | 8 | 66 | 44 | 30 | 5 | 19 |
| 284 | Information Era | 329 | 233.3 | 57.0 | 816 | 89.8 | 4800 | 571 | 8 | 67 | 45 | 30 | 4 | 18 |
| 285 | Information Era | 331 | 237.8 | 56.0 | 910 | 103.4 | 4823 | 568 | 8 | 67 | 45 | 30 | 5 | 18 |
| 286 | Information Era | 334 | 244.5 | 56.9 | 882 | 101.2 | 4846 | 576 | 8 | 68 | 45 | 30 | 5 | 17 |
| 288 | Information Era | 338 | 252.4 | 56.4 | 1082 | 94.8 | 4891 | 593 | 8 | 69 | 45 | 30 | 5 | 18 |
| 292 | Information Era | 338 | 254.7 | 56.9 | 550 | 99.2 | 4980 | 548 | 8 | 68 | 46 | 30 | 5 | 19 |
| 293 | Information Era | 340 | 259.3 | 57.1 | 634 | 95.6 | 5003 | 555 | 8 | 69 | 46 | 30 | 5 | 19 |
| 294 | Information Era | 341 | 257.6 | 58.7 | 312 | 99.0 | 5027 | 529 | 8 | 69 | 46 | 30 | 5 | 20 |
| 298 | Information Era | 343 | 259.6 | 59.2 | 266 | 94.8 | 5119 | 525 | 8 | 71 | 46 | 30 | 5 | 21 |
| 299 | Information Era | 343 | 259.9 | 59.2 | 366 | 99.8 | 5142 | 533 | 8 | 71 | 47 | 31 | 5 | 21 |
| 300 | Information Era | 347 | 259.6 | 59.2 | 469 | 103.8 | 5165 | 542 | 8 | 71 | 47 | 31 | 5 | 21 |
| 301 | Information Era | 353 | 258.4 | 59.5 | 364 | 103.8 | 5188 | 533 | 9 | 72 | 47 | 31 | 5 | 20 |
| 302 | Information Era | 353 | 258.4 | 59.5 | 463 | 97.8 | 5211 | 541 | 9 | 72 | 47 | 31 | 5 | 20 |
| 303 | Information Era | 353 | 262.0 | 59.5 | 566 | 102.8 | 5234 | 550 | 9 | 72 | 48 | 31 | 5 | 20 |
| 304 | Information Era | 355 | 260.7 | 59.8 | 224 | 101.8 | 5257 | 521 | 9 | 73 | 48 | 31 | 5 | 21 |
| 305 | Information Era | 356 | 259.3 | 59.8 | 325 | 101.4 | 5280 | 530 | 9 | 74 | 48 | 31 | 5 | 20 |
| 307 | Information Era | 357 | 257.0 | 60.7 | 520 | 103.4 | 5324 | 546 | 9 | 74 | 48 | 31 | 5 | 21 |
| 308 | Information Era | 357 | 256.5 | 61.2 | 612 | 90.4 | 5344 | 608 | 9 | 76 | 49 | 31 | 4 | 21 |
| 310 | Information Era | 361 | 259.0 | 61.5 | 792 | 90.4 | 5383 | 579 | 9 | 77 | 50 | 31 | 5 | 20 |
| 311 | Information Era | 364 | 259.1 | 61.5 | 883 | 90.4 | 5403 | 586 | 9 | 77 | 50 | 32 | 5 | 21 |
| 312 | Information Era | 366 | 277.0 | 63.9 | 981 | 97.9 | 5424 | 594 | 9 | 78 | 51 | 32 | 6 | 21 |
| 313 | Information Era | 369 | 283.3 | 63.9 | 1076 | 92.7 | 5444 | 602 | 9 | 78 | 51 | 32 | 6 | 21 |
| 314 | Information Era | 369 | 282.8 | 66.2 | 1171 | 95.9 | 5464 | 610 | 9 | 79 | 51 | 32 | 6 | 21 |
| 316 | Information Era | 372 | 282.1 | 66.5 | 914 | 106.9 | 5505 | 589 | 9 | 80 | 53 | 32 | 6 | 22 |
| 317 | Information Era | 375 | 280.0 | 66.5 | 1013 | 97.2 | 5525 | 597 | 9 | 80 | 53 | 32 | 6 | 22 |
| 318 | Information Era | 378 | 280.0 | 66.5 | 1110 | 97.2 | 5546 | 605 | 9 | 80 | 54 | 32 | 6 | 23 |
| 319 | Information Era | 380 | 275.7 | 66.1 | 1200 | 91.0 | 5566 | 613 | 9 | 82 | 54 | 32 | 5 | 22 |
| 322 | Information Era | 382 | 276.1 | 66.0 | 1512 | 105.7 | 5626 | 639 | 9 | 82 | 55 | 32 | 6 | 22 |
| 323 | Information Era | 384 | 276.6 | 66.1 | 1205 | 101.4 | 5646 | 613 | 9 | 83 | 55 | 32 | 6 | 23 |
| 324 | Information Era | 385 | 276.5 | 68.0 | 840 | 104.2 | 5666 | 582 | 9 | 85 | 56 | 33 | 6 | 24 |
| 325 | Information Era | 391 | 278.3 | 68.3 | 735 | 105.2 | 5688 | 574 | 9 | 85 | 56 | 34 | 6 | 24 |
| 326 | Information Era | 393 | 268.6 | 66.0 | 833 | 99.4 | 5709 | 583 | 9 | 85 | 56 | 35 | 6 | 23 |
| 327 | Information Era | 395 | 269.5 | 67.1 | 949 | 119.2 | 5730 | 592 | 9 | 86 | 57 | 36 | 6 | 23 |
| 328 | Information Era | 400 | 270.0 | 67.1 | 579 | 112.2 | 5753 | 561 | 9 | 86 | 57 | 36 | 6 | 24 |
| 329 | Information Era | 400 | 270.6 | 67.1 | 199 | 107.9 | 5772 | 529 | 9 | 86 | 58 | 36 | 6 | 25 |
| 335 | Information Era | 406 | 270.7 | 69.7 | 856 | 103.8 | 5890 | 584 | 9 | 90 | 59 | 36 | 6 | 23 |
| 338 | Information Era | 409 | 284.6 | 59.5 | 233 | 94.2 | 5952 | 572 | 9 | 91 | 59 | 36 | 6 | 23 |
| 339 | Information Era | 409 | 285.0 | 61.0 | 333 | 99.8 | 5972 | 580 | 9 | 91 | 59 | 36 | 6 | 23 |
| 342 | Information Era | 415 | 283.0 | 60.1 | 623 | 104.8 | 6035 | 604 | 9 | 93 | 60 | 36 | 6 | 23 |
| 345 | Information Era | 422 | 283.8 | 61.4 | 931 | 96.3 | 6098 | 630 | 9 | 93 | 61 | 37 | 4 | 23 |
| 349 | Information Era | 427 | 281.3 | 81.8 | 1231 | 120.9 | 6203 | 655 | 9 | 94 | 62 | 37 | 6 | 22 |
| 351 | Information Era | 432 | 281.7 | 81.8 | 1478 | 119.5 | 6259 | 676 | 9 | 95 | 62 | 37 | 6 | 23 |
| 352 | Information Era | 433 | 283.7 | 82.0 | 1598 | 120.1 | 6287 | 686 | 9 | 95 | 63 | 37 | 6 | 23 |
| 357 | Information Era | 438 | 282.5 | 85.7 | 2188 | 121.8 | 6427 | 735 | 9 | 96 | 64 | 37 | 6 | 23 |
| 360 | Information Era | 441 | 288.6 | 89.8 | 2092 | 119.8 | 6511 | 727 | 9 | 97 | 65 | 38 | 7 | 24 |
| 367 | Information Era | 445 | 225.4 | 90.4 | 2770 | 99.7 | 6707 | 783 | 9 | 99 | 65 | 38 | 7 | 24 |
| 370 | Information Era | 445 | 222.1 | 90.4 | 3074 | 100.4 | 6797 | 809 | 9 | 99 | 66 | 38 | 7 | 24 |
| 374 | Information Era | 448 | 221.8 | 93.5 | 3457 | 102.3 | 6919 | 841 | 9 | 100 | 67 | 38 | 7 | 24 |
| 378 | Information Era | 451 | 216.2 | 98.5 | 3868 | 117.5 | 7043 | 875 | 9 | 101 | 67 | 39 | 7 | 24 |
| 379 | Information Era | 456 | 225.9 | 83.0 | 4011 | 162.3 | 7075 | 887 | 9 | 101 | 68 | 39 | 7 | 24 |
| 380 | Information Era | 458 | 225.9 | 83.0 | 4173 | 154.5 | 7107 | 900 | 9 | 101 | 68 | 39 | 7 | 24 |
| 396 | Information Era | 467 | 239.3 | 78.8 | 5704 | 136.9 | 7611 | 1073 | 9 | 105 | 68 | 39 | 7 | 23 |

---

## 2. RIVAL TIMELINES

### Sumeria — Gilgamesh (player 3)

First observed T99, last observed T396, 196 observations.

| Turn | Score | Mil | Techs | Civics | Tourism | Cities | Govt | At war with |
|---|---|---|---|---|---|---|---|---|
| 99 | 123 | 151 | 18 | 11 | 4 | 5 | Autocracy | - |
| 100 | 128 | 144 | 19 | 11 | 4 | 5 | Autocracy | - |
| 101 | 130 | 136 | 19 | 11 | 4 | 5 | Autocracy | - |
| 102 | 130 | 132 | 19 | 11 | 4 | 5 | Autocracy | - |
| 103 | 130 | 133 | 19 | 11 | 4 | 5 | Autocracy | - |
| 104 | 132 | 129 | 20 | 11 | 4 | 5 | Autocracy | - |
| 105 | 132 | 131 | 20 | 11 | 4 | 5 | Autocracy | - |
| 106 | 134 | 146 | 20 | 12 | 4 | 5 | Autocracy | - |
| 107 | 134 | 156 | 20 | 12 | 4 | 5 | Autocracy | - |
| 108 | 140 | 159 | 20 | 12 | 4 | 6 | Autocracy | - |
| 109 | 140 | 155 | 20 | 12 | 4 | 6 | Autocracy | - |
| 110 | 142 | 162 | 21 | 12 | 4 | 6 | Autocracy | - |
| 111 | 143 | 167 | 21 | 12 | 4 | 6 | Autocracy | - |
| 112 | 145 | 167 | 22 | 12 | 4 | 6 | Autocracy | - |
| 114 | 145 | 171 | 22 | 12 | 4 | 6 | Autocracy | - |
| 115 | 147 | 171 | 23 | 12 | 4 | 6 | Autocracy | - |
| 116 | 148 | 172 | 23 | 12 | 4 | 6 | Autocracy | - |
| 117 | 151 | 172 | 23 | 12 | 4 | 6 | Autocracy | - |
| 118 | 151 | 172 | 23 | 12 | 4 | 6 | Autocracy | - |
| 119 | 151 | 172 | 23 | 12 | 4 | 6 | Autocracy | - |
| 120 | 157 | 166 | 23 | 13 | 4 | 6 | Autocracy | - |
| 121 | 161 | 159 | 24 | 14 | 4 | 6 | Autocracy | - |
| 122 | 162 | 147 | 24 | 14 | 4 | 6 | Autocracy | - |
| 123 | 162 | 147 | 24 | 14 | 4 | 6 | Autocracy | - |
| 124 | 162 | 153 | 24 | 14 | 4 | 6 | Autocracy | - |
| 125 | 165 | 159 | 24 | 14 | 4 | 6 | Autocracy | - |
| 128 | 166 | 172 | 24 | 14 | 4 | 6 | Autocracy | - |
| 129 | 171 | 172 | 24 | 14 | 7 | 6 | Autocracy | - |
| 130 | 171 | 172 | 24 | 14 | 7 | 6 | Autocracy | - |
| 131 | 171 | 160 | 24 | 14 | 7 | 6 | Autocracy | - |
| 132 | 173 | 160 | 25 | 14 | 9 | 6 | Autocracy | - |
| 133 | 175 | 166 | 25 | 15 | 9 | 6 | Autocracy | - |
| 134 | 175 | 137 | 25 | 15 | 9 | 6 | Autocracy | - |
| 135 | 176 | 137 | 25 | 15 | 9 | 6 | Autocracy | - |
| 136 | 180 | 129 | 26 | 16 | 9 | 6 | Classical Republic | - |
| 137 | 180 | 130 | 26 | 16 | 9 | 6 | Classical Republic | - |
| 138 | 180 | 130 | 26 | 16 | 9 | 6 | Classical Republic | - |
| 139 | 182 | 131 | 27 | 16 | 9 | 6 | Classical Republic | - |
| 140 | 182 | 135 | 27 | 16 | 9 | 6 | Classical Republic | - |
| 141 | 182 | 136 | 27 | 16 | 9 | 6 | Classical Republic | - |
| 142 | 182 | 146 | 27 | 16 | 9 | 6 | Classical Republic | - |
| 143 | 182 | 147 | 27 | 16 | 9 | 6 | Classical Republic | - |
| 144 | 186 | 147 | 27 | 16 | 9 | 6 | Classical Republic | - |
| 145 | 187 | 148 | 27 | 16 | 9 | 6 | Classical Republic | - |
| 146 | 187 | 148 | 27 | 16 | 9 | 6 | Classical Republic | - |
| 147 | 187 | 149 | 27 | 16 | 9 | 6 | Classical Republic | - |
| 148 | 187 | 149 | 27 | 16 | 9 | 6 | Classical Republic | - |
| 149 | 187 | 150 | 27 | 16 | 9 | 6 | Classical Republic | - |
| 150 | 189 | 150 | 28 | 16 | 9 | 6 | Classical Republic | - |
| 151 | 192 | 151 | 29 | 16 | 9 | 6 | Classical Republic | - |
| 152 | 194 | 154 | 29 | 17 | 9 | 6 | Classical Republic | - |
| 153 | 197 | 145 | 29 | 17 | 9 | 6 | Classical Republic | - |
| 154 | 197 | 136 | 29 | 17 | 9 | 6 | Classical Republic | - |
| 155 | 198 | 137 | 29 | 17 | 9 | 6 | Classical Republic | - |
| 156 | 200 | 199 | 30 | 17 | 9 | 6 | Classical Republic | - |
| 157 | 200 | 196 | 30 | 17 | 9 | 6 | Classical Republic | - |
| 158 | 200 | 196 | 30 | 17 | 9 | 6 | Classical Republic | - |
| 159 | 200 | 171 | 30 | 17 | 9 | 6 | Classical Republic | - |
| 160 | 201 | 154 | 30 | 17 | 9 | 6 | Classical Republic | - |
| 161 | 200 | 153 | 30 | 17 | 9 | 6 | Classical Republic | - |
| 162 | 201 | 163 | 30 | 17 | 9 | 6 | Classical Republic | - |
| 163 | 201 | 173 | 30 | 17 | 9 | 6 | Classical Republic | - |
| 164 | 204 | 172 | 30 | 17 | 9 | 6 | Classical Republic | - |
| 165 | 208 | 172 | 31 | 18 | 9 | 6 | Classical Republic | - |
| 166 | 211 | 211 | 31 | 18 | 9 | 6 | Classical Republic | - |
| 167 | 211 | 211 | 31 | 18 | 9 | 6 | Classical Republic | - |
| 168 | 213 | 210 | 32 | 18 | 11 | 6 | Classical Republic | - |
| 169 | 213 | 210 | 32 | 18 | 11 | 6 | Classical Republic | - |
| 170 | 213 | 194 | 32 | 18 | 11 | 6 | Classical Republic | - |
| 171 | 213 | 193 | 32 | 18 | 11 | 6 | Classical Republic | - |
| 172 | 213 | 193 | 32 | 18 | 11 | 6 | Classical Republic | - |
| 173 | 216 | 198 | 32 | 18 | 11 | 6 | Classical Republic | - |
| 174 | 216 | 198 | 32 | 18 | 11 | 6 | Classical Republic | - |
| 175 | 220 | 197 | 33 | 19 | 11 | 6 | Classical Republic | - |
| 176 | 220 | 197 | 33 | 19 | 11 | 6 | Classical Republic | - |
| 177 | 220 | 204 | 33 | 19 | 11 | 6 | Classical Republic | - |
| 178 | 220 | 188 | 33 | 19 | 11 | 6 | Classical Republic | - |
| 179 | 226 | 151 | 33 | 19 | 11 | 7 | Classical Republic | - |
| 180 | 226 | 151 | 33 | 19 | 11 | 7 | Classical Republic | - |
| 181 | 226 | 151 | 33 | 19 | 11 | 7 | Classical Republic | - |
| 182 | 226 | 150 | 33 | 19 | 11 | 7 | Classical Republic | - |
| 184 | 229 | 154 | 34 | 19 | 11 | 7 | Classical Republic | - |
| 186 | 233 | 154 | 34 | 19 | 11 | 7 | Classical Republic | - |
| 188 | 235 | 138 | 35 | 19 | 11 | 7 | Classical Republic | - |
| 190 | 235 | 125 | 35 | 19 | 11 | 7 | Classical Republic | - |
| 191 | 235 | 137 | 35 | 19 | 11 | 7 | Classical Republic | - |
| 192 | 235 | 126 | 35 | 19 | 11 | 7 | Classical Republic | - |
| 193 | 237 | 191 | 35 | 20 | 11 | 7 | Classical Republic | - |
| 194 | 240 | 188 | 36 | 20 | 11 | 7 | Classical Republic | - |
| 195 | 243 | 182 | 36 | 20 | 11 | 7 | Classical Republic | - |
| 197 | 245 | 223 | 36 | 20 | 11 | 7 | Classical Republic | - |
| 198 | 245 | 223 | 36 | 20 | 11 | 7 | Classical Republic | - |
| 199 | 248 | 224 | 36 | 20 | 11 | 7 | Classical Republic | - |
| 201 | 250 | 224 | 37 | 20 | 13 | 7 | Classical Republic | - |
| 203 | 252 | 224 | 38 | 20 | 13 | 7 | Classical Republic | - |
| 204 | 254 | 224 | 38 | 21 | 13 | 7 | Classical Republic | - |
| 205 | 254 | 224 | 38 | 21 | 13 | 7 | Classical Republic | - |
| 206 | 254 | 223 | 38 | 21 | 13 | 7 | Classical Republic | - |
| 207 | 254 | 222 | 38 | 21 | 13 | 7 | Classical Republic | - |
| 208 | 254 | 221 | 38 | 21 | 13 | 7 | Classical Republic | - |
| 211 | 255 | 218 | 38 | 21 | 13 | 7 | Classical Republic | - |
| 212 | 259 | 247 | 38 | 21 | 13 | 7 | Classical Republic | - |
| 213 | 259 | 196 | 38 | 21 | 13 | 7 | Classical Republic | - |
| 214 | 259 | 195 | 38 | 21 | 13 | 7 | Classical Republic | - |
| 215 | 267 | 195 | 39 | 21 | 13 | 8 | Classical Republic | - |
| 216 | 269 | 195 | 40 | 21 | 21 | 8 | Classical Republic | - |
| 220 | 275 | 74 | 41 | 21 | 21 | 8 | Classical Republic | - |
| 221 | 277 | 2 | 42 | 21 | 21 | 8 | Classical Republic | - |
| 222 | 277 | 0 | 42 | 21 | 21 | 8 | Classical Republic | - |
| 223 | 276 | 0 | 42 | 21 | 21 | 8 | Classical Republic | - |
| 226 | 281 | 1 | 43 | 22 | 21 | 8 | Classical Republic | - |
| 229 | 281 | 3 | 43 | 22 | 21 | 8 | Classical Republic | - |
| 230 | 281 | 4 | 43 | 22 | 21 | 8 | Classical Republic | - |
| 233 | 285 | 6 | 44 | 22 | 31 | 8 | Classical Republic | - |
| 236 | 289 | 8 | 45 | 22 | 31 | 8 | Classical Republic | - |
| 237 | 289 | 8 | 45 | 22 | 30 | 8 | Classical Republic | - |
| 238 | 289 | 9 | 45 | 22 | 30 | 8 | Classical Republic | - |
| 239 | 289 | 10 | 45 | 22 | 30 | 8 | Classical Republic | - |
| 240 | 289 | 10 | 45 | 22 | 30 | 8 | Classical Republic | - |
| 242 | 293 | 12 | 46 | 22 | 30 | 8 | Classical Republic | - |
| 243 | 293 | 12 | 46 | 22 | 30 | 8 | Classical Republic | - |
| 244 | 293 | 13 | 46 | 22 | 31 | 8 | Classical Republic | - |
| 246 | 295 | 16 | 47 | 22 | 31 | 8 | Classical Republic | - |
| 248 | 303 | 21 | 47 | 23 | 31 | 9 | Classical Republic | - |
| 250 | 305 | 25 | 48 | 23 | 66 | 9 | Classical Republic | - |
| 253 | 306 | 31 | 48 | 23 | 68 | 9 | Classical Republic | - |
| 254 | 306 | 33 | 48 | 23 | 68 | 9 | Classical Republic | - |
| 256 | 307 | 37 | 48 | 23 | 68 | 9 | Classical Republic | - |
| 257 | 307 | 39 | 48 | 23 | 68 | 9 | Classical Republic | - |
| 259 | 310 | 43 | 49 | 23 | 68 | 9 | Classical Republic | - |
| 260 | 310 | 45 | 49 | 23 | 68 | 9 | Classical Republic | - |
| 261 | 312 | 13 | 49 | 23 | 68 | 9 | Classical Republic | - |
| 262 | 312 | 16 | 49 | 23 | 68 | 9 | Classical Republic | - |
| 263 | 315 | 77 | 49 | 23 | 68 | 9 | Classical Republic | - |
| 265 | 316 | 80 | 49 | 23 | 68 | 9 | Classical Republic | - |
| 268 | 320 | 84 | 50 | 24 | 70 | 9 | Classical Republic | - |
| 269 | 320 | 86 | 50 | 24 | 70 | 9 | Classical Republic | - |
| 270 | 321 | 87 | 50 | 24 | 70 | 9 | Classical Republic | - |
| 271 | 321 | 88 | 50 | 24 | 70 | 9 | Classical Republic | - |
| 273 | 321 | 87 | 50 | 24 | 70 | 9 | Classical Republic | - |
| 276 | 325 | 91 | 51 | 25 | 70 | 9 | Classical Republic | - |
| 277 | 325 | 92 | 51 | 25 | 70 | 9 | Classical Republic | - |
| 278 | 325 | 93 | 51 | 25 | 70 | 9 | Classical Republic | - |
| 279 | 324 | 94 | 51 | 25 | 70 | 9 | Classical Republic | - |
| 280 | 327 | 78 | 51 | 25 | 70 | 9 | Classical Republic | - |
| 284 | 330 | 82 | 51 | 25 | 70 | 9 | Classical Republic | - |
| 285 | 332 | 83 | 52 | 25 | 70 | 9 | Classical Republic | - |
| 286 | 332 | 83 | 52 | 25 | 70 | 9 | Classical Republic | - |
| 288 | 332 | 85 | 52 | 25 | 70 | 9 | Classical Republic | - |
| 292 | 332 | 167 | 52 | 25 | 70 | 9 | Classical Republic | - |
| 293 | 337 | 167 | 52 | 26 | 100 | 9 | Classical Republic | - |
| 294 | 339 | 167 | 53 | 26 | 104 | 9 | Classical Republic | - |
| 298 | 345 | 168 | 53 | 26 | 104 | 10 | Classical Republic | - |
| 299 | 345 | 168 | 53 | 26 | 104 | 10 | Classical Republic | - |
| 300 | 347 | 168 | 54 | 26 | 104 | 10 | Classical Republic | - |
| 301 | 347 | 168 | 54 | 26 | 104 | 10 | Classical Republic | - |
| 302 | 347 | 168 | 54 | 26 | 104 | 10 | Classical Republic | - |
| 303 | 348 | 168 | 54 | 26 | 104 | 10 | Classical Republic | - |
| 304 | 349 | 168 | 54 | 26 | 104 | 10 | Classical Republic | - |
| 305 | 349 | 167 | 54 | 26 | 104 | 10 | Classical Republic | - |
| 307 | 352 | 165 | 54 | 26 | 104 | 10 | Classical Republic | - |
| 308 | 352 | 164 | 54 | 26 | 104 | 10 | Classical Republic | - |
| 310 | 352 | 162 | 54 | 26 | 104 | 10 | Classical Republic | - |
| 311 | 354 | 161 | 54 | 27 | 124 | 10 | Classical Republic | - |
| 312 | 354 | 160 | 54 | 27 | 124 | 10 | Classical Republic | - |
| 313 | 356 | 160 | 55 | 27 | 124 | 10 | Classical Republic | - |
| 314 | 356 | 239 | 55 | 27 | 124 | 10 | Classical Republic | - |
| 316 | 357 | 236 | 55 | 27 | 124 | 10 | Classical Republic | - |
| 317 | 356 | 235 | 55 | 27 | 124 | 10 | Classical Republic | - |
| 318 | 359 | 234 | 55 | 27 | 124 | 10 | Classical Republic | - |
| 319 | 362 | 232 | 56 | 27 | 128 | 10 | Classical Republic | - |
| 322 | 364 | 140 | 56 | 27 | 128 | 10 | Classical Republic | - |
| 323 | 364 | 63 | 56 | 27 | 130 | 10 | Classical Republic | - |
| 324 | 373 | 63 | 56 | 27 | 130 | 11 | Classical Republic | - |
| 325 | 373 | 63 | 56 | 27 | 130 | 11 | Classical Republic | - |
| 326 | 373 | 63 | 56 | 27 | 130 | 11 | Classical Republic | - |
| 327 | 375 | 64 | 57 | 27 | 130 | 11 | Classical Republic | - |
| 328 | 378 | 64 | 57 | 27 | 130 | 11 | Classical Republic | - |
| 329 | 378 | 64 | 57 | 27 | 130 | 11 | Classical Republic | - |
| 335 | 384 | 67 | 58 | 27 | 130 | 11 | Classical Republic | - |
| 338 | 388 | 68 | 59 | 28 | 138 | 11 | Classical Republic | - |
| 339 | 392 | 69 | 59 | 28 | 138 | 11 | Classical Republic | - |
| 342 | 394 | 71 | 60 | 28 | 138 | 11 | Classical Republic | - |
| 345 | 396 | 74 | 61 | 28 | 138 | 11 | Classical Republic | - |
| 349 | 400 | 77 | 62 | 29 | 140 | 11 | Classical Republic | - |
| 351 | 401 | 79 | 62 | 29 | 140 | 11 | Classical Republic | - |
| 352 | 402 | 79 | 62 | 29 | 140 | 11 | Classical Republic | - |
| 357 | 411 | 261 | 63 | 29 | 140 | 12 | Classical Republic | - |
| 360 | 419 | 214 | 64 | 30 | 132 | 12 | Classical Republic | - |
| 367 | 427 | 252 | 65 | 31 | 132 | 12 | Classical Republic | - |
| 370 | 428 | 248 | 65 | 31 | 132 | 12 | Classical Republic | - |
| 374 | 431 | 172 | 66 | 31 | 132 | 12 | Classical Republic | - |
| 378 | 438 | 60 | 66 | 32 | 130 | 12 | Classical Republic | - |
| 379 | 437 | 60 | 66 | 32 | 130 | 12 | Classical Republic | - |
| 380 | 439 | 60 | 67 | 32 | 130 | 12 | Classical Republic | - |
| 396 | 454 | 2 | 68 | 34 | 132 | 12 | Classical Republic | - |

### Brazil — ? (player 4)

First observed T99, last observed T396, 196 observations. **Recorded as no longer alive from T99.**

*No observations while alive — this civ was already gone by the time the archive starts. See the chronology for how they fell.*

### Aztec — Montezuma (player 5)

First observed T161, last observed T396, 137 observations.

| Turn | Score | Mil | Techs | Civics | Tourism | Cities | Govt | At war with |
|---|---|---|---|---|---|---|---|---|
| 161 | 164 | 105 | 21 | 16 | 8 | 1 | ? | - |
| 162 | 170 | 103 | 21 | 16 | 8 | 1 | ? | - |
| 163 | 170 | 105 | 21 | 16 | 16 | 1 | ? | - |
| 164 | 172 | 105 | 22 | 16 | 16 | 1 | ? | - |
| 165 | 172 | 105 | 22 | 16 | 16 | 1 | ? | - |
| 166 | 177 | 106 | 22 | 16 | 16 | 1 | ? | - |
| 167 | 177 | 106 | 22 | 16 | 16 | 1 | ? | - |
| 168 | 177 | 107 | 22 | 16 | 16 | 1 | ? | - |
| 169 | 179 | 108 | 22 | 16 | 16 | 1 | ? | - |
| 170 | 182 | 108 | 22 | 16 | 16 | 1 | ? | - |
| 171 | 182 | 111 | 22 | 16 | 16 | 1 | ? | - |
| 172 | 182 | 111 | 22 | 16 | 16 | 1 | Autocracy | - |
| 173 | 186 | 115 | 23 | 17 | 16 | 1 | Classical Republic | - |
| 174 | 186 | 116 | 23 | 17 | 16 | 1 | Classical Republic | - |
| 175 | 186 | 119 | 23 | 17 | 16 | 1 | Classical Republic | - |
| 176 | 187 | 119 | 23 | 17 | 16 | 1 | Classical Republic | - |
| 177 | 187 | 119 | 23 | 17 | 16 | 1 | Classical Republic | - |
| 178 | 192 | 136 | 24 | 17 | 16 | 1 | Classical Republic | - |
| 179 | 193 | 125 | 24 | 17 | 16 | 1 | Classical Republic | - |
| 180 | 193 | 125 | 24 | 17 | 16 | 1 | Classical Republic | - |
| 181 | 194 | 128 | 24 | 17 | 16 | 1 | Classical Republic | - |
| 182 | 194 | 130 | 24 | 17 | 16 | 1 | Classical Republic | - |
| 184 | 195 | 133 | 24 | 17 | 16 | 1 | Classical Republic | - |
| 186 | 200 | 133 | 24 | 17 | 16 | 1 | Classical Republic | - |
| 188 | 201 | 138 | 24 | 18 | 16 | 1 | Classical Republic | - |
| 190 | 203 | 104 | 25 | 18 | 16 | 1 | Classical Republic | - |
| 191 | 203 | 108 | 25 | 18 | 16 | 1 | Classical Republic | - |
| 192 | 203 | 110 | 25 | 18 | 16 | 1 | Classical Republic | - |
| 193 | 203 | 119 | 25 | 18 | 16 | 1 | Classical Republic | - |
| 194 | 204 | 121 | 25 | 18 | 16 | 1 | Classical Republic | - |
| 195 | 204 | 117 | 25 | 18 | 16 | 1 | Classical Republic | - |
| 197 | 209 | 129 | 26 | 18 | 16 | 1 | Classical Republic | - |
| 198 | 217 | 131 | 27 | 18 | 16 | 1 | Classical Republic | - |
| 199 | 217 | 126 | 27 | 18 | 16 | 1 | Classical Republic | - |
| 201 | 224 | 131 | 28 | 19 | 16 | 1 | Classical Republic | - |
| 203 | 229 | 128 | 29 | 19 | 16 | 1 | Classical Republic | - |
| 204 | 231 | 130 | 30 | 19 | 16 | 1 | Classical Republic | - |
| 205 | 235 | 132 | 30 | 19 | 16 | 1 | Classical Republic | - |
| 206 | 238 | 178 | 31 | 19 | 16 | 1 | Classical Republic | - |
| 207 | 238 | 180 | 31 | 19 | 16 | 1 | Classical Republic | - |
| 208 | 238 | 188 | 31 | 19 | 16 | 1 | Classical Republic | - |
| 211 | 243 | 189 | 32 | 19 | 16 | 1 | Classical Republic | - |
| 212 | 243 | 197 | 32 | 19 | 16 | 1 | Classical Republic | - |
| 213 | 245 | 191 | 32 | 20 | 16 | 1 | Classical Republic | - |
| 214 | 246 | 192 | 32 | 20 | 16 | 1 | Classical Republic | - |
| 215 | 246 | 193 | 32 | 20 | 16 | 1 | Classical Republic | - |
| 216 | 247 | 179 | 32 | 20 | 16 | 1 | Classical Republic | - |
| 220 | 252 | 183 | 33 | 21 | 16 | 1 | Classical Republic | - |
| 221 | 252 | 183 | 33 | 21 | 16 | 1 | Classical Republic | - |
| 222 | 253 | 184 | 33 | 21 | 16 | 1 | Classical Republic | - |
| 223 | 255 | 185 | 34 | 21 | 16 | 1 | Classical Republic | - |
| 226 | 256 | 191 | 34 | 21 | 16 | 1 | Classical Republic | - |
| 229 | 258 | 194 | 34 | 21 | 16 | 1 | Classical Republic | - |
| 230 | 260 | 195 | 35 | 21 | 16 | 1 | Classical Republic | - |
| 233 | 267 | 195 | 35 | 21 | 16 | 1 | Classical Republic | - |
| 236 | 269 | 195 | 35 | 22 | 16 | 1 | Classical Republic | - |
| 237 | 271 | 195 | 36 | 22 | 16 | 1 | Classical Republic | - |
| 238 | 271 | 194 | 36 | 22 | 16 | 1 | Classical Republic | - |
| 239 | 271 | 194 | 36 | 22 | 16 | 1 | Classical Republic | - |
| 240 | 273 | 194 | 36 | 22 | 16 | 1 | Classical Republic | - |
| 242 | 278 | 193 | 37 | 22 | 16 | 1 | Classical Republic | - |
| 243 | 278 | 192 | 37 | 22 | 16 | 1 | Classical Republic | - |
| 244 | 278 | 192 | 37 | 22 | 16 | 7 | Classical Republic | - |
| 246 | 278 | 191 | 37 | 22 | 16 | 7 | Classical Republic | - |
| 248 | 281 | 191 | 38 | 22 | 16 | 7 | Classical Republic | - |
| 250 | 284 | 190 | 38 | 23 | 16 | 7 | Classical Republic | - |
| 253 | 284 | 193 | 38 | 23 | 16 | 7 | Classical Republic | - |
| 254 | 284 | 195 | 38 | 23 | 16 | 7 | Classical Republic | - |
| 256 | 286 | 198 | 39 | 23 | 16 | 7 | Classical Republic | - |
| 257 | 292 | 200 | 39 | 23 | 16 | 8 | Classical Republic | - |
| 259 | 301 | 202 | 39 | 24 | 16 | 8 | Classical Republic | - |
| 260 | 301 | 202 | 39 | 24 | 16 | 8 | Classical Republic | - |
| 261 | 301 | 203 | 39 | 24 | 16 | 8 | Classical Republic | - |
| 262 | 302 | 203 | 39 | 24 | 16 | 8 | Classical Republic | - |
| 263 | 304 | 203 | 39 | 25 | 16 | 8 | Classical Republic | - |
| 265 | 306 | 203 | 40 | 25 | 16 | 8 | Classical Republic | - |
| 268 | 307 | 168 | 40 | 25 | 16 | 8 | Classical Republic | - |
| 269 | 308 | 168 | 40 | 25 | 16 | 8 | Classical Republic | - |
| 270 | 309 | 169 | 40 | 25 | 16 | 8 | Classical Republic | - |
| 271 | 312 | 169 | 40 | 25 | 16 | 8 | Classical Republic | - |
| 273 | 313 | 170 | 40 | 25 | 16 | 8 | Classical Republic | - |
| 276 | 316 | 211 | 41 | 25 | 32 | 8 | Classical Republic | - |
| 277 | 318 | 170 | 41 | 26 | 32 | 8 | Classical Republic | - |
| 278 | 318 | 213 | 41 | 26 | 32 | 8 | Classical Republic | - |
| 279 | 318 | 289 | 41 | 26 | 32 | 8 | Classical Republic | - |
| 280 | 319 | 255 | 41 | 26 | 32 | 8 | Classical Republic | - |
| 284 | 321 | 293 | 42 | 26 | 42 | 8 | Classical Republic | - |
| 285 | 321 | 290 | 42 | 26 | 42 | 8 | Classical Republic | - |
| 286 | 321 | 264 | 42 | 26 | 42 | 8 | Classical Republic | - |
| 288 | 322 | 303 | 42 | 26 | 42 | 8 | Classical Republic | - |
| 292 | 324 | 301 | 43 | 26 | 42 | 8 | Classical Republic | - |
| 293 | 330 | 267 | 43 | 26 | 54 | 8 | Classical Republic | - |
| 294 | 330 | 271 | 43 | 26 | 54 | 8 | Classical Republic | - |
| 298 | 332 | 350 | 43 | 27 | 82 | 8 | Classical Republic | - |
| 299 | 338 | 381 | 43 | 27 | 92 | 8 | Classical Republic | - |
| 300 | 338 | 381 | 43 | 27 | 92 | 8 | Classical Republic | - |
| 301 | 339 | 380 | 43 | 27 | 92 | 8 | Classical Republic | - |
| 302 | 339 | 390 | 43 | 27 | 92 | 8 | Classical Republic | - |
| 303 | 342 | 389 | 43 | 27 | 92 | 8 | Classical Republic | - |
| 304 | 348 | 388 | 43 | 27 | 92 | 9 | Classical Republic | - |
| 305 | 349 | 388 | 43 | 27 | 92 | 9 | Classical Republic | - |
| 307 | 350 | 377 | 43 | 27 | 92 | 9 | Classical Republic | - |
| 308 | 350 | 376 | 43 | 27 | 92 | 9 | Classical Republic | - |
| 310 | 352 | 376 | 43 | 27 | 92 | 9 | Classical Republic | - |
| 311 | 353 | 375 | 43 | 27 | 92 | 9 | Classical Republic | - |
| 312 | 354 | 195 | 43 | 27 | 92 | 9 | Classical Republic | - |
| 313 | 356 | 215 | 44 | 27 | 100 | 9 | Classical Republic | - |
| 314 | 359 | 184 | 44 | 27 | 100 | 9 | Classical Republic | - |
| 316 | 359 | 184 | 44 | 27 | 100 | 9 | Classical Republic | - |
| 317 | 359 | 185 | 44 | 27 | 100 | 9 | Classical Republic | - |
| 318 | 359 | 185 | 44 | 27 | 100 | 9 | Classical Republic | - |
| 319 | 360 | 186 | 44 | 27 | 100 | 9 | Classical Republic | - |
| 322 | 363 | 188 | 44 | 28 | 112 | 9 | Classical Republic | - |
| 323 | 365 | 190 | 44 | 29 | 112 | 9 | Monarchy | - |
| 324 | 370 | 192 | 45 | 29 | 116 | 9 | Monarchy | - |
| 325 | 376 | 193 | 46 | 29 | 132 | 9 | Monarchy | - |
| 326 | 378 | 195 | 46 | 30 | 128 | 9 | Monarchy | - |
| 327 | 378 | 197 | 46 | 30 | 136 | 9 | Monarchy | - |
| 328 | 378 | 199 | 46 | 30 | 136 | 9 | Monarchy | - |
| 329 | 379 | 201 | 46 | 30 | 128 | 9 | Monarchy | - |
| 335 | 383 | 320 | 48 | 30 | 136 | 9 | Monarchy | - |
| 338 | 385 | 324 | 49 | 30 | 144 | 9 | Monarchy | - |
| 339 | 386 | 325 | 49 | 30 | 144 | 9 | Monarchy | - |
| 342 | 390 | 305 | 50 | 31 | 144 | 9 | Monarchy | - |
| 345 | 392 | 286 | 51 | 31 | 144 | 9 | Monarchy | - |
| 349 | 396 | 290 | 52 | 32 | 150 | 9 | Monarchy | - |
| 351 | 400 | 291 | 53 | 32 | 150 | 9 | Monarchy | - |
| 352 | 400 | 292 | 53 | 32 | 150 | 9 | Monarchy | - |
| 357 | 409 | 319 | 55 | 32 | 150 | 10 | Monarchy | - |
| 360 | 415 | 279 | 55 | 32 | 150 | 10 | Monarchy | - |
| 367 | 425 | 233 | 57 | 33 | 150 | 10 | Monarchy | - |
| 370 | 425 | 236 | 57 | 33 | 150 | 10 | Monarchy | - |
| 374 | 436 | 242 | 59 | 34 | 150 | 10 | Monarchy | - |
| 378 | 438 | 247 | 60 | 34 | 150 | 10 | Monarchy | - |
| 379 | 439 | 247 | 60 | 34 | 150 | 10 | Monarchy | - |
| 380 | 439 | 228 | 60 | 34 | 150 | 10 | Monarchy | - |
| 396 | 456 | 227 | 64 | 35 | 148 | 10 | Democracy | - |

### England — Victoria (player 1)

First observed T242, last observed T396, 77 observations.

| Turn | Score | Mil | Techs | Civics | Tourism | Cities | Govt | At war with |
|---|---|---|---|---|---|---|---|---|
| 242 | 284 | 176 | 27 | 27 | 56 | 1 | Merchant Republic | - |
| 243 | 284 | 178 | 27 | 27 | 56 | 1 | Merchant Republic | - |
| 244 | 285 | 184 | 27 | 27 | 56 | 7 | Merchant Republic | - |
| 246 | 287 | 195 | 28 | 27 | 56 | 7 | Merchant Republic | - |
| 248 | 287 | 205 | 28 | 27 | 56 | 7 | Merchant Republic | - |
| 250 | 289 | 184 | 29 | 27 | 56 | 7 | Merchant Republic | - |
| 253 | 297 | 188 | 29 | 27 | 56 | 8 | Merchant Republic | - |
| 254 | 297 | 195 | 29 | 27 | 56 | 8 | Merchant Republic | - |
| 256 | 302 | 194 | 29 | 28 | 67 | 8 | Merchant Republic | - |
| 257 | 302 | 201 | 29 | 28 | 69 | 8 | Merchant Republic | - |
| 259 | 308 | 208 | 30 | 28 | 69 | 8 | Merchant Republic | - |
| 260 | 308 | 197 | 30 | 28 | 69 | 8 | Merchant Republic | - |
| 261 | 308 | 165 | 30 | 28 | 69 | 8 | Merchant Republic | - |
| 262 | 311 | 167 | 31 | 28 | 69 | 8 | Merchant Republic | - |
| 263 | 311 | 167 | 31 | 28 | 69 | 8 | Merchant Republic | - |
| 265 | 319 | 211 | 32 | 29 | 69 | 8 | Merchant Republic | - |
| 268 | 329 | 197 | 32 | 30 | 69 | 8 | Merchant Republic | - |
| 269 | 329 | 203 | 32 | 30 | 69 | 8 | Merchant Republic | - |
| 270 | 329 | 210 | 32 | 30 | 69 | 8 | Merchant Republic | - |
| 271 | 332 | 216 | 32 | 30 | 69 | 8 | Merchant Republic | - |
| 273 | 335 | 225 | 33 | 30 | 69 | 8 | Merchant Republic | - |
| 276 | 339 | 227 | 33 | 31 | 69 | 8 | Merchant Republic | - |
| 277 | 341 | 234 | 34 | 31 | 69 | 8 | Merchant Republic | - |
| 278 | 343 | 240 | 34 | 32 | 69 | 8 | Merchant Republic | - |
| 279 | 349 | 209 | 34 | 32 | 69 | 8 | Merchant Republic | - |
| 280 | 349 | 211 | 34 | 32 | 69 | 8 | Merchant Republic | - |
| 284 | 359 | 293 | 34 | 33 | 69 | 9 | Merchant Republic | - |
| 285 | 359 | 251 | 34 | 33 | 69 | 9 | Merchant Republic | - |
| 286 | 361 | 260 | 35 | 33 | 69 | 9 | Merchant Republic | - |
| 288 | 362 | 258 | 35 | 33 | 69 | 9 | Merchant Republic | - |
| 292 | 364 | 258 | 35 | 34 | 69 | 9 | Merchant Republic | - |
| 293 | 364 | 267 | 35 | 34 | 69 | 9 | Merchant Republic | - |
| 294 | 364 | 276 | 35 | 34 | 69 | 9 | Merchant Republic | - |
| 298 | 373 | 345 | 36 | 34 | 69 | 9 | Merchant Republic | - |
| 299 | 373 | 332 | 36 | 34 | 69 | 9 | Merchant Republic | - |
| 300 | 373 | 341 | 36 | 34 | 69 | 9 | Merchant Republic | - |
| 301 | 377 | 350 | 36 | 34 | 69 | 9 | Merchant Republic | - |
| 302 | 377 | 319 | 36 | 34 | 69 | 9 | Merchant Republic | - |
| 303 | 385 | 271 | 36 | 35 | 69 | 9 | Merchant Republic | - |
| 304 | 385 | 231 | 36 | 35 | 73 | 9 | Merchant Republic | - |
| 305 | 386 | 257 | 36 | 35 | 77 | 9 | Merchant Republic | - |
| 307 | 386 | 257 | 36 | 35 | 81 | 9 | Merchant Republic | - |
| 308 | 390 | 243 | 37 | 36 | 83 | 9 | Merchant Republic | - |
| 310 | 390 | 269 | 37 | 36 | 83 | 9 | Merchant Republic | - |
| 311 | 390 | 255 | 37 | 36 | 83 | 9 | Merchant Republic | - |
| 312 | 390 | 265 | 37 | 36 | 83 | 9 | Merchant Republic | - |
| 313 | 391 | 276 | 37 | 36 | 83 | 9 | Merchant Republic | - |
| 314 | 391 | 255 | 37 | 36 | 83 | 9 | Merchant Republic | - |
| 316 | 396 | 286 | 37 | 36 | 83 | 9 | Merchant Republic | - |
| 317 | 398 | 262 | 38 | 36 | 83 | 9 | Merchant Republic | - |
| 318 | 398 | 273 | 38 | 36 | 83 | 9 | Merchant Republic | - |
| 319 | 398 | 262 | 38 | 36 | 83 | 9 | Merchant Republic | - |
| 322 | 402 | 208 | 38 | 37 | 69 | 9 | Democracy | - |
| 323 | 402 | 160 | 38 | 37 | 69 | 9 | Democracy | - |
| 324 | 403 | 163 | 38 | 37 | 69 | 9 | Democracy | - |
| 325 | 404 | 122 | 38 | 37 | 69 | 9 | Democracy | - |
| 326 | 408 | 129 | 38 | 37 | 69 | 9 | Democracy | - |
| 327 | 412 | 118 | 38 | 37 | 77 | 9 | Democracy | - |
| 328 | 413 | 125 | 38 | 37 | 85 | 9 | Democracy | - |
| 329 | 415 | 147 | 39 | 37 | 85 | 9 | Democracy | - |
| 335 | 419 | 156 | 39 | 38 | 85 | 9 | Democracy | - |
| 338 | 432 | 179 | 41 | 38 | 89 | 9 | Democracy | - |
| 339 | 433 | 186 | 41 | 38 | 89 | 9 | Democracy | - |
| 342 | 438 | 159 | 42 | 38 | 101 | 9 | Democracy | - |
| 345 | 448 | 200 | 42 | 39 | 101 | 9 | Democracy | - |
| 349 | 457 | 250 | 43 | 39 | 202 | 9 | Democracy | - |
| 351 | 457 | 215 | 43 | 39 | 210 | 9 | Democracy | - |
| 352 | 461 | 224 | 43 | 39 | 210 | 9 | Democracy | - |
| 357 | 466 | 216 | 43 | 39 | 210 | 9 | Democracy | - |
| 360 | 470 | 181 | 43 | 40 | 242 | 9 | Democracy | - |
| 367 | 472 | 338 | 44 | 40 | 248 | 9 | Democracy | - |
| 370 | 475 | 266 | 44 | 40 | 256 | 9 | Democracy | - |
| 374 | 484 | 297 | 44 | 41 | 256 | 9 | Democracy | - |
| 378 | 489 | 383 | 45 | 41 | 256 | 9 | Democracy | - |
| 379 | 491 | 392 | 46 | 41 | 256 | 9 | Democracy | - |
| 380 | 492 | 342 | 46 | 41 | 256 | 9 | Democracy | - |
| 396 | 512 | 413 | 48 | 42 | 264 | 9 | Democracy | - |

### India — Gandhi (player 2)

First observed T244, last observed T396, 75 observations.

| Turn | Score | Mil | Techs | Civics | Tourism | Cities | Govt | At war with |
|---|---|---|---|---|---|---|---|---|
| 244 | 242 | 79 | 25 | 23 | 26 | 7 | Classical Republic | - |
| 246 | 244 | 79 | 26 | 23 | 26 | 7 | Classical Republic | - |
| 248 | 248 | 80 | 26 | 23 | 26 | 7 | Classical Republic | - |
| 250 | 254 | 80 | 26 | 24 | 32 | 7 | Classical Republic | - |
| 253 | 258 | 76 | 26 | 24 | 35 | 7 | Classical Republic | - |
| 254 | 258 | 75 | 26 | 24 | 36 | 7 | Classical Republic | - |
| 256 | 258 | 73 | 26 | 24 | 39 | 7 | Classical Republic | - |
| 257 | 259 | 74 | 26 | 24 | 39 | 7 | Classical Republic | - |
| 259 | 262 | 74 | 27 | 24 | 39 | 7 | Classical Republic | - |
| 260 | 262 | 75 | 27 | 24 | 39 | 7 | Classical Republic | - |
| 261 | 262 | 76 | 27 | 24 | 39 | 7 | Classical Republic | - |
| 262 | 265 | 77 | 27 | 25 | 39 | 7 | Classical Republic | - |
| 263 | 266 | 78 | 27 | 25 | 39 | 7 | Classical Republic | - |
| 265 | 266 | 81 | 27 | 25 | 39 | 7 | Classical Republic | - |
| 268 | 266 | 73 | 27 | 25 | 39 | 7 | Classical Republic | - |
| 269 | 266 | 74 | 27 | 25 | 39 | 7 | Classical Republic | - |
| 270 | 269 | 74 | 27 | 26 | 39 | 7 | Classical Republic | - |
| 271 | 271 | 77 | 28 | 26 | 43 | 7 | Classical Republic | - |
| 273 | 271 | 82 | 28 | 26 | 43 | 7 | Classical Republic | - |
| 276 | 275 | 89 | 28 | 26 | 43 | 7 | Classical Republic | - |
| 277 | 275 | 70 | 28 | 26 | 43 | 7 | Classical Republic | - |
| 278 | 277 | 73 | 28 | 27 | 43 | 7 | Classical Republic | - |
| 279 | 281 | 76 | 28 | 27 | 51 | 7 | Classical Republic | - |
| 280 | 281 | 78 | 28 | 27 | 59 | 7 | Classical Republic | - |
| 284 | 288 | 93 | 29 | 27 | 59 | 7 | Classical Republic | - |
| 285 | 288 | 96 | 29 | 27 | 59 | 7 | Classical Republic | - |
| 286 | 288 | 76 | 29 | 27 | 59 | 7 | Classical Republic | - |
| 288 | 290 | 76 | 29 | 27 | 59 | 7 | Classical Republic | - |
| 292 | 295 | 79 | 29 | 28 | 85 | 7 | Classical Republic | - |
| 293 | 296 | 80 | 29 | 28 | 85 | 7 | Classical Republic | - |
| 294 | 297 | 81 | 29 | 28 | 85 | 7 | Classical Republic | - |
| 298 | 299 | 85 | 29 | 28 | 85 | 7 | Classical Republic | - |
| 299 | 302 | 85 | 30 | 28 | 85 | 7 | Classical Republic | - |
| 300 | 303 | 86 | 30 | 28 | 85 | 7 | Classical Republic | - |
| 301 | 310 | 87 | 30 | 28 | 85 | 8 | Classical Republic | - |
| 302 | 310 | 133 | 30 | 28 | 85 | 8 | Classical Republic | - |
| 303 | 313 | 134 | 31 | 28 | 85 | 8 | Classical Republic | - |
| 304 | 313 | 135 | 31 | 28 | 85 | 8 | Classical Republic | - |
| 305 | 315 | 136 | 31 | 29 | 87 | 8 | Classical Republic | - |
| 307 | 315 | 140 | 31 | 29 | 90 | 8 | Classical Republic | - |
| 308 | 320 | 141 | 32 | 30 | 95 | 8 | Classical Republic | - |
| 310 | 321 | 145 | 32 | 30 | 95 | 8 | Classical Republic | - |
| 311 | 324 | 109 | 32 | 31 | 95 | 8 | Classical Republic | - |
| 312 | 324 | 109 | 32 | 31 | 95 | 8 | Classical Republic | - |
| 313 | 325 | 109 | 32 | 31 | 95 | 8 | Classical Republic | - |
| 314 | 327 | 109 | 33 | 31 | 95 | 8 | Classical Republic | - |
| 316 | 339 | 172 | 34 | 33 | 95 | 8 | Classical Republic | - |
| 317 | 339 | 174 | 34 | 33 | 95 | 8 | Classical Republic | - |
| 318 | 341 | 177 | 35 | 33 | 95 | 8 | Classical Republic | - |
| 319 | 341 | 179 | 35 | 33 | 95 | 8 | Classical Republic | - |
| 322 | 346 | 188 | 35 | 33 | 95 | 8 | Classical Republic | - |
| 323 | 346 | 191 | 35 | 33 | 96 | 8 | Classical Republic | - |
| 324 | 346 | 186 | 35 | 33 | 96 | 8 | Classical Republic | - |
| 325 | 348 | 189 | 35 | 34 | 96 | 8 | Classical Republic | - |
| 326 | 349 | 189 | 35 | 34 | 96 | 8 | Classical Republic | - |
| 327 | 350 | 190 | 35 | 34 | 96 | 8 | Classical Republic | - |
| 328 | 350 | 190 | 35 | 34 | 96 | 8 | Classical Republic | - |
| 329 | 351 | 191 | 35 | 34 | 96 | 8 | Classical Republic | - |
| 335 | 355 | 196 | 36 | 35 | 96 | 8 | Classical Republic | - |
| 338 | 358 | 210 | 37 | 35 | 96 | 8 | Classical Republic | - |
| 339 | 358 | 213 | 37 | 35 | 96 | 8 | Classical Republic | - |
| 342 | 367 | 222 | 37 | 36 | 96 | 8 | Classical Republic | - |
| 345 | 367 | 301 | 37 | 36 | 98 | 8 | Classical Republic | - |
| 349 | 370 | 262 | 38 | 36 | 98 | 8 | Classical Republic | - |
| 351 | 371 | 212 | 38 | 36 | 98 | 8 | Classical Republic | - |
| 352 | 373 | 214 | 38 | 37 | 98 | 8 | Democracy | - |
| 357 | 373 | 206 | 38 | 37 | 98 | 8 | Democracy | - |
| 360 | 378 | 208 | 39 | 37 | 98 | 8 | Democracy | - |
| 367 | 383 | 194 | 39 | 38 | 110 | 8 | Democracy | - |
| 370 | 389 | 206 | 39 | 38 | 117 | 8 | Democracy | - |
| 374 | 392 | 218 | 40 | 38 | 119 | 8 | Democracy | - |
| 378 | 395 | 225 | 40 | 39 | 128 | 8 | Democracy | - |
| 379 | 398 | 242 | 40 | 39 | 128 | 8 | Democracy | - |
| 380 | 397 | 245 | 40 | 39 | 134 | 8 | Democracy | - |
| 396 | 414 | 147 | 42 | 40 | 147 | 9 | Democracy | - |

### City-states

| City-state | Observations | Suzerain history |
|---|---|---|
| Kabul | 196 | T99:none → T143:SUMERIA → T160:none → T179:ME → T311:none → T312:ME |
| Hattusa | 196 | T99:none → T101:ME → T106:none → T131:ME |
| Stockholm | 196 | T99:none → T136:SUMERIA → T197:none → T199:ME → T276:none → T279:ME |
| Amsterdam | 196 | T99:none → T105:ME |
| Mohenjo-Daro | 75 | T244:ENGLAND → T270:none → T298:AZTEC → T308:INDIA → T326:none |
| Mogadishu | 75 | T244:ENGLAND → T305:INDIA |
| Kumasi | 75 | T244:ENGLAND → T248:none → T300:AZTEC → T313:none → T316:INDIA |
| Buenos Aires | 75 | T244:ENGLAND → T292:INDIA |
| Yerevan | 42 | T300:none → T374:ENGLAND → T378:none |


---

## 3. MASTER CHRONOLOGY

Gossip (the game's own dated record) merged with observed world events. This is the spine every conclusion should cite.

- **T52** `gossip` Rumor has it that Sumeria has just declared war on Brazil!
- **T53** `gossip` Rumor has it that Sumeria has conquered the original Brazilian capital of Rio de Janeiro.
- **T53** `gossip` Rumor has it that Sumeria has progressed from the Ancient Era to the Classical Era.
- **T59** `gossip` Rumor has it that Sumeria has conquered Adab.
- **T63** `gossip` Your delegate, Ahmes, learned that Sumeria has declared their friendship with Egypt.
- **T63** `gossip` Your delegate, Ahmes, learned that Sumeria has just received a foreign delegation. It appears they came from Egypt.
- **T63** `gossip` Your delegate, Ahmes, learned that Sumeria has switched governments to Autocracy.
- **T67** `gossip` Your delegate, Ahmes, learned that Sumeria is worshipping a Pantheon of the gods focused on the Dance of the Aurora Belief.
- **T70** `gossip` Your delegate, Ahmes, learned that Sumeria has used a War-Cart to clear a Barbarian Outpost.
- **T80** `gossip` Your delegate, Ahmes, learned that Sumeria has progressed from the Classical Era to the Medieval Era.
- **T81** `gossip` Your delegate, Ahmes, learned that Sumeria is expanding, adding the new settlement: Adab.
- **T88** `gossip` Rumor has it that Brazil has been targeted for a declaration of war by Sumeria!
- **T88** `gossip` Your delegate, Ahmes, learned that Sumeria has just declared war on Brazil!
- **T88** `gossip` Your delegate, Ahmes, learned that Sumeria is trading with Brazil.
- **T90** `gossip` Your delegate, Ahmes, learned that Sumeria has conquered Recife.
- **T90** `gossip` Your delegate, Ahmes, learned that Sumeria is expanding, adding the new settlement: Recife.
- **T94** `gossip` Your delegate, Ahmes, learned that Sumeria has declared their friendship with Egypt.
- **T98** `gossip` Your delegate, Ahmes, learned that Sumeria has used a War-Cart to clear a Barbarian Outpost.
- **T101** `event` suzerain of Hattusa: none -> ME
- **T105** `event` suzerain of Amsterdam: none -> ME
- **T106** `event` suzerain of Hattusa: ME -> none
- **T107** `gossip` Your delegate, Ahmes, learned that Sumeria is expanding, adding the new settlement: Kish.
- **T120** `event` player 2 founded Hinduism
- **T125** `gossip` Your delegate, Ahmes, learned that Sumeria has declared their friendship with Egypt.
- **T131** `event` suzerain of Hattusa: none -> ME
- **T131** `gossip` Your delegate, Ahmes, learned that Sumeria has progressed from the Medieval Era to the Renaissance Era.
- **T135** `gossip` Your delegate, Ahmes, learned that Sumeria has switched governments to Classical Republic.
- **T136** `event` Sumeria government Autocracy -> Classical Republic
- **T136** `event` suzerain of Stockholm: none -> SUMERIA
- **T143** `event` player 5 founded Eastern Orthodoxy
- **T143** `event` suzerain of Kabul: none -> SUMERIA
- **T151** `gossip` Your delegate, Ahmes, learned that Sumeria has just formed an alliance with Egypt.
- **T151** `gossip` Your delegate, Ahmes, learned that Sumeria is trading with Egypt.
- **T152** `gossip` An allied friend reports that Sumeria has built an Encampment in Adab.
- **T156** `event` Sumeria military 137 -> 199
- **T156** `gossip` An allied friend reports that Sumeria has used a Great Scientist to clear a Barbarian Outpost.
- **T157** `gossip` An allied friend reports that Sumeria has built a University in Lagash.
- **T157** `gossip` An allied friend reports that Sumeria has built a University in Uruk.
- **T160** `event` suzerain of Kabul: SUMERIA -> none
- **T161** `gossip` An allied friend reports that Sumeria has denounced the evil deeds of the Aztec.
- **T163** `gossip` An allied friend reports that Sumeria has earned the Great Scientist Galileo Galilei.
- **T163** `gossip` Rumor has it that the Aztec have progressed from the Medieval Era to the Renaissance Era.
- **T165** `gossip` An allied friend reports that Sumeria has built a Campus in Kish.
- **T166** `event` Sumeria military 172 -> 211
- **T167** `gossip` An allied friend reports that Sumeria has progressed from the Renaissance Era to the Industrial Era.
- **T171** `gossip` Your delegate, Bahiti, learned that the Aztec have just received a foreign delegation. It appears they came from Egypt.
- **T172** `gossip` An allied friend reports that Sumeria has earned the Great General Jeanne d'Arc.
- **T172** `gossip` Your delegate, Kanebti, learned that the Aztec have switched governments to Classical Republic.
- **T173** `event` Aztec government Autocracy -> Classical Republic
- **T174** `gossip` An allied friend reports that Sumeria completed development of Diplomatic Service.
- **T174** `gossip` An allied friend reports that Sumeria completed research on Astronomy.
- **T175** `gossip` An allied friend reports that Sumeria has built an Aqueduct in Lagash.
- **T177** `gossip` Your delegate, Kanebti, learned that the Aztec have built a Campus in Chapultepec.
- **T177** `gossip` Your delegate, Kanebti, learned that the Aztec have built a University in Atzcapotzalco.
- **T178** `gossip` An allied friend reports that Sumeria is expanding, adding the new settlement: Bad-Tibira.
- **T179** `event` suzerain of Kabul: none -> ME
- **T181** `gossip` Your delegate, Kanebti, learned that the Aztec have launched an inquisition rooting out heretics opposed to Eastern Orthodoxy.
- **T182** `gossip` A recent news article revealed that Sumeria has declared their friendship with Egypt.
- **T183** `gossip` Your delegate, Pasupti, learned that A new building has appeared in the capital of Sumeria: a permanent embassy from Egypt.
- **T184** `gossip` Your delegate, Pasupti, learned that Sumeria has built a Campus in Adab.
- **T185** `gossip` A recent news article revealed that the Aztec are trading with England.
- **T189** `gossip` A recent news article revealed that the Aztec have progressed from the Renaissance Era to the Industrial Era.
- **T190** `event` Aztec military 138 -> 104
- **T190** `gossip` A recent news article revealed that the Aztec have denounced the evil deeds of Egypt.
- **T191** `gossip` Your delegate, Pasupti, learned that Gilgamesh has warned Montezuma about interfering with the agenda: Ally of Enkidu.
- **T192** `gossip` Your delegate, Pasupti, learned that Sumeria has denounced the evil deeds of the Aztec.
- **T193** `event` Sumeria military 126 -> 191
- **T194** `gossip` An allied friend reports that Sumeria has earned the Great Scientist James Young.
- **T194** `gossip` An allied friend reports that Sumeria has just formed an alliance with Egypt.
- **T194** `gossip` An allied friend reports that Sumeria has used a War-Cart to clear a Barbarian Outpost.
- **T194** `gossip` An allied friend reports that Sumeria is trading with Egypt.
- **T197** `event` Sumeria military 182 -> 223
- **T197** `event` suzerain of Stockholm: SUMERIA -> none
- **T197** `gossip` A recent news article revealed that the Aztec are expanding, adding the new settlement: Texcoco.
- **T197** `gossip` A recent news article revealed that the Aztec have denounced the evil deeds of India.
- **T198** `gossip` An allied friend reports that Gilgamesh has warned Montezuma about interfering with the agenda: Explorer.
- **T198** `gossip` An allied friend reports that Sumeria has built an Industrial Zone in Kish.
- **T198** `gossip` An allied friend reports that Sumeria has cleared land in Lagash for the Potala Palace.
- **T198** `gossip` An allied friend reports that Sumeria is looking to found a city with their newly trained Settler.
- **T199** `event` suzerain of Stockholm: none -> ME
- **T199** `gossip` An allied friend reports that Sumeria completed research on Steel.
- **T199** `gossip` An allied friend reports that Sumeria has progressed from the Industrial Era to the Modern Era.
- **T202** `gossip` A recent news article revealed that the Aztec have denounced the evil deeds of England.
- **T206** `event` Aztec military 132 -> 178
- **T211** `gossip` An allied friend reports that Sumeria has built a Theater Square in Bad-Tibira.
- **T213** `event` Sumeria military 247 -> 196
- **T214** `gossip` An allied friend reports that Sumeria is expanding, adding the new settlement: Shuruppak.
- **T215** `gossip` An allied friend reports that Pilgrims from Sumeria are now flocking to see the holy relic: Book of Thoth.
- **T215** `gossip` An allied friend reports that Sumeria completed research on Combustion.
- **T217** `gossip` An allied friend reports that Sumeria completed research on Scientific Theory.
- **T218** `gossip` An allied friend reports that Sumeria has built a Theater Square in Rio de Janeiro.
- **T220** `event` Sumeria military 195 -> 74
- **T220** `gossip` An allied friend reports that Sumeria completed research on Industrialization.
- **T221** `event` Sumeria military 74 -> 2
- **T223** `gossip` An allied friend reports that Sumeria completed research on Sanitation.
- **T223** `gossip` An allied friend reports that Sumeria has denounced the evil deeds of the Aztec.
- **T225** `gossip` Your delegate, Titi, learned that Sumeria has declared their friendship with Egypt.
- **T226** `gossip` A recent news article revealed that the Aztec have denounced the evil deeds of Egypt.
- **T226** `gossip` Your delegate, Titi, learned that Gilgamesh has thanked Cleopatra for cooperating with the agenda: Ally of Enkidu.
- **T232** `gossip` Your delegate, Titi, learned that Gilgamesh has warned Montezuma about interfering with the agenda: Ally of Enkidu.
- **T233** `gossip` A recent news article revealed that the Aztec have denounced the evil deeds of England.
- **T233** `gossip` Your delegate, Titi, learned that Sumeria has earned the Great Scientist Alan Turing.
- **T234** `gossip` A recent news article revealed that the Aztec have denounced the evil deeds of India.
- **T236** `gossip` Your delegate, Titi, learned that Sumeria has just formed an alliance with Egypt.
- **T236** `gossip` Your delegate, Titi, learned that Sumeria is trading with Egypt.
- **T241** `gossip` A recent news article revealed that the Aztec have progressed from the Industrial Era to the Modern Era.
- **T241** `gossip` An allied friend reports that Sumeria completed research on Radio.
- **T243** `gossip` A recent news article revealed that England has declared their friendship with Egypt.
- **T243** `gossip` A recent news article revealed that England has just formed an alliance with Egypt.
- **T243** `gossip` A recent news article revealed that England is trading with Egypt.
- **T244** `gossip` An allied friend reports that Sumeria completed research on Electricity.
- **T244** `gossip` An allied friend reports that Sumeria is considering a war on India.
- **T246** `gossip` An allied friend reports that England has declared their friendship with Sumeria.
- **T246** `gossip` An allied friend reports that England is trading with Sumeria.
- **T246** `gossip` An allied friend reports that Gilgamesh has thanked Victoria for cooperating with the agenda: Ally of Enkidu.
- **T246** `gossip` An allied friend reports that Sumeria has declared their friendship with England.
- **T247** `gossip` An allied friend reports that Sumeria completed development of Nationalism.
- **T247** `gossip` An allied friend reports that Sumeria is expanding, adding the new settlement: Ur.
- **T248** `event` suzerain of Kumasi: ENGLAND -> none
- **T249** `gossip` A recent news article revealed that India has progressed from the Renaissance Era to the Industrial Era.
- **T249** `gossip` An allied friend reports that Sumeria completed research on Computers.
- **T249** `gossip` An allied friend reports that Sumeria has progressed from the Modern Era to the Atomic Era.
- **T250** `gossip` An allied friend reports that A new building has appeared in the capital of England: a permanent embassy from Sumeria.
- **T250** `gossip` An allied friend reports that A new building has appeared in the capital of Sumeria: a permanent embassy from England.
- **T250** `gossip` An allied friend reports that England is expanding, adding the new settlement: Bradford.
- **T250** `gossip` An allied friend reports that Victoria has warned Gilgamesh about interfering with the agenda: Sun Never Sets.
- **T254** `gossip` An allied friend reports that England has built a Commercial Hub in Plymouth.
- **T254** `gossip` An allied friend reports that Sumeria has denounced the evil deeds of the Aztec.
- **T255** `gossip` An allied friend reports that England adopted the Economic policy Heritage Tourism.
- **T255** `gossip` An allied friend reports that England has progressed from the Modern Era to the Atomic Era.
- **T255** `gossip` An allied friend reports that England is trading with India.
- **T256** `gossip` A recent news article revealed that the Aztec are expanding, adding the new settlement: Teotihuacán.
- **T257** `gossip` An allied friend reports that England has built an Industrial Zone in London.
- **T258** `gossip` An allied friend reports that Sumeria completed research on Plastics.
- **T259** `gossip` A recent news article revealed that the Aztec have denounced the evil deeds of Egypt.
- **T261** `event` Sumeria military 45 -> 13
- **T261** `gossip` An allied friend reports that England has cleared land in Birmingham for the Potala Palace.
- **T261** `gossip` An allied friend reports that England has just formed an alliance with Sumeria.
- **T261** `gossip` An allied friend reports that England is trading with Sumeria.
- **T261** `gossip` An allied friend reports that Gilgamesh has thanked Montezuma for cooperating with the agenda: Explorer.
- **T261** `gossip` An allied friend reports that Sumeria has just stumbled on the Great Barrier Reef natural wonder.
- **T261** `gossip` An allied friend reports that Sumeria has just stumbled on the Yosemite natural wonder.
- **T262** `gossip` An allied friend reports that Sumeria has built an Aerodrome in Adab.
- **T263** `gossip` An allied friend reports that England has built an Entertainment Complex in Newcastle upon Tyne.
- **T264** `gossip` A recent news article revealed that the Aztec have denounced the evil deeds of England.
- **T265** `event` England military 167 -> 211
- **T265** `gossip` An allied friend reports that England has built a Royal Navy Dockyard in Liverpool.
- **T266** `gossip` A recent news article revealed that India is trading with the Aztec.
- **T266** `gossip` An allied friend reports that Sumeria completed research on Chemistry.
- **T267** `gossip` Your delegate, Hasina, learned that Sumeria has declared their friendship with Egypt.
- **T270** `event` suzerain of Mohenjo-Daro: ENGLAND -> none
- **T270** `gossip` An allied friend reports that England has built a Theater Square in Manchester.
- **T270** `gossip` An allied friend reports that England is looking to found a city with their newly trained Settler.
- **T272** `gossip` An allied friend reports that A new building has appeared in the capital of England: a permanent embassy from Egypt.
- **T273** `gossip` A recent news article revealed that the Aztec have denounced the evil deeds of India.
- **T273** `gossip` A recent news article revealed that the Aztec have progressed from the Modern Era to the Atomic Era.
- **T273** `gossip` Your delegate, Hasina, learned that Gilgamesh has thanked Gandhi for cooperating with the agenda: Explorer.
- **T274** `gossip` Your delegate, Berenice, learned that England has declared their friendship with Egypt.
- **T275** `gossip` A recent news article revealed that India is trading with Sumeria.
- **T275** `gossip` Your delegate, Hasina, learned that Sumeria completed research on Rocketry.
- **T275** `gossip` Your delegate, Hasina, learned that Sumeria has sent an Envoy to Stockholm.
- **T276** `event` Aztec military 170 -> 211
- **T276** `event` suzerain of Stockholm: ME -> none
- **T278** `event` Aztec military 170 -> 213
- **T278** `gossip` Your delegate, Berenice, learned that England has built a Royal Navy Dockyard in Bristol.
- **T278** `gossip` Your delegate, Hasina, learned that Sumeria is looking to found a city with their newly trained Settler.
- **T279** `event` Aztec military 213 -> 289
- **T279** `event` suzerain of Stockholm: none -> ME
- **T279** `gossip` Your delegate, Hasina, learned that Sumeria has built a Campus in Bad-Tibira.
- **T282** `gossip` Your delegate, Berenice, learned that England is expanding, adding the new settlement: Sheffield.
- **T283** `gossip` Your delegate, Zuberi, learned that A new building has appeared in the capital of India: a permanent embassy from Egypt.
- **T284** `event` England military 211 -> 293
- **T285** `gossip` Your delegate, Merit, learned that Sumeria has denounced the evil deeds of the Aztec.
- **T286** `gossip` Your delegate, Berenice, learned that England has cleared land in London for the Oxford University.
- **T288** `gossip` Your Spy, Layla, uncovered news that Gilgamesh has thanked Cleopatra for cooperating with the agenda: Explorer.
- **T288** `gossip` Your delegate, Zuberi, learned that India adopted the Economic policy Resource Management.
- **T288** `gossip` Your delegate, Zuberi, learned that India adopted the Military policy Logistics.
- **T288** `gossip` Your delegate, Zuberi, learned that India has progressed from the Industrial Era to the Modern Era.
- **T291** `gossip` Your delegate, Berenice, learned that England completed development of Mass Media.
- **T292** `event` Sumeria military 85 -> 167
- **T292** `event` suzerain of Buenos Aires: ENGLAND -> INDIA
- **T292** `gossip` Your Spy, Layla, uncovered news that Sumeria has declared their friendship with England.
- **T292** `gossip` Your Spy, Layla, uncovered news that Sumeria has earned the Great Scientist Carl Sagan.
- **T292** `gossip` Your delegate, Berenice, learned that England has declared their friendship with Sumeria.
- **T293** `gossip` A recent news article revealed that the Aztec have denounced the evil deeds of Egypt.
- **T293** `gossip` Your Spy, Layla, uncovered news that Sumeria completed research on Composites.
- **T293** `gossip` Your Spy, Layla, uncovered news that Sumeria has progressed from the Atomic Era to the Information Era.
- **T294** `gossip` Your Spy, Layla, uncovered news that Sumeria is expanding, adding the new settlement: Sippar.
- **T294** `gossip` Your delegate, Zuberi, learned that India has built a Harbor in Mumbai.
- **T295** `gossip` A recent news article revealed that the Aztec have denounced the evil deeds of England.
- **T295** `gossip` Your delegate, Berenice, learned that England has launched an inquisition rooting out heretics opposed to Protestantism.
- **T296** `gossip` Your delegate, Berenice, learned that England has built a Royal Navy Dockyard in Bradford.
- **T298** `event` Aztec military 271 -> 350
- **T298** `event` England military 276 -> 345
- **T298** `event` suzerain of Mohenjo-Daro: none -> AZTEC
- **T298** `gossip` Your delegate, Benipe, learned that Sumeria has declared their friendship with Egypt.
- **T299** `gossip` Your delegate, Benipe, learned that Gilgamesh has thanked Cleopatra for cooperating with the agenda: Ally of Enkidu.
- **T300** `event` suzerain of Kumasi: none -> AZTEC
- **T300** `gossip` Your delegate, Benipe, learned that Gilgamesh has warned Cleopatra about interfering with the agenda: Explorer.
- **T300** `gossip` Your delegate, Berenice, learned that England has built an Industrial Zone in Birmingham.
- **T300** `gossip` Your delegate, Zuberi, learned that India is expanding, adding the new settlement: Srinagar.
- **T300** `gossip` Your delegate, Zuberi, learned that India is trading with Egypt.
- **T302** `event` India military 87 -> 133
- **T302** `gossip` Your delegate, Berenice, learned that England completed development of Mobilization.
- **T302** `gossip` Your delegate, Berenice, learned that England has built a Commercial Hub in Newcastle upon Tyne.
- **T302** `gossip` Your delegate, Berenice, learned that England has earned the Great Artist Vincent van Gogh.
- **T302** `gossip` Your delegate, Zuberi, learned that Gandhi has thanked Gilgamesh for cooperating with the agenda: Paranoid.
- **T303** `gossip` A recent news article revealed that the Aztec are expanding, adding the new settlement: Chalco.
- **T304** `gossip` A recent news article revealed that the Aztec have denounced the evil deeds of India.
- **T304** `gossip` Your delegate, Zuberi, learned that India has progressed from the Modern Era to the Atomic Era.
- **T305** `event` suzerain of Mogadishu: ENGLAND -> INDIA
- **T305** `gossip` Your delegate, Berenice, learned that England has declared their friendship with Egypt.
- **T305** `gossip` Your delegate, Berenice, learned that England is looking to found a city with their newly trained Settler.
- **T306** `gossip` Your Spy, Layla, uncovered news that Sumeria has built an Aerodrome in Ur.
- **T306** `gossip` Your delegate, Berenice, learned that Victoria has warned Cleopatra about interfering with the agenda: Money Grubber.
- **T307** `gossip` Your Spy, Layla, uncovered news that Gilgamesh has warned Victoria about interfering with the agenda: Explorer.
- **T307** `gossip` Your delegate, Berenice, learned that England completed development of Ideology.
- **T307** `gossip` Your delegate, Berenice, learned that England completed research on Flight.
- **T307** `gossip` Your delegate, Zuberi, learned that India adopted the Economic policy Heritage Tourism.
- **T308** `event` suzerain of Mohenjo-Daro: AZTEC -> INDIA
- **T310** `gossip` Your Spy, Layla, uncovered news that Sumeria has sent an Envoy to Kabul.
- **T311** `event` India military 145 -> 109
- **T311** `event` suzerain of Kabul: ME -> none
- **T312** `event` Aztec military 375 -> 195
- **T312** `event` suzerain of Kabul: none -> ME
- **T312** `gossip` Your Spy, Layla, uncovered news that Sumeria completed research on Stealth Technology.
- **T312** `gossip` Your delegate, Berenice, learned that England has denounced the evil deeds of India.
- **T313** `event` suzerain of Kumasi: AZTEC -> none
- **T313** `gossip` Your Spy, Layla, uncovered news that Gilgamesh has thanked Gandhi for cooperating with the agenda: Ally of Enkidu.
- **T313** `gossip` Your Spy, Layla, uncovered news that Sumeria has declared their friendship with India.
- **T313** `gossip` Your delegate, Zuberi, learned that India has declared their friendship with Sumeria.
- **T314** `event` Sumeria military 160 -> 239
- **T314** `gossip` Your Spy, Layla, uncovered news that Gilgamesh has warned Victoria about interfering with the agenda: Ally of Enkidu.
- **T314** `gossip` Your delegate, Berenice, learned that England has earned the Great Admiral Togo Heihachiro.
- **T314** `gossip` Your delegate, Zuberi, learned that India has cleared land in Agra for the Oxford University.
- **T314** `gossip` Your delegate, Zuberi, learned that India has declared their friendship with Egypt.
- **T315** `gossip` Your delegate, Zuberi, learned that India has built a Commercial Hub in Mysore.
- **T316** `event` India military 109 -> 172
- **T316** `event` suzerain of Kumasi: none -> INDIA
- **T316** `gossip` Your Spy, Layla, uncovered news that Sumeria has denounced the evil deeds of the Aztec.
- **T316** `gossip` Your Spy, Layla, uncovered news that Sumeria is looking to found a city with their newly trained Settler.
- **T316** `gossip` Your delegate, Berenice, learned that England has just formed an alliance with Egypt.
- **T316** `gossip` Your delegate, Berenice, learned that England is trading with Egypt.
- **T316** `gossip` Your delegate, Zuberi, learned that Gandhi has thanked Montezuma for cooperating with the agenda: Paranoid.
- **T317** `gossip` Your Spy, Layla, uncovered news that Sumeria has built an Entertainment Complex in Lagash.
- **T317** `gossip` Your Spy, Layla, uncovered news that Sumeria has cleared land in Lagash for the Oxford University.
- **T318** `gossip` Your Spy, Layla, uncovered news that Sumeria completed research on Advanced Flight.
- **T318** `gossip` Your delegate, Zuberi, learned that Gandhi has thanked Victoria for cooperating with the agenda: Paranoid.
- **T319** `gossip` An allied friend reports that England completed development of Suffrage.
- **T319** `gossip` An allied friend reports that England has switched governments to Democracy.
- **T319** `gossip` Your Spy, Layla, uncovered news that Sumeria has just formed an alliance with India.
- **T319** `gossip` Your Spy, Layla, uncovered news that Sumeria is trading with India.
- **T319** `gossip` Your delegate, Zuberi, learned that India has built an Entertainment Complex in Delhi.
- **T319** `gossip` Your delegate, Zuberi, learned that India has just stumbled on the Crater Lake natural wonder.
- **T319** `gossip` Your delegate, Zuberi, learned that India has just stumbled on the Tsingy de Bemaraha natural wonder.
- **T320** `gossip` An allied friend reports that England has built a Neighborhood in Plymouth.
- **T322** `event` England government Merchant Republic -> Democracy
- **T322** `event` England military 262 -> 208
- **T322** `event` Sumeria military 232 -> 140
- **T322** `gossip` A recent news article revealed that the Aztec have switched governments to Monarchy.
- **T322** `gossip` An allied friend reports that England has built a Neighborhood in Newcastle upon Tyne.
- **T322** `gossip` Your Spy, Layla, uncovered news that A new building has appeared in the capital of Sumeria: a permanent embassy from India.
- **T323** `event` Aztec government Classical Republic -> Monarchy
- **T323** `event` England military 208 -> 160
- **T323** `event` Sumeria military 140 -> 63
- **T323** `gossip` A recent news article revealed that the Aztec have progressed from the Atomic Era to the Information Era.
- **T323** `gossip` An allied friend reports that England is considering a war on Sumeria.
- **T323** `gossip` Your Spy, Layla, uncovered news that Sumeria has built a Harbor in Recife.
- **T323** `gossip` Your Spy, Layla, uncovered news that Sumeria is expanding, adding the new settlement: Larak.
- **T324** `gossip` A recent news article revealed that the Aztec have denounced the evil deeds of Egypt.
- **T325** `event` England military 163 -> 122
- **T325** `gossip` An allied friend reports that England has earned the Great Writer Karel Capek.
- **T326** `event` suzerain of Mohenjo-Daro: INDIA -> none
- **T326** `gossip` A recent news article revealed that the Aztec have denounced the evil deeds of England.
- **T326** `gossip` An allied friend reports that England has built a Theater Square in Bristol.
- **T326** `gossip` Your Spy, Layla, uncovered news that Sumeria completed research on Satellites.
- **T327** `gossip` An allied friend reports that Victoria has thanked Cleopatra for cooperating with the agenda: Money Grubber.
- **T327** `gossip` Your Spy, Layla, uncovered news that Sumeria has built a Campus in Shuruppak.
- **T328** `gossip` An allied friend reports that England completed research on Electricity.
- **T329** `gossip` Your Spy, Layla, uncovered news that Sumeria completed research on Robotics.
- **T329** `gossip` Your Spy, Layla, uncovered news that Sumeria has declared their friendship with Egypt.
- **T331** `gossip` An allied friend reports that England adopted the Economic policy Third Alternative.
- **T331** `gossip` An allied friend reports that England completed development of Totalitarianism.
- **T334** `gossip` Your Spy, Layla, uncovered news that Sumeria has built an Aerodrome in Kish.
- **T335** `event` Aztec military 201 -> 320
- **T335** `gossip` A recent news article revealed that the Aztec have denounced the evil deeds of India.
- **T335** `gossip` An allied friend reports that England completed research on Chemistry.
- **T335** `gossip` An allied friend reports that England has built a Theater Square in Bradford.
- **T335** `gossip` Your Spy, Layla, uncovered news that Sumeria completed development of Cultural Heritage.
- **T336** `gossip` Your Spy, Layla, uncovered news that Sumeria completed research on Telecommunications.
- **T337** `gossip` Your Spy, Layla, uncovered news that Sumeria has heard that the sunbathing is great at the new seaside resort outside Recife.
- **T337** `gossip` Your delegate, Zuberi, learned that India has built a Neighborhood in Agra.
- **T338** `gossip` Your Spy, Layla, uncovered news that Sumeria has built an Encampment in Ur.
- **T339** `gossip` An allied friend reports that England completed research on Radio.
- **T340** `gossip` An allied friend reports that England has earned the Great Musician Clara Schumann.
- **T340** `gossip` An allied friend reports that England has heard that the sunbathing is great at the new seaside resort outside Liverpool.
- **T340** `gossip` Your delegate, Zuberi, learned that Gandhi has thanked Montezuma for cooperating with the agenda: Paranoid.
- **T340** `gossip` Your delegate, Zuberi, learned that Gandhi has warned Victoria about interfering with the agenda: Paranoid.
- **T340** `gossip` Your delegate, Zuberi, learned that India has built a Campus in Patna.
- **T341** `gossip` An allied friend reports that England has heard that the sunbathing is great at the new seaside resort outside Liverpool.
- **T341** `gossip` An allied friend reports that England has used a Redcoat to clear a Barbarian Outpost.
- **T341** `gossip` Your delegate, Zuberi, learned that India has built a Harbor in Madurai.
- **T342** `gossip` An allied friend reports that England has sent an Envoy to Yerevan.
- **T343** `gossip` An allied friend reports that England has built a Royal Navy Dockyard in Sheffield.
- **T344** `gossip` An allied friend reports that England completed development of Cold War.
- **T344** `gossip` Your Spy, Layla, uncovered news that Sumeria completed research on Combined Arms.
- **T345** `event` England military 159 -> 200
- **T345** `event` India military 222 -> 301
- **T345** `gossip` An allied friend reports that England completed research on Computers.
- **T345** `gossip` An allied friend reports that England has built an Aerodrome in London.
- **T345** `gossip` Your Spy, Layla, uncovered news that Sumeria has just formed an alliance with Egypt.
- **T346** `gossip` An allied friend reports that Gilgamesh has thanked Gandhi for cooperating with the agenda: Explorer.
- **T346** `gossip` An allied friend reports that Sumeria is looking to found a city with their newly trained Settler.
- **T346** `gossip` Your delegate, Zuberi, learned that India has cleared land in Agra for the Broadway.
- **T347** `gossip` An allied friend reports that Sumeria has denounced the evil deeds of the Aztec.
- **T348** `gossip` Your delegate, Hotep, learned that England has built an Industrial Zone in Liverpool.
- **T349** `event` England military 200 -> 250
- **T350** `gossip` An allied friend reports that Sumeria has declared their friendship with India.
- **T350** `gossip` Your delegate, Hotep, learned that England has heard that the sunbathing is great at the new seaside resort outside Manchester.
- **T350** `gossip` Your delegate, Zuberi, learned that India has declared their friendship with Sumeria.
- **T351** `gossip` Your Spy, Layla, uncovered news that India adopted the Economic policy Heritage Tourism.
- **T351** `gossip` Your Spy, Layla, uncovered news that India adopted the Economic policy New Deal.
- **T351** `gossip` Your Spy, Layla, uncovered news that India completed development of Suffrage.
- **T351** `gossip` Your Spy, Layla, uncovered news that India has switched governments to Democracy.
- **T351** `gossip` Your delegate, Hotep, learned that England has built an Aerodrome in Newcastle upon Tyne.
- **T352** `event` India government Classical Republic -> Democracy
- **T352** `gossip` Your delegate, Hotep, learned that England has built an Aerodrome in Plymouth.
- **T353** `gossip` An allied friend reports that Gilgamesh has thanked Victoria for cooperating with the agenda: Ally of Enkidu.
- **T353** `gossip` An allied friend reports that Sumeria completed research on Advanced Ballistics.
- **T353** `gossip` An allied friend reports that Sumeria has declared their friendship with England.
- **T353** `gossip` Your Spy, Layla, uncovered news that Gandhi has thanked Gilgamesh for cooperating with the agenda: Paranoid.
- **T353** `gossip` Your delegate, Hotep, learned that England has declared their friendship with Sumeria.
- **T354** `gossip` An allied friend reports that Sumeria is expanding, adding the new settlement: Isin.
- **T354** `gossip` Your delegate, Hotep, learned that England has built a Power Plant in Birmingham.
- **T355** `gossip` A recent news article revealed that the Aztec are expanding, adding the new settlement: Malinalco.
- **T355** `gossip` Your delegate, Hotep, learned that Victoria has warned Montezuma about interfering with the agenda: Sun Never Sets.
- **T356** `gossip` A recent news article revealed that the Aztec have denounced the evil deeds of Egypt.
- **T356** `gossip` Your delegate, Hotep, learned that England has declared their friendship with Egypt.
- **T357** `event` Sumeria military 79 -> 261
- **T357** `gossip` A recent news article revealed that the Aztec have denounced the evil deeds of England.
- **T357** `gossip` Your Spy, Layla, uncovered news that India has built a Neighborhood in Delhi.
- **T357** `gossip` Your Spy, Layla, uncovered news that India has cleared land in Delhi for the Great Lighthouse.
- **T358** `gossip` An allied friend reports that Sumeria completed research on Nuclear Fission.
- **T358** `gossip` An allied friend reports that Sumeria has just formed an alliance with England.
- **T358** `gossip` An allied friend reports that Sumeria is trading with England.
- **T358** `gossip` Your delegate, Hotep, learned that England adopted the Economic policy Satellite Broadcasts.
- **T358** `gossip` Your delegate, Hotep, learned that England adopted the Economic policy Third Alternative.
- **T359** `gossip` An allied friend reports that Sumeria has earned the Great General Douglas MacArthur.
- **T359** `gossip` An allied friend reports that Sumeria has started Manhattan Project.
- **T359** `gossip` Your Spy, Layla, uncovered news that India has earned the Great Artist Boris Orlovsky.
- **T360** `gossip` Your delegate, Hotep, learned that A new building has appeared in the capital of England: a permanent embassy from India.
- **T361** `gossip` Your delegate, Hotep, learned that England has progressed from the Atomic Era to the Information Era.
- **T362** `gossip` Your Spy, Layla, uncovered news that Gandhi has warned Montezuma about interfering with the agenda: Paranoid.
- **T362** `gossip` Your Spy, Layla, uncovered news that Gandhi has warned Victoria about interfering with the agenda: Paranoid.
- **T363** `gossip` Your Spy, Layla, uncovered news that India adopted the Economic policy Third Alternative.
- **T363** `gossip` Your Spy, Layla, uncovered news that India completed development of Totalitarianism.
- **T364** `gossip` An allied friend reports that Sumeria completed research on Lasers.
- **T365** `gossip` Your Spy, Layla, uncovered news that India has declared their friendship with England.
- **T365** `gossip` Your delegate, Hotep, learned that England has declared their friendship with India.
- **T366** `gossip` A recent news article revealed that the Aztec have denounced the evil deeds of India.
- **T366** `gossip` An allied friend reports that Sumeria has built a Theater Square in Recife.
- **T367** `event` England military 181 -> 338
- **T368** `gossip` Your delegate, Hotep, learned that England has heard that the sunbathing is great at the new seaside resort outside Plymouth.
- **T370** `event` England military 338 -> 266
- **T370** `gossip` Your delegate, Hotep, learned that England adopted the Economic policy Sports Media.
- **T370** `gossip` Your delegate, Hotep, learned that England has built a Campus in Manchester.
- **T371** `gossip` An allied friend reports that Sumeria completed research on Nuclear Fusion.
- **T372** `gossip` Your delegate, Hotep, learned that England has built an Encampment in Newcastle upon Tyne.
- **T372** `gossip` Your delegate, Urbi, learned that A new building has appeared in the capital of India: a permanent embassy from England.
- **T372** `gossip` Your delegate, Urbi, learned that India completed research on Steel.
- **T374** `event` Sumeria military 248 -> 172
- **T374** `event` suzerain of Yerevan: none -> ENGLAND
- **T374** `gossip` Your delegate, Urbi, learned that Gandhi has thanked Gilgamesh for cooperating with the agenda: Paranoid.
- **T375** `gossip` Your Spy, Layla, uncovered news that India has extracted a new archaeological work: Earring.
- **T375** `gossip` Your delegate, Hotep, learned that England has built a Theater Square in Sheffield.
- **T376** `gossip` Your Spy, Layla, uncovered news that India has sent an Envoy to Yerevan.
- **T376** `gossip` Your delegate, Abubakar, learned that Sumeria has built an Aerodrome in Shuruppak.
- **T376** `gossip` Your delegate, Abubakar, learned that Sumeria has declared their friendship with Egypt.
- **T377** `gossip` Your Spy, Layla, uncovered news that India completed development of Cold War.
- **T377** `gossip` Your delegate, Abubakar, learned that Gilgamesh has thanked Cleopatra for cooperating with the agenda: Ally of Enkidu.
- **T378** `event` England military 297 -> 383
- **T378** `event` Sumeria military 172 -> 60
- **T378** `event` suzerain of Yerevan: ENGLAND -> none
- **T378** `gossip` Your Spy, Layla, uncovered news that India has built a Commercial Hub in Delhi.
- **T378** `gossip` Your delegate, Abubakar, learned that Sumeria has denounced the evil deeds of the Aztec.
- **T378** `gossip` Your delegate, Abubakar, learned that Sumeria is looking to found a city with their newly trained Settler.
- **T379** `gossip` Your Spy, Layla, uncovered news that India has extracted a new archaeological work: Scroll.
- **T379** `gossip` Your Spy, Layla, uncovered news that India is looking to found a city with their newly trained Settler.
- **T379** `gossip` Your delegate, Abubakar, learned that Sumeria completed research on Future Tech.
- **T379** `gossip` Your delegate, Hotep, learned that Victoria has thanked Cleopatra for cooperating with the agenda: Money Grubber.
- **T380** `gossip` Your Spy, Layla, uncovered news that India has extracted a new archaeological work: Astrolabe.
- **T381** `gossip` Your Spy, Layla, uncovered news that India has declared their friendship with Sumeria.
- **T381** `gossip` Your delegate, Abubakar, learned that Gilgamesh has thanked Gandhi for cooperating with the agenda: Ally of Enkidu.
- **T381** `gossip` Your delegate, Abubakar, learned that Sumeria has declared their friendship with India.
- **T381** `gossip` Your delegate, Hotep, learned that England has built an Aerodrome in Bradford.
- **T382** `gossip` Your Spy, Layla, uncovered news that India has launched an inquisition rooting out heretics opposed to Hinduism.
- **T384** `gossip` Your delegate, Hotep, learned that England has earned the Great Artist Amrita Sher-Gil.
- **T386** `gossip` Your Spy, Layla, uncovered news that India completed research on Replaceable Parts.
- **T386** `gossip` Your Spy, Layla, uncovered news that India is no longer seeking a Domination Victory.
- **T387** `gossip` A recent news article revealed that the Aztec have denounced the evil deeds of Egypt.
- **T387** `gossip` A recent news article revealed that the Aztec have used a Modern AT to clear a Barbarian Outpost.
- **T387** `gossip` Your delegate, Hamadi, learned that Sumeria has built a Harbor in Isin.
- **T388** `gossip` A recent news article revealed that the Aztec have denounced the evil deeds of England.
- **T388** `gossip` Your Spy, Layla, uncovered news that India has just formed an alliance with England.
- **T388** `gossip` Your Spy, Layla, uncovered news that India is expanding, adding the new settlement: Ahmadabad.
- **T388** `gossip` Your delegate, Hotep, learned that England is trading with India.
- **T389** `gossip` Your delegate, Hamadi, learned that Sumeria has declared their friendship with England.
- **T389** `gossip` Your delegate, Hotep, learned that England has declared their friendship with Sumeria.
- **T390** `gossip` Your Spy, Layla, uncovered news that India adopted the Economic policy Sports Media.
- **T390** `gossip` Your Spy, Layla, uncovered news that India completed development of Professional Sports.
- **T392** `gossip` A recent news article revealed that the Aztec have switched governments to Democracy.
- **T393** `gossip` Your Spy, Layla, uncovered news that India completed research on Combustion.
- **T394** `gossip` A recent news article revealed that the Aztec have completed the Space Race project Launch Earth Satellite.
- **T394** `gossip` Your Spy, Layla, uncovered news that Gandhi has warned Montezuma about interfering with the agenda: Paranoid.
- **T395** `gossip` Your delegate, Hamadi, learned that Sumeria has built a Commercial Hub in Recife.
- **T396** `event` Aztec government Monarchy -> Democracy
- **T396** `event` England military 342 -> 413
- **T396** `event` India military 245 -> 147
- **T396** `event` Sumeria military 60 -> 2

---

## 4. TURN-BY-TURN NARRATIVE

*No narrative blocks available.*

---

## 5. FINAL STATE

*Omitted to fit the budget.*