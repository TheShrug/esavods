# ESA Summer Online 2020 — backfill

Issue #53, and **the last of the twelve**: with this merged, epic #31 closes.
One Horaro schedule (`summeronline`), tag `#ESASummerOnline`, shipped as
`ESA 2020 Summer Online`.

**172 schedule rows — the largest event of the backfill**, 21 more than #51.
Single-stream, like #50 and #51, so one CSV, one event name and one line in the
manifest. The name is new: the restored production database holds
`ESA 2020 Winter (One)`/`(Two)` and nothing for the summer, and this is a
different event from either — ESA held no in-person summer marathon in 2020, and
the schedule calls itself `2020 Summer Online`.

- **Settings**: `--height 480 --tail 600 --step 12`, six shards, one pass plus a
  `--resume` pass after a local network outage. **No 720p pass was needed.**
- **Wall time**: 1h 13m for the first 46 reads, then 3h 07m for the remaining
  127 — 4h 20m for 169 reads, or 0.65 runs/min.
- **The bot wall never went up**, across roughly 385 yt-dlp requests — more than
  #51's 353, and the most the project has spent on one event.
- **Outcome**: **169 of 172 schedule rows live with a time.** 149 read `high`
  and shipped unreviewed, 20 were resolved from frames by hand, and **none
  ships on an unconfirmed reading.**

## Outcome

| | |
|---|---:|
| schedule rows | 172 |
| rows with an ESA upload | 169 |
| shipped with a time | **169** |
| `high`, shipped unreviewed | **149** |
| resolved from frames (`human`) | **20** |
| shipped unconfirmed | **0** |
| no time, not shipped | 3 |

**149 of 169 accepted without review — 88%**, against 88% on Summer 2021, 79% on
Winter 2022, 81% on both Summer 2022 runs and 89% on Winter 2021.
`release-event.sh` wrote no `unvouched.md`, because there is nothing on the list.

The three rows that do not ship, and why:

| row | why |
|---|---|
| Break The Record: LIVE — Doom Eternal (No Major Glitches) | not a run: a 13h30m partner-marathon block, `Layout: BTRL`, whose Game cell links `esamarathon.com` rather than a VOD. No ESA upload exists. |
| Super Monkey Ball — All Difficulties (No Extras, Warpless) | no ESA upload |
| Pokémon Red — Any% | no *separate* ESA upload — the run is inside Pokémon Blue's video. See below. |

**Pokémon Red is the one that is shipped-or-explained rather than simply
missing**, and its time is known: `0:03:33`, confirmed frozen at t=1665 in
`dKulNKkwIYQ`. It is left off only because that video id already carries the
Pokémon Blue row, and one run per video id is the invariant the CSV check
enforces. Nothing needs re-reading to add it if the model ever grows a
timestamped VOD reference.

## Resolution

No ESA timing sheet exists for 2020 (`data/run-timings/` holds 2022 and 2026
only), so `slot-exact` was unavailable. The schedule's Game cells link **Twitch**
VODs — 171 of 172, all long deleted — and not one links YouTube, so unlike #51
there is not even a single `horaro-link` answer. All 172 rows are title searches.

| how | n |
|---|---:|
| `tag-game-runner` | 166 |
| `tag-game` | 3 |
| `no-upload` (corrected by hand) | **3** |

The raw resolve was 166 `tag-game-runner`, 3 `tag-game`, 3 `weak`, and no
`no-hits` — **the healthiest shape any backfill has returned**, better than
#51's and reached without any of the help #51 had.

### The year-less hashtag was not the risk it looked like, and the reason is worth stating

#53 was flagged in advance as the event most exposed to resolver error, because
`#ESASummerOnline` carries no year where every other tag does. `resolve` builds
its query as `<game> #<tag>` and `score()` gates on the tag before `rank()` ever
runs, so a tag that does not pin a year should let other years' uploads through.

**It did not, because the tag is a unique literal even though it names no year.**
ESA's other 2020 uploads carry `#ESATogether2020` and `#ESAWinter20`; no other
event has ever used `#ESASummerOnline`. Every one of the 169 matched titles
carries it verbatim, and no title carrying it belongs to another event.

The lesson generalises: **what matters is whether the tag is unique, not whether
it encodes a year.** A year is one way to buy uniqueness and it is not the only
one. The risk to look for on a future event is a tag that is a *prefix* of, or
identical to, another event's — `#ESASummer` against `#ESASummer21` would be a
real problem in a way `#ESASummerOnline` never was.

