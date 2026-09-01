# ESA Summer 2025 — backfill

Issue #44. Two Horaro schedules (`2025-summer1`, `2025-summer2`), tag
`#ESASummer25`, shipped as `ESA 2025 Summer (One)` and `ESA 2025 Summer (Two)`.

- **Settings**: `--height 480 --tail 600 --step 12`, six shards (see *The wall*).
- **Wall time**: about six hours end to end, of which roughly four were spent
  blocked or waiting rather than reading.
- **Outcome**: **169 of 170 scheduled runs live with a time.** The one omission
  is the Closing Speech, which is not a speedrun.

## Resolution — ESA now publishes the VOD link itself

From Summer 2025 the schedule links each run to its own video from the Game
cell. `horaro_rows` was throwing that away: `_plain()` stripped the markdown
before anything looked at the URL, and the resolver then re-guessed the video by
title search.

Added a `horaro-link` tier that takes ESA's own id and probes it.

| | runs | resolved by link |
|---|---|---|
| Stream One | 129 | 129 |
| Stream Two | 41 | 41 |

**170 of 170, no duplicate video ids.** Compare Winter 2021's 129
`tag-game-runner` / 9 `tag-game` / 3 `weak` / 1 `no-hits`.

This matters for more than tidiness. It removes the resolver-error class
entirely — a confident time read off the *wrong* video, which no artefact the
tool produces can detect. Where a read looked wrong on this event, the video was
never in doubt, so every anomaly was a reading problem and could be diagnosed as
one. Do not use the title-search path on an event that carries links.

Seven schedule rows were filler (`End of Day 1-5`, two closing cards), all with
no category. They were dropped before reading. That mattered: `End of Stream 2`
had title-matched onto Metaphor: ReFantazio's VOD, and `cmd_export` keys metadata
by `video_id`, so it would have overwritten a real run's platform and category.

## Reads

| tier | n | shipped |
|---|---|---|
| high | 151 | yes |
| human | 17 | yes |
| medium | 1 | yes, unconfirmed |
| not shipped | 1 | no (Closing Speech) |

**151 of 170 accepted without review — 89% coverage**, level with Winter 2021 and
ahead of Summer 2022's 81%.

## Review was done from crops, not from links

The 19 flagged runs were resolved by grabbing a frame near the end of each VOD
and reading the timer directly, rather than handing a person 19 links. This is
the `--debug-crops` escape hatch the README describes, and it worked: 17 answers
from about 30 frames.

**Read the colour, not just the digits.** This layout renders the timer **orange
while running and green once stopped**. A first pass that ignored this produced
four wrong answers — Castlevania, Harry Potter, Hogwarts Legacy and Spider-Man
were all read mid-run, and all four turned out to match the OCR after all. Any
future last-frame or fast-path mode must confirm the clock has stopped before
trusting the number; the digits alone do not say.

### Corrections — 5 of 17

| run | OCR read | actual | cause |
|---|---|---|---|
| Super Mario Bros. 3 — Any% (Warpless) | `0:04:11` | `0:57:08` | read the **bonus run** that followed |
| Final Fantasy IX — Vivi% | `11:59:16` | `24:05:51` | end of Part 1 of 3; timer is cumulative |
| Pokémon Sapphire — Any% (Glitchless) | `2:20:00` | `2:17:12` | read the **estimate** |
| Spyro: Year of the Dragon — 100 Egg | `1:15:00` | `1:07:54` | read the **estimate** |
| Vib-Ribbon — All Songs | `0:20:00` | `0:16:39` | read the **estimate** |

The other twelve confirmed the OCR exactly. Every correction was in a non-`high`
tier, so the tiering placed the errors where a person would find them.

**Three of the five are the same failure: the OCR read the estimate.** When the
run ends well before the VOD does, the sampled window holds no ticking clock,
and calibration cannot separate the timer from the estimate — both are static,
and the README notes the estimate OCRs more cleanly. Final Fantasy IX Part 3
showed this at its clearest: a `58x16` crop (against the usual `188x57`) landed
on the estimate and returned `24:00:00` against an on-screen `EST. 24:00:00`.

**Two are a post-run timer.** ESA runs bonus runs and donation incentives inside
the same slot, and the crew resets the clock for them. The tail then holds a
*different* run's timer. SMB3's `0:04:11` and Sapphire's tail both come from
this. It is not detectable from the tail alone — only by looking further back.

## Runs that cannot be recovered from their VOD

- **Micro Mages — Second Quest.** The video ends at 1991s with the clock still
  running at `00:32:37`. There is no finish on camera. It ships at `0:32:36` as a
  **lower bound**, and is the event's single unvouched run. This is a different
  thing from an uncertain read and should not be "corrected" by guessing.
