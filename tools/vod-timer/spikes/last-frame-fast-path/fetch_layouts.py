"""Pull hidden:Layout (and ESA's own VOD link) out of the Summer 2025 schedules.

The layout key is the natural pin for a per-layout crop, and it is the one
thing all-resolved.csv does not carry. It costs two JSON fetches, not two
video downloads -- which is the whole point: the crop half of this spike is
answerable without touching YouTube.
"""
import csv, io, json, re, sys, urllib.request

UA = "esavods-vod-timer/0.1 (+https://github.com/TheShrug/esavods)"
YT = re.compile(r"youtu(?:\.be/|be\.com/watch\?v=)([\w-]{11})")
MD = re.compile(r"\[([^\]]+)\]\([^)]*\)")
OUT = "spikes/last-frame-fast-path/layouts.csv"


def plain(t):
    return MD.sub(lambda m: m.group(1), t or "").strip()


def fetch(slug):
    req = urllib.request.Request("https://horaro.net/esa/%s.json" % slug,
                                 headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as fh:
        return json.load(fh)


rows = []
for slug in sys.argv[1:]:
    sched = fetch(slug)["schedule"]
    # `columns` already names the hidden ones as "hidden:layout" etc, and the
    # values sit in the same `data` array, so there is nothing separate to zip.
    cols = [c.lower() for c in sched["columns"]]
    for item in sched["items"]:
        cells = dict(zip(cols, item.get("data") or []))
        raw = cells.get("game", "")
        if not plain(raw):
            continue
        m = YT.search(raw or "")
        rows.append({
            "slug": slug,
            "game": plain(raw),
            "video_id": m.group(1) if m else "",
            "layout": cells.get("hidden:layout") or "",
            "players": plain(cells.get("player(s)") or ""),
            "estimate": item.get("length_t", ""),
        })

with io.open(OUT, "w", encoding="utf8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
sys.stderr.write("wrote %s: %d rows\n" % (OUT, len(rows)))
