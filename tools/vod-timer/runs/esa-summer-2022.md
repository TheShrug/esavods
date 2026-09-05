# ESA Summer 2022 - validation run

Not a backfill. This event is one of the four for which ESA published real run
timings, so it was run end to end purely to measure the tool against truth.

- **Source**: `estimate-accuracy-model/data/run-timings/esa-summer-2022.csv`,
  where `Actual Time` is `TimerEnd - TimerStart` from nodecg-speedcontrol.
- **Settings**: `--height 480 --tail 600 --step 12`, six shards.
- **Wall time**: 1h 59m 47s for 133 runs. Resolution took a further ~4 min.

## Resolution

130 of 133 `slot-exact`, 2 `title`, 1 `weak`, and no duplicate video ids. The
slot-length check - VOD duration equals `EndTimestamp - StartTimestamp` - is
what makes this so clean, and it is exactly what a backfill event will not
have.

## Reads

| tier | n | within 1s | within 2s | wrong |
|---|---|---|---|---|
| high | 108 | 102 | 107 | 1 |
| medium | 8 | 1 | 1 | 7 |
| low | 2 | 0 | 0 | 2 |
| reject | 15 | 1 | 1 | 14 |

`high` is right 107/108 (99.1%) and covers 81% of the event. 24 of the 25
non-`high` results are genuinely wrong, so the tier is separating real signal.

Delta distribution for `high` is an offset, not a spread: 71 at -1s, 30 exact,
1 at +1s, 5 at -2s, 1 outlier.

## What went wrong, and what to change

1. **Tens-of-minutes `3` read as `5`** - seven rejects, each exactly +20:00 out.
   Inconsistent between frames, so no plateau forms and the resolver falls back
   to the largest reading, which is the inflated one. All seven were caught by
   the duration guard.
   *Tested and rejected*: switching the fallback from `max` to the mode. On
   Castlevania: Circle of the Moon the frozen clock reads `0:51:32` five times
   against `0:31:32` twice, so the mode is wrong too.
   **Open fix**: restrict plateau candidates to values inside the ramp band.
   The ramp there is clean (`0:30:26 ... 0:31:26`) and predicts `0:31:32`, the
   truth. This is the highest-value change outstanding.
2. **Short runs lose calibration to the estimate** - Golden Sun, 41s of run in
   an 8:44 slot, read `0:15:00`, its estimate exactly. Consider requiring the
   winning candidate to have ticked at least N times before trusting it, and
   flagging rather than answering when nothing ticks.
3. **The one `high` disagreement was not an OCR error.** Mega Man 8 (Crowd
   Control): sheet 1:53:25, screen 1:45:06, and the raw timestamps show the
   499s gap is the timer paused or restarted. This raises a question the
   backfill has to answer: when the two disagree, which one is `runs.time`?

## Bugs fixed during the run

- HLS formats cannot be range-cut; yt-dlp exited 0 after writing 257 bytes.
- `Path.with_suffix()` ate the cache key, so every clip re-downloaded.
- `batch` wrote results only at the end, losing progress on interruption.
- Interrupted downloads left truncated clips that passed the size check.

## Throughput

YouTube throttles per connection at ~77 KB/s. Six parallel containers measured
546-779 KB/s aggregate. `android_vr` (progressive format 18, usually
unthrottled) needs a PO token and returns 403, so it is not an option.

---

# ESA Summer 2022 - backfill

Issue #49, and the last of the twelve. Everything above this line is the 2022
**validation** run and is left exactly as it was: it is the origin of the
accuracy claims quoted across the other issues, and it predates #62, #65 and
#75. This section is a fresh read of the whole event with the current tool.

Two Horaro schedules (`2022-summer1`, `2022-summer2`), tag `#ESASummer22`,
shipped as `ESA 2022 Summer (One)` and `ESA 2022 Summer (Two)`.

- **Settings**: `--height 480 --tail 600 --step 12`, six shards per schedule,
  one schedule at a time.
