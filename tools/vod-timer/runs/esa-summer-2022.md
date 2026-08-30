# ESA Summer 2022 - validation run

Not a backfill. This event is one of the four for which ESA published real run
timings, so it was run end to end purely to measure the tool against truth.

- **Source**: `estimate-accuracy-model/data/run-timings/esa-summer-2022.csv`,
  where `Actual Time` is `TimerEnd - TimerStart` from nodecg-speedcontrol.
- **Settings**: `--height 480 --tail 600 --step 12`, six shards.
- **Wall time**: 1h 59m 47s for 133 runs. Resolution took a further ~4 min.

## Resolution

130 of 133 `slot-exact`, 2 `title`, 1 `weak`, and no duplicate video ids. The
slot-length check - VOD duration equals `EndTimestamp - StartTimestamp` - is
what makes this so clean, and it is exactly what a backfill event will not
have.

## Reads

| tier | n | within 1s | within 2s | wrong |
|---|---|---|---|---|
| high | 108 | 102 | 107 | 1 |
| medium | 8 | 1 | 1 | 7 |
| low | 2 | 0 | 0 | 2 |
| reject | 15 | 1 | 1 | 14 |

`high` is right 107/108 (99.1%) and covers 81% of the event. 24 of the 25
non-`high` results are genuinely wrong, so the tier is separating real signal.

Delta distribution for `high` is an offset, not a spread: 71 at -1s, 30 exact,
1 at +1s, 5 at -2s, 1 outlier.

## What went wrong, and what to change

1. **Tens-of-minutes `3` read as `5`** - seven rejects, each exactly +20:00 out.
   Inconsistent between frames, so no plateau forms and the resolver falls back
   to the largest reading, which is the inflated one. All seven were caught by
   the duration guard.
   *Tested and rejected*: switching the fallback from `max` to the mode. On
   Castlevania: Circle of the Moon the frozen clock reads `0:51:32` five times
   against `0:31:32` twice, so the mode is wrong too.
   **Open fix**: restrict plateau candidates to values inside the ramp band.
   The ramp there is clean (`0:30:26 ... 0:31:26`) and predicts `0:31:32`, the
   truth. This is the highest-value change outstanding.
2. **Short runs lose calibration to the estimate** - Golden Sun, 41s of run in
   an 8:44 slot, read `0:15:00`, its estimate exactly. Consider requiring the
   winning candidate to have ticked at least N times before trusting it, and
   flagging rather than answering when nothing ticks.
3. **The one `high` disagreement was not an OCR error.** Mega Man 8 (Crowd
   Control): sheet 1:53:25, screen 1:45:06, and the raw timestamps show the
   499s gap is the timer paused or restarted. This raises a question the
   backfill has to answer: when the two disagree, which one is `runs.time`?

## Bugs fixed during the run

- HLS formats cannot be range-cut; yt-dlp exited 0 after writing 257 bytes.
- `Path.with_suffix()` ate the cache key, so every clip re-downloaded.
- `batch` wrote results only at the end, losing progress on interruption.
- Interrupted downloads left truncated clips that passed the size check.

## Throughput

YouTube throttles per connection at ~77 KB/s. Six parallel containers measured
546-779 KB/s aggregate. `android_vr` (progressive format 18, usually
unthrottled) needs a PO token and returns 403, so it is not an option.