- **Closing Speech — Speech%.** Read `0:34:40` out of a `0:21:45` video and
  dropped by the longer-than-its-video guard. Correct outcome: it is not a
  speedrun. Note it must be left *out* of the answers file — `skip` sets
  `source=human-skip`, which bypasses that guard and would publish the bad time.

## The wall, twice — and what actually fixed it

YouTube's bot check blocked 92 of 170 reads partway through the first batch, then
returned during the finishing pass.

**A circuit breaker was added** (`--bot-wall-limit`, default 5, exit 75). The
first batch made ~92 doomed requests after the wall went up, which wastes wall
time *and* plausibly deepens the block. On its first real outing the breaker
stopped a pass after one minute instead of 51 runs. It counts *consecutive* wall
failures and resets on anything else, including a non-wall error — a clip that
downloaded and then failed in ffmpeg is proof YouTube is still answering.

**Cookies work, but only when freshly exported.** Two earlier attempts failed and
were misdiagnosed as a stale jar. The real cause was that **the container had no
JavaScript runtime**, so yt-dlp could not solve YouTube's `n` challenge:

```
n challenge solving failed: Ensure you have a supported JavaScript runtime
WARNING: Only images are available for download.
```

Cookies push the request down a path that *requires* solving it, so
authenticating made things strictly worse and surfaced as `The page needs to be
reloaded` — which reads like a session problem and is not one. **deno plus
`yt-dlp-ejs` are now in the image.** Note that an installed-but-too-old deno
presents identically to no deno at all in the user-facing warning; only `-v`
shows the difference:

```
[debug] JS runtimes: deno-2.1.4 (unsupported)      <- silently useless
[debug] JS runtimes: deno-2.9.6                    <- works
```

**Cookies do not clear the IP block.** Tested directly: one authenticated request
succeeded, an unauthenticated one immediately after was still refused. An earlier
apparent "fix" was the ~2.5h block expiring on its own. Export from a private
window and close it *without logging out*, or YouTube rotates the session out
from under the copy. Always mount a per-shard **copy** — yt-dlp rewrites the jar
on exit, so shards would race on it and the original would be destroyed.

## The estimate-ratio guard is now 0 for 13

Ghoul School — Any% (Best of 3) read `0:07:02` and was rejected for being 0.35x
its 20:00 estimate. The screen shows `00:07:02`. That is the thirteenth
consecutive run the guard has rejected that turned out to be correct, across
Winter 2026, Winter 2021 and now Summer 2025. It has never once been right. It
should be dropped from the reject criteria.

## Other defects found

- **No 480p means 240p, and 240p does not range-cut.** Two runs failed every
  attempt with `moov atom not found`. Neither video has a 480p rendition, so
  `--height 480` fell back to **240p**, whose DASH stream yt-dlp cannot cut.
  Both read `high` immediately at `--height 720`. The selector steps *down* when
  the requested height is missing; for reading small digits it should step up.
  A corrupt clip is also cached if it clears `MIN_CLIP_BYTES`, so the failure
  repeats until the cache entry is removed by hand.
- **`gmdate('H:i:s')` wraps at 24 hours.** All seven views formatted run times
  with it. `gmdate` formats an instant, not a duration, so Final Fantasy IX's
  `24:05:51` displayed as `00:05:51` — indistinguishable from a real 5m51s run,
  on a page whose entire purpose is run times. Latent since 2018; this is the
  first run over 24 hours on the site. Fixed with a `formatted_time` accessor on
  `App\Run`.
- **The crop was computed and thrown away.** `batch` now records it. Across the
  ~50 runs read after that change, most of a layout's "distinct" crops are ±1px
  calibration jitter around one position, but genuine outliers exist — within
  `16x9-1p`, 18 of 20 runs sit at `448,366-367` while one sits at `x=30`. The
  schedule's `hidden:Layout` is a good key but not a perfect one: a run labelled
  `16x9-1p` shared its crop with a `16x9-2p` run.

## Improvements worth making

1. **Reject a read that exactly equals the estimate.** Three of this event's five
   corrections were the OCR returning the estimate verbatim, and every one is
   trivially detectable — the estimate is in the schedule and already in
   `resolved.csv`. Today it is a hint in the docs ("a red flag, not a result");
   it should be a hard check that forces the run to a human. This is the single
   highest-value change on the list.
2. **Step up, not down, when the requested height is unavailable.** Two runs were
   lost to a silent 240p fallback that cannot be cut and would have been
   unreadable even if it could. Prefer the next height *above* `--height` when no
   rendition at or below it exists.

Not recommended yet: the last-frame fast path. It is genuinely tempting — the
frozen timer is on screen at the final sampled frame in **103 of 103** runs
measured here, and it would replace an 11-minute download with seconds. But
calibration cannot find the timer without a ticking clock, one frozen frame is
one observation rather than several, and this event produced three separate ways
for the tail to hold the *wrong* run's clock. It needs the pinned-crop work and
the estimate check above before it is safe.
