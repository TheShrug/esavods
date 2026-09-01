"""Dry-run the fast path on whatever clips are still in the cache.

Free: no yt-dlp invocation at all. The cached clips are full 600s tails, so
taking their last `--tail` seconds is exactly what a short-window download
would have produced, minus the download.
"""
import json, subprocess, sys, tempfile
from pathlib import Path

sys.path.insert(0, "/app")
sys.path.insert(0, "/spike")

from vodtimer import ocr, video
import fastread

TAIL = int(sys.argv[1]) if len(sys.argv) > 1 else 30
STEP = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0

cache = Path("/cache")
for clip in sorted(cache.glob("*.mp4")):
    vid = clip.name.split(".")[0]
    meta = cache / (vid + ".meta.json")
    title = json.loads(meta.read_text())["title"] if meta.exists() else "?"
    dur = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(clip)],
        capture_output=True, text=True).stdout.strip()
    clip_len = float(dur)
    start = max(0.0, clip_len - TAIL)
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(start),
                        "-i", str(clip), "-vf", "fps=1/%s" % STEP,
                        "-fps_mode", "passthrough", tmp + "/f_%05d.png"], check=True)
        frames = sorted(Path(tmp).glob("f_*.png"))
        reads = fastread.read_frames(frames)
        v = fastread.verdict(reads, None)
    print("%-12s %-46s clip %.0fs  last %ds" % (vid, title[:46], clip_len, TAIL))
    print("    box %s   %s -> %-9s  %s" % (
        reads[0]["box"] if reads else "-", v["colours"], v["time"], v["verdict"]))
    for r in reads:
        print("      %-10s %-9s %-8s %s" % (
            r["frame"], ocr.fmt(r["value"]) if r["value"] is not None else "-",
            r["colour"], r["counts"]))
    for w in v["why"]:
        print("      ! " + w)
    print()
