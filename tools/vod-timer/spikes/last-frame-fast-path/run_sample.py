"""Fast-read every run in spike/sample.csv and diff against the slow path.

One yt-dlp invocation per run -- the same count the slow path pays, because
the saving is bandwidth, not requests. Metadata comes from the cache, so
`probe` costs nothing. The bot-wall breaker is copied from cli.py: on this IP
the wall went up twice during Summer 2025, and continuing into it wastes time
and plausibly deepens the block.
"""
import csv, io, json, os, re, sys, tempfile, time
from pathlib import Path

sys.path.insert(0, "/app")
sys.path.insert(0, "/spike")

from vodtimer import ocr, video
from vodtimer.pipeline import parse_duration
import fastread

TAIL = int(os.environ.get("TAIL", "60"))
STEP = float(os.environ.get("STEP", "10"))
HEIGHT = int(os.environ.get("HEIGHT", "480"))
LIMIT = int(os.environ.get("LIMIT", "999"))
BUDGET = int(os.environ.get("BUDGET", "50"))

# A 60s tail of a static outro compresses to well under the 512 KB the slow
# path uses to detect a failed HLS cut, so that floor would reject good clips.
# Lowered, and backed up by requiring the clip to yield frames.
video.MIN_CLIP_BYTES = 48 * 1024

BOT_WALL = re.compile(r"not a bot|sign in to confirm|HTTP Error 429|too many requests", re.I)

rows = list(csv.DictReader(io.open("/spike/sample.csv", encoding="utf8")))[:LIMIT]
out_path = Path("/spike/fast-results.csv")
done = {}
if out_path.exists():
    done = {r["video_id"]: r for r in csv.DictReader(io.open(out_path, encoding="utf8"))
            if r.get("verdict")}
    print("resuming: %d already read" % len(done))

fields = ["video_id", "game", "layout", "estimate", "slow_time", "slow_conf",
          "fast_time", "verdict", "agree", "frames", "colours", "clip_bytes",
          "seconds", "why", "error"]
sink = io.open(out_path, "w", encoding="utf8", newline="")
w = csv.DictWriter(sink, fieldnames=fields, extrasaction="ignore", restval="",
                   lineterminator="\n")
w.writeheader()
for r in done.values():
    w.writerow(r)
sink.flush()

spent = 0
consecutive_wall = 0
for i, row in enumerate(rows, 1):
    vid = row["video_id"]
    if vid in done:
        continue
    if spent >= BUDGET:
        print("\nSTOPPED: download budget of %d yt-dlp invocations reached." % BUDGET)
        break
    t0 = time.time()
    rec = dict(row)
    try:
        meta = video.probe(vid)                    # cached: no request
        start = max(0, meta.duration - TAIL)
        spent += 1
        clip = video.download_window(vid, start, meta.duration, HEIGHT)
        rec["clip_bytes"] = clip.stat().st_size
        with tempfile.TemporaryDirectory() as tmp:
            frames = video.extract_frames(clip, Path(tmp), STEP)
            if not frames:
                raise RuntimeError("clip produced no frames")
            reads = fastread.read_frames(frames)
            v = fastread.verdict(reads, parse_duration(row.get("estimate")), meta.duration)
        rec.update({"fast_time": v["time"], "verdict": v["verdict"],
                    "agree": v.get("agree", 0), "frames": v["frames"],
                    "colours": json.dumps(v["colours"]),
                    "why": "; ".join(v["why"])})
        video.forget_clips(vid)
        consecutive_wall = 0
    except Exception as exc:
        rec["error"] = str(exc)[:400]
        rec["verdict"] = ""
        if BOT_WALL.search(str(exc)):
            consecutive_wall += 1
            if consecutive_wall >= 3:
                w.writerow(rec); sink.flush()
                print("\nSTOPPED: YouTube's bot wall, %d in a row. Not retrying into it."
                      % consecutive_wall)
                break
        else:
            consecutive_wall = 0
    rec["seconds"] = round(time.time() - t0, 1)
    w.writerow(rec); sink.flush()
    print("[%2d/%2d] %-11s %-9s %-32s slow %-9s fast %-9s %-7s %s"
          % (i, len(rows), vid, row["layout"], row["game"][:32], row["slow_time"],
             rec.get("fast_time") or "-", rec.get("verdict") or "ERROR",
             (rec.get("error") or rec.get("why") or "")[:60]))
sink.close()
print("\nspent %d yt-dlp invocations of a %d budget" % (spent, BUDGET))