### All 169 matches are ESA's own uploads, and the oEmbed check found the one that was not (#102)

#51 established that YouTube's public oEmbed endpoint returns a video's channel
off the yt-dlp request path entirely, and this event used it as the first check
after `resolve` rather than as a post-hoc audit. 171 lookups, under a minute, no
cost against the wall:

```
ESA Speedrunning   170
FireDragon           1
```

The single outlier is **Super Monkey Ball**, matched at `weak(0.227)` to
`6LQuHWqCYoc`, *"We got the World Record in Monkey Target for GONGON!"* — an
unrelated upload by a different channel. `resolve` had already flagged it as
`weak`, so the channel check confirmed a suspicion rather than raising one, but
it confirmed it in seconds and with certainty.

**No restream reached this event at all.** The exposure #50 lost eleven runs to
is absent here for the same reason it was absent on #51: the third-party
re-uploads of this marathon do not carry ESA's hashtag, so they never clear the
tag gate. Two events running, the `rank()` defect in #102 has been invisible
rather than fixed — it remains a live hazard for any event whose restreamer
happens to copy the hashtag, and nothing in the tool would catch it.

**The recommendation from #51 stands and this event is the second vote for it:
record `channel` in `resolved.csv` from oEmbed.** It is free, it is off the wall,
and used *before* the batch it turns a two-hour wasted read into a ten-second
check.

### Three rows resolved by hand, and only one of them was a resolver error

| row | how it announced itself | what it was |
|---|---|---|
| Super Monkey Ball | `weak(0.227)` + non-ESA channel | no ESA upload; took an unrelated video |
| Break The Record: LIVE | `weak(0.741)` | not a run at all; matched a `#BTRL4` video from a different year |
| Pokémon Red | **duplicate video id** | real run, real video — but the video is Pokémon Blue's |

The duplicate-id symptom did its job again: **one duplicate in the whole event,
and it was the one row that needed thinking about.** That is now four events
running where every hand correction announced itself either as a duplicate id or
as a sub-`tag-game` verdict.

### One video, two scheduled runs, and the trap it sets

Rows 140 and 141 are Pokémon Blue `Any% (No Save Corruption)` and Pokémon Red
`Any%`, both by G3neziz, minutes apart. **Horaro links them to the same Twitch
VOD, the second with `?t=21m25s`** — which says outright that ESA streamed them
as one block. ESA's single YouTube upload is titled for Blue and runs 29:31.

That makes the tail of `dKulNKkwIYQ` hold **Pokémon Red's** clock, not Blue's,
and the tool duly read `0:03:33` and attached it to the Blue row. Walking the
video settles both:

| video position | screen |
|---|---|
| t=1260 | Pokémon Blue, white `00:18:23` |
| t=1285 | Pokémon Blue, white `00:18:23` — frozen |
| t=1340 | **Pokémon Red, `00:00:00`** |
| t=1650 | Pokémon Red, yellow `00:03:19` |
| t=1665 | Pokémon Red, white `00:03:33` |

So Blue is `0:18:23` and Red is `0:03:33`, and the OCR's reading was a correct
reading of the wrong run. **The horaro link's `?t=` fragment predicted this
before a single frame was downloaded** — it is the cheapest possible warning that
two rows share a recording, and `resolve` currently throws it away when it
strips the markdown link.

## Reads

| tier | n | share |
|---|---:|---:|
| `high` | 149 | 88% |
| `medium` | 12 | |
| `low` | 4 | |
| `reject` | 4 | |
| unreadable | 0 | |

All 20 non-`high` rows were resolved from frames rather than handed over as a
list: **11 corrections and 9 confirmations**, with nothing left unresolved and
nothing shipped on a guess. That is the largest hand-review pass of the backfill
and the first to reach twenty.

### The colour rule holds for a third event, and this one is 2020

The timer is **yellow while running and white once stopped** — the same as
Summer 2022, Winter 2022 and Summer 2021, and not the orange/green the skill
describes from later years. Every correction and confirmation below was taken
from at least two frames.

