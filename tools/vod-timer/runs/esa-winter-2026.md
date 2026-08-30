# ESA Winter 2026 - run 1

Issue #43. First real backfill event, and the first run of the skill.

- **Source**: horaro.net `2026-winter1` (101 rows) and `2026-winter2` (26 rows).
  No ESA timing sheet exists for this event, so no ground truth and no
  slot-length check.
- **Settings**: `--height 480 --tail 600 --step 12`, 5 shards on stream one and
  1 on stream two.
- **Outcome**: 111 of 114 runs read, over two passes. The first pass read 61 and
  was stopped on the other 53 by YouTube bot detection; the wall had lifted a
  day later and the retry needed no cookies. The 3 that never read are genuine
  OCR failures, not blocks.

## Resolution

127 schedule rows, 114 with a video: 97 `tag-game-runner`, 9 `tag-game`,
8 `weak`, 13 `no-hits`. Six of the `no-hits` are schedule markers rather than
runs (`End of Day 1-4`, `The end (for now..)`, `Random Bingo Showcase`); the
genuine misses are Call of Duty: Black Ops II Zombies (twice), Mark of the
Deep, Journey to the Savage Planet, Duck Quack Shoot and Pokemon Snap.

### A matcher defect this event exposed

The first resolve put **five pairs of rows on the same video**. Every one was a
game with two runs in the event - Tomb Raider I and III, Mario Kart Wii's 32
Tracks and Glitch Showcase, UFO 50's Rail Heist and Waldorf's Journey. The game
name scores identically for both rows and the runner is often the same person,
so both collapsed onto whichever VOD ranked first and one of each pair was
silently wrong.

Summer 2022 never showed this because its timing sheet gave a slot length to
check the VOD duration against, which separated the pairs. Events in the
missing six years have no sheet, so nothing separated them.

Fixed in 3535bca by scoring the category out of the title (`Game [Category] by
Runner - #tag`). Duplicates fell from 5 to 2, and the three wrong matches now
resolve to their own distinct VODs. **Catching this before reading saved three
confidently wrong times.** The two remaining duplicates are both `weak` and are
in the review list: a Sly Cooper race final, and a Final Fantasy IX run split
across two schedule slots that ESA published as a single VOD.

## Reads

| tier | n |
|---|---|
| high | 44 |
| medium | 9 |
| reject | 8 |
| **blocked** | **53** |

44 of the 61 that were read came back `high`, so of the runs the tool actually
got to, 72% needed no human - close to the 81% from Summer 2022. There is no
ground truth for this event, so accuracy is unverified.

## What stopped it: YouTube bot detection

All 53 failures are the same error:

```
ERROR: [youtube] <id>: Sign in to confirm you're not a bot.
Use --cookies-from-browser or --cookies for the authentication.
```

Still active when probed afterwards. Notably **search still works** - only the
player/download path is gated - which is why resolution completed cleanly and
the reads did not.

This did not happen during the 133-run Summer 2022 validation. The plausible
cause is cumulative volume from one IP: that validation, then two full resolve
passes, then this read, inside a day.

**Remedy**: mount a cookies file and pass it through. The tool already supports
it and `--resume` means a retry only fetches what is missing. Both halves of
the obvious invocation are wrong, and both were found by trying it:

```sh
# WRONG - argparse rejects a leading-dash value in the space-separated form:
#   vodtimer read: error: argument --ytdlp-arg: expected one argument
# WRONG - yt-dlp writes the cookie jar back on exit, so :ro is a hard error:
#   OSError: [Errno 30] Read-only file system: '/cookies.txt'
-v "$HOME/cookies.txt:/cookies.txt:ro"
... --ytdlp-arg --cookies --ytdlp-arg /cookies.txt

# RIGHT - `=` form, and a writable per-shard COPY. The copy is not only to
# satisfy that write: six shards sharing one jar would race on it, and letting
# yt-dlp rewrite the original destroys the exported session.
cp ~/cookies.txt /tmp/cookies-$i.txt
-v "/tmp/cookies-$i.txt:/cookies.txt"
... --ytdlp-arg=--cookies --ytdlp-arg=/cookies.txt
```

That clears the bot wall, but an export taken from a browser session that is
still in use then fails differently, with `ERROR: [youtube] <id>: The page
needs to be reloaded.` — YouTube rotates `__Secure-1PSIDTS` and `SIDCC` out
from under the exported copy. Export from a private window and close it
*without logging out*, which leaves the session valid and unrotated.

