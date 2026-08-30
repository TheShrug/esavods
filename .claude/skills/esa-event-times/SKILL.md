---
name: esa-event-times
description: Recover the actual run times for one ESA event by reading the timer off its YouTube VODs, then hand the user a short numbered list of the runs a human still has to check. Use when backfilling a missing event for issue #31, or when asked for the real times of an ESA marathon.
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
unavailable and matching leans on three-way title agreement. That is weaker.
Expect more human review than the Summer 2022 validation needed, and say so
when you present the list.

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

## Step 3 - hand the user their list

Merge the shards, then produce the review list:

```sh
docker run --rm -v "$(pwd -W)/out:/out" esavods/vod-timer:latest \
  review /out/<event>/results.csv --resolved /out/<event>/resolved.csv \
  --event "<Event Name>" --out /out/<event>/review.md
```

Paste that list into the conversation. It is numbered, one line of context per
item, and each link lands a few minutes from the end where the clock is already
stopped. Keep it short - do not add commentary per item.

Say plainly how many were accepted without review and how many need a person.

## Step 4 - fold their answers back

The user replies with lines like `3 1:12:04`, or `skip`.

```sh
docker run --rm -v "$(pwd -W)/out:/out" esavods/vod-timer:latest \
  apply /out/<event>/results.csv --index /out/<event>/review-index.csv \
  --answers /out/<event>/answers.txt --out /out/<event>/final.csv
```

`final.csv` carries a `source` column of `ocr` or `human`, so the provenance of
every time survives into the import.

## Step 5 - evaluate the run, then stop

Append to `tools/vod-timer/runs/<event>.md`: counts per confidence tier, how
many needed a human, which `how` values the flagged runs had, and anything that
looked systematic. Where the user's answers disagreed with a `high` verdict,
that is the important finding - write it down specifically.

Then propose at most a couple of concrete improvements and stop. Do not start
the next event.

## Known defects, as of the Summer 2022 validation

Full numbers are in the tool's README. Carry these into how you read a result:

- **`high` was right 107 times out of 108 and covered 81% of that event.** The
  single disagreement was not an OCR error: the sheet measured wall time across
  a paused timer while the screen showed the timer's own value.
- **Reads land 1s under the sheet more often than they land exact.** That is the
  overlay's floored value against whole-second timestamps, not error. Do not
  "correct" it without deciding which of the two `runs.time` should hold.
- **A tens-of-minutes `3` is sometimes read as `5`**, putting a run exactly
  +20:00 out. It never forms a clean plateau, so the resolver falls back to the
  largest reading, which is the inflated one. The duration guard caught all
  seven cases in Summer 2022. **The fix is to restrict plateau candidates to
  values inside the ramp band; switching the fallback to the mode does not work
  and has been tested.** Until that lands, treat a rejected run whose read is
  suspiciously near +20:00 as very likely a misread of a correct value.
- **Short runs lose calibration to the estimate.** Too few frames show a ticking
  clock, so the static estimate wins. A read that exactly equals a round
  estimate is a red flag, not a result.
- **Races read one clock.** A 2p layout has a timer per runner; only one is
  read. Route races to the human.