**The layout puts the timer in one of three places, and the bottom strip is not
always one of them.** Cropping the bottom quarter — the recipe in the skill —
read cleanly on the `16x9-1p`/`4x3-1p` variants that carry a full-width info bar,
missed entirely on the variants that put the info card down the *left side*, and
cut the timer in half on the `4x3-2p` race layout, which carries it higher. Six
of the twenty rows looked like "no timer in the tail" for that reason alone.
**Reading the whole 1280×720 frame is legible enough for the timer in every
layout this event uses**, and it costs nothing extra — the download is the same.
That is the frame recipe to carry forward.

### The 11 corrections

| # | run | read | truth | what happened |
|---|---|---|---|---|
| 1 | Knytt Stories — Deep Freeze (Any%, No Major Skips) | `0:02:24` | **0:54:46** | reset clock: a bonus level ran after the run |
| 3 | Pokémon Blue — Any% (No Save Corruption) | `0:03:33` | **0:18:23** | the tail is the *next scheduled run* |
| 4 | TrackMania — Training & Summer 2020 | `0:50:00` | **0:27:27** | wrong element; `max` fallback exceeded the video |
| 5 | Diddy Kong Racing — 100% | `1:48:52` | **1:48:32** | `3`→`5`, tens of seconds |
| 6 | Pokémon Sword / Shield — Trade Alt Main (Litten) | `4:28:45` | **4:28:43** | `3`→`5`, units of seconds |
| 7 | Risk of Rain — Any% (Monsoon) | `0:15:15` | **0:13:15** | `3`→`5`, units of minutes |
| 8 | Super Mario World — 96 Exit | `1:24:52` | **1:24:32** | `3`→`5`, tens of seconds |
| 10 | Clock Tower 3 — Normal Mode | `1:25:51` | **1:25:31** | `3`→`5`, tens of seconds |
| 12 | Dragon Ball Z: Budokai 3 (HD) — Goku's Story Any% (Capsules) | `0:12:59` | **0:13:00** | one second under a round finish |
| 16 | Sonic the Hedgehog (2006) — Silver's Story (No MSG) | `1:00:00` | **0:52:18** | read the estimate |
| 18 | The Legend of Zelda: A Link To The Past — Randomizer (Crowd Control) | `1:56:07` | **1:58:57** | race layout; read a per-runner in-game total |

**Five of the eleven are the `3`/`5` glyph**, in three different digit columns —
`+2s`, `+20s`, `+2:00`. Five of eight on #51, six of eighteen on #50, five of
eleven here. It remains the single most common way a time comes out wrong, and
the size of the error remains a property of the column and nothing else. A review
looking for a specific magnitude would have found roughly one of these five.

**Dragon Ball Z is the sharpest one on the list, and it is #51's Job Simulator
again.** The tool read `0:12:59`; the screen, white and frozen at two positions
57 seconds apart, says `00:13:00`. The error is one second, in the direction that
makes the true value the rounder one. Two events running, the smallest error in
the set has been a single second next to a round number.

### The 9 confirmations

Runs 2, 9, 11, 13, 14, 15, 17, 19 and 20 read correctly and were confirmed frame
by frame: Pokémon Black `3:35:26`, Awful Havrd Games `0:56:14`, Dark SASI
`0:12:03`, Goat Simulator `0:20:00`, Pokémon Puzzle League `0:25:14`, Simon the
Sorcerer `1:04:03`, Super Mario Land `0:14:49`, Timeline `0:24:02`, TrackMania
Nations Forever `1:07:27`. They ship as `source=human` rather than on the OCR's
own word, which is what takes the event's unvouched list to zero.

### Two of those confirmations are guards firing on correct reads

**Pokémon Black was rejected for reading longer than its own video** — `3:35:26`
out of a 3:31:38 upload — and the screen says `03:35:26`, yellow `03:34:46` at
t=12578 and white `03:35:26` at t=12633. The run is genuinely longer than the
recording because **ESA's upload begins about five minutes after the timer
started**. The `secs > dur` check is not wrong in principle, but this is its
first false positive on a single-part VOD, and the only reason the run ships is
that a human answer is exempt from it.

**Goat Simulator finished on exactly `0:20:00`**, white and frozen at t=1268 and
t=1285, against a `0:16:00` estimate. A round number is not a red flag by itself
— this is the second event running to produce a genuine one (#51's Crash
Bandicoot 2: N-Tranced was the first).

## Evidence on the open tool tickets

### #71 — crop area against the modal crop: **3 for 3, and the per-layout refinement would have cost one of them**

