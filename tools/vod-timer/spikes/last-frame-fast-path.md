# Spike — the last-frame fast path (#69)

Issue [#69](https://github.com/TheShrug/esavods/issues/69), `type: spike`. Can a run's time be
read from a handful of frames at the very end of its VOD, with a crop pinned per layout, instead
of downloading 600 seconds and calibrating?

- **Time-box**: 4 hours, declared before starting. The crop half was done offline first, on
  artefacts already on disk, so the download budget was spent on the one question that needed it.
- **Download budget**: 50 yt-dlp invocations, against the ~250 that raised YouTube's bot wall
  twice during Summer 2025. **Spent 45** — 40 clip fetches and 5 format probes. The wall did not
  go up.
- **Verdict**: **adopt as a cross-check only.** The read itself is sound — 36 of 36 against the
  slow path's `high` answers, across both dominant layouts, with the fast read beating the slow
  path outright on one known-bad run and refusing to answer on two more. What it cannot do is
  tell whose clock it is looking at, and that is not a gap a better crop closes.

Everything below is reproducible from `spikes/last-frame-fast-path/`.

## The prize is real, and smaller than the issue says

The issue costs the download at ~11 minutes a run and the OCR at about a minute, and concludes
that an event goes from ~2.5 hours to minutes. The first half measures out almost exactly right.

| | slow path | fast path | measured over |
|---|---|---|---|
| window downloaded | 600s | **60s** | |
| bytes per run | ~20–40 MB | **2.51 MB** median | 36 runs |
| seconds per run | ~40s–11min | **7.8s** median | 36 runs |
| **yt-dlp invocations per run** | **1** | **1** | — |

That last row is the one that matters, and it does not move. `probe` is cached, and one
`--download-sections` fetch is one invocation whether it asks for 60 seconds or 600. **The fast
path saves bandwidth, not requests** — and request count is what YouTube polices.

So the saving lands entirely on the reading time, which was not the whole cost:

| event | wall time | of which reading | fast-path reading | total after |
|---|---|---|---|---|
| Summer 2025 | ~6h | ~2h | ~22 min | **~4h20m** |
| Winter 2021 | 2h 00m | ~2h | ~18 min | **~18 min** |
| Summer 2022 | 1h 59m | ~2h | ~17 min | **~17 min** |

Summer 2025 spent roughly four of its six hours blocked or waiting rather than reading, and
nothing here touches that. On an event where the wall stays down the fast path is a genuine 6x;
on the one event where it went up it is about 1.4x. Worth having, not transformative.

There is also a risk in the other direction that the issue does not raise. Compressing an
event's requests from two hours of reading into twenty minutes is roughly a **fivefold increase
in request rate** (42s per run on Summer 2025's six shards, against 7.8s here), and
whether YouTube's wall counts requests or rates them is not something this spike could test
without walking into it. If it rates them, the fast path brings the wall on sooner and the
pacing has to be added back by hand.

**The binary-search variant is dead on paper, as the issue suspects.** ~10 invocations a run is
~1,700 for an event against the ~250 that has already tripped the wall twice, and the thing it
buys — two genuine confirmations — is available for free from a 60s tail on the runs that
finish inside it (see below). It does not need testing at scale to be refused.

## The crop is stable. The layout key is the wrong pin.

`batch` recorded a `crop` for 51 of 170 Summer 2025 runs; 48 of those also carry a
`hidden:Layout`, and 42 of *those* are a single-player layout. That is the whole evidence base,
and it is thinner than #69's framing implies — the column was added partway through the event.
Every number in this section is against those 42, not against the event.

Read as pixels, the column looks unstable: `16x9-1p` holds one outlier at `x=30` against 20 runs
at `x=448`, and `4x3-1p` holds three apparently distinct positions. That reading is an artefact.
**`--height` was not constant across the event**, and a crop recorded in 360p pixels is not a
different position, it is the same position in a smaller frame.

Dividing each box by its own frame size collapses it:

| layout | n | x | y | note |
|---|---|---|---|---|
| `16x9-1p` | 21 | 0.522–0.525 | 0.758–0.794 | plus one outlier, below |
| `4x3-1p` | 21 | 0.516–0.532 | 0.761–0.803 | |
| `16x9-2p` | 2 | 0.522 | 0.758 | one of them |
| `16x9-4p` | 1 | 0.525 | 0.765 | |

**41 of 42 single-player crops sit on one position** — a spread of 13.7px horizontally and
21.4px vertically on an 854×480 frame. A single padded rectangle covers all of them with room
to spare, and it is the rectangle this spike then read 36 runs with.

The three "distinct positions" in `4x3-1p` resolve as:

- `279x83` — **Dare to Dream**, and `out/summer-2025-s1/extra-720.csv` names it as one of exactly
  two runs re-read at `--height 720`. Confirmed, not inferred.
- `143x44` ×2 — **We Love Katamari** and **Final Fantasy IX**, the standard box at 360p. Inferred:
  at 480p they would sit at x=0.39, nowhere near anything; at 360p they land in the middle of the
  cluster. Worth saying plainly that the *cause* is not established — both videos have a 480p
  rendition today, so this is **not** the missing-rendition step-down bug from
  `runs/esa-summer-2025.md`, and I do not know what it is.

The normalisation is not self-confirming. Reconstructing Ghoul School's frame height from an
unrelated artefact — review strip `r2`, a 720p grab — by undoing the pipeline's own padding
predicts a recorded crop of `x=78, w=161` at 480p against an actual `77,164`, while 360p predicts
`57,124` and 720p predicts `119,239`. The method recovers a frame height it was never told.

### `hidden:Layout` is neither necessary nor sufficient

- **Not necessary.** `16x9-1p`, `4x3-1p`, `16x9-4p` and one `16x9-2p` all put the timer in the
  same place. Keying the pin on the layout would maintain four entries where one would do.
- **Not sufficient.** **QuizBOSH Extravaganza** is labelled `16x9-1p` and sits at x=0.035 — and
  **Undertale**, labelled `16x9-2p`, sits at exactly the same odd position. That is the "a run
  labelled `16x9-1p` shared a crop with a `16x9-2p` run" note in #69, and the explanation is that
  both are somewhere the label does not predict. 1 in 42.
- **The real key is the event.** ESA Summer 2022's overlay puts the timer at x≈0.82–0.99, in a
  different colour scheme, with the estimate inline in the subtitle line. Pointing the Summer 2025
  rectangle at a Summer 2022 VOD (Trek to Yomi, still in the clip cache) reads **nothing** — and
  the estimate `01:30:00` falls *inside* that rectangle, so the failure mode it is one glyph size
  away from is landing on the estimate.

The 2p layouts are elsewhere again and disagree among themselves — `4x3-2p` at x≈0.09,
`16x9-2p` split between x=0.035 and the common position. They stay on the slow path, as #69 says.

### This unblocks #71

[#71](https://github.com/TheShrug/esavods/issues/71) says a global crop-size threshold cannot
work because "genuinely different layouts produce `279x83`, `244x57`, `164x50`, `161x49`,
`143x44` and `116x64`", and that a per-layout threshold needs a layout key `cmd_resolve` does not
record. **Two of those six are not different layouts** — `279x83` is the standard box at 720p and
`143x44` is the standard box at 360p. Normalise by frame width and the problem is not close:

| | crop / frame width |
|---|---|
| every crop that produced a correct read | **0.136 – 0.286** |
| Final Fantasy IX Part 3, the crop known to be wrong (`58x16`) | **0.045 – 0.068** |

A factor of two of clear air, with no layout key involved. **#71 needs `batch` to record the
frame size, not the layout** — and that is a strictly easier change, because the frame size is
already in hand at crop time while the layout key would have to be threaded through
`cmd_resolve`. This does not remove #71's need for a second event's evidence; it removes its
stated blocker.

## The clock's colour is the stopped-signal that obstacle 1 says does not exist

This is the finding that changes the answer, and it was free — it is measurable on the 53 review
stills already in `out/frames/`.

`runs/esa-summer-2025.md` records in passing that this overlay "renders the timer **orange while
running and green once stopped**", and warns that a fast path must confirm the clock has stopped.
Measured across every timer-shaped string on those stills, the three states do not overlap at all:

| what | n | mean RGB |
|---|---|---|
| timer, running | 15 | `(243, 189, 56)` |
| timer, stopped | 15 | `(106, 185, 136)` |
| timer, reset to `0:00:00` | 2 | `(244, 244, 243)` |
| the estimate | 32 | `(242, 242, 242)` |

Orange and green are ~130 apart in RGB. A classifier counting pixels within 60 of each reference
separated all 32 timer readings and all 32 estimate readings with no errors, on stills nobody
chose for it.

**This is the answer to obstacle 1.** `_running_score` cannot separate the timer from the
estimate on a frozen clock because both score zero — but it is asking the wrong question of the
wrong number of frames. *Ticking* needs two frames of a clock that is still moving. *Stopped*
is legible in one frozen frame, from the colour, and it is a strictly stronger statement: it says
the run finished on camera, which ticking never does.

It also reaches a place #65 cannot. The dangerous mis-crop lands on the estimate, and
`equals_estimate` compares the read against the **schedule's** estimate at whole-second equality.
FFIX Part 3 read `24:00:00` against an on-screen `EST. 24:00:00` and a schedule value of
`23:59:59`, so the check does not fire — the overlay rounded and the schedule did not. The colour
gate never sees that value at all: **the estimate renders white and the timer never does**, so
the crop is rejected before its digits are compared to anything.

**The palette is per-event, not universal.** Summer 2022 colours its timer too — yellow while
running, white when stopped — which is the same mechanism and an incompatible table. A gate
hardcoded to Summer 2025's green would reject every Summer 2022 run. Deriving the two colours
costs one slow-path read per event, which an event needs anyway.

## Agreement: 36 of 36

36 runs, 18 per dominant layout, sampled evenly across the event by scheduled time so a
mid-event overlay change could not hide inside a contiguous block. All were `high` on the slow
path. Fast read: `--tail 60 --step 10 --height 480`, crop pinned, no calibration.

| | `16x9-1p` | `4x3-1p` | all |
|---|---|---|---|
| runs | 18 | 18 | 36 |
| **fast answer == slow answer** | **18** | **18** | **36 (100%)** |
| download errors | 0 | 0 | 0 |
| refused to answer | 0 | 0 | 0 |

Not one disagreement, and not one second of drift. The pinned crop reproduced the slow path's
`high` tier exactly.

Two things behind that number are worth more than the number.

**A 60s tail sometimes catches the finish, which brings the ramp with it.** On 4 of 36 runs some
frames were still orange and still climbing — the slow path's second confirmation, arriving free.
All four agreed with the slow path. The prototype scored those as `check` because it demanded
every frame agree; that rule is wrong, and the physics-shaped one — *at least two green frames,
and every green frame reading the same value* — moves 4 runs from `check` to `accept` without
changing a single answer. Rescored from the recorded aggregates, not re-read: 28 `accept`, 8
`check`, still 36 of 36 correct.

**A frozen frame is not quite one observation, and the disagreement has a signature.** #69's
obstacle 3 assumes two frames of a frozen overlay are the same pixels, so tesseract makes the
same error twice. Empirically the encoder does not reproduce them exactly, and on **8 of 36
runs** at least one frame read exactly `+10:00:00` — a hallucinated leading `1` on the hours
digit (`0:29:07` read as `10:29:07`, `5:41:21` as `15:41:21`). The modal vote over six frames won
all 8 times. That is *some* independence, and it is much less than the ramp's: it is one glyph
misread by a deterministic engine on near-identical pixels, not a second measurement.

### The four deliberate hard cases

Agreeing with the slow path where the slow path was right says nothing about the runs where it
was wrong, so four known-bad runs were read on purpose.

| run | truth | slow path | fast path | |
|---|---|---|---|---|
| **Vib-Ribbon** — slow path read the estimate | `0:16:39` | `0:20:00` ✗ | **`0:16:39` accept** ✓ | fast path wins outright |
| **Final Fantasy IX** — part 1 of a cumulative multi-part VOD | `24:05:51` | `11:59:16` ✗ | **reject** | "never stopped on camera" |
| **QuizBOSH** — the one 1p crop not at the common position | `2:12:28` | `2:12:28` ✓ | **reject** | refuses rather than mis-reads |
| **Super Mario Bros. 3** — the tail holds a bonus run | `0:57:08` | `0:04:11` ✗ | `0:04:11` | **shares the error** |

Three of four are the fast path behaving better than or as safely as the slow path. The fourth is
the whole reason this is a cross-check and not a replacement.

Two further cases came free from clips still in the cache. **Final Fantasy IX Part 2/3** reads a
still-running orange clock across its last 30 seconds and is rejected; **Part 3/3** reads
`24:05:51` — the true cumulative time, which the slow path missed. The multi-part failure is
visible from the tail after all, as long as you look at the colour.

## What the fast path cannot catch

1. **Whose clock it is.** This is the one that matters. A bonus run, a donation incentive, or a
   second run in the same slot leaves a *stopped, green, correctly-cropped* clock in the tail, and
   nothing about that frame is wrong except that it belongs to a different run. SMB3 is the proof:
   the fast path read it cleanly and confidently, and it was `0:04:11` against a truth of
   `0:57:08`. **No crop, no colour, and no number of end-frames fixes this** — it is only visible
   by looking further back, which is the thing the fast path exists not to do. On Summer 2025 this
   class was 2 of 170 runs.
2. **An overlay it has not been calibrated for.** The rectangle and the palette are both
   per-event. Pointed at Summer 2022 the Summer 2025 pin reads nothing, and its rectangle contains
   that overlay's estimate. A new event must derive both before the fast path is safe on it, and
   nothing in the artefact detects the mistake.
3. **The 1-in-42 run inside a known event whose timer is somewhere else.** QuizBOSH refused to
   answer, which is the right failure, but it refused *silently* in the sense that the reason is
   "nothing timer-shaped here", not "this run needs the slow path".
4. **A resolver error.** Unchanged from the slow path: a confident read off the wrong video is
   undetectable from the video. Summer 2025 removed this class by using ESA's own links; a
   title-search event still has it.
5. **Races and every `-2p`-and-above layout.** Excluded by construction, as #69 says.
6. **The second confirmation, on runs that finish well before the VOD ends.** Where the ramp is
   outside the tail, the answer rests on the plateau and the colour alone.

## What this assumes from #65, and what should change about it

The recommendation assumes `equals_estimate` is in place — it is, at 28e210d — but it leans on
it less than #69 expected, because the colour gate covers the same failure by a different route
and covers it more completely.

Two things found here bear on its shape:

- **The FFIX Part 3 hole is real and the colour gate closes it.** Whole-second equality against
  the *schedule* estimate cannot fire when the overlay shows `24:00:00` and the schedule says
  `23:59:59`. The colour gate does not compare numbers at all; it rejects the estimate because it
  is white. If a fast path ships, that hole stops being theoretical — a pinned crop that drifts
  onto the estimate is exactly the failure #65 was written for.
- **The estimate-ratio guard should not be dropped for the fast path.** `runs/esa-summer-2025.md`
  asks for it to go, on a record of 0-for-13 on the slow path. On the fast path it is the *only*
  thing that catches SMB3: the read is `0:04:11` against a `1:00:00` estimate, 0.07x. Across the
  36 sampled runs the ratio spans 0.47x–1.62x, so the 0.4–2.0 window would have produced **zero**
  false rejects. The guard is useless where the slow path's ramp already protects the answer and
  load-bearing where it does not.

## Recommendation

**Adopt as a cross-check only**, in two parts, with the second much cheaper than the first.

**1. Fold the colour gate into the existing pipeline now, and do not build a fast mode for it.**
The slow path already downloads the tail and already extracts the frames. Classifying the
timer's colour on the frames in hand costs **zero requests, zero bandwidth and about a second of
CPU**, and it supplies three things calibration cannot:

- a per-frame *stopped* signal, where `_running_score` only offers a *ticking* one;
- rejection of a crop that landed on the estimate, including the case `equals_estimate` cannot
  reach;
- rejection of a run with no finish on camera — Micro Mages, Summer 2025's single unvouched run,
  never turns green.

This is the whole of the spike's value and it does not need the fast path to exist.

**2. The standalone fast path is viable, and worth having for re-reads rather than for backfills.**
It reproduces the `high` tier exactly at a twentieth of the bandwidth. But it cannot see the
bonus-run class at all, it needs a per-event pin and palette that only a slow-path pass produces,
and its wall-clock prize on the one event that hit the bot wall is ~1.4x rather than what the
headline suggests. Use it to re-read an event whose answers already exist — after a resolver fix,
a consensus change, a suspected regression — where a disagreement is a flag rather than an answer.
Do not use it to read an event for the first time.

**Not recommended:** pinning on `hidden:Layout`, and the binary-search variant.

### If someone picks this up

- Record the **frame size** next to the `crop` in `batch` output. It costs nothing, it is what
  makes every crop recorded so far comparable, and it is what #71 actually needs.
- Derive the pin and the two palette colours per event, from the slow path's own first few runs,
  and store them beside the event conf rather than in code.
- ESA Summer 2024 (`horaro.net/esa/2024-summer`) exposes `Layout` as a **visible** column, with
  the same vocabulary — `16x9-1p` 49, `4x3-1p` 49. The backfill under
  [#45](https://github.com/TheShrug/esavods/issues/45) is the natural place to get a second
  event's crops, and this spike's `crops_norm.py` will read them as-is once that event has an
  `all-results.csv`. That is the evidence #71 is missing.

## Artefacts

Everything in `spikes/last-frame-fast-path/`. Kept rather than deleted because
`crops_norm.py` and `crop_size.py` are the evidence #71 needs, and `fastread.py` is the colour
gate in the form part 1 would adopt.

| | |
|---|---|
| `fetch_layouts.py` | `hidden:Layout` and ESA's VOD link out of a schedule — two JSON fetches, no video |
| `crops_norm.py` | the recorded `crop` column normalised by frame size; the table above |
| `crop_size.py` | crop size as a fraction of frame width; the #71 threshold |
| `strip_scan.py` | timer position and colour over the 53 stills in `out/frames/` |
| `fastread.py` | the pinned-crop read and the colour gate |
| `run_cached.py` | dry-run against clips already in the cache — costs nothing |
| `run_sample.py` | the 40-run measurement, with the bot-wall breaker and a budget |
| `compare.py`, `rescore.py` | the agreement tables |
| `layouts.csv`, `sample.csv`, `fast-results.csv` | inputs and raw results |
| `s2022-early.png`, `s2022-late.png` | Summer 2022's timer, running and stopped |

`run_cached.py`, `run_sample.py`, `fastread.py` and `strip_scan.py` run inside the tool's own
image, which has PIL and tesseract:

```sh
docker run --rm --entrypoint python \
  -v vodtimer-cache:/cache -v "$(pwd -W)/out:/out" \
  -v "$(pwd -W)/spikes/last-frame-fast-path:/spike" \
  esavods/vod-timer:latest /spike/run_cached.py 30 5
```

The rest are plain CSV arithmetic and run on any Python 3.8+.
