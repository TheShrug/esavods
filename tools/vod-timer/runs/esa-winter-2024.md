# ESA Winter 2024 — backfill

Issue #46. Two Horaro schedules (`2024-winter1`, `2024-winter2`), tag
`#ESAWinter24`, shipped as `ESA 2024 Winter (One)` and `ESA 2024 Winter (Two)`.

- **Settings**: `--height 480 --tail 600 --step 12`, six shards per schedule,
  run one schedule at a time.
- **Outcome**: **148 of 155 scheduled runs live with a time.** 107 read `high`,
  26 were resolved from frames by hand, 15 ship on an unconfirmed reading.
- **Stopped early.** YouTube's bot wall went up before the Stream Two review
  frames were pulled, so 13 of those 15 are unchecked rather than unresolvable.
  See "The wall" below.

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
| high | 107 | shipped unreviewed |
| medium | 25 | 11 checked, 14 unchecked (wall) |
| low | 5 | all checked against frames |
| reject | 13 | 8 checked, 5 unchecked or unshippable |
| none | 4 | 1 recovered at 720p, 3 blocked by #67 |

**107 of 154 accepted without review — 69%**, well below Summer 2024's 87% and
Summer 2022's 81%. The shortfall is not mysterious: **22 runs report `no stable
plateau; fell back to the largest reading`**, and on this event that fallback is
usually a `3` misread as a `5`.

Of the 26 runs I resolved from frames, **11 confirmed the OCR exactly and 15
were corrected.**

### The layout has no colour change, so one frame proves nothing

Summer 2024 and Summer 2025 both had an orange-while-running,
green-once-stopped clock, and both write-ups record that this is what made
frame review cheap. **Winter 2024's timer is yellow throughout** — running and
stopped look identical.

Every check here therefore needs **two frames far enough apart to prove the
clock did not move**, and the review method that worked was a tiled montage:
one `yt-dlp` window, N frames evenly spaced, cropped to the bottom 30% and
stacked into a single PNG. A frozen clock is then obvious as a repeated value
down the strip, and the ramp above it confirms the crop is the timer and not
the estimate.

**Frame spacing has to match what is being asked.** Six frames over the last
five minutes answered "did this run finish long ago", but it wrongly suggested
five runs had no finish on camera: their clocks were still ticking in every
sampled frame. Re-probing the **last 40 seconds at 4-second spacing** found a
clean plateau in all five. Only one run in the event genuinely ends with the
clock still running.

### Corrections — 15 of 26

| run | OCR read | actual | cause |
|---|---|---|---|
| Devil May Cry 4: SE — NG (Devil Hunter) | `1:18:54` | `1:18:34` | `3`→`5`, tens of seconds |
| Alan Wake 2 — Glitchless | `3:12:55` | `3:12:35` | `3`→`5`, tens of seconds |
| TMNT: Shredder's Revenge — Any% | `1:24:55` | `1:24:35` | `3`→`5`, tens of seconds |
| Sonic Superstars — Story Mode (NG+, Trip) | `0:38:52` | `0:38:32` | `3`→`5`, tens of seconds |
| ibb & obb — Any% (Local, Highwayless) | `0:31:52` | `0:31:32` | `3`→`5`, tens of seconds |
| Super Mario Odyssey — Talkatoo% | `1:46:52` | `1:46:32` | `3`→`5`, tens of seconds |
| LEGO Pirates of the Caribbean — Any% (NOCUT5) | `1:19:51` | `1:19:31` | `3`→`5`, tens of seconds |
| Grand Theft Auto III — Tightened Thrice | `1:43:05` | `1:43:03` | `3`→`5`, units of seconds |
| Final Fantasy VII — Any% | `17:20:00` | `7:19:32` | read the **estimate** |
| Final Fantasy IX — Memoria Boss Rush (Level 1) | `1:05:00` | `0:56:26` | read the **estimate** |
| Classic Sonic Trilogy — Any% (65 Player Relay) | `3:00:00` | `2:20:50` | read the **estimate** |
| Bowser's Fury — Any% | `10:40:00` | `0:32:33` | read the **estimate** |
| Super Princess Peach — Any% | `0:11:07` | `1:35:42` | tail holds a **reset** clock |
| Splatoon 2 — Any% | `0:12:17` | `1:32:32` | tail holds a **reset** clock |
| Resident Evil 5 — No Merchant (Normal) | `0:11:20` | `2:11:32` | tail holds a **reset** clock |

**Eight of fifteen corrections are the `3`/`5` glyph confusion.** That is worth
stating plainly, because Summer 2024 recorded that it "did not appear once" and
concluded the estimate-read had displaced it as the dominant fault. It has not:
it is dominant again here, and it behaves exactly as the README describes —
never a clean plateau, so the resolver falls back to the largest reading, which
is the inflated one by construction. Seven of the eight are worth precisely
`+20s`; the eighth is `+2s`.

### The tail-reset class is bigger here than anywhere

Three runs read a small, confident, completely wrong value because the crew
**reset the timer** for a bonus segment before the VOD ended. Summer 2025 saw
this once (Super Mario Bros. 3), Summer 2024 once in its mildest form (Paris
Marseille, a 3-second near miss). Here it costs three runs and the errors are
enormous — `0:11:20` against a true `2:11:32`.

The fix in each case was to probe a window two-thirds of the way through the
VOD and watch the first segment's clock run past the estimate and freeze. On
Resident Evil 5 the montage shows the run clock ticking `01:59:20 → 02:11:32`
and then holding, followed later by a fresh `00:11:20` segment. Nothing in the
tail betrays this, which is exactly what the skill warns.

A fourth run in this class, **The Legend of Zelda: Link's Awakening**, was not
recovered: the wall went up before its mid-VOD probe ran. It ships on
`0:10:01`, which is **known to be wrong** — that value is the reset segment, not
the run. It is the one run in this event shipping a time I can positively say
is incorrect.

## ESA's VODs are cut to the run, and one cut lands short

Worth recording because it changes how a mid-run tail should be read. **Every
Winter 2024 VOD begins with the run's own timer at `00:00:00` and ticking** —
verified on three consecutive next-run VODs (Deus Ex, LEGO Batman, Tomb Raider
III). A run's finish is therefore never in the following video, and the gap
between two videos is simply unpublished.

That makes "the clock is still moving when the VOD ends" a terminal condition,
not something to chase into the next upload. It happens exactly once:
**The Lost Vikings — Any% (Coop)**, whose clock reads `01:06:53` four seconds
before the video ends and is still counting. `1:06:53` ships as a **lower
bound**, not a finish.

## #65 (`equals_estimate`) — 6 of 154, and the crop tells you which are wrong

It fired on **six runs**, the same count as Summer 2024:

| run | read | crop | verdict |
|---|---|---|---|
| Final Fantasy IX | `1:05:00` | `60x22` | wrong — actual `0:56:26` |
| Classic Sonic Trilogy | `3:00:00` | `63x21` | wrong — actual `2:20:50` |
| Sonic Spinball | `1:00:00` | `168x50` | **right** — a Crowd Control Showcase, capped at the hour |
| Tobari and the Night of the Curious Moon | `1:00:00` | `61x22` | unchecked (wall) |
| Kingdom Hearts 2 Final Mix | `2:45:00` | `63x22` | unchecked (wall) |
| Super Mario Galaxy 2 | `3:10:00` | `60x22` | unchecked (wall) |

Sonic Spinball is this event's Battleship Bingo: a **time-capped showcase** that
genuinely ends on a round number. The montage shows the clock ticking
`00:57:16 → 00:59:41 → 01:00:00` and stopping, so rejecting on this rule rather
than demoting would again have thrown away a correct time. Two events, two
saves — the demotion-not-rejection decision keeps looking right.

**The sharper finding is the crop.** Five of the six hits calibrated to a crop
around `60x22`; the sixth — the correct one — calibrated to the modal `168x50`
timer box. `equals_estimate` cannot tell a locked-on-the-estimate read from a
genuine round finish. **The crop size can, and did, on both cases I could
check.**

## #71 — crop size is now 9 for 9 across two events

`batch` records the calibrated crop, and on this event it separates the fault
as cleanly as it did on Summer 2024:

| crop size | runs | estimate-reads |
|---|---|---|
| 164–199 px wide (the timer) | 141 | **0** |
| 46–63 px wide (the `EST.` field) | 9 | **9** |

The nine tiny crops are Closing Speech `57x21`, Bowser's Fury `63x22`, Wendy
`46x16`, Final Fantasy VII `48x17`, Final Fantasy IX `60x22`, Classic Sonic
Trilogy `63x21`, Tobari `61x22`, Kingdom Hearts 2 `63x22`, Super Mario Galaxy 2
`60x22`. **Six were checked against frames and all six were the estimate
field**; the other three each read exactly their estimate, which is the same
signature. No crop of normal size was an estimate-read.

Combined with Summer 2024's 5-for-5 against 118 normal crops, that is
**14 tiny crops across two events, 14 estimate-reads, and zero false positives
across 259 normally-sized ones.** This is a cheap, already-recorded, and so far
perfect discriminator, and unlike `equals_estimate` it does not depend on the
run's true time differing from its estimate.

## Known bugs, re-confirmed

- **#66 — the estimate-ratio guard was right, for the first time ever, and it
  was right four times.** This reverses the recommendation the last five events
  built up, so it is worth being precise. Eight runs were rejected on the ratio
  alone. Seven were checked:

  | run | read | ratio | verdict on the *reading* |
  |---|---|---|---|
  | Super Princess Peach | `0:11:07` | 0.12x | **wrong** — true `1:35:42` |
  | Splatoon 2 | `0:12:17` | 0.13x | **wrong** — true `1:32:32` |
  | Resident Evil 5 | `0:11:20` | 0.08x | **wrong** — true `2:11:32` |
  | Link's Awakening | `0:10:01` | 0.21x | **wrong** — reset segment |
  | Sonic Frontiers | `0:24:19` | 0.24x | right |
  | Zool | `0:06:55` | 0.29x | right |
  | Anodyne | `0:12:16` | 0.35x | right |

  **Four of seven rejections were correct**, and the guard is the only thing
  that caught them: each is a tail-reset artefact, and without it those four
  would have shipped as plausible-looking `medium` times that are out by up to
  two hours.

  The split is clean and mechanical. The four correct rejections are all
  **below 0.22x**; the three wrong ones are all **above 0.23x**, and all three
  are "Showcase" categories that genuinely run a fraction of their slot. That
  is not a coincidence — the guard's failure mode is a genuinely short run,
  while its success mode is a reset clock reading a few minutes against an
  estimate of hours.

  So #66 should **not** simply be dropped, and this event is the counterexample
  the issue's comments were missing. Every prior event that made the 0-for-N
  case lacked this event's tail-reset class. Narrowing the lower bound from
  0.4x to about 0.22x would have kept all four catches and dropped all three
  false alarms here; that is one event's evidence, but it is the first evidence
  the rule has any true positives at all.
- **#67 fired, and hard.** Four Stream Two runs failed outright with
  `ffmpeg failed (183): moov atom not found` — Kalimba, M&Ms Shell Shocked,
  Deus Ex: Human Revolution, Okami — as did three of my frame grabs. Re-running
  at `--height 720` fixed the frame grabs immediately and recovered **M&Ms Shell
  Shocked at `high` (`0:56:52`)**. The other three were still queued when the
  wall went up and are unread. Note that the corrupt clip re-caches under a new
  parameter hash, so clearing `<id>.*.mp4` before the retry is required and was
  not sufficient for Kalimba, which failed again at 720.
- **#63 did not visibly fire**, which as ever is not a claim the artefacts can
  support.
- **#69, crop stability per layout.** `Layout` is hidden on both schedules here
  (`hidden:Layout`) where it was visible on Summer 2024; `horaro_rows` reads it
  either way because it lowercases column names. The modal crop is `168x50` at
  x≈428 (64 runs) with `167x50` close behind (47), so x is stable and y moves
  with the layout's lower third — the same picture as Summer 2024, and the nine
  tiny crops are what a pinned crop would have prevented.

## The wall

It went up at roughly **460 yt-dlp invocations**, the most of any event so far
and well past the ~250 where Summer 2025 hit it twice. The budget was
underestimated at the outset: the review helper makes **two** invocations per
frame grab (a `--print duration` probe and the download), so 66 grabs cost 132
requests, not 66.

The failure is unambiguous — `Sign in to confirm you're not a bot` — and
everything was stopped rather than retried, per the skill. Nothing was retried
into the block and no cookies were used.