Event-wide modal crop area is **4864 px**, and 156 of 169 crops sit within
`51–120%` of it.

| crop area vs event modal | n | corrections | confirmations | `high` |
|---|---:|---:|---:|---:|
| ≤ 25% | 2 | **2** | 0 | **0** |
| 26–50% | 1 | **1** | 0 | **0** |
| 51–120% | 156 | 7 | 7 | 142 |
| > 120% | 10 | 1 | 2 | 7 |

**Every crop below half the event modal is a wrong reading, and there are no
false positives at all.** Across the three events that have measured this, the
band is now **7 for 7** — 2 on #50, 2 on #51, 3 here.

**And this event contradicts #51's narrowing of the claim.** #51 concluded the
small-crop signal was "an estimate-read detector, not a wrong-element detector",
because both of its small crops were runs that read their own estimate. Here
only one of three is:

| run | crop % of event modal | read | truth | is it an estimate read? |
|---|---:|---|---|---|
| Sonic the Hedgehog (2006) | 17% | `1:00:00` | `0:52:18` | yes — #65 flagged it too |
| TrackMania | 17% | `0:50:00` | `0:27:27` | **no** — estimate is `0:30:00` |
| A Link To The Past | 37% | `1:56:07` | `1:58:57` | **no** — estimate is `3:00:00` |

TrackMania and A Link To The Past are wrong-element reads that #65 cannot see,
and the crop caught both. **The signal is broader than #51 concluded**, and on
this event it is the only automatic criterion that would have found them.

**The per-layout baseline #51 asked for would have lost A Link To The Past.** Its
layout is `4x3-2p` and it is the *only* row on that layout, so the per-layout
modal is its own area and it scores 100%:

| layout | n | commonest crop areas |
|---|---:|---|
| `16x9-1p` | 74 | 4864, 4826, 5248 |
| `4x3-1p` | 74 | 4864, 4826, 4750 |
| `GB-1p` | 7 | 4826, 8625, 8382 |
| `GBA-1p` | 3 | 4864 |
| `3DS-1p` | 2 | 4864 |
| `DS-1p` | 2 | 7750, 8300 |
| `4x3-2p` | **1** | 1804 |
| `GB-2p` | **1** | 10863 |

Per-layout does help where #51 said it does — on the *large* side, where
`GB-1p`'s Super Mario Land is 172% of the event modal and a perfectly correct
read — but half this schedule's layouts carry three rows or fewer, and a layout
of one row cannot be its own baseline.

**So the third reading settles it as a narrower rule than either previous event
proposed:** flag a crop below ~50% of the **event-wide** modal, and use the
per-layout modal only to *suppress* large-crop noise where the layout has enough
rows to have a modal at all. A threshold in the large direction remains a bad
idea in either baseline — 7 of this event's 10 large crops are correct reads.

### #66 — the estimate-ratio guard: **2 for 2, and both are reset clocks**

Two rows carry a `reading is N.NNx the … estimate` reason, and **both rejections
were right**:

| run | ratio | read | truth | why the reading was wrong |
|---|---:|---|---|---|
| Knytt Stories | 0.04x | `0:02:24` | `0:54:46` | a bonus level, `Don't Eat the Mushroom`, on a reset clock |
| Pokémon Blue | 0.20x | `0:03:33` | `0:18:23` | the *next scheduled run* on a reset clock |

That takes the running tally in `estimate-ratio-guard.md` to **17 correct of
38**, with no new false alarms. Updating it turned up a bookkeeping error worth
naming: **Winter 2022's own 2-for-2 was never added to that table**, and #51
carried the total forward as "unchanged at 13 of 34" without noticing, so the
pre-#53 figure was really 15 of 36. The guard's record is meaningfully better
than the issue claims, and better than this directory has been saying.

Winter 2022 was also 2 for 2, so this is the second event to score it, not the
first.

**Both true positives are the same shape every previous true positive was: a
clock that reset inside the sampled window.** Seven events have now produced true
positives and every one of them is a reset. This event is the strongest evidence
yet for the replacement the file already recommends — **detect the reset, not the
ratio** — because it is the first event where the ratio guard fired *only* on
resets and therefore cost nothing.

