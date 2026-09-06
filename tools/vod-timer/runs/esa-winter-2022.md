# ESA Winter 2022 — backfill

Issue #50. One Horaro schedule (`2022-winter`), tag `#ESAWinter22`, shipped as
`ESA 2022 Winter`.

**The first single-stream event of the backfill.** Every event from #43 to #49
had two schedules and shipped an `(One)`/`(Two)` pair. This one has a single
schedule, a single CSV and a single event name, following the site's existing
single-stream spelling (`ESA 2021 Winter`, `ESA 2018 Winter`, `ESA 2024
Summer`) rather than the two-stream one. Checked against the restored
production database first: no `ESA 2022 Winter` row existed.

- **Settings**: `--height 480 --tail 600 --step 12`, six shards.
- **124 schedule rows**, no filler — every row carries a category, including
  the two speeches.
- **Wall time**: 1h 53m for all 124 reads. **The bot wall never went up.**
- **Outcome**: **122 of 124 rows live with a time.** 98 read `high` and shipped
  unreviewed, 24 were resolved from frames by hand, and **none ships on an
  unconfirmed reading.** The two rows with no time are the Opening and Closing
  Speeches, whose layout carries no timer at all.

## Outcome

| | |
|---|---:|
| schedule rows | 124 |
| shipped with a time | **122** |
| `high`, shipped unreviewed | **98** |
| resolved from frames (`human`) | **24** |
| shipped unconfirmed | **0** |
| no time, not shipped | 2 |

**98 of 124 accepted without review — 79%**, against 81% on both Summer 2022
runs and 89% on Winter 2021. `release-event.sh` wrote no `unvouched.md`,
because there is nothing on the list.

## Resolution

No ESA timing sheet exists for this event, so `slot-exact` was unavailable. The
schedule's Game cells link **Twitch** VODs, not YouTube, so there are no
`horaro-link` answers either — `curl … | grep -c 'youtube.com/watch'` returns 0.
Every row was resolved by title search.

| how | n |
|---|---:|
| `tag-game-runner` | 106 |
| `tag-game` | 5 |
| corrected by hand | **13** |
| `weak` | 2 → corrected |
| `no-hits` | 1 → corrected |

The raw resolve was 116 `tag-game-runner`, 5 `tag-game`, 2 `weak`, 1 `no-hits`
— the expected shape. **Ten of the 116 were wrong anyway**, and that is the
finding of this event.

### Eleven rows matched ESA's Russian restream channel at full confidence

`resolve` returned `tag-game-runner(1.0)` — the highest tier title matching has
— for eleven runs whose video is ESA's **Russian restream**, not ESA's own
upload. The titles are unmistakable in hindsight (`… от tharixer -
#ESAWinter22 [RU]`) and invisible to every artefact the tool produces.

The cause is the `rank()` ordering #49 already named, and this event prices it
at **eleven matches out of 124 rather than two out of 130**. The restream
titles carry the runner's Horaro handle *verbatim*, while ESA's own upload
spells it differently or omits it entirely:

| run | ESA's own title says | the restream says |
|---|---|---|
| Sly 2: Band of Thieves | `by Ricky` | `от tharixer` |
| Castlevania: Portrait of Ruin | `by Diagon` | `от diagongdx` |
| Discworld | `by mindez` | `от mindezzy` |
| Bloodstained: Ritual of the Night | *(no runner)* | `от theblacktastic` |
| Kingdom Hearts Birth by Sleep | *(no runner)* | `от rebeldragon95` |
| Grand Theft Auto III | `by ` *(empty)* | `от english_ben` |

`runner` sorts above `cscore`, so an exact handle match on the restream beats
the category agreement that would have separated them. Ten were swapped by hand
to ESA's own upload. **GripShift has no surviving ESA upload at all** — two
searches return the restream and nothing else — so that row ships the restream
knowingly.

This is not cosmetic. ESA's Wind Waker upload is 4:30:09; the Russian restream
of the same run is 3:43:33. A restream is not reliably the same footage.

### Three genuine misses

