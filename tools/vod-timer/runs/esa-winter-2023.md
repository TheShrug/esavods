# ESA Winter 2023 — backfill

Issue #48. Two Horaro schedules (`2023-winter1`, `2023-winter2`), tag
`#ESAWinter23`, shipped as `ESA 2023 Winter (One)` and `ESA 2023 Winter (Two)`.

- **Settings**: `--height 480 --tail 600 --step 12`, six shards per schedule,
  one schedule at a time.
- **157 schedule rows**, against Summer 2023's 217 and Winter 2024's 164. No
  filler rows at all — every row on both schedules has a category, which is the
  first event where that is true.
- **Outcome**: **155 of 157 rows live with a time.** 126 read `high`, 27 were
  resolved from frames by hand, and **2** ship on an unconfirmed reading. Two
  rows carry no time and neither is recoverable.
- The bot wall went up **three times**, at ~220 requests, then after only ~122,
  then once more at the very end. The first two cleared in about 90 minutes
  each. See "The wall".

## Outcome

| | Stream One | Stream Two | event |
|---|---|---|---|
| schedule rows | 110 | 47 | **157** |
| shipped with a time | 109 | 46 | **155** |
| `high`, shipped unreviewed | 85 | 41 | **126** |
| resolved from frames (`human`) | 22 | 5 | **27** |
| shipped unconfirmed | 2 | 0 | **2** |
| no time, not shipped | 1 | 1 | **2** |

**126 of 157 accepted without review — 80%**, between Winter 2024's 71% and
Summer 2023's 82%. Stream Two again read better than Stream One (87% against
77%), the same split Summer 2023 saw, and again on the same days' footage with
the same settings — the difference is the run mix, not the reader.

## Resolution

No ESA timing sheet exists for 2023, and neither schedule links a VOD, so
`slot-exact` and `horaro-link` are both unavailable and the whole event runs on
title search.

| how | Stream One (110) | Stream Two (47) | total (157) |
|---|---|---|---|
| `tag-game-runner` | 89 | 46 | **135** |
| `tag-game` | 11 | 0 | **11** |
| `weak` | 8 | 1 | **9** |
| resolved by hand | 2 | 0 | **2** |

**Two duplicate video ids**, both caught before a frame was downloaded: one
within Stream One and one across the two streams. Both were `weak` matches
landing on a video another row had already claimed at `tag-game-runner(1.0)`,
which is the shape a duplicate takes when the resolver has nothing to match and
reaches for the nearest thing.

### `weak` is not a synonym for "wrong" on this event

This is the finding that most contradicts the previous four events. Summer 2024
had every `weak` wrong; Summer 2023 had all eleven wrong. **Here 7 of 9 `weak`
matches were the correct video**, and the two that were wrong were wrong for
reasons the tier does not name.

The seven correct ones are all the same thing: ESA published the run under a
title that breaks their own `Game [Category] by Runner - #tag` convention, so
`gscore` punished it even though the video was right.

| row | title ESA actually used | why it scored low |
|---|---|---|
| Goat Simulator 3 | `Goat Simulator 3 Beat the Farmer by Lordmau5 and Riekelt   #ESAWinter23 v1742222633` | trailing `v1742…` means `TITLE_TAG` never strips the hashtag, so every word of it counts against precision |
| PS5 SSD Upgrade | `PS5 SSD Upgrade Any% by Aeshmah, rebeldragon95, 97ames, Nashlax and DreeGon   #ESAWinter23 v17448523` | same, plus five runners' names |
| Planet Cube: Edge | `Planet Cube: Edge 4 Stages by nashlax and Edenal #ESAWinter23` | no bracket, so the category stays in the game field |
| Vampire Survivors | `Vampire Survivors Crowd Control by nashlax and Argick #ESAWinter23` | same |
| Lunistice | `Lunistice Any% Glitchless, Hana by Lordmau5 and MoD366   #ESAWinter23` | same |
| Sonic Triple Trouble (16-Bit) | `Sonic Triple Trouble (16-Bit) - #ESAWinter23` | `TITLE_PARENS` eats `(16-Bit)` as the category, so the game name loses a word it needs |
| tERRORbane | `#ESAWinter23 tERRORbane Any% Speedrun` | hashtag **leads** the title, so `TITLE_TAG`'s `$`-anchored pattern never strips it |