It also produced a reset the guard could not have caught, for the third event
running. **Goat Simulator** runs a bonus `Goat MMO` segment after the run, on a
clock reset to zero: yellow `00:02:21` at t=1428, white `00:03:16` at t=1541.
The tool still read `0:20:00` correctly, because the 600s tail window contained
the real freeze as well as the bonus clock — #50's Anodyne and #51's Crash
Bandicoot for the same reason. **Three events running, the tool has survived a
reset by where `--tail` happened to land rather than by logic**, and a reset
detector would make that structural instead of lucky.

### #65 — a read equal to the estimate: **1 for 1**

| run | read | estimate | truth |
|---|---|---|---|
| Sonic the Hedgehog (2006) | `1:00:00` | 1:00:00 | **0:52:18** |

One flag, correct, demoted rather than dropped — which is right, because Goat
Simulator finished on a round `0:20:00` on this same event and would have been
destroyed by a rule that treated roundness as proof.

### #63 and #67 — the truncated-clip guard fired three times, and the height bump was **not** what fixed it

Three rows failed `clip is only Ns of the Ms window` in the first pass:

| run | first pass | resume pass, **same `--height 480`** |
|---|---|---|
| Goat Simulator | 382s of a 600s window | `0:20:00`, 50/50 frames |
| Pepsiman: The Forbidden Drink | 421s of 600s | read cleanly |
| Omensight | 319s of 600s | read cleanly |

**All three recovered on a plain retry at the same height.** That is a direct
counterexample to #51's conclusion that the failure is "the rendition, not the
network" — though not a clean one, because this event's first pass died in a
local DNS outage and those three truncations sit right at its edge. What it does
establish is that **`clip is only Ns of the Ms window` has at least two causes**,
and that a same-height retry is worth one request before reaching for 720p. The
refinement to #67's proposed fix: retry once at the same height, then bump.

`frames_read`/`frames_total` reached the results CSV again and three rows read
fewer frames than they sampled — Pokémon Blue 49/50 (`reject`), Super Mario Land
49/50 (`medium`, correct), Wave Race 49/50 (`high`, correct, unreviewed). **A
short read is still not a wrong read**, and one frame short of fifty is noise.

### The `secs > dur` check has its first single-part false positive (new)

Pokémon Black above. Worth recording against whatever ticket eventually owns that
check: the rule assumes the upload contains the whole run, and ESA's 2020 uploads
do not always start where the timer did.

## The wall, and the request budget

**The bot wall never went up**, at the highest request count the project has
spent on a single event:

| | |
|---|---:|
| `resolve` searches | 172 |
| batch reads, first pass | ~50 |
| batch reads, resume pass | 127 |
| hand searches | 6 |
| review frame grabs | 30 |
| **total yt-dlp requests** | **~385** |
| oEmbed channel lookups (not yt-dlp) | 171 |

`seed` saved **169 requests**. Without it the batch alone would have cost ~346
and the event ~554 — past every wall the project has recorded (~220 Winter 2023,
~250 Summer 2025, ~275 Summer 2023, ~460 Winter 2024). At 172 rows it is no
longer an optimisation.

**The one interruption was not YouTube.** 123 of the first pass's 169 rows failed
with `[Errno -2] Name or service not known` — DNS resolution inside the
containers — and all six shards died within seconds of each other, which is the
signature. Those requests never left the machine, so they cost nothing against
the wall, and `--resume` re-read every one of them. The batch's own bot-wall
detector correctly did *not* classify them as refusals (exit 1, not 75).

Worth naming for the next reader: **a whole-fleet failure that looks like the
wall is more likely to be the network**, and the two are told apart by the error
string, not by the shape of the failure.

## Throughput

Six shards, `--discard-clips`. 46 reads in 1h 13m, then 127 in 3h 07m — 169
reads in 4h 20m of container time, or **0.65 runs/min against #51's 0.74 and
#50's 1.1**. The spread is the run mix again: this event carries a 11h 59m
Skies of Arcadia: Legends VOD (a genuine `11:55:41` run, read `high`, and the
only row over eight hours) among 172 rows.

---

# What the twelve events taught

Twelve events, roughly 1,700 runs, and one tool that grew through all of them.
This is the last look at it with fresh eyes, so what follows is the summary that
`runs/` as a whole supports rather than what any single event suggested.

## Where the tool is reliable

**`high` is the finding.** Across twelve events it has covered 79–89% of every
event read and been wrong a handful of times in over a thousand runs — 100 of 101
on #49's ground truth. Shipping it unreviewed is not a shortcut; it is the
measured behaviour, and it is what makes a 172-row event a day's work instead of
a week's.

