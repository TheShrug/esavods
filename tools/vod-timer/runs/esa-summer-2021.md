# ESA Summer 2021 — backfill

Issue #51. One Horaro schedule (`2021-summer`), tag `#ESASummer21`, shipped as
`ESA 2021 Summer`.

**The largest event of the backfill: 151 schedule rows.** Single-stream, like
#50, so one CSV, one event name and one line in the manifest. The spelling
follows the site's existing single-stream form (`ESA 2021 Winter`, `ESA 2022
Winter`) rather than the `(One)`/`(Two)` pairs of #43–#49. Checked against the
restored production database first: no `ESA 2021 Summer` row existed.

- **Settings**: `--height 480 --tail 600 --step 12`, six shards, then a
  `--resume` pass at `--height 720` for the rows the first pass could not read.
- **Wall time**: 3h 20m for 148 reads, plus 6m for the retry pass.
- **The bot wall never went up**, across roughly 353 yt-dlp requests — the most
  the project has spent on one event, and 92 more than #50.
- **Outcome**: **146 of 151 schedule rows live with a time.** 130 read `high`
  and shipped unreviewed, 16 were resolved from frames by hand, and **none
  ships on an unconfirmed reading.**

## Outcome

| | |
|---|---:|
| schedule rows | 151 |
| rows with an ESA upload | 148 |
| shipped with a time | **146** |
| `high`, shipped unreviewed | **130** |
| resolved from frames (`human`) | **16** |
| shipped unconfirmed | **0** |
| no time, not shipped | 5 |

**130 of 148 accepted without review — 88%**, against 79% on Winter 2022, 81%
on both Summer 2022 runs and 89% on Winter 2021. `release-event.sh` wrote no
`unvouched.md`, because there is nothing on the list.

The five rows that do not ship, and why:

| row | why |
|---|---|
| Resident Evil Village — Hardcore (Glitchless), 25 Jul | no ESA upload; see below |
| Tetris Effect: Connected — Journey Mode (Normal) | no ESA upload |
| Super Mario Maker 2 — 6 Levels Blindfolded (Endless, Easy) | no ESA upload |
| Minecraft — Random Seed (Glitchless, 1.16+) | VOD is **age-gated**; yt-dlp refuses it without cookies. **Resolved by hand afterwards — see the addendum** |
| Opening Speech | the layout carries no timer at all |

> [!note] Addendum, 2026-09-06 — four of the five, not five (#104)
> The Minecraft row now ships. The VOD is still age-gated and the tool still
> cannot read it; Stewart opened it in a browser and read the on-screen timer
> directly, giving `0:42:59`. That is the same standard as the sixteen rows the
> event resolved from frames by hand, so it ships as a normal time.
>
> **The counts elsewhere in this file are left as they were.** They record what
> the pipeline produced on the day, which is the thing this evaluation exists to
> measure, and an age gate the tool cannot pass is a real result rather than a
> gap to paper over. The site now carries **147 of 151**; the tool still read
> 146.
>
> Worth keeping in view for future events: this is the first age-gated VOD in
> twelve events, and the only fix available was a person watching it. If a second
> one appears, a cookie export becomes worth building rather than working around.

## Resolution

No ESA timing sheet exists for this event, so `slot-exact` was unavailable. The
schedule's Game cells link **Twitch** VODs — all long deleted — with exactly one
exception, the Opening Speech, whose cell links YouTube. So there is one
`horaro-link` answer and 150 title searches.

| how | n |
|---|---:|
| `tag-game-runner` | 137 |
| `tag-game` | 10 |
| `horaro-link` | 1 |
| `no-upload` (corrected by hand) | **3** |

The raw resolve was 138 `tag-game-runner`, 10 `tag-game`, 2 `weak`, 1
`horaro-link`, and no `no-hits` — the healthiest shape any backfill has
returned. **Every one of the three errors announced itself as a duplicate video
id**, which is the symptom #49 named and #50 confirmed. There were no others.

### All 151 matches are ESA's own uploads — and the check was free (#102)

#50 lost eleven runs to ESA's Russian restream at `tag-game-runner(1.0)`, and
nothing the tool produces could tell them apart. This event was checked
properly, and the way it was checked is the finding:

**YouTube's public oEmbed endpoint returns the channel for a video id, and it is
not on the yt-dlp request path.**

```sh
curl -s "https://www.youtube.com/oembed?url=https%3A//www.youtube.com/watch%3Fv%3D<id>&format=json"
# {"title":"...","author_name":"ESA Speedrunning","author_url":"https://www.youtube.com/@ESAMarathon",...}
```

All 151 matches came back `ESA Speedrunning`. **No restream reached this
event.** 151 lookups cost nothing against the bot wall and took under a minute.

The restream exists — the channel is `RUSC`, and it re-uploaded this marathon
too:

```
Q1Bu2zgLJoU  ESA Summer 2021 - Bloodborne от yarthow за 1:26:41                 (RUSC)
By1TSa0FV6g  Bloodborne [All Bosses (Unrestricted)] by yarthow - #ESASummer21   (ESA)
```

It did not win here for a reason worth writing down: **the Summer 2021 restream
titles carry no `#ESASummer21` hashtag**, so they never cleared the tag gate that
`score()` applies before `rank()` ever runs. #50's restream titles *did* carry
the tag (`… от tharixer - #ESAWinter22 [RU]`), which is why the same channel cost
eleven runs there and none here. **The exposure is a property of how that
channel happened to title one event, not of the ranking** — which makes the
`rank()` fix no less necessary, only less visible on this event.

