# ESA Summer 2024 — backfill

Issue #45. One Horaro schedule (`2024-summer`), tag `#ESASummer24`, shipped as
`ESA 2024 Summer`.

- **Settings**: `--height 480 --tail 600 --step 12`, six shards.
- **Wall time**: about two hours end to end, almost all of it the read itself.
  No bot wall, no cookies, no retries.
- **Outcome**: **124 of 124 scheduled runs live with a time**, every one either
  `high` or confirmed against a frame by eye.

## Resolution — the first event since Winter 2021 with no links, and it showed

This event links its runs to **Twitch**, not YouTube: 124 Twitch video ids in the
Game cells and exactly one `youtube.com/watch`. Every ESA Twitch VOD from
2020–2024 is deleted (the README's 1,206-id check), so those links are no use as
VOD sources and were left alone. The `horaro-link` tier added for Summer 2025
therefore fires **once** here, and resolution falls back to title search.

The first pass came back far worse than Winter 2021:

| how | Winter 2021 (142 runs) | Summer 2024 (124 runs) |
|---|---|---|
| `tag-game-runner` | 129 | 89 |
| `tag-game` | 9 | 16 |
| `weak` | 3 | 4 |
| `no-hits` | 1 | **14** |
| `horaro-link` | — | 1 |

**Fourteen `no-hits` is not fourteen missing videos.** Every one exists, is
titled with the tag, and is found immediately by a search that drops the runner:

```
Ratchet & Clank: Into The Nexus Syn #ESASummer24     -> nothing
Ratchet & Clank: Into The Nexus #ESASummer24         -> J6KShJ5Iofs
```

`resolve.match()` builds its query as game + runners + tag. On this event
horaro's `Player(s)` cell holds the runner's **Oengus display name** while ESA's
VOD titles use their **Twitch handle** — `Syn`/`synn1_`, `Bassguy`/`bassguy4`,
`Zyper`/`Zyper_S`, `Nitroz`/`NitrozSR`, `prisi`/`prisiii3`, `lurven`/`lurven_`.
YouTube's search is conjunctive enough that one wrong token returns **zero**
results rather than a worse ranking, so a run does not degrade to `weak`, it
vanishes. Winter 2021 got away with it because its schedule happened to carry
Twitch names.

A second pass searching `<game> #ESASummer24` recovered 17 of the 18
`no-hits`/`weak` rows outright, each with a `[Category]` bracket matching the
schedule exactly. Two things fall out of that:

- **All four `weak` matches were wrong.** Each had been handed an unrelated
  video. `weak` remains a synonym for "no".
- One run needed hand-assignment: Mega Man 2's VOD is titled `Mega Man 2 Relay
  Race (any%)` with no `[Category]` bracket at all, so game+category scoring
  preferred Mega Man 5's video.
- One run's game cell carries two markdown links (`[…Beta Quest](twitch) +
  [Stream 2](twitch)`) and `_plain()` keeps both link texts, so the query
  contained `+ Stream 2` and matched nothing.

**Final: 124 of 124 on a unique video id, no duplicates.**

Seven schedule rows were filler (`End of day 1`–`7`), all with no category, and
were dropped before reading. That mattered again: `End of day 1` had
title-matched onto South Park: Snow Day's VOD, and `cmd_export` keys metadata by
`video_id`, so it would have overwritten a real run's platform and category —
the same trap Summer 2025 recorded.

### Re-resolved after #75

The fix landed in #75 and this event is what it was measured against. Nothing
was re-imported — the times shipped here are unchanged — but the same
`resolve --horaro 2024-summer --tag ESASummer24` now returns, for the 124 real
runs:

| how | first pass | after #75 |
|---|---|---|
| `tag-game-runner` | 89 | **108** |
| `tag-game` | 16 | 15 |
| `weak` | 4 | **0** |
| `no-hits` | 14 | **0** |
| `horaro-link` | 1 | 1 |

124 distinct video ids, and every one of the 124 titles carries **every word**
of its row's game name. The second pass and the one hand-assignment this
backfill needed are both gone: Mega Man 2 lands on `Mega Man 2 Relay Race
(any%)` by itself, and the two-stream Ocarina of Time cell no longer asks for a
game called `... Beta Quest + Stream 2`.

The filler rows come back 6 `no-hits` and 1 `weak` instead of matching real
VODs, which is the right answer for a row with no video — but they still have to
be dropped before reading, because `weak` is a match as far as `cmd_export` is
concerned.

## Reads

| tier | n | outcome |
|---|---|---|
| high | 108 | shipped unreviewed |
| medium | 13 | all checked against a frame |
| reject | 3 | all checked against a frame |

**108 of 124 accepted without review — 87% coverage**, between Summer 2022's 81%
and Winter 2021's 89%, and reached without ESA's own links.

All 16 non-`high` runs were resolved from frames rather than handed over as
links: **10 confirmed the OCR exactly, 6 were corrected.**

### Corrections — 6 of 16

| run | OCR read | actual | cause |
|---|---|---|---|
| Star Wars Battlefront II (Classic 2005) — Any% with bonuses | `1:00:00` | `0:47:44` | read the **estimate** |
| The Neverhood — Cutscene% | `1:15:00` | `0:58:58` | read the **estimate** |
| Flash Game Gauntlet — Any%? | `1:20:00` | `1:30:01` | read the **estimate** |
| Quake: Arcane Dimensions — Easy Run (Top Floor) | `0:25:00` | `0:18:41` | read the **estimate** |
| Spyro 2: Ripto's Rage — 14 Talisman | `0:34:00` | `0:30:54` | read the **estimate** |
| Paris Marseille Racing — 2P1C | `0:13:31` | `0:13:34` | read an **orange, still-running** clock 3s before the freeze |

**Five of six corrections are the OCR reading the estimate** — the same dominant
failure as Summer 2025, and a larger share of it (5/6 against 3/5). The `3`/`5`
glyph confusion that dominated Winter 2021 did not appear once.

The sixth is new and worth naming. On Paris Marseille Racing the crew **reset the
clock** about fifteen seconds after the run ended and ran a nine-second
incentive, so the tail holds `00:00:09`. The batch never saw the freeze and fell
back to the largest reading in its window — which was a *running* clock at
`0:13:31`. The true finish is `0:13:34`, three seconds later. That is Summer
2025's "post-run timer" fault in its cheapest possible form: a near miss rather
than a wild one, and being a near miss is exactly what makes it invisible in a
list of times.

### The layout is orange-while-running, green-once-stopped

Same as Summer 2025, and again it is what made frame review cheap. Fifteen of
sixteen runs were settled by a single image holding two bottom-strip crops eight
seconds apart: a frozen green clock is unmistakable beside a ticking orange one.
Paris Marseille was caught only because its frame was **orange** — its digits
alone read as a perfectly plausible answer.

## #65 (`equals_estimate`) on its first real event

It fired on **6 of 124 runs**, and it was **right 5 times**:

| run | read | verdict |
|---|---|---|
| Star Wars Battlefront II | `1:00:00` | wrong — actual `0:47:44` |
| The Neverhood | `1:15:00` | wrong — actual `0:58:58` |
| Flash Game Gauntlet | `1:20:00` | wrong — actual `1:30:01` |
| Quake: Arcane Dimensions | `0:25:00` | wrong — actual `0:18:41` |
| Spyro 2: Ripto's Rage | `0:34:00` | wrong — actual `0:30:54` |
| OoT Beta Quest — Battleship Bingo | `3:30:00` | **right** — the run really does end at `3:30:00` |

The sixth is the case the issue argued for keeping as a demotion rather than a
rejection, and it turned up on the very first event. Battleship Bingo is a
**time-capped** race, so `3:30:00` against a `3:30:00` estimate is a run
genuinely finishing on a round number, exactly like Summer 2022's Super Smash TV.
Rejecting on this rule would have thrown away a correct time.

**Tier impact is smaller than the hit count suggests.** Only the OoT read passed
both confirmations, so `equals_estimate` moved exactly **one** run from `high` to
`medium` — and that one was correct. The other five were already `medium` or
`reject` on other grounds. What the check actually bought was the *note*: five
runs reached the review list saying `reading is exactly the H:MM:SS estimate`,
and that is what sent me to a frame rather than nodding at a plausible number.
Four of the five have a true time within 0.75×–1.13× of their estimate, so
nothing else about them looked wrong.

## The estimate-read has a second, sharper signature: the crop is tiny

`batch` has recorded the calibrated crop since Summer 2025, and on this event it
separates the fault perfectly:

| crop size | runs | estimate-reads |
|---|---|---|
| 160×49 – 192×58 (the timer) | 118 | **0** |
| 52×16, 56×16, 58×16 (×2), 59×31 | 5 | **5** |
| 125×38 (`4x3-2p`, the OoT race) | 1 | 1 — and correct |

**Every crop under 100px wide was calibration locking onto the `EST.` field, and
no crop of normal size ever was** — 5 for 5, no false positives across 118 runs.
That is a stronger discriminator than the value comparison, because it does not
depend on the run's true time differing from its estimate: it would have caught
Flash Game Gauntlet (`1:30:01` against a `1:20:00` estimate) even if the OCR had
returned something that was not the estimate verbatim.

## Known bugs, re-confirmed

- **#66 — the estimate-ratio guard is now 0 for 14.** LEGO Harry Potter: The
  Battle for Hogwarts read `0:01:22` and was rejected for being 0.27× its
  `0:05:00` estimate. The screen shows `00:01:22` in green on the results card.
  Fourteen consecutive rejections, fourteen correct readings. It should go.
- **#67 did not fire.** No run failed at `--height 480`; every VOD on this event
  has a 480p rendition.
- **#63 did not visibly fire** — but by construction that is not a claim the
  artefacts can support, which is the point of the issue.
- **#69, crop stability per layout.** This event's `Layout` column is *visible*
  (`Game, Player(s), Couch, Platform, Category, Layout`), not `hidden:Layout`,
  and `horaro_rows` reads it either way because it lowercases the column names.
  `16x9-1p` and `4x3-1p` account for 98 of the 124 runs and both calibrate to the
  same ~188×57 box around (448, 367–381): x is stable, y moves with the layout's
  lower third. The five tiny crops above are what a pinned crop would have
  prevented.

## Runs that need a second pair of eyes

- **The Legend of Zelda Ocarina of Time Beta Quest — Battleship Bingo.** One
  schedule row, a race, and ESA published **two** VODs, one per runner
  (`MV-2HflPXKs` Baal, `yDNKs24PT8k` Runnerguy2489), matching the row's two
  Twitch links. The site models one run per row with one video, so Baal's ships
  and the time (`3:30:00`) is the cap both hit. Which runner's VOD the row should
  carry is a call for a person, not for the tool.

No run shipped on a reading nobody confirmed: `out/release/unvouched.md` is empty
for this event, which is a first.

## Improvements worth making

1. ~~**Stop putting the runner in the search query as a hard term.**~~ Done in
   #75. It cost 14 runs here and would have cost the event outright if the
   fallback had not been obvious. Search game + tag, then use the runner to
   *rank* rather than to *filter* — ESA's `[Category]` bracket already separates
   two runs of one game, which is the job the runner was doing. Confined to
   `resolve.match()`, and the highest-value change on the list. Filed as #75.
2. **Flag a calibrated crop much smaller than the event's modal crop.** Five of
   six corrections here share one unmistakable fingerprint, and unlike
   `equals_estimate` this catches the case where the OCR reads the estimate but
   the estimate is not the answer's exact value.

Not recommended: a `horaro-link` tier for Twitch ids. Those VODs are all deleted;
the link names a video nobody can read.
