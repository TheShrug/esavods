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


def _plateau(valid: list[Reading], min_frames: int):
    """Largest value that holds steady over the tail of the series."""
    counts = Counter(r.value for r in valid)
    candidates = [v for v, n in counts.items() if n >= min_frames]
    if not candidates:
        return None, []
    value = max(candidates)
    members = [r for r in valid if r.value == value]
    first = members[0].index
    trailing = [r for r in valid if r.index >= first]
    # Allow a stray misread inside the plateau, but not a wholesale disagreement.
    if sum(1 for r in trailing if r.value != value) > max(1, len(trailing) // 5):
        return None, []
    return value, members


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

    value, members = _plateau(valid, min_plateau)
    if value is None:
        # The video may simply end on the finish with no outro to hold the
        # frozen clock. Fall back to the largest reading, but say so.
        value = max(r.value for r in valid)
        members = [r for r in valid if r.value == value]
        res.reasons.append("no stable plateau; fell back to the largest reading")

    res.plateau_frames = len(members)
    res.plateau_starts_at = members[0].position
    res.final_seconds = value
    res.final_time = fmt(value)

    ramp_end = max((r.position for r in valid if r.position < members[0].position),
                   default=members[0].position)
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

    return res