Every one of these was confirmed from frames or by the ESA overlay being present
in the read. The practical lesson is that **`weak` measures title convention,
not correctness**, and on an event where ESA's titling is loose it is a poor
proxy. Winter 2023's uploads are visibly less consistent than 2024's or 2025's.

### The two rows that were genuinely wrong, and neither is a scoring failure

- **`BONUS GAME: Dark Souls`** matched Darksiders 2 at `weak(0.303)`. ESA *had*
  published it, as `Dark Souls [Any%] by catalystz - #ESAWinter23`, which would
  have scored 1.0. It was never in the candidate set: `search_query()` sends the
  Game cell verbatim, and horaro's cell says `BONUS GAME: Dark Souls`, so the
  query carries two tokens no ESA title contains. Searching `Dark Souls
  #ESAWinter23 catalystz` returns it first.

  **This is the same failure as Summer 2023's LEGO Star Wars, and it is now
  twice** — retrieval, not ranking. #75 fixed ranking. The query is still one
  shot, still verbatim, and a schedule-side prefix (`BONUS GAME:`,
  `Milestone Madness #3`) is enough to lose a run outright.

- **`Pokémon Scarlet/Violet`** matched Pokémon Brilliant Diamond at `weak(0.5)`
  because **ESA never published it**. The only copy is a Russian re-upload.

### A third-party channel again — RUSC — and again it is ESA's own footage

Three rows resolve to **RUSC**, a Russian restream channel that copies ESA's
title convention (`[RU] <Game> [<Category>] от <Runner> - #ESAWinter23`) and
carries the real hashtag. Summer 2023 found the same thing with Iikodane and
Japanese Restream; `resolve` still records no channel, so nothing downstream
distinguishes these from ESA's own uploads.

| row | video | read | verdict |
|---|---|---|---|
| Winx Club | `sem6uXumX-4` | `0:44:42` high | ESA's overlay, intact — confirmed from a frame |
| de Blob | `P_o5cxsnaAY` | `1:04:31` high | ESA's overlay |
| Pokémon Scarlet/Violet | `l_T_s6A_-nA` | `5:32:53` high | ESA's overlay; the only copy that exists |

As on Summer 2023, these ship. The channel is third-party; the footage and the
timer are ESA's, and for Scarlet/Violet a re-upload is the only reason the run
is on the site at all.

**One new detail worth recording**: the search-reported duration for ESA's own
uploads is the true length rounded up by exactly 1s, but RUSC's Scarlet/Violet
over-reported by **58 seconds** (20153 against 20095). Summer 2023 saw the same
thing on a re-upload (+59s). Two events, two third-party channels, both
over-reporting by about a minute — the +1s rule is a property of ESA's uploads,
not of YouTube search.

## Reads

| tier | Stream One | Stream Two |
|---|---|---|
| high | 85 | 41 |
| medium | 14 | 5 |
| low | 2 | 0 |
| reject | 7 | 0 |
| no read | 2 | 1 |

**Stream Two produced no `reject` and no `low` at all** — 41 `high` and 5
`medium` out of 47. That is the cleanest schedule any event has produced,
beating Summer 2023's Stream Two.

23 of 155 reads report `no stable plateau; fell back to the largest reading`,
comparable to Summer 2023's 15 on a larger event.

### 31 flagged, 31 resolved from frames — 20 corrections, 7 confirmations

Four were not answerable from any reading (below). Of the 27 where a value could
be read off the screen, **20 were corrections and 7 confirmed the OCR exactly** —
a worse hit rate than Summer 2023's 10-of-23 confirmed, and the reason is that
this event's dominant fault is not a glyph error but a *short* read.

