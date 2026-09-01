"""Turn a noisy series of per-frame timer readings into one trustworthy answer.

The physics of the thing is what makes this checkable. A run timer advances at
exactly one second per second and then stops dead when the runner finishes, so
a correct series looks like a ramp of slope 1 followed by a flat plateau. That
gives two independent confirmations of the same number:

  * the plateau itself - N frames that all read the same value, and
  * the ramp - frames from *before* the finish, whose reading plus the time
    remaining to the plateau must extrapolate to that same value.

A tesseract digit error breaks one or the other. An answer that satisfies both
was effectively read several times over from independent pixels.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field, asdict

from .ocr import fmt

# Frames are cut on the nearest decodable frame, so positions carry a little
# jitter; 2s of slack keeps that from being mistaken for a misread digit.
SLOPE_TOLERANCE = 2.0


@dataclass
class Reading:
    index: int
    position: float   # seconds into the source video (approximate)
    value: float | None


@dataclass
class Result:
    final_seconds: float | None = None
    final_time: str | None = None
    confidence: str = "none"
    reasons: list[str] = field(default_factory=list)
    plateau_frames: int = 0
    plateau_starts_at: float | None = None
    ramp_frames: int = 0
    ramp_error: float | None = None
    ramp_band: list[str] | None = None
    frames_read: int = 0
    frames_total: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


def _modal_offset(valid: list[Reading]) -> float | None:
    """The start-offset the pre-finish frames agree on, found *before* an answer
    has been chosen.

    A frame at position p reading v implies the timer started at offset v - p.
    Every honest pre-finish frame shares that one offset. A frame after the
    finish does not, because the clock is frozen while p keeps advancing, so
    each of those contributes a distinct offset and none of them repeats. The
    offset that does repeat is therefore the ramp's, whichever side of the
    finish most of the sampled window falls on.

    Computing it here rather than inside _ramp() is the point of the change: the
    ramp can then *arbitrate* which value is the answer, instead of merely
    checking the answer `max` had already picked.
    """
    counts = Counter(round(r.value - r.position) for r in valid)
    offset, seen = counts.most_common(1)[0]
    # Three agreeing frames is the bar the ramp check already uses to call
    # itself good. Below that there is no ramp to speak of, and nothing that
    # should be overruling a plateau.
    return float(offset) if seen >= 3 else None


def _ramp_end(valid: list[Reading], plateau_start: float, offset: float | None):
    """Position of the last frame still *on* the ramp.

    Not simply the last frame before the plateau. Those differ whenever a
    misread sits between the ramp and the plateau, and taking the misread's
    position drags the low edge of the predicted band past the true value -
    rejecting the very answer the band exists to protect.
    """
    if offset is None:
        on_ramp = [r.position for r in valid if r.position < plateau_start]
    else:
        on_ramp = [r.position for r in valid
                   if r.position < plateau_start
                   and abs(r.value - (offset + r.position)) <= SLOPE_TOLERANCE]
    return max(on_ramp, default=plateau_start)


def _band_for(valid: list[Reading], value: float, offset: float):
    """The window a run whose plateau is `value` would have had to finish in."""
    plateau_start = next(r.position for r in valid if r.value == value)
    return (offset + _ramp_end(valid, plateau_start, offset) - SLOPE_TOLERANCE,
            offset + plateau_start + SLOPE_TOLERANCE)


def _plateau(valid: list[Reading], min_frames: int, offset: float | None = None):
    """The value that holds steady over the tail - preferring one the ramp predicts.

    Taking the *largest* steady value is what made a single misread digit
    authoritative. A `3` read as a `5` is always larger than the truth, so `max`
    selected it by construction: all seven Summer 2022 +20:00 failures and eight
    of the ten Winter 2021 corrections had exactly this shape.
    """
    counts = Counter(r.value for r in valid)
    candidates = sorted((v for v, n in counts.items() if n >= min_frames),
                        reverse=True)
    if not candidates:
        return None, [], False

    overruled = False
    if offset is not None:
        agreeing = []
        for v in candidates:
            low, high = _band_for(valid, v, offset)
            if low <= v <= high:
                agreeing.append(v)
        if not agreeing:
            # Nothing that holds steady is consistent with the clock the ramp
            # describes. Report no plateau and let the caller fall back to the
            # largest *plausible* reading, rather than certify a misread as a
            # confident answer. This is the Castlevania shape: the true value
            # was read only twice, under min_plateau, so it is not a candidate
            # here at all and only the fallback can find it.
            return None, [], False
        overruled = agreeing[0] != candidates[0]
        candidates = agreeing

    value = candidates[0]
    members = [r for r in valid if r.value == value]
    first = members[0].index
    trailing = [r for r in valid if r.index >= first]

    noise = [r for r in trailing if r.value != value]
    if offset is not None:
        # A stopped clock cannot climb past the value it stopped at, so a
        # trailing reading *above* `value` is a misread digit and not a
        # disagreement about when the run ended. Counting those as dissent is
        # what let a five-frame 0:51:32 outvote a two-frame 0:31:32 on
        # Castlevania: Circle of the Moon.
        noise = [r for r in noise if r.value < value]

    # Allow a stray misread inside the plateau, but not a wholesale disagreement.
    if len(noise) > max(1, len(trailing) // 5):
        return None, [], False
    return value, members, overruled


def _ramp(valid: list[Reading], value: float, ramp_end: float, plateau_start: float):
    """Do the pre-finish frames agree, and do they land on the same final time?

    A frame at position p showing v implies the timer started at offset v - p.
    Every honest pre-finish reading shares that one offset, so the modal offset
    is the ramp and anything far from it is a misread digit, discarded.

    The timer stops at some unobserved instant between the last ramp frame and
    the first plateau frame, so the ramp does not predict a single number - it
    predicts a band one frame-interval wide. The answer has to land in it.
    """
    ramp = [r for r in valid if r.position < plateau_start and r.value < value]
    if not ramp:
        return 0, None, None

    offsets = [round(r.value - r.position) for r in ramp]
    modal = Counter(offsets).most_common(1)[0][0]
    agree = [o for o in offsets if abs(o - modal) <= SLOPE_TOLERANCE]

    low = modal + ramp_end - SLOPE_TOLERANCE
    high = modal + plateau_start + SLOPE_TOLERANCE
    miss = 0.0 if low <= value <= high else min(abs(value - low), abs(value - high))
    return len(agree), miss, (low, high)


def equals_estimate(value: float | None, estimate_seconds: float | None) -> bool:
    """Did the read land exactly on the run's scheduled estimate?

    A value that lands exactly on the estimate is not an answer. The layout
    shows the estimate next to the timer, in the same font, and it OCRs more
    cleanly because it never moves. Calibration separates the two by which one
    *ticks* - and when a run finishes well before its VOD ends, no frame in the
    sampled window shows a ticking clock at all. Both candidates then score
    zero, the tie-break is `hits`, and the estimate wins it. Three of ESA
    Summer 2025's five corrections were exactly this, which made it a more
    frequent fault on that event than the 3/5 glyph confusion.

    Compared at whole-second resolution because an estimate is always a whole
    number of seconds; a read carrying a stray tenth inside the same second is
    the same suspicion, not a different one. Nothing wider than that: on Summer
    2025 the nearest honest read sat 3s off its estimate (Ocarina of Time,
    1:25:03 against 1:25:00) and was right, so a tolerance would start costing
    correct answers almost immediately.
    """
    if not estimate_seconds or value is None:
        return False
    return round(value) == round(estimate_seconds)


def resolve(
    readings: list[Reading],
    duration: int,
    estimate_seconds: float | None = None,
    min_plateau: int = 3,
) -> Result:
    res = Result(frames_total=len(readings))
    valid = [r for r in readings if r.value is not None]
    res.frames_read = len(valid)

    if not valid:
        res.reasons.append("no frame produced a readable timer")
        return res

    offset = _modal_offset(valid)
    value, members, overruled = _plateau(valid, min_plateau, offset)
    if value is None:
        # The video may simply end on the finish with no outro to hold the
        # frozen clock. Fall back to the largest reading - but only among those
        # the clock could actually have shown by the frame they appear on. A
        # reading claiming more elapsed time than has passed is a misread, and
        # a bare max() is precisely how the inflated one used to win.
        pool = valid
        if offset is not None:
            plausible = [r for r in valid
                         if r.value <= offset + r.position + SLOPE_TOLERANCE]
            if plausible:
                pool = plausible
        value = max(r.value for r in pool)
        members = [r for r in valid if r.value == value]
        res.reasons.append("no stable plateau; fell back to the largest reading")
    elif overruled:
        res.reasons.append(
            "a larger value held more frames, but the ramp does not predict it; "
            "took the value the ramp agrees with"
        )

    res.plateau_frames = len(members)
    res.plateau_starts_at = members[0].position
    res.final_seconds = value
    res.final_time = fmt(value)

    ramp_end = _ramp_end(valid, members[0].position, offset)
    res.ramp_frames, res.ramp_error, band = _ramp(
        valid, value, ramp_end, members[0].position)
    if band:
        res.ramp_band = [fmt(band[0]), fmt(band[1])]

    ok = True
    if value > duration + 1:
        res.reasons.append(f"reading {fmt(value)} exceeds the video's own {fmt(duration)}")
        ok = False
    if value < 60:
        res.reasons.append("reading is under a minute, which no ESA slot is")
        ok = False
    if estimate_seconds:
        ratio = value / estimate_seconds
        if not 0.4 <= ratio <= 2.0:
            res.reasons.append(f"reading is {ratio:.2f}x the {fmt(estimate_seconds)} estimate")
            ok = False

    matches_estimate = equals_estimate(value, estimate_seconds)

    ramp_good = res.ramp_frames >= 3 and res.ramp_error == 0.0
    plateau_good = res.plateau_frames >= min_plateau and not any(
        "fell back" in r for r in res.reasons
    )

    if not ok:
        res.confidence = "reject"
    elif plateau_good and ramp_good:
        res.confidence = "high"
        res.reasons.append(
            f"{res.plateau_frames} frames hold at {fmt(value)}, and {res.ramp_frames} "
            f"pre-finish frames independently predict "
            f"{res.ramp_band[0]}-{res.ramp_band[1]}"
        )
    elif plateau_good or ramp_good:
        res.confidence = "medium"
        res.reasons.append("only one of the two checks passed; worth a human glance")
    else:
        res.confidence = "low"
        res.reasons.append("neither a stable plateau nor a consistent ramp")

    if matches_estimate:
        # Demoted, never rejected. A run really can finish on a round number,
        # and this read may be that run - so it goes in front of a person
        # instead of being certified or thrown away. Anything below `high`
        # already reaches the review list, so only `high` needs moving; the
        # tier's own reason is left in place, because "both checks passed *and*
        # it equals the estimate" is what tells the reviewer how hard to look.
        if res.confidence == "high":
            res.confidence = "medium"
        # First in the list: `review.describe` truncates the notes column at 110
        # characters, and this is the one sentence the reviewer needs.
        res.reasons.insert(0, f"reading is exactly the {fmt(estimate_seconds)} "
                              "estimate; calibration may have read that, not the timer")

    return res