The duration difference that makes it matter is present here too: ESA's
Bloodborne upload is 1:30:20, the restream of the same run is 1:31:34, and the
restream's own title claims 1:26:41.

### Two runs on this schedule were never uploaded, and one row is not the row it looks like

Three duplicate video ids, all resolved before any reading:

| rows sharing an id | what it was |
|---|---|
| Pac-Man 99 / **Tetris Effect: Connected** | Tetris Effect has no ESA upload; it took Pac-Man's |
| Super Mario 64 FPS / **Super Mario Maker 2** | Super Mario Maker 2 has no ESA upload; it took SM64 FPS's |
| Resident Evil Village ×2 | two real schedule rows, **one** upload |

Resident Evil Village appears twice: `Hardcore (Glitchless)` on 25 July at 02:15,
and `Hardcore (Glitchless) v2` as the schedule's **final row** on 1 August. Both
by gidano, both estimated 2h. One YouTube upload exists, and its title says
`[Hardcore (Glitchless)]` with no `v2`, which points the wrong way.

**Upload dates settle it, and they settle it exactly.** ESA published this event
one video per day, in schedule order:

| schedule row | video | uploaded |
|---|---|---|
| 142 Pac-Man 99 | `WB1xhN3YZKc` | 2021-12-18 |
| 145 Muppet RaceMania | `-0GmF73-3-M` | 2021-12-19 |
| 146 Super Mario Kart | `5FZF_lI35Kk` | 2021-12-20 |
| 147 Super Mario Odyssey | `c7i2rfznh04` | 2021-12-21 |
| 148 Super Mario 64 | `wdUAtSO94MM` | 2021-12-22 |
| 149 GeoGuessr | `l13IRYFIEB4` | 2021-12-23 |
| **150 Resident Evil Village** | `WrDX7ddLWmc` | **2021-12-24** |

The RE Village upload sits at the end of that chain, so it is the schedule's last
row — the **v2**. The 25 July attempt was never uploaded (its neighbours went up
on 2021-08-08 and 2021-08-09). The same table proves the other two: there is no
upload day between 12-18 and 12-19 for the two juzockt_ runs that sit between
Pac-Man 99 and Muppet RaceMania on the schedule.

**`upload_date` ordering is a cheap disambiguator and the tool already fetches
it.** It cost seven `yt-dlp -J` calls to settle three rows that no amount of
title matching could have separated.

## Reads

| tier | n | share |
|---|---:|---:|
| `high` | 130 | 88% |
| `medium` | 11 | |
| `low` | 4 | |
| `reject` | 1 | |
| unreadable (age gate) | 1 | |
| no timer found | 1 | |

All 16 readable non-`high` rows were resolved from frames rather than handed
over as a list: **8 corrections and 8 confirmations**, with the two unreadable
rows left off the site rather than guessed.

### The colour rule holds, and this event proves it rather than assuming it

