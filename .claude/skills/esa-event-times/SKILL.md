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
| `slot-exact` | VOD length equals the slot from ESA's timing sheet | near-certain |
| `tag-game-runner(s)` | hashtag, game and runner all agree | good |
| `tag-game(s)` | hashtag and game agree, runner not found | check it |
| `weak(s)` / `no-hits` | nothing agreed | almost certainly wrong |

For the six missing years there is no ESA timing sheet, so `slot-exact` is
unavailable and matching leans on three-way title agreement. That is weaker in
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
script again. It applies the answers, re-exports, and re-imports - updating the
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

## Known defects, as of ESA Winter 2021

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
- **The estimate-ratio guard has never once been right.** It has gone 0 for 12
  across Winter 2026 and Winter 2021: every run it rejected on implausibility
  against the estimate alone turned out to be correct. It is pure reviewer cost
  and should be dropped from the reject criteria.
- **Short runs lose calibration to the estimate.** Too few frames show a ticking
  clock, so the static estimate wins. A read that exactly equals a round
  estimate is a red flag, not a result.
- **Races read one clock.** A 2p layout has a timer per runner; only one is
  read. Route races to the human.
