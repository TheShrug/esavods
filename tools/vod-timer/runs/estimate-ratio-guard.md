# The estimate-ratio guard (#66) — the tally across every event read so far

`resolve()` rejects a reading whose ratio to the run's horaro estimate falls
outside `0.4x`–`2.0x`. #66 proposes dropping that from the reject criteria on a
record of **0 for 13**.

This file is the count, reconstructed from the eight event write-ups in this
directory rather than from the issue. **The record is not 0 for 13.** It is
**13 correct out of 34 rejections**, and the issue's headline figure is not
supported by the write-ups it cites.

## Per event

Ordered by the date the write-up landed, which is the order the evidence
accumulated. "Correct" means the rejection was right — the *reading* was wrong.

| event | write-up | ratio rejections | correct | false alarms | unresolved |
|---|---|---|---|---|---|
| ESA Winter 2026 | `esa-winter-2026.md` | 7 | 0 | 7 | — |
| ESA Winter 2021 | `esa-winter-2021.md` | 1 | 0 | 1 | — |
| ESA Summer 2025 | `esa-summer-2025.md` | 2 | 1 | 1 | — |
| ESA Summer 2024 | `esa-summer-2024.md` | 1 | 0 | 1 | — |
| ESA Winter 2024 | `esa-winter-2024.md` | 8 | 5 | 3 | — |
| ESA Summer 2023 | `esa-summer-2023.md` | 6 | 2 | 4 | — |
| ESA Winter 2023 | `esa-winter-2023.md` | 6 | 3 | 2 | 1 |
| ESA Summer 2022 | `esa-summer-2022.md` | 3 | 2 | 1 | — |
| **total** | | **34** | **13** | **20** | **1** |

Five of the eight events produced true positives. The first four events read —
Winter 2026, Winter 2021, Summer 2025, Summer 2024 — produced none, which is
where the "0 for N" record came from; every event read since has produced them.

## Where the issue's figures come from, and why they do not hold

- **"12 combined" across Winter 2026 and Winter 2021 is not supported.** Winter
  2026's write-up records **8 rejects in total on the whole event**, of which
  **7** fired on the ratio, and Winter 2021 records exactly **1** (Be-Music
  Source). That is 8, not 12. Winter 2021's own write-up cites a "0-for-11
  record on Winter 2026", which Winter 2026's tier table (`reject | 8`)
  contradicts; the 11 is the likely source of the issue's 12.
- **Summer 2025 was 1 for 2, not 0 for 1.** The write-up counts only Ghoul
  School (`0:07:02`, 0.35x, correct read — a false alarm). But Super Mario
  Bros. 3 read `0:04:11` against a `1:00:00` estimate on the same event, which
  is **0.07x**, and its true time is `0:57:08`. Neither surviving criterion can
  fire on it — `0:04:11` is over a minute and under the video's own length — so
  the ratio guard is what rejected it, and the rejection was right. The issue
  concedes the guard "happened to flag it"; it was not then subtracted from the
  0-for-N count. Excluding it, the overall tally is 12 of 33 rather than 13 of 34.
- **Winter 2024 is 5 of 8, not 4 of 7.** The issue comment reporting that event
  says seven of the eight were checked and four rejections were correct. The
  write-up's table has all eight checked and **five** wrong readings — Resident
  Evil 5, Super Princess Peach, Splatoon 2, Deus Ex: Mankind Divided and Link's
  Awakening. The write-up is the primary record and this file follows it.

## What the true positives actually are

Every true positive on every event is one shape: **a clock that reset inside the
sampled window**, so the tail holds a bonus run, an incentive, a second attempt
or an estimate rather than the run's own frozen time.

