---
name: esa-event-times
description: Recover the actual run times for one ESA event by reading the timer off its YouTube VODs, import them into the local app, and have the user review the doubtful ones there. Use when backfilling a missing event for issue #31, or when asked for the real times of an ESA marathon.
---

# Recovering one ESA event's run times

One event per run. Do not batch several - the point of stopping at the event
boundary is that you evaluate the result and improve the process before the
next one.

The tool lives in `tools/vod-timer/`. Read its README before the first run of a
session; it explains why the crop is calibrated rather than hardcoded, and what
the two confirmations behind a `high` verdict actually are.

## What you need before starting

- **Horaro slug** - the event's schedule on horaro.net, e.g. `2021-winter`.
  Check it resolves: `https://horaro.net/esa/<slug>.json`. Use **horaro.net**,
  never horaro.org, whose API is 410 and whose exports are a stale snapshot.
- **Event hashtag** - as it appears in ESA's VOD titles, e.g. `ESAWinter21`.
  Confirm by eye first: `vodtimer search "<some game> #<tag>"`. Titles run
  `Game [Category] by Runner - #ESAWinter21` back to at least Winter 2021.

Ask the user for both if they gave only one, and confirm the hashtag against a
real search result before committing two hours to it.

### Check whether the schedule already names the VODs

From **ESA Summer 2025 on**, the horaro schedule links each run to its own video
from the Game cell. That is the organisers naming their own upload, so it is not
a match to be scored - it is the answer.

```sh
curl -sL "https://horaro.net/esa/<slug>.json" | grep -c 'youtube.com/watch'
```

If that comes back non-zero, `resolve` uses the links automatically and reports
`how = horaro-link`. On Summer 2025 that was **170 of 170 with no duplicates**,
against Winter 2021's 129 `tag-game-runner` / 9 `tag-game` / 3 `weak` / 1
`no-hits`. It removes the resolver-error class outright - a confident time read
off the *wrong* video, which no artefact the tool produces can detect - so every
later anomaly is a reading problem and can be diagnosed as one.

A `horaro-link-dead` means ESA's own link is gone; that is worth reporting, not
working around.

**Drop the filler rows before reading.** Schedules carry `End of Day N` and
closing cards, which have no category. They are not runs, and one of them
title-matched onto a real run's VOD on Summer 2025 - `cmd_export` keys metadata
by `video_id`, so it would have overwritten that run's platform and category.

### Check for an ESA timing sheet first