The timer is **yellow while running and white once stopped**, as on Summer 2022
and Winter 2022, and *not* the orange/green the skill describes from later years.
Two frames 45s apart settle any row without judging a hue, and three rows caught
the transition in the act:

- **GeoGuessr** — yellow `0:16:26` at t=1286, white `0:16:54` at t=1331. Not
  +45s, so it stopped in between, at `0:16:54`.
- **GTA: Vice City** — yellow `4:55:23` at t=17760, white `4:55:55` at t=17805.
- **Trackmania** — yellow `0:30:33` at t=1979, white `0:30:57` at t=2024.

Every correction and confirmation below was taken from two frames, never one.

### The 8 corrections

| # | run | read | truth | what happened |
|---|---|---|---|---|
| 3 | Dark Messiah of Might and Magic — Any% (Relay Race) | `0:56:55` | **0:37:32** | `max` fallback on a 2p race layout |
| 4 | Deus Ex: Human Revolution — Any% | `0:51:59` | **0:51:39** | `3`→`5`, tens of seconds |
| 6 | Mega Man 11 — Any% (Normal, No OoB) | `0:35:47` | **0:33:47** | `3`→`5`, units of minutes |
| 8 | Air Control — Full Game | `0:28:15` | **0:28:13** | `3`→`5`, units of seconds |
| 11 | Final Fantasy IV — Any% (Normal) | `3:49:52` | **3:49:32** | `3`→`5`, tens of seconds |
| 14 | Job Simulator — All Jobs | `0:40:00` | **0:39:59** | read the estimate |
| 15 | LOVE 2: kuso — LOVE+kuso (100%) | `0:20:52` | **0:20:32** | `3`→`5`, tens of seconds |
| 17 | The Last Guardian — Any% | `3:45:00` | **3:38:30** | read the estimate |

**Five of the eight are the `3`/`5` glyph**, landing in three different digit
columns — `+20s`, `+2s`, `+2:00`. That is the README's point again: the size of
the error is set only by the column. A review looking for `+20:00` would have
found none of them, and a review looking for anything over a minute would have
found one.

**Job Simulator is the sharpest one on the list.** It read `0:40:00`, was flagged
by #65 as exactly its estimate — and the truth is `0:39:59`. The flag was right,
the cause was right, and the error was **one second**. A reviewer who treated the
#65 flag as "this is the estimate, the real time is elsewhere" would have gone
looking for a value that was already under their nose.

### The 8 confirmations

Runs 5, 7, 9, 10, 12, 13, 16 and 18 read correctly and were confirmed frame by
frame: Elmo's ABCs `0:08:56`, Star Wars Jedi: Fallen Order `1:45:46`, Crash
Bandicoot 2: N-Tranced `0:32:00`, Crash Bandicoot: N. Sane Trilogy `0:52:51`,
GeoGuessr `0:16:54`, GTA: Vice City `4:55:55`, Super Mario Kart `0:34:54`,
Trackmania `0:30:57`. They are recorded as `source=human` rather than left on the
OCR's own word, which is what takes the event's unvouched list to zero.

### A race reads one clock, and the clock it reads is the right one

**Dark Messiah of Might and Magic** is a relay race, `Team Duncan vs. Team
Percy`, on the `16x9-2p` layout. The overlay carries a finish flag per team —
`00:37:32` left, `00:28:42` right — plus one main timer in the shared info card,
and the main timer reads **`0:37:32`**: the slot ends when the *last* team
finishes. That is the value `runs.time` should hold, and it is the one the crop
was already pointed at. The tool's `0:56:55` was a `max` fallback that exceeded
the video's own 45:32 and was correctly rejected.

The skill says to route races to the human. On this layout that is still right,
but the reason is narrower than "a timer per runner": the per-runner values are
**flags in the top bar**, not timers, and the main timer is unambiguous.

### One tail held a different run's clock, and the tool survived it again

**Crash Bandicoot: N. Sane Trilogy** finishes at `0:52:51`, and a bonus run
starts on a reset clock about 30 seconds later. At 5s from the end the screen
reads `00:01:21`; at 50s from the end, `00:00:31`. Walking back: the real
`0:52:51` is frozen and white at t=3280 and t=3303, and the reset happens at
t≈3309.

