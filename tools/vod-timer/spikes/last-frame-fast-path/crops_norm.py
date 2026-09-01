"""Re-read the crop column in *fractions of the frame*, not pixels.

The pixel view says 16x9-1p has an outlier at x=30 and 4x3-1p has three
distinct positions. But `--height` is not constant across the event: two runs
were re-read at 720p and the height selector is known to step *down* when a
rendition is missing, so some rows are 360p. A crop recorded in 360p pixels is
not a different position, it is the same position in a smaller frame.

The recorded box is the glyph union padded by (w0//12+5, h0//5+3), so the
padded width w scales with the frame. Take the 480p standard w=188 as unity,
infer each row's scale from its own width, and put every crop back on one map.
"""
import csv, io, collections

W480, H480 = 854.0, 480.0
STD_W = 188.0                      # padded box width of the 480p standard


def load(p):
    return list(csv.DictReader(io.open(p, encoding="utf8")))


res = load("out/all-results.csv")
lay = {r["video_id"]: r for r in load("spikes/last-frame-fast-path/layouts.csv") if r["video_id"]}

rows = []
for r in res:
    if not r["crop"]:
        continue
    x, y, w, h = (int(v) for v in r["crop"].split(","))
    s = w / STD_W                                  # frame scale vs 480p
    rows.append({
        "video_id": r["video_id"], "game": r["game"], "conf": r["confidence"],
        "layout": lay.get(r["video_id"], {}).get("layout", ""),
        "crop": r["crop"], "scale": s,
        "fx": x / (W480 * s), "fy": y / (H480 * s),
        "fw": w / (W480 * s), "fh": h / (H480 * s),
        "height": int(round(480 * s)),
    })

print("inferred download height, from the recorded box width:")
for hgt, n in sorted(collections.Counter(r["height"] for r in rows).items()):
    print("   %4dp  %3d" % (hgt, n))
print()

ONE = {"16x9-1p", "4x3-1p", "GB-1p", "DS-1p"}
print("%-9s %-38s %-7s %-18s  %s" % ("layout", "game", "height", "crop (px)", "as fraction of frame"))
off = []
for r in sorted(rows, key=lambda r: (r["layout"], r["fx"])):
    tag = ""
    if abs(r["fx"] - 0.524) > 0.02 or abs(r["fy"] - 0.77) > 0.05:
        tag = "  <-- not at the common position"
        off.append(r)
    print("%-9s %-38s %5dp  %-18s  x %.3f y %.3f w %.3f h %.3f%s" % (
        r["layout"] or "(none)", r["game"][:38], r["height"], r["crop"],
        r["fx"], r["fy"], r["fw"], r["fh"], tag))

print()
one = [r for r in rows if r["layout"] in ONE]
common = [r for r in one if r not in off]
print("single-player rows with a crop: %d" % len(one))
print("  at the common position:       %d" % len(common))
if common:
    print("  x  %.4f - %.4f   (%.1f px of an 854-wide frame)"
          % (min(r["fx"] for r in common), max(r["fx"] for r in common),
             854 * (max(r["fx"] for r in common) - min(r["fx"] for r in common))))
    print("  y  %.4f - %.4f   (%.1f px of a 480-high frame)"
          % (min(r["fy"] for r in common), max(r["fy"] for r in common),
             480 * (max(r["fy"] for r in common) - min(r["fy"] for r in common))))
    print("  right edge x+w  %.4f      bottom edge y+h  %.4f"
          % (max(r["fx"] + r["fw"] for r in common),
             max(r["fy"] + r["fh"] for r in common)))
