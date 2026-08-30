# ESA Winter 2026 - run 1 (incomplete)

Issue #43. First real backfill event, and the first run of the skill.

- **Source**: horaro.net `2026-winter1` (101 rows) and `2026-winter2` (26 rows).
  No ESA timing sheet exists for this event, so no ground truth and no
  slot-length check.
- **Settings**: `--height 480 --tail 600 --step 12`, 5 shards on stream one and
  1 on stream two.
- **Outcome**: **incomplete.** 61 of 114 runs read; the other 53 were blocked
  part-way through by YouTube bot detection.

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
it and `--resume` means a retry only fetches what is missing:

```sh
-v "$HOME/cookies.txt:/cookies.txt:ro"
... --ytdlp-arg --cookies --ytdlp-arg /cookies.txt
```

Nothing was deployed, so there is no half-imported event to clean up.

## Improvements worth making

1. **Detect the bot wall and stop the batch.** Right now each of the 53 runs
   burned its own failed request and recorded an individual error. The batch
   should recognise that specific message, abort the shard, and say so once -
   continuing past it neither helps nor is polite to YouTube.
2. **A read equal to a round estimate should never be `high`.** Two flagged
   runs read exactly their estimate (Borderlands 4 `6:00:00`, Darkest Dungeon
   `0:50:00`), which is the known calibration failure. Both were caught here
   only because other checks failed. Encouragingly, **zero of the 44 `high`
   reads equal their estimate**, so the ticking-clock ranking is holding - but
   an explicit guard is cheap.
3. The `+20:00` digit defect from Summer 2022 did not appear in this event.