| row | why | corrected to |
|---|---|---|
| Golden Sun: Dark Dawn **(PRE-SHOW START)** | `no-hits` — the Game cell's suffix wrecks the game match | `yw5QqZNsMUQ` |
| The Legend of Zelda: Wind Waker **(PRE-SHOW END)** | `weak(0.341)` — matched a *GDQ Hotfix* video | `bMY_54G_62g` |
| Final Fantasy — Any% (Glitchless) | `weak(0.833)` — took **Final Fantasy XIII-2**'s VOD | `X0t0IoaSORo` |

The Final Fantasy miss produced **the event's only duplicate video id**, which
is exactly the symptom #49 said to watch for — a duplicate is a resolver error
announcing itself. It is also a second instance of a bug #49 found: ESA's title
here is `Final Fantasy Any% Glitchless by nashlax #ESAWinter22`, with **no
brackets at all**, so `title_fields()` cannot find a category and the row scored
`weak` on a video it had matched correctly by name.

After the thirteen corrections: no duplicate video id within the event, and no
clash against any of the 24 CSVs already in `storage/app/csv/`.

### The schedule's own annotations are shipped verbatim

Two rows carry `(PRE-SHOW START)` / `(PRE-SHOW END)` inside the Game cell, and
those reach the site as part of the game name. That is deliberate and matches
what is already there — the games table holds `Skies of Arcadia: Legends
(PRE-SHOW)` from an earlier event. The exporter takes its metadata from Horaro;
inventing a cleaned name here would be a silent divergence from every other
event.

## Reads

| tier | n | share |
|---|---:|---:|
| `high` | 98 | 79% |
| `medium` | 11 | |
| `low` | 3 | |
| `reject` | 10 | |
| no timer found | 2 | |

All 26 non-`high` rows were resolved from frames rather than handed over as a
list: **18 corrections, 6 confirmations, and 2 that carry no timer to read.**

### The layouts, and the colour rule

Winter 2022 runs the same three layouts Summer 2022 did — a bottom info bar for
widescreen games, a left sidebar for 4:3 and handheld, and a per-runner sidebar
for races — and the **timer is yellow while running and white once stopped**,
as on Summer 2022 and *not* the orange/green the skill describes from later
years. The rule to carry forward remains "the colour changes", not "the colour
is green". Two frames 35s apart settle it without needing to judge the hue.

### The 18 corrections

| # | run | read | truth | what happened |
|---|---|---|---|---|
| 3 | Catechumen — Impossible + Hall of Fame | `0:35:00` | **0:23:31** | read the estimate |
| 4 | Control + Glitch Exhibition — Inbounds | `0:07:00` | **1:19:34** | reset clock (see below) |
| 6 | Kingdom Hearts III — Any% (Critical, L1) | `3:59:54` | **3:41:36** | `max` fallback |
| 7 | Lost Judgment — Any% (Easy) | `2:59:26` | **2:39:26** | `3`→`5`, tens of minutes |
| 8 | MediEvil: Resurrection — Any% | `0:59:16` | **0:39:16** | `3`→`5`, tens of minutes |
| 9 | Octopath Traveler — Three Stories | `5:30:00` | **4:01:52** | `max` fallback |
| 10 | Record of Lodoss War — Any% (No OoB) | `10:45:00` | **0:42:44** | `max` fallback |
| 11 | Red Dead Redemption 2 — Horseshoe Overlook | `1:59:51` | **1:43:23** | `max` fallback |
| 12 | Shadow of the Colossus — Any% (Normal) | `1:56:49` | **1:36:49** | `3`→`5`, tens of minutes |
| 13 | Anno 1404 — Any% (Fast Forward) | `0:10:55` | **0:10:35** | `3`→`5`, tens of seconds |
| 14 | Bloodstained — Any% (Zangetsu, NMG) | `0:25:00` | **0:23:00** | `3`→`5`, units of minutes |
| 15 | Discworld — Any% (ScummVM) | `0:15:09` | **0:13:09** | `3`→`5`, units of minutes |
| 18 | BioShock — Any% | `0:36:09` | **0:36:51** | wrong element |
| 19 | DANCERUSH STARDOM — Dance Showcase | `1:10:00` | **1:14:57** | read the estimate |
| 21 | Evergate — Any% (Unrestricted) | `0:32:12` | **0:34:11** | wrong element |
| 22 | Final Fantasy XIII-2 — Any% | `3:00:00` | **3:11:21** | read the estimate |
| 24 | Prey (2017) — Any% | `0:14:00` | **0:11:23** | read the estimate |
| 26 | Resident Evil 7 — Any% (NG+) | `1:31:07` | **1:32:23** | wrong element |

