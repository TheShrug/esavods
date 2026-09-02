# ESA Winter 2024 — backfill

Issue #46. Two Horaro schedules (`2024-winter1`, `2024-winter2`), tag
`#ESAWinter24`, shipped as `ESA 2024 Winter (One)` and `ESA 2024 Winter (Two)`.

- **Settings**: `--height 480 --tail 600 --step 12`, six shards per schedule,
  run one schedule at a time.
- **Outcome**: **151 of 155 scheduled runs live with a time.** 110 read `high`,
  39 were resolved from frames by hand, and only **2** ship on an unconfirmed
  reading — both lower bounds on runs whose VOD ends mid-run.
- **The bot wall interrupted this event** at roughly 460 yt-dlp invocations,
  with the Stream Two review pass unstarted. It cleared in under a day and the
  review was finished on a second sitting. See "The wall" below.

## Resolution — the first event to run on #75, and it holds

164 schedule rows, of which **9 are filler** (`Opening Speech`, `No Milestone,
just Madness #1`–`#7`, `Glorious Alphabet Tournament` — all with no category)
and were dropped before reading. That left **155 real runs**.

Every VOD link on both schedules is Twitch — 214 on Stream One, 127 on Stream
Two, zero YouTube — and ESA's Twitch VODs from this era are deleted, so
`horaro-link` never fires and the whole event runs on title search.

| how | Stream One (92) | Stream Two (63) | total (155) |
|---|---|---|---|
| `tag-game-runner` | 80 | 60 | **140** |
| `tag-game` | 10 | 3 | **13** |
| `weak` | 1 | 0 | **1** |
| `no-hits` | 1 | 0 | **1** |

**140 of 155 on three-way agreement, one video each, no duplicates.** That is a
better shape than Winter 2021's 129/142 on the same evidence, and it is reached
without ESA's own links.

All three of #75's fixes were exercised, and all three paid:

- **The runner as a rank signal, not a filter.** Six rows would have been
  `no-hits` under the old query, because horaro holds `English_Ben`,
  `Kingj0444`, `Shoen`, `PontonFSD`, `nepumukgaming` against titles carrying
  `EnglishBen`, `KingjO444`, `Sh0en`, `Matt Ponton`, `Nepumuk`. Each now lands
  `tag-game(1.0)` on the right video.
- **`_names()` splitting a race cell on its links.** Stream One has **nine**
  `A vs. B` races. All nine came back `tag-game-runner`, eight at 1.0. Unlike
  Summer 2024's Battleship Bingo, ESA published **one combined VOD per race**
  here, titled with both runners (`Bowser's Fury [Any%] by Riekelt and
  RDVvsTheWorld`), so there is no per-runner ambiguity to hand to a person.
- **`_plain()` keeping only the first link of a Game cell.** Stream Two row 39
  is `[Trauma Center: New Blood](twitch) + [Meme Center](twitch)`. It resolves
  to `Trauma Center: New Blood [Normal]` at 1.0 rather than asking for a game
  called `... + Meme Center`.

### The one `weak` is right, and that is new

Summer 2024's four `weak` matches were all the wrong video, and the write-up
concluded "`weak` remains a synonym for no". This event's single `weak` is
**correct**: Train Simulator `$25% to ESA`, whose title is
`Train Simulator $25% to ESA by popeter   #ESAWinter24` with no `[Category]`
bracket at all. `title_fields()` therefore scores the *whole* title as the game
name, gscore falls to 0.667, and a right answer is labelled almost certainly
wrong. One sample is not a trend, but "`weak` means no" is now 4-for-5 rather
than absolute.

The single `no-hits`, `Afterparty [🎉🎉🎉🎉]`, is correct too: ESA published no
VOD for it. It is the one scheduled row with no video anywhere.

### A new resolver false positive: the third-party restream

`Wendy: Every Witch Way` matched **`Wendy: Every Witch Way par Nordic
[ESA Winter 24]`** at `tag-game-runner(0.909)` — a French restream channel's
upload, not ESA's. Its footage is a completely different overlay (a pink
hexagon layout captioned `À SUIVRE`), and the OCR duly read `10:30:00` off a
`46x16` crop of it.

