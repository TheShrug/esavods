# ESA Winter 2021 — backfill

Issue #52. One Horaro schedule (`2021-winter`), tag `#ESAWinter21`, shipped as the
single event `ESA 2021 Winter`.

- **Settings**: `--height 480 --tail 600 --step 12`, six shards.
- **Wall time**: 2h 00m 30s for 141 videos (169h of source material). Resolution
  took a further ~4 min.
- **Outcome**: 139 of 142 scheduled runs live with a time.

## Resolution

142 runs: 129 `tag-game-runner`, 9 `tag-game`, 3 `weak`, 1 `no-hits`, and **no
duplicate video ids**. Only *Metal Gear Ghost Babel* found no video at all.

This reproduced the distribution recorded in the skill exactly, which is worth
noting on its own: resolution against title agreement is repeatable, and the
numbers in the docs are not a one-off.

### Re-resolved after #75

This event was the control for #75 — it is the one that must not get worse when
the runner comes out of the search query. It got better. Nothing was
re-imported; the same `resolve --horaro 2021-winter --tag ESAWinter21` now
returns:

| how | first pass | after #75 |
|---|---|---|
| `tag-game-runner` | 129 | **138** |
| `tag-game` | 9 | 3 |
| `weak` | 3 | **1** |
| `no-hits` | 1 | **0** |

*Metal Gear Ghost Babel*, the one run that found no video at all, had a video
the whole time: `g2p1L9okYaQ`, titled `Metal Gear Ghost Babel [Any% (Easy)] by
CDOSKEZ`. The schedule spells that runner `C\_DOS\_KEZ`, markdown escapes and
all, and that string in the query was enough for YouTube to return nothing.

141 of the 142 rows land on a title carrying every word of their game name. The
exception is the Opening Speech, which takes the Closing Speech's video at
`weak` — the only duplicate video id in the event, and both speeches are the
two runs with no timer on screen and no time to ship.

## Reads

| tier | n | shipped |
|---|---|---|
| high | 125 | yes |
| human | 10 | yes |
| medium | 3 | yes, unconfirmed |
| reject | 1 | yes, unconfirmed |
| no time at all | 2 | no |

**125 of 141 accepted without review — 89% coverage, against 81% on Summer 2022.**
16 went to a person; 14 of those were `tag-game-runner` matches and 2 were `weak`,
so a weak resolve does predict a bad read, but it is nowhere near the main source
of them.

The two with no time are the Opening and Closing Speeches, which have no timer on
screen. That is the correct answer, not a failure.

## The important finding: `3` is read as `5`, in every digit position

The reviewer corrected 10 runs. Eight of the ten are the **same single digit
confusion**, and the size of the error is set purely by which column the digit sat in:

| error | column | runs |
|---|---|---|
| +2s | units of seconds | Bloodstained `0:28:15`→`0:28:13`, Cyberpunk 2077 `3:18:35`→`3:18:33`, Devil May Cry 2 `0:48:15`→`0:48:13` |
| +20s | tens of seconds | Grand Theft Auto 2 `3:11:55`→`3:11:35` |
| +2:00 | units of minutes | Crash Bash `2:15:16`→`2:13:16`, Final Fantasy XV `4:25:09`→`4:23:09`, Touhou: Scarlet Curiosity `1:05:06`→`1:03:06`, Hylics 2 `0:45:48`→`0:43:48` |

The README already documents this as "a tens-of-minutes `3` read as `5`, putting a
run exactly +20:00 out". **It is not specific to the tens-of-minutes column.** It is
a glyph-level confusion that lands wherever the `3` happens to be, and the +20:00
signature was an artefact of Summer 2022's sample rather than a property of the bug.

Every one of the eight also reads **high**, never low — the misread inflates. That
matters because the resolver's fallback when no plateau forms is *the largest
reading*, which selects the inflated value by construction. This is now the second
event to point at the same open fix: **restrict plateau candidates to values inside
the ramp band.** It is the highest-value change outstanding and it would have caught
all eight here.

The remaining two corrections are not digit errors:

- **Serious Sam 4** `1:15:43`→`1:15:15`, off by 28s with both seconds digits wrong.
- **Skies of Arcadia: Legends (PRE-SHOW)** `19:55:57`→`20:30:31`, see below.

## Multi-part VODs break the "longer than its own video" guard

ESA published the Skies of Arcadia 100% run as six parts, and the on-screen timer
carries the **cumulative** total across them. Part 5/6 legitimately shows `20:30:31`
inside a 4-hour video.

Two places treated that as impossible and dropped it:

1. `cmd_export` filtered it out of the importer CSV entirely.
2. `Build/release-event.sh`'s report re-checked it and exited 1, failing the release.

Both did so *after* `apply` had stamped the row `source=human`. A person read that
number off the screen and the heuristic overruled them. Both now exempt human
answers and apply the check only to `source=ocr`, where it still catches the digit
misreads it was written for.

The guard did no damage before this: the live ESA Winter 2026 export dropped zero
runs to it. Winter 2021 is the first event with a multi-part VOD in it.

## Shipped on an unconfirmed time

Four runs, listed in the comment on #52. The reviewer saw all sixteen review items
and left these four unchanged, so they are "looked at and not obviously wrong"
rather than "never seen" — but no one stated a time for them, so they stay on the
correction list.

## Improvements worth making next

1. **Restrict plateau candidates to the ramp band.** Second event asking for it;
   would have removed 8 of this event's 10 corrections.
2. **Teach the review list about multi-part VODs.** A title matching `Part n/m`
   means the duration guard cannot apply, and the run should be flagged as
   cumulative rather than rejected.
3. **Drop the estimate-ratio test from the reject criteria.** It flagged exactly one
   run here (Be-Music Source), which the reviewer passed — consistent with its
   0-for-11 record on Winter 2026.