| event | run | read | true | ratio |
|---|---|---|---|---|
| Winter 2024 | Resident Evil 5 | `0:11:20` | `2:11:32` | 0.08x |
| Winter 2024 | Super Princess Peach | `0:11:07` | `1:35:42` | 0.12x |
| Winter 2024 | Splatoon 2 | `0:12:17` | `1:32:32` | 0.13x |
| Winter 2024 | Deus Ex: Mankind Divided | `0:09:00` | `0:43:08` | 0.14x |
| Winter 2024 | Link's Awakening | `0:10:01` | `0:43:26` | 0.21x |
| Winter 2023 | Metroid Dread | `0:12:45` | bonus run's reset clock | 0.20x |
| Winter 2023 | Quake Mission Pack 1 | `0:02:26` | read fell before the finish | 0.19x |
| Winter 2023 | Mirror's Edge | `10:40:00` | estimate read | 16.00x |
| Summer 2023 | Zelda: A Link to the Past | `0:05:53` | `0:02:39` | 0.37x |
| Summer 2023 | Closing Speech | `1:00:00` | no timer on the layout | 4.00x |
| Summer 2022 | GeoGuessr | `0:10:39` | `0:25:36` | 0.30x |
| Summer 2022 | Super Mario Sunshine | `0:09:45` | `2:36:09` | 0.06x |
| Summer 2025 | Super Mario Bros. 3 | `0:04:11` | `0:57:08` | 0.07x |

Two of the thirteen were caught by something else as well: Summer 2023's
Closing Speech also failed the longer-than-video guard, and Winter 2023's
Mirror's Edge is an estimate read that #65's `equals_estimate` would demote.
The remaining eleven had no other signal against them — Winter 2024's write-up
is explicit that without the ratio its five would have shipped as
plausible-looking times out by up to two hours.

## Why narrowing the bound does not work either

Winter 2024 proposed cutting the lower bound from `0.4x` to about `0.22x`, on
the grounds that all five of its true positives sat at or below 0.21x and all
three of its false alarms at or above 0.24x. The two events read after it both
tested that proposal against their own data and both rejected it:

- **Summer 2023 splits the other way round.** Its four false alarms sit at
  0.08x, 0.19x, 0.20x and 0.25x — all correct times — and its one true positive
  is the *highest* ratio of the five at 0.37x. A 0.22x cut keeps three of the
  four false alarms and drops the only real catch.
- **Summer 2022 says the same** — a 0.22x cut would keep its false alarm
  (Friday the 13th, 0.39x) and drop both true positives (Super Mario Sunshine
  0.06x, GeoGuessr 0.30x).
- **Winter 2023 found the guard's input is wrong for a whole class of row.**
  Both its false alarms compare against horaro's *slot*, which for an IRL or
  showcase segment includes setup and interview time the run's own estimate does
  not. IKEA Billy Assembly is 0.10x against horaro's `1:00:00` and 0.63x against
  the `00:10:00` printed on the layout beside the clock; No More Papers Please is
  0.18x against horaro and 0.93x against the screen. Neither is anomalous at all
  against the number the guard was supposed to be using.

There is no threshold that separates the two populations, because a genuinely
short run and a reset clock are the same shape to a rule that sees only a ratio.
What varies is how long the bonus segment happened to run.

## What the evidence points at instead

The three most recent write-ups converge on the same recommendation: **the reset
is the signal, not the ratio.** A value that *decreases* inside the sampled
window identifies every true positive above and rejects none of the short-run
false alarms. `batch` already reads every frame in order, so it needs no extra
request. Winter 2024 raises it as its improvement 3; Summer 2023 confirms it
covers that event's true positive as well; Summer 2022's five reset clocks are
the same shape.

Two secondary findings, both cheap and both independent of the threshold:

- **Read the estimate off the layout, not off horaro** (Winter 2023). It is in
  every frame the tool already downloads, and it is the number the guard was
  always meant to compare against.
- **Flag a calibrated crop much smaller than the event's modal crop** (#71).
  14 for 14 with no false positives across 262 normally-sized crops, and it
  catches the estimate-read class the ratio's upper bound was catching by
  accident.

## Caveat on comparing counts across events

The resolver has changed substantially over these eight events — the ramp-band
restriction on plateau candidates, the modal-offset arbitration, the plausible
fallback. A rejection count is a property of the pipeline that produced it as
much as of the guard, so the per-event rows are not strictly a like-for-like
series. The re-run recorded in `validation/esa-summer-2022/results.csv` shows
this directly: on the current resolver only GeoGuessr still carries a
ratio-alone rejection on Stream One. What the series does support is the shape
of the finding — the guard has true positives, they are all reset clocks, and
they are not separable from short runs by a threshold.