ESA publishes run timings for *some* events at
[esamarathon/estimate-accuracy-model](https://github.com/esamarathon/estimate-accuracy-model)
under `data/run-timings/`. Look before starting:

```sh
gh api repos/esamarathon/estimate-accuracy-model/contents/data/run-timings -q '.[].name'
```

If one exists it is worth a lot, and it is worth nothing for the thing it looks
most like.

- **Use it for the schedule and for resolution.** `resolve` takes a sheet as its
  positional argument (`--horaro` is the fallback), and a sheet unlocks
  `slot-exact` matching - VOD duration checked against `EndTimestamp -
  StartTimestamp`, the strongest tier there is. It also covers events that were
  never on Horaro at all, which is the only way to reach ESA Summer 2026 (#42).
- **Never use its `Actual Time` as `runs.time`.** That column is `TimerEnd -
  TimerStart`, wall clock between the crew starting and stopping the nodecg
  timer, and in ESA's 2026 events it routinely keeps running well past the point
  the on-screen timer froze. Measured against Winter 2026, 32 of 71 comparable
  runs disagree and **every one is the sheet reading high**. Two were checked
  frame by frame and the screen matched the OCR, not the sheet. For an archive of
  speedruns the displayed timer is the right value; the sheet includes dead air.

Do not try to settle a sheet-vs-screen disagreement with arithmetic on the
sheet's own columns. `slot = intro + actual + outro` is true *by construction*
(`End - Start` decomposes into exactly those three), so it can never fail and
proves nothing. Only a frame settles it.

## Step 1 - resolve runs to VODs

```sh
cd tools/vod-timer
docker compose build                       # first run of a session only
mkdir -p out/<event>

docker run --rm -v vodtimer-cache:/cache -v "$(pwd -W)/out:/out" \
  esavods/vod-timer:latest \
  resolve --horaro <slug> --tag <TAG> --out /out/<event>/resolved.csv
```

Roughly 1.5s per run, so a few minutes for a full event.

**Read the `how` column before going further.** It is the single best predictor
of whether the read will be any good:

| `how` | meaning | trust |
|---|---|---|
| `horaro-link` | ESA's own link, off their own schedule | certain |
| `slot-exact` | VOD length equals the slot from ESA's timing sheet | near-certain |
| `tag-game-runner(s)` | hashtag, game and runner all agree | good |
| `tag-game(s)` | hashtag and game agree, runner not found | check it |
| `weak(s)` / `no-hits` | nothing agreed | almost certainly wrong |
| `horaro-link-dead` | ESA's link is gone; report it, don't route around it | broken |

`horaro-link` is not a match at all - it is the organisers naming their own
upload - so where an event carries links there is nothing to check. Summer 2025
came back 170 of 170. Everything below it is guesswork by comparison.

For the older missing years there is no ESA timing sheet **and** no links, so
`slot-exact` is unavailable and matching leans on three-way title agreement. That is weaker in
principle, but measured on ESA Winter 2021 it holds up well: 129
`tag-game-runner`, 9 `tag-game`, 3 `weak`, 1 `no-hits` across 142 runs, with a
video found for 141 and no video used twice. Treat that as the expected shape
and investigate if a new event comes back much worse.

Check for duplicate video ids before reading anything. Two runs pointing at one
VOD means at least one is wrong, and it is far cheaper to catch here than after
two hours of downloads.

If a large share come back `weak`, stop and check the hashtag - a wrong tag
looks exactly like this.

## Step 2 - read the timers

YouTube throttles each connection to about 77 KB/s, so throughput is bought by
running several containers, not by asking for more from one. Six is the
measured sweet spot.

```sh
for i in 0 1 2 3 4 5; do
  docker run -d --name vt-<event>-$i \
    -v vodtimer-cache:/cache -v "$(pwd -W)/out:/out" \
    esavods/vod-timer:latest \
    batch /out/<event>/resolved.csv --out /out/<event>/shard$i.csv \
    --shard $i/6 --resume --discard-clips \
    --height 480 --tail 600 --step 12
done
```

`--height 480 --tail 600 --step 12` is validated: it produced identical answers
to 720p on the ground-truth cases at a fraction of the bandwidth. Do not raise
the quality without a reason.

**Batches now stop themselves when YouTube's bot wall goes up**
(`--bot-wall-limit`, default 5 consecutive refusals, **exit 75**). Treat 75 as
"blocked, nothing wrong with the input" - back off and resume - and 1 as "the
batch finished, some runs were unreadable". Do not push on through the remaining
shards on a 75: those requests can only fail, and they plausibly deepen the block.

### When the wall goes up

It went up twice on Summer 2025, so plan for it rather than being surprised.

- **Waiting works.** The block cleared in about 2.5 hours. `--resume` retries a
  row that failed, so a resumed pass costs only what is left.
- **Cookies bypass it, but only a *fresh* export.** Have the user export
  Netscape-format cookies **from a private window, closed without logging out** -
  a session still in use gets rotated out from under the copy, and yt-dlp then
  says `The provided YouTube account cookies are no longer valid`.
- **Mount a per-shard *copy*, never `~/cookies.txt` itself.** yt-dlp rewrites the
  jar on exit, so shards race on it and the original export is destroyed. Use the
  `=` form; the space-separated one trips argparse:

  ```sh
  cp ~/cookies.txt /tmp/ck-$i.txt
  -v "$(cygpath -w /tmp/ck-$i.txt)":/cookies.txt
  ... --ytdlp-arg=--cookies --ytdlp-arg=/cookies.txt
  ```
- **Cookies do NOT clear the IP block.** Tested directly: an authenticated
  request succeeded and an unauthenticated one immediately after was still
  refused. If unauthenticated access starts working after you try cookies, that
  is the block expiring, not the cookies fixing it.
- **These are the user's real Google credentials.** Say so, keep concurrency
  modest, and delete the copies afterwards.

**`The page needs to be reloaded` is not a session problem.** It means yt-dlp
could not solve YouTube's `n` challenge, and cookies push the request down the
path that requires solving it. The image ships deno plus `yt-dlp-ejs` for this.
If it recurs, check the version - an outdated deno presents exactly like no deno
at all unless you look at `-v`:

```
[debug] JS runtimes: deno-2.1.4 (unsupported)      <- silently useless
[debug] JS runtimes: deno-2.9.6                    <- works
```

**Expect about two hours for a ~130 run event.** Wait on it with a single
blocking check rather than polling:

```sh
until [ "$(docker ps -q --filter name=vt-<event> | wc -l)" -eq 0 ]; do sleep 60; done
```

Results are flushed per run and `--resume` skips what is already in the output,
so an interruption costs nothing. Tell the user the expected duration up front.

## Step 3 - build the list, then put the OCR's times in the local app

Merge the shards, then produce the review list:

```sh
docker run --rm -v "$(pwd -W)/out:/out" esavods/vod-timer:latest \
  review /out/<event>/results.csv --resolved /out/<event>/resolved.csv \
  --event "<Event Name>" --out /out/<event>/review.md
```

Now release the event **locally, before anyone has reviewed anything**. Write the
manifest (its shape is in step 6) with no `ANSWERS` line yet, and run the script:
it prints `no human answers yet - shipping the OCR's own reading of every run`
and imports into the local database.

```sh
docker compose up -d                                     # the app, on :8001
Build/release-event.sh tools/vod-timer/events/<event>.conf
```

Doing this before review is safe, and it is safe for exactly one reason: since
#55 the importer keys a run on its schedule slot, not its time, so the
corrections in step 5 update those same rows in place instead of adding a second
run beside each one. Before #55 this order would have doubled the event.

## Step 3b - resolve the flagged runs yourself, from crops

Do this **before** handing the user a list. On Summer 2025 it turned 19 flagged
runs into 17 answers and left the user one genuine judgement call.

For each flagged run, download a few seconds near the end, crop the bottom
strip, and read the timer directly:

```sh
yt-dlp --cookies /cookies.txt -f "bv*[height<=720][ext=mp4][protocol^=http]"   --download-sections "*$((dur-14))-$((dur-2))" --no-warnings --no-playlist   --no-part -o "/tmp/f.%(ext)s" "https://www.youtube.com/watch?v=$vid"
ffmpeg -ss 2 -i /tmp/f.mp4 -vframes 1 -vf "crop=iw:ih/5:0:ih*4/5" /out/frames/r$n.png
```

Then read the PNG. Three rules, each learned the hard way:

- **Check the colour before the digits.** The timer is **orange while running,
  green once stopped**. Reading an orange frame gives you a mid-run value that
  looks exactly like an answer. Four runs were misread this way on the first
  pass before the pattern was spotted.
- **A tail can hold the wrong run's clock.** ESA runs bonus runs and donation
  incentives in the same slot and resets the timer for them, so the end of the
  VOD may show a *different* run. Super Mario Bros. 3 read `0:04:11` (a bonus
  run) against a true `0:57:08`. If the value is wildly under the estimate, or
  the ticker names a bonus/incentive, walk backwards through the video until you
  find the green frozen clock.
- **A read that equals the estimate exactly is the estimate.** With no ticking
  clock in the window, calibration cannot tell the timer from the estimate, and
  the estimate OCRs more cleanly. Three of Summer 2025's five corrections were
  this. The frame shows both side by side, so it is obvious once you look.

Some runs genuinely cannot be recovered: Micro Mages' VOD ends with the clock
still running, so no finish exists on camera. Ship the largest reading as a
**lower bound**, say so plainly, and leave it on the unvouched list rather than
guessing.

## Step 4 - have the user review in the app, not from a list of links

Give them the page:

```
http://localhost:8001/event/<slug>
```

**Review in the app, not from the markdown list.** The list's deep-links open
bare YouTube, so the reviewer has to hold the game, the category and the expected
time in their head while they watch. The event page puts the time, game,
category, runners and the embedded VOD in one row. That is faster, and it is the
only way to catch a time attached to the *wrong run* - a resolver error the timer
check cannot see at all, because a confidently-read time from the wrong video
looks perfect in every artefact the tool produces.

Still tell them which runs need eyes: the page shows every run and only a handful
are in doubt. Paste the numbered review list for that - the numbers are what step
5 keys the answers on. Keep it short; do not add commentary per item.

Say plainly how many were accepted without review and how many need a person.

## Step 5 - fold their answers back and re-release

The user replies with lines like `3 1:12:04`, or `skip`. Write those to
`out/answers.txt`, add `ANSWERS="answers.txt"` to the manifest, and run the same
script again.

> [!CAUTION]
> **Never answer `skip` for a run you want left off the site.** `skip` sets
> `source=human-skip`, and every guard that drops a bad time - including the
> longer-than-its-own-video check - applies to `source=ocr` only. Skipping
> therefore *publishes* the bad value it was dropping. Leave the run out of the
> answers file entirely and let the guard do its job. Summer 2025's Closing
> Speech is the case: `0:34:40` read out of a `0:21:45` video. It applies the answers, re-exports, and re-imports - updating the
runs that changed and leaving the rest untouched.

```sh
Build/release-event.sh tools/vod-timer/events/<event>.conf
```

`final.csv` carries a `source` column of `ocr` or `human`, so the provenance of
every time survives into the import. Several checks key off it, so never
hand-edit a time into a CSV without setting it too - see "Multi-part VODs" below
for what goes wrong when a human time is mistaken for a machine one.

Have them take a second look at the page afterwards. The corrections are the
values most likely to have been mistyped, by either of you.

## Step 6 - deploy the times to the site

Ship what you have. A run listed with an imperfect time is more useful than a
run missing entirely, provided the uncertain ones are written down (step 7) so
they can be corrected.

One script does the whole deploy, driven by a small manifest per event:

```sh
Build/release-event.sh tools/vod-timer/events/<event>.conf --dry-run   # look first
Build/release-event.sh tools/vod-timer/events/<event>.conf
```

The manifest names one horaro schedule per line, because the app models each
stream as its own event:

```sh
SCHEDULES="
winter-2026-s1 | ESA 2026 Winter (One)
winter-2026-s2 | ESA 2026 Winter (Two)
"
```

Match the naming already in the database - `ESA 2020 Winter (One)`,
`ESA 2018 Summer (Two)`, `ESA 2016`. A new spelling does not fail; it silently
creates a second event beside the one people expect. Check before writing a
manifest for an event that is not there yet:

```sh
docker compose exec -T db psql -U esavods -d esavods -c 'select name from events order by id;'
```

The script applies the human answers, exports one CSV per schedule, prints what
it is about to publish by confidence tier, stages the CSVs into
`storage/app/csv/`, imports, and then *asks the table* what actually landed. It
**fails** on any run at 0s, which is always a parse failure, and **warns** when a
run is over eight hours or when two runs share a VOD. Long is not wrong - ESA
runs six-hour games - so length alone is never fatal. A CSV that reads perfectly
can still import into the wrong event or fold two runs together, so the check
worth having is the one after the import.

It also writes `out/release/unvouched.md`: every run that shipped on a reading
no person confirmed. That list is what makes shipping a guess safe rather than
merely fast - post it on the event's issue (step 7).

`runCsv:import` reads *every* file in `storage/app/csv`, not just the new one.
That is safe - unchanged rows resolve to the existing run - but it is not fast.

The CSV is the artifact of record: commit it to `storage/app/csv/` on the
event's branch and merge the PR. Merging deploys, and since #43 the container's
entrypoint runs `runCsv:import` itself on boot, so **production needs no manual
step** - the event is live when the deploy finishes.

### Correcting a time later

Since #55 the importer keys a run on game + category + event + **scheduled
slot**, not on its time. A correction is therefore just a re-import: edit the
time in `storage/app/csv/<event>.csv` and run the release script again, and the
existing run updates in place.

That is what makes shipping an unconfirmed time reasonable rather than reckless
- a wrong value is replaceable, not permanent. Correct the CSV, never the
database directly: production re-imports from the CSV, so a row patched only in
Postgres reverts on the next import.

### Multi-part VODs

ESA publishes a long run as several videos, and the on-screen timer carries the
**cumulative** total across them. Part 5/6 of a 100% run legitimately shows
`20:30:31` inside a four-hour video, so "longer than its own video" is not proof
of a misread there.

Both the exporter and the release script's report apply that check to
`source=ocr` only, and never to a human answer - a person read the number off the
screen, and the check exists to catch the tool's own digit misreads. This is why
a hand-edited time must carry `source=human`: set as `ocr`, it is silently
dropped from the CSV and the run never reaches the site.

## Step 7 - evaluate the run, then stop

Append to `tools/vod-timer/runs/<event>.md`: counts per confidence tier, how
many needed a human, which `how` values the flagged runs had, and anything that
looked systematic. **List every run that shipped with a time the tool would not
vouch for**, by game and category, so a later pass can find them without
re-reading the whole event. Post that list as a comment on the event's issue
too - that is what makes shipping a guess safe. Where the user's answers disagreed with a `high` verdict,
that is the important finding - write it down specifically.

Then propose at most a couple of concrete improvements and stop. Do not start
the next event.

**Open already, from Summer 2025** - check these before filing a duplicate:
#65 (reject a read equal to the estimate), #66 (drop the estimate-ratio guard),
#67 (height fallback picks an uncuttable 240p), #69 (spike: last-frame fast path
with pinned crops).

## Known defects, as of ESA Summer 2025

Full numbers are in the tool's README and in `tools/vod-timer/runs/`. Carry these
into how you read a result:

- **`high` was right 107 times out of 108 on Summer 2022 and covered 81% of that
  event; on Winter 2021 it covered 89%.** The single Summer 2022 disagreement was
  not an OCR error: the sheet measured wall time across a paused timer while the
  screen showed the timer's own value.
- **Reads land 1s under the sheet more often than they land exact.** That is the
  overlay's floored value against whole-second timestamps, not error. Do not
  "correct" it without deciding which of the two `runs.time` should hold.
- **A `3` is sometimes read as a `5`, in any digit position.** This is the single
  biggest source of wrong times: 8 of the 10 corrections on Winter 2021 were this
  one glyph confusion, and the size of the error is set only by which column the
  digit sat in - `+2s` in units of seconds, `+20s` in tens of seconds, `+2:00` in
  units of minutes, `+20:00` in tens of minutes.

  Earlier docs described it as a tens-of-minutes fault worth exactly `+20:00`.
  That was an artefact of the Summer 2022 sample, not a property of the bug, and
  a review that only looks for `+20:00` will miss most of them.

  It never forms a clean plateau, so the resolver falls back to the largest
  reading - which is the inflated one, every time, by construction. **The fix is
  to restrict plateau candidates to values inside the ramp band; switching the
  fallback to the mode does not work and has been tested.** Until that lands,
  treat any rejected or low-tier read as more likely to be a slightly-inflated
  version of the truth than a wild miss.
- **The estimate-ratio guard has never once been right - now 0 for 13.**
  Every run it rejected on implausibility against the estimate alone turned out
  to be correct, across Winter 2026, Winter 2021 and Summer 2025, where Ghoul
  School's `0:07:02` was rejected for being 0.35x its estimate and the screen
  showed exactly `00:07:02`. It is pure reviewer cost and should be dropped from
  the reject criteria (#66).

- **The OCR reading the *estimate* is the biggest single failure now.** Three of
  Summer 2025's five corrections were this, which makes it more frequent than
  the `3`/`5` glyph confusion on that event. When a run finishes well before its
  VOD ends, no frame in the sampled window shows a ticking clock, so calibration
  cannot rank the timer above the estimate - and the estimate OCRs more cleanly.
  A read that *exactly* equals the estimate is not a result. Until #65 lands,
  check for it by hand: the estimate is right there in `resolved.csv`.

- **A tail can hold a different run's timer.** ESA runs bonus runs and incentives
  inside a slot and resets the clock. Summer 2025's Super Mario Bros. 3 read
  `0:04:11` from the bonus run against a true `0:57:08`, and Pokemon Sapphire's
  tail held two later segments. Nothing in the tail betrays this - only looking
  further back does.

- **A long run split across VODs may or may not carry a cumulative timer.** Final
  Fantasy IX ran one run over three videos with the clock running throughout
  (`24:05:51`, read off Part 3). Metaphor: ReFantazio was two schedule rows and
  the clock **reset** between them. Check rather than assume; the parts chain
  arithmetically if it is cumulative.

- **`--height 480` silently becomes 240p when there is no 480p rendition**, and
  240p DASH cannot be range-cut, so the run fails with `moov atom not found` on
  every attempt. Retry at `--height 720`. A corrupt clip also caches if it clears
  `MIN_CLIP_BYTES`, so clear the cache entry or the failure repeats (#67).
- **Short runs lose calibration to the estimate.** Too few frames show a ticking
  clock, so the static estimate wins. A read that exactly equals a round
  estimate is a red flag, not a result.
- **Races read one clock.** A 2p layout has a timer per runner; only one is
  read. Route races to the human.
