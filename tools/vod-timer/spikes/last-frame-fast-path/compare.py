"""Fast read vs the slow path's own answer, over the sampled runs."""
import csv, io, collections, json

def load(p):
    return list(csv.DictReader(io.open(p, encoding="utf8")))

rows = [r for r in load("spikes/last-frame-fast-path/fast-results.csv") if r.get("verdict") or r.get("error")]
extra = {r["video_id"]: r["why"] for r in load("spikes/last-frame-fast-path/sample.csv") if r["why"]}

def secs(t):
    if not t:
        return None
    p = [float(x) for x in t.split(":")]
    v = 0.0
    for x in p:
        v = v * 60 + x
    return v

agree = load_err = 0
tbl = collections.Counter()
print("%-11s %-9s %-32s %-9s %-9s %-7s %s" % (
    "video", "layout", "game", "slow", "fast", "verdict", "delta"))
for r in sorted(rows, key=lambda r: (r["layout"], r["game"])):
    if r["video_id"] in extra:
        continue
    s, f = secs(r["slow_time"]), secs(r["fast_time"])
    d = "" if (s is None or f is None) else "%+d" % (f - s)
    if r.get("error"):
        d = "ERROR"
    tbl[(r["verdict"] or "error", "same" if (s is not None and f == s) else d or "-")] += 1
    print("%-11s %-9s %-32s %-9s %-9s %-7s %s" % (
        r["video_id"], r["layout"], r["game"][:32], r["slow_time"],
        r["fast_time"] or "-", r["verdict"] or "ERROR", d))

main = [r for r in rows if r["video_id"] not in extra]
n = len(main)
same = [r for r in main if r["fast_time"] and secs(r["fast_time"]) == secs(r["slow_time"])]
acc = [r for r in main if r["verdict"] == "accept"]
chk = [r for r in main if r["verdict"] == "check"]
rej = [r for r in main if r["verdict"] == "reject"]
err = [r for r in main if r.get("error")]
print()
print("sampled high-confidence runs      %d" % n)
print("  fast answer == slow answer      %d  (%.0f%%)" % (len(same), 100.0*len(same)/max(n,1)))
print("  verdict accept                  %d, of which agree %d"
      % (len(acc), sum(1 for r in acc if secs(r["fast_time"]) == secs(r["slow_time"]))))
print("  verdict check                   %d, of which agree %d"
      % (len(chk), sum(1 for r in chk if r["fast_time"] and secs(r["fast_time"]) == secs(r["slow_time"]))))
print("  verdict reject                  %d" % len(rej))
print("  download error                  %d" % len(err))
for L in sorted(set(r["layout"] for r in main)):
    ls = [r for r in main if r["layout"] == L]
    ok = sum(1 for r in ls if r["fast_time"] and secs(r["fast_time"]) == secs(r["slow_time"]))
    a = sum(1 for r in ls if r["verdict"] == "accept")
    print("  %-9s n=%-3d agree %-3d accept %-3d" % (L, len(ls), ok, a))
print()
print("bandwidth: %.1f MB total, %.2f MB median per run; %.1fs median per run"
      % (sum(float(r["clip_bytes"] or 0) for r in main)/1e6,
         sorted(float(r["clip_bytes"] or 0) for r in main)[len(main)//2]/1e6,
         sorted(float(r["seconds"] or 0) for r in main)[len(main)//2]))
print()
print("--- the four deliberate hard cases ---")
for r in rows:
    if r["video_id"] not in extra:
        continue
    print("%-11s %-34s\n    slow %-9s fast %-9s %-7s  %s\n    %s" % (
        r["video_id"], extra[r["video_id"]][:34], r["slow_time"],
        r["fast_time"] or "-", r["verdict"] or "ERROR", r["colours"],
        r["why"] or r["error"] or ""))
