# ESA Summer 2023 — backfill

Issue #47. Two Horaro schedules (`2023-summer1`, `2023-summer2`), tag
`#ESASummer23`, shipped as `ESA 2023 Summer (One)` and `ESA 2023 Summer (Two)`.

- **Settings**: `--height 480 --tail 600 --step 12`, six shards per schedule,
  one schedule at a time.
- **The largest event attempted so far** — 217 schedule rows against Winter
  2024's 164 and Summer 2024's 131.
- **Outcome**: **211 of 217 scheduled rows live with a time.** 178 read `high`,
  30 were resolved from frames by hand, and **3** ship on an unconfirmed
  reading. Six rows carry no time and none of them is recoverable.
- **The bot wall dominated this event.** It went up three times, the first at
  roughly **275 yt-dlp invocations** against Winter 2024's ~460, and thereafter
  after only ~85 requests in a fresh sitting. See "The wall" below.

## Resolution

217 rows, of which **one is filler** (`Milestone 1`, no category) and was
dropped before reading. Every VOD link on both schedules is Twitch — 305 on
Stream One, 125 on Stream Two, zero YouTube — so `horaro-link` never fires and
the whole event runs on title search. No ESA timing sheet exists for 2023, so
`slot-exact` is unavailable too.

| how | Stream One (154) | Stream Two (63) | total (217) |
|---|---|---|---|
| `tag-game-runner` | 116 | 60 | **176** |
| `tag-game` | 27 | 1 | **28** |
| `weak` | 9 | 2 | **11** |
| `no-hits` | 2 | 0 | **2** |

**176 of 217 on three-way agreement, and exactly one duplicate video id across
the whole event** — Grand Theft Auto V's row matched Grand Theft Auto III's VOD,
caught before a single frame was downloaded.

All 27 of Stream One's `tag-game` matches are correct. They are `tag-game`
rather than `tag-game-runner` for one of two reasons, both benign: ESA published
the title with an empty runner field (`... [Category] by  - #ESASummer23`, which
happens 11 times), or the row is a race whose title names both runners in a
form the schedule does not use.

### `weak` is a synonym for "ESA never uploaded it"

All eleven `weak` matches were hand-checked and **all eleven were the wrong
video**, which restores the reading Summer 2024 arrived at and Winter 2024's
single correct `weak` had complicated. But the useful finding is *why* they were
wrong, and it is not what the tier suggests:

- **Seven are rows ESA never published at all** — `Milestone Madness #2`–`#8`
  and `DJ Night`. The resolver reached for `Milestones - Workout Wednesday #12`,
  `REACHING CENTILLION - Miner's Haven` and `10 Deadliest Corners of the Isle of
  Man TT`. Nothing was matched wrongly so much as matched at all.
- **Two are third-party re-uploads** of ESA's own footage (see below).
- **One is the GTA V duplicate.**
- **One, `LEGO Star Wars: The Compete Saga`, is a search failure, not a scoring
  failure** — and it is the one worth acting on. See below.

Searching again with the runner appended found **no ESA upload at all** for
Final Fantasy XIV, Sammy Suricate, Grapple Hoops or A good time with..., so the
third-party matches are filling gaps ESA left rather than displacing ESA's own
videos. LEGO Star Wars is the only row where ESA had published and the resolver
failed to retrieve it.

### `search_query()` leaving the runner out cost a run

`LEGO Star Wars: The Compete Saga` came back `weak(0.167)` on an unrelated
Octopath Traveler world record. ESA *had* published it, as
`LEGO Star Wars: The Compete Saga [Free Play] by Shemcat - #ESASummer23` — a
title carrying every word of the game name and the hashtag, which would have
scored 1.0 had it been in the candidate set. It was not: the query
`LEGO Star Wars: The Compete Saga #ESASummer23` returns no ESA hit at all, while
`LEGO Star Wars Complete Saga ESA Summer 2023 Shemcat` returns it second.

`search_query()`'s docstring is right that the runner must not *filter* — horaro
and ESA's titles disagree about runner names often enough that six Winter 2024
rows depended on the fix. But it assumed the game-name query always **retrieves**
the right video, and here YouTube's search simply did not return it. Retrieval
and ranking are separate problems and #75 only solved the second.

### Two third-party channels, and only one of them is a false positive

Winter 2024 found `Wendy: Every Witch Way` matched a French restream because
`tag.lower() in norm(title).replace(" ", "")` collapses the *words* "ESA Winter
24" onto the hashtag `#ESAWinter24`. The same collapse fires here, twice over,
but the right answer is different in each case.

