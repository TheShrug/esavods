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
        if existing.stat().st_size >= MIN_CLIP_BYTES:
            return existing
        existing.unlink()          # a previous run cached a stub; don't trust it

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