**Six of the eighteen are the `3`/`5` glyph**, and they land in four different
digit columns — `+20:00`, `+20s`, `+2:00` — which is the README's point that
the size of the error is set only by the column, not by the bug. A review
looking only for `+20:00` would have found three of the six.

### The six confirmations

Runs 5, 16, 17, 20, 23 and 25 read correctly and were confirmed frame by frame:
Havrd's Secret Hour `1:18:32`, A Hat in Time `2:23:59`, Anodyne `1:06:44`,
Donut County `0:35:15`, Metal Gear Solid 2 `0:58:08`, Razion EX `0:21:09`. They
are recorded as `source=human` rather than left on the OCR's own word, which is
what takes the event's unvouched list to zero.

### Two runs held a different clock in their tail, and only one fooled the tool

- **Control + Glitch Exhibition.** The slot ran the Inbounds speedrun and then
  a glitch exhibition on a **reset clock and its own 10-minute estimate**, and
  the overlay's category line changes to match. At 5s from the end the screen
  reads `00:07:00` — the exhibition. Walking back: `01:19:07` yellow at
  t=4800, `01:19:34` white at t=4870 and again at t=4920. The Inbounds run is
  **1:19:34**.
- **Anodyne.** Same shape — an Any% bonus run with a 7-minute estimate follows
  the Glitchless run — but here the OCR was **right anyway**, because the
  600-second tail window happened to contain the real freeze (`01:06:44` white
  at t=4110) as well as the bonus clock. The window length, not the logic,
  is what saved it.

The lesson is the one #49 drew and this event sharpens: a tail holding a
different run's clock is not rare, and whether the tool survives it is luck
about where `--tail` happens to land.

## Evidence on the open tool tickets

### #63 — truncated downloads passing silently: **reproducible on demand**

DANCERUSH STARDOM (`Y67XdEGaAOk`) truncates *every* time near the end of the
video, and the numbers say plainly why `MIN_CLIP_BYTES` cannot be the check:

| window requested | bytes returned | duration returned | share of window |
|---|---:|---:|---:|
| 30s at t=6205 | 2,421,641 | **5.62s** | 19% |
| 25s at t=6220 | 2,421,641 | **5.62s** | 22% |
| 25s at t=6170 | 6,779,024 | 16.95s | 68% |
| 30s at t=5925 | — | 30.05s | 100% |

**2.4 MB of 480p clears any plausible byte floor while carrying 19% of the
footage that was asked for.** The failure is silent twice over: `yt-dlp` exits
0, and `ffmpeg -ss 2` on a 5.6s clip then produces *no output file at all*
while also exiting 0, so a naive `&&` reports success. The check belongs on the
clip's **duration against the window requested**, exactly as the ticket says.

### #71 — crop area against the event's modal crop: **strong, with one caveat**

This run recorded a `crop` for all 122 readable rows, so the ratio can be
computed without `--debug-crops`. Modal crop area is **8400 px** (`168×50`).

| crop area vs modal | n | outcome |
|---|---:|---|
| ≤ 20% | 7 | **6 wrong**, 1 right-by-coincidence |
| 99–100% | 12 corrections, 3 confirmations | mixed |
| ≥ 137% | 3 | 2 right, 1 wrong |

The small-crop band is the ticket's claim and it holds: **every crop at or
under 20% of the modal area had locked onto the wrong element** — Catechumen
14%, Octopath 16%, Lodoss War 16%, FF XIII-2 16%, Prey 16%, DANCERUSH 9%.