**The OCR was right anyway**, because the 600s tail window contained the real
freeze as well as the bonus clock — exactly #50's Anodyne, for exactly the same
reason. Two events running, the tool has survived this by where `--tail`
happened to land rather than by logic.

## Evidence on the open tool tickets

### #67 — the height fallback: **nine for nine, and this is the fixture**

Nine of the first pass's 148 reads failed on #63's truncated-clip guard, after
its re-probe recovery had already run. **All nine read cleanly at `--height
720`, every one at 50/50 frames:**

| run | at `--height 480` | at `--height 720` |
|---|---|---|
| Alan Wake's American Nightmare | 92s of a 600s window | `0:56:06` **high** |
| Saturn Bomberman | 56s of 600s | `0:45:57` **high** |
| Mega Man: Dr Wily's Revenge | 363s of 600s | `0:25:08` **high** |
| Don't Spill Your Coffee! | 80s of 600s | `0:17:50` **high** |
| SpongeGlock SquarePants | 340s of 477s | `0:03:08` **high** |
| Trackmania | 495s of 600s | `0:30:57` medium |
| Mega Man 11 | 93s of 600s | `0:35:47` low |
| Deus Ex: Human Revolution | 110s of 600s | `0:51:59` low |
| Dark Messiah of Might and Magic | 179s of 600s | `0:56:55` reject |

Nine for nine is the rendition, not the network. A retry at the same height
would have been a coin toss; the height change was deterministic. #50 hit this
once and #63 landed too late to catch it; this event turns it into a regression
fixture of nine.

**The two guards compose exactly as designed**, and that is worth stating
plainly: #63 refused to read a confident answer off a 56-second clip, and #67's
workaround then recovered every one of those rows. Before #63 these nine would
have produced nine confident wrong times with nothing in any artefact to show
it — five of them are now `high`.

The practical consequence for the next backfill: **when a run fails with `clip is
only Ns of the Ms window`, re-run it at `--height 720` before touching it by
hand.** It costs one request per row.

### #63 — the guard, and what the new columns are worth

`frames_read`/`frames_total` reached the results CSV for the first time on a full
event, and four rows read fewer frames than they sampled:

| run | frames | outcome |
|---|---|---|
| Wild Animal Sports Day | 45/46 | `high`, correct |
| SpongeGlock SquarePants | 30/40 | `high`, correct |
| Two Worlds | 23/46 | `high`, correct |
| Elmo's ABCs | 37/50 | `low` → confirmed correct |

**A short read is not a wrong read.** Half the frames missing still produced a
correct `high` on Two Worlds. The column is diagnostic, not a reject criterion,
and nothing on this event suggests it should become one.

### #71 — crop area against the modal crop: **much weaker here than on #50**

Modal crop area is **4864 px** (`128×38`), and 120 of the 146 crops sit within
`51–120%` of it.

| crop area vs modal | n | corrections | confirmations | `high` |
|---|---:|---:|---:|---:|
| ≤ 25% | 2 | **2** | 0 | 0 |
| 51–120% | 120 | 1 | 6 | 113 |
| > 120% | 24 | 5 | 2 | **17** |

The small-crop band is 2 for 2, which agrees with #50's finding — but **there are
only two rows in it**, and both are the *same* failure: The Last Guardian (17%)
and Job Simulator (18%) are precisely the two runs that read their estimate. That
is not a coincidence. The estimate renders smaller than the timer, so a crop that
locks onto it is small by construction. **On this event the small-crop signal is
an estimate-read detector, not a wrong-element detector** — which is a narrower
claim than #50's, and it is the same claim #65 already tests directly and more
cheaply.

The large band is where the ticket runs into trouble: **17 of the 24 crops above
120% of modal read correctly**, including four at 367% and one at 514%. A
threshold in that direction would throw away far more than it caught.

**The event-wide modal is the wrong baseline, and this schedule shows why.** It
carries a `Layout` column with twelve distinct values, and crop area is a
property of the layout, not of the read:

| layout | n | commonest crop areas |
|---|---:|---|
| `16x9-1p` | 80 | 4864, 4826, 17640 |
| `4x3-1p` | 51 | 4864, 4826, 4902 |
| `16x9-2p` | 7 | 6840, 24990, 6795 |
| `GB-1p` | 2 | 17568, 10230 |
| `DS-1p` | 3 | 8250, 4750, 4788 |

