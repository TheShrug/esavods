"""Rescore the accept/check split with a rule the prototype got wrong.

The prototype demanded that *every* sampled frame agree and be green. But a
60s tail sometimes catches the finish itself, so the earlier frames legitimately
show a ticking orange clock and legitimately disagree -- that is the slow
path's ramp, arriving free, and it is evidence *for* the answer, not against it.

The rule that follows the physics: at least two green frames, and every green
frame reading the same value. Rescored from the recorded aggregates -- `agree`
is how many readable frames held the modal value -- not re-read. A re-read
would cost another 40 invocations and could not change any answer, only its
label.
"""
import csv, io, json

rows = [r for r in csv.DictReader(io.open("spikes/last-frame-fast-path/fast-results.csv", encoding="utf8"))]
extra = {r["video_id"] for r in csv.DictReader(io.open("spikes/last-frame-fast-path/sample.csv", encoding="utf8")) if r["why"]}

def rescored(r):
    c = json.loads(r["colours"] or "{}")
    stopped, agree = c.get("stopped", 0), int(r["agree"] or 0)
    if stopped == 0:
        return "reject"
    if not r["fast_time"]:
        return "reject"
    if "estimate" in (r["why"] or "") or "longer than" in (r["why"] or ""):
        return "reject"
    return "accept" if (stopped >= 2 and agree >= stopped) else "check"

main = [r for r in rows if r["video_id"] not in extra]
print("%-32s %-9s %-8s %-8s %-24s %s" % ("game", "fast", "as run", "rescored", "colours", "why"))
for r in sorted(main, key=lambda r: r["game"]):
    if r["verdict"] == "accept" and rescored(r) == "accept":
        continue
    print("%-32s %-9s %-8s %-8s %-24s %s" % (r["game"][:32], r["fast_time"],
          r["verdict"], rescored(r), r["colours"], (r["why"] or "")[:52]))

import collections
print()
for name, f in (("as run", lambda r: r["verdict"]), ("rescored", rescored)):
    c = collections.Counter(f(r) for r in main)
    ok = sum(1 for r in main if f(r) == "accept" and r["fast_time"] == r["slow_time"])
    print("%-9s %-40s accept-and-agrees %d/%d" % (name, dict(c), ok, len(main)))

ramp = [r for r in main if json.loads(r["colours"])["stopped"] < int(r["frames"])]
print("\nruns whose 60s tail also caught the finish (some frames still orange): %d of %d"
      % (len(ramp), len(main)))
print("  every one of those still read the same value as the slow path: %s"
      % all(r["fast_time"] == r["slow_time"] for r in ramp))

print("\n--- the four hard cases, rescored ---")
for r in rows:
    if r["video_id"] in extra:
        print("%-32s slow %-9s fast %-9s  as run %-7s rescored %-7s  %s"
              % (r["game"][:32], r["slow_time"], r["fast_time"] or "-",
                 r["verdict"], rescored(r), r["colours"]))