Nothing was deployed, so there is no half-imported event to clean up.

## Improvements worth making

1. **`--resume` treated a failure as done — FIXED.** The batch records a row
   for a failed read as well as a successful one, and resume skipped any
   video_id already present. So the 53 blocked runs could never be retried:
   every relaunch reported "resuming: 53 already done" and exited having read
   nothing. Resume now keys on *having produced a time*, and rewrites the
   output from the surviving rows so a retry replaces the failed row instead of
   leaving two for one video.
2. **Detect the bot wall and stop the batch.** Right now each of the 53 runs
   burned its own failed request and recorded an individual error. The batch
   should recognise that specific message, abort the shard, and say so once -
   continuing past it neither helps nor is polite to YouTube.
3. **A read equal to a round estimate should never be `high`.** Two flagged
   runs read exactly their estimate (Borderlands 4 `6:00:00`, Darkest Dungeon
   `0:50:00`), which is the known calibration failure. Both were caught here
   only because other checks failed. Encouragingly, **zero of the 44 `high`
   reads equal their estimate**, so the ticking-clock ranking is holding - but
   an explicit guard is cheap.
4. The `+20:00` digit defect from Summer 2022 did not appear in this event.

## Human verification of the 17 flagged runs

All 17 came back. **15 were correct exactly as read; 2 were wrong.** That is a
useful result in both directions, and it does not say what the tiering assumed.

**The estimate-ratio guard has no true positives in this event.** Seven runs
were rejected purely for being implausible against their estimate, and every
one was right:

| run | read | vs estimate | verdict |
|---|---|---|---|
| Tiger Woods PGA Tour 2005 | 0:08:39 | 0.08x | correct |
| Call of Duty: MW2 | 0:08:58 | 0.09x | correct |
| Sly 3 + Showcase | 0:11:30 | 0.12x | correct |
| Mario Kart Wii | 0:12:21 | 0.16x | correct |
| Bejeweled 3 | 0:09:16 | 0.19x | correct |
| Sly Cooper (Aces Finals) | 0:34:13 | 0.23x | correct |
| Zelda: Link's Awakening DX | 4:50:35 | 5.28x | correct |

Nought for seven, and it fails in both directions - four times on runs that
beat their estimate by an order of magnitude, once on a run that took five
times as long. An ESA estimate is a scheduling slot, not a prediction: a
showcase or a short category routinely finishes in a tenth of it. Sending
these to a human costs the reviewer's attention and buys nothing.

**The estimate-equality signal is perfect.** Both genuine errors read *exactly*
their own estimate:

| run | read | estimate | truth |
|---|---|---|---|
| Borderlands 4 | 6:00:00 | 6:00:00 | 4:58:46 |
| Darkest Dungeon | 0:50:00 | 0:50:00 | 0:41:45 |

Meanwhile three reads that merely *look* round - `0:55:00`, `0:51:00`,
`0:14:00` - differ from their estimates (1:00:00, 0:58:00, 0:18:00) and all
three are correct. So the rule is not "a round number is suspect". It is
**"a read equal to its estimate is not a result"**: the OCR has locked onto the
layout's static estimate instead of the clock. Two for two, with no false
positives.

The duration guard also earned its place: it is what caught Borderlands 4,
whose 6:00:00 exceeded its own 5:16:20 video.

### What this changes

The estimate should be used to detect the decoy, not as a plausibility band.
Concretely, for the next event:

1. **Drop the ratio test from the reject criteria.** Keep it in the note text
   if it is useful colour, but stop routing a run to a human for it alone. On
   this event that would have cut the review list from 17 to 10 with no loss.
2. **Make estimate-equality a hard demotion**, not a heuristic - any read
   within a second or two of its own estimate is `reject` regardless of what
   the plateau and ramp agree on, because they agree on the wrong clock.
3. Keep the duration guard exactly as it is.

Left open: `ntbPRhxS1cY` is still matched to two runs - `Sly Cooper and the
Thievius Raccoonus [Coinless Any%]` in One and `Sly Cooper [The Aces Finals]`
in Two. The confirmed 0:34:13 belongs to whichever of the two that video
actually is; the other run needs its own VOD. This is a resolve defect that
spans the two schedules, so the per-schedule duplicate check cannot see it.
