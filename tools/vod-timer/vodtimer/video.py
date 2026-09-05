"""Fetch just enough of a YouTube VOD to read its on-screen timer.

Nothing here downloads a whole video. `probe` is metadata only, and
`download_window` asks yt-dlp for a byte range via --download-sections, so a
90-minute VOD costs us the ~12 minutes we actually look at.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

YOUTUBE_WATCH = "https://www.youtube.com/watch?v={}"

# Any real 13-minute clip is megabytes; anything smaller is a failed cut.
MIN_CLIP_BYTES = 512 * 1024

# How much shorter than the window it was asked for an *honest* clip may be.
#
# A byte-count cannot do this job: 50 seconds of 480p clears MIN_CLIP_BYTES
# comfortably, so the two truncated Summer 2022 clips (11 and 14 frames where
# 50 were expected) passed every check and read as confident times. The only
# thing that distinguishes them is how many seconds of video came back.
#
# The slack covers the two ways a complete clip legitimately measures short:
#   - a range cut lands on a keyframe, worth a second or two either way;
#   - a duration from `seed()` is the search result's, rounded *up* - by one
#     second across eight measured ESA uploads - so the last second of the
#     requested window is past the real end of the file.
# 5% of the default 780s tail is 39s, which swallows both with room to spare
# and is still an order of magnitude below the ~670s and ~640s that actually
# went missing. The floor keeps a short window (a VOD shorter than --tail
# yields one) from being policed to the frame.
CLIP_SLACK_SECONDS = 5.0
CLIP_SLACK_FRACTION = 0.05


class VideoError(RuntimeError):
    pass


@dataclass
class Meta:
    video_id: str
    title: str
    duration: int
    channel: str | None = None
    upload_date: str | None = None


def cache_dir() -> Path:
    d = Path(os.environ.get("VODTIMER_CACHE", "/cache"))
    d.mkdir(parents=True, exist_ok=True)
    return d


def _run(cmd: list[str], timeout: int = 900) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-6:]
        raise VideoError(f"{cmd[0]} failed ({proc.returncode}):\n  " + "\n  ".join(tail))
    return proc.stdout


def probe(video_id: str, ytdlp_args: list[str] | None = None) -> Meta:
    cached = cache_dir() / f"{video_id}.meta.json"
    if cached.exists():
        d = json.loads(cached.read_text())
    else:
        out = _run(
            ["yt-dlp", "-J", "--skip-download", "--no-warnings", "--no-playlist"]
            + (ytdlp_args or [])
            + [YOUTUBE_WATCH.format(video_id)],
            timeout=180,
        )
        raw = json.loads(out)
        d = {
            "id": raw.get("id"), "title": raw.get("title"), "duration": raw.get("duration"),
            "channel": raw.get("channel"), "upload_date": raw.get("upload_date"),
        }
        cached.write_text(json.dumps(d))
    if not d.get("duration"):
        raise VideoError(f"{video_id}: no duration in metadata (members-only, or removed?)")
    return Meta(
        video_id=d.get("id") or video_id,
        title=d.get("title") or "",
        duration=int(d["duration"]),
        channel=d.get("channel"),
        upload_date=d.get("upload_date"),
    )


def seed(video_id: str, title: str, duration: int, channel: str | None = None) -> bool:
    """Write a cache entry from a search result, so `probe` never has to ask.

    `resolve` already learns a video's title and duration from the same
    `ytsearch` that found it, and then `analyse` spends a second YouTube
    request re-asking for both. On a wall that is counted in requests rather
    than bytes - it arrived at ~250 on ESA Summer 2025 and ~275 on Summer 2023
    - that doubling is the difference between reading an event in one sitting
    and three.

    The search's duration is not the probe's: measured across eight ESA
    uploads it is the true length rounded *up* by exactly one second, and a
    third-party re-upload over-reported by 58. Up is the safe direction. Every
    consumer treats duration as where the end of the file is - the tail window
    is `duration - tail` to `duration`, and ffmpeg simply stops at EOF - so an
    over-estimate costs nothing, where an under-estimate would cut the window
    short of the finish and hide the very frames the read needs.

    Returns False rather than overwriting an entry already in the cache: a
    real probe knows the channel and the upload date, and this does not.
    """
    if not video_id or not duration:
        return False
    path = cache_dir() / f"{video_id}.meta.json"
    if path.exists():
        return False
    path.write_text(json.dumps({
        "id": video_id, "title": title or "", "duration": int(duration),
        "channel": channel, "upload_date": None,
        # Not read back by probe(); here so a cache entry can be told apart
        # from one a real probe wrote, which is the only way to know whether
        # the duration is exact or rounded up.
        "seeded": True,
    }))
    return True


def search(query: str, limit: int = 5, ytdlp_args: list[str] | None = None) -> list[dict]:
    """Thin wrapper over yt-dlp's own ytsearch, so no HTML scraping."""
    out = _run(
        ["yt-dlp", "-J", "--flat-playlist", "--no-warnings"]
        + (ytdlp_args or [])
        + [f"ytsearch{limit}:{query}"],
        timeout=180,
    )
    data = json.loads(out)
    return [
        {"video_id": e.get("id"), "title": e.get("title"), "duration": e.get("duration")}
        for e in data.get("entries", [])
        if e.get("id")
    ]