**The caveat is real, though.** Metal Gear Solid 2 also cropped small (13%,
`56×20`) and read **correctly**. It is a race, and the crop had locked onto the
game's *own* on-screen timer rather than the ESA overlay — a different element
that happened to display the same value the overlay did. So the ratio is a
reliable **wrong-element** detector, not a wrong-*answer* detector, and a
threshold that rejects on it alone would have thrown away one correct time in
seven. Worth stating in the ticket before the threshold is written.

It also catches nothing else: **12 of the 18 corrections cropped at 99–100% of
modal.** Crop area says nothing about a digit misread, which is where two
thirds of this event's errors live.

### #66 — do not narrow the estimate-ratio guard

Only two runs on this event carry a ratio reason at all, and **both were
genuinely wrong**: Control at `0.09x` its estimate (the reset clock) and Record
of Lodoss War at `14.33x` (the `max` fallback). That is 2 for 2, against 0 for
13 across the earlier events — and both are reset-clock/fallback cases, which
is the third event agreeing that **the reset is the signal, not the ratio.**

Neither was load-bearing: Control was already rejected on the ramp
disagreement, Lodoss War on exceeding its own video. So the guard cost nothing
and caught nothing the other checks missed — but it also raised **no false
alarm at all**, which is new.

### #65 — a read equal to the estimate: 5 for 5

Five runs read their estimate exactly and **all five were wrong**: Catechumen,
DANCERUSH STARDOM, Bloodstained, Final Fantasy XIII-2, Prey. The demotion is
doing precisely what it was added for.

One of the five is a warning about *why* it fires, though. Bloodstained read
`0:25:00` against a true `0:23:00` — flagged as "reading is exactly the
`0:25:00` estimate", but the actual cause is the `3`/`5` glyph in the units of
minutes, which **coincidentally** produced the estimate's value. Reading the
flag as "calibration locked onto the estimate" would have sent someone looking
in the wrong place.

### #67 — no evidence either way

**All 124 reads completed with no download failure of any kind** — no `moov
atom not found`, no `403`, no retry needed. Nothing on this event speaks to the
240p explanation or against it.

### `resolve` records no channel

This is the event that should settle it. Eleven rows matched a restream at
`tag-game-runner(1.0)`, and **no artefact the tool produces distinguishes them
from ESA's own uploads** — the `how` column, the confidence tier and the
duration check all read perfectly. It took reading 124 titles by eye to find
them. `yt-dlp`'s search already returns `channel_id`; one extra column in
`resolved.csv` would have turned an hour of manual comparison into a sort.

## The wall, and the request budget

**The bot wall never went up.** Roughly 261 requests were spent before the
review pass — 124 `resolve` searches, 13 hand searches, and 124 batch reads —
plus about 60 more downloading review frames. Previous events hit the wall at
~220 (Winter 2023), ~250 (Summer 2025) and ~275 (Summer 2023), and #49 hit it
twice.

`seed` saved **124 requests**, halving the batch's cost from two per run to
one. Without it this event would have needed ~385 before the first review frame
and would very probably have walled, as the two events either side of it did.

## Throughput

Six shards, `--discard-clips`, one pass, no `--resume` needed. Shards finished
between 1h 37m and 1h 53m — the spread is the run mix, not throttling. 124
reads in 1h 53m is the fastest per-run rate the project has recorded.

## What to change next

1. **Sort `cscore` above `runner` in `rank()`.** #49 recommended this at a cost
   of 2 matches in 130. This event puts the cost at **11 in 124**, all of them
   the same failure — a restream whose title carries the exact Horaro handle
   beating ESA's own upload that spells it differently or omits it. It is the
   single highest-value change outstanding, and this event is a ready-made
   regression fixture for it.
2. **Record `channel_id` in `resolved.csv`** (#63's sibling, and free). Eleven
   restream matches on one event, invisible to every check. The search already
   returns it.
3. **Check the clip's duration against the window requested** (#63). The
   DANCERUSH numbers above show a byte floor cannot work, and the same check
   would have caught the `ffmpeg` no-output case in the review tooling too.