**Resolution is a solved problem when the organisers name their own video, and
nearly solved when they do not.** `horaro-link` was 170 of 170 on Summer 2025.
Title search with a three-way agreement gate has run 129/142, 137/151 and now
166/172 at `tag-game-runner`, and the errors are not distributed at random: on
four consecutive events **every single hand correction announced itself either as
a duplicate video id or as a verdict below `tag-game`.** Those two signals are
the whole audit.

**The failure modes are few, and they are named.** Three recur and nothing else
does:

1. **The `3`/`5` glyph** — 8 of 10 on Winter 2021, 6 of 18 on #50, 5 of 8 on
   #51, 5 of 11 here. The magnitude is set by the digit column and by nothing
   else, so no threshold on size will find them.
2. **Reading the estimate** — the dominant error on Summer 2025, and since #65
   the tool flags it itself.
3. **A reset clock in the tail** — a bonus run, an incentive, a second attempt,
   or (here) the next scheduled run.

Everything else the twelve events produced is a variation on one of those three.

## Where it is not reliable

**Everything below `high` is roughly a coin toss, and it has stayed one.** This
event's 20 flagged rows split 11 wrong, 9 right. #51's split 8 and 8. The tiers
are doing their job — they are separating "trust this" from "look at this" — but
`medium` is not a weak `high`, it is a request for eyes, and four events have now
shown that resolving them from frames rather than handing over a list is both
faster and the only way the unvouched list reaches zero.

**A confident time read off the wrong video is invisible.** No artefact the tool
produces can see it. The duplicate-id check catches the case where two rows
collide; nothing catches a single row quietly pointed at a restream, which is
#102, and which cost #50 eleven runs at full confidence. **The oEmbed channel
lookup closes it for free and off the request path**, and two events have now
recommended it. It is the single highest-value change left.

**Races still need a person, but for a narrower reason than the docs say.** The
docs say "a timer per runner, only one is read". On the 2020 and 2021 two-player
layouts the per-runner values are *flags*, and the main timer is unambiguous —
what actually broke A Link To The Past here was that the layout puts the timer
somewhere the crop did not expect, and #51's Dark Messiah was a `max` fallback.
Two events, two race failures, neither of them the documented cause.

**Wall time is bought with concurrency and nothing else**, and it has not
improved: 1.1, 0.74 and 0.65 runs/min on the last three events, driven entirely
by how many hours of VOD the event carries.

## Which open ticket the evidence now most supports

In order:

1. **#102 — record the channel in `resolved.csv`, from oEmbed.** It is the only
   open ticket addressing an error class that is *silent*, it costs nothing
   against the wall, and it is the only one where the harm is already measured
   at eleven runs on a single event. Two independent events have now recommended
   the same implementation. **Do this one first.**
2. **#66 — replace the estimate ratio with a reset detector.** The tally is 17
   correct of 38, so the guard is not the pure noise the issue claims; but
   **every true positive across seven events is a clock that reset inside the
   sampled window**, and `batch` already reads every frame in order, so the
   replacement needs no extra request. Three events have also shown the tool
   surviving a reset purely by where `--tail` landed. The ratio should go, and
   what should replace it is now unambiguous.
3. **#71 — flag a crop below ~50% of the event modal.** Three events, 7 for 7,
   no false positives, and it catches wrong-element reads that #65 cannot. Ship
   it against the **event-wide** modal; this event shows the per-layout baseline
   #51 proposed would lose a true positive on any layout with one row, and it
   should be used only to damp large-crop noise.

**Not #67 and not #69.** #67 is half fixed and this event's three truncated
clips all recovered on a same-height retry, which weakens the case for the height
fallback being the mechanism. #69 is a performance spike, and throughput has
never been what limits an event — the wall and the review pass are.

## Two smaller things worth carrying forward

- **Read the whole frame, not the bottom strip.** The skill's
  `crop=iw:ih/5:0:ih*4/5` recipe assumes an info bar along the bottom. Three of
  the layouts on this event put the timer down the left side or higher up, and
  the crop silently returned "no timer" for six rows that had one. The full
  1280×720 frame is legible and costs nothing more.
- **Horaro's `?t=` fragments are free structural information.** The one row on
  this event that no title check could have separated was announced by a `?t=`
  in its own schedule cell, hours before anything was downloaded. `resolve`
  strips it.
