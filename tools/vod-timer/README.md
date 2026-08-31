# vod-timer

Reads the **finished run time** off the end of an ESA YouTube VOD, by finding
the on-screen speedrun timer and OCRing it.

This exists for [#31](https://github.com/TheShrug/esavods/issues/31). Horaro
gives us every run's *estimate*; `runs.time` needs the *actual*. For the events
we cannot get real timing data for, this recovers it from the only surviving
artefact — the video itself.

## Why not something easier

- **YouTube's captions API is owner-only.** `captions.download` "requires the
  user to have permission to edit the video". Third parties are locked out by
  design.
- **The unofficial `timedtext` endpoint is closed.** A signed `baseUrl` scraped
  from a watch page returns HTTP 200 and zero bytes, across all of `fmt=json3`,
  `srv1`, `vtt` and plain.
- **Twitch has no captions at all**, and in any case every ESA Twitch VOD from
  2020-2024 is deleted — 1,206 IDs checked across nine schedules, none alive.
  YouTube is the only surviving host.
- **Even a perfect transcript wouldn't help.** ASR captures speech, not the
  overlay. A commentator saying "forty-four forty-two" is not a time to three
  decimal places, and `runs.time` is `float(12,3)`.

## Quick start

```sh
docker compose build
docker compose run --rm vodtimer selftest
docker compose run --rm vodtimer read a3jEHrE17fU --estimate 00:45:00
```

`selftest` is the real proof. It reads three ESA Summer 2022 VODs whose true
times ESA published themselves in
[esamarathon/estimate-accuracy-model](https://github.com/esamarathon/estimate-accuracy-model)
(`data/run-timings/esa-summer-2022.csv`, where `Actual Time` is
`TimerEnd - TimerStart` as recorded live by nodecg-speedcontrol) and asserts
each read lands within a second.

A second of slack is inherent, not sloppiness. The sheet's truth is
`TimerEnd - TimerStart` in whole unix seconds; the overlay renders its own
sub-second value and rounds it its own way. The two can legitimately differ by
one.

### Result

`selftest` covers three runs. The tool has also been validated against the
**whole event**: all 133 timed runs of ESA Summer 2022, resolved to their VODs
and read end to end.

```
tier       n    within 1s   within 2s   wrong   what it means
high     108      102         107          1     trust unreviewed
medium     8        1           1          7     needs a human
low        2        0           0          2     needs a human
reject    15        1           1         14     refused to answer
```

**High confidence is right 107 times out of 108 (99.1%), and covers 81% of the
event.** The delta distribution is not a spread, it is an offset: 71 reads land
exactly 1s under, 30 land exact, 1 lands 1s over, 5 land 2s under. The sheet's
truth is `TimerEnd - TimerStart` in whole unix seconds while the overlay shows
its own floored value, so "1s under" is the two clocks disagreeing, not the OCR.

The single high-confidence disagreement is Mega Man 8 (Crowd Control): the
sheet says 1:53:25, the screen said 1:45:06. The screen's value is backed by a
17-frame plateau and 33 ramp frames. The sheet measures wall time between timer
start and stop, so those 499 seconds are the timer being paused or stopped and
restarted - the two numbers measure different things, and the read is not
obviously the wrong one.

The failures cluster, and they cluster informatively:

- **Seven rejects are one digit.** A tens-of-minutes `3` read as `5`, putting
  the answer exactly +20:00 out. The misread is inconsistent frame to frame, so
  no value holds a clean plateau and the resolver falls back to the largest
  reading - precisely the inflated one. Every one of the seven was still caught
  by the "longer than the video itself" guard.

  Note that swapping the fallback from `max` to the mode does **not** fix this.
  On Castlevania: Circle of the Moon the frozen clock reads `0:51:32` five
  times against `0:31:32` twice, so the mode is wrong too.

  **Fixed in #62** by restricting the answer to values the ramp independently
  predicts. The ramp's frames are clean and evenly spaced
  (`0:30:26, 0:30:38 ... 0:31:26`) and extrapolate to `0:31:32`, the truth, so
  the offset they share is now computed *before* any value is chosen and used to
  arbitrate rather than merely to check afterwards.

  Measured by re-reading real VODs against published truth:

  | set | n | correct before | after |
  |---|---|---|---|
  | Summer 2022, every non-`high` run | 25 | 2 | **12** |
  | Summer 2022, `high` sample (regression check) | 25 | 24 | **24** |
  | Winter 2021, the runs a human had to correct | 10 | 0 | **4** |

  No run that already read `high` changed its answer. Two runs did move, and
  neither was the resolver: both came back on a **truncated download** - 11 and
  14 frames against the usual 50 - so the finish was never in the sampled
  window at all. That is its own bug (#63), and it is worth knowing that a short
  clip still passes silently.

  **What this does not fix:** a misread in a low-order digit. The predicted band
  is about `step + 2 * SLOPE_TOLERANCE` wide - roughly 16s at the standard
  settings - so a `+2s` or `+20s` inflation sits *inside* it and cannot be
  discriminated. That is exactly the Winter 2021 residue: of the six still
  wrong, two are `+2s`, one is `+20s`, one is `+2:00`, one is a truncated
  download, and one is a multi-part VOD whose timer is cumulative. Catching the
  rest needs a narrower band, which needs a finer `--step`, which costs read
  time.
- **Short runs lose to the estimate.** When a run is brief next to its slot,
  too few frames show a ticking clock, and the static estimate wins
  calibration. Golden Sun (a 41-second run in an 8:44 slot) read `0:15:00`,
  its estimate exactly.
- **A bad VOD match shows up as a bad reading.** GeoGuessr was the one run
  whose VOD length disagreed with the slot; it read 0:10:39 against a truth of
  0:45:21 and was rejected on the estimate-ratio guard.

The practical reading: the confidence tier is doing its job. 24 of the 25
non-high results are genuinely wrong, and 107 of 108 high results are right, so
a backfill would take `high` and put 25 runs in front of a person.

## How it works## How it works

**1. Fetch almost nothing.** `yt-dlp --download-sections` pulls only the last
13 minutes, video stream only, at 720p — roughly 40 MB against a ~2 GB VOD.
Cached in a volume, so re-running a video is free.

**2. Locate the timer from the footage, not from a lookup table.** ESA has run
many nodecg-speedcontrol layouts over six years and each puts the timer
somewhere different, so a hardcoded crop per `hidden:Layout` would silently
mis-crop the first time an unseen layout appeared. Instead we OCR whole frames,
collect everything shaped like `HH:MM:SS`, and cluster the hits by position.

That alone is not enough, and the first real test proved it: the layout also
displays the *estimate*, which OCRs far more cleanly than the timer and sits
perfectly still. So candidates are ranked by whether they **tick** — how many
consecutive samples advance by exactly the wall-clock time between them. Only a
live clock does that. The estimate scores zero.

```
candidate (1050, 548, 204, 47) seen 10x ticking 7 e.g. 0:44:42   <- the timer
candidate  (765, 584,  70, 17) seen 12x ticking 0 e.g. 0:45:00   <- the estimate
```

**3. Read every frame.** Each crop is upscaled 4x and read under four image
variants (plain, inverted, and both thresholded) across three page-segmentation
modes, digits-only whitelist, majority vote.

**4. Resolve, with two independent confirmations.** A correct series is a ramp
of slope 1 followed by a flat plateau, which gives two separate ways to reach
the same number:

- the **plateau** — N frames after the finish that all read the same value;
- the **ramp** — frames from *before* the finish. A frame at position `p`
  reading `v` implies a start offset of `v - p`; every honest reading shares
  one offset, so the modal offset is the ramp and outliers are misread digits.

The timer stops at an unobserved instant between the last ramp frame and the
first plateau frame, so the ramp predicts a *band* one frame-interval wide, not
a point. The answer has to land in it:

```
18 frames hold at 0:44:42, and 56 pre-finish frames independently predict 0:44:35-0:44:49
```

A digit error breaks one or the other. Something that satisfies both was read
from independent pixels several times over.

**5. Refuse to guess.** A reading longer than the video, under a minute, or
outside 0.4x-2.0x the scheduled estimate is returned as `reject`. Confidence is
`high` only when both checks pass; `medium` when one does. Batch mode writes
the confidence into the CSV so a human reviews the thin ones instead of all of
them.

## Commands

```
vodtimer read <video_id> [--estimate 00:45:00] [--json]
vodtimer batch runs.csv --out times.csv      # CSV with a video_id column
vodtimer search <words...>                   # find a VOD by title
vodtimer selftest [--tolerance 1]            # check against ESA's own numbers
```

Useful flags: `--tail` (seconds of the end to inspect, default 780), `--step`
(frame spacing, default 10), `--height` (download quality, default 720),
`--crop X,Y,W,H` (skip calibration), `--debug-crops DIR` (dump every crop),
`--ytdlp-arg` (passed straight through, repeatable).

## Known limits

- **Races read one clock.** A 2p layout shows a timer per runner; calibration
  picks the one that ticks most cleanly. Race results need a human.
- **Positions are approximate.** `--download-sections` cuts on a keyframe, so
  frame positions carry a constant offset. Nothing here depends on absolute
  position — the ramp check uses differences only.
- **HLS formats cannot be range-cut.** `--download-sections` against an m3u8
  stream makes yt-dlp exit 0 having written a few hundred bytes, which only
  fails later inside ffmpeg. Format selection pins direct HTTPS, and a clip
  under 512 KB is rejected rather than cached.
- **A run with no outro has no plateau.** The tool falls back to the largest
  reading and says so in `reasons`; confidence drops.
- **If YouTube starts demanding a login**, mount a cookies file and pass
  `--ytdlp-arg --cookies --ytdlp-arg /cookies.txt`.
- **Vision-model escape hatch.** `--debug-crops` writes the same tiny crops the
  OCR sees. When tesseract fails on an unusual layout font, those crops are
  what to hand to a vision model — a few hundred 250x70px images, not video.