The mechanism is that the tag test is
`tag.lower() in norm(title).replace(" ", "")`, and `norm()` strips punctuation,
so the *words* "ESA Winter 24" collapse to `esawinter24` and satisfy a test
meant for the hashtag `#ESAWinter24`. Repeating the search finds no ESA upload
for this run, so nothing is lost by dropping it — but the same collapse would
happily hand a real run someone else's video.

## Reads

| tier | n | outcome |
|---|---|---|
| high | 110 | shipped unreviewed |
| medium | 25 | all checked against frames |
| low | 5 | all checked against frames |
| reject | 13 | 11 checked; 2 are rows with no timer at all |
| none | 1 | Taskmaster II, which has no overlay |

**110 of 154 accepted without review — 71%**, well below Summer 2024's 87% and
Summer 2022's 81%. The shortfall is not mysterious: **22 runs report `no stable
plateau; fell back to the largest reading`**, and on this event that fallback is
usually a `3` misread as a `5`.

Of the 39 runs resolved from frames, **12 confirmed the OCR exactly and 27 were
corrected.** That is a far worse hit rate than Summer 2024's 10-of-16, and it is
the headline fact about this event: **once a run on Winter 2024 falls out of
`high`, the reading is wrong about 70% of the time.** The `high` tier itself
showed no sign of trouble.

### The clock is yellow while running and white once stopped

Summer 2024 and Summer 2025 had an orange-while-running, green-once-stopped
clock. Winter 2024's layout is subtler but has the same tell: **the running
clock is yellow, and the moment it stops it renders in white/grey.** It is easy
to miss — I initially recorded this event as having no colour change at all —
but once seen it is unambiguous, and it is visible on every stopped frame in
this event including the ones where the digits alone look plausible.

The review method that worked was a tiled montage: one `yt-dlp` window, N frames
evenly spaced, cropped to the bottom 30% of the frame and stacked into a single
PNG. A stop then shows up twice over — a repeated value down the strip, and a
colour change at the same row — and the ramp above it confirms the crop is the
timer rather than the estimate.

**Frame spacing has to match the question being asked**, and getting this wrong
cost a whole pass. Six frames over the last five minutes answered "did this run
finish long ago", but it wrongly suggested five runs had no finish on camera:
their clocks were still ticking in every sampled frame. Re-probing the **last 40
seconds at 4-second spacing** found a clean plateau in all five. The general
shape that worked for a first look is **12 frames over the last 240 seconds**;
tighten to a 40–100 second window to pin an exact value, and widen to a
mid-VOD window when the tail holds a different clock.

One layout note: Ratatouille calibrated to `64,255,167,50`, a timer at 53% of
frame height rather than in the lower third. A bottom-30% strip misses it
entirely, so a per-run crop fraction is needed rather than one constant.

### Corrections — 27 of 39

**The `3`/`5` glyph confusion — 8 runs.** Summer 2024 recorded that this "did
not appear once" and concluded the estimate-read had displaced it. It has not:
it is the single largest cause here, and it behaves exactly as the README
describes — never a clean plateau, so the resolver falls back to the largest
reading, which is the inflated one by construction. Seven are worth precisely
`+20s`; the eighth is `+2s`.

| run | OCR read | actual |
|---|---|---|
| Devil May Cry 4: SE — NG (Devil Hunter) | `1:18:54` | `1:18:34` |
| Alan Wake 2 — Glitchless | `3:12:55` | `3:12:35` |
| TMNT: Shredder's Revenge — Any% | `1:24:55` | `1:24:35` |
| Sonic Superstars — Story Mode (NG+, Trip) | `0:38:52` | `0:38:32` |
| ibb & obb — Any% (Local, Highwayless) | `0:31:52` | `0:31:32` |
| Super Mario Odyssey — Talkatoo% | `1:46:52` | `1:46:32` |
| LEGO Pirates of the Caribbean — Any% (NOCUT5) | `1:19:51` | `1:19:31` |
| Grand Theft Auto III — Tightened Thrice | `1:43:05` | `1:43:03` |

**Read the estimate instead of the timer — 7 runs.** Every one calibrated to a
crop under 100px wide; see #71 below.

| run | OCR read | actual |
|---|---|---|
| Final Fantasy VII — Any% | `17:20:00` | `7:19:32` |
| Final Fantasy IX — Memoria Boss Rush (Level 1) | `1:05:00` | `0:56:26` |
| Classic Sonic Trilogy — Any% (65 Player Relay) | `3:00:00` | `2:20:50` |
| Bowser's Fury — Any% | `10:40:00` | `0:32:33` |
| Tobari and the Night of the Curious Moon — Any% (Normal Ending) | `1:00:00` | `0:52:30` |
| Kingdom Hearts 2 Final Mix — Any% (Critical, Modded) | `2:45:00` | `2:50:48` |
| Super Mario Galaxy 2 — Green Stars | `3:10:00` | `3:09:29` |

**The tail holds a reset clock — 6 runs.** See below.

| run | OCR read | actual |
|---|---|---|
| Resident Evil 5 — No Merchant (Normal) | `0:11:20` | `2:11:32` |
| Super Princess Peach — Any% | `0:11:07` | `1:35:42` |
| Splatoon 2 — Any% | `0:12:17` | `1:32:32` |
| Deus Ex: Mankind Divided — Any% | `0:09:00` | `0:43:08` |
| The Legend of Zelda: Link's Awakening — Warpless | `0:10:01` | `0:43:26` |
| Captain Toad: Treasure Tracker — All Gems | `1:53:38` | `1:53:44` |

**The remaining six** are ordinary short-of-the-finish misses where the largest
sampled reading landed before the plateau: System Shock (Remake) `0:27:21` →
`0:33:28`, The Guardian Legend `1:03:01` → `1:03:34`, Contrast `0:12:29` →
`0:15:29`, Garfield Lasagna Party `1:43:42` → `1:48:23`, Zortch `0:09:56` →
`0:12:52`, Splatoon `0:33:38` → `0:33:41`.

### The tail-reset class is far bigger here than anywhere

Six runs read a small, confident, completely wrong value because the crew
**reset the timer** for a bonus segment before the VOD ended. Summer 2025 saw
this once (Super Mario Bros. 3); Summer 2024 once in its mildest form (Paris
Marseille, a 3-second near miss). Here it costs six runs and the errors are
enormous — `0:11:20` against a true `2:11:32`.

The fix in each case was to probe a window earlier in the same VOD and watch the
first segment's clock run past the estimate and freeze. On Resident Evil 5 the
montage shows the run clock ticking `01:59:20 → 02:11:32` and holding, followed
much later by a fresh `00:11:20` segment. Captain Toad is the subtlest of the
six and the most instructive: its tail holds a **different game entirely**
(`Suika game / Showcase%`), and the OCR's `1:53:38` is only six seconds under
the true `1:53:44`, so nothing about the number looks wrong.

Captain Toad also shows the crew **editing the estimate live** — the layout
reads `01:28:00`, then `01:45:00`, then `01:50:00` as the run overran. Anything
that reasons about a run against "its estimate" is reasoning against a value
that was not constant.

## ESA's VODs are cut to the run, and two cuts land short

**Every Winter 2024 VOD begins with the run's own timer at `00:00:00` and
ticking** — verified on four next-run VODs (Deus Ex, LEGO Batman, Tomb Raider
III, Bowser's Fury). A run's finish is therefore never in the following video,
and the gap between two videos is simply unpublished.

That makes "the clock is still moving when the VOD ends" a terminal condition,
not something to chase into the next upload. It happens twice:

- **The Lost Vikings — Any% (Coop)**, clock at `01:06:53` four seconds before
  the video ends, still counting.
- **Golden Sun 3: Dark Dawn — Any%**, clock at `05:01:58` in the final frame,
  still counting.

Both ship as **lower bounds**, and both are the only two runs on the unvouched
list.

## #65 (`equals_estimate`) — 6 of 154, and all six now checked

| run | read | crop | verdict |
|---|---|---|---|
| Final Fantasy IX | `1:05:00` | `60x22` | wrong — actual `0:56:26` |
| Classic Sonic Trilogy | `3:00:00` | `63x21` | wrong — actual `2:20:50` |
| Tobari and the Night of the Curious Moon | `1:00:00` | `61x22` | wrong — actual `0:52:30` |
| Kingdom Hearts 2 Final Mix | `2:45:00` | `63x22` | wrong — actual `2:50:48` |
| Super Mario Galaxy 2 | `3:10:00` | `60x22` | wrong — actual `3:09:29` |
| Sonic Spinball | `1:00:00` | `168x50` | **right** — a Crowd Control showcase, capped at the hour |

Sonic Spinball is this event's Battleship Bingo: a **time-capped showcase** that
genuinely ends on a round number. The montage shows the clock ticking
`00:57:16 → 00:59:41 → 01:00:00` and stopping. Two events running, the
demotion-not-rejection decision has saved a correct time.

**The crop separates the six perfectly.** All five wrong reads calibrated to a
~`60x22` box; the one correct read calibrated to the modal `168x50` timer.
`equals_estimate` cannot tell a locked-on-the-estimate read from a genuine round
finish — the crop can, and did, 6 for 6.

Super Mario Galaxy 2 is the case that makes this concrete: its true time is
`3:09:29` against a `3:10:00` estimate, **31 seconds apart**. A rule that only
compared values would have called that agreement close enough to be suspicious
of nothing at all.

## #71 — crop size is now 14 for 14 across two events

| crop size | runs | estimate-reads |
|---|---|---|
| 164–199 px wide (the timer) | 144 | **0** |
| 46–63 px wide (the `EST.` field) | 9 | **9** |

All nine tiny crops were checked against frames this time, and all nine were the
estimate field: Closing Speech `57x21`, Bowser's Fury `63x22`, Wendy `46x16`,
Final Fantasy VII `48x17`, Final Fantasy IX `60x22`, Classic Sonic Trilogy
`63x21`, Tobari `61x22`, Kingdom Hearts 2 `63x22`, Super Mario Galaxy 2 `60x22`.
No crop of normal size was ever an estimate-read.

With Summer 2024's 5-for-5 against 118 normal crops, that is **14 tiny crops
across two events, 14 estimate-reads, and zero false positives across 262
normally-sized ones.** It is cheap, already recorded by `batch`, and unlike
`equals_estimate` it does not depend on the run's true time differing from its
estimate.

## Known bugs, re-confirmed

- **#66 — the estimate-ratio guard was right, for the first time ever, and it
  was right five times.** This reverses the recommendation the last five events
  built up, so it is worth being precise. Eight runs were rejected on the ratio
  alone, and all eight have now been checked:

  | run | read | ratio | verdict on the *reading* |
  |---|---|---|---|
  | Resident Evil 5 | `0:11:20` | 0.08x | **wrong** — true `2:11:32` |
  | Super Princess Peach | `0:11:07` | 0.12x | **wrong** — true `1:35:42` |
  | Splatoon 2 | `0:12:17` | 0.13x | **wrong** — true `1:32:32` |
  | Deus Ex: Mankind Divided | `0:09:00` | 0.14x | **wrong** — true `0:43:08` |
  | Link's Awakening | `0:10:01` | 0.21x | **wrong** — true `0:43:26` |
  | Sonic Frontiers | `0:24:19` | 0.24x | right |
  | Zool | `0:06:55` | 0.29x | right |
  | Anodyne | `0:12:16` | 0.35x | right |

  **Five of eight rejections were correct**, and the guard is the only thing
  that caught them: each is a tail-reset artefact, and without it those five
  would have shipped as plausible-looking times out by up to two hours.

  The split is clean and mechanical. Every correct rejection is **at or below
  0.21x**; every false alarm is **at or above 0.24x**, and all three false
  alarms are "Showcase" or tutorial categories that genuinely run a fraction of
  their slot. That is not a coincidence: the guard's failure mode is a genuinely
  short run, while its success mode is a reset clock reading a few minutes
  against an estimate of hours.

  So #66 should **not** simply be dropped, and this event is the counterexample
  its comments were missing. Every prior event that made the 0-for-N case lacked
  this event's tail-reset class. Narrowing the lower bound from 0.4x to about
  0.22x would have kept all five catches and dropped all three false alarms
  here.

- **#67 fired, and its stated cause is not the whole story.** Four Stream Two
  runs failed outright with `ffmpeg failed (183): moov atom not found` —
  Kalimba, M&Ms Shell Shocked, Deus Ex: Human Revolution, Okami — as did four
  frame grabs. The issue describes this as the height fallback picking an
  uncuttable 240p when no 480p exists. **On Ratatouille a 480p rendition exists
  and the failure still happened**: the selector picked format `398`, which is
  **AV1**, and a `--download-sections` cut of AV1 produces a file ffmpeg cannot
  open. Pinning the AVC itags (`-f 135/134/136/133`) fixed it immediately.

  All four batch failures re-read cleanly at `--height 720`, every one at
  `high`: Kalimba `1:17:21`, M&Ms Shell Shocked `0:56:52`, Deus Ex: Human
  Revolution `1:10:07`, Okami `8:54:43`. Note also that the corrupt clip
  re-caches under a *new* parameter hash, so clearing `<id>.*.mp4` is required
  before any retry or the failure simply repeats.

- **#63 did not visibly fire**, which as ever is not a claim the artefacts can
  support.

- **#69, crop stability per layout.** `Layout` is hidden on both schedules here
  (`hidden:Layout`) where it was visible on Summer 2024; `horaro_rows` reads it
  either way because it lowercases column names. The modal crop is `168x50` at
  x≈428 (64 runs) with `167x50` close behind (47), so x is stable and y moves
  with the layout's lower third — the same picture as Summer 2024. The nine tiny
  crops are what a pinned crop would have prevented, and Ratatouille's
  `64,255,167,50` is what a *per-layout* pin would have to accommodate.

## The wall

It went up at roughly **460 yt-dlp invocations**, the most of any event so far
and well past the ~250 where Summer 2025 hit it twice. The budget was
underestimated at the outset because the review helper makes **two** invocations
per frame grab — a `--print duration` probe and the download — so 66 grabs cost
132 requests, not 66.

The failure is unambiguous (`Sign in to confirm you're not a bot`) and
everything was stopped rather than retried; no cookies were used. **It cleared
in under a day**, consistent with Summer 2025's ~2.5 hours, and the remaining 17
items were finished on a second sitting at concurrency 2 with no further
refusals. Waiting continues to be the correct response.

