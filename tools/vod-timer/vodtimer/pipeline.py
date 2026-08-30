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

    start = max(0, meta.duration - tail)
    clip = video.download_window(video_id, start, meta.duration, height, ytdlp_args)
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