Both `GB-1p` rows are 210% and 361% of the event modal, and **both are correct** —
they are Game Boy layouts with a physically larger timer. Carrying the `Layout`
column through and comparing against the **per-layout** modal is what #71 asks
for and what this event says it actually needs; against the event-wide modal the
signal is mostly layout noise.

### #66 — the estimate-ratio guard fired **zero times**

No row on this event carries a `reading is N.NNx the … estimate` reason at all.
The guard cost nothing and caught nothing, on the largest event in the backfill.

The one reset clock this event contains — Crash Bandicoot: N. Sane Trilogy —
**the guard could not have caught, because the tool read that run correctly.**
The reset was in the tail but the freeze was too, so no implausible value was
ever produced. That is the third event agreeing that the reset is the signal, and
the first to show a reset that produced no signal at all.

The running tally in `estimate-ratio-guard.md` is unchanged at 13 correct out of
34: this event added nothing to either column.

### #65 — a read equal to the estimate: **2 of 3, and the third is the warning**

| run | read | estimate | truth |
|---|---|---|---|
| The Last Guardian | `3:45:00` | 3:45:00 | **3:38:30** |
| Job Simulator | `0:40:00` | 0:40:00 | **0:39:59** |
| Crash Bandicoot 2: N-Tranced | `0:32:00` | 0:32:00 | **0:32:00** |

Crash Bandicoot 2: N-Tranced **genuinely finished on its estimate to the
second**, confirmed frozen at t=2004 and t=2049. This is the case the skill warns
about — "a run can genuinely finish on a round number, so confirm it, do not
assume it is wrong" — and it is the first time the backfill has actually hit it.
The demotion is right; treating the flag as a verdict would have replaced a
correct time with a wrong one.

Job Simulator is the mirror image: flagged for the right reason, wrong by one
second.

## The wall, and the request budget

**The bot wall never went up**, at the highest request count the project has
spent on a single event:

| | |
|---|---:|
| `resolve` searches | 151 |
| batch reads (first pass) | 148 |
| retry pass at 720p | 11 |
| hand searches and `-J` probes | 11 |
| review frames | ~32 |
| **total yt-dlp requests** | **~353** |
| oEmbed channel lookups (not yt-dlp) | 151 |

`seed` saved **147 requests**. Without it the first pass alone would have cost
~295 and the event ~500, past every wall the project has recorded (~220 Winter
2023, ~250 Summer 2025, ~275 Summer 2023, ~460 Winter 2024).

The one refusal was not the wall: **Minecraft (`R2pViwALnj8`) is age-gated**, and
yt-dlp answers `Sign in to confirm your age` on every attempt regardless of
concurrency or backoff. It is the first age-gated VOD the backfill has met.

## Throughput

Six shards, `--discard-clips`, one pass plus a short retry. Shards finished
between 2h 37m and 3h 20m — 148 reads in 3h 20m, or **0.74 runs/min against
#50's 1.1**. The spread is the run mix: this event carries 174 hours of VOD
including a 15h 48m pre-show block, where Winter 2022 carried far less.

## What to change next

1. **Re-read a truncated clip at `--height 720` automatically** (#67). Nine for
   nine on this event, deterministic, one request per row. `pipeline.fetch_window`
   already re-probes once for an over-reporting seeded duration; this is the same
   shape of recovery for the other half of the same failure, and it would have
   turned nine dead rows into five `high` reads with no human involved.
2. **Record `channel` in `resolved.csv` from oEmbed, not from a yt-dlp probe.**
   #50 asked for `channel_id` and priced it at "free, the search already returns
   it" — but `video.search()` drops it and adding it back to a `-J` probe costs a
   request per row against the wall. The oEmbed endpoint gives the same answer off
   the wall entirely, at 151 lookups per event in under a minute. That closes half
   of #102 without spending anything.
3. **Compare crop area against the per-layout modal, not the event modal** (#71).
   This schedule's `Layout` column has twelve values and the crop follows the
   layout; against the event-wide modal, 17 of 24 large crops are correct reads
   and the signal is mostly noise.