def clip_duration(path: Path) -> float:
    """Seconds of video in `path`, per ffprobe.

    ffprobe ships with the ffmpeg `extract_frames` already shells to, so this
    costs a subprocess and no new dependency. Raises VideoError if the file
    cannot be opened or carries no duration - which is the same answer we
    want for it anyway: do not trust this clip.
    """
    out = _run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        timeout=120,
    )
    try:
        return float(out.strip().splitlines()[0])
    except (IndexError, ValueError):
        raise VideoError(f"{path.name}: ffprobe found no duration in the clip")


def _clip_fault(clip: Path, start: int, end: int) -> str | None:
    """Why this clip cannot stand in for [start, end), or None if it can.

    Compared against `end - start`, deliberately, and never against --tail:
    `pipeline.analyse` computes `start = max(0, duration - tail)`, so a video
    shorter than the tail asks for a window shorter than the tail and is
    entirely well-formed when it comes back that size.
    """
    requested = end - start
    try:
        got = clip_duration(clip)
    except VideoError as exc:
        return f"clip will not open - {exc}"
    if requested <= 0:
        return None
    slack = max(CLIP_SLACK_SECONDS, CLIP_SLACK_FRACTION * requested)
    if got < requested - slack:
        return (f"clip is only {got:.0f}s of the {requested}s window "
                f"{start}-{end}s that was requested - the download stopped "
                f"early, so the finish may never be on screen")
    return None


def download_window(
    video_id: str,
    start: int,
    end: int,
    height: int = 720,
    ytdlp_args: list[str] | None = None,
) -> Path:
    """Download [start, end) seconds of the video. Video stream only, no audio."""
    key = hashlib.sha1(f"{video_id}:{start}:{end}:{height}".encode()).hexdigest()[:12]
    stem = cache_dir() / f"{video_id}.{key}"
    for existing in cache_dir().glob(f"{stem.name}.*"):
        if existing.suffix == ".json":
            continue
        if existing.stat().st_size < MIN_CLIP_BYTES:
            existing.unlink()      # a previous run cached a stub; don't trust it
            continue
        # Size is not enough. A truncated range request produces a valid,
        # playable, *short* file that clears MIN_CLIP_BYTES easily, and once
        # one is in the cache every later run reuses it - --resume included,
        # which is precisely the run meant to fix it. So measure it, and drop
        # it if it is short or will not open at all.
        if _clip_fault(existing, start, end):
            existing.unlink()
            continue
        return existing

    # Download into a scratch dir and move the finished file into place. yt-dlp
    # writes its output incrementally, so a run killed mid-download would
    # otherwise leave a truncated clip in the cache that is large enough to
    # pass every check and quietly wrong for every future run.
    tmp = Path(tempfile.mkdtemp(dir=cache_dir(), prefix=".dl-"))
    try:
        _run(
            [
                "yt-dlp",
                # Direct HTTPS only. --download-sections cannot range-seek an
                # HLS stream: yt-dlp exits 0 having written a few hundred
                # bytes, which then fails much later inside ffmpeg as "output
                # file contains no stream".
                "-f", (f"bv*[height<={height}][ext=mp4][protocol^=http]/"
                       f"bv*[height<={height}][protocol^=http]/"
                       f"bv*[height<={height}]/bv*/b"),
                "--download-sections", f"*{start}-{end}",
                "--no-warnings", "--no-playlist", "--no-part",
                "-o", str(tmp / "clip.%(ext)s"),
            ]
            + (ytdlp_args or [])
            + [YOUTUBE_WATCH.format(video_id)]
        )
        hits = sorted(tmp.glob("clip.*"))
        if not hits:
            raise VideoError(f"{video_id}: yt-dlp reported success but wrote no file")
        got = hits[0]
        if got.stat().st_size < MIN_CLIP_BYTES:
            raise VideoError(
                f"{video_id}: yt-dlp exited 0 but wrote only {got.stat().st_size} "
                f"bytes for {start}-{end}s (no seekable format?)"
            )
        # Raised, not downgraded here: `analyse` propagates it, `cmd_batch`
        # catches it and records `confidence: none` with this message in
        # `notes`, and --resume keys "done" on a non-empty final_time, so the
        # run is re-read next time instead of standing as an answer. The
        # clip's length is a property of the clip, not of the readings, so
        # nothing in consensus needs to know about it.
        fault = _clip_fault(got, start, end)
        if fault:
            raise VideoError(f"{video_id}: {fault}")
        # NB: not stem.with_suffix() - the cache key is itself a dotted
        # suffix, and with_suffix() would replace it rather than append,
        # collapsing every window of a video onto one uncacheable name.
        final = stem.parent / (stem.name + got.suffix)
        got.replace(final)
        return final
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def extract_frames(clip: Path, outdir: Path, step: float) -> list[Path]:
    """One frame every `step` seconds of the clip, in order."""
    outdir.mkdir(parents=True, exist_ok=True)
    for old in outdir.glob("f_*.png"):
        old.unlink()
    _run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", str(clip),
        "-vf", f"fps=1/{step}",
        "-fps_mode", "passthrough",
        str(outdir / "f_%05d.png"),
    ])
    return sorted(outdir.glob("f_*.png"))


def forget_clips(video_id: str) -> None:
    """Drop a video's cached clips, keeping its metadata. A whole-marathon run
    would otherwise leave tens of gigabytes behind for footage already read."""
    for path in cache_dir().glob(f"{video_id}.*"):
        if path.suffix != ".json":
            path.unlink(missing_ok=True)
