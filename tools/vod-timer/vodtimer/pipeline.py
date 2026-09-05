"""Wire the three stages together: fetch a tail window, OCR it, resolve it."""
from __future__ import annotations

import tempfile
from pathlib import Path

from PIL import Image

from . import ocr, video

DIM, RESET = "[2m", "[0m"
from .consensus import Reading, resolve


def parse_duration(text: str | None) -> float | None:
    """Accept 45:00, 00:45:00, 0:44:42.5 or a bare number of seconds."""
    if text is None or text == "":
        return None
    text = str(text).strip()
    if ":" not in text:
        return float(text)
    parts = [float(p) for p in text.split(":")]
    total = 0.0
    for p in parts:
        total = total * 60 + p
    return total


def fetch_window(
    video_id: str,
    meta: video.Meta,
    tail: int,
    height: int,
    ytdlp_args: list[str] | None = None,
    log=None,
) -> tuple[video.Meta, int, Path]:
    """The tail window as a clip, plus the metadata and start it really used.

    A duration from `video.seed` is a search result's, not a probe's: rounded
    up by a second across eight measured ESA uploads, and over-reported by 58
    for one third-party re-upload. The window's end *is* that duration, so an
    over-estimate asks for footage past the end of the file and the clip comes
    back short of what was requested - which, from the clip alone, is
    indistinguishable from the truncated download #63 is about.

    Left there, that is a permanent refusal: the read fails, --resume re-reads
    it, and it fails identically forever, because nothing in the loop ever
    revisits the duration. Widening the slack to swallow 58s would instead
    blunt the check on exactly the reads that skipped a probe, which are the
    ones with the least evidence behind them.

    So when a *seeded* window comes back short, spend the request that seeding
    saved and ask for the real duration. If it accounts for the shortfall, the
    metadata was wrong rather than the download, and the corrected window is
    read instead - a full tail, not the 722s the bad duration left. If it does
    not, the download really was truncated and the error stands, at the cost
    of one probe and no second download.

    This settles a video once. `probe(refresh=True)` replaces the seeded entry
    with an exact one, so every later run - and every other run of the same
    VOD - starts from the true duration, and the recovery cannot recurse
    because the replacement is not seeded.
    """
    log = log or (lambda msg: None)
    start = max(0, meta.duration - tail)
    try:
        clip = video.download_window(video_id, start, meta.duration, height, ytdlp_args)
        return meta, start, clip
    except video.ShortClipError as short:
        if not video.is_seeded(video_id):
            raise
        log(f"short clip from a seeded duration - re-probing {video_id}")
        fresh = video.probe(video_id, ytdlp_args, refresh=True)
        # The same question the clip already failed, asked against the footage
        # that actually existed rather than the footage that was asked for.
        if not video.clip_is_complete(short.got, fresh.duration - start):
            raise
        log(f"seeded duration {ocr.fmt(meta.duration)} was really "
            f"{ocr.fmt(fresh.duration)}; re-reading the corrected window")
        start = max(0, fresh.duration - tail)
        clip = video.download_window(video_id, start, fresh.duration, height, ytdlp_args)
        return fresh, start, clip


def analyse(
    video_id: str,
    estimate: str | None = None,
    tail: int = 780,
    step: float = 10.0,
    height: int = 720,
    min_plateau: int = 3,
    crop: tuple[int, int, int, int] | None = None,
    debug_dir: Path | None = None,
    ytdlp_args: list[str] | None = None,
    verbose: bool = False,
) -> dict:
    def log(msg: str) -> None:
        if verbose:
            print(f"  {msg}", flush=True)

    meta = video.probe(video_id, ytdlp_args)
    log(f"{meta.title!r} - {ocr.fmt(meta.duration)}")

    # `meta` can come back corrected: a seeded duration that over-reported is
    # only caught by the window it produces. Everything below - the frame
    # positions, the resolve bound, the CSV's `duration` - wants the corrected
    # one.
    meta, start, clip = fetch_window(video_id, meta, tail, height, ytdlp_args, log)
    log(f"window {ocr.fmt(start)}-{ocr.fmt(meta.duration)} -> {clip.stat().st_size / 1e6:.1f} MB")

    with tempfile.TemporaryDirectory() as tmp:
        frames = video.extract_frames(clip, Path(tmp), step)
        log(f"{len(frames)} frames at {step}s spacing")
        if not frames:
            return {"video_id": video_id, "title": meta.title, "duration": meta.duration,
                    "error": "ffmpeg produced no frames"}

        positions = [start + i * step for i in range(len(frames))]

        if crop:
            box = ocr.Box(*crop)
            info = {"sampled": 0, "agreed": 0, "running": True, "candidates": [], "forced": True}
            log(f"crop forced to {box.as_tuple()}")
        else:
            with Image.open(frames[0]) as probe_img:
                bounds = probe_img.size
            box, info = ocr.calibrate(frames, positions)
            if box is None:
                return {"video_id": video_id, "title": meta.title, "duration": meta.duration,
                        "error": f"no timer-shaped text found in {info['sampled']} frames"}
            box = box.pad(box.w // 12 + 5, box.h // 5 + 3, bounds)
            for c in info["candidates"]:
                log(f"{DIM}candidate {c['box']} seen {c['hits']}x "
                    f"ticking {c['running']} e.g. {c['sample']}{RESET}")
            log(f"timer at {box.as_tuple()}"
                + ("" if info["running"] else "  (WARNING: nothing on screen was ticking)"))

        readings = [
            Reading(index=i, position=pos, value=ocr.read_box(f, box, debug_dir))
            for i, (f, pos) in enumerate(zip(frames, positions))
        ]

    est = parse_duration(estimate)
    result = resolve(readings, meta.duration, est, min_plateau)

    return {
        "video_id": video_id,
        "title": meta.title,
        "duration": meta.duration,
        "duration_hms": ocr.fmt(meta.duration),
        "estimate": estimate,
        "crop": list(box.as_tuple()),
        "calibration": info,
        "window": [start, meta.duration],
        "step": step,
        **result.to_dict(),
        "readings": [
            {"pos": round(r.position, 1), "value": r.value,
             "time": ocr.fmt(r.value) if r.value is not None else None}
            for r in readings
        ],
    }