Left unfinished by it:

- 13 Stream Two runs never had review frames pulled. They ship on their OCR
  readings and are on the unvouched list.
- Link's Awakening's mid-VOD probe, described above.
- Kalimba, Deus Ex: Human Revolution and Okami never re-read at 720p, so those
  three runs ship with **no time at all**.

## Runs that need a second pair of eyes

Full list in the comment on #46. The ones that are not merely unconfirmed:

- **The Legend of Zelda: Link's Awakening — Warpless.** Ships `0:10:01`, known
  wrong; the true time is in its own VOD before the timer reset.
- **The Lost Vikings — Any% (Coop).** `1:06:53` is a lower bound; the VOD ends
  mid-run and no finish exists on camera.
- **Wendy: Every Witch Way — Any%.** No ESA VOD exists; the only candidate is a
  third-party restream. Not shipped.
- **Closing Speech** and **Taskmaster II** carry no on-screen timer at all —
  Taskmaster II is a stage segment with no overlay. Neither ships a time.
- **Afterparty** has no VOD. Not shipped.
- **Kalimba**, **Deus Ex: Human Revolution — Director's Cut**, **Okami**: unread
  (#67 plus the wall). Not shipped.

## Improvements worth making

1. **Flag a calibrated crop much smaller than the event's modal crop (#71).**
   Summer 2024 proposed this at 5-for-5; this event takes it to 14-for-14 with
   zero false positives across 259 normal crops, and adds the case that makes it
   strictly better than `equals_estimate`: it is the *only* signal that
   separated Sonic Spinball's genuine `1:00:00` from Final Fantasy IX's spurious
   one. It needs no new data — `batch` already records the crop.
2. **Require the hashtag to be a hashtag.** `tagged` currently strips
   punctuation before testing, so a title containing the words "ESA Winter 24"
   passes a test meant for `#ESAWinter24`, which is how a French restream won a
   run at `tag-game-runner(0.909)`. Matching `#` + tag against the unnormalised
   title would cost nothing on the 155 runs here and would have caught it.
3. **Reconsider #66 rather than closing it as agreed.** Five events built a
   0-for-N case for deleting the estimate-ratio guard; this event is the first
   where it has true positives, and it has four of them. The evidence now points
   at *narrowing* the lower bound to roughly 0.22x, not removing it. Anyone
   about to action #66 should read this event first.
4. Smaller, but it cost real requests: **the review helper should reuse the
   duration already in `resolved.csv`** instead of probing for it. That halves
   the request cost of a review pass, which is exactly the pass that runs when
   the request budget is most nearly spent.