- **`Japanese Restream`** uploads as `<Game> | ESA Summer 2023`. Six rows matched
  it: `Grand Theft Auto V` and `Milestone Madness #2`–`#8`.
- **`Iikodane`** copies ESA's own title convention *and* carries the real
  hashtag — `Grapple Hoops Any% No Bosses & OG Levels by Lordmau5 #ESASummer23`.
  Four rows matched it, and one of those, `A good time with...`, matched at
  **`tag-game-runner(1.0)`**, the strongest tier available without a timing
  sheet. No title-shaped test can separate this channel from ESA.

**Both channels are rebroadcasting ESA's own video**, which is what makes this
different from Winter 2024's Wendy. The evidence is the calibrated crop, not the
title: Iikodane's Grapple Hoops calibrates to `168x50` at (684,356), *exactly*
ESA's modal timer box, and the Japanese Restream embeds the same ESA panel
scaled to `116x36` at (524,239) — the run's name, category, platform and
estimate all legible above a working ESA clock. So these rows ship, with their
provenance recorded here, rather than being dropped as Winter 2024 dropped
Wendy. The channel is third-party; the footage and the timer are ESA's.

The lesson is that **`norm()`'s collapse is not itself the bug**. It found real
ESA footage nine times out of ten here. What is missing is any record of *whose
upload* a match came from — `resolve` never asks for the channel, so nothing
downstream can tell ESA's own upload from a mirror of it.

### Races: 17 on Stream One, all resolved to one VOD each

Stream One carries **17 `A vs. B` races**, the most of any event yet, and #75's
`_names()` handled all of them: 13 `tag-game-runner`, 4 `tag-game`, no
duplicates. As on Winter 2024, ESA published **one combined VOD per race** titled
with both runners, so there is no per-runner ambiguity to hand to a person.

Reading them went nearly as well — 14 `high`, 2 `medium`, 1 `reject` — and the
three that fell out of `high` were ordinary misreads, not the "a race has two
clocks" failure the README warns about. Every race layout here puts one timer on
screen.

## Reads — Stream One

| tier | n | outcome |
|---|---|---|
| high | 123 | shipped unreviewed |
| medium | 16 | all checked against frames |
| low | 2 | both checked against frames |
| reject | 9 | all checked against frames |
| none | 2 | Taskmaster and Glorious Typing Competition, neither has an overlay |