- **202 schedule rows** - 131 and 71. The largest event in the backfill.
- **Outcome**: **200 of 202 rows live with a time.** 163 read `high` and shipped
  unreviewed, 37 were resolved from frames by hand, and **none ships on an
  unconfirmed reading**. The two rows with no time are the Opening and Closing
  Speeches, whose layout carries no timer at all.
- The bot wall went up **twice**, at ~206 requests and again 62 reads later.

## Outcome

| | Stream One | Stream Two | event |
|---|---|---|---|
| schedule rows | 131 | 71 | **202** |
| shipped with a time | 129 | 71 | **200** |
| `high`, shipped unreviewed | 100 | 63 | **163** |
| resolved from frames (`human`) | 29 | 8 | **37** |
| shipped unconfirmed | 0 | 0 | **0** |
| no time, not shipped | 2 | 0 | **2** |

**163 of 202 accepted without review - 81%**, the same share the validation
measured. Stream Two again read better than Stream One (89% against 76%) on the
same days' footage with the same settings, so the difference is the run mix.

## The point of doing this event last: scoring every shipped time

ESA published `Actual Time` for **Stream One only** -
`estimate-accuracy-model/data/run-timings/esa-summer-2022.csv`, 134 rows against
that schedule's 131. Stream Two has no sheet and had never been read before, so
nothing in this section covers it. The sheet carries its own ids rather than
Horaro's, so the two were joined by row order; the game names align 131-for-131
with three sheet rows left over (see "Three runs ESA timed that the schedule
never listed").

### What actually shipped

| tier | shipped | within 2s | further out |
|---|---|---|---|
| `high` | 100 | 99 | 1 |
| `human` | 29 | 26 | 3 |
| **total** | **129** | **125** | **4** |

**Every one of those four was checked frame by frame, and in all four the screen
is right and the sheet is measuring something else.** No shipped time on this
event is wrong.

| run | shipped | sheet | what the frame shows |
|---|---|---|---|
| GeoGuessr - A Diverse World (25k) | 0:25:36 | 0:45:21 | Timer froze white at `00:25:36`; the crew then reset it for the No Labels incentive, which is what the tail holds. The sheet spans both. |
| Mega Man 8 - Crowd Control | 1:45:06 | 1:53:25 | Screen reads `01:45:06`, exactly the OCR's answer. The 499s is the timer paused. Independently confirms the validation's reading of this run. |
| Batman: Arkham Asylum - Any% | 1:08:54 | 1:01:48 | Screen reads `01:08:54`, frozen at both 20s and 5s before the end - inside a VOD only 1:04:40 long. The upload is trimmed, so a real time can exceed its own video. |
| James Pond 2 - Any% | 0:30:43 | 0:33:12 | Screen frozen white at `00:30:43` from 6:40 before the end. A "Bonus run: Plushie from the Sky!" follows, on a reset clock. |

### How many would have shipped wrong with nobody reviewing

This is the number the whole exercise is for. The first release went out
**before** any review, exactly as step 3 prescribes - 122 Stream One runs, on the
tool's own reading of every one. Scored against the sheet:

| tier | shipped | within 2s | further out | genuinely wrong |
|---|---|---|---|---|
| `high` | 101 | 99 | 2 | **1** |
| `medium` | 16 | 5 | 11 | 11 |
| `low` | 4 | 1 | 3 | 3 |
| `reject` | 1 | 0 | 1 | 1 |
| **total** | **122** | **105** | **17** | **15** |

Two of the seventeen are the sheet, not the read - Mega Man 8 and James Pond 2
above - which is why "further out" and "genuinely wrong" differ.

**So: 15 of 122, or 12% of the event, would have carried a wrong time if nobody
had looked.** But that is almost entirely outside the `high` tier:

- **`high` was right 100 times out of 101 - 99.0%.** The single error is Metroid:
  Spooky Mission, shipped `0:35:56` against a screen reading `00:35:36`: the
  tens-of-seconds `3` read as a `5`, the glyph confusion the README already
  names, worth exactly `+20s` because of the column it sat in.
- **Everything below `high` was wrong 14 times out of 21 - 67%.**

That is the retroactive calibration the eleven sheet-less events needed. Shipping
`high` unreviewed costs about one wrong run in a hundred. Shipping anything below
it unreviewed costs two in three - and the eleven events before this one did ship
the low tiers unreviewed wherever a flagged run was never hand-resolved. The tier
is not a hint; it is the whole of the tool's accuracy claim.

The `high` delta distribution is still an offset rather than a spread: 40 exact,
78 at -1s, 5 at -2s, 1 at +1s. That is the overlay's floored value against the
sheet's whole unix seconds, not error.

## Resolution

Both schedules were resolved from Horaro, not from the sheet, because only the
Horaro path carries the `Scheduled`, `Platform` and `Players` the exporter needs.

| how | Stream One (131) | Stream Two (71) | total (202) |
|---|---|---|---|
| `tag-game-runner` | 120 | 68 | **188** |
| `tag-game` | 5 | 3 | **8** |
| `horaro-link` | 4 | 0 | **4** |
| `weak` | 1 | 0 | **1** |
| corrected by hand | 1 | 0 | **1** |

No `no-hits` and no `search-failed` on either schedule, and after one correction
no duplicate video id within a stream, across the two, or against any of the 22
CSVs already in `storage/app/csv/`.

Stream One carries four `horaro-link` rows - Jubeat, GITADORA, Clone Hero and
Stepmania, all rhythm-game showcases whose Game cell links the upload. All four
probed alive and all four are ESA's own VODs, titled to convention. This is the
earliest event known to carry any links at all; the skill's "from Summer 2025 on"
is about links being *systematic*, not about them being new.

### Title matching, measured against `slot-exact` for the first time

This event can do something no other backfill could. The validation run resolved
the same Stream One rows from the timing sheet, where a VOD whose duration equals
`EndTimestamp - StartTimestamp` is a near-certain match. Running the ordinary
Horaro title search over the same rows and comparing the two answers measures the
resolver that every sheet-less event has been trusting blind.

**It agreed 128 times out of 130.** Both disagreements are the same failure, and
it is a specific one:

> `rank()` sorts the runner **above** the category. Where ESA's own title omits
> the runner - `Super Mario 64 [120 Star (Relay Race)] - #ESASummer22`,
> `Duke Nukem: Manhattan Project [Any% (Hard)] - #ESASummer22` - a *different*
> video whose title does name a runner outranks it, and the category that would
> have told the two apart never gets consulted.

- **Super Mario 64 - 120 Star (Relay Race)** took the *Crowd Control (70 Star)*
  VOD, because that title says "by cheese" and cheese is one of the ten relay
  runners. This also produced the event's only duplicate video id, so it was
  visible without a sheet. Corrected by hand to `jBEtsLN1YZw`, whose 6867s
  matches the sheet's 6866s slot.
- **Duke Nukem: Manhattan Project** took `Ys-pPZzUjkg` where the sheet-based run
  took `Qxyca6mVtzI`. Both are 5583s, both match the slot exactly, and both follow
  ESA's title convention - two uploads of one run. **Nothing in any artefact the
  tool produces distinguishes them**, and no duplicate was raised because only one
  row wanted that video. Left as resolved.

The lesson for the eleven: title matching is very good - 98.5% here - but its
residual failure is *silent*, and the shape it takes is a title missing the
runner. #75 moved the runner from a filter to a rank signal; this says it should
sit **below** the category, not above it.

### `weak`, and the re-upload problem

One `weak` on the event: **Crash Team Racing - Any% (NMG)**, matched to
`[RU] #ESASummer22 - Crash Team Racing [Any% (NMG)] от Lornoveo`. It is the right
run on the wrong channel - ESA's Russian restream - and it read `high` at
`0:55:52`, which is the sheet's value **exactly**. The re-upload carries the same
overlay and reads perfectly.

It scored `weak(0.0)` here against the `weak(0.694)` the sheet-based run gave it,
because `title_fields()` takes the *first* bracket as the category and this title
opens with `[RU]`, leaving the game name empty. A small separate bug: the bracket
holding the category is not always the first one.

## What needed a human, and what it taught

39 runs were flagged - 38 by `review`, plus one added by hand (below). All 39
were resolved from frames: **13 confirmations, 24 corrections, and 2 that no
reading can settle.** Their `how` values were 34 `tag-game-runner`, 2
`horaro-link` and 1 `tag-game`, so a flagged run on this event is a *reading*
problem, not a matching one.

### Three layouts, and colour means something

ESA Summer 2022 runs at least three overlay layouts, and the timer moves between
them:

1. **Bottom info bar** (widescreen games) - game, category and timer along the
   bottom of the capture.
2. **Left sidebar** (4:3 and handheld games) - the same block stacked down the
   left, timer under the category.
3. **Sidebar with the timer beside the title** - Oracle of Seasons.

A crop tuned to one finds nothing in the others, which is exactly why the tool
calibrates rather than hardcoding a position. **The timer is yellow while running
and white once stopped** on all three - not the orange/green the skill describes
from later years, so the rule to carry forward is "the colour changes", not "the
colour is green".

### The `0:59:xx` cluster - what `max` fallback actually does

Four rejects on Stream One read `0:59:28`, `0:59:36`, `0:59:49` and `0:59:51` out
of videos 43 to 45 minutes long - Trackmania, Hitman: Blood Money, Clone Hero and
DOOM (2016). Their true times are `0:41:23`, `0:40:03`, `0:40:39` and `0:40:08`.

All four say "no stable plateau; fell back to the largest reading". That fallback
does not merely pick *an* inflated value: given a noisy candidate set it converges
on the **largest misreading the format allows**, which is why four independent
runs land within 23 seconds of `0:59:59`. Every one was caught - but only because
the video happened to be under an hour. The same failure inside a 90-minute VOD
would pass the duration guard and ship.

### Reset clocks are the real hazard, and the estimate-ratio guard finds them

Five runs held a *different* clock in their tail:

| run | tail shows | true finish |
|---|---|---|
| GeoGuessr | `00:10:39`, the No Labels incentive | `00:25:36` |
| Super Mario Sunshine (S2) | `00:09:45` | `02:36:09` |
| James Pond 2 | `00:00:49`, a bonus run | `00:30:43` |
| Castlevania: Order of Ecclesia (S2) | `00:00:00` | `00:29:47` (see below) |
| Golden Sun | its own `0:15:00` estimate | `00:00:41` |

**This matters for #66.** Three of this event's estimate-ratio rejections were
GeoGuessr (0.30x), Super Mario Sunshine (0.06x) and Friday the 13th (0.39x). The
first two are reset clocks and the guard was **right** about both; the third was
a correct read and the guard was wrong. That is a third event agreeing with #66's
actual finding - *the reset is the signal* - and a third event's worth of evidence
against narrowing the ratio, which would keep the false alarm and drop both true
positives.

### Castlevania: Order of Ecclesia cannot be pinned exactly

The clock is running at `00:29:47` 150s before the end and already back at
`00:00:00` by 144s, so the finish falls in a six-second window and the frozen
value is never on camera. Shipped as **`0:29:47`, a lower bound**, and listed on
the issue. The OCR's `0:29:45` is below a value the clock was still counting
through, so it cannot be right.

### The two speeches

Opening Speech and Closing Speech have no timer element in their layout at all -
the frame is the stage and the audience and nothing else. Neither ships a time,
and **neither was answered `skip`**: `skip` sets `source=human-skip`, which
exempts the row from the very guard that is dropping the bad value. Closing
Speech read `3:53:09` out of a 35:47 video; leaving it out of the answers file
lets the export drop it, which is the correct outcome.

### The one wrong `high`, and how it was corrected

Metroid: Spooky Mission read `high` and so never reached the review list. It is
the event's only genuinely wrong unreviewed read. Correcting it needed a number
`apply` could key on, so **row 39 was appended to `out/review-index.csv` by hand**
and answered there - which is what makes the correction carry `source=human`
rather than masquerading as the machine's own reading.

Its ramp was **16 frames against a median of 40**, one of the seven thinnest on
the event. Suggestive, not conclusive - Hades (15) and Super Mario 64 (16) are
thinner still and both correct - but the count is already in `notes` and costs
nothing to weigh.

## Evidence on the open tool tickets

- **#63, truncated downloads passing silently.** Two runs failed with
  `moov atom not found` - Command & Conquer: Red Alert 2 and OoT ACE Showcase -
  and **both read `high` on a plain retry at the same `--height 480`**, landing
  within 1s of the sheet. A missing 480p rendition cannot behave that way, so the
  cause here is a short download, not format fallback.
- **#67.** As above, and this is the third event running where the stated cause
  does not survive contact. One further failure, Clone Hero, was a bare
  `403 Forbidden` that also cleared on retry. Nothing on this event supports the
  240p explanation; everything supports "the download was short and nothing
  checked".
- **#66.** See "Reset clocks" above. Do not narrow the ratio.
- **#71.** No evidence either way - this run used no `--debug-crops`, so no crop
  areas were recorded. The ratio still wants a third event.
- **`resolve` records no channel.** Two concrete costs on one event: the Crash
  Team Racing RU restream matched at full confidence with nothing downstream able
  to see it, and Duke Nukem: Manhattan Project has two indistinguishable uploads.
  Recording `channel_id` in `resolved.csv` would make both visible for free -
  yt-dlp's search already returns it.

## Three runs ESA timed that the schedule never listed

The sheet carries three rows with no Horaro counterpart on either schedule:
**Smarties: Meltdown** (Showcase, 0:11:27), **Mary-Kate & Ashley: Sweet 16 -
Licensed To Drive** (Any%, 0:20:04) and **Timesplitters: Future Perfect** (Cat
Driving Challenge, 0:06:10). All three are real, timed, and have VODs. They are
not shipped, because the acceptance criteria are the schedule's rows and the
exporter takes its metadata from Horaro. Worth a follow-up rather than a silent
addition.

## The wall, and the request budget

| | |
|---|---|
| wall 1 | after ~206 requests (202 resolve searches plus probes). Cleared in **30 minutes** |
| wall 2 | after 62 more reads. Cleared in **~90 minutes** |
| then | 62 to 124 to 130 of Stream One, and 71 of Stream Two, with no further block |

`seed` saved **202 requests**: 129 of Stream One's rows were already cached from
the validation run, and the remaining 73 were written from `resolve`'s own search
results. Without it this event would have needed roughly 404 requests before the
first read finished.

The two walls also showed something worth writing down: **the block is
endpoint-specific.** While `-J` on a watch page and `--download-sections` were
both refused, `ytsearch` kept working - which is how Stream Two was resolved
during wall 1 rather than waiting it out idle. Probe the endpoint you actually
need before concluding you are blocked from everything.

`--resume` behaved exactly as #46 intended: a failed row has no `final_time`, so
each pass re-read the rows the wall had refused and skipped the rest.

## Throughput

- Stream One: 62 reads in 62 min, then 62 more in 68 min, then the stragglers.
- Stream Two: **71 of 71 in a single 60-minute pass**, with no failures at all.
- Six shards throughout, `--discard-clips`.

## What to change next

1. **Sort `cscore` above `runner` in `rank()`.** Both resolver misses on this
   event were a title omitting the runner losing to one that names a different
   run's, with the distinguishing category sitting right there in both titles.
   This is the only silent failure class title matching has left, and it is
   measurable: re-running the comparison above against the sheet scores any
   change directly.
2. **Record the channel in `resolved.csv`.** One extra field, from data the
   search already returns, and it separates ESA's uploads from restreams and
   re-uploads for every future event.
3. **Stop the `max` fallback reaching for the largest format-legal value.** The
   four `0:59:xx` rejects are one behaviour, not four incidents, and they only
   failed safely because the videos were short. Bounding the fallback by the
   ramp's own prediction - which #62 already computes - would have answered all
   four correctly.