The twenty corrections account for themselves exactly:

| cause | runs |
|---|---|
| truncated download, read from the start of the window (#63) | **11** |
| `3`/`5` glyph confusion | 3 |
| read the estimate, on a tiny crop (#71) | 3 |
| calibrated onto neither the timer nor the estimate | 1 (Gato Roboto) |
| the tail held a different run's clock | 1 (Metroid Dread) |
| no plateau, fell back to a value above the truth | 1 (Portal 2) |

**The largest sampled reading landed before the finish — 11 runs.** This is the
single biggest failure mode of the event, by a wide margin, and every one is a
plausible-looking undershoot rather than an obvious miss.

| run | OCR read | actual | short by |
|---|---|---|---|
| Bomberman 64 — Any% (Normal) | `0:25:51` | `0:31:47` | 5:56 |
| I Am Jesus Christ — Prologue | `0:24:53` | `0:30:20` | 5:27 |
| Pokémon Red/Blue — Any% (No Item Underflow) | `0:18:36` | `0:24:29` | 5:53 |
| LEGO Star Wars II (DS) — All Levels (1.0) | `0:43:43` | `0:49:54` | 6:11 |
| Lost Judgment — The Kaito Files | `0:46:08` | `0:53:05` | 6:57 |
| StarCraft: Remastered — Any% (Terran) | `0:37:58` | `0:42:42` | 4:44 |
| Super Mario Odyssey — Any% | `1:41:09` | `1:46:04` | 4:55 |
| Sonic 3D in 2D — Beat The Game (Sonic) | `0:26:28` | `0:31:08` | 4:40 |
| Streets of Rage 4 — Any% (Cherry, Easy) | `0:46:05` | `0:50:39` | 4:34 |
| Quake Mission Pack 1 — Easy Run | `0:02:26` | `0:09:12` | 6:46 |
| No Time To Explain Remastered — 100% | `0:36:17` | `0:36:28` | 0:11 |

**Ten of the eleven are short by 4:34 to 6:57**, and the cause is not what it
first looks like. It is not `--tail` being too short: every one of these
finishes lands **86 to 391 seconds before the end of its video**, so the frozen
clock sat inside the 600-second window and was sampled 7 to 32 times over.

Working backwards from each read instead, the last frame that produced a usable
value is only **50 to 100 seconds into the window**, and the remaining 400 to
700 seconds produced nothing at all. That is the signature of a **truncated
download** - `--download-sections` returning far less than the span it was
asked for - and it is #63, which Summer 2022 found on two runs and which the
README already warns "still passes silently".

Three of these eleven were independently reproduced during this event's own
frame-grab pass: LEGO Star Wars II, Sonic 3D in 2D and Streets of Rage 4 all
came back short when asked for a 300-second window, as did Portal 2, and each
needed a second request naming a much narrower span before the end of the run
was visible at all. The same videos truncate repeatably.

`MIN_CLIP_BYTES` cannot catch this. It rejects a clip under 512 KB, and 50
seconds of 480p video is several megabytes - comfortably past the bar while
holding one twelfth of the requested footage. **The check has to be on the
clip's duration against the window that was asked for, not on its size.**

The reason these land as `medium` rather than `reject` is that a short ramp
still looks like a consistent ramp: the frames that did arrive agree with each
other perfectly, so one of the two confirmations passes and the tier stays
mid-table. Nothing in the result says "you only saw a twelfth of what you asked
for".

**The `3`/`5` glyph confusion — 3 runs.** Present but not dominant, as on Summer
2023.

| run | OCR read | actual | column |
|---|---|---|---|
| Resident Evil 5 — NG+ (No 1-1, No Rocket, AMA) | `1:58:46` | `1:38:46` | tens of minutes (+20:00) |
| The Elder Scrolls V: Skyrim — Main Quest | `1:19:54` | `1:19:34` | tens of seconds (+20s) |
| Crash Bandicoot 4 — All Clear Gems | `2:37:55` | `2:37:35` | tens of seconds (+20s) |

**Read the estimate instead of the timer — 3 runs**, all on a tiny crop; see
#71 below.

| run | OCR read | actual | crop |
|---|---|---|---|
| Mirror's Edge — Any% | `10:40:00` | `0:38:53` | `63x22` |
| Mario Kart 8 Deluxe — 48 Tracks (200cc) | `1:30:00` | `1:30:37` | `60x22` |
| Frog Detective 3 — Any% | `0:40:00` | `0:35:21` | `63x22` |

Mirror's Edge is the clearest case the tool has produced: the screen reads
`00:38:53` and the panel prints `00:40:00` beside it as the estimate, and the
OCR returned `10:40:00` — the estimate with a mangled leading digit.

**A calibration that found neither — 1 run.** Gato Roboto calibrated to
`99x21` at (497,316), which is *above* where its timer actually sits; it read
`0:24:56` against a true `0:26:08`, and the value is not the estimate either
(`0:28:00`).

### The tail held a different run — Metroid Dread

The most valuable single correction of the event, and the one no artefact would
have exposed. `Metroid Dread — Any% Unrestricted (Normal, No Turbo, Digital)`
read `0:12:45`; the true time is **`0:55:24`**.

The last ~16 minutes of that VOD are a **bonus boss-rush run** with its own
reset clock, and ESA's panel names it: `Boss... no DREAD Rush / Switch /
00:12:00`. Every frame in the sampled window shows a confident, correctly-read,
completely wrong clock. Walking backwards to `dur-1235` finds the panel showing
the schedule's own category and the clock frozen white at `00:55:24`.

This is the third event to hit the reset-clock case (Summer 2025's Super Mario
Bros. 3, Summer 2023's A Link to the Past) and the first where the layout
*names the different run on screen*, which is what made it diagnosable from one
frame.

### The clock is yellow while running and white once stopped

Same tell as Winter 2024 and Summer 2023, and it decided several reads here.
Jubeat's `0:34:54` is yellow in the final frame, which is how we know the VOD
ends before the run does.

The layout also prints the run's name, category, platform and estimate beside
the clock in every frame. That is what caught Metroid Dread, and it is worth
saying plainly: **on this event a single frame is usually enough to settle a
run, because the frame carries its own metadata.**

## #71 — crop size, and a sharper way to measure it

Now **26 for 26 across four events**. But this event contains the case that
breaks the width-based rule Summer 2023 proposed, and supplies a better one.

Summer 2023's rule was "44–63px wide is the estimate field". Winter 2023 has
five crops below the modal `168x50`, and width alone mis-sorts two of them:

| run | crop | area vs modal | verdict |
|---|---|---|---|
| Mirror's Edge | `63x22` | **16%** | estimate read — wrong |
| Frog Detective 3 | `63x22` | **16%** | estimate read — wrong |
| Mario Kart 8 Deluxe | `60x22` | **16%** | estimate read — wrong |
| Gato Roboto | `99x21` | **25%** | mis-calibration — wrong |
| Winx Club (RUSC) | `104x42` | **52%** | **correct** — a scaled ESA panel |
| de Blob (RUSC) | `127x38` | **57%** | **correct** — a scaled ESA panel |
| Pokémon Scarlet/Violet (RUSC) | `152x45` | **81%** | **correct** — a scaled ESA panel |

A width cut at 100px would flag Gato Roboto correctly but would also have to
clear Winx Club at 104 by four pixels. **Area against the event's modal crop
separates all seven cleanly**: every wrong one is at or below 25%, every correct
one at or above 52%. There is no threshold in raw width with that much daylight
around it.

The reason is that a **third-party re-upload scales ESA's whole panel
uniformly**, so its timer crop is smaller than the modal one without being the
wrong element. Any rule stated in absolute pixels will keep meeting this case as
long as re-uploads keep filling gaps ESA left.

## #66 — the estimate-ratio guard, and why its false-alarm rate is overstated

Six rejections fired on the ratio this event. **Three were true positives** —
much better than the running record — but the more useful finding is *why* two
of the three false alarms fired.

| run | read | ratio | verdict |
|---|---|---|---|
| Metroid Dread | `0:12:45` | 0.20x | **true positive** — bonus run's reset clock |
| Quake Mission Pack 1 | `0:02:26` | 0.19x | **true positive** — read fell before the finish |
| Mirror's Edge | `10:40:00` | 16.00x (upper) | **true positive** — estimate read |
| PS5 SSD Upgrade | `0:04:43` | 0.16x | reset clock, unanswerable (see below) |
| IKEA Billy Assembly | `0:06:16` | 0.10x | false alarm — read is exactly right |
| No More Papers Please | `0:07:24` | 0.18x | false alarm — read is exactly right |

**Both false alarms compare against the wrong number.** The ESA layout prints
its own estimate beside the clock, and for these two rows it disagrees with
horaro:

- IKEA Billy Assembly — horaro `1:00:00`, **screen `00:10:00`**. True ratio 0.63x.
- No More Papers Please — horaro `0:40:00`, **screen `00:08:00`**. True ratio 0.93x.

Horaro's `length_t` is the **slot**, and for an IRL or showcase segment the slot
includes setup, teardown and interview time that the run's own estimate does
not. Against the screen's estimate neither row is anomalous at all.

So the running tally of the guard being "0 for 13" and then "6 correct against
20 false alarms" is measuring the guard against a number it was never given.
This does not rescue the threshold — Summer 2023's argument that **the reset is
the signal, not the ratio** still holds, and two of this event's three true
positives are reset clocks. But it does mean the guard's inputs are wrong for a
particular class of row, and that is fixable independently of the threshold: the
layout's own estimate is on screen in every frame the tool already downloads.

## #67 — fired twice, and the AVC pin fixed both

Two runs failed with `moov atom not found`: `No More Papers Please` (S1) and
`Resident Evil (1996)` (S2). Adding `--ytdlp-arg=-f --ytdlp-arg=136/135/134/133`
ahead of the height selector fixed both on the first retry, and Resident Evil
(1996) then read `0:47:55` at `high` with a 15-frame plateau.

**Three events running, the AVC pin is the fix and the height fallback in the
issue text is not the cause.** The issue should be corrected before someone
implements what it says.

## The "longer than its own video" guard — three saves, all recoverable

Three Stream One runs were dropped from the first export for reading longer than
their own video, and **all three were real runs whose OCR value was wrong**, not
multi-part VODs:

- Mirror's Edge `10:40:00` out of `0:41:48` — true `0:38:53`
- Resident Evil 5 `1:58:46` out of `1:42:33` — true `1:38:46`
- Portal 2 `0:59:57` out of `0:44:59` — true `0:40:09`

The guard did exactly its job, and because a human answer is exempt from it all
three now ship with correct times. Unlike Summer 2023's TAS Showcase, no run
this event was lost to a false positive on that check.

## The wall

Twice, and the second came far sooner than the first — the same shape Summer
2023 recorded.

| sitting | requests before it went up | outcome |
|---|---|---|
| 1 | ~220 (157 resolve + ~15 by hand + ~46 batch) | S1 35 of 110 |
| 2 | ~122 (75 S1 + 47 S2) | S1 finished, S2 35 of 47 |
| 3 | ~40 | S2 finished, every frame grab, both review passes |

The first two blocks cleared in **about 90 minutes**, faster than Summer 2023's
2.5 to 16 hours. A third went up at the very end of the event, on a single
diagnostic re-read after roughly 40 frame-grab requests, and was not waited out
— the event was already complete. Everything was stopped rather than retried and
no cookies were used at any point.

### Exit 75 does not fire on a small shard, and that is a real gap

The second wall refused **12 of Stream Two's 47 runs and every shard still
exited 1.** `--bot-wall-limit` counts *consecutive* failures within one shard;
47 rows across six shards is eight rows each, so no shard ever saw five in a
row. The batch reported "finished, some runs were unreadable" — which is the
message that means *don't* back off — at the exact moment backing off was the
right move.

Summer 2023's lesson was that reading the exit code is what makes a wall cheap.
That holds, but it only works while shards are large enough for the counter to
reach its limit. **The limit should scale with the shard, or the counter should
be a rate rather than a run.** Re-running the remaining 12 with
`--bot-wall-limit 2` behaved correctly.

### Seeding the metadata cache removed 152 requests

Implemented this event as `vodtimer seed` (see the tool README): 106 on Stream
One and 46 on Stream Two. Against a wall that arrived at ~220 total requests,
this is the difference between finishing Stream One in two sittings and
finishing it in four — the resolve pass alone spends 157, so without seeding the
first wall would have landed before Stream One's batch had read 20 runs.

The saving is exactly what #47 measured and predicted. Nothing about it was
surprising in use, which is the point.

## Runs that need a second pair of eyes

**Two runs ship on a time nobody has confirmed:**

- **Jubeat — Showcase** (Stream One) — `0:34:54`. The clock is yellow, still
  running, in the last frame before the VOD ends, so no finish exists on camera.
  A lower bound.
- **PS5 SSD Upgrade — Any%** (Stream One) — `0:04:43`. This is a five-runner
  segment where the timer **resets for each runner** — sampled frames show
  `00:00:00`, `00:00:48`, `00:03:05` and `00:01:33`, all yellow — and the VOD
  ends mid-attempt. There is no single value that represents the row. Which of
  the five attempts the archive should carry, if any, is a question about the
  row rather than about the reading; `0:04:43` is the largest value the tool saw.

**Two scheduled rows ship with no time, neither recoverable:**

- **Closing Speech** (Stream One) — the layout is an intermission/prize card
  with no timer at all. Same as Winter 2024 and Summer 2023.
- **RedCat Haunted Castle** (Stream Two) — a bare two-camera IRL layout with a
  name bar and no clock anywhere, checked five minutes apart.

Neither was answered `skip`: `skip` sets `source=human-skip`, which would
publish whatever value the guards were withholding.

No run trips the release script's over-eight-hours warning, and no VOD is used
by two runs.

## Improvements worth making

1. **Reject a clip whose duration falls short of the window that was asked
   for (#63).** Eleven runs — the largest single failure class of the event, and
   more than a third of everything flagged — read a value from the first 50-100
   seconds of a 600-second window because the download returned only that much.
   `MIN_CLIP_BYTES` passes them: 50 seconds of 480p clears 512 KB easily. The
   clip's *duration* is already known to ffmpeg and is the honest test. Failing
   loudly here would also make the retry obvious, since asking again for a
   narrower span near the end works — that is how all eleven were recovered.
2. **State #71's rule as area against the event's modal crop, not absolute
   width.** This event's seven sub-modal crops split perfectly at 25% vs 52% of
   modal area, and mis-sort under any width threshold, because a third-party
   re-upload scales ESA's whole panel uniformly.
3. **Scale `--bot-wall-limit` to the shard size.** Twelve refusals across six
   eight-row shards produced six exit-1s, and exit 1 is the code that says
   "nothing is wrong, carry on".
4. **Read the estimate off the layout instead of off horaro for the ratio
   guard.** Both of this event's false alarms compared a correct time against
   horaro's *slot* length, which for IRL and showcase rows is six times the
   run's own estimate. The right number is printed on screen in every frame the
   tool already has.
5. **Record the channel in `resolve`** — unchanged from Summer 2023's first
   improvement, and a third channel (RUSC) matched three rows here. Still no
   artefact distinguishes a mirror from ESA's own upload.
6. **Give `search_query()` a second attempt when the first returns nothing
   tagged.** `BONUS GAME: Dark Souls` is Summer 2023's LEGO Star Wars again:
   ESA published the run, the query never retrieved it, and a query built from
   the game name plus the runner finds it first. #75 fixed ranking; retrieval is
   still one verbatim shot.