## Runs that need a second pair of eyes

Only two runs ship on a time nobody has confirmed, and both are known lower
bounds rather than doubtful readings:

- **The Lost Vikings — Any% (Coop)** — `1:06:53`, VOD ends mid-run.
- **Golden Sun 3: Dark Dawn — Any%** — `5:01:59`, VOD ends mid-run.

Four scheduled rows ship with **no time**, none of them recoverable:

- **Afterparty** — 🎉🎉🎉🎉. ESA published no VOD.
- **Closing Speech** — the layout carries no timer, only the estimate.
- **Taskmaster II** — a stage segment with no overlay at all.
- **Wendy: Every Witch Way** — no ESA VOD exists; see the restream note above.

One run is worth a glance for a different reason: **Okami — Top Dog** at
`8:54:43` trips the release script's over-eight-hours warning. It is a real
8h55m run inside an 8h59m video, backed by an 11-frame plateau and 39 ramp
frames.

## Improvements worth making

1. **Flag a calibrated crop much smaller than the event's modal crop (#71).**
   Summer 2024 proposed this at 5-for-5; this event takes it to 14-for-14 with
   zero false positives across 262 normal crops, and adds the case that makes it
   strictly better than `equals_estimate`: it is the only signal that separated
   Sonic Spinball's genuine `1:00:00` from five spurious ones, including Super
   Mario Galaxy 2's `3:10:00` whose true time is 31 seconds away. It needs no
   new data — `batch` already records the crop.
2. **Reconsider #66 rather than closing it as agreed.** Five events built a
   0-for-N case for deleting the estimate-ratio guard; this event is the first
   where it has true positives, and it has five of them, cleanly separated from
   its three false alarms at 0.22x. The evidence now points at *narrowing* the
   bound, not removing the rule. Anyone about to action #66 should read this
   event first.
3. **Detect the tail-reset directly.** Six runs here, one on Summer 2025, one on
   Summer 2024. The signature is cheap: the sampled window contains a value that
   *decreases*. `batch` already reads every frame in order, so a note saying
   "the clock resets inside the sampled window — the run's finish is earlier"
   would have flagged all six without a single extra request, and would turn the
   most expensive review case in this event into a one-line hint.
4. **Pin the AVC itags in the downloader (#67).** `-f 135/134/136/133` ahead of
   the height-based selector avoids AV1 renditions, which are what actually
   break `--download-sections`. Also clear cached clips on retry: they re-cache
   under a new parameter hash.
5. Smaller, but it cost real requests: **the review helper should reuse the
   duration already in `resolved.csv`** instead of probing for it. That halves
   the request cost of a review pass, which is exactly the pass that runs when
   the request budget is most nearly spent.