**123 of 150 accepted without review — 82%**, well above Winter 2024's 71% and
close to Summer 2024's 87%. Only **14 runs** report `no stable plateau; fell back
to the largest reading`, against Winter 2024's 22 on a similar number of runs.

Of the 23 flagged runs where the tool produced a checkable time, **10 confirmed
the OCR exactly and 13 were corrected.** That is a better hit rate than Winter
2024's 12-of-39 and worse than Summer 2024's 10-of-16 — but the important
difference from Winter 2024 is that the failures here are *not* concentrated in
one glyph.

### The clock is yellow while running and white once stopped

Same tell as Winter 2024, and unmissable once known: every stopped frame in this
event renders the timer in white where the running clock is yellow. The layout
also prints the run's own name, category, platform and estimate beside the clock
in every frame, which makes a wrong-VOD match or a bonus segment visible at a
glance without reading a single digit.

**Frames must be cropped to where the timer actually is.** A fixed bottom-30%
strip — the Winter 2024 recipe — misses this event badly: nine flagged runs put
the clock at **50–62% of frame height**, and Mario Party 3's `55x20` box sits at
55%. The first review pass came back blank for those runs and looked like "no
timer on screen"; deriving each strip from the crop `batch` had already recorded
fixed all nine at no extra request cost. The crop is in `results.csv` already.

### Corrections — 13 of 23

**Read the estimate instead of the timer — 5 runs.** Every one calibrated to a
crop under 100px wide; see #71 below.

| run | OCR read | actual |
|---|---|---|
| Mario Party 3 — Blindfolded Showdown Match | `1:30:00` | `1:02:50` |
| Duolingo — First Chest (10 Random Languages) | `1:45:00` | `1:47:21` |
| Run Invalid — Showcase (Routing Competition) | `0:30:00` | `0:14:24` |
| Sonic Free Riders — Team Bid War | `0:30:00` | `0:23:57` |
| Milestone Madness #6 / #7 / #8 | `0:15:00` | no timer at all |

**The largest sampled reading landed before the finish — 6 runs.** The plateau
was outside the window or too short to hold, so the fallback took a frame from
the ramp. All six are small, plausible-looking undershoots, which is what makes
them dangerous.

| run | OCR read | actual |
|---|---|---|
| Sonic CD (2011) — Beat the Game (Sonic) | `0:17:19` | `0:21:49` |
| Horizon Chase Turbo — Summer Vibes | `0:21:14` | `0:27:09` |
| Citroën C4 Robot — Any% (Best of 3) | `0:10:51` | `0:15:42` |
| Crosscode — No Menu Glitches | `1:23:40` | `1:23:57` |
| Halo 2 Anniversary — Legendary | `1:33:20` | `1:33:23` |
| Super Mario Sunshine — True All Hundos | `3:52:55` | `3:53:15` |

**The `3`/`5` glyph confusion — 2 runs.** Present, but nothing like Winter
2024's eight.

| run | OCR read | actual |
|---|---|---|
| Age of Empires 2: Definitive Edition — Attila The Hun | `0:59:44` | `0:39:56` |
| Rate my Setup — Donate $10 and send an image! | `0:31:52` | `0:31:32` |

Rate my Setup is the textbook case, a tens-of-seconds `3` read as `5` worth
exactly +20s. Age of Empires 2 is the same fault in the tens-of-minutes column
(+20:00), and it was caught only because `0:59:44` is longer than its own
42-minute video.

**A timer reset inside the sampled window — 1 run.** `The Legend of Zelda: A
Link to the Past — Any% (w/ Major Glitches)` read `0:05:53` against a true
`0:02:39`. This is a two-runner row and the slot holds two attempts, so the
largest reading in the window belongs to the earlier one. Worth a human glance:
which of the two the archive should carry is a judgement about the row, not
about the OCR.

## Reads — Stream Two

| tier | n | outcome |
|---|---|---|
| high | 55 | shipped unreviewed |
| medium | 4 | all checked against frames |
| reject | 4 | all checked against frames |

**55 of 63 accepted without review — 87%**, matching Summer 2024's best. Exactly
**one** run reports `no stable plateau`. Stream Two is the cleanest schedule any
event has produced, and it is the same tool and settings that produced Stream
One's 82% on the same day's footage — the difference is the run mix, not the
reader.

Of the 8 flagged runs, **3 confirmed the OCR and 4 were corrected**; the eighth,
Small Soldiers, has no finish on camera.

| run | OCR read | actual | why |
|---|---|---|---|
| Pokémon White 2 — Any% | `3:30:00` | `3:18:28` | estimate read, `58x20` crop |
| Deliver Us Mars — Any% | `2:00:00` | `1:58:42` | estimate read, `63x22` crop |
| Disney's 102 Dalmatians — All Levels (OoB) | `0:28:00` | `0:22:00` | estimate read, `58x20` crop |
| Zelda: Twilight Princess — Low% | `14:55:44` | `14:35:44` | tens-of-minutes `3` read as `5` |

### Two multi-part runs, and the guard cannot see either

Both of Stream Two's `reject`s that were *not* estimate reads are single schedule
rows split across two VODs, where the timer carries the cumulative total and the
"longer than its own video" check therefore cannot hold:

- **Final Fantasy XIV — A Realm Reborn ($20%)** runs `22:42:06` across two
  11-hour uploads. Read off part 2, correctly, and rejected for exceeding its own
  11:25:45 video.
- **The Legend of Zelda: Twilight Princess — Low%** runs `14:35:44` across two
  7:22:33 uploads. This one is also the event's second `3`/`5` fault: the
  resolver answered `14:55:44`, exactly +20:00, while calibration's own candidate
  list shows the timer reading `14:35:44` and the estimate field reading
  `14:45:00` beside it.

Twilight Princess needed the resolver corrected as well. ESA published the run
three times — `[1/2]`, `[2/2]`, and a condensed "(Sped Up Slides)" edit — and
the search returned only the edit, whose 4:14:02 length matches neither part.
Repointing the row at `[2/2]` is what made the finish readable, and is the same
call as Final Fantasy XIV: **for a multi-part run, resolve to the part holding
the finish.**

## The estimate-ratio guard (#66) — this event inverts Winter 2024's proposal

Winter 2024 reversed five events of evidence by finding five true positives, and
proposed narrowing the lower bound from 0.4x to **about 0.22x**, on the grounds
that every correct rejection there sat at or below 0.21x and every false alarm at
or above 0.24x.

**This event's five lower-bound rejections split the other way round.** Four are
false alarms and one is a true positive — and the true positive is the *highest*
ratio of the five:

| run | read | ratio | reading | verdict on the guard |
|---|---|---|---|---|
| Thumper — Showcase | `0:05:16` | **0.08x** | right — 5:16 of a 70-minute slot | false alarm |
| Amnesia: The Bunker — Any% | `0:01:56` | **0.19x** | right — the whole run is a 5-minute VOD | false alarm |
| Yono and the Celestial Elephants | `0:05:00` | **0.20x** | right — a capped run, ends on `00:05:00` | false alarm |
| DuckTales — Any% (Best of Three) | `0:07:23` | 0.25x | right | false alarm |
| Zelda: A Link to the Past — Any% (w/ MG) | `0:05:53` | **0.37x** | **wrong** — true `0:02:39` | true positive |

Cutting at 0.22x, as Winter 2024 proposed, would therefore have been **exactly
backwards on this event**: it keeps all three rejections below the line (Thumper,
Amnesia, Yono — every one a correct time), and drops the only rejection that
caught a real error (A Link to the Past, at 0.37x).

The two events do not actually disagree about the mechanism, only about where it
lands on the ratio. Winter 2024's true positives were **reset clocks**, and so is
this event's: A Link to the Past is a two-runner slot holding two attempts, and
the largest reading in the window belongs to the earlier one. What varies is the
*ratio* a reset happens to produce, which depends on how long the bonus segment
ran — and it is not separable from a genuinely short run, because a Showcase
category and a reset clock look identical to a rule that only sees a ratio.

So the conclusion Winter 2024 reached is right and its proposed threshold is not:
**the signal to act on is the reset, not the ratio.** Winter 2024's own
improvement 3 — flag a value that *decreases* inside the sampled window —
identifies A Link to the Past and all six of Winter 2024's cases, and rejects
none of this event's four short runs. Running total for the lower bound across
all events is now **6 correct rejections against 20 false alarms.**

The upper bound is a different rule and did fire correctly once: Closing Speech's
`1:00:00` is 4.00x its `0:15:00` estimate, and there is no timer on that layout
at all. It was independently caught by the longer-than-video check.

## The "longer than its own video" guard has a false-positive mode

`TAS Showcase — TASBot plays...` read `0:48:28`, correctly — the montage shows
the clock frozen white at exactly that. It was rejected and dropped from the
export because 48:28 exceeds the video's own 44:53.

The cause is that **ESA's VOD starts after the run's timer did**, by about four
minutes. The guard's assumption — that a run cannot be longer than the video
containing it — holds only for a VOD cut to the whole run, and the multi-part
case in the README is not the only exception. Here a single-part VOD simply
begins late. A human answer was needed to publish a time the tool had read
perfectly.

## #65 (`equals_estimate`) — 10 fires across the event, 8 wrong and 2 right

| run | read | crop | verdict |
|---|---|---|---|
| Mario Party 3 | `1:30:00` | `55x20` | wrong — actual `1:02:50` |
| Duolingo | `1:45:00` | `60x22` | wrong — actual `1:47:21` |
| Run Invalid | `0:30:00` | `63x21` | wrong — actual `0:14:24` |
| Sonic Free Riders | `0:30:00` | `63x22` | wrong — actual `0:23:57` |
| Milestone Madness #6 / #7 / #8 | `0:15:00` | `44x16` | wrong — no timer on screen |
| Sonic The Hedgehog Classic Boss Shuffler | `0:50:00` | `168x50` | **right** — ticks to `00:49:59`, stops at `00:50:00` |

Stream Two adds four more, and splits the same way:

| run | read | crop | verdict |
|---|---|---|---|
| Pokémon White 2 | `3:30:00` | `58x20` | wrong — actual `3:18:28` |
| Disney's 102 Dalmatians | `0:28:00` | `58x20` | wrong — actual `0:22:00` |
| Deliver Us Mars | `2:00:00` | `63x22` | wrong — actual `1:58:42` |
| Nothing — 100% | `0:21:00` | `167x50` | **right** — ticks to `00:20:58`, stops at `00:21:00` |

Sonic Boss Shuffler and Nothing are this event's Sonic Spinball: time-capped or
short runs that genuinely end on a round number, kept because #65 demotes rather
than rejects. Three events running, the demotion-not-rejection decision has saved
a correct time — and this event saved two.

**And the crop separates all ten perfectly.** Every one of the eight wrong reads
calibrated to a box 44–63px wide; both correct reads calibrated to the modal
`167`/`168x50`.

## #71 — crop size is now 23 for 23 across three events

| crop width | runs (this event) | estimate-reads |
|---|---|---|
| 115–208 px (the timer) | 204 | **0** |
| 44–63 px (the `EST.` field) | 9 | **9** |

Nine tiny crops, nine estimate-reads, and no normally-sized crop was ever an
estimate-read. They are Milestone Madness #6/#7/#8 `44x16`, Mario Party 3
`55x20`, Closing Speech `57x21`, Pokémon White 2 `58x20`, 102 Dalmatians `58x20`,
Duolingo `60x22`, Run Invalid `63x21`, Sonic Free Riders `63x22` and Deliver Us
Mars `63x22`.

With Summer 2024's 5-for-5 and Winter 2024's 9-for-9, that is **23 tiny crops
across three events, 23 estimate-reads, and zero false positives across 466
normally-sized ones.** It also catches what `equals_estimate` structurally
cannot: Duolingo's true time is `1:47:21` against a `1:45:00` estimate, so a rule
comparing only values would have found nothing to suspect, and Closing Speech's
`57x21` flags a layout with no timer at all rather than a wrong number.

`batch` already records the crop. This remains the cheapest unimplemented win in
the tool.

## #67 fired, and Winter 2024's diagnosis is confirmed again

One frame grab failed with `moov atom not found`. The issue describes this as the
height fallback picking an uncuttable 240p; Winter 2024 found the real cause is
an **AV1** rendition, which `--download-sections` cannot cut. Pinning the AVC
itags — `-f 136/135/134/133` ahead of the height selector — fixed it on the
first retry, on a video where 480p and 720p both exist.

That is now two events where the AVC pin is the fix and the height fallback is
not the cause. The issue text should be corrected before someone implements what
it currently says.

## The wall

The wall is the story of this event. It went up **three times** across four
sittings, and roughly **600 yt-dlp invocations** were spent in total.

| sitting | requests before it went up | runs read |
|---|---|---|
| 1 | ~275 | 66 of 152 (Stream One) |
| 2 | ~85 | 58 more (Stream One, to 124) |
| 3 | ~50 | 18 of 63 (Stream Two) |
| 4 | did not go up | the remaining 26 S1 + 45 S2, plus both review passes |

Winter 2024 hit it once at ~460 and called that the most of any event. **This
event never got near that on a single sitting.** The first wall came at 275 and
the two after it came far sooner, which suggests the threshold is not a simple
per-session count — a recent history of refusals appears to lower it for the next
sitting. The fourth sitting then ran ~150 requests without a single refusal,
which fits the same picture from the other side: leave it alone long enough and
the budget comes back.

Everything was stopped rather than retried and no cookies were used. Each block
cleared on its own — the first in under 16 hours, the later ones faster — and
`--resume` means a resumed pass costs only what is left.

**Reading `batch`'s exit code is what makes this cheap.** Exit 75 says "blocked,
nothing wrong with the input", and on the third wall all six shards exited 75
with **zero non-wall failures**, so no time was spent looking for a bug that was
not there. The corollary matters too: a shard that exits **0 having read nothing
is not evidence the wall has lifted**, because `--resume` can satisfy it entirely
from work already done. One overnight probe exited 0 that way and had made no
network request at all; the real test is a shard that still has runs to fetch.

Two failures during the event looked like the wall and were not:

- **`Unable to download API page: [SSL: UNEXPECTED_EOF_WHILE_READING]`** hit two
  Stream Two runs and one frame grab. It is transient — both videos probed
  perfectly a minute later and then read `high` — so it is worth one retry before
  concluding anything.
- **`The page needs to be reloaded`** hit one frame grab. As the skill notes,
  this is the `n`-challenge solver, not a session problem; it cleared on retry.

### Seeding the metadata cache saved ~200 invocations

`analyse` calls `video.probe` for a title and duration `resolve` already recorded
off the same `ytsearch` that found the video, so every run cost two YouTube
requests where one would do. Measured on eight ESA VODs, the search duration is
the true duration **rounded up by exactly one second** — and rounding up is the
safe direction, because the tail window still runs to the real end of file.

Writing `<id>.meta.json` into the cache from `resolved.csv` before the batch
therefore removes one request per run at no cost to the read: 141 on Stream One
and 62 on Stream Two, **about 200 across the event**, on a budget where the wall
arrived at 275. This generalises Winter 2024's improvement 5, which proposed the
same saving for the review pass only.

One caveat worth recording: the +1s rule held for all eight ESA uploads tested,
but the Japanese Restream's Grand Theft Auto V reported a search duration **59
seconds longer** than its true length. Over-reporting is harmless here; a
third-party re-upload is where the rule is least reliable.

## Runs that need a second pair of eyes

Three runs ship on a time nobody has confirmed. Two are known lower bounds and
one is a genuine judgement call:

- **Small Soldiers — Any%** (Stream Two) — `0:45:53`. The VOD ends with the clock
  still ticking at `00:45:47`, so no finish exists on camera.
- **Milestone Madness #5 — Unlocked at $60,000** (Stream One) — `0:17:27`. The
  clock is still running at exactly that value when the stream cuts to the
  "coming up" card.
- **Milestone Madness #3 — Unlocked at $30,000** (Stream One) — `0:17:08`. The
  re-upload ends before the segment does; the last frame visible reads
  `00:16:23` and rising.

One more is worth a human decision rather than a re-read:

- **The Legend of Zelda: A Link to the Past — Any% (w/ Major Glitches)** ships
  `0:02:39`, the value frozen on screen at the end of the slot. It is a
  two-runner row and the slot holds two attempts — the earlier one reaching
  `0:05:53` — so which of the two the archive should carry is a question about
  the row, not about the reading.

**Six scheduled rows ship with no time, none of them recoverable:**

- **Milestone 1** (Stream One) — a filler row with no category and no VOD.
- **DJ Night** (Stream One) — ESA published no VOD. Confirmed by the Closing
  Speech footage, which ends on a `SETTING UP FOR / DJ Night` card.
- **Taskmaster** (Stream One) — a stage segment with no overlay at all.
- **Glorious Typing Competition** (Stream One) — likewise no overlay.
- **Closing Speech** (Stream One) — the layout carries no timer, only the next
  run's estimate. Same as Winter 2024's Closing Speech.
- **Milestone Madness #6 / #7 / #8** (Stream One) — the only copy is a re-upload
  whose tail holds a different segment with no ESA panel, so nothing on camera
  supports a time. Its `0:15:00` was blanked by hand rather than answered `skip`,
  because `skip` sets `source=human-skip` and would have published the very value
  the guards were withholding.

Three runs trip the release script's over-eight-hours warning and all three are
real: **Final Fantasy XIV** `22:42:06` and **Twilight Princess** `14:35:44`, both
cumulative totals across two-part VODs, and **Final Fantasy IX — Any%** at
`9:23:41` inside a 9:26:02 video, backed by a 10-frame plateau and 40 ramp
frames.

## Improvements worth making

1. **Record the channel in `resolve`, and flag a match that is not ESA's own
   upload.** Two separate third-party channels matched ten rows across this
   event, one of them at `tag-game-runner(1.0)`, and no artefact the tool
   produces distinguishes them from ESA's uploads. `yt-dlp`'s flat-playlist
   search entries already carry `channel`; `video.search()` simply drops the
   field. This is the one resolver error class that a confident read cannot
   expose, and here it happened to be benign only because both channels
   rebroadcast ESA's own overlay.
2. **Seed the metadata cache from `resolved.csv` before every batch.** ~200
   requests saved on this event against a wall that arrived at 275, for a
   duration that is provably an over-estimate by one second. This is the single
   highest-value change available.
3. **Flag a calibrated crop much smaller than the event's modal crop (#71).**
   Now 20 for 20 across three events with zero false positives across 406
   normal crops. Still needs no new data.
4. **Do not narrow #66 to 0.22x as Winter 2024 proposed — detect the reset
   instead.** On this event a 0.22x cut keeps every false alarm (Thumper 0.08x,
   Amnesia 0.19x, Yono 0.20x — all correct times) and drops the guard's only
   true positive (A Link to the Past, 0.37x). Both events' true positives are
   reset clocks, so Winter 2024's own improvement 3 — flag a value that
   *decreases* inside the sampled window — is the rule that catches them without
   rejecting a single genuinely short run.
5. **Derive the review montage's crop band from the crop `batch` recorded**,
   rather than using a fixed bottom strip. Nine of this event's flagged runs put
   the timer at 50–62% of frame height, where a bottom-30% strip sees nothing and
   the run looks like it has no clock.
6. **Exempt a VOD that starts mid-run from the "longer than its own video"
   guard**, or at least report it separately. TAS Showcase's `0:48:28` was read
   perfectly and dropped because ESA's upload begins four minutes after the timer
   did.
